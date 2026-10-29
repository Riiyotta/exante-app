#!/usr/bin/env python3
"""contentHash of the design-policy binding: sha256 over the policy file and every file it is enforcedBy.

    python3 extraction/policy_hash.py           print the hash
    python3 extraction/policy_hash.py --write   store it in registry.manifest.json designPolicy.contentHash
verify_all.py recomputes it with the same function and fails on a mismatch.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def policy_hash(repo=REPO, ref="policy/design-policy.json"):
    pol = json.load(open(os.path.join(repo, ref), encoding="utf-8"))
    h = hashlib.sha256()
    for rel in sorted(set([ref] + pol["enforcedBy"])):
        h.update(rel.encode() + b"\n" + open(os.path.join(repo, rel), "rb").read() + b"\n")
    return "sha256:" + h.hexdigest()


if __name__ == "__main__":
    v = policy_hash()
    if "--write" in sys.argv:
        p = os.path.join(REPO, "registry.manifest.json"); m = json.load(open(p, encoding="utf-8"))
        m["designPolicy"]["contentHash"] = v
        open(p, "w", encoding="utf-8").write(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(v)
