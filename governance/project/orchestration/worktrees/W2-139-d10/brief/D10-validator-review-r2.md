Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-139-d10/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of the plan validator, round 2 (W2-139, DAEO-ongl)

You are a fresh, read-only independent reviewer, **round 2 of at most two** (DEC-1010). READY is computed by
`verdict.py` from your block.

## Round 1
- The round-1 review (its record is `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/D10-validator-review.md`;
  read it) was NOT READY on F1: three-digit W2 ids were read on neither side, so `wave2-tickets` PASSed over 23
  tickets with no WBS entry.
- F2 (a hyphen-joined pair) and F3 (a card for an early ticket whose §1 row is gone) are rows. F4: the substring
  counts.
- The CTO added WBS cards for the 23 tickets on `w2/integrate` (`34f97dfea`).

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-139-d10 show c57955a96`:
  - one shared id pattern `W2-[0-9]{2,3}[a-z]?` for the tickets, §1's rows, §2's cards and the triage column;
  - three new unit cases;
  - case 1 compared by equality.
- **The worker's runs:**
  - validator `PASS wave2-tickets — 160 W2 ids agree … (106 in the §1 table, 54 in §2's cards only)`;
  - `RESULT: 3 FAIL`: CAP-22.c, the ten uncited items, and a new `ticket-contract-ids-exist — CAP-1 (W2-134)`. That
    last one is prose in W2-134's KPI ("CAP-1 never matches CAP-10"), the CTO's record to settle;
  - `tests/unit/plan` 75 passed, W2-51 47 passed, W2-49's validator lines 12 passed.

## Check
1. F1 closed: are all three-digit ids read on both sides, with nothing new hidden (four digits, letter suffixes, bold
   rows)? Is the PASS line honest?
2. F4 closed.
3. No regression in what round 1 passed (the CAP pattern, the §2 cards).
4. Trailers on `c57955a96`.

KPI ids for the verdict block: `validator-wbs-ids`, `validator-cap-pattern`.

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
