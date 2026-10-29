#!/usr/bin/env python3
"""Semantic validator for a PageSpec against this design repo.

Enforces, in order:
  1. JSON Schema draft-07 (schema/pagespec.schema.json) -- structural closure, closed `mode`
  2. template cross-reference: the node sequence must follow the DECLARED template's own node list
     (order, required nodes present, repeatable/maxCount respected, no foreign sections)
  3. every rule in compatibility/graph.json, respecting severity (error fails, warn is reported)
  4. per-field maxWords budgets from sections/<id>.json, on this instance
  5. motion: pattern allowed for that section, reducedMotionFallback present
  6. images: assetRole allowed for that section (mode=clone: the section's assetRoles; mode=generation:
     its generatedAssetRoles) and, in generation mode, PINNED_AVAILABILITY (pinned HERE, not read from the registry)
  7. retrieval eligibility: RETRIEVAL_INELIGIBLE is pinned HERE; contracts and node echoes must agree
  8. tokens: node.tokens slots resolve to approved catalog tokens (TOKEN_* rules); page theme is schema-validated
  9. mode=generation only: GENERATION_MODE_BRAND / _PERSON / _CUSTOMER / _CLAIM / _COPY / _URL / _EMBED /
     _ASSET / _SCREENSHOT, patterns from schema/source-identity.json (built from the real source by
     extraction/build_source_identity.py). Detection is string-based after schema/textnorm.py normalisation.
     mode=clone may carry the source's real content (that is its purpose) and is not checked by these rules.

Usage:  python3 semantic_validate.py <pagespec.json>
Import: check(spec) -> (errors, warnings)
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from textnorm import normalize, shingles, stats, words as norm_words  # noqa: E402

RULE_KINDS = {"maxCategoryPerPage", "perPageLimits", "mustBeFirst", "mustBeLast", "noConsecutive",
              "noAdjacentSameCategory", "maxAnimatedSections"}

# Availability per asset role, pinned in code (cross-checked against assets/asset-roles.json by verify_all.py,
# which keeps its own copy of this table). Editing the registry alone cannot make a role usable in generation mode.
PINNED_AVAILABILITY = {
    "logo": "clone-only", "hero-image": "clone-only", "content-image": "clone-only", "animation": "clone-only",
    "video": "clone-only", "font": "clone-only",
    "customer-logo": "blocked-for-generation", "integration-logo": "blocked-for-generation",
    "compliance-badge": "blocked-for-generation", "credential-logo": "blocked-for-generation",
    "avatar": "blocked-for-generation", "live-embed": "blocked-for-generation", "founder-contact-email": "blocked-for-generation",
    "icon": "generation-safe", "illustration": "generation-safe", "background": "generation-safe",
    "placeholder-brand-mark": "generation-safe", "user-supplied-asset": "generation-safe", "generated-illustration": "generation-safe",
    "placeholder-screenshot": "generation-safe", "fictional-avatar": "generation-safe", "placeholder-company-logo": "generation-safe",
    "placeholder-url": "generation-safe", "original-copy": "generation-safe",
}
# which GENERATION_MODE_* rule a non-generation-safe role violates
ROLE_RULE = {"logo": "BRAND", "avatar": "PERSON", "customer-logo": "CUSTOMER", "integration-logo": "CUSTOMER", "credential-logo": "CUSTOMER",
             "hero-image": "SCREENSHOT", "content-image": "SCREENSHOT", "live-embed": "EMBED", "founder-contact-email": "URL"}
# Runtime/utility sections that must never be retrieved as content (pinned; verify_all.py holds the same table).
RETRIEVAL_INELIGIBLE = {"content.white"}
GENERATION_RULES = ["GENERATION_MODE_BRAND", "GENERATION_MODE_PERSON", "GENERATION_MODE_CUSTOMER", "GENERATION_MODE_CLAIM",
                    "GENERATION_MODE_COPY", "GENERATION_MODE_URL", "GENERATION_MODE_EMBED", "GENERATION_MODE_ASSET", "GENERATION_MODE_SCREENSHOT"]
RAW_COLOR = re.compile(r"^\s*(#[0-9a-f]{3,8}|rgba?\(|hsla?\(|hwb\(|lab\(|lch\(|oklch\(|color\()", re.I)
RAW_LENGTH = re.compile(r"^\s*-?\d*\.?\d+\s*(px|rem|em|%|vw|vh|svh|dvh|ch|pt)?\s*$", re.I)
SPACING_SLOTS = {"paddingTop", "paddingBottom", "gap"}
THEMED_SLOTS = {"surface", "text", "accent", "border", "typography"}

_CACHE = {}


def load(rel):
    # contracts are read once per process: the adversarial suite calls check() hundreds of times
    if rel not in _CACHE:
        with open(os.path.join(REPO, rel), encoding="utf-8") as f:
            _CACHE[rel] = json.load(f)
    return _CACHE[rel]


def words(s):
    return len(str(s).split())


def contracts():
    if "__sections__" in _CACHE:
        return _CACHE["__sections__"]
    out = {}
    d = os.path.join(REPO, "sections")
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            c = json.load(open(os.path.join(d, f), encoding="utf-8"))
            out[c["id"]] = c
    _CACHE["__sections__"] = out
    return out


def validator():
    if "__validator__" not in _CACHE:
        from jsonschema import Draft7Validator
        _CACHE["__validator__"] = Draft7Validator(load("schema/pagespec.schema.json"))
    return _CACHE["__validator__"]


def identity():
    """compiled generation-mode patterns from schema/source-identity.json"""
    if "__identity__" in _CACHE:
        return _CACHE["__identity__"]
    d = load("schema/source-identity.json")
    rx = lambda terms: re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True)) + r")", re.I) if terms else None
    brand_prefix = [b["term"] for b in d["brand"] if b["match"] == "word-prefix"]
    brand_sub = [b["term"] for b in d["brand"] if b["match"] == "substring"]
    people_full = [p["name"] for p in d["people"]]
    surnames = [p["surname"] for p in d["people"] if p.get("surname")]
    comp_ci = [c["name"] for c in d["companies"] if c["match"] == "word"]
    comp_cs = [c["display"] for c in d["companies"] if c["match"] == "word-case-sensitive"]
    ids = {
        "brand": re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(t) for t in brand_prefix) + r")|" + "|".join(re.escape(t) for t in brand_sub), re.I),
        "people": re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(t) for t in people_full + surnames) + r")(?![a-z0-9])", re.I),
        "comp_ci": re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(t) for t in comp_ci) + r")(?![a-z0-9])", re.I) if comp_ci else None,
        "comp_cs": re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(t) for t in comp_cs) + r")(?![A-Za-z0-9])") if comp_cs else None,
        "hosts": [x["host"] for x in d["domains"]],
        "emails": [x["address"] for x in d["emails"]],
        "embeds": [normalize(e) for e in d["embeds"]],
        "stats": {s["token"] for s in d["stats"]},
        "copy": set(d["copy"]["shingles"]),
        "asset_paths": set(d["assets"]["paths"]) | {os.path.basename(p) for p in d["assets"]["paths"]},
        "asset_ids": [c.lower() for c in d["assets"]["contentIds"]],
        "asset_sha": set(d["assets"]["inlineSha256"]),
        "placeholder": tuple(d["placeholderDomains"]),
    }
    _CACHE["__identity__"] = ids
    return ids


def strings(o, path=""):
    """every (path, string) in a PageSpec, keys excluded except where they carry content"""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from strings(v, f"{path}/{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f"{path}/{i}")
    elif isinstance(o, str):
        yield path, o


STRUCTURAL = re.compile(r"^(pageSpecVersion|mode|template|theme|nodes/\d+/(type|motion/.*|tokens/.*)|nodes/\d+/content/images/\d+/assetRole)$")


def generation_checks(spec, errors):
    ids = identity()
    seen = set()

    def err(rule, where, msg):
        key = (rule, where)
        if key not in seen:
            seen.add(key); errors.append(f"{rule}: {where}: {msg}")
    for where, s in strings(spec):
        if STRUCTURAL.match(where):
            continue
        n = normalize(s)
        despaced = re.sub(r"[\s\-_.]+", "", n)
        m = ids["brand"].search(n) or ids["brand"].search(despaced)
        if m: err("GENERATION_MODE_BRAND", where, f"source brand '{m.group(0)}'")
        m = ids["people"].search(n)
        if m: err("GENERATION_MODE_PERSON", where, f"real person '{m.group(0)}'")
        m = (ids["comp_ci"] and ids["comp_ci"].search(n)) or (ids["comp_cs"] and ids["comp_cs"].search(normalize_case(s)))
        if m: err("GENERATION_MODE_CUSTOMER", where, f"real third-party company '{m.group(0)}'")
        st = stats(s) & ids["stats"]
        if st: err("GENERATION_MODE_CLAIM", where, f"source statistic {sorted(st)}")
        hit = shingles(s) & ids["copy"]
        if hit: err("GENERATION_MODE_COPY", where, f"{len(hit)} 5-word run(s) copied from the source")
        for e in ids["embeds"]:
            if e in n: err("GENERATION_MODE_EMBED", where, f"live embed endpoint '{e}'")
        for u in re.findall(r"(?:https?://|//|www\.)[^\s\"'<>]+|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|(?<![\w/@.-])(?:[a-z0-9-]+\.)+(?:com|app|io|net|org|co|ai|dev|so|us|uk|eu|de|xyz|example|invalid)(?![a-z0-9])(?:/[^\s]*)?", n):
            host = re.sub(r"^(https?:)?//", "", u).split("/")[0].split("@")[-1].removeprefix("www.")
            if any(host == h or host.endswith("." + h) for h in ids["hosts"]) or any(e in u for e in ids["emails"]):
                err("GENERATION_MODE_URL", where, f"source URL/address '{u}'")
            elif re.search(r"[a-z]", host.split(".")[-1]) and not host.endswith(ids["placeholder"]) and "." in host and not re.fullmatch(r"[\d.]+", host):
                err("GENERATION_MODE_URL", where, f"'{u}' is not on a reserved placeholder domain ({', '.join(ids['placeholder'])})")
        if where.endswith("/assetRef") or where.endswith("/href"):
            low = s.lower()
            if s in ids["asset_paths"] or s.lstrip("/") in ids["asset_paths"] or any(i in low for i in ids["asset_ids"]) or s.split(":")[-1] in ids["asset_sha"]:
                err("GENERATION_MODE_ASSET", where, f"reuses a registered source asset '{s}'")


def normalize_case(s):
    """normalisation without lower-casing, for case-sensitive company acronyms (SAP, BCG, Sage ...)"""
    from textnorm import ZERO_WIDTH, QUOTES, DASHES
    import unicodedata
    return DASHES.sub("-", ZERO_WIDTH.sub("", unicodedata.normalize("NFKC", str(s))).translate(QUOTES))


def token_checks(spec, nodes, errors):
    cat = load("tokens/llm/token-catalog.json")
    pol = load("tokens/llm/token-policy.json")
    man = load("registry.manifest.json")
    theme = spec.get("theme", man.get("defaultTheme"))
    if theme not in man.get("schemaValidatedThemes", []):
        errors.append(f"TOKEN_THEME_MISMATCH: theme '{theme}' is not a schema-validated theme ({', '.join(man.get('schemaValidatedThemes', []))})")
        resolved = set()
    else:
        resolved = set(cat["themes"].get(theme, {}).get("resolves", []))
    toks = cat["tokens"]
    for k, nd in enumerate(nodes):
        t = nd.get("tokens")
        if not isinstance(t, dict):
            continue
        for slot, val in t.items():
            where = f"node {k + 1} ({nd.get('type')}).tokens.{slot}"
            rule = pol["slots"].get(slot)
            if rule is None or not isinstance(val, str):
                continue  # the schema already rejects unknown slots / non-strings
            if slot == "fontFamily":
                if val not in rule["allowed"]:
                    errors.append(f"TOKEN_UNSUPPORTED_FONT: {where}: '{val}' is not a supported family ({', '.join(rule['allowed'])})")
                continue
            if RAW_COLOR.match(val):
                errors.append(f"TOKEN_RAW_VALUE: {where}: raw colour '{val}' (use a token id)"); continue
            if slot in SPACING_SLOTS and (RAW_LENGTH.match(val) or val.startswith("space.")):
                errors.append(f"TOKEN_ARBITRARY_SPACING: {where}: '{val}' is not an approved layout spacing token"); continue
            if val not in toks:
                errors.append(f"TOKEN_UNKNOWN: {where}: '{val}' is not in tokens/llm/token-catalog.json"); continue
            if not toks[val]["referenceable"]:
                errors.append(f"TOKEN_NOT_REFERENCEABLE: {where}: '{val}' is a foundation token"); continue
            if val not in rule["allowed"]:
                errors.append(f"TOKEN_SLOT_MISMATCH: {where}: '{val}' ({toks[val]['category']}) is not allowed in slot '{slot}'"); continue
            if slot in THEMED_SLOTS and resolved and val not in resolved:
                errors.append(f"TOKEN_THEME_MISMATCH: {where}: '{val}' is not resolved by theme '{theme}'")


def check(spec):
    errors, warnings = [], []
    # ---- 1. schema
    try:
        v = validator()
    except ImportError:
        return ["jsonschema is required (pip install jsonschema)"], []
    for e in sorted(v.iter_errors(spec), key=lambda e: [str(p) for p in e.absolute_path]):
        loc = "/".join(str(p) for p in e.absolute_path) or "(root)"
        errors.append(f"schema: {loc}: {e.message}")
    if not isinstance(spec, dict) or not isinstance(spec.get("nodes"), list):
        return errors or ["schema: nodes must be a list"], warnings
    nodes = [n for n in spec["nodes"] if isinstance(n, dict)]
    types = [n.get("type") for n in nodes]
    secs = contracts()
    templates = {t["id"]: t for t in load("templates/templates.json")["templates"]}
    mode = spec.get("mode")

    # ---- 2. declared template cross-reference
    tid = spec.get("template")
    t = templates.get(tid)
    if t:
        i = 0
        tsecs = [tn["section"] for tn in t["nodes"]]
        for k, tn in enumerate(t["nodes"]):
            cnt = 0
            while i < len(types) and types[i] == tn["section"]:
                cnt += 1; i += 1
            if cnt == 0 and tn.get("required"):
                if tn["section"] in types:
                    errors.append(f"template: section '{tn['section']}' is out of order for {tid} (expected as node {k + 1})")
                else:
                    errors.append(f"template: required section '{tn['section']}' missing (node {k + 1} of {tid})")
            if cnt > 1 and not tn.get("repeatable"):
                errors.append(f"template: section '{tn['section']}' repeated {cnt}x but is not repeatable in {tid}")
            if tn.get("repeatable") and cnt > tn.get("maxCount", cnt):
                errors.append(f"template: section '{tn['section']}' repeated {cnt}x, max {tn['maxCount']} in {tid}")
        for extra in types[i:]:
            if extra in tsecs:
                errors.append(f"template: section '{extra}' is out of order for {tid}")
            else:
                errors.append(f"template: section '{extra}' is not part of template {tid}")
            break

    # ---- 3. compatibility graph (severity-aware)
    cat = {sid: c["category"] for sid, c in secs.items()}
    for rule in load("compatibility/graph.json")["rules"]:
        kind, rid = rule.get("kind"), rule.get("id")
        sink = errors if rule.get("severity") == "error" else warnings
        tag = f"{rid} ({rule.get('severity')})"
        if kind not in RULE_KINDS:
            errors.append(f"graph: rule {rid} has kind '{kind}' that this validator does not implement")
            continue
        if kind == "maxCategoryPerPage":
            n = sum(1 for s in types if cat.get(s) == rule["category"])
            if n > rule["max"] and tid not in rule.get("exceptions", []):
                sink.append(f"{tag}: {n} {rule['category']} sections on one page (max {rule['max']})")
        elif kind == "perPageLimits":
            for s, lim in rule["limits"].items():
                n = types.count(s)
                if n > lim:
                    sink.append(f"{tag}: '{s}' appears {n}x (limit {lim})")
        elif kind == "mustBeFirst":
            for s in rule["sections"]:
                if s in types and types[0] != s:
                    sink.append(f"{tag}: '{s}' must be the first node")
        elif kind == "mustBeLast":
            for s in rule["sections"]:
                if s in types and types[-1] != s:
                    sink.append(f"{tag}: '{s}' must be the last node")
        elif kind == "noConsecutive":
            for a, b in zip(types, types[1:]):
                if a == b and a in rule["sections"]:
                    sink.append(f"{tag}: '{a}' appears twice in a row")
        elif kind == "noAdjacentSameCategory":
            allowed = {tuple(p) for p in rule.get("exceptions", [])}
            for a, b in zip(types, types[1:]):
                if a != b and a in cat and cat.get(a) == cat.get(b) and (a, b) not in allowed:
                    sink.append(f"{tag}: '{a}' and '{b}' are both {cat[a]} and adjacent")
        elif kind == "maxAnimatedSections":
            n = sum(1 for nd in nodes if isinstance(nd.get("motion"), dict) and nd["motion"].get("pattern") not in (None, "none"))
            if n > rule["max"]:
                sink.append(f"{tag}: {n} animated sections (max {rule['max']})")

    # ---- 4-7. per-node content budgets, motion, asset roles, retrieval eligibility
    for k, nd in enumerate(nodes):
        c = secs.get(nd.get("type"))
        if not c:
            continue
        sid = c["id"]
        f = c["content"]["fields"]
        content = nd.get("content") if isinstance(nd.get("content"), dict) else {}
        where = f"node {k + 1} ({nd.get('type')})"
        for key in ("heading", "subheading"):
            if key in content and key in f and words(content[key]) > f[key]["maxWords"]:
                errors.append(f"maxWords: {where}.{key} has {words(content[key])} words (max {f[key]['maxWords']})")
        if "body" in content and "body" in f and isinstance(content["body"], list):
            for j, p in enumerate(content["body"]):
                if words(p) > f["body"]["maxWords"]:
                    errors.append(f"maxWords: {where}.body[{j}] has {words(p)} words (max {f['body']['maxWords']})")
        if "ctas" in content and "ctas" in f and isinstance(content["ctas"], list):
            for j, cta in enumerate(content["ctas"]):
                if isinstance(cta, dict) and words(cta.get("label", "")) > f["ctas"]["maxWords"]:
                    errors.append(f"maxWords: {where}.ctas[{j}].label has {words(cta['label'])} words (max {f['ctas']['maxWords']})")
        if "items" in content and "items" in f and isinstance(content["items"], list):
            for j, it in enumerate(content["items"]):
                if not isinstance(it, dict): continue
                if words(it.get("title", "")) > f["items"]["titleMaxWords"]:
                    errors.append(f"maxWords: {where}.items[{j}].title has {words(it['title'])} words (max {f['items']['titleMaxWords']})")
                if "body" in it and words(it["body"]) > f["items"].get("bodyMaxWords", 0):
                    errors.append(f"maxWords: {where}.items[{j}].body has {words(it['body'])} words (max {f['items'].get('bodyMaxWords', 0)})")
        m = nd.get("motion")
        if not isinstance(m, dict) or not m.get("reducedMotionFallback"):
            errors.append(f"motion: {where} has no reducedMotionFallback")
        elif m.get("pattern") not in c["motion"]["allowedPatterns"]:
            errors.append(f"motion: {where} pattern '{m.get('pattern')}' not allowed (allowed: {', '.join(c['motion']['allowedPatterns'])})")
        roles = (c.get("generatedAssetRoles") if mode == "generation" else f.get("images", {}).get("assetRoles")) or []
        for j, img in enumerate(content.get("images", []) if isinstance(content.get("images"), list) else []):
            if not isinstance(img, dict):
                continue
            r = img.get("assetRole")
            if "alt" in img and words(img["alt"]) > 16:
                errors.append(f"maxWords: {where}.images[{j}].alt has {words(img['alt'])} words (max 16)")
            if mode == "generation" and r in PINNED_AVAILABILITY and PINNED_AVAILABILITY[r] != "generation-safe":
                rule = ROLE_RULE.get(r, "ASSET")
                errors.append(f"GENERATION_MODE_{rule}: {where}.images[{j}] role '{r}' is {PINNED_AVAILABILITY[r]} (pinned); use a generation-safe substitute")
            elif mode == "generation" and r not in PINNED_AVAILABILITY:
                errors.append(f"GENERATION_MODE_ASSET: {where}.images[{j}] role '{r}' has no pinned availability")
            if roles and r not in roles:
                errors.append(f"assetRole: {where}.images[{j}] role '{r}' not used by this section (allowed: {', '.join(roles)})")
            elif not roles and mode == "generation":
                errors.append(f"assetRole: {where}.images[{j}] role '{r}' not used by this section in generation mode (no generatedAssetRoles)")
        # retrieval eligibility: the pin is authoritative; the contract and any node echo must agree with it
        pinned_ok = sid not in RETRIEVAL_INELIGIBLE
        if c.get("retrievalEligible", True) != pinned_ok:
            errors.append(f"RETRIEVAL_PIN: sections/{sid}.json retrievalEligible={c.get('retrievalEligible', True)} but the pinned value is {pinned_ok}")
        if "retrievalEligible" in nd and nd["retrievalEligible"] != pinned_ok:
            errors.append(f"RETRIEVAL_PIN: {where} declares retrievalEligible={nd['retrievalEligible']} but '{sid}' is pinned {'eligible' if pinned_ok else 'ineligible'}")

    # ---- 8. tokens
    token_checks(spec, nodes, errors)
    # ---- 9. generation-mode leakage
    if mode == "generation":
        generation_checks(spec, errors)
    return errors, warnings


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: semantic_validate.py <pagespec.json>")
    errors, warnings = check(json.load(open(sys.argv[1], encoding="utf-8")))
    for w in warnings:
        print("WARN:", w)
    if errors:
        print("INVALID:"); [print("  -", e) for e in errors]; sys.exit(1)
    print("VALID"); sys.exit(0)


if __name__ == "__main__":
    main()
