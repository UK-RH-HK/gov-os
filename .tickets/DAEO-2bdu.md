---
id: DAEO-2bdu
status: in_progress
deps: [DAEO-ym8a, DAEO-siiz, DAEO-tgk2, DAEO-l78m, DAEO-q7lk, DAEO-61vm, DAEO-k1e2, DAEO-p8tv]
links: []
created: 2026-10-30T22:14:08Z
type: task
priority: 1
assignee: engineer
external-ref: W2-88
tags: [wave-2, implementation, memory, adoption, full, examin-minimum]
wbs_id: W2-88
title: 'Memory for any repository: at adoption, assess any repository however large, plan the refactoring it needs for full indexing as governed tickets for its owner to approve (never applied on their own), build the full index and the embeddings, set up the SQLite and vector-store structure'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-ym8a
- DAEO-siiz
- DAEO-tgk2
- DAEO-l78m
- DAEO-q7lk
- DAEO-61vm  # W2-170: the audit's set record and checks, called by memory_sets.py (S20) [added, DEC-1101 (1), DEC-1125 (2)]
- DAEO-k1e2  # W2-171: the audit's measure and pool, called by memory_sets.py (S20) [added, DEC-1101 (1), DEC-1125 (2)]
- DAEO-p8tv  # W2-172: the audit's driver and schedule rule (S18) [added, DEC-1101 (1), DEC-1125 (2)]
allowed_paths:
- src/gov/adopt/assess.py
- src/gov/adopt/refactor_plan.py
- src/gov/adopt/fabric.py
- src/gov/adopt/command.py
- src/gov/adopt/project.py
- src/gov/adopt/stages.py
- src/gov/rebuild/command.py
- src/gov/store/layout.py
- src/gov/store/loader.py
- docs/changes/W2-88-evidence.md  # its measurements and proof (a)'s record (DEC-996 (3) A; DEC-1150 (1))
- tests/unit/adopt/test_w2_88*
- tests/unit/rebuild/test_w2_88*
- docs/changes/W2-88-CIT-P.md
- src/gov/adopt/memory_sets.py  # [added, DEC-1099 (2)] the set tools: pre-flight, USED, resume, figures (its tests under tests/unit/adopt/test_w2_88*)
- docs/probes/DAEO-2bdu/**  # the probe record (the CTO, 2026-11-12)
kpis:
  success:
  - 'The assessment: before the target path map (A3), adoption writes a memory-assessment record for the repository. It holds tracked files and bytes, languages, commits, the largest files, binaries, generated, minified and vendored candidates (by name, header and folder), the files the secrets filter refuses (by rule id, never the value), the files no route can take (a language the code graph does not read, a file over the chunker''s limit), and the estimated index time, peak RSS and disk against DEC-078''s envelope and the machine''s free memory and disk. It streams the tree and never loads it whole: on the largest proof repository its peak RSS is recorded and stays under the resource gate''s per-session figure. The repository''s tree, index and history are byte-identical before and after. Verify: on a planted repository (a vendored folder, a generated file, a minified file, a binary, a file over the chunker''s limit, a secret in a tracked file, a language the code graph does not read) the memory-assessment record is written before A3 and holds every field named above, each planted item under its category and the secret by rule id only (a grep of every output for the planted secret''s value finds 0 hits); a hash of the planted repository''s tree, index and history before and after is identical; on the largest proof repository the recorded peak RSS is under the resource gate''s per-session figure [DEC-954 Q9f, DEC-078, CAP-44.b]'
  - 'The refactoring plan: every blocker to full indexing that the assessment finds becomes a proposed ticket in the kernel''s ticket form (title, class, allowed paths, KPIs with success and failure, each KPI line with its `Verify:` clause [changed, DEC-1132 (2)], profile, sources citing the assessment) in the adoption''s evidence folder. Blockers include: vendored or generated code with no folder of its own, a namespace that would need a value other than embedded or not embedded, files over the chunker''s limit, a secret in a tracked file, and paths that would fall in no namespace or in two. No proposal is created with tk, applied or committed by the tool; the A5 human gate is the only route to them. A repository with nothing to refactor gets a record that says so. Verify: a planted repository with one case of each blocker kind yields, in the adoption''s evidence folder, one proposed ticket per blocker in the kernel ticket form (title, class, allowed paths, KPIs with success and failure, profile, sources citing the assessment); `tk` ticket list and `git status` of the planted repository are the same before and after; a planted clean repository''s record says there is nothing to refactor [DEC-954 Q9f, DEC-694, DEC-388, CAP-44.g]'
  - 'The full index and the embeddings (A9 lite, after A6 and the owner''s approval of the path map): the stage builds the record store, the lexical index, the semantic vectors for every embedded namespace and the code graph, with one rebuild at a time on the machine (W2-76''s lock). Its record holds, per store: files judged, indexed and refused with the reason, chunks, vectors, nodes and edges, time and peak RSS. Every tracked file is either indexed or named with its reason (secrets filter, binary, namespace not embedded, unsupported language); a file in neither list fails the stage. Verify: a planted adoption run through A9 lite writes a record holding, per store, files judged, indexed and refused with the reason, chunks, vectors, nodes and edges, time and peak RSS; every planted tracked file is in the indexed list or the named list with its reason; a planted file in neither makes the stage not ok; a second rebuild started while one runs is refused by W2-76''s lock [DEC-954 Q9f, CAP-44.f (A9, lite, by CIT-P note), CAP-17, CAP-20]'
  - 'The structure: the store layout is stated once, in src/gov/store/layout.py: each store file, its tables and a layout version. The stage builds that layout, and the rebuild record carries a digest per store (the record graph, the lexical index, the vectors and the code graph), not only the record graph''s. A store of another layout version is rebuilt, never read as current. Two A9 runs on one commit give the same per-store digests, apart from the code graph''s bytes, which are reported, not compared. Verify: a grep of src/gov/store/layout.py finds the layout version and each store file with its tables; a planted adoption''s rebuild record holds four digests (record graph, lexical index, vectors, code graph); a planted store of another layout version is rebuilt and never read as current; two A9 runs on one planted commit print equal digests for the first three stores and report the code graph''s bytes without comparing them [DEC-954 Q9c, CAP-20, DEC-016]'
  - 'Scale: on each synthetic proof repository (proof (a); the real ones are W2-88b''s) the stage records the query time of one plain question on each route, and the vector scan''s time against the retrieve budget. A figure over the budget or over DEC-078''s envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan''s time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store''s files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]'
  - 'Memory works there, measured: on each synthetic proof repository (proof (a)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN''s copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61''s measure; each real repository has its 10 questions with the writer''s and checker''s records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]'
  - 'The proofs, recorded in docs/changes/W2-88-evidence.md (the implementer''s evidence, DEC-996 (3) A; the real repositories'' proofs (b) and (c) are W2-88b''s, DEC-1150 (1)), each with its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure: Verify: docs/changes/W2-88-evidence.md holds a section for proof (a) and one for (d), and (a) names its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from the section finds none'
  - '  (a) W2-81''s five synthetic repositories (Python with drifted specs, a Rust workspace, a TypeScript monorepo, legacy documents with large files, a secret in history), built by W2-81''s builders under ~/gov-os-runs/W2-88/proving-ground/. Verify: the proof record has a section for each of the five synthetic repositories (Python with drifted specs, a Rust workspace, a TypeScript monorepo, legacy documents with large files, a secret in history), each with a commit; the builders'' output path is under ~/gov-os-runs/W2-88/proving-ground/ and `git status` of this repository shows none of it [DEC-941, DEC-954 Q9f]'
  - '  (d) EXAMIN''s copy is its live trial: W2-27 runs these tools on its clone at adoption, on W2-16''s release; that run is W2-27''s, not this ticket''s. Verify: this ticket''s proof record has no adoption run on EXAMIN''s copy and names W2-27 for it; a planted check of this ticket''s branch for a run of the adoption tools against ~/gov-os-workbench/examin/ finds none [DEC-954 Q9f, Q8c]'
  - 'A store of another layout version is never read as missing or as current: the store''s open path (src/gov/store/loader.py, through layout.py) reads the layout version and refuses an older or newer one with STORE_LAYOUT_STALE naming both versions, and gov rebuild rebuilds it; the main tree''s STORE_MISSING of 2026-10-30 (a store built before W2-03''s span column) is a planted case. Verify: a planted store of an older layout version and one of a newer: the open path prints STORE_LAYOUT_STALE naming both versions for each and `gov rebuild` rebuilds it; a planted store built before W2-03''s span column gives STORE_LAYOUT_STALE and never STORE_MISSING; a current store opens with no refusal [DEC-957, CAP-20]'
  - 'S10 The standard pinned at Wave 0: A9 lite builds and serves the store with Gov OS''s memory standard: Qwen3-Reranker-0.6B through the machine''s one shared reranker service (no private reranker), the pool on (retrieval.yaml''s pool: block as Gov OS ships it), the 6,000-token bundle with its items widened to their sections, and the gov pin, the embedder, the reranker and the retrieval.yaml digest written in the A9 record. Any setting that differs from the standard is named in the record, and the stage is not ok unless the record cites the owner''s decision id for it. Verify: on a planted adoption the A9 record names the four settings and the pin; a planted retrieval.yaml with the pool off, a second reranker or another bundle budget is named, and the result is not ok without a decision id [DEC-1098 (1), DEC-1097 (1)(a), DEC-1097 (5), DEC-1046 (1)] [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'S11 The store current after every merge: adoption installs the refresh that this repository runs (practice record §7): after each update of the repository''s integration branch the store is rebuilt by the pinned code, double-buffered, so a failed build leaves the last good store in service; a daily backstop runs; every bundle names the commit its store was built at. Verify: on a planted repository, a merge followed by a query returns the new commit within the time the proof measured for a seeded rebuild; a planted failing build keeps the old store and reports the failure [DEC-1098 (1), DEC-1072 (2)] [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'S12 The repository''s own tuning set: about 80 questions, written blind under the rubric (docs/research/memory-measure-audit/RUBRIC.md, its version in force) by an independent writer, and cross-checked by an independent checker in at most two rounds. The checker lists every other place that states each answer. Both are sessions outside the retrieval work, opened by the owner''s operator. The writer never reads search results and never finds gold with the product''s search. The categories follow the fresh 80''s twelve (callers, code paraphrase, exact string, multi-file, decision, ticket, plan, contract or spec, kernel or template, history, failure memory, nonexistent id), mapped to the repository''s own domains. A category the repository has no domain for is dropped, and the drop is recorded. R5 applies: each domain at least 10 %, no subsystem over 25 %. There is at least one nonexistent-id question, scored apart. The set is split into two halves of 40: the first is used to choose fixes; the second is reported in counts only and never chooses. Source families (official copies) are declared in the path map. Verify: the set''s checks in the proof record (path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS) [DEC-1098 (1), DEC-1070 (2)-(3), DEC-1074 (4), DEC-1069 (5), DEC-1076 (5), DEC-1078 (4), DEC-1071 (5), DEC-1010] [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'S13 The fresh verdict set, used once: 80 questions, written by the same independent writer and checker under the same rubric, blind, before the first measure of the tuning set. None of its gold sources is a gold source of the tuning set. It is held outside every worktree in a folder of mode 700, declared in the path map''s evaluation_sets with every role but the orchestrator refused, and the guard refuses the measured roles a read of the set and of its run folder (as ACT-GUARD-SETS-1). It is used once, as FRESH-80-1 did. First a counts-only pre-flight: the set''s digest, how its anchors resolve at the measured commit, and whether each nonexistent id still exists nowhere. Then the checker''s staleness pass at that commit. Then a declaration, committed before any search, naming the configuration (S10), the commit, the denominator with nonexistent-id questions apart, the bar and how it rounds (S14), any data conditions as data only, and the fault rule (FRESH-80-1 §3.5). Then a control on the tuning set. A USED marker is written before the first search, and the runner refuses to start once it exists. The result record gives counts only. Verify: the declaration''s commit is earlier than the USED marker; a planted USED makes the runner refuse; a planted read of the set by a measured role is refused by the guard [DEC-1098 (1), DEC-1097 (1)(b), (1)(g), DEC-1097 (2), DEC-1092 (4), DEC-1078 (3), DEC-1074 (1)] [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'S14 The bar: on the verdict set, judged on the declared configuration only. The figure is right end to end: the answer correct and its citation right, graded by a named grader model, with a second grader''s agreement reported. It must be at least 85 % with wrong claims at most 5 %; the target is 95 %. On n judged questions that is at least ceil(0.85 n) right and at most floor(0.05 n) wrong claims. Reported beside it, never judged: hit@5, gold in the first bundle, the answer correct with the citation set aside, the stricter grade, one search against two (exact McNemar), the exact 95 % interval, and the reader model by name. Verify: the result record in docs/research/W2-88-any-repository.md (or the adopted repository''s copy of it) holds the verdict line and the side table [DEC-1097 (1)(d), DEC-1098 (1), DEC-957, CAP-10, DEC-1079] [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'S15 Search again once in the adopted repository: adoption copies, unchanged, the kernel''s retrieval skill with step 7 (W2-142 S1), the discovery skill''s line (W2-142 S2) and T-0''s and T-8''s "Search again once" line (W2-128''s line). Nothing is re-worded per repository. The verdict''s judged condition is up to two searches (A2). Verify: a string test on a planted adoption''s generated skill and T-0 for "search again once", "own, different words", "not found" and "two searches" [DEC-1098 (1), DEC-1094 (2), DEC-1092 (1)] [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'S16 A miss is a result. A verdict below either limit stands as recorded. It is never run again, never re-scored to pass, and its labels are never changed after its figures exist. The spent set becomes a diagnostic set. An independent auditor classifies its misses by kind, counts only: never retrieved, ranked low, vocabulary, correct answer citing an unlisted place, other. The result goes to the repository''s owner with options: structural fixes judged on the tuning set and then a new fresh set used once, or the figure accepted as a named residual with its cause. The store stays in service. The four settings of S10 change only by Gov OS''s owner''s decision (a CIT-P), never at the adopted repository. Verify: the result record''s miss section on a planted miss (stand-in figures); the runner refuses a set marked USED [DEC-1098 (1), DEC-1074 (1)-(2), DEC-1071 (1), DEC-1083 (2), DEC-954 Q9e, DEC-1070 (14)] [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'S18 The audit''s schedule at adoption: an adopted repository is audited on the same rhythm by the same tool (weekly while active, monthly once stable, by W2-172''s rule). Adoption writes the repository''s audit record: its sets root, its audit names, its mode, the three briefs'' variant ids and their sha256, and the first audit''s earliest date. It starts no audit and installs no schedule line itself (the crontab is an ACT). Verify: a planted adoption writes the record with those fields; a grep of the planted crontab and sets root before and after finds no change [DEC-1101 (1)-(2), DEC-1125 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'
  - 'S19 The briefs'' variants, approved once: the adopted repository''s writer, checker and auditor briefs are the Gov OS briefs (`governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/`, once approved) with two parts replaced by the repository''s own: the domain table (the writer''s section 5 items 1 and 3, the checker''s section 5a) mapped from S12''s twelve categories to the repository''s domains, with every dropped category recorded, and the list of records the audit stays blind to. Nothing else changes. Each variant is approved once by the repository''s owner and hashed; a launch under an unapproved variant is refused. Verify: a planted adoption''s variants differ from the Gov OS briefs only in those two parts (a diff test); a launch under a variant not on the planted approved list exits 10 [DEC-1101 (2), DEC-1099 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'
  - 'S20 One core, not two: `src/gov/adopt/memory_sets.py` calls `gov.memaudit` (W2-170''s checks and declaration, W2-171''s measure and pool) and defines no pre-flight, use-once marker or figures of its own. Verify: a test that the module imports from `gov.memaudit` and defines none of those functions; S12''s and S13''s planted runs produce the same declaration and verdict line as the audit''s [DEC-1101 (1), DEC-1099 (2), DEC-1125 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'
  - 'S21 The first scheduled audit follows the verdict set: an adopted repository''s first scheduled audit runs only after its verdict set (S13) was used and its result record written; the audits'' log starts at the verdict set''s commit (`gov.memaudit baseline`), and the tuning and verdict sets join the repository''s pool. Verify: a planted adoption before S13''s USED marker: `due` says `not due: no verdict set used`; after it: the baseline line holds the verdict commit [DEC-1101 (1), DEC-1098 (1)] [added, DEC-1101 (1), DEC-1125 (2)]'
  - 'S22 The walls for an adopted repository by one ACT: adoption writes one ACT package for the repository''s owner''s operator: the walls'' template copy, the sets root folder (mode 0700), the approved list with the three variant briefs, and the path-map hidden globs. Adoption never applies it. Verify: a planted adoption writes the package and changes nothing in the planted sets root or path map [DEC-1101 (2)-(3), DEC-1099 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'
  - 'S23 The audit''s cost is stated at adoption: the adoption record gives, for the repository''s set size, the estimated tokens and USD per audit, the GPU minutes and the owner''s minutes, from `governance/project/orchestration/packages/MEMORY-AUDIT-1.md` section 7, and names the figure to replace once the first audit has measured them. Verify: a string test on a planted adoption record for the four figures [DEC-1101 (3)] [added, DEC-1101 (1), DEC-1125 (2)]'
  failure:
  - 'Anything written, moved, committed or deleted in a repository by the assessment or the refactoring plan; a proposed ticket created with tk or applied without the owner. Verify: a hash of a planted repository''s tree, index and history and its `tk` ticket list before and after the assessment and the plan are identical; no tk create or apply call appears in the call log; any difference is a failure'
  - 'A tracked file neither indexed nor named with its reason; a store not built reported ok. Verify: a planted tracked file left out of both lists makes the stage not ok; a planted adoption where a store the path map calls for was not built never prints ok'
  - 'A store of another layout version read as current; a rebuild record whose only digest is the record graph''s. Verify: a planted store of another layout version is refused with STORE_LAYOUT_STALE, never opened as current; a planted rebuild record is checked for the four per-store digests and is refused if only the record graph''s is present'
  - 'The assessment loading the whole tree in memory, or exceeding the resource gate''s per-session figure on the largest proof repository. Verify: the assessment''s recorded peak RSS on the largest proof repository is under the resource gate''s per-session figure, and a test on a planted large tree shows the memory growing with the largest file, not with the tree''s size'
  - 'A secret''s value in any record, log or output; a hidden question read or printed. Verify: a grep of every record, log and output of a planted run for the planted secret''s value finds 0 hits; the guard''s log of the run holds no read of a hidden question and a grep of the outputs for a planted hidden question''s unique word finds 0 hits [re-worded, DEC-1084]'
  - 'A verdict set read by a measured role, measured twice, or used to choose anything; a declaration committed after the first search. Verify: a planted read of the set by a measured role is refused by the guard; a planted USED marker makes the runner refuse a second measure; the declaration''s commit is earlier than the first search in the ledger; the tuning set''s fixes cite no verdict question [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'A store served with a setting other than the standard''s and no decision id in the A9 record. Verify: a planted retrieval.yaml with the pool off, a second reranker or another bundle budget and no decision id in the A9 record makes the stage not ok and the setting is named [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'A tuning or verdict question written with the product''s own search, or by a session in the retrieval work. Verify: the writer session''s log holds no call of the product''s search and the writer''s session id is not among the retrieval work''s sessions; a planted question whose record names a search call or a retrieval-work session is refused by the checker [added, DEC-1099 (2); DEC-1098 (1)]'
  - 'An audit started by adoption; a variant brief launched without the repository owner''s approval; a second copy of the pre-flight, the use-once marker or the figures in `src/gov/adopt/`. Verify: a planted adoption leaves the audits'' log and the crontab unchanged and starts no audit process; a launch under a variant brief not on the planted approved list exits 10; a grep of src/gov/adopt/ finds no definition of the pre-flight, the use-once marker or the figures outside the import from gov.memaudit [added, DEC-1101 (1), DEC-1125 (2)]'
  moved:
  - 'A store not built is never ok: gov rebuild on a repository where the path map or .gitleaks.toml is missing, or where a store the path map calls for was not built, names each store not built with its reason, and its result is not ok. A rebuild with --no-embeddings stays ok for the vectors it was told not to build, and says so. W2-26''s finding 2 is a planted case [DEC-954 Q9f, W2-26 finding 2, DEC-530] [moved to W2-124, DEC-1083] (was S5)'
profile: FULL
sources:
- DEC-954
- DEC-953
- DEC-078
- DEC-071
- DEC-630
- DEC-718
- DEC-723
- DEC-728
- DEC-388
- DEC-694
- DEC-530
- DEC-833
- DEC-860
- DEC-941
- DEC-105
- CAP-44
- CAP-17
- CAP-20
- CAP-10
- CAP-19
- DEC-957
- CAP-44.b
- CAP-44.f
- CAP-44.g
- DEC-016
- DEC-1083
- DEC-1084
- DAEO-mb2t
- DAEO-2ds6
- DEC-1098
- DEC-1099
- DEC-1097
- DEC-1072
- DEC-1071
- DEC-1070
- DEC-1074
- DEC-1092
- DEC-1094
- CAP-33
- DEC-1010
- DEC-1046
- DEC-1069
- DEC-1076
- DEC-1078
- DEC-1079
- DEC-1101
- DEC-1125
- DEC-315
- DEC-1112
est_loc: 750  # [changed, DEC-1099 (2)] was 500 (W2-88-STANDARD-1 §4)
acceptance_tests:
  path: tests/acceptance/W2-88/
  author: 'independent-test-designer (MR-3); written before implementation. Small repositories are planted in temporary folders (a vendored folder, a generated file, a file over the chunker''s limit, a secret in a tracked file, a path with no namespace, a binary, a language the code graph does not read), W2-81''s builders are reused read-only, and stand-ins are used for the embedder and the code graph where a case needs none. No network, no real clone and never this repository''s store. This designer writes the planted cases (S10, S11, S13, S15 to S17) and chooses and pins the two GitHub repositories. The question sets (S12, S13 and the 10 questions per real repository) belong to the independent writer and checker, sessions outside the system opened by the owner''s operator [changed, DEC-1099 (2)]'
track: A
list_rows: []
waits_on:
- 'DAEO-qskx — W2-142: S15 copies the retrieval skill''s step 7 and the discovery skill''s line [added, DEC-1099 (2)]'
- 'DAEO-t8mp — W2-128: S15 copies T-0''s and T-8''s "Search again once" line [added, DEC-1099 (2)]'
- 'DAEO-f58b — W2-116: S11''s refresh after every merge, double-buffered [added, DEC-1099 (2)]'
- 'DAEO-2tfd — W2-145: S10 needs no private reranker beside the shared service [added, DEC-1099 (2)]'
---
# W2-88 Memory for any repository

**DEC-957 (2026-10-30):** this ticket also closes MEMORY-SPEC-MAP gaps 4 (the store layout, with the STORE_MISSING cause) and 5 (the large-repository measure, its Scale KPI). `src/gov/store/loader.py`'s open path is added for the layout check (W2-03 is merged and closing: split by function). The mapping of a query failure to STORE_MISSING in `retrieve.py` (W2-87's file) is named for the retrieval tickets if the open-path check does not make it unreachable.

Card: from the owner's DEC-954 Q9f (2026-10-30): "Memory for any repository, not only this one: if we build memory that only this repository can use, we have built nothing." It is in Wave 2's minimum. The tools assess any repository at adoption, however large; plan any refactoring it needs for full indexing as governed tickets, for the repository's owner to approve and never applied on their own; build the full index and the embeddings; and set up the database structure (SQLite and the vector store), so memory works there.

- **Why no existing ticket covers it** (checked):
  - **Adoption** (`src/gov/adopt/`, W1-39 and W1-41) runs A0 to A6 and A8. It has no knowledge-fabric stage: CAP-44.f's A9 is Wave 3 in the Contract.
  - **W2-52** writes the lite A7 and A10 records: verification, not building.
  - **W2-23** is adoption safety (rollback, adapters, paths with spaces).
  - **W2-81** builds synthetic repositories and judges an adoption's outputs. It builds no index.
  - **W2-27** is the integration run on EXAMIN's copy.
  - **W2-26's finding 2:** `gov rebuild` on an unadopted clone builds nothing and says ok.
  - **W2-86 and W2-87** change this repository's path map and ranking only.
  - So this is a new ticket, not a change to an existing one. The nearest, W2-52, keeps its scope: verification records. It holds `stages.py` and the adopt skill, so it merges first.
- **The Contract:** A9 lite comes into Wave 2 by a CIT-P note under DEC-105 option (a): apply now, as the owner decided in DEC-954 Q9f. `docs/changes/W2-88-CIT-P.md` holds the note, and the lead returns it as a package before the engineer starts. It also covers the adopt skill's A9 step: a kernel skill change, under CAP-33.
- **Profile FULL, not STANDARD:**
  - it changes adoption, a path where a fault loses an owner's work: the plan must never apply;
  - it changes what `gov rebuild` reports as ok, which is a fail-open fix;
  - it adds a stage the verdict reads.
- **Where it sits:**
  - stream S1 (memory), proven in S4's proving ground;
  - it closes before W2-27, which is its live trial and depends on it (DEC-954);
  - W2-15b's final measure on EXAMIN's clone and `~/workspace` uses it.
- **Overlaps, split by file:**
  - **W2-52** (`DAEO-siiz`, held) holds `src/gov/adopt/stages.py`, `lite_gates.py` and the adopt skill. It merges first (a dependency). This ticket changes `stages.py`'s stage list and the A9 call only, and the skill's A9 step only.
  - **W2-23** (`DAEO-kmcr`, open) holds `src/gov/adopt/**` and `src/gov/adapters/**`. This ticket's new modules are files of its own; whichever merges second merges back.
  - **W2-76** (`DAEO-tgk2`, finishing) holds `src/gov/rebuild/**`. It merges first (a dependency). This ticket changes the result's `ok` line only.
  - **W2-06** (`DAEO-kia7`, open) holds `src/gov/rebuild/**` too; it is split by line, and the second to merge merges back.
  - **W2-03** (`DAEO-ym8a`, merged, closing) holds `src/gov/store/**`. `layout.py` is new; the loader is read, not changed.
  - **W2-13 and W2-32** hold `src/gov/retrieval/**`: not touched. The vector store's possible change is a proposal, not this ticket's.
  - **W2-81** (`DAEO-l78m`) holds `tests/acceptance/W2-81/**`. Its builders and question sets are read and run, never edited.
- **Est.:** 500 LOC:
  - the assessment, about 150;
  - the plan, about 120;
  - A9 lite, about 150;
  - the layout, about 60;
  - the glue and the rebuild line, about 20.
  
  Scaled as the plan's §2.0 (W2-66's 400 LOC took 13.1 h; W2-67's 750 took 18.8 h): about 15 lead-hours to build, plus 5 to 10 h for the real runs. Embedding a repository of the order of 10^4 files on this machine is unmeasured: this repository's 2,521 files took 7 to 45 min. **Est. 20–26 lead-hours.**
- **Network:**
  - The two GitHub clones are made by the lead or the CTO, whose sessions have the network. Sandboxed workers have none.
  - The clones are exact-path folders under `~/gov-os-runs/W2-88/` (DEC-728), never under this repository.
  - Nothing of them is committed: only counts, ids, digests and figures go into `docs/research/W2-88-any-repository.md`.
- **Test repository paths the register names** (searched in `docs/DECISION_REGISTER.md`):
  - **`~/workspace`:** DEC-078's scale probe (1,005 files indexed then, 77,346 nodes, 270,647 edges, 2.2 GB peak RSS) and DEC-718's EXP-003 corpus. It has 1,467 tracked files today. **Used.**
  - **`~/gov-os-workbench/synthetic/`:** the dev tiers, a-dev (ORION) and b-dev (ARGUS), 150 and 149 tracked files (DEC-071, DEC-630 `GOV_DEV_TIERS`). **Used.** `customer-dev` sits beside them, with no tracked files.
  - **ARGUS's stress tier (×4: 5,355 files, 57,777 chunks; DEC-071):** its location is unconfirmed. **Used only if it is outside** `~/gov-os-workbench/qualification-oracle/`; that path and the qual tiers are held out (DEC-067, DEC-425, DEC-426) and are **never used**.
  - **`~/gov-os-workbench/examin/`:** the owner's copy of EXAMIN (DEC-723). **The assessment only**, on a clone. Adoption is W2-27's.
  - **`~/EXAMIN APP`:** the real repository (DEC-078, DEC-718). **Never touched here.** It is written only by W2-29, after W2-25, W2-15b and the owner's go (DEC-727).
  - **`~/gov-b2-throwaway`:** DEC-668's throwaway copy of a-dev-exit. **Deleted; not available.**
  - **`~/gov-os-workbench/archive/w1-42-exit-clones/`:** W1-42's adopted exit clones (DEC-673). They are backups, read-only. **Not needed:** a-dev and b-dev cover them.
- **What it does not do:**
  - It applies no refactoring.
  - It builds no indexed vector store (a proposal if the scale figures call for one).
  - It adds no graph route to plain-question retrieval (MEMORY-SPEC-MAP gaps 2 and 3).
  - It writes no question for W2-81's or EXAMIN's hidden halves (gaps 6 and 7).

## The memory-building practice (DEC-1072 (2), 2026-11-04)
- **Memory-building is a Gov OS practice for every adopted repository's Wave 0,** and this ticket owns it. The
  practice learned in D-4b is recorded in `docs/research/W2-88-memory-practice.md`, kept up to date as D-4b goes, and
  becomes a kernel skill after the refactoring. The record holds:
  - how the store is built;
  - how it is measured (the rubric, the three sets and their jobs, independent writers, the hidden-half rule,
    scoring);
  - how it is tuned (structural fixes only, judged on all sets, consistency as the proof);
  - every method tried, with its figures;
  - the lessons.
- **What it adds to this ticket's work:**
  - A9's index follows the record's section 6:
    - a census of the repository's stated links before the graph is built;
    - chunking by meaning, with the heading path given to every reader;
    - the three sets by independent writers.
  - The question sets follow the rubric: see the memory standard below. [changed, DEC-1099 (2)]
- **The KPIs are amended by DEC-1099 (2):** see the memory standard below. A KPI change goes through this ticket's test designer. [changed, DEC-1099 (2)]

## The memory standard (DEC-1098 (1), DEC-1099 (2), 2026-11-09)
- **The lines:** S10 to S17 and three failure lines, from `governance/project/orchestration/packages/W2-88-STANDARD-1.md`
  §2 as written; "Memory works there", proof (b), `acceptance_tests.author`, `est_loc` and this body changed per its §3.
- **The owner's answers (DEC-1099 (2)):**
  - (1) S10 to S17 and the three failure lines as written.
  - (2) (c): EXAMIN's copy at W2-27 is the practice's first full run, with no separate proof repository. What goes
    wrong there is fixed, and the repositories adopted after EXAMIN follow the practice as fixed.
  - (3) (a): the tuning set is 80 questions in two halves of 40; the second reports in counts only and never chooses.
  - (4) The writer and checker are sessions outside the system, opened by the owner's operator.
  - (5) The set tools (`src/gov/adopt/memory_sets.py`) and the practice record
    (`docs/research/W2-88-memory-practice.md`) are in this ticket's `allowed_paths`.
  - (6) The nonexistent-id row is its own ticket (W2-146). Until it lands, S12 and S14 score that question on the
    reader's "not found", apart from the bar (W2-88-STANDARD-1 §5).
- **Waits:** W2-142 and W2-128 (S15) and W2-116 (S11), in `waits_on`. S10 also waits on W2-145 (`DAEO-2tfd`, no
  private reranker), which is kept out of `waits_on` for now: W2-145 and W2-137 (`DAEO-5emz`) each need a file the
  other writes (`src/gov/retrieval/rerank.py`), `gov plan`'s one cycle, and with W2-145 in `waits_on` the plan's
  tiebreak orders W2-27 before W2-88 (measured 2026-11-09). It goes into `waits_on` when that cycle is gone.
- **Est.:** about 750 LOC (+250: the set tools, S10's check, the skill step). W2-88-STANDARD-1 §4 gave 30 to 38
  lead-hours with one full practice run; under answer (2)(c) that run is W2-27's, so this ticket's share is less by it.

[DEC-1099 (2), DEC-1098 (1)]

## Split by the owner (DEC-1150 (1), package 1 (a), 2026-11-12; DEC-996 (1))

This ticket keeps the code (engineer). Moved word for word: S17 (the adopt skill's order) and its kernel skill paths to **W2-88a** (DAEO-pg6i, product-spec, with W2-174's skill line); proofs (b) and (c), their scale and measure lines and the GitHub-clone failure line to **W2-88b** (DAEO-aks1, research, copies only). Proof (a)'s record moves to `docs/changes/W2-88-evidence.md`; the practice record `docs/research/W2-88-memory-practice.md` goes with the skill text to W2-88a. W2-27 depends on this ticket's tools, not on W2-88b.

## Interface (DEC-1052; P-W2-88-IF-1 (a), the CTO's delegated decision, DEC-1112 (3), 2026-11-12 23:25)


### Commands and stages
1. **`gov adopt --lite --stage MA --out <folder>`**: the memory assessment (S1) and the refactoring plan (S2). It is in no chain (like A7 and A10). `<folder>` must lie outside the project, or the stage refuses with `OUT_INSIDE_PROJECT`. It reads HEAD's blobs one at a time from git objects (`git cat-file --batch`). It writes only under `<folder>`:
   - `memory-assessment.json`: `commit`, `tracked_files`, `tracked_bytes`, `languages`, `commits`, `largest[]`, `binary[]`, `generated[]`, `minified[]`, `vendored[]` (each item `{path, by: name|header|folder}`), `secrets[]` as `{path, rule}` (never the value), `no_route[]` as `{path, reason: unsupported-language|over-limit}`, `estimate {index_seconds, peak_rss_bytes, disk_bytes, envelope, free_memory_bytes, free_disk_bytes}`, `peak_rss_bytes` (its own peak).
   - `refactor-plan/RP-<nn>-<kind>.md`: one per blocker, in the kernel ticket form. Frontmatter: `title`, `class`, `allowed_paths`, `kpis.success`, `kpis.failure` (each line ends with ` Verify: …`), `profile`, `sources: [memory-assessment sha256:<hex>]`. The kinds are `vendored-no-folder`, `generated-no-folder`, `namespace-policy`, `over-limit`, `secret`, `no-namespace` and `two-namespaces`.
   - `refactor-plan/PLAN.md` lists them. A repository with nothing to refactor gets `refactor-plan/NOTHING-TO-REFACTOR.md` instead.
   - No commit, no `tk` call, no write in the repository.
2. **A3 gains `--assessment <folder>`.** Without a `memory-assessment.json` for HEAD's commit, A3 refuses with `ASSESSMENT_MISSING`. A3's record cites the assessment's sha256 but copies no proposal.
3. **`gov adopt --lite --stage A9 --out <folder> [--decision DEC-n]…`** (A9 lite, S3–S6, S10, S11, S18–S23) follows A8 in `project.STAGES`' chain. It runs `gov.rebuild.command.run` in full under W2-76's lock and commits its record under `governance/adoption/`. The record holds:
   - `stores.<record|lexical|vectors|codegraph>`: `{judged, indexed, refused[{path, reason: secrets|binary|not-embedded|unsupported-language|over-limit}], chunks, vectors, nodes, edges, seconds, peak_rss_bytes}`;
   - `digests` (4, below);
   - `standard {reranker, reranker_service, pool, bundle_tokens, widen, gov_pin, embedder, retrieval_yaml_sha256, departures[{setting, value, decision}]}`;
   - `scale {routes{<route>: query_ms}, vector_scan_ms, budget_ms, envelope}`;
   - `measure {right_e2e, wrong_claims, hit_at_5, residuals[{name, cause}]}`;
   - `refresh {command, hook}`.

   The stage is not ok in two cases:
   - `FABRIC_INCOMPLETE`: a tracked file is in neither list, or a store the path map calls for was not built.
   - `STANDARD_DEPARTURE`: a setting differs from `fabric.STANDARD` and no `--decision` names it.

   A low measure is never a failure (no bar). A figure over the budget or over the envelope writes `<folder>/SCALE-PROPOSAL.md` (a CIT-P form) and changes no store file. Under `<folder>/memory-audit/` it writes:
   - `AUDIT-RECORD.json` (S18);
   - `briefs/` with the three variants (S19);
   - `ACT-WALLS/` (S22: the walls' template copy, the sets root spec (0700), the approved list, the hidden globs);
   - the cost block (S23).

   A9 starts no audit, writes no crontab line and applies no ACT. S11's refresh (`gov rebuild --integration <branch>`, W2-116) is installed through the same ACT package, never by the tool.

### Modules (each in this ticket's paths)
- `adopt/assess.py`: `assess(root: Path, out: Path) -> dict`. It holds the DEC-078 envelope constants and `FILE_LIMIT_BYTES`. "Over the chunker's limit" means a file over `FILE_LIMIT_BYTES` (1,048,576 B, proposed) or with a line over `chunking.READ_CHARS` (32,768). The languages the code graph reads come from `gov.codeintel` if it states them, else from `assess.CODE_GRAPH_SUFFIXES`, with its source. The per-session figure is read from `gov.resources.config` (`working_size_bytes`, 805,306,368 B by DEC-1149), never restated.
- `adopt/refactor_plan.py`: `plan(assessment: dict, path_map: dict | None, out: Path) -> dict`.
- `adopt/fabric.py`: `a9(run) -> dict`; `STANDARD = {reranker: "Qwen3-Reranker-0.6B", reranker_service: "shared", pool: <retrieval.yaml's pool: block as Gov OS ships it>, bundle_tokens: 6000, widen: "sections"}`. It reads the adopted repository's `governance/project/retrieval.yaml` and compares with the `gov.memaudit.declare` helpers (`pool_on`, `retrieval`, `gov_pin`).
- `adopt/memory_sets.py` (S18–S23) imports `gov.memaudit` (`preflight`, `declare`, `layout`, `figures`, `schedule`, `pool`). It defines no function or constant for a pre-flight, a USED marker or figures. It provides:
  - `audit_record(...)`;
  - `variants(...)` (only the domain table and the blind list differ);
  - `walls_act(...)`;
  - `cost(n_questions) -> {tokens, usd, gpu_minutes, owner_minutes, replace_after}`, from MEMORY-AUDIT-1.md §7;
  - `launch_check(variant: Path, approved: Path) -> int`, which returns 10 for a variant whose sha256 is not on the approved list (`python3 -m gov.adopt.memory_sets launch-check`).

  S21's `due` and `baseline` are `python3 -m gov.memaudit due|baseline` unchanged.
- `adopt/stages.py`, `project.py`, `command.py`: the stage ids `MA` and `A9`, A3's `--assessment`, and `--out` and `--decision`.

### The store layout (S4, S10, F3)
- `store/layout.py`:
  - `LAYOUT_VERSION = 2`;
  - `STORES = {record: {file: ".gov-runtime/store.db", tables: {...: columns}}, lexical: {file: ".gov-runtime/store.db", tables: lexical_*}, vectors: {file: ".gov-runtime/store.db", tables: semantic_*}, codegraph: {file: ".gov-runtime/codeintel/", tables: ()}}`;
  - `STAMP_TABLE = "store_layout"`;
  - `stamp(conn)`, `version_of(conn) -> int | None`, and `check(conn, path)`, which raises `GovError("STORE_LAYOUT_STALE", "<path>: store layout <found>, this gov reads <LAYOUT_VERSION>; run gov rebuild", {"found": n, "expected": LAYOUT_VERSION})`.
- Older and newer stamps are both stale.
- An **unstamped** store is stale (`found: 0`) when a table that `STORES` names is present without one of its columns. The planted case is the store from before W2-03's `register_entries.span`. Otherwise an unstamped store is read as current. Without this, the 35 test files that build a `store.db` by hand would go red outside this ticket's paths.
- `loader.load` stamps the store. `loader.connect` calls `layout.check` after its existing `STORE_MISSING` check, so a stale store never reports STORE_MISSING.
- `gov rebuild` replaces a stale store and says so (`layout: {found, expected, rebuilt: true}`).

### The rebuild's digests (S4, F3)
- `rebuild/command.py`'s result gains `digests: {record, lexical, vectors, codegraph_bytes}`. The first three are sha256s over the sorted rows of their tables. The code graph's bytes are reported, never compared. `digest` (the record graph's) stays as it is.
- `fabric.check_digests(record)` refuses `DIGESTS_INCOMPLETE` when any of the four is absent.
- No change to `rebuild`'s other `ok` rules (W2-124's).

### Not this ticket's code (tests read or plant them; none is built here)
- The guard's refusal of a measured role's read of a verdict set (ACT-GUARD-SETS-1, existing).
- S15's skill and T-0 text (copied by adoption; W2-142, W2-128, W2-88a).
- `retrieve.py`'s mapping of "no such table" to "the record store is missing": named for the retrieval tickets (W2-87's file) if `connect`'s check does not make it unreachable. `retrieve.py` reads the store through its own `_graph`, not `connect`.

## Options
- **(a) As above.** Cost: none beyond the ticket's estimate (750 LOC). Recommended.
- **(b) The stale check only in a new `layout.open_current(root)`, called by `gov rebuild` and the A9 stage, leaving `connect` unchanged.** Cost: S10's "the open path" holds only for those two callers; every other reader would still report STORE_MISSING or read the store as current (F3 is half met).
- **(c) Every unstamped store is stale.** Cost: about 35 test files outside this ticket's paths go red. That needs a widening, which this run may not ask for.

**Recommendation:** (a). **Confidence:** medium-high. The figures I could not pin from code are proposed and named for the engineer to confirm: `FILE_LIMIT_BYTES`, the retrieve budget's source and the code graph's language list. **Blocks:** the test design and everything after it (DEC-1052).

## Facts the CTO should know with it
- **Waits:** `waits_on` W2-142, W2-128 and W2-116 are `in_progress`, and so is W2-145. S15's string test needs W2-142's and W2-128's lines on integrate. S11 uses W2-116's `--integration` (its code is already on this branch). The test designer can write S15 and S11 now; their cases go red until those land.
- **The CIT-P:** DEC-1150 (1) gives "its CIT-P" (A9 lite into Wave 2, the skill step) to W2-88a, yet `docs/changes/W2-88-CIT-P.md` is still in this ticket's paths, and the body says the lead returns it before the engineer starts. Read with (a), A9 lite's Contract note is W2-88a's and this path stays unused unless the CTO says otherwise.

- **CIT-P:** `docs/changes/W2-88-CIT-P.md` stays in the paths but unused: the Contract CIT-P is W2-88a's (DEC-1150 (1)).
- **Three values for the engineer to confirm from the code** (proposals, not KPIs): the file-size limit (1 MiB or a line over `chunking.READ_CHARS`), where the retrieve budget comes from, and the code graph's language list.

## Interface additions (P-W2-88-TD-1, the CTO's delegated decision, DEC-1157 (3), (12), 2026-11-13 01:35)

- **R1 (b):** A3 refuses with `ASSESSMENT_MISSING` only when `--assessment` is given and holds no `memory-assessment.json` for HEAD's commit; a bare A3 runs as today and its record says `assessment: none`. "MA before A3" is carried by the adopt skill's order (W2-88a's S17). The case `test_i2_a3_without_an_assessment_for_head_refuses` loses its "no `--assessment` at all" half (a decided-behaviour revision, DEC-1156 (7)); S1's "before A3" holds on the skill's path.
- **P-1:** the engineer names, from the code, the retrieve budget's source (one of the three values it confirms) and A9's question-set input (e.g. `--questions <file>`, defaulting to W2-81's per-repository set); the test designer then adds the planted over-budget (S5) and low-measure (S6) cases.
- **P-2:** S15 is judged on `gov.memaudit`'s output here and on the record at W2-27; no new case.
- **P-3:** the real code-graph tool is not used in this suite; nodes and edges asserted present only, a named residual.
- **P-4 (a):** S3's "refused by W2-76's lock" reads "never two at once" (serialised: a second rebuild waits); and the unit seam `fabric.check_coverage(record, tracked)` raising `FABRIC_INCOMPLETE` for F2 (the case uses it instead of deleting store rows).
- **P-5 (a):** A9's `memory-audit/AUDIT-RECORD.json` carries `not due: no verdict set used` until the verdict set is used; W2-172's `due` is not changed.
- **P-6 (a):** the stage that installs the kernel today copies the retrieval skill and T-0; the engineer names it; if no existing stage copies the kernel skills, the lead returns that case as a package (it is not moved to W2-88a).
- **P-7:** F4 keeps its upper bound only.
- **P-8, P-9:** F6's tuning-set citation check and F8's checker are residuals for W2-27's first full run (and W2-170 for F8's checker); no case here, no new ticket.
- **P-10:** the engineer names the `retrieval.yaml` key for each `fabric.STANDARD` setting; the test designer aligns the plant in one narrow revision.
- **The seams the engineer names (P-1, P-4, P-10)** are recorded in the lead's return and in `docs/changes/W2-88-evidence.md` if it is in the paths; the CTO copies them into this section at the next commit.
