# The classification rubric: the standard repository layout, its classes and how material is classed (DEC-1255 (3))

Independent auditor (Opus, high: rule 7's one exception, a wide audit the owner asks for), read-only, 2026-11-26. Base:
`w2/integrate` at `c9351bba7`; D3 read from `e2/bundle-a`, the adoption guide from `e2/bundle-b`. **A proposal for the owner's
yes**, with its decisions page `docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html` (batch
`B-2026-11-26-rubric`, 17 cards). Nothing here is in force until he answers. Then the rubric joins the rubrics register
(DEC-1252 RG-0 to RG-2), and W2-213's spec (`.tickets/DAEO-stdl.md`) is written from it.

Every rule carries its basis (DEC-1233 (6)): a decision, a Contract item, an incident (FINDINGS `I-nn`) or a line of code.
"Card R-nn" or "C-nn" points to the choice on the page. Where the page offers options, this file states the recommended
one.

---

## 0. What was found (the evidence the rubric rests on)

1. **Guessing staleness from words fails both ways.** D3's stage A3 refused any namespace whose name or paths held
   `legacy`, `archive`, `superseded` or `historical` (`e2/bundle-a:src/gov/retrieval/stale.py`, `STALE_WORDS`,
   `unclassed`). It turned about 300 of batch A's 318 reds red (I-40, `DIAGNOSIS-bundle-a-1.md`) and would have dropped
   the live documents of any catch-all namespace once classed as told (DEC-1254 E-02). The other way, EXAMIN's likely
   stale sources carry no stale word at all: its pre-adoption register `docs/decisions/**` is "kept as history" and
   `docs/reports/**`, `docs/audits/**` are "dated history", yet all three are embedded namespaces (EXAMIN
   `governance/project/path-map.yaml`, namespaces `plans` and `reports`). Its fresh 80 lost 3 of 5 hidden misses to a cited
   stale or superseded source (I-36; `docs/audits/wave0/memory/FRESH80-2026-11-25.md`). A word list could never find them;
   a place can.
2. **Each repository invents its own map.** Gov OS keeps its archive in `docs/archive/**` and `docs/emergency-2/archive/**`;
   EXAMIN in `archive/**` split over two namespaces, one keyword-indexed and one out of both indexes; ASMO OS in `archive/**`
   (`history`) plus `legacy-position`, `legacy-framework` and `recovery-evidence` spread over `spec/` and `governance/`.
   EXAMIN's `research` is "reference only, never instructions" yet embedded and ranked like its own rules. The kit's map
   holds only the kit's own trees (`template/governance/project/path-map.yaml`), so `gov init` starts a repository with no
   layout at all (I-25).
3. **Material git does not track goes unseen.** ASMO OS has four top-level folders (`ASMO-Web`, `GitHub-Harness`,
   `Infrastructure`, `UPIM-SPEC`) with **0 tracked files and not ignored**. Its CI namespace's provenance says the CI
   type-checks and builds ASMO-Web. "Every tracked file classed exactly once" (DEC-1255 (2)) would pass with all four missing.
   **Erratum (2026-11-26, the ASMO OS CTO's F-18, checked against `git ls-files --others --exclude-standard` = 0):** the four
   folders hold only **ignored** material (`ASMO-Web`: `dist/`, `node_modules/`, `.env`; `GitHub-Harness`: personal data its
   `.gitignore` keeps out on purpose; `Infrastructure`: old SQLite stores and `__pycache__`) or nothing (`UPIM-SPEC`); ASMO-Web's
   source is tracked at `spec/3-SPEC/ux/asmo-web/`, where CI builds it (`ci.yml:28`). The rule stands unchanged (R-08: every
   ignored root is one line, listed and never read); only this example was wrong.
4. **A6 cannot change a file's content.** `gov adopt` moves with `git mv` and refuses a batch whose commit is not "the planned
   moves and nothing else" (`src/gov/adopt/stages.py`, module docstring and `_batch`, `CONTENT_CHANGED`). Moving code
   breaks every import, manifest and test path that names it, and the impact-selected tests then roll the batch back every
   time. CAP-44.j already keeps a healthy native package layout unless the target is materially better (A3 asks for
   `materially_better` and `migration_risk`).
5. **Memory reads more than the path map says.** The record graph reads every Markdown file with an `id`, `type` and
   `status`, wherever it lies: a copied folder's `DEC-010` demoted the repository's own `DEC-010`
   (`IMPORTS-ADOPTION-SPEC.md`, "What the code does today"). EXAMIN's 1,568 answered adoption packages stay records wherever
   they are archived (EXAMIN `docs/audits/wave0/memory/MEMORY-ASSESSMENT.md`). So `archive/` and `imports/` need a rule in the
   graph, not only in the indexes.
6. **The secrets default-deny by sensitivity is not built.** CAP-03.a asks that secret-class paths be excluded from every
   index by default. No code reads a namespace's `sensitivity` as a secret class. Secrets are kept out only by gitleaks on
   content (`gov.secrets.indexable`), which `scan: off` turns off (DEC-1045).
7. **Imports are designed but nowhere placed.** The imports spec classes them use, absorb or study, with their memory policy
   (DEC-1222 (1), DEC-1223 (8)), but leaves every import where it lies ("no move ... of an import by adoption",
   `IMPORTS-ADOPTION-SPEC.md` non-goals). DEC-1255 puts each one whole in `imports/<name>/`. The solar app
   (`/home/usain/workspace/ASMO`, DEC-1246 (1)) shows a typical case. It is a folder inside another repository
   (`/home/usain/workspace`), it carries a vendored library (`Cesium/`, 387 tracked files), and it keeps an ignored `.env`.
8. **Hidden sets were reached by an ordinary glob** (I-28). A classing agent that walks a tree is exactly that risk, so the
   hidden-set rule must be held by code before any agent sees a chunk (DEC-1249 (2)).

---

## 1. The classes

Eighteen classes, a closed list held by code (card R-01). "Memory" uses three policies: **embedded** (keyword index and
vectors), **keyword** (keyword index only, `embedding_policy: not embedded`), **out** (`lexical_policy: not indexed`,
`embedding_policy: not embedded`, or `memory_class: product`, which the indexer never reads). "Tier" is the
`retrieval_authority` tier: governing, middle, reports, reference (last). "Moves" covers an owned repository's
restructuring at A6. Every move needs the owner's yes on that repository's plan (DEC-1255 (2); card R-11). The table says
when a class never moves at all.

| # | Class | Definition | How to tell it (signs) | Place in the standard | Memory, tier | Moves? | Basis |
|---|---|---|---|---|---|---|---|
| 1 | `code` | The repository's own source that is built or run | Under a manifest's package root (`pyproject.toml`, `package.json`, `Cargo.toml`, ...); imported by other code; a language the code graph reads | `src/`, or **the native package root its manifest names**, which the path map records as the code place | embedded, middle; code graph | **No** at A6 when it sits in a native layout; a code move is a ticket of its own | CAP-44.j; `stages.py` `_native`, `CONTENT_CHANGED`; card R-05 |
| 2 | `tests` | Tests of the repository's own code | Under `tests/`; test-runner names (`test_*.py`, `*.spec.ts`); `tests/acceptance/<ticket>/` by the test designer | `tests/` (acceptance under `tests/acceptance/<ticket>/`) | keyword, reports | As code: no, where the runner's configuration names it | DEC-1052 M-4 (Gov OS `tests`); MR-3 |
| 3 | `spec` | What the product must do: specs, KPIs, OpenSpec's living behaviour | Spec form (problem, goals, KPIs, `Fails if:`); `openspec/` | `docs/specs/`; `openspec/` stays at the root (its tool reads it there) | embedded, governing | Yes (into `docs/specs/`) | DEC-1255 (2); GOLDEN-WORKFLOW W7, Q-3 |
| 4 | `research` | Studies, experiments and their evidence, written by this repository; reference, never a rule | An experiment's record, a study, a measurement, a comparison; no decision status | `docs/research/` (one folder per study or experiment) | embedded, reports | Yes | DEC-1255 (2); CAP-01.c (research never silently a decision) |
| 5 | `docs` | Current own documents that are none of the above: guides, architecture, ADRs, plans, the decision register | Current, maintained; cited as how things are now | `docs/` (the register at `docs/DECISION_REGISTER.md`, the path map's `decision_register` key) | embedded, middle (ACCEPTED decisions governing) | Yes | DEC-1255 (2) ("everything ... has one place"); Gov OS's `retrieval_authority` |
| 6 | `record` | Dated evidence of what happened: close records, checkpoints, probes, audits, reports, findings, handovers, measures | A date in its name or front matter; written once and kept; true as of its date | `docs/records/<kind>/`. What Gov OS's own tools write keeps their place (`docs/close/`, `docs/checkpoints/`, `docs/probes/`, `governance/adoption/`) | keyword, reports | Yes, except tool-written paths | DEC-1052 M-4 (`doc-records`); EXAMIN's R1-NOT-GOVERNING miss (I-36); card R-03 |
| 7 | `governance` | Gov OS's working material in this repository: the overlay, tickets, root rule files | `governance/project/**`, `.tickets/**`, `CLAUDE.md`, `AGENTS.md`, `.rulesync/**` | `governance/project/`; `.tickets/`, `CLAUDE.md`, `AGENTS.md`, `.rulesync/` stay where their tools read them | embedded, middle (adoption records keyword) | **Never** (tool-fixed) | kit map `project`, `adapters`; I-16, I-24 (the rule files' generated block) |
| 8 | `kit` | The Gov OS kit as copied and updated by `gov update` | `governance/kernel/**`, `governance/framework.lock`, `.copier-answers.yml` | `governance/kernel/` | keyword, middle | **Never** (`gov update` writes it) | kit map `kernel`; EXAMIN `kernel` (not embedded); CAP-45 |
| 9 | `config` | Configuration a tool reads at a fixed path | Manifests and lock files, `.gitignore`, `.gitleaks.toml`, `lefthook.yml`, `.github/**`, `.claude/**`, Docker and CI files | Where its tool reads it (the root, mostly) | keyword, middle | **Never** | kit map `ci`, `repository`; A6 moves nothing a tool reads |
| 10 | `data` | The repository's own data: synthetic or test data, small enough to track | Data suffixes, CSV, JSON fixtures, binary data; declared in a spec's test-data table | `data/` (`tests/fixtures/` for a test's own small fixtures) | out (`memory_class: product`) | Yes, unless code names its path | DS-0 to DS-4 (DEC-1252); CAP-03.b; `gov.secrets.indexable` lets governance memory only |
| 11 | `generated` | Output a named generator rebuilds: build output, caches, logs, generated adapter copies, generated views | A generator named in its header or provenance; ignored build folders | Tracked: where its generator writes it. Untracked: ignored, one line per ignored root | keyword when tracked text; else out | Never moved; tracked build output by mistake is untracked, its generator named | `refactor_plan.py` `generated-no-folder`; Gov OS `kernel-adapter-copies` |
| 12 | `archive` | Material that is no longer true or no longer used: **superseded**, **historical** or **legacy** | Superseded by a named successor; a retired system; a plan done; status RETIRED, SUPERSEDED; `superseded_by:` | `archive/<stale_class>/<original path>` | **out** (D3's `stale_class`); found on purpose by path or `--include-stale` | Yes | DEC-1255 (2); DEC-1227 D3; W2-212 SR-1, SR-2; card R-06 |
| 13 | `import-use` | Something brought in that the repository runs on and does not own | Its own licence or manifest naming another project; a submodule; a vendored-folder sign; a "vendored from" note | `imports/<name>/`, whole, never restructured | text keyword, reference, labelled `import:use`; non-text out | Moved whole only | DEC-1255 (2); DEC-1222 IM-3 |
| 14 | `import-absorb` | Brought in to assess; the useful parts are taken into own code or spec | As use, plus an assessment ticket | `imports/<name>/` until parts are taken; **taken parts become own classes in own places** | as use; taken parts as their own class, origin noted | Moved whole only; taken parts land through a ticket | DEC-1222 (1); DEC-1228 (3) |
| 15 | `import-study` | Brought in to learn from, never the repository's decision. REA's reconstructed code always starts here | A study copy; another project's decisions or notes; code reconstructed by a tool | `imports/<name>/` (a study outside the products keeps its own folder, DEC-1228 (4)) | keyword plus meaning under the ceiling (2,000 chunks an import, 5,000 a repository), reference, labelled `import:study`; over it, keyword | Moved whole only | DEC-1222 IM-4; DEC-1223 (8); DEC-1228 (3) |
| 16 | `evaluation` | The visible halves of evaluation sets and the measure's own records inside a tree | `evaluation_sets.visible`; `fixtures/evaluation/*/visible/**`; the measure's declared files | Where the path map's `evaluation_sets` names it | **out** | No | DEC-1066 (3) G4; Gov OS `evaluation-fixtures`, `evaluation-sources` |
| 17 | `hidden-set` | The hidden half of an evaluation set | Named by the sets-root registry and `sets_root_hidden` only, **never by reading** | **Outside every repository**, in its registered sets root | never in any tree or index | Never by a plan. One found inside a tree is a stopper finding; its repository's CTO moves it | DEC-1249 (2); I-28 |
| 18 | `secret` | A file that exists to hold a credential (`.env`, key files, credential stores) | By name pattern and gitleaks rule id, **never by printing it** | Never tracked: it stays ignored where it is | **out of everything**, by its namespace's policy, not by the scan alone | Never by a plan. A tracked one is a stopper: the owner removes and rotates | CAP-03.a, CAP-03.e; rule 8 (a secret is P1); `refactor_plan.py` `secret`; finding 6 above |

**Not a class: `ask`.** An item the agent cannot class with confidence gets `class: ask` with a recommended class and one
question. It stays where it is and nothing about it moves until the owner or the CTO answers. Memory holds it as it does
today (card R-10; IM-2 (a), DEC-1222 (1): an unsure import is held, nothing is blocked).

**What stays the same everywhere.** Gov OS keeps its own classing until restructuring pays (DEC-1255 (2)). New material
in Gov OS follows the standard where it touches no path its tests pin (card C-04). A class's memory policy holds in every
repository on the standard, because the path map is generated from the standard and not written by hand (§3).

---

## 2. The standard layout

The standard lives in the kit (`template/governance/standard.yaml`, a new kernel file `gov update` carries). The path map's
namespaces are generated from it: one namespace per class (two for `import-study`: under and over the ceiling; three for
`archive`: one per `stale_class`) plus one per import. A3 then judges a generated map, not a proposal (card R-04).

```
<root>/
  CLAUDE.md  AGENTS.md  README.md       governance (rule files) / docs     tool-fixed, never move
  .claude/  .github/  .gitignore ...    config                             tool-fixed, never move
  .rulesync/  .tickets/                 governance                         tool-fixed, never move
  pyproject.toml  package.json  *.lock  config                             tool-fixed, never move
  src/   (or the manifest's native root) code                              native layout kept (CAP-44.j)
  tests/                                tests  (tests/acceptance/<ticket>/)
  openspec/                             spec   (tool-fixed)
  docs/                                 docs   (incl. DECISION_REGISTER.md)
  docs/specs/                           spec
  docs/research/<study>/                research
  docs/records/<kind>/                  record (Gov OS's tools' own record paths stay)
  data/                                 data   (own synthetic or test data; real data never tracked)
  governance/kernel/                    kit    (gov update only)
  governance/project/                   governance (path map, registers: imports.yaml, tool-registry.yaml)
  governance/adoption/                  record (adoption's stage records, tool-written)
  imports/<name>/                       import-use | import-absorb | import-study (one class per import, whole)
  archive/superseded/<original path>    archive, stale_class superseded
  archive/historical/<original path>    archive, stale_class historical
  archive/legacy/<original path>        archive, stale_class legacy
  (outside every repository)            hidden-set: the registered sets root
  (ignored, untracked)                  secret, generated: listed by root, never read
```

**Rules of the layout.**

- **L1. One place per class, computed.** The destination is a function of the class and the path: `archive/<stale_class>/`
  plus the original path; `imports/<name>/` plus the path inside the import's root; `docs/specs/`, `docs/research/<study>/`,
  `docs/records/<kind>/` plus the file name; the path itself for a class that does not move. Code computes it, and the
  agent's `destination` must equal it (§4 check 3). *Basis:* DEC-1255 (2) ("every destination where the standard puts that
  class"); GOLDEN-WORKFLOW rule 4.
- **L2. Tool-fixed paths never move.** A file a tool reads at a fixed path (the manifests, CI, agent settings, the kit,
  the rule files, `openspec/`, `.tickets/`, and the records Gov OS's own commands write) keeps its place whatever its class.
  The standard lists them; the list grows only by the owner's yes on the rubric. *Basis:* A6 moves nothing it cannot prove
  safe (`stages.py`); I-16, I-24 (the rule files' generated block is matched by its place).
- **L3. Code and its tests keep their native layout** (card R-05). The path map records the manifest's package root as the
  code place. A code move is a ticket of its own, through the flow and its tests, never an A6 batch. *Basis:* CAP-44.j;
  finding 4 above.
- **L4. A move another file names is rewritten or held.** Before A6, code lists every tracked file that names a path to
  move (W2-190 S1's reference search, used for moves as well as deletes). A Markdown link or a path in a document's text or
  front matter is rewritten by code in the same batch, and each rewrite is listed in the plan the owner approves. A code or
  configuration file that names the path holds the move: the item stays and the plan names it. *Basis:* W2-190 S1
  (`DELETE_REFERENCED`); finding 4 above; card R-05.
- **L5. An import is never restructured.** Its tree moves whole and nothing inside it is renamed, split or edited. One
  import has one class. *Basis:* DEC-1255 (2); CAP-44.j.
- **L6. Nothing secret or hidden is ever in a plan's moves.** *Basis:* DEC-1249 (2); CAP-03.a; rule 8.

---

## 3. How memory treats each class (the path map generated from the standard)

The policies are in §1's table. These rules carry them into code (card R-02):

- **M1. Generated, not written.** On a repository that follows the standard, the path map's namespaces, their policies,
  `stale_class` and the `retrieval_authority` tiers are generated from `standard.yaml` plus the import register. A hand edit
  is refused by `gov check` as drift, with the line to regenerate. *Basis:* DEC-1255 (2) ("its path map then follows the
  standard"); GOLDEN-WORKFLOW W1 (the path map as the one source).
- **M2. Stale by place.** The three `archive/<stale_class>/**` namespaces carry `stale_class` with `lexical_policy: not
  indexed` and `embedding_policy: not embedded` (W2-212 F1). No other namespace carries `stale_class`. D3's route (drop
  stale-class chunks from every route, `--include-stale`, a path named in the question, the bundle's `stale` list) stays
  exactly as built: it reads the class, not words. *Basis:* DEC-1227 D3; W2-212 SR-1, SR-2, F1.
- **M3. The record graph follows the path map.** Records under `archive/` stay resolvable by id as history: they are marked
  stale, never ranked as current, and give no SUPERSEDES edge into a live record. Markdown under `imports/` is never a record
  or an edge. *Basis:* finding 5 above; the imports spec ("the record graph skips imported Markdown"); card C-02.
- **M4. Imports are labelled and ranked last.** As the imports spec designs it: `import:use` and `import:study` labels
  computed from the namespace, one last tier `reference`, the size ceiling. *Basis:* DEC-1222 IM-3, IM-4; DEC-1223 (8).
- **M5. Secrets by policy, not by scan alone.** The `secret` class's namespace is `not indexed`, so a secret-class path is
  kept out even when the scan is off. *Basis:* CAP-03.a (default-deny); DEC-1045; finding 6 above.
- **M6. Rebuilt after every restructure, by the plan itself.** The plan's last step runs `gov rebuild` and checks the store
  at HEAD. It does not wait on the refresh hook, which does nothing in an adopted repository today. *Basis:* I-43;
  GOLDEN-WORKFLOW W3.

---

## 4. How the classing runs: the fixed form and the checks code runs

**Who classes what.** Code classes everything a rule decides alone (DEC-1233 (6), GOLDEN-WORKFLOW rule 4): tool-fixed paths
(L2); `governance/kernel/**` (kit); paths the registries name (hidden sets, evaluation sets, the import register's existing
lines); ignored roots matching the secret name patterns (`.env*` except `*.example`, `*.pem`, `*.key`, `id_rsa*`,
credential stores); ignored generated roots (`node_modules/`, `.venv/`, `__pycache__/`, `logs/`, `pids/`, build folders).
Agents (Sonnet, DEC-1225) class the rest.

**Chunks.** Code splits the remaining items into disjoint chunks by path prefix, balanced by file count, **up to ten**,
started within the machine's gate (DEC-1255 (2); W2-207). Before any chunk is built, code removes every path of the
sets-root registry and of `sets_root_hidden`, and every file gitleaks flags (by rule id only). An agent receives its chunk's
path list. It also receives the signs code computed for each path: MA's vendored, generated, binary and minified lists;
manifests and licence files; front matter `status` and `superseded_by`; subtree trailers; whether other code imports the path;
D3's stale words as a hint; and the last commit's date. It may open a file of its own chunk, and nothing else. *Basis:*
DEC-1249 (2), I-28; `adopt/assess.py`; the imports spec's signs table.

**What is classed** (card R-08): every tracked file; every untracked file git does not ignore (`git ls-files --others
--exclude-standard`); every ignored root, as one line; every submodule entry; and every declared line of the import
register (material outside the tree). *Basis:* finding 3 above (ASMO OS); DEC-1255 (2) ("each file, folder and piece of
material").

**The form each agent writes** (one JSON object per line, card R-09):

```json
{"path": "docs/plans/roadmap-2025.md", "kind": "file", "class": "archive", "stale_class": "superseded",
 "import": null, "destination": "archive/superseded/docs/plans/roadmap-2025.md",
 "reason": "front matter status SUPERSEDED, superseded_by docs/plans/roadmap-2026.md", "sign": "front-matter",
 "ask": null, "chunk": "c03", "agent": "<session id>"}
```

- `path`, `class`, `destination` and `reason` are the owner's four fields (DEC-1255 (2)). `kind` is one of `file`,
  `folder`, `untracked`, `ignored-root`, `submodule` or `declared`. `stale_class` is required for `archive` and refused
  otherwise. `import` (the import's name) is required for the three import classes and refused otherwise. `sign` is the
  signal the reason rests on: `path`, `manifest`, `licence`, `header`, `front-matter`, `history`, `imports`, `content` or
  `registry`. `ask` is `null` or `{"question", "recommended"}`, and is required when `class` is `ask`.
- **A folder line** covers every file below it. It is allowed for an import, an archive move of a whole folder,
  `generated`, `data`, and any folder whose files all share one class. A file line below a folder line is a double.

**The checks code runs on the merged answers.** A failure goes back to its chunk's agent, with the lines named, at most
twice (GOLDEN-WORKFLOW rule 3). A third failure goes to the CTO.

1. **Exactly once.** Every item of "what is classed" is covered by exactly one line, after folder lines are expanded.
   A gap or a double fails, naming the path.
2. **Valid.** `class` is in the closed list; the required fields for that class are present and nothing else; `stale_class`
   is one of three values; `sign` and `kind` are from their lists; `reason` is not empty and is not a copy of another
   line's reason across more than ten paths (a filled-in template).
3. **Where the standard puts it.** `destination` equals L1's function for the class, the path and the import name. A class
   that does not move has its own path as its destination. A move out of a tool-fixed path or a native layout fails.
4. **Coherent.** One import, one class: every line under `imports/<name>` and every line naming that import carry the same
   import class (L5). No two items share one destination (A3's "target is taken"). No destination is an existing path. A
   `hidden-set` path found inside a tree, or a tracked `secret`, is a **stopper**: it is reported at once and never planned.
5. **References.** L4's search runs. Text references are listed for rewrite; a code or configuration reference holds its item.
6. **The map compiles.** The path map generated from the standard and the merged answers holds every path in exactly one
   namespace (A3, G-8). Every stale namespace has both policies (W2-212 F1). A study import over the ceiling is placed in
   the keyword namespace by code.
7. **Deterministic.** The plan is a pure function of the merged answers, the standard's version and the commit. Its hash is
   recorded, and the same inputs give the same plan.

**Then**, as DEC-1255 (2) orders: the orchestrator reviews the merged classification and the plan (each move, each
namespace, what memory will hold, every `ask`). An owned repository's plan goes to the owner (card R-11). Code executes the
approved plan through A6: the moves in batches with rollback points, the path map regenerated, the store rebuilt and checked
at HEAD (M6), the impact-selected tests, and a rollback on any break. A7 verifies it with a fresh auditor.

---

## 5. Kind by action

"Owner" means the owner's yes is needed; "CTO" means the CTO decides at P2 (rule 8). A dash means the action does not apply to
that kind.

| Kind | Adoption | Importing | Installing a tool | Testing a tool before use | Retiring |
|---|---|---|---|---|---|
| **Developed product** (EXAMIN) | Classed whole (§4). Specs, research, records, current docs, archive material, imports and own data move to their places at A6. Code and tests stay in their native layout (L3); the kit, config and governance stay (L2). The path map is regenerated and memory rebuilt. Already adopted, so this is a re-run of A1 to A7 with the generated map. **Owner:** the plan's moves | A new import lands whole in `imports/<name>/` with its register line (origin, kind, class, pin, licence, who, when). **CTO** for use and study, confirmed at the next A5 or by the register commit. Absorb's taken parts land through a ticket, with `commercial_licence` stated | A registry line in `governance/project/tool-registry.yaml` (MCP tools with `kind: mcp` and their roles); installed in a pinned prefix outside the tree; nothing in the tree but the line. **CTO** (G7); **owner** if paid or it needs a secret | In a run folder outside the product. The trial's own records come back as `research` (`docs/research/<trial>/`); nothing of the tool enters the tree until it passes and is installed. **CTO** | Superseded or retired material moves to `archive/<stale_class>/` as a chore (git keeps everything). Retiring the whole product: a tag, the tree read-only, nothing moves. **Owner** for the whole product (irreversible outside a worktree, rule 8) |
| **Light repository** (ASMO OS) | As the product. Also: the four folders (`ASMO-Web`, `GitHub-Harness`, `Infrastructure`, `UPIM-SPEC`) hold only ignored material or nothing (erratum, F-18): each ignored root is one line, never read (R-08). The legacy framework (`framework.json`, `governance/framework/**`, `scripts`, `memory`, `hooks`, `tools`) and `spec/1-NOW` position files go to `archive/legacy/`. **Owner:** the plan; timing in card C-03 | As the product. The solar app (DEC-1246 (1)), studied from ASMO OS, is a **declared** study import (a register line naming its folder, nothing copied): it lives inside another repository, carries `Cesium/` and an ignored `.env`. **CTO** | As the product | As the product | As the product |
| **Fresh repository** | `gov init` lays out the standard and generates the path map from it (I-25). Nothing to class until material arrives; each new file goes to its class's place, and the landing's path-map check (G-8) names a file outside it | As the product | As the product | As the product | As the product |
| **Imported tool or library** | Found by the signs (§4) and classed use, absorb or study. Moved whole into `imports/<name>/` with the owner's yes on the plan (card R-07). A package dependency (manifest and lock file) is one register line per pair; its files stay where its tool reads them (L2). Never restructured (L5) | It is the import: whole in `imports/<name>/`, one class, a register line. **CTO** (use, study); absorb's licence line is required by code | An MCP tool is an import registered in the tool registry (DEC-1228 (2)), not copied into the tree. **CTO** (G7) | The tool is tried in its own folder outside the products on synthetic material (DEC-1228 (4)) | Register line `state: retired`; the folder leaves the active tree, reachable at the retirement ref (A8's precedent); for a tool, the registry's `removed` state and its uninstall line. **CTO** |
| **Code reconstructed with REA** | Found as an import with `produced_by: rea@<version>` and its origin (app, version, date) | Always `import-study` first, in the study's folder outside the products or in `imports/<name>/` of the repository that studies it. Absorb only with `commercial_licence: held` or `not needed`; without one it stays out of anything commercialised (DEC-1228 (3); audit 3 MT-11). **Owner** for any absorb into a commercial product without a held licence: the answer is no by his rule | REA itself is an MCP tool (registry, pinned, given only to the study's sessions) | The study runs on a synthetic repository with planted issues, never our own code (DEC-1228 (4)) | As an import |
| **Data sets** | Own synthetic or test data to `data/` (memory out), unless code names its path (L4). Real data is never tracked: a declared line naming the owner's decision (DS-2). Imported data sets are `import-use`, non-text, memory out. **Owner** for any real data | An imported data set is `import-use` with its licence; an unlicensed import is red as test data (DS-3) | — | Trial data is synthetic | Moves to `archive/historical/` or leaves the active tree. **CTO**; real data's deletion is the **owner's** (rule 8) |
| **Vendored and generated files** | Vendored third-party code is an import (`import-use`), moved whole. The framework's own kit is `kit`, never an import. Tracked generated files stay where their generator writes them (keyword). Build output tracked by mistake is untracked, its generator named in the plan | Vendored code is an import | — | — | Generated files are rebuilt, never archived |
| **Archives** | Legacy, superseded and historical material moves to `archive/<stale_class>/<original path>` (memory out, found on purpose). An existing `archive/` is re-sorted into the three subfolders | — | — | — | It is where retiring ends. Nothing in `archive/` is deleted by a plan |
| **Hidden evaluation sets** | Never classed by reading. Code writes their lines from the registry (class `hidden-set`, destination unchanged). One found inside a tree is a **stopper**, reported at once; its repository's CTO moves it to the sets root (DEC-1249 (2), P2) | — | — | — | Spent sets stay in the sets root; never moved into a tree |
| **Secrets** | Never read and never planned. An ignored secret file is listed by path. A tracked one is a **stopper**: the **owner** removes and rotates it (rule 8) | A secret inside an import is named by its import, and the import is held out of memory until it is removed (imports spec K9) | A tool that needs a secret is the **owner's** (rule 8) | Planted secrets in a trial are fake and named as such (`STUDY-startup-launchpad.md`) | Rotation is the owner's |

**What needs the owner's yes, in one list** (card R-11): an owned repository's restructuring plan; a tracked secret's removal
and rotation; real data anywhere; an absorb into a commercial product without a held licence; a paid tool or one that needs
a secret; retiring a whole repository; any change to this rubric (RG-0); restructuring Gov OS itself. **What does not:**
classing an import use or study (CTO, confirmed at A5); a tool install (CTO, G7); archiving after adoption (a chore, rule 6);
a new repository in the standard; moving a hidden set (its repository's CTO, DEC-1249 P2).

---

## 6. What stays judgement, and why

These stay with the classing agent, inside the fixed form that code checks (GOLDEN-WORKFLOW rule 4, §2):

- **Own or brought in.** The signs can conflict, for example a vendored-looking folder that many of the repository's own
  later commits edited. Only reading its history and content decides. An unsure item is `ask` (R-10).
- **Current, record or archive.** Whether a document is still true is a matter of meaning: a plan done, a register replaced,
  a report that is history and not a rule. Front matter (`status`, `superseded_by`) decides it by code where it exists.
  Elsewhere the agent decides and names its sign. This is where most errors will sit, so the orchestrator samples it first
  (card R-03).
- **Use, absorb or study.** This is the import's purpose, which the repository's intent decides (DEC-1222 IM-2: unsure means
  held as study).
- **Where an import begins and ends** (its name and root), and **whether data is synthetic or real** (its provenance; real
  data is the owner's).
- **The reason text.** Code checks that it is present, varied and names a sign; it cannot check that it is true. The
  orchestrator's review and A5's fresh auditor read it.

Everything else is code: the class list, the places, the destinations, the policies, the map, the checks, the plan, the
moves, the rebuild and the rollback.

---

## 7. Conflicts with standing decisions or the plan

| # | Conflict | Cited | Proposed resolution | Card |
|---|---|---|---|---|
| X1 | D3's A3 refusal guesses staleness from words; the standard sets it by place | DEC-1227 D3; W2-212 SR-3, SR-4; DEC-1254 E-02 ("a stopgap only"); DEC-1255 (2) | §8 | C-01 |
| X2 | The imports spec never moves an import; DEC-1255 puts each one whole in `imports/<name>/` | `IMPORTS-ADOPTION-SPEC.md` non-goals and IM stage ("moves, copies and deletes no import"); CAP-44.j; DEC-1255 (2) | DEC-1255 wins (the later owner decision). The IM stage still classes and registers. A6 moves the whole tree in an owned repository with the owner's yes. Package dependencies and anything a tool reads at a fixed path stay as register lines | R-07 |
| X3 | A6 changes no file content; restructuring moves material other files name, and code moves break builds | `stages.py` (`CONTENT_CHANGED`); CAP-44.j; DEC-1255 (2) ("code executes the approved plan ... a rollback if anything breaks") | L3 (code stays native) and L4 (text references rewritten by code in the batch and listed; code references hold the item) | R-05 |
| X4 | The record graph reads every Markdown record wherever it lies; `archive/` and `imports/` must not speak as current | Imports spec ("the record graph ignores the path map"); EXAMIN MEMORY-ASSESSMENT (1,568 packages) | M3 | C-02 |
| X5 | ASMO OS is mid-adoption (its questions before A6 answered in its CTO's chat, DEC-1251 D-08); W2-213 lands at the earliest after 0.1.9 | DEC-1251 D-08; DEC-1255 CTO's call (release after 0.1.9) | Card C-03 (recommended: ASMO OS runs A6 now with its own map and moves only what is safe; it re-runs to the standard when W2-213 ships) | C-03 |
| X6 | "Gov OS keeps its classing", yet the rubric register binds through the kit; and new Gov OS material (imports, studies) has no place | DEC-1255 (2); DEC-1252 RG-2 | The rubric's register row `binds: every repository but Gov OS's existing paths`; new material in Gov OS follows the standard where no test pins a path | C-04 |
| X7 | DEC-1254 E-02 asks to confirm that EXAMIN's three stale citations leave default memory. The fresh-80 record names counts only, no paths | DEC-1254 E-02; EXAMIN `FRESH80-2026-11-25.md` (counts only) | Card C-05 | C-05 |
| X8 | CAP-03.a's default-deny of secret-class paths is not built; only gitleaks, which can be off, holds it | CAP-03.a; DEC-1045; `gov.secrets.indexable` | M5 (the `secret` class's namespace is not indexed) | R-02 |
| X9 | The imports spec says the tool registry is not the import register; DEC-1228 (2) registers MCP tools in the tool registry | `IMPORTS-ADOPTION-SPEC.md` (non-goals); DEC-1228 (2); audit 3 MT-5 | The decision wins: tools, MCP included, in the tool registry (`kind: mcp`); the import register cross-references by name; nothing is recorded twice | — (settled by DEC-1228) |
| X10 | The golden workflow's W1 and W2 already ask for this outcome ("imports classed use, absorb or study"; "stale and legacy material kept out of default memory") | GOLDEN-WORKFLOW W1, W2 | No conflict: the rubric is how W1 and W2 get there | — |

---

## 8. What happens to D3's word-guessing once the standard exists

- **Kept, unchanged:** the retrieval half of D3 (W2-212 SR-1, SR-2, F1). Stale-class chunks are dropped from every route,
  found on purpose by path or `--include-stale`, and marked in the bundle. It reads `stale_class`, never a word, and the
  standard's three `archive/` namespaces feed it (M2).
- **Retired on a repository that follows the standard:** A3's `ADOPT_STALE_CLASS` refusal and its notices. The map is
  generated, so there is no proposal to refuse. A `stale_class` outside `archive/` is drift that `gov check` names (M1).
- **Demoted to a sign:** `STALE_WORDS` and `unclassed()` become one of the signs code hands the classing agent ("this path
  says legacy"). A sign is never a decision.
- **Kept as the stopgap on repositories not yet on the standard** (Gov OS; EXAMIN and ASMO OS until their re-run): DEC-1254
  E-02's amended rule, with A3 refusing only a namespace stale as a whole and `gov doctor` naming mixed ones as a notice.
  Once every adopted repository except Gov OS follows the standard, the word check is deleted (W-2, DEC-1233 (4): no dead
  code). Gov OS's map is kept by hand.

---

## 9. Where it goes next

1. The owner answers `B-2026-11-26-rubric`.
2. The CTO records the answers (a decision), adds the rubric's row to `docs/RUBRICS.md`, which does not exist yet (RG-0;
   its first row is this rubric, enforcement `code` once W2-213 lands, `instruction` until then), and its kit copy (RG-2).
3. A product-spec session writes W2-213's spec from §1 to §8 as answered, with KPI lines for: the standard file and
   `gov init`; the generated path map; the classing form and the seven checks; the chunking within the gate; L4's reference
   rewrite; M3 in the record graph; M5; the plan, the yes, the execution and rollback; the D3 retirement in §8. The test
   data: a synthetic owned repository with planted material of all ten kinds, including an untracked folder, a referenced
   document, a vendored library, a fake secret and a registered hidden-set path that must never be opened.

---

## Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-26 | First proposal (DEC-1255 (3)), for the owner's yes on `B-2026-11-26-rubric` |
