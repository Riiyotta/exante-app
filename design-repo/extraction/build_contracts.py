#!/usr/bin/env python3
"""Regenerate every DERIVED contract file from the authored ones, so they cannot drift apart.

Authored (edit these): sections/*.json (content fields, category, purpose, retrievalEligible, assetRoles),
templates/templates.json, assets/asset-roles.json, motion/motion-contract.json, tokens/**.
Derived (written here):
  sections/*.json        constraints (onePerPage/maxPerPage/mustBeFirst/mustBeLast), semantic.category,
                         generatedAssetRoles (generation-safe roles + substitutes of the section's roles)
  compatibility/graph.json   per-page limits, SHELL first/last lists, ONE_HERO exceptions, observed same-category pairs
  tokens/llm/component-allowlist.json   sections, contentFields, retrievalIneligible, generatedAssetRoles
  schema/pagespec.schema.json           the whole draft-07 PageSpec schema

verify_all.py re-runs build() and fails when any derived file on disk differs (drift is caught, not trusted).
Usage: python3 design-repo/extraction/build_contracts.py [--check]
"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PAGESPEC_VERSION = "0.2.0"
HREF_PATTERN = r"^(/|#|https://([a-z0-9-]+\.)+(example|invalid)(/|$)|mailto:[^@\s]+@([a-z0-9-]+\.)+(example|invalid)$)"
TOKEN_SLOTS = ["surface", "text", "accent", "border", "typography", "radius", "paddingTop", "paddingBottom", "gap", "fontFamily"]


def J(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


def dump(d):
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"


def sections():
    d = os.path.join(REPO, "sections")
    return {json.load(open(os.path.join(d, f), encoding="utf-8"))["id"]: (f, json.load(open(os.path.join(d, f), encoding="utf-8")))
            for f in sorted(os.listdir(d)) if f.endswith(".json")}


def content_def(fields):
    props, req = {}, []
    for k, f in fields.items():
        t = f["type"]
        if t == "string":
            props[k] = {"type": "string", "minLength": 1, "maxWords": f["maxWords"]}
        elif t == "string[]":
            props[k] = {"type": "array", "maxItems": f["maxItems"], "items": {"type": "string", "minLength": 1, "maxWords": f["maxWords"]}}
        elif t == "cta[]":
            props[k] = {"type": "array", "maxItems": f["maxItems"], "items": {"type": "object", "required": ["label"], "additionalProperties": False, "properties": {
                "label": {"type": "string", "minLength": 1, "maxWords": f["maxWords"]},
                "href": {"type": "string", "pattern": HREF_PATTERN,
                         "description": "Relative path, #anchor, or a placeholder URL on a reserved .example/.invalid domain only: pages must not link to the source site's live URLs."}}}}
        elif t == "item[]":
            ip = {"title": {"type": "string", "minLength": 1, "maxWords": f["titleMaxWords"]}}
            if "bodyMaxWords" in f:
                ip["body"] = {"type": "string", "maxWords": f["bodyMaxWords"]}
            props[k] = {"type": "array", "maxItems": f["maxItems"], "items": {"type": "object", "required": ["title"], "additionalProperties": False, "properties": ip}}
        elif t == "image[]":
            props[k] = {"type": "array", "maxItems": f["maxItems"], "items": {"type": "object", "required": ["assetRole"], "additionalProperties": False, "properties": {
                "assetRole": {"$ref": "#/definitions/assetRole"},
                "assetRef": {"type": "string", "minLength": 1, "description": "Optional pointer to the file: a registered asset path (mode=clone only) or placeholder:/generated:/user-supplied:<id>."},
                "alt": {"type": "string", "maxWords": 16}}}}
        else:
            raise SystemExit(f"unknown field type {t}")
        if f.get("required"):
            req.append(k)
    d = {"type": "object", "additionalProperties": False, "properties": props}
    if req:
        d["required"] = req
    return d


def build():
    secs = sections()
    tdoc = J("templates/templates.json"); templates = tdoc["templates"]
    assets = J("assets/asset-roles.json"); roles = assets["roles"]
    motion = J("motion/motion-contract.json")
    man = J("registry.manifest.json")
    safe = sorted(r for r, v in roles.items() if v.get("availability") == "generation-safe")
    out = {}
    # ---- sections: constraints from templates, generatedAssetRoles from the role registry
    for sid, (f, c) in secs.items():
        c = copy.deepcopy(c)
        tm = [t for t in templates if any(n["section"] == sid for n in t["nodes"])]
        mx = max((sum((n.get("maxCount", 1) if n["repeatable"] else 1) for n in t["nodes"] if n["section"] == sid) for t in tm), default=0)
        cons = {"onePerPage": True} if mx == 1 else {"maxPerPage": mx}
        if c["category"] == "SHELL" and tm and all(t["nodes"][0]["section"] == sid for t in tm): cons["mustBeFirst"] = True
        if c["category"] == "SHELL" and tm and all(t["nodes"][-1]["section"] == sid for t in tm): cons["mustBeLast"] = True
        c["constraints"] = cons
        c["semantic"] = {"id": sid, "category": c["category"]}
        img = c["content"]["fields"].get("images")
        if img:
            gen = set()
            for r in img.get("assetRoles", []):
                if roles[r].get("availability") == "generation-safe": gen.add(r)
                gen |= set(roles[r].get("generationSafeSubstitutes", []))
            c["generatedAssetRoles"] = sorted(gen)
        else:
            c["generatedAssetRoles"] = []
        out[f"sections/{f}"] = c
    S = {c["id"]: c for c in (out[k] for k in out)}
    # ---- graph
    graph = J("compatibility/graph.json")
    rules = {r["id"]: r for r in graph["rules"]}
    rules["SECTION_PER_PAGE_LIMITS"]["limits"] = {sid: (1 if c["constraints"].get("onePerPage") else c["constraints"]["maxPerPage"]) for sid, c in sorted(S.items())}
    rules["SHELL_MUST_BE_FIRST"]["sections"] = sorted(s for s, c in S.items() if c["constraints"].get("mustBeFirst"))
    rules["SHELL_MUST_BE_LAST"]["sections"] = sorted(s for s, c in S.items() if c["constraints"].get("mustBeLast"))
    rules["NO_CONSECUTIVE_SAME_SECTION"]["sections"] = sorted(s for s, c in S.items() if c["constraints"].get("noConsecutive"))
    rules["ONE_HERO_PER_PAGE"]["exceptions"] = sorted(t["id"] for t in templates if sum((n.get("maxCount") or 1) if n.get("repeatable") else 1
                                                                                  for n in t["nodes"] if S[n["section"]]["category"] == "HERO") > 1)
    pairs = []
    for t in templates:
        seq = [n["section"] for n in t["nodes"]]
        for a, b in zip(seq, seq[1:]):
            if a != b and S[a]["category"] == S[b]["category"] and [a, b] not in pairs: pairs.append([a, b])
    rules["NO_ADJACENT_SAME_CATEGORY"]["exceptions"] = pairs
    graph["rules"] = [rules[r["id"]] for r in graph["rules"]]
    graph["version"] = "0.2.0"
    out["compatibility/graph.json"] = graph
    # ---- allowlist
    allow = J("tokens/llm/component-allowlist.json")
    allow["sections"] = sorted(S)
    allow["contentFields"] = {sid: sorted(c["content"]["fields"]) for sid, c in sorted(S.items())}
    allow["retrievalIneligible"] = sorted(sid for sid, c in S.items() if c.get("retrievalEligible") is False)
    allow["generatedAssetRoles"] = {sid: c["generatedAssetRoles"] for sid, c in sorted(S.items()) if c["generatedAssetRoles"]}
    allow["nodeProperties"] = ["content", "motion", "retrievalEligible", "tokens", "type"]
    out["tokens/llm/component-allowlist.json"] = allow
    # ---- schema
    node_props = {
        "type": {"type": "string", "enum": sorted(S)},
        "content": {"type": "object"},
        "motion": {"$ref": "#/definitions/motion"},
        "retrievalEligible": {"type": "boolean", "description": "Optional echo of the section contract's retrieval eligibility; must agree with it (pinned in the validators)."},
        "tokens": {"$ref": "#/definitions/tokenRefs"},
    }
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "PageSpec",
        "description": ("A page composition. mode=clone reconstructs the source (real copy/assets allowed as evidence); mode=generation builds a new "
                        "page for another brand and is checked by the GENERATION_MODE_* rules in schema/semantic_validate.py. Styling is owned by "
                        "the section/component contracts; the only style input is the closed node.tokens slot map (approved token ids)."),
        "type": "object",
        "required": ["pageSpecVersion", "mode", "template", "route", "nodes"],
        "additionalProperties": False,
        "properties": {
            "pageSpecVersion": {"type": "string", "const": PAGESPEC_VERSION},
            "mode": {"type": "string", "enum": ["clone", "generation"], "description": "clone = faithful reconstruction of the source; generation = a new page that must not contain the source's identity or content."},
            "template": {"type": "string", "enum": [t["id"] for t in templates]},
            "route": {"type": "string", "pattern": "^/"},
            "theme": {"type": "string", "enum": man["schemaValidatedThemes"]},
            "nodes": {"type": "array", "minItems": 1, "items": {"$ref": "#/definitions/node"}},
        },
        "definitions": {
            "assetRole": {"type": "string", "enum": sorted(roles)},
            "motion": {"type": "object", "required": ["pattern", "reducedMotionFallback"], "additionalProperties": False, "properties": {
                "pattern": {"type": "string", "enum": list(motion["patterns"])},
                "reducedMotionFallback": {"type": "string", "enum": motion["reducedMotionFallbacks"]}}},
            "tokenRefs": {"type": "object", "additionalProperties": False, "minProperties": 1,
                          "properties": {s: {"type": "string", "minLength": 1} for s in TOKEN_SLOTS},
                          "description": "Slot -> approved token id (tokens/llm/token-policy.json slots). Values are checked by the TOKEN_* rules in the semantic validator."},
            "node": {"type": "object", "required": ["type", "content", "motion"], "additionalProperties": False, "properties": node_props,
                     "allOf": [{"if": {"properties": {"type": {"const": sid}}, "required": ["type"]},
                                "then": {"properties": {"content": {"$ref": f"#/definitions/content.{sid}"}}}} for sid in sorted(S)]},
        },
    }
    for sid, c in sorted(S.items()):
        schema["definitions"][f"content.{sid}"] = content_def(c["content"]["fields"])
    out["schema/pagespec.schema.json"] = schema
    return out


def main():
    out = build()
    stale = [p for p, d in out.items() if open(os.path.join(REPO, p), encoding="utf-8").read() != dump(d)]
    if "--check" in sys.argv:
        print("derived contracts up to date" if not stale else f"derived contracts differ from the authored ones: {stale[:5]}"); sys.exit(1 if stale else 0)
    for p in stale:
        open(os.path.join(REPO, p), "w", encoding="utf-8").write(dump(out[p]))
    print(f"derived contracts rebuilt ({len(stale)} file(s) changed of {len(out)})")


if __name__ == "__main__":
    main()
