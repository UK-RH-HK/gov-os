---
type: probe
task: DAEO-2bdu
round: narrow check after round 2 (DEC-1154's practice; the owner's P1-W2-88-RV2-1 (a))
reviewer_session: fa647d9d-1cf1-4be9-adfc-2a44e4261318
implementer_session: d26e2156-1ea7-4775-a5e2-c945729f2ca0 (eng-4, run 5's fix); test designer td-7 258e165e-ea7b-472c-a781-058a60a89bad
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 8f9571c7919d512cc4928b9bbafd4e19a67b6460
decisions_applied: [DEC-1154, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1120, DEC-801, DEC-808]
---

# Probe record: W2-88 (DAEO-2bdu), narrow independent check of the RV2-1/RV2-2 fix: FAIL

Round 2 (the last, DEC-1010) is `PR-DAEO-2bdu-round-2.md`; round 1 is `PR-DAEO-2bdu-round-1.md`. This record is the narrow check the owner's decision P1-W2-88-RV2-1 (a) called for: only the change since a15de913e8c4.

## The lead's judgement and triage

- **Who checked.** A fresh, read-only Independent Auditor (`fa647d9d-1cf1-4be9-adfc-2a44e4261318`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-13. Its brief carried `governance/project/briefs/JUDGEMENT.md` word for word and the run-5 interface (`.gov-runtime/scratch/lead/briefs/run5-interface.md`). Step 0 held. HEAD was 8f9571c7919d and `git status --porcelain` was empty at the start and at the end. Its tripwire shows no change in this ticket's trees.
- **What it checked.** The engineer's commit af046b331e27 (`fabric.py`, `refactor_plan.py`, `tests/unit/adopt/test_w2_88_rv2.py`) and td-7's cases 3923bf8469f7, merged at 8f9571c7919d (`test_w2_88_rv2_undo.py`, `standin_rv2/`, two cases in `test_w2_88_s2_plan.py`, the README's "Run 5 revisions"), against RV2-1's and RV2-2's stated behaviour.
- **Refusals the checker met, each once, not retried in the same form:** the Write tool for files in its TMPDIR (the auditor's tool list holds no Write), and a shell `while read` loop. It wrote its probe scripts in its TMPDIR with `printf` from Bash, the probe channel its brief names (DEC-1144 (7)).
- **The lead's verification at the head** (outside the sandbox): `gov accept W2-88`: outcome pass, every KPI line pass, 214 passed, 0 failed, 0 skipped (`.gov-runtime/scratch/lead/log/accept-5.txt`). td-7's cases were red on a15de913e8c4 for the reasons the README states (td-7's return); 8 of them fail on the unfixed code, and Case D and the RV2-2 one-line form are guards. The rebuild was ok (complete, `not_built` empty, four digests; `log/rebuild-5.txt`). LEAD_VERIFY_LINE
- **The verdict stands as FAIL** (never decided away). RV2-2 is fixed. RV2-1 is fixed for every case its stated behaviour and the interface name. NC-1 is a second route to the same loss. The triage:

| finding | severity | triage | the fix, as a described behaviour for the test designer (DEC-136) |
|---|---|---|---|
| NC-1: a refused A9 record commit still runs `git reset --hard`. A9 commits through `run.finish` → W2-23's `project.commit` (`stages.py:54`). On a failed commit, `project.commit` calls `project.restore` (`project.py:144-145` → `:114`) before A9's undo runs. Confirmed by the lead from the code. | blocker (in scope: RV2-1's own words, "when A9 refuses … after installing the kernel files"; ordinary work: yes, a pre-commit hook or signing that refuses the record commit; consequence: loses work) | to the owner via the CTO (the rounds are spent, DEC-1010; the owner decided (a) for RV2-1 with W2-23's `project.restore` unchanged, and NC-1's fixes either keep that or change it): package P-W2-88-NC-1 | when A9's own record commit is refused (a `pre-commit` hook exits 1), A9 runs no `git reset --hard`. It unstages only what it staged (its copies and its record), deletes only the files it wrote whose bytes are still its own, keeps a tracked file edited during the run and a file staged during the run, and refuses by name (the commit's refusal) with HEAD unmoved and no `reset` in the reflog |
| NC-2: a Ctrl-C between `install`'s `git add` and its listing leaves A9's copies staged (`fabric.py:209-215`) | minor (ordinary work: no, a window of milliseconds; consequence: other) | a row; it rides along with NC-1's fix if the owner chooses (a) (DEC-802) | an interrupt at any point after A9's `git add` leaves no copy of A9's in the index; an index entry whose blob is A9's own bytes counts as staged by A9 |
| note: `project.commit` takes whatever is staged, so a file someone staged during the run goes into A9's adoption commit | note (ordinary work: yes; consequence: other, nothing lost) | a row, with NC-1 | — |

The checker's report follows, unchanged.

