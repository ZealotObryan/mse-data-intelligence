"""Transparent financial metrics with strict input validation.

These functions do not fetch or embed MSE market data. They operate on
permissioned user-supplied observations or explicitly labelled test data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def simple_returns(prices: pd.Series) -> pd.Series:
    """Calculate close-to-close simple returns, preserving missing values."""
    values = pd.to_numeric(prices, errors="coerce")
    if (values.dropna() <= 0).any():
        raise ValueError("Prices must be positive when present.")
    return values.pct_change(fill_method=None).rename("simple_return")


def annualised_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Sample standard deviation scaled by sqrt(periods_per_year)."""
    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive.")
    if len(clean) < 2:
        return float("nan")
    return float(clean.std(ddof=1) * np.sqrt(periods_per_year))


def wealth_index(returns: pd.Series, initial_value: float = 1.0) -> pd.Series:
    """Compound periodic returns into a wealth index."""
    if initial_value <= 0:
        raise ValueError("initial_value must be positive.")
    clean = pd.to_numeric(returns, errors="coerce")
    if (clean.dropna() < -1).any():
        raise ValueError("A simple return cannot be below -100%.")
    return (1 + clean.fillna(0)).cumprod().mul(initial_value).rename("wealth_index")


def maximum_drawdown(returns: pd.Series) -> float:
    """Return the minimum peak-to-trough percentage drawdown."""
    wealth = wealth_index(returns)
    if wealth.empty:
        return float("nan")
    drawdown = wealth.div(wealth.cummax()).sub(1)
    return float(drawdown.min())


def validate_price_frame(frame: pd.DataFrame) -> dict[str, object]:
    """Return auditable quality checks for a date/close price frame."""
    required = {"date", "close"}
    missing_columns = sorted(required.difference(frame.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    dates = pd.to_datetime(frame["date"], errors="coerce")
    close = pd.to_numeric(frame["close"], errors="coerce")
    return {
        "row_count": int(len(frame)),
        "invalid_dates": int(dates.isna().sum()),
        "missing_close": int(close.isna().sum()),
        "non_positive_close": int((close.dropna() <= 0).sum()),
        "duplicate_dates": int(dates.duplicated(keep=False).sum()),
        "out_of_order_dates": bool(dates.dropna().is_monotonic_increasing is False),
    }
