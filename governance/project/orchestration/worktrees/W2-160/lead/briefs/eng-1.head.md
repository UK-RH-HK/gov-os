# Brief eng-1: engineer for DAEO-fd0p (W2-160), profile STANDARD, class C2

You implement ticket DAEO-fd0p (W2-160): `gov wait <exit-file> [<max-s>]` (a bounded wait on a job's exit file,
liveness by its pid file alone) and `gov session-watch helper-watch` (an inbox item when a helper of the registered
session or a launched worker dies or goes silent), until its 66 acceptance tests in `tests/acceptance/W2-160/` pass.
The tests are merged and red (`invalid choice: 'wait'`, `invalid choice: 'helper-watch'`, the source folders not
built). Never edit `tests/acceptance/` (the test designer's; a test you believe wrong goes in `unresolved` with the
test name and why, never a change).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-160 |
| branch | w2/W2-160 |
| allowed paths | src/gov/wait/**, src/gov/session_watch/helper_watch.py, src/gov/session_watch/command.py (the `helper-watch` action only, about 20 lines; nothing else in the file changes), src/gov/check/commands.py (the one line adding `wait` to `RECORDED_GOV_COMMANDS`), tests/unit/wait/**, tests/unit/session_watch/test_w2_160*, docs/changes/W2-160-evidence.md |
| ticket (read it all; the Interface is I1 and I2 in its last section, word for word; it is also in the context below) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-fd0p.md |
| the acceptance tests (read README.md's map, then the tests and w2_160_support.py) | /home/usain/gov-os-worktrees/W2-160/tests/acceptance/W2-160/ |
| the references (the CTO's two scratch tools this ticket turns into product; port their behaviour; where they differ from I1/I2 the ticket rules: liveness by `os.kill(pid, 0)` plus `/proc/<pid>/stat` state `Z` as gone, never `proc.sh`; env names `GOV_WAIT_*`, `GOV_SESSION_WATCH_*`) | /home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/ref/wait_for.sh, helper_watch.py |
| the command form (a `gov` command is `src/gov/<name>/command.py` with `HELP`, `CLASS`, `add_arguments`, `run`, and `CHILD_EXIT_CODE = True` for its own exit code; the CLI finds it by folder) | src/gov/cli/main.py; src/gov/session_watch/command.py (W2-159, the command you extend); src/gov/resources/command.py (W2-20: an act command writing one inbox item, its ACT_PATHS) |
| W2-159's pieces to reuse (configuration `pid_globs` and its ConfigError; `state.registered`, `state.now` and the `GOV_SESSION_WATCH_NOW` clock; the folder constant) | src/gov/session_watch/config.py, state.py |
| the sources (read by id in /home/usain/gov-os-worktrees/W2-160/docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1119, DEC-1109 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## What to build (I1 and I2 are the contract; these are the points the tests hold you to)
- `src/gov/wait/__init__.py` (the package docstring carries the KPI map S1, S2, F1 to the code) and
  `src/gov/wait/command.py`: `CLASS = "read"`, `CHILD_EXIT_CODE = True`. Exit codes: the job's code % 256, 124
  RUNNING, 125 GONE, 2 usage / `<max-s>` not a number / exit file holding no number. Usage errors must exit 2
  **without** argparse's `invalid choice` text in stderr (the tests assert its absence). `<max-s>` default and
  ceiling 570; above it, stderr `wait: <max-s> <v> capped at 570`. Poll period `GOV_WAIT_EVERY` (default 5,
  fractions allowed); a gone pid ends the wait within one poll. One shared liveness function in `gov.wait` (e.g.
  `gov/wait/liveness.py` or in `__init__`) that the helper watch imports.
- `src/gov/session_watch/helper_watch.py`: I2 as written (registered session, helpers folder, workers by
  `pid_globs`, the clock, the four conditions once each in a state file that only grows, items opened with `x`, the
  state file and the log, stdout lines, exit 0, a W2-159 configuration error exit 1 named). It writes **only**
  `<root>/.gov-runtime/dispatch/inbox/*-helper-watch*.txt`, `<root>/.gov-runtime/session-watch/helper-watch-state.json`
  and `<root>/.gov-runtime/session-watch/helper-watch.log`: no lock file, no temporary file beside them (if you
  write the state atomically, check the S4 filesystem spy accepts it; a temp file left or created outside those
  names fails it), and nothing under HOME. It reads names, entry types, timestamps, tool names and error codes only,
  never a message's text (the text-canary tests plant a token in `message.content` and in a worker `.json`'s
  `result`; it must appear nowhere in items, the state file, the log or stdout). No process-name match anywhere in
  `src/gov/wait/` or `helper_watch.py`: none of the tokens `pgrep`, `pkill`, `killall`, `pidof`, `psutil`,
  `proc.sh`, `/cmdline`, `/comm`, `"ps"`, `'ps'`, `ps -`, not even in a comment or docstring.
- `src/gov/session_watch/command.py`: add `helper-watch` beside `stop-check` (its arguments `--every 300`, `--max
  86400`, `--stale-min 30`, `--window-h 24`, `--once`; `run` sends it to `helper_watch.run`) and
  `.gov-runtime/dispatch/inbox/**` to `ACT_PATHS`. `stop-check` behaves exactly as before: run W2-159's suites
  (`tests/acceptance/W2-159/`, `tests/unit/session_watch/`) and keep them green.
- `src/gov/check/commands.py`: `wait` added to `RECORDED_GOV_COMMANDS`, one line in the file's existing form.
- Unit tests in `tests/unit/wait/` and `tests/unit/session_watch/test_w2_160_*.py` for what the acceptance suite
  does not reach (e.g. liveness on a zombie, the `x`-open name collision `-<n>`, the window edge). Keep them short.
- `docs/changes/W2-160-evidence.md`: what was built, the KPI map to code and tests, the green run's summary lines,
  and the note that S2's "as `gov launch` writes it" is `launch_worker.sh`'s file names (the ticket's facts line).
- About 260 lines of product code (est_loc); say in your return if it runs far over.

## How to work
- Test first per batch (the `test-driven-development` skill's method); run the acceptance suite after each batch.
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside
  ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, as
  one line (create the empty-home folder first with `mkdir -p`):
  `mkdir -p /tmp/w2-160-eng && env TMPDIR=/tmp/w2-160-eng HOME=/home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-160/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-160 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (the same line with `tests/unit/wait tests/unit/session_watch tests/acceptance/W2-159` for the others). A resource
  gate's refusal is a wait: run it again when it opens; it does not count as a refusal.
- Commit in batches, your paths only, each commit naming its paths:
  `git commit -m "<subject>" --trailer "Task: DAEO-fd0p" --trailer "Role: engineer" --trailer "Implements: DEC-1079, DEC-1073, DEC-1112" -- <paths>`
  (`Implements:` only ids from the ticket's `sources:` that the commit carries: DEC-1079, DEC-1052, DEC-1073,
  DEC-1112, DEC-495, DEC-1119, DEC-1109.) Leave `git status --short` empty at the end (scratch under
  `.gov-runtime/` is ignored).
- One-line commands only; a longer script goes in a file under `/home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/eng/`
  run with `bash` or `python3`. Use literal paths. Never touch `.gov-runtime/scratch/lead/`. No install, no network,
  no `.claude/`, never a live session, never a hook registered anywhere, never a process killed by name. Refused
  twice for the same call by the guard, the sandbox or a hook: stop and say so in your return.

## The ticket's context (from `gov context DAEO-fd0p --role engineer`)
