# D-10's red-fix list: three whole-tree copies W1-28's check cannot run (W2-92, DAEO-n0wb)

You are a fresh **independent test designer**, launched under W2-92's ticket (`.tickets/DAEO-n0wb.md`). The CTO's
helper found these reds tonight, outside the sandbox at integrate `e74b551bc`, each red alone and serial.

## The reds
- `tests/acceptance/W1-28/test_w1_28_fixture_copies.py::test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs`:
  "these functions copy the whole tree of the repository and cannot be run by the check:
  ['W2-13/w2_13_lexical_policy_support.py::pre_s6_src', 'W2-92/test_w2_92_speed.py::base', 'W2-92/w2_92_support.py::base_src'].
  Make each a module-level function with a parameter `root=<ROOT_NAME>` that leaves <the held-out file> out by its
  path, or limit it to named paths (DEC-385)."
- `tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py`: 13 rows over the same three functions (IndexError,
  FileNotFoundError on `produced/.claude/settings.json`, and "these whole-tree copies cannot be run on a synthetic
  root").
- **The cause:** W2-92's `base_src` and `test_w2_92_speed.py::base` (`5214e0f01`, 11-05) and W2-13's `pre_s6_src`
  (`b6eb2267f`, 11-04) copy the whole repository tree in a form W1-28's rule (DEC-385) and W1-50's freeze check
  cannot run.

## The task
1. Bring each of the three into W1-28's form: a module-level function with a parameter `root=<the check's ROOT_NAME>`,
   leaving the held-out file out by its path. Or limit it to named paths, if that serves its suite as well.
   - Read W1-28's check (`tests/acceptance/W1-28/`) and W1-50's freeze cases to get the exact form they run.
   - Keep what each copy is for: W2-92's base tree for the unchanged-bundle and speed cases, W2-13's pre-S6 tree for
     the policy refresh.
2. Lower no expectation in W2-92, W2-13, W1-28 or W1-50.
3. Run outside-the-sandbox-equivalent where you can:
   - `tests/acceptance/W1-28/test_w1_28_fixture_copies.py`;
   - `tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py`;
   - `tests/acceptance/W2-92` (with `CODEINTEL_OFF_PATH=` set to the empty string, so the code-graph tool stays on
     `PATH`; say if the tool cannot start in your sandbox);
   - `tests/acceptance/W2-13`.
   - Report before and after counts, with `--optin=lifted,breadth`.
4. One README line in W2-92's and W2-13's READMEs.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-385: W2-92's and W2-13's whole-tree copies were not in the form W1-28's check and W1-50's freeze run (module-level, root=, the held-out file left out)"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-92-d10b-tests`, branch `w2/W2-92-d10b-tests`, at integrate `e74b551bc`.
- Write only `tests/acceptance/W2-92/**` and `tests/acceptance/W2-13/**`.
- Do not read W2-92's or W2-13's implementation (`src/gov/store/loader.py`, `src/gov/retrieval/**`): DEC-820 (c).
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-d10b-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`. Never read the held-out file's contents; its name is in W1-28's check.
- Commit on `w2/W2-92-d10b-tests` only, with `--trailer "Task: DAEO-n0wb" --trailer "Implements: DEC-1109, DEC-385"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 40 minutes. Return the twelve fields, short:
  - each function before and after;
  - the counts;
  - the head commit.
