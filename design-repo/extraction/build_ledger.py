#!/usr/bin/env python3
"""Rebuild the citation ledger (measured-values.json routes[].sections) from the runnable clone's OWN source.

The clone that ships in this package (src/ + public/ at the package root, tracked in git) is the evidence:
  router  src/routes.js            path -> src/pages/<Page>.jsx
  page    src/pages/<Page>.jsx     renders its sections in order as <Component /> (one per line)
  section src/sections/<C>.jsx     the root element of each component carries data-clone-section="<C>"

For every route this script maps the n-th section of the existing ledger to the n-th <Component /> usage in
the page, verifies that the component's root line holds the ledger's tag and anchor, and rewrites the citation
as file=src/sections/<C>.jsx, lines=[root line, closing line]. The previous rendered-HTML snapshot range
(recon/mirror/src/*.html, never shipped) is kept as liveSnapshot for history only; it is not checked.

Whole-document bodies are decomposed by real content boundaries (R6): a legal body becomes one
content.legal-preamble + one content.legal-clause per <h3>; an article body becomes one content.article-lead
+ one content.article-chapter per <h3>. The <h3> line is the cited start of each part.

Usage (from anywhere):  python3 design-repo/extraction/build_ledger.py [--check]
--check exits 1 if the ledger on disk differs from what the source gives (no write).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG = os.path.dirname(REPO)
LEDGER = os.path.join(HERE, "measured-values.json")

# whole-document bodies -> (part ids). Keyed by the section id the old ledger used on those routes' templates.
DECOMPOSE = {
    "template.legal": {"section": "content.content-section", "lead": "content.legal-preamble", "part": "content.legal-clause"},
    "template.blog-2": {"section": "content.content-section", "lead": "content.article-lead", "part": "content.article-chapter"},
}


def read(rel):
    with open(os.path.join(PKG, rel), encoding="utf-8") as f:
        return f.read()


def route_pages():
    txt = read("src/routes.js")
    return {m.group(1): "src/pages/" + m.group(2) for m in re.finditer(r'path: "([^"]+)".*?import\("\./pages/([^"]+)"\)', txt)}


def component_root(rel):
    lines = read(rel).split("\n")
    a = next(i for i, l in enumerate(lines) if re.match(r"^    <\w", l))
    tag = re.match(r"^    <(\w+)", lines[a]).group(1)
    if lines[a].rstrip().endswith("</" + tag + ">"):
        b = a
    else:
        b = max(i for i, l in enumerate(lines) if l.startswith("    </" + tag + ">"))
    return lines, a + 1, b + 1, tag


def heading_anchor(line):
    m = re.search(r">(\{\"(?:[^\"\\]|\\.)*\"\}|[^<{]+)</h3>", line)
    raw = m.group(1) if m else ""
    return raw[:40]


def build():
    ledger = json.load(open(LEDGER, encoding="utf-8"))
    pages = route_pages()
    problems = []
    for r in ledger["routes"]:
        page = pages.get(r["route"])
        if not page:
            problems.append(f"route {r['route']} is not in src/routes.js"); continue
        ptxt = read(page)
        imports = {m.group(1): "src/sections/" + m.group(2) for m in re.finditer(r'import (\w+) from "\.\./sections/([^"]+)"', ptxt)}
        uses = [(i + 1, m.group(1)) for i, l in enumerate(ptxt.split("\n")) for m in [re.match(r"\s*<(\w+) />\s*$", l)] if m and m.group(1) in imports]
        # the original (pre-rebase) section list is kept in liveSnapshot order; on a re-run rebuild from it
        base = r.get("snapshotSections") or [dict(id=s["id"], tag=s["tag"], anchor=s["anchor"], lines=s["lines"]) for s in r["sections"]]
        if len(uses) != len(base):
            problems.append(f"{r['route']}: {len(uses)} section components in {page} but {len(base)} ledger sections"); continue
        out = []
        dec = DECOMPOSE.get(r["template"])
        for (uline, comp), s in zip(uses, base):
            cf = imports[comp]
            lines, a, b, tag = component_root(cf)
            if tag != s["tag"] or s["anchor"] not in lines[a - 1]:
                problems.append(f"{r['route']}: {cf}:{a} is <{tag}> without anchor {s['anchor']!r} (ledger says <{s['tag']}>)"); continue
            entry = {"id": s["id"], "component": comp, "file": cf, "tag": tag, "anchor": s["anchor"], "lines": [a, b],
                     "usage": {"file": page, "line": uline}}
            if dec and s["id"] == dec["section"]:
                h3 = [i + 1 for i in range(a, b - 1) if re.match(r"^\s*<h3\b", lines[i])]
                if not h3:
                    problems.append(f"{r['route']}: {cf} has no <h3> to decompose by"); continue
                lead = dict(entry, id=dec["lead"], lines=[a, h3[0] - 1], part={"of": comp, "index": 0, "boundary": "before first <h3>"})
                out.append(lead)
                for k, h in enumerate(h3):
                    end = (h3[k + 1] - 1) if k + 1 < len(h3) else b - 1
                    out.append({"id": dec["part"], "component": comp, "file": cf, "tag": "h3", "anchor": heading_anchor(lines[h - 1]),
                                "lines": [h, end], "usage": {"file": page, "line": uline},
                                "part": {"of": comp, "index": k + 1, "boundary": "<h3>-bounded"}})
            else:
                out.append(entry)
        for i, e in enumerate(out):
            e["idx"] = i
        r["file"] = page
        r["snapshotSections"] = base
        r["sections"] = [{k: e[k] for k in ("idx", "id", "component", "file", "tag", "anchor", "lines", "usage", "part") if k in e} for e in out]
    ledger["sourceProject"] = {
        "url": ledger["sourceProject"]["url"], "framework": ledger["sourceProject"]["framework"],
        "scrapedAt": ledger["sourceProject"]["scrapedAt"],
        "evidenceRoot": "package root (the folder that contains design-repo/)",
        "evidenceTrees": ["src/", "public/"],
        "liveSnapshotFolder": "recon/mirror/src/ (rendered-HTML capture of the live site; gitignored, never shipped; snapshotSections ranges point into it and are history only)",
    }
    ledger["note"] = ("Citation ledger. routes[].sections[] cite the runnable clone's own source (src/sections/*.jsx, root element of each "
                      "data-clone-section component; usage = the <Component /> line in the route's page). verify_all.py resolves every range "
                      "whenever src/ sits next to design-repo/ (a git clone of the package) and warns only when design-repo/ is copied alone. "
                      "snapshotSections keep the original live-snapshot ranges (recon/mirror, not shipped) for history; they are not checked.")
    return ledger, problems


def main():
    ledger, problems = build()
    if problems:
        print("\n".join(problems)); sys.exit(1)
    new = json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"
    cur = open(LEDGER, encoding="utf-8").read()
    if "--check" in sys.argv:
        print("ledger up to date" if new == cur else "ledger differs from the source"); sys.exit(0 if new == cur else 1)
    open(LEDGER, "w", encoding="utf-8").write(new)
    n = sum(len(r["sections"]) for r in ledger["routes"])
    print(f"ledger rebuilt from src/: {len(ledger['routes'])} routes, {n} cited sections")


if __name__ == "__main__":
    main()
