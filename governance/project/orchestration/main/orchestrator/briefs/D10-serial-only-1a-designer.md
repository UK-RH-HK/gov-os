# D-10 gate: serial-only.txt names no case for W1-16's ui_off in a default run (W2-13, DAEO-zqvn)

You are a fresh **independent test designer**, launched under W2-13's ticket (`.tickets/DAEO-zqvn.md`). It already
changed `tests/acceptance/serial-only.txt` today (`89495ad15`). The CTO decided (delegated, DEC-1112 (3)), option (a)
now, before D-10's full run. **This gates D-10. Work fast and exactly.**

## The red
- `tests/acceptance/serial-only.txt` line 85: `tests/acceptance/W1-16/test_w1_16_ui_off.py  # serial: daemon: every case of the file starts or asks the codebase-memory daemon`.
- D-4's cut (DEC-1061) moved every case of that file to the opt-in suite `breadth`
  (`tests/optin-lifted-breadth.txt` lines 274-280, `# cap`).
- So in a run without `--optin=breadth` the entry names no collected case. The close's serial plugin then stops the
  whole serial phase at collection, exit 4 (`gov_close_serial_only.py:54-60`, "any one empty entry"):
  - a full close refuses;
  - `nightly.sh` can read green with no serial case run.
- Found by the W2-13 review's F1 (`/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/D10-W2-13-review.md`).

## The task
1. **Check every entry of `serial-only.txt`, not only line 85,** against a default run's collection (no `--optin`):
   - list each entry that names no collected case;
   - use the same reading the plugin uses: the text before ` #`, a file or a `file::function` prefix of node ids.
2. **For each such entry** (expected: the ui_off file alone), make the list name no empty entry in a default run,
   with its reason:
   - either re-point it to node ids the default run does collect (if some of its cases stay in the full run, which
     the cap list says they do not);
   - or comment it out in the file's own way, keeping it visible and stating why. For example:
     `# D-10 (DEC-1112 (3), the CTO's (a)): out while D-4's cut keeps every case in breadth (DEC-1061); the plugin fix (b) follows; was: <the line>`.
   - Choose, and say why. The daemon cases still need the serial route when they do run (in an opted-in run). Say what
     happens to them then. (b), the plugin fix, will restore it.
3. **Prove the serial phase now collects:**
   - run the plugin's own collection over the list in a default run;
   - the readers W2-57 (`test_w2_57_serial_list.py`, `test_w2_57_nightly_route.py`), W1-30's r11/r12/r13 files and
     `tests/unit/close/test_serial*.py` must stay as they were;
   - W1-30's `test_w1_30_r11_declared_here.py` (opt-in) may change; report it.
   - The simplest form: `python3 -m pytest -p gov_close_serial_only …` as `gov close` does; read
     `src/gov/close/serial.py` for the exact flags. You may read it: it is not this ticket's implementation.
4. Every commit carries `--trailer "Rewrite-Reason: DEC-1112 (3), DEC-1061: an entry of serial-only.txt that names no case a default run collects stops the close's serial phase; out until the plugin treats it as not in the run"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-13-d10b-tests`, branch `w2/W2-13-d10b-tests`, at integrate `af850b6f2`.
- Write only `tests/acceptance/serial-only.txt` (and W2-13's README, one line, if you like).
- Use the heavy slot, `PYTHONPATH=<worktree>/src`, your own TMPDIR, and `PYTHONUSERBASE=/home/usain/.local` if HOME
  is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-13-d10b-tests` only, with `--trailer "Task: DAEO-zqvn" --trailer "Implements: DEC-1109, DEC-1112"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 15 minutes. Return the twelve fields, short:
  - the empty entries found;
  - the change;
  - the collection proof;
  - the readers' counts;
  - the head commit.
