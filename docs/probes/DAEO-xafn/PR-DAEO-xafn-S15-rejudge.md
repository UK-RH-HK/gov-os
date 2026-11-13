---
type: probe
task: DAEO-xafn
reviewer_session: independent-auditor subagent of the Wave 2 CTO session b2f0511f (S15 re-judge, 2026-11-13); not W2-148's author, not the FULL probe's reviewer
implementer_session: not recorded
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 02873772c7dbca22c7bdbff02a5ca80ddd9e8c06
---

# Probe record: W2-148 (DAEO-xafn) S15 re-judge after ACT-W2-148-S15-1 (DEC-1142 (4)), on w2/integrate 02873772c7db

task: DAEO-xafn
decisions: DEC-1142, DEC-1104, DEC-1131, DEC-1108, DEC-1106, DEC-1010, DEC-801, DEC-808, DEC-1014, DEC-136, DEC-820

## Scope of this record

- **Narrow re-judge of one KPI line, S15**, after the owner's choice of S15's option 2 (DEC-1142 (4)) and its ACT, ACT-W2-148-S15-1, applied by the owner's operator: commit `4be656e70589` (`Role: owner`, `Task: DAEO-sdxk`, `Implements: DEC-1142`; `governance/project/operator/class-rules.yaml` only), an ancestor of the probed commit.
- **The other 38 lines (S1 to S14, S16 to S24, F1 to F15) are carried from the FULL probe `docs/probes/DAEO-xafn/PR-DAEO-xafn.md` (probed commit `2ef060a65c77`) at their verdicts and with their findings (FR-2 to FR-5 as rows), not re-probed here.** Between the two commits the operator's code (`act_class.py`, `operator_run.py`, `opcommon.py`, `verdict.py`, `freeze_gate.py`, `landing_check.py`, `operator_launch.py`) is byte for byte the installed copy; the only operator change since the FULL probe that this record judges is the table.

## S15: pass

S15 as written: after an (a) ACT, the control files hash as before, the settings deny lists and the path map differ only by the computed additions, and **for path-map or deny-list additions a replay of the guard** (checked against the call log by sha256 both ways, DEC-1108 (2)) changes no allowed call to refused beyond the review's list; any other difference undoes the ACT (under DEC-1106 (1)) and pushes a P1.

FR-1 failed it because the `settings` row made a deny addition to the home `~/.claude/settings*.json` class (a), while the after-check's replay reads only repository touched files. What I probed:

1. **The table, live and in the tree.** `~/gov-os-operator/install/class-rules.yaml` equals `governance/project/operator/class-rules.yaml` at `w2/integrate` byte for byte (sha256 `38ac2f2decce660a9e190c85038b7175dcbae0e0c0ce79acc0597df17d0e79a4`, the ACT's after). The install's `APPROVED` is `3744df3a637feadc26c673b88a10cbc757e8c8746aced078d700300906962815` (the ACT's after on the HOURS-3 base) and its own hash list checks OK for all 14 files (read-only). The seven operator code files in the install equal the tree's.
2. **The rule.** The `settings` row now matches only the repository's `.claude/settings*.json` (its deny-only list rule kept). A new `home-settings` row, straight after it, makes the home `.claude/settings*.json` a fixed (b), with `control: true`. Rows are matched first-to-last. No earlier row matches a home settings file. Every row with a list rule (`settings`, `rulesync-permissions`, `path-map`, `test-map`, `optin`) is now repository-root only, and the only home rows of class (a) are `cache` and `servers`, which hold neither deny lists nor the path map. So every deny list or path map that an (a) ACT can touch is a repository file, and those are the files the after-check replays and snapshots.
3. **The FR-1 plant, against the installed table.** An ACT claimed (a) and reviewed (a), adding `Read(**)` to the home `settings.json`'s `permissions.deny`, was run through the real `operator_run.py` in W2-148's planted world, in a clean detached worktree of `02873772c7db`. The world's install table was checked equal to the live installed table by sha256. Result: refused at G6, votes code b / claim a / review a. The reason was "class (b): no owner's line ... after the review", from row `home-settings`, with a disagreement notice. The home file was unchanged and no applied line was written. Before the ACT, the same plant was applied as (a) with no replay (the FULL probe's FR-1; the ACT's rehearsal and review reproduced the bite on the old table, and this record does not re-run it).
4. **S15's own cases.** All of them are green inside the full run below: the control-family undo with a P1, the path-map replay that keeps an addition when only listed calls turn and undoes it on an unlisted one, DEC-1108 (2)'s 13 call-set checks, and the F15 concurrent-change case.

**Tests** (clean detached worktree `/tmp/claude-1000/s15-rejudge-*` at `02873772c7db`, removed after; `heavy_slot.sh`, `-p no:cacheprovider -q -n auto`, TMPDIR inside that /tmp folder, outside the repository and `~/gov-os-runs`):
- `tests/acceptance/W2-148` and `tests/unit/operator` in full: **654 passed, 0 failed** (66.9 s).
- The FR-1 probe (the ACT's rehearsal probe, plus a check of the installed table's bytes): **2 passed, 0 failed**.

**What would reverse it:**
- A home `.claude/settings*.json` change that the installed `act_class` classes as (a). Today none can be, because the first matching row is `home-settings`, which is fixed (b).
- Any list-rule row or (a) row that matches a deny list outside the repository.
- The installed table drifting from the repository's: its sha256 is no longer `38ac2f2decce`, or `APPROVED`'s check fails.

## Findings

Classification: 0 blocking. FR-1 is closed by DEC-1142 (4). One row (R-1) is carried from the ACT review's F3.

- **R-1 (S15, the ACT review's F3).** The home settings are still not among the after-check's control files. Since this ACT an (a) ACT cannot list them. Only an unlisted write by an (a) ACT's script could reach them, and the dry run (S12) catches that: its changed set covers HOME, and an unlisted file refuses at G8.
  - scope: out
  - Ordinary work: no, because an (a) ACT that writes a file it does not list would have to get past the dry run's unlisted-file check first.
  - Consequence: other
  - Reversed by: an (a) ACT's script writing the home settings unlisted and passing the dry run.

## Notes for the close (not findings)

- `gov close` reads READY from the newest committed record under `docs/probes/DAEO-xafn/` that holds a block. That block must be last written by a commit carrying the reviewer's role alone, and every commit of the record must carry that role. The record's `probed_commit` must be an ancestor of the closing HEAD.
- **One guard refusal, not retried in the same form.** Copying the probe file into the temporary worktree's `tests/acceptance/W2-148/` was refused: "a reviewer or auditor writes only ... or /tmp". The probe and a copy of the `world` fixture were then written into a separate folder under `/tmp`, outside every tree, and the W2-148 support module was imported from the temporary worktree. No file under any `tests/acceptance/` was written.
- The repository's tracked files and `~/gov-os-operator` were not written; `git status --porcelain` of the main tree is empty.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": [{"id": "FR-5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "S11", "verdict": "pass", "findings": []}, {"kpi": "S12", "verdict": "pass", "findings": []}, {"kpi": "S13", "verdict": "pass", "findings": []}, {"kpi": "S14", "verdict": "pass", "findings": []}, {"kpi": "S15", "verdict": "pass", "findings": [{"id": "R-1", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S16", "verdict": "pass", "findings": []}, {"kpi": "S17", "verdict": "pass", "findings": []}, {"kpi": "S18", "verdict": "pass", "findings": []}, {"kpi": "S19", "verdict": "pass", "findings": []}, {"kpi": "S20", "verdict": "pass", "findings": []}, {"kpi": "S21", "verdict": "pass", "findings": []}, {"kpi": "S22", "verdict": "pass", "findings": []}, {"kpi": "S23", "verdict": "pass", "findings": []}, {"kpi": "S24", "verdict": "pass", "findings": [{"id": "FR-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": [{"id": "FR-3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "F6", "verdict": "pass", "findings": []}, {"kpi": "F7", "verdict": "pass", "findings": []}, {"kpi": "F8", "verdict": "pass", "findings": []}, {"kpi": "F9", "verdict": "pass", "findings": []}, {"kpi": "F10", "verdict": "pass", "findings": []}, {"kpi": "F11", "verdict": "pass", "findings": [{"id": "FR-4", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "F12", "verdict": "pass", "findings": []}, {"kpi": "F13", "verdict": "pass", "findings": []}, {"kpi": "F14", "verdict": "pass", "findings": []}, {"kpi": "F15", "verdict": "pass", "findings": []}]}
```
