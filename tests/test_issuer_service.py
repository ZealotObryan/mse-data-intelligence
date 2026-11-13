from __future__ import annotations

from contextlib import contextmanager

import pytest

from mse_analytics.issuer_service import analyze_published_issuer


class Cursor:
    def __init__(self, rows_by_period):
        self.rows_by_period = rows_by_period
        self.rows = []

    def execute(self, query, params=None):
        assert "public_issuer_financial_facts" in query
        assert "issuer_financial_facts " not in query
        self.rows = self.rows_by_period.get(params[1], [])

    def fetchall(self):
        return self.rows


class Connection:
    def __init__(self, rows_by_period):
        self.cursor_instance = Cursor(rows_by_period)

    @contextmanager
    def cursor(self):
        yield self.cursor_instance


def rows(period, *, revenue, income, currency="MWK", basis="IFRS", audited=True):
    return [
        ("issuer-1", "Demo issuer", period, basis, audited, "revenue", revenue, currency, "currency", "demo-"+period),
        ("issuer-1", "Demo issuer", period, basis, audited, "net_income", income, currency, "currency", "demo-"+period),
    ]


def test_service_analyzes_current_and_comparable_prior_approved_periods():
    connection = Connection({
        "2025-12-31": rows("2025-12-31", revenue=120, income=12),
        "2024-12-31": rows("2024-12-31", revenue=100, income=10),
    })

    result = analyze_published_issuer(
        connection,
        issuer_id="issuer-1",
        period_end="2025-12-31",
        prior_period_end="2024-12-31",
    )

    assert result.metrics.revenue_growth == pytest.approx(.2)
    assert result.metrics.net_income_growth == pytest.approx(.2)
    assert result.currency == "MWK"
    assert result.caveats == ()


def test_service_does_not_invent_growth_without_prior_period():
    connection = Connection({
        "2025-12-31": rows("2025-12-31", revenue=120, income=12),
    })

    result = analyze_published_issuer(
        connection, issuer_id="issuer-1", period_end="2025-12-31"
    )

    assert result.metrics.revenue_growth is None
    assert any("Growth metrics are unavailable" in caveat for caveat in result.caveats)


def test_service_rejects_incomparable_prior_currency():
    connection = Connection({
        "2025-12-31": rows("2025-12-31", revenue=120, income=12),
        "2024-12-31": rows("2024-12-31", revenue=100, income=10, currency="USD"),
    })

    with pytest.raises(ValueError, match="same currency"):
        analyze_published_issuer(
            connection, issuer_id="issuer-1", period_end="2025-12-31",
            prior_period_end="2024-12-31",
        )
