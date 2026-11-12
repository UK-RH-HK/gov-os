# W2-173 (DAEO-qz4p): the launch script's follow-ups for the memory audit — evidence

Engineer eng-1, 2026-11-12, branch `w2/W2-173`, base of the script `2f98aecbc` (W2-149's merge). Sources: DEC-1120 (2)-(3),
DEC-1101 (2), DEC-1112 (3), DEC-1113, DEC-1050, DEC-1073. The acceptance tests (`tests/acceptance/W2-173/`) were not
read; everything below is built to the ticket's KPI lines and the lead's interface notes.

## KPI lines, what implements them, the tests that show them

Unit tests: `tests/unit/orchestration/test_w2_173_indep_launch.py` (planted HOME, sets root and repository from W2-149's
`World`, a stub `claude` on PATH; nothing real).

| KPI | What implements it (indep_launch.py unless named) | Unit tests |
|---|---|---|
| S1 effort | `EFFORTS` (the five); `build_and_run` stage 10, right after `resolve_brief`: a front-matter `effort` that is not one of the five strings (another word, a number, a boolean, a list, a map, null) raises `Refuse(10, "effort")` before anything is built; `session_flags(..., effort=None)` adds `--effort <value>` after `--model` only when one is named, used by `run_canary` and `run_session` (the canary keeps running with the session's own flags, W2-149 S11); `WALL.json` gains `effort`; `State.counts` gains the top-level `effort` (null until stage 10 reads the brief); `indep-counts.schema.json` gains `effort` (`["string","null"]`, enum the five and null) and lists it in `required` (the counts object is built in one place, so every path carries it) | `test_s1_effort_high_reaches_the_canary_and_the_session_and_the_counts`, `test_s1_each_of_the_five_is_recorded_in_the_wall_manifest[*]`, `test_s1_no_effort_line_no_flag_and_null`, `test_s1_an_effort_outside_the_five_refuses_10_and_builds_nothing[loud, High, 3, empty (null), true, [high], {a: b}, 'high ']` (the sets root byte-identical, no seed line, no call to the stub), `test_s1_a_refusal_before_the_brief_is_read_carries_effort_null`, `test_s1_the_counts_schema_takes_the_five_or_null_and_nothing_else`, `test_s1_the_five_set_up_a_briefs_still_pass_stage_ten_without_effort` (all five set-up A flows, dry, `effort` null), `test_s1_session_flags_add_effort_only_when_given` |
| S2 stopped | `writer-result.schema.json` and `checker-result.schema.json` gain the optional `stopped` (enum: the seven `STOPPED` words); `check_result`: for a memory (non-set-up-A) writer or checker, a result read as a JSON object whose `stopped` is one of the six words other than `none` copies the word to `counts.out.stopped`, sets `out.schema_ok` to null (not checked) and raises `Refuse(21, "stopped")` before the schema check, the numbers and the out/ files; `build_and_run` takes that 21 like the existing session stop (status `stopped`, the wall packed, a trace still makes it 22). `none` or no `stopped`: as before; any other value: the schema's enum refuses it (20). Set-up A's `deliver_sgx` stop (20) and the auditor kind are untouched | `test_s2_a_result_that_says_it_stopped_delivers_nothing_and_ends_21[each word × writer, checker]`, `test_s2_a_stopped_result_ends_21_even_with_no_set_or_notes_beside_it`, `test_s2_none_or_absent_delivers_as_before`, `test_s2_none_or_absent_delivers_as_before_for_the_checker`, `test_s2_a_word_outside_the_seven_is_a_schema_refusal_20[tired, None, empty, 3, null, a list]`, `test_s2_the_result_schemas_take_stopped_as_optional`, `test_s2_a_stopped_result_with_a_trace_still_ends_22`, `test_s2_the_auditor_is_not_in_s2` |
| S3 the checker's notes | `deliver` (checker): before `deliver_file`, `check_notes(data, staged_set_ids(wall), result)`. `staged_set_ids`: the stems of the files staged under the wall's `input/set/` (nested files included), sorted; a stem twice refuses 20. `check_notes`: UTF-8; line 1 `# Cross-check notes`; `## Questions`; one line per id in id order, split on ` \| ` into at most five fields (as W2-170's `read_notes` splits it, so a sentence may itself hold ` \| `): exactly five, field 1 the id, field 2 `accept`, `revise` or `reject`, field 3 non-blank (`-` or codes), field 4 starting `also:`, field 5 non-blank; `## The set`; five lines starting `domains:`, `categories:`, `keyword:`, `supersession `, `set codes:`; nothing else. `result.json`'s `checked` equals the number of set files and `accepted`, `revise`, `rejected` the three words' counts. Any miss: `Refuse(20, "notes")`, nothing written | `test_s3_well_formed_notes_are_delivered`, `test_s3_notes_that_do_not_fit_are_refused_20_nothing_written[21 cases: a missing line (with and without counts following it), a fourth verdict word, an id not in the set, counts that disagree, checked that disagrees, ids out of order, a line twice, another heading, no set section, four set lines, set lines out of order, a line after the set, four fields, no also, an empty sentence, an empty codes field, a blank line between two questions, two trailing newlines, CRLF lines, the brief's stop form]` (the set's folder byte-identical), `test_s3_notes_not_utf8_are_refused_20`, `test_s3_check_notes_accepts_the_form_and_blank_lines_beside_the_headings`, `test_s3_the_ids_are_the_staged_sets_file_stems_in_order`, `test_s3_a_set_with_one_stem_twice_cannot_be_matched_line_for_file_20`, `test_s3_a_round_two_checker_delivers_its_own_round_and_keeps_round_one` |
| S4 the auditor's classes | `deliver` (auditor, the memory flow only; set-up A's overlap auditor goes through `deliver_sgx`, unchanged): before `deliver_file` and the `AUDITS.log` line, `check_classes(data, staged_miss_ids(wall), result)`. `staged_miss_ids`: the `id` of each line of the wall's staged `input/misses.jsonl` (the auditor brief §2's line form; a line that is not an object with a string id, or a repeated id, refuses 20). `check_classes`: a JSON object (a repeated key refused) whose keys are exactly those ids; each value an object with `class` one of `MISS_CLASSES` and `reason` a string with no `\n` or `\r` of at most 200 characters; `result.json`'s `misses` count for each of the five classes (an absent class is 0) equals the classes' count. Any miss: `Refuse(20, "classes")`: no `miss-classes.json`, no `AUDITS.log` line | `test_s4_well_formed_classes_are_delivered_and_the_audit_logged`, `test_s4_classes_that_do_not_fit_are_refused_20_nothing_written[15 cases: a missing id (with and without counts following it), an extra id, a sixth class, a two-line reason, a carriage return, a reason of 201 characters, counts that disagree, counts that disagree by a zero, a bare class string, no reason, a reason that is not a string, a list, not JSON, an id twice]` (the audit's folder byte-identical, no AUDITS.log), `test_s4_a_reason_of_200_characters_and_an_empty_misses_file_pass`, `test_s4_an_unreadable_misses_file_refuses_20` |
| S5 nothing else | `CODES` and `STOPPED` unchanged; the existing 21 (`stopped`) and 20 reused; the module docstring gains one paragraph for these four changes; no template, path map, guard, approved list or brief touched | `test_s5_the_exit_codes_and_reasons_are_as_at_the_base`; W2-149's suites below |
| F1-F4 | as S1-S4 and the diff below: `git diff --name-only dac438772` lists only the ticket's allowed paths | the same |

### Judgements the lead left to me
- **Blank lines in the notes (S3):** tolerated only next to a heading (after `# Cross-check notes`, around `## Questions`
  and `## The set`); a blank line between two question lines or two set lines, or after the last set line, refuses 20.
  Reason: the brief's §6 shows the form without blank lines but says nothing of spacing around headings, and the next
  step (W2-170's `read_notes`) skips blank lines; a blank line beside a heading changes nothing either reads.
- **Five fields:** split at most four times on ` | ` (W2-170's reader does the same), so a sentence holding ` | ` is still
  one fifth field; fewer than five fields refuses.
- **The canary gets `--effort` too:** it is built by the same `session_flags` and W2-149's S11 holds that the canary runs
  with the session's flags (`test_canary_runs_with_the_session_flags_plus_its_folder` compares them).
- **`effort` in the counts schema's `required`:** yes. W2-149's own unit test
  (`test_counts_schema_closes_every_object_and_string`) holds `required` equal to the properties, and every counts object
  the script writes carries it. Consequence: `--counts-only` on a `counts.json` written before this change (no `effort`)
  now refuses 17 (see Risks).

## S5: the diff

`git diff --stat 2f98aecbc -- governance/project/orchestration/tools/`:

```
 governance/project/orchestration/tools/deadman.py  | 159 +++++++++++++++++++--
 .../orchestration/tools/dispatch/dispatcher.py     |  74 ++++++++++
 .../tools/indep-schemas/checker-result.schema.json |   3 +-
 .../tools/indep-schemas/indep-counts.schema.json   |  16 +++
 .../tools/indep-schemas/writer-result.schema.json  |   3 +-
 .../project/orchestration/tools/indep_launch.py    | 159 +++++++++++++++++++--
 .../project/orchestration/tools/stop_idle_check.py | 118 ++++++++++++++-
 7 files changed, 501 insertions(+), 31 deletions(-)
```

`deadman.py`, `dispatcher.py` and `stop_idle_check.py` are not this ticket's: they came in with integrate before the
ticket started (`905b82a3b` ACT-DEADMAN-WAKE-1, `c769396a2` ACT-DEADMAN-STANDBY-1, `256b4e12d` ACT-IDLE-GUARD-1).
This branch's own change (`git diff --stat dac438772`) is the three schemas, `indep_launch.py` and the unit test file.
`git diff 2f98aecbc -- governance/project/orchestration/tools/indep_launch.py` holds only: the docstring paragraph; the
constants `EFFORTS`, `NOTES_HEAD`, `NOTES_SET`, `VERDICTS`, `REASON_MOST`; `effort` in `State.counts`; `session_flags`'s
`effort`; its two callers; `staged_set_ids`, `staged_miss_ids`, `check_notes`, `check_classes` and their call in
`deliver`; the stop in `check_result` and `ctx["result"]`; the stage-10 effort check, `effort` in `WALL.json` and
`ctx`; the 21 branch in `build_and_run`'s delivery `except`.

## Test runs (whole-folder form; HOME an empty scratch folder; `-m "not local_only" -k "not real and not green_here and not time_limit"`)

`PYTHONUSERBASE=/home/usain/.local` was added to each run: with HOME pointed at the empty folder, Python no longer
finds the user's site-packages, where pytest is installed. The repository's opt-in lists (`tests/optin-lifted*.txt`) keep
one representative per parametrized case in the default form, so each suite was run in the default form and with
`--optin lifted,breadth` (every case).

| Suite | Default form | Every case (`--optin lifted,breadth`) |
|---|---|---|
| `tests/unit/orchestration/test_w2_173_indep_launch.py` | in the three-file run below | 89 passed, 0 failed |
| `tests/unit/orchestration/test_w2_149_*.py` + `test_w2_173_indep_launch.py` | 116 passed, 2 failed, 3 skipped | W2-149's two files: 151 passed, 2 failed, 3 skipped |
| `tests/acceptance/W2-149` | 167 passed, 6 failed, 35 skipped | 167 passed, 6 failed, 35 skipped |

W2-149's merge count was 206 passed, 0 failed, 3 skipped. Here the live and bwrap cases (marked `live` and `bwrap`) are
skipped in the sandbox, which accounts for the 35 skipped; the CTO runs them outside. The 6 failed and the 2 unit failures
are listed in the next section; every one is a case whose planted product or fixed key set S1, S3 or S4 changes. The
`-k` exclusion left out the cases whose names hold `real`, `green_here` or `time_limit` (none in these suites' failures).

## W2-149's cases that S1, S3 and S4 turn red (a contradiction between the KPI lines)

S5 asks W2-149's cases to pass unchanged, but six of its acceptance cases and two of its unit cases plant products that
S1, S3 and S4 now require the script to treat differently:

| Case | Why it is red now | KPI |
|---|---|---|
| `tests/acceptance/W2-149/test_w2_149_results.py::test_s13_the_counts_schema_is_closed_and_every_value_typed` | its `free_text` holds the counts' top-level keys to W2-149's fixed set (`COUNTS_KEYS`), which has no `effort` | S1 ("records it ... in counts.json") |
| `...::test_s13_a_refusal_line_carries_its_code_reason_word_and_approved_sha256` | the same `free_text` check on a refusal line | S1 |
| `...::test_s16_the_delivery_lands_only_where_the_kind_delivers[checker]` | its planted notes (`GOOD_DELIVERY`: `# Cross-check notes (planted)` / `- q01 accepted`) do not fit the brief's form: 20 | S3 |
| `...::test_s16_the_delivery_lands_only_where_the_kind_delivers[auditor]` | its planted classes map each id to a bare word, not `{class, reason}`: 20 | S4 |
| `...::test_s17_a_finished_wall_is_one_file` | delivers the same planted checker notes: 20 | S3 |
| `tests/acceptance/W2-149/test_w2_149_canary_session.py::test_s10_tools_budget_and_timeout_come_from_kinds_yaml_when_the_brief_names_none` | delivers the same planted checker notes and asserts 0: 20 | S3 |
| `tests/unit/orchestration/test_w2_149_indep_launch.py::test_checker_delivers_its_notes` | notes `notes\n`: 20 | S3 |
| `tests/unit/orchestration/test_w2_149_indep_launch.py::test_auditor_delivers_its_classes_and_the_audit_is_logged` | misses line without an id, classes `{}` against a count of 2: 20 | S4 |

No form of S3 or S4 that refuses the KPI lines' malformed files can deliver these planted ones, and no top-level
`effort` passes the fixed key set; gating the checks on a brief's path or front matter would make them fail open for a
memory brief elsewhere (DEC-135). None of these tests was edited (they are not this ticket's paths). The fix belongs
to their owners: the acceptance cases' planted `GOOD_DELIVERY`/`GOOD_RESULT` for the checker and the auditor in the briefs'
fixed form and `effort` in `COUNTS_KEYS` (test designer, `tests/acceptance/W2-149/w2_149_support.py`), and the two unit
cases (an engineer on W2-149's paths).

## Run 2: the CTO's P-1 (a) (DEC-1112 (3), DEC-105 apply now, DEC-866), 2026-11-12

S5 now reads "W2-149's cases pass, with the 8 cases' planted products in the fixed form" (the ticket's last paragraph).
Test designer td-2 (Opus, high, C3) changed only `tests/acceptance/W2-149/w2_149_support.py` (`009642705`, trailer
`Rewrite-Reason: DEC-866, W2-173's S3 and S4`; merged `05abbd36f`): `COUNTS_KEYS` gains `effort`; the checker's planted
notes are `CHECKER_NOTES` in checker.md §6's form (q01, q02, q03 of the staged set; accept, revise, accept; the result's
3/2/1/0 unchanged); the auditor's planted classes are `AUDITOR_CLASSES` in auditor.md §6's form (m1, m2, m3 of the planted
misses.jsonl), and the auditor's result counts are derived from them. No assertion and no case changed; the script was not
touched in run 2.

| Check (head `05abbd36f`) | Result |
|---|---|
| `gov accept W2-173` | pass: 79 passed, 0 failed, 0 skipped (S1 25, S2 23, S3 15, S4 13, S5 1, F1 6, F2 24, F3 1, F4 1) |
| `gov accept W2-149` | 174 passed, 0 failed, 35 skipped; every line passes but success-26, whose only 2 cases are live (skipped without the CTO's `GOV_W2_149_LIVE=1`), as at run 1; run 1 was 168/6/35 |
| `tests/acceptance/W2-149`, td-2, whole-folder form from a writable copy | 173 passed, 35 skipped, the same as base `2f98aecbc` in the same form |
| `lead_verify` (whole suite, parallel) | 4065 tests, 8 failed, 41 skipped: W2-149's two unit cases below and six W2-96 signal cases |
| `git diff --name-only` against the merge-base with `w2/integrate` (`70e5840d9`) | only the ticket's allowed paths and `tests/acceptance/W2-173/**` (F3, F4) |

The six W2-96 signal cases (`tests/unit/accept/test_w2_96_review3.py`, `_review4.py`, `_run2.py`) are not this ticket's:
the branch changes neither `src/` nor `tests/unit/accept/` against its merge-base with `w2/integrate`. They are red again
when run alone with the empty HOME (13 failed, 7 passed over all their parameters); run 1 found them green alone with the real
HOME.

W2-149's two unit cases are in `tests/unit/orchestration/test_w2_149_indep_launch.py`, outside this ticket's paths, so they
are not edited here. Each needs its planted product in the fixed form (td-2's proposal, checked on a copy: both pass, and the
whole file passes, 49 passed):
- `test_checker_delivers_its_notes`: plant `out/notes.md` in §6's form for the unit set (q01, `sub/q02`), with
  `q01 | accept | - | also: none | ...` and `q02 | revise | R6-SPAN-MISSES | also: none | ...`, `## The set` and its five
  lines. The result (2/1/1/0) stays; the two asserts read that text and its sha256 instead of `"notes\n"`.
- `test_auditor_delivers_its_classes_and_the_audit_is_logged`: give `misses.jsonl` string ids (`{"id": "m1", ...}`,
  `{"id": "m2", ...}`), and set `classes.json` to `{"m1": {"class": "retrieval_miss", "reason": ...}, "m2": {...}}`. The
  result `{"misses": {"retrieval_miss": 2}}` and the counts assert stay; the `miss-classes.json` assert reads the new text.

## Risks
- `--counts-only` on a counts.json written before this change refuses 17 (its object lacks the now-required `effort`).
  The set-up A runs already on disk are such files; `round1_files` reads them without the schema and is unaffected.
- The real `claude` CLI must accept `--effort <value>`; the stub here records the flag only. The live cases (CTO) show it.
- The checker's brief §7 (a stop) and the auditor's §7 (a stop: no classes.json) both end 20 now, as before for the
  auditor; the checker brief names no `stopped` word, so a checker that stops by its brief ends 20, not 21, unless a
  later brief names the word.
