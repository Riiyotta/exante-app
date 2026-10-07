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

## Unreleased — content-safety asset roles
- Added three asset roles: `integration-logo` (third-party product/platform marks shown as
  integration partners), `compliance-badge` (certification graphics such as SOC 2 — no such asset
  exists on this measured site; added so a generated site cannot fabricate one), and
  `credential-logo` (third-party company/institution marks shown as team credentials — "our team
  previously worked at / studied at"). All three are `must-not-fabricate`, pinned, and added to the
  schema's `assetRole` enum and `verify_all.py`'s `PINNED` dict alongside the existing roles.
- Reclassified 20 misidentified assets in `assets/asset-roles.json`:
  - 12 integration logos (Stripe, Quickbooks, Xero, NetSuite, Sage, Campfire, SAP, Plaid, and 4
    unnamed) in `features.integrations-section`, `content-image` → `integration-logo`.
  - 7 real people's photos — 2 founders, 4 engineers, 1 unnamed testimonial author — `content-image`
    (one was `icon`) → `avatar`. The founder photo tagged `icon` was the more serious case: an
    `icon` generation policy (`may-generate-new`) would have let a generator invent a fake photo of
    a real CEO.
  - 17 team-credential logos (BCG, Barclays, Google, Harvard Business School, Harvard, X, P&G,
    Skillshare, Globant, BMW, UIF, Bain & Co, Pinterest, Main Street, GCM Grosvenor, Tesla, and 1
    unnamed), `content-image` → `credential-logo`. Found while auditing team sections for item 3;
    not in the original punch list.
- Extracted 5 inline `data:image/svg+xml` assets that existed only as data URIs baked into
  implementation markup — invisible to the whole asset-tracking system, since nothing is a file on
  disk to track — to real files under `recon/mirror/public/_extracted/` and registered them:
  - The site's own wordmark (2 fill-color variants, black/white, byte-identical path data; 20
    occurrences across all 7 header/footer implementation variants) → role `logo`. `shell.desktop`
    and `shell.desktop-filled` now declare an `images` field with `logo` in their `assetRoles`; the
    role already existed in the catalog at `observed: 0` — nothing had ever used it.
  - 3 client-logo marks from the home page's client-logo row (`proof.clients-section`) → role
    `customer-logo`. Their specific companies could not be conclusively identified — components
    elsewhere in this repo (`bain-co.json`, `barclays.json`, `bcg.json`, `bmw.json`) name real
    companies but are measured from a *different* section (the team-credentials strip, see above),
    and pairing a name to the wrong file risked a wrong attribution. Recorded as real, unidentified
    third-party trademarks; `must-not-fabricate` applies regardless of which company it is.
- `proof.clients-section` and `shell.desktop-filled` gained their first `images` field (previously
  had none); `component-allowlist.json`'s `contentFields` and the schema's per-section `content.*`
  definitions updated to match.
- `schema/tests/adversarial_test.py`: 3 new mutations proving the per-section role allowlist
  actually excludes these roles where it should — not just that an invented role name is rejected
  (the existing "invented assetRole" case). Each targets the specific section and role pair rather
  than the schema's generic `assetRole` enum, since `semantic_validate.py`'s enforcement is a plain
  per-section allowlist check, not role-type-aware. Suite is now 35 checks (was 32); one planned
  case (content-image swapped for avatar on testimonials) was retargeted mid-build after the first
  attempt did not actually prove anything — `content-image` is legitimately allowed there alongside
  `avatar`, so the real proof uses a role that is genuinely excluded.
- Not satisfied: item 4 asked to "add a compliance-badge role for certification graphics"; the role
  is added, but there is nothing on this measured site to reclassify — no SOC 2 or similar badge
  image exists (the footer's "Trust Center" is a plain text link to `app.vanta.com`, not a graphic).
  This entry is a forward-looking catalog addition plus test coverage only.
- `registry.manifest.json` and `README.md`'s asset count: 239 → 244 (the 5 newly tracked files).

## 0.1.0 — 2026-10-05T13:10:06Z
- Initial extraction from https://www.exante.app/: 31 sections, 9 templates, 18 routes.
