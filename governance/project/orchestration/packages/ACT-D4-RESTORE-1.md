# ACT-D4-RESTORE-1: D-4's 3 capped and 7 lifted cases back into the gates (DEC-1103 (2))

- **For:** the owner's operator. It edits three opt-in lists: test lists, the kind D-4's cut wrote.
- **By:** the CTO, 2026-11-09. Built and rehearsed in a clone. Nothing live is changed until the operator runs §3.
- **Under:** DEC-1103 (2), which amends DEC-1061's cut for these ten cases. The ten are the cases ACT-SELECT-FIXES-1's
  rehearsal left out of the gates (its §5): the 3 `# cap` breadth cases that were not run (K8, K9, K18c) and the 7 that
  ran report-only (K1, K2 ×4, K8 ×2).
- **Read first, §5:** three of the ten are **red at today's head by design**. They test guard features that DEC-1061
  (3a) switched off. As decided, they would turn every full run red, and every selection that reaches them, until those
  features return. This package gives the decided form (A, rehearsed) and the CTO's option B (rehearsed).

## 1. What changes (three files; no code, no test)
Each case comes out of its opt-in list as a commented line:
`# DEC-1103 (2): back in the gates (<why>); was: <the line>`.
- Nothing is deleted, so the list keeps its history (DEC-953).
- `tests/conftest.py` and the CTO's `select_tests.py` both skip whole-line comments.
- The lists' headers say "regenerate rather than edit by hand". This is a hand edit under DEC-1103 (2), as
  ACT-SELECT-FIXES-1's was.

| Case | Trial | Test id | List : line (as at `8b7bfe867`) | Edit |
|---|---|---|---|---|
| 1 | K18c | `tests/acceptance/W1-06/test_w1_06_install_approvals.py::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` | `optin-lifted-breadth.txt:16` (`# cap`) | line commented out. The file's `rep:` line 39 does not touch it: the function has no parameters |
| 2 | K8 | `tests/acceptance/W1-08/test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records` | `optin-lifted-breadth.txt:66` (`# cap`) | line commented out |
| 3 | K9 | `tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime` | `optin-lifted-breadth.txt:604` (`# cap`) | line commented out |
| 4 | K1 | `tests/acceptance/W2-71/test_w2_71_keywords_in_parts.py::test_premise_the_list_holds_this_suites_own_files` | `optin-lifted.txt:15`: the whole suite `tests/acceptance/W2-71/` (the real gitleaks, DEC-1045) | the suite's line commented out and replaced by its other parts, each still lifted: its 8 other test files and the sister case `::test_no_file_the_branch_writes_holds_a_keyword_of_row_w2_l423s_rule_whole`. The case is git-only and runs no gitleaks |
| 5 | K2 | `tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py::test_the_orchestrator_may_write_anywhere_else_in_the_repository` | `optin-lifted-guard.txt:81` | line commented out |
| 6 | K2 | `tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py::test_the_auditor_writes_only_the_report_path_of_its_own_ticket` | `optin-lifted-guard.txt:82` | line commented out (A only) |
| 7 | K2 | `tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through` | `optin-lifted-guard.txt:124` | line commented out (A only) |
| 8 | K2 | `tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner` | `optin-lifted-guard.txt:275` | line commented out (A only) |
| 9 | K8 | `tests/acceptance/W1-26/test_w1_26_probe_records.py::test_this_repository_s_probe_records_are_well_formed` | `optin-lifted.txt:38`: the whole file (a lifted family) | the file's line commented out and replaced by its 11 other functions, each still lifted |
| 10 | K8 | `tests/acceptance/W1-26/test_w1_26_probe_records.py::test_no_finding_of_the_check_on_this_repository_names_a_probe_record` | the same line | the same edit |

- K18a's `tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change` is no
  longer in the tree, so there is nothing to restore for it.
- `optin-lifted-guard-breadth.txt` holds none of the ten and is unchanged.
- The lists are built by `drafts/d4-restore/build/make_lists.py` from the tree's own lists. The patches are its
  output.

## 2. The files (scratch; checked by hash before they apply)
| File | sha256 (first 12) | What |
|---|---|---|
| `tests/optin-lifted-breadth.txt` (live) | `332f0a676f05` → `3528cd1ffbb0` | as ACT-SELECT-FIXES-1 left it (`8038e0ee6`) → three cap lines commented out |
| `tests/optin-lifted-guard.txt` (live) | `868b6e1c8464` → A `dfdef9b08541`, B `69a969e803bb` | as `15952bbfa` left it → four lines (A) or one (B) commented out |
| `tests/optin-lifted.txt` (live) | `bc67a6f3fe5f` → `29a2cc1033b9` | as `f551589dd` left it → W2-71's and W1-26's lines split |
| `drafts/d4-restore/optin-lifted-breadth.patch` | `19a5e7de3e27` | |
| `drafts/d4-restore/optin-lifted-guard.patch` / `.B.patch` | `1a7f3d92f6c6` / `a3ea473f6e51` | A / B |
| `drafts/d4-restore/optin-lifted.patch` | `a54a095295e8` | |
| `drafts/d4-restore/apply.sh` | `81e33d1c8495` | check, apply and undo (`[A|B]`, default A), with the three files' hashes |
| `drafts/d4-restore/rehearse.sh`, `rehearsal.log` | `df29f34130d4`, `b54fd50b4bff` | the rehearsal and its record (run 1, before two counting fixes in the script: `rehearsal-run1.log`) |
| `drafts/d4-restore/ten.txt`, `ten-k.txt`, `build/make_lists.py` | | the ten ids; the lists' builder |

## 3. The operator's steps (main tree, about a minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
A=.gov-runtime/scratch/orchestrator/drafts/d4-restore
bash $A/apply.sh check     # the three lists hash as built, the three patches give the hashes after (exit 0)
bash $A/apply.sh apply     # backups with their sha256 in $A/backup/, the three lists patched, the hashes after checked
git add tests/optin-lifted-breadth.txt tests/optin-lifted-guard.txt tests/optin-lifted.txt
git diff --cached --name-status    # expect: M on the three lists, nothing else
git commit -m "ACT-D4-RESTORE-1: D-4's 3 capped and 7 lifted cases back into the gates (K8, K9, K18c's cap lines; K1's W2-71 premise case, K2's four guard cases, K8's two W1-26 probe-record cases un-lifted; W2-71's suite and W1-26's file split so their other parts stay lifted), each line commented with DEC-1103 (2)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1103" --trailer "Role: owner"
```
- **Variant B**, if the owner chooses it (§5): `bash $A/apply.sh check B`, then `apply B`, the same `git add`, and the
  commit message with "K2's four guard cases" replaced by "K2's W1-33 orchestrator case (the three red by the guard's
  switched-off features stay lifted)".
- **Undo:** `bash $A/apply.sh undo` (or `undo B`). It restores the three lists byte for byte (rehearsed), then the
  operator commits them.
- **The hook:** the scoped selection's hook line has been applied since 12:14. This owner commit on three test lists
  starts a landing run. With A it is red on §4's three cases if the run reaches them.

**Then the CTO:** puts §4's reds on D-10's red-fix list by name, and re-runs `tests/unit/optin/test_optin_lifted.py`
on the main tree.

## 4. The rehearsal (`drafts/d4-restore/rehearsal.log`)
One run, 2026-11-09 12:51:04–12:54:59, **0 failures**, in a `--no-hardlinks` clone at the main tree's head `8b7bfe867`. Tests: scoped pytest only, in a
heavy slot. The full run's count is by collection only.

| Step | Result |
|---|---|
| Live files before and after | the three lists, `optin-lifted-guard-breadth.txt`, `tests/conftest.py`, the test map (`42e22dd70a05`, ACT-SELECT-FIXES-1's), the hook and the settings: **unchanged** |
| `test_optin_lifted.py` before | **16 passed** |
| **The replay, run** before (`rows_run.py`, ACT-SELECT-FIXES-1's; its replay of the 18 culprit trees on today's map) | **gate 23, report-only 7, not run 4** (30 of 34 run), as ACT-SELECT-FIXES-1's rehearsal found |
| `apply.sh check`, `apply` | the three lists as built; the patches give the hashes after |
| Each restored case, collected by its file with no opt-in and no node id (as the full run and a selection collect) | **all ten collected** |
| **The replay, run** after (A) | **gate 33, report-only 0, not run 1** (K18a, not in today's tree). **33 of 34, every traced red that still exists is a gate** |
| `test_optin_lifted.py` after | **16 passed** (its check that every entry names a test that exists covers the 20 new split lines) |
| The full run's count (`pytest tests --collect-only`, no opt-in) | **7,620 → 7,631 (+11)**: the ten cases' 11 rows (W1-05's case has 2), nothing else added, nothing removed. With both suites opted in: 21,990 → 21,990 (nothing lost) |
| **Variant B** | the replay: **gate 30, report-only 3** (the three red-by-design K2 cases), **not run 1** (K18a); the full run 7,620 → 7,627 (+7); `test_optin_lifted.py` 16 passed; undo B byte for byte |
| `apply.sh undo` (A, then B) | the three lists byte for byte; clean against HEAD |

**The ten at today's head** (by node id, in the clone):

| Result | Case |
|---|---|
| green | K8 W1-08 `test_the_probe_schema_accepts_this_repository_s_probe_records` |
| green | K9 W1-27 `test_the_mode_writes_only_under_gov_runtime` |
| green | K18c W1-06 `test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` |
| green | K1 W2-71 `test_premise_the_list_holds_this_suites_own_files` |
| green | K2 W1-33 `test_the_orchestrator_may_write_anywhere_else_in_the_repository` |
| green | K8 W1-26 `test_this_repository_s_probe_records_are_well_formed` |
| green | K8 W1-26 `test_no_finding_of_the_check_on_this_repository_names_a_probe_record` |
| **RED** | K2 W1-33 `test_the_auditor_writes_only_the_report_path_of_its_own_ticket`. The five-rule hook lets the auditor's write to `docs/audit/report.md` on an engineer's ticket through: write scope is G-4, switched off |
| **RED** (2 rows, ERROR at setup) | K2 W1-05 `test_an_install_by_the_orchestrator_asks_the_owner` `[pip install requests]`, `[npm install -g ccusage]`: "the switch-over has not happened: .claude/settings.json does not register … a PostToolUse hook for Bash". Post-command containment is G-5, switched off |
| **RED** | K2 W1-46 `test_a_research_install_inside_the_experiment_folder_is_let_through[npm-install]`: "installs are refused here: raise the install as a P1 escalation … (DEC-953 item 2)" |

**For D-10's red-fix list (named):** the three red cases above, 4 rows in all. Their cause is one and the same.
- The guard's full features (G-4, G-5, and the research-install rule) were switched off by ACT-1-GUARD. That switch
  is the trial's own K2 culprit, `6c36c7b5c`.
- The cases were then lifted for that reason (DEC-1061 (3a)).
- They are not regressions. They turn green when those features return, after the resume.

## 5. The contradiction, with three costed options (DEC-105)
DEC-1103 (2) puts the ten into the gates "where the trial showed misses". Seven of them are green today and catch the
reds the trial traced. The other three have been red since `6c36c7b5c` switched their features off. As gates, they
would report that switch over and over, and catch nothing new.
- **A, apply as decided** (rehearsed; §3's steps).
  - Gates: 33 of 34.
  - Cost: the full run is red on 3 cases (4 rows) until G-4 and G-5 return.
  - Every selection that reaches W1-33's, W1-46's or W1-05's files fails: since ACT-SELECT-FIXES-1, that is every
    change to `.claude/settings.json`, `.rulesync/hooks.jsonc` or `.rulesync/permissions.jsonc`.
  - So no settings or hook change lands green until the reds are fixed in D-10. Fixing them means switching the
    features back on, or rewriting the cases to the five-rule hook.
- **B, apply the seven green now; keep the three lifted until their features return** (rehearsed; `apply B`).
  - Gates: 30 of 34; the three run report-only, as today.
  - Cost: three of the trial's reds stay report-only, though each is already red, so no new red is missed.
  - The list's own rule then applies to them: the switch that turns a feature back on takes its lines out (DEC-953).
  - This narrows DEC-1103 (2), so it needs the owner's word.
- **C, defer the three to D-10.**
  - Apply B now. D-10 then decides per case: fix it for the five-rule hook and gate it, or keep it lifted.
  - Cost: one more D-10 item; the same gates as B until then.

**The CTO recommends B (or C, the same today).** Seven gates are added at no red cost. The three red-by-design cases
stay where DEC-1061 (3a) put them until their features return. If the owner holds to A, it is ready as it stands.

[DEC-1103 (2), DEC-1061 (1)-(3a), DEC-953, DEC-1100 (1), DEC-105, DEC-968]
