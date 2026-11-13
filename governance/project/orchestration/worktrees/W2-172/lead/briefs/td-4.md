# Brief td-4: independent test designer for DAEO-p8tv (W2-172), one revision batch on W2-171's F5, profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-p8tv (W2-172). The owner's DEC-1155 (1) (P1-N (a),
2026-11-12, ACCEPTED; read it by id in /home/usain/gov-os-worktrees/W2-172-tests/docs/DECISION_REGISTER.md) widens
this ticket by one file, `tests/acceptance/W2-171/test_w2_171_f5_paths.py`, for one test-designer revision: **F5 judges
only on branch w2/W2-171 and skips elsewhere naming why, as W2-180 did for W2-170.**

Why: W2-171's F5 judges whatever branch it runs on against W2-171's ticket (DAEO-k1e2). On w2/W2-172 (and in the merge
queue's clone of any other ticket) it fails, listing W2-172's own files as outside DAEO-k1e2's paths. Your lead's full
run at 42ec5de70751 shows it: `tests/acceptance/W2-171/test_w2_171_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows`
`AssertionError: ['docs/changes/W2-172-evidence.md', ...]`.

The model: `tests/acceptance/W2-170/test_w2_170_f5_paths.py` (commit e3ff31fc5, W2-180, DAEO-weh2): `OWN_BRANCH`, a
judge function over a root, the skip reasons (no `w2/integrate`, no ticket file, a detached HEAD, another branch), and
its planted cases. Follow it for W2-171 (`OWN_BRANCH = "w2/W2-171"`, ticket `.tickets/DAEO-k1e2.md`); keep the judgement
on w2/W2-171 exactly as it is now (allowed_paths plus the acceptance folder, `gov.close.select.match`). Add planted cases
in the same file as W2-180 did (its own branch clean: passes; its own branch with an outside path: fails; another branch:
skips naming the branch; detached: skips), so the skip is shown not to hide a red. Write only that one file; nothing
else in `tests/acceptance/W2-171/` changes (if the planted cases need a helper W2-170's file has, copy it into this file).

The file's docstring and every changed case carry the line
`Rewrite-Reason: DEC-1155 (1), the merge queue's 21:19 ejection (F5 judged any branch)`; the commit message names it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-172-tests |
| branch | w2/W2-172-tests (from 27f34f35c, which holds w2/integrate and the widened ticket) |
| your allowed path | tests/acceptance/W2-171/test_w2_171_f5_paths.py (that file only) |
| the tickets | .tickets/DAEO-p8tv.md (allowed_paths line 27 and the note near line 235), .tickets/DAEO-k1e2.md (W2-171's F5 line) |

Search with the Read, Grep and Glob tools; search again once in different words if the first does not answer
(DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the real `~/gov-os-eval`, `~/gov-os-runs`, a
hidden half or the crontab.

## Prove it (quote each summary line)
Every pytest through heavy_slot.sh. A heavy-slot or resource refusal is a wait: run again when it opens. `/tmp` is
read-only in your sandbox: use `$TMPDIR` (the launcher's) as the root, e.g. `$TMPDIR/td4/pt`; never inside a repository
and never under the real `~/gov-os-runs`.
`mkdir -p /home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/empty-home` once, then, with cwd
/home/usain/gov-os-worktrees/W2-172-tests:
`TMPDIR=<your pt dir> bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172-tests/src python3 -m pytest tests/acceptance/W2-171/test_w2_171_f5_paths.py tests/acceptance/W2-170/test_w2_170_f5_paths.py -v -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
1. On your branch (w2/W2-172-tests): the real-branch case skips naming the branch; the planted cases pass.
2. The whole W2-171 folder still passes as before: the same pytest line with `tests/acceptance/W2-171` (`-q`).

## Rules
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your one path only, one commit:
  `git commit -m "W2-171's F5 case judges only w2/W2-171, skips with its reason elsewhere (Rewrite-Reason: DEC-1155 (1), the merge queue's 21:19 ejection)" --trailer "Task: DAEO-p8tv" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073" -- tests/acceptance/W2-171/test_w2_171_f5_paths.py`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed (each changed or added case) / evidence (the pytest summary lines) / tests / discoveries
/ risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject,
trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
