#!/usr/bin/env python3
"""Derive the generation-mode leakage registry (schema/source-identity.json) from the REAL source.

Inputs (package root): src/**/*.jsx (the clone's markup and copy), src/routes.js (page titles), CLONE.md,
CLONE_SPEC*.md, ROUTES.md, ASSET_MANIFEST.md, clone-manifest.json, design-repo/assets/asset-roles.json and
design-repo/extraction/measured-values.json (source URL). Every pattern carries file:line evidence; copy is
stored only as hashed 5-word shingles (schema/textnorm.py), never as text.

Categories (one GENERATION_MODE_* rule each in schema/semantic_validate.py):
  brand     brand names / legal entity found in the source (seed: the source URL's registrable label, plus
            any page-title suffix " - <Name>" in src/routes.js)
  domain    hosts and e-mail addresses that belong to the source (contain a brand term), the asset CDN host
            and the live-embed host
  person    texts inside elements the source itself labels as a person's name (data-framer-name
            "Employee Name" / "Author Name" / "Author #n Name" / "Name"), plus mailbox names of real people
  customer  third-party company names: data-framer-name labels of logo elements in sections whose contract
            uses customer-logo / integration-logo / credential-logo, and testimonial "Company name" texts
  stat      marketing statistics (30%+, 30x, $50K+, 40+ hours ...) in non-article, non-legal sections
  copy      hashed 5-word shingles of every text block in src/sections + src/pages
  asset     every registered asset path, its content-id stem, and inline-mark sha256 values
  embed     live-embed URLs (asset-roles.json embeds)

Usage: python3 design-repo/extraction/build_source_identity.py [--check]
Needs the package's src/ (a git clone of the package); design-repo/ shipped alone keeps the committed registry.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG = os.path.dirname(REPO)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "schema"))
from jsx_text import text_blocks  # noqa: E402
from textnorm import normalize, shingles, stats  # noqa: E402

OUT = os.path.join(REPO, "schema", "source-identity.json")
PERSON_MARKERS = re.compile(r'data-framer-name="(Employee Name|Author Name|Author #\d Name|Name)"')
GENERIC_LABELS = {"image", "icon", "logo", "logos", "logo wrapper", "logos wrapper", "background", "overlay", "variant 1", "image wrapper",
                  "icon wrapper", "wrapper", "content", "clients grid", "employee photo", "author photo", "image bg", "media", "small",
                  "large", "black", "white", "desktop", "row", "column", "top", "bottom", "left", "right", "slide #1", "slide #2", "slide #3",
                  "soc2 badge", "your image goes here", "illustration wrapper", "featured image", "title card", "quote card"}
LOGO_ROLES = {"customer-logo", "integration-logo", "credential-logo"}
NON_CLAIM_SECTIONS = re.compile(r"ContentSection\d+|Container\d*$|OtherArticlesSection|BlogSection|FeaturedImageWrapper")


def rel(p):
    return os.path.relpath(p, PKG).replace(os.sep, "/")


def evidence_for(term, files, limit=3):
    out, pat = [], re.compile(re.escape(term), re.I)
    for f in files:
        for i, l in enumerate(open(f, encoding="utf-8", errors="ignore"), 1):
            if pat.search(l):
                out.append(f"{rel(f)}:{i}")
                if len(out) >= limit:
                    return out
    return out


def build():
    src_jsx = sorted(glob.glob(os.path.join(PKG, "src", "**", "*.jsx"), recursive=True))
    docs = [p for p in [os.path.join(PKG, x) for x in ("CLONE.md", "ROUTES.md", "ASSET_MANIFEST.md", "clone-manifest.json", "src/routes.js")]
            + sorted(glob.glob(os.path.join(PKG, "CLONE_SPEC*.md"))) if os.path.isfile(p)]
    allfiles = src_jsx + docs
    ledger = json.load(open(os.path.join(HERE, "measured-values.json"), encoding="utf-8"))
    assets = json.load(open(os.path.join(REPO, "assets", "asset-roles.json"), encoding="utf-8"))
    secs = {json.load(open(p, encoding="utf-8"))["id"]: json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(REPO, "sections", "*.json"))}

    # ---- brand
    host = re.match(r"https?://(?:www\.)?([^/]+)", ledger["sourceProject"]["url"]).group(1)
    seed = host.split(".")[0]
    brand_terms = {seed}
    for m in re.finditer(r'title: "[^"]* - ([A-Z][A-Za-z]+)"', open(os.path.join(PKG, "src", "routes.js"), encoding="utf-8").read()):
        brand_terms.add(m.group(1).lower())
    entities = set()
    for f in src_jsx:
        for _, _, t in text_blocks(f):
            for m in re.finditer(r"\b%s [A-Z][a-z]+, Inc\.?" % re.escape(seed.capitalize()), t):
                entities.add(m.group(0).rstrip("."))
    brand = [{"term": t, "match": "word-prefix", "evidence": evidence_for(t, allfiles)} for t in sorted(brand_terms)]
    brand += [{"term": e.lower(), "match": "substring", "evidence": evidence_for(e, allfiles)} for e in sorted(entities)]

    # ---- domains, e-mails, embeds
    hosts, emails = {}, {}
    url_re = re.compile(r"https?://([A-Za-z0-9.-]+)")
    for f in allfiles:
        for i, l in enumerate(open(f, encoding="utf-8", errors="ignore"), 1):
            for m in url_re.finditer(l):
                hh = m.group(1).lower().removeprefix("www.")
                if any(b in hh for b in brand_terms):
                    hosts.setdefault(hh, f"{rel(f)}:{i}")
            for m in re.finditer(r"(?:mailto:)?([a-z0-9._%+-]+@([a-z0-9.-]+\.[a-z]{2,}))", l, re.I):
                if any(b in m.group(2).lower() for b in brand_terms):
                    emails.setdefault(m.group(1).lower(), f"{rel(f)}:{i}")
    cdn = sorted({a["path"].split("/")[1] for a in assets["assets"] if a["path"].startswith("_ext/")})
    for c in cdn:
        hosts.setdefault(c, (evidence_for(c, src_jsx, 1) or ["assets/asset-roles.json"])[0])
    embeds = sorted({re.sub(r"[?#].*$", "", e["url"]) for e in assets.get("embeds", [])})
    for e in embeds:
        hosts.setdefault(re.match(r"https?://([^/]+)", e).group(1), "design-repo/assets/asset-roles.json (embeds)")
    domain = [{"host": k, "evidence": [v]} for k, v in sorted(hosts.items())]
    email = [{"address": k, "evidence": [v]} for k, v in sorted(emails.items())]

    # ---- people
    people = {}
    for f in src_jsx:
        lines = open(f, encoding="utf-8").read().split("\n")
        blocks = text_blocks(f)
        for i, l in enumerate(lines, 1):
            if PERSON_MARKERS.search(l):
                nxt = next((b for b in blocks if b[0] > i), None)
                if nxt and 1 < len(nxt[2].split()) <= 4 and re.fullmatch(r"[^\W\d_][^\W\d_ .'-]*(?:[ .'-]+[^\W\d_]+)+", nxt[2]):
                    people.setdefault(normalize(nxt[2]), f"{rel(f)}:{nxt[0]}")
    for addr, ev in emails.items():
        local = addr.split("@")[0]
        if local not in ("team", "info", "support", "sales", "hello", "press"):
            people.setdefault(local, ev)
    person = []
    for name, ev in sorted(people.items()):
        toks = name.split()
        person.append({"name": name, "surname": toks[-1] if len(toks) > 1 and len(toks[-1]) >= 5 else None, "evidence": [ev]})

    # ---- third-party companies
    comps = {}
    logo_secs = {sid for sid, c in secs.items() if LOGO_ROLES & set(c.get("assetRoles", []))}
    logo_files = {s["file"] for r in ledger["routes"] for s in r["sections"] if s["id"] in logo_secs}
    for f in sorted(logo_files):
        lines = open(os.path.join(PKG, f), encoding="utf-8").read().split("\n")
        for i, l in enumerate(lines):
            for m in re.finditer(r'data-framer-name=(?:"([^"]+)"|\{"([^"]+)"\})', l):
                lab = (m.group(1) or m.group(2)).strip()
                if lab.lower() in GENERIC_LABELS or len(lab) < 3 or re.search(r"#|\d|name|information|wrapper", lab, re.I):
                    continue
                if any(re.search(r"<(img|svg)\b", x) for x in lines[i:i + 5]) and len(lab.split()) <= 3:
                    comps.setdefault(lab, f"{f}:{i + 1}")
    proof_files = {s["file"] for r in ledger["routes"] for s in r["sections"] if secs.get(s["id"], {}).get("category") == "PROOF"}
    for f in sorted(proof_files):
        lines = open(os.path.join(PKG, f), encoding="utf-8").read().split("\n"); blocks = text_blocks(os.path.join(PKG, f))
        for i, l in enumerate(lines, 1):
            if re.search(r'data-framer-name="(Company name|Company)"', l):
                nxt = next((b for b in blocks if b[0] > i), None)
                if nxt and len(nxt[2].split()) <= 4 and "*" not in nxt[2]:
                    comps.setdefault(nxt[2], f"{f}:{nxt[0]}")
    customer = [{"name": normalize(k), "match": "word-case-sensitive" if len(k) <= 4 or "&" in k or k.lower() in ("sage", "main street", "campfire") else "word",
                 "display": k, "evidence": [v]} for k, v in sorted(comps.items())]

    # ---- copy shingles + statistics
    sh, blocks_ev, stat = set(), 0, {}
    for f in sorted(glob.glob(os.path.join(PKG, "src", "sections", "*.jsx")) + glob.glob(os.path.join(PKG, "src", "pages", "*.jsx"))):
        claimable = not NON_CLAIM_SECTIONS.search(os.path.basename(f)[:-4])
        for line, tag, t in text_blocks(f):
            s = shingles(t)
            if s:
                sh |= s; blocks_ev += 1
            if claimable and not tag.startswith("@"):
                for tok in stats(t):
                    stat.setdefault(tok, f"{rel(f)}:{line}")
    # ---- assets
    apaths = sorted(a["path"] for a in assets["assets"])
    stems = sorted({re.sub(r"__[0-9a-f]+$", "", os.path.splitext(os.path.basename(p))[0]) for p in apaths if p.startswith("_ext/")})
    stems = [s for s in stems if len(s) >= 12]
    inl = sorted(a["inlineSource"]["sha256"] for a in assets["assets"] if a.get("inlineSource"))
    return {
        "version": "0.2.0",
        "generatedBy": "extraction/build_source_identity.py (derived from the real source; do not edit by hand)",
        "humanReviewed": False,
        "note": ("Patterns are derived mechanically and were NOT reviewed by a human. Detection is string-based after normalisation "
                 "(schema/textnorm.py: NFKC, zero-width removal, curly quotes, dashes, case); it does not catch homoglyphs, paraphrase or translation."),
        "normalisation": "schema/textnorm.py",
        "brand": brand,
        "domains": domain,
        "emails": email,
        "people": person,
        "companies": customer,
        "stats": [{"token": k, "evidence": [v]} for k, v in sorted(stat.items())],
        "copy": {"shingleWords": 5, "hash": "sha256[:16] of the space-joined normalised words", "sourceBlocks": blocks_ev,
                 "sourceFiles": "src/sections/*.jsx, src/pages/*.jsx", "shingles": sorted(sh)},
        "assets": {"paths": apaths, "contentIds": stems, "inlineSha256": inl},
        "embeds": embeds,
        "placeholderDomains": [".example", ".invalid"],
    }


def dump(d):
    return json.dumps(d, indent=1, ensure_ascii=False) + "\n"


def main():
    if not os.path.isdir(os.path.join(PKG, "src")):
        sys.exit("no src/ next to design-repo/: the registry can only be (re)built from the package's own source")
    d = build()
    if "--check" in sys.argv:
        ok = open(OUT, encoding="utf-8").read() == dump(d)
        print("source-identity registry up to date" if ok else "source-identity registry differs from the source"); sys.exit(0 if ok else 1)
    open(OUT, "w", encoding="utf-8").write(dump(d))
    print(f"source identity: {len(d['brand'])} brand, {len(d['domains'])} domains, {len(d['emails'])} emails, {len(d['people'])} people, "
          f"{len(d['companies'])} companies, {len(d['stats'])} stats, {len(d['copy']['shingles'])} copy shingles, {len(d['assets']['paths'])} assets")


if __name__ == "__main__":
    main()
