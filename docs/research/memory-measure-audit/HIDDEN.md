# The rubric applied to the hidden half of the memory measure (DEC-1068 (2), W2-61h's role)

- **Status:** DRAFT for the owner. Nothing in the set changes until the owner decides (DEC-1068 (3)). These are
  recommendations only.
- **By:** an independent auditor in W2-61h's role (`.tickets/DAEO-h2k3.md`), 2026-11-04, working read-only under the
  hidden-half rule. This record quotes no hidden question, gold answer, gold source path, line or heading.
- **Against:** `w2/integrate` at `26b7edb73917`, with the path map there. The head moved to `bd87a8b21941` during the
  session; that commit only changes one ticket file, which is not a gold source, so every judgement holds there too.
  Each span was resolved with the measure's own span rule and read; no retrieval, measure or model was run.
- **Blind to results:** no measure record, search result or rank was read; neither were `VISIBLE.md` and lens B's
  report. R9 was checked against the text of the 24 visible questions.
- **Counts** are over the 22 questions judged here (h02 and h24 left out), except R2 and R5, which cover all 24.

## Per question

All items PASS unless listed.

| Id | Failed items | Reason, in general terms | Recommendation |
|---|---|---|---|
| h01 | R1-INCOMPLETE (minor) | Later standing decisions added refusals to the guard that the gold answer omits | Re-label, or re-word to ask for the named rule set only |
| h02 | — | Under correction by the owner's operator; verdicts held back (DEC-1068 (c)) | — |
| h03 | R1-INCOMPLETE (major), plus R1-DETAIL | A later standing decision, still in force, is the governing source for part of the answer and is not a source; a stale list in the answer | Re-label |
| h04 | R4-PHRASED-FROM-ANSWER (minor) | The question repeats its gold line's distinctive phrase | Re-word |
| h05 | R1-DETAIL (minor) | A stale line number in the gold answer | Re-label the answer |
| h06 | R4-PHRASED-FROM-ANSWER (minor) | The question is built from the comment beside the gold line | Re-word |
| h07 | none | | Keep |
| h08 | R1-INCOMPLETE (major), plus R1-DETAIL; R7-MISSING-PIECE (major); R10-RECORD (minor) | One caller, in the same module, is missing (it was there at the question's commit too), so the count is wrong; a stale line number | Re-label; record the re-anchor |
| h09 | none | | Keep |
| h10 | none | | Keep |
| h11 | none | Advisory: one alternative's span stops just short of the background line | Keep |
| h12 | R10-RECORD (minor) | Re-anchored (same fact, new span) with no written reason; the old copy is only in a dated backup, not a retired folder | Record the re-anchor |
| h13 | none | | Keep |
| h14 | none | | Keep |
| h15 | none | | Keep |
| h16 | R10-RECORD (minor) | As h12 | Record the re-anchor |
| h17 | R10-RECORD (minor) | As h12 | Record the re-anchor |
| h18 | R1-NOT-GOVERNING (minor, contested); R4-PHRASED-FROM-ANSWER (minor) | One alternative lies in the reports tier; the question repeats the sources' phrasing | Owner's reading (question 1 below); re-word |
| h19 | none | | Keep |
| h20 | none | | Keep |
| h21 | none | Advisory: part of the gold entry was later superseded; the question asks history, which still holds | Keep |
| h22 | none | | Keep |
| h23 | R10-RECORD (minor) | As h12 | Record the re-anchor |
| h24 | — | Under correction by the owner's operator; verdicts held back (DEC-1068 (c)) | — |

**R6 advisory:** 16 of the 24 have at least one lines-only anchor. All of them still hold their answer at the head.

## Counts

**FAILs per item, over the 22:**

| Item | FAIL | Major | Minor |
|---|---|---|---|
| R1 | 5 | 2 | 3 |
| R2 | 0 | 0 | 0 |
| R3 | 0 | 0 | 0 |
| R4 | 3 | 0 | 3 |
| R5 | set-level FAIL (below) | | |
| R6 | 0 (advisory only) | 0 | 0 |
| R7 | 1 | 1 | 0 |
| R8 | 0 | 0 | 0 |
| R9 | 0 | 0 | 0 |
| R10 | 5 | 0 | 5 |

- 11 of the 22 pass every item.
- 2 have a major FAIL (h03 and h08).
- Recommendations: re-label 5, re-word 3, record the re-anchor 5, mark as a keyword question 0, retire 0, keep 11.

**R2, keyword-only (over all 24):**

- Questions with any entry only in a keyword-only namespace: **0**.
- Questions with all entries there: **0**.
- Entries in neither index: 0. Paths that no namespace holds: 0.
- One alternative in the half is keyword-only, but its entry also has an embedded alternative.

**R5, the spread (over all 24):** FAIL, R5-DOMAIN-THIN.

| Governing domain | Questions |
|---|---|
| Decisions | 9 |
| Code | 9 |
| Contract and Charter | 2 |
| Tickets | 0 |
| The plan | 0 |
| None of the five (project configuration, the kernel's skill and role text) | 4 |

- **Tags:** kernel template 3 (pass). Failure memory 2 by category (pass), though neither cites a lesson or failure
  record.
- **Topic weight:** the largest subsystem holds 6 of 24, exactly at the 25 % bound (pass).
- **Supersession:** at least 4 questions have a superseded naive answer (pass).
- **Categories:** W2-61h KPI 3's category quotas are met exactly for the 28 new questions (pass).
- **Why the domains are thin:** the quota itself allows only one plan, ticket or path-map question.

## Two rubric questions for the owner

1. **R1.3 and harness code:** R1.3 rules out the reports tier, but R1 also says "for a code fact, the code". When the
   code is the test harness itself, which rule wins? This decides h18's R1 finding.
2. **R5's domain threshold:** W2-61h KPI 3's category quotas cannot meet the proposed 3 of 24 for tickets or the plan.
   Should the threshold change, or the quotas?
