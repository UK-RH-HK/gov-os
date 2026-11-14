# Brief: independent test designer, W2-130 (DAEO-q8cl), run 3 batch 3: five red cases whose reading the lead finds at odds with the history the Verify lines name

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-q8cl (W2-130), profile
STANDARD, class C2. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-130-tests |
| branch | w2/W2-130-tests (from ba9f5ed4d, the merge of the S4 revision) |
| your context packet (gov context output, JSON) | /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (its eleven KPI lines; the Verify clauses are the spec) | /home/usain/gov-os-worktrees/W2-130-tests/.tickets/DAEO-q8cl.md |
| the cases | /home/usain/gov-os-worktrees/W2-130-tests/tests/acceptance/W2-130/ (README first; `test_w2_130_marks.py`) |
| the five reds as the lead ran them (pytest output) | /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/brief/reds.txt |
| scratch | your sandbox's own `$TMPDIR` only |

Your allowed paths: `tests/acceptance/W2-130/**` only.

The implementer (the lead) works on the same ticket in `/home/usain/gov-os-worktrees/W2-130`: never read that tree,
its branch's commits after ba9f5ed4d, or `docs/research/W2-130-link-cleanup.md` (the counterpart's work, DEC-820).
History up to ba9f5ed4d is open to you. You may reproduce a red by building a plausible record in a scratch clone, as
the run-2 test designer did.

## What the lead found
At the implementer's head the folder gives 76 passed and 5 failed. The five reds are in `test_w2_130_marks.py`
(output in reds.txt). For each the lead describes what the history holds. Judge each against the ticket's Verify
line: where the case reads more than the line states, revise the case to the line; where the case is right and the
history is wrong, keep it red and say so in your return (the lead then takes it to the CTO as a package). You decide;
the lead's reading is not the spec.

1. `test_s1_the_marks_e12f8a30c_adds_equal_patches_a0_a1_a2_after_the_audits_drops_and_rewrites`
   fails with "a patch block holds no hunk of docs/DECISION_REGISTER.md". e12f8a30c's own message names "batches a1,
   a2, a0 and b1 ... the archive's collective line 34 one decision per line": patch a0 is the
   ARCHIVE-SUPERSEDED.md change (one decision per line), with no register hunk; a1 and a2 hold all of e12f8a30c's
   register marks (`git show e12f8a30c --stat`: the register and the archive). The S1 Verify: "the marks e12f8a30c
   adds equal the gov links --propose-marks output it applied (patches a0, a1 and a2, kept beside the record) after
   the auditor's drops and rewrites".
2. `test_s1_a_mark_on_one_of_the_87_added_after_e12f8a30c_is_in_a_marks_commit_and_append_only` fails on
   518772b5c (DEC-989). That commit is the CTO's on `w2/integrate` (Task: DAEO-sdxk, 2026-11-12), recording the
   owner's DEC-1141; it extends DEC-989's existing `**Changed by:** DEC-1045` to `**Changed by:** DEC-1045; DEC-1141
   (4) (...)` (DEC-866's marking of a new decision's change, not a W2-130 clean-up mark; its changer DEC-1141 is no
   changer the census states for DEC-989). The S1 Verify: "a mark on one of the 87 added after e12f8a30c is in
   c4420040f or a follow-up marks commit named in the record, under the same append-only check".
3, 4. `test_s2_the_two_follow_up_marks_are_in_a_marks_commit_after_a_right_verdict[...]` want the follow-up commit
   to append exactly ` · **Changed by:** DEC-1122 (4)` and ` · **Changed by:** DEC-086`. Those exact texts came from
   the lead's interface of run 2, which named `gov links --propose-marks`' proposals. The independent auditor of the
   two marks (2026-11-13, at 09542040f) judged both right and corrected their parts (its F1: "(4)" is DEC-1115's
   item, not DEC-1122's; its F2: DEC-086 settles DEC-026 "for Wave 1"), and bce798c3a appends
   ` · **Changed by:** DEC-1122 (2) (item (4): its 80 % trigger brought forward to now, until the weekly reset)` and
   ` · **Changed by:** DEC-086 (for Wave 1)`. The S2 Verify: "DEC-1115<-DEC-1122 (4) and DEC-026<-DEC-086 are marked
   on their own status lines at HEAD, each by a follow-up marks commit named in the record that comes after an
   independent auditor's check judging the mark right (S3)". The interface's `audits` items carry `mark` (the text
   gov links proposed) and `committed_mark` (the text committed).
5. `test_s2_each_census_id_names_every_stated_changer_unless_the_auditor_judged_the_pair_wrong` finds 38 census
   pairs "not on their status line". None is among the 87. Each status line names the changer's id in a form the
   register used before the clean-up, outside a `**Changed by:**` field or a `SUPERSEDED by` list: for example
   DEC-150 `**Amended by:** DEC-156`, DEC-466 `**Lifted by:** DEC-953 (item 1)`, DEC-936 "item 2's priority line
   replaced by DEC-946". `gov links` counts a pair as marked when the changer's id is on the status line
   (`src/gov/links/check.py`, the UNMARKED_CHANGE check), and reports none of the 38. The S1 Verify fixes the form for
   the 87's marks ("as **Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n"); the S2 Verify says "each of the
   census's 215 drifting ids ... has every stated changer named on its own status line at HEAD".

## The work
1. For each of the five, decide: revise the case to the Verify line, or keep it. If you revise, change only what
   the line does not state; keep every check the line does state (for 2: the clean-up's marks on the 87 stay under
   the append-only check; for 3 and 4: one follow-up marks commit, after a right verdict, at an ancestor head, dated
   before; for 5: every census pair still named on its own status line).
2. Prove each revised case still catches a planted break, in a scratch clone under `$TMPDIR` (never committed):
   for 1, a record whose a1 patch lacks one of e12f8a30c's marks; for 2, a scratch commit after e12f8a30c that edits
   one of the 87's status lines in its middle; for 3/4, a follow-up commit whose appended mark names another changer;
   for 5, a status line with the changer's id removed.
3. Run the folder at your head (ba9f5ed4d) and quote the count line; a result that changed for a case you did not
   touch is a finding. Lower nothing else; no skip, xfail, flaky or rerun mark.
4. Commit with `Rewrite-Reason: <the finding numbers you revised>, lead's run-3 findings` among the trailers, then
   return.

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder>[::<test>] -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"`. A resource gate's
refusal is a wait (relaunch when it opens). Quote the count lines in your return.

## Searching
Read and Grep only; no `gov retrieve` or `gov context` in the sandbox. Search once, then once more in other words.
Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder. The guard refuses the
register to your role: read entries through `git show <commit>` diffs of the commits named above, or not at all.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line of shell goes in a script
under your `$TMPDIR`, run with `bash <file>`. Refused twice for the same call by the guard, the sandbox or a hook: stop and
say so; never work around a refusal. No merge, no push.

## Commit (your paths only)
```
git -C /home/usain/gov-os-worktrees/W2-130-tests commit -m "<subject>" --trailer "Task: DAEO-q8cl" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1073, DEC-866, DEC-825, DEC-1010" --trailer "Rewrite-Reason: <...>" -- tests/acceptance/W2-130
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; for each of the five: revised or kept, and why, in one or
two lines; guard_refusals: none or a line each.
