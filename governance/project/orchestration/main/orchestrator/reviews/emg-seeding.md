# Review: emergency fix (d), no cold rebuild anywhere (DEC-1032 step iv, DEC-1033)

Reviewer: fresh, read-only session. Staged work: `.gov-runtime/scratch/orchestrator/tools-review/`. No engineer summary was found there, so the design was inferred from the two patches, `seed_store.py`, `new_worktree.sh`, the changed copies and the tests.

## What I ran

- `MQ_TOOL=<tools-review>/repo/merge_queue.py nice python3 -m pytest -q -p no:cacheprovider test_seed_store.py repo/test_merge_queue_seed.py` gave **29 passed** in 52 s. Without `MQ_TOOL` the queue test fails at collection, because it resolves `merge_queue.py` relative to the repository. That is a path matter, not a defect.
- `test_seed_store.py::test_a_seeded_rebuild_embeds_only_the_changed_chunks_and_equals_a_cold_one` runs the real `gov rebuild` against a stand-in Ollama on a loopback port.
- `test_nightly.sh` was not run. It reads the live `nightly.sh` through `$HERE` and starts night-mode scripts. I replayed its N10 and N11 checks by hand on the patched `repo/nightly.sh`:
  - There is exactly one `gov.cli.main rebuild` line, and it still carries `GOV_SECRETS_FULL_SCAN=1`.
  - No other non-comment line mentions `GOV_SECRETS_FULL_SCAN`.
  - `bash -n` is clean.
- I read `src/gov/retrieval/{semantic,lexical,chunking}.py`, `src/gov/rebuild/command.py` and `rebuild_slot.sh`.
- I did not touch the integration store, Ollama or the live tools. I created no temp folders beyond what the tests make.

## KPI 1: seeded-equals-cold (pass)

The design holds up from the code, not only from the tests.

- `semantic._build` computes `wanted` from `lexical_chunk`, which is the corpus after `gov.secrets.indexable` and the `embedding_policy` check. It deletes every vector whose id is not in `wanted` and embeds only the missing ones.
- A carried vector is therefore used only for a chunk the cold build would also index. A chunk that a changed `.gitleaks.toml`, a changed secrets rule or a changed path-map would now exclude is pruned. A chunk newly included gets no vector and is embedded.
- A chunk id is the hash of its path, its blob and its lines. The text embedded is the first 512 characters of the text built by `chunking.py` and `lexical.py`, and the guard compares those two files and `semantic.py` by blob. A changed embedder revision empties the table (`built_by != (MODEL, revision)`).
- The code index is never copied, and the record store is reloaded by `store_load` on every rebuild.
- In the whole-store case (same commit, both trees clean), the lexical refresh is incremental by path and blob (`lexical._freshness`), so a base that was mid-refresh, or whose store differs from its HEAD, is repaired by the tree's own rebuild.
- The seed fails closed. A missing base, an own store without `--replace`, a guard mismatch or a copy fault each return a named answer. `keep_vectors_only` raising `sqlite3.Error` is caught, and the rebuild then runs cold.

Findings, all low:

- **S1 (low, in).** The equality test compares only the `semantic_vector` rows, not the lexical tables or the secrets judgements. It has no case for a file whose blob is unchanged while the secrets config changes. My reading of `_build` says this is safe. A one-line test would pin it.
  - Ordinary work: no. It needs a secrets-config change with an unchanged blob.
  - Consequence: other.
- **S2 (low, in).** In `--replace` mode, `copy_seed` removes the tree's store before `os.replace`. If `os.replace` then fails, the tree is left with no store and its rebuild runs cold.
  - Ordinary work: no, because it needs a disk or permission fault.
  - Consequence: other. The result is slow, not wrong, though it contradicts "a failed seed leaves the tree as it was".
- **S3 (info, in).** A whole-store copy carries the secrets judgements made by the base's gitleaks run, which an incremental rebuild would keep too. Only the nightly (vectors-only) re-judges every file. No change from today.

## KPI 2: attribution-without-alt-at-head (FAIL, one blocking finding)

The nightly shortcut can only move a case toward "the batch's" or toward Stop. It never clears a red by itself, and `test_the_nightly_of_the_head_red_alone_stops_without_a_run_but_never_clears_by_itself` pins this. Lock ordering is sound (see KPI 3). The problem is the tree the re-runs go in.

- **A1 (medium, BLOCKING, in).** Nothing makes the integration store's ready tree clean **before** a re-run. `head_held` checks only `HEAD == head`. `restore` runs only in `finally`, after the run, and it ignores ignored files by design.
  - Scenario: a queue run is killed hard during an `alone` case in the ready tree (SIGKILL, OOM, a WSL or machine restart, or the load-driven timeout kill this machine sees).
    1. `finally` never runs, so a case that wrote a tracked file, left an untracked file, or rewrote `.gov-runtime/store.db` or another ignored file leaves its residue.
    2. The next run finds `HEAD == head` and runs the cases there.
    3. A baseline-cleared red that the residue makes red on that tree stays "unowned", so a bad batch lands. Equally, residue can turn a green into a red and misattribute it.
  - The previous design used a fresh `alt` clone built at the head, which had no residue. This is a new hermeticity loss.
  - Ordinary work: yes, because hard kills and restarts are ordinary on this loaded machine.
  - Consequence: fails open (a red wrongly cleared, so a bad batch lands). It can also wrongly eject a good ticket.
  - Severity: medium. The probability is low, but a wrong landing is the costly outcome.
  - Fix: in `head_held`, after taking the shared hold and confirming HEAD, call the same undo as `restore` (`git status --porcelain` must be empty, else `checkout --force` and `clean -fdq`, and name it). Add a test that plants a dirty tracked file and an untracked file before the run.
  - Stronger fix: run the cases in a throwaway `git worktree add --detach` of the head with `store.db` copied in, so the live ready tree is never executed in.
- **A2 (medium, in, not reproduced, needs a probe before approval).** The ready tree is a worktree of the main repository, so it shares refs, `config`, hooks and `packed-refs` with the live repo. The earlier `alt` was an isolated clone.
  - The undo covers tracked and untracked files and HEAD only.
  - It does not cover: refs, tags, stashes, `git config` writes, or the ignored `store.db` and caches in the tree.
  - It does not cover what concurrent retrievals see during the run. Test designers search that store, so a case that edits a tracked file and then refreshes the store rewrites `store.db`. After `restore` the store is stale against the head, and it stays that way until the next refresh.
  - My grep of `tests/` found only read-only git use against the repo root (`ls-files`, `show`, `config --get`). I could not show a case that does this. The owner's criterion names exactly this class, so I rank it just below A1.
  - Ordinary work: yes only if a selected case writes repo git state or refreshes a store in cwd. Not shown.
  - Consequence: fails open (what concurrent retrievals see). In one variant it loses work, if a test commits on the detached HEAD (the commit is dangling after `restore`).
  - Fix: either the throwaway worktree above, or compare `store.db`'s stamp and the refs before and after, and name any difference.
- **A3 (low, in).** `known == "passed"` comes from a case that passed inside the nightly's suite context. The clone's red was an `alone` run. A case that is red alone but green in a suite (order or fixture dependence) at the head is judged "not on the head", so the batch is blamed and a good ticket is ejected. It can never land a bad batch.
  - Ordinary work: rare. The case needs to be red at the baseline and red alone in the clone.
  - Consequence: other. A good ticket is ejected (recoverable by re-enqueue).
  - Mitigation: use "passed" only for cases that the nightly also ran alone, or re-run once when the clone's red was an alone-red.
- **A4 (info).** The `since`/Stop path and the "refresh first, else Stop and eject nobody" path behave as claimed. `head_known` stops at the first run file that names the head. If that run has no verdict, the cases are re-run, which is conservative.

## KPI 3: promotion-safe (pass)

- Promotion happens only when `built[clone] == result`, the clone's HEAD is `result`, and the integration branch's head is `result`.
- The flip happens under an exclusive, non-blocking `<link>.lock`. A held lock sends it to the normal refresh. The standby half is checked out at `result`, seeded `--replace` and rebuilt through `rebuild_slot.sh`. That wrapper returns 75 when the semantic store is "ok" but not recreated, so the link is not flipped on a partial rebuild (checked in `rebuild_slot.sh`).
- The refresh script takes the same lock with `flock -w`, reads `want` after taking it, and returns "fresh" if the link already matches. A promotion racing a refresh is serialized, and the loser is a no-op.
- Python 3 file descriptors are non-inheritable, so the test children do not keep the queue's lock.
- The shared hold is taken after `head_tree`, with HEAD re-checked under the hold. `restore` runs before the hold is closed.
- Findings, both low:
  - **P1 (low, in).** `promote` and `_promote` are not wrapped. A fault after `advance` and `_landed` (for example, no permission on the lock file or the symlink) would end the run with a traceback after the branch has moved. Nothing is lost, but the exit is unplanned. Wrap with `try/except OSError`, name it and start the refresh.
    - Ordinary work: no.
    - Consequence: other.
  - **P2 (low, in).** The head check (`self.head() == result`) is made before the lock. A hand merge to the integration branch during the flip leaves the link one commit behind, and nothing starts a refresh. The next queue run catches it in `head_tree` (refresh first, else Stop). A hand merge is the CTO's own act and was already followed by a manual refresh. This is no regression.
    - Ordinary work: occasionally.
    - Consequence: other.

## KPI 4: nightly-unharmed (pass)

- The new line is `seed ... --vectors-only --who nightly`, run before the unchanged rebuild line. In `--vectors-only` mode the seeder skips product mode and the whole-store path, drops every non-vector table, and refuses outright if the three guard files differ. The record store, the lexical index and the secrets judgements are all built by the clone's own code, under `GOV_SECRETS_FULL_SCAN=1` on every file.
- N10 and N11 still hold on the patched file. A seed failure is written to `run.txt` and does not stop the night.
- Findings, both low:
  - **N1 (low, in).** The nightly no longer exercises a cold embed. If the vectors carried over were wrong, the nightly would not see it. Pruning by `wanted` makes wrong vectors unlikely. If the owner wants one cold check, add a weekly cold run.
  - **N2 (info).** `echo "$(... | tail -1)"` writes the last line of a traceback if the seeder crashes. This is named but not parsed.

## Other notes

- `refresh_integration_store.sh` comments claim an exit-75 guard. That guard is real but lives in `rebuild_slot.sh`. The test for it only stubs rc 75.
- The seeder takes no lock on the base while it copies. SQLite backup gives a consistent snapshot, and the tree's own rebuild checks freshness by blob, so this is safe. Reading from a half that is being refreshed can only give a partly stale copy, which the rebuild corrects.
- `close_build.py`: the seeder wrapper passes the rebuild's stdout through and returns its exit code, so callers are unchanged.

## Blocking findings

- **A1.** Run the cases only in a tree verified clean, or in a throwaway worktree. This is a small change.
- **A2.** Not blocking on its own, but it needs the probe or the throwaway worktree before the fix goes live.

```verdict
{"kpis": [
 {"kpi": "seeded-equals-cold", "verdict": "pass", "findings": [
  {"id": "S1", "scope": "in", "ordinary_work": "no, because it needs a secrets-config change with an unchanged blob; _build prunes by the wanted set, so the result is still equal", "consequence": "other"},
  {"id": "S2", "scope": "in", "ordinary_work": "no, because it needs a disk or permission fault between removing the store and installing the copy", "consequence": "other"},
  {"id": "S3", "scope": "in", "ordinary_work": "yes, but it is the same as today's incremental rebuild", "consequence": "other"}]},
 {"kpi": "attribution-without-alt-at-head", "verdict": "fail", "findings": [
  {"id": "A1", "scope": "in", "ordinary_work": "yes, because a hard kill or restart during a re-run leaves residue that the next run executes in with no cleanliness check", "consequence": "fails open"},
  {"id": "A2", "scope": "in", "ordinary_work": "yes only if a selected case writes repo git state or refreshes a store in cwd; not shown", "consequence": "fails open"},
  {"id": "A3", "scope": "in", "ordinary_work": "rarely; a case red alone but green in the nightly's suite", "consequence": "other"}]},
 {"kpi": "promotion-safe", "verdict": "pass", "findings": [
  {"id": "P1", "scope": "in", "ordinary_work": "no, because it needs a lock or symlink fault after the landing", "consequence": "other"},
  {"id": "P2", "scope": "in", "ordinary_work": "occasionally, when the CTO hand-merges during a promotion", "consequence": "other"}]},
 {"kpi": "nightly-unharmed", "verdict": "pass", "findings": [
  {"id": "N1", "scope": "in", "ordinary_work": "yes, but it only means the nightly no longer checks a cold embed", "consequence": "other"},
  {"id": "N2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}
]}
```

## Round 2 (DEC-1010, the last): attribution-without-alt-at-head only

Reviewed `tools-review/repo/merge_queue.py` (`head_tree`, `copy_head_stores`, `sweep_head_trees`, `remove_head_trees`, `snapshot`, and their two call sites). Tests: `MQ_TOOL=<tools-review>/repo/merge_queue.py python3 -m pytest -q -p no:cacheprovider repo/test_merge_queue_seed.py test_seed_store.py` gave **30 passed** in 56 s.

### A1 and A2: resolved
- No case runs in the integration store's own tree any more. The ready half is only read: `store.db` and the query cache are copied by SQLite backup under the shared hold, and HEAD is re-checked under that hold. Residue there, concurrent retrievals and `store.db` rewrites can no longer reach a verdict or a retrieval.
- Before every `head_tree` use the tree's snapshot is compared: HEAD, status including untracked and ignored names, and the stamps of every file under `.gov-runtime`. Any difference makes a new tree.
- A tree a killed run left is swept at the next run's start. The sweep touches only paths of the form `<work root>/<stamp>/head-...` that are registered in this repository and are not this run's own folder.
- The code index is made anew in each throwaway tree, so nothing is embedded.

### The engineer's residual: shared refs and config
- **Scope: in.** It is the same property the owner named ("the live refs"). The throwaway worktree shares refs, `config`, hooks path and `packed-refs` with the live repository. The old `alt` clone did not.
- **Ordinary work: no, as far as I can show.** I searched `tests/` for tests that write git state (`config`, `tag`, `update-ref`, `stash`, `gc`, `worktree`, `notes`). Every hit is on a planted `project` or `repo` fixture, not on the repository root. The queue speed test that sets `core.hooksPath` does so on a planted warm clone. An honest agent writing a test would use a tmp repository. It would have to run a git write in the cwd repository deliberately, or run a `gov` command that installs hooks or writes config in the repository root.
- **Consequence if it happens: fails open.** A changed `core.hooksPath` or a new ref would apply to the live repository and every worktree, including the governance hooks. Severity: low to medium (low probability, high reach).
- **Verdict on it: acceptable residual, not blocking.** It is a cheap hardening, not a fix to wait for:
  - Make the throwaway tree `git clone -q --shared --no-checkout <repo> <tree>` followed by `checkout --detach <head>`. Refs, config and hooks are then its own, and objects are shared read-only. This costs seconds and removes the residual, and `git worktree add/prune` then no longer touches the live repo at all.
  - Failing that, snapshot `git for-each-ref | sha1sum` and `git config --local --list | sha1sum` of the live repository before and after each case and name any difference.

### Other round 2 findings
- **R2-1 (low, in).** The snapshot is checked once per `head_tree` call. The rounds of one case (`red_alone` and `kinds` in `on_head`) share the checked tree, so a case that dirties the tree in round 1 can affect round 2 of the same case. Re-check, or re-make, per run in `alone`.
  - Ordinary work: rare. Consequence: other. Round 1 had this class, and a fresh clone would not have.
- **R2-2 (low, in).** `git worktree prune` in `remove_head_trees` and the sweep is repository-wide. It would also drop the metadata of a lead's worktree whose folder is momentarily missing. `worktree remove --force` per path already suffices. Using a `--shared` clone makes this moot.
  - Ordinary work: rare. Consequence: other.
- **R2-3 (info).** `snapshot` sees ignored files by name only, not by content. A test cannot change an ignored file's content without leaving its stamp (under `.gov-runtime`) or its name (elsewhere) different, except for an ignored file that existed before. A fresh worktree has none. No action.
- **A3 (unchanged, low).** Still open: a "passed" from the nightly's suite context can eject a good ticket and never lands a bad batch.

### Round 2 verdict
`attribution-without-alt-at-head` passes. A1 and A2 are resolved. The shared-refs residual is in scope but not ordinary work as far as the repository's tests show, and it is not blocking. The `--shared` clone is recommended.

```verdict
{"kpis": [
 {"kpi": "seeded-equals-cold", "verdict": "pass", "findings": []},
 {"kpi": "attribution-without-alt-at-head", "verdict": "pass", "findings": [
  {"id": "A1", "scope": "in", "ordinary_work": "resolved: nothing runs in the integration store's tree; the throwaway tree is compared with its snapshot before each use and killed runs' trees are swept", "consequence": "other"},
  {"id": "A2", "scope": "in", "ordinary_work": "resolved for store.db and concurrent retrievals; the shared refs and config remain (the residual)", "consequence": "other"},
  {"id": "R-shared-refs", "scope": "in", "ordinary_work": "no, because no test in the repository writes git state in the repository root; it needs a deliberate git or hook-installing write in cwd", "consequence": "fails open"},
  {"id": "R2-1", "scope": "in", "ordinary_work": "rare; the rounds of one case share the checked tree", "consequence": "other"},
  {"id": "R2-2", "scope": "in", "ordinary_work": "rare; worktree prune is repository-wide", "consequence": "other"},
  {"id": "A3", "scope": "in", "ordinary_work": "rarely; a case red alone but green in the nightly's suite", "consequence": "other"}]},
 {"kpi": "promotion-safe", "verdict": "pass", "findings": []},
 {"kpi": "nightly-unharmed", "verdict": "pass", "findings": []}
]}
```

### Round 2 final verdict (strict form; the reasons are in the prose above)

```verdict
{"kpis": [
 {"kpi": "seeded-equals-cold", "verdict": "pass", "findings": []},
 {"kpi": "attribution-without-alt-at-head", "verdict": "pass", "findings": [
  {"id": "R-shared-refs", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
  {"id": "R2-1", "scope": "in", "ordinary_work": "no", "consequence": "other"},
  {"id": "R2-2", "scope": "in", "ordinary_work": "no", "consequence": "other"},
  {"id": "A3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "promotion-safe", "verdict": "pass", "findings": []},
 {"kpi": "nightly-unharmed", "verdict": "pass", "findings": []}
]}
```
