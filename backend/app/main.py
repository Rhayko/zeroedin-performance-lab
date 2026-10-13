from collections import defaultdict
from contextlib import asynccontextmanager
import csv
from datetime import UTC, date, datetime
from io import StringIO
from pathlib import Path
from statistics import mean
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .analytics import aggregate_daily_load, baseline_status, deviations, pearson, relationship_interpretation, rolling_mean
from .database import Base, engine, get_db
from .models import Athlete, DailyState, ExerciseSet, Outcome, PerformanceTest, Prediction, Sleep, Symptom, TrainingSession
from .schemas import AnalyticsPoint, AnalyticsResponse, AthleteCreate, AthleteRead, AthleteUpdate, DailyStateCreate, DailyStateRead, OutcomeCreate, PerformanceTestCreate, PerformanceTestRead, PredictionCreate, TrainingSessionCreate, TrainingSessionRead
from .seed import seed_demo

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="ZeroedIn Performance Lab API", version="0.1.0", lifespan=lifespan)
demo_seed_lock = Lock()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/demo/seed", response_model=AthleteRead)
def create_demo(db: Session = Depends(get_db)):
    with demo_seed_lock:
        return seed_demo(db)


@app.get("/api/athletes", response_model=list[AthleteRead])
def list_athletes(db: Session = Depends(get_db)):
    return db.scalars(select(Athlete).order_by(Athlete.created_at)).all()


@app.post("/api/athletes", response_model=AthleteRead, status_code=status.HTTP_201_CREATED)
def create_athlete(payload: AthleteCreate, db: Session = Depends(get_db)):
    item = Athlete(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


def get_athlete_or_404(athlete_id: int, db: Session):
    item = db.get(Athlete, athlete_id)
    if not item:
        raise HTTPException(404, "Athlete not found")
    return item


@app.get("/api/athletes/{athlete_id}", response_model=AthleteRead)
def get_athlete(athlete_id: int, db: Session = Depends(get_db)):
    return get_athlete_or_404(athlete_id, db)


@app.patch("/api/athletes/{athlete_id}", response_model=AthleteRead)
def update_athlete(athlete_id: int, payload: AthleteUpdate, db: Session = Depends(get_db)):
    item = get_athlete_or_404(athlete_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/athletes/{athlete_id}/daily-states", response_model=list[DailyStateRead])
def list_daily_states(athlete_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(DailyState).where(DailyState.athlete_id == athlete_id).options(selectinload(DailyState.sleep), selectinload(DailyState.symptoms)).order_by(DailyState.recorded_date)).all()


@app.post("/api/athletes/{athlete_id}/daily-states", response_model=DailyStateRead, status_code=201)
def create_daily_state(athlete_id: int, payload: DailyStateCreate, db: Session = Depends(get_db)):
    get_athlete_or_404(athlete_id, db)
    values = payload.model_dump(exclude={"sleep", "symptoms"})
    item = DailyState(athlete_id=athlete_id, **values)
    item.sleep = Sleep(**payload.sleep.model_dump())
    item.symptoms = [Symptom(**symptom.model_dump()) for symptom in payload.symptoms]
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "A check-in already exists for this date")
    return db.scalar(select(DailyState).where(DailyState.id == item.id).options(selectinload(DailyState.sleep), selectinload(DailyState.symptoms)))


@app.delete("/api/athletes/{athlete_id}/daily-states/{state_id}", status_code=204)
def delete_daily_state(athlete_id: int, state_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(DailyState).where(DailyState.id == state_id, DailyState.athlete_id == athlete_id))
    if not item:
        raise HTTPException(404, "Daily observation not found")
    db.delete(item)
    db.commit()


@app.get("/api/athletes/{athlete_id}/sessions", response_model=list[TrainingSessionRead])
def list_sessions(athlete_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(TrainingSession).where(TrainingSession.athlete_id == athlete_id).options(selectinload(TrainingSession.sets)).order_by(TrainingSession.performed_at.desc())).all()


@app.post("/api/athletes/{athlete_id}/sessions", response_model=TrainingSessionRead, status_code=201)
def create_session(athlete_id: int, payload: TrainingSessionCreate, db: Session = Depends(get_db)):
    get_athlete_or_404(athlete_id, db)
    item = TrainingSession(athlete_id=athlete_id, **payload.model_dump(exclude={"sets"}))
    item.sets = [ExerciseSet(**entry.model_dump()) for entry in payload.sets]
    db.add(item); db.commit(); db.refresh(item)
    return db.scalar(select(TrainingSession).where(TrainingSession.id == item.id).options(selectinload(TrainingSession.sets)))


@app.delete("/api/athletes/{athlete_id}/sessions/{session_id}", status_code=204)
def delete_session(athlete_id: int, session_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(TrainingSession).where(TrainingSession.id == session_id, TrainingSession.athlete_id == athlete_id))
    if not item:
        raise HTTPException(404, "Training session not found")
    db.delete(item)
    db.commit()


@app.get("/api/athletes/{athlete_id}/performance-tests", response_model=list[PerformanceTestRead])
def list_tests(athlete_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(PerformanceTest).where(PerformanceTest.athlete_id == athlete_id).order_by(PerformanceTest.performed_at.desc())).all()


@app.post("/api/athletes/{athlete_id}/performance-tests", response_model=PerformanceTestRead, status_code=201)
def create_test(athlete_id: int, payload: PerformanceTestCreate, db: Session = Depends(get_db)):
    get_athlete_or_404(athlete_id, db)
    item = PerformanceTest(athlete_id=athlete_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


@app.delete("/api/athletes/{athlete_id}/performance-tests/{test_id}", status_code=204)
def delete_test(athlete_id: int, test_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(PerformanceTest).where(PerformanceTest.id == test_id, PerformanceTest.athlete_id == athlete_id))
    if not item:
        raise HTTPException(404, "Performance test not found")
    db.delete(item)
    db.commit()


@app.post("/api/athletes/{athlete_id}/predictions", status_code=403)
def predictions_disabled(athlete_id: int, payload: PredictionCreate):
    raise HTTPException(403, "Predictive outputs are reserved for later validated models")


@app.post("/api/predictions/{prediction_id}/outcome", status_code=201)
def record_outcome(prediction_id: int, payload: OutcomeCreate, db: Session = Depends(get_db)):
    prediction = db.get(Prediction, prediction_id)
    if not prediction: raise HTTPException(404, "Prediction not found")
    item = Outcome(prediction_id=prediction_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "prediction_id": prediction_id, "observed_value": item.observed_value}


@app.get("/api/athletes/{athlete_id}/analytics", response_model=AnalyticsResponse)
def analytics(athlete_id: int, db: Session = Depends(get_db)):
    get_athlete_or_404(athlete_id, db)
    states = list(db.scalars(select(DailyState).where(DailyState.athlete_id == athlete_id).options(selectinload(DailyState.sleep)).order_by(DailyState.recorded_date)))
    sessions = list(db.scalars(select(TrainingSession).where(TrainingSession.athlete_id == athlete_id).order_by(TrainingSession.performed_at)))
    tests = list(db.scalars(select(PerformanceTest).where(PerformanceTest.athlete_id == athlete_id).order_by(PerformanceTest.performed_at)))
    loads = aggregate_daily_load(sessions)
    load_dates = sorted(loads)
    load_values = [loads[d] for d in load_dates]
    load_roll = rolling_mean(load_values)
    load_dev = deviations(load_values)
    wellness_values = [round((6-s.fatigue + 6-s.stress + s.motivation + s.perceived_recovery) / 4, 2) for s in states]
    wellness_roll = rolling_mean(wellness_values)
    wellness_dev = deviations(wellness_values)
    performance = defaultdict(list)
    grouped = defaultdict(list)
    for test in tests: grouped[test.test_type].append(test)
    for test_type, entries in grouped.items():
        vals = [x.value for x in entries]
        rolls, devs = rolling_mean(vals, 3), deviations(vals)
        performance[test_type] = [AnalyticsPoint(date=x.performed_at.date(), value=x.value, rolling_average=rolls[i], deviation_from_baseline=devs[i]) for i, x in enumerate(entries)]
    sleep_by_date = {s.recorded_date: s.sleep.duration_hours for s in states if s.sleep}
    wellness_by_date = {s.recorded_date: wellness_values[i] for i, s in enumerate(states)}
    shared = sorted(set(sleep_by_date) & set(wellness_by_date))
    pairs = [(sleep_by_date[d], wellness_by_date[d]) for d in shared]
    r = pearson([p[0] for p in pairs], [p[1] for p in pairs])
    relationships = [{"x_metric": "sleep duration", "y_metric": "self-reported wellness", "observations": len(pairs), "correlation": r, "interpretation": relationship_interpretation(r, len(pairs)), "analysis_type": "exploratory"}]
    return AnalyticsResponse(
        baseline=baseline_status([s.recorded_date for s in states]),
        training_load=[AnalyticsPoint(date=d, value=load_values[i], rolling_average=load_roll[i], deviation_from_baseline=load_dev[i]) for i, d in enumerate(load_dates)],
        wellness=[AnalyticsPoint(date=s.recorded_date, value=wellness_values[i], rolling_average=wellness_roll[i], deviation_from_baseline=wellness_dev[i]) for i, s in enumerate(states)],
        performance=dict(performance), relationships=relationships,
        scope_note="All current analytics are descriptive or exploratory. Relationships are unadjusted sample associations, not causal or predictive claims.",
    )


@app.get("/api/athletes/{athlete_id}/export.json")
def export_json(athlete_id: int, db: Session = Depends(get_db)):
    athlete = get_athlete_or_404(athlete_id, db)
    states = db.scalars(select(DailyState).where(DailyState.athlete_id == athlete_id).options(selectinload(DailyState.sleep), selectinload(DailyState.symptoms)).order_by(DailyState.recorded_date)).all()
    sessions = db.scalars(select(TrainingSession).where(TrainingSession.athlete_id == athlete_id).options(selectinload(TrainingSession.sets)).order_by(TrainingSession.performed_at)).all()
    tests = db.scalars(select(PerformanceTest).where(PerformanceTest.athlete_id == athlete_id).order_by(PerformanceTest.performed_at)).all()
    payload = {
        "format": "zeroedin-local-backup-v1",
        "exported_at": datetime.now(UTC),
        "athlete": AthleteRead.model_validate(athlete),
        "daily_states": [DailyStateRead.model_validate(item) for item in states],
        "sessions": [TrainingSessionRead.model_validate(item) for item in sessions],
        "performance_tests": [PerformanceTestRead.model_validate(item) for item in tests],
    }
    return JSONResponse(jsonable_encoder(payload), headers={"Content-Disposition": f'attachment; filename="zeroedin-{athlete_id}-backup.json"'})


@app.get("/api/athletes/{athlete_id}/export.csv")
def export_csv(athlete_id: int, db: Session = Depends(get_db)):
    athlete = get_athlete_or_404(athlete_id, db)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["record_type", "date", "category", "value_1", "value_2", "value_3", "notes"])
    states = db.scalars(select(DailyState).where(DailyState.athlete_id == athlete_id).options(selectinload(DailyState.sleep)).order_by(DailyState.recorded_date)).all()
    for item in states:
        writer.writerow(["daily_state", item.recorded_date, "wellness", item.sleep.duration_hours if item.sleep else "", item.perceived_recovery, item.fatigue, item.notes or ""])
    sessions = db.scalars(select(TrainingSession).where(TrainingSession.athlete_id == athlete_id).order_by(TrainingSession.performed_at)).all()
    for item in sessions:
        writer.writerow(["training_session", item.performed_at.isoformat(), item.session_type, item.duration_minutes, item.session_rpe, item.duration_minutes * item.session_rpe, item.notes or ""])
    tests = db.scalars(select(PerformanceTest).where(PerformanceTest.athlete_id == athlete_id).order_by(PerformanceTest.performed_at)).all()
    for item in tests:
        writer.writerow(["performance_test", item.performed_at.isoformat(), item.test_type, item.value, item.unit, "", item.notes or ""])
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="zeroedin-{athlete_id}-records.csv"'})


@app.post("/api/import", response_model=AthleteRead, status_code=201)
def import_backup(payload: dict, db: Session = Depends(get_db)):
    if payload.get("format") != "zeroedin-local-backup-v1":
        raise HTTPException(400, "Unsupported or invalid ZeroedIn backup")
    try:
        athlete_data = AthleteCreate.model_validate(payload["athlete"])
        athlete = Athlete(**athlete_data.model_dump())
        db.add(athlete)
        db.flush()
        for raw in payload.get("daily_states", []):
            data = DailyStateCreate.model_validate(raw)
            state = DailyState(athlete_id=athlete.id, **data.model_dump(exclude={"sleep", "symptoms"}))
            state.sleep = Sleep(**data.sleep.model_dump())
            state.symptoms = [Symptom(**entry.model_dump()) for entry in data.symptoms]
            db.add(state)
        for raw in payload.get("sessions", []):
            data = TrainingSessionCreate.model_validate(raw)
            session = TrainingSession(athlete_id=athlete.id, **data.model_dump(exclude={"sets"}))
            session.sets = [ExerciseSet(**entry.model_dump()) for entry in data.sets]
            db.add(session)
        for raw in payload.get("performance_tests", []):
            data = PerformanceTestCreate.model_validate(raw)
            db.add(PerformanceTest(athlete_id=athlete.id, **data.model_dump()))
        db.commit()
        db.refresh(athlete)
        return athlete
    except (KeyError, ValueError) as exc:
        db.rollback()
        raise HTTPException(400, "Backup contents are invalid") from exc


frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
