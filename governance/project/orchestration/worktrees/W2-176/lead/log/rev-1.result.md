Sandbox check (step 0): (a) the write of `/home/usain/gov-os-worktrees/.sandbox-trial-W2-176` failed with "OSError: Read-only file system" and no file exists; (b) `git hash-object -w --stdin` printed 1ae28402a109 (exit 0) and `git update-index --refresh` exited 0. `GOV_TICKET=DAEO-ktiw`. The `ps` check for ollama or llama-server shows nothing of mine.

task: DAEO-ktiw (W2-176), independent-auditor, review round 1 (CAP-33 review of a kernel template delta)
status: DONE
work_completed: Checked identity (HEAD 13fd1dd34e32 = probe head). Read the ticket, the governing decisions (DEC-1140 (1)(b) and (4), DEC-1118 (A)), both hooks at head, both W2-176 test files, `launch_worker.sh`, the lead's checkpoint, and the W1-49 helper that parses hook stdout. Checked the window table and the auto-compaction point against code.claude.com/docs/en/model-config. Ran the given unit folder through `heavy_slot.sh`. Ran 10 probes of my own in `$TMPDIR` (script at `$TMPDIR/probe/probe.py`). I did not re-run the lead's acceptance regression (its verify was running).
files_changed: none. `git status --porcelain` is empty at the end. Only `$TMPDIR` was written.
evidence: The diff names exactly the four allowed paths. Probes P1–P10 below. The docs say Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.2 all run a 1M window by default, and 1M models auto-compact "at about 967K tokens", so 85 % (850K) comes first. Scratch use: 112 KB and 28 inodes.
tests: The given command gave 147 passed, 5 failed, 36 deselected in 24 s. The 36 deselected are the local_only, real, green_here and time_limit cases. All 5 failures are older tests that expect the old stdout shape:
- `test_resume_hooks.py::test_an_unset_role_is_not_the_orchestrator` and `::test_precompact_appends_one_block_and_sessionstart_warns` assert empty stdout; they now get the read-first line.
- `::test_a_checkpoint_precompact_cannot_write_is_left_as_it_was`, `::test_a_write_that_fails_part_way_leaves_the_checkpoint_as_it_was` and `test_w29_hooks.py::TestPreCompactCombined::test_checkpoint_failure_reports_systemmessage` call `json.loads` on the whole of stdout and get JSONDecodeError, because the text line now comes first.

All 5 follow from S1 itself; none is a defect in the delta (R4). The W2-176 cases all pass; the 50 MB timing case passed in-suite.
discoveries: Once a session has been reminded it is never reminded again, even after a compaction (R1). A subagent's tool call can use up the main session's reminder (R2). For leads and workers, DEC-1118 (A) asks for a handover at about 200k, while the reminder fires at 850k on 1M models (R5).
risks: R1 and R2 only matter once `context_watch.py` is registered. Under DEC-803 they are entry criteria of the registration ACT, not of this delta. R4 leaves the hooks unit folder red when the branch is merged unless those two test files are updated.
lessons: A behaviour change to a kernel hook's stdout breaks every older test of that hook's output. A ticket's `allowed_paths` should include those tests, or name them as a known follow-up.
proposed_decisions: (a) The CTO adds `tests/unit/hooks/test_resume_hooks.py` and `tests/unit/hooks/test_w29_hooks.py` to the ticket's paths, for assert-only updates (the line first, the JSON on the second line). Otherwise these reds go to a follow-up ticket before the merge. (b) Before the registration ACT: re-arm the reminder after a compaction (R1), and skip events that carry `agent_id` (R2).
unresolved: R2 depends on which `transcript_path` Claude Code passes to a hook that fires inside a subagent. The docs do not say, and I could not observe it in the sandbox.
recommended_next_action: The lead writes the CIT-P record (S4) and handles proposal (a) as a paths decision, not as a review round. R1 and R2 go into the registration ACT's entry criteria.

## Findings

**R1** (`template/governance/kernel/hooks/context_watch.py:97-98`, S2)
- **What happens:** the "already reminded" marker is one file per `session_id` and is never cleared. Claude Code keeps the same session through a compaction (SessionStart fires "again later in the session, after /clear or a compaction"). So a session that compacts once and later fills up again gets no reminder the second time. DEC-1140 (4) has the CTO session running to about a million tokens with compactions. The read-first line in the compaction summary (S1) still fires every time, so only the earlier reminder is lost. This meets the KPI's literal "once per session", not the owner's "near compaction".
- **Reproduction:** P1. Same session id: 90 % gives the reminder; after a planted compaction, 4 % gives nothing; 92 % then gives nothing.
- Ordinary work: yes, because any session that compacts twice hits it.
- Consequence: other.
- **What would reverse it:** evidence that the session id changes at a compaction.

**R2** (`context_watch.py:87-100`, S2; PLAUSIBLE)
- **What happens:** `agent_id` is ignored. The docs say a subagent's tool calls fire the same PostToolUse hooks. If that event carries the main transcript, the main session's 85 % sends the reminder into the subagent's context and writes the marker. The main session then never gets it, and the subagent is told to update the CTO's RESUME HERE, DECIDED-NOT-DONE and report-state files.
- **Reproduction:** P2. An event with `agent_id: a1` at 90 % gives the reminder; the next main-thread event gives nothing.
- Ordinary work: yes, because the CTO and leads use subagents routinely.
- Consequence: other.
- **What would reverse it:** a real subagent event whose `transcript_path` is the subagent's own file. Its lines are marked as sidechain, so the hook would stay silent.

**R3** (`template/governance/kernel/hooks/precompact.py:53-59, 68`, S1)
- **What happens:** a worker's brief is picked as the most recently written file in the tree's shared brief folder. This worktree shows it now: `rev-1.md` (00:08:01) is newer than `eng-1.md` (23:58:25), so an engineer compacting now would be told to read the reviewer's brief.
- **Reproduction:** P9. The engineer's line names `rev-1.md`.
- Ordinary work: no, because `launch_worker.sh` copies the common files before the brief, and one tree's workers normally run in sequence. Only overlapping launches in one tree hit it.
- Consequence: other.
- **What would reverse it:** a launch flow where workers never overlap in one tree.

**R4** (`tests/unit/hooks/test_resume_hooks.py:119,130,146,170`, `tests/unit/hooks/test_w29_hooks.py:278`; out of the KPI lines)
- **What happens:** the 5 reds under "tests". They encode the stdout contract that S1 replaces. Their files are outside `allowed_paths`, and F2 forbids editing them here.
- **Reproduction:** the given pytest command.
- Ordinary work: yes, because any regression run of the hooks unit folder hits them after the merge.
- Consequence: other (red suite; behaviour is correct).
- **What would reverse it:** a reading of S1 under which empty stdout on success is still allowed.

**R5** (`context_watch.py:22-29`; out, the KPI fixed the table)
- **What happens:** the table is correct per the docs. But leads and workers are to hand over at about 200k (DEC-1118 (A)), and on 1M models the reminder fires at 850k, so in practice it reaches only the CTO. Separately, with `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` the session compacts at 200K and the hook stays silent. That variable is not set anywhere in the project.
- **Reproduction:** P6 (180K with that variable set gives nothing).
- Ordinary work: yes for the DEC-1118 point, because leads and workers are expected to hand over well before 850k.
- Consequence: other.
- **What would reverse it:** DEC-1118 (A) no longer applying to leads and helpers.

**R6** (`context_watch.py:92`, `precompact.py:141`, F1)
- **What happens:** without `CLAUDE_PROJECT_DIR`, both hooks take the working directory as the project root. From a subfolder, `context_watch.py` writes its marker under `<subfolder>/.gov-runtime/scratch/context_watch`, and `precompact.py` names `<subfolder>/…/CHECKPOINT.md` (the precompact behaviour predates this delta).
- **Reproduction:** P4 (marker created under `src/`) and P10.
- Ordinary work: no, because Claude Code sets `CLAUDE_PROJECT_DIR` for every hook, and the registration commands themselves use it.
- Consequence: other.
- **What would reverse it:** a supported hook launch without `CLAUDE_PROJECT_DIR`.

**R7** (`precompact.py:59`, S1)
- **What happens:** if a file disappears between listing the folder and reading its time, the error escapes before the line is printed. That worker's compaction then gets no read-first line and no message.
- Ordinary work: no, because it needs a file deleted at that very moment.
- Consequence: other.
- **What would reverse it:** that error being caught inside `newest()`.

**What I probed and found sound:**
- Exit code is always 0. No output has a `decision` key. Neither source names or reads a compaction threshold.
- The stdout line comes first; the error systemMessage follows it as text, which loses nothing since Claude Code discards a PreCompact systemMessage.
- The CTO (main tree) gets the orchestrator CHECKPOINT path and a lead (linked worktree) the lead CHECKPOINT path, each with RESUME HERE. A worker's record is the one just written.
- The names that `sessionstart.py` imports are kept.
- The reminder is silent below 85 % and fires once at 85 %. It reads only the last 256 KiB and answered a 50 MB transcript in 19–24 ms (P7).
- The hook stays silent, with exit 0, on: a partial last line, sidechain lines, an assistant line over 256 KiB (P3), synthetic zero-usage lines (P5), an unwritable marker folder (P8), and a hostile session id.
- F2: the diff names only the four allowed paths.

Classification (DEC-809): no blocking finding. R1 and R2 are in scope and reachable in ordinary work, with consequence other; they are entry criteria of the registration ACT (DEC-803). R4 and R5 are out of scope, ordinary work, consequence other; R4 is a prerequisite for the merge. R3, R6 and R7 are not ordinary work. So everything lands as recorded rows and no second round is needed (DEC-1010).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "R3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R7", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "R6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}]}
```

VERDICT: READY (probe head 13fd1dd34e32)