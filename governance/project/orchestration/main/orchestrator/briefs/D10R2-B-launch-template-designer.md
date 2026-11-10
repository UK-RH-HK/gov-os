# D-10 run 1's red group B (18 cases): launch fixtures without the role template (DAEO-8s85, W2-153)

You are a fresh **independent test designer**, launched under W2-153's ticket (`.tickets/DAEO-8s85.md`): W2-153 made
`gov launch` require the role template, and these suites' fixtures were not brought along. D-10 (DEC-1122 (3)) needs
the fix before run 2. The templates are approved (DEC-1116, 1.0.1 by DEC-1122): they do not change.

## The red
At integrate's head `c9742b08910a`: 17 cases of `tests/acceptance/W2-50/` (`test_w2_50_launcher.py` 10,
`test_w2_50_review_findings.py` 4, `test_w2_50_owner_answers.py` 2, `test_w2_50_short_round.py` 1) fail with
`gov launch: LAUNCH_NO_TEMPLATE: the role template <planted home>/gov-os-worktrees/W2-90/.claude/templates/role-engineer.md is missing`
(exit 1, no session recorded). `tests/acceptance/W1-28/test_w1_28_launch_product_spec.py::test_the_extra_cli_arguments_reach_the_product_spec_session`
fails too (exit 0, but the arguments check fails): confirm whether it is the same cause (the template prompt now
passed with `--append-system-prompt` changes the argument list) and fix it only if it is W2-153's change.

## The task
1. Make the planted worktrees carry the role template the product now requires (taken from the kernel's own
   template, as W2-153's cases do it), so each case tests what it tested before. Lower no other expectation; do not
   make a case accept LAUNCH_NO_TEMPLATE.
2. Run, through the heavy slot (`EMG-common.md`), with `PYTHONPATH=<your tree>/src`:
   `python3 -m pytest tests/acceptance/W2-50 tests/acceptance/W1-28 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
   Report counts before and after; a case red for another reason is named, not fixed. Then the same two suites with
   `--optin=lifted` added: run 1's lifted step had **296 more W2-50 cases** red on the same LAUNCH_NO_TEMPLATE (the
   lifted list keeps them out of the default run); they must turn green with the same fixture change.
3. One line in each changed suite's README.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-153-d10r2-tests`, branch `w2/W2-153-d10r2-tests` (from integrate at
  `c9742b08910a`). Write only `tests/acceptance/W2-50/**` and `tests/acceptance/W1-28/**`.

## Rules
- `EMG-common.md` holds. Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No installs, never the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1122, DEC-1116"
  --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-153: gov launch requires the role template; the fixtures planted none"
  --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short: the change, counts before and after, W1-28's cause, the head commit.
