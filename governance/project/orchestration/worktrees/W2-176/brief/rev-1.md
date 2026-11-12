Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-176 (DAEO-ktiw), independent auditor, review round 1 (CAP-33 independent review of a kernel template delta)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** independent-auditor, a fresh read-only session. Write nothing in the repository; your verdict goes in your
return. **Worktree:** `/home/usain/gov-os-worktrees/W2-176`, branch `w2/W2-176`. **Probe:** head `13fd1dd34e32`
against base `1798e82f1201` (`git diff 1798e82f1201..13fd1dd34e32`). **Ticket:** `DAEO-ktiw` (W2-176), class C3,
profile STANDARD.

## What to audit
The ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ktiw.md` is the spec: judge each KPI line S1, S2,
S3, F1, F2 against the code and the tests at the probe head (S4, the CIT-P record, is written after your review: mark
it out of this round). The governed context packet (ticket and mandatory inputs) is at
`/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/lead/briefs/rev-context.md`; read decisions by id in
`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (DEC-1140, DEC-838, DEC-901, DEC-445,
DEC-208, DEC-250, DEC-315, DEC-264, DEC-259).

The delta: `template/governance/kernel/hooks/precompact.py` (changed), `template/governance/kernel/hooks/context_watch.py`
(new), `tests/unit/hooks/test_w2_176_precompact.py`, `tests/unit/hooks/test_w2_176_context_watch.py`.
`template/governance/kernel/hooks/sessionstart.py` imports from precompact.py; the hooks are registered in
`.claude/settings.json` (context_watch.py is not registered yet: a later ACT, not in this delta).

Reference facts (official hooks docs, code.claude.com/docs/en/hooks, CLI 2.1.322): a PreCompact hook's stdout on exit 0
becomes instructions for the compaction summary; Claude Code discards a PreCompact hook's `systemMessage`; exit 2 or
`"decision": "block"` blocks compaction. PostToolUse input has the common fields (`session_id`, `transcript_path`,
`cwd`, `hook_event_name`) plus the tool fields, no `model`; context goes out as
`{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "..."}}`. Verify anything else yourself.

Probe as an adversary: the hook must never block or slow a tool call or a compaction, never write outside the
session's `.gov-runtime/scratch`, never set or read a compaction threshold; the read-first line must name the right
file for the CTO (main tree), a lead (linked worktree) and a worker; the reminder must fire once per session at 85 %
and not below; failure modes (partial last line, sidechain lines, huge transcript, odd session ids, missing
CLAUDE_PROJECT_DIR) must fail safe. Run the tests yourself (no edits):
`env HOME=/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-176/src python3 -m pytest tests/unit/hooks -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
and judge every failure you see: in scope or not, and what it means for the delta.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
Then your findings, each with an id, the file:line, what happens, and a reproduction; then exactly one fenced block
opened by ```verdict holding JSON in this form (one entry per KPI line S1, S2, S3, F1, F2):
`{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`
Then one line: `VERDICT: READY` or `VERDICT: NOT READY`, with the probe head.
