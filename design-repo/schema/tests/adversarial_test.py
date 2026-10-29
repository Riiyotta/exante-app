#!/usr/bin/env python3
"""Adversarial suite: proves every rule REJECTS a bad PageSpec for the RIGHT reason, and that controls pass.

Controls: the bundled mode=clone example (real content), every mode=generation example in schema/examples/, and
one synthesized minimal PageSpec per template in BOTH modes (generic loop, so a new template needs no new control
code). Also covers generation-mode leakage (GENERATION_MODE_*), token policy (TOKEN_*), the retrieval pin and the
wrapper gate (synthetic height mutations fed to extraction/wrapper_gate.gate()). Mutations are built from this repo's own contracts; each one must
produce an error (or, for warn-severity rules, a warning) naming the specific rule it targets. A mutation
that cannot be built for this repo is reported as SKIPPED with the reason -- never silently dropped.
Usage: python3 adversarial_test.py"""
import copy, glob, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.dirname(HERE)
REPO = os.path.dirname(SCHEMA)
spec_ = importlib.util.spec_from_file_location("semantic_validate", os.path.join(SCHEMA, "semantic_validate.py"))
sv = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(sv)

SECS = sv.contracts()
TEMPLATES = sv.load("templates/templates.json")["templates"]
GRAPH = {r["id"]: r for r in sv.load("compatibility/graph.json")["rules"]}
VERSION = sv.load("schema/pagespec.schema.json")["properties"]["pageSpecVersion"]["const"]
NONE = {"pattern": "none", "reducedMotionFallback": "disable-animation"}


def minimal_node(sid, motion=None):
    f = SECS[sid]["content"]["fields"]
    content = {}
    if f.get("heading", {}).get("required"): content["heading"] = "Sample"
    if f.get("subheading", {}).get("required"): content["subheading"] = "Sample"
    if f.get("body", {}).get("required"): content["body"] = ["Sample"]
    if f.get("ctas", {}).get("required"): content["ctas"] = [{"label": "Go"}]
    if f.get("items", {}).get("required"): content["items"] = [{"title": "Sample"}]
    return {"type": sid, "content": content, "motion": dict(motion or NONE)}


def control_for(t, mode="clone"):
    return {"pageSpecVersion": VERSION, "mode": mode, "template": t["id"], "route": (t.get("routes") or ["/sample"])[0] if mode == "clone" else "/sample",
            "nodes": [minimal_node(n["section"]) for n in t["nodes"]]}


def main():
    example = sv.load("schema/example.pagespec.json")
    tmpl = {t["id"]: t for t in TEMPLATES}[example["template"]]
    tseq = [n["section"] for n in tmpl["nodes"]]
    types = [n["type"] for n in example["nodes"]]
    cases, skipped = [], []   # case: (label, spec, expect, needle) with expect in {"pass", "error", "warn"}
    cases.append(("control: bundled example", example, "pass", None))
    for t in TEMPLATES:
        cases.append((f"control: minimal {t['id']} (clone)", control_for(t), "pass", None))
        cases.append((f"control: minimal {t['id']} (generation)", control_for(t, "generation"), "pass", None))
    gen_examples = {os.path.basename(p): json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(SCHEMA, "examples", "*.pagespec.json")))}
    for name, g in gen_examples.items():
        cases.append((f"control: generation example {name}", g, "pass", None))

    def mut(label, fn, needle, expect="error", why_not=None):
        if why_not:
            skipped.append(f"{label}: {why_not}"); return
        s = copy.deepcopy(example); fn(s); cases.append((label, s, expect, needle))

    first_idx = lambda pred: next((i for i, n in enumerate(example["nodes"]) if pred(n)), None)

    # ---- schema layer
    mut("wrong template enum", lambda s: s.__setitem__("template", "template.does-not-exist"), "schema: template")
    mut("missing required motion", lambda s: s["nodes"][0].pop("motion"), "'motion' is a required property")
    mut("invented section type", lambda s: s["nodes"][0].__setitem__("type", "hero.invented-type"), "schema: nodes/0/type")
    mut("missing reducedMotionFallback", lambda s: s["nodes"][0]["motion"].pop("reducedMotionFallback"), "reducedMotionFallback")
    mut("invented motion field", lambda s: s["nodes"][0]["motion"].__setitem__("inventedAnimation", True), "inventedAnimation")
    mut("per-instance style override on a node", lambda s: s["nodes"][0].__setitem__("style", {"color": "#ff0000"}), "'style' was unexpected")
    mut("raw theme override at page level", lambda s: s.__setitem__("theme", {"color.text.primary": "#ff0000"}), "schema: theme")
    mut("wrong pageSpecVersion", lambda s: s.__setitem__("pageSpecVersion", "9.9.9"), "schema: pageSpecVersion")
    mut("unknown content field", lambda s: s["nodes"][0]["content"].__setitem__("inventedField", "x"), "'inventedField' was unexpected")
    cta = first_idx(lambda n: "ctas" in SECS[n["type"]]["content"]["fields"])
    mut("link to a live external URL", lambda s: s["nodes"][cta]["content"].__setitem__("ctas", [{"label": "Go", "href": "https://www.exante.app/contact/sales"}]),
        "does not match", why_not=None if cta is not None else "no section with ctas")
    img = first_idx(lambda n: "images" in SECS[n["type"]]["content"]["fields"])
    mut("invented assetRole", lambda s: s["nodes"][img]["content"].__setitem__("images", [{"assetRole": "invented-role"}]),
        "invented-role", why_not=None if img is not None else "no section with images")
    if img is not None:
        role = (SECS[example["nodes"][img]["type"]]["content"]["fields"]["images"].get("assetRoles") or ["content-image"])[0]
        mut("alt text over its word budget", lambda s: s["nodes"][img]["content"].__setitem__("images", [{"assetRole": role, "alt": " ".join(["w"] * 17)}]), "alt has 17 words")

    # ---- asset-role closed-set proofs: a must-not-fabricate role cannot be swapped out for
    # content-image (or vice versa) just because both are "an image role" in the abstract. The
    # check in semantic_validate.py is a plain per-section allowlist (role in/out of the list for
    # that section's images field), not role-aware, so each proof targets the specific section
    # whose allowlist is meant to exclude content-image -- not the schema's generic enum.
    def mut_role_swap(label, tmpl_id, section_id, forbidden_role):
        tmpl = {t["id"]: t for t in TEMPLATES}.get(tmpl_id)
        if tmpl is None:
            skipped.append(f"{label}: no template '{tmpl_id}' in this repo"); return
        if section_id not in [n["section"] for n in tmpl["nodes"]]:
            skipped.append(f"{label}: '{section_id}' is not part of {tmpl_id}"); return
        allowed = SECS[section_id]["content"]["fields"].get("images", {}).get("assetRoles") or []
        if forbidden_role in allowed:
            skipped.append(f"{label}: '{forbidden_role}' is itself allowed on {section_id} (nothing to prove)"); return
        spec = control_for(tmpl)
        ni = next(i for i, n in enumerate(spec["nodes"]) if n["type"] == section_id)
        spec["nodes"][ni]["content"]["images"] = [{"assetRole": forbidden_role}]
        cases.append((label, spec, "error", f"role '{forbidden_role}' not used by this section"))

    # (a) a content-image cannot stand in for integration-logo on the integrations grid
    mut_role_swap("content-image cannot substitute for integration-logo", "template.home",
                  "features.integrations-section", "content-image")
    # (b) a role that is not avatar/content-image cannot be smuggled into the testimonials
    # section's image slot. (content-image itself is legitimately allowed there alongside avatar
    # -- this section mixes real headshots with decorative imagery -- so the proof that matters is
    # the closed allowlist, not content-image specifically; integration-logo is a real excluded role.)
    mut_role_swap("a role outside its allowlist cannot substitute for avatar", "template.customers",
                  "proof.testimonials-section", "integration-logo")
    # (c) compliance-badge is pinned must-not-fabricate but no measured section on this site uses
    # a certification graphic, so there is no section whose allowlist is "supposed to" include it.
    # The protection that matters is the converse of (a)/(b): compliance-badge must not be
    # insertable into ANY section's images field just because it exists in the role catalog -- the
    # allowlist is closed per section, not "any pinned role is fine anywhere". Proven against every
    # section in this repo that has an images field.
    img_secs = [sid for sid, c in SECS.items() if "images" in c["content"]["fields"]]
    bad = next((sid for sid in sorted(img_secs) if "compliance-badge" not in (SECS[sid]["content"]["fields"]["images"].get("assetRoles") or [])), None)
    if bad is None:
        skipped.append("compliance-badge cannot substitute for a section's own role: every section with images already allows it")
    else:
        owner = next((t for t in TEMPLATES if bad in [n["section"] for n in t["nodes"]]), None)
        if owner is None:
            skipped.append(f"compliance-badge cannot substitute for a section's own role: no template contains {bad}")
        else:
            spec = control_for(owner)
            ni = next(i for i, n in enumerate(spec["nodes"]) if n["type"] == bad)
            spec["nodes"][ni]["content"]["images"] = [{"assetRole": "compliance-badge"}]
            cases.append((f"compliance-badge cannot substitute for {bad}'s own role", spec, "error",
                          "role 'compliance-badge' not used by this section"))

    # ---- structural layer (template cross-reference)
    once = [i for i, tn in enumerate(tmpl["nodes"]) if tn["required"] and tseq.count(tn["section"]) == 1]
    mut("removed mandatory section", lambda s: s["nodes"].pop(types.index(tseq[once[0]])), "missing",
        why_not=None if once and len(types) > 1 else "no required section that occurs once")
    if len(types) >= 2 and types[0] != types[1]:
        mut("first two sections swapped", lambda s: s["nodes"].__setitem__(slice(0, 2), [s["nodes"][1], s["nodes"][0]]), "out of order")
    else:
        skipped.append("first two sections swapped: fewer than two distinct leading sections")
    foreign = next((sid for sid in sorted(SECS) if sid not in tseq), None)
    mut("section from outside the template", lambda s: s["nodes"].insert(1, minimal_node(foreign)), "not part of template",
        why_not=None if foreign else "every section belongs to this template")
    other = next((t for t in TEMPLATES if t["id"] != tmpl["id"] and [n["section"] for n in t["nodes"]] != tseq), None)
    mut("declared template contradicts the nodes", lambda s: s.__setitem__("template", other["id"]), "template:",
        why_not=None if other else "only one template in this repo")

    # ---- graph layer: each rule must fire by its own id
    one = first_idx(lambda n: SECS[n["type"]]["constraints"].get("onePerPage"))
    mut("SECTION_PER_PAGE_LIMITS: one-per-page section duplicated", lambda s: s["nodes"].insert(one + 1, copy.deepcopy(s["nodes"][one])),
        "SECTION_PER_PAGE_LIMITS", why_not=None if one is not None else "no one-per-page section")
    fb = GRAPH["SHELL_MUST_BE_FIRST"]["sections"]; fi = first_idx(lambda n: n["type"] in fb)
    mut("SHELL_MUST_BE_FIRST: first section moved to the end", lambda s: s["nodes"].append(s["nodes"].pop(fi)), "SHELL_MUST_BE_FIRST",
        why_not=None if fi is not None and len(types) > 1 else "no mustBeFirst section in the example")
    lb = GRAPH["SHELL_MUST_BE_LAST"]["sections"]; li = next((i for i in range(len(types) - 1, -1, -1) if types[i] in lb), None)
    mut("SHELL_MUST_BE_LAST: last section moved to the front", lambda s: s["nodes"].insert(0, s["nodes"].pop(li)), "SHELL_MUST_BE_LAST",
        why_not=None if li is not None and len(types) > 1 else "no mustBeLast section in the example")
    nc = GRAPH["NO_CONSECUTIVE_SAME_SECTION"]["sections"]; ni = first_idx(lambda n: n["type"] in nc)
    mut("NO_CONSECUTIVE_SAME_SECTION (warn)", lambda s: s["nodes"].insert(ni + 1, copy.deepcopy(s["nodes"][ni])), "NO_CONSECUTIVE_SAME_SECTION", "warn",
        why_not=None if ni is not None else "no section is restricted from repeating back-to-back")
    allowed = {tuple(p) for p in GRAPH["NO_ADJACENT_SAME_CATEGORY"].get("exceptions", [])}
    pair = next(((a, b) for a in sorted(SECS) for b in sorted(SECS) if a != b and SECS[a]["category"] == SECS[b]["category"] and (a, b) not in allowed), None)
    mut("NO_ADJACENT_SAME_CATEGORY (warn)", lambda s: s["nodes"].extend([minimal_node(pair[0]), minimal_node(pair[1])]), "NO_ADJACENT_SAME_CATEGORY", "warn",
        why_not=None if pair else "no two sections share a category")
    budget = GRAPH["MOTION_BUDGET"]["max"]
    animated = next((sid for sid in sorted(SECS) if [p for p in SECS[sid]["motion"]["allowedPatterns"] if p != "none"]), None)
    if animated:
        pat = [p for p in SECS[animated]["motion"]["allowedPatterns"] if p != "none"][0]
        mut("MOTION_BUDGET (warn)", lambda s: s["nodes"].extend([minimal_node(animated, {"pattern": pat, "reducedMotionFallback": "disable-animation"}) for _ in range(budget + 1)]), "MOTION_BUDGET", "warn")
    else:
        skipped.append("MOTION_BUDGET: no section allows an animated pattern")
    heroes = sorted(sid for sid, c in SECS.items() if c["category"] == "HERO")
    hi = first_idx(lambda n: SECS[n["type"]]["category"] == "HERO")
    extra = next((h for h in heroes if hi is None or h != types[hi]), None)
    # a second HERO: another HERO type when the repo has one, else the same hero twice (still two HERO sections)
    host = next((t for t in TEMPLATES if any(SECS[n["section"]]["category"] == "HERO" for n in t["nodes"]) and t["id"] not in GRAPH["ONE_HERO_PER_PAGE"]["exceptions"]), None)
    if host is None:
        skipped.append("ONE_HERO_PER_PAGE: no template with a HERO section")
    else:
        spec = control_for(host); k = next(i for i, n in enumerate(spec["nodes"]) if SECS[n["type"]]["category"] == "HERO")
        spec["nodes"].insert(k + 1, minimal_node(extra or spec["nodes"][k]["type"]))
        cases.append(("ONE_HERO_PER_PAGE: a second HERO section", spec, "error", "ONE_HERO_PER_PAGE"))

    # ---- runtime budgets
    wn = next(((i, k) for i, n in enumerate(example["nodes"]) for k in ("heading", "subheading") if k in n["content"]), None)
    if wn:
        i, k = wn; mw = SECS[types[i]]["content"]["fields"][k]["maxWords"]
        mut(f"maxWords overflow on a {k}", lambda s: s["nodes"][i]["content"].__setitem__(k, " ".join(["word"] * (mw + 1))), f"{k} has {mw + 1} words")
    else:
        skipped.append("maxWords overflow: example has no heading")
    itn = first_idx(lambda n: n["content"].get("items"))
    if itn is not None:
        tw = SECS[types[itn]]["content"]["fields"]["items"]["titleMaxWords"]
        mut("maxWords overflow on an item title", lambda s: s["nodes"][itn]["content"]["items"][0].__setitem__("title", " ".join(["word"] * (tw + 1))), "title has")
    noanim = first_idx(lambda n: SECS[n["type"]]["motion"]["allowedPatterns"] == ["none"])
    mut("motion pattern not allowed for its section", lambda s: s["nodes"][noanim]["motion"].__setitem__("pattern", "scroll-linked"), "not allowed",
        why_not=None if noanim is not None else "every section allows animation")

    generation_cases(cases, skipped, gen_examples, example)
    token_cases(cases, gen_examples)
    retrieval_cases(cases, skipped, gen_examples)

    ok = fail = 0
    for label, spec, expect, needle in cases:
        if callable(spec):  # in-process cases that patch a cached contract and restore it
            errors, warnings = spec()
            good = (not errors) if expect == "pass" else any(needle in e for e in (errors if expect == "error" else warnings))
            if good: ok += 1
            else:
                fail += 1; print(f"FAIL: {label}: expected {expect} containing '{needle}'; errors={errors[:3]} warnings={warnings[:3]}")
            continue
        errors, warnings = sv.check(spec)
        if expect == "pass": good = not errors
        elif expect == "error": good = any(needle in e for e in errors)
        else: good = any(needle in w for w in warnings)
        if good: ok += 1
        else:
            fail += 1
            print(f"FAIL: {label}: expected {expect}" + (f" containing '{needle}'" if needle else "") + f"; errors={errors[:3]} warnings={warnings[:3]}")
    gok, gfail = gate_cases()
    ok += gok; fail += gfail
    for s_ in skipped: print("SKIPPED:", s_)
    n_ctrl = sum(1 for c in cases if c[2] == "pass")
    print(f"adversarial: {ok} passed, {fail} failed ({n_ctrl} controls, {len(cases) - n_ctrl} PageSpec mutations, {gok + gfail} wrapper-gate cases, {len(skipped)} skipped as not applicable)")
    sys.exit(1 if fail else 0)


# ---------------------------------------------------------------- generation-mode leakage (R1, R2, R4, R5)
REAL_HERO = "From proactive outreach to rapid issue resolution, Exante is the extra set of hands that gets you sent → paid on time, every time."
REAL_QUOTE = "Our collections went from reactive chasing to automated, proactive and consistent flow. In just three months, we eliminated overdue invoices."


def _node(spec, sid):
    return next(i for i, n in enumerate(spec["nodes"]) if n["type"] == sid)


def generation_cases(cases, skipped, gens, clone_example):
    g = gens.get("example.generated.marketing.pagespec.json")
    if g is None:
        skipped.append("generation leakage: no marketing generation example"); return
    hero = _node(g, "hero.hero-section"); foot = len(g["nodes"]) - 1

    def mut(label, fn, needle):
        s = copy.deepcopy(g); fn(s); cases.append((label, s, "error", needle))
    H = lambda s: s["nodes"][hero]["content"]
    mut("mode missing", lambda s: s.pop("mode"), "'mode' is a required property")
    mut("mode outside the closed enum", lambda s: s.__setitem__("mode", "reference"), "schema: mode")
    mut("GENERATION_MODE_BRAND: source brand in a heading", lambda s: H(s).__setitem__("heading", "Meet Exante today"), "GENERATION_MODE_BRAND")
    mut("GENERATION_MODE_BRAND: zero-width split brand", lambda s: H(s).__setitem__("heading", "Meet Ex​ante today"), "GENERATION_MODE_BRAND")
    mut("GENERATION_MODE_BRAND: full-width brand (NFKC)", lambda s: H(s).__setitem__("heading", "Meet Ｅｘａｎｔｅ today"), "GENERATION_MODE_BRAND")
    mut("GENERATION_MODE_BRAND: legacy template brand (Vectura)", lambda s: H(s).__setitem__("body", ["Built by the Vectura team."]), "GENERATION_MODE_BRAND")
    mut("GENERATION_MODE_BRAND: source CTA 'Try Exante'", lambda s: H(s).__setitem__("ctas", [{"label": "Try Exante", "href": "/talk"}]), "GENERATION_MODE_BRAND")
    mut("GENERATION_MODE_BRAND: real wordmark role in the footer", lambda s: s["nodes"][foot]["content"].__setitem__("images", [{"assetRole": "logo"}]), "GENERATION_MODE_BRAND")
    mut("GENERATION_MODE_PERSON: real team member named", lambda s: H(s).__setitem__("body", ["Led by Giedrius Daubaris since day one."]), "GENERATION_MODE_PERSON")
    mut("GENERATION_MODE_PERSON: real testimonial author", lambda s: H(s).__setitem__("body", ["Justina Ramoskaite loves it."]), "GENERATION_MODE_PERSON")
    mut("GENERATION_MODE_PERSON: real-photo avatar role", lambda s: s["nodes"][_node(s, "proof.clients-section")]["content"].__setitem__("images", [{"assetRole": "avatar"}]), "GENERATION_MODE_PERSON")
    mut("GENERATION_MODE_CUSTOMER: real integration partners", lambda s: H(s).__setitem__("body", ["Syncs with QuickBooks and Xero overnight."]), "GENERATION_MODE_CUSTOMER")
    mut("GENERATION_MODE_CUSTOMER: real customer-logo role", lambda s: s["nodes"][_node(s, "proof.clients-section")]["content"].__setitem__("images", [{"assetRole": "customer-logo"}]), "GENERATION_MODE_CUSTOMER")
    mut("GENERATION_MODE_CUSTOMER: real integration-logo role", lambda s: s["nodes"][_node(s, "features.integrations-section")]["content"].__setitem__("images", [{"assetRole": "integration-logo"}]), "GENERATION_MODE_CUSTOMER")
    mut("GENERATION_MODE_CLAIM: source statistic reused", lambda s: H(s).__setitem__("body", ["Teams improved collection speed by 30%+ in a quarter."]), "GENERATION_MODE_CLAIM")
    mut("GENERATION_MODE_COPY: source hero sentence", lambda s: H(s).__setitem__("body", [REAL_HERO.replace("Exante", "Tallyfern")]), "GENERATION_MODE_COPY")
    mut("GENERATION_MODE_COPY: curly quotes / dashes do not hide copy", lambda s: H(s).__setitem__("body", ["From proactive outreach — to rapid issue resolution, it’s the extra set of hands."]), "GENERATION_MODE_COPY")
    mut("GENERATION_MODE_COPY: real testimonial (review) text", lambda s: H(s).__setitem__("body", [REAL_QUOTE[:180]]), "GENERATION_MODE_COPY")
    mut("GENERATION_MODE_URL: source mailbox in copy", lambda s: H(s).__setitem__("body", ["Write to team@exante.app any time."]), "GENERATION_MODE_URL")
    mut("GENERATION_MODE_URL: non-placeholder domain", lambda s: H(s).__setitem__("body", ["Docs at https://docs.acme.com/start."]), "GENERATION_MODE_URL")
    mut("GENERATION_MODE_URL: source asset CDN host", lambda s: H(s).__setitem__("body", ["See framerusercontent.com/images/x for the demo."]), "GENERATION_MODE_URL")
    mut("GENERATION_MODE_EMBED: live embed endpoint", lambda s: H(s).__setitem__("body", ["Embed https://framer.com/edit here."]), "GENERATION_MODE_EMBED")
    mut("GENERATION_MODE_ASSET: registered source file reused", lambda s: H(s).__setitem__("images", [{"assetRole": "generated-illustration", "assetRef": "_ext/framerusercontent.com/images/ecgwLxQMKk2bXTSZ21R1kisJ0__57a634cb.jpg"}]), "GENERATION_MODE_ASSET")
    mut("GENERATION_MODE_SCREENSHOT: source hero-image role", lambda s: H(s).__setitem__("images", [{"assetRole": "hero-image"}]), "GENERATION_MODE_SCREENSHOT")
    mut("GENERATION_MODE_ASSET: compliance badge in generation", lambda s: s["nodes"][foot]["content"].__setitem__("images", [{"assetRole": "compliance-badge"}]), "GENERATION_MODE_ASSET")
    mut("GENERATION_MODE_COPY: source route slug", lambda s: s.__setitem__("route", "/blog/agents-that-learn-how-you-work"), "GENERATION_MODE_COPY")
    skipped.append("store mark / store URL leakage: the source has no App Store / Play / TestFlight marks or links (grep of src/ finds none), so there is nothing source-specific to leak; non-placeholder URLs are still rejected by GENERATION_MODE_URL")
    # a registry edit cannot loosen availability: the validator reads only its pinned table
    reg = sv.load("assets/asset-roles.json") if os.path.isfile(os.path.join(REPO, "assets/asset-roles.json")) else None
    def registry_loosened():
        saved = copy.deepcopy(reg["roles"]["avatar"]); reg["roles"]["avatar"]["availability"] = "generation-safe"
        try:
            s = copy.deepcopy(g); s["nodes"][_node(s, "proof.clients-section")]["content"]["images"] = [{"assetRole": "avatar"}]
            return sv.check(s)
        finally:
            reg["roles"]["avatar"] = saved
    if reg: cases.append(("availability pin: registry edited to generation-safe is ignored", registry_loosened, "error", "GENERATION_MODE_PERSON"))
    # the clone example (real content) is valid in clone mode but is rejected the moment it claims to be generation
    flipped = copy.deepcopy(clone_example); flipped["mode"] = "generation"
    for rule in ("GENERATION_MODE_BRAND", "GENERATION_MODE_PERSON", "GENERATION_MODE_COPY", "GENERATION_MODE_SCREENSHOT"):
        cases.append((f"clone example relabelled generation is caught by {rule}", flipped, "error", rule))


# ---------------------------------------------------------------- token policy (R10)
def token_cases(cases, gens):
    g = gens.get("example.generated.marketing.pagespec.json")
    if g is None: return
    hero = _node(g, "hero.hero-section")
    def mut(label, tokens, needle, theme=None):
        s = copy.deepcopy(g); s["nodes"][hero]["tokens"] = tokens
        if theme: s["theme"] = theme
        cases.append((label, s, "error", needle))
    mut("TOKEN_RAW_VALUE: raw hex colour", {"surface": "#1e211e"}, "TOKEN_RAW_VALUE")
    mut("TOKEN_RAW_VALUE: raw rgb() colour", {"text": "rgb(255,255,255)"}, "TOKEN_RAW_VALUE")
    mut("TOKEN_UNKNOWN: invented token id", {"surface": "surface.brand"}, "TOKEN_UNKNOWN")
    mut("TOKEN_ARBITRARY_SPACING: raw px gap", {"gap": "24px"}, "TOKEN_ARBITRARY_SPACING")
    mut("TOKEN_ARBITRARY_SPACING: foundation spacing step", {"paddingTop": "space.96"}, "TOKEN_ARBITRARY_SPACING")
    mut("TOKEN_UNSUPPORTED_FONT: font not in the catalog", {"fontFamily": "Comic Sans MS"}, "TOKEN_UNSUPPORTED_FONT")
    mut("TOKEN_NOT_REFERENCEABLE: foundation colour", {"surface": "color.neutral.01"}, "TOKEN_NOT_REFERENCEABLE")
    mut("TOKEN_SLOT_MISMATCH: layout token as a colour", {"surface": "layout.gutter"}, "TOKEN_SLOT_MISMATCH")
    mut("TOKEN_THEME_MISMATCH: theme that is not schema-validated", {"surface": "surface.inverse"}, "TOKEN_THEME_MISMATCH", theme="dark")
    mut("token slot outside the closed set", {"shadow": "elevation.default"}, "'shadow' was unexpected")


# ---------------------------------------------------------------- retrieval eligibility (R8)
def retrieval_cases(cases, skipped, gens):
    c = gens.get("example.generated.contact.pagespec.json")
    if c is None:
        skipped.append("retrieval: no contact generation example"); return
    w = _node(c, "content.white")
    s = copy.deepcopy(c); s["nodes"][w]["retrievalEligible"] = True
    cases.append(("RETRIEVAL_PIN: utility layer flipped eligible at node level", s, "error", "RETRIEVAL_PIN"))
    s = copy.deepcopy(c); s["nodes"][_node(s, "hero.main")]["retrievalEligible"] = False
    cases.append(("RETRIEVAL_PIN: content section marked ineligible", s, "error", "RETRIEVAL_PIN"))
    secs = sv.contracts()
    def contract_flip(sid, val):
        def run():
            saved = secs[sid].get("retrievalEligible"); secs[sid]["retrievalEligible"] = val
            try: return sv.check(c)
            finally: secs[sid]["retrievalEligible"] = saved
        return run
    cases.append(("RETRIEVAL_PIN: utility contract flipped eligible", contract_flip("content.white", True), "error", "RETRIEVAL_PIN"))
    cases.append(("RETRIEVAL_PIN: content contract marked ineligible", contract_flip("hero.main", False), "error", "RETRIEVAL_PIN"))


# ---------------------------------------------------------------- wrapper gate (R9)
def gate_cases():
    spec = importlib.util.spec_from_file_location("wrapper_gate", os.path.join(REPO, "extraction", "wrapper_gate.py"))
    wg = importlib.util.module_from_spec(spec); spec.loader.exec_module(wg)
    led, secs, wl = wg.load_inputs(REPO)
    ok = fail = 0
    def run(label, mutate, expect, needle):
        nonlocal ok, fail
        l2, w2 = copy.deepcopy(led), copy.deepcopy(wl)
        mutate(l2, w2)
        e, w = wg.gate(l2, secs, w2)
        good = (not e) if expect == "pass" else any(needle in x for x in (e if expect == "error" else w))
        if good: ok += 1
        else: fail += 1; print(f"FAIL: wrapper gate: {label}: expected {expect} '{needle}'; errors={e[:2]} warnings={w[:2]}")
    home = "/"
    def hero(px):
        def f(l, w):
            s = next(x for x in l["sectionHeights"]["routes"][home]["sections"] if x["id"] == "hero.hero-section"); s["heightPx"] = px
        return f
    def share(frac):
        def f(l, w):
            r = l["sectionHeights"]["routes"][home]; s = next(x for x in r["sections"] if x["id"] == "features.key-features-section")
            s["heightPx"] = int(r["pageHeightPx"] * frac)
        return f
    def wl_entry(**kw):
        def f(l, w):
            share(0.65)(l, w)
            e = {"route": home, "section": "features.key-features-section", "reviewedBy": "design-repo agent (agent attestation, not a human sign-off)",
                 "justification": "Reviewed: one long feature tour that cannot be split further.", "maxHeightPx": 9000}
            e.update(kw); w["entries"] = [x for x in [e] if x is not None]
        return f
    run("control: the real measurements pass", lambda l, w: None, "pass", None)
    run("HERO 1900px warns", hero(1900), "warn", "HERO hero.hero-section")
    run("HERO 3100px errors", hero(3100), "error", "> 3000px")
    run("section holding 55% of a page warns", share(0.55), "warn", "> 50%")
    run("section holding 65% of a page errors", share(0.65), "error", "> 60%")
    run("whitelisted 65% section passes (still warns)", wl_entry(), "warn", "> 50%")
    run("whitelist entry without justification", wl_entry(justification="short"), "error", "justification")
    run("whitelist agent reviewer without the attestation phrase", wl_entry(reviewedBy="design-repo agent"), "error", "agent attestation")
    run("whitelist entry over its cap", wl_entry(maxHeightPx=100), "error", "over its cap")
    run("stale whitelist entry", lambda l, w: w.__setitem__("entries", [{"route": home, "section": "cta.another-cta", "reviewedBy": "x (agent attestation, not a human sign-off)", "justification": "x" * 40, "maxHeightPx": 9000}]), "error", "stale")
    run("missing measurement for a route", lambda l, w: l["sectionHeights"]["routes"].pop(home), "error", "no measured section heights")
    run("measured at the wrong viewport", lambda l, w: l["sectionHeights"]["viewport"].__setitem__("width", 1280), "error", "must be 1440px")
    run("no sectionHeights at all", lambda l, w: l.pop("sectionHeights"), "error", "missing measurement")
    return ok, fail


if __name__ == "__main__":
    main()
