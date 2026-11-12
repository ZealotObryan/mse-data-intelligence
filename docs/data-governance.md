# Data governance and acquisition plan

The MSE website publishes daily, weekly, monthly and quarterly market reports. Its disclaimer states that website and data use is for personal and non-commercial purposes and that commercial users must notify the Exchange to sign a data agreement. It also says data is supplied as-is and may change without notice.

The public dashboard must not reproduce MSE market data until written permission and a data agreement establish what is allowed. The current dashboard therefore uses synthetic values for interface demonstration only.

## Permission request topics
- Historical daily equity and index data availability and price.
- MASI, DSI and FSI history and calculation methodology.
- Corporate actions and dividend history.
- Permitted academic research and portfolio demonstration use.
- Public display of derived metrics and charts.
- Storage, caching, redistribution and attribution requirements.

## Planned data model
- instruments: security identifiers, names, asset class, listing status
- prices: instrument_id, observation_date, open, high, low, close, volume, turnover, source_id
- indices: index_code, observation_date, index_value, source_id
- corporate_actions: instrument_id, action_type, ex_date, effective_date, amount, source_id
- company_financials: instrument_id, period_end, metric_code, metric_value, currency, source_id
- macro_indicators: indicator_code, observation_date, value, unit, source_id
- sources: publisher, source_url, retrieved_at, licence_reference, checksum

Preserve provenance. Do not ingest data unless its use is permitted.
