
## W1-30: `gov close` (DEC-453, DEC-454, DEC-470, DEC-476, DEC-480, DEC-482, DEC-483, DEC-484; 2026-10-07)

Merged at `2c71bc64`. Cases by the test designer in seven rounds (last `be2e8c14`, 204 cases); code by the
engineer (last `a1c03c5b`; `src/gov/close/command.py` 833 lines against an estimate of 200). `gov close`
measures or refuses: containment as W1-50 judges it, one context, the ticket's and every earlier suite, the
reviewer's writes, the governance checks as W1-26's runner reports them, the owner's decision on escalation;
every finding goes through one failure path (counted, a repair ticket, escalation at the third, exit code 3).

- `gov check` on the branch before the merge (`log/check-at-W1-30-premerge.json`): the ticket's own check
  `product-traceability-trailers` is red with 735 findings and joins the baseline with that state (DEC-482);
  the twelve earlier baseline reds; `secrets-indexing` green in the worktree run.
- Full regression at `2c71bc64` (`log/reg/at-W1-30-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- Own runs at the branch head (`log/W1-30-r7-own.txt`): W1-30 204, W1-07 218, W1-11 142, W1-24 54, W1-25 52,
  W1-26 294 and 1 skipped (the full project does not pass `gov check` yet), W1-50 666, W1-28 149, unit 1171.
- **`product-traceability-trailers` here:** 408 findings are commits of closed tickets without `Implements:`,
  made before DEC-476; a trailers base commit (here `429815b5`) takes them out of judgement once the setting
  is built (DEC-482; W1-41 or a follow-up). 327 are ids that resolve to no record: the check knows the record
  store, ticket ids and `docs/**` Markdown frontmatter ids, and this repository's capability ids live in
  `docs/contract/contract.yaml` until W1-41's adoption. The check's module keeps one `except Exception` around
  the store read (it reports an error, not a pass) and was not read again after round 4.
- **`core-decision-citations` is yellow from this merge on (10 findings, a warning):** branch commits cite
  DEC-453, DEC-454, DEC-470, DEC-476 and DEC-480, recorded on `w1/integrate` before the changes but not yet
  merged into the branch when the commits were made. History is not rewritten. From now the orchestrator
  merges `w1/integrate` into a ticket branch before a worker turn that will cite a newly recorded decision.
- **The owner's decision on an escalation is read from decision files only**, not from a register file such
  as this repository's: for W1-41's adoption (DEC-483).
- Where `gov close` can still close or refuse on something it did not measure, or says less than it could
  (for the Wave 2 list, DEC-466):
  - a tree with uncommitted changes is measured as its HEAD;
  - an error of the check runner ends the close uncounted (exit code 1), without a repair ticket;
  - "governance-changing" is seven fixed path prefixes;
  - no acceptance case holds a check that runs over the runner's fixed 60-second limit (a case would wait a
    minute); the limit is not configurable;
  - `openspec-validate` is yellow where the tool is absent, and yellow refuses nothing (W1-26's question);
  - a finding raised with `--disposition` records no class and no context on its repair ticket;
  - the repair ticket's `state_class`, `disposition` and `context_hash` are inserted into the ticket tool's
    frontmatter by the close command itself;
  - the model of a session is read from the commits' co-author lines (DEC-470); a launch record per session
    is a Wave 2 item.
- **Run time here:** `gov close` runs the project's tests, about an hour per ticket on this repository
  (accepted, DEC-484).
- History of the branch, for the exit auditor: commit `7674efde` carries no `Role:` trailer (S0a-G-12);
  the lead's rounds 1 to 3 and engineer round 4 (`01c19515`, a session that ran unpinned on Claude Opus 4.6
  before DEC-460 was applied to it) were read and not accepted; the engineer's round-5 session ended without
  a report (its runs were in the background) and its commits were read from the tree; merge commits
  `148f7584` and `29af0646` are flagged by containment for their own change to
  `tests/acceptance/W1-07/w1_07_support.py` (the shared list, DEC-412), left in place.
- Learning metrics: KPI disputes raised by the designer: three (round 6, settled by DEC-480) and the
  baseline question (DEC-476); acceptance cases rewritten after implementation began: the round-4 to round-7
  batches, each for a behaviour the earlier code claimed without measuring, plus one reversed case (a
  warning check whose command is absent, DEC-480) and one W1-07 case that used `gov close` as its
  not-built example.
