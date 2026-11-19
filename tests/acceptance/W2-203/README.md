# W2-203 acceptance tests: the old register archived and out of memory's index; the kept register in force

Ticket DAEO-r3gx (W2-203), profile FULL, class C3 (EMERGENCY-2 11.3, DEC-1214 G4 (a)). Written by the independent test
designer (MR-3) from the ticket's six success lines and four failure lines and the lead's interface text, before any
implementation, reading only the code at the ticket's base (`05ed38219` on `w2/integrate`, DEC-963) and the G4 lead's
draft builder (`e2/g4-g5:docs/emergency-2/audits/08-new-register.py`, not this ticket's implementation). Nothing of
this ticket's implementation was read.

KPI cells use positions in the ticket: `S<n>` is the n-th success line, `F<n>` the n-th failure line.

## How they run

    TMPDIR=$(mktemp -d) PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-203 -q -p no:cacheprovider

63 cases (61 before the amendment of 2026-11-19, below). The planted cases take about 5 s together, in process. The six clone cases take about 150 s together on a
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
  id is DEC-1211 or later (6): 161 entries. Since the amendment below only the 155 are held to the archive's text;
  the entries from DEC-1211 on are the register's own.

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
- **S4 "every archived id a kept entry cites":** the ids a kept entry's text names that the register does not hold.
  Every `### DEC-n` heading of the archive is an archived id, with a status line or without (the lead's reading:
  `DEC-027` and `DEC-974`, no records on the base, resolve as archived ids). In the closure each is `history`, none
  is itself a gap and no gap is `UNRESOLVED`; a `DEPTH_LIMIT_REACHED` gap of a neighbour is any record's at depth 0.
- **F4 the file table:** `lexical_file.indexed` of the archive is `lexical.KEPT_OUT` (kept out by the path map's
  policy), the kept register's is 1.
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
| S2 | `test_w2_203_register.py::test_s2_the_register_holds_the_archives_kept_entries_in_its_order_then_its_own_from_dec_1211_on`, `test_w2_203_register.py::test_s2_each_kept_entry_is_the_archives_verbatim`, `test_w2_203_register.py::test_s2_the_store_loader_reads_the_register_with_no_refusal`, `test_w2_203_register.py::test_s2_the_head_says_what_the_file_is_and_names_the_archive_and_audit_8`, `test_w2_203_register.py::test_s2_doctor_lists_the_archive_among_its_historical_paths`, `test_w2_203_register.py::test_s2_doctor_reports_no_more_problems_than_on_the_base` | the archive file does not exist (the register is still the old one, its head names no archive); `HISTORICAL_PATHS` lacks the archive; HEAD holds no archive |
| S3 | `test_w2_203_memory.py::test_s3_the_archives_ids_and_headings_are_in_a_table_of_their_own`, `test_w2_203_memory.py::test_s3_the_table_is_outside_the_digest`, `test_w2_203_memory.py::test_s3_a_decision_of_the_kept_register_still_resolves_by_id_and_by_its_words`, `test_w2_203_memory.py::test_s3_a_path_map_that_names_no_archive_gives_an_empty_table`, `test_w2_203_memory.py::test_s3_a_named_archive_that_head_does_not_hold_refuses_nothing` | `gov.store.loader` has no `ARCHIVE_KEY`; the load writes no table `archived_decisions` |
| S4 | `test_w2_203_resolve.py::test_s4_the_archive_is_read_for_ids_and_headings_only`, `test_w2_203_resolve.py::test_s4_no_archive_named_or_held_reads_as_none`, `test_w2_203_resolve.py::test_s4_a_commit_citing_an_archived_id_is_no_finding_of_the_citations_check`, `test_w2_203_resolve.py::test_s4_gov_links_counts_archived_ids_among_the_ids_that_exist`, `test_w2_203_resolve.py::test_s4_no_dangling_reference_of_the_store_names_an_archived_id`, `test_w2_203_resolve.py::test_s4_the_closure_of_an_archived_id_lists_it_as_history`, `test_w2_203_resolve.py::test_s4_the_closure_from_a_kept_entry_reaches_the_archived_id_as_history`, `test_w2_203_resolve.py::test_s4_a_store_built_before_the_table_is_still_read`, `test_w2_203_resolve.py::test_s4_real_gov_links_reports_no_finding_about_an_archived_id_that_the_base_lacked`, `test_w2_203_resolve.py::test_s4_real_the_citations_check_reports_no_finding_about_the_archive_that_the_base_lacked`, `test_w2_203_resolve.py::test_s4_real_every_archived_id_a_kept_entry_cites_resolves` | no module `gov.util.archive`; the archived id is `DECISION_UNRECORDED`, `UNKNOWN_ID`, a dangling reference and an `UNRESOLVED` gap; no table `archived_decisions`; HEAD holds no archive |
| S5 | `test_w2_203_close_lookup.py::test_s5_the_register_reader_returns_the_archives_entry_with_its_status_line_and_text`, `test_w2_203_close_lookup.py::test_s5_a_ratchet_entry_whose_decision_lives_only_in_the_archive_counts`, `test_w2_203_close_lookup.py::test_s5_an_acceptance_exemption_whose_decision_lives_only_in_the_archive_counts`, `test_w2_203_close_lookup.py::test_s5_accepted_history_whose_decision_lives_only_in_the_archive_counts`, `test_w2_203_close_lookup.py::test_s5_a_closed_tickets_trailer_id_resolves_through_the_archive`, `test_w2_203_close_lookup.py::test_s5_real_the_lists_count_what_the_base_counted`, `test_w2_203_close_lookup.py::test_s5_real_no_closed_tickets_trailer_id_is_unresolved_that_the_base_resolved` | "the register holds no entry DEC-105": the reader does not read the archive, so the entry is refused and the trailer id unresolved; HEAD holds no archive |
| S6 | `test_w2_203_builder.py::test_s6_rebuilding_from_the_archive_gives_the_committed_registers_kept_part_byte_for_byte`, `test_w2_203_builder.py::test_s6_the_archive_is_read_from_the_path_maps_key_and_the_kept_and_late_entries_are_written`, `test_w2_203_builder.py::test_s6_an_entry_appended_to_the_archive_is_in_the_output_whatever_its_id`, `test_w2_203_builder.py::test_s6_real_a_late_entry_appended_to_this_archive_is_in_the_output_and_the_rest_is_unchanged` | `docs/emergency-2/audits/08-new-register.py` is not a file of this tree; the archive file does not exist |
| F1 | `test_w2_203_builder.py::test_f1_real_the_committed_register_and_archive_check_clean`, `test_w2_203_builder.py::test_f1_a_register_that_lacks_a_kept_entry_is_named`, `test_w2_203_builder.py::test_f1_the_check_reads_the_projects_own_register_by_default`, `test_w2_203_builder.py::test_f1_a_decision_made_after_the_move_is_no_failure` | the builder is not a file of this tree |
| F2 | `test_w2_203_builder.py::test_f2_a_kept_entry_whose_text_differs_by_one_character_is_named`, `test_w2_203_builder.py::test_f2_an_entry_from_dec_1211_on_that_differs_and_one_the_archive_lacks_are_no_failure`, `test_w2_203_builder.py::test_f2_the_last_classed_id_is_still_held_to_the_archive` | the builder is not a file of this tree; since the amendment: `--check` names an entry from DEC-1211 on that differs (`REGISTER_ENTRY_DIFFERS DEC-1211`) |
| F3 | `test_w2_203_resolve.py::test_f3_a_commit_citing_an_id_in_neither_file_is_still_unrecorded`, `test_w2_203_resolve.py::test_f3_gov_links_still_finds_an_id_in_neither_file_unknown_in_each_place`, `test_w2_203_resolve.py::test_f3_an_id_in_neither_file_is_still_a_dangling_reference`, `test_w2_203_resolve.py::test_f3_an_id_in_neither_file_is_still_an_unresolved_gap_of_the_closure` | no module `gov.util.archive`, no table `archived_decisions` (the finding itself exists on the base; the archived id beside it is also found there, which the S4 cases show) |
| F4 | `test_w2_203_memory.py::test_f4_no_archive_only_decision_is_a_store_record`, `test_w2_203_memory.py::test_f4_no_archive_only_decision_is_a_register_entries_row`, `test_w2_203_memory.py::test_f4_no_chunk_of_the_keyword_index_is_of_the_archive`, `test_w2_203_memory.py::test_f4_a_search_for_a_decision_only_the_archive_holds_returns_no_chunk_of_it` | the load writes no table `archived_decisions`: the archive was not read, so "kept apart" is not shown (the namespace's `not indexed` already keeps the file out of the keyword index on the base, W2-13 S6) |

## The register in force is live from DEC-1211 on (the CTO's amendment of S2, S6 and F1, 2026-11-19)

The cases first held the committed register to the archive word for word, the entries from DEC-1211 on included. That
was the brief's mistake. A decision made after audit 8's classes is amended in place (DEC-1215 (2) orders its revert
recorded in its entry, which `b5dc80c27` did) and new decisions are appended; the archive is frozen and never follows.
The amended rule, and the cases that hold it:

1. **The kept part is the archive's.** Every entry of the archive classed `kept` (DEC-001 to DEC-1210) is in the
   register, verbatim and in the archive's order, and rebuilding from the archive gives that part byte for byte.
2. **The entries from DEC-1211 on are the register's own.** They may differ from the archive's copy, and entries the
   archive does not hold may follow. The repository cases hold them only to being there: DEC-1211 to DEC-1216, each
   once and in order, after the kept part, as entries the store's loader accepts.
3. **The failure lines are the kept part's.** A kept entry the register lacks is `REGISTER_KEPT_MISSING`; a kept
   entry (below DEC-1211) with another text is `REGISTER_ENTRY_DIFFERS`; a difference in an entry from DEC-1211 on,
   or an entry the archive lacks, is no line.

| KPI | Case (its name before, where it changed) | What it holds now | Red on `b5dc80c27` before the revision |
|---|---|---|---|
| S2 | `test_w2_203_register.py::test_s2_the_register_holds_the_archives_kept_entries_in_its_order_then_its_own_from_dec_1211_on` (was `..._holds_the_kept_entries_and_every_late_one_in_the_archives_order_and_no_other`) | the ids below DEC-1211 are the archive's kept ids in its order; every entry from DEC-1211 on stands after them; DEC-1211 to DEC-1216 are there once each, in order; a later id may follow | green, but red at the first decision the archive lacks |
| S2 | `test_w2_203_register.py::test_s2_each_kept_entry_is_the_archives_verbatim` (was `test_s2_each_entry_is_the_archives_verbatim`) | each of the archive's kept entries has the archive's text in the register; an entry from DEC-1211 on is not compared | "1 entries are not the archive's text: ['DEC-1215']" |
| S2 | `test_w2_203_register.py::test_s2_the_store_loader_reads_the_register_with_no_refusal` | no refusal; the loader reads every entry of the register, in order, DEC-1211 to DEC-1216 among them | green, but red at the first decision the archive lacks |
| S6 | `test_w2_203_builder.py::test_s6_rebuilding_from_the_archive_gives_the_committed_registers_kept_part_byte_for_byte` (was `..._gives_the_committed_register_byte_for_byte`) | from the first entry's heading to the first heading from DEC-1211 on, the build and the committed register are the same bytes, and that part is exactly the archive's kept entries; the build as a whole is the archive's kept entries, then its entries from DEC-1211 on as it has them (`--out` is a first build, not a rebuild of a live register). The head is S2's case, not this one | "the register rebuilt from the archive is not the committed docs/DECISION_REGISTER.md" |
| S6 | `test_w2_203_builder.py::test_s6_real_a_late_entry_appended_to_this_archive_is_in_the_output_and_the_rest_is_unchanged` | the output is the first build of the archive and the appended entry; its kept part is the committed register's. The appended id follows the last id of either file | "the existing entries changed" |
| S5 | `test_w2_203_close_lookup.py::test_s5_real_the_lists_count_what_the_base_counted` (revised on `ed00f823b`) | the register reader still finds an id the archive alone holds; then no loss, not equality: an entry of `accepted_reds`, `load_sensitive`, `acceptance_exemptions` (`gates.owner_listed`) or `accepted_history` that the base counted is not refused, and is counted where HEAD's path map still names it; an entry HEAD counts and the base did not is backed in HEAD's path map by a decision from DEC-1211 on (DEC-1217 (2) added G1's commit `2c31268e4a7c`) | `owner_listed` differs from the base's: the head counts `2c31268e4a7c` (DEC-1217) |
| F1 | `test_w2_203_builder.py::test_f1_real_the_committed_register_and_archive_check_clean` | unchanged in code: `--check` on this tree exits 0 with no line and its `ok` summary. Clean now means the kept part | `REGISTER_ENTRY_DIFFERS DEC-1215`, exit 1 |
| F1 | `test_w2_203_builder.py::test_f1_a_register_that_lacks_a_kept_entry_is_named` (2; was `..._a_kept_or_late_entry_is_named`), `test_w2_203_builder.py::test_f1_the_check_reads_the_projects_own_register_by_default` | the entries removed are kept ones (DEC-102, DEC-104; the second with its class on the status line's second line) | green |
| F2 | `test_w2_203_builder.py::test_f2_a_kept_entry_whose_text_differs_by_one_character_is_named` (2; was `test_f2_an_entry_whose_text_differs_by_one_character_is_named`) | the entries changed are kept ones | green for the kept one; its DEC-1211 row asserted the old rule |
| F2 | `test_w2_203_builder.py::test_f2_an_entry_from_dec_1211_on_that_differs_and_one_the_archive_lacks_are_no_failure` (new) | a planted register with DEC-1211 amended in place by a line, DEC-1212 changed by one character and DEC-1300, which the archive lacks, appended: `--check` is clean; with a kept entry changed as well, that entry alone is named | new |
| F2 | `test_w2_203_builder.py::test_f2_the_last_classed_id_is_still_held_to_the_archive` (new) | the boundary: a planted kept entry DEC-1210 and DEC-1211, each changed by one character: `REGISTER_ENTRY_DIFFERS DEC-1210` alone | new |

**Left open, not asserted either way:** whether `--check` still names an entry from DEC-1211 on that the archive holds
and the register *lacks* (the first F1 line said "or of DEC-1211 and later"; the amended rule speaks of a kept entry
missing and of a late entry differing). The planted missing-entry cases now remove kept entries only, so they hold
under both readings; on this repository the S2 cases hold DEC-1211 to DEC-1216 to being there.

**Red until the builder's `--check` compares only the entries below DEC-1211** (the CTO's change to
`docs/emergency-2/audits/08-new-register.py`, not in this tree on `dafeb32b1`): three cases, each because the check
still prints `REGISTER_ENTRY_DIFFERS` for an entry from DEC-1211 on.
`test_f1_real_the_committed_register_and_archive_check_clean` (`DEC-1215`),
`test_f2_an_entry_from_dec_1211_on_that_differs_and_one_the_archive_lacks_are_no_failure` (`DEC-1211`, `DEC-1212`) and
`test_f2_the_last_classed_id_is_still_held_to_the_archive` (`DEC-1211` beside the expected `DEC-1210`).

## Kinds and cost

- `test_w2_203_archive.py`, `test_w2_203_register.py` and every case named `real`: repository-state (`record_reading`:
  they read this repository's own records). The six clone cases are over the 5 s limit of their kind because the
  checks they run take that long on this repository's history (7,700 commits): the citations check, the traceability
  check, `gov doctor` and `gov links`, each once on the base and once on HEAD, side by side.
- The rest: acceptance, in process or one child, under 1 s each on a planted project built from scratch.
- Adding the repository-state cases to `governance/project/test-map.yaml`'s `record_reading` list is outside this
  folder's paths (the lead's).
