sandbox_check: (a) `open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-141','w')` was refused (`OSError: [Errno 30] Read-only file system`), as required. (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0. Both work.
ps_check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.

task: W2-141 (DAEO-xwro): one-round independent review of `beec1f2f8`. This is the staged `docs/changes/W2-141-hook/pretooluse.py`, rebuilt on ACT-SETS-GLOBS-1's live hook (`74f8dbea4761`), plus its README (DECIDED-NOT-DONE row 78, DEC-1112 (3)).

status: DONE. R1–R4 all pass. There are four findings and none blocks: no finding is in scope, reachable in ordinary work, and fails open or loses work. READY is for verdict.py to compute.

work_completed:
- R1: computed the hashes and both diffs myself.
- R2: read `main()` in the live hook and in the old base, and traced a Glob call through it. Then ran the G-14 suite's hook-driven cases end to end against both the live hook and the staged hook, on planted repositories in my temp folder.
- R3: checked every count in the brief against `rehearsal.log` and `out/`, and re-ran the unit file. Read the scripts behind the evidence (`rehearse.sh`, `replay_globs.py`, `replay_walls.py`).
- R4: checked the README's table, its rebuild note, and its rollback commit, including git attributes and line-ending settings.

files_changed: no tracked file changed (`git status` is clean). Side effects to know about:
- Step 0 wrote one git blob object, as the check requires.
- My pytest run and one inline import check left Python bytecode caches in the worktree's git-ignored `__pycache__` folders: 3 files under `tests/unit/guard/__pycache__/` and about 40 under `src/gov/**/__pycache__/`. I did not delete them, because the rules allow `rm` only inside my temp folder. After that I set `PYTHONDONTWRITEBYTECODE=1` on every run.
- Scratch files went only to `/tmp/gov-launch-xb5jif6f/claude-1000/w2141rev`, now removed.

evidence:
- **Hashes (sha256):**
  - staged `pretooluse.py`: `e7e1c4ce66d66b39eea6c2285cf746e5ae62b65cd6ba89e3a991f04fbeb5ea22`, 61,221 bytes. The same on disk, at integrate's head `8513a4935`, and in the main tree's working copy.
  - live hook: `74f8dbea4761…`, 61,213 bytes. The same at `9cce7430d`, at integrate's head, and in the main tree today.
  - old staged copy: `7c8a6e8d9dbf…`, 33,254 bytes. Its base `15952bbfa`: `bd545af83198…`, 33,246 bytes.
  - `role_reads.py`: staged `b1bc1745f80c…` on both sides of the commit; live `5407aade9417…`, the same at `e02d55e40`.
  - The staged folder is identical to `9536ea954` (`git diff --stat` is empty). No guard file changed between `beec1f2f8` and integrate's head.
- **Scratch use:** 4.2 MB and 811 files and folders (`du -sh`, `du -s --inodes`), then removed.

tests:
- **Unit file:** `tests/unit/guard/test_w2_141_search.py`, run through `heavy_slot.sh` with an empty scratch HOME, `PYTHONPATH=<worktree>/src` and `-p no:cacheprovider`: **204 passed**. No `-m`/`-k` exclusion was needed: it is one file with no real-model cases.
- **G-14 suite, end to end:** a copy of the suite, run against copies of each hook pair in my temp folder (pinned interpreter with `-E`, scratch HOME, call log redirected), selecting `-k "near_misses or true_reads or absent_section"` (117 of 152 cases).
  - Live hook: **117/117 passed**.
  - Staged hook: **113 passed, 4 refused**, exactly the rehearsal's four. Each refusal carries W2-141's own reason, for example "the search can reach tests/acceptance/W2-G14T/, the ticket's own acceptance tests … give a path or a pattern that cannot reach it".
  - The call log recorded the engineer's Glob as `deny`/`g14` and the designer's Glob as `allow`/`none`.
  - The selection left out 35 cases: other path-map sections, the link-source cases, in-process checks of the module beside the suite file, and `test_w2_91_tests_today`, which reads a real worktree. The CTO's rehearsal ran them all, and after staging only the five named cases failed.
- I did not re-run `gov accept W2-141`. It loads the staged `role_reads.py`, which the rebuild did not change, and never the staged `pretooluse.py`.

discoveries:
- **D1 — the live guard refuses `git diff <rev>:<path> <rev>:<path>`.** The reason given is "git cannot say whether a revision holds the hidden part". In `src/gov/guard/reads.py` (`patched()`, around line 1637), every revision word is resolved as a commit (`rev-parse <word>^{commit}`). A blob reference can't resolve that way, so the call fails closed for any role that has hidden parts.
  - Ordinary work: yes, because a reviewer often diffs two versions of a file.
  - Consequence: other. It is a false refusal.
  - I worked round it with the guard's own supported forms: `git show <rev>:<path>` into scratch files, then `git diff --no-index`. Neither form was refused.
  - This is a row for the guard; it is outside R1–R4.
- **Tool refusals and workarounds (DEC-1040 item 3):**
  - The Write tool asked for a permission this non-interactive session cannot grant. It was refused once and I did not retry it. I wrote scratch files with single Bash commands inside the sandbox temp folder, which the brief allows.
  - The first hashes came from an inline `python3 -c` running `git cat-file blob`, which is a form the guard allows. I did this before any refusal.
  - No call was refused twice.
- **The rebuilt hook as a whole is exercised only by the rehearsal and my run.** The unit file runs `role_reads` directly. The acceptance suite runs `role_reads`, and its one whole-hook case (`test_w2_141_calls_dir.py`) runs the tree's live hook, not the staged one.

risks:
- F3 and F4 below.
- After the ACT, every engineer is judged under its own ticket in its own worktree. The replay judged every call under one forced ticket, so it does not count how many calls each other engineer will see refused. The six Bash calls in the window already excluded their own folder (`--exclude-dir=W2-150`, `--exclude-dir=W2-56`), which suggests the volume will be small.

lessons:
- Set `PYTHONDONTWRITEBYTECODE=1` on every Python run in a read-only review. Without it, pytest and inline imports write caches into the tree.
- Under the guard, compare two blobs with `git show <rev>:<path>` into scratch files and then `git diff --no-index`.

proposed_decisions: none needed. Record F1–F4 and D1 as rows.

unresolved:
- For five of the six Bash replay differences, the search's start folder lies past the 100-character cut in the comparison output (140 characters in the replay's JSON). For the sixth (`build_lead_settings`), the second start folder is cut. I could not see them: the full commands are only in the transcripts under `~/.claude`, which is out of bounds. Each one excludes only another ticket's folder, and the guard's reason says it found `tests/acceptance/W2-141/` reachable.
- I did not re-run the rehearsal's sets_globs_check, walls, guard4 or replay steps. They need the planted clone under `~/gov-os-runs`, which the brief keeps me out of.

recommended_next_action:
1. The moderator computes READY from the block below and records F1–F4 and D1 as rows.
2. When preparing the lift's re-pin ACT:
   - check that the live hashes still match the README's table;
   - re-run `rehearse.sh` with `PIN` set to the candidate pin's interpreter (F4);
   - write the steps to commit the copy, and any rollback, and to merge integrate into the live worktrees (F3);
   - name `test_g14`'s four engineer cases in "Before the ACT" (F2).
3. Optional: a replay under each call's own ticket, to see how many refusals other engineers will meet.

## R1: the rebuild is exact — pass
- `git diff --no-index .claude/hooks/pretooluse.py docs/changes/W2-141-hook/pretooluse.py` shows one hunk, at line 1075: `"Grep", "Bash"` becomes `"Grep", "Glob", "Bash"` (8 bytes, matching the size difference).
- The old staged copy against its base (both extracted with `git show`, hashes checked) has the same single line, at line 566.
- So nothing of W2-141 is lost. The unit test pins the same thing: `staged == live.replace(old, new)` with `live.count(old) == 1`.

## R2: both changes hold together — pass
- **The path a Glob takes through the live `main()`:**
  1. rule 2, held-out material (line 998);
  2. rules 2 and 3, the judge with SetsRoot/Narrow parts (1002–1031);
  3. rule 2b's line rule, Bash only (1036);
  4. rule 2b's write rule, writes only (1043);
  5. rule 2c, which already handles Glob (1058);
  6. rule 2d, writes and Bash only (1066);
  7. G-14 (1075).

  Every rule before G-14 can only refuse; none answers allow early. So once Glob is in the list, every Glob not already refused reaches `role_reads.refusal`.
- **What `role_reads` receives is unchanged from the old base:**
  - the call (1078–1080) is the same expression as the old base's 569–571;
  - `seen` is built the same way (Bash: `reads_view`);
  - `tree_roots`, `_tree_roots` and `main_tree` are byte-identical;
  - the ticket, the roles and `_expand_token` are taken the same way;
  - Narrow, the Judge, 2c and 2d only read the tool input, never change it;
  - `record()` runs only after the decision is made;
  - `bash_writes.py` last changed at `3bc25241f` (2026-11-03), before the old base.
- **ACT-SETS-GLOBS-1's cases are unaffected.** Rule 2b refuses and exits before G-14, so its answers and rule ids stay the same; G-14 can only add a refusal.
  - sets_globs_check's output is identical before and after, apart from one "heavy_slot … waiting" line.
  - The 86 replayed calls that name the new globs did not change under either ticket.
- **No new fail-open path, and no wrongly refused Glob found:**
  - errors still fail closed;
  - an engineer's Glob takes about 118 ms against the 20-second deadline;
  - in the end-to-end run, only the four intended refusals differ from the live hook.

## R3: the evidence is real and says what it claims — pass
- **The runs used these files.** The log shows the clone's live hashes (`74f8dbea4761` / `5407aade9417`), the staged hashes (`e7e1c4ce66d6` / `b1bc1745f80c`, equal to the commit), the one-line diff, and the staged hashes again after copying.
- **Every count in the brief matches the log:**
  - sets_globs_check 573/0, walls 331/0, guard4 501/0, before and after;
  - test_guard_fix_4 467/467;
  - live hook and reads 85/85;
  - test_g14: 1 failed before, 5 after;
  - replay of 14,569 unique calls:
    - under DAEO-sdxk, 0 changed;
    - under DAEO-xwro, 29 allow→deny and 0 deny→allow (14,482/87 before, 14,453/116 after);
  - latency median 147.3 → 168.0 ms (noise: orchestrator calls rose as much);
  - live files unchanged, and 0 lines in the live call log;
  - `out/`: guard4 and walls are byte-identical before and after; sets_globs_check differs only by the 61-byte "waiting" line;
  - unit 204, accept 184/0/0 (the per-KPI counts overlap; the total is 184 unique tests).
- **test_g14's four new failures are S1/S2's intended refusals.** All four are engineer searches from above that reach the engineer's own `W2-G14T` folder with no exclusion:
  - "Grep from above0": a Grep of the root (S1);
  - "Glob lists names0": `Glob tests/acceptance/**` (S1);
  - "a search of the whole acceptance folder (from above)": `grep -rn x tests/acceptance` (S2);
  - "grep -r from above": `grep -r foo tests/` (S2).

  The designer's Glob and Grep cases still pass. My own run reproduced the same four, with their reasons.
- **The 29 replay differences are all intended refusals.** Every one is an engineer call (acting role none), refused with "the search can reach tests/acceptance/W2-141/". Nothing else changed.
  - **23 Grep calls,** named by where they start:
    - W2-20 worktree: `tests/acceptance`, the root, and `tests` twice;
    - W2-141 worktree: the root;
    - W2-150 worktree: the root four times, and `tests` four times;
    - W2-153 worktree: the root twice;
    - W2-92-d6 worktree: the root;
    - W2-56 worktree: the root twice;
    - W2-152 worktree: the root three times;
    - W2-55-f2 worktree: the root;
    - `.` (the call's own folder).
  - **6 `grep -r` calls:** five with `--exclude-dir=W2-150`, one with `--exclude-dir=W2-56` (`build_lead_settings`). Each excludes another ticket's folder, not W2-141's.
- **Where the rehearsal differs from the operator's ACT:**
  1. It copied the pair into a clone and one of its worktrees. The ACT copies into the main tree, and each real worktree keeps running its own hook until integrate is merged into it.
  2. It used today's pin (`pin-bcea09060ebc`); the ACT lands at the re-pin (F4).
  3. The sets root and HOME were planted for sets_globs_check and walls, guard4 ran with the root planted, and the call log was redirected.
  4. The replay used the clone as every call's project root and forced one ticket, not each call's own tree and ticket.
  5. The README's rollback was not rehearsed; I checked it by hashes.
  6. "failures: 0" counts only prepare, stage, sets_globs_check, walls, guard4, the replay's exit and the live-file check. The suites and the replay comparison are never counted (F2).

## R4: the README — pass
- **The table is right:** `5407aade941734c086aefefe5372e715262aedc1805380f9427b068eb2444f07` for `role_reads.py` and `74f8dbea4761de37628305e5d58125641ae39a409a7ed0a2babb379b1ceca5b8` for `pretooluse.py` are the live files at `beec1f2f8`, at integrate's head, and in the main tree today.
- **The rebuild note is right but incomplete** (F1).
- **The rollback is right:**
  - Commit `9cce7430d8f617eccabc48a7f7df7346c40a7602` holds blobs `33f0a75b4b22` and `446c2e2b6915`, the same blobs as today's live files.
  - It is the last commit that changed `pretooluse.py`; `role_reads.py` last changed earlier, at `e02d55e40`.
  - No git attributes apply to these paths, and there is no `core.autocrlf`, `core.eol` or filter setting anywhere.
  - So `git checkout 9cce7430d… -- …`, or copying back the kept files, restores both files byte for byte, and step 3's hash check then passes.

## Findings
**F1** (R4, scope: in): the README's rebuild note says the first copy lacked "rule 2b's glob line, rule 2c and rule 2d". The first copy (`bd545af83198`) also lacked ACT-GUARD-CALLLOG-1's call log (`record()`, the rule argument of `answer()`) and ACT-SETS-GLOBS-1's `Narrow`. The commit message names all four ACTs.
Ordinary work: no, because nothing anyone does from the README depends on this list: the copy to apply carries both, and the table, the one-word diff and the rollback are right.
Consequence: other

**F2** (R3, scope: in): the record says "rehearsal 0 failures", but `rehearse.sh`'s `suites` step never counts a failure and the comparison's exit code is ignored. test_g14 went from 1 to 5 failed, which the commit body never mentions (it omits the suites). The README's "Before the ACT" names test_live_hook's revised case and guard4's case G5, but not test_g14's four engineer cases.
Ordinary work: yes, because the next rehearsal or the person preparing the re-pin ACT runs test_g14 as a regression suite, as both recent rehearsals did, and would meet four unexplained "new" failures.
Consequence: other

**F3** (R4, scope: out; this text predates the rebuild, which changed only the hash): the rollback covers only the tree the ACT applies to. It does not say to commit the rollback and merge it into the worktrees, each of which runs its own copy of the hook. ACT-SETS-GLOBS-1's undo does say to commit.
Ordinary work: yes, because a rollback is a planned step and the ACT's commit reaches the worktrees by merge.
Consequence: other (worktree sessions would keep the stricter staged hook until a rollback is merged; nothing fails open).

**F4** (R3, scope: out; it concerns the re-pin): the rehearsal ran the staged pair with today's pin, but the pair goes live together with a new pin, and that combination was never rehearsed. Integrate's source still has every name and signature the hook takes from the pin, so nothing is missing today.
Ordinary work: yes, because the re-pin is the planned path.
Consequence: other (a missing name would refuse every call, failing closed).

```verdict
{"staged_pretooluse_sha256": "e7e1c4ce66d66b39eea6c2285cf746e5ae62b65cd6ba89e3a991f04fbeb5ea22", "kpis": [{"kpi": "R1", "verdict": "pass", "findings": []}, {"kpi": "R2", "verdict": "pass", "findings": []}, {"kpi": "R3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "R4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```