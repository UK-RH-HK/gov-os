# ACT-SELECT-FIXES-1: the test map's couplings for the miss kinds seen, and W2-66's record-only case in the always-run set, run whole (DEC-1100 (1))

- **For:** the owner's operator (a test-map change; D-4's map edits were of this kind).
- **By:** the CTO, 2026-11-09. Built and rehearsed in a clone; nothing live is changed until the operator runs §3.
- **Pinned by W2-66c** (`DAEO-btcs`, filed 2026-11-09, tests first, six KPI lines): launched after this ACT's commit.
- **Under:** DEC-1100 (1); P-SELECT-FIXES-1 §1 (i) and §2 (ii) as written there; and **F1 (a)**, the CTO's choice of
  2026-11-09 implementing DEC-1100 (1)(ii) as decided (§5): the case must run whole in a selection, so it catches
  K3a, K4 and K13.

## 1. What changes (three files)
1. **`governance/project/test-map.yaml`** (`test-map.patch`). The map is read by `src/gov/close/select.py`, so no code
   changes.
   - **(ii)** one line at the end of `record_reading:`, with its comment:
     `tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only`.
   - **(i)** W1-28's coupling on `tests/acceptance/**.py` gains W1-50's `test_the_two_whole_tree_fixtures_are_found`,
     its `why` widened.
   - **(i)** three couplings after the last one, before `# Moved from the path map`:
     - settings and hook wiring (`.claude/settings.json`, `.rulesync/hooks.jsonc`, `.rulesync/permissions.jsonc`) →
       W1-33's guard-and-launcher file, W1-46's research-installs file, W2-54's sandboxed-worker file;
     - `template/governance/kernel/checks/**` → W2-54's `test_no_hard_block_check_is_weakened` alone;
     - `tests/acceptance/**` → W1-01's `test_the_integration_merges_of_this_repository_pass`.
   - **F1 (a)** four records in `record_only`, by exact path, after `win_toast.ps1`. They are the records the whole
     case finds unplaced today:
     - `packages/ACT-MSET-3/checker-settings.json`
     - `packages/ACT-MSET-3/writer-settings.json`
     - `packages/ACT-WSL-INTEROP-1/wsl-interop-binfmt.service`
     - `packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft`
   - Comments are kept (a hand edit, not a YAML dump). Every other key is unchanged (checked). The map now has 19
     couplings (was 16), 31 `record_reading` entries (was 30) and 17 `record_only` entries (was 13). Every new target
     exists today.
2. **`tests/optin-lifted-breadth.txt`** (`optin-lifted-breadth.patch`; **F1 (a)**). The one line
   `rep: tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only`
   is dropped.
   - Without that line, a selection (which names no node id) runs all seven rows of the case, not only `[.tickets/]`.
     Each row takes under 0.1 s.
   - This edits a list of D-4's cut by hand (its header says "regenerate rather than edit by hand", DEC-1061). Nothing
     else in the list changes, and no other test reads this line.
3. **`.gov-runtime/scratch/orchestrator/tools/record_checks.sh`** (`record_checks.patch`; **(ii)**, DEC-868 item 2).
   The same node id joins the pytest list that runs before the CTO's record commits. It is the CTO's tool and not
   tracked, so there is nothing to commit for it.

## 2. The files (scratch; checked by hash before they apply)
| File | sha256 (first 12) | What |
|---|---|---|
| `governance/project/test-map.yaml` (live) | `2001c392a3fb` → `42e22dd70a05` | as D-4 left it (`d3d757f3b`) → after the patch |
| `tests/optin-lifted-breadth.txt` (live) | `240bc62a826d` → `332f0a676f05` | as D-4's cut round 2 left it (`27cb63070`) → one line fewer |
| `tools/record_checks.sh` (live) | `81b758648843` → `d80b4eae5c56` | before → after the patch |
| `drafts/select-fixes/act/test-map.patch` | `513a6200045b` | (i), (ii) and F1 (a) in the map |
| `drafts/select-fixes/act/optin-lifted-breadth.patch` | `ac7342026ece` | F1 (a) in the breadth list |
| `drafts/select-fixes/act/record_checks.patch` | `309016802a6f` | (ii) in the record checks |
| `drafts/select-fixes/act/apply.sh` | `5c7097a41001` | check, apply, undo, with the three files' hashes |
| `drafts/select-fixes/act/replay_act.py` | `d9032ecacb95` | the replay with the lines read from the patched map |
| `drafts/select-fixes/act/rows_run.py` | `75c9d15587e5` | the second count: the rows a selection runs after the opt-in lists |
| `drafts/select-fixes/act/rehearse.sh`, `rehearsal.log` | `1b33913e1a1b`, `fc4c2467976c` | the rehearsal and its record |

## 3. The operator's steps (main tree, about a minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
A=.gov-runtime/scratch/orchestrator/drafts/select-fixes/act
bash $A/apply.sh check     # the three files hash as built, the three patches give the hashes after (exit 0)
bash $A/apply.sh apply     # backups with their sha256, the three files patched, the hashes after checked
git add governance/project/test-map.yaml tests/optin-lifted-breadth.txt
git diff --cached --name-status    # expect: M governance/project/test-map.yaml, M tests/optin-lifted-breadth.txt, nothing else
git commit -m "ACT-SELECT-FIXES-1: the test map's couplings for the miss kinds the P-SELECT-GRAPH trial saw (settings and hook wiring, the declared checks, the history rule, W1-50's fixture scan) and W2-66's record-only case in the always-run set, run whole (its four unplaced records placed, its breadth rep: line dropped); the same case in the CTO's record checks" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1100" --trailer "Role: owner"
```
`apply` prints the `git add` line at its end.

**Then the CTO:** runs `tests/acceptance/W2-66/`, `tests/unit/close/test_select.py` and
`tests/unit/optin/test_optin_lifted.py` on the main tree, scoped (143 passed in the rehearsal before, 149 after). It
then launches W2-66c's test designer.

**Undo:** `bash $A/apply.sh undo` restores the three files byte for byte (rehearsed), then a commit of the two
tracked ones.

**Order with ACT-SELECT-HOOK-1:** either order works. If the hook is applied first, this commit (an owner commit on
the test map) starts the first landing run.

## 4. The rehearsal (`drafts/select-fixes/act/rehearsal.log`)
One clean run, 2026-11-09 02:01:40–02:19:14, **0 failures**, in a `--no-hardlinks` clone at the main tree's head.
Tests: scoped pytest only, in a heavy slot. The first build's run (before F1 (a)) is kept as `rehearsal-before-f1a.log`.

| Step | Result |
|---|---|
| The selection's own tests before (`tests/acceptance/W2-66/`, `tests/unit/close/test_select.py`, `tests/unit/optin/test_optin_lifted.py`) | **143 passed** |
| `apply.sh check`, `apply` | the three files as built; the three patches give the hashes after; the patched map loads (`select.load_map`): 19 couplings, 31 `record_reading` entries |
| Planted changes, the CTO's `select_tests.py` (selection only) | S1: a settings change reaches all three suites (159 targets). S2: a kernel-check change selects W2-54's no-weakening case alone of its file. S3: an acceptance `.py` selects W1-01's and W1-50's cases. S5: a records-only change selects W2-66's case |
| What a selection's run collects (no opt-in) | W2-66's case: **all 7 rows**, `[governance/project/orchestration/]` included (1 row before the ACT) |
| **The replay, named** (`replay_act.py`: the 18 culprit trees, the lines read from the patched map) | **34 of 34 named with the patch, 22 without**. (i) alone gives 31, (ii) alone 25. No selection refused. Added a median of 8.5 cases and 16.7 s; the largest was 105 cases and 61.8 s (K2, K18a) |
| **The replay, run** (`rows_run.py`: named by the selection and collected after today's opt-in lists) | **with the patch: 30 of 34 run, 23 as gates and 7 report-only, 4 not run. Without: 18 of 34 (14 gates, 4 report-only).** K3a, K4 and K13 are gates. The 7 and the 4 are §5's |
| `record_checks.sh` before / after the patch | before: the record-reading line has 1 failure (W1-06, §5); after: **the patch adds no failure**, and W2-66's case runs whole and green |
| **A record commit** (`.md` under `governance/project/orchestration/`), then the patched `record_checks.sh` | **W2-66's case green**. The record-reading line's only failure is W1-06's, red before the ACT. The case by its file: 7 passed |
| S6, a planted `.foo` record | the patched checks exit non-zero and name the case and the planted file |
| The selection's own tests after (the patched map and list) | **149 passed** (the 143 plus W2-66's case's six other rows) |
| `apply.sh undo` | the three files byte for byte; the map and the list clean against HEAD; `record_checks.sh` equal to the live one |
| Live files | the test map, the breadth list, `record_checks.sh`, the hook and the settings hashed unchanged before and after |

`record_checks.sh` as a whole exits 1 in the clone before and after the ACT. One cause is W1-06's red. The other is
its `context-reproducibility` check, which needs a store the clone has not built. Neither comes from this ACT.

## 5. Decided, and what stays
**F1 (a), decided by the CTO on 2026-11-09.**
- The finding:
  - Since D-4's cut, the breadth list held `rep:` for W2-66's record-only case. A selection runs `pytest tests` with
    `--ignore` and `--deselect` and names no node id, so it collected only the case's `[.tickets/]` row.
  - The row K3a, K4 and K13 reded, `[governance/project/orchestration/]`, never ran in a selection.
  - That row was also red on `w2/integrate`, on the four records above.
- What applying (i) and (ii) as first written would have done:
  - the selection would name the case, but none of K3a, K4 or K13 would be caught;
  - `record_checks.sh` would turn red on every record commit.
- With F1 (a), the case runs whole, is green today, and is a gate for K3a, K4 and K13 (§4).

**What the opt-in lists still leave out (counted in §4; outside this ACT's lines):**
- **Report-only (7).** These run in `lifted_reached`'s report-only window, not as gates:
  - K2: W1-33's `test_the_orchestrator…` and `test_the_auditor…`, W1-46's research-install case (all 11 rows), and
    W1-05's `test_an_install_by_the_orchestrator…`;
  - K1: W2-71's suite;
  - K8: W1-26's two probe-record cases.
- **Not run (4).** Three are `# cap` breadth cases that the map itself selects:
  - K8: `test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records`;
  - K9: `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime`;
  - K18c: `test_w1_06_install_approvals.py::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool`.

  The fourth, K18a's `test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change`, is no longer in
  the tree.
- All of these were left out by D-4's cut (DEC-1061), not by the map. Bringing them back into the gates is a D-4
  question, not this ACT's. It would mean dropping three cap lines and un-lifting the seven, about 30 minutes with a
  new rehearsal.

**A red outside this ACT (the CTO's, at once, DEC-968):**
`tests/acceptance/W1-06/test_w1_06_approvals.py::test_every_approving_decision_is_accepted_by_the_owner`. DEC-892's
status now begins "DONE (owner, 2026-11-09, DEC-1098 (3))". It is red before and after this ACT, and it is the only
failure of `record_checks.sh`'s record-reading line after it.

[DEC-1100 (1), DEC-1098 (2)(b), DEC-889 item 2, DEC-891, DEC-1061, DEC-968]
