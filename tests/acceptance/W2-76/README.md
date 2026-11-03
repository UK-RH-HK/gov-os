# W2-76 acceptance tests: the rebuild's timings, watchdog and machine lock

Ticket `DAEO-tgk2` (W2-76), profile STANDARD; DEC-939 item 2, rows W2-L451 (timings, watchdog) and W2-M408 (the
lock); DEC-866 (fail closed), DEC-889 (the same stores and digest), DEC-898 (scratch). Written by the independent
test designer (MR-3) before the implementation, from the ticket's KPI lines and the lead's design, through the public
interface only (DEC-462).

## How the tests run this worktree's code (DEC-732)

Every rebuild runs as `sys.executable -m gov.cli.main rebuild --json [--no-embeddings]` in a subprocess that keeps the
caller's `PYTHONPATH` (else this worktree's `src/`), never a bare `gov`. Run them as:

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src python3 -m pytest tests/acceptance/W2-76 -q -p no:cacheprovider

and show the code under test with:

    $ PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src python3 -c "import gov; print(gov.__file__)"
    /home/usain/gov-os-worktrees/W2-76/src/gov/__init__.py

## How the cases are built

- Each case builds its repositories from scratch in pytest's `tmp_path` (`git init`, a path map with an indexed and
  embedded `docs/**` and `src/**`, the kernel's `.gitleaks.toml`, three small files), and each carries a committed
  `governance/project/rebuild.yaml` whose `lock` is a temporary path under the case's own folder. **No case takes the
  machine's lock (`/tmp/gov-os-rebuild.lock`) or waits for the default 1800 s.** The threshold is 600 s, or 2 s in the
  watchdog cases.
- The outside programs, through `PATH` only: the code-graph tool is left off `PATH` (the code index reports itself
  not recreated, inside a sandbox and outside it alike, and no daemon starts); `OLLAMA_HOST` is a closed loopback port
  (the semantic stage reports itself as it does when no endpoint answers); `gitleaks` is the real one, or the planted
  slow stage: a stand-in first on `PATH` that sleeps on its first call and then hands on to the real one (the secrets
  filter, inside the lexical stage, runs long).
- A holder that is not the rebuild's ancestor is `w2_76_holder.py`, started as a sibling: it takes the flock, prints
  `held <pid>`, and lets go when the case creates its release file.
- The suite is skipped where `gitleaks` or `git` is not on `PATH`, and the wrapper cases where `flock(1)` or
  `timeout(1)` is not. The unwritable-folder case is skipped for root.
- Bounds: one rebuild may take up to 120 s (a wait, not asserted); a rebuild under its caller's hold must end within
  **120 s** (asserted: no deadlock); a refusal within 30 s. Each case runs in about 5 to 20 s here.

## KPI lines and their tests

| KPI line | Success tests | Failure tests | Expected red today |
|---|---|---|---|
| S1 every stage timed in output and record (W2-L451) | `test_w2_76_timings.py::test_every_stage_timed_in_output_and_record[no-embeddings,full]`; `::test_lock_part_of_a_rebuild_on_a_free_lock` (`total_s` from the lock taken) | F "a stage's time missing": `::test_a_stage_that_did_not_run_still_has_its_time`; the same parametrised case (every key present, a number) | `timing` holds only `lexical_s`: "stage times missing … ['record_s', 'secrets_s', …]"; "the semantic stage did not run; its time must be 0: {'lexical_s': …}"; "the result has no lock part" |
| S2 past the threshold: a live record, flagged slow, goes on | `test_w2_76_watchdog.py::test_a_slow_rebuild_records_what_it_waits_on_and_goes_on` | F "a slow rebuild with no record" and "a rebuild stopped by the watchdog": the same case; `::test_a_watchdog_fault_is_reported_and_the_rebuild_still_succeeds`; `::test_a_watchdog_fault_in_a_slow_rebuild_never_stops_it` | no record while it runs: "no record of this rebuild's processes while it ran"; "the fault is not in watchdog_faults"; "the slow rebuild was not flagged slow" |
| S3 one rebuild at a time on the machine; a waiter says what it waits for, its wait apart (W2-M408) | `test_w2_76_machine_lock.py::test_two_rebuilds_at_once_run_one_after_the_other`; `::test_a_waiting_rebuild_says_before_it_waits_what_it_waits_for`; `::test_a_rebuild_under_its_callers_hold_runs_at_once[flock,flock-timeout]` | F "two rebuilds running at once": `::test_two_rebuilds_at_once_run_one_after_the_other`; `::test_a_wrapped_and_an_unwrapped_rebuild_never_run_at_once` | no lock: "the result has no full lock part"; "no line naming the lock … while the rebuild waited" (after its 20 s look) |
| S4 fail closed (DEC-866) | `test_w2_76_fail_closed.py::test_a_lock_whose_folder_is_missing_refuses_and_builds_nothing`; `::test_a_lock_in_an_unwritable_folder_refuses_and_builds_nothing`; `::test_a_refused_rebuild_leaves_the_existing_stores_unchanged`; `::test_an_invalid_rebuild_yaml_refuses_and_builds_nothing[6 kinds]` | the same cases: a lock never ignored, nothing built | the settings are not read: "the rebuild was not refused with REBUILD_FAILED" |
| S5 the same stores and digest (DEC-889) | `test_w2_76_unchanged.py::test_two_full_rebuilds_of_the_same_tree_give_the_same_digest`; the slow case compares its digest and stores' statuses with an unslowed first rebuild of a twin of the same commit, and its digest and stores with an unslowed rebuild of the same tree after it; the fault case with a fault-free one | the same | **green today by design** (a regression guard: today's rebuild already gives one digest); it must stay green |

Red as seen on 2026-10-30 (this worktree at `135ae009`, sandboxed): **21 failed, 1 passed**, each failure for the
reason in the last column.

## What each case asserts

- **Timings.** `timing` has `record_s`, `lexical_s`, `secrets_s`, `semantic_s`, `codeintel_s`, `compaction_s`,
  `total_s`, each a non-negative number; no key of `timing` is a wait; `secrets_s <= lexical_s + codeintel_s` (with
  0.11 s per term for rounding); no stage longer than `total_s`; `total_s` no longer than the run; `semantic_s` is 0
  under `--no-embeddings` and its store entry says why. `slow: false`, `slow_after_s: 600`, `watchdog_faults: []`,
  `record: ".gov-runtime/rebuild/record.json"`. The record is whole JSON and holds `timing` equal to the output's,
  `lock` equal to the output's, `slow_after_s`, `slow`; no run of 13 or more hex digits in its text.
- **The lock part.** `lock` has `path` (the configured one), `wait_s` (0.0 on a free lock), `holder`,
  `held_by_caller` (false unwrapped), `taken_at`, `released_at` (UTC ISO 8601 with six-digit microseconds, `Z` or
  `+00:00`); `released_at - taken_at` is `total_s` within 2 s; the lock is free once the rebuild has ended.
- **Two at once.** Two repositories, one lock path, both slowed 4 s, started together: the later `taken_at` is not
  before the earlier `released_at`; the later's `wait_s >= 2`, larger than the earlier's; its `total_s` leaves its
  wait out; its standard error names the lock path and the first rebuild's pid (the launched process's pid).
- **Says before it waits.** A sibling holds the lock. Within 20 s, while the rebuild still runs, its standard error
  names the lock path, the holder's pid and its command line (`w2_76_holder`); the rebuild is still waiting 2.5 s
  later; once the holder lets go it succeeds, `wait_s >= 2`, `lock.holder` names the holder's pid.
- **The wrapper.** `flock <lock> python -m gov.cli.main rebuild …` and `flock <lock> timeout 100 python -m …` end
  within 120 s, exit 0, `held_by_caller: true`, `wait_s == 0.0`. A wrapped and an unwrapped rebuild on one lock path,
  started together, do not overlap.
- **The slow rebuild.** Threshold 2 s, the planted gitleaks sleeps 9 s. **The slowed rebuild is the first rebuild of
  its tree** (DEC-956 item 1, revised in run 2): the lexical index is incremental by blob, so a second rebuild of an
  indexed tree no longer hands the lexical stage's files to the secrets filter, and the sleep would land in the code
  index's secrets filter instead (run 1: `lexical_s` short, `secrets_s` and `codeintel_s` about 10.5 s). The case
  builds two projects of the same files in the same commit (fixed author and committer dates, so one hash, asserted;
  the digest holds the commits), the second in a box of its own (HOME, TMPDIR, tools). While the slowed rebuild runs,
  the case reads the record every 0.25 s and keeps the reads whose process list holds this rebuild's pid: there is at
  least one, and at least two distinct write times. Among them, the reads whose stage running names `lexical` or
  `secrets` (the slow stage) are at least one, with at least two distinct write times; the last of them holds every
  part below (the sleep is no longer in the last stage, so the record is rewritten after it: the last read of the
  whole run may be in a later stage). Standard error has exactly one line starting `rebuild: slow:` that contains
  `.gov-runtime/rebuild/record.json`; the result says `slow: true`, `slow_after_s: 2`; `secrets_s` and `lexical_s`
  are at least 8 s. The twin's first rebuild, unslowed and after the slowed one, gives the same digest and the same
  status for every store (two first rebuilds: neither can reuse the other's index; a store's reason may name a folder
  made from the project's path, the code-graph tool's home, so the twin is compared on status). A
  `.gov-runtime/rebuild/slow-*.json` with this rebuild's `lock.taken_at` exists and says `slow: true`; the final record
  says slow with the result's `timing`; no record read holds 13 or more hex digits. Last, an unslowed rebuild of the
  same tree gives the same digest and the same `stores`, every field (the same path; the record store the digest is
  taken from is loaded again in full from git on every rebuild, so this rebuild's being incremental leaves the digest
  comparison whole).
- **Watchdog faults.** `.gov-runtime/rebuild` is a file: the rebuild exits 0, `ok`, `watchdog_faults` non-empty, a
  standard-error line contains `watchdog` or `.gov-runtime/rebuild`; digest and stores equal a fault-free rebuild. The
  same fault in a slow rebuild: exit 0, `slow: true`, faults listed, the lexical store recreated.
- **Fail closed.** A missing lock folder, a folder of mode 0555, and (after a good rebuild) a lock moved to a missing
  folder: exit non-zero, `ok: false`, `error.code == "REBUILD_FAILED"`, the error names the lock's path, within 30 s;
  no store created (nothing under `.gov-runtime/` outside `.gov-runtime/rebuild/`), the missing folder not made, the
  existing stores byte for byte unchanged. Six invalid `rebuild.yaml` kinds (not YAML; a list; `slow_after_s: 0`;
  `slow_after_s: soon`; a relative lock; an empty lock): the same refusal, naming `rebuild.yaml` and, for a value,
  its key; nothing built.

## The record's parts

The design names the live record's parts in words. A case accepts the names below for each part, **the first being
the recommended one**; the implementation uses one of them:

| Part | Accepted keys (top level of the record) |
|---|---|
| the processes (a list of maps) | `processes`, `procs`, `process_tree` |
| each process: pid, parent, state, wait channel, command line | `pid`; `ppid` / `parent` / `parent_pid`; `state`; `wchan` / `wait_channel`; `cmdline` / `command_line` / `command` / `cmd` (at most 200 characters) |
| the load (numbers) | `load`, `loadavg`, `load_average` |
| the time of the write | `written_at`, `write_time`, `updated_at`, `time`, `at`, `now` |
| the stage running (names `lexical` or `secrets` here) | `stage_running`, `running`, `current_stage`, `running_stage` |
| how long it has run | a number inside that part when it is a map, else `stage_running_s`, `running_s`, `running_for_s`, `elapsed_s` |
| the stages done with their times (holds `record`) | `stages_done`, `done`, `completed`, `stages` |

The final record and the result share `timing`, `lock`, `slow`, `slow_after_s` by those names.

## The lock measurement (step 1 of the brief, inside this test designer's sandbox, 2026-10-30)

| Path or question | What was done | Result | Error |
|---|---|---|---|
| `/tmp/gov-os-rebuild.lock` read-only | `os.open(O_RDONLY)` | opened | — |
| `/tmp/gov-os-rebuild.lock` read-write | `os.open(O_RDWR)` | refused | `EROFS` (Read-only file system) |
| `/tmp/gov-os-rebuild.lock` take | one `LOCK_EX\|LOCK_NB` on the read-only descriptor, released at once | **succeeded** (no rebuild held it) | — ; `/proc/locks` had no line for its inode (08:30:427810) |
| `/tmp/gov-os-W2-76-held.lock` (held by the lead, pid 3152832) | open read-only; `LOCK_EX\|LOCK_NB` | opened; take **failed** | `EAGAIN` (= `EWOULDBLOCK`): the lock **is shared across the sandbox** |
| the same, `/proc/locks` | lines for inode 674643 | **none**: `/proc/locks` in the sandbox is empty (0 lines); pid 3152832 is not visible (`/proc/3152832` absent), so its cmdline cannot be read | — |
| `/dev/shm/gov-os-W2-76-held.lock` (held by the lead, pid 3152876) | open read-only | **absent** | `ENOENT`: the sandbox's `/dev/shm` is its own empty tmpfs (st_dev 95, against the lead's 65); a lock there is **not shared** |
| create `/tmp/gov-os-W2-76-new-probe.lock` | `O_CREAT\|O_EXCL` | refused | `EROFS` |
| create `/dev/shm/gov-os-W2-76-new-probe.lock` | `O_CREAT\|O_EXCL` | **created** (in the private tmpfs), then removed | — |
| a child `sleep 5`, `/proc/<pid>/stat` and `wchan` | `subprocess.Popen` | state `S`, wchan `hrtimer_nanosleep` (child pid 5) | — |
| `readlink /proc/self/ns/pid` | — | `pid:[4026532501]` (the lead's is `pid:[4026532219]`: a separate pid namespace; visible pids 1, 2, 6) | — |
| `flock <temp file> <script>`: inherited descriptor | `/proc/self/fd` | fd 3 points at the lock file | — |
| the same: `/proc/locks` holder | line for its inode | `FLOCK ADVISORY WRITE 3 08:30:869044 0 EOF`: pid 3 is the `flock` process, the script's parent (seen as an ancestor) | — |

What it means for the design: a lock file that already exists in the shared `/tmp` is reachable and shared from a
sandbox (it opens read-only, and `flock` on a read-only descriptor works and is seen outside); `/dev/shm` is not
shared; a sandboxed session cannot create a new file in `/tmp`; and a holder outside the sandbox's pid namespace is
not shown (`/proc/locks` lists only locks whose holder is in the namespace), so a sandboxed rebuild waiting on an
outside holder can only say that the holder is not known. These tests' holders are always in the test's own
namespace, so they are always shown.

## Not covered (named, not guessed)

- "The holder is not known" (a holder in another pid namespace): it cannot be built from inside a test without
  privileges; the measurement above shows when it happens.
- The default threshold (1800 s) and the default lock (the machine's): never exercised, by the brief's rule.
- The watchdog's 30 s rewrite period for thresholds above 30 s: a case would wait more than 30 s; the per-threshold
  period (2 s) is tested.

## KPI map after D-4's cut (DEC-1061)

Regenerated at the cut (tier 2: each KPI line's own case kept first, then at most 6 functions per line;
a parametrised function keeps its first row in the full run unless it is a line's own case). The rest stay
built in the opt-in suite `lifted` (`tests/optin-lifted*.txt`), run report-only with `--optin=lifted`.

| KPI line | case(s) in the full run | placed by |
|---|---|---|
| S1: gov rebuild's output and record give the time of each stage (the lexical, semantic and code-index stores, the secrets filter where it... | `test_w2_76_timings.py::test_every_stage_timed_in_output_and_record`, `test_w2_76_timings.py::test_lock_part_of_a_rebuild_on_a_free_lock`, `test_w2_76_timings.py::test_a_stage_that_did_not_run_still_has_its_time` | README |
| S2: A rebuild that passes 30 minutes (a value the project may set) writes, and keeps updating while it runs, a record of the stages done ... | `test_w2_76_watchdog.py::test_a_slow_rebuild_records_what_it_waits_on_and_goes_on`, `test_w2_76_watchdog.py::test_a_watchdog_fault_is_reported_and_the_rebuild_still_succeeds`, `test_w2_76_watchdog.py::test_a_watchdog_fault_in_a_slow_rebuild_never_stops_it` | README |
| S3: One store rebuild at a time on the machine: every gov rebuild, in every session on this machine (the main tree, a worktree, a clone, ... | `test_w2_76_machine_lock.py::test_two_rebuilds_at_once_run_one_after_the_other`, `test_w2_76_machine_lock.py::test_a_waiting_rebuild_says_before_it_waits_what_it_waits_for`, `test_w2_76_machine_lock.py::test_a_rebuild_under_its_callers_hold_runs_at_once` | README |
| S4: Fail closed: a lock it cannot create or take is never ignored; the rebuild waits, or refuses with the reason, and never runs beside a... | `test_w2_76_fail_closed.py::test_a_lock_whose_folder_is_missing_refuses_and_builds_nothing`, `test_w2_76_fail_closed.py::test_a_lock_in_an_unwritable_folder_refuses_and_builds_nothing`, `test_w2_76_fail_closed.py::test_a_refused_rebuild_leaves_the_existing_stores_unchanged` | README |
| S5: Everything a rebuild builds is unchanged: the same stores, the same digest on the same tree [DEC-889] | `test_w2_76_unchanged.py::test_two_full_rebuilds_of_the_same_tree_give_the_same_digest`, `test_w2_76_unchanged.py::test_two_full_rebuilds_of_the_same_tree_give_the_same_digest` | README |
| F1: Two rebuilds running at once on the machine; a rebuild stopped by the watchdog; a slow rebuild with no record; a stage's time missing. | `test_w2_76_timings.py::test_lock_part_of_a_rebuild_on_a_free_lock`, `test_w2_76_watchdog.py::test_a_watchdog_fault_is_reported_and_the_rebuild_still_succeeds` | by its words (every function of the suite kept) |
