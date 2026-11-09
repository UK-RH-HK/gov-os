# D-6 part 2 item F2 — round 2 review: W2-55 S9 together with W2-129 S18 (DAEO-arrl, DAEO-q7lk)

You are a fresh, read-only independent reviewer. **Round 2 of F2** (the last round, DEC-1010).
- **Round 1** reviewed W2-55 S9 (`tags.py`'s `STATUS_RELATION_UNMARKED` removed, so that `gov links` is the one
  relation check). It found **F1, blocking:** an unmarked `**Settles:**` (a change by DEC-866 (1)) was caught by the
  removed check and by nothing in `gov links`.
- **The fix is W2-129 S18:** UNMARKED_CHANGE counts a `**Settles:**` label as a change.

The two branches merge together. READY is computed by `verdict.py` from your block.

## What to review
- **W2-55 S9:** `w2/W2-55-f2`, head `2fe928a4c` (`/home/usain/gov-os-worktrees/W2-55-f2`; `git diff b2b59caff..2fe928a4c`),
  unchanged since round 1.
- **W2-129 S18:** `w2/W2-129-f2`, head `c031faba0` (`/home/usain/gov-os-worktrees/W2-129-f2`;
  `git diff 7aaece52e..c031faba0`).
  - The designer's cases (`d0d07135`).
  - The engineer's change `c031faba0`. It adds `settle` to `CHANGE_CLASSES`, limited to the `**Settles:**` label (a
    free-text "settled by" is left out; the engineer names DEC-763 ← DEC-762 as a package-item settlement, not an
    entry's).
  - The engineer's figures: `gov accept W2-129` 156/0; `--all` 1,404 → 1,405, with only DEC-026 ← DEC-086 added.

## Check
1. **F1 closed:** with both branches, is every relation the removed loop caught now reported by `gov links`?
   - Take the loop's inputs from `src/gov/util/register.py` (`supersedes`, and `changes` from `Supersedes`, `Changes`,
     `Settles`, `Corrects`, `Reverses`, `Withdraws`).
   - Take UNMARKED_CHANGE's from `register_statements` and `CHANGE_CLASSES`.
   - Check each label form. Ideally, plant a register with one entry per form in your TMPDIR and run both branches'
     code on it.
2. **The free-text exclusion:** leaving "settled by" prose out is no loss against the removed loop, which read labels
   only. Confirm this.
3. **Nothing else changes:** every other code and count; round 1's out-of-scope rows (F2 to F7) stand as rows.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns S9 or S18.

## Write and return
- **You write nothing** in the trees (your TMPDIR only). Single simple Bash commands (DEC-1080). No GPU.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- **Search again once.**
- **Your record is your session's final message.** It holds:
  - the twelve labelled fields of `EMG-common.md`;
  - your answers to checks 1-3, with the per-form table;
  - every finding, with its two lines;
  - the fenced `verdict` block:
    `{"kpis": [{"kpi": "S9", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S18", "verdict": "pass|fail", "findings": [...]}]}`.
