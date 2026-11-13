# The visible half's 24 questions against the rubric (DEC-1068, the audit of the 48 questions, step 2)

- **Status:** DRAFT for the owner. **Every change below is a recommendation only.** No fixture was written; nothing
  changes until the owner decides (DEC-1068 (3)). A label changes only where it is wrong, never to fit a result.
- **Rubric:** `docs/research/memory-measure-audit/RUBRIC.md` (R1 to R10; reason codes from it).
- **Judged at:** `w2/integrate` `8284fb408bd4`, the working tree clean; the questions read from
  `fixtures/evaluation/memory-retrieval/visible/q01.yaml` to `q24.yaml`. Each source was resolved with the measure's
  own rule (`measure.py` `_span`) at the head, and each path placed with the head's path map.
- **Independence:** by a session independent of the retrieval work. No search was run and no measure record, search
  result, figure or per-question rank was read: not `docs/research/**` (other than this folder), not
  `retired/README.md`, not `~/gov-os-runs/**`, the D4B packages, drafts or reviews. Disclosed in section 6: two
  aggregate figures reached this session unasked.

## 1. Counts

| Item | Visible questions failing | Major | Minor | Which |
|---|---|---|---|---|
| R1 correct today, governing source | 8 | 3 | 5 | major Q04, Q07, Q14; minor Q02, Q10, Q11, Q12, Q23 |
| R2 searchable by meaning | **0** | | | any entry keyword-only: **0**; all entries keyword-only: **0** |
| R3 unambiguous, answerable | 1 | 1 | | Q14 |
| R4 what agents ask | 0 | | | (weakest: Q05, Q23) |
| R5 the set's spread | the set FAILS | | | the plan governs 0; failure or lesson memory 0; retrieval and the context packet are 10 of 24 (42 %) |
| R6 sources hold the answer at the head | 4 | 4 | | Q04, Q07, Q13, Q17 |
| R7 entries and alternatives | 2 | 2 | | Q03, Q14 |
| R8 never the evaluation's own documents | 0 | | | |
| R9 distinct | 1 | 1 | | Q04 (the same fact as Q09) |
| R10 label record and form | 2 | | 2 | Q04, Q09 (category) |

- **Pass every item:** 12 (Q01, Q05, Q06, Q08, Q15, Q16, Q18, Q19, Q20, Q21, Q22, Q24).
- **Fail an item with a major fault:** 6 (Q03, Q04, Q07, Q13, Q14, Q17).
- **Fail on minor faults only:** 6 (Q02, Q09, Q10, Q11, Q12, Q23). A minor fault changes no score: the gold answer's
  text is not scored, only its sources.

## 2. R2: each gold source in its namespace

Every alternative of every entry of the 24 lies in an embedded namespace at the head. No source is in a keyword-only
namespace (`tests`, `doc-records`, `orchestration-records`, `agent-settings`, `ci`, `kernel-vendored`,
`kernel-adapter-copies`, `fixtures`, `carried-code`) and none in neither index (`evaluation-sources`,
`evaluation-fixtures`). No question needs the keyword-question mark.

| Namespace (embedded) | Questions with a source there |
|---|---|
| `docs` (the register) | Q01, Q02, Q03, Q04, Q05, Q13, Q15, Q16, Q18, Q21 |
| `docs` (the Contract, the Charter, the plan) | Q04, Q07, Q08, Q09, Q19, Q20 |
| `tickets` | Q03, Q06, Q07, Q08, Q09, Q14, Q16 |
| `gov-source` | Q02, Q03, Q04, Q10, Q11, Q12, Q13, Q17, Q18, Q20, Q22, Q23, Q24 |
| `kernel-template` | Q18, Q19, Q20 |
| `project-overlay` | Q15, Q17 |

**R2 counts: any entry keyword-only 0 of 24; all entries keyword-only 0 of 24.**

## 3. R5: the set's spread (visible half)

| Governing domain | Questions | Count |
|---|---|---|
| Decisions (the register) | Q01, Q02, Q03, Q05, Q15, Q16, Q18, Q21 | 8 |
| Code | Q10, Q11, Q12, Q13, Q17, Q22, Q23, Q24 | 8 |
| Tickets | Q06, Q07, Q08, Q14 | 4 |
| The Contract and the Charter | Q04, Q09, Q19, Q20 | 4 |
| **The plan** | none: `docs/plan/WAVE_2_WBS.md` is only an alternative (Q07, Q08) | **0** |

- **Tags:** kernel template 3 (hooks Q18, Q20; roles Q19; no kernel skill anywhere); failure or lesson memory **0**;
  supersession questions with a superseded naive answer 4 (Q03, Q05, Q16, Q21).
- **Subject:** retrieval and the context packet are the subject of 10 of 24 (Q01, Q02, Q03, Q04, Q09, Q10, Q11,
  Q12, Q13, Q17), 11 with the measure's own code (Q22). Two facts are asked twice: DEC-782 (Q01, Q02: an id-form pair,
  allowed) and the packet's ~6k ceiling (Q04, Q09: a duplicate).
- **Verdict:** FAIL on R5-DOMAIN-THIN (the plan; failure memory) and R5-TOPIC-HEAVY (retrieval and context, 42 %
  against the proposed 25 %). Lens B's 20 are fixed by DEC-1009, so the remedy is in the hidden half's and any future
  questions, not in retiring visible ones (recommendation 8).

## 4. Per question

Format: each item PASS or FAIL with one sentence; R5 is set-level (section 3). Then the recommendation.

### Q01 `DEC-782` (decision)
- R1 PASS: DEC-782 is ACCEPTED with no later change; the gold answer restates its item 1.
- R2 PASS: the register (`docs`).
- R3 PASS: a bare id, read as "what does DEC-782 decide", which the gold answers.
- R4 PASS: any role meets decision ids in briefs and tickets and looks them up.
- R6 PASS: the `###` heading is found and spans the entry (8574 to 8592).
- R7 PASS: one entry, the governing entry.
- R8 PASS. R9 PASS: an id-form pair with Q02, allowed. R10 PASS.
- **Recommendation:** none. (Optional, minor: the gold answer could add that the cache key names the device today,
  per W2-54's KPI; DEC-782's own text does not, so it is not wrong.)

### Q02 `Which decision lets a read command write the query-vector cache?` (decision)
- R1 FAIL (minor, R1-DETAIL): the gold answer names `.gov-runtime/query-vectors.db`; at the head the file is
  `.gov-runtime/query-vector-cache.db` (`semantic.py` line 226).
- R2 PASS: the register and `src/`.
- R3 PASS. R4 PASS: an engineer touching the cache asks it.
- R6 PASS: both anchors found (the docstring line now at 24, spanning 24 to 28, holds "the one file a read writes
  (DEC-782)").
- R7 PASS: two places of one piece, alternatives. R8 PASS. R9 PASS (the pair with Q01). R10 PASS.
- **Recommendation:** re-label (gold answer only): the file name as the head has it, or no file name.

### Q03 `Where are query embeddings computed now, on which device, and why?` (decision)
- R1 PASS: DEC-1065 (1) is ACCEPTED and standing; every claim checked holds (the query host 127.0.0.1:11435 by
  default, GPU only, `EMBEDDER_ON_CPU`, `EMBEDDER_UNAVAILABLE`, the cache keyed by the device); DEC-1033's "any
  device" is named as replaced, not gold.
- R2 PASS: the register, the ticket and `src/`.
- R3 PASS: three asked facts, the most the rubric allows; "now" is clear because the gold names the decision.
- R4 PASS: an engineer or a lead working on the embedder asks it.
- R6 PASS: all four anchors found and hold their text.
- R7 FAIL (major, R7-PARTIAL-ALTERNATIVE): the one entry's four alternatives do not each hold the whole answer:
  W2-32's S10 line states neither where (the query daemon and its host) nor why; DEC-1065's entry states no host;
  so a hit on one of them is scored as full evidence for an answer it cannot give.
- R8 PASS. R9 PASS. R10 PASS, with a note: this second re-label (`a9ef6f82`) was by the CTO's order in DEC-1067
  (c)'s form, while DEC-1067 (c) itself named Q16 and Q19; the retired copy is kept. The owner may wish to confirm it.
- **Recommendation:** re-label (structure, same question and gold): two entries. (1) Where: `ollama.py` 3 to 17 or
  `semantic.py` 12 to 18. (2) The device and why: DEC-1065's entry or `semantic.py` 12 to 18; S10's line only if
  it is judged to hold the device part alone, as a third entry or not at all. Confidence medium: it changes Q03's
  full-evidence scoring, not its hit@5.

### Q04 `What is the token ceiling of a context packet?` (decision)
- R1 FAIL (major, R1-NOT-GOVERNING): DEC-004 is PROPOSED (settled by DEC-086, which does not state the size) yet is
  a gold alternative; Q09's own re-label left it out for that reason.
- R2 PASS: the Contract, the register, `src/`.
- R3 PASS. R4 PASS: a lead or engineer working on `gov context` asks it.
- R6 FAIL (major, R6-NO-ANSWER): CAP-15.g's record (11 to 16) states only "File path + summary ≤ ~2.5k tokens", not
  the ceiling; and `retrieve.py`'s `BUNDLE_BUDGET` is the retrieval bundle's budget, another limit whose comment only
  borrows DEC-004's number.
- R7 PASS: the rest are places of one piece.
- R8 PASS. R9 FAIL (R9-DUPLICATE, Q09): the same fact with the same governing source (CAP-15, the Contract's
  envelope); Q04 is the weaker label of the two.
- R10 FAIL (minor, R10-CATEGORY): `decision`, while the governing source is the Contract.
- **Recommendation:** re-label: keep CAP-15 in `CONTRACT_v4.md`, `CAP-15.md` and `context/__init__.py`'s
  `DEFAULT_BUDGET`; add CAP-15 in `contract.yaml` (962 to 969); drop DEC-004, `CAP-15.g.md` and `retrieve.py`'s
  `BUNDLE_BUDGET`; category `contract`. For the duplicate, three options for the owner: (a) keep both as they are
  after the re-label (no cost; one fact weighs twice); (b) re-word Q04 to a distinct fact, as DEC-1060 rewrote q03,
  for example the packet's summary cap (~2.5k: CAP-15, CAP-15.g, `BRIEF_LIMIT = 2500`); (c) retire Q04 (breaks
  DEC-1009's "lens B's 20 exactly"). Recommended: re-label now and (a), with (b) if the owner wants distinct facts.
  Confidence high on the re-label, medium on the option.

### Q05 `How is the old repository archived, and which decision is in force?` (decision)
- R1 PASS: DEC-051 is ACCEPTED and supersedes DEC-048, which superseded DEC-038; the superseded ones are the naive
  answer, not gold.
- R2 PASS. R3 PASS: two asked facts, both in DEC-051.
- R4 PASS (the weakest of the set): an engineer or auditor who meets the pre-restructure code or looks for an
  `archive/` folder asks it; a Wave 2 task rarely does.
- R6 PASS. R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none.

### Q06 `What are W2-54's sources and allowed paths?` (ticket)
- R1 PASS: the 5 sources and the 11 allowed paths are as the head's front matter lists them.
- R2 PASS: `.tickets/`. R3 PASS. R4 PASS: a lead or engineer on W2-54 asks it.
- R6 PASS: both anchors found and span their lists exactly. R7 PASS: two pieces, two entries.
- R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none.

### Q07 `Which tickets must be done before the Track A gate run?` (ticket)
- R1 FAIL (major, R1-WRONG): the gold answer lists 27 tickets "from DAEO-g0ip to DAEO-7rr2"; at the head
  `DAEO-0mab`'s `depends_on` holds 23, from DAEO-g0ip to DAEO-2bdu (DEC-954's change, `d7d41d6e`: nine moved out,
  five new ones in).
- R2 PASS: `.tickets/` and the plan. R3 PASS. R4 PASS: the orchestrator plans the gate from it.
- R6 FAIL (major, R6-SPAN-OVERRUNS): the span 17 to 44 now runs past the list (17 to 40) into `allowed_paths` and
  the KPIs.
- R7 PASS: the list in one place, the WBS row's statement in the other, alternatives of one piece.
- R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** re-label: the gold answer to the head's 23 (DAEO-g0ip, zflj, ym8a, u4oz, 0z8c, kia7, r9ss,
  7r5e, k7hz, zqvn, rd0g, 49o5, r30l, 1ahb, kmcr, ha8z, kl5e, 7rr2, cy5o, siiz, wnnz, egsy, 2bdu), and re-anchor the
  ticket's alternative to lines [17, 40]. Confidence high.

### Q08 `Which ticket builds the commit-time re-index?` (ownership)
- R1 PASS: W2-06 (DAEO-kia7), title as stated; W2-13's ticket confirms the re-index is W2-06's.
- R2 PASS. R3 PASS. R4 PASS: a lead finds which ticket owns a piece of work.
- R6 PASS: all three anchors found (the WBS row now at 132, the card at 356). R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none.

### Q09 `How large may the context packet be?` (ticket)
- R1 PASS: the Contract's envelope (`contract.yaml` `token_budget`) and CAP-15 state ~6k; DEC-004 is rightly left
  out; W2-04's KPI lines restate it.
- R2 PASS. R3 PASS. R4 PASS.
- R6 PASS: every anchor found and holds "~6k".
- R7 PASS, with a note: the Contract's alternatives hold the size the question asks, not the refusal over the ceiling
  that the gold answer adds from the ticket; the asked fact is held by each.
- R8 PASS. R9 PASS (Q04 is the one marked). R10 FAIL (minor, R10-CATEGORY): `ticket`, while the governing source is
  the Contract.
- **Recommendation:** re-label (category `contract`); optionally trim the gold answer to the size asked.

### Q10 `Who calls indexable?` (callers)
- R1 FAIL (minor, R1-DETAIL): the gold answer says `lexical.py` line 115 and `codeintel/__init__.py` line 185; at the
  head the calls are at 270 and 188. The two callers are complete (no third caller in `src/` or `template/`).
- R2 PASS: `src/`. R3 PASS. R4 PASS: an engineer changing `indexable` asks for its callers (DEC-859 sends it to the
  code graph first; `gov retrieve`'s code route answers it too).
- R6 PASS: both headings found. R7 PASS: two callers, two entries. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** re-label (gold answer only): drop the line numbers (the sources carry them) or give the head's.

### Q11 `Who calls rrf?` (callers)
- R1 FAIL (minor, R1-DETAIL): the gold answer's lines (62, 135) are now 80 and 283, and `retrieve` fuses the code
  route too when the question names a symbol (W2-92); the two callers are complete.
- R2 PASS. R3 PASS. R4 PASS.
- R6 PASS: both headings found (`fusion.py` 80 inside `search`, `retrieve.py` 283 inside `retrieve`). R7 PASS.
- R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** re-label (gold answer only): no line numbers; "the lexical, semantic and closure routes, and the
  code route when the question names a symbol".

### Q12 `CONTINUATION_INVALID` (code location)
- R1 FAIL (minor, R1-INCOMPLETE): the three cases hold, but the head adds two more raised for the same token, a
  malformed list of expanded parents or of spans sent alone (`_expanded_of`, `_alone_of`, `retrieve.py` 116 to 134,
  called from `_decode_continuation`; W2-32 S7, DEC-1067).
- R2 PASS. R3 PASS: a bare error code, read as "where and when is it raised". R4 PASS: an agent pastes the error it
  met.
- R6 PASS: the heading is found and spans the function (162 to 181), its calls to the two helpers included.
- R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** re-label (gold answer only): add the two cases. Adding the helpers as a second entry is the
  owner's choice (it would make full evidence stricter); not recommended.

### Q13 `Where is the bundle budget enforced?` (code location)
- R1 PASS: the expansion is kept only while `used + cost <= limit`, the limit `--bundle-budget` or `BUNDLE_BUDGET`
  (6000); DEC-419's DP-3 is ACCEPTED.
- R2 PASS. R3 PASS. R4 PASS.
- R6 FAIL (major, R6-SPAN-MISSES): entry 1's heading is found at 411 and, at the stated 13 lines, spans 411 to 423,
  ending before the deciding check at line 431; entry 2's `retrieve` alternative spans 214 to 220, ending before the
  line that takes the limit (221).
- R7 PASS. R8 PASS. R9 PASS (it shares the 6000 with Q04 but asks another fact). R10 PASS.
- **Recommendation:** re-anchor: entry 1 lines [411, 431] (the same heading); entry 2's `retrieve` alternative lines
  [214, 221]. Confidence high.

### Q14 `Which tickets depend on W2-03?` (ticket)
- R1 FAIL (major, R1-WRONG): the gold answer says nine; at the head 13 tickets list DAEO-ym8a in `depends_on`: the
  nine plus DAEO-2bdu (W2-88), DAEO-arrl (W2-55), DAEO-n0wb (W2-92) and DAEO-s9qc (W2-87, closed).
- R2 PASS. R4 PASS: a lead or the orchestrator checks what a ticket's change can hold up.
- R3 FAIL (R3-AMBIGUOUS): "depend on" can also be read as tk's `deps`, under which DAEO-2d6f (a child of W2-03, no
  `depends_on`) also depends on it.
- R6 PASS: the nine anchors resolve to the `depends_on` lines.
- R7 FAIL (major, R7-MISSING-PIECE): four members of the list have no entry, so full evidence is scored without them.
- R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** re-label: 13 entries, the four new ones anchored on `.tickets/DAEO-2bdu.md` and
  `.tickets/DAEO-s9qc.md` heading `- DAEO-ym8a` (line 18), `.tickets/DAEO-arrl.md` heading
  `depends_on: [DAEO-ym8a]` (17) and `.tickets/DAEO-n0wb.md` heading `depends_on: [DAEO-s9qc, DAEO-ym8a]` (17); the
  gold answer to say "in depends_on" and to name DAEO-2d6f as a tk-only dependency outside it. A re-word to "list W2-03
  in depends_on" would settle R3 too. Note: this answer grows each time a ticket is filed; it needs a re-check at
  every measure. Confidence high on the 13.

### Q15 `What two lines must every audit finding carry?` (decision)
- R1 PASS: DEC-808 item 4 is ACCEPTED; `JUDGEMENT.md` still carries both lines and "a row, never a round".
- R2 PASS. R3 PASS. R4 PASS: every auditor and reviewer writes them.
- R6 PASS. R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none.

### Q16 `How much free memory must the resource gate see before it launches a new lead?` (decision)
- R1 PASS: DEC-961 item 1 (ACCEPTED, standing) and DEC-947 item 5's floor (kept by DEC-961) hold at the head;
  later entries change DEC-961 only for the nightly's slots (DEC-984); DEC-798 is named as superseded, not gold.
- R2 PASS. R4 PASS: the orchestrator's launch rule.
- R3 PASS, with a note: the question presupposes a figure and the gold answer corrects it ("no fixed figure"), which
  its sources state; the gate is lifted for this repository's own development (DEC-953) but stays the product's.
- R6 PASS: both list-item headings found (12039, 11726). R7 PASS: the rule and the floor, two entries.
- R8 PASS. R9 PASS. R10 PASS (DEC-1067 (c), the retired copy kept; the rewording kept by DEC-1068 (d)).
- **Recommendation:** none (the owner kept it, DEC-1068 (d)).

### Q17 `Which paths are embedded for semantic search?` (code location)
- R1 PASS: `_wanted`'s rule holds; its new hold-out of `fixtures/memory-quality` (W2-32 S3) changes nothing today,
  as the path map already keeps that folder out.
- R2 PASS. R3 PASS. R4 PASS: an engineer or test designer asks why a file is not found by meaning.
- R6 FAIL (major, R6-SPAN-MISSES): the path map's `namespaces:` anchor spans the stated 130 lines, 6 to 135, while
  the block now runs 6 to 287; half the namespaces (kernel template, `src/`, tests, fixtures, the evaluation ones)
  fall outside it.
- R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** re-anchor: the path map's entry lines [6, 287]. Confidence high.

### Q18 `Where does the PreCompact hook write its automatic checkpoint?` (policy)
- R1 PASS: DEC-444 ACCEPTED; `record.py` writes an automatic record under `.gov-runtime/scratch/checkpoints/`
  as `CP-<ticket>-<number>.md`; the hook calls it with `dest="automatic"`.
- R2 PASS: the register, `src/`, the kernel hooks. R3 PASS. R4 PASS.
- R6 PASS. R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none.

### Q19 `May an engineer write acceptance tests?` (policy)
- R1 PASS: MR-3 in the Charter and the Contract; the role files state the guard's refusal.
- R2 PASS. R3 PASS. R4 PASS: an engineer asks it as it starts a ticket.
- R6 PASS. R7 PASS: every alternative states the "no". R8 PASS. R9 PASS.
- R10 PASS (DEC-1067 (c), the retired copy kept).
- **Recommendation:** none.

### Q20 `How does a session resume after compaction?` (policy)
- R1 PASS: CAP-37 and the SessionStart hook's docstring at the head (the critical and optional parts within the cap)
  match the gold answer.
- R2 PASS. R3 PASS. R4 PASS: a lead or the orchestrator after a compaction.
- R6 PASS (CAP-37 found at 574, `brief` at 155). R7 PASS: the rule and the mechanism. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none.

### Q21 `What compaction threshold is set for a session's context window?` (decision)
- R1 PASS: DEC-838 ACCEPTED and standing; the 300k entries are marked superseded by it (DEC-865, DEC-866).
- R2 PASS. R3 PASS. R4 PASS: the lead brief states the rule, and a lead asks it.
- R6 PASS. R7 PASS. R8 PASS. R9 PASS: Q20 asks how to resume, another fact.
- R10 PASS, with a note: like q22 to q24 it has no `id` field, so its id is the file's stem `q21`, while lens B's
  are `Q01` to `Q20`.
- **Recommendation:** none (optional: `id: Q21` to `Q24` for one form).

### Q22 `Which functions call set_fault?` (callers)
- R1 PASS: `check_sets` and `_hidden` in `reads.py` (465, 483) and `measure` in `measure.py` (247): complete and at
  those lines today.
- R2 PASS. R3 PASS. R4 PASS.
- R6 PASS, advisory (R6-LINES-ONLY): the two `reads.py` entries are lines only (their call lines are identical, so a
  heading would find the first); the next edit above them breaks them silently. A heading on each `def` line with a
  span to the call would hold.
- R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none required; re-anchor on the `def` lines when it is next touched.

### Q23 `Which constant in the close's test selection holds the test map's path, and what is its exact value?` (exact-string)
- R1 FAIL (minor, R1-DETAIL): the gold answer says line 26; at the head `MAP_REL` is at line 27 (value unchanged).
- R2 PASS. R3 PASS.
- R4 PASS (weak): the natural form is "where does the close read the test map from?"; naming "constant" points at the
  answer's form but not its text.
- R6 PASS: the heading is found. R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** re-label (gold answer only): drop the line number.

### Q24 `By default, how long may a store rebuild run before it counts as slow, and how often is its record rewritten after that?` (code-paraphrase)
- R1 PASS: `SLOW_AFTER_S = 1800`, `EVERY_S = 30.0`; this tree's `rebuild.yaml` sets no `slow_after_s`.
- R2 PASS. R3 PASS: two asked facts, two entries. R4 PASS: anyone waiting on a rebuild.
- R6 PASS: lines-only docstring alternatives each have a heading alternative beside them.
- R7 PASS. R8 PASS. R9 PASS. R10 PASS.
- **Recommendation:** none.

## 5. Top recommended changes (for the owner; nothing changed)

1. **Q14, re-label** (major, high): 13 dependents at the head, not nine; four entries added; "in depends_on" stated.
2. **Q07, re-label and re-anchor** (major, high): 23 tickets, not 27; the span to lines 17 to 40.
3. **Q04, re-label** (major, high): drop DEC-004 (PROPOSED), `CAP-15.g.md` (no ceiling in it) and `retrieve.py`'s
   `BUNDLE_BUDGET` (another budget); add `contract.yaml`'s CAP-15; then the owner's choice on the duplicate with Q09
   (recommended (a): keep both; (b) re-word Q04 to the summary cap).
4. **Q13 and Q17, re-anchor** (major, high): spans that now miss the deciding line (Q13) or half the block (Q17).
5. **Q03, re-label its structure** (major, medium): two entries (where; the device and why), since no single
   alternative holds all three asked facts.
6. **Gold-answer re-words with no scoring effect** (minor, high): Q02's file name; Q10, Q11 and Q23's line numbers
   (drop them: the sources carry the lines); Q11's code route; Q12's two new cases.
7. **Categories** (minor): Q04 and Q09 to `contract`; optionally `id: Q21` to `Q24`.
8. **The set's spread** (R5, for the owner and for W2-61h's hidden half and any future question): the plan governs
   none of the visible 24, failure or lesson memory none, no kernel skill is asked, and retrieval and the context
   packet are 42 % of them. Lens B's 20 stay (DEC-1009); the balance has to come from the other half or from new
   questions.
9. **A standing re-check** (process): Q07, Q14 and every line anchor move with ordinary work (tickets filed, code
   above an anchor edited); a resolve-at-head check of every source before each measure, as done here with the
   measure's own `_span` rule, would catch them before a run rather than after.

## 6. Notes

- **Figures seen unasked:** two aggregate figures reached this session without being looked for: the recent commit
  subjects in the session's opening context, and the header comment of `governance/project/rebuild.yaml` (read to
  check Q24's setting), which states an aggregate of the measure. Neither names a question or a rank; no finding
  above uses them. That comment sits in an embedded namespace (`project-overlay`), so any search can return it.
- **The measure does not read a source's own `commit`** (Q10, Q11, Q12 carry one): every anchor is judged at the
  measured root, which is why this audit judged at the head.
- **Retired labels on record:** `retired/q03-lens-b.yaml`, `q03-pre-dec1067.yaml`, `q09-lens-b.yaml`,
  `q16-pre-dec1067.yaml`, `q19-pre-dec1067.yaml` exist; the re-anchors of Q10, Q11 and Q12 are in git history
  (`ba08ca77`, `320b98f3`, `bc1219c1`), as the rubric allows for a re-anchor. `retired/README.md` was not read: it
  holds past results.
