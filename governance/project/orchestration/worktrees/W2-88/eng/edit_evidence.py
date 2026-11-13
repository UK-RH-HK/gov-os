p = "/home/usain/gov-os-worktrees/W2-88/docs/changes/W2-88-evidence.md"
s = open(p).read()

# header
s = s.replace('''## Seams (P-1, P-4, P-6, P-10; the three values)

Batch 1 of run 3, committed alone for the test designer's narrow revision. After this commit a seam's name or form
changes only with a later commit's subject saying so, and the return naming it. Every path:line is of this branch at
`b482fc5bf` (the base of run 3).
''', '''## Seams (P-1, P-4, P-6, P-10; the three values; run 4's decided items are item 8)

Batch 1 of run 3, committed alone for the test designer's narrow revision. After this commit a seam's name or form
changes only with a later commit's subject saying so, and the return naming it. Items 1 to 7 are as run 3 left them,
**except where item 8 says otherwise** (run 4: review round 1's findings and P-W2-88-B-1; items 4, 5 and the no-route
sentence of item 6 are superseded there).
''')

# item 1: the scan is compared only when it ran
s = s.replace('''- **Over the budget** is `vector_scan_ms > budget_ms`;''', '''- **Over the budget** is `vector_scan_ms > budget_ms` (only a vector scan that ran: item 8, RV1-2);''')

# item 4: superseded
s = s.replace('''### 4. P-10: the `retrieval.yaml` key of each `fabric.STANDARD` setting
''', '''### 4. P-10: the `retrieval.yaml` key of each `fabric.STANDARD` setting (superseded by item 8: only the pool has a key)
''')
s = s.replace('''### 5. P-6: the stage that copies the kernel's retrieval skill and T-0

**None.**''', '''### 5. P-6: the stage that copies the kernel's retrieval skill and T-0 (run 3's finding; built in run 4, item 8)

**None, at run 3.**''')
s = s.replace('''So S15's copy has no existing stage. I add **no copy code**. The lead returns the case as a package (it is not moved to
W2-88a, P-6 (a)).''', '''So S15's copy had no existing stage. The lead returned the case as package P-W2-88-B-1, which decided it (B-1.1 (a),
B-1.3 (a)): the copy step is `fabric.install` at A9 (item 8). A0 (`safety.py`) is not touched.''')

# item 6: the no-route rule
s = s.replace('''A file whose suffix is in no list and is no document is `no_route` with reason `unsupported-language`. The lead or the CTO confirms it against the tool on the machine that has it.''',
'''The no-route rule is stated once, in `assess.py`'s module text, and in item 8 (RV1-8). The lead or the CTO confirms the list against the tool on the machine that has it.''')

s = s.rstrip("\n") + "\n"
marker = "## Proof (a):"
item8 = '''### 8. Run 4: review round 1's findings and package P-W2-88-B-1 (the seams as built)

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
    stores' lists name them). On any refusal after the copies, `fabric.undo` takes them out (a hard reset to the commit
    the stage found, the copies and the folders made for them removed): a refusal writes nothing in the tree. An
    untracked file at a destination is never overwritten (`ADOPT_WOULD_OVERWRITE`).
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
  code did not apply.
- **Accepted seams, unchanged:** `fabric.RETRIEVE_BUDGET_MS = 2000` (provisional, for the owner's reading) with
  `--budget-ms <N>`; the sixth refused reason `not-indexed`; A9's question set only by `--questions <file>`.

'''
s = s.replace("## Proof (a):", item8 + "## Proof (a):", 1)
open(p, "w").write(s)
