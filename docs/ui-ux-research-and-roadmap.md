# MSE Data Intelligence — UI/UX research and improvement plan

## Product design direction

MSE Data Intelligence should feel like a dependable financial research terminal with an approachable learning centre. Preserve the forest-green institutional identity and the existing light/dark themes. Avoid copying any one reference brand or using motion that competes with financial information.

## How the supplied resources apply

| Resource | Best use in this product | Design decision |
|---|---|---|
| Jiro.build | Prompt patterns and reusable section ideas | Use as a prompt/reference library when designing specific sections; do not paste generic landing-page templates into the analytics workspace. |
| Recent.design | Current visual direction across web, interface, typography and motion | Use for periodic visual audits and to avoid dated visual conventions. |
| Land-book / Landdding | Landing-page composition and hero hierarchy | Apply selectively to the public-facing introduction/overview, not dense analytical screens. |
| Font In Logo | Understand how brands use type to build recognition | Keep the existing Manrope + DM Sans pairing; establish consistent type roles rather than imitate a logo font. |
| 60fps.design | Real interaction and animation references | Use subtle state transitions for navigation, charts, filters and learning progress; respect reduced-motion preferences. |
| Devault.design | Searchable shipped screens, full flows, pattern analysis and MCP research | Use as a benchmark for dashboard, table, empty-state, onboarding and responsive flows. Its MCP access is a separate paid connection and is not currently connected to this project. |
| Mobbin | Shipped mobile/web product patterns and flows | Benchmark responsive navigation, data tables, settings, search and lesson flows. |
| Pageflows | End-to-end recorded journeys | Review first-visit, find-a-company, inspect-a-metric and continue-learning journeys. |
| Navbar.gallery | Navigation patterns | Keep primary product areas obvious; make mobile navigation compact and predictable. |
| footer.design | Footer patterns | Improve source, methodology, legal and product navigation grouping when the footer is next revised. |
| Siteinspire / Minimal Gallery | Layout restraint and typography | Use whitespace and hierarchy to make research screens calmer and easier to scan. |
| Really Good Emails | Transactional and lifecycle email patterns | Later use for account, report-ready and data-update notification emails if/when those features exist. |

## Current audit observations

- The product has useful functional areas: Overview, Equities, Company research, Risk analytics, Forecast lab, Investor Academy and Methodology.
- The current visual foundation includes Manrope and DM Sans, responsive layouts, keyboard focus styles, dark mode and a reduced-motion rule.
- The stylesheet has accumulated multiple successive palette overrides. The latest UI refinement adds a final set of shared surface, text, border, accent and focus tokens, plus consistent spacing, radii, typography and control feedback.
- The Investor Academy already has structured pathways, progress, lesson diagrams, Malawi-context examples and knowledge checks. Further improvements should focus on saved progress, lesson search/filtering and stronger visual teaching aids.
- Company research and Forecast lab are currently honest empty/coming-soon states because no verified, permissioned issuer dataset or live market feed is connected. Do not disguise these limitations with fake populated screens.

## Implemented in this iteration

- Added a final product-wide visual refinement layer for spacing, typography, panel and metric surfaces, navigation, focus states and interactive feedback.
- Improved mobile content/header spacing and Academy pathway layout.
- Added a consistent focus ring and a reduced-motion fallback for users who request less motion.
- Preserved the existing brand direction, functionality, data caveats and dark theme.

## Next priorities

1. **Dashboard hierarchy:** make the overview answer “what am I looking at, what is synthetic, and what should I do next?” before showing charts.
2. **Equities discovery:** improve search/filter/sort feedback, table density, selected-company context and mobile table alternatives.
3. **Company research:** build a source-first issuer profile template with report periods, document links, audit status and corporate-action timeline, but keep it empty until approved data is available.
4. **Investor Academy:** persist progress only after a deliberate storage/auth decision; add lesson search, review mistakes and stronger concept diagrams.
5. **Onboarding and empty states:** add a concise first-visit orientation and task-based empty states that explain what is available, what is pending and why.
6. **Notification/email design:** only when notification workflows exist, use lifecycle-email patterns for concise, trustworthy updates.
7. **Validation:** test 320px reflow, keyboard navigation, contrast, touch targets, dark mode and reduced motion; review with real users before claiming usability gains.

## Research limitations

The public resource sites are inspiration and pattern libraries, not evidence that a design change will improve this product's outcomes. Devault's MCP is paid and not connected here. No private Mobbin/Pageflows screens were accessed. The changes above are based on public descriptions and the repository's current implementation. No proprietary screens or assets have been copied.
