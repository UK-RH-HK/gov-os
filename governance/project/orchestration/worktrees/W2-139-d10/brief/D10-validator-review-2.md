Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-139-d10/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of the plan validator's two reads (W2-139, DAEO-ongl)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- The plan validator (`docs/plan/tools/validate_w2.py`, W2-51's) gave 5 FAIL on `w2/integrate`. DEC-1112 (3) put
  them on D-10's red-fix list. Two were the validator's own reads:
  - **`wave2-tickets`** read W2 ids only from the WBS §1 table, while the WBS says "The later tickets (W2-59 onwards)
    are in §2's cards only" (31 ids failed).
  - **`ticket-contract-ids-exist`** read `CAP-1` and `CAP-2` inside `ACT-OLLAMA-CAP-1/2` as Contract ids.
- A product-spec worker revised the validator under W2-139's ticket. The CTO then fixed three plan records on
  `w2/integrate` itself (`966a9ac67`): W2-60's split-parent heading became `#### Split: W2-60 …`, and cards were
  added for W2-63 and W2-66c.

## What to review
- **The branch:** `w2/W2-139-d10` in `/home/usain/gov-os-worktrees/W2-139-d10`. Read
  `git -C /home/usain/gov-os-worktrees/W2-139-d10 diff adec4718a..d76e79996`.
  - `4771fba13` is the CTO's ticket commit (the two files in W2-139's paths).
  - `d76e79996` is the worker's change: `validate_w2.py`, plus three cases in `tests/unit/plan/test_validate_w2.py`.
- **The worker's runs:**
  - `tests/unit/plan` 69 → 72 passed;
  - `tests/acceptance/W2-51` 47 passed before and after;
  - `tests/acceptance/W2-49/test_w2_49_validator_lines.py` 12 passed before and after;
  - pattern matches over the repository 3,476 → 3,463, the 13 lost all inside longer names; 291 distinct ids before
    and after.
- **The CTO's run:** the branch's validator with `--root /home/usain/Dynamic-Agentic-Engineering-OS` (integrate with
  the records fixed) gave `PASS wave2-tickets — 109 W2 ids agree … (78 in the §1 table, 31 in §2's cards only)`.
  `RESULT: 2 FAIL`: contract-items-delivered (CAP-22.c) and contract-items-cited-by-tests. Those wait on P1-11's
  Contract re-baseline and on W2-37's tests.

## Check
1. **No fail-open.** Can the §2 reading hide a real disagreement? Consider:
   - a card for a ticket that does not exist;
   - a heading that is not a card;
   - a split parent;
   - a card outside §2;
   - an id in a card's body text rather than its heading.
   Is the PASS line's count honest?
2. **The CAP pattern.** Does excluding an id preceded by a hyphen lose any real Contract citation anywhere the
   validator reads it (tickets, acceptance tests, CIT-P lines, the WBS baseline)? Try forms such as `(CAP-22.c)`,
   `—CAP-1`, `CAP-22.c/CAP-22.b`, and a line that starts with the id.
3. **The three unit cases** fail against the old validator and pin the new behaviour, not an incidental string.
4. **Trailers:** Task, Role, Implements and Co-Authored-By on `d76e79996`. Only the two files changed, plus the
   CTO's ticket line.

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
