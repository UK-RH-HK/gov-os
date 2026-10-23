You are the ticket lead for ticket `DAEO-c1uz` (`W2-66`, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`.

**This is run 1.** `git log --oneline -1` must show `c2d539c6`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

The owner passed the review point on 2026-10-23 (DEC-899, in your register). This ticket's ticket file and card are confirmed as written: selection and evidence only, using the test map (`governance/project/test-map.yaml`), with lens I's P-IS-1 (a) and P-IS-2 (a). It is keystone 2's first ticket and rides in the first re-pin. Read the ticket file (`.tickets/DAEO-c1uz.md`) and the card (`docs/plan/WAVE_2_WBS.md` §2, W2-66) first. Then read lens I's synthesis (`docs/assessment/2026-10/I-SYNTHESIS.md`): §4's W2-66 block, P-IS-1 and P-IS-2.

## The owner's decisions for this run

- **DEC-899 item 2, the merge order.** W2-07 (`DAEO-r9ss`) is built in parallel with this ticket, in its own worktree. Both edit `src/gov/close/command.py`: this ticket the record's evidence lines and the calls into its new modules, W2-07 the gates.
  - **W2-07 merges first.**
  - When you return DONE, the orchestrator does not merge you until W2-07 has merged. You then merge `w2/integrate` back into this branch, re-verify in full, and get a fresh FULL probe on the merged head before the re-pin. Expect a second run for that.
  - Keep your edits to `command.py` small and in their own functions, so that merge is easy.
- **DEC-896 item 2:** the test-selection lists live in the test map, which this ticket creates (with its schema and the template's copy). The path map is a shared record that no ticket's paths name: never write `governance/project/path-map.yaml`. Its `test_inputs` key moves into the test map; its removal from the path map is the orchestrator's edit, so name it in your return.
- **DEC-892 b, the per-test limit:** pytest-timeout with the signal method. It is an owner install, not yet in the tool registry.
  - The orchestrator brings it to the owner as an install package now.
  - Your test designer writes the limit's tests regardless.
  - If your engineer reaches the limit's code and pytest-timeout is still not installed (`python3 -c "import pytest_timeout"` fails), build everything else and return PACKAGES for that KPI only.
- **DEC-892 a:** no worksteal. The distribution mode is a setting, left at today's default.
- **MR-3 (core-mutation):** your `allowed_paths` hold no `tests/acceptance/` path. W1-30's regression file, named at the end of your ticket file, is your test designer's to revise (with a `Rewrite-Reason:`), not your engineer's.
- **DEC-898, the scratch budget:** as in the common brief below. Report the scratch size in every return.

## This run's order

1. **Tests first:** a fresh independent test designer, launched sandboxed, `--effort xhigh` (a FULL ticket's designer, DEC-839), on every KPI line of the ticket file, FULL proportion.
   - It also writes the revision of W1-30's `test_regression_includes_other_acceptance_folders`, with its `Rewrite-Reason:`.
   - Its fixture repository must show the shared-core widening, a one-module scope, an unplaced file, a missing test map, and a record-only commit running the record-reading set.
2. **Check red yourself,** for the reason each README states.
3. **Implement:** a fresh engineer, launched sandboxed, `--effort high`, inside the allowed paths only.
4. **Verify** as the loop says, in the close's form (one parallel run, then the serial cases, with JUnit XML), with `gov check` after a rebuild.
5. **FULL review:** a fresh read-only reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final code. Commit the probe record under `docs/probes/DAEO-c1uz/`.
6. **The fixture trial (the ladder, DEC-884 item 4),** measured, in `docs/research/W2-66-scoped-close.md`:
   - a shared-core change runs everything;
   - a one-module change runs its suites;
   - a record-only commit runs the record-reading set;
   - the time of each.
7. **Return** DONE (do not merge; W2-07 goes first), or PACKAGES.

**Time:** a worker launched through `gov launch` is stopped at the Bash tool's two-hour limit and its return is lost. Give each worker a budget of about 90 minutes, and split larger work into rounds.

---
