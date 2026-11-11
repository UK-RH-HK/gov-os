# W2-142 evidence: search again once in the kernel skills (DAEO-qskx; DEC-1094 (2), DEC-1092 (1), DEC-1097 (8))

**The change.** SEARCH-AGAIN-PRACTICE (`governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md`)
§3.1 and §3.2, applied exactly; nothing else in either skill changes.

- **`template/governance/kernel/skills/retrieval/SKILL.md`:** step 7 after step 6, before "## Key constraints" (§3.1's
  paragraph, one line); W2-138's step-5 line kept; `version` "1.0.0" to "1.1.0".
- **`template/governance/kernel/skills/discovery/SKILL.md`:** line 55 gains §3.2's sentence; `version` "1.0.0" to
  "1.1.0".
- The generated `.claude/skills/` copies are not changed here (DEC-315): they are regenerated at the lift's re-pin ACT.

## The KPI lines and how each is met

| KPI | How it is met | Verify |
|---|---|---|
| S1: the retrieval skill's step 7 (the practice, the "does not answer" list in short, the cap of two searches), W2-138's step-5 line kept, version 1.1.0, under the size budget | §3.1's step 7 inserted after step 6; steps 1-6 untouched; front matter `version: "1.1.0"` | `PYTHONPATH=src python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/retrieval template/governance/kernel/skills/discovery`: `{"findings": []}`; `gov accept W2-142` |
| S2: the discovery skill's line 55 gains one sentence (search again once before routing a question as unanswered); version 1.1.0 [DEC-1097 (8)] | §3.2's sentence appended to line 55; front matter `version: "1.1.0"` | the same validator run; `gov accept W2-142` |
| S3: it lands at the lift's re-pin ACT, after the project layer has been in use; the adoption count's first reading in the evidence | the CTO's, at the lift's re-pin ACT: the generated `.claude/` copies regenerated there, and the adoption count's first reading | the ACT's record and this evidence |
| F1: no change beyond the two named lines; W2-138's step-5 line not lost | `git diff` against `w2/integrate` shows only step 7, line 55's sentence and the two version lines | `gov accept W2-142` |

## Results

- **Skills check:** `{"findings": []}` for both skills, both layouts.
- **`gov accept W2-142`:** pass, 9/9: success-1 4, success-2 3, failure-1 2; 0 unmapped, 0 skipped. S3 has no
  acceptance case: it is met at the ACT.
