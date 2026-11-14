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
