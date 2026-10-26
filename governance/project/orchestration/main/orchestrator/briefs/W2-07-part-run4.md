You are the ticket lead for ticket `DAEO-r9ss` (`W2-07`, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`.

**This is run 4, round 2 of the ticket (DEC-923, DEC-924).** `git rev-parse --short=12 HEAD` must show `80ec31ab61b8`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**First,** merge `w2/integrate` into `w2/W2-07` (`git merge --no-ff w2/integrate`, with `Task: DAEO-r9ss` and `Role: orchestrator` in the final trailer block). The ticket's round 1 is already merged and pinned. The merge brings round 2's KPI lines, the decisions and today's head. Then read:
- the ticket file (`.tickets/DAEO-r9ss.md`): KPI 3 as amended, the new round-2 KPI, and the new failure line;
- the card in `docs/plan/WAVE_2_WBS.md` §2 (the "Round 2" note);
- DEC-896 item 1, DEC-891, DEC-906, DEC-923 and DEC-924.

## Why you start now

- **Three closes are blocked.** After the first re-pin, the close's work-without-a-task gate still refuses W2-58, W2-63 and W2-07 on old decision-record commits that round 1's rule does not measure.
- **The cause is the rule's narrow reading.** `gov.close.gates.decision_records` counts:
  - only `docs/plan/`, `governance/project/prompts/`, `governance/project/briefs/`, `governance/project/orchestration/`, the register and the path map as records, not `.tickets/`;
  - only decisions that are owner decisions in force, so a delegated decision, or one later superseded, does not count.
- **The owner's answer (DEC-923 item 2, DEC-924 item 3):** round 2, beside W2-57. The second re-pin carries it.

## The decisions for this run

- **The rule, exactly (DEC-923 item 2):**
  - **What counts as measured:** a decision-record commit (`Task: decision-record`) that changes only governance records and names an ACCEPTED decision.
    - **Governance records** are DEC-891's records (`.tickets/`, `docs/checkpoints/`, `docs/close/`, `docs/probes/`, the register, the plan files, `governance/project/orchestration/`), beside the prompts, the briefs and the path map.
    - **The decision** may be the owner's or a delegated one, also when it was later superseded or changed. A decision never ACCEPTED does not count.
  - **The owner-committed lists:** the work-without-a-task gate also counts as measured a commit that `acceptance_exemptions` or `accepted_history` names, each under its ACCEPTED owner decision, read as the trailer gate and W1-01 read them.
  - **A `Role: owner` trailer alone measures nothing:** a trailer is only text until W2-44 (DEC-906).
  - **Any other path** (code, tests, the kernel, `docs/assessment/`) keeps a commit unmeasured unless a list names it.
- **Your files (DEC-924 item 3, an owner exception to the overlap rule, beside W2-57 in flight):**
  - **the engineer writes only:** `src/gov/close/gates.py`, gate (h)'s line in `src/gov/close/command.py` (the `recorded` subtraction before `_check_unmeasured`), `src/gov/close/history.py` (its readers, only if needed), and new unit tests `tests/unit/close/test_w2_07_*.py`;
  - **W2-57 owns** `src/gov/close/serial.py` and `tests/unit/close/test_serial*`. Never touch them, nor any other file of `src/gov/close/`.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`). It revises only `tests/acceptance/W2-07/`, chiefly `test_w2_07_decision_records.py`, each change with `Rewrite-Reason: DEC-923`, with no expectation lowered. One case per line of the rule, in temporary repositories:
  - a record-only commit under a delegated decision, and one under a later-superseded decision, measured;
  - one with a ticket file, measured;
  - one with any non-record path, unmeasured;
  - a commit named on each owner list, measured;
  - a `Role: owner` decision-record commit with a non-record path that no list names, unmeasured;
  - a decision never ACCEPTED, unmeasured.
- **Your own check on this repository** (a script file under `.gov-runtime/scratch/lead/`; never `python3 -c` with braces, DEC-409). Run the judge's work-without-a-task gate from this worktree's `src` for `DAEO-5j8b`, `DAEO-pl6k` and `DAEO-r9ss`, as the orchestrator's `tools/unmeasured_gate.py` does, and report the unmeasured count for each.
  - **Expected:** 0 for `DAEO-5j8b` and `DAEO-pl6k`.
  - **For `DAEO-r9ss`:** 1 (`611955faffaa`) until the owner commits its `accepted_history` entry (DEC-924 item 1), then 0. Say which you saw, and whether that entry was on the integrate head you merged.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **Known:** W1-19's warm-query case is on `load_sensitive`. W2-54's green-here case may time out under load (row W2-L429; re-run it alone). DEC-919's known red applies if your branch changes the serial list (it must not).
  - Any other red is named with its cause.
- **No review (STANDARD).**

## This run's order

1. The merge of `w2/integrate`.
2. Tests first (the test designer), then **check red yourself.**
3. The engineer.
4. Your check on the three tickets.
5. Rebuild and verify in full.
6. **Return** DONE (ready to merge; it rides the second re-pin), or PACKAGES. If W2-57 merged before you, the orchestrator merges `w2/integrate` back into your branch first, and you re-verify (DEC-924 item 3).

**Estimate:** about 30 to 60 lines in `gates.py` and `command.py`, about 5 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
