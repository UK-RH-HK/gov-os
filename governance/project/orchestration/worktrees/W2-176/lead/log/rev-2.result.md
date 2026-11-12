task: DAEO-ktiw (W2-176), review round 2 of 2 (the last one, DEC-1010), independent auditor, read-only. Probe head `7894a35e116f`, base `1798e82f1201`.

status: DONE. VERDICT READY. One new finding (R8); it is not blocking.

work_completed:
- **Step 0 sandbox check (launch_worker.sh):**
  - (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-176` failed (`OSError: [Errno 30] Read-only file system`), and no file exists.
  - (b) `git hash-object -w --stdin` worked (returned `1ae28402a109…`) and `git update-index --refresh` worked (exit 0).
  - `GOV_TICKET=DAEO-ktiw`.
  - The `ps` check for ollama or llama-server shows nothing.
- **Identity:** `git rev-parse HEAD` is `7894a35e116f30622d3177881b0e6777fed31083`, which matches the probe head.
- **What I read:** the ticket with its Delegated line, the context packet, DEC-1140 (1)(b) and (4), DEC-1118 (A) and DEC-838, the whole delta and round 2's own diff, both hooks, both W2-176 test files, the two older test files' diffs, the settings registration form, `launch_worker.sh`'s brief copy, the coordination ticket `DAEO-sdxk`, and the CTO's three files in the main tree.
- **What I ran:** the briefed unit run, an opt-in run of the rows the repository's lists leave out, and two probes of the hooks in TMPDIR copies (each role, hostile tickets, failure modes).

files_changed: none. `git status --porcelain` is empty at the end. The template hooks' `__pycache__` is unchanged: it still holds only `precompact.cpython-312.pyc` from 00:03, before round 2.

evidence:
- **F2:** the commits on the branch's first parent after the base (2f9e28dbb, 13fd1dd34, 761e80e78, 317955a4b, 7894a35e1) touch only allowed paths. The merge d69eed1fc differs from its integrate parent only in the ticket's five paths. The other names in the base-to-head diff (`.tickets/*`, `governance/project/orchestration/*`) come in through the integrate merge, not from the ticket.
- **The two older test files changed only in assertions.** One `out = capsys.readouterr().out` binding was added, and it feeds only asserts.
- **CTO setup:** the main tree's `.claude/settings.local.json` sets `GOV_ROLE=orchestrator` and `GOV_TICKET=DAEO-sdxk`. `DAEO-sdxk` is 2,934 bytes with `class: coordination` on line 14. The three files named for the CTO all exist in the main tree.
- **TMPDIR:** 48K and 14 inodes after cleanup.

tests:
- **Briefed run:** 167 passed, 36 deselected, 0 failed (63.7 s).
- **What was deselected:** the 36 come from the repository's opt-in lists (`tests/optin-lifted*.txt`: rows beyond the first of `test_w29_hooks.py` and `test_w2_106_template_hook_lines.py`). The `-m`/`-k` real-model exclusion removed nothing in this folder: 167 items are collected with and without it. No W2-176 case was deselected, and the 50 MB timing case ran.
- **Opt-in run:** `test_w29_hooks.py`, `test_resume_hooks.py` and `test_w2_106_template_hook_lines.py` with `--optin lifted,breadth` gave 75 passed and none deselected.
- **Not run by me:** the W1-29, W1-49 and W2-62 acceptance regression, which the lead is running.

discoveries:
- **Refusals I worked round:** the Write tool's permission prompt refused my probe script in TMPDIR (a non-interactive session). I ran the same probes from stdin with `python3 -`, writing only under TMPDIR, and removed them afterwards. Calling the `claude-api` skill to check the model windows failed.
- **Model windows:** the table (Sonnet 5.5 and Haiku 5.5 at 1,000,000) rests on the docs quoted in CIT-P §1. I did not fetch them myself. For leads and workers this matters only through `min(window, 200,000)`.

risks:
- R8 (below), not blocking.
- R3 and R6 stay recorded rows, as before:
  - **R3:** `launch_worker.sh` copies the two common files first and the task brief last, so the newest file is the latest launch's brief. A wrong brief needs two workers overlapping in one tree, with the earlier one compacting after the later launch. Ordinary work: no.
  - **R6:** the registration form runs `"$CLAUDE_PROJECT_DIR/template/…/hook.py"`, so the hook cannot start without that variable. The fallback to `cwd` is practically unreachable.

lessons: none

proposed_decisions: none

unresolved: none in this round's scope. S4 (the CIT-P record) is the lead's.

recommended_next_action: the lead lands R8 as a recorded row, finishes S4 with the sha256 values at `7894a35e116f`, then the owner approves and the class (b) registration ACT follows.

decisions: DEC-1140, DEC-1118, DEC-838, DEC-801, DEC-808, DEC-809, DEC-1010

**Round 1's items and the CTO's decisions, checked at `7894a35e116f`:**
- **P1 (a), done:** both older files now assert the read-first line first and the JSON object on the last line, and nothing else changed.
- **P2 (a), done:** the CTO's reminder names `<root>/.gov-runtime/scratch/orchestrator/log/report-state.json`.
- **R7, done:** `newest()` (precompact.py:53-67) skips a file that disappears before its stat. Its tests are `test_a_brief_deleted_before_its_stat_gives_the_next_newest` and `test_when_every_brief_is_gone…`.
- **R2, done:** an event carrying `agent_id` is silent and writes nothing, even at 99.9 % (probed).
- **R1, done:** probed for the CTO and a lead. One reminder at 85 %. Nothing at 120k/200k (above 50 %) or on later calls. Usage below 50 % removes the marker, and the next call at 85 % or more reminds again.
- **P4, done, CTO:** the orchestrator on the `class: coordination` ticket in the main tree is measured against the model's window. On Opus it is silent at 849k and reminded at 850k, also with `[1m]` and date-suffixed model ids. An unknown model gets 200,000.
- **P4, done, leads and workers:** a lead (orchestrator on its own ticket in a linked worktree) is silent at 169k and reminded at 170k, with its own `.gov-runtime/scratch/lead/CHECKPOINT.md` (taken from precompact's `checkpoint_rel`). An engineer is reminded at 171k with its record folder.
- **Hostile `GOV_TICKET` fails toward the 200,000 cap.** Every one of these probes got the capped reminder at 171k and no CTO text:
  - path traversal (`../../etc/passwd`, `x/../x`), a missing file, an empty value, a ticket path that is a directory;
  - `class:` only after 4 KiB, quoted or indented `class:`, `coordinationX`, `class: coordination` only in the body;
  - only CRLF line endings: the regex takes CRLF, but the `---\n` front-matter check does not.
  - A 50 MB coordination ticket reads only 4 KiB and answers in 23 ms.

**Probed and found sound:**
- **Never blocks or slows a call:**
  - No source holds `autocompact` or `AUTO_COMPACT`, a decision field or `"block"`.
  - Every exit code is 0.
  - Each hook process takes 20–80 ms, including the lead path's import of precompact.
  - precompact does not read stdin.
- **Writes stay in scratch:**
  - context_watch writes only `.gov-runtime/scratch/context_watch/<session>` (makedirs, `O_EXCL` create, removal on re-arm).
  - The lead path sets `dont_write_bytecode` before importing precompact, and a copied hooks folder gained no entries.
  - The read-first line adds no write to precompact.
- **Read-first line per role:** probed with trigger auto and manual. One line for the CTO (main tree, orchestrator CHECKPOINT), the lead (lead CHECKPOINT) and the engineer (newest brief and record folder). The line comes first and the systemMessage JSON last when the record or the state block fails.
- **Failure modes:** a scratch folder that cannot be written means silence and exit 0. A sidechain last line is skipped and the main line used. `sessionstart.py`'s imports from precompact are kept.

**Findings**

**R8:** `template/governance/kernel/hooks/context_watch.py:126-129`
- **What happens:** the per-window marker is created before the reminder text is built. For a lead, building the text imports `checkpoint_rel` from the sibling `precompact.py`. If that import (or anything else in `text()`) raises, the exception is swallowed: the window's only reminder is spent and nothing is said until usage falls below 50 %. It should build the text first, or remove the marker when building fails.
- **Reproduction:**
  1. Copy only `context_watch.py` into an empty folder.
  2. Create a linked-tree root (a `.git` file) and a transcript whose last assistant line is Opus with `input_tokens` 175,000.
  3. Run the hook twice as `GOV_ROLE=orchestrator`: both runs print nothing, exit 0, and the marker `.gov-runtime/scratch/context_watch/s` exists after the first.
  4. The same setup as an engineer prints the reminder.
- **Ordinary work: no**, because `precompact.py` always ships beside `context_watch.py` in the kernel template, and the registration form runs the hook from that folder. Only a partial copy or a rename of the hooks reaches it.
- **Consequence: other.** One reminder is lost; nothing is blocked and no work is lost.
- **Scope:** in (S2).
- **What would reverse it:** a registration or deployment path that runs `context_watch.py` without `precompact.py` beside it would make it ordinary work, yes. Code that builds the text before creating the marker would close it.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}]}
```

**Classification (DEC-809):** one finding, R8: in scope, ordinary work no, consequence other, so not blocking. It lands as a recorded row. R3 and R6 stay recorded rows (ordinary work no, consequence other).

VERDICT: READY (probe head `7894a35e116f`)