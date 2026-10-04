# W1-49 acceptance tests: light auto-resume hooks

Ticket `DAEO-32n6` (W1-49), profile FULL, covers item CAP-37.g. Written by the Independent Test Designer (MR-3,
DEC-069) from the ticket's KPI lines, CAP-37 and DEC-248, DEC-208, DEC-237, DEC-250, DEC-259, DEC-263, DEC-264.

Run: `python3 -m pytest tests/acceptance/W1-49 -q -p no:cacheprovider`
Without the real session and the CLI: add `-m "not local_only"`.

93 tests: 83 deterministic with no network, 10 marked `local_only` (9 share one real session, 1 runs
`claude --help`). Their history:

| Batch | When | Tests |
|---|---|---|
| 1 | Before the implementation | 62 written |
| 2 | After it, from a review's findings (DEC-136) | 3 added: 65 |
| 3 | After it, on the owner's decisions DEC-263 and DEC-264 | 15 rewritten and 2 removed (reason "owner decision, DEC-264"), 30 added (reason "owner decision"): 93 |

Batch 3 by name is in section 2.1.

## 1. What the engineer builds (the interface these tests fix)

| What | Fixed by these tests |
|---|---|
| Hook files | `template/governance/kernel/hooks/precompact.py` and `template/governance/kernel/hooks/sessionstart.py` |
| Registration | In the `hooks` key of `.claude/settings.json`: `PreCompact` for the triggers `manual` and `auto` (no matcher does it); `SessionStart` for the sources `compact`, `clear` and `resume`. Each command finds its file through `$CLAUDE_PROJECT_DIR`, as the guard hooks do. `startup` is neither required nor forbidden. |
| Input | The hook event's JSON object on stdin: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, and `trigger` + `custom_instructions` (PreCompact) or `source` + `model` (SessionStart). `CLAUDE_PROJECT_DIR`, `GOV_ROLE` and, for a ticket lead, `GOV_TICKET` in the environment. `tk` and `git` are found on `PATH`. |
| Roles (DEC-259) | The hooks act only when `GOV_ROLE` is exactly `orchestrator`. For any other role PreCompact writes to no checkpoint and SessionStart injects nothing of one; both end with 0. |
| Which checkpoint | In the main tree `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`; in a linked git worktree `.gov-runtime/scratch/lead/CHECKPOINT.md` of that worktree. A worktree session never reads or writes the main tree's checkpoint. The hook chooses without calling git: in a linked worktree `.git` is a file, in the main tree a directory. That keeps the choice working when git fails. |
| PreCompact: never blocks (DEC-264) | Exit 0 for `manual` and `auto`, whatever the checkpoint's age, and without one. No JSON answer with `decision: block` or `continue: false`. Input it can't read: any exit code but 2. Nothing of DEC-258 remains: no 30-minute age, no exit 2, no `CHECKPOINT NOT CURRENT`. |
| PreCompact: the state block (DEC-264) | The hook appends one generated block to the checkpoint, in this layout (the first and last lines exactly; the labels at the start of their lines; the rest of each line is free): |

```
<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-10-04T14:25:03Z
git head: <the full hash `git rev-parse HEAD` gives in this tree>
tickets in progress (`tk ls --status=in_progress`):
  <each line tk printed, unchanged>
worktrees (`git worktree list`):
  <each line git printed, unchanged>
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
```

| What | Fixed by these tests |
|---|---|
| The written part | Everything the session wrote: the file's content before the block. The hook never changes, cuts or reorders it; it stays first, byte for byte. If it doesn't end with a newline the hook may add one before the block, once. |
| How the block is found | A file holds a generated block only when its last line that is not empty is the end marker. The block then starts at the **last** line that is the begin marker and nothing else. On the next compaction the hook replaces exactly that block: there is one block, the newest, and what separates it from the written part doesn't grow. Marker text anywhere else belongs to the written part and stays: quoted in a sentence, or as whole lines in a code block that the file doesn't end with. The block holds no heading line, so it can't be taken for a section. |
| `tk` and git | Both are run in the tree (`CLAUDE_PROJECT_DIR`): `tk ls --status=in_progress`, `git rev-parse HEAD`, `git worktree list`. When one is not on `PATH`, fails or times out, the hook still ends with 0 and still appends the block; the label's line then reads `<label>: unavailable (<why>)`. What the other command gave stays in the block. |
| Pending owner decisions (DP-5) | A hook is a command and doesn't know them. The line says `not known to the hook` and points to the written part. The hook copies no decision from the written part into the block: that would give old text the look of generated state. |
| The file's modification time (DP-4) | After the append the hook sets the file's modification time back to what it was before (`os.utime`). So the file's time is always the time of its written part, and the hook's own appends never make an old written part look fresh. |
| PreCompact: what it could not do | Missing checkpoint, a file or directory it can't write, a directory in its place: exit 0, nothing created, nothing changed, and the checkpoint's relative path in a message (the JSON `systemMessage`, which the user sees; stderr is accepted too). A missing checkpoint is not created: a file with a block and no written part would pass for a checkpoint. |
| SessionStart answer | Exit 0. The injection is `hookSpecificOutput.additionalContext` of a JSON object on stdout (recommended), or plain stdout. Every string stays at or under 10,000 characters. |
| SessionStart in the main tree (DEC-263) | The path `governance/project/prompts/w1-orchestrator.md`, the orchestrator checkpoint's path, the whole RESUME HERE section, and an instruction that contains the words "read" and "now". Nothing about a ticket lead or appendix A5. |
| SessionStart in a worktree (DEC-263) | The sentence "You are the ticket lead for `<GOV_TICKET>`; read appendix A5 of governance/project/prompts/w1-orchestrator.md and your checkpoint .gov-runtime/scratch/lead/CHECKPOINT.md now", then the lead checkpoint's whole RESUME HERE section. The tests look for `ticket lead for <ticket>`, `appendix A5`, both paths, "read" and "now" (case of letters ignored for the first two). Nothing of the orchestrator's checkpoint, not even its path. The ticket comes from `GOV_TICKET` only; when it is unset the sentence still says "ticket lead" and names `GOV_TICKET` as not set (for example "for this worktree's ticket (GOV_TICKET is not set)"). |
| SessionStart: the warning (DEC-264, DP-4) | When the checkpoint holds a block and the file's modification time is earlier than the block's `generated:` time, the injection carries the phrase `CHECKPOINT OLDER THAN STATE BLOCK`, the checkpoint's path, and an instruction with the words `re-derive`, `git`, `tickets` and `before acting` ("Re-derive state from git and the tickets before acting."). On every source, in both trees. No warning when there is no block, or when the written part was written after the block was generated. |
| SessionStart and the block | Nothing of the block is injected. The RESUME HERE section is taken from the written part only: when it is the file's last section it ends where the block begins; when the written part has no such section the block doesn't stand in for it. The warning tells the session that the block is at the end of the checkpoint file. |
| RESUME HERE section | The heading whose text begins with `RESUME HERE` (any level, more text may follow on the line) and everything up to the next heading of the same or a higher level, or the end of the written part. Sub-headings belong to it. A line inside a fenced code block (three backticks, with or without a language name) is not a heading: it neither starts the section nor ends it. |
| The cap | The injection is the instruction, the warning if there is one, and the section, inside 10,000 characters. The warning is a fixed short text and is never cut. A section too large is cut from its end, and the injection then contains the word `truncated` (say how much is shown and that the rest is in the checkpoint file). |
| SessionStart: what it could not do | A missing checkpoint: exit 0, inside the cap, no content demanded. A checkpoint it can't read, or a directory in its place: exit 0, and the injection still carries the prompt path, the checkpoint's path and the instruction. Input it can't read: any exit code but 2. |
| Auto-compact window | `"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "300000"` in the `env` key of `.claude/settings.json`: a string of digits, 270000 to 330000. |

The estimate is 120 LOC, 154 are used, and W1-29 replaces both files, so nothing beyond these tables is asked for
(DEC-135). A throwaway reference pair that satisfies every deterministic test took 159 lines together, blank lines included. The
settings file carries the held-out deny line: edit it by script, as W1-47 did, and show it to nobody. These tests
load it as JSON and read the `hooks` and `env` keys only; no assertion message carries more than one hook command or
one env value.

## 2. KPI lines, their tests and the red reason

Red, as observed on 2026-10-04 against the implementation as it stands at commit `748b19bc` (it follows DEC-258):
**30 failed, 53 passed** of the 83 deterministic tests, and **2 failed, 8 passed** of the 10 `local_only` tests
(one real session, run once).

| KPI line | Tests | Red reason observed |
|---|---|---|
| Success 1 [CAP-37.g]: PreCompact ensures the orchestrator's checkpoint is current, in a worktree the lead's. Under DEC-264 "ensures" is the appended state block. | `test_w1_49_registration.py`: hook file exists, PreCompact registered for `manual` and `auto` (green). `test_w1_49_precompact.py`: in a worktree the block is appended to the lead's checkpoint and holds the worktree's head; a worktree without a lead checkpoint is said so and nothing is written | Failed: "a manual compaction in a worktree: the hook ended with 2, not 0: … stderr='CHECKPOINT NOT CURRENT: .gov-runtime/scratch/lead/CHECKPOINT.md is missing or older than 30 minutes. Update it, then compact again.'". The second test is green already. |
| Success 5 [CAP-37.g], first half, and failure 1: the PreCompact hook never blocks; it appends the state block (DEC-264) | `test_w1_49_precompact.py`: no compaction is blocked (current, old, missing × manual, auto); the block is appended and the written part is unchanged and first (2); the block holds the git head, the tickets as `tk` gives them, the worktree list, a line for the pending owner decisions, and invents none *(DP-5)*; a second compaction replaces the block; the append leaves the modification time; marker text in the written part is not taken for the block; missing checkpoint (2), read-only checkpoint, directory in its place; without `tk` (2), without git | Failed, 18 of 23: "a manual compaction over a old checkpoint: the hook ended with 2, not 0: … stderr='CHECKPOINT NOT CURRENT: …'" (5 tests: every `manual` case over an old, a missing or a read-only checkpoint); "no generated state block was appended to CHECKPOINT.md: the file is unchanged" (12 tests); "the hook did not say it could not append to .gov-runtime/scratch/orchestrator/CHECKPOINT.md: exit=0 stdout='' stderr=''" (directory). Green already: the four cases that DEC-258 did not block, and the missing checkpoint on `auto`. |
| Success 5 [CAP-37.g], second half, and failure 2: the injection warns when the written part is older than the block, with the instruction to re-derive state | `test_w1_49_sessionstart.py`: the warning after a compaction over an old checkpoint; a second compaction does not make it look fresh; no warning when the written part was rewritten after the block; none without a block; a checkpoint written minutes before the compaction is warned about *(DP-4)*; in a worktree the warning is about the lead's; the block is not injected as the end of the section, nor instead of a missing section; markers quoted inside the section do not cut it; a section over the cap with the warning stays inside the cap | Failed, 9 of 10: "no generated state block was appended to CHECKPOINT.md: the file is unchanged" (the compaction step of each test). Green already: no warning without a block. |
| Success 6 [CAP-37.g]: the injection is role-specific (DEC-263) | `test_w1_49_sessionstart.py`: in the main tree the injection is the orchestrator's; in a worktree it tells the session it is the ticket lead (ticket, appendix A5, prompt path, lead checkpoint path, the lead's section, nothing of the orchestrator's); without `GOV_TICKET` it says so | Failed, 2 of 3: "the injection does not say `you are the ticket lead for LD-4242`: 'Read now, before anything else: .gov-runtime/scratch/lead/CHECKPOINT.md. …'"; "without GOV_TICKET the injection does not say it is a ticket lead whose GOV_TICKET is not set". The main-tree test is green already. |
| Success 2 [CAP-37.g]: SessionStart on compact, clear and resume injects, within the cap, the prompt path and RESUME HERE, with the instruction to read both now | `test_w1_49_registration.py`: SessionStart registered for the three sources. `test_w1_49_sessionstart.py`: paths + whole section + instruction + cap (compact, clear, resume); heading variant; lead's section in a worktree (3) | Green (batch 1; not touched). |
| Failure 3: injects more than the cap, or leaves out the prompt path or the section | `test_w1_49_sessionstart.py`: long checkpoint doesn't push the section out; a section over the cap is cut and said so; no RESUME HERE section still gives both paths; missing checkpoint (3); plain startup; unreadable input; a worktree without a lead checkpoint gets nothing of the orchestrator's; the three code-block tests of batch 2; a checkpoint that can't be read (directory, unreadable file) *(batch 3)* | Green: batches 1 and 2 are not touched, and the two batch 3 cases are green already. |
| Success 3: the threshold is about 300k tokens if it can be configured; a test proves whether it can | `test_w1_49_threshold.py` (3, one `local_only`). `test_w1_49_live_session.py`: `/autocompact` reports the window and its origin (`local_only`) | Green (not touched). |
| Success 4 [CAP-37.g], failure 4, and failure 1 in a real session: after a forced compaction the next action shows the tickets, the open owner decisions and the loop counts, without restating; the compaction over an old checkpoint is not blocked | `test_w1_49_live_session.py` (`local_only`): the forced compaction over a checkpoint three days old is not blocked and the hooks fired around it; it left the state block in the checkpoint; the reply names 2 tickets, 2 decisions, 2 loop counts | Failed, 2 of 9: "the forced compaction did not complete: 'Compaction blocked by PreCompact hook: […]: CHECKPOINT NOT CURRENT: … is missing or older than 30 minutes. Update it, then compact again.'; hook events [('SessionStart', 'startup'), ('SessionStart', 'resume'), ('PreCompact', 'manual'), ('SessionStart', 'resume'), ('SessionStart', 'resume')]"; "the real session's PreCompact hook appended no state block". The six reply tests are green although the compaction was blocked: each `--resume` call fires SessionStart with the source `resume`, and that injection carries the section (section 3, point 4). |
| Edge: the guard hooks stay registered | `test_w1_49_registration.py::test_the_guard_hooks_stay_registered` (7) | Green; must stay green. |
| DEC-259: worker sessions | `test_w1_49_precompact.py`: a worker's compaction is not blocked and appends nothing (3). `test_w1_49_sessionstart.py`: a worker is not given the lead's checkpoint (3) | Green already: DEC-259 is implemented, and a hook that writes nothing appends nothing. |

Covers: CAP-37.g is tested by every row marked [CAP-37.g].

Every test not touched in batch 3 stayed green: the 40 deterministic tests of batches 1 and 2 that were neither
rewritten nor removed, and 8 of the `local_only` tests.

The deterministic suite was checked for satisfiability against a throwaway reference pair of hooks kept outside the
repository: all 83 passed with it. Two changes to the reference were tried to see the tests bite: without setting
the modification time back, 9 tests failed; with the block left inside the section, 2 failed. The real-session test
was not run against the reference (it would have cost a second session). The reference was not committed and is not
the design; the engineer builds from section 1.

### 2.1 Batch 3 by name

**Rewritten after the implementation, reason "owner decision, DEC-264": 15 cases; removed: 2.** Each asserted a
blocked manual compaction, the 30-minute age, or `CHECKPOINT NOT CURRENT` as DEC-258 defined it.

| Before (batch 1) | What became of it |
|---|---|
| `test_a_current_orchestrator_checkpoint_lets_the_compaction_proceed` (2) | `test_no_compaction_is_blocked[current-manual]`, `[current-auto]` |
| `test_a_manual_compaction_is_blocked_while_the_checkpoint_is_not_current` (2) | Reversed: `test_no_compaction_is_blocked[old-manual]`, `[missing-manual]` |
| `test_a_checkpoint_that_is_not_current_is_said_so` (4) | `[stale-auto]` → `test_no_compaction_is_blocked[old-auto]`; `[missing-manual]`, `[missing-auto]` → `test_a_missing_checkpoint_is_said_so_and_none_is_created` (2); `[stale-manual]` removed: an old checkpoint is no longer "said so" by PreCompact, it gets the block |
| `test_in_a_worktree_the_leads_checkpoint_is_the_one_checked` | `test_in_a_worktree_the_block_is_appended_to_the_leads_checkpoint` |
| `test_in_a_worktree_a_current_lead_checkpoint_is_enough` | Removed: nothing remains of it once no age is measured |
| `test_a_worktree_without_a_lead_checkpoint_is_not_current` | `test_a_worktree_without_a_lead_checkpoint_is_said_so_and_nothing_is_written` |
| `test_an_automatic_compaction_is_not_blocked_and_the_session_is_told_afterwards` | `test_after_a_compaction_over_an_old_checkpoint_the_injection_warns` (in `test_w1_49_sessionstart.py`) |
| `test_after_a_compaction_over_a_current_checkpoint_the_session_is_not_warned` | `test_a_written_part_rewritten_after_the_block_is_not_warned_about` (in `test_w1_49_sessionstart.py`) |
| `test_a_workers_compaction_is_not_blocked_by_the_leads_checkpoint` (3) | `test_a_workers_compaction_is_not_blocked_and_appends_nothing` (3) |
| `test_the_forced_compaction_ran_and_the_hooks_fired_around_it` (`local_only`) | `test_the_forced_compaction_over_an_old_checkpoint_is_not_blocked`: the session's checkpoint is now three days old. The eight other tests of that session share the changed session and were not rewritten. |

**Added after the implementation, reason "owner decision": 30 cases.**

| File | Tests |
|---|---|
| `test_w1_49_precompact.py` (16) | `test_no_compaction_is_blocked[missing-auto]`; `test_the_state_block_is_appended_and_the_written_part_is_unchanged_and_first` (2); `test_the_state_block_holds_the_git_head`; `test_the_state_block_holds_the_tickets_in_progress_as_tk_gives_them`; `test_the_state_block_holds_the_worktree_list`; `test_the_state_block_has_a_line_for_the_pending_owner_decisions`; `test_the_state_block_does_not_invent_the_pending_owner_decisions`; `test_a_second_compaction_replaces_the_block`; `test_the_append_leaves_the_checkpoints_modification_time`; `test_the_marker_text_in_the_written_part_is_not_taken_for_the_block`; `test_a_read_only_checkpoint_is_left_as_it_is_and_said_so`; `test_a_directory_in_place_of_the_checkpoint_is_left_alone_and_said_so`; `test_without_tk_the_block_says_so_and_holds_the_rest` (2); `test_without_git_the_block_says_so_and_holds_the_rest` |
| `test_w1_49_sessionstart.py` (13) | `test_in_the_main_tree_the_injection_is_the_orchestrators`; `test_in_a_worktree_the_injection_tells_the_session_it_is_the_ticket_lead`; `test_in_a_worktree_without_gov_ticket_the_injection_says_the_ticket_is_not_set`; `test_a_second_compaction_does_not_make_an_old_written_part_look_fresh`; `test_a_checkpoint_without_a_state_block_is_not_warned_about`; `test_a_checkpoint_written_minutes_before_the_compaction_is_warned_about`; `test_in_a_worktree_the_warning_is_about_the_leads_checkpoint`; `test_the_state_block_is_not_injected_as_the_end_of_the_resume_here_section`; `test_the_state_block_is_not_injected_instead_of_a_missing_resume_here_section`; `test_the_markers_quoted_inside_the_section_do_not_cut_it`; `test_a_section_over_the_cap_with_the_warning_stays_inside_the_cap`; `test_a_checkpoint_that_cannot_be_read_does_not_fail_the_hook` (2) |
| `test_w1_49_live_session.py` (1, `local_only`) | `test_the_forced_compaction_left_the_state_block_in_the_checkpoint` |

Of the 43 deterministic cases rewritten or added, 30 are red and 13 are green already, because the implementation
does that much today: `test_no_compaction_is_blocked` for `current-manual`, `current-auto`, `old-auto` and
`missing-auto`; `test_a_missing_checkpoint_is_said_so_and_none_is_created[auto]`;
`test_a_worktree_without_a_lead_checkpoint_is_said_so_and_nothing_is_written`;
`test_a_workers_compaction_is_not_blocked_and_appends_nothing` (3);
`test_in_the_main_tree_the_injection_is_the_orchestrators`;
`test_a_checkpoint_without_a_state_block_is_not_warned_about`;
`test_a_checkpoint_that_cannot_be_read_does_not_fail_the_hook` (2). They are there to stay green.

### 2.2 The earlier red records

- Batch 1, before the implementation, 2026-10-04: 9 failed, 8 passed, 45 errors (the hooks did not exist and were
  not registered).
- Batch 2, against the implementation of commit `9274e678`, 2026-10-04: 3 failed, 53 passed. The three code-block
  tests: "the injection leaves out 4 line(s) of the RESUME HERE section, first: '# FENCED-COMMENT-MARKER …'" and two
  like it.

## 3. Facts settled for Claude Code 2.1.288, and where each comes from

"Docs" is the hooks reference, the environment variables page and the model configuration page at
`code.claude.com/docs/en/` (`hooks`, `env-vars`, `model-config`), read on 2026-10-04. "Tried" is a short headless
session in a temporary directory with the pinned CLI at `~/.local/bin/claude` on 2026-10-04.

### Point 1: what a PreCompact hook can do

| Fact | Source |
|---|---|
| It gets `trigger` (`manual` for `/compact`, `auto` when Claude Code compacts by itself) and `custom_instructions`; the matcher filters on the trigger. | Docs. `manual` tried. `auto` was not tried (it needs at least 100,000 tokens of context). |
| Exit code 2 blocks the compaction; stderr is shown to the user as the reason. Tried: the result of `claude -p "/compact"` was "Compaction blocked by PreCompact hook: […]: <stderr>", and neither SessionStart nor PostCompact fired. A JSON `{"decision": "block", "reason": …}` does the same. | Docs and tried. |
| On exit 0, plain stdout goes to the debug log only. It reaches neither the user nor the model. A JSON `systemMessage` is shown to the user. | Docs. |
| It has no way to put text into the model's context and can't make the model write anything. It can read files, compare times, write a file of its own and block. | Docs (no `additionalContext` for this event). |
| After a compaction that isn't blocked, SessionStart fires with the source `compact`, then PostCompact. | Tried (order seen: PreCompact, SessionStart(compact), PostCompact). |
| A hook's own failure (any exit code other than 0 and 2) is a non-blocking error. | Docs. |

So a hook can **check** the checkpoint, **write** to it and **refuse** the compaction; it can't make the model
write anything. DEC-264 settles what it does: it never refuses, and it appends state it can generate itself.

| Fact (batch 3) | Source |
|---|---|
| A PreCompact hook that ends with 2 over a checkpoint three days old stops `claude -p "/compact" --resume <id>`: the result is "Compaction blocked by PreCompact hook: […]", and neither SessionStart(compact) nor PostCompact fires. This is what DEC-264 removes. | Tried on 2026-10-04 with the implementation of commit `748b19bc`. |
| A file's modification time can be set back after a write (`os.utime`), so an append need not change it. | Python's standard library; tried with the throwaway reference. |
| `tk ls --status=in_progress` prints one line for each ticket in progress (`<id> [in_progress] - <title> <- [<deps>]`) and reads `.tickets/` of the tree it runs in. In a linked worktree `.git` is a file; in the main tree it is a directory. | `tk --help` and tried in this repository; git's worktree layout. |

### Point 2: the SessionStart size cap

| Fact | Source |
|---|---|
| The cap is 10,000 characters for each of `additionalContext`, `systemMessage`, `initialUserMessage` and plain stdout, each measured on its own. No setting or environment variable raises it. | Docs ("Add context for Claude"). |
| Over the cap, Claude Code saves the text to a file in the session directory and puts the file path and a preview of the first 2,000 characters in its place; nobody tells the model to read the file. Tried with 12,000 characters: the model saw "Output too large (11.8KB). Full output saved to: …additionalContext.txt  Preview (first 2KB):" and not the end of the text. | Docs and tried. |
| SessionStart can't block. `additionalContext` and plain stdout are honoured on every exit code; on exit 2 stderr is shown to the user only. | Docs. |
| The sources are `startup`, `resume` (`--resume`, `--continue`, `/resume`), `clear`, `compact`, `fork`. `startup`, `resume` and `compact` tried. | Docs and tried. |
| A context injected at SessionStart(compact) is in the model's context on the next turn. | Tried. |

The Contract's envelope ("SessionStart injection ≤ ~2.5k tokens plus a file path") is about the same size, so one
number serves both. The tests assert 10,000 characters.

### Point 3: the auto-compact threshold can be configured

| Fact | Source |
|---|---|
| The auto-compact window is set in tokens, 100,000 to 1,000,000, by the `autoCompactWindow` settings key, the `--autocompact` flag, `/autocompact`, or the environment variable `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, which wins over the other three. It is capped at the model's context window. | Docs; `claude --help` lists `--autocompact`. |
| The variable takes a plain integer only: `300k` reads as 300 and clamps to the 100K minimum. | Docs. |
| Set in the `env` key of a project's `.claude/settings.json`, the variable reaches the session: `/autocompact` answered "Auto-compact window for Haiku 4.5: 300k tokens (from CLAUDE_CODE_AUTO_COMPACT_WINDOW) · capped to 200k by model", and the session's hooks saw the variable. | Tried. |
| Compaction fires a little below the window (the window minus a summary buffer). | The CLI's own schema text; not measured. |

DEC-248 allows the ticket "hook registration and any env key" in the settings file, so the env key is the form the
tests assert, not the top-level `autoCompactWindow` key. **No residual goes to `bootstrap.md` for KPI line 3: the
`CONTEXT_CHECKPOINT` stop can go when the ticket closes (DEC-250).** Not proved here: that a compaction really starts
near 300k tokens on a 1M model. That needs a session of 300k tokens; the tests prove the key is read and reported.
The key applies to every session in the repository; on a 200k model it is capped by the model and changes nothing.

### Point 4: a forced compaction works in a headless session

`claude -p "/compact" --resume <session id>` compacts the resumed session, costs no model turn of its own beyond the
summary, and fires PreCompact (`manual`), SessionStart (`compact`) and PostCompact. Tried. No package is needed. The
real-session test uses it: four calls on one session, model `haiku`, a turn limit on each, about 0.10 USD a run.
Every `--resume` call also fires SessionStart with the source `resume` (seen in batch 3), so the question call gets
the injection even when the compaction before it did not run; the test that proves the compaction is the first one
of the file, not the reply tests.
The question call has the Read tool only (`--tools Read`); with every tool available the model started the next
action instead of stating it and ran into the turn limit (seen twice).

## 4. Which tests stand on a recommendation, not on a settled fact

| Package | State | Tests that stand on it |
|---|---|---|
| DP-1 | Answered: DEC-258, then amended by the owner's DEC-264 (no compaction is blocked; the state block and the warning) | The tests of DP-1 (a) were rewritten or removed in batch 3 (section 2.1). |
| DP-2 | Answered: DEC-259, option (a) | `test_a_workers_compaction_is_not_blocked_and_appends_nothing` (3), `test_a_worker_session_is_not_given_the_leads_checkpoint` (3); every other hook test and the real session run with `GOV_ROLE=orchestrator`. They stand on a decision now. |
| DP-3 | Answered: DEC-263, the owner chose the role-specific injection | The three DEC-263 tests. They stand on a decision. |
| DP-4 (a) | **Open** | `test_a_checkpoint_written_minutes_before_the_compaction_is_warned_about`, and the README's rule that the hook sets the modification time back (`test_the_append_leaves_the_checkpoints_modification_time`). Under option (b) the first is reversed and the second stays. |
| DP-5 (a) | **Open** | `test_the_state_block_does_not_invent_the_pending_owner_decisions`. Under option (b) or (c) it is rewritten. |

Every other test follows from a KPI line, a decision or a settled fact. The warning fixtures were chosen so that
they hold under both options of DP-4: the old checkpoint is three days old, older than the last commit (an hour
ago) and than the block; the rewritten one is written after the block and after the last commit; one checkpoint has
no block.

## 5. Decision packages

DP-1, DP-2 and DP-3 are answered and kept here for the record. DP-4 and DP-5 are new and open.

### DP-4: what "the written part is older than the block" is measured against

- **Question.** DEC-264: the injection "warns when the checkpoint's written part is older than that block". The
  block is generated at the compaction, so a written part is always older than it, by three days or by three
  seconds. Is any age a reason to warn, or only an age that means the session's state moved on after it wrote?
- **Why now.** The engineer builds one comparison or the other, and one test differs.
- **Options.**
  - (a) **The times as they are.** Warn when the written part's time is earlier than the block's `generated:`
    time. After a compaction the warning is therefore always there (the session is always told to re-derive state
    from git and the tickets before acting), and it goes away once the session rewrites its checkpoint. On a later
    `clear` or `resume` it says whether the checkpoint was rewritten since the last compaction. One comparison, no
    git call, no threshold to choose.
  - (b) **Older than the state the block records.** Warn when the written part's time is earlier than the HEAD
    commit's time the block records (the block gets one more line for it). A checkpoint written after the last
    commit gets no warning. It misses what leaves no commit: an owner decision, a loop count, a ticket started and
    not yet committed.
  - (c) **A tolerance** (older by more than N minutes). This is the 30-minute rule of DEC-258 again, which DEC-264
    removed.
- **Impact.** (a): the tests stand as written. (b): `test_a_checkpoint_written_minutes_before_the_compaction_is_warned_about`
  is reversed (no warning), the block's layout gets a commit-time line, and one test is added for it. (c): the same
  one test is reversed and a threshold test is added. The other nine warning tests hold under (a) and (b).
- **Reversibility.** High: one comparison in a hook that W1-29 replaces.
- **Cost.** (a) about 4 lines; (b) about 8 and a git call more; (c) about 5 and a number to defend.
- **Recommendation.** (a). It is what the decision's words say, it is the simplest, and a warning that is always
  there after a compaction asks for something cheap and safe: look at git and the tickets before acting.
- **Confidence.** Medium. The words "warns when" suggest the owner expects compactions without a warning, which is
  (b); (a) gives none unless the checkpoint is rewritten in the same second.

### DP-5: where the block's "pending owner decisions" come from

- **Question.** DEC-264 lists four things the block holds. Three come from commands. The fourth, the pending owner
  decisions, is known to the model, and no source a command could read was found: `tk` has no field for them, and the
  orchestrator prompt gives the checkpoint no fixed place for them.
- **Why now.** The hook must write something under that name, and it must not invent state.
- **Options.**
  - (a) **The hook says it doesn't know.** The line reads `pending owner decisions: not known to the hook; see the
    written part of this checkpoint`. Nothing is copied.
  - (b) **The hook copies from the written part** every line that mentions an owner decision (for example the
    lines of the RESUME HERE section that contain "owner decision"). The block then repeats, under the name of
    generated state, text that is exactly as old as the written part: on the day the warning matters it is the stale
    text. It also needs a rule for what such a line looks like, and no document gives one.
  - (c) **A file the orchestrator keeps** (for example `.gov-runtime/scratch/orchestrator/PENDING_DECISIONS.md`),
    which the hook copies. A real source, and a new duty for the orchestrator and a change to its prompt, which only
    the owner changes.
- **Impact.** (a): the tests stand. (b) or (c): `test_the_state_block_does_not_invent_the_pending_owner_decisions`
  is rewritten to assert the copied lines; (c) adds a fixture file and a missing-file case.
- **Reversibility.** High.
- **Cost.** (a) one line; (b) about 5; (c) about 5, and the prompt change.
- **Recommendation.** (a) now; (c) when W1-29 builds the full context packet, if the owner wants the decisions in
  the block.
- **Confidence.** Medium-high that (b) is wrong; medium on (a) against (c), because (a) reads DEC-264's "holds the
  pending owner decisions" as "has their line".

### DP-1: what "ensures the checkpoint is current" means for a hook (answered: DEC-258, amended by DEC-264)

- **Question.** KPI success 1 says the PreCompact hook "ensures" the checkpoint is current. A hook can check and can
  block; it can't write the checkpoint's content (section 3, point 1). What does it do when the checkpoint is not
  current, and what is "current" measured against?
- **Options, as put in batch 1.** (a) Block a manual compaction, let an automatic one through and say so; current
  means at most 30 minutes old. (b) Block every compaction. (c) Never block, only say so. (d) The hook writes into
  the checkpoint itself.
- **Answer.** DEC-258 took (a). The owner then amended it with DEC-264: never block, and the hook appends a
  generated state block (the useful half of (d): generated state, kept apart from the written part, with a warning
  when the written part is older).

### DP-2: which sessions the hooks act for (answered: DEC-259)

- **Question.** The registration is in the repository's settings, so the hooks run in every session, including the
  workers that share a lead's worktree. Should a worker session be given the lead's RESUME HERE section?
- **Answer.** DEC-259, option (a): the hooks act only when `GOV_ROLE` is `orchestrator`; an unset `GOV_ROLE` is not
  the orchestrator. The lead's checkpoint holds the loop count, which no session inside the loop may see.

### DP-3: the prompt path of a ticket lead (answered: DEC-263)

- **Question.** KPI success 2 asks for "the prompt path". No document named a prompt file for a lead.
- **Answer.** DEC-263, by the owner: the injection is role-specific. In a worktree it tells the session it is the
  ticket lead for its ticket and sends it to appendix A5 of the orchestrator prompt and to its checkpoint.

## 6. Edge behaviours, decided or left

| Edge | Decided as | Tested |
|---|---|---|
| Checkpoint with no RESUME HERE section | SessionStart still gives both paths and the instruction, exit 0; the block does not stand in for the section. PreCompact appends the block all the same. | Yes |
| A fenced code block inside the RESUME HERE section, with a line that starts with `# ` or `## ` | The line is not a heading. The block and what follows it in the section are injected; the section ends at the next real heading. | Yes |
| A fenced code block before the section that shows a `## RESUME HERE` line (an example or a template) | Not the section. The real section is injected, the example's text is not. | Yes |
| Fences of tildes, indented code blocks, an unclosed fence, a heading-like line in a code block after the section | Not specified. | No |
| The markers quoted in the written part: in a sentence, or as whole lines in a code block | Written text. Never replaced, never cut, and the section that holds them is injected whole. | Yes |
| A written part whose very last lines are both markers, as whole lines, with nothing after them | It can't be told from a generated block and is replaced at the next compaction. Close the code block after it, or write a line after it. | No |
| RESUME HERE as the last section of the file | It ends where the generated block begins. | Yes |
| The session rewrites the whole file (the block is gone) | No block, no warning; the next compaction appends a new one. | Yes (no block) |
| `tk` gives no ticket in progress | The label's line and nothing under it, or `none`. | No |
| `tk` or git not on `PATH`, failing or slow | Exit 0; the block is appended; the label's line says `unavailable`. Give each command a timeout of a few seconds. | Yes (absent, failing); the timeout no |
| Missing checkpoint | PreCompact: exit 0, says so with the path, creates nothing. SessionStart: exit 0, inside the cap, no content demanded. | Yes |
| Read-only checkpoint, or a directory in its place | PreCompact: exit 0, nothing changed, says so with the path. SessionStart: exit 0, both paths and the instruction. | Yes |
| Worktree with a lead checkpoint | The lead's gets the block and is injected, never the orchestrator's. | Yes |
| Worktree without one | PreCompact: exit 0, says so, writes nothing. SessionStart: exit 0, nothing of the orchestrator's. | Yes |
| `GOV_TICKET` unset in a worktree | The injection says it is a ticket lead and that `GOV_TICKET` is not set. The hook does not guess the ticket from the branch. | Yes |
| `GOV_TICKET` set in the main tree | Ignored: the tree decides, not the variable. | No |
| A hook that fails | SessionStart can't block a session in 2.1.288, whatever its exit code. Neither hook answers 2 on input it can't read. | Yes (unreadable stdin) |
| Two compactions at the same moment in one tree | Not specified. | No |
| The guard hooks | Stay registered. Their files are not compared with an earlier version here; W1-05's suite runs them. | Registration: yes |
| The kernel template's `settings.json` | Outside this ticket's paths; W1-29's business. | No |
| `fork` and `startup` sources | Not required. `startup` must not fail if registered. | `startup`: yes |
| A main tree that is not a git repository | The block's git lines say `unavailable` (as for a failing git). | Failing git: yes |

## 7. What the tests never touch

No test opens a real checkpoint: every checkpoint is a stand-in with invented tickets (`ZQ-…`, `LD-…`), invented
owner decisions (`OD-…`) and invented loop counts, in a temporary git repository. No test calls the real `tk`: a
stand-in is first on the hook's `PATH` and prints invented tickets in progress (`GEN-…`); the tests that take it
away use a `PATH` without it or a stand-in that fails. The worktree list is that of the temporary repository. No file
of this suite reads the held-out list or carries one of its values, and the temporary settings of the real session
are built from the `hooks` and `env` values only.
