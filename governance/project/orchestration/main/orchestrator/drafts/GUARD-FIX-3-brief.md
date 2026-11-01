# ACT-GUARD-FIX-3 — the brief for its design subagent (DEC-1018 item 3); relaunch it from here after a reload

The first run started 2026-11-01 22:20 in the old session and stopped with that session. Its staging folder, possibly
partial: `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/20804c5c-af51-4450-934e-42f650effce2/scratchpad/guard-fix/`.
Tell the new subagent to read what is there first and reuse whatever is sound, and to stage into a new folder in its
own scratch area.

**Task.** Design, stage and measure a fix for the five-rule hook's acceptance-folder rule. The live hook is
`.claude/hooks/pretooluse.py`, and the write parser it imports is under `src/gov/`. Rule 1: only the independent test
designer writes `tests/acceptance/**` (MR-3, DEC-953 item 2). 57 of the 61 refusals in
`.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl` are false positives. The target is under 10 % false
positives (DEC-958), with no true write into the acceptance folder missed. Earlier fixes: ACT-GUARD-FIX-1
(`c3392f46`) and ACT-GUARD-FIX-2 (`ffc60703`), with their packages in `governance/project/orchestration/packages/`.

**Steps.**
1. Find the exact function that decides "may write the acceptance tests" for Bash.
2. Rebuild each row's full command from its `transcript` (the `tool_use` block whose `id` is the row's `key`).
   Redact anything that looks secret.
3. Gather the planted cases: `guard4_check.py` or similar, and the hook's tests.
4. Measure today's hook on both sets, driven as Claude Code drives it: JSON on stdin and the session's env.
5. Design the narrowest change. A write counts only when a write target resolves inside `tests/acceptance/`:
   - redirects and `tee`;
   - `cp` or `mv` destinations, `sed -i`, `touch`, `mkdir`, `rm`, `git checkout --`;
   - inline or heredoc code opening a path there for writing, `write_text`, `shutil` copies to it;
   - an undeterminable target stays refused (fail closed).

   Mentioning, reading or env-passing the path must pass. Fix the listing rule's fixed-file read case if it is safe.
6. Measure again: counts before and after, per rule.
7. Stage the proposed files, a unit test file and `ACT-GUARD-FIX-3.diff`, then run the tests.
8. Draft `ACT-GUARD-FIX-3.md` in the earlier ACTs' form:
   - context, the counts, the change, before and after;
   - the risk, the undo, and the exact files the operator changes (`.claude/hooks/` plus the product copy under
     `template/governance/kernel/hooks/`, or the ticket that owns the product half, DEC-1003);
   - options (a) apply, (b) the narrowest part, (c) defer, with a recommendation and its confidence.

**Never:**
- edit anything under `.claude/`, `template/`, `src/` or `tests/`;
- read the contents of `tests/acceptance/**`;
- run the live hook against real writes;
- print secrets.

Return the twelve fields, with the before and after counts in `evidence`.
