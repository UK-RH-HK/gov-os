# Readiness review 6 of 7: the search-again practice in the agents' briefs (DEC-1097 (3))

Reviewer: independent, read-only, in-session (2026-11-08), for the Wave 2 CTO. Branch `w2/integrate` at `0732a0a74a31` (read at
the review's end; the session started at `e66f2a696`).
Nothing under `~/gov-os-eval/`, no hidden or spent question file and no run-folder row was opened. The harness script
`drafts/d4b/e2_run.py` was read for its prompt strings and control flow only (it holds no question text).

## What was checked, against what

The measured practice (E2): `e2_run.py` lines 31-37 (`READER_SYS`), 141-159 (the attempt loop: cap 3, A2 = the cut at
two, a `search_again` at the cut counts as not found); `E1-DECLARATION.md` amendment item 1 (the "may be incomplete"
line, DEC-1091 (3)); `E2-RESULT.md`; `D4B-SEARCH-AGAIN.md` §3; `SEARCH-AGAIN-PRACTICE.md` §2, §3.4-3.6, §7;
DEC-1092 (1), DEC-1093 (2), DEC-1094 (2), DEC-1096, DEC-1097 (1), (3), (6).

The harness prompt's substance, item by item, against the three briefs:

| E2's reader prompt (`e2_run.py` 31-37) | LEAD-w2-common l.30 | AUDITOR-common l.8 | EMG-common l.45-51 |
|---|---|---|---|
| bundles do not answer: give different search words (the reader's own words, D4B §3) | yes ("own, different words") | yes | yes |
| "If you can tell your answer may be incomplete, search again for what is missing" | trigger yes; "for what is missing" no (F3) | trigger yes ("your finding may rest on an incomplete answer"); direction no (F3) | trigger yes; direction no (F3) |
| answer not in the repository: not_found | yes ("says 'not found'") | **no** (F2) | yes |
| cite path, start_line, end_line | yes ("path and lines") | no (F2) | yes |
| "Never answer beyond the bundles." | **no** (F1) | **no** (F1) | **no** (F1) |
| cap: three attempts run, judged at the A2 cut; the reader is not told the cap | "two searches in all" (same effect) | same | same |

Verdict on the match: **the trigger, the reformulation in own words and the cap of two match E2 in substance in all
three briefs.** The briefs lack the harness's "never answer beyond" clause (F1), and the auditor brief lacks the
not-found exit (F2). Both favour the harness: the judged reader is stricter than the briefs, so the 80's verdict on
the harness is unaffected, but its transfer to agents in use carries a caveat (wrong claims could run higher than
measured). The fresh 80's judged reader is E2's harness prompt (FRESH-80-1 §3.1 line 156), not the briefs.

Other checks, all clean:
- **W2-128 (`.tickets/DAEO-t8mp.md` line 55):** carries SEARCH-AGAIN-PRACTICE §3.3's line word for word, marked
  `[added, DEC-1092; approved by DEC-1094]`, including "never answer beyond what you read". Substance matches E2.
- **W2-142 (`.tickets/DAEO-qskx.md` lines 24-28):** S1 and S2 carry §3.1 and §3.2 exactly by reference, W2-138's
  step-5 line kept; §3.1's step 7 carries "Never answer beyond what the bundles and the files you read show".
- **The kernel retrieval skill** (`template/governance/kernel/skills/retrieval/SKILL.md`, v1.0.0): nothing contradicts
  the practice. Step 5 (the line-hash check) and step 6 (continuation) agree with the practice's "does not count" list.
  The generated `.claude/skills/retrieval/SKILL.md` still lacks W2-138's step-5 line (known; regenerated at the re-pin
  ACT). No kernel role file, template or other skill speaks of how to search (`discovery` l.35, l.55; `checkpoint` l.42
  only say where knowledge comes from); `w2-orchestrator.md` l.127, l.341, l.391 only require naming `gov retrieve`.
- **The exclusion line (DEC-1093 (2)):** LEAD-w2-common l.73 requires it in every engineer brief, in the decision's
  words; EMG-common l.38-42 carries it. The engineer briefs written after DEC-1093's commit (`38dda3b27`, 11-07 18:47):
  `W2-136-engineer.md` (18:48, l.15-17) and `W2-136-engineer-r2.md` (19:08) carry it. `W2-137-engineer*.md` and
  `W2-138-engineer.md` (16:35, 17:17) predate the decision; `W2-138-engineer-r2.md` carries a form of it anyway.
  `build_lead_brief.py` reads the committed LEAD-w2-common, so every new lead brief carries both lines.
- **No glossary:** no brief (governance/project/briefs, the CTO's briefs folder), kernel template, skill, role file,
  generated `.claude/` skill, agent or template, the w2 prompt, `facts.yaml` or any ticket mentions a glossary. Nothing
  tells an agent to paste one or to use the prototype (E2G: −6, p 0.031; DEC-1097 (6) still OPEN). FRESH-80-1 §3.1 lists
  E2G's glossary as excluded.

## Findings

### F1: the three project briefs omit "never answer beyond what you read"
- Where: LEAD-w2-common.md l.30, AUDITOR-common.md l.8, EMG-common.md l.49-51. E2's prompt ends "Never answer beyond the
  bundles." SEARCH-AGAIN-PRACTICE §7 says that clause "stays in every copy of the practice", but the package's own
  patches 3.4-3.6 (approved as written, DEC-1094 (2)) left it out; the kernel copies (W2-128's line, W2-142's step 7) have it.
- Scope: in.
- Ordinary work: yes, because every worker and auditor brief written today is built from these lines.
- Consequence: other (a weaker hold on wrong claims in agent work; nothing fails open; the 80's judged reader has
  the clause, so the verdict is not wrong).
- Classification: **ROW.** Fix it at the next touch: add "never answer beyond what the bundles and the files you read
  show" to the three lines (the CTO's lane, minutes). Evidence that would reverse it: a decision that dropped the clause
  from the project layer on purpose.

### F2: AUDITOR-common gives no not-found exit and no citation form
- Where: AUDITOR-common.md l.8: "search once more … before you rely on it; two searches in all"; there is no "or say
  'not found'" and no "with path and lines", which E2's prompt and the other two briefs carry.
- Scope: in.
- Ordinary work: yes, because every reviewer brief starts from this file.
- Consequence: other (an auditor may rest a finding on a guess, or not say what is missing).
- Classification: **ROW** (rides along with F1's edit).

### F3: the briefs drop E2's direction "search again for what is missing"
- Where: all three briefs. E2's line points the second search at the missing part. The briefs only say "in your own,
  different words"; SEARCH-AGAIN-PRACTICE §2 adds the ids and names the first bundle showed, which the briefs also leave out.
- Scope: in.
- Ordinary work: yes, because it applies on every incomplete answer.
- Consequence: other (a less aimed second query; Q14's kind is the case).
- Classification: **ROW** (rides along with F1).

### F4: "two searches in all" sits beside `--continue` with no word that a continuation is the same search
- Where: LEAD-w2-common l.30 and AUDITOR-common l.8 put the cap and the batching rule (`--batch-size`, `--continue`)
  side by side. Only SEARCH-AGAIN-PRACTICE §2 and the skill's step 7, which has not landed (W2-142), say that a
  continuation is not the second search.
- Scope: in.
- Ordinary work: yes, because a large question is batched by the same brief line.
- Consequence: other (an agent could stop a batched search early, or skip its real second search).
- Classification: **ROW**. W2-142 resolves it; until then, add "(a `--continue` is the same search)" with F1.

### F5: W2-128's and W2-142's string-test KPIs do not fit their own proposed texts as literally written
- Where: DAEO-t8mp l.55: "a string test on T-0 and T-8 for 'search again once', 'own, different words', 'not found' and
  'two searches'". T-8's proposed line (SEARCH-AGAIN-PRACTICE §3.3) holds only "search again once". T-0's line and
  §3.1's step 7 (DAEO-qskx S1) start "Search again once" and say "Two searches", both capitalised.
- Scope: out (W2-128 and W2-142 are kernel-layer tickets, neither before the 80).
- Ordinary work: yes, because a test designer who reads the KPI literally writes a case-sensitive test, or tests T-8
  for all four strings.
- Consequence: other (a KPI dispute or an extra round in those tickets).
- Classification: **ROW**. Each ticket's test-designer brief should say "case-insensitive; T-8 for 'search again once'
  only".

### F6: FRESH-80-1 item 19 does not require the copied reader prompt to stay byte-identical
- Where: FRESH-80-1 §2 item 19 ("a fresh-80 copy of each … one review (READY), then the files pinned by hash"); §3.1
  says "E2's reader … with the 'may be incomplete' line". Nothing requires `READER_SYS`, `READER_SCHEMA`,
  `GRADER_SYS`, `CAP = 3` and the A2 cut to be identical to `e2_run.py`. Now that the briefs carry other wording, an
  honest builder could "align" the prompt with them.
- Scope: in (does the harness match what was measured).
- Ordinary work: yes, plausibly, when the copy is written. Not present today: the scripts are not built.
- Consequence: other today. It would make the verdict judge a reader not chosen on the 138 (DEC-1092 (4)) only if it
  happens, and the item's review and hash pin stand before the 80.
- Classification: **ROW, riding along into item 19's build and review brief (DEC-802)**: one check that the four
  strings and the cut are byte-identical to `e2_run.py` (a hash of each), named in the review's KPI.

### F7: the adoption count is not built
- Where: DEC-1094 (2)(6): a read-only count, weekly from about 11-21. No script is in the CTO's tools. W2-142 S3 needs
  its first reading. It is already listed in DECIDED-NOT-DONE l.84 and START-NEXT-SESSION l.91.
- Scope: out (not in the 80's path).
- Ordinary work: no, because it is a CTO tool not yet due.
- Consequence: other.
- Classification: **ROW** (tracked already).

## Summary
- FIX BEFORE THE 80: none.
- Rows: 7 (F1 to F7). F1 to F4 ride one edit of the three briefs. F6 rides item 19's brief.

```verdict
{"kpis": [
 {"kpi": "A6.1 the three briefs carry search-again once as E2 measured it", "verdict": "pass", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "A6.2 W2-128's and W2-142's lines match the practice", "verdict": "pass", "findings": [
   {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "A6.3 the kernel retrieval skill does not contradict it", "verdict": "pass", "findings": []},
 {"kpi": "A6.4 every engineer brief carries the exclusion line (DEC-1093 (2))", "verdict": "pass", "findings": []},
 {"kpi": "A6.5 nothing tells agents to paste a glossary or use the prototype", "verdict": "pass", "findings": []},
 {"kpi": "A6.6 the briefs and the fresh 80's harness prompt match in substance", "verdict": "pass", "findings": [
   {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F7", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}
]}
```

**READY for the 80** (on this aspect): no finding is in scope, reachable in ordinary work, and fails open or would
make the verdict wrong.
