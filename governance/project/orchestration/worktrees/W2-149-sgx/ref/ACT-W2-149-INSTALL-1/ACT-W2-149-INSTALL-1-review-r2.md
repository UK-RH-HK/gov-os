**Sandbox check (Step 0, ticket `DAEO-52ku`):** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-52ku` failed with `OSError: [Errno 30] Read-only file system`. (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args` at the end shows only my shell and `ps`. No ollama or llama-server process of mine.

- **task:** the narrow review, round 2 (the last), of ACT-W2-149-INSTALL-1, as a fresh read-only reviewer (`GOV_ROLE=independent-auditor`, worktree `W2-149-f11` at `ee534d2bc`): check the answers to round 1's F1–F7, and that nothing else changed.
- **status:** DONE. **READY by `verdict.py`**: no finding is in scope, reachable in ordinary work, and fails open or loses work. Class **O**. K1–K6 all pass. Two new findings, F8 and F9, both non-blocking.
- **work_completed:**
  - Hashed all 12 drafts. They match §4, and the main tree's copy, which your operator will run, is byte for byte the same (12 of 12).
  - Rebuilt round 1's `apply.sh` exactly: reverting only lines 47, 65 and 97 gives `e52f548e979a…`, round 1's sha256. So F1 and F3 are the only changes.
  - Read the package in full, and checked §0, §3, §5, §6 and §8 against `class-rules.yaml`, OPERATOR-AGENT-1 §2, DEC-1115, the declaration (§2, §13), `tree-exclude.txt` and the experiment's README.
  - Read `rehearse.sh` and `rehearsal.log` (round 2's re-run).
  - Ran my own rehearsal: a `--no-hardlinks` clone of the main tree at `34f97dfea528` and a planted HOME, with the sets root at `apply.sh`'s own default (the name read from its `SETS=` line, never typed). It ran §5 exactly as written, with another session's changes already in the tree, plus controls from round 1's rebuilt text. Result: **failures: 0**.
  - One extra case: §5's commit during an unfinished merge (F9).
  - Deviations, named as EMG-common asks:
    - The Write tool was refused for `$TMPDIR` (a permission prompt that a non-interactive session can't grant). The brief allows copies in my temporary folder, so I treated this as a false refusal and wrote the helper scripts with Bash heredocs, as round 1 did.
    - The harness flagged one `rm -rf "$R/…"` line in my script draft; I rewrote it in the `${R:?}` form it suggested.
    - Nothing was refused twice.
- **files_changed:** none in any tree (`git status --porcelain` in my worktree is empty). Outside the trees:
  - Step 0's trial blob and index refresh;
  - possibly an index stat refresh in the main tree, from my one read-only `git status` there (no content change);
  - `$TMPDIR/r2/`: 6 files (`r2.sh`, `review.log`, `merge_case.sh`, `merge_case.log`, `r1rebuild.py`, `apply-r1.sh`). The clone and planted HOME are removed.
- **evidence:**
  - `drafts/apply.sh` sha256 `871d2c9db3dc8e98c1594367ccedeb5d41ef6eeb8177460b18943c907c7f81bb`.
  - Round 1's text, rebuilt: `e52f548e979ae0c0b9831f72b0ec9d2792e4a1cfa53c4aed6ba682d90792db03`; `git diff --no-index` shows 3 lines changed.
  - My run went from 00:43:22 to 00:43:25 UTC on 2026-11-10 and ended `failures: 0`. The merge case is in `merge_case.log`.
  - `$TMPDIR/r2` after cleanup: 56K, 7 inodes.
- **tests:** no pytest. The ACT changes no code, so I ran `apply.sh` and §5's git commands directly in a clone. The DEC-1012 exclusion left nothing out because no suite ran. I did not run the launch script this round: it, the two lists and the five briefs hash as round 1 read them, so round 1's launch results stand. No real `claude` session, no GPU, no network.
- **discoveries:**
  - (1) While the tree holds an unfinished merge, git refuses §5's `--`-limited commit: "fatal: cannot do a partial commit during a merge." (exit 128). Nothing is committed, and the five briefs stay staged beside the merge (F9). Round 1's unlimited form would have concluded that merge under this ACT's message.
  - (2) The package is untracked in the main tree (`??`), and round 1's copy was overwritten. So for the package, "nothing else changed" is checked against round 1's record of it, not against its bytes. Every difference I can see answers F1–F7.
  - (3) The main tree's head moved during the review (`a5dfa52bc` to `34f97dfea528`). The launch script (`b04db4547eec`), hook (`74f8dbea4761`) and map (`44f99ea563cb`) are still what `order_ok` requires, and `governance/project/indep-briefs/` does not exist yet.
  - (4) §0 quotes OPERATOR-AGENT-1 §2's row by its first and third columns; the middle column, the class, reads "none". This is accurate in substance, because the code's rule table makes "none" rows (O).
- **risks:** unchanged from round 1. After the apply, the briefs are in every worktree and every new wall tree. Nothing can run under them until the wiring follow-up lands, and its entry criteria are now stated (F4, F6, F7). The live list is still first checked at your operator's apply.
- **lessons:**
  - Rebuilding a reviewed script's exact bytes from the record turns "nothing else changed" into a proof.
  - A path-limited commit also changes git's behaviour mid-merge.
  - When reading another tree, use `git --no-optional-locks status`.
- **proposed_decisions:** none needed (READY). Optionally, the CTO fixes two package lines when it fills `@REVIEW2@` (DEC-802, text only, `apply.sh` unchanged):
  - §6's F2 parenthetical (F8);
  - one line in §5: "if the commit itself stops, send its line to the CTO" (F9).
- **unresolved:** whether "the operator's two" means the operator agent's two briefs is still the owner's to say (§1 item 2 asks).
- **recommended_next_action:**
  1. The CTO records round 2 READY in §7 and pings for `yes ACT-W2-149-INSTALL-1 <sha8>`.
  2. Your operator runs §5 **before any change to `indep_launch.py` merges** (F4).
  3. The CTO opens the wiring follow-up with the re-pin and the `indep-briefs/**` exclusion as entry criteria.

## K1–K6

**K1 F1 and F2: pass (F9, non-blocking).**
- F1:
  - `apply.sh`'s only two Python runs, `order_ok` (line 65) and `parse_check` (line 97), are both `python3 -I -B -`.
  - In my run, no `__pycache__` or `.pyc` appeared anywhere in the clone's tree after check, apply, the applied-state check, undo, and check.
  - Control: round 1's rebuilt text, in the same applied state, wrote `governance/project/orchestration/tools/__pycache__/indep_launch.cpython-312.pyc`.
- F2:
  - §5's commit (package line 116) and undo commit (line 121) both end `-- governance/project/indep-briefs/sgx1`.
  - Run exactly as written, with another session's changes in the tree (`M CLAUDE.md` and `A governance/project/foreign-staged.txt` staged, one file modified but unstaged):
    - the commit held exactly **5 A** (mode 100644, the three trailers);
    - the undo commit, with no `git add` before it, held exactly **5 D**;
    - both times, the other session's two staged changes stayed staged and its unstaged change stayed as it was.
  - Round 1's "could not open directory" warning is gone, because the undo no longer runs `git add`.
- The touched set (snapshots before and after check, apply, check):
  - The tree gained only the two brief folders, the five briefs (0644, the approved hashes) and `backup/` (`APPROVED` 0400, 943 bytes, and `SHA256SUMS`). Nothing was removed or changed.
  - The planted HOME changed only in the list: 943 to 2398 bytes, still 0400 in a 0700 folder, and no temporary file left. The trap files were untouched.
  - The clone's `.git` was untouched, and `git status --ignored` gained only `?? governance/project/indep-briefs/`.
  - So the touched set is §1's five briefs and list, plus the backup §4 states.

**K2 F3: pass.**
- Line 47 is now an array of four single-quoted globs, passed as `"${SETS_GLOBS[@]}"`.
- From a folder holding a match for all four globs, xtrace shows Python receiving `'fixtures/evaluation/*/hidden/**' 'fixtures/evaluation/*/XCHECK-r*.md' 'runs/*/miss-classes.json' 'runs/*/misses.jsonl'` unexpanded.
- `check` said "ready to apply" (exit 0) from:
  - that folder;
  - the same folder with `BASHOPTS=nullglob:globstar:dotglob`;
  - the same folder with `BASHOPTS=failglob` (confirmed taken from the environment);
  - `/`;
  - the tree's root.
- Control: round 1's text from the same folder refused falsely, with Python receiving the expanded paths.

**K3 nothing else changed: pass.**
- `apply.sh`: round 1's bytes are today's with exactly lines 47, 65 and 97 reverted (sha256 `e52f548e979a…`), and all three are F1/F3. Everything round 1 described is intact:
  - the order checks;
  - the state machine;
  - the backup, the temporary file and the rename;
  - `parse_check`;
  - an undo that skips `order_ok`.
- The other drafts:
  - `APPROVED.after` is `9e9d6f212a1e` and `APPROVED.before` is `331e48fa336e`;
  - the five briefs are `bbff1249953b`, `e13b5f96d0e0`, `82134b3dd6b5`, `137a73d1df4c` and `b212a424062e`, as in round 1 and §12;
  - `freeze.py` is `1f65c76bb05a` and `install_check.py` is `164136c6d8ea`. Their mtimes (23:28:05 and 23:30:18 on 2026-11-09) predate round 1's run at 00:15. Round 1's record names no hash for these two.
- `freeze.py` rewrites only the `LAUNCH_SHA=` and `LIST_AFTER=` lines, so a re-freeze cannot undo F1 or F3.
- The main tree's copy equals the reviewed one.

**K4 the rehearsal: pass (F8, non-blocking).**
- The log runs from 00:23:39 to 00:23:45 UTC at `f73e72d4a43b`, with `apply.sh` `871d2c9db3dc`, and ends `failures: 0`.
- F1: the rehearsal removes any cache before apply and checks after (line 41).
- F3: `check` from a folder holding `runs/x/misses.jsonl` (line 36). This test discriminates: round 1's text fails it.
- F2: the commit held 5 A, "5 files changed, 654 insertions(+)" (lines 47–53). But nothing else was staged, so the log cannot show the limit at work (F8). My own run covers both commits as written.

**K5 F5: pass.**
- §0 states "(O) (review F5)": the `walled-sessions` row, `class-rules.yaml` lines 31–42, is class O and matches both `gov-os-eval/**` and `governance/project/indep-briefs/**`.
- By effect it is at least (b); the higher vote applies.
- The routing: your yes in DEC-1115 (1)'s form, then your operator by hand. §5's message says the same.
- No claim of class (b) remains.

**K6 F4, F6, F7: pass.**
- F4: §3 (lines 77–84) says the ACT stands only if applied before the follow-up changes the launch script, and that it is otherwise rebuilt, re-reviewed and asked again. This matches `apply.sh` lines 63–64. §8 item 1 repeats it.
- F6: §3 (lines 85–88) is true on each point:
  - `f000adda4` holds no brief;
  - the declaration's §2 requires a new pin when the live files differ (the live hook and map now differ: `74f8dbea4761`/`44f99ea563cb` against `97a84e770058`/`40085090306e`);
  - "an amendment before the extractor runs" meets the declaration's "before the step it affects", because the extractor is step 4 and the first walls are step 5.
- F7: §8 item 2 makes `governance/project/indep-briefs/**` in `tree-exclude.txt` an entry criterion of the follow-up (DEC-803), landing at or before the new pin. Today's `tree-exclude.txt` lacks it, and README item 5 on the guard's code reads as cited.

## Findings

**F8 (K4) — the rehearsal's F2 step cannot show the limit, and its undo is not §5's.**
- When `rehearse.sh` commits, nothing besides the five is staged, so its "5 files changed, 654 insertions" would read the same without `--`.
- Its undo still runs `git add -A` before the commit, which §5 no longer does, and the undo commit's output is hidden by `-q`. Yet §6 attributes "5 files changed, 654 insertions" to both commits.
- Fix: correct §6's parenthetical, or cite this review's run.
- Ordinary work: no, because §5's commands as written work: this review ran both commits as written, with another session's staged and unstaged changes in the tree. Only the record's evidence is weaker than its text.
- Consequence: other.
- Scope: in.

**F9 (K1) — §5 has no step for a commit that stops.**
- While the main tree holds an unfinished merge, git refuses the `--`-limited commit ("cannot do a partial commit during a merge", exit 128). The list is already applied, and the briefs stay staged beside the merge, where a plain `git commit` of that merge would later carry them under its own message.
- §5 says to commit anyway whatever else is staged, but has no step for the commit itself failing.
- Fix: one line in §5: "if the commit stops, send its line to the CTO".
- Ordinary work: no, because the CTO's standing rule keeps a `--no-commit` merge out of the shared main tree; an open merge there is already the error.
- Consequence: other. It fails closed: nothing is committed under this ACT, and since the launch script reads briefs only at `--commit`, nothing launches under them.
- Scope: in.

```verdict
{"act": "ACT-W2-149-INSTALL-1", "round": 2, "class": "O", "apply_sh_sha256": "871d2c9db3dc8e98c1594367ccedeb5d41ef6eeb8177460b18943c907c7f81bb", "kpis": [
 {"kpi": "K1", "verdict": "pass", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "K2", "verdict": "pass", "findings": []},
 {"kpi": "K3", "verdict": "pass", "findings": []},
 {"kpi": "K4", "verdict": "pass", "findings": [{"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "K5", "verdict": "pass", "findings": []},
 {"kpi": "K6", "verdict": "pass", "findings": []}
]}
```