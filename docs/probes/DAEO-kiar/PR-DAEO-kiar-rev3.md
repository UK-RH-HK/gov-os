---
type: probe
task: DAEO-kiar
reviewer_session: 5c8892c4-424d-4abf-bfeb-ec237b997026
implementer_session: dea5d786-f092-4cd6-ad15-b42d329b5150
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: a4aa7d7565c1f7b7538c89b01d3fe990f21a0583
---

# Probe record: W2-107 (DAEO-kiar), round 3 (run 2 and the counts line, DEC-975)

## Summary
A fresh, read-only review of W2-107's final head `a4aa7d7565c1`, judging only what changed since `654fd0e3e26c` (DEC-975 item 1):
- the builder tests' move (P-W2-107-1 (a));
- W1-16's revised home case (P-W2-107-2 (a));
- the rebuild's counts line (P-W2-107-3);
- how the nightly's full-scan line (`2e2e6c8a0919` on `w2/integrate`) meets the code.

`src/gov/secrets/` is unchanged since `654fd0e3e26c`. `src/gov/rebuild/command.py` differs from `w2/integrate` (`ed7d3bca24ab`) by exactly the counts line's six lines.

How the probes ran:
- Every probe ran this worktree's `src/` (`gov.__file__` = `/home/usain/gov-os-worktrees/W2-107/src/gov/__init__.py`) and real gitleaks 8.30.1.
- Each ran in a throwaway git project in the reviewer's temp folder: 7 tracked files, one of them a canary built from parts at run time.
- Each probe had its own scan cache by `GOV_SECRETS_CACHE` and its own rebuild lock. The machine's cache was never touched.
- No suite was run (collection only). The guard refused once (a write path held in a shell variable; redone with literal paths). The removal of the reviewer's temp folder was not granted.

No finding is both "yes" and "fails open" or "loses work". F1 is a row for the Wave 3 hardening pass; it sharpens run 1's R-D. F2 and F3 are "other". Classification (DEC-809): one row (F1), two others (F2, F3), none round-justifying. Judgement: pass.

## What was probed and found sound

### The move (P-W2-107-1 (a))
- **Renames only.** Two renames at 100 % similarity, nothing else in that commit (`7853b7799284`).
- **No fixture or import lost.** The old folder held only the two files: no `__init__.py`, no conftest. Both locations inherit only `tests/conftest.py`. `parents[3]` reaches the same root, and the files hold no string tied to their folder.
- **Still collected.** All 10 + 7 functions collect (13 + 11 ids), with the new record test (2): 67 in `tests/unit/secrets_check/`, no errors.
- **No acceptance test changed.** `tests/acceptance/W2-107/` has no diff since `654fd0e3e26c`.

### W1-16's revised case (P-W2-107-2 (a))
- **The exclusion is exact.** It matches by relative path, and only in the place that is the child's HOME (or a folder holding it).
- **Synthetic sandbox, run through the case's own helpers:**
  - Under HOME, only `.cache/gov-os/secrets-scan.sqlite` was left out. Five near-misses still fail the case: another SQLite file beside it, a `.bak` copy, the same name one folder down, a `.db` name, a `.sqlite-wal.db` name.
  - The same name under TMPDIR or elsewhere still fails.
- **`-wal` and `-shm` lower nothing.** They are not index files by `index_files`' own test, so leaving them out changes nothing.
- **Nothing else lowered.** The repository checks, the other places, `.codebase-memory` and the status check are unchanged. The commit (`50f10962609a`) is the test designer's and carries `Rewrite-Reason: DEC-967`.

### The counts line (P-W2-107-3)
- **Keys kept, in their order.** The result is: digest, store, stores, compaction, **secrets_counts**, timing, lock, slow, slow_after_s, record, watchdog_faults.
  - Every key of W2-76's result is kept in its order; one key is added before `timing`.
  - `stores` is untouched, so two rebuilds' `stores` still compare equal.
  - W2-76's record file is unchanged.
  - The result is printed by `json.dumps` with no schema; `gov adopt` and the close batch read only `stores` and `digest`.
- **No new failure or hang.**
  - `gov.secrets` was already imported on every rebuild path, through the lexical module.
  - `scan_counts()` copies two fixed dicts under a lock held for one increment at a time.
  - With no path map, the rebuild succeeds with zero counts and the same statuses as before.
- **It counts what it says.** Each figure is content scanned / remembered, then names scanned / remembered:

  | Run | Content | Names |
  |---|---|---|
  | First rebuild, cache on | 8 / 6 | 6 / 0 |
  | Second rebuild, unchanged | 1 / 6 | 0 / 6 |
  | Full scan, same tree | 7 / 0 | 6 / 0 |
  | Full scan, fresh tree, empty cache | 14 / 0 | 6 / 0 |
  | Ordinary rebuild after that full scan | 1 / 6 | 0 / 6 |
  | Cache off (`GOV_SECRETS_CACHE` empty) | 7 / 0 | 6 / 0 |
  | Two rebuilds in one process (each its own difference) | 8 / 6, then 1 / 6 | 6 / 0, then 0 / 6 |

  With the cache off, the cache file was not written. In the one-process run, the process totals were cumulative while each result was its own difference.
- **No stage runs the filter in a child process.**
  - The lexical and code-index stages call it in-process (threads only).
  - The semantic stage only re-runs the lexical refresh in-process; it asks nothing for unchanged blobs.
  - The children (ollama, the rerank worker, the code-index tool) never run the filter, and the record stage does not run it.
  - So the window, from after the record stage to after the code index, covers every call.
- **The code-index tool itself could not start in this sandbox** (`/tmp` is read-only). Its filter calls come before the tool, so the counts were complete.

### The full scan as the nightly sets it
- The nightly sets `GOV_SECRETS_FULL_SCAN=1` on the rebuild's line only, with no `GOV_SECRETS_CACHE`, so the default record under HOME. The rebuild runs the filter in-process, so the variable reaches it.
- **It reads nothing from the cache.** Every text was scanned and none answered from the cache, whether or not a stale row was present.
- **It refreshes the cache.** It writes clean verdicts, and the next ordinary rebuild was answered from them.
- **No value is silently ignored.** Only unset, empty or exactly `0` switches it off. Every other value scans in full, including `false`, `no`, `off`, `00` and ` 0`. That costs time but never fails open.

### Run 1's rows
None is made worse by run 2. F1 sharpens R-D and the extended-rule-file row.

## Findings (each with its two lines)

### F1: the nightly's full scan answers its own rebuild correctly but leaves a stale clean verdict in place
- **What was done.** In a copy of my own cache I planted, by hand, a clean verdict for the canary's content under the current engine. It stands for a verdict the filter would no longer give: run 1's R-D case, or the extended rule file. I then rebuilt a fresh project exactly as the nightly does, then rebuilt another fresh project ordinarily over the same cache.
- **What happened.**
  - The full-scan rebuild read nothing (content 14 / 0, names 6 / 0) and kept the canary out of every store.
  - The stale row was still there afterwards. Nothing removes the clean row of a text found to hold a secret, and nothing says a remembered verdict was contradicted.
  - The ordinary rebuild then answered the canary clean from that row (content 0 scanned, 14 remembered). The canary reached `.gov-runtime/store.db` and the code index's staged copy.
- **What should have happened.** KPI 6 as written ("reads nothing … and refreshes it") is met. If DEC-966's "the nightly scans every file in full" is meant as the net that corrects the cache, the full scan should also drop a contradicted clean row and say so in the nightly's record.
- **Severity:** low, latent. **Reproduced:** yes, with a hand-planted row.
- Ordinary work: no, because a stale clean row needs a change that alters a verdict while leaving the engine's fingerprint as it was (run 1's R-D: the call's flags; or the extended rule file); I planted it by hand. Run 2 does not make it worse: before the nightly's line nothing ran a full scan at all.
- Consequence: fails open (latent: every rebuild but the nightly's, once such a row exists)

### F2: the counts are in the command's result, not in W2-76's record file
- **What was done.** I rebuilt and read both the JSON result and `.gov-runtime/rebuild/record.json`.
- **What happened.** `secrets_counts` is in the result, which the nightly keeps as `rebuild.json`. W2-76's record file carries no counts, and neither does a slow rebuild's `slow-*.json`. `watch.py` is unchanged, as the ticket's "At merge" paragraph requires.
- **What should have happened.** The "At merge" paragraph ("the rebuild's JSON record") is met by the result. KPI 7 says "the rebuild's record"; a reader who looks in W2-76's record file will not find the counts there. This is wording only.
- **Severity:** info. **Reproduced:** yes.
- Ordinary work: yes, because a reader may look in W2-76's record file.
- Consequence: other (the counts are read from the command's output)

### F3: the move deleted two files at a path the ticket's list no longer named
- **What was done.** I compared the ticket's `allowed_paths` at `654fd0e3e26c`, `cc2632efbc8a`, `7853b7799284` and `138a224f8157` with the files the move touches.
- **What happened.** `cc2632efbc8a` replaced `tests/unit/secrets/test_w2_107*` with `tests/unit/secrets_check/test_w2_107*` before the move. So the engineer's rename deleted two files at a path the list no longer named. DEC-970 ordered exactly this move, and both files arrive byte for byte.
- **What should have happened.** The list keeps the old glob until the move lands, or the decision names the deletion.
- **Severity:** info. **Reproduced:** yes, from git.
- Ordinary work: yes, because a decided move of a ticket's own files does this.
- Consequence: other (a record slip; nothing lost)
