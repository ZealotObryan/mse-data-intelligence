import pytest

from mse_analytics.financial_metrics import calculate_financial_metrics


def test_financial_metrics_calculate_from_comparable_facts():
    result = calculate_financial_metrics({
        "revenue": 1200, "prior_revenue": 1000,
        "net_income": 120, "prior_net_income": 100,
        "gross_profit": 600, "operating_income": 180,
        "current_assets": 500, "current_liabilities": 250,
        "total_debt": 300, "total_equity": 600,
        "weighted_average_shares": 60,
        "market_price": 30, "annual_dividend_per_share": 1.5,
    })
    assert result.revenue_growth == pytest.approx(.20)
    assert result.net_income_growth == pytest.approx(.20)
    assert result.gross_margin == pytest.approx(.50)
    assert result.operating_margin == pytest.approx(.15)
    assert result.net_margin == pytest.approx(.10)
    assert result.current_ratio == pytest.approx(2)
    assert result.debt_to_equity == pytest.approx(.5)
    assert result.earnings_per_share == pytest.approx(2)
    assert result.price_to_earnings == pytest.approx(15)
    assert result.dividend_yield == pytest.approx(.05)
    assert result.unavailable_reasons == {}


def test_missing_facts_return_none_with_explanation():
    result = calculate_financial_metrics({"revenue": 100, "prior_revenue": 0})
    assert result.revenue_growth is None
    assert "revenue_growth" in result.unavailable_reasons
    assert result.net_margin is None


def test_negative_prior_earnings_does_not_report_growth_percentage():
    result = calculate_financial_metrics({"net_income": 50, "prior_net_income": -10})
    assert result.net_income_growth is None


def test_zero_equity_and_zero_current_liabilities_are_not_divided_by():
    result = calculate_financial_metrics({
        "total_debt": 10, "total_equity": 0,
        "current_assets": 10, "current_liabilities": 0,
    })
    assert result.debt_to_equity is None
    assert result.current_ratio is None


def test_non_positive_eps_does_not_report_pe():
    result = calculate_financial_metrics({"net_income": -10, "weighted_average_shares": 5, "market_price": 20})
    assert result.earnings_per_share == pytest.approx(-2)
    assert result.price_to_earnings is None


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "not-a-number"])
def test_invalid_fact_values_are_rejected(value):
    with pytest.raises((TypeError, ValueError)):
        calculate_financial_metrics({"revenue": value})


def test_unknown_fact_keys_are_rejected():
    with pytest.raises(ValueError, match="unsupported"):
        calculate_financial_metrics({"revenue": 10, "made_up_metric": 20})


def test_metrics_are_serialisable_to_dict():
    result = calculate_financial_metrics({"revenue": 100, "prior_revenue": 80})
    payload = result.to_dict()
    assert payload["revenue_growth"] == pytest.approx(.25)
    assert isinstance(payload["unavailable_reasons"], dict)

@pytest.mark.parametrize(
    "facts,metric",
    [
        ({"total_debt": 20, "total_equity": -5}, "debt_to_equity"),
        ({"current_assets": 20, "current_liabilities": -5}, "current_ratio"),
        ({"net_income": 20, "weighted_average_shares": 0}, "earnings_per_share"),
        ({"market_price": 0, "annual_dividend_per_share": 2}, "dividend_yield"),
        ({"net_income": 20, "weighted_average_shares": 2, "market_price": -1}, "price_to_earnings"),
    ],
)
def test_ratios_with_economically_invalid_denominators_are_unavailable(facts, metric):
    result = calculate_financial_metrics(facts)
    assert getattr(result, metric) is None
    assert metric in result.unavailable_reasons
