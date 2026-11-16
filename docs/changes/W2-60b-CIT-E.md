---
id: W2-60b-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-11-16
branch: w2/W2-60b
base: 4bc0399fb
ticket: DAEO-ecac (W2-60b)
author: engineer (DAEO-ecac), briefs en-1, en-2 and en-3b
decisions_recorded: [DEC-946, DEC-838, DEC-839, DEC-826, DEC-655, DEC-495, DEC-392, DEC-959, DEC-963, DEC-847, DEC-983, DEC-982, DEC-1120, DEC-1156]
state_class: EVIDENCE
---

# W2-60b: change-execution record (CIT-E)

W2-60b (DAEO-ecac) gives every launched worker session one record keyed by its session id, read from the
harness's own record of the session (DEC-838 item 3, CAP-36.a lite). It also reads the launchable roles from the
kernel's role files (DEC-946 (W3-P09)), makes `qa-engineer` a known role of the guard (DEC-959 item 3), refuses a
second writing session in a worktree (DEC-847, DEC-963, DEC-1156 (3)), and builds the behaviour of
`gov launch --tests-worktree` (DEC-982). Status **APPLIED** in the code, except one part that is not in this
ticket's paths: the live hook's reviewer line, which needs the owner's ACT. It is drafted in §6 and not applied. The
`command.py` flag (§7) was applied by the CTO's path case P1 (a) (f5d4ce253).

## 1. The changes

| # | File | Change | Tests |
|---|---|---|---|
| 1 | `src/gov/launch/session_record.py` (new) | The record: `begin`, `finish`, `measures`, `write` (temporary file and rename), `read_record`, `Keeper` (the launcher's two calls, one stderr line), `live_writers` / `check_one_writer`, `REVIEWERS` | `tests/unit/launch/test_session_record.py` |
| 2 | `src/gov/telemetry/sessionlog.py` | New reading only: `measure(path, session)` (turns, compactions, rate-limit events, cost, effort, minutes, the main session's models, one model per sub-agent, versions). `find`, `subagent_files` and `read` are not changed. | `tests/unit/telemetry/test_sessionlog_w2_60b.py` (one case checks that `read` is unchanged for a 429 line) |
| 3 | `src/gov/launch/launcher.py` | (a) The `Keeper`'s `begin` once the session's process has started and its `end` in `_run`'s `finally`, on every exit path. (b) `_role_kind`: the launchable roles and the own-ticket rule, read from the role files. `OWN_TICKET_ROLES` and the `WORKER_ROLES` assignment are removed (§4). (c) `check_one_writer` before anything is written, and again under the start lock (en-3, review round 1 F1, §3); the start record is written straight after the CLI's start. (d) `tests_worktree()`. (e) A new role's template is found by name (§5). (f) en-2: a `--output-format json` worker session's stdout relayed, and its result line given to the record (§2a). | `tests/unit/launch/test_session_record_launch.py`, `tests/unit/launch/test_session_record_relay.py` |
| 4 | `src/gov/guard/decide.py` | `"qa-engineer"` added to `KNOWN_ROLES`, and nothing else in the file. | `test_session_record_launch.py` (the guard cases) |
| 5 | `src/gov/launch/command.py` | `--tests-worktree`: §7's diff, applied byte for byte (the CTO's path case P1 (a), DEC-1156 (7), f5d4ce253), and nothing else in the file. | `tests/unit/launch/test_session_record_tests_worktree_cli.py` |

`git diff 4bc0399fb -- src/gov/guard/decide.py` shows one added line, and `.claude/hooks/pretooluse.py` is unchanged.

## 2. The record (S1-S6, S11)

**Path:** `.gov-runtime/sessions/<session id>.json` in the repository's **main checkout**, found as
`gov.launch.record.main_checkout` finds `.gov-runtime/launches/`. The session id is the one W2-60a's launcher gives
with `--session-id` and keys the launch record by. Only a worker launch has a launch record, so only a worker launch
gets a session record; a lead launch (`gov launch orchestrator|lead`) gets neither.

**When it is written:**
- **At the start.** Once the session's process has started: the housekeeping keys and the launch record's five
  keys, with `ended_at` null.
- **At the end.** After the session ends, by every exit path: exit 0, a non-zero exit, DEC-392's SIGINT, SIGTERM and
  SIGHUP (exit 130), and a registry failure after the start. The record is replaced whole and holds every key.

**How it is written:** each write goes to a hidden `.<session id>.<16 hex>.tmp` in the same folder. That file is
fsynced and then renamed over `<session id>.json`; a failed write removes the temporary file, so a record is on disk
whole or not at all. No reader takes a hidden `.tmp` name.

**A record that cannot be written (S5):** the exit code is unchanged, and stderr gets one line for the whole session
(not one per attempt) naming the record's path:
`gov launch: the session record <path> cannot be written (<reason>); the session's exit code is kept (DEC-392)`.

**The folder is made before the settings are built.** `make_folder` runs after the one-writer check and before
`build_settings`. W2-56's runtime rules name every entry that exists under `.gov-runtime` at launch; made only at
the session's start, the folder gave the second launch one more literal rule (`Edit(/<tree>/.gov-runtime/sessions)`)
than the first. W2-153 F2 and W2-56 S3 saw that, and it broke W2-56 S3's "one list on every launch". Made first, it is
named on every launch of a main checkout. A folder that cannot be made refuses nothing; the write's failure is S5's
line. A launch refused after this point leaves the empty folder, as `_worker_plan` leaves the launch records' folder.

**Reading it back:** `read_record(root, ticket, session_id)` returns the record. It refuses when the record is
missing, cannot be read, is not a `gov-session` record of that id, or belongs to another ticket (its `ticket` value
differs).

**Housekeeping keys (plain values):**
- `record`: `"gov-session"`.
- `format`: `1`.
- `session_id`.
- `worktree`: the launched tree's real path.
- `pid`: the `gov launch` process.
- `started_at` and `ended_at`: UTC, `%Y-%m-%dT%H:%M:%SZ`; `ended_at` is null while the session runs.
- `exit_code`: the code the launcher returns; null while the session runs.

**Measured keys:** each is `{"value": v, "source": "<named source>"}` or `{"value": null, "not_measured": "<reason>"}`.
A key the log does not give is never reported as 0. A count the log does give may be 0, for example `compactions`
in a log with none.

| Key | Source |
|---|---|
| `role`, `ticket`, `task_class` (`ticket_class`), `criticality` | the launch record `.gov-runtime/launches/<id>.json`; null when it gives null |
| `promotion` | the launch record's `promotion.reason` (W2-184); null when there is none |
| `tokens_input`, `tokens_output`, `tokens_cache_creation`, `tokens_cache_read` | W1-31's `sessionlog.read`: the assistant lines' usage, each message once with its last line's figures, from the session's own file and its sub-agents' files |
| `model` | the models of the session's own assistant lines (`<synthetic>` left out). One model gives a string; several give a list. |
| `effort` | `perTurnEffort` of those lines, only when it is one of `low` .. `max`. One value gives a string; several give a list. |
| `turns` | the session log: the session's own assistant messages (message ids, each once, harness-written ones left out); where the log does not give it (no log, or one the reader refuses), the result line's `num_turns` |
| `cost_usd` | the result line's `total_cost_usd` (it wins: the CLI's own total for the session); else `totalCostUSD` of the last `cost-state` line of the session's own file |
| `minutes` | the session log: the time from the first to the last line timestamp of the session's own file; where the log does not give it, the result line's `duration_ms` / 60000 |
| `subagents` | `{"count": n, "models": [...]}`: the files `<id>/subagents/agent-*.jsonl`, each one's first model (null when it has none) |
| `rate_limit_events` | `[{"at": <timestamp>}, ...]`, one entry per line: a `system`/`api_error` line with `error.status` 429, or an assistant line with `isApiErrorMessage` true and `error` `rate_limit`, from the session's and its sub-agents' files. Each line counts once; the two forms are not merged. |
| `compactions` | the `system` lines of subtype `compact_boundary` in the session's own file |
| `claude_code_version` | the `version` the lines carry (one value gives a string, several give a list): the one log text allowed in the record |
| `window` | the result line's `modelUsage.<model>.contextWindow` of the main model: the log's main model (its first when several; matched as named or without a bracketed suffix such as `[1m]`); with no model from the log, the one entry when `modelUsage` holds only one. Else not measured, never a guess (§8) |
| `tier` | from the model's name: `opus`, `sonnet`, `haiku` or `other`. It is not measured when the model is not, or when the models span more than one tier. |

**Counts only (S3):**
- Model names are given out only in a plain name form (`[A-Za-z0-9][A-Za-z0-9._:\[\]-]{0,99}`). If any model name
  has another form, `model` is not measured.
- Timestamps are given out only in ISO form. If a rate-limit line has no timestamp, `rate_limit_events` is not
  measured.
- Efforts are given out only as one of the five words.
- A refusal's text names no line content (W1-31's rule).

**Which source wins, key by key (en-2, the lead's decision on S2):** the result line names its source as
`result line (--output-format json): <its key>`.
- `cost_usd` and `window`: the result line where it gives them; else the log (`cost_usd`) or not measured.
- `turns` and `minutes`: the log where it gives them; else the result line; else not measured.
- Every other key: the log alone (the result line's `usage` and `subagent_stats` are not read).
- The result line's `result` (the session's text) never reaches the record (S3).
- A result line of another form (not `"type": "result"`, a negative or boolean figure, a window of 0) gives nothing.

**Where the log is found:** W1-31's `find(config, session)`. `config` is `CLAUDE_CONFIG_DIR` when the launcher's
environment sets it, else `<home>/.claude`. When there is no log, or the reader refuses the log, every log value is
not measured and carries the reader's message as its reason.

**Not in the record (non-goals):**
- pass or fail;
- the repair count (W2-07's close keeps it);
- any session text, the version excepted.

## 2a. The result line: the relay (S2, S4; en-2)

**When.** A worker launch whose CLI arguments hold `--output-format json` (`--output-format json` or
`--output-format=json`; the last `--output-format` given counts, as the CLI takes it). `stream-json`, `text`, no
flag, an interactive run and every lead launch keep stdout inherited exactly as before. A run at a terminal with
`--output-format json` is relayed too: the bytes are the same.

**What.** The CLI starts with its stdout on a pipe (`_start(..., relay=True)`). `_Relay` copies every byte, as it
arrives, to the launcher's own descriptor 1: unbuffered `os.write`, binary, nothing added, dropped or reordered
(Python's own buffered stdout is flushed first). It keeps the last complete line that parses as a JSON object with
`"type": "result"`. A last line with no newline counts when it parses whole, so a truncated line is never a result.
A line longer than 64 MiB is relayed but not parsed. The line goes to the `Keeper`, which reads only the figures
of §2 from it.

**Order, with DEC-392's endings.** `pump` relays while the session's leader runs. The signal handler is unchanged
and never stops the relay, so a session asked to end (SIGTERM to its group) still has what it writes on the way out
relayed. Then come `wait()` and `_end_group` as before. `drain` relays what is left until the pipe ends, at most
`END_WAIT_S` more, for a process that left the group and still holds the pipe. The exit code is the session's (130
after a signal), as before.

**A relay failure (S5's rule).**
- A stdout that cannot be written (closed, EPIPE): one stderr line, `gov launch: the session's stdout cannot be
  relayed to the launcher's stdout, and the rest of it is lost (<reason>); the session's exit code is kept
  (DEC-392)`. The pipe is still read to its end, so the session is never blocked on a full pipe and its exit code
  is its own. The result line is still read.
- A pipe that cannot be read: one stderr line, and the relay stops. Not seen in practice, since `os.read` on a pipe
  fails only on a closed descriptor.

A line nested too deep for `json.loads` (it raises `RecursionError`, not `ValueError`) is relayed and is no result;
the relay goes on.

**Tests:** `tests/unit/launch/test_session_record_relay.py` (23). They cover which runs are relayed; bytes
identical, including all 256 byte values, a partial last line and a 5 MiB output; the last result line kept; a
truncated line not taken; a line nested 200,000 deep; the exit code unchanged (3, 7, 9); a SIGINT mid-run relayed to the end with exit 130 and
the result recorded; an unwritable stdout; an interactive run inherited; and `gov launch` run as its own process,
its stdout compared byte for byte.

**The signal cases in the lead's loaded run (en-3b).** At 2d1e751d4 two cases failed in the lead's parallel run:
`launch` returned `None` for SIGINT, and the relay case returned 0. The load was not the cause; a `SIG_IGN` the
cases inherited was. A job started with `&` by a non-interactive shell (no job control) inherits SIGINT and SIGQUIT
ignored (`SigIgn: 0x6`). `_run` keeps a signal its caller ignores ignored (W2-56), so the SIGINT never reached the
launcher:
- the stand-in session's `plan` passed `raise_signal`'s `None` as its return code;
- the relay case's stand-in CLI slept its 30 s and exited 0.

Both failures come back on an idle machine with `bash -c '<pytest> & wait'`.

**No path of `launch` or `_run` returns `None` or changes the session's code.** A real `Popen.wait()` returns an int,
and `code` starts at `INTERRUPT_EXIT`. Each path ends in one of these ways:
- a signal before the CLI starts returns 130 and starts nothing;
- a signal after the start, during the lock, the keeper's begin or end, or the relay, gives 130 through `end`, which
  raises nothing;
- otherwise the session's own code is returned;
- a refusal is raised, not returned.

A SIGINT while the start lock is awaited, before `_run` installs its handler, raises `KeyboardInterrupt` with no
session started, as before this ticket.

The cases now set the caller's handler themselves, as `test_w1_32.py` does, and the stand-in returns an int.
`test_a_signal_the_caller_ignores_stays_ignored_and_the_session_s_own_code_is_returned` pins the ignored path: the
session's own int code, recorded, and the caller's `SIG_IGN` given back. Each ordering rests on signals and pipes,
never on a sleep. All of them were green 20 runs of 20, in the foreground and as a `&` job.

## 3. One writer per worktree (S10, S12)

`gov launch` of a writing role reads the session records twice:
- **Before anything is written** (the launch record's folder, the placeholders, the temp folder), after today's
  checks and the role check. A planted or long-running writer is refused here, at no cost.
- **Under the machine-wide start lock** (`StartLock`, W2-20), straight after the lock is taken and before the gate's
  check (`_admit_start`, unchanged). This is the check that decides. A writing launch writes its start record
  (`Keeper.begin`) straight after its CLI's process has started, before any other step, and keeps the lock until the
  session is in the registry (`_run`'s `lock.release()`). So a launch that takes the lock after it always finds that
  record. Every path that gives the lock back has written the start record first, or has started no CLI: a refusal
  before the CLI starts, a signal that came first, or a CLI that could not be started.

**Review round 1, F1 (answered by en-3):** at 2d1e751d4 the check came before `StartLock()` and the start record only
after the CLI's start. Two launches inside that window both passed. The window was about 0.1 s, or the whole lock
wait while a third party held the lock, as it does in any fan-out. Both writers started. Now, of two writing launches
into one worktree, exactly one starts its CLI, however close together they start and whether or not a third party
holds the lock while they wait. The other gets `LAUNCH_REFUSED` and a non-zero exit, starts no CLI, and writes no
launch record and no session record. Its message names the first's session id and the worktree. A reviewer launched
together with a writer still starts.
Unit cases (`test_session_record_launch.py`):
- `test_two_writers_launched_together_start_one_cli_and_refuse_the_other_naming_it[barrier]` and `[held]`;
- `test_a_reviewer_launched_together_with_a_writer_still_starts`.

They run two real `gov launch` processes. Each says so on a FIFO as it reaches the start lock, so both are past
every earlier check before either can take the lock. They then contend together (`barrier`), or wait while the test
holds the lock itself (`held`). A planted CLI reports its start on the FIFO and runs until the test closes a pipe.
Every wait is on an event (a pipe or a process's end), never on a sleep. The reviewer case passed before the change
too; the two writer cases were red at 2d1e751d4 (both
writers started, in both modes) and red again with only the check under the lock taken out. They were green 20 runs
of 20, in the foreground and as a `&` job.

**A live writing session** is a record that meets all of these:
- its `worktree` (as a real path) is this launch's tree;
- its `ended_at` is null;
- its `pid` is alive: `kill(pid, 0)` succeeds or fails with anything but "no such process" (EPERM included);
- its role is not in the reviewer set `REVIEWERS = {independent-auditor, qa-engineer}`.

Its `started_at` plays no part. en-1 discounted a live pid whose process began after the record's `started_at`
(plus 2 s), as a pid-reuse guess. That judged the interface's planted live writer (a fixed stamp earlier than the
live process's start) not live, and let the second writer in. en-2 removed it on the lead's decision: a record with
`ended_at` null whose pid is alive **is live**, as the interface says.

When there is one, the launch is refused with `LAUNCH_REFUSED`. The message names that session's id, its role, its
pid and the worktree. A reviewer is never refused for this, and a live reviewer is never counted.

**Ways it fails closed:**
- **A reused pid.** A record left with no end by a launcher that died (SIGKILL, power loss), whose pid now belongs to
  another live process, is counted as live. The launch is refused, and the message names that record's session id,
  role, pid and worktree, so someone can see it is stale and remove it. A false refusal that names its cause is the
  fail-closed side, which the one-writer rule wants. A guess that let a second writer in would fail open.
- **A bad record.** A `*.json` that cannot be read, is not JSON, or is not of the record's form (`record`,
  `session_id`, `worktree`, `pid`, `started_at`, `ended_at`, `role.value`) refuses the launch, naming the file: it
  could be a live writer's.
- **A folder that cannot be listed** refuses.
- **A live record with no role** counts as a writer.

A place that is not a folder (a file at `.gov-runtime/sessions`) holds no record, because `write` writes into a
folder only, so it hides none. It refuses nothing, and S5 governs its write.

**Accepted cost of failing closed:** a stale record that is malformed blocks every writing launch of the repository
until someone removes it, and the refusal names the file. The same holds for a stale well-formed record of the same
worktree whose pid was reused (above): it blocks that worktree's writing launches until it is removed or its process
ends.

**Unit cases for the probes:** a live pid with an earlier stamp is live
(`test_a_live_pid_is_live_whatever_its_process_start`,
`test_a_live_writer_with_an_earlier_fixed_start_stamp_refuses_the_second_writer`); EPERM counts as alive; a
malformed record refuses, naming it; a folder that cannot be listed refuses; a dead pid or an ended record is not
live.

## 4. Launchable roles and the own-ticket rule, read from the role files (S7, S8, F1)

`_role_kind(root, role)` reads the kernel role file that `gov.launch.role` reads:
`template/governance/kernel/roles/<role>.md`, or `governance/kernel/roles/<role>.md` in a tree with no `template/`.

**What the file decides:**
- **Name.** The role name must be a plain name (`[a-z][a-z0-9]*(-[a-z0-9]+)*`), checked first with no file read.
- **Missing or unreadable file.** The launch is refused: `'<role>' is not a worker role: the role file <rel> cannot
  be read ...` (`LAUNCH_REFUSED`).
- **Worker or not.** A file is a worker's unless it says otherwise: its `- **Authority level:**` line's first word
  is not `worker`, or its `- **Network:**` line begins "no profile from the launcher". Either refuses with
  "not a worker role", naming the role. Either line written twice also refuses.
- **The kernel's files as they stand.**
  - Launchable: `engineer`, `independent-test-designer`, `independent-auditor`, `research`, `product-spec` and
    `qa-engineer`.
  - Not launchable: `orchestrator`, `senior-engineer` and `ticket-lead`. Each says "coordinator" and "no profile
    from the launcher". `orchestrator` and `lead` stay lead launches, as today.
- **The own-ticket rule.** A worker keeps to a ticket whose `role` is its own unless it is independent. It is
  independent when its Authority level line says "independent of", or its name begins `independent-`. The kernel
  gives own-ticket for engineer, research and product-spec, and any `in_progress` ticket for the test designer, the
  auditor and `qa-engineer`. The file is read for this only when the ticket's role is not the launched role.

**Why the name prefix is there:** the existing tests' fixture role files must launch unchanged (S7). Several of them
say only "worker, with no approval authority" for the test designer and the auditor (W2-60a's fixture), or carry no
Authority line at all (W2-56, W2-136, W2-116), and they launch those roles on an engineer's ticket. The file alone
cannot tell those fixtures apart from the engineer's. The clean form is a `Ticket` line in each role file
(ROLES-SPEC-1 §5.2); that is a kernel change, drafted as a CIT-P in §9 and not applied.

**Order (W2-60a Behaviour 10 kept):** in a tree with no role file, today's refusals come first with today's words:
the CLI arguments, the ticket, the repository's settings, the template and the CLI. `_role_kind` comes after `_cli()`.
A role the template map does not name has its file read just before its template, so a ticket naming a role with no
role file is refused `LAUNCH_REFUSED` naming the role, not `LAUNCH_NO_TEMPLATE`.

**F1:** `launcher.py` assigns neither `OWN_TICKET_ROLES` nor `WORKER_ROLES`, annotated or not (en-2, on the lead's
decision). `tests/unit/launch/test_w2_153_template.py` (keep-green) and `tests/acceptance/W1-50` still read
`launcher.WORKER_ROLES`. The module's `__getattr__` (PEP 562) serves that name when it is read: the template map's
worker entries (its five, the lead names left out), worked out at the time. No launch reads it to decide anything;
a launch admits whatever role file `_role_kind` admits. The unit case `test_no_fixed_role_tuple_is_left_in_the_launcher`
walks the module's syntax tree for any assignment to either name, and `test_worker_roles_is_still_served_for_w2_153_s_readers`
checks the served value.

## 5. How a new role's template is found

`ROLE_TEMPLATES` keeps its seven entries (the five workers and the two lead names, W2-153). A role it does not name
has the template `.claude/templates/role-<role>.md` (`TEMPLATE_STEM`). A sixth role is therefore two files, its role
file and its template, and no code change. A missing template refuses as today (`LAUNCH_NO_TEMPLATE`, DEC-1050).
`qa-engineer` has no `.claude/templates/role-qa-engineer.md` today, so its launch is refused until that template
exists. Writing it is an ACT (DEC-315) and is not in this ticket's paths.

## 6. The owner's ACT draft: the live hook's reviewer line (not applied)

```diff
--- a/.claude/hooks/pretooluse.py
+++ b/.claude/hooks/pretooluse.py
@@ -77,7 +77,7 @@
 ACCEPTANCE = "tests/acceptance/"
 WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
 TEST_DESIGNER = "independent-test-designer"
-REVIEWERS = ("independent-auditor", "independent-reviewer", "reviewer", "auditor")
+REVIEWERS = ("independent-auditor", "independent-reviewer", "reviewer", "auditor", "qa-engineer")
 REVIEW_PATHS = ("docs/probes/", "docs/audit/", "docs/assessment/", ".gov-runtime/scratch/review/",
                 ".gov-runtime/scratch/audit/",
                 # the CTO's review records, where its briefs tell reviewers to write them (ACT-GUARD-FIX-4: two false
```

## 7. The CTO's path question: `command.py` for `--tests-worktree` (applied in this ticket by the CTO's path case P1 (a), f5d4ce253)

**Applied (brief en-4, build run 2):** the CTO's path case P-W2-60B-P1 (a) (DEC-1156 (7), commit f5d4ce253) added
`src/gov/launch/command.py` to the ticket's `allowed_paths` for this diff only. The diff below was applied with
`git apply`, byte for byte as recorded here (its context lines still matched), and `git diff` of `command.py` shows
only its three hunks. The diff stays below as the record. The unit case
`tests/unit/launch/test_session_record_tests_worktree_cli.py` runs `python3 -m gov.cli.main launch ...` as its own
process in a scratch git repository. It covers four paths: the exit-0 path (it prints `<repo>-tests`, the tree is on
`w2/T-1-tests` at HEAD, and there is no launch or session record), the refusal while the branch exists (exit 1,
`LAUNCH_REFUSED` naming the branch, no tree), another role, and a tree on no branch. All four were red before the
diff (exit 2, `unrecognized arguments: --tests-worktree`) and green after.

What follows is the draft as en-2 wrote it, before it was applied.

The behaviour is `launcher.tests_worktree(root, role, ticket_id)`:
- the role is the independent test designer, and the ticket is known and `in_progress`;
- it makes the worktree `<tree>-tests` with `git worktree add -b <tree's branch>-tests <tree>-tests HEAD`;
- it prints the path, returns 0, and starts, records and gates nothing;
- an existing path or branch, or a tree on no branch, refuses.

The flag needs these bytes in `src/gov/launch/command.py`, which is not in this ticket's `allowed_paths`.
**Checked by en-2 (2026-11-16):** `git apply --check` applies the diff cleanly to a scratch copy of
`command.py` at ce97dba4c, under `$TMPDIR`, never in the tree. With the patched copy,
`gov launch independent-test-designer TST-a001 --tests-worktree` in a scratch repository on `w2/T-1` exits 0, prints
`<repo>-tests` and makes that worktree on `w2/T-1-tests` at the repository's HEAD. Run again while the branch exists,
it exits 1 with `LAUNCH_REFUSED: the tests worktree's branch w2/T-1-tests is already there` and makes no tree.
Unpatched, the same line exits 2 with `unrecognized arguments: --tests-worktree`. The draft needed no fix.

```diff
--- a/src/gov/launch/command.py
+++ b/src/gov/launch/command.py
@@ -29,8 +29,8 @@
 
 
 def add_arguments(parser) -> None:
-    parser.usage = ("gov launch <role> <ticket> [--plan] [--gate-override DEC-NNN] [--gpu-need-mib N] "
-                    "[--reason <text>] [--trial <id>] [--owner-named <DEC-id>] [-- <CLI arguments>]")
+    parser.usage = ("gov launch <role> <ticket> [--plan] [--tests-worktree] [--gate-override DEC-NNN] "
+                    "[--gpu-need-mib N] [--reason <text>] [--trial <id>] [--owner-named <DEC-id>] [-- <CLI arguments>]")
     parser.add_argument("worker_role", metavar="<role>", help="engineer, independent-test-designer, "
                         "independent-auditor, research or product-spec")
     parser.add_argument("ticket", metavar="<ticket>", help="an in_progress ticket")
@@ -39,6 +39,9 @@
     parser.add_argument("--gpu-need-mib", metavar="<MiB>", type=int, help="the session's declared GPU need")
     parser.add_argument("--plan", action="store_true", help="print the role file's default line (model <id>, "
                         "effort <e>) and start nothing")
+    # W2-60b S10 (DEC-847, DEC-963, DEC-982): the test designer's own tree, made from the ticket's worktree.
+    parser.add_argument("--tests-worktree", action="store_true", help="make the ticket's tests worktree "
+                        "(<tree>-tests, on <branch>-tests at HEAD), print its path and start nothing")
     # W2-184 (interface 7.2a, the CTO's P-W2-184-2 (a)): RUBRIC-2's options, before "--"; the launcher judges them.
     parser.add_argument("--reason", metavar="<text>", help="why the launch chooses effort max itself (recorded)")
     parser.add_argument("--trial", metavar="<id>", help="the trial (governance/project/trials/<id>.yaml) that "
@@ -55,6 +58,8 @@
     from gov.launch import launcher
     if getattr(args, "plan", False):
         return launcher.plan(root, args.worker_role, args.ticket)
+    if getattr(args, "tests_worktree", False):
+        return launcher.tests_worktree(root, args.worker_role, args.ticket)
     # a given option only (an empty one too, for the launcher to refuse); absent, the launcher's default is None
     options = {key: value for key, _ in OPTIONS if (value := getattr(args, key, None)) is not None}
     if args.worker_role in launcher.LEAD_ROLES and options:
```

## 8. The window (S4)

**No form in the session log states the window.**
- W1-31's four specimens show none: the `model` attachment is passed over by type, and the `cost-state` line's
  `modelUsage` carries no `contextWindow`.
- The lead found none in real logs (model ids without `[1m]`).

**The one documented form** is the `--output-format json` result line's `modelUsage.<model>.contextWindow`
(`docs/assessment/2026-10/F-models-context.md` l.424 and l.504). The record reads it there when a result line is
given.

**The launcher reads the result line (en-2).** A worker session run with `--output-format json` has its stdout
relayed (§2a), and its record states the window from `modelUsage.<main model>.contextWindow`, with the source
`result line (--output-format json): modelUsage.<model>.contextWindow`. A real Opus 5.5 run gave `1000000`
(the lead's specimen of 2026-11-16, Claude Code 2.1.32x). Every other session (interactive, or another output
format) records `window` not measured, with the reason: "the session log states no window in a form the specimens
show, and no --output-format json result line (modelUsage.<model>.contextWindow) was read". Compactions are counted
from the log (`compact_boundary`).

## 9. CIT-P draft (kernel, not applied): a `Ticket` line in each worker role file

This would replace §4's name-prefix fallback with a line each role file states (ROLES-SPEC-1 §5.2 `Ticket`). The
bytes add one line after each file's `- **Authority level:**` line:

| File | Line added |
|---|---|
| `template/governance/kernel/roles/engineer.md` | `- **Ticket:** own-role` |
| `template/governance/kernel/roles/research.md` | `- **Ticket:** own-role` |
| `template/governance/kernel/roles/product-spec.md` | `- **Ticket:** own-role` |
| `template/governance/kernel/roles/independent-test-designer.md` | `- **Ticket:** any-in-progress` |
| `template/governance/kernel/roles/independent-auditor.md` | `- **Ticket:** any-in-progress` |
| `template/governance/kernel/roles/qa-engineer.md` | `- **Ticket:** any-in-progress` |

`_role_kind` would read the line first and fall back to today's reading without it. That fallback keeps the existing
fixtures green until they are brought to the new form. Not needed for this ticket's lines.
