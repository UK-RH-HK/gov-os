Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-151/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-151 — the independent review: MR-1 to MR-6 regenerated from contract.yaml (DAEO-qzca)

You are a fresh, read-only independent reviewer of **W2-151** (`.tickets/DAEO-qzca.md`: read it whole, S1, S2 and the
failure lines). It is a LITE record regeneration (D-6 part 2 item C; DEC-1074 (8), DEC-1109 (2)). READY is computed by
`verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-151` in `/home/usain/gov-os-worktrees/W2-151`, head `539437dff`, made from `w2/integrate` at
  `661a0a49c`. Read `git diff 661a0a49c..539437dff`.
  - The six records `docs/contract/master-rules/MR-1.md` to `MR-6.md`: status PROPOSED → ACCEPTED, the Contract
    version 4.1 → 4.3.
  - The evidence note `docs/changes/W2-151-evidence.md`.
- **The worker's figures:** `gov links --all` STATUS_CONFLICT 6 → 0, no new finding of any code. The schema check is
  ok.

## Check
1. **S1, for each of the six records:** compare it field by field with `docs/contract/contract.yaml` at `661a0a49c`.
   - the status: the Contract's top-level status;
   - the title, the Text line (`text_source`) and the Acceptance line (`acceptance`): the entry's;
   - the version: the file's `version`;
   - the other front-matter keys: kept.

   Is any difference left?
2. **S2:** re-run `gov links --all` on the branch, with `PYTHONPATH=<tree>/src python3 -m gov.cli.main links --all`
   (it writes only its mark), and compare it with the base.
3. **The failure lines:** is any file changed outside the six records and the note? Is `contract.yaml` or
   `CONTRACT_v4.md` touched?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns S1, S2 or the failure lines.

## Write and return
- **You write nothing** in any tree.
- Single simple Bash commands (DEC-1080). No GPU.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- **Your record is your session's final message**, in full. It holds:
  - the twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first);
  - your answers to checks 1-3;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S2", ...}, {"kpi": "F1", ...}, {"kpi": "F2", ...}]}`.
