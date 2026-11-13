# ACT-CLAUDE-COPIES-8: the "until W2-56" line deleted from four generated copies

## 0. The short version

- **What:** one line, `- Run \`gov accept\` for a ticket whose suites need the code index outside the sandbox, until W2-56 [DEC-1052].`, deleted from four generated copies: `.claude/templates/role-lead.md` (line 27), `.claude/templates/role-cto.md` (line 21), `.rulesync/subagents/orchestrator.md` (line 30) and `.claude/agents/orchestrator.md` (line 36). W2-56 is closed (1c02c490f), so `gov brief` refuses every lead brief `UNTIL_CLOSED W2-56` while the line stands. The owner approved the deletion (DEC-1163 (1), 2026-11-13). Every byte comes from the product's own generation, not from an edit (§1). **Nothing live changes until it runs.**
- **Two forms, as the CTO asked.** The owner says one line, for the form the CTO picks:
  - **`ACT-CLAUDE-COPIES-8`** (the default): the four copies only. It is for integrate as it is, with the CTO's source commit b88a76172 standing and ACT-CLAUDE-COPIES-6 landed (by hand, 36d1a151b). **It applies at integrate's head now: rehearsed on 4be656e70.**
  - **`ACT-CLAUDE-COPIES-8-with-sources`**: the four copies and the three sources (`template/governance/kernel/templates/role-lead.md`, `role-cto.md`, `template/.rulesync/subagents/orchestrator.md`). It is for integrate after b88a76172 is reverted. **Read the class finding below before picking it.**
- **The owner's line,** on its own line, one of:

yes ACT-CLAUDE-COPIES-8 e2fc9815

yes ACT-CLAUDE-COPIES-8-with-sources c8396adc

- **Manifest sha256:**
  - `ACT-CLAUDE-COPIES-8`: `e2fc98150aa1d19165d8b0da3e5ec57dc65c69d5de55924ff8f6aefa7f4e0dae`;
  - `ACT-CLAUDE-COPIES-8-with-sources`: `c8396adcdd9c3acb24ac6d236a60c351e294bf682430855b5a4545dc952f2344`.
- **Bundles:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-8/` and `acts/ACT-CLAUDE-COPIES-8-with-sources/`. The builder is `drafts/claude-copies-8/build_copies8.py`. It is adapted from COPIES-6's `build_v2.py`, which is not edited, and its docstring lists the changes. Its full output is `drafts/claude-copies-8/build.out`.
- **Class:**
  - `ACT-CLAUDE-COPIES-8`: **(b)**, by the operator's own `act_class` on the bundle. The rows are `claude-rest` for `.claude/templates/**`, `agents-skills-kernel` for `.claude/agents/**` and `rulesync-other` for `.rulesync/**`. All three are (b) control paths.
  - `ACT-CLAUDE-COPIES-8-with-sources`: **(O)** by the same `act_class` (rows below).
- **Who applies it: the owner's operator agent, on the owner's yes,** as for COPIES-1 to -6. The CTO cannot: a session cannot write `.claude/**` (DEC-315), and `.rulesync/**` is a (b) control path, so it goes by an ACT. The by-hand route (§4) is the owner's, with `Role: owner`.
- **Under:** DEC-1163 (1), DEC-1052, DEC-315, CAP-33. Also DEC-1057 (rehearsed as the operator runs it).
- **When: only after ACT-CLAUDE-COPIES-6**, which changes the same two orchestrator copies; the before-hashes here are COPIES-6's after-hashes. COPIES-6 is now in: the owner landed it by hand at 36d1a151b during this build. The sources' deletion must also be in the tree: b88a76172 for the default form, or this ACT itself for the with-sources form. §2 gives the order. Check 2 holds it: an out-of-order run is refused at G7 or G8 (rehearsed, §3).
- **Review:** the operator's fixed reviewer brief applies (`<bundle>/review.md`). **It is not written yet.** The CTO starts the reviewer before asking for the owner's line. G4 refuses without the reviewer's fenced verdict block.

### Finding 1: COPIES-6's own check 2 is red at b88a76172 (settled by the hand landing)

COPIES-6's check 2 pins `template/.rulesync/subagents/orchestrator.md` at `ef15ea7d…`, its bytes before the deletion. b88a76172 moved that file to `5db8f0cb…`. So on integrate at b88a76172, COPIES-6's check 2 exits 1 (measured), and the operator's G8 would have refused COPIES-6 as approved.
- COPIES-6 was then landed by hand (36d1a151b, `Role: owner`). A hand landing runs no G8, so nothing is pending from this finding for the default form.
- The record should note that COPIES-6's approved check 2 is red on the tree it landed on, for exactly this one file. This is the reason it is red, and the bytes are the owner-approved deletion.

### Finding 2: the with-sources form's class

`template/.rulesync/**` has no row in the operator's class rules. It falls to the catch-all `unknown` row, which is (O) and "not an ACT's business", with `control: false`. (COPIES-6's package measured the same: that is why COPIES-6's eight template sources were the CTO's own commit.) `template/governance/kernel/**` is row `agents-skills-kernel`, which is (b) with `control: true`.
- So **the with-sources form carries an (O) file, and `act_class` gives it (O).** G6 refuses an (O) bundle as "yours".
- **The two kernel templates are (b) control paths**, and that is why the CTO is weighing the revert. The template's orchestrator source is not a control path.
- **A form that fits the rules:** revert only the two kernel templates, keep `template/.rulesync/subagents/orchestrator.md` as the CTO's commit (it is no control path), and carry the four copies and the two kernel templates (six files, class (b)). That form was not asked for, so it is not built. The builder makes it with a one-line change to `VARIANTS`.

## 1. The files

**`ACT-CLAUDE-COPIES-8` (4 files):**

| file | old sha256 | new sha256 |
|---|---|---|
| `.claude/agents/orchestrator.md` | `d46907b92776244721dceca7d8f8b33ec7352bde113068c54a638d3da3d7200c` | `20fd6d04a3cbf08c788790a6202965ec9163c1de56290a376976d33c797e802f` |
| `.claude/templates/role-cto.md` | `013d4d85bc5d55b2d858f6f07f10f949bccdc85e20458c2c45e4c3d6cfd67abd` | `dbcc9d8ccc925acd4f783cb1d359943eb564297cd7685433d98892956979d789` |
| `.claude/templates/role-lead.md` | `4e8e46b097797d13f70c8828f41562b768bfb19f06160dac87ee7e308aa590a9` | `c731503e7f643dc0b4377358dd09876d7dedaf688ec79ffb6e021776bf86e799` |
| `.rulesync/subagents/orchestrator.md` | `ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c` | `5db8f0cbac35e30ebb81757bb8b92001c611a8080ba8dba9402bd6a4b6a222ba` |

**`ACT-CLAUDE-COPIES-8-with-sources` (7 files):**

| file | old sha256 | new sha256 |
|---|---|---|
| `.claude/agents/orchestrator.md` | `d46907b92776244721dceca7d8f8b33ec7352bde113068c54a638d3da3d7200c` | `20fd6d04a3cbf08c788790a6202965ec9163c1de56290a376976d33c797e802f` |
| `.claude/templates/role-cto.md` | `013d4d85bc5d55b2d858f6f07f10f949bccdc85e20458c2c45e4c3d6cfd67abd` | `dbcc9d8ccc925acd4f783cb1d359943eb564297cd7685433d98892956979d789` |
| `.claude/templates/role-lead.md` | `4e8e46b097797d13f70c8828f41562b768bfb19f06160dac87ee7e308aa590a9` | `c731503e7f643dc0b4377358dd09876d7dedaf688ec79ffb6e021776bf86e799` |
| `.rulesync/subagents/orchestrator.md` | `ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c` | `5db8f0cbac35e30ebb81757bb8b92001c611a8080ba8dba9402bd6a4b6a222ba` |
| `template/.rulesync/subagents/orchestrator.md` | `ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c` | `5db8f0cbac35e30ebb81757bb8b92001c611a8080ba8dba9402bd6a4b6a222ba` |
| `template/governance/kernel/templates/role-cto.md` | `013d4d85bc5d55b2d858f6f07f10f949bccdc85e20458c2c45e4c3d6cfd67abd` | `dbcc9d8ccc925acd4f783cb1d359943eb564297cd7685433d98892956979d789` |
| `template/governance/kernel/templates/role-lead.md` | `4e8e46b097797d13f70c8828f41562b768bfb19f06160dac87ee7e308aa590a9` | `c731503e7f643dc0b4377358dd09876d7dedaf688ec79ffb6e021776bf86e799` |

**What changes in each file:** exactly one line is deleted, the line above. Nothing else changes; each file is one line shorter.

**How each copy is made (rehearsed twice, §3):**
- **`.claude/templates/role-lead.md` and `role-cto.md` are byte copies of the kernel templates, not generated text.** The evidence:
  - `src/gov/adapters/portability.py:69-70`: `TEMPLATE_COPIES` names the eight kernel templates copied "byte for byte into .claude/templates/ (written only by an ACT, DEC-315)";
  - `:207-223`: `_template_findings` reports `TEMPLATE_COPY_DIFFERS` when a copy is not the kernel template's bytes;
  - `:226-243`: `write_templates`, run as `python3 -m gov.adapters.portability --write-templates .claude/templates`, writes `path.read_bytes()` of each kernel template into the folder;
  - `src/gov/launch/launcher.py:80`: `TEMPLATES_REL = ".claude/templates"  # the generated copies, written only by an ACT (DEC-315)`.

  The builder ran that `--write-templates` step. Its output equals the kernel bytes `c731503e…` and `dbcc9d8c…`, which are the CTO's committed sources.
- **`.rulesync/subagents/orchestrator.md`** is `gov.adapters.portability.compose(root, "orchestrator")`. `compose()` takes the source's own front matter, then the body of the kernel template `role-lead.md` (`launcher.py:78`: `"orchestrator": "role-lead"`), then the body of `roles/orchestrator.md`. The line enters it through `role-lead.md`, not `role-cto.md`. The template's orchestrator source is the same text (`compose(template/, "orchestrator")`, asserted equal), which is why both are `5db8f0cb…`.
- **`.claude/agents/orchestrator.md`** is rulesync 24.0.0's output from the root `.rulesync/` (portability's GENERATE form).
- `role-cto.md` feeds no source: `ROLE_TEMPLATES` has no role mapped to it, so it reaches only its `.claude/templates/` copy.

**What stays:**
- `.claude/settings.json`, rulesync's only other differing output (the held-out deny, DEC-616), which no copies ACT regenerates;
- the six other `.claude/templates/` copies;
- the eight other agents and root sources (regenerated by the builder; byte-equal, so not changed).

## 2. The order

**The default form (`ACT-CLAUDE-COPIES-8`), b88a76172 standing:**
1. W2-33's merge (f6163461e), the COPIES-6 template patch (d172bc71f) and the sources' deletion (b88a76172). All three are on integrate now.
2. ACT-CLAUDE-COPIES-6: done by hand at 36d1a151b.
3. This ACT. Its G7 and G8 pass at integrate's head 4be656e70 (rehearsed, §3).

**The with-sources form, b88a76172 reverted:**
1. W2-33's merge, the COPIES-6 template patch and COPIES-6 (all in now); then the revert of b88a76172. On integrate's head the revert is clean, and on d172bc71f it gives d172bc71f's tree exactly (measured).
2. This ACT. It writes the three sources and the four copies together. Rehearsed on the head with the revert. **But G6 refuses it as class (O) (Finding 2).**

**How the order is held:**
- `apply.sh check` (G7) holds every before-hash. The two orchestrator copies must be at COPIES-6's after-hashes, so a run before COPIES-6 is refused at G7.
- **Check 2 holds the rest at G8.** It lists 36 files:
  - the nine kernel role files at W2-33's bytes;
  - the two kernel templates after the deletion;
  - the nine template role sources (COPIES-6's patch, with the orchestrator after the deletion);
  - COPIES-6's sixteen other copies at COPIES-6's after-hashes.

  A tree that passes G7 but lacks the template patch, the sources' deletion or COPIES-6 is red after the apply. Both forms carry the same checks. In the with-sources form, check 2 is red before the apply and green after it, because the sources are its own files.
- No check names a live HOME or repository path. The builder asserts this with the pattern `/home/[A-Za-z0-9_.-]+/`, and the operator's own `path_rule` passes (§3).

## 3. The rehearsal (DEC-1057; `rehearsal.log` in each bundle, hashed in its manifest; failures: 0 and 0)

The rehearsal ran on fresh clones under `/tmp/claude-1000/`, outside the repository and outside `~/gov-os-runs`. HOME was planted at an empty folder for every apply step.

1. **The generation, twice:**
   - **(A)** from W2-33's merge commit: `w2/W2-33` merged (already up to date); the COPIES-6 template patch applied by its own `apply.sh`, which gives d172bc71f's `template/.rulesync/` exactly; the line deleted literally from the three sources (one occurrence each), which gives b88a76172's bytes; COPIES-6 applied.
   - **(B)** from integrate at b88a76172, with COPIES-6 applied.

   In each: `compose()` for every root source, rulesync for `.claude/agents/`, `--write-templates` for `.claude/templates/`. **Both changed exactly the four files, to the four stated after-hashes, byte for byte, and A equals B.** Portability then exits 0 with no findings.
2. **Each form on its own tree:** `apply.sh check` exit 0; check 1 red before the apply; check 2 green before the apply (default) or red (with-sources); `apply`; both checks green; the changed set equals the touched list, each file at its new sha256 and equal to the generation's bytes; portability exit 0 with no findings; `undo` byte for byte, with the tree clean; `check` again, and `apply` again, giving the same bytes. Portability before the apply reads: exit 1; 3 findings: SOURCE_DIFFERS 1, TEMPLATE_COPY_DIFFERS 2 (default tree); exit 0; 0 findings: none (with-sources tree, where the copies and the old sources still agree).
3. **Integrate's head when built (4be656e70, COPIES-6 by hand):**
   - the default form: `apply.sh check`, check 2 green, `apply`, both checks green, the changed set equal to the four files, portability exit 0, `undo` leaving the tree clean;
   - the with-sources form: `apply.sh check` exits 3 while b88a76172 stands; with b88a76172 reverted, check, apply, both checks and undo all pass.
4. **Out of order:** each tree run as G7/G8 runs it. Every one is refused:
   Default form:
   - W2-33's merge alone (no template patch, no sources' commit, no COPIES-6): apply.sh check exit 3 (G7 refuses)
   - W2-33's merge and COPIES-6 (no template patch, no sources' commit): apply.sh check exit 0; after the apply check 1 exit 0, check 2 exit 1 (G8 refuses)
   - the template patch and COPIES-6, before the sources' commit: apply.sh check exit 0; after the apply check 1 exit 0, check 2 exit 1 (G8 refuses)
   - integrate at the sources' commit, before COPIES-6: apply.sh check exit 3 (G7 refuses)
   With-sources form:
   - W2-33's merge alone: apply.sh check exit 3 (G7 refuses)
   - W2-33's merge and COPIES-6, before the template patch: apply.sh check exit 0; after the apply check 1 exit 0, check 2 exit 1 (G8 refuses)
   - the template patch, before COPIES-6: apply.sh check exit 3 (G7 refuses)
   - integrate at the sources' commit (not reverted), before COPIES-6: apply.sh check exit 3 (G7 refuses)
   - integrate at the sources' commit (not reverted), after COPIES-6: apply.sh check exit 3 (G7 refuses)
5. **The gated runs,** one folder per pytest run through `tools/heavy_slot.sh`, with `-p no:cacheprovider` and TMPDIR outside the repository. Each result was read from pytest's own summary line, and failures by test id from `-rfE`. The landed tree is the same for both forms. These ran in the first build, and the final build re-read their output files from the same scratch folder: the same commits, the same bytes. The rest of the rehearsal was rerun, after the expected reds were named. **Three cases stay red on the landed tree, and they are named and expected.** They are W2-128's row 8 for `role-lead` and `role-cto` (`tests/acceptance/W2-128/test_w2_128_rows.py:72-75`), which pins the very line the owner deleted from the kernel templates, and W2-152's S10 (`test_w2_152_facts.py:61-75`), which runs `gov accept W2-128`. They are red from the sources' deletion (b88a76172), not from the copies; in the with-sources form, that deletion is the ACT's own. **Revising row 8 is the CTO's decided-behaviour test revision (DEC-1156 (7)), and it is not in this ACT.**

   Default form (window: integrate, then COPIES-6):
       window tests/acceptance/W2-153: exit 1; 64 passed, 2 failed
       window tests/unit/adapters: exit 1; 100 passed, 2 failed
       window tests/unit/launch: exit 0; 220 passed, 0 failed
       window tests/unit/brief: exit 0; 25 passed, 0 failed
       window tests/acceptance/W2-152: exit 1; 66 passed, 1 failed
       window tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
       window tests/acceptance/W2-128: exit 1; 119 passed, 2 failed
       window tests/acceptance/W1-35: exit 0; 124 passed, 0 failed
       ok   landed tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
       ok   landed tests/unit/adapters: exit 0; 102 passed, 0 failed
       ok   landed tests/unit/launch: exit 0; 220 passed, 0 failed
       ok   landed tests/unit/brief: exit 0; 25 passed, 0 failed
       ok   landed tests/acceptance/W2-152: exit 1; 66 passed, 1 failed
       ok   landed tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
       ok   landed tests/acceptance/W2-128: exit 1; 119 passed, 2 failed
       ok   landed tests/acceptance/W1-35: exit 0; 124 passed, 0 failed
       red in the window: tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto]
       red in the window: tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead]
       red in the window: tests/acceptance/W2-152/test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes
       red in the window: tests/acceptance/W2-153/test_w2_153_sources.py::test_s3_each_role_source_is_its_front_matter_its_skills_its_template_s_body_and_its_role_file_s_body[orchestrator-.rulesync]
       red in the window: tests/acceptance/W2-153/test_w2_153_sources.py::test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository
       red in the window: tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition[]
       red in the window: tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition
       red on the landed tree: tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto] (expected: the same row 8 for role-cto.md)
       red on the landed tree: tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead] (expected: row 8 pins the "until W2-56" line in the kernel template role-lead.md (:72-75); the owner deleted it (DEC-1163 (1)); red from the sources' deletion (b88a76172, or the with-sources form's own), not from the copies; the case's revision is the CTO's)
       red on the landed tree: tests/acceptance/W2-152/test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes (expected: runs gov accept W2-128 (:61-75), so red while row 8 is)
       red in the window: 7; made green by the ACT: 4; red after: 3; new red brought by the ACT: []

   With-sources form (window: the revert, then COPIES-6):
       window tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
       window tests/unit/adapters: exit 0; 102 passed, 0 failed
       window tests/unit/launch: exit 0; 220 passed, 0 failed
       window tests/unit/brief: exit 0; 25 passed, 0 failed
       window tests/acceptance/W2-152: exit 0; 67 passed, 0 failed
       window tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
       window tests/acceptance/W2-128: exit 0; 121 passed, 0 failed
       window tests/acceptance/W1-35: exit 0; 124 passed, 0 failed
       ok   landed tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
       ok   landed tests/unit/adapters: exit 0; 102 passed, 0 failed
       ok   landed tests/unit/launch: exit 0; 220 passed, 0 failed
       ok   landed tests/unit/brief: exit 0; 25 passed, 0 failed
       ok   landed tests/acceptance/W2-152: exit 1; 66 passed, 1 failed
       ok   landed tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
       ok   landed tests/acceptance/W2-128: exit 1; 119 passed, 2 failed
       ok   landed tests/acceptance/W1-35: exit 0; 124 passed, 0 failed
       red on the landed tree: tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto] (expected: the same row 8 for role-cto.md)
       red on the landed tree: tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead] (expected: row 8 pins the "until W2-56" line in the kernel template role-lead.md (:72-75); the owner deleted it (DEC-1163 (1)); red from the sources' deletion (b88a76172, or the with-sources form's own), not from the copies; the case's revision is the CTO's)
       red on the landed tree: tests/acceptance/W2-152/test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes (expected: runs gov accept W2-128 (:61-75), so red while row 8 is)
       red in the window: 0; made green by the ACT: 0; red after: 3; new red brought by the ACT: ['tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto]', 'tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead]', 'tests/acceptance/W2-152/test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes']
6. **§4 literally:** stage the paths; commit with the trailers; portability exit 0; `undo`, stage and commit; an empty diff over the paths against the start.
7. The live main tree's files were not written by the rehearsal, and nothing was written to the planted HOME. The first build saw COPIES-6's hand commit move two of them. The check now allows a move only when it is a live commit.

**The operator's own read-only gates on each bundle** (`~/gov-os-operator/install`: `check_act`, `validate_manifest`, `path_rule` with the install's settings, the manifest's file hashes, `act_class` with the install's `class-rules.yaml`):
- `ACT-CLAUDE-COPIES-8`: check_act pass; validate_manifest pass; path_rule pass; hash mismatches [], unnamed on disk []; act_class **(b)**, hits []; rows: `.claude/agents/orchestrator.md` agents-skills-kernel (b); `.claude/templates/role-cto.md` claude-rest (b); `.claude/templates/role-lead.md` claude-rest (b); `.rulesync/subagents/orchestrator.md` rulesync-other (b).
- `ACT-CLAUDE-COPIES-8-with-sources`: check_act pass; validate_manifest pass; path_rule pass; hash mismatches [], unnamed on disk []; act_class **(O)**, hits []; rows: `.claude/agents/orchestrator.md` agents-skills-kernel (b); `.claude/templates/role-cto.md` claude-rest (b); `.claude/templates/role-lead.md` claude-rest (b); `.rulesync/subagents/orchestrator.md` rulesync-other (b); `template/.rulesync/subagents/orchestrator.md` unknown (O); `template/governance/kernel/templates/role-cto.md` agents-skills-kernel (b); `template/governance/kernel/templates/role-lead.md` agents-skills-kernel (b).

**Where the rehearsal differs from the real run:**
- The real run applies in the main tree, at a later head.
- G7 and `apply.sh check` compare the before-hashes with the live files again.
- If the kernel role files, the template sources or COPIES-6's copies move first, check 2 goes red and the bundle must be rebuilt: `python3 -I build_copies8.py <scratch dir>`.

## 4. The operator's steps

**By the operator agent:** after the owner's yes (§0) and the steps of §2 that come before it, the CTO writes the request line in `~/gov-os-operator/queue/` under the chosen form's id. The agent then runs the bundle through its gates.

**Or by hand, by the owner,** in the main tree (`<form>` is `ACT-CLAUDE-COPIES-8` or `ACT-CLAUDE-COPIES-8-with-sources`):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
G=.gov-runtime/scratch/orchestrator/acts/<form>
sha256sum $G/manifest.json      # expect e2fc98150aa1d19165d8b0da3e5ec57dc65c69d5de55924ff8f6aefa7f4e0dae (default) or c8396adcdd9c3acb24ac6d236a60c351e294bf682430855b5a4545dc952f2344 (with-sources)
bash $G/apply.sh check && bash $G/apply.sh apply
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 4 (default) or 7 (with-sources)
git commit -m "<form>: the \"until W2-56\" line deleted from the generated copies (W2-56 closed)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1163, DEC-1052" --trailer "Role: owner"
```

**What the steps print:**
- `apply.sh check` prints nothing and exits 0. If a file has moved, it prints `moved: <path>` and exits 3.
- After the apply, each manifest check prints `<path>: OK` (4 lines, then 36) and exits 0.
- After the commit, `python3 -m gov.adapters.portability` exits 0 with no findings.

## 5. The undo

1. `bash $G/apply.sh undo`. It restores every file byte for byte (rehearsed: the tree is clean).
2. `git add -A $F` and commit with `--trailer "Role: owner"`. The operator's form is `undo <form> <sha8>`.
3. After the default form's undo, the copies again carry the line while the kernel no longer does. Portability reads `TEMPLATE_COPY_DIFFERS` 2 and `SOURCE_DIFFERS` 1, the window's own reading.

## 6. Not in this ACT

- the CTO's source commit b88a76172 or its revert (the CTO's);
- COPIES-6 (landed by hand, 36d1a151b);
- the revision of W2-128's row 8 case and, through it, W2-152's S10 (the CTO's);
- the six other `.claude/templates/` copies and `.claude/settings.json`;
- any change to the kernel or the policy beyond the three sources the owner approved (DEC-1163 (1)).
