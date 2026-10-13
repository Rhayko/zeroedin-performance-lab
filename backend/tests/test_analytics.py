from datetime import date, timedelta
from app.analytics import baseline_status, deviations, pearson, rolling_mean, session_load, set_volume

def test_load_calculations_are_transparent():
    assert session_load(60, 7.5) == 450
    assert set_volume(5, 100) == 500

def test_baseline_requires_unique_days():
    start=date(2025,1,1)
    assert baseline_status([start,start])["days_observed"] == 1
    status=baseline_status([start+timedelta(days=i) for i in range(28)])
    assert status["state"] == "established"
    assert status["progress_percent"] == 100

def test_rolling_mean_and_deviation():
    assert rolling_mean([1,2,3],2) == [1,1.5,2.5]
    assert deviations([1,2,3]) == [-1,0,1]

def test_pearson_handles_small_or_constant_samples():
    assert pearson([1,2],[2,3]) is None
    assert pearson([1,1,1],[1,2,3]) is None
    assert pearson([1,2,3],[2,4,6]) == 1

