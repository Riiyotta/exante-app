#!/usr/bin/env node
// Re-measure every route's section heights from the BUILT clone at a 1440px viewport.
//
//   npx vite build --outDir <scratch>            (from the package root)
//   npx vite preview --outDir <scratch> --port <port>
//   NODE_PATH="$(npm root -g)" node design-repo/extraction/measure_sections.mjs --base http://localhost:<port> > heights.json
//   python3 design-repo/extraction/record_heights.py heights.json
//
// Playwright is resolved through require() so NODE_PATH works (ESM `import` ignores NODE_PATH);
// PLAYWRIGHT_MODULE may name the module path instead. No browser or module path is stored in this repo.
// Each section root carries data-clone-section="<ComponentName>" in the clone's markup; the component
// name is mapped back to a section id by record_heights.py through measured-values.json's citations.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const base = (args[args.indexOf("--base") + 1] || "http://localhost:4173").replace(/\/$/, "");
const WIDTH = 1440, HEIGHT = 900;
const ledger = JSON.parse(readFileSync(join(here, "measured-values.json"), "utf8"));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });
const out = { viewport: { width: WIDTH, height: HEIGHT }, measuredAt: new Date().toISOString(), base: "local vite preview of the built clone", routes: {} };
for (const r of ledger.routes) {
  await page.goto(base + r.route, { waitUntil: "networkidle" });
  // walk the page once so lazy/appear-on-enter content settles, then measure from the top
  const h0 = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < h0; y += HEIGHT) { await page.evaluate((yy) => window.scrollTo(0, yy), y); await page.waitForTimeout(60); }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(400);
  // components whose body the ledger decomposes into <h3>-bounded parts: measure each part between visible <h3> tops
  const split = {};
  for (const s of r.sections) if (s.part && s.part.index > 0) split[s.component] = (split[s.component] || 0) + 1;
  out.routes[r.route] = await page.evaluate((split) => {
    const secs = [...document.querySelectorAll("[data-clone-section]")].map((el) => {
      const cs = getComputedStyle(el), rect = el.getBoundingClientRect();
      let fixed = false;
      for (let n = el; n && n !== document.body; n = n.parentElement) {
        const p = getComputedStyle(n).position;
        // fixed/sticky/absolute boxes (the nav bar, a full-bleed background layer) take no page height
        if (p === "fixed" || p === "sticky" || p === "absolute") { fixed = true; break; }
      }
      const comp = el.getAttribute("data-clone-section");
      const rec = { component: comp, heightPx: Math.round(rect.height), topPx: Math.round(rect.top + window.scrollY),
               position: cs.position, inFlow: !fixed && cs.display !== "none" && rect.height > 0, outOfFlowReason: fixed ? "fixed-sticky-or-absolute" : (cs.display === "none" || rect.height === 0 ? "not-rendered-at-1440" : null) };
      if (split[comp]) {
        const tops = [...el.querySelectorAll("h3")].filter((h) => h.getBoundingClientRect().height > 0).map((h) => h.getBoundingClientRect().top - rect.top);
        const edges = [0, ...tops, rect.height];
        rec.parts = edges.slice(0, -1).map((t, i) => Math.round(edges[i + 1] - t));
        rec.partsExpected = split[comp] + 1;
      }
      return rec;
    });
    return { pageHeightPx: document.documentElement.scrollHeight, sections: secs };
  }, split);
  process.stderr.write(`measured ${r.route}: ${out.routes[r.route].sections.length} sections, page ${out.routes[r.route].pageHeightPx}px\n`);
}
await browser.close();
process.stdout.write(JSON.stringify(out, null, 1) + "\n");
