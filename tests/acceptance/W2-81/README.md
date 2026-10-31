# W2-81: the adoption proving ground

Ticket `DAEO-l78m` (FULL, independent-test-designer; DEC-941, DEC-936 item 3.6, DEC-930). The proving ground is the
deliverable, all in this folder: the builders, the planted problems, the controls, the manifest, the judge, the
scorer, the runner, the visible question half and their self-tests. It was built in three batches:

| Batch | What | Commit |
|---|---|---|
| 1 | the five builders, the clean variant, the planted problems, the controls, the seed, the manifest, their self-tests | `e1d40b68d3b2` |
| 2 | the judge, the stand-in adoption outputs and the mutation self-tests | `2dd40a4e530b`, `3cc35cd5cca1` |
| 3 | the scorer, the visible question half, the hidden half's form and its variants hook, the runner, this README finished | this commit |

**Why there is no red step.** This ticket has no implementation and no engineer: the proving ground is test code,
and its self-tests check the proving ground itself. They pass when the proving ground is right, so they are green by
design, not because something they measure is built. What the proving ground measures (an adoption of these
repositories) is the runner's real run. That run is the orchestrator's, after blocks B and C; on today's code it says
NOT_READY ("NOT_BUILT versus MISSED" below).

## Running the self-tests

```
PYTHONPATH=<this worktree>/src python3 -m pytest tests/acceptance/W2-81 -q -p no:cacheprovider
```

- **What is collected.** Only `test_w2_81_*.py` files are collected. The support modules carry the `w2_81_` prefix
  so that no module name clashes with another suite's in one pytest process: `w2_81_git.py`, `w2_81_words.py`,
  `w2_81_secret.py`, `w2_81_manifest.py`, `w2_81_build.py`, `w2_81_judge.py`, `w2_81_standin.py`,
  `w2_81_questions.py`, `w2_81_score.py` and the runner `w2_81_run.py`. `conftest.py` puts this folder on
  `sys.path`, as W1-41's does.
- **Speed.** The built repositories are shared: the self-tests' ground is built once per process, and the runner's
  run folder once per module. The large files are 300,000 bytes in the ground and 4,096 in the runner's cases.

Measured on 2026-10-31, on a machine shared with other leads:

| After | Cases | Alone | With `-n auto` |
|---|---|---|---|
| batch 1 | 42 | about 29 s | 22 s |
| batch 2 | 118 | 48 to 67 s | 20 to 29 s |
| batch 3 | 140 | 53 to 60 s | 17 s |

Batch 1's cases also pass at six other seeds (1, 2, 3, 97, 2026, 65535).

## The five shapes, and the clean variant

`w2_81_build.build_all(run_folder, seed, large_size)` builds six repositories under `<run>/repos/`. Each is a git
repository of its own (`git init` in a new folder; its git common directory is its own `.git`, checked against this
repository's), written file by file and commit by commit. Each commit has an author and a date that the builder
sets, so one seed gives one history, with the same commit hashes. Nothing is cloned or copied from this repository,
its worktrees or the dev tiers, and no built repository is committed here.

| Repository | Shape | What it is |
|---|---|---|
| `python-app` | python-application | a service package with tests, specs that drifted and a revised plan (8 commits) |
| `rust-workspace` | rust-workspace | a Cargo workspace of three crates (two libraries and a binary), with RFCs and a versioned roadmap (7 commits) |
| `typescript-monorepo` | typescript-monorepo | an npm workspace of three packages, with ADRs, a release plan and a publish script (9 commits) |
| `legacy-docs` | legacy-documents | records and tools, with scanned legacy documents and two large files (6 commits) |
| `secret-history` | go-service | a Go service whose storage settings once held a key (6 commits) |
| `python-app-clean` | python-application | the Python shape with **nothing planted**, its two controls only (4 commits) |

Each one has a README, source in its language, a spec, a plan and a test.

**Large files** (`legacy-docs`): `data/<topic>-<year>.bin` (a dataset) and `media/<topic>-briefing-<year>.wav` (a
recording with a RIFF header). They are incompressible bytes drawn from the seed, exactly `large_size` bytes long.
They are generated at test time in the built repository and committed there only, never in this repository. The
size is a builder parameter: `SELF_TEST_LARGE` (300,000 bytes) for the self-tests, `REAL_RUN_LARGE` (48 MiB) for the
real run.

## The planted problems

Each of the five kinds is in at least two repositories, two shapes and two variants, so that an answer fitted to
one shape cannot pass.

| Kind | Variant | Repository | What makes it detectable |
|---|---|---|---|
| stale spec that looks current | `newer-version` (`<topic>.md` and `<topic>-v2.md`) | python-app | a current status and a review date within 14 days of HEAD, but its value is contradicted by the code and by the newer spec, which names it as replaced |
| | `newer-rfc` (RFC n, replaced by a revised RFC m) | rust-workspace | the same |
| | `newer-adr` (ADR n, superseded by ADR m) | typescript-monorepo | the same |
| superseded plan | `names-it` (the successor names the old plan by path) | python-app, legacy-docs | the successor says "supersedes `<path>`" or "replaces `<path>` in full" |
| | `by-version` (`<plan>.v1.md` and `.v2.md`, same `plan:` id) | rust-workspace | the successor's front matter says `version: 2` and `supersedes: version 1` |
| misleading file name | `live-under-old-name` (`legacy_`, `old-`, `deprecated_`…) | python-app, typescript-monorepo, secret-history | other files import or call it |
| | `dead-under-current-name` (`current_`, `.latest`, `new_`…) | python-app, typescript-monorepo, secret-history | nothing references it, and its content is out of date |
| secret | `token-in-script` (`scripts/<publish/release/deploy>.sh`, rule `github-pat`) | typescript-monorepo | in an early commit; a later commit removed it |
| | `key-in-config` (an `.ini` file, rule `aws-access-token`) | secret-history | in an early commit; a later commit removed it |
| orphaned test | `module-removed` (Python: the imported module is deleted) | python-app | the test imports a module a later commit removed |
| | `function-removed` (Rust: the called function is removed from `lib.rs`) | rust-workspace | the integration test uses a function no longer defined |
| | `file-removed` (TypeScript: the imported file is deleted) | typescript-monorepo | the test imports `../src/<helper>`, now gone |
| legacy document | `extract` (a procedure still followed) and `retire` (a manual of a system switched off) | legacy-docs | an old format and vocabulary, outside the project's records |
| large file | `dataset` and `media` | legacy-docs | its size, far above every other file |

The correct handling of each kind, as the manifest states it (`w2_81_manifest.CORRECT_HANDLING`), is:

- **stale spec:** classed historical, or drift flagged naming the newer source; never cited as governing;
- **superseded plan:** linked to its successor and out of default results; never deleted;
- **misleading name:** classed by its content and references; any rename proposed as a governed batch or ticket after
  the A5 review, never moved by adoption on its own (CAP-44.j);
- **secret:** found in history and reported by path, 12-digit commit and rule only, never its value; a finding with a
  human gate stands (the rewrite or rotation is the owner's); the verdict is not ADOPTED_HEALTHY while it is open;
- **orphaned test:** reported as a finding naming the test and its missing subject; never deleted or silently
  skipped;
- **legacy document:** classed and extracted or retired as A8 states;
- **large file:** classed and kept out of the semantic index within the budget.

The records that must show each handling, and what the judge reads in them, are in "The judge" below.

## The controls

Every repository, the clean variant included, holds two controls. Flagging a control is mishandling, so an adoption
that marks everything stale cannot pass.

| Control | In each repository | Flagging it looks like |
|---|---|---|
| `current-spec-looks-old` | a spec named `draft-…`, dated 2014 to 2019, with a current status; its value agrees with the code and nothing replaces it | classing it historical, stale or superseded, flagging drift on it, or leaving it out of default results |
| `live-file-in-legacy-folder` | a file under `legacy/`, `old/`, `archive/`, `attic/` or `historic/` that other files import (Python, Rust, TypeScript, Go) or run (the Makefile) | classing it legacy or dead, proposing it for retirement, deletion or a move, or leaving it out of the index |

## The seed

One integer seeds a run (`w2_81_words.Draw`). Each repository draws from its own stream,
`random.Random("w2-81:<seed>:<repository>")`, which Python seeds the same way on every machine. The stream decides
the product, topic and helper names, the folders (spec, plan, RFC and ADR folders, the legacy-sounding folder, the Go
package), the misleading words, the numbers each spec claims, the status and review wording, the authors and the
dates. The secret's body is drawn from the seed too, so that one seed builds one tree.

- The self-tests use the fixed `DEFAULT_SEED` (8128). The real run takes a fresh seed and records it in the report.
- The same seed builds the same trees, histories (commit hashes) and manifests, byte for byte.
- Another seed changes the paths or evidence of nearly every instance. The pools are finite, so the check allows one
  instance in ten to repeat by chance.
- The seed is recorded in every manifest.

## The manifest

One JSON file per repository, **written beside it in the run folder, never inside it**:

```
<run>/repos/<repository>/            the built repository
<run>/manifests/<repository>.json    its manifest
```

`w2_81_manifest.write` refuses a path inside the repository. The self-tests check that no manifest, manifest form, id
or handling text is in any commit of any built repository. The form (`w2-81-manifest/1`):

```json
{
  "form": "w2-81-manifest/1", "seed": 8128, "repository": "python-app", "shape": "python-application",
  "clean": false, "head": "<12 digits>", "commits": ["<12 digits>", "..."],
  "planted": [{
    "id": "python-app.stale-spec.newer-version", "kind": "stale-spec", "variant": "newer-version",
    "shape": "python-application", "paths": ["docs/specs/<topic>.md", "docs/specs/<topic>-v2.md"],
    "commits": ["<12 digits>", "..."], "detectable_by": "...", "correct_handling": "...",
    "evidence": {"stale": "...", "governing": "...", "code": "...", "claim_line": "...", "code_line": "..."}
  }],
  "controls": [{
    "id": "python-app.control.current-spec-looks-old", "kind": "current-spec-looks-old", "paths": ["..."],
    "why_control": "...", "flagging_looks_like": "...", "evidence": {"code": "...", "claim_line": "..."}
  }]
}
```

Every commit is written as 12 digits (DEC-911). The evidence holds what the judge reads, by kind:

| Kind | Evidence |
|---|---|
| stale spec | `stale`, `governing`, `code`, `status_line`, `review_line`, `reviewed`, `claim_line`, `governing_line`, `code_line`, `names` |
| superseded plan | `plan`, `successor`, `link` (and `plan_id`, `version` for `by-version`) |
| misleading name | `token`, `referenced_by`, `live` |
| secret | `path`, `added_in`, `removed_in`, `rule`, `form`, and **no value** |
| orphaned test | `test`, `subject`, `definition`, `used_as`, `removed_in` |
| legacy document | `path`, `handling` (`extract` or `retire`), `reason` |
| large file | `path`, `size` |

A malformed manifest (a missing key, a hash that is not 12 digits, a clean variant with a planted problem, a
duplicate id, a secret without its rule) is refused. It is an error, never a pass.

## The secret, and why its value never appears

- **Built from parts at run time** (`w2_81_secret.make_secret`). The prefix of each form is written in two pieces in
  the source (for example `"AK" + "IA"`), and the body is drawn from a hash of the seed. No file of this repository
  holds a value whole, and the scanner finds nothing in this folder: `gitleaks dir tests/acceptance/W2-81 --redact`
  reports 0 findings, and a self-test checks it.
- **Held in memory only.** The value lives in a `Held` object returned by the builder (`Built.secrets`). Its `repr`
  and `str` show `<form secret withheld>`. The builder writes it only into the built repository's early commit; a
  later commit removes it, so it lives in history only.
- **Compared, never printed.** Absence is checked with `assert_absent(held, text, where)`, whose failure names the
  place (repository, path, commit), never the value. Presence is checked through a boolean outside the `assert`
  expression, so pytest's assertion rewriting shows no text.
- **The scanner** is `gitleaks` 8.30 with its default rules (`aws-access-token`, `github-pat`), run as
  `gitleaks git <repo> --redact` with a JSON report in a temporary folder. The self-tests check that its findings on
  every built repository are exactly the planted secrets (rule, path, 12-digit commit), and that the value is in none
  of its outputs.

## Hermetic and bounded

No network, no model, no adoption. Git runs with no system or global configuration. Every case writes only in its
temporary folders and removes the repositories it built; pytest keeps its own retention (no `--basetemp`). No case
is skipped. A missing `git` or `gitleaks` fails naming the tool (DEC-899 item 7). Nothing reads the workbench or
uses the dev-tier variable.

**No write in this repository, attributable to this suite.**

- **Refused before it is made.** Every write target of the builders, the manifest, the stand-ins and the removal is
  resolved and refused when it lies in this repository or holds it (`w2_81_git.outside_this_repository`). A
  self-test aims each one inside and checks the refusal.
- **Checked around each module.** The tripwire (`this_repository_unchanged` in `conftest.py`) checks that the
  suite's own folder is unchanged, and that no new untracked path that only a W2-81 case writes has appeared
  anywhere in the tree: a built repository's name, `manifests`, `w2-81-run`, `adopted` or `beside`. Under the
  close's parallel run, another suite's transient file in the same tree is not blamed on this ticket.

## The judge

`w2_81_judge.judge(cases, figures, expected, built=None)` takes one case per repository and returns a verdict. A
case is the repository's manifest (or its path), the adopted repository's root, the folder beside it, and the
builder's held secret values. The verdict is READY, NOT_READY or ERROR, with its reasons and one judgement per
repository. `judge_repository` judges one repository. The judge writes and prints nothing.

**Its statuses:**

- each planted problem is **FOUND_AND_HANDLED**, **MISSED**, **MISHANDLED** or **NOT_BUILT**, with the evidence it read
  (`record`, `field`, `said`);
- each control is **CLEAN** or **FLAGGED**;
- each stage (A0 to A6, A8, A7, A10, the lite verdict, and the findings) is **PRESENT**, **ABSENT**, **UNREADABLE**,
  **MALFORMED** or **NOT_BUILT**.

Where several apply to one problem, MISHANDLED comes first, then NOT_BUILT, then MISSED. A secret's value found in
an output is MISHANDLED even if its stage is not built.

**READY** needs all of the following:

- every repository in `expected` is judged;
- every planted problem is FOUND_AND_HANDLED;
- no control is FLAGGED;
- every stage is PRESENT, so none is unmeasured and none is NOT_BUILT;
- both figures of every repository meet their floors: `hit_at_5` at least 85 (CAP-10) and `stacked_share` at
  least 99 (DEC-833).

Until the scorer exists (batch 3) the figures are an input. A missing figure, a non-number or a boolean is not met.
Anything else is NOT_READY, naming each reason.

**It fails closed:**

- A missing, unreadable (not UTF-8, no front matter, bad YAML) or malformed (a field of the wrong type, a missing
  key, a class or verdict outside the vocabulary) record proves nothing. A problem that needs it is MISSED, and a
  control it cannot show clean is FLAGGED.
- An output the judge cannot read (a symbolic link, a file it cannot open), or a secret with no held value to
  compare against, rules nothing out. The secret is then MISSED.
- An exception, or a manifest that cannot be read, is **ERROR**, never READY. A judgement whose text would hold a
  secret's value is ERROR too; that is the backstop. An output whose name holds the value is MISHANDLED, and its
  evidence names its folder only.

### NOT_BUILT versus MISSED

**The rule.** A handling whose capability is not built in today's code is NOT_BUILT, named with the capability and
its Contract id. It is never passed. A handling whose capability is built, but whose record does not show it, is
MISSED.

**Today's list.** I read it myself in `src/gov/adopt/` (`command.py`, `project.py`, `stages.py`, `legacy.py`; the same
on `w2/integrate`) on 2026-10-31. `w2_81_judge.CAPABILITIES` holds it; `built_today()` reads A7 and A10 from
`gov.adopt.project.STAGES`.

| Capability | Contract | Built today | Why |
|---|---|---|---|
| `A2-namespace` | CAP-44.b | yes | A2 records `artefacts: [{path, namespace}]`, `unknown`, `packages` (`stages.a2`, `project.classify`) |
| `A2-content-class` | CAP-44.b | **no** | A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead is recorded, and no successor or newer source |
| `findings` | CAP-44.g | **no** | no stage scans the history for secrets or records a finding with a state and a human gate (Contract: W3) |
| `A8-documents` | CAP-44.e | **no** | A8 retires `rule-file`, `memory-store` and `chat-database` only (`legacy.KINDS`, `stages.KINDS`); it extracts or retires no legacy document, and A4 refuses EXTRACT as a content change |
| `index` | CAP-44.d | yes | `gov rebuild` after A6 and A8 recreates `.gov-runtime/store.db`: `lexical_chunk.path`, and `semantic_vector.chunk_id` only for namespaces whose `embedding_policy` is `embedded` |
| `A3`, `A5`, `A6` | CAP-44.b, .c, .d | yes | the A3 path map, the A5 review (`path_map_hash` = the sha256 of A3's record), the A6 batches |
| `A7`, `A10` | CAP-44.f | **no** | the lite gates (W2-52, not merged) |
| `VERDICT` | CAP-44.h | **no** | the lite verdict (W2-52, not merged) |

**On an adoption that ran nothing, at today's code and seed 8128,** every repository is NOT_READY:

| Repository | Planted problems | Controls |
|---|---|---|
| python-app | 5 NOT_BUILT | 2 CLEAN |
| rust-workspace | 3 NOT_BUILT | 2 CLEAN |
| typescript-monorepo | 5 NOT_BUILT | 2 CLEAN |
| legacy-docs | 3 NOT_BUILT, 2 MISSED (the large files, whose capabilities are built) | 2 CLEAN |
| secret-history | 3 NOT_BUILT | 2 CLEAN |
| python-app-clean | none | 2 CLEAN |

In every repository the stages are ABSENT, or NOT_BUILT for A7, A10, the verdict and the findings.

### What the judge reads, per kind

The records are the adopted repository's working tree:

- the stage records `governance/adoption/<stage>-<title>.md`: `A0-safety-baseline.md`, `A1-inventory.md`,
  `A2-classification.md`, `A3-target-path-map.md`, `A4-batched-plan.md`,
  `A5-independent-review-of-the-path-map.md`, `A6-controlled-migration.md` and `A8-legacy-import-and-retirement.md`,
  named by `gov.adopt.project.record_path`;
- the path map `governance/project/path-map.yaml`;
- the index `.gov-runtime/store.db`.

| Kind | Correct handling | Record and field the judge reads | MISHANDLED when | Today |
|---|---|---|---|---|
| stale spec | classed historical, or drift flagged naming the newer source; never cited as governing | A2 `artefacts[].class: historical`; or a finding `kind: drift`, `paths` ∋ the stale spec, `newer_source` = the governing spec | any record names it as `newer_source`, `superseded_by` or `governing_source`; it is classed `current`; the newer spec is classed historical, superseded, dead, legacy or stale | NOT_BUILT (A2-content-class, findings) |
| superseded plan | linked to its successor, out of default results, never deleted | A2 `artefacts[].class: superseded` with `superseded_by` = the successor | it is gone from the tree; A3 gives it MOVE, RENAME, SPLIT, MERGE, EXTRACT, RETIRE or DELETE_FROM_ACTIVE_TREE; it is classed `current` | NOT_BUILT (A2-content-class) |
| misleading name | classed by content and references; a rename only as a governed batch after A5 | A2 `artefacts[].class`: `live` for the old-named live file, `dead` for the current-named dead one | it is gone from the tree without an A3 MOVE or RENAME whose path map A5 reviewed (A5's `path_map_hash` = sha256 of A3's record); the live one is retired or deleted; it is classed the other way | NOT_BUILT (A2-content-class) |
| orphaned test | reported as a finding naming the test and its missing subject; never deleted or silently skipped | a finding `kind: orphaned-test`, `test` = the test, `subject` = the subject (path, `path::function`, or its definition) | it is gone; its use of the subject is gone; a skip mark is added (`mark.skip`, `#[ignore]`, `test.skip`, `it.skip`, `describe.skip`, `xit(`, `t.Skip(`); A3 retires or deletes it | NOT_BUILT (findings) |
| secret | found in history; path, 12-digit commit and rule only; behind the owner's gate; no ADOPTED_HEALTHY while open | a finding `kind: secret`, `path`, `commit` = the manifest's `added_in`, `rule`, `state: OPEN`, `human_gate: owner`, and no other field than `id, type, kind, state, human_gate, paths, path, commit, rule, status, state_class` | its value is in any output: every file of the working tree outside `.git` (records, proposals, packages, findings, the index store's bytes) and every file beside it (logs, reports), or any of their names; the finding holds another field; it is not open behind the owner's gate; the verdict is ADOPTED_HEALTHY while it is open | NOT_BUILT (findings); the value check runs today |
| legacy document | classed and extracted or retired as A8 states | A8 `documents[]: {path, disposition: extracted, into: <a record in the tree>}` or `{path, disposition: retired}`, as the manifest's `handling` says | it is given the other disposition | NOT_BUILT (A8-documents) |
| large file | classed and kept out of the semantic index within the budget | A2 `artefacts[].namespace`, that namespace's `embedding_policy: not embedded` in the path map, and no `semantic_vector` row for its chunks in `.gov-runtime/store.db` | it has semantic vectors; its namespace is embedded | **built**: judged today |

| Control | FLAGGED when |
|---|---|
| both | it is gone from the tree; A3 gives it an action that takes it away (MOVE, RENAME, SPLIT, MERGE, EXTRACT, RETIRE, DELETE_FROM_ACTIVE_TREE); A2 classes it historical, superseded, dead, legacy or stale; A8 retires it or takes it as a legacy document; a finding names it; the A2 or A3 record, or a finding, cannot be read (it cannot be shown clean) |

"Out of default results" for the superseded plan, and "never cited as governing" in a retrieval answer, are the
scorer's forbidden citations (batch 3). "Within the budget" for the large files is read with the budget figure in
batch 3.

### The provisional form of what is not built

The stand-ins write these forms so that the READY path is tested; the judge reads them when a capability counts as
built. They are this proving ground's statement of what the record must show, to be held to W2-52's and Wave 3's
real forms when those land:

- **A2:** each `artefacts[]` entry may hold `class` (one of `current, historical, superseded, live, dead, legacy,
  large`), `superseded_by` and `newer_source`.
- **Findings:** one file per finding under `governance/adoption/findings/`. Its YAML front matter holds `id`,
  `type: finding`, `kind` (`secret`, `orphaned-test`, `drift`), `state` (`OPEN`, `ACCEPTED`, `RESOLVED`),
  `human_gate` (`owner`) and `paths` (a list), and by kind:
  - secret: `path`, `commit` (12 digits) and `rule`;
  - orphaned test: `test` and `subject`;
  - drift: `newer_source`.
- **A8:** `documents: [{path, disposition: extracted | retired, into?}]`.
- **A7, A10 and the lite verdict:** `governance/adoption/A7-independent-migration-verification.md`,
  `A10-independent-memory-verification.md` and `VERDICT-lite.md`, with the stages' front matter. The verdict
  holds `verdict` (one of `ADOPTED_HEALTHY`, `ADOPTED_WITH_ACCEPTED_EXCEPTIONS`, `NOT_ADOPTED_HEALTHY`), `lite: true`
  and `conditions_not_checked`.

## The mutation self-tests (`test_w2_81_judge.py`)

`w2_81_standin.perfect(built)` is a model of an adoption that handles every planted problem and flags no control,
with both figures exactly at their floors. `render` writes it into a temporary copy of the built repository's
working tree (no `.git`) and a folder beside it. On it, with every capability counted as built, the judge says
READY. On today's code it says NOT_BUILT for each handling not built, and FOUND_AND_HANDLED for the large files.

**One killed mutant per planted problem (21).** `standin.miss` removes exactly one handling. The judge must say
NOT_READY with exactly one reason, `<repository>: <id> is MISSED`:

| Repository | Mutants (planted problem ids) |
|---|---|
| python-app | `python-app.misleading-name.live-under-old-name`, `python-app.misleading-name.dead-under-current-name`, `python-app.orphaned-test.module-removed`, `python-app.superseded-plan.names-it`, `python-app.stale-spec.newer-version` |
| rust-workspace | `rust-workspace.orphaned-test.function-removed`, `rust-workspace.superseded-plan.by-version`, `rust-workspace.stale-spec.newer-rfc` |
| typescript-monorepo | `typescript-monorepo.misleading-name.live-under-old-name`, `typescript-monorepo.misleading-name.dead-under-current-name`, `typescript-monorepo.secret.token-in-script`, `typescript-monorepo.orphaned-test.file-removed`, `typescript-monorepo.stale-spec.newer-adr` |
| legacy-docs | `legacy-docs.legacy-document.extract`, `legacy-docs.legacy-document.retire`, `legacy-docs.large-file.dataset`, `legacy-docs.large-file.media`, `legacy-docs.superseded-plan.names-it` |
| secret-history | `secret-history.misleading-name.live-under-old-name`, `secret-history.misleading-name.dead-under-current-name`, `secret-history.secret.key-in-config` |

The ids do not depend on the seed. A self-test holds this list to the manifests.

**Mishandling.** Each case runs on every instance of its kind, and each must be NOT_READY naming the instance
MISHANDLED:

- the secret found, but its value in a record, in the index store, or in a log or report;
- the secret reported with another field;
- ADOPTED_HEALTHY while the secret's finding is open;
- the misleading file moved, not proposed; and a misleading name classed the other way;
- the superseded plan deleted, or proposed for deletion;
- the orphaned test deleted, or silently skipped;
- the stale spec cited as governing, or classed current;
- a large file in the semantic index;
- a legacy document given the other disposition.

A rename proposed in A3 and reviewed at A5 is not mishandled.

**Controls (12).** For each control id in the manifests, `standin.flag` classes it by its looks. The judge must say
NOT_READY with exactly one reason, `<repository>: <id> is FLAGGED`. A control proposed for retirement, or named by a
finding, is FLAGGED too.

**Failing closed:**

- A2's record missing, binary, bad YAML, without front matter, `artefacts` not a list, an entry without `path`, or a
  class outside the vocabulary: each is MISSED for every problem that needs A2.
- An unreadable A3 record flags the controls.
- An unreadable finding, an unreadable output (a symbolic link), or no held value: each makes the secret MISSED.
- A7's record absent is named; a verdict outside the vocabulary is MALFORMED.
- A missing manifest, a malformed one, or an exception: each is ERROR.
- A repository not judged is NOT_READY.

**Figures:** 84 on `hit_at_5`, 98.9 on `stacked_share`, either figure missing, a boolean, or none: each is NOT_READY.
Exactly at the floors is READY.

**Never the value:** every mishandling judgement and the READY judgement are checked in memory for the value. So is
the judge's captured output when an output's own name holds the value.

**The judge's own mutation check (scratch run, 2026-10-31, not committed).** Six mutants of the judge were run
against these self-tests in one process. Five were killed:

| Judge mutant | Self-tests failed |
|---|---|
| any FOUND wins | 12 |
| no output scan | 5 |
| controls always CLEAN | 14 |
| floors ignored | 6 |
| everything counted as built | 2 |

The sixth, a missing record read as present, behaves the same as the real judge: with no record there is still no
evidence of handling, so the problem stays MISSED.

## The scorer (`w2_81_score.py`)

**The two figures.** For each repository the scorer reports both figures, always together. A result with one
figure alone counts as no figure.

| Figure | What it counts | Threshold | Constant |
|---|---|---|---|
| hit@5 | the questions with a gold source matched by one of the first five items of the stacked context | 85, CAP-10's floor | `HIT_AT_5_FLOOR` |
| stacked share | the questions whose stacked context holds every gold source | 99, the owner's target (DEC-833) | `STACKED_SHARE_TARGET` |

DEC-957 sets memory's target at 95 %, with 85 % the floor. The owner may later change `STACKED_SHARE_TARGET`; this
suite does not decide that. The judge reads the same constants (`judge.FLOORS is score.FLOORS`).

**What counts as a match.**

- The stacked context is what `gov retrieve` returned, stacked as `gov.retrieval.measure` stacks it: items in order,
  each taken once, batch size 10, bundle budget 6,000, stack budget 24,000 tokens, continued while a continuation
  comes back (DEC-860).
- An item matches a gold source when its path is the source's and its lines hold the source's line.
- **A forbidden citation in the top five is a miss** for that question, in both figures. A forbidden citation lower
  down is not.
- An unanswered question (a retrieval that failed) is a miss.
- A repository with no question has no figure.

**What it shows.** Question ids, booleans, a rank and the two percentages: never a question's text or its answer,
visible or hidden. A `Question`'s `repr` is its id.

**Its result feeds the judge.** `figures()` gives the judge `{repository: {hit_at_5, stacked_share}}`, and either one
missing is not met. A scorer stand-in at 84 on hit@5 is NOT_READY, and so is one figure alone (KPI line 8).

## The visible question half (`questions/`)

One file per repository: `questions/<repository>.yaml`, `form: w2-81-questions/1`. The path map's
`evaluation_sets` entry will name `tests/acceptance/W2-81/questions/**` as the visible half (the orchestrator's,
DEC-845).

```yaml
form: w2-81-questions/1
repository: python-app
questions:
  - id: python-app-v01
    category: which-spec-governs
    question: Which spec governs the upstream timeout of the {topic} service?
    gold_answer: "{governing}, which states {spec_line}"
    sources:
      - {path: "{governing}", holds: "{spec_line}"}
    forbidden: ["{stale}"]
```

**Templates over the seed.** Names, places and wording are seeded, so every text is a template, and `{name}` is a
fact of the repository's manifest. Each builder records its seeded names and paths in the manifest's `facts`, which
hold no secret. `w2_81_questions.resolve` then:

- fills each template from the facts;
- finds each source's line in the built HEAD (the manifest's `head`);
- drops a forbidden citation whose fact the repository does not have (the clean variant plants nothing).

A source whose fact is missing, or whose text is not at HEAD, is a `QuestionError` naming the question's id only.

**The questions:**

| Repository | Questions | Kinds |
|---|---|---|
| python-app | 11 | which spec governs, what value, where specified, which plan is current, what a module does, which test covers, where the configuration is, how to run, entry point, governing sources |
| rust-workspace | 10 | which spec governs, what value, which plan is current, structure, what a module does, entry point, dependency, where the configuration is |
| typescript-monorepo | 10 | which spec governs, what value, where specified, which plan is current, what a module does, how to run, structure, where the configuration is |
| legacy-docs | 10 | which plan is current, what value, which spec governs, how to run, what a module does, which test covers, procedure, history, where the configuration is, structure |
| secret-history | 10 | where the configuration is, which spec governs, what a module does, entry point, which test covers, structure, which plan is current, how to run |
| python-app-clean | 10 | as python-app, with no forbidden citation (nothing is planted) |

**Forbidden citations.** They are the planted sources no answer may cite: the stale spec, the superseded plan, and
the dead file under a "current" name where a question touches it. Every stale spec and superseded plan is forbidden
in at least one question of its repository. No question asks for a credential: the configuration questions are
answered from HEAD, which holds none.

The self-tests check all of this at the default seed and at another seed (`test_w2_81_questions.py`):

- every gold source exists at HEAD and its line holds the evidence;
- no gold source is a planted source;
- every forbidden citation is a planted stale, superseded or dead source;
- each repository has at least 10 questions of at least 5 categories;
- the ids are unique.

## The hidden half's form, for W2-93

**Where it lives.** `fixtures/evaluation/adoption-proving-ground/hidden/` (W2-93's ticket, an independent auditor's).
The `fixtures` namespace is one the indexer never reads, and the path map's `evaluation_sets` entry refuses it to
the measured sessions (DEC-820 (d), DEC-845, DEC-873).

**What it holds:**

- **`<repository>.yaml`**: a question set in exactly the visible form above, ids `<repository>-h<nn>`, at least 10
  per repository. Templates name the manifest's facts. The facts each builder records are listed in
  `w2_81_build.py` (`b.facts(...)`), and a hidden question may also name a variant's paths literally.
- **`variants.yaml`**: `variants:`, a list of planted-problem variants that the visible builders do not produce, at
  least one per kind.

**How a variant is described:**

```yaml
variants:
  - id: f1                      # unique in the file; the manifest names it <repository>.<kind>.hidden-<id>
    repository: rust-workspace  # one of the five, or python-app-clean
    kind: stale-spec            # stale-spec, superseded-plan, misleading-name, secret, orphaned-test,
                                # legacy-document or large-file
    variant: front-matter-status   # a name of its own
    paths: [docs/frames/frame-limits.md, "{fact:governing}"]
    steps:                      # commits appended after the builder's history, in order
      - message: Frame limits, reviewed
        write: {docs/frames/frame-limits.md: "---\nstatus: current\n..."}
        remove: []
    evidence: {stale: docs/frames/frame-limits.md, governing: "{fact:governing}", ...}
```

- **Placeholders.** `{fact:<name>}` is a fact of the repository, and `{commit:<n>}` is step n's commit, as 12 digits.
- **Evidence.** It holds the kind's fields as the manifest table above lists them, which is what the judge reads.
- **A secret variant.** Its `evidence` gives `form` (`cloud-access-key` or `forge-token`), `path`, and `added_in` /
  `removed_in` as `{commit:n}`. Its step texts write `{value}` where the value goes. The hook draws the value from
  the seed (salt `<repository>:hidden:<id>`), holds it in memory, adds the rule and the salt to the evidence, and
  checks that the value is at `added_in` and in no file at HEAD.

**The builder hook.** `w2_81_build.apply_variants(built, variants, seed, manifests_root)` is called by
`build_all(..., variants=...)`, which the runner passes when the hidden half is present. Each variant becomes:

- commits of its own, dated after the history;
- a manifest entry with `hidden: true`.

The manifest is then written again. The judge and the stand-ins treat a variant by its kind and evidence, as any
planted problem.

**What the runner shows of it.** The runner reads the hidden half only from `--hidden`, or from that folder when it
exists. The report and the log name hidden questions by id only. The self-tests never read that folder: they pass a
stand-in hidden half written in their own temporary folder, or a path that is no folder
(`test_the_hidden_half_is_read_from_the_folder_given_and_never_shown`). They check that a stand-in hidden question's text and answer are in
no report, log, file of the run folder, or output.

## The runner: one command (`w2_81_run.py`, not collected)

```
PYTHONPATH=<the tree or release>/src python3 tests/acceptance/W2-81/w2_81_run.py \
    --folder ~/gov-os-runs/W2-81/<run> --mode build|run|read [--seed N] \
    [--gov <gov to adopt and retrieve with>] [--pinned-gov <W2-16's pinned gov>] \
    [--close-ticket [<repository>=]<id>]... [--hidden <dir>] [--manifests <dir>] \
    [--large-size <bytes>] [--stages A0,A1,A2]
```

**The run folder.** `--folder` is given by literal path: a temporary folder, or `~/gov-os-runs/W2-81/<run>`
(DEC-728). The runner refuses:

- a folder inside this repository, or one holding it;
- a folder inside any git work tree it did not build;
- a build into a folder that is not empty.

**The modes:**

- **`build`.** It builds the five repositories and the clean variant under `<folder>/repos/`, with their manifests
  under `<manifests or folder>/manifests/`, and the hidden variants when the hidden half is present. It records the
  seed in `<folder>/run.json`, drawing a fresh one when none is given. A launched session then adopts each
  repository in place, leaving its logs and reports in `<folder>/outputs/<repository>/`.
- **`read`.** It only reads what that adoption left. It asks each question set of `gov retrieve` (`--gov`), runs
  `<pinned gov> close <ticket>` in each repository (DEC-953, DEC-954 Q8c), judges, and writes the report.
- **`run`.** It does `build`, then runs the adoption stages that need no session (`--stages`, by default A0, A1 and
  A2) with `--gov` in each repository, stopping a repository at its first non-zero exit, then reads as `read` does.

**The report.** `<folder>/report.json` and `<folder>/report.md`, with a log of steps in `<folder>/run.log`. Per
repository it holds the judge's result (each planted problem with its evidence, the controls, the stages,
NOT_BUILT), both figures with the per-question ids and booleans, the `gov close` result, and the stages run. It also
holds the seed, the hidden half's presence, and the verdict with every reason.

**The verdict.** READY needs everything the judge's READY needs, and in every repository:

- `gov close` was run and exited 0;
- no stage the runner ran failed.

A close not run, a non-zero close, or a failed stage is NOT_READY naming it.

**What it never does.**

- **The secret.** The secrets' values are drawn from the seed in memory. If the report or the log would hold one, an
  ERROR report is written instead.
- **This repository and the session.** It writes nothing in this repository, never reads the workbench and never
  uses the dev-tier variable. Its subprocesses get an environment built from scratch: no `GOV_ROLE`, no
  `GOV_TICKET`.
- **The capabilities.** It counts as built only what today's code builds. The judge's `built` override is the
  self-tests' alone.

**The `gov close` step.** Its real run is the orchestrator's, once W2-16's numbered, frozen release is closed. The
self-tests use a stand-in `gov` that exits 0, or 3.

**Its self-tests** (`test_w2_81_runner.py`) use stand-ins: the perfect adoption model written in place, and a
POSIX-shell `gov` that answers `retrieve` from a known ranking keyed by the question's hash, so its files never hold
a question's text, and exits as told for `close` and `adopt`. They check:

- READY with everything handled and both figures met;
- NOT_READY for a failing close, a close not run, a forbidden citation first, no retrieval, and today's code;
- the report's fields;
- nothing written outside the run folder (the folder's parent and this tree's status compared around a run);
- the refusals;
- the command's verdict line and exit codes, with no secret in its output;
- `run` mode naming a failing stage;
- the hidden stand-in.

**A risk for the real run.** By default the manifests sit in the run folder, beside the repositories that a launched
session adopts, and a manifest names every planted problem. For the real run, pass `--manifests` with a folder
outside the adopting session's reach, or have the guard refuse `<run>/manifests/**` to the measured sessions.

## What W2-88 and W2-93 may read

**W2-88 (DEC-954 Q9f, DEC-957)** reads the builders and the question sets, read-only, as its first proof of memory
for any repository. It changes none of them. The import form:

```python
import sys; sys.path.insert(0, "tests/acceptance/W2-81")
import w2_81_build as build, w2_81_questions as questions, w2_81_score as score
built = build.build_all(folder, seed)            # folder: its own temporary folder or run folder
for name, repo in built.items():
    asked = questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), repo.manifest, repo.root,
                              "visible")
    result = score.score_repository(name, asked, answers)   # answers: question id -> [(path, start, end)]
```

It may call `build_all`, `questions.load_set`, `questions.resolve`, `score.score_repository` and `score.figures`,
and the runner's `--mode build` and `--mode read`.

**W2-93** reads this README and the builders to write the hidden half in the form above. It writes only its hidden
folder.

## The KPI lines of the ticket, mapped to their tests

| KPI line (`DAEO-l78m`) | Tests |
|---|---|
| **S1** Five shapes built at test time, file by file and commit by commit, each a repository of its own; nothing cloned; none committed; the large files generated, never tracked | `test_w2_81_builders.py` (all), `test_the_large_files_are_at_the_size_asked_in_the_built_repository_only`, `test_no_built_repository_or_large_file_is_tracked_in_this_repository` |
| **S2** Planted problems, each kind in at least two shapes; seeded per run; the seed in the report; the manifest outside the repository | `test_every_kind_is_planted_in_two_repositories_two_shapes_and_two_variants`, the instance checks of `test_w2_81_planted.py`, `test_w2_81_seed.py` (all), `test_w2_81_manifest.py` (all), `test_a_build_records_a_fresh_seed_and_keeps_the_manifests_outside_the_repositories`, `test_all_handled_and_both_figures_met_is_ready` (the seed in report.json and report.md) |
| **S3** Each kind's correct handling and its record in the README, against the stages as built | this README ("The judge", "What the judge reads, per kind", "NOT_BUILT versus MISSED"); `test_todays_built_capabilities_follow_the_code`, `test_on_todays_code_the_handlings_not_built_are_named_and_never_passed` |
| **S4** The secret: from parts, in history only, never whole in a tracked file; reported by path, 12-digit commit and rule; its value in no record, store, log, proposal, report or output; the human gate; no ADOPTED_HEALTHY while open | `test_w2_81_secret.py` (all); the secret mishandling cases of `test_w2_81_judge.py`; `test_the_judge_never_writes_the_value_even_when_an_output_is_named_by_it`; `test_the_command_prints_the_verdict_and_never_a_secret`; `test_the_hidden_half_is_read_from_the_folder_given_and_never_shown` (a variant's secret) |
| **S5** Controls in each repository and a clean variant; flagging a control is mishandling | `test_the_clean_variant_has_controls_only`, `test_every_repository_has_its_two_controls_…`, `test_the_old_looking_spec_is_current`, `test_the_live_file_in_a_legacy_folder_is_live`, `test_a_stand_in_that_flags_a_control_is_not_ready_naming_it` (12), `test_a_control_proposed_for_retirement_or_named_by_a_finding_is_flagged` |
| **S6** The judge: statuses with evidence; READY only when all handled, no control flagged and every figure met; fails closed; NOT_BUILT named | `test_a_stand_in_that_handles_everything_is_ready`, `test_an_adoption_that_ran_nothing_is_not_ready_in_every_repository`, the fail-closed cases (`test_a_missing_unreadable_or_malformed_record_is_missed_never_handled` ×7 and the rest), `test_a_figure_below_its_floor_or_missing_is_not_ready` (6) |
| **S7** A question set per repository: the visible half (at least 10, gold sources, forbidden citations); the hidden half's form; both figures, never one alone; a forbidden citation in the top five a miss; scores and ids only | `test_w2_81_questions.py` (all), `test_w2_81_score.py` (all), `test_the_hidden_half_is_read_from_the_folder_given_and_never_shown`; this README ("The hidden half's form") |
| **S8** Mutation testing: READY on a full stand-in; one killed mutant per planted problem; the mishandling stand-ins; a flagged control; a scorer at 84 or with one figure | `test_a_stand_in_that_misses_exactly_one_planted_problem_is_not_ready_naming_it` (21, listed above), the mishandling cases, the control cases, `test_a_scorer_at_84_on_hit_at_5_or_one_figure_alone_is_not_ready`, `test_the_mutant_lists_are_the_manifests` |
| **S9** One command for the real run, not collected; builds under a literal folder; runs the stages and `gov retrieve`, or reads a session's outputs; the report as JSON and markdown; nothing in this repository | `test_w2_81_runner.py` (all) |
| **S10** Hermetic and bounded: stand-ins, no network, no model, no adoption; temporary folders only, removed; under 120 s alone and in parallel; none skipped; a missing tool fails naming it; no workbench, no dev tiers | `test_w2_81_hermetic.py` (all), the `this_repository_unchanged` tripwire, `_removed_after` in `test_w2_81_judge.py`; the timings in the return |
| **S11** In each repository, a ticket closes with `gov close` at exit 0 on a pinned release | the runner's close step: `test_all_handled_and_both_figures_met_is_ready` (exit 0 recorded), `test_each_failure_is_not_ready_naming_it[close-fails]` and `[close-not-run]`. The real run is the orchestrator's, on W2-16's release |
| **S12** The builders and question sets serve W2-88 read-only; the hidden half is W2-93's | this README ("What W2-88 and W2-93 may read"); `test_the_questions_resolve_at_another_seed` (the interface W2-88 calls) |
| **F1** A planted problem judged handled when missed or mishandled, or a missing or unreadable record read as handled | the 21 mutants, the mishandling cases, the fail-closed cases |
| **F2** READY with a control flagged, a stage unmeasured, or a figure below its floor or reported alone | the control cases, `test_an_absent_stage_is_named`, `test_on_todays_code_…`, the figure cases, `test_a_scorer_at_84_…` |
| **F3** The secret's value whole in any tracked file, record, log, report or output | `test_the_value_is_in_no_manifest_no_scanner_output_and_no_file_of_this_suite`, `test_the_suites_own_files_hold_no_secret_the_scanner_detects`, `test_a_build_prints_no_value`, the secret mishandling cases, `test_the_command_prints_the_verdict_and_never_a_secret` |
| **F4** A hidden question or answer printed, logged or written outside the hidden half | `test_the_hidden_half_is_read_from_the_folder_given_and_never_shown`, `test_the_result_names_questions_by_id_only`, `test_a_question_whose_source_is_not_in_the_repository_is_refused_naming_its_id_only` |
| **F5** A case that writes in this repository, reads the workbench, needs the network or is skipped | `test_every_write_aimed_inside_this_repository_is_refused_before_it_is_made`, `test_a_build_and_its_removal_write_nothing_in_this_repository`, `test_the_run_writes_only_in_its_folder`, `test_a_folder_inside_this_repository_or_another_work_tree_or_not_empty_is_refused`, `test_no_case_is_skipped_and_nothing_names_the_workbench_or_the_dev_tiers`, `test_the_suite_imports_no_network_module`, the tripwire |
