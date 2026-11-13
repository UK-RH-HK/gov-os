---
type: probe
task: DAEO-fd0p
reviewer_session: 4d84e10e-d2b1-4380-a236-c36ba5f0e2b0
implementer_session: "eng-1 81ed5bbb-9c52-4b3a-9da9-c392927f48e5 (eb6d0cc07643)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: eb6d0cc076435ca12cac6d8a4cab47f236b82d69
decisions_applied: [DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1153, DEC-1010]
---

# Probe record: W2-160 (DAEO-fd0p) `gov wait` and the helper watch, STANDARD review, round 1 of 2 (DEC-1010)

- **Round 1** (reviewer session 4d84e10e-d2b1-4380-a236-c36ba5f0e2b0, independent-auditor, Opus high, read-only)
  probed head `eb6d0cc07643`: **pass**, 0 blocking. Every KPI line S1-S4 and F1-F4 passes. The findings are R1-1 and
  R1-3 to R1-10. The reviewer used no R1-2, so there are nine findings, though its return says ten. None of them
  fails open or loses work. R1-10 is out of scope (the ticket text). No second round is needed.
- **The lead's triage** (each row is non-blocking and is recorded as a residual, not fixed on this branch):
  - R1-1: two overlapping passes on one root write each condition twice (F3). The caller arms one watcher per root.
    Worth a follow-up fix that writes nothing beyond the three files S4 names.
  - R1-3: a zero or negative `--every` in loop mode spins or ends in a traceback. Worth a follow-up usage check.
  - R1-4: each action ignores the other action's stray arguments. A usability row.
  - R1-5: the helper's meta `description` label and single-word code fields are copied into items, as I2 and the
    reference do. Message text never is. It is the owner's call whether the label counts as a message's text under
    S4.
  - R1-6: the worker check does not read the exit file again before reporting "gone". A false alarm is possible
    in a window of microseconds, and the real code is still reported later.
  - R1-7: the digits of a pid file are joined across lines, as in the reference. `launch_worker.sh` writes one
    line.
  - R1-8: a fractional `<max-s>` exits 2, as in the reference. The wait fails closed.
  - R1-9: a worker's item names its log and the error flags, not a description of the log's last line. S4 forbids
    copying that line's text.
  - R1-10: I2 cites DEC-1140 (1)(a) for "the state file only grows". DEC-1140 does not say that. The rule stands
    by DEC-1153 (2). The CTO's decision record corrects the citation.
- **The lead's checks of the probed head `eb6d0cc07643`:**
  - `gov accept W2-160`: pass, 66 passed, 0 failed. success-1 21, success-2 9, success-3 25, success-4 11,
    failure-1, failure-2 and failure-3 3 each. F4 is the lead's check, below.
  - F4: `git diff --name-only b42bcff9e35e..eb6d0cc07643` lists 18 paths. Each one is in the ticket's
    allowed_paths or in its acceptance folder `tests/acceptance/W2-160/`.
  - The scoped verification (`lead_verify.sh`, after `rebuild_slot.sh`): 5187 tests in the parallel phase, 2 failed,
    7 skipped. The serial phase selected no entries. Both reds are outside this ticket's paths, and the lead has
    returned each to the CTO as a package:
    - `tests/unit/session_watch/test_route.py::test_the_command_is_declared_by_its_module` pins W2-159's
      single-path `ACT_PATHS`. DEC-1153 (2) adds `.gov-runtime/dispatch/inbox/**` (PKG-W2-160-ROUTE-1: a one-line
      test change on a widened path).
    - `tests/acceptance/W2-159/test_f4_scope.py::test_f4_the_branch_changes_only_the_tickets_allowed_paths`
      compares any branch with W2-159's own allowed_paths. It is green on w2/integrate and red on every other
      ticket's branch (PKG-W2-160-KNOWN-1: name it in skip_known.json).
  - `gov.__file__`: /home/usain/gov-os-worktrees/W2-160/src/gov/__init__.py.
- **Facts for the record:** S2's "as `gov launch` writes it" means `launch_worker.sh`'s `<base>.pid`, `.exit`
  and `.json` (the ticket's own facts line). `gov launch` in this tree writes no pid file.

The reviewer's return follows verbatim. Its verdict block decides.

## Round 1 (eb6d0cc07643): the reviewer's return

