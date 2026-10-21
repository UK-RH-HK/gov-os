
## W1-26 follow-up: the decision-citations check (DEC-463, DEC-473, DEC-474, DEC-475, DEC-479; 2026-10-07)

Merged at `8f0dcc8d` (cases `e3d2cc1b`, `ac952490`; code `c2058c80`, `f2361f1d`; all sessions pinned to
Claude Opus 5.5). `core-decision-citations` (family authority/role limits, tier G1, severity warning) flags a
commit whose message cites a decision id that its own tree does not record, as a decision file or as an
entry of the register file the project names. This repository names `docs/DECISION_REGISTER.md` and the base
commit `46ec8da3` in `governance/project/path-map.yaml`; the check is green here.

- `gov check` on the branch before the merge (`log/check-at-W1-26e-premerge.json`): no red outside the
  baseline; twelve baseline reds; `secrets-indexing` green in the worktree run (third time; it stays in the
  baseline until seen green in the main tree).
- Full regression at `8f0dcc8d` (`log/reg/at-W1-26e-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- Closed with `tk close` (W1-30 is not merged yet, DEC-476).
- The first engineer session of the second part ended before committing (it started its runs in the
  background); a second session ran them in the foreground and committed. No acceptance case was changed
  after implementation began.
- Where the check can still say clean without having measured (for the Wave 2 list, DEC-466): commits after
  the base that cite nothing give the same answer as none compared; whoever moves the base forward takes
  earlier commits out of judgement, unreported; any Markdown file in the tree whose frontmatter carries a
  decision id counts as its record, wherever it lies; a register heading counts whatever the entry's status
  or body says (a heading inside an HTML comment too); only HEAD's history is judged.
- The check imports private helpers of W1-11's decision checker (`_front`, `_git`, `_Objects`, `_once`):
  a change there can break it; the unit tests cover the join.
