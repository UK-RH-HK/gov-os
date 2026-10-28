# W2-68 design draft (the lead's; the worker writes it into docs/research/W2-68-batched-close.md)

Ticket DAEO-2gc7 (W2-68): batched closes, reuse on the same code, and two fingerprints.
Sources: DEC-883 (items 1 to 4), DEC-889 items 2 and 4 (2 b: re-run alone before any bisect), DEC-890, DEC-880
(the path map is shared core), DEC-884 item 4 (the trial), DEC-899, DEC-936. Builds on W2-66 (`gov.close.select`,
`gov.close.evidence`, `gov.close.nightly`, `governance/project/test-map.yaml`).

## 0. What exists (W2-66, read as it stands on w2/integrate)

- `gov.close.select.plan` picks a close's regression run against a base: the newest commit that a green record
  names and that is HEAD or an ancestor of it. Green records are (a) committed close records
  `docs/close/*/CL-*.md` whose `evidence.scope` is `full`, (b) `docs/close/nightly/*.json` with
  `verdict: green` (`select._green_heads`).
- `gov.close.evidence.block` states the scope, base, head, tree, changed paths, targets, left-out suites, skips
  (`skips`, `skip_count`), failures and the JUnit XML paths (under `.gov-runtime/close/<ticket>/<stamp>/`).
- `gov.close.nightly.night` runs the full regression on a commit in a detached worktree, in the close's form, with
  JUnit XML; re-runs each failing test alone; a red that passes alone is a flaky candidate and is not bisected; a red
  that fails alone is bisected (`git bisect run`) from the last green night; writes
  `docs/close/nightly/NR-<stamp>-<head12>.json`.
- The close (`gov.close.command.run`): commit gates; pre-close gate (collection, `gov check` at HEAD, checkpoint);
  acceptance run; regression run (W2-66's selection); reds by the ratchet lists; context; record.
- The store check (`gov.close.repo.store_is_of_head`): the record store holds HEAD and as many commits as HEAD's
  history; else `STORE_STALE` (exit 1, nothing counted).
- The orchestrator's queue (`close_queue.sh`, outside the repository) runs per ticket: checkpoint commit, full
  rebuild (~6 min), collection, the record suites, `gov check` (~7 min), `gov close`, the skip guard, the outputs
  commit. Measured 2026-10-27: about 12 minutes per ticket before the close itself.

No second store of runs is built: reuse and the batch read and write only (a) and (b) above.

## 1. The two fingerprints (new module `src/gov/close/fingerprint.py`)

- **Read, never written:** the test map's `record_only` list, as the commit being fingerprinted holds it
  (`git show <commit>:governance/project/test-map.yaml`), validated against the test-map schema exactly as
  `select.load_map` validates it. Patterns are read with the `allowed_paths` grammar (`select.match`).
- **The code fingerprint of a commit:** `sha256:` + sha256 over the sorted lines `<mode> <type> <object>\t<path>`
  of `git ls-tree -r -z --full-tree <commit>`, leaving out every path the commit's `record_only` list matches.
  Submodule entries are kept. Nothing is read from the working tree.
- **The records fingerprint of a commit:** the same over exactly the left-out (record-only) entries.
- **The path map and the test map are code, always** (DEC-880, DEC-899): `governance/project/path-map.yaml`,
  `governance/project/test-map.yaml` and the test-map schema are kept in the code fingerprint even if a
  `record_only` pattern matches them. So a change to the path map, or to the record-only list itself, changes the
  code fingerprint: a fresh run.
- **Cannot be computed** (no test map at that commit, a map that does not parse or fails its schema, no schema to
  judge it, a commit git cannot read): the answer is "none", never an empty list. Every caller reads "none" as
  "fresh": no reuse, no incremental store load, no fingerprint equality.

## 2. Where each fingerprint is recorded

| Where | What | Written by |
|---|---|---|
| the record store (`.gov-runtime/store.db`), a table `fingerprints` (one row) | the head loaded, its code fingerprint, its records fingerprint, the kind of load (`rebuild` or `records`) | `gov.store.load` (every `gov rebuild` calls it first) and the incremental record load |
| every close record's `evidence` | `code_fingerprint` and `records_fingerprint` of the head closed (or null) | the close (`command.py`'s record lines) |
| a batch's run record (`docs/close/nightly/NR-*.json`, `kind: batch`) | `code_fingerprint`, `records_fingerprint` of the batch's head | the batch |

## 3. The batch (new module `src/gov/close/batch.py`; `python3 -m gov.close.batch`, no new `gov` command)

`python3 -m gov.close.batch run <ticket> [<ticket> ...] --root <project> --json`. Step by step:

1. **Read and refuse (exit 1, nothing run):** the working tree is HEAD (`repo.tree_differences`, as the close
   reads it); every ticket named is a ticket of the project and not closed; HEAD's code fingerprint can be
   computed (else `FINGERPRINT_UNKNOWN`: the caller closes the tickets one by one, each on a fresh run). The batch's
   head H and its code fingerprint F are fixed here.
2. **One full rebuild** at H (`gov rebuild`'s own code, never `--no-embeddings`); the store records H, F and the
   records fingerprint.
3. **One `gov check`** at H (`gov.check.runner.run_checks`); its result is written under
   `.gov-runtime/close/batch/<stamp>/check.json`. A blocking result ends the batch red (exit 3): no regression,
   nothing closes.
4. **One full regression** at H in the close's form (`nightly.night` on H: a detached worktree, one parallel run,
   then the serial-only cases, per-test limit, retention `failed`, JUnit XML).
5. **A red run (DEC-883 item 2, DEC-889 item 2 b):** every failing test is first run again alone (the nightly's
   own step). A red that passes alone is a flaky candidate: named, never bisected. A red that fails alone is
   attributed: by `git bisect run` over the batch's merges (from the last green run to H) to its first bad commit,
   and the ticket of that commit's `Task:` trailer; else by the failing test's own ticket (the ticket whose
   acceptance folder holds it); else `outside` (the orchestrator's to fix and record). Each attribution keeps its
   evidence (the test, its failure text, its run alone, the bisect range and first bad commit, or the folder).
   The run's verdict is red if any test failed in it, flaky candidates included: **nothing closes on a red run.**
6. **No code merge during a batch:** at the end the batch reads HEAD again; if HEAD's code fingerprint is not F,
   it ends `BATCH_CODE_CHANGED` (exit 1) and its run, though valid for H, serves no close at another code.
7. **The record:** `docs/close/nightly/NR-<stamp>-<H12>.json`, the nightly's record with `kind: batch`, `tickets`,
   `code_fingerprint`, `records_fingerprint`, `skip_count`, `skips`, `check_result` (path, commit, blocks) and
   `attribution`. Exit 0 green, 3 red; the API-0002 envelope. The batch commits nothing: the caller commits the
   record (a record-only commit) before the first close.

`python3 -m gov.close.batch refresh --root <project> --json`: the incremental record load (section 5) at HEAD,
between closes.

Then the caller (the orchestrator's queue) closes each ticket **one after another**: `refresh`, `gov close
<ticket> --check-result <the batch's check.json>`, commit the close's outputs. Each close finds the batch's run by
reuse (section 4) and runs only its own checks: its acceptance suite, the record-reading set, its trailers, paths,
probe record and checkpoint. Each close record cites the batch's run (record, commit, fingerprint, JUnit XML) and
states `scope: reused`.

## 4. Reuse: "the last fully passing run" (in `batch.py`, called from the close)

Candidates are exactly W2-66's green records (no second store): committed close records whose `evidence.scope` is
`full`, and `docs/close/nightly/*.json` records (nights and batches) whose `verdict` is `green` and `scope` `full`.
A candidate is reused only if **all** hold (each failure means "not this one"; none left means a fresh run):

1. its head is a full commit id of the repository, HEAD or an ancestor of HEAD;
2. it is a full run: `scope: full` (a scoped or reused close is never a candidate, so reuse never chains);
3. it passed: no failure stated (`evidence.failures` empty; a night's `failures` and `findings` empty) — a run
   whose close needed a load-sensitive re-run or an accepted red is not reused;
4. every JUnit XML file it names exists, parses, holds at least one test case and no `failure` or `error`; a run
   cut short (a placeholder with no case, a missing file) is never reused;
5. the skip count read from its JUnit XML equals the count it states, where it states one;
6. the code fingerprint of its head, computed now, equals HEAD's, and equals the fingerprint it states, where it
   states one; HEAD's code fingerprint cannot be computed: no reuse;
7. the close was not asked `--full`, and W2-66's plan has no `TEST_MAP_*` or `UNRESOLVED_TARGET` reason.

Of the candidates left, the newest by ancestry is reused. The reusing close's regression run is then the
record-reading set alone (`record_reading` of HEAD's test map), in the full run's form (`pytest tests` with
`--ignore` and `--deselect`), and its acceptance run as always. Its evidence states `scope: reused`, the
`reused` block (`record`, `head`, `code_fingerprint`, `junit_xml`, `skip_count`, `skips`, `tests_run`) and its own
runs' skips: **a reused run's skips are stated, never inherited unseen.**

**The governance check of a reusing close:** where the reused record names a check result (a batch's), the file
exists, every check in it was run at the record's head, and it does not block, the close states that result
(`governance_checks_reused`: record, commit, code fingerprint) in place of running `gov check` again; otherwise
the close runs its own, as today.

## 5. The store (`src/gov/store/**`, `src/gov/close/repo.py`)

- `gov.store.load` records the fingerprints row (head, code, records, kind `rebuild`).
- **The incremental record load** (`gov.store`, called by `batch refresh`): only when the store's row holds a code
  fingerprint and it equals HEAD's (else `STORE_CODE_CHANGED`, exit 1: a full rebuild is needed). It reloads the
  record graph from HEAD (records, edges, commits, trailers, register entries: seconds), refreshes the lexical
  index (incremental by blob: only the changed record files are chunked) and the semantic vectors of the changed
  chunks, leaves the code index as it is, and writes the row (HEAD, the same code fingerprint, the new records
  fingerprint, kind `records`).
- **The store-freshness check** (`repo.store_is_of_head`): today's rule (the store holds HEAD and as many commits
  as HEAD's history) **and**, where the store has a fingerprints row: its head is HEAD, its code fingerprint equals
  HEAD's and its records fingerprint equals HEAD's. Where HEAD's fingerprints cannot be computed, the row must be a
  `rebuild` of HEAD itself. A store without a row (built before W2-68) is judged by today's rule alone.
- **The lexical index** is never fresh with changed record files: its own check (`gov.retrieval.lexical
  .freshness`) already compares every tracked file's blob; the store row's records fingerprint adds the same
  answer for the close.

## 6. What each step reads

| Step | Reads |
|---|---|
| fingerprints | git objects of one commit (`ls-tree`, `show` of the test map), the test-map schema |
| batch `run` | the working tree's status, the ticket files, HEAD; then the rebuild's, `gov check`'s and the nightly's own reads |
| reuse | the committed close records' frontmatter and the nightly folder's JSON (as `select._green_heads` does), the JUnit XML files they name, git ancestry, the fingerprints |
| batch `refresh` | the store's fingerprints row, HEAD's tree and log, the tracked files' blobs |
| store check | the store's `commits` table and fingerprints row, HEAD's fingerprints |

## 7. Failure KPIs and where each is refused

- a close citing a red run or another fingerprint's run: reuse conditions 3, 4 and 6;
- a reused run on different code: condition 6 (computed now, not only stated);
- a store accepted on another code fingerprint: the store check; the incremental load refuses a code change;
- a lexical index fresh with changed records: the lexical check and the store row's records fingerprint;
- a code merge during a batch: step 6, and every close compares fingerprints itself;
- a red that passes alone bisected: step 5 (the nightly's alone-first rule);
- reused evidence hiding a skip: the `reused` block's `skip_count` and `skips`, condition 5.

## 8. Allowed paths, as the ticket limits them

- new: `src/gov/close/batch.py`, `src/gov/close/fingerprint.py`;
- `src/gov/close/command.py`: the calls (reuse, the reused check) and the record's lines (`code_fingerprint`,
  `records_fingerprint`, `reused`, `governance_checks_reused`) only;
- `src/gov/close/repo.py`: the store-freshness check only;
- `src/gov/store/**`: the fingerprints a rebuild records and the incremental record load only;
- builder tests: `tests/unit/close/test_batch*`, `tests/unit/close/test_fingerprint*`,
  `tests/unit/store/test_fingerprint*`.

## 9. Known limits (residuals, not this ticket)

- The orchestrator's `close_queue.sh` and its skip guard (DEC-899 item 7) must call the batch and read the
  `reused` block's skip count; that is the orchestrator's tooling.
- The nightly's selection-miss rule (`nightly._scoped_closes`) reads only `scoped` closes; a red outside the
  record-reading set after a `reused` close is not named as that close's miss. `nightly.py` is not in this
  ticket's paths: a row.
- Equal fingerprints say the tree is the same, not the machine: installed packages, the interpreter and the
  pinned judge are outside the tree.

## 10. The trial (DEC-884 item 4), to be measured and added here

On a fixture programme built from scratch in a temporary folder (or a dev tier, cloned into a temporary folder):
the time per batch (two and three tickets) against the same closes one by one; reuse correct; a planted code change
forcing a fresh run; a planted record-only commit running the record-reading set and nothing else; a red batch
attributed, with nothing closing on it.
