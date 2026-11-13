# ACT-CLAUDE-COPIES-7: the generated copy of W2-98's new kernel skill spec-writing

## 0. The short version

- **What:** 4 generated files, all new: `.claude/skills/spec-writing/{SKILL.md, check_spec.py, imports.yaml, spec-form.md}`. Every byte comes from the product's own generation: rulesync 24.0.0, run from the root `.rulesync/` (portability's own GENERATE form). `SKILL.md` is rulesync's rendering (its front matter re-folded, `version` under `claudecode`); the other three are byte copies of the kernel files. **Nothing live changes until it runs.**
- **The owner's line,** on its own line:

yes ACT-CLAUDE-COPIES-7 78de1c5f

- **Manifest sha256:** `78de1c5fe9198ea3a3982e7d8557397b5b5ddce8682e2f85b9b6cfc5c4f1fb02`.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-7/`. The builder is `drafts/claude-copies-7/build_claude_copies_act_7.py`, adapted from COPIES-6's `build_v2.py` with COPIES-5's skill handling; neither is edited, and the changes are listed in its docstring. The build log is `drafts/claude-copies-7/build.out`; the gated runs' outputs and the operator gates are in `drafts/claude-copies-7/evidence/`.
- **Class (b), claimed, as ACT-CLAUDE-COPIES-1 to -6 were.** The operator's own `act_class.classify` gives class `b`, row `agents-skills-kernel` for all four files, no script hits.
- **Who applies it: the owner's operator agent, on the owner's yes,** as for ACT-1 to ACT-6. The CTO cannot apply it: a session cannot write `.claude/**` (DEC-315). The by-hand route (§4) is the owner's, with `Role: owner`.
- **Under:** the owner's CIT-P approval of W2-98 at `3a86f11c3981` (2026-11-13), DEC-315, DEC-1112 (3), DEC-1156 (3), CAP-33. Also DEC-1057 (rehearsed as the operator runs it).
- **When:** in the CTO's hand merge of W2-98, **after the merge commit, before the checks.** Integrate never holds W2-98's kernel skill without its copy past that sitting.
- **Review:** the operator's fixed reviewer brief applies (`ACT-CLAUDE-COPIES-7/review.md`). It is **not written yet.** The CTO starts the reviewer before asking for the owner's line. G4 refuses without the reviewer's fenced verdict block.

### No template patch, no CTO template commit

The brief allowed for a template patch beside the bundle, as in COPIES-6. The generation was measured, and none is needed:
- W2-98 itself carries the root `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/` copies (CIT-P §2). Its merge brings them, byte-equal to the kernel. The precedent is W2-11 and COPIES-5: the ticket carried the `.rulesync/skills` sources, and the ACT carried only `.claude/skills`.
- A skill has no `compose()`. Portability compares a kernel skill with its `.rulesync` source by bytes (`SKILL.md` by front matter and body).
- rulesync writes nothing under `.rulesync/` or `template/`. Its only other differing output is `.claude/settings.json` (the held-out deny, DEC-616), which no copies ACT regenerates.
- `compose()` for the six roles that have a source on the merged tree gives COPIES-6's after bytes (COPIES-8's for the orchestrator). So W2-98 changes no role composition, and no role source belongs in this ACT.
- Portability on `template/`, read as an adopted project, gives no spec-writing finding.

## 1. The files

| file | old sha256 | new sha256 |
|---|---|---|
| `.claude/skills/spec-writing/SKILL.md` | `null (new)` | `6b81479132379c32ab6b6419dea65492250da231fbbbee4b911a22c516a0955c` |
| `.claude/skills/spec-writing/check_spec.py` | `null (new)` | `b18ebd98028e33aa06c2b3aba634e0a7b012122db304b48436c616aa1c15f310` |
| `.claude/skills/spec-writing/imports.yaml` | `null (new)` | `3ddd0e1ab98d22585922395b0915014db4f048994be757b8283422986f9f9cff` |
| `.claude/skills/spec-writing/spec-form.md` | `null (new)` | `9174042b22312e69aac2fe4b02ca16e48216566371cf22e781a3985f3c604e4f` |

**The sources (check 2):** the twelve files of CIT-P §3, at the owner-approved bytes:
- `template/governance/kernel/skills/spec-writing/*`;
- `.rulesync/skills/spec-writing/*`;
- `template/.rulesync/skills/spec-writing/*`.

Each set of four is `SKILL.md 34500d5e…`, `check_spec.py b18ebd98…`, `imports.yaml 3ddd0e1a…` and `spec-form.md 9174042b…`. The builder asserts all twelve on the merged tree against the CIT-P's table.

**What stays:**
- `.claude/settings.json`;
- `.claude/agents/` and `.claude/templates/` (COPIES-6, landed as `36d1a151b`; COPIES-8, pending);
- the kernel;
- W2-98's own files.

## 2. The order in the hand merge (the CTO's sequence)

1. **Before the merge:** check W2-98's head and its kernel bytes.
   - `git rev-parse --short=12 refs/heads/w2/W2-98` gave `3a86f11c3981` at build time, the approved commit.
   - The twelve sources are byte for byte the CIT-P §3 hashes (measured).
   - The CIT-P's `owner_approval:` line is to be written before the merge (its front matter says so). That is a `docs/` edit and does not move check 2. Any kernel or `.rulesync` byte that moves does, and the bundle must then be rebuilt.
2. **Merge `w2/W2-98` into `w2/integrate`** in one command that commits (the merge commit, `Task: DAEO-wi46`). The merge is clean, measured on integrate `df9d442e8f82` (the build) and on `2bf4430f41d4` (re-checked after COPIES-6 landed).
3. **No template commit** (§0).
4. **Write the request line.** The operator applies this ACT (§4) and commits it. Its G7 dry run sees the head after step 2.
5. **The checks** (§3's folders and portability). Then close W2-98.

**What `apply.sh check` and check 2 read on each tree:**
- The four targets are absent on integrate and on the merged tree, so `apply.sh check` passes on both (rehearsed).
- **The order is held by check 2,** the twelve sources. It is red on plain integrate because the files are absent (rehearsed), so the operator's G8 refuses a run before the merge.
- **The ACT is independent of COPIES-6 and COPIES-8.** The paths are disjoint. It was rehearsed before them, after them, and in the other order, with the same bytes and portability exit 0 once all three stand.

**The window,** from step 2 to the ACT's commit: portability reads 4 `GENERATED_DIFFERS` (the four `.claude/skills/spec-writing` files). Three cases are red, as CIT-P §5 says:
- W2-98's `test_the_claude_copy_matches_the_kernel_source`;
- W2-98's `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`;
- W2-11's `test_the_skill_carries_one_version_in_all_four_places[spec-writing]`.

## 3. The rehearsal (DEC-1057; `rehearsal.log`, hashed in the manifest; failures: 0)

The rehearsal ran on fresh `--no-hardlinks` clones under `/tmp/claude-1000/act-copies-7-360720/build`, outside the repository and `~/gov-os-runs`. HOME was planted at an empty folder for every apply step.

1. **The merged tree** (integrate `df9d442e8f82` with W2-98 `3a86f11c3981` merged; COPIES-6 and -8 not yet applied there):
   1. `apply.sh check` exit 0;
   2. check 1 red and check 2 green before the apply;
   3. `apply`;
   4. both checks green;
   5. the changed set equals the 4 files, each at its stated new sha256;
   6. portability shows no spec-writing finding, and its 11 other findings (COPIES-6's and -8's window) are unchanged;
   7. `undo` byte for byte, with the tree clean, and portability back to the base's 15 findings;
   8. `check` and `apply` again, giving the same bytes.
2. **Plain integrate:** `apply.sh check` exit 0, check 2 red, nothing changed.
3. **The fully landed tree** (the merged tree with COPIES-6 and then COPIES-8 applied by their own `apply.sh`):
   - before this ACT, portability reads exactly the 4 spec-writing findings;
   - after it, portability exits 0 with no findings.
4. **The other order** (this ACT first, then COPIES-6 and -8): every check is green, portability exits 0, and the copies have the same bytes.
5. **The gated runs,** one folder per pytest run through `tools/heavy_slot.sh`. Each used `-p no:cacheprovider`, with TMPDIR outside the repository. "Window" is W2-98's merge without this ACT; "landed" is with it.
    merged window tests/acceptance/W2-98: exit 1; 500 passed, 2 failed
    merged window tests/unit/adapters: exit 1; 100 passed, 2 failed
    merged window tests/acceptance/W1-33: exit 1; 106 passed, 6 failed
    merged window tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
    merged window tests/acceptance/W2-153: exit 1; 53 passed, 13 failed
    merged window tests/acceptance/W2-11: exit 1; 197 passed, 1 failed, 1 skipped
    ok   merged landed tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    ok   merged landed tests/unit/adapters: exit 1; 100 passed, 2 failed
    ok   merged landed tests/acceptance/W1-33: exit 1; 106 passed, 6 failed
    ok   merged landed tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
    ok   merged landed tests/acceptance/W2-153: exit 1; 53 passed, 13 failed
    ok   merged landed tests/acceptance/W2-11: exit 0; 199 passed, 0 failed, 1 skipped
    merged: red in the window: 24; made green by the ACT: 3; red after: 21; new red brought by the ACT: []
    full window tests/acceptance/W2-98: exit 1; 500 passed, 2 failed
    full window tests/unit/adapters: exit 0; 102 passed, 0 failed
    full window tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    full window tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
    full window tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
    full window tests/acceptance/W2-11: exit 1; 197 passed, 1 failed, 1 skipped
    ok   full landed tests/acceptance/W2-98: exit 0; 502 passed, 0 failed
    ok   full landed tests/unit/adapters: exit 0; 102 passed, 0 failed
    ok   full landed tests/acceptance/W1-33: exit 0; 112 passed, 0 failed
    ok   full landed tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
    ok   full landed tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
    ok   full landed tests/acceptance/W2-11: exit 0; 199 passed, 0 failed, 1 skipped
    full: red in the window: 3; made green by the ACT: 3; red after: 0; new red brought by the ACT: []
6. **§4 literally:**
   1. stage the 4 paths;
   2. commit with the trailers;
   3. `undo`, stage and commit;
   4. an empty diff over the paths against the start.
7. The live files were unchanged by the rehearsal, and nothing was written to the planted HOME.

**What the gated runs show:**
- **The ACT makes 3 cases green:** CIT-P §5's two W2-98 cases and the W2-11 case. It brings no new red on either tree.
- **The 21 reds left on the merged tree are not this ACT's.** They are W2-33's window, which COPIES-6 and -8 close: W1-33 6, W2-153 13 and adapters 2. On the fully landed tree every suite is green.
- **Not run here:** W1-38 deselects 159 cases by `tests/conftest.py`'s own selection.

**Re-checked after the build on today's integrate** (`2bf4430f41d4`: COPIES-6 landed as `36d1a151b`, COPIES-8 pending), with W2-98 merged (clean):
- a fresh rulesync run gives the 4 after files byte for byte;
- `apply.sh check` exit 0;
- check 1 red and check 2 green before the apply, both green after;
- portability shows no spec-writing finding, only COPIES-8's 3 (`.rulesync/subagents/orchestrator.md`, `.claude/templates/role-lead.md`, `.claude/templates/role-cto.md`).

The suites on that tree with this ACT applied:
- W2-98: 502 passed, 0 failed;
- W2-11: 199 passed, 1 skipped;
- W1-33: 112 passed;
- W1-38: 42 passed (`drafts/claude-copies-7/evidence/now-landed.txt`);
- adapters: 2 failed;
- W2-153: 2 failed.

The 4 reds are COPIES-8's pending orchestrator source (integrate's own close note `3ec28e859` names them).

**The operator's read-only gates** (`~/gov-os-operator/install/`, `drafts/claude-copies-7/evidence/operator_gates.txt`):
- `validate_manifest`, `check_act` and `path_rule` pass;
- no hash mismatch and no unnamed file;
- `act_class`: class `b`, row `agents-skills-kernel`, no hits.

The checks name no HOME path (asserted by pattern).

**Where the rehearsal differs from the real run:**
- The real run applies in the main tree, at a later head.
- G7 and `apply.sh check` compare the before-hashes (absent) with the live files again.
- If W2-98 moves in a way that changes any of the twelve sources, check 2 goes red and the bundle must be rebuilt (`build_claude_copies_act_7.py`, the same arguments).

## 4. The operator's steps

**By the operator agent:** after the owner's yes (§0) and step 2 of §2, the CTO writes the request line in `~/gov-os-operator/queue/`. The agent then runs the bundle through its gates.

**Or by hand, by the owner,** in the main tree:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-7
sha256sum $G/manifest.json      # expect 78de1c5fe9198ea3a3982e7d8557397b5b5ddce8682e2f85b9b6cfc5c4f1fb02
bash $G/apply.sh check && bash $G/apply.sh apply
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 4
git commit -m "ACT-CLAUDE-COPIES-7: the .claude/skills copy of W2-98's kernel skill spec-writing (4 files)" --trailer "Task: DAEO-wi46" --trailer "Implements: DEC-1112, DEC-315" --trailer "Role: owner"
```

**What the steps print:**
- `apply.sh check` prints nothing and exits 0. If a file has moved, it prints `moved: <path>` and exits 3.
- After the apply, each manifest check prints `<path>: OK` (4 lines, then 12) and exits 0. Before the apply, check 1 prints `FAILED` lines and exits 1.
- After the commit, `python3 -m gov.adapters.portability` reports no spec-writing finding. It exits 0 once COPIES-8 has also landed.

## 5. The undo

1. `bash $G/apply.sh undo`. It removes the 4 new files (rehearsed: the tree is clean, and portability reads the window's 4 spec-writing findings).
2. `git add -A $F` and commit with `--trailer "Role: owner"`. The operator's form is `undo ACT-CLAUDE-COPIES-7 78de1c5f`.
3. The full close is W2-98's own rollback: revert the merge.

## 6. Not in this ACT

- the root and template `.rulesync/skills/spec-writing/` (W2-98's own, by its merge);
- any template commit (none is needed, §0);
- `.claude/agents`, `.claude/templates` and `.claude/settings.json` (COPIES-6 and COPIES-8);
- any change to the kernel or the policy (CAP-33: they follow W2-98's CIT-P and the owner's approval).
