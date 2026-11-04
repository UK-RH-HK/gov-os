# D-4's applied cut, one independent review (DEC-1061: "then one review of the regenerated KPI maps")

Reviewer: a fresh session, read-only for everything reviewed; this file is the only one written. Branch `w2/D4-cut-b`
at `0ad4a12e` (merge base with `w2/integrate` `7842fd9429c6`; `w2/integrate` at `7524fa042713` adds only register
text). Judged by ADR-0001's threat model and DEC-1010 item 1; every finding has its two lines; READY is computed from
the `verdict` block at the end.

## What I ran

All through `heavy_slot.sh`, `PYTHONPATH=~/gov-os-worktrees/D4-cut-b/src`, `TMPDIR=/tmp/gov-os-emg-d4-cut-review`,
`-o tmp_path_retention_policy=failed -p no:cacheprovider`; no full suite.

- **Collect-only, four ways** (exit 0 each): default `5429/20008 collected (14579 deselected)`; `--optin=lifted`
  14,400; `--optin=breadth` 11,035; `--optin=lifted,breadth` 20,006 (the 2 left are the 2 deselected before the cut
  too: 19,955/19,957). The engineer's counts hold.
- **Every regenerated map, mechanically:** 83 READMEs hold "The full run after D-4's cut" or "KPI map after D-4's
  cut", 615 rows. Every case they name resolves in the tree (`--optin=lifted,breadth`): **none is missing**. Against
  the default run: 14 rows name only lifted cases and say "moved to `lifted`" (W1-15 S1, S2, F1; W1-16 S4, F1;
  W1-26 S6, S9; W1-30 S2-S4, S6, S7, F2, F3), all lifted features (DEC-1045, DEC-953); 10 rows are process lines
  stated as such; **every other row has at least one case in the default run**. 10 READMEs have no new map: 7 wholly
  lifted suites (W2-01, W2-07, W2-53, W2-68, W2-69, W2-71, W2-107) and 3 uncut (W2-65, W2-90, W2-92).
- **By hand, 60+ KPI lines** (each ticket's `kpis:` against the map and the default cases): W1-02 (7 rows),
  W1-47 (7), W1-50 (7), W1-45 (4), W1-04 (F2, F3), W1-01 (S1, F1), W1-41 (13), W1-40 (5), W1-32 (S1-S3, F1), W1-08
  (S1, S2, S6, F1), W1-06 S2, W1-26 (S1, F1, S6, S9, the fold), W1-30 (core and lifted), W1-27 (10), W1-35 (18),
  W1-39 (5), W2-49 (5), W1-36 S3, W1-38 S1, W1-11 (6), W1-31 (8), W2-54 (S2, S4, S5, S9), W2-96 S1, W2-58 (c), and
  F3's 11 unplaced rows (W1-15 S3, W1-23 S1/S2, W2-55 S6, W2-61h F1/F3, W2-66 S13, W2-92 S5; the three opt-in ones
  lifted). Scripts: `/tmp/gov-os-emg-d4-cut-review/` (`mapcheck*.json`, `some-missing.txt`, `oldmap.txt`).
- **Runs alone (CUT-3, CUT-4):** see CUT-4.

## CUT-1, every kept KPI line covered

**F1: W1-40 S3 ("pre-commit also runs the second gitleaks scan, with the project's rules alone") has no case in the
default run.**
- The map names `test_a_clean_commit_passes_and_runs_the_g1_and_g2_checks`, `test_a_failing_hard_block_check_stops_the_commit`
  and `test_the_commit_passes_again_once_the_check_passes`: S1's cases (the third is on `breadth` itself). None
  stages a secret.
- The line's own cases, the pre-cut map's (`README.md:179`), are all on `tests/optin-lifted-breadth.txt` lines
  880-884 as `# cap`: `test_a_staged_secret_stops_the_commit`, `..._the_builtin_allowlist_shelters_stops_the_commit`,
  `test_the_sheltering_words_alone_do_not_stop_a_commit`, `test_a_secret_staged_beside_a_clean_working_copy_is_what_counts`,
  `test_a_missing_tool_stops_the_commit`. The default run holds 3 of `test_w1_40_pre_commit.py`'s 12 cases.
- The feature is in force: `template/lefthook.yml` lines 3-4 still run both scans; W1-40 is not lifted (T-11 lifts
  only this repository's CI; the template half is P1-11's, later).
- The scoped selection leaves `breadth` out too (it names files; the conftest deselects), so a change to the
  template's hook that drops the second scan passes both the scoped and the full run.

Ordinary work: yes, because P1-11 and any template hook edit change exactly this file, and nothing in the full or
scoped run would go red.
Consequence: fails open (a kept KPI line with no case in the default run).
Fix (one line each): take `test_a_staged_secret_stops_the_commit` (and the shelter case) off the breadth list;
correct S3's row.

**F2: W1-41 F3 ("A legacy rule file stays loaded after retirement") has no case in the default run, and S3 loses
two of its three clauses.**
- The map gives F3 the same three cases as S3 (`test_each_kind_of_legacy_rule_file_is_imported_into_rulesync`,
  `test_the_imported_mcp_server_keeps_its_command`, `test_the_two_role_sections_of_agents_md_are_both_imported`).
  They assert the import under `.rulesync/`, not that the old file is gone.
- F3's own cases, the pre-cut map's (`README.md:350`: "no legacy rule file stays loaded (failure 3)"),
  `test_no_legacy_rule_file_stays_where_an_agent_tool_loads_instructions` and `test_adapter_generation_is_run_or_named`,
  are on `optin-lifted-breadth.txt:913-914` as `# cap`. So are the two not-retired cases.
- S3's "a raw chat database is marked non-authoritative ... before retirement; retired systems contribute zero
  ACTIVE decisions" has no default case either (`test_the_chat_database_is_marked_non_authoritative`,
  `..._retired_after_its_knowledge_is_in_records`, `test_retired_systems_contribute_no_active_decision` all on
  breadth). The default run keeps 12 of `test_w1_41_legacy.py`'s functions, none of these.

Ordinary work: yes, because `gov adopt --lite` is a kept product command (W1-41 is not lifted) and any change to
`src/gov/adopt/` can break retirement without a red in the full or scoped run.
Consequence: fails open (a kept KPI line with no case in the default run).
Fix: take `test_no_legacy_rule_file_stays_where_an_agent_tool_loads_instructions` and
`test_the_chat_database_is_marked_non_authoritative` (or `test_retired_systems_contribute_no_active_decision`) off the
breadth list; correct F3's row.

**F3: the maps' cause: a line's "named case" is the first three functions of its README row or section, so where a
README groups lines, groups by file or numbers lines differently from the ticket, the wrong line gets the cases,
and the suite-wide cap (lines x 6 functions) then cuts the line's own cases.**
- 19 groups of rows share one identical case list (`W1-41 S3=F3`, `W1-40 S1=S3`, `S2=F1=F2`, `W1-32 S1=F1`,
  `W2-57 S3=S6=S9=F1`, `W2-61 S3=S4`, `W2-86` two groups, `W2-95` two, `W1-49` two, `W2-123`, `W2-126`, `W2-66`,
  `W2-87`, `W2-112`, `W1-42`, `W1-15`, `W1-26` (the fold, correct)).
- Mislabelled rows where the line is still covered by other default cases: W1-32 S1 names the status read-only
  cases (the README's "success 1" is the ticket's S4; `test_w1_32_launch.py` runs by default); W2-54 S2, S4, S5 name
  time-limit and audit-report cases (the sandboxed-worker and query-vector cases run by default); W1-36 S3 names
  frontmatter cases (`TestAuditDecisionPackages` runs); W2-66 S13 and W2-55 S6 (process lines given unrelated cases).
- 59 cases that the maps name "in the full run" are on a breadth list (58) or `lifted` (1), in 52 rows; each of those
  rows keeps another default case (`some-missing.txt`). E.g. W1-06 S2's `test_pyyaml_is_recorded_at_6_0_1`.
- Suites that keep every function ("by its words (every function of the suite kept)") lose no coverage whatever the
  row says; the risk sits in the capped suites (functions past the cap > 0): about 33 suites.

Ordinary work: yes, because the maps are what the next designer and the scoped selection's reviewer read.
Consequence: other (map accuracy; it loses a line's last case only where F1 and F2 name it).
Fix (rides with F1, F2): re-place the capped suites' lines by the ticket's line text, not the README's layout, at
least where a README section or file row carries more than one line; regenerate those rows.

**F4: part B's `rep:` keeps a function's first collected row whatever its class; part A picked one row per class.**
- Part A: `test_write_to_secret_file_is_denied` keeps pem, config-secrets, dotenv, key; W1-47's oracle case one row per
  tool kind. Part B (215 `rep:` lines): W1-32 S1 names "SIGTERM and SIGHUP", and the default run keeps
  `test_the_signal_ends_the_session[SIGTERM]` and `..._removes_the_temp_folder[SIGTERM]` only; W2-54's
  `test_the_two_checks_of_this_ticket_stay_hard_block` keeps context-reproducibility, not core-schema (S9 names both).
- EMG-d4-apply step 3 says "fold parameters to representative cases (keep every class a KPI line names)".

Ordinary work: yes, because a change to the launcher's signal handling would not go red in the full run.
Consequence: other (the line keeps cases; a named class is unchecked).
Fix (rides along): where a line names a row's class, list the rows instead of `rep:`.

## CUT-2, nothing kept is sent out

- `lifted` (`optin-lifted.txt` 169 lines: W1-30 97, `unit/close` 19, `unit/secrets_check` 9, W1-15 6, W1-26 5,
  W1-16 2, whole W2-01/07/53/68/69/71/107, W2-50's scan scale; `optin-lifted-guard.txt` 449: W1-02, W1-50, W2-106,
  `unit/guard`, W2-50, W1-46, W1-45, W1-03, W2-58, W1-05, `unit/containment`, W1-47, W2-72, W2-84, W2-59's Stop line,
  W1-33's three full-guard cases). Every entry I read sits on G-3, G-4, G-5, G-6, R-7, DEC-1045, DEC-953 or Q-2..Q-11.
- **The features in force keep default cases:** the five rules in `tests/unit/hooks/test_live_hook.py` (rule 1: 6
  cases, rules 2/3: 3, rule 4: 5, rule 5: 5, plus rm, git and fail-closed cases), and W1-02's `test_independence`
  (29, with `test_auditor_cannot_write_into_another_role_s_work`); G-14's `role_paths` (`test_role_paths_refuses_a_true_read`
  10, near miss, malformed, conflict, link sources) and W2-58's 102 (27 counterpart-read cases); memory (no retrieval
  suite is on `lifted`); Q-1 (`unit/orchestration`, not listed); the opt-in mechanism (`tests/unit/optin`, 16, in
  the default run); `unit/secrets_check/test_dec1045_switch.py` (22). G-1 and the structural pass are the CTO's tool
  tests, untouched.
- **The breadth clause fails:** F1 and F2 above are breadth entries that removed a kept line's last case.

**F5: T-11's new pin `test_this_repositorys_own_workflow_runs_only_when_started_by_hand` is on breadth (`:894`, `# cap`).**
Ordinary work: yes, because a later edit of `ci.yml` would not be checked by the full run.
Consequence: other (CI would start on push again; no guard or work is at stake).

## CUT-3, the mechanism

- Deselected, never skipped: `pytest_collection_modifyitems` drops the items and calls `pytest_deselected`
  (`tests/conftest.py`); the default run reports "14579 deselected", no skips added.
- The four forms (`--optin=lifted`, `GOV_TESTS_OPTIN=lifted`, the comma form, the option twice, and option with
  variable), the list-by-name rule (`*breadth*` is `breadth`), the node-id rule (a case named on the command line
  runs; a file or folder does not opt in) and the `rep:` rule are each a case in `tests/unit/optin/test_optin_lifted.py`
  on a planted tree. **Run alone: 16 passed.**
- A stale entry: `test_every_entry_of_the_real_lists_names_a_test_path_or_function_that_exists` runs in the default
  run and catches a path or function that names nothing. It does not check a row id (`[...]`); a stale row id
  deselects nothing, so the case runs (fails closed). A row for later, no finding.

## CUT-4, the red fixes and revisions, each run alone

| item | run | result |
|---|---|---|
| R2 (W1-26 exit 0 on the green base) | `test_w1_26_command.py::test_exit_0_when_all_checks_green` | 1 passed |
| R5 (`unit/retrieval/test_lexical.py`) | the file | 5 passed |
| M5 (W1-27's fold, three planted paths) | `test_w1_27_doctor_r5.py::test_stale_path_in_live_document_is_reported` | 1 passed |
| T-11 (W1-40 templates, with the new pin) | `test_w1_40_templates.py --optin=breadth` | 3 passed |
| W1-01's merge exemption, history | `test_w1_01_integration_merges.py`, `test_w1_01_history.py` | 41 passed |
| W1-28/W1-50's copy scan | `test_w1_28_fixture_copies.py` | 10 passed, 12 deselected |
| R3 (W1-35's row) | `test_w1_35_orchestration.py` | 26 passed, 28 deselected |
| W2-59 (worker env, R-2) | `test_w2_59_hook_lines_worker_env.py` | 8 passed, 1 deselected |
| R1, T-6, win_toast (W2-66 live test map) | `test_w2_66_live_test_map.py --optin=lifted,breadth` | 89 passed |
| W2-108 (R-1's PATH filter) | `tests/acceptance/W2-108` | 23 passed, 4 skipped (no store in the worktree: "the lead rebuilds the worktree's store", README; a reviewer does not rebuild) |
| W2-54's copy (sandboxed worker, R-2) | `test_w2_54_sandboxed_worker.py` | 1 passed |
| W1-46 (R-2, sandbox settings) | `test_w1_46_sandbox_settings.py` | 11 passed, 27 deselected |

Thirteen runs, all exit 0. W2-108's four store cases were not run here: they are the one part of CUT-4 not shown.

## CUT-5, the count

- Default 5,429 against the list's 4,679: **+750 (+16.0 %)**, just past the list's "about ±15 %", and 8.6 % over the
  owner's "about 5,000".
- **Part A, 1,195 against 1,050 (+145):** the live hook's 63 (decision 5; the list's figure had none) and about 82 from
  recounting named-first (F2 of the list review). Summed from A's commit subjects: 1,082 in the suites plus W1-01's
  54 plus the hook's 63.
- **Part B, 4,218 against 3,638 (+580, +16 %):** the list counted one case per kept function; the cut keeps each
  line's named case with all its rows. W1-07: 42 functions, as the list says, but 137 cases (104 are rows of
  multi-row functions); W1-08: 60 functions, 118 cases; W2-61: 61, 99. The biggest gaps: W1-07 +95, W1-08 +58,
  W2-61 +38, W2-64 +28, W1-13 +27, W2-04 +26, W1-21 +24, W1-14 +22. Also M1, M1b and M9 are not applied (F6).
- So it is the named-first rule (F2) together with "a named case keeps every row", not a cap breach.

**F6: M1, M1b and M9 (part B's approved merges) are not applied.**
- `test_w2_54_green_here.py` still holds `test_gov_check_gives_context_reproducibility_green_here` and
  `..._core_schema_green_here` apart; `unit/retrieval/test_emg_query_device.py` is still there. The list counted
  these 3 cases as removed, and M1/M1b are its largest single saving (about 2,200 case-s, est.).

Ordinary work: yes, because D-10's full run pays it.
Consequence: other (time; nothing is lost).

## CUT-6, deletions

- `git diff --diff-filter=D w2/integrate...w2/D4-cut-b` is empty: **no file is deleted anywhere.**
- Test functions removed, counted on the pre-cut collection (`c39cffc1`, whose `tests/` equal `7842fd94`'s):
  - **D1, 28 cases:** `test_w1_01_history.py` 2 functions (3 cases) and `test_w1_01_settings_deny.py` 5 (25).
  - **D2, 1:** `unit/install/test_install.py::test_unfrozen_repo_asks_install_for_orchestrator`.
  - **D3, 1:** `test_w1_24_packet.py::test_the_hash_is_stable_across_two_runs`.
  - **T-11's two:** `test_every_workflow_has_its_template_and_the_template_renders_to_it`,
    `test_the_template_holds_no_workflow_the_repository_lacks`.
  - **M5, 2 more:** `test_w1_27_path_compliance_r2.py`'s two stale-path cases, folded into
    `test_stale_path_in_live_document_is_reported` (approved in B's W1-27 row; the fold plants all three paths and
    runs green). This is outside CUT-6's enumerated set but approved.
- Part B's "four" (D3 1, M1 1, M9 2): only D3 is done (F6). Nothing else is removed; the other line removals are
  revisions with a `Rewrite-Reason:` (R1, R2, R3, R5, W2-66's lead-verification scope `75f550db`, W1-28's scan).

## Summary of the verdict

F1 and F2 are in scope, reachable in ordinary work and fail open: each is a kept KPI line whose last case in the
default run went to the breadth list. **Not READY.** Both are a list edit (move two to four node ids off
`tests/optin-lifted-breadth.txt`) plus two map rows, about 10 cases. F3 says where else to look (the capped suites
whose READMEs group lines); F4 to F6 ride along (DEC-802).

```verdict
{"kpis": [
 {"kpi": "CUT-1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "CUT-2", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "CUT-3", "verdict": "pass", "findings": []},
 {"kpi": "CUT-4", "verdict": "pass", "findings": []},
 {"kpi": "CUT-5", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "CUT-6", "verdict": "pass", "findings": []}
]}
```

## Round 2 (the last DEC-1010 allows): CUT-1 and CUT-2 re-judged

Branch `w2/D4-cut-b` at `27cb6307`: `92c7b131` (F1), `4712c1e4` (F2), `ce643f00` (F5), `cb96180d` (F3), `27cb6307`
(F4), on top of round 1's `0ad4a12e`. Round 2 changes only `tests/optin-lifted*breadth*.txt` and the 83 maps
(`git diff 0ad4a12e HEAD -- tests/optin-lifted.txt tests/optin-lifted-guard.txt` is empty: nothing new goes to
`lifted`).

### What I ran (same TMPDIR, `heavy_slot.sh`, the tree's own `src`)

- **Collect-only, four ways, my own:** default `5542/20008` (14,466 deselected); `--optin=lifted` 14,513;
  `--optin=breadth` 11,035; both 20,006. The coordinator's counts hold.
- **Against round 1's default collection:** 113 cases added, **none removed** (`comm` of the two id lists). So
  nothing round 1 kept is lost.
- **The designer's `check.py`**, copied and run (`python3 -I`) against **my** default and full collections:
  `83 maps, 688 rows checked against 5542 default cases` / `OK`, exit 0. It also checks that every `kpis:` line of each
  suite's ticket has a row.
- **My own map check (round 1's `mapcheck.py`)** on the new maps: 83 maps, 688 rows. **No row names a case that is
  out of the default run** (round 1: 59 cases in 52 rows). The only rows with no default case are the same 14 lifted
  lines as in round 1 (W1-15 S1, S2, F1; W1-16 S4, F1; W1-26 S6, S9; W1-30 S2-S4, S6, S7, F2, F3), plus 4 process
  lines stated as `none:` (W1-41 S8, W2-86 S5, F5, W2-96 S6).
- **The rows `check.py` lets through unchecked** (marked `lifted`, or `none:`): all 78 read. They are W1-02 F1,
  W1-03 (5), W1-15 (4), W1-16 (2), W1-26 (2), W1-30 (7), W1-45 (7), W1-46 (2), W1-47 (4), W1-50 (17), W2-50 (3),
  W2-59 (1), W2-72 (8), W2-84 (11), and the 4 process lines. Each sits on G-3, G-4, G-5, G-6, DEC-1045, DEC-953 or
  DEC-1061 (7). Three are partly lifted and say "none:" although their kept half runs by default (see row R2-2).
- **Round 1's pre-cut comparison (`oldmap.py`)** on the new collection: 36 lines whose pre-cut cases are all out of
  the default run, every one a lifted line (W1-02, W1-03, W1-15, W1-16, W1-45, W1-47, W1-50, W2-07). **W1-41 F3 is
  gone from the list**; nothing new is on it.
- **The 113 added cases run alone:** see "The added cases" below.

### F1 and F2's lines, re-checked

- **W1-40 S3:** the row names `test_a_staged_secret_stops_the_commit` and
  `test_a_staged_secret_that_the_builtin_allowlist_shelters_stops_the_commit` (2 of 2). The default run now holds
  6 cases of `test_w1_40_pre_commit.py`, these three among them (the shelter case's two rows, `alphabet` and
  `false`). **Fixed.** S1 now names the pre-push cases (`test_a_push_runs_the_g3_check`,
  `test_a_failing_g3_check_stops_the_push`) and F1 names `test_no_step_downloads_a_model_or_asks_for_a_gpu`, both in
  the default run.
- **W1-41 F3:** the row names `test_no_legacy_rule_file_stays_where_an_agent_tool_loads_instructions`, in the
  default run. S3 names the import case (5 of 5 rows), `test_the_chat_database_is_marked_non_authoritative` and
  `test_retired_systems_contribute_no_active_decision`, all in the default run. **Fixed.**
- **F5:** `test_this_repositorys_own_workflow_runs_only_when_started_by_hand` is in the default run. **Fixed.**
- **F4:** `test_the_signal_ends_the_session` and `..._removes_the_temp_folder` keep SIGTERM and SIGHUP;
  `test_the_exit_code_after_the_signal_is_130` keeps SIGINT, SIGTERM and SIGHUP; W2-54's
  `test_the_two_checks_of_this_ticket_stay_hard_block` keeps both checks. **Fixed.**

### Sample by the ticket's own text (25 lines, weighted to F3's)

Each line's `kpis:` text read beside the cases its new row names, each case's place in the default run checked
(`sample.py`):

| line | the row's cases, all in the default run | judgement |
|---|---|---|
| W1-32 S1 (launch exit code, SIGTERM/SIGHUP, 130) | `added_cases::test_a_failed_removal_keeps_the_sessions_exit_code_when_stderr_cannot_be_written`, `launch::test_the_signal_ends_the_session`, `..._removes_the_temp_folder`, `..._exit_code_after_the_signal_is_130` | right (was the status cases) |
| W1-32 S4 (git status unchanged) | `status_read_only::test_git_status_porcelain_is_unchanged` | right |
| W1-32 F1 (status mutates) | `..._porcelain_is_unchanged`, `test_status_writes_nothing_anywhere` | right |
| W1-32 F2 (an open gate missing) | `test_every_open_package_is_listed_however_many`, `test_an_open_specification_shows_every_open_row_linked_or_not` | right |
| W2-54 S2 (one text, one vector, keyed) | `query_vector::test_two_projects_asking_one_text_..._machine_wide_cache` and two `cpu_embedder` cases; every `query_vector` function runs | right |
| W2-54 S4 (sandboxed worker) | `test_inside_a_launched_sandboxed_worker_...` | right (was audit-report cases) |
| W2-54 S5 (query embedder on its port) | two `cpu_embedder` cases | right |
| W2-54 S9 (context-reproducibility green) | `test_gov_check_gives_context_reproducibility_green_here`, `..._stay_hard_block` | right |
| W1-36 S3 (decision packages, tickets) | the three `TestAuditDecisionPackages` cases | right (was frontmatter cases) |
| W1-38 S1 (CLAUDE.md, AGENTS.md <= 1.5k, skills) | `test_claude_md_is_the_root_rule`, `test_agents_md_token_limit`, `test_generated_skill_is_the_one_openspec_ships` | right (the token-limit class is back) |
| W1-40 S1, S3, F1, F2 | as above; F2 `test_a_push_with_a_failing_g3_check_never_leaves_ci_green` | right |
| W1-41 S3, F3 | as above | right |
| W1-49 S1 (PreCompact, the lead's checkpoint) | `test_in_a_worktree_the_block_is_appended_to_the_leads_checkpoint`, `..._without_a_lead_checkpoint_...`, `..._precompact_hook_is_registered_for_both_triggers` | right |
| W1-49 S2 (SessionStart injects) | `test_the_injection_carries_the_prompt_path_and_the_whole_resume_here_section` | right |
| W2-61 S3 (per-question script) | `test_the_measure_takes_the_real_visible_half_by_its_set_s_name` | weak name; `test_per_question_figures` runs by default (no function cut) |
| W2-61 S4 (both figures together) | `test_both_figures_together_against_85_and_99` and two `scores` cases | right |
| W2-66 S13 (the lead's full verification) | three "runs the full regression" cases | right (was W1-28's scan cases) |
| W2-123 S5 (configured cap, defaults) | the two `shared_start` cases | right |
| W2-126 F3 (fails because of the cache) | `test_an_all_cached_rebuild_...`, `test_concurrent_rebuilds_and_searches_serve_only_right_vectors` | right |
| W2-112 F3 (differs from a private reranker) | `test_the_services_answers_match_a_private_rerankers_...`, `test_the_same_inputs_get_the_same_answer_...` | right |
| W1-42 S13 (a real ticket closed clean) | `test_one_real_ticket_closed_by_a_clean_gov_close` | right |
| W2-55 S6, W2-87 S6 (W2-61's measure re-run) | one unrelated case each | process lines; see R2-2 |
| W2-57 S6, S9 (the resource gate; removals of load_sensitive entries) | `nightly_route` cases | close enough for S6; S9 is an orchestrator commit (process line); see R2-2 |

**No sampled line lacks a case of its own in the default run.** The three that name an unrelated case are process
lines (a measure re-run, an orchestrator commit) in suites that keep every function.

### No breadth entry removes a line's last case

- Mechanically, by three independent checks: the designer's `check.py`, my own map check (every non-lifted row's
  named cases are all in the default run) and the pre-cut comparison (only lifted lines left). Round 2 only adds to
  the default run.
- By the ticket's text: 25 lines above, and round 1's 60+.
- **I found no kept line whose last case is on a breadth list.**

### Rows (none blocks)

**R2-1 (round 1's F4, F5, F6, as rows):** F4 and F5 are fixed (above). F6: M1, M1b and M9 are still not applied
(`test_w2_54_green_here.py`'s two `gov check` cases apart; `unit/retrieval/test_emg_query_device.py` still there). The
count grows to 5,542: +18.4 % over the list's 4,679 and +10.8 % over "about 5,000", all of it named cases put back.
Ordinary work: yes, because D-10's full run pays the time.
Consequence: other (time; nothing is lost).

**R2-2: some rows still mislabel; coverage is unaffected.**
- W1-46 S6, F6 and W2-59 S2 say "none: the line's feature is lifted", while their kept half runs by default
  (`test_w1_46_research_installs.py` 16 cases, `test_w2_59_hook_lines.py` 15 and `..._worker_env.py` 8). A reader
  may take a covered line for lifted.
- W2-55 S6 and W2-87 S6 (a measure re-run) and W2-57 S9 (an orchestrator commit) are process lines but name an
  unrelated case. Their suites keep every function.
- `check.py` passes a row marked `lifted` or `none:` without reading it; I read all 78 by hand.

Ordinary work: yes, because the next designer reads the maps.
Consequence: other (fails closed: these lines are covered, or are process lines).

**R2-3: the conftest's node-id rule cuts a command-line argument at its first space** (`tests/conftest.py:209`,
`arg.split(" ")[0]`).
- Twenty opt-in entries have row ids with a space. Example:
  `test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[engineer-npm install -g ccusage]`.
- If a run names one of these by node id without opting in, the case is still deselected, against the documented rule.
  Pytest reports it as deselected; it never shows it passing.

Ordinary work: yes, because a lead re-running one named row hits it.
Consequence: other (fails closed: the case is reported deselected, never reported green).

**R2-4: a cross-suite `from conftest import` collision**, already there before the cut.
- When ids of W1-35 and W2-66 are passed in one process, `test_w1_35_orchestration.py` imports W2-66's
  `conftest`, and the import fails (`CITATION_PATTERN`).
- The tree's own collection (`pytest tests`) is clean, so the full run is unaffected. The cut did not cause it.

Ordinary work: yes, because a selection that names files from several suites could hit it.
Consequence: other (a collection error is red, never green).

### The added cases

- I ran the 113 cases that round 2 adds to the default run alone, by node id, one run per suite (33 suites), through
  `heavy_slot.sh`. I left out the 3 real-model W1-21 cases, which are routed `nightly` and would query the shared
  embedder.
- **110 of 110 passed: every suite exit 0, no skip, no failure.** W1-16's code-graph case took 131 s.
- So putting these cases back turns nothing red in the full run. The 3 W1-21 cases are left to D-10's nightly.

### Round 2 verdict

F1 and F2 are fixed, and no kept line's last case is on a breadth list. No finding is in scope, ordinary and failing
open or losing work. **READY.** The rows ride along, or go to Wave 3 (R2-3, R2-4).

```verdict
{"kpis": [
 {"kpi": "CUT-1", "verdict": "pass", "findings": [{"id": "R2-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "CUT-2", "verdict": "pass", "findings": []},
 {"kpi": "CUT-3", "verdict": "pass", "findings": [{"id": "R2-3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "CUT-4", "verdict": "pass", "findings": [{"id": "R2-4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "CUT-5", "verdict": "pass", "findings": [{"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "CUT-6", "verdict": "pass", "findings": []}
]}
```
