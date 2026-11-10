# D-10's red-fix list: the review of W2-55's backfill cases reading the register as of the proposal's commit (W2-55, DAEO-arrl)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- Three cases in `tests/acceptance/W2-55/test_w2_55_backfill.py` compared the fixed backfill proposal
  (`docs/research/W2-55-backfill.md`, written in `1c835d47d`) with "the register at the ticket's base", the merge
  base of HEAD with `w2/integrate`.
- On `w2/integrate` that base is HEAD, so the register kept growing and the cases went red (131 entries missing, six
  later SUPERSEDED marks, one later relation). At `1c835d47d` all 8 pass.
- The owner's DEC-1028 (2) option (i): "its backfill case reads the register as of the proposal file's own commit,
  not the moving base". Its append mode is not required: DEC-1083 lifted the KPI line.

## What to review
- **The branch:** `w2/W2-55-d10-tests` in `/home/usain/gov-os-worktrees/W2-55-d10-tests`. Read
  `git -C /home/usain/gov-os-worktrees/W2-55-d10-tests show c41e9bd4f`.
- **The revision:**
  - a `written()` fixture reads the register at `git log -1 --format=%H -- docs/research/W2-55-backfill.md`, and
    fails, not skips, without it;
  - the five comparison cases use it;
  - the "nothing written" case now checks three things: (1) no commit that wrote the proposal changes the register;
    (2) each merge that brought those commits onto HEAD's first-parent line changes nothing in the register against
    its own first parent; (3) the old diff against the merge base, skipped only without `w2/integrate`;
  - README lines.
- **The runs:**
  - the designer's: 3 failed, 55 passed → 58 passed (25 deselected by the breadth cut);
  - the CTO's helper's, outside the sandbox at `2fffdab24` (with `w2/integrate` merged in), with both opt-ins:
    83 passed.

## Check
1. **No expectation lowered:** the proposal still has one row per entry of the register it was made from, in
   order, with domain, scope, lands-in, status note and reason, every relation, the sample. Could `git log -1 -- <proposal>`
   pick a commit that is not the one the proposal was made from? Consider a later commit touching only the file's
   formatting, a rename, or a merge commit.
2. **The "nothing written" case:** does checks 1-3 still catch a backfill branch that writes the register, before
   and after its merge? Could check 2 go red on ordinary later decisions, or miss a register write in a merge?
3. **DEC-1028 (2) (i)** is what was built, and nothing that DEC-1083 lifted (no append mode is required).
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only `tests/acceptance/W2-55/**`
   changed.

KPI id for the verdict block: `w2-55-backfill-base`.

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
