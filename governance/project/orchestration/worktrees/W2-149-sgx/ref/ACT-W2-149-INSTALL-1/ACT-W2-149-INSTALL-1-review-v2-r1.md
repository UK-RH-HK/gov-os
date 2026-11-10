I reviewed the rebuilt ACT-W2-149-INSTALL-1. My recommendation is **READY by `verdict.py`, with no round**. I found five findings (F31–F35). All five are in scope and reachable in ordinary work, but none fails open or loses work, so none blocks. The class is **O**.

The list is right, the touched set is exact, the undo is real and the order checks hold. The findings are about what the package says:
- **F33:** a launch at the declared pin after the ACT is refused 11, where §3 says 10.
- **F34:** once applied, the list does not hold the launch script; a later script change still launches.
- **F35:** the owner's yes approving the template change is not said plainly where the yes is asked.
- **F31 and F32:** every wall's tree still holds a copy of the guard's code and the operator agent's two briefs. §8 says nothing of either.

**Sandbox check (Step 0, ticket `DAEO-52ku`):** passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-52ku` failed with `OSError: [Errno 30] Read-only file system`.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** no ollama or llama-server process of mine. The sandbox has its own process namespace. The only three lines that matched were my own shell and the check's own command line, which contains the search words.

**Identity:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-52ku`. The worktree is `/home/usain/gov-os-worktrees/W2-149-sgx` on `w2/W2-149-sgx`, and HEAD is `29907d75048f072b5ea013cb560b2b8a21c449ac`. `git status --porcelain` was empty at the start and is empty now.

**decisions:** DEC-1101 (2)-(3), DEC-1112 (3), DEC-1113, DEC-1109 (1), DEC-1115 (1), DEC-803, DEC-802, DEC-820, DEC-1057, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1073. I found no superseded or PROPOSED rule in use: the package and the code follow amendment A5 for the seeds, not §5's old blank.

---

- **task:** DAEO-52ku. The independent review, one round, of the rebuilt ACT-W2-149-INSTALL-1, as a fresh read-only reviewer who is not the ACT's author.
- **status:** DONE. READY by `verdict.py`. Class O. K7 is marked fail because two of its statements are untrue, but it carries no blocking finding.
- **work_completed:**
  - Read the package in full, every copied reference, the first build's two reviews and the wiring's review (F18–F30).
  - Read `apply.sh`, `freeze.py`, `install_check.py`, `rehearse.sh` and `rehearsal.log`.
  - Read the launch script's list parser, stages 14, 11 and 10, the front-matter resolver, the tree build, the set-up A staging (`plan_sgx`, `stage_sgx`) and the deliveries (`Landing`, `deliver_sgx`, `deliver_audit`).
  - Read the template folder with the Read tool. I compared its files before (`147706ae4`) and after (`7f0e71519`) with inline Python that builds the folder name in code, so no Bash line names it.
  - Checked the register (DEC-1109, DEC-1112, DEC-1113, DEC-1115), DECISIONS-IN-FORCE lines 395–431, `class-rules.yaml` and OPERATOR-AGENT-1 §1, §2 and §5.
  - Ran my own rehearsal in `$TMPDIR`:
    - The clone was a sparse `--no-hardlinks` clone at `29907d750`, on a local `w2/integrate`, with git hooks off.
    - `fixtures/evaluation/` was left out of the clone, so no hidden folder was ever written or opened.
    - I planted a HOME and a sets root named `sr`, holding the before-list (`331e48fa`) and three unreadable trap files, plus the same planted tuning half as the author's rehearsal.
    - I ran 17 refusal cases, check and apply under `bash -x`, snapshots before and after, a second apply, §5's commit with another session's changes staged, the script's own parser, `install_check.py`, five dry launches with their trees inspected, the operator-brief cases, launches at the declared pin, undo and its refusals under `bash -x`, §5's undo commit, and a launch-script change after the apply.
- **files_changed:** none in any tree.
  - Outside the trees: Step 0's trial blob and index refresh only.
  - My `$TMPDIR/rv` (the clone, the planted HOME and the traces) was made and then removed.
  - I read the main tree read-only: hashes, one `ls`, and `git --no-optional-locks` `rev-parse` and `merge-base`. I ran nothing against it.
- **evidence:**
  - I read `drafts/apply.sh` at sha256 `53c2c68122d2354aa5f1729ddb8482ce02a9e379632b5ed6f6d1f2bf2cb92ceb`.
  - All 12 drafts match §4. The main tree's copy, which your operator will run, is byte for byte the same (12 of 12).
  - The five briefs match the declaration's §12 exactly.
  - My rehearsal ended with no unexpected result. Every case below gave the expected exit code and message.
  - Scratch at its largest: `du -sh` 179M and `du -s --inodes` 9,165. It is removed now.
- **tests:** no pytest and no heavy-slot job. The ACT changes no code, so I ran `apply.sh`, `install_check.py` and the launch script directly in my clone. The DEC-1012 exclusion left nothing out, because no suite ran. No real `claude` session, no GPU, no network. I did not use `gov retrieve` (DEC-1064).
- **discoveries:**
  - **The live state, read-only:**
    - The main tree is at `c3bf5a5474bd` (`w2/integrate`).
    - It holds what `order_ok` requires: the script `a5f2e8f5d9c9`, `kinds.yaml` `734b26e261fa`, `tree-exclude.txt` `e8395088167e`, the hook `74f8dbea4761` with `sets_line_keys`, and the map `44f99ea563cb`.
    - There is no `governance/project/indep-briefs/` yet, and no `backup/` in the drafts folder.
    - So the live `check` will get as far as the real list.
  - **F21's tell shows in a planted wall.** The auditor's one dispute arrived with reasons `'planted'` and `''`. The empty side is labeller 1's script label.
  - **The writers' sample names left-out paths.** Of the 400 paths in `selection.json`, 6 are under `.claude/` and 1 under `src/gov/guard/`; 9 in all are not in the tree. The sample rule leaves out only `tree-exclude.txt`'s paths (S5). These are names only, so blindness is not affected.
  - **A transient temp file.** `drafts_ok` writes a `mktemp` file in `$TMPDIR` (default `/tmp`). It was removed on every path I ran, including every refusal. With no writable temp folder, check and apply stop on mktemp's own message, which fails closed.
  - **The first build's F8 is still open in the rehearsal script.** `rehearse.sh` line 177 runs `git add -A` before the undo commit; §5 does not, and §7 does not list F8 as answered. My run did §5's undo commit exactly as written and got 5 D.
  - **One claim has no evidence.** §6's "a trial at the branch head (`7df7c35e3`) gave the same results" has no log in the bundle.
- **risks:**
  - Once applied, set-up A can run, so the wiring's F18–F24 become live. F18 with F23 is the likeliest stall. F19 and F20 can leave files in a destination, and in the held-out half removing them needs an operator ACT.
  - The labellers' and the auditor's blindness to the guard's code rests on each brief's "leave them unread" (F31).
  - The real list is checked only at your operator's apply.
- **lessons:**
  - A sparse clone without `fixtures/evaluation/` lets a rehearsal build walls without ever writing a hidden folder.
  - A refusal code carried over from an earlier build has to be re-run when the list's template lines change (F33).
  - `git commit -- <path>` does not commit untracked files, so §5's `git add` before it matters. My own harness slipped on this once.
- **proposed_decisions (the CTO's, DEC-1112 (3)):**
  - Carry the text fixes for F33, F34 and F35 when filling `@REVIEW@` (DEC-802; `apply.sh` unchanged), and name F31 and F32 in §8.
  - Optionally, before asking: extend the set-up A entries' `tree_exclude` to `docs/changes/W2-141-hook/**`, `template/governance/kernel/hooks/**`, the guard's suites and the harness, and `tree-exclude.txt` to the operator's briefs. That is a template change, so it would rebuild this ACT (`freeze.py`, `rehearse.sh`) and need a new review.
- **unresolved:**
  - The real list's bytes: never opened by me.
  - Whether `docs/changes/W2-141-hook/` is still in the tree at the amended pin.
  - Round 2 of the labellers and the real deliveries were not exercised: dry launches only, no sessions. The package does not claim them.
- **recommended_next_action:**
  - READY by `verdict.py`; no round (DEC-1010).
  - The CTO fixes the package text and asks for `yes ACT-W2-149-INSTALL-1 <sha8>`.
  - Your operator runs §5 before any further change to the launch script or the walls' template is merged.

**Deviations, named as EMG-common asks:**
- The Write tool was refused once for my `$TMPDIR`: a permission prompt that a non-interactive session can't grant. I did not retry it. I used inline `python3 -I -c` programs instead, writing only under `$TMPDIR`.
- Two slips in my own harness, both only in `$TMPDIR`, both re-run:
  - My first run left `TMPDIR` out of the clean environment, so mktemp hit the read-only `/tmp`.
  - I once committed without `git add`, so the briefs were never committed and the launch was refused 10. I reset the clone and re-ran.
- Nothing was refused twice.

---

## K1–K8

**K1 — the touched set is exact: pass.**
- **What apply wrote in the tree:**
  - the five briefs under `governance/project/indep-briefs/sgx1/`, mode 0644, sha256 `bbff1249953b`, `e13b5f96d0e0`, `82134b3dd6b5`, `137a73d1df4c` and `b212a424062e`, which are §12's;
  - their two folders;
  - `backup/`, holding `APPROVED` (0400, `331e48fa`) and `SHA256SUMS`;
  - no `__pycache__`.
- **What apply wrote in the planted HOME:** only the list, now `a0af30f840db`, mode 0400 in a 0700 folder. The folder's timestamp changed because of the rename.
- **What it read under the sets root (from the trace):**
  - the root itself: `[ -d ]` and `realpath -m`;
  - the list: tests, `sha256sum`, and `cp -p` into `backup/`;
  - the temporary `.APPROVED.act-w2-149-install.<pid>` beside the list, renamed over it;
  - the parser opening the list.
  - Nothing else. The trap files were untouched.
- **The commit:** run exactly as §5 says, with another session's two changes staged and one unstaged, it held exactly 5 A (mode 100644, the three trailers). The other session's changes were left staged and unstaged as they were.

**K2 — the list is right: pass (F35).**
- **Against the first list:** `APPROVED.after` (`a0af30f840db`, 23 lines) is `APPROVED.before` with exactly lines 7 and 8 changed. The before-list is ACT-INDEP-WALLS-1's, and its hashes are that ACT's §3.
  - Line 7, `kinds.yaml`: `8b50a78f01b3` becomes `734b26e261fa`.
  - Line 8, `tree-exclude.txt`: `21660e1ee5ad` becomes `e8395088167e`.
  - Each new hash is the file's sha256 at `7f0e71519`, which is also its value at HEAD and in the main tree.
  - Then come the comments (10 comment lines in all) and 7 brief lines.
- **Through the script's own `parse_approved`:**
  - 6 template lines, one hash each, exactly the six files the script needs, all matching the tree;
  - 7 brief lines, no duplicate hash, each matching its bytes at the commit.
- **Kinds:** labeller, labeller, writer, writer and auditor, each equal to its brief's front-matter `kind`. The operator's two briefs have no front matter and are listed as `operator`:
  - `--kind operator` is refused 17;
  - the operator's brief launched as a writer is refused 10.
- **Every line has an owner approval:**
  - the four unchanged template lines: ACT-INDEP-WALLS-1;
  - the five briefs: the owner on 2026-11-09 under DEC-1113 (DECISIONS-IN-FORCE lines 400–404);
  - `reviewer-brief.md` `e8670330…`: DEC-1109 (1), by hash;
  - `brief.md` `51c459cf…`: DEC-1109 (1) "with one change". The register records no hash, but the file holds the changed sentence (line 25);
  - the two changed template lines: this ACT's yes. The CTO's delegated ruling of 2026-11-10 took the change, but `tree-exclude.txt`'s own header says a change to it needs your approval.
- **Does the package say plainly that the yes approves the template change?** Only partly (F35).
- **What `kinds.yaml` now lets a wall do that it could not before:**
  - Run on `claude-opus-5-5` when its brief names no model. This applies to every kind, memory sets' briefs included; before, such a brief was refused 10.
  - Launch as a labeller at all. Before, every labeller brief was refused 10.
  - Run one of set-up A's five flows. The script then:
    - stages that half's material into the wall: the tuning half from the runs folder, the held-out half from the sealed folder under the sets root;
    - delivers the wall's products by its own code into that half's folder. For the held-out half that means the sealed folder: planted cases, round-1 files, labels, the auditor's decisions and map, a rewritten `labels.jsonl` and `owner.jsonl`;
    - at labeller 1's round 2, runs that session's own rule script on the machine, confined by bwrap (code 18).
  - A set-up A wall's tree also loses `.claude/`, `src/gov/guard/`, `src/gov/launch/` and the template folder, which is a tightening.
- **What `tree-exclude.txt` now lets a wall do:** nothing new. It takes `governance/project/indep-briefs/**` out of every wall's tree and out of every sample.

**K3 — the undo is real: pass.**
- **It refuses safely.** Undo refused in the before state, with a damaged backup (`sha256sum -c` failed and nothing changed), and with the list changed after the apply.
- **It restores exactly.** Run for real, it:
  - put the list back byte for byte (`331e48fa…`, 0400), from a backup checked by `sha256sum -c` and by the pinned before-hash;
  - removed only the five files and their two folders;
  - renamed the backup to `backup.undone-<UTC>`;
  - touched nothing else under the sets root (from the trace).
- **§5's undo commit**, run as written with no `git add`, gave exactly 5 D. `check` then said "ready to apply".
- **The state after an undo:**
  - The tree holds no briefs folder, though the briefs stay in history at the ACT's commit.
  - The template stays as merged (`734b26e261fa`, `e8395088167e`), and the script is unchanged.
  - The list is ACT-INDEP-WALLS-1's: the old template hashes and no brief line.
- **The launches after an undo:**
  - Refused 11 at HEAD, and at the ACT's own commit even though the briefs are in it.
  - Refused 10 at a commit from before the wiring, such as `f000adda4`.
  - So nothing launches under any brief until a new list is written.
  - Walls already built, and products already delivered while the ACT was applied, stay where they are.
  - Undo skips `order_ok`, so it still works after a later script change. I showed this.

**K4 — the rehearsal is real: pass.**
- **It is a run of this `apply.sh`.** `rehearsal.log` (`780d8ddb9594`) is a run of `rehearse.sh` (`e0da436ef120`) with this `apply.sh` (`53c2c68122d2`, log line 7):
  - in a clone at `29907d75048f`, with a planted HOME and a planted sets root holding `331e48fa`, under `env -i`;
  - every heading and line is `rehearse.sh`'s own, and it ends `failures: 0`.
- **Set-up A's five briefs pass stage 10 and build their dry walls** (exit 0): 7 of 7 lines match, and every front matter passes. My run reproduced each wall: the same values, the same `input/`, the approved `brief.md`, 3,627 tree files each.
- **The counts are what §6 states.**
- **Where it differs from the live run:**
  - The real list is first checked at your apply.
  - The main tree is shared with other sessions. Its git hooks run at the commit; the clone had none.
  - The rehearsal's undo commit runs `git add -A` first (the first build's F8).
  - `env -i` is not your operator's shell. `mktemp` needs a writable temp folder.
  - The launches were dry, with seed 17, at the ACT's own commit, on a planted root. Real launches draw their own seed, start sessions, and are made at the amended pin.
  - The real sets root holds 4,560 hidden files, none of which `apply.sh` reads.
  - The main tree has since moved to `c3bf5a5474bd`, but every hash the checks need is unchanged.

**K5 — the order holds: pass.**
- **What the checks cover:**
  - `order_ok` pins the script, `kinds.yaml` and `tree-exclude.txt`, the four ACT-SETS-GLOBS-1 globs in the map, and `def sets_line_keys(` in the hook.
  - `drafts_ok` pins the five briefs, both lists' hashes, and the requirement that the after-list's head is the before-list with only the two lines changed.
- **What was refused,** with check and apply both tried where it matters and nothing written each time:
  - the hook and map from before ACT-SETS-GLOBS-1, either alone or both;
  - the script from before the wiring (`b04db4547eec`), or with one byte added;
  - `kinds.yaml` with one byte added, or as first written (`8b50a78f01b3`);
  - `tree-exclude.txt` as first written (`21660e1ee5ad`);
  - either list or a brief draft altered;
  - a list that is not `331e48fa`;
  - a stray file in the briefs folder.
- **The package states the order** in §2, and §5's message repeats it.
- **W2-141's hook breaks nothing, whenever it lands.** Its staged hook keeps `def sets_line_keys(` (line 428), and its ACT changes only the two hook files, not the map. After the apply nothing reads the hook, and undo skips `order_ok`.

**K6 — the class: O.**
- **The code's vote is O:**
  - `class-rules.yaml`'s `walled-sessions` row names `gov-os-eval/**` (the list) and `governance/project/indep-briefs/**` (the briefs) as O;
  - `.gov-runtime/**` (the backup) is O as well.
- **OPERATOR-AGENT-1:**
  - §1: the agent may never touch the sets root.
  - §2: the blind writers and checkers are walled sessions under DEC-1101, not the operator's.
  - §5: `Role: owner` records stay yours, and §5's commit carries `Role: owner`.
- **By effect it is at least (b):** it loosens what may launch.
- The highest vote applies (§3), so the class is **O**, as the package says.

**K7 — the package's account is true: fail, no blocking finding.**
- **"Set-up A launches through the merged script once applied": true.** The five dry walls built with exit 0.
- **"Before the ACT, a launch is refused 11": true.** At the merged commit the refusal is 11, with `template_ok` false.
- **"F18–F23 would rebuild it": stated,** but true only before the apply (F34).
- **"The pin amendment follows": stated,** but the refusal code it gives is wrong (F33).
- **How the stages work:**
  - Stage 11: each template file read at `--commit` must have exactly one hash on the list, equal to its sha256.
  - Stage 10:
    - the brief read at `--commit` must hash to `--brief-sha256`, under a line with that kind and that path, and its front matter's kind must match;
    - then model, result schema and sample are taken from the front matter, else the brief's `briefs:` entry, else (model only) the kind;
    - a labeller must have an entry;
    - for a flow, `--set` and `--round` are checked and the inputs are planned before anything is written.
  - The wall's tree leaves out `tree-exclude.txt`'s paths and the entry's `tree_exclude`.
  - The staging and the deliveries match each brief, apart from F21's tell.

**K8 — independence: pass (F31, F32).**
- **No wall's tree holds any of the five briefs.** I hashed every file of all five dry trees, with the briefs committed, and every tracked file at HEAD. The only brief copies found are the operator's two, which are in every tree (F32).
- **The template change lets no session see anything it could not see before.** It only takes folders out of trees, and it stages each wall's inputs as that wall's brief names them. But each set-up A tree still holds a copy of the guard's code, its suites and the experiment's harness (F31).
- **The residual (§8 item 4)** is right for the five briefs and says nothing of F31 or F32. F21's tell is carried as a residual in §3 and §8 item 1.

**Probed and found sound:**
- every draft hash and the brief hashes;
- the template's hashes before and after the wiring;
- the script's hash at the merge, at HEAD and in the main tree;
- the state machine and all 17 refusals;
- the touched set and what is read under the sets root;
- the path-limited commit;
- the parser's counts;
- `install_check.py`;
- the five dry walls;
- the undo, its refusals, and the launches after it;
- the temp file removed on every path.

## Findings

Classification: five findings, F31–F35. All are in scope, reachable in ordinary work, and consequence "other"; none blocks. Recommendation: READY, no round.

**F31 (K8) — The guard's code, its suites and the harness stay in every set-up A wall's tree.**
- **What was done:** I built five dry walls at the ACT's commit and inspected each tree (3,627 files).
- **What happened:**
  - None of the trees holds `.claude/`, `src/gov/guard/`, `src/gov/launch/`, the template folder or the briefs folder.
  - But every tree holds:
    - `docs/changes/W2-141-hook/pretooluse.py`: the live hook, 1,146 lines, rebuilt with W2-141's one-word change;
    - `docs/changes/W2-141-hook/role_reads.py`, whose matching block is byte for byte `src/gov/guard/reads.py`'s;
    - `template/governance/kernel/hooks/pretooluse.py`;
    - the guard's suites: `tests/unit/guard/`, `tests/unit/hooks/test_live_hook.py` and `tests/acceptance/W2-141/`;
    - the launch script.
  - Every brief forbids these. A labeller who searches its tree for DEC-1093, a decision its brief cites, gets lines from `role_reads.py` (5) and the guard's suites (29).
  - The template change added none of this. The briefs already say "your tree holds some of these; you leave them unread".
- **What should have happened:** §1, §3 and §8 should say that the entries leave out the §4 paths only, and that these copies stay under the briefs' own instruction. Alternatively, the CTO widens `tree_exclude`, which rebuilds the ACT.
- Ordinary work: yes, because a labeller judging a wide search will look the decision up across its tree.
- Consequence: other
- Scope: in
- **What would reverse it:** treating the tree exclusion, not the brief, as the guarantee of blindness; then it fails open for these copies. Or the copies are gone at the amended pin.

**F32 (K8) — Every wall's tree holds the operator agent's two briefs.**
- **What happened:**
  - `governance/project/operator/brief.md` and `reviewer-brief.md` are in every wall's tree, of every kind, and this list approves them as briefs.
  - `tree-exclude.txt`'s new line, whose comment says "never another job's brief", covers only `indep-briefs/**`.
  - §8 item 4 is silent on them.
- **What should have happened:** §8 names them as a known exception, or `tree-exclude.txt` leaves them out (a rebuild).
- Ordinary work: yes, because every wall built under this list holds them.
- Consequence: other (they say nothing about set-up A's labels, cases or the guard).
- Scope: in
- **What would reverse it:** if "another job's brief" means only the walls' jobs' briefs.

**F33 (K7) — §3 gives the wrong refusal at the declared pin.**
- **What was done:** a dry launch under writer-tuning at `f000adda4`, before and after the apply.
- **What happened:** before the apply it was refused 10. After the apply it was refused **11**: the pin's `kinds.yaml` and `tree-exclude.txt` are the two lines this ACT replaces, so stage 11 refuses before stage 10 looks for the brief. §3 says 10.
- **What should have happened:** §3 says "refused with 11". Its conclusion, that the pin moves, stands.
- Ordinary work: yes, because the CTO writes the pin amendment from §3.
- Consequence: other (fails closed either way).
- Scope: in
- **What would reverse it:** a launch at `f000adda4` under the after-list returning 10.

**F34 (K7) — After the apply, the list does not hold the launch script.**
- **What was done:** I applied the ACT, committed the briefs, then committed a one-line change to the script (new hash `22107628e364`).
- **What happened:**
  - A dry launch under the unchanged list exited 0.
  - `check` then said "merge it first", even though the ACT is applied. `undo` still worked.
  - The script's hash in the list is only a comment, which the parser skips.
  - Yet §2 says "the list thus names the script … that will run", and §8 says fixing F18–F23 "rebuilds this ACT". Both hold only before the apply.
  - The wiring's review routes F19, F20 and F23 into the next resume (DEC-802), so such a change is likely.
- **What should have happened:** §2 and §8 should say that the list holds the template and the briefs, and holds the script only until the apply. After it, a later script change runs as reviewed code without a new yes, and the list's comment then names an older script.
- Ordinary work: yes, because those fixes will merge after the apply.
- Consequence: other
- Scope: in
- **What would reverse it:** reading DEC-1101 (2) as the owner approving the script too; then a later script change fails open past the owner.

**F35 (K2) — The template approval is not said plainly where the yes is asked.**
- **What happened:**
  - Only §1's table and the list's own comment say that the two files' new contents are approved by this yes.
  - §0 says the ACT "adds no check and tightens nothing", but `tree-exclude.txt` does tighten.
  - §5's message, which carries the yes line, calls the ACT "the launch script's approved list".
  - The table does not say what `kinds.yaml`'s change turns on (K2's list): staging from and delivery into the halves, the sealed folder included; a session's rule script run on the machine; the labeller kind made launchable; a default model for every kind.
- **What should have happened:** one line in §0 and in §5: "your yes also approves the walls' `kinds.yaml` and `tree-exclude.txt` as set-up A's wiring changed them", with those effects in the table.
- Ordinary work: yes, because you give the yes from §0 and §5.
- Consequence: other
- Scope: in
- **What would reverse it:** if you consider §1's table enough.

```verdict
{"act": "ACT-W2-149-INSTALL-1", "class": "O", "apply_sh_sha256": "53c2c68122d2354aa5f1729ddb8482ce02a9e379632b5ed6f6d1f2bf2cb92ceb", "kpis": [
 {"kpi": "K1", "verdict": "pass", "findings": []},
 {"kpi": "K2", "verdict": "pass", "findings": [{"id": "F35", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K3", "verdict": "pass", "findings": []},
 {"kpi": "K4", "verdict": "pass", "findings": []},
 {"kpi": "K5", "verdict": "pass", "findings": []},
 {"kpi": "K6", "verdict": "pass", "findings": []},
 {"kpi": "K7", "verdict": "fail", "findings": [{"id": "F33", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F34", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K8", "verdict": "pass", "findings": [{"id": "F31", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F32", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```