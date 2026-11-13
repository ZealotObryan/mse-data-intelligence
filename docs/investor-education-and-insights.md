# Investor Education & Insights Centre

## Product objective

Make MSE Data Intelligence useful to both experienced market participants and people who are new to investing. The platform should not merely display market data; it should help users understand the market, interpret information and recognise risks before making their own decisions.

The experience has two complementary modes:

- **Explore the market** — detailed market data, company analysis, financial metrics, comparisons and research tools.
- **Learn the market** — plain-language explanations, guided lessons, worked examples, glossary entries and contextual explanations embedded throughout the dashboard.

## Target users

1. **New and aspiring investors** who need foundational knowledge and confidence to understand the Malawi Stock Exchange.
2. **Developing investors** who understand basic concepts but need help interpreting company information, market movements and risk.
3. **Experienced investors and analysts** who need deeper quantitative analysis, source transparency and research tools.

## Core modules

### 1. MSE 101 — beginner pathway

A structured introduction covering:

- What the Malawi Stock Exchange is and how it operates.
- What shares represent and why companies issue shares.
- How investors can participate, including the role of licensed brokers and the applicable account-opening process.
- How orders, trading, settlement and ownership work, subject to verified MSE procedures.
- How investors may earn returns through dividends and changes in share prices.
- How losses occur, including market, company, liquidity and concentration risks.
- How to read market reports, company announcements and financial statements.

Lessons should use plain English, local examples where verified, diagrams, short knowledge checks and a clear progression from beginner to intermediate.

### 2. Investor glossary

Provide searchable, concise definitions for terms such as share, equity, dividend, yield, market capitalisation, liquidity, turnover, volatility, price-to-earnings ratio, earnings per share, rights issue, bonus issue, corporate action, bid, ask and index.

Each entry should include:
- A plain-language definition.
- Why the term matters to an investor.
- A simple worked example using clearly labelled illustrative figures.
- Links to related concepts.

### 3. Market explained

Contextual explanations of:
- Index movements and what they do and do not tell an investor.
- Price changes, trading activity, turnover and liquidity.
- Market breadth and sector performance where the underlying data supports it.
- Corporate announcements and events that may affect securities.
- The difference between a confirmed event, a plausible explanation and speculation.

### 4. Company explainers

For each issuer with permissioned, verified data, provide:
- What the company does and its sector.
- Historical financial performance and key financial statement indicators.
- Dividend history and relevant corporate actions.
- Valuation measures with definitions and limitations.
- Business, financial, market and liquidity risks.
- Source links, reporting periods, publication dates and data freshness.

Do not create issuer profiles or financial histories from synthetic demo data. Synthetic examples must be explicitly labelled as fictional illustrations.

### 5. Contextual insight cards

Explain dashboard metrics in context. Examples:
- "What does this price movement mean?"
- "Why does trading volume matter?"
- "What can a high P/E ratio indicate?"
- "Why might a share be difficult to sell?"
- "What should I check before interpreting a dividend yield?"

Each insight should show the underlying evidence, calculation or source, observation period, assumptions and limitations. Where causation is not established, use language such as "may be associated with" rather than asserting a cause.

### 6. Guided learning and practice

Offer short learning paths:
- Beginner: understand the exchange and shares.
- Foundation: understand prices, returns, dividends and risk.
- Intermediate: read company reports and compare securities.
- Advanced: understand valuation, portfolio risk and quantitative metrics.

Use quizzes, worked examples and simulated exercises. Simulations must be clearly separated from real trading and must not imply that practice outcomes predict future returns.

## UX principles

- Offer a clear "New to investing?" entry point on the dashboard.
- Use plain English first, with technical terminology introduced progressively.
- Add "What does this mean?" explanations beside unfamiliar metrics.
- Let users move from a simple explanation to the detailed methodology.
- Avoid overwhelming beginners with dense tables or unexplained ratios.
- Keep advanced analysis available without making it the default learning experience.
- Make learning content searchable and accessible on mobile.

## Trust, suitability and responsible-use rules

- Education is not personalised financial advice, a recommendation to buy or sell, or a guarantee of returns.
- Never label a security as a "buy", "sell" or "guaranteed winner" based solely on an automated metric.
- Explain that all investments involve risk, including loss of capital.
- Distinguish verified facts, calculated metrics, model estimates, interpretation and opinion.
- Show sources, dates, reporting periods, calculation methods and data-quality warnings.
- Do not infer causation from correlation or a price movement alone.
- Do not present stale, incomplete, synthetic or unlicensed data as current market information.
- Direct users to official MSE information and appropriately licensed market professionals for procedural or investment decisions.
- Obtain data permissions before using or redistributing MSE market information.

## Phased delivery

### Phase 1 — beginner foundations
- Add a "New to investing?" entry point and MSE 101 landing page.
- Publish foundational lessons and a searchable glossary.
- Add contextual definitions to key dashboard metrics.
- Use illustrative examples only until permissioned real data is available.

### Phase 2 — market interpretation
- Add market movement explainers and guided chart reading.
- Add quizzes and progress tracking.
- Add clear distinctions between facts, calculations and interpretations.

### Phase 3 — company research
- Build issuer explainers from permissioned, verified filings and market data.
- Add financial statement summaries, dividend history, valuation context and risk disclosures.
- Link every claim and figure to its source and reporting period.

### Phase 4 — personalised learning, not personalised trading advice
- Allow users to choose learning goals and experience level.
- Recommend educational content based on learning progress.
- Keep educational guidance separate from investment recommendations or execution.

## Success measures

- Beginner onboarding completion rate.
- Lesson completion and quiz improvement.
- Glossary searches that lead to useful explanations.
- Use of contextual "What does this mean?" help.
- Repeat engagement with learning content.
- User-reported understanding and confidence, measured without implying investment performance.
- Accuracy, freshness and source coverage of published insights.

## MVP acceptance criteria

1. A first-time visitor can find the beginner pathway immediately.
2. A beginner can understand core market terms without leaving the platform.
3. Important dashboard metrics have plain-language explanations.
4. Learning examples are visibly labelled as illustrative where applicable.
5. Every real-market insight has traceable evidence and dates.
6. No feature presents unsupported predictions or automated buy/sell instructions.


## Expanded MSE 101 curriculum

The first guided pathway is delivered as nine sequential lessons. Each lesson includes explanatory sections, a fictional worked example, a key takeaway and a knowledge check with feedback. Users can open lessons in any order and mark them complete; the initial progress indicator is session-based and is not an account-level learning record.

| Lesson | Learning outcome |
|---|---|
| 1. The stock exchange: the big picture | Explain the purpose of an exchange, the role of MSE, and the difference between primary and secondary markets. |
| 2. Shares and ownership | Explain what a share represents, shareholder rights, equity capital and dilution. |
| 3. How to prepare to invest | Identify personal financial considerations, the role of licensed brokers and questions to ask before opening an account. |
| 4. Orders, trading and settlement | Distinguish market and limit orders, order execution and settlement. |
| 5. Returns, dividends and costs | Calculate a simple price return and distinguish capital gains, dividends, costs and taxes. |
| 6. Read prices and market information | Interpret last price, volume, turnover, liquidity and index information with attention to freshness. |
| 7. Understand company reports | Identify the purpose of the income statement, statement of financial position and cash-flow statement; interpret selected ratios cautiously. |
| 8. Risk, diversification and investor behaviour | Recognise common risk types, concentration risk and behavioural traps. |
| 9. A practical investor due-diligence checklist | Apply a structured set of verification questions before making an investment decision. |

### Lesson content and assessment standards

- Use plain English first, then introduce the technical term and its meaning.
- Include a practical explanation of why each concept matters, not only a dictionary definition.
- Use worked examples with transparent arithmetic and clearly fictional MWK figures. Never imply that an illustrative company, price or transaction is real.
- Knowledge checks should test understanding and explain why the correct answer is correct. They are educational checks, not a suitability test or a recommendation.
- Keep progress tracking honest: session-only progress must not be described as saved to a user account.
- Treat broker licensing, account opening, trading hours, order handling, settlement cycles, taxes and other procedural details as changeable. Link users to current official sources rather than inventing or hardcoding unverified MSE procedures.
- Do not imply that a company must pay dividends, that a limit order will execute, that diversification prevents all losses, or that historical performance predicts future returns.

### Further curriculum roadmap

After the beginner pathway, develop separate foundation/intermediate modules for reading annual reports in depth, interpreting corporate announcements and corporate actions, valuation methods and their limitations, portfolio construction, risk measurement, and quantitative market analysis. Advanced content should show assumptions, formulas, data requirements and limitations, and should only use real market or issuer information when source permissions and provenance are established.


## Three-stage guided curriculum

The Academy now groups its guided content into three learning levels. Each lesson contains a substantive explanation, a fictional worked example, a key takeaway and a multiple-choice knowledge check with feedback. Lesson completion and quiz selections are session-only in the current prototype; they are not stored against user accounts.

### Beginner — MSE 101 (9 lessons)

1. The stock exchange: the big picture
2. Shares and ownership
3. Prepare before investing
4. Orders, trading and settlement
5. Returns, dividends and costs
6. Read prices and market information
7. Understand company reports
8. Risk, diversification and investor behaviour
9. A practical investor due-diligence checklist

### Foundation — Company analysis (5 lessons)

1. Read an annual report systematically
2. Analyse income, margins and earnings quality
3. Understand balance sheets and cash flow
4. Use financial ratios with context
5. Analyse dividends and corporate actions

### Intermediate — Portfolio and market research (6 lessons)

1. Valuation: price, value and assumptions
2. Portfolio construction and diversification
3. Measure portfolio performance fairly
4. Risk measurement: volatility, drawdown and Sharpe ratio
5. Market data quality in thin markets
6. Write a defensible research conclusion

### Teaching and assessment rules

- Use plain language, define technical terms and explain why each concept matters.
- Show calculations step by step using fictional MWK figures. Clearly identify every example as illustrative.
- Explain correct and incorrect quiz answers; quizzes are for learning, not investment suitability.
- Distinguish market facts, calculated metrics, interpretation and model estimates.
- State assumptions, period alignment, data requirements and limitations for valuation and risk measures.
- Treat MSE procedures, broker requirements, fees, taxes and settlement arrangements as changeable; link to official sources instead of inventing details.
- Do not imply guaranteed dividends, execution, liquidity, profits or protection from losses.
- The current progress indicator is session-only. Persistent user progress requires authentication, a learning-record data model and a privacy review before implementation.

### Advanced pathway planned

Future modules may cover time-series analysis, market microstructure, fixed-income securities, quantitative portfolio optimisation, scenario and stress testing, model validation, and research-note construction. These should be released only with transparent methods, permissioned data and appropriate technical review.
