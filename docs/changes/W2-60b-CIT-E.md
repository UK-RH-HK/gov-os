---
id: W2-60b-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-11-16
branch: w2/W2-60b
base: 4bc0399fb
ticket: DAEO-ecac (W2-60b)
author: engineer (DAEO-ecac), brief en-1
decisions_recorded: [DEC-946, DEC-838, DEC-839, DEC-826, DEC-655, DEC-495, DEC-392, DEC-959, DEC-963, DEC-847, DEC-983, DEC-982, DEC-1120, DEC-1156]
state_class: EVIDENCE
---

# W2-60b: change-execution record (CIT-E)

W2-60b (DAEO-ecac) gives every launched worker session one record keyed by its session id, read from the
harness's own record of the session (DEC-838 item 3, CAP-36.a lite). It also reads the launchable roles from the
kernel's role files (DEC-946 (W3-P09)), makes `qa-engineer` a known role of the guard (DEC-959 item 3), refuses a
second writing session in a worktree (DEC-847, DEC-963, DEC-1156 (3)), and builds the behaviour of
`gov launch --tests-worktree` (DEC-982). Status **APPLIED** in the code, except two parts that are not in this
ticket's paths. They are drafted below and not applied: the live hook's reviewer line, which needs the owner's ACT
(§6), and the `command.py` flag, which is the CTO's path question (§7).

## 1. The changes

| # | File | Change | Tests |
|---|---|---|---|
| 1 | `src/gov/launch/session_record.py` (new) | The record: `begin`, `finish`, `measures`, `write` (temporary file and rename), `read_record`, `Keeper` (the launcher's two calls, one stderr line), `live_writers` / `check_one_writer`, `REVIEWERS` | `tests/unit/launch/test_session_record.py` |
| 2 | `src/gov/telemetry/sessionlog.py` | New reading only: `measure(path, session)` (turns, compactions, rate-limit events, cost, effort, minutes, the main session's models, one model per sub-agent, versions). `find`, `subagent_files` and `read` are not changed. | `tests/unit/telemetry/test_sessionlog_w2_60b.py` (one case checks that `read` is unchanged for a 429 line) |
| 3 | `src/gov/launch/launcher.py` | (a) The `Keeper`'s `begin` once the session's process has started and its `end` in `_run`'s `finally`, on every exit path. (b) `_role_kind`: the launchable roles and the own-ticket rule, read from the role files. `OWN_TICKET_ROLES` is removed, and `WORKER_ROLES` is no longer the launchable set (§4). (c) `check_one_writer` before anything is written. (d) `tests_worktree()`. (e) A new role's template is found by name (§5). | `tests/unit/launch/test_session_record_launch.py` |
| 4 | `src/gov/guard/decide.py` | `"qa-engineer"` added to `KNOWN_ROLES`, and nothing else in the file. | `test_session_record_launch.py` (the guard cases) |

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
| `turns` | the result line's `num_turns`; else the session's own assistant messages (message ids, each once, harness-written ones left out) |
| `cost_usd` | the result line's `total_cost_usd`; else `totalCostUSD` of the last `cost-state` line of the session's own file |
| `minutes` | the result line's `duration_ms`; else the time from the first to the last line timestamp of the session's own file |
| `subagents` | `{"count": n, "models": [...]}`: the files `<id>/subagents/agent-*.jsonl`, each one's first model (null when it has none) |
| `rate_limit_events` | `[{"at": <timestamp>}, ...]`, one entry per line: a `system`/`api_error` line with `error.status` 429, or an assistant line with `isApiErrorMessage` true and `error` `rate_limit`, from the session's and its sub-agents' files. Each line counts once; the two forms are not merged. |
| `compactions` | the `system` lines of subtype `compact_boundary` in the session's own file |
| `claude_code_version` | the `version` the lines carry (one value gives a string, several give a list): the one log text allowed in the record |
| `window` | the result line's `modelUsage.<model>.contextWindow`; else not measured (§8) |
| `tier` | from the model's name: `opus`, `sonnet`, `haiku` or `other`. It is not measured when the model is not, or when the models span more than one tier. |

**Counts only (S3):**
- Model names are given out only in a plain name form (`[A-Za-z0-9][A-Za-z0-9._:\[\]-]{0,99}`). If any model name
  has another form, `model` is not measured.
- Timestamps are given out only in ISO form. If a rate-limit line has no timestamp, `rate_limit_events` is not
  measured.
- Efforts are given out only as one of the five words.
- A refusal's text names no line content (W1-31's rule).

**Where the log is found:** W1-31's `find(config, session)`. `config` is `CLAUDE_CONFIG_DIR` when the launcher's
environment sets it, else `<home>/.claude`. When there is no log, or the reader refuses the log, every log value is
not measured and carries the reader's message as its reason.

**Not in the record (non-goals):**
- pass or fail;
- the repair count (W2-07's close keeps it);
- any session text, the version excepted.

## 3. One writer per worktree (S10, S12)

`gov launch` of a writing role reads the session records after today's checks and the role check, and before
anything is written (the launch record's folder, the placeholders, the temp folder).

**A live writing session** is a record that meets all of these:
- its `worktree` (as a real path) is this launch's tree;
- its `ended_at` is null;
- its `pid` is alive: `kill(pid, 0)` succeeds or is refused with EPERM;
- its role is not in the reviewer set `REVIEWERS = {independent-auditor, qa-engineer}`.

When there is one, the launch is refused with `LAUNCH_REFUSED`. The message names that session's id, its role, its
pid and the worktree. A reviewer is never refused for this, and a live reviewer is never counted.

**Ways it fails closed:**
- **A reused pid.** If `/proc/<pid>/stat` shows the process started more than 2 s after the record's `started_at`,
  the pid now belongs to another process and the record is not live. If `/proc` cannot be read, the session counts
  as alive.
- **A bad record.** A `*.json` that cannot be read, is not JSON, or is not of the record's form (`record`,
  `session_id`, `worktree`, `pid`, `started_at`, `ended_at`, `role.value`) refuses the launch, naming the file: it
  could be a live writer's.
- **A folder that cannot be listed** refuses.
- **A live record with no role** counts as a writer.

A place that is not a folder (a file at `.gov-runtime/sessions`) holds no record, because `write` writes into a
folder only, so it hides none. It refuses nothing, and S5 governs its write.

**Accepted cost of failing closed:** a stale record that is malformed blocks every writing launch of the repository
until someone removes it, and the refusal names the file.

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

**F1:** `OWN_TICKET_ROLES` is gone from `launcher.py`. The name `WORKER_ROLES` stays, as
`tuple(role for role in ROLE_TEMPLATES if role not in LEAD_ROLES)`. It is no fixed tuple and no launch reads it to
decide anything. It stays because `tests/unit/launch/test_w2_153_template.py` (keep-green) and
`tests/acceptance/W1-50` import it. If F1's check is read as "the name must not appear", that conflicts with those
two tests (see the return's `unresolved`).

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

## 7. The CTO's path question: `command.py` for `--tests-worktree` (not applied)

The behaviour is `launcher.tests_worktree(root, role, ticket_id)`:
- the role is the independent test designer, and the ticket is known and `in_progress`;
- it makes the worktree `<tree>-tests` with `git worktree add -b <tree's branch>-tests <tree>-tests HEAD`;
- it prints the path, returns 0, and starts, records and gates nothing;
- an existing path or branch, or a tree on no branch, refuses.

The flag needs these bytes in `src/gov/launch/command.py`, which is not in this ticket's `allowed_paths`:

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

**The launcher reads no result line.** The session's stdout is not captured, and capturing it would change the
launcher beyond its two calls. So a launched session's record says `window` not measured, with the reason: "the
session log states no window in a form the specimens show, and no --output-format json result line
(modelUsage.<model>.contextWindow) was read". S4 is open (see the return's `unresolved`). Compactions are counted
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
