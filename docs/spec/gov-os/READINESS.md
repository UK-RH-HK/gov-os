# Gov OS — readiness of its own specification

**Subject:** the Governance OS itself, as one spine specification (MR-1 applied to the Gov OS, DEC-081).
**Profile:** FULL. Every one of the 26 dimensions is required; each cell must be PRESENT or N/A_WITH_REASON.
**Dimensions:** Framework v4.1.2 §37, in its order and wording.
**Cell states:** PRESENT · MISSING · PROVISIONAL · BLOCKED · N/A_WITH_REASON. A silent N/A is invalid.
**Authority:** `docs/DECISION_REGISTER.md` (register v0.12 plus the S1 entries). Only ACCEPTED and DONE entries count
as evidence of a settled cell (DEC-082); a cell that rests on a PROPOSED entry is PROVISIONAL.
**Round:** 1 (2026-09-30). Status: **OPEN** — 7 PROVISIONAL cells, 5 decision packages with the owner.

## 1. Readiness table

| # | Dimension (§37) | State | Evidence | Open item |
|---|---|---|---|---|
| 1 | intent/outcome | PRESENT | DEC-039 (purpose: keep agents accurate, bounded, traceable); DEC-057 (memory and context live in the repository; agnostic); DEC-064 (full scope, three waves, one release); architecture v0.3 §1 | — |
| 2 | user/actor | PRESENT | DEC-065 MR-5, MR-6 (owner = customer and L5 authority; role agents are replaceable workers); DEC-066 (Wave 1–3 rosters); DEC-073 (operator console acts for the owner at the terminal) | — |
| 3 | journey/workflow | PRESENT | DEC-065 MR-1…MR-4; DEC-069 (tests before READY; `gov close` runs them); architecture v0.3 §2.3 (ten-step spec-first cycle), §2.5 | — |
| 4 | scenarios | PRESENT | DEC-067 (Programmes A and B, dev/qual/stress tiers, chaos/recovery/soak/isolation); DEC-071 (105 dev and 198 qual scenarios, 57/57 in-scope capabilities covered); `synthetic/COVERAGE_MATRIX.md` | — |
| 5 | inputs | PRESENT | Architecture v0.3 §2.2 (product repository layout), §2.3 steps 1–2; DEC-060 (overlay configuration is the only per-project input); DEC-074 Q6 (harness inputs: CLAUDE.md + AGENTS.md) | — |
| 6 | data model/schema | PROVISIONAL | Settled: DEC-074 D2 (MADR frontmatter + check-jsonschema), T3 ticket fields `kpis/role/allowed_paths/profile` (S0b2 RESULTS §3), DEC-080 (evidence bundle: citations by id and hash, stopping reason), `docs/interfaces/API-0002.yaml`. Open: the record frontmatter conventions rest on DEC-012 (PROPOSED); the profile → required-cells rule of the readiness schema is undefined in accepted sources, and DEC-005's "N/A_WITH_REASON auto-default" (PROPOSED) conflicts with MR-1's "silent N/A is invalid" | P1-A, P1-C |
| 7 | representative test data | PRESENT | DEC-067, DEC-071 (deterministic dev tiers, 151 files each, manifests); DEC-074 Q14 (TypeScript fixes to both tiers by the S0b1 author); repository `fixtures/` | — |
| 8 | processing/algorithm | PROVISIONAL | Settled: DEC-080 (paging with continuation, facet subagents, deterministic closure, dedup by chunk hash, authority filter, one rerank, validator, canaries, hierarchical synthesis); DEC-074 R1 (FTS5 + sqlite-vec + RRF + Qwen3 rerank); DEC-030. Open: two separate budgets (DEC-031), radius-scaled budgets (DEC-035), impact radius → profile mapping (DEC-005) are PROPOSED | P1-A |
| 9 | expected outputs | PRESENT | DEC-080 (cited evidence bundle, fixed stopping reasons); DEC-065 MR-2 (WBS), MR-6 (decision packages, answers in git); architecture v0.3 §2.3 (context packet as file path + ≤ 2.5k-token summary; checkpoints; trailers); `docs/interfaces/API-0002.yaml` (JSON envelope, exit codes 0–4, kept in tree by DEC-054) | — |
| 10 | functional requirements | PRESENT | DEC-064 (every Contract v3 capability that survives ADR-0001); `s0a/out/capabilities.yaml` (CAP-01…CAP-60); DEC-074 Q11 (the four LITE forms); DEC-067 (CAP-49 KEPT as qualification); DEC-053 Q7 (no upstream export) | — |
| 11 | non-functional requirements | PROVISIONAL | Settled: DEC-078 (scale envelope ≈ 80k nodes / 270k edges; worst-case RAM ≈ 12.5 GB of 15.5 GiB); DEC-074 facts (≈ 11.9 GB disk, one on-demand daemon, VRAM ≈ 5.2 GiB peak). Open: the governance token budget (DEC-004, ≤ 10–15 %, packet ≤ ~6k tokens) and the loop budget (DEC-044, two rounds) are PROPOSED | P1-A |
| 12 | UX/interactions where applicable | PRESENT | DEC-065 MR-6 (decision packages in the active chat, ranked and batched); Framework §33–34 (natural language first, small command set); architecture v0.3 §2.4; DEC-058 (stage state in a committed file; any panel only reads and writes it — no panel is required) | — |
| 13 | backend/service behaviour | PRESENT | Architecture v0.3 §2.1 L3–L4 (hooks; `gov` commands); DEC-076 (post-command containment in W1); DEC-080; DEC-074 Q4 (Ollama on demand, 5-min idle unload); `s0b2/out/GLUE_REQUIREMENTS.md` | — |
| 14 | database/state requirements | PRESENT | Architecture v0.3 §1 principle 1 and §2.1 L5–L6 (git is the only truth; `.gov-runtime/` derived and rebuildable); DEC-057; DEC-074 R1 + GLUE G-20 (one SQLite store for frontmatter graph, FTS5 and vectors); DEC-074 Q10 (codebase-memory home per repository) | — |
| 15 | interface/API/event contracts | PRESENT | `docs/interfaces/API-0002.yaml` (DEC-054, in-tree active); DEC-074 Q6–Q7 (rulesync adapters for Claude Code + AGENTS.md; rulesync owns `.claude/`); hook events SessionStart, PreToolUse, PreCompact, Stop, SubagentStop (architecture v0.3 §2.1 L3, DEC-069, DEC-076). DEC-025/DEC-046 wording is PROPOSED and is ratified with P1-A, but the accepted sources already fix the contracts | (P1-A) |
| 16 | security/privacy | PRESENT | DEC-039 as amended by DEC-075 (ADR-0001); DEC-074 Q8 (content secret filter before every indexer, W1 gate), Q9 (deny rules), Q10; DEC-076 (codebase-memory secret-exclusion proof); DEC-077 (deploy key); DEC-067 (oracle out of reach by placement) | — |
| 17 | integrations | PRESENT | DEC-074 (OpenSpec, codebase-memory-mcp, ticket, MADR + check-jsonschema, rulesync, Copier, lefthook, gitleaks, Ollama, Superpowers ×3); DEC-079 (private GitHub remote); DEC-075 (GitHub Actions, advisory) | — |
| 18 | DevOps/runtime | PROVISIONAL | Settled: host (architecture v0.3 header: WSL2, 20 vCPU, 15 GiB, RTX 5070 Ti 16 GB); DEC-074 Q4, Q7, Q13; DEC-075 (pre-push G3 + advisory CI G4–G5 + owner-only merge). Open: what the hosted CI runner executes, given no GPU, no local models and a private-repository minutes allowance; DEC-040 (owner installs and pins every tool) is PROPOSED | P2-E, P1-A |
| 19 | observability | PROVISIONAL | Settled: the metric exists (DEC-065 MR-3/MR-4 records; SCORECARD_FORMAT M-series). Open: DEC-026 (telemetry stack) is PROPOSED; no accepted source defines which tokens count as "governance" nor which instrument measures the share in Wave 1 (ccusage appears only in architecture v0.3 §4 and is not in `TOOL_REGISTRY.yaml`) | P2-D, P1-A |
| 20 | performance/capacity | PRESENT | DEC-078 (envelope, peak RSS, index sizes); S0b2 RESULTS §1 (warm query p50 0.24 s / p95 0.33 s; cold index 4.5 s; incremental 2.8 s), §5 (≈ 10.3 GB stack + IDE) | — |
| 21 | cost constraints | PRESENT | DEC-074 Q1 (Balanced stack: ≈ $100–104 a month, no Docker; no second-family verifier subscription, which settles OQ-03); DEC-074 Q13 and DEC-075 (no GitHub Pro); register §7 | — |
| 22 | recovery/fallback | PRESENT | GLUE G-22 (Ollama health check, FTS-only fallback); DEC-080 + DEC-034 list (`FACET_UNAVAILABLE`; NOT_FOUND ≠ absent); DEC-051/DEC-056 (archive tag); architecture v0.3 §4 (checkpoints; `gov rebuild`); Framework §74 (freeze flag, revert) | — |
| 23 | measurable success criteria | PROVISIONAL | Settled: Wave 1 exit (architecture v0.3 §6.1; DEC-080 RETR-A-04, RETR-X-02; DEC-070 wave-exit audit); Wave 2/3 exits (§6.1); qualification scorecard (SCORECARD_FORMAT M1–M18; thresholds held out, DEC-067). Open: "governance share ≤ 15 %" has no accepted definition or instrument | P2-D |
| 24 | measurable failure criteria | PRESENT | SCORECARD_FORMAT M15 (any forbidden outcome fails qualification), M14 (any MR-3 breach is forbidden); DEC-069; DEC-070 (at most two audit→repair rounds). The general loop budget (DEC-044) rides P1-A | (P1-A) |
| 25 | independent acceptance/system tests | PROVISIONAL | Settled: MR-3, DEC-069 (Independent Test Designer; implementer's allowed paths exclude `tests/acceptance/`), DEC-076 (G-02 containment in W1), DEC-067 (qualification by a fresh executor), DEC-070. Open: how MR-3 is held on the Gov OS's **own** Wave 1 tickets before the guard (G-01) and containment (G-02) exist, and which session plays the Independent Test Designer for them | P1-B |
| 26 | documentation/operations needs | PRESENT | DEC-058 (Charter v5, Contract v4; `docs/source/` archived after S1-A); DEC-081, DEC-082; DEC-073 (operating model until Release 1); DEC-053 Q7 (lessons in `docs/lessons/`) | — |

**Summary:** PRESENT 19 · PROVISIONAL 7 (#6, 8, 11, 18, 19, 23, 25) · MISSING 0 · BLOCKED 0 · N/A_WITH_REASON 0.

## 2. Decision packages (round 1)

Asked in the S1 chat on 2026-09-30, ranked by critical-path effect and irreversibility. Answers are recorded as new
entries in `docs/DECISION_REGISTER.md`, and this table is then updated.

| Id | Rank | Question (short) | Cells |
|---|---|---|---|
| P1-A | P1 | Ratify the PROPOSED decisions that Charter v5 and Contract v4 rest on, with the listed amendments and supersessions | 6, 8, 11, 15, 18, 19, 24 |
| P1-B | P1 | How MR-3 holds on the Gov OS's own Wave 1 before the guard and containment exist | 25 |
| P1-C | P1 | Which readiness cells each profile requires, and whether any N/A may be defaulted | 6 |
| P2-D | P2 | What counts as governance tokens, and what measures the share in Wave 1 | 19, 23 |
| P2-E | P2 | What the hosted CI runner executes | 18 |

Questions not asked, because the sources answer them: stack (DEC-074 Q1); task tracker (DEC-074 T3); branch
protection (DEC-075); second model family / OQ-03 (Balanced stack, DEC-074 Q1); adapters (DEC-074 Q6); retrieval wave
(DEC-080); codebase-memory home (DEC-074 Q10); Superpowers subset (DEC-074 Q5); which product adopts first (DEC-060,
deferred to adoption); control panel (DEC-058); AMD-01…AMD-08 / OQ-06 (Contract v4 replaces amendments to v3, DEC-058).

## 3. Conflicts with the register (the register wins)

| # | Source says | Register says | Resolution in S1 |
|---|---|---|---|
| X-01 | Architecture v0.3 §2.1 L5, §2.2, §2.3 step 3, §4: Backlog.md in `backlog/` | DEC-074 T3: wedow/ticket v0.3.2, vendored, in `.tickets/`; supersedes Backlog.md | ticket |
| X-02 | Architecture v0.3 §2.1 L3, §2.3 step 8, §4: GitHub Actions on a protected `main`; GitHub Pro | DEC-075 (amends DEC-007, DEC-039): no protection; pre-push G3 + advisory CI + owner-only merge on green | DEC-075 |
| X-03 | Architecture v0.3 §2.1 L4, §2.5, §4, §6.1: validator, canaries, `retrieve --validate` in Wave 2 | DEC-080: the whole retrieval-completeness capability in Wave 1 | Wave 1 |
| X-04 | Architecture v0.3 §2.1 L6, §4, §5, §6.1: semantic retrieval, rerank, fusion in Wave 2, "or qmd" | DEC-074 R1 and Q3 (reranker accepted for W1); DEC-080 (one rerank over the merged set in W1) | Wave 1, R1 |
| X-05 | Architecture v0.3 §4: adrkit if it passes, else check-jsonschema | DEC-074 D2 | D2 |
| X-06 | Architecture v0.3 §4: Claude Code LSP as part of code intelligence | DEC-074 C1 (LSP stays a harness feature, not a stack component) | C1 |
| X-07 | Register §6 Solo Core (V dropped; several gates DEFERRED); DEC-002 | DEC-064, DEC-067 (full scope; Gate V kept as qualification) | DEC-064 |
| X-08 | DEC-013 (`br`), register §8 (`.beads/`, `br init`) | DEC-074 (supersedes DEC-013); DEC-072 (beads_rust excluded) | ticket |
| X-09 | S0b2 GLUE G-02 in Wave 2 | DEC-076: G-02 in Wave 1 | Wave 1 |
| X-10 | S0a catalogue CORE/LATER labels; CAP-49 DROP | DEC-064 (waves, not CORE/LATER); DEC-067 (CAP-49 KEPT) | Contract v4 relabels by wave |
| X-11 | DEC-043 (products resume immediately); S0a STACK_OPTIONS §5 sequencing | DEC-064 (adoption only after Release 1) | DEC-064 |
| X-12 | DEC-024 and GLUE G-25: four Superpowers skills, incl. subagent-driven-development | DEC-074 Q5, DEC-076: three skills; subagent-driven-development excluded | three skills |
| X-13 | DEC-001: ~3k-line glue revisit trigger | DEC-064: per-wave review | per-wave review |
| X-14 | DEC-042: independent verification only in FULL | DEC-065 MR-3, DEC-069: every task's acceptance tests come from an independent test designer | MR-3 for all tasks; DEC-042's fresh verifier review stays FULL-only (P1-A) |
| X-15 | DEC-005: N/A_WITH_REASON auto-default for conditional dimensions | DEC-065 MR-1: silent N/A is invalid | P1-C |

## 4. Round log

| Round | Date | Asked | Answered | PROVISIONAL after |
|---|---|---|---|---|
| 1 | 2026-09-30 | P1-A, P1-B, P1-C, P2-D, P2-E | — | 7 |
