# Lead brief: integration plan item 1-11 (c), the landing proves the path map covers every path a change adds exactly once (G-8, Q-1 (a); a fix under W2-206, DAEO-l2b2)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store` (the main tree's own store is stale).

## Why
X-1 (DEC-1244): the selection's three inputs are made trustworthy first; 1-0 landed tonight (`fbcf2c9c8`), 1-11 is next. G-8 (a):
code proves the path map covers every tracked path exactly once, at every landing. Q-1 (a), the owner: "a new path the path map does
not hold exactly once is refused at the landing, naming the exact line to add (a record-only document inside an already-mapped folder
still passes with a notice, DEC-1239 (2))." Read row 1-11 of `docs/emergency-2/integration/INTEGRATION-PLAN.md`, RECORDS-MAP's SQ-R1
(`docs/emergency-2/integration/RECORDS-MAP.md`, about lines 348-368) and `governance/project/path-map.yaml`. Gov OS lands by the plain
path (a hand merge running exactly `gov queue ... --select`), so the check must show in `--select`'s answer as well as in the landing.

## What (K-lines as a `## Fix:` section in `.tickets/DAEO-l2b2.md`; the CTO approves them by this brief)
- **PM-1** Before the merge, the landing (and `--select`) runs the path map's coverage (`core-pathmap`'s check) on the merged tree for
  the paths the change adds or renames, and refuses (`PATH_UNMAPPED` / `PATH_MAPPED_TWICE`, or the names the existing check uses) a
  path held by no namespace or by two, naming the path and the exact line to add; there is no switch. Verify: a planted branch adding
  `docs/newfolder/x.md` under no namespace is refused naming the line to add; the same file under a mapped folder lands.
- **PM-2** A record-only document inside a folder the map already holds passes with a notice (DEC-1239 (2)), never a refusal. Verify:
  planted.
- **PM-3** The answer and the close record print `path map: n tracked, 0 in none, 0 in two` for the merged tree. Verify: planted.
- Not in this lead: A3's half of 1-11 (W1-41, adoption stage A3; it waits for the held batch, which changes A3), and `GRAPH_BEHIND`.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-1-11-pathmap`, branch `e2/1-11-pathmap` from `w2/integrate`. Code area: `src/gov/queue/`,
`src/gov/close/select.py` only where `--select`'s answer is built, the path map check's module (find it; reuse it, never copy it),
`tests/unit/queue/`, `tests/acceptance/W2-206/` (the independent test designer only), `.tickets/DAEO-l2b2.md`. Another lead works on
`src/gov/impact/` meanwhile; `e2/bundle-a` and `e2/bundle-b` are held (they change `src/gov/adopt/` and `governance/project/path-map.yaml`):
do not edit their files, and do not edit `path-map.yaml` itself.

## Green
PM-1 to PM-3 red on the base, green after; `gov accept W2-206` green; `--select` on `w2/integrate` itself reports 0 in none and 0 in two
(if not, list the paths and stop that point: the map is the CTO's); then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-l2b2=e2/1-11-pathmap --onto w2/integrate --select`) through the heavy
slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; where the check runs (file:line); PM-1 to PM-3 with tests and result; the coverage counts on `w2/integrate`; the
selected run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: c8ce78a15dfb (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "c8ce78a15dfb86d0d8a321c73351a8de03efc77e",
    "head": "c8ce78a15dfb86d0d8a321c73351a8de03efc77e",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "cf20e662ce174998d256f454",
      "sha256": "dafb96c381d38b475f7c2332b184ea0111d3607af3cfdbe8e33b66ae34281e7d",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 295,
      "end_line": 301,
      "text": "### The spec questions (11), answered\n\n**Q-1. At the landing, is a path the change adds that the path map does not hold exactly once a refusal or a notice?** [records SQ-R1]\n- *Found:* G-8 (a) says code proves exact coverage \"at every landing\"; DEC-1239 (2) says a record-only document is placed with a notice, never refused. They meet on a new folder no namespace holds (18 and 22 November). An unmapped path fails open: memory indexes it by default, so a hidden-set file outside its namespace would be indexed.\n- *Options:* (a) refuse, naming the line to add; cost one bounce per new folder (two in a week). (b) notice and fail doctor; cost: the drift of 22 November (two days unmapped) stays possible. (c) refuse only evaluation, hidden-set or doubled paths; cost a second rule and most new folders still drift.\n- *Recommendation:* (a). *Sources:* DEC-1241 G-8; DEC-1239 (2); `queue/after.py:8`; `path-map.yaml:58-62`; records \u00a73.3, \u00a73.4.\n- *Gates:* 1-11 (built as a refusal, no switch). *Stops:* no.\n",
      "chunk_id": "cf20e662ce174998d256f454",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ee5590f9bc5e8580d19a8235",
      "sha256": "6e8f7d7d978cf6c2d1a8a5a4ad427599aff5b02b0a01d641b02d77492a7f6835",
      "path": "docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html",
      "start_line": 374,
      "end_line": 403,
      "text": "    \"sources\": \"ticket.schema.json; queue/checks.py:121; DEC-1242 R-3; CHAIN-DISCOVERY.md \u00a75.\",\n    \"stops\": \"Gates plan items 2-11 (the property) and 5-11 (KPI_DRIFT). Stops only 5-11.\"\n   }\n  ]\n },\n {\n  \"title\": \"The landing, the loops and the floor\",\n  \"intro\": \"A new folder at the landing, a cap on fix loops, and what the 90 % floor does to a release.\",\n  \"qs\": [\n   {\n    \"id\": \"Q-1\",\n    \"from\": \"records SQ-R1\",\n    \"title\": \"At the landing, is a path the change adds that the path map does not hold exactly once a refusal or a notice?\",\n    \"found\": [\n     \"G-8 (a) says code proves exact coverage \\\"at every landing\\\". DEC-1239 (2) says a record-only document is placed with a notice, never refused. They meet on a new folder no namespace holds (18 and 22 November).\",\n     \"An unmapped path fails open: memory indexes it by default, so a hidden-set file outside its namespace would be indexed.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Refuse, naming the line to add\",\n      \"One bounce per new folder (two in a week).\",\n      1\n     ],\n     [\n      \"b\",\n      \"A notice, and doctor fails\",\n      \"The drift of 22 November (two days unmapped) stays possible.\"\n     ],\n     [\n",
      "chunk_id": "ee5590f9bc5e8580d19a8235",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "b7a5a88d665e0e3cbf5cee0a",
      "sha256": "26200009a9ae970b92523189654d394b021de25fba5d0630642e80915d746b87",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 348,
      "end_line": 368,
      "text": "### SQ-R1. At the landing, is a path the change adds that the path map does not hold exactly once a refusal or a notice?\n\n- **Found:** G-8 (a) says \"code proves it covers every tracked file exactly once, at every landing\". DEC-1239 (2) says\n  \"a record-only document a branch writes is placed as a record with a notice at the landing, never refused\". The two\n  meet on a new document in a folder no namespace holds (the integration folder, the release folders of 18 November).\n  An unmapped path fails open where it matters: memory indexes it by default (`retrieval/lexical.py:154-186` keeps out\n  only what a not-indexed namespace matches), so a hidden-set file put outside the evaluation namespace would be\n  indexed, and the guard's read-denies do not cover it.\n- **Options:**\n  - (a) **Refuse** a path the change adds or renames that falls in no namespace or in two, naming the line to add; the\n    branch adds one line and re-lands. Cost: one bounce per new folder (two such folders in the last week: 18 and 22 November).\n    DEC-1239 (2) stands, because it is about test selection, not classification.\n  - (b) **Notice** at the landing and fail doctor; the CTO adds the line as a chore. Cost: the drift seen on 22\n    November (two days unmapped) stays possible; a hidden-set leak is caught only by the memory measure's scan.\n  - (c) Refuse only a path in an evaluation or hidden-set folder, or in two namespaces; notice for the rest. Cost: a\n    second rule to keep; most new folders still drift until someone reads the notice.\n- **Recommendation:** (a). It is what G-8 (a) asks, the cost is one line in the same branch, and it is the only option\n  that closes the fail-open case in ordinary work.\n- **Sources:** DEC-1241 G-8; DEC-1239 (2); `queue/after.py:8`; `path-map.yaml:58-62`; \u00a73.3, \u00a73.4.\n- **Stops work:** no. Fixes 1 to 3 and 5 to 25 go on; only fix 4's refuse/notice line waits.\n\n",
      "chunk_id": "b7a5a88d665e0e3cbf5cee0a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2a7caa68e040ce484854a6fa",
      "sha256": "bd90fef330eeb6378661043a878393c89da830c5c0baf5ebef133f57f59b884a",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 73,
      "end_line": 73,
      "text": "| 1-11 | **The path map covers every tracked path exactly once, proved at the landing.** (a) The integration folder is in the map: done (`path-map.yaml:62`, records fix 1). (b) A3 refuses a proposal that leaves a tracked path in none or two namespaces (W2-81's A4). (c) Before the merge the landing runs `core-pathmap` on the merged tree for the paths the change adds or renames and refuses those in none or two, naming the line to add; **the landing refuses, with no switch (Q-1 (a), DEC-1244)**; a record-only document inside a folder the map already holds still passes with a notice (DEC-1239 (2)). [G-8 (a); Q-1 (a); X-1; records \u00a73.5 items 2, 5, fixes 3, 4; DEC-1238 (1c)] | (b) W1-41 (DAEO-cdoi); (c) W2-206 (DAEO-l2b2) | fix S + M | 1-0 | W1, W11 | A planted branch adding `docs/newfolder/x.md` under no namespace is refused, naming the line to add; the same file under a mapped folder lands; a record-only document inside a mapped folder lands with a notice. A3 given a planted map with `audits/**` in two namespaces refuses, naming the path and both namespaces. The close record prints \"path map: n tracked, 0 in none, 0 in two\". |\n",
      "chunk_id": "2a7caa68e040ce484854a6fa",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "b3dfd1f27a4d26d157b1a001",
      "sha256": "c1da8d9688feebc0255dc48c3e62d44c98765ffe871739780fa3321e219e976e",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 278,
      "end_line": 295,
      "text": "### 3.5 What makes it the one source (the owner's G-8 (a)), each with its smallest code\n\n| # | Piece | Today | Smallest code | Size | Owner |\n|---|---|---|---|---|---|\n| 1 | **One matcher** | 3 grammars (\u00a73.2) | doctor's `_check_path_map` returns `check.pathmap.check(root)` (unmapped and doubled, named); `adopt/project.classify` uses `check.pathmap._matches` (made public as `pathmap.matches`) and reports a double instead of the first match. Failing tests first: a planted map with `\"*\"` and an unmapped `sub/x` \u2192 doctor fails; a double \u2192 doctor names both. `memaudit/preflight` may stay wider (it fails safe), said in a comment | ~25 lines + 2 tests | fix under W1-27 (doctor) and W1-41 (A2) |\n| 2 | **Exact coverage proved in doctor and at adoption** | doctor unmapped only; A3 no doubles | item 1 gives doctor; A3 refuses a proposal whose resulting map leaves a tracked path in none or two (`stages.py:474-505`, one call to `pathmap.check` on the proposal) | ~15 lines | fix under W1-41 (the A4 fix, DEC-1238 (1c)) |\n| 3 | **Ticket paths checked when planned** | not at all | in `gov brief`'s ready check (and `gov plan`): each `allowed_paths`, `reads`, `needs` glob's fixed prefix (the part before the first `*`) must fall under a namespace of the map; a write path in an evaluation, hidden-set or archive namespace is refused. Codes `PATH_UNMAPPED`, `PATH_FORBIDDEN_NAMESPACE` | ~40 lines | fix under W2-152 (brief), W2-136 (plan) |\n| 4 | **`gov brief` takes each job's paths from the ticket and the map** | `{PATHS}` from `allowed_paths` only (`build.py:398`) | the brief prints, for each ticket path, its namespace, and the role's `reads_denied` from `util/role_paths.expand` (already computes them, `:355-365`); generated at launch per G-3 | ~30 lines | fix under W2-152, with G-3's launch change (W2-21) |\n| 5 | **The landing checks the same** | after-step notice (`queue/after.py`) | before the merge, `pathmap.check` on the merged tree, restricted to paths the change adds or renames; refuse those in none or two, naming the line to add (SQ-R1 for refuse vs notice); doubles of existing paths stay a notice | ~25 lines | fix under W2-206 (after-step) / W2-115b |\n| 6 | **Kept current by adoption and `gov update`** | update adds `governance/updates/**` and nothing more | after `gov update` merges, run `pathmap.check` and write its count into the update record (`update/core.py:595-598`); a new kit folder the adopted map does not hold becomes a notice with the line to add | ~15 lines | fix under W2-17 |\n| 7 | **Scheduled** | nothing | doctor in W16's weekly run (P-1, T-5) carries item 1 | 0 (schedule line) | W2-207 |\n| 8 | **This repository's map exact** | 6 unmapped | add `docs/emergency-2/integration/**` to `docs` (`path-map.yaml:58-62`) | 1 line | chore |\n\nWith 1, 2, 5 and 8, code proves exact coverage at every landing (in the scratch repository and EXAMIN; in Gov OS once\nit moves onto its own tools, DEC-1239 (4)) and in doctor; 3 and 4 make briefs carry it; 6 keeps adopted maps current.\n\n---\n\n",
      "chunk_id": "b3dfd1f27a4d26d157b1a001",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1244",
      "sha256": "0ba8d96600afd933eaa63d2d1a898db1b8c695bee6abc52c7ab8f4cfe0a1f085",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2213,
      "end_line": 2219,
      "text": "  - **X-3 (a):** when EXAMIN's fresh 80 passes, the imports feature (already approved) joins the plan as a fourth stream, so W1 is fully on by the exit.\n  - **X-4 (a):** EXAMIN's memory measure, Contract and planning (WBS, waves, tickets, in the forms this page settles) go ahead now, each for the owner's yes; only executing the plan waits for integrated Gov OS, and is its trial. (Changes DEC-1238 (4).)\n  - **X-5 (a):** after the capacity assessment, run as many streams as the machine holds, within the load gate.\n  - **Q-1 (a):** a new path the path map does not hold exactly once is refused at the landing, naming the exact line to add (a record-only document inside an already-mapped folder still passes with a notice, DEC-1239 (2)).\n  - **Q-2 (b):** a feature ticket names its spec: required for new feature tickets, optional on old ones.\n  - **Q-3 (a):** the nine-part form is the spec; OpenSpec holds the living behaviour beside it, each K-line naming its requirement (to be settled for good when EXAMIN's Contract is drafted, the owner's note on the card).\n  - **Q-4 (a):** a stable id as a KPI line's first token for new feature tickets, with a fingerprint of the list to catch drift.\n",
      "chunk_id": "34afcd7ea8031732cef89855",
      "routes": [
        "lexical"
      ],
      "batch": 1,
      "entry": "DEC-1244",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1245"
      ],
      "in_force": true
    },
    {
      "id": "CONTRACT-v5",
      "sha256": "fd631f054c8d8bb68aed1efee126a09f7058a8f182337a1763472c582e902774",
      "path": "docs/contract/CONTRACT_v5.md",
      "start_line": 61,
      "end_line": 61,
      "text": "| MR-3 | KPIs; the builder never writes its own acceptance tests | The landing refuses a commit that changes `tests/acceptance/` without `Role: independent-test-designer` (or the owner's `Role: owner`), naming the commit, in the Gov OS repository and in an adopted repository (`gov queue`); a feature ticket is not READY until `tests/acceptance/<ticket-id>/` exists and its tests are red on the base; a breach is a forbidden outcome. | W1-09, W1-30, W1-33, W1-05, W1-26, W1-35, W1-42, W2-115b | MR-A-01, MR-B-01 | DEC-065, DEC-069, DEC-906, DEC-1211 |\n",
      "chunk_id": "0c1694b95081dfce7e8cdcf9",
      "routes": [
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "d73838a5e88801bb9c25e440",
      "sha256": "580ff8bf33d979ac0e585967649496bd6a1677d4176b27bb64b5deeef161ae07",
      "path": "docs/emergency-2/briefs/AUDIT-G6-G8-records-and-path-map.md",
      "start_line": 1,
      "end_line": 6,
      "text": "# Audit G-6 with G-8: the records and forms map, and the path map (the owner, DEC-1241 G-6, G-8; a wide audit he asks for, on Opus, DEC-1225 (2))\n\nDecision: DEC-1241. You are read-only: you write only your one output file and commit nothing; no `git push`, no `sudo`; never open `~/examin-eval/**` or `~/gov-os-eval/**` (the hidden question sets). Repositories: Gov OS `/home/usain/Dynamic-Agentic-Engineering-OS` (branch `w2/integrate`), EXAMIN `/home/usain/gov-os-runs/W2-27/examin` (read only). Memory first (`PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 -m gov.cli.main retrieve \"<question>\"`, the whole bundle, once more in your own words); the store may be behind HEAD: where it answers with stale paths, read files and say so. **Decide, never ask:** you run as `claude -p`; a question in your final message is never answered; make the call and state it. Helpers (Agent tool, no model named: Sonnet) only with one narrow area each, returning rows as plain text with evidence (path:line), never whole files; if a helper stops early, do its area yourself. Every claim cites its evidence. Plain, short English. Spec questions you find (the golden workflow, the Contract or a spec unclear or in conflict, or code doing what no spec decides) go in a last section as decision records: the question, what was found, the options with their costs, your recommendation, the sources, whether it stops work (DEC-1238 (10)). Read first: `docs/emergency-2/GOLDEN-WORKFLOW.md`, then DEC-1238 to DEC-1242 in `docs/DECISION_REGISTER.md`, then the owner's page `docs/emergency-2/integration/golden-workflow-decisions.html` (its cards G-6 to G-9 state the task in his words).\n\n**Build on, do not repeat:** the tool map `docs/emergency-2/integration/TOOL-MAP.md` (tools; its hand-offs and rule 5), audit 4 `docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md` \u00a71.5 (templates, the seven missing forms) and \u00a73 (List B: what each job receives and produces), `docs/emergency-2/integration/DECISIONS-HELD.md`, the findings log `docs/emergency-2/integration/FINDINGS.md`.\n\n",
      "chunk_id": "d73838a5e88801bb9c25e440",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "CAP-63.d",
      "sha256": "50d1ba39643b9f9a9940b79fd6b98305d96380e62787cb33e3d13c25637fe132",
      "path": "docs/contract/capabilities/CAP-63.d.md",
      "start_line": 11,
      "end_line": 16,
      "text": "# CAP-63.d: The landing exists in an adopted repository (`gov queue`), not only among Gov OS's own tools\n\nA covers item of CAP-63 (The landing). Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority (DEC-614).\n\n- **Item:** The landing exists in an adopted repository (`gov queue`), not only among Gov OS's own tools\n- **Wave:** W2\n",
      "chunk_id": "ab81955f5a1f8972d2fa26d6",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "CONTRACT-v5",
      "sha256": "a89794db87dcd9ffda4ea2dade6b60f5c55200998da22d06ca2aef638378b672",
      "path": "docs/contract/CONTRACT_v5.md",
      "start_line": 60,
      "end_line": 61,
      "text": "| MR-2 | Closed specifications generate the work | A closed specification produces feature tickets with class, role, depends_on, allowed_paths, KPIs and profile, and `gov check` fails a ticket missing any of them; every required open readiness cell has a linked gap ticket (discovery, data, research or test-design) and `gov check` fails an unlinked one \u2014 created by the planning skill, generated by `gov discover` (`gov readiness --generate` is folded into it, W2-36). | W1-14, W1-35, W1-13, W1-26, W2-36 (gov discover), W1-09, W1-42 | MR-A-02, MR-A-04, MR-B-02, MR-B-04 | DEC-065, DEC-089, DEC-1211 |\n| MR-3 | KPIs; the builder never writes its own acceptance tests | The landing refuses a commit that changes `tests/acceptance/` without `Role: independent-test-designer` (or the owner's `Role: owner`), naming the commit, in the Gov OS repository and in an adopted repository (`gov queue`); a feature ticket is not READY until `tests/acceptance/<ticket-id>/` exists and its tests are red on the base; a breach is a forbidden outcome. | W1-09, W1-30, W1-33, W1-05, W1-26, W1-35, W1-42, W2-115b | MR-A-01, MR-B-01 | DEC-065, DEC-069, DEC-906, DEC-1211 |\n",
      "chunk_id": "aafaafcf62d465a98457ec41",
      "routes": [
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "1ed4e27978e4a66e33ad9514",
      "sha256": "76fcc7debfd9e21916171f41c0d73608441ecda493ac471edb4ea7a548f7137f",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 300,
      "end_line": 305,
      "text": "- *Recommendation:* (a). *Sources:* DEC-1241 G-8; DEC-1239 (2); `queue/after.py:8`; `path-map.yaml:58-62`; records \u00a73.3, \u00a73.4.\n- *Gates:* 1-11 (built as a refusal, no switch). *Stops:* no.\n- **Answered: (a), DEC-1244 Q-1.** A new path the path map does not hold exactly once is refused at the landing, naming the exact line to add; a record-only document inside an already-mapped folder still passes with a notice (DEC-1239 (2)). No switch. Carried by 1-11 (and 1-0, which puts it first in Phase 1).\n\n**Q-2. The ticket's `specification` field: code reads it, no schema states it. Must a feature ticket name its spec, and carry `acceptance_tests.path`?** [records SQ-R2; chain SQ-G7-5]\n- *Found:* `readiness/checker.py:101` and `tasks/queue.py:80` read `specification`; `gov discover` writes it; the schema does not name it; 0 of 271 tickets carry it. The queue treats \"has a spec\" as a non-empty body. `KPI_DRIFT` needs one field that links a ticket to its spec.\n",
      "chunk_id": "1ed4e27978e4a66e33ad9514",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "9c3b144655080ce359d3971a",
      "sha256": "48b3b93b5577190c91f55a402e0007fe8014c9e76b3984435a015d4ca161eced",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 332,
      "end_line": 345,
      "text": "the base and the memory figure. The path map is the best-kept record: EXAMIN's covers all 3,910 files exactly once, and\nGov OS's misses only six files in the integration folder made on 22 November. But two cracks matter more than the\ncount. First, nothing checks coverage where work lands (only a notice after a `gov queue` landing), so a new folder\ngoes unmapped until a test happens to fail. Second, `gov doctor` and adoption read the map with a different glob rule\nfrom the schema, the landing and memory: on Gov OS's own map doctor reports \"pass\" with six files missing, and\nadoption files every one of Gov OS's files under one namespace, as its own A2 record from October shows. The fix is\nsmall and mostly one matcher: doctor and adoption use the map's own rule and report doubles (about 25 lines), A3\nrefuses a double (the A4 fix you already ruled a fix), the landing checks the paths a change adds, and briefs and\nplans check each ticket's paths against the map; then the map can be the one source briefs, the landing and memory\nrely on. One question needs you (SQ-R1: refuse or notice at the landing); the rest are fixes under closed tickets or\nchores.\n\n---\n\n",
      "chunk_id": "9c3b144655080ce359d3971a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "2d6390f049963177177cbddb",
      "sha256": "77a4c5b076a72e0d8ac3e5ca09d149ec07812e2048e21ed05514dfc20cbe1f9e",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 40,
      "end_line": 49,
      "text": "   On Gov OS's map the root namespace `root-files: [\"*\"]` (`path-map.yaml:8-9`) then matches every file: doctor\n   reports **pass with 6 files unmapped**, sees **5,543 files in two namespaces** and cannot report it, and A2 classes\n   **every file as `root-files`**. Gov OS's own A2 record shows it: 1,712 of 1,712 artefacts `namespace: root-files`\n   (`governance/adoption/A2-classification.md`, 2026-10-11).\n3. **A4 (a path in two namespaces) is still not built** in A3 or doctor (DEC-1238 (1c)); only `core-pathmap` reports it.\n4. **No ticket path is checked against the map.** No code in brief, plan, launch, readiness, dispatch or discover loads\n   `path-map.yaml` (helper 1); `gov brief` checks only that `allowed_paths` is not empty (`brief/build.py:161`).\n5. **The brief chain is broken in the middle**, as G-3 says: `gov launch` takes no brief (`launch/command.py:52-81`),\n   its launch record holds the role template's hash, not the brief's (`launcher.py:857`); all 50 briefs in\n   `docs/emergency-2/briefs/` are hand-written; the agent files carry literal slots (`.claude/agents/engineer.md:21`).\n",
      "chunk_id": "2d6390f049963177177cbddb",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "ab9cd91d672776f2afc4c903",
      "sha256": "272aad8dcbb749df9c3218c33723e6ef9ade86239147e5a12d268e8c9f2faf60",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 31,
      "end_line": 41,
      "text": "## 0. The answer in ten lines\n\n1. **The path map is the best-held record in Gov OS, and it is still cracked.** Gov OS: 5,551 tracked files, 0 in two\n   namespaces, **6 in none** (the whole `docs/emergency-2/integration/` folder, made on 22 November; this file makes it\n   7). EXAMIN: 3,910 tracked files, 0 in none, 0 in two. Nothing caught Gov OS's six because the coverage check runs\n   only in `gov queue`'s after-step as a notice (`queue/after.py:8`, `check/structural.py:44`) and Gov OS lands by hand.\n2. **Two grammars read the same map.** The schema says `*` stays inside one folder (`path-map.schema.json:145`). The\n   check, the landing's selection, memory and the impact trace follow it. **`gov doctor` and adoption's A2 use\n   `fnmatch`, where `*` crosses folders** (`doctor/command.py:604-615`; `adopt/project.py:205-216` imports doctor's).\n   On Gov OS's map the root namespace `root-files: [\"*\"]` (`path-map.yaml:8-9`) then matches every file: doctor\n   reports **pass with 6 files unmapped**, sees **5,543 files in two namespaces** and cannot report it, and A2 classes\n",
      "chunk_id": "ab9cd91d672776f2afc4c903",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "808e2b1b8bcabec54eb691de",
      "sha256": "e264c1ab88e21a74b0aa226dda364c0476aa185215d4c28301cc146a61e4cbb6",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 267,
      "end_line": 277,
      "text": "### 3.4 Its cracks so far\n\n| Crack | What happened | Cause in code | State |\n|---|---|---|---|\n| **I-2** (22 Nov) | a record-only document a fix branch wrote refused the landing | the test map's selection, not the path map (`select.py:849`) | fixed in 0.1.5 (`8555186af`): placed with a notice `RECORD_PLACED` (`select.py:884`) |\n| **W2-81's A4** | the rust adopter's map put `governance/project/audits/**` in two namespaces; A9 stopped `FABRIC_INCOMPLETE` naming no file (`W2-81-PROVING-RUN-0.1.4-ANALYSIS.md:87,190`) | A3 and doctor do not check doubles; A2 takes the first match (`project.py:214-215`) | **open**: a fix under W1-41 (DEC-1238 (1c)); `refactor_plan.py:126` claims \"`gov doctor` lists no path held by two namespaces\", which doctor cannot do |\n| **Release folders, 18 Nov** | `docs/emergency-2/release-0.1.3/` in no namespace turned tests red | no coverage check at commit; hand commit | fixed by hand (`4c7bdc77d`, `release-*/**`) |\n| **Integration folder, 22 Nov** (new) | six files in no namespace for two days | the same: the check runs only in the queue's after-step | **open** (\u00a74 fix 1) |\n| **Two grammars** (new) | doctor and A2 read `*` as crossing folders; Gov OS's own A2 record classes 1,712 of 1,712 files `root-files` | `doctor/command.py:604-615`; `adopt/project.py:207` | **open**; contradicts the schema (`path-map.schema.json:145`), so a fix, not a question |\n| **EXAMIN's doctor** | `path_compliance` fails | substring matches of moved paths (audit 6 row 12) | open, F-009; outside the path map |\n\n",
      "chunk_id": "808e2b1b8bcabec54eb691de",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "5687fbbc4869da3381de2e9e",
      "sha256": "1da57464375d908bfbd0a423bc0882178ac87cf03dcb1a5ba38474fbc1cd04b0",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 199,
      "end_line": 200,
      "text": "## 3. The path map (G-8)\n\n",
      "chunk_id": "5687fbbc4869da3381de2e9e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "CONTRACT-v5",
      "sha256": "853cb3a35f1ea40f0b9c5a478a4a9ef7d1c8fc95a1134d5a4c08dce5af97555a",
      "path": "docs/contract/CONTRACT_v5.md",
      "start_line": 25,
      "end_line": 25,
      "text": "| 5.0 | 2026-11-18 | Re-baseline to EMERGENCY-2 (docs/emergency-2/audits/07-contract-rebaseline.md; owner decisions DEC-1214 G5, G6, L3, M1, G7), proposed by group in docs/emergency-2/G5-APPROVAL.md and approved by the owner on 2026-11-19, DEC-1219 (G5-1 to G5-13 yes, G5-7 worded: the scan runs once before a repository goes public or is shared with a third party; CAP-63 to CAP-69 each yes). No guard, no sandbox, no box (CAP-58, CAP-61, CAP-62 and their clauses dropped; \u00a72 Boundary rewritten); pause carried by the launch, the dispatcher and the landing (CAP-05); memory in the brief and a fresh 80 at 95 % end to end, `gov context` retired, hit@k a diagnostic (CAP-01, CAP-10, CAP-15, CAP-17.b, CAP-19.c, CAP-48.a, \u00a72 Token budget); the landing and the flow, no repair ticket, two rounds (MR-1 to MR-3, CAP-23.c, CAP-31, CAP-38, CAP-39, CAP-53, CAP-59, \u00a72 Loop budget); a fresh audit only at the release acceptance and at adoption stages A5, AS, A7 and A10 (MR-4, CAP-47.d, CAP-38.f, CAP-24.c, CAP-33.d); the lean release pinned and hash-verified, no signing, `gov update` in the release (CAP-02, CAP-43, CAP-45, CAP-44.f/.h, CAP-49); gitleaks runs once before a repository goes public or is shared with a third party, never while it is private (CAP-03, CAP-41.g); the run-time tool and the rubric (CAP-04, CAP-22.b, CAP-23.b, CAP-35, CAP-37, CAP-40); the CTO approves every install (\u00a72 Tool installs, CAP-25); Wave 3 is friction. New CAP-63 to CAP-69 (the landing, the run-time tool, memory by construction, the hidden-set scan, backups, the basis line, transcripts kept). Status ACCEPTED. CAP-44.m's leftovers settled: the records' version, DEC-1200 in the decisions list, the source map. 69 capabilities; 239 covers items. |\n",
      "chunk_id": "9b361d318c743291d24efe9e",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "CAP-63.d",
      "sha256": "44dcce9e8872bfc829ed5d42c0a0651556f7328a2ffa5d3f248643e2bf42944a",
      "path": "docs/contract/capabilities/CAP-63.d.md",
      "start_line": 1,
      "end_line": 10,
      "text": "---\nid: CAP-63.d\ntype: capability\nstatus: ACCEPTED\nstate_class: DERIVED\ntitle: The landing exists in an adopted repository (`gov queue`), not only among Gov OS's own tools\ndepends_on:\n- CAP-63\n---\n\n",
      "chunk_id": "0ff619f6d6a8b472c525d6e2",
      "routes": [
        "lexical",
        "semantic",
        "closure"
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
    "duplicates": 40,
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
      "chunk_id": "b7a5a88d665e0e3cbf5cee0a",
      "parent_id": "e8b5bb85f8061103f377a7b9",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 348,
      "end_line": 368
    },
    {
      "chunk_id": "b3dfd1f27a4d26d157b1a001",
      "parent_id": "ee414f9ad5692e886794bb6d",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 278,
      "end_line": 295
    },
    {
      "chunk_id": "d73838a5e88801bb9c25e440",
      "parent_id": "39b4cf664dc488cf29e27f78",
      "path": "docs/emergency-2/briefs/AUDIT-G6-G8-records-and-path-map.md",
      "start_line": 1,
      "end_line": 6
    },
    {
      "chunk_id": "808e2b1b8bcabec54eb691de",
      "parent_id": "806cda0b52e5482b972144e6",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 267,
      "end_line": 277
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "ADR-0001",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "ADR-0002",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-01",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-02",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-03",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-04",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-05",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-06",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-07",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-08",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-09",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-10",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-11",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-12",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-13",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-14",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-15",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-16",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-17",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-18",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-19",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-20",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-21",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-22",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-23",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-24",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-25",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-26",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-27",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-28",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-29",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-30",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-31",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-32",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-33",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-34",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-35",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-36",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-37",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-38",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-39",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-40",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-41",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-42",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-43",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-44",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-45",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-46",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-47",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-48",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-49",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-50",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-51",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-52",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-53",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-54",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-55",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-56",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-57",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-58",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-59",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-60",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-61",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-62",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-64",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-65",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-66",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-67",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-68",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-69",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CHARTER-v6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-4",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-5",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "112cee83e0b57b90b6910b56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c4c58728a5fa509b07624479",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "572367370bde705554059e9e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8683672a8a91fcb6bd9d7010",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c7dad3d31491d2fd3f7926df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "45db20593f6c4dbe377189fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "938488645025455b22b99fa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e84a90604302364382fbeaca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ac5bb6d7a7d74a0dfd0f9f62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "5c319ca879d7e29f4ac3b103",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d4fd33a9e9b468ef2ee82379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ee7fb2526dff2a4fa5f4c00b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "cc2ce371990c713fc091be7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e8950a8c24a066f172087c9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "557579098e787ffd1e3b0fe4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f75f917df92290db36eaa213",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f4a430109051db6b53eb966a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1af4920a62ee8832ff0fec1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "799868b3cb7246a8caa7de66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "3384d861b69cacef122a2793",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ef2e0404951b73fd2a51c303",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-57hm.md",
      "chunk_id": "2fee4aa71ab1320e835e2068",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d8d5ffedbd8b1374012e28ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "6de3e12bbd84098da51b4bdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "3b25834ac5ba410e658fc416",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e465c3733b00bd9bcb27fbb0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c4ef622a07a4bde9ba7c3f9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "bafa70738558c6d41b4442d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "fc868cc581e21c25f063b5ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "5861eb94c29053d039b570b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "bfb39b2b5bb469d6a5756f1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "704a6255174946d81f4f713b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "48c294b1025b3a21b0070bdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "62b21c46352c57d840bd3d1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "00333f344f5b0626635aae04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-57hm.md",
      "chunk_id": "c14ae83a59beeaa850f734f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "05282765a9b193094606a827",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "95a4a0d46dab19bb25c81b7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-G6-G8-records-and-path-map.md",
      "chunk_id": "e9af00ad6aa1e329bd7766f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ac63f1f2e4710a133eaa6c6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d50af533a7972b4a52032237",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.md",
      "chunk_id": "da1a7d2e9829b9baab1e16b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "75fccf287b98364673a6a5ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.a.md",
      "chunk_id": "a1775455d03b9554b25892f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5c7ecebb4eaa755305efd0f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-G6-G8-records-and-path-map.md",
      "chunk_id": "daf8141698730a8f575a7aa9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d6dc2d7e7c683f546651481e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.b.md",
      "chunk_id": "b6a059e93602b4ae556e14cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "567283513d661a86474c4eab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "chunk_id": "4614b2f2bea1967a96f9c774",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "63b2634029fcd77a7d49099e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.c.md",
      "chunk_id": "80a1fbd62576eac5a1fd8018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aeb8b1da6b882f8650ed8631",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.a.md",
      "chunk_id": "1a64f628dd956d9f12e7ea0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "a8f6056984189b1783176382",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5ac2864a00b4d4b7d90bd60c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "01d926ac86145ef28ec8bdf3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-H064.md",
      "chunk_id": "0fdacc98f02517d2136dafeb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7ba4e8f3ff2bc44fddd7ab57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.b.md",
      "chunk_id": "120b6cea3f290594c8d9f67a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "465b5f077fdf9817c1d8a65a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5999785546283b379b524e0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "9f2130430da7c1f6691dea82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.c.md",
      "chunk_id": "4240b3e9abe7352db7fe39e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d7edb1d99f6a1db1e3cd1fca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-57hm.md",
      "chunk_id": "1fbdd2d8e6a5d4b8dca68697",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "79be47e476f5439efd9a3d2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.md",
      "chunk_id": "b26600f14bbb8689c40188f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "6264bbd3683d33384c9cbd12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "d4dd59da50ac0d603f1c9089",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e8c9cbaa0b3adda63285750f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d404afff796890b4c7d3a902",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7e89d62af5aa45446cf548cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7ba70758f3aeb51d8613ce61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "abc522db18f194c70d9580f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "38947694e687ce4112e14411",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "6f5eaeec5611ffa157033d73",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "ede2d2f884bfc1b26b4493cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "5f34dcace36114a101d881d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "89a85be4b1913d73816510fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "24988366b3dbe291e5f34567",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "5f5fa2429834bbb04ef92ca3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f2c1ff8c20b4b7783c2e1d8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "f39ccc24075214442bec46d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "cbaedf1d27319dd6d45fbf92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "eca6d83999bf0aff9d951211",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-57hm.md",
      "chunk_id": "3faa10c912981adddf2bfd2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e08978255fd372e98aaf2947",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "14fccb5d17d5d5ddd50e53d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "a3a41ea519fed7dfe74b0d3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "46f74f1ee5d793972579aa30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e3fb6de18670c9b05326e39c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "00f9324f833ed4efb89f0252",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d886cdb7e7ff21531796cb7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "b2463d8604c7b1ce1efc874c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2844fd711cced06235cc40b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "07ab7803ce8030b21cac145a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "c5f4445a56e6f983bdd1b9b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "d9b51e0d1005a0d899734f97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2ac620d074aca7cca44b9c1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "189b0199f5250bf4eb886b8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "edac295b88993aea8adefa1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "0b8db9656e94f536dc4ad5d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2ddf1149560c2c6e5f17516e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2d5625f554c70fecaf94fb61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4c7cc75476ed8d58f43e46df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/README.md",
      "chunk_id": "ea69ba15ae1f9984cf0e3437",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-l2-4-queue.md",
      "chunk_id": "016527e84e52ab1456320ba8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "144d062fa81a196e2fa656be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f0207a25091522202b5dde66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "6d6f0442e46fb07e775158ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "33cafa168e646bbdcf575ae0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "66b96c7deb4307936196fe49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1b072994bacafd85d25ed39a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "80357a2b33baa49ccb15625a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "bed9fa9d6c1da51588736001",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "5cc74ed1cb449bfbe0541b37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "3b0c3fa1590547cd98a7552d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1a18b1b2b52722d6aa52910e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "6bed0ca4abe49ea679c4b11f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "925ad47c2b83055b4c27c3cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "bab98fb2c2a4dda7f3e6df6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e9b77166731cecbfbab912d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "9eebb1ac1fa79d8568eedbab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "56d8471d36d3a557c3fbbecf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "fe23ca03dd166bb225c17c8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "782088b03f8e74e7bad85c3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "f15528c48233fd55d404853f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-H064.md",
      "chunk_id": "f39a7df6f37b6041372885b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ac46c2d64f37d54c2bda2873",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5fe260bf6f8aa9bb6d6eb95b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1138223d03a41be5799db9a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-emq1.md",
      "chunk_id": "4300c17362b853c45e3bfde6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "6722e06a4298372f9be9c4eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "85858898e1a946c70c0582cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2d61d91e80f3b1498d8687ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "d1744f5e7aaa80adcb4219bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "6725bde267cc764c4a18ce2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "966a4844829247ab9ec22ed7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "477407060917e6877ad12c56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "4741bc6ec4a4ca53140bbc5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "530882ae4786686db887320d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e565b65659ce0c453d2fcce1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "293e8a2a5ea7df80b081626f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d83cf4b9f9273a49c50d6e97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d56d9ca4f3ad867f4a97dd69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "edbf01106e20fbd27a106ed7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "9524a6ee10fc1f99e73b71ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1500d2f059fbd6152f219a4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "000f405c39e555c29469d9eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ffae3c82fed2eb1d0ed16b7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8e3ea894c2f8f0cbafc5ce26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d93ae005d79620ec8c7418aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "9f1a0102828b04fb8f046a81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "ed525d0f8a008559470e8b91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aa2bae76945fe4dde186c666",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "cdf82f0bdc04dee85a2655f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2eeeb2ab8ef79a684f3a39cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "57972e1e22e1204efb9fe925",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "1083ece51a21a4f6b9c473ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ee0bac91f9c9b24e09bc68bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d922fb7824eb5e5166663467",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "ba8b13f8e4c6985caf40525b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "0ff23b735a76cd2c165d7ae9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "bb6faefaeb2787304bd69672",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "756dac68dc16d694b64302e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ec0f1b4abee7b4ad1e9b411b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-H064.md",
      "chunk_id": "5e71812753a2e27a0c282530",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "da3295ab179ee59823a7d435",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5975eb404c84e6a69a53f536",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2ff891398a24d9a50434d0b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "e262d27deacbea94b984b815",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "616300a9c0973f246c4cff64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "ec778d9136536027364da7e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d9e5e5b5593e13bb5f9f7894",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1e429d80eedad8cfb277de35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "29e5ccc543414c7b47e22aa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "9d513497c987f27d9832d5e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "chunk_id": "9e8591eedfdfc2c467e25d89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aa9b5ad5ed882ef8c4940714",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "08bd3a9e807219b021a37af6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4b074bb6abf0b811d62a2b3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R1-GOVCHECK.md",
      "chunk_id": "c958c1fae8656e1556098158",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e36c7c00f708780c34b007cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c242c40e6fe4d1774bba6603",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4a1220a390820a126fe56d51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/README.md",
      "chunk_id": "4be1128e0a8aa851c148eaf5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R1-GOVCHECK.md",
      "chunk_id": "d2de6d1831f25ffce1edb5d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1690ac041c483a4234b44b5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "abe407e45cfb7dc7c4937b29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "399fbd5297f35babf523cb0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4915d8c18ba141aa0a10cb1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "072ca65f519028a2e34b16b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "bd0a58b8efa19483d963abcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "defd21c545be9b6f4a1ff4f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "a48eba3be5f64a3e268961d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7207c4115e67f9ca050fe2b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-40-DAEO-6ox0.md",
      "chunk_id": "ba6ab0bb2360a9b7cc25d993",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "17a84fa6e84fe86965074749",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8518ab4a97f720df5e9a8a40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "0ea1528fd43dad4904f7a676",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ae67a907ee29c838b5dff0dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "54f87fbc75da6acbf44343da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "fdac3bf6e15168eb34aba111",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "83cda8144f2db1f273396208",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "db31479fe2c4ca9441a5cb99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "31570a79f3aa21cda82d0cf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "1e6ef8505c84dc3601f4bbb0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2edfe4b1c19242230de52a9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "289c7df017cbc1890183976b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "75f8cc029d0ecf5c8798c6fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "91351a3d91d35cb73cb651c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "01bb18efb2054fd57f582599",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "86649a38f306566f0f5af185",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "ece86344e3a6867e761705fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "cca99a82f1bbe50e489e7df9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "355e28e6ed634e49b6a316a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e2cab52bf2bc3b8fd833717b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4bf9df88911094209aaf5aa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8253b2771ed41a8b8fbdd5b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "a263d5e82fd8e983ec682603",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "2f327e5245355d9024a16e81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8e4116d0aec0b4625a48e829",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "dd642224f040b8d5355fd66c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5a1aef6797cdf23ea0350eb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "90c37c856daaf97e7ffa18fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "6a9016ed7f08efdf2f7cd4d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-H064.md",
      "chunk_id": "a86a291a1698da9bb6ddeefe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "581d6e7f2d45804ddadf1199",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "67eecf849b4d631beab86f2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "865f7ed8dd4e81b72f2cf905",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4f0c20719fc0220d5d89c382",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "435652af3c3c207a73b6e00d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d234cf0e099ecaa12e93d277",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html",
      "chunk_id": "fee7208acab5f3ce1ed96a59",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "chunk_id": "ff90edb585a8f3ec73a6d381",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "3c67d2c1e4c91124a4ec8a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d5d250c4f9d581bbf20c0df4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "9d05e716e979b2afe8368cb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "46dc0a406b82680d2e20d93c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "chunk_id": "1a1cfc0620a94178c7d2aaee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "773d63e36354f6c8b7316c3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "7cc5b5412d43b87a7cf46647",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-104-DAEO-drhj.md",
      "chunk_id": "61c420bcc876105d852d5cc6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "c243c778baa03017e6d5a355",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "4c3aa5e0dcbbdb86507b20cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "634f82fe4bacd1dcfa0ecbaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "d71f2a757ae4cf195c6ef2a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "547daaa9acdf99898d887edc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "84984b4c1c25755ea9470b2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "068871dafa28f4e4b9430d09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "2a836dd36701d5aff9c884ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "cf789d7ffcf0ce422d65e1e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f9be36cb5a352bacb6d5203c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "afc97bdb5f5b54eeabca51db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/checks/core-pathmap.yaml",
      "chunk_id": "966b35bb8c39215f683c19d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "020ddc431f8750a7c7b5967e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3a8e656f46b3ae457dceecdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "4231e8f70d82c8d4adae3f08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "638c698b448a098a3bb1e7a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWITCHED-OFF-1.md",
      "chunk_id": "c718a478637081ea0d67c797",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "d6c03449f6ff666157733ea7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "fb61fbc95cf0c535046305a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c7b00c65effac83665320ff1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3c9ba3a96bbacb78682c3c8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-159-DAEO-6lid.md",
      "chunk_id": "ef50b5857cf29525b187378b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "b0af20e732b40083246a69bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-183-DAEO-href.md",
      "chunk_id": "7fe30717669a0eb18758b260",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "bdca6a8ecdc9976c772aeac0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/pathmap.py",
      "chunk_id": "b71d27efe2dce3d62a1c32b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html",
      "chunk_id": "51a5958be7c402bded8cd8a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "3a1d319f05be7327ba91f293",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "95549eda076c75d669c84abd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "08822d7987887b662bc9bbdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-130-DAEO-q8cl.md",
      "chunk_id": "652c9af6293f11bef2b2b93a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/tools/counts_notes_v5.md",
      "chunk_id": "81f8c3f1db653714aef20b72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-94-DAEO-g87r.md",
      "chunk_id": "3fb45c5a8faaea7e364e6112",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "5b57c5d0d683eec9c2b60bc3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "e127db69c4b8e3644859ee8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-jsg1.md",
      "chunk_id": "ddee01195ee989c7f5d1a13f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "b53e695d579df344614c4903",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "c5a9ad8ca310e5995625106e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "63dcdee0411999a8addac3b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "05d74f3d59b3193c88af5e99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "2d46a19e273c58c690fcbaea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "060013124d32ac5cb4bbd838",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "6a17a22e40cf112732227d9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "48eaa3f2fd4f6de4d37804ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "eda751f223389e11b74302aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-15a-DAEO-rd0g.md",
      "chunk_id": "6279550813e9416ac60211fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "2b3cc90531b800c7b9e7d0c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-105-DAEO-zpdj.md",
      "chunk_id": "2009e8b67bc40621ff2ce78c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-66c-DAEO-btcs.md",
      "chunk_id": "cfb0110467feb43090b7cb53",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-90b-DAEO-nqa2.md",
      "chunk_id": "2b2c27fcacf8f46674ac8a2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-188-DAEO-zlog.md",
      "chunk_id": "095044d4da745013448ae507",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-179-DAEO-c9n8.md",
      "chunk_id": "2a3e079a79111882232561e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-184-DAEO-6f0s.md",
      "chunk_id": "23ffae4c226d16430fe3e496",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-88a-DAEO-pg6i.md",
      "chunk_id": "8fe665132f0d17d8e6e32a00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "522350a9fbee7b95e1f10988",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-180-DAEO-weh2.md",
      "chunk_id": "8f89298214885be390752279",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "0d720352ab1ded5cfdc4e916",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/SOURCE_MAP.csv",
      "chunk_id": "a3fb6866a64a6f0e85318f9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "a63a1a7dd79127fcbc302c65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "f60975e796dc4d944426e50d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "7bd968ad0c28f97e0789ef51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "fc06f44f4de6b21b3915d62e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-177-DAEO-1k7y.md",
      "chunk_id": "5f653a8fac3000d4b0b37802",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "d8b73da439269b431c5bcd0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "779c85ff6d94aa5dcccc5581",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "3f9a3c9b1600247d9c32b8dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "3157922a2b948c9712d5cd04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "bf51ad8e18a8d7f74c039459",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-110-DAEO-3r1j.md",
      "chunk_id": "8760be5d55b8bb3ae83feb25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-121-DAEO-cb2b.md",
      "chunk_id": "1de875f21c0a4b313e36fbf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-173-DAEO-qz4p.md",
      "chunk_id": "e58cc8ef1714856a967163d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/attribution.py",
      "chunk_id": "45591da29cfe3dcb0ec5794c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "74883afd9486beca42a00cb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "2ea766651933e75a840d3d1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-152-DAEO-o5x1.md",
      "chunk_id": "a9a990d425866e646dba5617",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-157-DAEO-ozyt.md",
      "chunk_id": "bff7528947049297918c7b7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "719b84480c60ec60311741fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-182-DAEO-5y8d.md",
      "chunk_id": "f5506debd111efa0124512cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-52-DAEO-siiz.md",
      "chunk_id": "8811203340d80da2bdae8ca1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "06b204add3134355146d1444",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/orchestration/test_merge_queue_q1.py",
      "chunk_id": "5493dfaefa443d23754b953d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "972e78dd37c0ffef1f679229",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "5098ca32f1e5614674e57ffa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-146-DAEO-f6x3.md",
      "chunk_id": "1317dd4315d2a66313d716c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "31188e4636c8d788ede13d2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-88b-DAEO-aks1.md",
      "chunk_id": "0d36c8cc3da3bbc7d78906fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-153-DAEO-8s85.md",
      "chunk_id": "525afe2b319e7d87bbad1ac5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "99dae813b2b538c701b59e55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-56-DAEO-wnnz.md",
      "chunk_id": "153493fac4af74a97bdc15ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/merge_queue.py",
      "chunk_id": "9df57bae73fb0ef7808c6ad1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "1778413a9d3f7a13867fbc7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-185-DAEO-qyt2.md",
      "chunk_id": "b0ad261ddd9e4cb1856d8e32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-61h-DAEO-h2k3.md",
      "chunk_id": "dea0ecfcc42ae0a75ad9a93b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-42a-DAEO-03ub.md",
      "chunk_id": "6d41e222afe55493df82b2e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "9d65996901d951fb06812a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-120-DAEO-i89t.md",
      "chunk_id": "fdc0ee8d3ebe57d950724a79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-45-DAEO-neam.md",
      "chunk_id": "9362aa644e2a6af0e9dcfb11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-60b-DAEO-ecac.md",
      "chunk_id": "1e6b59fa7f1e30efd7eac881",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "9a91b1c1728374221f9e6568",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html",
      "chunk_id": "3e747a8ccf87e9395515c8ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "130a932360ad2aaf76a64ba5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-115-DAEO-emq1.md",
      "chunk_id": "3286c682fdf76639d4230ce9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-181-DAEO-ywb5.md",
      "chunk_id": "d19bdd889be1d657bed86275",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-190-DAEO-6oj6.md",
      "chunk_id": "d35a2dae5b2dc973fb55e656",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-93-DAEO-6y0x.md",
      "chunk_id": "3dfd6a477e452f6a8000038b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "25d48660955eb5ccb84aaab0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "a978614104f1feb30638ee3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-158-DAEO-8a3f.md",
      "chunk_id": "b4f4833f02b8c8f83690da0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-113-DAEO-g29a.md",
      "chunk_id": "03ab8be04c742552d646db56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-116-DAEO-f58b.md",
      "chunk_id": "8f48b6931cb71afa2acdd1b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-124-DAEO-mb2t.md",
      "chunk_id": "74f8993e509995cbdecfa004",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "a29c6bc068eb122ad394d21f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-154-DAEO-l4gf.md",
      "chunk_id": "aff64845ac9b7abfc3a5f5a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-160-DAEO-fd0p.md",
      "chunk_id": "d40154fb3307e092231ace44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "92051809c825389c3193d126",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-171-DAEO-k1e2.md",
      "chunk_id": "3bb1775c55eb7213bdd794b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/OWNER-GLOSSARY.md",
      "chunk_id": "6fbdb0ec44210979132443e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-121b-DAEO-ifgf.md",
      "chunk_id": "e56dc1ac8cf28bc173fac8fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md",
      "chunk_id": "95cf81eeec34e0b336d5b9ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-178-DAEO-7oxm.md",
      "chunk_id": "cdc6109fea0ea7c2097cc388",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "e46cf5e0916eb5fd368ecd88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-172-DAEO-p8tv.md",
      "chunk_id": "afcca445ca2730ebe8faddbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-174-DAEO-zmo4.md",
      "chunk_id": "218015dda2ed1ef8be1321d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-23-DAEO-kmcr.md",
      "chunk_id": "7d550587f138380a42202284",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-81-DAEO-l78m.md",
      "chunk_id": "e18ea3a7749acd52bc3b2740",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "ad08ab7208005b9c9363aba6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "7867b662b98450637f781eb4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/README.md",
      "chunk_id": "e38f43aa3d0c0bc9b45851ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "3bc4c1a4644a474a2515b9a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/OWNER-GLOSSARY.md",
      "chunk_id": "eb37cd5ebd902330122aefd2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "a8839823ca5ba3f41a3447f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-187-DAEO-0cd2.md",
      "chunk_id": "5e4228e1e6354ac7b6364769",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "53c5e2699a0384ee9161a2dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "4ca9b8ca4f5e4a71ffd27e51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "01b467523442b9593ad53e1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "61478f65372f9b895e0b7ff2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-60a-DAEO-cv58.md",
      "chunk_id": "5b79ab2932f2188b7a1c306a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "2af0d7f239fda5d04b6c144b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "a1f4cf230c74301db2b63c3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "7f67c632d52b3a39b8d2577e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-88-DAEO-2bdu.md",
      "chunk_id": "036f0d5358d0fbe77478fd31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/07-contract-rebaseline.md",
      "chunk_id": "48fc5e1b879f87fba2c1a467",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "1f08e026b29cd33c0a80ef76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "7c1fa4208ee25f66c021c084",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "79ca1f3dfd57d10e9f689e8c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-05-DAEO-0z8c.md",
      "chunk_id": "caed2d05aabf4c11120bb316",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "b8107c02329a05dd23cd4e86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-111-DAEO-qvff.md",
      "chunk_id": "16f9cd47181ea658dcb98957",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "ab7d776f1d09de1e3ddca055",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "86de6e0841fa29d3bfa0871d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "68ee8d497bd1f28eae53b85d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-189-DAEO-kfn1.md",
      "chunk_id": "b2e8ab59222afc10da24508b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "5837ab84e49fb04bec813013",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LIFT-1.md",
      "chunk_id": "4e96c1b1020135b37d8bbf13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "aee2c47503b2332360b4f5c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "0f686c03ea3bb2d789205648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "e95e906a1016fcc9ce8bcb48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "92d61ca1b78f8685c70290c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "fed0a0ddf24a0b0da77f31c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "51ec60d0c851bf6f7bfe3631",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "b2f3d073279a826cc1945182",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "f1c05ad8c38741b366b64ace",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LIFT-1.md",
      "chunk_id": "7e2f54eaad0e23d5295159e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/orchestration/test_merge_queue_q1.py",
      "chunk_id": "ffc930c6e7a059a0eddec38b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "88f4cdfca188e3fdd08a0002",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "5d33a2ef5d839567014ecd87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "399ef6b8596a36d8eb19eb79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "c7b5c996570801d2e3d1e956",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "7a9f387ba1434e1c7732e70a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "9e899733cf74328db1a24806",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "cc012ddf342c1708856dba42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "c66bdca232f6ae378fbd8e43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "98b71825d36a379ffd140ac6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "4702b22276ffbed1426e623c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "2ea2881f687ec7dbaa9b12b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "be6b0c834e86ba98ac0bcd87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/integration-plan-decisions-2026-11-24.html",
      "chunk_id": "349efb59d4ea3c438739eac0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/golden-workflow-decisions.html",
      "chunk_id": "0b7c621c078e504eb4d6ccc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/orchestration/test_merge_queue_q1.py",
      "chunk_id": "e0fd5f107a202222dee65150",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "d0b05f25252deea7d6bb2060",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "3082ddfeedadfa026639a739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "bbcf90e05f24dbd6119df859",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "3df631a54cb299b968a1ffd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "1d5129a937414644b68b11e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "26346fd70108b505270ee4c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "7b122360266b83570b646c80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "3af9e4511d4fb18a0371d238",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "690d3abcbcaeb1b061a2fca4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "d9ff0de1a6d00ee7952ab992",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "b3bc68fd5a3d382df3cfa4fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "d9d3297a0511583bdd66788e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "721768d726a495736a21a5e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "e9587c7fe28d0fa3d80fca99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "2e5d1d746a111eb358d6ad9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "chunk_id": "dea38de5cb3cffde822815fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "244881e09b905dcd5661dd36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "103b509c4b54241f9a353154",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "93741b6f8506f97a8f6fa7a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "06feffa7d351cc570ad5181d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/B1.md",
      "chunk_id": "d3175a0d18feb98c8cc6e81c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "4417a14220fd6a34f0d6b355",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "2e0818d9298a2ecae04c2f15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "8fb1fda544a27f0c98a52242",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "chunk_id": "15a534547060395e1ae2be37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "eec52c7e096cb220717d4840",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "a46f5df216df1cbffab02cfb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "1fcc6139445418dccf47b940",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "5d219e90ce080a0883f64ca7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "1382a74e9b1f1c68f7d063e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "87dc28fc0fc8670c305896d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "chunk_id": "1c869db104a470d770d34cea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "0f20e20d17b3e988772ba05d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "87baf6f01c41d7695f4c8aa3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "cbcba0cedb99e85575e5b7bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-g5-land.md",
      "chunk_id": "9150127e8f5cd941d9230ef0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R1-GOVCHECK.md",
      "chunk_id": "d492d694da20ba40f219739a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "888040277cf4b76caae9d77c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "4d68bef02018f1e19c45e54e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "f725d2f5e9bfaff97dfee87e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "8e7d9b280ddcd5965e079b20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "face4eb1ac9b224c304ab528",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "9c20fef8d5f050b5784e4cbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "f0a1e3a60a4ed8d175863450",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "ce029903a6f27f90280c6a06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "67c548718f87327ed3b860dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "aefaf00c8f1d528405868664",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "43f87272b31a91307f4b5cc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kq8b.md",
      "chunk_id": "90482921a96607b452b679e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "7d661056c14d0159f8d720fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "0f92902227542c0a7295c918",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "4fded7078e8379d5e9d11a89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "0a3559b04fe2b81d835382d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "1075243cae156378f37ac532",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "aac0502c4fb51989f15916e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "fdb53da1d3c4dd40743ab13f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "c7d97fe40a468ea4194e7d58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "ee7e33633a0c9e82364fa3de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "1a3430790b16196dfa2dfa96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "12099bccb8c380393cd0287f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d7-adopt-lands.md",
      "chunk_id": "2b69cadd21f3888473c6ca4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "a621370dbcd008c53db43e75",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "d072eb0ec549f66c0331050f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "767dbddbfaace0a8fe4abb5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "de5a260428dd3d3dd297634b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "695cd95792cdf53766a85480",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "54139f9200fa74eddb0c37bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1047-aim.md",
      "chunk_id": "bb76c3004b3ff643505cc3d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "37a3a45c059a0ae943fcdffa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1047-aim.md",
      "chunk_id": "b672f6f035d8f36451e36a60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "11c7d07628fc7cfe06da74c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "b457f546cf96a61849d2707d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "ce6ade098c444a0a344f73a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "1aed8650b2e74b1406b674a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "99f0c7809d747191fca3d628",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "62e8ae328672bea744ad6731",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "7267abf577fc9e5ad96f01de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "7ccaf6912a3b602d2c532b82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-115b/README.md",
      "chunk_id": "1103b9409db65c5cb7ddccfd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-95/README.md",
      "chunk_id": "745b28037c984d4c68fa4643",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-95/README.md",
      "chunk_id": "b51b7d85dc8612018120cc97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-115b/README.md",
      "chunk_id": "79990bd76b58cc189a133416",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-95/README.md",
      "chunk_id": "67e4a93496fcbf428625f66d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-115b/README.md",
      "chunk_id": "8c7f3ec7c48eab9bda7e2fc6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-95/README.md",
      "chunk_id": "708605ffd796ebf4a26dec67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-95/README.md",
      "chunk_id": "20afc83e3942bc25b749f711",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-95/README.md",
      "chunk_id": "4a705094da92aee4557db59d",
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
    },
    "closure": {
      "available": true,
      "reason": null,
      "followed": {
        "records": [
          "DEC-065",
          "DEC-074",
          "DEC-085",
          "DEC-086",
          "DEC-087",
          "DEC-089",
          "DEC-090",
          "DEC-091",
          "DEC-093",
          "DEC-102",
          "DEC-103",
          "DEC-105"
        ],
        "left": 30
      },
      "changed_by": {
        "DEC-093": [
          "DEC-1236",
          "DEC-220"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5892
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwyMjEzLDIyMTksIjM0YWZjZDdlYTgwMzE3MzJjZWY4OTg1NSJdLFsiZG9jcy9jb250cmFjdC9DT05UUkFDVF92NS5tZCIsMjUsMjUsIjliMzYxZDMxOGM3NDMyOTFkMjRlZmU5ZSJdLFsiZG9jcy9jb250cmFjdC9DT05UUkFDVF92NS5tZCIsNjAsNjEsImFhZmFhZmNmNjJkNDY1YTk4NDU3ZWM0MSJdLFsiZG9jcy9jb250cmFjdC9DT05UUkFDVF92NS5tZCIsNjEsNjEsIjBjMTY5NGI5NTA4MWRmY2U3ZThjZGNmOSJdLFsiZG9jcy9jb250cmFjdC9jYXBhYmlsaXRpZXMvQ0FQLTYzLmQubWQiLDEsMTAsIjBmZjYxOWY2ZDZhOGI0NzJjNTI1ZDZlMiJdLFsiZG9jcy9jb250cmFjdC9jYXBhYmlsaXRpZXMvQ0FQLTYzLmQubWQiLDExLDE2LCJhYjgxOTU1ZjVhMWY4OTcyZDJmYTI2ZDYiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vSU5URUdSQVRJT04tUExBTi5tZCIsNzMsNzMsIjJhN2NhYTY4ZTA0MGNlNDg0ODU0YTZmYSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9JTlRFR1JBVElPTi1QTEFOLm1kIiwyOTUsMzAxLCJjZjIwZTY2MmNlMTc0OTk4ZDI1NmY0NTQiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vSU5URUdSQVRJT04tUExBTi5tZCIsMzAwLDMwNSwiMWVkNGUyNzk3OGU0YTY2ZTMzYWQ5NTE0Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1BMQU4tREVDSVNJT05TLTIwMjYtMTEtMjQuaHRtbCIsMzc0LDQwMywiZWU1NTkwZjliYzVlODU4MGQxOWE4MjM1Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1JFQ09SRFMtTUFQLm1kIiwzMSw0MSwiYWI5Y2Q5MWQ2NzI3NzZmMmFmYzRjOTAzIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1JFQ09SRFMtTUFQLm1kIiw0MCw0OSwiMmQ2MzkwZjA0OTk2MzE3NzE3N2NiZGRiIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1JFQ09SRFMtTUFQLm1kIiwxOTksMjAwLCI1Njg3ZmJiYzQ4NjlkYTMzODFkZTJlOWUiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUkVDT1JEUy1NQVAubWQiLDI4MywyODUsImY4OWNiYmQyYzVjM2RmYzgwZjgyY2IyYiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9SRUNPUkRTLU1BUC5tZCIsMzMyLDM0NSwiOWMzYjE0NDY1NTA4MGNlMzU5ZDM5NzFhIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1JFQ09SRFMtTUFQLm1kIiwzNTgsMzY4LCI3Nzg2MTUyZWFhOTYzZGY1N2U0M2YyMzUiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWIiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6IjQyZDI0YjFmN2RiMTlmOTYiLCJvIjpbMSw0LDAsMywxOSwzMSwzNiwzOSw4LDM1LDYsMiwyNywxNSwyNCwyMiwzMyw1LDksNywzNywxMiwyNiwzNCwyOCwzMiwxNywzOCwyMSwyOSwxMSwxMywzMCwyMCwxOCwxNCwxMCwyMywyNSwxNl19LCJxIjoidGhlIGxhbmRpbmcncyBwYXRoIG1hcCBjb3ZlcmFnZSBjaGVjayBjb3JlLXBhdGhtYXA6IGEgcGF0aCBpbiBubyBuYW1lc3BhY2Ugb3IgaW4gdHdvIHJlZnVzZWQgbmFtaW5nIHRoZSBsaW5lIHRvIGFkZCwgcmVjb3JkLW9ubHkgbm90aWNlLCBRLTEgRy04LCB3aGVyZSBnb3YgcXVldWUgc2VsZWN0IGJ1aWxkcyBpdHMgYW5zd2VyIiwiciI6MCwicyI6ImM4Y2U3OGExNWRmYjg2ZDBkOGEzMjFjNzMzNTFhOGRlMDNlZmM3N2UiLCJ0IjpudWxsLCJ4IjpbIjM5YjRjZjY2NGRjNDg4Y2YyOWUyN2Y3OCIsIjgwNmNkYTBiNTJlNTQ4MmI5NzIxNDRlNiIsImU4YjViYjg1ZjgwNjExMDNmMzc3YTdiOSIsImVlNDE0ZjlhZDU2OTJlODg2Nzk0YmI2ZCJdfQ==",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "the landing's path map coverage check core-pathmap: a path in no namespace or in two refused naming the line to add, record-only notice, Q-1 G-8, where gov queue select builds its answer",
      "landing s path map coverage check core-pathmap path no namespace two refused naming line add record-only notice Q-1 G-8 gov queue select builds answer",
      "the landing's path map coverage check core-pathmap: a path in no namespace or in two refused naming the line to add, record-only notice, Q-1 G-8, where gov queue select builds its answer CAP-63"
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
        "chunk_id": "7786152eaa963df57e43f235",
        "path": "docs/emergency-2/integration/RECORDS-MAP.md",
        "start_line": 358,
        "end_line": 368
      },
      {
        "chunk_id": "f89cbbd2c5c3dfc80f82cb2b",
        "path": "docs/emergency-2/integration/RECORDS-MAP.md",
        "start_line": 283,
        "end_line": 285
      }
    ]
  }
}
