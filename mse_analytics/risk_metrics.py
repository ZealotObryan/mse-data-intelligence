"""Transparent risk and return metrics for ordered price observations.

Inputs are price observations, not MSE market data. Callers are responsible for
providing permissioned, correctly adjusted prices and documenting their source.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RiskMetrics:
    observations: int
    cumulative_return: float
    annualised_return: float
    annualised_volatility: float
    maximum_drawdown: float
    sharpe_ratio: float | None


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate simple period returns from a positive, dated price series."""
    if not isinstance(prices, pd.Series):
        raise TypeError("prices must be a pandas Series indexed by dates")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must have a DatetimeIndex")
    if prices.empty:
        raise ValueError("prices must contain at least two observations")
    if len(prices) < 2:
        raise ValueError("prices must contain at least two observations")
    if prices.index.has_duplicates:
        raise ValueError("price dates must be unique")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices must be sorted in ascending date order")

    values = pd.to_numeric(prices, errors="coerce").astype(float)
    if not np.isfinite(values.to_numpy()).all():
        raise ValueError("prices must contain only finite numeric values")
    if (values <= 0).any():
        raise ValueError("prices must be greater than zero")

    return values.pct_change().dropna().rename("return")


def calculate_risk_metrics(
    prices: pd.Series,
    *,
    periods_per_year: int = 252,
    annual_risk_free_rate: float = 0.0,
) -> RiskMetrics:
    """Calculate annualised return, volatility, drawdown and Sharpe ratio.

    Assumes equally spaced observations (normally daily trading observations).
    The risk-free rate is an annual effective rate converted to a per-period
    rate. Annualised return uses geometric compounding over observed periods.
    """
    if isinstance(periods_per_year, bool) or not isinstance(periods_per_year, int) or periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")
    if not np.isfinite(annual_risk_free_rate) or annual_risk_free_rate <= -1:
        raise ValueError("annual_risk_free_rate must be finite and greater than -1")

    returns = calculate_returns(prices)
    periods = len(returns)
    cumulative_return = float((prices.iloc[-1] / prices.iloc[0]) - 1)
    annualised_return = float((1 + cumulative_return) ** (periods_per_year / periods) - 1)

    volatility = float(returns.std(ddof=1) * np.sqrt(periods_per_year)) if periods > 1 else float("nan")
    wealth = pd.concat([pd.Series([1.0]), (1 + returns).reset_index(drop=True).cumprod()], ignore_index=True)
    drawdown = wealth / wealth.cummax() - 1
    maximum_drawdown = float(drawdown.min())

    periodic_rf = (1 + annual_risk_free_rate) ** (1 / periods_per_year) - 1
    excess = returns - periodic_rf
    excess_std = float(excess.std(ddof=1))
    sharpe = (
        float(excess.mean() / excess_std * np.sqrt(periods_per_year))
        if periods > 1 and np.isfinite(excess_std) and excess_std > 0
        else None
    )

    return RiskMetrics(
        observations=len(prices),
        cumulative_return=cumulative_return,
        annualised_return=annualised_return,
        annualised_volatility=volatility,
        maximum_drawdown=maximum_drawdown,
        sharpe_ratio=sharpe,
    )
