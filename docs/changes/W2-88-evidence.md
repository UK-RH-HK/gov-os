# W2-88 (DAEO-2bdu) evidence: Memory for any repository

The implementer's evidence (DEC-996 (3) A; DEC-1150 (1)). Counts, ids, digests and figures only: nothing of a
repository's content, no secret value. Proofs (b) and (c) are W2-88b's; the Contract CIT-P is W2-88a's.

## Seams (P-1, P-4, P-6, P-10; the three values)

Batch 1 of run 3, committed alone for the test designer's narrow revision. After this commit a seam's name or form
changes only with a later commit's subject saying so, and the return naming it. Every path:line is of this branch at
`b482fc5bf` (the base of run 3).

### 1. P-1 (a): the retrieve budget's source

- **Found in the code: no budget for the vector scan.** `budget_ms` is defined nowhere under `src/gov/`. The nearest
  budgets are token budgets, not times: `src/gov/retrieval/retrieve.py:48` `BUNDLE_BUDGET = 6000` (tokens) and
  `src/gov/retrieval/semantic.py:92` `TIMEOUT_S = 120.0` (an embedder request's time-out, not a scan). DEC-078 (the
  register, line 509 to 513) states an envelope of nodes, edges and RSS, no query time.
- **The seam:** a constant `fabric.RETRIEVE_BUDGET_MS = 2000` (proposed: the owner or the lead confirms the figure;
  the code gives none). It is the default of `scale.budget_ms`.
- **How a lower budget is planted:** the flag `gov adopt --lite --stage A9 --budget-ms <N>` (a positive whole number),
  and the same as `fabric.a9`'s `run.args.budget_ms`. It is not a key of `retrieval.yaml`: `gov.config.loader`
  refuses any key of that file other than `routing` and `pool` (see item 4). The module constant may also be set by
  a test (`monkeypatch.setattr(fabric, "RETRIEVE_BUDGET_MS", n)`).
- **Over the budget** is `vector_scan_ms > budget_ms`; **over the envelope** is nodes above 80,000, edges above
  270,000 or the stage's peak RSS above 2.2 GB (`assess.ENVELOPE`, DEC-078). Either writes `<out>/SCALE-PROPOSAL.md`.

### 2. P-1 (b): A9's question-set input

- **The flag:** `--questions <file>` (a file outside the project; one YAML or JSON file).
- **Its form** (`form: w2-88-questions/1`): `questions: [ {id, question, gold: [<path>, ...], forbidden: [<path>, ...]} ]`.
  One question holds `id` (string, unique), `question` (the text asked), `gold` (the paths whose text answers it, at
  least one) and `forbidden` (optional: paths no top-five citation may name, W2-81's rule). No question's text or gold
  path is ever written to a record, log or output: the record names questions by id only.
- **What is measured** (no reader model runs in A9; the reader's grade is W2-27's first full run):
  `hit_at_5` is the share of questions with a gold path among the first five evidence items and no forbidden path
  among them; `right_e2e` is the share whose stacked evidence holds every gold path and no forbidden path in the top
  five (the evidence side of "right end to end"); `wrong_claims` is the count of questions with a forbidden path in
  the top five. `residuals[{name, cause}]` names each shortfall and its cause; one standing residual says that the
  reader's grade is not run here.
- **The default, for a synthetic repository:** **none in the code.** A `src/` module must not read
  `tests/acceptance/`. W2-81's per-repository sets are templates (`questions/<name>.yaml`) resolved against a built
  repository's manifest by `w2_81_questions.resolve`; the proving-ground script of this ticket resolves them and writes
  the file form above (gold = the resolved sources' paths, forbidden = the resolved forbidden paths), then passes it as
  `--questions`. **For a repository with none** (no `--questions`), the measure block says
  `{right_e2e: null, wrong_claims: null, hit_at_5: null, residuals: [{name: "questions", cause: "no question set was given"}]}`
  and the stage stays ok (no bar). The lead decides whether the designer's default case reads W2-81's sets through
  the proof script or through the flag only.

### 3. P-4: `fabric.check_coverage(record, tracked)`

- **Signature:** `check_coverage(record: dict, tracked) -> None`. `record` is the A9 record's data (a dict with
  `stores`: each store `{judged, indexed, refused, ...}`); `tracked` is any iterable of tracked file paths (the
  paths of HEAD, the adoption folder `governance/adoption/` excluded).
- **The store forms it reads:** `judged` is a count (int); `indexed` is the list of the paths the store holds;
  `refused` is a list of `{path, reason}` (reason one of `secrets`, `binary`, `not-embedded`, `unsupported-language`,
  `over-limit`; a file that a namespace keeps out of the index, by its `lexical_policy` or because its memory class is
  not governance, is `not-embedded`, the enum's word for "the namespace does not take it").
- **What it raises:** `GovError("FABRIC_INCOMPLETE", "<n> tracked file(s) are in neither the indexed list nor the
  refused list of the store that judges them: <paths>", {"missing": [<path>, ...]})`. The exact details key is
  `missing` (a sorted list of paths). The store that judges a file is the lexical store for every tracked file; the
  vector store additionally for a file of an embedded namespace; the code graph for a file of a language it reads. A
  file is covered when it is in the indexed list or the refused list of each store that judges it. A store the path
  map calls for and that was not built is `{"missing": [...]}` too, with the store's name in the message.
- **A9's `ok`:** `fabric.a9` calls `check_coverage` on the record it built; the stage is not ok through the
  `FABRIC_INCOMPLETE` error it raises.
- **S3's "refused by W2-76's lock":** read as "never two at once": `gov.rebuild.watch.take` (`watch.py:184` to
  `216`) takes `fcntl.flock(LOCK_EX | LOCK_NB)` and, when another holds it, waits with a blocking `LOCK_EX`
  (`watch.py:210`): a second rebuild waits, serialised. No change to the lock.

### 4. P-10: the `retrieval.yaml` key of each `fabric.STANDARD` setting

- **What the file is today.** `governance/project/retrieval.yaml` as Gov OS ships it holds two blocks only:
  `routing:` (`code_first`, `named_first`, `phrasings`) and `pool:` (`meaning_uncut`, `route_depth`, `rerank_depth`,
  `per_file_first10`, `drop_nested`).
- **`gov.config.loader` refuses unknown keys: yes.** `src/gov/config/loader.py:40` `RETRIEVAL_SCHEMA` has `routing` and
  `pool` only; `_validate_retrieval` (`loader.py:272` to `275`) raises `CONFIG_INVALID` ("unknown key") for any other
  top-level key, and for any key of `routing` or `pool` outside `ROUTING_KEYS` and `POOL_KEYS` (`loader.py:277`,
  `loader.py:288`). So only the pool has a key today; the other four settings are code constants of the pinned gov.
- **The map, setting by setting:**

| `fabric.STANDARD` setting | the key in `retrieval.yaml` (what `fabric` reads) | the code it stands for today |
|---|---|---|
| `pool` | `pool:` (the block; on = `pool.meaning_uncut: true`, the helper `gov.memaudit.declare.pool_on`, `declare.py:163`); a departure is `pool_on` false | `gov.config.loader.POOL_KEYS` (`loader.py:45`) |
| `reranker` | `rerank.model` (absent: the pin's `gov.retrieval.rerank.MODEL`, `rerank.py:29`, `Qwen/Qwen3-Reranker-0.6B`) | `rerank.py:29` |
| `reranker_service` | `rerank.service` (absent: `shared`; any other value, e.g. `private`, is "a second reranker") | the one shared service, `~/.cache/gov-os/rerank.sock` (`gov.retrieval.rerank`) |
| `bundle_tokens` | `bundle.tokens` (absent: `gov.retrieval.retrieve.BUNDLE_BUDGET`, `retrieve.py:48`, 6000) | `retrieve.py:48`, flag `--bundle-budget` |
| `widen` | `bundle.widen` (absent: `sections`; a child hit widened to its parent within the budget, `retrieve.py:680` to `686`; there is no setting for it) | `retrieve.py:680` to `686` |

- **How "a second reranker" shows:** `rerank: {service: private}` (or any `rerank.service` other than `shared`), or a
  `rerank.model` other than `Qwen3-Reranker-0.6B`. `fabric.a9` reads these keys from the raw file with
  `gov.memaudit.declare.retrieval(repo, commit)` (`declare.py:151`: the bytes and the parsed mapping, no schema), so the
  stage judges the file as the audit's declaration does, and writes `departures[{setting, value, decision}]`.
- **A consequence the lead decides (a package, not built here):** a live repository whose `retrieval.yaml` carries
  `rerank:` or `bundle:` is refused by `gov.config.loader` as `CONFIG_INVALID` before any stage runs (a fail-closed
  refusal, not `STANDARD_DEPARTURE`). `fabric.a9` reached with a run built by hand (the planted unit case) gives
  `STANDARD_DEPARTURE`. To make the CLI path name the departure, `RETRIEVAL_SCHEMA` and `_validate_retrieval` in
  `src/gov/config/loader.py` (not in this ticket's paths) would add `rerank` and `bundle`; that is a package. The
  four standard values are also written in the record's `standard` block from the pin's code (`rerank.MODEL`,
  `retrieve.BUNDLE_BUDGET`), so a pin whose constants differ from the standard is a departure too.

### 5. P-6: the stage that copies the kernel's retrieval skill and T-0

**None.** No stage of `gov adopt --lite` copies a kernel skill or T-0 into the adopted repository:

- `stages.py:497` `STAGE` holds `A0` to `A8` and `A10`. `A0` writes `.gitleaks.toml` and the `.gov-runtime/` ignore
  line only (`safety.py:41` `setup`); `A1` to `A6` read and move; `A8` imports legacy rule files and leaves the
  adapter generation "not run by this stage" (`legacy.py:238`; the step that follows is `rulesync generate ... skills`,
  `legacy.py:28`), which writes `.claude/skills/` from `.rulesync/` and copies nothing from the kernel by itself.
- T-0 is filled by `gov brief` (`src/gov/brief/command.py:3`) from `template/governance/kernel/templates/brief.md`;
  it is not copied at adoption.

So S15's copy has no existing stage. I add **no copy code**. The lead returns the case as a package (it is not moved to
W2-88a, P-6 (a)).

### 6. The three values

| value | figure | where it comes from |
|---|---|---|
| `assess.FILE_LIMIT_BYTES` | **1,048,576 B (1 MiB), the proposal stands: no byte limit is stated in the code.** | The chunker bounds a line, not a file: `chunking.py:29` `READ_CHARS = 32768`; the embedder cuts a chunk at `semantic.py:88` `EMBED_LIMIT_CHARS = 10_000`; `secrets/__init__.py:60` `_LARGE = 64 << 20` only throttles the scan's memory. The rebuild code (`rebuild/command.py`) holds no size limit. "Over the chunker's limit" is therefore: a file over `FILE_LIMIT_BYTES` **or** with a line over `READ_CHARS` (32,768). |
| the code graph's languages | **`assess.CODE_GRAPH_SUFFIXES`, the engineer's list, unconfirmed.** | `gov.codeintel` states none: `codeintel/__init__.py:37` names the tool (`codebase-memory-mcp`, 0.11.0 here) and `index` (`codeintel/__init__.py:293`) copies what `gov.secrets.indexable` returns; the tool decides which language it reads, and `codebase-memory-mcp --help` lists none. The list: `.py .pyi .js .jsx .mjs .cjs .ts .tsx .rs .go .java .kt .c .h .cc .cpp .hpp .cs .rb .php .swift .scala .sh .lua`. A file whose suffix is in no list and is no document is `no_route` with reason `unsupported-language`. The lead or the CTO confirms it against the tool on the machine that has it. |
| the retrieve budget | `fabric.RETRIEVE_BUDGET_MS = 2000` (proposed) | item 1: no budget in the code; the flag `--budget-ms` plants a lower one. |

The per-session figure is read from `gov.resources.config` (`working_size_bytes`) and never restated here.

### 7. What changed in a seam's form after this commit (said here, in batch 2c's subject and in the return)

- `memory-assessment.json` carries a `paths` list (every tracked path, sorted): the plan judges `no-namespace` and
  `two-namespaces` from it. No file but `memory-assessment.json` and `refactor-plan/*.md` is written under `--out`.
- A vendored or generated item found `by: folder` is never a blocker (it has a folder of its own); a `name` or `header`
  item is one (`vendored-no-folder`, `generated-no-folder`) unless it lies in a folder that holds nothing but flagged
  files of that kind (that folder is the code's own).
- `no-namespace` and `two-namespaces` proposals list the path map and the files in `allowed_paths`.
- A9's lists follow what the stores hold: the keyword index's `indexed = 0` for a namespace whose `memory_class` is not
  governance is `not-embedded` (`gov.secrets.indexable` lets through governance memory only; the reason stays in the
  five-word enum), a file the index holds as indexed whose first 8,000 bytes hold a zero byte is refused `binary`, and
  the record store judges the files that carry records (`judged` = `indexed`, `refused` empty) and reports `nodes` and
  `edges` (its records and edges).
- The peak RSS is the process's own `VmHWM` (`assess.peak_rss`), not `ru_maxrss`, which a process started by a large
  parent carries from the parent's copy.
- `check_coverage` also raises `FABRIC_INCOMPLETE` (details `not_built`) for a store the path map calls for that is
  absent from the record's `stores`, or marked `built: false` or `status: not_recreated`.

## Proof (a): W2-81's five synthetic repositories, adopted to A9 lite with a stand-in embedder

Built by W2-81's builders (`tests/acceptance/W2-81/w2_81_build.py`, read and run, never edited) under
`~/gov-os-runs/W2-88/proving-ground/` (the exact path: `/home/usain/gov-os-runs/W2-88/proving-ground/`, outside this
repository; `git status` of this repository shows none of it). Seed: W2-81's default; the large files of the legacy
documents at the real run's size (48 MiB each). Each repository: a path map (one namespace, `embedding_policy:
embedded`, `memory_class: governance`) and Gov OS's shipped `retrieval.yaml` committed, then A0, A1, A2, MA, A3
(`--assessment`; the proposal holds no action: every artefact kept), A4, A5 (the verdict commit is the proof's stand-in
for the independent auditor: `Role: independent-auditor`), A6, A8 and A9 (`--questions` from W2-81's visible set,
resolved by `w2_81_questions.resolve`). One process per repository: its peak is its own.

**What stands in, said once.** (1) The embedder: no model runs in the sandbox (DEC-1064, DEC-1065), so the vectors are
a hash of each chunk, written as the real stage writes them; there is no embedder manifest, so the semantic route
answers unavailable and retrieval is the keyword and code routes. The measure below is therefore not a measure of the
standard. (2) The code graph: `codebase-memory-mcp index_repository` exits 1 in this sandbox, so the path map's
`code_intelligence` is off here: the code graph is "not asked for" (`requested: false`), nodes and edges 0. (3) The
rebuild lock: `/tmp` is read-only here, so `GOV_REBUILD_LOCK` names a file in the sandbox's own temp folder; it is the
same lock, one rebuild at a time. (4) The reader: no reader model runs in A9; `right_e2e` is the evidence side (every
gold path stacked, no forbidden path in the first five). The lead re-runs the proof outside the sandbox with the real
embedder, the code graph and the reranker. The figures are data and set no bar (DEC-954 Q9e).

**The largest proof repository** is the legacy documents (19 files, 100,671,458 bytes).
Its assessment's **peak RSS** is 41,230,336 bytes, against the resource gate's
**per-session figure** of 805,306,368 bytes (`working_size_bytes`, read from
`gov.resources.config` by the assessment itself): under it. The A9 stage's own high-water mark on that repository is
1,083,609,088 bytes: it is the rebuild's, which the gate bounds by `rebuild_peak_bytes`
(7,582,199,808 B on this machine), not by the session figure.

### Python with drifted specs (python-app)

- **commit:** built at `feadf6088cca`; assessed at `2db3994aae90` (after A2); A9's record committed at `2c3959f12b87`.
- **size:** 23 files, 9,271 bytes, 12 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take; the estimate: 25 s to index, 76,682,730 B estimated peak RSS, 1,943,912 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,556,096 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 21, 21, 0 (reasons: none), 54 chunks, 0.0 s; vectors 20, 20, 0, 54 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 42.2 s of the rebuild's stage. The A9 stage's high-water mark 66,129,920 B. Digests: record `6970274f0134`, lexical `79e7d8df7061`, vectors `ae9c25625530`, code graph 26,742 bytes (reported, not compared).
- **scale:** lexical 6.2 ms, semantic 1.7 ms (the stand-in's route), retrieve 12.7 ms; the vector scan 1.7 ms against the budget 2,000 ms; no `SCALE-PROPOSAL.md`.
- **measure** (11 questions): right end to end 54.5 %, wrong claims 4, hit@5 45.5 %; 7 residuals named with their cause (4 forbidden path in the first five, 2 no gold path among the first five items, 1 the standing reader residual).

### Rust workspace (rust-workspace)

- **commit:** built at `9f10774ca647`; assessed at `18a4f268e57e` (after A2); A9's record committed at `750b8b9ba66f`.
- **size:** 22 files, 8,929 bytes, 11 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take; the estimate: 24 s to index, 67,934,850 B estimated peak RSS, 1,087,508 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,576,576 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 20, 20, 0 (reasons: none), 46 chunks, 0.0 s; vectors 20, 20, 0, 46 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 43.8 s of the rebuild's stage. The A9 stage's high-water mark 65,572,864 B. Digests: record `2eccf4640945`, lexical `0b2b27661884`, vectors `8e9408cd000d`, code graph 26,353 bytes (reported, not compared).
- **scale:** lexical 5.5 ms, semantic 1.4 ms (the stand-in's route), retrieve 14.9 ms; the vector scan 1.4 ms against the budget 2,000 ms; no `SCALE-PROPOSAL.md`.
- **measure** (10 questions): right end to end 80.0 %, wrong claims 2, hit@5 80.0 %; 3 residuals named with their cause (2 forbidden path in the first five, 1 the standing reader residual).

### TypeScript monorepo (typescript-monorepo)

- **commit:** built at `36b5401b6ae5`; assessed at `37f9e4036cba` (after A2); A9's record committed at `13868f450ae3`.
- **size:** 25 files, 9,652 bytes, 13 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take; the estimate: 27 s to index, 74,495,760 B estimated peak RSS, 1,730,744 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,609,344 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 23, 23, 0 (reasons: none), 48 chunks, 0.0 s; vectors 23, 23, 0, 48 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 52.0 s of the rebuild's stage. The A9 stage's high-water mark 65,966,080 B. Digests: record `0c7e5cebe5ec`, lexical `efbdcf7a4596`, vectors `487da05a8265`, code graph 27,269 bytes (reported, not compared).
- **scale:** lexical 10.0 ms, semantic 3.2 ms (the stand-in's route), retrieve 26.3 ms; the vector scan 3.2 ms against the budget 2,000 ms; no `SCALE-PROPOSAL.md`.
- **measure** (10 questions): right end to end 60.0 %, wrong claims 3, hit@5 60.0 %; 5 residuals named with their cause (3 forbidden path in the first five, 1 no gold path among the first five items, 1 the standing reader residual).

### Legacy documents with large files (legacy-docs)

- **commit:** built at `55ceb419d9aa`; assessed at `0527ab774fe0` (after A2); A9's record committed at `ea6dae6ebc40`.
- **size:** 19 files, 100,671,458 bytes, 10 commits.
- **assessment:** 2 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take; the estimate: 18 s to index, 61,373,940 B estimated peak RSS, 201,770,776 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 41,230,336 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 17, 15, 2 (reasons: binary), 94,192 chunks, 2.0 s; vectors 15, 15, 0, 94,192 vectors (stand-in), 0.3 s; code graph not asked for (the sandbox cannot run the tool), 61.8 s of the rebuild's stage. The A9 stage's high-water mark 1,083,609,088 B. Digests: record `ed42d9e0d5d6`, lexical `bd70b805563b`, vectors `5e90a77fb297`, code graph 100,688,792 bytes (reported, not compared).
- **scale:** lexical 269.2 ms, semantic 1.7 ms (the stand-in's route), retrieve 6356.3 ms; the vector scan 1.7 ms against the budget 2,000 ms; no `SCALE-PROPOSAL.md`.
- **measure** (10 questions): right end to end 80.0 %, wrong claims 2, hit@5 60.0 %; 5 residuals named with their cause (2 forbidden path in the first five, 2 no gold path among the first five items, 1 the standing reader residual).

### A secret in history (secret-history)

- **commit:** built at `00c9d7c90d27`; assessed at `b743f424ac43` (after A2); A9's record committed at `37f161bc9c6b`.
- **size:** 17 files, 7,680 bytes, 10 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take; the estimate: 18 s to index, 67,934,850 B estimated peak RSS, 1,085,010 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,523,328 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 15, 15, 0 (reasons: none), 36 chunks, 0.0 s; vectors 15, 15, 0, 36 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 30.2 s of the rebuild's stage. The A9 stage's high-water mark 63,721,472 B. Digests: record `8fc292138743`, lexical `6acdb02d062f`, vectors `d9517b31cc17`, code graph 24,827 bytes (reported, not compared).
- **scale:** lexical 4.8 ms, semantic 1.2 ms (the stand-in's route), retrieve 10.9 ms; the vector scan 1.2 ms against the budget 2,000 ms; no `SCALE-PROPOSAL.md`.
- **measure** (10 questions): right end to end 100.0 %, wrong claims 0, hit@5 100.0 %; 1 residuals named with their cause (1 the standing reader residual).

**Set checks of these questions** (W2-81's visible sets, resolved by W2-81's builders against each built `HEAD`; counts
by `set-checks`): path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS (a source's `holds` line stands for the heading; the quota is W2-81's own, at least 10 questions with gold sources in each repository: python-app 11, rust-workspace 10, typescript-monorepo 10, legacy-docs 10, secret-history 10; it is not the R5 quota of S12's set).

## Proof (d): EXAMIN's copy is W2-27's live trial

This ticket's proof record holds **no adoption run on EXAMIN's copy**: no stage of `gov adopt` was run by this ticket
against `~/gov-os-workbench/examin/`, and nothing there was read or touched. **W2-27** runs these tools (MA, the plan,
A3's `--assessment`, A9 lite) on its clone at adoption, on W2-16's release; that run, and the practice's first full run
(S12 to S14), are W2-27's, with no separate proof repository (DEC-1099 (2)).

## KPI lines: where each is built, and its state in the sandbox

| KPI line | built in | state |
|---|---|---|
| success 1 (the assessment) | `adopt/assess.py` `assess`; `stages.ma` | built; its own unit tests; proof (a) |
| success 2 (the plan) | `adopt/refactor_plan.py` `plan` | built; its own unit tests |
| success 3 (A9: stores, lists, coverage, never two at once) | `adopt/fabric.py` `a9`, `_stores`, `check_coverage`; `stages.a9` | built; stand-ins for the embedder and the code graph |
| success 4 (the layout, four digests) | `store/layout.py`; `store/loader.py`; `rebuild/command.py` `digests_of` | built; its own unit tests |
| success 5 (scale) | `fabric.scale`, `over`, `proposal` | built; the vector scan is the stand-in's here |
| success 6 (memory works, measured) | `fabric.load_questions`, `measure`; `--questions` | built; evidence side only, no reader model |
| success 7, 8, 9 (the proofs) | this file | (a) and (d) written; the real-embedder re-run is the lead's |
| success 10 (stale layout refused) | `store/layout.py` `check`; `loader.connect`; `rebuild/command.py` `_replace_stale` | built |
| success S10 (the standard) | `fabric.read_standard`, `departures`, `settings_of` | built; only the pool has a key `gov.config.loader` accepts (package) |
| success S11 (the refresh) | the refresh command is written in the record and the ACT (`memory_sets.walls_act`); never installed by the tool | built |
| success S12 to S14, S16, S17 | not this ticket's code (the sets are the writer's and checker's; S17 is W2-88a's); S15's copy has no stage today (package P-6) | not built here |
| success S18 to S23 | `adopt/memory_sets.py` | built; its own unit tests |
| failure 1 to 9 | the same modules; nothing is written in the repository by MA and the plan; no `tk` call | built; see the tests |
