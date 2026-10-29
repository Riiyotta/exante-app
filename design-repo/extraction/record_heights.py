#!/usr/bin/env python3
"""Merge a measure_sections.mjs run into extraction/measured-values.json under `sectionHeights`.

Each measured data-clone-section element is matched to the ledger's section entries for that route by component
name, in order; a decomposed body (ledger entries with `part`) is matched part-by-part to the measured
<h3>-bounded heights. Any mismatch (a section the browser did not find, a part count that differs) is an error
and nothing is written.

Usage: python3 design-repo/extraction/record_heights.py <heights.json>
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "measured-values.json")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run = json.load(open(sys.argv[1], encoding="utf-8"))
    led = json.load(open(LEDGER, encoding="utf-8"))
    if run["viewport"]["width"] != 1440:
        sys.exit(f"measured at {run['viewport']['width']}px, the gate requires 1440px")
    out, problems = {}, []
    for r in led["routes"]:
        m = run["routes"].get(r["route"])
        if not m:
            problems.append(f"{r['route']}: not measured"); continue
        pool = list(m["sections"])
        recs = []
        i = 0
        while i < len(r["sections"]):
            s = r["sections"][i]
            k = next((j for j, x in enumerate(pool) if x["component"] == s["component"]), None)
            if k is None:
                problems.append(f"{r['route']}: {s['component']} ({s['id']}) not found in the measured page"); i += 1; continue
            el = pool.pop(k)
            group = [s] + [x for x in r["sections"][i + 1:] if x.get("part") and x["component"] == s["component"]] if s.get("part") else [s]
            if s.get("part"):
                parts = el.get("parts") or []
                if len(parts) != len(group):
                    problems.append(f"{r['route']}: {s['component']} measured {len(parts)} parts, ledger has {len(group)}")
                for g, h in zip(group, parts):
                    recs.append({"idx": g["idx"], "id": g["id"], "component": g["component"], "heightPx": h, "inFlow": el["inFlow"],
                                 **({"outOfFlowReason": el["outOfFlowReason"]} if el.get("outOfFlowReason") else {})})
            else:
                recs.append({"idx": s["idx"], "id": s["id"], "component": s["component"], "heightPx": el["heightPx"], "inFlow": el["inFlow"],
                             **({"outOfFlowReason": el["outOfFlowReason"]} if el.get("outOfFlowReason") else {})})
            i += len(group)
        out[r["route"]] = {"template": r["template"], "pageHeightPx": m["pageHeightPx"], "sections": recs}
    if problems:
        print("\n".join(problems)); sys.exit(1)
    led["sectionHeights"] = {
        "viewport": {"width": 1440, "height": run["viewport"]["height"]},
        "viewportLabel": "1440px desktop",
        "measuredAt": run["measuredAt"],
        "method": ("built clone (npx vite build --outDir <scratch>; npx vite preview --outDir <scratch>), headless Chromium via Playwright, "
                   "extraction/measure_sections.mjs; each page scrolled once top-to-bottom before measuring. Height = the data-clone-section "
                   "element's bounding box; a decomposed body is split at the top of each visible <h3>. Elements inside a fixed, sticky or "
                   "absolute box are recorded with inFlow=false and take no page height."),
        "routes": out,
    }
    json.dump(led, open(LEDGER, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(LEDGER, "a", encoding="utf-8").write("\n")
    print(f"sectionHeights recorded for {len(out)} routes at 1440px")


if __name__ == "__main__":
    main()
