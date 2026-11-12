import numpy as np
import pandas as pd
import pytest

from mse_analytics.risk_metrics import calculate_returns, calculate_risk_metrics


def prices(values):
    dates = pd.date_range("2025-01-01", periods=len(values), freq="B")
    return pd.Series(values, index=dates, dtype=float)


def test_simple_returns_are_calculated_correctly():
    result = calculate_returns(prices([100, 110, 99]))
    assert result.tolist() == pytest.approx([0.10, -0.10])


def test_risk_metrics_capture_gain_and_drawdown():
    result = calculate_risk_metrics(prices([100, 120, 90, 110]))
    assert result.observations == 4
    assert result.cumulative_return == pytest.approx(0.10)
    assert result.maximum_drawdown == pytest.approx(-0.25)
    assert result.annualised_volatility > 0
    assert result.sharpe_ratio is not None


def test_constant_prices_have_undefined_sharpe():
    result = calculate_risk_metrics(prices([100, 100, 100]))
    assert result.cumulative_return == pytest.approx(0)
    assert result.sharpe_ratio is None


@pytest.mark.parametrize("values", [[100], [100, 0], [100, -1], [100, np.nan]])
def test_invalid_price_inputs_are_rejected(values):
    with pytest.raises(ValueError):
        calculate_returns(prices(values))


def test_duplicate_dates_are_rejected():
    series = pd.Series([100, 110], index=pd.to_datetime(["2025-01-01", "2025-01-01"]))
    with pytest.raises(ValueError, match="unique"):
        calculate_returns(series)


def test_unsorted_dates_are_rejected():
    series = pd.Series([110, 100], index=pd.to_datetime(["2025-01-02", "2025-01-01"]))
    with pytest.raises(ValueError, match="sorted"):
        calculate_returns(series)


def test_invalid_annualisation_is_rejected():
    with pytest.raises(ValueError):
        calculate_risk_metrics(prices([100, 101]), periods_per_year=0)
