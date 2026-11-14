# ACT-CLAUDE-COPIES-11: the generated copies of W2-101's three new kernel skills (frontend, ui-ux, devops)

## 0. The short version

- **What:** 15 generated files, all new: `.claude/skills/{frontend,ui-ux,devops}/{SKILL.md, check_domain_skill.py, scenario-records.yaml, scenario-summaries.md, scenarios.md}`.
  - Every byte comes from the product's own generation: rulesync 24.0.0, run from the root `.rulesync/` of the merged tree (portability's own GENERATE form), not by hand.
  - rulesync renders **all five files** of each skill folder. `SKILL.md` is its rendering (front matter re-folded: `name`, `description`, `version` under `metadata`); the other four are byte copies of the kernel files.
  - **Nothing live changes until it runs.**
- **The owner's line,** on its own line:

yes ACT-CLAUDE-COPIES-11 3b4e462f

- **Manifest sha256:** `3b4e462f1e1fdbb3fefef7559ae2c83de03eb6ba534da34cf85d40815ffde7ba`.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-11/`.
  - The builder is `drafts/claude-copies-11/build_claude_copies_act_11.py`. It is copied from COPIES-10's `build_claude_copies_act_10.py`; neither COPIES-10's nor COPIES-9's files are edited, and the changes are in its docstring.
  - The build log is `drafts/claude-copies-11/build.out`. The gated runs' outputs and the operator gates are in `drafts/claude-copies-11/evidence/`.
- **Class (b), claimed, as ACT-CLAUDE-COPIES-1 to -10 were.** The operator's own `act_class.classify` gives class `b`, row `agents-skills-kernel` for all 15 files, no script hits.
- **Who applies it: the owner's operator agent, on the owner's yes,** as for ACT-1 to ACT-10. The CTO cannot apply it: a session cannot write `.claude/**` (DEC-315). The by-hand route (§4) is the owner's, with `Role: owner`.
- **Under:**
  - the owner's CIT-P approval of W2-101 (pending: `yes W2-101-CIT-P 42c1cc38`; `docs/changes/W2-101-CIT-P.md` at `3bf1c96b47c1`, sha256 `42c1cc38f4c985afc23609bb999b95a5207ee6e434b057b40dd4dd7419c5cb27`);
  - DEC-315, DEC-1112 (3), CAP-33;
  - also DEC-1057 (rehearsed as the operator runs it).
  - The manifest's `dec` field names DEC-315, DEC-1112 (3) and CAP-33 only. If the CTO wants the approval's DEC number in it, the bundle must be rebuilt, and the manifest sha changes.
- **When:** in the CTO's hand merge of `w2/W2-101` (head `3bf1c96b47c1`), **after the merge commit, before the checks.** Integrate never holds W2-101's three kernel skills without their copies past that sitting.
- **Independent of COPIES-10:** the two ACTs touch disjoint folders. This bundle is the same bytes whether or not W2-100 and COPIES-10 landed first (order 2, §3), and its check 2 is green in both orders.
- **Review:** the operator's fixed reviewer brief applies (`ACT-CLAUDE-COPIES-11/review.md`). It is **not written yet.** The CTO starts the reviewer before asking for the owner's line. G4 refuses without the reviewer's fenced verdict block.

### No template patch, no CTO template commit

- W2-101 itself carries the root `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/` copies of all three skills, byte-equal to the kernel (CIT-P §2, §3). Its merge brings them. As in COPIES-7 and -10, the ticket carries the `.rulesync` sources and the ACT carries only `.claude/skills`.
- rulesync writes nothing under `.rulesync/` or `template/`. Its only other differing output is `.claude/settings.json` (the held-out deny, DEC-616). The same difference shows on plain integrate, and no copies ACT regenerates it.
- Portability on `template/`, read as an adopted project, gives no finding for the three skills.

## 1. The files

Every "old" is `absent` (`null` in `list.txt`): no `before/` file is written, as in COPIES-7 and -10, and the undo removes the files.

| file | old | new sha256 |
|---|---|---|
| `.claude/skills/devops/SKILL.md` | absent | `a41243e1e6745fee8aa7c9cd6ce9cabd7f12d7c48531daf6df7362cae985720f` |
| `.claude/skills/devops/check_domain_skill.py` | absent | `3532f93de84972ded38ef7725dac323f45bab78e5c4735dc90d8ed84ddc9d62a` |
| `.claude/skills/devops/scenario-records.yaml` | absent | `87f6c71296571252c7bd82b4f0062c03be7f8396a1bf8c13c4d7a5f7edd25b28` |
| `.claude/skills/devops/scenario-summaries.md` | absent | `6b5c340edba9fbee9d2a4664749fe34de99eeae8d4c7d4fbbbd125c0681575f0` |
| `.claude/skills/devops/scenarios.md` | absent | `a6a737c6c2db84d0b905f38c3532337b9387b4d0ab70b87f2c9fe963a19dd5d9` |
| `.claude/skills/frontend/SKILL.md` | absent | `7b8f57f29bfda69ac792a645e9008b44235f008280e6a6c8e59c5ae8661e9931` |
| `.claude/skills/frontend/check_domain_skill.py` | absent | `3532f93de84972ded38ef7725dac323f45bab78e5c4735dc90d8ed84ddc9d62a` |
| `.claude/skills/frontend/scenario-records.yaml` | absent | `44f6d05d0f56d526cec2d7c0f2c8e945b5088180ceabbf16d532a495a07cdcfd` |
| `.claude/skills/frontend/scenario-summaries.md` | absent | `a3f597664ece8d9e9e690b8db9cca99360b4988df3d38619d329cfed7fc1a11d` |
| `.claude/skills/frontend/scenarios.md` | absent | `d572be6bb9143e2a70e4499771e554ba2bba16a259c2601417c84f2dac60640a` |
| `.claude/skills/ui-ux/SKILL.md` | absent | `775ff4da6694a81e318108c46d08a0f42879b12de48b4ec7e7ee13c1ced28c54` |
| `.claude/skills/ui-ux/check_domain_skill.py` | absent | `3532f93de84972ded38ef7725dac323f45bab78e5c4735dc90d8ed84ddc9d62a` |
| `.claude/skills/ui-ux/scenario-records.yaml` | absent | `9b038c094435183aa0866866222f8f5931f69e9dc0285bd28fa290514eaf146e` |
| `.claude/skills/ui-ux/scenario-summaries.md` | absent | `665707193be00eb7f888a623b55327e043bd95617a1a9279be177363c202895b` |
| `.claude/skills/ui-ux/scenarios.md` | absent | `714ecf9e1d15b597c3dd938fc2427218b52ba403cbd79e4f12cb5d5bf9caabc9` |

The three `check_domain_skill.py` copies are the same bytes (`3532f93d…`), as in the kernel (not W2-100's `538a11b5…`; the folders are separate). The three `SKILL.md` renderings carry `metadata.version` 1.2.0 (frontend) and 1.1.0 (ui-ux, devops), the kernel's versions.

**The sources (check 2, forty-five files):** the five files of each of the three skills in `template/governance/kernel/skills/<skill>/`, `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/`, each at the sha256 of W2-101's CIT-P §3.
- These are asserted on the merged tree and in the objects of `refs/heads/w2/W2-101` at `3bf1c96b47c1`.
- The commits after the verified product head `1ef54a70037a` touch only `docs/changes/W2-101-CIT-P.md` and `docs/probes/DAEO-6icv/` (asserted).

**What stays:**
- `.claude/settings.json`;
- the other skills (W2-100's four with COPIES-10 among them), `.claude/agents/` and `.claude/templates/`;
- the kernel and W2-101's own files.

## 2. The order in the hand merge (the CTO's sequence)

1. **Before the merge:** `git rev-parse --short=12 refs/heads/w2/W2-101` gives `3bf1c96b47c1` (measured at build time, the approved commit). A move of any of the forty-five sources changes check 2, and the bundle must then be rebuilt. A later commit that touches only docs (for instance the CIT-P's `owner_approval:` line) leaves check 2 green.
2. **Merge `w2/W2-101` into `w2/integrate`** in one command that commits (the merge commit, `Task: DAEO-6icv`). The merge is clean, measured on integrate `2b034037a4b6`: no conflict, merge base `aeee743e9e41`, 57 files brought, none under `.claude/`. Also measured after W2-100 and COPIES-10 (order 2): `w2/W2-100` merges clean (merge base `0a706dc4c2f1`), COPIES-10 applies, and `w2/W2-101` then merges clean too: no conflict, merge base `aeee743e9e41`, 57 files brought, none under `.claude/` (the two tickets touch disjoint files).
3. **No template commit** (§0).
4. **Write the request line.** The operator applies this ACT (§4) and commits it. Its G7 dry run sees the head after step 2.
5. **The checks.** Then close W2-101.

**What `apply.sh check` and check 2 read on each tree:**
- All fifteen targets are absent on integrate, on the merged tree and on the tree after COPIES-10, so `apply.sh check` passes on each (rehearsed).
- **The order is held by check 2.** It is red on plain integrate, and red after W2-100 and COPIES-10 alone, because W2-101's sources are absent there (rehearsed), so the operator's G8 refuses a run before the merge. After W2-101's merge it is green with or without W2-100.
- `apply.sh check` refuses a moved target: a file planted at `.claude/skills/devops/SKILL.md` gives `moved:` and exit 3 (rehearsed).

**The window,** from step 2 to the ACT's commit:
- Portability reads 15 `GENERATED_DIFFERS`, one for each absent copy, and no `SOURCE_` finding. Plain integrate reads none.
- Nine test cases are red by design (CIT-P §2, §6):
  - W2-101's `test_the_claude_copy_matches_the_kernel_source[frontend|ui-ux|devops]`;
  - W2-101's `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[frontend|ui-ux|devops]`;
  - W2-11's `test_the_skill_carries_one_version_in_all_four_places[frontend|ui-ux|devops]`.

## 3. The rehearsal (DEC-1057; `rehearsal.log`, hashed in the manifest; failures: 0)

The rehearsal ran on fresh `--no-hardlinks` clones in the CTO helper's scratchpad under `/tmp/claude-1000/`, outside the repository, `~/gov-os-runs` and `~/gov-os-worktrees`. HOME was planted at an empty folder for every apply, undo and check step.

**Order 1.** Its base is integrate `2b034037a4b6` with `w2/W2-101` `3bf1c96b47c1` merged by one `--no-ff` commit, exactly what the operator sees after the hand merge.

1. **The merged tree:**
   1. `apply.sh check` exit 0;
   2. check 1 red and check 2 green before the apply;
   3. `apply`;
   4. both checks green (15 copies, 45 sources);
   5. the changed set equals the 15 files, each at its stated new sha256;
   6. **portability exits 0 with no finding** (before the apply it read the 15 `GENERATED_DIFFERS`);
   7. `undo` removes every file, the tree is clean, and portability is back to those 15 findings;
   8. `check` and `apply` again, giving the same bytes.
2. **Plain integrate:** `apply.sh check` exit 0, check 2 red, nothing changed.
3. **A moved target:** `apply.sh check` exit 3.
4. **The gated runs,** one folder per pytest run through `tools/heavy_slot.sh`, `-p no:cacheprovider`, TMPDIR `/tmp/gov-os-cto-f388`. "Window" is W2-101's merge without this ACT; "landed" is with it.
    merged window tests/acceptance/W2-101: exit 1; 271 passed, 6 failed
    merged window tests/acceptance/W2-11: exit 1; 211 passed, 3 failed, 1 skipped
    merged window tests/unit/adapters: exit 0; 110 passed, 0 failed
    merged window tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    merged window tests/acceptance/W1-38: exit 0; 46 passed, 0 failed
    merged window tests/acceptance/W2-153: exit 0; 137 passed, 0 failed, 18 skipped
    merged window tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    merged window tests/acceptance/W2-88a: exit 0; 35 passed, 0 failed
    merged window tests/acceptance/W2-52: exit 0; 65 passed, 0 failed
    merged window tests/acceptance/W2-37: exit 0; 120 passed, 0 failed
    ok   merged landed tests/acceptance/W2-101: exit 0; 277 passed, 0 failed
    ok   merged landed tests/acceptance/W2-11: exit 0; 217 passed, 0 failed, 1 skipped
    ok   merged landed tests/unit/adapters: exit 0; 110 passed, 0 failed
    ok   merged landed tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    ok   merged landed tests/acceptance/W1-38: exit 0; 46 passed, 0 failed
    ok   merged landed tests/acceptance/W2-153: exit 0; 137 passed, 0 failed, 18 skipped
    ok   merged landed tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    ok   merged landed tests/acceptance/W2-88a: exit 0; 35 passed, 0 failed
    ok   merged landed tests/acceptance/W2-52: exit 0; 65 passed, 0 failed
    ok   merged landed tests/acceptance/W2-37: exit 0; 120 passed, 0 failed
    merged: red in the window: 9; made green by the ACT: 9; red after: 0; new red brought by the ACT: []
5. **The named acceptance cases,** with each case's own status (`-rA`), window and then landed:
   - `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[devops]`: FAILED -> PASSED
   - `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[frontend]`: FAILED -> PASSED
   - `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[ui-ux]`: FAILED -> PASSED
   - `test_the_claude_copy_matches_the_kernel_source[devops]`: FAILED -> PASSED
   - `test_the_claude_copy_matches_the_kernel_source[frontend]`: FAILED -> PASSED
   - `test_the_claude_copy_matches_the_kernel_source[ui-ux]`: FAILED -> PASSED
   - `test_the_skill_carries_one_version_in_all_four_places[devops]`: FAILED -> PASSED
   - `test_the_skill_carries_one_version_in_all_four_places[frontend]`: FAILED -> PASSED
   - `test_the_skill_carries_one_version_in_all_four_places[ui-ux]`: FAILED -> PASSED
   - The four-places case for the other 10 kernel skills: PASSED after the ACT. The generated-drift cases ran with rulesync present, so they PASSED and were not skipped.
6. **§4 literally:**
   1. stage the 15 paths;
   2. commit with the trailers;
   3. `undo`, stage and commit;
   4. an empty diff over the paths against the start.

**Order 2.** Integrate `2b034037a4b6`, then `w2/W2-100` `cdac25763613` merged `--no-ff`, then ACT-CLAUDE-COPIES-10 applied by its own `apply.sh` (check, apply, both its manifest checks green) and committed, then `w2/W2-101` merged `--no-ff`, then this bundle (the same bytes) applied.
1. order 2: w2/W2-100 cdac25763613 merged --no-ff: clean (no conflict, merge base 0a706dc4c2f1, 72 files brought)
2. COPIES-10 apply.sh check: exit 0
3. COPIES-10 apply.sh apply: exit 0
4. COPIES-10 check 1: exit 0
5. COPIES-10 check 2: exit 0
6. COPIES-10 committed (as the operator does): exit 0
7. this ACT's check 2 is red after COPIES-10 without W2-101 (the order is held): exit 1
8. this ACT's apply.sh check passes there (targets absent): exit 0
9. order 2: w2/W2-101 3bf1c96b47c1 merged --no-ff after them: clean (no conflict, merge base aeee743e9e41, 57 files brought, none under .claude/)
10. apply.sh check (targets absent): exit 0
11. check 1 before the apply (red): exit 1
12. check 2 before the apply (green with W2-100 merged as without): exit 0
13. apply.sh apply: exit 0
14. check 1 after the apply: exit 0
15. check 2 after the apply: exit 0
16. COPIES-10 check 1 still green after this ACT: exit 0
17. COPIES-10 check 2 still green after this ACT: exit 0
18. order 2: the changed set equals the touched list (15 files)
19. order 2: rulesync from the landed tree's root .rulesync renders all seven skills' folders (35 files) equal to the tree; it differs only in ['.claude/settings.json'] (as on plain integrate); so the bundle's bytes are the same in both orders
20. order 2: portability after this ACT: exit 0; 0 findings (none), all seven skills
21. order 2 landed tests/acceptance/W2-100: exit 0; 230 passed, 0 failed
22. order 2 landed tests/acceptance/W2-101: exit 0; 277 passed, 0 failed
23. order 2 landed tests/acceptance/W2-11: exit 0; 241 passed, 0 failed, 1 skipped
24. order 2 landed tests/unit/adapters: exit 0; 110 passed, 0 failed
25. order 2: W2-101's nine named cases FAILED in the window (9) and PASSED after this ACT (9 of 9)
26. order 2: W2-100's twelve named cases PASSED in the window and after (12 of 12)
27. order 2: the four-places case for the other 10 kernel skills PASSED after this ACT

The live files were unchanged by the rehearsal, and nothing was written to the planted HOME.

**The operator's read-only gates** (`~/gov-os-operator/install/`, `drafts/claude-copies-11/evidence/operator_gates.txt`):
- `validate_manifest`, `check_act` and `path_rule` pass;
- no hash mismatch and no unnamed file;
- `act_class`: class `b`, row `agents-skills-kernel` for all 15 files, no hits.

The checks name no HOME path (asserted by pattern).

**Where the rehearsal differs from the real run:**
- The real run applies in the main tree, at a later head.
- G7 and `apply.sh check` compare the before-state (absent) with the live tree again. If any of the fifteen targets exists by then, `apply.sh check` exits 3 and the bundle must be rebuilt.
- If `w2/W2-101` moves in a way that changes any of the forty-five sources, check 2 goes red and the bundle must be rebuilt (`build_claude_copies_act_11.py`, the same arguments). The builder also asserts the branch head `3bf1c96b47c1` (and `w2/W2-100` at `cdac25763613` for order 2). A docs-only commit on the branch (for instance the CIT-P's approval line) needs only that constant raised before a rebuild; the bundle's bytes would not change.
- The builder asserts that its integrate clone is at live `w2/integrate`; integrate moved once during the build (`f3d3438fcb45` to `2b034037a4b6`, `.tickets/DAEO-03ub.md` only), and the bundle was built and rehearsed on `2b034037a4b6`.
- In the main tree, an untracked `__pycache__/` in a root `.rulesync/skills/<skill>/` folder would be rendered by rulesync and read by portability as generated drift. A clean tree has none, and the bundle does not depend on it.

## 4. The operator's steps

**By the operator agent:** after the owner's yes (§0) and step 2 of §2, the CTO writes the request line in `~/gov-os-operator/queue/`. The agent then runs the bundle through its gates.

**Or by hand, by the owner,** in the main tree:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-11
sha256sum $G/manifest.json      # expect 3b4e462f1e1fdbb3fefef7559ae2c83de03eb6ba534da34cf85d40815ffde7ba
bash $G/apply.sh check && bash $G/apply.sh apply
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 15
git commit -m "ACT-CLAUDE-COPIES-11: the generated copies of W2-101's three kernel skills, frontend, ui-ux and devops (15 files)" --trailer "Task: DAEO-6icv" --trailer "Implements: DEC-315, DEC-1112" --trailer "Role: owner"
```

**What the steps print:**
- `apply.sh check` prints nothing and exits 0. If a file is already there, it prints `moved: <path>` and exits 3.
- After the apply, each manifest check prints `<path>: OK` (15 lines, then 45) and exits 0. Before the apply, check 1 prints `FAILED open or read` lines and exits 1.
- After the commit, `python3 -m gov.adapters.portability` reports no finding and exits 0.

## 5. The undo

1. `bash $G/apply.sh undo`. It removes the 15 files. Rehearsed: the tree is clean, and portability reads the window's 15 findings. The three emptied `.claude/skills/<skill>/` folders are left behind, and git does not see them.
2. `git add -A $F` and commit with `--trailer "Role: owner"`. The operator's form is `undo ACT-CLAUDE-COPIES-11 3b4e462f`.
3. The full close is W2-101's own rollback: revert the merge.

## 6. Not in this ACT

- the kernel and `.rulesync` sources (W2-101's own);
- any template commit (none is needed, §0);
- `.claude/settings.json`, `.claude/agents` and `.claude/templates`;
- W2-100's four skills and their copies (ACT-CLAUDE-COPIES-10);
- the rows F2 to F9 of W2-101's probes (`docs/probes/DAEO-6icv/`). The `.claude` copies carry `scenario-summaries.md` too, as every file of the folder (CIT-P §6: an engineer who loads the skill can read it; the harness copies from the kernel folder and leaves it out);
- any change to the kernel or the policy (CAP-33: they follow W2-101's CIT-P and the owner's approval).
