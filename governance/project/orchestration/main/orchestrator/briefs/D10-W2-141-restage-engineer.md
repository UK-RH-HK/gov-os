# D-10's red-fix list: W2-141's staged hook rebuilt on the live hook (W2-141, DAEO-xwro; DECIDED-NOT-DONE row 78)

You are a fresh **engineer**, launched under W2-141's ticket (`.tickets/DAEO-xwro.md`). DECIDED-NOT-DONE row 78
says W2-141's staged hook is rebuilt on top of ACT-SETS-GLOBS-1's hook before the lift's re-pin ACT. That ACT is
now live on `w2/integrate` (`9cce7430d`; the live hook's sha256 starts `74f8dbea4761`). This also clears a red on
D-10's list.

## The red (the CTO's helper's run at integrate `adb4f6b4c`: 1 failed, 203 passed)
- **The case:** `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`.
- **What it requires:** `docs/changes/W2-141-hook/pretooluse.py` equals the live `.claude/hooks/pretooluse.py`
  with one change, `if tool in ("Read", "NotebookRead", "Grep", "Bash"):` becoming
  `if tool in ("Read", "NotebookRead", "Grep", "Glob", "Bash"):`.
- **Why it fails:** the staged copy was built on an older hook. The live one has since gained:
  - rule 2b's glob line (ACT-SETS-GLOBS-1);
  - rule 2c (ACT-INDEP-WALLS-1);
  - rule 2d (ACT-OPERATOR-1);
  - whatever else the diff shows.

## The task
1. Rebuild `docs/changes/W2-141-hook/pretooluse.py` from today's live hook, with W2-141's one change and nothing
   else.
   - First read the old staged file against the hook it was built on (`git log` of both paths), and confirm that
     W2-141's only change to `pretooluse.py` was that line. If it changed more, return PACKAGES with the diff.
2. Check the other staged files (`role_reads.py`, the README) still match what the live hook and
   `src/gov/guard/reads.py` need:
   - `test_the_hook_s_block_is_reads_py_s_byte_for_byte` and the rest of `tests/unit/guard/test_w2_141*` must pass;
   - update the README's "built on" line (the hook's sha256 prefix and commit), if it has one.
3. Run, and report:
   - `tests/unit/guard/test_w2_141*`;
   - `tests/unit/hooks`;
   - `tests/unit/guard/test_g14.py` (if present);
   - W2-141's acceptance suite, through `gov accept`: `PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-141`
     (the CTO runs it if it cannot run in your sandbox; say so).
4. Never edit `.claude/` (DEC-315): the staged copy is what the re-pin ACT applies, which is the CTO's work.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-141-d10`, branch `w2/W2-141-d10`, at integrate `adb4f6b4c`.
- Write only `docs/changes/W2-141-hook/**`.
- Never search into `tests/acceptance/W2-141/`: `EMG-common.md`'s exclusion rule, with `W2-141` as the folder.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-141-d10/src` and `TMPDIR` a folder of your own under the sandbox's
    TMPDIR;
  - pytest with `-q -p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite.
- Commit on `w2/W2-141-d10` only, with `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1109, DEC-1093"`
  `--trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 20 minutes. Return the twelve fields, short:
  - W2-141's change confirmed one line;
  - the new staged file's sha256 and the live hook's;
  - each suite's counts;
  - the head commit.
