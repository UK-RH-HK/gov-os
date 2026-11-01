Batch 3 accepted (ecb7824a). P-7: keep your per-kind run-time limits as defaults a project may set otherwise (your lead's decision). **Now do batch 4 of your brief (the versions, the rulesync sources, the generated copies through the adapter, the CIT-P, and one run of the acceptance tests reading results only), commit it, and return** with the twelve fields first, as before, plus lines added and removed per file, the validator's result per skill, the adapter check's output, the acceptance run's counts and failing case names, and your scratch figures. Every rule of your original brief still holds. Step 0 again (a new launch).

Notes from your lead for this batch:
1. **Versions (G13):** every kernel skill but `adopt` gains `metadata:` with `version: "<the same as its top-level version>"`; a skill changed in this round has already raised its version (orchestration 1.1.0, audit 1.2.0, test-design 1.1.0, qa-review 1.0.0): check each. The unchanged skills (change, checkpoint, discovery, planning, retrieval) gain only the `metadata` lines; nothing else in their files changes. The skill template already carries `metadata.version`.
2. **Sources and copies:** the `.rulesync/skills/<name>/` and `template/.rulesync/skills/<name>/` folders of every kernel skill you touched (versions included) and `qa-review` (new) match the kernel exactly as your brief says; `.rulesync/subagents/orchestrator.md` and `template/.rulesync/subagents/orchestrator.md` carry the role file's body. Then generate with rulesync into an empty temporary folder and copy only in-path generated files (`.claude/skills/<each kernel skill but adopt>/**`, `.claude/agents/orchestrator.md`). If a compound command under `/tmp/gov-os-lead-W2-11` needs approval, use your session scratchpad as the empty folder instead. Then run the adapter check (`gov.adapters.portability`, from the worktree root, with this worktree's `src/`). Name every finding it reports and whether it is on a file outside your paths (for example the adopt skill or the vendored skills); fix only what is in your paths.
3. **The CIT-P** `docs/changes/W2-11-CIT-P.md`: as your brief says; lean (about 100 to 150 lines). Include under "Not in this round / outside the paths" your packages P-1 to P-7 in one line each, and that the generated copies carry the version as `metadata.version` because the adapter writes no top-level `version` (the launcher's skill reader, held by another ticket, must read it there: your lead's package).
4. **The acceptance run, once, after your last commit:** `TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m pytest tests/acceptance/W2-11 tests/acceptance/W1-35 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE`; report the counts and the names of the failing cases with their one-line failure messages. Do not open the test source; do not change anything after the run (your lead decides what follows).

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

The twelve fields first, any payload after. Refused twice for the same call: stop and say so.
