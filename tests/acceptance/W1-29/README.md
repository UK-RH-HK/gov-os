# W1-29 Session hooks — acceptance tests

Ticket: `DAEO-zsvl` (W1-29), profile STANDARD (DEC-221).
Tests written by the Independent Test Designer (MR-3, DEC-069) before
implementation.

## Test infrastructure

The combined PreCompact and SessionStart hooks are the same files the W1-49
suite exercises: `template/governance/kernel/hooks/precompact.py` and
`sessionstart.py`.  For these two events, W1-29 tests run the registered
shell commands (read from `.claude/settings.json`) in a temporary project
built by `w1_49_support.make_project()`, extended with W1-29 fixture data
(ticket, checkpoint record).  Every case of `tests/acceptance/W1-49/` passes
unchanged: W1-29 adds to W1-49's hooks, it does not replace them.

Stop and SubagentStop are W1-29-only hooks in `src/gov/hooks/`.  They are
run as Python scripts directly because they may not yet be registered.

The watchdog tests call `gov.checkpoint.record.watch` directly because
`gov close` (W1-30) is not built.

## KPI-to-test map

### Success line 1 — SessionStart injects gov context --brief plus tk ready within the 2.5k-token cap; PreCompact and Stop write checkpoints and respect stop_hook_active [CAP-15.g, CAP-37.b]

| Test | Covers | Red reason |
|------|--------|------------|
| `TestSessionStart::test_injects_context_brief_on_startup` | CAP-15.g | hook not built |
| `TestSessionStart::test_reinjects_on_compact_clear_resume[compact]` | CAP-37.b, DEC-208 | hook not built |
| `TestSessionStart::test_reinjects_on_compact_clear_resume[clear]` | CAP-37.b, DEC-208 | hook not built |
| `TestSessionStart::test_reinjects_on_compact_clear_resume[resume]` | CAP-37.b, DEC-208 | hook not built |
| `TestSessionStart::test_orchestrator_compact_carries_prompt_path` | CAP-15.g, DEC-259 | hook not built |
| `TestSessionStart::test_orchestrator_compact_carries_resume_section` | CAP-37.b, DEC-259 | hook not built |
| `TestSessionStart::test_orchestrator_compact_combined_within_cap` | CAP-15.g, DEC-259 | hook not built |
| `TestPreCompact::test_writes_checkpoint` | CAP-37.b | hook not built |
| `TestStop::test_writes_checkpoint` | CAP-37.b | hook not built |
| `TestStop::test_no_checkpoint_without_ticket` | CAP-37.b, Point 4 | GREEN (Stop already skips when GOV_TICKET is empty) |
| `TestStop::test_respects_stop_hook_active` | CAP-37.b | hook not built |

### Success line 2 — SubagentStop enforces the 12-field return contract of Framework §61 [CAP-37.d]

| Test | Covers | Red reason |
|------|--------|------------|
| `TestSubagentStop::test_accepts_all_twelve_fields` | CAP-37.d | hook not built |
| `TestSubagentStop::test_blocks_missing_fields` | CAP-37.d | hook not built |
| `TestSubagentStop::test_block_includes_reason_and_is_once` | CAP-37.d | hook not built |
| `TestSubagentStop::test_malformed_input_fails_closed[empty stdin]` | CAP-37.d, DEC-136 | hook not built |
| `TestSubagentStop::test_malformed_input_fails_closed[invalid JSON]` | CAP-37.d, DEC-136 | hook not built |
| `TestSubagentStop::test_malformed_input_fails_closed[null last_assistant_message]` | CAP-37.d, DEC-136 | hook not built |
| `TestSubagentStop::test_text_labels_without_content_do_not_satisfy_contract` | CAP-37.d, DEC-413, Point 5 | RED (text-path regex accepts labels without content — fail-open) |
| `TestSubagentStop::test_empty_and_null_values_do_not_satisfy_contract` | CAP-37.d, DEC-136 | hook not built |

### Success line 3 — A checkpoint is written when context utilisation passes the threshold, not only at PreCompact [CAP-37.c]

| Test | Covers | Red reason |
|------|--------|------------|
| `TestCheckpointOnContextUtilisation::test_stop_writes_checkpoint_not_only_precompact` | CAP-37.c | hook not built |
| `TestCheckpointOnContextUtilisation::test_watchdog_marks_stale_on_context_utilisation` | CAP-37.c | GREEN (tests W1-25 `record.watch`) |

### Success line 4 — Compaction preserves decisions, ticket and loop counts; PreCompact checkpoint, SessionStart re-injection, auto-compact threshold (DEC-208)

| Test | Covers | Red reason |
|------|--------|------------|
| `TestCompactionPreservesState::test_precompact_then_sessionstart_preserves_ticket` | DEC-208 | hook not built |
| `TestCompactionPreservesState::test_precompact_then_sessionstart_preserves_decisions` | DEC-208, KPI line 4 | GREEN (preservation already works: PreCompact's `split()` keeps the written part) |
| `TestCompactionPreservesState::test_precompact_then_sessionstart_preserves_loop_counts` | DEC-208, DEC-096, KPI line 4 | GREEN (preservation already works) |
| `TestCompactionPreservesState::test_auto_compact_threshold` | DEC-208 | GREEN (rewrite: owner correction — see §9 below) |

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

### Cut order (DEC-136, Finding 3)

| Test | Covers | Red reason |
|------|--------|------------|
| `TestCutOrder::test_instruction_preserved_when_cap_tight` | CAP-15.g, DEC-136 | hook not built |

### DEC-444 — Automatic checkpoints go to the ignored scratch folder

Revised or added after the implementation, from the owner's decision DEC-444.

**Revised cases** (the assertion that the hook writes under `docs/checkpoints/`
is replaced by the assertion that it writes under
`.gov-runtime/scratch/checkpoints/` and writes nothing under
`docs/checkpoints/`; no other assertion weakened, no case removed):

| Test | Covers | Red reason |
|------|--------|------------|
| `TestPreCompact::test_writes_checkpoint` | CAP-37.b, DEC-444 | revised after implementation: owner decision DEC-444 — asserts scratch, current code writes to docs |
| `TestStop::test_writes_checkpoint` | CAP-37.b, DEC-444 | revised after implementation: owner decision DEC-444 — asserts scratch, current code writes to docs |
| `TestStop::test_no_checkpoint_without_ticket` | CAP-37.b, DEC-444 | revised after implementation: owner decision DEC-444 — GREEN (now checks both places; Stop still writes nothing without a ticket) |
| `TestStop::test_respects_stop_hook_active` | CAP-37.b, DEC-444 | revised after implementation: owner decision DEC-444 — GREEN (now checks scratch; stop_hook_active still prevents writing) |
| `TestCheckpointOnContextUtilisation::test_stop_writes_checkpoint_not_only_precompact` | CAP-37.c, DEC-444 | revised after implementation: owner decision DEC-444 — asserts scratch, current code writes to docs |
| `TestNoStopLoop::test_stop_exits_without_side_effects_when_active` | DEC-025, DEC-444 | revised after implementation: owner decision DEC-444 — GREEN (now checks scratch; no checkpoint is written when re-entered) |

**New cases:**

| Test | Covers | Red reason |
|------|--------|------------|
| `TestAutomaticCheckpointLocation::test_precompact_writes_under_scratch_not_docs` | DEC-444 point 1 | hook writes to docs/checkpoints/ instead of .gov-runtime/scratch/checkpoints/ |
| `TestAutomaticCheckpointLocation::test_stop_writes_under_scratch_not_docs` | DEC-444 point 1 | hook writes to docs/checkpoints/ instead of .gov-runtime/scratch/checkpoints/ |
| `TestAutomaticCheckpointLocation::test_precompact_does_not_create_docs_folder` | DEC-444 point 1 | hook creates docs/checkpoints/(ticket)/ |
| `TestDeliberateCheckpointLocation::test_gov_checkpoint_writes_under_docs_not_scratch` | DEC-444 point 2 | GREEN (current code already writes deliberate checkpoints to docs/checkpoints/) |
| `TestGitCleanAfterHook::test_precompact_leaves_tree_clean` | DEC-444 point 3 | hook writes untracked files under docs/checkpoints/ |
| `TestGitCleanAfterHook::test_stop_leaves_tree_clean` | DEC-444 point 3 | hook writes untracked files under docs/checkpoints/ |
| `TestCheckpointReinjection::test_reinjects_automatic_checkpoint_from_scratch` | DEC-444 point 4 | SessionStart does not look in .gov-runtime/scratch/checkpoints/ |
| `TestCheckpointReinjection::test_newer_automatic_wins_over_older_deliberate` | DEC-444 point 4 | SessionStart does not look in .gov-runtime/scratch/checkpoints/ |
| `TestCheckpointReinjection::test_newer_deliberate_wins_over_older_automatic` | DEC-444 point 4 | GREEN (SessionStart already reads from docs/checkpoints/, which is the deliberate location) |
| `TestCheckpointReinjection::test_injection_says_which_path` | DEC-444 point 4 | SessionStart does not report the scratch path |
| `TestWatchdogCountsBoth::test_automatic_checkpoint_counts_for_freshness` | DEC-444 point 4 | watchdog does not look in .gov-runtime/scratch/checkpoints/ |
| `TestRecordIdUniqueness::test_ids_unique_across_automatic_and_deliberate` | DEC-444 point 5 | id numbering does not consider both locations |

### Hook copies — src/gov/hooks/ matches template/governance/kernel/hooks/ (Point 6)

| Test | Covers | Red reason |
|------|--------|------------|
| `TestHookCopiesIdentical::test_hook_copies_identical[stop.py]` | Point 6 | GREEN (files are currently identical) |
| `TestHookCopiesIdentical::test_hook_copies_identical[subagentstop.py]` | Point 6 | GREEN (files are currently identical) |

## Covers coverage

| Covers id | Item | Tests |
|-----------|------|-------|
| CAP-15.g | File path + summary ≤ ~2.5k tokens (harness output caps) | `test_injects_context_brief_on_startup`, `test_large_context_within_cap`, `test_orchestrator_compact_carries_prompt_path`, `test_orchestrator_compact_combined_within_cap`, `test_instruction_preserved_when_cap_tight` |
| CAP-37.b | Mandatory triggers incl. ticket transition, compaction, stop | `test_writes_checkpoint` (PreCompact), `test_writes_checkpoint` (Stop), `test_no_checkpoint_without_ticket`, `test_reinjects_on_compact_clear_resume`, `test_respects_stop_hook_active`, `test_orchestrator_compact_carries_resume_section` |
| CAP-37.c | Provider-independent watchdog: marks stale; checkpoints on context utilisation; blocks handoff/close when freshness violates policy | `test_stop_writes_checkpoint_not_only_precompact`, `test_watchdog_marks_stale_on_context_utilisation`, `test_stale_by_age`, `test_missing_checkpoint`, `test_stale_on_ticket_transition` |
| CAP-37.d | Worker return contract: the 12 fields | `test_accepts_all_twelve_fields`, `test_blocks_missing_fields`, `test_block_includes_reason_and_is_once`, `test_malformed_input_fails_closed`, `test_empty_and_null_values_do_not_satisfy_contract`, `test_text_labels_without_content_do_not_satisfy_contract` |
| DEC-096 | Loop counts held by the orchestrator, never disclosed to sessions inside the loop | `test_precompact_then_sessionstart_preserves_loop_counts` |
| DEC-136 | Review findings feed the independent suite as described behaviour | `test_malformed_input_fails_closed`, `test_empty_and_null_values_do_not_satisfy_contract`, `test_instruction_preserved_when_cap_tight`, `test_text_labels_without_content_do_not_satisfy_contract` |
| DEC-208 | Compaction preserves decisions, ticket and loop counts; auto-compact threshold | `test_precompact_then_sessionstart_preserves_ticket`, `test_precompact_then_sessionstart_preserves_decisions`, `test_precompact_then_sessionstart_preserves_loop_counts`, `test_auto_compact_threshold` |
| DEC-259 | Hooks act only for GOV_ROLE=orchestrator (W1-49 behaviour); W1-29 extends so non-orchestrator roles get W1-29 content | `test_orchestrator_compact_carries_prompt_path`, `test_orchestrator_compact_carries_resume_section`, `test_orchestrator_compact_combined_within_cap` |
| DEC-413 | SubagentStop text-path fail-open on labels without content | `test_text_labels_without_content_do_not_satisfy_contract` |
| DEC-444 | Automatic checkpoints go to the ignored scratch folder; deliberate records stay under docs/checkpoints/ | `test_precompact_writes_under_scratch_not_docs`, `test_stop_writes_under_scratch_not_docs`, `test_precompact_does_not_create_docs_folder`, `test_gov_checkpoint_writes_under_docs_not_scratch`, `test_precompact_leaves_tree_clean`, `test_stop_leaves_tree_clean`, `test_reinjects_automatic_checkpoint_from_scratch`, `test_newer_automatic_wins_over_older_deliberate`, `test_newer_deliberate_wins_over_older_automatic`, `test_injection_says_which_path`, `test_automatic_checkpoint_counts_for_freshness`, `test_ids_unique_across_automatic_and_deliberate`, and 6 revised cases |

## Red/green summary

- **23 hook tests** fail because the hooks are not built yet (`src/gov/hooks/`
  is empty for Stop/SubagentStop; the combined PreCompact and SessionStart
  hooks at `template/governance/kernel/hooks/` do not yet include W1-29
  behaviour).
- **1 test is RED because it exposes a bug**: `test_text_labels_without_content_do_not_satisfy_contract`
  — the text-path regex in `_find_fields` accepts labels without content
  (DEC-413 fail-open).
- **4 watchdog tests** pass because they test `gov.checkpoint.record.watch`
  (W1-25), which is already built.  Since `gov close` (W1-30) is not built,
  these test the function directly per the instruction: "if the watchdog can
  only be a function that W1-30 calls, the case tests the function."
- **5 tests are GREEN** because they test existing behaviour:
  - `test_precompact_then_sessionstart_preserves_decisions` — PreCompact's
    `split()` already preserves the written part containing decision IDs.
  - `test_precompact_then_sessionstart_preserves_loop_counts` — same
    preservation mechanism for loop count content.
  - `test_auto_compact_threshold` (rewritten) — tests the compaction cycle
    that is already built, not the owner's settings file.
  - `test_no_checkpoint_without_ticket` — Stop already skips when
    `GOV_TICKET` is empty.
  - `test_hook_copies_identical[stop.py]` and `[subagentstop.py]` — files are
    currently byte-for-byte identical.

### DEC-444 cases (added 2026-10-07)

- **9 new DEC-444 tests are RED** because the hooks' automatic checkpoints
  still go to `docs/checkpoints/`, not to `.gov-runtime/scratch/checkpoints/`:
  `test_precompact_writes_under_scratch_not_docs`,
  `test_stop_writes_under_scratch_not_docs`,
  `test_precompact_does_not_create_docs_folder`,
  `test_precompact_leaves_tree_clean`,
  `test_stop_leaves_tree_clean`,
  `test_reinjects_automatic_checkpoint_from_scratch`,
  `test_newer_automatic_wins_over_older_deliberate`,
  `test_injection_says_which_path`,
  `test_automatic_checkpoint_counts_for_freshness`.
- **1 new DEC-444 test is RED** because the id numbering does not consider
  both locations: `test_ids_unique_across_automatic_and_deliberate`.
- **2 new DEC-444 tests are GREEN** because the existing code already
  satisfies them:
  - `test_gov_checkpoint_writes_under_docs_not_scratch` — deliberate
    `gov checkpoint` already writes to `docs/checkpoints/`.
  - `test_newer_deliberate_wins_over_older_automatic` — SessionStart already
    reads from `docs/checkpoints/`, which is the deliberate location.
- **3 revised cases are RED** because the assertion was changed from
  `docs/checkpoints/` to `.gov-runtime/scratch/checkpoints/`:
  `test_writes_checkpoint` (PreCompact),
  `test_writes_checkpoint` (Stop),
  `test_stop_writes_checkpoint_not_only_precompact`.
- **3 revised cases remain GREEN**: `test_no_checkpoint_without_ticket`,
  `test_respects_stop_hook_active`,
  `test_stop_exits_without_side_effects_when_active`.

Total: **45 test cases** (the parametrized `test_reinjects_on_compact_clear_resume`
counts as 3; the parametrized `test_malformed_input_fails_closed` counts as 3;
the parametrized `test_hook_copies_identical` counts as 2).

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
block is once — it does not loop.  Empty string `""` and `null` values do
not satisfy the contract (DEC-136, Finding 2).

### 3. Where a checkpoint is written

A deliberate checkpoint (`gov checkpoint`, W1-25) writes under
`docs/checkpoints/<ticket>/`.  An automatic checkpoint (written by the
PreCompact or Stop hook) writes under
`.gov-runtime/scratch/checkpoints/<ticket>/` (DEC-444).

"Stale for its policy" = the watchdog (`gov checkpoint --watch`), which checks
age, commits since the checkpoint, context utilisation and ticket-status
transitions.  Exit 3 = `CHECKPOINT_STALE` or `CHECKPOINT_MISSING`.  The
watchdog counts the newer of the two (automatic and deliberate) checkpoints
(DEC-444).

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

### 6. Auto-compact threshold (revised — owner correction)

The correct Claude Code setting is `autocompact` (not `autoCompactWindow`).
It lives in `.claude/settings.json`, which is the owner's file and is NOT in
this ticket's `allowed_paths`.  The pinned Claude Code version (2.1.288)
supports this setting.  The project sets it to approximately 300 000 tokens;
the exact line is `"autocompact": 300000`.  Since the setting is in the owner's
file, the test verifies what IS in this ticket's reach: the hooks handle
compaction correctly (PreCompact writes a checkpoint and SessionStart
re-injects it on compact).  The KPI's fallback ("if it can't be configured the
orchestrator's CONTEXT_CHECKPOINT stop stays") does not apply because the
pinned version supports it.

The original `test_auto_compact_threshold` was vacuous (asserted only that
SessionStart exits 0 — a case that cannot fail is not a case).  It has been
rewritten to verify the compaction cycle, with reason: "owner correction — the
setting is in the owner's file, not reachable by this ticket's paths."

### 7. Combined hook behaviour (W1-49 + W1-29)

The PreCompact and SessionStart hooks at `template/governance/kernel/hooks/`
combine W1-49 and W1-29 behaviour:

- **Combined PreCompact**: for orchestrator, appends a generated state block
  to `CHECKPOINT.md` (W1-49, DEC-264) AND writes a checkpoint record via
  `gov.checkpoint.record.write` (W1-29).  For non-orchestrator, writes the
  checkpoint record only (DEC-259).  Never blocks.

- **Combined SessionStart**: for orchestrator on compact/clear/resume, injects
  prompt path, RESUME HERE section, staleness warning (W1-49) AND
  `gov context --brief` + `tk ready` (W1-29), all within the 10 000-character
  cap.  For non-orchestrator, W1-29 content only.

- **Cut order** (Finding 3): when the combined injection exceeds the cap,
  context brief and tk ready are cut first.  The instruction to read the prompt
  and checkpoint and the staleness warning are last to be cut.

### 8. Empty/null values (Finding 2)

Empty string `""` and `null` values in the SubagentStop 12-field return
contract do not count as "present".  The contract requires meaningful values.
SubagentStop must block (exit 2) when any field is empty or null.

### 9. Context utilisation and checkpoints (Point 3)

KPI line 3 says "a checkpoint is written when the session's context utilisation
passes the configured threshold, not only at PreCompact."  No Claude Code hook
input carries context utilisation.  The hook inputs are:

- **Stop**: `hook_event_name`, `session_id`, `cwd`, `last_assistant_message`,
  optionally `stop_hook_active`.
- **PreCompact**: `trigger` (manual/auto).
- **SessionStart**: `source`.

No hook can read context utilisation at call time.  The clause is met only as:

1. **A checkpoint at every stop** — the Stop hook writes a checkpoint at every
   stop (tested by `test_stop_writes_checkpoint_not_only_precompact`).
2. **The watchdog marks stale on utilisation** — W1-25's `record.watch` marks
   the checkpoint stale when context utilisation exceeds the threshold (tested
   by `test_watchdog_marks_stale_on_context_utilisation`).

No hook can write a checkpoint triggered BY utilisation passing a threshold
because no hook input carries utilisation.  This is a residual for the owner:
the KPI line's literal reading is not met by any hook mechanism.  The existing
tests cover what IS possible.

### 10. Checkpoint files under docs/checkpoints/ (Point 4)

Stop writes a checkpoint record at every stop, and PreCompact at every
compaction, as untracked files under `docs/checkpoints/<ticket>/`.

1. **Who commits them?**  W1-25 writes them as files via
   `gov.checkpoint.record.write`.  No code in W1-25, W1-29 or W1-49 commits
   them.  W1-30 (`gov close`) is not built.  They stay untracked until
   something commits them.

2. **What does a session with no GOV_TICKET write?**  Nothing.  The Stop hook
   checks `ticket = os.environ.get("GOV_TICKET", "")` and returns if empty.
   PreCompact does the same.  So a session without GOV_TICKET writes no
   checkpoint.  Tested by `test_no_checkpoint_without_ticket`.

3. **Can a worker's hook write docs/checkpoints/ even if the guard restricts
   that path?**  Yes.  A hook is a subprocess (`python3 script.py`) that writes
   directly to the filesystem.  The guard mediates tool calls (Read, Write,
   Edit, Bash targets), not subprocess writes.  So a worker whose
   `allowed_paths` exclude `docs/` still has its hook write checkpoint files
   there.

### 11. SubagentStop text-path fail-open (DEC-413, Point 5)

The `_find_fields` function in `subagentstop.py` has two parsing paths:

1. **JSON path**: checks `obj[k] is not None and obj[k] != ""` — correct,
   blocks empty/null.
2. **Text path**: regex `(?:^|\n)\s*(?:#+\s*)?[\*_]*{field}[\*_]*\s*[:=\n]` —
   matches a label like `task:` with NOTHING after it.  A message like
   `task:\nstatus:\nwork_completed:\n...` passes all 12 fields through the
   text path with no actual content.  This is a fail-open.

Every one of the twelve fields needs content in both forms.  The text path
must verify content exists after the label, not just the label itself.  Tested
by `test_text_labels_without_content_do_not_satisfy_contract`.

### 12. Hook copies: src/gov/hooks/ vs template/governance/kernel/hooks/ (Point 6)

`src/gov/hooks/stop.py` and `src/gov/hooks/subagentstop.py` are byte-for-byte
copies of `template/governance/kernel/hooks/stop.py` and
`template/governance/kernel/hooks/subagentstop.py`.  The template hooks are
installed into projects by the kernel installer.  The `src/` copies are used
by tests (`conftest.py`'s `HOOKS_DIR = REPO_ROOT / "src" / "gov" / "hooks"`
and `run_w29_hook`).  The test `test_hook_copies_identical` pins that they are
identical so a divergence is caught immediately.

## Residual: S0a-G-09

Source S0a-G-09 is listed among the ticket's sources and its text is not in
the tree.  No test is derived from unread text.
