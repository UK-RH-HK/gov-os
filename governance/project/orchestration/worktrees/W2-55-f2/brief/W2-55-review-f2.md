Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-55-f2/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-55 — the narrow review of S9, one relation check (D-6 part 2 item F2) (DAEO-arrl)

You are a fresh, read-only independent reviewer. **Narrow scope: S9** in `.tickets/DAEO-arrl.md`. Read it and the note
"D-6 part 2 item F2 placed here". READY is computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-55-f2` in `/home/usain/gov-os-worktrees/W2-55-f2`, head `2fe928a4c`, made from
  `w2/integrate` at `b2b59caff`. Read `git diff b2b59caff..2fe928a4c`:
  - the designer's cases: `tests/acceptance/W2-55/` (`c5ed68d4`);
  - the engineer's change: `2fe928a4c`, which removes `STATUS_RELATION_UNMARKED` from `src/gov/decisions/tags.py`
    and updates the unit case.
- **The runs:**
  - `gov accept W2-55`: 55 passed, 3 failed. The 3 are `test_w2_55_backfill.py` cases, red on the base too (the
    CTO's run on the designer's tree, without the change, gave the same 3 plus the 2 S9 cases).
  - `tests/acceptance/W2-129`: 150/0.
  - `tests/unit/decisions`: 37/0.

## Check
1. **Nothing else changes in `check_tags`:** the other codes, their messages and their order.
2. **The relation is still reported by one tool:** for every form the removed loop caught (`**Supersedes:**` with ids
   alone, `**Changes:**`, `Settles`, `Corrects`, `Reverses`, `Withdraws`), does `gov links`' UNMARKED_CHANGE report
   it? Compare the removed loop's inputs (`register.py`'s `supersedes` and `changes`) with `register_statements`' forms.
   A form only the removed loop caught is a finding.
3. **Out-of-date text:** `STATUS_RELATION_UNMARKED` is still named in `.tickets/DAEO-q7lk.md:79`,
   `LINK-INTEGRITY.md` and `W2-129-gov-links.md`. Record these as rows only.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns S9.

## Write and return
- **You write nothing.** Single simple Bash commands (DEC-1080). No GPU.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message.** It holds:
  - the twelve labelled fields of `EMG-common.md`;
  - your answers to checks 1-3;
  - every finding, with its two lines and its scope;
  - the fenced `verdict` block: `{"kpis": [{"kpi": "S9", "verdict": "pass|fail", "findings": [...]}]}`.
