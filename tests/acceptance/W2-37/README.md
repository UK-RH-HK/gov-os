# W2-37 acceptance tests (DAEO-6n5k): `gov impact`

A fresh independent test designer (MR-3, DEC-136) wrote these tests before the implementation. They come from the
ticket's KPI lines and its sources: CAP-33 (its acceptance line and covers CAP-33.a, .b, .e, .f, .g), the W2-37
card in `docs/plan/WAVE_2_WBS.md` §2, the list rows W2-L319, W2-M056, W2-M150, W2-M285 and W2-M320, the S0b2 glue
items G-16 and G-24 (`docs/plan/WAVE_2_TRIAGE.md`, `docs/plan/WAVE_1_WBS.md` §5–6, W2-L322 with DEC-388), and the
decisions DEC-167, DEC-391 (with DEC-393), DEC-035, DEC-105, DEC-309, DEC-466, DEC-500, DEC-674, DEC-680, DEC-747,
DEC-221, DEC-462, DEC-136 and DEC-732. The profile is FULL (DEC-221): every KPI line's success and failure, thoroughly,
with no combinatorial expansion. Every covers id has at least one test.

**81 cases** (65 test functions) in eleven files, a support module and a conftest. 13 cases are `local_only`.

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
