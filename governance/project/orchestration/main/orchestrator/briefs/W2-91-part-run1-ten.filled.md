You are the ticket lead for ticket `DAEO-a3u2` (`W2-91`, "Full embeddings: the root files, the governance overlay and schemas/ embedded"). It is profile STANDARD, on memory's critical chain (DEC-979 item 4), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-91` on branch `w2/W2-91`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-957, DEC-954, DEC-388, DEC-694, DEC-381, DEC-856, DEC-887, DEC-820, DEC-833, DEC-860, CAP-10.a); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-91/`) are set; its dependency is closed: W2-86 (`DAEO-jsg1`, closed today; its `kernel-template` namespaces are on `w2/integrate`).

**Read first:** the ticket file; `governance/project/path-map.yaml` as W2-86 left it (and DEC-990's `tools/**` line); W2-86's measure `docs/research/W2-86-memory-measure.md` (hit@5 11/20, full evidence 11/20, bundle 15/20; ranking the remaining cause); `governance/project/orchestration/packages/MEMORY-SPEC-MAP.md`.

## The decisions for this run
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort high) in `/home/usain/gov-os-worktrees/W2-91-tests`, retrieving only from the integration branch's store, writes `tests/acceptance/W2-91/` from the spec and KPIs (a planted repository with its own path map and a stub embedder; never this repository's store). In parallel a fresh engineer (sandboxed, effort high) changes the path map to the spec, never to the tests; it runs the acceptance tests once merged, through `gov accept DAEO-a3u2`, results only.
- **Scope, by file:** `governance/project/path-map.yaml` (engineer config under DEC-996 (D)) and builder tests as new `tests/unit/retrieval/test_w2_91*` files only. **W2-13 (running) holds the rest of `tests/unit/retrieval/**`:** never write another file there. The indexer's code is not changed (KPI 4).
- **The measurement record is your implementer's evidence (DEC-995, DEC-996 (A)):** the CTO moves your ticket's record path from `docs/research/W2-91-memory-measure.md` to `docs/changes/W2-91-evidence.md` at claim; write it there, in W2-61's form (both figures together: hit@5 against 85 and the owner's 95 %, full evidence against 99 %; the in-the-bundle count; per question; beside W2-86's and W2-61's figures). If the ticket file still names the old path, use the new one and say so.
- **The re-measure (W2-61's §8, as W2-86 ran it):** clones by exact path under `/home/usain/gov-os-runs/W2-91/` (`base` at `@@HEAD@@`, `head` at your final commit); each store rebuilt with the embedder under `flock /tmp/gov-os-rebuild.lock`; the visible half only (`--part visible`), never the hidden half; `head` with `--compare` on `base`. Record each namespace's chunk count with vectors from the clone's store (KPI 1).
- **Fail closed:** `fixtures/**`, `.claude/**`, `.rulesync/**`, `template/.rulesync/**`, the vendored parts and `cli/**` stay not embedded; the governance overlay keeps `restricted` and `export_policy: denied` (a planted export case shows the export path still refuses it).
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh`. Never the full suite. A path-map change selects the path-map suites (W1-08, `core-pathmap`): quote them.
- **One role (DEC-995):** a part needing another role's writes is a split named in your return. **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified. **No review (STANDARD).**

**Estimate:** about 30 lines of path map and 100 of tests; about 4 hours (two rebuilds with embeddings dominate). Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-91`.

---
