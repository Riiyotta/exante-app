# exante-app — Design Repo

Machine-validated design system extracted from a live site, structured per the design-repo BUILD-GUIDE.
Status: **design-review-pending** (`productionApproved: false`). The source is a real, live site: see `assets/asset-roles.json`
for what a generator may and may not reproduce.

## Counts

- Sections: 31
- Templates: 9
- Routes: 18
- Primitives: 12
- Components: 178
- Assets: 239
- Foundation tokens: 113
- Semantic tokens: 19
- Rules: 7

## Layout

- `tokens/00-foundation → 10-semantic → 20-component → 30-layout → themes`, and `tokens/llm/` (catalog, policy, allowlist)
- `primitives/`, `components/`, `sections/` (one contract per section type), `templates/templates.json` (structured nodes)
- `compatibility/graph.json` (rules with severity), `assets/asset-roles.json`, `motion/motion-contract.json`
- `schema/` (draft-07 PageSpec schema, example, semantic validator, adversarial tests), `extraction/` (citations, admission)

## What is measured vs inferred

Values (colours, sizes, spacing, radii, widths, word counts, line ranges) are measured. Semantic role **names**
(`text.primary`, `surface.alt`…), section **categories**, asset **roles** and section **purposes** are heuristics and are labelled
`basis` / `inferred`. Review them before production use.

## Admit this repo

```
python3 extraction/verify_all.py      # files, entryPoints, counts, parity, citations, pinned policies, schema, adversarial suite
python3 extraction/prove_drift.py     # proves each check fails on injected drift
```
