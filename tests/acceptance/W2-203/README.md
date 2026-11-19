# W2-203 acceptance tests: the old register archived and out of memory's index; the kept register in force

Ticket DAEO-r3gx (W2-203), profile FULL, class C3 (EMERGENCY-2 11.3, DEC-1214 G4 (a)). Written by the independent test
designer (MR-3) from the ticket's six success lines and four failure lines and the lead's interface text, before any
implementation, reading only the code at the ticket's base (`05ed38219` on `w2/integrate`, DEC-963) and the G4 lead's
draft builder (`e2/g4-g5:docs/emergency-2/audits/08-new-register.py`, not this ticket's implementation). Nothing of
this ticket's implementation was read.

KPI cells use positions in the ticket: `S<n>` is the n-th success line, `F<n>` the n-th failure line.

## How they run

    TMPDIR=$(mktemp -d) PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-203 -q -p no:cacheprovider

61 cases. The planted cases take about 5 s together, in process. The six clone cases take about 150 s together on a
quiet machine (the citations check 65 s, the traceability check 26 s, `gov doctor` 20 s, `gov links` 10 s, the lists
1 s, the clone's store 6 s): each runs the same child on two temporary clones, side by side. No model, no network, no
GPU, no vector; never the shared store, never a real worktree's `.gov-runtime/`. They need `git`, `PyYAML` and
`jsonschema`. `gov accept W2-203 --root <worktree>` reads the map below: 10 lines, none unmapped.

## What the cases do

- **The planted project** (`w2_203_support.plant`; once per session for the cases that only read it): a git
  repository whose path map names a register (`decision_register`), an archive (`decision_register_archive`) and the
  namespace `archive` (`docs/archive/**`, not embedded, not indexed). The archive holds seven entries; the kept
  register holds four of them verbatim (two of class `kept`, one of them with its class on the status line's second
  line, and two from DEC-1211 on). An id the archive alone holds (`DEC-101`) and an id no file holds (`DEC-9999`)
  are cited side by side in each place: a kept entry's `**Supersedes:**`, `**Changed by:**` and `**Under:**` labels,
  a ticket's `sources:`, a note's `decisions:` and `constrains:`, a test file's comment, and a commit's message and
  `Implements:` trailer. The first commit predates the archive file. Its keyword index and record store are built in
  place (`lexical.refresh`, `store.load`), the secret filter replaced, as W2-197's support builds its store.
- **The stand-ins** (`conftest.py`, as W2-197's): the semantic route answers with no hit, the file route is off, the
  reranker is the identity, the code index knows no symbol (so a start id of `gov closure` that is no record is
  `UNRESOLVED`, never `FACET_UNAVAILABLE`). `GOV_ROLE`, `GOV_TICKET`, `GOV_STORE`, `GOV_SESSION` are cleared.
- **The repository-state cases** (`record_reading`; names with `real`, and all of S1 and S2) read this tree's own
  archive, register, path map and schema, and the base's register by `git show 05ed38219:...`. Nothing is written.
- **The clone cases** (`base_clone`, `head_clone`, `moved`): two throwaway repositories in a temporary folder that
  borrow this repository's objects (`objects/info/alternates`), one holding the base commit, one HEAD; each holds no
  other ref. The same child runs on both, each with its clone's own `src`: `gov doctor --json`,
  `gov links --all --json`, `gov.check.citations.check`, `python -m gov.close.traceability`, and the ratchet lists.
  **They judge HEAD, the committed state:** commit the data move and the code before running them. The clone's own
  record store is built by `store.load` in the clone (never the shared store).
- **An entry's text** (S1, S2, S6, F1, F2) is read by one reader for every file (`w2_203_support.entries`): from the
  heading `### DEC-n` to the line before the next such heading, a `## ` heading or a `---` line, without the blank
  lines that end it, as the draft builder reads the register. An entry is **kept** when the first `**Class:**` of
  that text is `kept` (155 entries of the base, two of them with the class on the status line's second line) or its
  id is DEC-1211 or later (6): 161 entries.

## How the cases read what the interface leaves open

- **S1 "the rest of it":** every line of the base register is in the archive, under its first line, in order; lines
  added after the base (a later decision) are allowed.
- **S1 "as evaluation-sources has them":** the namespace `archive` has the same fields as `evaluation-sources` and the
  same `memory_class`, `sensitivity`, `permitted_roles` and `export_policy`; `retention`, `provenance` and
  `deletion_rebuild` are free text.
- **S2 "short head":** at most 40 lines before the first entry, opening with a title, naming the archive's path and
  audit 8 (`audit 8` or `08-register`).
- **S2 doctor:** each part's `status` equals the base's; `path_map.unclassified_count` is 0; no `moved_references`
  item appears that the base lacked (the archive's own text names old paths: it is historical).
- **S3/F4 vectors:** no vector is built in these cases (no model). The archive's namespace is `not embedded` and the
  vectors are built from the keyword index's chunks, so the chunk table's case covers the vector chunk.
- **S3 "no row in edges":** no edge and no stated link has an archive-only id as its *source*; a kept entry's
  `SUPERSEDES` edge to it stays, as the interface says.
- **S4 "every archived id a kept entry cites":** the ids a kept entry's text names that the register does not hold
  and that are live entries of the archive by the store's own grammar. `DEC-027` and `DEC-974` are headings of the
  archive with no status line first: no record on the base, no row of the table now; two kept entries cite them.
- **S5 `acceptance_exemptions`:** `gov.close.ratchet.counted_entries` reads `accepted_reds` and `load_sensitive`
  only (its `FIELDS`); the exemptions are read by `gov.close.gates.owner_listed`, so that is the function the case
  calls, with `gov.close.history.accepted_history` for the accepted history.
- **F1/F2 lines:** a failure line is read wherever it is printed (standard output or error) by its first two words;
  the summary line is the last line of standard output that is not blank and starts with `ok`.
- **F3:** each F3 case first asks the new interface that the id is in neither file (`gov.util.archive.read`, or the
  store's table), so it is red on the base for that reason, though the finding itself already exists there.

## Map

| KPI | Test | Red reason on the base |
|---|---|---|
| S1 | `test_w2_203_archive.py::test_s1_the_archive_opens_with_a_line_saying_archived_and_read_only`, `test_w2_203_archive.py::test_s1_every_entry_of_the_base_register_is_in_the_archive_text_for_text`, `test_w2_203_archive.py::test_s1_the_rest_of_the_archive_is_the_base_register_whole`, `test_w2_203_archive.py::test_s1_the_path_map_names_the_archive_beside_the_register`, `test_w2_203_archive.py::test_s1_the_archive_namespace_is_out_of_both_indexes`, `test_w2_203_archive.py::test_s1_every_tracked_path_matches_exactly_one_namespace`, `test_w2_203_archive.py::test_s1_the_kernel_schema_accepts_the_key_as_text` | the archive file does not exist; the path map has no key `decision_register_archive` and no namespace `archive`; the schema does not state the key |
| S2 | `test_w2_203_register.py::test_s2_the_register_holds_the_kept_entries_and_every_late_one_in_the_archives_order_and_no_other`, `test_w2_203_register.py::test_s2_each_entry_is_the_archives_verbatim`, `test_w2_203_register.py::test_s2_the_store_loader_reads_the_register_with_no_refusal`, `test_w2_203_register.py::test_s2_the_head_says_what_the_file_is_and_names_the_archive_and_audit_8`, `test_w2_203_register.py::test_s2_doctor_lists_the_archive_among_its_historical_paths`, `test_w2_203_register.py::test_s2_doctor_reports_no_more_problems_than_on_the_base` | the archive file does not exist (the register is still the old one, its head names no archive); `HISTORICAL_PATHS` lacks the archive; HEAD holds no archive |
| S3 | `test_w2_203_memory.py::test_s3_the_archives_ids_and_headings_are_in_a_table_of_their_own`, `test_w2_203_memory.py::test_s3_the_table_is_outside_the_digest`, `test_w2_203_memory.py::test_s3_a_decision_of_the_kept_register_still_resolves_by_id_and_by_its_words`, `test_w2_203_memory.py::test_s3_a_path_map_that_names_no_archive_gives_an_empty_table`, `test_w2_203_memory.py::test_s3_a_named_archive_that_head_does_not_hold_refuses_nothing` | `gov.store.loader` has no `ARCHIVE_KEY`; the load writes no table `archived_decisions` |
| S4 | `test_w2_203_resolve.py::test_s4_the_archive_is_read_for_ids_and_headings_only`, `test_w2_203_resolve.py::test_s4_no_archive_named_or_held_reads_as_none`, `test_w2_203_resolve.py::test_s4_a_commit_citing_an_archived_id_is_no_finding_of_the_citations_check`, `test_w2_203_resolve.py::test_s4_gov_links_counts_archived_ids_among_the_ids_that_exist`, `test_w2_203_resolve.py::test_s4_no_dangling_reference_of_the_store_names_an_archived_id`, `test_w2_203_resolve.py::test_s4_the_closure_of_an_archived_id_lists_it_as_history`, `test_w2_203_resolve.py::test_s4_the_closure_from_a_kept_entry_reaches_the_archived_id_as_history`, `test_w2_203_resolve.py::test_s4_a_store_built_before_the_table_is_still_read`, `test_w2_203_resolve.py::test_s4_real_gov_links_reports_no_finding_about_an_archived_id_that_the_base_lacked`, `test_w2_203_resolve.py::test_s4_real_the_citations_check_reports_no_finding_about_the_archive_that_the_base_lacked`, `test_w2_203_resolve.py::test_s4_real_every_archived_id_a_kept_entry_cites_resolves` | no module `gov.util.archive`; the archived id is `DECISION_UNRECORDED`, `UNKNOWN_ID`, a dangling reference and an `UNRESOLVED` gap; no table `archived_decisions`; HEAD holds no archive |
| S5 | `test_w2_203_close_lookup.py::test_s5_the_register_reader_returns_the_archives_entry_with_its_status_line_and_text`, `test_w2_203_close_lookup.py::test_s5_a_ratchet_entry_whose_decision_lives_only_in_the_archive_counts`, `test_w2_203_close_lookup.py::test_s5_an_acceptance_exemption_whose_decision_lives_only_in_the_archive_counts`, `test_w2_203_close_lookup.py::test_s5_accepted_history_whose_decision_lives_only_in_the_archive_counts`, `test_w2_203_close_lookup.py::test_s5_a_closed_tickets_trailer_id_resolves_through_the_archive`, `test_w2_203_close_lookup.py::test_s5_real_the_lists_count_what_the_base_counted`, `test_w2_203_close_lookup.py::test_s5_real_no_closed_tickets_trailer_id_is_unresolved_that_the_base_resolved` | "the register holds no entry DEC-105": the reader does not read the archive, so the entry is refused and the trailer id unresolved; HEAD holds no archive |
| S6 | `test_w2_203_builder.py::test_s6_rebuilding_from_the_archive_gives_the_committed_register_byte_for_byte`, `test_w2_203_builder.py::test_s6_the_archive_is_read_from_the_path_maps_key_and_the_kept_and_late_entries_are_written`, `test_w2_203_builder.py::test_s6_an_entry_appended_to_the_archive_is_in_the_output_whatever_its_id`, `test_w2_203_builder.py::test_s6_real_a_late_entry_appended_to_this_archive_is_in_the_output_and_the_rest_is_unchanged` | `docs/emergency-2/audits/08-new-register.py` is not a file of this tree; the archive file does not exist |
| F1 | `test_w2_203_builder.py::test_f1_real_the_committed_register_and_archive_check_clean`, `test_w2_203_builder.py::test_f1_a_register_that_lacks_a_kept_or_late_entry_is_named`, `test_w2_203_builder.py::test_f1_the_check_reads_the_projects_own_register_by_default`, `test_w2_203_builder.py::test_f1_a_decision_made_after_the_move_is_no_failure` | the builder is not a file of this tree |
| F2 | `test_w2_203_builder.py::test_f2_an_entry_whose_text_differs_by_one_character_is_named` | the builder is not a file of this tree |
| F3 | `test_w2_203_resolve.py::test_f3_a_commit_citing_an_id_in_neither_file_is_still_unrecorded`, `test_w2_203_resolve.py::test_f3_gov_links_still_finds_an_id_in_neither_file_unknown_in_each_place`, `test_w2_203_resolve.py::test_f3_an_id_in_neither_file_is_still_a_dangling_reference`, `test_w2_203_resolve.py::test_f3_an_id_in_neither_file_is_still_an_unresolved_gap_of_the_closure` | no module `gov.util.archive`, no table `archived_decisions` (the finding itself exists on the base; the archived id beside it is also found there, which the S4 cases show) |
| F4 | `test_w2_203_memory.py::test_f4_no_archive_only_decision_is_a_store_record`, `test_w2_203_memory.py::test_f4_no_archive_only_decision_is_a_register_entries_row`, `test_w2_203_memory.py::test_f4_no_chunk_of_the_keyword_index_is_of_the_archive`, `test_w2_203_memory.py::test_f4_a_search_for_a_decision_only_the_archive_holds_returns_no_chunk_of_it` | the load writes no table `archived_decisions`: the archive was not read, so "kept apart" is not shown (the namespace's `not indexed` already keeps the file out of the keyword index on the base, W2-13 S6) |

## Kinds and cost

- `test_w2_203_archive.py`, `test_w2_203_register.py` and every case named `real`: repository-state (`record_reading`:
  they read this repository's own records). The six clone cases are over the 5 s limit of their kind because the
  checks they run take that long on this repository's history (7,700 commits): the citations check, the traceability
  check, `gov doctor` and `gov links`, each once on the base and once on HEAD, side by side.
- The rest: acceptance, in process or one child, under 1 s each on a planted project built from scratch.
- Adding the repository-state cases to `governance/project/test-map.yaml`'s `record_reading` list is outside this
  folder's paths (the lead's).
