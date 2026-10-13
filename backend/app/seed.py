from datetime import date, datetime, time, timedelta
from math import sin

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Athlete, DailyState, ExerciseSet, PerformanceTest, Sleep, Symptom, TrainingSession


def seed_demo(db: Session) -> Athlete:
    existing = db.scalar(select(Athlete).where(Athlete.name == "Alex Morgan"))
    if existing:
        return existing
    athlete = Athlete(name="Alex Morgan", sport="Hybrid performance", height_cm=178, weight_kg=79.4, training_age_years=6, goals="Build durable strength and improve 5 km performance")
    db.add(athlete)
    db.flush()
    today = date.today()
    for offset in range(18, -1, -1):
        day = today - timedelta(days=offset)
        wave = sin(offset / 2.4)
        state = DailyState(athlete_id=athlete.id, recorded_date=day, fatigue=max(1, min(5, round(3 + wave))), stress=max(1, min(5, round(2.5 + wave / 2))), motivation=max(1, min(5, round(4 - wave / 2))), perceived_recovery=max(1, min(5, round(3.5 - wave / 1.5))), notes="Demo observation")
        state.sleep = Sleep(duration_hours=round(7.4 - wave * .55, 1), quality=max(1, min(5, round(4 - wave / 2))))
        if offset in (13, 6):
            state.symptoms.append(Symptom(body_region="Quadriceps", symptom_type="soreness", severity=3))
        db.add(state)
        if offset % 2 == 0:
            performed = datetime.combine(day, time(17, 30))
            kind = "Strength" if offset % 4 == 0 else "Conditioning"
            session = TrainingSession(athlete_id=athlete.id, performed_at=performed, session_type=kind, duration_minutes=55 + offset % 15, session_rpe=round(5.5 + (offset % 4) * .5, 1), notes="Seeded demo session")
            if kind == "Strength":
                for set_no in range(1, 4):
                    session.sets.append(ExerciseSet(exercise_name="Back squat", set_number=set_no, reps=5, load_kg=100 + (18 - offset) * .5, rpe=6.5 + set_no * .5, rir=3 - set_no * .5))
            db.add(session)
    for offset, value in ((16, 42.1), (9, 43.4), (2, 42.8)):
        db.add(PerformanceTest(athlete_id=athlete.id, performed_at=datetime.combine(today - timedelta(days=offset), time(9)), test_type="Countermovement jump", value=value, unit="cm", protocol="Hands on hips; best of three"))
    db.commit()
    db.refresh(athlete)
    return athlete

