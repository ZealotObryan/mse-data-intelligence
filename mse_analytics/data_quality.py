"""Non-destructive validation helpers for staged market observations.

The validator flags suspicious or incomplete rows; it never silently edits,
drops or imputes source observations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class QualityIssue:
    code: str
    severity: str
    message: str
    row_indices: tuple[Any, ...] = ()


@dataclass(frozen=True)
class QualityReport:
    rows_received: int
    rows_checked: int
    issues: tuple[QualityIssue, ...]

    @property
    def passed(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def status(self) -> str:
        if not self.passed:
            return "rejected"
        if self.issues:
            return "warning"
        return "passed"


def validate_price_observations(
    frame: pd.DataFrame,
    *,
    required_columns: tuple[str, ...] = (
        "instrument_id", "observation_date", "price", "currency"
    ),
) -> QualityReport:
    """Check staged price rows and return issues without mutating the input.

    Expected grain: one price per instrument, observation date and currency.
    Duplicate natural keys and invalid/non-positive prices are errors.
    Missing metadata and non-monotonic ordering are warnings so a reviewer can
    distinguish data defects from ordering or completeness concerns.
    """
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")

    missing_columns = tuple(column for column in required_columns if column not in frame.columns)
    if missing_columns:
        issue = QualityIssue(
            code="missing_columns",
            severity="error",
            message=f"required columns are missing: {', '.join(missing_columns)}",
        )
        return QualityReport(rows_received=len(frame), rows_checked=0, issues=(issue,))

    issues: list[QualityIssue] = []
    checked = frame.copy(deep=False)

    missing_mask = checked.loc[:, required_columns].isna().any(axis=1)
    if missing_mask.any():
        issues.append(QualityIssue(
            code="missing_required_values",
            severity="error",
            message="one or more required values are missing",
            row_indices=tuple(checked.index[missing_mask].tolist()),
        ))

    instrument_ok = checked["instrument_id"].map(
        lambda value: isinstance(value, str) and bool(value.strip())
    )
    currency_ok = checked["currency"].map(
        lambda value: isinstance(value, str) and len(value.strip()) == 3
    )
    invalid_metadata = ~(instrument_ok & currency_ok)
    if invalid_metadata.any():
        issues.append(QualityIssue(
            code="invalid_instrument_or_currency",
            severity="error",
            message="instrument_id must be non-empty and currency must be a three-letter code",
            row_indices=tuple(checked.index[invalid_metadata].tolist()),
        ))

    dates = pd.to_datetime(checked["observation_date"], errors="coerce", utc=True)
    invalid_dates = dates.isna()
    if invalid_dates.any():
        issues.append(QualityIssue(
            code="invalid_observation_date",
            severity="error",
            message="observation_date contains values that cannot be parsed as dates",
            row_indices=tuple(checked.index[invalid_dates].tolist()),
        ))

    prices = pd.to_numeric(checked["price"], errors="coerce")
    invalid_prices = prices.isna() | ~prices.map(lambda value: pd.notna(value) and value > 0)
    if invalid_prices.any():
        issues.append(QualityIssue(
            code="invalid_price",
            severity="error",
            message="price must be numeric and greater than zero",
            row_indices=tuple(checked.index[invalid_prices].tolist()),
        ))

    valid = ~(missing_mask | invalid_dates | invalid_prices | invalid_metadata)
    keys = pd.DataFrame({
        "instrument_id": checked["instrument_id"],
        "observation_date": dates,
        "currency": checked["currency"],
    }, index=checked.index)
    duplicate_mask = valid & keys.duplicated(keep=False)
    if duplicate_mask.any():
        issues.append(QualityIssue(
            code="duplicate_natural_key",
            severity="error",
            message="more than one row exists for an instrument/date/currency key",
            row_indices=tuple(checked.index[duplicate_mask].tolist()),
        ))

    valid_dates = dates[~invalid_dates]
    if len(valid_dates) > 1 and not valid_dates.is_monotonic_increasing:
        issues.append(QualityIssue(
            code="non_monotonic_observation_dates",
            severity="warning",
            message="observations are not ordered by ascending date; sort explicitly before time-series analysis",
        ))

    return QualityReport(
        rows_received=len(frame),
        rows_checked=int(valid.sum()),
        issues=tuple(issues),
    )
