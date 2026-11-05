# The spent measurement set's 19 misses, by kind (DEC-1074 (2))

- **By:** an independent session acting in W2-61h's role (the hidden half's checker, `.tickets/DAEO-h2k3.md`), on the CTO's brief under the owner's order of 2026-11-05. Read-only apart from this file.
- **Date:** 2026-11-05.
- **What was read:** the 19 missed question files of `memory-verdict` named in the brief, and no other question of the set; the clone `~/gov-os-runs/D4B/g1/repo` at `e884675b465e`, with each gold span resolved by the measure's own `_span` and the store's chunk and parent tables (read-only); the kept outputs `~/gov-os-eval/runs/verdict/v-run1/` (each miss's first call and its later calls); the CTO's rows `stage1-verdict.json` and `stage2-verdict-depth1000.json`, for these ids; the route code (`retrieve.py`, `routing.py`, `fusion.py`, `lexical.py`, `semantic.py`); the earlier diagnosis's form and its K1-K8 kinds; the rubric's codes.
- **What was not read:** the other 41 questions; the tuning sets; `XCHECK.md`; the CTO's drafts other than the leak check. Nothing was run: no `gov`, no retrieval, no measure, no model, no GPU.
- **The hidden-half rule was kept:** ids, kinds, counts, tiers, ranks and general phrases only; no question text, gold answer, gold path, heading, line, fact, symbol or distinctive phrase, and no path of a competing chunk.
- **No label was judged.** Two ids carry "label doubt" with a rubric code; both are classified as they stand.

## How the run was read (a note on the pool)

The brief describes v456 as routes 60 deep and 40 fused candidates reranked in one pass. The kept outputs of `v-run1` show something else: every first call gathered and reranked a page of **20** (`merge.candidates` 20 in all 19 first calls), and the clone's code at `e884675b` cuts the meaning route to 30 after its phrasings are fused and gathers two batches of 10 at radius 0. The stage rows' "in the 20" matches the kept outputs literally. This report classifies the run as kept: "the pool" below is the first call's reranked page of 20, and `CUT` is "in the fused list, below the page". Whether `v-run1` is the v456 run is for the CTO to settle (see the return).

Stage rows checked against the kept outputs: every place in the page agrees. Two fused positions differ by 1 (m39) and 4 (m33) from the gap order in the kept output; no stage changes. Two ids fit two stage definitions; the stage rows' choice is kept: m33 is `CUT` (its "sibling" is a far chunk of a large module), m39 is `SECTION` (its gold also sits at fused 108).

## Per id

Route ranks are stage 2's (keyword / meaning, each route's phrasings fused, 1,000 deep; "parent" where the parent's rank is better). Tiers: governing (Charter, Contract, decision and architecture records), kernel (template skills, roles, schemas), middle (plans, tickets, packages, prompts, bootstrap and evidence records), reports (assessments, research, probes, audits), tests, code.

| Id | Stage | Main cause | Secondary causes | K-kinds | What outranked the gold in the first call (kind and tier) | Levers |
|---|---|---|---|---|---|---|
| m02 | LOW (place 6; the other alternative at 14) | RERANK | HOP, FORM, CROWDING | K6, K7, K4, K5 | Governing: the earlier decision record that the gold's record replaced, shown as in force, first; a neighbouring decision; an architecture-record section. Middle: a prompt section and a package section on the subject. No route had the gold in its own top 5 (13 / 12). | Stronger reranker: strong. Hop (from the replaced record to its replacement): weak. Answer-unit chunks: weak. |
| m03 | LOW (place 12) | RERANK | CROWDING, HOP | K6, K5, K4 | Governing: two related decision records, one that the gold's record builds on. Middle: a ticket and its plan card on the same subject. Reports: assessment sections, among them the proposal the gold's decision adopted, and a glossary entry. Keyword route only (13; meaning 155). | Stronger reranker: strong. Hop (from the adopted proposal to the decision): weak. |
| m05 | LOW (places 11 and 12) | RERANK | CROWDING, FORM | K5, K2, K4 | Kernel: the role file and a skill for the role the question names. Middle: a role specification package and a prompt template. Governing: an older decision on the same role. The gold's heading chunk and its decision chunk are split (11, 12). The meaning route had it at 7 (1 in one phrasing). | Stronger reranker: strong. Widening a gathered chunk to its section: weak. |
| m09 | CUT (fused 67) | VOCABULARY | FORM, CROWDING | K1, K7, K4, K5 | Middle: packages and a bootstrap record on neighbouring subjects that match the question's general words. The question paraphrases; the gold states it under a label with few shared words. Meaning route only (119; 60 in one phrasing); the second alternative is in no fused list. A later page put the gold at 7. | Stronger embedder: strong. Query phrasing or term mapping: strong. Deeper pool: weak. Stronger reranker: weak. |
| m12 | NEVER (keyword 158, meaning 124) | CROWDING | FORM | K5, K7, K4 | Governing: two decision records on the same subject, one of them later and changing the asked form for one class of case. Kernel: two skill sections. Governing: a Contract item. Middle: a prompt section. All restate the rule; the gold is one list item in a long section chunk. Label doubt: R1-INCOMPLETE. | Deeper pool: weak. Answer-unit chunks: weak. |
| m15 | LOW (place 7) | RERANK | FORM, CROWDING | K4, K7, K5 | Reports: two sections of a research report on the same subject. Middle: a prompt section and a plan card. Governing: two decision records on the same subject. The keyword route had the gold at 3. The gold is one long list item holding several rules. | Stronger reranker: strong. Answer-unit chunks: weak. |
| m18 | NEVER (keyword 131, meaning 424) | CROWDING | FORM, VOCABULARY (partial) | K5, K4, K7, K1 | Middle: package sections, a ticket and a triage row on neighbouring subjects sharing the question's words. Governing: decision records on neighbouring subjects. The gold is one sentence in a list item of several rules; the question's scenario words are not in it. | Answer-unit chunks: weak. Query phrasing: weak. Deeper pool: weak. |
| m20 | LOW (place 6) | CROWDING | FORM, RERANK | K5, K7, K2, K4 | Middle (plan tier): a report's table row that restates the asked line, first (an unlabelled restatement). Governing: an architecture-record section and a decision record. Kernel: a skill section. The gold's own heading chunk sits just below it (7). Meaning route only (11). | Stronger reranker: weak. Answer-unit chunks: weak. Widening to its section: weak. |
| m22 | LOW (place 7) | MULTI-PART | CROWDING, FORM | K8, K5, K7, K4 | Middle: the plan card of the same ticket (it answers the first half), a package, the list row the second half asks for, and the same ticket's title section. Governing: a decision on a neighbouring subject. Reports: a probe report's finding. Both routes had the gold high (keyword 6, meaning 4). The gold is one field in a front-matter chunk. | Query phrasing (splitting the two parts): strong. Stronger reranker: weak. Answer-unit chunks: weak. |
| m24 | LOW (place 12) | RERANK | CROWDING, FORM, OTHER (code-first routing) | K5, K7, K4 | Code: two chunks moved ahead by the code-first routing, which matched a word of the question to a symbol. Governing: a decision on a neighbouring subject. Middle: the plan card of the same ticket, its source package, and the same ticket's other sections. The meaning route had the gold at 2. | Stronger reranker: strong. Answer-unit chunks: weak. |
| m26 | LOW (place 11) | RERANK | CROWDING, FORM | K5, K7, K4 | Middle: the plan card and fields of other tickets on the same subject, a list row, and the same ticket's reason section (at 3, which names the ticket). Governing: a decision on the same subject. The meaning route had the gold at 1. The gold is one field in a front-matter chunk. | Stronger reranker: strong. Answer-unit chunks: weak. |
| m30 | LOW (place 6; the second piece never appears) | VOCABULARY | HOP, FORM | K1, K3, K6 | Kernel: a schema and a skill section. Middle: two chunks of a record on the subject. Governing: a Contract item. All match the subject's general words. The keyword route returned nothing at all for the question as typed; the meaning route had the first piece at 27. | Query phrasing or term mapping (splitting identifiers): strong. Hop (from the first piece to the second): weak. Stronger reranker: weak. Stronger embedder: weak. |
| m33 | CUT (fused 71) | FORM | CROWDING, OTHER (the code route did not answer for the named symbol) | K3, K4, K7, K5 | Code: other functions that use the asked symbol, and a neighbouring function of the same module. Governing: the decision on the same subject. The gold is one definition line in a chunk whose other lines are unrelated (keyword 97, meaning 55). A later page put it at 11. | Answer-unit chunks (definitions): strong. Deeper pool: weak. Term mapping (a symbol to its definition): weak. Stronger reranker: weak. |
| m37 | NEVER (keyword 400, meaning 878) | CROWDING | FORM, VOCABULARY (partial) | K5, K3, K4, K1 | Governing: the decision record that states the list, first. Code: the validator and another module that use it. Middle: the plan card and a plan line that restate the list, and a ticket. The gold is one definition among others in its chunk. Label doubt: R3-AMBIGUOUS. | Hop (from the decision to the code that cites it): strong. Answer-unit chunks: weak. Query phrasing: weak. |
| m39 | SECTION (siblings at 3 and 4; gold at fused 108) | FORM | CROWDING, HOP, OTHER (named-record routing) | K2, K3, K5 | Middle: the ticket the record route resolved, put first by the named-record routing, and an evidence file. Code: the same module's top chunks, which state the rules in summary (3, 4). Governing: the decision that states the rules (5), and other decisions. The answer is spread over three functions' chunks, none of which carries the question's words (parent ranks 14 / 13, chunk ranks 78 / 360). | Hop (from the decision on the page to the code citing it): strong. Widening to its section: weak. Answer-unit chunks: weak. Stronger reranker: weak. |
| m41 | NEVER (keyword 352, meaning 970) | VOCABULARY | CROWDING, FORM | K1, K3, K5 | Governing: decision records, and middle: packages, that match the question's role words. Tests: an acceptance README section. The code states the rule as a test on a role variable and never uses the question's role words. | Query phrasing or term mapping: strong. Stronger embedder: weak. |
| m42 | SECTION (module's top chunk at 11; gold in no fused list, meaning 1150) | VOCABULARY | HOP, CROWDING, OTHER (named-record routing) | K1, K3, K6, K5 | Middle: two chunks of the resolved ticket, first. Code: two neighbouring functions of the same module (3, 4), one of which calls the gold. Governing: decisions on the same command. Middle: a bootstrap record. The question asks in a user's scenario words; the code states the mechanism in its own terms. | Query phrasing or term mapping: strong. Stronger embedder: strong. Hop (a caller on the page): strong. |
| m43 | SECTION (module's top chunk at 4; gold in no fused list) | FORM | VOCABULARY, HOP, CROWDING, OTHER (named-record routing) | K3, K7, K1, K6, K5 | Middle: the resolved ticket, first; a bootstrap record; another ticket. Governing: decisions on the same subject. Code: the module's top chunk (4) and a function that calls the gold (5). The gold is two two-line functions whose meaning sits in identifiers the tokenizer keeps whole (keyword parent 43, meaning none in 1,000). | Hop (a caller on the page): strong. Term mapping (identifier tokenisation): strong. Widening to its section: weak. |
| m51 | LOW (pieces at 9 and 10) | MULTI-PART | CROWDING, FORM | K8, K5, K7, K4 | Code: the second piece's module top chunks (1, 4). Governing: a decision on a neighbouring subject. Middle: the plan card of the same ticket (it answers the first half), a prompt line, a list row. Each piece matches half the question (keyword 9 / meaning 6; the second piece's parent at meaning 4). | Query phrasing (splitting the two parts): strong. Stronger reranker: weak. Answer-unit chunks: weak. |

Kind notes, in general terms:
- **K4 / K7** here are mostly one list item, one front-matter field, one table row or one definition line inside a chunk that holds other things.
- **K6** here is an answer in a record that replaced or completes the one the question's words match (m02, m03), or in code that a gathered function calls (m42, m43), or split across two functions (m30).
- **K8** is a two-part question (m22, m51).
- **OTHER:** the routing steps moved chunks ahead of the reranked order in four first calls (code-first in m24; the named-record routing in m39, m42, m43); in m33 the code route gave nothing for a named symbol.

## Counts over the 19

### The owner's kinds

| Kind | Count | Ids |
|---|---|---|
| ranked below 5 | 10 | m02, m03, m05, m15, m20, m22, m24, m26, m33, m51 |
| vocabulary | 4 | m09, m30, m41, m42 |
| never retrieved | 3 | m12, m18, m37 |
| other | 2 | m39, m43 |

### Stages

| Stage | Count | Ids |
|---|---|---|
| LOW (in the page, below 5) | 10 | m02, m03, m05, m15, m20, m22, m24, m26, m30, m51 |
| NEVER | 4 | m12, m18, m37, m41 |
| SECTION | 3 | m39, m42, m43 |
| CUT | 2 | m09, m33 |

### Main causes

| Main cause | Count | Ids |
|---|---|---|
| RERANK | 6 | m02, m03, m05, m15, m24, m26 |
| VOCABULARY | 4 | m09, m30, m41, m42 |
| CROWDING | 4 | m12, m18, m20, m37 |
| FORM | 3 | m33, m39, m43 |
| MULTI-PART | 2 | m22, m51 |
| HOP | 0 | |
| OTHER | 0 | |

### Stage against main cause

| Stage | RERANK | VOCABULARY | CROWDING | FORM | MULTI-PART | Total |
|---|---|---|---|---|---|---|
| LOW | 6 | 1 | 1 | 0 | 2 | 10 |
| CUT | 0 | 1 | 0 | 1 | 0 | 2 |
| SECTION | 0 | 1 | 0 | 2 | 0 | 3 |
| NEVER | 0 | 1 | 3 | 0 | 0 | 4 |
| Total | 6 | 4 | 4 | 3 | 2 | 19 |

### K-kinds (an id counted once per kind)

| Kind | Count |
|---|---|
| K1 vocabulary | 7 (m09, m18, m30, m37, m41, m42, m43) |
| K2 split section | 3 (m05, m20, m39) |
| K3 code fragment | 7 (m30, m33, m37, m39, m41, m42, m43) |
| K4 diluted chunk | 14 (all but m30, m39, m41, m42, m43) |
| K5 crowded topic | 18 (all but m30) |
| K6 indirect | 5 (m02, m03, m30, m42, m43) |
| K7 form | 12 (m02, m09, m12, m15, m18, m20, m22, m24, m26, m33, m43, m51) |
| K8 two-part question | 2 (m22, m51) |

### Levers

| Lever | Strong | Weak | Either |
|---|---|---|---|
| A stronger reranker | 6 (m02, m03, m05, m15, m24, m26) | 7 (m09, m20, m22, m30, m33, m39, m51) | 13 |
| Query phrasing or term mapping | 7 (m09, m22, m30, m41, m42, m43, m51) | 3 (m18, m33, m37) | 10 |
| A hop | 4 (m37, m39, m42, m43) | 3 (m02, m03, m30) | 7 |
| A stronger embedder | 2 (m09, m42) | 2 (m30, m41) | 4 |
| Answer-unit chunks | 1 (m33) | 11 (m02, m12, m15, m18, m20, m22, m24, m26, m37, m39, m51) | 12 |
| Widening a gathered chunk to its section | 0 | 4 (m05, m20, m39, m43) | 4 |
| A deeper pool | 0 | 4 (m09, m12, m18, m33) | 4 |
| None of these | 0 | | |

### LOW and CUT: did a route's own top 5 hold the gold?

| | Count | Ids |
|---|---|---|
| Yes, a route's fused list (stage 2) | 4 | m15 (keyword), m22 (both), m24 (meaning), m26 (meaning) |
| Only one phrasing's list, not the route's fused list | 1 | m05 (meaning) |
| No | 7 | m02, m03, m09, m20, m30, m33, m51 |
| Total LOW and CUT | 12 | |

### Unlabelled answers in the first five (an observation, not a label judgement)

In 7 of the 19 first calls a chunk in the first five answers the question wholly or in part without being a labelled source: m12 and m37 (both carry a label doubt), m20, m22, m24, m26 and m39; m51's first five answer its first half only.

## What the misses have in common

Thirteen of the 19 reached the reranked page: ten as the gold itself below place 5, three as another chunk of its section. Four never entered the fused list and two were cut below the page. The same shape repeats. The answer is one item, field, row or line inside a chunk that holds other things (K4 14, K7 12). The subject is restated across tiers, so the first five fill with chunks on the same subject: the same ticket's plan card and other sections, decisions on the subject, kernel pages and reports (K5 18). Seven of the first fives already hold an unlabelled answer. Vocabulary is the main cause of four misses and a part of three more. Counted by strong reach, query phrasing or term mapping reaches the most (7), then a stronger reranker (6) and a hop (4). Counted by any reach, a stronger reranker reaches the most (13 of 19), then answer-unit chunks (12, almost all weak) and phrasing or term mapping (10). A reranker cannot reach the four that never entered the pool, and of the ten "ranked below 5", only six have RERANK as their main cause.
