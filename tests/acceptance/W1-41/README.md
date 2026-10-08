# W1-41 Acceptance Tests — gov adopt --lite and legacy importer

Ticket: `DAEO-cdoi` · Profile: FULL · Covers: CAP-06.b, CAP-06.c, CAP-06.d, CAP-42.a, CAP-42.b, CAP-42.c,
CAP-44.b, CAP-44.c, CAP-44.d, CAP-44.e, CAP-44.j

Written by the Independent Test Designer (MR-3, DEC-069) before implementation, from the ticket's KPI lines, the
Contract items they cite, DEC-006, DEC-090, DEC-137, DEC-449, DEC-454, DEC-488, DEC-499, and the READMEs and code of
the suites the stages stand on. No earlier ticket's test was rewritten.

Run: `env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-41 -q -p no:cacheprovider -rs`

**104 cases in 7 files** (102 without the two `local_only` dev-tier cases). Standard library, PyYAML, pytest, and
W1-07's support. No network, no model.

**This ticket builds the tool. It adopts nothing.** Every case runs `gov adopt --lite` on a project the case
builds itself, file by file, in its own temporary folder, as a git repository of its own. `run_gov` refuses a
project that is this repository, a folder of it, or a worktree of it. Nothing under `governance/project/` of this
repository is read: the temporary project's path map is written from the kernel's schema. Backup ref, rollback
points and archive ref are created by the tool in the temporary project only.

## Red run (before implementation)

At `c96add70`: **80 failed, 23 errors, 1 passed** in 25 s.

- **103 cases are red only because the command is not built**: `gov adopt --lite …` answers `NOT_IMPLEMENTED`
  ("gov adopt is reserved and not built yet"). 80 fail in the case, 23 error in a module fixture that carries one
  adoption through A8 (21 in `test_w1_41_legacy.py`, 2 in `test_w1_41_dev_tier.py`). Among them
  `test_lite_without_a_stage_is_a_usage_error` fails as "exit code 1, expected 2", for the same reason.
- **1 case is green and must stay green**: `test_adopt_without_lite_is_still_reserved` (see "The interface", 1).

No behaviour assertion can be red for a reason of its own before the command exists; every refusing case asserts
that the refusal is the tool's own (`assert_refused` fails on `NOT_IMPLEMENTED`), so none passes by the command's
absence.

## Sources that could not be read

- **S0a-G-13 and G-10** (the ticket's first two sources) are not in the readable tree: `docs/source/` is closed to
  this session and the workbench is not read. **Nothing here is derived from them.**
- The Adoption Protocol v3.0, the Distribution Protocol v1.2 and Framework v4.1.2, which the Contract items cite
  by paragraph, are not in the readable tree either. Where the cases needed more than the Contract's own words,
  the point is in "Settled here" or in "Packages" below.

## Not covered here

The ticket's last two success lines (every adoption-gap exception ends at this ticket's merge; sources that live
outside the repository are in the record store or are recorded as external references) are not derived in this
batch: the lead returns them as a package. No case is written for them.

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
| no move before an A5 verdict (failure 2) | `verdict`: all 17 cases (table above) |
| a failed batch rolls back to its recorded point | `migration`: `test_a_failed_batch_rolls_back_to_its_point_and_the_batches_before_it_stay` |
| moves precede `gov rebuild` | `migration`: `test_the_index_refresh_follows_the_moves` |
| the baseline is measured | `migration`: `test_a_backup_ref_that_no_longer_resolves_stops_the_migration`, `test_a_tree_that_is_dirty_at_a6_is_not_migrated` |

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

### Success 5 — memory store: dependency proof, CIT-E, index refresh [CAP-42.b]

`legacy`: `test_a_memory_store_nothing_cites_is_retired`, `test_the_dependency_proof_is_recorded`,
`test_a_memory_store_an_active_record_cites_is_not_retired` (an edge `depends_on` to a record of the store),
`test_a_memory_store_a_rule_cites_is_not_retired` (a rule under `.rulesync/rules/` that names a file of the store),
`test_a_record_that_is_not_active_does_not_keep_the_store`,
`test_a_record_that_cannot_be_read_is_no_proof_of_no_dependency`,
`test_the_retirement_of_the_memory_store_is_a_cit_e` (a committed record of type `change-execution-record`, the
form of `docs/changes/S2-CIT-E.md`, that names every retired file),
`test_the_index_is_refreshed_after_the_retirement` (`gov doctor`'s `index_freshness` in the temporary project).

In the "not retired" cases the stage's exit code is left open (it may retire the rest and say so, or refuse as a
whole); what is held is that the files stay and the citer is named.

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

### Measured or refused (DEC-449, DEC-454)

| A reading that fails | Case | Never becomes |
|---|---|---|
| no path map in the project | `baseline`: `test_a_project_without_a_path_map_is_not_classified` | "nothing is unknown" |
| the proposal cannot be read | `path_map`: `test_a_proposal_that_cannot_be_read_is_refused` | "keep everything" |
| the code graph cannot be read | `path_map`: `test_a_code_graph_that_cannot_be_read_refuses_and_records_no_importers` | "no importers", a move |
| the verdict cannot be read | `verdict`: `test_a_verdict_that_cannot_be_read_moves_nothing` (4) | a pass, a move |
| the backup ref no longer resolves | `migration`: `test_a_backup_ref_that_no_longer_resolves_stops_the_migration` | a move |
| a legacy rule file cannot be read or parsed | `legacy`: the two cases above | a retirement |
| the chat database cannot be read | `legacy`: `test_a_chat_database_that_cannot_be_read_is_not_retired` | a retirement |
| a record cannot be read | `legacy`: `test_a_record_that_cannot_be_read_is_no_proof_of_no_dependency` | "no citer", a retirement |

### Covers → tests

| Item | Files |
|---|---|
| CAP-06.b | `path_map` (the eight actions) |
| CAP-06.c | `unknown` |
| CAP-06.d | `path_map` (importers, references, consumers; the plan's handling) |
| CAP-42.a | `legacy` (import, nothing stays loaded, zero ACTIVE decisions) |
| CAP-42.b | `legacy` (chat database; dependency proof; CIT-E; index refresh) |
| CAP-42.c | `legacy` (reachable, disposition) |
| CAP-44.b | `baseline`, `path_map` (A4), `unknown` (packages), `dev_tier` |
| CAP-44.c | `verdict` |
| CAP-44.d | `migration` |
| CAP-44.e | `legacy` |
| CAP-44.j | `path_map` (native layout) |

## Where the cases can run

- **The code graph.** The path map of the project turns code intelligence on, so every case that proposes a move
  needs the code graph (W1-16's tool). In a launched worker session that tool cannot build an index: its daemon
  folder `/tmp/gov-cbm-<uid>` is read-only there (measured in this session; `tests/acceptance/W1-20/README.md`
  records the same). **These cases can go green only outside the sandbox; that run is the lead's** (package P-2):
  all of `test_w1_41_migration.py`, all of `test_w1_41_verdict.py`, in `test_w1_41_path_map.py` every case that
  reaches A3 with a move (the eight actions, importers/references/consumers, the justified native move, A4's
  batches), and `test_an_unknown_artefact_blocks_the_whole_destructive_migration`.
- **Everything else** (baseline, the A3 refusals, unknown artefacts, all of `legacy`, the dev tier) proposes no
  move, or is refused before one is examined.
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
| P-8 | In a project whose path map turns code intelligence off, may an artefact be moved? | no case with a move in such a project |
| P-9 | `gov adopt` without `--lite` stays `NOT_IMPLEMENTED`; does "all twelve Wave 1 commands are implemented" accept that? | W1-07's lists untouched |
