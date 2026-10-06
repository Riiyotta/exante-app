# clone/ — Exante: AI Teammate for Collections

A runnable **Vite + React + react-router + Tailwind v3** project written from the real rendered DOM of https://www.exante.app/: one component per section with that section's own markup, the site's own stylesheets, its real images, fonts and video under `public/`, routes declared in `src/routes.js`.

```
npm install
npm run dev      # http://localhost:5173
npm run build
```

## What is in it

- `src/sections/`: **83** component(s) (104 section instance(s) over 18 route(s); identical markup shared across routes is one component).
- `src/pages/` + `src/routes.js` + `src/App.jsx`: one page per captured route, sections in page order, react-router links between captured pages.
- `src/styles/`: the site's own CSS, copied as it was with every `url()` rewritten to a file under `public/`; `tokens.css` + `tailwind.config.cjs` carry the measured design tokens (Tailwind utilities load first, preflight is off, so the site's CSS wins).
- `public/`: **232** real file(s), 29.0 MB (images, fonts, video, SVG). Nothing points outside the project.
- `clone-manifest.json`: route → page → component map, every still, every dropped file.

## Animation

- **Canvas / Rive areas: 0 still(s) captured** (0 canvas(es) drew nothing and are an empty, correctly sized box). The 0 `.riv` file(s) are **not** included: a remix cannot recolour or redraw a Rive file and would ship the original mascot on every generated site. Replace each still with an image slot, CSS or GSAP.
- **Scroll-driven motion is not reproduced.** The clone keeps one reveal-on-scroll observer only. Rebuild them with CSS or GSAP in the remix.
- **Scroll-reveal: 129 element(s)** that started hidden or offset and animated in are marked `data-reveal`; one IntersectionObserver (`src/lib/usePageChrome.js`) fades them up (off under reduced motion).
- **78 element(s) forced visible.** These started hidden/offset on the original and were still hidden/offset when this clone was captured — the scroll-triggered animation that reveals them on the original did not fire the same way during capture. Rather than ship them permanently invisible, their hiding style was stripped so they render plainly (no animation, but visible). Rebuild the real scroll-in motion in the remix.
- **3 stat counter(s) replayed.** A bare number whose digits read differently right after load than once settled (a count-up) is marked `data-count-from`/`data-count-to`; `src/lib/usePageChrome.js` counts it up for real the first time it scrolls into view, matching the original's digit grouping and decimal places (off under reduced motion).
- **14 dropdown / mega-menu panel(s) captured.** A nav item whose panel is only built on hover/click (no entries of its own in the static DOM) was hovered for real; the panel that appeared is saved as a permanent sibling of its trigger and shown with real CSS `:hover`/`:focus-within` (see `src/styles/clone.css`) — a working dropdown, not just a label. Its own open/close script behaviour (animation, click-outside-to-close) is not reproduced.
- **Not reproduced**: GSAP timelines / ScrollTrigger pins and scrubs (pin wrappers are removed, content flows normally), Lenis smooth scroll, accordions, tabs, carousels and other script behaviour (only the state the page was in after load is captured), forms (submit is prevented), third-party frames (replaced by an empty box of the same size), shadow-DOM content.
- **No analytics or trackers**: none are in `src/` or `public/`.
- **No external links**: links to other sites (and to pages that were not captured) keep their element and styling but have no `href`; links between cloned pages go through the router. `--keep-external-links` keeps them.

## Checks run by the builder

| Check | Result |
|---|---|
| Every `src` / `url()` the code points at exists in `public/` | PASS (126 image reference(s), 126 resolved) |
| No tracker host in code or `public/` | PASS |
| No external hyperlink in `src/` | PASS (41 link(s) to other sites or uncaptured pages lost their target) |
| No placeholder boxes from the level-2 scaffold | PASS |
| Vite build + every route loads offline | PASS: vite build ok; 18 route(s) loaded: 0 console/network error(s), 0 outside host(s), 0 empty page(s) |
| Parity vs the original page, per section (gate 80%) | PASS: average 94.9% over 6 route(s) |

### Parity detail

Each section of the built clone is compared with the same section of the **original page**: the crawl's own full-page screenshot at 1440 px (`extras/images/`, taken from the live site with its scripts running) cut at that section's rectangle, or a fresh screenshot of the offline mirror when that file is missing. Both sides are compared on a half-scale grid; a pixel matches when no channel differs by more than 40/255, and a section whose height differs by more than 10 % is scaled down by the height ratio (except GSAP-pinned sections, whose extra scroll length is a script's doing). The route score weights sections by height. Sections below the gate get a side-by-side picture (original | clone) in `qa/parity/`. Whole-page height is not scored: GSAP pin spacers add blank scroll length the clone does not reproduce. Live animation, video and carousels in motion differ by design.

**`/`**: 99.8% over 12 of 12 section(s) (reference: original crawl screenshot); page height 8584 → 8584 px.

| # | Component | Height (original → clone) | Match | Score |
|---|---|---|---|---|
| 0 | `FramerHuxi9oContainer` | 72 → 72 px | 100.0% | 100.0% |
| 1 | `HeroSection` | 900 → 900 px | 100.0% | 100.0% |
| 2 | `ROISection` | 777 → 777 px | 99.8% | 99.8% |
| 3 | `ProblemSection` | 779 → 779 px | 100.0% | 100.0% |
| 4 | `KeyFeaturesSection` | 1227 → 1227 px | 100.0% | 100.0% |
| 5 | `OtherFeaturesSection` | 1139 → 1139 px | 99.0% | 99.0% |
| 6 | `ClientsSection` | 472 → 472 px | 99.7% | 99.7% |
| 7 | `CTASection2` | 565 → 565 px | 100.0% | 100.0% |
| 8 | `IntegrationsSection` | 578 → 578 px | 100.0% | 100.0% |
| 9 | `FAQSection` | 963 → 963 px | 100.0% | 100.0% |
| 10 | `AnotherCTA` | 367 → 367 px | 99.3% | 99.3% |
| 11 | `Framer39uowvContainer` | 818 → 818 px | 100.0% | 100.0% |

**`/customers`**: 99.9% over 5 of 5 section(s) (reference: original crawl screenshot); page height 2531 → 2531 px.

| # | Component | Height (original → clone) | Match | Score |
|---|---|---|---|---|
| 0 | `Framer1h4pb9vContainer` | 72 → 72 px | 100.0% | 100.0% |
| 1 | `HeroSection4` | 641 → 641 px | 100.0% | 100.0% |
| 2 | `TestimonialsSection` | 757 → 757 px | 99.8% | 99.8% |
| 3 | `AnotherCTA3` | 315 → 315 px | 99.8% | 99.8% |
| 4 | `FramerGzkazmContainer` | 818 → 818 px | 100.0% | 100.0% |

**`/contact/sales`**: 100.0% over 4 of 4 section(s) (reference: original crawl screenshot); page height 1983 → 1983 px.

| # | Component | Height (original → clone) | Match | Score |
|---|---|---|---|---|
| 0 | `DesktopFilled` | 72 → 72 px | 100.0% | 100.0% |
| 1 | `Main` | 1165 → 1165 px | 100.0% | 100.0% |
| 2 | `Desktop` | 818 → 818 px | 100.0% | 100.0% |
| 3 | `White` | 1983 → 1983 px | 100.0% | 100.0% |

**`/blog/what-we-hear-when-we-talk-to-finance-teams`**: 87.3% over 6 of 6 section(s) (reference: original crawl screenshot); page height 7720 → 7720 px. Below the gate: 2:FeaturedImageWrapper 27%, 4:OtherArticlesSection 72%.

| # | Component | Height (original → clone) | Match | Score |
|---|---|---|---|---|
| 0 | `Framer1h4pb9vContainer4` | 72 → 72 px | 85.7% | 85.7% |
| 1 | `Container` | 388 → 388 px | 91.2% | 91.2% |
| 2 | `FeaturedImageWrapper` | 760 → 760 px | 27.4% | 27.4% ⚠ |
| 3 | `ContentSection4` | 4189 → 4189 px | 99.7% | 99.7% |
| 4 | `OtherArticlesSection` | 1205 → 1205 px | 72.4% | 72.4% ⚠ |
| 5 | `FramerGzkazmContainer5` | 818 → 818 px | 100.0% | 100.0% |

**`/blog/from-aging-reports-to-cash-control`**: 99.8% over 5 of 6 section(s) (reference: original crawl screenshot); page height 5927 → 5927 px.

| # | Component | Height (original → clone) | Match | Score |
|---|---|---|---|---|
| 0 | `Framer1h4pb9vContainer5` | 72 → 72 px | 100.0% | 100.0% |
| 1 | `Container4` | 417 → 417 px | 100.0% | 100.0% |
| 2 | `FeaturedImageWrapper4` | 760 → 760 px | 100.0% | 100.0% |
| 3 | `ContentSection7` | 2367 → 2367 px | 99.7% | 99.7% |
| 4 | `OtherArticlesSection4` | 1205 → 1205 px | 99.8% | 99.8% |
| 5 | `FramerGzkazmContainer5` | 818 → 818 px | — | skipped |

**`/blog/why-collections-software-keeps-failing-finance-teams`**: 82.8% over 6 of 6 section(s) (reference: original crawl screenshot); page height 6575 → 6575 px. Below the gate: 2:FeaturedImageWrapper7 6%, 4:OtherArticlesSection5 74%.

| # | Component | Height (original → clone) | Match | Score |
|---|---|---|---|---|
| 0 | `Framer1h4pb9vContainer4` | 72 → 72 px | 85.7% | 85.7% |
| 1 | `Container7` | 388 → 388 px | 90.1% | 90.1% |
| 2 | `FeaturedImageWrapper7` | 760 → 760 px | 6.4% | 6.4% ⚠ |
| 3 | `ContentSection10` | 3044 → 3044 px | 99.8% | 99.8% |
| 4 | `OtherArticlesSection5` | 1205 → 1205 px | 73.9% | 73.9% ⚠ |
| 5 | `FramerGzkazmContainer5` | 818 → 818 px | 100.0% | 100.0% |

