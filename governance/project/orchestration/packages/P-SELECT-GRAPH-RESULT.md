# P-SELECT-GRAPH-RESULT: the code graph in the scoped selection, the trial's result (DEC-1062; DEC-1097 (9))

By a research agent for the Wave 2 CTO, 2026-11-08. Research only, on the CPU: nothing was built and no tracked file
changed but this one. It is uncommitted; the CTO commits it. The result goes to the owner before anything is built
(DEC-1062).

## Headline

Over the 18 changes that reds in the window were traced to, there are 34 red cases. A case here is a test function;
parametrized ids are counted once, and K12's 11 cases count once as their suite. The test map's selection, run on
each change, would have caught **22 of the 34**. The union (map + callers + commands) would have caught **22** with
reverse walks of radius 1 or 2. It would have caught **23** only when the walk to the command handlers is unbounded.
That one extra case is incidental: a W2-54 case that reads a YAML declaration and runs no `gov`. It came in only
because the sibling cases in its file run `gov check`. Of the 12 reds the map missed, 11 came from changes the graph
cannot see: settings and hook wiring, records under `governance/`, a `.ps1` file, a merge commit judged by a history
rule, and a static scan of test fixtures. The cost is within the bound: the median added cases is +1.7 % to +14.3 %
on the changes that touch Python, depending on the variant, and 0 % over all 18 changes. **The adoption test fails
on its first half: the union catches no regression the map missed, except one incidental case. Recommendation: do
not build it (option (c) for the graph). The misses have cheaper causes, listed in §5.**

## 1. What was run (the declaration, and the readings chosen where it left a choice)

The declaration is `P-SELECT-GRAPH.md` (a). For each merge whose reds were traced to a change, it asks for: the test
map's selection, the union's selection, which reds each would have caught, and the extra cases with their seconds.
The adoption bar is "catches regressions the map missed at a median of at most +30 % scoped cases".

| Open point | Reading chosen (conservative) | Why |
|---|---|---|
| "The last two weeks" | 2026-10-20 to 2026-11-08: the two weeks before the declaration (11-03) and the days since, together | The superset loses no evidence. No full run took place after 11-02 (DEC-1049). |
| Which reds | Every red that a record traces to a named change (the nightly packages, the close and merge-queue logs, the "red fixed on the spot" commits), once, at its first appearance | The declaration names "the nightly and close records". The merge queue and the fix commits are the same kind of record. |
| Left out | Reds the records put down to load, the machine or the environment, plus untraced reds and misattributions the records later corrected (list in §6) | No change caused them, so no selection can catch them. |
| The map | Today's `select_tests.py` (sha256 `a18d8e7a…`) with today's `src/gov/close/select.py` (integrate `0732a0a7`), run on the tree at each culprit commit, with that tree's test map and tickets | The same selection logic for every replay. Only the data is historical. |
| The change | A merge: its first parent to the merge. A plain commit: its parent to the commit. W2-81's unmerged head: the merge base with the commit the queue tested it on, to the head | This is how `select_tests.py` reads `--merge` and `--base`. |
| The code graph | W2-92's tool, `codebase-memory-mcp` 0.11.0, built fresh on the tree at each culprit commit (about 16 s each). Edges: CALLS and CALL_REFERENCE, plus USAGE as the first hop from an edited module variable | The tool and graph that `gov.codeintel` reads. |
| "Each symbol the change defines or edits" | Every function, method and class whose source differs or is new (AST compare of parent and child), plus edited module-level assignments. Removed symbols are named but have no node | This is the widest reading of "defines or edits". |
| Callers, "radius 1 to 2" | Both radii measured. Tests taken are those among the reached nodes or calling them, **selected as whole files** | Whole files give the union its best chance to catch, and they make its cost the highest. |
| Commands, "the same reverse walk stopped at a subcommand's handler" | Two readings: the radius-limited walk, and an unbounded walk that stops at each handler (`run` in `src/gov/<x>/command.py` or `src/gov/cli/commands/<x>.py`). A change to `src/gov/cli/main.py` reaches every subcommand | The unbounded walk is the generous reading. |
| "A plain scan of the tests for `gov <subcommand>` or the module form" | Strict: `gov <sub>` in a string, `"gov", "<sub>"` or `gov.cli.main", "<sub>"`. Generous: also `"<sub>"` as a quoted argument in a file, or beside a helper of its suite, that drives `gov` (`run_gov`, `_gov(`, `cli_support`, `COMMAND` and the like) | Most suites pass the subcommand to a helper as a string, so the strict scan misses them. |
| The cap ("at most a set share of the suite, e.g. 30 %") | Applied to what the graph adds: added cases over 30 % of the suite means the map plus a named note | The map alone selects 19.5 % to 39.7 % of the suite. A cap on the union's total would trip on most changes before the graph added anything. |
| Cases and seconds | Per case, the median JUnit time over the 35 XMLs of 10-30 to 11-02 (19,915 case ids, close to the pre-cut full suite). A file missing from them counts its top-level tests at 0 s | The nightly's own XMLs did not survive the restart. These are the nearest full and scoped runs. |

Eight variants were measured: radius 1 or 2, commands walk radius or unbounded, and scan strict or generous. Variant
names have the form `r2-unbounded-generous`.

**Check of the replay against the selections the real closes made:** for W2-107 (K9) and W2-55 (K5), the replayed map
selection equals the close's own `select-*.json`, with the same base. The only difference is two W1-07 files fewer
(40 against 42, and 39 against 41): DEC-1061's T-7 helper exception, added since, drops them. Neither holds a red.

## 2. The cases (18 changes, 34 red cases)

Columns: the map's cases and seconds; red cases (all), (map) and (union); added cases for `r2-radius-generous` and
`r2-unbounded-generous`, each as share of the map's cases and seconds.

| Case | Culprit | Changed (.py) | Map: cases (s) | Reds | Map | Union r2-radius / r2-unbounded | Added: r2-radius / r2-unbounded |
|---|---|---|---|---|---|---|---|
| K1 | `cd2566415` W2-71's merge | 16 (15) | 5,402 (11,445) | 1 | 1 | 1 / 1 | +3 (0.1 %, 16 s) / +454 (8.4 %, 1,530 s) |
| K2 | `6c36c7b5c` ACT-1-GUARD switched on (settings, hooks) | 2 (0) | 5,394 (9,664) | 10 | 4 | 4 / 4 | 0 |
| K3a | `bd07b6503` ACT-1-GUARD's patch (a record) | 0 after the governance leave-out | 3,367 (3,466) | 1 | 0 | 0 / 0 | 0 |
| K3b | `9f4484488` W2-71's close record | 0 after the leave-out | 3,367 (3,466) | 1 | 1 | 1 / 1 | 0 |
| K4 | `42104b116` the CTO's tools (`win_toast.ps1`) | 2 (2 unit tests) | 3,879 (3,722) | 1 | 0 | 0 / 0 | 0 |
| K5 | `e0cb7d13c` W2-55's merge | 18 (16) | 5,620 (13,863) | 1 | 1 | 1 / 1 | +295 (5.2 %, 721 s) / same |
| K6 | `9b03ac0b5` W2-67's merge (carrying `0568d91b`) | 24 (19) | 5,090 (12,260) | 1 | 0 | 0 / 0 | 0 |
| K7 | `7224a5641` W2-120 filed (AR-5) | 0 after the leave-out | 3,882 (3,722) | 1 | 1 | 1 / 1 | 0 |
| K8 | `166f459f4` W2-81's head (probe records) | 30 (23) | 4,176 (3,805) | 5 | 5 | 5 / 5 | +181 (4.3 %, 1,054 s) / +1,242 (29.7 %, 6,609 s) |
| K9 | `73736f4b8` W2-107's merge | 22 (20) | 6,625 (21,133) | 1 | 1 | 1 / 1 | +136 (2.1 %, 323 s) / +1,914 (28.9 %, 4,367 s) |
| K10 | `789513df6` W2-108's first merge | 11 (9) | 3,919 (4,743) | 2 | 1 | 1 / 1 | +2,551 (65.1 %, 6,243 s) / +3,194 (81.5 %, 10,915 s) |
| K12 | `0c5d7f4c9` W2-126's merge (the D-1 merge, no queue run) | 28 (24) | 5,657 (14,862) | 1 (the suite's 11) | 1 | 1 / 1 | over the cap: the map with a note (uncapped +6,481 / +6,990, 115 % / 124 %) |
| K13 | `49158e131` ACT-GUARD-FIX-3's `.diff` (a record) | 0 after the leave-out | 4,083 (3,884) | 1 | 0 | 0 / 0 | 0 |
| K14 | `b60ff1120` review records moved | 0 after the leave-out | 4,185 (3,954) | 1 | 1 | 1 / 1 | 0 |
| K15 | `7fa7fe54e` DEC-1033 (DEC-798 superseded) | 0 after the leave-out | 4,089 (3,885) | 1 | 1 | 1 / 1 | 0 |
| K16 | `c72ededc5` emg/noscan (DEC-1045) | 10 (9) | 7,790 (21,297) | 1 | 0 | **0 / 1** | +194 (2.5 %, 516 s) / +1,112 (14.3 %, 6,346 s) |
| K18a | `8ba8b231a` the settings regeneration (DEC-921 B) | 3 (0) | 4,828 (5,404) | 3 | 3 | 3 / 3 | 0 |
| K18c | `82f2d4538` the first re-pin (the registry) | 1 (0) | 3,342 (3,456) | 1 | 1 | 1 / 1 | 0 |

The red case ids, the culprits and the record each comes from are in `~/gov-os-runs/P-SELECT-GRAPH/scripts/cases.json`.
The full outputs, per variant, are in `raw/cases/<id>.json` and `<id>-map.json`.

## 3. The counts

**What each catches (34 red cases over 18 changes):**

| Selection | Caught | Missed |
|---|---|---|
| Test map | 22 | 12 |
| Union, radius 1 or 2 (all four variants) | 22 | 12 |
| Union, unbounded commands walk (all four variants) | 23 (+1: K16, incidental) | 11 |

**The cost (added cases as share of the map's cases):**

| Variant | Median, all 18 | Median, the 9 that touch .py | Largest | Median added seconds (.py) | Capped |
|---|---|---|---|---|---|
| r1-radius-strict | 0 % | 1.7 % | 69.6 % | 263 s | 0 |
| r2-radius-generous | 0 % | 2.1 % | 114.6 % | 323 s | 1 (K12) |
| r1-unbounded-generous | 0 % | 14.3 % | 83.9 % | 4,356 s | 0 |
| r2-unbounded-generous | 0 % | 8.4 % (14.3 % uncapped) | 123.6 % | 1,530 s | 1 (K12) |

Every variant meets the cost bar (a median of at most +30 %). The spread is wide. A change near a hub adds 65 % to
124 %: K10 (retrieval freshness) and K12 (the embedding client).

**Supplementary: the cost over every merge in the window (not part of the declared measure).** 113 first-parent
merges on `w2/integrate` from 10-20 to 11-08. 100 were replayed. The other 13 (10-20 to 10-24) predate W2-66's test
map, so the selection refuses them (`TEST_MAP_MISSING`). Of the 100, 87 touch Python. The map selects a median of
22.1 % of the suite (15.2 % to 81.6 %).

| Variant | Median added, all 100 | Median added, the 87 that touch .py | Over +30 % | Capped | Largest |
|---|---|---|---|---|---|
| r1-radius-strict | 0.0 % | 0.3 % (16 s) | n/a | 0 | 107.6 % |
| r2-radius-generous | 0.2 % | 2.5 % (456 s) | 19 of 87 | 2 | 132.1 % |
| r1-unbounded-generous | 2.0 % | 5.2 % (647 s) | n/a | 1 | 127.5 % |
| r2-unbounded-generous | 0.8 % | 4.5 % (618 s) | 24 of 87 | 4 | 166.0 % |

So the median cost is small. About one Python merge in four or five would add more than 30 %. The largest are
W2-15a, W2-136 (`gov plan`), W2-126, D-6 part 1, W2-66 and W2-16: changes to shared helpers that many commands reach.

## 4. What it shows

**The map's 12 misses, by cause.** For each, could the graph have seen the cause?

| Miss | Red cases | What caused it | Graph |
|---|---|---|---|
| K2 | 6: W1-33 ×4, W2-54 sandboxed worker, W1-46 | `.claude/settings.json` and `.rulesync/hooks.jsonc`: the hook wiring. The tests copy or read the live settings | No Python changed. The hook code under `.claude/` is also left out of the index by the tool itself (`excluded: .claude`) |
| K3a, K13 | 2: W2-66's record-only case | A new `.patch` and a new `.diff` under `governance/project/orchestration/packages/` | No code. `select_tests.py` also drops `governance/project/orchestration/**` from the change first (DEC-953 4a) |
| K4 | 1: the same W2-66 case | `win_toast.ps1` under the same folder | Not Python. The commit's only .py files are two unit tests, which have no callers |
| K6 | 1: W1-01's integration-merge rule | A merge commit's own conflict resolution in a W1-30 test file, with `Role: orchestrator` | A rule over git history. The test runs no code the change touched |
| K10 | 1: W1-50's whole-tree fixture scan | A new whole-tree fixture in W2-108's test file | W1-50 scans the tests' text. There is no call edge to it |
| K16 | 1: W2-54's no-weakening case | Three lines in `secrets-indexing.yaml` (DEC-1045's decided change; the test needed a revision) | A YAML edit. The union catches it only through the unbounded walk to `check`, with the whole file selected |

The graph adds reach along call edges between Python functions. In this window, no red reached a test that way
unseen. On the changes that touched Python, the reds were either in the map's selection already, put there by
tickets' `allowed_paths`, test-changed suites, helpers or couplings (K1, K5, K8, K9, K10's W1-28 case, K12), or
caused by something other than a call edge (K4, K6, K10's W1-50 case, K16). All of `tests/unit` is in every
map selection (reason `UNIT`; 3,641 cases, 791 s), so the callers step can only add acceptance files. The declaration
counts 37 of 983 acceptance files that import `gov`.

**Also seen (outside the question, for the owner's reading):**
- 12 of the 22 caught reds came from commits outside any ticket, which no close or queue run selects for: the ACTs
  and the CTO's record commits (K2's 4, K3b, K7, K14, K15, K18a's 3, K18c). The map would catch them, mostly through
  its always-run sets (`record_reading`), but only if a selection ran on such commits. They were found later, by the
  next close or full run that happened to run the case.
- K12's 11 reds were in the map's selection: OVERLAP, because W2-122's ticket holds `tests/unit/rebuild/test_w2_122_seed.py`,
  which W2-126's merge changed. They reached integrate because the D-1 merge ran no selection, not because the map
  missed them.

## 5. Recommendation

**Do not build the union. Option (c) of P-SELECT-GRAPH for the graph: leave the selection as it is.** Confidence:
medium-high (sample size and K16 below). It meets the cost bar. But in two weeks of traced reds it caught nothing the
map missed except one incidental case, so it fails "adopt only if the union catches regressions the map missed".
Building it would cost about a day (an engineer and a test designer) for no measured gain.

The 12 misses point to cheaper fixes. They are listed for the CTO and owner to weigh, and none is part of this trial:
1. **Couplings in the test map** for the classes seen: `.claude/settings.json` and `.rulesync/hooks.jsonc` → W1-33,
   W1-46 and W2-54's sandboxed-worker file; `template/governance/kernel/checks/**` → W2-54's time-limit file;
   `tests/acceptance/**` (new fixtures) → W1-28 and W1-50's fixture scans; a merge commit's own changes → W1-01's
   integration-merge case. Each is one test-map line.
2. **W2-66's record-only case in `record_reading`**, or a selection run on governance-only commits. Three of the 12
   misses (K3a, K4, K13) are this one case, red after a new kind of file landed under `governance/`. It is now
   W2-66b's (the `.ps1` half).
3. A selection run once on every CTO commit or merge that touches settings, the registry or the test map. K2, K18a
   and K18c ran no selection at the time.

**For the owner to decide:**
- (a) Accept "do not build". DEC-1062's trial is then closed with no W2-115 line (D9-FATES §2), and D-9's last
  open item is done.
- (b) Whether any of the cheaper fixes 1 to 3 above should be drafted as proposals. Each would need its own
  decision; this trial decides none of them.
- (c) Whether the three readings marked as mine are acceptable: the cap on what the graph adds, whole-file
  selection, and the window 10-20 to 11-08. No other reading changes the verdict. With every generous reading
  together (radius 2, unbounded walk, generous scan, whole files), the union still catches only K16's incidental case.

## 6. Left out of the case list (no change caused them, or no trace)

- **Load or the machine:** W1-19 and W1-21's real-model cases (the embedder on the CPU, 11-02). The W1-19 warm query
  (10-31). W2-54's time limit (10-30, 11-02). The W1-02, W1-05 and W2-57 p95 cases in a 10-31 batch (W2-106's close
  record: "reds caused by the change: none"). The W1-50 read-merge flaky candidates. W2-123's embedding-cap builder
  tests under a heavy slot (fixed by `043f82222`).
- **The environment:** the six dispatcher unit tests of 11-02 read the CTO's untracked scratch tools. `tests/unit` is
  in every selection, so the selection was not at fault. W2-110's three cases red until the pinned gov was renewed.
- **Misattributions the records corrected:** the batch-of-eight trace of W1-46, W1-05 and W1-33 to the batch
  (P1-MORNING-11-01: a wrong baseline). The W2-66 red blamed on W2-05, W2-55 and W2-96 (its real culprit is K4).
- **No trace in the records:** 10-25's W1-03 head-move case. 10-21's two reds. 10-31's W2-61 visible-half case. The
  W2-86 core-mutation red (the case id is not recorded). The product traceability red after W2-70's close (its cause
  is commit messages, not paths).
- **W1-01 history (DEC-906):** known before the window.

## 7. Basis against DEC-1052's five tests

1. **Memory, spec and KPIs, roles, ticket traffic:** neutral. It serves the regression floor, not these.
2. **Would ordinary work fail open or lose work without it?** No. In this window no regression that the union would
   have caught reached integrate unseen, apart from one incidental case. The misses that did reach it are fixed more
   cheaply by test-map couplings (§5).
3. **Does it run only where the risk is?** It runs on Python changes only. Near a hub it adds 65 % to 124 % to a
   scoped run for no measured catch. The cap stops that, at the price of a fallback.
4. **More delivery with less drift, or more machinery?** More machinery: an index per change, a walk, a scan and a
   cap with a note, for zero measured catches.
5. **Proven in use before entering the product:** it was not proven here, so by this test it does not enter.

## 8. Cost, time, confidence, residuals

- **Cost and time:** about 50 minutes of wall time on 2026-11-08 (01:05 to 01:50 GMT). That covers the evidence
  search, the replay of the 18 cases (about 4 minutes) and the supplementary 100 merges (28 minutes). Then the
  record. One research session. CPU only, at `nice` 10 to 19. No GPU, embedder, reranker, `gov retrieve` or
  `gov rebuild`, no full suite, and no tests run. Each code graph index took about 16 s. Each selection took about
  2 s.
- **Confidence: medium-high** in "the union adds no catch that matters". The sample is the window's traced reds: 18
  changes, 34 cases. Only 9 changes touched Python. A longer window could show a miss of the kind the graph sees: an
  acceptance test that drives a command, reached through code, with no ticket path, helper or coupling tying it to
  the change. None appeared in these two weeks. The cost figures depend on reading choices, so the record gives
  their range.
- **Residuals:**
  - Case counts and seconds come from JUnit XMLs of 10-30 to 11-02, not from a collection at each commit. For the
    11-03 to 11-07 merges they predate D-4's cut, so their shares are approximate.
  - K14's red case is inferred as W1-08's path-map case: the record says "core-pathmap red".
  - Three readings are mine: the cap (§1), whole-file selection, and K2's grouping of W2-90's 7 named reds under
    ACT 1.
  - The graph misses dynamic dispatch (the CLI loads each command module by name). The handler step works around
    that, as the declaration says.

## 9. Raw outputs and how to rerun

Everything is under `~/gov-os-runs/P-SELECT-GRAPH/`:
- `repo/`: a local clone; each replay checks out the culprit commit there.
- `tool/`: frozen copies of today's `select_tests.py`, its two lists and `src/` (integrate `0732a0a7`).
- `scripts/`:
  - `cases.json`: the 18 cases with their records;
  - `all_merges.json`: the 113 merges;
  - `junit_table.py`, `replay.py`, `aggregate.py`, `summary.py`.
- `raw/`:
  - `junit_table.json`: per-case median seconds and the 35 sources;
  - `cases/`: per case, the map's JSON, the union's variants and `results.json`;
  - `all-merges/`: the supplementary measure;
  - the run logs.
- `cbm/<sha>/home/code.db`: the code graph of each culprit tree.

Rerun: `cd ~/gov-os-runs/P-SELECT-GRAPH && python3 scripts/junit_table.py raw/junit_table.json && python3
scripts/replay.py scripts/cases.json raw/cases && python3 scripts/aggregate.py raw/cases/results.json`
