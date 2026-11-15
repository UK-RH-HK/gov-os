---
type: probe
task: DAEO-qvff
round: r4c
reviewer_session: 21e927ea-dc13-4df1-be61-bc6f2ce0e01b
implementer_session: "fa09841f-4475-4da2-b503-2625e317462f"
reviewer_wrote_nothing: true
reviewer_model: claude-opus-5-5
reviewer_effort: high
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: e2f3f8ca4e67bb51103e09dd9c48370819dcb93b
reviewed_commit: 3137efe994335cae371ef779c78978f770f0a5f7
decisions_applied: [DEC-1154, DEC-1010, DEC-808, DEC-1184, DEC-979, DEC-906, DEC-968, DEC-958, DEC-1157]
---

# Probe record: W2-111 (DAEO-qvff), r4c: the narrow re-check (DEC-1154) of 3137efe99..e2f3f8ca4

## The lead's judgement

**Why there is a re-check.** At 17:07 on 2026-11-15 the land queue refused the branch: "FULL ticket without a passing
independent review record at 13a74e7051a6". The ticket's review, round 1 of at most two, passed at `3137efe99`
(`PR-DAEO-qvff-r4.md`, all six reopen lines pass). After that, the branch gained four first-parent commits:
- `a8ea132f3`: the r4 record;
- `75e709f68`: the merge of td-3's `3b910336e3fb`, which adds 36 lines of measured figures to
  `tests/acceptance/W2-111/README.md`;
- `13a74e705`: a merge of w2/integrate at `076cded14`;
- `e2f3f8ca4`: a merge of w2/integrate at `301708296`, the re-pin from release 0.1.0, made by the lead in this run.

This is a narrow re-check under DEC-1154. It is not a review round.

The lead found the refusal's actual cause: `PR-DAEO-qvff-r4.md` holds a quoted copy of its verdict block
(`> ```verdict`) above the real one. The queue's `verdict.ready()` reads that record as "the verdict block is not the
structured form (fail closed)", so it would refuse r4 at any head. This record holds the reviewer's block once, unquoted.
`ready()` returns `(True, [])` on it before the commit.

**The reviewer.** A fresh independent auditor:
- model claude-opus-5-5, effort high, class C3;
- launched read-only with `--owner-named DEC-1154`;
- session `21e927ea-dc13-4df1-be61-bc6f2ce0e01b`;
- brief `rv-2`, which carried JUDGEMENT.md word for word and asked for the verdict block.

The reviewer wrote nothing: `git status --porcelain` was empty at e2f3f8ca4. The launcher's tripwire saw one change, the
head of `W2-00-record` (`af01451ae091` to `6330f014e51e`). That is the CTO's record commit of 17:13:37 (Task DAEO-sdxk),
not the reviewer's work.

**What it confirmed.**
1. **Only the README changed in W2-111's paths.** From 3137efe99 to e2f3f8ca4 these diffs print nothing:
   `git diff --stat -- src/gov/guard tests/unit/guard`. Over all the judged paths the only change is
   `tests/acceptance/W2-111/README.md`: 36 lines, one new section, and no `.py`, conftest or support file. The judged
   paths are the 15 revised cases and their READMEs, `tests/acceptance/W2-111/**`, `tests/acceptance/W2-42a/…` and
   `src/gov/guard`.
2. **The figures match the logs they came from.** The README section was committed at 02:29 and its figures come from
   the lead's runs of 00:02 to 02:08.
   - Every ms value and planted range in the table matches its log.
   - The gov accept row matches `accept-1.json`.
   - Some load labels and context notes are off. These are rows R1 to R3 below.
   - The r4b logs (12:38 to 12:59) contradict no verdict. After the change, quiet runs give 27.0 to 50.5 ms and runs at
     load 60 to 64 give 46.4 to 86.5 ms, all passing. The planted 150 ms hook fails every case in every round at
     178.1 to 253.3 ms.
   - The README's lines "quiet run after … not yet taken", "(180-304)" and "every load (20-59)" have been stale since the
     r4b runs. Stale is not a contradiction (R4).
3. **The merged integrate changes touch none of W2-111's judged files.**
   - 74 paths changed, none under `src/gov/guard`, `src/gov/util`, `.claude/`, the conftests above the cases, or the
     judged folders.
   - `pyproject.toml` changed only in package data.
   - The guard's imports (`gov.guard.*`, `gov.util.*`) and the YAML it reads (`path-map.yaml`, `held-out.yaml`,
     `roster.yaml`) are unchanged.
   - The cases run `src/` through PYTHONPATH, so the re-pin of the installed gov does not reach the code under test.

**The verdict block, as returned:** all 13 lines pass (success-1 to success-8, failure-1 to failure-5), each "unchanged
since the reviewed commit, so the r4 verdict stands". No finding is in scope, reachable in ordinary work, and fails open
or loses work, so the branch is READY by the block's rule.

**The lead's triage.** Every finding is a row, and none blocks.
- R1 to R4 are labels in the README's figure table and text that were copied by hand. None of them changes a figure or a
  verdict. Correcting them, and adding the r4b figures, is a README revision for a later test-design batch.
- R5 is the reviewer's step 0 (a). The hook's reviewer write rule refused it twice, before the OS sandbox was reached.
  The check failed closed. This is the known behaviour for a read-only reviewer.

## Findings (the reviewer's, with their two lines)

- **R1** (success-5, success-6 figures; README row "about 20 / before"). The load column says 20-24. The log shows
  23.2-26.3 for the Bash rounds and 20.8-23.4 for the tree cases; the planted cases ran at 7.4-18.5.
  `Ordinary work: yes, because the figures were copied by hand from a log.`
  `Consequence: other`. Scope: out.
- **R2** (failure-5 figures; row "50 or more / after"). In `measure-load58-after.log` the planted cases ran at load 38-49,
  not 51-59. Five planted figures are printed, not four; the fifth (trees Write, 203.7-212.2) has no recorded result.
  `Ordinary work: yes, because it is a transcription slip.`
  `Consequence: other`. Scope: out.
- **R3** (success-6 figures; row "gov accept"). "load 25-40" and "PATH 5 entries" appear in neither `accept-1.json` nor
  `accept-1.err`. The verdicts in the row do match the JSON.
  `Ordinary work: yes, because the context was recorded somewhere other than the logs named.`
  `Consequence: other`. Scope: out.
- **R4** (README text). "The quiet run after the change is not yet taken", "(180-304)" and "every load (20-59)" have been
  stale since the r4b runs, though the verdicts are the same.
  `Ordinary work: yes, because the README was written before the later runs.`
  `Consequence: other`. Scope: out.
- **R5** (the reviewer's step 0). Check (a) was refused twice by the hook's reviewer write rule, so the OS sandbox itself
  was never tested. The target file is absent.
  `Ordinary work: yes, because the auditor role runs this check by brief.`
  `Consequence: other` (failed closed). Scope: out.

## The verdict block (the reviewer's, copied unchanged)

```verdict
{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, {"kpi": "success-2", "verdict": "pass", "findings": []}, {"kpi": "success-3", "verdict": "pass", "findings": []}, {"kpi": "success-4", "verdict": "pass", "findings": []}, {"kpi": "success-5", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-6", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-7", "verdict": "pass", "findings": []}, {"kpi": "success-8", "verdict": "pass", "findings": []}, {"kpi": "failure-1", "verdict": "pass", "findings": []}, {"kpi": "failure-2", "verdict": "pass", "findings": []}, {"kpi": "failure-3", "verdict": "pass", "findings": []}, {"kpi": "failure-4", "verdict": "pass", "findings": []}, {"kpi": "failure-5", "verdict": "pass", "findings": [{"id": "R2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
