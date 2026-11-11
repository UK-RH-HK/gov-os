# D-10's red-fix list: the review of W2-116's and W1-32's cases against W2-56's cleaned environment and full removal (W2-116, DAEO-f58b)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-56-effects-review.md`; branch `w2/W2-116-d10-tests at b0384ac62`; reviewer log `/home/usain/gov-os-worktrees/W2-116-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-56-effects-review.json`.
- verdict.py: READY (no blocking finding).

task: W2-116 (DAEO-f58b). Independent review of D-10's red-fix revision `9ca161a6f..b0384ac62` (commits `4c798dff5` for W2-116 and `b0384ac62` for W1-32), on head `2e316b5a3469`.

- **sandbox check (step 0):** passed.
  - (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-116` failed with `OSError: [Errno 30] Read-only file system`.
  - (b) `git hash-object -w --stdin` worked (blob `1ae28402a109`, "sandbox-trial", with no reference to it) and `git update-index --refresh` worked. That blob is the only thing this session wrote, and the check requires it.
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing. No model server is running and none is mine; I started no process apart from git, ps and du.
- **status:** DONE
- **work_completed:**
  - Identity: HEAD is `2e316b5a3469`, the merge of integrate `7b422979c` onto `b0384ac62`. `git status --porcelain` was empty at the start and is empty now.
  - The later merge brings in only W1-46's new helper function, two W1-46 cases and two governance records. `git diff 9ca161a6f 2e316b5a3 -- tests/acceptance/W2-116 tests/acceptance/W1-32 tests/acceptance/W2-56 src/gov/launch` shows exactly the revision's 7 files.
  - I read the diff, both suites' support code, the launcher (`src/gov/launch/launcher.py`, `environ.py`), how `gov retrieve` picks its store, W2-56's ticket lines 36, 43 and 46, the designer's brief, JUDGEMENT.md and the register entries cited.
- **files_changed:** none
- **evidence:**
  - Step 0 and ps results above.
  - Trailers as git parses them (see check 3).
  - The diff stats.
  - My TMPDIR (`/tmp/gov-launch-ip3g6k9m/claude-1000`): `du -sh` 20K, `du -s --inodes` 8. I created nothing there.
- **tests:** I ran none. My role says to re-run nothing already run and to run code only to reproduce a finding, and the one finding (F1) is about documentation. The designer's counts (W2-116 20 passed; W1-32 79 passed, 1 failed in the command-set case, which is another item) were taken on `b0384ac62`. The later merge does not touch any code these cases use. No exclusion filter applied because I ran no pytest.
- **discoveries:**
  - Work is now split between the suites. W2-116's stand-in only needs the launcher's own values (`GOV_STORE`, `GOV_ROLE`, `GOV_TICKET`) to reach the session.
  - Which parent variables the session keeps (PATH, HOME, locale), and that no parent CLAUDE*, GOV* or PYTHONPATH reaches it, is checked only by W2-56's S5 cases. That was already true: before the revision, W2-116 relied on exactly the variables W2-56 now removes.
- **risks:** The W1-32 premise relies on the launcher creating its temp folder directly in its own TMPDIR and never changing that folder's mode. If a future launcher changes either, these cases go red on the premise, visibly; they do not pass by accident.
- **lessons:** When a stand-in needs case values under a cleaned environment, write them into the stand-in's own file, beneath the session's environment so the launch's values still win. Then check that the planted set contains none of the variables under test (here `GOV_STORE`, `GOV_ROLE`, `GOV_TICKET`).
- **proposed_decisions:** none
- **unresolved:** none in scope. I did not review the W1-32 command-set red.
- **recommended_next_action:** Both KPIs pass and nothing blocks; READY is for `verdict.py` to compute. The CTO merges `w2/W2-116-d10-tests` as usual. F1 can be fixed next time W1-32's support module is edited (DEC-802); no review round needed.

decisions: DEC-392, DEC-826, DEC-877, DEC-902, DEC-1112, DEC-801, DEC-808, DEC-1010

The cited decisions are in force. DEC-826, DEC-902, DEC-1109 and DEC-1112 are ACCEPTED; DEC-877 is DONE (it was ACCEPTED before). None is PROPOSED or superseded, so there is no DEC-1073 finding.

## Answers to the checks

**1. No expectation lowered**

*W2-116*

- **Where the session's search gets its environment:** the case's environment plus the open-gate readings sit at the bottom. The session's own process environment is laid over them, and the `--settings` env block over that (`w2_116_support.py:694`).
- **What decides the store:** with no `--root`, a plain `gov retrieve` answers from `GOV_STORE`, or else from the working tree (`src/gov/retrieve/command.py:100-116`).
- **The planted values name no store:** the case's environment (`w2_116_support.py:235-260`) and the gate variables (`:734-783`) contain no `GOV_STORE`, `GOV_ROLE` or `GOV_TICKET`. Nothing in the suite changes `env` or mentions `GOV_STORE` (grep).
- **So these values come only from the launch:** both the CLI's environment and the settings block carry the launcher's own values (`environ.py:26-33`, `launcher.py:530-531`). If the launch failed to set `GOV_STORE`:
  - the S3 cases would answer STORE_MISSING and go red;
  - the F1 case would answer from the worktree's own store and go red.
- **No hidden leak:** the planted values live in the stand-in's file and reach only its child `gov retrieve`. They neither widen the cleaned environment nor read from it. No W2-116 case ever checked that parent variables are absent; that is W2-56 S5's job, and its cases are untouched.
- **What the session received is still checked:**
  - The guard case checks `GOV_ROLE` and `GOV_TICKET` in the settings block, and that the session's working folder is the worktree.
  - S3 and F1 check which store the search answered from, which depends on the launch's `GOV_STORE`.
  - The assertions in `test_w2_116_launch.py` are unchanged; the diff touches only its module docstring.
- **Templates:** the eight template copies are committed in H1, so W2-153's template refusal never stops these launches. W2-116 asserts nothing about templates.

*W1-32*

- **The failure is still in the launcher's removal:**
  - The launcher creates the session's temp folder directly in its own TMPDIR (`launcher.py:521`).
  - The stand-in session's last act sets that TMPDIR, the temp folder's parent, to mode 0500.
  - The launcher's removal (`:679-695`) restores 0700 on the temp folder and the folders inside it, and empties it. Its final step, deleting the folder itself, fails with EACCES at the read-only parent.
  - The launcher catches the error (`:573-575`), writes one line naming the folder, and keeps the session's exit code.
- **What stays asserted, unchanged:**
  - the exit code (0 and 7);
  - no Traceback;
  - exactly one non-blank stderr line, containing the folder's path;
  - the exit codes in the stderr-closed and reader-gone cases;
  - no envelope and one session (that case was not edited).
- **The premise is not weaker:** the new premise ("the temp folder still exists") holds for a removal that fails. Like the old premise (`sealed/kept.txt` still exists), it would also hold for a launcher that never tried to remove anything. That gap is not new: the stderr case and the folder-removed cases in W1-28 and W2-56 cover it. If the removal succeeds, the premise goes red.
- **Realistic, and not something the launcher should handle:**
  - The mechanism is a test construction. A real sandboxed session cannot change its temp folder's parent, because that folder is mounted read-only to it.
  - The effect is a realistic kind of failure: an error during removal that the launcher cannot fix inside its own folder. Examples: an entry held by a process that outlived the session, a read-only remount, an entry owned by another user.
  - The launcher handles every such error on the same path, so the case exercises the real code.
  - To handle it, the launcher would have to change the mode of the shared TMPDIR. For /tmp, which root owns, that is impossible, and it goes beyond restoring 0700 on its own folder (DEC-902, W2-M405).
- **Clean-up:** both the `stuck` fixture and the added case's `finally` now restore the parent folder too.

**2. No interference with W2-56's own cases.**
- Only the 7 files in the two suites changed.
- No other suite imports `w1_32_launch_support` or `w2_116_support` (grep across `tests/`).
- W1-32 builds its stand-in from a copy of W1-28's stand-in text and changes nothing shared. The new `plan()` option defaults to off, and only W1-32's `stuck_plan` turns it on.
- All state lives in each case's own temp folder.
- W2-56's folder mentions W2-116 only in prose.

**3. Trailers.** Both commits parse as `Task: DAEO-f58b`, `Implements: DEC-1109, DEC-1112`, `Role: independent-test-designer`, a Rewrite-Reason and `Co-Authored-By: Claude Opus 5.5`.
- Each Rewrite-Reason is word for word what the designer's brief gave:
  - W2-116: "DEC-826 Q5, DEC-877 item 4: …"
  - W1-32: "DEC-902, W2-M405: …"
- There is one commit per suite: `4c798dff5` changes only `tests/acceptance/W2-116/**` (3 files) and `b0384ac62` only `tests/acceptance/W1-32/**` (4 files).

**Probed and found sound:**
- The planted values are embedded in the stand-in safely: quotes in paths are escaped, and each placeholder appears once.
- The stand-in is written fresh for each launch.
- The stand-in's search uses the root of the vector cache, so it starts with an empty cache. That cache holds only question vectors, never evidence, so it cannot change which store answers.
- The README red-fix paragraphs are prose outside the README tables, and `gov accept` reads only the tables (`src/gov/accept/runner.py:69`). The test ids they name exist.
- Nothing still refers to the removed `SESSION_LOG` or `SESSION_QUESTION`.
- The `sealed_parent` step acts on the one temp folder the session saw, and `temp_folder` checks there is exactly one. If its permission change failed, the stand-in would exit 1 and the cases would go red.

## Findings

Classification: 1 finding, in scope, ordinary work yes, consequence other. Nothing blocks and no round is proposed.

**F1 (w1-32-failed-removal, scope: in).** The opening description of W1-32's launch-support module (`w1_32_launch_support.py:8-17`) still says a plan can ask for "three more things" (sealed, pid, release). This revision added a fourth, the read-only parent (`sealed_parent`), and described it only at `plan` and `stuck_plan`. One more bullet in that list would fix it.
- Ordinary work: yes, because the next designer who reads the module's opening will not learn about the option there.
- Consequence: other. No case's result changes.
- What would reverse it: a line in that opening description (lines 1-23) that names the read-only parent option.

```verdict
{"kpis": [{"kpi": "w2-116-cleaned-env", "verdict": "pass", "findings": []}, {"kpi": "w1-32-failed-removal", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
