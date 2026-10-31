# W2-64 acceptance tests (DAEO-0uhh)

W2-02's widening: the record validator through check-jsonschema; `docs/imported/` out of the schema check.
Written by the independent test designer (MR-3) from the ticket's KPI lines, its sources (DEC-872 item 2, DEC-844,
DEC-890 item 1, DEC-831, lens G F2 / R2 (a)) and the lead's design note (run 1), before the implementation.

## How the tests run

- **Public interfaces only.** core-schema's declared command (`python3 -m gov.check.schema`, from
  `template/governance/kernel/checks/core-schema.yaml`), run by `sh -c` in a project's root as `gov check` runs it:
  its exit code and its output (a list; `{"ok": true, "result": ...}`; or `{"findings": [...], ...}`).
  `gov check --json` and its `core-schema` entry. The kernel's schema files, copied by name. check-jsonschema itself
  (the installed one, 0.38.2, and its pin in `governance/project/tool-registry.yaml`, read by name).
- **This worktree's code (DEC-732).** Every process a case starts has `PYTHONPATH=<this worktree>/src`, set for that
  process (`SRC` in `w2_64_support.py`, found from the file's place). `python3` on the case's `PATH` is a wrapper
  that runs the interpreter running the suite. Run the suite from this worktree with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m pytest tests/acceptance/W2-64 -q -p no:cacheprovider -rs`.
- **The validator on `PATH` is the case's.** `PATH` is `<case>/bin:<case>/validator:/usr/bin:/bin`. The validator
  folder holds nothing, a link to the installed check-jsonschema, or a stand-in script. No other folder of the
  machine (`~/.local/bin` included) is on it. A case that needs the real tool and does not find it **fails**; it is
  never skipped.
- **Nothing is written in this worktree.** Each project is a temporary git repository built from scratch under
  pytest's `tmp_path`, with single named files copied in (the kernel schema files, the core-schema declaration, three
  close records of `docs/close/`); its tool registry holds only this repository's check-jsonschema entry. The live
  cases run in this worktree's root and only read.
- One core-schema run per case. Every case holds under parallel load (no fixed port, no shared file); none is
  added to `tests/acceptance/serial-only.txt`.

## KPI lines and their tests

"Red" below is the reason each test fails on today's code (the subset validator of `w2/integrate`, the close schema
without an evidence block). "Passes today" marks the cases that guard what stays.

### S1 — every record validated through check-jsonschema (pinned), lens G's planted ticket refused

`test_w2_64_full_validator.py`
- `test_lens_g_planted_ticket_is_refused_naming_record_and_rule` — **red**: exit 0, no finding (the subset reads
  only required fields). Expects a finding per refused fault (state_class, profile, est_loc, `deps[0]`,
  allowed_paths, kpis' `success` and `failure`) naming `ticket.schema.json`, the place and the validator's message;
  none for `status: banana` (no rule refuses it).
- `test_one_fault_the_subset_passed_is_refused[...]` (state_class, profile, deps, wbs_id) — **red**: no finding.
- `test_a_finding_under_both_layouts_is_given_once` — **red**: no finding.
- `test_the_installed_layout_alone_is_measured` — **red**: no finding.
- `test_a_valid_ticket_passes`, `test_a_missing_required_field_is_schema_missing_field`,
  `test_a_standalone_record_owes_no_shared_frontmatter`, `test_a_shared_field_is_owed_by_every_other_record` —
  pass today (what stays).

`test_w2_64_tool_red.py` (the pin)
- `test_a_validator_of_another_version_than_the_pin_is_red_naming_both` — **red**: exit 0 (no version is read).
- `test_a_registry_that_cannot_be_read_is_red` — **red**: exit 0 (the registry is not read).
- `test_no_pin_stated_still_validates[absent|no-entry]` — **red**: the fault passes.
- `test_no_pin_stated_is_green_and_says_so[absent|no-entry]` — **red**: nothing printed (no word of a pin).
- `test_the_pinned_version_is_green` — passes today.

### S2 — `docs/imported/` left out, as history, by name

`test_w2_64_imported.py`
- `test_a_refused_record_under_docs_imported_does_not_fail_and_is_named_as_history` — **red**: exit 0 but nothing
  printed (no success form, no statement).
- `test_the_pass_counts_the_records_validated` — **red**: nothing printed.
- `test_the_refusal_also_names_docs_imported_as_left_out` — **red**: no finding (the subset passes the fault), and
  a list with no statement.
- `test_the_same_record_anywhere_else_fails[...]` (`docs/adr/`, `docs/imported-notes/`, `docs/plan/imported/`) —
  **red**: no finding (the subset does not check `id` against `decision_id`).
- Live: `test_w2_64_live.py::test_core_schema_is_green_here_and_names_docs_imported` — **red**: exit 0, nothing
  printed.

### S3 — every record of the head still validates, the close records included

`test_w2_64_live.py`
- `test_core_schema_is_green_here_and_names_docs_imported` — green half passes today; red for the S2 statement.
- `test_every_close_record_here_validates_under_the_pinned_validator` — passes today; must keep passing once the
  close schema states the block.
- `test_this_worktree_holds_close_records_of_both_forms`, `test_the_installed_validator_is_the_pinned_one` —
  pass today (the live preconditions).

### S4 — the close schema states W2-66's evidence block

`test_w2_64_close_schema.py`
- `test_an_evidence_block_without_a_required_field_is_refused[<field>]`, for each of `scope`, `why_full`, `base`,
  `head`, `tree`, `changed`, `selected`, `left_out`, `skips`, `skip_count`, `failures`, `junit_xml` — **red**: no
  finding (the close schema states no block).
- `test_an_evidence_block_of_the_wrong_shape_is_refused[<case>]` (15 cases: scope, empty `why_full` on a full
  scope, an empty reason, base, an abbreviated head, tree, changed, `selected`/`left_out` without `why`, a skip
  without reason, a negative or text `skip_count`, a failure without text, `junit_xml` as text,
  `per_test_timeout` as text) — **red**: no finding.
- `test_an_evidence_block_that_is_no_object_is_refused` — **red**: no finding.
- `test_this_repository_s_close_records_validate[...]` (DAEO-c1uz's block, DAEO-uzme's with `base: null`,
  DAEO-0rfi's written before W2-66), `test_evidence_null_validates`,
  `test_the_close_s_other_fields_and_a_later_key_validate`, `test_task_stays_required` — pass today.

### S5 — W2-61's 20-question measure, after the merge

**Not a test of this ticket.** It is the orchestrator's step after the merge, once W2-61's script has landed: the
measure is run again and reported beside its baseline. No test is written for it here.

### F1 — a refused record passes; a refusal that does not name the record and the rule

- All of S1's and S4's red cases above (each asserts the record's repository path and, where it names the rule,
  the schema file, the place and the validator's message).
- `test_w2_64_full_validator.py::test_every_finding_is_on_a_record_s_repository_path` — **red**: no finding. Every
  finding has `code`, `path`, `field`, `message`; its path is a record's, never a temporary instance file's.
- `test_w2_64_full_validator.py::test_several_errors_of_one_record_are_several_findings` — **red**: no finding.
- `test_w2_64_tool_red.py::test_errors_answered_with_exit_0_are_still_refused` — **red**: no finding.

### F2 — check-jsonschema missing or failing to run reported as anything but RED

`test_w2_64_tool_red.py`
- `test_check_jsonschema_absent_from_path_is_red_naming_the_tool` — **red**: exit 0.
- `test_gov_check_shows_core_schema_red_without_the_tool` — **red**: the entry is GREEN.
- `test_a_validator_that_fails_to_run_or_answers_no_json_is_red[<kind>]` (`prints-text`, `silent-exit-0`,
  `names-no-instance`, `killed`, `fails-every-call`) — **red**: exit 0 (the validator is never called).
- `test_a_validator_that_cannot_be_executed_is_red` — **red**: exit 0.

### What stays (W2-02's KPIs) and no silent skip

`test_w2_64_what_stays.py`
- `test_a_type_absent_or_not_a_string_is_schema_invalid_type[...]`, `test_an_unknown_type_is_schema_unknown_type`,
  `test_a_type_whose_schema_is_in_neither_layout_is_unmeasured`, `test_a_record_schema_that_cannot_be_parsed_is_red`,
  `test_a_file_whose_first_line_is_not_dashes_is_no_record` — pass today.
- `test_a_common_schema_that_cannot_be_parsed_is_red` — **red**: green (the subset reads the ticket schema alone).
- `test_a_file_that_opens_with_dashes_and_whose_frontmatter_cannot_be_read_is_a_finding[...]` (no closing line, a
  YAML error, not a mapping) — **red**: skipped silently, exit 0.

## Red first

On today's code (this worktree at `894b7278`, nothing of the implementation yet), the run above gives
`63 failed, 20 passed in 17.46s`: every red case fails for the reason stated above, and the 20 that pass are the
ones marked "passes today". The fixtures were checked against the installed check-jsonschema 0.38.2 directly: the
valid ticket and the audit report pass; lens G's planted ticket gives exactly the seven errors expected
(`$.state_class`, `$.deps[0]`, `$.allowed_paths`, `$.kpis` twice, `$.profile`, `$.est_loc`), and none on `status`.

## Earlier acceptance tests this change affects (named, never edited)

Revising any of them is outside this folder; the lead returns them as a package. Run against today's code by the
test designer: `tests/acceptance/W2-54/test_w2_54_audit_report.py`, 24 passed; the others were read, not run.

1. **W2-54, `tests/acceptance/W2-54/test_w2_54_audit_report.py`** — every case that calls `w2_54_support.core_schema`
   (`Box.env()` sets `PATH=<workdir>/bin:/usr/bin:/bin` and a throwaway `HOME`; the bin holds `python3`, `git`,
   `gitleaks` wrappers and no check-jsonschema): with this change they see RED (the tool is absent) by design.
   `w2_54_support.core_schema` also asserts that the output is a JSON **list** (`assert isinstance(findings, list)`),
   which the success form `{"ok": true, ...}` and the refusal form `{"findings": [...], ...}` are not. Affected:
   `test_an_audit_report_*` green cases (the two that assert no finding at lines ~121–137), the shape cases
   `test_an_audit_report_s_fields_are_held_to_the_schema_s_shapes[...]`,
   `test_a_record_outside_the_audit_folder_that_states_no_type_still_fails[...]`,
   `test_an_audit_report_lacking_a_required_field_fails_naming_it[...]`. Not affected:
   `test_w2_02_s_other_types_are_judged_as_an_unknown_type[...]` (it runs the module as an earlier commit left it,
   `core_schema_at`).
   `test_core_schema_is_green_on_this_repository_with_w1_43_untouched` runs with `worktree_env()` (the suite's own
   environment, its `PATH` included) and asserts only exit 0: not affected where the suite's `PATH` holds
   check-jsonschema.
2. **W2-54, `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here`** — reads
   the close's own `gov check` result (W2-75, `GOV_CLOSE_CHECK_RESULT`) or runs `gov check` here: green after the
   change only if that run's `PATH` holds check-jsonschema. Not run by the test designer.
3. **W2-02, `tests/acceptance/W2-02/`** (`w2_02_support.env` keeps the suite's `PATH`, so the tool is found where the
   suite's `PATH` holds `~/.local/bin`): the subset's own wording is not pinned (findings are matched by `code`,
   `path`, `field`, or a word of the message; `names_field_or_part` accepts a top-level `field`). Affected only if a
   fixture record holds a value the full schemas refuse and a case expects it green; and on any machine whose `PATH`
   lacks check-jsonschema, every core-schema case turns RED.
4. **W1-26** (`w1_26_support` keeps the suite's `PATH`), **W1-30** (`test_w1_30_r15_record_types.py`; it reads a
   dict's `findings` and asserts findings ⇔ non-zero exit, which the new forms keep) and **W2-66**
   (`test_w2_66_followed_couplings.py` reads a recorded check result): affected only where a fixture the subset
   passed is refused by the full schemas (for example W1-26's green bases in `test_w1_26_derived.py`,
   `test_w1_26_dec436.py`), or on a `PATH` without check-jsonschema.
5. **W2-59, `test_w2_59_judge_checks.py`** — compares core-schema's status between two runs in the same environment
   and asserts no `No module named`; with no check-jsonschema on its judge's `PATH` both runs are RED and the
   comparison still holds. Not expected to be affected.
