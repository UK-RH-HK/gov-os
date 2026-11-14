- **sandbox_check:** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-g87r` failed with `OSError: [Errno 30] Read-only file system`, as it should. (b) `git hash-object -w --stdin` worked (`1ae28402a109c3397a44b19239a00adfa9472eb0`) and `git update-index --refresh` worked. The check passed.
- **ps_check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- **task:** DAEO-g87r (W2-94). Narrow independent check (DEC-1154, DEC-1156 (7)) of the W2-149 counts-schema pin's one-map revision at `900035fdd51c1e469038feb48510483cd095a1e0`.
- **status:** done. Verdict: pass.
- **work_completed:**
  - Confirmed HEAD is `900035fdd51c…`.
  - Read the branch's own diff since the merge, the test file's diff since `f192e50da`, and the commit's trailers against the ticket's `sources:` and `allowed_paths`.
  - Ran the revised case against 10 in-memory schema mutations plus two green controls.
  - Ran the brief's suite command, then the same command with both opt-in suites.
- **files_changed:** none. `git status --porcelain` is empty at the end.
- **evidence:** listed in the probe record below.
- **tests:**
  - Brief's command, under the heavy slot: **311 passed, 35 skipped, 114 deselected** (189 s).
  - Same command with `GOV_TESTS_OPTIN=lifted,breadth`: **424 passed, 35 skipped, 1 deselected** (225 s).
  - What the exclusion left out: the `-k` filter dropped one case, `tests/acceptance/W2-149/test_w2_149_seed_content.py::test_s6_two_real_builds_draw_different_63_bit_seeds`, which the CTO runs outside the sandbox. The `local_only` marker dropped none.
  - The other 113 deselected in the first run were the opt-in rows from `tests/conftest.py` (DEC-1061): 23 in the W2-149 unit file, 61 in the W2-173 unit file and 29 in the fix-flow unit file. All of them passed in the second run.
  - The heavy slot waited for a free slot, could not write its wait log or remove its `/tmp` priority files (both read-only in this sandbox), and then ran.
- **discoveries:** the brief's suite command leaves out 113 rows unless the run opts in (`tests/conftest.py`). Here they pass either way.
- **risks:** none from this change.
- **lessons:** for the W2-149, W2-173 and fix-flow suites, an "unchanged suites pass" check needs `GOV_TESTS_OPTIN=lifted,breadth` to cover every row.
- **proposed_decisions:** none.
- **unresolved:**
  - The Write tool's permission for `$TMPDIR/s13b/mutants.py` was not granted (refused once). I didn't write that file another way. I ran the mutations in memory in a single `python3 -c` instead, which writes no file.
  - The `-k "real"` case above was not run here; the CTO runs it outside the sandbox.
- **recommended_next_action:** the lead commits the body below as `docs/probes/DAEO-g87r/PR-DAEO-g87r-s13b.md`. Per DEC-1154, the ticket can land on this check.

---

# Narrow independent check: the W2-149 counts-schema pin's one-map revision (W2-94, DAEO-g87r, S13b)

task: DAEO-g87r
decisions: DEC-1154, DEC-1156, DEC-1180, DEC-1010, DEC-801, DEC-808, DEC-820, DEC-1061

## What was probed
- **Commit:** head `900035fdd51c1e469038feb48510483cd095a1e0` of `w2/W2-94-fix`, in worktree `/home/usain/gov-os-worktrees/W2-94-fix`. The base is `f192e50da`; the `w2/integrate` merge `820f5d3ab` is not under review.
- **Scope:** only the revision decided by the path case P-W2-94-S13-1 (a) (DEC-1156 (7), ticket paragraph "Path case 2026-11-14 18:05"). S13 (passed at `ff6ba10be89a`) and the fix flow (reviewed at `fac8d2026`) were not re-reviewed.

## How
- **Diffs read:** `git diff 820f5d3ab 900035fdd` and `git diff f192e50da 900035fdd -- tests/unit/orchestration/test_w2_149_indep_launch.py`, plus `git log -1 --format=%B` for the trailers.
- **Ticket read:** `sources:`, `allowed_paths`, S12, S13 and the path case paragraph.
- **Mutation runs:** the test module was loaded and its `schema()` helper monkeypatched to return a mutated copy of the real `indep-counts.schema.json`. The mutations were made in memory, with no file written. Then `test_counts_schema_closes_every_object_and_string` was called.
- **Suites:** the brief's command from the worktree, run once as given and once with both opt-in suites.

## Confirmation 1: the diff is that one map only — confirmed
- **Since the merge:** `git diff --stat 820f5d3ab 900035fdd` shows one file changed, 2 insertions and 1 deletion: `tests/unit/orchestration/test_w2_149_indep_launch.py`.
- **Since the base:** for that file, `git diff f192e50da 900035fdd` shows a single hunk at line 1093. The merge did not touch this file.
  ```
  -                id(whole["properties"]["delivered"]): {"files_sha256"}}
  +                id(whole["properties"]["delivered"]): {"files_sha256"},
  +                id(whole): {"fix"}}
  ```
- **The added entry:** `id(whole): {"fix"}` is the root entry in the file's own form; the other entries also key by `id(<node>)`. The only other change is the comma and the closing brace moving down one line. No other line, comment, case, import or file changed.
- **Allowed paths:** the file is in the ticket's `allowed_paths` ("the one pin S13 meets, its optional map gains fix (P-W2-94-S13-1 (a)…)").
- **Trailers:** one final paragraph holding `Task: DAEO-g87r`, `Role: engineer`, `Implements: DEC-1180` and `Co-Authored-By: …`. DEC-1180 is in the ticket's `sources:`.

## Confirmation 2: the case still refuses — confirmed
The case was run against each mutation of the real schema (`tests/unit/orchestration/test_w2_149_indep_launch.py:1088-1117`). "Fails at" is the assertion that turned it red.

| # | change to the schema | expected | got | fails at |
|---|---|---|---|---|
| m0 | none (real `schema()`, not patched) | green | green | – |
| m1 | none (deep copy, patched in) | green | green | – |
| m2 | optional root property `extra` | red | red | `required == want` |
| m3 | `fix.required` drops `action` | red | red | `required == want` |
| m4 | `fix.required` drops `id` | red | red | `required == want` |
| m5 | `fix.required` drops `code` | red | red | `required == want` |
| m6 | `fix` loses `additionalProperties` | red | red | `additionalProperties is False` |
| m7 | `fix.additionalProperties: true` | red | red | `additionalProperties is False` |
| m8 | `fix` gains an unrequired property `note` | red | red | `required == want` |
| m9 | `fix` made required at the root | red | red | `required == want` |
| m10 | `delivered` gains an unrequired property `more` | red | red | `required == want` |
| m11 | `fix.id` pattern loses its leading `^` | red | red | string-anchor assertion |

What the table shows:
- The new entry exempts exactly one key (`fix`) at exactly one node (the root).
- Any other unrequired root key still fails.
- `fix`'s own object is still held to `additionalProperties: false` and to `required == {id, code, action}`, because the map has no entry for the `fix` node.
- Making `fix` required at the root also fails, so the pin now fixes `fix` as optional, which matches S13.

## Confirmation 3: the suites pass — confirmed
- **Command:** the brief's command, under the heavy slot, from the worktree, with `HOME` set to an empty folder under `$TMPDIR`. It covers S13's file, `tests/acceptance/W2-149/`, and the W2-149, W2-173, W2-178 and fix-flow unit suites.
- **Run as given:** 311 passed, 35 skipped, 114 deselected. The revised case (`test_w2_149_indep_launch.py::test_counts_schema_closes_every_object_and_string`) was in the selection and passed.
- **Run with `GOV_TESTS_OPTIN=lifted,breadth`:** 424 passed, 35 skipped, 1 deselected. This adds the 113 opt-in rows (W2-149 unit 23, W2-173 unit 61, fix-flow unit 29), so S12's "pass unchanged except this one entry" is checked across every row.
- **What remains deselected:** one case, `tests/acceptance/W2-149/test_w2_149_seed_content.py::test_s6_two_real_builds_draw_different_63_bit_seeds`, dropped by the `-k "not real"` exclusion. The CTO runs it outside the sandbox.

## Findings
**None.** The probe found nothing that blocks and nothing to record as a row.

## Probed and found sound
- The revision is exactly the decided entry.
- The pin still closes the root against any key other than `fix`.
- The pin still closes `fix` itself: no unrequired key inside it, `additionalProperties: false`, and `id`, `code` and `action` required.
- The pin still closes the rest of the schema (m10, m11).
- The commit stays within the ticket's paths and sources.
- The S12 and S13 suites pass at the head, opt-in rows included.

S1 to S11 and F1 to F6: this change touches no code or test of theirs, and nothing in it bears on them.

## Judgement
**pass**

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "S11", "verdict": "pass", "findings": []}, {"kpi": "S12", "verdict": "pass", "findings": []}, {"kpi": "S13", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": []}, {"kpi": "F6", "verdict": "pass", "findings": []}]}
```