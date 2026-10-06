#!/usr/bin/env python3
"""Admission check for this design repo. Exit 0 = admitted.

  1  required files exist and parse
  2  manifest fields; entryPoints relative, inside design-repo/ (no ../), present
  3  allowlistVersion matches the allowlist (machine-checked version field)
  4  counts recomputed from the files on disk (manifest AND README)
  5  allowlist parity: sections/components/primitives files <-> allowlist, nodeProperties <-> schema
  6  schema parity: template/section/assetRole enums and content definitions match the contracts
  7  templates: every node has a contract; routes assigned exactly once; coverage matches the ledger
  8  constraints + graph recomputed from templates (a rule in prose and in code must agree)
  9  citations: every path:line-line resolves, is in range, and the cited line holds the cited tag.
     The evidence tree is resolved from measured-values.json's sourceProject.snapshotFolder, never
     guessed from a generic root src/ (which could be the runnable clone's own source) — a ledger
     that declares one and finds it missing fails outright; one with none at all (an older ledger)
     degrades to a warning instead, same as a design-repo shipped without its evidence tree.
 10  tokens: every {reference} resolves; theme resolves every semantic token to the recomputed value;
     catalog ids exist; policy categories match catalog keys
 11  assets: closed role vocabulary; PINNED roles hold their exact policy; files exist (warn if no public/)
 12  motion closed to the contract's fields; section patterns inside the contract
 13  no absolute machine paths in any JSON/MD file
 14  schema is valid draft-07; example validates with zero errors; adversarial suite passes
 15  zip hygiene, only if someone creates ../design-repo.zip by hand (the builder does not produce one)

Drift-proofing lives in extraction/prove_drift.py (injects each defect into a scratch copy).
"""
import importlib.util, json, os, re, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG = os.path.dirname(REPO)
MIRROR = PKG  # resolved for real at the top of main(), from measured-values.json's sourceProject.snapshotFolder
errs, warns = [], []
NOT_SHIPPED = False  # set when the evidence tree is absent because the package's .gitignore leaves it out (a published copy)


def gitignored(rel):
    """True when the package's own .gitignore excludes rel or one of its parent folders (plain folder patterns only)."""
    gi = os.path.join(PKG, ".gitignore")
    if not os.path.isfile(gi): return False
    pats = {l.strip().strip("/") for l in open(gi, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")}
    parts = rel.strip("/").split("/")
    return any("/".join(parts[:i]) in pats for i in range(1, len(parts) + 1))
# Pinned generation policies. Kept HERE, independent of assets/asset-roles.json, so that changing a
# role in the registry to a different-but-still-valid policy is caught (membership alone is not enough).
PINNED = {"logo": "must-reuse-exact", "customer-logo": "must-not-fabricate", "avatar": "must-not-fabricate",
          "font": "must-reuse-exact", "live-embed": "must-not-reuse-live-endpoint",
          "founder-contact-email": "must-not-reuse-live-endpoint"}
REQUIRED = ["registry.manifest.json", "README.md", "CHANGELOG.md", "tokens/themes/light.json",
            "tokens/llm/token-catalog.json", "tokens/llm/token-policy.json", "tokens/llm/component-allowlist.json",
            "templates/templates.json", "compatibility/graph.json", "assets/asset-roles.json", "motion/motion-contract.json",
            "schema/pagespec.schema.json", "schema/example.pagespec.json", "schema/semantic_validate.py",
            "schema/tests/adversarial_test.py", "extraction/measured-values.json", "extraction/prove_drift.py"]
ENTRY_KEYS = ["tokenCatalog", "tokenPolicy", "componentAllowlist", "compatibilityGraph", "assetContract", "motionContract",
              "templates", "pagespecSchema", "examplePageSpec", "semanticValidate", "adversarialSuite", "admission",
              "driftProof", "measuredValues", "defaultTheme"]


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


def main():
    # 1
    for rel in REQUIRED:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p): errs.append(f"missing: {rel}")
        elif rel.endswith(".json"):
            try: J(rel)
            except Exception as e: errs.append(f"bad json {rel}: {e}")
    for d in ("tokens/00-foundation", "tokens/10-semantic", "tokens/20-component", "tokens/30-layout", "sections", "primitives", "components"):
        if not os.path.isdir(os.path.join(REPO, d)): errs.append(f"missing folder: {d}/")
    if errs: return finish()
    man = J("registry.manifest.json")
    allow = J("tokens/llm/component-allowlist.json")
    schema = J("schema/pagespec.schema.json")
    templates = J("templates/templates.json")["templates"]
    graph = J("compatibility/graph.json")
    assets = J("assets/asset-roles.json")
    ledger = J("extraction/measured-values.json")

    # the evidence tree (rendered HTML snapshots + their asset mirror) is wherever the ledger itself says it is —
    # never guessed from a generic root src/ or public/, which could just as easily be the runnable clone's own
    # source. snapshotFolder is relative to the package root (PKG), e.g. "recon/mirror/src/" or "src/" for an
    # older package that still keeps its evidence at the root. A ledger with no snapshotFolder at all (written by
    # a builder version that predates this field) falls back to the old recon/mirror-or-root heuristic so it is
    # not treated as a hard failure; a ledger that DOES declare one and the folder is missing is a real defect.
    snap = ledger.get("sourceProject", {}).get("snapshotFolder")
    if snap:
        mirror = os.path.normpath(os.path.join(PKG, snap, ".."))
        if not os.path.isdir(mirror):
            # A published copy of a package (a git clone of it) deliberately leaves the evidence out: recon/ is gigabytes and the
            # package's own .gitignore excludes it. That is not a misplaced evidence tree, so it is reported, not failed, but ONLY for
            # the standard location: any other declared folder that is missing (a typo, a moved tree) still fails outright.
            global NOT_SHIPPED
            if os.path.normpath(snap) == os.path.normpath("recon/mirror/src") and gitignored("recon/mirror/src"):
                NOT_SHIPPED = True
                warns.append("evidence not shipped with this copy (recon/ is in .gitignore): citations and asset files are not checked here; run verify_all.py where recon/mirror/ exists to admit fully")
            else:
                errs.append(f"measured-values.json declares sourceProject.snapshotFolder '{snap}' but {os.path.relpath(mirror, PKG)}/ does not exist")
    else:
        mirror = os.path.join(PKG, "recon", "mirror") if os.path.isdir(os.path.join(PKG, "recon", "mirror")) else PKG
    global MIRROR
    MIRROR = mirror
    secs = {}
    for f in files_in("sections"):
        c = J(f"sections/{f}")
        if c.get("id") + ".json" != f: errs.append(f"sections/{f}: id '{c.get('id')}' does not match its file name")
        secs[c["id"]] = c

    # 2
    for k in ("repositoryId", "status", "productionApproved", "defaultTheme", "schemaValidatedThemes", "allowlistVersion", "versionFieldNote", "counts", "entryPoints"):
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

    # 4
    F, S, L = tokens_in("00-foundation"), tokens_in("10-semantic"), tokens_in("30-layout")
    C = {}  # component tokens share prop names across files, so namespace them: button.background
    for f in files_in("tokens/20-component"):
        d = J(f"tokens/20-component/{f}")
        C.update({f"{d['component']}.{k}": v for k, v in d.get("tokens", {}).items()})
    comp_tokens = len(C)
    actual = {"sections": len(secs), "templates": len(templates), "routes": sum(t["routeCount"] for t in templates),
              "primitives": len(files_in("primitives")), "components": len(files_in("components")), "assets": len(assets.get("assets", [])),
              "themes": len(files_in("tokens/themes")), "rules": len(graph.get("rules", [])),
              "tokens": {"foundation": len(F), "semantic": len(S), "component": comp_tokens, "layout": len(L)}}
    mc = man.get("counts", {})
    for k, v in actual.items():
        if mc.get(k) != v: errs.append(f"manifest counts.{k} = {mc.get(k)} but the files give {v}")
    readme = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    for label, v in [("Sections", actual["sections"]), ("Templates", actual["templates"]), ("Routes", actual["routes"]),
                     ("Primitives", actual["primitives"]), ("Components", actual["components"]), ("Assets", actual["assets"]),
                     ("Foundation tokens", len(F)), ("Semantic tokens", len(S)), ("Rules", actual["rules"])]:
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
    for sid, c in secs.items():
        if sorted(allow.get("contentFields", {}).get(sid, [])) != sorted(c["content"]["fields"]):
            errs.append(f"allowlist.contentFields['{sid}'] differs from sections/{sid}.json")

    # 6
    if sorted(schema["properties"]["template"]["enum"]) != sorted(t["id"] for t in templates): errs.append("schema template enum differs from templates.json")
    if sorted(schema["definitions"]["node"]["properties"]["type"]["enum"]) != sorted(secs): errs.append("schema node type enum differs from sections/")
    if sorted(schema["definitions"]["assetRole"]["enum"]) != sorted(assets["roles"]): errs.append("schema assetRole enum differs from assets/asset-roles.json roles")
    for sid, c in secs.items():
        d = schema["definitions"].get(f"content.{sid}")
        if not d: errs.append(f"schema has no content definition for {sid}"); continue
        if d.get("additionalProperties") is not False: errs.append(f"schema content.{sid} is not closed (additionalProperties must be false)")
        if sorted(d["properties"]) != sorted(c["content"]["fields"]): errs.append(f"schema content.{sid} fields differ from the section contract")

    # 7
    seen = {}
    ledger_routes = [r["route"] for r in ledger["routes"]]
    for t in templates:
        for n in t["nodes"]:
            if n["section"] not in secs: errs.append(f"template {t['id']} node '{n['section']}' has no section contract")
            for k in ("section", "required", "repeatable"):
                if k not in n: errs.append(f"template {t['id']} node is missing '{k}' (nodes must be structured objects)")
    for r in ledger["routes"]:
        if r["route"] in seen: errs.append(f"route {r['route']} assigned twice")
        seen[r["route"]] = r["template"]
        if r["template"] not in {t["id"] for t in templates}: errs.append(f"route {r['route']} maps to unknown template {r['template']}")
    if sum(t["routeCount"] for t in templates) != len(ledger_routes): errs.append("sum of template routeCount differs from the measured route list")
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

    # 8
    for sid, c in secs.items():
        tm = [t for t in templates if any(n["section"] == sid for n in t["nodes"])]
        mx = max((sum((n.get("maxCount", 1) if n["repeatable"] else 1) for n in t["nodes"] if n["section"] == sid) for t in tm), default=0)
        cons = c["constraints"]
        if (cons.get("onePerPage") and mx != 1) or (not cons.get("onePerPage") and cons.get("maxPerPage") != mx):
            errs.append(f"sections/{sid}.json constraints disagree with templates (observed max per page {mx})")
        first = c["category"] == "SHELL" and tm and all(t["nodes"][0]["section"] == sid for t in tm)
        last = c["category"] == "SHELL" and tm and all(t["nodes"][-1]["section"] == sid for t in tm)
        if bool(cons.get("mustBeFirst")) != bool(first): errs.append(f"sections/{sid}.json mustBeFirst disagrees with templates")
        if bool(cons.get("mustBeLast")) != bool(last): errs.append(f"sections/{sid}.json mustBeLast disagrees with templates")
    rules = {r["id"]: r for r in graph["rules"]}
    sv = load_validator()
    for r in graph["rules"]:
        if r.get("severity") not in ("error", "warn"): errs.append(f"graph rule {r['id']} has no valid severity")
        if r.get("kind") not in sv.RULE_KINDS: errs.append(f"graph rule {r['id']} kind '{r.get('kind')}' is not implemented by semantic_validate.py")
    lim = rules.get("SECTION_PER_PAGE_LIMITS", {}).get("limits", {})
    for sid, c in secs.items():
        want = 1 if c["constraints"].get("onePerPage") else c["constraints"].get("maxPerPage")
        if lim.get(sid) != want: errs.append(f"graph SECTION_PER_PAGE_LIMITS['{sid}'] = {lim.get(sid)} but the contract says {want}")
    for rid, key in (("SHELL_MUST_BE_FIRST", "mustBeFirst"), ("SHELL_MUST_BE_LAST", "mustBeLast"), ("NO_CONSECUTIVE_SAME_SECTION", "noConsecutive")):
        if sorted(rules.get(rid, {}).get("sections", [])) != sorted(s for s, c in secs.items() if c["constraints"].get(key)):
            errs.append(f"graph {rid} disagrees with the section contracts' {key}")
    # a repeatable node (consecutive duplicates collapsed by the model into one {repeatable, maxCount}) represents
    # maxCount instances of that section, not one — a template with hero.main, hero.main collapses to a single
    # node but still puts two HERO sections on the page, so it must count as 2 here too, not 1.
    hero_ex = sorted(t["id"] for t in templates if sum((n.get("maxCount") or 1) if n.get("repeatable") else 1 for n in t["nodes"] if secs.get(n["section"], {}).get("category") == "HERO") > 1)
    if sorted(rules.get("ONE_HERO_PER_PAGE", {}).get("exceptions", [])) != hero_ex:
        errs.append(f"graph ONE_HERO_PER_PAGE exceptions {rules.get('ONE_HERO_PER_PAGE', {}).get('exceptions')} but templates give {hero_ex}")

    # 9
    src = os.path.join(MIRROR, "src")
    ledger_at = {}  # "file:start-end" -> ledger entry (the ONE element that range belongs to)
    for r in ledger["routes"]:
        for s_ in r["sections"]:
            if s_.get("lines"):
                ledger_at[f"{r['file']}:{s_['lines'][0]}-{s_['lines'][1]}"] = dict(s_, file=r["file"])
    for sid, c in secs.items():  # a contract may only cite ranges the ledger attributes to THIS section
        for cite in c["evidence"].get("measuredFrom", []):
            e = ledger_at.get(cite)
            if not e: errs.append(f"citation {cite} in sections/{sid}.json is not a measured section range")
            elif e["id"] != sid: errs.append(f"citation {cite} in sections/{sid}.json points at '{e['id']}', not '{sid}'")
    if not os.path.isdir(src):
        warns.append(f"no evidence src/ tree at {os.path.relpath(src, PKG)} — {len(ledger_at)} citations not resolved against files (expected when design-repo/ is shipped alone)")
    else:
        cache = {}
        for cite, e in ledger_at.items():
            m = re.match(r"^(.+):(\d+)-(\d+)$", cite)
            p, a, b = os.path.join(MIRROR, m.group(1)), int(m.group(2)), int(m.group(3))
            if p not in cache:
                cache[p] = open(p, encoding="utf-8", errors="ignore", newline="").read().split("\n") if os.path.isfile(p) else None
            lines = cache[p]
            if lines is None: errs.append(f"citation {cite}: file does not exist"); continue
            if not (1 <= a <= b <= len(lines)): errs.append(f"citation {cite}: range exceeds the file ({len(lines)} lines)"); continue
            line = lines[a - 1]
            if f"<{e['tag']}" not in line: errs.append(f"citation {cite}: line {a} does not contain the cited <{e['tag']}> element")
            elif e.get("anchor") and e["anchor"] not in line: errs.append(f"citation {cite}: line {a} does not contain the cited element's {e['anchor']!r}")

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
    cat = J("tokens/llm/token-catalog.json")["categories"]
    comp_ids = set(C)
    for k, ids in cat.items():
        for i in ids:
            if i not in S and i not in L and i not in comp_ids: errs.append(f"token-catalog.{k}: '{i}' is not a real token")
    pol = J("tokens/llm/token-policy.json")
    if sorted(pol.get("rawValueRestrictions", {})) != sorted(cat): errs.append(f"token-policy rawValueRestrictions keys {sorted(pol.get('rawValueRestrictions', {}))} do not match catalog categories {sorted(cat)}")

    # 11
    roles = assets["roles"]; policies = set(assets["generationPolicies"])
    for r, v in roles.items():
        if v["generationPolicy"] not in policies: errs.append(f"asset role {r}: policy '{v['generationPolicy']}' is not in generationPolicies")
    for r, want in PINNED.items():
        if r not in roles: errs.append(f"pinned asset role '{r}' is missing from the registry")
        elif roles[r]["generationPolicy"] != want or not roles[r].get("pinned"): errs.append(f"pinned asset role '{r}' must be '{want}' (pinned), found '{roles[r]['generationPolicy']}'")
    pub = os.path.join(MIRROR, "public")
    # Some asset entries are not a file under public/ at all (e.g. a mailto: contact address) — real
    # evidence worth a pinned contract, but nothing to resolve on disk.
    is_virtual = lambda a: ":" in a["path"].split("/")[0] and not re.match(r"^[A-Za-z]:\\", a["path"])
    for a in assets["assets"]:
        if a["role"] not in roles: errs.append(f"asset {a['path']}: role '{a['role']}' is not in the closed role set")
    if os.path.isdir(pub):
        for a in assets["assets"]:
            if is_virtual(a): continue
            p = os.path.join(pub, a["path"])
            if not os.path.isfile(p): errs.append(f"asset missing on disk: public/{a['path']}")
    else:
        warns.append(f"no evidence public/ mirror at {os.path.relpath(pub, PKG)} — asset files not checked")
    for sid, c in secs.items():
        for r in c.get("assetRoles", []):
            if r not in roles: errs.append(f"sections/{sid}.json uses unknown asset role '{r}'")

    # 12
    mot = schema["definitions"]["motion"]; mc_ = J("motion/motion-contract.json")
    if mot.get("additionalProperties") is not False: errs.append("schema motion object is not closed")
    if sorted(mot["properties"]) != sorted(mc_["closedFields"]): errs.append("schema motion fields differ from motion-contract closedFields")
    if sorted(mot["properties"]["pattern"]["enum"]) != sorted(mc_["patterns"]): errs.append("schema motion patterns differ from motion-contract patterns")
    for sid, c in secs.items():
        for p in c["motion"]["allowedPatterns"]:
            if p not in mc_["patterns"]: errs.append(f"sections/{sid}.json motion pattern '{p}' is not in the motion contract")

    # 13  machine paths: every JSON string VALUE that starts with one (site routes like "/home/about" are not paths)
    leak = re.compile(r"^(/Users/|/home/[^/]+/|/private/|/var/folders/|/tmp/|[A-Za-z]:\\\\)")
    md_leak = re.compile(r"(?:^|[\s`(\"'])(/Users/|/home/[^/\s]+/|/private/|/var/folders/|/tmp/|[A-Za-z]:\\\\)", re.M)
    ROUTE_KEYS = {"route", "routes", "sampleRoute", "routePattern"}
    def walk(v, key=None):
        if isinstance(v, dict):
            for k, x in v.items(): yield from walk(x, k)
        elif isinstance(v, list):
            for x in v: yield from walk(x, key)
        elif isinstance(v, str) and key not in ROUTE_KEYS:
            m = leak.match(v)
            if m: yield m.group(1)
    for root, _, fs in os.walk(REPO):
        for f in fs:
            p = os.path.join(root, f); rel = os.path.relpath(p, REPO)
            if f.endswith(".json"):
                hit = next(walk(json.load(open(p, encoding="utf-8"))), None)
                if hit: errs.append(f"absolute path in {rel}: {hit}")
            elif f.endswith(".md"):
                m = md_leak.search(open(p, encoding="utf-8", errors="ignore").read())
                if m: errs.append(f"absolute path in {rel}: {m.group(1)}")
            elif f.endswith(".py") and re.search(r"^(REPO|ROOT|HERE)\s*=\s*['\"]/", open(p, encoding="utf-8").read(), re.M):
                errs.append(f"hard-coded root path in {rel}")

    # 14
    from jsonschema import Draft7Validator
    try: Draft7Validator.check_schema(schema)
    except Exception as e: errs.append(f"pagespec.schema.json is not valid draft-07: {e}")
    e1, w1 = sv.check(J("schema/example.pagespec.json"))
    for e in e1: errs.append(f"example.pagespec.json: {e}")
    if os.environ.get("VERIFY_SKIP_ADVERSARIAL") != "1":  # prove_drift.py sets this: its injections target the checks above
        r = subprocess.run([sys.executable, os.path.join(REPO, "schema/tests/adversarial_test.py")], capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        if r.returncode: errs.append("adversarial suite failed:\n      " + (r.stdout + r.stderr).strip().replace("\n", "\n      "))
        else: print("  " + last)

    # 15
    z = os.path.join(PKG, "design-repo.zip")
    if os.path.isfile(z):
        names = zipfile.ZipFile(z).namelist()
        junk = [n for n in names if "__MACOSX" in n or n.endswith(".DS_Store")]
        if junk: errs.append(f"design-repo.zip contains {len(junk)} __MACOSX/.DS_Store entries")
        zt = os.path.getmtime(z)
        newer = [os.path.relpath(os.path.join(rt, f), REPO) for rt, _, fs in os.walk(REPO) for f in fs if os.path.getmtime(os.path.join(rt, f)) > zt + 1 and "__pycache__" not in rt]
        if newer: errs.append(f"design-repo.zip is stale: {len(newer)} file(s) changed after it was built (e.g. {newer[0]})")
    return finish()


def load_validator():
    spec = importlib.util.spec_from_file_location("semantic_validate", os.path.join(REPO, "schema/semantic_validate.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def finish():
    for w in warns: print("WARN:", w)
    if errs:
        print("REPO NOT ADMITTED:"); [print("  -", e) for e in errs]; sys.exit(1)
    if NOT_SHIPPED:
        print("REPO OK (evidence not shipped with this copy: citations and asset files not checked) — structure, entryPoints, versions, counts, parity, templates, graph, tokens, pinned assets, motion, paths, schema and adversarial suite all pass.")
    else:
        print("REPO OK — structure, entryPoints, versions, counts, parity, templates, graph, citations, tokens, pinned assets, motion, paths, schema and adversarial suite all pass.")
    sys.exit(0)


if __name__ == "__main__":
    main()
