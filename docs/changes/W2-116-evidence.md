# W2-116 evidence: the integration store in the product (pass 1: S1, S3 widened, S4, S5, F1-F3)

Ticket `DAEO-f58b`. Under DEC-963, DEC-983, DEC-982, DEC-1014, DEC-1087 (3). S2 (the two daily times and `gov status`)
is the next pass; until then the CTO's `store_refresh_daily.sh` stays the backstop (DEC-1087 (3)).

## What was built

| File | What it does |
|---|---|
| `src/gov/rebuild/integration.py` (new) | `gov rebuild --integration <branch>`: the two halves, the lock, the seed from the ready half, the checks before the switch, the atomic switch |
| `src/gov/rebuild/command.py` | the `--integration` flag and its dispatch (refused with `--seed` or `--no-embeddings`); a seed's answer names a base behind the tree's head (`base_head`, `behind`) |
| `src/gov/launch/store.py` (new) | the configured place (`integration_store` in `governance/project/rebuild.yaml`) and the session variable `GOV_STORE` |
| `src/gov/launch/launcher.py` | every worker session's `env` carries `GOV_STORE`, the link itself; a place that cannot be used refuses the launch |
| `src/gov/retrieve/command.py` | a plain `gov retrieve` (no `--root`) answers from `GOV_STORE`'s folder, never the working tree; no fall-back |

## One row per KPI line of this pass

| KPI line | How it is met | Verified by |
|---|---|---|
| **S1** `gov rebuild --integration <branch>` keeps a store of the head in two detached worktrees outside the project, builds into the one not in use, switches the link only when the build succeeded; a search during a build is answered from the ready one | `integration.refresh`: halves `<link>-a`/`-b` (worktrees of the project's repository, made or checked out `--detach` at the head); the build is `gov rebuild --seed <ready half>` in the other half, run by the running code; the switch is `os.replace` of a new link; nothing at an unchanged head | unit: first refresh, unchanged head, new head into the other half, third head back, seeded equals cold, a search during a build; `gov accept` success-1: 5 passed |
| **S3 (widened)** `gov launch` points every worker session's retrieval at the integration store; a designer's retrieval never reads a ticket worktree's store | `build_settings` sets `env.GOV_STORE` to the configured link for every worker role; `gov retrieve` without `--root` answers from it; set and empty there, `STORE_MISSING` names that folder, never the worktree's store | unit: four roles carry the link; plain retrieve answers from the link; `--root` wins; unset: today's behaviour; `gov accept` success-3: 6 passed |
| **S4** refreshed after every landing on the integration branch; it is the warm base `gov rebuild --seed` reads; a seed behind the head is named; only what changed is re-embedded | the command is idempotent, so a hook can call it after every landing (the hook line below); the refresh seeds from the ready half, and the seed's answer carries `base_head` (40 hex) and `behind` ("built at `<sha>`, behind this tree's head `<sha>` by N commit(s)") only when the base is not at the head | unit: only the changed texts are sent (empty machine cache), seed at the head says nothing of behind, behind by 2 commits named; `gov accept` success-4: 7 passed |
| **S5** a re-index never empties the semantic index; a model-less re-index reports the facet unavailable | no change was needed in `semantic.py`: with no endpoint, `semantic._build` returns before any vector is touched, and the rebuild reports `stores.semantic: not_recreated` with the reason; the record and lexical stages are each one transaction | unit: model-less re-index keeps every vector, facet unavailable; `gov accept` success-5: 2 passed |
| **F1** a designer's retrieval answered from a ticket worktree's store | refused by construction: with `GOV_STORE` set, the working tree is never opened, even when it holds a store | unit: a worktree with its own store answers `STORE_MISSING` for the configured place; `gov accept` failure-1: 1 passed |
| **F2** the link switched to a failed build, or a search answered from a half-built store | the switch only after: no error, `lexical` and `semantic` both `recreated` (N-2), the half's lexical index then `fresh` and its semantic facet clean (`semantic._status` is None), the half still at the head built; any other end leaves the link and raises `REBUILD_FAILED` with the stores in `details` | unit: endpoint fails, model-less, a stage raising, a build killed half-way (then the next refresh seeds over it); `gov accept` failure-2: 4 passed |
| **F3** a failed re-index leaves the previous index and reports the failure | the double buffer for the integration store; in a tree, a failing stage raises `REBUILD_FAILED` and its transaction leaves the earlier rows | unit: a lexical stage that raises leaves chunk and vector counts as before; `gov accept` failure-3: 2 passed |

## How the double buffer keeps the ready half answering (F2)

- The link always points at a half whose build completed. The refresh never writes that half: it checks out and
  rebuilds the other one, and reads the ready half only through SQLite's backup (a consistent read while searches run).
- Searches take no lock and follow the link when they open the store, so every search started during a build opens the
  ready half, complete. A search that opened the link just before a switch finishes on the half it opened; the old half
  is rebuilt only at the refresh after next.
- The switch is one `rename(2)` of a new symbolic link over the old (`os.replace`): a reader sees the old or the new
  half, never neither.
- A build that fails, or a process killed before the switch, leaves the link where it was. The half left behind has no
  W2-122 record (`forget` at the start of every rebuild), so it is never a warm base and never pointed at; the next
  refresh seeds over it.
- One refresh at a time: an exclusive `flock` on `<link>.lock` (the file `refresh_integration_store.sh` and the merge
  queue's promotion already use), waited for with a line on stderr. Lock order is the link's lock, then the rebuild
  lock, the same order as the CTO's script.
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
so the hook does not fire again:

```sh
#!/bin/sh
# W2-116: refresh the integration store after every landing on w2/integrate (does nothing at an unchanged head)
[ "$1" = committed ] || exit 0
grep -q ' refs/heads/w2/integrate$' || exit 0
setsid -f sh -c 'cd /home/usain/Dynamic-Agentic-Engineering-OS && exec bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh "$HOME/.local/bin/gov" rebuild --integration w2/integrate' >> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/integration-store.log 2>&1 </dev/null
exit 0
```

**It needs one line of configuration first,** outside this ticket's paths: the CTO adds
`integration_store: /home/usain/gov-os-worktrees/W2-00-store` to `governance/project/rebuild.yaml` on `w2/integrate`.
Without it, `--integration` refuses, and `gov launch` sets no `GOV_STORE` (today's behaviour).

## Tests

- Unit (stand-in embedder and code-graph tool, planted git repositories, no model):
  - `tests/unit/rebuild/test_w2_116_integration.py`: 19 passed (all rows, with the opt-in suites);
  - `tests/unit/launch/test_w2_116_store.py`: 13 passed.
- `gov accept W2-116` (`HOME=/home/usain`): **pass**, 20 passed, 0 failed, 0 skipped. Lines success-1/3/4/5 and
  failure-1/2/3; S2 is not mapped in this pass.
- Regression, `tests/unit/rebuild`, `tests/unit/launch`, `tests/unit/retrieve` with `-m "not local_only" -k "not real
  and not green_here and not time_limit"`: 138 passed, 111 deselected by the opt-in sampling. With
  `GOV_TESTS_OPTIN=lifted,breadth`: 249 passed. The real-model exclusion removes no case in these folders.
