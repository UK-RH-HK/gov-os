# W2-116 evidence: the integration store in the product (pass 1: S1, S3 widened, S4, S5, F1-F3; the review's ride-along)

Ticket `DAEO-f58b`. Under DEC-963, DEC-983, DEC-982, DEC-1014, DEC-1087 (3). S2 (the two daily times and `gov status`)
is the next pass; until then the CTO's `store_refresh_daily.sh` stays the backstop (DEC-1087 (3)).

## What was built

| File | What it does |
|---|---|
| `src/gov/rebuild/integration.py` (new) | `gov rebuild --integration <branch>`: the two halves, the lock, the branch's head read under it, the seed from the ready half, the checks before the switch, the atomic switch; every stderr line dated |
| `src/gov/rebuild/command.py` | the `--integration` flag and its dispatch (refused with `--seed` or `--no-embeddings`); a seed's answer names the base's head and how it stands to the tree's head (`base_head`, `relation`: `behind`, `ahead`, `diverged` or `unknown`, and the sentence under that key) |
| `src/gov/launch/store.py` (new) | the configured place (`integration_store` in `governance/project/rebuild.yaml`), the main repository's root it is read from (`main_root`), and the session variable `GOV_STORE`, its link followed once per search (`session_root`) |
| `src/gov/launch/launcher.py` | every worker session's `env` carries `GOV_STORE`, the link itself, from the main repository's `rebuild.yaml`; a place that cannot be used refuses the launch |
| `src/gov/retrieve/command.py` | a plain `gov retrieve` (no `--root`) answers from `GOV_STORE`'s folder, never the working tree; no fall-back |

## The review's ride-along fixes before window 4 (review `w2-116.md`, DEC-802)

The review (READY, eight findings, all `Consequence: other`) left F1, F2, F4, F6 (its code part) and F8 to ride along
before window 4 puts the store live. F3 and F7 are rows; F5 and F6's slot order are the hook's lines in window 4's ACT
(restated below, not installed).

| Finding | The fix | Unit test (red on `e6724c208` before the fix, green after) |
|---|---|---|
| **F1** the head read before the lock: a refresh that waited could move the link back | `integration._refresh` takes `<link>.lock` first and only then resolves `<branch>^{commit}`; a refresh that finds the ready half at that head (and built by the running code) does nothing | `test_review_f1_a_refresh_that_waited_builds_the_head_as_it_is_once_it_holds_the_lock`; `test_review_f1_of_two_refreshes_that_waited_one_builds_the_latest_head_and_the_other_does_nothing` (the reviewer's P1: one `switched`, one `unchanged`, the link at the latest head) |
| **F2** one search opened the link once per facet, so a search spanning a switch read both halves | `store.session_root` resolves `GOV_STORE` once (`os.path.realpath`) and `retrieve`'s `_store_root` hands that one folder to every facet; where it leads to no folder the value is kept, so `STORE_MISSING` still names the configured place | `test_review_f2_one_search_follows_the_link_once_and_reads_one_half_across_a_switch` |
| **F4** `GOV_STORE` came from the launch tree's `rebuild.yaml`, which older worktrees lack | `build_settings` reads the place from `store.main_root(root)`: the main worktree of the launch tree's common git folder, read from git's own `.git` and `commondir` files (no git process); a tree that is no worktree is its own main | `test_review_f4_a_worktree_branched_before_the_line_gets_the_main_repositorys_place` (also: a launch tree naming another place still gets the main repository's) |
| **F6** (code) the product's log lines carried no date | while a refresh runs, `sys.stderr` is wrapped so each line starts with `%Y-%m-%d %H:%M:%S ` (the CTO script's `%F %T`), whichever stage writes it (the seed's line, the rebuild lock's wait, the watchdog); a refused refresh also says its `REBUILD_FAILED` there, dated, before it is raised | `test_review_f6_every_line_a_refresh_logs_starts_with_its_date_and_time`; `test_review_f6_a_refused_refresh_logs_its_failure_with_the_date_and_time` |
| **F8** a seed from a base ahead of the tree was labelled `behind` | `_behind` counts both ways: `behind` (base an ancestor), `ahead` (the tree an ancestor), `diverged` (both counts non-zero), `unknown` (the base's head is not in this repository); `relation` names it and the sentence, with the base's head, is under that key; `behind` keeps its sentence | `test_review_f8_a_seed_from_a_base_ahead_of_the_tree_is_named_ahead_never_behind`; `test_review_f8_a_seed_from_a_base_on_another_line_is_named_diverged` |

## One row per KPI line of this pass

| KPI line | How it is met | Verified by |
|---|---|---|
| **S1** `gov rebuild --integration <branch>` keeps a store of the head in two detached worktrees outside the project, builds into the one not in use, switches the link only when the build succeeded; a search during a build is answered from the ready one | `integration.refresh`: halves `<link>-a`/`-b` (worktrees of the project's repository, made or checked out `--detach` at the head); the build is `gov rebuild --seed <ready half>` in the other half, run by the running code; the switch is `os.replace` of a new link; nothing at an unchanged head | unit: first refresh, unchanged head, new head into the other half, third head back, seeded equals cold, a search during a build; `gov accept` success-1: 5 passed |
| **S3 (widened)** `gov launch` points every worker session's retrieval at the integration store; a designer's retrieval never reads a ticket worktree's store | `build_settings` sets `env.GOV_STORE` to the configured link for every worker role; `gov retrieve` without `--root` answers from it; set and empty there, `STORE_MISSING` names that folder, never the worktree's store | unit: four roles carry the link; plain retrieve answers from the link; `--root` wins; unset: today's behaviour; `gov accept` success-3: 6 passed |
| **S4** refreshed after every landing on the integration branch; it is the warm base `gov rebuild --seed` reads; a seed behind the head is named; only what changed is re-embedded | the command is idempotent, so a hook can call it after every landing (the hook line below); the refresh seeds from the ready half, and the seed's answer carries `base_head` (40 hex), `relation` and, under that key, the sentence (`behind`: "built at `<sha>`, behind this tree's head `<sha>` by N commit(s)"; `ahead` and `diverged` as they are, review F8) only when the base is not at the head | unit: only the changed texts are sent (empty machine cache), seed at the head says nothing of behind, behind by 2 commits named, ahead by 2 named and never `behind`, diverged named; `gov accept` success-4: 7 passed |
| **S5** a re-index never empties the semantic index; a model-less re-index reports the facet unavailable | no change was needed in `semantic.py`: with no endpoint, `semantic._build` returns before any vector is touched, and the rebuild reports `stores.semantic: not_recreated` with the reason; the record and lexical stages are each one transaction | unit: model-less re-index keeps every vector, facet unavailable; `gov accept` success-5: 2 passed |
| **F1** a designer's retrieval answered from a ticket worktree's store | refused by construction: with `GOV_STORE` set, the working tree is never opened, even when it holds a store | unit: a worktree with its own store answers `STORE_MISSING` for the configured place; `gov accept` failure-1: 1 passed |
| **F2** the link switched to a failed build, or a search answered from a half-built store | the switch only after: no error, `lexical` and `semantic` both `recreated` (N-2), the half's lexical index then `fresh` and its semantic facet clean (`semantic._status` is None), the half still at the head built; any other end leaves the link and raises `REBUILD_FAILED` with the stores in `details` | unit: endpoint fails, model-less, a stage raising, a build killed half-way (then the next refresh seeds over it); `gov accept` failure-2: 4 passed |
| **F3** a failed re-index leaves the previous index and reports the failure | the double buffer for the integration store; in a tree, a failing stage raises `REBUILD_FAILED` and its transaction leaves the earlier rows | unit: a lexical stage that raises leaves chunk and vector counts as before; `gov accept` failure-3: 2 passed |

## How the double buffer keeps the ready half answering (F2)

- The link always points at a half whose build completed. The refresh never writes that half: it checks out and
  rebuilds the other one, and reads the ready half only through SQLite's backup (a consistent read while searches run).
- Searches take no lock and follow the link once, at their start (`store.session_root`, review F2), so every search
  started during a build reads the ready half, complete, and every facet of one search reads the same half. A search
  that started just before a switch finishes on the half it resolved; the old half is rebuilt only at the refresh after
  next.
- The switch is one `rename(2)` of a new symbolic link over the old (`os.replace`): a reader sees the old or the new
  half, never neither.
- A build that fails, or a process killed before the switch, leaves the link where it was. The half left behind has no
  W2-122 record (`forget` at the start of every rebuild), so it is never a warm base and never pointed at; the next
  refresh seeds over it.
- One refresh at a time: an exclusive `flock` on `<link>.lock` (the file `refresh_integration_store.sh` and the merge
  queue's promotion already use), waited for with a line on stderr. Lock order is the link's lock, then the rebuild
  lock, the same order as the CTO's script. The branch's head is read only once the lock is held (review F1), so of
  several refreshes that waited, the first builds the latest head and the others find it built and do nothing.
- **The rebuild uses the code it runs under:** the build runs in-process (`gov.rebuild.command.run` on the half), never
  the half's own `src/`. "Unchanged" requires the ready half's record to name the running code, so after a re-pin the
  first refresh rebuilds even at the same head. The pinned gov's store always matches the pinned code.

## Where a search's question-vector cache goes (N-4)

- A search through the link would write `<ready half>/.gov-runtime/query-vector-cache.db` (DEC-782). A launched
  (sandboxed) session may not write there: its sandbox allows writes only to its own temp folder and its runs folder.
- No change is needed: the cache write is already skipped when it fails (`semantic._cache` catches `sqlite3.Error`),
  and reading an existing cache is read-only. The machine-wide cache (`~/.cache/gov-os/vector-cache`, W2-126) is also
  outside the sandbox's writes and also skips a failed write. So a sandboxed search embeds its question again each time
  (one small GPU request) and changes no answer.
- Unsandboxed searches (the CTO's) still fill the ready half's cache. That file is separate from `store.db`, and the
  seed does not copy it.
- I did not let sessions write into the halves on purpose: the double buffer's guarantee rests on nothing but the
  refresh writing a half. If the repeated query embedding ever costs too much, the fix is to point the cache at the
  session's `TMPDIR` in `semantic.py` (not in this ticket's paths).

## The hook for re-pin window 4 (the owner's operator installs it; not installed here)

`/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/reference-transaction` (executable, shared by every worktree; git
2.43 has the hook). It fires on every update of `w2/integrate`, whether by `git merge` by hand or the merge queue's
`update-ref`, and runs the refresh in the background. The refresh's own worktree checkouts move only the halves' `HEAD`,
so the hook does not fire again. Restated with the review's F5 and F6 (the CTO's lines for window 4's ACT):

```sh
#!/bin/sh
# W2-116: refresh the integration store after every landing on w2/integrate (does nothing at an unchanged head)
[ "$1" = committed ] || exit 0
grep -q ' refs/heads/w2/integrate$' || exit 0
setsid -f env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u GOV_REBUILD_LOCK sh -c 'cd /home/usain/Dynamic-Agentic-Engineering-OS && exec flock /home/usain/gov-os-worktrees/W2-00-store.refresh.lock bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh /home/usain/.local/bin/gov rebuild --integration w2/integrate' >> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/integration-store.log 2>&1 </dev/null
exit 0
```

- **F5:** `env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u GOV_REBUILD_LOCK` comes before everything the hook
  starts, so the pinned `gov` runs its own code whatever environment the git call that fired the hook had. The path of
  `gov` is written out, not `$HOME/...`, so a commit made by a session with another `HOME` still finds it.
- **F6 (the slot order):** the hook waits on the store's refresh lock before it asks for a heavy slot, so a refresh that
  waits for another holds no slot. The lock is `W2-00-store.refresh.lock`, beside the link's own `<link>.lock`, **not
  that file itself**: `flock` locks belong to each open of a file, so if the hook held `<link>.lock`, the `gov` it starts
  would wait on its own parent forever. The product's `<link>.lock` still keeps the refresh apart from the CTO's
  `refresh_integration_store.sh` and the merge queue's promotion. Waiters queue on the outer lock; with F1, the first
  through builds the latest head and the rest each take a slot for a few seconds and find it `unchanged`.
- The product dates its own log lines (F6's code part, above); the `REBUILD_FAILED` line of a refused refresh is dated
  there too. The JSON result `gov` prints on stdout at the end is not a log line and is not dated.

**It needs one line of configuration first,** outside this ticket's paths: the CTO adds
`integration_store: /home/usain/gov-os-worktrees/W2-00-store` to `governance/project/rebuild.yaml` on `w2/integrate`.
Without it, `--integration` refuses, and `gov launch` sets no `GOV_STORE` (today's behaviour).

## Tests

- Unit (stand-in embedder and code-graph tool, planted git repositories, no model):
  - `tests/unit/rebuild/test_w2_116_integration.py`: 25 passed (19 + 6 for the review's F1, F6, F8);
  - `tests/unit/launch/test_w2_116_store.py`: 15 passed (13 + 2 for F2, F4).
  - The 8 new tests were run against the code before the fix (a detached worktree at `e6724c208`): 8 failed.
- `gov accept W2-116` (`HOME=/home/usain`, after the ride-along): **pass**, 20 passed, 0 failed, 0 skipped. Lines
  success-1/3/4/5 and failure-1/2/3; S2 is not mapped in this pass.
- Regression, `tests/unit/rebuild`, `tests/unit/launch`, `tests/unit/retrieve` with `GOV_TESTS_OPTIN=lifted,breadth`
  and `-m "not local_only" -k "not real and not green_here and not time_limit"`, `HOME` an empty folder: **257
  passed** (249 + the 8 new), none deselected: the real-model exclusion removes no case in these folders.
- Every run went through `heavy_slot.sh`. No real embedder, reranker or model was started.
