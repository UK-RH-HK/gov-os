# Brief td-1: independent test designer for DAEO-6lid (W2-159), profile STANDARD, class C2

You write the acceptance tests for ticket DAEO-6lid (W2-159): `gov session-watch stop-check waiter|idle`, the
orchestrator's two Stop checks in the product. An engineer implements it in parallel in another tree; you never read
its work (`src/gov/session_watch/`, `tests/unit/session_watch/`, the guard refuses it) and write from the ticket's KPI
lines and its Interface only. The tests run red here (nothing is built in your tree); the lead merges them and checks
them red, then green on the engineer's code.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-159-tests |
| branch | w2/W2-159-tests |
| allowed paths | tests/acceptance/W2-159/** |
| ticket (read it first: KPI lines S1-S5, F1-F4, the Interface section at its end) | /home/usain/gov-os-worktrees/W2-159-tests/.tickets/DAEO-6lid.md |
| the test-design method | /home/usain/gov-os-worktrees/W2-159-tests/template/governance/kernel/skills/test-design/SKILL.md |
| the form of an acceptance suite that runs a `gov` command as a child process (read its support file for the pattern: `SRC = Path(gov.__file__).resolve().parents[1]`, a planted root, a clean environment) | /home/usain/gov-os-worktrees/W2-159-tests/tests/acceptance/W2-121/ (README.md, conftest.py, w2_121_support.py) |
| the reference (this repository's own two Stop hooks; read for the behaviours and the planted-input forms; your tests target the product command, never these) | /home/usain/gov-os-worktrees/W2-159-tests/governance/project/orchestration/tools/stop_waiter_check.py, stop_idle_check.py (where the KPI lines or the Interface differ from them, the KPI lines and the Interface rule: e.g. S4's unreadable state file is an error here, the reference ignores it) |
| the dispatcher's status and ready list forms (W2-121) | the ticket DAEO-cb2b's `## Interface` (/home/usain/gov-os-worktrees/W2-159-tests/.tickets/DAEO-cb2b.md), src/gov/dispatch/run.py (the `data` dict of status.json), src/gov/plan/render.py `ready_text` |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1027, DEC-1028, DEC-1110, DEC-1109, DEC-936, DEC-1088, DEC-1119, DEC-994 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## The behaviours to test (one test or more each; name each after its KPI: `test_s1_...`, `test_f2_...`)
Run the command as a child process: `[sys.executable, "-B", "-m", "gov.cli.main", "session-watch", "stop-check",
"waiter"|"idle", "--root", <planted root>]`, `PYTHONPATH` the tree under test's `src`, the hook's JSON on standard
input, a clean environment (no `GOV_*` or `GIT_*` of the running session; `HOME` a temporary folder), and the test
overrides of the Interface's item 6 (and the lead's two names) set in it. Assert on the exit code (0 always), the
parsed standard output (nothing, or one JSON object) and `stop-check.log`. Plant everything in `tmp_path`: the root
with `governance/project/session-watch.yaml`, `.gov-runtime/session-watch/` (session.txt, standby.txt with a set
mtime, state.json), `.gov-runtime/dispatch/status.json` (mtime set with `os.utime`), pid and exit files, the
transcript (JSON lines), a fake `gov` program for the dispatcher source (a small script that writes a ready list to
the file after `--ready`), and an item file for the file source. Never a live session, never `/proc` (always
`GOV_SESSION_WATCH_PS`), never a hook registered in any `.claude/`.

- S1: waiter absent (configured `waiter_commands`, none in the planted process list, registered session, no stand-by
  note): a block whose reason names the inbox waiter and the `waiter_arm` command. Each says no block: the waiter
  present in the process list; a stand-by note younger than 2 h (and, one more, an older note: blocks again); another
  session's id; a session file that cannot be read (e.g. a folder in its place, or mode 000 where the test is not root).
- S2: one case per legitimate wait, each no block and the wait named (systemMessage and log): the gate shut
  (`gate.open` false), the disk gate shut (`gate.disk.open` false), the machine full (`outcome` "refused"), every
  remaining item waiting on the owner, a running job (one each: a live pid file under 3 h with no exit file; a
  running entry in a fresh status.json). One with a stale pid (alive, started over 3 h ago): not counted, named as
  stale; with unblocked items it still blocks. One with an exit file beside a live pid: not counted. One with a status
  file older than 5 minutes showing the gate shut: not used (blocks on unblocked items). One with unblocked items and
  nothing running: a block naming each item's id.
- S3: a planted turn: first call blocks; second with `stop_hook_active: true` no block; a third in the same turn (no
  `stop_hook_active`) no block; a new turn (a new user entry appended to the transcript) blocks again. For both checks.
  A turn whose assistant text holds a line `IDLE-REASON: <why>`: the idle check lets it end, and `<why>` is in the
  log; the next turn (no such line) blocks again.
- S4: an unreadable `state.json` (both checks, the registered session, a case that would otherwise block): no block,
  a `systemMessage` naming the error, a log line naming it. A stand-by note beside unblocked items: the idle check
  still blocks.
- S5: the same unblocked items from each source (the default dispatcher source with the fake `gov`; a file source
  with reader `lines`; a file source with a `module.path:function` reader you plant on a path the child can import,
  e.g. via `PYTHONPATH`): each block names the same ids. A search of `src/gov/session_watch/` (under the tree under
  test's `src`) for this repository's names finds none: at least `DECIDED-NOT-DONE`, `cto-session`, `cto-standby`,
  `inbox_wait`, `stop_idle_check`, `stop_waiter_check`, `orchestration/tools`, `/home/`, `Dynamic-Agentic`, a
  `W2-<digits>` or `DAEO-<4 chars>` id. (This one also fails red here, as the folder is missing: make the test
  assert the folder exists first.)
- F1-F3 are S3, S2 and S4, S5's cases seen from the failure side: name them in the README's KPI map rather than
  duplicating; F4 (the paths) is the lead's check, not a test.
- The hyphenated route (P-W2-159-1 (a)): `gov session-watch --help` exits 0 (one test).
## The interface (the ticket's `## Interface` section, accepted as a whole by the CTO, P-W2-159-2 (a); the lead's reading of the KPI lines where marked [lead])

Read the ticket's `## Interface` section first: it is the contract, and neither you nor your counterpart changes it.
A gap or a contradiction you find comes back to the lead as a package (question, options with cost, recommendation),
never a choice of your own on an interface point. What follows restates it and adds the lead's reading where the
KPI lines leave a point open, so the test designer and the engineer build to the same thing.

1. Command: `gov session-watch stop-check waiter|idle [--root <dir>]`; standard input is the Stop hook's JSON
   (`session_id`, `transcript_path`, `stop_hook_active`, ...). It prints at most one JSON object on standard output,
   either `{"decision": "block", "reason": "..."}` or `{"systemMessage": "..."}`, or nothing; it exits 0 always and
   prints no envelope (the module declares `CHILD_EXIT_CODE = True`). The hyphenated command maps to the folder
   `src/gov/session_watch/` (P-W2-159-1 (a): `src/gov/cli/main.py`'s `_known` and `_module_name`, and
   `src/gov/check/commands.py`'s existence check, map `session-watch` to `session_watch`).
2. Configuration: `<root>/governance/project/session-watch.yaml`, mapping under `session_watch:`; every key optional:
   `waiter_commands` (list of substrings of a process's command line; unset or empty: the waiter check says
   nothing), `waiter_arm` (default the first of `waiter_commands`), `standby_max_age_h` (default 2), `pid_globs`
   (relative to the root; default `.gov-runtime/**/*.pid`), `items` (`{source: dispatcher}` default, or
   `{source: file, path: <relative>, reader: lines | <module.path:function>}`).
   - Reader `lines`: one item per non-`#` non-empty line, `<id> <state words>`; state `WAIT owner...` is
     owner-waiting, `WAIT ...` another wait, `DONE` or `CLOSED` closed, anything else unblocked.
   - Reader `module.path:function`: called as `function(path)` [lead: with the item file's absolute path], returns a
     list of `{id, title, state}`, state one of `open`, `owner`, `job`, `closed`.
   - Source `dispatcher`: runs `<gov> plan --root <root> --ready <tmp file>` and takes batch 1 (the lines under
     `# batch 1`, form `<name> <ticket id> <brief> <log>`) as unblocked, less the tickets `status.json`'s `running`
     shows. [lead] An item's id is the ticket id (the second column); its title the first column.
3. Runtime folder `<root>/.gov-runtime/session-watch/`: `session.txt` (the registered orchestrator session id; read,
   never written), `standby.txt` (the stand-by note; its age is its mtime), `state.json` (the once-a-turn state,
   shared by both checks, keyed by check: `{"waiter": {...}, "idle": {...}}`), `stop-check.log` (one tab-separated
   line per decision, the check's name in it, and the IDLE-REASON line's text when one ended the turn).
4. Dispatcher status `<root>/.gov-runtime/dispatch/status.json` (W2-121's schema), used only when at most 5 minutes
   old by mtime (an older one is not used): gate shut = `gate.open` false or `gate.disk.open` false; machine full =
   `outcome` "refused"; running = `running`, `running_jobs` or `pending_starts` non-empty.
5. Running (S2): the session's background agents and tasks as the reference reads them, and pid files under
   `pid_globs` (the process alive, started under 3 h ago, no `<name>.exit` beside the `<name>.pid`); one past 3 h is
   named as stale and not counted.
6. Test overrides (environment): `GOV_SESSION_WATCH_PS` (a JSON list of `{pid, cmdline, start, state, fds}` in place
   of /proc; `start` epoch seconds, `state` a /proc state letter, `Z` or `X` not alive), `GOV_SESSION_WATCH_NOW`
   (epoch seconds, the check's "now" for every age: stand-by note, status file, pid start), `GOV_SESSION_WATCH_GOV`
   (the `gov` program run for the plan). [lead, the Interface's item 5 "overridable for tests by env", named after the
   reference's precedent:] `GOV_SESSION_WATCH_SUBAGENTS` (the folder of the session's background agents' files) and
   `GOV_SESSION_WATCH_TASKS` (the folder of its background tasks' output files).

The lead's reading of the KPI lines (for both of you):
- [lead] Which session: both checks act only for the registered session (`session_id` equal to `session.txt`'s
  stripped text). Another session's id, no `session.txt`, or a `session.txt` that cannot be read: the check prints
  nothing (S1's "says nothing").
- [lead] A turn (S3): the reference's definition (`stop_idle_check.py`, docstring item 1 and `turn_and_reason`): the
  transcript (`transcript_path`, JSON lines) read back from its end to the last `user` entry that starts a turn (not
  a tool result and not `isMeta`, or any user entry carrying `turnOrigin` or `wakeupSource`); its `uuid` (else its
  `timestamp`) is the turn's key. The `IDLE-REASON: <why>` line is searched in the `assistant` entries' text items
  after that entry (and in the hook input's `last_assistant_message` if present). Only entry types, keys and those
  text items are read.
- [lead] Once a turn (S3): the state file records, per check, the session and the turn it blocked. A check never
  blocks when `stop_hook_active` is true, nor when the state shows it already blocked this session's same turn; a new
  turn key blocks again. A missing `state.json` is an empty state.
- [lead] Errors (S4) for the registered session: a `state.json` that exists but cannot be read or parsed is an
  error. On an error the check prints `{"systemMessage": "..."}` naming the error (no `decision`), and writes a line
  naming it in `stop-check.log`; the turn ends. This holds for both checks.
- [lead] S1's other cases (the waiter running, a stand-by note younger than its limit, another session, a session
  file that cannot be read): no block (no `decision` key in the output).
- [lead] The waiter's block reason names the inbox waiter and the `waiter_arm` command (the configured string, as it
  is).
- [lead] The idle check ignores the stand-by note (S4). A let-through for a legitimate wait (the gate shut, the
  machine full, every remaining item waiting on the owner, a running job) prints `{"systemMessage": "..."}` naming
  which wait and writes it in the log; a stale pid file (past 3 h) is named there too. An IDLE-REASON let-through
  prints a `systemMessage` with the stated reason and logs it. The idle block's reason names each unblocked item by
  its id.
- [lead] Order in the idle check: registered session; IDLE-REASON (ends the turn, logged); the bound
  (`stop_hook_active` or already blocked this turn: through); running (through, named); a legitimate wait from the
  dispatcher's status (through, named); the items: none unblocked (through, naming the waits, e.g. "every remaining
  item waits on the owner", with counts of owner, job and other waits); unblocked items: block, naming them.
- No name, path, folder or ticket id of this repository in `src/gov/session_watch/` (S5, F3): no `cto-`, no
  `DECIDED-NOT-DONE`, no `inbox_wait`, no `W2-`/`DAEO-` id, no `/home/...`, no `orchestrator/tools`.

## Rules
- Write `tests/acceptance/W2-159/README.md` with the KPI map (each KPI line S1-S5 and F1-F3 to its test names; F4 is
  the lead's) and the planted forms; a `conftest.py` and one support module if you need them (name it
  `w2_159_support.py`); the tests in a few files by KPI. Plain pytest, standard library, `yaml` as the repository
  uses it. Each test runs in well under 10 s; no sleeps (ages through `GOV_SESSION_WATCH_NOW` and `os.utime`).
- Test the interface only: the command, its standard input and output, the configuration, the runtime files and the
  log. Never import `gov.session_watch` (the engineer's inner names are not the interface). A point the Interface
  and the lead's reading do not settle: test only what they settle, and name the point in `unresolved` (or as a
  package if a KPI cannot be tested without it).
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside
  ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, as
  one line:
  `mkdir -p /tmp/w2-159-td && env TMPDIR=/tmp/w2-159-td HOME=/home/usain/gov-os-worktrees/W2-159-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-159 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Expect red here (no implementation): check that each test fails for the missing command (or folder), not for an
  error in the test itself (a collection error or a fixture failing is yours to fix). `--collect-only` must list
  every test.
- Commit in one or two batches, your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1027, DEC-1110" -- tests/acceptance/W2-159`
  (`Implements:` only ids from the ticket's `sources:`: DEC-1027, DEC-1028, DEC-1110, DEC-1109, DEC-936, DEC-1088,
  DEC-1119, DEC-994, DAEO-cb2b; name the ones your tests carry.)
- One-line commands only; a longer script goes in a file under your tree's `.gov-runtime/scratch/td/` run with
  `bash` or `python3`. Use literal paths. Never touch `.gov-runtime/scratch/lead/`. No install, no network, no
  `.claude/`, never a live session or a hook registered anywhere.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (the files and the test count per KPI) / files_changed / evidence (the red run's summary line and
the `--collect-only` count) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time |
form | the hook's reason | true or false-positive).
