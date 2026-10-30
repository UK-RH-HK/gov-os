---
type: probe
task: DAEO-g0ip
reviewer_session: 69f2282b-1f75-4cd1-a40a-81c507d2ed9a
implementer_session: b6ab76f6-6bbc-4ee8-b651-1e0ae60b1c85
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 4437d61778e752e27b248ff49e1b4ac5b7076057
---

# Probe record: W2-01, round 3, the last review (DEC-739)

- **What was probed.** Head `4437d61778e752e27b248ff49e1b4ac5b7076057` of `w2/W2-01` (DAEO-g0ip), after the
  DEC-739 round (tests `92f04d64`, implementation `a814cd3b`, engineer session
  `b6ab76f6-6bbc-4ee8-b651-1e0ae60b1c85`), running this worktree's `src/` (`gov.__file__` in the worktree). A
  fresh read-only reviewer (role `independent-auditor`, session `69f2282b-1f75-4cd1-a40a-81c507d2ed9a`,
  2026-10-17), commissioned and judged by the orchestrator (DEC-137), wrote nothing in the repository
  (`git status --short` empty before and after). 458 tests passed (the W2-01 acceptance suite and the close
  unit tests). Then 26 temporary projects built from scratch with the suite's support module, with `gov close`
  run in them. They focused on which merge the close takes as the merge-back and what it exempts:
  - other tickets' merges on the integration branch before the merge-back, trailered and plain, alone and in
    KPI 4's layout;
  - repeated merge-backs, including a reopened ticket and a partial merge-back before the probe;
  - later merge-backs naming no task or another ticket's task that drop the probed code;
  - inward merges naming another ticket's task;
  - merge-backs that keep the code but change the acceptance test, the ticket file or an allowed path;
  - merge-backs through a staging branch, octopus merges and fast-forwards;
  - a STANDARD ticket after a plain merge-back;
  - task-less commits the new exemption could hide.
- **What it found.**
  - A second merge-back that names another ticket's task and removes a probed file passes `gov close`. The
    ticket is closed with its code missing at the closed head. Seen with a merge-back only and in KPI 4's
    layout. Only the first merge-back, whose first parent lacks the probed commit, is measured by the probed
    code; a later one falls back to "another ticket's commit is that ticket's". The same merge as a plain
    merge, or with the ticket's task, refuses.
  - A merge on the integration branch that does not hold the probed commit is taken as the merge-back and
    refused ("brings the probed commit but not the probed code"). This happens when another ticket arrives on
    the integration branch by a merge, trailered or plain, alone or in KPI 4's layout. It also happens to an
    earlier merge-back of the same ticket before the final probe (a reopened ticket, a partial merge-back).
    KPI 4's success line therefore fails in the most common layout. By reading this is new in this round; it
    was not run on the earlier code.
  - Lesser:
    - An inward merge naming another ticket's task that resolves the probed file to the integration side
      closes on the ticket branch. This is consistent with the README's restated form, not with KPI 9's
      wording.
    - A task-less merge, not holding the probed commit, whose own resolution writes byte-identical probed
      content escapes the work-without-task rule.
    - A STANDARD ticket closed after a plain merge-back refuses with work without a task.
  - Sound:
    - merge-backs that keep the code but change the acceptance test, the ticket file or an allowed path
      refuse, naming the merge;
    - task-less changes on either side still refuse;
    - staging-branch, octopus and fast-forward merge-backs close, or refuse when the code was replaced;
    - a merge-form merge-back with its own change refuses.
- **Judgement.** fail. A merge-back that drops probed code still closes the ticket, which is the shape DEC-739
  orders refused. Here it is a later merge-back naming another ticket's task, in the repeated merge-back layout
  this round was asked to probe. It fails open and loses the ticket's work at close. Separately, the repair
  refuses KPI 4's success case whenever the integration branch received any other merge after the branch
  point. DEC-739 allows no fourth round, so whether to fix, defer or re-baseline goes to the owner.
