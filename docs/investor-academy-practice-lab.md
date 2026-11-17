# Investor Academy Practice Lab — Phase 1 implementation notes

## Purpose

The Practice Lab provides guided, interactive exercises that complement the Investor Academy curriculum. Every numerical example is fictional and must remain clearly separated from live Malawi Stock Exchange (MSE) information.

## Tools included

| Tool | Learning objective | Calculation / interaction |
|---|---|---|
| Investment return simulator | Understand investment gain and loss | User-controlled investment assumptions |
| Dividend calculator | Understand dividend income and yield | Shares, dividend per share and reference price |
| Order-book simulator | Understand bids, asks and matching | Illustrative order-book mechanics |
| Market flow explorer | Distinguish primary and secondary markets | Guided market-participant flow |
| Portfolio builder | Understand allocation and concentration | Editable allocations, total validation and allocation bars |
| Risk and return explorer | Understand compounding and volatility assumptions | Annual compounding plus a simplified volatility sensitivity band |
| Financial ratio playground | Understand common statement ratios | Net margin, current ratio, debt-to-equity, simplified EPS and P/E |
| Investor knowledge assessment | Check understanding | Five multiple-choice questions with explanatory feedback |

## Financial calculation safeguards

- Portfolio allocations accept values from 0 to 100 and clearly indicate whether the total equals 100%.
- The risk and return explorer labels return and volatility as assumptions supplied by the learner. Its sensitivity band is not a confidence interval, forecast, probability estimate or maximum-loss estimate.
- Financial ratios use fictional input facts. Empty inputs and invalid denominators must not be silently treated as valid ratios.
- P/E is withheld when earnings per share or the reference price is not positive.
- The simplified EPS calculation is not a substitute for reported EPS and its accounting basis.
- No ratio or scenario generates a buy, sell or hold recommendation.
- No live MSE price, issuer fact, dividend event or corporate action is seeded into these learning tools.

## Learning experience

- Sticky, horizontally scrollable section navigation provides direct access to Market Mechanics, Portfolio Tools, Financial Analysis and the Knowledge Check.
- Each tool has a clear learning objective, immediate feedback and a concise explanation.
- Controls reflow into a single column on narrow screens.
- Assessment answers are session-only. The interface does not claim to persist learning progress.
- Touch controls, field labels, semantic sections, focus indicators and live result announcements are included where practical.

## Verification checklist

- [ ] Run web lint and production build.
- [ ] Run Python analytics tests.
- [ ] Inspect the Vercel preview at 320, 360, 375, 390, 414, 768 and desktop widths.
- [ ] Check keyboard navigation, visible focus, form labels and screen-reader announcements.
- [ ] Exercise zero, negative, blank, very large and boundary input values.
- [ ] Confirm all tools state that their examples are illustrative and not investment advice.
- [ ] Confirm existing Academy lessons and navigation remain reachable.
- [ ] Confirm no practice-tool values are represented as current MSE data.

## Out of scope for this phase

- Persisted learner progress, streaks or certificates. These require authenticated storage, access controls and a separate privacy review.
- Real-time issuer data, prices, dividends or corporate actions. These require verified source licensing, ingestion validation and publication approval.
- Personalised investment recommendations or suitability assessments.

## Release criteria

Merge only after CI passes and the preview has been visually reviewed. Production publication should be confirmed from the deployment provider; a successful GitHub check alone does not prove that the production domain has updated.
