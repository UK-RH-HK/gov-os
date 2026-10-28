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
   - every ticket named is a ticket of the project and is not closed;
   - HEAD's code fingerprint can be computed. Otherwise the batch refuses with `FINGERPRINT_UNKNOWN`, and the caller closes the tickets one by one, each on a fresh run.

   The batch's head H and its code fingerprint F are fixed here.
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
7. **The record** is `docs/close/nightly/NR-<stamp>-<H12>.json`: the nightly's record plus `kind: batch`, `tickets`, `code_fingerprint`, `records_fingerprint`, `skip_count`, `skips`, `check_result` (path, commit, blocks) and `attribution`. The batch exits 0 on green and 3 on red, with the API-0002 envelope. The batch commits nothing: the caller commits the record before the first close. That commit is record-only, because `docs/close/nightly/*.json` is on the record-only list.

`python3 -m gov.close.batch refresh --root <project> --json` runs the incremental record load (section 5) at HEAD, between closes.

Then the caller (the orchestrator's queue) closes each ticket **one after another**:

1. `refresh`;
2. `gov close <ticket> --check-result <the batch's check.json>`;
3. commit the close's outputs.

Each close finds the batch's run by reuse (section 4) and runs only its own checks: its acceptance suite, the record-reading set, its trailers, paths, probe record and checkpoint. Each close record cites the batch's run (record, commit, fingerprint, JUnit XML) and states `scope: reused`.

## 4. Reuse: "the last fully passing run" (in `batch.py`, called from the close)

The candidates are exactly W2-66's green records; no second store is built:
- committed close records whose `evidence.scope` is `full`;
- `docs/close/nightly/*.json` records (nights and batches) whose `verdict` is `green` and whose `scope` is `full`.

A candidate is reused only if **all** of the following hold. Each failure means "not this one", and when no candidate is left the close runs fresh.

1. Its head is a full commit id of the repository, and is HEAD or an ancestor of HEAD.
2. It is a full run: `scope: full`. A scoped or reused close is never a candidate, so reuse never chains.
3. It passed, with no failure stated: `evidence.failures` is empty, or for a night both `failures` and `findings` are empty. A run whose close needed a load-sensitive re-run or an accepted red is not reused.
4. Every JUnit XML file it names exists, parses, holds at least one test case and holds no `failure` or `error`. A run cut short is never reused, whether its file is a placeholder with no case or is missing.
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
| batch `run` | the working tree's status, the ticket files, HEAD; then the reads of the rebuild, `gov check` and the nightly |
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

- The orchestrator's `close_queue.sh` and its skip guard (DEC-899 item 7) must call the batch and read the `reused` block's skip count. That is the orchestrator's tooling.
- The nightly's selection-miss rule (`nightly._scoped_closes`) reads only `scoped` closes. A red outside the record-reading set after a `reused` close is therefore not named as that close's miss. `nightly.py` is not in this ticket's paths, so this goes to a row.
- Equal fingerprints say the tree is the same, not the machine: installed packages, the interpreter and the pinned judge are all outside the tree.
- Reuse needs the reused run's JUnit XML, which lives under `.gov-runtime/` and is not committed. On another clone or after a clean-up, condition 4 fails and the close runs fresh. That is safe, but it saves nothing there.
- The bisect needs a green nightly-folder record before H. Without one, the attribution falls to the test's own ticket or to `outside`.
- The governance checks are not run again over the records committed after H (close records, ticket status, checkpoints): a reusing close states the batch's check result, made at H. The reason is the owner's own text, DEC-883 item 1 a (one `gov check` for the whole batch, on that head) and item 1 b (each ticket's own checks, which do not include `gov check`). Those records are judged by the record-reading set, which every reusing close runs; the next batch's or night's check sees them in full.

## 10. The trial (DEC-884 item 4), to be measured and added here

The trial runs on a fixture programme built from scratch in a temporary folder, or on a dev tier cloned into a temporary folder. It measures:
- the time per batch, for two and for three tickets, against the same closes run one by one;
- that reuse is correct;
- that a planted code change forces a fresh run;
- that a planted record-only commit runs the record-reading set and nothing else;
- that a red batch is attributed, with nothing closing on it.

Figures: to be added after implementation.

## 11. Settled points

The engineer returned four points from the check against the code; the lead settled each.

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
