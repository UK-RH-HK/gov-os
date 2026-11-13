
## Rules
- Every pytest goes through the heavy-slot gate (the CTO's order, 2026-11-12), one folder (or one file) per run:
  `TMPDIR=/home/usain/gov-os-runs/tmp/W2-171 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-171/src python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
  Run the eight cases first; then tests/acceptance/W2-171, tests/unit/memaudit and tests/acceptance/W2-170 once each
  before your last commit.
- Add or update a unit test in tests/unit/memaudit for each behaviour you change. Update
  docs/changes/W2-171-evidence.md with what changed and why.
- The scratch folder refuses the Write tool here; use single plain commands. Literal paths only as write targets. No
  merge, no push, no edit outside your paths.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-k1e2" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1074, DEC-833, DEC-860, DEC-1118, DEC-1050, DEC-1073" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line of each folder run) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

The ticket's context packet (`gov context DAEO-k1e2 --role engineer`, built by your lead) follows.
