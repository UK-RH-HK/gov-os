```

## Rules
- The one judged path stays one: never copy the reader path into a second module; `prompts.py` unchanged. `maintain` is
  never a gate (exit 0 always, 4 for usage). Counts only: no id or text of a standing set outside its run folder.
- Keep green what is green: `tests/unit/memaudit`, `tests/acceptance/W2-170`, `W2-171` (but for the two cases of the
  lead's open package P1, `test_the_ledger_events_have_item_3s_fields` and
  `test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result`, which pin the old bar outside the ticket's
  paths), `W2-172` (but for two cases the test designer is fixing in parallel: `test_s6_a_log_present_but_empty_is_empty`
  and `test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log`), `W2-173`, `W2-88`.
  Two W2-187 cases are also being revised by the test designer and may stay red here:
  `test_s2_a_run_writes_the_declaration_then_used_before_any_search` and
  `test_s8_the_owners_decision_id_closes_it_and_is_recorded`. Never edit `tests/acceptance/`.
- Add or update unit tests under `tests/unit/memaudit/` for what you change, and update
  `docs/changes/W2-187-evidence.md` (per KPI line, the cases and their result; the pytest summary lines).
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest tests/acceptance/W2-187 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for each folder above, one folder per run; a single case: append `::<name>`. A heavy-slot or resource
  gate refusal is a wait: run again when it opens.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/eng/,
  run with `bash <file>` or `python3 <file>`. Literal paths only as write targets.
- **Commit** your paths only, the trailers in ONE final paragraph:
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write or a Bash form is a refusal too: do not
  redo the same edit by another form; report it.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of each folder) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
