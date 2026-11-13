{
  "ticket": "DAEO-2bdu",
  "ticket_text": "---\nid: DAEO-2bdu\nstatus: in_progress\ndeps: [DAEO-ym8a, DAEO-siiz, DAEO-tgk2, DAEO-l78m, DAEO-q7lk, DAEO-61vm, DAEO-k1e2, DAEO-p8tv]\nlinks: []\ncreated: 2026-10-30T22:14:08Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-88\ntags: [wave-2, implementation, memory, adoption, full, examin-minimum]\nwbs_id: W2-88\ntitle: 'Memory for any repository: at adoption, assess any repository however large, plan the refactoring it needs for full indexing as governed tickets for its owner to approve (never applied on their own), build the full index and the embeddings, set up the SQLite and vector-store structure'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-ym8a\n- DAEO-siiz\n- DAEO-tgk2\n- DAEO-l78m\n- DAEO-q7lk\n- DAEO-61vm  # W2-170: the audit's set record and checks, called by memory_sets.py (S20) [added, DEC-1101 (1), DEC-1125 (2)]\n- DAEO-k1e2  # W2-171: the audit's measure and pool, called by memory_sets.py (S20) [added, DEC-1101 (1), DEC-1125 (2)]\n- DAEO-p8tv  # W2-172: the audit's driver and schedule rule (S18) [added, DEC-1101 (1), DEC-1125 (2)]\nallowed_paths:\n- src/gov/adopt/assess.py\n- src/gov/adopt/refactor_plan.py\n- src/gov/adopt/fabric.py\n- src/gov/adopt/command.py\n- src/gov/adopt/project.py\n- src/gov/adopt/stages.py\n- src/gov/rebuild/command.py\n- src/gov/store/layout.py\n- src/gov/store/loader.py\n- docs/changes/W2-88-evidence.md  # its measurements and proof (a)'s record (DEC-996 (3) A; DEC-1150 (1))\n- tests/unit/adopt/test_w2_88*\n- tests/unit/rebuild/test_w2_88*\n- docs/changes/W2-88-CIT-P.md\n- src/gov/adopt/memory_sets.py  # [added, DEC-1099 (2)] the set tools: pre-flight, USED, resume, figures (its tests under tests/unit/adopt/test_w2_88*)\n- docs/probes/DAEO-2bdu/**  # the probe record (the CTO, 2026-11-12)\nkpis:\n  success:\n  - 'The assessment: before the target path map (A3), adoption writes a memory-assessment record for the repository. It holds tracked files and bytes, languages, commits, the largest files, binaries, generated, minified and vendored candidates (by name, header and folder), the files the secrets filter refuses (by rule id, never the value), the files no route can take (a language the code graph does not read, a file over the chunker''s limit), and the estimated index time, peak RSS and disk against DEC-078''s envelope and the machine''s free memory and disk. It streams the tree and never loads it whole: on the largest proof repository its peak RSS is recorded and stays under the resource gate''s per-session figure. The repository''s tree, index and history are byte-identical before and after. Verify: on a planted repository (a vendored folder, a generated file, a minified file, a binary, a file over the chunker''s limit, a secret in a tracked file, a language the code graph does not read) the memory-assessment record is written before A3 and holds every field named above, each planted item under its category and the secret by rule id only (a grep of every output for the planted secret''s value finds 0 hits); a hash of the planted repository''s tree, index and history before and after is identical; on the largest proof repository the recorded peak RSS is under the resource gate''s per-session figure [DEC-954 Q9f, DEC-078, CAP-44.b]'\n  - 'The refactoring plan: every blocker to full indexing that the assessment finds becomes a proposed ticket in the kernel''s ticket form (title, class, allowed paths, KPIs with success and failure, each KPI line with its `Verify:` clause [changed, DEC-1132 (2)], profile, sources citing the assessment) in the adoption''s evidence folder. Blockers include: vendored or generated code with no folder of its own, a namespace that would need a value other than embedded or not embedded, files over the chunker''s limit, a secret in a tracked file, and paths that would fall in no namespace or in two. No proposal is created with tk, applied or committed by the tool; the A5 human gate is the only route to them. A repository with nothing to refactor gets a record that says so. Verify: a planted repository with one case of each blocker kind yields, in the adoption''s evidence folder, one proposed ticket per blocker in the kernel ticket form (title, class, allowed paths, KPIs with success and failure, profile, sources citing the assessment); `tk` ticket list and `git status` of the planted repository are the same before and after; a planted clean repository''s record says there is nothing to refactor [DEC-954 Q9f, DEC-694, DEC-388, CAP-44.g]'\n  - 'The full index and the embeddings (A9 lite, after A6 and the owner''s approval of the path map): the stage builds the record store, the lexical index, the semantic vectors for every embedded namespace and the code graph, with one rebuild at a time on the machine (W2-76''s lock). Its record holds, per store: files judged, indexed and refused with the reason, chunks, vectors, nodes and edges, time and peak RSS. Every tracked file is either indexed or named with its reason (secrets filter, binary, namespace not embedded, unsupported language); a file in neither list fails the stage. Verify: a planted adoption run through A9 lite writes a record holding, per store, files judged, indexed and refused with the reason, chunks, vectors, nodes and edges, time and peak RSS; every planted tracked file is in the indexed list or the named list with its reason; a planted file in neither makes the stage not ok; a second rebuild started while one runs is refused by W2-76''s lock [DEC-954 Q9f, CAP-44.f (A9, lite, by CIT-P note), CAP-17, CAP-20]'\n  - 'The structure: the store layout is stated once, in src/gov/store/layout.py: each store file, its tables and a layout version. The stage builds that layout, and the rebuild record carries a digest per store (the record graph, the lexical index, the vectors and the code graph), not only the record graph''s. A store of another layout version is rebuilt, never read as current. Two A9 runs on one commit give the same per-store digests, apart from the code graph''s bytes, which are reported, not compared. Verify: a grep of src/gov/store/layout.py finds the layout version and each store file with its tables; a planted adoption''s rebuild record holds four digests (record graph, lexical index, vectors, code graph); a planted store of another layout version is rebuilt and never read as current; two A9 runs on one planted commit print equal digests for the first three stores and report the code graph''s bytes without comparing them [DEC-954 Q9c, CAP-20, DEC-016]'\n  - 'Scale: on each synthetic proof repository (proof (a); the real ones are W2-88b''s) the stage records the query time of one plain question on each route, and the vector scan''s time against the retrieve budget. A figure over the budget or over DEC-078''s envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan''s time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store''s files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]'\n  - 'Memory works there, measured: on each synthetic proof repository (proof (a)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN''s copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61''s measure; each real repository has its 10 questions with the writer''s and checker''s records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]'\n  - 'The proofs, recorded in docs/changes/W2-88-evidence.md (the implementer''s evidence, DEC-996 (3) A; the real repositories'' proofs (b) and (c) are W2-88b''s, DEC-1150 (1)), each with its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure: Verify: docs/changes/W2-88-evidence.md holds a section for proof (a) and one for (d), and (a) names its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from the section finds none'\n  - '  (a) W2-81''s five synthetic repositories (Python with drifted specs, a Rust workspace, a TypeScript monorepo, legacy documents with large files, a secret in history), built by W2-81''s builders under ~/gov-os-runs/W2-88/proving-ground/. Verify: the proof record has a section for each of the five synthetic repositories (Python with drifted specs, a Rust workspace, a TypeScript monorepo, legacy documents with large files, a secret in history), each with a commit; the builders'' output path is under ~/gov-os-runs/W2-88/proving-ground/ and `git status` of this repository shows none of it [DEC-941, DEC-954 Q9f]'\n  - '  (d) EXAMIN''s copy is its live trial: W2-27 runs these tools on its clone at adoption, on W2-16''s release; that run is W2-27''s, not this ticket''s. Verify: this ticket''s proof record has no adoption run on EXAMIN''s copy and names W2-27 for it; a planted check of this ticket''s branch for a run of the adoption tools against ~/gov-os-workbench/examin/ finds none [DEC-954 Q9f, Q8c]'\n  - 'A store of another layout version is never read as missing or as current: the store''s open path (src/gov/store/loader.py, through layout.py) reads the layout version and refuses an older or newer one with STORE_LAYOUT_STALE naming both versions, and gov rebuild rebuilds it; the main tree''s STORE_MISSING of 2026-10-30 (a store built before W2-03''s span column) is a planted case. Verify: a planted store of an older layout version and one of a newer: the open path prints STORE_LAYOUT_STALE naming both versions for each and `gov rebuild` rebuilds it; a planted store built before W2-03''s span column gives STORE_LAYOUT_STALE and never STORE_MISSING; a current store opens with no refusal [DEC-957, CAP-20]'\n  - 'S10 The standard pinned at Wave 0: A9 lite builds and serves the store with Gov OS''s memory standard: Qwen3-Reranker-0.6B through the machine''s one shared reranker service (no private reranker), the pool on (retrieval.yaml''s pool: block as Gov OS ships it), the 6,000-token bundle with its items widened to their sections, and the gov pin, the embedder, the reranker and the retrieval.yaml digest written in the A9 record. Any setting that differs from the standard is named in the record, and the stage is not ok unless the record cites the owner''s decision id for it. Verify: on a planted adoption the A9 record names the four settings and the pin; a planted retrieval.yaml with the pool off, a second reranker or another bundle budget is named, and the result is not ok without a decision id [DEC-1098 (1), DEC-1097 (1)(a), DEC-1097 (5), DEC-1046 (1)] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'S11 The store current after every merge: adoption installs the refresh that this repository runs (practice record \u00a77): after each update of the repository''s integration branch the store is rebuilt by the pinned code, double-buffered, so a failed build leaves the last good store in service; a daily backstop runs; every bundle names the commit its store was built at. Verify: on a planted repository, a merge followed by a query returns the new commit within the time the proof measured for a seeded rebuild; a planted failing build keeps the old store and reports the failure [DEC-1098 (1), DEC-1072 (2)] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'S12 The repository''s own tuning set: about 80 questions, written blind under the rubric (docs/research/memory-measure-audit/RUBRIC.md, its version in force) by an independent writer, and cross-checked by an independent checker in at most two rounds. The checker lists every other place that states each answer. Both are sessions outside the retrieval work, opened by the owner''s operator. The writer never reads search results and never finds gold with the product''s search. The categories follow the fresh 80''s twelve (callers, code paraphrase, exact string, multi-file, decision, ticket, plan, contract or spec, kernel or template, history, failure memory, nonexistent id), mapped to the repository''s own domains. A category the repository has no domain for is dropped, and the drop is recorded. R5 applies: each domain at least 10 %, no subsystem over 25 %. There is at least one nonexistent-id question, scored apart. The set is split into two halves of 40: the first is used to choose fixes; the second is reported in counts only and never chooses. Source families (official copies) are declared in the path map. Verify: the set''s checks in the proof record (path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS) [DEC-1098 (1), DEC-1070 (2)-(3), DEC-1074 (4), DEC-1069 (5), DEC-1076 (5), DEC-1078 (4), DEC-1071 (5), DEC-1010] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'S13 The fresh verdict set, used once: 80 questions, written by the same independent writer and checker under the same rubric, blind, before the first measure of the tuning set. None of its gold sources is a gold source of the tuning set. It is held outside every worktree in a folder of mode 700, declared in the path map''s evaluation_sets with every role but the orchestrator refused, and the guard refuses the measured roles a read of the set and of its run folder (as ACT-GUARD-SETS-1). It is used once, as FRESH-80-1 did. First a counts-only pre-flight: the set''s digest, how its anchors resolve at the measured commit, and whether each nonexistent id still exists nowhere. Then the checker''s staleness pass at that commit. Then a declaration, committed before any search, naming the configuration (S10), the commit, the denominator with nonexistent-id questions apart, the bar and how it rounds (S14), any data conditions as data only, and the fault rule (FRESH-80-1 \u00a73.5). Then a control on the tuning set. A USED marker is written before the first search, and the runner refuses to start once it exists. The result record gives counts only. Verify: the declaration''s commit is earlier than the USED marker; a planted USED makes the runner refuse; a planted read of the set by a measured role is refused by the guard [DEC-1098 (1), DEC-1097 (1)(b), (1)(g), DEC-1097 (2), DEC-1092 (4), DEC-1078 (3), DEC-1074 (1)] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'S14 The bar: on the verdict set, judged on the declared configuration only. The figure is right end to end: the answer correct and its citation right, graded by a named grader model, with a second grader''s agreement reported. It must be at least 85 % with wrong claims at most 5 %; the target is 95 %. On n judged questions that is at least ceil(0.85 n) right and at most floor(0.05 n) wrong claims. Reported beside it, never judged: hit@5, gold in the first bundle, the answer correct with the citation set aside, the stricter grade, one search against two (exact McNemar), the exact 95 % interval, and the reader model by name. Verify: the result record in docs/research/W2-88-any-repository.md (or the adopted repository''s copy of it) holds the verdict line and the side table [DEC-1097 (1)(d), DEC-1098 (1), DEC-957, CAP-10, DEC-1079] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'S15 Search again once in the adopted repository: adoption copies, unchanged, the kernel''s retrieval skill with step 7 (W2-142 S1), the discovery skill''s line (W2-142 S2) and T-0''s and T-8''s \"Search again once\" line (W2-128''s line). Nothing is re-worded per repository. The verdict''s judged condition is up to two searches (A2). Verify: a string test on a planted adoption''s generated skill and T-0 for \"search again once\", \"own, different words\", \"not found\" and \"two searches\" [DEC-1098 (1), DEC-1094 (2), DEC-1092 (1)] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'S16 A miss is a result. A verdict below either limit stands as recorded. It is never run again, never re-scored to pass, and its labels are never changed after its figures exist. The spent set becomes a diagnostic set. An independent auditor classifies its misses by kind, counts only: never retrieved, ranked low, vocabulary, correct answer citing an unlisted place, other. The result goes to the repository''s owner with options: structural fixes judged on the tuning set and then a new fresh set used once, or the figure accepted as a named residual with its cause. The store stays in service. The four settings of S10 change only by Gov OS''s owner''s decision (a CIT-P), never at the adopted repository. Verify: the result record''s miss section on a planted miss (stand-in figures); the runner refuses a set marked USED [DEC-1098 (1), DEC-1074 (1)-(2), DEC-1071 (1), DEC-1083 (2), DEC-954 Q9e, DEC-1070 (14)] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'S18 The audit''s schedule at adoption: an adopted repository is audited on the same rhythm by the same tool (weekly while active, monthly once stable, by W2-172''s rule). Adoption writes the repository''s audit record: its sets root, its audit names, its mode, the three briefs'' variant ids and their sha256, and the first audit''s earliest date. It starts no audit and installs no schedule line itself (the crontab is an ACT). Verify: a planted adoption writes the record with those fields; a grep of the planted crontab and sets root before and after finds no change [DEC-1101 (1)-(2), DEC-1125 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'\n  - 'S19 The briefs'' variants, approved once: the adopted repository''s writer, checker and auditor briefs are the Gov OS briefs (`governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/`, once approved) with two parts replaced by the repository''s own: the domain table (the writer''s section 5 items 1 and 3, the checker''s section 5a) mapped from S12''s twelve categories to the repository''s domains, with every dropped category recorded, and the list of records the audit stays blind to. Nothing else changes. Each variant is approved once by the repository''s owner and hashed; a launch under an unapproved variant is refused. Verify: a planted adoption''s variants differ from the Gov OS briefs only in those two parts (a diff test); a launch under a variant not on the planted approved list exits 10 [DEC-1101 (2), DEC-1099 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'\n  - 'S20 One core, not two: `src/gov/adopt/memory_sets.py` calls `gov.memaudit` (W2-170''s checks and declaration, W2-171''s measure and pool) and defines no pre-flight, use-once marker or figures of its own. Verify: a test that the module imports from `gov.memaudit` and defines none of those functions; S12''s and S13''s planted runs produce the same declaration and verdict line as the audit''s [DEC-1101 (1), DEC-1099 (2), DEC-1125 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'\n  - 'S21 The first scheduled audit follows the verdict set: an adopted repository''s first scheduled audit runs only after its verdict set (S13) was used and its result record written; the audits'' log starts at the verdict set''s commit (`gov.memaudit baseline`), and the tuning and verdict sets join the repository''s pool. Verify: a planted adoption before S13''s USED marker: `due` says `not due: no verdict set used`; after it: the baseline line holds the verdict commit [DEC-1101 (1), DEC-1098 (1)] [added, DEC-1101 (1), DEC-1125 (2)]'\n  - 'S22 The walls for an adopted repository by one ACT: adoption writes one ACT package for the repository''s owner''s operator: the walls'' template copy, the sets root folder (mode 0700), the approved list with the three variant briefs, and the path-map hidden globs. Adoption never applies it. Verify: a planted adoption writes the package and changes nothing in the planted sets root or path map [DEC-1101 (2)-(3), DEC-1099 (2)] [added, DEC-1101 (1), DEC-1125 (2)]'\n  - 'S23 The audit''s cost is stated at adoption: the adoption record gives, for the repository''s set size, the estimated tokens and USD per audit, the GPU minutes and the owner''s minutes, from `governance/project/orchestration/packages/MEMORY-AUDIT-1.md` section 7, and names the figure to replace once the first audit has measured them. Verify: a string test on a planted adoption record for the four figures [DEC-1101 (3)] [added, DEC-1101 (1), DEC-1125 (2)]'\n  failure:\n  - 'Anything written, moved, committed or deleted in a repository by the assessment or the refactoring plan; a proposed ticket created with tk or applied without the owner. Verify: a hash of a planted repository''s tree, index and history and its `tk` ticket list before and after the assessment and the plan are identical; no tk create or apply call appears in the call log; any difference is a failure'\n  - 'A tracked file neither indexed nor named with its reason; a store not built reported ok. Verify: a planted tracked file left out of both lists makes the stage not ok; a planted adoption where a store the path map calls for was not built never prints ok'\n  - 'A store of another layout version read as current; a rebuild record whose only digest is the record graph''s. Verify: a planted store of another layout version is refused with STORE_LAYOUT_STALE, never opened as current; a planted rebuild record is checked for the four per-store digests and is refused if only the record graph''s is present'\n  - 'The assessment loading the whole tree in memory, or exceeding the resource gate''s per-session figure on the largest proof repository. Verify: the assessment''s recorded peak RSS on the largest proof repository is under the resource gate''s per-session figure, and a test on a planted large tree shows the memory growing with the largest file, not with the tree''s size'\n  - 'A secret''s value in any record, log or output; a hidden question read or printed. Verify: a grep of every record, log and output of a planted run for the planted secret''s value finds 0 hits; the guard''s log of the run holds no read of a hidden question and a grep of the outputs for a planted hidden question''s unique word finds 0 hits [re-worded, DEC-1084]'\n  - 'A verdict set read by a measured role, measured twice, or used to choose anything; a declaration committed after the first search. Verify: a planted read of the set by a measured role is refused by the guard; a planted USED marker makes the runner refuse a second measure; the declaration''s commit is earlier than the first search in the ledger; the tuning set''s fixes cite no verdict question [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'A store served with a setting other than the standard''s and no decision id in the A9 record. Verify: a planted retrieval.yaml with the pool off, a second reranker or another bundle budget and no decision id in the A9 record makes the stage not ok and the setting is named [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'A tuning or verdict question written with the product''s own search, or by a session in the retrieval work. Verify: the writer session''s log holds no call of the product''s search and the writer''s session id is not among the retrieval work''s sessions; a planted question whose record names a search call or a retrieval-work session is refused by the checker [added, DEC-1099 (2); DEC-1098 (1)]'\n  - 'An audit started by adoption; a variant brief launched without the repository owner''s approval; a second copy of the pre-flight, the use-once marker or the figures in `src/gov/adopt/`. Verify: a planted adoption leaves the audits'' log and the crontab unchanged and starts no audit process; a launch under a variant brief not on the planted approved list exits 10; a grep of src/gov/adopt/ finds no definition of the pre-flight, the use-once marker or the figures outside the import from gov.memaudit [added, DEC-1101 (1), DEC-1125 (2)]'\n  moved:\n  - 'A store not built is never ok: gov rebuild on a repository where the path map or .gitleaks.toml is missing, or where a store the path map calls for was not built, names each store not built with its reason, and its result is not ok. A rebuild with --no-embeddings stays ok for the vectors it was told not to build, and says so. W2-26''s finding 2 is a planted case [DEC-954 Q9f, W2-26 finding 2, DEC-530] [moved to W2-124, DEC-1083] (was S5)'\nprofile: FULL\nsources:\n- DEC-954\n- DEC-953\n- DEC-078\n- DEC-071\n- DEC-630\n- DEC-718\n- DEC-723\n- DEC-728\n- DEC-388\n- DEC-694\n- DEC-530\n- DEC-833\n- DEC-860\n- DEC-941\n- DEC-105\n- CAP-44\n- CAP-17\n- CAP-20\n- CAP-10\n- CAP-19\n- DEC-957\n- CAP-44.b\n- CAP-44.f\n- CAP-44.g\n- DEC-016\n- DEC-1083\n- DEC-1084\n- DAEO-mb2t\n- DAEO-2ds6\n- DEC-1098\n- DEC-1099\n- DEC-1097\n- DEC-1072\n- DEC-1071\n- DEC-1070\n- DEC-1074\n- DEC-1092\n- DEC-1094\n- CAP-33\n- DEC-1010\n- DEC-1046\n- DEC-1069\n- DEC-1076\n- DEC-1078\n- DEC-1079\n- DEC-1101\n- DEC-1125\n- DEC-315\n- DEC-1112\nest_loc: 750  # [changed, DEC-1099 (2)] was 500 (W2-88-STANDARD-1 \u00a74)\nacceptance_tests:\n  path: tests/acceptance/W2-88/\n  author: 'independent-test-designer (MR-3); written before implementation. Small repositories are planted in temporary folders (a vendored folder, a generated file, a file over the chunker''s limit, a secret in a tracked file, a path with no namespace, a binary, a language the code graph does not read), W2-81''s builders are reused read-only, and stand-ins are used for the embedder and the code graph where a case needs none. No network, no real clone and never this repository''s store. This designer writes the planted cases (S10, S11, S13, S15 to S17) and chooses and pins the two GitHub repositories. The question sets (S12, S13 and the 10 questions per real repository) belong to the independent writer and checker, sessions outside the system opened by the owner''s operator [changed, DEC-1099 (2)]'\ntrack: A\nlist_rows: []\nwaits_on:\n- 'DAEO-qskx \u2014 W2-142: S15 copies the retrieval skill''s step 7 and the discovery skill''s line [added, DEC-1099 (2)]'\n- 'DAEO-t8mp \u2014 W2-128: S15 copies T-0''s and T-8''s \"Search again once\" line [added, DEC-1099 (2)]'\n- 'DAEO-f58b \u2014 W2-116: S11''s refresh after every merge, double-buffered [added, DEC-1099 (2)]'\n- 'DAEO-2tfd \u2014 W2-145: S10 needs no private reranker beside the shared service [added, DEC-1099 (2)]'\n---\n# W2-88 Memory for any repository\n\n**DEC-957 (2026-10-30):** this ticket also closes MEMORY-SPEC-MAP gaps 4 (the store layout, with the STORE_MISSING cause) and 5 (the large-repository measure, its Scale KPI). `src/gov/store/loader.py`'s open path is added for the layout check (W2-03 is merged and closing: split by function). The mapping of a query failure to STORE_MISSING in `retrieve.py` (W2-87's file) is named for the retrieval tickets if the open-path check does not make it unreachable.\n\nCard: from the owner's DEC-954 Q9f (2026-10-30): \"Memory for any repository, not only this one: if we build memory that only this repository can use, we have built nothing.\" It is in Wave 2's minimum. The tools assess any repository at adoption, however large; plan any refactoring it needs for full indexing as governed tickets, for the repository's owner to approve and never applied on their own; build the full index and the embeddings; and set up the database structure (SQLite and the vector store), so memory works there.\n\n- **Why no existing ticket covers it** (checked):\n  - **Adoption** (`src/gov/adopt/`, W1-39 and W1-41) runs A0 to A6 and A8. It has no knowledge-fabric stage: CAP-44.f's A9 is Wave 3 in the Contract.\n  - **W2-52** writes the lite A7 and A10 records: verification, not building.\n  - **W2-23** is adoption safety (rollback, adapters, paths with spaces).\n  - **W2-81** builds synthetic repositories and judges an adoption's outputs. It builds no index.\n  - **W2-27** is the integration run on EXAMIN's copy.\n  - **W2-26's finding 2:** `gov rebuild` on an unadopted clone builds nothing and says ok.\n  - **W2-86 and W2-87** change this repository's path map and ranking only.\n  - So this is a new ticket, not a change to an existing one. The nearest, W2-52, keeps its scope: verification records. It holds `stages.py` and the adopt skill, so it merges first.\n- **The Contract:** A9 lite comes into Wave 2 by a CIT-P note under DEC-105 option (a): apply now, as the owner decided in DEC-954 Q9f. `docs/changes/W2-88-CIT-P.md` holds the note, and the lead returns it as a package before the engineer starts. It also covers the adopt skill's A9 step: a kernel skill change, under CAP-33.\n- **Profile FULL, not STANDARD:**\n  - it changes adoption, a path where a fault loses an owner's work: the plan must never apply;\n  - it changes what `gov rebuild` reports as ok, which is a fail-open fix;\n  - it adds a stage the verdict reads.\n- **Where it sits:**\n  - stream S1 (memory), proven in S4's proving ground;\n  - it closes before W2-27, which is its live trial and depends on it (DEC-954);\n  - W2-15b's final measure on EXAMIN's clone and `~/workspace` uses it.\n- **Overlaps, split by file:**\n  - **W2-52** (`DAEO-siiz`, held) holds `src/gov/adopt/stages.py`, `lite_gates.py` and the adopt skill. It merges first (a dependency). This ticket changes `stages.py`'s stage list and the A9 call only, and the skill's A9 step only.\n  - **W2-23** (`DAEO-kmcr`, open) holds `src/gov/adopt/**` and `src/gov/adapters/**`. This ticket's new modules are files of its own; whichever merges second merges back.\n  - **W2-76** (`DAEO-tgk2`, finishing) holds `src/gov/rebuild/**`. It merges first (a dependency). This ticket changes the result's `ok` line only.\n  - **W2-06** (`DAEO-kia7`, open) holds `src/gov/rebuild/**` too; it is split by line, and the second to merge merges back.\n  - **W2-03** (`DAEO-ym8a`, merged, closing) holds `src/gov/store/**`. `layout.py` is new; the loader is read, not changed.\n  - **W2-13 and W2-32** hold `src/gov/retrieval/**`: not touched. The vector store's possible change is a proposal, not this ticket's.\n  - **W2-81** (`DAEO-l78m`) holds `tests/acceptance/W2-81/**`. Its builders and question sets are read and run, never edited.\n- **Est.:** 500 LOC:\n  - the assessment, about 150;\n  - the plan, about 120;\n  - A9 lite, about 150;\n  - the layout, about 60;\n  - the glue and the rebuild line, about 20.\n  \n  Scaled as the plan's \u00a72.0 (W2-66's 400 LOC took 13.1 h; W2-67's 750 took 18.8 h): about 15 lead-hours to build, plus 5 to 10 h for the real runs. Embedding a repository of the order of 10^4 files on this machine is unmeasured: this repository's 2,521 files took 7 to 45 min. **Est. 20\u201326 lead-hours.**\n- **Network:**\n  - The two GitHub clones are made by the lead or the CTO, whose sessions have the network. Sandboxed workers have none.\n  - The clones are exact-path folders under `~/gov-os-runs/W2-88/` (DEC-728), never under this repository.\n  - Nothing of them is committed: only counts, ids, digests and figures go into `docs/research/W2-88-any-repository.md`.\n- **Test repository paths the register names** (searched in `docs/DECISION_REGISTER.md`):\n  - **`~/workspace`:** DEC-078's scale probe (1,005 files indexed then, 77,346 nodes, 270,647 edges, 2.2 GB peak RSS) and DEC-718's EXP-003 corpus. It has 1,467 tracked files today. **Used.**\n  - **`~/gov-os-workbench/synthetic/`:** the dev tiers, a-dev (ORION) and b-dev (ARGUS), 150 and 149 tracked files (DEC-071, DEC-630 `GOV_DEV_TIERS`). **Used.** `customer-dev` sits beside them, with no tracked files.\n  - **ARGUS's stress tier (\u00d74: 5,355 files, 57,777 chunks; DEC-071):** its location is unconfirmed. **Used only if it is outside** `~/gov-os-workbench/qualification-oracle/`; that path and the qual tiers are held out (DEC-067, DEC-425, DEC-426) and are **never used**.\n  - **`~/gov-os-workbench/examin/`:** the owner's copy of EXAMIN (DEC-723). **The assessment only**, on a clone. Adoption is W2-27's.\n  - **`~/EXAMIN APP`:** the real repository (DEC-078, DEC-718). **Never touched here.** It is written only by W2-29, after W2-25, W2-15b and the owner's go (DEC-727).\n  - **`~/gov-b2-throwaway`:** DEC-668's throwaway copy of a-dev-exit. **Deleted; not available.**\n  - **`~/gov-os-workbench/archive/w1-42-exit-clones/`:** W1-42's adopted exit clones (DEC-673). They are backups, read-only. **Not needed:** a-dev and b-dev cover them.\n- **What it does not do:**\n  - It applies no refactoring.\n  - It builds no indexed vector store (a proposal if the scale figures call for one).\n  - It adds no graph route to plain-question retrieval (MEMORY-SPEC-MAP gaps 2 and 3).\n  - It writes no question for W2-81's or EXAMIN's hidden halves (gaps 6 and 7).\n\n## The memory-building practice (DEC-1072 (2), 2026-11-04)\n- **Memory-building is a Gov OS practice for every adopted repository's Wave 0,** and this ticket owns it. The\n  practice learned in D-4b is recorded in `docs/research/W2-88-memory-practice.md`, kept up to date as D-4b goes, and\n  becomes a kernel skill after the refactoring. The record holds:\n  - how the store is built;\n  - how it is measured (the rubric, the three sets and their jobs, independent writers, the hidden-half rule,\n    scoring);\n  - how it is tuned (structural fixes only, judged on all sets, consistency as the proof);\n  - every method tried, with its figures;\n  - the lessons.\n- **What it adds to this ticket's work:**\n  - A9's index follows the record's section 6:\n    - a census of the repository's stated links before the graph is built;\n    - chunking by meaning, with the heading path given to every reader;\n    - the three sets by independent writers.\n  - The question sets follow the rubric: see the memory standard below. [changed, DEC-1099 (2)]\n- **The KPIs are amended by DEC-1099 (2):** see the memory standard below. A KPI change goes through this ticket's test designer. [changed, DEC-1099 (2)]\n\n## The memory standard (DEC-1098 (1), DEC-1099 (2), 2026-11-09)\n- **The lines:** S10 to S17 and three failure lines, from `governance/project/orchestration/packages/W2-88-STANDARD-1.md`\n  \u00a72 as written; \"Memory works there\", proof (b), `acceptance_tests.author`, `est_loc` and this body changed per its \u00a73.\n- **The owner's answers (DEC-1099 (2)):**\n  - (1) S10 to S17 and the three failure lines as written.\n  - (2) (c): EXAMIN's copy at W2-27 is the practice's first full run, with no separate proof repository. What goes\n    wrong there is fixed, and the repositories adopted after EXAMIN follow the practice as fixed.\n  - (3) (a): the tuning set is 80 questions in two halves of 40; the second reports in counts only and never chooses.\n  - (4) The writer and checker are sessions outside the system, opened by the owner's operator.\n  - (5) The set tools (`src/gov/adopt/memory_sets.py`) and the practice record\n    (`docs/research/W2-88-memory-practice.md`) are in this ticket's `allowed_paths`.\n  - (6) The nonexistent-id row is its own ticket (W2-146). Until it lands, S12 and S14 score that question on the\n    reader's \"not found\", apart from the bar (W2-88-STANDARD-1 \u00a75).\n- **Waits:** W2-142 and W2-128 (S15) and W2-116 (S11), in `waits_on`. S10 also waits on W2-145 (`DAEO-2tfd`, no\n  private reranker), which is kept out of `waits_on` for now: W2-145 and W2-137 (`DAEO-5emz`) each need a file the\n  other writes (`src/gov/retrieval/rerank.py`), `gov plan`'s one cycle, and with W2-145 in `waits_on` the plan's\n  tiebreak orders W2-27 before W2-88 (measured 2026-11-09). It goes into `waits_on` when that cycle is gone.\n- **Est.:** about 750 LOC (+250: the set tools, S10's check, the skill step). W2-88-STANDARD-1 \u00a74 gave 30 to 38\n  lead-hours with one full practice run; under answer (2)(c) that run is W2-27's, so this ticket's share is less by it.\n\n[DEC-1099 (2), DEC-1098 (1)]\n\n## Split by the owner (DEC-1150 (1), package 1 (a), 2026-11-12; DEC-996 (1))\n\nThis ticket keeps the code (engineer). Moved word for word: S17 (the adopt skill's order) and its kernel skill paths to **W2-88a** (DAEO-pg6i, product-spec, with W2-174's skill line); proofs (b) and (c), their scale and measure lines and the GitHub-clone failure line to **W2-88b** (DAEO-aks1, research, copies only). Proof (a)'s record moves to `docs/changes/W2-88-evidence.md`; the practice record `docs/research/W2-88-memory-practice.md` goes with the skill text to W2-88a. W2-27 depends on this ticket's tools, not on W2-88b.\n",
  "authority": [
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-078",
      "sha256": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "reason": "declared in sources",
      "tokens": 250
    },
    {
      "id": "DEC-071",
      "sha256": "f71a05a5f760d7466d8f3bb2a37aa1557c0a0a376bcb8f0cb6b177052f27a4b5",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "f71a05a5f760d7466d8f3bb2a37aa1557c0a0a376bcb8f0cb6b177052f27a4b5",
      "reason": "declared in sources",
      "tokens": 318
    },
    {
      "id": "DEC-630",
      "sha256": "d7d61c6ac3ace57635a86d5f223d5884e9e1828e6820170a868869988b66a4ba",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d7d61c6ac3ace57635a86d5f223d5884e9e1828e6820170a868869988b66a4ba",
      "reason": "declared in sources",
      "tokens": 147
    },
    {
      "id": "DEC-718",
      "sha256": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "reason": "declared in sources",
      "tokens": 4248
    },
    {
      "id": "DEC-723",
      "sha256": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "reason": "declared in sources",
      "tokens": 315
    },
    {
      "id": "DEC-728",
      "sha256": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "reason": "declared in sources",
      "tokens": 475
    },
    {
      "id": "DEC-388",
      "sha256": "43300405b822608d9c048115c2b476dcb63a973ef9b773d61a2999f505f29d95",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43300405b822608d9c048115c2b476dcb63a973ef9b773d61a2999f505f29d95",
      "reason": "declared in sources",
      "tokens": 411
    },
    {
      "id": "DEC-694",
      "sha256": "387a4c3cac2a5bf0470e32d679cea14df7b6ab09af931f9d12f85f474de1a1a5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "387a4c3cac2a5bf0470e32d679cea14df7b6ab09af931f9d12f85f474de1a1a5",
      "reason": "declared in sources",
      "tokens": 307
    },
    {
      "id": "DEC-530",
      "sha256": "7a69e155084b53a9693994af93c0b02e4a98247acf1174b148dbc6a15a3f270f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7a69e155084b53a9693994af93c0b02e4a98247acf1174b148dbc6a15a3f270f",
      "reason": "declared in sources",
      "tokens": 125
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-860",
      "sha256": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "reason": "declared in sources",
      "tokens": 416
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-016",
      "sha256": "a68271c189153cbcbe4b34c3757157b8bfa316d241e14ab297009c415f2bdd34",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a68271c189153cbcbe4b34c3757157b8bfa316d241e14ab297009c415f2bdd34",
      "reason": "declared in sources",
      "tokens": 166
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1099",
      "sha256": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "reason": "declared in sources",
      "tokens": 693
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1070",
      "sha256": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "reason": "declared in sources",
      "tokens": 1245
    },
    {
      "id": "DEC-1074",
      "sha256": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "reason": "declared in sources",
      "tokens": 900
    },
    {
      "id": "DEC-1092",
      "sha256": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "reason": "declared in sources",
      "tokens": 564
    },
    {
      "id": "DEC-1094",
      "sha256": "77ad0cbb6b92142bd64c1d2d07352c32043cc41ae63d31c1735a095221ea2c03",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "77ad0cbb6b92142bd64c1d2d07352c32043cc41ae63d31c1735a095221ea2c03",
      "reason": "declared in sources",
      "tokens": 521
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1046",
      "sha256": "ca51226ba58ec52e004bee8c93ba16dc74525fcb3dcf3de93728d49b27a1a8a3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ca51226ba58ec52e004bee8c93ba16dc74525fcb3dcf3de93728d49b27a1a8a3",
      "reason": "declared in sources",
      "tokens": 450
    },
    {
      "id": "DEC-1069",
      "sha256": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "reason": "declared in sources",
      "tokens": 1134
    },
    {
      "id": "DEC-1076",
      "sha256": "79aecc9b619991894a55a4455155e72c21bdf1fc03b37bf06902463fae49d297",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "79aecc9b619991894a55a4455155e72c21bdf1fc03b37bf06902463fae49d297",
      "reason": "declared in sources",
      "tokens": 865
    },
    {
      "id": "DEC-1078",
      "sha256": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    },
    {
      "id": "DEC-1125",
      "sha256": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "reason": "declared in sources",
      "tokens": 945
    },
    {
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "CAP-44",
      "sha256": "e8353fca43e1670c01aef5af65a314f56c589b99c0ef6dd2a9f2f75b5b1113e0",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "e8353fca43e1670c01aef5af65a314f56c589b99c0ef6dd2a9f2f75b5b1113e0",
      "reason": "declared in sources",
      "tokens": 245
    },
    {
      "id": "CAP-17",
      "sha256": "b55cb068d148939c3cb1ff57615d157de07dbe9521496ef12a33539cfa4c1783",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "b55cb068d148939c3cb1ff57615d157de07dbe9521496ef12a33539cfa4c1783",
      "reason": "declared in sources",
      "tokens": 192
    },
    {
      "id": "CAP-20",
      "sha256": "4c29acb9bb5abf61510bfc504949aeaa5b99ce6847086e011b789d2241fafa2f",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "4c29acb9bb5abf61510bfc504949aeaa5b99ce6847086e011b789d2241fafa2f",
      "reason": "declared in sources",
      "tokens": 183
    },
    {
      "id": "CAP-10",
      "sha256": "8fcbca27e7b3ed804850594b78decbb77f1da71e68127242c890425731201d67",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "8fcbca27e7b3ed804850594b78decbb77f1da71e68127242c890425731201d67",
      "reason": "declared in sources",
      "tokens": 165
    },
    {
      "id": "CAP-19",
      "sha256": "8b9e56249d7e6581ce489cd96add42446f54b379945a739c188b451cb3a42c0a",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "8b9e56249d7e6581ce489cd96add42446f54b379945a739c188b451cb3a42c0a",
      "reason": "declared in sources",
      "tokens": 201
    },
    {
      "id": "CAP-44.b",
      "sha256": "7426cbe02f79eba956e12632171896067cdc6bee9dfa18130da38b5587c2fbc2",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "7426cbe02f79eba956e12632171896067cdc6bee9dfa18130da38b5587c2fbc2",
      "reason": "declared in sources",
      "tokens": 184
    },
    {
      "id": "CAP-44.f",
      "sha256": "c54f64e5e8095ac8115f7ba303f9607d27f689ec73e271545ad2fe4b6c694fc2",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "c54f64e5e8095ac8115f7ba303f9607d27f689ec73e271545ad2fe4b6c694fc2",
      "reason": "declared in sources",
      "tokens": 360
    },
    {
      "id": "CAP-44.g",
      "sha256": "c7d6f6ad88eaf92525ffaa8c21417c9f915282b3e8e800caeee5ab5eaf046977",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "c7d6f6ad88eaf92525ffaa8c21417c9f915282b3e8e800caeee5ab5eaf046977",
      "reason": "declared in sources",
      "tokens": 121
    },
    {
      "id": "DAEO-mb2t",
      "sha256": "985d27d5e80ecd3fce60669b4246eb82fef1df0cff6e3418a02c3ae1508cc695",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "985d27d5e80ecd3fce60669b4246eb82fef1df0cff6e3418a02c3ae1508cc695",
      "reason": "declared in sources",
      "tokens": 2376
    },
    {
      "id": "DAEO-2ds6",
      "sha256": "f8f7a6efcb5343447f61185d3a834e2b8fc9da2cf51e4f79d9f41d2961c88c33",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "f8f7a6efcb5343447f61185d3a834e2b8fc9da2cf51e4f79d9f41d2961c88c33",
      "reason": "declared in sources",
      "tokens": 832
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    },
    {
      "id": "DAEO-ym8a",
      "sha256": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "reason": "declared in sources",
      "tokens": 164
    },
    {
      "id": "DAEO-siiz",
      "sha256": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "reason": "declared in sources",
      "tokens": 152
    },
    {
      "id": "DAEO-tgk2",
      "sha256": "8c3b0d7892ee07c758246b4ac8b992d8eb8536f267630429dde02f208a09e13d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8c3b0d7892ee07c758246b4ac8b992d8eb8536f267630429dde02f208a09e13d",
      "reason": "declared in sources",
      "tokens": 361
    },
    {
      "id": "DAEO-l78m",
      "sha256": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "reason": "declared in sources",
      "tokens": 1878
    },
    {
      "id": "DAEO-q7lk",
      "sha256": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "reason": "declared in sources",
      "tokens": 2274
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "reason": "declared in sources",
      "tokens": 1644
    },
    {
      "id": "DAEO-p8tv",
      "sha256": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "reason": "declared in sources",
      "tokens": 2005
    }
  ],
  "mandatory": [
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-078",
      "sha256": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "reason": "declared in sources",
      "tokens": 250
    },
    {
      "id": "DEC-071",
      "sha256": "f71a05a5f760d7466d8f3bb2a37aa1557c0a0a376bcb8f0cb6b177052f27a4b5",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "f71a05a5f760d7466d8f3bb2a37aa1557c0a0a376bcb8f0cb6b177052f27a4b5",
      "reason": "declared in sources",
      "tokens": 318
    },
    {
      "id": "DEC-630",
      "sha256": "d7d61c6ac3ace57635a86d5f223d5884e9e1828e6820170a868869988b66a4ba",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d7d61c6ac3ace57635a86d5f223d5884e9e1828e6820170a868869988b66a4ba",
      "reason": "declared in sources",
      "tokens": 147
    },
    {
      "id": "DEC-718",
      "sha256": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "reason": "declared in sources",
      "tokens": 4248
    },
    {
      "id": "DEC-723",
      "sha256": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "reason": "declared in sources",
      "tokens": 315
    },
    {
      "id": "DEC-728",
      "sha256": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6be4db51030e9119fbb94aea770ed22a1b2f0cc29b33cffe5df5f9aa78210334",
      "reason": "declared in sources",
      "tokens": 475
    },
    {
      "id": "DEC-388",
      "sha256": "43300405b822608d9c048115c2b476dcb63a973ef9b773d61a2999f505f29d95",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43300405b822608d9c048115c2b476dcb63a973ef9b773d61a2999f505f29d95",
      "reason": "declared in sources",
      "tokens": 411
    },
    {
      "id": "DEC-694",
      "sha256": "387a4c3cac2a5bf0470e32d679cea14df7b6ab09af931f9d12f85f474de1a1a5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "387a4c3cac2a5bf0470e32d679cea14df7b6ab09af931f9d12f85f474de1a1a5",
      "reason": "declared in sources",
      "tokens": 307
    },
    {
      "id": "DEC-530",
      "sha256": "7a69e155084b53a9693994af93c0b02e4a98247acf1174b148dbc6a15a3f270f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7a69e155084b53a9693994af93c0b02e4a98247acf1174b148dbc6a15a3f270f",
      "reason": "declared in sources",
      "tokens": 125
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-860",
      "sha256": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b02ef840a9d231a0f91fbe0abd5dbcdbc318a852fc964291a599945fe8d2ced5",
      "reason": "declared in sources",
      "tokens": 416
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-016",
      "sha256": "a68271c189153cbcbe4b34c3757157b8bfa316d241e14ab297009c415f2bdd34",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a68271c189153cbcbe4b34c3757157b8bfa316d241e14ab297009c415f2bdd34",
      "reason": "declared in sources",
      "tokens": 166
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1099",
      "sha256": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "reason": "declared in sources",
      "tokens": 693
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1070",
      "sha256": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "reason": "declared in sources",
      "tokens": 1245
    },
    {
      "id": "DEC-1074",
      "sha256": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "reason": "declared in sources",
      "tokens": 900
    },
    {
      "id": "DEC-1092",
      "sha256": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "reason": "declared in sources",
      "tokens": 564
    },
    {
      "id": "DEC-1094",
      "sha256": "77ad0cbb6b92142bd64c1d2d07352c32043cc41ae63d31c1735a095221ea2c03",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "77ad0cbb6b92142bd64c1d2d07352c32043cc41ae63d31c1735a095221ea2c03",
      "reason": "declared in sources",
      "tokens": 521
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1046",
      "sha256": "ca51226ba58ec52e004bee8c93ba16dc74525fcb3dcf3de93728d49b27a1a8a3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ca51226ba58ec52e004bee8c93ba16dc74525fcb3dcf3de93728d49b27a1a8a3",
      "reason": "declared in sources",
      "tokens": 450
    },
    {
      "id": "DEC-1069",
      "sha256": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "reason": "declared in sources",
      "tokens": 1134
    },
    {
      "id": "DEC-1076",
      "sha256": "79aecc9b619991894a55a4455155e72c21bdf1fc03b37bf06902463fae49d297",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "79aecc9b619991894a55a4455155e72c21bdf1fc03b37bf06902463fae49d297",
      "reason": "declared in sources",
      "tokens": 865
    },
    {
      "id": "DEC-1078",
      "sha256": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    },
    {
      "id": "DEC-1125",
      "sha256": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "reason": "declared in sources",
      "tokens": 945
    },
    {
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "CAP-44",
      "sha256": "e8353fca43e1670c01aef5af65a314f56c589b99c0ef6dd2a9f2f75b5b1113e0",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "e8353fca43e1670c01aef5af65a314f56c589b99c0ef6dd2a9f2f75b5b1113e0",
      "reason": "declared in sources",
      "tokens": 245
    },
    {
      "id": "CAP-17",
      "sha256": "b55cb068d148939c3cb1ff57615d157de07dbe9521496ef12a33539cfa4c1783",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "b55cb068d148939c3cb1ff57615d157de07dbe9521496ef12a33539cfa4c1783",
      "reason": "declared in sources",
      "tokens": 192
    },
    {
      "id": "CAP-20",
      "sha256": "4c29acb9bb5abf61510bfc504949aeaa5b99ce6847086e011b789d2241fafa2f",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "4c29acb9bb5abf61510bfc504949aeaa5b99ce6847086e011b789d2241fafa2f",
      "reason": "declared in sources",
      "tokens": 183
    },
    {
      "id": "CAP-10",
      "sha256": "8fcbca27e7b3ed804850594b78decbb77f1da71e68127242c890425731201d67",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "8fcbca27e7b3ed804850594b78decbb77f1da71e68127242c890425731201d67",
      "reason": "declared in sources",
      "tokens": 165
    },
    {
      "id": "CAP-19",
      "sha256": "8b9e56249d7e6581ce489cd96add42446f54b379945a739c188b451cb3a42c0a",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "8b9e56249d7e6581ce489cd96add42446f54b379945a739c188b451cb3a42c0a",
      "reason": "declared in sources",
      "tokens": 201
    },
    {
      "id": "CAP-44.b",
      "sha256": "7426cbe02f79eba956e12632171896067cdc6bee9dfa18130da38b5587c2fbc2",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "7426cbe02f79eba956e12632171896067cdc6bee9dfa18130da38b5587c2fbc2",
      "reason": "declared in sources",
      "tokens": 184
    },
    {
      "id": "CAP-44.f",
      "sha256": "c54f64e5e8095ac8115f7ba303f9607d27f689ec73e271545ad2fe4b6c694fc2",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "c54f64e5e8095ac8115f7ba303f9607d27f689ec73e271545ad2fe4b6c694fc2",
      "reason": "declared in sources",
      "tokens": 360
    },
    {
      "id": "CAP-44.g",
      "sha256": "c7d6f6ad88eaf92525ffaa8c21417c9f915282b3e8e800caeee5ab5eaf046977",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "c7d6f6ad88eaf92525ffaa8c21417c9f915282b3e8e800caeee5ab5eaf046977",
      "reason": "declared in sources",
      "tokens": 121
    },
    {
      "id": "DAEO-mb2t",
      "sha256": "985d27d5e80ecd3fce60669b4246eb82fef1df0cff6e3418a02c3ae1508cc695",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "985d27d5e80ecd3fce60669b4246eb82fef1df0cff6e3418a02c3ae1508cc695",
      "reason": "declared in sources",
      "tokens": 2376
    },
    {
      "id": "DAEO-2ds6",
      "sha256": "f8f7a6efcb5343447f61185d3a834e2b8fc9da2cf51e4f79d9f41d2961c88c33",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "f8f7a6efcb5343447f61185d3a834e2b8fc9da2cf51e4f79d9f41d2961c88c33",
      "reason": "declared in sources",
      "tokens": 832
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    },
    {
      "id": "DAEO-ym8a",
      "sha256": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "reason": "declared in sources",
      "tokens": 164
    },
    {
      "id": "DAEO-siiz",
      "sha256": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "reason": "declared in sources",
      "tokens": 152
    },
    {
      "id": "DAEO-tgk2",
      "sha256": "8c3b0d7892ee07c758246b4ac8b992d8eb8536f267630429dde02f208a09e13d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8c3b0d7892ee07c758246b4ac8b992d8eb8536f267630429dde02f208a09e13d",
      "reason": "declared in sources",
      "tokens": 361
    },
    {
      "id": "DAEO-l78m",
      "sha256": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "fbdb59e6a86529a332264b8523b2b0b4af85b603bf771afbbe5d3a854b128678",
      "reason": "declared in sources",
      "tokens": 1878
    },
    {
      "id": "DAEO-q7lk",
      "sha256": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "reason": "declared in sources",
      "tokens": 2274
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "reason": "declared in sources",
      "tokens": 1644
    },
    {
      "id": "DAEO-p8tv",
      "sha256": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "reason": "declared in sources",
      "tokens": 2005
    }
  ],
  "supplementary": [
    {
      "id": "DAEO-aks1",
      "path": ".tickets/DAEO-aks1.md",
      "text": "  - 'Memory works there, measured: on each real proof repository ((b) and (c)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN''s copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61''s measure; each real repository has its 10 questions with the writer''s and checker''s records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]'\n",
      "tokens": 302
    },
    {
      "id": "18118c21c89f363827876872",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "text": "  against 215). W2-129's UNMARKED_CHANGE replaces it in use. The duplicate check is listed for D-6's tidy-up, which\n  points it at `register_statements` or removes it.\n\n**W2-88** (`DAEO-2bdu`, open)\n- **Why:** DEC-1073 (5) makes link integrity part of every adopted repository, and DEC-1072 (2) makes this ticket the\n  owner of memory-building at Wave 0.\n- **Add to success:** `'Link integrity at adoption (DEC-1073 (5)): after its store is built, A9 runs gov links --all on the adopted repository and writes in the memory-assessment record the census of its stated links (per kind: instances, distinct pairs, resolvable, in the graph) and the findings by code and role; the findings go to the repository''s owner as its clean-up list and are never fixed by the tool. The kernel ships the link-integrity check declaration (severity warning, never hard-block) and the adopt skill''s step only after gov links has run in this repository''s structural pass for at least a week with its new findings fixed within the day [DEC-1073, DEC-1072 (2), DEC-1052]'`\n- **Add to failure:** `'A link finding that stops or refuses an adoption; a link fixed by the tool in an adopted repository.'`\n",
      "tokens": 296
    },
    {
      "id": "DEC-1150",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1150 \u2014 W2-88 split into W2-88a and W2-88b, with W2-174's skill line; P1-K (a) the fallback dropped; P1-L (a) the 13 files revised, each case keeping its guard\n- **Status:** ACCEPTED (owner, 2026-11-12, in the chat ~17:00; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-12)`) \u00b7 **Under:** DEC-996 (1), DEC-995, DEC-974, DEC-1010, DEC-802, DEC-1027, DEC-1142 (8)\n- **Decision:**\n  - (1) **Package 1 (a):** W2-88a (DAEO-pg6i, product-spec: S17 and W2-174's S5, moved word for word, the three adopt-skill paths, its CIT-P and the practice record) and W2-88b (DAEO-aks1, research: proofs (b) and (c), their scale and measure lines, the proof record in `experiments/W2-88/`, the clone failure line) filed under DEC-996 (1)'s split list; W2-88 keeps the code, proof (a)'s record moving to `docs/changes/W2-88-evidence.md`; W2-174 loses S5 and the skill paths; W2-27 depends on W2-88a too. **Proof (c) works on copies only:** nothing is written in ~/workspace or in any of the owner's own repositories (a failure line of W2-88b).\n",
      "tokens": 278
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "#### W2-88 Memory for any repository: assess, plan the refactoring, build the full index and embeddings, set up the stores (FULL, engineer; DEC-954 Q9f; Wave 2's minimum; to file)\n- **Draft:** `.gov-runtime/scratch/orchestrator/drafts/tickets/W2-88.md`, with its KPIs, paths and proofs.\n- **Why:** \"if we build memory that only this repository can use, we have built nothing\" (the owner, DEC-954 Q9f). Today:\n  - adoption has no knowledge-fabric stage (CAP-44.f's A9 is Wave 3 in the Contract);\n  - `gov rebuild` on an unadopted clone builds no index and says ok (W2-26's finding 2);\n  - nothing assesses a large repository or plans what full indexing needs.\n- **Allowed paths:** new modules under `src/gov/adopt/` (the assessment, the refactoring plan, the A9 lite stage), the stage list in `src/gov/adopt/command.py`, `project.py` and `stages.py`, `src/gov/rebuild/command.py` (the result's `ok` only), `src/gov/store/layout.py` (new), the adopt skill's A9 step and its generated copies, `tests/unit/adopt/test_w2_88*`, `docs/research/W2-88-any-repository.md`, `docs/changes/W2-88-CIT-P.md`. Clones go under `~/gov-os-runs/W2-88/` and are never committed.\n- **KPIs, success:**\n",
      "tokens": 295
    },
    {
      "id": "7c99160bec6d01c496740381",
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "text": "### 5.3 W2-88's line (open, not started; marked DEC-1096; DEC-1088 (6))\nAdded to `kpis.success`, after the A9 line. `waits_on` gains `W2-143`, marked the same. W2-88's own rule holds: a KPI\nchange goes through its test designer.\n```\n- 'The glossary at Wave 0 (DEC-1096 (5)): A9 lite''s build writes the repository''s glossary and code map (W2-143''s stage of gov rebuild). On each proof repository the stage''s record holds the entries by kind, the code map by kind and language, the files not mapped with their reason, the size and the build time; five of the repository''s own ids or code names, chosen by the test designer, each come first in gov glossary; a build without a glossary names its reason in the stage''s record. Verify: the proofs'' records in docs/research/W2-88-any-repository.md and one planted repository [DEC-1096, DEC-1072 (2), DEC-954 Q9f] [added, DEC-1096]'\n```\n\n",
      "tokens": 222
    },
    {
      "id": "1635e0d13b9641267936680e",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "  - 'S14 The bar: on the verdict set, judged on the declared configuration only. The figure is right end to end: the answer correct and its citation right, graded by a named grader model, with a second grader''s agreement reported. It must be at least 85 % with wrong claims at most 5 %; the target is 95 %. On n judged questions that is at least ceil(0.85 n) right and at most floor(0.05 n) wrong claims. Reported beside it, never judged: hit@5, gold in the first bundle, the answer correct with the citation set aside, the stricter grade, one search against two (exact McNemar), the exact 95 % interval, and the reader model by name. Verify: the result record in docs/research/W2-88-any-repository.md (or the adopted repository''s copy of it) holds the verdict line and the side table [DEC-1097 (1)(d), DEC-1098 (1), DEC-957, CAP-10, DEC-1079] [added, DEC-1098 (1)]'\n",
      "tokens": 218
    },
    {
      "id": "DAEO-f58b",
      "path": ".tickets/DAEO-f58b.md",
      "text": "---\nid: DAEO-f58b\nstatus: in_progress\ndeps: [DAEO-ecac, DAEO-lrre]\nlinks: []\ncreated: 2026-10-31T23:52:57Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-116\ntags: [wave-2, implementation, memory, standard, smart-work]\nwbs_id: W2-116\ntitle: 'The designers'' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer''s retrieval reads (SMART-WORK-1)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-ecac\n- DAEO-lrre\nallowed_paths:\n- src/gov/rebuild/integration.py\n- src/gov/rebuild/command.py\n- src/gov/launch/store.py\n- src/gov/launch/launcher.py\n- src/gov/retrieve/command.py\n- docs/changes/W2-116-evidence.md\n- tests/unit/rebuild/test_w2_116*\n- tests/unit/launch/test_w2_116*\nkpis:\n  success:\n  - '`gov rebuild --integration <branch>` keeps a store of that branch''s head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982]'\n",
      "tokens": 283
    },
    {
      "id": "DEC-982",
      "path": "docs/DECISION_REGISTER.md",
      "text": "  2. **The smart way of working becomes part of the Gov OS, not the CTO's own tools (standing):** the practices established in Wave 2, which replace bulk work with smart work: the secrets scan on new or changed content only (by content hash; a full scan in the nightly; the cache cleared on any rule or version change); scoped tests at every level, records and governance files never widening a run; the full suite once a day, in the nightly; a close refused only by failures its own change caused, proven with and without the change; every failure the change did not cause fixed at once or escalated, never left on a list; batch closes that take out a failing ticket and close the rest on the same run; test before merge (the merge queue), skipping a run when the merged code is identical; heavy jobs take a slot, everything else runs freely; failures re-run alone to filter out load, and timing tests time only their own work; checks done once per run, not before every search; shared services (one embedding service, one reranker) instead of a copy per session; the test designer and the engineer in parallel, the engineer seeing pass or fail only, QA batched per stream with core tickets individually; the designers' store kept separate, double-buffered, refreshed twice a day; and the audit's 10 practices for closing a ticket, which `gov close` itself must embody. The CTO maps each to the product (a feature that has it, a ticket that will give it and whether its spec and KPIs say so, or none), proposes the changes to existing tickets' specs and KPIs, and proposes new tickets as P1s (before or after EXAMIN's copy), naming what stays this repository's own and why: `packages/SMART-WORK-1.md`.\n",
      "tokens": 426
    },
    {
      "id": "ADR-0002",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "text": "| L4 | `gov` CLI | **W1:** `status \u00b7 check \u00b7 readiness \u00b7 doctor \u00b7 rebuild \u00b7 context \u00b7 closure \u00b7 retrieve \u00b7 checkpoint \u00b7 close \u00b7 adopt --lite \u00b7 pause`, plus the claim lock, and `launch`, the start command for worker sessions (DEC-153, DEC-161; not one of the twelve governance operations). **W2:** `impact \u00b7 readiness --generate \u00b7 discover` (DEC-166); `rebuild --integration`, the double-buffered integration store, and `launch` setting `GOV_STORE` (W2-116; DEC-1087 (3)); `links` (W2-129; DEC-1074 (7), DEC-1087 (4)); `plan` (W2-136, live at the lift's re-pin; DEC-1088); at the lift `launch` refuses a lead outside the approved batch or with unmet waits, and any session while the gate is shut or the machine's limits would be passed, with one recorded override (W2-136, W2-20; DEC-1088 (5)). **W3:** `claim` (concurrency) \u00b7 `route` \u00b7 `health` \u00b7 `research sync` \u00b7 `update --check` (W2-17, moved to Wave 3; DEC-1089 (2)) | code |\n",
      "tokens": 233
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-114 | A | **New (DEC-982, P1-NEW-TICKETS-2026-10-31 T2).** W1-28's whole-tree copy check reads code, not message text; every true copy still found (`DAEO-4eux`) | test-revision | independent-test-designer | LITE | none | 40 | DEC-982, DEC-385, DEC-906 |\n| W2-115 | A | **New (DEC-983, SMART-WORK-1 decision 1).** `gov close`, the smart close: scoped runs only, a close refused only by a red its own change caused, the culprit of a batch sent back, no lists, a close record, the nightly's full secrets scan; the strict close kept built; before EXAMIN's copy (`DAEO-emq1`) | implementation | engineer | FULL | W2-55 | 400 | DEC-983, DEC-982, DEC-968, DEC-953 |\n| W2-116 | A | **New (DEC-983, SMART-WORK-1 decision 2).** The designers' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, read by a test designer's retrieval; before EXAMIN's copy (`DAEO-f58b`) | implementation | engineer | STANDARD | W2-60b, W2-33 | 150 | DEC-983, DEC-982, DEC-963 |\n",
      "tokens": 256
    },
    {
      "id": "b524e1adb8703e59663d291f",
      "path": "docs/research/W2-88-memory-practice.md",
      "text": "## 7. What changed on 2026-11-06 and 2026-11-07 (DEC-1084 to DEC-1088; re-pin window 4)\n- **Freshness is a practice, not an accident.** The live store had gone 201 commits stale (11-04 to 11-06): queries\n  never re-index, and every refresh path had stopped. Now:\n  - W2-116's `reference-transaction` hook refreshes the integration store after every update of the integration\n    branch, double-buffered (`gov rebuild --integration`);\n  - a daily backstop runs at 10:00 and 18:00;\n  - the store is always rebuilt **with the code that searches it** (the pin). A store built by newer code can read as\n    stale to older code, so check one search before switching the link (`tools/rebuild_pinned.sh`).\n- **Workers search the integration store, not their worktree:** `GOV_STORE` is set by `gov launch`, or\n  `gov retrieve --root <the store>`. A worktree has no store of its own. Line numbers are the integration head's:\n  read the file in the worktree before relying on a line.\n- **Bundle hygiene:** a line over 4,000 characters is cut in a bundle item, marked `cut` with its line numbers, and\n",
      "tokens": 273
    },
    {
      "id": "868e890ee2e86be828d4d6b0",
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "text": "| L4 | `gov` CLI | **W1:** `status \u00b7 check \u00b7 readiness \u00b7 doctor \u00b7 rebuild \u00b7 context \u00b7 closure \u00b7 retrieve \u00b7 checkpoint \u00b7 close \u00b7 adopt --lite \u00b7 pause`, plus the claim lock, and `launch`, the start command for worker sessions (DEC-153, DEC-161; not one of the twelve governance operations). **W2:** `impact \u00b7 readiness --generate \u00b7 discover` (DEC-166); `rebuild --integration`, the double-buffered integration store, and `launch` setting `GOV_STORE` (W2-116; DEC-1087 (3)); `links` (W2-129; DEC-1074 (7), DEC-1087 (4)); `plan` (W2-136, live at the lift's re-pin; DEC-1088); at the lift `launch` refuses a lead outside the approved batch or with unmet waits, and any session while the gate is shut or the machine's limits would be passed, with one recorded override (W2-136, W2-20; DEC-1088 (5)). **W3:** `claim` (concurrency) \u00b7 `route` \u00b7 `health` \u00b7 `research sync` \u00b7 `update --check` (W2-17, moved to Wave 3; DEC-1089 (2)) | code |\n",
      "tokens": 233
    },
    {
      "id": "d94dd360e8fb33577ee0ecea",
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "text": "| D13 | `rerank_service_slot_hold.py` | S | holds every reranker GPU slot while the shared service runs | DEC-1036 | yes: pid 8416 since 11-04; log 15:27 (M) | yes | yes | ticket W2-145 exists (merged, live at the re-pin) | yes, then retire |\n| D14 | `rerank_reset_watch.sh` | S | restarts the shared reranker when its memory climbs | DEC-1067 (11-04 night) | no since 11-04 07:22 (M) | no | no | none (W2-112's cache emptying replaced it) | no, retire |\n| D15 | `new_worktree.sh` + `seed_store.py` | S | a lead's worktree with its store seeded warm | DEC-1032 (iv) | yes: `log/seed.jsonl` 15:05 (M) | yes | yes | already in product (W2-122, `gov rebuild --seed`, merged D-1) | yes, done (close at the lift) |\n| D16 | `refresh_integration_store.sh` + `rebuild_pinned.sh` + `store_refresh_daily.sh` | S (the last pre-emergency) | the designers' store, double-buffered, rebuilt with the pinned gov | DEC-963, DEC-1032 (iv), DEC-1087 (2)-(3) | yes: `store_refresh_daily.sh` pid 4003400 (M) | yes | yes | ticket W2-116 exists (pass 1 in product) | yes, W2-116 says so |\n",
      "tokens": 267
    }
  ],
  "supplementary_query": "Memory for any repository: at adoption, assess any repository however large, plan the refactoring it needs for full indexing as governed tickets for its owner to approve (never applied on their own), build the full index and the embeddings, set up the SQLite and vector-store structure\nThe assessment: before the target path map (A3), adoption writes a memory-assessment record for the repository. It holds tracked files and bytes, languages, commits, the largest files, binaries, generated, minified and vendored candidates (by name, header and folder), the files the secrets filter refuses (by rule id, never the value), the files no route can take (a language the code graph does not read, a file over the chunker's limit), and the estimated index time, peak RSS and disk against DEC-078's envelope and the machine's free memory and disk. It streams the tree and never loads it whole: on the largest proof repository its peak RSS is recorded and stays under the resource gate's per-session figure. The repository's tree, index and history are byte-identical before and after. Verify: on a planted repository (a vendored folder, a generated file, a minified file, a binary, a file over the chunker's limit, a secret in a tracked file, a language the code graph does not read) the memory-assessment record is written before A3 and holds every field named above, each planted item under its category and the secret by rule id only (a grep of every output for the planted secret's value finds 0 hits); a hash of the planted repository's tree, index and history before and after is identical; on the largest proof repository the recorded peak RSS is under the resource gate's per-session figure [DEC-954 Q9f, DEC-078, CAP-44.b]\nThe refactoring plan: every blocker to full indexing that the assessment finds becomes a proposed ticket in the kernel's ticket form (title, class, allowed paths, KPIs with success and failure, each KPI line with its `Verify:` clause [changed, DEC-1132 (2)], profile, sources citing the assessment) in the adoption's evidence folder. Blockers include: vendored or generated code with no folder of its own, a namespace that would need a value other than embedded or not embedded, files over the chunker's limit, a secret in a tracked file, and paths that would fall in no namespace or in two. No proposal is created with tk, applied or committed by the tool; the A5 human gate is the only route to them. A repository with nothing to refactor gets a record that says so. Verify: a planted repository with one case of each blocker kind yields, in the adoption's evidence folder, one proposed ticket per blocker in the kernel ticket form (title, class, allowed paths, KPIs with success and failure, profile, sources citing the assessment); `tk` ticket list and `git status` of the planted repository are the same before and after; a planted clean repository's record says there is nothing to refactor [DEC-954 Q9f, DEC-694, DEC-388, CAP-44.g]\nThe full index and the embeddings (A9 lite, after A6 and the owner's approval of the path map): the stage builds the record store, the lexical index, the semantic vectors for every embedded namespace and the code graph, with one rebuild at a time on the machine (W2-76's lock). Its record holds, per store: files judged, indexed and refused with the reason, chunks, vectors, nodes and edges, time and peak RSS. Every tracked file is either indexed or named with its reason (secrets filter, binary, namespace not embedded, unsupported language); a file in neither list fails the stage. Verify: a planted adoption run through A9 lite writes a record holding, per store, files judged, indexed and refused with the reason, chunks, vectors, nodes and edges, time and peak RSS; every planted tracked file is in the indexed list or the named list with its reason; a planted file in neither makes the stage not ok; a second rebuild started while one runs is refused by W2-76's lock [DEC-954 Q9f, CAP-44.f (A9, lite, by CIT-P note), CAP-17, CAP-20]\nThe structure: the store layout is stated once, in src/gov/store/layout.py: each store file, its tables and a layout version. The stage builds that layout, and the rebuild record carries a digest per store (the record graph, the lexical index, the vectors and the code graph), not only the record graph's. A store of another layout version is rebuilt, never read as current. Two A9 runs on one commit give the same per-store digests, apart from the code graph's bytes, which are reported, not compared. Verify: a grep of src/gov/store/layout.py finds the layout version and each store file with its tables; a planted adoption's rebuild record holds four digests (record graph, lexical index, vectors, code graph); a planted store of another layout version is rebuilt and never read as current; two A9 runs on one planted commit print equal digests for the first three stores and report the code graph's bytes without comparing them [DEC-954 Q9c, CAP-20, DEC-016]\nScale: on each synthetic proof repository (proof (a); the real ones are W2-88b's) the stage records the query time of one plain question on each route, and the vector scan's time against the retrieve budget. A figure over the budget or over DEC-078's envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan's time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store's files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]\nMemory works there, measured: on each synthetic proof repository (proof (a)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61's measure, and right end to end, wrong claims and hit@5 are reported. W2-81's per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN's copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61's measure; each real repository has its 10 questions with the writer's and checker's records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]\nThe proofs, recorded in docs/changes/W2-88-evidence.md (the implementer's evidence, DEC-996 (3) A; the real repositories' proofs (b) and (c) are W2-88b's, DEC-1150 (1)), each with its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure: Verify: docs/changes/W2-88-evidence.md holds a section for proof (a) and one for (d), and (a) names its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from the section finds none\n  (a) W2-81's five synthetic repositories (Python with drifted specs, a Rust workspace, a TypeScript monorepo, legacy documents with large files, a secret in history), built by W2-81's builders under ~/gov-os-runs/W2-88/proving-ground/. Verify: the proof record has a section for each of the five synthetic repositories (Python with drifted specs, a Rust workspace, a TypeScript monorepo, legacy documents with large files, a secret in history), each with a commit; the builders' output path is under ~/gov-os-runs/W2-88/proving-ground/ and `git status` of this repository shows none of it [DEC-941, DEC-954 Q9f]\n  (d) EXAMIN's copy is its live trial: W2-27 runs these tools on its clone at adoption, on W2-16's release; that run is W2-27's, not this ticket's. Verify: this ticket's proof record has no adoption run on EXAMIN's copy and names W2-27 for it; a planted check of this ticket's branch for a run of the adoption tools against ~/gov-os-workbench/examin/ finds none [DEC-954 Q9f, Q8c]\nA store of another layout version is never read as missing or as current: the store's open path (src/gov/store/loader.py, through layout.py) reads the layout version and refuses an older or newer one with STORE_LAYOUT_STALE naming both versions, and gov rebuild rebuilds it; the main tree's STORE_MISSING of 2026-10-30 (a store built before W2-03's span column) is a planted case. Verify: a planted store of an older layout version and one of a newer: the open path prints STORE_LAYOUT_STALE naming both versions for each and `gov rebuild` rebuilds it; a planted store built before W2-03's span column gives STORE_LAYOUT_STALE and never STORE_MISSING; a current store opens with no refusal [DEC-957, CAP-20]\nS10 The standard pinned at Wave 0: A9 lite builds and serves the store with Gov OS's memory standard: Qwen3-Reranker-0.6B through the machine's one shared reranker service (no private reranker), the pool on (retrieval.yaml's pool: block as Gov OS ships it), the 6,000-token bundle with its items widened to their sections, and the gov pin, the embedder, the reranker and the retrieval.yaml digest written in the A9 record. Any setting that differs from the standard is named in the record, and the stage is not ok unless the record cites the owner's decision id for it. Verify: on a planted adoption the A9 record names the four settings and the pin; a planted retrieval.yaml with the pool off, a second reranker or another bundle budget is named, and the result is not ok without a decision id [DEC-1098 (1), DEC-1097 (1)(a), DEC-1097 (5), DEC-1046 (1)] [added, DEC-1099 (2); DEC-1098 (1)]\nS11 The store current after every merge: adoption installs the refresh that this repository runs (practice record \u00a77): after each update of the repository's integration branch the store is rebuilt by the pinned code, double-buffered, so a failed build leaves the last good store in service; a daily backstop runs; every bundle names the commit its store was built at. Verify: on a planted repository, a merge followed by a query returns the new commit within the time the proof measured for a seeded rebuild; a planted failing build keeps the old store and reports the failure [DEC-1098 (1), DEC-1072 (2)] [added, DEC-1099 (2); DEC-1098 (1)]\nS12 The repository's own tuning set: about 80 questions, written blind under the rubric (docs/research/memory-measure-audit/RUBRIC.md, its version in force) by an independent writer, and cross-checked by an independent checker in at most two rounds. The checker lists every other place that states each answer. Both are sessions outside the retrieval work, opened by the owner's operator. The writer never reads search results and never finds gold with the product's search. The categories follow the fresh 80's twelve (callers, code paraphrase, exact string, multi-file, decision, ticket, plan, contract or spec, kernel or template, history, failure memory, nonexistent id), mapped to the repository's own domains. A category the repository has no domain for is dropped, and the drop is recorded. R5 applies: each domain at least 10 %, no subsystem over 25 %. There is at least one nonexistent-id question, scored apart. The set is split into two halves of 40: the first is used to choose fixes; the second is reported in counts only and never chooses. Source families (official copies) are declared in the path map. Verify: the set's checks in the proof record (path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS) [DEC-1098 (1), DEC-1070 (2)-(3), DEC-1074 (4), DEC-1069 (5), DEC-1076 (5), DEC-1078 (4), DEC-1071 (5), DEC-1010] [added, DEC-1099 (2); DEC-1098 (1)]\nS13 The fresh verdict set, used once: 80 questions, written by the same independent writer and checker under the same rubric, blind, before the first measure of the tuning set. None of its gold sources is a gold source of the tuning set. It is held outside every worktree in a folder of mode 700, declared in the path map's evaluation_sets with every role but the orchestrator refused, and the guard refuses the measured roles a read of the set and of its run folder (as ACT-GUARD-SETS-1). It is used once, as FRESH-80-1 did. First a counts-only pre-flight: the set's digest, how its anchors resolve at the measured commit, and whether each nonexistent id still exists nowhere. Then the checker's staleness pass at that commit. Then a declaration, committed before any search, naming the configuration (S10), the commit, the denominator with nonexistent-id questions apart, the bar and how it rounds (S14), any data conditions as data only, and the fault rule (FRESH-80-1 \u00a73.5). Then a control on the tuning set. A USED marker is written before the first search, and the runner refuses to start once it exists. The result record gives counts only. Verify: the declaration's commit is earlier than the USED marker; a planted USED makes the runner refuse; a planted read of the set by a measured role is refused by the guard [DEC-1098 (1), DEC-1097 (1)(b), (1)(g), DEC-1097 (2), DEC-1092 (4), DEC-1078 (3), DEC-1074 (1)] [added, DEC-1099 (2); DEC-1098 (1)]\nS14 The bar: on the verdict set, judged on the declared configuration only. The figure is right end to end: the answer correct and its citation right, graded by a named grader model, with a second grader's agreement reported. It must be at least 85 % with wrong claims at most 5 %; the target is 95 %. On n judged questions that is at least ceil(0.85 n) right and at most floor(0.05 n) wrong claims. Reported beside it, never judged: hit@5, gold in the first bundle, the answer correct with the citation set aside, the stricter grade, one search against two (exact McNemar), the exact 95 % interval, and the reader model by name. Verify: the result record in docs/research/W2-88-any-repository.md (or the adopted repository's copy of it) holds the verdict line and the side table [DEC-1097 (1)(d), DEC-1098 (1), DEC-957, CAP-10, DEC-1079] [added, DEC-1099 (2); DEC-1098 (1)]\nS15 Search again once in the adopted repository: adoption copies, unchanged, the kernel's retrieval skill with step 7 (W2-142 S1), the discovery skill's line (W2-142 S2) and T-0's and T-8's \"Search again once\" line (W2-128's line). Nothing is re-worded per repository. The verdict's judged condition is up to two searches (A2). Verify: a string test on a planted adoption's generated skill and T-0 for \"search again once\", \"own, different words\", \"not found\" and \"two searches\" [DEC-1098 (1), DEC-1094 (2), DEC-1092 (1)] [added, DEC-1099 (2); DEC-1098 (1)]\nS16 A miss is a result. A verdict below either limit stands as recorded. It is never run again, never re-scored to pass, and its labels are never changed after its figures exist. The spent set becomes a diagnostic set. An independent auditor classifies its misses by kind, counts only: never retrieved, ranked low, vocabulary, correct answer citing an unlisted place, other. The result goes to the repository's owner with options: structural fixes judged on the tuning set and then a new fresh set used once, or the figure accepted as a named residual with its cause. The store stays in service. The four settings of S10 change only by Gov OS's owner's decision (a CIT-P), never at the adopted repository. Verify: the result record's miss section on a planted miss (stand-in figures); the runner refuses a set marked USED [DEC-1098 (1), DEC-1074 (1)-(2), DEC-1071 (1), DEC-1083 (2), DEC-954 Q9e, DEC-1070 (14)] [added, DEC-1099 (2); DEC-1098 (1)]\nS18 The audit's schedule at adoption: an adopted repository is audited on the same rhythm by the same tool (weekly while active, monthly once stable, by W2-172's rule). Adoption writes the repository's audit record: its sets root, its audit names, its mode, the three briefs' variant ids and their sha256, and the first audit's earliest date. It starts no audit and installs no schedule line itself (the crontab is an ACT). Verify: a planted adoption writes the record with those fields; a grep of the planted crontab and sets root before and after finds no change [DEC-1101 (1)-(2), DEC-1125 (2)] [added, DEC-1101 (1), DEC-1125 (2)]\nS19 The briefs' variants, approved once: the adopted repository's writer, checker and auditor briefs are the Gov OS briefs (`governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/`, once approved) with two parts replaced by the repository's own: the domain table (the writer's section 5 items 1 and 3, the checker's section 5a) mapped from S12's twelve categories to the repository's domains, with every dropped category recorded, and the list of records the audit stays blind to. Nothing else changes. Each variant is approved once by the repository's owner and hashed; a launch under an unapproved variant is refused. Verify: a planted adoption's variants differ from the Gov OS briefs only in those two parts (a diff test); a launch under a variant not on the planted approved list exits 10 [DEC-1101 (2), DEC-1099 (2)] [added, DEC-1101 (1), DEC-1125 (2)]\nS20 One core, not two: `src/gov/adopt/memory_sets.py` calls `gov.memaudit` (W2-170's checks and declaration, W2-171's measure and pool) and defines no pre-flight, use-once marker or figures of its own. Verify: a test that the module imports from `gov.memaudit` and defines none of those functions; S12's and S13's planted runs produce the same declaration and verdict line as the audit's [DEC-1101 (1), DEC-1099 (2), DEC-1125 (2)] [added, DEC-1101 (1), DEC-1125 (2)]\nS21 The first scheduled audit follows the verdict set: an adopted repository's first scheduled audit runs only after its verdict set (S13) was used and its result record written; the audits' log starts at the verdict set's commit (`gov.memaudit baseline`), and the tuning and verdict sets join the repository's pool. Verify: a planted adoption before S13's USED marker: `due` says `not due: no verdict set used`; after it: the baseline line holds the verdict commit [DEC-1101 (1), DEC-1098 (1)] [added, DEC-1101 (1), DEC-1125 (2)]\nS22 The walls for an adopted repository by one ACT: adoption writes one ACT package for the repository's owner's operator: the walls' template copy, the sets root folder (mode 0700), the approved list with the three variant briefs, and the path-map hidden globs. Adoption never applies it. Verify: a planted adoption writes the package and changes nothing in the planted sets root or path map [DEC-1101 (2)-(3), DEC-1099 (2)] [added, DEC-1101 (1), DEC-1125 (2)]\nS23 The audit's cost is stated at adoption: the adoption record gives, for the repository's set size, the estimated tokens and USD per audit, the GPU minutes and the owner's minutes, from `governance/project/orchestration/packages/MEMORY-AUDIT-1.md` section 7, and names the figure to replace once the first audit has measured them. Verify: a string test on a planted adoption record for the four figures [DEC-1101 (3)] [added, DEC-1101 (1), DEC-1125 (2)]\nAnything written, moved, committed or deleted in a repository by the assessment or the refactoring plan; a proposed ticket created with tk or applied without the owner. Verify: a hash of a planted repository's tree, index and history and its `tk` ticket list before and after the assessment and the plan are identical; no tk create or apply call appears in the call log; any difference is a failure\nA tracked file neither indexed nor named with its reason; a store not built reported ok. Verify: a planted tracked file left out of both lists makes the stage not ok; a planted adoption where a store the path map calls for was not built never prints ok\nA store of another layout version read as current; a rebuild record whose only digest is the record graph's. Verify: a planted store of another layout version is refused with STORE_LAYOUT_STALE, never opened as current; a planted rebuild record is checked for the four per-store digests and is refused if only the record graph's is present\nThe assessment loading the whole tree in memory, or exceeding the resource gate's per-session figure on the largest proof repository. Verify: the assessment's recorded peak RSS on the largest proof repository is under the resource gate's per-session figure, and a test on a planted large tree shows the memory growing with the largest file, not with the tree's size\nA secret's value in any record, log or output; a hidden question read or printed. Verify: a grep of every record, log and output of a planted run for the planted secret's value finds 0 hits; the guard's log of the run holds no read of a hidden question and a grep of the outputs for a planted hidden question's unique word finds 0 hits [re-worded, DEC-1084]\nA verdict set read by a measured role, measured twice, or used to choose anything; a declaration committed after the first search. Verify: a planted read of the set by a measured role is refused by the guard; a planted USED marker makes the runner refuse a second measure; the declaration's commit is earlier than the first search in the ledger; the tuning set's fixes cite no verdict question [added, DEC-1099 (2); DEC-1098 (1)]\nA store served with a setting other than the standard's and no decision id in the A9 record. Verify: a planted retrieval.yaml with the pool off, a second reranker or another bundle budget and no decision id in the A9 record makes the stage not ok and the setting is named [added, DEC-1099 (2); DEC-1098 (1)]\nA tuning or verdict question written with the product's own search, or by a session in the retrieval work. Verify: the writer session's log holds no call of the product's search and the writer's session id is not among the retrieval work's sessions; a planted question whose record names a search call or a retrieval-work session is refused by the checker [added, DEC-1099 (2); DEC-1098 (1)]\nAn audit started by adoption; a variant brief launched without the repository owner's approval; a second copy of the pre-flight, the use-once marker or the figures in `src/gov/adopt/`. Verify: a planted adoption leaves the audits' log and the crontab unchanged and starts no audit process; a launch under a variant brief not on the planted approved list exits 10; a grep of src/gov/adopt/ finds no definition of the pre-flight, the use-once marker or the figures outside the import from gov.memaudit [added, DEC-1101 (1), DEC-1125 (2)]",
  "further_batch": [
    {
      "id": "e3124b68fd42c768b2f60b3a",
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md"
    },
    {
      "id": "d710c8703a18339c511db484",
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md"
    },
    {
      "id": "41e2416823e8b89a96d80fbf",
      "path": "governance/project/orchestration/packages/LIFT-1/MEMORY-INVENTION-DISCLOSURE.md"
    },
    {
      "id": "4a1adba99543b3d31b1ce407",
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md"
    },
    {
      "id": "1c07f12a4a0f83688ceead7a",
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md"
    },
    {
      "id": "7887ea8543f6b7476da39ef5",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
    },
    {
      "id": "8f7e0b669974b3babc062d3d",
      "path": "src/gov/rebuild/command.py"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "DAEO-aks1",
          "path": ".tickets/DAEO-aks1.md"
        },
        {
          "id": "18118c21c89f363827876872",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md"
        },
        {
          "id": "DEC-1150",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "7c99160bec6d01c496740381",
          "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md"
        },
        {
          "id": "1635e0d13b9641267936680e",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "DAEO-f58b",
          "path": ".tickets/DAEO-f58b.md"
        },
        {
          "id": "DEC-982",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "ADR-0002",
          "path": "docs/adr/ADR-0002-architecture-and-stack.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "b524e1adb8703e59663d291f",
          "path": "docs/research/W2-88-memory-practice.md"
        },
        {
          "id": "868e890ee2e86be828d4d6b0",
          "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft"
        },
        {
          "id": "d94dd360e8fb33577ee0ecea",
          "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md"
        },
        {
          "id": "e3124b68fd42c768b2f60b3a",
          "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md"
        },
        {
          "id": "d710c8703a18339c511db484",
          "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md"
        },
        {
          "id": "41e2416823e8b89a96d80fbf",
          "path": "governance/project/orchestration/packages/LIFT-1/MEMORY-INVENTION-DISCLOSURE.md"
        },
        {
          "id": "4a1adba99543b3d31b1ce407",
          "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md"
        },
        {
          "id": "1c07f12a4a0f83688ceead7a",
          "path": "governance/project/orchestration/packages/SMART-WORK-1.md"
        },
        {
          "id": "7887ea8543f6b7476da39ef5",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "8f7e0b669974b3babc062d3d",
          "path": "src/gov/rebuild/command.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "1c07f12a4a0f83688ceead7a",
      "reason": "budget exceeded"
    },
    {
      "id": "41e2416823e8b89a96d80fbf",
      "reason": "budget exceeded"
    },
    {
      "id": "4a1adba99543b3d31b1ce407",
      "reason": "budget exceeded"
    },
    {
      "id": "7887ea8543f6b7476da39ef5",
      "reason": "budget exceeded"
    },
    {
      "id": "8f7e0b669974b3babc062d3d",
      "reason": "budget exceeded"
    },
    {
      "id": "d710c8703a18339c511db484",
      "reason": "budget exceeded"
    },
    {
      "id": "e3124b68fd42c768b2f60b3a",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-2bdu): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 59866,
  "budget": {
    "limit": 60000,
    "used": 59866
  },
  "hash": "25af05571f31c1f8a65bdb581f03713a4786b5530d08fb11401a1b7b0ee7645d"
}
