# Changelog

## Unreleased
- `verify_all.py` / `prove_drift.py`: resolve the evidence tree from `measured-values.json`'s
  `sourceProject.snapshotFolder` instead of guessing `recon/mirror` or falling back to the package
  root. The old fallback could point at the runnable clone's own `src/`, so citation checks ran
  against React files and injected drift went uncaught. A declared-but-missing folder now fails
  outright; the standard `recon/mirror/src` left out by the package's own `.gitignore` (a published
  copy) warns instead, and the admission line says evidence was not checked.
- `verify_all.py`: count repeatable template nodes as `maxCount` sections when recomputing
  `ONE_HERO_PER_PAGE` exceptions. A collapsed `{repeatable, maxCount}` node was counted as one hero,
  so a template rendering two `hero.main` sections did not register as an exception.
- `prove_drift.py`: two new injections covering the above — a `snapshotFolder` pointing at a missing
  evidence folder, and an `ONE_HERO_PER_PAGE` exception for a template that is not one. Suite is now
  19 checks (was 17).

## 0.1.0 — 2026-10-05T13:10:06Z
- Initial extraction from https://www.exante.app/: 31 sections, 9 templates, 18 routes.
