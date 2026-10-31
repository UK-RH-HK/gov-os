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
  commit its lead tested, resolved to its full id (in `--repo`, default the current folder). A commit id that folder
  does not hold is kept as given and resolved by `run` in its own `--repo`; one that does not resolve there is
  ejected as `missing`. **A request alone never enters the queue.**
- `approve` moves the request to `approved/`, adding `approved_by` and `approved_at`. **The approval file is the
  entry:** until the three layers start, only the CTO approves (by `approve`, or by writing the file in the same
  form). A ticket with no request is refused (non-zero exit, nothing written).
- `run` processes every approved entry, in approval order, as one batch on one head.

`run`'s options: `--integration` (default `w2/integrate`); `--work` (the clean clones; default
`~/gov-os-runs/W2-00/merge-queue/`, each run's own folder removed when the run ends); `--rounds` (default 3, the
re-runs of each red alone); and the three stand-ins below.

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
   union of the selected targets (one ticket's `pytest_options` added). No full run (DEC-968).
4. **Green:** the head is read again. If it moved, the same commits are merged onto the new head and tested again (3
   attempts, then exit 4). If not, the branch is fast-forwarded to the tested merge: `merge --ff-only` in the worktree
   that has it checked out, else the ref is moved only if it still holds the old head.
5. **Red:** each failing test is re-run alone once; a pass alone is a **flaky candidate** (named, decides nothing). A
   red alone is traced on the head without the batch, interleaved, `--rounds` rounds (and as many again unless
   decisive): red there too is **not the batch's** (`unowned`, DEC-968) and does not stop the advance.
6. **A red the batch caused:** one ticket is ejected. In a batch of several, each candidate is tried: the result is
   built without it and each red re-run alone `--rounds` times; green in every round means it explains the red. A test
   a ticket added is blamed on it only if red, every round, with that ticket alone merged. **Only the culprits are
   ejected;** the rest are merged again and get a run of their own. **Fail closed:** see the ejection reasons above.
7. **A step that cannot be done** (the clone, the prepare command, the selection, a run that did not complete, the
   branch that cannot be moved): nothing advances, nothing is ejected for it, the entries stay approved.

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
  serial-only cases, with the checkout's own `src` on `PYTHONPATH`.
- `--select-cmd "<cmd>"`: run in the merged checkout with `<checkout> <ticket> <task> --merge <merge commit>`
  appended; prints `select_tests.py`'s JSON. A non-zero exit, a `refused` scope or output that is not that JSON: the
  selection cannot be made. **Default:** `select_tests.py` (DEC-953 item 4) with the checkout's `src` on `PYTHONPATH`.
- `--prepare-cmd "<cmd>"`: run in the merged checkout before the selection. **Default:** the store rebuild,
  `flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json`.

Every command runs with `PYTHONPATH=<checkout>/src` (DEC-732) and without `PYTEST_ADDOPTS` or `PYTEST_PLUGINS`.

### Exit codes of `run`

| Code | Meaning |
|---|---|
| 0 | every approved entry landed, or there were none |
| 3 | at least one ticket was ejected (others may have landed) |
| 4 | the run stopped on a step it could not do, or another run holds the lock; entries kept, the branch unmoved by that step; the reason on stderr |
