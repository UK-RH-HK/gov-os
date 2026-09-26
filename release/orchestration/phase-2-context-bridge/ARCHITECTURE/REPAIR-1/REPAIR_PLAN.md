# REPAIR-1: generic repair plan for the Context/Retrieval Bridge (BR-AR-0016)

| Field | Value |
|---|---|
| Status | **PROPOSED**, for the orchestrator. Nothing here has been built. The analyst diagnosed and did not repair. |
| Basis | `CAUSE_ANALYSIS.md`: 129 measured failed items and root causes RC-1…RC-11 |
| Binding inputs | OD-BR-05 (multi-batch and multi-hop retrieval); OD-BR-06 §2–4 (retrieval completeness; parallel and sequential retrieval; hierarchical synthesis); OC-BR-02 (whole repository, generic, not Review-8-shaped); OBS-BR-05…10; GD-1…GD-9 (BR-AR-0012), plus GD-10 (found here) |
| Machine-readable | `REPAIR_DAG.yaml`, with the same node format as `ARCHITECTURE/IMPLEMENTATION_DAG.yaml` |
| Oracle rule | This plan contains no oracle content. No acceptance check uses a public demonstration query text, a Review-8 identifier or the run-1 oracle. Every capability is proved on fixtures and on an **unrelated** real-view control chosen by the orchestrator. |

## 0. The repair in one paragraph

The bridge preserved authority and found the real enforcement points. It failed on completeness, for three reasons:

* it delivered **heads of documents** (section A was cut at 4,000 characters with no marker, and declared selectors
  were ignored);
* it delivered **pointers instead of evidence** (code signatures, and semantic hits with 0 bytes);
* it retrieved **once, at a fixed top-8, for only 11 of 41 queries**, with a facet-blind budget that dropped every
  TESTS edge.

The agent then compensated with 103 raw query dumps. Those dumps broke G7 and still missed items that it had named
but not cited.

The repair builds the OD-BR-05 retrieval loop as one generic command, `govbridge gather`, and makes the compiler
consume it. The loop covers:

* instantiate the query;
* decompose it into facets;
* retrieve the facets in parallel;
* merge, with provenance, deduplication, version reconciliation and authority filtering;
* follow up the identifiers the evidence exposes;
* page until an explicit stopping reason.

The compiler must deliver content rather than pointers, under facet quotas, with supplementary packets and
hierarchical evidence notes for overflow. The repair also:

* makes mandatory inputs exact: never silently truncated, and selectors honoured;
* closes four graph gaps: tests, data dependencies, requirement citations and state-record ids;
* adds answer-side citation aids;
* repairs the grader after five grading-rule decisions.

Run-2 then repeats the demonstration with a fresh oracle, agent and grader. That happens only after an OD-BR-05 §9
multi-batch demonstration on an unrelated subject has passed.

## 1. From root cause to repair

| RC (CAUSE_ANALYSIS §6) | Repair | Node |
|---|---|---|
| RC-1: section A truncated; selectors ignored; by-reference directory never expanded | Mandatory fidelity: delivered in full, **or** as a hierarchical section map plus facet-selected sections plus a by-reference remainder, always disclosed. Entry, key and multi-path selectors are resolved. Directory items are expanded to a member manifest. | R1-RM |
| RC-2: 30 of 41 queries never compiled | Query instantiation. A query with no executable text is a **compile error**, never a silent skip. | R1-GA1 |
| RC-3: one round, k = 8, no facets, no follow-up; fan-out caps without continuation | `govbridge gather`: facets, parallel retrieval, follow-up, paging, stopping reasons, telemetry | R1-GA1, R1-GA2 (paging primitives in R1-RL) |
| RC-4: facet-blind budget; label-lexicographic drop order | Facet quotas, and a drop order that is round-robin across facets. Drops carry continuation handles. | R1-GA3 |
| RC-5: pointer-only delivery | Content slices for code, test and semantic items | R1-GA3 |
| RC-6: no supplementary packets; occurrence fan-out; bootstrap inlines the packet | Budgeted supplementary packets for every query command, with occurrence collapse, deduplication against the main packet, and a bootstrap that references the packet instead of inlining it | R1-RS |
| RC-7: graph and lineage gaps | TESTS edges beyond names; code→data and code→requirement edges; addressable YAML state records; a symbol-introduction history facet; a version-reconciliation facet | R1-RL (edges), R1-GA2 (reconciliation) |
| RC-8: exclusions not automatic | One task context that applies `retrieval_exclusions` in every route, command and compile call site | R1-RX |
| RC-9: task inputs outside the packet | Section I carries the query set and the answers and receipt schemas, by hash | R1-RS |
| RC-10: grader and grading-rule defects | Five decisions (D-1…D-5), then GD-1…GD-10 and OBS-BR-05, each with a regression test | R1-DEC, R1-RG |
| RC-11: no answer-side aids | `govbridge cite` and `govbridge answers lint`, plus run-2 protocol rules | R1-RA, R1-DEMO2 |

## 2. Target flow: `govbridge gather` (OD-BR-05 §1–§8, OD-BR-06 §2–§4)

```
query (id, class, subject | text)
  -> instantiate (class x subject template -> executable text; missing text = error)
  -> facet plan (config/facets.yaml: class -> facets; each facet = routes + scopes + query builders + batch size + quota)
  -> round 0: facets retrieved in PARALLEL (deterministic merge order), one batch each
  -> merge (dedup by content identity; provenance list; occurrence collapse; version reconciliation; authority/lifecycle)
  -> unresolved identifiers (record ids, symbols, path literals, test names, commits, requirement citations)
  -> round n: SEQUENTIAL follow-up for new identifiers + next page for facets still yielding new items
  -> stop with a recorded reason
  -> compile (quotas, content slices, notes when evidence > budget) + supplementary packets + telemetry
```

### 2.1 Query instantiation

A query entry is executable if and only if it resolves to text. A `{class, subject}` entry is instantiated from the
query set's own `query_classes` and `subjects` tables, and the compiler never skips it. Instantiation is generic: it
reads the tables that the query file itself carries, and nothing in code names a class or a subject. The compiler
fails with `QUERY_NOT_EXECUTABLE` for any entry it cannot instantiate.

### 2.2 The facet registry (`config/facets.yaml`, versioned, sha256 in the manifest)

These facets are generic and follow OD-BR-05 §1 and the ten query classes:

* `purpose`
* `requirement`
* `decisions_active`
* `decisions_history`
* `failed_approaches`
* `dependencies` (callees, data and config files read)
* `dependents` (callers, consumers, literal-key readers)
* `enforcement`
* `tests` (proving and challenging, including tests that drive the product as a process)
* `evidence_staleness`
* `versions` (canonical ref, and per-path identity across the view's refs)

Each facet declares:

* its routes;
* its scopes, by path class and never by file name (for example `CONTRACT`-class documents for `requirement`, and
  the decision and owner-record classes for `decisions_*`);
* how its queries are built (query text, subject text, and discovered identifiers of the kinds it accepts);
* its batch size;
* its minimum packet share.

A query class maps to a set of facets. A chain query maps to all of them. Controls are ordinary queries. **No facet,
scope or mapping may name a Review-8 item** (OC-BR-02), and the generic-rule audit in R1-INT checks this.

### 2.3 Parallel and deterministic

Facets in the same round run concurrently. The thread count does not affect the result: each facet's hits are sorted
by a stable key, and merging follows the registry order. R1-GA1 must prove byte-identical merged output for 1, 4 and
16 threads.

### 2.4 Continuation and paging

Every route accepts a cursor:

* lexical and semantic take an offset;
* code `callers`, `tests` and `reads_key` take a page (built in R1-RL).

`batch_size` is configuration (OD-BR-05: "8k … a configurable batch size only"). The literal 8 survives only as a
default in configuration. The profile's fan-out caps become page sizes, and a capped list returns a continuation
handle instead of a silent cut.

### 2.5 Adaptive follow-up

Identifier extractors run over every merged item:

* id-grammar record ids;
* symbol-shaped tokens;
* repository path literals and path fragments joined in code;
* test function names;
* commit hashes;
* requirement citations such as `<document>:<line>` or `§n`.

Each unresolved identifier is resolved by the matching route: `exact id`, code definitions or callers or tests, path
resolution, or a section of a known document. Each follow-up item records its **trigger**: the identifier and the
item it came from. A visited set prevents loops. Rounds continue while new identifiers or new facet pages appear.

### 2.6 Stopping reasons (fixed vocabulary, recorded per query)

* `FACETS_COVERED`: every requested facet has at least one item, or an explicit `MISSING` reason.
* `NO_UNRESOLVED_IDENTIFIERS`
* `MARGINAL_GAIN_ONLY_DUPLICATES`: the last round added only duplicates.
* `MAX_ROUNDS`: configurable. The unresolved identifiers are disclosed.
* `BUDGET_REACHED_WITH_UNRESOLVED`: the unresolved facets and identifiers are listed.

"Top-k returned" is never a stopping reason.

### 2.7 Merge before compilation

* **Deduplicate** by content identity: blob plus line span.
* **Keep provenance** for every item: each route, facet, round and trigger that produced it.
* **Collapse occurrences** to the canonical occurrence plus a per-ref identity summary ("identical at refs X, Y;
  differs at Z"). This removes RC-6's 98-row fan-out.
* **Version reconciliation** is the `versions` facet: per-path blob identity across the view's refs, and the canonical
  ref. The store already holds this data in its per-ref `occurrence` rows.
* **Authority and lifecycle filtering** is unchanged: only the resolver fills A, and superseded items go to E with a
  banner.

### 2.8 Compilation

* **Facet quotas.** Every requested facet that has candidates keeps at least its minimum share. Drop order is
  round-robin across facets, lowest-ranked first within a facet. A resolution label is never a global key. A drop
  records a continuation handle, per facet, in the manifest.
* **Content, not pointers.**
  * Code and test items carry the definition body, up to `max_slice_chars` (1,600), with a larger slice for the
    facet's top items.
  * Semantic hits carry their chunk text.
  * Items whose content is already in the packet are cited by item id.
* **Per-item tags:** the query ids and facets each item serves, so an agent can find "the tests for query X".
* **Overflow.**
  * If merged evidence exceeds the profile, the compiler emits hierarchical evidence notes (§2.10) and
    supplementary packets.
  * The main packet carries the mandatory sources, the notes, and the highest-ranked items per facet.
  * Nothing is silently discarded (OD-BR-06 §4).
* **D.2 both-ways evidence** runs through `gather` with the task's exclusions.

### 2.9 Supplementary packets (OBS-BR-06)

Every query command writes a supplementary packet directory: `search`, `why`, `impact`, `history`, `exact`, `state`,
and every `gather` round beyond the main packet. It holds `manifest.json`, `packet.md` and `meta.json`, with a
packet hash and read tokens. Each packet:

* is budgeted (a per-command profile);
* is deduplicated against the main packet and earlier supplementary packets, by item id;
* collapses occurrences.

`packet verify` verifies each one, `receipt check` covers all of them, and G7 counts them. Raw JSON remains available
behind `--raw`, and is never the default.

### 2.10 Hierarchical evidence notes (OD-BR-05 §7, OD-BR-06 §4)

A note is a derived record with this schema (`govbridge/notes`, with a validator):

* `note_id`
* `class: DERIVED_NOTE` (never ladder-admissible in A)
* `claims[]`, each with `sources[]` = {item_id, path, commit, blob, lines, content_sha256}
* `unresolved[]`
* `built_from_sha256`, over the sorted source hashes, so the note can be rebuilt

The validator refuses a note that:

* has a claim with no source;
* has a source that does not resolve;
* is placed in A;
* has a hash mismatch.

### 2.11 Telemetry (OD-BR-05 §9)

Each gather records:

* rounds, and per round and facet the candidate items and bytes;
* deduplicated items and bytes;
* follow-up triggers;
* final compiled bytes (main plus supplementary);
* the stop reason and the unresolved list.

The telemetry goes to the configured telemetry directory and is summarised in the packet manifest.

## 3. Mandatory-input fidelity (R1-RM)

1. **No silent truncation.** Remove the 4,000-character excerpt cut from mandatory items. A mandatory item is
   delivered in one of two ways:
   * **in full**; or
   * as a **section map** (headings and keys with line ranges and hashes), plus the sections selected by the task's
     facets, plus a **by-reference remainder** with read obligations.

   The second form carries a J notice, `MANDATORY_PARTIAL_DELIVERY`, that lists every undelivered range. No item may
   end mid-content without that notice.
2. **Selectors.** The resolver honours the selectors declared in the bridge state. Each is resolved to exact line
   spans; an unresolvable selector fails closed with a J notice:
   * an `entries` range of record ids;
   * a YAML `keys` list;
   * multiple `paths`.
3. **Directory items.** A by-reference directory is expanded into a member manifest: path, blob, size and class.
   Its members become retrievable through the `evidence_staleness` facet.
4. **Receipt semantics.** The receipt acknowledges `delivered_sha256` (what the agent received) separately from
   `source_sha256` (the resolver's record). It must not appear to acknowledge content that was never delivered.
5. **Budget.** Delivered in full, run-1's section A alone would be 384,595 bytes, more than the 360 KB profile.
   Selectors and section maps are therefore required. A larger cap is not a fix. Section A is still never *dropped*,
   as rule 6 of §5.3 requires.

## 4. Graph and lineage additions (R1-RL)

* **TESTS edges** come from three sources:
  * direct calls inside test functions;
  * tests that drive the product through its command-line binary, mapped from the invoked subcommand to its
    dispatch handler, generically from the CLI dispatch table;
  * test registries, meaning files that bind capabilities to tests, recognised by path class and schema rather than
    by name.
* **Code→data edges.** String literals, and joined path fragments, that name tracked repository paths.
* **Code→requirement edges.** Requirement citations in code comments, such as `<contract doc>:<line>` or section
  references, are resolved to the cited section.
* **State records.** YAML state files expose nested keys and `id:`-bearing list items as addressable records
  (`record_def`), so `exact id` resolves them. Run-1 measured one state file with 54 top-level keys and 2
  `record_def` rows.
* **Symbol history.** `INTRODUCED_IN` and `DELETED_IN` for a symbol across the indexed history layer, bounded by
  configuration, so that a "why was it created" facet can reach the introducing commit. Blobs outside the view may be
  read through the exact route by commit.
* **Paging primitives.** `callers`, `tests_of` and `reads_key_of` return pages and a cursor.

Each addition is a registered store layer with a digest. Rebuilding from clean twice must give identical digests.

## 5. Exclusions and the task context (R1-RX)

One `TaskContext`, loaded from `--task <spec>` or `GOVBRIDGE_TASK`, carries `retrieval_exclusions`. Every route and
every CLI query command applies it, and so do the compiler's seed code route and the D.2 templates. The two compile
call sites that run without exclusions today are listed in `evidence/06-packet-facts.json`. Each output discloses how
many hits were excluded. This closes OBS-BR-08 and OD-BR-03 item 1. Run-1 measured 75 excluded-path hits for the 11
text queries under the CLI default, and 0 with the exclusions applied.

## 6. Task inputs and bootstrap (R1-RS)

Section I carries the task's query set (instantiated) and the answers and receipt schemas, verbatim and by hash
(OBS-BR-07). The bootstrap references the packet by id and hash instead of inlining it; run-1's bootstrap was
282,782 bytes and contained the whole packet.

## 7. Answer-side aids (R1-RA)

* `govbridge cite <identifier> [--commit]` resolves a record id, symbol or test name to an exact citation: path,
  commit, lines, and symbol where there is one.
* `govbridge answers lint <answers> --packet … [--supplementary …]` reports:
  * identifiers named in a claim that resolve in the index and carry no citation;
  * whole-document citations of a document that has a section map;
  * a claim that points to "another answer" instead of restating it;
  * per-query self-containment.

  Lint is advisory for the agent. The run-2 protocol requires a clean lint or a justified waiver per finding.

In run-1, 30 of the 83 gated missing anchors were already in the agent's hands: in the packet or in its own outputs.
These tools target exactly that failure.

## 8. Grader repair (R1-DEC, then R1-RG)

### 8.1 Decisions required first (orchestrator; the owner where a gate's meaning changes)

| Id | Question | Analyst's recommendation (not a decision) |
|---|---|---|
| D-1 (GD-8) | Does a whole-document citation match a sectioned anchor? | It matches **only if** the cited packet item's *delivered* content covers the section. After R1-RM, the section map makes precise citation cheap. |
| D-2 | Is a must_state fact bound to a stage or to the chain? | The oracle declares the binding per fact: `stage` or `chain`. The default is `chain` for facts that span stages, and `stage` only where the stage's own claim is the point. |
| D-3 (GD-9) | Are AUTH-1…4 gated? | Gate them under G3's answer-side rule, with an explicit [R] ingestion format, or state in the design that they are informational. |
| D-4 (GD-6) | Is reading RUN's own orchestrator metadata an undeclared read? | No, if the metadata is not corpus and is listed as a task input. Otherwise it must be declared. |
| D-5 (G7) | What counts as packet bytes? | Main plus supplementary packets, which are manifested, deduplicated and budgeted. Task inputs in section I count once. Raw `--raw` output counts in full. |

### 8.2 Tool defects: every fix has a regression test on a synthetic fixture

| Id | Defect | Fix | Regression test (synthetic, no oracle) |
|---|---|---|---|
| GD-1 | crash on `lines: "START-END"` | normalise every accepted line form; make the schema say which forms are allowed | answers that use string, list and single-line forms all grade without error |
| GD-2 | G6 grades the first answer with `evidence_for` | select the answer by the oracle's both-ways `query_id` | two answers that both carry `evidence_for`; the right one is graded |
| GD-3 | record anchor matched by record id only | match by record id **or** by section (path, blob-identical commit, line overlap) | a section anchor with no id matches a line citation in that section |
| GD-4 | literal phrase test for a withdrawn finding | detect the item id plus a withdrawn marker within the same claim or banner, generically | several marker spellings pass; an unmarked citation fails |
| GD-5 | side-by-side requires both chains to PASS | require both enforcement points reached, and shared and differing recall ≥ 0.8 | the chains fail elsewhere, yet the side-by-side passes |
| GD-6 | undeclared-read false positives; `gq.sh exact …` arguments parsed as reads | exclude supplied inputs, the agent's own outputs and scratch; parse govbridge arguments as queries | a fixture transcript with 0 true undeclared reads gives 0 |
| GD-7 | external bytes counted as whole blobs when the content came through govbridge | count declared windows, or only direct reads, per D-5 | the fixture receipt's windows are counted as windows |
| GD-8 | whole-document versus sectioned anchor undefined | implement D-1 | a whole-document citation with delivered coverage matches; one without coverage does not |
| GD-9 | [R] results not ingested per query; AUTH ungated | ingest the rubric file per query; implement D-3 | a fixture rubric file changes the G5 result as expected |
| GD-10 (new) | a symbol-qualified anchor is never matched by an exact line citation inside that symbol | resolve the cited lines' enclosing symbol through the code store at the cited commit | a citation of lines inside a function matches that function's anchor |
| OBS-BR-05 | the 1%-of-corpus packet check never fires | always apply it, over main plus supplementary packet bytes | an oversize fixture fails G7 |

## 9. Genericity and controls (OC-BR-02)

* No code, configuration, facet, scope or test may name a Review-8 item, an F-finding, a Phase-2 file or a symbol
  taken from the Review-8 chains. R1-INT runs a generic-rule audit over `govbridge/**`, `config/**` and `tests/**`
  (fixture *data* excepted).
* Builders must **not** use the public demonstration query texts or the run-1 answers as acceptance input. They use
  synthetic fixtures and, on the real view, **unrelated controls** chosen by the orchestrator: CONTROL-A for building,
  and CONTROL-B, held back, for R1-MB. The criteria for a
  control subject:
  * its evidence spans at least 3 top-level directories;
  * at least one decision record and one test file are involved;
  * it is not a Review-8 subject and not a subject of CTRL-1, CTRL-2 or CTRL-3.

  Two such subjects are needed: one for R1-INT and one for R1-MB.
* Run-1's own controls failed on the bridge: 8 of 11 items were BRIDGE-R. A repair that lifts Review-8 recall
  without lifting the controls has failed OC-BR-02. Run-2's G8 is the external check.

## 10. OD-BR-05 §9: multi-batch demonstration (R1-MB, an acceptance node before run-2)

A fresh opus agent runs `gather` on one orchestrator-chosen query, whose evidence spans distant repository locations
and exceeds one batch, plus one unrelated control query. Both run on the repaired real view. The node passes only
if the telemetry and packets show all of the following:

1. **Multiple retrieval calls:** at least 2 rounds.
2. **Parallel retrieval:** at least one round where at least 2 facets ran concurrently.
3. **Sequential follow-up:** at least one round triggered by an identifier discovered in an earlier round, with the
   trigger recorded.
4. **More than one batch of evidence:** candidate bytes greater than the configured batch size, and final evidence
   from at least 3 distinct top-level directories.
5. **Provenance-bound merge:** every merged item carries provenance; deduplication counts are reported.
6. **Facet coverage:** every requested facet is covered, or `MISSING` with a reason.
7. **Stop reason** from the fixed vocabulary.
8. **Telemetry:** rounds, candidate and deduplicated tokens or chunks, final size and stop reason.

A fresh grader confirms items 1–8 mechanically, and checks that every claim in the answer cites a merged item.

## 11. Run-2 protocol

1. **Preconditions:**
   * R1-INT and R1-MB are PASS;
   * the grader is repaired (R1-RG) and D-1…D-5 are recorded;
   * the store has been rebuilt from clean at a frozen, repaired bridge tip (R1-D2): coverage `unclassified = 0`,
     freshness `NOOP`;
   * the demonstration freeze applies (OBS-BR-03).
2. **Fresh test-author (R1-TA2).** This is a fresh opus role: not the run-1 test-author, not a builder, not the
   analyst. It writes a **fresh** oracle from primary sources, under the D-2 fact-binding rule. The oracle is sealed
   in a `0700` directory that the orchestrator creates, at a location that is **not recorded in any committed file**,
   state or brief (lesson of OBS-BR-04). Only the sha256 commitment is committed. The run-1 oracle is contaminated,
   because it is committed on `bridge/grade-0012`, and it is never reused (OBS-BR-10).
3. **Same public queries.** `demonstration-queries.yaml` is unchanged. The only difference is that the compiler now
   instantiates the class queries (§2.1).
4. **Fresh demonstration agent (R1-DEMO2).** This is a fresh opus role with no prior chat. It receives the bootstrap,
   the main packet with section I carrying the task inputs, and the query commands, with the task context applied
   (§5). Supplementary packets are its only retrieval outputs. It must run `answers lint` before returning and
   justify each waiver. The secrecy audit from run-1 is repeated.
5. **Fresh grader (R1-GRADE2).** The repaired deterministic grader runs, then a fresh opus rubric grader under
   D-1…D-5. G1 and G2 now cover every supplementary packet.

## 12. Sequencing (see `REPAIR_DAG.yaml`)

| Group | Nodes | Why they are in this group |
|---|---|---|
| R1-PG0 | R1-CTRL, R1-DEC, R1-RN | have no dependencies. CTRL writes CONTROL-A and its baseline on the unrepaired bridge before any builder starts. |
| R1-PG1 | R1-RX, R1-RL, R1-RG, R1-TA2 | RX and RL need CONTROL-A. RG and TA2 need DEC. Their scopes are disjoint. |
| R1-PG2 | R1-RM, R1-GA1 | RM follows RX, which edits the compile call sites first. GA1 needs RX's task context and RL's paging. |
| R1-PG3 | R1-GA2, R1-RS | GA2 needs GA1 and RL. RS needs GA1 and RM. Their scopes are disjoint. |
| R1-PG4 | R1-GA3, R1-RA | GA3 needs GA2, RS, RN and RM. RA needs GA2 and RS. Their scopes are disjoint. |
| R1-PG5 | R1-INT | integration: whole suite, store rebuild, determinism, generic-rule audit, CONTROL-A before and after |
| R1-PG6 | R1-MB | OD-BR-05 §9 acceptance, on CONTROL-B, which the orchestrator chooses at dispatch and never shows to builders |
| R1-PG7 | R1-D2 | fresh store at the frozen, repaired tip |
| R1-PG8 | R1-DEMO2 | also needs TA2's commitment |
| R1-PG9 | R1-GRADE2 | |

`evidence/tools/check_repair_dag.py` verifies the ordering, the domain of every scope, and that scopes are disjoint
within each group (`evidence/12-check-repair-dag.out`: 18 nodes, 10 groups, 0 problems).

Shared files are sequenced, never co-edited. `govbridge/cli.py` is edited in turn by RX, GA1, RS and RA, and
`govbridge/compile/packet.py` by RX, RM and GA3.

## 13. Risks

* **Cost of the loop.** Unbounded rounds are a risk: `MAX_ROUNDS`, per-facet batch sizes and a wall-clock
  budget are configuration, and R1-INT measures the controls' wall time.
* **Over-delivery.** Content slices and quotas could re-create G7. Supplementary packets are budgeted and
  deduplicated, and G7 counts them (D-5).
* **Re-shaping around Review 8.** Tuning facets on the public queries is prohibited. Acceptance runs only on fixtures
  and unrelated controls, and run-2's controls are the external test.
* **Agent-side gaps remain.** The answer aids make them visible and cheap to fix. They do not guarantee the fix, which
  is why the run-2 protocol requires a clean lint.
* **Decision latency.** D-2 changes how the oracle is authored. TA2 must not start its authoring until DEC records
  D-2.
