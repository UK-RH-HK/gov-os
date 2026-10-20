# W2-59 (DAEO-kh9l) packages, run 2 (2026-10-20)

## P-W2-59-5 — the merge-back 3eadca4c names no task; once W2-59 lands, other tickets' closes refuse (P1 for the wave's closes; blocks W2-59's second, last review and its merge; not the rest)

1. **Context.** DEC-750 asks every merge, into `w2/integrate` or of `w2/integrate` into a ticket branch, to carry `Task:` and `Role:`. `gov close`'s gate "work without a task" (`src/gov/close/command.py` `_check_unmeasured`, DEC-490, DEC-500) refuses a ticket's close when a commit in its range names no task and changes the ticket's paths. It reads a merge by its first-parent diff. That gate has no exemption for a merge that is git's own merge of its parents: only the trailer gate has one (DEC-436's merge form, `adds_nothing`), and a FULL ticket's probe gate measures such merges (DEC-754). The accepted history (DEC-734) feeds only the trailer gate.
2. **What happened.** The lead of W2-59 made run 2's merge of `w2/integrate` (74d22909) into `w2/W2-59` as `3eadca4c` with `-m` and no trailers. Its subject also says `DAEO-kl9l` by a typing error. It is git's own merge: tree 6b2943c8 equals `git merge-tree --write-tree`, there was no conflict, and it touches none of W2-59's paths. The lead did not amend (no amend, rebase or reset) and recorded the correction in the body of `6d4925ab`, which no gate reads. The CIT-P review (rev-1, probe at `9b9faac3`) ran the close's own functions on this history: against its first parent the merge brings 543 paths, among them other tickets' ticket files, checkpoints and probe records. Once `w2/integrate` holds it, the gate refuses the closes of W2-63, W2-58, W2-62, W2-05 and W2-12, each naming only `3eadca4c`. W2-50's FULL probe gate exempts it, and W2-59's own close has no finding. A history built from scratch gives WORK_WITHOUT_TASK without the trailer and no finding with it.
3. **Why it matters.** Every such refusal is a false one and counts toward that ticket's escalation. Nothing but a history rewrite or a close change ends it, and exit criterion 1 needs clean closes. Nothing fails open and no work is lost.
4. **Options.**
   (a) **Remake the ticket branch before its merge.** The orchestrator, or W2-59's next lead under a decision that lifts the no-rewrite rule for this one unmerged and unpushed branch, recreates `w2/W2-59` from `c76cddf5`. First the merge of `74d22909` again, with `Task: DAEO-kh9l` and `Role: orchestrator` (git's own merge, the same tree 6b2943c8). Then each later commit (`6d4925ab` … the head) re-applied unchanged with its trailers. Cost: about 20 minutes, plus W2-59's suite and the second (last) review on the new head. The CIT-P names `3eadca4c` and `6d4925ab` by id, so a product-spec or engineer edit of §1 rides along. Risk: low; the scratch records keep naming the old ids as history. It changes DEC-412's scope once, for an unmerged ticket branch.
   (b) **Merge as is, and give the gate DEC-436's exemption** (a merge whose tree is git's own merge of its parents changes no path of its own, as the trailer gate already reads it). Cost: a judge change in another ticket, with a CIT-P (CAP-33) and a re-pin before it judges; until then the five closes refuse. Risk: medium. It also covers any later slip of the same kind.
   (c) **Merge as is, with an owner-accepted history entry for this gate** (DEC-734 widened to WORK_WITHOUT_TASK for `3eadca4c`). Cost: a judge change too. Risk: medium.
   (d) **Merge as is and leave the closes refused.** It breaks exit criterion 1.
5. **Recommendation:** (a) now, confidence medium-high: cheapest, no judge change, and the branch is unmerged. (b) as a Wave 3 row, so the two gates read merges alike. Classification (DEC-809): F2, ordinary work: yes (a forgotten trailer on a routine merge-back); consequence: other (fails closed).
6. **Blocks:** W2-59's second (last) review and its merge, because (a) moves the head the review must probe. It blocks nothing else: F1's fix is made and verified in this run. Waiting costs W2-59's merge and keystone 1's re-pin.

## P-W2-59-6 — does a bare `gov` whose command sets `PYTHONPATH` run the pin or the tree? (P2; blocks nothing)

1. **Context.** DEC-732: the code under test is chosen by a per-command `PYTHONPATH`. DEC-822 item 3: that variable chooses only the code under test, never the judge, and a bare `gov` is the pinned judge.
2. **What happened.** The pin's pip-written `gov` script follows `PYTHONPATH`. A bare `gov …` with the variable set (per command, or inherited, P-W2-59-7) runs the tree's code. The hook lines no longer do (`e791465b`: `-E`).
3. **Why it matters.** A session that types a bare `gov check` in a worker's environment is judged by its own tree. Today's briefs always use `python3 -m gov.cli.main` with the variable, which is the code under test by intent. The close runs in the main tree without it.
4. **Options.** (a) A command that sets the variable itself is a run of the code under test; only the judge's own entry points (the hook lines, the runner's checks) ignore it. This is as built, with the CIT-P §4 stating it. (b) The pin's `gov` script ignores the variable too (a packaging change to the console script). (c) Leave it to W2-16 and W2-18 (the release).
5. **Recommendation:** (a), confidence medium (the test designer's and the engineer's readings agree). Classification: ordinary work: yes; consequence: other (the judge in the main tree is unaffected).
6. **Blocks:** nothing. Waiting costs nothing.

## P-W2-59-7 — the launch form and the launcher carry `PYTHONPATH` into every worker session (P2; blocks nothing)

1. **Context.** The committed launch form (`governance/project/briefs/LEAD-w2-common.md`) runs `PYTHONPATH=<worktree>/src python3 -m gov.cli.main launch …`, and `src/gov/launch/launcher.py:319` gives the session `{**os.environ, **settings["env"]}`. DEC-732 says the variable is set per command, "never in a session's env".
2. **What happened.** Every launched worker's environment carries the variable. The review found that the new hook lines then ran the tree's guard (F1). That is fixed in the lines (`e791465b`); a bare `gov` in such a session still runs the tree (P-W2-59-6).
3. **Why it matters.** It contradicts DEC-732's wording and leaves every other inheritor of the variable on the tree's code.
4. **Options.** (a) A row for the launcher's ticket (W2-56): the launcher drops `PYTHONPATH` from the session's environment, or states that it passes it on. (b) Change the launch form instead: the launcher is found by an absolute path, without the variable. (c) Accept, as the lines now ignore it.
5. **Recommendation:** (a), confidence medium. Classification: ordinary work: yes; consequence: other (the guard path is closed by the lines).
6. **Blocks:** nothing.

## Rows proposed (Wave 3 hardening pass; the review's F3, F4, F5, F7; ordinary work: no)
- F3: the preToolUse line checks only that the named interpreter is an executable file (a hand-made `gov` naming `/bin/true` ends with exit 0). Consequence: fails open, with a deliberate construction.
- F4: `gov --version` from a source tree follows a `GIT_DIR` set by hand. Consequence: other.
- F5: only a declared command whose first word is exactly `python3` or `gov` is rewritten (no declaration uses another form). Consequence: other.
- F7: a project holding both kernel layouts with different canary declarations uses the template's silently. Consequence: other.

## Rows proposed from the test designer of the three revised cases (td-2; ordinary work: no new behaviour)
- W1-26 `test_w1_26_dec436.py::test_readiness_check_all_return_value_not_ignored` and `::test_readiness_check_all_exception_caught` plant `src/gov/readiness/checker.py` in the judged project, which the judge no longer imports, and assert on a family name that no family has. They pass whether or not the plant runs. `::test_new_command_module_discovered_by_commands_check`'s condition is always true.
- W1-22 README line 103 and `tests/unit/validate/test_canary.py` still describe a module-level `_TEMPLATE` install path.
- W1-22's lexical canary hits its own declaration files in the adopted layout, so it proves only that the index is searchable.
