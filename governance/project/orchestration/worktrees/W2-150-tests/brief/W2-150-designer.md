Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-150-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-150 — the independent test designer's brief: memory's import closure free of the gates (DAEO-ijf5)

You are the independent test designer for **W2-150** (`.tickets/DAEO-ijf5.md`: read it whole). It is D-6 part 2's
code item (P1-PLAN §A P1-6 item 1, §D; DEC-1039 (2), DEC-1040 (1), DEC-1109 (2)). Its source is INVESTIGATION-1
part E's E-2 (`governance/project/orchestration/packages/INVESTIGATION-1-parts/E.md`): memory's import closure takes
in 18,063 lines in 77 modules through four edges into the gates' code. Write the acceptance tests **before** the
engineer, from the KPI lines S1 to S5 and the failure lines.

## What the cases must show
- **S1, the closure (red today):** a **static** walk of `src/gov`'s imports. Use `ast`, every `import` and `from …
  import` statement, at module level **and inside functions and methods**. Resolve relative imports, and a
  `from gov.x import y` where `y` is a submodule. Start from every module of `gov.retrieval`, `gov.retrieve`,
  `gov.store` and `gov.secrets`. The walk must reach no module of `gov.close`, no module of `gov.guard`, and not
  `gov.decisions.checker`.
  - On failure, print the path of imports that reaches each gate module, for example
    `gov.store.loader -> gov.close.fingerprint -> …`. The engineer then sees which edge is left.
  - Read `src/gov` only as data, through the walk. That is what the case judges.
- **S2, the four edges (red today), one case each:**
  - `gov.store.loader`'s own imports name no `gov.close.*` and no `gov.tasks.tickets`;
  - `gov.retrieve.command`'s closure does not reach `gov.decisions.checker`;
  - `gov.secrets`' does not reach `gov.guard.*`;
  - `gov.retrieval.measure`'s does not reach `gov.guard.*`.
- **S3, the old names stay (green today, guards):** each name can be imported from its old module in a fresh
  subprocess (`python3 -c`):
  - `gov.close.fingerprint.of_commit`;
  - `gov.guard.decide._match_pattern`;
  - `gov.tasks.tickets.TICKETS_REL`;
  - `gov.guard.runs.root`;
  - `gov.decisions.register.leave_out`;
  - `gov.guard.reads.evaluation_sets`, `PolicyError`, `PATH_MAP_REL`, `SETS_KEY`, `set_fault`.

  Add one behaviour check per moved helper where it is cheap and needs no planted repository beyond a temporary git
  folder, for example `_match_pattern` on two patterns.
- **S4 (green today, guard):** in a fresh subprocess, `import gov.guard.decide` loads no module outside `gov.guard`,
  `gov.util` and the standard library. Compare `sys.modules` before and after.

Map every case to its KPI line in a README, with the expected red reason. S5 (the unit tests moving with their
helpers) is the reviewer's to check. Note that in the README.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-150-tests`, branch `w2/W2-150-tests`, made from `w2/integrate`.
  Write only `tests/acceptance/W2-150/`.
- **Your record:** your whole return is your session's **final message**, in full.

## Rules
- **No implementation exists yet.** You may read `src/gov/**` as the subject of the walk, and E.md. Never open the
  engineer's worktree (base name `W2-150`) or its branch.
- No GPU, model, network or installs.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. The walk reads source files, never `fixtures/evaluation/**`.
- **Search again once (DEC-1092 (1)).**
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-150-tests/src` and a scratch HOME. Then run
  `python3 -m gov.cli.main accept W2-150 --root /home/usain/gov-os-worktrees/W2-150-tests`. Never the full suite.
- **DEC-1080:** use the Read and Grep tools, one simple command per Bash call, and no `cd … &&` chains.
- **Commit** on `w2/W2-150-tests`, only `tests/acceptance/W2-150/`, with
  `--trailer "Task: DAEO-ijf5" --trailer "Implements: DEC-1109, DEC-1039" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
- The twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first).
- The cases: node id, KPI line, expectation, red or green today and why. For each red S1 and S2 case, the import
  path it prints.
- The commit, `gov accept`'s counts and `TESTS-READY`.
- `discoveries`.
