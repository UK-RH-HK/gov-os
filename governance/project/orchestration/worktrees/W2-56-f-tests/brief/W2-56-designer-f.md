# W2-56 — the independent test designer's brief, the two follow-ups R3 and R5 before the close (DAEO-wnnz)

You are a fresh independent test designer for **W2-56** (`.tickets/DAEO-wnnz.md`: read **S1**, **S5**, F3 and the note
"The owner's choice (DEC-1114 (1))" at its end). W2-56 is merged on `w2/integrate`; its review (round 1, READY) left
two findings that the CTO sends back as follow-ups before the close, tests first (DEC-1112 (3), DEC-1114). Your cases
come first; an engineer then builds to the KPI lines and to the interface section you write. FULL profile: thorough
on these two points, nothing beyond them.

## R3 (S1: "cleaned when the session ends, so no daemon folder is left behind")
**What happens today:** a test run (the repository's own pytest, `tests/conftest.py`) makes one folder for its
code-graph daemon folders, `/tmp/gov-cbm-<uid>-XXXX` (in a `gov launch` session: a short folder inside the launched
session's temp folder), names it in `CODEINTEL_DAEMON_BASE`, and removes it when the run ends. Each process of the run
may also make a folder of links for the tool off `PATH` (`gov-path-*`, in its temp root). A run that is **killed**
(SIGKILL, a heavy-slot timeout) leaves both behind, and no weekly sweep covers them (DEC-902's sweep list names
`/tmp/gov-cbm-<uid>/*` and `/tmp/gov-launch-*` only).

**What must hold after the fix (the behaviour your cases pin):**
1. A run killed after it has made its folder(s) leaves them; **the next test run, when it starts, removes them** (the
   folders in the place where that run makes its own: `/tmp` outside a launched session, the launched session's temp
   folder inside one; the links folder in its temp root).
2. **A live run's folder is never removed:** while run A is still running (for example held in a case until a file
   appears), run B starts and ends; A's folder is still there, and A then ends normally and removes its own.
3. Only this user's real directories with the run-folder names are touched: never a link (and never its target),
   never another user's folder, never the shared `/tmp/gov-cbm-<uid>` (the default daemon place, which live sessions
   outside a test run use) or anything inside it, never `/tmp/gov-launch-*`, never a folder of another name.
4. A folder whose owner cannot be told (made by older code, or being made at that moment) is kept, unless it was last
   modified more than 24 hours ago (DEC-902's line); then it is removed.
5. A clean-up that cannot remove something (a read-only `/tmp` inside the sandbox, a permission error) never fails,
   stops or delays the run: the run starts and its cases run as before.
6. Optional, your judgement: a folder whose recorded owner's pid now belongs to an unrelated live process. Keeping it
   is the safe side; say in the README which way your cases (if any) read it.

How the next run tells a live owner from a dead one is the engineer's choice (for example the owner's pid, and its
start time, recorded in the folder). **Prefer cases that do not depend on that choice:** start real nested runs of
this repository's pytest on a small planted suite (as `test_w2_56_suite_daemon.py` and `w2_56_daemon_probe.py`
already do), learn each run's folder from inside it (a case writes `CODEINTEL_DAEMON_BASE` to a file), kill one with
SIGKILL by its pid, and start the next. Where a case must plant a folder (points 3 and 4), plant only what needs no
knowledge of the record (a link, a bare folder with an old modification time, another name).

## R5 (S5: "the launcher's own values")
**What happens today:** since S5, a lead started by `gov launch orchestrator|lead <ticket>` gets the cleaned
environment too. A worker's launch sets `GOV_STORE` itself (W2-116 S3: the project's `integration_store`, read from
the **main** repository's `governance/project/rebuild.yaml`, the link path as written), but a lead's settings carry
only `GOV_ROLE=orchestrator` and `GOV_TICKET`. So a lead's plain `gov retrieve` in a fresh worktree answers
`STORE_MISSING`, where before S5 it could inherit the parent's `GOV_STORE`.

**The CTO's decision (delegated, DEC-1112 (3)): the lead gets the launcher's own `GOV_STORE`, exactly as a worker
does, and never the parent's.** S5 forbids the parent's `CLAUDE*` and `GOV*` values and allows "the launcher's own
values"; the CIT-E (`docs/changes/W2-56-CIT-E.md` §6) already names `GOV_STORE` as one. `TERM` and `TMPDIR` are not
passed to a lead: S5's list does not hold them, sessions start with `-p`, and a lead has no temp folder of its own
(DEC-743 item 7).

**What must hold (the behaviour your cases pin):**
1. With `integration_store` set in the main repository's `rebuild.yaml`, an admitted lead's session gets `GOV_STORE`
   equal to that path as written (not the link's target), in its process environment and in its `--settings` env,
   whether it is launched from the main tree or from a worktree of it whose own `rebuild.yaml` lacks the line.
2. A parent's `GOV_STORE` (a different, planted value) never reaches the lead, with the setting and without it;
   without the setting, the lead has no `GOV_STORE` at all.
3. A setting that cannot be used (not an absolute path, a file that is not a map) refuses the lead's launch as it
   refuses a worker's: no session started, the reason named.
4. The lead's environment holds no parent `TERM` and no parent `TMPDIR`, and its `--settings` env holds
   `GOV_ROLE=orchestrator`, its `GOV_TICKET` and (where set) `GOV_STORE`, nothing else.
5. Guard: a worker's environment is unchanged (S5's existing cases stay green).

A lead launch is admitted only by the plan's check and the resource gate: `tests/acceptance/W2-136/test_w2_136_launch_check.py`
shows how a planted repository admits one (a ready list, the gate's readings planted). Use a stand-in CLI as
`test_w2_56_environment.py` does.

## Your files and the README
- Write only `tests/acceptance/W2-56/` (new files beside the existing ones; change no existing case; a support helper
  added to a support file is fine).
- README: map each new case **by full node id** to S1 (R3) or S5 (R5) and to its expected red reason; a section
  **"The follow-ups' interface (R3, R5)"** that the engineer is given verbatim in its brief (what your cases call,
  set, read and expect; no code to write); and one line each: `Follow-up: R3 (DEC-1112 (3))`, `Follow-up: R5
  (DEC-1112 (3); the lead gets the launcher's own GOV_STORE)`.
- Show every new case red on today's integrated code for the stated reason, except its guards (green), and say which
  cases need the real `/tmp` (outside a launched session): mark those so the existing exclusion
  (`-k "not real ..."`) leaves them out in the sandbox, as the existing real cases are; the CTO's lead runs them
  outside the sandbox.

## Where you work, and the rules
- `/home/usain/gov-os-worktrees/W2-56-f-tests`, branch `w2/W2-56-f-tests`, from `w2/integrate` at `336828354`.
- **Never read this follow-up's implementation (DEC-820 (c)):** do not open, grep or list `src/gov/codeintel/__init__.py`,
  `src/gov/launch/launcher.py`, `src/gov/launch/environ.py`, `src/gov/launch/sandbox.py`, `tests/conftest.py`,
  `tests/unit/codeintel/**` or `tests/unit/launch/**`, nor the engineer's worktree `/home/usain/gov-os-worktrees/W2-56-f`
  or the branch `w2/W2-56-f`. Grep and Glob calls that could reach them carry those exclusions. You work from the
  ticket, the CIT-E, the existing W2-56 README and support files, and the code that is not this ticket's
  (`src/gov/launch/store.py`, `src/gov/launch/plan_check.py`, `src/gov/launch/gate.py`, the W2-116 and W2-136 tests).
- Run your new file(s) with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56-f-tests/src`, keeping the sandbox's own
  short `TMPDIR` (never a long one: the tool's socket path holds at most 107 bytes), `HOME` an empty scratch folder,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`, the exclusion of `EMG-d4b-launched.md`. Then once, from
  the worktree root: `PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-56`
  and report its counts.
- No GPU, model, network or installs. The hidden-half rule: never open the evaluation sets' hidden half or the run
  folders outside this repository, as `EMG-common.md` names them. DEC-1080: Read and Grep tools, one simple command per
  Bash call. Search again once (DEC-1092 (1)). Every wait and stop by pid only, never a name match; before you end,
  every process you started (the nested runs included) has ended, and nothing of yours is left in `/tmp`.
- Under `.gov-runtime/`: hashes as 12 digits; row W2-L423's rule.
- **Commit** on `w2/W2-56-f-tests` with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1114" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A KPI point you find ambiguous: do not guess; return PACKAGES with your recommendation and confidence.

## Return
Your final message: the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed,
evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), the sandbox
and `ps` checks first; the cases (node id, line, red or green today and why); the interface section's text; the
commit; `gov accept`'s counts; and `TESTS-READY <head>`. Refused twice for the same call: stop and say so.
