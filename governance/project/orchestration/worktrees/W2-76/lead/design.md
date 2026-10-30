# W2-76 design (lead, run 1): gov rebuild timed, watched and locked

Base: `135ae00947cb` on `w2/W2-76`. Plan in behaviour, not code. Sources: DEC-939 item 2, DEC-866, DEC-889, DEC-898;
rows W2-M408, W2-L451. Allowed paths: `src/gov/rebuild/**`, `tests/unit/rebuild/test_w2_76*`.

## 1. The project's settings (the one interface for the threshold and the lock's path)

- An optional project file, `governance/project/rebuild.yaml`, read by `gov rebuild` itself from the tree it rebuilds:
  - `slow_after_s`: a positive number of seconds; default **1800** (30 minutes) when the file or the key is absent;
  - `lock`: an absolute path; default: the machine's rebuild lock (section 4).
- A file that is not valid YAML, is not a map, or holds a value of the wrong kind (a number that is not positive, a
  relative or empty path) refuses the rebuild with the reason (`REBUILD_FAILED`, naming the file and the key), and
  nothing is built. No environment variable changes either value.
- Tests set both through this file in a temporary repository: the threshold to seconds, the lock to a temporary
  path. This repository carries no such file: the defaults hold.

## 2. Stages timed, in the output and in the record

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

## 3. The watchdog

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

## 4. The machine's rebuild lock: its path (MEASURED: see the line below)

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

## 5. A waiting rebuild

- When the lock is held by another process, the rebuild says on stderr what it waits for before it waits:
  the lock's path and its holder (pid and command line) where the machine shows them, else "holder not known".
  (Measured on this machine: `/proc/locks` lists a holder as `FLOCK ADVISORY WRITE <pid> <maj:min>:<inode> 0 EOF`,
  with the major and minor numbers in hex, and lists each waiter on the next lines prefixed `->`: a waiter is not a
  holder. In a sandbox it lists only its own pid namespace's locks.)
- It waits without a time limit, then records its wait apart from its stages: in the result,
  `lock: {path, wait_s, holder, held_by_caller, taken_at, released_at}`, and the same in the record. `wait_s` is 0.0
  when the lock was free; `taken_at` and `released_at` are UTC ISO 8601 times with microseconds (`released_at` is
  the end of the rebuild's work, just before the lock goes), so two rebuilds' spans can be compared.

## 6. The interim wrapper, until the re-pin that carries this ticket

- The queue, the nightly and every lead keep running `flock /tmp/gov-os-rebuild.lock gov rebuild`; the pinned gov
  takes no lock of its own.
- **A rebuild started under the wrapper never waits on itself:** when the lock is already held by the rebuild's own
  caller (a process it descends from, as `flock <path> gov rebuild` and `flock <path> timeout <n> gov rebuild` are,
  or an open descriptor on the lock it inherited), it runs at once under that hold, takes no second lock, and says
  so (`held_by_caller: true`, wait 0.0).
- **An old wrapped rebuild and a new one never run at once:** both lock the same file. A new rebuild started while an
  old wrapped one runs waits for it (section 5); an old wrapper started while a new one runs waits in `flock`.

## 7. Fail closed

- A lock that cannot be opened or created (no such folder, no permission, a read-only file system) or that cannot be
  taken (an error other than "held by another") refuses the rebuild at once: `REBUILD_FAILED`, naming the lock's path
  and the reason; nothing is built, nothing is written. It never runs unlocked and never runs beside another.
- No watchdog path stops or fails a rebuild (section 3).

## 8. Nothing else changes

- The same stores, the same digest on the same tree, the same `--no-embeddings` behaviour, the same errors for the
  stores' own faults. The record lives under `.gov-runtime/` and is in no store and no digest.

## 9. Known consequence (reported, not a package)

- Once pinned, every `gov rebuild` on the machine takes the lock, including the rebuilds that existing suites run in
  temporary repositories (W1-27, W1-26, W2-50, W2-54, W2-68, W2-69, adopt): those cases queue behind each other and
  behind any real rebuild while it runs. Correct by the KPI; a cost in suite time under contention.
