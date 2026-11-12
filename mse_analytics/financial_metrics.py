"""Transparent issuer financial metrics with explicit missing-data handling.

This module performs calculations only. Callers must supply permissioned,
comparable financial facts with consistent periods, currency and accounting
basis. It does not infer missing values or issue investment recommendations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Mapping


@dataclass(frozen=True)
class FinancialMetrics:
    revenue_growth: float | None
    net_income_growth: float | None
    gross_margin: float | None
    operating_margin: float | None
    net_margin: float | None
    current_ratio: float | None
    debt_to_equity: float | None
    earnings_per_share: float | None
    price_to_earnings: float | None
    dividend_yield: float | None
    unavailable_reasons: Mapping[str, str]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""
        return asdict(self)


def _number(name: str, value: object | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError(f"{name} must be a finite number, not bool")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be a finite number or None") from exc
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _growth(current: float | None, prior: float | None) -> float | None:
    # A zero or negative prior period is not a meaningful conventional growth
    # denominator; return None rather than creating misleading percentages.
    if current is None or prior is None or prior <= 0:
        return None
    return current / prior - 1


def calculate_financial_metrics(
    facts: Mapping[str, object | None],
) -> FinancialMetrics:
    """Calculate common issuer metrics from a single comparable reporting basis.

    Supported fact keys:
      revenue, prior_revenue, net_income, prior_net_income, gross_profit,
      operating_income, current_assets, current_liabilities, total_debt,
      total_equity, weighted_average_shares, market_price,
      annual_dividend_per_share.

    Currency and reporting-period comparability, audited status, and share
    count/price date alignment must be checked by the caller before use.
    Growth values, margins and dividend yield are decimals (0.10 = 10%).
    """
    allowed = {
        "revenue", "prior_revenue", "net_income", "prior_net_income",
        "gross_profit", "operating_income", "current_assets",
        "current_liabilities", "total_debt", "total_equity",
        "weighted_average_shares", "market_price",
        "annual_dividend_per_share",
    }
    unknown = sorted(set(facts) - allowed)
    if unknown:
        raise ValueError(f"unsupported financial fact keys: {', '.join(unknown)}")

    v = {key: _number(key, facts.get(key)) for key in allowed}
    reasons: dict[str, str] = {}

    def record(name: str, value: float | None, reason: str) -> float | None:
        if value is None:
            reasons[name] = reason
        return value

    revenue_growth = record(
        "revenue_growth",
        _growth(v["revenue"], v["prior_revenue"]),
        "requires current and prior comparable revenue; prior revenue must be positive",
    )
    net_income_growth = record(
        "net_income_growth",
        _growth(v["net_income"], v["prior_net_income"]),
        "requires current and prior comparable net income; prior net income must be positive",
    )
    gross_margin = record(
        "gross_margin",
        _ratio(v["gross_profit"], v["revenue"]),
        "requires gross profit and non-zero revenue",
    )
    operating_margin = record(
        "operating_margin",
        _ratio(v["operating_income"], v["revenue"]),
        "requires operating income and non-zero revenue",
    )
    net_margin = record(
        "net_margin",
        _ratio(v["net_income"], v["revenue"]),
        "requires net income and non-zero revenue",
    )
    current_ratio = record(
        "current_ratio",
        _ratio(v["current_assets"], v["current_liabilities"]),
        "requires current assets and non-zero current liabilities",
    )
    debt_to_equity = record(
        "debt_to_equity",
        _ratio(v["total_debt"], v["total_equity"]),
        "requires total debt and non-zero total equity",
    )
    eps = record(
        "earnings_per_share",
        _ratio(v["net_income"], v["weighted_average_shares"]),
        "requires net income and non-zero weighted-average shares",
    )
    pe = record(
        "price_to_earnings",
        _ratio(v["market_price"], eps if eps is not None and eps > 0 else None),
        "requires a market price and positive earnings per share",
    )
    dividend_yield = record(
        "dividend_yield",
        _ratio(v["annual_dividend_per_share"], v["market_price"]),
        "requires annual dividend per share and non-zero reference market price",
    )

    return FinancialMetrics(
        revenue_growth=revenue_growth,
        net_income_growth=net_income_growth,
        gross_margin=gross_margin,
        operating_margin=operating_margin,
        net_margin=net_margin,
        current_ratio=current_ratio,
        debt_to_equity=debt_to_equity,
        earnings_per_share=eps,
        price_to_earnings=pe,
        dividend_yield=dividend_yield,
        unavailable_reasons=reasons,
    )
