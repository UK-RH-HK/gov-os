Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-154/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-1: W2-154 (DAEO-l4gf), engineer, build (run 3)

You are the engineer for ticket DAEO-l4gf (W2-154), profile STANDARD, class C2. Implement the ticket's Interface I1-I4
(KPIs S1, S2, S3; failure lines F1, F2, F3) until its acceptance tests pass. Use your test-driven-development and
systematic-debugging skills. S4 is NOT yours and NOT in this run (never touch `tests/acceptance/serial-only.txt`).

## Where you work
- Worktree / branch: /home/usain/gov-os-worktrees/W2-154  /  w2/W2-154 (write here only; you are its one writer).
- Allowed paths (the guard refuses anything else; F3 judges `git diff --name-only` against the base):
  - src/gov/close/pytest_plugin/gov_close_serial_only.py
  - src/gov/close/serial.py
  - src/gov/close/command.py  (the serial-afterwards run's lines only: where its env is built and its stated record made,
    about lines 933-990; leave the `--verify` path, lines ~1572-1620, as it is)
  - governance/project/orchestration/nightly/nightly.sh
  - tests/unit/close/test_serial* (do not open or edit the acceptance tests `tests/unit/close/test_serial_w2_154_*.py`
    and `tests/unit/close/test_serial.py`: they are the independent test designer's; the guard denies you their
    contents. You may add your own unit tests in a NEW file, e.g. `tests/unit/close/test_serial_eng_w2_154.py`, if useful.)
- The ticket (read-only): /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-l4gf.md — read it whole, above all its
  "## Interface" section (I1-I4). The Interface is the contract the acceptance tests hold you to; implement it literally:
  the exact strings, the variable names, the record keys.
- Sources (grep by id only in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md): DEC-1112 (item 3),
  DEC-1061, DEC-889 (item 5), DEC-549, DEC-1109. The context packet is beside this brief: eng-context.md.
- Read for the ground: `src/gov/close/pytest_plugin/gov_close_serial_only.py` (70 lines; lines 51-61 are the serial-afterwards
  branch that raises today), `src/gov/close/serial.py`, `src/gov/close/command.py:849-997` (`_run_tests`),
  `governance/project/orchestration/nightly/nightly.sh` (lines 127-128 read ENTRIES and exit 2 on none; 211-222 the serial
  phase; 224 nightly_alone.py; 230 the verdict), `governance/project/orchestration/nightly/nightly_alone.py` (read only,
  never change it), the project's opt-in mechanism in `tests/conftest.py` (it reports opted-out cases through
  `config.hook.pytest_deselected`, deselected not skipped), and `governance/project/orchestration/reviews/D10-W2-13-review.md` (F1).

## What to build (the Interface, with what the lead knows of the harness)
- **I1 (plugin).** In the serial-afterwards run (`GOV_CLOSE_SERIAL_ONLY_OF` and `GOV_CLOSE_SERIAL_ONLY_GIVEN` set), the
  plugin's `pytest_collection_modifyitems` is `trylast=True` (e.g. `@pytest.hookimpl(trylast=True)` — import pytest lazily or
  set the attribute so the module stays standard-library only at import) and it records every item other plugins passed to
  `pytest_deselected` (implement a `pytest_deselected(items)` hook in the plugin that collects their node ids, relative to the
  project's root as `_node` gives them). For each given entry: a collected case -> it runs; no collected case but at least one
  deselected case it names -> "not in this run"; neither -> `pytest.UsageError` "no case is named by the entry of
  tests/acceptance/serial-only.txt: <entries>" (exit 4), exactly as today. Never read `tests/optin-lifted*.txt`.
  Mind the order: the project's conftest's own modifyitems must have run before yours (trylast), and the plugin's
  parallel-run branch (no GIVEN) must behave exactly as today.
- **I2 (record).** For each such entry print `gov_close_serial_only: not in this run: <entry>` (one line each; stdout via the
  terminal reporter or print is fine, but it must reach the run's output), and write the entries, one per line, to the file
  named by `GOV_CLOSE_SERIAL_ONLY_OUT` (only when that variable is set; write it, even empty, in the serial-afterwards run).
  pytest itself ends exit 5 when every given case is deselected: when every given entry is out (and no case was collected),
  the plugin must make the run end exit 0 (e.g. `pytest_sessionfinish` setting `session.exitstatus = 0` when it was 5 and the
  plugin recorded entries out). In `command.py`, for the serial-afterwards run only: set `GOV_CLOSE_SERIAL_ONLY_OUT` in that
  run's env to a fresh file (outside the project's tree, e.g. a tempfile), read it after the run, and its stated record gains
  `"not_in_this_run": [<entry>, ...]` while `"cases"` keeps only the entries that ran. When every given entry is out, the close
  counts a serial run of 0 cases with no finding (check `_one_test_run`/`_told_run`'s exit-code and "stated no result" rules
  so an all-out run is not a finding). Keep `_run_tests(..., stated=...)`'s signature and the stated record's form for every
  other key and run.
- **I3 (nightly.sh's serial lines).** N = the number of `<testcase>` elements in `$JUNIT/serial.xml` (0 when the file is
  missing). Entries declared: append `serial: N cases run` to run.txt. Nothing declared: `serial: 0 declared`, the serial phase
  skipped, not red (replaces today's `no serial-only entry read` / exit 2 at line 128). When entries are declared and N is 0,
  or the serial phase's exit is neither 0 nor 1, append — after `nightly_alone.py`'s output, so it is the LAST `verdict:` line
  of run.txt — `verdict: red serial: 0 cases run` or `verdict: red serial: collection error, exit E` (E the exit). The existing
  verdict grep (line 230) then reads red and the P1 ping follows. Decide and state which wins when both hold (a collection
  error that also ran 0 cases): the lead suggests the collection error line.
- **I4 (test seam).** With `NIGHTLY_SERIAL_STUB=<file>` set, nightly.sh skips the clone, the seed, the secrets switch, the
  rebuild, the gate, the slots and both suites; it sources the stub (the stub sets `ENTRIES`, `s_exit`, `CLONE` and writes
  `$JUNIT/serial.xml`), then runs only the serial count and verdict steps (nightly_alone.py, the serial lines, the verdict, the
  digest, the ping). The tests run `nightly.sh night` on a copy with the start conditions met and a fake disk gate and fake
  `nightly_estimate.py`, so put the seam after the start-conditions loop and the disk gate. Keep the night's other behaviour
  unchanged when the variable is unset.
- **Never change** nightly.sh's lines that begin `ORCH=`, `REPO=`, `RUNS=`, `JUNIT=`, `PING=` or `  window_end=` (the test
  harness rewrites each, and needs exactly one of each). Never run the real nightly (no `bash nightly.sh` without
  `NIGHTLY_SERIAL_STUB`, and only on a copy whose paths you rewrote under your TMPDIR).

## How you run tests (every pytest, no exception)
```
mkdir -p /tmp/w2-154-eng /home/usain/gov-os-worktrees/W2-154/.gov-runtime/scratch/empty-home
env TMPDIR=/tmp/w2-154-eng PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-154/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-154/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/close/test_serial_w2_154_plugin.py tests/unit/close/test_serial_w2_154_nightly.py tests/unit/close/test_serial.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
You may RUN the acceptance tests by path (that gives you their failure output) even though you may not read their source.
Also run, the same way, `tests/unit/close/` as a folder with `-m "not local_only" -k "not real and not green_here and not
time_limit"` once at the end, to show nothing else in the close broke (name any red there with its one-line reason; if a red
is not yours, show it is red on the base too: `git stash` is forbidden — use `git worktree add /tmp/w2-154-eng/base f6dbab76b`
and remove it after). A resource gate's refusal is a wait: retry when it opens.

## Commit (your paths only, in your worktree; one or more commits)
```
git commit -m "W2-154: <what>" --trailer "Task: DAEO-l4gf" --trailer "Role: engineer" --trailer "Implements: DEC-1112, DEC-1061, DEC-889, DEC-549, DEC-1109" -- <your paths>
```
`Task:` is DAEO-l4gf; `Implements:` only these ids. No `Role: owner`, no `Decided-by:`. Leave `git status --short` empty at the end.

## Rules
- Reads are open, except secrets, held-out qualification material's contents, the hidden half of any evaluation set, and the
  test designer's acceptance tests on this ticket. No `gov retrieve` and no `gov context` in the sandbox: search with Read and
  Grep, then search once more in different words.
- Anything longer than one line goes in a script file under /home/usain/gov-os-worktrees/W2-154/.gov-runtime/scratch/,
  run with `bash <file>` or `python3 <file>`. Write files with Write/Edit and absolute paths; literal paths as write targets.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No new ticket and no widening: a gap in the Interface comes back in `unresolved` as a question, not a guess.
- No `git stash`, no merge, no push, no edit of `.tickets/` or the register.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` quote the pytest summary line of the acceptance run and of the folder run; in `files_changed:` each commit's
hash12 and paths; in `tests:` the counts per file and every red left with its one-line reason.
