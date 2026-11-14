```

## Rules
- Change only what the four cases need; every other case of the four folders keeps its bytes. Every W2-172 test file
  other than `test_w2_172_s7_digest.py` stays byte-unchanged.
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Run each of the four cases alone (append `::<name>`), then the whole `tests/acceptance/W2-172` folder, and report
  each summary line. The four must pass against the merged code; W2-172's folder must be green. A heavy-slot refusal is
  a wait; run again when it opens.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- **Commit** your paths only, the trailers in ONE final paragraph:
  `git commit -m "<subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1179, DEC-1156" [--trailer "Rewrite-Reason: DEC-1179 (5)"] --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  (one commit for the W2-187 cases; one for the W2-172 helper and s7 with the Rewrite-Reason). Never `Role: owner` or
  `Decided-by:`. No merge, no push, no edit of `.tickets/` or the register.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write is a refusal too: do not redo it by
  another form.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
