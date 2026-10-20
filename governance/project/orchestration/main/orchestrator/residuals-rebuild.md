
## The one rebuild of this repository's stores (DEC-448, 2026-10-07)

- **Run once at `5d2390e4`,** after W1-27's merge: `gov rebuild` exit 0 in about 8 minutes; the record store,
  the lexical index, the semantic index and the code index were recreated. The record store names three files
  as invalid (no `type` key): `docs/charter/CHARTER_v5.md`, `docs/contract/CONTRACT_v4.md`,
  `docs/plan/WAVE_1_WBS.md`.
- **`gov doctor` before and after:** index freshness went from unmeasured (no index) to pass, the canaries from
  unmeasured to pass on both indexes. Doctor still exits 3, for two reasons: the Claude Code drift (extension
  2.1.289 above the pinned CLI 2.1.288; harmless by DEC-448, re-recorded at the exit) and path compliance.
  Unmeasured: hooks (no hook-manager configuration, no binary) and the framework lock (none exists).
- **Path compliance reports 180 stale paths and none of them is in a live document to correct by hand:** 156
  are in `docs/SOURCES.md`, which is the table of moves itself (new path, old path, hash); 23 are in the old
  `cli/` tree (its configuration, fixtures and two source files, carried unchanged from the v4 line); one is
  the original Framework's file name in `docs/plan/tools/validate_s1.py`. Doctor counts no file as left out
  as historical on this repository (`historical_excluded: 0`), though the register and this file are full of
  old paths: either the exclusion is not counted or the old paths in those files are not in the move table.
  The cleanup ticket `DAEO-0f1y` holds this: the table of moves is a historical record for the check; whether `cli/` is
  live is the owner's to say.
- Adoption level reported for this repository: INTERMEDIATE, 15 of 22 systems identified.
