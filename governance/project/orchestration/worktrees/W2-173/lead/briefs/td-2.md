# Brief td-2: independent test designer for DAEO-qz4p (W2-173), profile FULL, class C3 (run 2)

You are the independent test designer (MR-3) for ticket DAEO-qz4p (W2-173): the launch script's follow-ups for the
memory audit. Run 1's acceptance tests (tests/acceptance/W2-173/, merged) stand. This batch is the CTO's decision P-1 (a)
(DEC-1112 (3), DEC-105 apply now, DEC-866), recorded at the end of the ticket: this ticket's stricter delivery and result
checks (S3 notes form, S4 classes form, S1 `effort` in counts.json) break W2-149's acceptance cases whose fixtures plant the
old form. You bring W2-149's planted products into the fixed form, and nothing else. You never read the engineer's unit
tests `tests/unit/orchestration/test_w2_173*`.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-173-tests |
| branch | w2/W2-173-tests |
| your allowed paths | tests/acceptance/W2-149/w2_149_support.py (only this file; Rewrite-Reason: DEC-866, W2-173's S3 and S4), and tests/acceptance/W2-173/** if one of run 1's cases must follow (say why) |
| ticket (read it first, especially its last paragraph "Delegated ... P-1 (a)") | /home/usain/gov-os-worktrees/W2-173-tests/.tickets/DAEO-qz4p.md |
| the script (its delivery checks: read them to learn the fixed form; do not test internals) | governance/project/orchestration/tools/indep_launch.py |
| the fixed forms (read-only; never write under indep-briefs/ or indep-walls/) | governance/project/indep-briefs/memory-audit/checker.md §6, §7; auditor.md §6, §7 |
| how run 1's tests plant the good forms (reuse that reading) | tests/acceptance/W2-173/test_w2_173_notes.py (or the notes file there), test_w2_173_classes.py, test_w2_173_effort.py |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-1101, DEC-1120, DEC-1112, DEC-1113, DEC-866, DEC-105 |

Search with Read, Grep and Glob; if the first search does not answer, search once more in different words, then answer
from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## What to change in tests/acceptance/W2-149/w2_149_support.py
1. `COUNTS_KEYS` gains `"effort"` (S1: every counts.json carries `effort`, a string or null).
2. `GOOD_DELIVERY["checker"]["notes.md"]`: the fixed form of S3, matching the set W2-149's planting stages in the
   checker's `input/set/`: `# Cross-check notes`, `## Questions`, one line per file of that set in id order
   (`<id> | accept|revise|reject | <codes or -> | also: <...> | <sentence>`), `## The set`, its five lines. Its verdict
   counts must equal `GOOD_RESULT["checker"]` (`checked`, `accepted`, `revise`, `rejected`); change `GOOD_RESULT["checker"]`
   only if the staged set forces it (say so).
3. `GOOD_DELIVERY["auditor"]["classes.json"]`: the fixed form of S4: `{"<id>": {"class": ..., "reason": ...}}`, one key
   per line of W2-149's planted `input/misses.jsonl` and no other, each class one of the five, each reason one line of at
   most 200 characters; `GOOD_RESULT["auditor"]["misses"]` equal to the classes' counts (the five classes, as the result
   schema requires).
4. Any other W2-149 helper that plants a checker's notes, an auditor's classes, or checks counts keys, if a case still
   fails for the old form only. Do not weaken any assertion; do not change what a case checks, only the planted product.

Run 1's red list on W2-149 (head b6d2f6f90, before the engineer's code was merged it was green): acceptance 168 passed,
6 failed, 35 skipped. Expected after your change, with the engineer's code on this branch: W2-149's cases all pass
(W2-149's own count at its merge was 206/0/3 with the real environment; with the empty HOME form below, compare
against the same form at base `2f98aecbc` if a count differs and say so).

W2-149's two unit cases (`tests/unit/orchestration/test_w2_149_indep_launch.py::test_checker_delivers_its_notes` and
`::test_auditor_delivers_its_classes_and_the_audit_is_logged`) are outside your paths and the ticket's: do not edit them.
Read them and write in `discoveries` the exact change each needs (the planted notes / classes and counts), for the CTO.

## Rules
- Planted folders only (pytest's tmp_path); never the real ~/gov-os-eval, ~/gov-os-runs, ~/.claude, a hidden folder, or a
  real walled session.
- Run both folders, whole-folder form:
  `env HOME=/home/usain/gov-os-worktrees/W2-173-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-173-tests/src python3 -m pytest tests/acceptance/W2-149 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for tests/acceptance/W2-173. Both must be green (W2-173's F4 check must accept the support file now
  that the ticket's allowed_paths names it). Report the summary lines and any case still red with its reason.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-173-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only (the Rewrite-Reason trailer is required for the W2-149 file):
  `git commit -m "<subject>" --trailer "Task: DAEO-qz4p" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1120, DEC-1112, DEC-1113" --trailer "Rewrite-Reason: DEC-866, W2-173's S3 and S4 (the CTO's P-1 (a), 2026-11-12)" -- tests/acceptance/W2-149/w2_149_support.py`
  (add tests/acceptance/W2-173 to the path list only if you changed it).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines for both folders) / tests / discoveries (include the
two unit cases' needed change) / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then
`commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
