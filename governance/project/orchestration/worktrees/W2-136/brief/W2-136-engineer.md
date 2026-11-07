Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-136/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-136 — the engineer's brief (DAEO-p3ln)

You are the engineer for **W2-136** (`.tickets/DAEO-p3ln.md`): `gov plan`, the dependency map, the launch batches it
proposes, and `gov launch`'s check against them (DEC-1088; `governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md`).
Read the ticket in full first, with its TESTS-READY and D-1 note.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-136`, branch `w2/W2-136`: `w2/integrate` with the designer's cases
  merged in (`543b6954`).
- **Your paths:** `src/gov/plan/**`, `src/gov/launch/plan_check.py`, `src/gov/launch/launcher.py` (the one call to
  `plan_check` at the argument checks only), `tests/unit/plan/**`, `tests/unit/launch/test_w2_136*`,
  `docs/changes/W2-136-evidence.md`. Register the `plan` command where the CLI's commands are registered only if that
  file is in your paths; if it is not, say so in your return and stop at a working module (the CTO widens the path).
- **You never read `tests/acceptance/W2-136/`** (DEC-957, DEC-1056). Run those cases only through `gov accept W2-136`.
  **Every Grep or Glob call that could reach `tests/acceptance/W2-136/` excludes it (`!tests/acceptance/W2-136/**`), and
  so does every recursive Bash search** (DEC-1093 (2)); if a search shows you a line from there anyway, stop reading it
  and say so in your return.
- **The interface the tests assume** (from the designer's README, given to you here):
  - `gov plan --open [--json] [--ready <file>]`; first line `gov plan: N tickets, B batches, W waits (codes...)`, then
    `batch k: T1, T3, T5`, then for each waiting ticket `T2 waits for T1 (<CODE> <path or id>)`; exit 0 a plan, 1 a plan
    with findings, 2 cannot run; `--json` the shared envelope;
  - codes `NEEDS_WHAT_WRITES`, `WRITES_OVERLAP`, `DEPENDS_ON`, `WAITS_ON`, `READS_WIDE` (a warning, orders nothing),
    `NEEDS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT`, `CYCLE_TIEBREAK`, `OVERRIDE` (with its decision id);
  - overlap decided by the guard's own matcher `gov.guard.decide._match_pattern`, on tracked files and pattern to
    pattern for paths not yet created, erring toward overlap;
  - deterministic: ties and cycles broken by priority, then WBS order, then id;
  - `--ready <file>` writes `# batch k` headers then the dispatcher's lines `<W2> <id> <brief>.md <W2>-A5-<run>.json`;
    nothing is written without it;
  - `plan_check.check_lead(root, ticket_id, *, ready=)` returns `admitted`, `reason` and `override`; the launcher calls
    it for a lead (GOV_ROLE orchestrator with a GOV_TICKET) and refuses, naming what the ticket waits for, starting no
    session; a `plan_override: <DEC-id>` admits and is logged;
  - never a gate elsewhere (no close, landing, claim, readiness or hook module imports `gov.plan`).

## Tests and evidence
- **Unit tests** in `tests/unit/plan/` and `tests/unit/launch/test_w2_136*`, on planted ticket stores. No GPU.
- **The evidence record:** one row per KPI line S1-S10; S11 (under 5 s on this repository) is the CTO's.
- **Every run** through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **`gov accept` drops `PYTHON*` variables:** a scratch HOME whose `.local` links to `/home/usain/.local`.
- **When your unit tests pass:** `python3 -m gov.cli.main accept W2-136 --root <worktree>` and its counts; then
  `tests/unit/launch tests/acceptance/W2-20` with `-m "not local_only" -k "not real and not green_here and not time_limit"`,
  every red named.
- **Before you end your session, every run you started has finished:** never end with a background run going.

## Rules
The hidden-half rule; no GPU; DEC-1080 (Read and Grep; one simple command per Bash call; no `cd … &&`, no `git -C`);
do not merge `w2/integrate`; commit on `w2/W2-136` with
`--trailer "Task: DAEO-p3ln" --trailer "Implements: DEC-1088" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, the sandbox and `ps` checks first: the diff's size, the unit tests,
`gov accept`'s counts, and the regression's counts with every red named.
