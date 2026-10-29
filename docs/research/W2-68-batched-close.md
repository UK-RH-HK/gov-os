# W2-68: batched closes, reuse on the same code, and two fingerprints

- **Ticket:** DAEO-2gc7 (W2-68), profile FULL.
- **Sources:** DEC-883 items 1 to 4; DEC-889 items 2 (2 b: a failing test is re-run alone before any bisect) and 4; DEC-890; DEC-880 (the path map is shared core); DEC-884 item 4 (the trial); DEC-899; DEC-936 item 2. The card is in `docs/plan/WAVE_2_WBS.md` §2 (W2-68) and the ticket file is `.tickets/DAEO-2gc7.md`. The design builds on W2-66's `gov.close.select`, `gov.close.evidence`, `gov.close.nightly` and `governance/project/test-map.yaml`.
- **Status:** design, before implementation. It is the lead's design, checked by the engineer against the code on `w2/integrate` at `966b9f6b`. Section 12 lists what was corrected. Section 11 lists the points the engineer returned, each settled by the lead with its answer and why.
- **Readers:** the test designer and the reviewer, before any code is written.

## 0. What exists (W2-66, as it stands on w2/integrate)

- **The base.** `gov.close.select.plan` picks a close's regression run against a base: the newest commit that a green record names and that is HEAD or an ancestor of it. `select._green_heads` reads two kinds of green record from the working tree, which the close has already checked is HEAD:
  - (a) close records `docs/close/*/CL-*.md` whose `evidence.scope` is `full`;
  - (b) `docs/close/nightly/*.json` records whose `verdict` is `green`.
- **The evidence block.** `gov.close.evidence.block` states the scope, base, head, tree, changed paths, targets, left-out suites, skips (`skips`, `skip_count`) and failures. It also names each run's JUnit XML file, under `.gov-runtime/close/<ticket>/<stamp>/`. That folder is untracked, so the files exist only on the machine that ran the close.
- **The nightly.** `gov.close.nightly.night` runs the full regression on a commit in the close's form, in a detached worktree, with JUnit XML under `.gov-runtime/nightly/<stamp>-<head12>/`. It re-runs each failing test alone:
  - a red that passes alone is a flaky candidate and is not bisected;
  - a red that fails alone is bisected with `git bisect run` from the last green nightly-folder record to the head, when there is such a record.

  It writes `docs/close/nightly/NR-<stamp>-<head12>.json`. Its verdict is red when any test failed in the run, flaky candidates included.
- **The close.** `gov.close.command.run` runs these steps in order:
  1. the commit gates;
  2. the pre-close gate: collection, `gov check` at HEAD (`_check_governance_blocks` with `every`), the checkpoint;
  3. the acceptance run;
  4. the regression run, by W2-66's selection;
  5. the reds, judged by the ratchet lists;
  6. the context;
  7. the record.

  `--check-result <file>` copies a `gov check --json` output into the close's folder and gives it to every test run as `GOV_CLOSE_CHECK_RESULT`. It does not replace the pre-close gate's own `gov check`.
- **The store check.** `gov.close.repo.store_is_of_head` answers whether the record store holds HEAD and as many commits as HEAD's history. It answers None when there is no store, and raises `STORE_UNREADABLE`. On a false answer, `command._check_store` refuses with `STORE_STALE` (exit 1, nothing counted).
- **The orchestrator's queue.** `close_queue.sh`, outside the repository, runs these steps for each ticket: the checkpoint commit, a full rebuild (about 6 min), collection, the record suites, `gov check` (about 7 min), `gov close`, the skip guard and the outputs commit. The ticket measured it on 2026-10-27 at about 12 minutes per ticket before the close itself.

No second store of runs is built. Reuse and the batch read and write only (a) and (b) above.

## 1. The two fingerprints (new module `src/gov/close/fingerprint.py`)

- **Read, never written:** the test map's `record_only` list, as the commit being fingerprinted holds it (`git show <commit>:governance/project/test-map.yaml`). The list is judged by the same steps as `select.load_map`: YAML that parses to a mapping, then validation against the test-map schema (Draft 2020-12). The schema is the commit's own `template/governance/kernel/schemas/test-map.schema.json`, then its `governance/kernel/schemas/test-map.schema.json`, else the running package's own; a map that none of them validates is "cannot be computed" (section 11, point B). Patterns are read with the `allowed_paths` grammar (`select.match`).
- **The code fingerprint of a commit** is `sha256:` followed by the sha256 of the sorted lines of `git ls-tree -r -z --full-tree <commit>`. Each line has the form `<mode> <type> <object>`, a tab, then the path. Every path that the commit's `record_only` list matches is left out. Submodule entries are kept. Nothing is read from the working tree.
- **The records fingerprint of a commit** is computed the same way over exactly the left-out (record-only) entries.
- **The path map and the test map are always code** (DEC-880, DEC-899). `governance/project/path-map.yaml`, `governance/project/test-map.yaml` and the test-map schema stay in the code fingerprint even if a `record_only` pattern matches them. A change to the path map, or to the record-only list itself, therefore changes the code fingerprint and forces a fresh run.
- **"Cannot be computed"** covers a commit with no test map, a map that does not parse or fails its schema, no schema to judge it, and a commit git cannot read. The answer is then "none", never an empty list. Every caller reads "none" as "fresh": no reuse, no incremental store load, no fingerprint equality.
- **One reader for git.** The module asks git through `gov.close.repo.git`, so the store and the close compute the same value. That reader strips the caller's `GIT_` variables and ignores replacement refs.

## 2. Where each fingerprint is recorded

| Where | What | Written by |
|---|---|---|
| the record store (`.gov-runtime/store.db`), a one-row table `fingerprints` | the head loaded, its code fingerprint, its records fingerprint, the kind of load (`rebuild` or `records`) | `gov.store.load` (every `gov rebuild` calls it first) and the incremental record load |
| every close record's `evidence` | `code_fingerprint` and `records_fingerprint` of the head closed (or null) | the close (`command.py`'s record lines) |
| a batch's run record (`docs/close/nightly/NR-*.json`, `kind: batch`) | `code_fingerprint` and `records_fingerprint` of the batch's head | the batch |

The `fingerprints` row is kept out of the store's digest and out of the graph's tables (section 5; section 11, point C).

## 3. The batch (new module `src/gov/close/batch.py`; `python3 -m gov.close.batch`, no new `gov` command)

`python3 -m gov.close.batch run <ticket> [<ticket> ...] --root <project> --json` runs these steps:

1. **Read and refuse (exit 1, nothing run).** The batch refuses unless all of these hold:
   - the working tree is HEAD (`repo.tree_differences`, as the close reads it);
   - every ticket named is a ticket of the project and is not closed.

   The batch's head H and its code fingerprint F are fixed here. Where HEAD's fingerprints cannot be computed (no test map, an invalid one), the batch still runs steps 2 to 7, its record stating the fingerprints as null, and each close of step 9 then runs fresh (section 11, point E).
2. **One full rebuild** at H, with `gov rebuild`'s own code and never `--no-embeddings`. The store records H, F and the records fingerprint.
3. **One `gov check`** at H (`gov.check.runner.run_checks`). Its result is written to `.gov-runtime/close/batch/<stamp>/check.json`. A blocking result ends the batch red (exit 3): no regression runs and nothing closes.
4. **One full regression** at H in the close's form. This is `nightly.night` on H: a detached worktree, one parallel run, then the serial-only cases, the per-test limit, retention `failed` and JUnit XML.
5. **A red run** (DEC-883 item 2, DEC-889 item 2 b). Every failing test is first run again alone, which is the nightly's own step.
   - A red that passes alone is a flaky candidate: it is named and never bisected.
   - A red that fails alone is attributed in this order:
     - by `git bisect run` over the batch's range (from the last green run to H) to its first bad commit, and then to the ticket that commit's `Task:` trailer names;
     - else to the failing test's own ticket, the ticket whose acceptance folder holds the test;
     - else `outside`, which is the orchestrator's to fix and record.
   - Each attribution keeps its evidence: the test, its failure text, its run alone, and either the bisect range and first bad commit or the folder.
   - The run's verdict is red if any test failed in it, flaky candidates included. **Nothing closes on a red run.**
6. **No code merge during a batch.** At the end the batch reads HEAD again. If HEAD's code fingerprint is not F, the batch ends with `BATCH_CODE_CHANGED` (exit 1). Its run is still valid for H, but it serves no close at another code.
7. **The record** is `docs/close/nightly/NR-<stamp>-<H12>.json`: the nightly's record plus `kind: batch`, `tickets`, `code_fingerprint`, `records_fingerprint`, `skip_count`, `skips`, `check_result` (path, commit, blocks) and `attribution`.
8. **The batch commits the run record** (a record-only path, since `docs/close/nightly/*.json` is on the record-only list) in a commit that names no task: trailers `Role: <the caller's GOV_ROLE, else orchestrator>`, `Implements: DEC-883`, and a `Co-Authored-By` only where the caller's environment gives one. A red run's record is committed too, and the batch ends there (exit 3): **nothing closes on a red run.**
9. **The batch closes each ticket, one after another, in the order given** (section 11, point E):
   - before each close, it makes the store fresh at HEAD: the incremental record load (section 5) where the store's code fingerprint equals HEAD's; else (a fingerprint that cannot be computed) a full rebuild at HEAD;
   - it runs `gov close <ticket>` in-process (the close's own code path, with `--check-result` set to the batch's `check.json`), which finds the batch's run by reuse (section 4) and runs only its own checks: its acceptance suite, the record-reading set, its trailers, paths, probe record and checkpoint;
   - it commits the close's outputs as the orchestrator's queue does today (the ticket file, `docs/close/<ticket>/`, `docs/checkpoints/<ticket>/`; trailers `Task: <ticket>`, `Implements: DEC-883`, `Role: <as in step 8>`), so the next close finds a clean tree;
   - **a refused close ends the batch** (the owner's queue rule of 2026-10-27: a refusal ends the queue with a non-zero status). The closes before it stand, the tickets after it are not closed, the envelope names the refusal (its code and its findings), exit 3. What the refused close left (its repair ticket) is left in the tree, uncommitted.

   Each close record cites the batch's run (record, commit, fingerprint, JUnit XML) and states `scope: reused`. Where HEAD's fingerprints cannot be computed, each close runs fresh: no reuse, its own `gov check`, a full rebuild before it.
10. **The envelope** (API-0002) gives the run record, each ticket's close (its record path, or its refusal) and the store loads made. The batch exits 0 when the run is green and every ticket closed, 3 on a red run or a refused close, 1 on a refusal of step 1 or step 6.

`python3 -m gov.close.batch refresh --root <project> --json` runs the incremental record load (section 5) at HEAD on its own. It exits 0 when the store is fresh at HEAD after the load, and 1 with the error's code otherwise.

## 4. Reuse: "the last fully passing run" (in `batch.py`, called from the close)

The candidates are exactly W2-66's green records; no second store is built:
- committed close records whose `evidence.scope` is `full`;
- `docs/close/nightly/*.json` records (nights and batches) whose `verdict` is `green` and whose `scope` is `full`.

A candidate is reused only if **all** of the following hold. Each failure means "not this one", and when no candidate is left the close runs fresh.

1. Its head is a full commit id of the repository, and is HEAD or an ancestor of HEAD.
2. It is a full run: `scope: full`. A scoped or reused close is never a candidate, so reuse never chains.
3. It passed, with no failure stated: `evidence.failures` is empty, or for a night both `failures` and `findings` are empty. A run whose close needed a load-sensitive re-run or an accepted red is not reused.
4. It names at least one JUnit XML file, and every JUnit XML file it names exists, parses, holds at least one test case and holds no `failure` or `error`. A run cut short is never reused, whether its file is a placeholder with no case or is missing. A record that names none (an empty `junit_xml`, as W2-66's planted green nights) is never reused.
5. The skip count read from its JUnit XML equals the count the record states: a close's or a batch's `skip_count`, or a night's `tests_run.skipped`. A record that states neither is not reused (section 11, point D).
6. The code fingerprint of its head, computed now, equals HEAD's, and also equals the fingerprint the record states, where it states one. If HEAD's code fingerprint cannot be computed, nothing is reused.
7. The close was not asked `--full`, and W2-66's plan gives no `TEST_MAP_*` or `UNRESOLVED_TARGET` reason.

**Running the reusing close:**
- Of the candidates left, the newest by ancestry (`select.newest`) is reused.
- The regression run is the record-reading set alone (`record_reading` of HEAD's test map), in the full run's form (`pytest tests` with `--ignore` and `--deselect`). The acceptance run is unchanged.
- The evidence states:
  - `scope: reused`;
  - the `reused` block: `record`, `head`, `code_fingerprint`, `junit_xml`, `skip_count`, `skips` and `tests_run`;
  - the skips of the close's own runs.

  **A reused run's skips are stated, never inherited unseen.**
- The reused run's regression also leaves out `tests/unit` and every other folder under `tests/` that is not a record-reading target, each by `--ignore`. W2-66's `select._form` leaves out only acceptance suites, which its scoped plan never needed to widen, because that plan always selects `tests/unit`.

**The governance check of a reusing close.** The close states the reused record's check result (`governance_checks_reused`: record, commit, code fingerprint) in place of running `gov check` again, when all of these hold:
- the reused record names a check result (a batch does);
- the file exists;
- every check in it was run at the record's head;
- it does not block.

Otherwise the close runs its own check, as today. Today the pre-close gate runs `gov check` before `_scope` asks for the selection, so the reuse decision has to be taken before the pre-close gate. That is a change to the order of the calls in `command.py`. The records committed after H are judged by the record-reading set, which every reusing close runs (section 11, point A).

## 5. The store (`src/gov/store/**`, `src/gov/close/repo.py`)

- **The fingerprints row.** `gov.store.load` records the row: head, code, records, kind `rebuild`.
- **The row and the store's digest.** The row is kept out of the store's digest (`_digest`) and out of the graph's tables (`_TABLES`), so the recovery-rebuild check (CAP-38.b, `gov.rebuild.check`) is unchanged. An incremental record load of a commit must leave the same store digest as a full load of that commit.
- **The incremental record load** (in `gov.store`, called by `batch refresh`):
  - It runs only when the store's row holds a code fingerprint equal to HEAD's. Otherwise it refuses with `STORE_CODE_CHANGED` (exit 1): a full rebuild is needed.
  - It reloads the record graph from HEAD: records, edges, commits, trailers, commit paths and register entries. This takes seconds.
  - It refreshes the lexical index by calling `gov.retrieval.lexical.refresh` as it stands. That function is already incremental by blob, so only the changed record files are chunked.
  - It refreshes the semantic vectors of the changed chunks by calling `gov.retrieval.semantic.refresh` as it stands, which embeds only the chunk ids it lacks. Where Ollama cannot be reached, the vectors stay stale and the semantic facet reports it through its own status. The close does not read the vectors.
  - It leaves the code index as it is.
  - It writes the row: HEAD, the same code fingerprint, the new records fingerprint, kind `records`.

  No file under `src/gov/retrieval/` changes.
- **The store-freshness check** (`repo.store_is_of_head`) keeps today's rule: the store holds HEAD and as many commits as HEAD's history. Where the store has a fingerprints row, it also requires:
  - the row's head is HEAD;
  - the row's code fingerprint equals HEAD's;
  - the row's records fingerprint equals HEAD's.

  Where HEAD's fingerprints cannot be computed, the row must be a `rebuild` of HEAD itself. A store without a row (built before W2-68) is judged by today's rule alone. The refusal stays `command._check_store`'s `STORE_STALE`.
- **The lexical index** is never fresh while record files have changed. Its own check, `gov.retrieval.lexical.freshness`, already compares the blob of every tracked file as the working tree holds it. The store row's records fingerprint gives the close the same answer from HEAD.
- **W1-30's case.** `test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later` still holds under this design: after one more commit, the row's head is no longer HEAD, so the store is stale whether that commit is code or records. The test designer re-reads the case against the two fingerprints (Rewrite-Reason).

## 6. What each step reads

| Step | Reads |
|---|---|
| fingerprints | the git objects of one commit (`ls-tree`, `show` of the test map), the test-map schema |
| batch `run` | the working tree's status, the ticket files, HEAD; then the reads of the rebuild, `gov check` and the nightly; then, for each close, the reads of the store load before it and of `gov close` itself, and the status of the close's outputs it commits |
| reuse | the committed close records' frontmatter and the nightly folder's JSON (as `select._green_heads` reads them), the JUnit XML files they name, git ancestry, the fingerprints |
| batch `refresh` | the store's fingerprints row, HEAD's tree and log, the tracked files' blobs |
| store check | the store's `commits` table and fingerprints row, HEAD's fingerprints |

## 7. Failure KPIs and where each is refused

| Failure | Refused by |
|---|---|
| a close citing a red run, or the run of another fingerprint | reuse conditions 3, 4 and 6 |
| a reused run on different code | condition 6 (computed now, not only read from the record) |
| a store accepted on another code fingerprint | the store check; the incremental load also refuses a code change |
| a lexical index fresh while records changed | the lexical check and the store row's records fingerprint |
| a code merge during a batch | step 6; every close also compares fingerprints itself |
| a red that passes alone being bisected | step 5 (the nightly's alone-first rule) |
| reused evidence hiding a skip | the `reused` block's `skip_count` and `skips`; condition 5 |

## 8. Allowed paths, as the ticket limits them

- new: `src/gov/close/batch.py`, `src/gov/close/fingerprint.py`;
- `src/gov/close/command.py`: the calls (reuse, the reused check and their order before the pre-close gate) and the record's lines (`code_fingerprint`, `records_fingerprint`, `reused`, `governance_checks_reused`), added to the block `evidence.block` returns, only;
- `src/gov/close/repo.py`: the store-freshness check only;
- `src/gov/store/**`: the fingerprints a rebuild records and the incremental record load only;
- builder tests: `tests/unit/close/test_batch*`, `tests/unit/close/test_fingerprint*`, `tests/unit/store/test_fingerprint*`.

The design needs no change to `select.py`, `evidence.py`, `nightly.py`, `src/gov/retrieval/` or the test map. `batch.py` calls their functions as they stand and rewrites the nightly's record with the batch's keys.

## 9. Known limits (residuals, not this ticket)

- The orchestrator's `close_queue.sh` must call the batch, and keeps its own gates around it: the keyword warning, the collection, the network check, the gitleaks scan of the staged outputs, and the skip guard (DEC-899 item 7) reading the `reused` block's skip count. That is the orchestrator's tooling. The batch does not run gitleaks on what it commits (the run record of step 8, each close's outputs of step 9).
- The nightly's selection-miss rule (`nightly._scoped_closes`) reads only `scoped` closes. A red outside the record-reading set after a `reused` close is therefore not named as that close's miss. `nightly.py` is not in this ticket's paths, so this goes to a row.
- Equal fingerprints say the tree is the same, not the machine: installed packages, the interpreter and the pinned judge are all outside the tree.
- Reuse needs the reused run's JUnit XML, which lives under `.gov-runtime/` and is not committed. On another clone or after a clean-up, condition 4 fails and the close runs fresh. That is safe, but it saves nothing there.
- The bisect needs a green nightly-folder record before H. Without one, the attribution falls to the test's own ticket or to `outside`.
- A red *night* on the same code does not hold closes: the wait of section 11, point F, reads batch runs only. A red night goes on through the nightly's own P1 packages (bisect and selection miss) as it does today; extending the hold to nights is the orchestrator's to propose.
- The governance checks are not run again over the records committed after H (close records, ticket status, checkpoints): a reusing close states the batch's check result, made at H. The reason is the owner's own text, DEC-883 item 1 a (one `gov check` for the whole batch, on that head) and item 1 b (each ticket's own checks, which do not include `gov check`). Those records are judged by the record-reading set, which every reusing close runs; the next batch's or night's check sees them in full.

## 10. The trial (DEC-884 item 4)

Measured on 2026-10-29, 03:34 to 03:48 UTC, after the nightly had ended, with the 1-minute load below 20 at the start of each run. The code was this branch at `6563856f` (`PYTHONPATH` set to the worktree's `src/`).

**The fixture programme.** Each scenario built a fresh git repository from scratch under the session's temporary folder, and removed it when the scenario ended. The commit dates are fixed, so every scenario starts from the same commits. The repository holds:
- a Python package `src/app/` (`core.py`, plus one module for each ticket);
- `tests/unit/test_core.py` (3 tests);
- four open STANDARD tickets, `PROJ-aaaa` to `PROJ-dddd` (W9-aa to W9-dd). Each has its ticket file (orchestrator), an acceptance suite of 3 tests (test designer) and one work commit inside its `allowed_paths` (engineer). There is also one closed ticket, `PROJ-rrrr`, whose `tests/acceptance/W9-rr/test_records.py` (2 tests, reading the register) is the record-reading set;
- the test map: `shared_core` holds `src/app/core.py`, the path map and the test map; `record_only` holds `.tickets/**`, `docs/checkpoints/**`, `docs/close/**`, `docs/probes/**`, the register and `docs/notes/**`; `record_reading` holds the W9-rr file;
- the path map: four namespaces with their memory keys (records `embedded`), and `close_workers: 2`;
- W1-07's minimal `.gitleaks.toml`;
- ten of the kernel's check declarations, written as text: core-graph, core-pathmap, core-authority, core-claims, core-mutation, core-decision-citations, index-freshness, recovery-rebuild, secrets-indexing and product-traceability-trailers. core-schema was left out because the fixture carries no copy of the kernel's schemas;
- the decisions `DEC-000` and `DEC-883` (the batch's commits cite `DEC-883`);
- a green base: a planted green night record on the initial head, naming no JUnit XML.

In the full run, the regression is 17 tests.

**The commands.** Every command ran with `GOV_ROLE=orchestrator`, from the programme's root.
- The queue, one by one: `gov checkpoint --ticket <t> --role orchestrator --trigger ticket-transition` (committed), `gov rebuild --json`, `python3 -m pytest tests --collect-only -q`, `gov check --json`, `gov close <t> --check-result <check.json> --json`, then the outputs committed.
- The batch: `gov checkpoint` for each ticket (committed), then `python3 -m gov.close.batch run <t> ... --root <programme> --json`. It ran through a wrapper that times the batch's own functions in-process (`_rebuild`, `_check`, `nightly.night`, `_fresh`, `_close`, `_commit`) and then calls `batch.main`.
- After a batch: `python3 -m gov.close.batch refresh --root <programme> --json` and a plain `gov close <t> --json`.

The trial's script and logs were kept in the session's own scratch folder, because the guard refused writes to the worktree's `.gov-runtime/scratch/` for this session.

**Times (wall-clock seconds; load is the 1-minute load before → after).**

| Run | Step | Seconds | Load |
|---|---|---|---|
| queue, `PROJ-aaaa` | checkpoint 0.1, rebuild 8.9, collection 0.2, check 1.6, close 59.7 | 70.5 | 9.8 → 14.2 |
| queue, `PROJ-bbbb` | checkpoint 0.1, rebuild 9.5, collection 0.2, check 1.0, close 60.9 | 71.7 | 14.2 → 12.1 |
| queue, `PROJ-cccc` | checkpoint 0.1, rebuild 11.1, collection 0.2, check 1.2, close 55.3 | 67.9 | 12.1 → 15.1 |
| **queue, 2 tickets** | | **142.2** | |
| **queue, 3 tickets** | | **210.1** | |
| batch of 2 | checkpoints 0.1; rebuild 7.5, check 1.4, regression 1.0, record commit 0.0; store load 1.1, close `aaaa` 52.5; store load 4.1, close `bbbb` 71.7; commits 0.0 | **140.0** (command 139.9) | 15.1 → 23.1 |
| batch of 3 | checkpoints 0.3; rebuild 8.0, check 1.5, regression 1.0; store loads 1.1, 3.8 and 4.2; closes 44.6, 41.9 and 42.1 | **149.1** (command 148.8) | 17.0 → 11.4 |
| red batch of 3 | rebuild 8.0, check 1.5, regression with its re-runs alone and its bisect 2.4; nothing closed | 11.9 | 10.7 → 12.2 |

**What the times say.**
- On this fixture, the steps a batch shares are small: a rebuild of 8 to 11 s, a check of 1 to 2 s and a regression of about 1 s. Each close's own fixed cost dominates, at 42 to 72 s. Of that, its test runs take under 2 s; its standard error shows a model's weights being loaded, and the cost was not broken down further.
- So the batch of two (140 s) is no faster than the queue (142 s). The batch of three is 29 % faster (149 s against 210 s), because two rebuilds, two checks and two broad regressions are not run.
- On the programme itself, the shared steps are the expensive ones: a rebuild of about 6 minutes, `gov check` of about 7 minutes, and a full regression. The saving then grows with each ticket by about one rebuild plus one check plus the difference between a scoped regression and the record-reading set. That is an extrapolation, not a measurement.
- The close of `PROJ-bbbb` in the batch of two (71.7 s) ran while the load rose to 23. That figure is load-sensitive.
- **Caveat:** a sandboxed session embeds on a CPU Ollama of its own, started by `gov` in the sandbox, so the rebuild times are not the shared GPU's. The code index was not recreated in the sandbox (`codeintel: not_recreated`, a read-only `/tmp/gov-cbm-1000`), so the rebuilds above exclude it.

**1. Reuse correct (batch of 2, then `PROJ-cccc`).**
- Each close in the batch, and the later plain `gov close PROJ-cccc` (after its checkpoint, a record-only commit, and `batch refresh`, 5.1 s), states `scope: reused`.
- Its `reused` block names `docs/close/nightly/NR-20261029T033809Z-969143eb5abc.json`, head `969143eb5abc`, `code_fingerprint` `sha256:b0505e53…`, the run's JUnit XML file, `skip_count: 0`, `skips: []` and `tests_run` (17 passed, 0 skipped).
- `governance_checks_reused` names the same record and commit and the batch's `check.json`.
- Its runs were its acceptance suite (the 3 W9-cc tests) and, as the regression, the record-reading set alone (`selected: [tests/acceptance/W9-rr/test_records.py]`, the 2 W9-rr tests): 5 passed, 0 skipped.
- The batch's record states `kind: batch`, `verdict: green`, `scope: full`, both fingerprints, `skip_count: 0` and the check result (`blocks: false`). Its store loads were one `rebuild` before the run and one `records` load before each close.

**2. A planted code change forces a fresh run (then `PROJ-dddd`).**
- `PROJ-dddd`'s engineer changed `src/app/delta.py` after the batch, then made its checkpoint.
- `batch refresh` refused with `STORE_CODE_CHANGED` (exit 1, 0.1 s). A `gov rebuild` (7.4 s) followed, then `gov close PROJ-dddd` (47.5 s).
- That close states `scope: scoped`, a new `code_fingerprint` (`sha256:cf10ffea…`), no `reused` block and no `governance_checks_reused`; it ran its own `gov check`.
- Its regression was W2-66's scoped selection: W9-dd, `tests/unit` and the record-reading set, 8 passed.
- It cites no earlier run. Its `base` is the batch's head, which is W2-66's selection base: the newest green record.

**3. A planted record-only commit runs the record-reading set and nothing else (batch of 3, then `PROJ-dddd`).**
- After the batch, a record-only commit (`docs/notes/trial.md` and a register line), the checkpoint, and `batch refresh` (5.2 s), then `gov close PROJ-dddd` (45.5 s).
- That close states `scope: reused`, citing the batch's record at `dec233d78698`. Its code fingerprint equals the batch's (`sha256:b0505e53…`).
- Its runs were the W9-dd acceptance suite (3 tests) and, of the regression, the 2 W9-rr record-reading tests only.

**4. A red batch (3 tickets; `PROJ-bbbb`'s work sets `beta.VALUE = 2`, which `tests/unit/test_core.py::test_beta_value` reads; a planted `tests/unit/test_flaky.py` fails on its first run only).**
- The batch ended `BATCH_RED`, exit 3: "2 failing tests, 2 findings; nothing closes on a red run".
- The record's verdict is `red`.
- `test_fails_once` was run again alone and passed, so it is a `flaky_candidate`, with no bisect package.
- `test_beta_value` was run again alone and failed, so it is `red`. One P1 `bisect` package spans `b4e509c1…231ec094` (from the green base to H), with `first_bad` `88299c83`, `PROJ-bbbb`'s work commit. The attribution names `ticket: PROJ-bbbb`, `by: bisect`, with the failure text, the run alone and the range.
- No close ran (`closes: []`). All three tickets are still `in_progress` and none has a close record.
- In a second run of the same scenario (03:47 UTC, load 6.9), after `batch refresh`, a plain `gov close PROJ-aaaa` (a ticket the red is not attributed to) refused `RED_RUN_ON_CODE` (exit 1, not counted), naming the red record and its head (point F). In the first run, the same close without the record load refused `STORE_STALE`, because the red record's commit had moved HEAD.

No defect was found in the code; no code changed in this batch.

## 11. Settled points

The engineer returned four points from the check against the code (A to D); the lead settled each, and added point E after the acceptance tests were written.

- **A. The batch's `gov check` serves closes whose records differ from H.**
  - *The point:* after the first close, HEAD is H plus record-only commits (close records, ticket status, checkpoints). `gov check`'s declared checks read records, and `_check_governance` today stands only on a result of the commit being closed.
  - *Answer:* one check per batch. A reusing close states the batch's check result in place of its own, under the conditions of section 4. The record-only commits after H are judged by the record-reading set, which every reusing close runs. The gap is named in section 9 as a residual.
  - *Why:* the owner's own text settles it. DEC-883 item 1 a: "one rebuild, one `gov check` and one full regression for the whole batch, on that head"; item 1 b: each ticket's own checks are its acceptance suite, the record-reading tests, trailers, paths, probe record and checkpoint.
- **B. Which schema judges a past commit's test map.**
  - *The point:* `select._schema` reads the working tree's kernel schema, else the running package's; a fingerprint of a commit that is not HEAD needs one answer.
  - *Answer:* the commit's own `template/governance/kernel/schemas/test-map.schema.json`, then its `governance/kernel/schemas/test-map.schema.json`, else the running package's own. A map that none of them validates is "cannot be computed".
  - *Why:* the fingerprint is then a function of the commit and the judge alone, never of the working tree.
- **C. The `fingerprints` row and the store's digest.**
  - *The point:* the recovery-rebuild check (CAP-38.b, `gov.rebuild.check`) compares the store's digest with a clean load of HEAD. A row that counted toward `_digest`, its kind in particular, would turn that check red after every `refresh`.
  - *Answer:* the row is kept out of the store's digest and out of the graph's tables, and an incremental record load of a commit must leave the same store digest as a full load of that commit (both stated in section 5).
  - *Why:* the recovery-rebuild check stays unchanged, and an incremental load is checkable against a full one.
- **D. A night's stated skip count.**
  - *The point:* a night's record states no `skip_count` or `skips`, only `tests_run.skipped`.
  - *Answer:* a night's stated skip count is its `tests_run.skipped`; a batch's record states `skip_count` and `skips` itself. Condition 5 compares the count read from the JUnit XML with whichever the record states; a record that states neither is not reused.
  - *Why:* every candidate then has one stated count to check, and a record with none cannot show that it hides no skip.
- **E. The batch drives the whole batch, its closes included** (the lead's amendment).
  - *The point:* the acceptance tests read DEC-883 item 1 ("queued closes on one integrated head ... then each ticket's own checks, one after another") as one command that closes the tickets; the draft left the closes to the caller.
  - *Answer:* `python3 -m gov.close.batch run` does, after steps 1 to 7 of section 3, step 8 (it commits the run record, in a commit that names no task; a red run's record is committed too and the batch ends there, exit 3), step 9 (it closes each ticket one after another in the order given: the store made fresh at HEAD before each close, by the incremental record load where the code fingerprint equals HEAD's, else a full rebuild; `gov close` in-process with the batch's check result; the close's outputs committed as the orchestrator's queue does today; a refused close ends the batch, exit 3, the closes before it standing, its repair ticket left uncommitted) and step 10 (the envelope: the run record, each close, the store loads). A fingerprint that cannot be computed no longer refuses the batch (`FINGERPRINT_UNKNOWN` is gone): the batch runs, its record states the fingerprints as null, and each close runs fresh. A record that names no JUnit XML file is never reused (condition 4). The queue keeps its own gates around a batch, and the batch runs no gitleaks scan on what it commits (section 9).
  - *Why:* that is the better reading of a merge queue: one command takes the queued tickets from one head to closed, or stops at the first refusal as the owner's queue rule of 2026-10-27 does.
- **F. A close on the code of a red batch waits for a green run** (the lead's answer to the engineer's package P-W2-68-RED-WAIT).
  - *The point:* after a red batch, a plain `gov close` of a ticket the red is not attributed to could not reuse the red run (condition 3), ran fresh, and closed on the code the batch had just found red. Section 4 refused only the citing of a red run; nothing held the close itself.
  - *Answer:* a close on HEAD refuses before the pre-close gate, not counted (a `GovError`, exit 1, code `RED_RUN_ON_CODE`, its details naming the red run's record and head, no evidence block), when the newest batch run on HEAD's code is red and no green full run on that code is newer. The batch runs are the nightly folder's records of `kind: batch` whose head is HEAD or an ancestor of it and whose stated code fingerprint equals HEAD's, computed now; the newest is the deepest by ancestry, ties by the record's name. A green full run (a night or a batch) is on that code where the fingerprint it states, else its head's computed now, equals HEAD's. Where HEAD's code fingerprint cannot be computed, no batch record can be on its code, and the rule asks nothing. The logic is `batch.check_red_run`; `command.py` calls it with the other "could not measure" checks, after the store check. The causing ticket is repaired (a code change, so a new fingerprint) and the batch re-runs; on a green run on the same code the hold lifts.
  - *Why:* the ticket's own KPI line, DEC-883 item 2 c: "nothing closes on a red run; the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run". The rule is limited to batches; a red night is the residual of section 9.

## 12. Corrections to the lead's draft

- **Section 0, the nightly's bisect.** The range starts at the newest green record of the nightly folder (`nightly._last_green`). Full close records are not read for it. When there is no such record, nothing is bisected (`range` and `first_bad` are null). `git bisect run` walks every commit in the range, not only the merges, so the first bad commit can be a ticket's own commit.
- **Section 0, `--check-result`.** It gives the copied result to the close's test runs as `GOV_CLOSE_CHECK_RESULT`. It does not skip the pre-close gate's `gov check`. The reused check of section 4 is a new call.
- **Section 0, `STORE_STALE`.** `repo.store_is_of_head` answers true, false or None (no store), and raises only `STORE_UNREADABLE`. `STORE_STALE` is raised by `command._check_store`.
- **Section 1, the map's reading.** `select.load_map` reads the working tree's file, so it cannot be called on a commit's blob. The fingerprint repeats its steps on the blob (point B).
- **Section 4, the reused form.** `select._form` ignores only acceptance suites. The reused run must also ignore `tests/unit` and the other folders under `tests/` (added in section 4).
- **Section 4, ordering.** The pre-close gate's `gov check` runs before the selection today. Reuse has to be decided first (added in section 4).
- **Section 5, the record graph.** The loader's tables also include `commit_paths`, which the incremental load reloads too.
- **Section 5, the lexical and semantic refresh.** These are the existing `lexical.refresh` and `semantic.refresh`, already incremental: by blob for the lexical index, by missing chunk id for the vectors. The lexical index reads the working tree (DEC-344), not HEAD. That is the same thing only because the close and the batch first require the tree to be HEAD.
- **Section 4, condition 5.** Nights state no `skip_count`; see point D.
