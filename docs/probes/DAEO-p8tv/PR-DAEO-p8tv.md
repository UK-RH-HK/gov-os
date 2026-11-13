---
type: probe
task: DAEO-p8tv
reviewer_session: 26522cdc-412b-4c3b-a104-dc236287cfcb
implementer_session: n/a (two test-designer revisions, ce3269f3b and c6f7b9d6e)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 25634cdde4600fddbb80f72e5604e785b711e9e6
decisions_applied: [DEC-1154, DEC-1155, DEC-1156, DEC-1010]
---

# Probe record: W2-172 (DAEO-p8tv), the narrow check of the two test revisions after the 21:19 ejection

- **What was probed.** Head `25634cdde460` of `w2/W2-172`: only W2-172's changes since its review round 1 record (`0c16d8afb`, reviewed head `f706a77f5b7e`, now `PR-DAEO-p8tv-round-1.md`): the test designer's `ce3269f3b` (path hygiene judges the world's paths, not the repository's own location) and `c6f7b9d6e` (W2-171's F5 judged only on `w2/W2-171`, DEC-1155 (1)). A narrow check (DEC-1154), not a design review.
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, Opus high, class C2, session `26522cdc-412b-4c3b-a104-dc236287cfcb`, 2026-11-12, started through `gov launch` under its OS sandbox; commissioned and judged by the CTO (orchestrator). Brief: `.gov-runtime/scratch/orchestrator/briefs/W2-172-fix-check.md`.

# W2-172 (DAEO-p8tv): narrow check of the two test revisions after the 21:19 ejection

task: DAEO-p8tv
decisions: [DEC-1154, DEC-1155, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1012, DEC-820]
head: 25634cdde460 (worktree /home/usain/gov-os-worktrees/W2-172, branch w2/W2-172); review round 1 record 0c16d8afb, reviewed head f706a77f5b7e
KPI: w2-172-fix-check, verdict **pass**

## What was probed and found sound
- **Scope of the change.** Since `0c16d8afb`, W2-172's own changes are only `ce3269f3b` (5 files under tests/acceptance/W2-172/) and `c6f7b9d6e` (tests/acceptance/W2-171/test_w2_171_f5_paths.py).
  - Both are `Role: independent-test-designer`, `Task: DAEO-p8tv`, each with a Rewrite-Reason.
  - The integrate merge `27f34f35c` touches neither ticket folder nor `src/gov/memaudit`, which is identical to the reviewed code.
- **Path hygiene (ce3269f3b).** Precondition: the world's 8 paths are still checked. The repository's own location and the interpreter are no longer checked; dropping them can only remove false reds.
  - Run with an interpreter whose own path holds `runs/`, the helpers skip only the exact interpreter token or element.
  - They still catch a word in any other token, an exe-prefixed path, an `=`-glued interpreter, and `hidden`.
  - The check that no started command names a path under the sets root is unchanged.
- **F1 still guards.** In a clone at `…/gov-os-runs/clone`, I planted a driver that opens a file under the sets root. F1 went red ("the driver itself touched the sets root").
  - The unplanted clone passes: 168 passed, 2 skipped (both F5s, each naming the missing `w2/integrate` reference).
- **W2-171's F5 (c6f7b9d6e).** On a planted `w2/W2-171` branch in the clone, the real case goes red naming exactly the two outside paths.
  - A detached HEAD skips with "this is a detached HEAD". The worktree (w2/W2-172) skips with "this is the branch w2/W2-172".
  - Against W2-170's F5 (W2-180's revision), only docstrings and the planted branch names differ.
- **Nothing moved.** `gov accept W2-172` passes 163/0/0 with all 14 KPI lines passing. W2-171's folder gives 139 passed and 2 skipped, each skip with its reason (an AF_UNIX sandbox stand-in, and F5's branch). Both runs went through heavy_slot.sh.

## Findings (recorded rows, none blocking)
Classification: 2 findings, both out of scope and failing closed; no round proposed.

**R1. An interpreter whose path holds a sets-root word stops every run.**
- What was done: I ran the W2-172 suite from the clone with an interpreter at `…/gov-os-runs/venv/bin/python`.
- What happened: the driver refused every run with exit 4 ("a line that names a sets-root folder was not printed"), and 77 of 163 cases went red.
- What should have happened: the revision's comment says an interpreter under `gov-os-runs/` does not trip the check. That is true of the test's grep, but the product refuses that line itself.
- Ordinary work: no, because the project's interpreters (the pin under ~/.local/share, /usr/bin) never live under a sets-root word, and the merge queue's clone passes with the pin. Hitting it takes a venv planted under gov-os-runs.
- Consequence: other (the product fails closed: it refuses, hides nothing and loses nothing).
- scope: out (product behaviour from round 1; not part of these two test revisions).
- Reversed by: a run of the merge queue, or a documented cron set-up, that uses an interpreter under a sets-root word.

**R2. The pinned gov's accept reports a crash when HOME is empty.**
- What was done: I ran `gov accept W2-172` with HOME set to an empty scratch folder, as the DEC-1012 run rule asks.
- What happened: outcome `error`/`crash` with zero counts. The pinned runner strips `PYTHON*` variables including `PYTHONUSERBASE`, so the child pytest cannot be found. The tree's src already carries W2-177's fix; the pin does not.
- What should have happened: the run completes. It did, 163/0, with the normal HOME and when the folder was run directly with an empty HOME.
- Ordinary work: yes, because every sandboxed worker following the empty-HOME rule runs `gov accept` through the pin.
- Consequence: other (fails closed: it reports an error, never a pass).
- scope: out (the pin's version, not W2-172).
- Reversed by: a pin built after W2-177 that passes `PYTHONUSERBASE` through, or `gov accept` passing with an empty HOME.

## Process notes
- The guard hook refused a symbolic link into my TMPDIR, and the Write tool was not granted for a `.pth` file in my TMPDIR. These were two different calls, and neither was retried or worked around.
- `gov accept` then ran with the normal HOME, after I confirmed neither folder has a `local_only`, `real`, `green_here` or `time_limit` case.
- No tree was written: `git status --porcelain` is empty and HEAD is unchanged.

```verdict
{"kpis": [{"kpi": "w2-172-fix-check", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "R2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
