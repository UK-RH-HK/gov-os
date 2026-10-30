You are a fresh engineer. Ticket: DAEO-tgk2 (W2-76), profile STANDARD. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-76` on branch `w2/W2-76`. You implement the ticket until its acceptance tests pass.

## Step 0: the sandbox check (before any work; report it first)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-tgk2','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-tgk2`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-76` and `w2/W2-76`). If
anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. Return only after your commit exists. Commit your work before you run any
  long suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508).
  Never read `.claude/settings.json`, in this worktree or anywhere.
- **Protected material (DEC-820):** never read, print, search, diff or copy the held-out material's contents, and never
  type its path; never read or name the qualification oracle; never print a secret. Never write in
  `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **DEC-820 (c) and (d):** (c) you never read this ticket's acceptance tests: nothing under `tests/acceptance/W2-76/`,
  by any tool. You may run them and read their results (names, pass or fail, failure messages), never their source.
  (d) you never read the hidden half of any evaluation set.
- **DEC-849:** until W2-58 lands, the guard still refuses some reads (searches that start at the repository root,
  `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead.
  Count the refusals you met, in your return.
- **Never copy the repository** or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of
  it); copy single named files only, never `governance/project/`. Builder tests that need a repository build a
  temporary one. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing
  from it.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (`> "$OUT/x"`, `mkdir -p $D/t`),
  no here-document (`<<EOF`), no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with
  the Write and Edit tools at literal absolute paths, and run them. A refused form is not retried in another disguise.
- No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag.
  Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` gives commit hashes as 12 digits, never
  the full 40, and never names the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Scratch budget (DEC-898):** your share is 5 GB and 300,000 files and folders, outside the tracked tree. Keep
  pytest's own retention (never `--basetemp`), remove what you make as you go, and measure your temp folder
  (`du -s --inodes` and `du -sh`) before your suite runs and at the end; give the figures in `evidence`. Keep the
  temporary folder the launcher set; never set `TMPDIR` yourself.
- **Rebuilds:** never run `gov rebuild --no-embeddings` on this worktree, and never rebuild this worktree's or the main
  tree's stores at all: the lead does that, under the machine's lock. Rebuilds in temporary repositories (tests) are
  fine.
- **The nightly (DEC-933):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING`
  exists, run at most a single test file at a time; wait, checking each few minutes.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at
  random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src python3 -m gov.cli.main retrieve "<question>" --json`.
  A large question is taken in batches (`--batch-size`, then `--continue <token>`), never one giant query. A code
  question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted,
  never a load of the whole graph. Drop unread any result under `tests/acceptance/W2-76/`.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-tgk2.md` (read-only): its KPI lines and `allowed_paths`.
- Its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-76"); rows W2-M408 and W2-L451 in `docs/plan/WAVE_2_LIST.md`.
- In `docs/DECISION_REGISTER.md`: DEC-939 (item 2 and its "How it is applied"), DEC-866, DEC-889, DEC-898, DEC-135.
- The code the ticket touches: `src/gov/rebuild/command.py` (`run`, its stages, `_compact`), and, read-only, the code
  it calls: `src/gov/store/`, `src/gov/retrieval/lexical.py`, `src/gov/retrieval/semantic.py`,
  `src/gov/codeintel/__init__.py`, `src/gov/secrets/__init__.py`, and `src/gov/cli/main.py` for how a command's
  result and errors are shown. The existing rebuild suites (`tests/acceptance/W1-27/` and the others that run
  `gov rebuild`) you may read; they must stay green.

## The behaviour to build (the lead's design; the interface is fixed here)

### 1. The project's settings (the one interface for the threshold and the lock's path)

- An optional project file, `governance/project/rebuild.yaml`, read by `gov rebuild` itself from the tree it rebuilds:
  - `slow_after_s`: a positive number of seconds; default **1800** (30 minutes) when the file or the key is absent;
  - `lock`: an absolute path; default: the machine's rebuild lock (section 4).
- A file that is not valid YAML, is not a map, or holds a value of the wrong kind (a number that is not positive, a
  relative or empty path) refuses the rebuild with the reason (`REBUILD_FAILED`, naming the file and the key), and
  nothing is built. No environment variable changes either value.
- Tests set both through this file in a temporary repository: the threshold to seconds, the lock to a temporary
  path. This repository carries no such file: the defaults hold.

### 2. Stages timed, in the output and in the record

- Stages, each timed by the rebuild around its call (the stores', code index's and secrets filter's code is not
  edited): the record store load; the lexical index; the semantic index; the code index; the compaction (both
  calls together: the record store and query vectors, and the code tool's home).
- The secrets filter runs inside the lexical and the code-index stages. Its wall time is given apart, and is never
  more than the two stages that ran it (it is nested in them, not added to them). Where it could not be timed,
  the output says so with the reason; it is never left out or given as a silent 0.
- A stage that did not run (no path map, `--no-embeddings`, no code tool) still has its time, as 0, and its store
  entry says why, as today.
- `--json` result, `timing`: `record_s`, `lexical_s`, `secrets_s`, `semantic_s`, `codeintel_s`, `compaction_s`
  (seconds, one decimal) and `total_s` (from the lock taken to the end). The lock's wait is **not** in `timing`
  (section 5). Every other key of today's result is kept as it is.
- The record: `.gov-runtime/rebuild/record.json` in the tree rebuilt, replaced whole (never half-written) at the end
  of every rebuild, with each stage's time, `total_s`, the lock part (section 5), the threshold and whether the
  rebuild was slow. The result names it (`record`, project-relative). A slow rebuild's record is also kept as
  `.gov-runtime/rebuild/slow-<UTC start, YYYYmmddTHHMMSSZ>.json`, so the next rebuild does not erase it.
- Nothing in a record breaks row W2-L423's rule: every run of 13 or more hexadecimal digits in a command line is cut
  to its first 12, and each command line is cut to 200 characters.

### 3. The watchdog

- Starts when the rebuild has its lock; the threshold counts the rebuild's own time, not its lock wait.
- Past the threshold, the record is written at once and then rewritten while the rebuild runs, at least every
  30 s and at least once per threshold when the threshold is shorter. Each write holds:
  - the stages done, each with its time; the stage running and how long it has run;
  - each of the rebuild's processes (the rebuild itself and every descendant): pid, parent, state, wait channel,
    command line (cut as above); the load (`/proc/loadavg`); the time of the write.
- The record's names (fixed by the lead, 14:30): top level `timing`, `lock`, `slow`, `slow_after_s` (as in the
  result), `stages_done` (each stage done, with its time; the record store is `record`), `stage_running` (the stage
  now running: `record`, `lexical`, `secrets`, `semantic`, `codeintel` or `compaction`, the innermost one) and
  `stage_running_s`, `processes` (a list of maps: `pid`, `ppid`, `state`, `wchan`, `cmdline`), `load` (the three
  numbers), `written_at` (UTC ISO 8601 with microseconds).
- The rebuild flags itself slow in its output: one line on stderr when it passes the threshold
  (`rebuild: slow: past <n> s ...`, naming the record), and in the result `slow: true` with `slow_after_s`.
  A rebuild under the threshold says `slow: false`.
- It goes on to the end. The watchdog never stops, kills, signals or fails a rebuild. A fault of the watchdog itself
  (a record it cannot write, a process it cannot read) is reported: one stderr line, and in the result
  `watchdog_faults` (a list, empty when none). A fault is never fatal and never changes the exit code.

### 4. The machine's rebuild lock: its path (MEASURED: see the line below)

- **Lock line (settled 2026-10-30 14:25 from the sandboxed test designer's measurement, session de62ac96):
  `/tmp/gov-os-rebuild.lock`, the wrapper's own path.** Measured inside a launched sandbox: the file opens read-only
  (read-write: EROFS); a non-blocking exclusive `flock` on that read-only descriptor fails with EAGAIN while the lead
  holds the same kind of file in `/tmp` outside the sandbox, so the lock is shared across the sandbox boundary; a new
  file cannot be created in `/tmp` (EROFS), so a sandboxed rebuild relies on the file existing (it does, and every
  wrapper and every unsandboxed rebuild creates it when absent). `/dev/shm` is not shared (a private tmpfs per
  sandbox) and is ruled out. No change to `src/gov/launch/**` is needed.
- Also measured: the sandbox is its own pid namespace; its `/proc/locks` shows only its own namespace's locks (an
  outside holder is not shown: a sandboxed waiter says "holder not known"); a lock taken by `flock` inside the
  sandbox shows there with its pid, and the child inherits the descriptor (fd 3); `/proc/<pid>/wchan` is readable.
- The lock is an advisory whole-file lock (`flock`) on that file, taken exclusively before anything is read or
  written, held to the end, and released by the process ending (a crashed rebuild leaves no stale lock).
- The file is created when absent; where it cannot be created, an existing one is opened read-only.

### 5. A waiting rebuild

- When the lock is held by another process, the rebuild says on stderr what it waits for before it waits:
  the lock's path and its holder (pid and command line) where the machine shows them, else "holder not known".
  (Measured on this machine: `/proc/locks` lists a holder as `FLOCK ADVISORY WRITE <pid> <maj:min>:<inode> 0 EOF`,
  with the major and minor numbers in hex, and lists each waiter on the next lines prefixed `->`: a waiter is not a
  holder. In a sandbox it lists only its own pid namespace's locks.)
- It waits without a time limit, then records its wait apart from its stages: in the result,
  `lock: {path, wait_s, holder, held_by_caller, taken_at, released_at}`, and the same in the record. `wait_s` is 0.0
  when the lock was free; `taken_at` and `released_at` are UTC ISO 8601 times with microseconds (`released_at` is
  the end of the rebuild's work, just before the lock goes), so two rebuilds' spans can be compared.

### 6. The interim wrapper, until the re-pin that carries this ticket

- The queue, the nightly and every lead keep running `flock /tmp/gov-os-rebuild.lock gov rebuild`; the pinned gov
  takes no lock of its own.
- **A rebuild started under the wrapper never waits on itself:** when the lock is already held by the rebuild's own
  caller (a process it descends from, as `flock <path> gov rebuild` and `flock <path> timeout <n> gov rebuild` are,
  or an open descriptor on the lock it inherited), it runs at once under that hold, takes no second lock, and says
  so (`held_by_caller: true`, wait 0.0).
- **An old wrapped rebuild and a new one never run at once:** both lock the same file. A new rebuild started while an
  old wrapped one runs waits for it (section 5); an old wrapper started while a new one runs waits in `flock`.

### 7. Fail closed

- A lock that cannot be opened or created (no such folder, no permission, a read-only file system) or that cannot be
  taken (an error other than "held by another") refuses the rebuild at once: `REBUILD_FAILED`, naming the lock's path
  and the reason; nothing is built, nothing is written. It never runs unlocked and never runs beside another.
- No watchdog path stops or fails a rebuild (section 3).

### 8. Nothing else changes

- The same stores, the same digest on the same tree, the same `--no-embeddings` behaviour, the same errors for the
  stores' own faults. The record lives under `.gov-runtime/` and is in no store and no digest.

### 9. Known consequence (reported, not a package)

- Once pinned, every `gov rebuild` on the machine takes the lock, including the rebuilds that existing suites run in
  temporary repositories (W1-27, W1-26, W2-50, W2-54, W2-68, W2-69, adopt): those cases queue behind each other and
  behind any real rebuild while it runs. Correct by the KPI; a cost in suite time under contention.

## What you write

- Only inside `src/gov/rebuild/**` and new files `tests/unit/rebuild/test_w2_76*` (builder tests, regression evidence
  only). Nothing in `src/gov/store/**`, `src/gov/codeintel/**`, `src/gov/secrets/**`, `src/gov/retrieval/**`,
  `src/gov/launch/**`, `src/gov/close/**` or any other ticket's files: every stage is timed from the rebuild's side.
  If the design needs a change there, return a package.
- Leave how the rebuild's git calls build their environment as it stands.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never
  worked around.
- Proportion (DEC-135): no code for edge cases beyond the design and the KPI lines. Never make a lock or watchdog
  decision fail open: no watchdog path stops or fails a rebuild; no lock fault passes silently; a rebuild that could
  not take the lock never runs.
- Run, in the foreground, each to its end, never with `-x`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src python3 -m pytest tests/acceptance/W2-76 -q -p no:cacheprovider`
  until it passes; then your builder tests; then the existing rebuild suites
  (`tests/acceptance/W1-27`, `tests/unit/rebuild`), which must stay green. Inside your sandbox the code-graph
  folder `/tmp/gov-cbm-<uid>` is read-only, so a case that needs the code index really built fails there for that
  reason alone: name such cases with their message; the lead runs them outside the sandbox. Once your code is in,
  every rebuild those suites run in a temporary repository takes the machine's real lock (`/tmp/gov-os-rebuild.lock`)
  and may wait behind a real rebuild on this machine: that is the design, not a fault; note any such wait.

## Commit

Commit only your paths, with the trailers in the final block:

    git commit -m "W2-76: gov rebuild timed per stage, watched past its threshold, and locked machine-wide" --trailer "Task: DAEO-tgk2" --trailer "Role: engineer" --trailer "Implements: DEC-939" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

After the twelve fields: the sandbox check (step 0), your commit's hash (12 digits), the files changed with lines
added and removed, the tests you ran with their results, the guard refusals you met, whether you used `gov retrieve`,
and your scratch figures.
Refused twice for the same call: stop and say so.
