review = open("/home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/lead/log/rev-2.result.md").read().rstrip() + "\n"
head = """---
type: probe
task: DAEO-fd0p
reviewer_session: 33f2b54b-891e-4b48-88ea-ed1ecb9add24
implementer_session: "eng-3 64613a2c-585d-42c0-9660-1c944d5cc325 (2c2302c4b); td-2 12f37ea5-d41d-44cb-9f19-30f87c1a8705 (e1e170d35)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 14c9e7a36eb200e3fd7c1203b54f628aa87bd6e0
decisions_applied: [DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1153, DEC-1154, DEC-1156]
---

# Probe record: W2-160 (DAEO-fd0p), narrow independent check (DEC-1154) of the run-3 changes (DEC-1156 (1), (6))

- **What was checked.** Review round 1 passed at `eb6d0cc07643` (0 blocking; its record is now
  `PR-DAEO-fd0p-round-1.md`). The owner then decided two changes for this ticket (DEC-1156 (1), (6)). Under
  DEC-1154 (1) they had a narrow independent check of those two changes only, at head `14c9e7a36`:
  - ROUTE-1 (a), commit `2c2302c4b` (engineer): `tests/unit/session_watch/test_route.py:19` asserts the two-path
    `ACT_PATHS` of `src/gov/session_watch/command.py:17` (DEC-1153 (2)).
  - W2-159's F4 revision, commit `e1e170d35` (test designer; `Rewrite-Reason:` DEC-1156 (6)), merged at
    `14c9e7a36`: `tests/acceptance/W2-159/test_f4_scope.py` judges only on `w2/W2-159` and skips elsewhere with its
    reason. On a planted `w2/W2-159` branch with a change outside W2-159's paths, it still fails.
- **The verdict.** Reviewer session 33f2b54b-891e-4b48-88ea-ed1ecb9add24 (independent-auditor, Opus high,
  read-only): **pass**, 0 blocking.
- **The lead's triage.** N-1 is non-blocking and is recorded as a residual, not fixed on this branch. The judgement
  in `test_f4_scope.py:52-53` reads the git config of whoever runs pytest. The planted repositories do not. The
  reviewer found no key that changes these four git calls' output, and any such change would show red, not pass.
  W2-170's F5 model has the same gap.
- **The round-1 rows that stay recorded and are not fixed.** R1-1, R1-3, R1-5, R1-6 and R1-10 are out of this run's
  scope (see `PR-DAEO-fd0p-round-1.md`).
- **The lead's checks at `14c9e7a36`:**
  - `lead_verify.sh`, after `rebuild_slot.sh`: GREEN. The parallel phase ran 5413 tests: 0 failed, 0 errors,
    8 skipped. The serial phase selected 0 entries. One of the skips is W2-159's F4 real case, whose reason reads
    "F4 judges only the branch w2/W2-159; this is the branch w2/W2-160: not judged here". The other seven skip
    for reasons unrelated to this ticket: local_only, bwrap, and the CTO's scratch tools.
  - F4: `git diff --name-only --no-renames <merge-base with w2/integrate>...HEAD` lists 21 paths. Each one is in the
    ticket's allowed_paths or in `tests/acceptance/W2-160/`.

The reviewer's return follows verbatim. Its verdict block decides.

## Narrow check (14c9e7a36): the reviewer's return

"""
open("/home/usain/gov-os-worktrees/W2-160/docs/probes/DAEO-fd0p/PR-DAEO-fd0p.md", "w").write(head + review)
