---
id: W2-37-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-13
branch: w2/W2-37
base: 96498443f (F1 (a) built and its tests merged; the change skill as Wave 1 left it)
head: {SKILL_HEAD}
ticket: DAEO-6n5k (W2-37)
task: DAEO-6n5k
author: orchestrator (W2-37 ticket lead)
review: {REVIEW}
decisions_carried: [DEC-167, DEC-816, DEC-1163]
decisions_applied: [DEC-1157, DEC-1083, DEC-105]
state_class: EVIDENCE
---

# W2-37: change-impact proposal (CIT-P) on the change skill's impact section

The change skill's `## Impact assessment` section states Wave 1's method: the plain-language question "what is the
impact of X?" triggers an assessment done by hand with `gov closure`. Wave 2 has `gov impact` (this ticket), which
takes that question itself and answers over both graphs. This change routes the section to `gov impact`
(CAP-33.g, DEC-167; DEC-816 named the section, DEC-1163 (7) put its two source files in the ticket's paths and asks
this CIT-P). The section is in the kernel's skill files, so the owner approves the bytes before the merge (CAP-33).

## 1. What triggers the change

| # | Trigger | Source |
|---|---|---|
| T1 | From Wave 2, "what is the impact of X?" runs `gov impact` (the ticket's KPI S1) | CAP-33.g, DEC-167 |
| T2 | The section named for the change, and its synced copies | DEC-816 |
| T3 | The two source files in W2-37's paths; a CIT-P with the lines verbatim, both hashes and an independent review; the root `.rulesync` and `.claude` copies by the CTO's copies ACT after the approval | DEC-1163 (7) |

## 2. The kernel files and their sha256

{HASH_TABLE}

## 3. The lines, verbatim

{DIFF}

## 4. Impact

{IMPACT}

## 5. Options (DEC-105)

{OPTIONS}

## 6. Review

{REVIEW_BODY}
