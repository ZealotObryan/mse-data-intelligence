from __future__ import annotations

from contextlib import contextmanager

import pytest

from mse_analytics.issuer_repository import fetch_published_issuer_period


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.query = None
        self.params = None

    def execute(self, query, params=None):
        self.query = query
        self.params = params

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows):
        self.fake_cursor = FakeCursor(rows)

    @contextmanager
    def cursor(self):
        yield self.fake_cursor


def row(metric, value, *, currency="MWK", unit="currency", dataset="issuer-demo-v1",
        issuer="issuer-1", name="Demo Issuer", period="2025-12-31",
        basis="IFRS", audited=True):
    return (issuer, name, period, basis, audited, metric, value, currency, unit, dataset)


def test_reads_only_approved_public_view_and_maps_known_facts():
    connection = FakeConnection([
        row("revenue", 1200),
        row("net_income", 120, dataset="issuer-demo-v2"),
        row("weighted_average_shares", 100, currency=None, unit="shares"),
        row("unknown_disclosure_metric", 9),
    ])

    result = fetch_published_issuer_period(
        connection, issuer_id="issuer-1", period_end="2025-12-31"
    )

    assert result.facts == {
        "revenue": 1200.0,
        "net_income": 120.0,
        "weighted_average_shares": 100.0,
    }
    assert result.currency == "MWK"
    assert result.dataset_ids == ("issuer-demo-v1", "issuer-demo-v2")
    assert result.ignored_metric_codes == ("unknown_disclosure_metric",)
    assert "public_issuer_financial_facts" in connection.fake_cursor.query
    assert "FROM issuer_financial_facts" not in connection.fake_cursor.query
    assert connection.fake_cursor.params == ("issuer-1", "2025-12-31")


def test_no_public_rows_returns_lookup_error():
    with pytest.raises(LookupError, match="no approved public"):
        fetch_published_issuer_period(
            FakeConnection([]), issuer_id="issuer-1", period_end="2025-12-31"
        )


def test_duplicate_canonical_metric_fails_closed():
    with pytest.raises(ValueError, match="duplicate published metric"):
        fetch_published_issuer_period(
            FakeConnection([row("revenue", 100), row("revenue", 110)]),
            issuer_id="issuer-1", period_end="2025-12-31"
        )


def test_mixed_monetary_currencies_are_rejected():
    with pytest.raises(ValueError, match="inconsistent currencies"):
        fetch_published_issuer_period(
            FakeConnection([row("revenue", 100), row("net_income", 10, currency="USD")]),
            issuer_id="issuer-1", period_end="2025-12-31"
        )


def test_unit_mismatch_is_rejected():
    with pytest.raises(ValueError, match="must use unit"):
        fetch_published_issuer_period(
            FakeConnection([row("weighted_average_shares", 100, unit="currency")]),
            issuer_id="issuer-1", period_end="2025-12-31"
        )


def test_inconsistent_period_metadata_is_rejected():
    with pytest.raises(ValueError, match="inconsistent reporting metadata"):
        fetch_published_issuer_period(
            FakeConnection([row("revenue", 100), row("net_income", 10, audited=False)]),
            issuer_id="issuer-1", period_end="2025-12-31"
        )


@pytest.mark.parametrize("issuer_id,period_end", [("", "2025-12-31"), ("issuer-1", "FY2025")])
def test_invalid_lookup_arguments_are_rejected(issuer_id, period_end):
    with pytest.raises(ValueError):
        fetch_published_issuer_period(
            FakeConnection([]), issuer_id=issuer_id, period_end=period_end
        )
