# W2-153 — W2-56's S6 assertion and the appended template pair, the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer working under **W2-153** (`.tickets/DAEO-8s85.md`). W2-153 appends exactly
one pair to every launched session's arguments, after the caller's: `--append-system-prompt-file <root>/.claude/templates/<stem>.md`.
That is its S1 and its Interface ("appended to the CLI arguments the launcher builds (after the caller's)").
W2-56's acceptance case `tests/acceptance/W2-56/test_w2_56_refused_arguments.py::test_s6_guard_arguments_that_are_not_refused_start_the_session`
(both parameters) asserts `launch.call["args"][-len(args):] == args`, that the caller's arguments end the argv. With
W2-153 they are followed by the one pair, so the case fails on W2-153's branch, though W2-56's S6 still holds.

## The change (DEC-866: `Rewrite-Reason:`)
- Revise that assertion so it holds with or without the single appended pair. The caller's arguments must appear in
  order, as one contiguous run. What follows them is either nothing or exactly
  `--append-system-prompt-file <path ending .claude/templates/<stem>.md>`. Anything else still fails: an extra
  argument, a dropped one, a reordering.
- Look in W2-56's other cases (and their support module) for the same pattern, the caller's arguments taken as the
  argv's tail, and revise each the same way. List them.
- Change nothing else in W2-56. Run the folder on your tree (integrate's launcher, no pair): every count stays as
  before.

## Where you work, rules, return
- Worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`. Write only
  `tests/acceptance/W2-56/`.
- Never open `/home/usain/gov-os-worktrees/W2-153` or read W2-153's implementation. The behaviour is stated above.
- Run only `tests/acceptance/W2-56`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src python3 -m pytest tests/acceptance/W2-56 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit" --tb=no`.
  No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the
  sandbox.
- **Commit** on `w2/W2-153-tests`, only `tests/acceptance/W2-56/`, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-153 appends the role template pair after the caller's arguments (S1, DEC-1050); S6's argv-tail assertion allows exactly that pair (DEC-866)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the assertions revised, the folder's counts before and after, the commit and `TESTS-READY <hash12>`.
