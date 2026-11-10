# W2-153 — two W1-46 cases and the appended template pair, the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer working under **W2-153** (`.tickets/DAEO-8s85.md`). W2-153 is merged on
integrate. By its S1 and Interface, every launched session gets exactly one pair appended **after** the caller's
arguments: `--append-system-prompt-file <root>/.claude/templates/<stem>.md`. **The CTO has ruled this order is
W2-153's intent, not a bug** (DEC-1112 (3)). It is the order the ticket states, and W2-56's S6 was revised the same
way (`896190341226`).

Two W1-46 cases on integrate assert that the CLI got the caller's arguments "unchanged, in order" as the argv's tail.
With the pair after them, they fail:
- `tests/acceptance/W1-46/test_w1_46_bypass_and_added_directories.py::test_a_harmless_permission_mode_is_launched[accept-edits]`
  (about line 108);
- `tests/acceptance/W1-46/test_w1_46_guard_wiring.py::test_a_headless_workers_ordinary_arguments_pass_unchanged[engineer]`
  (about line 66).

## The change (DEC-866: `Rewrite-Reason:`)
- Revise each assertion so it holds with or without the single appended pair:
  - the caller's arguments appear unchanged, in order, as one contiguous run;
  - what follows them is nothing, or exactly `--append-system-prompt-file <path ending .claude/templates/<stem>.md>`;
  - an extra argument, a dropped one or a reordering still fails.
- Use the same rule as W2-56's revised S6, if it suits: read it in `tests/acceptance/W2-56/`.
- Check W1-46's support module and other cases for the same argv-tail pattern, and revise any you find the same way.
  List them.
- Change nothing else.

## Where you work, rules, return
- Worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`, with integrate merged by the CTO.
  Your tree has W2-153's launcher, since it is merged, so these two cases are red there now. Write only
  `tests/acceptance/W1-46/`.
- Run `tests/acceptance/W1-46` (one pytest call) before and after:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit" --tb=no`,
  with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not found). Expect 2 failed before and 0
  after, everything else unchanged.
- No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict`
  or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the sandbox.
- **Commit** on `w2/W2-153-tests`, only `tests/acceptance/W1-46/`, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-153 appends the role template pair after the caller's arguments by design (S1, its Interface; DEC-1050); W1-46's argv-tail assertions allow exactly that pair (DEC-866)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the assertions revised, the folder's counts before and after, the commit and `TESTS-READY <hash12>`.
