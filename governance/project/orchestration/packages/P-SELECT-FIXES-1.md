# P-SELECT-FIXES-1: the three cheaper fixes from P-SELECT-GRAPH, as proposals; the code route stays (DEC-1098 (2)(b))

By a research agent for the Wave 2 CTO, 2026-11-09. This is a proposal only, made on the CPU. Nothing is applied,
and no tracked file has changed but this one, which is uncommitted (the CTO commits it). Each proposal needs its own
owner decision (DEC-1098 (2)(b)). The test selector on the code graph is not built (DEC-1098 (2)(a); DEC-1062
closed).

## Headline

The trial's selection missed 12 red cases (P-SELECT-GRAPH-RESULT §4). All three proposals were replayed on the
trial's 18 culprit trees, each tree with its own test map plus the proposed lines, using the trial's frozen selection
(`drafts/select-fixes/replay_fixes.py`):

| Selection | Red cases caught (of 34) | Of the map's 12 misses |
|---|---|---|
| The map today (the trial's baseline, reproduced) | 22 | 0 |
| + (i) the couplings | 31 | 9: K2 ×6, K6, K10 (W1-50), K16 |
| + (ii) W2-66's case in `record_reading` | 25 | 3: K3a, K4, K13 |
| + (i) and (ii) | **34** | **12** |

The cost on the 18 replays:
- added per selection: a median of **8.5 cases and 16.7 s** of test time; the largest was 105 cases and 62 s (K2 and
  K18a, the settings changes);
- under 1 % of the map's own seconds on every case;
- no selection refused.

The trial's catch is "the selection, run on the culprit change, holds the red case". Proposal (iii) makes sure a
selection runs on the change at all, for the commits that land outside a ticket. In the window those commits were
K2, K18a and K18c, and none of them ran a selection at the time.

## 0. The 12 misses (from P-SELECT-GRAPH-RESULT §4 and `~/gov-os-runs/P-SELECT-GRAPH/scripts/cases.json`)

| # | Case | Red case | What caused it |
|---|---|---|---|
| 1-4 | K2 (`6c36c7b5c`, ACT-1-GUARD) | W1-33 `test_w1_33_guard_and_launcher.py`: `test_only_the_test_designer…`, `test_the_orchestrator_may_write…`, `test_the_auditor_writes_only…`, `test_an_install_asks…` | `.claude/settings.json`, `.rulesync/hooks.jsonc` |
| 5 | K2 | W2-54 `test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker…` | the same |
| 6 | K2 | W1-46 `test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through` | the same |
| 7 | K3a (`bd07b6503`, a `.patch` record) | W2-66 `test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only` | a new kind of file under `governance/project/orchestration/` |
| 8 | K4 (`42104b116`, `win_toast.ps1`) | the same W2-66 case | the same |
| 9 | K13 (`49158e131`, a `.diff` record) | the same W2-66 case | the same |
| 10 | K6 (`9b03ac0b5`, W2-67's merge) | W1-01 `test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass` | a merge's own resolution in `tests/acceptance/` (DEC-253's rule over history) |
| 11 | K10 (`789513df6`, W2-108's merge) | W1-50 `test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found` | a new whole-tree fixture in an acceptance file |
| 12 | K16 (`c72ededc5`, emg/noscan) | W2-54 `test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened` | `template/governance/kernel/checks/secrets-indexing.yaml` |

## 1. Proposal (i): test-map couplings for the miss kinds seen

**What changes.** These go in `governance/project/test-map.yaml`. The map is read by the product's selection,
`src/gov/close/select.py:404-408`, so no code changes. Three new `couplings:` entries go after the last one (insert
after line 167, before `# Moved from the path map` at line 169). One target is added to the existing W1-28 entry
(lines 162-164):

```yaml
  - paths: ["tests/acceptance/**.py"]                       # existing (line 162); suites gain the W1-50 case
    suites: ["tests/acceptance/W1-28/test_w1_28_fixture_copies.py",
             "tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found"]
    why: "file scan: W1-28's held-out copy check and W1-50's whole-tree fixture count read every Python source under tests/acceptance/ (I1 §4.1, DEC-385, DEC-912 item 3; P-SELECT-FIXES-1 (i), K10)"
  - paths: [".claude/settings.json", ".rulesync/hooks.jsonc", ".rulesync/permissions.jsonc"]
    suites: ["tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py",
             "tests/acceptance/W1-46/test_w1_46_research_installs.py",
             "tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py"]
    why: "settings and hook wiring: these suites copy or read the live settings and the hook lines (P-SELECT-FIXES-1 (i), K2)"
  - paths: ["template/governance/kernel/checks/**"]
    suites: ["tests/acceptance/W2-54/test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened"]
    why: "text read: W2-54's no-weakening case compares each declared check with its base (P-SELECT-FIXES-1 (i), K16)"
  - paths: ["tests/acceptance/**"]
    suites: ["tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass"]
    why: "history rule: W1-01 judges every merge that touches tests/acceptance/ (DEC-253, DEC-912; P-SELECT-FIXES-1 (i), K6)"
```

Two targets name one case, not the whole file. W2-54's time-limit file has 10 cases worth 632 s, and the red case
alone takes 0.1 s. W1-01's merge case takes 33 s. Nothing changes in `src/` or in the schema: a coupling's suites
already take node ids, under the schema's `target` pattern `^tests/`.

**KPI lines.** These go in a new ACT under W2-00, `ACT-SELECT-FIXES-1` (the map edit, made as D-4's map edits were:
`d3d757f3b`, `c0a3520ac`, `530879a4a`). The pinning cases go in a new test-revision ticket, W2-66c (§4).
- 'S1 Settings and hook wiring are coupled: a change of `.claude/settings.json`, `.rulesync/hooks.jsonc` or
  `.rulesync/permissions.jsonc` selects W1-33''s guard-and-launcher file, W1-46''s research-installs file and W2-54''s
  sandboxed-worker file. Verify: `replay_fixes.py` on K2 (`6c36c7b5c`) selects all 10 of its red cases; on today''s
  tree the cases in the `lifted` list are named in `lifted_reached`; W2-66''s `COUPLINGS` fixture holds
  (`.claude/settings.json`, the three files). [DEC-1098 (2)(b), DEC-896 item 2, DEC-889 item 2]'
- 'S2 The declared checks are coupled to W2-54''s no-weakening case: a change under
  `template/governance/kernel/checks/` selects `test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened` and
  no other case of that file. Verify: `replay_fixes.py` on K16 (`c72ededc5`) catches its red, and the case''s
  `--deselect` leaves the file''s other nine cases out. [DEC-1098 (2)(b), DEC-896 item 2, DEC-1045]'
- 'S3 The history rule and the fixture scans are coupled: a change under `tests/acceptance/` selects W1-01''s
  integration-merge case, and a change of an acceptance `.py` also selects W1-50''s whole-tree fixture case. Verify:
  `replay_fixes.py` on K6 (`9b03ac0b5`) and K10 (`789513df6`) catches both reds. [DEC-1098 (2)(b), DEC-253,
  DEC-912 item 3]'
- 'S4 Bounded cost: over the trial''s 18 culprit trees the four lines and (ii) add a median of at most 10 cases and
  30 s to a selection, and no selection is refused. Verify: `replay_fixes.py`''s totals (measured: median 8.5 cases,
  16.7 s; largest 105 cases, 62 s). [DEC-1098 (2)(b), DEC-1052]'

**Which misses it would have caught:** 9 of the 12: K2 ×6, K6, K10 (the W1-50 case) and K16 (all replayed).

**Cost.** About an hour of the CTO's time for the map edit, the replay and a scoped run of W2-66's suite. A test
designer then pins the lines, about an hour (W2-66c). At run time:
- most ticket merges touch `tests/acceptance/`, so they add W1-01's case (+33 s, one worker);
- a settings change adds about 99 cases (62 s);
- a kernel-check change adds 0.1 s.

**Risk.**
- *Brittle node ids.* A coupling's target is checked only when the coupling fires (`select.py:376-379`). If W1-01's
  or W2-54's case is renamed, the selections that reach it refuse with `UNRESOLVED_TARGET` (`select_tests.py` exit 2)
  until the map is fixed. That is loud, and it does not fail open. W2-66's `test_every_record_reading_target_exists`
  covers only `record_reading`, so W2-66c adds the same check for couplings.
- *Lifted cases.* Since D-4 (DEC-1061 (3a)), three of K2's W1-33 cases are in `tests/optin-lifted-guard.txt`:
  `test_the_orchestrator…`, `test_the_auditor…` and `test_an_install…[orchestrator]`. Today they would be named in
  `lifted_reached` and run report-only, not as gates. The other four of K2's six misses run as gates.
- *W2-54's sandboxed-worker case* carries `local_only`. It runs here, not in a hosted CI.

## 2. Proposal (ii): W2-66's record-only case in the always-run set

**What changes.**
1. `governance/project/test-map.yaml`: one line at the end of `record_reading:` (after line 101):
   `  - "tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only"`,
   with the comment `# P-SELECT-FIXES-1 (ii): reads every tracked record of DEC-891's places (K3a, K4, K13)`. This is
   the same ACT as (i).
2. `.gov-runtime/scratch/orchestrator/tools/record_checks.sh:22-26`: the same node id joins the pytest list that runs
   before the CTO's record commits (DEC-868 item 2). There a record of a new kind is caught before it lands, not at the
   next close.

The case is a record reader by KPI 5's own rule: it scans every tracked file under DEC-891's record places
(DEC-889 item 2). It belongs in the set on that rule alone.

**KPI lines** (in the ACT, and in W2-66c for the fixture):
- 'S5 W2-66''s record-only case is always run: `record_reading` holds
  `test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only`, so every scoped
  selection runs it, a records-only change included. Verify: `replay_fixes.py` on K3a, K4 and K13 catches each red;
  W2-66''s `RECORD_READERS` holds the case. [DEC-1098 (2)(b), DEC-889 item 2, DEC-891, DEC-1050 (T-4)]'
- 'S6 The CTO''s record checks run it before each record commit. Verify: `record_checks.sh` on a clone with a planted
  untracked-kind record committed under `governance/project/orchestration/` (a new `.foo` file) exits non-zero and
  names the case; on today''s tree it exits 0. [DEC-868 item 2, DEC-1098 (2)(b)]'

**Which misses it would have caught:** 3 of the 12: K3a, K4 and K13 (replayed).

**Cost.** Minutes for the edit. 7 parametrized cases, under 0.1 s, plus collecting one file.

**Risk.**
- `record_reading` targets are checked on every selection (`select.py:377`). If the case is renamed, every selection
  refuses until the map is fixed. That is loud, and W2-66's `test_every_record_reading_target_exists` already pins it.
- After a new kind of record lands, every selection reds on the case until `record_only` is widened. That is the
  intended signal (DEC-968: fix at once). The close's attribution names it as not caused by the change.

## 3. Proposal (iii): a scoped selection on every commit outside a ticket that touches settings, the registry or the test map

**What changes.** The CTO's tools lane comes first; the product line is optional (§5 decision 4).
1. A new tool, `.gov-runtime/scratch/orchestrator/tools/outside_ticket_select.sh <old head> <new head>`, modelled on
   `act_clone_run.sh`:
   - It lists the first-parent commits of `old..new` whose `Task:` is not a work ticket (`DAEO-sdxk`, W2-00's, or
     `decision-record`; ACTs included).
   - If they touch `.claude/settings*.json`, `.rulesync/**`, `governance/project/tool-registry.yaml` or
     `governance/project/test-map.yaml`, it takes a clone at `new` and runs
     `select_tests.py <clone> W2-00 DAEO-sdxk --base <old>`.
   - It then runs the selection's targets in the heavy slot (`heavy_slot.sh`, no full run), and writes the verdict to
     the CTO's inbox and to `log/outside-ticket/<stamp>/`.
2. Its trigger is one line in `.git/hooks/reference-transaction`, the hook W2-116 installed at re-pin window 4. The
   hook already starts the store refresh after every landing on `w2/integrate`. A second `setsid -f` line starts the
   tool with the old and new heads. This changes a git hook, which is configuration: it needs the owner's approval
   (§5 decision 3). The alternative is `record_checks.sh`, before the CTO's own commits. That prevents rather than
   detects, but it misses commits made with `Role: owner`, as K2, K18a and K18c were.

**KPI lines** (in the tools lane under W2-00, filed with the ACT):
- 'S7 A scoped selection follows every landing outside a ticket that touches settings, the registry or the test map:
  the first-parent commits of the landing with no work ticket (`Task:` W2-00''s or `decision-record`), touching
  `.claude/settings*.json`, `.rulesync/**`, `governance/project/tool-registry.yaml` or
  `governance/project/test-map.yaml`, start one `select_tests.py --base <old head>` in a clone at the new head, run in
  the heavy slot, with its verdict sent to the CTO''s inbox; a red that the landing caused is fixed at once or
  reverted. Verify: on a planted repository, a settings commit outside a ticket starts the run, and a records-only
  commit and a ticket''s merge do not; on the trial''s trees the selection catches K2''s 10 reds with (i), and K18a''s 3
  and K18c''s 1 without it. [DEC-1098 (2)(b), DEC-968, DEC-953 item 4]'
- 'S8 Never a full run, never a held landing: the run follows the landing and never blocks it, and never runs the full
  suite; a refused selection (exit 2) is reported as refused, never as green; the heavy slot orders it behind a
  running close. Verify: the tool''s tests (planted refusals, a slot held by a close). [DEC-968, DEC-953 item 4,
  DEC-1011]'
- (Product, optional) 'S9 `gov close --select` takes `--base <commit>` without a ticket, so a commit outside any
  ticket gets the same scoped set. Verify: on a planted repository, the set equals `select_tests.py`''s for the same
  span. [DEC-953 item 4, DEC-1098 (2)(b)]'. This would be a KPI line added to W2-115, which already owns the selection
  command (its KPI 3).

**Which misses it would have caught.** None of the 12 on its own: its job is to *run* the selection that (i) and (ii)
fix.
- With (i), it would have caught K2's 6 at the landing. Today, 4 run as gates and 2 run report-only (lifted).
- It also brings forward 8 of the 22 reds the map did catch, which surfaced only at later closes: K2 ×4, K18a ×3 and
  K18c.
- Its trigger as decided does not cover K16 (an emergency merge of code and a kernel check) or K3a, K4 and K13
  (records and tools only). (ii) catches those at the next selection of any kind, and `record_checks.sh` before a CTO
  commit.

**Cost.**
- In the window (10-20 to 11-08), 17 first-parent commits outside a ticket touched the trigger paths, about 0.85 a
  day out of 635 commits outside a ticket.
- Each run is one scoped selection: 3,342 to 5,394 cases at the trial's counts, `tests/unit` included, or 1 to 3
  hours of test time across the parallel workers (about 10 to 20 minutes of wall time).
- Building it: about half a day for the tool and its planted tests, then one hook line.

**Risk.**
- A run competes for the heavy slot with closes and the queue.
- A hook line that fails must never block a landing. It uses the existing pattern: `setsid -f`, `exit 0` always.
- The red has no ticket of its own. Its owner is the CTO, at once (DEC-968).

## 4. Where each belongs

| Proposal | Home | Why |
|---|---|---|
| (i), (ii): the map lines | **New `ACT-SELECT-FIXES-1` under W2-00 (DAEO-sdxk)**, applied as D-4's map edits were | This repository's test map is named by no open ticket. W2-66 (DAEO-c1uz) and W2-68 are closed. W2-115 holds only the *template* map. |
| (i), (ii): pinning the lines in W2-66's live-map suite | **New W2-66c**, a test-revision ticket (LITE; independent test designer; `allowed_paths`: `tests/acceptance/W2-66/test_w2_66_live_test_map.py`, `tests/acceptance/W2-66/README.md`) | W2-66b (DAEO-zuiy, in progress) holds the same file, but its KPI forbids any other change ("every other case of the file and its verdicts unchanged"). Folding it in would need W2-66b's KPI changed. Option: W2-66c after W2-66b, the same designer. |
| (ii): `record_checks.sh` | The CTO's tools lane (W2-00) | DEC-868 item 2's own tool. |
| (iii): the tool and the hook line | The CTO's tools lane (W2-00); the hook line on the owner's approval | It is the CTO's integration practice, beside `close_build.py` and `land.py`. |
| (iii): the product line S9 | **W2-115** (DAEO-emq1, open), as an added KPI line, or deferred to Wave 3 | W2-115 owns `gov close --select` and `src/gov/close/select.py`. |

## 5. For the owner to decide

1. Whether to accept (i) and (ii) as `ACT-SELECT-FIXES-1`, with W2-66c to pin them. Recommended: yes. They catch the
   12 of 12 in replay, for a median of +8.5 cases and +17 s.
2. (iii)'s trigger:
   - (a) as decided: settings, the registry, the test map (about 0.85 runs a day);
   - (b) every commit outside a ticket that touches code, the kernel, tests, settings, the registry or the map: 65
     commits in the window, about 3.3 runs a day. It would also have run on K16's emergency merge, so K16 would have
     been caught at the landing.
   Recommended: (a) now. Widen it if an emergency merge reds again.
3. (iii)'s mechanism:
   - (a) one line in `.git/hooks/reference-transaction` (configuration: your approval). It sees every landing,
     whoever made it.
   - (b) `record_checks.sh` before the CTO's own commits. No configuration change, but it misses commits made with
     `Role: owner`, as K2, K18a and K18c were.
   Recommended: (a).
4. Whether S9 is added to W2-115 now, or deferred to Wave 3.

## 6. The code route stays (DEC-1098 (2)(b))

**The design, unchanged.** No file of the code route changed with P-SELECT-GRAPH. The trial built its graphs in
`~/gov-os-runs/P-SELECT-GRAPH/cbm/`, outside the product. `src/gov/retrieval/code_route.py` and `measure.py` on
`w2/integrate` are byte-identical to the measured pin's (`pin-bcea09060ebc`; `diff -q`: no difference).
- **What it does** (W2-92; DEC-957, DEC-859, CAP-12; `code_route.py`):
  - It takes the symbol words of a plain question: words shaped as code, plus plain words that a non-test code file
    defines, but only in a question with a code cue (DEC-1006 P-3).
  - It asks the code index for their **definitions** (`search_graph`), then each function's **callers and callees**
    (`query_graph` over CALLS edges, into and out of the one qualified name). It reads in pages of 50 rows, and leaves
    test files out.
  - It maps the returned spans onto the store's lexical chunks. Those chunks join the fusion as the route `code`.
  - A question that names no symbol does not ask the index, and gets today's bundle.
  - A missing or unreadable index gives `facets.code.available: false` with its reason, and the other routes answer
    (DEC-957, DEC-860).
  - One tool session serves a process (P-4). The route only reads; it builds nothing.
- **The index:**
  - `gov.codeintel` with `codebase-memory-mcp` 0.11.0, project `code`, under `.gov-runtime/codeintel/`;
  - built by `gov rebuild` (also seeded, and by the watch), read at query time;
  - its consumers are retrieval (the code route and the closure's facet), the store loader, rebuild and adoption.
    Test selection is not one of them, and stays so (DEC-1098 (2)(a)).
- **Routing, in the measured configuration** (`governance/project/retrieval.yaml` at `c00d525fd420` and today):
  `code_first: 2` puts the code route's first two hits, ordered by stored-vector cosine, ahead of the reranked page
  (W2-32 S8, DEC-1067 (a)). The bundle names them in `routing.code`. This is part of the configuration that
  DEC-1098 (1) made the memory standard.
- **How an item records its route:** each evidence item carries `routes`, the list of every route that returned its
  chunk (`fusion.rrf`, carried by `retrieve.item`). A pooled or code-first reorder leaves it unchanged, and an item
  widened to its section keeps its child's routes. "By the code route" below means `code` is in `routes`; "alone"
  means it is the only route.
- **What was known before** (W2-92's record, `docs/research/W2-92-memory-measure.md` §6, visible 20 only):
  - the code route took words in 4 of 20 questions;
  - the two callers' questions gained both of their gold pieces through it;
  - run 1, before the cue gate, showed the route's items crowding gold out of three non-code questions. The cue gate
    removed that.
  - The 138 and the 80 were not counted by route until now.

**The figures (the CTO fills this table from `code_route_counts.py`'s output; counts only).** Command:
`nice -n 10 ~/.local/share/gov-os/pin-bcea09060ebc/bin/python -I
.gov-runtime/scratch/orchestrator/drafts/code-route/code_route_counts.py --sets-root ~/gov-os-eval` (README beside
it; planted test PASS). Take each row from the block "-- the 138, …" or "-- the 80, …", the version without
`nonexistent-id` where the set scores it apart.

| Set | Questions | Code route asked | Bundle holds a code item | First gold by code (alone) | First gold by code in top 5 | Any gold by code (alone) | Code share of bundle items (alone) |
|---|---|---|---|---|---|---|---|
| the 138, all | 140 | 14 | 13 | 9 (1) | 9 | 9 (4) | 57 of 2535 (21) |
| the 138, without `nonexistent-id` | 138 | 14 | 13 | 9 (1) | 9 | 9 (4) | 57 of 2535 (21) |
| the 80, all | 80 | 11 | 7 | 3 (0) | 3 | 3 (1) | 23 of 1442 (11) |
| the 80, without `nonexistent-id` | 79 | 11 | 7 | 3 (0) | 3 | 3 (1) | 23 of 1423 (11) |

| Category `callers` (from the per-category lines: questions; code item in the bundle; first gold by code; alone; in the first five; any gold by code) | Questions | Code item in bundle | First gold by code | Alone | In top 5 | Any gold by code |
|---|---|---|---|---|---|---|
| the 138 | 12 | 10 | 9 | 1 | 9 | 9 |
| the 80 | 8 | 4 | 3 | 0 | 3 | 3 |

The script's header lines must say "the kept outputs re-read whole", "first gold rank as the measure scores it: N of
N" and "(the same)" against the measure's recorded total. If one does not, the figures are not the measure's and are
not entered.

**Filled by the CTO, 2026-11-09** (clone `c00d525fd420`; E0's kept outputs for the 138, the fresh 80's attempt-1).
The spent 60's and the 80's headers read "(the same)". The visible and hidden 80's header reads hit@5 re-scored 67
against the measure's recorded 66: Q07 and Q14 were re-worded on 11-09 (`55d1c029`) after E0 kept its outputs, so one
question is scored against its new label. Both are `ticket` questions with no code item, so the code route's counts
are unaffected; they are entered with this note.
- **The code route supplies the gold for the callers questions:** the first gold came by it for 9 of 12 on the 138 and
  3 of 8 on the 80, almost always beside another route (alone: 1 and 0). Outside `callers` it supplied no first gold.
- **It is cheap:** about 2 % of bundle items (1.6 % on the 80), under 1 % by the code route alone.
- **It stays unchanged** (DEC-1098 (2)(b)).

**Reading the figures.**
- They confirm the route; they decide nothing. The owner kept the code route unchanged (DEC-1098 (2)(b)).
- "First gold by code alone" counts the questions where no other route returned the gold that came first.
- Any category other than `callers` with many questions that hold code items but few with gold by code is the
  crowding that W2-92's run 1 showed. It is a point to look at, not a change.

## 7. Evidence, rerun, residuals

- **Replay of (i) and (ii):** `python3 .gov-runtime/scratch/orchestrator/drafts/select-fixes/replay_fixes.py --work
  <empty folder> --out <json>`. It uses a `git clone --shared` of the repository; the main tree is not checked out.
  The trial's frozen `tool/` (`select_tests.py`, `src/` at integrate `0732a0a7`) runs on each culprit tree. The
  proposed lines are committed on top of that tree's own map, and the map path is left out of the change. The
  baseline reproduces the trial: 22 of 34. About 3 minutes on the CPU at `nice` 15.
- **Commit counts:** `git log --first-parent w2/integrate --since=2026-10-20 --until=2026-11-09`, read by `Task:`:
  - 635 commits outside a work ticket;
  - 17 of them touch the trigger paths (11 `decision-record`, 6 `DAEO-sdxk`);
  - 65 touch code, the kernel, tests, settings, the registry or the map.
- **Residuals:**
  - The catch is the trial's, on the trial's 34 cases. A longer window could show other kinds.
  - Seconds are the trial's JUnit medians of 10-30 to 11-02.
  - The `yaml.safe_dump` used in the replay drops the map's comments. The ACT edits the file by hand.
  - (iii) is not built or tried. Its S7 and S8 are a design, not measured.
  - The code route's figures depend on the CTO's run of the script. Its author did not read the sets or the kept
    outputs.
