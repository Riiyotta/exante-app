# Exante: AI Teammate for Collections — information architecture

`ia.json` is the only file to hand-edit here. `IA.md` and `matrix.csv` are generated from it: re-run the scripts below after any change and never hand-edit the generated files.

```bash
cd ia
node validate.mjs   # checks route/template totals, referential integrity, category coverage
node build.mjs      # regenerates IA.md and matrix.csv
```

Every section's `implementedBy` is a path from the project root (`src/sections/*.jsx`, or `src/pages/*.jsx` when a section is only part of a page). The design repo's `sections/*.json` carry the same pointer.
