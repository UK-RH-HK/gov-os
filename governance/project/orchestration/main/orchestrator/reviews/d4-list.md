# D-4's list review: the test suite cut (DEC-1052; `D4-LIST.md`, `D4-LIST-A.md`, `D4-LIST-B.md` at `a22718fd0aec`)

The one independent reviewer of the list (DEC-1052: "test designers do it, with one independent reviewer"). I am a fresh
session and read-only for everything I reviewed; this file is the only one I wrote. I judged the list by ADR-0001's
threat model and DEC-1010 item 1. Every finding has its two lines, and READY is computed from the `verdict` block at
the end. Tree: `w2/integrate` at `a22718fd0aec`. Its `tests/` match `c39cffc1b191`'s (`git diff --stat` is empty), so
the designers' collection holds here.

## What I ran and read

- **Collect-only, my own run:** `heavy_slot.sh python3 -m pytest tests --collect-only -q -o tmp_path_retention_policy=failed
  -p no:cacheprovider` with `PYTHONPATH=<main>/src` and `TMPDIR=/tmp/gov-os-emg-d4-review`. Result:
  `19955/19957 tests collected (2 deselected) in 11.71s`, exit 0. My scripts and outputs are in
  `/tmp/gov-os-emg-d4-review/` (`counts.py`, `tables.py`, `tier2check.py`, `tier2files.py`, `named.py`, `appb.py`).
  I ran no tests apart from W1-06's helper functions, which I called directly, with no pytest run.
- I read every row of both tables against my counts per suite and per file. I compared part A's `fates.json` and
  `tier2.py` (`/tmp/gov-os-emg-d4a/`) and part B's `final.json` (`/tmp/gov-os-emg-d4b-list/`; its `py/` folder is
  empty, so B's rules cannot be re-run) with the lists.
- I read the KPI lines (`kpis:` front matter) of W1-02, W1-04, W1-26, W1-28, W1-30, W1-40, W1-41, W1-46, W1-47, W1-50,
  W2-01, W2-50, W2-53, W2-54, W2-58, W2-69 and W2-71, and the README maps of W1-41 and W2-58.
- I read DECISIONS-IN-FORCE ("Lifted"), P1-PLAN's DEC-1052 section and INVESTIGATION-1-COMBINED's rows T-3, T-6,
  T-7, T-10, T-11, Q-1..Q-4, Q-7..Q-11, G-1..G-14 and R-7.

## D4-1, the counts

- **Before:** every row of both tables equals the collected count, suite by suite. Each of the 133 collected suite
  folders sits in exactly one part. A totals 10,633 and B totals 9,366. They overlap in exactly one file,
  `tests/unit/hooks/test_w2_106_template_hook_lines.py` (44 cases, 9 functions). 10,633 + 9,366 − 44 = 19,955.
- **Part A's rows:** each row holds before = tier 1 + `lifted` + parametrised + deleted. The columns sum to 1,404 /
  1,050 / 6,684 / 2,516 / 29. The case-seconds sum to 5,391 / 821 / 3,156 against the stated 5,389 / 824 / 3,155,
  which is rounding.
- **Part B's rows:** they sum to 9,366 → 3,638 (tier 2) / 4,591 (tier 1), with 2,261 to `lifted`, and
  9,366 − 2,261 − 2,510 − 4 = 4,591 (the 4 are D3 1, M1 1 and M9 2). The case-seconds sum to 27,588 → 9,045, with
  11,293 to `lifted`. All of these agree.
- `unit/close`'s 19 lifted files hold exactly 402 cases, and the kept 8 hold 65 functions. W1-30 sends 486 cases plus
  44 node ids to `lifted`, which makes 530. All seven core cases exist.

**F1: the combined "after" figures count the overlap file's kept cases twice.**
- B's `unit/hooks` row (75 → 39) is 30 functions from the other two files plus the overlap file's 9.
- A also counts that file (25 at tier 1, 9 at tier 2), and `D4-LIST.md` adds the two parts unchanged
  (1,050 + 3,638 = 4,688; 1,404 + 4,591 = 5,995).
- So the full run is **4,679 (tier 2) and 5,986 (tier 1)**, and "folded" is 4,991 rather than 5,026.
- Its open-rows claim that "the totals above already count it once" is not true.
- Its "deleted 29" row leaves out B's 4.
- The summary's rows add up to 19,999, not 19,955.
- The effect is 0.2 %, inside the stated ±15 %.

Ordinary work: yes, because the owner decides on these figures as written.
Consequence: other (a count off by 9 cases; no case is lost).

**F2: part A's tier-2 counts come from a selection that breaks the list's own rule.**
- `tier2.py` keeps the first 6 × lines kept functions in collection order. The list's text (A §1, D4-LIST
  decision 1) says each line's named cases are kept first.
- The counted selection cuts every function of `test_w1_02_test_independence.py` (11 functions, 29 cases). A §1
  says the cut falls "never on `test_independence`".
- It also cuts every function of files that are the only named cases of kept lines:
  - W1-28 S3 (`roles`, `repeat`);
  - W1-46 F8 (`sandbox_settings`, the only file that tests excludedCommands);
  - W2-58 S3 (`test_designer`), S7 and S8 (`tilde_and_test_runs`);
  - W1-50 S7's orchestrator half (W1-28's `test_the_orchestrator_can_pause`, in `roles`).
- A selection that follows the rule fits inside the same caps (functions are capped, and the swap changes only the
  rows per function). So 1,050 is close, but it is not the count of any selection the list allows.

Ordinary work: yes, because a designer who wants to reach the approved 1,050 at the cut would reproduce the script
the list cites. Step 2 of D4-LIST (the regenerated README maps, checked by the reviewer) is what stops this.
Consequence: other. As written, the list keeps every line, because its rule protects the named cases. The defect is
in the derivation of the count. Fix it in the cut that follows: recompute tier 2 named-first, and write the tier-2
kept functions per line as data.

## D4-2, KPI coverage (sample of 31 rows, weighted to the biggest cuts)

I checked the tier-1 names mechanically:
- **Part A:** all 182 back-quoted cases and files in A §4 have fate `keep` in `fates.json`. The only exceptions are
  the three A names as moved (`test_the_orchestrator_may_write_anywhere_else_in_the_repository`, `secrets_scan_scale`
  and `protected.py`).
- **Part B:** all 364 names in Appendix B resolve to collected functions or files (13 of them through their
  `TestX::` class).
- I also checked the representative classes the list promises against the parameter ids:
  - W1-47 oracle: Read 18, Grep 12, Glob 12, Bash 96, Write/Edit/NotebookEdit, MCP 24;
  - W1-47 uv: orchestrator ask rows and denied-role rows;
  - W1-01 secrets: the four classes, on Edit and Write.
- The count's "first k rows" never holds these classes (for example, the first 40 oracle rows are all Bash), but each
  class exists, so k rows can hold every class.

| # | ticket, KPI line | removed (tier 1 / tier 2) | kept case in the full run | result |
|---|---|---|---|---|
| 1 | W1-02 S1 (writes only inside allowed_paths) | 30 files, 3,282 cases to `lifted` | `lifted` (G-4: write scope lifted in the product's defaults) | lifted, correct |
| 2 | W1-02 S2 (engineer denied under tests/acceptance; test designer only there) | `test_independence` 73 → 29 | `test_engineer_bash_write_under_acceptance_tests_is_denied`; `test_the_test_designer_s_multiedit_is_allowed_under_the_acceptance_tests_only`; `test_independence` (tier 1) | covered (F2 at tier 2) |
| 3 | W1-02 S3 (freeze denies every write; p95 < 100 ms) | freeze 21 → 7 | `test_w1_02_freeze.py` (7); `test_decision_p95_is_under_100_ms` | covered |
| 4 | W1-02 F2 (crash or timeout lets the call through) | `guard_failure` 26 → 9, `deadline` 14 → 6 | `test_w1_02_guard_failure.py` (9), `test_w1_02_deadline.py` | covered |
| 5 | W1-02 S4/F1/F3 (no role is read-only; any write outside allowed) | role-less, unknown role, allow list to `lifted` | `lifted` (G-4) | lifted, correct |
| 6 | W1-47 S1/F1 (`dangerouslyDisableSandbox`) | escape hatch 66 to `lifted` | `lifted`. The live five-rule hook has no such check; only `decide.py:1115` does. Decision 7 to the owner | lifted, correct |
| 7 | W1-47 S2 (containment on PostToolUseFailure) | `failed_commands` 13 | `lifted` (G-5) | lifted, correct |
| 8 | W1-47 S4/F2 (any tool naming the oracle path denied) | `oracle_guard` 281 → 26, naming 181 → 19 | `test_a_call_that_names_the_oracle_path_is_denied` (6, one per tool kind) | covered |
| 9 | W1-47 S6/F6 (uv forms ask/deny) | 267 → 23 | `test_w1_47_uv_installs.py` 6 functions | covered |
| 10 | W1-47 S5/F5 (no install ask rule; sudo deny stays) | 23 → 10 | `test_w1_47_settings_rules.py` | covered |
| 11 | W1-04 S1/F1 (installs ask or denied) | `install_rule` 106 → 19, probe 128 → 17 | `test_w1_04_install_rule.py` 7 functions | covered |
| 12 | W1-04 S2 (Auto mode) | 36 → 6 | `test_w1_04_auto_mode.py` 3 functions | covered |
| 13 | W1-04 F2 (sudo never allowed) | 43 → 10 | `test_w1_04_sudo.py` | covered |
| 14 | W1-04 F3 (only escalates) | 11 → 5 | `test_the_hook_never_gives_an_explicit_allow` | covered |
| 15 | W1-50 S1 (marker; empty flag is no freeze) | 33 → 10, 11 → 7 | `test_w1_50_freeze_marker.py`, `freeze_guard_reading.py` | covered |
| 16 | W1-50 S4/S5/S6/S9 (lift refusal, terminal code, mirror) | 193 to `lifted` | `lifted` (G-6) | lifted, correct |
| 17 | W1-50 S13-S17, F1-F3 (commit judging) | 421 to `lifted` | `lifted` (G-5) | lifted, correct |
| 18 | W1-50 S7 (setting a freeze open to the orchestrator) | — | W1-28 `test_the_orchestrator_can_pause` (tier 1) | covered (F2 at tier 2) |
| 19 | W1-46 S1/F1/F8 (sandbox strict; no excludedCommands) | 38 → 11 | `test_w1_46_sandbox_settings.py` 11 functions, `launch_refusals` | covered (F2 at tier 2 for F8) |
| 20 | W2-58 S3 (test designer refused the branch's changes) | 53 → 12 | `test_the_test_designer_is_refused_the_files_the_branch_changes` | covered (F2 at tier 2) |
| 21 | W2-58 S7/S8 (tilde; interpreter flags) | 54 → 17 | `test_w2_58_tilde_and_test_runs.py` | covered (F2 at tier 2) |
| 22 | W2-58 S1, F1 (engineer refused own acceptance tests; still refused) | 47 → 8, 184 → 21 | `test_the_engineer_is_refused_its_tickets_acceptance_tests`, `test_w2_58_still_refused.py` | covered |
| 23 | W1-28 S3 (owner/orchestrator only; same on repeat) | `roles` 20 → 15 | `test_w1_28_roles.py` 15 functions | covered (F2 at tier 2) |
| 24 | W1-01 S1 (secret files denied) | 41 → 4 (25 deleted by D1) | `test_write_to_secret_file_is_denied` (4 classes) | covered |
| 25 | W2-50 S4 (never indexed) | 6 → 5 | `test_w2_50_never_indexed.py` | covered |
| 26 | W2-69, its 9 S and 4 F lines (secrets check over stores) | 352 to `lifted` | `lifted`. DEC-1045: with the switch off, nothing goes to gitleaks and the namespace filter stays (`test_off_the_namespace_filter_stands_and_nothing_is_given_to_gitleaks`, kept) | lifted, correct |
| 27 | W2-54 S9 (context-reproducibility green here), S8 (time limit) | M1/M1b merge 2 + 1 into 1 | the merged green-here case; `test_a_check_past_its_declared_limit_is_red` (F2) | covered |
| 28 | W2-54 S4 (sandboxed worker) | none (R-2 fixes it) | `test_inside_a_launched_sandboxed_worker_...` | covered, after R-2 |
| 29 | W1-30 S1, S5, F1 | 537 → 7 | `test_close_runs_acceptance_tests`, `test_regression_failure_blocks_close`, `test_close_record_has_packet_hash`, `..._tests_and_deviations`, `test_close_refuses_when_acceptance_tests_fail` | covered |
| 30 | W1-30 S2-S4, S6, S7, F2, F3 | to `lifted` | `lifted` (DEC-953; Q-7, Q-8, Q-11) | lifted, correct |
| 31 | W1-41, its 12 tool lines (S8 is a process line with no case today) | 242 → 78 | by rule; README sections name each line's cases (S1 `test_stages_a0_to_a4_each_leave_their_own_evidence_record`, S2/F2 `test_a_plan_that_is_not_the_audited_path_maps_plan_is_not_executed`, F1 `test_every_moved_file_is_byte_for_byte_what_it_was`, S3/F3, S4, S5, S6, S7, F4, S9 likewise) | covered by rule |

**Uncovered lines of kept features, as the list is written:** none. The lines that F2 names lose their case only
under the count's selection, not under the list's rule.

**F3: 78 lines (B §6) and 11 "(not placed)" README rows have no named case in the list.**
- The 78 lines sit in 13 capped suites. The 11 rows are in uncapped suites: W1-15 L3, W1-23 S1/S2, W2-55 KPI6,
  W2-61h F1/F3, W2-66 S13, W2-92 S5, W2-107 F3 (opt-in), W2-53 KPI8 (opt-in) and W2-68 S6 (opt-in).
- The brief asks for a named case. The list defers naming to the cut. For the uncapped suites, no function is
  removed, so whatever covered these rows still covers them, but nobody has shown that anything did.

Ordinary work: yes, because the cut's designer must name them.
Consequence: other (the rule requires a case per line, and D4-LIST step 2 checks it).

**F4: W1-26 S1/F1 enumerate the check families, and the rule keeps only "the file's first case".**
- Appendix B maps both lines to `test_w1_26_planted_defects.py` alone, and its rule keeps that file's first case.
- The file holds 19 separate functions, one per family. Among them is
  `test_planted_mutation_defect_implementer_covers_acceptance`, which tests core-mutation, a check Q-9 names as part
  of the floor.
- At 6 functions per line, the 19 families cannot all stay. B should state "fold the planted defects into one case
  asserting every family", as it does for W1-07, W1-08 and W2-49.

Ordinary work: yes, because the cap applied to the letter can drop it.
Consequence: other. Rule 1 refuses the engineer's write by role whatever `allowed_paths` say, so this is a second
check.

**F5: the live five-rule hook and G-14's `role_paths` have no case under `tests/`.**
- This was true before the cut, and both parts and decision 5 name it.
- G-1's landing check and the structural pass are tested only by the CTO's tool tests
  (`tools/test_land_dec1050.py`, `test_structural_pass.py`), which the cut does not touch.

Ordinary work: no, because the live hook changes only by an operator ACT, rehearsed with its own tests.
Consequence: fails open (a guard change with no full-run test). It is recorded as a row, not a round.
Recommendation: make decision 5 a step of the cut.

## D4-3, the lifted moves

Every move I traced lands on a lifted or switched-off feature:
- G-4: the read and write-side rules W1-02 lifts (DEC-820), W1-45's wide scope, W1-46's command forms, W2-50's guard
  half, `protected`, `runs`, `tools`.
- G-5: W1-03, W2-72, `unit/containment`, W1-50's commit judging, W2-106's post-tool lines.
- G-6: W1-50's lift refusal and mirror. G-3: W2-84.
- R-7: W2-59's Stop line.
- DEC-1045: W1-15, W1-16's token rule, W2-50's scan scale, W2-69, W2-71, W2-107, `unit/secrets_check` (the switch
  file is kept).
- DEC-953, Q-2..Q-11 and T-3: W1-26's policy, skill, citations and probe records; W1-30; W2-01; W2-07; W2-53; W2-68;
  `unit/close`.

The features still in force keep their cases in the full run:
- rule 1 (`test_independence`, `bash_writes`, `multiedit`, W1-45's three cases, W1-46's three into
  `tests/acceptance`, W2-50's two);
- rule 2 (W1-47's oracle, W1-46's held-out, `heldout*`, W2-58 (b)/(d));
- rule 3 (W1-01 S1, W2-58 F1);
- rule 4 (W1-04, W1-47's uv forms, `unit/install`);
- rule 5 (W1-33's auditor report path, `test_auditor_cannot_write_into_another_role_s_work`, `decide`'s auditor);
- G-14's counterpart reads (W2-58 (c));
- memory (every retrieval suite kept, with representatives);
- the merge queue's Q-1 (`unit/orchestration/test_merge_queue_q1.py`, kept and folded);
- G-1 and the structural pass (tool tests, see F5).

**No kept feature's cases are sent to `lifted`.**

**F6: D4-LIST decision 9 says "T-11 (CI off here, with W1-40's workflow cases to `lifted`)", and part B says the
opposite.**
- B §3 and §4 keep W1-40's cases in the full run (74 → 30, 0 to opt-in), revised to judge the template's workflow,
  and delete only the "this repository's workflow equals the render" cases.
- The counts follow B. Either reading fits T-11, but the summary and its source must agree before the owner decides.

Ordinary work: yes, because the applier reads the decisions as approved.
Consequence: other (30 cases in or out of the full run; T-11 lifts the template half later, P1-11).

**F7: "`lifted` runs whenever a change reaches its code" (D4-LIST decision 2, A PD-1) has no mechanism.**
- B's conftest leaves the list out of every run that does not opt in, and B says `select_tests.py` "needs no code
  change". So a scoped run never opts in.
- Either add the opt-in to `select_tests.py` for the named paths, or drop the clause.

Ordinary work: no, because the features are off here (T-10: "not reachable in ordinary work here while lifted").
Consequence: other.

**F8: A's PD-1 makes the guard's moves conditional on G-4, G-5 and G-6's switches being in the product. D4-LIST
decision 3 drops that condition.**
- The template's default guard is still the full guard today: no `guard.profile` exists, and CAP-62 is checked only
  in `decide.py`.

Ordinary work: no, because nothing here runs the full guard, and adopters come after D-9 and D-10.
Consequence: other. This is a sequencing line for the cut.

## D4-4, the moved D-3 items and today's reds

- **T-7:** confirmed.
  - `template/governance/kernel/schemas/test-map.schema.json` sets `additionalProperties: false` at line 31
    (couplings) and line 55 (top level).
  - `select.load_map` validates and returns `TEST_MAP_UNREADABLE` (select.py 75-85), so a `helpers:` key would refuse
    every selection.
  - A list beside the tool is the right form. Its risk (an importer broken by a W1-07 helper change is found only by
    the full run) is the one T-7 accepted.
- **Q-10:** confirmed and safe.
  - `acceptance_exemptions` (path map line 437) is read by W1-01's history case, and also by
    `test_w1_01_integration_merges.py` (lines 15 and 412, through `w1_01_support.acceptance_exemptions`).
  - Freezing it keeps both. Deleting it would turn both red.
- **Q-8:** safe.
  - B's list of readers leaves out W1-01 (`test_w1_01_history.py:114` and `integration_merges.py:231` write their own
    `accepted_history: []`) and W1-08 (`path_map_tool_keys` builds its own maps; the schema keeps the keys optional).
  - No full-run test reads this repository's `trailers_base` (line 295) or `accepted_history` (line 298), and
    `land.py` reads neither.
- **T-6:** confirmed.
  - `test-map.yaml` 128-131 hold the coupling.
  - `test_w2_66_live_test_map.py` 104-109 hold three tuples (path map, `.gitleaks.toml`, `template/.gitleaks.toml`) of
    one function, and all three need the edit.
  - `serial-only.txt` 100-102 already route the real-model files `nightly`.
  - A row for later: D-7 changes the path map's embedding fields, and after T-6 that no longer selects W1-19 or
    W1-21 in a scoped run, so only the full run checks it (accepted by T-6's row).
- **R-1, the PATH filter:** confirmed.
  - `w2_108_support.Driver.env()` at 484-486, `w2_126_support.env()` at 351-353 and `w2_54_support.env()` at 1665-1666
    all drop every folder that holds `ollama`.
  - W2-91's pattern (`w2_91_support.py` 320-333) links `gitleaks` from a scratch `tools/`, asserts that it holds no
    `ollama`, and never puts the dropped folder back. It is safe to copy.
- **R-2, the hook file:** confirmed and safe.
  - `w1_46_support.PROJECT_PATHSPECS` (107-108) lacks `.claude/hooks`.
  - The three hook files are tracked, and the live `PreToolUse` line runs `$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse.py`.
  - `test_w2_54_sandboxed_worker.py:49` imports `w1_46_support`.
  - In a planted project, `role_reads.section()` finds no `role_paths:` and does no check, and its link cache is under
    the temp folder, so the copy changes no behaviour beyond running the hook.
- **R-4:** confirmed. I ran W1-06's own helpers: `names_tool(own_text(DEC-1037), "gov")` is True; for DEC-1052 and
  DEC-1033 it is False. The registry's `gov` entry at line 235 cites DEC-1052. The fix is an owner line.
- **T-11:** B §4 matches its row and T-11. `push_workflows()` (w1_40_support 519) reads this repository's workflows
  today. See F6 for the summary's mismatch.

No finding here beyond F6.

## D4-5, the estimates

**F9: the time estimate's method is stated, but it scales the whole 11-02 wall linearly by case-seconds.**
- The 11-02 wall of 19,448 s includes setup (2,381 s), lock wait (898 s) and red re-runs. W1-19 and W1-21's
  real-model re-runs alone took about 4,900 s. None of these scales with case-seconds.
- Part A uses a 17:1 ratio (the 10-21 parallel phase), while 11-02's parallel phase ran 27,038 case-s in 3,567 s,
  about 7.6:1. So "320 s → 45-50 s" is too small by about two.
- Summing by phase:
  - setup: about 2,400 s;
  - serial: about 5,350 s less M1/M1b's about 2,200 s, so about 3,100 s;
  - parallel: about 6,700 case-s at 7.6:1, so about 900 s.
- That gives about 1.8 h before any red re-run. Setup plus the serial floor alone are about 1.5 h, so "1.5 to 2 h" is
  right in its middle but not at its lower end.
- The "±15 %" is labelled an estimate and stated for counts only. No basis is given for it, and it does not cover the
  time.
- Both parts mark their "after" figures "est." honestly.

Ordinary work: yes, because the owner plans D-10 from this figure.
Consequence: other. Suggested wording: "about 1.8 h plus red re-runs (est., by phase)".

## Summary of the verdict

There is no finding that is in scope, reachable in ordinary work and failing open or losing work. F5 fails open, but
it is "Ordinary work: no" (a row). **READY.**

The fixes should ride along with the cut (DEC-802):
- F1: restate 4,679 and 5,986, and add the 4 deletions.
- F2: recompute A's tier 2 named-first.
- F4: fold W1-26's planted defects.
- F6: make decision 9 match B §4.
- F9: restate the time by phase.
- F3, F7 and F8: as above.

```verdict
{"kpis": [
 {"kpi": "D4-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "D4-2", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "D4-3", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "D4-4", "verdict": "pass", "findings": []},
 {"kpi": "D4-5", "verdict": "pass", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
