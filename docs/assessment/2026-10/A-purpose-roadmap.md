# Independent assessment of the Gov OS, October 2026 — Lens A: Purpose and roadmap

## 1. Header

- **Lens:** A, Purpose and roadmap. It is one of five lenses (A to E) assessed in parallel; a sixth session synthesises them.
- **Date:** 2026-10-19.
- **Assessor:** a fresh, read-only session in the independent-auditor role (`GOV_ROLE=independent-auditor`). The Wave 2 orchestrator started it on the owner's order of 2026-10-19. I wrote none of the work assessed here.
- **Head assessed:** `w2/integrate` at `fecb870c` (2026-10-19, "Brief text in force, versioned: …"). `w2/integrate` is Wave 2's integration branch: a finished ticket is merged there before it closes. While I read, the owner's next batch was staged but not committed: decisions DEC-813 to DEC-817 in the register, the W2-57 card and lines for W2-24, W2-37 and W2-52 in the WBS, and rows W2-M364 and W2-L319 in the list. I read those three files as staged.
- **Branches read** (head commit of each):
  - `main` and `w1/integrate`: `7d60dec6` (Wave 1's exit and the Wave 2 plan's approval, 2026-10-16 17:29). `w1/W1-42`: `da6fb889`.
  - Built and held on their own branches, not merged: `w2/W2-02` `2a35fd7b`, `w2/W2-03` `9a3e3456` (stacked on W2-02), `w2/W2-05` `f19f156e`, `w2/W2-16` `1908149d` (stacked on W2-49), `w2/W2-20` `1a54976c`, `w2/W2-26` `62c4e477`, `w2/W2-37` `2ff873b2` (stacked on W2-03), `w2/W2-49` `19d45246` (carries Contract v4.2), `w2/W2-50` `0affa162`, `w2/W2-51` `c2c80e6c`, `w2/W2-52` `a21f06a7` (stacked on W2-49).
  - Merged into `w2/integrate`: `w2/W2-53` `4f3d3405` (merge `c9537e39`), `w2/W2-54` `226ec458` (merge `6f7d4f9e`), and W2-01 (merge `3022c2df`).
- **What I read:**
  - Charter v5 (`docs/charter/CHARTER_v5.md`). Contract v4 at version 4.1 on `w2/integrate` (`docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml`) and at version 4.2 on `w2/W2-49`. ADR-0001 (threat model) and ADR-0002 (architecture and stack).
  - The decision register (`docs/DECISION_REGISTER.md`): every decision cited in this report, in full. The Wave 2 decisions DEC-719 to DEC-817 by title, and in full where I use them.
  - Wave 1: `docs/plan/WAVE_1_WBS.md` (its size estimate, §6 the Wave 2 outline, §7 the Wave 3 outline), the Wave 1 exit audit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`, and the exit report `docs/plan/wave-1-exit/EXIT-REPORT.md` (searched for a size review).
  - Wave 2: `docs/plan/WAVE_2_WBS.md`, `docs/plan/WAVE_2_LIST.md`, `docs/plan/WAVE_2_TRIAGE.md`; the front matter of every ticket file in `.tickets/`; the acceptance-test folders on every Wave 2 branch, for the Contract ids they cite; the W2-51 plan validator.
  - The orchestrator's records: `.gov-runtime/scratch/orchestrator/CHECKPOINT.md` (its "RESUME HERE" block) and the close logs `log/W2-01-close.json`, `log/close-DAEO-7rr2-2.json` and `log/close-DAEO-7rr2-3.json`. W2-50's review logs by file name only.
  - `governance/project/prompts/w2-orchestrator.md` (§3, §13, §14 and appendix A3). No other file in `governance/project/` is a basis for any finding.
- **What I ran:**
  1. In the main repository, read-only git commands only: `git log`, `git show`, `git diff --stat`, `git diff --numstat`, `git diff --shortstat`, `git ls-tree`, `git merge-base`, `git rev-list --count`, `git rev-parse` and `git status --short`.
  2. My own Python scripts in `/tmp/gov-os-assessment-A/`, each run as `python3 -I <script>`. They read the repository's files and write only into `/tmp/gov-os-assessment-A/`: `parse_contract.py` (the items of Contract v4.1 and v4.2), `parse_list.py`, `parse_triage.py`, `parse_tickets.py`, `build_map.py` and `build_cap_summary.py`. They import no `gov` code.
  3. A clone, `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /tmp/gov-os-assessment-A/repo`. Inside the clone only, a worktree `/tmp/gov-os-assessment-A/tree-v42` on a scratch branch cut from `origin/w2/integrate`, with Contract v4.2's two files, `docs/changes/` and the held branches' acceptance folders checked out from their branches.
  4. The W2-51 plan validator. This is W2-51's own code (`docs/plan/tools/validate_w2.py` at `c2c80e6c`), copied out with `git show` into `/tmp/gov-os-assessment-A/tools/`. I ran it as `python3 -I tools/validate_w2.py --root <tree>` on the clone at `fecb870c` and on `tree-v42`. It imports no `gov` code.
  5. No `gov` command was run. The `gov` on PATH imports the main repository's `src/`, so no code of that package ran for this report. No test, rebuild, indexing run or regression was run, so no run needed the resource gate.
- **Limits:**
  - I ran no tests. Test results come from the orchestrator's close logs and from the records.
  - I did not read the held-out material, the settings files, `~/.claude/`, `~/gov-os-workbench`, `docs/source/` or EXAMIN's repository. The validator's five checks that need the workbench or `docs/source/` reported NOT RUN. For the same reason, the table in 2.2 shortens one capability title, CAP-49's.
  - List rows are mapped to a Contract item where the row names the item's id. For Wave 2 items, the rows assigned to the ticket that closes the item are mapped too. A row that serves an item without naming it, on some other ticket, is not caught.
  - "Built and closed" for the 149 Wave 1 items rests on three things: the Contract's provider fields, the closed state of all 47 provider tickets, and W1-43's finding that all 149 are delivered and cited. I did not re-run their tests.
  - Line counts are physical lines of `.py` files (`git show … | wc -l`). "Lines added" are `git diff` insertions.
  - The machine's 1-minute load was above 20 for part of the session: 22.3 when I made the clone, 22.9 at a later check. A clone is not a heavy run under the brief, and I made no heavy run.
  - One close log, `log/close-DAEO-7rr2.json`, is not valid JSON. I did not use it.
  - Two shell commands were each refused once by the guard. The first was refused because its quoting could not be read (DEC-409); I made the same read with the search tool. The second was refused because it wrote to a path the guard could not resolve; I made the same read without writing a file. No call was refused twice.

**Terms used in this report.** Each internal term is defined once here.

- **Gov OS:** the governance system built in this repository. It is a Python command-line tool (`gov`), a path guard, ticket and decision records, and search indexes. Together they govern the AI agents that build software for the owner.
- **Charter v5:** the top document. It sets the purpose, the scope, the roles, the waves and the order of authority.
- **Contract v4, versions 4.1 and 4.2:** the list of mandatory capabilities, **CAP-01 to CAP-62**. Each capability has lettered **items**, such as CAP-44.h. Each item belongs to a wave: **W1**, **W2**, **W3**, or **NONE** (a non-goal or a dropped item). The owner accepted version 4.2 (DEC-741), but it sits on the unmerged branch `w2/W2-49`. `w2/integrate` still carries 4.1.
- **MR-1 to MR-6:** the master rules, the six constitutional rules in the Charter and the Contract.
- **Waves:** Wave 1 "Integrate" (done, with exceptions the owner accepted), Wave 2 "Strengthen" (running since 2026-10-16) and Wave 3 "Complete" (not yet planned in detail). **Release 1** is the single signed release `v1.0.0`. It comes after Wave 3 and after qualification.
- **Ticket:** one unit of work with its allowed paths and its KPIs, the measurable success and failure conditions. An independent test designer writes its acceptance tests before the work. Wave 2's tickets are W2-00 to W2-57. The **WBS** (`WAVE_2_WBS.md`, the work breakdown structure) holds their table and their cards. A ticket's **profile**, FULL or STANDARD, sets how much review it gets.
- **Ticket states:** **closed**, by `gov close` or by an owner-ordered `tk close`; **merged** into `w2/integrate` but not closed; **held**, meaning built and reviewed on its own branch and waiting to merge and close; **planned**, meaning a ticket file exists but work has not started; **nowhere**, meaning no ticket.
- **`gov close`:** the command that closes a ticket. It runs the full regression of about 13,500 tests, which takes about an hour. It also checks that nothing changed after the review (the **probe gate**). A **clean close** exits 0 with no exception.
- **Ratchet and quarantine:** two lists in the path map. A test on the ratchet, `accepted_reds`, is a known failure that does not refuse a close. A test on the quarantine, `load_sensitive`, that fails is re-run alone, and the close counts the re-run if it passes. Both lists change only by an owner commit, and from 2026-10-18 they only shrink (DEC-757, DEC-766).
- **The Wave 2 list** (`WAVE_2_LIST.md`): the open findings and wishes carried into Wave 2. Each is a **row**, with an id by severity: W2-H (high), W2-M (medium), W2-L (low), W2-I (info), W2-C (closed before Wave 2). **Triage** (`WAVE_2_TRIAGE.md`) assigns each row to a ticket, to Wave 3 or to the backlog.
- **AR-1 to AR-10:** the adoption-readiness block. These are the repairs the Wave 1 exit audit required before any product adoption (DEC-718).
- **Tracks:** Track A, adoption readiness; Track B, the EXAMIN pilot; Track C, the rest of Wave 2.
- **W1-43:** the Wave 1 exit audit. It classed each capability, item and master rule as OK or **WEAKENED**.
- **Owner package** (P-W2-n): a question put to the owner, with options. The answer becomes a decision (DEC-n). A **round** is one extra cycle of review and repair on a ticket.
- **Lead and worker:** a lead session runs one ticket and starts worker sessions: engineer, test designer, reviewer.
- **CIT-P and CIT-E:** the proposal and the evaluation of a change to a closed specification (CAP-33).
- **Lite:** a reduced Wave 2 form of a Wave 3 item, named as lite in Contract v4.2.
- **EXP-003:** the planned experiment on retrieval and indexing (W2-15a, W2-15b).

Severity in the findings is my own judgement. **High** means it threatens the wave's purpose or schedule. **Medium** means it weakens a promised check or a promised part of the scope. **Low** means a gap in the records with little effect of its own.

## 2. Answers to the lens questions

### 2.1 Does what is built, and what is planned, match the Charter and Contract v4.2?

**In short.** The plan matches the Charter and Contract v4.2 closely, with two gaps: eight of the Charter's Wave 2 roles (F5) and the per-wave size review (F6). One item has no closing ticket on record: CAP-44.f (F8). What is built does not yet deliver any Wave 2 item. No Wave 2 Contract item is closed, four are built on held branches, and the step that turns built work into delivered work, a clean `gov close`, has not yet worked once (F1). Most of Wave 2's effort so far has gone into the Gov OS's own machinery (F2). The purpose is met in its structure, but not yet in its payoff to the products (F3).

**The purpose, aim by aim.**

| Aim (the owner's words) | What the Charter and Contract say | State on 2026-10-19 |
|---|---|---|
| The project's memory lives in the repository instead of agents' memory | Charter §1: "The authoritative memory is the repository: git-tracked records plus derived indexes that can be rebuilt from git on any machine." | Built in Wave 1: records, the decision register, indexes, checkpoints. Wave 2 strengthens it: W2-06 (commit-time re-index, CAP-17.b), W2-13 (ranked lexical retrieval), W2-55 (decision tagging). None of these has closed. W1-43 found CAP-15.d (the context packet's ceiling: "814821 tokens against 6000"), CAP-17.c (the index canaries) and CAP-10 (semantic retrieval below the Contract's line) weakened (F7). |
| Agents are safe and governed | ADR-0001: guardrails catch honest mistakes. The hard boundary is git history, the lefthook pre-push gate, CI and owner-only merge. | The guard, the sandboxed launcher and the probe gate are built. The lefthook hooks, including the pre-push gate that ADR-0001 counts in the hard boundary, stay uninstalled until W2-08 (WBS §0 rule 4; exit criterion 2). W2-08 waits for W2-01, W2-02, W2-05 and W2-06 to land, and those wait on closes (F1). Row W2-H002 says the CI job is red "unmeasured" until the owner approves three tools. |
| The owner stays in control | Charter §6: the owner is the customer and the final authority (MR-6). CAP-21: approvals are owner facts. | Every decision is either the owner's or delegated with a right to overturn it, and the owner commits the register. W1-43 classed MR-6 WEAKENED: approvals were transcribed, not owner git facts (F-M6). Its repair, AR-7 (W2-12), has not started. In three and a half days the owner faced packages numbered up to P-W2-47, and the register gained 99 decisions (F2). |
| The products EXAMIN, UPIM and ASMO are built faster and more safely | Charter §1: adoption starts after Release 1, with one exception, the EXAMIN pilot in Wave 2. | No product is governed yet. EXAMIN's pilot comes at the end of Wave 2, and three later decisions have lengthened its path. UPIM and ASMO are in no plan before Release 1, and Release 1 has no date (F3). |

**The Contract.** Contract v4.2 has 62 capabilities and 214 items: 149 in Wave 1, 20 in Wave 2, 38 in Wave 3 and 7 NONE.

| Contract v4.2 wave | Items | Built and closed | Merged | Held | Planned | Nowhere |
|---|---|---|---|---|---|---|
| W1 | 149 | 149, of which 12 were WEAKENED at W1-43 | — | — | — | 0 |
| W2 | 20 | 0 | 0 | 4: CAP-33.b and CAP-33.g (W2-37), CAP-43.b (W2-16), CAP-44.f (W2-52) | 16 | 0, but CAP-44.f is in no ticket's `closes` field (F8) |
| W3 | 38 | 0 | 0 | parts of CAP-43.d, built early on W2-16, as the Contract allows | — | 38: Wave 3 has no tickets yet |
| NONE | 7 | — | — | — | — | 7, by design |

- **Wave 1 items.** All 149 are built, by 47 Wave 1 tickets, all of them closed. W1-43 found every one delivered and cited by an acceptance test. It also classed 25 of its 197 rows (capabilities, items and master rules) WEAKENED. These include 12 Wave 1 items: CAP-01.b, 06.d, 15.d, 17.c, 21.a, 25.a, 39.a, 40.c, 56.a, 58.c, 59.a and 59.b. They also include CAP-10 at capability level (hit@5 of 83.33 against the Contract's 85, with "the contract … not re-baselined") and MR-4, MR-5 and MR-6. Their repairs are Wave 2 work, and most have not started (F7).
- **Wave 2 items.** Every one of the 20 has a ticket:
  - CAP-04.a and 04.d: W2-31.
  - CAP-10.b, 19.a and 19.c: W2-32.
  - CAP-17.b: W2-06.
  - CAP-22.b and 22.c: W2-33.
  - CAP-30.c: W2-34.
  - CAP-30.g: W2-35.
  - CAP-32.d: W2-36.
  - CAP-33.b and 33.g: W2-37.
  - CAP-37.e: W2-39.
  - CAP-43.b: W2-16.
  - CAP-44.f: W2-52, in the WBS table only.
  - CAP-44.h: W2-30.
  - CAP-45.a: W2-17.
  - CAP-53.b: W2-38.
  - CAP-61.f: W2-40.

  None is delivered by a closed ticket. Four are built on held branches. The tickets that hold the other 16 have not started.
- **Wave 3 and NONE items** stay outside Wave 2 by design, with two kinds of exception:
  - W2-16 builds parts of CAP-43.d early (semantic version, CLI version, schema versions, release notes). The CAP-43 wave note allows this: "release contents of CAP-43.d built before W3 are delivered ahead of that item's wave".
  - W2-38 and W2-48 (both planned) build parts of CAP-39.c early: impact-selected tests at close, and a test-result cache "keyed on exact input hashes". CAP-39.c is a Wave 3 item: "dependency-aware impacted-test selection … cache keyed by content/policy/framework hashes".

  Tests on several held branches also cite Wave 3 items (CAP-02.c, 43.c, 43.d, 44.g, 44.k, 44.l, 47.a). Most of these citations check what stays in Wave 3.
- **Master rules.** W1-43 found MR-1 to MR-3 OK, and MR-4 to MR-6 WEAKENED (table in 2.2).

**Roles.** Charter §6 puts eleven roles and typed handoffs in Wave 2. Contract v4.2 carries only two items for them, and the plan adds one role. The other eight roles have no Contract item, ticket or row (F5).

**Size.** DEC-064 set a size review for every wave. None is recorded, and the code is about three times DEC-064's estimate for all three waves (F6).

**Plan against time.** The plan (WBS §4) is ≈ 7,100 lines in "53 + W2-00" tickets (its ticket table now lists 57 plus W2-00; F8), over ≈ 21 to 27 working days, with a critical path of ≈ 20.5 days. By the plan's own duration rule, the first three tickets on the critical path (W2-01, W2-02, W2-03) take ≈ 6.8 working days. Two of the three are built and held. The building is therefore roughly on the plan's pace. The closing is not: after three and a half calendar days, 1 of 55 tickets is closed, and that one by owner decision (F1).

### 2.2 Every Contract v4.2 item mapped to its tickets, its list rows and its state

The table below gives one row per capability (62 rows). Appendix A gives one row per item (214 rows): the Wave 1 tickets that built it; the Wave 2 tickets that close it or cite it; the acceptance folders on Wave 2 branches that cite it; the list rows that name it, with their triage; the list rows on its closing ticket; and its state. Appendix B states the method.

| Capability | Title | Items (W1/W2/W3/NONE) | Where the Wave 2 and Wave 3 items stand |
|---|---|---|---|
| CAP-01 | Authority precedence and hard invariants | 4/0/0/0 | W1: 4 built and closed (CAP-01.b WEAKENED at W1-43) |
| CAP-02 | Release authenticity (lite: signed git tags) | 1/0/1/1 | W1: 1 built and closed; W3: CAP-02.c; NONE: CAP-02.b |
| CAP-03 | Security and sensitivity classification | 5/0/0/0 | W1: 5 built and closed |
| CAP-04 | Budget and resource governance | 2/2/0/0 | W1: 2 built and closed; CAP-04.a: W2-31: planned (not started); CAP-04.d: W2-31: planned (not started) |
| CAP-05 | Emergency controls (pause/freeze/cancel/rollback) | 4/0/0/0 | W1: 4 built and closed |
| CAP-06 | Repository contract and path map | 5/0/0/0 | W1: 5 built and closed (CAP-06.d WEAKENED at W1-43) |
| CAP-07 | Authoritative vs derived state separation | 2/0/0/0 | W1: 2 built and closed |
| CAP-08 | Deterministic structured memory (records) | 1/0/0/0 | W1: 1 built and closed |
| CAP-09 | Relationship/graph memory | 2/0/0/0 | W1: 2 built and closed |
| CAP-10 | Semantic memory (vector/embedding retrieval) | 1/1/0/0 | W1: 1 built and closed; CAP-10.b: W2-32: planned (not started) |
| CAP-11 | Lexical memory (FTS/BM25) | 1/0/0/0 | W1: 1 built and closed |
| CAP-12 | Code-structural memory (AST/LSP/SCIP) | 2/0/0/0 | W1: 2 built and closed |
| CAP-13 | Temporal and episodic memory | 2/0/0/0 | W1: 2 built and closed |
| CAP-14 | Failure memory | 1/0/0/0 | W1: 1 built and closed |
| CAP-15 | Context packet compilation | 7/0/0/0 | W1: 7 built and closed (CAP-15.d WEAKENED at W1-43) |
| CAP-16 | Multi-batch, multi-hop, paginated retrieval | 3/0/0/0 | W1: 3 built and closed |
| CAP-17 | Incremental indexing and freshness | 2/1/0/0 | W1: 2 built and closed (CAP-17.c WEAKENED at W1-43); CAP-17.b: W2-06: planned (not started) |
| CAP-18 | Retrieval router (multi-route fusion) | 2/0/0/0 | W1: 2 built and closed |
| CAP-19 | Retrieval component separation and model selection | 0/2/1/0 | CAP-19.a: W2-32: planned (not started); CAP-19.c: W2-32: planned (not started); W3: CAP-19.b |
| CAP-20 | Rebuild guarantee (delete derived, rebuild from git) | 1/0/0/0 | W1: 1 built and closed |
| CAP-21 | Owner-only approval facts (lite of L0-L5 authority levels) | 1/0/0/1 | W1: 1 built and closed (CAP-21.a WEAKENED at W1-43); NONE: CAP-21.b |
| CAP-22 | Agent roles and typed A2A handoffs | 2/2/0/0 | W1: 2 built and closed; CAP-22.b: W2-33: planned (not started); CAP-22.c: W2-33: planned (not started) |
| CAP-23 | Concurrency and task claims | 2/0/1/0 | W1: 2 built and closed; W3: CAP-23.b |
| CAP-24 | Skill lifecycle and versioning | 3/0/0/0 | W1: 3 built and closed |
| CAP-25 | Tool registry and capability memory (lite) | 6/0/0/1 | W1: 6 built and closed (CAP-25.a WEAKENED at W1-43); NONE: CAP-25.c |
| CAP-26 | Plugin trust boundary (hash-binding, descriptor security) | 0/0/0/1 | NONE: CAP-26.a |
| CAP-27 | Read/act separation of commands (lite of MCP/A2A/knowledge layers) | 1/0/0/1 | W1: 1 built and closed; NONE: CAP-27.b |
| CAP-28 | Natural-language intent routing and small command surface | 2/0/0/0 | W1: 2 built and closed |
| CAP-29 | Specification lineage (idea to live evidence) | 0/0/2/0 | W3: CAP-29.a, CAP-29.b |
| CAP-30 | Feature readiness contract (26-dimension checklist) | 4/2/1/0 | W1: 4 built and closed; CAP-30.c: W2-34: planned (not started); CAP-30.g: W2-35: planned (not started); W3: CAP-30.d |
| CAP-31 | Unified task DAG with dynamic generation | 4/0/0/0 | W1: 4 built and closed |
| CAP-32 | Research and experiment lifecycle | 1/1/2/0 | W1: 1 built and closed; CAP-32.d: W2-36: planned (not started); W3: CAP-32.a, CAP-32.b |
| CAP-33 | Change-impact transactions (CIT-P simulation, CIT-E execution) | 4/2/1/0 | W1: 4 built and closed; CAP-33.b: W2-37: held (built on its branch, not merged); CAP-33.g: W2-37: held (built on its branch, not merged); W3: CAP-33.c |
| CAP-34 | Human decision gates and contradiction resolution | 5/0/0/0 | W1: 5 built and closed |
| CAP-35 | Model routing (T0-T3 tiers, reasoning levels) | 0/0/3/0 | W3: CAP-35.a, CAP-35.b, CAP-35.c |
| CAP-36 | Empirical model routing telemetry | 0/0/1/0 | W3: CAP-36.a |
| CAP-37 | Structured checkpoints and mandatory triggers | 6/1/0/0 | W1: 6 built and closed; CAP-37.e: W2-39: planned (not started) |
| CAP-38 | Verification test families (product and governance) | 6/0/0/0 | W1: 6 built and closed |
| CAP-39 | Governance health scheduler (G0-G6 tiers) | 2/0/2/0 | W1: 2 built and closed (CAP-39.a WEAKENED at W1-43); W3: CAP-39.b, CAP-39.c |
| CAP-40 | Execution telemetry and organisational questions | 3/0/1/0 | W1: 3 built and closed (CAP-40.c WEAKENED at W1-43); W3: CAP-40.b |
| CAP-41 | Lesson records with scope | 5/0/4/1 | W1: 5 built and closed; W3: CAP-41.g, CAP-41.h, CAP-41.i, CAP-41.j; NONE: CAP-41.e |
| CAP-42 | Legacy governance retirement and archive policy | 3/0/0/0 | W1: 3 built and closed |
| CAP-43 | Canonical OS repo separation and immutable releases | 1/1/2/0 | W1: 1 built and closed; CAP-43.b: W2-16: held (built on its branch, not merged); W3: CAP-43.c, CAP-43.d |
| CAP-44 | gov init and gov adopt lifecycle | 6/2/4/0 | W1: 6 built and closed; CAP-44.f: held: built on W2-52's branch (W2-49 writes it into Contract v4.2); no ticket's `closes` names it (F8); CAP-44.h: W2-30: planned (not started); W3: CAP-44.g, CAP-44.i, CAP-44.k, CAP-44.l |
| CAP-45 | gov update lifecycle | 0/1/1/0 | CAP-45.a: W2-17: planned (not started); W3: CAP-45.b |
| CAP-46 | Cross-machine sync via git | 1/0/0/0 | W1: 1 built and closed |
| CAP-47 | Independent adoption/audit roles and fresh-session independence | 2/0/2/0 | W1: 2 built and closed; W3: CAP-47.a, CAP-47.c |
| CAP-48 | Framework health SLOs and healthy-repo definition | 0/0/2/0 | W3: CAP-48.a, CAP-48.b |
| CAP-49 | Qualification (title shortened in this report) | 2/0/1/0 | W1: 2 built and closed; W3: CAP-49.a |
| CAP-50 | Artifact flow, dependency consumption and end-to-end traceability | 2/0/5/0 | W1: 2 built and closed; W3: CAP-50.b, CAP-50.d, CAP-50.e, CAP-50.f, CAP-50.g |
| CAP-51 | Decisions register (structured, versioned, authoritative) | 2/0/0/0 | W1: 2 built and closed |
| CAP-52 | Model-agnostic adapters (provider, IDE, CLI) | 2/0/0/0 | W1: 2 built and closed |
| CAP-53 | Proportionality profiles (LITE/STANDARD/FULL) | 2/1/0/0 | W1: 2 built and closed; CAP-53.b: W2-38: planned (not started) |
| CAP-54 | Progressive adoption (day-one to maturity) | 2/0/0/0 | W1: 2 built and closed |
| CAP-55 | Retrieval stopping reasons | 1/0/0/0 | W1: 1 built and closed |
| CAP-56 | Retrieval in disposable subagent context | 1/0/0/0 | W1: 1 built and closed (CAP-56.a WEAKENED at W1-43) |
| CAP-57 | Deterministic worklist closure for facets | 1/0/0/0 | W1: 1 built and closed |
| CAP-58 | Path guards as default-deny allow-lists | 7/0/1/0 | W1: 7 built and closed (CAP-58.c WEAKENED at W1-43); W3: CAP-58.g |
| CAP-59 | Review-repair loop budget | 3/0/0/0 | W1: 3 built and closed (CAP-59.a, CAP-59.b WEAKENED at W1-43) |
| CAP-60 | Below-floor recovery (break-glass) | 0/0/0/1 | NONE: CAP-60.a |
| CAP-61 | Worker session launcher and OS sandbox | 5/1/0/0 | W1: 5 built and closed; CAP-61.f: W2-40: planned (not started) |
| CAP-62 | Sandbox escape hatch denied | 1/0/0/0 | W1: 1 built and closed |

**The master rules.**

| Master rule | W1-43 class, and why | Wave 2 work and its state |
|---|---|---|
| MR-1 Specification comes first | OK | — |
| MR-2 Closed specifications generate the work | OK | Its Wave 2 part, `gov readiness --generate`, is W2-34's. W2-34 closes MR-2 and CAP-30.c; planned. |
| MR-3 KPIs; the builder never writes its own acceptance tests | OK | — |
| MR-4 Audit, discovery and impact are distinct functions | WEAKENED: FULL tickets W1-16 and W1-21 have no probe or review record, and W1-42 has none (F-M11). | Accepted as named exceptions: row W2-C042, DEC-718 item 7. |
| MR-5 The Gov OS works as a software company | WEAKENED: ticket leads still run in the orchestrator role (DEC-434 not built), and the main session records its writes under a closed ticket. | Rows W2-H001 and W2-M291, both triaged to W2-21 (planned). The Charter's eight further Wave 2 roles: nowhere (F5). |
| MR-6 The human is the customer and final authority | WEAKENED: owner approvals are transcribed, not owner git facts (F-M6); three pushes and a hook reinstall are not recorded (F-M9); W1-30 closed past an escalation stop (DEC-651). | AR-7 (W2-12, planned). F-M9's row W2-L338 is carried to Wave 3. |

### 2.3 Where the scope drifted, what is missing, and what is surplus

**Drift.**
- **From Contract items to the Gov OS's own machinery** (F2). Seven tickets were added during Wave 2, and six of them repair or enable the machinery. The twelve tickets built so far added about twice their estimated code, and about 8 lines of tests for each line of code. Review rounds kept being driven by findings that need a deliberate construction. That went on until the owner re-anchored every review on ADR-0001's threat model on day four (DEC-801 to DEC-809).
- **From delivering to closing** (F1). Work is built faster than it can be closed.
- **From the pilot's planned path** (F3). The EXAMIN copy now waits behind the Track A gate run (W2-24) and two new tickets.
- **From the size the owner approved** (F6).

**Missing.**
- A clean `gov close`: the proof that AR-8 and exit criterion 1 require (F1).
- Eight Wave 2 roles named in the Charter (F5).
- The per-wave size review (F6).
- A plan with dates for UPIM and ASMO, for Wave 3 and for Release 1 (F3).
- The validator's check of "delivered by a closed ticket" (F4).
- Several records (F8, F9):
  - ticket files for W2-55, W2-56 and W2-57;
  - CAP-44.f in some ticket's `closes` field;
  - triage lines for 49 rows;
  - W2-27's dependencies on W2-24's check and on W2-56.

**Surplus.** This is work beyond the Contract's Wave 2 items. None of it is waste in itself.
- **Built ahead of the Contract's wave:**
  - parts of CAP-43.d on W2-16, which the Contract's wave note allows;
  - parts of CAP-39.c in W2-38 and W2-48, both planned. They serve the cost of closes (DEC-567, DEC-726).
- **Enablers and repairs that are not Contract items.** Each is traced to a decision:
  - W2-20: the machine-wide resource gate.
  - W2-50: the durable scratch root (DEC-728).
  - W2-51: the plan validator (DEC-744).
  - W2-53: the probe gate's merge measure, the ratchet and the quarantine (DEC-757).
  - W2-54: the context packet's order and the context check's time limit (DEC-768).
  - W2-55: decision tagging (DEC-791).
  - W2-56: `gov launch` for every worker (DEC-799).
  - W2-57: W1-46's live cases under load (DEC-813).
- **Tests.** The twelve tickets built so far added about 28,500 lines of tests against about 3,600 lines of code. The suite's size (153,124 lines of Python tests on `w2/integrate`, about 13,500 tests) is why a close takes an hour (F1, F6).

## 3. Findings

### F1. No ticket has yet closed through a clean `gov close`, and the close step now holds up all delivery

**Evidence.**
- **What the plan requires.**
  - Exit criterion 1 (WBS §5, line 951): "Every Wave 2 ticket in this repository closes through a clean `gov close` … A ticket closed any other way is a named failure of this criterion."
  - AR-8 (list, line 120) asks for the first such close. It is the proof missing from Wave 1, where W1-43's F-M3 found that "no Wave 1 ticket of this repository closed through a clean `gov close`. All seven closes after `1c33dd28` used `tk close` under owner decisions" (list, line 122).
- **W2-01.** Its `gov close` was refused with six findings (`log/W2-01-close.json`, CHECK_FAILED):
  - a probe record made invalid by a later edit;
  - W1-42's two red tests;
  - a W1-05 timing case;
  - a stale checkpoint;
  - a failed context check.

  The owner then closed it with `tk close`, as "the one named exception to exit criterion 1" (DEC-757 item 1).
- **W2-53.** It builds the ratchet and the quarantine. It was merged (`c9537e39`) so that it could close next, alone. Its close was refused twice:
  - STORE_STALE (`log/close-DAEO-7rr2-2.json`);
  - CHECK_FAILED at 12:01 on 2026-10-19 (`log/close-DAEO-7rr2-3.json`). 13,454 tests passed and 3 failed: the two accepted reds, and W1-30's `test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project`. That test "alone 3/3 pass, 17.8 s; 2 s reaping margin" (orchestrator checkpoint, lines 27–30). The regression ran 1,876 s in parallel plus 1,642 s in series.
- **The rules leave no quick way out, by design.**
  - A re-close without a change is a forbidden ratchet retry.
  - Adding the W1-30 case to the quarantine needs an owner package and an owner commit (DEC-766).
  - That package, P-W2-47, is on hold for this assessment. It "Blocks W2-53's re-close and every close behind it" (checkpoint, lines 44–45).
- **The quarantine already holds 27 entries** (DEC-766: "`load_sensitive` grew from 26 to 27"). 23 of them are W1-46's live-session cases. These raised setup errors in a full run "at load about 25" (DEC-813), and they stay listed until W2-57.
- **The countdown** (checkpoint, line 26): "1/55 closed (W2-01). Merged not closed: W2-53, W2-54. Running 0. Idle 1 (W2-05). Held 10. Not started 41." So thirteen tickets are built and waiting in the close order of DEC-806.
- **Much else waits on closes:**
  - The hooks come back only after W2-01, W2-02, W2-05 and W2-06 land (WBS §0 rule 4), so the commit-time checks and the pre-push gate stay off.
  - Exit criterion 7 counts an item only when it is "delivered by a closed ticket".
  - W2-48 is the test-result cache that "takes the close queue off the critical path from layer 3 on" (WBS §3). It waits too: it starts after W2-53 closes and after W2-21 (DEC-780).
- **The plan assumed closes pass.** WBS §4 costs closes at "≈ 7 hours over layers 1 and 2", one hour each.
- **The machine is shared.** The 1-minute load was 22 to 23 during this assessment, with five auditors running.

Ordinary work: yes, because an ordinary close runs the full regression on a shared, loaded machine, and that is enough to fail a timing-sensitive test, as W2-53's close shows.
Consequence: other. The close fails closed: it refuses, which is safe. But no Wave 2 work can count as delivered until closes pass.
Severity: high. It holds back every exit criterion that needs a closed ticket, and it repeats Wave 1's F-M3.

### F2. Wave 2's effort has gone mostly into the Gov OS's own machinery, at a high cost in rounds and owner decisions

**Evidence.**
- **Contract work.** Of the 20 Wave 2 Contract items, 4 are built, on W2-16, W2-37 and W2-52. None of the 12 tickets that hold the other 16 has started (Appendix A).
- **New tickets.** By my count of ticket ids in the WBS ticket table, it listed 52 at the plan's approval (`7d60dec6`: W2-00 to W2-50, with W2-15 as W2-15a and W2-15b) and lists 58 now: W2-51 to W2-56 were added. W2-57 also has a staged card (DEC-813). Of the seven tickets added:
  - one builds a Contract item: W2-52, CAP-44.f;
  - six repair or enable the machinery: W2-51 (DEC-744), W2-53 (DEC-750, DEC-754, DEC-757), W2-54 (DEC-768), W2-55 (DEC-791), W2-56 (DEC-799) and W2-57 (DEC-813).
- **Size against the estimates**, for the twelve tickets built so far:

| Ticket | State | Estimate (lines) | Code lines added | Test lines added |
|---|---|---|---|---|
| W2-01 | closed by owner decision (DEC-757) | 180 | 294 | 2,445 |
| W2-02 | held | 160 | 167 | 1,481 |
| W2-03 | held, stacked on W2-02 | 160 | 134 | 1,202 |
| W2-05 | held (idle) | 140 | 163 | 2,088 |
| W2-16 | held, stacked on W2-49 | 150 | 483 | 2,667 |
| W2-20 | held | 120 | 239 | 1,016 |
| W2-37 | held, stacked on W2-03 | 280 | 487 | 2,543 |
| W2-50 | held | 120 | 519 | 5,472 |
| W2-51 | held | 120 | 276 | 1,213 |
| W2-52 | held, stacked on W2-49 | 100 | 292 | 1,598 |
| W2-53 | merged | 40, raised to 160 by DEC-757 | 370 | 1,857 |
| W2-54 | merged | 120 | 180 | 4,885 |
| **Total** | | **1,810** | **3,604** | **28,467** |

  "Code" means lines added under `src/`, `template/`, `docs/plan/tools/` and `.rulesync/`, and in `copier.yml`. For a stacked branch, its base's lines are subtracted. W2-49 (a specification ticket with an estimate of 0) and W2-26 (research) are not in the table. The plan's upper range allows 30 % for overruns (WBS §4). The code came in at about twice the estimate, with about 8 lines of tests for each line of code.
- **Rounds.**
  - W2-50 is the scratch-root ticket, estimated at 120 lines. It has review records for seven runs (`log/W2-50-A5-run1.json` to `run7b.json`). DEC-758 named its fifth run "W2-50's last round", and DEC-778 said "W2-50's run 7 is its last". It is still held, with a failed probe record and a resume probe due (checkpoint, line 35).
  - W2-01 went through four rounds (DEC-750: "a fourth and last round, then closes or splits"), a split (DEC-754) and an exception close (DEC-757).
  - DEC-801 names the cause: "W2-50's run-7 review and W2-05's second review raised findings that need a deliberate construction."
- **ADR-0001 foresaw this** (line 30): "Machinery against an adversary the design cannot stop produces endless review loops." The threat model went into every review brief only on day four, 2026-10-19 (DEC-801 to DEC-809). That is a sound correction, but it came after most of the rounds.
- **The owner's load.**
  - Between 2026-10-16 and 2026-10-19 the register gained 99 decisions (DEC-719 to DEC-817), and owner packages were numbered up to P-W2-47.
  - Of the 131 commits on `w2/integrate` since `main`, 88 carry `Role: orchestrator` (records, decisions and merges), 19 engineer, 14 test designer and 10 owner.
  - The owner's new package format, to be recorded as DEC-818 (checkpoint, lines 48–49), starts from the fact that the owner and an outside adviser may lack context.

Ordinary work: yes, because the rounds and the new tickets came out of ordinary reviews of ordinary tickets, not out of anything deliberate.
Consequence: other. The cost is time, owner attention and size. Nothing fails open.
Severity: high for the roadmap. At this rate the plan's 21 to 27 working days will not hold, and the products' payoff (F3) moves with them.

### F3. The products wait: only EXAMIN has a pilot, its path has grown longer, and UPIM and ASMO have no date

**Evidence.**
- **What the purpose and the Charter say.**
  - The owner's purpose includes building EXAMIN, UPIM and ASMO faster and more safely.
  - Charter §1 (lines 32–36) allows "a single pilot adoption in Wave 2 (EXAMIN …)", and "Every other product repository waits for Release 1."
  - DEC-064 superseded DEC-043, "Products resume immediately" (register, line 753).
- **UPIM and ASMO.** They are named nowhere in the Charter, the Contract, the ADRs or the Wave 2 plan. The register names them once, in DEC-567 (line 6124): "language-agnostic test commands are a must-have before the Gov OS is adopted in any non-Python repository (UPIM, ASMO)". W2-19 builds those commands; it is planned and not started.
- **Release 1.** It needs Wave 3 (38 items, no tickets yet; WAVE_1_WBS §7) and qualification on two synthetic programmes (CAP-49.a, a Wave 3 item). No size or date for Wave 3 is recorded.
- **The pilot's path.**
  - WBS §3: "The copy's verdict comes at ≈ day 13", by way of W2-01 → W2-49 → W2-16 → W2-18 → W2-23 → W2-27 → W2-28.
  - Three later decisions put the copy behind more work:
    - DEC-794: W2-27 "does not start unless W2-24's repeat of the quality-control check gives sections (a) and (d) green".
    - DEC-799: "and W2-56 has closed".
    - DEC-813, staged: "W2-24 does not start before W2-57 has closed".
  - W2-24 is the Track A gate run. It has 27 dependencies and sits in layer 6 of the plan's 11 layers. WBS §3's estimate of day 13 has not been updated.
- **The real repository.** Its verdict (W2-30) comes after W2-29, W2-25 and W2-15b, in layer 9 of 11 (WBS §3 table). WBS §4 puts it at day 18 to 23.

Ordinary work: no, because this is a roadmap matter set by owner decisions, not a fault that an agent hits in its work.
Consequence: other. The product payoff of the purpose is deferred.
Severity: high, measured against the purpose. The products are where the Gov OS pays back, and none is governed yet.

### F4. The plan validator for exit criterion 7 checks less than the criterion asks, and can pass undelivered items

**Evidence.**
- **What the criterion asks.** Exit criterion 7 (WBS, line 965) asks that each Wave 2 item and each lite item be "delivered by a closed ticket and cited by an acceptance test. The plan validator checks this both ways."
- **"Delivered" is checked without the ticket's state.** W2-51's KPI asks only that each item be "delivered by a Wave 2 ticket" (the W2-51 card); the word "closed" has gone. The validator (`docs/plan/tools/validate_w2.py` at `c2c80e6c`, `check_delivered`, lines 169–173) counts an item as delivered when any Wave 2 ticket's `closes` field names it, whatever that ticket's state. On `fecb870c` it prints "PASS contract-items-delivered", "17 Wave 2 items, each in a Wave 2 ticket's closes", although none of those tickets is closed.
- **"Cited" is checked against any file, READMEs included.** The citation check (`acceptance_citations`, lines 142–151) counts any mention in any file under `tests/acceptance/`. Three Wave 2 items count as cited only through Wave 1 README text that says they are Wave 2 work:
  - CAP-17.b: `tests/acceptance/W1-17/README.md:152`, "the commit-time hook (CAP-17.b, Wave 2)";
  - CAP-30.c: `tests/acceptance/W1-13/README.md:299`, "`gov readiness --generate` (Wave 2, CAP-30.c)";
  - CAP-61.f: `tests/acceptance/W1-46/README.md:550` and `:562`.
- **Two more on the v4.2 tree.** With the held branches' acceptance folders in place, two more items count as cited without a test of their own behaviour:
  - CAP-53.b counts only through W2-37's README, which says "The profile from the radius is W2-38's (CAP-53.b)" (`tests/acceptance/W2-37/README.md:219`).
  - CAP-45.a (`gov update`) counts only through W2-49's test of the Contract's wording, which asserts that the item's wave is W2 (`tests/acceptance/W2-49/test_w2_49_owner_answers.py:188–189`).
- **My runs.**
  - On `fecb870c`: "RESULT: 4 FAIL, 5 NOT RUN". The citation check lists 14 of the 17 items as uncited. None of the 17 has a test there, and the other three pass through README text.
  - On the v4.2 tree: 5 FAIL, with CAP-44.f undelivered and 10 items uncited. Of the 10 items counted as cited, five rest on README text or a wording test: CAP-17.b, 30.c, 61.f, 53.b and 45.a.
- **The fix has a place.** W2-51 is held, with profile STANDARD, and can take the fix in its resume.

Ordinary work: yes, because the validator is the routine check for exit criterion 7. A README that mentions an item is ordinary, and so is a ticket that names an item in `closes` and has not closed.
Consequence: fails open. It gives a PASS for an exit criterion that is not met.
Severity: medium. The exit audit (W2-47) is a second check, but the plan names the validator as the check.

### F5. Eight Wave 2 roles in the Charter have no Contract item, ticket or row

**Evidence.**
- **The Charter.** Charter §6 (line 164) puts in Wave 2: "architecture · frontend · backend · database/data · integration/API · test execution · integration · DevOps/SRE · security · performance · UX; typed handoffs (DEC-094)". MR-5, "The Gov OS works as a software company" (Charter §4, lines 110–112), names these roles among its role agents.
- **The Contract.** Contract v4.2 carries Wave 2 role work only as CAP-22.b (typed handoff records) and CAP-22.c (distinct test-execution and integration roles, DEC-094). Its CAP-22 wave note reads "specialist roles, including test execution and integration (DEC-094), are W2".
- **The plan.** W2-33's KPIs cover test-execution and integration roles, a UX role (W2-M322) and typed handoffs. No ticket, KPI or row names an architecture, frontend, backend, database/data, integration/API, DevOps/SRE, security or performance role. WAVE_1_WBS §6's outline of Wave 2 says "specialist roles".
- **No recorded decision.** No decision drops or defers these eight roles.

Ordinary work: no, because this is a gap between the Charter and the plan, not something an agent hits in its work.
Consequence: other. Part of the Charter's Wave 2 scope is not built, and nothing records a decision to drop or defer it.
Severity: medium. For product work these roles are what makes a "software company" more than one engineer role. DEC-105's three options apply: apply now, defer or re-baseline.

### F6. The per-wave size review set by DEC-064 was never held, and the code is about three times the estimate for all three waves

**Evidence.**
- **The rule.**
  - DEC-064 (register, line 440): "DEC-001's ~3k-line revisit trigger becomes a per-wave review (glue ≈ 4.5k LOC across three waves)."
  - WAVE_1_WBS (line 167): "DEC-064 makes the size check a per-wave review, not a stop." ADR-0002 also lists the per-wave glue review as a revisit trigger.
- **The estimate.** WAVE_1_WBS (line 153) put Wave 1's glue code at "≈ 5,680 LOC".
- **The measured size.**
  - At Wave 1's exit (`main`), `src/gov` has 110 Python files with 16,834 lines, of which 13,891 are code lines (my count). The Python tests have 145,505 lines.
  - `w2/integrate` adds 788 lines of source and 9,184 lines of tests so far. The held branches add more (F2's table). The Wave 2 plan adds ≈ 7,100 lines on top (WBS §4).
- **No review on record.** No size review appears in the Wave 1 exit report, the W1-43 audit or the Wave 2 WBS. I searched them for "glue", "per-wave" and "size review".

Ordinary work: yes, because the review was simply left out of the ordinary writing of the Wave 1 exit and the Wave 2 plan.
Consequence: other. Nothing fails open, but the owner has had no decision point on size.
Severity: medium. Size drives the hour-long regression (F1) and the review rounds (F2).

### F7. Twelve Wave 1 items count as delivered but were found weakened, and most of their repairs have not started

**Evidence.**
- **What W1-43 found.** It found "All 149 W1 covers items are delivered and cited by an acceptance test", but it classed 25 of its 197 rows WEAKENED. Among them:
  - CAP-01.b and CAP-21.a: approvals as owner git facts.
  - CAP-15.d: "packet ceiling not held: 814821 tokens against 6000".
  - CAP-17.c: "canaries miss on this repository".
  - CAP-25.a: "doctor false failure on pytest-xdist".
  - CAP-40.c: "governance share not per programme".
  - CAP-56.a: "acceptance sentence untested".
  - CAP-58.c: "guard known-tool list lacks SubagentHandback".
  - CAP-59.a and CAP-59.b: untested.
  - CAP-06.d and CAP-39.a.
  - CAP-10 at capability level: hit@5 of 83.33 against the Contract's 85, and "the contract is not re-baselined".
  - MR-4, MR-5 and MR-6.
- **The repairs.** DEC-718 accepted Wave 1 with these exceptions and named the AR block as their repairs. The AR tickets stand as follows:
  - W2-01: closed, by exception.
  - W2-02, W2-03 and W2-05: held.
  - Not started: W2-04, W2-06 to W2-15b, W2-17, W2-19, W2-21 and W2-24.
  - AR-8, the first clean close, is unmet (F1).
- **In the map.** Appendix A shows these 12 items as "built and closed", which is true by the record. Each is marked "W1-43: WEAKENED".

Ordinary work: yes, because agents rely on these items in ordinary work: the context packet, the approval facts, the guard's tool list.
Consequence: other. W1-43 found these items weakened, not missing, and the guard item fails closed (it refuses SubagentHandback).
Severity: medium. The weakened items touch two of the purpose's aims: memory (CAP-15.d, CAP-17.c, CAP-10) and the owner's control (CAP-01.b, CAP-21.a, MR-6).

### F8. The plan's records are out of step with the decisions and with each other

**Evidence.**
1. **Missing ticket files.** W2-55, W2-56 and W2-57 are decided (DEC-791, DEC-799, and the staged DEC-813) but have no ticket file in `.tickets/`. The validator fails on W2-55 and W2-56, which are "in the WBS table only". W2-57 has a card but no table row.
2. **`closes` fields.**
   - CAP-44.f is in no ticket's `closes`. The WBS table gives it to W2-52 (line 124), but W2-52's ticket file says `closes: [DEC-741 (H)]`. On the v4.2 tree the validator fails: "no Wave 2 ticket delivers: CAP-44.f".
   - W2-16's `closes` is split at a comma into two entries, "CAP-43.b (lite" and "DEC-722)".
3. **The list's counts.** The list's §3 text (line 181) says "849 are open, 62 of them high, 383 medium and 361 low". With the 41 info rows that adds up to 847, and my parser also counts 847 open rows. The section headings still say high (60), medium (367) and low (354). The validator fails on the headings.
4. **The triage.** 49 rows added during Wave 2 have no line in the triage: W2-H056 to W2-H062, W2-M360 to W2-M383, and W2-L344 to W2-L361. The triage's stated counts differ from its rows: 88 Wave 3 stated against 89 rows, and 169 backlog stated against 168 rows. Exit criterion 10 asks for the triage "kept current".
5. **No row is marked closed.** W2-01 closed on 2026-10-17 with 13 rows triaged to it. The list's rule (line 30) is: "An item that closes is marked **closed** with its commit."
6. **The prompt's cap.** The Wave 2 orchestrator prompt §3 (line 30) still allows "up to 6" tickets in flight. DEC-776 and WBS §0 rule 14 cap it at 3.
7. **Statuses.**
   - ADR-0001 and ADR-0002 still say `status: PROPOSED`, yet ADR-0001 is now the standard every review applies (DEC-801). Row W2-C039 closed the same issue for the Charter, the Contract and the WBS. No row names the ADRs.
   - On `w2/integrate`, `contract.yaml` says PROPOSED while `CONTRACT_v4.md` says ACCEPTED. Row W2-L343 tracks this, and it is fixed on the held W2-49.
8. **The Charter's front matter.** Its `decisions:` list ends at DEC-173. Yet §1 was amended by DEC-740 (owner commit `cf4ce2b8`) and now cites DEC-718 and DEC-727.
9. **The WBS's own counts.** Its ids note (line 39) still says Wave 2 tickets are "W2-00 to W2-50", and its totals (line 155) still say "51 tickets plus the coordination ticket W2-00". Its §4 summary (line 937) says "53 + W2-00". Its ticket table lists 57 tickets plus W2-00, and `.tickets/` holds 55 plus W2-00.

Ordinary work: yes, because each gap comes from an ordinary edit: a decision recorded without its ticket file, a count not carried over, a row not triaged.
Consequence: other. The validator catches some of these, and it fails, which is closed. The rest mislead a reader rather than open a gate.
Severity: low. But these gaps make the plan harder for an outside reader to trust, and the validator's FAILs on them hide the real gap in F4.

### F9. W2-27's recorded dependencies miss two of the owner's conditions

**Evidence.**
- **The conditions.** W2-27 (EXAMIN adoption on a copy) has 18 dependencies in its ticket file. The WBS card (lines 689–690) and the register add two conditions:
  - DEC-794: "W2-27 does not start unless W2-24's repeat of the quality-control check gives sections (a) and (d) green";
  - DEC-799: "and W2-56 has closed".
- **The gap.** Neither W2-24 nor W2-56 is among W2-27's dependencies, and W2-56 has no ticket file to depend on.
- **How tickets are started.** The orchestrator prompt §3 (line 30) starts tickets "chosen so that each one's dependencies are closed".

Ordinary work: yes, because starting the next ticket whose dependencies are closed is the orchestrator's ordinary routine.
Consequence: fails open. The dependency check would pass W2-27 before the sandbox and retrieval checks are green. Only a reader of the card or the register would hold it back.
Severity: low. W2-27 works on a throwaway copy, and the card states the conditions.

## 4. Recommendations

1. **Make one clean `gov close` the next milestone, ahead of any new start** (F1, F2).
   - Decide P-W2-47.
   - Then put one owner decision on how closes stop depending on the machine's load. Two possible routes: a quiet-window close with the resource gate applied to the close itself, or timing-sensitive cases run as their own isolated suite.
   - Bring W2-48 (the test-result cache) forward, since it shortens every later close.
   - Report the close success rate in the countdown.
2. **Hold DEC-064's per-wave size review now** (F6, F2). Measure the size of Wave 1 and of Wave 2 so far against DEC-064's estimate. Include the test-to-code ratio and the cost of a close and of a round. Then decide whether to re-baseline the Wave 2 plan's scope and duration, using DEC-105's three options.
3. **Admit a new ticket only when it serves an exit criterion or a Contract item, and record which** (F2). Keep applying DEC-801's threat model to each held ticket's open findings before its resume.
4. **Make the products' timeline an owner decision** (F3). It should cover:
   - when UPIM and ASMO are adopted, and what each needs first (W2-19's language-agnostic test commands for both);
   - a date range for Release 1, with Wave 3's size;
   - whether the EXAMIN copy can get back to its earlier path.

   Update WBS §3's estimate for the copy after DEC-794, DEC-799 and DEC-813.
5. **Fix the validator in W2-51's resume** (F4, F8).
   - "Delivered" should mean a closed ticket that names the item in `closes`.
   - A citation should count only in a test file, not in a README.
   - Then add CAP-44.f to W2-52's `closes`, and re-run the validator on Contract v4.2 once W2-49 merges.
6. **Put the Charter's eight missing Wave 2 roles to the owner as a DEC-105 package** (F5). The options: apply now (Contract items and a ticket), defer to Wave 3, or re-baseline the Charter's wave table by a CIT-P.
7. **Show the 12 weakened Wave 1 items and CAP-10's re-baseline in the countdown** (F7), each with its repairing ticket and that ticket's state.
8. **Repair the records in one orchestrator pass** (F8, F9):
   - ticket files for W2-55 to W2-57, with their dependencies;
   - W2-56 and W2-24's check added to W2-27's dependencies;
   - the WBS's ids note, its totals and its §4 summary;
   - the list's counts and headings;
   - triage lines for the 49 rows;
   - W2-01's rows marked;
   - the in-flight cap in prompt §3;
   - the ADRs' status, or a row for it;
   - the Charter's front matter.

## Appendix A. Contract v4.2: one row per item (214 rows)

States: **built and closed** (Wave 1 tickets, all closed; "W1-43: WEAKENED" where the Wave 1 exit audit said so); **held** (built on a ticket branch that is not merged); **planned (not started)**; **Wave 3 (not in Wave 2)**; **not built (NONE)**. No Wave 2 item is merged or closed. "Wave 2 tickets": tickets whose `closes` names the item, then, after "/", tickets whose file or WBS card cites it. "Acceptance folders": `tests/acceptance/W2-xx/` on that ticket's branch head. "List rows naming it": rows whose text has the item's id, with their triage after the arrow. "List rows on the closing ticket": the `list_rows` of the ticket that closes the item.

| Item | Wave | Wave 1 provider | Wave 2 tickets (closes / cites) | Wave 2 acceptance folders citing it | List rows naming it (→ triage) | List rows on the closing ticket | State |
|---|---|---|---|---|---|---|---|
| CAP-01.a | W1 | W1-24 | — | W2-02 | — | — | built and closed (W1-24) |
| CAP-01.b | W1 | W1-11 | — | — | — | — | built and closed (W1-11); W1-43: WEAKENED |
| CAP-01.c | W1 | W1-26 | — | — | — | — | built and closed (W1-26) |
| CAP-01.d | W1 | W1-24 | — | — | — | — | built and closed (W1-24) |
| CAP-02.a | W1 | W1-39, W1-27 | — | W2-16 | — | — | built and closed (W1-39, W1-27) |
| CAP-02.b | NONE | — | — | — | — | — | not built (NONE: non-goal or drop) |
| CAP-02.c | W3 | — | — / W2-16, W2-49 | W2-16, W2-49 | W2-H029→W2-16 | — | Wave 3 (not in Wave 2); cited by W2-16, W2-49 |
| CAP-03.a | W1 | W1-15, W1-08 | — | — | — | — | built and closed (W1-15, W1-08) |
| CAP-03.b | W1 | W1-15, W1-08 | — | — | — | — | built and closed (W1-15, W1-08) |
| CAP-03.c | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-03.d | W1 | W1-17 | — | — | — | — | built and closed (W1-17) |
| CAP-03.e | W1 | W1-16, W1-15 | — | — | — | — | built and closed (W1-16, W1-15) |
| CAP-04.a | W2 | — | W2-31 | — | — | W2-31: 0 | W2-31: planned (not started) |
| CAP-04.b | W1 | W1-31 | — | — | — | — | built and closed (W1-31) |
| CAP-04.c | W1 | W1-21 | — | — | — | — | built and closed (W1-21) |
| CAP-04.d | W2 | — | W2-31 | — | — | W2-31: 0 | W2-31: planned (not started) |
| CAP-05.a | W1 | W1-28 | — | — | — | — | built and closed (W1-28) |
| CAP-05.b | W1 | W1-28 | — | — | — | — | built and closed (W1-28) |
| CAP-05.c | W1 | W1-28 | — | — | — | — | built and closed (W1-28) |
| CAP-05.d | W1 | W1-28 | — | — | — | — | built and closed (W1-28) |
| CAP-06.a | W1 | W1-27, W1-08 | — | — | — | — | built and closed (W1-27, W1-08) |
| CAP-06.b | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-06.c | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-06.d | W1 | W1-41, W1-27 | — | — | — | — | built and closed (W1-41, W1-27); W1-43: WEAKENED |
| CAP-06.e | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-07.a | W1 | W1-27 | — | — | — | — | built and closed (W1-27) |
| CAP-07.b | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-08.a | W1 | W1-10 | — | — | W2-L085→Wave 3, W2-L234→Wave 3, W2-L274→backlog | — | built and closed (W1-10) |
| CAP-09.a | W1 | W1-10 | — | — | — | — | built and closed (W1-10) |
| CAP-09.b | W1 | W1-10 | — | — | — | — | built and closed (W1-10) |
| CAP-10.a | W1 | W1-19 | — | — | — | — | built and closed (W1-19) |
| CAP-10.b | W2 | — | W2-32 | — | — | W2-32: 11 (W2-L029, W2-L065, W2-L066, W2-L068, W2-L239, W2-M001, W2-M073, W2-M103, W2-M104, W2-M191, W2-M341) | W2-32: planned (not started) |
| CAP-11.a | W1 | W1-17 | — | — | — | — | built and closed (W1-17) |
| CAP-12.a | W1 | W1-16 | — | — | — | — | built and closed (W1-16) |
| CAP-12.b | W1 | W1-16 | — | — | — | — | built and closed (W1-16) |
| CAP-13.a | W1 | W1-10, W1-30 | — | — | — | — | built and closed (W1-10, W1-30) |
| CAP-13.b | W1 | W1-25 | — | — | — | — | built and closed (W1-25) |
| CAP-14.a | W1 | W1-21 | — | — | — | — | built and closed (W1-21) |
| CAP-15.a | W1 | W1-24 | — | — | — | — | built and closed (W1-24) |
| CAP-15.b | W1 | W1-24 | — | — | — | — | built and closed (W1-24) |
| CAP-15.c | W1 | W1-24 | — | — | — | — | built and closed (W1-24) |
| CAP-15.d | W1 | W1-24 | — / W2-04 | — | — | — | built and closed (W1-24); W1-43: WEAKENED |
| CAP-15.e | W1 | W1-24 | — | — | — | — | built and closed (W1-24) |
| CAP-15.f | W1 | W1-23 | — | — | — | — | built and closed (W1-23) |
| CAP-15.g | W1 | W1-24, W1-29 | — | — | — | — | built and closed (W1-24, W1-29) |
| CAP-16.a | W1 | W1-21 | — | — | — | — | built and closed (W1-21) |
| CAP-16.b | W1 | W1-36, W1-21 | — | — | — | — | built and closed (W1-36, W1-21) |
| CAP-16.c | W1 | W1-21 | — | — | — | — | built and closed (W1-21) |
| CAP-17.a | W1 | W1-17 | — | — | — | — | built and closed (W1-17) |
| CAP-17.b | W2 | — | W2-06 | — | W2-H039→W2-06, W2-H041→W2-06 | W2-06: 19 (W2-H039, W2-H040, W2-H041, W2-L056, W2-L103, W2-L330, W2-M011, W2-M040, W2-M045, W2-M070, W2-M088, W2-M099, W2-M125, W2-M143, W2-M210, W2-M243, W2-M282, W2-M293, W2-M295) | W2-06: planned (not started) |
| CAP-17.c | W1 | W1-22 | — | — | — | — | built and closed (W1-22); W1-43: WEAKENED |
| CAP-18.a | W1 | W1-19, W1-21 | — | — | — | — | built and closed (W1-19, W1-21) |
| CAP-18.b | W1 | W1-17, W1-21 | — | — | — | — | built and closed (W1-17, W1-21) |
| CAP-19.a | W2 | — | W2-32 | — | — | W2-32: 11 (W2-L029, W2-L065, W2-L066, W2-L068, W2-L239, W2-M001, W2-M073, W2-M103, W2-M104, W2-M191, W2-M341) | W2-32: planned (not started) |
| CAP-19.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-19.c | W2 | — | W2-32 | — | — | W2-32: 11 (W2-L029, W2-L065, W2-L066, W2-L068, W2-L239, W2-M001, W2-M073, W2-M103, W2-M104, W2-M191, W2-M341) | W2-32: planned (not started) |
| CAP-20.a | W1 | W1-27, W1-25 | — | — | — | — | built and closed (W1-27, W1-25) |
| CAP-21.a | W1 | W1-11 | — | — | — | — | built and closed (W1-11); W1-43: WEAKENED |
| CAP-21.b | NONE | — | — | — | — | — | not built (NONE: non-goal or drop) |
| CAP-22.a | W1 | W1-05, W1-33 | — | — | — | — | built and closed (W1-05, W1-33) |
| CAP-22.b | W2 | — | W2-33 | — | — | W2-33: 6 (W2-L250, W2-L251, W2-L252, W2-M084, W2-M085, W2-M321) | W2-33: planned (not started) |
| CAP-22.c | W2 | — | W2-33 | — | — | W2-33: 6 (W2-L250, W2-L251, W2-L252, W2-M084, W2-M085, W2-M321) | W2-33: planned (not started) |
| CAP-22.d | W1 | W1-46 | — | — | — | — | built and closed (W1-46) |
| CAP-23.a | W1 | W1-09 | — | — | — | — | built and closed (W1-09) |
| CAP-23.b | W3 | — | — | — | W2-I019→Wave 3 | — | Wave 3 (not in Wave 2) |
| CAP-23.c | W1 | W1-42 | — | — | — | — | built and closed (W1-42) |
| CAP-24.a | W1 | W1-35, W1-30 | — | — | — | — | built and closed (W1-35, W1-30) |
| CAP-24.b | W1 | W1-35, W1-36 | — | — | — | — | built and closed (W1-35, W1-36) |
| CAP-24.c | W1 | W1-35, W1-26 | — | — | — | — | built and closed (W1-35, W1-26) |
| CAP-25.a | W1 | W1-04, W1-06, W1-27 | — | — | — | — | built and closed (W1-04, W1-06, W1-27); W1-43: WEAKENED |
| CAP-25.b | W1 | W1-04 | — | — | — | — | built and closed (W1-04) |
| CAP-25.c | NONE | — | — | — | W2-M025→Wave 3, W2-M026→Wave 3, W2-M034→Wave 3 | — | not built (NONE: non-goal or drop) |
| CAP-25.d | W1 | W1-48 | — | — | — | — | built and closed (W1-48) |
| CAP-25.e | W1 | W1-46 | — | — | — | — | built and closed (W1-46) |
| CAP-25.f | W1 | W1-47 | — | — | — | — | built and closed (W1-47) |
| CAP-25.g | W1 | W1-47 | — | — | — | — | built and closed (W1-47) |
| CAP-26.a | NONE | — | — | — | — | — | not built (NONE: non-goal or drop) |
| CAP-27.a | W1 | W1-07, W1-32 | — | — | — | — | built and closed (W1-07, W1-32) |
| CAP-27.b | NONE | — | — | — | — | — | not built (NONE: non-goal or drop) |
| CAP-28.a | W1 | W1-32, W1-35 | — | — | — | — | built and closed (W1-32, W1-35) |
| CAP-28.b | W1 | W1-07, W1-42 | — | — | — | — | built and closed (W1-07, W1-42) |
| CAP-29.a | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-29.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-30.a | W1 | W1-12, W1-13 | — | — | — | — | built and closed (W1-12, W1-13) |
| CAP-30.b | W1 | W1-13, W1-26, W1-35 | — | — | — | — | built and closed (W1-13, W1-26, W1-35) |
| CAP-30.c | W2 | — | W2-34 | — | — | W2-34: 25 (W2-H015, W2-H051, W2-L053, W2-L164, W2-L245, W2-L246, W2-L247, W2-M050, W2-M052, W2-M074, W2-M075, W2-M076, W2-M077, W2-M078, W2-M079, W2-M080, W2-M081, W2-M082, W2-M083, W2-M207, W2-M274, W2-M283, W2-M302, W2-M303, W2-M305) | W2-34: planned (not started) |
| CAP-30.d | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-30.e | W1 | W1-12, W1-26 | — | — | — | — | built and closed (W1-12, W1-26) |
| CAP-30.f | W1 | W1-35 | — | — | — | — | built and closed (W1-35) |
| CAP-30.g | W2 | — | W2-35 | — | — | W2-35: 1 (W2-M322) | W2-35: planned (not started) |
| CAP-31.a | W1 | W1-08, W1-14 | — | — | — | — | built and closed (W1-08, W1-14) |
| CAP-31.b | W1 | W1-30 | — | — | — | — | built and closed (W1-30) |
| CAP-31.c | W1 | W1-09 | — | — | — | — | built and closed (W1-09) |
| CAP-31.d | W1 | W1-09 | — | — | — | — | built and closed (W1-09) |
| CAP-32.a | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-32.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-32.c | W1 | W1-35 | — | — | — | — | built and closed (W1-35) |
| CAP-32.d | W2 | — | W2-36 | — | — | W2-36: 1 (W2-M284) | W2-36: planned (not started) |
| CAP-33.a | W1 | W1-35 | — | W2-37 | — | — | built and closed (W1-35) |
| CAP-33.b | W2 | — | W2-37 | W2-37 | — | W2-37: 5 (W2-L319, W2-M056, W2-M150, W2-M285, W2-M320) | W2-37: held (built on its branch, not merged) |
| CAP-33.c | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-33.d | W1 | W1-35 | — | — | — | — | built and closed (W1-35) |
| CAP-33.e | W1 | W1-35 | — | W2-37, W2-49 | — | — | built and closed (W1-35) |
| CAP-33.f | W1 | W1-35 | — | W2-37 | — | — | built and closed (W1-35) |
| CAP-33.g | W2 | — | W2-37 | W2-37 | — | W2-37: 5 (W2-L319, W2-M056, W2-M150, W2-M285, W2-M320) | W2-37: held (built on its branch, not merged) |
| CAP-34.a | W1 | W1-34 | — | — | — | — | built and closed (W1-34) |
| CAP-34.b | W1 | W1-34 | — | — | — | — | built and closed (W1-34) |
| CAP-34.c | W1 | W1-34, W1-35 | — | — | — | — | built and closed (W1-34, W1-35) |
| CAP-34.d | W1 | W1-11, W1-34 | — | — | — | — | built and closed (W1-11, W1-34) |
| CAP-34.e | W1 | W1-09 | — | — | — | — | built and closed (W1-09) |
| CAP-35.a | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-35.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-35.c | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-36.a | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-37.a | W1 | W1-25 | — | — | — | — | built and closed (W1-25) |
| CAP-37.b | W1 | W1-25, W1-29 | — | — | — | — | built and closed (W1-25, W1-29) |
| CAP-37.c | W1 | W1-25, W1-29 | — | — | — | — | built and closed (W1-25, W1-29) |
| CAP-37.d | W1 | W1-29 | — | — | — | — | built and closed (W1-29) |
| CAP-37.e | W2 | — | W2-39 | — | — | W2-39: 8 (W2-L035, W2-L043, W2-L113, W2-M060, W2-M062, W2-M136, W2-M137, W2-M213) | W2-39: planned (not started) |
| CAP-37.f | W1 | W1-25 | — | — | — | — | built and closed (W1-25) |
| CAP-37.g | W1 | W1-49 | — | — | — | — | built and closed (W1-49) |
| CAP-38.a | W1 | W1-30 | — | — | — | — | built and closed (W1-30) |
| CAP-38.b | W1 | W1-26, W1-15, W1-17, W1-21, W1-24, W1-25, W1-27, W1-30, W1-35, W1-36, W1-38, W1-42 | — | — | — | — | built and closed (W1-26, W1-15, W1-17, W1-21, W1-24, W1-25, W1-27, W1-30, W1-35, W1-36, W1-38, W1-42) |
| CAP-38.c | W1 | W1-30, W1-02 | — | — | — | — | built and closed (W1-30, W1-02) |
| CAP-38.d | W1 | W1-30 | — | — | — | — | built and closed (W1-30) |
| CAP-38.e | W1 | W1-35 | — | — | — | — | built and closed (W1-35) |
| CAP-38.f | W1 | W1-30 | — | — | — | — | built and closed (W1-30) |
| CAP-39.a | W1 | W1-40, W1-02 | — | — | — | — | built and closed (W1-40, W1-02); W1-43: WEAKENED |
| CAP-39.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-39.c | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-39.d | W1 | W1-26 | — | — | — | — | built and closed (W1-26) |
| CAP-40.a | W1 | W1-31 | — | — | — | — | built and closed (W1-31) |
| CAP-40.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-40.c | W1 | W1-31, W1-42 | — | — | — | — | built and closed (W1-31, W1-42); W1-43: WEAKENED |
| CAP-40.d | W1 | W1-31 | — | — | — | — | built and closed (W1-31) |
| CAP-41.a | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-41.b | W1 | W1-44 | — | — | — | — | built and closed (W1-44) |
| CAP-41.c | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-41.d | W1 | W1-44 | — | — | — | — | built and closed (W1-44) |
| CAP-41.e | NONE | — | — | — | — | — | not built (NONE: non-goal or drop) |
| CAP-41.f | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-41.g | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-41.h | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-41.i | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-41.j | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-42.a | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-42.b | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-42.c | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-43.a | W1 | W1-39 | — | W2-16, W2-49 | — | — | built and closed (W1-39) |
| CAP-43.b | W2 | — | W2-16 / W2-24, W2-49 | W2-16, W2-49 | — | W2-16: 6 (W2-H029, W2-L002, W2-L014, W2-L227, W2-M174, W2-M175) | W2-16: held (built on its branch, not merged) |
| CAP-43.c | W3 | — | — | W2-49 | — | — | Wave 3 (not in Wave 2) |
| CAP-43.d | W3 | — | — | W2-16, W2-49 | — | — | Wave 3 (not in Wave 2) |
| CAP-44.a | W1 | W1-39 | — | W2-49 | — | — | built and closed (W1-39) |
| CAP-44.b | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-44.c | W1 | W1-41 | — | W2-52 | — | — | built and closed (W1-41) |
| CAP-44.d | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-44.e | W1 | W1-41 | — | W2-52 | — | — | built and closed (W1-41) |
| CAP-44.f | W2 | — | — / W2-49, W2-52 | W2-49, W2-52 | — | — | held: built on W2-52's branch (W2-49 writes it into Contract v4.2); no ticket's `closes` names it (F8) |
| CAP-44.g | W3 | — | — | W2-49 | — | — | Wave 3 (not in Wave 2) |
| CAP-44.h | W2 | — | W2-30 / W2-02, W2-28, W2-49, W2-52 | W2-02, W2-49, W2-52 | — | W2-30: 0 | W2-30: planned (not started) |
| CAP-44.i | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-44.j | W1 | W1-41 | — | — | — | — | built and closed (W1-41) |
| CAP-44.k | W3 | — | — | W2-49, W2-52 | — | — | Wave 3 (not in Wave 2) |
| CAP-44.l | W3 | — | — | W2-49 | — | — | Wave 3 (not in Wave 2) |
| CAP-45.a | W2 | — | W2-17 / W2-24 | W2-49 | — | W2-17: 1 (W2-M176) | W2-17: planned (not started) |
| CAP-45.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-46.a | W1 | W1-27 | — | — | — | — | built and closed (W1-27) |
| CAP-47.a | W3 | — | — | W2-52 | — | — | Wave 3 (not in Wave 2) |
| CAP-47.b | W1 | W1-36 | — | — | — | — | built and closed (W1-36) |
| CAP-47.c | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-47.d | W1 | W1-13, W1-35, W1-36 | — | — | — | — | built and closed (W1-13, W1-35, W1-36) |
| CAP-48.a | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-48.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-49.a | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-49.b | W1 | W1-46 | — | — | — | — | built and closed (W1-46) |
| CAP-49.c | W1 | W1-47 | — | — | — | — | built and closed (W1-47) |
| CAP-50.a | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-50.b | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-50.c | W1 | W1-30 | — | — | — | — | built and closed (W1-30) |
| CAP-50.d | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-50.e | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-50.f | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-50.g | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-51.a | W1 | W1-11 | — | — | — | — | built and closed (W1-11) |
| CAP-51.b | W1 | W1-21 | — | — | — | — | built and closed (W1-21) |
| CAP-52.a | W1 | W1-38 | — | — | — | — | built and closed (W1-38) |
| CAP-52.b | W1 | W1-38 | — | — | — | — | built and closed (W1-38) |
| CAP-53.a | W1 | W1-13, W1-08 | — | — | — | — | built and closed (W1-13, W1-08) |
| CAP-53.b | W2 | — | W2-38 | W2-37 | — | W2-38: 4 (W2-H043, W2-M163, W2-M240, W2-M241) | W2-38: planned (not started) |
| CAP-53.c | W1 | W1-31 | — | — | — | — | built and closed (W1-31) |
| CAP-54.a | W1 | W1-27 | — | — | — | — | built and closed (W1-27) |
| CAP-54.b | W1 | W1-08 | — | — | — | — | built and closed (W1-08) |
| CAP-55.a | W1 | W1-21, W1-22 | — | — | — | — | built and closed (W1-21, W1-22) |
| CAP-56.a | W1 | W1-36 | — | — | — | — | built and closed (W1-36); W1-43: WEAKENED |
| CAP-57.a | W1 | W1-20, W1-22 | — | — | — | — | built and closed (W1-20, W1-22) |
| CAP-58.a | W1 | W1-02, W1-03, W1-26 | — | — | — | — | built and closed (W1-02, W1-03, W1-26) |
| CAP-58.b | W1 | W1-33 | — | — | — | — | built and closed (W1-33) |
| CAP-58.c | W1 | W1-02 | — | — | — | — | built and closed (W1-02); W1-43: WEAKENED |
| CAP-58.d | W1 | W1-46 | — | — | W2-L342→Wave 3 | — | built and closed (W1-46) |
| CAP-58.e | W1 | W1-45 | — | — | — | — | built and closed (W1-45) |
| CAP-58.f | W1 | W1-47 | — | — | — | — | built and closed (W1-47) |
| CAP-58.g | W3 | — | — | — | — | — | Wave 3 (not in Wave 2) |
| CAP-58.h | W1 | W1-50 | — | — | — | — | built and closed (W1-50) |
| CAP-59.a | W1 | W1-30, W1-43 | — / W2-47 | — | W2-M333→W2-47 | — | built and closed (W1-30, W1-43); W1-43: WEAKENED |
| CAP-59.b | W1 | W1-30, W1-43 | — / W2-47 | — | W2-M333→W2-47 | — | built and closed (W1-30, W1-43); W1-43: WEAKENED |
| CAP-59.c | W1 | W1-30, W1-44 | — | — | — | — | built and closed (W1-30, W1-44) |
| CAP-60.a | NONE | — | — | — | — | — | not built (NONE: non-goal or drop) |
| CAP-61.a | W1 | W1-46 | — | — | — | — | built and closed (W1-46) |
| CAP-61.b | W1 | W1-46 | — | — | — | — | built and closed (W1-46) |
| CAP-61.c | W1 | W1-46 | — | — | — | — | built and closed (W1-46) |
| CAP-61.d | W1 | W1-46 | — | — | — | — | built and closed (W1-46) |
| CAP-61.e | W1 | W1-48 | — | — | — | — | built and closed (W1-48) |
| CAP-61.f | W2 | — | W2-40 | — | — | W2-40: 19 (W2-H052, W2-I001, W2-I036, W2-I037, W2-L025, W2-L316, W2-L328, W2-M005, W2-M087, W2-M234, W2-M334, W2-M335, W2-M336, W2-M337, W2-M338, W2-M344, W2-M345, W2-M347, W2-M350) | W2-40: planned (not started) |
| CAP-62.a | W1 | W1-47 | — | — | — | — | built and closed (W1-47) |

## Appendix B. Method of the mapping

1. **Contract items.** These come from the machine-readable Contract, `docs/contract/contract.yaml`, at version 4.2 on `w2/W2-49` (`19d45246`): each capability's `covers` items, with their wave and their Wave 1 providers. I read the item texts in `CONTRACT_v4.md` on the same branch.
   - The counts match the Contract's own changelog: 62 capabilities and 214 items (149 W1, 20 W2, 38 W3, 7 NONE).
   - Version 4.1 on `w2/integrate` gives 211 items (149, 17, 38, 7).
   - Version 4.2 moves CAP-43.b, CAP-44.f and CAP-44.h from W3 to W2, and adds CAP-43.d, CAP-44.k and CAP-44.l in W3.
2. **Tickets.** I read the front matter of every file in `.tickets/` on `w2/integrate` (`fecb870c`): `wbs_id`, `status`, `profile`, `closes`, `list_rows`, `deps` and `est_loc`.
   - A ticket "closes" an item when its `closes` field holds the item's id.
   - A ticket "cites" an item when its file or its WBS card mentions the id.
   - A ticket's state comes from its `status`, from whether its branch is merged into `w2/integrate`, and from the orchestrator's countdown.
3. **Acceptance folders.** I collected the Contract ids in every file of `tests/acceptance/W2-*/` on each Wave 2 branch head.
   - W2-02, W2-16, W2-37, W2-49 and W2-52 cite lettered items.
   - W2-01 and W2-54 cite capabilities only (CAP-01, CAP-19, CAP-33).
   - W2-51's ids (CAP-91 to CAP-99) are test fixtures, not Contract ids.
   - W2-03, W2-05, W2-20, W2-50 and W2-53 cite none.
4. **List rows.**
   - From `WAVE_2_LIST.md`: every table row with a W2-H, W2-M, W2-L or W2-I id (847 open rows), plus 42 W2-C rows that were closed before Wave 2. A row is mapped to an item when its text holds the item's id; only 17 rows hold any Contract id.
   - For Wave 2 items I added the `list_rows` of the ticket that closes the item.
   - Each row's triage comes from `WAVE_2_TRIAGE.md`.
5. **W1-43 classes.** These are taken from the audit's capability, item and master-rule table: 197 rows, 172 OK and 25 WEAKENED.
6. **What the map does not show.**
   - Rows that serve an item without naming it, on a ticket that does not close it.
   - The internal quality of any built item beyond W1-43's class. Other lenses assess that.
