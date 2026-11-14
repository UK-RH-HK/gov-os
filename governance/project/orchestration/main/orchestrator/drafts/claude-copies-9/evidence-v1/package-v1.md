# ACT-CLAUDE-COPIES-9: the generated copies of W2-37's approved change-skill bytes (version 1.1.0)

## 0. The short version

- **What:** 2 generated files, both existing and both replaced: `.rulesync/skills/change/SKILL.md` (a byte copy of `template/.rulesync/skills/change/SKILL.md`) and `.claude/skills/change/SKILL.md` (rulesync 24.0.0's rendering from that `.rulesync/` source, portability's own GENERATE form; its front matter re-folded, `version` under `metadata`). Every byte comes from the product's own generation, not by hand. **Nothing live changes until it runs.**
- **The owner's line,** on its own line:

yes ACT-CLAUDE-COPIES-9 dc314cf7

- **Manifest sha256:** `dc314cf75fe722d07465118de3b34c851c870d7ea87bbe19b0c740ec5a1036c6`.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-9/`. The builder is `drafts/claude-copies-9/build_claude_copies_act_9.py`, adapted from COPIES-7's `build_claude_copies_act_7.py` (not edited; the changes are listed in its docstring). The build log is `drafts/claude-copies-9/build.out`; the gated runs' outputs and the operator gates are in `drafts/claude-copies-9/evidence/`.
- **Class (b), claimed, as ACT-CLAUDE-COPIES-1 to -8 were.** The operator's own `act_class.classify` gives class `b`: row `agents-skills-kernel` for `.claude/skills/change/SKILL.md`, row `rulesync-other` for `.rulesync/skills/change/SKILL.md`, no script hits.
- **Who applies it: the owner's operator agent, on the owner's yes,** as for ACT-1 to ACT-8. The CTO cannot apply it: a session cannot write `.claude/**` (DEC-315), and `.rulesync/**` is a control path (b). The by-hand route (§4) is the owner's, with `Role: owner`.
- **Under:** the owner's CIT-P approval of W2-37 ("yes W2-37 CIT-P a25b02a7, version 1.1.0", DEC-1166 (4)), whose approved head is `7bde87727b0f`; DEC-315, DEC-1112 (3), DEC-1156 (3), CAP-33. Also DEC-1057 (rehearsed as the operator runs it).
- **When:** right after the CTO's hand merge of `w2/W2-37` (head `7bde87727b0f`) into `w2/integrate`, **after the merge commit, before the checks.** Integrate never holds W2-37's new change skill without its copies past that sitting.
- **Review:** the operator's fixed reviewer brief applies (`ACT-CLAUDE-COPIES-9/review.md`). It is **not written yet.** The CTO starts the reviewer before asking for the owner's line. G4 refuses without the reviewer's fenced verdict block.

### No template patch, no CTO template commit

- W2-37 itself carries `template/governance/kernel/skills/change/SKILL.md` and `template/.rulesync/skills/change/SKILL.md`, both at `cdf43a49…` (CIT-P §3). Its merge brings them. The root `.rulesync` copy is not in W2-37's diff; this ACT writes it, as a byte copy of the template file.
- rulesync writes nothing under `.rulesync/` or `template/`. Its differing output on the merged tree is `.claude/skills/change/SKILL.md` (this ACT's) and two drifts that integrate already has and no copies ACT here covers (see "Left alone").

## 1. The files

| file | old sha256 | new sha256 |
|---|---|---|
| `.rulesync/skills/change/SKILL.md` | `2af36b728573e930ff4c5ea689f3a66faff11d342aced19a6a1babbfe16dc982` | `cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76` |
| `.claude/skills/change/SKILL.md` | `e22fd92ff3a6f88d15850ba01046f4f66bf0399e1865ca1bfd51258e0569a352` | `dc4d01de95fb22703f3ef2db79ce5ca516990d641bb6f425af1732cce99f7cd8` |

**The sources (check 2):** the two template files, at the owner-approved bytes: `template/governance/kernel/skills/change/SKILL.md` and `template/.rulesync/skills/change/SKILL.md`, each `cdf43a49…`. The builder asserts both on the merged tree and against `refs/heads/w2/W2-37` at `7bde87727b0f`.

**The generated file equals the lead's expected bytes:** rulesync's rendering is `dc4d01de…`, the hash of `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/changes/expected-claude-change-SKILL-1.1.0.md` (the builder stops with both hashes if they differ; they do not).

**What stays:**
- `.claude/settings.json` (the held-out deny, DEC-616);
- the other skills, `.claude/agents/` and `.claude/templates/`;
- the kernel and W2-37's own files.

**Left alone: `.claude/skills/adopt/SKILL.md`.** On plain integrate `aa4d460fffad` portability already reads `GENERATED_DIFFERS` for it (rulesync's rendering of the root adopt source is not the tracked copy, since W2-88a's source change). It is not W2-37's and not this ACT's. It is why portability exits 1 before and after this ACT; after it, the adopt finding is the only one.

## 2. The order in the hand merge (the CTO's sequence)

1. **Before the merge:** `git rev-parse --short=12 refs/heads/w2/W2-37` gives `7bde87727b0f` (measured at build time, the approved commit). A move of either template source changes check 2 and the bundle must be rebuilt.
2. **Merge `w2/W2-37` into `w2/integrate`** in one command that commits (the merge commit, with the ticket's Task trailer). The merge is clean, measured on integrate `aa4d460fffad`.
3. **No template commit** (§0).
4. **Write the request line.** The operator applies this ACT (§4) and commits it. Its G7 dry run sees the head after step 2.
5. **The checks.** Then close W2-37.

**What `apply.sh check` and check 2 read on each tree:**
- Both targets are at their old bytes on integrate and on the merged tree (W2-37 touches neither), so `apply.sh check` passes on both (rehearsed).
- **The order is held by check 2.** It is red on plain integrate because the template sources are the old bytes there (rehearsed), so the operator's G8 refuses a run before the merge.
- `apply.sh check` refuses a moved target (a `.claude` copy with one byte appended gives `moved:` and exit 3, rehearsed).

**The window,** from step 2 to the ACT's commit: portability reads `SOURCE_DIFFERS` for `.rulesync/skills/change/SKILL.md` (it differs from the kernel file), beside integrate's own adopt finding. Two cases are red:
- W2-37's `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question[claude-copy]`;
- W2-11's `test_w2_11_skills.py::test_the_skill_carries_one_version_in_all_four_places[change]`.

## 3. The rehearsal (DEC-1057; `rehearsal.log`, hashed in the manifest; failures: 0)

The rehearsal ran on fresh `--no-hardlinks` clones under `/tmp/claude-1000/copies9-run`, outside the repository and `~/gov-os-runs`. HOME was planted at an empty folder for every apply step. Its base is integrate `aa4d460fffad` with `w2/W2-37` `7bde87727b0f` merged by one `--no-ff` commit, exactly what the operator sees after the hand merge.

1. **The merged tree:**
   1. `apply.sh check` exit 0;
   2. check 1 red and check 2 green before the apply;
   3. `apply`;
   4. both checks green;
   5. the changed set equals the 2 files, each at its stated new sha256;
   6. portability shows no change-skill finding, and its one other finding (adopt) is unchanged;
   7. `undo` byte for byte, the tree clean, and portability back to the merged tree's own 2 findings;
   8. `check` and `apply` again, giving the same bytes.
2. **Plain integrate:** `apply.sh check` exit 0, check 2 red, nothing changed.
3. **A moved target:** `apply.sh check` exit 3.
4. **The gated runs,** one folder per pytest run through `tools/heavy_slot.sh`, `-p no:cacheprovider`, TMPDIR outside the repository. "Window" is W2-37's merge without this ACT; "landed" is with it.
    merged window tests/acceptance/W2-37: exit 1; 98 passed, 1 failed, 21 skipped
    merged window tests/unit/impact: exit 0; 42 passed, 0 failed
    merged window tests/unit/adapters: exit 0; 102 passed, 0 failed
    merged window tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    merged window tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
    merged window tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
    merged window tests/acceptance/W2-11: exit 1; 198 passed, 1 failed, 1 skipped
    merged window tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    ok   merged landed tests/acceptance/W2-37: exit 0; 99 passed, 0 failed, 21 skipped
    ok   merged landed tests/unit/impact: exit 0; 42 passed, 0 failed
    ok   merged landed tests/unit/adapters: exit 0; 102 passed, 0 failed
    ok   merged landed tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    ok   merged landed tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
    ok   merged landed tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
    ok   merged landed tests/acceptance/W2-11: exit 0; 199 passed, 0 failed, 1 skipped
    ok   merged landed tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    merged: red in the window: 2; made green by the ACT: 2; red after: 0; new red brought by the ACT: []
5. **§4 literally:**
   1. stage the 2 paths;
   2. commit with the trailers;
   3. `undo`, stage and commit;
   4. an empty diff over the paths against the start.
6. The live files were unchanged by the rehearsal, and nothing was written to the planted HOME.

**What the gated runs show:**
- **The ACT makes 2 cases green:** W2-37's claude-copy routing case and W2-11's four-places version case. It brings no new red.
- **Not run here:** W1-33 deselects 2 cases and W1-38 deselects 159, adapters 40, by `tests/conftest.py`'s own selection.
- **No full-landed or other-order rehearsal:** integrate already holds COPIES-6, -7 and -8, and this ACT's two paths are disjoint from theirs.

**The operator's read-only gates** (`~/gov-os-operator/install/`, `drafts/claude-copies-9/evidence/operator_gates.txt`):
- `validate_manifest`, `check_act` and `path_rule` pass;
- no hash mismatch and no unnamed file;
- `act_class`: class `b`, rows `agents-skills-kernel` and `rulesync-other`, no hits.

The checks name no HOME path (asserted by pattern).

**Where the rehearsal differs from the real run:**
- The real run applies in the main tree, at a later head.
- G7 and `apply.sh check` compare the before-hashes with the live files again. If `.rulesync/skills/change/SKILL.md` or `.claude/skills/change/SKILL.md` moves, `apply.sh check` exits 3 and the bundle must be rebuilt.
- If `w2/W2-37` moves in a way that changes either template source, check 2 goes red and the bundle must be rebuilt (`build_claude_copies_act_9.py`, the same arguments).

## 4. The operator's steps

**By the operator agent:** after the owner's yes (§0) and step 2 of §2, the CTO writes the request line in `~/gov-os-operator/queue/`. The agent then runs the bundle through its gates.

**Or by hand, by the owner,** in the main tree:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-9
sha256sum $G/manifest.json      # expect dc314cf75fe722d07465118de3b34c851c870d7ea87bbe19b0c740ec5a1036c6
bash $G/apply.sh check && bash $G/apply.sh apply
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 2
git commit -m "ACT-CLAUDE-COPIES-9: the .rulesync and .claude copies of W2-37's change skill, version 1.1.0 (2 files)" --trailer "Task: <W2-37's Task id>" --trailer "Implements: DEC-1166, DEC-315" --trailer "Role: owner"
```

**What the steps print:**
- `apply.sh check` prints nothing and exits 0. If a file has moved, it prints `moved: <path>` and exits 3.
- After the apply, each manifest check prints `<path>: OK` (2 lines, then 2) and exits 0. Before the apply, check 1 prints `FAILED` lines and exits 1.
- After the commit, `python3 -m gov.adapters.portability` reports no change-skill finding (it still reads integrate's adopt finding).

## 5. The undo

1. `bash $G/apply.sh undo`. It restores the 2 files to their before-bytes (rehearsed: the tree is clean, and portability reads the window's findings).
2. `git add -A $F` and commit with `--trailer "Role: owner"`. The operator's form is `undo ACT-CLAUDE-COPIES-9 dc314cf7`.
3. The full close is W2-37's own rollback: revert the merge.

## 6. Not in this ACT

- the template sources (W2-37's own, by its merge);
- any template commit (none is needed, §0);
- `.claude/skills/adopt/SKILL.md`'s drift, `.claude/settings.json`, `.claude/agents` and `.claude/templates`;
- any change to the kernel or the policy (CAP-33: they follow W2-37's CIT-P and the owner's approval).
