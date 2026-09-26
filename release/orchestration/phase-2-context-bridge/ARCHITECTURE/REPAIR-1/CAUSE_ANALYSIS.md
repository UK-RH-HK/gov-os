# REPAIR-1: cause analysis of the run-1 demonstration failure (BR-AR-0016)

| Field | Value |
|---|---|
| Run | BR-AR-0016, fresh failure analyst (brief `HANDOFFS/BR-HO-0016-failure-analyst.md`) |
| Subject | run-1 (`DEMONSTRATION/run-1/`, answers of BR-AR-0011), graded `DEMONSTRATION_FAIL` by BR-AR-0012 (G4, G5, G6, G7, G8 failed) |
| Inputs | quarantined grade and unsealed oracle (read only via `git show bridge/grade-0012:…`); run-1 packet, answers, receipt, the 104 saved query outputs; bridge code at the frozen tip `94d0211` (unchanged in `govbridge/**` and `config/**` up to this branch's base); a byte-identical read-only **copy** of `store-BR-AR-0010` |
| Oracle rule | This file holds no oracle content. Failed items are named only by grade-report keys (`G5.S2-QC7.R3` = the 3rd required item of that query; `G4.R8-CHAIN-F3.tests.M2` = must_state fact M2 of that stage; `G4.….D` = that stage's missing anchor). Anchor locators, expected facts and per-query expected items stay out of every committed file; `evidence/tools/oracle_overlap_selfcheck.py` checks this. |
| Class vocabulary | `GRADER_DEFECT`, `ORACLE_STRICTNESS`, `AGENT_BEHAVIOUR`, `BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE` (short: BRIDGE-R), `BRIDGE_NOT_RETRIEVABLE` (short: BRIDGE-NR), exactly one per item |

## 0. Result on one screen

**129 failed gate items**, every one classified by measurement:

| Class | Items | Share |
|---|---:|---:|
| BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE | 55 | 43% |
| AGENT_BEHAVIOUR | 53 | 41% |
| GRADER_DEFECT | 13 | 10% |
| ORACLE_STRICTNESS | 7 | 5% |
| BRIDGE_NOT_RETRIEVABLE | 1 | 1% |

The 129 are 83 missing anchors (G4, G5, G6, G8), 43 missing must_state facts, and the 3 G7 conditions. Five more
failed items belong to the ungated AUTH queries (§3.6) and are reported separately.

What the numbers say:

1. **The index was not the problem. Delivery and retrieval strategy were.** 88 of the 89 measured anchor rows are
   indexed in the demonstration store. Only one required item is not retrievable at all: it sits at a historical
   commit that the store does not hold. Every other bridge-caused miss was retrievable. The bridge did not put it in
   the packet: it cut the document, never ran the query, dropped the item by budget, or never followed up an
   identifier it had already surfaced.
2. **The agent's misses are real, but the bridge induced most of them.** 19 anchors were in the agent's own query
   outputs, and 11 more were in the packet. The agent did not cite them. 23 facts were in hand and not
   stated, 11 of them because they were stated in another answer. The agent grepped for test names because the packet
   carried no tests facet: all 37 TESTS-edge candidates were dropped by budget. No tool helped it turn a
   name into a citation.
3. **Neither side alone recovers the gate** (§5). Suppose the grader, the oracle and the agent were all perfect.
   G5 still reaches only 6/10 classes, because QC3, QC8, QC9 and QC10 remain, and QC9 must pass for all three
   subjects. Fixing only the bridge reaches 2/10. The controls fail almost entirely on the bridge: 8 of their 11
   items are BRIDGE-R. The G8 failure is therefore generic, not a sign of a Review-8-shaped bridge.
4. **Nine generic root causes explain the bridge side** (§6, RC-1…RC-9). RC-10 covers the grader and RC-11 the
   answer side. The largest is that section A was silently truncated.
   15 of the 20 mandatory items were cut at 4,000 characters with no marker: 384,595 source bytes were rendered as
   61,107. The resolver also ignored three declared sub-selectors (an entry range, a key list, a second path).
   The next largest cause is that the compiler never executed 30 of the 41 public queries, because a templated
   query has no `text`.

## 1. Method: what was run

All commands are in `AGENT_RUNS/BR-AR-0016.checkpoint.yaml`, and their outputs are under `evidence/`. The measuring
tools are in `evidence/tools/`. They carry no oracle content. Two of them read the quarantined oracle at runtime and
print keys only.

1. **Store safety.** The demonstration store was hashed before and after, and was unchanged (`01`, `10`). Every
   query ran against a byte-identical copy (`02`). Telemetry was later redirected to a scratch `GOV_BRIDGE_HOME`.
   There is one disclosed side effect. Before that redirection, the analyst's first two exploratory recompiles
   appended 26 query-telemetry rows (query hash, k, hit count, latency) to the shared
   `$HOME/.cache/gov-bridge/telemetry/queries.jsonl`, between 2026-09-26T00:41:42Z and 00:45:27Z. That file is not
   the store, and the rows were not reverted, because no shared file is edited or removed.
2. **Exact reproduction of the run-1 compile.** The committed view follows the bridge tip, which has moved since
   run-1, so `make_pinned_task.py` pins the records ref to `94d0211`. `recompile_capture.py` then re-runs
   `compile_packet` and captures every candidate before and after budget. The result reproduces all 424 packet items
   in all 13 sections, with identical item ids and content hashes (`04`, `05`). This makes the pre-budget candidate
   set and the budget drops measurable, although the manifest keeps only a compact drop summary.
3. **Packet, compile and output facts, oracle-free** (`packet_facts.py`, `06`). This covers: section A rendered
   bytes against source bytes; declared selectors; rendered bytes per section; delivered content bytes per route;
   which public queries were compiled; G and H candidates by tier, route, type, resolution label and fate; caller
   fan-out against the profile cap; a decomposition of the saved query outputs; state-record addressability; and the
   compile call sites that do not pass exclusions.
4. **Exclusion probe (OBS-BR-08)** (`exclusion_probe.py`, `07`). The routes were run for the 11 text-bearing public
   queries exactly as `govbridge search` runs them, then again with the task's exclusions.
5. **Per-item measurement** (`measure_anchors.py`, `08`). For each missed required item, the tool measures:
   * whether a post-budget packet item would have matched it, whether its content was rendered, and in which section;
   * whether its document is in A but cut before it;
   * whether it was a compile candidate, and whether it was dropped by budget;
   * whether its content or definition line appears in the agent's saved outputs;
   * whether another answer cites it;
   * whether this answer cites its whole document (GD-8) or lines inside its symbol (GD-10);
   * store coverage: blob, chunk, vector, code symbol and record id;
   * a lexical and a semantic rank up to 200 for the query's own text (a class×subject query is instantiated as
     "<class question> Subject: <subject>");
   * its rank inside its own document;
   * one code hop from any symbol the compile surfaced;
   * whether its identifier or path was already discovered in the packet or outputs;
   * whether it lies inside a by-reference mandatory directory.

   The anchor locators go to a private file in scratch, which is not committed.
6. **Aggregation** (`aggregate.py`, `09`). Class counts, per-gate, per-class and per-control tallies, and the
   counterfactual recall table (§5).
7. **must_state facts** (`evidence/must_state_classes.yaml`). Each of the 44 facts was classified from:
   * the grader's own per-fact note (`elsewhere_in_chain`, or "stated in X, not in this answer");
   * a presence check of the establishing content in the rendered packet, the agent's outputs and the answers;
   * the anchor measurement for the same query or stage.

   The presence-check tokens are derived from the oracle and were kept private. The committed table carries keys and
   classes only.

## 2. Classification rules

### 2.1 Missing anchors: deterministic, `measure_anchors.classify()`

These rules are applied in order, and the first match decides:

| Order | Condition | Class / cause code |
|---|---|---|
| 1 | this answer cites the anchor's whole document (whole-document vs sectioned anchor, undefined in §4) | GRADER_DEFECT / `GD-8` |
| 2 | this answer cites lines inside the anchor's symbol body, and the matcher ignores enclosing symbols | GRADER_DEFECT / `GD-10` (new) |
| 3 | a post-budget packet item would match it, or its content was rendered in the packet | AGENT_BEHAVIOUR / `A-PACKET-NOT-CITED` |
| 4 | its content, or its code or test definition line, is in the agent's own saved outputs | AGENT_BEHAVIOUR / `A-OUTPUT-NOT-CITED` |
| 5 | another answer cites it with substantive overlap | AGENT_BEHAVIOUR / `A-CITED-ELSEWHERE` |
| 6 | indexed, with at least one bridge signal; primary chosen in this order: `B-BUDGET-DROP` (compiled, then dropped) > `B-TRUNCATED-MANDATORY` (its document is in A, cut before it) > `B-BYREF-DIR-UNEXPANDED` > `B-QUERY-NOT-RUN` (query never compiled; rank ≤ 100 for its text) > `B-FOLLOWUP-ID` (identifier or path already discovered, resolvable by id or path) > `B-FOLLOWUP-CALLERS` (one code hop) > `B-TOPK` (compiled at k = 8; rank 9–100) > `B-SCOPED-SECTION` (top 5 in a document already named in the packet) | BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE |
| 7 | otherwise: not indexed, or no route reaches it | BRIDGE_NOT_RETRIEVABLE / `N-NOT-INDEXED` or `N-NO-ROUTE` |

"Evidence possession" (rules 3 to 5) requires real line overlap: at least `min(3, anchor length)` shared lines. It
is not the grader's ±3 tolerance. A tolerance-edge overlap therefore does not count as the agent "having" the item.
Metadata-only graph edges from `history`, `why` and `impact` count as pointers, not possession.

Every item also records **all** of its bridge signals, not only the primary one. The table in §7 shows them.

### 2.2 Missing must_state facts: basis codes

| Code | Meaning | Class |
|---|---|---|
| `MS-STAGE-PLACEMENT` | stated in another stage's claim of the same chain answer (grader: `elsewhere_in_chain`); the public query does not fix stage boundaries, and the oracle binds the fact to one stage | ORACLE_STRICTNESS |
| `MS-CROSS-ANSWER` | stated in another answer of the run, not in this one | AGENT_BEHAVIOUR |
| `MS-IN-HAND-NOT-STATED` | the establishing content was in the rendered packet or in the agent's own outputs | AGENT_BEHAVIOUR |
| `MS-TRUNCATED-MANDATORY` | the establishing content lies in a mandatory input past its rendered cut, and was not otherwise fetched | BRIDGE-R |
| `MS-NOT-RETRIEVED-FOLLOWUP` | the source was not delivered, but its identifier was already in hand | BRIDGE-R |
| `MS-VERSION-RECONCILIATION` | needs per-path blob identity across the view's refs; the store holds it (`occurrence` rows per ref), and no facet surfaces it | BRIDGE-R |
| `MS-DEPENDENCY-DATA` | needs a data or config file that the enforcing code reads; the code-to-data dependency is not an edge, and the agent asserted an unverified instance instead | BRIDGE-R |
| `MS-TESTS-BODY` | needs a test body; the tests facet delivered no bodies | BRIDGE-R |
| `MS-IMPACT-CONSUMERS` | needs the consumer set; the candidates were compiled, then budget-dropped or cut by the fan-out cap | BRIDGE-R |

## 3. Per gate

### 3.1 G4: chain reconstruction (19 items)

Both chains reached the real enforcement point with no trap or wrong anchor. That part of the bridge's purpose
worked. The chains fail on stage content:

* **The two missing stage anchors.**
  * `G4.R8-CHAIN-F3.tests.D` is AGENT. Two acceptable alternatives were in the agent's own grep output, and it named
    them without citing them. The third alternative was BRIDGE-R.
  * `G4.R8-CHAIN-F3.prior_findings.D` is GRADER (GD-8). The answer cites a document that contains an acceptable
    section anchor, at whole-document granularity. Three other alternatives were packet items it did not cite.
* **17 missing facts.**
  * **7 ORACLE_STRICTNESS**, all stage placement: the fact is in the chain answer, but in a neighbouring stage.
  * **5 AGENT**: facts from the review return that the agent itself had fetched, and facts it stated in the other
    chain.
  * **5 BRIDGE-R**:
    * two need a passage of a mandatory input past its 4,000-character cut;
    * two need a config-data dependency of the enforcing code;
    * one needs a test body.
* The grader's chain-level sensitivity still fails both chains. The stage-placement items are therefore not
  verdict-determining. The design must still settle them (decision D-2 in the plan).

### 3.2 G5: query classes (95 items; 1 of 10 classes pass)

| Class | Items | GRADER | AGENT | BRIDGE-R | BRIDGE-NR | Dominant cause, measured |
|---|---:|---:|---:|---:|---:|---|
| QC1 why (class passes) | 4 | 1 | 1 | 2 | 0 | the class query was never compiled |
| QC2 requirement | 4 | 0 | 1 | 3 | 0 | contract sections past the cut; a code-comment citation of a contract line is not an edge |
| QC3 decisions | 10 | 0 | 4 | 6 | 0 | decision ids already discovered, never followed up; class query not compiled |
| QC4 depends on | 5 | 0 | 4 | 1 | 0 | agent: packet pointers not cited; bridge: a data file read by code, not linked |
| QC5 depended on by | 9 | 0 | 5 | 4 | 0 | consumers compiled, then budget-dropped; caller fan-out cap with no continuation |
| QC6 failed approaches | 8 | 2 | 4 | 2 | 0 | GD-8; records past A's cut; ids not followed |
| QC7 tests | 13 | 0 | 12 | 1 | 0 | tests named from the agent's own grep output and never cited; the packet held no test facet (0 of 37 TESTS edges kept) |
| QC8 stale evidence | 18 | 4 | 4 | 10 | 0 | members of a by-reference mandatory directory were never expanded; records past A's cut; GD-8 |
| QC9 current vs superseded | 13 | 1 | 3 | 9 | 0 | records past A's cut, and not addressable by id; no version-reconciliation facet |
| QC10 deletable | 11 | 0 | 7 | 3 | 1 | agent did not cite packet items it had; one item at a commit outside the view, not indexed |

Across the 70 missing class-query anchors, the instantiated query text finds only 7 lexically and 5 semantically in
the top 8. 34 are within the top 100. So running the 30 class queries once at k = 8 would **not** have been enough.
Facet recipes and identifier follow-up are needed, as OD-BR-05 §1–§3 require.

### 3.3 G6: F1 evidence both ways (1 item)

`G6.R8-F1-BOTHWAYS.C4` is AGENT (`A-OUTPUT-NOT-CITED`). The consumer is named in the answer text, and its definition
line is in the agent's own grep output, but it is never cited. There is a bridge contributing factor: no test
consumer reached the packet, and no tool turns a named test into a citation. GD-2 (the tool graded the wrong answer)
does not change this outcome.

### 3.4 G7: no whole-repository dumping (3 items)

| Key | Class | Measured |
|---|---|---|
| `G7.packet_bytes` | BRIDGE-R (`B-NO-SUPPLEMENTARY-PACKETS`) | `packet.md` is 274,798 bytes: within the 360 KB profile and 0.34% of the corpus. The 104 raw saved outputs add 1,063,203 bytes. Of those, `search` is 538,151 bytes (3 calls), and 406,501 bytes of that are per-hit occurrence lists (up to 98 ref rows per hit). `exact show` adds 279,455 and `exact grep` 130,731. The text payload of all outputs is only 338,553 bytes. The agent had to fetch because the packet delivered pointers and heads: G carries 22,558 content bytes for 325 items, the 24 semantic items carry 0 bytes, and A is truncated. Nothing budgets, packetises, deduplicates or collapses these outputs (OBS-BR-06). |
| `G7.external_read_bytes` | GRADER_DEFECT (`GD-7`) | the declared line windows total 138,569 bytes, under 0.5% of the corpus (401,332). The tool counts whole blobs whose content already arrived through govbridge outputs. |
| `G7.undeclared_reads` | GRADER_DEFECT (`GD-6`) | the tool counts 83 reads; the grader adjudicated 0 undeclared corpus reads. The residue is 3 orchestrator run-metadata files in RUN, which the design does not scope, so this is part of the GD-6 decision. |

A separate measure of context efficiency, which failed no gate: `bootstrap.md` (282,782 bytes) contains the whole
packet body, so the agent was handed the packet twice. The orchestrator also measured a peak of 503,981 context
tokens.

### 3.5 G8: controls (11 items; all three fail)

| Control | Items | Classes | Measured |
|---|---:|---|---|
| CTRL-1 | 3 | 3 BRIDGE-R | two required records whose ids were already discovered and never followed up; one code window reachable by `callers` of a function already in the agent's own output |
| CTRL-2 | 4 | 3 BRIDGE-R, 1 GRADER (GD-10) | one record id already discovered and not followed; one required item ranked 11th semantically for the compiled query text, just past k = 8; one fact whose source record was never delivered; one citation inside the right function's body that the matcher cannot see |
| CTRL-3 | 4 | 2 BRIDGE-R, 1 AGENT, 1 GRADER (GD-8) | two record ids discovered and not followed (BRIDGE-R); one record past A's cut, cited only at document level (GD-8); one pointer-only (0-byte) semantic packet item not cited (AGENT) |

The controls fail on generic retrieval defects: no follow-up, fixed top-k, truncation and pointer-only delivery. This
supports the finding that the bridge is not Review-8-shaped. A generic repair must be shown on controls.

### 3.6 G3 and the ungated AUTH queries (5 items, informational)

G3 passes, as adjudicated by the grader. The AUTH-3 and AUTH-4 misses carry no gate:

| Key | Class |
|---|---|
| `G3i.AUTH-3.R1` | GRADER (GD-8) |
| `G3i.AUTH-3.R2` | AGENT (packet F) |
| `G3i.AUTH-3.R3` | BRIDGE-R (record past A's cut) |
| `G3i.AUTH-4.R3` | BRIDGE-R (id already discovered) |
| `G3i.AUTH-4.M1` | AGENT (in hand) |

Some failures appear in the tool only, with the grade overruled by the rubric grader. They are not counted as failed
items:

* GD-1: a crash;
* GD-2: G6 graded the wrong answer;
* GD-3: a record anchor matched by record id only;
* GD-4: the G3 phrase test;
* GD-5: the side-by-side check;
* GD-9: [R] results not ingested, and AUTH has no gate.

## 4. Where the bridge lost the evidence

Counts are over the 89 measured anchor rows: 83 gated items, with the two any-of stages expanded into their 8
alternatives.

| Signal | Rows |
|---|---:|
| indexed in the store (chunk, code symbol or record definition) | 88 |
| the anchor's document is in section A but cut before the anchor | 22 |
| a compile candidate before budget | 25 |
| … of which dropped by budget | 11 |
| test anchors that are one code hop from any surfaced symbol | 3 of 20 |
| test anchors in the packet | 1 of 20 |
| test anchors in the agent's own grep output (definition line only) | 16 of 20 |

## 5. Counterfactuals: which fixes the gate needs

These are computed in `09-aggregate.json` by treating one cause family's items as found. For facts, the pass rule
also requires every remaining fact to be in a fixed family.

| Scenario | Failing G5/G8 queries that would pass (of 29) | G5 classes passing (of 10) |
|---|---:|---:|
| no change | 0 | 1 |
| grader and oracle rules fixed | 0 | 1 |
| grader, oracle and agent behaviour fixed | 12 | 6 (QC3, QC8, QC9, QC10 still fail) |
| bridge (retrievable) fixed only | 6, including CTRL-1 and CTRL-2 | 2 |
| both | all 29 (one reaches recall 0.8 exactly, with only its BRIDGE-NR item missing) | 10 |

The consequence for the plan is that the repair must cover **both** the bridge's delivery and retrieval and the
answer-side aids. Only the bridge can make the agent-side aids effective: it must deliver a tests facet, bodies
instead of pointers, and a citation lint. Grader repairs are necessary for honest scoring, but they rescue no failing
query on their own.

## 6. Generic root causes

Each root cause below is a capability defect. None names a Review-8 item.

| RC | Defect (measured) | Items it explains (primary) | Repair node |
|---|---|---:|---|
| RC-1 | **Mandatory inputs are silently truncated, and declared selectors are ignored.** `item_from_mandatory` renders `_read_excerpt(max_chars=4000)` with no marker (`truncation_marker_in_packet: false`), despite "A is never truncated" (§5.3 rule 6). 15 of 20 A items are cut: 384,595 source bytes become 61,107 rendered. An entry-range item renders the file head rather than its range: 57,583 bytes selected become 4,051 rendered, none of them in range. A key-list item behaves the same way: about 16,100 bytes selected become 4,006 rendered, none of them those keys (`06b`). A two-path item resolves one path and delivers a 77-byte by-reference directory stub. Untruncated A alone (384,595) would exceed the 360 KB profile, so the fix must be hierarchical, not a raised cap. | B-TRUNCATED-MANDATORY 7, B-BYREF-DIR-UNEXPANDED 6, MS-TRUNCATED-MANDATORY 4; contributing in 22 rows | RM |
| RC-2 | **Templated queries are silently not run.** 30 of 41 public queries (class × subject) have no `text`, and `_load_queries` skips them. Only 11 public queries and 2 D.2 templates were compiled. | B-QUERY-NOT-RUN 6; contributing throughout G5 | GA1 |
| RC-3 | **Retrieval is a single round with a fixed top-k.** There are no facets and no follow-up; k = 8 everywhere, with no paging. The fan-out caps have no continuation: 33 of 63 T1 symbols have more call sites than `max_callers` (6), and 1,255 call sites lie beyond the cap. Identifiers the packet and the agent had already surfaced (decision ids, record ids, functions, path literals) were never followed. | B-FOLLOWUP-ID 9, B-FOLLOWUP-CALLERS 2, B-TOPK 1, B-SCOPED-SECTION 1, MS-NOT-RETRIEVED-FOLLOWUP 2, MS-IMPACT-CONSUMERS 1 | GA1, GA2 |
| RC-4 | **The budget is facet-blind.** G's T2 retention is decided by resolution label, EXACT before HEURISTIC. 225 READS_KEY items (EXACT_SPAN) are kept, while all 37 TESTS edges (HEURISTIC_NAME) and 263 heuristic CALLS are dropped. H drops 58 of 100 lexical and semantic hits. Drops carry no continuation handle. | B-BUDGET-DROP 9; the missing tests facet behind most QC7 agent misses | GA3 |
| RC-5 | **Delivery is pointer-only.** G symbol items are signatures only: 2,879 bytes for 63 items. Semantic hits carry `text=None`, which gives 24 items with 0 bytes. The agent therefore had to re-read by `exact show` (55 calls, 279,455 bytes). | contributing to A-PACKET-NOT-CITED (11) and G7 | GA3 |
| RC-6 | **There are no supplementary packets** (OBS-BR-06). Query outputs are raw JSON. Each search hit lists every occurrence across 98 refs, which gives 406,501 bytes of metadata. There is no manifest, hash, read token, deduplication against the packet, or budget. The bootstrap inlines the whole packet. | G7.packet_bytes | RS |
| RC-7 | **Graph and lineage gaps.** Four gaps were measured: (a) TESTS edges come only from a name heuristic, and 17 of 20 missing test anchors are not one hop from any surfaced symbol, so tests that exercise behaviour through the binary or a test registry are invisible; (b) no code-to-data edges (path literals of config and template files); (c) no code-to-requirement edges: requirement citations in code comments, such as `<contract>:<line>` or `§n`, are not parsed; (d) YAML state records are largely unaddressable: 54 top-level keys in one state file, but 2 `record_def` rows. The two missing capabilities are symbol-introduction history and version reconciliation across refs, although the store holds per-ref blob ids. | MS-VERSION-RECONCILIATION 3, MS-DEPENDENCY-DATA 2, MS-TESTS-BODY 1, N-NOT-INDEXED 1; contributing to QC2, QC7, QC9 | RL |
| RC-8 | **Exclusions are not automatic** (OBS-BR-08, OD-BR-03 item 1). The CLI routes return 75 excluded-path hits across the 11 public texts; with the task's exclusions passed, they return 0. Two compile call sites pass no exclusions at all (`packet.py`: the seed code route and the D.2 both-ways templates). | no gate item (secrecy risk) | RX |
| RC-9 | **The task inputs are not in the packet** (OBS-BR-07). The query set and the answers and receipt schemas travel outside the packet, in orchestrator-copied files. | no gate item (protocol risk) | RS |
| RC-10 | **Grader and grading-rule defects.** GD-1…GD-9 (BR-AR-0012); **GD-10 (new)**: a symbol-qualified anchor is never matched by an exact line citation inside that symbol; OBS-BR-05 (the 1% check is disabled). The undefined rules behind GD-8, stage placement and AUTH gating need decisions. | GD-8 10, GD-10 1, GD-7 1, GD-6 1; ORACLE_STRICTNESS 7 | DEC, RG |
| RC-11 | **Answer-side aids are absent.** No tool resolves a named identifier to a citation. Nothing flags names without citations, whole-document citations of sectioned documents, or facts carried only in another answer. | the 53 AGENT items: A-OUTPUT-NOT-CITED 19, A-PACKET-NOT-CITED 11, MS-IN-HAND-NOT-STATED 12, MS-CROSS-ANSWER 11 | RA, plus the run-2 protocol |

## 7. Every failed item

The 126 gated items of G4, G5, G6 and G8 are listed below. The three G7 items are in §3.4, and the five
informational AUTH items follow the gated ones. Class short forms: GRADER, ORACLE, AGENT, BRIDGE-R, BRIDGE-NR.
Where an item's class depends on the GD-8 decision, its class under a strict ruling ("a whole-document citation does
not match a sectioned anchor") is shown in brackets.

| Key | Type | Class | Cause code | Measured signals (full record: evidence/08-anchors.public.json) |
|---|---|---|---|---|
| G4.R8-CHAIN-F3.prior_findings.D | anchor, any-of | GRADER | GD-8 | per alternative: A1 AGENT, A2 BRIDGE-R, A3 GRADER, A4 AGENT, A5 AGENT |
| G4.R8-CHAIN-F3.tests.D | anchor, any-of | AGENT | A-OUTPUT-NOT-CITED | per alternative: A1 AGENT, A2 AGENT, A3 BRIDGE-R |
| G5.S1-QC3.R4 | record | BRIDGE-R | B-QUERY-NOT-RUN | indexed; query-text probe: lexical #166, semantic #35, in-document #3/9; identifier already discovered |
| G5.S1-QC3.R5 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: in-document #1/5; identifier already discovered |
| G5.S1-QC4.R5 | code | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: in-document #1/9; identifier already discovered |
| G5.S1-QC5.R2 | code | BRIDGE-R | B-FOLLOWUP-CALLERS | indexed; query-text probe: in-document #10/133; one code hop from a surfaced symbol |
| G5.S1-QC5.R3 | code | BRIDGE-R | B-BUDGET-DROP | compiled, then budget-dropped; indexed; query-text probe: lexical #86, in-document #1/133; one code hop from a surfaced symbol |
| G5.S1-QC5.R4 | code | BRIDGE-R | B-BUDGET-DROP | compiled, then budget-dropped; indexed; query-text probe: in-document #17/57 |
| G5.S1-QC5.R5 | code | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (content, 2 file(s)); cited in 2 other answer(s); indexed; query-text probe: in-document #1/11; one code hop from a surfaced symbol; identifier already discovered |
| G5.S1-QC7.R1 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #4, semantic #51, in-document #1/34; identifier already discovered |
| G5.S1-QC7.R2 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: in-document #5/34; identifier already discovered |
| G5.S1-QC7.R4 | test | AGENT | A-PACKET-NOT-CITED | packet G: citable item, no body; indexed; query-text probe: in-document #4/13; one code hop from a surfaced symbol; identifier already discovered |
| G5.S1-QC7.R5 | test | BRIDGE-R | B-BUDGET-DROP | compiled, then budget-dropped; indexed; query-text probe: lexical #48, in-document #2/16; one code hop from a surfaced symbol |
| G5.S1-QC8.R1 | contract | GRADER | GD-8 (strict GD-8: A-PACKET-NOT-CITED) | packet A: content delivered; in agent outputs (definition/grep line, 1 file(s)); this answer cites its whole document; indexed; query-text probe: semantic #17, in-document #1/42 |
| G5.S1-QC8.R2 | record | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: in-document #4/20; identifier already discovered |
| G5.S1-QC8.R3 | record | BRIDGE-R | B-BUDGET-DROP | its document is in A but cut before it; compiled, then budget-dropped; indexed; query-text probe: in-document #3/77; identifier already discovered |
| G5.S1-QC8.R4 | evidence | BRIDGE-R | B-BYREF-DIR-UNEXPANDED | inside a by-reference mandatory directory; indexed; query-text probe: in-document #8/13 |
| G5.S1-QC8.R5 | evidence | BRIDGE-R | B-BYREF-DIR-UNEXPANDED | inside a by-reference mandatory directory; indexed |
| G5.S1-QC9.R1 | record | BRIDGE-R | B-BUDGET-DROP | its document is in A but cut before it; compiled, then budget-dropped; indexed; query-text probe: in-document #16/77; identifier already discovered |
| G5.S1-QC10.R1 | record | AGENT | A-PACKET-NOT-CITED | packet A/D.1: citable item, no body; its document is in A but cut before it; indexed; query-text probe: lexical #25, semantic #3, in-document #1/12; identifier already discovered |
| G5.S1-QC10.R2 | contract | AGENT | A-OUTPUT-NOT-CITED | its document is in A but cut before it; in agent outputs (content, 1 file(s)); cited in 5 other answer(s); indexed; query-text probe: semantic #86, in-document #15/42 |
| G5.S1-QC10.R3 | code | AGENT | A-PACKET-NOT-CITED | packet G: citable item, no body; in agent outputs (content, 1 file(s)); cited in 4 other answer(s); indexed; query-text probe: in-document #66/166; one code hop from a surfaced symbol; identifier already discovered |
| G5.S1-QC10.R4 | code | BRIDGE-R | B-BUDGET-DROP | compiled, then budget-dropped; indexed; query-text probe: lexical #155, in-document #1/133; one code hop from a surfaced symbol |
| G5.S2-QC1.R1 | record | BRIDGE-R | B-QUERY-NOT-RUN | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #3, semantic #21, in-document #1/10; identifier already discovered |
| G5.S2-QC1.R2 | record | GRADER | GD-8 (strict GD-8: A-PACKET-NOT-CITED) | packet A: content delivered; this answer cites its whole document; indexed; query-text probe: semantic #6, in-document #3/6; identifier already discovered |
| G5.S2-QC1.R4 | record | AGENT | A-OUTPUT-NOT-CITED | its document is in A but cut before it; compiled, then budget-dropped; in agent outputs (content, 1 file(s)); indexed; query-text probe: lexical #43, semantic #75, in-document #1/77; identifier already discovered |
| G5.S2-QC1.R5 | record | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: lexical #1, semantic #66, in-document #1/7; identifier already discovered |
| G5.S2-QC3.R3 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: lexical #177, in-document #3/10; identifier already discovered |
| G5.S2-QC3.R4 | record | BRIDGE-R | B-QUERY-NOT-RUN | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #7, in-document #1/10; identifier already discovered |
| G5.S2-QC4.R4 | code | AGENT | A-PACKET-NOT-CITED | packet G: citable item, no body; in agent outputs (content, 2 file(s)); cited in 2 other answer(s); indexed; query-text probe: in-document #9/25; one code hop from a surfaced symbol; identifier already discovered |
| G5.S2-QC4.R5 | code | AGENT | A-PACKET-NOT-CITED | packet G: citable item, no body; in agent outputs (definition/grep line, 2 file(s)); indexed; query-text probe: in-document #80/144; one code hop from a surfaced symbol; identifier already discovered |
| G5.S2-QC6.R1 | record | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: in-document #11/77; identifier already discovered |
| G5.S2-QC6.R2 | record | GRADER | GD-8 (strict GD-8: A-PACKET-NOT-CITED) | packet A: content delivered; this answer cites its whole document; indexed; query-text probe: lexical #16, semantic #9, in-document #2/6; identifier already discovered |
| G5.S2-QC6.R3 | record | GRADER | GD-8 (strict GD-8: A-PACKET-NOT-CITED) | packet A: content delivered; this answer cites its whole document; indexed; query-text probe: lexical #144, semantic #91, in-document #2/7; identifier already discovered |
| G5.S2-QC6.R4 | record | AGENT | A-PACKET-NOT-CITED | packet H: content delivered; its document is in A but cut before it; in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #153, in-document #3/174; identifier already discovered |
| G5.S2-QC6.R5 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: in-document #3/10; identifier already discovered |
| G5.S2-QC7.R1 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #16, in-document #1/17; identifier already discovered |
| G5.S2-QC7.R2 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #138, in-document #3/17; identifier already discovered |
| G5.S2-QC7.R3 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #10, in-document #1/34; identifier already discovered |
| G5.S2-QC7.R4 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #139, semantic #47, in-document #2/34; identifier already discovered |
| G5.S2-QC7.R5 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #188, in-document #3/34; identifier already discovered |
| G5.S2-QC8.R1 | contract | GRADER | GD-8 (strict GD-8: A-PACKET-NOT-CITED) | packet A: content delivered; in agent outputs (definition/grep line, 1 file(s)); this answer cites its whole document; indexed; query-text probe: in-document #1/42 |
| G5.S2-QC8.R2 | evidence | BRIDGE-R | B-BYREF-DIR-UNEXPANDED | inside a by-reference mandatory directory; indexed; query-text probe: lexical #16, in-document #3/13 |
| G5.S2-QC8.R3 | record | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: in-document #11/77; identifier already discovered |
| G5.S2-QC8.R4 | evidence | BRIDGE-R | B-BYREF-DIR-UNEXPANDED | inside a by-reference mandatory directory; indexed |
| G5.S2-QC8.R5 | record | BRIDGE-R | B-QUERY-NOT-RUN | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #5, semantic #48, in-document #1/10; identifier already discovered |
| G5.S2-QC9.R1 | record | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: in-document #11/77; identifier already discovered |
| G5.S2-QC9.R2 | record | BRIDGE-R | B-QUERY-NOT-RUN | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #10, semantic #3, in-document #1/10; identifier already discovered |
| G5.S2-QC9.R3 | record | GRADER | GD-8 (strict GD-8: A-PACKET-NOT-CITED) | packet A: content delivered; this answer cites its whole document; indexed; query-text probe: lexical #33, semantic #136, in-document #2/6; identifier already discovered |
| G5.S2-QC9.R4 | record | BRIDGE-R | B-BUDGET-DROP | its document is in A but cut before it; compiled, then budget-dropped; indexed; query-text probe: in-document #45/77; identifier already discovered |
| G5.S2-QC10.R3 | record | BRIDGE-R | B-QUERY-NOT-RUN | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #3, semantic #100, in-document #1/10; identifier already discovered |
| G5.S3-QC2.R1 | contract | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: in-document #18/42 |
| G5.S3-QC2.R2 | code | BRIDGE-R | B-SCOPED-SECTION | indexed; query-text probe: in-document #2/8; identifier already discovered |
| G5.S3-QC3.R3 | record | BRIDGE-R | B-BUDGET-DROP | its document is in A but cut before it; compiled, then budget-dropped; indexed; query-text probe: lexical #24, semantic #38, in-document #2/77; identifier already discovered |
| G5.S3-QC6.R2 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 2 file(s)); indexed; query-text probe: lexical #38, semantic #1, in-document #2/35; identifier already discovered |
| G5.S3-QC6.R3 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #100, semantic #124, in-document #12/42; identifier already discovered |
| G5.S3-QC6.R5 | record | AGENT | A-PACKET-NOT-CITED | packet H: content delivered; its document is in A but cut before it; indexed; query-text probe: lexical #42, semantic #27, in-document #1/174; identifier already discovered |
| G5.S3-QC7.R2 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #85, in-document #13/42; identifier already discovered |
| G5.S3-QC7.R3 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 2 file(s)); indexed; query-text probe: lexical #69, semantic #17, in-document #2/35; identifier already discovered |
| G5.S3-QC7.R4 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #91, in-document #2/34; identifier already discovered |
| G5.S3-QC7.R5 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: lexical #91, semantic #11, in-document #2/34; identifier already discovered |
| G5.S3-QC8.R1 | evidence | BRIDGE-R | B-BYREF-DIR-UNEXPANDED | inside a by-reference mandatory directory; indexed; identifier already discovered |
| G5.S3-QC8.R2 | evidence | BRIDGE-R | B-BYREF-DIR-UNEXPANDED | inside a by-reference mandatory directory; indexed; query-text probe: lexical #155, in-document #1/13 |
| G5.S3-QC8.R3 | test | AGENT | A-OUTPUT-NOT-CITED | compiled, then budget-dropped; in agent outputs (content, 1 file(s)); cited in 4 other answer(s); indexed; query-text probe: lexical #31, semantic #119, in-document #4/42; one code hop from a surfaced symbol; identifier already discovered |
| G5.S3-QC8.R4 | contract | GRADER | GD-8 (strict GD-8: A-PACKET-NOT-CITED) | packet A: content delivered; in agent outputs (definition/grep line, 1 file(s)); this answer cites its whole document; indexed; query-text probe: in-document #1/42 |
| G5.S3-QC8.R5 | evidence | GRADER | GD-8 (strict GD-8: B-TRUNCATED-MANDATORY) | its document is in A but cut before it; this answer cites its whole document; indexed; query-text probe: lexical #123, in-document #9/25 |
| G5.S3-QC9.R2 | record | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: lexical #75, in-document #2/77; identifier already discovered |
| G5.S3-QC9.R3 | record | BRIDGE-R | B-BUDGET-DROP | its document is in A but cut before it; compiled, then budget-dropped; indexed; query-text probe: lexical #74, semantic #26, in-document #1/77; identifier already discovered |
| G5.S3-QC9.R4 | record | AGENT | A-PACKET-NOT-CITED | packet F: citable item, no body; its document is in A but cut before it; in agent outputs (content, 1 file(s)); indexed; query-text probe: in-document #3/77; identifier already discovered |
| G5.S3-QC10.R2 | code | AGENT | A-PACKET-NOT-CITED | packet G: citable item, no body; in agent outputs (content, 1 file(s)); cited in 2 other answer(s); indexed; query-text probe: in-document #7/46; one code hop from a surfaced symbol; identifier already discovered |
| G5.S3-QC10.R4 | code | BRIDGE-NR | N-NOT-INDEXED | not indexed; identifier already discovered |
| G5.S3-QC10.R5 | record | AGENT | A-PACKET-NOT-CITED | packet A/D.1/D.2/D.3: content delivered; cited in 7 other answer(s); indexed; query-text probe: lexical #3, semantic #4, in-document #1/4; identifier already discovered |
| G8.CTRL-1.R1 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: in-document #1/4; identifier already discovered |
| G8.CTRL-1.R2 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: lexical #126, semantic #22, in-document #2/19; identifier already discovered |
| G8.CTRL-1.R4 | code | BRIDGE-R | B-FOLLOWUP-CALLERS | indexed; query-text probe: in-document #59/65; one code hop from a surfaced symbol |
| G8.CTRL-2.R1 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: semantic #199, in-document #1/5; identifier already discovered |
| G8.CTRL-2.R2 | code | BRIDGE-R | B-TOPK | indexed; query-text probe: lexical #109, semantic #11, in-document #1/24 |
| G8.CTRL-2.R4 | code | GRADER | GD-10 | this answer cites lines inside the symbol; indexed; query-text probe: in-document #11/73 |
| G8.CTRL-3.R1 | record | GRADER | GD-8 (strict GD-8: B-TRUNCATED-MANDATORY) | its document is in A but cut before it; this answer cites its whole document; indexed; query-text probe: lexical #30, in-document #1/77; identifier already discovered |
| G8.CTRL-3.R2 | record | AGENT | A-PACKET-NOT-CITED | packet H: citable item, no body; indexed; query-text probe: lexical #31, semantic #5, in-document #1/60; identifier already discovered |
| G8.CTRL-3.R3 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: in-document #3/7; identifier already discovered |
| G8.CTRL-3.R4 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: in-document #1/4; identifier already discovered |
| G6.R8-F1-BOTHWAYS.C4 | test | AGENT | A-OUTPUT-NOT-CITED | in agent outputs (definition/grep line, 1 file(s)); indexed; query-text probe: in-document #20/42; identifier already discovered |
| G4.R8-CHAIN-F2.requirement.M1 | fact | BRIDGE-R | MS-TRUNCATED-MANDATORY | basis code, section 2.2 |
| G4.R8-CHAIN-F2.partition_filtering.M2 | fact | ORACLE | MS-STAGE-PLACEMENT | basis code, section 2.2 |
| G4.R8-CHAIN-F2.effective_behaviour.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G4.R8-CHAIN-F2.effective_behaviour.M2 | fact | BRIDGE-R | MS-DEPENDENCY-DATA | basis code, section 2.2 |
| G4.R8-CHAIN-F2.prior_findings.M2 | fact | ORACLE | MS-STAGE-PLACEMENT | basis code, section 2.2 |
| G4.R8-CHAIN-F3.requirement.M1 | fact | BRIDGE-R | MS-TRUNCATED-MANDATORY | basis code, section 2.2 |
| G4.R8-CHAIN-F3.source_construction.M2 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G4.R8-CHAIN-F3.composition_union.M1 | fact | ORACLE | MS-STAGE-PLACEMENT | basis code, section 2.2 |
| G4.R8-CHAIN-F3.composition_union.M2 | fact | ORACLE | MS-STAGE-PLACEMENT | basis code, section 2.2 |
| G4.R8-CHAIN-F3.partition_filtering.M1 | fact | ORACLE | MS-STAGE-PLACEMENT | basis code, section 2.2 |
| G4.R8-CHAIN-F3.precedence_ordering.M3 | fact | ORACLE | MS-STAGE-PLACEMENT | basis code, section 2.2 |
| G4.R8-CHAIN-F3.matcher_evaluator.M1 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G4.R8-CHAIN-F3.effective_behaviour.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G4.R8-CHAIN-F3.effective_behaviour.M3 | fact | BRIDGE-R | MS-DEPENDENCY-DATA | basis code, section 2.2 |
| G4.R8-CHAIN-F3.tests.M2 | fact | BRIDGE-R | MS-TESTS-BODY | basis code, section 2.2 |
| G4.R8-CHAIN-F3.prior_findings.M1 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G4.R8-CHAIN-F3.prior_findings.M2 | fact | ORACLE | MS-STAGE-PLACEMENT | basis code, section 2.2 |
| G5.S1-QC2.M2 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S1-QC3.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S1-QC3.M2 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S1-QC4.M2 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S1-QC5.M1 | fact | BRIDGE-R | MS-IMPACT-CONSUMERS | basis code, section 2.2 |
| G5.S1-QC8.M2 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S1-QC9.M1 | fact | BRIDGE-R | MS-VERSION-RECONCILIATION | basis code, section 2.2 |
| G5.S1-QC10.M1 | fact | BRIDGE-R | MS-TRUNCATED-MANDATORY | basis code, section 2.2 |
| G5.S2-QC3.M2 | fact | BRIDGE-R | MS-NOT-RETRIEVED-FOLLOWUP | basis code, section 2.2 |
| G5.S2-QC5.M1 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S2-QC8.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S2-QC9.M1 | fact | BRIDGE-R | MS-VERSION-RECONCILIATION | basis code, section 2.2 |
| G5.S2-QC9.M2 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S2-QC10.M2 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S3-QC2.M1 | fact | BRIDGE-R | MS-TRUNCATED-MANDATORY | basis code, section 2.2 |
| G5.S3-QC3.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S3-QC3.M2 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S3-QC4.M2 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S3-QC5.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S3-QC5.M2 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S3-QC5.M3 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S3-QC8.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |
| G5.S3-QC9.M2 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G5.S3-QC9.M3 | fact | BRIDGE-R | MS-VERSION-RECONCILIATION | basis code, section 2.2 |
| G5.S3-QC10.M2 | fact | AGENT | MS-CROSS-ANSWER | basis code, section 2.2 |
| G8.CTRL-2.M2 | fact | BRIDGE-R | MS-NOT-RETRIEVED-FOLLOWUP | basis code, section 2.2 |

**Informational: the ungated AUTH items.**

| Key | Type | Class | Cause code | Measured signals |
|---|---|---|---|---|
| G3i.AUTH-3.R1 | evidence | GRADER | GD-8 (strict GD-8: B-TOPK) | in agent outputs (definition/grep line, 1 file(s)); this answer cites its whole document; indexed; query-text probe: lexical #12, in-document #1/4; identifier already discovered |
| G3i.AUTH-3.R2 | record | AGENT | A-PACKET-NOT-CITED | packet F: citable item, no body; its document is in A but cut before it; in agent outputs (content, 1 file(s)); indexed; query-text probe: lexical #6, in-document #2/77; identifier already discovered |
| G3i.AUTH-3.R3 | record | BRIDGE-R | B-TRUNCATED-MANDATORY | its document is in A but cut before it; indexed; query-text probe: in-document #15/174; identifier already discovered |
| G3i.AUTH-4.R3 | record | BRIDGE-R | B-FOLLOWUP-ID | indexed; query-text probe: semantic #64, in-document #1/5; identifier already discovered |
| G3i.AUTH-4.M1 | fact | AGENT | MS-IN-HAND-NOT-STATED | basis code, section 2.2 |

## 8. Limits of this analysis

* **Judgement calls.** Five kinds of classification rest on judgement rather than a single mechanical test:
  * The must_state rows rest on the grader's own notes and on private presence checks. Their bases are recorded,
    and the tokens are not.
  * The LINE rule counts a grep definition line as possession for code and test anchors, but not for records.
    Changing that rule moves 16 test rows from AGENT to BRIDGE-R through the tests facet. It does not change the
    counterfactual conclusion that both sides need repair.
  * Any-of stages are classified by their most favourable alternative.
  * The GD-8 items flip to AGENT or BRIDGE-R under a strict ruling; the brackets in §7 show each flip.
  * `ORACLE_STRICTNESS` is used only for stage placement. No required item was found that the public query does
    not ask for, and no oracle anchor was found where an equally correct alternative was cited but refused. The
    single BRIDGE-NR item is an anchor at a commit outside the view. The answer that missed it cites no equivalent
    at the canonical ref, so it is not classed as strictness.
* **Probe realism.** The query-text probes use the instantiated public text, which is what a compile would have
  run. They are not a claim about the best possible query. The follow-up probes show that an identifier was
  already discovered and resolvable. They do not simulate a full adaptive loop.
* **Store version.** All retrievability was measured on the run-1 store, which is the only view that bears on
  run-1. Any repair changes the store layers, so D2 must rebuild the store.
