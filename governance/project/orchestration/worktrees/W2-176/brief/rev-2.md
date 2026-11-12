Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-176 (DAEO-ktiw), independent auditor, review round 2, the last one (CAP-33 review of a kernel template delta; DEC-1010)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** independent-auditor, a fresh read-only session. Write nothing in the repository; your verdict goes in your
return. **Worktree:** `/home/usain/gov-os-worktrees/W2-176`, branch `w2/W2-176`. **Probe:** head `7894a35e116f` against
base `1798e82f1201` (the whole delta: `git diff 1798e82f1201..7894a35e116f -- template tests`); round 2's own change is
`git diff 13fd1dd34e32..7894a35e116f -- template tests`. **Ticket:** `DAEO-ktiw` (W2-176), class C3, profile STANDARD.

## What to audit
The ticket `/home/usain/gov-os-worktrees/W2-176/.tickets/DAEO-ktiw.md` is the spec (S2 was amended after round 1; read
the "Delegated" line at its end): judge each KPI line S1, S2, S3, F1, F2 against the code and the tests at the probe head.
S4 (the CIT-P record, `docs/changes/W2-176-CIT-P.md`) is the lead's and is finished after your review: out of this round.
The governed context packet is `/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/lead/briefs/rev-context-2.md`;
read decisions by id in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (DEC-1140 (1)(b) and (4),
DEC-1118 (A), DEC-838, DEC-901, DEC-445, DEC-208, DEC-250, DEC-264, DEC-259, DEC-315).

Round 1 (head `13fd1dd34e32`) was READY with findings R1-R7. The CTO then decided: P1 (a) the two older test files
`tests/unit/hooks/test_resume_hooks.py` and `test_w29_hooks.py` for assert-only updates to S1's form; P2 (a) the CTO's
report-state path is `<root>/.gov-runtime/scratch/orchestrator/log/report-state.json`, with R7 (OSError caught in
`newest()`); P3 R2 (events carrying `agent_id` skipped) and R1 (re-armed once usage falls below 50 %); P4 leads and
workers reminded against `min(model window, 200,000)` (DEC-1118 (A)), the CTO's own session (`GOV_TICKET` a coordination
ticket) against its model's window (DEC-1140 (4)). Check each is done as decided, and that nothing round 1 found sound
broke. R3 (a worker's brief chosen as the newest file in a shared folder) and R6 (no `CLAUDE_PROJECT_DIR`) were left as
recorded rows; say whether that still holds.

The delta: `template/governance/kernel/hooks/precompact.py` (changed), `template/governance/kernel/hooks/context_watch.py`
(new; it imports `checkpoint_rel` from precompact.py), the W2-176 unit tests, and the two older test files (assert-only:
check that only assertions changed). `sessionstart.py` imports from precompact.py; context_watch.py is not registered in
`.claude/settings.json` yet (a later ACT, not in this delta).

Reference facts (official hooks docs, code.claude.com/docs/en/hooks): a PreCompact hook's stdout on exit 0 becomes
instructions for the compaction summary; Claude Code discards a PreCompact hook's `systemMessage`; exit 2 or
`"decision": "block"` blocks compaction. PostToolUse input has the common fields (`session_id`, `transcript_path`, `cwd`,
`hook_event_name`, and `agent_id` inside a subagent) plus the tool fields, no `model`; context goes out as
`{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "..."}}`. Verify anything else yourself.

Probe as an adversary: never block or slow a tool call or a compaction; never write outside the session's
`.gov-runtime/scratch` (including `__pycache__`); never set or read a compaction threshold; the right files and window for
the CTO (main tree, coordination ticket), a lead (orchestrator on its own ticket, linked worktree) and a worker; the
reminder once per context window at 85 % and not below, re-armed below 50 % only; subagent events silent; the
coordination-ticket test fails toward the 200,000 cap (a hostile `GOV_TICKET`, a missing or huge ticket file); failure
modes fail safe. Run the tests yourself (no edits):
`env HOME=/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-176/src python3 -m pytest tests/unit/hooks -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
and judge every failure you see. The lead's acceptance regression is running in parallel; do not re-run it.

This is the last round (DEC-1010): classify each finding under DEC-809 (scope, ordinary work, consequence), so the lead
can land the non-blocking ones as recorded rows.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
Then your findings, each with an id (continue from R8), the file:line, what happens, and a reproduction; then exactly one
fenced block opened by ```verdict holding JSON in this form (one entry per KPI line S1, S2, S3, F1, F2):
`{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R8", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`
Then one line: `VERDICT: READY` or `VERDICT: NOT READY`, with the probe head.
