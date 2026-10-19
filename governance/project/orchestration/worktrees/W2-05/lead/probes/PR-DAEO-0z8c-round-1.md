---
type: probe
task: DAEO-0z8c
reviewer_session: 3f14bb4d-0856-418c-8ead-d372c7e03d73
implementer_session: e28a6c37-e973-43dd-a132-c65e94e529ee
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 0983be4c7cb4f2e34bfbef281493f1942d47fd9c
---

# Probe record: W2-05, round 1 (draft, not committed: the round failed)

- **What was probed.** Head `0983be4c7cb4f2e34bfbef281493f1942d47fd9c` of `w2/W2-05` (DAEO-0z8c), running this
  worktree's `src/` (engineer sessions `e28a6c37-e973-43dd-a132-c65e94e529ee`, `89af54b4-d8ce-4955-a686-6e5434e9b27d`).
  A fresh read-only reviewer (role `independent-auditor`, session `3f14bb4d-0856-418c-8ead-d372c7e03d73`, started
  through `gov launch`, sandboxed, 2026-10-18), commissioned and judged by the orchestrator. Its only writes were
  the sandbox check's git object and index refresh (DEC-789); the tripwire saw no change in any tree.
- **Findings.**
  - F1 (high, a gate fails open, a regression): a commit whose index lies outside the git directory, with a
    secret staged, passed the staged-secrets gate (it scanned `.git/index`); the base refused it.
  - F2 (medium, KPI 1): the code-index tool started by the code index inherits every `GIT_*` variable; the
    tool starts git itself (one call writes configuration); the sweep record does not list it.
  - F3 (low–medium, fails closed): `gov ci push`'s own push loses push settings given with `git -c`.
  - F4 (low): a work tree whose git directory is named only by `GIT_DIR` and `GIT_WORK_TREE` breaks every gov
    git call; some checks could then pass on nothing (by reading).
  - F5 (low): the containment check's pinned configuration ignores a global `core.excludesFile`.
  - F6 (cosmetic): sweep row 9's wording differs from the code.
- **Found sound.** The sweep's 42 rows against the direct call sites; `GIT_DIR` always cleared; a linked worktree's
  own index kept and every other index cleared; identity and `GIT_SSH*` kept; no trace from the changed direct
  calls; containment refuses when its git fails; `lefthook install` byte-identical with both hooks files and the
  restore after `uninstall` clean; no DEC-777 file changed.
- **Judgement: fail** (F1).
