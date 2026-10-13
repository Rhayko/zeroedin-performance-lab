from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AthleteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sport: str = "General performance"
    date_of_birth: date | None = None
    height_cm: float | None = Field(None, gt=0)
    weight_kg: float | None = Field(None, gt=0)
    training_age_years: float | None = Field(None, ge=0)
    goals: str | None = None


class AthleteRead(AthleteCreate, ORMModel):
    id: int
    created_at: datetime


class AthleteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    sport: str | None = Field(None, min_length=1, max_length=120)
    date_of_birth: date | None = None
    height_cm: float | None = Field(None, gt=0)
    weight_kg: float | None = Field(None, gt=0)
    training_age_years: float | None = Field(None, ge=0)
    goals: str | None = None


class SleepInput(BaseModel):
    duration_hours: float = Field(ge=0, le=24)
    quality: int = Field(ge=1, le=5)
    bedtime: str | None = None
    wake_time: str | None = None


class SymptomInput(BaseModel):
    body_region: str
    symptom_type: str = "soreness"
    severity: int = Field(ge=0, le=10)
    notes: str | None = None


class DailyStateCreate(BaseModel):
    recorded_date: date
    fatigue: int = Field(ge=1, le=5)
    stress: int = Field(ge=1, le=5)
    motivation: int = Field(ge=1, le=5)
    perceived_recovery: int = Field(ge=1, le=5)
    notes: str | None = None
    sleep: SleepInput
    symptoms: list[SymptomInput] = []


class DailyStateRead(DailyStateCreate, ORMModel):
    id: int
    athlete_id: int


class ExerciseSetInput(BaseModel):
    exercise_name: str
    set_number: int = Field(ge=1)
    reps: int = Field(ge=0)
    load_kg: float = Field(ge=0)
    rpe: float | None = Field(None, ge=0, le=10)
    rir: float | None = Field(None, ge=0, le=10)


class TrainingSessionCreate(BaseModel):
    performed_at: datetime
    session_type: str
    duration_minutes: int = Field(gt=0)
    session_rpe: float = Field(ge=0, le=10)
    notes: str | None = None
    sets: list[ExerciseSetInput] = []


class TrainingSessionRead(TrainingSessionCreate, ORMModel):
    id: int
    athlete_id: int


class PerformanceTestCreate(BaseModel):
    performed_at: datetime
    test_type: str
    value: float
    unit: str
    protocol: str | None = None
    notes: str | None = None


class PerformanceTestRead(PerformanceTestCreate, ORMModel):
    id: int
    athlete_id: int


class OutcomeCreate(BaseModel):
    observed_value: float
    notes: str | None = None


class PredictionCreate(BaseModel):
    target: str
    predicted_value: float
    unit: str
    model_version: str
    confidence: float | None = Field(None, ge=0, le=1)
    target_date: datetime


class AnalyticsPoint(BaseModel):
    date: date
    value: float
    rolling_average: float | None = None
    deviation_from_baseline: float | None = None


class Relationship(BaseModel):
    x_metric: str
    y_metric: str
    observations: int
    correlation: float | None
    interpretation: str
    analysis_type: Literal["exploratory"] = "exploratory"


class AnalyticsResponse(BaseModel):
    baseline: dict
    training_load: list[AnalyticsPoint]
    wellness: list[AnalyticsPoint]
    performance: dict[str, list[AnalyticsPoint]]
    relationships: list[Relationship]
    scope_note: str
