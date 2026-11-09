Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-152 — the independent review, round 2, the last (DEC-1010) (DAEO-o5x1)

You are a fresh, read-only independent reviewer. Review **W2-152** (`.tickets/DAEO-o5x1.md`: read it in full, with
its body's "Interface" and "Clarified after the test design"): `gov brief`, a filled brief from the ticket and the
facts file, refused when the ticket is not READY by code (DEC-1050, DEC-1052, DEC-1083, DEC-1088 (3)). The design is
`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §B ("Filling") and §D TPL-3 and TPL-5. The
templates it fills are `template/governance/kernel/templates/`.

## What to review
- **Round 1:** `governance/project/orchestration/reviews/w2-152-r1.md` (NOT READY on F1; read all its findings).
- **The branch now:** `w2/W2-152` in `/home/usain/gov-os-worktrees/W2-152` at `09fc68645`, against `w2/integrate`.
  Since round 1: the designer's revision 2 (11 cases, TESTS-READY `50902d8a422f`, merged `645fcfd4`) and the
  engineer's fix `09fc68645` (F1, F3, F4, F6, and F5 riding along). The CTO kept F7, F8, F9, F10 and F11 as rows, and
  decided F2 as option (a) (D5-STATUS).
- **The runs (the CTO's, outside the sandbox):** `gov accept W2-152` 67/67; `gov accept W2-128` 92/92; unit tests
  25/25; schema ok.

## Check
- Is F1 closed: does every role's whole template now pass through the "until <ticket>" check, the lead's common part
  included? Probe it with a closed planted ticket.
- Are F3, F4, F5 and F6 closed as the fixes say, with named refusals and no traceback? Re-run round 1's robustness
  probes.
- Did the fix change anything else (S1's determinism, S4, the ready check's split)?
- Every KPI line S1 to S10 and F1 to F3 again, briefly: a pass stays a pass only if the code still holds it.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- **You write nothing** in any tree, and run nothing that writes: tests read-only with `-p no:cacheprovider`, only
  `tests/acceptance/W2-152`, `tests/unit/brief` and `gov brief` itself. Single simple Bash commands (DEC-1080). The
  hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words. Then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your verdict per line, and every finding with its lines and `scope: in|out`;
  - at the end, the fenced `verdict` block in DEC-1010's form, one entry per line (S1 to S10, F1 to F3):
    `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`
