# Investor Academy learning experience review

## Research-informed design decisions

This review informs the Investor Academy improvements in this repository. It uses public guidance from established learning products and accessibility standards; it does not claim access to proprietary engagement or performance analytics from those platforms.

### Benchmarks

- **Duolingo**: its published explanation of the learning-path redesign describes sequencing lessons and revisiting concepts using spaced repetition. We adopt a clear pathway, a visible next step and a foundation for future review sessions; we do not copy its streak-driven gamification.
  - https://blog.duolingo.com/new-duolingo-home-screen-design/
- **Moodle**: its current mobile-course guidance recommends responsive HTML, topic/weekly structure, collapsed supplementary blocks and avoiding document-heavy or text-heavy pages. We use focused course sections, progressive disclosure and a single-column mobile lesson layout.
  - https://docs.moodle.org/501/en/Creating_mobile-friendly_courses
- **W3C WCAG 2.2**: Reflow (1.4.10) requires content to work at a 320 CSS-pixel viewport without loss of information or functionality or two-dimensional scrolling, except where two-dimensional presentation is essential. Target Size Minimum (2.5.8) sets a 24 by 24 CSS-pixel minimum subject to exceptions. The Academy aims for larger touch controls where practical.
  - https://www.w3.org/TR/WCAG22/#reflow
  - https://www.w3.org/TR/WCAG22/#target-size-minimum
- **Khan Academy-style mastery learning**: use explanations, practice and feedback to support mastery rather than treating a correct/incorrect score as the entire learning experience. The current implementation has immediate explanatory feedback; richer practice and course assessments remain planned.

### Product decisions

1. Keep the four pathways and their existing curriculum: Beginner, Foundation, Intermediate and Advanced.
2. Give learners a clear starting point and a Continue Learning action.
3. Make the investor glossary searchable so it remains useful as terminology grows.
4. Keep the current lesson sequence accessible without presenting all lesson content expanded at once.
5. Design phone layouts around a single reading column, larger answer controls, clear progress and collapsible supplementary material.
6. Keep all worked examples fictional and clearly labelled. Do not invent current MSE prices, procedures or issuer data.
7. Progress is currently session-only. Do not represent it as account-saved until authentication and persistent storage are implemented.
8. Avoid streak pressure, speculative trading simulations and decorative interactions that do not improve understanding.

## Current implementation scope

- Responsive Academy pathway and lesson typography refinements.
- Larger quiz and lesson action touch areas.
- Improved glossary layout and dark theme.
- Academy learning-journey entry point with a Continue Learning action.
- Searchable glossary.

## Remaining work

- Test at 320, 360, 375, 390, 414, 768 and desktop viewport widths, in portrait and landscape.
- Review the actual rendered Vercel preview on mobile and fix any overflow or focus issues.
- Add measurable lesson objectives, structured content sections, visual explanations and guided numerical/scenario exercises across the curriculum.
- Move from the current expandable list to a dedicated lesson-reading view with a compact course outline and previous/next navigation.
- Add low-pressure course assessments and spaced review.
- Implement persistent progress only after a separate authenticated data store and row-level access controls are approved and configured.
- Run lint, production build and automated interaction checks before merging.

## Important limitations

This is a product-design and implementation review, not a controlled usability study. No learner telemetry or comparative conversion/retention metrics from Duolingo, Coursera, Moodle or Khan Academy were available. Claims about their internal performance are therefore intentionally avoided.
