# Lead brief: tool-status, the tool status list for 0.1.7 and a draft for 0.1.8 (DEC-1252 TL-0 to TL-11; a chore)

You are a lead (Sonnet, medium; the product-spec profile), started by the Gov OS CTO on 2026-11-26. **Read
`docs/emergency-2/briefs/LEAD-COMMON.md` first** (memory first with `--root /home/usain/gov-os-worktrees/W2-00-store`, never cut a
result, never open a sets root). Decide, never ask (I-10). You write two documents; no code.

## Why
DEC-1245 (1) and DEC-1252 (TL-0 to TL-11, all (a)): each release ships a tool status list, set by the CTO from the tool map and the
findings: green (proven, use now), amber (standby: do the step by hand, the plain path), not yet in the product (a documented equivalent
meanwhile); a tool moves to green only once proven on the scratch repository. The plan of today
(`docs/emergency-2/integration/PRACTICE-FIRST-PLAN.md` §2.1 items 1-2 and conflicts C3, C4, C5, with the CTO's rulings) says how.

## What
- `docs/releases/0.1.7/TOOL-STATUS.md`: the proposals' list (`docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md` §1) re-read
  against 0.1.7 (tag `v0.1.7`, commit `3d039a8fb6d3`) and FINDINGS up to I-42: each row the tool, its status, the reason in one line
  with its source (finding, landing record, test), and for amber and not-yet the hand step or equivalent. C3: the memory refresh is amber
  (built, not proven on the scratch repository), its cron equivalent kept; C4: the "never run `gov impact` on a record id" line holds for
  0.1.7. Check first that `docs/releases/0.1.7/` exists and that `gov release` does not read extra files there (C5's note: verification
  reads the manifest's files from `template/`); if adding the file there would break any release check, write it to
  `docs/emergency-2/release-0.1.7/TOOL-STATUS.md` instead and say why.
- `docs/emergency-2/release-0.1.8/TOOL-STATUS-DRAFT.md`: the same list moved to what has landed since 0.1.7 on `w2/integrate` (1-0,
  1-8, 1-9, 1-11 (c), 1-13, memaudit-launch, timing-tests, release-rule, the card) and what batch A and batch B would add if landed
  (mark those "if batch A lands" / "if batch B lands"); nothing turns green without its scratch proof (DEC-1245 (1)).
- A one-paragraph message for the EXAMIN and ASMO OS CTOs (in your return, not sent): which tools they use now and which by hand.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-tool-status`, branch `e2/tool-status` from `w2/integrate`; commit with `Role: orchestrator`,
`Task: chore`, `Class: C`. Check that both new paths are held by the path map exactly once (`gov queue X=e2/tool-status --onto
w2/integrate --select` says `0 in none, 0 in two`, or names the line to add: add it in your branch if it is a docs folder line).

## Return
Branch and head; counts by status for each list; the rows whose status changed from the proposals and why; the product CTOs' paragraph;
your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: decisions, history and plans; uncut)
store: 5eb29e7ff560 (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "5eb29e7ff560a27a00d5e91d36d3f3648f0e8c0a",
    "head": "5eb29e7ff560a27a00d5e91d36d3f3648f0e8c0a",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DEC-1245",
      "sha256": "646bbf572813691be9e1c8c9059ed2ba9f72147cfb2aa4ba4f32bbf230ace880",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2238,
      "end_line": 2238,
      "text": "  - (1) **Practice first, code catches up.** \"From now, every repository works by the golden workflow v2 as written practice: its rules in CLAUDE.md and AGENTS.md and in every brief. Products use only the Gov OS tools proven in real use.\" Each release ships a **tool status list**, set by the CTO from the tool map and the findings: **green** (proven, use now; the owner expects memory and its measure, `gov adopt`, `gov update`, `gov doctor`, `gov accept`, the kit's settings), **amber** (standby: products do that step by hand as the workflow says, the plain path; he expects the landing, `gov launch`, `gov brief`, `gov impact`, the dispatcher), and **not yet in the product** (a documented equivalent meanwhile, such as a cron line for the memory refresh and the weekly measure). A tool moves from amber to green only once the integration has proven it on the scratch repository; products then gain it through `gov update`. Gov OS's integration, Wave 2's close and Wave 3 go on as planned, and the emergency norm still holds for Gov OS itself until its tools are proven; \"but no product waits for Gov OS any more: each new release helps it.\"\n",
      "chunk_id": "6aa9542dd431661ee697fff1",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-1245",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1250",
        "DEC-1248"
      ],
      "in_force": true
    },
    {
      "id": "0c122f4bbf91b38ddb6d7e0e",
      "sha256": "249a23dc67c73dba06e80386343ac034a2cfb8e3932ac8cf2b2a7b9db2ba88b4",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 22,
      "end_line": 39,
      "text": "## 1. The tool status list\n\n**Problem.** DEC-1245 (1) says products use only tools proven in real use, and each release ships a list with a green, amber and \"not yet\" status for each tool. No such list exists. Without it a repository's CTO cannot tell a tool that works from a tool that is built (GW \u00a71 \"Today\" column is typed by the CTO and says \"partly\" for 11 of 16 steps).\n\n**Proposal.** One row for each tool the golden workflow's steps use, from TOOL-MAP \u00a71 (102 rows, of which 55 are in the product and 37 outside it; I kept the ones a product's steps need, 52). Three statuses:\n\n- **Green:** proven in real use (named: EXAMIN, W2-81's run, Gov OS's own work), and no open finding that fails open or loses work in ordinary use. Use it now. The row says what to read to know it worked (a record, not the exit code, DEC-1240).\n- **Amber:** built, not proven. The step is done by hand as the workflow says, the plain path (plan \u00a71 rule 1); the row says what the hand step is.\n- **Not yet in the product:** no product code, or the code is a scratch script outside the kit. The row gives the documented equivalent meanwhile (a cron line, a hand step).\n\n**What code holds and what stays practice.** Code holds nothing of the list's content: the CTO sets it from the tool map and the findings (DEC-1245 (1)). Code holds three things: the machine copy is read by `gov doctor`, which prints it and the release it describes; the first line of `gov retrieve` already prints the store and HEAD commits; a green row names the record that proves a run (the \"It must produce\" column), so a CTO reads the record and not the exit code (DEC-1240; I-11 passed its scoped runs and failed the full suite). The statuses and hand steps are practice.\n\n**Where it lives, so adopted repositories get it.** (a) `docs/releases/<v>/TOOL-STATUS.md`, for people, one for each release, written by the CTO before the owner builds the record (I did not check whether `gov release` hashes extra files in that folder). (b) `governance/kernel/tool-status.yaml` in the kit: a machine copy that `gov update` carries, because the project overlay is never overwritten by an update (IMPORTS spec line 72). It sits in the kernel folder, with no schema, because a patch release cannot add or remove a kit schema (DEC-1223 (7), P5; `LEAD-fixes-015b.md` F2); the schema comes with the next full release. (c) A `gov doctor` part `tool_status` prints it (W2-22, DAEO-xm6l, a fix of size S).\n\n**Rides.** The markdown for release 0.1.5 is a chore the CTO can commit now; products need it today. The machine copy and the doctor part ride Phase 0 and the first patch release after 0.1.5, with memory first (DEC-1245 (2)). Plan items 3-1, 3-2 and 4-1 turn rows green when they pass on the scratch repository.\n\n**How a tool moves.** Amber to green: the integration proves it on the scratch repository (DEC-1245 (1), the test of DEC-1240), and the next release's list says so; products gain it through `gov update`. Green to amber: not decided anywhere; the proposal is at once, in a patch release, when a finding marked \"blocks or loses work: yes\" (proposal 2) names a green tool.\n\n",
      "chunk_id": "0c122f4bbf91b38ddb6d7e0e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "1da53b821f10f7667af2803f",
      "sha256": "d17852af54e36c01f2d1c9455db2c9e7a9e7a729cab5c147648487f510f9becb",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 9,
      "end_line": 14,
      "text": "**Sources, by short name.** \"TOOL-MAP row n\" is `docs/emergency-2/integration/TOOL-MAP.md` \u00a71; \"RECORDS-MAP\" is `docs/emergency-2/integration/RECORDS-MAP.md`; \"I-n\" is `docs/emergency-2/integration/FINDINGS.md`; \"plan n-n\" is `docs/emergency-2/integration/INTEGRATION-PLAN.md`; \"HELD\" is `docs/emergency-2/integration/DECISIONS-HELD.md`; \"audit 4\" is `docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md`; \"A-n\" is audit 4's List A; \"GW\" is `docs/emergency-2/GOLDEN-WORKFLOW.md`; \"W1 to W16\" are GW's steps.\n\n**The answer in six lines.**\n\n1. **Tool list:** 52 tools in the 16 steps: **17 green, 17 amber, 18 not yet in the product**. It keeps every tool in the status the owner expected. It adds \"not yet\" rows beside four of them (memory's refresh and schedule, the kit's settings, adopt's verdict and imports, accept's two missing checks) and puts a rule on two greens (`gov update`, `gov doctor`).\n2. **Friction:** one log per repository in eight fixed columns, collected daily by a read-only pull, a stopper pushed at once, status brought back by the product's own session.\n",
      "chunk_id": "1da53b821f10f7667af2803f",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1245",
      "sha256": "25a1c24c3e921f20e215cdf1ff9d59b34958e8e8542663d714598fa0897de227",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2241,
      "end_line": 2241,
      "text": "  - (4) **Six proposals, one decisions page** in the form of the owner's last two: the tool status list (with each tool's reason); friction from the repositories (one findings log in a fixed form in each repository, collected by code into Gov OS's daily, a stopper pushing at once, each kind routed: a bug in a green tool, silent ones included, a fix in the next patch release; a workflow gap a change for the owner's yes; hand-step pain ordering which amber tool is proven first; a missing capability a Wave 3 candidate; status written back); old work under new releases (every ticket and record carries its release; closed work accepted as is; new rules apply to work created after them; a reopened ticket moves to the current forms; a rule that stops lost work or a fail-open applies at once; `gov update` never rewrites history; doctor shows earlier forms as a notice); decisions (a rubric for what is recorded as a decision and what is not; every decision names the paths, specs or steps it affects; one code holds is marked so and leaves agents' reading; how many are in force today); the rubrics register (every decided rubric with its decisions and enforcement field); data in specs (every spec and KPI line declares its data need: none, synthetic, imported or real, with its path and an imported source's licence class; the ready check red when the data is missing; the test designer builds on it).\n",
      "chunk_id": "405a244a76f3e09d7d4c39ea",
      "routes": [
        "lexical"
      ],
      "batch": 1,
      "entry": "DEC-1245",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1250",
        "DEC-1248"
      ],
      "in_force": true
    },
    {
      "id": "d18b35814d8279c0bc79105c",
      "sha256": "aca2c56c5a4eedcc09b68c2a74621d0a9fee6f3e419d8fe74b945dcf842954b6",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 123,
      "end_line": 149,
      "text": "    \"id\": \"TL-0\",\n    \"from\": \"Proposal 1 \u00b7 DEC-1245 (1)\",\n    \"title\": \"Approve the tool status list as drafted?\",\n    \"found\": [\n     \"52 tools in the 16 steps: 17 green, 17 amber, 18 not yet in the product.\",\n     \"Every green names where it was proven and the record that shows a run worked. Every amber has its hand step. Every \\\"not yet\\\" has its equivalent: a cron line or a hand step.\",\n     \"It keeps every tool in the status you expected. It adds \\\"not yet\\\" rows beside four of them and puts a rule on two greens. Cards TL-1 to TL-9 take each call you may want to change.\",\n     \"Nothing was run to prove a tool; each status rests on a record and the file says which.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Approve as drafted, with your answers to TL-1 to TL-9 applied\",\n      \"The CTO re-reads the list at each release until the enforcement field fills it.\",\n      1\n     ],\n     [\n      \"b\",\n      \"Approve with the changes in my note\",\n      \"The CTO applies them before a product uses the list.\"\n     ],\n     [\n      \"c\",\n      \"Not yet: products use only the tools you named\",\n      \"No hand steps are written; the greens beyond your list become amber.\"\n     ]\n    ],\n",
      "chunk_id": "d18b35814d8279c0bc79105c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "d235ff047184536b1cf42608",
      "sha256": "2462ec5c10fb37d98318a8017f23ce213f57ec136646256a8e7145b050bc6989",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 425,
      "end_line": 448,
      "text": "      \"A product's CTO cannot tell if it may use them.\"\n     ]\n    ],\n    \"reason\": \"They meet the same test as your six: real use, no open finding that loses work.\",\n    \"sources\": \"TOOL-MAP.md rows 2, 17, 45, 55, 72, 74, 76, 78, 80, 81; FINDINGS.md I-16.\",\n    \"stops\": \"Does not stop work.\"\n   },\n   {\n    \"id\": \"TL-10\",\n    \"from\": \"Proposal 1 \u00b7 where it ships\",\n    \"title\": \"Where does the list ship, so adopted repositories get it?\",\n    \"found\": [\n     \"DEC-1245 asks one list for each release.\",\n     \"The project overlay is never overwritten by <code>gov update</code>, so a machine copy must sit in the kernel folder to arrive.\",\n     \"A patch release cannot add or remove a kit schema (DEC-1223 (7), P5), so the machine copy ships without a schema until the next full release.\",\n     \"<code>gov doctor</code> already reads the install and the project; a <code>tool_status</code> part would print the list.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"<code>docs/releases/&lt;v&gt;/TOOL-STATUS.md</code> for people, <code>governance/kernel/tool-status.yaml</code> in the kit for machines, and a doctor part that prints it\",\n      \"Small code in doctor (W2-22, size S).\",\n      1\n     ],\n",
      "chunk_id": "d235ff047184536b1cf42608",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "0d945dec412d97a5484a3166",
      "sha256": "4fb9432ab510ebd9aadc9817db165ce53ddfbb243876b947fe5c403cbc80075d",
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "start_line": 42,
      "end_line": 52,
      "text": "## Output 1: `docs/emergency-2/integration/TOOL-MAP.md`\n1. **The map**, one row per tool, script, hook, cron line or schedule doing Gov OS's work, with exactly the golden\n   workflow \u00a75 columns: Step (W1-W16 or none) \u00b7 Tool (and path) \u00b7 Where it lives (product / outside) \u00b7 Trigger (automatic by\n   code, and when / called by an agent / run by the owner) \u00b7 On the path (yes / bypassed today, and by what) \u00b7 Receives /\n   hands on (form) \u00b7 How an agent knows it \u00b7 Gap and fix (the fix, its owning ticket found with\n   `grep -l \"^wbs_id: ...\" .tickets/*.md`, its place: 0.1.5 in flight / integration / later). Group rows by step.\n2. **The five rules checked**, each as a short list of violations: a step with no tool; a hand-off with no named form or no\n   code check; a tool an agent must call that no brief names with its exact command (and every skill or role file that\n   carries a tool catalogue instead); a tool outside the product with its disposition (absorb / replace / retire); a tool\n   serving no step or duplicating another.\n3. **How bad it is:** for each step W1-W16, on the path / partly / off; the share of steps on the path today (count and\n",
      "chunk_id": "0d945dec412d97a5484a3166",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2b0e7ea86605e28d07bf4797",
      "sha256": "f2c3cba26b617b500729e56bd2fc474fed07445c246c34e01bd956b671fd2099",
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "start_line": 105,
      "end_line": 108,
      "text": "| 70 | W12 | **no tool:** `gov queue --direct` (chores) | n/a | n/a | N | n/a | n/a | the draft names it; the queue's flags have no `--direct` (`queue/command.py:85-101`); A-16; spec question SQ-2; integration |\n| 71 | W12, W15 | `status_block.py` (scratch) | O | the CTO each owner report (DEC-1216) | Y | git and ticket state \u2192 the status block | memory note: run it on every report | `[replace]` by `gov status --digest` (A-32): chores, fixes, tickets landed, counts; integration |\n| **W13 Release** |||||||||\n| 72 | W13 | `gov release` full (`src/gov/release/command.py`, `cut.py`) | P | the owner types it | Y (0.1.5 is the owner's manual cut) | a clean tree and a new version \u2192 `docs/releases/<v>/`, tag, manifest | the owner | no acceptance gate (A-13); owner-only: the draft says the CTO cuts approved releases (SQ-4); 0.1.5 contract-015 wording |\n",
      "chunk_id": "2b0e7ea86605e28d07bf4797",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ae70871abf982bede034a3ac",
      "sha256": "4f179d891732381d8fca61fa11f512630711ed3be21139590e6f0da7bfd8dc12",
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "start_line": 210,
      "end_line": 213,
      "text": "- **The share of the map's rows on the path:** by a script over the \"On path\" column of the 102 rows: **Y 30 (29 %), partly 21 (21 %), N 50 (49 %), 1 not verified (row 35)**. The five \"no tool\" rows and the seven dead-file rows count as N. Leaving out the five \"no tool\" rows (97 tools and groups): Y 30 (31 %), Y or partly 51 (53 %). The Y rows are the memory build and retrieval (5 to 8), the automatic hooks and git hook (11, 55, 79, 80), the live scratch and cron tools (12, 16, 28, 43 to 46, 49, 57, 71, 81 to 84, 87), `gov accept` (54), the owner's release and update commands (72, 74 to 76) and `gov adopt` and `gov adapters` (1, 2); the product's refusals (`gov launch`, `gov queue`, `gov brief`, `gov dispatch`, `gov discover`, `gov impact`) are the P and N rows. Audit 4's own baseline for the Contract items was 21 % on the path; the step and row shares here are measured differently (tools in use, not Contract items), so the two are not comparable.\n\n---\n\n",
      "chunk_id": "ae70871abf982bede034a3ac",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "26a1d97cf2ec87bf376c9fdc",
      "sha256": "4d40d0cd3b4b4b058443cad4a15f2bef0d1f5fc3480112e05472324ce88a36bb",
      "path": "docs/emergency-2/integration/golden-workflow-decisions.html",
      "start_line": 85,
      "end_line": 99,
      "text": "td.n{text-align:right;font-variant-numeric:tabular-nums}\n</style>\n</head>\n<body>\n<header class=\"bar\"><div class=\"bar-in\">\n  <h1>Golden workflow decisions, 23 November</h1>\n  <div class=\"meter\"><div class=\"track\" aria-hidden=\"true\"><div class=\"fill\" id=\"fill\"></div></div><span id=\"count\">0 answered</span></div>\n</div></header>\n<main>\n<p class=\"lead\">The CTO checked your golden workflow against the code (16 corrections, 9 proposed changes) and mapped every tool. This page holds those, your rename, the gaps I found in the tool map, the discoveries you asked for in your comments, and the go-ahead. The 18 spec questions stay on their own page. Every card is selected with my recommendation; change anything, then copy the answer sheet at the end.</p>\n<section class=\"state\">\n  <h3>Where things stand</h3>\n  <ul>\n    <li><b>Steps on the path today:</b> 1 of 16 fully (memory build), 11 partly, 4 off (deciding, launching, fixes and chores, weekly hygiene): about 41 % counting partly as half.</li>\n    <li><b>The tool map:</b> 102 rows; 42 tools have a part outside the product (16 to replace, 11 to absorb, 15 to retire), plus about 255 dead scratch files.</li>\n",
      "chunk_id": "26a1d97cf2ec87bf376c9fdc",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "410777faaaf69a1fc5a9a03e",
      "sha256": "8cffbbdaa85c459bff02fee69c188682f21999a362feb908ab5635d1f929c3c6",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 40,
      "end_line": 47,
      "text": "### The list\n\nCounts: **17 green, 17 amber, 18 not yet** of 52. \"It must produce\" is for green rows only.\n\n| # | Step | Tool | Status | Why, and where it was proven or fails | It must produce (green) | Hand step, or the equivalent meanwhile |\n|---|---|---|---|---|---|---|\n| TL01 | W1 | `gov adopt` stages A0 to A10 and AS | **green** | Ran on EXAMIN (the W2-27 run) and on the six W2-81 repositories on 0.1.4: one has no A10 (analysis R11, the rust map with a path in two namespaces, A9 `FABRIC_INCOMPLETE`); the run's other reds are the verdict, findings and test set-up (R2 to R8). Open: A4 not built, A2 reads doctor's glob (RECORDS-MAP \u00a70 (2), (3), \u00a73.4). | one commit per stage, `governance/adoption/<stage>-*.md`, no `CHAIN_BROKEN` | After A3 run `gov check` (core-pathmap) and compare `git ls-files` with the map by eye; keep no root `*` namespace. |\n| TL02 | W1 | Adoption verdict stage (CAP-44.h) | not yet | On `e2/d1-verdict`, not merged (TOOL-MAP row 1; plan 5-8). | \u2014 | The A10 auditor's record is read by the CTO, who writes the verdict as the first line of the adoption note and tells the owner. |\n",
      "chunk_id": "410777faaaf69a1fc5a9a03e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "95ea03bac8452386ad10c6e7",
      "sha256": "a2f093c3b11dafdc1b4826e945f081a773381915e435ad9917b1542a479b6056",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 445,
      "end_line": 470,
      "text": "      \"<code>docs/releases/&lt;v&gt;/TOOL-STATUS.md</code> for people, <code>governance/kernel/tool-status.yaml</code> in the kit for machines, and a doctor part that prints it\",\n      \"Small code in doctor (W2-22, size S).\",\n      1\n     ],\n     [\n      \"b\",\n      \"The markdown only\",\n      \"A product's agents never see it after adoption.\"\n     ],\n     [\n      \"c\",\n      \"One list in the head of CLAUDE.md\",\n      \"The head grows each release.\"\n     ]\n    ],\n    \"reason\": \"It reaches every repository by the road fixes already use.\",\n    \"sources\": \"DEC-1223 (7); LEAD-fixes-015b.md F2; IMPORTS-ADOPTION-SPEC.md line 72; PRACTICE-FIRST-PROPOSALS.md \u00a71.\",\n    \"stops\": \"Does not stop work.\"\n   },\n   {\n    \"id\": \"TL-11\",\n    \"from\": \"Proposal 1 \u00b7 how a tool moves\",\n    \"title\": \"How does a tool move between statuses?\",\n    \"found\": [\n     \"DEC-1245 (1): amber to green only once the integration has proven it on the scratch repository; products gain it through <code>gov update</code>.\",\n     \"Nothing says how a green tool falls back. Two real cases: <code>gov update</code> leaving doctor red in 6 of 6 repositories, and the memory refresh failing with no retry.\",\n",
      "chunk_id": "95ea03bac8452386ad10c6e7",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "1883a5caf8cf11a1af8d6f5d",
      "sha256": "38d3e4451630e7724a87a5645fb73c2bfd2c2ccaf6ff0b54c60717c956622543",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 403,
      "end_line": 428,
      "text": "    \"from\": \"Proposal 1 \u00b7 TL04, TL16, TL27, TL33, TL40, TL43 to TL46\",\n    \"title\": \"Nine greens you did not name: keep them?\",\n    \"found\": [\n     \"Nine more tools qualify by real use: <code>gov backup</code> (hourly), <code>gov checkpoint</code> with its hooks, <code>gov msg</code>, <code>gov install</code> and <code>gov release</code> with the re-pin (0.1.0 to 0.1.5), the helper-return hook, the <code>gov resources</code> gate, <code>gov decisions in-force</code> and <code>gov adapters</code>.\",\n     \"Each carries its gap in its row: a 41-hour backup gap nothing noticed; a message to a running <code>claude -p</code> lead is never read; I-16 for adapters.\",\n     \"Without them the hand work grows for tools that work.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Green, each with its note\",\n      \"Nine more rows a CTO reads.\",\n      1\n     ],\n     [\n      \"b\",\n      \"Only your named list green; these nine amber\",\n      \"Hand work for tools that work.\"\n     ],\n     [\n      \"c\",\n      \"Leave them off the list\",\n      \"A product's CTO cannot tell if it may use them.\"\n     ]\n    ],\n    \"reason\": \"They meet the same test as your six: real use, no open finding that loses work.\",\n",
      "chunk_id": "1883a5caf8cf11a1af8d6f5d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "835e36f8d2cf0329b700f94d",
      "sha256": "f495b498738a7a77038bd26f370efc4bf022b9a76aea282caf14c791f7d62b41",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 86,
      "end_line": 88,
      "text": "| TL41 | W13 | `gov release --patch` | amber | Switched on since the 0.1.5 cut (`patch_releases: on`, `a48c6e3ed`), not yet used for a real cut; gate G2 reads a nightly record while the nightly is off (TOOL-MAP row 73). | \u2014 | The CTO cuts approved content by it from 0.1.6; the first cut is its proof. |\n| TL42 | W14 | `gov update` | **green** | First updates found two bugs, both fixed for 0.1.5 (merge `2cadc0cf8`): `context_watch.py` twice in EXAMIN (report 28, F4) and `gov doctor` red after the update in 6 of 6 W2-81 repositories (22 November, F6). Not re-run on a real repository yet. | `governance/updates/<B>.json`, and `gov doctor` no worse than before | After each update run `gov doctor`; if it is worse, `gov update --rollback` (one revert commit) and log a finding. |\n| TL43 | W14 | `gov install` and the pin | **green** | Used in every re-pin; hash-verified (TOOL-MAP row 76). | a pinned environment, hash checked | None. |\n",
      "chunk_id": "835e36f8d2cf0329b700f94d",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "03ed61643ae60da274a9692d",
      "sha256": "7a5ceda09eb4de9dfb4b21a6727bc7111af46f91e4bf282707b0af972dd694cc",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 377,
      "end_line": 405,
      "text": "     \"The hand steps are in the rows; the CTO starts leads by hand within the machine's limit.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Amber, with the rule: never run <code>gov impact</code> on a record id\",\n      \"Impact is traced by <code>gov retrieve</code> and <code>grep</code>.\",\n      1\n     ],\n     [\n      \"b\",\n      \"<code>gov impact</code> as \\\"not yet in the product\\\"\",\n      \"It fails on its main use; this hides a built tool.\"\n     ],\n     [\n      \"c\",\n      \"Green for <code>gov brief</code>'s ready check alone\",\n      \"A prints-only use; its other parts stay amber.\"\n     ]\n    ],\n    \"reason\": \"Amber is what you expected, and the one rule stops the one use that hangs.\",\n    \"sources\": \"TOOL-MAP.md rows 22, 36, 37, 42, 43; FINDINGS.md I-5; plan 1-8.\",\n    \"stops\": \"Does not stop work.\"\n   },\n   {\n    \"id\": \"TL-9\",\n    \"from\": \"Proposal 1 \u00b7 TL04, TL16, TL27, TL33, TL40, TL43 to TL46\",\n    \"title\": \"Nine greens you did not name: keep them?\",\n    \"found\": [\n",
      "chunk_id": "03ed61643ae60da274a9692d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "8e8327fc9c4e4296d5880068",
      "sha256": "0aad6929a40464f4d5938dd7018a2726d9d8cba5b43c414ca0372eb45f46bf5c",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 106,
      "end_line": 110,
      "text": "| Green: `gov doctor` | `path_map` passes with unmapped files on a map with a root `*` (RECORDS-MAP \u00a70 (2)); adopted maps have none | Green with two read-rules (TL51) |\n| Green: `gov accept` | 66 of 188 old folders fail the map parse; new ones parse (RECORDS-MAP \u00a71.2) | Green (TL32); the two missing checks are **not yet** (TL30, TL31) |\n| Green: the kit's settings | The two denies, hooks and connectors key are in the kit. `defaultMode` and the model hook are not (TOOL-MAP rows 3, 57) | Split: TL05 green, TL06 **not yet** |\n| Amber: the landing, `gov launch`, `gov brief`, `gov impact`, the dispatcher | Confirmed (TL35, TL25, TL24, TL18, TL26). `gov impact` must not be run on a record id (I-5) | Amber, with that rule on TL18 |\n\n",
      "chunk_id": "8e8327fc9c4e4296d5880068",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "61a18285594d43f06d7955aa",
      "sha256": "a4ad639be00ad4076523520c255b6ba78fa7647706248b029fff711a89408d39",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 99,
      "end_line": 110,
      "text": "### Where the evidence differs from the owner's expected list\n\n| The owner expected | Evidence | The list says |\n|---|---|---|\n| Green: memory and its measure | Build, retrieve and the measure are used daily (TL08, TL10, TL14). The refresh hook is untracked and fires only for `w2/integrate`; a failed refresh was not retried (I-9); the boot start and the weekly measure are cron lines to scratch scripts (TOOL-MAP rows 11, 12, 15) | Green for TL08, TL10, TL14; **not yet** for TL12, TL13, TL15, each with its cron or hand equivalent |\n| Green: `gov adopt` | Ran on EXAMIN and six W2-81 repositories; the verdict stage and the imports step are not at HEAD; A4 is not built (TOOL-MAP row 1; RECORDS-MAP \u00a73.4) | Green for A0 to A10 and AS (TL01); **not yet** for the verdict (TL02) and imports (TL03) |\n| Green: `gov update` | Two real bugs (hook twice, doctor red 6 of 6), both fixed for 0.1.5, not re-run on a real repository (`LEAD-fixes-015b.md` F4, F6) | Green with the rule \"doctor after, roll back if worse\" (TL42) |\n| Green: `gov doctor` | `path_map` passes with unmapped files on a map with a root `*` (RECORDS-MAP \u00a70 (2)); adopted maps have none | Green with two read-rules (TL51) |\n| Green: `gov accept` | 66 of 188 old folders fail the map parse; new ones parse (RECORDS-MAP \u00a71.2) | Green (TL32); the two missing checks are **not yet** (TL30, TL31) |\n| Green: the kit's settings | The two denies, hooks and connectors key are in the kit. `defaultMode` and the model hook are not (TOOL-MAP rows 3, 57) | Split: TL05 green, TL06 **not yet** |\n| Amber: the landing, `gov launch`, `gov brief`, `gov impact`, the dispatcher | Confirmed (TL35, TL25, TL24, TL18, TL26). `gov impact` must not be run on a record id (I-5) | Amber, with that rule on TL18 |\n\n",
      "chunk_id": "61a18285594d43f06d7955aa",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "c441b1ddc9f3c25e7ce9e6f3",
      "sha256": "352f6d62fc8885cd014c811a683faae0e72523dad7f1490516295aff80d68877",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 84,
      "end_line": 86,
      "text": "| TL39 | W12 | `gov land --direct` for chores that touch code | not yet | Not built (A-16; TOOL-MAP row 70). | \u2014 | As TL38; list the chore in the digest by hand. |\n| TL40 | W13 | `gov release` (full) and the re-pin | **green** | Cut 0.1.0 to 0.1.5, each re-pinned with self-rollback (`docs/releases/`; TOOL-MAP rows 72, 74). | `docs/releases/<v>/manifest.json` verified, a tag, `~/.local/bin/gov` re-linked | None. 0.1.5 was the owner's last manual cut; from 0.1.6 the CTO cuts content the owner approved, once the release acceptance passes (DEC-1235 (2)). |\n| TL41 | W13 | `gov release --patch` | amber | Switched on since the 0.1.5 cut (`patch_releases: on`, `a48c6e3ed`), not yet used for a real cut; gate G2 reads a nightly record while the nightly is off (TOOL-MAP row 73). | \u2014 | The CTO cuts approved content by it from 0.1.6; the first cut is its proof. |\n",
      "chunk_id": "c441b1ddc9f3c25e7ce9e6f3",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "e54c54c57c59c086e3d3400a",
      "sha256": "d5eecf1157dca897817d6245b1117063e5436c5b1011fbefbd48610da96dda3a",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 94,
      "end_line": 98,
      "text": "| TL49 | W15 | Usage and context figures, pushes at 95 and 99 % | not yet | Scratch `usage_log.sh` and `cto_watch.sh` (TOOL-MAP rows 82, 83; plan 3-10). | \u2014 | The plan is one figure for the machine and Gov OS's CTO's watcher already sees it; a product's CTO adds nothing. |\n| TL50 | W15 | `gov status` and the status block | amber | `gov status` never refuses; the status block is the scratch `status_block.py` (TOOL-MAP rows 71, 86; plan 3-12). | \u2014 | End each report with the block by hand: tickets landed, chores, fixes and counts from `git log` and `.tickets/`, never copied forward (DEC-1216 (3)). |\n| TL51 | W16 | `gov doctor` | **green** | Ran on the six W2-81 repositories and in every update rehearsal. On a map with a root `*` (Gov OS's) `path_map` passes with unmapped files (RECORDS-MAP \u00a70 (2)); EXAMIN agrees under every matcher (\u00a73.3). `path_compliance` fails on EXAMIN for moved-path text (F-009). | one healthy or drift line for each part | Read `path_map` as proof only for a map with no root `*`; read `path_compliance` as a notice. |\n| TL52 | W16 | `gov telemetry` | amber | Typed; no schedule (TOOL-MAP row 90). | \u2014 | Nothing depends on it. |\n\n",
      "chunk_id": "e54c54c57c59c086e3d3400a",
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
    "duplicates": 19,
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
      "chunk_id": "0c122f4bbf91b38ddb6d7e0e",
      "parent_id": "59a266dedbbfd5dd62707337",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 22,
      "end_line": 39
    },
    {
      "chunk_id": "61a18285594d43f06d7955aa",
      "parent_id": "9d1730d5209eec1537b37906",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 99,
      "end_line": 110
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "24be32b093ef20a16d661a09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "14433477ff460893d27813cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "f6edf4e73955a98bed8963d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "6fa8ebc1ac94c730341711fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "402556a41920feda9b183042",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "69bd425a9112b2a0c300cf99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "3a7ae39b8f5eccb7d8560afd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "d4586f06edf1aca9ed76c4cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "7f0f33b753cb7c4a3feb94b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "04e8e0be9630f6b545f53cec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "0083bde357340f2b7bfedf7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "52b0be7a4a38226be6c2c349",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/golden-workflow-decisions.html",
      "chunk_id": "520e87f83ddedb1409c5316b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "578546c5692ec12f0ef4ab65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "80a9b8fbaa860b2603e2513c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-25.md",
      "chunk_id": "e8cd59a26f5eef24199e60b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "37dce3379aa687b04def6f81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "82497daab714537dccd10313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1bf642f128c3a3738d7c2db2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e3f050f7c7f6d3f33560cf2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cc22f8ec310fe1d07afc7ff9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md",
      "chunk_id": "2c5a3467886ff327ef2ab871",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "8a6e46f4154e615748350033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "09289cf4ccbc36b954e8e3b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "abc74248c32273f1c022bc7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "08c3a6ab1bb6dbed0868b515",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "4156e3419fcc7a1eb1abcd9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "d2db95c4ee512c8d137877d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "4f06c3572295fd92f13ccb78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "a7b70f70efb8a59e0958c326",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "6f579211d49b6c69388df820",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "chunk_id": "2b7a2ddbf3183207da8b2215",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "989c6afbd3bdfaafd5ed6a12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md",
      "chunk_id": "6164e98504ae1743db5fba96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "c767fd7a54cca86055e4d7d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "91c433d34ab0f87811570d31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-3-mcp-tools.md",
      "chunk_id": "80547fbd2666d0451f6c79ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cf99cd773ecf6cf6e1ed0830",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "ce6c2cf73fde0d65573b955b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "77dad34ce6792d9ee0b7b6f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ae204bbcdb9b8211a1ef9307",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "9ca3537a229cc4c6e63fe51d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "71ccde76a15fe19a15dbeae4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e753b8925f988bef182f0415",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "4d20cbbc5c2c33d3a3c170b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "d6224cdda5084295e978a7e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "e8e76a102080e6fe6f43bd97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "039bc5163540c789d83cc017",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/doctor/command.py",
      "chunk_id": "a90030562ff3759953cc4bef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "64aed06850053d40c7af7608",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "f57558a8221a57b1560a4a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "13767eaf6bb5e3777c776721",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "3ac9b63444a1aae7ee9c0286",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "e38c6001a0dc049fe49c7de7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "60f6798d6fca501b58ac067e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "63c42cd5ebdddc0c8563fa80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "145cb69295360125965d53c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "d3f0ae5652bd22722e1509c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "bd0a58b8efa19483d963abcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-neam.md",
      "chunk_id": "1afbb8b7865cb2f7afff8365",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4e433d38c9370738dec705d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "07aa9bad6c4ee88bf4280c50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "dd204a753774ff6873947d49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "01d926ac86145ef28ec8bdf3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "79b7aee9706b1ef29de0931e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "34e2e90e5af054ecb4ac1ea8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "2a87b2966fec1d55b0300856",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "8fa30bcf85d093017c3a27ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9b0ebfe72ee53d6ed08dd309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6a9dee6e838a6b4ead5fa878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "d2f71866790f92585fe8a45f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "19f49b00a88a8f0fb42c62e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "1f6f49b3af5ec845dab090b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "63ba33081f31cfb82cce61bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "213f0c02b7aaa40127bbd43f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-TOOLS-REVIEW-1.md",
      "chunk_id": "d3ec3c89d3e49a663724dfdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "chunk_id": "f1cd1e58020b6502d968e8c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "83850893cc262225a7df4a02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md",
      "chunk_id": "e4f49376f2c7f9b696515c48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "17ed5559660c8d8f5d9146d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "chunk_id": "3afec7806cf2fc33ab0f5d7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "chunk_id": "7395b43f17bd9a3f7897b54d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "537238c2d17635417a8ff53a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "630df801022885cd686c79b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "b23ede756d58d608f60156b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "7cc214def2d0f3e757ac171b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "b408ef35122fa0433489e9de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "80f904a7d94538ff9d993143",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "2163c270c5b9c19522109704",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "7bd84ccfc1d3101d874e4bda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "61698711cb6484f461cd1ece",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "fedb0af1503ada3a665b80b3",
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
      "used": 5983
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwyMjM4LDIyMzgsIjZhYTk1NDJkZDQzMTY2MWVlNjk3ZmZmMSJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMjI0MSwyMjQxLCI0MDVhMjQ0YTc2ZjNlMDlkN2Q0YzM5ZWEiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL1JFU0VBUkNILXN0ZXAxLXRvb2wtbWFwLm1kIiw0Miw1MiwiMGQ5NDVkZWM0MTJkOTdhNTQ4NGEzMTY2Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1BSQUNUSUNFLUZJUlNULURFQ0lTSU9OUy0yMDI2LTExLTI0Lmh0bWwiLDEyMywxNDksImQxOGIzNTgxNGQ4Mjc5YzBiYzc5MTA1YyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9QUkFDVElDRS1GSVJTVC1ERUNJU0lPTlMtMjAyNi0xMS0yNC5odG1sIiwzNzcsNDA1LCIwM2VkNjE2NDNhZTYwZGEyNzRhOTY5MmQiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUFJBQ1RJQ0UtRklSU1QtREVDSVNJT05TLTIwMjYtMTEtMjQuaHRtbCIsNDAzLDQyOCwiMTg4M2E1Y2FmOGNmMTFhMWFmOGQ2ZjVkIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1BSQUNUSUNFLUZJUlNULURFQ0lTSU9OUy0yMDI2LTExLTI0Lmh0bWwiLDQyNSw0NDgsImQyMzVmZjA0NzE4NDUzNmIxY2Y0MjYwOCJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9QUkFDVElDRS1GSVJTVC1ERUNJU0lPTlMtMjAyNi0xMS0yNC5odG1sIiw0NDUsNDcwLCI5NWVhMDNiYWM4NDUyMzg2YWQxMGM2ZTciXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vVE9PTC1NQVAubWQiLDEwNSwxMDgsIjJiMGU3ZWE4NjYwNWUyOGQwN2JmNDc5NyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9UT09MLU1BUC5tZCIsMjEwLDIxMywiYWU3MDg3MWFiZjk4MmJlZGUwMzRhM2FjIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL2dvbGRlbi13b3JrZmxvdy1kZWNpc2lvbnMuaHRtbCIsODUsOTksIjI2YTFkOTdjZjJlYzg3YmYzNzZjOWZkYyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvUFJBQ1RJQ0UtRklSU1QtUFJPUE9TQUxTLm1kIiw5LDE0LCIxZGE1M2I4MjFmMTBmNzY2N2FmMjgwM2YiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL1BSQUNUSUNFLUZJUlNULVBST1BPU0FMUy5tZCIsMzYsMzksImFhYjQ3ZDRhMzA1YTI2ZTdmNDI2NGMyNiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvUFJBQ1RJQ0UtRklSU1QtUFJPUE9TQUxTLm1kIiw0MCw0NywiNDEwNzc3ZmFhYWY2OWExZmM1YTlhMDNlIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9QUkFDVElDRS1GSVJTVC1QUk9QT1NBTFMubWQiLDg0LDg2LCJjNDQxYjFkZGM5ZjNjMjVlN2NlOWU2ZjMiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL1BSQUNUSUNFLUZJUlNULVBST1BPU0FMUy5tZCIsODYsODgsIjgzNWUzNmY4ZDJjZjAzMjliNzAwZjk0ZCJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvUFJBQ1RJQ0UtRklSU1QtUFJPUE9TQUxTLm1kIiw5NCw5OCwiZTU0YzU0YzU3YzU5YzA4NmUzZDM0MDBhIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9QUkFDVElDRS1GSVJTVC1QUk9QT1NBTFMubWQiLDEwNiwxMTAsIjhlODMyN2ZjOWM0ZTQyOTZkNTg4MDA2OCJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYSIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiMjM3MGVmNDY4ZjQ5YjJhOCIsIm8iOlswLDEsNywyMSwyLDI0LDMxLDEzLDI1LDMwLDUsNCw2LDMsMjYsOSw4LDE2LDI3LDEwLDE5LDE0LDE1LDE3LDExLDEyLDIzLDI5LDE4LDI4LDMzLDIwLDM4LDIyLDM5LDMyLDM2LDM0LDM3LDM1XX0sInEiOiJ0b29sIHN0YXR1cyBsaXN0IGdyZWVuIGFtYmVyIG5vdCB5ZXQgcGVyIHJlbGVhc2UsIHRvb2xzIHByb3ZlbiBpbiByZWFsIHVzZSwgVE9PTC1NQVAgcm93cywgZmluZGluZ3MgYWdhaW5zdCBncmVlbiB0b29scyIsInIiOjAsInMiOiI1ZWIyOWU3ZmY1NjBhMjdhMDBkNWU5MWQzNmQzZjM2NDhmMGU4YzBhIiwidCI6bnVsbCwieCI6WyI1OWEyNjZkZWRiYmZkNWRkNjI3MDczMzciLCI5ZDE3MzBkNTIwOWVlYzE1MzdiMzc5MDYiXX0=",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "tool status list green amber not yet per release, tools proven in real use, TOOL-MAP rows, findings against green tools",
      "tool status list green amber not yet per release tools proven real use TOOL-MAP rows findings against green tools"
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
        "chunk_id": "aab47d4a305a26e7f4264c26",
        "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
        "start_line": 36,
        "end_line": 39
      }
    ]
  }
}
