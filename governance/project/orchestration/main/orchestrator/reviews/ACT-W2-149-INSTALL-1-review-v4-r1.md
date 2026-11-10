I'm returning READY by `verdict.py`. The class is (O). There is one new finding, F41, which is two sentences of text to fix, and nothing blocks. At `2f98aecbc` the overlap auditor's dry-built tree holds no file that says which dispute side is which labeller's.

- **sandbox_check:** Passed. (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-149','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system`, and no file exists there. (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109…`, and `git update-index --refresh` exited 0. I ran as `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-52ku`.
- **ps_check:** At the end I ran `ps -eo pid,args` on its own, with no pipe (DEC-1080). It shows only my shell and `ps`; no ollama or llama-server process of mine.
- **task:** DAEO-52ku. The independent, read-only, one-round review of ACT-W2-149-INSTALL-1's fourth build (on F36 and F38 closed), on `w2/W2-149-sgx` at `2f98aecbc525`, which was w2/integrate's head when I was briefed. I am not the ACT's author.
- **status:** DONE. READY by `verdict.py`. There is one finding, F41: in scope, ordinary work yes, consequence other. No finding is in scope, reachable in ordinary work and fail-open or work-losing. Class O. I marked K7 fail for F41: two sentences carried over from the third build stopped being true when F38 was closed. Nothing blocks.
- **work_completed:**
  - **Read:** the package in full; the third build's review and the narrow F36 review; JUDGEMENT.md, EMG-common.md and the step-0 file; all five briefs.
  - **Drafts:** `apply.sh`, `freeze.py`, `install_check.py`, `rehearse.sh` and all four logs. I diffed every draft against `drafts-v3-reviewed/`, and the package against its committed third-build text.
  - **Launch script:** the list parser, stages 14, 11 and 10, the resolver, the tree build, the auditor's staging, labeller 2's check, labeller 1's merge and the round-1 rule check.
  - **Template:** `kinds.yaml`, `tree-exclude.txt` and `settings.json.tmpl`, with the Read tool only.
  - **Re-run in my clone:** a sparse clone at `2f98aecbc` in my `$TMPDIR`, with no `fixtures/evaluation/`, a planted HOME and a planted sets root. There I:
    - re-ran `freeze.py`;
    - ran `check`, four refusals of the order, and the third build's `check`;
    - ran `apply`, a second `apply`, and `check` again;
    - ran §5's commit with another change already staged, then `install_check.py`;
    - made dry launches under all five briefs and both operator refusal cases;
    - ran `undo`, §5's undo commit, `check`, and a launch after the undo.
  - **Search:** I searched the auditor's built tree in two passes with line breaks folded, and read every passage in it that names the labellers.
- **files_changed:** None in any tree. `git status --porcelain` was empty at the start and is empty at the end; HEAD was `2f98aecbc` both times. Outside the trees, only Step 0's blob and index refresh. My `$TMPDIR/rv4` was made and then removed. I only read the main tree: hashes, listings, Read and Grep. I never opened the real sets root.
- **evidence:**
  - I read `drafts/apply.sh` at sha256 `122116f1a5e49ad4415b11765759c0ddfe1a3b0a94d6038e7f1ff2c2bead2366`.
  - The 12 files §4 hashes match it. All 15 files in `drafts/` equal the main tree's `drafts/w2-149-install/` byte for byte.
  - `freeze.py` re-run at `2f98aecbc` rebuilds `APPROVED.before` `331e48fa…`, `APPROVED.after` `6b923cb4…` and `apply.sh` `122116f1…` exactly.
  - At `2f98aecbc` and in the main tree: the launch script is `90b943aef8be`, `kinds.yaml` `ddd84ae25910`, `tree-exclude.txt` `e8395088167e`.
  - Of 3,871 tracked files, the auditor's dry tree holds 3,153, each other set-up A tree 3,651, and a brief with no entry 3,729.
  - Scratch at its largest: `du -sh` 199M, `du -s --inodes` 11,195. Now `$TMPDIR` is 20K and 8 inodes, all the harness's own.
- **tests:** No pytest and no heavy-slot job: the ACT changes no code, and the role re-runs nothing the lead ran. So the DEC-1012 exclusion left nothing out. I ran `apply.sh` and the launch script (dry, `--seed 17`) only in my clone. No real `claude` session, no GPU, no network, no `gov retrieve` (DEC-1064).
- **discoveries:**
  1. w2/integrate moved during the review to `8bd387c7f`. It adds 5 lines to `.tickets/DAEO-52ku.md` only. The auditor's tree leaves that file out, and the commit touches no script, template, schema or operator brief.
  2. The committed third-build package on integrate still states the tell in its §3. It sits under `packages/**`, so the auditor's tree no longer holds it, but every labeller's and writer's tree does.
  3. DECIDED-NOT-DONE row 75 still names the third build's yes, `d38b6fe2`.
  4. The narrow F36 review searched W2-149's head `bdda27d28`, before W2-96-d10b reached integrate. The merge `2f98aecbc` adds 4 files to the auditor's tree, and my search there also finds no tell.
- **risks:** Once this is applied, set-up A can run, and F37 and F40 go live with it. The auditor's blind now rests on the six excluded places (F40). A record written before the pin that restates the tell in DECISIONS-IN-FORCE, the register or `governance/project/orchestration/reviews/` would reach its tree. So option (a)'s search at the amended pin is still needed. The real list is checked only at your operator's apply.
- **lessons:** A rebuild that closes a finding by code has to re-read the package's history and residual sections, not only its account. Two sentences written for the text-fix route survived into this code-fix build. A review "at the merged head" should name the commit it searched, because integrate can move between a review and its merge.
- **proposed_decisions:** For the CTO (DEC-1112 (3)): carry F41 as a text fix when filling @SHA8@ and @REVIEW@ (DEC-802). Optionally, cite this review's search at `2f98aecbc` in §3 beside the narrow review's. No round.
- **unresolved:** I never opened the real list. Real sessions, real deliveries and labeller round 2 were not exercised: dry code only, which is all the package claims. Whether an auditor could infer the sides from the labels' own content, with no file saying so, cannot be tested without a live session; §3 names this remainder. The amended pin is not yet chosen, so F40's search at that pin is still to be done.
- **recommended_next_action:** READY by `verdict.py`, no round (DEC-1010).
  1. The CTO carries F41, fills @SHA8@ and @REVIEW@, and moves row 75's yes line to the new sha8.
  2. The CTO then asks for `yes ACT-W2-149-INSTALL-1 <sha8>`.
  3. Your operator runs §5 before any further change to the script, the template or the operator's briefs is merged.
  4. Before the overlap auditor's first real run, the CTO repeats this review's tree search at the amended pin (F40, option (a)).
  5. This record stays under `.gov-runtime/`.

---

**Identity:** HEAD `2f98aecbc525ecc9b8f3aecb419851e8845dd5a5` on `w2/W2-149-sgx`, clean at the start and at the end. w2/integrate is now `8bd387c7f`, which touches the ticket file only.
**task:** DAEO-52ku
**decisions:** DEC-1101 (2)-(3), DEC-1112 (3), DEC-1113 (2), DEC-1109 (1), DEC-1115 (1), DEC-1099 (1) Q5, DEC-820, DEC-1057, DEC-801, DEC-802, DEC-808, DEC-809, DEC-1010, DEC-1014, DEC-1064, DEC-1065 (1), DEC-1073, DEC-1080, DEC-1092 (1). DEC-1101, 1109, 1112, 1113 and 1115 all read ACCEPTED. I found no superseded or PROPOSED rule in use.

**Deviations, named as EMG-common asks:**
- **The template folder, once:** one early Bash line, a read-only `git ls-tree` at `2f98aecbc`, named it. Every later program took the name from the launch script's own `TEMPLATE_DIR` and `WALLS` constants.
- **Step 0's pipe** is the brief's own command.
- **A `git show`** meant to save the committed package to scratch printed it to my output instead; it was read-only.
- **The Write tool:** I made no Write call. The probes were inline `python3 -I -B -c` programs that wrote only under `$TMPDIR`.
- **Refusals:** nothing was refused.
- **The hidden-half rule held:** the clone left out `fixtures/evaluation/`, where no `hidden` folder is tracked anyway. I read contents only inside wall trees, which leave out `fixtures/evaluation/**`, and skipped any path with a `hidden` part. I never opened the real sets root.

**Search again once (DEC-1092 (1)):** Pass one searched the auditor's built tree for the tell's phrasings and 12 other pattern groups. Pass two used different words: co-occurrence patterns, plus a census of every file naming the labellers or set-up A, with each passage read.

## K1–K8

**K1: the touched set is exact. Pass.**
- I snapshotted the clone and both planted roots before and after `apply`. `apply` wrote exactly:
  - `backup/`, holding `APPROVED` (0400, `331e48fa`) and `SHA256SUMS`;
  - `governance/project/indep-briefs/` and `sgx1/`, with the five briefs (0644);
  - the list, as `6b923cb4` at 0400, in its 0700 folder.
- It left alone: the rest of the clone (no `__pycache__`), the planted HOME, and an unreadable trap file under the planted sets root. Its `mktemp` file was removed.
- I ran §5's commit with `README.md` already staged. It committed exactly **5 A** with the three trailers, and `README.md` stayed staged.

**K2: the list is right. Pass.** I read both lists with the launch script's own `parse_approved`.
- **The before-list:** 8 lines, 6 template lines, 0 brief lines, `331e48fa`.
- **The after-list:** 23 lines ending in a newline, 6 template lines, 7 brief lines, `6b923cb4`.
- **Only two template lines change.** Lines 7 and 8 alone differ from the before-list:
  - `kinds.yaml` `8b50a78f01b3` → `ddd84ae25910`;
  - `tree-exclude.txt` `21660e1ee5ad` → `e8395088167e`.
- **The tree agrees.** Every template line equals its file at `2f98aecbc`, and the six keys are exactly the script's `TEMPLATE_FILES`, one hash each.
- **The comments:** lines 10 and 14 name `2f98aecbc525`, and line 14 names the script `90b943aef8be33f6…`.
- **The seven brief lines:**
  - the five set-up A briefs are absent at the commit, because your operator commits them;
  - the operator's two equal their files;
  - no line is skipped and no hash repeats.
- **The parser:** `apply.sh`'s read-back says "6 template lines, 7 brief lines (auditor, labeller, operator, writer); template mismatches 0; brief mismatches 0".
- **Does §1 state the auditor's wider exclusion?** Yes, in two places: the `kinds.yaml` row of §1's table, and the last "turns on" bullet. Both name `.tickets/**`, the packages, the launch script, and W2-149's tests and evidence. §0 and §5 say the yes approves `kinds.yaml` as changed. These are the six globs in the template's auditor entry.

**K3: the undo is real. Pass.**
- `undo` put the list back byte for byte (`331e48fa`, 0400). It removed the five briefs and both folders, and renamed the backup to `backup.undone-<UTC>`.
- §5's undo commit, exactly as written, gives **5 D** with the three trailers. The clone's tree then equals `2f98aecbc`, with an empty diff.
- `check` says "ready to apply" again, and a launch at `2f98aecbc` is refused **11**.
- The snapshot after the undo differs from the one before the apply only by the renamed backup.

**K4: the rehearsal is real. Pass.**
- **The log:** `rehearsal.log` (`7d25071d1b5f`) is a run of `rehearse.sh` (`e0da436ef120`) with `apply.sh` `122116f1a5e4`. It ran in a clone at `2f98aecbc525` with the script `90b943aef8be`, and ends `failures: 0`. Every row of §6 matches it.
- **My reproduction agrees on every count:**
  - stage 10: **7 of 7** lines, with front matter ok for all five briefs;
  - each of the five dry launches exits **0**, with model `claude-opus-5-5` and schema `sgx1-<brief>-result.schema.json`;
  - each `input/` is as §6 lists, and each `brief.md` is the approved bytes;
  - no tree holds `indep-briefs/`, `.claude/`, `src/gov/guard/`, `src/gov/launch/` or the template folder;
  - the operator's brief named as a writer is refused **10**, and `--kind operator` is refused **17**.
- `rehearsal-trial-bdda27d28.log` is identical to the run except for heads, hashes, times, the commit id and the scratch size.

**K5: the order holds. Pass.**
- With one byte added to the script, to `kinds.yaml` or to `tree-exclude.txt`, `check` refuses: "… merge it first". With the map put back to before ACT-SETS-GLOBS-1, it refuses: "apply it first". After each restore it is ready again.
- The third build's `apply.sh` refuses at `2f98aecbc` ("(95fe78dd49bb): merge it first"), so a stale build cannot be applied.
- `order_ok` is byte for byte the third build's.
- **Today's main tree:** script `90b943ae`, `kinds.yaml` `ddd84ae2`, `tree-exclude.txt` `e8395088`, map `44f99ea5`, hook `74f8dbea` with `sets_line_keys`. It has no `indep-briefs/` and no `backup/`. So the live `check` will get as far as the real list.
- F39 (§8 item 7) still stands; that code is unchanged.

**K6: the class. O.**
- `class-rules.yaml`'s `walled-sessions` row (O) matches `gov-os-eval/**` (the list) and `governance/project/indep-briefs/**` (the briefs).
- The `cto-scratch` row (O) matches `.gov-runtime/**` (the backup).
- By effect it is at least (b). The higher vote applies: O.

**K7: the account is true. Fail (F41), nothing blocking.**
- **F36:** every dispute's reasons are blanked (`a["reason"] = b["reason"] = ""`), and x/y keep the seeded draw. In my wall both reasons were `""`, and no `how` field got through.
- **F38:** the six globs are in the template's auditor entry, and none of their files is in the built tree. The auditor's brief reads only the register, the Contract, the path map and the held-out list. Its `tickets.jsonl` comes from git at the commit, not from the tree.
- **"Searched the auditor's tree at the merged head":** this is true of W2-149's head `bdda27d28`. This review repeated the search at the merge `2f98aecbc` with the same result.
- **"What remains is the labels' own content":** this is fair. The narrow review also named the seed as a remainder, but the draw rule appears nowhere in the auditor's tree, and the auditor has no tool that runs code.
- **F37:** as §3 says. A round-1 rule-check refusal of any kind becomes `Refuse(20, "rules")`, logged as `rejected rules`.
- **F40 and §8 item 1:** as the narrow review gives them, with option (a).
- **Sources:** the merge message gives 362 passed outside the sandbox.
- **Not true:** two sentences carried over from the third build (F41).

**K8: independence. Pass.**
- **The auditor's tree is the script's rule.** Its dry-built tree at `2f98aecbc` holds 3,153 files. That set equals the launch script's own `excluded_by`, applied with `tree-exclude.txt` and the real auditor entry at the commit.
- **No file in it states the tell.** I searched all 3,153 files twice, with whitespace folded, literal `\n` folded and adjacent quotes joined. No file states which dispute side is which labeller's.
- **The set-up A text that remains says nothing of the sides.** 17 files hold any:
  - the register's DEC-1099 Q5, DEC-1101 and DEC-1113 (an outside labeller, a second on 10 %, an auditor for disagreements);
  - DECISIONS-IN-FORCE (the same, plus labeller 1's hand-label rule and "exit 18 for a rule script that cannot run confined");
  - comments in the path map, a row in `class-rules.yaml`, and a line in START-NEXT-SESSION;
  - the result and counts schemas, whose counts schema names the round-1 file `label_rules.py`.
- These say the first labeller has a rule script and hand labels. None says what either side's labels look like, or which side is whose. Every other hit was unrelated: N/A reasons, git merge sides, `index_is_` test names, and review lines saying "Ordinary work".
- **The auditor's wall itself:** `CLAUDE.md`, `WALL.json`, `half.json` and `tickets.jsonl` (id, role, wbs_id and allowed_paths only) hold nothing of the sides. The x/y map is written only at delivery.
- **My planted case:** one side's `rule_class` came through as a string, only because I wrote the second labeller's file by hand. Both real deliveries store an integer (labeller 2's check, line 1797; labeller 1's merge, line 1751).
- **Do the labellers' and writers' trees still hold what their briefs need?** Yes. Each holds 3,651 files, unchanged by this build: the register, 286 Contract files, SANDBOX-GUARD-EXP-1.md and the declaration, the path map, the held-out list, all 218 tickets (W2-56's included) and the 6 role files. The writers' samples each name 9 paths left out of their trees, names only, as noted before.

## The diff from the third build (`drafts/` against `drafts-v3-reviewed/`)
- **Byte for byte the same:** `briefs/` (all five), `APPROVED.before`, `freeze.py`, `install_check.py`, `rehearse.sh`, and both older trial logs.
- **`APPROVED.after`** (`32f1aab70bc2` → `6b923cb4d552`) changes on exactly three lines:
  - line 7: the `kinds.yaml` hash, `734b26e261fa` → `ddd84ae25910`;
  - line 10: the merge, `90c1fea6c7e5` → `2f98aecbc525`;
  - line 14: the script, `95fe78dd49bb…` → `90b943aef8be…`, plus the same merge change.
- **`apply.sh`** (`e3943ad4e243` → `122116f1a5e4`) changes on exactly three lines: `LAUNCH_SHA`, `LIST_AFTER` and `KINDS_SHA`. `EXCLUDE_SHA`, every other constant and all of the logic are unchanged.
- **`rehearsal.log`** (`5fb57e916221` → `7d25071d1b5f`): only the times, the clone's head (`067a8b79c988` → `2f98aecbc525`), the script's and the drafts' hashes, the list after, the commit id and the scratch size (196M → 201M). Every check line and count is the same.
- **New:** `rehearsal-trial-bdda27d28.log` (`a02ef3160128`).
- **The package text** (beside the brief's ask), against the committed third build:
  - the header, the sources and §1–§6 move to `2f98aecbc`, `90b943aef8be` and `ddd84ae25910`;
  - §1 adds the auditor's wider exclusion;
  - §3's F36 paragraph becomes "F36 and F38 are closed", with F37 and F40 as the rows that stay;
  - §8 item 1 becomes F37 and F40;
  - the yes line becomes `@SHA8@`, and §7 adds `@REVIEW@`.

## Findings
Classification: one finding. F41 is in scope, ordinary work yes, consequence other. Nothing fails open or loses work. Recommendation: READY, no round.

**F41 (K7): two sentences carried over from the third build are no longer true now that F38 is closed.**
- **What was done:** I compared the package with its committed third-build text and with what this build does.
- **What happened:**
  - §7's third-build bullet still says of F38: "It is carried as a text fix to §3 and §8 item 1 (DEC-802); `apply.sh`, the drafts and §5's commands are unchanged". But F38 was then closed by code, the template change merged at `2f98aecbc`, which is why this build exists. This build's `apply.sh` and list did change. §0, §3 and §4 say so, and §7 contradicts them.
  - §8 item 5 still says every set-up A tree holds "the launch script". The overlap auditor's tree holds 0 copies now. The item's other copies (the W2-141 hook copies, the kernel hook template, the guard's suites) are still in every tree.
- **What should have happened:**
  - §7: say F38 was first to be carried as a text fix, then closed by code (DEC-1112 (3), DEC-1113 (2)) in the auditor entry's wider `tree_exclude` at `2f98aecbc`, which is this build.
  - §8 item 5: "the launch script, except in the overlap auditor's tree".
- Ordinary work: yes, because you read §7 and §8 before your yes, and a rebuild that carries text forward routinely leaves an earlier disposition standing.
- Consequence: other. Nothing applies differently: `check` pins every draft by hash, and your yes covers the list as it is.
- Scope: in.
- **What would reverse it:** the CTO holding that §7 is a frozen record of the third build's review, and that §8 item 5 speaks of the set-up A trees generally.

## Probed and found sound
- the drafts' hashes, and the main tree's copies;
- `freeze.py` reproducing the build exactly;
- the parser's counts, and the template's hashes at the commit;
- the four order refusals, and the stale build refused;
- the touched set, and the `--` path limiting §5's commit;
- the backup, `undo` and §5's undo commit;
- stage 10 per line, and all five dry walls;
- the operator's two refusal cases;
- the F36 blanking, and no `how` field in the wall;
- `rule_class` stored as an integer by both deliveries;
- tickets staged from git, not from the tree;
- the auditor's tree equal to the script's rule, and searched twice;
- the other trees' contents;
- the class rows;
- the main tree's live files;
- the corpus window (2026-11-02 to 11-09), which ends before any of the tell's text was written.

```verdict
{"act": "ACT-W2-149-INSTALL-1", "class": "O", "apply_sh_sha256": "122116f1a5e49ad4415b11765759c0ddfe1a3b0a94d6038e7f1ff2c2bead2366", "kpis": [
 {"kpi": "K1", "verdict": "pass", "findings": []},
 {"kpi": "K2", "verdict": "pass", "findings": []},
 {"kpi": "K3", "verdict": "pass", "findings": []},
 {"kpi": "K4", "verdict": "pass", "findings": []},
 {"kpi": "K5", "verdict": "pass", "findings": []},
 {"kpi": "K6", "verdict": "pass", "findings": []},
 {"kpi": "K7", "verdict": "fail", "findings": [{"id": "F41", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K8", "verdict": "pass", "findings": []}
]}
```