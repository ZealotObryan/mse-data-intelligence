import pandas as pd

from mse_analytics.data_quality import validate_price_observations


def valid_prices():
    return pd.DataFrame({
        "instrument_id": ["MSE-001", "MSE-001"],
        "observation_date": ["2026-01-02", "2026-01-05"],
        "price": [100.0, 101.5],
        "currency": ["MWK", "MWK"],
    })


def test_valid_price_rows_pass_without_mutating_input():
    frame = valid_prices()
    original = frame.copy(deep=True)
    report = validate_price_observations(frame)
    assert report.status == "passed"
    assert report.rows_received == 2
    assert report.rows_checked == 2
    pd.testing.assert_frame_equal(frame, original)


def test_missing_required_columns_reject_dataset():
    report = validate_price_observations(pd.DataFrame({"price": [10]}))
    assert report.status == "rejected"
    assert report.issues[0].code == "missing_columns"


def test_missing_values_are_rejected_with_row_locator():
    frame = valid_prices()
    frame.loc[1, "price"] = None
    report = validate_price_observations(frame)
    assert report.status == "rejected"
    issue = next(item for item in report.issues if item.code == "missing_required_values")
    assert issue.row_indices == (1,)


def test_non_numeric_and_non_positive_prices_are_rejected():
    frame = valid_prices()
    frame.loc[0, "price"] = "not-a-price"
    frame.loc[1, "price"] = 0
    report = validate_price_observations(frame)
    issue = next(item for item in report.issues if item.code == "invalid_price")
    assert issue.row_indices == (0, 1)


def test_duplicate_instrument_date_currency_is_rejected():
    frame = valid_prices()
    frame.loc[1, "observation_date"] = frame.loc[0, "observation_date"]
    report = validate_price_observations(frame)
    assert report.status == "rejected"
    assert any(item.code == "duplicate_natural_key" for item in report.issues)


def test_invalid_currency_and_instrument_are_rejected():
    frame = valid_prices()
    frame.loc[0, "instrument_id"] = " "
    frame.loc[1, "currency"] = "MW"
    report = validate_price_observations(frame)
    assert any(item.code == "invalid_instrument_or_currency" for item in report.issues)


def test_unordered_dates_are_warning_not_silent_reordering():
    frame = valid_prices().iloc[::-1]
    report = validate_price_observations(frame)
    assert report.status == "warning"
    assert any(item.code == "non_monotonic_observation_dates" for item in report.issues)


def test_unparseable_date_is_rejected():
    frame = valid_prices()
    frame.loc[0, "observation_date"] = "not-a-date"
    report = validate_price_observations(frame)
    assert any(item.code == "invalid_observation_date" for item in report.issues)
