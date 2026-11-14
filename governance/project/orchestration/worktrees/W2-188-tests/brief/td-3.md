Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-188 (DAEO-zlog): revise the two F2 guard cases so the copies ACT's own commit is not a red (brief td-3, from the ticket lead)

You are a fresh independent test designer for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C3. Use your skill
`test-design`. You revise **two cases** as described behaviour (DEC-136) and touch no other case.

## Why (the CTO's answer P-C12-1 (a), DEC-1156 (7), within the ticket's purpose, listed for the owner's reading)
The owner approved the adopt skill's bytes (sha256 `6a884cf1...9489`, DEC-1181 (1)). The copies ACT
**ACT-CLAUDE-COPIES-12** will write the generated `.claude/skills/adopt/SKILL.md` from that approved kernel skill. That
copy's after-bytes have sha256 `65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc`, and the copy lands as
the owner's operator's commit, with the trailer `Role: owner` and a subject naming `ACT-CLAUDE-COPIES-12`. Ticket F2
("the ticket writes `.claude/skills/adopt/SKILL.md` or any test under `tests/acceptance/`") is about the ticket's own
writers, not the ACT; F2's verify line already says "the copies ACT regenerates the `.claude` copy after the owner's
approval". Two guard cases would go red on the ACT's commit although nothing wrong happened.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188-tests |
| branch | w2/W2-188-tests (from w2/W2-188 at 84ca16727) |
| the only paths you write | tests/acceptance/W2-188/test_w2_188_copies.py, tests/acceptance/W2-188/README.md (and, only if you need a shared helper or constant, tests/acceptance/W2-188/w2_188_support.py) |
| the ticket (read whole; F2 is the clause) | /home/usain/gov-os-worktrees/W2-188-tests/.tickets/DAEO-zlog.md |
| the context packet (`gov context DAEO-zlog --role independent-test-designer`, JSON) | /home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/lead/briefs/ctx-td.md |

Never read /home/usain/gov-os-worktrees/W2-188 (the counterpart's tree), nor in your own tree the counterpart's work on
this ticket: `docs/changes/W2-188-CIT-P.md`, `docs/probes/DAEO-zlog/**` (DEC-820). You may read
`tests/acceptance/W2-188/**`, the skill copies, and the register by id only (`docs/DECISION_REGISTER.md`, 1.6 MB;
`### DEC-1156`, `### DEC-136`, `### DEC-1181`).

## The two cases, as described behaviour

1. `test_w2_188_copies.py::test_f2_the_claude_copy_of_the_skill_equals_the_base` (line 109). Now: the `.claude` copy
   must equal `git show <BASE>:.claude/skills/adopt/SKILL.md`. **New behaviour:** it passes when the `.claude` copy's
   bytes equal the base's, **or** when their sha256 is exactly
   `65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc` (the ACT's after-bytes). Any other bytes stay red,
   with a message naming the copy's sha256 and both allowed values.

2. `test_w2_188_copies.py::test_f2_no_commit_of_the_ticket_outside_the_test_designer_touches_claude_or_tests` (line
   116). Now: a commit after the base with `Task: DAEO-zlog` whose `Role:` is not `independent-test-designer` names no
   `.claude/` and no `tests/` path. **New behaviour:** in addition, a commit whose trailers carry `Role: owner` **and**
   whose subject names `ACT-CLAUDE-COPIES-` is excused. Any other commit touching `.claude/` or `tests/` outside the
   test designer stays red: a `Role: owner` commit whose subject does not name `ACT-CLAUDE-COPIES-` stays red, and a
   commit by any other role whose subject names `ACT-CLAUDE-COPIES-` stays red. Do not widen the excuse further (for
   example to any `Role: owner` commit, to a subject match alone, or to paths outside `.claude/`).

Rename each function if its name no longer says what it checks (keep the `test_f2_` prefix), and update its docstring.
Change nothing else in the file. In the README, update the `failure-2` map row and the F2 note (around line 109) with
your reading in one line each, and any count.

## Show each revision both ways (record what you ran in your return)
In a throwaway clone of your branch under the sandbox's own `$TMPDIR` (never a new folder under `.gov-runtime/scratch/`;
`git clone --no-hardlinks /home/usain/gov-os-worktrees/W2-188-tests "$TMPDIR/plant"` or similar), run the two cases:
- on the branch as it is: both pass;
- with the `.claude` copy replaced by bytes whose sha256 is `65d6abd9...dbc` **and** a commit carrying `Task: DAEO-zlog`
  and `Role: owner` and a subject naming `ACT-CLAUDE-COPIES-12` that touches `.claude/skills/adopt/SKILL.md`: both
  pass. (To get those exact bytes: they are the approved kernel skill as the project's generator writes the `.claude`
  copy. Try `git show HEAD:template/governance/kernel/skills/adopt/SKILL.md` and the `.rulesync` copy, or the
  generator (`grep -rn "rulesync\|generate" src/gov/adapters/ | head`), and check the sha256. If you cannot produce
  those bytes, plant them by monkeypatching the constant's comparison in a scratch copy of the case, and say so.)
- with any other bytes in the `.claude` copy: case 1 red;
- with the same planted commit but `Role: product-spec` (or `orchestrator`), and separately with `Role: owner` but a
  subject not naming `ACT-CLAUDE-COPIES-`: case 2 red each time.

## Run
Run the folder once on your branch through the heavy slot, with the sandbox's own `$TMPDIR`:
`env HOME=/home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-188-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-188 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(a resource gate's refusal is a wait: wait and retry; if the sandbox refuses the heavy slot itself, run the same pytest
line without it and say so). Every pytest in the planted clone goes through the same heavy slot with the same flags.
No red is expected now (the owner's approval line is written). Report the counts and each red's one-line reason as the
assertion message gives it; do not open the counterpart's record to explain a red.

## Commit (your paths only; trailers in ONE final paragraph)
```
git commit -m "W2-188 (DAEO-zlog): the two F2 guard cases excuse only the copies ACT's own change (the .claude copy at the ACT's after-bytes; a Role: owner commit naming ACT-CLAUDE-COPIES-)" --trailer "Task: DAEO-zlog" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1157, DEC-1179, DEC-105, CAP-33" --trailer "Rewrite-Reason: P-C12-1 (a), DEC-1156 (7)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-188/test_w2_188_copies.py tests/acceptance/W2-188/README.md
```
(add `tests/acceptance/W2-188/w2_188_support.py` to the paths only if you changed it.)

## Rules
- Anything longer than one line goes in a script under the sandbox's own `$TMPDIR`. Write files with the Write and
  Edit tools and absolute paths.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- Never open the evaluation sets' root or any hidden or memory-verdict folder; never secrets.
- No new ticket; a gap comes back in `unresolved` as a question with options.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: your commit's hash; the pytest counts (passed / failed) with each red's reason in one line; the planted runs
(each, with its result); and a `TESTS-READY` text (the lead writes the marker).
