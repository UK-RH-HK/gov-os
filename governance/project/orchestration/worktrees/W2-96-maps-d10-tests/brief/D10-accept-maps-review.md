Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-96-maps-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of W1-46's and W1-27's README maps made readable by gov accept (W2-96, DAEO-ouet)

You are a fresh, read-only independent reviewer. **Narrow scope: two README maps.** READY is computed by
`verdict.py` from your block.

## What happened
- `gov accept W1-46` and `gov accept W1-27` stopped with `ACCEPT_MAP_UNREADABLE`: a map row named no KPI line in the
  form the reader takes. The cases themselves pass.
- A test designer fixed both READMEs.
  - **W1-46:** the `DEC-242` row now names "Success 1". Four rows that listed "failures 1, 2, 8" now name each line
    in full.
  - **W1-27:** ten headings `### Success KPI N` became `### Success N`.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-96-maps-d10-tests show 48c2cd33b`.
- **The CTO's helper's runs outside the sandbox,** the declared way, at the branch with integrate merged:
  - `gov accept W1-27`: outcome fail, 67 passed and 0 failed. success-8 answers fail with no failed case: its items
    name parametrised rows in a form the reader does not match, and D-4's cut moved three of the four to `breadth`.
  - `gov accept W1-46`: outcome fail, 134 passed and 0 failed. The lines that answer fail with no failed case name
    cases D-4's cut moved to `breadth`, such as success-10's file.

## Check
1. **Same meaning:** does every row still map exactly the cases it meant to, to the lines it meant? Was "DEC-242 (no
   KPI line of its own)" really success 1's? No case dropped or moved.
2. **The remaining fails:** confirm they come from D-4's cut (cases the default run does not collect) and the
   parametrised-row form, not from this revision. Say whether a map fix within these READMEs could clear them
   without lowering what a line requires.
3. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only the two READMEs changed.

KPI id for the verdict block: `accept-maps-readable`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<the branch's worktree>/src`, a TMPDIR folder of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` if you set an empty HOME (so pytest is found).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
