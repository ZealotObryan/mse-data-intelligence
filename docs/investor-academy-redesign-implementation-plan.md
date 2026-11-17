# MSE Investor Academy Redesign — Implementation Plan

**Status:** In progress  
**Design direction:** Combination of premium financial education, guided/gamified learning, and market-terminal interaction  
**Illustration direction:** Combination of custom vector diagrams, editorial infographics, and purposeful animation  
**Workflow:** Hybrid Figma-first design with implementation in the existing Next.js application

## Product objective

Turn the existing Investor Academy into a practical, visual financial-learning experience for Malawi-based learners. The Academy should help learners understand concepts, practise decisions safely, assess their understanding, and see their learning progress.

The redesign retains the four existing pathways and 26 lessons. It is an experience upgrade, not a rewrite of the learning curriculum.

## Current foundation

- Four pathways: Beginner (9 lessons), Foundation (5), Intermediate (6), Advanced (6).
- Existing lesson content, knowledge checks, takeaways, visual explanations and Malawi-context examples.
- Existing Next.js / React / TypeScript application and forest-green visual identity.
- Existing progress is session-only; durable learner accounts and server persistence are not assumed.
- No live MSE market feed is connected. Synthetic figures must remain explicitly labelled as illustrative.

## Design principles

1. Teach first: every visual, interaction and animation must make a financial concept easier to understand.
2. Malawi context: use familiar local business and household examples without implying a real issuer or real market transaction.
3. Progressive disclosure: beginner learners see simple explanations first; advanced learners can explore assumptions and detail.
4. Evidence and caveats: show units, dates, assumptions, calculation methods and limitations beside financial outputs.
5. Accessible by default: keyboard operation, readable contrast, visible focus, reduced-motion support and responsive layouts.
6. Honest data: label every synthetic example, simulation and sample company; never imply live prices or investment recommendations.
7. Reusable system: build diagrams, cards, simulator controls and assessment patterns as reusable React components.

## Phase 1 — Design foundation

**Deliverables**
- Figma design file with Academy dashboard and lesson/simulator direction.
- Colour, typography, spacing, radius, elevation and state tokens aligned to the existing forest-green/sage identity.
- Reusable patterns for navigation, pathway cards, progress, callouts, diagrams, controls, quiz feedback and simulator results.
- Desktop and mobile layout rules.

**Acceptance**
- Dashboard, pathway overview and lesson reader share a consistent visual system.
- Light and dark themes remain legible.
- Component names and token names map clearly to implementation.

## Phase 2 — Academy information architecture and dashboard

**Deliverables**
- Redesigned Academy landing page with a clear learning entry point.
- Four pathway cards with lesson counts, level descriptions and progress states.
- Continue-learning and browse-pathways actions.
- A practice-tools entry point.
- Clear disclosure that examples are educational and may use synthetic data.

**Acceptance**
- Learners can identify where to start and how to continue.
- Existing lesson destinations and content remain accessible.
- Mobile layout does not require horizontal scrolling.

## Phase 3 — Lesson reader and illustration system

**Deliverables**
- Consistent lesson header, estimated time, section navigation, concept explanation, worked example, visual explanation, Malawi-context example, key takeaway and knowledge check.
- A reusable illustration vocabulary: process flows, ownership diagrams, timelines, comparison panels, financial statement relationships, ratio breakdowns, risk-return charts and portfolio allocation views.
- A mix of editable SVG/React diagrams, editorial infographics and selective motion.

**Acceptance**
- Each of the 26 lessons has a visual that is specific to its learning objective.
- Illustrations have text equivalents or labels and remain understandable on small screens.
- Motion is optional and respects reduced-motion preferences.

## Phase 4 — Interactive practice tools

Build in this order:

1. **Investment return simulator:** starting investment, price movement, ending value, gain/loss and percentage return. State whether fees, taxes and dividends are excluded.
2. **Dividend calculator:** shares held × dividend per share, with an explicit gross/net and tax assumption note.
3. **Order-book simulator:** buyers, sellers, bid/ask spread, matching and unfilled orders.
4. **Primary vs secondary market flow:** show who receives funds in each transaction.
5. **Portfolio builder:** allocations, concentration and diversification, using hypothetical holdings.
6. **Risk/return explorer:** compare volatility, drawdown and return without presenting forecasts as guarantees.
7. **Financial statement explorer:** link profit, assets/liabilities and cash flow.
8. **Ratio playground:** editable inputs, formula, output and interpretation.
9. **Valuation simulator:** transparent forecast and discount-rate assumptions; sensitivity rather than a single certain answer.
10. **Model evaluation lab:** train/test separation, baseline comparison, errors and model limitations.

**Acceptance**
- Every tool explains inputs, formula, output and limitations.
- Controls update results immediately and are keyboard accessible.
- Sample data is labelled illustrative.
- Calculations have unit tests and edge-case coverage (zero, negative, missing and unusually large inputs where relevant).

## Phase 5 — Assessments and feedback

**Deliverables**
- Scenario-based questions in addition to recall questions.
- Immediate feedback explaining why an answer is right or wrong.
- Worked solutions for calculation questions.
- Short topic challenges and end-of-pathway checks.
- Revision prompts based on incorrect answers.

**Acceptance**
- Feedback teaches the underlying concept rather than only showing a score.
- Questions remain aligned to the lesson content and stated learning objectives.
- Scoring and answer states are accessible without relying on colour alone.

## Phase 6 — Progress and motivation

**Deliverables**
- Pathway and lesson completion states.
- Milestones and achievement markers.
- Revision queue and recommended next lesson.
- Optional streaks only if they can be implemented without pressuring learners.
- Persistence architecture proposal, separate from UI work.

**Acceptance**
- Progress states are truthful and recoverable.
- Do not imply cross-device persistence until authentication/storage is implemented and tested.
- No learner data is collected unnecessarily.

## Phase 7 — Quality, release and measurement

**Deliverables**
- Responsive, accessibility, interaction and performance review.
- Automated unit tests for simulator calculations.
- Browser-level smoke tests for lesson navigation and interactions.
- Content and financial-accuracy review.
- Release notes and a post-release improvement backlog.

**Acceptance**
- CI lint, build and tests pass.
- No critical mobile, keyboard or contrast issues remain.
- Synthetic-data disclosures are visible wherever simulated figures appear.
- Production deployment is confirmed READY before describing the redesign as live.

## Suggested delivery sequence

| Increment | Scope | Review gate |
|---|---|---|
| A | Figma foundation + dashboard | Approve visual direction |
| B | Lesson reader + reusable illustration components | Review one lesson at each level |
| C | First three simulators | Validate formulas and teaching value |
| D | Remaining practice tools | Validate assumptions and responsive behaviour |
| E | Assessments + progress | Validate learning flow and persistence boundaries |
| F | Full QA + production release | CI, accessibility and deployment sign-off |

## Initial design artefact

Figma: [MSE Investor Academy — Redesign System](https://www.figma.com/design/aQdwTglVgbJyYO7AN6yHWp)

The first desktop concept establishes the navigation, welcome hero, four pathway cards, learning summary and a preview of the investment-return practice area. It is a starting point for review and refinement, not a final approved visual specification.
