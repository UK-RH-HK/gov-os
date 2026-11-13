# Brief: engineer, DAEO-neam (W2-45), run 4 (review round 1's fix: F1 merges at scale; F2/F3 group stop)

You are a fresh engineer. Ticket `DAEO-neam` (W2-45), profile STANDARD, class C2, in `/home/usain/gov-os-worktrees/W2-45`
on branch `w2/W2-45`, head `0098b58d5`. Batches 1 and 2 implemented the ticket's `## Interface`; `gov accept W2-45`
passed 32/32. Review round 1 (an independent auditor) failed the work on one major finding and two minor ones that
the CTO put in this round (P-W2-45-3 (a)). Your job is those three, in the ticket's paths. You never change the
Interface, the runner's result shape, what the decision checker finds, or any test under `tests/acceptance/`. A test
designer is writing acceptance cases for the same behaviours in another tree at the same time; the lead merges them
after you return.

## Step 0, before any work: the sandbox check (report it first in `evidence`)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-neam','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop and return ESCALATION with what you saw. Delete nothing (a) made.

## Standing rules

- First: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-neam`), `printenv TMPDIR` (the sandbox's temp
  folder: call it T below and write it out literally in every command), and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-45`, `w2/W2-45`).
- Everything in the foreground; return only after your commit exists. No `git checkout` of another commit, `reset`,
  `clean`, amend, rebase, merge, push or tag.
- **Allowed paths (write only these):** `src/gov/decisions/checker.py` (speed only: the same findings on every input),
  `src/gov/check/runner.py`, `tests/unit/check/**`. Never write `tests/acceptance/`.
- **Scratch:** `/tmp` is read-only and the Write tool is refused under `.gov-runtime/scratch/` for you. Put every
  scratch script and file under T, `mkdir -p T/w2-45-eng3` first; write scripts there with the Write tool at the
  literal path and run them with `python3 <file>` / `bash <file>`.
- **Code under test (DEC-732):** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src` per command; quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src python3 -c "import gov; print(gov.__file__)"`.
- **Every pytest goes through the heavy-job slot**, TMPDIR outside the repository and outside `~/gov-os-runs` (T is),
  `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, e.g.:
  `env TMPDIR=T/w2-45-eng3 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/check -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (one command, no `&&`, no pipe). A whole-folder run adds `-m "not local_only" -k "not real and not green_here and
  not time_limit"` and `HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home`. Never `--basetemp`.
  If cases are deselected by the opt-in rule, add `GOV_TESTS_OPTIN=lifted,breadth` to the env. A slot, memory or CPU
  gate refusal is a wait: run it again later; it does not count as a refusal.
- **Reads (DEC-820):** open, except secrets and keys, the held-out qualification material's contents (never under
  `governance/project/`), the hidden half of any evaluation set.
- **Search (DEC-1065):** no `gov retrieve`, no `gov context`; Read and Grep, search again once in other words. Grep the
  register only by id. No search from the repository root, `governance/project/` or `.claude/`.
- **Command forms:** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long
  inline `python3 -c`, no compound `&&` / pipe chains around pytest.
- **Refused twice for the same call: stop and say so.** Never reach the same effect by another command, form or file
  (DEC-1142 (9)); return it as a package.
- Never copy the repository. Install nothing. No subagents that write. Never ask the owner. Hashes: 12 digits.

## F1 (major, S1): the decision checker is over budget on a history with merges

The reviewer's words: "On a planted 200-decision, 20,000-commit history with merges, the decision checker takes
132.8 s (3,300 merges, one commit in six) or 285.9 s (6,600 merges) against the 60 s budget. Only one-parent commits
are passed over; every merge is still read for every decision." Findings were correct (parity against the base).
It fails closed: core-authority goes `CHECK_TIMED_OUT` RED and every close is refused. This repository has 984 merges
in 6,133 commits.

The lead's reading, for you to check: `_approved` in `src/gov/decisions/checker.py` (about line 288) settles a
one-parent commit that leaves the file alone through `_changes` (one `git log --raw` pass with `--diff-merges=off`), but
every merge the walk reaches goes to `_held` -> `_merged`, which reads `objects.file(parent, path)` for the merge and
each parent: decisions x merges reads. The CTO's direction (P-W2-45-3 (a)): **also pass over a merge whose parents all
hold the file as the merge does** (it continues every parent, no change: `_merged`'s first branch), learnt in the
same kind of one-pass git read (e.g. `--diff-merges=separate` / `-m` gives each merge's raw diff against each parent;
a merge whose path appears in none of them holds the file as every parent does), so such a merge goes on to all its
parents without a read. The reviewer estimates 25 to 40 lines. Measure; if the walk's own node count (every merge
visited once per decision) is then the cost, say so and fix that too, inside `checker.py`.

Must hold: the same findings on every input. Merges that bring the file from one side, moves, removed files,
several merge bases, unreadable merges (`read_merge` raising) and every rule in the module's docstring give the same
answer as now. Where git cannot give the pass, every commit is read as before (as `_changes` does now).

Target: on a planted 200-decision, 20,000-commit history with one merge in six (build one under T with
`git fast-import`; see `tests/acceptance/W2-45/w2_45_support.py`'s `repo_with_decisions` for the linear one, and give
side branches that touch `src/` files and now and then revise a decision, merged back with owner trailers), the
decision checker (time `python3 -m gov.check.authority` in that repository, or `gov check --json` holding
`template/governance/kernel/checks/core-authority.yaml`) runs well under 60 s; aim below 20 s on this loaded machine.
Record before and after. Add a unit test in `tests/unit/check/test_w2_45_checker_speed.py` (yours, from batch 2) for
the merge pass: findings unchanged on small merge histories (a merge that leaves the file alone; a merge that brings
the file from the side branch; a merge that changes it itself), and one scale case only if it runs in a few seconds.

## F2 and F3 (minor, S5): the check's group is left running when the runner ends by an exception

- F2: "When the runner is interrupted mid-check (Ctrl-C, or any exception other than the timeout), the check's whole
  process group keeps running with no limit." The check runs in its own session now (Interface item 7), so a
  terminal Ctrl-C no longer reaches it.
- F3 (W2-L167): "With a stated limit above about 2,147,483 s, `gov check` still ends in a traceback (`OverflowError:
  timeout is too large` from `communicate`), and now the check's group is left running."
- Direction: in `_run_command` (`src/gov/check/runner.py` about line 116), stop the group on any exception:
  `except BaseException: _stop(process); raise` (about 3 lines), keeping the timeout path as it is. The traceback for
  F3 itself stays the row W2-L167 unless the same lines cover it; do not widen.
- Add unit tests in `tests/unit/check/test_w2_45_runner_semantics.py`: a check whose `communicate` is interrupted
  (e.g. a `KeyboardInterrupt` raised into the wait, or a huge limit) leaves no process of its group running (the shell
  and a grandchild), and the exception still reaches the caller. Make each case clean up what it starts in a `finally`.

## Proof

Through the slot: `tests/unit/check`, `tests/unit/decisions`, `tests/unit/gitenv`, `tests/unit/ci/test_ci_command.py`,
`tests/acceptance/W2-45`, `tests/acceptance/W1-26`, `tests/acceptance/W2-150`, `tests/acceptance/W2-01`,
`tests/acceptance/W1-21`, `tests/acceptance/W2-95`: report each folder's counts. Nothing that passed before may fail.

## Commit

    git commit -m "W2-45: <subject>" --trailer "Task: DAEO-neam" --trailer "Role: engineer" --trailer "Implements: DEC-729" -- <your paths>

(`git add` a new file first.) One commit for F1 and one for F2/F3 is fine.

## Return

Your last message, complete in itself. The twelve fields first, each a labelled line ("none" where nothing):

```
task: / status: (DONE | PACKAGES | ESCALATION ...) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Include: the sandbox check first in `evidence`; commits (12 digits) with trailers; before/after time of the decision
checker on your planted merge history (and its merge count) and on the linear S1 repository; each suite's counts; the
`gov.__file__` line; read refusals; scratch figures (`du -sh`, `du -s --inodes` of T/w2-45-eng3, removed at the end);
any package.

## Context bundle (gov context DAEO-neam, hash ef773753cafd)

Authority: DEC-729 (decision, ACCEPTED); DAEO-g0ip (task, closed). Supplementary: none (the lexical index is stale). The ticket text as the bundle gives it:

    ---
    id: DAEO-neam
    status: in_progress
    deps: [DAEO-g0ip]
    links: []
    created: 2026-10-16T16:35:12Z
    type: task
    priority: 4
    assignee: engineer
    external-ref: W2-45
    tags: [wave-2, implementation, standard]
    wbs_id: W2-45
    title: gov check runner semantics and scale
    class: implementation
    state_class: AUTHORITATIVE
    role: engineer
    depends_on:
    - DAEO-g0ip
    allowed_paths:
    - src/gov/check/runner.py
    - src/gov/check/commands.py
    - src/gov/decisions/checker.py
    - tests/unit/check/**
    - tests/acceptance/W2-95/test_w2_95_adopted_and_gov_check.py  # one test-designer revision: _others() leaves out elapsed_s (Rewrite-Reason: P-W2-45-1 item 2; DEC-1148 (4))
    - tests/unit/ci/test_ci_command.py  # one revision: line 80 == "RED" and line 73's comment (Rewrite-Reason: P-W2-45-1 item 5; DEC-1148 (4))
    - docs/probes/DAEO-neam/**  # the probe record (P-W2-45-5 (a), the CTO, 2026-11-12)
    - tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py  # one test-designer revision: line 49 and its docstring, Rewrite-Reason P-W2-45-1 item 5 (DEC-1153 (1))
    kpis:
      success:
      - 'The decision checker runs within the gov check budget on a 200-decision, 20k-commit repository Verify: a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget''s value printed beside it) [W2-H018].'
      - 'A check that exits 0 with findings, or with "unmeasured" in its result, is not green Verify: planted checks, one exiting 0 with a finding and one exiting 0 with "unmeasured" in its result: both are reported not green; a planted clean check exiting 0 is green [W2-M129, W2-M212].'
      - 'An absent tool of a hard-block check is red, not yellow Verify: a planted hard-block check whose tool is absent from the path: its result is red, never yellow [W2-M130, W2-M265].'
      - 'A hard-block key is covered only by a check of hard-block tier Verify: a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted [W2-M211, W2-M259].'
      - 'The time limit is stated and tested Verify: the limit''s value is printed in the runner''s result, and a planted check that runs past it is stopped and reported as timed out, by a unit test [W2-M151].'
      failure: []
    profile: STANDARD
    sources:
    - DEC-729
    est_loc: 160
    acceptance_tests:
      path: tests/acceptance/W2-45/
      author: independent-test-designer (MR-3); written before implementation
    track: C
    closes:
    - W2-H018
    list_rows:
    - W2-H018
    - W2-L096
    - W2-L098
    - W2-L104
    - W2-L118
    - W2-L167
    - W2-L168
    - W2-L169
    - W2-L171
    - W2-L223
    - W2-M063
    - W2-M128
    - W2-M129
    - W2-M130
    - W2-M131
    - W2-M132
    - W2-M144
    - W2-M146
    - W2-M151
    - W2-M170
    - W2-M211
    - W2-M212
    - W2-M259
    - W2-M265
    - W2-M268
    - W2-M315
    ---
    # W2-45 gov check runner semantics and scale
    
    **Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** K8 (DEC-941); W2-26 found no trigger (indexing about 30 % of the envelope).
    
    Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-45), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).
    
    - **Allowed paths:** `src/gov/check/runner.py`, `src/gov/check/commands.py`, `src/gov/decisions/checker.py` (speed only), `tests/unit/check/**`.
    - **KPIs:**
      - The decision checker runs within the `gov check` budget on a 200-decision, 20k-commit repository [W2-H018].
      - A check that exits 0 with findings, or with "unmeasured" in its result, is not green [W2-M129, W2-M212].
      - An absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].
      - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].
      - The time limit is stated and tested [W2-M151].
    
    ## Interface (DEC-1052; P-W2-45-1 accepted as a whole, item 5 as written: an absent tool of a hard-block check is RED, openspec included; the CTO, 2026-11-12 12:58)
    
    Proposal (all in src/gov/check/runner.py unless named):
    
    1. **Tier = the declaration's `severity`.** "Hard-block tier" means `severity: hard-block`. `tier:` (G0-G5) is not read.
    2. **Time fields (S1, S5).** Every check result gains `elapsed_s` (wall seconds, float) and `time_limit_s` (the limit
       applied: its `timeout-seconds`, else `TIMEOUT_S`). The runner's result gains top-level `time_limit_s` (= `TIMEOUT_S`,
       60, DEC-595). Built-in checks carry both too.
    3. **S1, the budget.** The `gov check` budget of the decision checker is the time limit of the check that runs it,
       core-authority: 60 s (TIMEOUT_S; its declaration states none). Verified by a planted repository of 200 decision
       records and 20,000 commits (built with `git fast-import`) holding the core-authority declaration: `gov check --json`
       exits, and core-authority's entry has `elapsed_s` < `time_limit_s`, both printed. Speed work only in
       `src/gov/decisions/checker.py`.
    4. **S2, not green.** A check is GREEN only when it exits 0 with no finding. Exit 0 also yields findings when: the
       success form `{"ok": true, "result": R}` has a non-empty `R.findings`; or any JSON mapping in the output (top level
       or R) has `"unmeasured": true` -> finding `CHECK_UNMEASURED` with its `reason`; or non-JSON output contains the word
       "unmeasured" -> `CHECK_UNMEASURED`. Status from findings as now: RED if hard-block, YELLOW if warning.
    5. **S3, absent tool.** Exit code 127, or OSError on start -> finding `CHECK_TOOL_ABSENT` naming the command's first
       word; RED when hard-block (never YELLOW), YELLOW when warning. The built-in `openspec-validate` (hard-block) follows
       the same rule: `OPENSPEC_ABSENT` becomes RED. (Cost: a machine without openspec gets a red `gov check`; openspec
       and gitleaks are installed here. Alternative (b): leave openspec YELLOW, named as a residual against S3.)
    6. **S4, tier coverage.** A path-map policy key of strength hard-block whose covering declarations (`enforces`) are all
       of severity warning -> a `policy-<key>` result, severity hard-block, RED, finding `POLICY_TIER_TOO_LOW` with
       `policy`, `checks` (the covering ids) and a message naming the key. "Refused" = that RED result and `gov check`'s
       non-zero exit (unchanged). One hard-block declaration covering it -> no policy result (accepted). An uncovered key
       keeps `POLICY_NOT_COVERED`.
    7. **S5, time limit.** A check past its limit is stopped with its whole process group (`start_new_session=True`,
       `killpg` on timeout, so a grandchild holding the pipe cannot keep the runner waiting) -> finding `CHECK_TIMED_OUT`
       (was `CHECK_FAILED`) carrying `time_limit_s`; status by severity. Unit test in `tests/unit/check/` (engineer): a
       planted check `sleep 30` with `timeout-seconds: 1` -> `CHECK_TIMED_OUT`, `time_limit_s` 1 printed, ends in < 10 s.
    8. **Unchanged:** family roll-up, `gov check`'s exit code rule, the not-applicable (exit 2) path, `commands.py`
       (W2-159's line kept; touched only if a module list needs it).
    
    ## Widened by the owner (DEC-1148 (4), P1-J (a), 2026-11-12)
    
    Two older tests assert what the accepted Interface changed: R1 (W2-95's `_others()`, `elapsed_s` is a wall time) by the test designer; R2 (`test_ci_command.py:80`, OPENSPEC_ABSENT is RED) by the engineer or designer. One revision each, each with its Rewrite-Reason; nothing else in either file changes.
    
    ## Run 3's packages (2026-11-12)
    
    - **P-W2-45-3 (a)** (the CTO, delegated P2): a fix round inside the paths: a test-design batch (a history with one merge in six, an interrupt case), one engineer (`checker.py` passes over merges whose parents hold the decision's file unchanged; `runner.py` stops the group on any exception: F2, F3), then review round 2, the last (DEC-1010). F4 to F6 are rows.
    - **P-W2-45-5 (a)** (the CTO): the probe folder added.
    - **P-W2-45-4** (the W1-40 case, a widening): with the owner.
    
    ## P-W2-45-4 decided (the owner, DEC-1153 (1), 2026-11-12)
    
    (a): `tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py` added for one test-designer revision: line 49 expects a non-zero exit and RED, its docstring (lines 46-47) says so, `Rewrite-Reason: P-W2-45-1 item 5`; nothing else in the file changes. It rides run 4's batch with P-W2-45-3 (a).
