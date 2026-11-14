```

## Rules
- Counts only (F7): no finding's text, secret, match or line in any output, log or digest; git's own output only in the
  0600 file in the key folder, never printed. `push.py` stays the only gitleaks caller. `say` the only printer.
- Keep green: `tests/unit/memaudit`, `tests/unit/adopt/test_w2_187*`, `tests/acceptance/W2-187` (but the two
  no-declaration cases and `test_scope_...`, which the test designer is revising), `tests/acceptance/W2-172` (whole,
  unchanged files), `tests/acceptance/W2-171`.
- Update the unit tests and `docs/changes/W2-187-evidence.md` (the reading above, under S12).
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`, a Bash timeout of 3600000 ms each:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest tests/acceptance/W2-187 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same per folder above. A heavy-slot refusal is a wait.
- Literal paths only as write targets; if a Write into `.gov-runtime/scratch/` is refused, write no script.
- **Commit** your paths only, the trailers in ONE final paragraph:
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1182, DEC-1179, DEC-1101" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another form (DEC-1142 (9)). A permission denial of a Write or a Bash form is a refusal too: report it.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence (the pytest summary lines) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form |
the hook's reason | true or false-positive).
