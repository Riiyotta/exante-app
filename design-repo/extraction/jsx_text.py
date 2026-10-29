"""Text extraction from the clone's JSX section/page files (standard library only).

The clone's markup is machine-written: one element per line, text either bare between tags or as a JSON-style
string expression {"..."}. text_blocks() returns one block per block-level element (p, h1-h6, li, button, label,
a, td, figcaption, blockquote) with the 1-based line where it opens, joining inline pieces (strong, em, span,
time, code, br) so a sentence split across <strong> keeps its word order.
"""
import json, re

BLOCK = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "button", "label", "td", "th", "figcaption", "blockquote", "summary", "dt", "dd"}
TAG = re.compile(r"<(/?)([A-Za-z][\w.]*)((?:\"(?:[^\"\\]|\\.)*\"|\{\{.*?\}\}|\{[^{}]*\}|[^>\"{])*?)(/?)>")
EXPR = re.compile(r"\{\"((?:[^\"\\]|\\.)*)\"\}")
ATTR_TEXT = re.compile(r"\b(alt|aria-label|placeholder|title)=\"([^\"]+)\"")


def _decode(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s


def text_blocks(path, start=1, end=None):
    """[(line, tag, text)] for block elements whose opening line is within [start, end]."""
    lines = open(path, encoding="utf-8").read().split("\n")
    end = end or len(lines)
    out, stack = [], []  # stack of [tag, line, pieces]
    for ln in range(start, end + 1):
        line = lines[ln - 1]
        if line.lstrip().startswith(("import ", "//", "export ", "return", "const ")):
            continue
        for m in ATTR_TEXT.finditer(line):
            out.append((ln, "@" + m.group(1), m.group(2)))
        pos = 0
        for m in TAG.finditer(line):
            seg = line[pos:m.start()]
            pos = m.end()
            if stack and seg.strip():
                stack[-1][2].append(EXPR.sub(lambda x: _decode(x.group(1)), seg))
            closing, name, _, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
            if name == "br" and stack:
                stack[-1][2].append(" ")
            if name in BLOCK or (name == "a" and not stack):
                if closing:
                    if stack and stack[-1][0] == name:
                        t, l0, pieces = stack.pop()
                        txt = re.sub(r"\s+", " ", "".join(pieces)).strip()
                        if txt:
                            if stack:
                                stack[-1][2].append(" " + txt + " ")
                            out.append((l0, t, txt))
                elif not selfclose:
                    stack.append([name, ln, []])
        tail = line[pos:]
        if stack and tail.strip():
            stack[-1][2].append(EXPR.sub(lambda x: _decode(x.group(1)), tail) + " ")
        elif not stack and EXPR.search(tail):
            pass
    # nested blocks were also folded into their parent; keep only the outermost text once
    seen, res = set(), []
    for b in sorted(out):
        if (b[0], b[2]) in seen:
            continue
        seen.add((b[0], b[2]))
        res.append(b)
    return res
