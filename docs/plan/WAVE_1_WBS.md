---
id: WAVE-1-WBS
status: PROPOSED
depends_on: [CHARTER-v5, CONTRACT-v4, ADR-0002]
decisions: [DEC-065, DEC-076, DEC-080, DEC-083, DEC-084, DEC-086, DEC-087, DEC-088, DEC-089, DEC-090, DEC-091, DEC-092, DEC-093, DEC-094, DEC-096, DEC-102, DEC-103, DEC-104, DEC-105, DEC-106, DEC-119, DEC-136, DEC-137, DEC-150, DEC-152, DEC-153, DEC-154, DEC-155, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162, DEC-163, DEC-164, DEC-165, DEC-166, DEC-167, DEC-168, DEC-169, DEC-170, DEC-171, DEC-172, DEC-174, DEC-179, DEC-180, DEC-182]
---

# Wave 1 (Integrate) — work breakdown

Generated from the closed Gov OS specification (MR-2): Charter v5, Contract v4 (version 4.1) and ADR-0002. Tickets W1-45…W1-48 and the KPI lines that cite DEC-102…DEC-174 were added by the S2 specification change and its repairs after the S2-A round-1 and round-2 audits and the round-3 closure check (`docs/changes/S2-CIT-P.md`, `docs/changes/S2-CIT-E.md`). Every item is a `ticket` in `.tickets/`; the `wbs_id` field (and `external-ref`) carries the W1 number, and the old G-numbers are kept as `sources` (`G-xx` = S0b2 GLUE_REQUIREMENTS; `S0a-G-xx` = S0a STACK_OPTIONS §3).

**Rules for every ticket.**
- **READY rule:** an implementation ticket is READY only when `tests/acceptance/<ticket-id>/` exists. The Independent Test Designer writes those tests from the ticket's KPIs and Contract v4 before implementation starts (MR-3, DEC-069).
- **Bootstrap:** until W1-02, W1-03 and W1-04 pass their acceptance tests, MR-3 is held by the settings deny rules of W1-01 and the operator's diff check. From W1-05 on, every ticket runs under the live guard (DEC-084).
- **Installs:** no tool is installed before W1-05. Until then the interim rule of W1-01 holds: install commands are denied in every session's settings. From W1-05, the DEC-083 rule is enforced by W1-04: `ask` for the orchestrator, also in Auto mode, and `deny` for every other role. W1-06, the first install, depends on W1-05. Worker roles never install system-wide (DEC-157). The research role may install only into a venv or local prefix inside its own experiment folder, within its ticket's `allowed_paths`; the sandbox's write fence enforces this (DEC-163). Inside the repository the fence is a list of `Edit` deny rules the launcher generates at launch, because the sandbox always leaves the working directory writable (EXP-001 §3.4, §5.3). The deny list is computed at launch; a path created later is covered by the guard's per-ticket allow-list, and the list leaves out `.git/` and any entry whose name contains `*`, `?` or `[` (EXP-001 §1). The guard's install rule decides install commands alone: W1-47 removes the install and download ask rules from the committed `.claude/settings.json` (DEC-172), and extends the rule to `uv add`, `uv sync`, `uv run --with` and `uvx` (DEC-174). Raising the Claude Code pin (W1-48) is an orchestrator install under DEC-083.
- **Paths:** no implementer ticket's `allowed_paths` covers `tests/acceptance/**`.
- **Orchestrator write scope** (DEC-156, W1-45). The orchestrator may write anywhere in the repository except `tests/acceptance/**`; the guard enforces only that exclusion for it, and containment still records its changes. Its session is not sandboxed. Its checkpoint lives in `.gov-runtime/scratch/orchestrator/` until W1-25. An orchestrator change outside the active ticket's `allowed_paths` is a record, not a containment finding (DEC-171); a change under `tests/acceptance/**` stays a finding. The acceptance tests of W1-02 and W1-03 that assert the old orchestrator rule are revised by the Independent Test Designer in W1-45's test design batch, as rewrites after implementation (reason: owner correction, DEC-156). W1-45 is `in_progress` and is bootstrapped as DEC-150 states: the test designer writes its tests with the ticket in its `GOV_TICKET`, an `engineer` subagent implements it and commits its own work, and the owner closes it from the operator console.
- **Worker sessions** (DEC-161, W1-46). Once W1-46 is closed, engineer, test designer, auditor and research or experiment work runs as worker sessions started by `gov launch`, inside the OS sandbox with the role's network profile (DEC-158). In-session subagents remain for read-only work (review, exploration, web research). The launcher sets no `excludedCommands` (DEC-164).
- **Research role** (DEC-163, W1-46). The Wave 1 roster has a minimal research role, a role file delivered with the launcher. Its network profile is the research allowlist of DEC-158. The full research lifecycle (CAP-32) stays in Wave 3.
- **Impact questions** (DEC-167). "What's the impact of X?" in plain language triggers the impact assessment: in Wave 1, an OpenSpec proposal plus `gov closure` (W1-35); from Wave 2, `gov impact`.
- **Experiments** (DEC-102) are part of discovery and can run at any point; they run outside production paths, leave an evidence record, and change this plan only through CIT-P with three costed options (DEC-105).
- **Order of specification work** (DEC-103): discovery and research, scenarios, representative data, UX for a feature with a user interface, acceptance tests, implementation.
- **Probes** (DEC-136, DEC-137). A case the orchestrator's review finds goes to the next test design batch as a described behaviour, never as code. A FULL ticket's post-green probe is done by a fresh reviewer that writes nothing.
- **Learning metrics** (DEC-106). Per ticket: KPI disputes raised by the test designer; acceptance tests rewritten after implementation began, with the reason; governance share. W1-31 records them at close and W1-42 reports them at the exit. Only governance share has a threshold (≤ 15 %).
- **Commit trailers** (DEC-182). Every commit puts `Task:`, `Implements:` and `Role:` in the final trailer block, using `git commit --trailer`, because git reads trailers only from the last paragraph of a commit message. Checks that read trailers fall back to the message body for commits made before 2026-10-03. History is not rewritten.
- **Gap tickets:** every required open readiness row has a linked gap ticket (DEC-089).
- **Covers items:** every Wave 1 `covers` item of Contract v4 is named by a KPI line of the ticket that delivers it. The line ends with the item id in brackets, for example `[CAP-03.b]`, and the contract item names that ticket as its `provider`. `docs/plan/tools/validate_s1.py` checks this both ways.
- **Dependencies carry the KPIs:** a ticket depends on every ticket whose output its KPIs need. Each governance test family's check is registered by the ticket that builds its subject, and W1-42 asserts that 17 of 17 families have an executable check.
- **Audits:** closing a spine, STANDARD or FULL feature specification creates an audit ticket for a fresh Independent Auditor (DEC-088).
- **Loop policy** (DEC-096, amending DEC-044). Every review→repair, audit→repair, test→fix or verification loop runs until it converges, or until three consecutive iterations fail to converge. The third failure goes to the owner as an escalation package. The orchestrator or `gov` holds the count and never discloses it to the sessions inside the loop.

## 1. Tickets

| W1 | ticket | Title | Class | Role | Profile | Depends on | est. LOC | Sources |
|---|---|---|---|---|---|---|---|---|
| **W1-01** | `DAEO-dtv3` | Interim bootstrap guardrails | config | orchestrator | LITE | — | 30 | DEC-084, DEC-074 Q9, CAP-58, CAP-03 |
| **W1-02** | `DAEO-emkd` | PreToolUse default-deny guard | implementation | engineer | FULL | W1-01 | 200 | G-01, S0a-G-10, CAP-58, CAP-05, DEC-041, DEC-069, OWNER-DECISION-P2-0001 BC-P2-08, CAP-38, CAP-39, MR-3 |
| **W1-03** | `DAEO-8qvp` | Post-command containment check | implementation | engineer | FULL | W1-02 | 100 | G-02, DEC-076, CAP-58, MR-3 |
| W1-04 | `DAEO-78bn` | Install-approval rule | implementation | engineer | FULL | W1-02 | 60 | DEC-083, DEC-040, CAP-25 |
| **W1-05** | `DAEO-m7u4` | Dogfood switch-over | config | orchestrator | LITE | W1-02, W1-03, W1-04 | 20 | DEC-084, MR-3, CAP-22, DEC-119 |
| W1-06 | `DAEO-ipqy` | Wave 1 tool prerequisites | ops | orchestrator | STANDARD | W1-05 | 60 | DEC-083, DEC-086, DEC-074, CAP-25, CAP-40 |
| **W1-07** | `DAEO-drvn` | gov CLI skeleton | implementation | engineer | STANDARD | W1-05 | 220 | S0a-G-01, API-0002, DEC-046, CAP-27, CAP-28 |
| W1-08 | `DAEO-uudf` | Record schemas and templates | schema | product-spec | STANDARD | W1-05 | 200 | DEC-012, G-04, CAP-06, CAP-08, CAP-14, CAP-41, CAP-03, CAP-07, CAP-29, CAP-31, CAP-50, CAP-53, CAP-54, DEC-168 |
| W1-09 | `DAEO-topz` | Ticket vendoring, claims and READY rule | implementation | engineer | FULL | W1-07, W1-08, W1-10 | 100 | G-03, DEC-074, DEC-069, CAP-23, CAP-31, CAP-53, MR-2, MR-3, CAP-34 |
| **W1-10** | `DAEO-4yyl` | Store and record graph | implementation | engineer | STANDARD | W1-07, W1-08 | 260 | S0a-G-03, G-20, DEC-012, CAP-01, CAP-08, CAP-09, CAP-13, CAP-29, CAP-50 |
| W1-11 | `DAEO-be7u` | Decision checker and owner-approval facts | implementation | engineer | FULL | W1-08, W1-10, W1-34 | 310 | G-04, DEC-074 D2, DEC-046, CAP-21, CAP-51, CAP-01, CAP-34 |
| W1-12 | `DAEO-lc4q` | Readiness schema and proposal templates | schema | product-spec | STANDARD | W1-08 | 110 | G-07, G-09, DEC-085, CAP-30, MR-1 |
| W1-13 | `DAEO-w616` | gov readiness | implementation | engineer | FULL | W1-09, W1-12 | 170 | G-08, DEC-085, DEC-088, DEC-089, CAP-30, MR-1, MR-2, MR-4, CAP-47, CAP-53 |
| W1-14 | `DAEO-w9l3` | Proposal-to-ticket bridge | implementation | engineer | STANDARD | W1-09, W1-12 | 120 | G-05, CAP-31, MR-2 |
| W1-15 | `DAEO-7nne` | Secret rules and pre-index filter | implementation | engineer | FULL | W1-07, W1-08 | 70 | G-12, G-18, DEC-074 Q8, CAP-03, CAP-38 |
| W1-16 | `DAEO-lkeb` | codebase-memory wrapper | implementation | engineer | FULL | W1-15 | 50 | G-06, DEC-074 Q10, DEC-076, CAP-12, CAP-03 |
| **W1-17** | `DAEO-rxln` | Lexical index and shared store | implementation | engineer | STANDARD | W1-10, W1-15 | 240 | G-17, G-20, G-21, DEC-091, CAP-07, CAP-11, CAP-17, CAP-18, CAP-03, CAP-38 |
| W1-18 | `DAEO-1ve2` | Ollama on-demand lifecycle and fallback | implementation | engineer | STANDARD | W1-07 | 40 | G-22, DEC-074 Q4 |
| **W1-19** | `DAEO-t6hf` | Semantic retrieval, RRF and rerank | implementation | engineer | STANDARD | W1-17, W1-18 | 280 | G-17, DEC-074 R1, DEC-080, CAP-10, CAP-18 |
| W1-20 | `DAEO-jozo` | gov closure | implementation | engineer | STANDARD | W1-10, W1-16 | 100 | DEC-080, DEC-033, S0a-G-03, CAP-09, CAP-57 |
| **W1-21** | `DAEO-5x4l` | gov retrieve with completeness | implementation | engineer | FULL | W1-19, W1-20 | 300 | DEC-080, DEC-091, G-19, S0a-G-06, CAP-14, CAP-16, CAP-18, CAP-41, CAP-55, CAP-04, CAP-38, CAP-51 |
| W1-22 | `DAEO-8nue` | Evidence validator and zero-result canaries | implementation | engineer | FULL | W1-21 | 120 | DEC-080, DEC-036, DEC-037, CAP-17, CAP-55, CAP-57 |
| W1-23 | `DAEO-9i8e` | Hierarchical synthesis notes | implementation | engineer | STANDARD | W1-22 | 100 | DEC-080, DEC-030, DEC-036, CAP-15 |
| **W1-24** | `DAEO-wk2v` | gov context | implementation | engineer | FULL | W1-09, W1-10, W1-21, W1-34 | 350 | S0a-G-07, DEC-003, DEC-004, CAP-01, CAP-15, CAP-38 |
| W1-25 | `DAEO-rrxp` | gov checkpoint | implementation | engineer | STANDARD | W1-07, W1-08 | 180 | S0a-G-09, CAP-13, CAP-22, CAP-37, CAP-20, CAP-38 |
| W1-26 | `DAEO-fygv` | gov check G0-G2 | implementation | engineer | FULL | W1-09, W1-11, W1-13 | 290 | S0a-G-02, DEC-041, DEC-046, DEC-089, CAP-38, MR-2, MR-3, CAP-01, CAP-24, CAP-30, CAP-39, CAP-58 |
| W1-27 | `DAEO-xw3k` | gov doctor and gov rebuild | implementation | engineer | STANDARD | W1-04, W1-16, W1-17, W1-22 | 230 | S0a-G-04, DEC-083, CAP-02, CAP-06, CAP-07, CAP-20, CAP-25, CAP-46, CAP-48, CAP-54, CAP-38, MR-4 |
| W1-28 | `DAEO-9279` | gov pause | implementation | engineer | STANDARD | W1-02, W1-07, W1-09 | 80 | S0a-G-10, CAP-05 |
| W1-29 | `DAEO-zsvl` | Session hooks | implementation | engineer | STANDARD | W1-09, W1-24, W1-25 | 180 | DEC-025, S0a-G-09, CAP-15, CAP-37 |
| W1-30 | `DAEO-2lwj` | gov close | implementation | engineer | FULL | W1-03, W1-09, W1-24, W1-25, W1-26 | 220 | S0a-G-12, DEC-044, DEC-096, DEC-069, CAP-13, CAP-24, CAP-31, CAP-38, CAP-59, CAP-50, MR-3, DEC-137 |
| W1-31 | `DAEO-6mk8` | Governance share counter | implementation | engineer | STANDARD | W1-06, W1-29, W1-30 | 150 | DEC-086, DEC-004, CAP-04, CAP-40, CAP-53, DEC-106, DEC-138, DEC-170 |
| W1-32 | `DAEO-8goq` | gov status | implementation | engineer | STANDARD | W1-13, W1-28, W1-31 | 80 | S0a-G-01, CAP-28, CAP-27 |
| W1-33 | `DAEO-xog0` | Wave 1 role definitions | role-definition | product-spec | STANDARD | W1-05 | 300 | DEC-066, DEC-083, MR-5, CAP-47, CAP-22, CAP-58, MR-3, MR-4, DEC-119, DEC-154, DEC-156, DEC-163, DEC-158 |
| W1-34 | `DAEO-egm9` | Decision-package template | template | product-spec | LITE | W1-08 | 60 | DEC-065, DEC-093, MR-6, CAP-34 |
| W1-35 | `DAEO-0i6h` | Skills: discovery, planning, independent test design, change | skill | product-spec | STANDARD | W1-12, W1-13, W1-14, W1-21, W1-26, W1-33, W1-34 | 480 | DEC-066, DEC-088, DEC-089, DEC-093, MR-1, MR-2, MR-3, MR-4, MR-6, CAP-24, CAP-30, CAP-33, CAP-34, CAP-38, CAP-47, DEC-102, DEC-103, DEC-105, DEC-136, CAP-32, DEC-167 |
| **W1-36** | `DAEO-skiy` | Skills: retrieval, audit, checkpoint/resume, adopt | skill | product-spec | STANDARD | W1-21, W1-24, W1-25, W1-26, W1-33 | 480 | DEC-080, DEC-032, DEC-070, DEC-088, CAP-16, CAP-24, CAP-56, MR-4, CAP-38, CAP-47 |
| W1-37 | `DAEO-yvzh` | Superpowers three-skill vendoring | config | engineer | LITE | W1-06 | 20 | G-25, DEC-074 Q5, DEC-076, CAP-24, CAP-38 |
| **W1-38** | `DAEO-3ef2` | rulesync adapters and .claude ownership | config | engineer | STANDARD | W1-04, W1-29, W1-33, W1-35, W1-36, W1-37 | 50 | G-11, G-15, DEC-022, DEC-074 Q6, DEC-074 Q7, CAP-52, CAP-38, MR-5 |
| **W1-39** | `DAEO-5ylr` | Copier kernel template and lock | implementation | engineer | STANDARD | W1-27, W1-38 | 100 | G-14, S0a-G-15, DEC-023, DEC-027, CAP-02, CAP-43, CAP-44, CAP-54 |
| W1-40 | `DAEO-fdkq` | lefthook and CI workflow | config | engineer | STANDARD | W1-22, W1-26, W1-30 | 80 | S0a-G-11, DEC-075, DEC-087, CAP-39 |
| **W1-41** | `DAEO-cdoi` | gov adopt --lite and legacy importer | implementation | engineer | FULL | W1-27, W1-33, W1-38, W1-39 | 440 | S0a-G-13, G-10, DEC-006, DEC-090, CAP-06, CAP-42, CAP-44, CAP-54 |
| **W1-42** | `DAEO-gjjf` | Wave 1 exit run on the dev tiers | integration | orchestrator | FULL | W1-23, W1-32, W1-35, W1-36, W1-40, W1-41, W1-44, W1-46, W1-47 | 0 | DEC-080, DEC-086, DEC-088, DEC-089, DEC-091, MR-1, MR-2, MR-3, MR-4, MR-6, CAP-28, CAP-38, DEC-106, DEC-161, CAP-40 |
| **W1-43** | `DAEO-03pw` | Wave 1 exit audit | audit | independent-auditor | FULL | W1-42 | 0 | DEC-070, DEC-088, DEC-092, DEC-096, MR-4, CAP-47, CAP-59 |
| W1-44 | `DAEO-wqd6` | Phase-2 lessons as lesson records | documentation | product-spec | LITE | W1-08, W1-21 | 150 | DEC-046, OWNER-DECISION-P2-0008, OWNER-DIRECTION-BR-0004, OWNER-AMENDMENT-P2-0010, CAP-14, CAP-41, CAP-59, DEC-168 |
| W1-45 | `DAEO-6cc2` | Orchestrator write scope | implementation | engineer | FULL | W1-05 | 40 | DEC-150, DEC-156, DEC-112, DEC-106, DEC-171, MR-3, CAP-58 |
| W1-46 | `DAEO-jdqr` | Worker session launcher (gov launch) | implementation | engineer | FULL | W1-07, W1-47, W1-48 | 220 | DEC-152, DEC-153, DEC-158, DEC-159, DEC-161, DEC-163, DEC-164, DEC-172, DEC-174, DEC-180, EXP-001, CAP-49, CAP-58, CAP-61, CAP-22, CAP-25 |
| W1-47 | `DAEO-o4fg` | Guard hardening: escape hatch, failed commands, oracle path | implementation | engineer | FULL | W1-45 | 60 | DEC-152, DEC-153, DEC-162, DEC-172, DEC-174, DEC-179, DEC-083, EXP-001, CAP-25, CAP-49, CAP-58, CAP-62 |
| W1-48 | `DAEO-0qs5` | Claude Code version pin | ops | orchestrator | LITE | W1-06 | 10 | DEC-153, DEC-141, DEC-157, DEC-083, CAP-25, CAP-61 |

Bold rows are on the critical path. KPIs (success and failure criteria), `allowed_paths` and the acceptance-test path are in each ticket file.

## 2. Dependency order and critical path

Layers: a ticket depends only on tickets in earlier layers, so the tickets within a layer can run in parallel, subject to claims.

| Layer | Tickets |
|---|---|
| 1 | W1-01 |
| 2 | W1-02 |
| 3 | W1-03, W1-04 |
| 4 | W1-05 |
| 5 | W1-06, W1-07, W1-08, W1-33, W1-45 |
| 6 | W1-10, W1-12, W1-15, W1-18, W1-25, W1-34, W1-37, W1-47, W1-48 |
| 7 | W1-09, W1-11, W1-16, W1-17, W1-46 |
| 8 | W1-13, W1-14, W1-19, W1-20, W1-28 |
| 9 | W1-21, W1-26 |
| 10 | W1-22, W1-24, W1-35, W1-44 |
| 11 | W1-23, W1-27, W1-29, W1-30, W1-36 |
| 12 | W1-31, W1-38, W1-40 |
| 13 | W1-32, W1-39 |
| 14 | W1-41 |
| 15 | W1-42 |
| 16 | W1-43 |

**Critical path** (weighted by est. LOC; a ticket with no code counts as 50): W1-01 → W1-02 → W1-03 → W1-05 → W1-07 → W1-10 → W1-17 → W1-19 → W1-21 → W1-24 → W1-36 → W1-38 → W1-39 → W1-41 → W1-42 → W1-43.

Why this path:
- the guard and containment come first (DEC-084);
- then the CLI, the record graph and the R1 retrieval chain (lexical with parent ids → semantic → `gov retrieve` with parent expansion);
- then `gov context`, the audit and retrieval skills (which need the context pack), the adapters, the Copier template and adoption (with the A5 review, DEC-090);
- then the exit run and the audit.

**The S2 tickets are off the critical path** (recomputed 2026-10-03; the path and its tickets are unchanged). W1-45 → W1-47 hangs off W1-05; W1-48 hangs off W1-06; W1-46 hangs off W1-07, W1-47 and W1-48 (it follows W1-47 because both change the guard files, DEC-163). Their longest chains (W1-01 … W1-07 → W1-46, and W1-01 … W1-05 → W1-45 → W1-47 → W1-46) are far shorter than the retrieval chain, and both rejoin at W1-42, which now depends on W1-46 and W1-47.

## 3. Size

| Class | est. LOC |
|---|---|
| implementation | 5460 |
| skill | 960 |
| schema | 310 |
| role-definition | 300 |
| config | 200 |
| documentation | 150 |
| ops | 70 |
| template | 60 |
| integration | 0 |
| audit | 0 |
| **Total** | **7510** |

- **Glue code** (class implementation, Python): **≈ 5,460 LOC**.
- **Everything else** (markdown skills and roles, schemas, templates, YAML): ≈ 2,050 lines.
- **The one figure:** ADR-0002 quotes this total.
- **Why the code estimate is higher than earlier ones.** Architecture v0.3 put Wave 1 at ≈ 2,400 LOC, and S0b2's W1 glue list at ≈ 1,830 LOC. Wave 1 is now larger because:
  - DEC-080 moved all of retrieval completeness into Wave 1 (+≈ 400 LOC);
  - DEC-074 moved semantic retrieval and the reranker into Wave 1;
  - DEC-076 moved G-02 into Wave 1;
  - DEC-083 and DEC-086 added the install rule and the share counter;
  - the S1-A round-1 repairs added gap-ticket checks (DEC-089), parent-child retrieval (DEC-091), the A5 review and rollback in adoption (DEC-090), and the CANCEL_AGENTS, rollback and watchdog items from the covers lists (DEC-092);
  - the S1-A round-2 repair gave every Wave 1 `covers` item a ticket KPI (F-21), which added about 380 LOC across 13 tickets;
  - the S2 specification change added the orchestrator write scope (W1-45, 40), the worker session launcher with the minimal research role (W1-46, 220) and the guard hardening (W1-47, 60): +320 LOC (DEC-152, DEC-153, DEC-156, DEC-162, DEC-163);
  - the KPIs the S2 change added to existing tickets were re-estimated (S2A-F-09): W1-30 200 → 220 (the post-green probe record check) and W1-31 120 → 150 (the learning metrics and the sandbox token line, DEC-170), +50 LOC. The KPIs added to W1-33 (role definitions) and W1-35 (skills) fit their existing estimates: both are markdown, and W1-35's skill bodies are capped at 2.5k tokens each. W1-08's two lesson fields and W1-48's two registry entries also fit. The round-2 repair changes no estimate: removing the settings ask rules (DEC-172) fits W1-47's 60, and the launch-time deny list with its later-path test fits W1-46's 220. The four `uv` forms of DEC-174 are a few lines in the install rule and also fit W1-47's 60.
- DEC-064 makes the size check a per-wave review, not a stop.
- **Calibration:** the S0b2 prototypes (guard 174 LOC, decision checker 249 LOC, R1 retrieval 549 LOC) and the carried `cli/govbridge` FTS5 and chunking code.

## 4. Wave 1 exit criteria

Wave 1 exits when **all** of these hold. W1-42 runs the checks, and W1-43 is the independent audit:

1. **Spec-first cycle end to end** on the dev tier of both synthetic programmes (a-dev and b-dev clones). One feature per programme goes through:
   - discovery Q&A;
   - a closed specification (`gov readiness` passes; spines at FULL);
   - an **independent specification audit** by a fresh auditor (DEC-088), with contested or owner-level findings brought to the owner as decision packages;
   - WBS tickets with KPIs, including a linked gap ticket for every required open row (DEC-089);
   - independent acceptance tests → implementation → `gov close` → CI → owner merge.
2. **RETR-A-04 and RETR-X-02 are run.** Each produces multi-batch evidence bundles with:
   - citations by id and hash;
   - named parent expansions (DEC-091);
   - synthesis notes wherever the evidence exceeds the packet ceiling (W1-23);
   - a stopping reason from the fixed list.
   The validator passes, and retrieval stays outside the main context (DEC-080).
3. **MR-3 containment holds.** No implementer write reaches `tests/acceptance/**`, and no orchestrator write either (DEC-156). The guard refuses the attempts, and the post-command check catches any Bash form the guard misses, also after a failed command. The exit run's worker sessions are started by `gov launch` inside the OS sandbox, which stops a Bash write outside the repository (DEC-152, DEC-161). Any breach is a forbidden outcome.
4. **Governance share is ≤ 15 %** on each programme's run, measured as in DEC-086. Cache reads are reported separately. The exit report also gives the other two learning metrics per ticket (KPI disputes; acceptance tests rewritten after implementation began, with reasons), which have no threshold (DEC-106).
5. **An independent wave-exit audit against Contract v4** (DEC-070, DEC-088). A fresh, read-only Independent Auditor gives a finding row to every W1 contract item, every W1 `covers` item (DEC-092) and every MR clause. Contested and owner-level findings come to the owner as decision packages, and agreed fixes become tickets. The audit→repair loop follows DEC-096.

Also required:
- `gov doctor` is green on this repository;
- the dev tiers' canaries hit, and no dev canary secret appears in any derived store;
- `gov check` reports 17 of 17 governance test families with an executable check, and all twelve Wave 1 `gov` commands are implemented.

The plan itself is checked by `docs/plan/tools/validate_s1.py` (run it from the repository root).

## 5. Source merge (DEC-076)

Every source item is carried by a W1 ticket:

| Source | Carried by |
|---|---|
| S0b2 GLUE, W1 items | G-01 → W1-02 · G-03 → W1-09 · G-04 → W1-11 · G-05 → W1-14 · G-06 → W1-16 · G-07, G-09 → W1-12 · G-08 → W1-13 · G-10 → W1-41 · G-11, G-15 → W1-38 · G-12, G-18 → W1-15 · G-14 → W1-39 · G-17 → W1-17 + W1-19 · G-19 → W1-21 · G-20, G-21 → W1-17 · G-22 → W1-18 · G-25 → W1-37 |
| S0b2 GLUE, moved to W1 | G-02 → W1-03 (DEC-076) |
| S0b2 GLUE, W2 (stay W2) | G-13 framing-tolerant MCP client · G-16 id mapping · G-23 incremental re-index hook · G-24 deletable-class join |
| DEC-080 (retrieval completeness) | paging/continuation, facets, dedup, authority filter, one rerank, evidence bundle → W1-21 · `gov closure` → W1-20 · validator, canaries → W1-22 · hierarchical synthesis → W1-23 · parallel facet subagents → W1-36 |
| Architecture components | `gov` skeleton + API-0002 → W1-07 · status → W1-32 · check → W1-26 · readiness → W1-13 · doctor, rebuild → W1-27 · context → W1-24 · closure → W1-20 · checkpoint → W1-25 · close → W1-30 · adopt --lite → W1-41 · pause → W1-28 · hooks: PreToolUse → W1-02, SessionStart/PreCompact/Stop/SubagentStop → W1-29 · lefthook + CI → W1-40 · Copier + lock + manifest → W1-39 · roles → W1-33 · 8 skills → W1-35, W1-36 · decision package → W1-34 · codebase-memory wrapper → W1-16 · Superpowers → W1-37 · ticket vendoring + claims → W1-09 · Ollama on demand → W1-18 |
| Register decisions | DEC-074 Q9 deny rules → W1-01 · DEC-083 install rule → W1-04 (interim rule W1-01), registry → W1-06 · DEC-084 bootstrap → W1-01, W1-05 · DEC-086 ccusage → W1-06, counter → W1-31 · DEC-087 CI evidence record → W1-40 · DEC-070 exit audit → W1-43 · DEC-088 audit triggers → W1-13, W1-35, W1-36, W1-43 · DEC-089 gap tickets → W1-13, W1-26, W1-35 · DEC-090 A0–A6, A8 → W1-41 · DEC-091 parent-child → W1-17, W1-21 · DEC-093 package cap → W1-34, W1-35 · DEC-046 lessons → W1-44 · DEC-102 experiments, DEC-103 order of specification work, DEC-105 three-option CIT-P, DEC-136 probe findings → W1-35 · DEC-104 UX and visual testing → Wave 2 · DEC-106 learning metrics → W1-31, W1-42 · DEC-137 post-green probe → W1-30 · DEC-119, DEC-154 role definitions → W1-05, then W1-33 · DEC-150, DEC-156 orchestrator write scope → W1-45 · DEC-152, DEC-153, DEC-158, DEC-159, DEC-161 launcher and sandbox → W1-46 · DEC-153 escape hatch and failed commands, DEC-162 oracle hiding → W1-47 · DEC-153 Claude Code pin → W1-48 · DEC-160 untested sandbox cases → Wave 2 · DEC-163 minimal research role → W1-46 · DEC-164 no `excludedCommands` → W1-46; subagents in a sandboxed worker and `excludedCommands` → EXP-002, Wave 2 · DEC-165 lite upstream lesson loop → Wave 3 · DEC-166 `gov discover` → Wave 2 · DEC-167 plain-language impact question → W1-35, then `gov impact` in Wave 2 · DEC-168 lesson scope and severity in the schema → W1-08 (records: W1-44) · DEC-141 sandbox prerequisites in the registry → W1-48 · DEC-169 validator → `docs/plan/tools/validate_s1.py` · DEC-170 sandbox token line → W1-31 · DEC-171 orchestrator change as a record → W1-45 · DEC-172 settings ask rules removed → W1-47 (install test with the committed settings: W1-46) · DEC-173 Charter §6 install sentence → no ticket · DEC-174 four `uv` forms in the install rule → W1-47 |
| EXP-001 (`spike-sandbox/EVIDENCE.md` §5.5) | 1 launcher → W1-46 · 2 guard → W1-47 · 3 network allowlist and installs → DEC-157, DEC-158 (W1-46) · 4 `$TMPDIR` → DEC-159 (W1-46) · 5 untested cases → Wave 2 (DEC-160) · 6 pin → W1-48 |
| S0a STACK_OPTIONS §3 | S0a-G-01 → W1-07, W1-32 · S0a-G-02 → W1-26 · S0a-G-03 → W1-10, W1-20 · S0a-G-04 → W1-27 · S0a-G-05 → W1-17, W1-19 · S0a-G-06 → W1-21 · S0a-G-07 → W1-24 · S0a-G-08 → Wave 2 (`gov impact`) · S0a-G-09 → W1-25, W1-29 · S0a-G-10 → W1-02, W1-28 · S0a-G-11 → W1-40 · S0a-G-12 → W1-30 · S0a-G-13 → W1-41 · S0a-G-14 → Wave 3 (`gov research sync`) · S0a-G-15 → W1-39 |

## 6. Wave 2 — Strengthen (outline only; no tickets)

- **Readiness generates work:** `gov readiness --generate` (CAP-30, MR-2).
- **Change impact:** `gov impact` over the record and code graphs → radius → computed profile (CAP-33, CAP-53; S0a-G-08). "What's the impact of X?" in plain language runs it (DEC-167).
- **Discovery entry point** (DEC-166): `gov discover <question or feature>` opens a discovery ticket, runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose evidence records, with measured numbers, back the answer. Plain language works the same way (CAP-32).
- **Budgets:** budget gates in `gov close` and hooks (CAP-04).
- **Retrieval components:** fail-closed model pins and swap-by-configuration (CAP-19), plus a lighter reranker spike (DEC-074 Q3).
- **S0b2 W2 glue:** G-13, G-16, G-23, G-24.
- **Organisation:** specialist roles, including the distinct test execution and integration roles (DEC-094), and typed handoff records (CAP-22); model-switch continuity (CAP-37).
- **Distribution:** the first real `copier update` and `gov update --check` (CAP-45).
- **Sandbox experiment EXP-002** (DEC-160, DEC-164): `denyWrite` on a path that doesn't exist yet, symlink and hard-link tricks, the seccomp filter, `bypassPermissions` mode, subagents inside a sandboxed worker session, and `excludedCommands` (CAP-61). Until it runs, these are residuals in `governance/project/bootstrap.md`.
- **UX before build** (DEC-104): the UX role; the UX readiness row closes only on owner-approved, scenario-derived wireframes or mockups; acceptance tests include visual checks (CAP-30). Visual-testing tools are installed under DEC-083 when first needed.
- **Scale:** the probes on `~/EXAMIN APP` and `~/workspace` are already done (DEC-078); larger graphs are measured before adoption.
- **Exit:** the dev-tier regression suite is green. A mid-programme specification change on Programme A's dev tier propagates through CIT-P → CIT-E with the correct impact set. Independent audit.

## 7. Wave 3 — Complete (outline only; no tickets)

- **Research lifecycle:** Docling and MarkItDown, `gov research sync`, research records; RAGFlow only on its trigger (CAP-32). The minimal research role of Wave 1 (DEC-163) grows into the full role here.
- **Upstream lesson loop, lite** (DEC-165; reverses DEC-053 Q7 for framework lessons only):
  - every lesson record carries a scope (project, product or framework) and a severity (low, medium, high or critical). Both fields are already in the Wave 1 lesson schema (W1-08, DEC-168), so no migration is needed;
  - a framework lesson becomes a lesson packet (failure pattern, evidence, suggested change; no product code, data or secrets; gitleaks-scanned), written by the product's orchestrator to the shared inbox `~/gov-os-lessons-inbox/`, the one path outside its repository it may write (a guard exception, CAP-58);
  - a high or critical lesson is raised to the owner immediately, as a decision package;
  - the Gov OS orchestrator triages the inbox (deduplicate, rank) into change proposals under the normal cycle, and each release's notes list the lessons fixed, with their severity;
  - `gov doctor` compares the installed release with the latest and reports pending updates and their highest severity at session start; the owner decides when to run `gov update` (CAP-45);
  - product decisions, specifications and lessons never leave their repository (CAP-41).
- **Model routing and empirical routing:** OTel (CAP-35, CAP-36). The DEC-018 local T1 model is decided here.
- **Concurrency:** claims and concurrency for parallel agents, and the claims role (CAP-23).
- **Traceability:** full specification lineage and Gate W (CAP-29, CAP-50).
- **Health:** the health scheduler and SLOs (CAP-39, CAP-48).
- **Roles and adoption:** full independent adoption and audit roles (CAP-47) with the A7, A10 and A11 gates and the final adoption verdict (CAP-44, DEC-090), and the remaining Wave 3 roles.
- **Isolation and benchmarks:** multi-project isolation checks, and per-repository retrieval benchmarks.
- **Exit:** every CAP in Contract v4 has at least one passing mechanism test and a mapped qualification scenario. Independent audit. Then qualification (CAP-49) and Release 1.
