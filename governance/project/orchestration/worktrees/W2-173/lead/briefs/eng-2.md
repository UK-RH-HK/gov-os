# Brief eng-2: engineer for DAEO-qz4p (W2-173), profile FULL, class C3 (run 2c)

You make one small, fully specified test change for ticket DAEO-qz4p (W2-173). The launch script
(governance/project/orchestration/tools/indep_launch.py) now checks the checker's `notes.md` (KPI S3) and the auditor's
`classes.json` (KPI S4) at delivery, so two of W2-149's unit cases that plant the old form are red. The CTO put their
file in this ticket's paths (DEC-866, DEC-105 apply now). Change those two cases exactly as below; nothing else.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-173 |
| branch | w2/W2-173 |
| the ONE file you edit | tests/unit/orchestration/test_w2_149_indep_launch.py (only the two functions named below) |
| ticket (read-only) | /home/usain/gov-os-worktrees/W2-173/.tickets/DAEO-qz4p.md (its last paragraph is the CTO's P-1 (a)) |
| the required change, as stated | docs/changes/W2-173-evidence.md, section "Run 2", the last paragraph and its two bullets (lines ~123-131) |
| the fixed forms (read-only) | governance/project/indep-briefs/memory-audit/checker.md §6, auditor.md §2 and §6 (never write under indep-briefs/ or indep-walls/) |
| a worked example of the same fixed form | tests/acceptance/W2-149/w2_149_support.py: `CHECKER_NOTES`, `AUDITOR_CLASSES` (read-only) |
| the script's checks (read-only) | indep_launch.py, the notes and classes checks |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## The change (exactly)
1. `test_checker_delivers_its_notes` (line ~993): plant `out/notes.md` in checker.md §6's form for the unit set that
   `w.plant_set()` stages (q01 and `sub/q02`, ids q01 and q02, in id order): `# Cross-check notes`, `## Questions` with
   `q01 | accept | - | also: none | <one sentence>` and `q02 | revise | R6-SPAN-MISSES | also: none | <one sentence>`,
   `## The set` and its five lines (as §6 states them). Keep the result `{"checked": 2, "accepted": 1, "revise": 1,
   "rejected": 0}`. Put the notes text in one local name; the two asserts that read `"notes\n"` read that text and
   `sha(<its bytes>)` instead. Every other assert stays as it is.
2. `test_auditor_delivers_its_classes_and_the_audit_is_logged` (line ~1006): `misses.jsonl` gets two lines with string
   ids, `{"id": "m1", ...}` and `{"id": "m2", ...}` (in auditor.md §2's line form as far as the script reads it);
   `classes.json` becomes `{"m1": {"class": "retrieval_miss", "reason": "<one line>"}, "m2": {"class":
   "retrieval_miss", "reason": "<one line>"}}`. The result `{"misses": {"retrieval_miss": 2}}` stays, and so does the
   counts assert; the `miss-classes.json` assert reads the new classes text. Every other assert stays.
3. No other change: no other test, no helper, no fixture, not the script, not the evidence. No assertion is removed or
   weakened. Add a one-line comment on each changed planted product naming the reason (`# W2-173 S3: §6's fixed form`
   and `# W2-173 S4: classes keyed by the misses' ids`).

## Check before you return
Run, and quote the summary lines:
`env HOME=/home/usain/gov-os-worktrees/W2-173/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-173/src python3 -m pytest tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_173_indep_launch.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(the whole W2-149 unit file must pass; the two cases named must pass). Also quote `git diff --stat HEAD~1 HEAD` after
your commit: one file.

## Commit (your path only)
`git commit -m "W2-173 (DAEO-qz4p): W2-149's two unit cases plant the checker's notes and the auditor's classes in the fixed form (S3, S4)" --trailer "Task: DAEO-qz4p" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-866, DEC-105" --trailer "Rewrite-Reason: DEC-866, W2-173's S3 and S4" -- tests/unit/orchestration/test_w2_149_indep_launch.py`

Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-173/.gov-runtime/scratch/; literal
paths as write targets. Never touch .gov-runtime/scratch/lead/. Never a real walled session; never ~/gov-os-eval,
~/gov-os-runs, ~/.claude or a hidden folder.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (pytest summary lines) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
