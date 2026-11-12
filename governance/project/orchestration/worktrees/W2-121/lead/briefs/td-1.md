# Brief td-1: independent test designer for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-cb2b (W2-121, part a: `gov dispatch tick` and
`gov dispatch status`). You write the acceptance tests from the ticket's KPI lines and its Interface section, before
the engineer's code exists. You never read the engineer's work on this ticket (branch w2/W2-121 after this brief,
`src/gov/dispatch/**`, `tests/unit/dispatch/**`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121-tests |
| branch | w2/W2-121-tests |
| your allowed paths | tests/acceptance/W2-121/** |
| ticket (read it first: KPI lines S1-S10 and F1 with their Verify, and the Interface section at its end) | /home/usain/gov-os-worktrees/W2-121-tests/.tickets/DAEO-cb2b.md |
| the command convention (how `gov <command>` is built, exit codes, the envelope) | src/gov/cli/main.py (docstring) |
| the gate you plant (read its docstrings: the planting variables, gate.json's form) | src/gov/resources/machine.py, src/gov/resources/config.py, src/gov/resources/gate.py |
| the lead's settings (the identity marker) | src/gov/launch/launcher.py `build_lead_settings` |
| the ready list `gov plan --ready` writes (S10) | src/gov/plan/render.py `ready_text` |
| the model, as a description only (read its README; not its code) | /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/README.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## What is in part a, and what is not
In: S1 (minus the installed host entry), S2, S3, S4, S5, S6 (the grep and the planted refusals; not the review record
or the switch-over), S7, S8 (as passes and items; not the restart of a real host), S9, S10, and F1's start half.
Out (other parts or the CTO's ACT at the last close; do not test): the host's cron or service entry, the switch-over
of this repository's dispatcher, landings (`land.txt` claimed, `land-done.txt`, the landing command, F1's landing
half), health checks, `gov watch`, `gov launch lead` itself.

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
- One test (or more) per KPI line and per refusal S6 names: an uncommitted claim, a shut gate, no room for a peak, a
  running ticket, an unread return, a malformed list line, a hung command (a stub `git` or launch command that sleeps
  past a small `command_timeout_s`: the pass ends in bounded time, the check named as failed), a crash after a launch
  (a pass killed or failing after the launch command ran: the next pass does not start that log again). Name each test
  after its KPI id (`test_s2_...`, `test_f1_...`).
- S6's grep: the dispatcher code (`src/gov/dispatch/`) holds none of this repository's branch names (`w2/integrate`,
  `w2/W2-`), its paths (`/home/usain`, `gov-os-worktrees`, `Dynamic-Agentic-Engineering-OS`,
  `.gov-runtime/scratch/orchestrator`) or ticket ids (`DAEO-[0-9a-z]{4}`, `W2-[0-9]+`). It is red now (no folder):
  make the test fail, not skip, when the folder is missing.
- Everything planted under pytest's tmp_path: a project root that is a git repository with an integration branch and
  a worktree per W2 (git worktree add), `.tickets/<id>.md` with a claim, briefs, a `dispatch.yaml`, a tmp `HOME` with
  `.gov-os/machine/gate.json` (use `gov.resources.config.template()` and write it, or write the values its docstring
  names), the `GOV_RESOURCES_*` variables, a planted `/proc` folder for the marker processes, and a stub launch command
  (a small script that records its argv and stdin to a file and exits) set as `launch_command`, a stub notifier set
  as `notifier_command`. Never the real HOME, ~/.claude, ~/gov-os-worktrees, the real /proc for counting, or a real
  session. Wait for the stub's record with a bounded poll (the launch is detached), never a bare sleep.
- Two `tick`s started together (S1): start both as subprocesses at once (or hold `tick.lock` with `fcntl.flock` from
  the test while one runs); assert exit 4 for the loser and that it wrote nothing (state folder listing and mtimes
  unchanged apart from the winner's writes).
- Tests are red now (no `gov dispatch` yet: the command answers unknown). Run them and say which are red and why;
  anything green now is a fault in the test unless it is a guard for "nothing else happens".
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/empty-home
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-121-tests/src python3 -m pytest tests/acceptance/W2-121 -q
  -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
  (Inside a test, set HOME and the planting variables per test with monkeypatch or the subprocess's env.)
- Keep the suite fast: seconds per case; the stub commands, never a real model call. No test named with `real`,
  `green_here` or `time_limit` unless it must be skipped by that filter.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003" -- tests/acceptance/W2-121`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket and this brief do not settle: write your reading into the test's docstring and name it in
`unresolved`.
