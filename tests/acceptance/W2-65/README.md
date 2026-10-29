# W2-65 acceptance tests (DAEO-e82f, LITE)

**The guard's hook lines refuse a call when the guard program cannot run** (DEC-880 item 3, P-W2-59-8 (b)), with
P-H-7 riding along (DEC-889 item 8) and W1-29's SubagentStop case revised (DEC-899, P-IS-5 (a), I3 F4).

Written by the independent test designer (MR-3) before the implementation, from the ticket's KPI lines, the card
(`docs/plan/WAVE_2_WBS.md` §2, W2-65), DEC-880, DEC-889, DEC-899, the I3 finding 4 and the I1 note to W2-65's test
designer, and Claude Code's hook contract (code.claude.com/docs/en/hooks). No implementation file was read.

## What Claude Code does with a hook's answer (the contract the cases hold the lines to)

- **PreToolUse:** the call is blocked only on exit 2 (standard error goes to the model) or a deny decision on
  standard output with exit 0. Any other non-zero exit is a non-blocking error: the call goes through.
- **SubagentStop:** the helper's stop is blocked on exit 2, with standard error as the reason, or on exit 0 with
  `{"decision": "block", "reason": "…"}` on standard output. Standard output with exit 2 is not read.

## How the cases run (public interfaces only)

- The hook lines are read at run time from this worktree's `.rulesync/hooks.jsonc` and
  `template/.rulesync/hooks.jsonc`: every preToolUse line containing `hooks/pretooluse.py` and every line containing
  `hooks/posttooluse.py` (the containment program, on postToolUse and postToolUseFailure). Six lines today.
- Each line is run as Claude Code runs it: `sh -c '<line>'`, the event's JSON on standard input, in a temporary project
  under pytest's `tmp_path` with `CLAUDE_PROJECT_DIR` set to it, a temporary `HOME` and a temporary `PATH`.
- The temporary home holds `.local/bin/gov`, a script whose first line names the interpreter (the form of the owner's
  pin and of the documented rollback), and a `python3` first on `PATH` that goes on to the same interpreter. So the
  repository's line (which starts its program with the interpreter named by `gov`'s first line, W2-59) and the
  template's line (`python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>.py"`) both reach a working
  interpreter, or, in the "cannot start" case, both reach a missing one (`/nonexistent/w265/python3`).
- The program each line starts is a **stand-in** written where the line looks for it (the path after
  `$CLAUDE_PROJECT_DIR/` in the line): a syntax error, an exit 1, a crash, a deny decision, an exit 2. What is measured
  is the line's mapping of its program's exit, never the guard's judgement.
- Nothing touches the live hooks, `.claude/`, the real `HOME` or `$HOME/.local/bin/gov`. No network.

**The code under test (DEC-732).** The hook lines and the SubagentStop program are this worktree's own files, read
and run from `Path(__file__).parents[3]` (this worktree). The SubagentStop program runs with
`PYTHONPATH=<this worktree>/src`. The suite is run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-65/src` set on the
command:

```
PYTHONPATH=/home/usain/gov-os-worktrees/W2-65/src TMPDIR=/tmp/gov-os-lead-W2-65 python3 -m pytest \
  tests/acceptance/W2-65 tests/acceptance/W1-29/test_session_hooks.py -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed
```

Nothing is imported from another ticket's test folder: `w2_65_support.py` rewrites the way W2-59's
`w2_59_support.run_hook_line` runs a line.

## KPI lines and their tests

| KPI line | Test(s) | Expected red before the implementation |
|---|---|---|
| Success 1: the preToolUse and containment lines in `.rulesync/hooks.jsonc` end with exit 2, with a message naming the program, whenever the program ends with anything other than 0 or 2; 0, 2 and a deny decision pass through | `test_w2_65_hook_lines.py::test_a_program_that_cannot_run_blocks_the_call[repo-preToolUse[0]]`, `[repo-postToolUse[0]]`, `[repo-postToolUseFailure[0]]`; `::test_exit_0_and_exit_2_pass_through_unchanged[repo-…]` (three) | syntax error and exit 1: the line ends with exit 1; crash: exit -9 (killed); interpreter missing: exit 2 already (W2-59's no-pin refusal) but standard error does not name the program. The pass-through cases are green before and must stay green. |
| Success 2: the template's hook source does the same for its lines | the same two tests, `[template-preToolUse[0]]`, `[template-postToolUse[0]]`, `[template-postToolUseFailure[0]]` | syntax error and exit 1: exit 1; crash: exit 137; interpreter missing: exit 127. Pass-through green. |
| Success 3: one acceptance case per line: a program that cannot run blocks the call | `test_a_program_that_cannot_run_blocks_the_call`, one case per line (six). Each runs four ways a program cannot run: a syntax error (a half-finished edit), an exit 1 with nothing written, a crash (killed by a signal), an interpreter that cannot start. All failures of a line are reported together. | as above |
| Success 3 (the launcher, I1 §2.3): the guard's line stays recognisable | `test_both_sources_hold_the_guard_and_the_containment_lines_and_the_guard_stays_recognisable`: each source has a preToolUse line containing `hooks/pretooluse.py` and containment lines on postToolUse and postToolUseFailure | green before; must stay green |
| Success 4: the SubagentStop hook gives its block reason as Claude Code reads it, so a helper missing some of the twelve fields learns which | `test_w2_65_subagentstop_reason.py::test_a_helper_missing_fields_is_told_which_ones` (the template's copy, run as a process; a message with six of the twelve labelled fields; the delivered reason must name the six missing ones). Holds for either documented form. | the hook exits 2 with the reason only in standard output under `hookSpecificOutput.blockReason`, and standard error empty: "the stop is blocked but Claude Code delivers no reason" |
| Success 5: `src/gov/hooks/subagentstop.py` stays byte-identical to the template's copy | W1-29's `test_session_hooks.py::TestHookCopiesIdentical::test_hook_copies_identical[subagentstop.py]` (named here, not duplicated) | green before; must stay green |
| Success 5: W1-29's SubagentStop case revised to the documented form | `tests/acceptance/W1-29/test_session_hooks.py::TestSubagentStop::test_block_includes_reason_and_is_once` (revised, `Rewrite-Reason: DEC-889 item 8`) | same as success 4: exit 2 with empty standard error |
| Failure: a program that exits 1 or cannot start lets the call through; a line that turns exit 0 into a refusal | the "exit 1" and "cannot start" ways in `test_a_program_that_cannot_run_blocks_the_call`; `test_exit_0_and_exit_2_pass_through_unchanged` (exit 0 with nothing written stays exit 0 with empty standard output; exit 0 with a deny decision keeps its standard output byte for byte; exit 2 keeps 2 and its standard error) | as above |

The stand-ins that exit 1 or crash leave a marker first, and the case checks it, so a line that never started its
program cannot pass by accident. The pass-through stand-ins read the event's JSON from standard input and echo its
`tool_use_id`, so a line that does not hand its input on fails.

## The W1-29 revision (DEC-899, P-IS-5 (a), I3 F4)

`test_block_includes_reason_and_is_once` accepted the reason anywhere in the stdout JSON with exit 2, the form Claude
Code does not deliver. Revised, on that case's lines only:

- the block must be in a documented form: exit 2 (the reason is standard error), or exit 0 with
  `{"decision": "block", "reason": …}` (the reason is that field);
- the delivered reason must be non-empty and name **every** missing field (the input still lacks all twelve); the old
  case asked for at least one. No expectation is lowered: the block itself is still required, in either form.

**"Once" is not added.** The I3 row notes the case never tests it. Its reading here would be "a helper's second stop
with `stop_hook_active` true is not blocked again", which would let a helper end without the twelve fields and so
cut across CAP-37.d's enforcement; no source in this ticket decides it. Left as it was (untested), and reported to the
lead.

**A consequence for the implementer's choice.** The other W1-29 SubagentStop cases (`test_blocks_missing_fields`,
`test_malformed_input_fails_closed`, `test_text_labels_without_content_do_not_satisfy_contract`,
`test_empty_and_null_values_do_not_satisfy_contract`) require exit 2 for a block. They are not this ticket's to change,
so the form that keeps W1-29 green is exit 2 with the reason on standard error. W2-65's own case accepts both forms.

## Count

- `tests/acceptance/W2-65`: 14 tests (1 structure, 6 cannot-run, 6 pass-through, 1 SubagentStop); 7 red before the
  implementation (the six cannot-run cases and the SubagentStop case).
- `tests/acceptance/W1-29/test_session_hooks.py`: one case revised, red before the implementation; the others unchanged.
