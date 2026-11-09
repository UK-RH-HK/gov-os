# ACT-STOP-IDLE-1: the CTO's idle check, a second Stop hook (DEC-1110 (1))

- **For:** the owner's operator, in the main tree. It installs one hook script and its tests (tracked, committed with
  `Role: owner`) and adds one `Stop` entry to `.claude/settings.local.json` (local, untracked). A Claude session may
  run it, but Claude Code's safety check asks for the settings edit; a plain terminal is simpler.
- **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-09, prepared by a helper agent. Rehearsed in a clone; nothing
  live is changed until the operator runs §6.
- **Under:** DEC-1110 (1) (the check, as an ACT, rehearsed), DEC-1109 (3) and DEC-936 item 2 (unblocked work keeps
  moving while an item waits on the owner), DEC-1027 E (the inbox waiter's Stop hook, the pattern followed),
  OPERATOR-AGENT-1 §2 (the class).
- **Class: (b)**, your yes, by OPERATOR-AGENT-1's table: a hooks block in a settings file ("allow rules, hooks blocks,
  any other key: (b)") and hook code of the same kind as `stop_waiter_check.py` (the guard-hook row). See §5 for the
  code's vote, which is higher.
- **Review:** not yet. One independent review (the hook, its tests, `apply.sh`, the rehearsal log) before this goes
  to the owner, as for every ACT.

## 1. What it does
Before the CTO's session ends a turn, `governance/project/orchestration/tools/stop_idle_check.py` answers **block**
when nothing of the CTO's is running while DECIDED-NOT-DONE shows unblocked items, and names them. It lets a
legitimate wait through and names which. In order:

| Step | What it reads | Outcome |
|---|---|---|
| 0. Whose session | `log/cto-session.txt` | another session, or none registered: nothing said, nothing logged |
| 1. The bound | `stop_hook_active`; the turn's id (the transcript's last user entry, kept in `log/stop-idle-state.json`); a line `IDLE-REASON: <why>` in the CTO's last message (the transcript, or `last_assistant_message`) | at most one block per turn; a stated reason ends the turn, is logged and shown to the owner; a second stop with no reason is let through and named ("a second stop this turn, no IDLE-REASON line stated") |
| 2. Running | the four sources in §2 | anything running: let through silently, everything counted named in the log |
| 3. A legitimate wait | the dispatcher's tick: the gate or the disk gate shut; admission refused or the lead forecast refusing | let through: "the gate shut (…)" or "the machine full (…)" |
| 4. Unblocked items | DECIDED-NOT-DONE's tracking tables (§3) | none unblocked: let through, "every open item waits (N on the owner, M on a running job, K on a trigger)"; otherwise **block**, naming up to 15 items with their states |

The block's reason tells the CTO to start the items within the machine's limits (or move each to its true state in
DECIDED-NOT-DONE), or to write one `IDLE-REASON:` line and end the turn. It never blocks forever: at most once per
turn, and a stated reason always passes.

**It never fails open silently.** Any error (an unreadable or malformed DECIDED-NOT-DONE, bad input, an unreadable
`/proc`) is named to the owner (`systemMessage`: "Idle check (DEC-1110) could not run: …; the turn ends unchecked")
and logged in `log/stop-idle.log`; the turn ends. It always exits 0 and prints at most one JSON object. If the script
file is missing, the settings command exits 1 with a named message (Claude Code shows it as a non-blocking error);
it never exits 2, which Claude Code would read as a block on every turn. Standard library only; 26 to 63 ms on the
live state.

**A declared stand-by (`log/cto-standby.txt`) does not let an idle turn end here**, unlike the inbox waiter's check:
DEC-1109 (3) says unblocked items keep moving while one waits on the owner. A turn that truly cannot move states its
reason line.

## 2. How "running" is read, and why this reading
Each source was checked against the live session on 2026-11-09 19:14–19:31. The first three come from the machine's
own state, not from any record the CTO writes.

1. **The session's background agents:** `<transcript>/subagents/agent-*.meta.json`. Claude Code writes
   `"finished": true` there when an agent ends. Live: 51 of 58 finished, and the 7 unfinished were exactly the 7
   agents then running. An unfinished agent counts only if its transcript was written in the last 30 minutes; an
   older one is named in the log as stale and not counted. A killed or crashed agent therefore cannot hide idling for
   more than 30 minutes.
2. **The session's background Bash tasks:** `/tmp/claude-<uid>/<project>/<session>/tasks/*.output` held open by a
   live process (read from `/proc/*/fd`). A task that has ended holds nothing, so this needs no guessing from file
   ages. The standing watchers do not count as work: the inbox waiter, `sentinel_check.sh`, `usage_log.sh`,
   `store_refresh_daily.sh`, `bare_watch.sh`, and a bare `sleep N` timer. All six were found running live. A
   `proc.sh wait` or `wait_for.sh` task does count, because it ends when its target ends.
3. **Launched workers, verifications, landing selections and runs:** pid files (`launch_worker.sh`'s
   `<tree>/.gov-runtime/scratch/lead/log/*.pid`, `lead_verify.sh`'s `verify.pid`, `landing_select.sh`'s `run.pid`,
   `~/gov-os-runs/*/*.pid` and one level deeper). A pid file counts when its process is alive, its `<name>.exit` is
   absent, and either the process started no more than 15 minutes after the file was written or the process is one
   of the launchers.
   - **Why the start-time rule:** `pid_max` is 4,194,304 and the live pids had reached 4,089,492, so pids wrap within
     days and a stale pid file can name an unrelated process.
   - **Why 15 minutes of slack:** WSL's boot clock drifts against the wall clock. Live, `btime` placed workers' starts
     103 to 112 s after their pid files were written.
   - **Why the launchers are always accepted:** a reused pid that runs a launcher is running work whichever file
     named it.
   - **Why this source matters:** the dispatcher showed "leads running (0)" while 5 workers were alive. Only the pid
     files saw them.
4. **The dispatcher:** `dispatch/status.json`, written by the same tick as `status.txt` but machine-readable. It
   supplies the leads, the pending launches, the jobs by phase, a close and a landing. It is used only if it is at
   most 5 minutes old. A stale or unreadable status is named ("dispatcher status unusable …") and never relied on,
   neither for "running" nor for the gate.

**Anything running lets the turn end.** This follows the decision's words: "if no agent or job is running". So "IN
PROGRESS with nothing running for it" reduces to "IN PROGRESS while nothing runs".

A stricter per-item check is an option, not built: block when an unblocked item has nothing running for it by name
while the machine has room. Matching items to jobs by name is unreliable, and a wrong match would block a turn that
was working.

## 3. How "unblocked" is read
The hook reads every `## 0<letter>.` section of `governance/project/orchestration/packages/DECIDED-NOT-DONE.md`
(§0 to §0i today; a §0j is picked up without a change). It finds the `#`, `item` and `state` columns by header. The
`state` text is read after `*` and backticks are removed, in this order:

- **open** (unblocked): `DUE NOW` anywhere (for example "DONE (trigger set); rubric v3 DUE NOW"), or a state beginning
  `NOT STARTED` or `IN PROGRESS`;
- **wait:** `WAITS` or `WAIT` anywhere, on the owner (the text names the owner), a running job ("running"), or else a
  trigger;
- **closed:** the state begins DONE, MERGED, APPLIED, READY, ANSWERED, APPROVED, DECIDED, FILED, REHEARSED,
  STANDING, NOTED, CLOSED or SUPERSEDED;
- **unclassified:** anything else. It is not counted as unblocked but is **named** in the reason or message.

Rows in §1 onward are not read. Live at `d1f50e2fa`: 72 rows, of which 37 closed, 16 waits on a trigger, 3 on the
owner, 16 open, 0 unclassified. At `6a8707001` the CTO's new state for #66, "Built (45 tests, …)", reads as
unclassified and is named.

**A rule for the CTO:** begin each state with one of the words above.

**What counts as a parse error:** a missing or unreadable file; no `## 0` section; a section with no table; a table
without `#` or `state`; a row shorter than its header. Each is named, logged, and never a block.

## 4. The rehearsal (`drafts/stop-idle/rehearse.sh`, `rehearsal.log`): 2026-11-09 19:31, 0 failures
A clone of `w2/integrate` at `d1f50e2fa` in `~/gov-os-runs/STOP-IDLE-1-rehearsal`, with the live
`settings.local.json` copied in. `apply.sh` ran with `STOPIDLE_REPO` set to the clone.

| Step | Result |
|---|---|
| The live files before | 13 paths hashed: both settings files, the three guard hooks, the path map, `stop_waiter_check.py`, `permission_request.py`, the two targets (absent), the hook's log and state (absent), `cto-session.txt` |
| `check`, `apply`, `check`, `apply` | state old; backup `2b8909d236b7`; both files installed by hash; one `Stop` entry added; `verify` shows only that entry differs; 30 tests pass (24 for the idle check, 6 for the waiter); the settings command, as Claude Code runs it, answers nothing for another session; then "state applied"; a second apply "already applied" |
| The live bytes | the same edit on the live file with the live path computes the pinned `d715292711a2…` (computed only, never written) |
| The inbox waiter unaffected | its tests 6 passed before and after; its command byte-identical; its answer on the CTO's real input unchanged (`rc=0`, nothing said: armed) |
| End to end on the live state (read only) | through the settings command with the CTO's real session id and transcript: **let through, "running: 24"** (6 agents, the workers' pid files, tasks), exit 0, 63 ms |
| The same, with the live state planted away | **block**, naming 15 unblocked items from the live DECIDED-NOT-DONE (#14, #17, #19, #27, #30, …); the second stop of the turn: let through, named; the gate planted shut: "let through: the gate shut (SHUT (planted))"; DECIDED-NOT-DONE removed: "could not run …", logged as `error`, exit 0; the hook file removed: exit 1 with its message, never 2 |
| Planted faults | an edit to the hook after review: `check` refuses; a settings file changed since the rehearsal: `apply` refuses ("re-rehearse") |
| `undo` | the backup put back (`2b8909d236b7`); the two files removed; the clone's tree clean; `check` reads state old; the waiter's tests unchanged |
| The live files after | **the same 13 hashes**; the live tree's `git status` unchanged |
| The guard suites | not run: no guard file is touched (`.claude/hooks/**`, the path map and the guard's code hash as before) |

**The tests** (`test_stop_idle_check.py`, 24 cases on a planted DECIDED-NOT-DONE and a planted `/proc`, task folder,
agent folder, pid files and dispatcher status):
- blocks naming exactly the open rows (a DONE row with a DUE NOW part included; waits, closed rows and §1 rows left
  out);
- every open item waiting (owner, running job, trigger counted);
- a running agent; finished and stale agents;
- a running task; the watchers and timers not counted; an ended task;
- a worker by its pid file; with its exit file; dead; a reused pid (refused, or accepted as a launcher);
- the dispatcher's leads and jobs; the gate shut, the disk gate shut, the machine full; a stale status named and
  ignored;
- once per turn; a new turn checked again; `stop_hook_active`;
- a reason line (in the transcript, or in `last_assistant_message`); a reason from an earlier turn refused;
- a stand-by not honoured; another session, or none registered;
- five malformed or missing DECIDED-NOT-DONE files, each named; bad input named;
- the tree's own DECIDED-NOT-DONE parses; an unclassified state named; the default paths are the tree's own.

**The mutation check** (`mutation.log`): 13 of 13 mutants killed (the root one level short, never blocks, ignores
`stop_hook_active`, blocks twice a turn, the reason ignored, agents ignored, watchers counted, the exit file ignored,
a reused pid trusted, a stale status trusted, the gate ignored, DUE NOW not open, errors silent).

**Found by the rehearsal and fixed before pinning:** the hook first took its tree as `parents[3]` (the `governance/`
folder), so installed it saw no CTO session and said nothing. The unit tests missed it because they override the
paths. It is now `parents[4]`, with a test that installs the hook in a planted tree and runs it with no overrides.

## 5. The class, by the code (`governance/project/operator/act_class.py`, run read-only on two bundles)
- **Only the settings file:** (b), from the `settings` row (a hooks block). No script hits.
- **The settings, the hook and its test:** **(O)**. `class-rules.yaml`'s guard-hook row names `stop_waiter_check.py`
  and `permission_request.py` by file name. The new hook and its test fall to the catch-all row as unknown paths.

The higher vote applies, so through the operator agent this ACT would be refused as yours. Applied by hand at the
terminal, as §6 asks, the owner's commit with `Role: owner` covers it.

**A gap to close (your change, (O): the rule table is the operator's own file, §5):** add
`governance/project/orchestration/tools/stop_idle_check.py` to the guard-hook row. Until then, the landing check
does not flag a later CTO edit of this hook as a control path.

## 6. The operator's steps: the message
> **ACT-STOP-IDLE-1 (DEC-1110 (1)): the CTO's idle check as a second Stop hook.** In the main tree, about a minute.
> Class (b). The inbox waiter's Stop hook and everything else in `settings.local.json` stay as they are.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> A=.gov-runtime/scratch/orchestrator/drafts/stop-idle
> bash $A/apply.sh check     # the three files hash as reviewed (hook 482663cb476f, tests 46d06d1513c0, edit b9afa575c4ed); 24 tests pass; "state: old (settings 2b8909d236b7)" (exit 0)
> bash $A/apply.sh apply     # backup; hook and tests installed; one Stop entry added (settings d715292711a2); only that entry differs; 30 tests pass; "APPLIED" (exit 0)
> git add governance/project/orchestration/tools/stop_idle_check.py tests/unit/orchestration/test_stop_idle_check.py
> git diff --cached --name-status    # expect exactly 2 A: those two files
> git commit -m "ACT-STOP-IDLE-1: the CTO's idle check as a second Stop hook (DEC-1110 (1)): blocks once a turn when nothing runs while DECIDED-NOT-DONE shows unblocked items, names a legitimate wait or a stated IDLE-REASON; hook 482663cb476f, tests 46d06d1513c0; settings.local.json 2b8909d236b7 -> d715292711a2 (local)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1110" --trailer "Role: owner"
> ```
> **Then:** the CTO's running session picks up the new hook after you review it in its `/hooks` menu, or at its next
> start (the fresh session before D-10, DEC-1110 (2)).
>
> **Undo:** `bash $A/apply.sh undo`. If the settings still hash as written, it puts the backup back; otherwise it
> removes only this entry. It removes the two files if they were never committed. If they were committed, revert that
> commit with the same three trailers (the files are inert without the entry).

## 7. Residuals
- **Internal Claude Code layouts:** `subagents/*.meta.json`'s `finished` flag and the `tasks/` folder are Claude
  Code's internals (checked on 2.1.318/319).
  - If an update changes them, agents or tasks go unseen. The check then errs toward a block, which happens at most
    once a turn and passes on a reason line; it never errs toward silence.
  - The log names everything counted, so a drift shows there.
- **The watcher list is fixed in the hook.** A new standing watcher would count as running and mask idling until it
  is added; the log names it.
- **The tree's own DECIDED-NOT-DONE is read by one unit test.** A malformed tracking table reds that test, as it
  would break the hook live. That is intended: the fix is in the file.

## 8. The files (scratch, `drafts/stop-idle/`)
| File | sha256 (first 12) | What |
|---|---|---|
| `stop_idle_check.py` | `482663cb476f` | the hook (installed at `governance/project/orchestration/tools/`) |
| `test_stop_idle_check.py` | `46d06d1513c0` | 24 tests (installed at `tests/unit/orchestration/`) |
| `settings_edit.py` | `b9afa575c4ed` | the one settings change: expect, add, remove, verify |
| `apply.sh` | `1441f951309c` | check, apply, undo; the files' and both settings hashes pinned |
| `rehearse.sh`, `rehearsal.log` | `d8d0bf9f908b`, `49170181563c` | the rehearsal and its record |
| `mutation.log` | `82a572c00f52` | 13 of 13 mutants killed |

[DEC-1110 (1), DEC-1109 (3), DEC-936 item 2, DEC-1027 E, ACT-STOP-WAITER-1, OPERATOR-AGENT-1 §2 and §5]
