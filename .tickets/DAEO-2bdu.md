---
id: DAEO-2bdu
status: open
deps: [DAEO-ym8a, DAEO-siiz, DAEO-tgk2, DAEO-l78m]
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
- template/governance/kernel/skills/adopt/SKILL.md
- template/.rulesync/skills/adopt/SKILL.md
- .rulesync/skills/adopt/SKILL.md
- .claude/skills/adopt/SKILL.md
- tests/unit/adopt/test_w2_88*
- tests/unit/rebuild/test_w2_88*
- docs/research/W2-88-any-repository.md
- docs/changes/W2-88-CIT-P.md
kpis:
  success:
  - 'The assessment: before the target path map (A3), adoption writes a memory-assessment record for the repository. It holds tracked files and bytes, languages, commits, the largest files, binaries, generated, minified and vendored candidates (by name, header and folder), the files the secrets filter refuses (by rule id, never the value), the files no route can take (a language the code graph does not read, a file over the chunker''s limit), and the estimated index time, peak RSS and disk against DEC-078''s envelope and the machine''s free memory and disk. It streams the tree and never loads it whole: on the largest proof repository its peak RSS is recorded and stays under the resource gate''s per-session figure. The repository''s tree, index and history are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-44.b]'
  - 'The refactoring plan: every blocker to full indexing that the assessment finds becomes a proposed ticket in the kernel''s ticket form (title, class, allowed paths, KPIs with success and failure, profile, sources citing the assessment) in the adoption''s evidence folder. Blockers include: vendored or generated code with no folder of its own, a namespace that would need a value other than embedded or not embedded, files over the chunker''s limit, a secret in a tracked file, and paths that would fall in no namespace or in two. No proposal is created with tk, applied or committed by the tool; the A5 human gate is the only route to them. A repository with nothing to refactor gets a record that says so [DEC-954 Q9f, DEC-694, DEC-388, CAP-44.g]'
  - 'The full index and the embeddings (A9 lite, after A6 and the owner''s approval of the path map): the stage builds the record store, the lexical index, the semantic vectors for every embedded namespace and the code graph, with one rebuild at a time on the machine (W2-76''s lock). Its record holds, per store: files judged, indexed and refused with the reason, chunks, vectors, nodes and edges, time and peak RSS. Every tracked file is either indexed or named with its reason (secrets filter, binary, namespace not embedded, unsupported language); a file in neither list fails the stage [DEC-954 Q9f, CAP-44.f (A9, lite, by CIT-P note), CAP-17, CAP-20]'
  - 'The structure: the store layout is stated once, in src/gov/store/layout.py: each store file, its tables and a layout version. The stage builds that layout, and the rebuild record carries a digest per store (the record graph, the lexical index, the vectors and the code graph), not only the record graph''s. A store of another layout version is rebuilt, never read as current. Two A9 runs on one commit give the same per-store digests, apart from the code graph''s bytes, which are reported, not compared [DEC-954 Q9c, CAP-20, DEC-016]'
  - 'A store not built is never ok: gov rebuild on a repository where the path map or .gitleaks.toml is missing, or where a store the path map calls for was not built, names each store not built with its reason, and its result is not ok. A rebuild with --no-embeddings stays ok for the vectors it was told not to build, and says so. W2-26''s finding 2 is a planted case [DEC-954 Q9f, W2-26 finding 2, DEC-530]'
  - 'Scale: on each proof repository the stage records the query time of one plain question on each route, and the vector scan''s time against the retrieve budget. A figure over the budget or over DEC-078''s envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store [DEC-954 Q9f, DEC-078, CAP-19]'
  - 'Memory works there, measured: on each proof repository after A9, the repository''s question set is run with W2-61''s measure, both figures together. W2-81''s per-repository sets apply to the synthetic repositories; 10 questions with gold sources apply to each real GitHub repository, written by this ticket''s independent test designer at a pinned commit. Both figures are reported: hit@5 against CAP-10''s floor of 85 and the owner''s target of 95 % (DEC-957), full evidence against 99 %. On W2-81''s five synthetic repositories hit@5 is at least 85 on the visible half. A figure short of its floor is a named residual with its cause, and goes to the owner under DEC-954 Q9e [DEC-833, DEC-860, CAP-10]'
  - 'The proofs, recorded in docs/research/W2-88-any-repository.md, each with its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure:'
  - '  (a) W2-81''s five synthetic repositories (Python with drifted specs, a Rust workspace, a TypeScript monorepo, legacy documents with large files, a secret in history), built by W2-81''s builders under ~/gov-os-runs/W2-88/proving-ground/ [DEC-941, DEC-954 Q9f]'
  - '  (b) two real, messy, public GitHub repositories of different languages and sizes. Candidates for the test designer or the owner to confirm, each pinned to a commit: a large polyglot monorepo with generated code and large fixtures (for example grafana/grafana, Go and TypeScript, of the order of 10^4 files), and a mid-size repository of another language with vendored dependencies in its tree (for example redis/redis, C, with deps/). They are cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88/github/<name>/, with their licence recorded, never committed and never pushed anywhere [DEC-954 Q9f]'
  - '  (c) the test repositories the register names, each read through a clone under ~/gov-os-runs/W2-88/: ~/workspace (DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope''s top); the dev tiers ~/gov-os-workbench/synthetic/a-dev (ORION) and b-dev (ARGUS) (DEC-071, DEC-630); ARGUS''s stress tier (DEC-071: 5,355 files, 57,777 chunks) only if it lies outside the held-out qualification material; the assessment step only, never an adoption, on a clone of EXAMIN''s copy ~/gov-os-workbench/examin/ (DEC-723), to feed W2-27 [DEC-954 Q9f]'
  - '  (d) EXAMIN''s copy is its live trial: W2-27 runs these tools on its clone at adoption, on W2-16''s release; that run is W2-27''s, not this ticket''s [DEC-954 Q9f, Q8c]'
  - 'A store of another layout version is never read as missing or as current: the store''s open path (src/gov/store/loader.py, through layout.py) reads the layout version and refuses an older or newer one with STORE_LAYOUT_STALE naming both versions, and gov rebuild rebuilds it; the main tree''s STORE_MISSING of 2026-10-30 (a store built before W2-03''s span column) is a planted case [DEC-957, CAP-20]'
  failure:
  - 'Anything written, moved, committed or deleted in a repository by the assessment or the refactoring plan; a proposed ticket created with tk or applied without the owner.'
  - 'A tracked file neither indexed nor named with its reason; a store not built reported ok.'
  - 'A store of another layout version read as current; a rebuild record whose only digest is the record graph''s.'
  - 'The assessment loading the whole tree in memory, or exceeding the resource gate''s per-session figure on the largest proof repository.'
  - 'A clone of a GitHub repository, or any of its files, in this repository or in a commit; a clone outside ~/gov-os-runs/W2-88/; a write in the workbench, EXAMIN''s real repository or the held-out qualification material.'
  - 'A secret''s value in any record, log or output; a figure of the measure reported without the other; a hidden question read or printed.'
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
est_loc: 500
acceptance_tests:
  path: tests/acceptance/W2-88/
  author: independent-test-designer (MR-3); written before implementation. Small repositories are planted in temporary folders (a vendored folder, a generated file, a file over the chunker's limit, a secret in a tracked file, a path with no namespace, a binary, a language the code graph does not read), W2-81's builders are reused read-only, and stand-ins are used for the embedder and the code graph where a case needs none. No network, no real clone and never this repository's store. The 10 questions per real repository and the choice and commit of the two GitHub repositories are this designer's too.
track: A
list_rows: []
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
