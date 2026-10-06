# W1-29 Session hooks — acceptance tests

Ticket: `DAEO-zsvl` (W1-29), profile STANDARD (DEC-221).
Tests written by the Independent Test Designer (MR-3, DEC-069) before
implementation.

## KPI-to-test map

### Success line 1 — SessionStart injects gov context --brief plus tk ready within the 2.5k-token cap; PreCompact and Stop write checkpoints and respect stop_hook_active [CAP-15.g, CAP-37.b]

| Test | Covers | Red reason |
|------|--------|------------|
| `TestSessionStart::test_injects_context_brief_on_startup` | CAP-15.g | hook not built |
| `TestSessionStart::test_reinjects_on_compact_clear_resume[compact]` | CAP-37.b, DEC-208 | hook not built |
| `TestSessionStart::test_reinjects_on_compact_clear_resume[clear]` | CAP-37.b, DEC-208 | hook not built |
| `TestSessionStart::test_reinjects_on_compact_clear_resume[resume]` | CAP-37.b, DEC-208 | hook not built |
| `TestPreCompact::test_writes_checkpoint` | CAP-37.b | hook not built |
| `TestStop::test_writes_checkpoint` | CAP-37.b | hook not built |
| `TestStop::test_respects_stop_hook_active` | CAP-37.b | hook not built |

### Success line 2 — SubagentStop enforces the 12-field return contract of Framework §61 [CAP-37.d]

| Test | Covers | Red reason |
|------|--------|------------|
| `TestSubagentStop::test_accepts_all_twelve_fields` | CAP-37.d | hook not built |
| `TestSubagentStop::test_blocks_missing_fields` | CAP-37.d | hook not built |
| `TestSubagentStop::test_block_includes_reason_and_is_once` | CAP-37.d | hook not built |

### Success line 3 — A checkpoint is written when context utilisation passes the threshold, not only at PreCompact [CAP-37.c]

| Test | Covers | Red reason |
|------|--------|------------|
| `TestCheckpointOnContextUtilisation::test_stop_writes_checkpoint_not_only_precompact` | CAP-37.c | hook not built |
| `TestCheckpointOnContextUtilisation::test_watchdog_marks_stale_on_context_utilisation` | CAP-37.c | GREEN (tests W1-25 `record.watch`) |

### Success line 4 — Compaction preserves decisions, ticket and loop counts; PreCompact checkpoint, SessionStart re-injection, auto-compact threshold (DEC-208)

| Test | Covers | Red reason |
|------|--------|------------|
| `TestCompactionPreservesState::test_precompact_then_sessionstart_preserves_ticket` | DEC-208 | hook not built |
| `TestCompactionPreservesState::test_auto_compact_threshold` | DEC-208 | hook not built |

### Failure line 1 — A Stop hook loops

| Test | Covers | Red reason |
|------|--------|------------|
| `TestNoStopLoop::test_stop_exits_without_side_effects_when_active` | DEC-025 | hook not built |

### Failure line 2 — SessionStart injects more than the cap

| Test | Covers | Red reason |
|------|--------|------------|
| `TestInjectionCap::test_large_context_within_cap` | CAP-15.g | hook not built |

### Failure line 3 — A handoff or ticket close proceeds while the latest checkpoint is stale for its policy

| Test | Covers | Red reason |
|------|--------|------------|
| `TestWatchdogBlocksStale::test_stale_by_age` | CAP-37.c | GREEN (tests W1-25 `record.watch`) |
| `TestWatchdogBlocksStale::test_missing_checkpoint` | CAP-37.c | GREEN (tests W1-25 `record.watch`) |
| `TestWatchdogBlocksStale::test_stale_on_ticket_transition` | CAP-37.c | GREEN (tests W1-25 `record.watch`) |

## Covers coverage

| Covers id | Item | Tests |
|-----------|------|-------|
| CAP-15.g | File path + summary ≤ ~2.5k tokens (harness output caps) | `test_injects_context_brief_on_startup`, `test_large_context_within_cap` |
| CAP-37.b | Mandatory triggers incl. ticket transition, compaction, stop | `test_writes_checkpoint` (PreCompact), `test_writes_checkpoint` (Stop), `test_reinjects_on_compact_clear_resume`, `test_respects_stop_hook_active` |
| CAP-37.c | Provider-independent watchdog: marks stale; checkpoints on context utilisation; blocks handoff/close when freshness violates policy | `test_stop_writes_checkpoint_not_only_precompact`, `test_watchdog_marks_stale_on_context_utilisation`, `test_stale_by_age`, `test_missing_checkpoint`, `test_stale_on_ticket_transition` |
| CAP-37.d | Worker return contract: the 12 fields | `test_accepts_all_twelve_fields`, `test_blocks_missing_fields`, `test_block_includes_reason_and_is_once` |

## Red/green summary

- **15 hook tests** fail because `src/gov/hooks/` is empty (the module under
  test does not exist yet).
- **4 watchdog tests** pass because they test `gov.checkpoint.record.watch`
  (W1-25), which is already built.  Since `gov close` (W1-30) is not built,
  these test the function directly per the instruction: "if the watchdog can
  only be a function that W1-30 calls, the case tests the function."

Total: **19 test cases** (the parametrized `test_reinjects_on_compact_clear_resume`
counts as 3).

## Determined from sources

### 1. Hook inputs and outputs (Claude Code 2.1.288)

- **SessionStart**: input field `source` distinguishes `startup`, `resume`,
  `clear`, `compact`, `fork`.  W1-29 acts on all four non-fork sources.
  Output: `{"hookSpecificOutput": {"hookEventName": "SessionStart",
  "additionalContext": "<text>"}}`.  The `additionalContext` cap is 10 000
  characters.

- **Stop**: input includes `stop_hook_active` — an object
  `{hook_name, hook_type, matcher, event_name}` that identifies the hook
  currently running.  When present the hook must exit 0 without acting to
  prevent re-entrancy loops.

- **SubagentStop**: input includes `last_assistant_message` (the subagent's
  final output) and `agent_id`/`agent_type`.  The hook enforces the 12-field
  contract by parsing the message; exit 2 blocks with a reason, once.

- **PreCompact**: input includes `trigger` (manual/auto).  The hook writes a
  checkpoint and always exits 0 (never blocks compaction).

### 2. The 12 fields

task, status, work_completed, files_changed, evidence, tests, discoveries,
risks, lessons, proposed_decisions, unresolved, recommended_next_action.

"Enforces" = SubagentStop exit 2 with a reason naming missing fields.  The
block is once — it does not loop.

### 3. Where a checkpoint is written

By `gov checkpoint --ticket <id> --trigger <trigger> --next <text>` (W1-25,
`gov.checkpoint.record.write`) under `docs/checkpoints/<ticket>/`.

"Stale for its policy" = the watchdog (`gov checkpoint --watch`), which checks
age, commits since the checkpoint, context utilisation and ticket-status
transitions.  Exit 3 = `CHECKPOINT_STALE` or `CHECKPOINT_MISSING`.

`gov close` (W1-30) is not built.  The tests test `record.watch()` directly.

### 4. The cap

`_tokens(text) = ceil(len(text) / 4)` from `src/gov/context/__init__.py`.
`BRIEF_LIMIT = 2500` tokens = 10 000 characters.

### 5. "Preserves the open decisions, the active ticket and the loop counts"

- **Active ticket**: `GOV_TICKET` env var, recorded in the checkpoint's `task`
  field.
- **Open decisions**: in the checkpoint body and `next_action`.
- **Loop counts**: held by the orchestrator or `gov`, never disclosed to
  sessions inside the loop (DEC-096).  The checkpoint records them for the
  session's own use on resume.

### 6. Auto-compact threshold

Claude Code 2.1.288 supports `autoCompactWindow` in settings.json.  The
project sets it to approximately 300 000 tokens.  Since this is a configuration
concern (not a hook concern), the test verifies the hooks exist and handle
compaction correctly; the threshold value is verified by the orchestrator.
The fallback (CONTEXT_CHECKPOINT stop) applies only when the setting is
unavailable, which does not apply to the pinned version.

## Residual: S0a-G-09

Source S0a-G-09 is listed among the ticket's sources and its text is not in
the tree.  No test is derived from unread text.
