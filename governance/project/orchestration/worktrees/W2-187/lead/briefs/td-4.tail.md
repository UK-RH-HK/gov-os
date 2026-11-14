```

## Rules
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`, a Bash timeout of 3600000 ms:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -m pytest tests/acceptance/W2-187/test_w2_187_s12_push.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Report the summary line. The two revised push cases may stay red until the engineer's parallel batch lands (say what
  they fail on). The scope case judges only branch `w2/W2-187` and skips elsewhere; check it by reading.
- Literal paths only as write targets; if a Write into `.gov-runtime/scratch/` is refused, write no script.
- **Commit** your paths only, one commit, the trailers in ONE final paragraph:
  `git commit -m "<subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1182, DEC-1179, DEC-1156" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-187`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/` or the register.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write is a refusal too.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then
`commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
