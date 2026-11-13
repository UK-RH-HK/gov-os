# D4-LIST-A: the test suite cut, part A (the guard, its hooks, the launcher's role checks and the role files)

**For the owner first (DEC-1052, "the test suite"): nothing is deleted, merged or moved yet.** Written 2026-11-03 by
part A's test designer (CTO session 33b3628c, brief `EMG-d4-cut.md`). Tree read: the main tree at `w2/integrate`
`c39cffc1b191` (its `tests/` are the same as at `5522a603`). Nothing in any tree was changed. The boundary with part B
follows `D4-LIST-B.md` §1 (§2 below), and the totals use part B's two tiers, so the two lists add up. The scripts and
raw outputs are in `/tmp/gov-os-emg-d4a/`: `collect.txt`, `durations.py`, `cases.json`, `rules.py` (every action
below, as data), `apply.py`, `fates.json`, `tier2.py`, `kpimap.py`.

## Headline

| part A (24 suites, 10,633 cases) | cases | case-seconds |
|---|---:|---:|
| today | **10,633** | **5,389** |
| **full run, tier 1** (representative cases, no cap) | **1,404** | **824 (est.)** |
| **full run, tier 2** (part B's cap of 6 functions per KPI line; unit families folded) | **1,050** | **738 (est.)** |
| moved to the opt-in suite `lifted`, outside the full run | 6,684 | 3,155 |
| removed by parametrising to representative rows (every function keeps at least one row) | 2,516 | 1,409 (est.) |
| deleted (approved rows D1, D2, DEC-1040 (1)) | 29 | 0 |

- **With part B** (`D4-LIST-B.md`: tier 2 3,638, tier 1 4,591): **tier 2 gives 4,688 cases in the full run, tier 1
  5,995.** The owner's "about 5,000" is met by tier 2. (One overlap to correct in B: `tests/unit/hooks/test_w2_106_template_hook_lines.py`,
  44 cases, is counted in both; B's boundary table gives it to part A, so B's `unit/hooks` row is 75 → 31 before its
  fold. Without it the two parts are 9,322 + 10,633 = 19,955, the whole collection.)
- **Wall time (est.):** on 10-21 the nightly's parallel phase ran about 32,000 case-seconds in 1,906 s of wall (about
  17 to 1; INVESTIGATION-1 B2). At that ratio part A's share of the full run falls from about 320 s to about 50 s
  (tier 1) or 45 s (tier 2). Part A's share of `lifted` is about 185 s of wall when it runs.
- **No KPI line of a kept feature is left without a case in the full run.** Lines covered only in `lifted` are all
  lines of lifted features, each with the decision that lifts it (§4).
- **Two gaps that exist today, not made by this cut:** the live five-rule hook (`.claude/hooks/pretooluse.py`) and
  G-14's `role_paths` (`role_reads.py`) have **no case in `tests/`**; their 683 cases are in scratch
  (`drafts/g14/test_g14.py` 146, `drafts/act-guard-fix-4/test_guard_fix_4.py` 467, `guard4_check.py` 70). G-9
  (approved) moves them; not done (PD-4).
- **A red fix that comes with the cut (from part B, checked):** `tests/acceptance/W1-46/w1_46_support.py:107`
  `PROJECT_PATHSPECS` lacks `.claude/hooks`, and W2-59's planted project needs the same copy: the live settings'
  `preToolUse[0]` runs `$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse.py` since ACT-GUARD-FIX-4, so planted projects that
  copy the settings without the hook file go red. One test designer's change, with `Rewrite-Reason:` (B §5 R-2).

## 1. Sources and method

- **Cases:** `heavy_slot.sh python3 -m pytest tests --collect-only -q -o tmp_path_retention_policy=failed -p
  no:cacheprovider`, `PYTHONPATH=<main tree>/src`, `TMPDIR=/tmp/gov-os-emg-d4a`: `19955/19957 tests collected (2
  deselected) in 16.66s`, exit 0.
- **Seconds:** the inventory's method, re-run (its `/tmp/gov-os-emg-inventory/` is gone): the latest duration of each
  case across the 24 JUnit files of `.gov-runtime/scratch/orchestrator/log/close-build/*/` (2026-10-30 to 11-02) and
  `log/nightly/20261021-1743/`. 19,026 of 19,955 cases have one. In part A, 24 cases have none (W1-28 12, W1-50 12) and
  count as 0 s. Seconds are case time, not wall time.
- **What is lifted:** `DECISIONS-IN-FORCE.md` ("Lifted": DEC-953, the guard beyond its five rules) and the approved rows
  of `INVESTIGATION-1-COMBINED.md` (`P1-PLAN.md`'s first section): **G-1, G-2** (rules 1 and 5 judge only resolvable
  targets), **G-3** (the hidden half outside every tree, no guard rule; ACT-D8), **G-4** (the five rules as the
  product's default; the full guard built but off, "its suites run only under `full`"), **G-5** (post-command
  containment off, built), **G-6** (a plain freeze flag kept; the lift refusal and the mirror lifted), **G-9**,
  **G-14** (role separation by path checks, live since `4edd196c`, DEC-1059), **R-7** (the Stop hook's checkpoint),
  **T-10** (lifted features' suites out of the ordinary runs), DEC-1045 (gitleaks off here). B2's guard classes
  (INVESTIGATION-1-parts/B2.md) gave the first split by file name; every file was then read (module docstrings,
  function names, parameter ids).
- **The inventory's approved rows in part A:** D1 (W1-01, 28 cases) and D2 (unit install, 1) are counted as deleted.
  M2 (W1-45's two orchestrator scratch-write cases) now sits in `lifted`: do it there. M4's 20 families of
  `tests/unit/guard/test_decide.py` are in `lifted` too (folding optional).
- **Tier 1, representative cases ("R k"):** a function keeps k parameter rows. The counts take the first k rows in
  collection order; **the designer who makes the cut picks the rows that cover every class the KPI line names** (one
  row per secret-file class in W1-01, per install class in W1-04, per `uv` form and per tool kind in W1-47, the
  PreToolUse line in both sources in W2-106). "RF k" is R k plus a filter: the rows it names (the containment
  program's post-tool lines, the Stop hook's line) move to `lifted` instead of being cut.
- **Tier 2 (part B's levers, for totals that add up):** acceptance suites keep at most 6 functions per KPI line of
  their ticket, **after** every line's named cases (part B §2); unit families fold to one case per function (count
  only). Tier 2 bites in four of part A's suites: W1-02 (79 kept functions, cap 42: the cut falls on the 29
  held-out path-limit functions of DEC-574 and the deadline variants, never on `test_independence`), W1-28 (100, cap
  60), W1-46 (137, cap 120), W2-58 (71, cap 54). The tier 2 seconds are estimates (which functions go is the
  designer's).
- **KPI coverage (§4):** the inventory's §5 method. Each README's map ("KPI line | test functions") was parsed by
  `kpimap.py` against the cases' fates; where a README maps by file (W1-46, W1-47, W2-106) or numbers its lines
  differently from the ticket (W1-50), the lines were mapped by hand from the ticket's `kpis:` and the docstrings.

## 2. Which suites are part A, and how that was decided

1. `grep -rlE 'gov\.guard|gov guard|pretooluse|posttooluse|gov\.launch|gov launch|roles/|\.claude/agents|GOV_ROLE|settings\.json|subagentstop|sessionstart'`
   over every suite folder gave 79 candidate folders.
2. For each, the ticket's title and KPI lines and the files' docstrings were read. **A suite is part A when its
   subject is** the guard (PreToolUse: its five rules, its read and write judges, the command forms, the settings and
   permission rules, the post-command containment it ships with, the freeze it reads), **the guard's hook lines**
   (their form, pinning and failure), **the launcher's role checks** or **the role files**. Suites that only run the
   guard in their fixtures are part B's.
3. **Agreed with part B (its §1 and the coordinator's message):**
   - **Part A, the brief's named suites:** W1-01, W1-02, W1-03, W1-04, W1-05, W1-33, W1-47, W1-50, W2-58, W2-59
     (whole, 46), W2-84, `tests/unit/guard`.
   - **Part A, B's eleven boundary suites, all taken, whole:** W2-50 (636, its `secrets_scan_scale` and
     `never_indexed` included), W1-45, W2-65, W2-106 with `tests/unit/hooks/test_w2_106_template_hook_lines.py`,
     W1-46, W1-28 (154, the `gov pause` command's files included), W2-72, and unit `install`, `containment`, `pause`,
     `launch` (138, `test_command_modules.py` included).
   - **Part B's, although they touch hooks:** W1-29 (45), W1-38 (201), W1-49 (105), W2-05 (65), W2-62 (58),
     `tests/unit/gitenv` (56) and the rest of `tests/unit/hooks` (31). B's rows cover them (session and resume hooks,
     rulesync, git environment). Part A's earlier draft held parts of these; they are left to B so that nothing is
     counted twice.
4. Named in the brief but with no cases on `w2/integrate`: **W2-42a** (its tests are on its stopped worktree branch
   only), W2-90 (a support module, 0 cases), W2-70, W2-90b, W2-111, W2-114 (no folder).

## 3. The list, suite by suite

**The opt-in suite is part B's `lifted`** (one list, `tests/optin-lifted.txt`, read by `tests/conftest.py`; B §2 and
App. A), so that one list serves both parts. Part A's entries carry one of four tags in their `#` reason:
**`guard-full`** (the full guard's lifted rules: write scope and the durable root's scope, the command forms, the
settings, root-search and second-name read refusals, the run-time listing refusals, unknown tools, the CAP-62 escape
hatch, the bounds of the lifted read rule, the freeze's lift refusal, mirror and ancestry, the hidden half under every
tree), **`containment`** (the post-command check, `judge_commits`, the merge rules, its records, the template's
post-tool hook lines), **`gitleaks`** (W2-50's scan-scale cases, DEC-1045) and **`lifted-hooks`** (the Stop hook's
line, R-7).

| group | before (cases / s) | full run, tier 1 (cases / s) | tier 2 cases | `lifted` (cases / s) | removed by parametrising | deleted | action | reason | confidence |
|---|---:|---:|---:|---|---:|---:|---|---|---|
| W1-01 interim guardrails | 90 / 58 | 50 / 58 | 50 | 0 | 12 | 28 | delete D1; R 4 on the secret-file case; keep the rest | D1 approved (DEC-1040 (1)); the secret case's 16 rows are 4 classes × 2 tools × forms. `test_only_the_test_designer_commits_to_acceptance_tests` reads the path map's `acceptance_exemptions`: Q-10 freezes that list, it must not be deleted (B §4 item 7) | high |
| W1-02 PreToolUse guard | 3,655 / 926 | 111 / 84 | 52 | guard-full 3,282 / 751 | 262 | 0 | 30 files to `lifted`; 13 files R 1 to R 4 | G-4: write scope, allow-lists, role-less default-deny, unknown and listed tools, the protected-file read and second-name refusals (opened by DEC-820), the read rule's bounds, NUL, long paths; kept: rule 1 (`test_independence`, Bash and MultiEdit into the tests), rule 2 (the held-out path-limit cases), fail closed (`guard_failure`, deadlines), the plain freeze (G-6), the acting role (`subagent`), the hook (`guard_hook`) | high (moves); medium (k) |
| W1-03 containment | 364 / 307 | 0 / 0 | 0 | containment 364 / 307 | 0 | 0 | to `lifted` | G-5 (off, built) | high |
| W1-04 installs | 336 / 660 | 69 / 182 | 69 | 0 | 267 | 0 | R 1 to R 3; the registry schema kept | rule 4 kept; the breadth is roles × permission modes × spellings (B2-5: "stop extending it") | medium |
| W1-05 live hooks (the kernel's wiring) | 98 / 81 | 32 / 27 | 32 | guard-full 5 / 1, containment 10 / 6 | 51 | 0 | R 1 to R 2; role subagents kept | the hook registration, install, sudo and reads stay; role-less and ticket-path writes are G-4's, containment G-5's | medium |
| W1-28 `gov pause`, launcher rounds | 154 / 78 | 102 / 56 | 62 | 0 | 52 | 0 | R 1 to R 2 | the plain freeze (G-6), cancel and rollback, owner-gated pause, the launcher's product-spec session and temp folder, fixtures leave the held-out file out | medium |
| W1-33 role files | 113 / 7 | 112 / 6 | 112 | guard-full 1 / 0 | 0 | 0 | keep | each case reads another role's file or definition (static, ~0 s); the one moved case is W1-45's lifted wide scope | high |
| W1-45 orchestrator scope | 105 / 41 | 4 / 1 | 4 | guard-full 71 / 27, containment 25 / 12 | 5 | 0 | rule 1's orchestrator cases kept; the rest moved; M2 inside `lifted` | G-4 (the orchestrator's wide scope is write scope), G-5 (its records) | high |
| W1-46 the launcher | 493 / 308 | 147 / 114 | 130 | guard-full 101 / 36 | 245 | 0 | R 1 to R 2; the guard's command-form and write-scope cases to `lifted`; **the `PROJECT_PATHSPECS` fix** | the launcher's role checks are the floor (the sandbox's `Edit` deny on `tests/acceptance`, B2-1); the guard's `ln`/`mv -t`/`install`/option forms and the research write scope are G-4's; the forms into `tests/acceptance` stay | medium |
| W1-47 hardening | 980 / 405 | 108 / 36 | 108 | guard-full 69 / 29, containment 18 / 11 | 785 | 0 | R 2 to R 6; escape hatch and session role to `lifted`; failed commands to `lifted` | rule 2 (the oracle path) and rule 4 (`uv`) kept, one row per tool kind and per form; CAP-62 is beyond the five rules (PD-3); S7 is the wide scope (G-4) | medium |
| W1-50 freeze and attribution | 689 / 535 | 30 / 30 | 30 | containment 421 / 368, guard-full 193 / 108 | 45 | 0 | the plain freeze's 4 files R 1; the rest moved | G-6 (lift refusal, terminal code, ancestry, mirror), G-5 (commit attribution is containment's), G-4 (the lead's write scope) | high |
| W2-50 durable scratch root | 636 / 1,056 | 24 / 65 | 24 | guard-full 570 / 780, gitleaks 23 / 198 | 19 | 0 | the launcher's half and `never_indexed` R 1; the guard's half and the scan scale to `lifted` | the root's write scope is write scope (G-4; B2-8 "`runs.py` lifted"); the scan is gitleaks (DEC-1045, today in `nightly_only.txt`); two cases that refuse a write onto the acceptance tests stay (rule 1) | high |
| W2-58 Policy 2 | 808 / 366 | 106 / 86 | 77 | guard-full 153 / 53 | 549 | 0 | R 1 to R 3; run-time listings, the protected files' write side and the hook-listing helper to `lifted` | (a) secrets and (b) held-out kept (rules 3 and 2); (c) kept as G-14 keeps it in force (PD-6); (d) one row per function (G-3, PD-2); the reads-open breadth to 6 cases | medium |
| W2-59 the pinned judge | 46 / 29 | 39 / 24 | 39 | lifted-hooks 4 / 0 | 3 | 0 | RF 4 on the hook lines (the Stop line to `lifted`); R 1 on the rest; **the planted project's hook copy** (as W1-46) | R-7; the judge's checks, baseline, project root and version are small and stay | high |
| W2-65 hook lines fail closed | 10 / 4 | 10 / 4 | 10 | 0 | 0 | 0 | keep | fail closed is what every rule needs | high |
| W2-72 containment's merge rule | 73 / 41 | 0 / 0 | 0 | containment 73 / 41 | 0 | 0 | to `lifted` | G-5 | high |
| W2-84 hidden half under every tree | 329 / 390 | 0 / 0 | 0 | guard-full 329 / 390 | 0 | 0 | to `lifted`; deletion proposed at D-9 | G-3 (ACT-D8: "D-9 re-scopes the guard's hidden-half rule; no guard rule needed"); the in-tree glob now matches nothing | high (move); PD-2 |
| W2-106 template hook lines | 88 / 10 | 26 / 9 | 26 | containment 58 / 1 | 4 | 0 | RF 2: the PreToolUse line in the settings and the source kept; post-tool rows to `lifted` | G-5 takes the two post-tool lines out of the template's defaults | high |
| unit/containment | 114 / 24 | 0 / 0 | 0 | containment 114 / 24 | 0 | 0 | to `lifted` | G-5 | high |
| unit/guard | 1,103 / 44 | 163 / 26 | 105 | guard-full 780 / 12, containment 20 / 1 | 140 | 0 | kept rules' units kept or R 2 to R 12; the rest moved | kept: `heldout`, `heldout_limit`, `hook_deadline`, `reads` (secrets, hidden part, tilde, test runs), `research_install`, `decide`'s auditor, hook process, deny form, unparseable Bash, acting role, `_expand_token` (the live hook imports it), freeze state; moved: `decide`'s write scope and forms, `protected`, `protected_one_reader`, `runs`, `tools`, `w2_84_trees` (G-4, G-3), `records`, `w2_72_*` (G-5) | medium |
| unit/hooks: `test_w2_106_template_hook_lines.py` | 44 / 1 | 25 / 0 | 9 | 0 | 19 | 0 | R 3 | W2-106's builder table | high |
| unit/install | 144 / 18 | 89 / 11 | 45 | 0 | 54 | 1 | R 3; D2 | rule 4's detector tables; D2 approved | medium |
| unit/launch | 138 / 1 | 138 / 1 | 52 | 0 | 0 | 0 | keep (tier 2: fold) | the launcher's builder tests, 1 s together | high |
| unit/pause | 23 / 1 | 19 / 1 | 14 | 0 | 4 | 0 | R 3 | the plain freeze (G-6) | high |
| **total** | **10,633 / 5,389** | **1,404 / 824** | **1,050** | **6,684 / 3,155** | **2,516** | **29** | | | |

Part A's share of `lifted`: **guard-full 5,554 cases / 2,186 s; containment 1,103 / 771 s; gitleaks 23 / 198 s;
lifted-hooks 4 / 0 s.** File by file: annex.

## 4. KPI coverage kept

For every ticket whose cases are cut or moved: each KPI line, the kept case(s) in the full run that still cover it,
or "opt-in only" with the decision that lifts the feature. Case names are the test functions; "(n)" is the number of
rows kept. Unit tests cover no KPI line (DEC-136, regression evidence). A line not named here keeps every case it had.

**W1-01** (`DAEO-dtv3`)
- S1: `test_w1_01_settings_deny.py::test_write_to_secret_file_is_denied` (4: `.env*`, `*.pem`, `*.key`,
  `config/secrets*`), `test_w1_01_bootstrap_record.py::test_a_denied_attempt_is_recorded_for_each_path_class` (5); the
  acceptance-test half as the guard enforces it: W1-02 `test_engineer_cannot_write_under_acceptance_tests` (3), W1-33
  `test_only_the_test_designer_may_write_the_acceptance_tests` (5).
- S3: `test_interim_install_rule_is_recorded`, `test_install_rule_lists_every_agent_session_settings_file`,
  `test_a_denied_install_attempt_is_recorded`; "in force": W1-04 `test_an_install_by_any_other_role_is_denied` (3),
  `test_sudo_is_denied_to_every_role` (3).
- F1: `test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests` (kept). F2: retired (DEC-925
  item 1). F3: spent (the inventory's D1, approved).

**W1-02** (`DAEO-emkd`)
- S1 (writes only inside `allowed_paths` plus scratch): **opt-in only** (G-4: write scope is the full guard's;
  `allow_list`, `bash_writes`, `scratch`, `target_resolution`). Still touched in the full run by
  `test_a_role_subagent_writes_what_its_own_role_allows` (2).
- S2: `test_w1_02_test_independence.py`, its 11 functions (29), `test_engineer_bash_write_under_acceptance_tests_is_denied`
  (4), `test_a_ticket_that_names_the_acceptance_tests_gives_no_multiedit_there` (2),
  `test_the_test_designer_s_multiedit_is_allowed_under_the_acceptance_tests_only` (2).
- S3a (the freeze flag denies every write): `test_w1_02_freeze.py`, 7 functions (7); "no agent role lifts it" is
  **opt-in only** (G-6 lifts the lift refusal).
- S3b (frontmatter read directly): **opt-in only** (G-4; `allowed_paths` serve write scope only).
- S3c (p95 < 100 ms): `test_decision_p95_is_under_100_ms` (1 of 5 decisions; W2-111's re-cut of the latency cases is
  merged into this refactor by INVESTIGATION-1 §5).
- S4, F3 (no or unknown role is read-only): **opt-in only** (G-4: default-deny; `role_less_session`, `unknown_role`).
  The part the five rules keep, a role-less write into the tests refused:
  `test_no_ticket_role_can_write_under_acceptance_tests` (3).
- F1: **opt-in only** (G-4). F2: `test_w1_02_guard_failure.py`, 6 functions (9), `test_w1_02_deadline.py` (6),
  `test_w1_02_deadline_in_time.py` (6). CAP-39.a: `test_guard_hook_ships_in_the_kernel_template`,
  `test_guard_decides_before_the_tool_runs`.

**W1-03** (`DAEO-8qvp`): S1 to S3, F1, F2: **opt-in only** (G-5; `lifted`, tag `containment`).

**W1-04** (`DAEO-78bn`)
- S1, F1: `test_w1_04_install_rule.py`, 7 functions (19: one package manager, one `curl|sh`, one download into PATH
  per function), `test_w1_04_probe_findings.py` (17).
- S2: `test_w1_04_auto_mode.py`, 3 functions (6). S3: `test_w1_04_registry_schema.py` (12, unchanged).
- F2: `test_w1_04_sudo.py` (10), `test_sudo_in_a_later_part_of_the_command_is_denied_to_every_role` (2).
- F3: `test_w1_04_only_escalates.py` (5), `test_the_hook_never_gives_an_explicit_allow` among them (65 s).

**W1-05** (`DAEO-m7u4`)
- S1, F1: `test_a_hook_runs_before_every_tool` (2), `test_a_hook_runs_after_every_bash_call` (2),
  `test_hooks_are_not_switched_off`, `test_the_hooks_stay_wired_in_every_later_commit`,
  `test_an_install_by_any_other_role_is_denied` (2), `test_sudo_is_denied_to_every_role` (2),
  `test_ordinary_reads_stay_open`, `test_a_call_waits_under_100_ms_p95_for_the_hook` (1). Its containment cases are
  **opt-in only** (G-5); its role-less and ticket-path cases **opt-in only** (G-4).
- S2: `test_the_operator_diff_check_is_recorded_as_retired`. S3 to S7: `test_w1_05_role_subagents.py` (11,
  unchanged). F2: spent (a one-time order at W1-05's close; its case was retired by W2-70).

**W1-28** (`DAEO-9279`)
- S1, F1: `test_w1_28_freeze.py`, 8 functions (10). F2: `test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else`.
- S2: `test_w1_28_cancel.py` (2 rows per function), `test_w1_28_rollback.py` (2 per function), `test_w1_28_command.py` (1 per function).
- S3: `test_w1_28_roles.py`, 15 functions (15), `test_w1_28_repeat.py` (1 per function). S4: `test_w1_28_fixture_copies.py` (9).
- S5: `test_w1_28_launch_temp_folder.py` (9). S6: `test_w1_28_launch_product_spec.py`, 23 functions (23).
- Tier 2 (cap 60 functions for 10 lines): the cut falls on `launch_product_spec`'s and `roles`' review-round
  variants beyond 6 per line; each line keeps the cases named above first.

**W1-33** (`DAEO-xog0`): every line keeps its cases (112 of 113). The one case moved,
`test_the_orchestrator_may_write_anywhere_else_in_the_repository`, is W1-45's wide scope (G-4); S4's statement of that
scope in the definition stays covered by `test_the_orchestrator_definition_states_its_write_scope`.

**W1-45** (`DAEO-6cc2`)
- S2, F1: `test_orchestrator_cannot_write_under_acceptance_tests` (2),
  `test_orchestrator_bash_write_under_acceptance_tests_is_denied` (1),
  `test_orchestrator_subagent_acceptance_denied_in_orchestrator_session` (1).
- S1, S5, S7, F2, F3 and the DEC-176/DEC-178 rows: **opt-in only** (G-4: write scope). S3, S4 and the DEC-177 row:
  **opt-in only** (G-5). S6, F4: process lines; no case today.

**W1-46** (`DAEO-jdqr`)
- S1, F1, F2, F8: `test_w1_46_sandbox_settings.py`, 11 functions (11). S2: `test_w1_46_role_settings.py` (8),
  `test_the_role_and_the_ticket_reach_the_session_and_its_hooks`.
- S3: `test_engineer_test_designer_and_auditor_get_an_empty_allowlist`, `test_w1_46_research_allowlist.py` (11),
  `test_the_research_allowlist_refuses_a_domain_that_is_not_on_it`.
- S4: `test_w1_46_research_fence.py`, the launcher's deny list (7), `test_a_research_bash_write_to_a_sibling_directory_fails`;
  the guard's own research refusals are **opt-in only** (G-4).
- S5: `test_the_research_role_has_a_role_file`, `test_the_role_file_states_the_six_parts_the_kpi_names`,
  `test_the_roster_has_an_entry_for_the_research_role`. S6, F6: `test_w1_46_research_installs.py` (19).
- S7: `test_the_launcher_sets_a_temp_directory_of_the_sessions_own`, `test_each_session_uses_a_temp_directory_of_its_own`.
- S8: `test_an_opaque_bash_write_outside_the_repository_fails` (1), `test_a_file_tool_write_outside_the_repository_is_refused`.
- S9: `test_w1_46_held_out.py` (9), `test_the_held_out_directory_looks_empty_from_the_sessions_bash`.
- S10: `test_the_built_settings_deny_edits_under_gov_runtime`, `test_each_name_under_gov_runtime_at_launch_has_a_literal_edit_deny_rule`,
  `test_a_bash_write_under_gov_runtime_fails_and_scratch_stays_writable`; the guard's `.gov-runtime` refusals are
  **opt-in only** (G-4).
- S11: `test_w1_46_protected_trees.py` (8), `test_an_opaque_bash_write_to_the_acceptance_tests_the_tickets_and_dot_claude_fails`.
- F3, F4, F7: `test_w1_46_research_installs.py`, `test_a_research_install_outside_the_repository_fails_at_the_write_fence`.
  F5: `test_a_research_write_to_a_new_path_outside_the_folder_is_refused_or_reported` (the guard half opt-in).
  F9: `test_no_file_of_this_ticket_names_a_held_out_path`.
- The DEC-311/DEC-334 guard forms (`ln`, hard links, `mv -t`, `install`, options after the destination): **opt-in only**
  (G-4), but for the three into `tests/acceptance` (rule 1): `test_the_guard_refuses_install_into_the_acceptance_tests_and_the_tickets`,
  `test_the_test_designer_may_hard_link_one_acceptance_test_to_another_name_there`,
  `test_the_guard_refuses_cp_with_the_acceptance_tests_as_the_target_directory_option`.

**W1-47** (`DAEO-o4fg`)
- S1, F1 (the `dangerouslyDisableSandbox` escape hatch, CAP-62): **opt-in only** (beyond the five rules, DEC-953; PD-3).
- S2 (containment after a failed command): **opt-in only** (G-5).
- S3, F3, F4, F7: `test_w1_47_oracle_rule.py` (7, unchanged).
- S4, F2: `test_a_call_that_names_the_oracle_path_is_denied` (6: Read, Grep, Glob, Bash, a write tool, another tool),
  its 8 sibling functions in `oracle_guard` (20), `test_w1_47_oracle_naming.py` (19), `test_w1_47_oracle_config.py` (10),
  `test_the_template_s_guard_hides_a_held_out_path`.
- S5, F5: `test_w1_47_settings_rules.py` (10). S6, F6: `test_w1_47_uv_installs.py`, 6 functions (23: `uv add`,
  `uv sync`, `uv run --with`, `uvx`).
- S7 (no wide scope without a session role): **opt-in only** (G-4: the wide scope is write scope).

**W1-50** (`DAEO-xnbx`)
- S1: `test_w1_50_freeze_marker.py` (7), `test_w1_50_freeze_guard_reading.py` (10). S2: `test_w1_50_freeze_launcher.py`
  (8). S12: `test_w1_50_freeze_fixture_settings.py` (5).
- S4, S5, S6, S9: **opt-in only** (G-6: the lift refusal, the terminal code, the ancestry and the mirror are lifted).
  S7: **opt-in only** for the owner's terminal; the orchestrator's half stays by W1-28 `test_the_orchestrator_can_pause`.
- S11 (the ticket lead's write scope): **opt-in only** (G-4).
- S3, S8, S10, S13 to S17, F1 to F3: **opt-in only** (G-5: commit attribution and the flag's restore are containment's).

**W2-50** (`DAEO-kl5e`)
- S1, S2 (the launcher's half), S3: `test_w2_50_launcher.py` (10), the four launcher functions of `review_findings`
  (4), the two of `owner_answers` (2).
- S1, S2 (the guard's half), F1 to F6: **opt-in only** (G-4: the durable root's scope is write scope). Rule 1's two
  cases stay: `test_a_copy_into_a_repository_folder_that_lands_on_a_link_to_the_acceptance_test_is_refused` (1),
  `test_the_acceptance_test_named_directly_is_refused`.
- S4: `test_w2_50_never_indexed.py`, one row per function (5).
- S5, S6, F7 (the secrets scan on large stores, reuse by hash): **opt-in only** (DEC-1045: gitleaks off here;
  `test_w2_50_secrets_scan_scale.py`, today in `nightly_only.txt`).

**W2-58** (`DAEO-5j8b`)
- S1: `test_the_engineer_is_refused_its_tickets_acceptance_tests` (2), `test_the_engineer_still_runs_its_tests_and_reads_the_rest`
  (2), the subagent and WBS-id functions of `test_w2_58_review.py` (1 each).
- S2: `test_w2_58_launched_sessions.py` (6). S3: `test_w2_58_test_designer.py` (12). S4: `test_w2_58_evaluation_sets.py`,
  one row per function (10). S5: `test_w2_58_reads_open.py` (6: the held-out list and the settings readable, searches
  of `governance/` and `.claude/` open, root searches open). S6: `test_w2_58_auditor.py` (4). S7:
  `test_w2_58_tilde_and_test_runs.py` (17). S8: `test_the_engineer_runs_its_tests_with_interpreter_flags_or_under_coverage` (2).
- F1: `test_w2_58_still_refused.py` (21), `test_a_credential_file_is_refused` (3),
  `test_every_role_is_refused_each_credential_file_by_the_read_tool` (1), `test_w2_58_fails_closed.py` (6, unchanged).
  The run-time listing forms, the protected files' write side and the hook-listing helper: **opt-in only** (the
  run-time listing refusal is a command form, G-1/G-2/B2-3; the write side is `protected.py`, G-4).

**W2-59** (`DAEO-kh9l`)
- S1, F1 (the pinned judge's declared checks): `test_w2_59_judge_checks.py`, one row per function (6).
- S2: `test_w2_59_hook_lines.py` (15), `test_w2_59_hook_lines_worker_env.py` (8), every line but the Stop hook's; the
  Stop line's rows **opt-in only** (R-7). The four `preToolUse[0]` cases need the planted project's copy of
  `.claude/hooks/` (B §5 R-2).
- S3: `test_w2_59_project_root.py` (3). S4, F1 (the wheel ships the baseline): `test_w2_59_baseline.py` (4). S5:
  `test_w2_59_version.py` (3).

**W2-65** (`DAEO-e82f`): unchanged (10).

**W2-72** (`DAEO-ye2a`): S1 to S5, F1 to F3: **opt-in only** (G-5).

**W2-84** (`DAEO-m1u3`): S1 to S6, F1 to F5: **opt-in only** (G-3; PD-2). Until D-9, the hidden half's refusal in the
main tree stays covered in the full run by W2-58's S4 cases above.

**W2-106** (`DAEO-0mtg`)
- S1, F1: `test_w2_106_form.py` (5: the PreToolUse line in the settings and in the rulesync source).
- S2, F2: `test_w2_106_fail_closed.py` (8). S3, F3: `test_w2_106_generated_project.py` (3). S4, F4:
  `test_the_settings_and_the_rulesync_source_hold_the_same_guard_line[PreToolUse]`,
  `test_the_generated_settings_hold_the_template_s_guard_line[PreToolUse]`.
- The post-tool (containment) lines' rows: **opt-in only** (G-5 removes those lines from the template's defaults).

## 5. Totals for part A

- **Cases:** 10,633 before. After: **tier 1 1,404, tier 2 1,050 in the full run**; 6,684 in `lifted` (guard-full
  5,554, containment 1,103, gitleaks 23, lifted-hooks 4); 2,516 parameter rows removed (tier 1); 29 deleted (D1, D2).
- **Case-seconds:** 5,389 before. After: **about 824 (tier 1) or 738 (tier 2) in the full run (est.)**; 3,155 in
  `lifted`; about 1,409 removed (est.).
- **With part B:** tier 2 3,638 + 1,050 = **4,688**; tier 1 4,591 + 1,404 = **5,995** (B's `unit/hooks` row less the
  44 cases of `test_w2_106_template_hook_lines.py`, which are part A's).
- **Wall time of the full run (est.):** part A's share from about 320 s to about 50 s (tier 1) or 45 s (tier 2), at the
  10-21 parallel ratio of about 17 to 1. The heaviest kept cases: W1-04 `test_the_hook_never_gives_an_explicit_allow`
  (65 s), W1-01 `test_the_integration_merges_of_this_repository_pass` (33 s), W2-50 `never_indexed`'s adopted clone
  (31 s), W1-02 `test_a_decision_still_running_at_the_deadline_is_refused` (2 rows of 7, 23 s: the guard's deadline is
  20 s), `tests/unit/guard/test_hook_deadline.py` (20 s), W1-01 `test_only_the_test_designer_commits_to_acceptance_tests`
  (17 s), W1-50 `test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path` (16 s), W1-05's p95 case (16 s),
  W1-46's real research install (16 s) and W2-58's two launched sessions (13 s, 10 s).
- **The guard's ~9,000 (the owner's figure):** the inventory's seven guard suites (W1-02, unit/guard, W1-47, W2-58,
  W2-50, W2-84, W1-04: 7,847 cases today) keep 581 in the full run at tier 1.

## 6. Lines not placed, and what needs the owner

**Not placed in `tests/` (no case exists today, before any cut):**
1. **G-14's `role_paths`** (DEC-1052 G-14, DEC-1054, DEC-1056, DEC-1059): its cases are scratch only
   (`drafts/g14/test_g14.py`, 146; 5 in `guard4_check.py`). No case in the full suite reads `role_reads.py`.
2. **The live five-rule hook** (`.claude/hooks/pretooluse.py`: rules 1 to 5 as wired here, the catastrophic `rm`):
   `test_guard_fix_4.py` (467) and `guard4_check.py` (70) are scratch only. The full suite tests the product's guard
   (the template's hook and `src/gov/guard/`), which the live hook imports for rules 2 to 4.
3. W2-42a's 13 lines: tests only on its stopped worktree branch.
4. Process lines with no case, as before: W1-45 S6, F4. Spent or retired: W1-01 F2, F3; W1-05 F2.

**Proposed decisions (each with a recommendation):**
- **PD-1, the opt-in suite.** Part A's 6,684 cases join part B's `lifted` (`tests/optin-lifted.txt`, read by
  `tests/conftest.py`, outside the full run), each line tagged `guard-full`, `containment`, `gitleaks` or
  `lifted-hooks`, so one list serves both parts; part A's lines go after G-4's, G-5's and G-6's switches are in the
  product, or now if the owner prefers (the suites test the full guard, which is still the template's default
  today). It runs as B §4 item 4 proposes (once, report-only, in D-10's window; and when a change reaches its code:
  `src/gov/guard/containment*.py`, `decide.py`, `protected.py`, `runs.py`, `src/gov/pause/`, the template's hooks).
  **Recommended: opt-in, not delete**: G-4, G-5 and G-6 keep the features built and G-4's row says "its suites run
  only under `full`"; deleting would leave about 3,100 lines of built guard code untested (B2's estimate).
  Confidence high.
- **PD-2, the hidden half's guard rule (G-3).** W2-84 (329) and `tests/unit/guard/test_w2_84_trees.py` (34) test a rule
  ACT-D8 says D-9 re-scopes ("no guard rule needed"). **Recommended:** opt-in now; delete them with the rule at D-9,
  and W2-58's 10 (d) cases with it. Confidence high.
- **PD-3, the CAP-62 escape hatch** (W1-47 S1, F1; 49 cases, 1 in the template case). It is not one of the five rules,
  so it goes with `guard-full`. **Recommended:** opt-in, unless the owner wants the five-rule profile (G-4's ticket) to
  refuse `dangerouslyDisableSandbox` too; then 2 cases stay in the full run. Confidence medium: it is a one-line check
  against a sandbox escape.
- **PD-4, G-9 done with the cut.** Move the live hook's tests into `tests/unit/hooks/`, cut to representative cases
  (about 60, est.: rules 1 to 5, `rm`, `role_paths`, fail closed), so that the rules as wired here and G-14 have cases
  in the full run. **Recommended: yes**, as one CTO-tools change with one review. Confidence high.
- **PD-5, the representative rule and the tier.** Approve "R k" (§1): the designer keeps k rows per function, chosen
  to cover every class each KPI line names; one independent reviewer checks §4's map. **Recommended: tier 2**, as
  part B recommends, since only tier 2 meets "about 5,000" (4,688 with B); in part A tier 2 bites in W1-02, W1-28,
  W1-46 and W2-58 only, after every line's named cases. The after counts may move by about ±15 % when rows are chosen
  (est.). Confidence medium.
- **PD-6, W2-58's (c), the counterpart reads.** Kept in the full run (about 30 cases) because G-14 keeps the rule in
  force, although the product's implementation (`reads.py`, git-based) is not G-14's `role_paths`. D-9 places G-14's
  KPI lines; if the product adopts `role_paths`, a test designer rewrites W2-58's (c) cases then. Confidence medium.

## Annex: file by file (mixed suites; wholly moved files are grouped per suite)

Tier 1 figures; "rule" is the action of `rules.py` (K keep, R k, RF k, O to `lifted`, D delete).
**W1-01**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_01_bootstrap_record.py` | 9 / 0 | 9 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w1_01_history.py` | 14 / 19 | 11 / 19 | 0 (0 s) | 0 | 3 | D, K |
| `test_w1_01_integration_merges.py` | 26 / 40 | 26 / 40 | 0 (0 s) | 0 | 0 | K |
| `test_w1_01_settings_deny.py` | 41 / 0 | 4 / 0 | 0 (0 s) | 12 | 25 | D, R4 |

**W1-02**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_02_bash_writes.py` | 50 / 27 | 4 / 1 | 38 guard-full (22 s) | 8 | 0 | O, R4 |
| `test_w1_02_deadline.py` | 14 / 23 | 6 / 23 | 0 (0 s) | 8 | 0 | R2 |
| `test_w1_02_deadline_in_time.py` | 12 / 7 | 6 / 7 | 0 (0 s) | 6 | 0 | R1 |
| `test_w1_02_freeze.py` | 21 / 10 | 7 / 4 | 1 guard-full (2 s) | 13 | 0 | R1, O |
| `test_w1_02_guard_failure.py` | 26 / 13 | 9 / 7 | 0 (0 s) | 17 | 0 | R2 |
| `test_w1_02_guard_hook.py` | 7 / 16 | 3 / 3 | 0 (0 s) | 4 | 0 | R1 |
| `test_w1_02_multiedit.py` | 179 / 35 | 6 / 2 | 153 guard-full (30 s) | 20 | 0 | O, R2, R1 |
| `test_w1_02_path_limit_boundary.py` | 47 / 4 | 11 / 1 | 0 (0 s) | 36 | 0 | R1 |
| `test_w1_02_path_limit_time.py` | 26 / 3 | 7 / 1 | 0 (0 s) | 19 | 0 | R1 |
| `test_w1_02_path_limit_unchanged.py` | 56 / 5 | 12 / 1 | 0 (0 s) | 44 | 0 | R1 |
| `test_w1_02_subagent.py` | 52 / 40 | 9 / 7 | 0 (0 s) | 43 | 0 | R2 |
| `test_w1_02_target_resolution.py` | 46 / 34 | 2 / 9 | 44 guard-full (25 s) | 0 | 0 | O, K |
| `test_w1_02_test_independence.py` | 73 / 37 | 29 / 19 | 0 (0 s) | 44 | 0 | R3 |
| the other 30 file(s): `w1_02_allow_list`, `w1_02_bounded_time`, `w1_02_brace_bound`, `w1_02_copies`, `w1_02_copies_open`, `w1_02_daily_spellings`, `w1_02_fix_round_time`, `w1_02_holding_folders`, `w1_02_hook_listing`, `w1_02_hook_listing_home_paths`, `w1_02_hook_listing_paths`, `w1_02_listed_tools`, `w1_02_long_paths`, `w1_02_name_filters`, `w1_02_nul_bytes`, `w1_02_numbered_redirects`, `w1_02_protected_reads`, `w1_02_protected_reads_forms`, `w1_02_protected_reads_open`, `w1_02_refusals_beyond_the_order`, `w1_02_role_less_session`, `w1_02_root_searches`, `w1_02_scratch`, `w1_02_search_on_a_pipe`, `w1_02_second_names`, `w1_02_shell_keywords`, `w1_02_unknown_role`, `w1_02_unknown_tools`, `w1_02_unknown_tools_failure`, `w1_02_wildcard_globs` | 3046 / 672 | 0 / 0 | 3046 guard-full (672 s) | 0 | 0 | O |

**W1-04**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_04_auto_mode.py` | 36 / 85 | 6 / 26 | 0 (0 s) | 30 | 0 | R2 |
| `test_w1_04_install_rule.py` | 106 / 146 | 19 / 33 | 0 (0 s) | 87 | 0 | R3 |
| `test_w1_04_only_escalates.py` | 11 / 83 | 5 / 71 | 0 (0 s) | 6 | 0 | R1 |
| `test_w1_04_probe_findings.py` | 128 / 292 | 17 / 37 | 0 (0 s) | 111 | 0 | R2, R1 |
| `test_w1_04_registry_schema.py` | 12 / 0 | 12 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w1_04_sudo.py` | 43 / 54 | 10 / 16 | 0 (0 s) | 33 | 0 | R3 |

**W1-05**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_05_live_hooks.py` | 86 / 79 | 20 / 25 | 5 guard-full, 10 containment (7 s) | 51 | 0 | R2, O, R1 |
| `test_w1_05_role_subagents.py` | 11 / 2 | 11 / 2 | 0 (0 s) | 0 | 0 | K |
| `test_w1_05_switch_over_record.py` | 1 / 0 | 1 / 0 | 0 (0 s) | 0 | 0 | R2 |

**W1-28**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_28_cancel.py` | 9 / 5 | 9 / 5 | 0 (0 s) | 0 | 0 | R2 |
| `test_w1_28_command.py` | 5 / 1 | 3 / 1 | 0 (0 s) | 2 | 0 | R1 |
| `test_w1_28_fixture_copies.py` | 21 / 9 | 9 / 9 | 0 (0 s) | 12 | 0 | R1 |
| `test_w1_28_freeze.py` | 13 / 8 | 10 / 5 | 0 (0 s) | 3 | 0 | R2 |
| `test_w1_28_launch_product_spec.py` | 43 / 25 | 23 / 15 | 0 (0 s) | 20 | 0 | R1 |
| `test_w1_28_launch_temp_folder.py` | 19 / 10 | 9 / 5 | 0 (0 s) | 10 | 0 | R1 |
| `test_w1_28_repeat.py` | 4 / 2 | 4 / 2 | 0 (0 s) | 0 | 0 | R1 |
| `test_w1_28_roles.py` | 20 / 9 | 15 / 7 | 0 (0 s) | 5 | 0 | R1 |
| `test_w1_28_rollback.py` | 20 / 9 | 20 / 9 | 0 (0 s) | 0 | 0 | R2 |

**W1-33**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_33_agent_definitions.py` | 33 / 2 | 33 / 2 | 0 (0 s) | 0 | 0 | K |
| `test_w1_33_guard_and_launcher.py` | 16 / 4 | 15 / 4 | 1 guard-full (0 s) | 0 | 0 | K, O |
| `test_w1_33_kernel_role_files.py` | 52 / 0 | 52 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w1_33_roster.py` | 12 / 0 | 12 / 0 | 0 (0 s) | 0 | 0 | K |

**W1-45**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_45_orchestrator_scope.py` | 34 / 13 | 3 / 1 | 26 guard-full (11 s) | 5 | 0 | O, R2, R1 |
| `test_w1_45_subagent_scope.py` | 31 / 13 | 1 / 0 | 28 guard-full, 2 containment (12 s) | 0 | 0 | O, K |
| the other 2 file(s): `w1_45_containment`, `w1_45_records` | 23 / 10 | 0 / 0 | 23 containment (10 s) | 0 | 0 | O |
| the other 1 file(s): `w1_45_gov_runtime` | 17 / 5 | 0 / 0 | 17 guard-full (5 s) | 0 | 0 | O |

**W1-46**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_46_bypass_and_added_directories.py` | 28 / 20 | 7 / 5 | 0 (0 s) | 21 | 0 | R1 |
| `test_w1_46_duplicate_keys.py` | 16 / 14 | 6 / 5 | 0 (0 s) | 10 | 0 | R1 |
| `test_w1_46_exit_codes.py` | 6 / 6 | 4 / 5 | 0 (0 s) | 2 | 0 | R1 |
| `test_w1_46_experiment_folder.py` | 14 / 12 | 6 / 5 | 0 (0 s) | 8 | 0 | R1 |
| `test_w1_46_guard_wiring.py` | 21 / 15 | 8 / 6 | 0 (0 s) | 13 | 0 | R1 |
| `test_w1_46_hard_links_mv_and_install.py` | 15 / 9 | 2 / 1 | 10 guard-full (8 s) | 3 | 0 | O, K, R1 |
| `test_w1_46_held_out.py` | 21 / 12 | 9 / 5 | 0 (0 s) | 12 | 0 | R2 |
| `test_w1_46_install_spellings.py` | 7 / 4 | 5 / 2 | 0 (0 s) | 2 | 0 | R1 |
| `test_w1_46_launch_refusals.py` | 25 / 19 | 8 / 6 | 0 (0 s) | 17 | 0 | R1 |
| `test_w1_46_links_and_cp_targets.py` | 15 / 4 | 1 / 0 | 11 guard-full (3 s) | 3 | 0 | O, R1 |
| `test_w1_46_live_sessions.py` | 36 / 24 | 15 / 24 | 0 (0 s) | 21 | 0 | R1 |
| `test_w1_46_protected_trees.py` | 22 / 13 | 8 / 5 | 0 (0 s) | 14 | 0 | R1, R2 |
| `test_w1_46_research_allowlist.py` | 18 / 13 | 11 / 8 | 0 (0 s) | 7 | 0 | R1 |
| `test_w1_46_research_fence.py` | 12 / 8 | 7 / 6 | 3 guard-full (0 s) | 2 | 0 | R1, O |
| `test_w1_46_research_installs.py` | 72 / 41 | 19 / 7 | 0 (0 s) | 53 | 0 | R2 |
| `test_w1_46_research_role.py` | 40 / 11 | 8 / 3 | 31 guard-full (7 s) | 1 | 0 | R1, O |
| `test_w1_46_role_settings.py` | 36 / 25 | 8 / 7 | 8 guard-full (2 s) | 20 | 0 | R1, O |
| `test_w1_46_runtime_and_ln.py` | 44 / 26 | 4 / 4 | 31 guard-full (13 s) | 9 | 0 | R1, O |
| `test_w1_46_sandbox_settings.py` | 38 / 30 | 11 / 8 | 0 (0 s) | 27 | 0 | R1 |
| the other 1 file(s): `w1_46_options_after_the_destination` | 7 / 2 | 0 / 0 | 7 guard-full (2 s) | 0 | 0 | O |

**W1-47**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_47_kernel_template.py` | 30 / 4 | 7 / 1 | 2 guard-full, 5 containment (2 s) | 16 | 0 | R2, O, R1 |
| `test_w1_47_oracle_config.py` | 99 / 38 | 10 / 4 | 0 (0 s) | 89 | 0 | R3, R4 |
| `test_w1_47_oracle_guard.py` | 281 / 110 | 26 / 10 | 0 (0 s) | 255 | 0 | R6, R3 |
| `test_w1_47_oracle_naming.py` | 181 / 74 | 19 / 9 | 1 guard-full (0 s) | 161 | 0 | R3, O |
| `test_w1_47_oracle_rule.py` | 7 / 0 | 7 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w1_47_settings_rules.py` | 23 / 0 | 10 / 0 | 0 (0 s) | 13 | 0 | R2 |
| `test_w1_47_template_hook_time_limit.py` | 13 / 0 | 6 / 0 | 0 (0 s) | 7 | 0 | R2 |
| `test_w1_47_uv_installs.py` | 267 / 142 | 23 / 11 | 0 (0 s) | 244 | 0 | R4 |
| the other 2 file(s): `w1_47_escape_hatch`, `w1_47_session_role` | 66 / 28 | 0 / 0 | 66 guard-full (28 s) | 0 | 0 | O |
| the other 1 file(s): `w1_47_failed_commands` | 13 / 9 | 0 / 0 | 13 containment (9 s) | 0 | 0 | O |

**W1-50**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w1_50_freeze_fixture_settings.py` | 14 / 0 | 5 / 0 | 0 (0 s) | 9 | 0 | R1 |
| `test_w1_50_freeze_guard_reading.py` | 33 / 21 | 10 / 5 | 0 (0 s) | 23 | 0 | R1 |
| `test_w1_50_freeze_launcher.py` | 17 / 32 | 8 / 22 | 0 (0 s) | 9 | 0 | R1 |
| `test_w1_50_freeze_marker.py` | 11 / 5 | 7 / 3 | 0 (0 s) | 4 | 0 | R1 |
| the other 43 file(s): `w1_50_acceptance_test_changed_on_both_sides`, `w1_50_author_chosen_bytes`, `w1_50_callers`, `w1_50_close_commit`, `w1_50_close_commit_edges`, `w1_50_committed_path_names`, `w1_50_finding_record`, `w1_50_forward_moves`, `w1_50_freeze_flag_comparison`, `w1_50_freeze_mirror_restore`, `w1_50_grafts`, `w1_50_integration_merge`, `w1_50_judge_commits`, `w1_50_merge_commit_file_that_equals_one_parent_s_version`, `w1_50_merge_commit_own_change_of_a_ticket_file`, `w1_50_merge_commit_own_change_of_an_acceptance_test`, `w1_50_merge_commit_own_changes`, `w1_50_merge_read_by_the_merge_base`, `w1_50_merge_that_drops_a_parent_s_change`, `w1_50_merge_that_takes_each_side_s_change`, `w1_50_merge_that_undoes_earlier_commits`, `w1_50_merge_with_an_earlier_parent`, `w1_50_mirror_tripwire`, `w1_50_move_of_very_many_merge_commits`, `w1_50_no_trailers`, `w1_50_orchestrator_task_names`, `w1_50_owner_commit`, `w1_50_owner_commit_that_arrives`, `w1_50_read_merge_brought`, `w1_50_read_merge_every_parent`, `w1_50_read_merge_helper`, `w1_50_repository_settings`, `w1_50_review_of_the_symmetric_rule`, `w1_50_role_owner_unseen_characters`, `w1_50_rollback_commits`, `w1_50_ticket_file_at_head_and_in_the_tree`, `w1_50_ticket_file_changed_on_both_sides`, `w1_50_ticket_file_commit_in_a_worker_s_call`, `w1_50_ticket_state`, `w1_50_trailer_forms`, `w1_50_uncommitted_ticket_state`, `w1_50_worker_commit`, `w1_50_worker_commit_of_a_ticket_file` | 421 / 368 | 0 / 0 | 421 containment (368 s) | 0 | 0 | O |
| the other 11 file(s): `w1_50_freeze_lift_ancestry`, `w1_50_freeze_lift_guard_rule`, `w1_50_freeze_lift_terminal`, `w1_50_freeze_live_pause`, `w1_50_freeze_mirror`, `w1_50_freeze_near_spellings`, `w1_50_freeze_pause_links`, `w1_50_freeze_records_file`, `w1_50_freeze_rollback_flag`, `w1_50_freeze_seam`, `w1_50_ticket_lead_role` | 193 / 108 | 0 / 0 | 193 guard-full (108 s) | 0 | 0 | O |

**W2-106**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w2_106_fail_closed.py` | 24 / 5 | 8 / 5 | 16 containment (0 s) | 0 | 0 | RF2 |
| `test_w2_106_form.py` | 15 / 0 | 5 / 0 | 10 containment (0 s) | 0 | 0 | RF2 |
| `test_w2_106_generated_project.py` | 7 / 4 | 3 / 4 | 4 containment (0 s) | 0 | 0 | RF9 |
| `test_w2_106_interpreter.py` | 42 / 1 | 10 / 0 | 28 containment (1 s) | 4 | 0 | RF2, RF4 |

**W2-50**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w2_50_code_under_test.py` | 1 / 0 | 1 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w2_50_extra_review.py` | 72 / 140 | 1 / 1 | 68 guard-full (137 s) | 3 | 0 | O, R1 |
| `test_w2_50_launcher.py` | 18 / 10 | 10 / 6 | 0 (0 s) | 8 | 0 | R1 |
| `test_w2_50_never_indexed.py` | 6 / 52 | 5 / 52 | 0 (0 s) | 1 | 0 | R1 |
| `test_w2_50_owner_answers.py` | 15 / 18 | 2 / 1 | 13 guard-full (17 s) | 0 | 0 | O, K |
| `test_w2_50_review_findings.py` | 54 / 63 | 4 / 3 | 43 guard-full (54 s) | 7 | 0 | O, R1 |
| `test_w2_50_short_round.py` | 53 / 98 | 1 / 2 | 52 guard-full (97 s) | 0 | 0 | O, K |
| the other 5 file(s): `w2_50_guard_own_folder`, `w2_50_guard_refusals`, `w2_50_last_review`, `w2_50_link_replaced`, `w2_50_one_reader` | 394 / 475 | 0 / 0 | 394 guard-full (475 s) | 0 | 0 | O |
| the other 1 file(s): `w2_50_secrets_scan_scale` | 23 / 198 | 0 / 0 | 23 gitleaks (198 s) | 0 | 0 | O |

**W2-58**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w2_58_auditor.py` | 15 / 8 | 4 / 3 | 0 (0 s) | 11 | 0 | R2 |
| `test_w2_58_code_under_test.py` | 1 / 0 | 1 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w2_58_engineer.py` | 47 / 19 | 8 / 5 | 0 (0 s) | 39 | 0 | R2 |
| `test_w2_58_evaluation_sets.py` | 62 / 27 | 10 / 3 | 0 (0 s) | 52 | 0 | R1 |
| `test_w2_58_fails_closed.py` | 6 / 4 | 6 / 4 | 0 (0 s) | 0 | 0 | K |
| `test_w2_58_launched_sessions.py` | 12 / 26 | 6 / 24 | 0 (0 s) | 6 | 0 | R1 |
| `test_w2_58_reads_open.py` | 196 / 69 | 6 / 2 | 36 guard-full (11 s) | 154 | 0 | R2, O |
| `test_w2_58_review.py` | 178 / 74 | 15 / 11 | 117 guard-full (42 s) | 46 | 0 | O, R1, R3 |
| `test_w2_58_still_refused.py` | 184 / 86 | 21 / 18 | 0 (0 s) | 163 | 0 | R3 |
| `test_w2_58_test_designer.py` | 53 / 20 | 12 / 5 | 0 (0 s) | 41 | 0 | R2 |
| `test_w2_58_tilde_and_test_runs.py` | 54 / 33 | 17 / 11 | 0 (0 s) | 37 | 0 | R2 |

**W2-59**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w2_59_baseline.py` | 4 / 9 | 4 / 9 | 0 (0 s) | 0 | 0 | R1 |
| `test_w2_59_hook_lines.py` | 18 / 8 | 15 / 8 | 3 lifted-hooks (0 s) | 0 | 0 | RF4 |
| `test_w2_59_hook_lines_worker_env.py` | 9 / 1 | 8 / 1 | 1 lifted-hooks (0 s) | 0 | 0 | RF4 |
| `test_w2_59_judge_checks.py` | 7 / 3 | 6 / 3 | 0 (0 s) | 1 | 0 | R1 |
| `test_w2_59_project_root.py` | 5 / 7 | 3 / 3 | 0 (0 s) | 2 | 0 | R1 |
| `test_w2_59_version.py` | 3 / 0 | 3 / 0 | 0 (0 s) | 0 | 0 | R1 |

**W2-65**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w2_65_hook_lines.py` | 9 / 4 | 9 / 4 | 0 (0 s) | 0 | 0 | K |
| `test_w2_65_subagentstop_reason.py` | 1 / 0 | 1 / 0 | 0 (0 s) | 0 | 0 | K |

**unit/guard**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_decide.py` | 316 / 2 | 68 / 1 | 233 guard-full (1 s) | 15 | 0 | O, K, R1, R2, R3 |
| `test_heldout.py` | 22 / 0 | 22 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_heldout_limit.py` | 20 / 1 | 20 / 1 | 0 (0 s) | 0 | 0 | K |
| `test_hook_deadline.py` | 4 / 20 | 4 / 20 | 0 (0 s) | 0 | 0 | K |
| `test_reads.py` | 179 / 8 | 37 / 3 | 40 guard-full (2 s) | 102 | 0 | R12, K, O, R3, R2 |
| `test_research_install.py` | 35 / 1 | 12 / 0 | 0 (0 s) | 23 | 0 | R3 |
| the other 5 file(s): `protected`, `protected_one_reader`, `runs`, `tools`, `w2_84_trees` | 507 / 10 | 0 / 0 | 507 guard-full (10 s) | 0 | 0 | O |
| the other 3 file(s): `records`, `w2_72_merge_rule`, `w2_72_merge_whole` | 20 / 1 | 0 / 0 | 20 containment (1 s) | 0 | 0 | O |

**unit/hooks**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_w2_106_template_hook_lines.py` | 44 / 1 | 25 / 0 | 0 (0 s) | 19 | 0 | R3 |

**unit/install**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_install.py` | 144 / 18 | 89 / 11 | 0 (0 s) | 54 | 1 | R3, D |

**unit/launch**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_batch4.py` | 41 / 0 | 41 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_command_modules.py` | 16 / 0 | 16 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_launcher.py` | 51 / 0 | 51 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_runs.py` | 6 / 0 | 6 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w1_28.py` | 6 / 0 | 6 / 0 | 0 (0 s) | 0 | 0 | K |
| `test_w1_32.py` | 18 / 1 | 18 / 1 | 0 (0 s) | 0 | 0 | K |

**unit/pause**

| file | before (cases / s) | full run, tier 1 (cases / s) | opt-in `lifted` (cases, s) | removed by parametrising | deleted | rule |
|---|---:|---:|---|---:|---:|---|
| `test_pause.py` | 23 / 1 | 19 / 1 | 0 (0 s) | 4 | 0 | R3 |
