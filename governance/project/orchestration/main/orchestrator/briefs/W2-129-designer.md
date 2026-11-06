# W2-129 — the independent test designer's brief (DAEO-q7lk)

You are the independent test designer for **W2-129** (`.tickets/DAEO-q7lk.md`): `gov links`, one cheap, incremental,
read-only link-integrity check that finds every unlinked or contradicted record and names the role that fixes it; a
notice, never a gate. Read the ticket in full first, and its design, LINK-INTEGRITY §4
(`governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md`). The ticket's `acceptance_tests.author` field
describes the planted repository it wants. The owner wants it built, tested and reviewed before re-pin window 4
(DEC-1087 (4)).

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-129-tests`, branch `w2/W2-129-tests`, made from `w2/integrate`.
- You write only `tests/acceptance/W2-129/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads. Its header is `| KPI line | Test (node id) | On integrate | Why |`, with one id in each KPI cell
  (`S1` … or `success-1` …; `F1` … for the failure lines) and the test in backticks (as
  `tests/acceptance/W2-133/README.md`).
- You may read any code on `w2/integrate` (there is no `src/gov/links/` yet): the loader's `register_statements`
  (`src/gov/store/loader.py`, W2-92), `src/gov/decisions/propagation.py` (W2-55), the store's id grammar, and
  `docs/research/W2-92-proto-drift.py`.

## What the cases must show
One case or more per KPI success line (13 lines: number them S1 to S13 in the order the ticket gives them) and per
failure line (F1 to F6), on the planted repository the ticket describes, in a temporary folder. Plant:
- a register with each statement form: `Changes:`, `Changed by:`, `Supersedes:` with ids alone and with a part, free
  text "amended by", an entry with no mark, a PROPOSED and a REJECTED entry;
- ARCHIVE-SUPERSEDED with §A and §B, and DECISIONS-IN-FORCE;
- tickets with sources, KPI brackets, an unknown id and a missing acceptance path;
- commits with `Task:`, `Implements:` and `Role:`, with a landing commit among them;
- a lesson, a plan file, a kernel skill line citing a PROPOSED decision, and a `contract.yaml` with a provider that
  does not exist;
- a second planted repository with no register and no tickets.

Each finding code (UNMARKED_CHANGE, UNKNOWN_ID, UNLINKED_ID, STATUS_CONFLICT, NOT_IN_FORCE_AS_RULE,
ENFORCES_SUPERSEDED) is found, and is not found where it should not be.
- The output's first line and per-finding line, `--json`, the exit codes 0, 1 and 2.
- The mark and the incremental range: `--since`, the mark, and a refusal with neither.
- `--propose-marks` and `--propose-sources`: their patches apply with `git apply --check`.
- No file written but the mark, the tree hashed before and after.
- "Not applicable" on the second repository.
- The fixed role table.

The timing line (S12) is the CTO's measured run, not a test: map it to a README note only. Never-a-gate (S11) is
tested by checking that no close, queue, landing, launch, claim or readiness module imports or calls it (a source
scan), plus a note.

Every case is red on integrate for the right reason (there is no `gov links` command yet), or a green guard; say which.

## Rules
- No GPU, no model, no network. Never this repository's store.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot (`EMG-common.md`), with `PYTHONUSERBASE=/home/usain/.local`, and run
  `python3 -m gov.cli.main accept W2-129 --root <your worktree>` to show the runner reads your map.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-129-tests` with
  `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1073" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with:
- the case list (node id, KPI line, red or green, and why);
- the commit;
- `gov accept`'s counts;
- the interface the cases assume (the command, its options, the output lines, the module the engineer must provide);
- anything untestable or ambiguous, as `discoveries`.
