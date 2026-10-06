# CLONE_SPEC — Exante: AI Teammate for Collections

Source: https://www.exante.app/ · stack guess: React+Framer+Lenis · 18 route(s), 9 template(s), 31 section type(s).
Measured from the rendered pages at 1440, 1280 and 390px wide. Colours are hex. Values are measurements; role names are inferred from usage.

## Colours

| Token | Hex | Uses | Mostly used as |
|---|---|---|---|
| `color.neutral.01` | `#000000` | 4962 | text, fill |
| `color.neutral.02` | `#1e211e` | 1251 | text, bg, fill |
| `color.neutral.03` | `#ffffff` | 1099 | text, bg, fill |
| `color.blue.01` | `#0000ee` | 1045 | text |
| `color.neutral.04` | `#222222` | 402 | text |
| `color.green.01` | `#90fc95` | 63 | bg |
| `color.neutral.05` | `#fbfaf9` | 61 | bg |
| `color.neutral.06` | `#1e211e99` | 58 | text, bg |
| `color.orange.01` | `#f2ece8` | 40 | bg |
| `color.neutral.07` | `#ffffff26` | 33 | bg |
| `color.neutral.08` | `#767676` | 22 | border |
| `color.neutral.09` | `#8a8a8a` | 10 | text |
| `color.neutral.10` | `#fafafa` | 10 | bg |
| `color.neutral.11` | `#ffffffcc` | 6 | text |
| `color.neutral.12` | `#1e211ecc` | 6 | text |
| `color.neutral.13` | `#f5f3f24d` | 4 | bg |
| `color.neutral.14` | `#000000b3` | 3 | text |
| `color.neutral.15` | `#ffffff03` | 2 | bg |
| `color.neutral.16` | `#f9fafb` | 1 | bg |
| `color.green.02` | `#213622` | 1 | bg |
| `color.neutral.17` | `#00000066` | 1 | text |
| `color.neutral.18` | `#1e211e4d` | 1 | border |

Semantic roles:

- `surface.default` → `color.neutral.03` (#ffffff): most-used opaque background (241 uses)
- `surface.alt` → `color.neutral.02` (#1e211e): second most-used neutral background (168 uses)
- `surface.inverse` → `color.neutral.02` (#1e211e): most-used background neutral, with opposite lightness to surface.default (168 uses)
- `surface.accent` → `color.green.01` (#90fc95): most-used saturated background (63 uses)
- `text.primary` → `color.neutral.01` (#000000): most-used text colour (4480 uses)
- `text.secondary` → `color.neutral.02` (#1e211e): most-used neutral text colour with lower contrast than text.primary on surface.default (1067 uses)
- `text.inverse` → `color.neutral.03` (#ffffff): most-used text colour neutral, with opposite lightness to text.primary (840 uses)
- `text.accent` → `color.blue.01` (#0000ee): most-used saturated text/fill colour (1045 uses)
- `border.default` → `color.neutral.08` (#767676): most-used border colour (22 uses)
- `accent.primary` → `color.blue.01` (#0000ee): most-used saturated colour overall (1045 uses)

## Type roles

| Role | Family | Size | Line height | Weight | Inferred from |
|---|---|---|---|---|---|
| `typography.display` | Inter | 16px | 19.2px | 400 | most-used style on display text (9 uses) |
| `typography.heading` | Geist Mono | 32px | 38.4px | 400 | most-used style on heading text (82 uses) |
| `typography.body` | Geist Variable | 19px | 26.6px | 400 | most-used style on body text (443 uses) |
| `typography.label` | Geist Variable | 19px | 26.6px | 400 | most-used style on label text (274 uses) |

## Radii

- `radius.4`: 4px (222 uses)
- `radius.2`: 2px (207 uses)
- `radius.8`: 8px (47 uses)
- `radius.64`: 64px (32 uses)
- `radius.16`: 16px (20 uses)
- `radius.50`: 50px (6 uses)
- `radius.10`: 10px (5 uses)
- `radius.1`: 1px (1 uses)

## Shadows

- `elevation.01`: `#00000000 0px 0px 0px 1px inset`

## Motion

- `duration.1300ms`: 1.3s (4 uses)
- `duration.250ms`: 0.25s (2 uses)
- `duration.400ms`: 0.4s (2 uses)
- `duration.1500ms`: 1.5s (2 uses)
- `easing.01`: cubic-bezier(0.44, 0, 0.13, 0.96) (6 uses)
- `easing.02`: cubic-bezier(0.215, 0.61, 0.355, 1) (2 uses)
- `easing.03`: linear (2 uses)

## Breakpoints (from the site's CSS)

- `breakpoint.759`: 759px
- `breakpoint.759.98`: 759.98px
- `breakpoint.760`: 760px
- `breakpoint.1099.98`: 1099.98px
- `breakpoint.1100`: 1100px
- `breakpoint.1439`: 1439px
- `breakpoint.1439.98`: 1439.98px

## Layout

- `layout.contentWidth`: 1360px (most common width of a section's first child at a 1440px viewport (measured, not a max-width rule))
- `layout.gutter`: 40px (most common left offset of section content at 1440px)
- `layout.sectionPaddingTop`: {space.96} (most common padding-top of a section)
- `layout.sectionPaddingBottom`: {space.96} (most common padding-bottom of a section)
- `layout.gridGap`: {radius.64} (most common column-gap of a grid/flex container inside a section)
- `layout.sectionPaddingTop.cta`: 26px (most common padding-top of a CTA section (differs from the sitewide mode))
- `layout.sectionPaddingBottom.cta`: 26px (most common padding-bottom of a CTA section (differs from the sitewide mode))
- `layout.gridGap.cta`: {radius.10} (most common column-gap of a CTA section (differs from the sitewide mode))
- `layout.sectionPaddingTop.features`: 66px (most common padding-top of a FEATURES section (differs from the sitewide mode))
- `layout.sectionPaddingBottom.features`: 22px (most common padding-bottom of a FEATURES section (differs from the sitewide mode))
- `layout.gridGap.features`: {space.24} (most common column-gap of a FEATURES section (differs from the sitewide mode))
- `layout.sectionPaddingTop.hero`: 200px (most common padding-top of a HERO section (differs from the sitewide mode))
- `layout.gridGap.hero`: {radius.10} (most common column-gap of a HERO section (differs from the sitewide mode))
- `layout.sectionPaddingTop.proof`: 85px (most common padding-top of a PROOF section (differs from the sitewide mode))
- `layout.sectionPaddingBottom.proof`: 46px (most common padding-bottom of a PROOF section (differs from the sitewide mode))
- `layout.gridGap.proof`: {radius.50} (most common column-gap of a PROOF section (differs from the sitewide mode))
- `layout.sectionPaddingTop.shell`: {space.80} (most common padding-top of a SHELL section (differs from the sitewide mode))
- `layout.sectionPaddingBottom.shell`: {space.80} (most common padding-bottom of a SHELL section (differs from the sitewide mode))
- `layout.sectionPaddingTop.support`: 212px (most common padding-top of a SUPPORT section (differs from the sitewide mode))
- `layout.gridGap.support`: 53px (most common column-gap of a SUPPORT section (differs from the sitewide mode))

## Sections

Height = median across the type's instances. Phone/laptop columns come from the same section re-measured at that width.

### `content.framer-huxi9o-container` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<div>`, named "framer-huxi9o-container"
- height: 72px @1440 · 72px @1280 · 64px @390
- columns: 2 @1440 · 2 @1280 · 1 @390
- box: padding 0/0px · first child 1440px wide · gap 64px
- colour: background #ffffff · text #000000 · align start
- body: Geist Variable 16px/22.4px weight 400 #1e211e
- motion: appear-on-enter

### `hero.hero-section` (HERO)

- appears on 8 route(s), 8 instance(s); tag `<section>`, named "Hero Section"
- height: 822px @1440 · 800px @1280 · 844px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 200/96px · first child 1360px wide · gap 24px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Light 80px/88px weight 300 tracking -4px #1e211e
- body: Geist Variable 21px/29.4px weight 400 #ffffff
- layout: text + visual, 648 / 648px, text on the left
- motion: appear-on-enter, scroll-linked
- example headline: "AI teammate that handles collections"

### `content.roi-section` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "ROI Section"
- height: 777px @1440 · 686px @1280 · 1030px @390
- columns: 2 @1440 · 2 @1280 · 1 @390
- box: padding 106/106px · first child 1392px wide · gap 10px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Mono 12px/14.4px weight 400 #1e211e
- motion: none observed
- example headline: "Go from outstanding invoices to outstanding cash flow in no time."

### `content.problem-section` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Problem Section"
- height: 779px @1440 · 545px @1280 · 897px @390
- columns: 3 @1440 · 3 @1280 · 1 @390
- box: padding 0/90px · first child 1392px wide · gap 10px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Mono 12px/14.4px weight 400 #1e211e
- motion: none observed
- example headline: "Your collections process can't scale, and it's costing you"

### `features.key-features-section` (FEATURES)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Key Features Section"
- height: 1227px @1440 · 1107px @1280 · 2632px @390
- columns: 2 @1440 · 2 @1280 · 1 @390
- box: padding 66/22px · first child 980px wide · gap 29px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Mono 12px/14.4px weight 400 #1e211e
- motion: none observed
- example headline: "No matter what's outstanding, Exante leaves no dollar behind"

### `features.other-features-section` (FEATURES)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Other Features Section"
- height: 1139px @1440 · 987px @1280 · 2186px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 124/124px · first child 1360px wide · gap 36px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Mono 12px/14.4px weight 400 #1e211e
- motion: none observed
- example headline: "Your imagination is the only limit"

### `proof.clients-section` (PROOF)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Clients Section"
- height: 472px @1440 · 439px @1280 · 671px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 85/46px · first child 1360px wide · gap 50px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Variable 21px/29.4px weight 400 #1e211e
- motion: none observed
- example headline: "Trusted by forward-thinking finance teams"

### `cta.cta-section-2` (CTA)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "CTA Section #2"
- height: 565px @1440 · 548px @1280 · 937px @390
- columns: 2 @1440 · 2 @1280 · 2 @390
- box: padding 26/26px · first child 1392px wide · gap 10px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Regular 52px/62.4px weight 400 tracking -2.08px #1e211e
- body: Geist Mono 12px/14.4px weight 400 #1e211e
- motion: appear-on-enter
- example headline: "Go live in days and get paid in a week"

### `features.integrations-section` (FEATURES)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Integrations Section"
- height: 578px @1440 · 579px @1280 · 789px @390
- columns: 6 @1440 · 6 @1280 · 2 @390
- box: padding 110/22px · first child 1360px wide · gap 45px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Variable 21px/29.4px weight 400 #1e211e
- motion: none observed
- example headline: "No rip-and-replace required"

### `support.faq-section` (SUPPORT)

- appears on 2 route(s), 2 instance(s); tag `<section>`, named "FAQ Section"
- height: 963px @1440 · 884px @1280 · 792px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 212/96px · first child 1000px wide · gap 64px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist 19px/26.6px weight 300 #1e211ecc
- motion: none observed
- example headline: "Frequently asked questions"

### `cta.another-cta` (CTA)

- appears on 3 route(s), 3 instance(s); tag `<section>`, named "Another CTA"
- height: 315px @1440 · 331px @1280 · 338px @390
- columns: 2 @1440 · 2 @1280 · 2 @390
- box: padding 74/83px · first child 1392px wide · gap 10px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Variable 19px/26.6px weight 400 #ffffff
- layout: two text columns, 787 / 407px, text on the left
- motion: appear-on-enter
- example headline: "Get started right now with one of our pre-built AI agents!"

### `content.framer-39uowv-container` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<div>`, named "framer-39uowv-container"
- height: 818px @1440 · 796px @1280 · 1260px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1440px wide · gap 160px
- colour: background #ffffff · text #000000 · align start
- headline: Alliance No.2 Regular 24px/28.8px weight 400 tracking -0.24px #ffffff
- body: Geist Variable 17px/23.8px weight 400 #ffffff
- motion: none observed
- example headline: "Getting you from "sent" to "paid", your way."

### `content.framer-guhhla-container` (CONTENT)

- appears on 2 route(s), 2 instance(s); tag `<div>`, named "framer-guhhla-container"
- height: 72px @1440 · 64px @1280 · 64px @390
- columns: 2 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1440px wide · gap 64px
- colour: background #ffffff · text #000000 · align start
- body: Geist Variable 16px/22.4px weight 400 #ffffff
- motion: none observed

### `content.intro-section` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Intro Section"
- height: 374px @1440 · 380px @1280 · 416px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 123/0px · first child 1360px wide · gap 80px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Variable 21px/29.4px weight 400 #1e211e
- motion: none observed
- example headline: "Built for autonomous finance. Run by people who’ve done the work."

### `content.approach-section` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Approach Section"
- height: 940px @1440 · 1180px @1280 · 1720px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 120/120px · first child 1360px wide · gap 16px
- colour: background #ffffff · text #000000 · align start
- layout: text + visual, 823 / 447px, text on the left (layered)
- motion: none observed

### `content.team-members-section` (CONTENT)

- appears on 2 route(s), 3 instance(s); tag `<section>`, named "Team Members Section"
- height: 1424px @1440 · 1771px @1280 · 1501px @390
- columns: 10 @1440 · 5 @1280 · 2 @390
- box: padding 69/69px · first child 1360px wide · gap 43px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Variable 16px/22.4px weight 400 #ffffff
- layout: text + visual, 800 / 532px, text on the left (layered)
- motion: none observed
- example headline: "Built by a team with deep finance, engineering, and enterprise experience"

### `content.framer-1nc9gyu-container` (CONTENT)

- appears on 2 route(s), 2 instance(s); tag `<div>`, named "framer-1nc9gyu-container"
- height: 818px @1440 · 1095px @1280 · 1260px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1440px wide · gap 160px
- colour: background #ffffff · text #000000 · align start
- headline: Alliance No.2 Regular 24px/28.8px weight 400 tracking -0.24px #ffffff
- body: Geist Variable 17px/23.8px weight 400 #ffffff
- motion: none observed
- example headline: "Getting you from "sent" to "paid", your way."

### `content.blog-section` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Blog Section"
- height: 2330px @1440 · 2340px @1280 · 3515px @390
- columns: 3 @1440 · 2 @1280 · 1 @390
- box: padding 96/96px · first child 1360px wide · gap 64px
- colour: background #ffffff · text #000000 · align start
- layout: text + visual, 440 / 440px, text on the left (layered)
- motion: none observed

### `content.framer-1h4pb9v-container` (CONTENT)

- appears on 13 route(s), 13 instance(s); tag `<div>`, named "framer-1h4pb9v-container"
- height: 72px @1440 · 64px @1280 · 64px @390
- columns: 2 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1440px wide · gap 64px
- colour: background #ffffff · text #000000 · align start
- body: Geist Variable 16px/22.4px weight 400 #1e211e
- motion: appear-on-enter

### `proof.testimonials-section` (PROOF)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Testimonials Section"
- height: 757px @1440 · 1029px @1280 · 953px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1200px wide · gap 56px
- colour: background #ffffff · text #000000 · align start
- motion: none observed

### `content.framer-gzkazm-container` (CONTENT)

- appears on 13 route(s), 13 instance(s); tag `<div>`, named "framer-gzkazm-container"
- height: 818px @1440 · 1095px @1280 · 1260px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1440px wide · gap 160px
- colour: background #ffffff · text #000000 · align start
- headline: Alliance No.2 Regular 24px/28.8px weight 400 tracking -0.24px #ffffff
- body: Geist Variable 17px/23.8px weight 400 #ffffff
- motion: none observed
- example headline: "Getting you from "sent" to "paid", your way."

### `features.benefits-section` (FEATURES)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Benefits Section"
- height: 647px @1440 · 952px @1280 · 876px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 85/85px · first child 1360px wide · gap 64px
- colour: background #ffffff · text #000000 · align center
- headline: Alliance No.2 Light 80px/88px weight 300 tracking -4px #1e211e
- body: Geist Variable 21px/29.4px weight 400 #1e211e
- motion: none observed
- example headline: "We invest in our people"

### `content.open-roles-section` (CONTENT)

- appears on 1 route(s), 1 instance(s); tag `<section>`, named "Open Roles Section"
- height: 525px @1440 · 427px @1280 · 341px @390
- columns: 3 @1440 · 3 @1280 · 2 @390
- box: padding 94/94px · first child 1360px wide · gap 64px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Variable 21px/29.4px weight 400 #1e211e
- motion: appear-on-enter
- example headline: "Open roles"

### `content.content-section` (CONTENT)

- appears on 11 route(s), 11 instance(s); tag `<section>`, named "Content Section"
- height: 3474px @1440 · 3136px @1280 · 5145px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 96/96px · first child 1360px wide · gap 64px
- colour: background #fafafa · text #000000 · align start
- headline: Inter 16px/19.2px weight 400 #000000
- body: Geist Mono 12px/14.4px weight 400 #1e211e
- layout: two text columns, 432 / 864px, text on the right
- motion: scroll-linked, appear-on-enter

### `shell.desktop-filled` (SHELL)

- appears on 2 route(s), 2 instance(s); tag `<header>`, named "Desktop/Filled"
- height: 72px @1440 · ?px @1280 · ?px @390
- columns: 2 @1440 · ? @1280 · ? @390
- box: padding 0/0px · first child 1440px wide · gap 64px
- colour: background #ffffff · text #000000 · align start
- body: Geist Variable 16px/22.4px weight 400 #1e211e
- motion: none observed

### `hero.main` (HERO)

- appears on 2 route(s), 2 instance(s); tag `<main>`, named "Main"
- height: 1173px @1440 · 1039px @1280 · 1229px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1440px wide · gap 64px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Regular 52px/62.4px weight 400 tracking -2.08px #1e211e
- body: Geist Variable 19px/26.6px weight 400 #1e211e
- layout: two text columns, 584 / 584px, text on the left
- motion: css-transition, appear-on-enter
- example headline: "Contact sales"

### `shell.desktop` (SHELL)

- appears on 2 route(s), 2 instance(s); tag `<footer>`, named "Desktop"
- height: 818px @1440 · ?px @1280 · ?px @390
- columns: 1 @1440 · ? @1280 · ? @390
- box: padding 80/80px · first child 1360px wide · gap 160px
- colour: background #1e211e · text #000000 · align start
- headline: Alliance No.2 Regular 24px/28.8px weight 400 tracking -0.24px #ffffff
- body: Geist Variable 17px/23.8px weight 400 #ffffff
- motion: none observed
- example headline: "Getting you from "sent" to "paid", your way."

### `content.white` (CONTENT)

- appears on 2 route(s), 2 instance(s); tag `<div>`, named "White"
- height: 1991px @1440 · ?px @1280 · ?px @390
- columns: 1 @1440 · ? @1280 · ? @390
- box: padding 0/0px · first child ?px wide · gap none
- colour: background #ffffff · text #000000 · align start
- motion: none observed

### `content.container` (CONTENT)

- appears on 8 route(s), 8 instance(s); tag `<div>`, named "Container"
- height: 417px @1440 · 409px @1280 · 514px @390
- columns: 3 @1440 · 4 @1280 · 3 @390
- box: padding 0/0px · first child 1020px wide · gap 48px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Light 80px/88px weight 300 tracking -4px #1e211e
- body: Geist Mono 16px/22.4px weight 400 #1e211e
- motion: appear-on-enter
- example headline: "Agents That Learn How You Work (Not Software You Have to Learn)"

### `features.featured-image-wrapper` (FEATURES)

- appears on 8 route(s), 8 instance(s); tag `<div>`, named "Featured Image Wrapper"
- height: 760px @1440 · 684px @1280 · 196px @390
- columns: 1 @1440 · 1 @1280 · 1 @390
- box: padding 0/0px · first child 1360px wide · gap 24px
- colour: background #ffffff · text #000000 · align start
- motion: appear-on-enter

### `content.other-articles-section` (CONTENT)

- appears on 8 route(s), 8 instance(s); tag `<section>`, named "Other Articles Section"
- height: 1205px @1440 · 1401px @1280 · 1911px @390
- columns: 3 @1440 · 3 @1280 · 3 @390
- box: padding 96/96px · first child 1360px wide · gap 64px
- colour: background #ffffff · text #000000 · align left
- headline: Alliance No.2 Regular 58px/69.6px weight 400 tracking -2.9px #1e211e
- body: Geist Variable 19px/26.6px weight 400 #ffffff
- motion: none observed
- example headline: "Looking for more? Dive into our other articles, updates, and strategies"

## Routes

| Route | Template | Sections in order |
|---|---|---|
| `/` | `template.home` | `content.framer-huxi9o-container` → `hero.hero-section` → `content.roi-section` → `content.problem-section` → `features.key-features-section` → `features.other-features-section` → `proof.clients-section` → `cta.cta-section-2` → `features.integrations-section` → `support.faq-section` → `cta.another-cta` → `content.framer-39uowv-container` |
| `/about` | `template.about` | `content.framer-guhhla-container` → `hero.hero-section` → `content.intro-section` → `content.approach-section` → `content.team-members-section` → `content.team-members-section` → `cta.another-cta` → `content.framer-1nc9gyu-container` |
| `/blog` | `template.blog` | `content.framer-guhhla-container` → `hero.hero-section` → `content.blog-section` → `content.framer-1nc9gyu-container` |
| `/customers` | `template.customers` | `content.framer-1h4pb9v-container` → `hero.hero-section` → `proof.testimonials-section` → `cta.another-cta` → `content.framer-gzkazm-container` |
| `/careers` | `template.careers` | `content.framer-1h4pb9v-container` → `hero.hero-section` → `features.benefits-section` → `content.team-members-section` → `content.open-roles-section` → `content.framer-gzkazm-container` |
| `/contact` | `template.contact` | `content.framer-1h4pb9v-container` → `hero.hero-section` → `content.content-section` → `support.faq-section` → `content.framer-gzkazm-container` |
| `/contact/sales` | `template.contact-2` | `shell.desktop-filled` → `hero.main` → `shell.desktop` → `content.white` |
| `/legal/terms-of-service` | `template.legal` | `content.framer-1h4pb9v-container` → `hero.hero-section` → `content.content-section` → `content.framer-gzkazm-container` |
| `/legal/privacy` | `template.legal` | `content.framer-1h4pb9v-container` → `hero.hero-section` → `content.content-section` → `content.framer-gzkazm-container` |
| `/blog/what-we-hear-when-we-talk-to-finance-teams` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/blog/from-source-of-truth-to-source-of-action` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/blog/agents-that-learn-how-you-work` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/blog/from-aging-reports-to-cash-control` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/blog/when-software-becomes-a-teammate` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/blog/how-to-choose-the-right-collections-software` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/blog/why-collections-software-keeps-failing-finance-teams` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/blog/how-ai-agents-are-transforming-ar-and-collections` | `template.blog-2` | `content.framer-1h4pb9v-container` → `content.container` → `features.featured-image-wrapper` → `content.content-section` → `content.other-articles-section` → `content.framer-gzkazm-container` |
| `/contact/support` | `template.contact-2` | `shell.desktop-filled` → `hero.main` → `shell.desktop` → `content.white` |
