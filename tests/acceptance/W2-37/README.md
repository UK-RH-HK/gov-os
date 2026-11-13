# W2-37 acceptance tests (DAEO-6n5k): `gov impact`

A fresh independent test designer (MR-3, DEC-136) wrote these tests before the implementation. They come from the
ticket's KPI lines and its sources: CAP-33 (its acceptance line and covers CAP-33.a, .b, .e, .f, .g), the W2-37
card in `docs/plan/WAVE_2_WBS.md` §2, the list rows W2-L319, W2-M056, W2-M150, W2-M285 and W2-M320, the S0b2 glue
items G-16 and G-24 (`docs/plan/WAVE_2_TRIAGE.md`, `docs/plan/WAVE_1_WBS.md` §5–6, W2-L322 with DEC-388), and the
decisions DEC-167, DEC-391 (with DEC-393), DEC-035, DEC-105, DEC-309, DEC-466, DEC-500, DEC-674, DEC-680, DEC-747,
DEC-221, DEC-462, DEC-136 and DEC-732. The profile is FULL (DEC-221): every KPI line's success and failure, thoroughly,
with no combinatorial expansion. Every covers id has at least one test.

**81 cases** (65 test functions) in eleven files, a support module and a conftest. 13 cases are `local_only`.
With the second batch (the first review's findings, below): **96 cases** (75 test functions) in twelve files,
20 of them `local_only`. With the third batch (the second review's findings, below): **115 cases** in thirteen files,
21 of them `local_only`.

## How the suite runs, and the code it runs (DEC-732)

From this worktree's root:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -rs

- **This worktree's code.** The `PYTHONPATH` in the command makes the suite import this worktree's `gov`. Every
  process a case starts gets its environment from `w2_37_support.child_env`, which sets `PYTHONPATH` to this
  worktree's `src/` (`SRC`, found from the support file's own place), a throwaway `HOME`, `TMPDIR` and runtime
  directory. `GOV_ROLE` and `GOV_TICKET` are not passed on. A reader checks it with
  `test_w2_37_code_under_test.py`, which asserts that `gov.__file__` in a started process lies under `SRC`.
- **Public interfaces only.** No case reads `src/`.
  - `gov impact` (`python -m gov.cli.main impact`), through its `--json` envelope (API-0002).
  - `gov closure --json` (DEC-391): the depth a radius gives, and the records it reaches.
  - `gov.store.load(root)` and `gov.codeintel.index(root)` (with `gov.codeintel.callers` as the premise check), to
    build the record store and the code index of a temporary repository, as the W1-20 suite does. `gov impact` is
    never expected to build either (DEC-391 DP-4: a closure never builds the store or the code index).
  - `gov check --json`, for row W2-M056.
- **Nothing is written in this worktree.** Each project is a temporary git repository built from scratch under
  pytest's temporary folder. Single named files of this checkout are read: two kernel schemas and the path-map
  schema, the one check declaration `core-claims.yaml`, the change skill and its copy, the readiness dimensions,
  `template/.gitleaks.toml` and this checkout's `docs/DECISION_REGISTER.md` (all read-only). Nothing is copied from
  `governance/project/`. No dev tier is used: no KPI line of this ticket names one.
- **Two search paths.** Most cases run with `git` alone on `PATH` (`bare`): the code tool is not there, so the code
  graph cannot be read, and they run on any machine and in a worker's sandbox. The `local_only` cases use the
  session's own `PATH` and run the real `codebase-memory-mcp` and `gitleaks` (skipped when either is missing).
- **The `local_only` cases cannot run inside a worker's sandbox** (P-W2-38): there `/tmp/gov-cbm-<uid>` is
  read-only and `gov.codeintel.index` fails with `OSError: [Errno 30] Read-only file system`. The lead runs them
  outside it. The tool's daemon folders of this suite's repositories are removed at the end of the session, as
  W1-20 does.
- **Deterministic, no network.** Fixed authors, dates and trailers. About 2 s while `gov impact` is missing.

## The interface the tests assume

The sources fix the command's name (`gov impact`, CAP-33.g, DEC-167), the five kinds, the two graphs, the radius
(R0 to R3+, DEC-035) and the depth it implies (DEC-391). They do not fix the output's form. The tests take the
following, named once in `w2_37_support.py` ("The interface the tests assume") so that a package that renames a key
changes one line. **Package P-6** asks for it to be confirmed.

```
gov impact [--json] [--root <path>] [--out <path>] <change>...       an impact assessment, and the CIT-P
gov impact [--json] [--root <path>] --compare <CIT-E path>           the CIT-E checked against its CIT-P
```

A `<change>` is a record id, a symbol name, or one plain-language question.

`result` of an assessment:

| Key | What the tests hold it to |
|---|---|
| `change` | The stated change: a list of maps, each with `id` and `graph`, `deletable` (G-24) and `governance` (W2-M150). The stated change itself is not listed in `affected` (reading R1). |
| `radius` | `R0`, `R1`, `R2`, `R3` (or `R3+`). |
| `depth` | A whole number: the depth the radius implies, equal to `gov closure --radius <n>`'s `depth`. |
| `depth_source` | Where the depth of that radius comes from (W2-L319). |
| `affected` | A map of exactly five lists: `specifications`, `decisions`, `tickets`, `tests`, `code`. Each item is a map with `id` and `graph` (`record` or `code`): the graph it came from. |
| `graphs` | `{"record": ..., "code": ...}`: `ok` when that graph was read in full and is current; anything else says what was wrong. |
| `complete` | `false` whenever a graph was missing, stale or unreadable. |
| `gaps` | A list of maps with `id` (and a reason): what lies beyond the depth or could not be resolved. |
| `proposal` | The CIT-P's frontmatter: the shared frontmatter (common.schema.json) with `type: change-impact-proposal`. |
| `options` | For a change to a closed specification: DEC-105's three options, each a map with `option` and `cost`. |
| `findings` | A list of maps with `code`; an in-place edit of a closed specification gives a code holding `IN_PLACE`. |

`--out <path>` writes the CIT-P as a record file: frontmatter valid for `change-impact-proposal`, with `change`,
`radius`, `depth` and `affected` (five lists of ids), and nothing else is written. `--compare` gives `proposal` and
`execution` (the two ids), `matches` (true or false) and `differences` (each with `id` and `only_in`: `proposal` or
`execution`).

A refusal is `ok: false` with an `error.code`, exit code not 0, no traceback, and an error that names what it
refuses. A command-line usage error (no change at all) is a refusal too.

## Readings taken

- **R1. The stated change is not one of the affected items.** It is named in `change`. (`test_a_decision_nothing_links_is_deletable_and_affects_nothing` needs it.)
- **R2. The five kinds.** Records of type `specification` and `capability` are specifications; `decision` and
  register entries (W2-03) are decisions; tickets (`type: task`, under `.tickets/`) are tickets; a record that names
  an affected record by a `tests` edge is a test (the fixture's `TR-0001` is of type `evidence`). From the code
  graph, a symbol defined in a test file (`tests/`) is a test and any other symbol is code. Package P-6.
- **R3. The CIT-P "raised" is the result's `proposal` and, with `--out`, a record file.** `gov impact` is a read
  command (the brief), so the declared output is standard output and the one file `--out` names.
- **R4. "Says it is incomplete"** is either a result with `complete: false` and `graphs.<graph>` not `ok` (and the
  word `stale` where the graph is stale), or a refusal whose error names the graph (`record`/`store` or `code`). A
  report that reads the changed state as it is now and lists the late item is accepted too: nothing is dropped.
- **R5. G-16, the id mapping.** A record's typed edge whose target is no record but a symbol of the code index
  joins the two graphs (DEC-391 leaves such an edge `UNRESOLVED`, and follows no record-to-symbol edge). From the
  symbol, callers and callees are followed as `gov closure` follows them. Back the other way, a symbol's change
  reaches the records that name it. A mention in prose is no edge (DEC-391: no text scan). Package P-3.
- **R6. KPI 2.** The CIT-E names its CIT-P by id in `proposal` (as `docs/changes/S2-CIT-E.md` does); both carry the
  five lists in `affected` in their frontmatter (the kernel schemas allow keys beyond the shared frontmatter). The
  CIT-P is found through the record store. Package P-2.
- **R7. KPI 3.** The question is one argument of `gov impact`; it gives the same assessment as the id it names.
- **R8. G-24, the deletable-class join.** "Deletable" is the S0b2 query class (W2-L322) whose code half the code
  index answers as dead code (W1-16). An item is deletable only when neither graph has anything that depends on it
  (no caller, no record edge naming it); what it depends on itself does not count. A change nothing depends on
  has a lower radius than one that reaches all five kinds. Package P-3.
- **R9. A closed specification** is a `specification` record with `status: CLOSED`. No source spells the status.
  Package P-5.
- **R10. W2-M150.** `change[].governance` is true when the item's path lies in a namespace whose `memory_class` is
  `governance` (path-map.schema.json), false otherwise.
- **R11. W2-L319.** `depth_source` names an owner decision of this repository's register (`**Status:** ACCEPTED
  (owner`), not DEC-035 or DEC-391, or a measurement file under `docs/`. Package P-2.

## KPI lines → tests, and why each is red today

The red reasons below are what this suite printed at the commit that added it: **3 failed, 7 passed, 71 errors,
0 skipped.** Every error is at setup, in the session fixture `built`, with one reason: *"gov impact is not built:
`gov --help` lists no `impact` command, and `gov impact --help` exits 2: gov: error: argument <command>: invalid
choice: 'impact'"*. The 13 `local_only` cases are among them: their fixtures ask for `built` before they build a
code index, so in a worker's sandbox they show the same reason today (once the command exists, they need a run
outside the sandbox, P-W2-38).

### KPI 1: a decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285]

| Test | Holds | Today |
|---|---|---|
| `test_w2_37_proposal.py::test_a_decision_change_lists_each_linked_record_once_under_its_kind_from_the_record_graph` (5) | SPEC-001, CAP-901, DEC-002, PROJ-ab01 and TR-0001 (edges both ways, one hop) each listed once, under its kind, `graph: record` | error: not built |
| `…::test_the_change_is_named_as_the_stated_change` | `change` is DEC-001, from the record graph | error: not built |
| `…::test_a_decision_that_is_an_entry_of_the_register_is_a_stated_change` | DEC-070, a register entry (W2-03): its ticket is listed | error: not built |
| `…::test_nothing_the_graphs_do_not_link_is_listed` | Unlinked records are not listed | error: not built |
| `…::test_no_list_is_cut_short` | 30 specifications and 30 tickets of DEC-003, all listed | error: not built |
| `…::test_two_changes_together_list_what_each_lists` | Two changes together drop nothing either lists alone | error: not built |
| `…::test_the_radius_gives_the_depth_gov_closure_gives_for_it` | `depth` equals `gov closure --radius <n>`'s depth | error: not built |
| `…::test_the_list_holds_every_record_gov_closure_reaches_at_that_depth` | No record `gov closure` reaches at that depth is dropped | error: not built |
| `…::test_an_item_beyond_the_depth_is_a_gap_and_the_report_is_not_complete` | SPEC-002 (two hops): listed when the depth reaches it, else a gap and `complete: false` | error: not built |
| `…::test_the_assessment_is_a_change_impact_proposal` | `proposal` has the shared frontmatter and type change-impact-proposal (CAP-33.a) | error: not built |
| `…::test_the_same_change_gives_the_same_assessment` | Two runs, the same result | error: not built |
| `…::test_out_writes_the_proposal_as_a_cit_p_record` | `--out` writes a CIT-P record whose change, radius, depth and five lists are the result's | error: not built |
| `test_w2_37_code_graph.py` (7, `local_only`) | The symbol DEC-001 names is listed under `code`, `graph: code` (G-16); the record side beside it; callers and callees within the depth (the test function under `tests`); both graphs `ok`; a symbol's change reaches the records that name its callers; prose is no link; every item traced to its graph | error: not built |
| `test_w2_37_command.py::test_gov_lists_an_impact_command` | `gov --help` lists `impact`; its help names `--json`, `--root`, `--compare`, `--out` (W2-M285) | **failed**: `gov --help` lists no `impact` command |

### The failure behaviour

| Test | Holds | Today |
|---|---|---|
| `test_w2_37_incomplete.py::test_without_a_record_store_the_report_is_not_complete` | No store: incomplete, the record graph named | error: not built |
| `…::test_an_unreadable_record_store_is_said` | The store's database overwritten: as above | error: not built |
| `…::test_a_stale_record_store_is_said_and_never_complete` | A ticket committed after the load: listed, or incomplete with the record graph `stale` | error: not built |
| `…::test_an_unreadable_code_graph_is_said_and_the_record_side_still_given` | No code tool on PATH: incomplete, the code graph named; the record side still listed; w37_apply listed or a gap | error: not built |
| `…::test_a_code_graph_never_built_is_said` (`local_only`) | Tool present, no index: incomplete, the code graph named | error: not built |
| `…::test_a_stale_code_graph_is_said_and_never_complete` (`local_only`) | A caller committed after the index: listed, or incomplete with the code graph `stale` | error: not built |
| `test_w2_37_command.py::test_an_unknown_id_is_refused_not_answered_with_an_empty_impact` | NOPE-0001: refused, named | error: not built |
| `…::test_a_known_id_beside_an_unknown_one_is_refused_and_the_unknown_one_named` | DEC-001 with NOPE-0002: refused, NOPE-0002 named | error: not built |
| `…::test_a_malformed_change_is_refused` (3) | `""`, blanks, `???`: refused | error: not built |
| `…::test_no_change_at_all_is_refused` | No change: refused, no traceback | error: not built |
| `…::test_gov_impact_writes_nothing` | After an assessment, a question and a refusal: every file (store included) and git's HEAD, refs, stash and status unchanged | error: not built |
| `…::test_out_writes_the_named_file_and_nothing_else` | `--out` adds the one file it names | error: not built |

### KPI 2: after apply or archive, the CIT-E record matches the proposal or lists the differences [CAP-33 acceptance; the ticket cites W2-L319]

| Test (`test_w2_37_execution.py`) | Holds | Today |
|---|---|---|
| `test_an_execution_record_that_agrees_with_its_proposal_is_reported_as_matching` | `matches: true`, no differences, both ids named | error: not built |
| `test_the_order_of_the_lists_does_not_matter` | The same items in another order match | error: not built |
| `test_an_item_proposed_and_not_done_is_a_listed_difference` | DEC-002 left out: `matches: false`, one difference, `only_in: proposal` | error: not built |
| `test_an_item_done_and_not_proposed_is_a_listed_difference` | SPEC-099 added: one difference, `only_in: execution` | error: not built |
| `test_every_difference_is_listed` | Four differences across three kinds, each with its side | error: not built |
| `test_an_execution_record_that_lists_nothing_never_matches` | No lists: refused or `matches` not true | error: not built |
| `test_an_execution_record_without_its_proposal_is_refused` (3) | No `proposal` key, an unknown CIT-P, a proposal that is no CIT-P: refused, named | error: not built |
| `test_a_record_that_is_no_execution_record_is_refused` | `--compare` on the CIT-P itself: refused | error: not built |
| `test_a_missing_execution_record_is_refused` | No such file: refused, named | error: not built |
| `test_comparing_writes_nothing` | Nothing changes | error: not built |
| `test_the_proposal_gov_impact_writes_is_what_the_execution_record_is_checked_against` | KPI 1 then KPI 2: the `--out` CIT-P and a CIT-E recording what it lists match | error: not built |

### KPI 3: "What's the impact of X?" in plain language runs `gov impact` [CAP-33.g, DEC-167]

| Test | Holds | Today |
|---|---|---|
| `test_w2_37_question.py::test_a_plain_language_question_gives_the_assessment_of_the_id_it_names` (3) | Three phrasings (one with a typographic apostrophe) give DEC-001's assessment | error: not built |
| `…::test_a_question_about_an_unknown_id_is_refused_and_names_it` | DEC-999: refused, named | error: not built |
| `…::test_a_question_that_names_no_change_is_refused` (2) | No subject; not about a change: refused | error: not built |
| `…::test_a_plain_language_question_about_a_symbol` (`local_only`) | A question about w37_helper gives its assessment | error: not built |
| `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question` (2) | **Outside the ticket's paths (P-1):** the change skill's impact-assessment section, template and copy, runs `gov impact` | **failed**: the section names `gov closure` only (Wave 1 form) |
| `…::test_regression_the_skill_says_the_question_triggers_the_impact_assessment` (2) | CAP-33.f (W1-35): the section says the question triggers the assessment, DEC-167 | green (regression) |

### KPI 4: the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join)

| Test | Holds | Today |
|---|---|---|
| G-16: `test_w2_37_code_graph.py` (7, `local_only`), and `test_w2_37_incomplete.py::test_an_unreadable_code_graph_is_said_and_the_record_side_still_given` | Reading R5 (above) | error: not built |
| G-24: `test_w2_37_deletable.py::test_a_decision_nothing_links_is_deletable_and_affects_nothing` | DEC-050: `deletable: true`, nothing affected | error: not built |
| `…::test_a_decision_others_depend_on_is_not_deletable` | DEC-001: `deletable: false` | error: not built |
| `…::test_the_radius_of_a_deletable_change_is_below_that_of_a_wide_one` | radius(DEC-050) < radius(DEC-001) | error: not built |
| `…::test_a_symbol_nothing_calls_and_no_record_names_is_deletable` (`local_only`) | w37_orphan (has a callee, no caller, a prose mention only): deletable | error: not built |
| `…::test_a_symbol_nothing_calls_but_a_record_names_is_not_deletable` (`local_only`) | The join: w37_named_only is dead code to the code graph, but DEC-051 names it: not deletable, DEC-051 listed | error: not built |
| `…::test_a_called_symbol_is_not_deletable` (`local_only`) | w37_helper: not deletable | error: not built |

### The list rows (re-checked against the code, DEC-718)

| Row | Test | Holds | Today |
|---|---|---|---|
| W2-M285 | KPI 1 and KPI 3 above | `gov impact` returns an impact assessment for a stated change | not met: no command |
| W2-M150 | `test_w2_37_rows.py::test_governance_paths_are_the_path_maps_not_fixed_prefixes` (2) | `policy/DEC-010.md` and `governance/notes/DEC-011.md`: `governance` follows the path map, both ways round. The close command's part is package P-4 | error: not built |
| W2-M320 | `…::test_a_change_to_a_closed_specification_gives_the_three_costed_options` | DEC-105's three options, each with a cost (CAP-33.e) | error: not built |
| | `…::test_an_unedited_closed_specification_is_not_flagged_as_edited_in_place` | No `IN_PLACE` finding without an edit | error: not built |
| | `…::test_an_edit_in_place_of_a_closed_specification_in_the_working_tree_is_flagged` | An uncommitted edit of SPEC-300 (CLOSED) is flagged | error: not built |
| | `…::test_an_edit_in_place_of_a_closed_specification_in_a_commit_is_flagged` | A committed edit (as a-dev `f59aa0e`) is flagged | error: not built |
| | `…::test_an_edit_of_an_open_specification_is_not_flagged` | A draft's edit is not flagged | error: not built |
| W2-L319 | `…::test_the_depth_of_a_radius_comes_from_an_owner_decision_or_a_measurement` | `depth_source` is an owner decision (not DEC-035 or DEC-391) or a measurement under `docs/`. **Stays red after the build until the owner decides (P-2)** | error: not built |
| W2-M056 | `test_w2_37_regressions.py::test_regression_a_taxonomy_change_without_a_linked_cit_e_fails_a_check` (2) | **Already met** (W1-26, DEC-309): `gov check --json` flags the changed `readiness-dimensions.yaml` red (`core-claims`, `TAXONOMY_CHANGE_NO_CITE`) without a CIT-E, and not with a linked one | green (regression) |

### Covers ids

| Covers | Tests |
|---|---|
| CAP-33.a (CIT-P and CIT-E records) | `test_w2_37_regressions.py::test_regression_the_kernel_states_both_change_record_types` (2, green); `test_the_assessment_is_a_change_impact_proposal`, `test_out_writes_the_proposal_as_a_cit_p_record`, `test_w2_37_execution.py` |
| CAP-33.b (impact over both graphs; radius → profile) | `test_w2_37_proposal.py`, `test_w2_37_code_graph.py`, `test_w2_37_incomplete.py`, `test_w2_37_deletable.py`. The profile from the radius is W2-38's (CAP-53.b) |
| CAP-33.e (three costed options on a closed specification) | `test_w2_37_rows.py` (W2-M320 cases) |
| CAP-33.f (Wave 1: the question triggers the assessment) | `test_w2_37_skill_routing.py::test_regression_…` (2, green) |
| CAP-33.g (Wave 2: the question runs `gov impact`) | `test_w2_37_question.py`; `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question` (P-1) |
| DEC-732 | `test_w2_37_code_under_test.py` (green) |

## Second batch: the first review's findings (DEC-136, DEC-413)

A fresh independent test designer added these after the implementation, from the review's findings F1, F2, F3, F6
and F8, passed on as described behaviours (DEC-136). Every case is in `test_w2_37_review_findings.py`. No earlier
case was changed. They are built on the suite's fixtures (`project`, `repo`, `indexed_own`, `built`, `tools`) and its
support module; behaviour 4 builds two temporary repositories of its own. The success half of each behaviour is
there too (green today), or is an existing case named below.

The red reasons are what this run printed at the commit that added the batch, with `gov impact` built: **9 failed,
68 passed, 19 errors** over the whole suite. The 81 earlier cases keep the results they had (the three known reds,
66 passed, 12 `local_only` errors at setup). Of the 15 new cases, 6 fail, 2 pass (success halves) and 7 are
`local_only`. Here those 7 error at setup with `OSError: [Errno 30] Read-only file system: '/tmp/gov-cbm-<uid>/…'`
(P-W2-38); the lead runs them outside the sandbox, and the reason expected there is given in the table.

| # | Behaviour | Test (`test_w2_37_review_findings.py`) | `local_only` | Red reason |
|---|---|---|---|---|
| 1 | A record graph that does not match the working tree is never reported current (reading R4; `gov closure` names such paths under `uncommitted`, DEC-391 DP-7) | `test_a_record_graph_that_does_not_match_the_tree_is_never_reported_current` (3: a ticket implementing DEC-001 added and not committed; CAP-901's edge removed and not committed; the store loaded on `main`, then the repository switched to the older branch `older`, where the ticket is absent and the edge present). Without the code tool: the record side alone | no | **failed**: "`graphs.record` says 'ok' although that graph was not". The listing is the store's: the new ticket is missing, CAP-901 is still listed, and after the switch `main`'s ticket is listed |
| | | `test_with_both_graphs_a_record_graph_that_does_not_match_the_tree_is_never_complete` (2: the ticket added and not committed; the branch switch, with the code index built again on `main` first). With a current code graph, `complete` turns on the record graph | yes | expected: `graphs.record` says `ok` and `complete` is true while the listing misses the new ticket (or lists `main`'s) |
| | Success | `test_a_store_loaded_from_the_tree_as_it_is_reads_the_record_graph_current`: the ticket committed and the store loaded again: `graphs.record` is `ok` and the ticket is listed | no | green |
| 2 | A CIT-E whose kind is not a list never matches (reading R6) | `test_an_execution_record_whose_kind_is_not_a_list_never_matches` (2: `code: "some_symbol"`; `decisions: {DEC-099: done}`; the proposal's list for that kind empty). A refusal naming the kind, or the item listed as a difference | no | **failed**: "a CIT-E whose `code` is 'some_symbol', not a list, matches" (and the same for the map): `matches: true`, no differences |
| | Success | `test_an_empty_list_on_both_sides_matches`; and the earlier `test_w2_37_execution.py` cases with lists | no | green |
| 3 | A CIT-P written from an incomplete assessment never reads as complete (readings R3, R4) | `test_a_cit_p_written_from_an_incomplete_assessment_says_so_or_is_refused`: no code tool, so the result is `complete: false`. The `--out` file carries `complete: false`, the result's `graphs` and the result's gap ids; or the write is refused, naming why (the assessment incomplete, or the code graph), and no file is written | no | **failed**: "the CIT-P written from an incomplete assessment does not say `complete: false`": its frontmatter has the change, radius, depth and lists only |
| | Success | `test_a_cit_p_written_from_a_complete_assessment_is_written`: both graphs read, the file is written; whatever it says of completeness and of the graphs is the result's | yes | expected green (a guard for the fix: a complete assessment's file is not refused) |
| 4 | A name two code definitions share is deletable only when every definition of it is (reading R8) | `test_a_name_two_definitions_share_is_not_deletable_when_one_is_called`: `app/alpha.py` and `app/beta.py` each define `w37_shared`; alpha's is called by `w37_caller`, which DEC-201 constrains; beta's by nothing. No `change` entry for `w37_shared` is `deletable`, and its radius is not below the radius of `w37_shared` in the same repository with beta's renamed to `w37_spare` | yes | expected: `w37_shared` reported `deletable: true` with a radius below the renamed repository's (the dead definition is the one judged) |
| | Success | `test_with_the_dead_definition_renamed_each_name_is_judged_alone`: in the renamed repository `w37_shared` is not deletable and `w37_spare` is | yes | expected green |
| 5 | A code file the index does not hold makes the code graph not current, whatever its modification time (reading R4) | `test_a_code_file_older_than_the_index_but_not_in_it_is_never_missed` (2: left untracked; committed). After the index was built, `app/moved.py`, calling `w37_apply`, arrives with its own and its folder's modification time from before the index (as `mv`, `cp -p` or an archive leave them). For the change `w37_apply`: the new caller listed, or the code graph not `ok` and `complete: false` | yes | expected: `graphs.code` says `ok` and `complete` is true while `w37_moved` is not listed |
| | Success | The earlier `test_w2_37_incomplete.py::test_a_stale_code_graph_is_said_and_never_complete` (a caller committed with a fresh modification time) and `test_w2_37_code_graph.py::test_with_both_graphs_read_the_report_says_so` | yes | as before |

The readings behind them are the suite's own. Behaviour 1 is R4 as `test_a_stale_record_store_is_said_and_never_complete`
reads it, widened to the working tree and to a change of branch: "stale" may be said by the word, or by naming the
paths that differ. Behaviour 3 takes R3 (the CIT-P is the result's `proposal` and the `--out` file) to mean that
the file says what the result says about completeness. No new package: each behaviour follows from a source the
suite already cites.

## Third batch: the second review's findings A, B, C, E and F4 (DEC-812 (1) and (2), DEC-136)

A fresh independent test designer added these in the resume, before the fixes, from the second review's findings
passed on as described behaviours (DEC-136). Every case is in `test_w2_37_resume_findings.py`, built on the suite's
fixtures (`project`, `repo`, `built`, `tools`, `box`) and its support module, which is unchanged (helpers specific to
the batch are in the new file). No earlier case was changed. Each behaviour has a failure and a success half (a
success half is green today, a guard for the fix).

Run at the commit that added the batch, with `gov impact` built, in the sandbox, excluding `local_only`
(`-m "not local_only"`): **13 failed, 81 passed** (21 `local_only` deselected). The 94 earlier cases keep their
results (the three known reds: `test_w2_37_rows.py::test_the_depth_of_a_radius_comes_from_an_owner_decision_or_a_measurement`
and `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question[template]` and `[claude-copy]`). The
new file has **19 cases** (17 functions): 10 red, 8 green, 1 `local_only`. With them the suite is **115 cases**
(92 test functions), 21 of them `local_only`.

Readings taken here: the result of `--compare` carries `complete` and `gaps` under the keys an assessment uses
(`complete: false` and a list of maps with `id`); "names the clash", "says the file is missing", "says the path is
empty" and "says it is a folder" are each a word of a list in the file's head (`CLASH_WORDS`, `MISSING_WORDS`,
`EMPTY_WORDS`, `FOLDER_WORDS`) found in the refusal's `error`; a refusal exits 1, prints no traceback and writes nothing.

| # | Behaviour | Test (`test_w2_37_resume_findings.py::`) | `local_only` | Red reason (today) |
|---|---|---|---|---|
| A | `--compare` checks the CIT-E against the proposal as committed. CIT-P lists DEC-002; CIT-E leaves it out: `matches: false`. Then DEC-002 is removed from the CIT-P file in the working tree, not committed: not `matches: true`; either DEC-002 is still a difference, or the result or refusal names the CIT-P file (`CITP-001.md`) that differs from HEAD | `test_a_proposal_edited_after_it_was_committed_never_turns_a_difference_into_a_match` | no | **failed**: `matches: true`, `differences: []` |
| | Success | `test_a_proposal_edited_and_committed_is_the_one_compared`: the same edit committed and the store loaded again: `matches: true` | no | green |
| B | A register that had no entry at HEAD (the path map's `decision_register`), the store loaded, a first entry (DEC-090, `**Supersedes:** DEC-001`) added and not committed: `graphs.record` not `ok`, reads `stale`, `complete` false, and names `records/decision-log.md`. The fixture's premise (a clean tree reads `ok`) is asserted first | `test_a_register_with_no_entry_at_head_and_a_first_one_uncommitted_reads_stale` | no | **failed**: "`graphs.record` says 'ok' although that graph was not" |
| | The same with the register in a non-governance namespace of the path map (`records/**` is `product` memory) | `test_a_register_in_a_non_governance_namespace_with_a_first_entry_uncommitted_reads_stale` | no | **failed**: as above |
| | The same with a current code graph (both graphs `ok` and, with no gap, `complete: true` before the entry): the report is never `complete` while the record graph is stale | `test_with_a_current_code_graph_a_first_register_entry_uncommitted_is_never_complete` | **yes** | expected: `graphs.record` says `ok` and `complete` is true while the register's first entry is missing. In my runs it is **skipped** (`codebase-memory-mcp` is not on the PATH `heavy_slot.sh` gives pytest); in a worker's sandbox it would error at setup in the fixture `indexed_split_register` (P-W2-38). Not run: the lead runs it outside |
| | Guard: the register holds one entry (DEC-070) at HEAD and a further one is uncommitted | `test_a_register_that_held_one_entry_at_head_and_gets_a_further_one_uncommitted_reads_stale` | no | green: `stale`, naming the register |
| | Success: the first entry committed and the store loaded again: `graphs.record` is `ok`; DEC-090 is a stated change read from a current record graph | `test_a_register_entry_committed_and_the_store_loaded_again_reads_the_record_graph_current` | no | green |
| C | A CIT-P written with `complete: false` and gaps (SPEC-002) and a CIT-E with the same lists: the result carries `complete: false` and the gaps (it may say `matches: true`) | `test_a_match_with_a_proposal_written_as_incomplete_carries_its_incompleteness` | no | **failed**: the result is `proposal`, `execution`, `matches`, `differences` only |
| | End to end: the CIT-P `--out` writes without a code tool (`complete: false`), a CIT-E recording its lists, compared: `complete: false` | `test_a_match_with_a_proposal_the_assessment_wrote_as_incomplete_carries_it_end_to_end` | no | **failed**: as above |
| | Success: a CIT-P with `complete: true` and no gaps: the result is not incomplete and lists no gap | `test_a_match_with_a_proposal_written_as_complete_says_no_incompleteness` | no | green |
| E | `--compare` against a CIT-P whose file is gone (committed, the store loaded, the file removed from the working tree) is refused, exit 1, naming the proposal and saying the file is missing, not that it "lists nothing under `affected`" | `test_comparing_against_a_proposal_whose_file_is_gone_is_refused_as_missing` | no | **failed**: `IMPACT_NOTHING_LISTED`, "CITP-001 lists nothing under `affected`: the records cannot be compared" |
| | `--out ""` is refused as an empty path, not as "a file is there already"; exit 1, nothing written | `test_out_with_an_empty_path_is_refused_as_empty` | no | **failed**: `IMPACT_OUT_EXISTS`, ": a file is there already; gov impact writes no file over another" |
| | `--out <an existing folder>` is refused as a folder, not as "a file is there already"; exit 1, nothing written | `test_out_naming_an_existing_folder_is_refused_as_a_folder` | no | **failed**: `IMPACT_OUT_EXISTS` with the same message |
| | Success: `--compare` naming a file that does not exist (`docs/changes/CITP-404.md`, `docs/changes/CITE-404.md`) is refused naming it as missing | `test_comparing_a_file_that_does_not_exist_is_refused_as_missing[CITP-404]`, `[CITE-404]` | no | green: these two forms are refused as missing today; the form that reads "lists nothing" is the proposal whose file is gone (row above) |
| | Success: `--out <a file that is there>` is refused naming it, "already"; the file untouched | `test_out_naming_a_file_that_is_there_already_is_refused_as_that` | no | green |
| F4 | `--out` whose stem is an id the store holds (`CITP-001`, a stored CIT-P; `DEC-001`, a stored decision), written to a new path, is refused naming the id and the clash; nothing written | `test_out_whose_stem_is_an_id_the_store_holds_is_refused_naming_the_clash[a-cit-p]`, `[a-decision]` | no | **failed**: exit code 0; `docs/proposals/CITP-001.md` is written, and its `proposal.id` is the stem |
| | Success: a stem no record holds, in a new folder, is written | `test_out_whose_stem_is_a_new_id_is_written` | no | green |

No new package. Two points for the reading of the fixes: (1) finding A accepts both ways the brief names, so a fix that
reads the proposal from HEAD or the store passes with DEC-002 still a difference, and one that refuses or reports not
matching while the CIT-P file differs from HEAD passes by naming `CITP-001.md`; (2) a CIT-P file removed from the
working tree is expected to be refused as missing (finding E), also by a fix that reads the proposal from HEAD for A.

## Packages, and the tests that depend on each

- **P-1, the change skill (outside `allowed_paths`).** The routing of the question to `gov impact` is in
  `template/governance/kernel/skills/change/SKILL.md` and its copy `.claude/skills/change/SKILL.md`. Tests:
  `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question` (2). The rest of the suite does
  not depend on them.
- **P-2, KPI 2's citation of W2-L319, and W2-L319's numbers.** W2-L319 is about the depth numbers per radius, not
  the CIT-E. KPI 2's text is CAP-33's acceptance line; the tests hold that (reading R6). W2-L319 itself needs an
  owner decision or a measurement. Tests: `test_w2_37_execution.py` (13, reading R6),
  `test_w2_37_rows.py::test_the_depth_of_a_radius_comes_from_an_owner_decision_or_a_measurement` (red until the
  owner decides).
- **P-3, G-16 and G-24.** Their only written definitions are one line each. Tests: `test_w2_37_code_graph.py` (7),
  `test_w2_37_deletable.py` (6), `test_w2_37_incomplete.py::test_an_unreadable_code_graph_is_said_and_the_record_side_still_given`,
  `test_w2_37_question.py::test_a_plain_language_question_about_a_symbol`.
- **P-4, the close command's governance prefixes (W2-M150, outside `allowed_paths`).** `src/gov/close/` is not in
  this ticket's paths. DEC-500's residual 14 (kernel folders outside the six prefixes run no checks) stays open
  there. No test is written for it here: a case would need a whole `gov close` scenario in that ticket's suite.
- **P-5, what makes a specification "closed".** Tests: the five W2-M320 cases in `test_w2_37_rows.py`. The rule
  W2-M320 asks for is product-spec work (a document outside these paths).
- **P-6, the output's form** (the keys under "The interface the tests assume", and reading R2's kinds). Every case
  of `gov impact` reads it.
- **P-7, the recorded command lists (DEC-747, outside `allowed_paths`).** A new `gov` command must be recorded in
  `RECORDED_GOV_COMMANDS` (`src/gov/check/commands.py`) and in W1-07's tests' list, or W1-26 and W1-07 turn red. No
  test here: those suites already hold it.
