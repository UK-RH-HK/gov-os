Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-188 (DAEO-zlog): revise one acceptance case to the re-baselined S5 clause (brief td-2, from the ticket lead)

You are a fresh independent test designer for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C2. Use your skill
`test-design`. The ticket's S5 clause (and its Interface I6) was re-baselined on 2026-11-14 by the CTO within purpose
(DEC-1157 (12), P-W2-188-S5 (a)), the old text kept beside the new. You revise **one case** to the new clause, as
described behaviour (DEC-136), and touch no other case.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188-tests |
| branch | w2/W2-188-tests (from w2/W2-188 at ccc5b3225) |
| the only paths you write | tests/acceptance/W2-188/test_w2_188_citp.py, tests/acceptance/W2-188/README.md |
| the ticket (read whole; S5, I6 and the last paragraph `P-W2-188-S5 (a)` are the clause) | /home/usain/gov-os-worktrees/W2-188-tests/.tickets/DAEO-zlog.md |
| the context packet (`gov context DAEO-zlog --role independent-test-designer`, JSON) | /home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/lead/briefs/ctx-td.md |

Never read /home/usain/gov-os-worktrees/W2-188 (the counterpart's tree), nor in your own tree the counterpart's work on
this ticket: `docs/changes/W2-188-CIT-P.md`, `docs/probes/DAEO-zlog/**` (DEC-820). Write the case from the clause, not
from the record. You may read `tests/acceptance/W2-188/**` (the suite's own support and the case's neighbours),
`tests/acceptance/W2-11/test_w2_11_skills.py` (line 124: the parametrization the clause cites), the register by id only
(`docs/DECISION_REGISTER.md`, 1.6 MB; `### DEC-1157`, `### DEC-136`), and `src/gov/adapters/portability.py` for the
finding's name.

## The case
`tests/acceptance/W2-188/test_w2_188_citp.py::test_s5_the_impact_table_names_w2_11s_body_case_red_and_w2_88as_cases_unchanged`
tests the old clause: a table row naming `test_every_copy_carries_the_kernel_skills_body[adopt]` with `red`. That case
does not exist (W2-11's body test is parametrized over test-design, orchestration, audit and qa-review only).

The new clause, as described behaviour: **the CIT-P record's impact table states**
1. that W2-11's body and version cases do not cover `adopt` (so they stay as they are after the merge);
2. that the hard-block check `adapter-portability` reports `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md`
   until the copies ACT regenerates that copy;
3. that W2-88a's cases are unchanged.

Revise the case to check these three statements in the record's table rows (the lines beginning `|`), reading them as
you judge a reasonable writer would state them (the support module's `flat()` is there for case and markup), and
rename the function to match what it now checks (keep the `test_s5_` prefix). Drop `W2_11_CASE` if nothing else uses
it. Change nothing else in the file. Update the README's map row for `success-5` and any count, with your reading of the
three statements in one line.

## Run
Run the folder once through the heavy slot, with the sandbox's own `$TMPDIR` (make the empty-home folder first):
`env HOME=/home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-188-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-188 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(a resource gate's refusal is a wait: wait and retry; if the sandbox refuses the heavy slot itself, run the same pytest
line without it and say so). Report the counts and each red's one-line reason. `test_s5_the_owner_approval_line_names_the_after_sha256`
is red by design (the owner's approval is pending). Do not open the record to explain a red: report it as the
assertion message gives it.

## Commit (your paths only; trailers in ONE final paragraph)
```
git commit -m "W2-188 (DAEO-zlog): the S5 impact case reads the re-baselined clause (W2-11's cases do not cover adopt; adapter-portability until the copies ACT; W2-88a unchanged)" --trailer "Task: DAEO-zlog" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1157, DEC-1179, DEC-105, CAP-33" --trailer "Rewrite-Reason: DEC-1157 (12), P-W2-188-S5 (a)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-188/test_w2_188_citp.py tests/acceptance/W2-188/README.md
```

## Rules
- Anything longer than one line goes in a script under the sandbox's own `$TMPDIR`; never a new folder under
  `.gov-runtime/scratch/`. Write files with the Write and Edit tools and absolute paths.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- Never open the evaluation sets' root or any hidden or memory-verdict folder; never secrets.
- No new ticket; a gap comes back in `unresolved` as a question with options.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: your commit's hash; the pytest counts (passed / failed) with each red's reason in one line; and a `TESTS-READY`
text (the lead writes the marker).
