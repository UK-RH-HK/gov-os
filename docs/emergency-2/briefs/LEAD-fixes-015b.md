# Lead brief: fixes-015b, seven fixes for release 0.1.5 that do not touch `gov launch` (DEC-1232, DEC-1233)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. **Do not merge.** Every helper Sonnet (DEC-1225). Each fix: failing test first by the independent test designer, then the engineer; one commit series per fix with its own `Task:` and `Fix:` trailers; record each in its owning ticket's file as a `## Fix: ...` section (the form of `.tickets/DAEO-xm6l.md`'s last section). Find each owning ticket with `gov retrieve` and `grep -l "^wbs_id: W.-N" .tickets/*.md`. The audits these come from: `docs/emergency-2/audits/E2-AUDIT-{1,2,3}-*.md` and the merged table `.gov-runtime/scratch/orchestrator/log/audits-merged-2026-11-22.md` (ids N-nn, M-nn). Decisions: DEC-1232, DEC-1233.
Name: `fixes-015b`; worktree `/home/usain/gov-os-worktrees/E2-fixes-015b`, branch `e2/fixes-015b` from `w2/integrate` (it holds L2-4's `gov queue` fix).

## The fixes
- **F2 `gov doctor` checks a tool installed in its own folder** (audit 3, M-04): the registry entries `node-22.23.5` and
  `rea-agents` (`governance/project/tool-registry.yaml`, the last two) are reported `ok: false` because doctor finds a
  binary only by `TOOL_BINARIES` or a `PATH=<prefix>:$PATH` in the install line (`src/gov/doctor/command.py:38-46`,
  `:86-95`, `:440-540`). Make doctor find and version both with **no schema change** (a kit schema added or removed is
  not a patch: RB-7 P5); a registry note or install line may change. A `PATH=` prefix from one tool's install line must
  never answer for another tool of the same binary at another version (v22.23.5 must never answer for `node` v22.23.3).
  Owner: W2-22 `DAEO-xm6l`.
- **F4 `context_watch.py` registered twice after `gov update`** (EXAMIN's report 28 in
  `/home/usain/gov-os-runs/W2-27/examin/REQUESTS.md`, read only): `gov update` never adds a hook entry already present;
  an update of a repository that has it twice leaves it once. Owner: W2-17 `DAEO-sdhj`.
- **F5 `gov accept W2-16` gives `ACCEPT_NO_MAP`:** its README maps no KPI line; the test designer writes the map (no test
  changed). Owner: W2-16.
- **F6 `gov update` leaves `gov doctor` red** (the real G3 run of 2026-11-22, `.gov-runtime/scratch/orchestrator/log/g3-real-20261122.json`):
  the update writes `governance/updates/<version>.json`, which an adopted repository's path map does not classify, so
  `gov doctor`'s `path_map` part fails (`unclassified: ["governance/updates/0.1.5.json"]`) in all six of W2-81's kept
  repositories after `gov update 0.1.5` (doctor exit 0 before, 3 after). The kit's path map classifies
  `governance/updates/**` (as the other governance records are), and `gov update` adds the line to a repository whose
  map lacks it (a merge, never a conflict). Verify: an adopted repository at 0.1.4 updated by the candidate: doctor's
  exit equal before and after; EXAMIN's copy (read only, `/home/usain/gov-os-runs/W2-27/examin`): say whether its map
  already classifies it. Owner: W2-17 `DAEO-sdhj`.
- **F7 G3 judges the update by regression, not by an absolute READY** (W2-209 `DAEO-a2h5`, the CTO's ruling): the kept
  W2-81 run of 0.1.4 is NOT_READY and four of its queue tickets hold no acceptance test (`gov close` refuses
  `NO_ACCEPTANCE_TESTS` before any update), so `src/gov/release/proving.py`'s judge step (`verdicts == [READY, READY]`)
  and close step (`rc == 0`) can never pass on it. Each step passes when the copy after the update is no worse than the
  kept repository before it, as the doctor step already does: the judge's verdict over the copy equals its verdict over
  the kept repository (and READY stays READY); `gov close` of the queue ticket exits as it does on an un-updated copy.
  The report names both values. Also: `rehearse(root, ...)` resolves `root` to an absolute path (a relative `.` made the
  scratch clone fail: `fatal: repository '.' does not exist`). Verify: W2-209's G3 cases with a NOT_READY kept stand-in
  and a regressing copy (READY before, NOT_READY after: refused).
- **F8 `gov queue` never leaves uncommitted work behind** (N-01, the one new gap that meets EMERGENCY-2 §3.2: it loses
  work): the queue merges the branch tip; a worktree holding that branch with uncommitted or untracked changes in tracked
  paths is refused before the merge, naming the worktree and the files (`QUEUE_WORKTREE_DIRTY`). Owner: W2-115b `DAEO-j9z6`.
- **F9 No hit@5 floor and no hard-blocking kit check left** (N-14, the owner: "so no hit@5 floor or hard-blocking kit
  check is left when EXAMIN's measure runs on 0.1.5"; EMERGENCY-2 5.2, DEC-1210): remove `FLOOR, TARGET = 85, 99`, the
  `retrieve_check` exit 1 on hit@k, the kit check that hard-blocks on it and every other hit@k floor in `src/` and the kit;
  hit@k stays a reported diagnostic only. The three floor-85 tests are revised by the test designer with a Rewrite-Reason
  naming DEC-1210 and DEC-1233. Owners: W2-61, W2-134 (say which holds what).

## Green and return
`gov accept` of each owning ticket green; `tests/unit/doctor`, `tests/unit/update`, `tests/unit/queue`,
`tests/unit/release`, `tests/unit/memaudit`, W1-06, W1-48, W2-16, W2-17, W2-22, W2-115b, W2-209, W2-61, W2-134,
`tests/unit/optin`. Return: branch and head; each fix with its owning ticket and tests; reds not yours; the trial
figures (runs to green, send-backs, minutes).
