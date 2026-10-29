#!/usr/bin/env python3
"""Proves verify_all.py actually CATCHES drift: copies this design repo to a scratch folder, injects one defect
at a time, and requires verify_all.py to fail with the matching message. The unmodified copy must pass (a
check that rejects everything is broken too).

The package's own src/ and public/ (the runnable clone, the citation evidence) are symlinked read-only into
each scratch package, so citation / asset / rebuild checks run for real. Injections that need them are skipped
(and reported) when design-repo/ is run alone.

Usage: python3 prove_drift.py [--scratch DIR]     (DIR defaults to a fresh OS temp folder; it is emptied after)
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG = os.path.dirname(REPO)
HAS_SRC = os.path.isfile(os.path.join(PKG, "src", "routes.js")) and os.path.isdir(os.path.join(PKG, "public"))


def jload(p): return json.load(open(p, encoding="utf-8"))
def jsave(p, d): open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
def P(r, rel): return os.path.join(r, rel)
def edit(r, rel, fn):
    p = P(r, rel); d = jload(p); out = fn(d); jsave(p, d); return out
def text_edit(r, rel, old, new):
    p = P(r, rel); s = open(p, encoding="utf-8").read()
    if old not in s: raise RuntimeError(f"{rel}: anchor text not found")
    open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))


def first_section(r):
    return sorted(f for f in os.listdir(P(r, "sections")) if f.endswith(".json"))[0]


def inj_phantom(r): edit(r, "tokens/llm/component-allowlist.json", lambda d: d["sections"].append("content.phantom-section"))
def inj_orphan(r):
    d = jload(P(r, "sections/" + first_section(r))); d["id"] = "content.orphan-section"; jsave(P(r, "sections/content.orphan-section.json"), d)
def inj_count(r): edit(r, "registry.manifest.json", lambda d: d["counts"].__setitem__("sections", d["counts"]["sections"] + 1))
def inj_readme(r):
    p = P(r, "README.md"); s = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(re.sub(r"^- Templates: (\d+)$", lambda m: f"- Templates: {int(m.group(1)) + 7}", s, flags=re.M))
def _first(d): return d["routes"][0]["sections"][1]
def inj_cite_range(r): edit(r, "extraction/measured-values.json", lambda d: _first(d).__setitem__("lines", [999999, 1000000]))
def inj_cite_wrong(r): edit(r, "extraction/measured-values.json", lambda d: _first(d).__setitem__("anchor", "anchor-that-is-not-on-this-line"))
def inj_cite_usage(r): edit(r, "extraction/measured-values.json", lambda d: _first(d)["usage"].__setitem__("line", 1))
def inj_cite_other(r):
    led = jload(P(r, "extraction/measured-values.json"))
    ents = [(x["id"], f"{x['file']}:{x['lines'][0]}-{x['lines'][1]}") for rt in led["routes"] for x in rt["sections"]]
    a = ents[0]; b = next(e for e in ents if e[0] != a[0])
    edit(r, f"sections/{a[0]}.json", lambda d: d["evidence"].__setitem__("measuredFrom", [b[1]]))
def inj_source_range(r): edit(r, "sections/hero.hero-section.json", lambda d: d["source"].__setitem__("lines", [1, 2]))
def inj_source_id(r): edit(r, "sections/hero.hero-section.json", lambda d: d["source"].__setitem__("id", "hero.hero-section"))
def inj_semantic_id(r): edit(r, "sections/hero.hero-section.json", lambda d: d["semantic"].__setitem__("id", "hero.something-else"))
def inj_allow_version(r): edit(r, "tokens/llm/component-allowlist.json", lambda d: d.__setitem__("version", str(d["version"]) + "-drift"))
def inj_pinned(r): edit(r, "assets/asset-roles.json", lambda d: d["roles"]["avatar"].__setitem__("generationPolicy", "may-generate-new"))
def inj_availability(r): edit(r, "assets/asset-roles.json", lambda d: d["roles"]["avatar"].__setitem__("availability", "generation-safe"))
def inj_logo_safe(r): edit(r, "assets/asset-roles.json", lambda d: d["roles"]["logo"].__setitem__("availability", "generation-safe"))
def inj_remove_pin(r):  # drop a role from the validator's pinned table only
    text_edit(r, "schema/semantic_validate.py", '"avatar": "blocked-for-generation", ', "")
def inj_pin_both(r):  # loosen BOTH code pins together; the registry still disagrees
    text_edit(r, "schema/semantic_validate.py", '"avatar": "blocked-for-generation", ', '"avatar": "generation-safe", ')
    text_edit(r, "extraction/verify_all.py", '"avatar": "blocked-for-generation", ', '"avatar": "generation-safe", ')
def inj_substitutes(r): edit(r, "assets/asset-roles.json", lambda d: d["roles"]["hero-image"].__setitem__("generationSafeSubstitutes", []))
def inj_retrieval_contract(r): edit(r, "sections/content.white.json", lambda d: (d.__setitem__("retrievalEligible", True), d.pop("retrievalIneligibleReason")))
def inj_retrieval_both(r):  # flip contract AND allowlist together: the code pin still disagrees
    inj_retrieval_contract(r); edit(r, "tokens/llm/component-allowlist.json", lambda d: d.__setitem__("retrievalIneligible", []))
def inj_retrieval_reason(r): edit(r, "sections/content.white.json", lambda d: d.__setitem__("retrievalIneligibleReason", "too short"))
def inj_runtime_ui(r): edit(r, "sections/cta.another-cta.json", lambda d: d.__setitem__("purpose", "A cookie consent banner pinned to the bottom of the viewport."))
def inj_contract_closed(r): edit(r, "sections/hero.hero-section.json", lambda d: d.__setitem__("inventedField", True))
def inj_abs(r): open(P(r, "README.md"), "a", encoding="utf-8").write("\nSource: " + "/" + "Users/someone/project\n")
def inj_entry(r): edit(r, "registry.manifest.json", lambda d: d["entryPoints"].__setitem__("tokenCatalog", "../ia.json"))
def inj_policy(r): edit(r, "tokens/llm/token-policy.json", lambda d: d["rawValueRestrictions"].__setitem__("typography-human-label", "forbidden"))
def inj_catalog(r): edit(r, "tokens/llm/token-catalog.json", lambda d: d["tokens"]["surface.default"].__setitem__("value", "rgb(1,2,3)"))
def inj_catalog_cat(r): edit(r, "tokens/llm/token-catalog.json", lambda d: d["categories"]["color"].append("surface.invented"))
def inj_token_file(r):  # a real token file changes; the catalog was not regenerated
    edit(r, "tokens/30-layout/layout.json", lambda d: d["tokens"].__setitem__("layout.newGap", {"$value": "{space.24}", "basis": "drift"}))
def inj_graph(r):
    def f(d):
        lim = next(x for x in d["rules"] if x["id"] == "SECTION_PER_PAGE_LIMITS")["limits"]; lim[sorted(lim)[0]] += 5
    edit(r, "compatibility/graph.json", f)
def inj_theme(r): edit(r, "tokens/themes/light.json", lambda d: d["resolves"].__setitem__(sorted(d["resolves"])[0], "rgb(1,2,3)"))
def inj_schema_enum(r): edit(r, "schema/pagespec.schema.json", lambda d: d["definitions"]["node"]["properties"]["type"]["enum"].append("hero.not-a-contract"))
def inj_schema_mode(r): edit(r, "schema/pagespec.schema.json", lambda d: d["required"].remove("mode"))
def inj_rule_kind(r): edit(r, "compatibility/graph.json", lambda d: d["rules"].append({"id": "UNIMPLEMENTED", "severity": "error", "kind": "notARealKind"}))
def inj_hero_exception(r):
    edit(r, "compatibility/graph.json", lambda d: next(x for x in d["rules"] if x["id"] == "ONE_HERO_PER_PAGE")["exceptions"].append("template.phantom-multi-hero"))
def inj_no_gen_example(r): os.remove(P(r, "schema/examples/example.generated.legal.pagespec.json"))
def inj_gen_example_leak(r):
    edit(r, "schema/examples/example.generated.marketing.pagespec.json", lambda d: d["nodes"][1]["content"].__setitem__("heading", "Exante for finance teams"))
def inj_family(r): edit(r, "templates/templates.json", lambda d: d["templates"][0].pop("family"))
def inj_heights_missing(r): edit(r, "extraction/measured-values.json", lambda d: d["sectionHeights"]["routes"].pop("/"))
def inj_heights_viewport(r): edit(r, "extraction/measured-values.json", lambda d: d["sectionHeights"]["viewport"].__setitem__("width", 1280))
def inj_hero_tall(r):
    edit(r, "extraction/measured-values.json", lambda d: d["sectionHeights"]["routes"]["/"]["sections"][1].__setitem__("heightPx", 3100))
def inj_whole_page(r):  # re-merge the decomposed legal body into one section height (the pre-0.2.0 state)
    def f(d):
        rt = d["sectionHeights"]["routes"]["/legal/terms-of-service"]
        k = next(i for i, s in enumerate(rt["sections"]) if s["id"] == "content.legal-clause")
        rt["sections"][k]["heightPx"] = int(rt["pageHeightPx"] * 0.87)
    edit(r, "extraction/measured-values.json", f)
def inj_whitelist(r):
    edit(r, "extraction/wrapper-whitelist.json", lambda d: d["entries"].append({"route": "/", "section": "hero.hero-section", "reviewedBy": "agent", "justification": "", "maxHeightPx": 1}))
def inj_gate_threshold(r): text_edit(r, "extraction/wrapper_gate.py", "HERO_WARN_PX, HERO_ERROR_PX = 1800, 3000", "HERO_WARN_PX, HERO_ERROR_PX = 180, 300")
def inj_policy_hash(r): edit(r, "registry.manifest.json", lambda d: d["designPolicy"].__setitem__("contentHash", "sha256:" + "0" * 64))
def inj_policy_enforced(r):  # an enforcedBy file changes; the contentHash was not recomputed
    edit(r, "compatibility/graph.json", lambda d: d.__setitem__("note", "edited after hashing"))
def inj_policy_ref(r): edit(r, "registry.manifest.json", lambda d: d["designPolicy"].__setitem__("ref", "policy/missing.json"))
def inj_policy_category(r): edit(r, "registry.manifest.json", lambda d: d.__setitem__("category", "consumer-app"))
def inj_ledger_route(r):  # the ledger forgets a route the clone serves
    def f(d):
        d["routes"] = [x for x in d["routes"] if x["route"] != "/contact/support"]
    edit(r, "extraction/measured-values.json", f)
def inj_asset_missing(r): edit(r, "assets/asset-roles.json", lambda d: d["assets"].append(dict(d["assets"][10], path="_ext/does-not-exist.png")))
def inj_asset_inclone(r):  # an asset the clone really ships is flagged absent
    def f(d):
        a = next(x for x in d["assets"] if x["path"].startswith("_ext/") and x.get("inClone") is not False); a["inClone"] = False
    edit(r, "assets/asset-roles.json", f)
def inj_inline_sha(r): edit(r, "assets/asset-roles.json", lambda d: next(x for x in d["assets"] if x.get("inlineSource"))["inlineSource"].__setitem__("sha256", "0" * 64))
def inj_identity(r): edit(r, "schema/source-identity.json", lambda d: d["people"].pop())
def inj_pagespec_version(r): edit(r, "registry.manifest.json", lambda d: d.__setitem__("pageSpecVersion", "0.1.0"))


INJECTIONS = [
    ("phantom allowlist entry", inj_phantom, "has no contract file"),
    ("orphan section contract", inj_orphan, "has no allowlist entry"),
    ("wrong manifest count", inj_count, "manifest counts.sections"),
    ("stale README count", inj_readme, "README count 'Templates'"),
    ("out-of-range citation", inj_cite_range, "range exceeds the file", "src"),
    ("in-range citation pointing at the wrong element", inj_cite_wrong, "does not contain the cited element", "src"),
    ("usage line that does not render the component", inj_cite_usage, "does not render", "src"),
    ("contract citing another section's range", inj_cite_other, "points at"),
    ("R7 source range moved off its element", inj_source_range, "source", "src"),
    ("R7 source.id equal to the contract id", inj_source_id, "source.id must name"),
    ("R7 semantic.id differing from the contract id", inj_semantic_id, "semantic.id must equal"),
    ("allowlistVersion drift", inj_allow_version, "allowlistVersion drift"),
    ("pageSpecVersion drift", inj_pagespec_version, "pageSpecVersion drift"),
    ("pinned asset policy changed to a different valid value", inj_pinned, "pinned asset role 'avatar'"),
    ("registry availability loosened (avatar -> generation-safe)", inj_availability, "PINNED_AVAILABILITY: asset role 'avatar'"),
    ("real logo made generation-safe in the registry", inj_logo_safe, "PINNED_AVAILABILITY: asset role 'logo'"),
    ("pin removed from the validator only", inj_remove_pin, "PINNED_AVAILABILITY in semantic_validate.py differs"),
    ("both code pins loosened together", inj_pin_both, "PINNED_AVAILABILITY: asset role 'avatar'"),
    ("clone-only role without substitutes", inj_substitutes, "no generationSafeSubstitutes"),
    ("utility contract flipped retrieval-eligible", inj_retrieval_contract, "retrieval pin"),
    ("contract + allowlist flipped together", inj_retrieval_both, "retrieval pin"),
    ("ineligible reason under 30 characters", inj_retrieval_reason, "section-contract.schema.json"),
    ("runtime-UI-looking section not pinned", inj_runtime_ui, "looks like runtime/utility UI"),
    ("section contract not closed", inj_contract_closed, "section-contract.schema.json"),
    ("absolute path leak", inj_abs, "absolute path"),
    ("entryPoint escaping design-repo", inj_entry, "entryPoints.tokenCatalog"),
    ("policy category not in catalog", inj_policy, "rawValueRestrictions"),
    ("catalog value edited by hand", inj_catalog, "token drift"),
    ("catalog lists an invented token", inj_catalog_cat, "token drift"),
    ("token file changed, catalog not regenerated", inj_token_file, "token drift"),
    ("graph limit drifted from contract", inj_graph, "SECTION_PER_PAGE_LIMITS"),
    ("theme resolution drift", inj_theme, "theme light"),
    ("schema enum drifted from contracts", inj_schema_enum, "derived file drift: schema/pagespec.schema.json"),
    ("schema no longer requires mode", inj_schema_mode, "derived file drift: schema/pagespec.schema.json"),
    ("graph rule the validator does not implement", inj_rule_kind, "not implemented"),
    ("ONE_HERO_PER_PAGE exception for a template that is not one", inj_hero_exception, "ONE_HERO_PER_PAGE exceptions"),
    ("template family without a generation example", inj_no_gen_example, "family 'legal' has no mode=generation example"),
    ("generation example leaking the source brand", inj_gen_example_leak, "GENERATION_MODE_BRAND"),
    ("template without a family", inj_family, "has no family"),
    ("section heights missing for a route", inj_heights_missing, "no measured section heights"),
    ("section heights measured at the wrong viewport", inj_heights_viewport, "must be 1440px"),
    ("HERO over 3000px", inj_hero_tall, "> 3000px"),
    ("whole-page legal body re-merged (87% of the page)", inj_whole_page, "> 60%"),
    ("whitelist entry without reviewer attestation/justification", inj_whitelist, "wrapper whitelist"),
    ("gate threshold edited in code", inj_gate_threshold, "> 300px"),
    ("policy contentHash wrong", inj_policy_hash, "designPolicy.contentHash"),
    ("enforcedBy file edited after hashing", inj_policy_enforced, "designPolicy.contentHash"),
    ("policy ref points at a missing file", inj_policy_ref, "designPolicy.ref"),
    ("manifest category contradicts the policy", inj_policy_category, "disagrees with policy isSaaS"),
    ("ledger drops a served route", inj_ledger_route, "served by src/routes.js but not mapped", "src"),
    ("asset registered but missing from public/", inj_asset_missing, "asset missing on disk", "src"),
    ("asset flagged inClone=false although shipped", inj_asset_inclone, "flagged inClone=false", "src"),
    ("inline mark sha256 drift", inj_inline_sha, "does not hash", "src"),
    ("source-identity registry edited by hand", inj_identity, "source-identity drift", "src"),
]


def run(r, full=False):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    if not full: env["VERIFY_SKIP_ADVERSARIAL"] = "1"  # injections target verify_all's own checks
    p = subprocess.run([sys.executable, P(r, "extraction/verify_all.py")], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--scratch", help="scratch directory (created if missing; emptied afterwards)")
    a = ap.parse_args()
    if a.scratch:
        os.makedirs(a.scratch, exist_ok=True); tmp = tempfile.mkdtemp(prefix="drift-", dir=a.scratch)
    else:
        tmp = tempfile.mkdtemp(prefix="drift-")
    try:
        def fresh():
            pkg = tempfile.mkdtemp(dir=tmp)
            shutil.copytree(REPO, P(pkg, "design-repo"), ignore=shutil.ignore_patterns("__pycache__"))
            if HAS_SRC:
                for d in ["src", "public"] + [f for f in os.listdir(PKG) if f in ("CLONE.md", "ROUTES.md", "ASSET_MANIFEST.md", "clone-manifest.json") or (f.startswith("CLONE_SPEC") and f.endswith(".md"))]:
                    os.symlink(os.path.join(PKG, d), P(pkg, d))  # the evidence the ledger/identity rebuilds read
            return P(pkg, "design-repo")
        ok = fail = skip = 0
        code, out = run(fresh(), full=True)
        if code == 0: ok += 1; print("  ok    control: unmodified copy is admitted" + ("" if HAS_SRC else " (design-repo alone)"))
        else: fail += 1; print("  FAIL  control: unmodified copy was rejected:\n" + out[-3000:])
        for inj in INJECTIONS:
            label, fn, needle = inj[:3]; needs = inj[3] if len(inj) > 3 else None
            if needs == "src" and not HAS_SRC:
                skip += 1; print(f"  skip  {label}: needs the package's src/ + public/ (design-repo shipped alone)"); continue
            r = fresh()
            try:
                fn(r)
            except Exception as e:  # a broken injection is a failure of this proof, not a silent pass
                fail += 1; print(f"  FAIL  {label}: the injection itself crashed: {e!r}"); continue
            code, out = run(r)
            if code != 0 and needle in out: ok += 1; print(f"  ok    caught: {label}")
            else: fail += 1; print(f"  FAIL  NOT caught: {label} (expected '{needle}')\n{out[-800:]}")
        print(f"drift-proof: {ok} passed, {fail} failed, {skip} skipped")
        sys.exit(1 if fail else 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
