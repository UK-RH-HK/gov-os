# Brief td-3: W2-154 (DAEO-l4gf), independent test designer, S4: W1-16's ui_off entry back in serial-only.txt (run 4)

You are the independent-test-designer (MR-3) for ticket DAEO-l4gf (W2-154), profile STANDARD, class C2. S1-S3 are built
and verified on this branch (the close's serial plugin now names an entry whose every case an opt-in list leaves out as
"not in this run" instead of stopping the serial phase with exit 4). The owner decided S4 (a) on 2026-11-13: the ticket's
paths gain `tests/acceptance/serial-only.txt` for S4 only (df8ba7007, merged into this branch). Your one job is S4.

## S4 (the KPI line)
S4 Once S1 holds, W1-16's ui_off entry returns to serial-only.txt (commented out on 2026-11-10 by the D-10 gate,
b78f862a9 / 6afff5d74), restored by a test designer with its Rewrite-Reason; the designer writes
tests/acceptance/serial-only.txt, never the implementer. Verify: `git log` on the file shows the ui_off line restored in a
commit with `Role: independent-test-designer` and a Rewrite-Reason, and no commit by the engineer role touches that file.

## What to do
1. In `tests/acceptance/serial-only.txt` (about lines 84-88), the D-10 comment block reads "out while D-4's cut keeps ... Was:"
   followed by the commented-out line
   `# tests/acceptance/W1-16/test_w1_16_ui_off.py  # serial: daemon: every case of the file starts or asks the codebase-memory daemon`.
   Restore that entry as a live line in its place among the other W1-16 daemon entries, and replace the D-10 comment block
   with a short comment (one or two lines) saying why it is safe now: every case of the file is in
   `tests/optin-lifted-breadth.txt` (`# cap`, DEC-1061), so a default run names the entry "not in this run" (W2-154 S1,
   DEC-1112 (3)); a run with `--optin=breadth` runs its cases serially (S2). Change nothing else in the file.
2. Check, with `--collect-only` only (never run the ui_off cases: they start the codebase-memory daemon), on this worktree:
   a. the serial-afterwards collection in a default run names the entry not in this run and exits 0:
      `GOV_CLOSE_SERIAL_ONLY_GIVEN=tests/acceptance/W1-16/test_w1_16_ui_off.py GOV_CLOSE_SERIAL_ONLY_OUT=$TMPDIR/w2-154-td3/out.txt`
      with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-154-tests/src:/home/usain/gov-os-worktrees/W2-154-tests/src/gov/close/pytest_plugin`,
      `python3 -m pytest tests/acceptance/W1-16/test_w1_16_ui_off.py --collect-only -q -p gov_close_serial_only -p no:cacheprovider`
      → expect the line `gov_close_serial_only: not in this run: tests/acceptance/W1-16/test_w1_16_ui_off.py`, exit 0, and the out
      file naming the entry. (Read `src/gov/close/pytest_plugin/gov_close_serial_only.py` and `src/gov/close/command.py` around
      lines 900-975 for the exact variables if this form does not match; you may read the code here.)
   b. the same with the opt-in switched on (`--optin=breadth`, or the project's variable for it; see `tests/conftest.py` /
      `conftest.py`) collects the file's seven cases and prints no "not in this run" line.
3. Run the existing cases that read the project's real serial-only.txt and could notice a new live entry, and show them green
   (or name a red with file:line and its cause; do not change them, they are outside your paths):
   `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`, `tests/acceptance/W2-57/` (the list cases),
   `tests/acceptance/W1-15/test_w1_15_parallel_scan.py`, `tests/unit/close/test_serial.py`, `tests/unit/close/test_serial_w2_154_plugin.py`.
   Skip any case whose id contains real, green_here or time_limit, and anything marked local_only.

## Where you work
- Worktree / branch: /home/usain/gov-os-worktrees/W2-154-tests  /  w2/W2-154-tests (write here only).
- Write ONLY `tests/acceptance/serial-only.txt`. Do not touch the engineer's work (`src/`, `nightly.sh`, `tests/unit/close/test_serial_eng_w2_154.py`).
- The ticket (read-only): /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-l4gf.md. Context packet beside this brief: td3-context.md.

## How you run tests (every pytest, no exception)
Make `/tmp/w2-154-td3` first (or `$TMPDIR/w2-154-td3` if /tmp is read-only to you) and set `TMPDIR` to it. Every pytest:
```
env TMPDIR=/tmp/w2-154-td3 PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-154-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-154-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <PATHS> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
(make the empty-home folder first). Never a pytest outside heavy_slot.sh. A heavy_slot refusal (memory/CPU/slot gate) is a wait: retry when it opens.

## Commit (your path only, in your worktree)
```
git commit -m "W2-154 S4: W1-16's ui_off entry back in serial-only.txt (the plugin names it not in this run in a default run)" --trailer "Task: DAEO-l4gf" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1112, DEC-1061, DEC-889, DEC-549, DEC-1109" --trailer "Rewrite-Reason: DEC-1112 (3) and the owner's S4 (a), 2026-11-13: with W2-154's S1 the close's serial plugin names an entry whose every case an opt-in list leaves out as not in this run, so W1-16's ui_off entry (out since the D-10 gate, 6afff5d74) returns" -- tests/acceptance/serial-only.txt
```
No `Role: owner`, no `Decided-by:`. Leave `git status --short` empty.

## Rules
- Reads are open, except secrets, held-out qualification material's contents, the hidden half of any evaluation set. Never open
  the evaluation sets' root or any hidden or memory-verdict folder. No `gov retrieve` and no `gov context` in the sandbox: Read and
  Grep, then once more in other words.
- Anything longer than one line goes in a script file under $TMPDIR, run with `bash <file>` or `python3 <file>`; scripts that `cd` stop if the `cd` fails.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No new ticket and no widening; a gap comes back in `unresolved`.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` quote the two collect-only outcomes (the "not in this run" line and exit code; the seven cases collected with the
opt-in) and each pytest summary line; in `files_changed:` the commit hash12 and the path.
