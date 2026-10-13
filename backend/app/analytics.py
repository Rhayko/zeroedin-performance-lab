from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean, pstdev


BASELINE_DAYS = 28


def session_load(duration_minutes: float, session_rpe: float) -> float:
    """Foster-style session load in arbitrary units."""
    return round(duration_minutes * session_rpe, 1)


def set_volume(reps: int, load_kg: float) -> float:
    return round(reps * load_kg, 1)


def rolling_mean(values: list[float], window: int = 7) -> list[float | None]:
    result = []
    for index in range(len(values)):
        start = max(0, index - window + 1)
        result.append(round(mean(values[start : index + 1]), 2))
    return result


def baseline_status(observation_dates: list[date], target_days: int = BASELINE_DAYS) -> dict:
    unique = sorted(set(observation_dates))
    completed = min(len(unique), target_days)
    return {
        "state": "established" if completed >= target_days else "building",
        "days_observed": completed,
        "target_days": target_days,
        "progress_percent": round(completed / target_days * 100),
        "message": "Baseline established" if completed >= target_days else f"Baseline building: Day {completed}/{target_days}",
    }


def deviations(values: list[float], baseline_window: int = BASELINE_DAYS) -> list[float | None]:
    if not values:
        return []
    base = values[:baseline_window]
    center = mean(base)
    return [round(value - center, 2) for value in values]


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    x_mean, y_mean = mean(xs), mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - x_mean) ** 2 for x in xs) * sum((y - y_mean) ** 2 for y in ys))
    return round(numerator / denominator, 3) if denominator else None


def relationship_interpretation(r: float | None, n: int) -> str:
    if r is None:
        return "Insufficient variation or observations."
    direction = "positive" if r > 0 else "negative"
    strength = "weak" if abs(r) < 0.3 else "moderate" if abs(r) < 0.6 else "strong"
    qualifier = " Very small sample; do not generalize." if n < 14 else " Exploratory association; not causal."
    return f"{strength.title()} {direction} sample association.{qualifier}"


def aggregate_daily_load(sessions) -> dict[date, float]:
    totals: dict[date, float] = defaultdict(float)
    for session in sessions:
        totals[session.performed_at.date()] += session_load(session.duration_minutes, session.session_rpe)
    return dict(totals)

