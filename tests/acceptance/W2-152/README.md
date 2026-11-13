# W2-152 acceptance tests: gov brief and the ready check

Ticket DAEO-o5x1 (W2-152), profile STANDARD. Written by the independent test designer (MR-3) before any
implementation, from the ticket's ten KPI lines, its three failure lines and its body's "Interface" section; W2-128's
"Interface and rounds" (DAEO-t8mp: the placeholder syntax, `keys.yaml`, the facts file's shape); `R3-TEMPLATES.md`
§B "Filling", §C, §D TPL-3 and TPL-5; and the templates and facts as merged on `w2/integrate` at `97f39dc4e`.
Nothing of this ticket's implementation was read.

KPI cells use positions in the ticket: `S<n>` is the n-th success line, `F<n>` the n-th failure line.

## How they run

    HOME=<empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-152 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

About 15 s. No model, no network, no GPU, no store, no `gov retrieve`. No case is named `real`, `green_here` or
`time_limit` and none is marked `local_only`, so the exclusion leaves nothing out. The cases need `git`, `PyYAML` and
`jsonschema` 4.x.

## What the cases do

- **Fixture repositories, never this one.** Each case builds a repository under `tmp_path/repo`: a `.tickets/` with
  planted tickets (tk's form: front matter between `---` lines, `created:` unquoted as tk writes it), a
  `governance/project/facts.yaml` and the kernel templates at `template/governance/kernel/templates/`. Two template
  sets:
  - **kernel**: this tree's templates and facts file, copied at test time (`ready.new_since` set to the fixtures'
    date, `2026-11-10`);
  - **planted** (`fixtures/planted/`): a small T-0 and six role templates under the case's control, with this tree's
    `keys.yaml` and a planted facts file (`w2_152_support.planted_facts`: paths under `/fx/`, `budgets.brief` 4321,
    steps `alpha`, `beta`, `gamma` on).
- **The public interface.** `python3 -B -m gov.cli.main brief <role> <ticket> [...] --root <tmp>/repo [--json]` as a
  subprocess, with `PYTHONPATH=<this tree>/src`, an empty `HOME`, `PYTHONDONTWRITEBYTECODE=1` and dead proxies.
- **The READY ticket** (`ready_front`): `DAEO-fx01`, `wbs_id` W2-901, title "Build the widget", every required
  field, both advisory items satisfied, `reads`/`needs`/`waits_on` set, created after `ready.new_since`. Its KPI
  lines carry a verify in each form (`{line, verify}` and a string holding `Verify:` and text). Each case changes one
  thing.
- **Golden files (S1, S6)** are committed in `fixtures/golden/`, written by hand from the planted inputs by this
  rule: each `{KEY}` replaced by its value (`{ID}` the tk id, `{W2}` the `wbs_id`, `{TITLE}` the title, `{PROFILE}`
  the profile, `{ROLE}` the role argument, a `paths` key upper-cased its path with its own placeholders filled,
  `{WRITE_TREE}` `{TESTS_TREE}` for a test designer and `{TREE}` otherwise, `{CMD:name}` the command's `run` form
  filled, `{LEAD_NOTE}` and `{REPAIR}` "none" with no `--part`/`--repair`), a `{STEP:name}` line replaced by the
  step's `line` filled. The comparison drops a leading front-matter block, trailing white space on each line, and
  leading and trailing blank lines; nothing else. A lead golden file is the selected run block, which must appear in
  the lead brief as one contiguous run of lines (where in T-0 it goes is the implementation's).
- **Refusals** are read under `--json` from the API-0002 envelope: `ok: false`, `error.code` `BRIEF_NOT_READY`,
  `error.details.findings` a list of `{code, detail}`; a KPI finding's detail begins with `S<n>`/`F<n>`, the others
  contain the key, ticket or reference named. Without `--json`: non-zero exit, nothing on stdout, and one stderr line
  holding each code with its detail.
- **Warnings** (S3, S8): without `--json`, stderr lines `gov brief: <CODE> <detail>`, and a `gov brief:` line holding
  the size and facts.yaml's `budgets.brief`; with `--json`, `result.warnings` (items `{code, detail}` or
  `"<CODE> <detail>"`), `result.size` (an int, at most the brief's length) and `result.budget`.
- **Role template text (S4, S6)** on the kernel templates: a fragment of a role template's line (the text between
  placeholders, 25 characters or more) that occurs neither in T-0 nor in facts.yaml must not be in the brief; for the
  lead, the run section (its heading, its blocks and its `{STEP:}` lines) is excepted, and each other kind's block
  fragments (15 characters or more, not in T-0, facts.yaml or the selected block) must be absent. The blocks are read
  as the ticket defines them: from a line `**<kind>**:` to the next such line or the section's first `{STEP:` line.
- **The filesystem spy (F3).** `w2_152_spy.py` runs gov under a Python audit hook (PEP 578) and logs every `open`
  (with its write mode or flags), every call that changes the file system (`os.mkdir`, `os.rename`, `os.remove`,
  `shutil.*`, `tempfile.mkstemp`, ...) and every process start. Files under the repository that may be opened: the
  ticket files (`.tickets/*.md`: the ticket, and the tickets a `depends_on`, a `waits_on` or an "until" names),
  `facts.yaml`, the kernel templates (either location), the `--part`/`--repair` files, and the CLI's own
  configuration every gov command loads (`governance/project/{path-map,secrets,retrieval,rebuild}.yaml`, DEC-185;
  never planted). Decoys (a register, notes, code, a test, a README, a schema) are planted; listing a folder is not
  counted as reading. A second case checks the tree byte for byte (content, mode, size, mtime) and a third makes the
  decoys unreadable (mode 000): the brief must be byte-identical.
- **S10's W2-128 guard** runs `gov accept W2-128 --root <this tree> --json` in the case. `gov accept` drops every
  `PYTHON*` variable from its child, so the case's scratch `HOME` holds one symlink, `.local`, to the real user site
  (where pytest is installed); nothing else of the real home.

## Map

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_152_fill.py::test_s1_golden_brief_per_worker_role[engineer]` | red | no `gov brief`: the CLI exits 2, "invalid choice: 'brief'" |
| S1 | `test_w2_152_fill.py::test_s1_golden_brief_per_worker_role[independent-auditor]` | red | no `gov brief` (exit 2) |
| S1 | `test_w2_152_fill.py::test_s1_golden_brief_per_worker_role[independent-test-designer]` | red | no `gov brief` (exit 2) |
| S1 | `test_w2_152_fill.py::test_s1_golden_brief_per_worker_role[product-spec]` | red | no `gov brief` (exit 2) |
| S1 | `test_w2_152_fill.py::test_s1_golden_brief_per_worker_role[research]` | red | no `gov brief` (exit 2) |
| S1 | `test_w2_152_fill.py::test_s1_kernel_templates_fill_for_every_worker_role` | red | no `gov brief` (exit 2) |
| S1 | `test_w2_152_fill.py::test_s1_a_w2_id_resolves_to_the_same_brief_as_the_tk_id` | red | no `gov brief` (exit 2) |
| S1 | `test_w2_152_fill.py::test_s1_templates_under_governance_kernel_are_the_fallback` | red | no `gov brief` (exit 2) |
| S2 | `test_w2_152_refusals.py::test_s2_each_unknown_placeholder_is_named` | red | no `gov brief`: no envelope, no refusal |
| S2 | `test_w2_152_refusals.py::test_s2_a_command_placeholder_with_no_such_command_is_named` | red | no `gov brief` (exit 2) |
| S2 | `test_w2_152_refusals.py::test_s2_a_string_kpi_line_without_verify_text_is_named` | red | no `gov brief` (exit 2) |
| S2 | `test_w2_152_refusals.py::test_s2_an_object_kpi_line_with_an_empty_verify_is_named` | red | no `gov brief` (exit 2) |
| S2 | `test_w2_152_refusals.py::test_s2_either_verify_form_counts_as_a_verify` | red | no `gov brief` (exit 2) |
| S3 | `test_w2_152_ready.py::test_s3_warnings_and_size_on_stderr_and_the_brief_unchanged` | red | no `gov brief` (exit 2) |
| S3 | `test_w2_152_ready.py::test_s3_json_carries_warnings_size_and_budget` | red | no `gov brief` (exit 2) |
| S3 | `test_w2_152_ready.py::test_s3_a_brief_over_its_budget_still_prints` | red | no `gov brief` (exit 2) |
| S4 | `test_w2_152_fill.py::test_s4_part_fills_lead_note` | red | no `gov brief` (exit 2) |
| S4 | `test_w2_152_fill.py::test_s4_repair_fills_repair` | red | no `gov brief` (exit 2) |
| S4 | `test_w2_152_fill.py::test_s4_no_text_of_the_kernel_role_template_is_in_a_worker_brief` | red | no `gov brief` (exit 2) |
| S5 | `test_w2_152_refusals.py::test_s5_a_template_line_until_a_closed_ticket_is_refused` | red | no `gov brief` (exit 2) |
| S5 | `test_w2_152_refusals.py::test_s5_a_part_line_until_a_closed_ticket_is_refused` | red | no `gov brief` (exit 2) |
| S5 | `test_w2_152_refusals.py::test_s5_until_a_ticket_still_open_is_not_refused` | red | no `gov brief` (exit 2) |
| S5 | `test_w2_152_rev2.py::test_s5_role_engineer_template_until_a_closed_ticket_is_refused` | red | no `gov brief` (exit 2); on the engineer's round-1 head: role-engineer.md's until line not checked |
| S5 | `test_w2_152_rev2.py::test_s5_role_lead_common_part_until_a_closed_ticket_is_refused` | red | no `gov brief` (exit 2); on the round-1 head: role-lead.md's common part not checked |
| S5 | `test_w2_152_rev2.py::test_s5_role_templates_until_an_open_ticket_are_not_refused` | red | no `gov brief` (exit 2); a guard, green on the round-1 head |
| S6 | `test_w2_152_fill.py::test_s6_golden_lead_block_per_run_kind[tests]` | red | no `gov brief` (exit 2) |
| S6 | `test_w2_152_fill.py::test_s6_golden_lead_block_per_run_kind[build]` | red | no `gov brief` (exit 2) |
| S6 | `test_w2_152_fill.py::test_s6_golden_lead_block_per_run_kind[review]` | red | no `gov brief` (exit 2) |
| S6 | `test_w2_152_fill.py::test_s6_golden_lead_block_per_run_kind[resume]` | red | no `gov brief` (exit 2) |
| S6 | `test_w2_152_fill.py::test_s6_golden_lead_block_per_run_kind[land]` | red | no `gov brief` (exit 2) |
| S6 | `test_w2_152_fill.py::test_s6_kernel_role_lead_each_run_kind_carries_only_its_block` | red | no `gov brief` (exit 2) |
| S7 | `test_w2_152_fill.py::test_s7_a_switch_turned_off_removes_its_one_line_planted` | red | no `gov brief` (exit 2) |
| S7 | `test_w2_152_fill.py::test_s7_a_switch_turned_off_removes_its_one_line_kernel` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_ready.py::test_s8_empty_allowed_paths_is_refused` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_refusals.py::test_s2_a_string_kpi_line_without_verify_text_is_named` | red | KPI_NO_VERIFY, the required field in string form; no `gov brief` |
| S8 | `test_w2_152_refusals.py::test_s2_an_object_kpi_line_with_an_empty_verify_is_named` | red | KPI_NO_VERIFY in `{line, verify}` form; no `gov brief` |
| S8 | `test_w2_152_ready.py::test_s8_a_depends_on_not_closed_is_refused[tk-id]` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_ready.py::test_s8_a_depends_on_not_closed_is_refused[w2-id]` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_ready.py::test_s8_depends_on_all_closed_is_ready` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_ready.py::test_s8_no_non_goals_warns_and_never_refuses` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_ready.py::test_s8_est_loc_401_warns_and_never_refuses` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_ready.py::test_s8_est_loc_400_does_not_warn` | red | no `gov brief` (exit 2) |
| S8 | `test_w2_152_ready.py::test_f2_advisory_items_alone_exit_0_with_ok_true` | red | exits 0 with advisory warnings only; no `gov brief` |
| S8 | `test_w2_152_rev2.py::test_s8_no_readable_kpi_lines_is_refused_naming_kpis[kpis-missing]` | red | no `gov brief` (exit 2); on the round-1 head: no KPI lines read as none lacking a verify, READY |
| S8 | `test_w2_152_rev2.py::test_s8_no_readable_kpi_lines_is_refused_naming_kpis[kpis-a-list]` | red | no `gov brief` (exit 2); on the round-1 head: READY |
| S8 | `test_w2_152_rev2.py::test_s8_no_readable_kpi_lines_is_refused_naming_kpis[success-empty]` | red | no `gov brief` (exit 2); on the round-1 head: READY |
| S8 | `test_w2_152_rev2.py::test_s8_unreadable_front_matter_is_refused_as_ticket_unreadable[unclosed-block]` | red | no `gov brief` (exit 2); on the round-1 head: refused as ALLOWED_PATHS_EMPTY |
| S8 | `test_w2_152_rev2.py::test_s8_unreadable_front_matter_is_refused_as_ticket_unreadable[invalid-yaml]` | red | no `gov brief` (exit 2); on the round-1 head: refused as ALLOWED_PATHS_EMPTY |
| S9 | `test_w2_152_ready.py::test_s9_a_ticket_created_on_new_since_without_the_field_is_refused[needs]` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_a_ticket_created_on_new_since_without_the_field_is_refused[reads]` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_a_ticket_created_on_new_since_without_the_field_is_refused[waits_on]` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_a_ticket_created_after_new_since_without_all_three_names_each` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_a_ticket_created_before_new_since_is_not_refused_for_them` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_empty_lists_are_a_declared_none` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_a_waits_on_reference_that_does_not_exist_is_refused[unknown-id]` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_a_waits_on_reference_that_does_not_exist_is_refused[unknown-record-path]` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_ready.py::test_s9_waits_on_references_that_exist_are_ready` | red | no `gov brief` (exit 2) |
| S9 | `test_w2_152_rev2.py::test_s9_facts_without_a_readable_new_since_is_refused_naming_it[no-ready-key]` | red | no `gov brief` (exit 2); on the round-1 head: the dependency check silently off, READY |
| S9 | `test_w2_152_rev2.py::test_s9_facts_without_a_readable_new_since_is_refused_naming_it[new-since-soon]` | red | no `gov brief` (exit 2); on the round-1 head: the dependency check silently off, READY |
| S9 | `test_w2_152_rev2.py::test_s9_schema_requires_ready` | red | facts.schema.json does not require `ready` (none declared on integrate; declared, not required, on the round-1 head) |
| S10 | `test_w2_152_facts.py::test_s10_facts_yaml_holds_ready_new_since_an_iso_date` | red | facts.yaml has no `ready` key |
| S10 | `test_w2_152_facts.py::test_s10_schema_declares_ready_new_since_and_the_file_validates` | red | facts.schema.json declares no `ready` |
| S10 | `test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes` | green | a guard: W2-128's 92 cases pass through `gov accept` today and must still pass |
| F1 | `test_w2_152_fill.py::test_f1_two_runs_are_byte_identical` | red | no `gov brief` (exit 2) |
| F1 | `test_w2_152_fill.py::test_f1_json_brief_is_the_same_text_as_plain_stdout` | red | no `gov brief` (exit 2) |
| F2 | `test_w2_152_ready.py::test_f2_advisory_items_alone_exit_0_with_ok_true` | red | no `gov brief` (exit 2) |
| F2 | `test_w2_152_ready.py::test_f2_every_required_field_missing_is_refused_and_each_named` | red | no `gov brief`: no envelope, no refusal |
| F3 | `test_w2_152_files.py::test_f3_the_tree_is_byte_unchanged_after_a_brief_and_after_a_refusal` | red | no `gov brief` (exit 2): the run must succeed before the tree is compared |
| F3 | `test_w2_152_files.py::test_f3_the_spy_sees_no_write_and_no_read_beyond_the_inputs` | red | no `gov brief` (exit 2) |
| F3 | `test_w2_152_files.py::test_f3_no_process_starts_and_unreadable_other_files_change_nothing` | red | no `gov brief` (exit 2) |

## Revision 2 (`test_w2_152_rev2.py`, 11 cases)

Added by a fresh independent test designer after review round 1, from the ticket's lines only (the implementation was
not read). The "round-1 head" column notes give the expected outcome on the engineer's branch as the review describes
it; these were not run there.

- **S5, every role's template:** an "until <ticket>" line in the role's own template (role-engineer.md; role-lead.md's
  common part, outside the selected run block) is refused as `UNTIL_CLOSED` when that ticket is closed, because W2-153
  delivers the whole role template as the system prompt (DEC-1050). The closed ticket is W2-909 (`DAEO-fx09`) and the
  open one W2-908 (`DAEO-fx08`); W2-901 is the briefed fixture ticket itself, so it is not the "until" target.
- **S9, never off silently:** a facts file with no `ready` key, or `ready.new_since: "soon"`, is refused (any error
  code) with `new_since` named in the envelope's error and on stderr; nothing on stdout. The schema requires `ready`.
- **S8, no readable KPI lines:** `kpis` missing, `kpis` a list, or `kpis.success` empty: refused `BRIEF_NOT_READY`,
  a finding (any code) naming `kpis`.
- **S8, unreadable front matter:** an unclosed front-matter block or invalid YAML in it: refused as
  `TICKET_UNREADABLE` (the error code, or a finding's code), never `ALLOWED_PATHS_EMPTY`.

## Checked against a stand-in

Before the commit the designer ran the cases against a throwaway stand-in `gov brief` written from the interface
alone (in the designer's scratch, never committed): 53 of 53 passed (S10 left out: it reads this tree's facts and
W2-128). Nine planted faults were each caught by the cases meant for them: role text in a worker brief (S1, S4, S6),
an advisory item refusing (S3, S8, F2), a file written (F3), the register read (F3), every lead block carried (S6),
the time in the brief (S1, F1), a process started (F3), the dependency fields ignored (S9), `depends_on` ignored
(S8, F2).
