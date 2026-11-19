# W2-200 acceptance tests: `gov context` retired; the close records decisions from the ticket's own sources

Ticket DAEO-r4xc (W2-200), profile FULL (DEC-1214 M1 (c)). Written by the independent test designer (MR-3) from the
ticket's nine success lines, two failure lines, its `## Interface` and non-goals, before any implementation, on the base
`0123c8b5f` (`w2/integrate`), reading only the integrated code. Every case is of the acceptance kind but S9's three
(repository-state: they read this tree's `tests/` and this README). Public interfaces only: the `gov` command line (exit
code, stdout, stderr, the `--json` envelope), the close record `docs/close/<ticket>/CL-<ticket>.md`, the repair ticket,
the facts file, `git`, the files of the code under test, and an import tried in a child process.

## How they run

    TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-200 -q -p no:cacheprovider

or `gov accept W2-200`. 57 cases, about 45 s (about 16 closes). No network, no model. Every `gov` runs as
`python3 -m gov.cli.main` (the runner's `PYTHONPATH`, else this worktree's `src/`) with a fixture `HOME` under the
test's `tmp_path` (its own `.gitconfig`), `TZ=UTC`, every `GIT_*`, `GOV_*` and `PYTEST_*` variable of the caller removed,
proxies and the embedder's address pointed at a dead local port.

## What is planted

- **The close fixture** (`w2_200_support.CloseProject`): the smallest project a strict `gov close` passes in (no
  `governance/project/close.yaml`, so the product default): a path map (`namespaces` with `**`, `close_workers: 2`,
  `decision_register: docs/DECISION_REGISTER.md` unless the case names none), the planted register, one declared check
  that passes (`command: "true"`), the kernel's `tk` and schemas; then the orchestrator's ticket commit, the test
  designer's acceptance test, the engineer's `src/example/feature.py` (each with W1-30's trailers), `gov checkpoint`,
  and `gov rebuild` before the close (the store gate, `STORE_STALE`, is unchanged by this ticket). A stand-in
  `openspec` that validates is first on `PATH`: the strict close's `gov check` runs the built-in `openspec-validate`,
  RED where `openspec` is absent; no case measures it. The worlds of S3 to S7 and F1 are built and closed once per session
  (`conftest.py`).
- **The register's ids.** The ticket's verify names DEC-10, DEC-11, DEC-12 and DEC-99, but the register's grammar
  (W2-03, `gov.store.loader`) holds only `DEC-` and three digits or more: `### DEC-10 — …` is no entry. The cases use
  DEC-110, DEC-111, DEC-112 (and DEC-1013, to tell sorting by number from sorting as text) for the ticket's DEC-10,
  -11 and -12: the same classes, in the grammar. S6 as amended names DEC-999, DEC-998 and DEC-150, which the grammar
  holds: the cases use them as written (and DEC-199 in the KPI-only world, unchanged since the first commit).
- **S3's ticket**: `sources: [DEC-1013, DEC-110, CAP-1, W2-9, docs/notes/plain.md, EMERGENCY-2 5.5]`,
  `decisions: [DEC-111, DEC-110]`, KPI lines citing `[DEC-112, DEC-111]` and `[DEC-112]`, and the look-alikes
  `PREDEC-141` and `DEC-1400x` (no whole-word id); the register holds the four and DEC-150 (cited nowhere). A clone of the
  repository at the same commit is closed too.
- **S4**: DEC-130's span is over 1,200,000 characters; the ticket's own text about 300,000; a second project with
  `budgets: {close_context_tokens: "abc"}` in `governance/project/facts.yaml`.
- **S5**: one cited decision in each state: DEC-120 stands; DEC-121 `SUPERSEDED` by its status word, DEC-122 by
  DEC-127's `**Supersedes:**` (its own status ACCEPTED), DEC-123 `SUPERSEDED by DEC-128`; DEC-124 `RETIRED`, DEC-125
  `REJECTED`; DEC-126 tagged `· done`.
- **S6** (as amended at the land): DEC-999 in `sources`, DEC-997 in `decisions` and DEC-998 in a KPI line, held by no
  register, no archive named; DEC-199 only in a KPI line; a path map naming no register (a register file at the usual
  path, unnamed, holding the three cited ids); a ticket with `sources: []`.
- **S6's archive**: the path map names `decision_register_archive: docs/archive/DECISION_REGISTER-2026-11-01.md` beside
  the register. The register holds DEC-110. The archive holds an older wording of DEC-110 (a kept entry is in both
  files), DEC-150 (status line ACCEPTED), DEC-151 (its own status line SUPERSEDED) and DEC-152 (a heading and its text,
  no status line). The ticket cites DEC-110, DEC-150 and DEC-151 from `sources`, DEC-152 from a success line and DEC-996
  (in neither file) from a failure line.
- **S7**: a failing acceptance test, `gov close --disposition repair`.
- **S1, F2's `gov check`**: a project holding this tree's kernel check declarations (`template/governance/kernel/checks/`
  copied whole, as an adopted project holds its kernel).
- **S8, F2's adopt and brief**: a folder with the kernel's templates and one READY ticket; `gov adopt --facts`; for the
  brief, the commands adopt leaves `{UNSET_<NAME>}` given a form (as the project's CTO fills them), every other entry as
  adopt wrote it; `gov brief lead <ticket> --run build` (the lead's brief needs its run kind).
- **F2's import sentinel**: a `sitecustomize.py` first on `PYTHONPATH` logs every import of `gov.context` (or a module
  under it) in the command's process and in every Python child that inherits the environment.

## The map

| KPI line | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_200_s1_retired.py::test_s1_the_context_command_is_an_invalid_choice`, `test_w2_200_s1_retired.py::test_s1_gov_help_lists_no_context_command`, `test_w2_200_s1_retired.py::test_s1_the_library_folder_is_gone_and_its_import_fails`, `test_w2_200_s1_retired.py::test_s1_the_kernel_holds_no_context_reproducibility_check`, `test_w2_200_s1_retired.py::test_s1_gov_check_names_no_context_reproducibility_family`, `test_w2_200_s1_retired.py::test_s1_the_token_counter_lives_in_gov_util_tokens_and_the_helpers_import_without_gov_context`, `test_w2_200_s1_retired.py::test_s1_no_module_of_the_code_imports_gov_context` | the command answers (exit 0, not 2), `gov --help` lists `context`, `src/gov/context/` exists and imports, the kernel holds the check, `gov check` names `context reproducibility`, `gov.util.tokens` does not exist, five modules import `gov.context` |
| S2 | `test_w2_200_s2_in_force.py::test_s2_json_result_is_the_digest_of_the_planted_register`, `test_w2_200_s2_in_force.py::test_s2_text_form_gives_one_line_an_entry_then_the_left_out_and_the_register`, `test_w2_200_s2_in_force.py::test_s2_an_uncommitted_edit_of_the_register_changes_neither_form`, `test_w2_200_s2_in_force.py::test_s2_a_repository_with_no_register_exits_0_with_empty_lines` | `gov decisions in-force` does not exist: exit 2, "invalid choice: 'in-force'" |
| S3 | `test_w2_200_s3_decisions_recorded.py::test_s3_the_close_passes_and_records_each_cited_decision_once_sorted_by_number`, `test_w2_200_s3_decisions_recorded.py::test_s3_inputs_hold_the_ticket_then_each_applied_decision_with_the_hash_of_its_span`, `test_w2_200_s3_decisions_recorded.py::test_s3_ids_of_other_forms_are_not_decisions_and_are_left_alone`, `test_w2_200_s3_decisions_recorded.py::test_s3_the_record_has_no_packet_hash`, `test_w2_200_s3_decisions_recorded.py::test_s3_the_same_ticket_at_the_same_commit_gives_the_same_lists_and_hashes` | the close is refused `CONTEXT_FAILED` alone ("mandatory input 'CAP-1' not found in the store"): every other gate passes |
| S4 | `test_w2_200_s4_no_ceiling.py::test_s4_a_decision_over_a_million_characters_and_a_long_ticket_close_and_are_recorded`, `test_w2_200_s4_no_ceiling.py::test_s4_an_invalid_close_context_tokens_setting_is_ignored`, `test_w2_200_s4_no_ceiling.py::test_s4_no_close_output_names_a_retired_code`, `test_w2_200_s4_no_ceiling.py::test_s4_the_code_names_no_ceiling_code_and_no_setting` | `CONTEXT_FAILED` alone: `CONTEXT_OVER_CEILING` (375,175 tokens against 6,000) and `CONTEXT_SETTING_INVALID` ('abc'); `src/` names the four words on 14 lines |
| S5 | `test_w2_200_s5_not_standing.py::test_s5_the_close_passes_and_applies_the_standing_and_the_done_tagged`, `test_w2_200_s5_not_standing.py::test_s5_the_others_are_listed_not_standing_with_their_states_sorted_by_number`, `test_w2_200_s5_not_standing.py::test_s5_no_decision_is_both_applied_and_not_standing` | `CONTEXT_FAILED` alone: "mandatory input 'DEC-121' is SUPERSEDED" |
| S6 | `test_w2_200_s6_not_found.py::test_s6_an_id_no_register_holds_in_sources_decisions_or_a_kpi_line_is_unresolved_and_the_close_goes_on`, `test_w2_200_s6_not_found.py::test_s6_the_close_of_a_ticket_citing_an_unknown_id_is_whole_and_no_output_names_the_refusal`, `test_w2_200_s6_not_found.py::test_s6_an_id_only_in_a_kpi_line_and_not_in_the_register_is_unresolved_and_the_close_passes`, `test_w2_200_s6_not_found.py::test_s6_a_decision_only_the_archived_register_holds_is_not_standing_as_archived_and_never_applied`, `test_w2_200_s6_not_found.py::test_s6_an_archived_decision_is_archived_whatever_its_own_status_line_and_wherever_it_is_cited`, `test_w2_200_s6_not_found.py::test_s6_beside_an_archive_the_register_s_entry_is_applied_and_an_id_in_neither_is_unresolved`, `test_w2_200_s6_not_found.py::test_s6_where_the_path_map_names_no_register_every_cited_id_is_unresolved`, `test_w2_200_s6_not_found.py::test_s6_a_ticket_citing_no_decision_closes_with_empty_lists` | on the base every close is refused `CONTEXT_FAILED` (the KPI-only id closes with no `decisions_unresolved`). At the land before the amendment's change (`6a7918fa7`): the first two are red, the close refused `DECISION_NOT_FOUND` (exit 1, "names DEC-997, DEC-999 in its sources or decisions", nothing closed or recorded); the other six are green (the KPI-only id, the three archive cases since the fix `f59534941`, no register, no citation) |
| S7 | `test_w2_200_s7_refusal_path.py::test_s7_the_refusal_keeps_its_code_and_class`, `test_w2_200_s7_refusal_path.py::test_s7_the_repair_ticket_has_the_fields_of_before_less_context_hash`, `test_w2_200_s7_refusal_path.py::test_s7_no_line_of_the_repair_ticket_speaks_of_a_context` | the repair ticket holds `context_hash: <64 digits>`; the first case is **green on the base by design** (a guard: `CHECK_FAILED`, exit 3, the class, no `CONTEXT_FAILED`) |
| S8 | `test_w2_200_s8_adopt_facts.py::test_s8_the_facts_file_holds_no_context_command_and_no_gov_context_text`, `test_w2_200_s8_adopt_facts.py::test_s8_the_context_ceiling_step_stays_off_with_a_line_naming_no_command`, `test_w2_200_s8_adopt_facts.py::test_s8_gov_brief_lead_on_the_adopted_facts_leaves_no_placeholder` | `commands.context` is written; `steps.context_ceiling.on` is true with `{CMD:context_ceiling}`; the brief case is **green on the base by design** (a guard: the brief never carries the step's line) |
| S9 | `test_w2_200_s9_tests_retired.py::test_s9_no_test_file_outside_w2_200_matches_a_retired_pattern`, `test_w2_200_s9_tests_retired.py::test_s9_every_retired_file_listed_is_deleted`, `test_w2_200_s9_tests_retired.py::test_s9_every_rewritten_case_listed_carries_its_rewrite_reason` | on the base: about 75 test files match the four patterns, the retired files exist, the rewritten cases carry no reason; green once this designer's retirements are in (they are in this commit) |
| F1 | `test_w2_200_f1_never_applied.py::test_f1_a_decision_that_no_longer_stands_is_never_applied_nor_hashed`, `test_w2_200_f1_never_applied.py::test_f1_an_id_neither_register_holds_is_never_applied_nor_hashed`, `test_w2_200_f1_never_applied.py::test_f1_an_archived_decision_is_never_applied_nor_hashed` | on the base the S5 and no-register closes are refused (`CONTEXT_FAILED`), so there is no record to read. At the land before the amendment's change: the second is red (the world citing DEC-999 and DEC-997 is refused `DECISION_NOT_FOUND`, so it has no record); the first and the third are green |
| F2 | `test_w2_200_f2_no_dangling_consumer.py::test_f2_the_command_never_imports_gov_context_nor_names_gov_context`, `test_w2_200_f2_no_dangling_consumer.py::test_f2_the_other_close_gates_judge_as_before` | `gov --help`, `gov check` (through `gov.adapters.portability` and the skill validator) and `gov close` import `gov.context`; `gov adopt --facts`, `gov brief lead` and the four gate cases (`TRAILER_MISSING` 3, `CHECKPOINT_MISSING` 3, `STORE_STALE` 1, `CONTAINMENT_FINDING` 3) are **green on the base by design** (guards) |

Count: 46 functions, 57 cases (S1 8, S2 5, S3 5, S4 4, S5 3, S6 8, S7 3, S8 3, S9 6, F1 3, F2 9).

## Red result on the base (`0123c8b5f` plus this commit's tests)

Run before this commit's retirements: 47 failed, 8 passed in 43 s, no error. The eight green are the guards named
above (S7's first case, S8's brief case, F2's adopt and brief cases and its four gate cases). Every close fixture was
refused by `CONTEXT_FAILED` alone (or, for the KPI-only id, closed without the new fields): the fixtures are proven up to
the retired behaviour. With this commit's retirements in (the second commit): 41 failed, 14 passed in 40 s: S9's six
cases are green as well, and every other case is red for the reason in the map.

## Revision at the land: S6 and F1 as the CTO amended them (2026-11-19, `6a7918fa7`)

Before: a `DEC-<n>` in a ticket's `sources` or `decisions` that the register does not hold refused the close
(`DECISION_NOT_FOUND`, nothing written). Amended: an id neither the register at `HEAD` nor the archived register holds
is listed in `decisions_unresolved` and the close goes on; an id only the archived register holds is listed in
`decisions_not_standing` as `{id, status: ARCHIVED}`; neither is ever applied or hashed (F1). The reason: the refusal was
a new blocking rule with no incident behind it (EMERGENCY-2 2.1; DEC-1214 M1 (c): the close records), and W2-203
archived most decisions the same night (EMERGENCY-2 11.3).

| Case | Was | Now |
|---|---|---|
| `test_w2_200_s6_not_found.py::test_s6_an_id_no_register_holds_in_sources_decisions_or_a_kpi_line_is_unresolved_and_the_close_goes_on` | `::test_s6_a_missing_id_in_sources_or_decisions_refuses_decision_not_found_naming_ticket_and_ids` | the close passes; `decisions_unresolved` holds the three ids, `decisions_applied` DEC-110 alone, `inputs` the ticket and DEC-110 |
| `test_w2_200_s6_not_found.py::test_s6_the_close_of_a_ticket_citing_an_unknown_id_is_whole_and_no_output_names_the_refusal` | `::test_s6_the_refusal_exits_as_a_close_refusal_of_its_kind`, `::test_s6_the_refusal_writes_nothing` | no output names `DECISION_NOT_FOUND`; exit 0, a close record, the ticket `closed`, no repair ticket |
| `test_w2_200_s6_not_found.py::test_s6_a_decision_only_the_archived_register_holds_is_not_standing_as_archived_and_never_applied` | new | DEC-150 is `{id: DEC-150, status: ARCHIVED}`, in no other list and not in `inputs` |
| `test_w2_200_s6_not_found.py::test_s6_an_archived_decision_is_archived_whatever_its_own_status_line_and_wherever_it_is_cited` | new | DEC-150, DEC-151 (its own status SUPERSEDED) and DEC-152 (no status line, cited from a KPI line) are ARCHIVED, sorted by number |
| `test_w2_200_s6_not_found.py::test_s6_beside_an_archive_the_register_s_entry_is_applied_and_an_id_in_neither_is_unresolved` | new | DEC-110 (in both files) is applied with the hash of the register's span; DEC-996 is unresolved |
| `test_w2_200_f1_never_applied.py::test_f1_an_id_neither_register_holds_is_never_applied_nor_hashed` | `::test_f1_an_id_the_register_does_not_hold_is_never_applied_nor_hashed` (two worlds) | four worlds: the unresolved one and the archive's DEC-996 as well |
| `test_w2_200_f1_never_applied.py::test_f1_an_archived_decision_is_never_applied_nor_hashed` | new | no archived id is applied or hashed |

Deleted with the refusal: `test_w2_200_f1_never_applied.py::test_f1_a_refused_close_leaves_no_record_no_checkpoint_and_no_state_change`
(F1 no longer speaks of a refusal). Unchanged: the KPI-only, no-register and no-citation cases of S6, and F1's first.
Outside this folder: W1-30's receipt case (the Rewritten list below), a lifted case (`--optin=lifted`): red before the
engineer's change for the same refusal. Its fixture is repaired with it: `add_ticket(..., sources=[...])` wrote a second
`sources` key beside the fixture's own, an unreadable frontmatter (`core-authority` RED, `CHECK_FAILED`), which the
refusal hid in this case and which kept
`test_w1_30_receipt.py::test_close_record_decisions_come_from_the_ticket_s_sources_with_their_span_hashes` (lifted, so
never run by `gov accept`) red on the landed code; both cases now replace the fixture's one source, and that case is
green.

Red on the tree at the land before the engineer's change (`6a7918fa7`, the implementation still refusing): 3 failed, 54
passed. Red: S6's first two cases and F1's second, each for the refusal `DECISION_NOT_FOUND` of the world citing DEC-999
and DEC-997. Green already: the three archive cases of S6 and F1's archive case (the CTO's fix `f59534941` made an
archived id not standing), and every unchanged case.

## The test designer's readings where the ticket is open

- **The ids.** DEC-10/11/12/99 are outside the register's grammar (above); the cases use three-digit ids of the same
  classes. Not a weakening: an id the grammar cannot hold could only ever be "unresolved".
- **The span's hash** is accepted as the sha256 of the span's UTF-8 bytes with or without the line break that ends it
  (`span_hashes`): both are "the span"; two decisions never share one hash.
- **`decisions_not_standing`'s status** is `SUPERSEDED` for all three forms of supersession, including DEC-122, whose
  own status word is ACCEPTED and which a successor's `**Supersedes:**` supersedes ("recorded as such"). Returned as a
  package.
- **S6's two readings of the refusal** ("exit as other close refusals of that kind", "git status and .governance as they
  were") are withdrawn with the refusal (the revision at the land, above).
- **The archive's entries** are its `### DEC-<n>` headings (W2-203): an archived id is ARCHIVED whatever its own status
  line says and with none at all (W2-203 asks no status line of history). An id both files hold (every kept entry)
  is "only the archive's" by no reading: it stands by the register and is hashed by the register's span.
- **`decisions_unresolved`'s order** is not stated by the ticket: the cases compare it sorted.
- **S8's brief**: on the adopted defaults `gov brief lead <ticket>` needs `--run` (`BRIEF_RUN_MISSING`) and is refused
  for eight `PLACEHOLDER_LEFT UNSET_*` commands by W2-174's design; the case fills those commands first and then holds
  "no `PLACEHOLDER_LEFT`". The brief never carries `{STEP:context_ceiling}`'s line (the lead's run section stops before
  it), so this case is a guard.
- **S1's `gov check`**: `gov check` names every family of its own list whether or not a check is declared, so
  "names no `context-reproducibility` family" needs the family out of that list too (sixteen families, not CAP-38.b's
  seventeen). W1-26's family cases are rewritten to sixteen (below).
- **The strict close.** The worlds run the strict close (the product default). The lead decided that every path that
  writes a close record (plain, scoped/selected, batch) records the decision lists; no case here covers the scoped or
  the batch path (each would be a slow run of its own): that is said in the designer's return, not tested.
- **The ticket's own input** is the sha256 of the ticket file as the commit the close measured holds it (HEAD before the
  close, read with `git show`): `tk close` rewrites the working file afterwards (`status: closed`). Revised after the
  engineer's measurement (the two cases first hashed the working file after the close).
- **S9's walk** reads every `*.py` under `tests/` but this folder and the Retired list, line by line, for the four
  patterns (`PATTERNS` in the S9 file: an import or mention of `gov.context`; the command line `gov context` or a call
  that hands `"context"` to `gov`; `context-reproducibility` in any spelling; `close_context_tokens`). One exemption: a
  line that itself names "DEC-1214 M1" states the retirement (W2-54's decided removal of the declaration, W2-108's history
  read of its path, the wall template's deny rule kept in `governance/`), so it does not name the retired thing as live.

## Retired

Each file deleted by this ticket's test designer (S9), the KPI line or ticket it served, and why.

| Path | Served | Why |
|---|---|---|
| `tests/acceptance/W1-24/README.md` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/conftest.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_authority.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_blocked.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_brief.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_command.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_family_check.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_mandatory.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_packet.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_pressure.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_standing_sources.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/test_w1_24_supplementary.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-24/w1_24_support.py` | W1-24 (DAEO-wk2v): the context command, its packet, `--brief`, the family check | the command, its library and its check are retired (S1) |
| `tests/acceptance/W1-30/test_w1_30_context_failures.py` | W1-30 S5, S6 (A4, DEC-454): a context that cannot be built refuses the close | no packet can fail (S4, S7) |
| `tests/acceptance/W1-30/test_w1_30_r15_context_tickets.py` | W1-30 rounds 15, 16 (DEC-612, DEC-628): what the context check measures | the check is retired (S1) |
| `tests/acceptance/W1-30/test_w1_30_r16_context_own_tickets.py` | W1-30 rounds 15, 16 (DEC-612, DEC-628): what the context check measures | the check is retired (S1) |
| `tests/acceptance/W1-41/test_w1_41_external_follow_up.py` | W1-41 success 9 (CAP-15.c): external references in the packet | the packet is retired (S1) |
| `tests/acceptance/W1-41/test_w1_41_external_references.py` | W1-41 success 9 (CAP-15.c): external references in the packet | the packet is retired (S1) |
| `tests/acceptance/W2-04/README.md` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/conftest.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_batches.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_ceiling.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_code_under_test.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_context_check.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_decision_hash.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_emptied.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_one_read_and_notes.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_query.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_refusal.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_reproducible.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/test_w2_04_unreadable.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-04/w2_04_support.py` | W2-04 (DAEO-u4oz): the packet bounded and reproducible, its ceiling, the context check | retired with the library and its check; the close's decision record replaces the packet (S1, S3 to S6) |
| `tests/acceptance/W2-183/README.md` | W2-183 (DAEO-href) S1 to S3, F1: the close's packet at `budgets.close_context_tokens`; the supplementary cap | no ceiling anywhere (S4); the packet is retired (S1) |
| `tests/acceptance/W2-183/conftest.py` | W2-183 (DAEO-href) S1 to S3, F1: the close's packet at `budgets.close_context_tokens`; the supplementary cap | no ceiling anywhere (S4); the packet is retired (S1) |
| `tests/acceptance/W2-183/test_w2_183_f1_invalid_setting.py` | W2-183 (DAEO-href) S1 to S3, F1: the close's packet at `budgets.close_context_tokens`; the supplementary cap | no ceiling anywhere (S4); the packet is retired (S1) |
| `tests/acceptance/W2-183/test_w2_183_s1_close_setting.py` | W2-183 (DAEO-href) S1 to S3, F1: the close's packet at `budgets.close_context_tokens`; the supplementary cap | no ceiling anywhere (S4); the packet is retired (S1) |
| `tests/acceptance/W2-183/test_w2_183_s2_supplementary_cap.py` | W2-183 (DAEO-href) S1 to S3, F1: the close's packet at `budgets.close_context_tokens`; the supplementary cap | no ceiling anywhere (S4); the packet is retired (S1) |
| `tests/acceptance/W2-183/test_w2_183_s3_unchanged.py` | W2-183 (DAEO-href) S1 to S3, F1: the close's packet at `budgets.close_context_tokens`; the supplementary cap | no ceiling anywhere (S4); the packet is retired (S1) |
| `tests/acceptance/W2-183/w2_183_support.py` | W2-183 (DAEO-href) S1 to S3, F1: the close's packet at `budgets.close_context_tokens`; the supplementary cap | no ceiling anywhere (S4); the packet is retired (S1) |
| `tests/acceptance/W2-54/test_w2_54_dropped_order.py` | W2-54 S1, F1: the packet's order and the check over it | the packet and its check are retired (S1) |
| `tests/unit/close/test_context.py` | W1-30, W2-07: the close's `_build_context` and `CONTEXT_FAILED` | the close builds no packet (S3 to S7) |
| `tests/unit/close/test_w2_183_context_setting.py` | W2-183 S1, F1 (the close's setting) | no ceiling anywhere (S4) |
| `tests/unit/context/test_all_external.py` | unit tests of `gov.context` (W1-24, W2-04, W2-183, W1-41) | the library is retired (S1) |
| `tests/unit/context/test_bounded.py` | unit tests of `gov.context` (W1-24, W2-04, W2-183, W1-41) | the library is retired (S1) |
| `tests/unit/context/test_context_check_selection.py` | unit tests of `gov.context` (W1-24, W2-04, W2-183, W1-41) | the library is retired (S1) |
| `tests/unit/context/test_context_internals.py` | unit tests of `gov.context` (W1-24, W2-04, W2-183, W1-41) | the library is retired (S1) |
| `tests/unit/context/test_dropped_order.py` | unit tests of `gov.context` (W1-24, W2-04, W2-183, W1-41) | the library is retired (S1) |
| `tests/unit/context/test_external_references.py` | unit tests of `gov.context` (W1-24, W2-04, W2-183, W1-41) | the library is retired (S1) |
| `tests/unit/context/test_w2_183_close_budget.py` | unit tests of `gov.context` (W1-24, W2-04, W2-183, W1-41) | the library is retired (S1) |

## Rewritten

Each case rewritten for DEC-1214 M1; its docstring carries the `Rewrite-Reason:` quoted here (cut at 330 characters).

| Case | Asserts now |
|---|---|
| `tests/acceptance/W1-26/test_w1_26_green_base.py::test_the_base_project_is_green_before_any_defect` | DEC-1214 M1 (W2-200): the context family and its check are retired with the context command, so the check is no longer among those left out of the base and its family is no longer among those held not GREEN; every other assertion is unchanged. |
| `tests/acceptance/W1-26/test_w1_26_registry.py::test_all_families_named_in_result` | DEC-1214 M1 (W2-200): was ``test_all_17_families_named_in_result``; the context family is retired with its one check, so the list holds sixteen; what is asserted of each family is unchanged. |
| `tests/acceptance/W1-26/test_w1_26_registry.py::test_exactly_the_sixteen_families` | DEC-1214 M1 (W2-200): was ``test_exactly_17_families``; the context family is retired with its one check (the context command's), so the result names sixteen and none of them is the context family. |
| `tests/acceptance/W1-30/test_w1_30_disposition.py::test_valid_disposition_records_the_class_and_no_context_hash` | DEC-1214 M1 (W2-200 S7): was ``test_valid_disposition_builds_context_first``, which asked for the context packet's hash on the repair ticket; the context command is retired, so the repair ticket records the class and holds no ``context_hash`` and no 64-digit hash. |
| `tests/acceptance/W1-30/test_w1_30_r15_enforces.py::test_a_family_name_that_contains_the_key_no_longer_covers_it` | DEC-1214 M1 (W2-200): the second family is a planted name holding the key ("context budget"), since the kernel's own (the context family) is retired with its check; what is asserted is unchanged. |
| `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py::test_every_key_a_kernel_declaration_states_is_a_policy_key` | DEC-1214 M1 (W2-200): the kernel template holds nineteen declarations, not twenty: the context check is retired with the context command. |
| `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py::test_the_kernel_template_states_exactly_the_pairs_that_are_proved` | DEC-1214 M1 (W2-200): eight decided pairs; the context pair is gone with its retired check. |
| `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py::test_no_policy_key_that_is_not_informational_is_left_without_a_check` | DEC-1214 M1 (W2-200): the ``context`` key's one check is retired with the context command and no check replaces it (the ticket's non-goals), so it is owed by none, by that decision (``LEFT_BY_DECISION``); every other key that is not informational still needs a declaration that states it. |
| `tests/acceptance/W1-30/test_w1_30_r8_last_step.py::test_a_record_store_older_than_the_commit_being_closed_refuses_and_names_the_rebuild` | DEC-1214 M1 (W2-200): the case read the fixture through the retired context command (a context built before the owner's commit, and refused for the superseded base decision after the store was loaded again). Those two readings are deleted with the command; the owner's commit still makes the loaded store older than the commit bei… |
| `tests/acceptance/W1-30/test_w1_30_receipt.py::test_close_record_names_its_decisions_and_has_no_packet_hash` | DEC-1214 M1 (W2-200 S3): was ``test_close_record_has_packet_hash``; the close builds no context packet, so the receipt has no ``packet_hash`` and states its decisions in three lists. |
| `tests/acceptance/W1-30/test_w1_30_receipt.py::test_close_record_decisions_come_from_the_ticket_s_sources_with_their_span_hashes` | DEC-1214 M1 (W2-200 S3): was ``test_close_record_packet_hash_matches_context``, which compared the record's packet hash with the retired context command's; the receipt's decisions now come from the ticket's own sources, resolved in the register by id, each hashed by its span. |
| `tests/acceptance/W1-30/test_w1_30_receipt.py::test_unresolvable_source_is_recorded_unresolved_and_the_close_goes_on` | DEC-1214 M1 (W2-200 S6 and F1 as the CTO amended them at the land; EMERGENCY-2 2.1): was ``test_unresolvable_source_refuses_the_close``, which asked for the refusal ``DECISION_NOT_FOUND``; an id no register holds is now recorded in ``decisions_unresolved`` and the close goes on. |
| `tests/acceptance/W1-36/test_w1_36_audit_skill.py::test_the_skill_says_inputs_are_context_pack_and_repository` | DEC-1214 M1 (W2-200): the alternative that named the retired context command is dropped; the skill's own words (a context pack or packet, and the repository) are asked as before. |
| `tests/acceptance/W2-108/test_w2_108_scope.py::test_w2_54_is_not_changed_by_this_ticket` | DEC-1214 M1 (W2-200): the context check's declaration is retired; it is still a path this ticket's commits must not have touched, and git reads its history whether or not it exists now. Unchanged otherwise. |
| `tests/acceptance/W2-197/test_w2_197_text.py::test_f3_no_commit_of_this_ticket_touches_the_context_library_or_its_tests` | DEC-1214 M1 (W2-200): was ``test_f3_gov_context_and_its_tests_are_untouched_since_the_base``, which compared the two folders with the base; W2-200 retires them, so the guard reads this ticket's own history instead: no commit with ``Task: DAEO-3d3o`` touches ``src/gov/context`` or ``tests/unit/context``. Skipped where the base is… |
| `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_retrieve_exits_alike_at_a_path_with_a_space` | DEC-1214 M1 (W2-200): was ``test_s6_retrieve_and_context_exit_alike_at_a_path_with_a_space``; the context command is retired, so its dry run is no longer one of the invocations; retrieve's is asserted as before. |
| `tests/acceptance/W2-54/test_w2_54_cpu_embedder.py::test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner` | DEC-1214 M1 (W2-200): the context command is retired, so the two context reads kept as a guard ("they send neither embedder a text") are deleted; every other step and assertion is unchanged. |
| `tests/acceptance/W2-54/test_w2_54_green_here.py::test_outside_a_close_the_fixture_runs_gov_check_in_this_worktree` | DEC-1214 M1 (W2-200): the route's answer is read for the planted core-graph check, no longer the retired context check; what it asserts of the route is unchanged. |
| `tests/acceptance/W2-54/test_w2_54_green_here.py::test_a_check_result_that_is_missing_or_broken_is_never_read_as_green` | DEC-1214 M1 (W2-200): the planted texts name the core-graph check and another command (``retrieve``) in place of the retired context check and command; the forms refused are unchanged. |
| `tests/acceptance/W2-54/test_w2_54_green_here.py::test_a_red_or_missing_check_in_the_close_s_result_still_fails_the_cases` | DEC-1214 M1 (W2-200): the context check's case is deleted with the check, so the routes are proved on core-schema's case alone; the forms (RED, missing, advisory) are unchanged. |
| `tests/acceptance/W2-54/test_w2_54_query_cache.py::test_gov_retrieve_writes_at_most_one_derived_file_under_the_runtime_folder` | DEC-1214 M1 (W2-200): was ``test_gov_retrieve_and_gov_context_write_at_most_one_derived_file_under_ the_runtime_folder``; the context command is retired, so its two reads (two tickets) are two ``gov retrieve`` of those tickets' questions. What is asserted of the tree is unchanged. |
| `tests/acceptance/W2-54/test_w2_54_query_cache.py::test_in_a_project_without_an_index_a_read_creates_nothing` | DEC-1214 M1 (W2-200): the context command is retired, so its read is a second ``gov retrieve``, of the ticket's question; what is asserted of the tree is unchanged. |
| `tests/acceptance/W2-54/test_w2_54_query_cache.py::test_one_ticket_s_question_gets_one_answer_whatever_the_cache_s_state` | DEC-1214 M1 (W2-200): was ``test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state``. The context command is retired, so the packet part is deleted (the reference packet, each state's packet and its "sends the embedder nothing" guard); the case now asserts that the ticket's question, through ``gov retrieve``, gets the o… |
| `tests/acceptance/W2-54/test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened` | DEC-1214 M1 (W2-200): the context check is retired with the context command, so its declaration is removed by decision (``DECIDED_REMOVALS``): the folder holds the base's declarations less that one, and no other is removed, added or changed. The exception that let the context check's one added line through is gone with it. |
| `tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_two_checks_of_this_ticket_stay_hard_block` | DEC-1214 M1 (W2-200): the other of the two, the context check, is retired with the context command; its row is deleted and core-schema's stays. |
| `tests/acceptance/W2-55/test_w2_55_in_force.py::test_one_line_per_entry_in_force_in_register_order_beginning_with_its_id` | DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context command's retirement; the assertions are unchanged. |
| `tests/acceptance/W2-55/test_w2_55_in_force.py::test_superseded_and_done_entries_are_left_out_with_their_count` | DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context command's retirement; the assertions are unchanged. |
| `tests/acceptance/W2-55/test_w2_55_in_force.py::test_a_changed_entrys_line_names_what_changed_it` | DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context command's retirement; the assertions are unchanged. |
| `tests/acceptance/W2-55/test_w2_55_in_force.py::test_the_digest_is_generated_from_the_register_not_a_hand_made_file` | DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context command's retirement; the assertions are unchanged. |
| `tests/acceptance/W2-55/test_w2_55_in_force.py::test_no_register_named_gives_an_empty_digest` | DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context command's retirement; the assertions are unchanged. |
| `tests/acceptance/W2-55/test_w2_55_in_force.py::test_a_named_register_that_cannot_be_read_refuses` | DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context command's retirement; the assertions are unchanged. |
| `tests/acceptance/W2-55/test_w2_55_in_force.py::test_decisions_with_no_action_is_refused_by_the_parser` | DEC-1214 M1 (W2-200): was ``test_context_with_neither_a_ticket_nor_in_force_is_refused_by_the_ parser``; the digest's command is now ``gov decisions in-force``, so the parser's refusal is asked of ``gov decisions`` with no action (exit 2), as it was of the retired command with neither a ticket nor the flag. |
| `tests/unit/check/test_check.py::test_families_count` | DEC-1214 M1 (W2-200): sixteen families, not seventeen: the context family is retired with its one check (the context command's), and no family takes its place. |
| `tests/unit/check/test_check.py::test_families_unique` | DEC-1214 M1 (W2-200): the sixteen families, each once. |
| `tests/unit/check/test_check.py::test_run_checks_returns_families_and_checks` | DEC-1214 M1 (W2-200): the result names the sixteen families (the context family is retired). |
| `tests/unit/check/test_check.py::test_a_policy_key_is_covered_by_enforces_and_never_by_a_family_name` | DEC-1214 M1 (W2-200): the family name that holds the key is a planted one ("context budget"), since the kernel's own (the context family) is retired; what is asserted is unchanged. |
| `tests/unit/cli/test_cli.py::test_the_read_commands_are_those_of_cap_27` | DEC-1214 M1 (W2-200): CAP-27's read commands less the context command, which the owner retired with its library and its check. |
| `tests/unit/close/test_every_finding.py::test_without_a_class_the_findings_await_it_and_no_context_hash_is_recorded` | DEC-1214 M1 (W2-200 S7): the refusal is given no packet (the context command is retired); the findings still await their class and no context hash is recorded. |
| `tests/unit/close/test_every_finding.py::test_with_a_class_the_repair_ticket_records_it_and_no_context_hash` | DEC-1214 M1 (W2-200 S7): was ``test_with_a_class_the_repair_ticket_has_the_context_hash``; the context command is retired, so the repair ticket records the class and no ``context_hash``, and no line of it speaks of a context. |
| `tests/unit/close/test_repair_ticket.py::test_the_repair_ticket_has_the_parent_the_dependency_the_findings_and_the_class` | DEC-1214 M1 (W2-200 S7): the repair ticket is opened with no context hash (the context command is retired): it records the class and holds no ``context_hash``. |
| `tests/unit/orchestration/test_dispatcher.py::test_a_heavy_step_outside_a_slot_is_named_and_holds_starts` | DEC-1214 M1 (W2-200): the heavy step is the retrieval check (one of the dispatcher's heavy modules), no longer the context check, retired with the context command; what is asserted is unchanged. |
| `tests/unit/orchestration/test_dispatcher.py::test_a_heavy_step_inside_a_slot_is_not_a_finding` | DEC-1214 M1 (W2-200): the heavy step is the retrieval check (one of the dispatcher's heavy modules), no longer the context check, retired with the context command; what is asserted is unchanged. |
| `tests/unit/orchestration/test_dispatcher.py::test_nightly_slot_a_heavy_step_elsewhere_still_holds_starts_while_the_nightly_runs` | DEC-1214 M1 (W2-200): the heavy step is the retrieval check (one of the dispatcher's heavy modules), no longer the context check, retired with the context command; what is asserted is unchanged. |

## Removed cases

Functions deleted from files that survive, and parametrised rows gone with their data (nothing replaces them, or W2-200
holds what replaces them).

| Case | Why |
|---|---|
| `tests/acceptance/W1-07/test_w1_07_registry.py::test_each_wave_1_operation_is_a_gov_command[context]` and W1-07's `context --dry-run` read rows | `RESERVED_COMMANDS` holds eleven, `READ_COMMANDS` no context row |
| `tests/acceptance/W1-26/test_w1_26_registry.py`'s `NOT_YET_REGISTERED` row of the context family | sixteen families |
| `tests/acceptance/W1-30/test_w1_30_receipt.py::test_close_refuses_when_context_cannot_be_built`, `::test_no_fallback_hash_when_context_fails`, `::test_context_failure_non_cycle_refuses_close` | no packet; a decision that no longer stands never refuses (S5) |
| `tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure` | no context can fail (S7) |
| `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py::test_a_ticket_whose_mandatory_input_is_missing_turns_the_context_check_red` and the `context:context-reproducibility` row of `::test_the_kernel_declaration_of_the_check_states_the_key_it_is_proved_to_enforce` | the check is retired |
| `tests/acceptance/W2-13/test_w2_13_role_separation.py::test_engineer_context_supplementary_holds_none_of_its_own_tickets_acceptance_tests` | the packet's supplementary block is retired |
| `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here`; `test_w2_54_time_limit.py`'s five S8 cases; `test_w2_54_query_vector.py::test_gov_context_twice_for_each_ticket_with_others_between_gives_one_packet`, `::test_the_context_check_is_green_over_several_tickets_with_an_embedder_whose_vectors_vary` | the check and the packet are retired (W2-54's README) |
| `tests/acceptance/W2-55/test_w2_55_left_out.py`: the five context-packet cases | the packet is retired; S5 holds the close's record |
| `tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_each_coupling_imports_cannot_see_is_declared[src/gov/context/command.py]` | the file is gone |
| `tests/acceptance/W2-108/test_w2_108_scope.py::test_the_context_checks_limit_is_not_raised`, `test_w2_108_unchanged.py::test_this_repositorys_context_packet_is_unchanged` | no declaration, no packet |
| `tests/acceptance/W2-200/test_w2_200_s6_not_found.py::test_s6_a_missing_id_in_sources_or_decisions_refuses_decision_not_found_naming_ticket_and_ids`, `::test_s6_the_refusal_exits_as_a_close_refusal_of_its_kind`, `::test_s6_the_refusal_writes_nothing`; `test_w2_200_f1_never_applied.py::test_f1_a_refused_close_leaves_no_record_no_checkpoint_and_no_state_change` | S6 and F1 as amended at the land: no refusal for a decision id; the unresolved and archive cases replace them |
| `tests/unit/close/test_every_finding.py::test_with_a_class_a_context_that_failed_is_a_finding_and_is_named_on_the_repair_ticket` and the `_build_context` rows of its gate cases | no context gate |
| `tests/unit/close/test_repair_ticket.py::test_a_context_that_failed_is_named_and_no_hash_is_recorded` | no context can fail |
| `tests/unit/retrieval/test_w2_13_role_filter.py::test_a_supplementary_block_whose_role_paths_cannot_be_read_is_empty_and_says_why`, `::test_gov_context_with_role_given_withholds_the_engineers_tests_and_names_it`, `::test_gov_context_command_passes_role_through_to_the_block`, `::test_a_packet_built_from_another_tickets_session_judges_the_packets_own_ticket_too` | the context command and its wrapper are retired; `supplementary.stack`'s cases stay |

## Support, lists and text only

- Support modules: `W1-07` (the reserved and read commands), `W1-26` (sixteen families), `W1-30` (`context_error`
  deleted; docstrings), `W1-30` round 16 (`CONTEXT_CHECK` deleted), `W1-31` (the counter's docstring), `W1-36` (the
  families), `W1-41` (the context section), `W2-13` (the context reader), `W2-54` (the packet's helpers, its hook, three
  fixtures), `W2-55` and `W2-108` (docstrings, a constant), `tests/unit/close/test_governance_checks.py` (its helper no
  longer patches `_build_context`), `tests/unit/close/test_every_finding.py` (`_refused` hands no packet).
- Lists: `tests/acceptance/serial-only.txt` (two deleted W2-54 cases), `tests/optin-lifted.txt` (W1-30's deleted
  files and cases; the renamed receipt case), `tests/optin-lifted-breadth.txt` (W1-24, W2-04, `tests/unit/context/`, the
  W1-41 files, W2-54's deleted file).
- Text only (no assertion changed): `W1-29/test_session_hooks.py` (two comments of the hook's KPI line),
  `W2-128/test_w2_128_rows.py` (a comment), `W2-66/test_w2_66_followed_couplings.py` (a docstring), the
  `DEC-1214 M1`-marked lines of `W2-149/w2_149_support.py` and `tests/unit/orchestration/test_w2_149_indep_launch.py`
  (the wall template's deny of the retired command, kept in `governance/`).
- READMEs revised: W1-07, W1-26, W1-30, W1-36, W1-41, W2-13, W2-23, W2-54, W2-55, W2-66, W2-108, W2-197 (each with a
  "W2-200 revision" section and its map rows taken to the surviving names).
