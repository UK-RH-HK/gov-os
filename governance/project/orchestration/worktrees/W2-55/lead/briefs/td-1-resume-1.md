A test-design batch for DAEO-arrl (W2-55), in the same tests worktree, `/home/usain/gov-os-worktrees/W2-55-tests` (branch `w2/W2-55-tests`). All the rules of your first brief still hold (DEC-732's `PYTHONPATH` per command; reads and writes; command forms; refused twice: stop). Keep the sandbox's own `TMPDIR` this time: do not set `TMPDIR` (it made pytest write `pytest-of-usain/` into the worktree last time).

A behaviour of one of your cases, found when the tests ran against an implementation (DEC-136):

- `test_w2_55_propagation.py::test_a_changed_entrys_id_alone_in_the_sweep_is_no_finding` fails on a finding that S3 requires: the W1-49 live-session fixture holds the recorded value `300000` on its fifth line, so a value finding `[DEC-665, DEC-838]` at line 5 is correct. The case takes that line-5 finding for one at line 1, because its line match accepts the number 1 wherever a lone digit 1 stands in the message, and the message's path (`…/W1-49/test_w1_49_live_session.py:5 …`) holds one in `w1_49`. A finding at another line of the same file is not a finding at line 1.
- The same loose line match is used by your cases that expect a finding at a given line: they could pass on a finding at another line whose path or ids happen to hold that digit.

Make the line match pick out only the line the case means (for example, the place written as `<path>:<line>`, the number not followed by another digit), in every case that uses it. Lower no other expectation, and change nothing else. Then run the whole suite in your worktree to its end (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-tests/src python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, never `-x`): on the base, every case that was red must still be red for its README reason, and the 7 that passed must still pass. Update the README if it describes the line match.

Commit only `tests/acceptance/W2-55/`:

    git commit -m "W2-55: acceptance tests: the line match names only the line meant" --trailer "Task: DAEO-arrl" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-791, DEC-866" --trailer "Rewrite-Reason: DEC-866 (a test defect: the line match took a finding at another line; no expectation lowered)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

Report first, in your return: step 0's sandbox check, as your first brief asked (it was missing from your last return): (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-arrl','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Right after the twelve fields: `guard_refusals:` (one line each, or `guard_refusals: none`) and `brief_gaps:` (one line each, or `brief_gaps: none`). Refused twice for the same call: stop and say so.
