"""Comparable-period issuer analysis adapter.

This layer validates period metadata before passing financial facts to the
calculation engine. It does not read the database or fetch market prices.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Mapping

from .financial_metrics import FinancialMetrics, calculate_financial_metrics


@dataclass(frozen=True)
class ReportingContext:
    issuer_id: str
    period_end: str
    currency: str
    reporting_basis: str
    audited: bool | None


@dataclass(frozen=True)
class IssuerAnalysisResult:
    issuer_id: str
    period_end: str
    currency: str
    reporting_basis: str
    audited: bool | None
    metrics: FinancialMetrics
    caveats: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _validate_context(context: ReportingContext, label: str) -> None:
    for field in ("issuer_id", "period_end", "currency", "reporting_basis"):
        value = getattr(context, field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}.{field} must be a non-empty string")
    if len(context.currency) != 3 or not context.currency.isalpha() or context.currency.upper() != context.currency:
        raise ValueError(f"{label}.currency must be a three-letter uppercase code")
    try:
        date.fromisoformat(context.period_end)
    except ValueError as exc:
        raise ValueError(f"{label}.period_end must be an ISO date (YYYY-MM-DD)") from exc
    if context.audited is not None and not isinstance(context.audited, bool):
        raise ValueError(f"{label}.audited must be true, false or None")


def analyze_issuer_period(
    *,
    context: ReportingContext,
    current_facts: Mapping[str, object | None],
    prior_context: ReportingContext | None = None,
    prior_facts: Mapping[str, object | None] | None = None,
    market_price: float | None = None,
    annual_dividend_per_share: float | None = None,
) -> IssuerAnalysisResult:
    """Validate comparable statement context and calculate issuer metrics.

    Financial fact keys are those accepted by calculate_financial_metrics.
    Prior-period revenue and net income are taken only from prior_facts after
    issuer, currency and reporting-basis comparability checks pass.
    """
    _validate_context(context, "context")
    facts = dict(current_facts)

    if prior_context is not None or prior_facts is not None:
        if prior_context is None or prior_facts is None:
            raise ValueError("prior_context and prior_facts must be supplied together")
        _validate_context(prior_context, "prior_context")
        if prior_context.issuer_id != context.issuer_id:
            raise ValueError("prior and current periods must belong to the same issuer")
        if prior_context.currency != context.currency:
            raise ValueError("prior and current periods must use the same currency")
        if prior_context.reporting_basis != context.reporting_basis:
            raise ValueError("prior and current periods must use the same reporting basis")
        if date.fromisoformat(prior_context.period_end) >= date.fromisoformat(context.period_end):
            raise ValueError("prior period must end before the current period")
        if "prior_revenue" in facts or "prior_net_income" in facts:
            raise ValueError("prior-period values must come from prior_facts, not current_facts")
        if "revenue" in prior_facts:
            facts["prior_revenue"] = prior_facts["revenue"]
        if "net_income" in prior_facts:
            facts["prior_net_income"] = prior_facts["net_income"]

    if "market_price" in facts or "annual_dividend_per_share" in facts:
        raise ValueError("market_price and dividend inputs must be supplied through their explicit arguments")
    facts["market_price"] = market_price
    facts["annual_dividend_per_share"] = annual_dividend_per_share
    metrics = calculate_financial_metrics(facts)

    caveats: list[str] = []
    if context.audited is not True:
        caveats.append("Current financial statements are not confirmed as audited.")
    if prior_context is not None and prior_context.audited is not True:
        caveats.append("Prior-period financial statements are not confirmed as audited.")
    if prior_context is None:
        caveats.append("Growth metrics are unavailable unless comparable prior-period facts are supplied.")
    if market_price is not None:
        caveats.append("Valuation metrics depend on the caller-supplied reference price and its date alignment.")
    if annual_dividend_per_share is not None:
        caveats.append("Dividend yield depends on the caller-supplied annual dividend per share and price reference.")
    return IssuerAnalysisResult(
        issuer_id=context.issuer_id,
        period_end=context.period_end,
        currency=context.currency,
        reporting_basis=context.reporting_basis,
        audited=context.audited,
        metrics=metrics,
        caveats=tuple(caveats),
    )
