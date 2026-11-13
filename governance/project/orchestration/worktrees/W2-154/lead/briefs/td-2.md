# Brief td-2: W2-154 (DAEO-l4gf), independent test designer, a harness fix to your own tests (run 3)

You are the independent-test-designer (MR-3) for ticket DAEO-l4gf (W2-154), profile STANDARD, class C2. Your run-2
tests (commit 22ccf2150, merged f6dbab76b) are green in a run that sets `PYTHONUSERBASE`, but RED in the lead's full
verification run (the close's form, the real `HOME`, no `PYTHONUSERBASE`). The fault is in the test harness, not the
behaviour under test: fix the harness only; never weaken a check.

## The failing output (lead_verify, head 0269b817e3cd; the same 7 are red on the base f6dbab76b in the same environment)
```
tests.unit.close.test_serial_w2_154_plugin test_s1_i1_i2_an_entry_whose_every_case_the_optin_list_leaves_out_is_not_in_the_run | AssertionError: an entry the opt-in list leaves out stopped the serial phase:   exit 1   --- stdout      --- stderr   /usr/bin/python3: No module named pytest      --- out file: []   --- ran: []
tests.unit.close.test_serial_w2_154_plugin test_s1_i2_the_run_goes_on_with_the_entries_that_ran_and_names_only_the_one_that_is_out | exit 1 ... /usr/bin/python3: No module named pytest
tests.unit.close.test_serial_w2_154_plugin test_s1_i1_an_entry_with_some_of_its_cases_kept_is_in_the_run | exit 1 ... No module named pytest
tests.unit.close.test_serial_w2_154_plugin test_f1_an_entry_that_names_no_case_and_no_optin_list_explains_stops_the_serial_run_with_exit_4 | exit 1 ... No module named pytest
tests.unit.close.test_serial_w2_154_plugin test_f1_with_an_entry_that_is_out_given_too_the_one_that_names_no_case_still_stops_the_run | exit 1 ... No module named pytest
tests.unit.close.test_serial_w2_154_plugin test_s2_i1_in_a_run_that_opts_in_by_the_variable_... | exit 1 ... No module named pytest
tests.unit.close.test_serial_w2_154_plugin test_s2_i1_in_a_run_that_opts_in_by_the_option_... | exit 1 ... No module named pytest
```
The lead's diagnosis: `run_plugin` in `tests/unit/close/test_serial_w2_154_support.py` (about line 151-153) sets the nested
run's `HOME` to the work folder; this machine's pytest is installed in the user site (`/home/usain/.local/lib/python3.12/
site-packages`), which the child interpreter finds through `HOME` unless `PYTHONUSERBASE` names it. Reproduce with:
```
env -u PYTHONUSERBASE TMPDIR=/tmp/w2-154-td2 PYTHONPATH=/home/usain/gov-os-worktrees/W2-154-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/close/test_serial_w2_154_plugin.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A fix that holds in both environments: keep the parent's user site for the child, e.g. `env.setdefault("PYTHONUSERBASE",
site.getuserbase())` (the standard library's `site`), or another way you judge better; check the nightly helper
(`run_nightly`, which also sets `HOME`) needs nothing (its cases were green in the lead's run). Look at how other tests in
`tests/unit/close/` that start a nested pytest with their own `HOME` keep pytest importable, and follow the project's form.

## Where you work
- Worktree / branch: /home/usain/gov-os-worktrees/W2-154-tests  /  w2/W2-154-tests (write here only).
- Write ONLY `tests/unit/close/test_serial_w2_154_support.py` (and, only if needed, the other `tests/unit/close/test_serial_w2_154_*.py`).
  Do not read or touch the engineer's work on this ticket (`src/`, `nightly.sh`, `tests/unit/close/test_serial_eng_w2_154.py`).
- The ticket (read-only): /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-l4gf.md. Context packet beside this brief: td2-context.md.

## How you run tests (every pytest, no exception; make /tmp/w2-154-td2 first, or use $TMPDIR/w2-154-td2 if /tmp is read-only to you)
Show green BOTH ways, on this worktree's head:
1. the reproduction above (no `PYTHONUSERBASE`, the real `HOME`) — all of `tests/unit/close/test_serial_w2_154_plugin.py`,
   `tests/unit/close/test_serial_w2_154_nightly.py`, `tests/unit/close/test_serial.py`;
2. the same three files with `PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-154-tests/.gov-runtime/scratch/empty-home` (make that folder).
Every case must keep failing for missing behaviour where it did on the base: do not change any assertion.

## Commit (your paths only, in your worktree)
```
git commit -m "W2-154: the plugin cases' nested run keeps the user site (harness fix; no check changed)" --trailer "Task: DAEO-l4gf" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1112, DEC-1061, DEC-889, DEC-549, DEC-1109" -- tests/unit/close/test_serial_w2_154_support.py
```
No `Role: owner`, no `Decided-by:`. Leave `git status --short` empty.

## Rules
- Reads are open, except secrets, held-out qualification material's contents, the hidden half of any evaluation set, and the
  engineer's work on this ticket. No `gov retrieve` and no `gov context` in the sandbox: Read and Grep, then once more in other words.
- Anything longer than one line goes in a script file under $TMPDIR, run with `bash <file>` or `python3 <file>`; scripts that `cd` stop if the `cd` fails.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No new ticket and no widening; a gap comes back in `unresolved`.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` quote both pytest summary lines; in `files_changed:` the commit hash12 and paths.
