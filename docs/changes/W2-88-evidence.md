# W2-88 (DAEO-2bdu) evidence: Memory for any repository

The implementer's evidence (DEC-996 (3) A; DEC-1150 (1)). Counts, ids, digests and figures only: nothing of a
repository's content, no secret value. Proofs (b) and (c) are W2-88b's; the Contract CIT-P is W2-88a's.

## Seams (P-1, P-4, P-6, P-10; the three values; run 4's decided items are item 8)

Batch 1 of run 3, committed alone for the test designer's narrow revision. After this commit a seam's name or form
changes only with a later commit's subject saying so, and the return naming it. Items 1 to 7 are as run 3 left them,
**except where item 8 says otherwise** (run 4: review round 1's findings and P-W2-88-B-1; items 4, 5 and the no-route
sentence of item 6 are superseded there).

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
- **Over the budget** is `vector_scan_ms > budget_ms` (only a vector scan that ran: item 8, RV1-2); **over the envelope** is nodes above 80,000, edges above
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

### 4. P-10: the `retrieval.yaml` key of each `fabric.STANDARD` setting (superseded by item 8: only the pool has a key)

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

### 5. P-6: the stage that copies the kernel's retrieval skill and T-0 (run 3's finding; built in run 4, item 8)

**None, at run 3.** No stage of `gov adopt --lite` copies a kernel skill or T-0 into the adopted repository:

- `stages.py:497` `STAGE` holds `A0` to `A8` and `A10`. `A0` writes `.gitleaks.toml` and the `.gov-runtime/` ignore
  line only (`safety.py:41` `setup`); `A1` to `A6` read and move; `A8` imports legacy rule files and leaves the
  adapter generation "not run by this stage" (`legacy.py:238`; the step that follows is `rulesync generate ... skills`,
  `legacy.py:28`), which writes `.claude/skills/` from `.rulesync/` and copies nothing from the kernel by itself.
- T-0 is filled by `gov brief` (`src/gov/brief/command.py:3`) from `template/governance/kernel/templates/brief.md`;
  it is not copied at adoption.

So S15's copy had no existing stage. The lead returned the case as package P-W2-88-B-1, which decided it (B-1.1 (a),
B-1.3 (a)): the copy step is `fabric.install` at A9 (item 8). A0 (`safety.py`) is not touched.

### 6. The three values

| value | figure | where it comes from |
|---|---|---|
| `assess.FILE_LIMIT_BYTES` | **1,048,576 B (1 MiB), the proposal stands: no byte limit is stated in the code.** | The chunker bounds a line, not a file: `chunking.py:29` `READ_CHARS = 32768`; the embedder cuts a chunk at `semantic.py:88` `EMBED_LIMIT_CHARS = 10_000`; `secrets/__init__.py:60` `_LARGE = 64 << 20` only throttles the scan's memory. The rebuild code (`rebuild/command.py`) holds no size limit. "Over the chunker's limit" is therefore: a file over `FILE_LIMIT_BYTES` **or** with a line over `READ_CHARS` (32,768). |
| the code graph's languages | **`assess.CODE_GRAPH_SUFFIXES`, the engineer's list, unconfirmed.** | `gov.codeintel` states none: `codeintel/__init__.py:37` names the tool (`codebase-memory-mcp`, 0.11.0 here) and `index` (`codeintel/__init__.py:293`) copies what `gov.secrets.indexable` returns; the tool decides which language it reads, and `codebase-memory-mcp --help` lists none. The list: `.py .pyi .js .jsx .mjs .cjs .ts .tsx .rs .go .java .kt .c .h .cc .cpp .hpp .cs .rb .php .swift .scala .sh .lua`. The no-route rule is stated once, in `assess.py`'s module text, and in item 8 (RV1-8). The lead or the CTO confirms the list against the tool on the machine that has it. |
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

### 8. Run 4: review round 1's findings and package P-W2-88-B-1 (the seams as built)

Every path:line is of this branch after run 4's first commit.

- **B-1.1 and B-1.3, the copy step** (`fabric.install`, `fabric._sources`, `fabric.undo`; called by `fabric.a9`).
  A9 first judges the standard (a refusal there writes nothing), then writes, byte for byte, into the adopted
  repository, stages them (`git add`) and lets the stage's one record commit take them:
  - every file of Gov OS's `template/governance/kernel/skills/retrieval/` and `.../discovery/` to
    `.claude/skills/retrieval/` and `.claude/skills/discovery/` (same relative names);
  - T-0 `template/governance/kernel/templates/brief.md` and T-8 `.../role-cto.md` to
    `governance/kernel/templates/brief.md` and `governance/kernel/templates/role-cto.md`;
  - Gov OS's `governance/project/retrieval.yaml` to `governance/project/retrieval.yaml` **only where the repository
    tracks none**; a tracked one is kept as it is and judged (B-1.4).
  - The files are in place before the build and the scale and measure queries, and join the stage's judged files (the
    stores' lists name them). On any refusal or interrupt after the copies, `fabric.undo` takes back only what A9 did,
    never a reset or a checkout (run 5, RV2-1; run 6, NC-1 and NC-2, the owner's P1-W2-88-NC-1 (a)): it unstages a copy
    only while its index entry is still the blob A9 staged (hashed before A9's `git add`), deletes a copy only while
    its bytes are still A9's (a replaced tracked file gets its start-commit content back), then the folders A9 made
    when empty; an edit, a staged file or a commit made during the run stays, and where HEAD moved the refusal is
    `HEAD_MOVED`. A9 commits its copies and its record through its own step (`fabric.commit`, not W2-23's
    `project.commit`): a refused record commit (a hook, signing) is `ADOPT_GIT_FAILED` with `exit_code`, and the record
    is undone with the copies. An untracked file at a destination or at the record's path is never overwritten
    (`ADOPT_WOULD_OVERWRITE`).
  - The record, and the stage's result, hold `installed: [{path, sha256, from}]` (`path` relative to the adopted
    repository, `from` relative to Gov OS) and `kept: [{path, sha256}]` (the repository's own `retrieval.yaml`; `[]`
    when none).
  - The standard is judged on the `retrieval.yaml` in force: the tracked one, else the installed copy
    (`read_standard`). A fresh adoption with none and no `--decision` is ok.
- **B-1.2, the reranker and the bundle are the pin's constants** (`fabric.settings_of`, `_code_settings`,
  `check_keys`). `reranker` is the last `/` part of `gov.retrieval.rerank.MODEL`; `bundle_tokens` is
  `gov.retrieval.retrieve.BUNDLE_BUDGET`; `reranker_service` is `shared` when `(rerank.CACHE_REL, rerank.SOCKET)` is
  `(".cache/gov-os", "rerank.sock")`, else `"<CACHE_REL>/<SOCKET>"` (a second reranker); `widen` is `sections`. A
  `retrieval.yaml` in force with a top-level `rerank` or `bundle` key is refused `CONFIG_INVALID` naming the key
  (`details["keys"]`) before any store is built; a `--decision` does not make it ok. On the CLI path
  `gov.config.loader` refuses it first with its own `CONFIG_INVALID` (either is the decided behaviour). Item 4's table
  is superseded: only the pool has a key.
- **B-1.4, the pool** (RV1-1; `fabric.departures`). The standard's pool is the whole `pool:` block as Gov OS ships it
  (`fabric.STANDARD["pool"]`). A block that differs in any key (a value, a missing or an added key), or none, is a
  departure `{setting: "pool", value: <the file's block, or false when there is none or meaning_uncut is not true>}`:
  A9 is `STANDARD_DEPARTURE` without a `--decision` naming it.
- **B-1.5, the secrets scan not run** (RV1-3; `assess._rules`, `refactor_plan.unscanned`, `stages.ma`). With no
  `gitleaks` on `PATH`, rules that cannot be read, or blobs over `assess.SCAN_LIMIT_BYTES` (16 MiB), MA still writes
  `memory-assessment.json` (now with `secrets_unscanned_reason`) and the proposals found; it writes no
  `NOTHING-TO-REFACTOR.md`; `refactor-plan/PLAN.md` holds `secrets: not scanned (<reason>)` and `Unscanned paths:` (the
  paths, or `all <n> tracked files` where the scanner did not run); the result is not ok: `SECRETS_UNSCANNED`, `details`
  `{reason, unscanned, unscanned_count, proposals, kinds, assessment}` (at most 1,000 paths in `unscanned`; the whole
  list of tracked paths is the assessment's `paths`). The repository is byte-identical before and after.
- **RV1-2, a vector scan that did not run** (`fabric.vector_scan`, `fabric._scan`, `fabric.scale`). The scan is taken
  through `fabric.vector_scan(root, question) -> dict` (the semantic route's reply; the seam a test replaces, as
  `fabric.search`). `scale.vector_scan_ms` is a figure only where the reply has `available: true`; an unavailable reply or
  an error gives `vector_scan_ms: null` and `scale.vector_scan_reason` (the reply's `reason`, or the error's name; `null`
  when measured). A null scan is never compared with the budget and writes no proposal. `scale.routes.semantic` stays the
  time of the route's reply (a route time, recorded and never compared); only the vector scan is compared with the
  budget, and DEC-078's envelope figures still write the proposal when over.
- **RV1-4, binaries the store holds** (`fabric._stores`). A tracked binary the lexical index chunked is in
  `stores.lexical.indexed` (and `stores.vectors.indexed` when it has vectors) and named in that store's
  `binary_held: [paths]`; `refused` never holds a file the store holds. The reason `binary` stays for a binary the store
  did not take.
- **RV1-5, the code graph** (`fabric._stores`, `fabric.check_coverage`). With the code graph called for, a file whose
  suffix is not in `assess.CODE_GRAPH_SUFFIXES` is refused `unsupported-language` and never counted as indexed by it,
  whatever the tool staged. A graph that cannot be read makes `stores.codegraph` `{built: false, error: "<reason>"}` and
  A9 `FABRIC_INCOMPLETE` with `codegraph` in `details["not_built"]` and the error in the message (never nodes 0 and
  edges 0 with ok). The graph's own suffix list stays the engineer's, unconfirmed (item 6).
- **RV1-6, a load never makes a stale store current** (`store/loader.py` `_current_or_new`, `_load`). `loader.load`
  stamps a store only when `layout.found_of` finds it current, or the store is new; `loader.connect` after a load into a
  stale store still raises `STORE_LAYOUT_STALE` with the same `details["found"]`. (`gov rebuild` replaces a stale store
  before it loads, so a rebuilt store is new and is stamped.)
- **RV1-8, the no-route rule** (`assess.py`'s module text, `OTHER_CODE_SUFFIXES`). Stated once: a file is no route
  when it is over the chunker's limit (`over-limit`) or when its suffix is in `assess.OTHER_CODE_SUFFIXES`, a code
  language the graph does not read (`unsupported-language`; the list holds at least `.vue .ps1 .proto .svelte .cob`, and
  `.psm1 .graphql .gql .tf .hcl .sol .bat .cmd .coffee .fs .fsx` besides the older ones). A file of any other suffix is
  no code and is not `no_route` for that reason. This replaces item 6's former sentence, which described a rule the
  code did not apply. (L-1a below refines "over the chunker's limit" for a binary.)
- **L-1, what the stores will take: a binary over the limit, and the chunks of the estimate** (the lead's finding from
  proof (a) with the real embedder, DEC-1052; `assess.py`: `FILE_LIMIT_BYTES`, `CHUNK_STEP`, `EMBED_S_PER_CHUNK`,
  `assess`). On W2-81's legacy documents (two tracked binaries of 48 MiB) the first assessment listed the binaries only
  under `binary`, left them out of `no_route` and out of the time estimate (17 s), and the plan wrote
  `NOTHING-TO-REFACTOR.md`; but the keyword index chunks a binary's bytes as text (94,222 chunks), A9 lists them indexed
  (`binary_held`, RV1-4) and the real embedder had not finished those chunks after 3,720 s. (a) **The rule (L-1a):** a
  tracked file that is not a link and is larger than `FILE_LIMIT_BYTES` (1,048,576) is in `no_route` as
  `{path, reason: "over-limit"}`, text or binary; a binary over the limit is listed in `binary` and in `no_route`, and
  the plan proposes its `over-limit` ticket for it exactly as for a text file (so a repository whose only finding is such
  a binary gets no `NOTHING-TO-REFACTOR.md`). A binary at or under the limit stays only in `binary`, no proposal. A text
  file with a line over `LINE_LIMIT` stays `over-limit`. (b) **The estimate (L-1b):** `estimate.chunks` is the sum over
  the tracked files (links excluded) of `ceil(size / CHUNK_STEP)`, with `CHUNK_STEP` =
  `chunking.MAX_CHARS - chunking.OVERLAP_CHARS` = 1,080 characters a chunk, binaries included; `estimate.index_seconds` =
  `round(estimate.chunks * EMBED_S_PER_CHUNK + code_files * GRAPH_S_PER_FILE)`. **`EMBED_S_PER_CHUNK = 0.04` s**, a
  **lower bound**: its source is the lead's proof run of 2026-11-13 (legacy documents' 94,222 chunks had not finished
  after 3,720 s with the real embedder), and it is consistent with the ticket's 2,521 files in 7 to 45 minutes.
  `EMBED_S_PER_FILE` (1.07 s a file) is removed: the estimate no longer counts files. `estimate.disk_bytes`
  and the peak-RSS estimate are unchanged. Unit tests: `tests/unit/adopt/test_w2_88_l1.py`.
- **Accepted seams, unchanged:** `fabric.RETRIEVE_BUDGET_MS = 2000` (provisional, for the owner's reading) with
  `--budget-ms <N>`; A9's question set only by `--questions <file>`. **The sixth refused reason `not-indexed` is not in
  the code:** run 3's batch 2c added it and batch 3b withdrew it (`77299906`), so the refused reasons are the
  Interface's five and `not-embedded` names a file a namespace keeps out of the keyword index. Run 4 does not re-add it
  (the brief calls it unchanged); the lead says if it is wanted.

## Proof (a): W2-81's five synthetic repositories, adopted to A9 lite with a stand-in embedder

Built by W2-81's builders (`tests/acceptance/W2-81/w2_81_build.py`, read and run, never edited) under
`~/gov-os-runs/W2-88/proving-ground/` (the exact path: `/home/usain/gov-os-runs/W2-88/proving-ground/`, outside this
repository; `git status` of this repository shows none of it). Seed: W2-81's default; the large files of the legacy
documents at the real run's size (48 MiB each). Each repository: a path map (one namespace, `embedding_policy:
embedded`, `memory_class: governance`) committed (**no hand copy of `retrieval.yaml` any more**: A9's copy step installs
Gov OS's as shipped, B-1.3, and the standard is judged on that copy), then A0, A1, A2, MA, A3
(`--assessment`; the proposal holds no action: every artefact kept), A4, A5 (the verdict commit is the proof's stand-in
for the independent auditor: `Role: independent-auditor`), A6, A8 and A9 (`--questions` from W2-81's visible set,
resolved by `w2_81_questions.resolve`). One process per repository: its peak is its own.

**What stands in, said once.** (1) The embedder: no model runs in the sandbox (DEC-1064, DEC-1065), so the vectors are
a hash of each chunk, written as the real stage writes them; there is no embedder manifest, so the semantic route
answers unavailable (`available: false`) and **no vector scan was measured on any of the five repositories**: each
section's `vector_scan_ms` is null with the route's reason, and the budget was compared with no scan (RV1-7; the figure
the first run of this proof gave as a scan time was an unavailable route's reply and was never a scan). Retrieval is
the keyword and code routes; the measure below is therefore not a measure of the standard. (2) The code graph: `codebase-memory-mcp index_repository` exits 1 in this sandbox, so the path map's
`code_intelligence` is off here: the code graph is "not asked for" (`requested: false`), nodes and edges 0. (3) The
rebuild lock: `/tmp` is read-only here, so `GOV_REBUILD_LOCK` names a file in the sandbox's own temp folder; it is the
same lock, one rebuild at a time. (4) The reader: no reader model runs in A9; `right_e2e` is the evidence side (every
gold path stacked, no forbidden path in the first five). The lead re-runs the proof outside the sandbox with the real
embedder, the code graph and the reranker. The figures are data and set no bar (DEC-954 Q9e).

**The largest proof repository** is the legacy documents (18 files, 100,670,630 bytes).
Its assessment's **peak RSS** is 41,353,216 bytes, against the resource gate's
**per-session figure** of 805,306,368 bytes (`working_size_bytes`, read from
`gov.resources.config` by the assessment itself): under it. The A9 stage's own high-water mark on that repository is
1,068,199,936 bytes: it is the rebuild's, which the gate bounds by `rebuild_peak_bytes`
(7,582,199,808 B on this machine), not by the session figure.

**L-1 on that repository.** Its 2 tracked binaries are over the chunker's limit
(`FILE_LIMIT_BYTES`): the assessment lists them under `binary` and under no route (2 files,
reasons: over-limit), the plan holds 1 proposal(s)
(over-limit), and the estimate counts 93,228 chunks
(`estimate.chunks`) for 3,729 s at `EMBED_S_PER_CHUNK` = 0.04 s; A9's
keyword index made 94,222 chunks (the stand-in run: the estimate counts the file's bytes
at 1,080 a chunk, the chunker's own count may differ a little).

A section's figures are the stand-in's. The section the lead adds for the real embedder follows this one.

### Python with drifted specs (python-app)

- **commit:** built at `7b8383e5fd74`; assessed at `656c8cc5da84` (after A2); A9's record committed at `90f71419c0c2`.
- **size:** 22 files, 8,443 bytes, 12 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take (none); the estimate: 25 chunks, 2 s to index, 76,682,730 B estimated peak RSS, 1,942,256 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,609,344 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 33, 33, 0 (reasons: none), 83 chunks, 2.4 s; vectors 32, 32, 0, 83 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 38.2 s of the rebuild's stage. The A9 stage's high-water mark 65,810,432 B. Digests: record `29a40b2e9dbe`, lexical `29cffd473a97`, vectors `45829613b4f9`, code graph 41,433 bytes (reported, not compared).
- **scale:** lexical 1.7 ms, semantic route's reply 4.4 ms (recorded as a route time only: an unavailable answer, no scan ran), retrieve 13.1 ms; **no vector scan was measured** (`vector_scan_ms` null; reason: missing): the budget of 2,000 ms was compared with no scan, so this run says nothing of whether a scan is under it; no `SCALE-PROPOSAL.md`.
- **installed by A9's copy step:** 5 files (the retrieval and discovery skills, T-0, T-8, and Gov OS's `retrieval.yaml`), kept: 0 (the repository's own `retrieval.yaml`); the standard's departures: 0.
- **measure** (11 questions): right end to end 54.5 %, wrong claims 4, hit@5 54.5 %; 6 residuals named with their cause (4 forbidden path in the first five, 1 no gold path among the first five items, 1 the standing reader residual).

### Rust workspace (rust-workspace)

- **commit:** built at `31e1f447d2ef`; assessed at `561bc3c84447` (after A2); A9's record committed at `caf4bc2f3392`.
- **size:** 21 files, 8,101 bytes, 11 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take (none); the estimate: 25 chunks, 1 s to index, 67,934,850 B estimated peak RSS, 1,085,852 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,703,552 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 32, 32, 0 (reasons: none), 76 chunks, 2.4 s; vectors 32, 32, 0, 76 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 39.2 s of the rebuild's stage. The A9 stage's high-water mark 64,303,104 B. Digests: record `3579f735e3a3`, lexical `c6b5d1550474`, vectors `ddaf36d7d0d3`, code graph 41,044 bytes (reported, not compared).
- **scale:** lexical 1.8 ms, semantic route's reply 5.9 ms (recorded as a route time only: an unavailable answer, no scan ran), retrieve 19.7 ms; **no vector scan was measured** (`vector_scan_ms` null; reason: missing): the budget of 2,000 ms was compared with no scan, so this run says nothing of whether a scan is under it; no `SCALE-PROPOSAL.md`.
- **installed by A9's copy step:** 5 files (the retrieval and discovery skills, T-0, T-8, and Gov OS's `retrieval.yaml`), kept: 0 (the repository's own `retrieval.yaml`); the standard's departures: 0.
- **measure** (10 questions): right end to end 80.0 %, wrong claims 2, hit@5 80.0 %; 3 residuals named with their cause (2 forbidden path in the first five, 1 the standing reader residual).

### TypeScript monorepo (typescript-monorepo)

- **commit:** built at `899f899f89e8`; assessed at `1f13e079b04d` (after A2); A9's record committed at `5b990e3a931d`.
- **size:** 24 files, 8,824 bytes, 13 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take (none); the estimate: 28 chunks, 2 s to index, 74,495,760 B estimated peak RSS, 1,729,088 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,609,344 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 35, 35, 0 (reasons: none), 78 chunks, 2.4 s; vectors 35, 35, 0, 78 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 39.9 s of the rebuild's stage. The A9 stage's high-water mark 63,746,048 B. Digests: record `58cba11afcb1`, lexical `47f80e412f76`, vectors `92d0b37bd22e`, code graph 41,960 bytes (reported, not compared).
- **scale:** lexical 1.5 ms, semantic route's reply 4.4 ms (recorded as a route time only: an unavailable answer, no scan ran), retrieve 12.5 ms; **no vector scan was measured** (`vector_scan_ms` null; reason: missing): the budget of 2,000 ms was compared with no scan, so this run says nothing of whether a scan is under it; no `SCALE-PROPOSAL.md`.
- **installed by A9's copy step:** 5 files (the retrieval and discovery skills, T-0, T-8, and Gov OS's `retrieval.yaml`), kept: 0 (the repository's own `retrieval.yaml`); the standard's departures: 0.
- **measure** (10 questions): right end to end 60.0 %, wrong claims 3, hit@5 50.0 %; 6 residuals named with their cause (3 forbidden path in the first five, 2 no gold path among the first five items, 1 the standing reader residual).

### Legacy documents with large files (legacy-docs)

- **commit:** built at `1bfca6544fb7`; assessed at `6abae9d9d796` (after A2); A9's record committed at `06c49ac59ccd`.
- **size:** 18 files, 100,670,630 bytes, 10 commits.
- **assessment:** 2 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 2 files no route can take (over-limit); the estimate: 93,228 chunks, 3,729 s to index, 61,373,940 B estimated peak RSS, 201,769,120 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 41,353,216 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 1; over-limit.
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 29, 29, 0 (reasons: none), 94,222 chunks, 4.0 s; vectors 29, 29, 0, 94,222 vectors (stand-in), 0.2 s; code graph not asked for (the sandbox cannot run the tool), 57.2 s of the rebuild's stage. The A9 stage's high-water mark 1,068,199,936 B. Digests: record `511c3cba242e`, lexical `3376b6fb0944`, vectors `65cc48ff9345`, code graph 100,703,483 bytes (reported, not compared).
- **scale:** lexical 76.9 ms, semantic route's reply 162.3 ms (recorded as a route time only: an unavailable answer, no scan ran), retrieve 5339.5 ms; **no vector scan was measured** (`vector_scan_ms` null; reason: missing): the budget of 2,000 ms was compared with no scan, so this run says nothing of whether a scan is under it; no `SCALE-PROPOSAL.md`.
- **installed by A9's copy step:** 5 files (the retrieval and discovery skills, T-0, T-8, and Gov OS's `retrieval.yaml`), kept: 0 (the repository's own `retrieval.yaml`); the standard's departures: 0.
- **measure** (10 questions): right end to end 80.0 %, wrong claims 2, hit@5 60.0 %; 5 residuals named with their cause (2 forbidden path in the first five, 2 no gold path among the first five items, 1 the standing reader residual).

### A secret in history (secret-history)

- **commit:** built at `75b0074e0b75`; assessed at `0b4fc61b67d1` (after A2); A9's record committed at `a625cb7ada97`.
- **size:** 16 files, 6,852 bytes, 10 commits.
- **assessment:** 0 binary, 0 generated, 0 minified, 0 vendored, 0 secrets by rule id (none), 0 files no route can take (none); the estimate: 19 chunks, 1 s to index, 67,934,850 B estimated peak RSS, 1,083,354 B disk, inside DEC-078's envelope: True; **the assessment's own peak RSS 23,592,960 B** (alone in its own process), per-session figure 805,306,368 B, under it: True.
- **plan's proposals (count and kinds):** 0; none (`NOTHING-TO-REFACTOR.md`).
- **per-store figures** (judged, indexed, refused with reason, chunks, vectors, nodes, edges, seconds; each store's memory field in the record holds the A9 stage's own high-water mark, one rebuild, not one per store): record 1, 1, 0, nodes 9, edges 0, 0.0 s; lexical 27, 27, 0 (reasons: none), 66 chunks, 2.4 s; vectors 27, 27, 0, 66 vectors (stand-in), 0.0 s; code graph not asked for (the sandbox cannot run the tool), 32.3 s of the rebuild's stage. The A9 stage's high-water mark 65,089,536 B. Digests: record `899f2be301ed`, lexical `4a244cc99d20`, vectors `50d2b37129a4`, code graph 39,518 bytes (reported, not compared).
- **scale:** lexical 1.5 ms, semantic route's reply 4.4 ms (recorded as a route time only: an unavailable answer, no scan ran), retrieve 12.7 ms; **no vector scan was measured** (`vector_scan_ms` null; reason: missing): the budget of 2,000 ms was compared with no scan, so this run says nothing of whether a scan is under it; no `SCALE-PROPOSAL.md`.
- **installed by A9's copy step:** 5 files (the retrieval and discovery skills, T-0, T-8, and Gov OS's `retrieval.yaml`), kept: 0 (the repository's own `retrieval.yaml`); the standard's departures: 0.
- **measure** (10 questions): right end to end 100.0 %, wrong claims 0, hit@5 90.0 %; 2 residuals named with their cause (1 no gold path among the first five items, 1 the standing reader residual).

**Set checks of these questions** (W2-81's visible sets, resolved by W2-81's builders against each built `HEAD`; counts
by `set-checks`): path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS (a source's `holds` line stands for the heading; the quota is W2-81's own, at least 10 questions with gold sources in each repository: python-app 11, rust-workspace 10, typescript-monorepo 10, legacy-docs 10, secret-history 10; it is not the R5 quota of S12's set).

## Proof (a) with the real embedder (the lead's run outside the sandbox)

The same five repositories, built again by W2-81's builders under `~/gov-os-runs/W2-88/proving-ground-real/` (outside
this repository), taken through the same chain to A9 lite with **no stand-in**: the real embedder
(`qwen3-embedding:0.6b`, revision `ac6da0dfba84`), the machine's one shared reranker (`Qwen3-Reranker-0.6B`), the code
graph on (`code_intelligence` enabled) and A9's copy of Gov OS's `retrieval.yaml` (sha256 `53970c0c0a05`). Script
`~/gov-os-runs/W2-88/proof_a_real.py`; figures in `~/gov-os-runs/W2-88/proof-a-real-results.json` and
`proving-ground-real/<repository>-result.json`. Run on 2026-11-13 from 07:59 UTC on head `14c7ec15c8d8`; the only
source change since then is L-1 (`b3f4e768f`, `src/gov/adopt/assess.py`: the assessment's no-route list and estimate),
so every A9 figure below stands for the final code; the assessment's estimate column is the pre-L-1 one and the
stand-in section above gives L-1's. The standard on every repository: gov pin `pin-797495bdfc70`, the 6,000-token
bundle widened to sections, the pool on, departures 0. The figures are data and set no bar (DEC-954 Q9e).

| repository | built / A9 commit | size | A9 time | per store (indexed/judged; chunks, vectors, nodes, edges) and the stage's peak RSS | scale (budget 2,000 ms) | measure (right e2e, wrong claims, hit@5) |
|---|---|---|---|---|---|---|
| python-app | `25caecc3c504` / `079086cacea1` | 22 files, 8,442 B | 33.7 s | record 1/1; lexical 33/33, 83 chunks; vectors 32/32, 83 vectors; code graph 9/9, 56 nodes, 6 edges; 75,026,432 B | lexical 2.2 ms, **vector scan 415.3 ms** (the first query: the embedder's load), retrieve 1,844.5 ms; no proposal | 11 q: 63.6 %, 4, 54.5 % |
| rust-workspace | `70c95cdd69e0` / `73eba6cffb85` | 21 files, 8,100 B | 25.8 s | record 1/1; lexical 32/32, 76 chunks; vectors 32/32, 76 vectors; code graph 68 nodes, 4 edges; 75,022,336 B | lexical 1.6 ms, **vector scan 11.1 ms**, retrieve 541.7 ms; no proposal | 10 q: 70.0 %, 3, 60.0 % |
| typescript-monorepo | `d23a8c0501bb` / `456869adb07a` | 24 files, 8,823 B | 26.0 s | record 1/1; lexical 35/35, 78 chunks; vectors 35/35, 78 vectors; code graph 54 nodes, 1 edge; 74,932,224 B | lexical 1.7 ms, **vector scan 10.1 ms**, retrieve 701.3 ms; no proposal | 10 q: 70.0 %, 3, 60.0 % |
| legacy-docs | not finished | 18 files, 100,670,630 B | stopped at 3,720 s | A9 still embedding the two binaries' 94,222 chunks when the run's one-hour limit ended it; no record, no figures | none measured | none |
| secret-history | `44b4fd5e36ae` / `4341bfede039` | 16 files, 6,851 B | 20.2 s | record 1/1; lexical 27/27, 66 chunks; vectors 27/27, 66 vectors; code graph 46 nodes, 5 edges; 75,091,968 B | lexical 1.5 ms, **vector scan 11.9 ms**, retrieve 768.1 ms; no proposal | 10 q: 100.0 %, 0, 100.0 % |

Refused files on every finished repository: 0 in every store. Digests (record, lexical, vectors; code graph bytes
reported, not compared): python-app `92d07043e83f`, `6c32697cf3ce`, `98b4307822dc`, 2,334,661 B; rust-workspace
`59e599eb9422`, `c0d96b586b59`, `06c925ef951a`, 2,334,272 B; typescript-monorepo `e0212b70210d`, `694e4b2e9b2f`,
`8c74d418a54f`, 2,335,188 B; secret-history `8a864e8c7a0e`, `8b0b74f2f33b`, `85eccb1333ca`, 2,332,800 B. Residuals
named with their cause: on each repository the reader (no reader model runs in A9; the reader's grade is W2-27's first
full run), and per question "forbidden path in the first five" (python-app 4, rust-workspace 3, typescript-monorepo 3)
or "no gold path among the first five items" (1 each on python-app, rust-workspace and typescript-monorepo).

**Legacy documents: the residual, and the finding it gave (L-1).** The run's A9 on legacy-docs did not end within the
one-hour limit of the lead's run: the keyword index chunks the two 48 MiB binaries' bytes as text (94,222 chunks, held
as `binary_held`, RV1-4) and the real embedder was still embedding them at 3,720 s. That run's assessment (pre-L-1)
listed them only under `binary`, estimated 17 s and the plan wrote `NOTHING-TO-REFACTOR.md`: it did not say what the
stores would take. L-1 (`b3f4e768f`) makes the assessment list a file over `FILE_LIMIT_BYTES` under no route
(`over-limit`) whether text or binary, the plan propose its `over-limit` ticket, and the estimate count chunks
(`estimate.chunks`, `EMBED_S_PER_CHUNK` = 0.04 s, a lower bound from this run): on legacy-docs it now gives 93,228
chunks and 3,729 s, and one `over-limit` proposal for the owner (the stand-in section above). Legacy-docs' real vector
scan and measure are therefore **not measured** here: a named residual whose cause is the two binaries, which the plan
now proposes to move out of the embedded namespace; the A9 code is unchanged by L-1, so a re-run would take the same
hour or more. The real repositories' proofs (b) and (c) are W2-88b's (DEC-1150 (1)).

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
| success 5 (scale) | `fabric.scale`, `vector_scan`, `over`, `proposal` | built; no vector scan in the sandbox (no query embedder): null with its reason; with the real embedder (the lead's run) measured on 4 of 5, 10.1 to 415.3 ms against 2,000 ms; legacy-docs not measured (named residual, L-1) |
| success 6 (memory works, measured) | `fabric.load_questions`, `measure`; `--questions` | built; evidence side only, no reader model |
| success 7, 8, 9 (the proofs) | this file | (a) and (d) written; the real-embedder re-run is the lead's |
| success 10 (stale layout refused) | `store/layout.py` `check`; `loader.connect`; `rebuild/command.py` `_replace_stale` | built |
| success S10 (the standard) | `fabric.read_standard`, `departures`, `settings_of`, `check_keys` | built; the pool is the whole shipped block; the reranker, its service and the bundle are the pin's constants, and a `retrieval.yaml` with `rerank:` or `bundle:` is `CONFIG_INVALID` |
| success S11 (the refresh) | the refresh command is written in the record and the ACT (`memory_sets.walls_act`); never installed by the tool | built |
| success S12 to S14, S17 | not this ticket's code (the sets are the writer's and checker's; S17 is W2-88a's) | not built here |
| success S15, S16 (the kernel copy) | `fabric.install`, `undo`; called by `fabric.a9` | built (B-1.1, B-1.3); its own unit tests |
| success S18 to S23 | `adopt/memory_sets.py` | built; its own unit tests |
| failure 1 to 9 | the same modules; nothing is written in the repository by MA and the plan; no `tk` call | built; see the tests |

## Run 7 (2026-11-14; the reopen under DEC-1164 (18) on DEC-1178 (3)(b) and (4)): S24 to S27

Where each is built, and the unit tests that show it (`tests/unit/adopt/test_w2_88_p1.py`, `_f1.py`, `_ignored.py`;
`tests/unit/secrets/test_w2_88_scan.py`). Each test file was run against the code before its item and failed there
(S26 and S24: 17 of 21 failed on `a23678e27`; S25: 4 of 6 failed on S24's commit; S27: 4 of 12 failed on `a23678e27`; the
cases that pass on the old code are the ones that state what must stay the same).

### S24 (P-1): A9 from an installed release

- **Built:** `fabric.shipped(rel, root)` and `fabric._source_tree()`. The source tree is the nearest ancestor of the running
  `gov` package that holds `copier.yml`, `template/` and `src/gov/` (no fixed number of levels); then, for a `rel` under
  `template/`, the project's own copy that `copier copy` installed (`template/X` read as `<root>/X`); else
  `SHIPPED_FILE_MISSING` (`details`: `file`, `looked`), never a default. The search for the source tree is a place looked
  (run 7, fix 2): `looked` is never empty; it names first the tree's `<tree>/<rel>`, or, where none was found, the gov
  package's folder and that no folder at or above it holds `copier.yml`, `template/` and `src/gov/`; then, for a `rel`
  under `template/`, `<root>/X`; never `<root>/<rel>` for a `rel` outside `template/`. Every read of a shipped file goes through it, when
  it is needed: A9's kernel copies (`fabric._sources`, `install`), its copy of `retrieval.yaml` and the standard's `pool:`
  block (`fabric.standard_of`, read by `read_standard`; `fabric.STANDARD` is now a module attribute computed when read, and
  `departures` takes the standard as an argument), the walls template (`memory_sets.walls_act`, with the new `root`
  argument), the audit briefs (`fabric._stage`) and the `.gitleaks.toml` fallback (`safety.setup`, `assess._rules`;
  `safety.TEMPLATE_GITLEAKS` is computed when read). A9 also asks for the walls and the briefs before it copies anything, so
  a missing one refuses before the stores are built. `grep -n "parents\[3\]\|GOV_OS" src/gov/adopt/*.py` finds nothing.
- **The release form, shown in a unit test** (`test_a_wheel_in_the_release_form_runs_a9s_reads_with_no_source_tree`): an
  export of `src/` and `pyproject.toml` is built with `python3 -m pip wheel -q --no-deps --no-build-isolation --no-index`,
  installed with `--no-deps --no-index` into a fresh `--system-site-packages` venv, and run from a folder outside the tree
  with no `PYTHONPATH`: `gov.__file__` is in the venv, `_source_tree()` is None, importing `gov.adopt.fabric`,
  `memory_sets` and `safety` reads no shipped file and does not fail.
- **What an installed release now finds, and what it refuses (item 4 of the interface):** it finds the kit's files that
  `copier copy` installs from `template/`: the retrieval and discovery skill folders (`governance/kernel/skills/...`),
  `brief.md` and `role-cto.md` (`governance/kernel/templates/...`). It refuses `SHIPPED_FILE_MISSING` for the files that are
  neither in the wheel nor under `template/`: `governance/project/retrieval.yaml` (the pool: the first read, so A9 refuses
  at its start with nothing written), `governance/project/indep-walls` and
  `governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs`; and `template/.gitleaks.toml` for a project that has no
  `.gitleaks.toml` of its own (A0; MA's assessment then says "no secrets rules could be read"). So an installed release
  cannot yet run A9 end to end: the three are the package's (the lead's). **What it would take (outside these paths):** the
  wheel must carry them as package data of `gov` (`pyproject.toml`, `[tool.setuptools.package-data]`, or a `src/gov/...`
  folder that holds copies) and the resolver gets that folder as a place after (1) and (2). Moving them under `template/`
  is not enough and is wrong for the pool: `template/governance/project/` is the overlay copier installs once and never
  overwrites, so (2) would read the project's own, possibly tuned, `retrieval.yaml` as Gov OS's standard, and the
  departure check would compare the file with itself.

### S25 (F-1): redis's code graph

- **Built:** `fabric.refuse_too_large(root)`, called when `_stores` cannot read the graph, and `fabric.graph_counts(root)`
  (two count queries of one row, in the same session class `gov.codeintel._graph` uses). Where either count is over
  `fabric.GRAPH_CAP` (100,000), A9 refuses `CODEGRAPH_TOO_LARGE` (`details`: `nodes`, `edges`, `cap`, `tool`), the message
  naming `codebase-memory-mcp`, its cap, the counts and that `gov.codeintel`'s read takes the whole graph in one query;
  the copies are undone as for any refusal after them. Any other failure keeps `FABRIC_INCOMPLETE` naming `codegraph` and
  the error text; a failed read is never 0 nodes and edges.
- **Not built (outside the paths):** the cause. `gov.codeintel._graph` reads all edges in one query
  (`MATCH (a)-[r]->(b) RETURN ...`), which the tool refuses over 100,000 rows before its own `offset`/`max_rows` paging; the
  lead's probe measured 41,086 nodes and 143,008 edges on redis. **What it would take:** `_graph` reads each query in
  pages the tool accepts (the probe in `.gov-runtime/scratch/lead/f1_probe2.py` asks `SKIP`/`LIMIT` under the cap), a change
  of `src/gov/codeintel/__init__.py`; with it A9 on redis reads and checks the graph, and this refusal stays for a graph the
  paging cannot bring under the cap. The unit tests plant a stand-in `codebase-memory-mcp` first on `PATH` (MCP over stdio)
  that answers as the real tool does over its cap (`isError: true`, "result exceeded 100k rows"); the redis copy's A9
  re-run is the lead's, outside the sandbox.

### S26 (F-3): ignore rules found at the start

- **Built:** `safety.written_paths(root)` (the one list: A0's `.gitleaks.toml` and `.gitignore`, the roster and a ticket
  where `tk` is vendored, every stage's record, A2's packages, A8's CIT-E, and A9's copies, each file of the kernel folders
  and templates, and `retrieval.yaml`), `safety.ignored(root, paths)` (`git check-ignore -v -z --stdin`; a path the index
  tracks is not judged by git, a re-including rule `!` is no finding) and `safety.refuse_ignored(root)`, called first by
  stage MA (`stages.run`) and by A0 (`stages.a0`). A path ignored and untracked refuses `ADOPT_PATH_IGNORED` at once, the
  message naming each path with `source:line:pattern` as `git check-ignore -v` gives them (`details["ignored"]`: `path`,
  `source`, `line`, `pattern`); nothing is written, staged or committed, no ignore file is edited, `git add -f` is never run.
- **Not in the list:** what a stage writes later from the caller's proposal (A6's targets, A8's imports) is not known at the
  start. **A change of behaviour to know:** an untracked file already standing at an ignored path of the list used to be
  refused by the stage that writes it (`ADOPT_WOULD_OVERWRITE`); it is now refused at the start as ignored. The existing test
  `tests/unit/adopt/test_safety.py::test_s1_a_stage_writes_nothing_over_an_untracked_file` plants exactly that (a
  `.gitignore` of `governance/`) and expects the older code; it needs its expected code changed (outside these paths).

### Run 7: the secret scan's speed (S27)

- **Built:** `gov.secrets.indexable` reads each worker's group of files in batches (`_BATCH_BYTES` 1 MiB or `_BATCH_FILES` 256, a
  file of 1 MiB or more alone), gives each batch to **one gitleaks process per rule set** (`_scan_batch`: each file's
  chunks framed as `_scan` frames them, a blank line after every piece, each finding put back on its file by its line,
  which gitleaks counts over the whole input: confirmed with a planted secret in two of 60 files), and runs the batches in
  the one pool of `_workers()` (the CPU set within `GOV_HEAVY_THREAD_BUDGET`). A file the record holds clean is answered
  from it; a file no finding names is clean (counted `scanned`, kept in the record); a file a finding names, a finding that
  cannot be put back on a file, or a report that cannot be read sends the file (or the batch) to the one-per-file judgement
  as ever, so the commit-hash exemption and every other rule of `_holds_secret` stand. `indexable`, `path_holds_secret`,
  `pool_size` and `scan_counts` keep their signatures and meaning; `_holds_secret` is still the one verdict per file
  (the batch's result reaches it through a thread-local, set around that worker's own calls). No secret's value is
  printed or recorded; the planted secret in the tests and in the tree is built from parts.
- **Fix 3 (P1-1, the narrow check's blocker):** a bare generic key at one file's end (`password:`, `token =`) had its `\s`
  classes run over the blank line between two files in a batch and take the next file's first line as its value; the match
  was then dropped by the rule's own filter (stopwords or entropy, on a value such as `token=...`), so gitleaks reported
  nothing and the next file's own secret was shadowed: it was written to the reuse record as clean. Built:
  (1) every text of a batch ends with a line of one `#` and a blank line (`_FENCE`), which no rule's value class takes in,
  so no match runs from one file into the next (this is the cause fixed; a report cannot name a swallowed match that a
  filter dropped, so lines alone could not); (2) a finding is put back on **every** file its `StartLine` to `EndLine`
  covers, and on the file after the last of them, each then judged alone; (3) `_FORM` is 5, so every record the batched
  scan wrote under form 4 is ignored. Unit tests: the pair in both orders, 4 bare tails by 4 head forms, with a clean file
  before and after, in a batch of 16 with the pair in the middle; the rules without the fence (`_FENCE` empty) still give
  the one-per-file verdict through (2); a form-4 record is not reused.
- **The measure** (`indexable` over every file of a planted tree, same machine, same slot kind, gitleaks 8.30.1,
  `GOV_SECRETS_CACHE` empty so no clean result is reused; the tree: 5,000 files in 50 folders, 15.3 MB, 3,013 of 8 lines,
  1,732 of 60 lines, 255 of 400 lines, one file in fifty holding the planted test secret = 100; the machine has 20 CPUs
  and was shared with other slots; the slot's CPU set was 7 CPUs and its exported thread budget 1; the old code is `git
  archive a23678e27 src` on `PYTHONPATH`):

| form | thread budget (workers) | seconds | files per second | files left out |
|---|---|---|---|---|
| one gitleaks per file (`a23678e27`) | 1 | 2,808.4 | 1.8 | 100 |
| batched (this change) | 1 | 46.2 | 108.2 | 100 |
| one gitleaks per file (`a23678e27`) | 7 | 574.3 | 8.7 | 100 |
| batched (this change) | 7 | 40.6, 40.2 (two runs) | 123.3, 124.5 | 100 |

  **Re-measure after fix 3 (P1-1, 2026-11-14; same slot kind, a freshly generated tree of the same shape: 5,000 files in 50
  folders, 15.6 MB, 100 holding the planted secret; `GOV_SECRETS_CACHE` empty; the batched code of this change, now with
  the `#` fence and the owner's neighbours):** budget 1 (1 worker): **41.7 s, 119.8 files per second, 100 files left
  out**; budget raised to 7 (the CPU set gave 6 workers): **34.3 s, 145.8 files per second, 100 left out**. The old form
  (`a23678e27`) was not re-run over all 5,000 files (47 minutes at budget 1, over this run's hour): on every 20th file (250
  files, 5 holding the secret) at budget 1 it took 122.3 s, 2.0 files per second, 5 left out, so the whole tree at that rate
  is about 2,500 s. **Ratio now:** about 60 times at budget 1 (2,500 s extrapolated over 41.7 s; 67 times against the
  measured 2,808.4 s above) and 16.7 times at budget 7 (574.3 s measured above over 34.3 s). S27's line is at least 10
  times: met. The fix cost nothing visible (42 s here against 46 s above; the machine is shared, so the small difference
  is noise): a file a finding names was already judged alone, and now so is the file after it (two per finding).

  **Ratio (the first measure, before fix 3):** 60 times at the slot's own budget (1 worker), 14.3 times with the budget raised to the whole CPU set (7
  workers), both at least 10 times; the verdicts are the same (the same 100 files left out in every run, and the unit
  tests compare each file's verdict with the one-per-file form's). The old form's 1.8 files per second is grafana's A6
  rate (about 2 a second). **What the figures say about the rest:** a gitleaks process already uses every CPU it may, so
  more workers add little (108 to 124 files per second from 1 to 7): the scan now costs gitleaks' own time on the bytes
  (about 0.37 MB a second here with this rule file), not a process per file. EXAMIN's copy of 36,000 files, at the same
  shape (about 3 KB a file), is about 110 MB: roughly 5 minutes here, against about 5.5 hours one process per file.
  If a repository's files are many and large the time follows the bytes; a faster scan then needs gitleaks' own rule cost
  cut (the rule file), outside these paths. `gov.codeintel` still calls `path_holds_secret` once per allowed path (one
  gitleaks per path on a cold record, each answered from the record once clean); batching those calls would take a
  change of `src/gov/codeintel/__init__.py` and of `path_holds_secret`'s callers, outside these paths.

## Run 8 (2026-11-14; the owner's answer of 21:50, to be recorded as DEC-1183: `P-W2-88-S27-1 (b), package 1 (a), package 2 (a)`)

### S27: its next round (DEC-1183)

- **S27 is not delivered in this land.** The section "Run 7: the secret scan's speed (S27)" above records what was built
  and measured in run 7; that code is gone. `src/gov/secrets/__init__.py` is back to the one-file-at-a-time scan of
  `a23678e27` (each file's text read by gitleaks processes of its own, one per rule set; the same findings as before S27);
  `indexable`, `path_holds_secret`, `pool_size` and `scan_counts` keep their signatures and meaning. The batched path is
  removed entirely (`_scan_batch`, `_batched`, `_BATCH_BYTES`, `_BATCH_FILES`, `_BATCH_MIN`, `_FENCE`): no code path in
  `src/gov/secrets/` judges two files' texts in one gitleaks process. Nothing else in the file had changed since
  `a23678e27` (the diff `a23678e27..2491c9bec` of the file is batching only; the `.gitleaks.toml` fallback through
  `fabric.shipped` lives in `safety.py` and `assess.py`, not here).
- **The reuse record's form is 6** (`_FORM`), a value no earlier form used (4: `a23678e27` and `ef9c773c3`; 5: `d766514fd`,
  the batched scan), so no record any earlier form wrote, in the content cache or a store's record, is reused: a file the
  batched form judged clean wrongly (P1R-1: 0 scanned, 12 remembered on a second run) is scanned again.
- **Why the text-batch form was dropped:** run 7's narrow checks found it fails open twice. P1-1 (`PR-DAEO-2bdu-p1-check1.md`):
  a bare generic key at one text's end took the next text's first line over the blank line between them, the match was
  dropped by the rule's own filter, and the next file's secret was shadowed. The `#` fence of fix 3 closed that shape; P1R-1
  (`PR-DAEO-2bdu-p1.md`): two other default rules still cross it, `curl-auth-user` (a gap of up to five lines that takes in
  `#`) and `private-key` (a body class that takes in anything); a match dropped by a filter (the rule's allowlist or the
  global allowlist) swallowed the next file's own secret, which was judged clean, kept as indexable and recorded clean.
  A text batch read by one gitleaks process cannot be fenced against every rule a project's rule file may hold.
- **Evidence kept for the next round (no code for it here):** the run 7 figures above (one gitleaks per file: 1.8 files a
  second at budget 1, 8.7 at budget 7, on a planted 5,000-file tree; the text batches about 60 and 14 to 17 times that);
  and the lead's record of a folder form: `gitleaks dir` judges a folder in one process and reports one file per finding
  (its own file boundaries, so no match runs from one file into the next), and a scratch test judged 403 files in 0.34 s.
  A next round built on it would need the one-per-file form as its oracle for every default rule (P1-1's and P1R-1's
  shapes among them) and its own measure on the same tree.
- **Unit tests** (`tests/unit/secrets/test_w2_88_scan.py`, 14 cases): every gitleaks process reads one file's text (12
  clean files, 12 times the rule sets' processes, each input holding exactly one file's marker); no batched name is left
  in the module; the verdict per file is the one-per-file form's in the order asked; links; namespaces; a gitleaks that
  cannot run refuses; `scan: off` starts no gitleaks; counts one per file; a clean file is remembered and not scanned
  again; P1-1's bare-key pairs (4 tails by 4 heads, three orders) and the pair in the middle of a long list; a record
  written under form 4 or 5 is not reused; a commit hash of the project is no finding. The cases only a batched scan
  meets (few processes, parallel batches, put-back and fence internals) are deleted. Run against the batched code
  first: 4 of 14 failed (the one-file and no-batch cases, and the form cases); after the revert: 14 of 14 pass.
