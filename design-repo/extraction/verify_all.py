#!/usr/bin/env python3
"""Admission check for this design repo. Exit 0 = admitted.

  1  required files exist and parse
  2  manifest fields (incl. category + designPolicy binding); entryPoints relative, inside design-repo/, present
  3  allowlistVersion / pageSpecVersion match their sources (machine-checked version fields)
  4  counts recomputed from the files on disk (manifest AND README)
  5  allowlist parity; section contracts validate against schema/section-contract.schema.json; R7 source/semantic
     split; R8 retrieval pin (RETRIEVAL_INELIGIBLE here == semantic_validate's == contracts == allowlist)
  6  derived files equal what extraction/build_contracts.py and build_token_llm.py generate (no drift)
  7  templates: every node has a contract; routes assigned exactly once and every route in src/routes.js mapped;
     every template family has a mode=generation example that validates; the clone example validates
  8  constraints + graph recomputed from templates (a rule in prose and in code must agree)
  9  citations, resolved against the runnable clone's own source at the package root (src/, tracked in git):
     every ledger range is in range, its first line holds the cited tag and anchor, the page's usage line renders
     that component, and each contract's `source` range holds its tag. When design-repo/ is copied alone (no
     ../src) this degrades to one warning; the ledger and source-identity registry are also rebuilt and compared
     whenever src/ is present.
 10  tokens: every {reference} resolves; theme resolves every semantic token; catalog/policy regenerated equal
 11  assets: closed role vocabulary; PINNED policies and PINNED_AVAILABILITY hold (here AND in the validator AND in
     the registry); files exist under ../public/ (or are flagged inClone=false and really absent); inline marks
     hash to their recorded sha256
 12  motion closed to the contract's fields; section patterns inside the contract
 13  no absolute machine paths in any JSON/MD/PY/MJS file
 14  schema valid draft-07; examples validate; adversarial suite passes
 15  wrapper gate (extraction/wrapper_gate.py): measured 1440px heights, HERO/page-share thresholds
 16  design-policy binding: policy file exists, ids/versions agree, contentHash matches the enforcedBy files
 17  zip hygiene, only if ../design-repo.zip exists

ir/ at the package root is deliberately NOT read: the IR was left untouched by request and is stale against
this release (see CHANGELOG). Drift-proofing lives in extraction/prove_drift.py.
"""
import glob, hashlib, importlib.util, json, os, re, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG = os.path.dirname(REPO)
SRC, PUB = os.path.join(PKG, "src"), os.path.join(PKG, "public")
errs, warns = [], []
EVIDENCE = os.path.isdir(SRC) and os.path.isfile(os.path.join(SRC, "routes.js"))
sys.path.insert(0, HERE)

# Pinned generation (clone-mode reuse) policies, independent of assets/asset-roles.json.
PINNED = {"logo": "must-reuse-exact", "customer-logo": "must-not-fabricate", "integration-logo": "must-not-fabricate",
          "compliance-badge": "must-not-fabricate", "credential-logo": "must-not-fabricate", "avatar": "must-not-fabricate",
          "font": "must-reuse-exact", "live-embed": "must-not-reuse-live-endpoint",
          "founder-contact-email": "must-not-reuse-live-endpoint", "user-supplied-asset": "must-reuse-exact"}
# Pinned availability (mode=generation), independent of the registry; semantic_validate.py holds the same table.
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
REQUIRED_GENERATION_SAFE = ["placeholder-brand-mark", "user-supplied-asset", "generated-illustration", "placeholder-screenshot",
                            "fictional-avatar", "placeholder-company-logo", "placeholder-url", "original-copy"]
# Runtime/utility sections that are never retrievable (semantic_validate.py holds the same pin).
RETRIEVAL_INELIGIBLE = {"content.white"}
RUNTIME_UI = re.compile(r"cookie|consent|modal|dialog|drawer|pop-?up|preloader|loader|toast|background layer|cursor", re.I)

REQUIRED = ["registry.manifest.json", "README.md", "CHANGELOG.md", "tokens/themes/light.json",
            "tokens/llm/token-catalog.json", "tokens/llm/token-policy.json", "tokens/llm/component-allowlist.json",
            "templates/templates.json", "compatibility/graph.json", "assets/asset-roles.json", "motion/motion-contract.json",
            "schema/pagespec.schema.json", "schema/section-contract.schema.json", "schema/example.pagespec.json",
            "schema/semantic_validate.py", "schema/textnorm.py", "schema/source-identity.json", "schema/tests/adversarial_test.py",
            "extraction/measured-values.json", "extraction/prove_drift.py", "extraction/wrapper_gate.py", "extraction/wrapper-whitelist.json",
            "extraction/build_contracts.py", "extraction/build_token_llm.py", "extraction/build_ledger.py",
            "extraction/build_source_identity.py", "extraction/policy_hash.py", "policy/design-policy.json"]
ENTRY_KEYS = ["tokenCatalog", "tokenPolicy", "componentAllowlist", "compatibilityGraph", "assetContract", "motionContract",
              "templates", "pagespecSchema", "examplePageSpec", "semanticValidate", "adversarialSuite", "admission",
              "driftProof", "measuredValues", "defaultTheme", "sectionContractSchema", "sourceIdentity", "wrapperGate",
              "wrapperWhitelist", "designPolicy"]


def J(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


def files_in(d, ext=".json"):
    p = os.path.join(REPO, d)
    return sorted(f for f in os.listdir(p) if f.endswith(ext)) if os.path.isdir(p) else []


def tokens_in(tier):
    out = {}
    for f in files_in(os.path.join("tokens", tier)):
        out.update(J(os.path.join("tokens", tier, f)).get("tokens", {}))
    return out


def mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def dump(d):
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"


def main():
    # 1
    for rel in REQUIRED:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p): errs.append(f"missing: {rel}")
        elif rel.endswith(".json"):
            try: J(rel)
            except Exception as e: errs.append(f"bad json {rel}: {e}")
    for d in ("tokens/00-foundation", "tokens/10-semantic", "tokens/20-component", "tokens/30-layout", "sections", "primitives", "components", "schema/examples"):
        if not os.path.isdir(os.path.join(REPO, d)): errs.append(f"missing folder: {d}/")
    if errs: return finish()
    man = J("registry.manifest.json")
    allow = J("tokens/llm/component-allowlist.json")
    schema = J("schema/pagespec.schema.json")
    templates = J("templates/templates.json")["templates"]
    graph = J("compatibility/graph.json")
    assets = J("assets/asset-roles.json")
    ledger = J("extraction/measured-values.json")
    if not EVIDENCE:
        warns.append("design-repo/ is copied alone (no ../src/routes.js): citations, asset files, ledger and source-identity rebuilds are not checked here; run verify_all.py inside a git clone of the package to admit fully")
    secs = {}
    for f in files_in("sections"):
        c = J(f"sections/{f}")
        if c.get("id") + ".json" != f: errs.append(f"sections/{f}: id '{c.get('id')}' does not match its file name")
        secs[c["id"]] = c
    sv = mod("semantic_validate", "schema/semantic_validate.py")

    # 2
    for k in ("repositoryId", "status", "productionApproved", "defaultTheme", "schemaValidatedThemes", "allowlistVersion", "versionFieldNote",
              "counts", "entryPoints", "category", "designPolicy"):
        if k not in man: errs.append(f"manifest: missing field {k}")
    eps = man.get("entryPoints", {})
    for k in ENTRY_KEYS:
        if k not in eps: errs.append(f"entryPoints.{k} is not wired in")
    for k, v in eps.items():
        if not isinstance(v, str) or os.path.isabs(v) or v.startswith("..") or "/../" in v or re.match(r"^[A-Za-z]:", v):
            errs.append(f"entryPoints.{k} must be a relative path inside design-repo/, got {v!r}")
        elif not os.path.exists(os.path.join(REPO, v)):
            errs.append(f"entryPoints.{k} points at a missing file: {v}")

    # 3
    if man.get("allowlistVersion") != allow.get("version"):
        errs.append(f"allowlistVersion drift: manifest {man.get('allowlistVersion')!r} vs allowlist {allow.get('version')!r}")
    if man.get("pageSpecVersion") != schema["properties"]["pageSpecVersion"].get("const"):
        errs.append(f"pageSpecVersion drift: manifest {man.get('pageSpecVersion')!r} vs schema const {schema['properties']['pageSpecVersion'].get('const')!r}")

    # 4
    F, S, L = tokens_in("00-foundation"), tokens_in("10-semantic"), tokens_in("30-layout")
    C = {}
    for f in files_in("tokens/20-component"):
        d = J(f"tokens/20-component/{f}")
        C.update({f"{d['component']}.{k}": v for k, v in d.get("tokens", {}).items()})
    actual = {"sections": len(secs), "templates": len(templates), "routes": sum(t["routeCount"] for t in templates),
              "primitives": len(files_in("primitives")), "components": len(files_in("components")), "assets": len(assets.get("assets", [])),
              "themes": len(files_in("tokens/themes")), "rules": len(graph.get("rules", [])),
              "tokens": {"foundation": len(F), "semantic": len(S), "component": len(C), "layout": len(L)}}
    mc = man.get("counts", {})
    for k, v in actual.items():
        if mc.get(k) != v: errs.append(f"manifest counts.{k} = {mc.get(k)} but the files give {v}")
    readme = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    gen_examples = sorted(glob.glob(os.path.join(REPO, "schema", "examples", "*.pagespec.json")))
    for label, v in [("Sections", actual["sections"]), ("Templates", actual["templates"]), ("Routes", actual["routes"]),
                     ("Primitives", actual["primitives"]), ("Components", actual["components"]), ("Assets", actual["assets"]),
                     ("Asset roles", len(assets["roles"])), ("Foundation tokens", len(F)), ("Semantic tokens", len(S)),
                     ("Rules", actual["rules"]), ("Generation examples", len(gen_examples))]:
        m = re.search(rf"^- {label}: (\d+)$", readme, re.M)
        if not m or int(m.group(1)) != v: errs.append(f"README count '{label}' is {m.group(1) if m else 'missing'} but the files give {v}")

    # 5
    for key, found in [("sections", sorted(secs)), ("primitives", [f[:-5] for f in files_in("primitives")]), ("components", [f[:-5] for f in files_in("components")])]:
        a = set(allow.get(key, []))
        for x in sorted(a - set(found)): errs.append(f"allowlist parity: '{x}' in allowlist.{key} has no contract file")
        for x in sorted(set(found) - a): errs.append(f"allowlist parity: {key}/{x}.json has no allowlist entry")
    node_props = set(schema["definitions"]["node"]["properties"])
    if set(allow.get("nodeProperties", [])) != node_props:
        errs.append(f"allowlist.nodeProperties {sorted(allow.get('nodeProperties', []))} != schema node properties {sorted(node_props)}")
    from jsonschema import Draft7Validator
    cv = Draft7Validator(J("schema/section-contract.schema.json"))
    for sid, c in secs.items():
        for e in cv.iter_errors(c):
            errs.append(f"sections/{sid}.json violates section-contract.schema.json at {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:120]}")
        sem, src = c.get("semantic", {}), c.get("source", {})
        if sem.get("id") != sid: errs.append(f"sections/{sid}.json: semantic.id must equal the contract id")
        if sem.get("category") != c.get("category"): errs.append(f"sections/{sid}.json: semantic.category {sem.get('category')} != category {c.get('category')}")
        if src.get("id") == sid: errs.append(f"sections/{sid}.json: source.id must name the source component, not repeat the contract id")
        pinned_ok = sid not in RETRIEVAL_INELIGIBLE
        if c.get("retrievalEligible") is not pinned_ok:
            errs.append(f"retrieval pin: sections/{sid}.json retrievalEligible={c.get('retrievalEligible')} but RETRIEVAL_INELIGIBLE says {pinned_ok}")
        text = " ".join(str(c.get(k, "")) for k in ("id", "label", "purpose"))
        if RUNTIME_UI.search(text) and sid not in RETRIEVAL_INELIGIBLE:
            errs.append(f"retrieval pin: sections/{sid}.json looks like runtime/utility UI ('{RUNTIME_UI.search(text).group(0)}') but is not in RETRIEVAL_INELIGIBLE")
    if set(getattr(sv, "RETRIEVAL_INELIGIBLE", set())) != RETRIEVAL_INELIGIBLE:
        errs.append(f"retrieval pin: semantic_validate.RETRIEVAL_INELIGIBLE {sorted(getattr(sv, 'RETRIEVAL_INELIGIBLE', []))} != verify_all's {sorted(RETRIEVAL_INELIGIBLE)}")
    if sorted(allow.get("retrievalIneligible", [])) != sorted(RETRIEVAL_INELIGIBLE):
        errs.append(f"retrieval pin: allowlist.retrievalIneligible {allow.get('retrievalIneligible')} != pinned {sorted(RETRIEVAL_INELIGIBLE)}")

    # 6 derived files
    bc = mod("build_contracts", "extraction/build_contracts.py")
    for rel, d in bc.build().items():
        if open(os.path.join(REPO, rel), encoding="utf-8").read() != dump(d):
            errs.append(f"derived file drift: {rel} differs from what extraction/build_contracts.py generates")
    bt = mod("build_token_llm", "extraction/build_token_llm.py")
    cat_b, pol_b = bt.build()
    for rel, d in (("tokens/llm/token-catalog.json", cat_b), ("tokens/llm/token-policy.json", pol_b)):
        if open(os.path.join(REPO, rel), encoding="utf-8").read() != bt.dump(d):
            errs.append(f"token drift: {rel} differs from what extraction/build_token_llm.py derives from the token files")

    # 7
    seen = {}
    for t in templates:
        for n in t["nodes"]:
            if n["section"] not in secs: errs.append(f"template {t['id']} node '{n['section']}' has no section contract")
            for k in ("section", "required", "repeatable"):
                if k not in n: errs.append(f"template {t['id']} node is missing '{k}' (nodes must be structured objects)")
        if not t.get("family"): errs.append(f"template {t['id']} has no family")
    for r in ledger["routes"]:
        if r["route"] in seen: errs.append(f"route {r['route']} assigned twice")
        seen[r["route"]] = r["template"]
        if r["template"] not in {t["id"] for t in templates}: errs.append(f"route {r['route']} maps to unknown template {r['template']}")
    if sum(t["routeCount"] for t in templates) != len(ledger["routes"]): errs.append("sum of template routeCount differs from the measured route list")
    if EVIDENCE:
        served = re.findall(r'path: "([^"]+)"', open(os.path.join(SRC, "routes.js"), encoding="utf-8").read())
        for p in served:
            if p not in seen: errs.append(f"route {p} is served by src/routes.js but not mapped to a template")
        for p in seen:
            if p not in served: errs.append(f"route {p} is mapped but src/routes.js does not serve it")
    for t in templates:
        n = sum(1 for r in ledger["routes"] if r["template"] == t["id"])
        if n != t["routeCount"]: errs.append(f"template {t['id']}: routeCount {t['routeCount']} but {n} measured routes map to it")
        for r in t.get("routes", []):
            if seen.get(r) != t["id"]: errs.append(f"template {t['id']} lists route {r} that the ledger maps elsewhere")
        seq = [n["section"] for n in t["nodes"]]
        for r in ledger["routes"]:
            if r["template"] == t["id"]:
                ids = [s["id"] for s in r["sections"]]
                collapsed = [x for i, x in enumerate(ids) if i == 0 or ids[i - 1] != x]
                if collapsed != seq: errs.append(f"route {r['route']}: measured section sequence differs from template {t['id']}"); break
    fam_of = {t["id"]: t.get("family") for t in templates}
    covered = {}
    for p in gen_examples:
        rel = os.path.relpath(p, REPO)
        ex = json.load(open(p, encoding="utf-8"))
        if ex.get("mode") != "generation": errs.append(f"{rel}: examples/ holds generation examples only (mode is {ex.get('mode')!r})"); continue
        e1, _ = sv.check(ex)
        for e in e1: errs.append(f"{rel}: {e}")
        covered.setdefault(fam_of.get(ex.get("template")), rel)
    for fam in sorted({f for f in fam_of.values() if f}):
        if fam not in covered: errs.append(f"template family '{fam}' has no mode=generation example in schema/examples/")

    # 8
    rules = {r["id"]: r for r in graph["rules"]}
    for r in graph["rules"]:
        if r.get("severity") not in ("error", "warn"): errs.append(f"graph rule {r['id']} has no valid severity")
        if r.get("kind") not in sv.RULE_KINDS: errs.append(f"graph rule {r['id']} kind '{r.get('kind')}' is not implemented by semantic_validate.py")
    for sid, c in secs.items():
        tm = [t for t in templates if any(n["section"] == sid for n in t["nodes"])]
        mx = max((sum((n.get("maxCount", 1) if n["repeatable"] else 1) for n in t["nodes"] if n["section"] == sid) for t in tm), default=0)
        cons = c["constraints"]
        if (cons.get("onePerPage") and mx != 1) or (not cons.get("onePerPage") and cons.get("maxPerPage") != mx):
            errs.append(f"sections/{sid}.json constraints disagree with templates (observed max per page {mx})")
        want = 1 if cons.get("onePerPage") else cons.get("maxPerPage")
        if rules.get("SECTION_PER_PAGE_LIMITS", {}).get("limits", {}).get(sid) != want:
            errs.append(f"graph SECTION_PER_PAGE_LIMITS['{sid}'] = {rules.get('SECTION_PER_PAGE_LIMITS', {}).get('limits', {}).get(sid)} but the contract says {want}")
    for rid, key in (("SHELL_MUST_BE_FIRST", "mustBeFirst"), ("SHELL_MUST_BE_LAST", "mustBeLast"), ("NO_CONSECUTIVE_SAME_SECTION", "noConsecutive")):
        if sorted(rules.get(rid, {}).get("sections", [])) != sorted(s for s, c in secs.items() if c["constraints"].get(key)):
            errs.append(f"graph {rid} disagrees with the section contracts' {key}")
    hero_ex = sorted(t["id"] for t in templates if sum((n.get("maxCount") or 1) if n.get("repeatable") else 1 for n in t["nodes"] if secs.get(n["section"], {}).get("category") == "HERO") > 1)
    if sorted(rules.get("ONE_HERO_PER_PAGE", {}).get("exceptions", [])) != hero_ex:
        errs.append(f"graph ONE_HERO_PER_PAGE exceptions {rules.get('ONE_HERO_PER_PAGE', {}).get('exceptions')} but templates give {hero_ex}")

    # 9 citations against the clone's own source
    ledger_at = {}
    for r in ledger["routes"]:
        for s_ in r["sections"]:
            k = f"{s_['file']}:{s_['lines'][0]}-{s_['lines'][1]}"
            if k in ledger_at and ledger_at[k]["id"] != s_["id"]: errs.append(f"citation {k} is attributed to both '{ledger_at[k]['id']}' and '{s_['id']}'")
            ledger_at[k] = dict(s_, route=r["route"])
    for sid, c in secs.items():
        for cite in c["evidence"].get("measuredFrom", []):
            e = ledger_at.get(cite)
            if not e: errs.append(f"citation {cite} in sections/{sid}.json is not a measured section range")
            elif e["id"] != sid: errs.append(f"citation {cite} in sections/{sid}.json points at '{e['id']}', not '{sid}'")
    if EVIDENCE:
        cache = {}
        def lines_of(rel):
            p = os.path.join(PKG, rel)
            if p not in cache: cache[p] = open(p, encoding="utf-8", newline="").read().split("\n") if os.path.isfile(p) else None
            return cache[p]
        for cite, e in ledger_at.items():
            a, b = e["lines"]
            lines = lines_of(e["file"])
            if lines is None: errs.append(f"citation {cite}: file does not exist"); continue
            if not (1 <= a <= b <= len(lines)): errs.append(f"citation {cite}: range exceeds the file ({len(lines)} lines)"); continue
            if f"<{e['tag']}" not in lines[a - 1]: errs.append(f"citation {cite}: line {a} does not contain the cited <{e['tag']}> element")
            elif e.get("anchor") and e["anchor"] not in lines[a - 1]: errs.append(f"citation {cite}: line {a} does not contain the cited element's {e['anchor']!r}")
            if not e.get("part") and f'data-clone-section="{e["component"]}"' not in lines[a - 1]:
                errs.append(f"citation {cite}: line {a} is not the root of component {e['component']}")
            u = e.get("usage", {}); ul = lines_of(u.get("file", "")) if u else None
            if not ul or not (1 <= u.get("line", 0) <= len(ul)) or f"<{e['component']} />" not in ul[u["line"] - 1]:
                errs.append(f"citation {cite}: usage {u.get('file')}:{u.get('line')} does not render <{e['component']} /> (route {e['route']})")
        for sid, c in secs.items():
            src = c["source"]; lines = lines_of(src["file"])
            if lines is None or not (1 <= src["lines"][0] <= src["lines"][1] <= len(lines)):
                errs.append(f"sections/{sid}.json source {src['file']}:{src['lines']} does not resolve"); continue
            if f"<{src['tag']}" not in lines[src["lines"][0] - 1]: errs.append(f"sections/{sid}.json source line {src['lines'][0]} does not hold <{src['tag']}>")
            if f"{src['file']}:{src['lines'][0]}-{src['lines'][1]}" not in ledger_at: errs.append(f"sections/{sid}.json source range is not a ledger range")
        bl = mod("build_ledger", "extraction/build_ledger.py")
        nl, probs = bl.build()
        for p_ in probs: errs.append(f"ledger rebuild: {p_}")
        if not probs and dump(nl) != open(os.path.join(HERE, "measured-values.json"), encoding="utf-8").read():
            errs.append("ledger drift: measured-values.json differs from what extraction/build_ledger.py derives from src/")
        bs = mod("build_source_identity", "extraction/build_source_identity.py")
        if bs.dump(bs.build()) != open(os.path.join(REPO, "schema", "source-identity.json"), encoding="utf-8").read():
            errs.append("source-identity drift: schema/source-identity.json differs from what extraction/build_source_identity.py derives from the source")

    # 10
    known = set(F) | set(S) | set(L) | set(C)
    def refs(v):
        if isinstance(v, dict): return [x for vv in v.values() for x in refs(vv)]
        return re.findall(r"^\{(.+)\}$", v) if isinstance(v, str) else []
    for tier, toks in (("10-semantic", S), ("20-component", C), ("30-layout", L)):
        for tid, t in toks.items():
            for ref in refs(t.get("$value")):
                if ref not in known: errs.append(f"tokens/{tier}: {tid} references unknown token {{{ref}}}")
    allvals = {k: v.get("$value") for d in (F, S, L) for k, v in d.items()}
    def resolve(v, depth=0):
        if isinstance(v, dict): return {k: resolve(x, depth) for k, x in v.items()}
        m = re.match(r"^\{(.+)\}$", v) if isinstance(v, str) else None
        return resolve(allvals.get(m.group(1), v), depth + 1) if m and depth < 5 else v
    theme = J("tokens/themes/light.json")["resolves"]
    for sid, t in S.items():
        if sid not in theme: errs.append(f"theme light does not resolve semantic token {sid}")
        elif resolve(t["$value"]) != theme[sid]: errs.append(f"theme light: {sid} resolves to {theme[sid]!r} but the tokens give {resolve(t['$value'])!r}")
    for sid in theme:
        if sid not in S: errs.append(f"theme light resolves unknown token {sid}")
    cat = J("tokens/llm/token-catalog.json")
    for k, ids in cat["categories"].items():
        for i in ids:
            if i not in cat["tokens"] or not cat["tokens"][i]["referenceable"]: errs.append(f"token-catalog.{k}: '{i}' is not a real referenceable token")
    pol = J("tokens/llm/token-policy.json")
    if sorted(pol.get("rawValueRestrictions", {})) != sorted(cat["categories"]): errs.append(f"token-policy rawValueRestrictions keys {sorted(pol.get('rawValueRestrictions', {}))} do not match catalog categories {sorted(cat['categories'])}")
    for rule in ("TOKEN_UNKNOWN", "TOKEN_RAW_VALUE", "TOKEN_ARBITRARY_SPACING", "TOKEN_UNSUPPORTED_FONT", "TOKEN_THEME_MISMATCH"):
        if rule not in pol.get("rules", {}) or rule not in open(os.path.join(REPO, "schema", "semantic_validate.py"), encoding="utf-8").read():
            errs.append(f"token rule {rule} is not both declared in token-policy.json and enforced in semantic_validate.py")

    # 11
    roles = assets["roles"]; policies = set(assets["generationPolicies"]); avs = set(assets.get("availabilities", []))
    if avs != {"clone-only", "generation-safe", "blocked-for-generation"}: errs.append(f"asset-roles.json availabilities {sorted(avs)} is not the closed set")
    for r, v in roles.items():
        if v["generationPolicy"] not in policies: errs.append(f"asset role {r}: policy '{v['generationPolicy']}' is not in generationPolicies")
        if v.get("availability") not in avs: errs.append(f"asset role {r}: availability {v.get('availability')!r} is not closed")
        if v.get("availability") != "generation-safe":
            subs = v.get("generationSafeSubstitutes") or []
            if not subs: errs.append(f"asset role {r} is {v.get('availability')} but has no generationSafeSubstitutes")
            for s in subs:
                if PINNED_AVAILABILITY.get(s) != "generation-safe": errs.append(f"asset role {r}: substitute '{s}' is not a pinned generation-safe role")
        if not v.get("generatedModeGuidance"): errs.append(f"asset role {r} has no generatedModeGuidance")
    for r, want in PINNED.items():
        if r not in roles: errs.append(f"pinned asset role '{r}' is missing from the registry")
        elif roles[r]["generationPolicy"] != want or not roles[r].get("pinned"): errs.append(f"pinned asset role '{r}' must be '{want}' (pinned), found '{roles[r]['generationPolicy']}'")
    for r in REQUIRED_GENERATION_SAFE:
        if PINNED_AVAILABILITY.get(r) != "generation-safe": errs.append(f"required generation-safe role '{r}' is not pinned generation-safe")
    for r, want in PINNED_AVAILABILITY.items():
        if r not in roles: errs.append(f"PINNED_AVAILABILITY role '{r}' is missing from the registry")
        elif roles[r].get("availability") != want: errs.append(f"PINNED_AVAILABILITY: asset role '{r}' must be '{want}', registry says '{roles[r].get('availability')}'")
    for r in roles:
        if r not in PINNED_AVAILABILITY: errs.append(f"asset role '{r}' has no PINNED_AVAILABILITY entry")
    if getattr(sv, "PINNED_AVAILABILITY", None) != PINNED_AVAILABILITY:
        diff = sorted(k for k in set(PINNED_AVAILABILITY) | set(getattr(sv, "PINNED_AVAILABILITY", {})) if PINNED_AVAILABILITY.get(k) != getattr(sv, "PINNED_AVAILABILITY", {}).get(k))
        errs.append(f"PINNED_AVAILABILITY in semantic_validate.py differs from verify_all.py for {diff}")
    if PINNED_AVAILABILITY.get("logo") == "generation-safe": errs.append("the real logo can never be generation-safe")
    for a in assets["assets"]:
        if a["role"] not in roles: errs.append(f"asset {a['path']}: role '{a['role']}' is not in the closed role set")
    if EVIDENCE and os.path.isdir(PUB):
        srcblob = None
        for a in assets["assets"]:
            if a["path"].startswith("mailto:"): continue
            if a.get("inlineSource"):
                il = a["inlineSource"]; p = os.path.join(PKG, il["file"])
                line = open(p, encoding="utf-8").read().split("\n")[il["line"] - 1] if os.path.isfile(p) else ""
                ok = False
                for m in re.finditer(r'"(data:image/svg\+xml,(?:[^"\\]|\\.)*)"', line):
                    b = json.loads('"' + m.group(1) + '"').split(",", 1)[1].encode()
                    ok = ok or hashlib.sha256(b).hexdigest() == il["sha256"]
                if not ok: errs.append(f"asset {a['path']}: inline mark at {il['file']}:{il['line']} does not hash to its recorded sha256")
                continue
            onpub = os.path.isfile(os.path.join(PUB, a["path"]))
            if a.get("inClone") is False:
                if srcblob is None:
                    srcblob = "\n".join(open(f, encoding="utf-8", errors="ignore").read() for f in glob.glob(os.path.join(SRC, "**", "*.*"), recursive=True))
                if onpub or os.path.basename(a["path"]) in srcblob: errs.append(f"asset {a['path']} is flagged inClone=false but the clone ships or references it")
            elif not onpub:
                errs.append(f"asset missing on disk: public/{a['path']}")
    elif EVIDENCE:
        errs.append("package has src/ but no public/: the clone's asset tree is missing")
    for sid, c in secs.items():
        for r in c.get("assetRoles", []) + c.get("generatedAssetRoles", []):
            if r not in roles: errs.append(f"sections/{sid}.json uses unknown asset role '{r}'")
        for r in c.get("generatedAssetRoles", []):
            if PINNED_AVAILABILITY.get(r) != "generation-safe": errs.append(f"sections/{sid}.json generatedAssetRoles has non-generation-safe '{r}'")

    # 12
    mot = schema["definitions"]["motion"]; mc_ = J("motion/motion-contract.json")
    if mot.get("additionalProperties") is not False: errs.append("schema motion object is not closed")
    if sorted(mot["properties"]) != sorted(mc_["closedFields"]): errs.append("schema motion fields differ from motion-contract closedFields")
    if sorted(mot["properties"]["pattern"]["enum"]) != sorted(mc_["patterns"]): errs.append("schema motion patterns differ from motion-contract patterns")
    for sid, c in secs.items():
        for p in c["motion"]["allowedPatterns"]:
            if p not in mc_["patterns"]: errs.append(f"sections/{sid}.json motion pattern '{p}' is not in the motion contract")

    # 13 machine paths
    U = "/" + "Users/"  # assembled so this file does not match its own check
    leak = re.compile(r"(?:^|[\s`(\"'=])(" + U + r"[^/\s]+/|/home/[^/\s]+/|/" + r"private/(?:tmp|var)/|/var/" + r"folders/|/" + r"tmp/[^\s]|[A-Za-z]:\\\\" + "Users" + r"\\\\)")
    for root, _, fs in os.walk(REPO):
        if "__pycache__" in root: continue
        for f in fs:
            if not f.endswith((".json", ".md", ".py", ".mjs")): continue
            p = os.path.join(root, f); rel = os.path.relpath(p, REPO)
            m = leak.search(open(p, encoding="utf-8", errors="ignore").read())
            if m: errs.append(f"absolute path in {rel}: {m.group(1)}")

    # 14
    try: Draft7Validator.check_schema(schema)
    except Exception as e: errs.append(f"pagespec.schema.json is not valid draft-07: {e}")
    ex = J("schema/example.pagespec.json")
    if ex.get("mode") != "clone": errs.append("schema/example.pagespec.json must be the mode=clone example")
    e1, _ = sv.check(ex)
    for e in e1: errs.append(f"example.pagespec.json: {e}")
    if os.environ.get("VERIFY_SKIP_ADVERSARIAL") != "1":  # prove_drift.py sets this: its injections target the checks above
        r = subprocess.run([sys.executable, os.path.join(REPO, "schema/tests/adversarial_test.py")], capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        if r.returncode: errs.append("adversarial suite failed:\n      " + (r.stdout + r.stderr).strip().replace("\n", "\n      ")[-3000:])
        else: print("  " + last)

    # 15
    wg = mod("wrapper_gate", "extraction/wrapper_gate.py")
    ge, gw = wg.gate(*wg.load_inputs(REPO))
    errs.extend(ge); warns.extend(gw)

    # 16 design-policy binding
    dp = man.get("designPolicy", {})
    ref = dp.get("ref", "")
    if not ref or not os.path.isfile(os.path.join(REPO, ref)):
        errs.append(f"designPolicy.ref {ref!r} does not exist")
    else:
        pf = J(ref)
        for k in ("policyId", "policyVersion", "commonIrVersion"):
            if pf.get(k) != dp.get(k): errs.append(f"designPolicy.{k} {dp.get(k)!r} != {ref} {pf.get(k)!r}")
        if dp.get("commonIrVersion") != "0.5": errs.append("designPolicy.commonIrVersion must be 0.5")
        if dp.get("enforcementMode") != "hard-and-soft" or pf.get("enforcementMode") != "hard-and-soft": errs.append("designPolicy.enforcementMode must be hard-and-soft")
        saas = pf.get("classification", {}).get("isSaaS")
        if (man.get("category") == "saas") != bool(saas): errs.append(f"manifest category {man.get('category')!r} disagrees with policy isSaaS={saas}")
        if saas and (dp.get("policyId"), dp.get("policyVersion")) != ("n0-saas-design-constraints-common", "0.1.0"):
            errs.append("a SaaS repo must bind n0-saas-design-constraints-common 0.1.0")
        if not saas and dp.get("policyId") == "n0-saas-design-constraints-common": errs.append("a non-SaaS repo must not bind the SaaS policy")
        for f in pf.get("enforcedBy", []):
            if not os.path.isfile(os.path.join(REPO, f)): errs.append(f"{ref}: enforcedBy file {f} does not exist")
        for ev in pf.get("classification", {}).get("evidence", []):
            m = re.match(r"^(src/[^:]+):(\d+)$", ev.get("at", ""))
            if not m: errs.append(f"{ref}: evidence {ev.get('at')!r} is not a src/file:line citation")
            elif EVIDENCE:
                p = os.path.join(PKG, m.group(1))
                if not os.path.isfile(p) or int(m.group(2)) > len(open(p, encoding="utf-8").read().split("\n")): errs.append(f"{ref}: evidence {ev['at']} does not resolve")
        if pf.get("approval", {}).get("architectureDecisionRecorded") is not False and pf.get("approval", {}).get("policyDecision") == "defined-pending-architecture-review":
            errs.append(f"{ref}: approval is pending, architectureDecisionRecorded must be false")
        ph = mod("policy_hash", "extraction/policy_hash.py").policy_hash(REPO, ref)
        if dp.get("contentHash") != ph: errs.append(f"designPolicy.contentHash {dp.get('contentHash')} != recomputed {ph}")

    # 17
    z = os.path.join(PKG, "design-repo.zip")
    if os.path.isfile(z):
        names = zipfile.ZipFile(z).namelist()
        junk = [n for n in names if "__MACOSX" in n or n.endswith(".DS_Store")]
        if junk: errs.append(f"design-repo.zip contains {len(junk)} __MACOSX/.DS_Store entries")
        zt = os.path.getmtime(z)
        newer = [os.path.relpath(os.path.join(rt, f), REPO) for rt, _, fs in os.walk(REPO) for f in fs if os.path.getmtime(os.path.join(rt, f)) > zt + 1 and "__pycache__" not in rt]
        if newer: errs.append(f"design-repo.zip is stale: {len(newer)} file(s) changed after it was built (e.g. {newer[0]})")
    return finish()


def finish():
    for w in warns: print("WARN:", w)
    if errs:
        print("REPO NOT ADMITTED:"); [print("  -", e) for e in errs]; sys.exit(1)
    if not EVIDENCE:
        print("REPO OK (design-repo copied alone: citations, asset files and source rebuilds not checked) — structure, entryPoints, versions, counts, parity, contract schema, retrieval pin, derived files, templates, graph, tokens, pinned assets + availability, motion, paths, examples, adversarial suite, wrapper gate and policy binding pass.")
    else:
        print("REPO OK — structure, entryPoints, versions, counts, parity, contract schema, retrieval pin, derived files, templates + route coverage, graph, citations against src/, ledger + source-identity rebuilds, tokens, pinned assets + availability, asset files, motion, paths, examples, adversarial suite, wrapper gate and policy binding all pass.")
    sys.exit(0)


if __name__ == "__main__":
    main()
