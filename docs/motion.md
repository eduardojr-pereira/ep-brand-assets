# Motion Library

Load `styles/foundations.css`, `styles/motion-tokens.css`, and `styles/motion.css` in that order, then `scripts/scroll-trigger.js` synchronously in the document head (no async/defer). The script opts in before the body is parsed. Without JavaScript or IntersectionObserver, content remains visible.

Apply `data-motion="fade-in|reveal-up|reveal-left|reveal-right|scale-in"` to a dedicated wrapper and `data-scroll-trigger="load|once|repeat"`. Left/right name the origin. `load` runs at DOMContentLoaded; `once` on viewport entry; `repeat` rearms after leaving the viewport. Do not nest motion wrappers unnecessarily or apply motion to an element whose transform is controlled by an interactive component. Use custom properties `--ep-motion-distance`, `--ep-motion-duration`, `--ep-motion-delay`, `--ep-motion-ease`, `--ep-motion-opacity`, `--ep-motion-scale` for contextual parameters. Stagger is composed through the delay property, not a second animation system.

Hero reference: the three lines enter left/right/left, from 100vw, opacity .15, duration 1650ms, delays 50/190/330ms; details fade for 1350ms after 700ms. These are contextual parameters in the future Hero component; do not apply them globally. Explicit replay is `EPMotion.replay(hero)` after the language controller changes the content; locale fade sequencing belongs to the language/Hero integration. No implicit replay on scroll for the Hero.

Shared timings: 450ms diagonal link motion, 550ms directional underline, 550ms radial fill, 420ms navigation weight/color transition, 250ms feedback, 20s rotating label and 3370ms arrow cycle. Link, button, orbit, marquee and cursor behavior will be implemented by their canonical components, not duplicated here. Continuous motion components must independently honor reduced motion and pause rules.

Default reveal duration 650ms, distance 24px, scale .96 and viewport threshold 0 are initial implementation values, subject to integrated visual verification. Reduced motion immediately reveals content; keyboard focus reveals its containing motion wrappers. `ep-motion-fade-out` is available for explicit component transitions, never used to conceal ordinary page content automatically.

Run `python3 tests/test_motion.py` in an environment with Python Playwright and an installed Chromium-compatible browser. The test uses an isolated document, not a visual reference; browser executable selection can be overridden via `EP_TEST_BROWSER`. Final appearance, timing, layout and remote delivery must still be checked in the integrated page.
