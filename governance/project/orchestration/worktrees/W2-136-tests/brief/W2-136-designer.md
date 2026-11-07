Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-136-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-136 — the independent test designer's brief (DAEO-p3ln)

You are the independent test designer for **W2-136** (`.tickets/DAEO-p3ln.md`): `gov plan`, the dependency map from
each ticket's writes (`allowed_paths`), `reads:`, `needs:`, `waits_on:` and `depends_on`, the launch batches it proposes,
and `gov launch`'s check against them (DEC-1088; `governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md`).
Read the ticket in full first. Its KPI lines S1 to S10 are what you test; S11 (under 5 s on this repository) is the
CTO's measure.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-136-tests`, branch `w2/W2-136-tests` (from `w2/integrate`).
- You write only `tests/acceptance/W2-136/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads, header `| KPI line | Test (node id) | On integrate | Why |`, one id such as `S1` per KPI cell, the test
  in backticks (as `tests/acceptance/W2-133/README.md`). State there the interface the tests assume (the command, its
  output lines, `--json`, `--ready <file>`, the exit codes, the codes `NEEDS_WHAT_WRITES`, `WRITES_OVERLAP`,
  `DEPENDS_ON`, `WAITS_ON`, `READS_WIDE`, `NEEDS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT`, `CYCLE_TIEBREAK`,
  `OVERRIDE`, and `src/gov/launch/plan_check.py`'s one function the launcher calls), so the engineer builds to it.
- You may read any code on `w2/integrate` (there is no implementation yet): the guard's pattern matcher (S3 says
  overlap is decided by it: find it under `src/gov/` and name it), `src/gov/launch/launcher.py` (its argument checks,
  for S9), the ticket store's reader, and the dispatcher's ready-list form (`.gov-runtime/scratch/orchestrator/dispatch/ready.txt`
  and `dispatcher.py`) for S7.

## What the cases must show
- A **planted ticket store** in a temporary folder for every case (never this repository's `.tickets/`), with the
  tickets each KPI line names: overlapping writes, `needs:` on a path another writes, `depends_on`, an unfinished
  `waits_on`, a wide `reads:`, a ticket with no `needs:`, `deps` disagreeing with `depends_on`, an unknown wait, ties,
  a needs-after-write cycle, a `plan_override: <DEC-id>`, and a shuffled file order (S4).
- **S7:** `--ready <file>` writes the batches in the ready-list form and nothing else; without it, the tree is hashed
  unchanged.
- **S9:** with a planted ready list: a lead not in a batch refused (naming what it waits for), a wait unmet refused, a
  wait met admitted, an override admitted and logged. No session is started (test the check function, and the
  launcher's refusal path with a stub).
- **S10:** a source scan that no close, landing, claim, readiness or hook module imports `gov.plan`.
- Say for each case whether it is red on integrate for the right reason (no `gov plan` yet), or a green guard.

## Rules
- No GPU, no model, no network.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, with `PYTHONUSERBASE=/home/usain/.local`, and run
  `python3 -m gov.cli.main accept W2-136 --root <your worktree>` (a scratch HOME whose `.local` links to
  `/home/usain/.local`) to show the runner reads your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains and no
  `git -C`; one line before any command that will ask for permission.
- **Commit** on `w2/W2-136-tests` with
  `--trailer "Task: DAEO-p3ln" --trailer "Implements: DEC-1088" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished: do not end with a background
  run still going.

## Return
The twelve labelled fields of `EMG-common.md`, with the case list (node id, KPI line, red or green on integrate, and
why), the commit, `gov accept`'s counts, and anything untestable or ambiguous as `discoveries`.
