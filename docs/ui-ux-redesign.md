# MSE Analytics — UI/UX redesign direction

## Design reference library

These references guide the redesign; they are inspiration and implementation resources, not a reason to copy another product's identity.

- [21st.dev](https://21st.dev/) — polished React components, dashboard patterns, themes, templates, navigation, cards and AI-oriented interface patterns. Use selectively for production-ready building blocks.
- [React Bits](https://reactbits.dev/) — motion, animated components, backgrounds and micro-interactions. Use restrained motion to explain state and improve feedback, not as decoration.
- [Magic UI](https://magicui.design/) — React, TypeScript, Tailwind and Motion components/effects. Use for refined visual treatments and subtle transitions where they improve hierarchy.
- [Uiverse](https://uiverse.io/) — community UI elements in CSS, Tailwind and React. Use as a source for small controls and interaction ideas; audit accessibility and consistency before adoption.
- [Mobbin](https://mobbin.com/) — shipped web and mobile product screens. Use for UX research into navigation, information architecture, data-dense tables, onboarding, filters, empty states and responsive behaviour.

## Product design goals

MSE Analytics should feel like a credible financial research terminal: calm, precise, trustworthy, data-led and fast to scan. It should not look like a generic crypto trading template or a flashy AI landing page.

### Visual direction
- Establish a consistent design system for colour, typography, spacing, radii, borders, elevation and chart styles.
- Keep a restrained financial palette with clear positive, negative, neutral and warning states.
- Use strong typographic hierarchy and whitespace to make dense market information readable.
- Keep motion subtle, purposeful, and respectful of reduced-motion preferences.
- Make charts, tables, filters and data provenance the visual focus.

### UX priorities
1. Responsive application shell with clear navigation and a compact mobile navigation pattern.
2. Market overview with transparent data status, last-updated context and clear distinction between synthetic/demo and verified data.
3. Equities explorer with search, sorting, filters, column clarity and accessible table behaviour.
4. Risk analytics with clear metric definitions, assumptions and chart explanations.
5. Forecast lab with model status, validation approach, confidence/uncertainty communication and no unsupported forecast claims.
6. Methodology and source provenance pages with visible source, licence, retrieval and data-quality context.
7. Consistent loading, empty, error, stale-data and unavailable states.
8. Keyboard accessibility, visible focus, semantic controls, sufficient contrast and reduced-motion support.

## Non-negotiable trust rules

- Never present synthetic values, invented issuers or sample series as actual Malawi Stock Exchange data.
- Keep the demo-data notice prominent until verified and permissioned data is connected.
- Show source, observation date, retrieval time, units and methodology where relevant.
- Do not imply real-time market data unless the underlying feed supports it.
- Obtain the appropriate MSE/data-provider permissions before displaying or redistributing real market data.

## Implementation approach

1. Audit the current screens and identify the highest-impact usability issues.
2. Define design tokens and reusable components before restyling individual pages.
3. Improve the application shell, overview, tables, charts and responsive layouts.
4. Add consistent interaction states and accessibility checks.
5. Validate on desktop, tablet and mobile; run lint/build and review screenshots before deployment.

## Reference URLs

- https://21st.dev/
- https://reactbits.dev/
- https://magicui.design/
- https://uiverse.io/
- https://mobbin.com/
