# W2-197 acceptance tests: memory used by construction, and the memory-use log

Ticket DAEO-3d3o (W2-197), profile STANDARD (EMERGENCY-2 5.4, 5.6, 5.7; audit 2 Table 2 rows M1-M4, M6, M7, M10).
Written by the independent test designer (MR-3) from the ticket's nine success lines, its three failure lines and its
"Interface", before any implementation, reading only the integrated code at the ticket's base (`067cd2946` on
`w2/integrate`, DEC-963): `gov.retrieval.retrieve` (`retrieve`, `store_of`, the bundle), `gov.retrieve.command`,
`gov.brief` (the command and the builder), `gov.util.role_paths`, `gov.adapters.portability.compose`, `gov.adopt.facts`,
`gov.cli.main` and `gov.accept.runner`'s map reader. Nothing of this ticket's implementation was read.

KPI cells use positions in the ticket: `S<n>` is the n-th success line, `F<n>` the n-th failure line.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-197 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

About 4 s with `-n 6`, in process. No model, no network, no GPU, never the real store (`W2-00-store`) and never a real
repository's memory-use log. The cases need `git` and `PyYAML`. `gov accept W2-197 --root <worktree>` reads the map
below: 12 lines (S1-S9, F1-F3), 90 cases (parametrised functions are named once and cover every row), none unmapped.

## What the cases do

- **The planted store** (`w2_197_support.plant_store`, once per session): a git repository and a store folder as the
  integration store keeps it (W2-116), a detached linked worktree with its lexical index and record store built in
  place (`lexical.refresh`, `store.load`), the secret filter replaced, as W2-138's support builds its stores. No
  vectors. It holds the READY ticket `DAEO-fx01` (W2-901, title "Build the widget", `allowed_paths: src/widget/**`), a
  register (`DEC-101`), notes whose words meet the title (one, `notes/widget.md`, opens with a line over 100
  characters), an implementation file `src/widget/build.py` and an acceptance file
  `tests/acceptance/W2-901/test_widget_build.py`, and a path map with a `role_paths` section.
- **The stand-ins** (`conftest.py`, as W2-138's): the semantic route answers with no hit, the file route is off, the
  reranker is the identity (so every bundle here is `reranked: false`), no model is loaded. `GOV_ROLE`, `GOV_TICKET`,
  `GOV_STORE` and `GOV_SESSION` are cleared; `GOV_MEMORY_LOG` names a file in the case's own folder (the one case of
  the default place unsets it); each case runs in an empty folder.
- **The command line in process** (`gov.cli.main.main`), so the stand-ins hold for `gov brief`, `gov retrieve` and
  `gov memory-use` alike.
- **The brief's repository** (`BriefRepo`): this tree's kernel templates and facts file, copied at test time
  (`ready.new_since` set to the fixture's date), and the READY ticket, as W2-152's `real_repo`. Every `gov brief` run
  passes `--store` (the planted store, or a folder that does not exist), or sets the facts' `store_tree` or
  `GOV_STORE` to a folder under the case's `tmp_path`.
- **The oracle of S1 and S2** is the library's own bundle: `gov.retrieval.retrieve.retrieve(<store>, <query>,
  ticket="DAEO-fx01", role=<the brief's role>)` called in the case, with `GOV_TICKET` set to the brief's ticket as
  the role's own session would have it (DEC-1065 (2)); the brief itself runs with no `GOV_TICKET`. The block's index
  lines are compared with its evidence item for item (rank, path, start line, end line, id), never with a ranking
  computed here. The first-line text may be cut to 100 characters (an ellipsis after it allowed).
- **What is pinned, and what is the engineer's.** Pinned: the section heading `## What memory holds for this ticket`;
  a line outside the fenced block naming the store's commit (12 hex), its folder, the query, the item count, the stop
  reason and the word "rerank"; the fenced index lines `<n>. <path>:<start>-<end> <id> <first line>`; the two commands
  verbatim (`gov retrieve --root <store> --ticket DAEO-fx01 "<query>"`, `gov retrieve --root <store> "<your
  question>"`, the store as given or with its links followed); `Memory not reached: <CODE> <detail>.`; the stderr
  line `gov brief: MEMORY_UNAVAILABLE <detail>`; `result.memory`'s keys; the log's field names and types; the command's
  `<day> <role> retrieves <n> briefs <n> refused <n>` lines. Not pinned: the order and wording of the header line,
  the words around the commands, how `read` exposes its skipped count (if the list has a `skipped` attribute it must
  be 1), the JSON shape of `gov memory-use --json` beyond an `ok` envelope.

## Readings (lines read one way where the ticket leaves room)

- **S2, the test designer's half.** `{ticket_impl}` names the ticket's paths only in the engineer's own tree
  (`~/gov-os-worktrees/<WBS>`, DEC-963); in any other tree the integrated code is readable, so a store planted under
  `tmp_path` with this repository's exact section would withhold nothing from a test designer. The planted section
  gives the test designer a plain glob for the implementation path (`src/widget/**`); the engineer's half uses the real
  `{ticket_tests}` placeholder, which needs the brief's ticket (the brief runs with no `GOV_TICKET`).
- **S3, "no unfilled `{UPPER}` slot".** Read as the lead answered (reading (b); the ticket's line as amended in
  `e485739a1`): no generated brief holds `{QUESTION}` (`test_s3_generated_brief_holds_no_question`), and every
  `{UPPER}` slot a generated brief still holds is a form key this tree's `keys.yaml` lists, read at test time
  (`{SUBJECT}`, `{COMMIT_PATHS}`, `{EXIT_FILE}`, `{FOLDER}`, the lead's `{BASE}`, `{BRIEF_FILE}`, ...), with
  QUESTION not among them (`test_s3_generated_brief_holds_no_unfilled_upper_slot`).
- **S8, "the caller's tree".** For `gov retrieve` from a linked worktree the case runs with the working folder and
  `--root` both in the linked worktree (a planted store of its own), so either reading of "caller's tree" lands the
  line in the main worktree's `.gov-runtime/memory-use.jsonl`.
- **S8, refusals.** STORE_MISSING (a `--root` that does not exist), CONTINUATION_INVALID (a `--continue` that is no
  token) and UNRESOLVED_IDS (a question naming only `DEC-9999`, which exists nowhere; the command answers it with that
  stopping reason, not an error) each give one line whose `refusal` is the code. STORE_UNREADABLE is not planted: with
  the stand-in semantic route the library answers an unreadable store as FACET_UNAVAILABLE, not an error.
- **S8, types.** `ts` a timezone-aware ISO time at UTC offset 0; `role`, `ticket`, `session`, `stop_reason`,
  `refusal`, `store_commit` a string or null; `query_sha256` 16 lower-case hex digits; `items`, `characters` counts;
  `latency_ms` a non-negative number; `reranked` a boolean or null; `search_number` a count from 1 or null.
  `search_number` is checked on retrieves only (sessions of retrieves alone).
- **S9, retrieves counted.** Whether a refused retrieve also counts in `retrieves` is not stated: both readings are
  accepted (`per_role_day` and the command must agree with each other); `refused` and `briefs` are pinned. `since` is
  tested through the command (`--since 2026-11-16`); `read`'s `since` argument is not called (its type is not stated).
- **F1, an unreadable store.** The brief must still print (exit 0) with both commands in the section; which code or
  line it shows is not pinned (see S8's refusals).
- **F3.** Its verify names other suites (tests/unit/*, W2-128, W2-88, W2-152); `gov accept` runs only this folder, so
  the line maps to the one repository-state guard here: no file under `src/gov/context` or `tests/unit/context`
  differs from the base `067cd2946` (skipped in a clone without that commit). W2-128's and W2-152's revised cases are
  in their own folders (below).

## Kinds

Every case is acceptance kind but one: `test_f3_no_commit_of_this_ticket_touches_the_context_library_or_its_tests` (was `test_f3_gov_context_and_its_tests_are_untouched_since_the_base`) is
**repository-state** (it reads this repository's git history, not the code): it belongs to the record-reading set,
and it is meant to hold from this ticket's base through its landing.

## Map

| KPI line | Test (node id) | On the base `067cd2946` | Why |
|---|---|---|---|
| S1 | `test_w2_197_block.py::test_s1_every_role_brief_holds_the_library_bundle_as_its_memory_block` | red (6 rows: the six roles, the lead with `--run build`) | `gov brief` has no `--store` option (argparse exits 2, "unrecognized arguments") and no memory section |
| S1 | `test_w2_197_block.py::test_s1_long_first_line_is_cut_to_100_characters` | red | no `--store` option |
| S1 | `test_w2_197_block.py::test_s1_two_runs_give_the_same_bytes` | red | no `--store` option |
| S1 | `test_w2_197_block.py::test_s1_json_result_memory_matches_the_library_bundle` | red | no `--store` option; no `result.memory` |
| S1 | `test_w2_197_block.py::test_s1_query_falls_back_to_the_first_heading_then_the_id` | red (2 rows) | no `--store` option; no `result.memory.query` |
| S1 | `test_w2_197_block.py::test_s1_store_is_flag_then_gov_store_then_facts_then_root` | red | no `result.memory` (its first step passes no flag) |
| S1 | `test_w2_197_block.py::test_s1_facts_store_tree_is_filled_and_answers` | red | the brief has no section "What memory holds for this ticket" |
| S2 | `test_w2_197_block.py::test_s2_engineer_block_omits_its_ticket_acceptance_tests` | red | no `--store` option; no block |
| S2 | `test_w2_197_block.py::test_s2_test_designer_block_omits_the_implementation_paths` | red | no `--store` option; no block |
| S3 | `test_w2_197_text.py::test_s3_t0_ask_memory_first_names_retrieve_and_read_every_item` | red | the "Ask memory first" line splits by the sandbox and lacks "read every item of the bundle, ..." |
| S3 | `test_w2_197_text.py::test_s3_t0_holds_no_sandbox_split_for_retrieve` | red | brief.md says "No `gov retrieve` in the sandbox" |
| S3 | `test_w2_197_text.py::test_s3_t0_holds_the_memory_section_with_its_key` | red | brief.md has no memory section and no `{MEMORY_BLOCK}` |
| S3 | `test_w2_197_text.py::test_s3_generated_brief_holds_no_question` | red (6 rows) | no `--store` option (and every brief holds `{QUESTION}`) |
| S3 | `test_w2_197_text.py::test_s3_generated_brief_holds_no_unfilled_upper_slot` | red (6 rows) | no `--store` option (and every brief holds `{QUESTION}`, which keys.yaml still lists); see "Readings" |
| S4 | `test_w2_197_text.py::test_s4_role_template_holds_the_shared_memory_line` | red (7 rows) | no role template holds the shared memory line |
| S4 | `test_w2_197_text.py::test_s4_role_cto_launching_work_opens_every_subagent_prompt_with_the_memory_block` | red | role-cto.md's Launching work names no subagent memory block |
| S4 | `test_w2_197_text.py::test_s4_brief_commands_table_has_a_retrieve_row` | red (3 rows: engineer, product-spec, independent-auditor) | no `--store` option (and their templates name no `{CMD:retrieve}`) |
| S5 | `test_w2_197_text.py::test_s5_retrieval_skill_step_7_says_read_every_item` | red | step 7 lacks "read every item of the bundle, never head or cut it, and cite the ids you use" |
| S5 | `test_w2_197_text.py::test_s5_retrieval_skill_holds_the_shared_line_with_the_command` | red | the skill does not hold the shared line |
| S6 | `test_w2_197_text.py::test_s6_claude_template_copy_equals_its_kernel_template` | red (8 rows: brief and the seven role templates) | the copies equal the kernel's, but the kernel's lack the new memory text |
| S6 | `test_w2_197_text.py::test_s6_shipped_copy_equals_its_source` | red (3 rows) | the sources lack the new memory text |
| S6 | `test_w2_197_text.py::test_s6_retrieval_skill_copies_carry_the_new_step_7` | red (3 rows) | step 7 of each copy lacks "read every item ..." |
| S6 | `test_w2_197_text.py::test_s6_rulesync_subagent_equals_its_composition` | red (6 rows: each role with a source and a template) | each equals `compose(root, role)`, but lacks the shared memory line |
| S7 | `test_w2_197_text.py::test_s7_facts_retrieve_form_names_the_question_as_text` | red | facts.yaml's form is `gov retrieve --root {STORE_TREE} "{QUESTION}"` |
| S7 | `test_w2_197_text.py::test_s7_keys_drop_question_and_hold_memory_block` | red | keys.yaml holds QUESTION |
| S7 | `test_w2_197_text.py::test_s7_adopt_facts_writes_the_question_as_text` | red | `gov adopt --facts` writes `gov retrieve "{QUESTION}"` |
| S8 | `test_w2_197_log.py::test_s8_retrieve_appends_one_line_with_every_field` | red | the log holds no line after a retrieve |
| S8 | `test_w2_197_log.py::test_s8_role_ticket_and_session_come_from_the_environment` | red | no line |
| S8 | `test_w2_197_log.py::test_s8_search_number_counts_the_session_and_is_null_without_one` | red | no line |
| S8 | `test_w2_197_log.py::test_s8_a_refused_call_is_logged_with_its_code` | red (3 rows: STORE_MISSING, CONTINUATION_INVALID, UNRESOLVED_IDS) | no line |
| S8 | `test_w2_197_log.py::test_s8_brief_appends_one_line_for_its_retrieval` | red | no `--store` option; no line |
| S8 | `test_w2_197_log.py::test_s8_without_the_variable_the_line_lands_in_the_main_worktree` | red | no line in the main worktree's `.gov-runtime/memory-use.jsonl` |
| S9 | `test_w2_197_log.py::test_s9_read_returns_the_records_and_skips_the_malformed_line` | red | no module `gov.memory_use` (ImportError) |
| S9 | `test_w2_197_log.py::test_s9_read_by_root_finds_the_default_log` | red | no module `gov.memory_use` |
| S9 | `test_w2_197_log.py::test_s9_per_role_day_counts_retrieves_briefs_and_refusals` | red | no module `gov.memory_use` |
| S9 | `test_w2_197_log.py::test_s9_command_prints_one_line_per_day_and_role` | red | no command `gov memory-use` (argparse exits 2, "invalid choice") |
| S9 | `test_w2_197_log.py::test_s9_command_since_keeps_the_later_days` | red | no command `gov memory-use` |
| S9 | `test_w2_197_log.py::test_s9_command_json_is_an_envelope` | red | no command `gov memory-use` |
| F1 | `test_w2_197_block.py::test_f1_missing_store_prints_the_brief_with_the_not_reached_line` | red | no `--store` option (exit 2, no brief) |
| F1 | `test_w2_197_block.py::test_f1_missing_store_under_json_is_ok_with_the_refusal_named` | red | no `--store` option |
| F1 | `test_w2_197_block.py::test_f1_unreadable_store_still_prints_the_brief` | red | no `--store` option |
| F1 | `test_w2_197_block.py::test_f1_a_ticket_not_ready_is_still_refused` | red | no `--store` option: argparse's usage error, not BRIEF_NOT_READY |
| F2 | `test_w2_197_log.py::test_f2_retrieve_output_is_the_same_with_an_unwritable_log` | red (2 rows: a folder, a read-only file) | the writable log got no line (no writer to fail) |
| F2 | `test_w2_197_log.py::test_f2_brief_output_is_the_same_with_an_unwritable_log` | red (2 rows) | no `--store` option; no line |
| F2 | `test_w2_197_log.py::test_f2_append_never_raises` | red | no module `gov.memory_use` |
| F3 | `test_w2_197_text.py::test_f3_no_commit_of_this_ticket_touches_the_context_library_or_its_tests` | green (guard, repository-state) | no commit with `Task: DAEO-3d3o` touches `src/gov/context` or `tests/unit/context` (rewritten for DEC-1214 M1, W2-200) |

Red on the base: 89 of 90 cases, each for the reason above; green: 1 (F3's guard).

## Cases revised in other folders (same commit series; `Task: DAEO-3d3o`)

- `tests/acceptance/W2-128/test_w2_128_rows.py`: row 6, renamed `..._and_memory_first`: it required brief.md to say
  no gov retrieve in the sandbox; it now requires the opposite (no unit denies or splits retrieve by the sandbox, a
  unit holds "Ask memory first" with the retrieve command). Red on the base, and so is W2-152's S10 case, which runs
  `gov accept W2-128`. W2-128's README says so.
- `tests/acceptance/W2-152/`: every run is hermetic (`child_env` sets `GOV_STORE` to a folder that does not exist and
  `GOV_MEMORY_LOG` to the case's scratch folder); F3's spy and process cases allow exactly the store's folder (reads,
  and a git naming it), the log's folder (open, make, write) and Python's one `tempfile` probe file, and nothing else.
  Green on the base. W2-152's README says so.

## Checked against a stand-in

Before the commit the designer ran the S1, S2, S8, S9, F1 and F2 cases against a throwaway stand-in written from the
ticket's interface alone (in the designer's scratch, never committed): 38 of 38 passed, and W2-152's three revised F3
cases passed on it. Planted faults were caught by the cases meant for them: the brief not filtering by its own ticket
(S1 engineer row, S2 engineer), `append` raising on an unwritable log (all five F2 cases), and the brief's log line
written into the repository (W2-152's three F3 cases).

## Files

- `w2_197_support.py`: the ticket, the planted store, the brief's repository, the in-process command line, the
  library oracle, the block and log readers.
- `conftest.py`: the session's planted store, the stand-ins, the cleared variables and the case's own log.
- `test_w2_197_block.py` (S1, S2, F1), `test_w2_197_text.py` (S3-S7, F3), `test_w2_197_log.py` (S8, S9, F2).

## W2-200 revision (DEC-1214 M1)

W2-200 retires the context library and its unit tests (DEC-1214 M1), so F3's guard can no longer compare the two
folders with the base: `test_f3_no_commit_of_this_ticket_touches_the_context_library_or_its_tests` (was
`test_f3_gov_context_and_its_tests_are_untouched_since_the_base`) reads this ticket's history instead: no commit with
`Task: DAEO-3d3o` touches `src/gov/context` or `tests/unit/context` (`Rewrite-Reason:` in the case).
