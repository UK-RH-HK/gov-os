Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-1: engineer for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You implement ticket DAEO-cb2b (W2-121, part a): `gov dispatch tick` and `gov dispatch status`, the generic core of
the dispatcher. An independent test designer writes the acceptance tests (tests/acceptance/W2-121/) in parallel; you
never read them (the guard refuses the counterpart's work). Write your own unit tests as you go (test first).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121 |
| branch | w2/W2-121 |
| allowed paths | src/gov/dispatch/**, tests/unit/dispatch/** |
| ticket (read it first: KPI lines S1-S10 and F1, and the Interface section at its end) | /home/usain/gov-os-worktrees/W2-121/.tickets/DAEO-cb2b.md |
| the command convention (module, run(), EXIT_CODES, the reserved 0/1/2) | src/gov/cli/main.py (docstring) and an example: src/gov/launch/command.py, src/gov/plan/command.py |
| the gate (W2-20): reuse, never copy | src/gov/resources/config.py (gate.json, memory_floor_bytes, working_size_bytes), gate.py (`read`, `check_disk`), machine.py (memory, load, nproc, busy cores, processes; the GOV_RESOURCES_* planting variables), registry.py / slots.py (slots held, read-only) |
| the identity marker | src/gov/launch/launcher.py `build_lead_settings`, `LEAD_ROLES` |
| the ready list `gov plan --ready` writes (S10) | src/gov/plan/render.py `ready_text` |
| the reference (read for ideas; never a target, never copy its project-specific names) | /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/ (README.md, dispatcher.py, balancer.py) |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## What is in part a, and what is not
In: S1 (minus the installed host entry), S2, S3, S4, S5, S6 (the code generic and the refusals tested), S7, S8, S9,
S10, and F1's start half. Out (W2-121b/c/d or the CTO's ACT at the last close): landing (`land.txt` is only shown as
the queue), health checks, `gov watch`, `gov launch lead` itself, the host's cron entry, the switch-over.
Size: the ticket estimates about 500 lines for the part; keep it plain (standard library, git through subprocess with
a timeout; `yaml` as the repository already uses it). Split the module into a few files (config, state, readiness,
peaks, returns, status, command) rather than one long one.
Exit code 2 for a configuration error: 2 is reserved to the command line for usage errors; find the convention's
legal way (read `src/gov/cli/main.py`: e.g. `CHILD_EXIT_CODE`, or a usage error) and say which in the evidence.

## The interface (the ticket's Interface section, and the lead's reading where marked [lead])

The ticket's own words are the spec; where it is silent the lead's reading below holds for both the test designer and
the engineer, so both build to the same surface. A reading you think wrong: follow it, and name it in `unresolved`.

- **Commands.** `gov dispatch tick` and `gov dispatch status` (`--root <project>`, `--json` as every gov command), built
  as the command module `src/gov/dispatch/command.py` (the convention in `src/gov/cli/main.py`'s docstring: a
  positional action `tick` or `status`; no change to `src/gov/cli/`). Run in tests as
  `python3 -m gov.cli.main dispatch tick --root <planted project>` with `PYTHONPATH=<tree>/src`.
- **Exit codes (ticket).** 0 a pass done or nothing to do; 3 the gate or the forecast refused a start (named in the
  status); 4 the lock held (`tick.lock`; the second pass writes nothing); 2 a usage or configuration error.
- **State folder (ticket).** `<root>/.gov-runtime/dispatch/`: `ready.txt` (`<W2> <ticket id> <brief> <log name>` a line;
  `#` comments and blank lines ignored; one start per log name), `land.txt` and `land-done.txt` (part b's; part a only
  shows `land.txt`'s pending lines as the queue in the status), `started.txt`, `never-ran.txt`, `inbox/` and
  `inbox/read/` (one text item per event, first lines `log: <log name>`, `W2: <W2>`, `status: <status>`; an item is
  unread while it is in `inbox/`, read once moved to `inbox/read/`), `status.json` and `status.txt` (every pass),
  `peaks.json`, an `OFF` file (no pass runs, nothing written but the status may say OFF), `tick.lock`.
  [lead] More bookkeeping files in the same folder are allowed (e.g. `returns-seen.txt`, `escalated.txt`); the
  sessions' output goes to `<state>/logs/<log name>` and, when the session ends, `<state>/logs/<log name>.exit` holding
  its exit code (written by the dispatcher's own detached wrapper around the launch command). A session is finished
  when its `.exit` file exists.
- **Configuration (ticket + [lead]).** [lead] The file `<root>/governance/project/dispatch.yaml`, top-level mapping
  `dispatch:` (read by `gov.dispatch` itself, as `rebuild.yaml`'s own keys are; `src/gov/config/` is not changed).
  Ticket keys: `max_leads` (int), `stagger_s` (seconds between two starts), `cpu_band` (cores kept free), `nightly_hold`
  (`{from: "HH:MM", until: "HH:MM"}`; landings only, part b: read and shown, never holds a start), `landing_command`
  (part b: read, not run), `notifier_command` (an argv list; the item's path is appended as the last argument).
  [lead] Also: `integration_branch` (the branch the claim must be committed on), `worktrees_root` (a ticket's worktree is
  `<worktrees_root>/<W2>`; relative to the root or absolute), `briefs_dir` (a relative brief resolves against it;
  default `.gov-runtime/dispatch/briefs`), `launch_command` (an argv list; placeholders `{ticket}`, `{w2}`, `{brief}`,
  `{log}`; default `["gov", "launch", "lead", "{ticket}"]`; the brief goes to its stdin, its output to the log),
  `never_ran_after_s` (a start with no process and no `.exit` after this long is a start that never ran; default 300),
  `unread_escalate_s` (an inbox item unread this long raises one escalation; default 3600), `command_timeout_s` (every
  external command, git included, is limited to this; default 60; a timeout is a failed check naming the command,
  never a hung pass), `history` (the job-history file, relative to the root; default `.gov-runtime/dispatch/history.jsonl`),
  `job_markers` (a map kind -> a substring of a process's command line marking a running job of that kind, for the
  kinds other than `lead`), `probes_dir` (default `docs/probes`). A missing or malformed value the pass needs is a
  configuration error: exit 2, named. No default may name this repository's branches, paths or ticket ids (S6).
- **The gate (ticket: W2-20).** The memory floor (`memory_floor_bytes`) and working size (`working_size_bytes`) are read
  from W2-20's `gate.json` (`gov.resources.config`, `$HOME/.gov-os/machine/gate.json`); the gate's open/shut and disk
  from `gov.resources.gate` (`read(...)`, `check_disk(...)`). Planted with a tmp `HOME` and the `GOV_RESOURCES_*`
  variables documented in `src/gov/resources/machine.py` (`GOV_RESOURCES_MEMINFO`, `_LOADAVG`, `_NPROC`, `_BUSY_CORES`,
  `_DISK`, `_PROC`, ...). A shut gate or a full disk: no start, every entry named with the reason, exit 3.
- **The identity marker (ticket).** A running lead is a process whose command line carries `--settings` JSON with the
  lead's `GOV_TICKET` (and `GOV_ROLE` `orchestrator`), as `gov launch lead` sets it (`build_lead_settings` in
  `src/gov/launch/launcher.py`). [lead] Read from `/proc/<pid>/cmdline` under `GOV_RESOURCES_PROC` (planted: a folder
  `<proc>/<pid>/cmdline` with NUL-separated arguments). The sessions running are counted from these processes only,
  never from `started.txt` or the logs.
- **Readiness of an entry (ticket S2).** Started only when, in this order of checks, each failure skipping the entry with
  its reason named in the status: the line well formed (else `malformed`, the other lines still read); the log name not
  already in `started.txt`; the claim committed (`.tickets/<ticket id>.md` with `status: in_progress` at the tip of
  `integration_branch` and at the worktree's HEAD); the worktree clean (no tracked change); the brief complete (exists,
  not empty, no `@@`, no unfilled slot: an upper-case name in curly braces, regex `\{[A-Z][A-Z0-9_]*\}`); the ticket not running (no marker process for it); no unread return (no
  item in `inbox/` whose `W2:` is the entry's); [lead] a review launch (its brief holds a line `run: review`) refused
  when `<worktree>/<probes_dir>/<ticket id>/` holds two or more probe records (`*.md`): one owner item in the inbox
  (`status: owner`), once (S7); the gate and the disk open; `max_leads` not reached (running + started within
  `never_ran_after_s` with no process yet); `stagger_s` since the last start; room for the peak (below).
- **Peaks (ticket S3, [lead] the forms).** History lines (JSON) `{"kind": "<lead|rebuild|close|queue|check|...>",
  "at": "<ISO-8601>", "cpu": <cores>, "mem_bytes": <int>}`. `peaks.json`: each kind's peak CPU and memory (the maximum
  over the history) and the date it was computed, refreshed from the history when older than a day (or missing). The
  start of a lead is admitted only when MemAvailable − the gate's memory floor − the peaks ahead (for each running job:
  its kind's memory peak less what it holds now, never below 0) ≥ the lead kind's memory peak, and nproc − busy cores
  − `cpu_band` − the CPU peaks ahead ≥ the lead's CPU peak. A kind with no history counts the gate's working size as
  its memory peak. Refused: the entry named `no room for its peak` with the figures; exit 3. Memory admission at the
  launch itself stays W2-20's S6 (the launched `gov launch` passes the gate again).
- **At most one start a pass (ticket S2), first eligible entry in the list's order** (never the dispatcher's order);
  [lead] the log name is appended to `started.txt` (with its time) **before** the launch command is spawned, so a crash
  after a launch never starts that log again. The launch is detached (its own session) and the pass exits without
  waiting for it.
- **Returns (ticket S4, S8, S9).** Each finished session (`.exit` present) becomes one inbox item, once; a start that
  never ran (in `started.txt`, past `never_ran_after_s`, no marker process, no `.exit`) one item, once (listed in
  `never-ran.txt`); an item unread past `unread_escalate_s` runs `notifier_command` once for it. [lead] The item's
  `status:` is the return's `status:` line where the log holds one, else `exit <code>`; every commit id (7-40 hex) and
  path the return names on its `commits:` and `files_changed:` lines is resolved against git in the ticket's worktree;
  any that does not resolve is named on an `unresolved:` line in the item (none: no such line). Every wake the caller
  gets is such an item; no watcher process, no re-arm.
- **Status (ticket S5).** `status.json` and `status.txt` written whole (temp file + rename) every pass: the pass's time
  and outcome, the running sessions (from the processes), load, memory, the gate, the slots held (`gov.resources`
  registry, read-only), each kind's peak with its date, the peaks ahead, the queue (`land.txt`), the inbox (unread
  items), the started entry if any, each skipped entry with its reason. A pass that fails (an exception, a failed
  check it cannot pass over) writes `PASS FAILED <time>: <reason>` as the first line of `status.txt` and `"ok": false`
  with the reason in `status.json`, so no stale file looks current. `gov dispatch status` prints the status (the text,
  or the JSON under `--json`) and says when the last pass is older than three minutes.

## Rules
- Unit tests in tests/unit/dispatch/, everything planted under tmp_path (a git project with an integration branch and
  worktrees, a tmp HOME with gate.json, GOV_RESOURCES_* variables, a planted /proc folder, a stub launch command and a
  stub notifier); never the real HOME, ~/.claude, ~/gov-os-worktrees, a real session or the real crontab. Cover every
  refusal S6 names (uncommitted claim, shut gate, no room for a peak, running ticket, unread return, malformed list
  line, hung command, crash after a launch).
- Nothing project-specific in `src/gov/dispatch/`: no `w2/integrate`, `w2/W2-`, `/home/usain`, `gov-os-worktrees`,
  `Dynamic-Agentic-Engineering-OS`, `.gov-runtime/scratch/orchestrator`, `DAEO-xxxx` or `W2-<n>` in code, comments or
  defaults (the test designer greps for them). Generic examples in docstrings use `<W2>`-style placeholders.
- Before you return, run your suite and the neighbours you import, whole-folder form:
  `env HOME=/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-121/src python3 -m pytest <folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  for tests/unit/dispatch, tests/unit/resources (if present) and tests/unit/cli (if present); report each summary line.
- Commit in small batches (the lead merges the tests between them; never edit while a merge is announced), your paths
  only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: engineer" --trailer "Implements: DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003" -- <your paths>`
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/;
  literal paths as write targets. Never touch .gov-runtime/scratch/lead/.
- In the module docstring of `src/gov/dispatch/__init__.py`: each KPI line, what implements it (function names), and the
  lead's readings you followed or departed from.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (pytest summary lines per suite; the line count of src/gov/dispatch/) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
