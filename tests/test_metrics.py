import numpy as np
import pandas as pd
import pytest

from analysis.mse_analytics.metrics import (
    annualised_volatility, maximum_drawdown, simple_returns,
    validate_price_frame, wealth_index,
)


def test_simple_returns():
    result = simple_returns(pd.Series([100, 110, 99]))
    assert np.isnan(result.iloc[0])
    assert result.iloc[1] == pytest.approx(0.10)
    assert result.iloc[2] == pytest.approx(-0.10)


def test_annualised_volatility():
    result = annualised_volatility(pd.Series([0.01, -0.01, 0.02, -0.02]))
    assert result > 0


def test_wealth_index_compounds():
    result = wealth_index(pd.Series([0.10, -0.10]))
    assert result.iloc[-1] == pytest.approx(0.99)


def test_maximum_drawdown():
    assert maximum_drawdown(pd.Series([0.10, -0.20, 0.05])) == pytest.approx(-0.20)


def test_invalid_prices_rejected():
    with pytest.raises(ValueError):
        simple_returns(pd.Series([100, 0, 110]))


def test_quality_report_flags_duplicates_and_missing_values():
    frame = pd.DataFrame({"date": ["2026-01-01", "2026-01-01", "bad"], "close": [10, None, 12]})
    report = validate_price_frame(frame)
    assert report["row_count"] == 3
    assert report["invalid_dates"] == 1
    assert report["missing_close"] == 1
    assert report["duplicate_dates"] == 2
