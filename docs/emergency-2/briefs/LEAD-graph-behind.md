# Lead brief: graph-behind, the landing refuses a stale code and test graph (plan item 1-0 (b), the part left; a fix under W2-206, DAEO-l2b2)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store`.

## Why
Plan item 1-0 (b) (`docs/emergency-2/integration/INTEGRATION-PLAN.md`, row 1-0): the selection's inputs made trustworthy, among them
"the code and test graph current, with the landing refusing `GRAPH_BEHIND` when the graph's commit is not the merged tree's base and
refreshing it before the selection runs". 1-0 landed tonight (`fbcf2c9c8`) without this part (its landing record says so); 1-11 (c),
1-8 and 1-9 landed after it. Find first which graph the selection reads (the import graph `select.scoped` uses, the test map, a stored
graph) and where its commit is recorded; if the selection builds its graph fresh from the merged tree every run, say so with file:line
and build only what is missing.

## What (K-lines as a `## Fix:` section in `.tickets/DAEO-l2b2.md`; the CTO approves them by this brief)
- **GB-1** Before the selection runs, the landing and `--select` compare the graph's recorded commit with the merged tree's base;
  when it is behind they refresh it, and when the refresh fails they refuse `GRAPH_BEHIND`, naming both commits. Verify: a planted
  stale graph is refreshed and the selection then runs; a planted stale graph whose refresh fails is refused naming both commits.
- **GB-2** The answer and the close record say which graph commit the selection used. Verify: planted.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-graph-behind`, branch `e2/graph-behind` from `w2/integrate`. Code area: `src/gov/queue/`,
`src/gov/close/select.py`, the graph's own module if it records its commit, `tests/unit/queue/`, `tests/acceptance/W2-206/` (the
independent test designer only), `.tickets/DAEO-l2b2.md`. Another lead works on `src/gov/resources/slots.py` meanwhile; `e2/bundle-a`
and `e2/bundle-b` are held: do not edit their files.

## Green
GB-1 and GB-2 red on the base, green after; `gov accept W2-206` green; then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-l2b2=e2/graph-behind --onto w2/integrate --select`) through the heavy
slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; which graph the selection reads and where its commit is (file:line); GB-1 and GB-2 with tests and result; the selected
run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: fd61f060956d (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "fd61f060956d284b2396587558fc227503d43718",
    "head": "fd61f060956d284b2396587558fc227503d43718",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "1d29ec4ff60877eec61a130f",
      "sha256": "a7d170e655f5e150ad7bc0a27fef847ed1bf56dd316f257bd865576f59489094",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 1,
      "end_line": 6,
      "text": "# P-SELECT-GRAPH-RESULT: the code graph in the scoped selection, the trial's result (DEC-1062; DEC-1097 (9))\n\nBy a research agent for the Wave 2 CTO, 2026-11-08. Research only, on the CPU: nothing was built and no tracked file\nchanged but this one. It is uncommitted; the CTO commits it. The result goes to the owner before anything is built\n(DEC-1062).\n\n",
      "chunk_id": "1d29ec4ff60877eec61a130f",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "152e19b9419b6b7cbf542915",
      "sha256": "10e8e221a6b9d63f2b81f2c017648b4631c86e59fcd381f29df20069b717a1a5",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
      "start_line": 1,
      "end_line": 44,
      "text": "# P-SELECT-GRAPH: should the scoped selection also use W2-92's code graph? (for D-9; short form)\n\nBy the CTO (session 33b3628c), 2026-11-03, at the owner's request. **DECIDED (DEC-1062): (a), the trial in D-9; its result to the owner before anything is built.** Nothing changes\nnow.\n\n**The question.** Today `select_tests.py` (the product's `gov.close.select.plan`) selects by the test map: a changed\npath selects the suites the map ties to it. It misses a regression when a change reaches code that a suite exercises\nbut the map does not tie to that path; such reds surface only in the full run (the nightly, stopped by DEC-1049). The\nowner asks whether the selection should also take the tests of every caller of a changed symbol, from W2-92's code graph\n(now in `w2/integrate`: the code route asks the index by symbol name, then for its call edges in pages of 50).\n\n**What the repository shows (2026-11-03):**\n- Unit tests import the code: 148 of 203 unit test files import `gov`. A reverse call graph reaches them directly.\n- Acceptance tests mostly do not: 37 of 983 acceptance files import `gov`; the rest drive it as a process (the `gov`\n  command, `python -m gov.cli.main`). A call graph sees no edge from such a test to the code it exercises. So the graph\n  alone would catch unit-level regressions and miss most acceptance-level ones.\n- The code index is rebuilt with the store (codeintel; about a minute seeded), so it can be current at a change's head.\n\n**The design that would work:** the union of three, never a replacement:\n1. the test map, as today (the floor);\n2. **callers:** for each symbol the change defines or edits, its callers by the reverse call graph (radius 1 to 2),\n   and the unit tests among them or calling them;\n3. **commands:** the same reverse walk stopped at a `gov` subcommand's handler (the CLI's command table names the\n   handler of each subcommand), then the acceptance tests that run that subcommand (found once per index build by a\n   plain scan of the tests for `gov <subcommand>` or the module form).\nA cap protects the run: a change that reaches a hub (a helper every command calls) selects at most a set share of the\nsuite (e.g. 30 %), then falls back to the test map with a named note. Dynamic dispatch the graph cannot see stays\ncovered by the test map and the full run.\n\n**Options:**\n- **(a) Recommended: a measured trial in D-9, then adopt only if it proves itself** (question 5). A research agent\n  replays the merges of the last two weeks whose reds were traced to a change (the nightly and close records), and\n  computes for each: the test map's selection, the union's selection, which reds each would have caught, the extra cases\n  and their seconds. Adopt if the union catches regressions the map missed at a bounded cost (for example a median of\n  at most +30 % scoped cases); its home is a KPI line in the selection's product ticket (named in D-9's list), with the\n  CTO's `select_tests.py` using it first (in the tools lane) once it has proven itself in use. About half a day for the\n  trial; about a day to build (an engineer and a test designer), if adopted.\n- **(b) Build it now, without a trial.** Faster, but against question 5, and the acceptance tests' process boundary\n  makes its value uncertain without the command step.\n- **(c) Leave the selection as it is.** The full run (now about 1.8 h, DEC-1061) catches what the map misses, but only\n  when it runs (the owner's word, D-10, then the nightly).\n\n**Basis:** question 3 (tests run where the risk is: the change and everything it reaches) and question 2 (a regression\nthe map misses would otherwise reach the integration branch), with question 5 deciding the order (trial before product).\n",
      "chunk_id": "152e19b9419b6b7cbf542915",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1098",
      "sha256": "cc9dc8f827d595c8a5ee9fe94530d8d09fc133a6c016a5262c432d5ded96858d",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1541,
      "end_line": 1569,
      "text": "### DEC-1098 \u2014 The fresh 80 accepted and the measured configuration made Gov OS's memory standard; P-SELECT-GRAPH closed (do not build) with three cheaper fixes to propose; W2-130's sitting accepted; a sandbox-and-guard experiment before W2-56; ADR-0002 accepted; the work restarts in order\n- **Status:** ACCEPTED (owner, 2026-11-09, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-09)`); item (1) standing \u00b7 **Under:** DEC-1097, DEC-1083 (2), DEC-1062, DEC-1073 (5)(a), DEC-1074 (7) O2, DEC-1093 (3), DEC-1072 (2), DEC-799, DEC-1088 (6), DEC-1052 \u00b7 **Source:** the owner's message (chat, 2026-11-09), after FRESH-80-RESULT, P-SELECT-GRAPH-RESULT, W2-130-SITTING and ADR-0002-REFRESH \u00b7 **Changed by:** DEC-1179 (7); DEC-1164 (7) ((6) spent at the lift); DEC-1128 (4): item (4)'s sandbox experiment loses set-up B (dropped entirely, not a Wave 3 row); set-up A stays \u00b7 **Class:** kept (items changed: (1),(2) kept; (4) superseded \u00a72.2; (3),(5),(6) history)\n- **Decision:**\n  - (1) **The fresh 80 accepted; K9's memory line is met** (FRESH-80-RESULT: right end to end 78 of 79, wrong claims\n    0). **Standing:** the measured configuration (the 0.6B reranker, the pool on, today's 6,000-token bundle widened to\n    sections, and agents searching again once) is Gov OS's memory standard, and the memory-building practice for every\n    adopted repository: built at its Wave 0 as W2-88's practice record describes, and proven there with its own tuning\n    set and a fresh verdict set, measured once. The CTO brings W2-88's lines for it as a package.\n  - (2) **P-SELECT-GRAPH:** (a) \"do not build\" accepted for test selection; DEC-1062's trial is closed. (b) The CTO\n    drafts its three cheaper fixes as proposals: the test-map couplings; W2-66's record-only case in the always-run set;\n    a scoped selection on every commit outside a ticket that touches settings, the registry or the test map. The code\n    graph stays in memory as the code route (definitions, callers, callees), unchanged: the CTO confirms it, with the\n    code route's figures on the 138 and the 80 (the callers questions and any question where it supplied the gold).\n  - (3) **W2-130's sitting accepted as proposed:** groups A to G; H1 (b), open and in-progress tickets only, W2-130's\n    KPI 4 changed to say so (marked DEC-1098, DEC-1088 (6)); H2 as recommended. Applied as the record describes.\n  - (4) **Sandboxing and the guard (K6, W2-56): an experiment before the leads are sandboxed.** The bar: every agent\n    action judged right, no false refusal and no wrong allow, 100 %. Two set-ups measured against it: the path-map\n    guard alone, and the guard with the sandbox generated from the same path map; both tuned. If the guard with the\n    sandbox cannot reach the bar, the path-map guard alone is kept. Designed as a package for the owner first (what it\n    measures, on which actions, and how), then run, both results to the owner before W2-56 builds anything.\n  - (5) **ADR-0002 accepted now** (`packages/ADR-0002-REFRESH/`), re-read at the lift's re-pin.\n  - (6) **The work restarts in the CTO's order:** item 8 (W2-141, W2-20 rebuilt, W2-142 and W2-145, tests first);\n    Q07 and Q14 re-worded; W2-139 and W2-140 in one batch; the sitting applied; then D-5 and D-6 part 2; then D-10 on\n    the owner's word, and the lift. Each item ticked off DECIDED-NOT-DONE when done; each new decided item added with\n    its trigger.\n- **Basis:** question 1 (the memory standard proven end to end on a set used once, carried to every adopted\n  repository), question 2 (the guard proven at 100 % before it is widened) and question 4 (no test selector built\n  without a measured gain).\n\n",
      "chunk_id": "395d1b34c63864d042f8a821",
      "routes": [
        "lexical"
      ],
      "batch": 1,
      "entry": "DEC-1098",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1225"
      ],
      "in_force": true
    },
    {
      "id": "ddef442bf0a638230d8a435a",
      "sha256": "68643af6463ba79561cabf33ecca602fdd0d6dc69ad82bbed6d9c6843a18395f",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 21,
      "end_line": 30,
      "text": "## 1. What was run (the declaration, and the readings chosen where it left a choice)\n\nThe declaration is `P-SELECT-GRAPH.md` (a). For each merge whose reds were traced to a change, it asks for: the test\nmap's selection, the union's selection, which reds each would have caught, and the extra cases with their seconds.\nThe adoption bar is \"catches regressions the map missed at a median of at most +30 % scoped cases\".\n\n| Open point | Reading chosen (conservative) | Why |\n|---|---|---|\n| \"The last two weeks\" | 2026-10-20 to 2026-11-08: the two weeks before the declaration (11-03) and the days since, together | The superset loses no evidence. No full run took place after 11-02 (DEC-1049). |\n| Which reds | Every red that a record traces to a named change (the nightly packages, the close and merge-queue logs, the \"red fixed on the spot\" commits), once, at its first appearance | The declaration names \"the nightly and close records\". The merge queue and the fix commits are the same kind of record. |\n",
      "chunk_id": "ddef442bf0a638230d8a435a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "d46bb9192c33894b2ccb6bdf",
      "sha256": "a17060e2d513a88bef216c2cbe8dceef11784164adbfefb76f6b9980e193222c",
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "start_line": 144,
      "end_line": 157,
      "text": "## 3. Proposal (iii): a scoped selection on every commit outside a ticket that touches settings, the registry or the test map\n\n**What changes.** The CTO's tools lane comes first; the product line is optional (\u00a75 decision 4).\n1. A new tool, `.gov-runtime/scratch/orchestrator/tools/outside_ticket_select.sh <old head> <new head>`, modelled on\n   `act_clone_run.sh`:\n   - It lists the first-parent commits of `old..new` whose `Task:` is not a work ticket (`DAEO-sdxk`, W2-00's, or\n     `decision-record`; ACTs included).\n   - If they touch `.claude/settings*.json`, `.rulesync/**`, `governance/project/tool-registry.yaml` or\n     `governance/project/test-map.yaml`, it takes a clone at `new` and runs\n     `select_tests.py <clone> W2-00 DAEO-sdxk --base <old>`.\n   - It then runs the selection's targets in the heavy slot (`heavy_slot.sh`, no full run), and writes the verdict to\n     the CTO's inbox and to `log/outside-ticket/<stamp>/`.\n2. Its trigger is one line in `.git/hooks/reference-transaction`, the hook W2-116 installed at re-pin window 4. The\n   hook already starts the store refresh after every landing on `w2/integrate`. A second `setsid -f` line starts the\n",
      "chunk_id": "d46bb9192c33894b2ccb6bdf",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2ad53afa366a6cd808b5c46a",
      "sha256": "124fe0d75793ed6fb58c6f43f28fc297c1b68687035dceb42ecf965fbc7c682a",
      "path": "docs/research/W2-115-smart-close.md",
      "start_line": 130,
      "end_line": 131,
      "text": "| S2 scoped selection | `select.scoped`: the change is every path since the newest green record (the strict close's `select.base`) with the ticket's own commits (eng-2: a record commit without the ticket's trailer, or a path merged since the green base, is the change); own suite, couplings, test files, other tickets' paths, the import graph (and a module named as text); records alone \u2192 `record_reading` and nothing else (not even the own suite); `governance/project/` alone \u2192 nothing; unmapped \u2192 `SELECTION_REFUSED`; never `tests/` whole | `select.py`: 11; `close.py`: 2 |\n| S3 `--select` | prints `{\"ticket\",\"suites\",\"pytest_options\"}` (the options the same on every machine: `--timeout=<per-test limit>` always; without pytest-timeout the run does not complete, fail closed), exit 0; refused: stderr, exit 2; the close record's `selection` is the same object | `select.py`: 2; `close.py`: 1 |\n",
      "chunk_id": "2ad53afa366a6cd808b5c46a",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "6e9019ca52af518ef1092dcc",
      "sha256": "8eba86cd03b4b9d2e768b186fbc61e83b74123062af65e15a20d071f95f8abb1",
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "start_line": 1,
      "end_line": 7,
      "text": "# P-SELECT-FIXES-1: the three cheaper fixes from P-SELECT-GRAPH, as proposals; the code route stays (DEC-1098 (2)(b))\n\nBy a research agent for the Wave 2 CTO, 2026-11-09. This is a proposal only, made on the CPU. Nothing is applied,\nand no tracked file has changed but this one, which is uncommitted (the CTO commits it). Each proposal needs its own\nowner decision (DEC-1098 (2)(b)). The test selector on the code graph is not built (DEC-1098 (2)(a); DEC-1062\nclosed).\n\n",
      "chunk_id": "6e9019ca52af518ef1092dcc",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "977adaff6d046bc82ed088a6",
      "sha256": "323728db86c5ef7f65938f9325b4f964a3724daadcacf01ae470f21a6b4e3602",
      "path": "docs/emergency-2/audits/04-classification.csv",
      "start_line": 1261,
      "end_line": 1264,
      "text": "6cf2e7d2d,direct commit,DAEO-sdxk,,orchestrator,\"The plan's status: D-4 done (merged 6008a41f; ACT-G14b open), D-4b's four merges done and measure 1 running\",chore,4.6r,records only,,,,0,0,1,,,,,,,direct commit (2026-11-03),direct commit,no,\r\n156a5feb6,direct commit,DAEO-zqvn,,orchestrator,W2-13: P-W2-13-R3 (a) as a delegated line in its ticket (DP-3 kept; the spec question to W2-32 S5); merged in D-4b,chore,4.6r,records only,,,,0,0,1,,,,,,,direct commit (2026-11-03),direct commit,no,\r\n7524fa042,direct commit,decision-record,,orchestrator,\"DEC-1062 (owner): P-SELECT-GRAPH (a), the code-graph selection trial in D-9, its result to the owner before anything is built\",chore,4.6r,records only,,,,0,0,2,,,,,,,direct commit (2026-11-03),direct commit,no,\r\n21325f303,direct commit,DAEO-sdxk,,orchestrator,\"P-SELECT-GRAPH: the code graph in the scoped selection, a proposal for D-9 (a trial first; callers plus the commands' tests, as a union with\",chore,4.6r,records only,,,,0,0,1,,,,,,,direct commit (2026-11-03),direct commit,no,\r\n",
      "chunk_id": "977adaff6d046bc82ed088a6",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "3740d31a49f752bd1db16fd7",
      "sha256": "6de8dc4dee0ff403f9c226ba09c837a303468097042d714c7335c037c0ddac3d",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 33,
      "end_line": 36,
      "text": "| The change | A merge: its first parent to the merge. A plain commit: its parent to the commit. W2-81's unmerged head: the merge base with the commit the queue tested it on, to the head | This is how `select_tests.py` reads `--merge` and `--base`. |\n| The code graph | W2-92's tool, `codebase-memory-mcp` 0.11.0, built fresh on the tree at each culprit commit (about 16 s each). Edges: CALLS and CALL_REFERENCE, plus USAGE as the first hop from an edited module variable | The tool and graph that `gov.codeintel` reads. |\n| \"Each symbol the change defines or edits\" | Every function, method and class whose source differs or is new (AST compare of parent and child), plus edited module-level assignments. Removed symbols are named but have no node | This is the widest reading of \"defines or edits\". |\n| Callers, \"radius 1 to 2\" | Both radii measured. Tests taken are those among the reached nodes or calling them, **selected as whole files** | Whole files give the union its best chance to catch, and they make its cost the highest. |\n",
      "chunk_id": "3740d31a49f752bd1db16fd7",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ad379569ddf6da946e741142",
      "sha256": "ef838a6371bc29a9cc1dcc6fa05839d64e4872374059498cff908ea23f2cea66",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 30,
      "end_line": 33,
      "text": "| Which reds | Every red that a record traces to a named change (the nightly packages, the close and merge-queue logs, the \"red fixed on the spot\" commits), once, at its first appearance | The declaration names \"the nightly and close records\". The merge queue and the fix commits are the same kind of record. |\n| Left out | Reds the records put down to load, the machine or the environment, plus untraced reds and misattributions the records later corrected (list in \u00a76) | No change caused them, so no selection can catch them. |\n| The map | Today's `select_tests.py` (sha256 `a18d8e7a\u2026`) with today's `src/gov/close/select.py` (integrate `0732a0a7`), run on the tree at each culprit commit, with that tree's test map and tickets | The same selection logic for every replay. Only the data is historical. |\n| The change | A merge: its first parent to the merge. A plain commit: its parent to the commit. W2-81's unmerged head: the merge base with the commit the queue tested it on, to the head | This is how `select_tests.py` reads `--merge` and `--base`. |\n",
      "chunk_id": "ad379569ddf6da946e741142",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "366381c25cf985074abc95c5",
      "sha256": "332282f9e0b47e9ac8b8ec0766f0458e887bbef9fe2bd4a008732ea609a561fc",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 124,
      "end_line": 132,
      "text": "| K6 | 1: W1-01's integration-merge rule | A merge commit's own conflict resolution in a W1-30 test file, with `Role: orchestrator` | A rule over git history. The test runs no code the change touched |\n| K10 | 1: W1-50's whole-tree fixture scan | A new whole-tree fixture in W2-108's test file | W1-50 scans the tests' text. There is no call edge to it |\n| K16 | 1: W2-54's no-weakening case | Three lines in `secrets-indexing.yaml` (DEC-1045's decided change; the test needed a revision) | A YAML edit. The union catches it only through the unbounded walk to `check`, with the whole file selected |\n\nThe graph adds reach along call edges between Python functions. In this window, no red reached a test that way\nunseen. On the changes that touched Python, the reds were either in the map's selection already, put there by\ntickets' `allowed_paths`, test-changed suites, helpers or couplings (K1, K5, K8, K9, K10's W1-28 case, K12), or\ncaused by something other than a call edge (K4, K6, K10's W1-50 case, K16). All of `tests/unit` is in every\nmap selection (reason `UNIT`; 3,641 cases, 791 s), so the callers step can only add acceptance files. The declaration\n",
      "chunk_id": "366381c25cf985074abc95c5",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "0fb3c7aa8c1ec96d273ee1c1",
      "sha256": "c9c5eeb5706d2cc25217a92de1bd217513bf09c37da7a4cb299e7679725da48f",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 182,
      "end_line": 185,
      "text": "  W2-86 core-mutation red (the case id is not recorded). The product traceability red after W2-70's close (its cause\n  is commit messages, not paths).\n- **W1-01 history (DEC-906):** known before the window.\n\n",
      "chunk_id": "0fb3c7aa8c1ec96d273ee1c1",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "d7ecbedfb05da14a31f65536",
      "sha256": "5e8368bbea51617089cc4c3da5220176753322df2a87178f884fa6bb7fadaa91",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 156,
      "end_line": 170,
      "text": "2. **W2-66's record-only case in `record_reading`**, or a selection run on governance-only commits. Three of the 12\n   misses (K3a, K4, K13) are this one case, red after a new kind of file landed under `governance/`. It is now\n   W2-66b's (the `.ps1` half).\n3. A selection run once on every CTO commit or merge that touches settings, the registry or the test map. K2, K18a\n   and K18c ran no selection at the time.\n\n**For the owner to decide:**\n- (a) Accept \"do not build\". DEC-1062's trial is then closed with no W2-115 line (D9-FATES \u00a72), and D-9's last\n  open item is done.\n- (b) Whether any of the cheaper fixes 1 to 3 above should be drafted as proposals. Each would need its own\n  decision; this trial decides none of them.\n- (c) Whether the three readings marked as mine are acceptable: the cap on what the graph adds, whole-file\n  selection, and the window 10-20 to 11-08. No other reading changes the verdict. With every generous reading\n  together (radius 2, unbounded walk, generous scan, whole files), the union still catches only K16's incidental case.\n\n",
      "chunk_id": "d7ecbedfb05da14a31f65536",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "87af7b7ee7ff77183f9d536e",
      "sha256": "3a58c1db01e43328bc6e30018a6c6a02014a6f6dc3eed24aa2ffe4d1a1a51d2c",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 115,
      "end_line": 124,
      "text": "## 4. What it shows\n\n**The map's 12 misses, by cause.** For each, could the graph have seen the cause?\n\n| Miss | Red cases | What caused it | Graph |\n|---|---|---|---|\n| K2 | 6: W1-33 \u00d74, W2-54 sandboxed worker, W1-46 | `.claude/settings.json` and `.rulesync/hooks.jsonc`: the hook wiring. The tests copy or read the live settings | No Python changed. The hook code under `.claude/` is also left out of the index by the tool itself (`excluded: .claude`) |\n| K3a, K13 | 2: W2-66's record-only case | A new `.patch` and a new `.diff` under `governance/project/orchestration/packages/` | No code. `select_tests.py` also drops `governance/project/orchestration/**` from the change first (DEC-953 4a) |\n| K4 | 1: the same W2-66 case | `win_toast.ps1` under the same folder | Not Python. The commit's only .py files are two unit tests, which have no callers |\n| K6 | 1: W1-01's integration-merge rule | A merge commit's own conflict resolution in a W1-30 test file, with `Role: orchestrator` | A rule over git history. The test runs no code the change touched |\n",
      "chunk_id": "87af7b7ee7ff77183f9d536e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "f62f14c550327d4caa5029d7",
      "sha256": "3a2b0d55a04e74eeee2ca9d658648776a2b23e3323152758ca35b532429f11b0",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 219,
      "end_line": 236,
      "text": "## 9. Raw outputs and how to rerun\n\nEverything is under `~/gov-os-runs/P-SELECT-GRAPH/`:\n- `repo/`: a local clone; each replay checks out the culprit commit there.\n- `tool/`: frozen copies of today's `select_tests.py`, its two lists and `src/` (integrate `0732a0a7`).\n- `scripts/`:\n  - `cases.json`: the 18 cases with their records;\n  - `all_merges.json`: the 113 merges;\n  - `junit_table.py`, `replay.py`, `aggregate.py`, `summary.py`.\n- `raw/`:\n  - `junit_table.json`: per-case median seconds and the 35 sources;\n  - `cases/`: per case, the map's JSON, the union's variants and `results.json`;\n  - `all-merges/`: the supplementary measure;\n  - the run logs.\n- `cbm/<sha>/home/code.db`: the code graph of each culprit tree.\n\nRerun: `cd ~/gov-os-runs/P-SELECT-GRAPH && python3 scripts/junit_table.py raw/junit_table.json && python3\nscripts/replay.py scripts/cases.json raw/cases && python3 scripts/aggregate.py raw/cases/results.json`\n",
      "chunk_id": "f62f14c550327d4caa5029d7",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "601d25e48ee6e48eb129be26",
      "sha256": "0f613edb28725839c07c9e40767ada07f65607e233038b7a4d1ef39865b1e741",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 144,
      "end_line": 157,
      "text": "## 5. Recommendation\n\n**Do not build the union. Option (c) of P-SELECT-GRAPH for the graph: leave the selection as it is.** Confidence:\nmedium-high (sample size and K16 below). It meets the cost bar. But in two weeks of traced reds it caught nothing the\nmap missed except one incidental case, so it fails \"adopt only if the union catches regressions the map missed\".\nBuilding it would cost about a day (an engineer and a test designer) for no measured gain.\n\nThe 12 misses point to cheaper fixes. They are listed for the CTO and owner to weigh, and none is part of this trial:\n1. **Couplings in the test map** for the classes seen: `.claude/settings.json` and `.rulesync/hooks.jsonc` \u2192 W1-33,\n   W1-46 and W2-54's sandboxed-worker file; `template/governance/kernel/checks/**` \u2192 W2-54's time-limit file;\n   `tests/acceptance/**` (new fixtures) \u2192 W1-28 and W1-50's fixture scans; a merge commit's own changes \u2192 W1-01's\n   integration-merge case. Each is one test-map line.\n2. **W2-66's record-only case in `record_reading`**, or a selection run on governance-only commits. Three of the 12\n   misses (K3a, K4, K13) are this one case, red after a new kind of file landed under `governance/`. It is now\n",
      "chunk_id": "601d25e48ee6e48eb129be26",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "d92ff4a73a753e47b5d69c81",
      "sha256": "60bf84e9c727466cfcabd1627997fb9f9b52d090dce470a3f1122c8d07bc8ab6",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 211,
      "end_line": 218,
      "text": "  - Case counts and seconds come from JUnit XMLs of 10-30 to 11-02, not from a collection at each commit. For the\n    11-03 to 11-07 merges they predate D-4's cut, so their shares are approximate.\n  - K14's red case is inferred as W1-08's path-map case: the record says \"core-pathmap red\".\n  - Three readings are mine: the cap (\u00a71), whole-file selection, and K2's grouping of W2-90's 7 named reds under\n    ACT 1.\n  - The graph misses dynamic dispatch (the CLI loads each command module by name). The handler step works around\n    that, as the declaration says.\n\n",
      "chunk_id": "d92ff4a73a753e47b5d69c81",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "0c24fc724a00d577a7a00632",
      "sha256": "e08e8107bb04ee06e57e515c9b1958de3420fc6e851f6f80079372fbefc57f5f",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "start_line": 131,
      "end_line": 143,
      "text": "caused by something other than a call edge (K4, K6, K10's W1-50 case, K16). All of `tests/unit` is in every\nmap selection (reason `UNIT`; 3,641 cases, 791 s), so the callers step can only add acceptance files. The declaration\ncounts 37 of 983 acceptance files that import `gov`.\n\n**Also seen (outside the question, for the owner's reading):**\n- 12 of the 22 caught reds came from commits outside any ticket, which no close or queue run selects for: the ACTs\n  and the CTO's record commits (K2's 4, K3b, K7, K14, K15, K18a's 3, K18c). The map would catch them, mostly through\n  its always-run sets (`record_reading`), but only if a selection ran on such commits. They were found later, by the\n  next close or full run that happened to run the case.\n- K12's 11 reds were in the map's selection: OVERLAP, because W2-122's ticket holds `tests/unit/rebuild/test_w2_122_seed.py`,\n  which W2-126's merge changed. They reached integrate because the D-1 merge ran no selection, not because the map\n  missed them.\n\n",
      "chunk_id": "0c24fc724a00d577a7a00632",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 38,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "152e19b9419b6b7cbf542915",
      "parent_id": "f8d1cd680b939abd536d9b89",
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
      "start_line": 1,
      "end_line": 44
    },
    {
      "chunk_id": "395d1b34c63864d042f8a821",
      "parent_id": "411508e5dcf62b0f80c665ba",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1541,
      "end_line": 1569
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "d36c7e6c3033fa125021c973",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "51d793ae69752d8a76bded2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "f07bfd2643f270c42241be7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "f2852b53dacd06e54ce3f7fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "5f81edd2f41e515d2249dbab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "d63a0be72711ed7ffaa65a4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "7d902df1d575f6682ab65f03",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "2c815227fbc541eb1b646570",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
      "chunk_id": "e8ef343c754ba495b7e6857d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "84f3462110d630cdb53e6415",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "2d14b0e06608ad5ab8c6cd2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "62a9477a1358e96b9fee49f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "87ef05db06d43c988e998a97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "645939fa5a12e28513735704",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "34450c04c240ded117d183cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "64a4fcacf5bd7337a95d5b8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "df21e04ba41f71cdb1afd867",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "e1e117e32d8595a50e699f6d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "a3bbd6b1b2e9887f46b20152",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "78ba97799bf26ce3d103fa0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "41accb7e87167eca64319283",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "d044f25a4ec28b2524140688",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "75a191f2b78bb1e16d436a62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "d3267e65a5d5e414553ed6e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "2ea2881f687ec7dbaa9b12b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "69082a9026ba89a3d348b828",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-btcs.md",
      "chunk_id": "470147e4737f8c966f2e71c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "c76f47d80a18175863946f2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "8c82e9cc5e32bfcdeace5d1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "8e1ee2e632be4b33ca5385a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "349e3447198b93be0e069e2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "70458978daca6c53c705ab89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "075a80ea7a247c631ee71594",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "f8a6b6110401c69352e364fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "bdd30a8766cd4c15e3b96d3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "d7967d334c63dadddd5d9bac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "885630cdacb19e23a5c2e718",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "7852a5a51fd0c021acaa2379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "44572e3c994ecb813153ec2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "9da0b4dbd6e23a336abb56c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88-evidence.md",
      "chunk_id": "31b2a17633d06b03f285f183",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-115-smart-close.md",
      "chunk_id": "59b79662db9fff31edaf9289",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l2b2.md",
      "chunk_id": "66567bfd010a5070dbd5a015",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "60daac28ca7c27bed75f5674",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "3306f0a4a44ab707737003fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "076327fe754d9738d3cbc800",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "395f766bd23f48a657f9c450",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "30fbdf12a1136f2333798c40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "4668c25ae33b75bae31f00e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "523d339a8b68f603f789b44e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-c1uz.md",
      "chunk_id": "0f060cc0bbde30c8b90348f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "6994c8ac36609340484988a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88-evidence.md",
      "chunk_id": "cf5c293e0ec16b03d8b8c11e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "93bdda5a5ffbee290fb1a905",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "29f86214d49c36072d109da0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "51c94448282583d1abd94596",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-68-batched-close.md",
      "chunk_id": "285ff387b2970f1ef2d60786",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "chunk_id": "1c869db104a470d770d34cea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "04b6420d90af0ab4eef13a0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-115-smart-close.md",
      "chunk_id": "c2fb6daafa024fce2df576bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "602043d58ffaf7c20bf6701f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "794d1c368074408eb4d5b2c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "e2f73e4623236910b89a76fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-emq1.md",
      "chunk_id": "d33fb7de4a0fc57fe76eed48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-memory-measure.md",
      "chunk_id": "ad707370dcc45a5c1e795480",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "eb0bd8ff01b9df7ea31bfab3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "23829260ed117e4bc51a8bbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-115/test_w2_115_selection.py",
      "chunk_id": "ec3cfffe3b6024205102427b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-66/README.md",
      "chunk_id": "a9574edace306a56d45ca867",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "1c15360cf4d8a5a8122c30aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-66/README.md",
      "chunk_id": "5286558c6e034dd89b62977a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "49346c4f3f3621a474e0fe18",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5918
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyJkb2NzL2VtZXJnZW5jeS0yL2F1ZGl0cy8wNC1jbGFzc2lmaWNhdGlvbi5jc3YiLDEyNjEsMTI2NCwiOTc3YWRhZmY2ZDA0NmJjODJlZDA4OGE2Il0sWyJkb2NzL3Jlc2VhcmNoL1cyLTExNS1zbWFydC1jbG9zZS5tZCIsMTMwLDEzMSwiMmFkNTNhZmEzNjZhNmNkODA4YjVjNDZhIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVNFTEVDVC1GSVhFUy0xLm1kIiwxLDcsIjZlOTAxOWNhNTJhZjUxOGVmMTA5MmRjYyJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1TRUxFQ1QtRklYRVMtMS5tZCIsMTQ0LDE1NywiZDQ2YmI5MTkyYzMzODk0YjJjY2I2YmRmIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVNFTEVDVC1HUkFQSC1SRVNVTFQubWQiLDEsNiwiMWQyOWVjNGZmNjA4NzdlZWM2MWExMzBmIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVNFTEVDVC1HUkFQSC1SRVNVTFQubWQiLDIxLDMwLCJkZGVmNDQyYmYwYTYzODIzMGQ4YTQzNWEiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtU0VMRUNULUdSQVBILVJFU1VMVC5tZCIsMzAsMzMsImFkMzc5NTY5ZGRmNmRhOTQ2ZTc0MTE0MiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1TRUxFQ1QtR1JBUEgtUkVTVUxULm1kIiwzMywzNiwiMzc0MGQzMWE0OWY3NTJiZDFkYjE2ZmQ3Il0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVNFTEVDVC1HUkFQSC1SRVNVTFQubWQiLDExNSwxMjQsIjg3YWY3YjdlZTdmZjc3MTgzZjlkNTM2ZSJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1TRUxFQ1QtR1JBUEgtUkVTVUxULm1kIiwxMjQsMTMyLCIzNjYzODFjMjVjZjk4NTA3NGFiYzk1YzUiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtU0VMRUNULUdSQVBILVJFU1VMVC5tZCIsMTMxLDE0MywiMGMyNGZjNzI0YTAwZDU3N2E3YTAwNjMyIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVNFTEVDVC1HUkFQSC1SRVNVTFQubWQiLDE0NCwxNTcsIjYwMWQyNWU0OGVlNmU0OGViMTI5YmUyNiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1TRUxFQ1QtR1JBUEgtUkVTVUxULm1kIiwxNTYsMTcwLCJkN2VjYmVkZmIwNWRhMTRhMzFmNjU1MzYiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtU0VMRUNULUdSQVBILVJFU1VMVC5tZCIsMTgyLDE4NSwiMGZiM2M3YWE4YzFlYzk2ZDI3M2VlMWMxIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVNFTEVDVC1HUkFQSC1SRVNVTFQubWQiLDIxMSwyMTgsImQ5MmZmNGE3M2E3NTNlNDdiNWQ2OWM4MSJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1TRUxFQ1QtR1JBUEgtUkVTVUxULm1kIiwyMTksMjM2LCJmNjJmMTRjNTUwMzI3ZDRjYWE1MDI5ZDciXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtU0VMRUNULUdSQVBILm1kIiwyNCwzNiwiYTkyYjU0YmM5YWZlZGNlZjQ2ZTlhMjE4Il0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVNFTEVDVC1HUkFQSC5tZCIsMzYsNDQsIjI5YTQ3MjhmZjUxNjZlZWM3OTViOTg5MSJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYiIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiYWQxMDRjOGUzOGM0MmQxMiIsIm8iOlsxLDcsMzksNSw5LDIyLDM4LDM2LDI5LDIsMCwxNSwxMCwzLDYsMTQsMjMsNCw4LDExLDM3LDE5LDI1LDI4LDEzLDE4LDE2LDM0LDE3LDEyLDIwLDI2LDMxLDI3LDMyLDI0LDIxLDMzLDM1LDMwXX0sInEiOiJ0aGUgc2VsZWN0aW9uJ3MgY29kZSBhbmQgdGVzdCBncmFwaDogd2hpY2ggZ3JhcGggc2VsZWN0LnNjb3BlZCByZWFkcywgd2hlcmUgaXRzIGNvbW1pdCBpcyByZWNvcmRlZCwgR1JBUEhfQkVISU5ELCByZWZyZXNoIGJlZm9yZSB0aGUgc2VsZWN0aW9uIiwiciI6MCwicyI6ImZkNjFmMDYwOTU2ZDI4NGIyMzk2NTg3NTU4ZmMyMjc1MDNkNDM3MTgiLCJ0IjpudWxsLCJ4IjpbIjQxMTUwOGU1ZGNmNjJiMGY4MGM2NjViYSIsImY4ZDFjZDY4MGI5MzlhYmQ1MzZkOWI4OSJdfQ==",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "the selection's code and test graph: which graph select.scoped reads, where its commit is recorded, GRAPH_BEHIND, refresh before the selection",
      "selection s code test graph graph select.scoped reads commit recorded GRAPH_BEHIND refresh selection"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": [
      {
        "chunk_id": "a92b54bc9afedcef46e9a218",
        "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
        "start_line": 24,
        "end_line": 36
      },
      {
        "chunk_id": "29a4728ff5166eec795b9891",
        "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
        "start_line": 36,
        "end_line": 44
      }
    ]
  }
}
