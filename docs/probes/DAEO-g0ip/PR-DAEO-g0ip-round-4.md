---
type: probe
task: DAEO-g0ip
reviewer_session: fdac0d7a-c2d1-4303-8d33-726ae0c132fa
implementer_session: 841dfb85-9565-40ba-b1d4-22aa2e876b42
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 09a01912f05f36a8e0a72442e0a96b2f0e073ec0
---

# Probe record: W2-01, round 4, the last review (DEC-750)

- **What was probed.** Head `09a01912f05f36a8e0a72442e0a96b2f0e073ec0` of `w2/W2-01` (DAEO-g0ip), after the
  DEC-750 round (tests `40dbe546`, implementation `b283af77`, engineer session
  `841dfb85-9565-40ba-b1d4-22aa2e876b42`), running this worktree's `src/` (`gov.__file__` in the worktree). A
  fresh read-only reviewer (role `independent-auditor`, session `fdac0d7a-c2d1-4303-8d33-726ae0c132fa`,
  2026-10-17), commissioned and judged by the orchestrator (DEC-137), wrote nothing in the repository
  (`git status --short` empty before and after). 468 tests passed (the W2-01 acceptance suite and the close
  unit tests). Then 31 temporary projects built from scratch with the suite's support module, with 35
  `gov close` runs. They covered which merge is taken as the merge-back, and what a later merge holding the
  probed commit is compared with:
  - round 3's two failing scenarios, re-run;
  - later merges of another ticket's branch onto `main` that remove or revert a probed file or an acceptance
    test, alone, in KPI 4's layout, as an octopus and inward;
  - P-5's case and its mirror image;
  - a reopened ticket whose round 1 was merged back;
  - staging-branch, fast-forward and `-s ours` second merge-backs;
  - a later FULL close of another ticket;
  - task-less commits behind a merge-back;
  - an object git cannot read.
- **What it found.**
  - A later merge holding the probed commit that brings another ticket's branch, made before the merge-back,
    and names that ticket's task can delete a probed file or set it back to its pre-ticket text, and the ticket
    closes. Seen on `main` alone and in KPI 4's layout, as an octopus merge-back, and inward on the branch. The
    same merge can delete an acceptance test the test designer added on the ticket's branch, and the close
    passes with the test gone. The repair counts a probed path as the merge's own change only when it matches
    neither parent. A parent made before the ticket still has the pre-ticket version, or no file, so going back
    to it passes. No ticket's commit changed those files, and git's merge of the parents would keep them, so
    this is outside package P-5. The same merges as a plain merge, or with the ticket's task, refuse.
  - Lesser: a reopened ticket whose first round was merged back before its final probe cannot close. That
    merge-back is judged against the final probed commit (fails closed, against KPI 5 in that layout).
  - P-5, for the owner: taking another ticket's whole version of a probed file in a later merge closes, from
    either side. The integration branch's version kept by a second merge-back with the ticket's task refuses.
  - Sound:
    - round 3's F1 now refuses and names the second merge-back;
    - round 3's F2 is no longer the merge-back, and the ticket closes, trailered or plain, in both layouts;
    - a merge with both parents holding the probed commit that replaces probed code refuses;
    - staging-branch, fast-forward and `-s ours` merge-backs behave as stated;
    - a later FULL close of another ticket closes both;
    - task-less work on the ticket's paths still refuses;
    - an object git cannot read gives `GIT_FAILURE`, not a pass.
- **Judgement.** fail. DEC-750's second point says every later merge that holds the probed commit and changes
  probed code refuses, whatever task it names. In the layout the suite itself uses for that point's boundary, a
  merge of another ticket's branch that removes or reverts the ticket's probed code, or one of its acceptance
  tests, closes the ticket. It fails open, loses the ticket's work and changes its acceptance tests at close. It
  needs a hand removal inside a merge naming another ticket, as round 3's first finding did. DEC-750 allows no
  fifth round: W2-01 is split (DEC-750 item 2).
