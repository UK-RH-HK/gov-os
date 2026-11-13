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
