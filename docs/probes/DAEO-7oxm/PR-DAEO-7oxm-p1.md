---
type: probe
task: DAEO-7oxm
reviewer_session: 4f88f3fb-bc2b-4660-815a-66438edc346a
implementer_session: 97eb8f47-08cb-4068-9661-e839211c9af8
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 6676fcdb01202becc8b8e628ca53e251e03decfb
decisions_applied: [DEC-1154, DEC-1101, DEC-820, DEC-1052, DEC-1120]
---

# Probe record: W2-178, the narrow check of the base-build revision (path case DEC-1156 (7))

This is a narrow independent check under DEC-1154 of one test-only revision: the CTO's path case DEC-1156 (7) of
2026-11-15, after the nightly's six `WALL.json differs` reds. It is not a review round of the ticket. The ticket's
review passed at `2de763208278` (`PR-DAEO-7oxm.md`). The revision is test designer td-1's commit `fccde9a521f9`
(session `97eb8f47-08cb-4068-9661-e839211c9af8`, independent-test-designer), merged at `6676fcdb0120`. It makes the
base build in `tests/acceptance/W2-178/w2_178_support.py` use the head's `indep-schemas` folder with the base script.

The check ran in two fresh, read-only independent-auditor sessions on Opus at high effort, class C2, launched with
`--owner-named DEC-1154`. Both probed head `6676fcdb0120` and wrote nothing in the tree.
- **au-1** (`d88d2680-1371-4228-8e08-e8d4edd2ccb3`) confirmed points 1 and 3. It could not run point 2's planted reds:
  it called the Write tool, which the read-only launch does not grant, and in quiet hours the guard refused the call
  and queued it (DEC-991).
- **au-2** (`4f88f3fb-bc2b-4660-815a-66438edc346a`) was launched with the same brief plus one paragraph telling it to
  make scratch files through Bash. It ran the planted reds: four plants red, naming only the planted file, and the
  control green.

Verdict: **pass**. Its one finding, R1, is a stale docstring in `conftest.py`. It is out of scope, has consequence
"other", and is a row, not a round. au-1's body comes first for the record, then au-2's, which ends with the verdict block.

## First session (au-1), for the record (point 2 not run)

### Confirmation 1: the diff is that revision only (confirmed)
- `git diff --stat 076cded14 6676fcdb0` lists one file: `tests/acceptance/W2-178/w2_178_support.py`, 11 lines added and 5 removed.
- That diff touches only two places:
  - the module docstring (lines 10–14);
  - `extract_base_script` (lines 109–121). `git archive` now takes `SCRIPT_REL` only. The assert now checks the script only. A new `shutil.copytree(support.SCHEMAS, dst / SCHEMAS_REL)` is followed by an assert that the copy exists and is not empty. The function's docstring was updated.
- Everything else is unchanged: `read_wall`, `differences`, `input_set`, `without_dropped`, `build`, `launch_with`, the cases, `conftest.py` and `README.md`.
- The trailers of `fccde9a52` sit in one final paragraph: `Task: DAEO-7oxm`, `Role: independent-test-designer`, `Implements: DEC-1101, DEC-820, DEC-1052, DEC-1120` (exactly the ticket's `sources:`), `Rewrite-Reason: DEC-1156 (7)`, and `Co-Authored-By`.
- `w2_178_support.py` is listed in the ticket's `allowed_paths`, added by the CTO's path case.

### Confirmation 2: the revision still catches a wall that differs in any other file (by reading; the planted runs were not made)
**What reading shows:**
- The cases' comparison path is byte-for-byte unchanged: `read_wall` (`w2_178_support.py:157-181`) snapshots every entry with its mode and bytes, and replaces only the run id and `settings_sha256`. `differences` (line 184) and each case's `assert diff == {}` (`test_w2_178_unchanged.py:50,60`; the auditor's lines 102 and 111) are also unchanged.
- The revision changes only what the base script finds beside itself, and that is now byte-identical to what the head script reads. W2-149 sets `SCHEMAS = SCRIPT.parent / "indep-schemas"` (`w2_149_support.py:32`), and the script uses `SCHEMAS = dirname(abspath(__file__))/indep-schemas` (`indep_launch.py:87`). The schemas are read by name and hashed (`indep_launch.py:330-332`); none is copied into a wall.
- So a wall file that the base script writes differently (seed.txt, brief.md, CLAUDE.md, settings, selection, any `input/set/` file) still lands in `differences` under its own path.
- `schema_sha256` is still compared raw, so a schema that differs between the two builds still shows as `WALL.json` differing. The nightly itself showed this with the unchanged comparison: DIAG.md line 6 records `{'WALL.json': 'differs'}`, with nothing else in the wall differing.
- The sanity cases (`test_s1_sanity_…[writer-round-2|checker|auditor]`, which build with the base script twice) pass. That shows the comparison resolves every entry after the run id is replaced.

**Not done: the planted runs.** The guard refused my Write of the scratch plugin `$TMPDIR/w2178/plug/w2178_plant.py`, citing quiet hours (DEC-991), and queued it. I did not retry it.

The plugin's design, for the re-run:
- It is a `pytest_collection_modifyitems` hook that wraps `w2_178_support.extract_base_script`. It asserts that the extracted copy lies under `$TMPDIR`.
- `W2178_MUT=<wall path>` (`seed.txt`, `brief.md`, `input/set/q01.yaml`, `.claude/settings.json`) inserts redefinitions of `write_new` and `copy_new` just before `if __name__ == "__main__":` in the base copy. The redefinitions append `b"\n"` to the named wall file.
- `W2178_MUT=schema:indep-counts.schema.json` appends a newline to the base copy's schema only.
- Run each value against `test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it` (both kinds) and `test_s1_the_auditor_s_wall_differs_from_the_base_build_only_by_the_dropped_subtree`, plus a control run with no mutation.
- Expected: red, with the named file in the difference (`WALL.json` for the schema). Control: green.

### Confirmation 3: the cases and the folder pass, and F2 holds (confirmed)
- `tests/acceptance/W2-178/` at the head: **21 passed in 27.17 s**, run through `heavy_slot.sh` with the brief's command plus `PYTHONDONTWRITEBYTECODE=1`.
- 21 cases are collected without the filter, so the exclusion left nothing out. The six cases that failed in the nightly are among the 21 and green:
  - auditor: `…differs_from_the_base_build_only_by_the_dropped_subtree` and `…a_set_with_no_dropped_folder_builds_the_same_auditor_wall_as_before`;
  - unchanged: `…equals_the_base_build_byte_for_byte…[writer-round-2|checker]` and `…without_a_dropped_folder_equals_the_base_build[writer-round-2|checker]`.
- F2: the revision's new source is `support.SCHEMAS`, which is the tree's own tools folder (or a scratch sketch's, under `W2_149_SCRIPT`). No line names the real sets root, and `test_f2_no_line_of_this_folder_names_the_owner_s_sets_root` passes. Every launch still goes through `World.check_planted`.
- F3: the revision adds no path. `test_f3_the_branch_changes_only_the_ticket_s_paths` passes.
- `git status --porcelain` is empty after the runs.

### Findings
None against the revision.

One row, not a finding, covering the check itself: confirmation 2's planted red runs were not made, because the scratch-file Write was refused in quiet hours.
- Ordinary work: yes, because any probe launched in quiet hours hits the same refusal.
- Consequence: other. Nothing fails open: the comparison code is unchanged, and the nightly showed it catching a schema difference.
- Scope: out. It concerns the check, not the change.

### Overall judgement
**pass** on what I checked. No finding is in scope, ordinary work yes, and fails open or loses work. The lead should still have confirmation 2's planted runs made before relying on this record as complete.

(au-1's verdict block, all four lines pass with no findings, is replaced by au-2's below.)

## Second session (au-2): the record

**What was probed:** head `6676fcdb01202becc8b8e628ca53e251e03decfb` of `w2/W2-178`, worktree `/home/usain/gov-os-worktrees/W2-178`, base `076cded14`. The revision is `fccde9a521f9b62e66bfd737e582db85f8e83925` (td-1, independent-test-designer). The scope is that revision only, under DEC-1154 and DEC-1156 (7). The launch script and the ticket's other tests were not re-reviewed.

**How:**
- Read-only reads of the diff, the support, the conftest, the two case files and the ticket.
- The planted runs used a pytest plugin under `$TMPDIR/au2/plug`, loaded with `-p plant_w2178` and `PYTHONPATH`. In `pytest_collection_finish` it wraps `w2_178_support.extract_base_script`. The wrapper first calls the real function, which extracts BASE's script from git and copies in the head's schemas. It then changes one thing in that extracted copy, which lives under pytest's temporary folder inside `$TMPDIR` (the wrapper asserts this). The repository's script was never touched.
- Every run: `HOME` set to an empty folder under `$TMPDIR`, its own `TMPDIR` under `$TMPDIR`, `-p no:cacheprovider`.

### Confirmation 1: the diff is that revision only. Holds.
- `git diff --stat 076cded14 6676fcdb0` lists only `tests/acceptance/W2-178/w2_178_support.py` (11 lines added, 5 removed). There is one commit in the range plus its merge.
- Inside the file, the changes are:
  - the module docstring's paragraph about the base build (lines 10–14);
  - `extract_base_script` (lines 109–121). `git archive` now names `SCRIPT_REL` only, the assert checks only the script, and `shutil.copytree(support.SCHEMAS, dst / SCHEMAS_REL)` is added with a check that the copy is not empty. `shutil` was already imported.
- `read_wall`, `differences`, `input_set`, `without_dropped`, `build`, `launch_with`, the cases, `conftest.py` and the README are unchanged.
- `support.SCHEMAS` is `TREE/governance/project/orchestration/tools/indep-schemas` (W2-149 support, lines 28–32): the tree's own tools folder.
- Trailers, all in one final paragraph:
  - `Task: DAEO-7oxm`
  - `Role: independent-test-designer`
  - `Implements: DEC-1101, DEC-820, DEC-1052, DEC-1120`, which is exactly the ticket's `sources:`
  - `Rewrite-Reason: DEC-1156 (7)`
  - `Co-Authored-By: …`
- Between BASE `03393ee51` and the head, both `indep_launch.py` (159 lines changed) and `indep-counts.schema.json` (40 lines changed) differ. So the base build really runs the old script, and the old schema folder really was the stale input the nightly tripped on.

### Confirmation 2: the revision still catches a wall that differs in any other file. Holds; run for real.
Each run covered four cases:
- `test_w2_178_unchanged.py::test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it[writer-round-2]`
- the same case, `[checker]`
- `test_w2_178_auditor.py::test_s1_the_auditor_s_wall_differs_from_the_base_build_only_by_the_dropped_subtree`
- `test_w2_178_auditor.py::test_s1_a_set_with_no_dropped_folder_builds_the_same_auditor_wall_as_before`

| plant (in the base copy only) | result | difference reported in every failing case |
|---|---|---|
| none (unaltered support, control) | 4 passed | — |
| `claude_md`: CLAUDE.md written with one extra byte | 4 failed | `{'CLAUDE.md': 'differs'}` |
| `input_set`: `input/set/q02.yaml` written with one extra byte | 4 failed | `{'input/set/q02.yaml': 'differs'}` |
| `hook_mode`: `.claude/wall_hook.py` written with mode 0o440 instead of 0o444, same bytes | 4 failed | `{'.claude/wall_hook.py': 'differs'}` |
| `schema`: the base copy's `indep-counts.schema.json` given one trailing newline (head's copy untouched) | 4 failed | `{'WALL.json': 'differs'}` |

Sample output, identical in form across the plants:
```
E   AssertionError: the head's writer wall differs from the base's: {'CLAUDE.md': 'differs'}
E   AssertionError: the head's checker wall differs from the base's: {'CLAUDE.md': 'differs'}
E   AssertionError: the head's auditor wall differs from the base's beyond the dropped subtree: {'CLAUDE.md': 'differs'}
E   AssertionError: the head's auditor wall differs from the base's: {'CLAUDE.md': 'differs'}
4 failed in 7.33s
```

What this shows:
- A one-byte difference in a wall file (CLAUDE.md, which no WALL.json hash covers) is still caught for the writer, the checker and the auditor.
- A one-byte difference in one file of `input/set/` is still caught, including in the auditor's comparison apart from `dropped/`.
- A mode-only difference is still caught.
- A schema that really differs between the base build and the head build is still caught as `WALL.json` differing. The revision removed only the stale copy from git; the comparison itself is intact.

S1's judgement stands:
- writer and checker walls are byte- and mode-identical to the base build;
- the auditor's wall equals the base build apart from `input/set/dropped/`.

### Confirmation 3: the folder passes, and F2 and F3 hold. Holds.
- Command: the brief's command as written, through `heavy_slot.sh`, which ran inside the sandbox with no refusal and no wait. Result: **21 passed in 26.37s**, 0 failed, 0 deselected by the exclusion filter.
- The six nightly reds are all among the passes:
  - auditor `…differs_from_the_base_build_only_by_the_dropped_subtree`
  - auditor `…a_set_with_no_dropped_folder_builds_the_same_auditor_wall_as_before`
  - unchanged `…equals_the_base_build_byte_for_byte…` `[writer-round-2]` and `[checker]`
  - unchanged `…without_a_dropped_folder_equals_the_base_build` `[writer-round-2]` and `[checker]`
- **F2:**
  - The only path the revision adds is `support.SCHEMAS`, the tree's own tools folder.
  - Every launch still goes through `World.check_planted`.
  - Grepping the folder for the real roots finds one line: `test_w2_178_unchanged.py:92`, the needle list of the F2 case itself, which builds the name from two halves. That line is unchanged by the revision.
  - `test_f2_no_line_of_this_folder_names_the_owner_s_sets_root` passes.
- **F3:**
  - The revision touches `tests/acceptance/W2-178/w2_178_support.py`, which is in the ticket's `allowed_paths` (added by the CTO's path case) and under `tests/acceptance/W2-178/**`.
  - `test_f3_the_branch_changes_only_the_ticket_s_paths` passes.
  - `indep-schemas/` is not in `allowed_paths`, so if this ticket's own branch changed a schema, F3 would go red. Using the head's schemas therefore hides nothing this ticket could change.
- **No writes to the worktree:** `git status --porcelain` is empty after all runs. The existing ignored `__pycache__/` files keep their 05:32:56 times, which are earlier than this session's runs.

### Findings
- **R1 (S1, out of scope, row):** `tests/acceptance/W2-178/conftest.py:29`, the `base_script` fixture's docstring, still reads "The launch script at the base commit, next to its schemas (out of git)". Since the revision, the schemas next to it are the head's copy, not schemas out of git. The behaviour is correct; only the description is stale. This would reverse if the conftest docstring were meant to describe the folder's origin only loosely, or were outside the narrow scope of this check.
  - Ordinary work: yes, because a reader of the conftest alone could take the base build to use BASE's schemas.
  - Consequence: other (a stale description; no check fails open and no work is lost).
  - Scope: out (the conftest is outside the revision, and the brief has it unchanged).

Probed and found sound:
- The diff's scope and the commit trailers.
- The S1 comparison still catches differences in CLAUDE.md, `input/set/` content, file modes and real schema differences, for the writer, the checker and the auditor.
- The control stays green.
- The whole folder passes.
- The revision reaches no sets root other than the planted one.

What would reverse the pass:
- a plant in another wall file that the comparison misses (for example, a difference that `read_wall`'s run-id replacement erases);
- a difference in the head's own `indep-schemas` coming from this ticket's branch that F3 does not flag.

Neither appeared.

**Overall judgement: pass.**

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}]}
```
