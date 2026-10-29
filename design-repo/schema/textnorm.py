"""Shared string normalisation for source-identity patterns (build side) and the semantic validator (check side).

Both sides MUST use these exact functions, otherwise a hash built from the source would never match the same
text in a PageSpec. Detection is string-based: it defeats case, Unicode compatibility forms (NFKC: full-width,
ligatures), zero-width/soft-hyphen insertion, curly quotes and dash variants. It does not defeat homoglyphs
from other scripts (e.g. a Cyrillic "е"), paraphrase, or translation.
"""
import hashlib, re, unicodedata

ZERO_WIDTH = re.compile("[­᠎​-‏‪-‮⁠-⁤﻿]")
QUOTES = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'", "´": "'", "`": "'",
                        "“": '"', "”": '"', "„": '"', "‟": '"', "″": '"', "«": '"', "»": '"'})
DASHES = re.compile("[‐‑‒–—―−﹘﹣－]")
SHINGLE = 5


def normalize(s):
    s = unicodedata.normalize("NFKC", str(s))
    s = ZERO_WIDTH.sub("", s).translate(QUOTES)
    s = DASHES.sub("-", s).lower()
    return re.sub(r"\s+", " ", s).strip()


def words(s):
    """word tokens of normalised text; apostrophes are dropped inside words (i'm -> im)."""
    return re.findall(r"[a-z0-9]+", normalize(s).replace("'", ""))


def h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def shingles(s, n=SHINGLE):
    w = words(s)
    return {h(" ".join(w[i:i + n])) for i in range(len(w) - n + 1)}


STAT = re.compile(r"(?<![\w$])(\$\s?\d[\d,.]*\s?[kmb]?\+?|\d[\d,.]*\s?(?:%\+?|x(?![a-z])|×|\+))(?:\s+(hours?|days?|weeks?|months?|minutes?|customers?|invoices?))?")


def stats(s):
    """marketing-statistic tokens ("30%+", "30x", "$50k+", "40+ hours") in normalised form."""
    out = set()
    for m in STAT.finditer(normalize(s)):
        tok = re.sub(r"\s+", "", m.group(1)).replace("×", "x")
        if tok in ("100%",):
            continue
        out.add(tok + (" " + m.group(2) if m.group(2) else ""))
    return out
