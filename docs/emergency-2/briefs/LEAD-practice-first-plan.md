# Lead brief: practice-first-plan, DEC-1252's 31 approved recommendations planned into the integration plan's streams (a planning job for the CTO; no code)

You are a planning lead (Sonnet, medium; the orchestrator's planning profile), started by the Gov OS CTO on 2026-11-26. **Read
`docs/emergency-2/briefs/LEAD-COMMON.md` first** (memory first, never cut a result, never open a sets root). Decide, never ask (I-10).
Every `gov retrieve` takes `--root /home/usain/gov-os-worktrees/W2-00-store`. You write one document; you change no code, no ticket,
no plan file.

## Why
The owner approved every recommendation on the practice-first page, all 31 cards (DEC-1252, by DEC-1251 D-06 (b)): the tool status
list, the findings log in each repository with `gov findings collect` and `gov findings sync` (a new feature, approved), every record
carrying its release, the decision rubric with `Affects:` and `Enforced-by:` and one Sonnet research pass classing the 162 older
decisions, the rubrics register (`docs/RUBRICS.md` and its kit copy), data declared in specs. The CTO's handover (next action 7) says:
plan them into the integration plan's streams.

## Read
`docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md` (the proposals, whole); the cards on
`docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html` (their ids TL-0..TL-11, FR-0..FR-3, OW-0..OW-3, DE-0..DE-2,
RG-0..RG-2, DS-0..DS-4 and each recommended option: FR-2 is option (b), every other (a)); DEC-1245, DEC-1251, DEC-1252 in
`docs/DECISION_REGISTER.md`; `docs/emergency-2/integration/INTEGRATION-PLAN.md` §1 (scope and rules), §2's phase headings and the
items each card touches, §4 (streams); `docs/emergency-2/integration/TOOL-MAP.md` for the tool status list; FINDINGS.md's form.

## What: write `docs/emergency-2/integration/PRACTICE-FIRST-PLAN.md`
- One row per card (31): the card id; what it asks (one line); its kind by the rubric (feature: only `gov findings collect`/`sync`,
  which the owner approved as a feature; otherwise a fix under an owning ticket, found with `grep -l "^wbs_id: W.-N" .tickets/*.md`,
  or a chore); the owning ticket; size (XS/S/M/L, the plan's scale); the plan item it joins or a new item id in the phase it belongs to;
  what it waits on; a verify that names what the step must produce (the plan's rule 5); which repositories it reaches (Gov OS, the
  kit through `gov update`, EXAMIN, ASMO OS).
- Then the order: which cards are chores the CTO can commit today (records, the tool status list for 0.1.7 and 0.1.8, `docs/RUBRICS.md`),
  which ride the next releases, and the one research pass (the 162 decisions) as a job form (question, scope, evidence, output path).
- Then the conflicts: any card that contradicts the plan, the golden workflow or a later decision, cited, with your recommendation.
  Do not resolve them yourself.

## Green
Every one of the 31 ids appears exactly once in the table (a count printed at the end); every owning ticket named exists; every plan
item named exists in the plan or is marked new. Commit the one file on branch `e2/practice-first-plan` (worktree
`/home/usain/gov-os-worktrees/E2-practice-first-plan`, from `w2/integrate`) with `Role: orchestrator`, `Task: chore`, `Class: C`.

## Return
Branch and head; the count by kind and by phase; the chores for today; the conflicts; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: decisions, history and plans; uncut)
store: a455b00cf073 (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "a455b00cf0736d7a37d9e585e6430c455ef4fe60",
    "head": "a455b00cf0736d7a37d9e585e6430c455ef4fe60",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DEC-1245",
      "sha256": "25a1c24c3e921f20e215cdf1ff9d59b34958e8e8542663d714598fa0897de227",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2241,
      "end_line": 2241,
      "text": "  - (4) **Six proposals, one decisions page** in the form of the owner's last two: the tool status list (with each tool's reason); friction from the repositories (one findings log in a fixed form in each repository, collected by code into Gov OS's daily, a stopper pushing at once, each kind routed: a bug in a green tool, silent ones included, a fix in the next patch release; a workflow gap a change for the owner's yes; hand-step pain ordering which amber tool is proven first; a missing capability a Wave 3 candidate; status written back); old work under new releases (every ticket and record carries its release; closed work accepted as is; new rules apply to work created after them; a reopened ticket moves to the current forms; a rule that stops lost work or a fail-open applies at once; `gov update` never rewrites history; doctor shows earlier forms as a notice); decisions (a rubric for what is recorded as a decision and what is not; every decision names the paths, specs or steps it affects; one code holds is marked so and leaves agents' reading; how many are in force today); the rubrics register (every decided rubric with its decisions and enforcement field); data in specs (every spec and KPI line declares its data need: none, synthetic, imported or real, with its path and an imported source's licence class; the ready check red when the data is missing; the test designer builds on it).\n",
      "chunk_id": "405a244a76f3e09d7d4c39ea",
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
      "id": "DEC-1252",
      "sha256": "b3f94e430bfdc3e5d4cff58f7a309fe8087f37ab0b0842aa816496b38d336ada",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2303,
      "end_line": 2308,
      "text": "### DEC-1252 \u2014 The practice-first decisions (B-2026-11-24-practice, 31 cards): every recommendation, by the owner's D-06 (b)\n- **Status:** ACCEPTED (owner, 2026-11-25T21:55:15Z, card D-06 (b) of B-2026-11-25-cto: \"every recommendation on the practice-first page, all 31 cards, including gov findings collect and the one pass classing the 162 older decisions\"; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (page B-2026-11-25-cto, D-06)`; standing) \u00b7 **Under:** DEC-1245 (4), DEC-1251\n- **Decision** (each card's findings, options and costs are on `docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html`; the proposals are `docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md`): **TL-0 (a)**; **TL-1 (a)**; **TL-2 (a)**; **TL-3 (a)**; **TL-4 (a)**; **TL-5 (a)**; **TL-6 (a)**; **TL-7 (a)**; **TL-8 (a)**; **TL-9 (a)**; **TL-10 (a)**; **TL-11 (a)**; **FR-0 (a)**; **FR-1 (a)**; **FR-2 (b)**; **FR-3 (a)**; **OW-0 (a)**; **OW-1 (a)**; **OW-2 (a)**; **OW-3 (a)**; **DE-0 (a)**; **DE-1 (a)**; **DE-2 (a)**; **RG-0 (a)**; **RG-1 (a)**; **RG-2 (a)**; **DS-0 (a)**; **DS-1 (a)**; **DS-2 (a)**; **DS-3 (a)**; **DS-4 (a)**. In short: the tool status list as drafted, with its rules and where it ships; the findings log in each repository with `gov findings collect` and `gov findings sync` (a new feature, approved), a stopper pushed at once; every record carries its release, closed work never re-checked, a rule marked `Applies: at once` by the CTO; the decision rubric with `Affects:` and `Enforced-by:`, and one Sonnet research pass classing the 162 older decisions in HELD's key; the rubrics register (`docs/RUBRICS.md` and its kit copy, binding rows only); data declared in the spec's test-data table with `serves` and `path`, `real` rows naming an owner decision, an unlicensed import red for test data, old specs a notice.\n- **Basis:** the owner's answer of 2026-11-25 (D-06 (b)).\n- **Governing sources:** docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html; docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md; DEC-1245; DEC-1251.\n\n",
      "chunk_id": "1b3bfd607b71dc1f3a4fe894",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-1252",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "c3b11fb7a341c76b9c2d4f82",
      "sha256": "3e57159aa99241bdf51a2913c8c6ca48d9d535d14ef7de52096fe1242d1ff68f",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 14,
      "end_line": 21,
      "text": "2. **Friction:** one log per repository in eight fixed columns, collected daily by a read-only pull, a stopper pushed at once, status brought back by the product's own session.\n3. **Old work:** every record carries `release:`; closed work is never re-checked; new rules read the field, as `ready.new_since` already does for one date.\n4. **Decisions:** 190 are in force. Of the 30 that HELD classed (DEC-1209 to DEC-1238): **1 held by code on the path, 6 spent, 3 partial, 20 text or not built**; 153 older and 7 newer are not classed. At least **7** would leave agents' reading now, at most about **18** from what is classed today.\n5. **Rubrics:** 20 rubrics found, each with its decisions and its enforcement; one file, `docs/RUBRICS.md`, and a kit copy.\n6. **Data in specs:** the spec form already has a `## Test data` table that `check_spec.py` reads; the proposal adds kinds `none` and `real`, a `path`, the KPI lines served, and a ready check that goes red when the data is not there.\n\n---\n\n",
      "chunk_id": "c3b11fb7a341c76b9c2d4f82",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4ae918cc5dd4f33e8c8fc3de",
      "sha256": "2c82d52bdc73d94efe57abf4f03da7aa266a39b3c9fe91d2af3266d4747ff6c0",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 5,
      "end_line": 8,
      "text": "**What the owner asked for.** DEC-1245 (4): six proposals on one decisions page, in the form of his last two: the tool status list, friction from the repositories, old work under new releases, decisions, the rubrics register, data in specs. DEC-1245 (1): \"from now, every repository works by the golden workflow v2 as written practice\"; products use only the tools proven in real use.\n\n**How it was made.** Memory first: `gov retrieve` ran three times (the store was at `0bd2945b04fe`, one stale path: the register); each bundle was read whole and one search in my own words followed. Then the files named in each source line. `gov decisions in-force` was run for the count (190 lines). Nothing was run to prove a tool; every status below rests on records that exist, and says which. A statement I could not check is marked \"not checked\".\n\n",
      "chunk_id": "4ae918cc5dd4f33e8c8fc3de",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e8e76a102080e6fe6f43bd97",
      "sha256": "8a81bce4d4f708fc76a4da569f705deefc8292a12e8176763b4e2b1f027b1bbf",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 499,
      "end_line": 519,
      "text": "  \"intro\": \"One findings log in each repository, collected by code, a stopper pushed at once, each kind routed.\",\n  \"qs\": [\n   {\n    \"id\": \"FR-0\",\n    \"from\": \"Proposal 2 \u00b7 DEC-1245 (4)\",\n    \"title\": \"Approve the findings log and its routing?\",\n    \"found\": [\n     \"One log in each repository: <code>governance/project/findings/FINDINGS.md</code>, in a namespace the kit's path map already holds, never overwritten by an update.\",\n     \"Eight columns: id, what happened, evidence, Gov OS release, step, blocks or loses work (yes or no), kind, status. Kinds: bug in a green tool (silent ones included), workflow gap, hand-step pain, missing capability.\",\n     \"Routing: a bug is a fix under its owning ticket in the next patch release; a workflow gap is a change for your yes; hand-step pain orders which amber tool is proven first; a missing capability is a Wave 3 candidate.\",\n     \"Repository CTOs judge a tool by the record it produces, not its exit code.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Approve\",\n      \"A new read-only command, <code>gov findings collect</code>, is a feature for your yes (S to M, about $2.50 to $6.60).\",\n      1\n     ],\n     [\n      \"b\",\n",
      "chunk_id": "e8e76a102080e6fe6f43bd97",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "0e2b1cfe5a433f18cad3648c",
      "sha256": "0c451679b2e768509a440525fa4ffa91eff5b6e4023d59318618c7b30da283cc",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 768,
      "end_line": 791,
      "text": "     \"Recorded: a standing rule or practice, a choice whose reason matters later, an exception, a measurement period, a rubric. Not recorded: a spec change (it is a change to the spec file; git keeps its history), a one-off instruction, a status report.\",\n     \"Every new decision names what it affects in an <code>Affects:</code> line: paths, specs or steps W1 to W16, or <code>none</code>.\",\n     \"The impact trace (W6) would read it. Today the graph has <code>Under</code>, <code>Changes</code> and <code>Supersedes</code> links only.\",\n     \"192 decisions are in force today (DEC-1246 and DEC-1247 added since the proposal was drafted).\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Approve both\",\n      \"One more line on each decision; the basis check requires it from plan 5-4.\",\n      1\n     ],\n     [\n      \"b\",\n      \"Approve with the changes in my note\",\n      \"The CTO applies them first.\"\n     ],\n     [\n      \"c\",\n      \"The rubric only, no <code>Affects:</code> line\",\n      \"The impact trace stays blind to a decision's paths and steps.\"\n     ]\n    ],\n    \"reason\": \"The rubric is in your words, and the line gives W6 the input it lacks.\",\n",
      "chunk_id": "0e2b1cfe5a433f18cad3648c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "a61150760204d2cf9787de87",
      "sha256": "30d98d2b707828c808cbc94ed890e800de5023b73869385d7328cd1faa952bcb",
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "start_line": 301,
      "end_line": 326,
      "text": "    \"from\": \"DEC-1245 (4) \u00b7 the practice-first page\",\n    \"title\": \"The practice-first decisions page: 31 cards, unanswered since 24 Nov\",\n    \"found\": [\n     \"The six proposals (tool status list, friction from the repositories, old work under new releases, decisions, the rubrics register, data in specs) are on their own page, published 24 Nov: <a href=\\\"https://claude.ai/artifact/6EaYA5GiQ561qpTf7xDHRu\\\">https://claude.ai/artifact/6EaYA5GiQ561qpTf7xDHRu</a>.\",\n     \"None of them stops work; several (the findings log, the tool status list) shape how EXAMIN and ASMO OS work now.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"I answer on that page\",\n      \"Nothing here.\"\n     ],\n     [\n      \"b\",\n      \"Take every recommendation on that page\",\n      \"The CTO applies all 31 as recommended; your notes there still count.\",\n      1\n     ]\n    ],\n    \"reason\": \"Each recommendation stands on its own card there, so (b) hides no choice.\",\n    \"sources\": \"PRACTICE-FIRST-DECISIONS-2026-11-24.html; PRACTICE-FIRST-PROPOSALS.md.\",\n    \"stops\": \"Does not stop work.\"\n   },\n   {\n    \"id\": \"D-07\",\n    \"from\": \"EXAMIN \u00b7 its assessment and Contract draft\",\n",
      "chunk_id": "a61150760204d2cf9787de87",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "893d71547ea74432739ca5ac",
      "sha256": "37c1c2bada0bf12f807f7f46fad2bc475eef9c13ad7026411dd7a9531b315add",
      "path": "docs/emergency-2/CTO-HANDOVER.md",
      "start_line": 32,
      "end_line": 44,
      "text": "## 5. NEXT ACTIONS, in order\n1. Take over (the card); takeover message to the owner.\n2. Land `e2/1-0-selection` by the plain path (its selection run exactly; trailers checked; landing record; `log/plan-items.json`: 1-0 landed).\n3. Tell the EXAMIN and ASMO OS CTOs the handover method from tomorrow (DEC-1253): each writes its handover in its own repository at day end, records it, starts its fresh session from it, and the fresh session takes over by the same checks; send them the card's \"Take over\" section adapted (their own coordination ticket and paths).\n4. Start, in parallel (one code area each):\n   - the timing-tests lead (DEC-1251 D-03: (b) the timing cases W2-112, W2-13, W1-19 into the serial phase now, then (a) measured against the machine's reading; I-32);\n   - the release-rule lead (DEC-1251 D-01's note: build DEC-1235 (2)'s rule for approved bigger releases, I-34, and settle W2-209 so a fix like RP-1 rides a patch);\n   - the I-33 fix (`gov memaudit brief --kind writer` exits 4 and prints no LAUNCH line).\n5. The bundle: one batch merge and one selected run, then land; then the owner builds 0.1.8 by hand (or the CTO by code once I-34's rule lands).\n6. Gov OS's own fresh 80 on 0.1.7: the writer wall's template is approved (the owner added the line to `APPROVED`); confirm the launcher accepts it when the measure starts (DEC-1253).\n7. The practice-first work (DEC-1252, all 31 recommendations): the tool status list for 0.1.7, the findings log form in each repository with `gov findings collect`/`sync` (an approved feature), the `release:` field, the decision rubric with `Affects:`/`Enforced-by:` and one Sonnet research pass classing the 162 older decisions, `docs/RUBRICS.md`, data in specs. Plan them into the integration plan's streams.\n8. ASMO OS's usage report to the owner about 27 Nov (DEC-1245 (3)).\n\n",
      "chunk_id": "893d71547ea74432739ca5ac",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "140f140cd6b118b5931574cb",
      "sha256": "50ffb199d5f54978ac12d27dd0be2ff5699ff2b6814563519405f1f3dff0d279",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 323,
      "end_line": 329,
      "text": "4. **How it joins the decisions page:** `gov decisions page` takes only P1 and the P2 the CTO brings (`blocks` is not `nothing`); `rubric` is the computed line; a stopper (`blocks` set) forces the immediate page and the push; `gov decisions answer <sheet>` writes each answer as a register entry with `Decided-by: owner (page <batch>)`, so the level check at the commit passes by the same rule the sheet's entry satisfies (`ACCEPTED (owner, \u2026)`, DEC-862 (c)). `gov decisions basis --week` lists owner entries by channel (`page` or `chat`) and counts open packages not on a page, as the spec says.\n5. **The fixed form of the judgement** is the package itself: `question` (300), `found` (900), `options` 2-6 with `cost` and `consequence`, `recommendation {option, reason, confidence}`, `sources` each existing. The lead's or the CTO's own P3 and P2 choices are the same record with `status: ACCEPTED` and their `Decided-by`, listed in the digest (DEC-220), so the check at the commit is one rule for all three levels.\n\n**Size and when:**\n\n| Piece | Size | When |\n|---|---|---|\n",
      "chunk_id": "140f140cd6b118b5931574cb",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "587889641d57b2cbfde59ddc",
      "sha256": "7845714603d963ad62cfeeeb365583b86b7142fba8ce13a047461b7bb2adf096",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 321,
      "end_line": 323,
      "text": "   - **At the queue:** a branch that changes a spec (`docs/specs/**`, a `specification` record), a ticket's `kpis` or `allowed_paths`, a path under `docs/contract`, `docs/charter` or a planned wave's list must name an ACCEPTED P1 decision in a `Decision:` trailer; otherwise `QUEUE_DECISION_BELOW_LEVEL` (refuse). This is the same place as `NEW_TICKET_NOT_FEATURE` and uses the patch rule's P2 (owner's text) as a model.\n   - **At launch:** the planned-wave check (K2) stays and joins A-6 so it is on the path.\n4. **How it joins the decisions page:** `gov decisions page` takes only P1 and the P2 the CTO brings (`blocks` is not `nothing`); `rubric` is the computed line; a stopper (`blocks` set) forces the immediate page and the push; `gov decisions answer <sheet>` writes each answer as a register entry with `Decided-by: owner (page <batch>)`, so the level check at the commit passes by the same rule the sheet's entry satisfies (`ACCEPTED (owner, \u2026)`, DEC-862 (c)). `gov decisions basis --week` lists owner entries by channel (`page` or `chat`) and counts open packages not on a page, as the spec says.\n",
      "chunk_id": "587889641d57b2cbfde59ddc",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "79a5a8ce90609fffb13e174c",
      "sha256": "8c6bfb00ba9f6fdb959ce98d30507a6d4a7df0268f2302aced0ce748730a5220",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 192,
      "end_line": 199,
      "text": "## 4. Decisions\n\n**Problem.** `gov decisions in-force` lists **190** decisions, about 6,800 tokens of titles (27,115 characters over four, my estimate), and every CTO reads them at each start. Many are spent, many say a thing code already holds, and some are choices, not rules. Nothing says what deserves a decision record at all; and the owner's own words in DEC-1245 (4) already say a spec change is not one.\n\n**Proposal.**\n\n1. **A rubric for what is recorded as a decision.** *Recorded:* a standing rule or practice; a choice whose reason matters later; an exception to a rule; a measurement period; a rubric. *Not recorded:* a spec change (it is a change to the spec file, and git keeps its history); a one-off instruction; a status report. The test: if the reason would be needed in a month and no file says it, it is a decision.\n2. **Every new decision names what it affects:** an `Affects:` line with paths, specs or workflow steps (W1 to W16), or `none`. The impact trace (W6) reads it, so a change to a decision shows the paths and steps it touches. Today the graph has `Under`, `Changes` and `Supersedes` links only (`store/loader.py:410-470`).\n",
      "chunk_id": "79a5a8ce90609fffb13e174c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DEC-1238",
      "sha256": "98878e1a42d472df5c7c3b1315b169dc79a6c92031a6196f1c2eee6a31e4636f",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2134,
      "end_line": 2135,
      "text": "  - (5) **Step one, the tool map:** the golden workflow's \u00a75 completed from the code (audit 4's inventory the start), one row per tool, script, hook, cron line or schedule doing Gov OS's work, inside the product or outside it, meeting the section's five rules; the share of steps on the path today; and the answer to whether code today traces a change in a decision or a spec to the tickets, specs and tests it affects (through the graph and the path map), or only the landing's test selection does. The owner assesses the map for gaps before the plan.\n  - (6) **Step two, the decisions and the rubrics:** every decision since DEC-1209, and EXAMIN's from DEC-001, marked as held by code or by text only (from audits 1 and 4); in particular the ticket rubric, the model and effort rubric by criticality, and the escalation rubric (rule 8: the level set by code from the record, a decision below its level refused, the judgement kept in a fixed form); what makes each enforced on the path, and when.\n",
      "chunk_id": "fc6307e02a41619bfc588824",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2,
      "entry": "DEC-1238",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1244",
        "DEC-1240",
        "DEC-1239"
      ],
      "in_force": true
    },
    {
      "id": "729567ee0400859bbb8716ab",
      "sha256": "86f0584ffa64a673b156c7aa0de3f061bf0ae155e16dd2ba24475f51707bdf79",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 221,
      "end_line": 229,
      "text": "**What code holds and what stays practice.** Code: the `Enforced-by:` and `Affects:` lines required on a new decision by the basis check (`gov decisions basis`, extended with plan 5-1 and 5-4); the digest's hiding. Practice: deciding what is a decision, writing the lines, the one-time classing of the old ones.\n\n**Where it lives in the kit.** The rubric: the `decision-record.md` template (`template/governance/kernel/templates/`) and a section of `docs/RUBRICS.md` (proposal 5). The two lines: the template and the basis check.\n\n**Rides.** Plan 5-1 (the enforcement field, F-1) and 5-4 (the record's stated facts, F-2): `Affects:` and `Enforced-by:` are two more lines on the record those items already change. The digest change is a fix under W2-200 (`decisions/command.py:79`). Practice from today: the CTO writes both lines in every new decision.\n\n**Options and costs.** Cards DE-0 to DE-2 on the page.\n\n- **Approval:** (a) approve the rubric and `Affects:` (recommended); (b) with changes; (c) the rubric only, no `Affects:` line: cost, the impact trace stays blind to a decision's paths and steps.\n",
      "chunk_id": "729567ee0400859bbb8716ab",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "ed1e74722f44171ed55d6948",
      "sha256": "cd349c6f09a9103d248ae5f373974b6bfce949305d8a3d3a517845a8bcffa2e5",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 235,
      "end_line": 242,
      "text": "## 5. The rubrics register\n\n**Problem.** The owner has decided rubrics one at a time over a month: DEC-1120, DEC-1204, DEC-1208, DEC-1219, DEC-1225, DEC-1242 and more. They are scattered over many decisions and several files, and nothing says which a code check holds. GW \u00a73 says every standing rule carries its enforcement; for the rubrics nobody has written it down.\n\n**Proposal.** One file, **`docs/RUBRICS.md`** in Gov OS and its copy in the kit, **`governance/kernel/RUBRICS.md`** (the kernel folder, so `gov update` carries it). One row for each rubric: its rule in one line, the decisions that made it, and its **enforcement** field: `code` (held by code, with the check), `checked-after` (found after the fact, auto or typed), or `instruction` (only a sentence). The values are A-23's `class` values (audit 4 \u00a74.2): `instruction` is A-23's `judgement`. A column `binds` says `every repository` or `Gov OS only`. The kit copy carries the rows that bind every repository. A new or changed rubric is a standing decision, so it comes to the owner (GW rule 8: P1).\n\n**How A-23's field fills it.** When plan item 5-1 lands, the `enforcement:` block of `contract.yaml` and the `Enforced-by:` line of a decision (proposal 4) are the source. A G1 check (`kernel/checks/enforcement.yaml`, plan 5-1) compares each RUBRICS.md row's `by:` with them and refuses a `code` row whose check does not exist. Until then the CTO fills the column by hand from HELD and audit 4, at each release (as GW's \"Today\" column is filled).\n\n",
      "chunk_id": "ed1e74722f44171ed55d6948",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "77810aef3f1e168f55c077bc",
      "sha256": "8b2aed1b74fd9b852a6807f2d5eb457aa973c0a3d3bfa16668ae92d826ea219c",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 866,
      "end_line": 891,
      "text": "    \"from\": \"Proposal 5 \u00b7 DEC-1245 (4)\",\n    \"title\": \"Approve the rubrics register and its 20 rubrics?\",\n    \"found\": [\n     \"You listed 12: the golden rule and threat model, the work rubric, models and effort, escalation, criticality, usage, tests, fix loops, releases, the memory standard, imports, data in specs.\",\n     \"I found 8 more in the register and EMERGENCY-2: review convergence, the three measures and the floor, decision packages and the page, the machine and resource gate, proportionality profiles, secrets scanning, pings and quiet hours, test independence.\",\n     \"Each row has its decisions and an enforcement field: held by code, checked after, or only an instruction. Most are only an instruction today.\",\n     \"One file, <code>docs/RUBRICS.md</code>, and a kit copy.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Approve the register and the 20\",\n      \"A new or changed rubric is a standing decision and comes to you.\",\n      1\n     ],\n     [\n      \"b\",\n      \"Approve with the changes in my note\",\n      \"The CTO applies them first.\"\n     ],\n     [\n      \"c\",\n      \"Not yet\",\n      \"The rubrics stay scattered over many decisions.\"\n     ]\n    ],\n",
      "chunk_id": "77810aef3f1e168f55c077bc",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DEC-1238",
      "sha256": "8fad90066c8aebc30facbcd22ca783c84c3b361030f62f3c6c679193d523e21c",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2139,
      "end_line": 2143,
      "text": "  - (10) **Spec questions during the integration come to the owner:** wherever the golden workflow, the Contract or a spec is unclear, conflicts with another, or the code does something no spec decides, the CTO does not guess; each becomes a decision record (the question, what was found, the options with their costs, the recommendation, the sources), batched in the decisions-page form, by hand until the tool exists; a question that stops work pushes the owner at once, the rest come together; work that does not depend on the answer goes on.\n  - The order of the reports: steps one and two together as one report with the corrections to the golden workflow, then the plan; 0.1.5 stays first tonight.\n- **Basis:** the owner's message of 2026-11-22; audit 4's finding (21 % of the live Contract items enforced on the path; most refusals built inside `gov queue` and `gov launch`, which Gov OS bypassed).\n- **Governing sources:** docs/emergency-2/GOLDEN-WORKFLOW.md; docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md; docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md; docs/emergency-2/T2-ESCALATION-RUBRIC.md; DEC-1233; DEC-1236; DEC-1237.\n\n",
      "chunk_id": "513cb11d9011ff76f495e06c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2,
      "entry": "DEC-1238",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1244",
        "DEC-1240",
        "DEC-1239"
      ],
      "in_force": true
    },
    {
      "id": "d110962c15e25b031cb6c2a3",
      "sha256": "b8d861086211573ec37cb7dbdbc8550a39fa9d4f77c91167aa54857ab1f1d3e6",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 884,
      "end_line": 922,
      "text": "      \"The CTO applies them first.\"\n     ],\n     [\n      \"c\",\n      \"Not yet\",\n      \"The rubrics stay scattered over many decisions.\"\n     ]\n    ],\n    \"reason\": \"It collects what you decided into one place with its enforcement, as GW \u00a73 asks.\",\n    \"sources\": \"PRACTICE-FIRST-PROPOSALS.md \u00a75; GW \u00a73; DEC-1245 (4).\",\n    \"stops\": \"Does not stop work.\"\n   },\n   {\n    \"id\": \"RG-1\",\n    \"from\": \"Proposal 5\",\n    \"title\": \"How is the register kept?\",\n    \"found\": [\n     \"A-23's enforcement field is approved (DEC-1238 (1b)) and not built.\",\n     \"Until it is built, the column can only be written by hand, from HELD and audit 4.\",\n     \"A G1 check could later compare each row's <code>by:</code> with the field.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"A hand-written file now; the column filled from A-23's field once it exists\",\n      \"The CTO re-reads it at each release.\",\n      1\n     ],\n     [\n      \"b\",\n      \"Generated from a <code>Rubric:</code> tag on each decision\",\n      \"Needs plan 5-1 first and tags on 20 decisions.\"\n     ],\n     [\n      \"c\",\n      \"Leave the rubrics in the register and CLAUDE.md\",\n      \"The scatter this proposal ends.\"\n     ]\n    ],\n",
      "chunk_id": "d110962c15e25b031cb6c2a3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DEC-1238",
      "sha256": "7ce4dd568f1a4919d4c6cc9124d9675f73cd6a1b8259ced8a0c72e787fa09208",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2127,
      "end_line": 2129,
      "text": "### DEC-1238 \u2014 Audit 4 approved as the plan (the Charter's determinism sentence, the enforcement field as a feature, the rubric over research outputs); the golden workflow, the owner's draft, to be verified and completed; the integration emergency from the 0.1.5 cut; EXAMIN's planning waits for integrated Gov OS; steps one to four and the lift; spec questions come to the owner as decision records\n- **Status:** ACCEPTED (owner, 2026-11-22 about 16:50, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing; (3) takes effect when the owner cuts 0.1.5) \u00b7 **Under:** DEC-1233 (5)-(6), DEC-1232 (1), DEC-1236, DEC-1237 \u00b7 **Changes:** DEC-1232 (1) (EXAMIN's planning stage, the owner's priority 5, waits for integrated Gov OS); the Charter v6 principle 4 and the Contract's envelope rules (the determinism sentence, a seventh envelope rule)\n- **Decision:**\n",
      "chunk_id": "7b048a39f64c408205a1f0ad",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2,
      "entry": "DEC-1238",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1244",
        "DEC-1240",
        "DEC-1239"
      ],
      "in_force": true
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
    "duplicates": 30,
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
      "chunk_id": "1b3bfd607b71dc1f3a4fe894",
      "parent_id": "2ed23f677083c2697d6db005",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2303,
      "end_line": 2308
    },
    {
      "chunk_id": "893d71547ea74432739ca5ac",
      "parent_id": "0b21535bb73e60eb85081c96",
      "path": "docs/emergency-2/CTO-HANDOVER.md",
      "start_line": 32,
      "end_line": 44
    },
    {
      "chunk_id": "ed1e74722f44171ed55d6948",
      "parent_id": "c4da36fc70d94186550311e4",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 235,
      "end_line": 242
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "29e3957a3474f57aac75f412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "6fa8ebc1ac94c730341711fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "935a61d752571c96d09d8805",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e2cab52bf2bc3b8fd833717b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c179e29f1818433f13c1cd81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "cfd12adde4376b5278c7c0a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "5919eee2d849c071477a75a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "1840ca6dfab62e550780ca84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4250c59a485bd8117c3c1f32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "2e9659cb5f4a11a2372cee3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "chunk_id": "886c2488e6e7babf7319007a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "99dcff6d1a2eded4c47445d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "chunk_id": "90f900b0f85bc003447c5a81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "1d5d569ee3a8d3df0a7b38ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "2dfc45f420fdddffa3af4ad5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "db498749c1a1d29d8a578413",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "578546c5692ec12f0ef4ab65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "da36367d5192642722fe34b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c5576f0a9cae399ad14a8934",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "1a067776913effa2dbd91015",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "7f0f33b753cb7c4a3feb94b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "67d93f3050fd08a30c0a47f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "e796bf4cda2e181f66664789",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "52b0be7a4a38226be6c2c349",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "df066c775dd6ec39da6c3b67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "24be32b093ef20a16d661a09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "chunk_id": "503371e8317a6a0913c87362",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "6aa9542dd431661ee697fff1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "9688bb6b74567d0621c1cb20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "7eaaa5e27988881aefb5bcf9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "d2af1d04475a17e391461db8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "840693c1e06d562be03500de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3c8ad782d1191ff2d9612bc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "fe241ea2858da1e32c7d164b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "13767eaf6bb5e3777c776721",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "185e1120d06824391a371c18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "05d74f3d59b3193c88af5e99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "d6b92d9829cc473c4a591d9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4135d580cb7cd66baf0ec3bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "9a9660e8d079ccc05016c03d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "c239d037dc9616dccbf00bc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "0f8dfd9ec3eeb6ca759d02e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "f91fec910ef94da776844b09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "chunk_id": "bad504b6b1f21117539efa55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "d1a02397d4174dfaae858781",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "9a5b3413f034b6e1d0a1c7e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "ce6c2cf73fde0d65573b955b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "cd33a21d59323f1b61892f4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "1434327e371f542064f6a6d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "4e661ab96eb4c2dbea8c42f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "f638f756c49a82c851222393",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-esl1.md",
      "chunk_id": "81ac2b32c804f4d5db2514cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "030934a4e9968892a201f540",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "f269b49d897f8b77354681c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "7651e003f1783d626f1b0d92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "59adc3fe8cc39bcf7ebe43d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "e2d295a285038f84c17036ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "62d149c23394fc84716d1f24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "d6d947ca9bd14dec10fd84e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "a35570ae70adfe57927f63da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "cd81776c20ca8265e7912cee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "chunk_id": "3a754c7181c96150a6db7412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "c79f9a70411715d471ea0914",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "096973f12db60789c80e53ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "d6d28a0f1419609db8f30145",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "8197abf31f5242efeebc1211",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md",
      "chunk_id": "debaa3680663c7af3d4fb9df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "1720064ff6648362d8b6d236",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4ab56cb82ae415b0536ba6e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-129-links.md",
      "chunk_id": "7ac6e9ec7b147230293d8aca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "c9d4ab61d97bb344e39290ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "3a7ae39b8f5eccb7d8560afd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/skills/orchestration/briefs-and-returns.md",
      "chunk_id": "4e68019f28b40e0109e3f794",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "2e0818d9298a2ecae04c2f15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4b9ec159fb8a9faeac928fbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "35a6334e947769a729676e0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "656798572c12706bedbc99d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "06feffa7d351cc570ad5181d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "29e96e16fccd3e1e7ea12d5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "dff484dff5ab68650ea4a4c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "1451dc6a9f2f71ff4deb13e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "51447077e70c5fbf5f3b6532",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "schemas/records/decision.schema.json",
      "chunk_id": "d74667c0b4111926327711b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "8acad86b83f7d67405a94b8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/rubric-research.md",
      "chunk_id": "9cacf33a9f459b0a12995c6c",
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
      "used": 5911
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwyMTI3LDIxMjksIjdiMDQ4YTM5ZjY0YzQwODIwNWExZjBhZCJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMjEzNCwyMTM1LCJmYzYzMDdlMDJhNDE2MTliZmM1ODg4MjQiXSxbImRvY3MvREVDSVNJT05fUkVHSVNURVIubWQiLDIxMzUsMjEzNSwiODgyMWIxMzlkODViODE1YjI1ZWM2MWVhIl0sWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwyMTM5LDIxNDMsIjUxM2NiMTFkOTAxMWZmNzZmNDk1ZTA2YyJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMjI0MSwyMjQxLCI0MDVhMjQ0YTc2ZjNlMDlkN2Q0YzM5ZWEiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vREVDSVNJT05TLUhFTEQubWQiLDMyMSwzMjMsIjU4Nzg4OTY0MWQ1N2IyY2JmZGU1OWRkYyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9ERUNJU0lPTlMtSEVMRC5tZCIsMzIzLDMyOSwiMTQwZjE0MGNkNmIxMThiNTkzMTU3NGNiIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0dPVi1PUy1ERUNJU0lPTlMtMjAyNi0xMS0yNS5odG1sIiwzMDEsMzI2LCJhNjExNTA3NjAyMDRkMmNmOTc4N2RlODciXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUFJBQ1RJQ0UtRklSU1QtREVDSVNJT05TLTIwMjYtMTEtMjQuaHRtbCIsNDk5LDUxOSwiZThlNzZhMTAyMDgwZTZmZTZmNDNiZDk3Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1BSQUNUSUNFLUZJUlNULURFQ0lTSU9OUy0yMDI2LTExLTI0Lmh0bWwiLDc2OCw3OTEsIjBlMmIxY2ZlNWE0MzNmMThjYWQzNjQ4YyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9QUkFDVElDRS1GSVJTVC1ERUNJU0lPTlMtMjAyNi0xMS0yNC5odG1sIiw4NjYsODkxLCI3NzgxMGFlZjNmMWUxNjhmNTVjMDc3YmMiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUFJBQ1RJQ0UtRklSU1QtREVDSVNJT05TLTIwMjYtMTEtMjQuaHRtbCIsODg0LDkyMiwiZDExMDk2MmMxNWUyNWIwMzFjYjZjMmEzIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9QUkFDVElDRS1GSVJTVC1QUk9QT1NBTFMubWQiLDUsOCwiNGFlOTE4Y2M1ZGQ0ZjMzZThjOGZjM2RlIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9QUkFDVElDRS1GSVJTVC1QUk9QT1NBTFMubWQiLDE0LDIxLCJjM2IxMWZiN2EzNDFjNzZiOWMyZDRmODIiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL1BSQUNUSUNFLUZJUlNULVBST1BPU0FMUy5tZCIsMTkyLDE5OSwiNzlhNWE4Y2U5MDYwOWZmZmIxM2UxNzRjIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9QUkFDVElDRS1GSVJTVC1QUk9QT1NBTFMubWQiLDIyMSwyMjksIjcyOTU2N2VlMDQwMDg1OWJiYjg3MTZhYiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvUFJBQ1RJQ0UtRklSU1QtUFJPUE9TQUxTLm1kIiwyMzksMjQyLCJmNDc4OTFiYzcwZGMwMTg3MjY3MGZjOTYiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWEiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6IjM5MTU1YjBjZTJhYTk1MzQiLCJvIjpbMSwwLDIxLDI2LDE2LDEzLDExLDM2LDI1LDI5LDE1LDMsMTQsMiwxOCwyMiw4LDUsNCw3LDIwLDM0LDEwLDM4LDMxLDYsMzUsOSwzMCwyNywzNywyMywyNCwzMywxOSwzMiwzOSwyOCwxMiwxN119LCJxIjoicHJhY3RpY2UtZmlyc3QgZGVjaXNpb25zOiB0b29sIHN0YXR1cyBsaXN0LCBmaW5kaW5ncyBsb2cgYW5kIGdvdiBmaW5kaW5ncyBjb2xsZWN0IHN5bmMsIHJlY29yZCByZWxlYXNlIGZpZWxkLCBkZWNpc2lvbiBydWJyaWMgQWZmZWN0cyBFbmZvcmNlZC1ieSwgcnVicmljcyByZWdpc3RlciwgZGF0YSBpbiBzcGVjczsgdGhlIGludGVncmF0aW9uIHBsYW4ncyBzdHJlYW1zIGFuZCBwaGFzZXMiLCJyIjowLCJzIjoiYTQ1NWIwMGNmMDczNmQ3YTM3ZDllNTg1ZTY0MzBjNDU1ZWY0ZmU2MCIsInQiOm51bGwsIngiOlsiMGIyMTUzNWJiNzNlNjBlYjg1MDgxYzk2IiwiMmVkMjNmNjc3MDgzYzI2OTdkNmRiMDA1IiwiYzRkYTM2ZmM3MGQ5NDE4NjU1MDMxMWU0Il19",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "practice-first decisions: tool status list, findings log and gov findings collect sync, record release field, decision rubric Affects Enforced-by, rubrics register, data in specs; the integration plan's streams and phases",
      "practice-first decisions tool status list findings log gov findings collect sync record release field decision rubric Affects Enforced-by rubrics register data specs integration plan s streams phases"
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
        "chunk_id": "8821b139d85b815b25ec61ea",
        "path": "docs/DECISION_REGISTER.md",
        "start_line": 2135,
        "end_line": 2135
      },
      {
        "chunk_id": "f47891bc70dc01872670fc96",
        "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
        "start_line": 239,
        "end_line": 242
      }
    ]
  }
}
