"""Service orchestration for approved issuer facts and financial analysis."""
from __future__ import annotations

from typing import Any

from .issuer_analysis import IssuerAnalysisResult, ReportingContext, analyze_issuer_period
from .issuer_repository import ReadConnection, fetch_published_issuer_period


def analyze_published_issuer(
    connection: ReadConnection,
    *,
    issuer_id: str,
    period_end: str,
    prior_period_end: str | None = None,
    market_price: float | None = None,
    annual_dividend_per_share: float | None = None,
) -> IssuerAnalysisResult:
    """Calculate issuer metrics using only publication-approved issuer facts.

    The caller supplies a connection with SELECT access to the approved view.
    Price and dividend inputs remain explicit because they may come from
    different approved datasets and must be date-aligned by the caller.
    """
    current = fetch_published_issuer_period(
        connection, issuer_id=issuer_id, period_end=period_end
    )
    if current.currency is None:
        raise ValueError("published monetary facts are required to establish reporting currency")

    context = ReportingContext(
        issuer_id=current.issuer_id,
        period_end=current.period_end,
        currency=current.currency,
        reporting_basis=current.reporting_basis or "",
        audited=current.audited,
    )

    prior_context = None
    prior_facts = None
    if prior_period_end is not None:
        prior = fetch_published_issuer_period(
            connection, issuer_id=issuer_id, period_end=prior_period_end
        )
        if prior.currency is None:
            raise ValueError("prior published monetary facts are required to establish reporting currency")
        prior_context = ReportingContext(
            issuer_id=prior.issuer_id,
            period_end=prior.period_end,
            currency=prior.currency,
            reporting_basis=prior.reporting_basis or "",
            audited=prior.audited,
        )
        prior_facts = prior.facts

    return analyze_issuer_period(
        context=context,
        current_facts=current.facts,
        prior_context=prior_context,
        prior_facts=prior_facts,
        market_price=market_price,
        annual_dividend_per_share=annual_dividend_per_share,
    )
