- **sandbox_check:** Passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-52ku` failed with `OSError: [Errno 30] Read-only file system`, as required. (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0. Launched as `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-52ku`.
- **ps_check:** I ran `ps -eo pid,args` on its own (no pipe, DEC-1080). It shows only my shell and `ps`: no ollama or llama-server process of mine.
- **task:** DAEO-52ku. The independent, read-only, one-round review of ACT-W2-149-INSTALL-1's third build, on `w2/W2-149-sgx` at `9f66e4084b44496566114d114b96e620f86fcd05`. I am not the ACT's author.
- **status:** DONE. READY by `verdict.py`: no finding is in scope, reachable in ordinary work, and fails open or loses work. Class O. I marked K8 fail because §3's account of F36 leaves out where the auditor's blind actually rests (F38, a text fix). Nothing blocks.
- **work_completed:** I read the package in full; the copied references (ACT-INDEP-WALLS-1, the two W2-149 reviews, the second build's review, the declaration's §12 and A5); JUDGEMENT.md; and the overlap auditor's and labellers' briefs. I read `apply.sh`, `freeze.py`, `install_check.py`, `rehearsal.log` and both trial logs. I compared every draft with `drafts-v2-reviewed/`, and this package with its committed second-build text. I read the launch script's list parser, stages 11 and 10, the resolver, the tree build, set-up A's staging and deliveries, and its whole `7f0e71519`→`90c1fea6c` diff. I read `kinds.yaml` and `tree-exclude.txt` with the Read tool. I checked the register (DEC-1099, DEC-1109, DEC-1112, DEC-1113, DEC-1115), DECISIONS-IN-FORCE lines 390–443, `class-rules.yaml` and DECIDED-NOT-DONE row 75. I ran four in-memory probes with the launch script's own code, and one targeted reproduction (F39) with this `apply.sh` in a sparse clone in my `$TMPDIR`.
- **files_changed:** None in any tree. `git status --porcelain` was empty at the start and is empty now; HEAD was `9f66e4084` both times. Outside the trees: Step 0's blob and index refresh only. My `$TMPDIR/rv3` (the clone, a planted HOME and a planted sets root) was made and then removed. I only read the main tree: hashes, two `ls`, Grep and Read. I ran nothing against it.
- **evidence:** I read `drafts/apply.sh` at sha256 `e3943ad4e243b41ef4e6b7f4081d59e556a84ed4cc7960640f0d3a1e5fd22b55`. All 14 files in `drafts/` hash as §4 states, and the main tree's `drafts/w2-149-install/`, which your operator will run, holds the same 14 byte for byte. The launch script is `95fe78dd…` at `90c1fea6c`, at HEAD, at integrate's head `b5c23e7b3` and in the main tree. The six template files at `7f0e71519`, `90c1fea6c` and HEAD each equal their line in the after-list. Scratch at its largest: `du -sh` 194M, `du -s --inodes` 10,663; now removed.
- **tests:** No pytest and no heavy-slot job, because the ACT changes no code. I ran `apply.sh` (check, apply, undo) and the launch script's own functions directly, only in my clone. The DEC-1012 exclusion left nothing out, because no suite ran. No real `claude` session, no GPU, no network, and no `gov retrieve` (DEC-1064).
- **discoveries:** (1) w2/integrate has moved to `b5c23e7b3`. Its two new commits touch neither the script, the template, the schemas nor the operator's briefs, so the live `check` still gets as far as the real list. (2) The tell is already written plainly in files on w2/integrate: W2-149's ticket (`c17edb833`) and the committed second-build package (F38). (3) DECIDED-NOT-DONE row 75 and the committed package still name the second build's yes, `0edc1eb9`; no yes is recorded anywhere. (4) The second build's trial log hashed 18 live-file lines, against 23 in its run; this build's trial and run match exactly.
- **risks:** Once this is applied, set-up A can run, and F36 and F37 go live with it. For the copies of the tell that sit in its tree, the auditor's x/y blind rests on its brief's "never read any package, draft or ticket file" (F38). The real list is checked only at your operator's apply.
- **lessons:** Reviewing a blind means checking what the project's own records will say at the pin: a package that names a blind's limit lands in the very tree it describes. `check` and `apply` should test the same things before the first write.
- **proposed_decisions:** For the CTO (DEC-1112 (3)): carry F38 as a text fix to §3 and §8 when filling @REVIEW@ (DEC-802). Optionally, add `.tickets/**` and `governance/project/orchestration/packages/**` to the overlap auditor entry's `tree_exclude`; its tickets arrive in `input/`. That is a template change, so it would rebuild this ACT. F39 is a row.
- **unresolved:** I never opened the real list. Labeller round 2, real deliveries and real sessions were not exercised: dry code only, and the package does not claim them. Whether the auditor's tree-wide search would actually surface the ticket's line among its other hits is untested, because no session was run.
- **recommended_next_action:** READY by `verdict.py`; no round (DEC-1010). The CTO carries F38 into §3 and §8, fills @SHA8@ and @REVIEW@, moves row 75's yes line to the new sha8, then asks for `yes ACT-W2-149-INSTALL-1 <sha8>`. Your operator runs §5 before any further change to the script, the template or the operator's briefs is merged.

**Identity:** HEAD `9f66e4084b44496566114d114b96e620f86fcd05` on `w2/W2-149-sgx`; the tree was clean at the start and is clean at the end.
**decisions:** DEC-1101 (2)-(3), DEC-1112 (3), DEC-1113 (2), DEC-1109 (1), DEC-1115 (1), DEC-1099 (1) Q5, DEC-820, DEC-1057, DEC-801, DEC-802, DEC-808, DEC-1010, DEC-1014, DEC-1073, DEC-1080, DEC-1092 (1). I found no superseded or PROPOSED rule in use. The register's DEC-1113 names four briefs; DECISIONS-IN-FORCE line 400 records your approval of all five by hash.
**Deviations, named as EMG-common asks:**
- The Write tool was refused once for my `$TMPDIR`: a permission prompt this session can't grant. I did not retry it. I used inline `python3 -I -B -c` programs instead, writing only under `$TMPDIR`.
- Step 0's pipe is the brief's own command.
- Nothing was refused twice.
- No Bash line named the template folder or the sets root. Where a program needed the template folder's name, it built it in code.
- The hidden-half rule held. The clone left out `fixtures/evaluation/`, and my tree probe skipped every path with a `hidden` part.
**Search again once (DEC-1092 (1)):** I first searched the register for "F21", "rule script", `label_rules`, "class 14 (" and "script label"; the only hits were W2-148's F21, an unrelated finding. I then searched in other words, reading DEC-1099 (1) Q5 and DEC-1113 in full. Nothing the auditor may read describes the first labeller's script.

---

## K1–K8

**K1: the touched set is exact. Pass.**
- `apply.sh` writes to the same places as the second build's: only two constants differ.
- **What my run wrote (a stopped apply, F39):**
  - the list, through a temporary file beside it renamed over it (0400, in a 0700 folder);
  - the five briefs (0644) and their two folders;
  - `backup/`, holding `APPROVED` and `SHA256SUMS`.
- **What it left alone:** an unreadable trap file under the planted sets root, and the planted HOME. Its `mktemp` file was removed.
- **After undo:** the clone was clean except for `backup.undone-<UTC>`.
- **The commit:** §5's commit is unchanged. The second build's reviewer ran it with another session's changes staged and got exactly 5 A.

**K2: the list is right. Pass.**
- **The before-list,** through the script's own parser: 8 lines, 6 template lines, no brief line, sha256 `331e48fa…`. ACT-INDEP-WALLS-1's live apply recorded that hash (`drafts/indep-walls/backup/APPROVED.sha256`), and wrote the list in this form.
- **The after-list:** 23 lines ending in a newline, sha256 `32f1aab7…`.
  - Exactly lines 7 and 8 differ from the before-list: `kinds.yaml` `8b50a78f01b3` → `734b26e261fa`, and `tree-exclude.txt` `21660e1ee5ad` → `e8395088167e`. The other four are ACT-INDEP-WALLS-1 §3's.
  - Then 10 comment lines. Line 10 names `90c1fea6c7e5`; line 14 names the script `95fe78dd49bb…`.
  - Then 7 brief lines.
  - The parser skips no line that is not a comment, and no hash repeats.
  - It holds exactly the six template files the script needs, one hash each.
- **The script's own parser reads 6 template lines and 7 brief lines.** My in-memory probe and `apply.sh`'s own read-back in my clone both said "6 template lines, 7 brief lines (auditor, labeller, operator, writer)".
- **Kinds:** each set-up A line's kind equals its brief's front-matter `kind`. `--kind operator` is refused 17.
- **Every line has an owner approval:**
  - the four unchanged template lines: ACT-INDEP-WALLS-1;
  - the two changed lines: this ACT's yes. §0 and §5 now say so plainly, and §1 lists what `kinds.yaml` turns on, including the rule-script run at round 1;
  - the five briefs: DECISIONS-IN-FORCE lines 400–404, whose hashes equal §12's in full;
  - `reviewer-brief.md`: DEC-1109 (1), by hash;
  - `brief.md`: DEC-1109 (1) "with one change". The register records no hash, but line 25 holds the changed sentence.
- The script's hash is only a comment (F34). §2, §3 and §8 now say so.

**K3: the undo is real. Pass.**
- Undo's code is unchanged.
- I ran it for real after a stopped apply (the after-list, the five briefs and a backup in place). It:
  - put the list back byte for byte (`331e48fa…`, 0400);
  - removed the five files and both folders;
  - renamed the backup and left the state "before".
- `check` then said "ready to apply".
- The second build's reviewer's refusal cases (the before state, a damaged backup, a list changed after the apply) hold, because the code is the same.

**K4: the rehearsal is real. Pass.**
- **What it is:** `rehearsal.log` (`5fb57e916221`) is a run of `rehearse.sh` (`e0da436ef120`) with this `apply.sh` (`e3943ad4e243`). It ran in a clone at `067a8b79c988` with the script `95fe78dd49bb`, and ends `failures: 0`.
- **Set-up A's five briefs pass stage 10 and build their dry walls:** 7 of 7 lines match their bytes; each dry launch exits 0 with model `claude-opus-5-5` and schema `sgx1-<brief>-result.schema.json`; each `input/` is as §6 lists; each `brief.md` is byte for byte the approved brief; no tree holds `indep-briefs/`, `.claude/` or `src/gov/guard/`.
- **The counts are what §6 states,** row by row:
  - the order refusal, and the refusal 11 before the ACT;
  - the parser's line on apply, the second apply refused, and "already applied";
  - the commit: 5 A with three trailers; the list's folder 0700 and file 0400;
  - the operator's brief launched as a writer: refused 10;
  - undo: back to `331e48fa`, 5 D, check ready again, a launch refused 11;
  - 23 live lines unchanged.
- My own run of the script's resolver gives the same stage-10 values for the five drafts. Their budgets and timeouts are within their kinds', and their tools equal their kinds'.
- `rehearsal-trial-d388da2f2.log` is identical to the run except for heads, hashes and times.

**K5: the order holds. Pass (F39, a row).**
- `order_ok` is byte for byte the second build's. With this `apply.sh` in my clone at `b5c23e7b3`:
  - `check` said "ready to apply";
  - with one byte added to the launch script it refused: "is not W2-149 with set-up A's wiring (95fe78dd49bb): merge it first";
  - with the script restored it was ready again.
- The second build's reviewer's refusal cases for the template files, the hook and map, the lists and the drafts hold, because the code is the same.
- **Today's main tree** holds the script `95fe78dd`, the hook `74f8dbea` (with `sets_line_keys`) and the map `44f99ea5`. It has no `indep-briefs/` and no `backup/`.
- W2-141's staged hook still has `def sets_line_keys(` (line 428).
- **The gap:** `check` does not test the other four template files or the operator's two briefs. Only `apply`'s read-back, after it has written, does (F39).

**K6: the class. O.**
- `class-rules.yaml`'s `walled-sessions` row (O) matches `gov-os-eval/**` (the list) and `governance/project/indep-briefs/**` (the briefs).
- The `cto-scratch` row (O) matches `.gov-runtime/**` (the backup).
- By effect it is at least (b). The highest vote applies: O, as §0 says.

**K7: the package's account is true. Pass.**
- **F18–F23 are as §3 says,** read in the code at `95fe78dd`:
  - **F18:** labeller 1's round-1 delivery runs the confined check over the half's staged lines before anything lands; any refusal or OS error gives 20.
  - **F19:** a result that says it stopped delivers nothing (20), as the delivery's first step.
  - **F20:** labeller 2's labels are checked against the overlap's ids, else 20.
  - **F21:** in the auditor's disputes, both reasons are blanked when either is empty. The labels files keep the real reasons.
  - **F22:** a settled line takes the auditor's whole decision.
  - **F23:** `rule_class` is accepted as an integer 1–14 (never a boolean) or a decimal string "1"–"14", and stored as an integer everywhere.
- **F36 and F37** are named as their review states them: both in scope, ordinary work, consequence other.
- **F33 holds:** at `f000adda4` all six template hashes are the before-list's, so after the apply that pin is refused 11.
- **F34** holds in §2, §3 and §8 item 1. **F35** holds in §0 and §5. **F31 and F32** are §8 items 5 and 6.
- **The sources check out:** `9cce7430d` is ACT-SETS-GLOBS-1's apply, and the ticket's row gives 197/0/3.

**K8: independence. Fail (F38), no blocking finding.**
- **(1) Is F36 a fair account of what remains of the auditor's blind?** It is fair on the pattern: the script's side is the class-14 side, with no clause when the script gives none. It is not fair on where the blind rests (F38).
  - "The auditor cannot name a labeller from anything it may read" is true for the reads its brief allows. The register says nothing of the script.
  - But every set-up A tree, the auditor's included, holds files stating the tell. Only the brief's "never read any package, draft or ticket file" keeps them unread. The package says exactly this of the guard's code (F31), but not of the tell.
  - **Minor:** "blanking every dispute's reasons would hide it" covers the reason channel. The labellers' own clause wording, the review's second residual, would remain and is not named.
- **(2) Does anything in this build change what a wall's tree holds?**
  - **The rules: no.** The template has not changed since `7f0e71519`, and the tree build and its exclusions did not change in the F18–F23 diff.
  - **The inputs:** the only change is the auditor's `disputes.jsonl`, narrowed by F21's blanking.
  - **The content: yes.** The walls are built at the amended pin, after `90c1fea6c` and your operator's commit. At that pin every set-up A tree holds:
    - W2-149's ticket row, on w2/integrate since `c17edb833`;
    - the second build's committed package;
    - this package's §3, once the CTO commits it to record it ready;
    - the F18–F23 code, its tests and its evidence.
  - Three of these say plainly how to pick out the script's side. No exclusion leaves them out.

**Probed and found sound:** every draft's hash; the main tree's copies; the template's hashes at four commits; the script's hash at every head; the parser's counts; stage 10's resolver over the five drafts; the order checks; check, apply and undo; the touched set; the temp file removed; the trial log; the class rows; and the F18–F23 code paths.

## The diff from the second build
- `briefs/` (five files), `APPROVED.before`, `freeze.py`, `install_check.py` and `rehearse.sh`: byte for byte the same.
- `APPROVED.after` (`a0af30f840db` → `32f1aab70bc2`): only two comment lines changed.
  - Line 10: the merge `7f0e71519f83` → `90c1fea6c7e5`.
  - Line 14: the script `a5f2e8f5d9c9…` → `95fe78dd49bb…`, and the same merge change.
  - Every template line and brief line is identical.
- `apply.sh` (`53c2c68122d2` → `e3943ad4e243`): exactly two lines changed, `LAUNCH_SHA` and `LIST_AFTER`. Every other constant and all of the logic are unchanged.
- `rehearsal.log` (`780d8ddb9594` → `5fb57e916221`): only the times, the clone's head (`29907d75048f` → `067a8b79c988`), the script's and the drafts' hashes, the planted list after, the clone's commit id and the scratch size changed. Every check line and count is identical, and it still ends `failures: 0`.
- New in this bundle: `rehearsal-trial-7df7c35e3.log` (the second build's trial) and `rehearsal-trial-d388da2f2.log` (this build's).
- Nothing changed beyond the re-frozen hashes, the log and the trial logs.

## Findings

Classification: two findings. F38 is in scope, ordinary work yes, consequence other. F39 is in scope, ordinary work no, consequence other. Neither blocks. Recommendation: READY, no round.

**F38 (K8): §3 and §8 do not tell the owner that the auditor's tree holds the tell in writing.**
- **What was done:** I listed the tracked files that survive the overlap auditor's exclusions at HEAD, using the launch script's own exclusion code and template: 3,642 files. I searched them for the tell's wording.
- **What happened:**
  - The tree holds `.tickets/DAEO-52ku.md`, whose 12:35 row says "in the disputes F21 blanks, the script's side is still readable (it is the class-14, no-clause side)".
  - It holds the committed package's line "an empty script reason tells the auditor which side is labeller 1's (F21)".
  - Once committed, it will hold this build's §3: "it is the class-14 side with no clause, against the second labeller's refuse or ask".
  - It also holds the launch script's merge and blanking code, W2-149's tests, README and evidence, and the declaration.
  - §3 tells you "the auditor cannot name a labeller from anything it may read", but does not say that its tree holds these statements and only its brief keeps them unread.
- **What should have happened:** one line in §3 and §8. Every set-up A tree holds text naming the tell; the auditor's brief forbids reading it; so for these copies the auditor's not knowing which side is which rests on that instruction, as F31 says for the guard's code. Alternatively, the CTO adds `.tickets/**` and `governance/project/orchestration/packages/**` to the auditor entry's `tree_exclude`, which rebuilds this ACT.
- Ordinary work: yes, because the tell is in files every set-up A tree holds. A search over the whole tree for a word of the auditor's own task ("dispute", "labeller", "ordinary work") returns those lines, as the second build's review showed for DEC-1093 (F31).
- Consequence: other. No label lands wrongly and the guard is untouched. DEC-1113 (2) asks for blindness to the guard and the results; the labeller blind is the brief's own.
- Scope: in.
- **What would reverse it:** the CTO holding that "anything it may read" already tells you the blind rests on the brief's prohibition. Or the pin falling before `c17edb833`, which cannot happen: the pin follows `90c1fea6c` and your operator's commit.

**F39 (K5): `check` says "ready" when a list line other than the two it pins no longer matches; `apply` then writes before stopping.**
- **What was done:** in my clone I added one byte to the operator agent's `brief.md`, then ran check, apply, check and undo.
- **What happened:**
  - `check` said "state: before … check: ready to apply" (exit 0).
  - `apply` wrote the after-list (`32f1aab70bc2`, 0400), the five briefs and a backup. It then stopped with "brief mismatches 1 … run 'bash apply.sh undo'; nothing more is done" (exit 1).
  - `check` then failed at the same read-back.
  - `undo` put back `331e48fa…` byte for byte.
  - A change to any of the four unchanged template files takes the same path.
- **What should have happened:** `check`, and `apply` before its first write, read `APPROVED.after` back against the tree. And the stop message should not say "nothing more is done" after a write.
- Ordinary work: no, because it needs an owner-approved change to one of those six files to merge between the freeze and the apply, without a rebuild.
- Consequence: other. It fails closed: the briefs are not committed, so every launch is refused 10 (or 11 for a changed template file), and undo restores the list exactly.
- Scope: in.
- **What would reverse it:** a CTO procedure that rebuilds this ACT on any change to those six files. Then `check`'s silence never matters.

```verdict
{"act": "ACT-W2-149-INSTALL-1", "class": "O", "apply_sh_sha256": "e3943ad4e243b41ef4e6b7f4081d59e556a84ed4cc7960640f0d3a1e5fd22b55", "kpis": [
 {"kpi": "K1", "verdict": "pass", "findings": []},
 {"kpi": "K2", "verdict": "pass", "findings": []},
 {"kpi": "K3", "verdict": "pass", "findings": []},
 {"kpi": "K4", "verdict": "pass", "findings": []},
 {"kpi": "K5", "verdict": "pass", "findings": [{"id": "F39", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "K6", "verdict": "pass", "findings": []},
 {"kpi": "K7", "verdict": "pass", "findings": []},
 {"kpi": "K8", "verdict": "fail", "findings": [{"id": "F38", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```