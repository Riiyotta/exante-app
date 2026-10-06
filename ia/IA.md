# https://www.exante.app/

Source: https://www.exante.app/ · website-builder crawl, 2026-10-05T13:10:06Z
Status: **measured-from-mirror** · production approved: **false**
18 routes · 9 templates · 31 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 3 templates (Blog pages, Contact pages, Legal pages) account for 12 of 18 routes (67%). The remaining 6 routes span 6 templates.

| template | routes | share |
|---|---:|---:|
| Blog pages | 8 | 44% |
| Contact pages | 2 | 11% |
| Legal pages | 2 | 11% |
| Home | 1 | 6% |
| About | 1 | 6% |
| Blog | 1 | 6% |
| Customers | 1 | 6% |
| Careers | 1 | 6% |
| Contact | 1 | 6% |

## Page chrome

**16 routes carry chrome = `none`** — Home, About, Blog, Customers, Careers, Contact, Legal pages, Blog pages.

**2 routes carry chrome = `partial`** — Contact pages.

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `content.framer-1h4pb9v-container` | CONTENT | 5 | 13 | `src/pages/Customers.jsx` | Appears on 13 routes. |
| `content.framer-gzkazm-container` | CONTENT | 5 | 13 | `src/pages/Customers.jsx` | Appears on 13 routes. |
| `content.content-section` | CONTENT | 3 | 11 | `src/pages/Contact.jsx` | Appears on 11 routes. |
| `hero.hero-section` | HERO | 7 | 8 | `src/pages/HomePage.jsx` | Appears on 8 routes. |
| `content.container` | CONTENT | 1 | 8 | `src/pages/BlogWhatWeHear.jsx` | Appears on 8 routes. |
| `content.other-articles-section` | CONTENT | 1 | 8 | `src/pages/BlogWhatWeHear.jsx` | Appears on 8 routes. |
| `features.featured-image-wrapper` | FEATURES | 1 | 8 | `src/pages/BlogWhatWeHear.jsx` | Appears on 8 routes. |
| `cta.another-cta` | CTA | 3 | 3 | `src/pages/HomePage.jsx` | Appears on 3 routes. |
| `content.framer-1nc9gyu-container` | CONTENT | 2 | 2 | `src/pages/About.jsx` | Appears on 2 routes. |
| `content.framer-guhhla-container` | CONTENT | 2 | 2 | `src/pages/About.jsx` | Appears on 2 routes. |
| `content.team-members-section` | CONTENT | 2 | 2 | `src/pages/About.jsx` | Appears on 2 routes. |
| `support.faq-section` | SUPPORT | 2 | 2 | `src/pages/HomePage.jsx` | Appears on 2 routes. |
| `content.white` | CONTENT | 1 | 2 | `src/pages/ContactSales.jsx` | Appears on 2 routes. |
| `hero.main` | HERO | 1 | 2 | `src/pages/ContactSales.jsx` | Appears on 2 routes. |
| `shell.desktop` | SHELL | 1 | 2 | `src/pages/ContactSales.jsx` | Appears on 2 routes. |
| `shell.desktop-filled` | SHELL | 1 | 2 | `src/pages/ContactSales.jsx` | Appears on 2 routes. |
| `content.approach-section` | CONTENT | 1 | 1 | `src/pages/About.jsx` | Appears on 1 route. |
| `content.blog-section` | CONTENT | 1 | 1 | `src/pages/Blog.jsx` | Appears on 1 route. |
| `content.framer-39uowv-container` | CONTENT | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `content.framer-huxi9o-container` | CONTENT | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `content.intro-section` | CONTENT | 1 | 1 | `src/pages/About.jsx` | Appears on 1 route. |
| `content.open-roles-section` | CONTENT | 1 | 1 | `src/pages/Careers.jsx` | Appears on 1 route. |
| `content.problem-section` | CONTENT | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `content.roi-section` | CONTENT | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `cta.cta-section-2` | CTA | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `features.benefits-section` | FEATURES | 1 | 1 | `src/pages/Careers.jsx` | Appears on 1 route. |
| `features.integrations-section` | FEATURES | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `features.key-features-section` | FEATURES | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `features.other-features-section` | FEATURES | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `proof.clients-section` | PROOF | 1 | 1 | `src/pages/HomePage.jsx` | Appears on 1 route. |
| `proof.testimonials-section` | PROOF | 1 | 1 | `src/pages/Customers.jsx` | Appears on 1 route. |

**9 shared sections** appear in more than one template and belong in a component library.

**22 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

## Templates

### Home — `template.home`

1 route · `/` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-huxi9o-container` | page-local |
| 2 | HERO | `hero.hero-section` | shared ×7 |
| 3 | CONTENT | `content.roi-section` | page-local |
| 4 | CONTENT | `content.problem-section` | page-local |
| 5 | FEATURES | `features.key-features-section` | page-local |
| 6 | FEATURES | `features.other-features-section` | page-local |
| 7 | PROOF | `proof.clients-section` | page-local |
| 8 | CTA | `cta.cta-section-2` | page-local |
| 9 | FEATURES | `features.integrations-section` | page-local |
| 10 | SUPPORT | `support.faq-section` | shared ×2 |
| 11 | CTA | `cta.another-cta` | shared ×3 |
| 12 | CONTENT | `content.framer-39uowv-container` | page-local |

### About — `template.about`

1 route · `/about` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-guhhla-container` | shared ×2 |
| 2 | HERO | `hero.hero-section` | shared ×7 |
| 3 | CONTENT | `content.intro-section` | page-local |
| 4 | CONTENT | `content.approach-section` | page-local |
| 5 | CONTENT | `content.team-members-section` | shared ×2 |
| 6 | CONTENT | `content.team-members-section` | shared ×2 |
| 7 | CTA | `cta.another-cta` | shared ×3 |
| 8 | CONTENT | `content.framer-1nc9gyu-container` | shared ×2 |

### Blog — `template.blog`

1 route · `/blog` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-guhhla-container` | shared ×2 |
| 2 | HERO | `hero.hero-section` | shared ×7 |
| 3 | CONTENT | `content.blog-section` | page-local |
| 4 | CONTENT | `content.framer-1nc9gyu-container` | shared ×2 |

### Customers — `template.customers`

1 route · `/customers` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-1h4pb9v-container` | shared ×5 |
| 2 | HERO | `hero.hero-section` | shared ×7 |
| 3 | PROOF | `proof.testimonials-section` | page-local |
| 4 | CTA | `cta.another-cta` | shared ×3 |
| 5 | CONTENT | `content.framer-gzkazm-container` | shared ×5 |

### Careers — `template.careers`

1 route · `/careers` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-1h4pb9v-container` | shared ×5 |
| 2 | HERO | `hero.hero-section` | shared ×7 |
| 3 | FEATURES | `features.benefits-section` | page-local |
| 4 | CONTENT | `content.team-members-section` | shared ×2 |
| 5 | CONTENT | `content.open-roles-section` | page-local |
| 6 | CONTENT | `content.framer-gzkazm-container` | shared ×5 |

### Contact — `template.contact`

1 route · `/contact` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-1h4pb9v-container` | shared ×5 |
| 2 | HERO | `hero.hero-section` | shared ×7 |
| 3 | CONTENT | `content.content-section` | shared ×3 |
| 4 | SUPPORT | `support.faq-section` | shared ×2 |
| 5 | CONTENT | `content.framer-gzkazm-container` | shared ×5 |

### Contact pages — `template.contact-2`

2 routes · `/contact/sales`, `/contact/support` · chrome: **partial**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.desktop-filled` | page-local |
| 2 | HERO | `hero.main` | page-local |
| 3 | SHELL | `shell.desktop` | page-local |
| 4 | CONTENT | `content.white` | page-local |

### Legal pages — `template.legal`

2 routes · `/legal/terms-of-service`, `/legal/privacy` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-1h4pb9v-container` | shared ×5 |
| 2 | HERO | `hero.hero-section` | shared ×7 |
| 3 | CONTENT | `content.content-section` | shared ×3 |
| 4 | CONTENT | `content.framer-gzkazm-container` | shared ×5 |

### Blog pages — `template.blog-2`

8 routes · `/blog/what-we-hear-when-we-talk-to-finance-teams`, `/blog/from-source-of-truth-to-source-of-action`, `/blog/agents-that-learn-how-you-work`, `/blog/from-aging-reports-to-cash-control`, `/blog/when-software-becomes-a-teammate`, `/blog/how-to-choose-the-right-collections-software`, `/blog/why-collections-software-keeps-failing-finance-teams`, `/blog/how-ai-agents-are-transforming-ar-and-collections` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | CONTENT | `content.framer-1h4pb9v-container` | shared ×5 |
| 2 | CONTENT | `content.container` | page-local |
| 3 | FEATURES | `features.featured-image-wrapper` | page-local |
| 4 | CONTENT | `content.content-section` | shared ×3 |
| 5 | CONTENT | `content.other-articles-section` | page-local |
| 6 | CONTENT | `content.framer-gzkazm-container` | shared ×5 |

## Section reference

### CONTENT

_The substantive body of a page: articles, listings, resources and general sections._

**`content.approach-section`** — "Approach Section" — a <section> block named by a data attribute. Typically 940px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/About.jsx`

**`content.blog-section`** — "Blog Section" — a <section> block named by a data attribute. Typically 2330px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/Blog.jsx`

**`content.container`** — "Container" — a <div> block named by a data attribute; first heading: "Agents That Learn How You Work (Not Software You Have to Learn)". Typically 417px tall at 1440px wide.

· Appears on 8 routes. · appears on 8 routes · implemented by `src/pages/BlogWhatWeHear.jsx`

**`content.content-section`** — "Content Section" — a <section> block named by a data attribute. Typically 3474px tall at 1440px wide.

· Appears on 11 routes. · appears on 11 routes · implemented by `src/pages/Contact.jsx`

**`content.framer-1h4pb9v-container`** — "framer-1h4pb9v-container" — a <div> block named by its CSS class. Typically 72px tall at 1440px wide.

· Appears on 13 routes. · appears on 13 routes · implemented by `src/pages/Customers.jsx`

**`content.framer-1nc9gyu-container`** — "framer-1nc9gyu-container" — a <div> block named by its CSS class; first heading: "Getting you from "sent" to "paid", your way.". Typically 818px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/About.jsx`

**`content.framer-39uowv-container`** — "framer-39uowv-container" — a <div> block named by its CSS class; first heading: "Getting you from "sent" to "paid", your way.". Typically 818px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

**`content.framer-guhhla-container`** — "framer-guhhla-container" — a <div> block named by its CSS class. Typically 72px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/About.jsx`

**`content.framer-gzkazm-container`** — "framer-gzkazm-container" — a <div> block named by its CSS class; first heading: "Getting you from "sent" to "paid", your way.". Typically 818px tall at 1440px wide.

· Appears on 13 routes. · appears on 13 routes · implemented by `src/pages/Customers.jsx`

**`content.framer-huxi9o-container`** — "framer-huxi9o-container" — a <div> block named by its CSS class. Typically 72px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

**`content.intro-section`** — "Intro Section" — a <section> block named by a data attribute; first heading: "Built for autonomous finance. Run by people who’ve done the work.". Typically 374px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/About.jsx`

**`content.open-roles-section`** — "Open Roles Section" — a <section> block named by a data attribute; first heading: "Open roles". Typically 525px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/Careers.jsx`

**`content.other-articles-section`** — "Other Articles Section" — a <section> block named by a data attribute; first heading: "Looking for more? Dive into our other articles, updates, and strategies". Typically 1205px tall at 1440px wide.

· Appears on 8 routes. · appears on 8 routes · implemented by `src/pages/BlogWhatWeHear.jsx`

**`content.problem-section`** — "Problem Section" — a <section> block named by a data attribute; first heading: "Your collections process can't scale, and it's costing you". Typically 779px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

**`content.roi-section`** — "ROI Section" — a <section> block named by a data attribute; first heading: "Go from outstanding invoices to outstanding cash flow in no time.". Typically 777px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

**`content.team-members-section`** — "Team Members Section" — a <section> block named by a data attribute; first heading: "Built by a team with deep finance, engineering, and enterprise experience". Typically 1424px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/About.jsx`

**`content.white`** — "White" — a <div> block named by a data attribute. Typically 1991px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/ContactSales.jsx`

### HERO

_Page-opening block: the main headline (h1) and first call to action._

**`hero.hero-section`** — "Hero Section" — a <section> block named by a data attribute; first heading: "AI teammate that handles collections". Typically 822px tall at 1440px wide.

· Appears on 8 routes. · appears on 8 routes · implemented by `src/pages/HomePage.jsx`

**`hero.main`** — "Main" — a <main> block named by a data attribute; first heading: "Contact sales". Typically 1173px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/ContactSales.jsx`

### FEATURES

_Product explanation: capabilities, benefits, workflows and integrations._

**`features.benefits-section`** — "Benefits Section" — a <section> block named by a data attribute; first heading: "We invest in our people". Typically 647px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/Careers.jsx`

**`features.featured-image-wrapper`** — "Featured Image Wrapper" — a <div> block named by a data attribute. Typically 760px tall at 1440px wide.

· Appears on 8 routes. · appears on 8 routes · implemented by `src/pages/BlogWhatWeHear.jsx`

**`features.integrations-section`** — "Integrations Section" — a <section> block named by a data attribute; first heading: "No rip-and-replace required". Typically 578px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

**`features.key-features-section`** — "Key Features Section" — a <section> block named by a data attribute; first heading: "No matter what's outstanding, Exante leaves no dollar behind". Typically 1227px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

**`features.other-features-section`** — "Other Features Section" — a <section> block named by a data attribute; first heading: "Your imagination is the only limit". Typically 1139px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

### PROOF

_Social proof: customer logos, testimonials, reviews and case studies._

**`proof.clients-section`** — "Clients Section" — a <section> block named by a data attribute; first heading: "Trusted by forward-thinking finance teams". Typically 472px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

**`proof.testimonials-section`** — "Testimonials Section" — a <section> block named by a data attribute. Typically 757px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/Customers.jsx`

### CTA

_Conversion prompts: sign-up, demo, newsletter and get-started bands._

**`cta.another-cta`** — "Another CTA" — a <section> block named by a data attribute; first heading: "Get started right now with one of our pre-built AI agents!". Typically 315px tall at 1440px wide.

· Appears on 3 routes. · appears on 3 routes · implemented by `src/pages/HomePage.jsx`

**`cta.cta-section-2`** — "CTA Section #2" — a <section> block named by a data attribute; first heading: "Go live in days and get paid in a week". Typically 565px tall at 1440px wide.

· Appears on 1 route. · appears on 1 routes · implemented by `src/pages/HomePage.jsx`

### SUPPORT

_Questions and contact: FAQs, help, forms._

**`support.faq-section`** — "FAQ Section" — a <section> block named by a data attribute; first heading: "Frequently asked questions". Typically 963px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/HomePage.jsx`

### SHELL

_Site chrome: navigation, header, footer, announcement bars and other elements carried across pages._

**`shell.desktop`** — "Desktop" — a <footer> block named by a data attribute; first heading: "Getting you from "sent" to "paid", your way.". Typically 818px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/ContactSales.jsx`

**`shell.desktop-filled`** — "Desktop/Filled" — a <header> block named by a data attribute. Typically 72px tall at 1440px wide.

· Appears on 2 routes. · appears on 2 routes · implemented by `src/pages/ContactSales.jsx`
