task: DAEO-wahn (W2-175), independent review, round 1 of at most 2, of head `44d83e22d7e7` on `w2/W2-175`
status: DONE. Verdict PASS on all nine KPI lines (S1–S7, F1, F2). No finding is in scope, reachable in ordinary work and failing open or losing work, so none blocks.
work_completed: I read the ticket in full; the template diff `7709021ad6cc..HEAD` (seven role templates, 1.0.0 → 1.0.1); the `.rulesync` diff (six files); the CIT-P record; the W2-175 tests (`test_w2_175_templates.py`, `test_w2_175_record.py`, `w2_175_support.py`); the register entries DEC-820, DEC-861, DEC-957, DEC-963, DEC-1137, DEC-953, DEC-1057, DEC-315, DEC-1116 and DEC-1121; the W2-153 `test_s3_*` cases; and `gov/brief/build.py` `run_section`. Read-only probes: compose() byte equality, 26 sha256 values, the tests' base commits against the ticket base, and the root copies against the template copies. I re-ran no suite.
files_changed: none
evidence: Step 0: (a) `open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wahn','w')` was refused with `OSError: [Errno 30] Read-only file system`, so no file was written; (b) `git update-index --refresh` exit 0, no output. Identity: `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-wahn`, toplevel `/home/usain/gov-os-worktrees/W2-175`, branch `w2/W2-175`. Head at start `44d83e22d7e7`, at end `44d83e22d7e7`. `git status --porcelain` at end: empty. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-175/src/gov/__init__.py`. compose(Path("template"), role) == bytes of `template/.rulesync/subagents/<role>.md`: True for all six roles. sha256: all 13 "New" values in the CIT-P record equal `sha256sum` at head (e.g. role-cto `013d4d85bc5d`, role-reviewer `eff256eb0277`, rulesync engineer `33155d8015ac`), and all 13 "Base" values equal `git show 7709021ad6cc:<path> | sha256` (e.g. role-cto `1b1745571c51`, rulesync research `2b8e2b217397`). The tests' pinned bases (`a6c83d497035`, `baa2696f713f`) hold the same blobs as `7709021ad6cc` for all seven templates. `git diff --no-index --stat .rulesync/subagents template/.rulesync/subagents`: 42 insertions, exactly the ticket's lines. The `.claude/templates/role-*.md` copies differ from the kernel templates only by this delta. Read refusals met: none.
tests: none run (the brief says not to re-run the suites). I take the lead's results as given: `gov accept` 51/0; S6 247 passed and 7 red, all on the root copies.
discoveries: (1) DEC-953 item 2 cut the guard to four rules, and the counterpart rule (c) is not among them, so the templates are now the only place (c) is enforced. That makes the S2 lines carry real weight. (2) The lead brief takes only role-lead's run section (`build.py:245-264`). The new role-lead lines sit in "Every run" and reach the lead through the appended template, as the other "Every run" lines do, so nothing is lost.
risks: Until the copies ACT runs, the root `.rulesync/` and `.claude/templates/` copies still give launched sessions the 1.0.0 text. That is the ticket's stated plan, not a defect.
lessons: none
proposed_decisions: none
unresolved: none
recommended_next_action: The lead fills CIT-P section 3 with this READY and sends the 13 sha256 values to the owner for approval (DEC-1116 route). After approval, the copies ACT writes the root `.rulesync/subagents/*.md` and `.claude/templates/role-*.md`, then S6 is re-run. The rows below can ride along or wait for Wave 3; none needs a round.

Classification: 6 findings, all rows (ordinary work yes/no with consequence `other`); none in scope with fails open or loses work. Recommendation: READY, no second round.

What I probed and found sound:
- **S1–S4:**
  - Each line is one paragraph in the Interface section's exact words.
  - Each ends with the right id: `[DEC-820]`, `[DEC-820, DEC-957]`, `[DEC-820, DEC-963]`, `[DEC-861]`, `[DEC-1137]`.
  - The stop sentence is byte-equal to `brief.md:62`.
  - role-cto's decision-record line (now `role-cto.md:33`) is unchanged byte for byte, and role-cto has no REC line.
- **Non-goals:** the diff is additions plus the version line only. No rule is reworded or dropped, and nothing beyond the three rules is added.
- **S5:** only `version` changed in each front matter. The new lines add no placeholders. The record's prose sizes are within budget (role-reviewer is the tightest at 3188 of 3500).
- **F1:** DEC-820, DEC-861, DEC-957, DEC-963 and DEC-1137 are all ACCEPTED. Their later changes (DEC-953 item 2, DEC-1057 R-8, DEC-959, DEC-966) leave the cited rules standing. Neither DEC-508 nor DEC-849 is cited.
- **F1 test:** `test_f1_a_stop_sentence_changed_by_one_letter_fails_the_s4_check` shows the one-letter case ("twice" → "tvice").
- **S7:** one section per CAP-33 step; status PROPOSED; DEC-1137, DEC-820 and DEC-861 appear in both `decisions_read` and `decisions_carried`.
- **F2:** the ticket's paths in `w2/integrate...HEAD` are the seven templates, the six `template/.rulesync` files and the CIT-P record. The rest is the designer's tests, which are allowed.

RV1: `template/governance/kernel/templates/role-engineer.md:22` vs `:15`
What happens: the new line lets the engineer "run its cases and read their names, pass or fail and failure messages". Item 6 still says to run the cases once through accept, "pass or fail per KPI line, never their text". Pytest's failure output usually prints the failing assert line of the test source. So an engineer told to read failure messages will see fragments of acceptance-test code, which the same line forbids. The wording is DEC-820 item 2 (c)'s own, so the tension is in the decision, not in this delta. What should happen: one wording that says whether the assert lines shown in a failure count as "text".
Reversed by: a reading of DEC-820 (c) that counts pytest failure output as allowed "failure messages", or accept output that hides source lines.
Ordinary work: yes, because every red accept run prints the failing assert lines.
Consequence: other (it only shows fragments DEC-820 itself allows; it neither grants a forbidden read nor stops a session)
Scope: out

RV2: `template/governance/kernel/templates/role-test-designer.md:25` vs `:13`
What happens: the new designer line repeats item 4's first half ("never read what this ticket's branch changes other than your own tests") and adds the missing half. The Interface asked for this: "keep it and add what is missing". Nothing contradicts; the template just says the rule twice, under two brackets (`[DEC-820]` and `[DEC-820, DEC-963]`).
Reversed by: an Interface reading that wanted item 4 itself extended, which the non-goal against rewording forbids.
Ordinary work: yes, because every designer launch reads both lines.
Consequence: other
Scope: out

RV3: `template/governance/kernel/templates/role-reviewer.md:18-20` (and `role-lead.md:31`, `role-cto.md:10`)
What happens: these roles have no counterpart, but they get the same Policy 2 line, which lists "the counterpart's work on the same ticket" as refused. In role-reviewer, the next line ("You read everything, tests and code alike") settles it, as DEC-820 item 3 does. role-lead and role-cto have no such line, so a lead could ask whether the tests or the code are the counterpart's work. Their existing lines (merge the tests, check red, verify) already settle it in practice.
Reversed by: a lead or CTO session that refuses to read a ticket's tests or code because of this line.
Ordinary work: no, because no step of the lead's or the CTO's run needs a read that line refuses; their existing steps name the reads they do.
Consequence: other
Scope: out

RV4: `tests/acceptance/W2-175/test_w2_175_templates.py:27-40` (S2), `:19-22` (S1)
What happens: the S2 cases need a negation somewhere in the statement, not on the reading verb. An engineer line such as "read the acceptance-test code, never skip running its cases and their names, pass, fail, messages" would pass. S1 checks `secret`, `held-out`, `counterpart` and `hidden half`, but not "never printed" or "file names may be seen". So a shortened line that drops one of those ideas would still pass, though the Interface forbids dropping an idea. The head text holds every idea, so the KPI lines are true now.
Reversed by: a mutated template that drops one of those ideas and still fails the cases.
Ordinary work: no, because only a later edit of these exact lines would hit it, and that edit goes through the review route again (DEC-1116).
Consequence: other
Scope: out

RV5: `tests/acceptance/W2-175/test_w2_175_record.py:47-65` and `docs/changes/W2-175-CIT-P.md:106`
What happens: the S7 sha256 cases cover only the seven templates. The six `template/.rulesync` rows added by the scope amendment have no case (I checked them by hand: all 12 values match). Also, section 3 describes the review as being of "the seven templates" only, though this review also covered the six composed files.
Reversed by: a case on the six rows, and a section 3 text that names them.
Ordinary work: yes, because a later re-composition that forgets to update the record would pass unnoticed.
Consequence: other (the files are byte-determined by compose(), which W2-153 S3 checks)
Scope: out

RV6: the brief, question 8 (the lead's reading of the S6 reds)
What happens: the reading itself is right. All 7 reds are the root `.rulesync/subagents/*.md`, which differ from the template copies by exactly the 42 lines of this ticket. But the root `.rulesync/` is out of the paths because of the ticket's allowed_paths and the CTO's "Scope amended" line, not because of DEC-315. DEC-315 covers `Edit` deny rules for `.claude` (and acceptance tests and tickets). The ticket's F2 line cites DEC-315 for `.rulesync/` paths too.
Reversed by: a register entry that extends DEC-315 to `.rulesync/`.
Ordinary work: no, because no session acts differently on which id is cited for an exclusion it already has.
Consequence: other
Scope: out

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "RV3", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "RV4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "RV1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": [{"id": "RV6", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S7", "verdict": "pass", "findings": [{"id": "RV5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": [{"id": "RV6", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}]}
```