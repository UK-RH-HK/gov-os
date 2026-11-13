# Brief: independent test designer, DAEO-neam (W2-45), run 3 (two one-line test revisions, R1 and R2)

You are a fresh independent test designer (MR-3). Ticket `DAEO-neam` (W2-45), profile STANDARD, class C2. You work
only in the tests worktree `/home/usain/gov-os-worktrees/W2-45-tests` on branch `w2/W2-45-tests` (DEC-963), head
`55446b8fc`. Two older tests assert what the ticket's accepted Interface changed; the owner widened the ticket's
allowed_paths by the two files for one revision each (DEC-1148 (4), P1-J (a), 2026-11-12). You make exactly those two
revisions, one commit each, and change nothing else in either file.

## Step 0, before any work: the sandbox check (report it first in `evidence`)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-neam','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop and return ESCALATION with what you saw. Delete nothing (a) made.

## Standing rules

- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-neam`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-45-tests`,
  `w2/W2-45-tests`). If anything differs, stop and say so.
- Everything in the foreground; return only after both commits exist. No `git checkout` of another commit, `reset`,
  `clean`, amend, rebase, merge, push or tag.
- Never read this ticket's implementation (`src/gov/check/runner.py`, `src/gov/check/commands.py`,
  `src/gov/decisions/checker.py`, `tests/unit/check/`), nor the worktree `/home/usain/gov-os-worktrees/W2-45`. The
  ticket's Interface below tells you what the code does; that is all you need.
- `/tmp` is read-only in the sandbox: scratch goes under your `$TMPDIR` (`printenv TMPDIR`, then write it literally).
  Any pytest goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with that
  TMPDIR, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45-tests/src`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`. A slot/memory gate refusal is a wait: run it again later.
- No `gov retrieve`, no `gov context`; Read and Grep. No here-document, no backticks, no `bash -c`, no long inline
  `python3 -c`; a script longer than a line goes under your `$TMPDIR` and you run it.
- **Refused twice for the same call: stop and say so.** Never reach the same effect by another form (DEC-1142 (9)).
- Install nothing; no subagents that write; never ask the owner. Hashes: 12 digits.

## What the accepted Interface says (the ticket, P-W2-45-1, accepted by the CTO 2026-11-12)

- Item 2: every check result gains `elapsed_s` (wall seconds, float) and `time_limit_s`. A wall time differs from run
  to run, so a comparison of two runs' entries must leave `elapsed_s` out, as it leaves out `provenance`.
- Item 5: an absent tool of a hard-block check is RED, never YELLOW; the built-in `openspec-validate` (hard-block)
  follows the same rule: `OPENSPEC_ABSENT` is RED.

## R1: `tests/acceptance/W2-95/test_w2_95_adopted_and_gov_check.py`

`_others(result)` (about line 112) builds each other check's entry as `{k: v for k, v in c.items() if k != "provenance"}`.
Make it leave out `elapsed_s` as well as `provenance` (e.g. `if k not in ("provenance", "elapsed_s")`) and update its
docstring's "without provenance" to name both. Nothing else in the file changes. Then run that test file alone through
the slot; `test_w2_95_other_checks_results_do_not_change_with_core_pathmap` must pass (report counts).

    git commit -m "W2-95 test: _others() leaves out elapsed_s beside provenance (a wall time)" --trailer "Task: DAEO-neam" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Rewrite-Reason: P-W2-45-1 item 2: elapsed_s is a wall time" -- tests/acceptance/W2-95/test_w2_95_adopted_and_gov_check.py

## R2: `tests/unit/ci/test_ci_command.py`

In `test_the_job_gate_names_a_check_whose_tool_is_absent_as_unmeasured_and_refuses`: line 80
`assert refused.value.details["checks"]["openspec-validate"] == "YELLOW"` becomes `== "RED"`, and line 73's comment
`# no openspec: the runner gives OPENSPEC_ABSENT, YELLOW` says `RED`. Nothing else in the file changes (the rest of the
case already passes). Then run that test file alone through the slot; report counts.

    git commit -m "W2-45: test_ci_command's absent-openspec case expects RED (OPENSPEC_ABSENT is RED)" --trailer "Task: DAEO-neam" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Rewrite-Reason: P-W2-45-1 item 5: OPENSPEC_ABSENT is RED" -- tests/unit/ci/test_ci_command.py

After both: `git diff --stat 55446b8fc HEAD` must show exactly those two files, a few lines each; paste it in `evidence`.

## Return

Your last message, complete in itself. The twelve fields first, each a labelled line ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Include the sandbox check first in `evidence`, both commits (12 digits), each file's pytest counts, and the diff stat.
