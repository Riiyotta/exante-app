#!/usr/bin/env python3
"""Whole-page-wrapper quality gate (R9), called by verify_all.py.

Inputs: extraction/measured-values.json `sectionHeights` (measured from the BUILT clone at 1440px by
measure_sections.mjs + record_heights.py), sections/*.json categories, and extraction/wrapper-whitelist.json.

Thresholds are pinned HERE (not read from JSON):
  HERO taller than 1800px                     -> warn
  HERO taller than 3000px                     -> error unless whitelisted (a whitelisted hit still warns)
  one in-flow section > 50% of its page height -> warn
  one in-flow section > 60% of its page height -> error unless whitelisted
Share checks skip pages with fewer than 3 in-flow non-SHELL sections; SHELL sections and anything inside a
fixed/sticky/absolute box (inFlow=false) are excluded. Missing measurement or a non-1440px viewport is an error.
Whitelist entries need reviewedBy, a justification of 30+ characters and a maxHeightPx above the measured
height; an entry that matches nothing (stale) or is over its cap fails. An agent's reviewedBy must say
"agent attestation, not a human sign-off".

Usage: python3 extraction/wrapper_gate.py      (prints findings; exit 1 on error)
Import: gate(ledger, sections, whitelist) -> (errors, warnings)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VIEWPORT_WIDTH = 1440
HERO_WARN_PX, HERO_ERROR_PX = 1800, 3000
SHARE_WARN, SHARE_ERROR = 0.50, 0.60
MIN_IN_FLOW = 3
AGENT_PHRASE = "agent attestation, not a human sign-off"


def gate(ledger, sections, whitelist):
    errors, warnings = [], []
    sh = ledger.get("sectionHeights")
    if not sh:
        return ["wrapper gate: measured-values.json has no sectionHeights (missing measurement)"], []
    if sh.get("viewport", {}).get("width") != VIEWPORT_WIDTH:
        errors.append(f"wrapper gate: sectionHeights measured at {sh.get('viewport', {}).get('width')}px, must be {VIEWPORT_WIDTH}px")
    entries = whitelist.get("entries", [])
    used = set()
    for i, w in enumerate(entries):
        if not w.get("reviewedBy"): errors.append(f"wrapper whitelist[{i}]: reviewedBy is required")
        elif "agent" in w["reviewedBy"].lower() and AGENT_PHRASE not in w["reviewedBy"]:
            errors.append(f"wrapper whitelist[{i}]: an agent reviewer must say '{AGENT_PHRASE}'")
        if len(w.get("justification", "")) < 30: errors.append(f"wrapper whitelist[{i}]: justification must be at least 30 characters")
        if not isinstance(w.get("maxHeightPx"), int): errors.append(f"wrapper whitelist[{i}]: maxHeightPx is required")

    def allowed(route, sid, h):
        for i, w in enumerate(entries):
            if w.get("route") == route and w.get("section") == sid:
                used.add(i)
                if isinstance(w.get("maxHeightPx"), int) and h > w["maxHeightPx"]:
                    errors.append(f"wrapper whitelist[{i}]: {sid} on {route} measures {h}px, over its cap {w['maxHeightPx']}px")
                    return False
                return len(w.get("justification", "")) >= 30 and bool(w.get("reviewedBy"))
        return False

    routes = sh.get("routes", {})
    for r in ledger.get("routes", []):
        m = routes.get(r["route"])
        if not m:
            errors.append(f"wrapper gate: route {r['route']} ({r['template']}) has no measured section heights"); continue
        if len(m.get("sections", [])) != len(r["sections"]) or [s["id"] for s in m["sections"]] != [s["id"] for s in r["sections"]]:
            errors.append(f"wrapper gate: {r['route']}: measured sections do not match the ledger's section list (missing measurement)"); continue
        page = m.get("pageHeightPx") or 0
        if page <= 0:
            errors.append(f"wrapper gate: {r['route']}: no page height"); continue
        for s in m["sections"]:
            if not isinstance(s.get("heightPx"), (int, float)):
                errors.append(f"wrapper gate: {r['route']}: {s['id']} has no heightPx (missing measurement)"); continue
            if sections.get(s["id"], {}).get("category") == "HERO" and s["heightPx"] > HERO_WARN_PX:
                if s["heightPx"] > HERO_ERROR_PX and not allowed(r["route"], s["id"], s["heightPx"]):
                    errors.append(f"wrapper gate: HERO {s['id']} on {r['route']} is {s['heightPx']}px (> {HERO_ERROR_PX}px)")
                else:
                    warnings.append(f"wrapper gate: HERO {s['id']} on {r['route']} is {s['heightPx']}px (> {HERO_WARN_PX}px)")
        flow = [s for s in m["sections"] if s.get("inFlow") and sections.get(s["id"], {}).get("category") != "SHELL"]
        if len(flow) < MIN_IN_FLOW:
            continue
        for s in flow:
            share = s["heightPx"] / page
            if share > SHARE_ERROR and not allowed(r["route"], s["id"], s["heightPx"]):
                errors.append(f"wrapper gate: {s['id']} holds {share:.0%} of {r['route']} ({s['heightPx']}/{page}px, > {SHARE_ERROR:.0%})")
            elif share > SHARE_WARN:
                warnings.append(f"wrapper gate: {s['id']} holds {share:.0%} of {r['route']} ({s['heightPx']}/{page}px, > {SHARE_WARN:.0%})")
    for i, w in enumerate(entries):
        if i not in used:
            errors.append(f"wrapper whitelist[{i}]: stale entry ({w.get('section')} on {w.get('route')} no longer needs or matches a gate hit)")
    return errors, warnings


def load_inputs(repo=REPO):
    led = json.load(open(os.path.join(repo, "extraction", "measured-values.json"), encoding="utf-8"))
    secs = {}
    for f in sorted(os.listdir(os.path.join(repo, "sections"))):
        if f.endswith(".json"):
            c = json.load(open(os.path.join(repo, "sections", f), encoding="utf-8")); secs[c["id"]] = c
    wl_p = os.path.join(repo, "extraction", "wrapper-whitelist.json")
    wl = json.load(open(wl_p, encoding="utf-8")) if os.path.isfile(wl_p) else {"entries": []}
    return led, secs, wl


def main():
    e, w = gate(*load_inputs())
    for x in w: print("WARN:", x)
    for x in e: print("ERROR:", x)
    print(f"wrapper gate: {len(e)} error(s), {len(w)} warning(s)")
    sys.exit(1 if e else 0)


if __name__ == "__main__":
    main()
