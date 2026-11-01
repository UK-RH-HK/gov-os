Your package P-W2-123-TD-1, option (a), is the lead's call (a P3 inside your own test paths, no expectation lowered):
apply it. In `tests/acceptance/W2-123/README.md`, in the S2 and S5 test cells only, write the two parametrized items as
their bare function names (`test_w2_123_determinism.py::test_equal_vectors_are_accepted_with_that_many_requests_in_flight`
and `test_w2_123_restart.py::test_a_server_that_answers_is_never_restarted`), so that `gov accept`'s matcher maps every
parameter. Change no test and nothing else. All the standing rules of your first brief still hold.

Check: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src python3 -m gov.cli.main accept DAEO-qzrq --json` in your
worktree: every line read, all red on the base, and no unmapped test; quote the per-line counts.

Commit only that file, with the trailers in the final block:

    git commit -m "W2-123 acceptance README: parametrized map items by their function names" --trailer "Task: DAEO-qzrq" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1014, DEC-1017" --trailer "Rewrite-Reason: parametrized items in a form gov accept's matcher (W2-96) reads" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then quote `git log --oneline -2` and `git status --short`.

Return as before: one message, your last, the twelve fields first, each as a labelled line (task, status,
work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
recommended_next_action), any payload after them. Refused twice for the same call: stop and say so.
