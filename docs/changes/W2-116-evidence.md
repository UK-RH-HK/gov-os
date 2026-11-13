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

# Pass 2b: S2 (the two daily refreshes, `gov status`'s integration_store part) and R2-F3 (the token's mark)

Built to the interface text of P-W2-116-S2-INTERFACE Q1 (a) (the CTO, DEC-1157 (12)) with the lead's settlement of one
gap (DEC-1052). Nothing runs in production here: the cron line every 5 minutes (`flock <link>.refresh.lock`) is window
4's ACT.

## What was built

| Part | Where | Against the interface |
|---|---|---|
| `gov rebuild --integration <branch> --when-due` | `src/gov/rebuild/command.py` (the flag, the usage refusal), `src/gov/rebuild/integration.py` (`refresh_settings`, `now`, `due_reason`, `refresh_when_due`, `read_record`, `_write_record`) | Only valid with `--integration` (else `REBUILD_FAILED`). Due: runs the S1/S4 refresh unchanged and sets `integration.reason`. Not due: nothing built or written, `{"integration": {"status": "not_due", "branch", "link", "last_refresh"}}`. A plain `gov rebuild --integration` never reads the times and never writes the record. |
| This repository's line | `governance/project/rebuild.yaml` | `integration_refresh: {branch: w2/integrate, after_nightly: {verdict: .gov-runtime/scratch/orchestrator/log/nightly/*/run.txt, latest: "10:00"}, second: "18:00"}` (Q2 (b)). A unit test reads it. |
| `gov status`'s `integration_store` part | `src/gov/status/integration_store.py` (new), `src/gov/status/command.py` (the ninth part, `_part`) | `{link, half, head, branch, branch_head, built_at, age_seconds, stale, stale_reason, last_refresh}`; unread forms as the interface states. Never refuses; exit 0. |
| R2-F3, the token's mark | `src/gov/retrieval/retrieve.py` (committed in pass 2a, `09247e423`) | The token carries `f`, the store root as resolved once; another folder refuses `CONTINUATION_INVALID` even at one commit, naming both; a token with no `f` refuses. |

## The due rules (`integration.due_reason`)

- **after_nightly:** a counting verdict file whose time is later than the record's `at` (any one with no record); or
  `now` at or after today's `latest` with no scheduled `after_nightly` refresh whose `at` is on today's date. Both due:
  one refresh, reason `after_nightly`.
- **second:** `now` at or after today's `second` and the record's `at` before it (or no record).
- A verdict file *counts* once it has a line `^verdict:` or parses as JSON with a `"verdict"` key (a nightly still
  running holds neither). Its time is its modification time. `HH:MM` times are wall-clock times on `now`'s date, in
  `now`'s offset.
- **The clock:** `GOV_NOW` (ISO 8601; with an offset it is that instant and that offset's wall clock, kept as given; naive
  is local time), else the real clock. An invalid or empty one refuses `REBUILD_CONFIG_INVALID`, `key: "GOV_NOW"`.
- **Configuration refusals:** a missing or invalid time, a missing `branch` or no `integration_refresh` refuses
  `REBUILD_CONFIG_INVALID`; `details` = `{key, value}` (dotted key; value null when missing); nothing is built, no record
  written. Checked before anything else, so a bad line never builds.

## The record `<link>.refresh.json`

`{"at": <now, ISO with offset>, "reason", "head" (full sha), "status", "branch", "after_nightly_at"}`, written whole by
an atomic replace (a temporary file beside it, then `os.replace`) after a refresh that switched or found the head built.
`at` is `now` as the decision was taken (so a verdict file that lands during a long build is later than it and the next
tick is due again). A failed refresh refuses `REBUILD_FAILED` as before and leaves the record.

**`after_nightly_at` (the lead's settlement of the first session's gap, DEC-1052):** the record keeps only the last
refresh, so after an `after_nightly` refresh at 10:00 and a `second` one at 18:00 the literal rule would make one more
`after_nightly` refresh due. The record therefore also carries `after_nightly_at`, the `at` of the last refresh with the
reason `after_nightly`: written by that refresh, carried over (as written) by a `second` refresh. The rule "no scheduled
`after_nightly` refresh has an `at` on today's date" reads it. A record without the key (written before this) is read
as its own `at` where its reason is `after_nightly`. The acceptance case
`test_s2_success_second_is_due_once_after_its_time_and_brings_the_store_to_the_branch_head` expects `not_due` on the tick
after the second refresh; it passes.

## The stale rule (`gov status`)

`stale` is true with a `stale_reason` of the reasons that hold, joined by `"; "`, each starting with its code:
- `behind_branch: ...` when the half's head is not the branch's head in the project (both named, 12 hex digits);
- `built_before_due: ...` when `built_at` (`written_at` of the half's `.gov-runtime/rebuild/stores.json`) is before the last
  time a refresh fell due: the latest at or before `now` among the newest counting verdict file's time, `second` on today's
  and yesterday's dates, and `latest` on today's and yesterday's dates each counted only where no counting verdict file's
  time falls on that date before that `latest` (`integration.last_due`). The text names that time and what made it so.
- A figure that cannot be read is never an answer: where `integration_refresh` is missing or invalid, `branch`,
  `branch_head`, `stale` and `stale_reason` are each `{"read": false, "reason": ...}` naming the key, the rest given;
  where only one reason cannot be judged and none holds, `stale` is unread, not `false`.
- No `integration_store`, no link or a link that leads to no folder: the part is `{"read": false, "reason": ...}` and is
  in `not_read`.

## The first session's choices, kept (item 3 of the brief)

- The command line's `--integration <branch>` is what is built; `gov status` reads the config's `branch`.
- An empty `GOV_NOW` is invalid.
- A missing `after_nightly` block is key `integration_refresh.after_nightly.latest` with value null; an `after_nightly`
  that is not a map is key `integration_refresh.after_nightly`.
- A verdict file stamped after `now` does not count yet (applied in `due_reason`: `seen <= when`; a unit row pins it).
- A record with no readable `at` is no record.
- No acceptance case showed otherwise.

## Tests (pass 2b)

Every run went through `heavy_slot.sh` with the sandbox's own `TMPDIR`; a whole-folder run adds `-m "not local_only" -k
"not real and not green_here and not time_limit"` and `HOME` an empty scratch folder. No real embedder, reranker or model
was started; no `gov retrieve` or `gov context` was run.

- The repository's opt-in list keeps only the first row of a parametrised test unless `GOV_TESTS_OPTIN=lifted,breadth`
  is set, so the table cases are counted both ways:
  - Unit, new, default: `test_w2_116_when_due.py` 27 passed, `test_w2_116_integration_store.py` 25 passed,
    `test_w2_116_token_mark.py` 8 passed (pass 2a).
  - Unit, new, with the opt-in lifted (every table row): **138 passed** (the three files). The first run of it found two
    rows of the first session's table wrong in the test's own helper (it read `now` as local time, not the given offset,
    as `integration.now()` now keeps it); fixed in the test, not the code.
  - Acceptance `tests/acceptance/W2-116/` + `tests/unit/rebuild` + `tests/unit/status`, opt-in lifted: **329 passed, 1
    failed** (the known red below), 1 deselected. Pass 1's cases and pass 2b's `test_w2_116_s2_*` and
    `test_w2_116_r2f3_continuation.py` are all green.
- Regression, `tests/unit/rebuild tests/unit/status tests/unit/retrieval tests/unit/retrieve`: **724 passed, 2 skipped,
  27 failed**, 517 deselected. The 27 are none of this pass's cases and are named, not fixed:
  - `tests/unit/status/test_status.py:172` `test_a_status_with_a_part_not_read_names_every_such_place`: asserts the exact
    `PARTS` tuple and `not_read == []`; the interface's new part turns it red. Outside this ticket's paths; the CTO fixes
    it (DEC-1156 (7)).
  - Six cases of other tickets that compare a continuation token decoded "without its s key" (DEC-1090 (3)) and now also
    differ by R2-F3's `f` key (the only difference in the assertion output): `test_w2_131_register_ids.py:189` and `:209`,
    `test_w2_133_gap_label.py:170` and `:191`, `test_w2_135_item_cap.py:358` and the continuation case of the same file.
    Their `_without_s` helper must drop `f` as well. Outside this ticket's paths.
  - 20 cases of `tests/unit/retrieval/test_w2_112_shared_reranker.py`: `PermissionError: [Errno 1] Operation not
    permitted` from the sandbox (the shared reranker's socket); they do not touch this ticket's code.
