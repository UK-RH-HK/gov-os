# The orchestration tools

## `merge_queue.py`: the local merge queue (W2-97)

The CTO's tool and the only thing that moves `w2/integrate` (DEC-959 item 1, ROLES-RESEARCH-1 option (c)). It tests
each candidate merge before the branch moves, advances the branch only on green, and only by a fast-forward to the
merge commit it tested, so the commit tested is the commit landed. On red the branch stays where it was and the ticket
that caused the red goes back. It never pushes (the push stays the owner's, DEC-959 item 2), never touches another
branch (`main` included), and never amends, rebases or resets a branch. Standard library and `git` only.

It follows `close_build.py`'s steps and reuses its reviewed red attribution and culprit search (`trace_node`,
`decisive`, `attribute`, `explained_without`, `red_alone`, `assign_culprits`, and `merge_is_own`'s rule as
`own_commits`), copied with their test cases into `tests/unit/orchestration/test_w2_97_merge_queue.py`.

### How the CTO approves and runs it

```
python3 merge_queue.py enqueue --queue <dir> --ticket W2-97 --task DAEO-wq2b --branch w2/W2-97 --commit <tested commit>
python3 merge_queue.py approve --queue <dir> --ticket W2-97 --by CTO
python3 merge_queue.py run --repo <repo> --queue <dir>
```

- `enqueue` writes the request: the ticket (WBS id), its task (the `Task:` its commits carry), its branch, and the exact
  commit its lead tested, resolved to its full id (in `--repo`, default the current folder: the lead's worktree); a
  commit it cannot resolve there is refused unless given as a full id. `run` resolves a short id in a hand-written
  approval in its own `--repo`. **A request alone never enters the queue.**
- `approve` moves the request to `approved/`, adding `approved_by` and `approved_at`. **The approval file is the
  entry:** until the three layers start, only the CTO approves (by `approve`, or by writing the file in the same
  form). A ticket with no request is refused (non-zero exit, nothing written).
- `run` processes every approved entry, in approval order, as one batch on one head.

`run`'s options: `--base <commit>` (the known state reds are traced against: the last nightly with a verdict until a
green one after ACT 1, then the last green one, DEC-988, DEC-989; see below; the old way, which builds a clone at
the baseline: since Q-1, DEC-1050, `land.py` no longer passes it, and without it no baseline clone is built);
`--integration` (default `w2/integrate`); `--work` (the clean clones; default
`~/gov-os-runs/W2-00/merge-queue/`, each run's own folder removed when the run ends); `--rounds` (default 1, Q-1,
DEC-1050: the re-runs of each red alone); `--load-sensitive <file>` (a plain list, one test id, function or file per
line: those cases get 3 rounds); and the three stand-ins below.

### The queue folder (`--queue`, created if missing)

| Path | Written by | Holds |
|---|---|---|
| `requested/<ticket>.json` | `enqueue` | `ticket`, `task`, `branch`, `commit`, `requested_at` |
| `approved/<ticket>.json` | `approve` (or the CTO) | the request, plus `approved_by`, `approved_at`; removed when the ticket lands or is ejected |
| `ejected/<ticket>.json` | `run` | the entry, plus `reason`, `failing` (test ids), `log` (the run's log folder), `tested_on` (the head) |
| `landed/<ticket>.json` | `run` | the entry, plus `merge` (its merge commit) and `record` (the record's path) |
| `records/<new head, 12 hex>.json` | `run` | the record of each advance (below) |
| `log/<stamp>/` | `run` | the run's logs: `queue.txt`, the test output and JUnit files, each selection's output |
| `run.lock` | `run` | the queue's own lock (`flock`), held for the whole of a run |

Ejection reasons: `conflict` (the commit does not merge cleanly onto the head and the tickets before it); `red` (the
ticket caused the failing tests named); `red: ... (fail closed)` (the whole batch: a red no single ticket explains, a
commit that brings another ticket's commits, or a candidate that cannot be isolated); `missing` and `already merged`
(the approved commit is not in the repository, or is on the head already).

### What `run` does

1. **One head, one batch, one merged result.** A clean clone at the integration head; each approved commit merged in
   turn, `--no-ff`, one merge commit per ticket (`Merge <branch> (<task>): merge queue`, trailers `Task: <task>` and
   `Role: orchestrator`, the repository's git identity or `orchestrator <orchestrator@localhost>`).
2. **Skipped only when the code is what the lead tested:** the merged tree equals an approved commit's tree, leaving
   out the governance paths (`select_tests.py`'s: briefs, prompts, the orchestration record, `.gov-runtime/`, and the
   test map's `record_only` places). The record's `skipped` says why, naming that commit and the paths left out.
3. **Otherwise one run:** the prepare command, each ticket's selection on its own merge, then the tests once on the
   union of the selected targets (one ticket's `pytest_options` added). **No full run:** the full suite runs only in
   the nightly (DEC-968, DEC-983); a selection whose `scope` is not `scoped` (`full`, `refused`, anything else) is
   never run, and the run stops (exit 4). **No test lock** (DEC-962 ended it): the default run's two test commands
   each take one of the machine's heavy-job slots (DEC-979 D1, below); the queue's own `run.lock` keeps one writer.
4. **Green:** the head is read again. If it moved, the same commits are merged onto the new head and tested again (3
   attempts, then exit 4). If not, the branch is fast-forwarded to the tested merge: `merge --ff-only` in the worktree
   that has it checked out, else the ref is moved only if it still holds the old head.
5. **Red:** each failing test is re-run alone once; a pass alone is a **flaky candidate** (named, decides nothing). A
   red alone is traced on the head without the batch **once each way** (Q-1, DEC-1050: its alone re-run with the
   batch, one alone run without it); a case the load-sensitive list names is traced interleaved, 3 rounds (and as many
   again unless decisive). Red there too, failing the same way, is **not the batch's** (`unowned`, DEC-968) and does
   not stop the advance.
6. **A red the batch caused:** one ticket is ejected. In a batch of several, each candidate is tried: the result is
   built without it and each red re-run alone `--rounds` times; green in every round means it explains the red. A test
   a ticket added is blamed on it only if red, every round, with that ticket alone merged. **Only the culprits are
   ejected;** the rest are merged again and get a run of their own. **Fail closed:** see the ejection reasons above.
7. **A step that cannot be done** (the clone, the prepare command, the selection, or a selection that is not
   `scoped`, a run that did not complete, the branch that cannot be moved): nothing advances, nothing is ejected for
   it, the entries stay approved.

### The record the close cites

`records/<new head, 12 hex>.json`, one per advance; the close cites it instead of running its own tests on the same
code. Fields: `head` (the new integration head, full id), `base` (the head before), `tickets` (`ticket`, `task`,
`commit`, `merge` each), `skipped` (null, or the reason), `selection` (`targets`, `core_changed`, `unplaced`), `counts`
(`tests`, `failures`, `errors`, `skipped` from the run's JUnit files; null when skipped), `flaky`, `unowned`, `ejected`
(the tickets sent back in this run, with their tests), `log`, `started`, `finished` (local time).

### Stand-ins (production defaults when not given)

- `--test-cmd "<cmd>"`: split like a shell would, run in the merged checkout with `--junitxml=<file>` and then the
  targets (or one test id for an alone re-run) appended. Exit 0 green; 1 red, failures named in the JUnit file; any
  other exit, or a missing or unreadable JUnit file, is a run that did not complete. **Default:** the close's form,
  one parallel run (`-n auto`, the serial-only plugin, `-o tmp_path_retention_policy=failed`), then the selected
  serial-only cases, with the checkout's own `src` on `PYTHONPATH`. Each of those two commands goes through a
  heavy-job slot: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh
  <the command>`, which waits for a slot, caps `-n auto` for it and exits with the command's own code (a missing
  wrapper is a run that did not complete). The single-process alone re-runs and traces take no slot. A stand-in
  replaces the whole run command, slot included, and is run as given.
- `--select-cmd "<cmd>"`: run in the merged checkout with `<checkout> <ticket> <task> --merge <merge commit>`
  appended; prints `select_tests.py`'s JSON. A non-zero exit or output that is not that JSON: the selection cannot be
  made. A `scope` other than `scoped` (`full`: the full suite runs only in the nightly): it is not run. Either way
  exit 4. **Default:** `select_tests.py` (DEC-953 item 4) with the checkout's `src` on `PYTHONPATH`.
- `--prepare-cmd "<cmd>"`: run in the merged checkout before the selection. **Default:** the store rebuild,
  `flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json`.

Every command runs with `PYTHONPATH=<checkout>/src` (DEC-732) and without `PYTEST_ADDOPTS` or `PYTEST_PLUGINS`.

### Exit codes of `run`

| Code | Meaning |
|---|---|
| 0 | every approved entry landed, or there were none |
| 3 | at least one ticket was ejected (others may have landed) |
| 4 | the run stopped on a step it could not do, or another run holds the lock; entries kept, the branch unmoved by that step; the reason on stderr |

### `--base`: attribution against a known state (DEC-988, DEC-989; the CTO's tools lane, reviewed 2026-11-01)

With `--base`, a red that fails alone is traced against that commit (never against code made by undoing merges). It
is cleared (`unowned`) only if it is red, in every traced round, failing the same way (the same exception types, a
bare `assert` counted as `AssertionError`; an unknown failure such as a timeout never matches) both at the baseline
and on the head without the batch. A red the baseline does not clear that the head without the batch has too, the
same way, came from a merge already on the branch since the baseline: the run stops (exit 4), nothing advances and
nobody is ejected, for the CTO to investigate at once (DEC-968). Every other red is the batch's, as before. The record
gains `trace_base`. The CTO runs the queue through `.gov-runtime/scratch/orchestrator/tools/land.py`, which passes
the baseline and closes each ticket that lands in the same step.

## The CTO's safety nets (DEC-991)

- `permission_request.py`: a Claude Code `PermissionRequest` hook (ACT-QUIET-DENY-1, in the owner's local settings).
  Between 02:00 and 07:30 it refuses, at once and with a message, a call that would ask the owner, and queues it in
  `.gov-runtime/scratch/orchestrator/log/approval-queue.jsonl` for the 09:00 package; by day it says nothing (the
  normal prompt appears). Any error inside the quiet hours still refuses.
- `deadman.py` (cron every 15 minutes, ACT-DEADMAN-1) and `win_toast.ps1`: alerts when the CTO session's last
  `assistant` entry is over 60 minutes old (2 hours in the quiet hours), naming a tool call left waiting. Channels:
  a Windows toast, a headless `claude -p` PushNotification, the pings log.
- Tests: `tests/unit/orchestration/test_cto_safety_nets.py`, `tests/unit/orchestration/test_merge_queue_base.py`.

### The queue's speed-ups (DEC-1001; reviewed 2026-11-01, PASS on the second round)

- **A records-only head move:** if `w2/integrate` moved during a run only by record files (an allowlist: `.md`, `.txt`,
  `.patch`, `.log`, `.jsonl` under the governance patterns, plus the test map's `record_only` places), the same commits
  are merged onto the new head and only the test map's `record_reading` and `every_close` lists re-run; a red there is
  accepted only if this batch already cleared it, with the same failure. Any other file in the move: the full re-run.
- **`--warm <dir>`:** the `merged` and `alt` clones are kept between runs (`warm.lock`, one run at a time). A clone is
  reused only if its origin is this repository, its `.git/config` and `.git/info/exclude` match the mark written when
  it was made, and the fetch, forced checkout, `clean -ffdxq` and scrub succeed; the scrub keeps only the rebuild's
  stores (`store.db*`, `codeintel/`, `query-vector-cache.db*`, `secrets-clean.json`) and removes test-installed hooks.
  Otherwise a fresh clone.
- **`--base-results <JUnit dir>` and `--base-run <run.txt>`:** a red is cleared from the nightly's own record when that
  run names the baseline head, lists the case red alone, and its failure kinds match; else today's trace. The check on
  the head without the batch always runs.
- **Rebuilds** (the default prepare command, and `close_build.py`): `.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh
  <tree>` takes a heavy-job slot and rebuilds with a lock of the tree's own (`GOV_REBUILD_LOCK`), so rebuilds of
  different trees run side by side, at most as many as there are slots.
- `land.py` passes `--warm` and the baseline nightly's record. Tests: `tests/unit/orchestration/test_merge_queue_speed.py`.

### No cold rebuild (DEC-1032 step (iv); for review)

`--integration-store <link>` (the link to the integration store's ready half, `~/gov-os-worktrees/W2-00-store`) turns
on three things; without it the queue works as before. `land.py` passes it, with `--nightly-log` and `--nightly-junit`.
- **Seed:** a clone with no `.gov-runtime/store.db` (a fresh `merged` or `alt`, or one replaced) is seeded before its
  first rebuild by `.gov-runtime/scratch/orchestrator/tools/seed_store.py`: where the clone's own `gov rebuild` offers
  `--seed` (W2-122), the rebuild gets `--seed <the ready half>`; otherwise the seeder copies the ready half's store
  (the whole store at the same commit, else its vectors only, where the code that makes a chunk's text is the same),
  so only chunks with no vector are embedded. A seed refused, or a seeder that cannot answer, is named in `queue.txt`
  and the rebuild runs as before. Every prepare is one line of the run's `prepares.jsonl`.
- **Promotion:** after a landing, when the `merged` clone's stores were rebuilt at exactly the landed commit (and the
  branch is still there), the standby half is checked out at that commit, seeded from the clone (`--replace`), rebuilt
  (nothing left to embed; the code index is made anew, since it holds its tree's absolute path) and the link moved,
  under the store's lock (`<link>.lock`, which `refresh_integration_store.sh` takes too). Otherwise (a skipped run, a
  moved head, the lock held, a failed step) the normal refresh is started apart, named.
- **The head without the batch is never rebuilt.** A red the baseline cleared, or one the batch may own, is first
  judged from the nightly of exactly that head (its `run.txt` names it, it has a verdict and JUnit files): green there
  means not on the head; red alone there with the same failure means on the head only for a red that would stop the
  queue, never to keep one cleared. Otherwise the case is re-run alone, `--rounds` rounds, as before, in a throwaway
  detached worktree of that head (`git worktree add --detach <work>/head-<id>-<n>`), made in the run's work folder,
  holding a copy of the integration store's stores (the whole store, the same commit: nothing embedded; copied under a
  shared hold of the store's lock, the only time it is held) and its code index made anew. Nothing ever runs in the
  integration store's own tree (review of 2026-11-02, A1, A2). The throwaway tree is checked before every case against
  its state when made (HEAD, changes, ignored files, its stores' stamps); a case that changed it gets a new one. The
  run removes its own throwaway worktrees (`git worktree remove --force`, only paths named `head-*` in its work
  folder); one a killed run left is removed at the next run's start. A store behind the head is refreshed first (its
  standby half, incrementally) while the branch is still at that head; if it still is not (or the branch moved on,
  the 2026-11-02 20:41 stop), the throwaway tree is rebuilt once, seeded from the integration store (never cold; Q-1).
  With no `--base`, the trace against the head without the batch runs there too. The `alt` clone is built only at the
  baseline (a red its nightly's record does not clear) and for the culprit search.
- Tests: `tests/unit/orchestration/test_merge_queue_seed.py`; the seeder's: `.gov-runtime/scratch/orchestrator/tools/test_seed_store.py`.
