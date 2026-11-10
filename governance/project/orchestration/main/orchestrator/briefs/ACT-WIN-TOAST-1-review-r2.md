# The review of ACT-WIN-TOAST-1, round 2: the class and the two fixed findings (DEC-1112 (3))

You are a fresh, read-only independent reviewer, **round 2 of at most two** (DEC-1010). READY is computed by
`verdict.py` from your block.

## Round 1 (READY; `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/ACT-WIN-TOAST-1-review.md`, read it)
- **F1:** the operator agent classes a test-map removal (b). The package now says (b), with the owner's yes.
- **F2:** `undo` overwrote a later change. It now refuses unless the map is as this ACT left it.
- **F3:** `apply` installed an altered candidate. It now refuses a candidate that is not the reviewed one, and
  restores the backup if the result is not the applied state.

## What to review
- `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/win-toast/apply.sh` (changed),
  `rehearse.sh` (two negative steps added), `rehearsal.log` (re-run).
- `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-WIN-TOAST-1.md` (class and
  §4 updated).
- The candidate and its hashes are unchanged from round 1.

## Check
1. F1 to F3 are closed, and nothing else in `apply.sh` changed meaning. Reproduce F2 and F3 in a scratch clone of
   your own under your TMPDIR, as round 1 did.
2. The package's class (b) and its steps match what the operator agent will do.

KPI id for the verdict block: `act-win-toast-1`.

You write nothing in any tree but your own scratch clone; never run `apply` on the live map.

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
