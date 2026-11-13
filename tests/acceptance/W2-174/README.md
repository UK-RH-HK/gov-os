# W2-174 acceptance tests: the Verify pass and the adoption's facts file

Ticket DAEO-zmo4 (W2-174), profile STANDARD. Written by the independent test designer before any implementation, from
the ticket's eight KPI lines (five success, three failure), its "Interface" and "Rabbit holes", the two owner sections
at its end (S5 widened by DEC-1148 (2); the skill line moved to W2-88a by DEC-1150 (1), so there is no skill case),
the approach (`governance/project/orchestration/packages/ADOPT-VERIFY-1/APPROACH.md`), the lead's decisions L1 to L9
(the brief's text), `src/gov/brief/build.py` (`kpi_rows`, `ready_check`, `build`: read-only) and
`tests/acceptance/W2-152/` (the form of this folder). Nothing of this ticket's implementation was read.

KPI cells use positions in the ticket: `S<n>` is the n-th success line, `F<n>` the n-th failure line:

| id | line |
|---|---|
| S1 | `gov adopt --verify-list` prints the id and labels of each open or in-progress ticket with a KPI line lacking a verify; `none`, exit 0, when none |
| S2 | `gov adopt --verify-apply` appends ` Verify: <clause>` to each named line and adds `verify_pass: <date> <session>`; every other byte unchanged |
| S3 | after an apply, `ready_check` gives no `KPI_NO_VERIFY` and `gov brief engineer` builds |
| S4 | the answers file is checked by code before anything is written (unknown ticket, closed, unknown label, unanswered line, empty clause) |
| S5 | `gov adopt` writes `governance/project/facts.yaml` when there is none (schema-valid, `ready.new_since` the UTC date, product defaults, named placeholders); an existing one is left byte for byte |
| F1 | all or nothing; an unnamed or closed ticket never edited; no ticket marked while a line lacks a verify |
| F2 | nothing of `gov brief`, the ready check, the template or the schema changes |
| F3 | the verify pass reads and writes nothing outside `<repo>/.tickets/` and the answers file; no model, no network |

## How they run

    HOME=<empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-174 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

About 7 s on the finished code. No model, no network, no GPU, no store, no `gov retrieve`. No case is named `real`,
`green_here` or `time_limit` and none is marked `local_only`, so the exclusion leaves nothing out. No skip, xfail, flaky
or rerun mark. The cases need `git`, `PyYAML` and `jsonschema` 4.x. In-process cases import `gov` from the tree under
test (`conftest.py` puts its `src/` first).

## What the cases do

- **Fixture repositories, never this one.** Each case builds `tmp_path/adopted-fixture-q7x` with a `.tickets/` of
  planted tickets (tk's form), optionally the kernel templates (copied from this tree) and a filled facts file (this
  tree's `governance/project/facts.yaml` with `ready.new_since` set to `2026-11-10`: what the project's CTO has after the
  defaults, the ticket's S3 fixture). The answers file lives in a folder beside the repository, never inside it.
  The folder's name is distinctive so S5 can check the facts file does not name it.
- **The public interface.** `python3 -B -m gov.cli.main adopt --verify-list|--verify-apply <file>|--facts --root <tmp>/adopted-fixture-q7x [--session s] [--json]`
  as a subprocess (`PYTHONPATH=<this tree>/src`, an empty `HOME`, `PYTHONDONTWRITEBYTECODE=1`, dead proxies), read
  from the API-0002 envelope (`result`, or `error.code` on exit 1); and the functions `verify_pass.missing(root)`,
  `verify_pass.apply(root, answers_path, session, today)` (with `today` a `datetime.date`) and
  `facts.write_default(root, today)`.
- **Lists (S1).** Three tickets as the ticket's Verify clause says (all lines verified in both forms; two plain lines
  lacking a verify; a closed ticket with one) give exactly the second's `S2 F1`; the all-verified repository gives
  `missing == []`, `text == "none"`; a sorted, mixed repository checks the order (ids sorted, labels in `kpi_rows` order,
  one line per ticket); the list agrees with `ready_check`'s `KPI_NO_VERIFY` details.
- **Byte diff (S2).** A ticket with YAML comments (before keys, after values, on KPI lines, between lines), keys in no
  alphabetical order, five KPI lines (plain, single-quoted, double-quoted, a `{line, verify}` mapping, a plain failure
  line) and a body holding a `---` rule: after the apply the whole file equals the original with the four clauses
  appended and one `verify_pass: <date> <session>` line before the front matter's closing `---`. The mapping and every
  comment are byte-identical. The CLI case accepts the UTC date either side of the run.
- **Refusals (S4, F1).** One case per code of L4, each refused through the CLI (exit 1, code in the envelope) and
  through the function (a `GovError` of the same code), with every file of the tree (repository and the answers folder:
  names, modes, sizes, modification times and SHA-256) byte-identical afterwards. Ten tickets with a nine-good, one-bad
  answers file: the bad entry first or last (by file order and by id), five kinds of fault; an unnamed ticket and the
  closed ones are never edited; no ticket carries `verify_pass` while a line lacks a verify.
- **Facts (S5).** The file validates against `template/governance/kernel/schemas/facts.schema.json` (`jsonschema`
  Draft 2020-12 with the format checker); `ready.new_since` is a quoted ISO string equal to the UTC date of the run (a
  fixed date for the function); the text names neither the repository's path, its folder name, nor `/home/`; every
  command's `run` starts with `gov ` or is exactly `{UNSET_<NAME>}` (and then its `check` is too); `lead_verify` is
  `{UNSET_LEAD_VERIFY}`; `wait_for` starts `gov wait`. `gov brief engineer` there no longer answers
  `BRIEF_FACTS_MISSING`; `gov brief lead <ticket> --run build` is refused `BRIEF_NOT_READY` with a `PLACEHOLDER_LEFT`
  finding naming `UNSET_LEAD_VERIFY`. A repository with its own facts file (valid or not) keeps it byte-identical and gets
  `written: false`.
- **Untouched (F2).** `git diff --name-only f2b1d38af HEAD` (plus tracked changes and `git status`) of the tree under
  test names no file under `src/gov/brief/`, `template/governance/kernel/templates/` or
  `template/governance/kernel/schemas/`, and none of `src/gov/adopt/stages.py` or `tests/acceptance/W2-152/` (lead
  decision L9). The base is `f2b1d38af`; `W2_174_BASE` names another when the CTO has merged a moved integrate into the
  branch. The cases skip, with the reason, only when the tree is not a git checkout or the base commit is not in it.
  **`tests/acceptance/W2-152` must still pass unchanged: the lead runs it** (`gov accept W2-152`); it is not rerun here.
- **Scope (F3).** A decoy file outside `.tickets/` (README, register, code, facts file, notes) and decoys beside the
  answers file are byte-identical after list and apply, through the CLI and the function, and `.tickets/` holds the same
  file names afterwards (no temporary or backup file left). `verify_pass.py`'s imports (read with `ast`, nested ones
  included) name none of `socket`, `http`, `urllib`, `requests`, `httpx`, `anthropic`, `openai`, `subprocess`, and name
  `gov.brief.build`. An audit hook watches every `open` while the functions run in-process: nothing is opened outside
  `<root>/.tickets/` and the answers file (the code files Python itself loads are not counted), nothing connects or
  starts a process, and the spy is shown to see the ticket and answers reads, so it cannot pass by seeing nothing.

## Readings of the interface where it is silent (the implementation may differ in these only where noted)

- **A plain scalar cannot take ` Verify: <clause>`.** `: ` inside a plain YAML scalar opens a mapping, so
  `- The widget prints its name. Verify: a test` is not a string. The tool must re-quote the item it edits (L5 says an item
  "may" be turned into a single-quoted scalar when the clause holds `: `; it must always, because ` Verify: ` itself holds
  one). The cases therefore accept a plain item edited into either quote style, its trailing note kept, and check by
  re-reading with `kpi_rows` that the clause is exactly the verify; the two quoted items are checked byte for byte.
  Fixtures hold already-verified plain strings in single quotes for the same reason.
- **`today`** is passed to `apply` as a `datetime.date` (as `write_default`'s is), and `str(today)` is the marker's date.
- **`--session ""` / no `--session`** on `--verify-apply`: the usage error must mention the session, exit 2, write nothing.
- **A named ticket with no label answered** (`{}`) is `VERIFY_PASS_UNANSWERED` when it has a line lacking a verify.
- **A clause starting with a placeholder word** (`none of the files change: ...`) is accepted: only a clause that is
  *only* TBD, TODO, n/a or none (case, padding and trailing dots ignored) is refused.
- **An answers file naming a label already answered** (including a second apply of the same file) is
  `VERIFY_PASS_UNKNOWN_LABEL`, as L4 says.
- The default facts' other keys, and whether `launch_worker` has a product form, are the engineer's call; the cases only
  check what L7 states.

## Map

| KPI line | Test (node id) | On base | Why |
|---|---|---|---|
| S1 | `test_w2_174_list.py::test_s1_cli_names_exactly_the_open_ticket_with_two_lines_lacking_a_verify` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_function_names_exactly_the_open_ticket_with_two_lines_lacking_a_verify` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S1 | `test_w2_174_list.py::test_s1_cli_without_json_prints_the_result_as_gov_does` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_all_verified_repository_prints_none_and_exits_0_cli` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_all_verified_repository_prints_none_function` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S1 | `test_w2_174_list.py::test_s1_nothing_to_list_is_none_with_exit_0[no-tickets]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_nothing_to_list_is_none_with_exit_0[only-closed-with-a-missing-line]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_open_and_in_progress_listed_sorted_by_id_labels_in_kpi_order` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_the_list_agrees_with_the_ready_check` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_byte_diff_shows_only_the_appended_clauses_and_the_one_added_line[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_byte_diff_shows_only_the_appended_clauses_and_the_one_added_line[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_the_mapping_line_and_its_comment_are_byte_identical[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_the_mapping_line_and_its_comment_are_byte_identical[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_the_marker_is_one_line_just_before_the_closing_rule[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_the_marker_is_one_line_just_before_the_closing_rule[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_the_applied_ticket_reads_back_with_each_clause_and_every_other_value_unchanged[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_the_applied_ticket_reads_back_with_each_clause_and_every_other_value_unchanged[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_a_clause_the_style_cannot_hold_is_escaped_and_only_its_item_changes[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_a_clause_the_style_cannot_hold_is_escaped_and_only_its_item_changes[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_an_existing_marker_is_replaced_in_place_and_stays_the_only_one[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_an_existing_marker_is_replaced_in_place_and_stays_the_only_one[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_two_tickets_are_both_changed_and_each_marked[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_two_tickets_are_both_changed_and_each_marked[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_apply_without_a_session_is_a_usage_error_and_writes_nothing` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S3 | `test_w2_174_apply.py::test_s3_after_an_apply_the_ticket_is_ready_and_gov_brief_engineer_builds_its_brief` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S3 | `test_w2_174_apply.py::test_s3_the_function_applied_ticket_is_ready_too` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S4 | `test_w2_174_checks.py::test_s4_the_good_answers_are_applied_to_prove_the_fixture_is_not_the_cause` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_key_that_is_no_ticket_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_closed_ticket_is_refused_and_never_edited` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_the_ticket_does_not_have_is_refused[S9]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_the_ticket_does_not_have_is_refused[F7]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_the_ticket_does_not_have_is_refused[S0]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_whose_line_already_has_a_verify_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_answered_twice_over_an_earlier_apply_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_f1_a_line_still_lacking_a_verify_is_refused_and_the_ticket_unmarked` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_f1_a_named_ticket_with_no_label_answered_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[empty]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[spaces]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[tab]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TBD]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[tbd]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[Tbd]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TODO]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[todo]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[n-a]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[N-A]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[none]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[None]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[NONE]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[none-padded]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TBD-dot]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[none-dot]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[n-a-dots]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TODO-padded-dot]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[number]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[null]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_clause_with_words_of_its_own_is_accepted_even_when_it_starts_with_a_placeholder_word` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[missing-file]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[not-yaml]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[a-list]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[a-mapping-of-text]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[empty-file]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_a_repository_without_a_facts_file_gets_one_that_validates_and_is_a_product_default` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_the_default_file_is_the_same_text_on_a_second_repository` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_gov_brief_there_no_longer_answers_facts_missing` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_gov_brief_lead_names_the_unset_lead_verify_placeholder_as_a_refusal` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_a_repository_with_its_own_facts_file_keeps_it_byte_identical` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_a_valid_facts_file_of_the_project_is_kept_too` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_running_the_step_twice_changes_nothing_the_second_time` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_function_write_default_with_a_fixed_date` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_write_default_leaves_an_existing_file_alone` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_new_since_is_the_date_given[date0]` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_new_since_is_the_date_given[date1]` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_new_since_is_the_date_given[date2]` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| F1 | `test_w2_174_checks.py::test_s4_f1_a_line_still_lacking_a_verify_is_refused_and_the_ticket_unmarked` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_s4_f1_a_named_ticket_with_no_label_answered_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[empty-clause-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[empty-clause-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-label-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-label-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unanswered-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unanswered-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[closed-ticket-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[closed-ticket-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-ticket-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-ticket-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_a_ticket_the_answers_file_does_not_name_is_never_edited` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_the_function_never_edits_an_unnamed_ticket_either` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| F1 | `test_w2_174_checks.py::test_f1_no_ticket_is_marked_while_a_line_of_it_lacks_a_verify` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F2 | `test_w2_174_scope.py::test_f2_the_diff_against_the_base_names_no_file_of_gov_brief_the_templates_or_the_schemas` | green | a guard: the base's own diff is empty (the tree under test, not integrate, is what it checks) |
| F2 | `test_w2_174_scope.py::test_f2_the_adoption_stages_and_w2_152s_acceptance_folder_are_unchanged` | green | a guard: the base's own diff is empty (the tree under test, not integrate, is what it checks) |
| F3 | `test_w2_174_scope.py::test_f3_a_decoy_outside_tickets_is_byte_identical_after_list_and_apply_cli` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F3 | `test_w2_174_scope.py::test_f3_a_decoy_outside_tickets_is_byte_identical_after_list_and_apply_function` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| F3 | `test_w2_174_scope.py::test_f3_the_module_imports_no_network_or_model_package` | red | src/gov/adopt/verify_pass.py is missing |
| F3 | `test_w2_174_scope.py::test_f3_list_and_apply_open_nothing_outside_tickets_and_the_answers_file_and_start_no_connection` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| F3 | `test_w2_174_scope.py::test_f3_a_refusal_opens_nothing_outside_either` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |

Cases per KPI line: S1 9, S2 15, S3 2, S4 36, S5 12, F1 15, F2 2, F3 5 (a case naming two lines counts for both).
