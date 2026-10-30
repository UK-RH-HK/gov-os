**DEC-953 and DEC-954 (owner, 2026-10-30), read with the common brief's DEC-953 block:** the Gov OS's features are lifted as gates on this repository's development, and this ticket closes on the audit's 10 practices. Where this part names a lifted rule (the close queue, the ratchet lists, the quiet windows), the common brief's block holds. The owner confirmed this ticket goes ahead (DEC-954 Q3). Verification: the two routed cases in the close's serial form, plus the selection `select_tests.py` gives; no full run.

You are the ticket lead for ticket `DAEO-gdzh` (`W2-85`, "W2-54's two time-limit cases routed to the nightly"), profile LITE, a test-revision ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-85` on branch `w2/W2-85`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `403d70b396ff`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-gdzh.md`);
- `tests/acceptance/serial-only.txt`, its header above all: the entry's form, the two routes, the kinds and the rule that no case is listed merely because it is slow;
- how the route is enforced:
  - `src/gov/close/serial.py`: a `nightly` entry is collected by the close and left out of both its phases;
  - `src/gov/close/pytest_plugin/gov_close_serial_only.py`: every listed entry is deselected from the parallel phase;
- how the list's form is held:
  - `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`, `test_every_entry_says_its_route_its_kind_and_its_reason`: its `KINDS` give each kind its route;
  - W2-57's README, the table of routes, with its rows for the live and real-model cases it moved to the nightly (`nightly: live-session`, `nightly: real-model`);
- W2-54's README, the parts on the time limit and on "green here";
- DEC-951 (item 3), DEC-889 (item 5), DEC-906 and DEC-942.

## Why you start now

- **The time-limit case is a load failure, not a defect.** `tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit` refused W2-71's close at 02:12 on 2026-10-30. That close ran beside four leads' suites, at a load of 30 to 70. The case passed in the nightly and in W2-57's close (load 4).
- **The green-here case is the same check, run under `gov check`:** `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here` (row W2-L429: it timed out at 600 s in a parallel run, and passed alone).
- **Closes now run beside leads (DEC-942),** so both cases would refuse closes by load alone.
- **The owner's answer (DEC-951 item 3):** route both cases to the nightly, not onto `load_sensitive`, by a test designer's change with a `Rewrite-Reason:`, as W2-57 did for the live tests.

## The decisions for this run

1. **A fresh independent test designer** (`gov launch`, sandboxed, `--effort high`; its brief must not set `TMPDIR`). It writes in `tests/acceptance/serial-only.txt`, and in `tests/acceptance/W2-54/` only where a text states where these two cases run: the README's sections on them, and a docstring of the two cases if one says it.
   - **Two entries,** one per case, each a `file::function` entry, in the list's form `<entry>  # nightly: <kind>: <reason>`, in the section of its kind.
   - **The kind** must be one that W1-30's r11 and W2-57's list accept on the nightly route, `real-model` or `live-session`, and it must be true of the case.
     - Both cases run the context-reproducibility check over this repository's tickets. The check builds each context through retrieval, which asks this machine's embedder, so `real-model` should fit.
     - The designer confirms this from the code as it stands on `w2/integrate` (`src/gov/context/`, `src/gov/retrieval/`), and says so in its return.
     - If neither kind is true of a case, it writes no line for that case and returns a package: a new kind or route needs W1-30's and W2-57's cases revised, outside this ticket's paths.
   - **The reason** is in words and says what the case asks (the real embedder, over this repository's tickets, within the declared limit), never only that it is slow.
   - **Nothing else changes:** neither case's assertions, no other entry, no case removed, no expectation lowered. No new test case.
   - **`Rewrite-Reason: DEC-951 item 3`** on the commit and in each changed text's note, with `Implements: DEC-951, DEC-889`.
   - **The README of W2-54:** only the sections on these two cases. Run 1 of W2-60a changed other parts of it (the sandboxed worker); leave those as they are.
2. **Your check** (a new worktree has no store: rebuild first, under the rebuild lock).
   - **The selection, by a script file** under `.gov-runtime/scratch/lead/` (never `python3 -c` with braces, DEC-409), with this worktree's `src/`:
     - `gov.close.serial.nightly(<this worktree>)` holds both entries;
     - `gov.close.serial.phase(<this worktree>, <the list's entries>)` leaves both out;
     - a collect-only run of `tests/acceptance/W2-54` with the close's plugin (`-p gov_close_serial_only`, `GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-85`, the plugin folder on `PYTHONPATH`) deselects both and keeps every other W2-54 case that no entry names.
     
     Quote the counts.
   - **W2-54 in the close's form:** the parallel run of `tests/acceptance/W2-54` with the plugin. It must be green, with the two cases deselected.
   - **The two cases as the nightly runs them:** each alone, in its own run, without the plugin, once, under the load gate. Each must be green. The time-limit case takes about 3 minutes; the green-here case about 6, since it runs `gov check` itself outside a close.
   - **The list's readers:** `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`, and `tests/acceptance/W2-57/test_w2_57_serial_list.py` and `test_w2_57_nightly_route.py`. All must be green.
   - **Collect-only over `tests`** (DEC-868).
3. **No full run:** no code changes, and every reader of the list is run. Say so in the return.
   - **Known, if you run it:** this branch changes the serial-only list, so W2-66's `test_no_file_a_plain_run_reads_for_its_configuration_or_collection_changes` is red (DEC-919, row W2-L440). It does not stop your DONE.
4. **No review:** LITE (DEC-498).
5. **`gov checkpoint`** at the end (DEC-511), and `trailer_gate.py` before you return.
6. **Return** DONE (ready to merge, then the close), or PACKAGES.

**Running beside you:**
- W2-60a (round 3) adds one `nightly: live-session` line, for its own live file, to the same list. Keep your lines in their own section; the second ticket to merge merges the first back.
- W2-05 holds `tests/acceptance/W1-02/**` and `src/gov/**/*.py` for git calls.
- W2-84 holds `src/gov/guard/reads.py`.

Touch none of them.

**Estimate:** about 10 lines, and about 1.5 hours with the rebuild and the two alone runs.

**Time:** the test designer gets about 45 minutes.

---
