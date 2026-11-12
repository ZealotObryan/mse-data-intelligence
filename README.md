# MSE Data Intelligence — MSE Analytics

Independent financial data science and market intelligence research prototype focused on the Malawi Stock Exchange.

## Current status
The initial dashboard uses **synthetic illustrative data only**. It does not represent actual MSE prices, index values, turnover, market capitalisation, company performance or forecasts.

## Data governance
The MSE website states that access to and use of its website and data is for personal and non-commercial use. It states that parties intending commercial use must first notify the Exchange to sign a data agreement. This public-facing prototype therefore does not republish MSE market data. Before integrating real MSE data into a public product, obtain written permission and agree permitted scope, storage, display, caching and redistribution terms.

Primary source: https://www.mse.co.mw/
Market reports: https://www.mse.co.mw/market/reports

## Roadmap
1. Data-source and licensing assessment.
2. Permissioned data acquisition and provenance.
3. Validation, cleaning and relational data model.
4. Exploratory and quantitative analysis.
5. Time-series and machine-learning experiments.
6. Interactive analytics dashboard and equities research tools.
7. Investor Education & Insights Centre: MSE 101, glossary, guided learning, contextual metric explanations and evidence-based company explainers.
8. Documentation, reproducibility and deployment.

## Technology
Next.js, TypeScript, Recharts, Lucide icons. Python analytics/ETL and PostgreSQL are planned.

## Local development
Run npm install, then npm run dev.

## Research standards
Never fabricate market observations. Keep synthetic and real data clearly separated. Preserve source and retrieval metadata. Use time-ordered validation for forecasting. Document assumptions, missingness and limitations. Do not present outputs as investment advice.

No open-source licence is granted yet. Third-party data and trademarks remain subject to their owners' terms.
