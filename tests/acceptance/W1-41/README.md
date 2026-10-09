# W1-41 Acceptance Tests — gov adopt --lite and legacy importer

Ticket: `DAEO-cdoi` · Profile: FULL · Covers: CAP-06.b, CAP-06.c, CAP-06.d, CAP-42.a, CAP-42.b, CAP-42.c,
CAP-44.b, CAP-44.c, CAP-44.d, CAP-44.e, CAP-44.j, and CAP-15.c for the ticket's ninth success line

Written by the Independent Test Designer (MR-3, DEC-069) before implementation, from the ticket's KPI lines, the
Contract items they cite, DEC-006, DEC-090, DEC-137, DEC-449, DEC-454, DEC-488, DEC-499, DEC-517, and the READMEs and
code of the suites the stages stand on. The ninth success line and the rows of DEC-535 were added later, from
DEC-473, DEC-511, DEC-519, DEC-520, DEC-521, DEC-523, DEC-535 and W1-24's README. The cases of DEC-552 (the
forms of a citation, the records that still stand, all-external sources beside dependencies) were added after the
reviewer's probe. No earlier ticket's test was rewritten; one case of this suite was (below, "Success 5").

Run: `env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-41 -q -p no:cacheprovider -rs`

**182 cases in 8 files** (180 without the two `local_only` dev-tier cases): the 134 of the adoption tool (52 of
them in `test_w1_41_legacy.py`), 3 rows for DEC-535, and 45 for the ninth success line. Standard library, PyYAML, pytest, W1-07's support, and W1-24's
support for the context. No network, no model.

**This ticket builds the tool. It adopts nothing.** Every case runs `gov adopt --lite` on a project the case
builds itself, file by file, in its own temporary folder, as a git repository of its own. `run_gov` refuses a
project that is this repository, a folder of it, or a worktree of it. Nothing under `governance/project/` of this
repository is read: the temporary project's path map is written from the kernel's schema. Backup ref, rollback
points and archive ref are created by the tool in the temporary project only.

## Red run (before implementation)

At `c96add70`: 80 failed, 23 errors, 1 passed in 25 s (104 cases). With the six cases of DEC-517 added on top of
`eb64224f`: **80 failed, 29 errors, 1 passed** in 37 s.

- **109 cases are red only because the command is not built**: `gov adopt --lite …` answers `NOT_IMPLEMENTED`
  ("gov adopt is reserved and not built yet"). 80 fail in the case, 29 error in a fixture: 23 in a module fixture
  that carries one adoption through A8 (21 in `test_w1_41_legacy.py`, 2 in `test_w1_41_dev_tier.py`), and the 6
  cases of DEC-517 in the fixture that carries their project through A2 (stage A0 answers `NOT_IMPLEMENTED`). Among them
  `test_lite_without_a_stage_is_a_usage_error` fails as "exit code 1, expected 2", for the same reason.
- **1 case is green and must stay green**: `test_adopt_without_lite_is_still_reserved` (see "The interface", 1).

**Four cases added after the command was built** (`0a148039`), each red for a reason of its own: the two of
`test_a_memory_store_a_kept_legacy_rule_file_cites_is_not_retired` (A8 reports success, lists the three files of the
store under `retired` and does not name the citing rule file; measured in the sandbox), and the two of
`test_a_plan_that_is_not_the_audited_path_maps_plan_is_not_executed` (they stop at A3 in the sandbox, see "Where the
cases can run"; the lead runs them).

No behaviour assertion can be red for a reason of its own before the command exists; every refusing case asserts
that the refusal is the tool's own (`assert_refused` fails on `NOT_IMPLEMENTED`), so none passes by the command's
absence.

**Added on `9ad3bfbe`** (measured in the sandbox):

- **3 rows of DEC-535, green**: `test_a_split_a_merge_or_an_extract_where_code_intelligence_is_off_is_refused_and_writes_nothing`
  (SPLIT, MERGE, EXTRACT). The tool refuses as built.
- **36 cases of the ninth success line: 30 failed, 6 passed** in 5 s, against the context as W1-24 built it. The red
  reasons and the six that are green by design are in "Success 9". Run against a stand-in kept outside the tree
  (and not committed), all 36 pass: the cases can be satisfied together.

**Added on `4c66d012`** (the context accepts listed ids; measured in the sandbox): **3 cases of a ticket whose
declared ids are all external, all 3 failed**, the 36 before them passed (3 failed, 36 passed in 9 s). Each is red
for its own reason: the context is built, exit code 0, with `mandatory: []`, `tokens: 0` and the ids under
`external` (package P-13). Run against a stand-in kept outside the tree (and not committed), all 39 pass.

**Added on `8463aeb5`, after the reviewer's probe (DEC-552; measured in the sandbox).** 27 rows added, one case
rewritten; the suite went from 156 to 182 cases.

- `test_w1_41_legacy.py`: **10 failed, 42 passed** in about 4 minutes. Red, each for a reason of its own (A8
  reports success, exit code 0, and lists the three files of the store under `retired`): the 5 rows of
  `test_a_kept_rule_file_cites_the_store_however_it_writes_the_path` (the answer does not name the kept rule
  file), and the rows `ACCEPTED`, `PROPOSED`, `DRAFT`, `DEPRECATED` and "a status nobody knows" of
  `test_a_record_that_still_stands_keeps_the_store` ("retired although it must not be"). Green as built, and they
  stay green: the 4 rows of `test_a_citation_the_proof_sees_today_is_refused_and_the_citer_named`, the 3 rows of
  `test_a_longer_path_or_id_that_only_contains_the_stores_is_no_citation`, the row "no status" of
  `test_a_record_that_still_stands_keeps_the_store`, and the 3 rows of
  `test_a_record_that_no_longer_stands_does_not_keep_the_store`.
- `test_w1_41_external_references.py`: **3 failed, 42 passed** in 8 s. Red: the 3 rows of
  `test_a_ticket_whose_sources_are_all_external_is_refused_beside_dependencies` (the packet is built, exit code
  0, the dependency among its mandatory inputs with the reason "declared in sources", the ids under `external`).
  Green, and they stay green: the 3 rows of `test_a_ticket_with_a_source_that_was_read_is_built_beside_dependencies`.

## Sources that could not be read

- **S0a-G-13 and G-10** (the ticket's first two sources) are not in the readable tree: `docs/source/` is closed to
  this session and the workbench is not read. **Nothing here is derived from them.**
- The Adoption Protocol v3.0, the Distribution Protocol v1.2 and Framework v4.1.2, which the Contract items cite
  by paragraph, are not in the readable tree either. Where the cases needed more than the Contract's own words,
  the point is in "Settled here" or in "Packages" below.

## Not covered here

- The ticket's eighth success line (the ticket closes under the adoption-gap exceptions, which end when this
  repository's adoption is complete, DEC-522) is about how this ticket is closed, not about what the tool does. No
  case is written for it.
- `gov close` is not run by any case of the ninth success line: it uses the context as it is. What W1-30's README
  records about it: where `gov context` answers `BLOCKED`, the close is refused with exit code 3, the answer says
  the context failed and names the source, no close record is written, the ticket stays in progress and the
  attempt is counted (DEC-454: a context that cannot be built refuses the close).
- That this repository's own `governance/project/external-references.yaml` lists the right sources is not held:
  the engineer writes that file, and no case reads it.

## The project every case builds

`build_project` writes the "harbour" project: a path map that classes every file (one namespace, code
intelligence on), a native package layout (`pyproject.toml`, `src/app/`), a loose module `lib/util.py` imported by
`scripts/run.py`, two documents, a record `notes/dec-300.md` (`DEC-300`, with a consumer) that another record
(`DEC-301`) depends on, a root rule under `.rulesync/`, and the legacy material:

| Legacy material | Files |
|---|---|
| Rule files (the five kinds of success line 3) | `AGENTS.md` with two role sections, `.cursorrules`, `.windsurfrules`, `.cursor/rules/style.mdc`, `.cursor/rules/review.mdc`, `.mcp/tools.json` |
| Legacy memory store | `legacy/memory/decisions/leg-001.md`, `leg-002.md` (two ACTIVE decisions), `legacy/memory/index.md` |
| Raw chat database stand-in | `legacy/chat/history.db` (a small SQLite file; the tool is never asked to understand it) |
| What was extracted from the chat database | `spec/research/ext-0001.md`, which cites the database by path and content hash |

Variants add or leave out files (`vault/ledger.bin`, which no namespace holds; a citing record; a citing rule; a
record that cannot be read; a tools file that is not JSON).

## The interface the cases hold

Settled here where the sources leave it open, staying with what the existing commands do (`src/gov/cli/main.py`,
API-0002). **Each point is the cases' reading, not a source's word; the engineer may dispute any of them through
the lead.**

1. **`gov adopt` without `--lite` stays `NOT_IMPLEMENTED`** (exit code 1). DEC-090: Wave 1 delivers
   `gov adopt --lite`; the full transaction with its verdict is Wave 3. So W1-07's lists and cases are untouched:
   `adopt` stays in `NOT_BUILT` there, and its cases that run `gov adopt --json` keep holding.
2. **One stage per call:** `gov adopt --lite --stage <A0|A1|A2|A3|A4|A5|A6|A8> [--json] [--session <id>]`, in the
   project that is the working directory (or `--root`). `--lite` without `--stage` is a usage error (exit code 2).
   - `--stage A3 --map <file>`: the proposal (below).
   - `--stage A5 --verdict <path in the project>`: the auditor's verdict record.
3. **Success:** the envelope with `ok: true`, exit code 0, `result.stage` and `result.record` (the evidence
   record's path, relative to the project). The record is committed by the stage and the tree is clean afterwards.
4. **A refusal:** `ok: false`, an exit code of API-0002 other than 0 and 2 (1, 3 or 4; which one is the
   implementation's), and an error object that names what the case says it names. A refusal writes nothing: no
   record, no ref, no commit (held wherever a case compares the tree).
5. **A stage stands on the one before it:** on a project where no stage has run, A1, A2, A3, A4, A6 and A8 each
   refuse. A8 comes after A6, so retirement is behind the A5 verdict too. A3 and A4 may be run again before A6.
6. **An evidence record** is a Markdown record with frontmatter: `id` (the record id grammar of
   `common.schema.json`), `type: evidence`, `state_class: EVIDENCE`, a `status`, `stage`, and the stage's data:

   | Stage | Frontmatter the cases read |
   |---|---|
   | A0 | `baseline_commit`; `backup_ref` (a full ref name, also `result.backup_ref`) resolving to that commit |
   | A1 | `artefacts`: a list of `{path}` |
   | A2 | `artefacts`: `{path, namespace}`; `unknown`: the paths no namespace holds; `result.packages`: the decision packages raised |
   | A3 | `artefacts`: `{path, action, target or targets, authority, importers, references, consumers, justification}` |
   | A4 | `batches`: `{batch, rollback_point, artefacts: [{path}]}`; somewhere in the record, one object with `handling: rewrite` or `handling: flag` for every importer, reference and consumer |
   | A5 | `verdict` (the verdict record's path), `path_map_hash` |
   | A6 | `batches`: `{batch, status, rollback_point, commit}`, `status` being `done` for a completed batch |
   | A8 | `imported`: `{source, into: [paths under .rulesync/]}`; `dependency_proof: {…, citers: []}` naming that records and rules were read; `cit_e` (the CIT-E record's path); for every artefact that left the tree, an object `{path, disposition, reachable_at}` (in the A6 or the A8 record) |

   Where the records lie is the implementation's: the cases take each path from the envelope.
7. **The proposal** (`--map`), a YAML file outside the project: `artefacts:` a list of
   `{path, action, target | targets, batch, kind, justification}`. `targets` (a list) for SPLIT, `target` for the
   other actions that have one. `kind` is `rule-file`, `memory-store` or `chat-database` for legacy material.
   `justification: {materially_better, migration_risk}` for a move out of a native layout. **An artefact the
   proposal does not name is kept.** See package P-1.
8. **Batches.** Every batch of A6 ends in a commit of the project. A batch's rollback point is the ref A4 recorded
   for it; after the batch started it resolves to the commit the batch started from.
9. **An unknown material artefact** is a tracked path that no namespace of the project's path map holds (CAP-06's
   acceptance line; what `gov doctor` reports as unclassified).

### The A5 verdict

From CAP-44.c ("independent review of the path map before any move (Independent Auditor)"), DEC-090, the kernel
role file (`independent-auditor.md`: "a fresh session that wrote none of the audited files"; its report is
"committed with the trailers `Task: <ticket>` and `Role: independent-auditor`"), and the way DEC-137's probe record
was settled for W1-30 (DEC-454: independence is read from the commits' `Role` trailers, not from the record's own
word; DEC-490: only `pass` passes).

A verdict is accepted when all of these hold; otherwise A5 refuses, A6 refuses, and no file moves:

| What | Held by |
|---|---|
| it is a committed record whose frontmatter can be read | broken YAML, no frontmatter, written and not committed, no such file |
| `verdict: pass` | `fail`, `inconclusive`, `pass_with_findings`, no `verdict` key |
| the commit that brought it carries `Role: independent-auditor` | `Role: engineer`, `Role: orchestrator`, no `Role` trailer |
| `path_map_hash` is the sha256 of the path map's record (A3) as it stands | no hash; the map changed after the verdict; the map changed after A5 had passed |
| `auditor_session` is not the session that ran the stages (`--session`) | the adopter's own session id |

The case's verdict: `id`, `type: adoption-verdict`, `status`, `state_class: EVIDENCE`, `stage: A5`, `verdict`,
`path_map`, `path_map_hash`, `auditor_session`, at `audit/adoption/a5-verdict.md`.

## KPI lines → tests

### Success 1 — the stages' evidence records [CAP-06.b, CAP-44.b]

| Clause | Tests |
|---|---|
| each stage writes an evidence record | `baseline`: `test_stages_a0_to_a4_each_leave_their_own_evidence_record`; every `ok(...)` of every case (record committed, typed, names its stage); `verdict`: `test_a_passing_verdict_of_the_independent_auditor_is_recorded_by_a5`; `dev_tier`: `test_the_eight_stages_each_leave_an_evidence_record_on_b_dev` |
| "on b-dev" | `dev_tier` (2 cases, `local_only`) |
| A0 clean tree and backup ref | `baseline`: `test_a0_records_the_clean_tree_and_a_backup_ref`, `test_a0_refuses_a_dirty_tree_and_writes_nothing` (3), `test_a_folder_that_is_no_git_repository_is_refused` |
| A1 inventory | `baseline`: `test_a1_inventory_lists_every_tracked_artefact` |
| A2 classification | `baseline`: `test_a2_classifies_every_inventoried_artefact`, `test_a_project_without_a_path_map_is_not_classified` |
| A3 path map with the eight actions [CAP-06.b] | `path_map`: `test_every_artefact_has_exactly_one_of_the_eight_actions`, `test_each_of_the_eight_actions_is_recorded_as_proposed`, `test_an_action_outside_the_eight_is_refused` (4), `test_an_artefact_given_two_actions_is_refused`, `test_a_path_the_inventory_does_not_hold_is_refused`, `test_a_move_without_a_target_is_refused`, `test_a_move_onto_an_artefact_that_stays_is_refused`, `test_a_proposal_that_cannot_be_read_is_refused` |
| A4 batched plan, a rollback point per batch | `path_map`: `test_the_plan_has_the_proposed_batches_each_with_its_own_rollback_point`; `migration`: `test_the_rollback_points_are_the_ones_the_plan_recorded` |
| customer questions as decision packages | `unknown`: `test_the_unknown_artefact_becomes_a_decision_package_for_the_customer`, `test_a_project_without_unknown_artefacts_raises_no_package_about_one` |
| a stage stands on the one before | `baseline`: `test_a_stage_without_the_record_of_the_stage_before_it_refuses` (6) |

### Success 2 and failure 2 — A5 before any move; rollback; moves before the rebuild [CAP-44.c, CAP-44.d]

| Clause | Tests |
|---|---|
| no move before an A5 verdict (failure 2) | `verdict`: the 17 cases of the table above |
| a plan that is not the audited path map's plan is not executed (failure 2) | `verdict`: `test_a_plan_that_is_not_the_audited_path_maps_plan_is_not_executed` (2: another target for an artefact the path map moves; a move of an artefact the path map keeps) |
| a failed batch rolls back to its recorded point | `migration`: `test_a_failed_batch_rolls_back_to_its_point_and_the_batches_before_it_stay` |
| moves precede `gov rebuild` | `migration`: `test_the_index_refresh_follows_the_moves` |
| the baseline is measured | `migration`: `test_a_backup_ref_that_no_longer_resolves_stops_the_migration`, `test_a_tree_that_is_dirty_at_a6_is_not_migrated` |

**The plan that is not the path map's.** The verdict is about the path map (the A3 record); the batches A6
executes are recorded by A4. After A4 wrote its record, the case changes that record's frontmatter, commits the
change (no trailer), and the Independent Auditor then passes the path map, which did not change (same content
hash); A5 is run in the ordinary way. The change, on the shape of interface point 6 (`batches[].artefacts[]`):
the guide's entry gets `action: MOVE` and `target: docs/elsewhere/guide.md`, and every string of the frontmatter
that holds the path map's target holds the other one instead; or an entry for `README.md` (which the path map
keeps), shaped as the plan's own entry for the guide, is added to the guide's batch with `target: docs/README.md`.
Held: A6 refuses (the tool's own refusal); no origin left its place; no target and no altered target exists at HEAD
or on disk; every file the project held before A5 is at its path with its content; nothing arrived but records in
the stages' own folder. **Left open:** whether A5 already refuses or only A6 does, and what the refusal names.

**How the batch is made to fail.** Batch 2 holds two moves. The folder of one target (`spec/decisions/`) exists and
is made read-only before A6; git does not see that, so the tree is clean. Batch 1 stays, batch 2 is undone as a
whole, batch 3 does not run, and the tree equals batch 2's rollback point. The case is skipped for a user that
folder permissions do not hold (root).

### Failure 1 — no file content changes during a move batch

`migration`: `test_every_moved_file_is_byte_for_byte_what_it_was`,
`test_no_other_tracked_file_changes_content_during_a_move_batch`. Between a batch's rollback point and its commit:
a path in both holds the same blob; a path that appears is a planned target holding its origin's blob, or one of
the tool's own records; a path that disappears is a planned origin of that batch. It follows that a rewrite of a
reference is never inside a move batch; whether the tool performs rewrites at all is package P-7.

### Success 3 and failure 3 — A8 import and retirement [CAP-42.a, CAP-44.e]

| Clause | Tests (`legacy`) |
|---|---|
| the five kinds import into `.rulesync/` | `test_each_kind_of_legacy_rule_file_is_imported_into_rulesync` (5), `test_the_imported_mcp_server_keeps_its_command`, `test_the_two_role_sections_of_agents_md_are_both_imported`, `test_the_a8_record_names_what_each_legacy_rule_file_was_imported_into` |
| no legacy rule file stays loaded (failure 3) | `test_no_legacy_rule_file_stays_where_an_agent_tool_loads_instructions`, `test_adapter_generation_is_run_or_named` (DEC-488) |
| a legacy file that cannot be read is not retired | `test_a_legacy_rule_file_that_cannot_be_parsed_is_not_retired`, `test_a_legacy_rule_file_that_cannot_be_read_is_not_retired` |
| the chat database is marked non-authoritative | `test_the_chat_database_is_marked_non_authoritative` |
| its unique knowledge is extracted to records before retirement | `test_the_chat_database_is_retired_after_its_knowledge_is_in_records`, `test_a_chat_database_with_nothing_extracted_is_not_retired`, `test_an_extraction_from_another_content_of_the_database_does_not_count`, `test_a_chat_database_that_cannot_be_read_is_not_retired` |
| retired systems contribute zero ACTIVE decisions | `test_retired_systems_contribute_no_active_decision` |

The import is held by its **result**: what each legacy file says is found, committed, under `.rulesync/`
afterwards. The way is package P-3.

### Success 4 — importers, references, consumers [CAP-06.d]

`path_map`: `test_every_artefact_to_be_moved_carries_importers_references_and_consumers`,
`test_the_importer_of_a_moved_module_is_read_from_the_code_graph`,
`test_the_references_and_consumers_of_a_moved_record_are_read_from_the_record_graph`,
`test_the_plan_rewrites_or_flags_every_importer_reference_and_consumer`,
`test_a_code_graph_that_cannot_be_read_refuses_and_records_no_importers` (the code index tool is taken off `PATH`).

**Where the project's path map turns code intelligence off (DEC-517, ratified by DEC-523; DEC-535 point P-10).**
The importers of an artefact are read from the code graph; such a project has none, so they cannot be measured, and
nothing is moved there: none of the five actions that put an artefact, or its content, at another path is
accepted. The project is the harbour project with `code_intelligence: {enabled: false}`.

| Clause | Tests (`path_map`) |
|---|---|
| a proposal that takes an artefact to another path is refused by A3, which names the artefact and the reason and writes nothing (no record, no ref, no commit, the tree as it was) | `test_a_move_where_code_intelligence_is_off_is_refused_and_writes_nothing` (3: MOVE of a module that has an importer, MOVE of a document, RENAME of a document) |
| SPLIT, MERGE and EXTRACT are refused in the same way: the same refusal, the same reason, nothing written, no origin gone, nothing at a proposed target (DEC-535) | `test_a_split_a_merge_or_an_extract_where_code_intelligence_is_off_is_refused_and_writes_nothing` (3: SPLIT of a document into two, MERGE of two documents into one, EXTRACT from a document) |
| the proposal is refused as a whole | `test_a_move_among_retirements_is_refused_as_a_whole_where_code_intelligence_is_off` |
| no later stage moves it | `test_no_later_stage_moves_what_was_refused_where_code_intelligence_is_off` (A4 and A6 each refuse; no origin left its place, no target exists) |
| a proposal that moves nothing is not refused for that reason | `test_a_proposal_that_moves_nothing_is_recorded_where_code_intelligence_is_off` (on a built project; the two dev-tier cases hold the same on a clone, but are `local_only`) |

- **The reason** is read from the error object, whatever the case of its letters: it holds "code intelligence"
  (or `code_intelligence`, `code-intelligence`) and "importer". The error code and the exit code (1, 3 or 4) are
  the implementation's.
- **Which actions move.** MOVE and RENAME take an artefact whole from its path to another ("Failure 1": a planned
  target holds its origin's blob). SPLIT, MERGE and EXTRACT put its content, or a part of it, at another path.
  All five are held in such a project, one row per action for the last three (DEC-535 decides package P-10). KEEP,
  RETIRE and DELETE_FROM_ACTIVE_TREE take nothing to another path and are recorded there.

### Success 5 — memory store: dependency proof, CIT-E, index refresh [CAP-42.b]

`legacy`: `test_a_memory_store_nothing_cites_is_retired`, `test_the_dependency_proof_is_recorded`,
`test_a_memory_store_an_active_record_cites_is_not_retired` (an edge `depends_on` to a record of the store),
`test_a_memory_store_a_rule_cites_is_not_retired` (a rule under `.rulesync/rules/` that names a file of the store),
`test_a_memory_store_a_kept_legacy_rule_file_cites_is_not_retired` (2: `.windsurfrules`, `.cursorrules`; a legacy
rule file the proposal does not retire, so the path map keeps it and it stays loaded after A8, that names a file of
the store),
`test_a_citation_the_proof_sees_today_is_refused_and_the_citer_named` (4),
`test_a_kept_rule_file_cites_the_store_however_it_writes_the_path` (5),
`test_a_longer_path_or_id_that_only_contains_the_stores_is_no_citation` (3),
`test_a_record_that_still_stands_keeps_the_store` (6),
`test_a_record_that_no_longer_stands_does_not_keep_the_store` (3),
`test_a_record_that_cannot_be_read_is_no_proof_of_no_dependency`,
`test_the_retirement_of_the_memory_store_is_a_cit_e` (a committed record of type `change-execution-record`, the
form of `docs/changes/S2-CIT-E.md`, that names every retired file),
`test_the_index_is_refreshed_after_the_retirement` (`gov doctor`'s `index_freshness` in the temporary project).

In the "not retired" cases the stage's exit code is left open (it may retire the rest and say so, or refuse as a
whole); what is held is that the files stay and the citer is named. In the kept-rule-file case
the kept file stays as it was too, and where the stage reports success its record's `dependency_proof.citers` is not
the empty list. Two of the five kinds are held, not every kind.

**How a citation is written (DEC-552, finding 1).** A rule file the path map keeps (`.windsurfrules`) cites the
store whatever stands before the store's path or before the id of one of its records. Each row's project is built
in a folder named `harbour`.

| The kept rule file writes | Held |
|---|---|
| `./legacy/memory/index.md` | a citation |
| `[memory](/legacy/memory/index.md)` (a root-relative link) | a citation |
| `../legacy/memory/decisions/leg-002.md` | a citation |
| `harbour/legacy/memory/index.md` (the path as seen from the folder above the project) | a citation |
| `decisions/LEG-001` (a record id behind a folder) | a citation |
| `docs/memory/index.md` (another folder's file of the same name; the file exists in the project) | no citation: the store is retired |
| `oldlegacy/memory/index.md` (the store's path ends it, but not at a folder's boundary) | no citation: the store is retired |
| `LEG-0011` (an id that only begins with an id of the store) | no citation: the store is retired |

For a citation, A8 **refuses**: `ok: false`, the rule file named in the error object, and the error code and the
exit code are the ones A8 gives today for the bare path (`legacy/memory/index.md`) or the bare id (`LEG-001`) in
the same rule file. The cases measure that refusal in a project of their own
(`test_a_citation_the_proof_sees_today_is_refused_and_the_citer_named`) and name no code. Every file of the store
and the kept file stay as they were. Here the exit code is not left open.

**Which records count (DEC-552, finding 6; the stricter reading of "no active record").** A record outside the
store that cites it (by `depends_on` to a record of the store, or by naming a file of the store in its text) holds
the store back unless its status says that it no longer stands. Three statuses say so: `SUPERSEDED`, `RETIRED`,
`REJECTED`; a record with one of them does not keep the store. Every other status keeps it: `ACCEPTED`,
`PROPOSED`, `DRAFT` and `DEPRECATED` are refused as an `ACTIVE` record is (the same error code and exit code,
measured as above; the record named by its id or its path in the error object). A record with no `status` key and
one with a status nobody knows (`LINGERING`) keep the store too and are named; for those two the refusal's code is
left open (the tool may refuse them as records it cannot judge).

**Rewritten (Rewrite-Reason: stricter reading decided after the probe, DEC-552):**
`test_a_record_that_is_not_active_does_not_keep_the_store` held that a `DEPRECATED` record's citation is no
dependency. `DEPRECATED` is not one of the three statuses, so that record now keeps the store: the case became the
row `DEPRECATED` of `test_a_record_that_still_stands_keeps_the_store`, and what it held for a record that no
longer stands is held by `test_a_record_that_no_longer_stands_does_not_keep_the_store`.

### Success 6 — archive policy [CAP-42.c]

`legacy`: `test_retired_material_stays_reachable_as_it_was`, `test_nothing_left_the_tree_without_a_recorded_disposition`,
`test_what_the_path_map_keeps_is_untouched_by_the_retirement`,
`test_a_file_deleted_from_the_active_tree_stays_reachable_too`. `reachable_at` is a commit or a ref of the project
(git history or an archive ref: either).

### Success 7 — a healthy native layout is kept [CAP-44.j]

`path_map`: `test_a_native_package_layout_is_kept_where_nothing_else_is_proposed`,
`test_a_move_out_of_a_native_layout_without_a_justification_is_refused`,
`test_a_justification_that_states_only_one_of_the_two_grounds_is_refused` (2),
`test_a_justified_move_out_of_a_native_layout_is_recorded_with_both_grounds`. **Refusing reading, package P-6.**

### Failure 4 — an unknown material artefact is never moved or deleted [CAP-06.c]

`unknown`: `test_a2_names_the_unknown_artefact`,
`test_a_path_map_that_moves_or_deletes_the_unknown_artefact_is_refused` (4: MOVE, RENAME, RETIRE,
DELETE_FROM_ACTIVE_TREE), `test_an_unknown_artefact_blocks_the_whole_destructive_migration`,
`test_an_unknown_artefact_blocks_retirement_too`. **The last two hold the refusing reading, package P-5.**

### Success 9 — the context and sources that live outside the repository [CAP-15.c; DEC-511, DEC-520]

`test_w1_41_external_references.py`, 45 cases. Reached through the public interface only: the command
`gov context --json --root <project> [--brief] <ticket>` for the main rows, the function
`gov.context.context(root, ticket, ...)` for twelve. Every case builds the "quay" project in its own temporary
folder (a charter `CHARTER-H9`, a decision `ADR-H9-A`, a superseded decision `ADR-H9-OLD`, nine tickets, a path
map written from the kernel's schema), commits it and loads its record store there, as W1-24's cases do. No index
is built. Each point below is the cases' reading; the engineer may dispute any of them through the lead.

**The file: `governance/project/external-references.yaml`.** Shaped as the project's other lists there (one
top-level key that holds the entries, as `hosts:` and `tools:` do; an entry carries its own name, as a tool does,
so that a second entry for the same id can be seen).

```yaml
references:
  - id: S0a-G-12
    location: "the owner's archive of source documents: sources/S0a/G-12.md"
    reason: "a planning source the owner keeps outside this repository"
```

| Key | Required | Type | Meaning |
|---|---|---|---|
| `references` (top level) | yes | list of entries; may be empty | the sources that live outside the repository |
| `id` | yes | text, not empty | the id a ticket declares, exactly (compared as written) |
| `location` | yes | text, not empty | where the source lives |
| `reason` | yes | text, not empty | why it is not in the record store |

**The file is not of the stated shape** when any of these holds: it is not valid YAML; it is empty; its top level
is not a mapping; the mapping has no `references`; `references` is not a list; an entry is not a mapping; an entry
lacks `id`, `location` or `reason`; one of the three is not text, or is empty or only white space; two entries
have the same `id`; an `id` is of the decision register's form, `DEC-` followed by digits only (below). One
defective entry makes the whole file defective. A file with `references: []` is of the shape. **Left open, no
case:** a key the table does not name (at the top level or in an entry).

**The packet's addition: the key `external`.** A list, one item per id the ticket declares that is not a record of
the store and is listed, in the order the ticket declares them:

| Key of an item | Value |
|---|---|
| `id` | the declared id |
| `location` | the entry's `location`, as the file states it |
| `reason` | the entry's `reason`, as the file states it |
| `read` | `false`: this source was not read |

An item carries none of `sha256`, `authority`, `lifecycle`, `constraint`, `text`, `tokens`, `path`. The id is in
none of `mandatory`, `authority`, `supplementary`. The packet's `tokens` and `budget` are what they are for a
ticket that declares the same records and no external id. The packet's `hash` covers the items. **The key is
absent, not present and empty, where the ticket declares no external reference:** the packet of a ticket whose ids
are all records keeps W1-24's eight keys and its hash, with or without the file. An entry no id of the ticket
names is not reported. With `--brief` the summary has a line that names the id and holds the words "not read"
(whatever the case of the letters), and the file the result points to is the packet, `external` included.

**A refusal** is the context's `BLOCKED` (the code it gives a missing input today), never a packet. For a
defective file the error names the file by its path `governance/project/external-references.yaml`: anywhere in the
error object of the command's envelope, and in the message for a caller of the function.

**A ticket whose declared ids are all external is refused (held until the owner answers, package P-13).** Every id
it declares is listed and none is a record of the store, so a packet for it would hold nothing that anybody read.
The refusal is the same `BLOCKED` a ticket that declares no mandatory inputs gets today, never a packet. The error
names the ticket and every external id the ticket declares, in the same places as the suite's other refusals:
anywhere in the error object of the command's envelope, and in the message for a caller of the function. In both,
the error's message holds the words "external" and "read" (whatever the case of the letters): it says that every
declared input is external and none was read, which neither the refusal of a missing id nor that of a ticket
without inputs says. A ticket that declares at least one record beside its external references is built, as the
rows above hold.

**All-external sources beside dependencies (DEC-552, finding 8).** A dependency that was read is not a source
that was read. The ticket's `sources` are all listed and none is a record; beside them it names, by `depends_on`
or by `deps`, a ticket of the project that exists and that the context reads (the case first asks for the context
of a ticket that names the same dependency and no source, and finds the dependency among its mandatory inputs).
The refusal is the one above, from the command and from the function: `BLOCKED`, the ticket and every external id
named, the message holds "external" and "read". A third row holds the same where `depends_on` names a record that
is no ticket (a decision): the stricter reading, package P-14. A ticket with at least one source that is a record
is built as before, with or without dependencies: the record among its mandatory inputs with its content hash,
the external ids under `external` in the ticket's order, none of them among the mandatory inputs, and the
function gives the command's packet. What stands in `mandatory` beside the record is not held. Nothing is held
here for a ticket without external ids: that is W1-24's.

| Clause | Tests (`external_references`) | Against the context as it stands |
|---|---|---|
| a listed id is accepted: the context is built, the other declared ids are its mandatory inputs | `test_the_context_of_a_ticket_that_declares_a_listed_id_is_built` | red: `BLOCKED`, the listed id reported as not found in the store |
| reported as external, with its id, where it lives and why, and that it was not read; in the ticket's order; an entry the ticket does not name is not reported | `test_the_packet_reports_each_listed_id_as_external_with_where_it_lives`, `test_the_function_reports_the_same_external_reference` | red: the same |
| never as content: in no block of read items, no hash, tier or lifecycle | `test_an_external_reference_is_not_among_the_items_read_as_records` | red: the same |
| nothing of it counts into the packet's tokens | `test_an_external_reference_adds_nothing_to_the_packets_tokens` | red: the same |
| the summary of `--brief` says the source was not read; the brief file is the packet | `test_the_brief_says_that_the_external_source_was_not_read` | red: the same |
| the hash covers it: the same project gives the same packet twice; a change of the entry's `location` or `reason` changes the hash | `test_the_same_project_gives_the_same_hash_twice`, `test_a_change_of_the_listed_entry_changes_the_packets_hash` (2) | red: the same |
| a ticket whose declared ids are all external is refused: `BLOCKED`, the ticket and every external id named, the message says that all are external and none was read (package P-13) | `test_a_ticket_whose_declared_ids_are_all_external_is_refused` (2: one external id; several), `test_the_function_refuses_a_ticket_whose_declared_ids_are_all_external` | red: the packet is built, exit code 0, with no mandatory item, 0 tokens and the ids under `external` |
| … whether or not the ticket also names dependencies that were read (DEC-552; package P-14 for the third row) | `test_a_ticket_whose_sources_are_all_external_is_refused_beside_dependencies` (3: a dependency ticket by `depends_on`; by `deps`; a record that is no ticket by `depends_on`) | red (measured after the row above was built): the packet is built, exit code 0, the dependency in `mandatory`, the ids under `external` |
| … and a ticket with a source that was read is built beside them | `test_a_ticket_with_a_source_that_was_read_is_built_beside_dependencies` (3: no dependency; by `depends_on`; by `deps`) | **green as built, and stays green** |
| unlisted stays blocked, the id named | `test_an_id_that_is_neither_a_record_nor_listed_stays_blocked` | **green, and stays green** |
| … also beside a listed id | `test_an_unlisted_id_blocks_a_ticket_that_also_declares_a_listed_one` | red: the error names the listed id as missing and stops before the unlisted one |
| the list never hides a record: a listed id that is a record stands among the mandatory inputs with its hash and is not reported as external | `test_a_listed_id_that_is_a_record_is_the_stores_record` | red: `BLOCKED` on the external id the ticket declares beside it |
| … and a listed superseded record still blocks, named | `test_a_listed_id_that_is_a_superseded_record_still_blocks` | **green, and stays green** |
| nothing fails open: a file that is not of the stated shape blocks and is named | `test_a_file_that_is_not_of_the_stated_shape_blocks_and_is_named` (13 rows, the list above but the register's form), `test_the_function_names_the_defective_file_in_its_message` | red: `BLOCKED` for the missing id, the file not named (it is not read) |
| … a file that cannot be read | `test_a_file_that_cannot_be_read_blocks_and_is_named` (skipped for a user that permissions do not hold) | red: the same |
| … for a ticket whose ids are all records too (package P-11) | `test_a_defective_file_blocks_a_ticket_whose_ids_are_all_records_too` (2) | red: the packet is built |
| a project without the file: the packet has W1-24's eight keys and no other | `test_a_project_without_the_file_gives_the_packet_it_gave_before` | **green, and stays green** |
| … a missing id blocks there, the id named (function and command) | `test_a_missing_id_blocks_in_a_project_without_the_file` | **green, and stays green** |
| … and a file that lists nothing the ticket declares leaves its whole packet, hash included, as it was without the file | `test_a_file_the_ticket_names_nothing_of_leaves_its_packet_as_it_was` (2: `references: []`; other ids) | **green, and stays green** |
| a register decision is not an external reference | `test_a_listed_id_of_the_decision_registers_form_is_refused` (2) | red: `BLOCKED` for the missing id, the file not named |

**Readings.**

- **The list never hides a record (held as stated).** The store is asked first: an id that is a record is that
  record, whatever the file says. A listed id that is also a record is not refused as a defect of the file: the
  file is judged from its own text and the project's configuration, never from what the store holds at that
  moment, so that the same file is not sound before a record arrives and defective after.
- **A defective file blocks every ticket (the stricter reading, package P-11).** DEC-449 and DEC-454 settle that
  what cannot be read is never taken for a clean answer (a count file that cannot be read refuses; a context that
  cannot be built refuses the close). They do not say whether the file is an input of a context that would not
  consult it. Held: it is one of every context's inputs once it exists.
- **A register decision (DEC-519, DEC-521).** The context can tell in two ways the sources give: the form of the
  id (DEC-473: a register entry is `### DEC-<digits>`), and the register file the project's path map names
  (`decision_register`, DEC-473). Held: a listed id of the form `DEC-<digits>` makes the file defective, and the
  error names the file and the id. One row has the id as an entry of a register the path map names; the other has
  no register at all and is refused by the form alone (the stricter reading, package P-12). The id itself stays
  blocked in both until the store loads register decisions as records (DEC-521's follow-up).
- **A ticket whose declared ids are all external is refused (the stricter reading, package P-13).** The ninth
  success line and DEC-520 say that a listed id is accepted and reported as external, never as content; CAP-15.a
  says a packet holds its mandatory inputs by id and sha256; neither says what a packet is when no declared id is
  one. A ticket that declares nothing is blocked today, and DEC-454 keeps a close from standing on a context
  that measured nothing. Held: such a ticket's context is not built, and the refusal says why. The other reading
  (the packet is built and says that nothing was read) is option (b) of the package.
- **Left open, no case:** whether the summary of `--brief` also gives the location; the exit code of the refusal
  (1 today).

### Measured or refused (DEC-449, DEC-454)

| A reading that fails | Case | Never becomes |
|---|---|---|
| no path map in the project | `baseline`: `test_a_project_without_a_path_map_is_not_classified` | "nothing is unknown" |
| the proposal cannot be read | `path_map`: `test_a_proposal_that_cannot_be_read_is_refused` | "keep everything" |
| the code graph cannot be read | `path_map`: `test_a_code_graph_that_cannot_be_read_refuses_and_records_no_importers` | "no importers", a move |
| the project has no code graph (code intelligence is off in its path map) | `path_map`: `test_a_move_where_code_intelligence_is_off_is_refused_and_writes_nothing` (3), `test_a_split_a_merge_or_an_extract_where_code_intelligence_is_off_is_refused_and_writes_nothing` (3), `test_a_move_among_retirements_is_refused_as_a_whole_where_code_intelligence_is_off`, `test_no_later_stage_moves_what_was_refused_where_code_intelligence_is_off` | "no importers", a move |
| the external references file is there and cannot be read, is not YAML, or is not of the stated shape | `external_references`: `test_a_file_that_is_not_of_the_stated_shape_blocks_and_is_named` (13), `test_a_file_that_cannot_be_read_blocks_and_is_named`, `test_the_function_names_the_defective_file_in_its_message`, `test_a_defective_file_blocks_a_ticket_whose_ids_are_all_records_too` (2), `test_a_listed_id_of_the_decision_registers_form_is_refused` (2) | "no external references", a missing id reported without the defect, a packet |
| every id the ticket declares is an external reference: nothing was read | `external_references`: `test_a_ticket_whose_declared_ids_are_all_external_is_refused` (2), `test_the_function_refuses_a_ticket_whose_declared_ids_are_all_external` | a packet with no mandatory input, a context hash for a close |
| the verdict cannot be read | `verdict`: `test_a_verdict_that_cannot_be_read_moves_nothing` (4) | a pass, a move |
| the backup ref no longer resolves | `migration`: `test_a_backup_ref_that_no_longer_resolves_stops_the_migration` | a move |
| a legacy rule file cannot be read or parsed | `legacy`: the two cases above | a retirement |
| the chat database cannot be read | `legacy`: `test_a_chat_database_that_cannot_be_read_is_not_retired` | a retirement |
| a record cannot be read | `legacy`: `test_a_record_that_cannot_be_read_is_no_proof_of_no_dependency` | "no citer", a retirement |
| a rule file that stays in the tree lies outside `.rulesync/` (a kept legacy rule file) | `legacy`: `test_a_memory_store_a_kept_legacy_rule_file_cites_is_not_retired` (2) | "no citer" about a rule file that was not read, a retirement |
| a kept rule file writes the store's path behind `./`, `/`, `../` or a folder, or one of its ids behind a folder | `legacy`: `test_a_kept_rule_file_cites_the_store_however_it_writes_the_path` (5) | "no citer" because the citation is not written as the proof expects it, a retirement |
| a record that cites the store has no status, or a status nobody knows | `legacy`: `test_a_record_that_still_stands_keeps_the_store` (the rows "no status" and "a status nobody knows") | "it no longer stands", a retirement |
| the ticket's sources are all external and only its dependencies were read | `external_references`: `test_a_ticket_whose_sources_are_all_external_is_refused_beside_dependencies` (3) | a packet that holds no source, a context hash for a close |
| the plan (A4) is not the plan of the path map the verdict is about | `verdict`: `test_a_plan_that_is_not_the_audited_path_maps_plan_is_not_executed` (2) | a pass for the plan, a move |

### Covers → tests

| Item | Files |
|---|---|
| CAP-06.b | `path_map` (the eight actions) |
| CAP-06.c | `unknown` |
| CAP-06.d | `path_map` (importers, references, consumers; the plan's handling; no MOVE, RENAME, SPLIT, MERGE or EXTRACT where code intelligence is off) |
| CAP-15.c | `external_references` (a listed id is accepted and reported as external; an unlisted one, a superseded record and a defective file block; a ticket whose ids are all external is refused, and so is one whose sources are all external beside dependencies that were read) |
| CAP-42.a | `legacy` (import, nothing stays loaded, zero ACTIVE decisions) |
| CAP-42.b | `legacy` (chat database; dependency proof, with a kept legacy rule file as citer, in every form it writes the path or the id, and with every record that still stands as citer; CIT-E; index refresh) |
| CAP-42.c | `legacy` (reachable, disposition) |
| CAP-44.b | `baseline`, `path_map` (A4), `unknown` (packages), `dev_tier` |
| CAP-44.c | `verdict` (the verdict; the plan that is not the audited path map's) |
| CAP-44.d | `migration` |
| CAP-44.e | `legacy` |
| CAP-44.j | `path_map` (native layout) |

## Where the cases can run

- **The code graph.** The path map of the project turns code intelligence on (but for the six cases of DEC-517,
  below), so every case that proposes a move there needs the code graph (W1-16's tool). In a launched worker session that tool cannot build an index: its daemon
  folder `/tmp/gov-cbm-<uid>` is read-only there (measured in this session; `tests/acceptance/W1-20/README.md`
  records the same). **These cases can go green only outside the sandbox; that run is the lead's** (package P-2):
  all of `test_w1_41_migration.py`, all of `test_w1_41_verdict.py` (the two cases of the changed plan among them:
  in the sandbox they stop in `_planned`, at stage A3, with `ADOPT_CODE_GRAPH_UNREADABLE`, before the plan is
  changed; their fixture was only dry-run on a made-up A4 record), in `test_w1_41_path_map.py` every case that
  reaches A3 with a move (the eight actions, importers/references/consumers, the justified native move, A4's
  batches), and `test_an_unknown_artefact_blocks_the_whole_destructive_migration`.
- **Everything else** (baseline, the A3 refusals, unknown artefacts, all of `legacy`, the dev tier) proposes no
  move, or is refused before one is examined. The two kept-rule-file cases and the cases of DEC-552 are among them:
  they run in the sandbox.
- **The six cases of DEC-517 and the three rows of DEC-535 run inside the sandbox.** Their project turns code
  intelligence off, so no code index is built or read: the moves are refused at A3, and the proposal that moves
  nothing needs no code graph.
- **The 45 cases of the ninth success line run inside the sandbox.** They need no code index and no `gitleaks`:
  the record store of the case's own project is loaded, no index is built.
- **b-dev.** A clone of `~/gov-os-workbench/synthetic/b-dev` into the session's temporary folder was made in this
  sandbox (149 tracked files; it tracks `AGENTS.md`, `.cursorrules` and `.windsurfrules`). The two dev-tier cases
  give the clone a path map with code intelligence off and move nothing.
- **Unreadable files.** Two cases take a file's permissions away and are skipped for a user that permissions do
  not hold. git then reports the file as modified, so the refusal may be the dirty tree's; the case holds only
  that the file is named and not retired.
- `gov rebuild` and `gov doctor` are run by cases only in their own temporary project.

## Packages (in full in the designer's return)

| Id | Question | Held meanwhile |
|---|---|---|
| P-1 | How does A3 learn each artefact's action, target and batch: from a proposal the caller gives, or from the tool's own judgement? | the caller's proposal (`--map`); what it does not name is kept |
| P-2 | The sandbox of a launched session cannot build the code index; who runs the move cases? | the lead, outside the sandbox |
| P-3 | Is `rulesync import` the way of the A8 import? Measured: rulesync 24.0.0 imports `.cursor/rules/*.mdc` and `AGENTS.md` (whole, as the root rule) and neither `.cursorrules`, `.windsurfrules` nor `.mcp/tools.json` | the result under `.rulesync/`, not the way |
| P-4 | Who extracts the chat database's "unique knowledge", and what establishes that it is all extracted? | the caller extracts; the tool retires only where a committed record cites the database by path and current content hash |
| P-5 | Does one unknown artefact block all destructive migration, or only actions on itself? | all of it (the contract item's words) |
| P-6 | What must the record show for a move out of a native layout, and who judges "healthy" and "materially better"? | both grounds stated in the proposal and shown in the path map; the A5 auditor reads them |
| P-7 | Does the tool perform the rewrites of references (apart from the move batches), or only flag them? | only that a move batch changes no content, and that the plan names `rewrite` or `flag` for each |
| P-8 | In a project whose path map turns code intelligence off, may an artefact be moved? | held as a refusal (DEC-517, the stricter reading) until the owner answers: A3 refuses a MOVE or a RENAME there and writes nothing |
| P-9 | `gov adopt` without `--lite` stays `NOT_IMPLEMENTED`; does "all twelve Wave 1 commands are implemented" accept that? | W1-07's lists untouched |
| P-10 | Where code intelligence is off, are SPLIT, MERGE and EXTRACT refused as MOVE and RENAME are? | **decided by DEC-535: refused.** One row per action, green as built |
| P-11 | Does a defective external references file block every ticket's context, or only that of a ticket that declares an id the store does not hold? | every ticket (the stricter reading): `test_a_defective_file_blocks_a_ticket_whose_ids_are_all_records_too` (2) |
| P-12 | Is a listed id of the form `DEC-<digits>` refused in every project, or only where it is an entry of the register the project names? | every project, by the form alone: the second row of `test_a_listed_id_of_the_decision_registers_form_is_refused` |
| P-13 | A ticket whose declared ids are all external references (none is a record of the store): is its context refused, or built with a packet that says nothing was read? | refused (the stricter reading): `BLOCKED`, the ticket and the external ids named, the message says that all are external and none was read: `test_a_ticket_whose_declared_ids_are_all_external_is_refused` (2), `test_the_function_refuses_a_ticket_whose_declared_ids_are_all_external` |
| P-14 | A ticket whose sources are all external names, by `depends_on`, a record that is no ticket (W1-24 resolves the ids of `depends_on` as mandatory inputs): is it refused as beside a dependency ticket, or built because a record was read? | refused (the stricter reading; DEC-552: "a dependency that was read is not a source that was read"): the third row of `test_a_ticket_whose_sources_are_all_external_is_refused_beside_dependencies` |
