---
id: DAEO-fd0p
status: in_progress
deps: []
links: [DAEO-wnnz, DAEO-t8mp, DAEO-6lid]
created: 2026-11-11T01:20:19Z
type: task
priority: 1
assignee: engineer
external-ref: W2-160
tags: [wave-2, implementation, standard, after-the-lift, orchestration, launch]
wbs_id: W2-160
title: 'gov wait and the helper watch in the product: a bounded wait on a job''s exit file by pid, and an inbox item when a helper or a launched worker dies or goes silent (EMERGENCY-TOOLS-1 D3, D17; DEC-1079, DEC-1112 (3), DEC-1073 (4))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/wait/**
- src/gov/session_watch/helper_watch.py
- src/gov/check/commands.py  # the one line that records `wait` (the precedent: W2-20's `resources`)
- tests/unit/wait/**
- tests/unit/session_watch/test_w2_160*
- docs/changes/W2-160-evidence.md
- src/gov/session_watch/command.py  # the helper-watch action and its entry in the act and path list, about 20 lines (DEC-1153 (2))
- docs/probes/DAEO-fd0p/**  # the probe record (PKG-W2-160-IFACE-1, the CTO)
reads:
- src/gov/launch/**
- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md
needs:
- src/gov/check/commands.py
waits_on:
- ref: DAEO-6lid
  reason: 'W2-159 creates src/gov/session_watch/; the helper watch is one more module there'
kpis:
  success:
  - 'S1 `gov wait <exit-file> [<max-s>]` blocks until the exit file is non-empty or `<max-s>` seconds pass (default and ceiling 570, so a wait ends under a 600-second tool limit; a larger value is capped and says so), then prints the job''s log tail and its exit code; it waits on the file, never on a process name. Verify: a stand-in job writing its exit file after 2 seconds: its code is printed and returned; a never-written file at `<max-s>` 1: exit 124 "RUNNING"; a value of 9999 is capped at 570 with a line saying so [DEC-1079, DEC-1052]'
  - 'S2 When a pid file sits beside the exit file (`<base>.pid`, as `gov launch` writes it), the job''s liveness is asked of its pid alone: a job gone without its exit file ends the wait at once with exit 125 "GONE", never waits to the bound; an exit file holding no number, or a usage error, is exit 2. Verify: a stand-in job killed before it writes its exit file: exit 125 within one poll period; a second process of the same name left running does not keep the wait alive [DEC-1073 (4), DEC-1079]'
  - 'S3 The helper watch (`gov session-watch helper-watch`, one pass or a loop every 5 minutes, ending after a maximum of 24 hours with one "ended" line so the caller re-arms it) writes one inbox item, once per condition, when an in-session helper of the registered orchestrator session ends on an API or network error as its last entry, or is not finished and has written nothing for 30 minutes; and when a launched worker (found by its pid file) is gone without its exit file, or its exit file appeared with a non-zero code or an error in its result. The item names the helper or the worker''s log and its last line. Verify: planted helper transcripts and worker pid and exit files, one per condition, and a healthy one: one item each for the first four, none for the healthy one, none again on the next pass [DEC-1112 (3), DEC-1073 (4)]'
  - 'S4 The helper watch reads names, timestamps and error codes only, never a message''s text; it matches no process by name; it writes only the inbox, its own state file and its own log; only transcripts whose last entry is inside a window (default 24 hours) are looked at. Verify: a filesystem-spy and a text-canary test: a planted message text never appears in an item or the log; a search of the module for a process-name match finds none [DEC-1112 (3), DEC-1073 (4), DEC-495]'
  failure:
  - 'A wait that outlives its bound, or that waits for a job whose process is gone. Verify: S1''s never-written exit file at `<max-s>` 1 returns exit 124 within the bound, and S2''s killed stand-in job returns exit 125 within one poll period with a same-name process still running'
  - 'A process matched by name, or a message''s text copied into an item or a log. Verify: S4''s text-canary test (the planted message text found 0 times in items and log) and its search of the module for a process-name match (none found)'
  - 'The same condition written to the inbox twice. Verify: S3''s planted conditions run through two passes: the inbox holds one item per condition after the second pass, and none is added by it'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: STANDARD
sources:
- DEC-1079
- DEC-1052
- DEC-1073
- DEC-1112
- DEC-495
- DEC-1119
- DEC-1109
est_loc: 260
acceptance_tests:
  path: tests/acceptance/W2-160/
  author: 'independent-test-designer (MR-3), from these KPI lines; stand-in jobs, planted transcripts and pid files, never a live session'
track: A
list_rows: []
---
# W2-160 gov wait and the helper watch

Filed by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 rows D3 and D17; **after the lift**, not before EXAMIN's copy.

- **Problem.** The role templates name three scripts for the lead's loop: `lead_verify.sh`, `launch_worker.sh` and `wait_for.sh` (W2-128 TPL-3 S5; the facts file's `verify`, `launch` and `wait`). All three are the CTO's scratch tools. `gov launch` (W2-56) replaces the launch; the verify run is W2-115's (see the audit's proposed line); the wait has no product form, and neither has the helper watch, which exists because two helpers died of a network fault on 2026-11-10 and the CTO sat idle for 7 hours (`helper_watch.py`'s own header).
- **Approach.** `gov wait` is `wait_for.sh` as a command, with the exit codes the script gives; the helper watch is `helper_watch.py` as a module beside W2-159's. Alternative: put the wait in `gov launch` as `--wait` (rejected: a lead also waits on a verify run and a close).
- **Interface.** `gov wait <exit-file> [<max-s>]` exits with the job's code, 124 running, 125 gone, 2 usage. `gov session-watch helper-watch [--every 300] [--max 86400] [--stale-min 30] [--window-h 24] [--once]`. The inbox is the project's inbox folder.
- **Non-goals.** No change to `gov launch`'s pid and exit file names; the dead-man's switch (W3-P16) and the Stop checks (W2-159) are not here.
- **Rabbit holes.** Waiting on a process name (never; DEC-1073 (4)); a wait longer than the tool's own limit.

[DEC-1079, DEC-1112 (3), DEC-1073 (4), DEC-1119 (5)]

## Onto EXAMIN's path (the owner, DEC-1148 (2), item 4 (a1), 2026-11-12)

`gov wait` is the product command an adopted project's facts file names for `wait_for`; every brief's envelope names it (`brief.md:35`), so EXAMIN's copy builds no brief until this lands. Starts after W2-159 lands (the Stop checks it builds on); priority raised for the path.

## P-W2-160-1 decided (the owner, DEC-1153 (2), 2026-11-12) and PKG-W2-160-IFACE-1 (the CTO, delegated P2)

(a): `src/gov/session_watch/command.py` added for the `helper-watch` action (about 20 lines; nothing else in the file changes). The Interface takes the lead's I1 (`gov wait`) and I2 (the helper watch) as written; the lead's package, word for word:

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
