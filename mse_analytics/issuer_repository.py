"""Read-only access to the approved issuer financial facts view.

This adapter deliberately queries only public_issuer_financial_facts. It does
not read base tables, bypass publication controls, or create connections.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol, Sequence


class ReadCursor(Protocol):
    def execute(self, query: str, params: Sequence[Any] | None = None) -> Any: ...
    def fetchall(self) -> list[Sequence[Any]]: ...


class ReadConnection(Protocol):
    def cursor(self) -> Any: ...


@dataclass(frozen=True)
class PublishedIssuerPeriod:
    issuer_id: str
    issuer_name: str
    period_end: str
    currency: str | None
    reporting_basis: str | None
    audited: bool | None
    dataset_ids: tuple[str, ...]
    facts: dict[str, float]
    ignored_metric_codes: tuple[str, ...]


# Only exact, documented metric codes are mapped. No fuzzy label matching.
_METRIC_UNITS = {
    "revenue": ("revenue", "currency"),
    "net_income": ("net_income", "currency"),
    "gross_profit": ("gross_profit", "currency"),
    "operating_income": ("operating_income", "currency"),
    "current_assets": ("current_assets", "currency"),
    "current_liabilities": ("current_liabilities", "currency"),
    "total_debt": ("total_debt", "currency"),
    "total_equity": ("total_equity", "currency"),
    "weighted_average_shares": ("weighted_average_shares", "shares"),
}


def fetch_published_issuer_period(
    connection: ReadConnection, *, issuer_id: str, period_end: str
) -> PublishedIssuerPeriod:
    """Fetch one issuer period from the publication-approved read view.

    Monetary facts must share one currency. Duplicate canonical metrics,
    inconsistent statement metadata, malformed dates, or unit mismatches fail
    closed instead of silently selecting or converting values.
    """
    if not isinstance(issuer_id, str) or not issuer_id.strip():
        raise ValueError("issuer_id must be a non-empty string")
    if not isinstance(period_end, str) or not period_end.strip():
        raise ValueError("period_end must be an ISO date")
    try:
        date.fromisoformat(period_end)
    except ValueError as exc:
        raise ValueError("period_end must be an ISO date (YYYY-MM-DD)") from exc

    query = """
        SELECT issuer_id, display_name, period_end, reporting_basis, audited,
               metric_code, numeric_value, currency, unit, dataset_id
        FROM public_issuer_financial_facts
        WHERE issuer_id = %s AND period_end = %s
        ORDER BY metric_code, dataset_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (issuer_id, period_end))
        rows = cursor.fetchall()

    if not rows:
        raise LookupError("no approved public financial facts found for this issuer period")

    first = rows[0]
    expected_identity = (first[0], first[1], str(first[2]), first[3], first[4])
    if expected_identity[0] != issuer_id or expected_identity[2] != period_end:
        raise ValueError("database returned a mismatched issuer period")

    facts: dict[str, float] = {}
    datasets: set[str] = set()
    ignored: set[str] = set()
    currencies: set[str] = set()

    for row in rows:
        identity = (row[0], row[1], str(row[2]), row[3], row[4])
        if identity != expected_identity:
            raise ValueError("issuer period rows have inconsistent reporting metadata")

        metric_code = row[5]
        numeric_value = row[6]
        currency = row[7]
        unit = row[8]
        dataset_id = row[9]
        if dataset_id:
            datasets.add(str(dataset_id))

        mapping = _METRIC_UNITS.get(metric_code)
        if mapping is None:
            ignored.add(str(metric_code))
            continue
        target_key, expected_unit = mapping
        if unit != expected_unit:
            raise ValueError(f"metric {metric_code!r} must use unit {expected_unit!r}")
        if expected_unit == "currency":
            if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha() or currency.upper() != currency:
                raise ValueError(f"metric {metric_code!r} requires a three-letter currency")
            currencies.add(currency)
        elif currency is not None and (not isinstance(currency, str) or len(currency) != 3):
            raise ValueError(f"metric {metric_code!r} has an invalid currency")

        if target_key in facts:
            raise ValueError(f"duplicate published metric {target_key!r}; refusing ambiguous analysis")
        try:
            value = float(numeric_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"metric {metric_code!r} is not numeric") from exc
        if not __import__("math").isfinite(value):
            raise ValueError(f"metric {metric_code!r} must be finite")
        facts[target_key] = value

    if len(currencies) > 1:
        raise ValueError("published monetary facts use inconsistent currencies")

    return PublishedIssuerPeriod(
        issuer_id=issuer_id,
        issuer_name=str(first[1]),
        period_end=period_end,
        currency=next(iter(currencies), None),
        reporting_basis=first[3],
        audited=first[4],
        dataset_ids=tuple(sorted(datasets)),
        facts=facts,
        ignored_metric_codes=tuple(sorted(ignored)),
    )
