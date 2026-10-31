---
id: DAEO-kiar
status: in_progress
deps: []
links: []
created: 2026-10-31T01:22:30Z
type: task
priority: 0
assignee: engineer
external-ref: W2-107
tags: [wave-2, implementation, secrets, speed, full]
wbs_id: W2-107
title: 'Rebuild speed: gitleaks results remembered by content hash, so a rebuild scans only new or changed files; the nightly scans in full; any change to gitleaks or its rules forgets them all'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/secrets/__init__.py
- src/gov/secrets/cache.py
- tests/unit/secrets_check/test_w2_107*
- src/gov/rebuild/command.py
kpis:
  success:
  - 'A rebuild scans with gitleaks only content it has not judged clean before: each scan''s verdict is remembered in one machine-wide cache (`~/.cache/gov-os/secrets-scan.sqlite`, outside every repository, shared by worktrees, close clones and the nightly), keyed by the sha256 of the bytes scanned, the kind (a file''s content, or a path''s names for `path_holds_secret`) and the engine''s fingerprint (gitleaks'' version string, the sha256 of every rule set in force, the cache format''s version); a second rebuild of an unchanged tree scans nothing again [DEC-966 item 4, DEC-939]'
  - 'Only a clean verdict is remembered: no finding of any kind by any rule set. Any finding, row W2-L423''s exempt commit hash included (its exemption depends on the repository), is never remembered and is scanned again every time; a secret''s content is never answered clean from the cache [DEC-966 item 4, DEC-911, DEC-285]'
  - 'Any change to gitleaks or its rules forgets every remembered result: a fingerprint that differs from the cache''s clears it before the first read [DEC-966 item 4]'
  - 'Fail closed: a cache that cannot be opened, is corrupt, has the wrong form or is locked counts as a miss, and the content is scanned; a write that fails is ignored; a scan that cannot decide still raises as today [DEC-966 item 4, DEC-285]'
  - 'The cache holds hashes and verdicts only, never content, a path or a secret''s text [DEC-966 item 4, DEC-911]'
  - 'A full scan reads nothing from the cache (and refreshes it) when `GOV_SECRETS_FULL_SCAN=1` is set: the nightly sets it (that one line in `nightly.sh` is the orchestrator''s at merge, with `test_nightly.sh`) [DEC-966 item 4]'
  - 'The rebuild''s record says how many contents and names were scanned and how many were answered from the cache; measured before and after on this repository, in seconds of the secrets stage: a second rebuild of an unchanged tree, and a close clone''s rebuild after the main tree''s; the target is a secrets stage that scans only new or changed files [DEC-966 item 4, DEC-939 item 2]'
  failure:
  - 'A secret''s content answered clean from the cache, or a finding remembered.'
  - 'A changed gitleaks or rule set answered from the old results.'
  - 'A corrupt, missing or locked cache that stops a rebuild or answers clean.'
  - 'Content, a path or a secret''s text written into the cache.'
  - 'The full-scan setting answered from the cache.'
  - 'No measured before and after, or a second unchanged rebuild that scans everything again.'
profile: FULL
sources:
- DEC-966
- DEC-939
- DEC-911
- DEC-285
- DEC-898
est_loc: 180
acceptance_tests:
  path: tests/acceptance/W2-107/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer in its own tests worktree (DEC-959 item 7, DEC-963)
track: A
list_rows: []
---
# W2-107 Rebuild speed

**DEC-970 (2026-10-31):** the unit path is `tests/unit/secrets_check/test_w2_107*` (W2-69 renamed `tests/unit/secrets/`; an engineer moves the two files). For the independent test designer, not in allowed_paths: `tests/acceptance/W1-16/test_w1_16_home.py::test_no_index_file_exists_outside_gov_runtime_after_a_run` leaves out exactly the scan cache's file and its `-wal`/`-shm` (P-W2-107-2 (a), `Rewrite-Reason: DEC-967`).

Card: the owner's order of 2026-10-31 (DEC-966 item 4): rebuild speed is a priority.

- **Why:** W2-76 measured the rebuild's stages. The secrets filter in the code-index stage took 274.8 of 307.4 s (run 1) and 547.9 of 735.4 s (run 2): `gov.secrets.indexable` starts gitleaks once per file and rule set, for every file, on every rebuild, while the lexical index is already incremental by blob. Every rebuild (a worktree's, a close clone's, the designers' store, the nightly's) pays it again.
- **The fix (P-SPEED-1):** remember each clean verdict by the content's hash and the engine's fingerprint, so a rebuild scans only new or changed content; the nightly scans everything in full; any gitleaks or rule change forgets every result. Only "no finding" is remembered, so a cache error can only cause a rescan, never a missed secret.
- **Where:** `src/gov/secrets/__init__.py` (`indexable`, `path_holds_secret`, `_scan`) and a new `cache.py`. No running ticket holds `src/gov/secrets/`, but W2-05 (`DAEO-0z8c`, in progress) lists `src/gov/**/*.py` for the git environment of its helpers: split by file, W2-05 leaves `src/gov/secrets/__init__.py` to this ticket (its `_commits` git call's environment, if W2-05 needs it, is a merge-back between them, whichever merges second).
- **Not here:** W2-76's timing and lock (`src/gov/rebuild/**`); batching many files into one gitleaks call (a further speed-up, a later option if the cache is not enough).
- **Profile FULL:** the secrets filter guards the index against secrets; an independent review of the final code (the QA step) on every path where a remembered result is used.

**At merge (DEC-970 P-W2-107-3, DEC-975 item 1):** `src/gov/rebuild/command.py` is in this ticket's paths for one change only: the rebuild's JSON record gives the secrets stage's counts from `gov.secrets.scan_counts()` (contents and names, scanned and remembered), taken as the difference around the stage; nothing else in that file changes (W2-76's file, merged).

**W1-27 (DEC-978):** a fresh independent test designer revises W1-27's case `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime` to leave out exactly the secrets cache (`.cache/gov-os/secrets-scan.sqlite`, its `-wal` and `-shm`, and `.cache`, `.cache/gov-os` only where they hold nothing else) under the home it gives, and W1-27's README line for it; nothing else (`Rewrite-Reason: DEC-967`).
