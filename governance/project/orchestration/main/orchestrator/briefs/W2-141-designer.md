# W2-141 — the independent test designer's brief (DAEO-xwro)

You are the independent test designer for **W2-141** (`.tickets/DAEO-xwro.md`): the guard refuses an engineer's Grep,
Glob or recursive Bash search that can reach its own ticket's acceptance folder unless the call excludes it, and the
refusal says how (DEC-1093 (2)). Read the ticket in full first. Its KPI lines S1 to S3 (and its three failure lines)
are what you test. Profile STANDARD: every KPI line's success and failure, plus the key edge cases; no combinatorial
expansion.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-141-tests`, branch `w2/W2-141-tests`, made from `w2/integrate` today.
- You write only `tests/acceptance/W2-141/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads. Its header is `| KPI line | Test (node id) | On integrate | Why |`, with one id such as `S1` in each KPI
  cell and the test in backticks with its full node id (as `tests/acceptance/W2-133/README.md`). State there the
  interface the tests assume (the decide function and its call form, the refusal's wording that names the folder and
  the exclusion), so the engineer builds to it.
- **Your record:** write your return (the twelve fields below) also to
  `/home/usain/gov-os-worktrees/W2-141-tests/.gov-runtime/scratch/lead/W2-141-designer-return.md` (you cannot write the
  main tree's scratch).
- You may read any code on `w2/integrate`: `src/gov/guard/decide.py` (the decide function the ticket names: "planted
  calls against the guard's decide function, no real session"), `src/gov/guard/reads.py` (its Grep and Glob tool-name
  branches and its recursive Bash reads), `src/gov/guard/role_paths.py`, the existing tests under `tests/unit/guard/`
  and `tests/acceptance/W2-84/` for how a planted call, a role, a ticket and a path map are set up, and
  `.gov-runtime/scratch/orchestrator/tools/guard4_check.py`'s G-14 cases (S3: they must pass unchanged; your green
  guards reproduce their decisions through the decide function).

## What the cases must show (from the ticket)
- **S1:** for an engineer on ticket T, Grep and Glob calls whose path and pattern can reach `tests/acceptance/<T>/`
  (the repository root, `tests/`, `tests/acceptance/`, a pattern such as `**/*.py`) refused unless the call excludes
  it; the refusal names the folder and says how (for Grep a glob such as `!tests/acceptance/<T>/**`). The same calls
  with the exclusion allowed. Red on integrate where today's guard allows the broad search.
- **S2:** Bash recursive searches (`grep -r`/`-R`, `rg`, `ag`, `ack`, `find` with a reading action or piped into a
  reader) started at a folder that holds `tests/acceptance/<T>/`, refused unless excluded (`grep --exclude-dir`,
  `rg -g '!…'`, `find -not -path` / `-prune`); the refusal says how. Planted commands; each refused or allowed as
  stated.
- **S3 and the failure lines:** nothing else newly refused: a search that cannot reach the folder or that excludes it;
  other tickets' acceptance tests readable (DEC-963); the test designer, reviewer, auditor and orchestrator
  unaffected; a grep for the tests' names by pattern only stays allowed. Green guards on integrate.
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** there is none yet; never open
  `/home/usain/gov-os-worktrees/W2-141` or the branch `w2/W2-141` if either appears, and never read the engineer's
  files on this ticket. You work from the ticket's KPI lines and today's integrate code only.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree, never from `/home/usain/gov-os-worktrees/` or `/home/usain/`, so no search can reach this ticket's engineer
  worktree; if a search shows you a line of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- No GPU, no model, no network, no real session; planted calls only.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names (where the sandbox allows it), with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-141-tests/src`, and run
  `python3 -m gov.cli.main accept W2-141 --root /home/usain/gov-os-worktrees/W2-141-tests` to show the runner reads
  your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-141-tests`, only `tests/acceptance/W2-141/`, with
  `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1093, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished: do not end with a background
  run still going.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), the commit, `gov accept`'s counts, `TESTS-READY` text, and anything
untestable or ambiguous as `discoveries` or a decision package with your recommendation and confidence.
