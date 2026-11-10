# D-10 round 2: one inconsistent case in W2-96's S-D10a tests (W2-96, DAEO-ouet)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`, S-D10a).
The CTO's decision PKG-D10a-scope (b) (DEC-1112 (3), DEC-1061 (2)): a formal `gov accept` never enables `lifted`; a
line resting only on lifted cases has `"outcome": "report-only"` and the text form shows `report-only (lifted)` for
it; the top-level `"report_only": ["lifted"]` names the group; `"optin"` names exactly the groups enabled.

## The failing output (implementation head `443ce88f5`, w2/W2-96-d10b, all 90 other D-10 and premise cases pass)
```
FAILED test_w2_96_at_d10a_optin.py::test_s_d10a_a_group_no_mapped_case_needs_is_not_enabled[an-unneeded-breadth-beside-a-report-only-line]
AssertionError: the report names the opt-in groups ['lifted'], expected [] (the groups it enabled)
stdout: {"ok": true, "command": "accept", "result": {"ticket": "TDPL-a961", "outcome": "pass", "error_kind": null,
 "lines": [{"kpi": "success-1", "outcome": "pass", "passed": 3, "failed": 0, "skipped": 0},
 {"kpi": "success-2", "outcome": "report-only", "note": "report-only (lifted)", "passed": 0, "failed": 0, "skipped": 0}],
 "unmapped": {...}, "totals": {"passed": 3, "failed": 0, "skipped": 0}, "report_only": ["lifted"]}, "session": ""}
```
`_enabled` reads group names anywhere in the result except `report_only`, so it counts the line's
`report-only (lifted)` text as an enabled group. Yet the folder's text-form case requires that very text in the line
(the text form prints the result as JSON). The two cases contradict each other.

## The task
- Make the "groups enabled" check read what the report names as enabled (`"optin"`, absent meaning none), not a
  report-only line's own wording, so the variant judges scope (b) as stated above. Change nothing else's meaning.
- Show the D-10 files and the premises file green on the implementation head above, and the variant red if
  `"optin"` held `lifted` (by reasoning or a planted check), in your return. Do not read `src/gov/accept/**`.
- Worktree `/home/usain/gov-os-worktrees/W2-96-d10b-tests`, branch `w2/W2-96-d10b-tests` (head `5e36c7fc5`). Write only
  `tests/acceptance/W2-96/**`. To run against the implementation, use
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-d10b/src` read-only, with your tests' files (never write that tree);
  the heavy slot, your own TMPDIR=/tmp/…, `--optin=lifted --optin=breadth -n 4`, never the full suite.

## Rules
- `EMG-common.md` holds, including its hidden-half rule. No GPU, no installs, never `git worktree prune`.
- Commit on `w2/W2-96-d10b-tests` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1112, DEC-1061"`
  `--trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: the groups-enabled check read a report-only line's wording (PKG-D10a-scope (b)); DEC-866"`
  `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.
- Estimate: 15 minutes. Return the twelve fields, short, with the head commit.
