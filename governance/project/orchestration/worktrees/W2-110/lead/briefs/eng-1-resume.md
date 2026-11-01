The acceptance tests are merged: `/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/TESTS-READY` exists.
Run them once, reading results only (never their source, DEC-820 (c)), in the foreground, to the end:

`cd /home/usain/gov-os-worktrees/W2-110 && TMPDIR=/tmp/gov-os-lead-W2-110 PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -m pytest tests/acceptance/W2-110 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`

Change no file and commit nothing in this step. Report the counts, and for any failure its test name and failure
message. Give your full return again, with all twelve fields as labelled lines first (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
nothing before them. Refused twice for the same call: stop and say so.
