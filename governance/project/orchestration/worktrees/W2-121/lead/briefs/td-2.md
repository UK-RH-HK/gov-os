# Brief td-2: independent test designer, fix round, for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-cb2b (W2-121, part a: `gov dispatch tick` and
`gov dispatch status`). Your first batch (td-1, commit 0384e71db) is the acceptance suite in `tests/acceptance/W2-121/`
(read its README.md and `w2_121_support.py` first: the planted project, the stubs and the helpers are yours). The
independent review's round 1 failed with findings you now turn into tests, as **described behaviours**: you get the
behaviour, never the engineer's code. You never read the engineer's work on this ticket (`src/gov/dispatch/**`,
`tests/unit/dispatch/**`; the guard refuses them).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121-tests |
| branch | w2/W2-121-tests |
| your allowed paths | tests/acceptance/W2-121/** |
| ticket (KPI S2, S4, S5, S6, S9; the Interface section; the sections P-W2-121-5 to P-W2-121-7 at its end) | /home/usain/gov-os-worktrees/W2-121-tests/.tickets/DAEO-cb2b.md |
| the round-1 interface readings (still hold) | below ("The interface") |
| **the fix round's readings (build to these)** | below ("The fix round's interface") |
| the gate you plant | src/gov/resources/machine.py, src/gov/resources/config.py, src/gov/resources/gate.py (docstrings) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1007, DEC-1010, DEC-1014, DEC-998 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The behaviours to test (one test or more each; name each after its KPI: `test_s4_...`, `test_s2_...`)
- **F-1 (S4):** an inbox item, once written, is never written again as unread. Planted: a finished session's return item
  is written; it is read (moved to `inbox/read/`) and then deleted; the next passes write no item for that log in
  `inbox/` (nor in `inbox/read/`). The same when the item is deleted straight from `inbox/` unread. The same for a start
  that never ran (its never-ran item deleted: not written again). If cheap, the same for an S7 owner item.
- **F-2 (S4):** an escalation is recorded only after the notifier exits 0, retried at a bounded cadence, its failure shown
  every pass. Planted (your stub notifier given a planted exit code, as your stub launcher has one):
  (a) the notifier exits 1 with `notify_retry_s: 0`; the next pass, with the notifier fixed (exit 0), runs it again for
  that item; after that success no more runs for it on later passes;
  (b) the notifier keeps exiting 1 with `notify_retry_s: 3600`: the pass after the failure does not run it again, and
  that pass's status (`status.txt` and `status.json`'s `problems`) still names the item's failed escalation;
  (c) a notifier that times out (your `set_notify_sleep` past a small `command_timeout_s`): the escalation is not
  recorded as raised: with `notify_retry_s: 0` and the notifier then working, a later pass runs it for that item;
  (d) a failed notifier does not fail the pass: exit 0 (no start refused), `ok` true in `status.json`.
  (e) an item read (moved to `inbox/read/`) while its escalation is failing is never retried and its problem line goes.
- **F-3 (S4, S5):** a `dispatch.yaml` without `notifier_command` (and one with `[]`): `tick` exits 2 naming
  `notifier_command`, starts nothing (a ready entry planted; the stub launcher never runs), and the status's first line
  is `PASS FAILED ...` naming it. Add `notifier_command` to the missing-key cases you already have if that is how your
  suite is built.
- **F-4 (S9):** a return whose `files_changed:` names a file that exists in the ticket's worktree only untracked (not
  committed, not ignored): the item's `unresolved:` line names it. Guards in the same case or beside it: a committed
  path is not named; a path that exists and is ignored by the worktree's `.gitignore` is not named.
- **F-5 (S2, S6):** the shut-gate refusal that only the gate gives: a gate shut for load (or CPU busy cores) with memory
  ample for every peak (so the room check alone would admit): no start, exit 3, every entry skipped with a reason that
  names the gate and does not rest on memory. Tighten your existing shut-gate tests if they accept a "memory" reason
  where the gate is what must refuse.

Not yours: F-6 (the engineer's, a unit test).

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

## The fix round's interface (review round 1's findings F-1 to F-6; the CTO's P-W2-121-7 (a), ticket section "P-W2-121-6 and P-W2-121-7")

Both the test designer and the engineer build to these readings; everything in the first round's interface still holds
except where a line below changes it. A reading you think wrong: follow it, and name it in `unresolved`. Tests check the
behaviour, never the names of the bookkeeping files (those are the engineer's).

- **F-1, an item is written once, ever (S4, S7).** An inbox item (a return `<log>.return.txt`, a start that never ran
  `<log>.never-ran.txt`, an owner item `<log>.owner.txt`), once written, is never written again, as unread or at all, even
  after it is deleted from `inbox/` (an honest operator removes a handled item) or from `inbox/read/` (a tidy-up of the
  read folder). The record that it was written lives in the state folder outside `inbox/` and outlives the item (e.g. an
  `items-written.txt`, one line per item name, appended when the item is written; `never-ran.txt` is read for the
  never-ran items). An item already in `inbox/` or `inbox/read/` also counts as written (a state folder from before this
  record). Deleting an item never raises its escalation again either.
- **F-2, an escalation is recorded only when it was sent (S4).** An item unread past `unread_escalate_s` runs
  `notifier_command` (the item's path its last argument). It counts as raised (never run again for that item) only when
  the notifier exits 0. A notifier that exits non-zero, times out (`command_timeout_s`) or cannot be started leaves the
  escalation due: it is tried again on a later pass, no sooner than `notify_retry_s` seconds (new key; a number >= 0;
  default 600; malformed: exit 2 naming the key) after its last attempt (0: every pass). While an escalation is due after
  a failed attempt, **every** pass's status (`problems` in `status.json`, the `problems:` block of `status.txt`) names
  the item and the last failure, also on passes that do not retry it; the line goes once it is sent or once the item is
  read (moved to `inbox/read/`), and a read item is never retried. A notifier timeout in a pass ends that pass's
  escalations (bounded pass time): the escalations still due in that pass are not run and not recorded as raised, and the
  status names them as not sent. A failed notifier never fails the pass: `ok` stays true and the exit code is the one the
  starts give (0 or 3).
- **F-3, the notifier is required at load (S4, S5).** `notifier_command` is a required key: missing, empty or not an argv
  list is a configuration error at load: exit 2 naming `notifier_command`, nothing started, the status's first line
  `PASS FAILED <time>: ...notifier_command...` (as every other missing key). No pass raises a configuration error after
  it has started a session.
- **F-4, an untracked path is unresolved (S9).** A relative path a return names on `files_changed:` resolves only when
  git knows it in the ticket's worktree: it is in HEAD's tree or in the history (`git log -- <path>` names a commit), or
  it exists and git ignores it (`git check-ignore`). A path that exists only as an untracked, not-ignored file (or only
  staged, in no commit) is named on the item's `unresolved:` line. Absolute paths: unchanged.
- **F-5, the gate case that only the gate refuses (S2, S6).** A gate shut for load or CPU (not memory) with memory room
  ample for the peak refuses every entry with a reason naming the gate (the round-1 reading: "gate shut"), exit 3, no
  start. (Test-only finding; the code already does this.)
- **F-6, a hung git while resolving (S9).** When git times out or fails while resolving a return's commits and paths,
  the item names them as not checked, never as unresolved: a line `unchecked: could not be checked (<the failure>): <the
  ids and paths>` and no `unresolved:` line for them; the pass's status names the failure as before. (Engineer only, with
  a unit test.)

## Rules
- Keep every existing test green on its own behaviour; change an existing test only where the readings above change the
  behaviour (F-2: an escalation is no longer recorded on a failed notifier; F-3: a missing notifier is exit 2 at load)
  and say which in `work_completed`.
- The new cases are red now against the current code where the behaviour is missing (F-1, F-2, F-3, F-4 expected red;
  F-5 may be green: it guards a check that exists). Run them and say which are red and why.
- Everything planted under pytest's tmp_path as in your first batch: never the real HOME, ~/.claude, the real /proc for
  counting, or a real session; bounded polls, never a bare sleep. Seconds per case.
- Every pytest run goes through the heavy-slot gate, one folder per run, TMPDIR outside the repository:
  `env HOME=/home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-121-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-121 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (a single file or `-k` selection in the same form while you work).
- Update README.md's KPI-to-test table for the new cases.
- One-line commands only; anything longer in a script under /home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1007, DEC-1010, DEC-1014, DEC-998" -- tests/acceptance/W2-121`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line; the new cases with red or green and why) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket and these readings do not settle: write your reading into the test's docstring and name it in
`unresolved`.
