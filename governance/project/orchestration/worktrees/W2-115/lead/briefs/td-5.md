# Brief: independent test designer, DAEO-emq1 (W2-115), FULL, class C3 — the owner's P1-K (a) and review round 2's R2-4, R2-5 (run 5, td-5)

Budget: projection 4 USD. Keep your context short: read only what these behaviours need; cut long outputs to head and tail.

You are a fresh independent test designer (MR-3) for ticket DAEO-emq1 (W2-115), in
`/home/usain/gov-os-worktrees/W2-115-tests` on `w2/W2-115-tests` (DEC-963), which holds the acceptance tests
(`tests/acceptance/W2-115/`) and the built smart close. Step 0 (the sandbox check), the standing rules, the never-read
rule for `src/gov/close/` and the return are those of the first designer's brief, copied beside this one:
`/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/brief/td-1.md` (read its sections "Step 0", "Standing
rules" and "Return"; its "What to write" is done). Do step 0 first and report it first. Your writes:
`tests/acceptance/W2-115/**`, and for R2-5 only, the one line named below in `docs/research/W2-115-smart-close.md`.
The ticket (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md`): its KPI lines S4, S5, S6, S9, F1, F3,
its Interface section and its last section "P1-K decided". No context packet: `gov context` refuses this ticket
(CONTEXT_OVER_CEILING); this brief and the ticket are your inputs. Read the existing suites
`tests/acceptance/W2-115/test_w2_115_reds.py`, `test_w2_115_batch.py`, `conftest.py` and `w2_115_support.py` to reuse
their planted projects and batches.

## Every pytest run goes through the heavy-job slot

With a TMPDIR outside the repository and outside `~/gov-os-runs` (your sandbox TMPDIR is fine),
`PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

A heavy-slot, memory, CPU or disk gate refusal is a wait, not a refusal: run it again when it opens (DEC-1146). If the
slot script itself is refused by the sandbox, say so and run the same line without it, once. A session refused twice
for an action stops and says so; it never reaches the same effect by another command, form or file (DEC-1142 (9)).
Never write a hand-made `sleep`/`until` wait loop.

## The behaviours (DEC-136: each is a behaviour, write it as one)

### B-5 (S4, F1; the owner's P1-K (a), DEC-1150 (2)): with no green base on HEAD's line, every red is the change's

The head a red is judged against is **the green base** (the newest green record the selection counts the change from)
**only when that commit is an ancestor of HEAD**. When there is none (no green record at all, or the green record names
a commit HEAD does not contain) there is **no** head without the change: every red of the scoped close counts as the
change's, and the close refuses (`RED_CAUSED`; fails closed). The earlier fallback (the parent of the ticket's oldest
own commit) is dropped.

1. **Revise** `test_with_the_green_base_not_an_ancestor_a_red_the_parent_has_is_not_the_change_s` to the new rule
   (rename it to say what it now asserts): the same planted history (green record on another branch; W2-bb's known red
   red on the parent of the oldest own commit with the same failure type) now **refuses** with `RED_CAUSED`, the record
   or refusal marks the red caused, **no** repair ticket is opened, and the ticket does not close. Keep it honest about
   what is not run: assert nothing about a run on the parent unless you need it. The revision carries the trailer
   `Rewrite-Reason: DEC-1150 (2), the owner's P1-K (a): with no green base every red is the change's` and its
   docstring names R2-1 and DEC-1150 (2).
2. Keep `..._a_red_the_parent_does_not_have_is_the_change_s` (still refused under the new rule); update only its
   docstring if it names the dropped fallback.
3. **Add** R2-1's planted case (the reviewer's P1): **no green record at all**; an untrailered first commit (an honest
   slip) breaks W2-bb's widget test; then the ticket's trailered work. The scoped close refuses `RED_CAUSED`, the red is
   caused, no repair ticket, the ticket does not close. Today's code closes it (exit 0, caused false, a repair ticket):
   this case must be red on today's code.
4. Run the whole folder `tests/acceptance/W2-115/` and find **every other case** whose verdict depends on the dropped
   fallback (a red judged against the parent of the oldest own commit with no green base on HEAD's line, e.g. the
   `unowned` fixture's S5 cases, the nightly-read-first case). Name them in `discoveries` with their red on today's
   code expected or not. Where a case is about something else (S5's repair ticket, the nightly read first, S4's rounds)
   and would now go red only because its planted project has no green base on HEAD's line, revise its planting so the
   project has one (a green record naming an ancestor of HEAD), each with `Rewrite-Reason: DEC-1150 (2): the planted
   project needs a green base on HEAD's line under the owner's P1-K (a)`. Do not weaken any assertion.

You cannot see the code; reason from these lines. After the engineer's change, cases 1 and 3 turn green.

### B-6 (S6, F3; review round 2's R2-4, part 1): a culprit's own new test that times out alone is not confirmed

A batch of three candidates: c1 adds a new test that fails in the batch; with c1 alone on the base that test **times
out** (runs past the per-test limit; plant it as the existing timeout cases do) instead of failing. A timeout never
confirms (S4: an unknown failure never matches), so no single candidate explains the red: the batch refuses with
`BATCH_UNEXPLAINED`, **nothing lands** (c2 and c3 do not land; no landing ref or branch moves). The reviewer planted it
as B3; today's code is right, so this case should be **green** on today's code (it guards against a mutant that counts
a timeout as confirmation).

### B-7 (S6, F3; review round 2's R2-4, part 2): the rest never lands on a run of zero tests

A batch whose selection's only target is the culprit c1's own new (failing) test file, c1 confirmed alone as the
culprit; the rest (the other candidates) then holds none of the selection's targets. The rest must not land after a run
of 0 tests: the batch refuses with `RUN_INCOMPLETE`, **nothing lands**. The reviewer planted it as B1; today's code is
right, so this case should be **green** on today's code (it guards against a mutant that lets an empty target list run).
Plant the other candidates so they select nothing by themselves (for example a change only to a file the test map gives
no suite and that S2 lets pass, or a records-only change) — choose the narrowest planting the existing support allows,
and name it in `discoveries`. If no planting reaches this without reading `src/gov/close/`, say so in `unresolved`
instead of guessing.

### R2-5 (S9): the research script's run line

`docs/research/W2-115-smart-close.md` line 34 (inside the inline script's docstring) reads
`Run: PYTHONPATH=<worktree>/src python3 -I s9.py <close-build log folder>`. `-I` ignores `PYTHONPATH`, so `gov` cannot
be imported. Change only that line: drop `-I` (match the document's re-run paragraph, which runs without it). Nothing
else in the document. If the guard refuses the write, say so in `guard_refusals`; do not try another form (the lead
gives it to the engineer).

## Check and commit

1. Run `tests/acceptance/W2-115/` with the slot line above on this branch. Expected on today's code: B-5 cases 1 and 3
   **red** (quote each one-line reason), every B-6/B-7 case **green**, every other case as before (name any other red
   and why). Quote the last line.
2. Commit in two commits, only your paths:

       git commit -m "W2-115 acceptance: with no green base on HEAD's line every red is the change's (P1-K (a), R2-1)" --trailer "Task: DAEO-emq1" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-988, DEC-989, DEC-1083, DEC-983" --trailer "Rewrite-Reason: DEC-1150 (2), the owner's P1-K (a): with no green base every red is the change's" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-115

   (if B-6/B-7 are in a separate file, or you prefer, a second commit for them with the subject "W2-115 acceptance: a
   culprit timing out alone is not confirmed; the rest never lands on zero tests (R2-4)" and `Implements: DEC-979,
   DEC-1002, DEC-983`, no Rewrite-Reason), and for R2-5:

       git commit -m "W2-115 (DAEO-emq1): the S9 script's run line without -I (R2-5)" --trailer "Task: DAEO-emq1" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-983" --trailer "Rewrite-Reason: R2-5: -I ignores PYTHONPATH, so gov cannot be imported" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/W2-115-smart-close.md

   Then quote `git log --oneline -4` and `git status --short`.

Return as td-1.md says; in `tests`, each new or revised case per behaviour and which are red on today's code; in
`discoveries`, every other case you revised and why.
