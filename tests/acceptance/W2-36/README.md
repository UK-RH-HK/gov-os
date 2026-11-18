# W2-36 acceptance tests: `gov discover`

Written by the independent test designer (MR-3) from the ticket's seven success and two failure KPI lines
(`.tickets/DAEO-w19l.md`, profile STANDARD, rewritten for Emergency 2) and the body's **Interface**, on base commit
80bd9f355, before any implementation (`src/gov/discover/` does not exist there). Every case is of the acceptance
kind. Public interfaces only: `gov` run as a subprocess (`python3 -m gov.cli.main <args> --root <P>`, `PYTHONPATH`
this worktree's `src/`, run in P): `gov discover` in its four forms, `gov readiness --specification <id> --json` and
`gov brief <role> <ticket>`; `git`; the files of P; and the spec-writing skill's `check_spec.py`. No `gov.discover`
module is imported.

## The fixtures

- **P** (`w2_36_support.build_project`, once per session): a git repository named `planted-project` (so the
  vendored `tk` gives ids `pp-xxxx`), holding `.tickets/`, `governance/kernel/bin/tk` (from
  `template/governance/kernel/bin/tk`), `openspec/schemas/feature-readiness/` (from `template/openspec/`),
  `governance/project/facts.yaml` (this worktree's), the kernel templates at `template/governance/kernel/templates/`
  (where `gov brief` looks first), the adopted template's `.gitignore` (`.gov-runtime/`, `__pycache__/`), no memory
  store, and the four planted files: `docs/report.md` and `openspec/specs/report/spec.md` (both mention "CSV" and
  "export"), the ticket `.tickets/pp-rp01.md` (its body mentions "report page") and `docs/unrelated.md` (none of the
  idea's words, not even as part of a word). Everything is committed, so `git status --porcelain` starts empty.
- **P with a change** (`build_with_change`, once per session): P plus `openspec/changes/add-csv-export-report-page/`
  as the interface says discovery writes it (proposal.md at LITE with `id: SPEC-add-csv-export-report-page`, the
  schema template's readiness.yaml, all 26 rows `MISSING`), a `spec.md` written to spec-form that passes
  `check_spec.py` (K1 and K2 each with a `Fails if:` line, one test-data row, `## Verify` with `- K1:` and `- K2:`,
  two Non-goals bullets), and its discovery ticket `pp-ds01`; committed. It is the start of S3, S6, F1 and F2's
  cases, so a fault in discovery does not hide the check, the feature ticket or the refusals.
- **S4's planted change** `csv-export-gaps` at LITE: every mandatory row `PRESENT` with evidence but `scenarios`
  (`MISSING`), `inputs` (`MISSING`, `depends_on: [scenarios]` on its row) and `acceptance_tests` (`PROVISIONAL`);
  the other 16 rows `MISSING` (not required at LITE).
- **Shared outcomes** (each once per session, in its own copy): the first discovery (S1, S2), the plain-language
  discovery (S7), S5's STANDARD discovery then `--generate` (S5, and S2's STANDARD run), S4's generation (then
  `gov readiness`, then a second `--generate`) and S6's `--ticket`. Every other case that writes works in its own copy.
- **Environment**: a fake `HOME` (no memory store), `PYTHONUSERBASE` the real user base, no `GOV_*` variable of the
  caller's (`GOV_PIN=off`, a rebuild lock of the session's own), `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` removed.
  S5's runs (discovery, generation and both briefs) also have `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` (and the lower
  case forms) set to a closed local port and `NO_PROXY` removed.
- A fixture that cannot be built fails its cases with "W2-36 fixture could not be built (not the feature under
  test)", never as the feature's failure.

Run: `TMPDIR=$(mktemp -d) python3 -m pytest tests/acceptance/W2-36 -n 2 -q` (about half a minute), or
`gov accept W2-36`.

## The map

| KPI line | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_36_discover.py::test_discovery_writes_one_ticket_and_one_change_folder_and_nothing_else`, `test_w2_36_discover.py::test_json_result_names_the_change_the_spec_id_the_ticket_and_the_spec_path`, `test_w2_36_discover.py::test_proposal_front_matter_is_a_lite_draft_specification_naming_its_ticket`, `test_w2_36_discover.py::test_readiness_holds_the_26_rows_all_missing_and_unlinked`, `test_w2_36_discover.py::test_discovery_ticket_is_a_product_spec_ticket_whose_verify_is_the_check`, `test_w2_36_discover.py::test_sources_read_lists_the_three_matching_files_and_says_memory_is_not_available` | `gov discover` does not exist: exit 2, "invalid choice: 'discover'", no ticket and no change folder |
| S2 | `test_w2_36_draft.py::test_draft_has_the_nine_parts_in_order_then_verify_and_sources_read`, `test_w2_36_draft.py::test_draft_problem_holds_the_idea_verbatim`, `test_w2_36_draft.py::test_lite_draft_asks_one_package_per_mandatory_row_and_one_on_profile_and_types`, `test_w2_36_draft.py::test_standard_draft_records_profile_and_type_and_asks_its_rows_with_no_profile_package`, `test_w2_36_draft.py::test_check_refuses_the_unfilled_draft_by_name_but_not_problem_or_open_questions` | `gov discover` does not exist: exit 2, "invalid choice: 'discover'", so no draft `spec.md` |
| S3 | `test_w2_36_check.py::test_check_passes_the_finished_spec_and_lists_every_open_required_row_unlinked`, `test_w2_36_check.py::test_check_names_a_linked_rows_ticket_and_leaves_out_a_present_row` | `gov discover --check` does not exist: exit 2, "invalid choice: 'discover'", no `PASS` and no `OPEN` line |
| S4 | `test_w2_36_generate.py::test_generate_creates_one_ticket_per_open_row_naming_its_row_with_its_class_and_role`, `test_w2_36_generate.py::test_generate_writes_each_rows_gap_ticket_in_place_and_changes_nothing_else`, `test_w2_36_generate.py::test_gap_tickets_depend_on_each_other_in_the_order_of_spec_work`, `test_w2_36_generate.py::test_readiness_lists_no_open_row_as_unlinked_after_generate`, `test_w2_36_generate.py::test_a_second_generate_exits_0_creates_no_ticket_and_changes_no_byte`, `test_w2_36_generate.py::test_a_row_already_linked_to_an_existing_ticket_gets_no_ticket` | `gov discover --generate` does not exist: exit 2, "invalid choice: 'discover'", no gap ticket, every open row still `UNLINKED` |
| S5 | `test_w2_36_generate.py::test_research_rows_get_research_tickets_whose_kpi_names_the_evidence_record`, `test_w2_36_generate.py::test_gov_brief_research_accepts_each_research_ticket`, `test_w2_36_generate.py::test_gov_brief_product_spec_on_the_discovery_ticket_holds_the_idea_and_the_spec_path`, `test_w2_36_generate.py::test_discover_and_generate_name_the_brief_command_of_each_ticket_they_created` | `gov discover` does not exist: exit 2, "invalid choice: 'discover'" (with no key and no network as without), so no discovery ticket, no research ticket and no brief command named |
| S6 | `test_w2_36_ticket.py::test_ticket_writes_exactly_one_new_ticket_and_nothing_else`, `test_w2_36_ticket.py::test_feature_ticket_is_an_engineer_ticket_of_the_spec_with_its_paths_non_goals_and_test_path`, `test_w2_36_ticket.py::test_feature_ticket_has_a_success_and_a_failure_line_per_k_each_with_the_ks_verify`, `test_w2_36_ticket.py::test_gov_brief_accepts_the_feature_ticket_and_its_kpi_table_holds_every_k` | `gov discover --ticket` does not exist: exit 2, "invalid choice: 'discover'", no feature ticket |
| S7 | `test_w2_36_discover.py::test_plain_request_makes_the_same_change_and_files_and_one_ticket`, `test_w2_36_discover.py::test_plain_request_problem_holds_its_words_verbatim`, `test_w2_36_discover.py::test_plain_request_reads_the_same_sources_and_asks_the_same_packages` | `gov discover` does not exist: exit 2, "invalid choice: 'discover'", no change `add-csv-export-report-page` |
| F1 | `test_w2_36_check.py::test_check_refuses_an_unfinished_spec_by_name_and_never_prints_pass` | `gov discover --check` does not exist: exit 2 with "invalid choice: 'discover'", not exit 1 with the named `REFUSED` line (four cases: `REFUSED Verify: K2 has no verify`, `REFUSED Verify: K3 is not a KPI`, check_spec.py's `REFUSED KPIs: K1 names code (...)`, `REFUSED Goals: missing`) |
| F2 | `test_w2_36_refusals.py::test_discovering_an_existing_change_again_is_refused_and_overwrites_nothing`, `test_w2_36_refusals.py::test_discover_with_no_words_is_refused_and_writes_nothing`, `test_w2_36_refusals.py::test_a_change_that_does_not_exist_is_refused_by_name`, `test_w2_36_refusals.py::test_ticket_on_a_spec_the_check_refuses_is_refused_listing_the_lines_and_writes_no_ticket` | `gov discover` does not exist: exit 2 with no JSON envelope, so no `DISCOVER_EXISTS`, `DISCOVER_CHANGE_NOT_FOUND` (three cases: `--check`, `--generate`, `--ticket`) or `DISCOVER_SPEC_NOT_READY`; for no words, neither `DISCOVER_NO_WORDS` nor `gov discover`'s own usage error, only "invalid choice: 'discover'" |

A refusal case is red on the base because it asks for the feature's own refusal (the `--json` envelope's
`error.code`, or the named `REFUSED` line with exit 1), not merely a non-zero exit: argparse's exit 2 for an unknown
command is not the refusal the line asks for.

## How the lines are read

- **S1**: "nothing else" is `git status --porcelain --untracked-files=all` listing exactly the new ticket file and the
  change folder's three files. The JSON result "names" each of the change, `SPEC-<change>`, the ticket id and the spec
  path when some string value of `result` equals it (the spec path: ends with it). `discovers` names the change when
  it holds the change name. "Whose verify is `gov discover --check <change>`": a success KPI's verify (a `{line,
  verify}` mapping, or a string's text after `Verify:`), backticks removed, holds that command. The three sources are
  checked by path in `## Sources read`; `docs/unrelated.md` must not appear; the memory line matches
  `Memory: not available` followed by a reason.
- **S2**: the `##` headings outside HTML comments are exactly the nine parts, `Verify`, `Sources read`, in order. A
  package is a `- Question:` line with its `- Options:` line (at least two `(cost: ...)`) and `- Recommendation:`
  line. A question names a row by its key (or the key with spaces) or its schema name, as a whole word not joined to
  a hyphenated type (so `performance-capacity` does not name `performance`). LITE: exactly eleven packages, the ten
  mandatory rows each named, and one naming none of them that mentions the profile. STANDARD with
  `performance-capacity` (S5's run, read before its `--generate`): `profile: STANDARD`,
  `capability_types: [performance-capacity]` and exactly twelve packages, each naming a required row (so no profile
  package), `nfr` and `performance` among them. The draft's `--check` (text form, in a copy) exits 1 with a line
  holding `REFUSED <part>:` for each of the seven parts, none for Problem or Open questions, and no `PASS` line.
- **S3**: `--check` (text form) exits 0, prints a `PASS` line and one `OPEN <key> <ticket or UNLINKED>` line per open
  required row: the ten mandatory rows, `UNLINKED`. The edge case makes `intent` PRESENT (no longer listed) and links
  `scenarios` to the existing ticket `pp-rp01` (`OPEN scenarios pp-rp01`). `check_spec.py` on the same file prints
  `PASS`.
- **S4**: the three tickets are told apart by `readiness_row.key`; `readiness_row` must equal `{specification, n,
  key}`. "No other field changed" compares the parsed record before and after: every row as before but the three
  `gap_ticket`s, now their tickets. `depends_on` is the ticket's `depends_on` key (not tk's `deps`). `gov readiness`
  exits 3 (`SPEC_NOT_CLOSED`) with `error.details.open`; each open row's `gap_ticket` must be its new ticket. The
  second run must exit 0 and leave every file outside `.git` byte-identical. The linked-row case plants `scenarios`
  with `gap_ticket: pp-rp01` and expects tickets for `inputs` and `acceptance_tests` only.
- **S5**: the research tickets are those whose `readiness_row.key` is `nfr` or `performance`; `allowed_paths` must
  hold `docs/research/add-csv-export-report-page/**`; a success KPI's verify names
  `docs/research/add-csv-export-report-page/<key>.md`, and its line and verify mention the four parts by the words
  "tested", "how", "measured" and "verdict". The discovery and generation run in the text form (as the verify writes
  them); their output (stdout and stderr) must hold `gov brief <role> <ticket>` for each ticket each created, the role
  as the ticket's `role`. The product-spec brief's stdout must hold the idea's words and
  `openspec/changes/add-csv-export-report-page/spec.md`. "No key, no network" is each of those runs passing in the
  environment above.
- **S6**: a K's success line holds its behaviour (trailing full stop aside) and its id `K<n>` as a word; its failure
  line holds its `Fails if:` text; each verify holds the K's `## Verify` text (whitespace folded, backticks removed).
  `non_goals` equals the spec's two bullets. The brief's KPI table is its `| S<n> | ... |` and `| F<n> | ... |` rows:
  exactly four, no verify `none`, each K's behaviour and `Fails if:` text with its verify.
- **S7**: the words go as separate arguments (`how could we add CSV export to the report page?`). "The same `## Sources
  read` list and the same open-question packages" compares those two sections with the first run's, after replacing
  each run's own discovery ticket id, project path and words.
- **F1**: each variant is written over the passing spec in a copy of P with a change; the line must be printed (a
  line holding it, on stdout or stderr) with exit 1 and no `PASS` line. The code line is the one `check_spec.py`
  prints for the same file (`REFUSED KPIs: K1 names code (snake_case identifier "export_rows")`).
- **F2**: "naming the folder" / "naming it" is the change name (or `no-such-change`) appearing in the envelope's
  `error`; "listing the refused lines" is `REFUSED Verify: K2 has no verify` appearing there. Every case also compares
  `git status --porcelain --untracked-files=all` (and the ticket list) before and after; the two that write nothing at
  all (`DISCOVER_EXISTS`, no words) compare every file's bytes too.
