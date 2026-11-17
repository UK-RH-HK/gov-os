# Audit 2: memory in use, and what depends on `gov context` (EMERGENCY-2 §9 row 2)

Date: 2026-11-17 · Commit: `a246f72b2` (branch `w2/integrate`; the working tree holds uncommitted changes to role-cto, role-lead, facts.yaml and the launcher, named where they matter) · Auditor: fresh, read-only
Sources read: EMERGENCY-2.md (whole); BRIEF-COMMON.md; retro-P5-memory-use.md; context/dec-1210-fresh-80.md; HANDOVER.md §4, §9; LIFT-1/FRESH-80-RESULT.md; DEC-836, DEC-1098 in the register; the code, templates, skills, facts and tests cited below; the landing log `log/landing-select/20261116-220824-3649974`; one generated brief (`gov brief engineer W2-17`, stdout only).
Memory use: 2 retrieves against the store (`W2-00-store`, built at `a246f72b2`). Both helped: the first led to W2-152's interface, DEC-836 and LEAD-w2-common's memory lines; the second led to DEC-1098 (1) and W2-88's table of default settings. I read each bundle in full.

"HEAD" means the committed file. "WT" means the working tree's uncommitted version.

---

## Table 1: every caller of `gov context`, `gov retrieve` and `gov brief`

### 1a. `gov context` (the command, the library `gov.context`, and its check)

`gov context` is switched off only in what agents are told. The command still runs (`src/gov/cli/main.py:99`). Code, adopted repositories and EXAMIN's copy still call it.

| # | Caller | What it uses `gov context` for | What changes now it is switched off (§5.5) | Source |
|---|---|---|---|---|
| C1 | SessionStart hook (Gov OS) | It used to put a ticket's context-packet summary into the session at start | **Done.** The call was removed by bb61d3d74; the checkpoint injection stays. The docstring still says it injects "gov context --brief output" (a stale line) | `template/governance/kernel/hooks/sessionstart.py:149` (call gone), `:16` (docstring); bb61d3d74 |
| C2 | role-lead template: building a worker's brief | It built each worker's brief | **Done.** The line now reads `gov brief <role> {ID}`; no `gov context` | `template/governance/kernel/templates/role-lead.md:24`; bb61d3d74 |
| C3 | role-lead's step `{STEP:context_ceiling}` (the check before DONE) | A lead ran `gov context {ID} --json` before DONE (DEC-1027) | **Done.** The step is `on: false`, so `gov brief` drops the line. The command and the step are still defined | `role-lead.md:64`; `governance/project/facts.yaml:95-97`, `:158-162` |
| C4 | role-cto template: building a worker's brief | The CTO built worker briefs with it | **Committed version still says `gov context {ID} --role`.** Only WT changes it to `gov brief`. The pinned shipped copy still says `gov context` | HEAD `role-cto.md:16` (`git diff`); `src/gov/_shipped/.../role-cto.md:16` (untracked build copy) |
| C5 | role-cto: the in-force list | `gov context --in-force` generates the list of decisions in force (DEC-1073) | This is a separate function (`gov.decisions.register.in_force`) that happens to sit under the `context` command. Switching off the ticket packet need not touch it. Retiring the command would need a new home for it | `role-cto.md:36`; `src/gov/context/command.py:10,18-20` |
| C6 | facts.yaml `commands.context` and `commands.context_ceiling` | Command forms that templates name as `{CMD:context}` and `{CMD:context_ceiling}` | No template names `{CMD:context}` any more (WT). Both forms are dead entries; the header comment (l.5-6) still says "a worker brief is built with `context`" | `governance/project/facts.yaml:5-6,43-45,95-97` |
| C7 | `gov adopt --facts`: the facts file written for an adopted repository | It writes `context` and `context_ceiling` into a new repository's facts, **with the step `on: true`** | **Not switched off.** Every repository adopted on 0.1.x gets the context-ceiling step in its lead briefs. It must change in the product | `src/gov/adopt/facts.py:45,60,99-102` |
| C8 | `gov close` | It builds the ticket's packet at the close. It records `packet_hash` and `decisions_applied` from the packet's mandatory inputs. If the packet cannot be built, the close refuses with `CONTEXT_FAILED` | **Still live.** The default ceiling is 6,000 tokens: no `budgets.close_context_tokens` in facts.yaml. A large ticket can fail its close with the same CONTEXT_OVER_CEILING that refused 103 lead calls (P5 table C). Gov OS's own landing uses `tk close`, not `gov close` | `src/gov/close/command.py:261,268-275,500-535`; `src/gov/context/__init__.py:22,43-60`; `land.py:365` |
| C9 | The `context-reproducibility` check in `gov check` | A kernel check family: the same ticket and commit must give the same packet hash (CAP-38.b) | **Still live** in every `gov check`. It goes red on a tree with no loaded store | `template/governance/kernel/checks/context-reproducibility.yaml:5`; bootstrap.md W1-24 residuals (retrieve 1) |
| C10 | The audit skill | Step 1 says the audit starts from "the bounded context pack from `gov context`" | It must change to `gov retrieve --ticket {ID}` plus reading the ticket's sources by id | `template/governance/kernel/skills/audit/SKILL.md:17` (+ `.claude/skills` copy) |
| C11 | The checkpoint skill | "Knowledge of the repository comes from … the context packets (`gov context`)" | Drop the clause; retrieval alone | `template/governance/kernel/skills/checkpoint/SKILL.md:44` |
| C12 | Library helpers `_tokens` / `TOKEN_CHARS` | The token counter, the session log, the skill validator and the supplementary block import a 4-character token helper from `gov.context` | Unaffected while the module exists. Retiring the module breaks four imports | `src/gov/telemetry/counter.py:25`, `sessionlog.py:24`, `check/skill_validator.py:47`, `retrieval/supplementary.py:129` |
| C13 | Orchestration tools | The dispatcher classes the context check as a heavy job. `record_checks.sh` runs it | Harmless; they go when the check goes | `governance/project/orchestration/tools/dispatch/dispatcher.py:350`; `.gov-runtime/scratch/orchestrator/tools/record_checks.sh:11` |
| C14 | Old prompts and briefs | w2-orchestrator.md tells the CTO to "build every brief with `gov context`". LEAD-w2-common.md runs the context check in a heavy slot | Archived by §11.1 (the old prompt); LEAD-w2-common becomes obsolete once lead briefs come from `gov brief lead` | `governance/project/prompts/w2-orchestrator.md:160`; `governance/project/briefs/LEAD-w2-common.md:64` |
| C15 | **EXAMIN's copy** (`~/gov-os-runs/W2-27/examin`) | role-cto builds worker briefs with `gov context`. Its SessionStart hook still imports `gov.context`. Its facts carry `context` and `context_ceiling` | **Not switched off.** This belongs with the 0.1.2 re-pin row of §6.1 | `examin/.claude/templates/role-cto.md:16`; `examin/.claude/hooks/sessionstart.py:152`; `examin/governance/project/facts.yaml:33-35,78-80` |
| C16 | Tests that assert `gov context` | W1-24, W2-04, W2-54, W2-183 and W2-13 test the command and the library. W2-55 tests `--in-force` and the left-out entries. W1-30 tests the close's packet | They stay green while the code stays. Retiring the command takes these folders with it (audit 7 and CAP-15) | `tests/acceptance/{W1-24,W2-04,W2-54,W2-55,W2-183,W2-13,W1-30}/`; `tests/unit/context/` |
| C17 | Tests that asserted the switched-off lines | W2-128 row 3 ("worker brief built with gov context") and W2-128 F1 (every command a template names is in facts) went red at bb61d3d74. So did W2-152 S10 (which runs W2-128's acceptance) and three W2-153 composition cases (template bytes changed) | WT already renames row 3 to `gov brief` and adds `commands.brief` to facts. **5 of the 29 reds are this audit's; the other 24 are the guard's** | `verify/parallel.xml` of the landing log above; `git diff tests/acceptance/W2-128/` |

### 1b. `gov retrieve`

| # | Caller | What it uses memory for | What changes (§5.4, §5.5) | Source |
|---|---|---|---|---|
| R1 | T-0 (`brief.md`), the envelope of every worker's and lead's brief | "Ask memory first: outside the sandbox `{CMD:retrieve}` …"; then search again once; then **"No `gov retrieve` in the sandbox … a launched worker searches with the Read and Grep tools"** | Line 33 tells every launched worker not to use memory, and with no sandbox the "outside/inside" split means nothing. Line 31's command comes out malformed: `gov retrieve --root …/W2-00-store "{QUESTION}" "<which decision governs X …>"` (two quoted arguments; seen in a generated brief, line 38) | `template/governance/kernel/templates/brief.md:31-33`; `gov brief engineer W2-17` stdout |
| R2 | role-cto | The CTO's own start: "the rest on demand ({CMD:retrieve}), and search again once" | It stays. There is **no memory block for the CTO's subagents** (P5 F2) | `role-cto.md:8`; "Launching work" `:14-21` |
| R3 | role-lead | "Ask memory, not the register: {CMD:retrieve}"; the store's path is in the table | It stays. There is no "read every item, never head"; 11 of 20 lead bundles were cut short (P5 F4) | `role-lead.md:16,21` |
| R4 | role-test-designer, role-research | "outside the sandbox {CMD:retrieve}; inside it, the Read and Grep tools" | Drop the sandbox split: retrieve always | `role-test-designer.md:12`; `role-research.md:12` |
| R5 | role-engineer, role-product-spec | "ask memory for the rest (T-0)": they name no command, so `gov brief`'s command table carries no `retrieve` row for them | Name `{CMD:retrieve}` here so the command reaches their table | `role-engineer.md:11`; `role-product-spec.md:11`; `src/gov/brief/build.py:411-419` |
| R6 | role-reviewer | none | Add the memory line (P5 F8, gap 4) | `role-reviewer.md` (no line) |
| R7 | facts.yaml `commands.retrieve` | The form `gov retrieve --root {STORE_TREE} "{QUESTION}"`; `QUESTION` is a form key, so `gov brief` leaves it as written | Make it `… "<question>"` and drop `QUESTION` from keys.yaml (gap 7) | `governance/project/facts.yaml:40-42`; `template/governance/kernel/templates/keys.yaml:45`; `build.py:186-217` |
| R8 | `gov adopt --facts` | The adopted form `gov retrieve "{QUESTION}"`, with no `--root` (it relies on `GOV_STORE` or the tree's store) | Same fix as R7 | `src/gov/adopt/facts.py:44` |
| R9 | Skills: api, backend, data, devops, frontend, security, ui-ux, spec-writing, qa-review, discovery, the skill template | "what else it needs to know, through `gov retrieve` first (DEC-836)" | They stay. Add search again once and "read the whole bundle" | e.g. `skills/backend/SKILL.md:32`, `qa-review/SKILL.md:29`, `templates/skill.md:73` |
| R10 | The retrieval skill | The method, plus step 7, search again once (DEC-1092 (1)) | Add: read every item, never head or cut, cite the ids used (P5 F4) | `skills/retrieval/SKILL.md:15-28` |
| R11 | Skills with no memory line | adopt, audit, change, planning, test-design, orchestration's SKILL.md, the vendored superpowers | Add the memory-first line (§5.4 "every skill") | `grep` over `template/governance/kernel/skills/*/` |
| R12 | Orchestration checklist item C6 | "Memory: `gov retrieve` first (DEC-836) …" | It stays. Add "the brief's memory block" | `skills/orchestration/briefs-and-returns.md:17` |
| R13 | `gov launch` (WT, 0.1.2) | It sets `GOV_STORE` to the integration store's link, so a worker's plain `gov retrieve` answers from it; `GOV_ROLE` sets the bundle's role filter | It stays. With no sandbox, the embedder and the reranker are reachable | `src/gov/launch/launcher.py:182-199` (WT); `src/gov/launch/store.py:10`; `src/gov/retrieve/command.py` docstring |
| R14 | Product code that runs retrieval (not agents) | `gov adopt` A9 (the standard's settings and a smoke search); the memory measure and memaudit; rebuild canaries; impact; machine resources | Unaffected | `src/gov/adopt/fabric.py:149-185,638-682`; `src/gov/memaudit/*`; `src/gov/retrieval/measure.py` |
| R15 | Orchestration tools | The dispatcher classes retrieve as a retrieval slot. `rerank_reset_watch.sh` warms the reranker. `adoption_count.py` counts retrieves in transcripts (a usage meter). `repin.sh` makes a smoke search after the re-pin | Unaffected; `adoption_count.py` is a ready base for the weekly measure | `dispatch/dispatcher.py:528,839,888`; `tools/rerank_reset_watch.sh:31`; `tools/adoption_count.py:6`; `docs/emergency-2/release-0.1.2/repin.sh:80` |
| R16 | Lead and auditor common briefs | LEAD-w2-common: DEC-836, search again once, batches, code-graph queries. AUDITOR-common: retrieve, then search again once | Obsolete once `gov brief lead` replaces `build_lead_brief.py` (facts.yaml `lead_brief` still maps to it) | `governance/project/briefs/LEAD-w2-common.md:30`; `AUDITOR-common.md:8`; `facts.yaml:80-82` |
| R17 | CLAUDE.md, AGENTS.md, `.rulesync/rules/governance.md` | No memory-first line (only "retrieval" in the list of skills) | Add one line (P5 F5, F7) | `CLAUDE.md:29`; `AGENTS.md:33` |
| R18 | Tests that constrain the change | W2-128 row 6 **requires** brief.md to say "no gov retrieve in the sandbox". W2-128 S20 requires "Ask memory first" in Commands, followed by the search-again line. W2-128 S6: no facts check may call retrieve except `--help` | Row 6 must change, by the test designer, in the same change as brief.md, or the landing turns red | `tests/acceptance/W2-128/test_w2_128_rows.py:55-65`; `test_w2_128_templates.py:190-213`; `test_w2_128_facts.py:54-60` |

### 1c. `gov brief`

| # | Caller | What it uses memory for | What changes | Source |
|---|---|---|---|---|
| B1 | `gov brief` itself | **Nothing.** It fills T-0 and the role template from the ticket, facts.yaml and keys.yaml. It runs no retrieval and puts no memory content into the brief | §5.4: it must put the ticket's retrieval into every brief (Table 2) | `src/gov/brief/build.py:317-366,368-408` |
| B2 | role-cto, role-lead (WT and HEAD for lead) | "Build each worker's brief … with `gov brief <role> {ID}`" | It stays | `role-lead.md:24`; `role-cto.md:16` (WT) |
| B3 | facts.yaml `commands.brief` (WT) and `lead_brief` | The worker form is added in WT. `lead_brief` still maps to `build_lead_brief.py`, while `release_lead.sh` refuses a brief built that way | Map `lead_brief` to `gov brief lead {ID} --run {RUN_KIND} --part {PART}`, as `adopt/facts.py:55` already does | `facts.yaml:46-49` (WT), `:80-82`; `tools/release_lead.sh:25` |
| B4 | `gov adopt` verify pass | It reuses `kpi_rows` so the adoption's KPI list and the ready check agree | Unaffected | `src/gov/adopt/verify_pass.py:27` |
| B5 | Product dispatcher's brief check | It refuses a brief that holds an unfilled `{UPPER}` slot. **Every `gov brief` output holds `{QUESTION}`** (R1), so a lead brief built by `gov brief lead` is refused as "brief incomplete" | Fixed by R7 | `src/gov/dispatch/readiness.py:19,81-94` |
| B6 | CLAUDE.md, AGENTS.md | "put in by `gov brief`, once it lands": the golden rule through `judging-work` (W2-195) | Separate from memory; A-13 trims it | `CLAUDE.md:39`; `AGENTS.md:43` |

---

## Table 2: the change for §5.4 (memory used by construction)

| # | What | Line or behaviour to add | Files to change | Size (estimate) | Closes |
|---|---|---|---|---|---|
| M1 | `gov brief` puts the ticket's retrieval into every brief | **A "What memory holds for this ticket" block.** `gov brief` calls `gov.retrieval.retrieve(store, <ticket title>, ticket=<id>)` on the integration store. The brief gets one line per item (`path:start-end`, the record id, the first line) inside a fenced block, plus the store's commit. The whole bundle is written to `{WRITE_TREE}/.gov-runtime/scratch/memory/<ID>.json`. Fenced blocks do not count against the 4,000-character prose budget (`facts.yaml:173`), and a generated brief is already at 3,560. A store that is missing or not reranked gives a warning, never a refusal (trust, catch and correct). The run is deterministic at a fixed store commit, so W2-152 S1 still holds | `src/gov/brief/build.py`, `command.py`; `brief.md` (the block's place); unit tests; W2-152's acceptance cases for the new block (the test designer) | ~120-150 LOC code + ~120 LOC tests; ~2,200-6,000 tokens more per brief (the lead median of 8,660 characters in P5 §2 D, up to the 6,000-token bundle) | §5.4; gaps 1, 3, 5, 7 |
| M2 | T-0 says memory first, for everyone | Replace `brief.md:31-33` with: "**Ask memory first:** {CMD:retrieve} with your question; read every item of the bundle, never `head` or cut it, and cite the ids you use. Search again once in your own, different words if it does not answer; then answer from both bundles with path and lines, or say "not found". Grep the register only by id." Delete "No `gov retrieve` in the sandbox, and no `gov context` …" | `template/governance/kernel/templates/brief.md`; W2-128 row 6 (the test designer, same change) | 3 lines; 1 test | gaps 1, 6 |
| M3 | facts and keys | `retrieve.run: 'gov retrieve --root {STORE_TREE} "<question>"'`; drop `QUESTION` from keys.yaml; delete `commands.context`, `commands.context_ceiling` and `steps.context_ceiling`; fix the header comment l.5-6; map `lead_brief` to `gov brief lead` | `governance/project/facts.yaml`; `template/governance/kernel/templates/keys.yaml`; `src/gov/adopt/facts.py` (the same for adopted repositories, step removed) | ~15 lines + ~10 lines and 1 unit test | gap 7; C3, C6, C7, B5 |
| M4 | Role templates | role-engineer:11 and role-product-spec:11: "ask memory first: {CMD:retrieve} …" (so the command reaches their table). role-test-designer:12 and role-research:12: drop "outside/inside the sandbox". **role-reviewer: a new step 2a**: "Ask memory first ({CMD:retrieve}) for the decisions a finding rests on; search again once; grep the register only by id." role-lead:21: add "read the whole bundle, never `| head`; cite the ids used". role-lead:64: delete `{STEP:context_ceiling}`. role-cto "Launching work": "**Every subagent prompt opens with the memory block:** ask memory first (`gov retrieve --root {STORE_TREE} "<question>"`), read the whole bundle, search once more in your own words, note in the return how many retrieves helped." (BRIEF-COMMON.md:17-21 is this block written by hand.) role-cto:16: commit the WT line | 7 files in `template/governance/kernel/templates/` and their `.claude/templates/` copies | ~10 lines | gaps 3, 4, 6 |
| M5 | Instruction files | One line in each: "Memory first: before grepping for a concept, ask `gov retrieve` once, read the whole bundle, and ask once more in your own words; look a decision up by id in the register." Also in the adopted repository's CLAUDE.md template | `CLAUDE.md`, `AGENTS.md`, `.rulesync/rules/governance.md`; the adopt CLAUDE.md template | 4 lines | gaps 3, 5 |
| M6 | Skills | Add the M5 line to adopt, audit, change, planning, test-design and orchestration's SKILL.md. audit:17: `gov context` becomes `gov retrieve --ticket {ID}` plus the sources by id. checkpoint:44: drop "the context packets". retrieval: a new step "read every item; never head or cut; cite ids" | 8 SKILL.md files and their `.claude/skills/` copies | ~10 lines | gaps 6; C10, C11 |
| M7 | The memory-use log (§5.6; P5 F6's fields, plus four of mine) | Every `gov retrieve` (and every M1 retrieval) appends one JSON line to `<main repo>/.gov-runtime/memory-use.jsonl`. P5 F6's fields: role, ticket, query hash, stop reason, items, characters, latency, refusal code. Mine: session id, store commit, `reranked`, and search number in the session (1st/2nd, which measures search-again). A write failure never fails the search. A digest line reads it daily. `adoption_count.py`'s transcript count is the weekly cross-check against greps | `src/gov/retrieve/command.py` (writer); a small reader (`gov memory-use --since`, or inside the digest); unit tests | ~60 LOC writer + ~60 LOC reader + ~100 LOC tests | §5.6; §10.2 "memory use" |
| M8 | Retrieve's output fit for "read the whole bundle" | Print a one-line index of all items first (P5 F4). Put `gaps` (282 entries, 37 KB in one of my two bundles) and `continuation` behind `--gaps`/`--json`. Today one 6,000-token bundle prints 50-77 KB, so a reader who reads it all spends ~13-19k tokens, two thirds of them not evidence | `src/gov/retrieve/command.py`; tests | ~40 LOC + tests | gap 6; the second rerank of §5.1 |
| M9 | Store fresh after every commit | Refresh the integration store after every commit to `w2/integrate`, not only after landings. Today a direct decision-record commit is indexed only by a by-hand run (the twice-daily backstop is not in the crontab). Belongs to the run-time tool (§6.3) | run-time tool / `refresh_integration_store.sh` trigger | ~20 lines | gap 8 |
| M10 | Generated copies | Regenerate `.claude/templates`, `.claude/skills`, `.claude/agents`, `.rulesync`, `template/.rulesync`; `_shipped` at the 0.1.2 build | generated | none by hand | |

Estimates are mine: by analogy to `build.py` (419 lines for the whole of `gov brief`) and to the line counts above. Total ≈ 400-500 LOC of code and tests, plus ~45 lines of template, skill and instruction text in one CTO change (3.5).

---

## Table 3: the gaps of §5.7, open or closed today

| # | Gap (§5.7) | Today | Evidence |
|---|---|---|---|
| 1 | The brief says "No `gov retrieve` in the sandbox" | **Open** | `template/governance/kernel/templates/brief.md:33`, the same in `.claude/templates/brief.md:33` and the pinned `_shipped` copy; generated brief line 40. W2-128 row 6 asserts the line (`test_w2_128_rows.py:55-65`) |
| 2 | Workers' retrieves were degraded in the sandbox | **Open until 0.1.2 is cut and pinned; closed by construction after.** The pin is 0.1.1 (`gov --version`; `pin-2becaacdc2fb`), and its launcher writes the sandbox block with the reranker socket only (`…/site-packages/gov/launch/launcher.py:250-255`). WT's launcher has no sandbox (`src/gov/launch/launcher.py:11-17`, uncommitted). Under 0.1.1 the launcher refuses every worker launch (§6.1), so no worker retrieves at all today | as stated |
| 3 | The CTO asked memory 6 times; its subagents 3 | **Open in the templates; done by hand here.** role-cto:8 covers the CTO itself. "Launching work" (`role-cto.md:14-21`) has no subagent memory block. BRIEF-COMMON.md:17-21 adds one by hand for these audits | as stated |
| 4 | `role-reviewer.md` has no memory line | **Open** | `template/governance/kernel/templates/role-reviewer.md` (43 lines, no "memory" or "retrieve") |
| 5 | The EXAMIN CTO made 0 retrieves | **Open.** EXAMIN's CLAUDE.md and AGENTS.md carry no memory-first line. Its role-cto still builds worker briefs with `gov context` | `~/gov-os-runs/W2-27/examin/CLAUDE.md` (no line); `examin/.claude/templates/role-cto.md:16` |
| 6 | Leads cut bundles with `head` | **Open.** No template, skill or instruction file says "read every item / never head". `gov retrieve` prints no index first, and its output is 3-4 times the bundle (M8) | grep over templates, skills, CLAUDE.md, AGENTS.md: no hit; `skills/retrieval/SKILL.md:28` |
| 7 | `{QUESTION}` left unfilled in 23 briefs | **Open, and worse than stated:** every brief `gov brief` builds has it, at T-0 line 31, next to a second quoted placeholder. The product dispatcher would refuse such a brief | `facts.yaml:41`; `keys.yaml:45`; `build.py:213-216`; generated brief line 38; `src/gov/dispatch/readiness.py:19,92-94` |
| 8 | The store lacks recent decisions until it is rebuilt | **Open (fresh at this moment by hand).** The store is at `a246f72b2` = HEAD only because a rebuild ran at 21:54, ~22 h after the commit. Landings promote the store (`merge_queue.py:1035-1058`), but a direct decision-record commit triggers nothing. The only active crontab line is `run_tick.sh`. The result names `store.commit` beside `head`, so lag is visible, not silent | `.gov-runtime/scratch/orchestrator/log/integration-store.log:188539-188543`; `crontab -l`; `src/gov/retrieve/command.py` docstring (W2-138) |

### The standard of §5.1, against what `gov retrieve` does by default today

- **The tool side is the standard by default, when the shared reranker and the embedders are up.** A plain call runs four routes: lexical (BM25), semantic, closure (the record graph) and code (the code graph). It searches three phrasings, uses the candidate pool (route depth 60, rerank depth 40), and reranks with Qwen3-Reranker-0.6B through the shared service on the GPU. The first call returns ~20 items within the 6,000-token bundle, widened to sections (2 batches of 10). That is DEC-1098 (1)'s configuration, and the first call's 20 items cover hit@10 and hit@20. Evidence:
  - my two bundles: `rerank.by: service, cuda:0`; all four facets available; `pool.settings` as in `governance/project/retrieval.yaml:9-14`; `budget.bundle.limit 6000`; 19-20 items;
  - `src/gov/retrieval/retrieve.py:48,57-58`; `rerank.py:29`; `docs/changes/W2-88-evidence.md:82-90`.
- **It degrades quietly when a service is down.** A dead reranker leaves `merge.reranked: false` and raises nothing (`docs/DECISION_REGISTER.md:4515-4518`, DP-6). An unreachable embedder gives `FACET_UNAVAILABLE` for the semantic route, and there is no CPU fallback (§5.8). The bundle names both, but no agent is told to check them.
- **The agent side is half carried.**
  - "Search again once" is stated in T-0:32, retrieval skill step 7, role-cto:8 and AUDITOR-common:8. It is not stated in role-engineer, role-product-spec, role-reviewer or the engineering skills.
  - "Read the whole ranked bundle as a second reranker" is stated nowhere (gap 6). The output shape works against it (M8).
- **What a worker launched by 0.1.2 gets** (WT launcher; 0.1.2 not yet cut):
  - It gets `GOV_STORE` and `GOV_ROLE`, and no sandbox. A `gov retrieve` it ran would get the full standard bundle (role-filtered).
  - Its appended prompt (role file + skills + template, `launcher.py:31-36`) says "ask memory for the rest (T-0)".
  - Its T-0 brief (stdin) carries **no retrieval content** (B1). It tells the worker **not** to use `gov retrieve` (brief.md:33). The one copyable command in it is malformed (gap 7).
  - **Net: the standard is reachable, but by construction the worker is told not to use it and is given none of it.** M1, M2 and M3 are the change that reverses this.

## Findings the tables cannot say

- **F-A. §5.5's switch-off covers only Gov OS's own hook and lead step.** It does not reach the product. `gov adopt --facts` turns the context-ceiling step on for every new repository (C7), `gov close` and `gov check` still depend on the packet (C8, C9), and EXAMIN's copy still calls it (C15). Ordinary work hits these. They fail closed (a refused close or a red check), so they lose no work: they do not block, but they are friction to fix in 0.1.2.
- **F-B. The committed role-cto still says `gov context`.** Only the uncommitted working tree fixes it (C4). If the WT is lost, the CTO template goes back to the off command.
- **F-C. Changing brief.md alone turns the landing red** (W2-128 row 6, R18). The template change and the test change must land together, the test by the test designer.

## Decisions for the owner

1. **What happens to `gov context` as code?** §6.1 says "switched off". Is the command also retired?
   - (a) Keep it as it is, with no instruction calling it. Cost: none now; `gov close` can still refuse on the 6,000-token ceiling, and adopted repositories still get the step unless M3 lands.
   - (b) Retire the command, its check and the adopt facts entries. Keep the library only for `gov close` (with the close's ceiling raised or removed) and move `--in-force` to `gov decisions`. Cost: ~1 day; 7 test folders retire or move; CAP-15 goes to audit 7.
   - (c) Retire the module too and change `gov close` to record decisions from the ticket's `sources:`. Cost: ~2 days; it touches the close's record format.
   - **Recommendation: (b)**, in the 0.1.2-to-release window. Agents never need the packet any more, and (b) removes the close refusal that 38 % of lead calls already hit.

## The CTO decides (under 3.5, 4.2 and 4.6)

- **The §5.4 text pack (M2, M4, M5, M6) as one CTO change,** with W2-128 row 6 rewritten by the test designer in the same landing. Recommend: do it now. It is ~45 lines and needs no ticket. It makes every brief and skill say memory first.
- **M1 + M7 (+ M8) as one feature ticket, "memory by construction"** (§6.1 build row), with KPIs:
  - every `gov brief` output holds the ticket's memory block and the store commit;
  - every retrieve writes one log line;
  - the digest shows retrieves per role per day.
  Recommend: build it for the release.
- **M3 (facts, keys, adopt facts) as a fix** (4.2): the failing test first (`{QUESTION}` absent from a generated brief). Recommend: now. It also clears the product dispatcher's refusal (B5).
- **M9 (store refresh on every commit to `w2/integrate`):** fold it into the run-time tool. Until then, run a refresh after each decision-record commit. Recommend: yes.
- **Commit WT's role-cto:16 line** with the next CTO change (F-B). Recommend: yes.
- **EXAMIN's copy** (C15, gap 5): change its role-cto, hook and facts, and add the CLAUDE.md memory line, at the 0.1.2 re-pin (§6.1 row). Recommend: yes, in the same step.
