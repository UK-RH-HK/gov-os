# W2-91 (DAEO-a3u2) acceptance tests

Full embeddings: the root files, the governance overlay and `schemas/` are embedded; the hidden half, the generated
copies, the vendored code and `cli/` stay out; the restricted overlay stays restricted; nothing else moves
(DEC-957, DEC-954 Q9c, DEC-388, DEC-694, DEC-381, DEC-856, DEC-887, DEC-820 (d)). The independent test designer
(MR-3) wrote these tests from the ticket's KPI lines, before the implementation and without reading it.

## How the tests pick up the code under test (DEC-732)

- **The repository** is the one the test file sits in: `Path(__file__).resolve().parents[3]`. No worktree path is
  written in the tests. They read three things from it: its path map (`governance/project/path-map.yaml`, from the
  working tree), its tracked files (`git ls-files`) and its history (`git log`, `git show`). They write nothing in it.
- **`gov`** is imported from whatever `PYTHONPATH` the run sets. An autouse fixture fails every case unless the
  imported package lies in `<repository>/src`. The planted rebuilds pass that same folder to their child processes.
  Run it as:
  `PYTHONPATH=<repository>/src python3 -m pytest tests/acceptance/W2-91 -q -p no:cacheprovider`
- **The public interfaces used:**
  - `gov rebuild --json`, run as `python -m gov.cli.main`;
  - the semantic store it writes (`semantic_vector` joined to `lexical_chunk` in `.gov-runtime/store.db`);
  - the pinned path-map check, `gov.check.pathmap.check`.

  No private function is called or patched.
- **The path map's verdict** follows DEC-381 and DEC-388. A file is embedded when at least one namespace holds it
  and every namespace that holds it says exactly `embedded`. Any other value, or no namespace, means not embedded.
  The language is the path map's own: `**` crosses folders, `*` stays inside one folder. The planted rebuilds show
  that the indexer gives vectors by this same verdict.
- **The planted repositories** are built from scratch in pytest's `tmp_path`. They copy two single named files from
  the repository: its path map and `template/.gitleaks.toml`. The embedder is a stand-in for Ollama's HTTP interface
  on the loopback interface. There is no network and no real embedder, and this repository's store is never touched.
  The rebuild cases skip, with the reason, on a machine without `gitleaks` or `sqlite_vec`.

## The base, and why the tests stay right after later merges

- **"Nothing else moves"** is judged over the ticket's own changes, not against a fixed commit:
  - each non-merge commit carrying `Task: DAEO-a3u2` that touches the path map, compared with its first parent;
  - plus any uncommitted change (`HEAD` against the working tree).

  Every comparison runs over the tracked paths of the repository the run is in. If the ticket has no such commit
  and no such change, the base `904bb3a0e7c6` is compared with the working tree.
- **What later merges can and cannot do.** A later `w2/integrate` may add tracked files, other top-level blocks or
  other tickets' namespace changes. None of these makes this case red, because other tickets' commits do not carry
  this ticket's `Task:`.
- **"Code not changed"** is judged the same way: no non-merge commit of this ticket, and no uncommitted change,
  touches `src/`.
- **The other cases** read the repository's path map and tracked files as they stand. A later file under `governance/`,
  `schemas/` or the root has to be embedded. A later file under `fixtures/`, `.claude/`, `.rulesync/` or `cli/` has
  to be left out.

## KPI lines and cases

| KPI line | Tests |
|---|---|
| Success 1: the root files, `governance/**` and `schemas/**` have vectors | `test_root_files_governance_and_schemas_are_embedded` (the path map's verdict for every tracked file in the three sets; each set non-empty; `CLAUDE.md`, `README.md` and `AGENTS.md` tracked); `test_a_rebuild_gives_vectors_exactly_to_the_files_the_path_map_embeds` (this repository's path map in a planted repository, rebuilt: the root, overlay and `schemas/` files have vectors, and the vectors are exactly the files the map embeds) |
| Success 2 / failure 1: what stays out stays out; `schemas/**` gets a namespace of its own | `test_the_hidden_half_generated_copies_vendored_code_and_cli_are_not_embedded` (every tracked file under `fixtures/`, `.claude/`, `.rulesync/`, `template/.rulesync/` and W2-86's vendored parts, the probed `cli/` paths and the path map's `evaluation_sets` hidden patterns); `test_schemas_has_a_namespace_of_its_own_and_cli_stays_out`; the planted rebuild (none of the planted out-files has a vector); `test_failure_1_an_embedded_file_that_stays_out_is_refused` (4 cases) |
| Success 3 / failure 2: the overlay stays restricted | `test_the_overlay_stays_restricted_and_its_export_denied` (every namespace that holds a tracked `governance/` file says `restricted` and `denied`); `test_the_indexer_verdict_ignores_sensitivity_and_export_policy` (a planted rebuild: four namespaces that differ only in those fields get the same verdict as their `embedding_policy`); `test_failure_2_the_overlay_unrestricted_is_refused` (2 cases) |
| Success 4 / failure 3: the two values only, exactly one namespace each, the indexer's code unchanged | `test_every_namespace_states_one_of_the_two_values`; `test_every_tracked_path_is_in_exactly_one_namespace` (`gov.check.pathmap.check`); `test_this_ticket_changes_no_code`; `test_failure_3_a_third_value_is_refused`; `test_failure_3_a_path_in_no_namespace_or_in_two_is_refused` (a planted repository) |
| Success 5: nothing else moves | `test_nothing_else_moves`; `test_success_5_a_verdict_moved_elsewhere_is_refused` |

The `test_failure_*` and `test_success_5_*` cases each plant one fault, by changing one namespace of the
repository's own path map in memory. Each shows that its check refuses that fault, so the green cases above are
not vacuous.

## What is not tested here

- **The export half of success 3** ("the export path still refuses the overlay, with a planted export case"). On
  `w2/integrate`, no public command or module reads a namespace's `export_policy`. The only code that reads it is
  the schema check, `gov.config.path_map_schema`. No stand-in is invented here. DEC-1013 (TD-1 (a)) dropped this
  clause from success 3; an export command that refuses a `denied` namespace is Wave 3 row W3-P18.
- **The vector counts per set in success 1**, which are read from the clone's store; **success 6** (W2-61's
  re-measure); and **failure 4** (a figure reported alone, or the hidden half read or run). These need the real
  embedder and built stores. They belong to the lead's measurement record, `docs/changes/W2-91-evidence.md`.

## Red at the base `904bb3a0e7c6`

The run gave 3 failed and 16 passed.

- **`test_root_files_governance_and_schemas_are_embedded` fails.** 179 tracked files are not embedded: 8 root
  files, 166 under `governance/` and 5 under `schemas/`. At the base, `root-files`, `project-overlay` and
  `carried-code` say `not embedded`.
- **`test_schemas_has_a_namespace_of_its_own_and_cli_stays_out` fails** with `['carried-code']`, because
  `schemas/**` and `cli/**` share one namespace.
- **`test_a_rebuild_gives_vectors_exactly_to_the_files_the_path_map_embeds` fails.** None of the 12 planted root,
  overlay and `schemas/` files has a vector.
- **The other 16 pass at the base.** The base already meets those lines (what stays out, the overlay's two fields,
  the two values, one namespace each, no code change, nothing else moved), and the refusal cases show that the
  checks refuse a planted fault. They have to stay green after the change.

These tests were also run against an in-memory stand-in of the change, which was never written to the tree:
`root-files` and `project-overlay` say `embedded`, and `carried-code` is split into `cli/**` (not embedded) and
`schemas/**` (embedded). With that stand-in, every check is empty and the planted rebuild's vectors are exactly the
embedded files.

## An earlier test these KPIs make red

`tests/acceptance/W2-86/test_w2_86_kernel_template_embedding.py::test_guard_outside_template_every_verdict_as_at_the_base`
compares every verdict outside `template/` with W2-86's base `9dc5288161c4`. DEC-957 embeds the root files,
`governance/**` and `schemas/**`, all of them outside `template/`, so that case turned red. It was revised under
DEC-1013 TD-2 (a) in commit `a31d314e5091`, which added its path to this ticket's paths. DEC-957's three newly
embedded sets are now left out of its comparison: the tracked root files, every tracked file under `governance/**`
and every tracked file under `schemas/**`. The sets are defined the same way as `newly_embedded_area` in
`w2_91_support.py`. Every other tracked path outside `template/` is still compared with the base, in both
directions, and the case fails if nothing is left to compare.

## Revised to D-7's scope (DEC-1052 M-4, DEC-1055 (2) and (3), DEC-1066 (3))

DEC-1055 (2) says W2-91 lands as built and D-7 then narrows it. D-7's path map (`9c080788`) makes three changes
these tests notice:
- the overlay's record folders, `governance/project/orchestration/{closes,nightly,sessions,reviews}/**`, move to a
  namespace of their own, `orchestration-records`, which is not embedded;
- `tests/**` is not embedded;
- `fixtures/` is named by its sub-folders, and `fixtures/evaluation/**` gets its own namespace,
  `evaluation-fixtures`, which is not embedded and not indexed.

Three cases turned red and were revised. The other cases are unchanged.

- **`test_root_files_governance_and_schemas_are_embedded`.** Success 1 now judges DEC-957's sets less the
  overlay's record folders. That is `embedded_after_d7` in `w2_91_support.py`, with the folders written there as
  `OVERLAY_RECORDS`, as the decision words them. The case also requires every tracked file in those folders to be
  not embedded, and the folders to hold at least one tracked file.
- **`test_a_rebuild_gives_vectors_exactly_to_the_files_the_path_map_embeds`.**
  - The overlay plant under `sessions/` moved from the in-files to the controls. The case requires it to have a
    chunk and no vector.
  - An embedded overlay plant takes its place in the in-files: `governance/project/orchestration/tools/planted.md`.
  - The `fixtures/` plant sat in a sub-folder the path map no longer names, so it was in no namespace. There are
    now two plants, `fixtures/evaluation/planted/sample.md` and `fixtures/brownfield/planted/sample.md`. Both must
    stay without a vector.
- **`test_failure_1_an_embedded_file_that_stays_out_is_refused`.** The first row's plant moved to
  `fixtures/evaluation/planted/sample.md` for the same reason. It still shows that a `fixtures/` file embedded is
  refused.

`newly_embedded_area` is left unchanged. `test_nothing_else_moves` judges this ticket's own steps by the scope they
were made under, and W2-86 case 3 shares the definition.

Each revised case is green on `emg/d7`. In a clone of `emg/d7`, each of these plants turned it red:
- `project-overlay` not embedded: success 1 (209 files) and the rebuild;
- `orchestration-records` embedded: success 1 (40 record files embedded) and the rebuild (the session plant has a
  vector);
- `governance/project/orchestration/tools/**` moved into `orchestration-records`: success 1 (14 files) and the
  rebuild;
- `evaluation-fixtures` removed: the rebuild and failure 1's first row (the plant in no namespace).

The D-7 review's F5 (`e44d6732`) moves `docs/research/EXP-003/w2-15a/raw/**` into `evaluation-sources`. These tests
do not name that folder, and need not. It is outside every set W2-91 judges: the root files, `governance/`,
`schemas/`, and what stays out. The rebuild's `docs/planted.md` control lies in `docs/*`, which is still embedded.
W2-86 case 3 holds the folder in its cut.

## KPI map after D-4's cut (DEC-1061)

Regenerated in round 2 of the cut (DEC-1061; the review's F3, F4): each line of the ticket's `kpis:` is placed
by its own words (or by the designer, or by part A's row for that line), never by the README's layout; each
case named here runs in the full run, with every row of a class the line names; tier 2's cap then cut only
the rest. The rest stay built: `breadth` (`tests/optin-lifted*breadth*.txt`, `--optin=breadth`) and, for the
switched-off features, `lifted` (the other `tests/optin-lifted*.txt`, `--optin=lifted`). The placement is data
(`placement.json`, with the designer's `overrides.json`), checked by code against the default collection.

Cases: 15 in the full run, 4 in `breadth`, 0 in `lifted`.

| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |
|---|---|---|
| S1: After a rebuild with the embedder, the tracked root files (CLAUDE.md, README.md, AGENTS.md and the rest the root-files namespace holds), every ... | `test_w2_91_full_embeddings.py::test_root_files_governance_and_schemas_are_embedded`, `test_w2_91_full_embeddings.py::test_a_rebuild_gives_vectors_exactly_to_the_files_the_path_map_embeds` | the ticket's words |
| S2: What stays out stays out: fixtures/** (the hidden half), .claude/** and .rulesync/** (generated copies), template/.rulesync/** and the vendored... | `test_w2_91_full_embeddings.py::test_the_hidden_half_generated_copies_vendored_code_and_cli_are_not_embedded`, `test_w2_91_full_embeddings.py::test_schemas_has_a_namespace_of_its_own_and_cli_stays_out` | the ticket's words |
| S3: The restricted overlay stays restricted: governance/** keeps sensitivity restricted and export_policy denied, and the ticket shows from the cod... | `test_w2_91_full_embeddings.py::test_the_overlay_stays_restricted_and_its_export_denied`, `test_w2_91_full_embeddings.py::test_the_indexer_verdict_ignores_sensitivity_and_export_policy` | the ticket's words |
| S4: The path map states it in its two valid values only, every tracked path matches exactly one namespace, and the indexer's code is not changed [D... | `test_w2_91_full_embeddings.py::test_every_tracked_path_is_in_exactly_one_namespace`, `test_w2_91_full_embeddings.py::test_every_namespace_states_one_of_the_two_values`, `test_w2_91_full_embeddings.py::test_this_ticket_changes_no_code` | the ticket's words |
| S5: Nothing else moves: for every tracked path outside the newly embedded sets, the embedding verdict is the same at the head as at the base; the v... | `test_w2_91_full_embeddings.py::test_nothing_else_moves` | the ticket's words |
| S6: W2-61's measure is re-run on the visible half, control at the base and the head, both figures together (hit@5 against CAP-10's floor of 85 and ... | `test_w2_91_full_embeddings.py::test_the_hidden_half_generated_copies_vendored_code_and_cli_are_not_embedded` | the ticket's words |
| F1: A file under fixtures/, .claude/, .rulesync/ or cli/ embedded. | `test_w2_91_full_embeddings.py::test_the_hidden_half_generated_copies_vendored_code_and_cli_are_not_embedded` | the ticket's words |
| F2: The overlay's sensitivity or export policy changed, or the overlay exported. | `test_w2_91_full_embeddings.py::test_the_overlay_stays_restricted_and_its_export_denied` | the ticket's words |
| F3: A namespace with a value other than embedded or not embedded, or a tracked path in no namespace or in two. | `test_w2_91_full_embeddings.py::test_every_tracked_path_is_in_exactly_one_namespace`, `test_w2_91_full_embeddings.py::test_every_namespace_states_one_of_the_two_values` | the ticket's words |
| F4: A figure of the measure reported without the other, or the hidden half read or run. | `test_w2_91_full_embeddings.py::test_the_hidden_half_generated_copies_vendored_code_and_cli_are_not_embedded` | the ticket's words |
