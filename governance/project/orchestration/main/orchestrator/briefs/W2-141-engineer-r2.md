# W2-141 — the engineer's brief, round 2 (DAEO-xwro)

You are a fresh engineer for **W2-141** (`.tickets/DAEO-xwro.md`). Round 1 (`a3dbf84f` on `w2/W2-141`) built the decide
side and the staged hook copies; `gov accept W2-141` passes 182/182. Its regression left **15 rows of
`tests/unit/guard/test_reads.py`** red: they expect the old refusal of a search into the engineer's own acceptance
folder (one of them, row 44, now a refusal under S1). The CTO has put that file in the ticket's paths.

**Your job:** revise only those rows of `tests/unit/guard/test_reads.py` to the new behaviour (the refusal names
`tests/acceptance/<T>/` and the tool's exclusion; row 44 a refusal), each change commented `DEC-1093 (2)`. Keep what
each row protects; never weaken an expectation that is not about this refusal. Change no product code unless a row
shows a real defect in round 1's code; if so, say so and fix it within your paths.

## Where you work
- `/home/usain/gov-os-worktrees/W2-141`, branch `w2/W2-141` (integrate merged in).
- **Your paths:** the ticket's `allowed_paths` (you need only `tests/unit/guard/test_reads.py`). Never `.claude/`.
- **You never read `tests/acceptance/W2-141/`** (DEC-820 (c)): only `gov accept W2-141`'s results. Every Grep or Glob
  call that could reach it carries `!tests/acceptance/W2-141/**`; recursive grep `--exclude-dir=W2-141`.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-141/src` and your real `HOME`: `tests/unit/guard tests/unit/hooks
  tests/acceptance/W2-84`, both the standard run and with `GOV_TESTS_OPTIN=lifted,breadth`; every red named with its
  cause. Then `python3 -m gov.cli.main accept W2-141 --root /home/usain/gov-os-worktrees/W2-141`.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: Read and Grep tools; one simple command per Bash call.
- Search again once (DEC-1092 (1)) if a search does not answer.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-141` with
  `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1093, DEC-1102" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round. Before you end, every test run you started has finished.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), each row changed (old and new expectation), the regression
counts with every red named, `gov accept`'s counts.
