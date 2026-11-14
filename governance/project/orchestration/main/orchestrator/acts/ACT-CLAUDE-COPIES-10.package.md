# ACT-CLAUDE-COPIES-10: the generated copies of W2-100's four new kernel skills (backend, api, data, security)

## 0. The short version

- **What:** 20 generated files, all new: `.claude/skills/{backend,api,data,security}/{SKILL.md, check_domain_skill.py, scenario-records.yaml, scenario-summaries.md, scenarios.md}`.
  - Every byte comes from the product's own generation: rulesync 24.0.0, run from the root `.rulesync/` of the merged tree (portability's own GENERATE form), not by hand.
  - rulesync renders **all five files** of each skill folder. `SKILL.md` is its rendering (front matter re-folded: `name`, `description`, `version` under `metadata`); the other four are byte copies of the kernel files.
  - **Nothing live changes until it runs.**
- **The owner's line,** on its own line:

yes ACT-CLAUDE-COPIES-10 f535215e

- **Manifest sha256:** `f535215e5ba08a366fda4c0e4580e95c0d1cd1cd9150af0329372f107814c6bd`.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-10/`.
  - The builder is `drafts/claude-copies-10/build_claude_copies_act_10.py`. It is adapted from COPIES-9's `build_claude_copies_act_9.py`, with COPIES-7's handling of new files; neither is edited, and the changes are in its docstring.
  - The build log is `drafts/claude-copies-10/build.out`. The gated runs' outputs and the operator gates are in `drafts/claude-copies-10/evidence/`.
- **Class (b), claimed, as ACT-CLAUDE-COPIES-1 to -9 were.** The operator's own `act_class.classify` gives class `b`, row `agents-skills-kernel` for all 20 files, no script hits.
- **Who applies it: the owner's operator agent, on the owner's yes,** as for ACT-1 to ACT-9. The CTO cannot apply it: a session cannot write `.claude/**` (DEC-315). The by-hand route (§4) is the owner's, with `Role: owner`.
- **Under:**
  - the owner's CIT-P approval of W2-100 (pending: `yes W2-100-CIT-P 7bb4f1ac`; `docs/changes/W2-100-CIT-P.md` at `cdac25763613`, sha256 `7bb4f1ac4b0b14bc15440f189447be02c8dd80710289c1f0153dbcaa0e08e515`);
  - DEC-315, DEC-1112 (3), CAP-33;
  - also DEC-1057 (rehearsed as the operator runs it).
  - The manifest's `dec` field names DEC-315, DEC-1112 (3) and CAP-33 only. If the CTO wants the approval's DEC number in it, the bundle must be rebuilt, and the manifest sha changes.
- **When:** in the CTO's hand merge of `w2/W2-100` (head `cdac25763613`), **after the merge commit, before the checks.** Integrate never holds W2-100's four kernel skills without their copies past that sitting.
- **Review:** the operator's fixed reviewer brief applies (`ACT-CLAUDE-COPIES-10/review.md`). It is **not written yet.** The CTO starts the reviewer before asking for the owner's line. G4 refuses without the reviewer's fenced verdict block.

### No template patch, no CTO template commit

- W2-100 itself carries the root `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/` copies of all four skills, byte-equal to the kernel (CIT-P §2, §3). Its merge brings them. As in COPIES-7, the ticket carries the `.rulesync` sources and the ACT carries only `.claude/skills`.
- rulesync writes nothing under `.rulesync/` or `template/`. Its only other differing output is `.claude/settings.json` (the held-out deny, DEC-616). The same difference shows on plain integrate, and no copies ACT regenerates it.
- Portability on `template/`, read as an adopted project, gives no finding for the four skills.

## 1. The files

Every "old" is `absent` (`null` in `list.txt`): no `before/` file is written, as in COPIES-7, and the undo removes the files.

| file | old | new sha256 |
|---|---|---|
| `.claude/skills/api/SKILL.md` | absent | `9c3fa501a1fbf9251d2b9cc7902f417fe70550b061ba76610920272ca27c0f25` |
| `.claude/skills/api/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` |
| `.claude/skills/api/scenario-records.yaml` | absent | `a78358a1ffd994e9f8497c08b3cbc3b1fe5f1947095ceda0d5f3995e522bd880` |
| `.claude/skills/api/scenario-summaries.md` | absent | `7c0bc6fa0f15653b3381f3047b911f09fdfb3224d1c41e2982573f1b6007505f` |
| `.claude/skills/api/scenarios.md` | absent | `65b6460ce7b4fb628f9646e03369a40b466b1a12bf475b1a91e4de397c5fbae3` |
| `.claude/skills/backend/SKILL.md` | absent | `e6f8cd8d6af5e99b2b3bc097917a828e4835875e89d4e941a844a1712343cbf2` |
| `.claude/skills/backend/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` |
| `.claude/skills/backend/scenario-records.yaml` | absent | `cf20652e825386ca82b763e811bcd93f94cba6e5ab77a4d5d0de1ac20b8f5476` |
| `.claude/skills/backend/scenario-summaries.md` | absent | `509f68994fa29bc06f1065ff4b6ee3d62c219374efcafe1bdc82da7afe51014d` |
| `.claude/skills/backend/scenarios.md` | absent | `84b71aed50416474ecda06b9d927893b071f7ee190859b982dfe088b7d82409a` |
| `.claude/skills/data/SKILL.md` | absent | `d5b626f07ee83e9e1eadc53952270be44bfb950f54c7cf64f4f1be6b1bce32eb` |
| `.claude/skills/data/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` |
| `.claude/skills/data/scenario-records.yaml` | absent | `11436b7a7ec6ab9000c6ff1f15a9f1082e72cd2ae39c80e3016c202cb6e89589` |
| `.claude/skills/data/scenario-summaries.md` | absent | `cf701bd3ed5523426f1d1e9e2a82f18b309fcddf925c69b34d9fe346d110b135` |
| `.claude/skills/data/scenarios.md` | absent | `514c5e473f2ef48346c9a69b5c30de3122ce997a65095bc0754ca302ef711418` |
| `.claude/skills/security/SKILL.md` | absent | `973c40f5701e996877e5cb037ce4ff450c30f8635ef9a678be30782cd38dad61` |
| `.claude/skills/security/check_domain_skill.py` | absent | `538a11b5959753b5a9f145d8752d9e776a40245f57cfc9e0371ad248e4459382` |
| `.claude/skills/security/scenario-records.yaml` | absent | `dfcebf97d06b2d1709e7250d72fa2dbfe029e212aefb2a9270a867a4625359df` |
| `.claude/skills/security/scenario-summaries.md` | absent | `4791045bd5b06fac8b4b6eb7d4f9f81f012030e4caed11b8d75ce2a86552e7c6` |
| `.claude/skills/security/scenarios.md` | absent | `477d93046c27d03668d98e848fd248c45d0cdcc59d57050cabd9737e179cb3ea` |

The four `check_domain_skill.py` copies are the same bytes (`538a11b5…`), as in the kernel. The four `SKILL.md` renderings carry `metadata.version` 1.0.1 (backend, security) and 1.0.2 (api, data), the kernel's versions.

**The sources (check 2, sixty files):** the five files of each of the four skills in `template/governance/kernel/skills/<skill>/`, `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/`, each at the sha256 of W2-100's CIT-P §3.
- These are asserted on the merged tree and in the objects of `refs/heads/w2/W2-100` at `cdac25763613`.
- The commits after the verified product head `f7637bd03e25` touch only `docs/changes/W2-100-CIT-P.md` and `docs/probes/DAEO-uw5h/` (asserted).

**What stays:**
- `.claude/settings.json`;
- the other skills, `.claude/agents/` and `.claude/templates/`;
- the kernel and W2-100's own files.

## 2. The order in the hand merge (the CTO's sequence)

1. **Before the merge:** `git rev-parse --short=12 refs/heads/w2/W2-100` gives `cdac25763613` (measured at build time, the approved commit). A move of any of the sixty sources changes check 2, and the bundle must then be rebuilt. A later commit that touches only docs (for instance the CIT-P's `owner_approval:` line) leaves check 2 green.
2. **Merge `w2/W2-100` into `w2/integrate`** in one command that commits (the merge commit, `Task: DAEO-uw5h`). The merge is clean, measured on integrate `f3d3438fcb45`: no conflict, merge base `0a706dc4c2f1`, 72 files brought, none under `.claude/`.
3. **No template commit** (§0).
4. **Write the request line.** The operator applies this ACT (§4) and commits it. Its G7 dry run sees the head after step 2.
5. **The checks.** Then close W2-100.

**What `apply.sh check` and check 2 read on each tree:**
- All twenty targets are absent on integrate and on the merged tree, so `apply.sh check` passes on both (rehearsed).
- **The order is held by check 2.** It is red on plain integrate because W2-100's sources are absent there (rehearsed), so the operator's G8 refuses a run before the merge.
- `apply.sh check` refuses a moved target: a file planted at `.claude/skills/api/SKILL.md` gives `moved:` and exit 3 (rehearsed).

**The window,** from step 2 to the ACT's commit:
- Portability reads 20 `GENERATED_DIFFERS`, one for each absent copy, and no `SOURCE_` finding. Plain integrate reads none.
- Twelve test cases are red by design (CIT-P §2, §6):
  - W2-100's `test_the_claude_copy_matches_the_kernel_source[backend|api|data|security]`;
  - W2-100's `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[backend|api|data|security]`;
  - W2-11's `test_the_skill_carries_one_version_in_all_four_places[backend|api|data|security]`.

## 3. The rehearsal (DEC-1057; `rehearsal.log`, hashed in the manifest; failures: 0)

The rehearsal ran on fresh `--no-hardlinks` clones in the CTO helper's scratchpad under `/tmp/claude-1000/`, outside the repository, `~/gov-os-runs` and `~/gov-os-worktrees`. HOME was planted at an empty folder for every apply step. Its base is integrate `f3d3438fcb45` with `w2/W2-100` `cdac25763613` merged by one `--no-ff` commit, exactly what the operator sees after the hand merge.

1. **The merged tree:**
   1. `apply.sh check` exit 0;
   2. check 1 red and check 2 green before the apply;
   3. `apply`;
   4. both checks green (20 copies, 60 sources);
   5. the changed set equals the 20 files, each at its stated new sha256;
   6. **portability exits 0 with no finding** (before the apply it read the 20 `GENERATED_DIFFERS`);
   7. `undo` removes every file, the tree is clean, and portability is back to those 20 findings;
   8. `check` and `apply` again, giving the same bytes.
2. **Plain integrate:** `apply.sh check` exit 0, check 2 red, nothing changed.
3. **A moved target:** `apply.sh check` exit 3.
4. **The gated runs,** one folder per pytest run through `tools/heavy_slot.sh`, `-p no:cacheprovider`, TMPDIR `/tmp/gov-os-cto-f388`. "Window" is W2-100's merge without this ACT; "landed" is with it.
    merged window tests/acceptance/W2-100: exit 1; 222 passed, 8 failed
    merged window tests/acceptance/W2-11: exit 1; 215 passed, 4 failed, 1 skipped
    merged window tests/unit/adapters: exit 0; 110 passed, 0 failed
    merged window tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    merged window tests/acceptance/W1-38: exit 0; 46 passed, 0 failed
    merged window tests/acceptance/W2-153: exit 0; 137 passed, 0 failed, 18 skipped
    merged window tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    merged window tests/acceptance/W2-88a: exit 0; 35 passed, 0 failed
    merged window tests/acceptance/W2-52: exit 0; 65 passed, 0 failed
    merged window tests/acceptance/W2-37: exit 0; 120 passed, 0 failed
    ok   merged landed tests/acceptance/W2-100: exit 0; 230 passed, 0 failed
    ok   merged landed tests/acceptance/W2-11: exit 0; 223 passed, 0 failed, 1 skipped
    ok   merged landed tests/unit/adapters: exit 0; 110 passed, 0 failed
    ok   merged landed tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    ok   merged landed tests/acceptance/W1-38: exit 0; 46 passed, 0 failed
    ok   merged landed tests/acceptance/W2-153: exit 0; 137 passed, 0 failed, 18 skipped
    ok   merged landed tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    ok   merged landed tests/acceptance/W2-88a: exit 0; 35 passed, 0 failed
    ok   merged landed tests/acceptance/W2-52: exit 0; 65 passed, 0 failed
    ok   merged landed tests/acceptance/W2-37: exit 0; 120 passed, 0 failed
    merged: red in the window: 12; made green by the ACT: 12; red after: 0; new red brought by the ACT: []
5. **The three named acceptance cases,** with each case's own status (`-rA`), window and then landed:
   - `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[api]`: FAILED -> PASSED
   - `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[backend]`: FAILED -> PASSED
   - `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[data]`: FAILED -> PASSED
   - `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[security]`: FAILED -> PASSED
   - `test_the_claude_copy_matches_the_kernel_source[api]`: FAILED -> PASSED
   - `test_the_claude_copy_matches_the_kernel_source[backend]`: FAILED -> PASSED
   - `test_the_claude_copy_matches_the_kernel_source[data]`: FAILED -> PASSED
   - `test_the_claude_copy_matches_the_kernel_source[security]`: FAILED -> PASSED
   - `test_the_skill_carries_one_version_in_all_four_places[api]`: FAILED -> PASSED
   - `test_the_skill_carries_one_version_in_all_four_places[backend]`: FAILED -> PASSED
   - `test_the_skill_carries_one_version_in_all_four_places[data]`: FAILED -> PASSED
   - `test_the_skill_carries_one_version_in_all_four_places[security]`: FAILED -> PASSED
   - The four-places case for the other 10 kernel skills: PASSED after the ACT. The generated-drift cases ran with rulesync present, so they PASSED and were not skipped.
6. **§4 literally:**
   1. stage the 20 paths;
   2. commit with the trailers;
   3. `undo`, stage and commit;
   4. an empty diff over the paths against the start.
7. The live files were unchanged by the rehearsal, and nothing was written to the planted HOME.

**The operator's read-only gates** (`~/gov-os-operator/install/`, `drafts/claude-copies-10/evidence/operator_gates.txt`):
- `validate_manifest`, `check_act` and `path_rule` pass;
- no hash mismatch and no unnamed file;
- `act_class`: class `b`, row `agents-skills-kernel` for all 20 files, no hits.

The checks name no HOME path (asserted by pattern).

**Where the rehearsal differs from the real run:**
- The real run applies in the main tree, at a later head.
- G7 and `apply.sh check` compare the before-state (absent) with the live tree again. If any of the twenty targets exists by then, `apply.sh check` exits 3 and the bundle must be rebuilt.
- If `w2/W2-100` moves in a way that changes any of the sixty sources, check 2 goes red and the bundle must be rebuilt (`build_claude_copies_act_10.py`, the same arguments). The builder also asserts the branch head `cdac25763613`. A docs-only commit on the branch (for instance the CIT-P's approval line) needs only that constant raised before a rebuild; the bundle's bytes would not change.
- In the main tree, an untracked `__pycache__/` in a root `.rulesync/skills/<skill>/` folder would be rendered by rulesync and read by portability as generated drift. A clean tree has none, and the bundle does not depend on it.

## 4. The operator's steps

**By the operator agent:** after the owner's yes (§0) and step 2 of §2, the CTO writes the request line in `~/gov-os-operator/queue/`. The agent then runs the bundle through its gates.

**Or by hand, by the owner,** in the main tree:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-10
sha256sum $G/manifest.json      # expect f535215e5ba08a366fda4c0e4580e95c0d1cd1cd9150af0329372f107814c6bd
bash $G/apply.sh check && bash $G/apply.sh apply
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 20
git commit -m "ACT-CLAUDE-COPIES-10: the generated copies of W2-100's four kernel skills, backend, api, data and security (20 files)" --trailer "Task: DAEO-uw5h" --trailer "Implements: DEC-315, DEC-1112" --trailer "Role: owner"
```

**What the steps print:**
- `apply.sh check` prints nothing and exits 0. If a file is already there, it prints `moved: <path>` and exits 3.
- After the apply, each manifest check prints `<path>: OK` (20 lines, then 60) and exits 0. Before the apply, check 1 prints `FAILED open or read` lines and exits 1.
- After the commit, `python3 -m gov.adapters.portability` reports no finding and exits 0.

## 5. The undo

1. `bash $G/apply.sh undo`. It removes the 20 files. Rehearsed: the tree is clean, and portability reads the window's 20 findings. The four emptied `.claude/skills/<skill>/` folders are left behind, and git does not see them.
2. `git add -A $F` and commit with `--trailer "Role: owner"`. The operator's form is `undo ACT-CLAUDE-COPIES-10 f535215e`.
3. The full close is W2-100's own rollback: revert the merge.

## 6. Not in this ACT

- the kernel and `.rulesync` sources (W2-100's own);
- any template commit (none is needed, §0);
- `.claude/settings.json`, `.claude/agents` and `.claude/templates`;
- P-W2-100-F2: the harness copying `scenario-summaries.md` into a `gov skilleval` session. The `.claude` copies carry that file too, as every file of the folder (CIT-P §6);
- any change to the kernel or the policy (CAP-33: they follow W2-100's CIT-P and the owner's approval).
