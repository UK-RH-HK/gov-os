---
type: probe
task: DAEO-2bdu
round: 2
reviewer_session: c56e1745-57dd-42fb-bece-ed52b319a502
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 15ad055adbb5d12abe4ecdf83344c7f504315d01
decisions_applied: [DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1112, DEC-1144, DEC-1157, DEC-1150]
---

# Probe record: W2-88 (DAEO-2bdu), review round 2 of 2, the last (DEC-1010): FAIL

## The lead's judgement and triage

- **Who probed.** A fresh, read-only Independent Auditor session (`c56e1745-57dd-42fb-bece-ed52b319a502`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-13. Step 0 held (the write outside the tree failed with a read-only file system; the index refresh worked). The head was 15ad055adbb5 and `git status --porcelain` was empty at start and end. Its tripwire shows no change in this ticket's trees.
- **Refusals the reviewer met, once, not retried:** one Write of a probe script into its own TMPDIR (the auditor's tool list holds no Write; expected).
- **The lead's verification at the head** (outside the sandbox): `gov accept W2-88`: outcome pass, every KPI line pass, 204 passed, 0 failed, 0 skipped (`.gov-runtime/scratch/lead/log/accept-4.txt`). lead_verify (scoped, DEC-968): @VERIFY@
- **The verdict stands as FAIL** (never decided away; this was the last round, there is no third, DEC-1010). All three round-1 blockers (RV1-1, RV1-2, RV1-3), the five minors (RV1-4 to RV1-8) and the package items (RV1-9 to RV1-11) are fixed and probed; L-1 is built and probed. The triage of the new findings:

| finding | severity | triage | the fix, as a described behaviour for the test designer (DEC-136) |
|---|---|---|---|
| RV2-1 a refused or interrupted A9 throws away work done in the repository while it ran (`fabric.undo` → `project.restore` = `git reset --hard <head>`, `fabric.py:218-226`, `project.py:110-125`; reached on any exception after the copy step, `fabric.py:564-569`) | blocker | to the owner with options (the last round: no third review; an owner-decided fix gets a narrow independent check). Lead's recommendation: (a) fix, within the ticket's paths (`fabric.py` only; `project.restore`, W2-23's, unchanged) | when A9 refuses or is interrupted after installing the kernel files, it unstages only the paths it staged and deletes only the files it wrote whose bytes are still the ones it wrote (and the empty folders it made); a tracked file edited during the run keeps its edit; a file staged during the run stays staged; if HEAD moved during the run, A9 refuses without resetting, names the new commit and leaves the branch where it is |
| RV2-2 `PLAN.md`'s first unscanned path sits on the heading's line (`refactor_plan.py:172-178`) | minor | fix with RV2-1 (one line) | the unscanned paths form a list starting on the line after `Unscanned paths:`, each `- \`path\`` at the start of a line |

The reviewer's review follows, unchanged.

