# Lead brief: W2-81 judges memory end to end, on Sonnet, on the release candidate (W2-81, `DAEO-l78m`, in progress; the owner, DEC-1221 (1))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `w2-81-e2e`; worktree
`/home/usain/gov-os-worktrees/E2-w2-81-e2e`, branch `e2/w2-81-e2e` from `w2/integrate`. W2-81 is a feature ticket in
progress (the proving run on synthetic repositories, release acceptance item 2, EMERGENCY-2 8.2); every commit
`Task: DAEO-l78m`.

**The owner's words (DEC-1221 (1)):** "W2-81 stays: adopting Gov OS across different kinds of repository matters. It
judges memory end to end, not by hit@5, and runs on Sonnet."

**What is wrong today** (`.tickets/DAEO-l78m.md`, `tests/acceptance/W2-81/README.md`):
- The question-set line's scorer "reports both figures per repository, hit@5 against CAP-10's floor of 85 and the share of
  questions whose stacked context holds all their evidence against the 99 % target". EMERGENCY-2 5.2: hit@k is no target
  or floor anywhere; Contract v5's CAP-10 is a fresh measure judged end to end at 95 %.
- S-RERUN names release 0.1.1 and `gov close` (the strict close retires into `gov queue`, L2-1).
- Its failure line "a figure below its floor or reported alone" refers to the two old figures.

## The change
1. **KPI lines (yours, `Role: orchestrator`):** rewrite the scorer line: per repository, memory is judged **end to end**
   as EMERGENCY-2 5.3 and DEC-1210 (1) define, applied to the repository's question set: a reader reads the whole ranked
   `gov retrieve` bundle and searches once more in its own words, then answers with a citation; a grader judges the answer
   and the citation (both must be right; a forbidden citation, such as the stale spec, is wrong); the figure is the share
   of questions judged right, **95 % or more** per repository; hit@k may be printed as a diagnostic, never a pass line.
   **Every session of the run (adopter, reader, grader) runs Sonnet** (`claude-sonnet-5-5`), stated in the run record.
   Rewrite S-RERUN for the release candidate (the release that will be 0.1.4 or its successor: read the version from
   the pinned install, never a fixed number), with the landing (`gov queue`) in place of `gov close`. Revise the failure
   line to "a READY verdict with a control flagged, a stage unmeasured, or a repository's end-to-end figure under 95 %".
   Append a dated amendment note naming DEC-1221 (1) under the ticket's record. Leave every other line as it is.
2. **Independent test designer (Sonnet; `Task: DAEO-l78m`):** revise the scorer, the judge's figure handling and their
   self-tests in `tests/acceptance/W2-81/` to the new lines: the end-to-end judge is a function taking the reader's and
   grader's verdicts per question (stand-ins in the suite: no model, hermetic, as the folder's other cases), the 95 % bar
   per repository, hit@k only as a printed diagnostic; mutation self-tests: a stand-in where one answer is right but its
   citation is the forbidden stale spec is judged wrong; a repository at 94 % gives NOT_READY; a run record without
   the Sonnet model line is refused. Reuse the product's end-to-end measure where it fits (W2-204: `gov memaudit`'s
   reader/grader steps, `docs/changes/W2-204-evidence.md`) rather than a second judge; say which. The real-run command
   (not collected as a test) starts its reader and grader sessions on Sonnet. `Rewrite-Reason` naming DEC-1221 (1).
3. **Green:** `gov accept W2-81 --root <worktree>` green; `tests/acceptance/W2-88` (it imports W2-81's builders) green;
   `tests/unit/optin`.
4. **Do not run the real proving run** (it needs the release candidate; the CTO starts it). **Do not merge.** Return:
   branch and head; the new lines; the tests changed; the summary lines; reds not yours; the exact real-run command for
   the CTO, with its expected time and model use.

Not here: the new imports feature (a proposal for the owner); `tests/optin-weekly.txt` beyond W2-81's own lines (the
ti-cuts lead edits it).
