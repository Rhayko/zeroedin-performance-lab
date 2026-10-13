from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Athlete(Base):
    __tablename__ = "athletes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    sport: Mapped[str] = mapped_column(String(120), default="General performance")
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    training_age_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class DailyState(Base):
    __tablename__ = "daily_states"
    __table_args__ = (UniqueConstraint("athlete_id", "recorded_date"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), index=True)
    recorded_date: Mapped[date] = mapped_column(Date, index=True)
    fatigue: Mapped[int] = mapped_column(Integer)
    stress: Mapped[int] = mapped_column(Integer)
    motivation: Mapped[int] = mapped_column(Integer)
    perceived_recovery: Mapped[int] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sleep: Mapped[Optional["Sleep"]] = relationship(back_populates="daily_state", cascade="all, delete-orphan", uselist=False)
    symptoms: Mapped[list["Symptom"]] = relationship(back_populates="daily_state", cascade="all, delete-orphan")


class Sleep(Base):
    __tablename__ = "sleep"
    id: Mapped[int] = mapped_column(primary_key=True)
    daily_state_id: Mapped[int] = mapped_column(ForeignKey("daily_states.id", ondelete="CASCADE"), unique=True)
    duration_hours: Mapped[float] = mapped_column(Float)
    quality: Mapped[int] = mapped_column(Integer)
    bedtime: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    wake_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    daily_state: Mapped[DailyState] = relationship(back_populates="sleep")


class Symptom(Base):
    __tablename__ = "symptoms"
    id: Mapped[int] = mapped_column(primary_key=True)
    daily_state_id: Mapped[int] = mapped_column(ForeignKey("daily_states.id", ondelete="CASCADE"))
    body_region: Mapped[str] = mapped_column(String(80))
    symptom_type: Mapped[str] = mapped_column(String(80), default="soreness")
    severity: Mapped[int] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    daily_state: Mapped[DailyState] = relationship(back_populates="symptoms")


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), index=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    session_type: Mapped[str] = mapped_column(String(80))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    session_rpe: Mapped[float] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sets: Mapped[list["ExerciseSet"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("training_sessions.id", ondelete="CASCADE"), index=True)
    exercise_name: Mapped[str] = mapped_column(String(120))
    set_number: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    load_kg: Mapped[float] = mapped_column(Float, default=0)
    rpe: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rir: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    session: Mapped[TrainingSession] = relationship(back_populates="sets")


class PerformanceTest(Base):
    __tablename__ = "performance_tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), index=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    test_type: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    protocol: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class WearableMetric(Base):
    __tablename__ = "wearable_metrics"
    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    metric_type: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    source: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    target: Mapped[str] = mapped_column(String(120))
    predicted_value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    model_version: Mapped[str] = mapped_column(String(80))
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_date: Mapped[datetime] = mapped_column(DateTime)
    outcome: Mapped[Optional["Outcome"]] = relationship(back_populates="prediction", cascade="all, delete-orphan", uselist=False)


class Outcome(Base):
    __tablename__ = "outcomes"
    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id", ondelete="CASCADE"), unique=True)
    observed_value: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prediction: Mapped[Prediction] = relationship(back_populates="outcome")
