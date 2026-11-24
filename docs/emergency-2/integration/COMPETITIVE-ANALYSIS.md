# G-9: Gov OS against open-source AI software factories

`docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md` · research (Sonnet), read-only · 2026-11-24 · Gov OS `w2/integrate` at `98893679c`; the decision is the owner's (DEC-1241 G-9)

**How it was made.**
- **Memory first.** `gov retrieve` ran once and returned a store 584 paths behind HEAD and an off-target bundle (an old roles-research sketch of a "benchmarking" skill). I used files instead, as the tool map's author did (`TOOL-MAP.md` header). That is finding I-9 again.
- **Gov OS's side** is read from `GOLDEN-WORKFLOW.md`, `TOOL-MAP.md` §1 and §3, audit 4 §0, `IMPORTS-ADOPTION-SPEC.md`, DEC-1228 (3), DEC-1238 to DEC-1242 and EMERGENCY-2 §2 to §3. I checked three lines myself: `src/gov/spend/brake.py:31`, `src/gov/launch/launcher.py:107` and `.tickets/DAEO-rt4s.md` (W2-207).
- **The outside side** was read by six Sonnet helpers, one area each, from the projects' own repositories and docs. GitHub API and raw URLs gave the exact figures (stars, licence, dates). Every outside fact below is read on **2026-11-24** at the URL given.
- **Limits.** Docs pages were summarised by a small fetch model, so a quote or a number may be slightly off. The vendors' own pages are not independent. I installed and ran nothing. No hidden question set was opened.

## 0. The answer in seven lines

1. **Two of the owner's four named projects are one.** `software-factory.dev` is Ona's build-in-public experiment, and its code is the `gitpod-io/memo` repository. It is a demo app with **no licence**, no releases and no commit since 2026-07-06. It is a source of ideas, not an engine.
2. **"Vercel's AI SDK factory"** is the AI SDK team's own `ai-sdk-factory`, whose repository is **not public** (`github.com/vercel/ai-sdk-factory` returns 404). The inspectable comparable is **Foreman** (`vercel-labs/eve-software-factory-template`, MIT, 3 months old, 2 contributors, no releases), built on Vercel's `eve` framework (Apache-2.0).
3. **The two real engines are Fabro and Archon**, both MIT. Fabro is a Rust binary with workflows as DOT graphs. Archon is a TypeScript workflow engine with YAML, worktrees and loop nodes. OpenHands is the large mature agent platform, but its engine does not hold a test gate.
4. **None of them has what Gov OS is for:** memory-first retrieval measured end to end, a decision register with levels, an independent test designer, an impact-selected landing, and an adoption stage chain. Every source says so in its own words (§3).
5. **What they have that Gov OS lacks** is real, but small and local: loop caps held in code, a circuit breaker on a repeated failure, a stall detector, per-stage usage figures, durable human gates, and run observability (§3, §4).
6. **The plain answer: finish our integration. Do not adopt an engine now.** An engine would replace about 19 of the tool map's 102 rows (launch and run, W8 and W15). Those rows are already built in `src/gov`, and the slice still open is about 500 lines (`DAEO-rt4s`, `est_loc: 500`). Gov OS bypassed its own tools, and a second engine would be one more thing to bypass (§5).
7. **Recommended:** absorb nothing and use nothing now. Build six small things from what the engines show us, inside the integration plan. Set one check for when to look at an engine again (§5.4).

---

## 1. The field

Six projects, in the owner's order, then two I found. Each is five lines: what it is, maturity, licence and language, who runs it. A seventh is a note.

**Why these.** The owner named four. I searched for "agentic software factory", "autonomous coding pipeline with gates and fix loops", OpenHands, SWE-agent, Goose and Aider pipelines, and read the awesome list `ghempton/awesome-software-factories` (a fork of `varun1505/…`; I read only the sections on open-source factories, ticket-to-PR pipelines, autonomous loops, review gates and multi-agent frameworks). I picked the two found projects that are the most comparable on the owner's dimensions:
- **Archon**, because it mixes agent steps, scripts, gates, loops and human waits in a worktree, with no sandbox, as Gov OS does.
- **OpenHands**, because it is the reference open-source coding-agent platform, with the largest community, and its confirmation, stuck-detection and budget features are the market's baseline.

I did not pick SWE-agent or Aider pipelines (single-task agents, no pipeline of gates in the sources I saw) or Goose (a general agent; not read in depth).

### 1.1 Fabro: https://github.com/fabro-sh/fabro

- **What.** "Open source dark software factory for expert engineers". Processes are version-controlled **Graphviz DOT graphs** whose nodes are agents, prompts, shell commands, conditions, human gates and parallel fan-outs. Its docs call it a research preview (https://docs.fabro.sh/administration/security.md).
- **Maturity.** 1,886 stars, 210 forks, 31 contributors (one author has 4,652 of about 5,663 commits; the rest are mostly bots). Created 2026-03-13. Last commit 2026-11-20. **Every visible release is a nightly** (latest `v0.423.0-nightly.0`, 2026-11-20; no stable release found). (https://api.github.com/repos/fabro-sh/fabro, `/contributors`, `/releases`)
- **Licence, language.** MIT, "Copyright (c) 2026 Lithos Computer Co. / Copyright Qlty Software Inc." (https://raw.githubusercontent.com/fabro-sh/fabro/main/LICENSE.md). Rust, single binary.
- **Who runs it.** The `fabro-sh` organisation; the main author is `brynary` (README contact on `qlty.sh`). No Fabro-run SaaS found; a one-click Railway deploy of the same image exists (https://docs.fabro.sh/administration/deploy-railway.md).

### 1.2 Ona's `memo`, also `software-factory.dev`: https://github.com/gitpod-io/memo

- **What.** "A Notion-style note-taking app, built entirely by AI agents", the product of Ona's April 2026 build-in-public sprint. About 17 chained "Automations" of Ona's platform (planner, builder, bug fixer, PR reviewer, incident responder, post-merge verifier, auditors) run on cron and webhooks, with GitHub issues and labels as the work queue (https://software-factory.dev; `.ona/skills/development-workflow/SKILL.md` in the repo; https://github.com/gitpod-io/memo).
- **Maturity.** 62 stars, 13 forks, 4 contributors (one is the bot `sw-factory-automations`), 964 commits, **no releases**, last commit **2026-07-06**. The site's own numbers disagree by date (375, 489 and 688 PRs) (https://api.github.com/repos/gitpod-io/memo).
- **Licence, language.** **None.** The API field is `license: null`, `/LICENSE` returns 404, and the root listing has no licence file. Public code with no grant is all rights reserved. TypeScript (Next.js, Supabase).
- **Who runs it.** Ona (formerly Gitpod). **The engine is a closed SaaS**: Ona hosts the management plane, and runners deploy into the customer's AWS or GCP on the Enterprise plan (https://ona.com/docs/ona/runners/overview.md). The old open-source `gitpod-io/gitpod` is AGPL-3.0 and "no longer recommended" (https://api.github.com/repos/gitpod-io/gitpod). Automations need Ona's Core or Enterprise plan; time and webhook triggers are Enterprise (https://ona.com/docs/ona/automations/plans-and-limits.md).

### 1.3 Vercel's factory: the AI SDK team's `ai-sdk-factory`, and Foreman

- **What.** The AI SDK team's own factory handles AI SDK issues and PRs with agents for classification, bug reproduction, fixes, review, backports and docs; the blog says its agents author 25 to 35 % of weekly merged PRs after about four weeks (https://vercel.com/blog/building-a-software-factory-for-ai-sdk, 12 Aug 2026). Its repository is not public (404). **Foreman** is the open template: stations Triage, Classifier, Researcher, Analyst, Implementer, Reviewer; started by a GitHub label, an @mention, a Linear session, an HTTP POST or red CI; one Vercel Sandbox per station (https://raw.githubusercontent.com/vercel-labs/eve-software-factory-template/main/README.md).
- **Maturity.** Foreman: 1,186 stars, 84 forks, 2 contributors, no releases, created 2026-08-12, last commit 2026-11-17. `eve` (the framework, "beta"): 6,061 stars, latest `eve@1.4.0` 2026-11-23. `vercel/ai`: 28.2k stars, `ai@7.0.181` 2026-11-23 (https://api.github.com/repos/vercel-labs/eve-software-factory-template, `/vercel/eve`, `/vercel/ai`).
- **Licence, language.** Foreman MIT; `eve` Apache-2.0; `vercel/ai` Apache-2.0 (the API reports NOASSERTION; the LICENSE file is Apache). TypeScript.
- **Who runs it.** Vercel (Foreman under Vercel Labs). It is built to run on Vercel's own platform (Workflows, Sandbox, AI Gateway, Blob).

### 1.4 Archon: https://github.com/coleam00/Archon

- **What.** "First open-source harness builder for AI coding": YAML workflows (a DAG) of agent steps, bash and script nodes, loops, human `wait` nodes, each run in its own git worktree; a bundled `sdlc` pack runs issue to PR (https://archon.diy/getting-started/why-archon/). It is the 0.x rewrite; the older "Archon" v1 to v6 (RAG, Supabase) is a different, unmaintained product.
- **Maturity.** 23,985 stars, 3,544 forks, 86 contributors (one maintainer has 3,878 commits against the owner's 431). Created 2025-02-07, last push 2026-11-23, latest release `v0.14.0` 2026-11-07 (0.3 to 0.14 in about six months; **pre-1.0, fast semantic change**) (https://api.github.com/repos/coleam00/Archon, `/contributors`, `/releases`).
- **Licence, language.** MIT, Cole Medin (https://raw.githubusercontent.com/coleam00/Archon/main/LICENSE). TypeScript on Bun. Anonymous PostHog telemetry is on by default (`ARCHON_TELEMETRY_DISABLED=1` turns it off).
- **Who runs it.** A personal account (`coleam00`), not an organisation. No commercial offer found.

### 1.5 OpenHands: https://github.com/OpenHands/OpenHands

- **What.** The reference open-source AI software-development platform. **The repository split in 2026:** `OpenHands/OpenHands` is now "Agent Canvas", the self-hosted control centre (React/TypeScript); the agent engine is `OpenHands/software-agent-sdk` (Python, MIT, v1.63.1 on 2026-11-20); schedules are `OpenHands/automation` (MIT) (https://raw.githubusercontent.com/OpenHands/OpenHands/main/README.md).
- **Maturity.** 94,165 stars, 12,605 forks, release `v1.44.0` on 2026-11-23, two to three releases a week, last commit 2026-11-23 (https://api.github.com/repos/OpenHands/OpenHands). Contributor count not found.
- **Licence, language.** MIT, "Copyright 2025 OpenHands contributors". The `enterprise/` folder is gone from the repository now (API 404). A third-party snippet said "MIT except `enterprise/`, under Polyform Free Trial"; **I could not verify that on the official repository.**
- **Who runs it.** The OpenHands company (openhands.dev, formerly All Hands AI). It sells OpenHands Cloud and OpenHands Enterprise (self-hosted; SSO, RBAC, budgets, GitHub-event automations, the GitHub resolver) (https://docs.openhands.dev/enterprise/enterprise-vs-oss.md).

### 1.6 Note: `agentic-software-factory` (two unrelated repositories with one name)

- `ankur-paan/agentic-software-factory` (MIT, Python): a ticket-to-commit pipeline of builder, two-tier gates, two reviewers, arbiter and a triage "Doctor". It is the **closest in spirit** (code-held exit-code gates, round caps of 5/4/4/2, park-and-escalate). But it is **an early prototype**: 9 commits, 1 author, 1 star, no releases, about 58 KB of Python, **no tests**, and README metrics that are self-reported (https://api.github.com/repos/ankur-paan/agentic-software-factory).
- `OmegaMc1331/agentic-software-factory` (MIT, Rust and TypeScript, 29 stars, 1 contributor): a local runtime with a worktree per task and an integration branch; a reviewer agent plus a policy engine decide pass or fail, three attempts. Read from the README and API only.
- **Not in the table.** Neither is mature enough to adopt; I take ideas from the first (§4).

**Not chosen, and why.** OpenCode++, ESF (Temporal and microVMs), `loki-mode` (BUSL, source-available, not open source) and "Ralph-style" loop scripts appeared in search results with small or young repositories. I did not read them.

---

## 2. The comparison table

Gov OS cells cite paths in this repository. Others cite the URLs of §1 and the docs named in each cell. "Held by code" and "prompt-held" are used as the audit 4 text uses them.

| Dimension | **Gov OS** | **Fabro** | **Archon** | **OpenHands** | **Foreman / Vercel** | **Ona memo (Software Factory)** |
|---|---|---|---|---|---|---|
| **Triggers and orchestration** | An Opus CTO session starts Sonnet leads; `gov launch` and `gov dispatch` are built, but leads start from `start_lead.sh` and a cron tick runs the old scratch dispatcher (`TOOL-MAP.md` rows 37 to 44). Git hook on `w2/integrate` (row 11). W8: "off" (§3) | CLI, REST, web UI; automations by API or cron only; no GitHub-event trigger documented; DOT graph with parallel fan-out (docs.fabro.sh/execution/automations.md, /workflows/stages-and-nodes.md) | YAML DAG; CLI, interval schedules, GitHub webhooks via plugin; chat-start claim conflicts with its own triggers page (guides/workflow-triggers.md) | UI, CLI, SDK, API; schedules; GitHub-event automations are Enterprise docs; sub-agents by `TaskToolSet` (docs.openhands.dev/sdk/guides/task-tool-set.md) | GitHub label, @mention, Linear, HTTP POST, red CI; six stations; durable on Vercel Workflows (README; vercel.com/docs/eve) | GitHub issues and labels are the state machine; about 17 cron and webhook automations every 15 to 120 min (`.ona/automations/*.yaml`) |
| **Code-held gates and fix loops** | `gov queue` merges on a scratch copy, runs selected tests, checks authorship and a dirty tree (row 58); `gov accept` (row 54). **21 % of live Contract items enforced on the path** (audit 4 §0). Red on the base **not built** (row 52); no auditor called on a red; hand merges bypass the queue (row 60) | **Engine holds it:** a command node passes on exit 0; the engine, not the model, picks the next node; `goal_gate`; `max_visits` per node; same failure three times trips a circuit breaker (docs.fabro.sh/workflows/transitions.md, /execution/failures.md) | **Engine holds it:** loops need `max_iterations` and exit by `until_bash` or `until_field`; exhaustion fails by default; a merge-gate script checks verdict-for-head, CI and base CI (guides/loop-nodes.md; reference/sdlc-workflows.md) | **No engine test gate.** A Stop hook with exit 2 can block, optional; the goal loop is judged by an LLM, 10 rounds; stuck detector on by default (docs.openhands.dev/sdk/guides/hooks.md, /convo-goal.md, /agent-stuck-detector.md) | In code: a `gh` allowlist, no push to `main`, reviewer sees the diff only, CI repair capped at 2 counted from PR comments. Whether the 2-round review cap is code or prompt: not confirmed (vercel.com/kb/guide/eve-software-factory) | **Prompt-held:** lint, test, E2E, "Closes #N", severity and the 3-strike CI cap (the agent counts `[ci-fix]` commits). The PR reviewer **merges its own PRs; the ruleset needs zero approvals** (`AGENTS.md`; `.ona/automations/pr-reviewer.yaml`) |
| **Human checkpoints** | Owner decides P1 (features, specs, KPIs, Contract, paid services, releases); pushes and sudo are his (`GOLDEN-WORKFLOW.md` rule 8). The decisions page and push are **not built** (row 21) | Human node; answer by CLI, UI, API or Slack; **fails closed** (missing input is never approval); `--auto-approve` to run dark (docs.fabro.sh/workflows/human-in-the-loop.md) | `wait` node (approval, select, form); durable pause; an answer must name its pause; no timeout; the `sdlc` pack never merges (guides/approval-nodes.md) | Confirmation policies `AlwaysConfirm`, `ConfirmRisky`; risk analysers; `execute_tool()` bypasses them (sdk/guides/security.md) | A human merges every change; unattended runs refuse anything needing approval; approval is bound to the reviewed commit (README; docs "software-factory/ai-sdk") | None by design: the loop is dark. `needs-human` label pauses an issue until someone comments (`AGENTS.md`) |
| **Memory** | `gov retrieve`: words, meaning, record graph, rerank, a second search by the agent; **a fresh 80 questions judged end to end at 95 %** (`GOLDEN-WORKFLOW.md` W4). Store behind HEAD today; bundle cut at 6,000 tokens against "uncut" (row 8) | **None across runs** found; git checkpoints and event logs only (docs.fabro.sh/getting-started/comparison.md; /execution/checkpoints.md) | **None** (no RAG or vector store); run logs, SQLite, per-project state dir (archon.diy/getting-started/why-archon/) | `AGENTS.md`, skills triggered by keyword or path; no retrieval (docs.openhands.dev/overview/skills.md) | A flat "factory brain" of notes in Blob; unattended runs cannot write it (README) | Markdown in `.agents/` and `docs/` plus issues; a weekly auditor checks freshness (`.agents/README.md`) |
| **Context use** | Fresh orchestrators each morning from a handover; helpers from a written brief, never forks; `gov brief` carries memory (rule 10, W8); the cost of a wake is being measured (DEC-1229) | Fidelity modes per edge; compaction at 80 % of the window; outputs over 100 KB become files; loads `AGENTS.md` and `CLAUDE.md` (docs.fabro.sh/execution/context.md) | Per node `fresh`, `shared` or `resume`; hand-over by artifact files (reference/workflow-language.md) | `LLMSummarizingCondenser` on by default (sdk/guides/context-condenser.md) | Reviewer never sees the implementer's reasoning; compaction at 0.75; session output capped at 100,000 tokens (kb/guide/eve-software-factory) | `AGENTS.md` loads each session; skills on match; no compaction found (ona.com/docs/ona/agents-md) |
| **Usage and cost** | `gov spend` brake at twice the projection, in `gov launch` (`src/gov/spend/brake.py:31`); `check` never scheduled (row 47); plan-usage watchers are scratch scripts (rows 82, 83); no per-stage figures yet (A-36) | Per-stage tokens and cost in micro-dollars by API; no budgets found; the docs contradict each other on cost tracking (docs.fabro.sh/api-reference/run-outputs/retrieve-run-usage.md) | Per-run metrics with intervals; per-node `maxBudgetUsd` (Claude only) and a run budget; Codex has no cost, so sums are floors (guides/metrics.md) | `max_budget_per_run` checked after each step, so it can overshoot; org budgets at the managed gateway (sdk/guides/metrics.md) | Per-session output-token cap only; no cost tracking found | None visible; credits are Ona's, price not published (ona.com/docs/ona/billing/usage.md) |
| **Model routing** | By role in code: Opus for the CTO and senior engineer, Sonnet for the rest, Fable refused (`src/gov/launch/launcher.py:107`; `.claude/hooks/agent_model.py`, rows 37, 57); **one vendor**; a change comes to the owner first (rule 7) | `model_stylesheet` sets model and effort per node; about a dozen providers; ordered fallback chains; no routing by difficulty (docs.fabro.sh/workflows/stylesheets.md) | Provider and model per node (Claude Code, Codex, Pi); tiers in configuration (not read in depth) | LiteLLM names; fallback on transient errors; router "under development" (sdk/guides/llm-fallback.md, /llm-routing.md) | Fixed per station through AI Gateway; **reviewer and implementer on different vendors** (kb/guide/eve-software-factory) | Not set in the automations; Ona decides; docs list only an OpenAI family (ona.com/docs/ona/agents/llm-providers/overview.md) |
| **Decisions and escalations** | A register of decisions numbered up to DEC-1242; levels P3, P2, P1 and emergency (`GOLDEN-WORKFLOW.md` rule 8); **level computed by code is not built** (T-1, DEC-1242, first slice approved); `gov decisions` has `basis` and `in-force` only (row 17) | Failure routing, then a human gate, else the run fails; failure class written to context; **no decision records** (docs.fabro.sh/execution/failures.md) | Attention items in a queue; the `sdlc` pack pauses on stated conditions; no durable decision record (reference/sdlc-workflows.md) | Confirmation prompt; stuck, budget and iteration stops; no register | `awaiting-input` ticket; public-API changes wait for approval; no register | The agent sets severity from prompt bands; `needs-human`; "never fail silently"; no register (`AGENTS.md`) |
| **Adopting an existing repository** | `gov adopt` stage chain A0 to A10 and AS, a path map, spec audit, memory build, legacy retired (row 1); imports spec approved, not built; **verdict stage not at HEAD** | `fabro repo init` writes `.fabro/project.toml` and a starter workflow; runs on a clone; Linux and Apple Silicon only (docs.fabro.sh/getting-started/quick-start.md) | Add `.archon/`; `archon setup`; plugins (reference/archon-directories.md) | Add `AGENTS.md`, `.agents/skills/`, `.openhands/hooks.json` (usage/customization/repository.md) | Set repo and label, install a GitHub App, `eve deploy`, protect the default branch (README) | `AGENTS.md`, `.agents/`, a devcontainer, `.ona/`, labels, a ruleset, an Ona org (memo README) |
| **Licences** | **No `LICENSE` file** in the repository root or `template/` (`ls`, 2026-11-24) | MIT (two holders: Lithos Computer Co., Qlty Software Inc.) | MIT | MIT core; enterprise licence not verified | Foreman MIT; `eve` and `ai` Apache-2.0; `ai-sdk-factory` repository not public | **None** (all rights reserved); engine closed; `gitpod-io/gitpod` AGPL-3.0, legacy |

**Sandboxes (the owner's caution), compared and not assumed.**
- **Gov OS** has none, on purpose: worktrees only (EMERGENCY-2 §2.2).
- **Archon** is closest: a worktree per run, and its docs say plainly it is "not an execution or security sandbox".
- **Fabro's** default is a Docker clone. It has **no provider that runs in place** in your checkout or worktree; a local sandbox runs in a clone under the run directory (docs.fabro.sh/administration/security.md).
- **OpenHands** recommends Docker; the open-source Canvas runs without isolation.
- **Foreman** uses one Vercel Sandbox per station with egress limits, central to its design.
- **memo** uses Ona environments (dev containers on the customer's runner).
- Whether their sandbox is better for Gov OS is the owner's call on §2.2. My finding is only that **Fabro and Foreman assume one; Archon and OpenHands can run without**.

---

## 3. What Gov OS has that they lack, and what they have that it lacks

### 3.1 Gov OS has, and they lack

Each is stated by their own docs or by the absence in them (a "not found" is not proof, so I mark it).

| Gov OS has | Evidence on their side |
|---|---|
| **Memory-first retrieval**, measured end to end at 95 % on a fresh 80 questions, with a record graph and a rerank (`GOLDEN-WORKFLOW.md` W2 to W4) | Fabro: none across runs found. Archon: "no knowledge base or RAG". OpenHands: files loaded, no retrieval. Foreman: flat notes. memo: markdown files. |
| **A decision register with levels** (P3, P2, P1, emergency), basis lines, standing decisions and a graph to specs and tickets | None has a register or a decision record (§2 row "Decisions"). |
| **An independent test designer**: acceptance tests written from KPIs only, red on the base, authorship checked at the land | Archon's docs say its `sdlc` pack has no test-first step. Foreman's acceptance criteria come from its own Analyst. memo: "same agent family writes code and tests". ASF-A: builder judged by reviewers, no pre-written tests. |
| **An impact-selected landing** (changed paths to tests by the path map, authorship, paths, close record) | Their gate is CI or the repository's own checks plus an agent's review (Archon merge gate: verdict, CI, base CI; Foreman: CI and branch protection; memo: CI). |
| **An adoption stage chain** with a path map, spec audit and verdict (W1) | They add config files to a repository; none audits specs or classes legacy. |
| **Plan-aware, trace-aware governance** (record graph, `gov impact`, `gov links`), even though most of it runs only when typed | None traces decision to spec to ticket to test. |
| **A written escalation rubric** the owner approved (`T2-ESCALATION-RUBRIC.md`) | They escalate by a label, a node edge or a prompt. |

### 3.2 They have, and Gov OS lacks (or has built but off the path)

| They have | Where | Gov OS today |
|---|---|---|
| **Loop caps and exits held in code.** Archon requires `max_iterations` and exits by `until_bash`; Fabro has `max_visits`; ASF-A has round caps | Archon guides/loop-nodes.md; Fabro tutorials/branch-loop.md | `GOLDEN-WORKFLOW.md` W10 says "builds until `gov accept` is green" with **no cap**; two review rounds are a rule, and `ESCALATION_AT = 3` in code (`close/state.py:17`, row 59). The only count-free brake is `gov spend` at twice the projection |
| **A circuit breaker on a repeated failure**, with named failure classes (transient, deterministic, budget, compilation loop, structural) | Fabro docs.fabro.sh/execution/failures.md | None. A red landing is "one cause per red" by an agent's diagnosis (B6), not by a signature |
| **A stall or stuck detector with thresholds** (same action and result 4 times; ping-pong 6) | OpenHands sdk/guides/agent-stuck-detector.md | W15 says "stalls are caught"; the CTO-stall push is in the old dispatcher and moves in W2-207 RT-3 (`DAEO-rt4s.md`) |
| **Durable human gates** with fail-closed answers, an answer that must name its pause, and an explicit `--auto-approve` | Fabro; Archon | The decisions page and `gov decisions answer` are not built (rows 17, 21; T-1 slice approved) |
| **Per-stage usage and cost records** (tokens, cache, cost, by model) | Fabro API; Archon metrics | No per-stage figure; daily usage is a scratch script (rows 83, 85; A-36) |
| **Run observability**: a live view of stages, an event stream, checkpoint, resume and fork | Fabro docs.fabro.sh/execution/observability.md | `gov status` is "one read" and never refuses (row 86); no live run view |
| **A reviewer on a different vendor that sees only the diff** | Foreman README | One vendor, Sonnet reviewers by rule 7. The independent auditor is a fresh read-only session, which gives the same isolation of context but not of vendor |
| **A verdict bound to the reviewed commit** | Archon merge gate; Foreman approvals | Not verified for Gov OS READY (computed by code from verdict blocks, EMERGENCY-2 §4.4); I did not check the binding to a head commit |
| **Failed runs turned into evals** | Foreman | W2-81's proving ground plants cases by hand; step four plants ten cases (DEC-1240) |
| **Fallback chains and a per-node model stylesheet** | Fabro | Not needed with one vendor and a rubric by role |
| **Dedup keys and one action per run** for event-driven work | memo incident responder | The dispatcher "does not start a ticket twice" through a claim, but `tasks/claims.claim()` has no caller (row 50) |

**What they have that is not worth having for Gov OS.** Sandboxes as the default (§2.2); GitHub-label queues (Gov OS's ready list is the tickets and `gov plan --ready`); an agent that merges its own PRs with no approval (memo), which is the opposite of the landing; cron every 15 minutes to poll (the dispatcher is event-aware).

---

## 4. Each useful piece, classed

The imports rule (`IMPORTS-ADOPTION-SPEC.md`): **use** is a dependency the repository runs on and does not own; **absorb** is taking useful parts into the repository's own code or spec; **study** is reading it and taking ideas; **build** is ours. DEC-1228 (3) adds that code reached by study is classed absorb before use in a product, with its licence assessed. The spec says: "licence is a note, never a gate", and a copyleft or unrecognised licence on an absorb candidate is named in the assessment. I class each piece as the outcome I recommend now.

| # | Piece | From, licence | Class | What it would replace or serve in Gov OS |
|---|---|---|---|---|
| 1 | Loop exit by code, a required cap, fail on exhaustion | Archon, MIT | **study, then build** | The cap W10 and W12 lack (`GOLDEN-WORKFLOW.md` W10, W12; `ESCALATION_AT`, row 59). Small: a count and a stated outcome in the queue's fix path and the lead's return form (A-7) |
| 2 | Circuit breaker on a repeated failure signature; failure classes | Fabro, MIT | **study, then build** | W11's red diagnosis form (B6) and W15's stall catch (W2-207 RT-3); one signature check |
| 3 | Stuck-detector thresholds | OpenHands, MIT | **study, then build** | W15 stall watch (rows 44, 82; `DAEO-rt4s.md` RT-3). Thresholds are design, not code to take |
| 4 | An answer that must name the pause it targets; fail-closed gate | Archon, Fabro, MIT | **study, then build** | `gov decisions answer` (T-1, DEC-1242): refuse a stale answer, treat missing input as no |
| 5 | Per-stage usage and honest cost floors | Fabro, Archon, MIT | **study, then build** | The daily usage and context figures (A-36, rows 83, 85) and `gov spend`'s projection. Gov OS is plan-billed, so tokens, not dollars, are the honest unit (§6 SQ-1) |
| 6 | A verdict bound to the head commit | Archon, Foreman, MIT | **study** | Check that READY is bound to a head; if not, a fix in W11 (not verified, §7) |
| 7 | A reviewer from a different vendor that sees only the diff | Foreman, MIT | **study** | Nothing now; a spec question (§6 SQ-3) |
| 8 | Run observability: stage view, event stream, fork | Fabro, MIT | **study** | W15's `gov status` (row 86). Not needed for the integration; Wave 3 from friction (EMERGENCY-2 §3.2) |
| 9 | A weekly auditor of the harness and docs; `needs-human` requeue on a comment | memo, **no licence** | **study (ideas only)** | W16 weekly hygiene (row 92) already names the weekly doctor and basis review. **Never absorb text or code**: no licence is a grant of none |
| 10 | Park stopped work under a named ref; builder model excluded from review | ASF-A, MIT | **study** | `gov backup` and worktrees keep work (row 81). Its `git reset --hard` after a park is the opposite of "never lose work" |
| 11 | The whole Fabro engine | MIT | **study; do not use now** | Would replace W8 and W15 rows. §5 |
| 12 | The whole Archon engine | MIT | **study; do not use now** | The same. §5; revisit by the §5.4 check |
| 13 | The OpenHands SDK as a coding agent | MIT | **do not use** | Gov OS drives Claude Code sessions; an SDK agent would be a second agent to govern and a second bill |
| 14 | Foreman and `eve` | MIT, Apache-2.0 | **do not use** | Built for Vercel's platform (Workflows, Sandbox, Gateway) |

**Licence summary.** Everything worth studying is MIT or Apache-2.0, so a study or an absorb can proceed with the licence noted. Two exceptions: **memo has no licence** (ideas only), and **OpenHands' enterprise terms are not verified** (do not touch enterprise code). The old `gitpod-io/gitpod` is AGPL-3.0: never absorb. **Gov OS itself has no licence file**, which does not block any of this; it matters only if an engine or Gov OS code is ever shared (§6 SQ-4).

---

## 5. The plain answer

**Would adopting one of their engines serve better than finishing our integration? No, not now.** My recommendation is to finish the integration, build the six small pieces of §4 rows 1 to 5 inside it, and set one check for when to look at an engine again. The decision is yours.

### 5.1 What an engine would replace, and what it could not

- **It could replace** the launch and run rows of the tool map: rows 36 to 50 and 82 to 85, about **19 of the 102 rows**. In the golden workflow that is W8 (launch) and W15 (run), and the loop wiring inside W10 to W12.
- **It could not replace**, and none of the six has an equivalent for: memory and its measure (W2 to W4), decisions (W5), the trace (W6), plan (W7), test-first (W9), the landing's checks (W11), release and update (W13, W14), adoption (W1), weekly hygiene (W16). Gov OS would call its own `gov accept`, `gov queue` and `gov retrieve` as command nodes in the engine's graph, so the checks would stay ours either way.
- **The orchestration is not the weak part.** `gov launch`, `gov dispatch`, `gov resources`, `gov spend` and `gov pause` exist in `src/gov` (rows 37, 42, 45, 47, 48). The tool map's finding is that Gov OS "runs itself around" them (DEC-1238 (3)), not that they are missing. W2-207's cut-over slice is `est_loc: 500` over slices 1 to 3 already built (`.tickets/DAEO-rt4s.md`).

### 5.2 The case for adopting, stated fairly

- Fabro and Archon already hold, by engine code, the three things Gov OS lacks in W10 to W12: a loop cap, a circuit breaker and durable gates (§3.2). Both are MIT. Archon runs in worktrees with no sandbox, as Gov OS does, and lists Claude Code as a provider.
- An engine gives run observability, resume and fork that Gov OS has no plan for.
- It would give a second, independent place where a step is "held by code", which helps the 90 % target (P-6).
- A bypass is harder when the work only runs through the engine.

### 5.3 The case against, with the cost in the plan's terms

| Cost | What it breaks or adds |
|---|---|
| **The bypass is not caused by a missing engine.** Leads start from a script because `gov launch` was never made the only start (DEC-1238 (3); rows 37, 38) | An engine becomes a second tool beside `gov launch` and `start_lead.sh`. Unless the cut-over discipline changes (G-5: each duplicate retires the day the product's tool takes over), it is bypassed as the first was |
| **Fit with EMERGENCY-2 §2** | **Fabro** runs only on clones (Docker, Daytona, local copy), with no provider in the owner's worktree (docs.fabro.sh/administration/security.md). Gov OS's tools read the store and the worktree at HEAD (`TOOL-MAP.md` rows 5, 25, 54). **Archon** fits (worktree, no sandbox). **OpenHands** and **Foreman** assume Docker or Vercel Sandbox |
| **Billing and the plan** | Fabro holds provider keys (`fabro provider login`, `fabro secret set`); OpenHands uses LiteLLM. Gov OS runs on Claude Code sessions under the owner's plan, with plan-usage watchers at 95 and 99 % (rows 82, 83). **A paid service is the owner's** (rule 8, P1). Whether Fabro or OpenHands can drive the `claude` CLI under the plan: **not verified**. Archon lists Claude Code as a provider; whether that uses the plan login: not verified |
| **Maturity** | Fabro: every release a nightly, "research preview", one author with most commits. Archon: pre-1.0, a "wait" node replaced "approval", loops reworked in the last releases (CHANGELOG), one maintainer; telemetry on by default. A pinned engine that moves this fast would break `gov update` (W14) |
| **The integration test and the exit** | DEC-1240's scratch repository test and DEC-1239's exit are written against `gov launch`, `gov dispatch` and `gov queue`. Moving the orchestration layer moves the target; EXAMIN's planning waits for integrated Gov OS (DEC-1238 (4)) and would wait longer |
| **The Contract and adopted repositories** | The Contract items for W8 and W15 name the product's tools (`CAP-23.b`, `CAP-64.a` close under W2-207). They would need a re-baseline. Adopted repositories would get an engine to pin, check and start (P-7: not shipped, but pinned and started by `gov update`), one more thing to refuse on a small machine (P-8) |
| **Memory and the register** | **Not broken.** Neither depends on the engine, and the engine has no equivalent. The memory store, rebuild hook and register are unaffected. This is the strongest reason it is not a rewrite |
| **What it would not fix** | G-1 (stale memory), G-2 (72 folders), G-3 (hand-written briefs), G-6 to G-8 (records and path map), and W5 (decisions). These are the largest gaps in the tool map's §3 and none is orchestration |

### 5.4 Recommendation

1. **Finish the integration** as DEC-1238 (7) lays it out. It is mostly wiring built tools.
2. **Build, inside it**, §4 rows 1 to 5: a loop cap and a stated exhaustion outcome in the fix path (row 1); a failure signature breaker in the red-landing record (row 2); stall thresholds in the W2-207 stall watch (row 3); the fail-closed, pause-named answer in `gov decisions answer` (row 4); per-stage token figures in the daily usage line (row 5). Each is small; none is a new ticket (a fix under its owning ticket, or part of a ticket already approved). I did not size them beyond "small".
3. **Study, as a read-only chore**, Archon's loop and wait code and Fabro's failure routing when W2-207 and the decisions slice are written, so we copy the semantics, not the code.
4. **When to look at an engine again** (a check, not a date): if step four's scratch run (DEC-1240) shows the run-time tool failing the dispatcher, load balancer or fix-loop cases for a reason of **workflow expression** (parallel branches, durable pause, resume) rather than a bug, **or** if the owner wants a live run view. At that point Archon is the candidate to read first (worktree, no sandbox, MIT, Claude Code provider), and only after it reaches 1.0 or the maintainers stop changing node semantics.
5. **Do not use** OpenHands' SDK, Foreman or `eve`, or any engine whose sandbox is the default.

---

## 6. Spec questions found (decision records, DEC-1238 (10))

None of these stops work.

### SQ-1: Is an engine's API billing acceptable, or must orchestration stay on the owner's Claude plan?

- **Question.** Rule 8 makes "a secret or a paid service" the owner's. EMERGENCY-2 and the rubric (rule 7) name only Claude models run through Claude Code under the plan, with plan-usage watchers (rows 82, 83). No spec says whether a tool that bills provider keys by token may ever run Gov OS's agents.
- **Found.** Fabro holds provider keys (docs.fabro.sh/getting-started/quick-start.md); OpenHands names models by LiteLLM; Archon lists Claude Code as a provider. Whether each can use the plan login: not verified.
- **Options.** (a) Plan only; an engine must drive the `claude` CLI or be refused. Cost: rules out Fabro and OpenHands unless they drive the CLI. (b) Allow API keys for one named job at a time, as a paid-service decision. Cost: a new cost line, with `gov spend` in dollars. (c) Leave open until an engine is chosen.
- **Recommendation.** (c). §5 recommends no engine now; record the constraint when one is considered.
- **Sources.** `GOLDEN-WORKFLOW.md` rule 7, rule 8; `TOOL-MAP.md` rows 82, 83; https://docs.fabro.sh/getting-started/quick-start.md.
- **Stops work?** No.

### SQ-2: Does a step "held by an engine's graph" count as held by code?

- **Question.** P-6 (DEC-1241) sets the 90 % floor on "steps held by code". The enforcement field's classes (audit 4) are about code that refuses. If an engine's graph routes a step, the refusal is in a third-party engine.
- **Found.** Audit 4's classes are enforced, enforced (off path), checked after, judgement, not built. No class for "held by a pinned third-party program". P-7 treats a third-party program as "outside the product" but pinned and checked.
- **Options.** (a) Count it as code if the engine is pinned and its behaviour is checked by a test of ours. (b) Count it as a new class below "code", above "judgement". (c) Do not count.
- **Recommendation.** (a), only if an engine is adopted. Not needed today.
- **Sources.** DEC-1241 P-6, P-7; `E2-AUDIT-4-DETERMINISM.md` §0; `GOLDEN-WORKFLOW.md` §3.
- **Stops work?** No.

### SQ-3: Is review by a model from another vendor wanted?

- **Question.** Foreman's reviewer is on a different vendor from its implementer, so a shared blind spot is less likely. Rule 7 says every agent other than the two Opus orchestrators runs Sonnet, "critical work included". The rubric is silent on vendor.
- **Found.** Foreman (kb/guide/eve-software-factory): orchestrator, classifier, analyst, researcher and reviewer on one vendor's model; the implementer on another. Fixed in code.
- **Options.** (a) Keep one vendor. Cost: none. (b) A trial: the independent auditor on a second vendor for one wave, measured. Cost: a paid service (SQ-1), a second tool to pin, a hidden-set risk if outputs leave the machine. (c) Add to R-4's "measured trial after the integration".
- **Recommendation.** (a) now; (c) after the integration, beside R-4's medium-effort trial.
- **Sources.** `GOLDEN-WORKFLOW.md` rule 7; DEC-1242 R-4, R-5; Foreman README.
- **Stops work?** No.

### SQ-4: Gov OS has no licence file

- **Question.** Neither the repository root nor `template/` holds a `LICENSE`. Adopted repositories get the kit by `copier`. No spec says what licence the kit carries to them or what Gov OS may be shared under. The imports rule treats an unrecognised licence as a note; it has never been asked of Gov OS itself.
- **Found.** `ls LICENSE*` at the root and in `template/` finds none, and `pyproject.toml` names no licence (2026-11-24).
- **Options.** (a) Leave it; the owner keeps all rights and the kit is private to his repositories. Cost: none today; a question the day anything is shared. (b) State "all rights reserved" in a file. Cost: a chore. (c) Choose a licence now. Cost: an owner decision with a business angle.
- **Recommendation.** (a) now; revisit before any share (the secrets scan before a repository goes public is already tied to that moment, EMERGENCY-2 §2.11).
- **Sources.** `ls`, `pyproject.toml`; `IMPORTS-ADOPTION-SPEC.md` "Licence is a note, never a gate".
- **Stops work?** No.

### SQ-5: The build and fix loops have no stated cap

- **Question.** `GOLDEN-WORKFLOW.md` W10 says the engineer "builds until `gov accept` is green", and W12 and W11 say a red calls an engineer to fix. Review has a cap (two rounds, then the owner, DEC-1204 (3)). No spec caps the build loop or the fix loop, or says what happens on exhaustion. Every engine and prototype I read caps its loops (Fabro `max_visits`; Archon required `max_iterations`; Foreman 2; ASF-A 4 to 5).
- **Found.** Code has a cost brake at twice the projection (`brake.py:31`), not a count; W15 says "stalls are caught" without a rule; `ESCALATION_AT = 3` is the stale review cap (`close/state.py:17`).
- **Options.** (a) Cost only: the spend brake plus the stall watch are the cap. Cost: nothing new; a fix loop that spends little can still go in circles. (b) A count (for example three fix rounds on one failure signature), then the CTO decides at P2. Cost: a small code change; one more number to justify. (c) Count plus signature (the same failure three times).
- **Recommendation.** (c): a count on the same failure signature, with the exhaustion going to the CTO (P2, per rule 8 "a red landing"), and the brake kept as the cost cap. It adds no owner decision, because the CTO decides a red landing already.
- **Sources.** `GOLDEN-WORKFLOW.md` W10 to W12, W15; `src/gov/spend/brake.py:31`; `TOOL-MAP.md` row 59; Fabro docs.fabro.sh/execution/failures.md; Archon guides/loop-nodes.md.
- **Stops work?** No, but it should be answered before the plan's W10 to W12 items are fixed.

---

## 7. What I could not verify

- **Source code.** I read docs, READMEs and APIs, not the engines' source. Whether Fabro's GitHub webhook route does anything, whether Foreman's revision cap is in code, and Archon's container-isolation guide are not read.
- **Provider and billing.** Whether Fabro, Archon or OpenHands can use a Claude Code plan login rather than API keys: not verified (SQ-1).
- **OpenHands enterprise terms** and where its enterprise code lives now: not verified. Contributor count: not found.
- **Fabro:** total release count and any cross-run memory in the source: not found. The docs contradict each other on cost tracking.
- **Archon:** whether chat can start a run in 0.14: the README and the triggers page disagree.
- **Ona:** credit unit and price, who chooses the model, local runs, and the other 14 automations: not found or not read. The site's figures (375, 489, 688 PRs) vary by date.
- **Vercel:** the `ai-sdk-factory` repository and its licence: not public. Cost tracking and how its workflow runs durably: not found.
- **The Gov OS side.** I did not re-run the tool map's counts. Whether READY is bound to a head commit (§4 row 6): not checked. The figure "about 19 of 102 rows" is my count of rows 36 to 50 and 82 to 85 of `TOOL-MAP.md`; the decision count is not used.
- **Memory.** The `gov retrieve` store was stale, so no memory bundle was used; every Gov OS claim is from a file read.
