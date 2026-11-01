Your lead has merged the acceptance tests into this worktree (`/home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/TESTS-READY` now exists; the merge is `0a11d525b715`). This is your next batch, under the same brief and rules as before.

1. Repeat step 0 (the sandbox check) and the identity check, and report them first.
2. Run the acceptance tests once, reading results only, with your session's own writable temp folder (not `/tmp/gov-os-lead-W2-97`, which your sandbox cannot write): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 -m pytest tests/acceptance/W2-97 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rA`, to the end. Never read the tests' source (DEC-820 (c)); names, results and failure messages only.
3. If every case passes: report each case's name and result, and stop; commit nothing.
4. If a case fails: decide from its name and failure message whether the tool departs from the specification or the KPIs. If it does, fix the tool (only inside the ticket's `allowed_paths`; keep your unit tests passing, adding one for the behaviour if it is missing), commit with the same trailers as before, and run the acceptance tests once more to the end. If you believe the test is wrong against the specification, change nothing for it and return it as a package (the test's name, its message, the specification's line, your recommendation and confidence). Never read the test's source.
5. Leave no `pytest-of-usain/` or other scratch in the worktree.

Return in the twelve fields as before (labelled lines first; refused twice for the same call, stop and say so), then the sandbox check, the acceptance results by name, any commit with its trailers, `git log --oneline -3` and `git status --short`.
