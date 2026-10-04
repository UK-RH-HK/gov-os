# W1-49 acceptance tests: light auto-resume hooks

Ticket `DAEO-32n6` (W1-49), profile FULL, covers item CAP-37.g. Written by the Independent Test Designer before the
implementation (MR-3, DEC-069), from the ticket's KPI lines, CAP-37 and DEC-248, DEC-208, DEC-237, DEC-250.

Run: `python3 -m pytest tests/acceptance/W1-49 -q -p no:cacheprovider`
Without the real session and the CLI: add `-m "not local_only"`.

62 tests: 53 deterministic with no network, 9 marked `local_only` (8 share one real session, 1 runs
`claude --help`).

## 1. What the engineer builds (the interface these tests fix)

| What | Fixed by these tests |
|---|---|
| Hook files | `template/governance/kernel/hooks/precompact.py` and `template/governance/kernel/hooks/sessionstart.py` |
| Registration | In the `hooks` key of `.claude/settings.json`: `PreCompact` for the triggers `manual` and `auto` (no matcher does it); `SessionStart` for the sources `compact`, `clear` and `resume`. Each command finds its file through `$CLAUDE_PROJECT_DIR`, as the guard hooks do. `startup` is neither required nor forbidden. |
| Input | The hook event's JSON object on stdin: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, and `trigger` + `custom_instructions` (PreCompact) or `source` + `model` (SessionStart). `CLAUDE_PROJECT_DIR` and `GOV_ROLE` in the environment. |
| Which checkpoint | In the main tree `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`; in a linked git worktree `.gov-runtime/scratch/lead/CHECKPOINT.md` of that worktree. A worktree session never gets the main tree's checkpoint. |
| PreCompact answer | Checkpoint current: exit 0 and no warning. Not current (stale or missing): the phrase `CHECKPOINT NOT CURRENT` and the checkpoint's relative path, on stderr or in the JSON `systemMessage`. On DP-1's recommendation: exit 2 with that text on stderr for `manual`; exit 0 for `auto`. Input it can't read: any exit code but 2. |
| SessionStart answer | Exit 0. The injection is `hookSpecificOutput.additionalContext` of a JSON object on stdout (recommended), or plain stdout. It carries the path `governance/project/prompts/w1-orchestrator.md`, the checkpoint's path, the whole RESUME HERE section, and an instruction that contains the words "read" and "now". Every string stays at or under 10,000 characters. A section too large for that is cut from its end, and the injection then contains the word `truncated` (say how much is shown and that the rest is in the checkpoint file). After a compaction over a checkpoint that is not current it carries `CHECKPOINT NOT CURRENT` and the path (DP-1). |
| RESUME HERE section | The heading whose text begins with `RESUME HERE` (any level, more text may follow on the line) and everything up to the next heading of the same or a higher level, or the end of the file. Sub-headings belong to it. |
| Roles | With `GOV_ROLE=orchestrator` the hooks act. With a worker role (`engineer`, `independent-test-designer`, `independent-auditor`) PreCompact never blocks and SessionStart injects nothing of a checkpoint (DP-2). |
| Auto-compact window | `"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "300000"` in the `env` key of `.claude/settings.json`: a string of digits, 270000 to 330000. |

The estimate is 120 LOC and W1-29 replaces both files, so nothing beyond this table is asked for (DEC-135). The
settings file carries the held-out deny line: edit it by script, as W1-47 did, and show it to nobody. These tests
load it as JSON and read the `hooks` and `env` keys only; no assertion message carries more than one hook command or
one env value.

## 2. KPI lines, their tests and the red reason

Red, as observed on 2026-10-04 before the implementation: **9 failed, 8 passed, 45 errors**.

| KPI line | Tests | Red reason observed |
|---|---|---|
| Success 1 [CAP-37.g]: PreCompact ensures the orchestrator's checkpoint is current, in a worktree the lead's | `test_w1_49_registration.py`: hook file exists, PreCompact registered for `manual` and `auto`. `test_w1_49_precompact.py`: current checkpoint lets it proceed (2), in a worktree the lead's is checked, a current lead checkpoint is enough, a worktree without one is not current | Failed: "the hook template/governance/kernel/hooks/precompact.py does not exist yet", ".claude/settings.json registers no PreCompact hook that runs … for a manual compaction". Behaviour tests error in the fixture with the first of these. |
| Failure 1: a compaction proceeds while the checkpoint is not current, and nothing says so | `test_w1_49_precompact.py`: not current is said so (stale, missing × manual, auto); manual is blocked (stale, missing) *(DP-1)*; auto isn't blocked and the session is told afterwards *(DP-1)*; no warning after a compaction over a current checkpoint *(DP-1)* | Error in the fixture: the PreCompact hook does not exist yet. |
| Success 2 [CAP-37.g]: SessionStart on compact, clear and resume injects, within the cap, the prompt path and RESUME HERE, with the instruction to read both now | `test_w1_49_registration.py`: SessionStart registered for the three sources. `test_w1_49_sessionstart.py`: paths + whole section + instruction + cap (compact, clear, resume); heading variant; lead's section in a worktree (3) | Failed: ".claude/settings.json registers no SessionStart hook that runs … for the source compact". Behaviour tests error: "the hook …/precompact.py does not exist yet" or "…/sessionstart.py does not exist yet". |
| Failure 2: injects more than the cap, or leaves out the prompt path or the section | `test_w1_49_sessionstart.py`: long checkpoint doesn't push the section out; a section over the cap is cut and said so; no RESUME HERE section still gives both paths; missing checkpoint (3); plain startup; unreadable input; a worktree without a lead checkpoint gets nothing of the orchestrator's | Error in the fixture, as above. |
| Success 3: the threshold is about 300k tokens if it can be configured; a test proves whether it can | `test_w1_49_threshold.py`: env key present as a plain integer; value about 300k; the pinned CLI has `--autocompact` (`local_only`, green already). `test_w1_49_live_session.py`: `/autocompact` reports the window and its origin (`local_only`) | Failed: "the env key of .claude/settings.json does not set CLAUDE_CODE_AUTO_COMPACT_WINDOW". The live test errors in the fixture. |
| Success 4 [CAP-37.g] and failure 3: after a forced compaction the next action shows the tickets, the open owner decisions and the loop counts, without restating | `test_w1_49_live_session.py` (`local_only`): the compaction ran and the hooks fired around it; the reply names 2 tickets, 2 decisions, 2 loop counts | Error in the fixture before any session starts: the hooks are not registered. |
| Edge: the guard hooks stay registered | `test_w1_49_registration.py::test_the_guard_hooks_stay_registered` (7) | Green before the implementation; must stay green. |
| DP-2: worker sessions | `test_w1_49_precompact.py` (3), `test_w1_49_sessionstart.py` (3) | Error in the fixture. |

Covers: CAP-37.g is tested by every row marked [CAP-37.g].

The 8 tests green before the implementation are the 7 guard-registration checks and the `--autocompact` help check;
they are there to stay green.

The suite was checked for satisfiability against a throwaway reference pair of hooks kept outside the repository:
all 37 hook-behaviour tests and all 8 real-session tests passed with it. The reference was not committed and is
not the design; the engineer builds from section 1.

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

So a hook can **check** that the checkpoint is current and can **refuse** the compaction; it can't **make** it
current. What "current" is measured against is not in the specification: that is DP-1.

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
The question call has the Read tool only (`--tools Read`); with every tool available the model started the next
action instead of stating it and ran into the turn limit (seen twice).

## 4. Which tests stand on a recommendation, not on a settled fact

| Package | Tests that stand on its recommendation |
|---|---|
| DP-1 (a) | `test_a_manual_compaction_is_blocked_while_the_checkpoint_is_not_current` (2), `test_an_automatic_compaction_is_not_blocked_and_the_session_is_told_afterwards`, `test_after_a_compaction_over_a_current_checkpoint_the_session_is_not_warned` |
| DP-2 (a) | `test_a_workers_compaction_is_not_blocked_by_the_leads_checkpoint` (3), `test_a_worker_session_is_not_given_the_leads_checkpoint` (3); every other hook test and the real session run with `GOV_ROLE=orchestrator` |
| DP-3 (a) | None asserts it. The worktree tests assert the lead checkpoint's path and section and no prompt path. |

Every other test follows from a KPI line or a settled fact. The current and stale fixtures were chosen so that they
hold under any measure DP-1 could end in: the current checkpoint was written this minute, after the last commit (an
hour ago) and after the transcript's last write (ten minutes ago); the stale one is three days old.

## 5. Decision packages

### DP-1: what "ensures the checkpoint is current" means for a hook

- **Question.** KPI success 1 says the PreCompact hook "ensures" the checkpoint is current. A hook can check and can
  block; it can't write the checkpoint's content (section 3, point 1). What does it do when the checkpoint is not
  current, and what is "current" measured against?
- **Why now.** The engineer can't build the hook, and four tests can't be final, without it.
- **Options.**
  - (a) **Block a manual compaction, let an automatic one through and say so.** `manual`: exit 2, the reason on
    stderr, so whoever typed `/compact` has the session update the checkpoint and compacts again. `auto`: exit 0,
    the user is told (`systemMessage`), and the SessionStart injection after the compaction tells the model
    `CHECKPOINT NOT CURRENT` with the path. Current means: the file exists and was modified within the last 30
    minutes.
  - (b) **Block every compaction** while the checkpoint is not current. The strict reading of "ensures". An
    automatic compaction that is blocked reaches nobody who can act: the reason goes to the user's screen, not to
    the model, so an unattended orchestrator keeps growing past 300k with nothing changed. What Claude Code does
    after repeated blocked automatic compactions was not tried.
  - (c) **Never block, only say so**, for both triggers. The weakest reading; it satisfies failure line 1 as
    written ("and nothing says so") and nothing more.
  - (d) **The hook writes into the checkpoint itself** (a stamp with the time, the HEAD commit and the transcript
    path). It makes the file's time current without making its content current, and puts a hook's hand in the
    orchestrator's file.
  - Measure, for any of them: (i) a maximum age of the file (30 minutes recommended; the orchestrator writes it
    after every merge and close); (ii) not older than the last commit on HEAD; (iii) not older than the transcript
    (always false in practice without a tolerance). (i) is one comparison and needs no git call.
- **Impact.** (a): 4 tests stand as written. (b): `test_an_automatic_compaction_is_not_blocked…` is rewritten to
  expect exit 2. (c): the two `manual_compaction_is_blocked` tests are rewritten to expect exit 0. (d): new tests
  for the stamp. The tests in the first part of `test_w1_49_precompact.py` hold under all four.
- **Reversibility.** High: a few lines of one hook that W1-29 replaces anyway.
- **Cost.** (a) and (c) fit the 120 LOC estimate; (b) the same; (d) adds a write path and its failure cases.
- **Recommendation.** (a) with measure (i).
- **Confidence.** Medium-high on (a) against (b), (c) and (d). Medium on the measure and on 30 minutes: the
  orchestrator's real rhythm is the owner's to say. The automatic trigger was read from the documentation, not
  tried.

### DP-2: which sessions the hooks act for

- **Question.** The registration is in the repository's settings, so the hooks run in every session, including the
  workers that share a lead's worktree. Should a worker session be given the lead's RESUME HERE section, and be
  blocked by the lead's stale checkpoint?
- **Why now.** The WBS loop policy says the count is never disclosed to the sessions inside the loop, and the lead's
  checkpoint holds it. A worker that is resumed or compacted in the worktree would get it injected. The KPI lines
  don't speak of roles.
- **Options.**
  - (a) The hooks act only when `GOV_ROLE` is `orchestrator` (the main orchestrator and the leads). For any other
    role PreCompact exits 0 and SessionStart injects nothing of a checkpoint.
  - (b) The hooks act for every session.
  - (c) (a), and an unset `GOV_ROLE` also counts as the orchestrator.
- **Impact.** (a): 6 tests stand as written. (b): those 6 are deleted and the loop policy has a hole.
  (c): as (a); no test sets it apart, because no test runs with the variable unset.
- **Reversibility.** High.
- **Cost.** Two lines per hook.
- **Recommendation.** (a). The orchestrator should confirm that the main session and the leads do run with
  `GOV_ROLE=orchestrator`; if one of them runs with the variable unset, choose (c).
- **Confidence.** High that workers must be left out; medium on (a) against (c), because I could not see how the
  main session and the leads set the variable.

### DP-3: the prompt path of a ticket lead

- **Question.** KPI success 2 asks for "the prompt path". The orchestrator's is
  `governance/project/prompts/w1-orchestrator.md`. No document names a prompt file for a lead.
- **Why now.** In a worktree the hook has to inject something for "read both now".
- **Options.**
  - (a) In a worktree the injection carries the lead checkpoint's path and its RESUME HERE section; the lead's
    checkpoint names its own brief in that section. No prompt path of the hook's own.
  - (b) The same orchestrator prompt path in both trees.
  - (c) A fixed lead brief path that the orchestrator defines (for example under `.gov-runtime/scratch/lead/`).
- **Impact.** (a): no test changes. (b) or (c): one assertion is added to the worktree test.
- **Reversibility.** High.
- **Cost.** None to a few lines.
- **Recommendation.** (a) now; (c) when W1-29 builds the full packet.
- **Confidence.** Medium.

## 6. Edge behaviours, decided or left

| Edge | Decided as | Tested |
|---|---|---|
| Checkpoint with no RESUME HERE section | SessionStart still gives both paths and the instruction, exit 0. Whether PreCompact calls such a file "not current" is left to the engineer. | SessionStart: yes. PreCompact: no. |
| Missing checkpoint | PreCompact: not current. SessionStart: exit 0, inside the cap, no content demanded. | Yes |
| Worktree with a lead checkpoint | The lead's is checked and injected, never the orchestrator's. | Yes |
| Worktree without one | PreCompact: not current. SessionStart: exit 0, nothing of the orchestrator's. | Yes |
| A hook that fails | SessionStart can't block a session in 2.1.288, whatever its exit code. PreCompact must not answer 2 on input it can't read. | Yes (unreadable stdin) |
| The guard hooks | Stay registered. Their files are not compared with an earlier version here; W1-05's suite runs them. | Registration: yes |
| The kernel template's `settings.json` | Outside this ticket's paths; W1-29's business. | No |
| `fork` and `startup` sources | Not required. `startup` must not fail if registered. | `startup`: yes |
| A main tree that is not a git repository | Not specified. | No |

## 7. What the tests never touch

No test opens a real checkpoint: every checkpoint is a stand-in with invented tickets (`ZQ-…`, `LD-…`), invented
owner decisions (`OD-…`) and invented loop counts, in a temporary git repository. No file of this suite reads the
held-out list or carries one of its values, and the temporary settings of the real session are built from the
`hooks` and `env` values only.
