Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-188 (DAEO-zlog): the adopt skill's step 6 and the practice record, product-spec (brief ps-3, from the ticket lead: a red to fix)

You are the product-spec worker for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C2, by the CIT-P route (a
kernel skill change: the owner approves its bytes after an independent review, before any merge; CAP-33, DEC-1166 (4)).
Use your skill `spec-writing` where it applies.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188 |
| branch | w2/W2-188 (from w2/integrate at 5336a6fca, the base) |
| the ticket (read whole; its **Interface** I1-I6 first: it is binding) | /home/usain/gov-os-worktrees/W2-188/.tickets/DAEO-zlog.md |
| the CIT-P draft to start from (a copy of the CTO's) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/draft-W2-188-CIT-P.md |
| the context packet (`gov context DAEO-zlog --role product-spec`, JSON: ticket and decisions' texts) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/ctx-ps.md |
| the reconciliation (G4, G6) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/MEMORY-AUDIT.md |
| the decision package | /home/usain/gov-os-worktrees/W2-188/governance/project/orchestration/packages/MEMORY-AUDIT-P1.md |
| the figures' sources | governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md, .../LIFT-1/E3-RESULT.md |
| the step matcher | tests/acceptance/W2-88a/w2_88a_support.py (`a9_regions`, `check_steps`, `check_pointer`, `heading_section`) |
| your scratch | the sandbox's own `$TMPDIR` (the sandbox's permission settings deny creating a folder under `.gov-runtime/scratch/`) |

Allowed paths, and the only ones you write: `template/governance/kernel/skills/adopt/SKILL.md`,
`.rulesync/skills/adopt/SKILL.md`, `template/.rulesync/skills/adopt/SKILL.md`, `docs/research/W2-88-memory-practice.md`,
`docs/changes/W2-188-CIT-P.md`, `docs/probes/DAEO-zlog/**`. Never `.claude/` (the copies ACT regenerates
`.claude/skills/adopt/SKILL.md` after the owner's yes) and never any test file (`tests/**`): F2.

Read the register by id only (`docs/DECISION_REGISTER.md`, 1.6 MB; grep `### DEC-1179` and the others in the ticket's
`sources:`). Search with the Read and Grep tools; if the first search does not answer, search once more in other words.

## The state
The work is written and committed (head `599fa2a22`, the acceptance tests merged into it). The skill's three copies are
final at sha256 `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`: **do not change the skill**. The
ticket's acceptance run shows the reds below. Fix the text (never a test: you do not read or write `tests/**`), then
re-run the record's checks of `docs/probes/DAEO-zlog/checks.md` that your changes touch and update that record.

## The failing output (the whole of what you are given)
```
FAILED tests/acceptance/W2-188/test_w2_188_practice.py::test_s3_section_5_item_6s_practice_lines_name_the_standing_set_and_that_it_never_chooses_or_judges_a_fix
E       AssertionError: section 5 item 6's practice lines (after its last `The practice:`) lack: ['never chooses or judges a fix']

FAILED tests/acceptance/W2-188/test_w2_188_citp.py::test_s5_the_record_holds_the_full_sha256_before_on_a_line_that_says_before
E       AssertionError: docs/changes/W2-188-CIT-P.md holds 16fd341f267b... but not on a line that says `before`

FAILED tests/acceptance/W2-188/test_w2_188_citp.py::test_s5_the_record_holds_the_sha256_after_as_the_kernel_skill_was_last_committed
E       AssertionError: docs/changes/W2-188-CIT-P.md holds 6a884cf1639f... but not on a line that says `after`
```
And one fact found by the lead for the CIT-P's impact table (§5, the W2-11 row): `tests/acceptance/W2-11/test_w2_11_skills.py`'s
`test_every_copy_carries_the_kernel_skills_body` is parametrized over `test-design`, `orchestration`, `audit` and
`qa-review` only, so no `[adopt]` case exists; `tests/acceptance/W2-11` and `tests/acceptance/W2-88a` run 276 passed,
1 skipped on `599fa2a22`. The row must say what is true: name `test_every_copy_carries_the_kernel_skills_body[adopt]`
and say it is not a case (the parametrization leaves `adopt` out), so W2-11 stays green after the merge and the `.claude`
copy's drift until the copies ACT is caught by no W2-11 case. Read the test to confirm it before you write it.

Two cases stay red and are not yours: `test_s5_the_last_verdict_is_pass_after_an_independent_review` (the lead adds the
reviewer's verdict after the review) and `test_s5_the_owner_approval_line_names_the_after_sha256` (the CTO writes it after
the owner's yes). Keep `owner_approval: 'pending'` and write no `verdict:` line.

## What to change
1. `docs/research/W2-88-memory-practice.md`, §5 item 6's practice sub-bullet on the standing set: say, in the literal
   words, that the standing set **never chooses or judges a fix** (it now says "never used to choose or judge a fix").
   Keep the rest of the line.
2. `docs/changes/W2-188-CIT-P.md` (the last file you change): §2.2 quotes the new §5 line as written; §3 gives the
   practice record's new after sha256; and the skill's before and after sha256 each stand **on a line that says
   `before` or `after`** (e.g. two lines under §3's heading: "The kernel skill's sha256 before: `16fd...`" and "The
   kernel skill's sha256 after: `6a88...`", full hashes; keep the table). Fix the W2-11 row as above. In §6 the
   review's round limit is DEC-1010 (two rounds at most), not DEC-1131.
3. Commit the practice record, the probe record and the CIT-P (CIT-P last), as below.

## Commits (your paths only; trailers in ONE final paragraph, no blank line inside it)
Commit in batches (the skill's three copies; the practice record; the probe record; the CIT-P last), each as:
```
git commit -m "<subject>" --trailer "Task: DAEO-zlog" --trailer "Role: product-spec" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1074, DEC-1072, DEC-1071, DEC-105, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>
```
`Implements:` lists only ids from the ticket's `sources:`. If anything changes the skill after the CIT-P is written,
recompute the after hash and commit the CIT-P again last.

## Rules
- Write files with the Write and Edit tools and absolute paths; anything longer than one line goes in a script in the sandbox's own `$TMPDIR` (find it with `echo $TMPDIR`; write
  it there with the Write tool at its absolute path), run with `python3 <file>` or `bash <file>`. `docs/probes/DAEO-zlog/`
  exists already; write into it with the Write tool.
- Use the sandbox's own `$TMPDIR`. You run no pytest; if you ever do, through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
  `PYTHONUSERBASE=/home/usain/.local -p no:cacheprovider -o tmp_path_retention_policy=failed`.
- Never open the evaluation sets' root (`~/gov-os-eval`), any hidden or memory-verdict folder, or secrets.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- No new ticket; a gap comes back in `unresolved` as a question with options, cost and a recommendation.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: each commit's hash and subject; the skill's sha256 after; the CIT-P record's sha256; the I5 results in one line each.
