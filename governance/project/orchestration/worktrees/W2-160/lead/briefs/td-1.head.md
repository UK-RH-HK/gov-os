# Brief td-1: independent test designer for DAEO-fd0p (W2-160), profile STANDARD, class C2

You write the acceptance tests for ticket DAEO-fd0p (W2-160): `gov wait <exit-file> [<max-s>]` (a bounded wait on a
job's exit file, liveness by its pid file alone) and `gov session-watch helper-watch` (an inbox item when a helper of
the registered session or a launched worker dies or goes silent). An engineer implements it in another tree; you
never read its work (`src/gov/wait/`, `src/gov/session_watch/helper_watch.py`, `tests/unit/wait/`,
`tests/unit/session_watch/test_w2_160*`; the guard refuses it) and write from the ticket's KPI lines and its Interface
(I1 and I2, at the ticket's end) only. The tests run red here (nothing is built in your tree); the lead merges them and
checks them red, then green on the engineer's code.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-160-tests |
| branch | w2/W2-160-tests |
| allowed paths | tests/acceptance/W2-160/** |
| ticket (read it first, all of it: KPI lines S1-S4, F1-F4, and the section "P-W2-160-1 decided ...", whose I1 and I2 are the Interface) | /home/usain/gov-os-worktrees/W2-160-tests/.tickets/DAEO-fd0p.md |
| the test-design method | /home/usain/gov-os-worktrees/W2-160-tests/template/governance/kernel/skills/test-design/SKILL.md |
| the form of an acceptance suite that runs a `gov` command as a child process (read its support file for the pattern: `SRC = Path(gov.__file__).resolve().parents[1]`, a planted root, a clean environment); W2-159 is also the `gov session-watch` command this one extends | /home/usain/gov-os-worktrees/W2-160-tests/tests/acceptance/W2-159/ (README.md, conftest.py, w2_159_support.py) |
| W2-159's configuration (the `pid_globs` key and its default `.gov-runtime/**/*.pid`; a missing file is the defaults; a key of the wrong kind is a configuration error) and its registered-session file | /home/usain/gov-os-worktrees/W2-160-tests/src/gov/session_watch/config.py, state.py (merged W2-159 code, readable) |
| the references (the CTO's two scratch tools this ticket turns into product; read for the behaviours and the planted-file forms; your tests target the product commands, never these; where they differ from the KPI lines or I1/I2, the KPI lines and I1/I2 rule: e.g. the product asks liveness with `os.kill(pid, 0)`, never `proc.sh`, and its env names are `GOV_WAIT_*`, `GOV_SESSION_WATCH_*`) | /home/usain/gov-os-worktrees/W2-160-tests/.gov-runtime/scratch/ref/wait_for.sh, helper_watch.py |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1119, DEC-1109 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## The behaviours to test (one test or more each; name each after its KPI: `test_s1_...`, `test_f3_...`)
Run each command as a child process: `[sys.executable, "-B", "-m", "gov.cli.main", "wait", <exit-file>, (<max-s>)]`
and `[sys.executable, "-B", "-m", "gov.cli.main", "session-watch", "helper-watch", "--root", <planted root>, ...]`,
`PYTHONPATH` the tree under test's `src`, a clean environment (no `GOV_*` or `GIT_*` of the running session; `HOME` a
temporary folder), with I1's and I2's test hooks set in it: `GOV_WAIT_EVERY` (e.g. 0.2), `GOV_WAIT_LINES`,
`GOV_SESSION_WATCH_SUBAGENTS`, `GOV_SESSION_WATCH_NOW`. Plant everything in `tmp_path`. Stand-in jobs are small
Python or shell child processes you start (`subprocess.Popen`), whose pid you write into `<base>.pid`; never a live
session, never a hook, never `~/.claude`.

`gov wait` (I1):
- S1: a stand-in job that writes `<base>.log` lines and then, after 2 seconds, its code (e.g. 3) into `<base>.exit`:
  exit code 3, stdout has `wait: DONE exit 3` and the log's tail. A never-written exit file with `<max-s>` 1: exit
  124, `RUNNING` in stdout, and the call ends well inside a few seconds (measure it). `<max-s>` 9999 on an exit file
  already written: stderr says `capped at 570` (and the job's code is returned). A JSON log (`<base>.json`, launcher
  lines then one `{"type":"result","session_id":..,"is_error":..,"num_turns":..,"result":..}` object): its
  session_id and is_error appear in the tail. `<base>.summary` is printed when there. A code over 255: % 256.
- S2: a stand-in job with its pid in `<base>.pid`, killed (and reaped) before it writes its exit file: exit 125,
  `GONE` in stdout, and the call ends within one poll period plus a small slack, far below `<max-s>` (give `<max-s>`
  e.g. 60 and assert well under it). With a second process of the same command line left running beside it: still
  125 at once. A zombie (a child killed and not reaped by its parent) counts as gone if you can arrange it portably;
  if not, leave it out and name it in `unresolved`. Exit 2 each: an exit file holding `abc`, a `<max-s>` of `x`, no
  arguments.
- F1 is S1's 124 within the bound and S2's 125 with a same-name process running: name them in the README's map.

`gov session-watch helper-watch` (I2), always with `--once` (a loop test only through `--max` small and `--every`
small, if at all: the "ended" line, `HELPER_WATCH ended after`, `re-arm it`, exit 0):
- Plant: `<root>/.gov-runtime/session-watch/session.txt` (the registered session id); a subagents folder named by
  `GOV_SESSION_WATCH_SUBAGENTS` holding `agent-<id>.jsonl` (JSON lines, each with `type`, `timestamp` (ISO, UTC) and
  `message`) and `agent-<id>.meta.json` (`finished`, `description`, `agentType`); worker files under
  `<root>/.gov-runtime/<some folder>/<name>.pid|.exit|.json`; the clock by `GOV_SESSION_WATCH_NOW` (epoch seconds),
  with file mtimes set by `os.utime` relative to it, and entry timestamps relative to it. Where I2 does not say
  whether "no entry for 30 minutes" is read from the entry's `timestamp` or the file's mtime, make both agree (both
  old for a stalled case, both fresh for a healthy one), and name the point in `unresolved`.
- S3: one planted condition each, plus a healthy helper and a healthy worker, in one root: (1) a helper whose last
  entry is an API error (`isApiErrorMessage: true`, or `apiError`, `model: "<synthetic>"`); (2) a helper not
  finished whose last entry is 31 minutes old; (3) a worker whose pid is gone (a stand-in started and killed) and no
  `.exit`; (4) a worker whose `.exit` holds a non-zero code, mtime at the clock; plus (4b) one whose `.exit` is 0 but
  whose `.json` result has `is_error: true` (or `api_error_status`). Healthy: a finished helper with a fresh normal
  last entry, a worker with a live pid (a running stand-in) and no exit file, one with exit 0 and a clean result.
  First pass: one item per condition in `<root>/.gov-runtime/dispatch/inbox/` (`*-helper-watch*.txt`), each naming
  the helper's id or the worker's log, and stdout one `HELPER_WATCH item <path>` per item; none for the healthy ones.
  Second pass (same clock or a little later, nothing changed): no new item, the inbox count unchanged (F3).
  No `session.txt`: no helper item (workers still looked at, if I2 says so; test only what it settles).
- S4: a text canary: each planted message's own text (a unique token, e.g. `CANARY-7f3a...`, in `message.content`
  of user, assistant and error entries, and in a worker `.json`'s `result`) never appears in any item, the state
  file, the log, or stdout. A filesystem spy: a snapshot (paths, sizes, mtimes) of the root and the temporary HOME
  before and after a pass: only files under `.gov-runtime/dispatch/inbox/`,
  `.gov-runtime/session-watch/helper-watch-state.json` and `.gov-runtime/session-watch/helper-watch.log` are new or
  changed. The window: a helper whose last entry is an API error 25 hours before the clock gives no item (and one at
  23 hours does, with `--window-h 24`). A source search: `src/gov/session_watch/helper_watch.py` and `src/gov/wait/`
  (under the tree under test's `src`) hold no process-name match: none of `pgrep`, `pkill`, `killall`, `pidof`,
  `psutil`, `proc.sh`, `/cmdline`, `/comm`, `"ps"`, `'ps'`, `ps -` (match whole tokens so `command` or `steps` is
  no hit); assert each file or folder exists first (so it is red
  here). F2 is these cases: name them in the map.
- F4 (the paths) is the lead's check, not a test.
