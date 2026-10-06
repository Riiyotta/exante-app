#!/usr/bin/env python3
"""Proves verify_all.py actually CATCHES drift: copies this design repo to a scratch folder,
injects one defect at a time, and requires verify_all.py to fail with the matching message.
Also requires the unmodified copy to pass (a check that rejects everything is broken too).
The sibling src/ snapshot tree is symlinked (read-only) so citation checks run for real.
Usage: python3 prove_drift.py"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG = os.path.dirname(REPO)
# The evidence tree is where the ledger says it is (same rule as verify_all.py), never guessed from a root src/, which in the final layout is the
# runnable clone's own source: guessing it made citation injections run against React files in a published copy and "fail to be caught".
def _evidence_root():
    try:
        with open(os.path.join(REPO, "extraction", "measured-values.json"), encoding="utf-8") as f: snap = json.load(f).get("sourceProject", {}).get("snapshotFolder")
    except Exception: snap = None
    if snap: return os.path.normpath(os.path.join(PKG, snap, ".."))
    return os.path.join(PKG, "recon", "mirror") if os.path.isdir(os.path.join(PKG, "recon", "mirror")) else PKG
MIRROR = _evidence_root()


def jload(p): return json.load(open(p, encoding="utf-8"))
def jsave(p, d): json.dump(d, open(p, "w", encoding="utf-8"), indent=2)


def first_section(r):
    return sorted(f for f in os.listdir(os.path.join(r, "sections")) if f.endswith(".json"))[0]


def inj_phantom(r):
    p = os.path.join(r, "tokens/llm/component-allowlist.json"); d = jload(p); d["sections"].append("content.phantom-section"); jsave(p, d)
def inj_orphan(r):
    src = os.path.join(r, "sections", first_section(r)); d = jload(src); d["id"] = "content.orphan-section"
    jsave(os.path.join(r, "sections/content.orphan-section.json"), d)
def inj_count(r):
    p = os.path.join(r, "registry.manifest.json"); d = jload(p); d["counts"]["sections"] += 1; jsave(p, d)
def inj_readme(r):
    p = os.path.join(r, "README.md"); s = open(p).read(); s = re.sub(r"^- Templates: (\d+)$", lambda m: f"- Templates: {int(m.group(1)) + 7}", s, flags=re.M); open(p, "w").write(s)
def _ledger(r):
    p = os.path.join(r, "extraction/measured-values.json"); return p, jload(p)
def _first_cited(d):
    return next((x for rt in d["routes"] for x in rt["sections"] if x.get("lines")), None)
def inj_cite_range(r):   # the ledger claims a range past the end of the snapshot file
    p, d = _ledger(r); x = _first_cited(d)
    if not x: return False
    x["lines"] = [999999, 1000000]; jsave(p, d)
def inj_cite_wrong(r):   # in range, but the cited line is not that element (anchor no longer on the line)
    p, d = _ledger(r); x = _first_cited(d)
    if not x: return False
    x["anchor"] = "anchor-that-is-not-on-this-line"; jsave(p, d)
def inj_cite_other(r):   # a contract cites a range that belongs to a DIFFERENT section
    _, led = _ledger(r)
    ents = [(x["id"], f"{rt['file']}:{x['lines'][0]}-{x['lines'][1]}") for rt in led["routes"] for x in rt["sections"] if x.get("lines")]
    if not ents: return False
    a = ents[0]; b = next((e for e in ents if e[0] != a[0]), None)
    if not b: return False
    p = os.path.join(r, "sections", a[0] + ".json"); d = jload(p); d["evidence"]["measuredFrom"] = [b[1]]; jsave(p, d)
def inj_allow_version(r):
    p = os.path.join(r, "tokens/llm/component-allowlist.json"); d = jload(p); d["version"] = str(d["version"]) + "-drift"; jsave(p, d)
def inj_pinned(r):
    p = os.path.join(r, "assets/asset-roles.json"); d = jload(p); d["roles"]["avatar"]["generationPolicy"] = "may-generate-new"; jsave(p, d)  # valid value, wrong for this role
def inj_abs(r):
    p = os.path.join(r, "README.md"); open(p, "a").write("\nSource: /Users/someone/project\n")
def inj_entry(r):
    p = os.path.join(r, "registry.manifest.json"); d = jload(p); d["entryPoints"]["tokenCatalog"] = "../ia.json"; jsave(p, d)
def inj_policy(r):
    p = os.path.join(r, "tokens/llm/token-policy.json"); d = jload(p); d["rawValueRestrictions"]["typography-human-label"] = "forbidden"; jsave(p, d)
def inj_graph(r):
    p = os.path.join(r, "compatibility/graph.json"); d = jload(p)
    lim = next(x for x in d["rules"] if x["id"] == "SECTION_PER_PAGE_LIMITS")["limits"]
    if not lim: return False
    k = sorted(lim)[0]; lim[k] += 5; jsave(p, d)
def inj_theme(r):
    p = os.path.join(r, "tokens/themes/light.json"); d = jload(p)
    if not d["resolves"]: return False
    k = sorted(d["resolves"])[0]; d["resolves"][k] = "rgb(1,2,3)"; jsave(p, d)
def inj_schema_enum(r):
    p = os.path.join(r, "schema/pagespec.schema.json"); d = jload(p); d["definitions"]["node"]["properties"]["type"]["enum"].append("hero.not-a-contract"); jsave(p, d)
def inj_rule_kind(r):
    p = os.path.join(r, "compatibility/graph.json"); d = jload(p); d["rules"].append({"id": "UNIMPLEMENTED", "severity": "error", "kind": "notARealKind"}); jsave(p, d)
def inj_snapshot_folder(r):   # the ledger declares an evidence folder that does not exist — must fail outright, not fall back silently
    p, d = _ledger(r)
    if "snapshotFolder" not in d.get("sourceProject", {}): return False
    d["sourceProject"]["snapshotFolder"] = "recon/does-not-exist/src/"; jsave(p, d)
def inj_hero_exception(r):   # the graph claims a template has >1 HERO section that it does not
    p = os.path.join(r, "compatibility/graph.json"); d = jload(p)
    rule = next((x for x in d["rules"] if x["id"] == "ONE_HERO_PER_PAGE"), None)
    if rule is None: return False
    rule["exceptions"] = list(rule.get("exceptions", [])) + ["template.phantom-multi-hero"]; jsave(p, d)


INJECTIONS = [
    ("phantom allowlist entry", inj_phantom, "has no contract file"),
    ("orphan section contract", inj_orphan, "has no allowlist entry"),
    ("wrong manifest count", inj_count, "manifest counts.sections"),
    ("stale README count", inj_readme, "README count 'Templates'"),
    ("out-of-range citation", inj_cite_range, "range exceeds the file", "src"),
    ("in-range citation pointing at the wrong element", inj_cite_wrong, "does not contain the cited element", "src"),
    ("contract citing another section's range", inj_cite_other, "points at", None),
    ("allowlistVersion drift", inj_allow_version, "allowlistVersion drift"),
    ("pinned asset policy changed to a different valid value", inj_pinned, "pinned asset role 'avatar'"),
    ("absolute path leak", inj_abs, "absolute path"),
    ("entryPoint escaping design-repo", inj_entry, "entryPoints.tokenCatalog"),
    ("policy category not in catalog", inj_policy, "rawValueRestrictions"),
    ("graph limit drifted from contract", inj_graph, "SECTION_PER_PAGE_LIMITS"),
    ("theme resolution drift", inj_theme, "theme light"),
    ("schema enum drifted from contracts", inj_schema_enum, "schema node type enum"),
    ("graph rule the validator does not implement", inj_rule_kind, "not implemented"),
    ("snapshotFolder points at a missing evidence folder", inj_snapshot_folder, "declares sourceProject.snapshotFolder"),
    ("ONE_HERO_PER_PAGE exception for a template that is not one", inj_hero_exception, "ONE_HERO_PER_PAGE exceptions"),
]


def run(r, full=False):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    if not full: env["VERIFY_SKIP_ADVERSARIAL"] = "1"  # injections target verify_all's own checks
    p = subprocess.run([sys.executable, os.path.join(r, "extraction/verify_all.py")], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def main():
    tmp = tempfile.mkdtemp(prefix="drift-")
    try:
        def fresh():
            pkg = tempfile.mkdtemp(dir=tmp)
            shutil.copytree(REPO, os.path.join(pkg, "design-repo"), ignore=shutil.ignore_patterns("__pycache__"))
            if os.path.isfile(os.path.join(PKG, ".gitignore")):  # same evidence policy as the real package (a published copy leaves recon/ out)
                shutil.copy(os.path.join(PKG, ".gitignore"), os.path.join(pkg, ".gitignore"))
            if os.path.isdir(os.path.join(MIRROR, "src")):
                dst = os.path.join(pkg, os.path.relpath(MIRROR, PKG), "src")
                os.makedirs(os.path.dirname(dst), exist_ok=True); os.symlink(os.path.join(MIRROR, "src"), dst)
            return os.path.join(pkg, "design-repo")
        ok = fail = skip = 0
        has_src = os.path.isdir(os.path.join(MIRROR, "src"))
        code, out = run(fresh(), full=True)
        if code == 0: ok += 1; print("  ok    control: unmodified copy is admitted")
        else: fail += 1; print("  FAIL  control: unmodified copy was rejected:\n" + out)
        for inj in INJECTIONS:
            label, fn, needle = inj[:3]; needs = inj[3] if len(inj) > 3 else None
            if needs == "src" and not has_src:
                skip += 1; print(f"  skip  {label}: needs the sibling src/ snapshots (design-repo shipped alone)"); continue
            r = fresh()
            try:
                applied = fn(r)
            except Exception as e:  # a broken injection is a failure of this proof, not a silent pass
                fail += 1; print(f"  FAIL  {label}: the injection itself crashed: {e!r}"); continue
            if applied is False:
                skip += 1; print(f"  skip  {label}: not applicable to this repo"); continue
            code, out = run(r)
            if code != 0 and needle in out: ok += 1; print(f"  ok    caught: {label}")
            else: fail += 1; print(f"  FAIL  NOT caught: {label} (expected '{needle}')\n{out[-600:]}")
        print(f"drift-proof: {ok} passed, {fail} failed, {skip} skipped")
        sys.exit(1 if fail else 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
