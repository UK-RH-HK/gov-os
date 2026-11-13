# Brief: independent test designer, DAEO-emq1 (W2-115), FULL, class C3 — review round 1's two findings as described behaviours (run 4, td-4)

Budget: projection 4 USD. Keep your context short: read only what these two behaviours need; cut long outputs to head and tail.

You are a fresh independent test designer (MR-3) for ticket DAEO-emq1 (W2-115), in
`/home/usain/gov-os-worktrees/W2-115-tests` on `w2/W2-115-tests` (DEC-963), which holds the acceptance tests
(`tests/acceptance/W2-115/`) and the built smart close. Step 0 (the sandbox check), the standing rules, the writes
(`tests/acceptance/W2-115/**` only), the never-read rule for `src/gov/close/` and the return are those of the first
designer's brief, copied beside this one: `/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/brief/td-1.md`
(read its sections "Step 0", "Standing rules" and "Return"; its "What to write" is done). Do step 0 first and report
it first. The ticket (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md`): its KPI lines S4, S6, F1,
F3, its Interface section and the line "PK-3 (a)" near its end. No context packet: `gov context` refuses this ticket
(CONTEXT_OVER_CEILING); this brief and the ticket are your inputs. Read the existing suites
`tests/acceptance/W2-115/test_w2_115_reds.py`, `test_w2_115_batch.py`, `conftest.py` and `w2_115_support.py` to reuse
their planted projects and batches.

## Every pytest run goes through the heavy-job slot

With a TMPDIR outside the repository and outside `~/gov-os-runs` (your sandbox TMPDIR is fine),
`PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

If the slot script is refused by the sandbox, say so and run the same line without it, once. A session refused twice
for an action stops and says so; it never reaches the same effect by another command, form or file (DEC-1142 (9)).

## The two behaviours (the CTO's PK-3 (a); DEC-136: each is a behaviour, write it as one)

### B-1 (S4, F1): a red the change caused is never excused

The base a red is judged against ("the head without the change") is **the green base** (the newest green record the
selection counts the change from) **when that commit is an ancestor of HEAD**; otherwise it is **the parent of the
ticket's oldest own commit** (DEC-988 item 3, DEC-989). Today the close judges against the parent of the oldest
Task-trailered commit even when the green base is older, so work between the green base and the first trailered commit
is counted in the change but sits in the base reds are judged against.

Plant at least:
1. A green record at commit G where a test `t` passes; then a commit **without a `Task:` trailer** (an honest slip) that
   breaks `t`; then the ticket's trailered commits. The scoped close of the ticket refuses with `RED_CAUSED` (exit as
   the Interface names it), the close record marks `t` as the change's (caused), and **no** repair ticket is opened for
   `t` in `.tickets/`.
2. The same, but the slip commit is green and the break is in a trailered commit: still refused (a control, so the
   first case is not passing for another reason).
3. The green base is **not** an ancestor of HEAD (e.g. the green record names a commit on another branch that HEAD
   does not contain): the base is the parent of the ticket's oldest own commit. A red that parent already has with the
   same failure type is not the change's (the close does not refuse on it; it is named in the record with a repair
   ticket, as S5 says); a red that parent does not have is the change's (refused).
Plant the green record as the existing suites do; where the Interface is silent on how "the green base" is recorded,
choose the narrowest reading from the ticket and name it in `discoveries`.

### B-2 (S6, F3): a culprit whose red is its own new test is blamed once confirmed alone

In a batch, a candidate's red may be a test that candidate itself adds: built without that candidate the test does not
exist (absent), so no build "without one candidate" turns it green. Such a candidate is the culprit **once its red is
confirmed with that candidate alone** (the base plus that candidate only, the test red there too); it goes back and the
others land on the same run.

Plant at least:
1. A batch of three candidates: c1 adds a new test that fails; c2 and c3 are clean. Result: c1 goes back (named as the
   culprit), c2 and c3 land on the same run, and nothing lands before the culprit is found. Today this refuses the
   batch as unexplained; it must not.
2. c1 adds a new test that fails in the batch but **passes with c1 alone** (it fails only with another candidate's
   change): not confirmed alone, so no single candidate explains it and the batch refuses as today's unexplained case
   (nothing lands). If the Interface gives no code for this, assert the existing unexplained refusal; never invent a code.
Keep the existing S6 cases unchanged and green.

## Check and commit

1. Run the two files (and any new file) with the slot line above on this branch: the new B-1 case 1 and B-2 case 1
   should be **red** on today's code (that is the finding); the controls green. Quote the last line and each failure's
   one-line reason. A new case green on today's code that the finding says is wrong: fix it or say why.
2. Commit only your paths, a `Rewrite-Reason:` not needed (new cases); name the finding (F-1, F-3) in each new case's
   docstring:

       git commit -m "W2-115 acceptance: reds judged against the green base when an ancestor (F-1); a culprit's own new test blamed once confirmed alone (F-3) (td-4)" --trailer "Task: DAEO-emq1" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-988, DEC-989, DEC-979, DEC-1002, DEC-983" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-115

   Then quote `git log --oneline -2` and `git status --short`.

Return as td-1.md says; in `tests`, the new cases per behaviour and which are red on today's code.
