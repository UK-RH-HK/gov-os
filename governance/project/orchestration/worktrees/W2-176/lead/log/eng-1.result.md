Sandbox check: (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-176` failed with "Read-only file system", and no file was created. (b) `git hash-object -w` (wrote `1ae28402a109…`) and `git update-index --refresh` both exited 0. Pass.
ps check: `ps -eo pid,args -C ollama,llama-server` shows no ollama or llama-server process of mine. The sandbox's own pid namespace showed only the ps command and its shell.

task: W2-176 (DAEO-ktiw), engineer, run 1: context awareness before compaction (S1, S2, S3, F1, F2).
status: PACKAGES. The code meets S1, S2, S3, F1 and F2. All 50 of my unit cases and the whole regression pass. But 5 existing unit tests in `tests/unit/hooks` (outside my paths) now fail because S1 changes what precompact.py prints. Someone who owns those files has to decide on them; see proposed_decisions.
work_completed:
- Red tests were committed first and confirmed red (41 failed, 8 passed). The code then turned them green.
- **precompact.py:** prints one plain-text line on every run, for every role: `Begin the compaction summary with this line: "READ FIRST: …"`.
  - The orchestrator gets the absolute `checkpoint_rel` path with "its RESUME HERE section".
  - Other roles get "your brief and your record" with the newest file in `scratch/brief/` and `scratch/checkpoints/<GOV_TICKET>/`, or the folder when it is empty.
  - The line is built after the record write, so it names the record just written.
  - Unchanged: the checkpoint record, the state block, the systemMessage JSON, the always-exit-0, and the names `STAMP`, `checkpoint_rel` and `split`.
  - On error the read-first line goes out first and the JSON after it. Why (comment in `say()`): stdout that is not one JSON object is read as plain text, so all of it goes into the compaction instructions with the line at their head. Claude Code discards a PreCompact systemMessage anyway, so the JSON loses nothing.
- **context_watch.py** (new, PostToolUse):
  - Reads only the transcript's last 256 KiB (seek).
  - Takes the last assistant line that is not a sidechain (subagent) line and has usage, skipping lines that do not parse; used = input + cache_creation + cache_read.
  - Window table: `CONTEXT_LIMITS`, a module-level dict that tests can replace. Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.2 are 1,000,000; a `[1m]` or date suffix matches its base; anything else is 200,000.
  - At 85 % or more it creates the state file (O_EXCL) in `<root>/.gov-runtime/scratch/context_watch/<safe session id>`, then prints the additionalContext once.
  - The wording depends on the role: the CTO in the main tree, a lead in a linked worktree, or a worker.
  - Any error, a non-PostToolUse event, or a project root that is not absolute: prints nothing, exits 0.
files_changed: template/governance/kernel/hooks/precompact.py; template/governance/kernel/hooks/context_watch.py (new); tests/unit/hooks/test_w2_176_precompact.py (new); tests/unit/hooks/test_w2_176_context_watch.py (new).
evidence:
- **Commits:**
  - `2f9e28dbb3a9` W2-176: red unit tests for the read-first line (precompact.py) and the context watch (context_watch.py)
  - `13fd1dd34e32` W2-176: the read-first line in precompact.py for every role, and context_watch.py (PostToolUse, once per session at 85 %)
- **sha256 at 13fd1dd34e32:**
  - precompact.py: `adde0bbeca5854d0da3fce5776f5db066a88a09301a1901b5cd7e8a37380605f` (base `eb0174da…c95086`, checked before the edit)
  - context_watch.py: `4f62182637698dbdf7f5d5c79480a3eb50be5505b6dc0418bd479dae5ca7ca18`
- **F2:** `git diff --name-only 1798e82f1201..HEAD` lists exactly the four allowed paths.
- **Read-first lines** (planted roots shown as `<root>`):
  - orchestrator, main tree: `Begin the compaction summary with this line: "READ FIRST: <root>/.gov-runtime/scratch/orchestrator/CHECKPOINT.md, its RESUME HERE section, before any other work."`
  - orchestrator, linked worktree: `Begin the compaction summary with this line: "READ FIRST: <root>/.gov-runtime/scratch/lead/CHECKPOINT.md, its RESUME HERE section, before any other work."`
  - engineer: `Begin the compaction summary with this line: "READ FIRST: your brief and your record, <root>/.gov-runtime/scratch/brief/eng-1.md and <root>/.gov-runtime/scratch/checkpoints/DAEO-ktiw/CP-DAEO-ktiw-3.md, before any other work."`
- **additionalContext**, CTO in the main tree, in full:

  > Context watch: this session has used 85 % or more of its context window. Write your checkpoint now and update every file that needs it: the RESUME HERE section of <root>/.gov-runtime/scratch/orchestrator/CHECKPOINT.md, <root>/governance/project/orchestration/packages/DECIDED-NOT-DONE.md and <root>/log/report-state.json. Begin your compaction summary with the line "READ FIRST: <root>/.gov-runtime/scratch/orchestrator/CHECKPOINT.md, its RESUME HERE section, before any other work." This is a handover aid, not a stop and not an early compaction: carry on with your work once the handover is written.

  The lead's version differs only in the files part (`your CHECKPOINT, <root>/.gov-runtime/scratch/lead/CHECKPOINT.md`) and its READ FIRST path, the lead checkpoint. The worker's files part is `your record (gov checkpoint), under <root>/.gov-runtime/scratch/checkpoints/<GOV_TICKET>`, and its line is `"READ FIRST: your brief and your record, before any other work."`
- **Scratch:** my folder is 6 inodes; the sandbox TMPDIR is 5.1 MB in all. Pytest removed the 50 MB transcript after it passed.
tests:
- **My files:** 50 passed (16 precompact, 34 context_watch).
- **Unit run** (the brief's command over `tests/unit/hooks`): 147 passed, 5 failed, 36 deselected. The 5 are the tests named under proposed_decisions; they failed the same way when re-run alone.
- **Regression** (W1-29, W1-49, W2-62 through `heavy_slot.sh`, unchanged): 147 passed, 61 deselected, exit 0. Run alone, `test_w1_49_threshold.py::test_the_project_settings_set_no_auto_compact_window_of_their_own` passes.
- **50 MB timing:** median 16.8 ms over 5 runs (17.6, 17.0, 16.6, 16.8, 16.6 ms), including Python start-up.
- **Left out by the exclusion:** the cases marked `local_only` or with `real`, `green_here` or `time_limit` in their names (36 in the unit run, 61 in the regression). The CTO runs those outside the sandbox.
discoveries:
- pytest is installed in the user site under the real HOME (`~/.local`). With `HOME` set to the empty folder, `python3 -m pytest` fails with "No module named pytest". I kept HOME empty and added `PYTHONUSERBASE=/home/usain/.local` to both runs; nothing else in the commands changed.
- The Write tool is refused under `.gov-runtime/scratch/engineer/`, so my run scripts live in the sandbox TMPDIR.
- `gov.checkpoint.record.write` needs `.tickets/<id>.md` and a git repository, so the precompact unit fixture plants both.
risks:
- These 5 tests are now red because S1 makes precompact print a line on every run:
  - `test_resume_hooks.py::test_an_unset_role_is_not_the_orchestrator` and `::test_precompact_appends_one_block_and_sessionstart_warns` expect empty stdout (`(0, "", "")`, lines 119 and 130).
  - `test_resume_hooks.py::test_a_checkpoint_precompact_cannot_write_is_left_as_it_was` (line 146), `::test_a_write_that_fails_part_way_leaves_the_checkpoint_as_it_was` (line 170) and `test_w29_hooks.py::TestPreCompactCombined::test_checkpoint_failure_reports_systemmessage` (line 278) call `json.loads` on the whole stdout, which now holds the line plus the JSON.
- The read-first line names the newest file in the brief folder by modification time. Where several briefs share the folder (this worktree has three), the newest may not be the session's own.
lessons: Check where pytest is installed before setting HOME to an empty folder. Run the whole `tests/unit/hooks` folder before writing code: tests that pin a hook's exact stdout belong to the regression too.
proposed_decisions:
- **(P1)** Revise the 5 tests above, by a ticket that owns `tests/unit/hooks/test_resume_hooks.py` and `test_w29_hooks.py`, or by adding them to W2-176's `allowed_paths`. Each keeps its assertion, but on the JSON line: expect the read-first line as the first stdout line, and parse the systemMessage from the last line. Recommended; confidence high. The alternative, printing no line in those cases, breaks S1 ("on every compaction, for every role").
- **(P2)** The class (b) ACT that registers `context_watch.py` under PostToolUse in `.claude/settings.json` stays the CTO's, after the owner's approval. I made no change there.
unresolved: S4 (`docs/changes/W2-176-CIT-P.md`) is the lead's and is not written. The 5 reds wait for P1.
recommended_next_action: The lead decides P1, then gets the 5 tests revised and re-runs `tests/unit/hooks`. Then the independent review of the delta (hashes above), the owner's approval of the bytes, S4, and the registration ACT.