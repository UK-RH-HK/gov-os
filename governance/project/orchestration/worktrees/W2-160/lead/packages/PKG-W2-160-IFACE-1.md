task: DAEO-fd0p
# PKG-W2-160-IFACE-1: `gov session-watch helper-watch` needs a path the ticket does not allow, and the helper watch's files are not stated

## Question
The ticket's Interface names `gov session-watch helper-watch [...]`. `gov session-watch` is
`src/gov/session_watch/command.py` (W2-159). Its argparse accepts only `stop-check` (`add_arguments`, the `action`
choices), its `run` sends every call to the Stop checks, and its `ACT_PATHS` is `.gov-runtime/session-watch/**` alone.
A `helper-watch` action needs that file changed, and the file is not in allowed_paths (only `helper_watch.py` is).
The ticket also leaves out the product's paths and test hooks for the helper watch (I2 below), and the probe folder
`docs/probes/DAEO-fd0p/` is not in allowed_paths. Which of these does the CTO choose?

## Options
(a) **Widen and state (recommended).** Add `src/gov/session_watch/command.py` (the `helper-watch` action beside
    `stop-check`, the call to `helper_watch.run`, and `.gov-runtime/dispatch/inbox/**` added to `ACT_PATHS`) and
    `docs/probes/DAEO-fd0p/**` to allowed_paths, and put I1 and I2 below into the ticket's Interface. Cost: about 20
    lines in a W2-159 file. W2-159 is merged and closed, so no one else is editing it. One ticket edit. The test
    design starts as soon as the ticket is edited.
(b) **Keep the paths, change the command.** The helper watch becomes the module command
    `python3 -m gov.session_watch.helper_watch [...]`, so only `helper_watch.py` is touched. Cost: S3's command text
    changes. The watch runs outside `gov`'s act class and ACT_PATHS check. `gov --help` does not list it.
    `check/commands.py` gets a `RECORDED_MODULE_COMMANDS` line, which is not the line the ticket names. I1 and I2 are
    still needed.
(c) **Split.** Ship `gov wait` (S1, S2, F1) now and the helper watch (S3, S4) later. This needs a new ticket or a
    split, so the owner has to decide it (DEC-974). Cost: the wait reaches EXAMIN sooner; the helper watch waits for
    the owner.

## Recommendation
(a), confidence high. The ticket's own Interface and S3 name `gov session-watch helper-watch`. W2-20's `resources`
already writes its one inbox item under `.gov-runtime/dispatch/inbox/` and declares that path in its ACT_PATHS
(src/gov/resources/command.py:28, backstop.py:17-18, 126-127), so the helper watch can do the same.

## What it blocks
The whole ticket. The test designer needs the helper watch's seams (I2) and cannot write S3 or S4 without them.
`gov wait` (S1, S2) is on EXAMIN's path (DEC-1148 (2)). Under (a), the S1 and S2 tests can start the moment the
ticket is edited.

## Accept in one line
"PKG-W2-160-IFACE-1 (a): allowed_paths add src/gov/session_watch/command.py and docs/probes/DAEO-fd0p/**; the
Interface takes I1 and I2 as written."

## I1 `gov wait <exit-file> [<max-s>]` (src/gov/wait/command.py)
- `CLASS = "read"`, `CHILD_EXIT_CODE = True` (no envelope). It exits with the job's code % 256; 124 RUNNING; 125
  GONE; 2 for a usage error, a `<max-s>` that is not a number, or an exit file holding no number.
- `<base>` is the exit file's path less `.exit`. The pid file is `<base>.pid`. Liveness is checked by that pid alone:
  `os.kill(pid, 0)`, and a `/proc/<pid>/stat` state of `Z` counts as gone. It never matches a process by name and
  calls no `proc.sh`.
- Lines, in wait_for.sh's form with the `wait:` prefix: `wait: DONE exit <n> (<file>)`,
  `wait: RUNNING after <s>s: <file>`, `wait: GONE: the job's process (<pid>) exited without writing <file>`,
  `wait: <file> holds no exit code: '<text>'`, and on stderr `wait: <max-s> <v> capped at 570`.
- The tail comes from `GOV_WAIT_LOG`, else the first of `<base>.log`, `<base>.json`, `<base>.txt` that exists. For a
  JSON log it prints the last result object's `session_id`, `is_error` and `num_turns` and the end of its `result`.
  Then `<base>.summary`, if present.
- Test hooks (environment): `GOV_WAIT_EVERY` (poll period in seconds, default 5; fractions allowed) and
  `GOV_WAIT_LINES` (30).
- check/commands.py: `wait` is added to `RECORDED_GOV_COMMANDS`.

## I2 `gov session-watch helper-watch [--every 300] [--max 86400] [--stale-min 30] [--window-h 24] [--once] [--root <project>]` (src/gov/session_watch/helper_watch.py)
- Registered session: `<root>/.gov-runtime/session-watch/session.txt` (W2-159's `state.registered`). With no
  session file, it looks at no helpers.
- Helpers: `GOV_SESSION_WATCH_SUBAGENTS`, else
  `~/.claude/projects/<the root's absolute path, each character not a letter, digit or "-" as "-">/<session>/subagents/`;
  the files `agent-<id>.jsonl` and `agent-<id>.meta.json` (`finished`, `description`, `agentType`).
- Workers: W2-159's configuration `pid_globs` (default `.gov-runtime/**/*.pid`, relative to the root). Each pid file
  is `<base>.pid`, with `<base>.exit` and `<base>.json` (the log) beside it. Liveness is checked as in I1 (one shared
  function in gov.wait).
- Clock: `GOV_SESSION_WATCH_NOW` (epoch seconds, as W2-159). The watch starts at the clock's value. An exit file
  counts only if its mtime is at or after the start less `--every`.
- Conditions, once each, recorded in a state file that only grows (DEC-1140 (1)(a)): `api-error` (the last
  assistant/user/system entry has `isApiErrorMessage` or `apiError`); `stalled` (not `finished`, and no entry for
  `--stale-min` minutes); `worker gone` (no `.exit`, and the pid is gone); `worker ended with an error` (the exit code
  is not 0, or the last JSON object has `is_error` or `api_error_status`). A transcript whose last entry is older than
  `--window-h`, or a pid file whose mtime is older, is skipped.
- Writes: items in `<root>/.gov-runtime/dispatch/inbox/<UTC yyyymmdd-HHMMSS>-helper-watch[-<n>].txt` (opened with
  `x`, so no item overwrites another), each naming the helper's id or the worker's log and its last line; the state
  file `<root>/.gov-runtime/session-watch/helper-watch-state.json`; the log
  `<root>/.gov-runtime/session-watch/helper-watch.log` (one JSON line per pass: at, conditions, item names).
- Last line: names, entry types, timestamps, tool names, error codes, and the client's fixed synthetic API-error text
  only (`model == "<synthetic>"`); never a message's own text.
- Stdout: `HELPER_WATCH item <path>` for each item; when `--max` is reached,
  `HELPER_WATCH ended after <s> s; <n> item(s) written; re-arm it`. Exit 0. A W2-159 configuration error: exit 1,
  named.

## Facts for the record (no decision needed)
- S2 says "as `gov launch` writes it", but `gov launch` in this tree writes no `<base>.pid`. The `<base>.pid`,
  `<base>.exit` and `<base>.json` names are `launch_worker.sh`'s. The tests plant the files, so S2 can still be
  tested; the ticket's wording is wrong and should be noted.
