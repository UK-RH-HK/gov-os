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
  `over-limit`, and `not-indexed` for a namespace whose `lexical_policy` keeps it out: an addition to the enum, so
  that no file is named with a wrong reason).
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
