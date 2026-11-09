**W2-148 is not READY after round 2. One new finding blocks, and round 2 was the last round, so it goes to the owner (DEC-1010).** F1, F2 and the rows F4, F6, F8 to F14 are fixed. The new problem is in round 2's own F2 fix. If someone commits to the live repository while the G8 dry run is running, G8 puts the old file contents back. A guard tightening merged in that window stops being enforced (fails open), and the commit's files are lost from the working tree.

- **sandbox check (Step 0):** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-148` failed with `OSError: [Errno 30] Read-only file system`, as required. (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109…`, and `git update-index --refresh` exited 0. Both pass.
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- **task:** W2-148 (DAEO-xafn), independent review round 2 (the last), head `85a5cf655`, profile FULL.
- **status:** DONE. The verdict is NOT READY: F15 is in scope, ordinary work, and fails open.
- **work_completed:**
  - Read the ticket in full (including the CTO's settled readings), OPERATOR-AGENT-1 §1 to §6, JUDGEMENT.md and round 1's findings.
  - Read the round-2 diff (`45dd9e2dc..85a5cf655`) and re-read the whole ticket's code.
  - Probed the script scan with 61 shell forms in my own script (`python3 -I`).
  - Probed the path rule with 21 spellings.
  - Built a planted test on the engineer's kit: a CTO commit lands during the dry run. Read the related code paths. Ran the unit and acceptance tests read-only.
- **files_changed:** none in any tree. My probes are only in the scratchpad: `/tmp/gov-launch-independent-auditor-6r453i3z/claude-1000/-home-usain-gov-os-worktrees-W2-148/487b8f28-3cd7-4f08-9cc8-22ef54bbc860/scratchpad/probe_scan.py` and `/tmp/gov-launch-independent-auditor-6r453i3z/claude-1000/-home-usain-gov-os-worktrees-W2-148/487b8f28-3cd7-4f08-9cc8-22ef54bbc860/scratchpad/test_probe_r2.py`.
- **evidence:**
  - **Scan probe:** every round-1 F1 form now gives its hit: `then`, `do`, `else`, `elif`, `{ …; }`, `!`, `if !`, `while`, `until`, a subshell, a multi-line `for`, `case` arms, `f() { … }`, `function f { … }`, heredoc-fed `bash` and `bash -s`. So do `exec sudo`, `command sudo`, `xargs sudo`, `time git push`, `time -p`, a backslash-newline between words, `bash -c '…'`, unquoted `$(…)` and backticks.
  - **Scan misses (F16):**
    - `"$(git push)"`, `"$(curl https://…)"` and `` "`sudo ls`" `` inside double quotes;
    - `bash -lc` / `bash -ec`;
    - `eval "…"`, a here-string `bash <<< '…'`, `trap '…'`, `watch`;
    - `su\` + newline + `do`.
  - **Path rule probe:** it refuses the absolute repository path (quoted, trailing slash, double slash), `R=/home/usain/…`, `~/`, `$HOME/`, `${HOME}/`, `~usain/`, and a bare `cd`, `cd ~`, `cd -P ~`, `cd $HOME`, `pushd ~`. It allows `/home/$USER/Dynamic-Agentic-Engineering-OS`, `"/home/${USER}/…"` and `H=/home; cd $H/usain/…` (F17). It also allows `~/$D`, `"$HOME/$D"` and `cd -- ~`, which are harmless in the dry run because HOME is planted.
  - **Concurrency probe (F15):** an (a) ACT whose check sleeps 4 s, with a simulated CTO commit 1.5 s after G7 that adds a hidden glob to `path-map.yaml` and a new `.claude/skills/new/SKILL.md`. Result:
    - refused at G8 with "LIVE FILES CHANGED during the dry run (repo:.claude/skills/new/SKILL.md, repo:governance/project/path-map.yaml): restored…", `restored: true`;
    - HEAD's map has the new set, but the working tree's map does not; the skill is in HEAD but deleted from the working tree;
    - `git status` shows ` D .claude/skills/new/SKILL.md` and ` M governance/project/path-map.yaml`;
    - the P1 blames the dry run.
  - **Guard read:** the live guard reads the main tree's `path-map.yaml` from disk (`.claude/hooks/pretooluse.py:210, 220, 320`).
  - **Live checkout:** it is on `w2/integrate`. Over 2026-10-31 to 11-09, 25 commits there touched `path-map.yaml`, `.claude/` or `.rulesync/`, three of them on 11-09. Nothing the CTO's tools read holds commits during G8: the freeze is written only at the apply, under the operator root (F5).
  - **Scratch use:** 104K, 25 inodes.
- **tests:**
  - Unit tests `tests/unit/operator/`: **153 passed**.
  - Acceptance tests `tests/acceptance/W2-148/`: **156 passed, 1 deselected**. The required exclusion `-k "not real …"` left out `test_w2_148_launch.py::test_s18_settings_that_did_not_load_fail_the_canary_and_no_real_session_starts`, which uses a stub and was run in the CTO's `gov accept` (157/157). The `local_only`, `green_here` and `time_limit` filters left nothing else out.
  - My probe file: 2 passed.
  - All runs used the heavy slot, `-p no:cacheprovider`, an empty HOME and `PYTHONPATH=<W2-148>/src`.
  - S23's classifier part was re-run as `test_no_act_file_is_classed_lower_than_the_table` (passed). The replays and faults were not re-run in the sandbox, because the trial's `main()` hashes the live `~/.claude/`, `~/gov-os-operator/` and crontab. I take the CTO's run outside the sandbox for those.
- **discoveries:**
  - The new G8 re-hash cannot tell the dry run's changes from anyone else's. It restores control files byte for byte and deletes files created in the meantime, while the live tree is the CTO's working branch.
  - `restore_controls` in the (a) after-check's undo (round-1 code, now covering `.git/config` and core.hooksPath's folder too) does the same during the apply, reached through F5.
- **risks:** F15, if merged as is. The first time a merge lands during a dry run, the live guard silently enforces the old path map or settings, and the P1 points at the wrong cause.
- **lessons:** a byte-restore safety net on a shared live tree must check who made the change, or refuse without writing. "Restore whatever changed" is only safe under a freeze that everyone honours.
- **proposed_decisions:** the owner's choice on F15 (options under recommended_next_action).
- **unresolved:** F3, F5 and F7 stand as the owner's. F5 now also feeds F15's S15 site.
- **recommended_next_action:** to the owner, once (DEC-1010). Three options:
  - **Fix now (recommended; small: about 30 lines and 2 unit cases).**
    1. In `Run.live_changed` and the after-check's undo, restore a file only when it is on the touched list and its live bytes equal the frozen `after/` copy (the dry run's own effect).
    2. For any other changed file (a control file, or a touched file with other bytes, especially when the live HEAD moved), write nothing. Refuse, hold the lock, and send a P1 that names each file as "changed during the dry run by someone else or by the script: not restored, check".
    3. When F5 is settled, write the freeze the CTO actually reads from the start of G8, not only at the apply.
  - **Defer:** merge as is, with a standing rule that the CTO makes no commits while an ACT is queued. That rule is honour-based; nothing enforces it.
  - **Re-baseline:** drop the live re-hash and rely on the path rule alone. That brings back part of F2 (the `/home/$USER` spelling).

## Verdict per line

| Line | Verdict | Findings |
|---|---|---|
| S1 G1 frozen | pass | F8 fixed: an existing copy is reused only when intact, never replaced |
| S2 | pass | — |
| S3 | pass | — |
| S4 | pass | F9 fixed. A `review.md` taken afresh passes G4 only if its last block names this manifest sha, so it can never pass for a sha it did not review |
| S5 | pass | — |
| S6 | pass | F1 fixed, F14 fixed; F16 row |
| S7 | pass | — |
| S8 | pass | — |
| S9 | pass | — |
| S10 | pass | F13 fixed |
| S11 | pass | — |
| S12 G8 | **fail** | **F15 (blocking)**; F17 row. F2 is fixed for its own case: the path rule at G1 plus the live re-hash and restore |
| S13 | pass | F12 fixed (`<scratch>/NIGHTLY-RUNNING`, 6 h, as in `nightly.sh`); F5 stands |
| S14 | pass | F5 stands |
| S15 | **fail** | **F15** (the same restore in the after-check's undo); F3 stands; F11 fixed |
| S16 | pass | — |
| S17 | pass | F6 fixed (the wall's env and `request.txt`'s `timeout_ms`); F20 row |
| S18 | pass | — |
| S19 | pass | F7 stands (row) |
| S20 | pass | — |
| S21 | pass | F4 fixed (three channels, 190 characters, no TEST label, `push_cmd` still overrides); F10 fixed; F18 and F19 rows |
| S22 | pass | — |
| S23 | pass | Classifier re-run green; replays and faults from the CTO's run |
| S24 | pass | — |

**Failure lines:** all 14 hold on the round-2 code. The gates fail closed. An error at G7 or later is now pushed. Bytes changed after review are refused. No yes is taken from a non-human line. Waits and stops go by pid only. Residuals:
- Failure line 3 (a script hit classed (a)): partly open through F16's forms, a row.
- Failure line 5 (a file changed by the dry run not on the list): such a file is refused, but under F17 it can stay changed live.
- F15 itself is a live change made by the operator, which no failure line covers exactly. It is judged under S12 and S15.

## Findings

**F15 (S12, S15), scope: in. Blocking.**
- **What:** the round-2 live re-hash around G8 (`operator_run.py:561-613`) cannot tell whether the script or someone else changed a file.
  - It takes `control_snapshot` plus the touched files before the dry run and again after it, and treats every difference as the dry run's.
  - `live_changed` then calls `restore_controls` (`:1357-1388`), which writes the pre-dry-run bytes and unlinks any file created in the meantime under `.claude/**`, `.rulesync/**`, `.git/hooks`, `.git/config`, core.hooksPath's folder, the path map, the dead-man's and sentinel's files, the pin and the crontab.
- **Where it bites:** the live tree is `w2/integrate`, where the CTO merges and commits, and nothing holds those commits during G8. A ticket merge or CTO commit landing in the dry run's minutes (the clone, the checks, the undo) is reverted in the working tree. So are the owner's "don't ask again" rule in `.claude/settings.local.json` and Claude Code's `.claude/scheduled_tasks.lock`.
- **Shown by:** my planted probe. A committed path-map hidden glob was removed from the working tree and a committed new skill deleted, while the P1 said the dry run changed them and they were "restored".
- **Same defect, older site:** the (a) after-check's undo (`after_checks` → `undo_live` → `restore_controls`, round-1 code now also covering `.git/config` and core.hooksPath's folder) reverts a commit that races the apply and checks (F5's race).
- Ordinary work: yes, because the CTO commits and merges control files in the live tree several times a day (25 commits in 10 days, 3 on 11-09; the trial itself saw the path map change between rounds "by others' work"), the cron launch comes at any 10-minute mark, and no freeze the CTO reads is held during G8.
- Consequence: fails open. The live guard reads `path-map.yaml`, the settings and the hooks from the working tree, so a tightening merged during the dry run (for example a new hidden set, as in `3d8f2c67a` and `efcd91a22`) stops being enforced. It also loses work: a later `add -A` or `commit -a` commits the reversion, and new files are deleted.

**F16 (S6), scope: in. Row.**
- **What:** the script scan still misses:
  - `"$(…)"` and backticks inside double quotes (shlex keeps them as one word);
  - `bash -lc` / `-ec` (only a bare `-c` is read);
  - `eval "…"`, here-strings `<<<`, `trap '…'`, `watch …`;
  - a backslash-newline inside a word.
- Ordinary work: no, because none of the 57 past ACT files uses these forms with a hit command (searched twice in different words), and an install ACT's files are (b) or (O) by their path anyway.
- Consequence: fails open.

**F17 (S12), scope: in. Row.**
- **What:** the G1 path rule allows `/home/$USER/<repo>` and `"/home/${USER}/…"`; `USER` is in the dry run's clean env.
- **What the re-hash covers:** only the touched files and the control snapshot. A live file outside both stays changed after the refusal, and the refusal then reads "missing", with no live-changed notice. Outside the snapshot are unlisted repository files and, in HOME, `~/.claude/settings.json`, `~/.claude/hooks/**`, `~/.gov-os/machine/**` and `~/.config/gov-os*`.
- Ordinary work: no, because it needs both an uncommon spelling past the rule and the reviewer's path check, and a file the touched list does not name.
- Consequence: fails open.

**F18 (S21), scope: in. Row.**
- **What:** `send_channels`' per-channel results are returned but never recorded, and the `pings_log` line is always written. So the digest's "notices missing" can never show a toast or phone push that failed.
- Ordinary work: yes, because headless pushes fail now and then.
- Consequence: other (the notice is still in `pings.log` and the digest).

**F19 (S21), scope: in. Row.**
- **What:** `docs/changes/W2-148-evidence.md:56` still gives `push_cmd`'s default as `deadman.py --channel push --test`. In code, an unset `push_cmd` now means the three channels. The defaults table feeds ACT-OPERATOR-1's settings.
- Ordinary work: yes, because the CTO will copy that table.
- Consequence: other.

**F20 (S17), scope: in. Row.**
- **What:** F6's Bash timeout is `session_timeout_s − 60` (2,640 s). The program can still run longer:
  - a manifest check may run up to `check_timeout_s` (3,600 s);
  - a G9 hold that begins mid-run (a run at 01:50 reaching 02:00) waits with `hold_max_s` 0, that is, without limit.
- **What happens then:** the session is stopped by pgid (fails closed; the journal undoes if the apply had started). The request has already moved to `done/` and is not re-queued.
- Ordinary work: yes, because the cron launches up to the quiet hours.
- Consequence: other.

**Round 1's findings still standing (the owner's, recorded as they stand):**
- **F3 (S15):** the replay's call source; consequence other.
- **F5 (S13, S14):** the freeze's place; consequence other. It is also the route by which F15 reaches S15.
- **F7 (S19):** a row; ordinary no; fails open.

None of these now fails open in a new way, apart from F5's part in F15 above.

**Round 1's findings verified fixed:** F1, F2 (its own case), F4, F6, F8, F9, F10, F11, F12, F13, F14.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "pass", "findings": []},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "S6", "verdict": "pass", "findings": [{"id": "F16", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S7", "verdict": "pass", "findings": []},
 {"kpi": "S8", "verdict": "pass", "findings": []},
 {"kpi": "S9", "verdict": "pass", "findings": []},
 {"kpi": "S10", "verdict": "pass", "findings": []},
 {"kpi": "S11", "verdict": "pass", "findings": []},
 {"kpi": "S12", "verdict": "fail", "findings": [{"id": "F15", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F17", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S13", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S14", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S15", "verdict": "fail", "findings": [{"id": "F15", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S16", "verdict": "pass", "findings": []},
 {"kpi": "S17", "verdict": "pass", "findings": [{"id": "F20", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S18", "verdict": "pass", "findings": []},
 {"kpi": "S19", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S20", "verdict": "pass", "findings": []},
 {"kpi": "S21", "verdict": "pass", "findings": [{"id": "F18", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F19", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S22", "verdict": "pass", "findings": []},
 {"kpi": "S23", "verdict": "pass", "findings": []},
 {"kpi": "S24", "verdict": "pass", "findings": []}
]}
```