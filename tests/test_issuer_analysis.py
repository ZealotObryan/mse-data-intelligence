import pytest

from mse_analytics.issuer_analysis import ReportingContext, analyze_issuer_period


def context(period_end="2025-12-31", currency="MWK", basis="IFRS", audited=True):
    return ReportingContext("issuer-1", period_end, currency, basis, audited)


def test_analysis_uses_prior_period_only_after_comparability_checks():
    result = analyze_issuer_period(
        context=context(),
        current_facts={"revenue": 120, "net_income": 12},
        prior_context=context("2024-12-31"),
        prior_facts={"revenue": 100, "net_income": 10},
    )
    assert result.metrics.revenue_growth == pytest.approx(.2)
    assert result.metrics.net_income_growth == pytest.approx(.2)
    assert result.issuer_id == "issuer-1"
    assert result.caveats == ()


@pytest.mark.parametrize(
    "prior_context",
    [
        context("2024-12-31", currency="USD"),
        context("2024-12-31", basis="local_gaap"),
        ReportingContext("issuer-2", "2024-12-31", "MWK", "IFRS", True),
        context("2025-12-31"),
    ],
)
def test_incomparable_prior_period_is_rejected(prior_context):
    with pytest.raises(ValueError):
        analyze_issuer_period(
            context=context(),
            current_facts={"revenue": 120},
            prior_context=prior_context,
            prior_facts={"revenue": 100},
        )


def test_prior_context_and_facts_must_be_supplied_together():
    with pytest.raises(ValueError, match="supplied together"):
        analyze_issuer_period(context=context(), current_facts={}, prior_facts={"revenue": 10})


def test_audit_status_is_exposed_as_caveat():
    result = analyze_issuer_period(
        context=context(audited=False),
        current_facts={"revenue": 100},
    )
    assert any("not confirmed as audited" in item for item in result.caveats)


def test_price_and_dividend_inputs_are_explicit_and_caveated():
    result = analyze_issuer_period(
        context=context(),
        current_facts={"net_income": 10, "weighted_average_shares": 5},
        market_price=20,
        annual_dividend_per_share=1,
    )
    assert result.metrics.price_to_earnings == pytest.approx(10)
    assert result.metrics.dividend_yield == pytest.approx(.05)
    assert len(result.caveats) == 3
    assert any("Growth metrics are unavailable" in item for item in result.caveats)


def test_context_rejects_invalid_currency_and_audit_flag():
    with pytest.raises(ValueError, match="currency"):
        analyze_issuer_period(
            context=context(currency="mkw"),
            current_facts={},
        )
    with pytest.raises(ValueError, match="audited"):
        analyze_issuer_period(
            context=ReportingContext("issuer-1", "2025-12-31", "MWK", "IFRS", "yes"),
            current_facts={},
        )


def test_prior_values_cannot_be_smuggled_into_current_facts():
    with pytest.raises(ValueError, match="prior-period"):
        analyze_issuer_period(
            context=context(),
            current_facts={"revenue": 100, "prior_revenue": 90},
            prior_context=context("2024-12-31"),
            prior_facts={"revenue": 90},
        )

def test_prior_period_must_be_chronologically_earlier():
    with pytest.raises(ValueError, match="before the current period"):
        analyze_issuer_period(
            context=context("2025-12-31"),
            current_facts={"revenue": 120},
            prior_context=context("2026-12-31"),
            prior_facts={"revenue": 100},
        )


def test_period_end_must_be_iso_date():
    with pytest.raises(ValueError, match="ISO date"):
        analyze_issuer_period(
            context=context("FY2025"),
            current_facts={},
        )
