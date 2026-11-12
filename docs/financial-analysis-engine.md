# Issuer financial analysis engine

## Purpose

`mse_analytics/financial_metrics.py` provides deterministic, transparent calculations for common issuer research metrics. It accepts already-validated financial facts and returns a typed result with unavailable metrics explained. It does not fetch source data, infer missing values, select investments or generate recommendations.

## Input contract

Pass a mapping containing any available numeric facts:

- `revenue`, `prior_revenue`
- `net_income`, `prior_net_income`
- `gross_profit`, `operating_income`
- `current_assets`, `current_liabilities`
- `total_debt`, `total_equity`
- `weighted_average_shares`
- `market_price`
- `annual_dividend_per_share`

Missing facts may be omitted or set to `None`. Values must be finite numbers; booleans, NaN and infinity are rejected. Unknown metric keys are rejected to catch mapping errors.

## Metric definitions

| Metric | Formula | Interpretation / limitation |
|---|---|---|
| Revenue growth | Current revenue / prior revenue − 1 | Prior revenue must be positive; compare like-for-like reporting periods. |
| Net income growth | Current net income / prior net income − 1 | Prior net income must be positive; growth is not meaningful across a zero/negative base. |
| Gross margin | Gross profit / revenue | Requires non-zero revenue and consistent statement definitions. |
| Operating margin | Operating income / revenue | Requires consistent classification of operating income. |
| Net margin | Net income / revenue | Can be negative when the issuer reports a loss. |
| Current ratio | Current assets / current liabilities | Requires non-zero current liabilities; a high ratio is not automatically better. |
| Debt-to-equity | Total debt / total equity | Requires non-zero equity; debt definition must be consistent across issuers. |
| Earnings per share | Net income / weighted-average shares | Simplified calculation; use reported EPS when available and preserve its basis. |
| P/E | Reference market price / positive EPS | Only returned for positive EPS; price date and reporting period must align. |
| Dividend yield | Annual dividend per share / reference market price | Requires a verified annual DPS and explicit price reference date; not a forecast. |

Growth, margins and yield are decimal ratios (0.10 means 10%). Current ratio, debt-to-equity and P/E are multiples. EPS is expressed in the input currency per share.

## Missing and invalid data

A missing input or zero denominator yields `None` and a metric-specific explanation in `unavailable_reasons`. Non-positive prior earnings/revenue do not produce conventional growth percentages. Negative EPS is retained as a valid earnings-per-share result, but P/E is withheld. No imputation, annualisation or currency conversion is performed.

## Comparability requirements before use

The caller must establish that input facts:
- Refer to the same issuer and compatible reporting period.
- Use the same currency and unit scale.
- Have compatible accounting definitions and consolidation scope.
- Distinguish audited from unaudited statements.
- Align share counts and market prices to the relevant dates.
- Have passed source, licence and data-quality checks.

For comparisons across issuers, disclose differences in fiscal year ends, reporting basis, sector and capital structure. Ratios are descriptive measures, not standalone measures of investment quality.

## Example

```python
from mse_analytics import calculate_financial_metrics

metrics = calculate_financial_metrics({
    "revenue": 1200,
    "prior_revenue": 1000,
    "net_income": 120,
    "prior_net_income": 100,
    "gross_profit": 600,
    "operating_income": 180,
    "current_assets": 500,
    "current_liabilities": 250,
    "total_debt": 300,
    "total_equity": 600,
    "weighted_average_shares": 60,
    "market_price": 30,
    "annual_dividend_per_share": 1.5,
})
print(metrics.to_dict())
```

## Current status

Unit tests cover normal calculations, missing values, zero denominators, negative earnings, invalid values and serialisation. This engine is not yet connected to a live database or the web dashboard. No actual MSE issuer financial facts have been loaded.
