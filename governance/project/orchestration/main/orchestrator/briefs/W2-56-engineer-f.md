# W2-56 — the engineer's brief, the follow-ups R3 and R5 before the close (DAEO-wnnz)

You are a fresh engineer for **W2-56** (`.tickets/DAEO-wnnz.md`: read **S1**, **S5**, F3, `allowed_paths` and the note
"The owner's choice (DEC-1114 (1))" at its end; and `docs/changes/W2-56-CIT-E.md` §6). W2-56 is merged on
`w2/integrate`; its review left two findings the CTO sends back before the close (DEC-1112 (3), DEC-1114). The
independent test designer's cases are merged into your branch; you build to the KPI lines, the points below and the
interface section at the end, never to the tests. **One small pass, R3 and R5 only.**

## R3 (S1): a killed test run's folders are removed by the next run
A test run (`tests/conftest.py`) makes one folder for its code-graph daemon folders (`gov.codeintel.make_session_base`:
`/tmp/gov-cbm-<uid>-XXXX`, or a short `c???` folder in a launched session's temp folder, or under the temp root where
`/tmp` cannot be written) and each process may make a `gov-path-*` links folder; both are removed when the run ends.
A run killed by SIGKILL or a heavy-slot timeout leaves them, and no sweep covers them.
- **The fix:** each such folder carries a record of its owner **inside it**, and the next run, when it starts (before
  its first case), removes the folders of those names in the place where it makes its own (and the links folders in
  its temp root) whose owner is gone.
- **Settled (the lead, D-15 (a), delegated under DEC-1112 (3)):** the owner check must hold **across pid namespaces**
  (each sandboxed command runs in a pid namespace of its own, so a pid names no process, or another one, in the next
  run's). Use a lock the kernel releases when the owner dies: for example a file inside the folder held with
  `fcntl.flock` (opened close-on-exec) for the run's life; the next run's non-blocking try that succeeds means the
  owner is gone. A pid alone is not enough. This also keeps a folder whose pid is reused (point 6) on the safe side.
- **Never:** a link (or its target), a regular file at such a name, another user's folder, a folder of another name,
  the shared `/tmp/gov-cbm-<uid>` or anything inside it, `/tmp/gov-launch-*`. A folder with no owner record is kept
  unless it was last modified more than 24 hours ago (DEC-902's line). A clean-up that cannot remove something never
  fails, stops or delays the run (a read-only `/tmp`, a 0500 folder: removing or leaving are both right).
- **Paths:** `src/gov/codeintel/__init__.py` (the daemon folder's code only) and `tests/conftest.py` (the run's
  folders only), `tests/unit/codeintel/**`, a short paragraph in `docs/changes/W2-56-CIT-E.md` §6 (S1). Killed runs
  also leave `gov-rebuild-<pid>-*.lock` files: not this pass; name it in your return.

## R5 (S5): a lead gets the launcher's own GOV_STORE
- **Settled (the lead, delegated under DEC-1112 (3)):** `gov launch orchestrator|lead <ticket>` sets `GOV_STORE` in a
  lead's `--settings` env and process environment exactly as a worker's launch does (W2-116 S3: the project's
  `integration_store` from the **main** repository's `governance/project/rebuild.yaml`, the path as written; a setting
  that cannot be used refuses the lead as it refuses a worker, before anything starts). The parent's `GOV_STORE`
  never passes (S5). `TERM` and `TMPDIR` are not passed to a lead (S5's list; sessions start with `-p`; a lead has no
  temp folder, DEC-743 item 7). A worker's launch is unchanged.
- **Paths:** `src/gov/launch/launcher.py` (the lead's settings and its call site only), `src/gov/launch/environ.py`'s
  docstring if it needs a line, `tests/unit/launch/**`, a line in the CIT-E §6 (S5).

## Where you work
- `/home/usain/gov-os-worktrees/W2-56-f`, branch `w2/W2-56-f`, head `52566b514` (integrate `336828354` with the
  designer's cases `473e8ad828d5` merged).
- **You never read `tests/acceptance/W2-56/`** (DEC-820 (c)). Recursive grep carries `--exclude-dir=W2-56`; Grep and
  Glob carry `!tests/acceptance/W2-56/**` as a separate pattern. You see only `gov accept`'s results.
- Write only inside the paths above. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.

## Verify
- Your unit tests: `tests/unit/codeintel` and `tests/unit/launch`, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56-f/src`,
  keeping the sandbox's own short `TMPDIR` (never a long one: the tool's socket path holds at most 107 bytes), `HOME`
  an empty scratch folder with `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`
  and the exclusion of `EMG-d4b-launched.md`; through the heavy slot if the sandbox allows it.
- Then, from the worktree root, once at the end:
  `PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-56`
  (running pytest on the acceptance folder yourself is not allowed; this form also avoids the pinned old `gov`).
  The R3 and R5 cases must turn green; the cases that need the real `/tmp` or a pid namespace skip in your sandbox
  (the lead runs them outside). Name every red, and every red that is red on the base too.
- A small change to `tests/conftest.py` reaches every run of the repository: keep it to the run's folders, and run
  one other small suite (for example `tests/unit/codeintel`) to show nothing else changed.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. No GPU, network or installs.
- **DEC-1080:** one simple command per Bash call. Search again once (DEC-1092 (1)). Every wait and stop by pid only,
  never a name match; before you end, every process you started has ended and nothing of yours is left in `/tmp`.
- Do not merge `w2/integrate`. Under `.gov-runtime/`: hashes as 12 digits; row W2-L423's rule.
- **Commit** on `w2/W2-56-f`, `-- <paths>`, with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1114" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
Your final message: the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed,
evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), the sandbox
and `ps` checks first; the commits; `gov accept W2-56` per line with its counts; the unit counts; every red named.
Refused twice for the same call: stop and say so; no third try. A point you cannot settle: PACKAGES, with your
recommendation and confidence.

## The tests' interface section (verbatim from the README; build to the KPI lines, not to these cases)

### The follow-ups' interface (R3, R5)

**R3 (S1): a killed test run's folders.**

- *What the cases start:* real runs of this repository's pytest on a one-case suite,
  `<python> -m pytest tests/acceptance/W2-56/w2_56_sweep_probe.py --rootdir=<repo> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`,
  from the repository's root (so `tests/conftest.py` applies), each leading a process group of its own. Each run's
  environment is the one the outer test run was started with (`/proc/self/environ`), without `PYTEST_*`,
  `CODEINTEL_DAEMON_BASE`, `TMPDIR`, `TEMP`, `TMP` and `CLAUDE_CODE_TMPDIR`, then one of three settings:
  - *session* (inside a launched session): `TMPDIR` and `CLAUDE_CODE_TMPDIR` both `<case folder>/gov-launch-XXXXXXXX/claude-<uid>`,
    the session folder made as the launcher makes its own (`gov-launch-` and 8 letters, mode 0700);
  - *temp-root* (outside a launched session): `TMPDIR` a folder of the case's own, no `CLAUDE_CODE_TMPDIR`;
  - *real-tmp* (outside, from a shell): no `TMPDIR`, so the temp root is `/tmp`.
- *What they read inside a run:* `CODEINTEL_DAEMON_BASE` (the run's folder for its daemon folders: it must name a
  folder that exists while the run's cases run); the run's **place** is the folder that holds it; the temp root is
  `tempfile.gettempdir()`; the run's **links folders** are the `gov-path-*` folders that hold an entry of its `PATH`
  (today `<temp root>/gov-path-XXXXXXXX/tmpXXXXXXXX`; a run that makes none has none to leave). Inside a launched
  session the run's folder must lie in the session's temp folder (the `gov-launch-` folder above `CLAUDE_CODE_TMPDIR`).
  Two runs started alike must share their place and temp root. The place is never assumed: today it is the session
  folder (session), the temp root where `/tmp` cannot be written (temp-root in the sandbox), or `/tmp`.
- *How a run is killed:* SIGKILL to its process group, once its case has written its record (its folders exist).
- *What they expect:*
  1. The next run started alike has removed a killed run's folder and links folders **before its first case runs**
     (the case reads them gone), and they stay gone after it.
  2. A run held in its case keeps its folder and links folders while another run starts and ends, **whether or not
     the two share a pid namespace**: two commands of one sandboxed session each run in a pid namespace of their own
     (pids 4 and 5 seen here), so the pid a run records for itself may name no process, or another one, in the next
     run's namespace. The held run, let go, ends with 0 and removes its own; the other removes its own at its end.
  3. Never removed or changed, at any age (the cases set 25 hours): a link at a run folder's or a links folder's own
     path, and its target (a folder outside, holding a file); a regular file at such a path; folders of other names
     in the place and the temp root (`gov-cbm-<uid>`, `cbm`, `cc-socks`, `gov-launch-w56XXXXXXXX`,
     `w56-other-XXXXXXXX`, `gov-pathology-XXXXXXXX`, `w56-gov-path-XXXXXXXX`); in the real `/tmp`, the shared
     `/tmp/gov-cbm-<uid>` and a folder of a run folder's form planted inside it (`gov-cbm-<uid>-w56XXXXXXXX`), and the
     live `/tmp/gov-launch-*`. Another user's folder is not planted (it needs a second user): the auditor reads it.
  4. **"Its owner cannot be told" is read as: the folder holds no record of its owner.** A case makes one by emptying
     a killed run's folder **in place** (its own path, so its name is the code's; one file `older-code.txt` inside),
     so the owner's record must lie inside the run's folder (and inside the links folder), not beside it. Fresh, or
     last modified 23 hours ago: kept. Last modified 25 hours ago (the folder and its file): removed by the next run.
  5. A killed run's folders emptied in place, 25 hours old, mode 0500 with a 0500 folder inside holding a file: the
     next run starts, makes its own folder, its case passes, and the whole run takes no more than an ordinary run of
     the same setting, timed just before, and 15 s. Opening and removing them, or leaving them, are both right.
  6. A folder whose recorded owner's pid now belongs to an unrelated live process: no case; keeping it is accepted
     (no case asks for its removal).

**R5 (S5): a lead gets the launcher's own `GOV_STORE`.**

- *What the cases launch:* `gov launch orchestrator <ticket>` and `gov launch lead <ticket>` through gov's console
  entry point, `--gate-override DEC-1112` before `--` (as every launch of these cases), the stand-in CLI and the
  fixture project of S5, an approved ready list naming the ticket at `governance/project/orchestration/ready.txt` in
  the main tree. `integration_store` in the main repository's `governance/project/rebuild.yaml` is the absolute path
  of a link to a folder.
- *What they expect:*
  1. The lead's process environment and its `--settings` env hold `GOV_STORE` equal to that path **as written**
     (the link, not its target), launched from the main tree, and from a worktree of it whose own `rebuild.yaml`
     has no `integration_store` (the main tree's names it, uncommitted).
  2. A parent `GOV_STORE` (`/tmp/zqxw56parent-store`) is never in either; with no `integration_store`, neither holds
     `GOV_STORE`.
  3. `integration_store: relative/store`, or a `rebuild.yaml` that is a list: the lead's launch exits non-zero,
     says `LAUNCH_REFUSED` and names `rebuild.yaml` or `integration_store`, starts no session and leaves no
     `gov-launch-*` folder, as the worker's launch of the same project is refused.
  4. With the parent's `TERM`, `TMPDIR` and every variable S5's cases plant (each value holds `zqxw56parent`): none
     of their values in the lead's process environment or `--settings` env under any name; `TERM`, `TMPDIR` and
     `PYTHONPATH` not there at all; the `--settings` env exactly `GOV_ROLE=orchestrator`, `GOV_TICKET=<ticket>` and,
     where `integration_store` is set, `GOV_STORE`.
  5. A worker's `GOV_STORE` stays the launcher's own (main tree and worktree), and S5's earlier cases are unchanged.
