# D-6 part 2, item F — the review: the link findings left in the tests (DAEO-q7lk)

You are a fresh, read-only independent reviewer of D-6 part 2's item F. It is a test designer's comment, docstring and
README pass over `tests/acceptance/**`, to clear `gov links`' findings in the tests (LINK-INTEGRITY §7; DEC-1109 (2)).
READY is computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/D6-F-tests` in `/home/usain/gov-os-worktrees/D6-F-tests`, head `2761682a2`, made from
  `w2/integrate` at `260e70bd1`. Read `git diff 260e70bd1..2761682a2`: 53 files (43 `.py` with comments and
  docstrings only, 10 READMEs).
- **The designer's figures:** `gov links --all`, the test designer's findings: ENFORCES_SUPERSEDED 45 → 8, UNKNOWN_ID
  60 → 0, no new finding. An AST comparison shows no code change in the 43 `.py` files. The 25 touched folders give
  the same results as the unchanged tree (55 sandbox reds on both).
- **Its classification:**
  - DEC-798 → DEC-1033 citations of current behaviour are re-cited to DEC-1033;
  - the dated history lines are kept;
  - W2-07's DEC-876 lines go on a Kept list for the CTO;
  - one real finding is reported, in W2-54 `test_w2_54_shared_gpu.py:142`.

## Check
1. **No behaviour change:** every `.py` change is a comment or docstring only. Re-run the AST comparison yourself on
   each changed `.py`, ignoring docstrings.
2. **Honest re-citation:** for each (c) re-citation, read DEC-798 and DEC-1033 in `docs/DECISION_REGISTER.md`. Does
   the test's behaviour match DEC-1033? A re-citation that hides a test still enforcing DEC-798's superseded rule is a
   finding.
3. **The README notes:** a note citing DEC-1033 in a README clears every old citation in that file (the check judges
   the whole file). Is each note true, or was it added only to silence the check?
4. **The planted ids:** do the reworded comments keep their meaning?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns this pass.

## Write and return
- **You write nothing.** Single simple Bash commands (DEC-1080). No GPU.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message.** It holds:
  - the twelve labelled fields of `EMG-common.md`;
  - your answers to checks 1-4;
  - every finding, with its two lines and its scope;
  - the fenced `verdict` block:
    `{"kpis": [{"kpi": "F-tests", "verdict": "pass|fail", "findings": [...]}]}`.
