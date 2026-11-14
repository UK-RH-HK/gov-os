---
type: probe
task: DAEO-uw5h
reviewer_session: ed998176-b05d-4462-acf4-bb4a4ede09e4
implementer_session: 836194c6-44c6-45a7-9218-ccff2a11ec57
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: f8e7c0fad6c6f07e48edb0d7e110625212089066
decisions_applied: [DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112, DEC-801, DEC-808, DEC-1010]
---

# Probe record: W2-100, the narrow independent check of the four domain skills (check 1)

A fresh independent-auditor session (`ed998176-b05d-4462-acf4-bb4a4ede09e4`) ran on Opus at high effort, class C2,
with read-only tools. It probed head `f8e7c0fad6c6` of `w2/W2-100` (base `627bcaa19351`, the merge of the ticket's
interface) and wrote nothing in the tree: `git status --porcelain` was empty when it finished. Its brief carried
JUDGEMENT.md word for word. The implementers were:
- product-spec ps-1 (`836194c6-44c6-45a7-9218-ccff2a11ec57`): `a7989493b` (the scenarios, before the text) and
  `c7686c533` (the four skills, `check_domain_skill.py`, the `.rulesync` copies);
- product-spec fix 1 (`2125e132-c077-4cfd-ac60-a0b45b32c215`): `fef53fb21`; batch 2 (`7f067bc9-4d95-4ebc-b18a-f72acb35c721`):
  `b266cf8a4`; fix 2 (`e859d446-e243-4df5-a8d4-f9164f30d36b`): `121c99a44`; batch 3
  (`08f87d1f-1380-43ae-b26b-e80355368346`): `b3503e0a3`;
- test designer td-1 (`3eb5fc04-64f6-4ceb-9fcd-89784d9aea97`): `d9379baaa`; td-2 (`4f0b240e-e96e-4619-b3fd-3c5a1c44b977`):
  `26a1a98ce`. The lead merged the tests as `8ce2dd268` and `f8e7c0fad`.

## The lead's triage (DEC-1010: a finding blocks only if in scope, ordinary work and fails open or loses work)

- **F1** (S4, in, ordinary work yes, other): run 5's passes were made with `scenario-summaries.md` in the session's
  skill folder. Not blocking; accepted and acted on in the same round (DEC-802): clean runs 6 to 8 with the summaries
  moved aside, and each summaries file now states it. Checked by check 2 (`PR-DAEO-uw5h-check2.md`).
- **F2** (S4, out, ordinary work yes, fails open): `gov skilleval` (W2-104's harness, `src/gov/skilleval/harness.py:167-168`)
  copies every file of a skill folder but `scenarios.md` and the record into the session, so a later run of these
  skills sees the summaries. Out of this ticket's scope and paths (`src/`): package P-W2-100-F2 to the CTO in the
  lead's return; an entry criterion for the next `gov skilleval` of any folder holding a summaries file (DEC-803).
- **F3** (S4, in, other): api scenario 2 had one clean fail and one borderline clean pass. Acted on: run 6 failed it
  again cleanly; the api text was fixed (1.0.2, `3318e42f6`, `05fcc8f2e`); clean runs 7 and 8 pass it.
- **F4** (F2, in, other): `fef53fb21` labels the defect "a security finding" in the Situation. A row (the scenario
  passed twice on the earlier wording).
- **F5** (F2, in, other): I1's below-P1 check is bound to the word "finding(s)", per the interface. A row for a later
  I1 revision (also vulnerability, weakness).

## The reviewer's record (verbatim)

# W2-100 (DAEO-uw5h): independent auditor's check of the four domain skills

- **task:** DAEO-uw5h
- **decisions:** DEC-959 (items 4, 5, 7), DEC-957 (Q5, the escalation rubric), DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112 (3), CAP-24.b, DEC-801, DEC-808, DEC-1010, DEC-803
- **Probed head:** `f8e7c0fad6c6` (base `627bcaa19351`). **Session:** `ed998176-b05d-4462-acf4-bb4a4ede09e4`.
- **Method:** read-only. I1 and the skill validator on the real files and on in-memory planted copies. Records vs envelopes, summaries vs records and captured replies, the harness's copy list, `diff -r`, the adapter check, commit order and trailers. No pytest run, no model call.

## What was probed and found sound
- **Template and parts:** the four SKILL.md files have the template's eight sections in order, the five labelled parts and every named point. Front matter is closed with versions equal, bodies are 131 to 143 lines, and there are no deep reference files. The text is substantive and correct for each area.
- **I1:** byte-equal ×12, PASS on the real files. It refuses every planted defect the interface lists, naming it (sections, parts, points, permission lines in the front matter and body, order, a heading after Sources, a security P2 route).
- **Validator:** exit 0 on the four folders. It names a 400-line body and an `allowed-tools` key.
- **S2:** no permission grant in any file of the four folders; nothing tells the role to write outside its paths or beyond `output: none`. The guard case is not vacuous.
- **F2:** no below-P1 route in the security skill. Scenario 2 wants P1. The lead's planted P2 copy gives 3 REFUSED lines and `gov skilleval` exits 3 with scenario 2 FAIL.
- **S4 order and records:** `scenarios.md` committed before SKILL.md (`a7989493bb19` < `c7686c533f86`). The records equal the envelopes in order (runs 1–5 as the lead stated), and the api run-1 fail is kept. Summaries match the records one to one with three lines each, and the sampled summaries agree with the replies.
- **S5:** nothing imported.
- **S6:** the copies are identical. The adapter check gives no `SOURCE_*`, and its 20 `GENERATED_DIFFERS` are only the absent `.claude/skills/` copies (the copies ACT).
- **Tests:** they bite both ways, and the td-2 revision is justified.
- **Scope:** ticket paths and tests only. Trailers are correct.

## Findings
| id | KPI | scope | summary | Ordinary work | Consequence |
|---|---|---|---|---|---|
| F1 | S4 | in | Run 5's 12 passes made with `scenario-summaries.md` in the session's skill folder (backend 1 read it); not disclosed | yes, because the lead followed the interface and re-ran after a version raise | other |
| F2 | S4 | out | Harness (`harness.py:167-168`) gives every future run of these skills the summaries: a weakened skill can pass | yes, because every later revision re-runs its scenarios | fails open |
| F3 | S4 | in | api 2: one clean fail, one clean borderline pass after a re-run with unchanged text | yes, because a re-run after a fail is ordinary | other |
| F4 | F2 | in | `fef53fb21b40` labels the defect "a security finding" in the Situation (not the route); earlier wording passed twice | yes, because fitting a test's word is ordinary | other |
| F5 | F2 | in | I1's below-P1 check is bound to "finding(s)"; "vulnerability"/"weakness" P2/P3 routes pass | yes, because an editor may word it that way | other |

**What would reverse each finding:**
- F1: a clean 1.0.1 re-run with the summaries moved out passes all twelve.
- F2: the harness leaves the file out, or it moves out of the folder.
- F3: a clean api 2 re-run passes.
- F4: the earlier wording fails where the current wording passes.
- F5: the interface intends the narrow rule, so it stays a row.

**Classification:** 0 blocking (none is in scope, ordinary work, and fails open or loses work). 4 in-scope rows (F1, F3, F4, F5). 1 out-of-scope package (F2, fails open, P1 to the CTO).

**Recommendation:** no review round. Before the CIT-P cites run 5, the lead re-runs the 12 scenarios at 1.0.1 with the summaries moved aside, or states that the clean evidence is 1.0.0's. The CTO takes P-W2-100-F2: (a) W2-104's ignore list leaves `scenario-summaries.md` out (recommended), (b) move the summaries out of the skill folder, or (c) record the gap.

**Refusals:** 1. The Write tool in my TMPDIR was refused under quiet hours and queued for the morning package. I did not retry it.

## The reviewer's verdict block (verbatim)

```verdict
{"kpis": [
 {"kpi": "w2-100-S1", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-S2", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-S3", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-S4", "verdict": "pass", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "w2-100-S5", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-S6", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-F1", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-F2", "verdict": "pass", "findings": [
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "w2-100-F3", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-F4", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-F5", "verdict": "pass", "findings": []},
 {"kpi": "w2-100-F6", "verdict": "pass", "findings": []}
]}
```
