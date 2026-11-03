# W2-92 evidence: the record route and the code route in plain-question retrieval (DAEO-n0wb; DEC-995, DEC-1055)

The ticket as built at `448a835a9dca` (lead run 3, DONE; code head `e95eb4ad12ca`), brought up to `w2/integrate` at
`23625eb2aebe` by the merge `ebba014ac355` (D-4b, DEC-1055). The merge's one conflict was the import lines of
`src/gov/retrieval/retrieve.py`: both sides kept (W2-112's `last_outcome` with W2-92's `loader`); no other change to
the ticket's code. `retrieve.py`'s public shape is the branch's (`retrieve(root, query, *, ids, ticket, radius,
batch_size, bundle_budget, continuation, reranker)`), as W2-13 will build on it.

**Verified on:** the merge commit `ebba014ac355` (the store rebuilt there with `--seed`, 2026-11-03); S4 and F1
again on `7f4d519b`, the merge of the test designer's revision `w2/W2-92-tests` at `507df49a68f8` (below), where
`gov accept` passes 30 of 30, 7 of 7 lines. The ticket's code is the same at both (the revision changes only
`tests/acceptance/W2-92/README.md` and `test_w2_92_unchanged.py`).

## The KPI lines and how each is verified

`gov accept` = `PYTHONPATH=<tree>/src bash heavy_slot.sh python3 -m gov.cli.main accept W2-92 --json`, in the
worktree. Unit = `pytest tests/unit/retrieval/test_w2_92_routes.py tests/unit/retrieval/test_w2_92_record_files.py`
(43 cases, all passed at `ebba014ac355`).

| KPI | How it is verified | Command | Result | Verified on |
|---|---|---|---|---|
| S1 the record route | `gov accept` line success-1; unit cases on start ids, titles, the closure join | `gov accept`; unit | pass, 9 of 9; unit pass | `ebba014ac355` |
| S2 the code route | `gov accept` line success-2; unit cases on small pages, the cue gate, one session per process | `gov accept`; unit | pass, 7 of 7; unit pass | `ebba014ac355` |
| S3 a missing or unreadable index or store named per route | `gov accept` line success-3; unit cases on a missing or unreadable index and record store (DEC-1006 P-1, DEC-1019) | `gov accept`; unit | pass, 6 of 6; unit pass | `ebba014ac355` |
| S4 nothing else changes; two runs give one bundle | `gov accept` line success-4; unit `test_a_question_naming_nothing_gets_todays_bundle`; a direct comparison on this tree's store (below) | `gov accept`; unit; the comparison (scratch `/tmp/gov-os-emg-w2-92/cmp_run.sh`) | pass, 9 of 9 (at `ebba014ac355` before the revision: 4 of 9, 5 failed); unit pass; direct comparison: same bundle | `7f4d519b` (`gov accept`); `ebba014ac355` (unit, comparison) |
| S5 W2-61's measure re-run, both figures together | the measure record `docs/research/W2-92-memory-measure.md` (run 2 at `d72c96fc029c`: hit@5 11 of 20, full evidence 13 of 20, control 11 and 11) | measure: D-4b measure 1 | earlier record as cited; re-measured: D-4b measure 1 | `d72c96fc029c` (record); D-4b measure 1 |
| F1 a no-record question gets a different bundle | `gov accept` line failure-1 (the same 9 cases as success-4) | `gov accept` | pass, 9 of 9 (at `ebba014ac355` before the revision: 4 of 9, 5 failed) | `7f4d519b` |
| F2 a whole-graph query or one over the row cap | `gov accept` line failure-2; unit small-page cases | `gov accept`; unit | pass, 6 of 6; unit pass | `ebba014ac355` |
| F3 a missing index reported ok or failing the whole answer | `gov accept` line failure-3; unit missing-index cases | `gov accept`; unit | pass, 6 of 6; unit pass | `ebba014ac355` |
| F4 a figure without the other, or the hidden half read or run | the measure record (§4 gives both figures together; §8: the hidden half neither read nor run) | measure: D-4b measure 1 | earlier record as cited; re-measured: D-4b measure 1 | `d72c96fc029c` (record); D-4b measure 1 |
| S6 a plain question costs about one second (DEC-1065 (4)) | the record route reads the titles the store keeps (`record_titles`), parses no record file; same start ids as before; the route timed cold with stand-ins (below); the cold `gov retrieve` median of ten: the CTO's, on the shared servers | unit `tests/unit/retrieval/test_w2_92_titles.py` (18 cases) with the W2-92 and store unit files (81 cases, `--optin=lifted,breadth`); the timing scripts (below); `gov accept` after the test designer's S6 tests merge | unit 81 passed; the record route 2.97 s → 0.0045 s median of ten; 1,968 records' titles equal both ways; `gov accept` in the launch sandbox at `00a3daa0`: 14 of 15, 1 failed (pre-S6 code: 12 of 15); `gov retrieve` median: CTO | `62013a81`; `00a3daa0` |

`gov accept` totals at `ebba014ac355`: 25 passed, 5 failed, 0 skipped; 5 of 7 lines pass (2026-11-03 15:39-15:41
UTC). At the pre-merge head `448a835a9dca`, run the same day in a clone: 30 passed, 7 of 7 lines. **At `7f4d519b`
(after the revision): 30 passed, 0 failed, 0 skipped, 0 unmapped; 7 of 7 lines pass (2026-11-03 16:24:25-16:25:53
UTC).**

## S4 and F1: red after the merge, from W2-112's new bundle field; the cases revised (P-W2-92-D4B-1 (a))

- **What fails:** the 5 cases mapped to both success-4 and failure-1. They passed at `448a835a9dca` today (30 of 30),
  so the merge brings the red in, not the machine.
- **Its cause, found from pass and fail alone:** a scratch clone of `ebba014ac355` with only W2-112's line
  `"rerank": reranked_by` taken out of the bundle passes 30 of 30. So the 5 cases judge "today's bundle" against
  a reference without W2-112's field `rerank` (who scored and on which device, W2-112's KPI). The engineer has not
  read the cases (DEC-1056).
- **The code meets the line against today's integration code:** on this tree's store rebuilt at the merge, for a
  question naming no record or symbol, the merged code twice and `w2/integrate`'s code once (the main tree at
  `f451207018ce`, whose `src/` equals `23625eb2aebe`'s) give the same bundle, field for field, `rerank` included.
- **Not fixed here:** taking the field out of `retrieve.py` would undo W2-112, and the cases are the test designer's
  (MR-3).
- **The revision (the CTO's P-W2-92-D4B-1, option (a)):** a test designer revised S4/F1's reference on
  `w2/W2-92-tests` at `507df49a68f8` (parent `0024c753aaf6`): the pinned bundles are the integrated code's
  (`w2/integrate` at `23625eb2aebe`), with W2-112's `rerank` field part of the baseline and pinned to its value; a
  planted extra field still fails the 5 cases. Merged into `w2/W2-92` as `7f4d519b`; `gov accept` there: 30 of 30.

## The rebuild and the scoped set

- **Rebuild:** `flock /tmp/gov-os-d4b-rebuild.lock bash rebuild_slot.sh ~/gov-os-worktrees/W2-92 --seed`, 15:38:22 to
  15:39:19 UTC (57 s; the rebuild's own total 51.4 s): ok; lexical, semantic and codeintel recreated. Seed `none`:
  `governance/project/rebuild.yaml` names no `integration_store`, so no warm base was taken.
- **Scoped set:** `select_tests.py <tree> W2-92 DAEO-n0wb` (scoped; core changed `src/gov/retrieval/retrieve.py`;
  86 targets), run as `pytest tests -n auto <its pytest_options> --ignore=tests/acceptance/W2-92` through
  `heavy_slot.sh` (W2-92's own cases are `gov accept`'s, DEC-1056), 15:59:40 to 16:11:09 UTC: **4863 passed, 8
  failed, 8 skipped in 637 s.** The 8 are red again when run alone (8 failed in 244 s), and none is this ticket's:
  the merged tree differs from `w2/integrate` (`23625eb2aebe`) only in the ticket's 16 files, and none of the 8
  reads retrieval code.
  - `tests/acceptance/W1-06/test_w1_06_install_approvals.py::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool`:
    the tool registry's `gov` entry cites DEC-1052, which does not name the tool.
  - `tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written`:
    the launched worker's `PreToolUse:Bash` hook found no `.claude/hooks/pretooluse.py` and refused the probe.
  - `tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit`
    and `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here`:
    `context-reproducibility` has 1 error (DAEO-swdu's mandatory input DEC-798 is SUPERSEDED).
  - `tests/acceptance/W2-59/test_w2_59_hook_lines.py` (1 case) and `test_w2_59_hook_lines_worker_env.py` (3 cases),
    `preToolUse[0]`: the planted project has no `.claude/hooks/pretooluse.py` (W2-59's hook-line cases, red at the
    ticket's base already in the lead's run 1).

## S6: the titles kept in the store (DEC-1065 (4); the DEC-1065 round, 2026-11-03)

**Merged first:** `w2/integrate` at `eb28c40866af` into the branch by `1e29f3cc` (a fast-forward case, no conflict;
built with `git merge-tree` and `git commit-tree`, as the launch sandbox keeps `tests/acceptance/**`, `.tickets/**`
and `.claude/hooks/**` read-only for the engineer, so `git merge` could not check them out; the commit's tree is
`w2/integrate`'s). **The change:** `62013a81`.

- **Where the time went:** `graph_route.start_ids` parsed every record file's frontmatter with PyYAML's pure-Python
  loader in each process, for its `title`, while the store had parsed the same frontmatter at the load and dropped
  the title.
- **What changes:** `store/loader.py` keeps each file record's string `title` in a new table `record_titles (path, id,
  title)`; `graph_route` reads it in one query. The table is outside the store's digest (as the fingerprints row is),
  so a commit's digest is unchanged, and outside `records` (a `title` column there would clash with
  `register_entries.title` in `records/queries.py`'s join). Where a store has no such table (built before this
  change), the route reads the files as before, with `yaml.CSafeLoader` where PyYAML has it. `retrieve.py` is not
  touched (W2-13's this round), nor `semantic.py`, `rerank.py`, `fusion.py`, `ollama.py` (W2-32's).
- **One change of source:** the titles are now `HEAD`'s at the load (the store's), not the working tree's at the
  question. The ids the route matches were already the store's, so titles and ids now come from one commit.
- **The rebuild it needs:** a full `gov rebuild`. `gov rebuild --records` refuses with `STORE_CODE_CHANGED`, as
  `loader.py` is part of the code fingerprint. **Old seeds are refused:** `rebuild/seed.py`'s `schema_version()`
  hashes `loader._TABLES`, which now holds `record_titles`, and the code fingerprint differs as well, so a warm base
  built without the table is refused, named, and the rebuild runs cold. Until the rebuild, the route answers from the
  files with the C loader.
- **Timed with stand-ins only** (no `gov retrieve`, no embedder, reranker or model): a clone of `1e29f3cc` +
  `62013a81` in the sandbox's TMPDIR (its acceptance tests not checked out), its record graph loaded with
  `store.load` alone (4.8 s; digest `9a7c281ee14d…`, 0 invalid); ten cold processes per mode, one plain question,
  1,968 records:

  | Mode | `start_ids` median of ten |
  |---|---|
  | before: the files, pure-Python loader | 2.97 s |
  | a store without the table: the files, C loader | 0.479 s |
  | the store's `record_titles` | 0.0045 s |

  The same start ids in all three modes on five questions (plain, ids and W2 ids, a title, none); all 1,968 records'
  titles equal from the store and from the files, with either loader (844 records have one). A question naming W2
  ids still reads the tickets' files for their W2 id (by a regex, no YAML): 0.008 s, left as it is.
- **Not measured here:** the cold `gov retrieve` median of ten against the target of about 1.2 s: the CTO's, on the
  shared servers, after the full rebuild.

### `gov accept W2-92` at `00a3daa0` (S6's tests merged), in the engineer's launch sandbox, 2026-11-03

Run as `PYTHONPATH=<tree>/src bash heavy_slot.sh python3 -m gov.cli.main accept W2-92 --json` (pass or fail per
line only; the engineer never reads `tests/acceptance/W2-92/`). To tell the sandbox from the change, the same command
ran in a clone of `00a3daa0` with only `src/gov/store/loader.py` and `src/gov/retrieval/graph_route.py` put back to
`1e29f3cc`'s (the code before S6): the same tests, the same sandbox.

| KPI line | S6 code (`00a3daa0`) passed / failed | Code before S6, same sandbox | Reading |
|---|---|---|---|
| success-1 | 0 / 9 | 0 / 9 | the sandbox (same at both) |
| success-2 | 1 / 6 | 1 / 6 | the sandbox (same at both) |
| success-3 | 3 / 3 | 3 / 3 | the sandbox (same at both) |
| success-4 | 0 / 9 | 0 / 9 | the sandbox (same at both) |
| success-6 | **14 / 1** | 12 / 3 | S6 fixes 2 of the 3 the designer showed red on `w2/integrate`; 1 still fails |
| failure-1 | 0 / 9 | 0 / 9 | the sandbox (same at both) |
| failure-2 | 1 / 5 | 1 / 5 | the sandbox (same at both) |
| failure-3 | 3 / 3 | 3 / 3 | the sandbox (same at both) |
| totals | 18 / 27 | 16 / 29 | |

- **What in the sandbox fails them (found with a planted repository of the engineer's own, no test read):** the code
  index cannot be built there: `codeintel`'s runtime folder is fixed at `/tmp/gov-cbm-<uid>/` (`codeintel.DAEMON_BASE`),
  which the launch sandbox keeps read-only (`gov rebuild` answers ok with `codeintel: not_recreated, [Errno 30]
  Read-only file system: '/tmp/gov-cbm-1000/…'`); and the machine's default rebuild lock `/tmp/gov-os-rebuild.lock`
  is read-only there too. These lines passed 30 of 30 at `7f4d519b`, run outside the sandbox.
- **Outside the sandbox (the CTO, on `a01fc5f4`):** 44 passed, 1 failed; every line passes but S6 (14 of 15). The red:
  `test_s6b_a_title_is_the_one_the_store_was_built_with` ("the question names SPEC-0092's title as the store holds
  it ('Cormorant Nesting Protocol') and the record is not in the bundle ... (the bundle holds [])").
- **Traced (2026-11-03, stand-ins only, the test not read):** with a store that has `record_titles`, nothing on the
  question's path reads a title from the working file: `graph_route` reads the table (files only where the table is
  missing), and neither `retrieve.py` nor `retrieve/command.py` reads a title. A planted SPEC-0092 committed as
  'Cormorant Nesting Protocol', loaded, then retitled in the working file:

  | After the change | Start ids for the store's title | Closure evidence |
  |---|---|---|
  | the lexical index refreshed (working file uncommitted, or committed without a store load) | `SPEC-0092` | `SPEC-0092` |
  | the lexical index not refreshed | `SPEC-0092` | `[]`: the lexical facet is `stale`, and `retrieve` takes no chunk from a stale index (`retrieve.py:156`, DEC-342) |

  So the record route matches the store's title; an empty bundle comes from the stale lexical index, not from a
  title. Both are unit cases now (`test_a_title_changed_in_the_working_file_is_matched_as_the_store_holds_it`,
  `test_a_working_file_changed_after_the_index_leaves_no_chunk_to_cite`); 83 unit cases pass. If the red case
  changes the working file without refreshing the lexical index, no change to the titles turns it green; that
  would be `retrieve.py`'s chunk rule (W2-13's file this round) or the case's setup.
- **The one S6 case still red (as first seen in the sandbox):** not known from inside (the runner names no case, by design). It is red with the S6
  code and with the code before it, so it may be the sandbox's as the others, or a reading of S6 the change does not
  meet; `gov accept` outside the sandbox tells which.

