---
type: probe
task: DAEO-g0ip
reviewer_session: 41e2621e-c198-4333-bacb-ead7cc690556
implementer_session: 1a44fff2-732d-4651-86c1-bd447aafeab5
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: f74b361bb8cf9eb525491d076383bcb4930d40f8
---

# Probe record: W2-01, round 2, the last review (DEC-413)

- **What was probed.** Head `f74b361bb8cf9eb525491d076383bcb4930d40f8` of `w2/W2-01` (DAEO-g0ip), after fix
  round 1 (tests `5e28cd05`, implementation `1352c2e7`, engineer session
  `1a44fff2-732d-4651-86c1-bd447aafeab5`), running this worktree's `src/` (`gov.__file__` in the worktree). A
  fresh read-only reviewer (role `independent-auditor`, session `41e2621e-c198-4333-bacb-ead7cc690556`,
  2026-10-16), commissioned and judged by the orchestrator (DEC-137), wrote nothing in the repository
  (`git status --short` empty before and after). 444 tests passed (the W2-01 acceptance suite and the close
  unit tests). Then 22 temporary projects built from scratch with the suite's support module, with `gov close`
  and the trailers check's command run in them, covering:
  - merge-backs that drop the probed code, carrying the ticket's `Task:`, another ticket's, or none (a plain
    `git merge`), alone and in KPI 4's merge-in-then-back layout;
  - accepted history from an uncommitted path map or register, and from a register entry committed by a
    non-owner;
  - the merge form with a real octopus, a rename against a change, `-X theirs`, and side branches with
    untrailered commits;
  - probe rounds with a later record outside the history, and with equal probed commits;
  - a trailers base at the ticket's own head and off the history.
- **What it found.**
  - A merge-back onto the integration branch that names no task (`Role:` only, or a plain `git merge` with no
    trailer) and drops the ticket's probed code passes `gov close`; the ticket is closed with its code missing
    at the closed head. Seen with `-s ours`, a removed probed file, and a conflict resolved to the integration
    side, including in KPI 4's layout. Such a merge is judged only against its first parent, so code that came
    only from the ticket's branch is never compared with the probed commit. The same merge carrying the
    ticket's `Task:` refuses, as do the inward plain merge and the removal of an acceptance test already on
    the integration branch. The no-task handling appears to predate this ticket (not reproduced on the old
    code). 131 of the last 300 merges on this repository's `main` carry no `Task:` trailer.
  - Lesser: accepted history trusts the register's text whoever committed it (an entry worded as the
    owner's, committed by an engineer-role commit, was accepted when the owner's path map listed it); the
    close's register reader takes any id heading at levels 2 to 6, also inside fenced code, where the record
    store takes only `### DEC-n` headings outside fences (both find the same 725 headings in this repository's
    register).
  - Sound: an uncommitted path map or register is refused; the real register's owner and delegated wordings
    are read correctly; octopus and `-X theirs` merges in the merge form refuse; clean rename merges pass;
    probe rounds and the trailers base fail closed.
- **Judgement.** fail. In a merge layout this repository's history shows is common (a merge-back without a
  `Task:` trailer), the probe gate and the close fail open on dropped probed code and lose the ticket's work at
  close. This was the last review round (DEC-413): whether to fix, defer or re-baseline goes to the owner.
