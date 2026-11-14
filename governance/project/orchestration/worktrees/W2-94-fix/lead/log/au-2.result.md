task: W2-94 (DAEO-g87r) S13: a narrow independent check of the counts schema's `fix` object and the `--help` epilog fix, at head `ff6ba10be89a` (DEC-1156 (7)).

sandbox_check: (a) `open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-g87r','w')` failed (`OSError: [Errno 30] Read-only file system`), as required. (b) `git hash-object -w --stdin` worked (`1ae28402a109…`) and `git update-index --refresh` worked. Passed.

ps_check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing. No model, embedder or reranker was started. The suites ran on planted stand-ins with an empty `HOME` under `$TMPDIR`.

status: done. Verdict **pass**. One open item: the W2-149 unit case `test_counts_schema_closes_every_object_and_string` stays red until the CTO revises it (F1, question 5).

work_completed:
- Confirmed the head is `ff6ba10be89a`.
- Read the ticket's S6–S13 and its last paragraphs, and the full `git diff 5285ef173 ff6ba10be89a`.
- Read the parts of the launcher this change touches: `_check`/`schema_ok`, `finish`, `counts_only`, the fix-flow argument checks, `action` set at the result, and `parse_args`. Also read check_gold.py's failure codes, the W2-149 `--help` and schema unit cases, the W2-149 S5 acceptance case and the earlier review's P4.
- Ran the brief's scoped suite through the heavy slot.
- Made four altered copies under `$TMPDIR/breaks/` (head launcher with the base schema; `action` without `null`; `fix` under `patternProperties`; base launcher with the head schema) and ran the S13 file against the first three with `W2_94_FIX_SCRIPT`.
- Replayed the W2-149 unit case's walk, as is and with the proposed one-line revision.

files_changed: none in any tree; `git status --porcelain` is empty at the end. Scratch only, under `$TMPDIR`. The Write tool was not permitted to write in `$TMPDIR` for this role, so I passed scripts to python on stdin and made the scratch copies with sandboxed Bash, which the brief allows. I did not retry the Write tool.

evidence:
- **Scoped suite at head** (the brief's command, through `heavy_slot.sh`; it waited for a slot, and its write to the wait log was refused as read-only, which did no harm): `1 failed, 952 passed, 37 skipped, 114 deselected in 293.09s`. The only failure is `tests/unit/orchestration/test_w2_149_indep_launch.py::test_counts_schema_closes_every_object_and_string`, with "Extra items in the right set: 'fix'". This is identical to the engineer's run.
- **S13 file against the base schema:** `36 failed, 3 passed`. Each red fails on "the counts schema refuses the fix key" (lines 51, 120 or 192, after its control passed). The 3 green are the as-before guards. This matches the README's claim.
- **S13 file with `action` lacking `null`:** `11 failed, 28 passed`. The red ones are the dry run, the run refused at 20, the stopped run, and the eight code cases.
- **S13 file with `fix` under `patternProperties`:** `39 failed`, including the three guards for counts without `fix` (line 235). The launcher's `_check` refuses any keyword it does not know (line 373), so every counts object of every flow fails.
- **Schemas compared directly:** the head schema minus `properties.fix` equals the base schema, so nothing else changed. The schema's `code` list equals the launcher's `FIX_CODES` (`True`). Those are check_gold.py's eight per-question codes (check_gold.py:408–452).
- **`--help`, base against head:** the one difference is the removed fix-flow line (`40d39`). Head's `--help` names only `--audit --brief --brief-sha256 --commit --counts-only --dry --help --kind --round --run --seed --set --sets-root -h`. The docstring keeps the fix-flow usage line (indep_launch.py:17).
- **The unit case's walk replayed:** at head as is, it reports `[('req', ['fix'])]`. With `optional[id(whole)] = {"fix"}` it reports `[]`. With the `patternProperties` copy it reports `[]`: the case would pass while the launcher breaks.

tests: the scoped suite above, and three runs of the S13 file against altered copies. Left out by the exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"`: 114 deselected, the real-model and timing cases. The CTO runs those outside the sandbox.

discoveries:
- The `patternProperties` workaround is not schema-equivalent for this launcher: its own checker refuses the keyword, so the workaround would break every flow.
- The schema's `pattern` checks use `re.search` with `$`, so `"q02\n"` passes the `fix.id` pattern. The launcher's own check uses `fullmatch`, so such an id never gets into counts. Recorded as row R2.

risks: until the W2-149 unit case is revised, the scoped launcher suite has one red, and any landing pre-check that runs it will stop on it.

lessons:
- An altered copy that removes a keyword the local checker doesn't support is a cheap test of whether a "schema-equivalent" restructure really is equivalent.
- An epilog built from the docstring inherits every documented line, so a new documented line also needs checking against `--help`.

proposed_decisions:
- Question 5: revise the W2-149 unit case now, by the CTO's path case, under DEC-1180 (4) and DEC-105's "apply now". The revision is one line: `optional` gains `id(whole): {"fix"}`.
- Record the lead's reading of `action: null` against S13's text: a ticket note, or the KPI's words "`corrected` or `replaced`, or `null` until the result has passed its checks".

unresolved: F1, the W2-149 unit case. It is outside W2-94's allowed paths and waits on the CTO's path case.

recommended_next_action: the lead commits this record. The CTO makes the one-line W2-149 unit-case revision through the path case and re-runs the scoped suite (expected: 953 passed). Then the ticket proceeds to q02's run.

---

## The probe record: W2-94 S13, a narrow check of the counts schema's `fix` object and the `--help` epilog fix

task: DAEO-g87r (W2-94)
decisions: DEC-1180 (4), DEC-1180 (2), DEC-1156 (7), DEC-136, DEC-820, DEC-801, DEC-802, DEC-808, DEC-1010, DEC-105

**What I checked:** head `ff6ba10be89a` of `w2/W2-94-fix`, against base `5285ef173`. This covers:
- the counts schema change (`46eb8bf11`);
- the `--help` epilog fix (`ff6ba10be`);
- the S13 cases and the S11/F6 revision (`0af5f2e1f`, merged at `382924bd3`).

The fix flow itself was reviewed at `fac8d2026` and I did not re-review it.

**How:**
- Read the diff and the code the schema meets: `_check`/`schema_ok` (indep_launch.py:345–426), `finish` (470–492), `counts_only` (2658–2672), the fix arguments (583–586) and `action` set at the result (2177–2181).
- Ran the scoped suite once at head.
- Ran the S13 file against three altered copies under `$TMPDIR`.
- Compared `--help` output between base and head.
- Replayed the W2-149 unit case's walk on the head schema, as is and revised, and on the `patternProperties` form.

### 1. The schema against S13: sound

- `fix` (indep-counts.schema.json:1003–1042) is an object with `additionalProperties: false` and `required: [id, code, action]`, holding those three properties and nothing else.
- `id` has the pattern `^q[0-9]{2}$`.
- `code` lists exactly the launcher's `FIX_CODES`, which are check_gold.py's eight per-question codes (checked equal in the same order).
- `action` has type `["string","null"]` and the values `corrected`, `replaced` or `null`.
- `fix` is not in the root's `required`. The root keeps `additionalProperties: false`.
- The head schema minus `fix` is identical to the base schema, so every counts object without `fix` is checked exactly as before. The three as-before guards pass at head and on the base, and the W2-149 counts cases pass.
- The checker supports every keyword used, including `type` as a list and `enum` with `null`.

### 2. The lead's reading of `action: null`: correct

The fix flow already landed and was reviewed under S9. It writes `fix` with `action: null` at the argument stage (indep_launch.py:586) and sets the word only after the result passes its checks (2181). So these runs all reach `finish()` with `action: null`:
- dry runs;
- refusals at staging (10) or at the result (20);
- stopped runs (21).

S13 says without qualification that "a fix run's counts validate, so `finish()` no longer logs 'counts schema failed' and `--counts-only` of a fix run no longer refuses with 17". S9's own landed cases also assert `action` null on a refused result (`test_s9_a_result_of_a_wrong_form_is_20_nothing_delivered_and_the_action_null`).

The altered copy shows what the KPI's literal words alone would do. Without `null`, 11 S13 cases go red. Every non-delivered fix run's counts would fail the schema: `finish()` would log "counts schema failed" again and `--counts-only` would refuse 17 on those runs. That is the P4 defect S13 exists to remove, in a narrower form.

The other route, dropping `fix` or `action` while it is null, would change S9's landed behaviour and its reviewed cases, which is outside this change. So "`corrected` or `replaced`" reads as the words a delivered result names, and `null` is the value before that. The README and the schema's `description` say so. One gap: S13's text does not, so I record R1.

### 3. The cases: sound

- **Coverage.** The S13 file (39 cases) checks every part of the KPI line:
  - validation of delivered (`corrected`, `replaced`), dry, refused-20 and stopped-21 runs, both stdout and `counts.json`;
  - each code × `q00`/`q02`/`q99` × each action;
  - 21 refused forms: an extra key (twice), each key missing, wrong actions, ids, codes and `fix` shapes;
  - the log has no "counts schema" line;
  - `--counts-only` exits 0 and prints the `fix` object;
  - as before, for a writer round 2 without `--fix` and for the W2-149 checker and auditor dry runs.
- **Why each case is red on the base.** Each valid-form case first checks that the counts validate without `fix`, and each refusal case first checks that the delivered counts validate. So all 36 fail for the one stated reason, which I reproduced: 36 failed, 3 green guards.
- **The S11/F6 revision is exactly as wide as S13 needs.** Only the exact path `indep-counts.schema.json` is exempt from the tracked diff. Untracked files under all three folders are still refused, and walls, briefs and the other schemas stay fully guarded. It would also let that one file be deleted. Every launch would then log "counts schema unreadable", and `--counts-only` would refuse 17. I did not run that deletion. Recorded as R3.

### 4. The epilog fix: sound

- `parse_args` (indep_launch.py:517–523) drops from the epilog any documented line that has `--fix` as a word. `--fix` and `--reason` were already `help=argparse.SUPPRESS` (539–540).
- `--help` at head names only the pinned options. The one line removed from base is the fix-flow line. The docstring keeps it (line 17), as S11 requires, and the S11 docstring case passes.
- `tests/acceptance/W2-149/test_w2_149_seed_content.py::test_s5_the_argument_parser_offers_no_path_or_path_list_option` and the unit case `test_help_offers_exactly_the_options_and_no_path_list` both pass.
- The change only affects help text. No flow without `--fix` is touched, and the W2-149, W2-173 and W2-178 launcher unit suites pass apart from F1 (S12).
- The fix flow's review and the lead's earlier scoped run missed this red. Recorded as R4.

### Findings

**F1 (S13, a test conflict that needs a revision): `test_counts_schema_closes_every_object_and_string` (tests/unit/orchestration/test_w2_149_indep_launch.py:1088–1116) is red at head.**
- Its walk requires every root property to be in `required`, apart from a hard-coded `optional` map (1095–1096) that has no root entry. S13 explicitly requires an optional `fix` at the root, so S13 conflicts with this pin.
- S13's own Verify ("the W2-149 counts cases pass unchanged") therefore cannot hold for this one case without a revision.
- Ordinary work: yes, because every scoped run of the launcher suites, and any landing pre-check that includes it, hits this red.
- Consequence: other. It fails closed: a red test, nothing opened and no work lost.
- Scope: in (S13's Verify).
- Reversed by: a schema form that meets S13 (optional `fix`, closed) and passes this case unchanged without defeating the launcher's checker. None exists among the forms I checked (see question 5).

**R1 (S13, wording only): the schema allows `action: null`, but S13's text says "`corrected` or `replaced`".**
- The reading is right (question 2), but it is recorded only in the README, the schema's `description` and the lead's interface text, not in the KPI or a ticket note.
- Ordinary work: yes, because a later reader of S13 alone could "tighten" the schema back. The S13 cases would catch that (11 red).
- Consequence: other (documentation).
- Scope: in.
- Reversed by: a ticket note or KPI wording that already names `null`.

**R2 (S13): `fix.id`'s pattern `^q[0-9]{2}$` is matched with `re.search`, so `"q02\n"` validates.**
- Every other pattern in the schema has the same `$` form. The launcher writes the id only after `full(FIX_RX, …)` (`fullmatch`), so it never produces such an id.
- Ordinary work: no, because only a hand-edited `counts.json` could carry it.
- Consequence: other.
- Scope: out. A Wave 3 row, for the whole schema's anchoring convention.
- Reversed by: a launcher path that writes an id without `fullmatch`.

**R3 (S11/F6): the revised diff case would also pass if `indep-counts.schema.json` were deleted on the branch.**
- Ordinary work: no, because no honest edit for S13 deletes the schema. If it happened, every launch would log "counts schema unreadable" and `--counts-only` would refuse 17, so the error would show at once. I did not run this deletion.
- Consequence: other.
- Scope: out. A row.
- Reversed by: a deletion of the schema that leaves the other suites green.

**R4 (S12, process): the `--help` red (W2-149 S5) was missed by both the fix flow's review and the lead's earlier scoped run.**
- It came in at `0b43625da` because the epilog copies every docstring line that starts with `python3 `.
- Ordinary work: yes, because adding a documented line is ordinary.
- Consequence: other (a red test, fixed here).
- Scope: out. A lesson row: a launcher change's scoped run should include `tests/acceptance/W2-149/`, as the brief's command now does.
- Reversed by: a record showing the W2-149 acceptance folder was in that earlier scoped run.

### Question 5: the open path case

- **(a) Yes, S13 makes this pin a conflict that needs a test revision.** The case pins "every root property is required". S13, decided by the CTO under DEC-1180 (4), requires an optional root key. No schema form meets both without dodging the case (see c). Making `fix` required would break "optional" and every other flow's counts. The case's real purpose, every object and string closed, still holds for `fix`: when the walk reaches it, `fix` is closed, its required list equals its properties, `id` is anchored, and `code` and `action` are enums. W2-149 is closed and the file is outside W2-94's paths, so this falls under DEC-105. Recommendation: **apply now** (DEC-1180 (4): a defect spotted is fixed in the same flow), through the CTO's path case.
- **(b) Yes, the one-line revision is the narrowest correct one.** `optional` gaining `id(whole): {"fix"}` exempts exactly one root key from `required` and changes nothing else. The `additionalProperties: false` check, the string rules and the walk into `fix` all still apply. Replayed at head, the walk goes from `[('req', ['fix'])]` to `[]`. A future optional root key would still fail the case unless named, which keeps its purpose.
- **(c) The `patternProperties` form is not acceptable.** It defeats the case's purpose, and worse, it breaks the launcher. The walk does not count `patternProperties` keys in `want`, so the case would pass unchanged. But the launcher's `_check` refuses any keyword it does not know (indep_launch.py:346–374), and `patternProperties` is not among them. With that form, every counts object of every flow fails the schema: the altered copy turned all 39 S13 cases red, including the three as-before guards. `finish()` would log "counts schema failed" on every run of every kind, and `--counts-only` would refuse 17 everywhere. So that form would have hidden the conflict from the test while making P4 worse across every flow. The engineer was right not to use it.

### Overall: pass

Of the findings, F1 is in scope with ordinary work yes, but its consequence is "other": it fails closed. R1 and R4 are rows; R2 and R3 are Wave 3 rows. No finding is in scope, reachable in ordinary work, and fails open or loses work. The other KPI lines (S1–S10, F1–F6 outside S11/S12) are not touched by this change's code. Only `indep-counts.schema.json` and `parse_args`'s epilog changed, and I found nothing against them.

```verdict
{"kpis": [{"kpi": "S13", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S11", "verdict": "pass", "findings": [{"id": "R3", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S12", "verdict": "pass", "findings": [{"id": "R4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": []}, {"kpi": "F6", "verdict": "pass", "findings": []}]}
```