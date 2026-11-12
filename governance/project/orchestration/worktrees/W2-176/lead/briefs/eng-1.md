# W2-176 (DAEO-ktiw), engineer, run 1: context awareness before compaction

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** engineer. **Worktree:** `/home/usain/gov-os-worktrees/W2-176`, branch `w2/W2-176`, base head `1798e82f1201`
(tree clean). **Ticket:** `DAEO-ktiw` (W2-176), profile STANDARD, class C3. Your scratch:
`/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/engineer/`.

## The spec
Read `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ktiw.md`: its KPIs S1, S2, S3, F1 and F2 are your spec
(S4, the CIT-P record, is the lead's; do not write `docs/changes/W2-176-CIT-P.md`). The governed context packet (the
ticket and its mandatory inputs DEC-1140, DEC-838, DEC-901, DEC-445, DEC-208, DEC-250) is at
`/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/lead/briefs/eng-context.md`. Read decisions by id in
`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (grep by id only). Search with Read and Grep;
search again once in different words if the first does not answer.

**Allowed paths (nothing else):** `template/governance/kernel/hooks/precompact.py`,
`template/governance/kernel/hooks/context_watch.py` (new), `tests/unit/hooks/test_w2_176_precompact.py`,
`tests/unit/hooks/test_w2_176_context_watch.py`. Never touch `.claude/`, any settings file, `sessionstart.py` or
another hook (non-goals; the registration in `.claude/settings.json` is the CTO's ACT after the owner's approval).

## Facts the lead checked (official docs, code.claude.com/docs/en/hooks, CLI 2.1.322)
- **PreCompact:** input = the common fields (`session_id`, `transcript_path`, `cwd`, `hook_event_name`) plus `trigger`
  (`manual`|`auto`) and `custom_instructions` (null for auto). "When a PreCompact hook exits 0 and doesn't block,
  Claude Code uses its stdout as instructions for the compaction summary" (cap 10,000 chars). "Claude Code discards a
  PreCompact hook's `systemMessage` and `continue` fields." A `"decision": "block"` or exit 2 blocks compaction:
  never produce either (F1).
- **PostToolUse:** input = the common fields plus `tool_name`, `tool_input`, `tool_response`, `tool_use_id`,
  `duration_ms`. **No `model` field** in any hook input except SessionStart: take the model from the transcript.
  Context is added with exactly
  `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "<text>"}}` (one JSON object on stdout).
- **Transcript (JSONL)**, checked on a live transcript: an assistant line has `"type": "assistant"`, `"isSidechain"`
  (skip `true` lines: a subagent's), `"sessionId"`, and `message.model` (e.g. `claude-opus-5-5`) and `message.usage`
  with `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`. Context used =
  input + cache_creation + cache_read. The last line may be partial (written asynchronously): skip what does not parse.
- **Windows** (code.claude.com/docs/en/model-config): Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable models run with the
  1M window by default. Table: `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5-2`:
  1,000,000 (a `[1m]` suffix or date suffix matches its base); anything else: 200,000. Let a test plant the table
  (e.g. a module-level dict the test can patch, or an env-free argument), so 50/84/85/99 % cases need no 850k-token
  file. Never read or set `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `--autocompact` or any threshold (F1, DEC-838 (1)); the
  source must not contain those strings.

## What to build
1. **precompact.py** (base sha256 `eb0174da477ff6f4eab7ca5bb133c667079830aa5c5c64f8f8d8337ad8c95086`): on every run,
   for every role, print one plain-text line on stdout telling the compaction summary to begin with `READ FIRST:` and:
   - GOV_ROLE `orchestrator`: the checkpoint path `checkpoint_rel(project_root)` already gives (main tree:
     `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`; linked worktree: `.gov-runtime/scratch/lead/CHECKPOINT.md`),
     absolute, with "its RESUME HERE section".
   - any other role: `READ FIRST: your brief and your record`, with their paths: the brief under
     `<root>/.gov-runtime/scratch/brief/` (launch_worker.sh copies it there) and the record under
     `<root>/.gov-runtime/scratch/checkpoints/<GOV_TICKET>/` (the automatic record this hook writes, DEC-444); name the
     newest file in each when there is one, else the folder.
   Keep the checkpoint writing, the state block and the systemMessage on error unchanged. **Keep the names `STAMP`,
   `checkpoint_rel` and `split`: `sessionstart.py` imports them.** On error the systemMessage JSON and the read-first
   line both go out; decide the order so the read-first line still reaches the summary, and say why in a comment
   (the W1-49 helper `HookRun.said` reads plain stdout as text when it is not one JSON object). The line is written
   even when the checkpoint write fails; the hook still always exits 0.
2. **context_watch.py** (new, PostToolUse): S2 and S3 exactly. Read only the transcript's last 256 KiB (seek); find
   the last non-sidechain assistant line with usage; ratio = used / window(model); at >= 0.85 and no state file for
   this `session_id`, print the additionalContext once and create the state file under
   `<project root>/.gov-runtime/scratch/context_watch/` (project root: `CLAUDE_PROJECT_DIR`, else the input's `cwd`;
   a safe file name from the session id). The text: write your checkpoint now; update every file that needs it, by
   role (orchestrator in the main tree, the CTO: RESUME HERE, DECIDED-NOT-DONE, report-state; orchestrator in a linked
   worktree, a lead: its CHECKPOINT; anyone else, a worker: its record); begin the compaction summary with the
   read-first line; and one sentence that this is a handover aid, not a stop and not an early compaction (DEC-838 (2),
   DEC-901's precedent). Any error (no transcript, unreadable usage, malformed line, empty or non-PostToolUse event):
   print nothing, exit 0. No decision field ever; no write outside that state folder.

## Tests first (test-driven: red, then green)
Write `tests/unit/hooks/test_w2_176_precompact.py` and `tests/unit/hooks/test_w2_176_context_watch.py` covering every
Verify column of S1, S2, S3 and F1, run as subprocesses fed planted events (look at `tests/unit/hooks/test_w29_hooks.py`
and `tests/acceptance/W1-49/w1_49_support.py` for the house form): trigger auto and manual, orchestrator (main and
linked tree) and engineer; 50/84/85/99 % planted windows; once per session; an Opus 5.5 transcript uses 1,000,000;
a 50 MB planted transcript under 100 ms (median of 5; build the file in tmp_path, not in the repo); missing path,
malformed last line, empty event → exit 0 and no stdout; no `decision` key in any parsed output; the sources contain
no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` / `autocompact`; a write-tracing run (e.g. snapshot the planted project tree
before and after) lists only the scratch state file. Commit the red tests first, then the code.

Run your unit tests:
`env HOME=/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-176/src python3 -m pytest tests/unit/hooks -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
Then the regression, unchanged, through the heavy-job gate:
`env HOME=/home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-176/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W1-29 tests/acceptance/W1-49 tests/acceptance/W2-62 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(create the empty-home folder first). Report each run's counts. A red in those suites: re-run that case alone once;
if it still fails and you believe your change did not cause it, name it with its failure output in `risks` (the lead
checks it against the known-red list). Never edit those suites; never `git stash`.

## Commit (your paths only, after each green batch)
```
git commit -m "W2-176: <subject>" --trailer "Task: DAEO-ktiw" --trailer "Role: engineer" --trailer "Implements: DEC-1140, DEC-838, DEC-901, DEC-445, DEC-208, DEC-250" -- <paths>
```
No push, no merge, no `.tickets/` edit. Keep the delta near the ticket's estimate (about 160 lines of code, tests aside).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
In `evidence`: each commit hash12 and subject; the new sha256 of both hook files at your last commit; the exact
read-first lines produced for orchestrator (main, linked) and engineer; the additionalContext text in full. In
`tests`: counts for the unit run and the regression run, and the 50 MB timing's median.
