#!/usr/bin/env python3
"""Regenerate tokens/llm/token-catalog.json and tokens/llm/token-policy.json from the real token files.

Nothing here is hand-typed: every token id, tier, type and resolved value comes from tokens/00-foundation,
10-semantic, 20-component, 30-layout and tokens/themes/*.json. The curated `categories` (what a PageSpec may
reference) are the semantic, component and layout tokens; foundation tokens are catalogued (so a generator can
see the real scale) but not referenceable. verify_all.py re-runs build() and fails if the files on disk differ.

Usage: python3 design-repo/extraction/build_token_llm.py [--check]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VERSION = "0.2.0"


def J(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


def files(d):
    p = os.path.join(REPO, d)
    return sorted(f for f in os.listdir(p) if f.endswith(".json"))


def build():
    tiers = {}
    for tier in ("00-foundation", "10-semantic", "30-layout"):
        for f in files(f"tokens/{tier}"):
            for k, v in J(f"tokens/{tier}/{f}").get("tokens", {}).items():
                tiers[k] = (tier, f, v)
    for f in files("tokens/20-component"):
        d = J(f"tokens/20-component/{f}")
        for k, v in d.get("tokens", {}).items():
            tiers[f"{d['component']}.{k}"] = ("20-component", f, v)
    vals = {k: v[2].get("$value") for k, v in tiers.items()}

    def resolve(v, depth=0):
        if isinstance(v, dict):
            return {k: resolve(x, depth) for k, x in v.items()}
        m = re.match(r"^\{(.+)\}$", v) if isinstance(v, str) else None
        return resolve(vals.get(m.group(1), v), depth + 1) if m and depth < 6 else v

    def category(tid, tier, v):
        t = v.get("$type")
        if tier == "20-component": return "component"
        if tier == "30-layout": return "layout"
        if tid.startswith(("surface.", "text.", "border.", "accent.")) or t == "color": return "color"
        if tid.startswith(("typography.", "fontFamily.", "fontSize.", "fontWeight.", "lineHeight.")): return "typography"
        if tid.startswith("radius."): return "radius"
        if tid.startswith("elevation."): return "elevation"
        if tid.startswith(("motion.", "duration.", "easing.")): return "motion"
        if tid.startswith("space."): return "spacing"
        if tid.startswith("breakpoint."): return "breakpoint"
        if tid.startswith("iconSize."): return "iconSize"
        return "other"

    tokens = {}
    for tid in sorted(tiers):
        tier, f, v = tiers[tid]
        tokens[tid] = {"tier": tier, "file": f"tokens/{tier}/{f}", "category": category(tid, tier, v),
                       "type": v.get("$type"), "value": resolve(v.get("$value")),
                       "referenceable": tier != "00-foundation"}
        if isinstance(v.get("$value"), str) and v["$value"].startswith("{"):
            tokens[tid]["ref"] = v["$value"][1:-1]
    cats = {}
    for tid, t in tokens.items():
        if t["referenceable"]:
            cats.setdefault(t["category"], []).append(tid)
    themes = {}
    for f in files("tokens/themes"):
        th = J(f"tokens/themes/{f}")
        themes[th["id"]] = {"file": f"tokens/themes/{f}", "mode": th.get("mode"), "resolves": sorted(th["resolves"])}
    fonts = sorted({t["value"] for t in tokens.values() if t["type"] == "fontFamily"})
    spacing = sorted(tid for tid, t in tokens.items() if t["category"] == "layout" and re.search(r"(Padding|Gap|gutter)", tid))
    catalog = {
        "version": VERSION,
        "generatedBy": "extraction/build_token_llm.py (derived from the token files; do not edit by hand)",
        "note": "Full catalog of every real token. `categories` lists the referenceable view (semantic, component, layout); foundation tokens are catalogued with referenceable=false.",
        "categories": {k: sorted(v) for k, v in sorted(cats.items())},
        "tokens": tokens,
        "fontFamilies": fonts,
        "spacingTokens": spacing,
        "themes": themes,
        "counts": {"tokens": len(tokens), "referenceable": sum(1 for t in tokens.values() if t["referenceable"]),
                   "byTier": {tr: sum(1 for t in tokens.values() if t["tier"] == tr) for tr in ("00-foundation", "10-semantic", "20-component", "30-layout")}},
    }
    color = cats.get("color", [])
    slots = {
        "surface": {"categories": ["color"], "allowed": sorted(t for t in color if t.startswith("surface."))},
        "text": {"categories": ["color"], "allowed": sorted(t for t in color if t.startswith("text."))},
        "accent": {"categories": ["color"], "allowed": sorted(t for t in color if t.startswith("accent."))},
        "border": {"categories": ["color"], "allowed": sorted(t for t in color if t.startswith("border."))},
        "typography": {"categories": ["typography"], "allowed": sorted(cats.get("typography", []))},
        "radius": {"categories": ["radius"], "allowed": sorted(cats.get("radius", []))},
        "paddingTop": {"categories": ["layout"], "allowed": sorted(t for t in spacing if "PaddingTop" in t)},
        "paddingBottom": {"categories": ["layout"], "allowed": sorted(t for t in spacing if "PaddingBottom" in t)},
        "gap": {"categories": ["layout"], "allowed": sorted(t for t in spacing if "Gap" in t or "gutter" in t)},
        "fontFamily": {"categories": ["fontFamily"], "allowed": fonts, "note": "a family name from the catalog, not a token id"},
    }
    policy = {
        "version": VERSION,
        "generatedBy": "extraction/build_token_llm.py (derived from the token catalog; do not edit by hand)",
        "rawValuesAllowed": False,
        "rawValueRestrictions": {k: "forbidden" for k in sorted(cats)},
        "overrides": {
            "perInstance": "node.tokens only",
            "note": "A PageSpec node may carry an optional closed `tokens` object whose keys are the slots below and whose values are approved token ids (or, for fontFamily, a supported family name). Page-level `theme` must be a schema-validated theme. There is no free-form style field.",
        },
        "slots": slots,
        "themes": {k: {"file": v["file"], "mode": v["mode"]} for k, v in themes.items()},
        "rules": {
            "TOKEN_UNKNOWN": "a slot value that is not a token id in the catalog",
            "TOKEN_RAW_VALUE": "a raw colour (#hex, rgb(), rgba(), hsl(), hsla()) or other literal CSS value instead of a token id",
            "TOKEN_ARBITRARY_SPACING": "a spacing slot given a raw length (px/rem/em/%/vw/vh) or a foundation space.* token instead of an approved layout token",
            "TOKEN_UNSUPPORTED_FONT": "a fontFamily slot naming a family the catalog does not list",
            "TOKEN_NOT_REFERENCEABLE": "a foundation token id (catalogued but referenceable=false)",
            "TOKEN_SLOT_MISMATCH": "a real token used in a slot of the wrong category (e.g. a layout token as a surface colour)",
            "TOKEN_THEME_MISMATCH": "the page's theme is not schema-validated, or a colour/typography token is not resolved by that theme",
        },
        "enforcement": {"pageSpec": "schema/semantic_validate.py (rules above)", "catalogPolicyParity": "machine-checked by extraction/verify_all.py (rebuilds both files)"},
    }
    return catalog, policy


def dump(d):
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"


def main():
    cat, pol = build()
    pairs = [("tokens/llm/token-catalog.json", cat), ("tokens/llm/token-policy.json", pol)]
    if "--check" in sys.argv:
        bad = [p for p, d in pairs if open(os.path.join(REPO, p), encoding="utf-8").read() != dump(d)]
        print("token catalog/policy up to date" if not bad else f"stale: {bad}"); sys.exit(1 if bad else 0)
    for p, d in pairs:
        open(os.path.join(REPO, p), "w", encoding="utf-8").write(dump(d))
    print(f"token catalog: {cat['counts']['tokens']} tokens ({cat['counts']['referenceable']} referenceable); policy: {len(pol['slots'])} slots, {len(pol['rules'])} rules")


if __name__ == "__main__":
    main()
