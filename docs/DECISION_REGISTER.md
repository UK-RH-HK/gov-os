# Governance OS — Tool & Architecture Decision Register

**Register ID:** GOV-DR
**Version:** 0.12 (draft for product-owner approval)
**Date:** 2026-09-28
**Applies to:** the current Rust Governance OS repository *and/or* a new assembled `gov-os` repository
**Normative sources this register interprets (not replaces):**
- Dynamic Agentic Software Engineering Operating Framework v4.1.2
- Governance OS Release, Distribution, Adoption & Upstream Learning Protocol v1.2
- Governance OS Adoption, Migration & Independent Audit Protocol v3.0
- Governance OS Capability Acceptance Contract v3

---

## 0. How to read this register

Each decision carries:

| Field | Meaning |
|---|---|
| **ID** | `DEC-###` (decisions), `AMD-##` (proposed contract amendments), `OQ-##` (open questions) |
| **Status** | `ACCEPTED` · `PROPOSED` · `CONDITIONAL` (adopt only when trigger fires) · `DEFERRED` · `REJECTED` · `SUPERSEDED` |
| **Basis** | `ESTABLISHED` = prior art / external evidence cited · `SUGGESTION` = design proposal not yet validated in our repos · `OWNER` = product-owner guidance |
| **Gates** | Contract v3 gates/items the decision helps satisfy |
| **Revisit trigger** | The observable condition that re-opens the decision |

Status values here are *proposals from the design session*. The product owner flips them to approved state; agents must not.

Evidence was gathered on 2026-09-28 (v0.1 carried an incorrect date of 2026-09-26). Tool facts (versions, bugs, features) go stale quickly — re-verify at install time and record exact pinned versions in the Tool Capability Registry (Gate F2).

---

## 1. Context

Two product repositories stalled while a full Governance OS was being built from first principles in Rust. Repository context growth was the original trigger. Research on 2026-09-26 showed that most Contract v3 capabilities can be satisfied by assembling mature open-source tools plus a thin glue layer, with the Rust implementation deferred as a later replacement for that glue.

Core risk identified: a naive Governance OS becomes token-heavy (governance consuming more tokens than the work it governs). Several decisions below exist specifically to prevent that.

---

## 2. Strategic decisions

### DEC-001 — Assemble first; Rust kernel becomes the later replacement
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** Build the Governance OS by assembling existing tools behind a stable `gov` CLI interface (Python first). The Rust implementation continues later as a drop-in replacement of the `gov` CLI internals, not as a prerequisite for product work.
- **Rationale:** Contract v3's own proposed order places ~9 milestones (including synthetic qualification repos and a retrieval bake-off) before Product A/B adoption. Tools now exist for most layers (see §3).
- **Consequence:** The `gov` command surface and file formats (frontmatter schema, lockfile, context packet schema, checkpoint schema) are the **surviving layer**; implementations may change.
- **Revisit trigger:** Assembled version fails a Solo Core gate that no tool can cover, or glue exceeds ~3k lines.

### DEC-002 — Contract v3 retained as normative property spec; add a "Solo Core" profile
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** Keep Contract v3 unchanged as the full specification. Add a profile layer (§6) marking each capability `CORE` / `DEFERRED` / `DROPPED_FOR_SOLO` with the implementing tool.
- **Rationale:** The contract's properties are sound; its implied implementation scope is enterprise/multi-tenant.

### DEC-003 — Governance is code, not prose
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** No agent reads the framework, protocols or contract during normal work. They compile into deterministic checks (hooks, `gov check`, CI). Agents see only: a short AGENTS.md (target ≤ ~1.5k tokens), a compiled context packet, and terse `gov` output.
- **Rationale:** Framework (~62KB) + contract (~42KB) ≈ 25k tokens per session if read; multiplied across fresh independent sessions this dominates spend.
- **Gates:** A1, G1, M1 (T0 routing), U (tokens/completed task)

### DEC-004 — Governance overhead budget (hard SLO)
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** Governance share of tokens per completed task target ≤ 10–15%; final context packet target ≤ ~6k tokens (tunable). Breach is a health finding (Gate U), not a silent cost.
- **Measurement:** telemetry (DEC-026) tagged by task ID.

### DEC-005 — Proportionality profiles keyed to impact radius
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** Three ceremony profiles: `LITE` (R0–R1), `STANDARD` (R2), `FULL` (R3+). Profile controls: readiness dimensions required, independent test author/verifier, retrieval budget, human gate.
- **Readiness (H2) reduction:** 8 mandatory dimensions always (intent, actor, scenarios, inputs/outputs, data, success+failure criteria, acceptance tests, security); remaining 18 conditional by capability type and profile, with `N/A_WITH_REASON` auto-default.

### DEC-006 — Progressive adoption
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** A repo is governable from day one (hooks + `gov check` + task tracker) while A1–A11 path migration proceeds in background batches. Full A0–A11 remains the target for `ADOPTED_HEALTHY`.

### DEC-007 — Native harness features first; CI is the enforcement boundary
- **Status:** PROPOSED · **Basis:** ESTABLISHED + SUGGESTION
- **Decision:** Use harness-native hooks, subagents, skills and LSP where they exist. Treat hooks as guardrails, never as the security/enforcement boundary. Every hook check is re-run in git hooks (lefthook) and CI, which are authoritative for merge.
- **Evidence:**
  - Claude Code hook docs note a stalled hook does not act as a gate — the call continues through the normal permission flow. [E-HOOK-CC]
  - OpenAI's Codex hook docs state tool hooks are a guardrail, not a complete enforcement boundary; some tool paths bypass the default hook path. [E-HOOK-CX]
- **Gates:** N3 (provider-independent watchdog), O5 (G0–G5 tiers)

---

## 3. Tool decisions

### DEC-010 — Agent harness
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Claude Code as primary T2/T3 harness (Claude Max 5x to start). Optional second model family (Codex) as independent verifier for R3+ changes.
- **Evidence:** Pro $20/mo; Max $100 (5x) or $200 (20x). Programmatic/headless usage (Agent SDK, `claude -p`, GitHub Actions) draws from a separate monthly credit pool rather than interactive limits. [E-PRICE]
- **Consequence:** Health-scheduler verifiers should run as interactive subagents, or headless spend must be budgeted separately (Gate A4).
- **Revisit trigger:** telemetry shows sustained limit hits → Max 20x.

### DEC-011 — Specification & change control: OpenSpec
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** OpenSpec owns spec truth (`openspec/specs/`) and change proposals (`openspec/changes/`). Proposal ≈ CIT-P; archive ≈ CIT-E. Accept OpenSpec's directory convention; the project path map describes it (do not force into `spec/`).
- **Pin:** ≥ v1.12.0 (findings-only validation reports; code-grounded planning). [E-OSPEC-REL]
- **Extension point:** custom schemas in `openspec/schemas/` (version-controlled) — use to add readiness and impact artefacts to the change workflow. [E-OSPEC-CUST]
- **CI:** `openspec validate --strict` runs at G2/G5.
- **Gates:** H1, K1, K2, W1 (partial)
- **Alternatives considered:** GitHub Spec Kit (heavier, greenfield-oriented); BMAD (REJECTED, DEC-021).

### DEC-012 — Decisions: ADR markdown with frontmatter in git
- **Status:** PROPOSED · **Basis:** ESTABLISHED (ADR practice) + SUGGESTION (schema)
- **Decision:** Decisions are ADR files in git with YAML frontmatter: `id`, `type`, `status` (ACTIVE/PROVISIONAL/SUPERSEDED/…), `supersedes`, `superseded_by`, `depends_on`, `implements`, `constrains`, `content_hash` (computed). The decision/spec graph is **derived deterministically** from frontmatter into SQLite — no LLM extraction.
- **Explicitly not used:** codebase-memory-mcp's `manage_adr` feature — an open issue (July 2026) reports ADR content silently destroyed on incremental reindex. [E-CBM-ADR]
- **Gates:** B3, C1, C2, C6, W1–W3, W10

### DEC-013 — Task DAG & claims: beads_rust (`br`) — *changed from earlier recommendation of `bd`*
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Use `br` (beads_rust), which freezes the "classic" SQLite + JSONL architecture: JSONL tracked in git, SQLite local; no daemon, no auto-git, no auto-commit/push. [E-BR]
- **Why changed:** Upstream `bd` moved to Dolt; some community tooling reports regressions after `bd` switched to server mode and recommends `br` or pinning `bd` 0.49.x. [E-BR-GUI] The classic model matches our rule that git is authoritative and SQLite is derived (Gate B3), and that the Governance OS — not the tracker — controls commits.
- **Known limitation:** agents do not spontaneously use the tracker; instructions fade over long sessions. [E-BEADS-USE] → SessionStart hook must inject `br ready`; task-close enforced by `gov close`.
- **Risk:** single maintainer, no outside contributions accepted. Mitigation: JSONL format is plain and `bd`-classic compatible; replaceable behind `gov`.
- **Gates:** I1, I4, E4, N (partial)
- **Alternatives:** `bd` v1.3.x (Dolt), wedow/ticket, Beans, Backlog.md.

### DEC-014 — Code-structural memory: codebase-memory-mcp
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Use codebase-memory-mcp for call graphs, impact analysis, routes, dead code.
- **Evidence:** 31-repo evaluation: 83% answer quality vs 92% for a file-exploration agent at ~10× fewer tokens and 2.1× fewer tool calls. [E-CBM-PAPER]
- **Pin & hygiene:**
  - Use a release after the July–August 2026 fixes: watcher no longer re-indexes dirty repos every poll (previously caused >1 TB/day disk writes), and store/artifact integrity fixes with atomic reindex publication. [E-CBM-WATCH][E-CBM-REL]
  - Upgrades can force one full cold reindex (format stamp). [E-CBM-REL]
  - Incremental reindex has open performance issues on very large monorepos (not expected to affect our repo sizes). [E-CBM-INC]
  - Do **not** commit its `.codebase-memory/graph.db.zst` artifact by default — derived state stays gitignored (B3); revisit if clean-clone rebuild time becomes painful.
- **Gates:** C5, D2 (code route), K1 (code-side impact), W7 (dead code)

### DEC-015 — Symbol navigation & refactoring: native LSP first, Serena optional
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Use Claude Code's built-in LSP tools (definition, references, document symbols — available since v2.0.74). Add Serena only for multi-file refactors (rename/move) where it collapses many steps into one atomic call. [E-SERENA-LSP][E-SERENA]
- **Install note:** Serena's maintainers advise installing via their Quick Start, not MCP/plugin marketplaces. [E-SERENA]

### DEC-016 — Lexical + semantic index: SQLite FTS5 + sqlite-vec, fused with RRF
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** One derived `.gov-runtime/index.sqlite` with FTS5 (lexical) + sqlite-vec (vectors), Reciprocal Rank Fusion. Content-hash gating for incremental embedding. Brute-force vector search is adequate to ~100K vectors — far above expected spec/decision/research corpus size. [E-VEC]
- **Upgrade path:** LanceDB if vectors exceed ~100K or latency degrades.
- **Gates:** C3, C4, D1, D2, D3, D6

### DEC-017 — Embedding & reranking models
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B via Ollama, resident on GPU (~3 GB VRAM total). Pin revisions in the index manifest (D5).
- **Licence rule:** only permissively licensed models (Apache-2.0/MIT). Some top-ranked embedders (e.g. jina-embeddings-v3) are non-commercial and are excluded for commercial projects. [E-EMBED]
- **Gates:** D4, D5

### DEC-018 — Local T1 model
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** gpt-oss:20b loaded on demand (≈13 GB, fits a 16 GB card fully resident at 8k context) for T1 tasks: file classification during adopt, lesson scoping, summaries. Not used for implementation. [E-LOCAL]
- **Constraint:** cannot co-reside comfortably with embed+rerank at larger contexts; rely on Ollama keep-alive unload.

### DEC-019 — Research corpus ingestion: Docling → markdown in git
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Convert research PDFs (papers, patents, datasheets, standards) once with Docling; commit the markdown with frontmatter (`source_path`, `source_sha256`, `converter`, `converter_version`) next to the original; index with DEC-016. Use MarkItDown as fast path for DOCX/PPTX and clean digital PDFs.
- **Evidence:** Docling is MIT, LF AI & Data hosted, runs fully locally, and ships CLI, HTTP service and an MCP server. [E-DOCLING] Comparative testing reports Docling materially better on tables, formulas and multi-column PDFs; MarkItDown 50–100× faster on simple digital PDFs but loses structure. [E-PDFCMP]
- **Pin:** Docling releases very frequently — pin the exact version (record in manifest so conversions are reproducible). [E-DOCLING-PIN]
- **Gates:** J1, B3 (truth stays in git), D1

### DEC-020 — RAGFlow: conditional, research facet only
- **Status:** CONDITIONAL · **Basis:** ESTABLISHED (evidence) + SUGGESTION (integration pattern)
- **Verdict by use:**

  | Use in Gov OS | Fit | Reason |
  |---|---|---|
  | Authority layer (specs, decisions, tasks) | **No** | Similarity-ranked retrieval conflicts with W10; stores its own copies of files (second truth store). |
  | Code intelligence | **No** | Git connectors sync files/issues/PRs, not code structure; connector reliability issues (below). |
  | Research/evidence corpus (Gate J) — complex PDFs, scans, tables | **Yes, when volume/messiness justifies it** | Deep document parsing, multiple parsers (DeepDoc, MinerU, Docling, layout-aware OCR), RAPTOR hierarchical indexing, citations with positions, metadata filtering, MCP. |

- **Evidence (capabilities):**
  - Latest docs reference v0.27.2; frequent releases through 2026 with new connectors, an ingest-documents API endpoint and a layout-aware OCR parser. [E-RF-REL]
  - Retrieval API supports `document_ids` and `metadata_condition` filters (operators include is/not/in/contains/range/empty) — usable to filter `status=ACTIVE` and pin `source_sha256`. [E-RF-API]
  - Returned chunks include document ID, position, and separate vector/term similarity scores (provenance for W4/W5). [E-RF-PY]
  - RAPTOR "AHC mode" (dataset-level hierarchical trees) stabilised May 2026 with better Recall@5/F1 than the old mode. [E-RF-RAPTOR]
  - Official MCP server (RAGFlow ≥ v0.18.0), API-key auth; maintainers recommend binding to localhost only. [E-RF-MCP]
- **Evidence (risks):**
  - Heavy: ≥4 cores, ≥16 GB RAM (32 GB recommended), ≥50 GB disk; runs Elasticsearch/Infinity, MySQL, MinIO, Redis, Nginx; Linux x86_64 with `vm.max_map_count ≥ 262144`. [E-RF-REQ]
  - Pre-1.0, fast-moving; upgrade friction (e.g. metadata visibility issues during v0.24→v0.25 upgrades; switching doc engine with `down -v` wipes data). [E-RF-REL][E-RF-ENGINE]
  - **Silent-zero failure modes observed in 2026:** retrieval with an empty `metadata_condition.conditions` list returned zero chunks (fixed via PR); the GitHub connector synced nothing under default settings (fixed). [E-RF-ZERO][E-RF-GH]
- **Integration pattern (when adopted):**
  1. Originals stay in git (or Git LFS) under the research path; RAGFlow is **disposable derived state**.
  2. `gov research sync` pushes changed files via API, deletes removed ones, maintains manifest `{path, source_sha256, ragflow_doc_id, dataset_id, parser, parser_version}`; full re-push must rebuild RAGFlow from scratch (D6).
  3. Every query passes explicit `metadata_condition` (never empty list) including authority/status; results enter only the **supplementary** block of the context packet.
  4. Canary queries per dataset at G1/G4 (DEC-037) to detect silent-zero regressions.
  5. MCP server bound to 127.0.0.1; API key in secret store, never in repo.
  6. Conclusions are written back as J1 evidence records in git citing `ragflow_doc_id` + `source_sha256`.
- **Hosting options:** local on demand (`docker compose up` for research sessions; slim image with external embeddings pointed at Ollama); small VPS; managed hosts (e.g. Elestio advertises from ~$55/mo). [E-RF-SLIM][E-RF-HOST]
- **Adoption trigger (any one):** research corpus > ~200 complex documents; scan-heavy or table-dense material where Docling output fails review on a 20-document sample; need for cross-document hierarchical summaries (RAPTOR) that DEC-036 synthesis cannot meet cheaply.
- **Default until triggered:** DEC-019 path.

### DEC-021 — Rejected for the authority layer
- **Status:** REJECTED (for authority) · **Basis:** ESTABLISHED
- **Graphiti / Zep:** each episode requires asynchronous LLM processing (~25s locally); works best with structured-output-capable services, smaller models cause ingestion failures. Non-deterministic and token-consuming. [E-GRAPHITI] May be reconsidered for *episodic/lesson* memory only.
- **LightRAG / Microsoft GraphRAG / Cognee:** LLM-extracted entity graphs — same objection. LightRAG merged multimodal parsing (MinerU/Docling) in May 2026 and now overlaps RAGFlow for compact stacks; a candidate alternative to DEC-020 for the research facet only. [E-LIGHTRAG]
- **BMAD:** many personas → more tokens per cycle and handoff failures as a debugging surface. [E-BMAD]

### DEC-022 — Provider adapters: rulesync
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Single source in `.rulesync/` generating CLAUDE.md, AGENTS.md, `.claude/`, Codex and other targets; `rulesync import` used during legacy-rule retirement (R1). [E-RULESYNC]
- **CI:** generated files must match source (drift = G2 failure). Generated adapters are never hand-edited.

### DEC-023 — Distribution: Copier (`gov init` / `gov update`)
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** `gov-os` repo is a Copier template; kernel files are template-owned; overlay files listed in `_skip_if_exists`; tags = releases. Update uses Copier's three-way merge. [E-COPIER][E-COPIER-SKIP]
- **Rule:** never hand-edit `.copier-answers.yml` (breaks the update diff). [E-COPIER-DOCS]
- **Lock:** `framework.lock` = `.copier-answers.yml` reference + file hash manifest generated at install.
- **Gates:** S1, S2 (partial), S3, S5, S6

### DEC-024 — Method skills: Superpowers, selectively
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Adopt selected Superpowers skills (test-driven development, systematic debugging, verification-before-completion, subagent-driven development with two-stage review). OpenSpec (DEC-011) remains owner of planning/spec artefacts — do not run Superpowers' brainstorm/plan workflow in parallel with OpenSpec proposals.
- **Evidence:** 14 SKILL.md files plus a session-start bootstrap reportedly under ~2k tokens; multi-host; listed in Anthropic's official plugin marketplace. [E-SUPERPOWERS][E-SP-MKT]
- **Gates:** F1, O3 (two-stage independent review)

### DEC-025 — Enforcement stack
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:**
  - Claude Code hooks: `SessionStart` (inject compact context + `br ready`), `PreToolUse` (path guard via exit 2 / `permissionDecision: deny`; the guard is a **default-deny allow-list** of the task's declared paths — see DEC-041), `PreCompact` + `Stop` (checkpoint; guard against loops with `stop_hook_active`), `SubagentStop` (worker return contract N4). [E-HOOK-CC][E-HOOK-EVENTS]
  - Codex hooks mirror where supported; Codex caps model-visible hook output at ~2,500 tokens → context packet delivered as file path + short summary, not inline. [E-HOOK-CX]
  - lefthook (pre-commit/pre-push) + CI run `gov check` tiers; gitleaks for secrets.
- **Gates:** A3, E1, N2, N3, O5 (G0–G3 local, G4–G5 CI)

### DEC-026 — Telemetry
- **Status:** PROPOSED · **Basis:** ESTABLISHED
- **Decision:** Start with Claude Code OpenTelemetry → local collector → Prometheus → Grafana (no cloud, light). [E-OTEL] Add Langfuse (plugin, self-host or cloud) when per-turn traces are needed. [E-LANGFUSE]
- **Primary metric:** governance tokens per completed task (DEC-004).
- **Gates:** P1, P2 (partial), U

### DEC-027 — Root of trust (solo scope)
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** Signed git tags (SSH signing) on `gov-os` releases + file hash manifest verified at install/update. Key rotation/revocation, offline envelopes and bootstrap-mode separation (full A2) DEFERRED.

---

## 4. Retrieval decisions

### DEC-030 — Retrieval completeness principle
- **Status:** ACCEPTED · **Basis:** OWNER
- **Decision:** A top-k or per-query token allowance (e.g. 8k) is a batch size, not an evidence-completeness limit. Retrieval supports multiple batches, pagination/continuation, facets, adaptive follow-up, multi-hop, provenance-preserving merge, deduplication, authority/current/superseded filtering, and an explicit stopping reason. Parallel facet retrieval → merge/filter → unresolved dependencies → sequential follow-up → repeat → bounded context compilation. Evidence larger than one packet uses hierarchical synthesis whose notes are derived, cited, lineage-preserving, disclose unresolved evidence, and are rebuildable.
- **Gates extended:** D2, D3, C9, W4, W10

### DEC-031 — Two separate budgets
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** (1) *retrieval spend budget* — scales with impact radius; (2) *final context packet budget* — fixed ceiling. Hitting (1) is a governed event, never silent truncation.

### DEC-032 — Retrieval loop runs in a disposable context
- **Status:** PROPOSED · **Basis:** ESTABLISHED (harness subagents) + SUGGESTION
- **Decision:** Iterative retrieval and synthesis run inside a research subagent; only the compiled, cited bundle returns to the implementing context.

### DEC-033 — Deterministic worklist for closure facets
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** `gov retrieve` resolves referenced IDs (spec, ADR, task, symbol) through the frontmatter graph and codebase-memory callers/callees to a radius-scaled depth at T0 (no LLM). LLM judgement only for the semantic facet. Completeness for deterministic facets = dependency closure to depth N; for semantic facets = saturation.

### DEC-034 — Stopping reasons (enumerated)
- **Status:** PROPOSED · **Basis:** SUGGESTION
```text
CLOSURE_COMPLETE             # no unresolved referenced IDs within depth limit
SATURATED                    # follow-up batch added < ~10% novel sources after dedup
DEPTH_LIMIT_REACHED          # closure incomplete beyond radius-scaled depth; gaps listed
BUDGET_EXHAUSTED_WITH_GAPS   # ceiling hit; unresolved list disclosed; escalate if R≥3
FACET_UNAVAILABLE            # index stale/down; NOT_FOUND ≠ absent
```

### DEC-035 — Radius-scaled budgets and task-class facets
- **Status:** PROPOSED · **Basis:** SUGGESTION (numbers are placeholders to tune from telemetry)

  | Impact radius | Facets | Max follow-up rounds | Synthesis |
  |---|---|---|---|
  | R0–R1 | code + tests | 1 | none |
  | R2 | + decisions, graph | ~3 | single pass |
  | R3+ | all (WHY, decisions, code, graph, tests, history) | ~8, then escalate | hierarchical + verifier |

  Facet selection also by task class (bug fix → code, tests, history, failures; spec change → decisions, graph, tests).

### DEC-036 — Synthesis notes: derived + deterministic citation check
- **Status:** PROPOSED · **Basis:** ESTABLISHED (RAPTOR/GraphRAG/map-reduce patterns) + SUGGESTION (check)
- **Decision:** Notes stored in `.gov-runtime/` (derived); invalidated when any cited `source_sha256` changes. G2 verifies every cited source ID exists at the cited hash and every quoted span appears in the source.

### DEC-037 — Zero-result canaries on every index
- **Status:** PROPOSED · **Basis:** SUGGESTION, motivated by ESTABLISHED evidence
- **Decision:** Each derived index (FTS/vector, codebase-memory, RAGFlow if adopted) has a small set of canary queries with known expected hits, run at G1 after reindex and at G4/G5. A canary miss marks the facet `FACET_UNAVAILABLE`, never "no evidence exists".
- **Motivation:** 2026 silent-zero defects in RAGFlow retrieval and connectors [E-RF-ZERO][E-RF-GH]; Contract rule "NOT_FOUND is never proof of absence".

---

## 4A. Decisions from the Rust repository review (2026-09-28)

Evidence for this section is the owner's own repository records: spec records D-0001…D-0011, ARCH-0001…0003, API-0001/0002, CIT-0001; Phase-1 and Phase-2 orchestrator state, ledgers, decision packages, the performance diagnostic, the model/context telemetry report and the trust-architecture existing-solutions review. Figures below are quoted from those records.

**Findings that motivate these decisions**
- Phase 1 targeted `OS_RELEASE_CANDIDATE_ACCEPTED` and delivered one subsystem (Signed Release Root, R1-accepted) — roughly Contract gate A2 — across 33 agent runs; Contract integration and Prompt-2 verification never ran.
- Phase 2 (18–25 Sep) ran ~97 agent runs; eight adversarial review rounds on the tool-install / class-authority surface each produced new HIGH findings; the product is frozen at `3c880d8` awaiting a "Context/Retrieval Bridge".
- Telemetry for the first 37 Phase-2 agents: ~3.5B tokens processed (>99% cache reads); every Opus-class agent peaked at 606k–965k context; the orchestrator session reached ~944k. Product source is 3.4 MB (~1.0–1.65M tokens). Full certification suite ~50 min machine-exclusive (~2.5 h single-threaded); target directories ~178 GB.
- The control-panel roadmap places adoption into Product A at Phase 9 of 11.
- The repository's own records already reached the key conclusions: the T2 HMAC seal is not proof-grade authority because a process with the owner's OS privileges can read the key; the recurring defect is the confused-deputy / ambient-authority problem; builder-authored property tests are not independent evidence; independence requires complete relevant context; optional features that repeatedly produce HIGH findings should be deleted, not wrapped.

### DEC-038 — Freeze and archive the Rust repository; do not delete it
- **Status:** SUPERSEDED by DEC-048 · **Basis:** SUGGESTION
- **Decision:** Stop all Phase-2 work (do not start the Context/Retrieval Bridge session). Commit or record any dirty worktree, tag the final state, create a verified `git bundle --all`, push to the private remote, then reclaim disk (remove worktrees, `cargo clean`). Keep the repository read-only as an asset.
- **Rationale:** Deletion is irreversible and the records hold real IP (trust research, root-cause analyses, the SRR implementation). Archiving costs only disk once `target/` and worktrees are removed.
- **Revisit trigger:** the assembled Gov OS needs a component the Rust code already provides (e.g. SRR release signing at R2, a `gov` binary behind API-0002).

### DEC-039 — Threat model: the Gov OS guards against mistakes and drift, not a same-privilege adversary
- **Status:** ACCEPTED (owner, 2026-09-29); to be written as ADR-0001 · **Basis:** ESTABLISHED (owner's own Phase-2 finding) + SUGGESTION
- **Decision:** The Gov OS's purpose is to keep agents accurate, bounded and traceable. It does **not** attempt to be a security boundary against a process running with the owner's OS privileges. The hard boundary is: git history, CI on a protected branch, and owner-signed approvals (signed commits/tags or PR approval by the owner's account). This is ADR-0001 of the new repository.
- **Rationale:** Phase 2's eight-round loop was an attempt to make a same-privilege process secure against itself; the repository's own records identify this as the confused-deputy / ambient-authority problem and concede the seal is not proof-grade.
- **Consequence:** No in-process trust classes beyond the simple rule inherited from D-0007 (DEC-046).

### DEC-040 — The Gov OS never executes install commands; tools are installed by the owner and pinned
- **Status:** PROPOSED · **Basis:** ESTABLISHED (Phase-2 evidence)
- **Decision:** No `gov tools install` equivalent and no argv classification. Third-party tools (DEC-011…DEC-026) are installed by the owner with a version pin recorded in `governance/project/tool-registry.yaml`; `gov doctor` only verifies presence and version.
- **Rationale:** The tool-install surface produced HIGH findings in every Phase-2 review round; "reading argv" cannot determine what executes.

### DEC-041 — Path guards are default-deny allow-lists; checks are derived, not enumerated
- **Status:** PROPOSED · **Basis:** ESTABLISHED (Phase-1 ledger L-0074 root cause)
- **Decision:** The PreToolUse write guard permits only the current task's declared paths (plus a small kernel-defined scratch set); everything else is denied. CI checks derive their scope from the repository (e.g. all records under `spec/`), never from a hand-maintained deny-list.
- **Rationale:** L-0074: a universal negative implemented as a positive enumeration fails silently as soon as the product grows a path the author did not list, and tests derived from the same list cannot notice.

### DEC-042 — Evidence classes and verifier context
- **Status:** PROPOSED · **Basis:** ESTABLISHED (OD-P2-07, OD-P2-10)
- **Decision:** Builder-authored tests, including property tests, are regression evidence only. Independent verification is used only in the FULL profile (R3+), by a fresh subagent that receives a bounded whole-system context pack from `gov context` (not the full repository).
- **Rationale:** Phase 2 showed builder property tests quantify over the implementation's own domain; the owner's OD-P2-10 recorded that independence without relevant context produces architectural ignorance.

### DEC-043 — Products resume immediately; the glue is built from real friction
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** Product A work restarts as soon as the off-the-shelf layer is installed (short CLAUDE.md/AGENTS.md, `br`, OpenSpec, codebase-memory-mcp, gitleaks). `gov` commands are added only when a real product task shows the need. Product B follows once Product A has run one real feature end to end.
- **Rationale:** The Rust Gov OS was never exercised on real work, including its own orchestration (which ran on Python scripts and an HTML panel). Dogfooding from day one prevents speculative scope.

### DEC-044 — Hard loop budget per surface
- **Status:** PROPOSED · **Basis:** ESTABLISHED (OD-P2-09 simplification principle) + SUGGESTION (numbers)
- **Decision:** At most two review→repair rounds on any one surface. If the second round still finds a blocking defect, the default disposition is DELETE, NARROW or DEFER; continuing requires an explicit owner decision recorded as an ADR.

### DEC-045 — Original governance documents preserved unchanged; lean successors authored
- **Status:** PROPOSED, amended by DEC-049 (location of the originals) · **Basis:** SUGGESTION
- **Decision:** Framework v4.1.2, the two protocols and Contract v3 are copied unchanged (with SHA-256 sums) into `docs/source/originals/` of the new repository as owner reference. No agent reads them by default. Lean successors are authored with the owner: Framework v5 (short operating model), a Solo Core acceptance profile derived from §6 of this register, and a new control panel.

### DEC-046 — Assets carried from the Rust repository
- **Status:** PROPOSED · **Basis:** ESTABLISHED (records reviewed)
- **Carry as principles/specs:** D-0007 trust direction (simplified: "approved/verified/registered" facts come only from git records plus owner-signed commits or PR approvals); D-0003 enforcement map (every policy key maps to an executable check or is declared informational); D-0005/D-0006 fail-closed pinned embedder with benchmark; API-0002 CLI JSON envelope and exit codes 0–4 as the `gov` interface; the record schema conventions (supersedes / amends / state_class, amendments by new record); L-0074 and the Phase-2 root-cause lessons as `docs/lessons/`.
- **Carry as archived reference only:** ARCH-0003 and the R1-accepted SRR implementation (candidate for R2 release signing later); the trust-architecture existing-solutions review; the performance diagnostic.
- **Leave behind:** D-0008 / ARCH-0002 (CP-1), D-0010/D-0011 plugin and tool-install machinery, the 61-prompt V8.x control panel.

### DEC-047 — New control panel: small, repository-backed
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** A single-file HTML panel with five phases — P0 Archive, P1 Gov OS v0.1 (assembled), P2 Adopt Product A, P3 Adopt Product B, P4 Operate and improve — each with its stages, prompts and exit checks. State is exported/imported as a JSON file committed to the repository so the panel is never the only copy.

---

### DEC-048 — Archive is one inert git bundle outside any working tree; the working copy is deleted
- **Status:** SUPERSEDED by DEC-051 (owner decision) · **Basis:** OWNER + SUGGESTION · **Supersedes:** DEC-038
- **Decision:** Collect the seed set (`collect_gov_seed.sh`), then create one verified `git bundle --all` of the old repository with a SHA-256 file under `~/archives/` (optionally a second copy off the machine). Delete the working folder and its outside footprint (scratch worktrees, bridge caches, sealed oracle, Claude Code project transcripts/memory). The new repository starts with a fresh `git init`; no history is rewritten and no archive is placed inside it.
- **Rationale:** Storage is not the constraint (635 GiB free, plus ~800 GiB recoverable by compacting WSL). Anything inside the new working tree is reachable by agent search and indexers, which recreates the context-bloat and competing-authority problem; a bundle is inert until deliberately cloned. Clearing history and embedding the files would discard provenance while keeping the influence risk.

### DEC-049 — Original documents stay out of the new repository; provenance by hash
- **Status:** SUPERSEDED by DEC-053 Q5 (originals kept in-tree under `docs/source/`, excluded from agents and indexes) · **Basis:** OWNER + SUGGESTION · **Amends:** DEC-045
- **Decision:** Framework v4.1.2, the two protocols, Contract v3 and the V8.3 panel live in the Claude Project knowledge and in the bundle, not in the repository. The repository carries `docs/SOURCES.md` listing each original by name and SHA-256, plus the bundle's SHA-256 and final tag, so every lean successor can cite what it derives from.

### DEC-050 — Workstation hygiene
- **Status:** PROPOSED · **Basis:** ESTABLISHED + SUGGESTION
- **Decision:** New repositories gitignore `.claude/worktrees/`, `target/`, `.gov-runtime/`; no long-lived in-repo worktrees. WSL stays non-sparse (sparse VHD is gated by Microsoft for potential data corruption); after large deletions, compact `ext4.vhdx` with `wsl --shutdown` then DiskPart or `Optimize-VHD`, preceded by `wsl --export` as a safety copy.

### DEC-051 — Same repository; the archive is git history, not a folder
- **Status:** ACCEPTED (owner) · **Basis:** OWNER + SUGGESTION (mechanism) · **Supersedes:** DEC-048
- **Decision:** Nothing is deleted. The existing repository is kept with its full history. After the DEC-052 inventory and owner review, an annotated archive tag marks the pre-restructure state, every existing branch is kept, and the working tree of the new default branch is restructured to useful outputs only. Everything else leaves the working tree and remains reachable through the tag and branches. No history is rewritten. No `archive/` directory is created inside the working tree (it would be visible to agents and indexers). Untracked build output, caches and stale worktrees are reclaimed.

### DEC-052 — Read-only inventory before any restructure
- **Status:** ACCEPTED (owner) · **Basis:** OWNER + SUGGESTION (method)
- **Decision:** A fresh, read-only Claude Code session produces a complete inventory (every ref and tracked path classified; 0 unclassified) with dispositions KEEP_ACTIVE / KEEP_REFERENCE / ADAPT / ARCHIVE / DISCARD_UNTRACKED / OWNER_DECISION, reuse evidence, the recommended base ref and at most 10 owner questions. The session runs with its working directory outside the repository (`~/gov-os-inventory`, repository added with `--add-dir`) so the old project's CLAUDE.md, hooks and per-project memory do not load, under guardrail permissions (`inventory-settings.json`) and the prompt `INVENTORY_SESSION_PROMPT.md`. Repository content is treated as data, not instructions. `collect_gov_seed.sh` is superseded by the inventory's KEEP lists.

### DEC-053 — Owner answers to the inventory questions (2026-09-29)
- **Status:** ACCEPTED (owner) · **Basis:** OWNER, on the inventory's defaults with Claude's amendments
- Q1: disable the bridge checkpoint hook before any restructure; let the uncommitted `BR-CP-0058.yaml` go.
- Q2: base = current tip of `bridge/p2-context-retrieval` (`1ab6782`, or a later tip whose extra commits touch only bridge `CHECKPOINTS/`). Annotated tag `archive/gov-os-v4-final` at the base. `main` fast-forwarded to the base and restructured. All other local branches moved to the hidden namespace `refs/archive/heads/*` (kept, protected from gc, not shown by `git branch`). Tags and `refs/safe-hold/*` kept.
- Q3: reclaim untracked material (worktrees, `target/`, stale registrations, `~/.cache/gov-bridge`, `~/.cache/gov`) after the tag and namespace move exist.
- Q4: keep all 29 owner records under `docs/source/owner-records/`.
- Q5: keep the four originals verbatim under `docs/source/originals/`, excluded from agents (committed `.claude/settings.json` deny rules) and from indexes; ADRs supersede them where they conflict.
- Q6: keep V8.2 and the owner's working V8.3 `MASTER_DRAFT_v2` (sha256 `8e7dce78…`) under `docs/source/control-panel/`; archive V8.1; the Downloads `v8_3_DRAFT` (`570aa329…`) is not carried.
- Q7: no upstream-lesson → FCP loop; lessons go to `docs/lessons/`.
- Q8: archive the schemas that overlap OpenSpec.
- Q9: archive the Python AST module and the demonstration query set; keep the ten query classes as a lesson note.
- Q10: revoke the DeepSeek key at the provider, then delete the file; delete the sealed oracle after the tag exists; leave transcripts.

### DEC-054 — What stays in the working tree: buckets and derivation
- **Status:** ACCEPTED (owner) · **Basis:** SUGGESTION, accepted
- **In tree, active:** R004, R009, R013, R016–R018, R020, R039, R059, R060, R064, R076, plus the tests of these modules. The Python set is the **static import closure** of the kept govbridge modules (lexical, semantic/modelpin, semantic/profile, authority), plus the config and schema files they reference by name, plus the test files whose imports fall inside that closure. Derived, never hand-enumerated (L-0074).
- **In tree, reference only:** R001, R002, R053, R054, V8.2, V8.3 MASTER_DRAFT_v2.
- **Seeds (read from the archive, not copied):** R006–R008, R011, R025, R026, R032, R055, R057, R058, R085, R084 query classes.
- **Mine later (archive; pulled per command):** R021, R023, R028, R031, R033, R035, R043–R049, R061–R063, R067, R069, R071, R078, R079, R081–R083, remainder of R074.
- **Archive:** everything else, including R010, R022, R040, R084 files.
- **Rule:** the restructure commit is move-and-remove only. The only files it creates or edits are `.gitignore`, `README.md`, `docs/SOURCES.md`, `.claude/settings.json`, `.gitleaks.toml` and empty placeholders. Content adaptation happens in later sessions.
- **Rule:** the Rust port rows are not ported; the new `gov` is written fresh and consults the archive when needed.

### DEC-055 — Pre-restructure maintenance
- **Status:** ACCEPTED (owner) · **Basis:** SUGGESTION, accepted
- **Decision:** Neutralise the hook script (renamed, reversible), remove its wiring from the repo's untracked `.claude/settings.local.json` (backup kept), install gitleaks to `~/.local/bin` with checksum verification, and take a `git bundle --all` backup before any ref surgery. Old per-project Claude Code auto-memory for this repository path, if present, is moved aside only with explicit owner approval.

### DEC-056 — Restructure executed (record of facts, 2026-09-29)
- **Status:** DONE · **Basis:** session report
- Base `1ab6782fa4e8f490c8b97ac6959cdd77a29350f9`; annotated tag `archive/gov-os-v4-final` (tag object `6e4ae20`).
- Bundle `~/gov-os-inventory/restructure/pre-restructure.bundle`, verified, sha256 `efafe460af693d4159ba4549067309c20c5a2def2aabc0284527aacfc0532434`.
- 168 branches moved to `refs/archive/heads/*` with matching shas; `main` is the only branch; tags, `refs/safe-hold/*` and `refs/codex/*` unchanged. 72 linked worktrees removed; the read-only `br-frozen-3c880d8` was moved to `~/gov-os-inventory/restructure/`.
- Restructure commit `903f367` on `main`: 222 files, 1,628,338 bytes; 157 moved and 58 kept in place, all byte-identical to base except `.gitignore`; all 7,305 removed paths readable from the tag; gitleaks 8.30.1 clean.
- Python closure: 115 files (36 modules, 6,854 LOC; 22 modules pulled in from outside the active bucket: `core/`, `compile/sectionmap`, `gather/facets`, `graph/edges`, `semantic/{freshness_layer,vectors,runner}`). 63 tests and 5 support files excluded.
- Tests: from `cli/` 159 passed, 15 failed, 2 skipped. Failures: missing ONNX adapter (12, replaced by DEC-017), canonical view pinned to the archived bridge branch (2), missing `python -m govbridge` entry point (1, replaced by the `gov` CLI). From the repository root: collection errors (`sys.path`).
- Build output and caches deleted; empty directory skeletons moved to `~/gov-os-inventory/restructure/ignored-leftovers/`. Repository size 55 MB.
- **Open:** DEC-039 (threat model) becomes ADR-0001 on owner acceptance; Product A not yet named (OQ-04).

### DEC-057 — S0 research and discovery before any rebuild
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER
- **Decision:** Before building, a research phase establishes (a) a capability catalogue re-expressed from the owner's originals and owner records, with each capability marked CORE / LATER / DROP against ADR-0001, and (b) the tool landscape per capability category with footprint (disk, RAM, VRAM, Docker), cost, maintenance, harness- and language-agnosticism, and where state lives. S0a is desk research (web allowed, no installs); an owner gate approves the shortlist; S0b is a hands-on bake-off on the repository fixtures with measured resource and token costs. The new S1 is drafted from S0 outputs.
- **Framing carried into S0:** the Gov OS extends agents' context and memory; authoritative memory and context live in the repository (git-tracked records, rebuildable derived indexes), never in the agent or a vendor account; it must be agnostic to project type (an MCP server, a dashboard, a physics kernel, an operating system), language and agent harness.

### DEC-058 — Originals are not edited; successors replace them; `docs/source/` is archived afterwards
- **Status:** ACCEPTED (owner direction, 2026-09-29) · **Basis:** OWNER + SUGGESTION
- **Decision:** Framework v4.1.2, the two protocols and Contract v3 stay unchanged as provenance. Their wanted features are re-established in two successors written from the S0 catalogue: a short **Charter v5** (purpose, threat model, principles, proportionality, loop budget) and **Contract v4** (outcome-level capabilities with one observable acceptance check each, a CORE/LATER profile, the providing tool, and explicit non-goals). Once both are accepted, all of `docs/source/` (originals, owner records, old control panels) leaves the working tree and remains reachable through the archive tag. Until then it stays in the tree, excluded from normal agent sessions, because S0 reads it.
- **Diagnosis recorded:** the drift did not come from the feature list but from an unstated threat model, acceptance defined as exhaustive adversarial closure, no loop budget, and normative documents loaded into every session.
- **Control panel:** the old V8.x panels are archived with `docs/source/`. Stage state for the new plan lives in the repository (a small committed plan/state file); any panel UI only reads and writes that file.

### DEC-059 — S1 stabilisation deferred
- **Status:** ACCEPTED (owner, 2026-09-29)
- **Decision:** The `S1_STABILISE_PROMPT` is not run. The carried `govbridge` code may be replaced by tools chosen in S0; fixing its tests first would be wasted work. The carried code is evaluated in S0 as an in-house candidate.

### DEC-060 — One agnostic Gov OS; projects differ only by overlay configuration
- **Status:** ACCEPTED (owner, 2026-09-29)
- **Decision:** There is one Gov OS release line for every project type. Projects differ only in their committed overlay configuration (path map, enabled capabilities such as code-intelligence languages or a research corpus, policy strengths). The choice of which product adopts first is a sequencing decision for dogfooding, not a variant. OQ-04 is deferred to the adoption stage.

### DEC-061 — One workbench folder for out-of-repo sessions
- **Status:** ACCEPTED (owner, 2026-09-29)
- **Decision:** `~/gov-os-inventory` is renamed `~/gov-os-workbench` and holds every out-of-repo session: `inventory/` (the completed inventory), `restructure/` (bundle, ref snapshot, scripts, leftovers), `input/` (register), `s0a/`, later `s0b/`. A symlink `~/gov-os-inventory → ~/gov-os-workbench` keeps the bundle path cited in `docs/SOURCES.md` valid. Session settings deny edits to `inventory/`, `restructure/`, `input/` and `.claude/`.

### DEC-062 — GitHub access through `gh` with a read-only fine-grained token
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** Research sessions read GitHub metadata through the GitHub CLI authenticated with a fine-grained token limited to public repositories, read-only, with an expiry. The token lives in the `gh` credential store, never in a repository, a workbench file or a prompt. Any older token found in plaintext is revoked. The earlier ad-hoc GitHub harness is not revived.

### DEC-063 — Repository settings files
- **Status:** ACCEPTED (owner, 2026-09-29)
- **Decision:** Keep the committed `.claude/settings.json` (deny rules for `docs/source/`). Keep the untracked, gitignored `.claude/settings.local.json` (per-user; Claude Code writes approvals there). Remove `.vscode/` and ignore it. Remove the empty `.claude/worktrees/`.

### DEC-064 — Full scope, built in waves, released once
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER
- **Decision:** Every capability in Contract v3 that survives ADR-0001 is in scope, including the full 26-dimension readiness contract and everything previously marked "Later". The Gov OS is built in three waves (Wave 1 Integrate, Wave 2 Strengthen, Wave 3 Complete), each ending in an exit check, and released **once** as Release 1 (signed `v1.0.0`) after qualification (DEC-067). Adoption into product repositories starts only after Release 1. Supersedes the "R1 → R2 if friction → Later if needed" framing of architecture v0.1 and S0a Q4's demotions.
- **Consequence:** DEC-001's ~3k-line revisit trigger becomes a per-wave review (glue ≈ 4.5k LOC across three waves).

### DEC-065 — Master rules (constitutional, every session, every Gov OS)
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER, grounded in Framework v4.1.2 §23–25, §36–39, §52–54 and Contract v3 H, I, K, L, O3
- MR-1 Specification first: discovery Q&A between agent sessions and the human customer closes a spine or feature specification (26-dimension readiness; silent N/A invalid).
- MR-2 Closed specifications generate the WBS: tasks, dependencies, order, roles; readiness gaps generate tasks; no production task is READY before its specification's required cells are satisfied.
- MR-3 Every task carries KPIs; an independent, freshly spawned test designer writes the acceptance tests from them before implementation; the implementer's allowed paths exclude the acceptance tests; builder tests are regression evidence only.
- MR-4 Discovery, impact (CIT-P), execution (CIT-E), audit and `gov doctor` are distinct functions.
- MR-5 The Gov OS works as a virtual software company of role agents; models are replaceable workers.
- MR-6 The human is the customer and final authority (L5): decision packages in the active chat, ranked and batched, non-blocking for independent branches, answers recorded in git.
- These rules go verbatim into Charter v5 and apply to the Gov OS's own development from S1.

### DEC-066 — Organisation layer and the five distinct functions
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER + SUGGESTION (mechanism)
- **Decision:** Roles are subagent definitions generated by rulesync from kernel role files plus a project roster; each carries purpose, allowed-path pattern, tools, model tier, authority level and handoff format. Wave 1: orchestrator, product/specification, independent test designer, engineer, independent auditor. Wave 2: architecture, frontend, backend, database/data, integration/API, DevOps/SRE, security, performance, UX, typed handoffs. Wave 3: research, AI/ML, data author, change controller, memory/knowledge, tooling, release, claims/concurrency. `gov doctor` (installation health), discovery skill + `gov readiness`, `gov impact` (CIT-P), OpenSpec apply/archive + `gov close` (CIT-E), and the audit skill with an Independent Auditor role are separate.

### DEC-067 — Two layers of testing; Gate V returns as qualification
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER, from the old control panel's Phase 4 (AQ-1) and Contract v3 Gate V
- **Decision:** Layer 1 = mechanism fixtures and per-wave tests in CI. Layer 2 = two synthetic programmes of different shape and aim: **Programme A**, greenfield R&D build (idea → release through the spec-first cycle, a customer gate, a mid-programme change); **Programme B**, brownfield adoption and recovery (scattered legacy platform with planted hazards). Each has a dev tier (open, used during S0b2 and the waves), a qualification tier and an optional stress tier, a simulated customer, and chaos/recovery/soak/isolation scenarios. The held-out oracle (fault manifest, path-map and memory oracles, gold answers, forbidden outcomes, customer answer key, scorecard) lives in `~/gov-os-workbench/qualification-oracle/`; builder sessions are denied read access and the architect sees only the coverage matrix and scorecard format. CAP-49 changes from DROP to KEPT (as qualification). The G6 chaos/soak tier moves into qualification. Scenarios phrased as attacks in the old brief become mistake scenarios under ADR-0001.

### DEC-068 — S0b split into S0b1 and S0b2
- **Status:** ACCEPTED (owner, 2026-09-29)
- **Decision:** S0b1: an independent scenario architect builds both synthetic programmes in the workbench (deterministic generators, dev tier public, qual tier and oracle held out, coverage matrix over all 60 capabilities) without reading Gov OS implementation code. S0b2: the chosen tools are installed in a sandbox, tested together end to end on the dev tiers, the four open choices are decided (retrieval, code intelligence, decision records, task tracker) and resources are measured, including a codebase-memory probe on the qualification tier.

### DEC-069 — Test independence enforced mechanically
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** SUGGESTION, implementing MR-3
- **Decision:** Acceptance tests live under `tests/acceptance/` and are written only by the Independent Test Designer role from the task's KPIs and the specification. The implementer role's allowed paths never include them (default-deny guard, DEC-041). An implementation task becomes READY only when its acceptance tests exist. `gov close` runs them.

### DEC-070 — Independent fidelity audit of the successor documents, and audit at every wave exit
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER, implementing MR-4
- **Decision:** After S1 drafts Charter v5, Contract v4, ADR-0001 and ADR-0002, a fresh read-only Independent Auditor (S1-A) builds a traceability matrix: every clause of the originals and owner records maps to the carrying clause, or to its recorded disposition and the decision behind it. Rows are classed OK / MISSING / WEAKENED / CONTRADICTS / UNJUSTIFIED_DROP / SCOPE_CREEP. It checks that MR-1…MR-6 appear verbatim, that all 26 readiness dimensions are carried, and that nothing reintroduces same-privilege-adversary machinery. The yardstick is the originals **plus** the accepted decisions, so a recorded drop is not a defect. At most two audit→repair rounds; contested findings go to the owner as decision packages. `docs/source/` is archived only after S1-A closes. The same role audits each wave's output against Contract v4 at the wave's exit. Recorded in architecture v0.3 (MR-4, §2.5, §6.1, §7).

### DEC-071 — S0b1 complete (record of facts, 2026-09-29)
- **Status:** DONE · **Basis:** session report
- Programme A (ORION, greenfield R&D) and Programme B (ARGUS, brownfield) with deterministic generators; dev tiers public in `~/gov-os-workbench/synthetic/` (151 files each; 757 and 697 chunks; manifests `64a2e302…`, `5a4d922d…`); qual tiers held out (≈1,269 and ≈1,461 files; ≈12.7k and ≈15.0k chunks); stress tier for B only (×4: 5,355 files, 57,777 chunks).
- Determinism: byte-identical on repeat, including modes and git ids. Oracle verifier 349/349 claims true, 21/21 extra checks; no qual fault reuses a dev hazard; no leakage between tiers.
- Coverage 57/57 in-scope capabilities; 3 marked N/A (CAP-26, CAP-49 as "the pack itself is the mechanism", CAP-60). 105 dev and 198 qual scenarios; 52 dev queries; public scorer with 18 metrics; any forbidden outcome fails qualification.
- Not fully synthetic: CAP-02/CAP-43 (release signature and immutability: a release audit with `git tag -v`), CAP-47 (the qualification run's own fresh-verifier transcript), CAP-36 (analysis over real usage). Rust and TypeScript are syntax-checked only until S0b2 installs toolchains.
- The matrix still shows S0a's CORE/LATER labels; Contract v4 relabels them by wave (DEC-064).

### DEC-072 — S0b2 scope and guardrails
- **Status:** ACCEPTED (owner, by running it) · **Basis:** SUGGESTION
- **Decision:** S0b2 installs the stack user-level (owner approves each install; versions pinned; uninstall commands recorded), runs twelve integration checks (I-01…I-12) on sandbox clones of the dev tiers, decides the four open choices by BAKEOFF_PLAN's fixed rules (retrieval tie-break now "shared store", since Node ≥ 20.19 is needed for OpenSpec anyway), compiles the dev tiers' Rust and TypeScript for the first time, and measures resources. The scale probe indexes an owner-generated qual tier of Programme B in `s0b2/probe/`; the session may not read its contents or the oracle. beads_rust excluded (Q2). Running S0b2 accepts S0a Q2, Q6 (probe on the qual tier) and Q7 (user-level, approved installs); Q1, Q3, Q5, Q8, Q9 settle in S1; Q4 is superseded by DEC-064.

### DEC-073 — Operating model until the Gov OS lands
- **Status:** ACCEPTED (owner, 2026-09-30)
- **Decision:** One **operator console** session (`~/gov-os-operator`: broad allow, ask for destructive commands, deny for secrets, the oracle, `sudo` and force-push; command log hook; charter in `CLAUDE.md`) replaces the owner at the terminal and is driven over Remote Control. Each repository has its own interactive session, reached over Remote Control and cleared with `/clear` between tasks; settings changes are made by the operator and take effect in a new session. Prompts and settings are saved as files (by the operator, from pasted text or the inbox) for provenance. Files reach the architect chat through the owner's laptop. User-level `rm` rules moved from deny to ask; restricted sessions keep their own deny. Temporary: after Release 1, one session per repository with fresh context per task, independence coming from role subagents.

### DEC-074 — S0b2 decisions and the owner's answers (2026-09-30)
- **Status:** ACCEPTED (owner)
- **Bake-off (fixed rules):** retrieval **R1** (carried FTS5 + sqlite-vec + Qwen3-Embedding-0.6B via Ollama + Qwen3-Reranker-0.6B + RRF; hit@5 85 vs 76, 0.24 s vs 28 s, 2.2 vs 5.1 GB); code intelligence **C1** codebase-memory-mcp 0.11.0 (20 MB peak; qual-B probe 19.7 MB, 7.4 s, 47 MB index); tasks **T3** wedow/ticket v0.3.2, vendored into the kernel template (sha256 `408f2c11…`) + claim glue; decisions **D2** MADR + check-jsonschema + checker. Supersedes DEC-013 (`br`) and the Backlog.md choice in architecture v0.2/v0.3.
- **Owner answers:** Q1 stack Balanced · Q2 ticket · Q3 reranker accepted for W1, lighter replacement spiked in W2 (5.6 GB is disk; ~2.2 GB RAM and ~1.2 GB VRAM only while a query runs) · Q4 Ollama on demand, 5-min idle unload · Q5 Superpowers: copy three skills (test-driven-development, systematic-debugging, verification-before-completion) through rulesync; not the plugin and not subagent-driven-development (conflicts with MR-3 and OpenSpec, and adds a foreign SessionStart hook) · Q6 adapters for Claude Code + AGENTS.md from one rulesync source, version pinned · Q7 rulesync owns `.claude/`; OpenSpec and vendored skills registered as rulesync sources · Q8 content-based secret filter before every indexer, ours and codebase-memory's (W1 gate) · Q9 deny rules for `.env`, `.pem`, `.key`, secret config · Q10 codebase-memory wrapped per repository (private home under `.gov-runtime/`, so `list_projects` sees only its own index) · Q11 the four LITE forms accepted · Q12 private GitHub repository, push `main` only · Q13 no GitHub Pro: CI advisory · Q14 the independent S0b1 author patches both tiers' TypeScript defects and re-verifies the oracle · Q15 scale probes on `~/EXAMIN APP` and `~/workspace` before Wave 2.
- **S0b2 facts:** 6 PASS, 5 PARTIAL, 0 FAIL, 1 BLOCKED (I-09, closed afterwards by the operator: skill sizes 2,389 / 2,360 / 899 / 8,089 / 795 tokens). Stack ≈ 11.9 GB disk, one on-demand daemon, no Docker, VRAM peak ≈ 5.2 of 16 GiB, ≈ 10.3 GB RAM worst case with the IDE. Housekeeping done: Ollama stopped, probe and its index deleted, rejected tools uninstalled.

### DEC-075 — ADR-0001's hard boundary without branch protection
- **Status:** ACCEPTED (owner, Q13) · **Amends:** DEC-007, DEC-039
- **Decision:** Without GitHub Pro, `main` is not protected. The boundary is: the lefthook pre-push gate (G3) on the owner's machine, GitHub Actions CI (G4–G5) as a visible advisory result on every push, and the owner's rule that only the owner merges, and only on green. ADR-0001 and Contract v4 state this explicitly. Enabling protection later changes no other decision.

### DEC-076 — Wave 1 adjustments from S0b2
- **Status:** ACCEPTED (owner, via Q-answers) · **Basis:** SUGGESTION
- G-02 (post-command `git status` containment against `allowed_paths`) moves from W2 to **W1**: it is the non-enumerative enforcement of MR-3.
- codebase-memory in W1 must prove (a) a per-repository home isolates `list_projects`, and (b) the pre-index secret filter or an ignore mechanism keeps secrets out of its index.
- S0b2's glue list and the stack plan's components are merged into one numbered W1 task list in S1 (the two G-numberings collide).
- Superpowers' subagent-driven-development is excluded; the Gov OS's own orchestration and independent test-design skills replace it.

### DEC-077 — GitHub write access through a per-repository deploy key
- **Status:** DONE (2026-09-30; see DEC-079) · **Basis:** SUGGESTION
- **Decision:** Pushes to the private `gov-os` repository use an SSH deploy key with write access to that repository only, generated on the WSL machine; only its public half leaves the machine. No broad personal token is created and no secret is pasted into a chat. The read-only `gh` token (DEC-062) stays as it is.

### DEC-078 — Real-repository scale probes and a corrected RAM figure (2026-09-30)
- **Status:** DONE · **Basis:** operator report
- `~/EXAMIN APP`: 1,378 files indexed, 24,665 nodes / 81,356 edges, 6.1 s, **57 MB** peak RSS, 86 MB index. `~/workspace`: 1,005 files indexed, 77,346 nodes / 270,647 edges, 61.4 s, **2.2 GB** peak RSS, 215 MB index. No GPU use. `.gitignore` is respected (`workspace/ASMO/.env` not indexed).
- **Correction:** codebase-memory-mcp runs a separate daemon and worker; S0b2's "20 MB peak" measured only the CLI process. Memory scales with graph size (edges), not file count.
- **Envelope for Contract v4:** tested up to ≈ 80k nodes / 270k edges at ≈ 2.2 GB peak; larger graphs are measured before adoption. Worst-case RAM with IDE + models + a full index run ≈ 12.5 GB of 15.5 GiB (≈ 2.5 GiB spare); incremental updates are far smaller. `workspace` holds several projects; each gets its own index when adopted. Probe indexes and all codebase-memory logs deleted afterwards.

### DEC-079 — Private GitHub remote established
- **Status:** DONE (2026-09-30)
- `UK-RH-HK/gov-os` (private). `main` pushed through the per-repository deploy key (`~/.ssh/gov_os_deploy`, host alias `github-gov-os`); no tags or other refs pushed. GitHub's ED25519 host key verified.

### DEC-080 — Retrieval completeness entirely in Wave 1
- **Status:** ACCEPTED (owner, 2026-09-30) · **Amends:** DEC-030…DEC-037 wave placement, architecture v0.3 §4/§6
- **Decision:** Wave 1 delivers the whole retrieval-completeness capability: `gov retrieve` paging with continuation (batch size configurable, never a completeness limit); parallel facet subagents (decisions, code, tests, history, why, …); deterministic closure (`gov closure`); deduplication by chunk hash and authority filtering; one rerank over the merged candidate set; a cited evidence-bundle format (citations by id and hash, stopping reason from the fixed list); the citation validator; zero-result canaries; and hierarchical synthesis notes (derived, cited, hash-checked) when evidence exceeds the packet budget. Wave 1's exit runs RETR-A-04 and RETR-X-02 on the dev tiers. Estimated +≈400 LOC in Wave 1.

### DEC-081 — How S1 runs
- **Status:** ACCEPTED (owner, by running it) · **Basis:** SUGGESTION
- **Decision:** S1 is one session and one author (subagents only for mechanical extraction, counting and validation), running from `~/gov-os-workbench/s1/` with the Gov OS repository as an additional directory. It applies MR-1 and MR-6 to the Gov OS itself: it builds the Gov OS's own 26-dimension readiness table, asks the owner only what the sources don't answer, as ranked decision packages, and records the answers. It then writes Charter v5, Contract v4 (all 60 capabilities, with waves, acceptance checks, providers, sources and scenario ids), ADR-0001, ADR-0002, and the Wave 1 WBS as tickets with KPIs, roles and allowed paths. Everything goes on branch `s1/spec` of the Gov OS repository, and the register is committed as `docs/DECISION_REGISTER.md`. S1 does not push, merge, implement, or write acceptance tests (those are the Independent Test Designer's, MR-3).

### DEC-082 — How S1-A runs, and what closes S1
- **Status:** ACCEPTED (owner, by running it) · **Basis:** SUGGESTION, implementing DEC-070
- **Decision:** S1-A is a fresh, read-only session in `~/gov-os-workbench/s1a/`. It builds its own traceability matrix from the originals **before** looking at S1's source map. Its yardstick is the originals plus decisions whose status is ACCEPTED or DONE; PROPOSED entries justify nothing. Verdict: ACCEPT, ACCEPT_WITH_FINDINGS or REJECT, at most two rounds. After closure, the owner merges `s1/spec` into `main`; then `docs/source/` is archived (removed from the working tree, reachable through the tag); then Wave 1 starts.

## 5. Proposed Contract v3 amendments

| ID | Amendment | Affects |
|---|---|---|
| AMD-01 | **Governance overhead budget** as a hard SLO (DEC-004) | U, A4 |
| AMD-02 | **Proportionality profiles** LITE/STANDARD/FULL keyed to R0–R5 (DEC-005) | H2, K4, O3, T |
| AMD-03 | **Progressive adoption** — governable before A11 completes (DEC-006) | S4, T3 |
| AMD-04 | **Native-first / hooks-are-guardrails** — CI is the enforcement boundary (DEC-007) | N3, O5, A3 |
| AMD-05 | **Retrieval completeness & stopping reasons** as an extension of D2 (DEC-030–035) | D2, D3, C9, W4 |
| AMD-06 | **Zero-result canaries** per index (DEC-037) | D1, D6, O2 |
| AMD-07 | **Tool-substitution contract** — every adopted tool sits behind a `gov` adapter with a recorded replacement path and exit procedure | D4, F2, F3 |
| AMD-08 | **Synthesis citation check** (DEC-036) | W5, J1 |

---

## 6. Solo Core profile (first pass)

| Gate | Profile | Implemented by |
|---|---|---|
| A1 Authority/precedence | CORE | frontmatter status + `gov check` |
| A2 Root of trust | DEFERRED (lite in CORE) | signed tags + hash manifest (DEC-027) |
| A3 Security/sensitivity | CORE | gitleaks, PreToolUse path guard, index exclusion lists |
| A4 Budgets | CORE (monitor) / DEFERRED (enforce) | telemetry + plan limits |
| A5 Emergency controls | CORE (minimal) | `gov pause` = freeze-writes flag read by PreToolUse; git revert |
| B1–B3 Repo contract/path map/derived state | CORE | overlay `path-map.yaml`, `.gov-runtime/` gitignored |
| C1, C2, C4, C5, C9 | CORE | SQLite from frontmatter, FTS5, codebase-memory, `gov context` |
| C3 Semantic | CORE (small) | sqlite-vec + Qwen3 |
| C6–C8 Temporal/episodic/failure | CORE (via git log, `br`, checkpoints) | — |
| C10 Capability memory | CORE (lite) | tool registry YAML |
| D1–D4, D6 | CORE | DEC-014/016/017, `gov rebuild` |
| D5 Retrieval bake-off | DEFERRED | — |
| E1–E4 | CORE (lite) | role/path policy in hooks; `br` claims |
| F1, F2, F5 | CORE | Superpowers + own skills; tool registry |
| F3 Missing-tool acquisition, F4 Plugin trust | DEFERRED | — |
| G1–G2 Command surface | CORE | natural language + `gov status/continue/decide/audit/pause` |
| H1–H4 | CORE (reduced H2 per DEC-005) | OpenSpec + custom schema |
| I1–I4 | CORE | `br` |
| J1–J2 | CORE (lite) | DEC-019, research records |
| K1–K4 | CORE | OpenSpec + `gov impact` |
| L1–L4 | CORE | gate package printed in chat; decisions recorded as ADR |
| M1–M3 | CORE (declared) · M4 DEFERRED | role defaults in overlay |
| N1–N4 | CORE | hooks + `gov checkpoint` + CI watchdog |
| O1–O4 | CORE | product tests + `gov check` + subagent reviewers |
| O5 G0–G5 | CORE · G6 DEFERRED | hooks/lefthook/CI |
| P1 | CORE · P2 partial | DEC-026 |
| Q1–Q3 | CORE (lite) | lesson records with scope |
| Q4 Upstream export gate | DEFERRED | — |
| R1–R3 | CORE | adopt-lite + rulesync import |
| S1, S3, S5, S6 | CORE | Copier |
| S2 Immutable releases | CORE (lite) | tags + manifest |
| S4 `gov adopt` | CORE (progressive, DEC-006) | adopt-lite |
| T1–T3 | CORE (collapsed roles) | fresh subagents per role for R3+ |
| U Health SLOs | CORE (subset) | telemetry + `gov status` |
| V Qualification oracle | DROPPED_FOR_SOLO (revisit for Rust kernel certification) | — |
| W1–W10 | CORE | frontmatter IDs, `gov context`, commit trailers, `gov close` |
| W11–W12 | PARTIAL | `gov status` metrics |

---

## 7. Hardware & cost allocation

| Component | Where | Resource | Cost/month |
|---|---|---|---|
| Qwen3-Embedding-0.6B + Reranker-0.6B | RTX 5070 Ti (resident) | ~3 GB VRAM | $0 |
| gpt-oss:20b (T1, on demand) | RTX 5070 Ti | ~13 GB VRAM when loaded | $0 |
| SQLite index, codebase-memory, `br` | local | negligible | $0 |
| Docling conversions | local (GPU-accelerated if available) | batch | $0 |
| Grafana/Prometheus/OTel collector | local Docker | light | $0 |
| RAGFlow (CONDITIONAL) | local on demand / VPS / managed | ≥16 GB RAM | $0 local · VPS varies · managed ~$55+ |
| Claude Max 5x (or 20x) | cloud | — | $100 (or $200) |
| Optional second-family verifier | cloud | — | ~$20 |
| Optional headless/API credits | cloud | — | $20–50 |

**Starting position:** ~$120/month (Max 5x + optional verifier).

---

## 8. Per-repository layout & install

```text
product-x/
├── AGENTS.md, CLAUDE.md, .claude/     # generated by rulesync — never hand-edit
├── .rulesync/                          # generated from kernel + overlay
├── governance/
│   ├── kernel/        # Copier-owned: schemas, hook scripts, skills, gov pin
│   ├── project/       # overlay (_skip_if_exists): path-map.yaml, policy overrides, roles, tool-registry.yaml
│   └── framework.lock # Copier answers ref + file hash manifest
├── openspec/specs/  openspec/changes/  openspec/schemas/
├── spec/decisions/ADR-*.md
├── spec/research/sources/  spec/research/converted/  spec/research/records/
├── .beads/            # issues.jsonl tracked; SQLite gitignored
├── <native product layout, untouched>
└── .gov-runtime/      # gitignored: index.sqlite, synthesis notes, codebase-memory DB, checkpoints cache
```

Install sequence (wrapped by Copier post-copy tasks / `gov init`):
```text
copier copy <gov-os remote> . --vcs-ref vX.Y.Z
br init
openspec init
rulesync generate
lefthook install
gov doctor        # verifies tools, pins, hooks, canaries
gov rebuild       # derived state
```

---

## 9. Glue backlog (the only code to write)

| Command / artefact | Purpose | Gates |
|---|---|---|
| Frontmatter JSON Schema + templates (spec, ADR, research record, lesson) | stable IDs & lifecycle | W1, A1 |
| `gov context <task>` | deterministic authority block + supplementary block, budgeted, hashed | C9, W3, W4, W10 |
| `gov retrieve <task>` | facets, worklist closure, stopping reason (DEC-033/034) | D2, D3 |
| `gov check --tier g0..g5` | schema, IDs, supersession, orphans, path map, staleness, secrets, adapter drift, canaries | O2, O5, W6, W7 |
| `gov impact <ids|paths>` | frontmatter graph + codebase-memory impact → R0–R5 | K1, K4 |
| `gov close <task>` | G2: tests, commit trailers (`Implements:`, `Task:`), traceability | W5, O4 |
| `gov checkpoint` | structured checkpoint (called by hooks) | N1–N4 |
| `gov adopt --lite` | inventory → classification → path map → batched `git mv` | S4, B2, R1 |
| `gov research sync` | Docling conversion manifest; RAGFlow sync if adopted | J1, DEC-019/020 |
| `gov status` / `gov pause` | human control surface | G2, A5, U |
| Hook scripts (SessionStart, PreToolUse, PreCompact, Stop, SubagentStop) | enforcement guardrails | N, E1 |
| CI workflow | authoritative G4–G5 re-check | O5 |

---

## 10. Open questions for the product owner

- **OQ-01:** Size and messiness of the research corpus per project (drives DEC-020 trigger).
- **OQ-02:** OS environment — RAGFlow requires Linux x86_64 (`vm.max_map_count`); on Windows this means WSL2/Docker Desktop.
- **OQ-03:** Second model-family subscription for independent verification — yes/no.
- **OQ-04:** Which of the two product repos is the Day-2 pilot (Product A in DEC-043).
- **OQ-05:** Timeline for resuming the Rust kernel as `gov` replacement.
- **OQ-06:** Approve or amend AMD-01 … AMD-08 into Contract v3 (as new labelled requirement class, e.g. `SOLO_PROFILE_REFINEMENT`).

---

## 11. Evidence index (accessed 2026-09-28)

| Ref | Source |
|---|---|
| E-PRICE | https://benchlm.ai/claude/pricing-plans · https://mem0.ai/blog/anthropic-claude-pricing · https://claude.com/pricing |
| E-OSPEC-REL | https://github.com/Fission-AI/openspec/releases |
| E-OSPEC-CUST | https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md |
| E-CBM-PAPER | https://arxiv.org/abs/2603.27277 |
| E-CBM-ADR | https://github.com/DeusData/codebase-memory-mcp/issues/1190 |
| E-CBM-WATCH | https://github.com/DeusData/codebase-memory-mcp/pull/1045 |
| E-CBM-REL | https://github.com/DeusData/codebase-memory-mcp/releases |
| E-CBM-INC | https://github.com/DeusData/codebase-memory-mcp/issues/1172 |
| E-BR | https://github.com/Dicklesworthstone/beads_rust |
| E-BR-GUI | https://github.com/w3dev33/beads-task-issue-tracker |
| E-BEADS-USE | https://ianbull.com/posts/beads/ |
| E-SERENA | https://github.com/oraios/serena |
| E-SERENA-LSP | https://github.com/oraios/serena/issues/858 |
| E-VEC | https://github.com/NousResearch/hermes-agent/issues/844 |
| E-EMBED | https://d-central.tech/local-embedding-models/ |
| E-LOCAL | https://techfuelhq.com/articles/best-local-llm-coding-2026/ |
| E-DOCLING | https://github.com/api-evangelist/docling (project summary) |
| E-DOCLING-PIN | https://www.avonture.be/blog/docling/ |
| E-PDFCMP | https://www.danilchenko.dev/posts/markitdown-vs-docling-vs-marker/ |
| E-RF-REL | https://ragflow.io/docs/release_notes · https://github.com/infiniflow/ragflow |
| E-RF-API | https://ragflow.io/docs/http_api_reference |
| E-RF-PY | https://ragflow.io/docs/python_api_reference |
| E-RF-RAPTOR | https://github.com/infiniflow/ragflow/releases/tag/v0.25.6 |
| E-RF-MCP | https://ragflow.io/docs/launch_mcp_server |
| E-RF-REQ | https://github.com/infiniflow/ragflow · https://docs.clore.ai/guides/rag-and-vector-databases/ragflow |
| E-RF-ENGINE | RAGFlow README (doc engine switch section) |
| E-RF-ZERO | https://github.com/infiniflow/ragflow/issues/19366 · https://github.com/infiniflow/ragflow/pull/19589 |
| E-RF-GH | https://github.com/infiniflow/ragflow/pull/14062 |
| E-RF-SLIM | RAGFlow README (build without embedding models) |
| E-RF-HOST | https://elest.io/open-source/ragflow |
| E-GRAPHITI | https://github.com/Flo976/graphiti-mcp-ollama · https://github.com/klaviyo/graphiti_mcp |
| E-LIGHTRAG | https://www.turingpost.com/p/rag-tools |
| E-BMAD | https://dev.to/willtorber/spec-kit-vs-bmad-vs-openspec-choosing-an-sdd-framework-in-2026-d3j |
| E-RULESYNC | https://github.com/dyoshikawa/rulesync |
| E-COPIER | https://smarttldr.com/en/topic/python-copier-project-scaffolding/deep-dive |
| E-COPIER-SKIP | https://deepwiki.com/copier-org/copier/3.4-updating-projects |
| E-COPIER-DOCS | https://copier.readthedocs.io/en/stable/updating/ |
| E-SUPERPOWERS | https://blog.marcnuri.com/superpowers-claude-code-skills-framework · https://github.com/obra/superpowers |
| E-SP-MKT | https://github.com/anthropics/claude-plugins-official/pull/148 |
| E-HOOK-CC | https://code.claude.com/docs/en/hooks |
| E-HOOK-EVENTS | https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html |
| E-HOOK-CX | https://developers.openai.com/codex/hooks |
| E-OTEL | https://github.com/mrcrdg/claude-telemetry |
| E-LANGFUSE | https://github.com/langfuse/Claude-Observability-Plugin |

---

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.12 | 2026-09-30 | DEC-078 (scale probes, RAM correction, envelope), DEC-079 (GitHub remote), DEC-080 (retrieval completeness all in W1), DEC-081 (how S1 runs), DEC-082 (how S1-A runs); DEC-077 DONE. |
| 0.11 | 2026-09-30 | DEC-073 (operating model), DEC-074 (S0b2 decisions + owner answers Q1–Q15), DEC-075 (boundary without branch protection), DEC-076 (W1 adjustments), DEC-077 (deploy key). |
| 0.10 | 2026-09-29 | DEC-070 (S1-A fidelity audit + wave-exit audits), DEC-071 (S0b1 facts), DEC-072 (S0b2 scope). |
| 0.9 | 2026-09-29 | DEC-064 (full scope, three waves, one release), DEC-065 (master rules MR-1…MR-6), DEC-066 (organisation layer, five functions), DEC-067 (two-layer testing; Gate V returns as qualification), DEC-068 (S0b1/S0b2), DEC-069 (mechanical test independence). |
| 0.8 | 2026-09-29 | DEC-060 (one agnostic Gov OS, overlay per project), DEC-061 (workbench folder), DEC-062 (GitHub via gh, read-only token), DEC-063 (settings files). |
| 0.7 | 2026-09-29 | DEC-039 accepted (becomes ADR-0001); DEC-057 (S0 research first), DEC-058 (originals kept unchanged, successors Charter v5 and Contract v4, docs/source archived afterwards), DEC-059 (S1 stabilise deferred). |
| 0.6 | 2026-09-29 | DEC-056: restructure executed (facts). |
| 0.5 | 2026-09-29 | DEC-053 (owner answers Q1–Q10), DEC-054 (working-tree buckets, import-closure rule, move-only commit), DEC-055 (pre-restructure maintenance); DEC-049 closed by DEC-053 Q5. |
| 0.4 | 2026-09-28 | DEC-051 (same repo, archive = git history; supersedes DEC-048), DEC-052 (read-only inventory first); DEC-049 reopened pending inventory. |
| 0.3 | 2026-09-28 | DEC-048 (bundle-only archive, delete working copy; supersedes DEC-038), DEC-049 (originals out of repo; amends DEC-045), DEC-050 (workstation hygiene, WSL compaction). |
| 0.2 | 2026-09-28 | Added §4A (DEC-038…DEC-047) from the Rust repository review: archive-not-delete, threat model, no executed installs, default-deny path guards, evidence classes, products-first, loop budget, originals preserved, carried assets, new control panel. DEC-025 path guard clarified as allow-list. Date corrected. |
| 0.1 | 2026-09-26 (date recorded in error; actual 2026-09-28) | Initial register from design session: strategy, tool selection, RAGFlow deep evaluation, retrieval-completeness guidance, Solo Core profile, amendments. `bd` → `br` change recorded in DEC-013. |

---

## 13. S1 decisions (register v0.13, appended by S1 on branch `s1/spec`)

Entries above this line are register v0.12, copied verbatim. The entries below record the owner's answers to S1's
decision packages (round 1, asked 2026-09-30). They are the only changes to this file in S1.

### DEC-083 — PROPOSED decisions ratified for Charter v5 and Contract v4; DEC-040 amended (tool installs)
- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P1-A option (a) with one amendment
- **Accepted as written:** DEC-003, DEC-004, DEC-005 (readiness part as settled by DEC-085), DEC-006, DEC-010, DEC-011,
  DEC-012, DEC-014, DEC-015 (native LSP; Serena not adopted), DEC-022, DEC-023, DEC-025, DEC-026 (as settled by DEC-086),
  DEC-027, DEC-041, DEC-044, DEC-046, DEC-050, DEC-062.
- **Accepted as realised by later decisions:** DEC-007 as amended by DEC-075; DEC-016 and DEC-017 as realised by DEC-074
  R1; DEC-024 as amended by DEC-074 Q5; DEC-031…DEC-037 as realised by DEC-080 (DEC-035's numbers stay placeholders tuned
  from telemetry); DEC-042 amended: MR-3 test independence applies to every task, and the fresh independent-verifier
  review remains FULL-profile only.
- **Superseded:** DEC-002 (by DEC-058, DEC-064); DEC-043 (by DEC-064); DEC-045 (by DEC-058); DEC-047 (by DEC-058).
- **Deferred:** DEC-018 (local gpt-oss T1 model) to Wave 3 model routing.
- **DEC-001 and OQ-05:** "assemble first" stands; a Rust kernel replacing the `gov` internals is a non-goal for Release 1.
- **Closed:** OQ-02 (host is WSL2 Linux x86_64); OQ-03 (no second model-family subscription: Balanced stack, DEC-074 Q1);
  OQ-06 (Contract v4 replaces amendments to Contract v3; AMD-01…AMD-08 are carried as Contract v4 clauses).
- **DEC-040 amended (tool installs):** Installing a tool is the orchestrator's job when a task needs it, and never
  automatic. The orchestrator presents a decision package — tool, exact version, source and checksum, why it is needed,
  disk and RAM, uninstall command — and installs only after the owner's explicit approval in chat. Every install is
  recorded in the tool registry (version, sha256, install and uninstall commands, date, approving decision), and
  `gov doctor` checks the pins. Install commands are an `ask` permission for the orchestrator role only and are denied
  for every other role; `sudo` stays with the owner. No automated install classification or authority envelope is
  reintroduced (ADR-0001). This updates the CAP-25 LITE form (DEC-074 Q11).
- **Wave 1 KPI added:** the install approval prompt appears even when the harness runs in Auto mode.

### DEC-084 — MR-3 on the Gov OS's own Wave 1: bootstrap, then dogfood
- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P1-B option (a)
- **Decision:** The PreToolUse guard (G-01) and the post-command containment check (G-02) are the first implementation
  tickets on Wave 1's critical path. Until both pass their own acceptance tests, every implementer session runs with a
  harness settings deny rule on `tests/acceptance/**`, and the operator checks `git diff --name-only` against the
  ticket's `allowed_paths` at every ticket close. From then on every later Wave 1 ticket runs under the real guard and
  containment check. The Independent Test Designer is a fresh session per ticket batch that reads only Contract v4 and
  the tickets' KPIs and writes only `tests/acceptance/<ticket-id>/`.

### DEC-085 — Readiness: profile → required cells; no defaulted N/A; spines close at FULL
- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P1-C option (a) with one addition ·
  **Amends:** DEC-005 (readiness reduction)
- **Decision:** The mandatory set is ten rows of Framework §37: 1 intent/outcome, 2 user/actor, 4 scenarios, 5 inputs,
  6 data model/schema, 9 expected outputs, 16 security/privacy, 23 success criteria, 24 failure criteria, 25 independent
  acceptance tests. LITE requires the mandatory set. STANDARD requires the mandatory set plus the rows a fixed
  capability-type table in `readiness-dimensions.yaml` marks. FULL requires all 26. A row a profile does not require may
  stay MISSING without blocking. There is no defaulted N/A: every N/A is written by an agent as N/A_WITH_REASON, and the
  checker rejects an empty reason.
- **Addition:** a spine specification always closes at the FULL profile, whatever the profile of the change that
  opens it.

### DEC-086 — Governance share: definition and Wave 1 measurement
- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P2-D option (a) · **Settles:** DEC-004
  measurement, DEC-026 for Wave 1
- **Decision:** Governance tokens are the tokens of text the Gov OS injects or returns: instruction files, the
  SessionStart packet, hook output, `gov` output, governance MCP tool definitions, and checkpoint and close records,
  counted deterministically per ticket by the `gov` CLI. The denominator is the ticket's fresh input plus output tokens,
  read from the harness's local session logs by ccusage. Cache reads are reported separately and are not in the share.
- **ccusage** is installed and pinned by the orchestrator under DEC-083's install rule and is a Wave 1 prerequisite.

### DEC-087 — CI scope on the hosted runner
- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P2-E option (a) · **Refines:** DEC-075
- **Decision:** GitHub Actions (G4–G5, advisory) runs the deterministic checks only: schemas, `gov check` G0–G2,
  readiness, the decision checker, the ticket DAG, `openspec validate --strict`, gitleaks, rulesync drift, and tests that
  need no local models (lexical fallback; codebase-memory is a static binary). Tests that need local models run in the
  pre-push gate (G3) and produce an evidence record bound to the head commit; CI checks that it exists and matches the
  head commit. The carrier of that record (for example a git note or a commit) is left to the CI ticket's design.

| Version | Date | Change |
|---|---|---|
| 0.13 | 2026-09-30 | S1 round 1: DEC-083 (ratification; DEC-040 amended), DEC-084 (MR-3 bootstrap), DEC-085 (readiness profiles; spines at FULL), DEC-086 (governance share), DEC-087 (CI scope). |

## 14. S1-A round-1 decisions (register v0.14, appended by S1 on branch `s1/spec`)

The owner's answers to the S1-A round-1 decision packages DP-1…DP-8 (`~/gov-os-workbench/s1a/DECISION_PACKAGES.md`;
round-1 files fingerprinted in `~/gov-os-workbench/s1a-round1.sha256`).

### DEC-088 — MR-4: what triggers an independent audit
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-1 (owner's own option) · **Implements:** MR-4, DEC-070
- **Decision:** A fresh, independent audit runs when a spine specification closes, when a STANDARD or FULL feature
  specification closes, when an accepted CIT-E changes a closed spine specification, and at every wave and release
  exit. LITE feature specifications are audited at the wave exit. Contested and owner-level findings reach the owner in
  chat as decision packages; agreed fixes become tickets.

### DEC-089 — MR-2 holds from Wave 1: every required open readiness cell has a linked gap ticket
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-2 option (a)
- **Decision:** In Wave 1 the planning skill creates one linked ticket (class discovery, data, research or test-design)
  per required open cell, and `gov check` fails a specification with an unlinked required open cell. Wave 2 automates
  the generation with `gov readiness --generate`.

### DEC-090 — The adoption transaction A0–A11 in Contract v4
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-3 option (b) · **Refines:** DEC-006
- **Decision:** CAP-44 states A0–A11 with one evidence record per stage and the three final verdicts
  (ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS, NOT_ADOPTED_HEALTHY). Wave 1 (`gov adopt --lite`) delivers A0–A4,
  A6 and A8 with a safety baseline and a rollback point per batch, **and A5**: an independent review of the path map
  before any move, by the Wave 1 Independent Auditor role. The independent gates A7, A10 and A11 are Wave 3 with CAP-47;
  the verdict is issued from Wave 3.

### DEC-091 — Hierarchical (parent-child) retrieval in Wave 1
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-4 option (a) · **Consistent with:** DEC-080
- **Decision:** Chunk records carry `parent_id` (section level for documents, function/module level for code), and
  `gov retrieve` expands a child hit to its parent within the bundle budget and names the expansion. Both are Wave 1.

### DEC-092 — One acceptance check per capability, plus a `covers` list
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-5 option (a) · **Refines:** DEC-058
- **Decision:** Each Contract v4 capability keeps one observable acceptance check and adds a `covers` list naming every
  carried sub-requirement with its source reference and wave. Wave-exit audits check each covered item. Nothing is
  dropped by the compression.

### DEC-093 — Decision packages: at most five at a time; P1 may bypass the cap
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-6 option (a) with an addition
- **Decision:** Decision packages are ranked P1–P3 and asked at most five at a time. A P1 package may bypass the cap.

### DEC-094 — Test execution and integration are distinct roles, added in Wave 2
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-7 option (b) · **Amends:** DEC-066 (Wave 2 roster)
- **Decision:** MR-5's "test execution" and "integration" roles are distinct role definitions in Wave 2, alongside
  integration/API.

### DEC-095 — DEC-040 status
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-8 option (a)
- **Decision:** DEC-040 is ACCEPTED as amended by DEC-083. Its v0.12 text above stays verbatim; this entry is the status
  change.

| Version | Date | Change |
|---|---|---|
| 0.14 | 2026-10-01 | S1-A round 1: DEC-088 (audit triggers), DEC-089 (gap tickets in W1), DEC-090 (A0–A11), DEC-091 (parent-child retrieval W1), DEC-092 (covers lists), DEC-093 (five-package cap, P1 bypass), DEC-094 (test execution, integration roles W2), DEC-095 (DEC-040: ACCEPTED as amended by DEC-083). |

### DEC-096 — Loop policy: iterate to convergence; escalate after three consecutive non-converging iterations
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER · **Amends:** DEC-044, DEC-070, DEC-082
- **Decision:** Any iterative loop that runs until convergence (review→repair, audit→repair, test→fix, verification)
  continues until it converges, or until three consecutive iterations fail to converge. The third consecutive failure
  produces an escalation package for the owner: each iteration's outcome, why it is not converging, and the options
  (fix differently, narrow, split, defer, delete, or continue). The owner decides. The iteration count and budget are
  held by the orchestrator or `gov`, and are never disclosed to the sessions inside the loop.
- **Unchanged:** the retrieval stopping rules (DEC-034, DEC-080).

| Version | Date | Change |
|---|---|---|
| 0.14 (cont.) | 2026-10-01 | DEC-096 (loop policy; amends DEC-044, DEC-070, DEC-082). |

## 15. Wave 1 build decisions (register v0.15, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers to the W1-01 KPI disputes KD-1…KD-4, raised by the Independent Test Designer on ticket `DAEO-dtv3`
(recorded in `tests/acceptance/W1-01/README.md`, commit `71100b5`). They settle how W1-01's KPI lines are read; the
ticket's KPI text is unchanged.

### DEC-097 — W1-01 KD-1: git history is the record that the operator diff procedure was used
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-01 KPI dispute KD-1 (accept) · **Implements:** DEC-084
- **Decision:** For W1-01's KPI "the operator diff procedure … is written and used from the first implementation
  ticket", the record that the procedure was used is git history, through `Task:` trailers: until W1-05 lands, a commit
  with a `Task:` trailer stays inside that ticket's `allowed_paths`.
- **Known limit:** a commit without a `Task:` trailer is not checked.

### DEC-098 — W1-01 KD-2: which session settings the interim install rule lists
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-01 KPI dispute KD-2 (accept) · **Implements:** DEC-083
- **Decision:** For "install commands are denied in every session settings file", `governance/project/bootstrap.md`
  lists every agent session folder (`w1-build`, `w1-tests`, `s1`, `s1a`) and the repository's own settings. The
  operator console is not listed; it acts as the owner.

### DEC-099 — W1-01 KD-3: what the interim install rule denies until W1-05
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-01 KPI dispute KD-3 (accept) · **Implements:** DEC-083
- **Decision:** Until W1-05, the interim install rule denies `curl` or `wget` piped to a shell, `sudo`, and package
  managers. Shell aliases and functions are left to W1-03's containment check.

### DEC-100 — W1-01 KD-4: one dated denied attempt per class in `bootstrap.md`
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-01 KPI dispute KD-4 (accept)
- **Decision:** For "verified by one denied attempt each", `governance/project/bootstrap.md` records one dated denied
  attempt per class.

| Version | Date | Change |
|---|---|---|
| 0.15 | 2026-10-01 | W1-01 KPI disputes: DEC-097 (KD-1, diff procedure shown by `Task:` trailers), DEC-098 (KD-2, session list), DEC-099 (KD-3, interim install denials), DEC-100 (KD-4, dated denied attempts). |

## 16. Wave 1 build decisions, round 2 (register v0.16, appended by W1-BUILD on branch `w1/integrate`)

The owner's answer to W1-BUILD decision package DP-1 (asked 2026-10-01 at the W1-01 bootstrap diff check), and five
owner decisions given to W1-BUILD in chat on 2026-10-01 without a package. From this section on, a commit that records
owner decisions touches only `docs/DECISION_REGISTER.md` and `governance/project/bootstrap.md`, and carries the trailer
`Task: decision-record` (owner rule, 2026-10-01). Commit `0aa1428` (DEC-097…DEC-100) predates the rule and is accepted
as it is.

### DEC-101 — Secret-file deny rules in the session-folder settings; `s1` and `s1a` retired
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-BUILD DP-1 option (b) · **Refines:** DEC-098
- **Decision:** The owner has added Read and Edit deny rules for `.env*`, `*.pem`, `*.key` and `config/secrets*` to the
  `w1-build` and `w1-tests` session settings, and has retired the `s1` and `s1a` session folders. The install forms
  those two files did not name are closed by the retirement.
- **Record:** the session table in `governance/project/bootstrap.md`. The `w1-build` rules were read by the
  orchestrator on 2026-10-01; the `w1-tests` file is not readable from the build session and is recorded as the owner
  states it.

### DEC-102 — Experiments are part of discovery
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package)
- **Decision:** Research and experiment tasks (spikes, and tool compatibility and performance trials like S0a and
  S0b2) are a normal part of discovery and can run at any point in development. They run in sandboxes outside
  production paths and produce an evidence record: what was tested, how, the results and a verdict. Their code is never
  promoted except through the normal cycle. Their results change a closed specification only through CIT-P.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

### DEC-103 — The order of specification work
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package)
- **Decision:** Specification work runs in this order: discovery and research, then scenarios, then representative
  data, then UX for any feature with a user interface, then acceptance tests, then implementation. The owner reviews
  scenarios and UX designs, not test code.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

### DEC-104 — UX before build, with visual testing
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package)
- **Decision:** For a feature with a user interface, the UX readiness dimension closes only with scenario-derived
  wireframes or mockups the owner has approved. Its acceptance tests include visual checks against those designs
  (screenshot comparison and scenario walk-throughs). The UX role (Wave 2) owns this; visual-testing tools are
  installed under DEC-083 when first needed.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

### DEC-105 — Evidence-triggered change
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package)
- **Decision:** When an experiment or finding contradicts a closed specification, a CIT-P opens. The impact assessment
  shows the affected specifications, decisions, tickets, tests and code, with three options and the cost of each: apply
  now; defer (record it and continue); or re-baseline (reopen the affected specification, re-plan from it, and retire
  the work it invalidates). The owner chooses; CIT-E records what was done. A closed specification means "ready to
  build", not "frozen", and every version is kept.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

### DEC-106 — Wave 1 learning metrics
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package) · **Extends:** DEC-086
- **Decision:** Per ticket, measure: KPI disputes raised by the test designer; acceptance tests rewritten after
  implementation began, with the reason; and governance share. Report all three at the Wave 1 exit. Only governance
  share has a threshold (≤ 15%, DEC-086). The other two show whether specifications are being locked too early or are
  too vague.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

| Version | Date | Change |
|---|---|---|
| 0.16 | 2026-10-01 | W1-BUILD DP-1: DEC-101 (secret-file deny rules in `w1-build` and `w1-tests`; `s1`, `s1a` retired). Owner decisions: DEC-102 (experiments are part of discovery), DEC-103 (order of specification work), DEC-104 (UX before build, visual testing), DEC-105 (evidence-triggered change), DEC-106 (Wave 1 learning metrics). |

## 17. Wave 1 build decisions, round 3 (register v0.17, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers of 2026-10-01 to the W1-02 KPI disputes KD-1…KD-7, raised by the Independent Test Designer on
ticket `DAEO-emkd` (recorded in `tests/acceptance/W1-02/README.md`, commits `5d65ba7` and `43fdf41`), and the owner's
defaults for the edge cases that README lists as left open (KD-8). They settle how W1-02's KPI lines are read; the
ticket's KPI text is unchanged. The acceptance tests at `43fdf41` cover KD-1…KD-5 and take no side on KD-6…KD-8.

### DEC-107 — W1-02 KD-1: how a session declares its role and ticket; the stricter of session and subagent applies
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-1 · **Implements:** CAP-58.a, CAP-58.c
- **Decision:** A session declares its role and its active ticket through the environment variables `GOV_ROLE` and
  `GOV_TICKET`, set at session start. Inside a subagent, the hook input's `agent_type` identifies the subagent's role,
  and the guard applies the stricter of the session's role and the subagent's. A missing or unknown role means
  read-only.
- **Evidence:** the test designer verified that in this harness (Claude Code 2.1.286) the hook input inside a subagent
  carries `agent_id` and `agent_type`.
- **Follow-up:** W1-05's switch-over report confirms this on the live guard.

### DEC-108 — W1-02 KD-2: the kernel scratch set
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-2 · **Implements:** CAP-58.a
- **Decision:** The kernel scratch set is `.gov-runtime/scratch/**` plus the directory returned by
  `tempfile.gettempdir()`.

### DEC-109 — W1-02 KD-3: the freeze flag until `gov pause` exists
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-3
- **Decision:** Until `gov pause` exists, the freeze flag is the file `.gov-runtime/freeze`.

### DEC-110 — W1-02 KD-4: the guard fails closed
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-4 · **Refines:** DEC-025
- **Decision:** The guard catches every internal error, exits with code 2 and appends one line to
  `.gov-runtime/findings.jsonl`.
- **Why exit code 2:** exit code 1 and timeouts don't block in Claude Code. W1-03 covers the timeout case.

### DEC-111 — W1-02 KD-5: which Bash forms the guard judges
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-5
- **Decision:** The guard judges plain Bash forms. All other forms stay with W1-03.

### DEC-112 — W1-02 KD-6: the auditor's one write path
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-6
- **Decision:** The auditor is read-only everywhere except the report path its own ticket allows (for example
  `docs/audit/wave-1/**`).

### DEC-113 — W1-02 KD-7: a subagent whose type is not a defined role is read-only
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-7 · **Implements:** CAP-58.c
- **Decision:** A subagent whose `agent_type` is not a defined role is read-only.
- **Consequence for W1-05:** the role definitions (W1-33) land after the switch-over, so W1-05 must ensure the Wave 1
  roles (orchestrator, engineer, product-spec, independent test designer, independent auditor) exist as subagent types
  when the guard goes live. If that needs a change to W1-05's or W1-33's KPIs, the orchestrator raises a decision
  package before implementing W1-05.

### DEC-114 — W1-02 KD-8: owner defaults for the open edge cases
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, defaults for the cases `tests/acceptance/W1-02/README.md` leaves open
- **Decision:**
  - `GOV_TICKET` accepts both the ticket id and the W1 id.
  - Writes require the ticket to be claimed.
  - A test designer with no ticket is read-only.
  - A repository located inside the temp dir gets no temp-dir allowance.
  - Redirects to `/dev/null` are allowed.

| Version | Date | Change |
|---|---|---|
| 0.17 | 2026-10-01 | W1-02 KPI disputes: DEC-107 (KD-1, `GOV_ROLE` and `GOV_TICKET`; stricter of session and subagent role), DEC-108 (KD-2, scratch set), DEC-109 (KD-3, freeze flag), DEC-110 (KD-4, fail-closed with exit code 2 and a finding), DEC-111 (KD-5, plain Bash forms), DEC-112 (KD-6, auditor report path), DEC-113 (KD-7, non-role subagent is read-only; W1-05 consequence), DEC-114 (KD-8, edge-case defaults). |

## 18. Wave 1 build decisions, round 4 (register v0.18, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers of 2026-10-01 to the points W1-BUILD reported at the W1-02 bootstrap diff check (commit `7d9ab30`;
the owner gave `DIFF OK`): one known limit of the guard, three readings of DEC-114, and three points on the W1-05
switch-over. W1-02 (`DAEO-emkd`) is reopened as a repair for DEC-115 and DEC-117; its acceptance tests are revised
first. The KPI text of W1-02 is unchanged. W1-05's ticket changes under DEC-119 only.

### DEC-115 — The guard resolves a Bash write target before judging it
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the known limit reported at the W1-02 diff check · **Refines:** DEC-111
- **Decision:** Before judging a Bash write target, the guard expands `~`, `~user` and environment variables from the
  hook's own environment. Any target it still can't resolve (command substitution, an unset or unknown variable, a glob
  it can't expand) is denied. W1-03 stays the second line.

### DEC-116 — Three readings of DEC-114 confirmed
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the readings reported at the W1-02 diff check · **Refines:** DEC-114
- **Decision:**
  - "Claimed" means `status: in_progress`.
  - A test designer without a claimed ticket has no write, scratch included.
  - `/dev/null` is the only device target that isn't a write, for any session, also when frozen.

### DEC-117 — Amendment of DEC-107: inside a role subagent, the subagent's role governs
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER (owner correction) · **Amends:** DEC-107
- **Decision:** Inside a subagent with a defined role, that subagent's role governs its tool calls. The session's role
  governs the main thread only. There is no "stricter of the two". A subagent whose type isn't a defined role stays
  read-only (DEC-113).
- The rest of DEC-107 stands. Its text above stays as written; this entry is the amendment.

### DEC-118 — Project root: from the switch-over, every Gov OS session starts in the repository root
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the W1-05 points reported at the W1-02 diff check
- **Decision:** From the switch-over, every Gov OS session starts in the repository root, so `CLAUDE_PROJECT_DIR` is
  the repository. A write target outside the project directory is denied unless it's in the scratch set. The `w1-build`
  and `w1-tests` folders end with the bootstrap.

### DEC-119 — W1-05 delivers minimal subagent definitions for the five Wave 1 roles
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the W1-05 points reported at the W1-02 diff check · **Implements:** DEC-113
- **Decision:** W1-05 delivers minimal subagent definitions for the five Wave 1 roles (orchestrator, engineer,
  product-spec, independent-test-designer, independent-auditor) under `.claude/agents/`. W1-33 later replaces them with
  full definitions.
- **Ticket change:** under this decision the orchestrator updates W1-05's ticket (`DAEO-m7u4`): `.claude/agents/**` is
  added to its `allowed_paths`, with one KPI line per role definition. That is a separate commit with the trailers
  `Task: DAEO-m7u4` and `Implements: DEC-119`.
- **For the post-bootstrap spec change (provider change):** Contract v4 names W1-33 as the only provider of CAP-22.a
  (roles as subagent definitions). W1-05 now provides the minimal definitions first. Until the Contract names W1-05,
  the new KPI lines of W1-05 cite no covers id, and the W1-05 row of `docs/plan/WAVE_1_WBS.md` is unchanged.

| Version | Date | Change |
|---|---|---|
| 0.18 | 2026-10-01 | Owner answers at the W1-02 diff check: DEC-115 (Bash target resolution; unresolvable targets denied), DEC-116 (three readings of DEC-114 confirmed), DEC-117 (amends DEC-107: the subagent's role governs inside a role subagent), DEC-118 (sessions start in the repository root from the switch-over), DEC-119 (W1-05 delivers minimal role subagent definitions; provider change noted for the spec change). |

## 19. Wave 1 build decisions, round 5 (register v0.19, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers of 2026-10-01 to KPI disputes raised by the Independent Test Designer on three tickets:

- W1-04 (`DAEO-78bn`), KD-1 and KD-2. The package is with the test designer and is not readable from the build
  session; W1-04 has no acceptance tests yet.
- W1-03 (`DAEO-8qvp`), KD-1…KD-3, recorded in `tests/acceptance/W1-03/README.md` (commit `a389ebc`).
- W1-02 (`DAEO-emkd`), KD-9, recorded in `tests/acceptance/W1-02/README.md` (commit `a4e6691`). W1-BUILD asked the same
  question as DP-2.

The KPI text of the three tickets is unchanged. W1-04's `allowed_paths` change under DEC-120 only.

### DEC-120 — W1-04 KD-1: the install rule reaches the harness through the PreToolUse guard
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-04 KPI dispute KD-1 · **Implements:** DEC-083
- **Decision:** The install rule reaches the harness through the PreToolUse guard. For a Bash call it classifies as an
  install, the guard returns the permission decision `ask` when the acting role is orchestrator, and `deny` for every
  other role, and for no role. The classifier only ever escalates: a match never allows something the harness would
  otherwise ask about (DEC-083). Settings rules for install commands remain as a second line.
- **Ticket change:** under this decision the orchestrator extends W1-04's `allowed_paths` to the guard's install module
  and the hook entry it uses, in a separate commit with the trailers `Task: DAEO-78bn` and `Implements: DEC-120`.
- **Verification:** the Auto-mode KPI is verified by driving the hook, and by one live headless attempt.

### DEC-121 — W1-04 KD-2: the tool-registry schema
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-04 KPI dispute KD-2
- **Decision:** The test designer's recommended registry schema is accepted. If the test designer proposed none: one
  file, `governance/project/tool-registry.yaml`, listing entries with `id`, `version`, `source`, `sha256`,
  `install_command`, `uninstall_command`, `installed_at` and `decision` (the approving DEC), validated by a JSON Schema
  in `schemas/`.
- Which of the two applies is shown by W1-04's acceptance tests; the build session cannot read the package.

### DEC-122 — W1-03 KD-1: the containment finding record
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-03 KPI dispute KD-1 · **Extends:** DEC-110
- **Decision:** A containment finding is one JSON line in `.gov-runtime/findings.jsonl`, the same file as guard
  failures, with: `time`, `session_id`, `agent_type`, `role`, `ticket`, `tool`, `command`, `paths`, `action`
  (`reverted` or `flagged`) and `reason`.

### DEC-123 — W1-03 KD-2: the nine I-06 forms are tested by their effect; one accepted residual
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-03 KPI dispute KD-2 · **Under:** ADR-0001
- **Decision:** All nine I-06 forms are tested by their effect inside the repository. A write outside the repository
  through an opaque form (for example `perl -e` or `$(…)`) is seen by neither the guard nor the containment check.
  That is an accepted residual under ADR-0001.
- **Record:** `governance/project/bootstrap.md`, section "Accepted residual".

### DEC-124 — W1-03 KD-3: containment acts only on changes made by the current call
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-03 KPI dispute KD-3
- **Decision:** Containment acts only on changes made by the current call. It snapshots the changed-path set before the
  call (PreToolUse) and compares it after (PostToolUse). Paths already changed before the call are never touched. When
  attribution is uncertain, it flags and doesn't revert.

### DEC-125 — W1-02 KD-9: a role subagent's role applies only in a session with a declared role
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-9 and W1-BUILD DP-2 option (a) · **Refines:** DEC-117
- **Decision:** A role subagent's own role applies only when the session itself has a declared role. In a session with
  no role, everything, subagents included, is read-only.

| Version | Date | Change |
|---|---|---|
| 0.19 | 2026-10-01 | KPI disputes: DEC-120 (W1-04 KD-1, install rule through the PreToolUse guard; `ask` for the orchestrator, `deny` otherwise), DEC-121 (W1-04 KD-2, tool-registry schema), DEC-122 (W1-03 KD-1, containment finding record), DEC-123 (W1-03 KD-2, nine I-06 forms by effect; residual outside the repository accepted), DEC-124 (W1-03 KD-3, only the current call's changes), DEC-125 (W1-02 KD-9, role subagent only in a session with a declared role). |

## 20. Wave 1 build decisions, round 6 (register v0.20, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers to W1-BUILD decision packages DP-3 and DP-4 and to the known limit reported at the bootstrap diff
check of the W1-02 repair (commit `cd23357`; the owner gave `DIFF OK` for `7d9ab30..cd23357`). No KPI text changes.
W1-03's `allowed_paths` change under DEC-126 only.

### DEC-126 — W1-03 may change the PreToolUse hook entry
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-BUILD DP-3 option (a) · **Implements:** DEC-124
- **Decision:** `template/governance/kernel/hooks/pretooluse*` is added to W1-03's `allowed_paths`, so containment can
  take its before-snapshot in PreToolUse (DEC-124). W1-02's acceptance tests must still pass after W1-03's change.
- **Ticket change:** the orchestrator commits it separately, with the trailers `Task: DAEO-8qvp` and
  `Implements: DEC-126`.

### DEC-127 — Where the tool-registry schema and the registry live
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-BUILD DP-4 option (a) · **Amends:** DEC-121 (its fallback)
- **Decision:** The registry schema stays in the kernel template at the path W1-04's ticket names
  (`template/governance/kernel/schemas/tool-registry*`). The registry itself is per-repository project data at
  `governance/project/tool-registry.yaml`. W1-04 ships no registry file; W1-06 creates it at the first install.

### DEC-128 — The guard's quoting limit is an accepted residual
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the known limit reported at the W1-02 repair diff check · **Refines:** DEC-115
- **Decision:** In a Bash write target, a single-quoted or escaped `$NAME` is expanded by the guard although the shell
  keeps it literal. That is accepted as a residual.
- **Record:** `governance/project/bootstrap.md`, section "Accepted residual".

| Version | Date | Change |
|---|---|---|
| 0.20 | 2026-10-01 | W1-BUILD DP-3: DEC-126 (W1-03 may change the PreToolUse hook entry). DP-4: DEC-127 (schema in the kernel template, registry at `governance/project/tool-registry.yaml`, created by W1-06; amends DEC-121). DEC-128 (quoted or escaped `$NAME` in a target: accepted residual). |

## 21. Wave 1 build decisions, round 7 (register v0.21, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers on a call that moves `HEAD`, to the Independent Test Designer's KPI dispute KD-4 on W1-03
(`DAEO-8qvp`) and to the readings and open cases recorded in `tests/acceptance/W1-03/README.md` (commits `5aeb62a` and
`e31e11d`). That README dates the answer to KD-4 2026-10-02; the status date below is the one the owner gave. The
KPI text of W1-03 is unchanged.

### DEC-129 — W1-03 KD-4: containment also snapshots `HEAD`
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-03 KPI dispute KD-4 · **Extends:** DEC-124
- **Decision:** Containment also snapshots `HEAD` before the call. A forward move on the same branch has its new
  commits' paths checked against the allowed paths, with anything outside flagged. Any other `HEAD` move (reset,
  checkout of another branch, rebase, amend) is flagged and never reverted.

### DEC-130 — The test designer's readings of DEC-124 confirmed
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the readings in `tests/acceptance/W1-03/README.md` · **Refines:** DEC-124
- **Decision:** No before-snapshot or overlapping calls means flag and never revert. A path changed before the call is
  never restored. Uncommitted work discarded by `git reset --hard` is reported.

### DEC-131 — The test designer's readings of KD-4 confirmed
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the readings in `tests/acceptance/W1-03/README.md` · **Refines:** DEC-129
- **Decision:** Any other `HEAD` move is flagged whoever makes it, even when it only undoes the caller's own in-scope
  commit. A `git commit -a` that sweeps up another role's uncommitted work is flagged for those paths.

### DEC-132 — Owner defaults for the open `HEAD` cases
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, defaults for the cases `tests/acceptance/W1-03/README.md` leaves open · **Refines:** DEC-129
- **Decision:**
  - Checking out a branch that points at the same commit isn't a `HEAD` move.
  - Creating a new branch and committing on it in one call is flagged.
  - A merge that isn't a fast-forward is flagged.
  - A `HEAD` move with no before-snapshot is flagged.
- **Tests:** these four are covered by builder tests until the test designer adds acceptance tests.

| Version | Date | Change |
|---|---|---|
| 0.21 | 2026-10-01 | W1-03 and `HEAD`: DEC-129 (KD-4, `HEAD` in the before-snapshot; forward commits checked, any other move flagged and never reverted), DEC-130 (readings of DEC-124 confirmed), DEC-131 (readings of KD-4 confirmed), DEC-132 (defaults for four open `HEAD` cases; builder tests until acceptance tests exist). |

## 22. Wave 1 build decisions, round 8 (register v0.22, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers at the bootstrap diff check of W1-03 (commit `7143034`; the owner gave `DIFF OK`): the answer to
W1-BUILD decision package DP-5, the known limits W1-BUILD reported, and four working rules. DEC-136, DEC-137 and
DEC-138 will be carried into Contract v4 by the post-bootstrap spec change; the orchestrator changes neither the
Contract nor any ticket for them now.

### DEC-133 — The orchestrator claims a ticket before its test design
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-BUILD DP-5 option (a) · **Refines:** DEC-114, DEC-116
- **Decision:** The orchestrator claims a ticket (`tk start`) before sending its `TEST_DESIGN_REQUEST`; claim and test
  design swap order in the loop. Engineer writes on a claimed ticket remain subject to the READY rule: no
  implementation before its acceptance tests exist (enforced from W1-09).

### DEC-134 — W1-03's four known limits are accepted residuals
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the known limits reported at the W1-03 diff check
- **Decision:** These are accepted residuals of the containment check:
  - an unseen change during a Bash call is attributed to that call;
  - a `HEAD` move with no snapshot is checked only against the last `HEAD` seen;
  - while frozen, an acceptance test changed through an opaque form is restored whoever changed it;
  - the snapshot adds about 28 ms per Bash call.
- **Record:** `governance/project/bootstrap.md`, section "Accepted residual".

### DEC-135 — Proportion rule for enforcement code
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER (Charter principle 9)
- **Decision:** In guard and containment work, fix every probe finding that could lose work or let an implementer
  change acceptance tests. Record every other edge case as a residual in `governance/project/bootstrap.md` instead of
  adding code. Report the ticket's actual LOC against its estimate when closing it.

### DEC-136 — Probe findings feed the independent suite
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER · **Refines:** DEC-069
- **Decision:** When the orchestrator's review finds a case the acceptance tests miss, it passes the case to the next
  test design batch as a described behaviour, never as code. The test designer decides from the specification whether
  it becomes an acceptance test, and reports when a finding reveals a specification gap. Builder tests stay regression
  evidence only.
- **First use:** the twelve cases of the W1-03 review go, described as behaviours, into the orchestrator's next
  `TEST_DESIGN_REQUEST`.
- To be carried into Contract v4 by the post-bootstrap spec change.

### DEC-137 — Independent post-green probe for FULL tickets
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER
- **Decision:** For a FULL-profile ticket, the adversarial probe after the acceptance tests go green is done by a fresh
  reviewer subagent, not by the engineer who wrote the code. The orchestrator commissions and judges the probe; the
  reviewer writes nothing to the repository.
- To be carried into Contract v4 by the post-bootstrap spec change.

### DEC-138 — Sandbox spike after the bootstrap
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER · **Under:** DEC-102
- **Decision:** Right after `SWITCH_OVER_READY`, an experiment tests Claude Code's sandbox on this WSL2 machine:
  - whether it blocks writes outside the repository through opaque Bash forms;
  - whether it can hide the qualification oracle;
  - whether per-role headless sessions can each get their own write scope;
  - what it costs in tokens and time.

  The result decides whether Wave 1 adds the sandbox as the outer layer under the guard. The owner launches the spike;
  the orchestrator does not start it.
- To be carried into Contract v4 by the post-bootstrap spec change.

| Version | Date | Change |
|---|---|---|
| 0.22 | 2026-10-01 | Owner answers at the W1-03 diff check: DEC-133 (DP-5: claim before test design), DEC-134 (four W1-03 residuals accepted), DEC-135 (proportion rule for enforcement code; LOC against estimate at close), DEC-136 (probe findings go to the test designer as described behaviours), DEC-137 (independent post-green probe for FULL tickets), DEC-138 (sandbox spike after the bootstrap, launched by the owner). |

## 23. Wave 1 build decisions, round 9 (register v0.23, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers at the bootstrap diff check of W1-04 (commit `48ccac7`; the owner gave `DIFF OK` for
`7143034..5e14561`), given together with the test designer's acceptance tests for the review's probe findings
(commits `e10a3b3` for W1-03 and `17ef3ae` for W1-04). KD-5 and KD-6 are KPI disputes of the Independent Test Designer
on W1-03 (`DAEO-8qvp`); their package is with the test designer and is not readable from the build session. No KPI
text changes.

### DEC-139 — While frozen, an install is denied to every role
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the reading reported at the W1-04 diff check · **Refines:** DEC-109, DEC-120
- **Decision:** `pip install` is denied while frozen. While frozen, an install by any role, the orchestrator included,
  is denied. Only the owner acts while frozen.

### DEC-140 — Residual entries in `bootstrap.md` use the trailer `Task: decision-record`
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the question at the W1-04 diff check · **Refines:** DEC-135
- **Decision:** A commit that records residuals in `governance/project/bootstrap.md` carries the trailer
  `Task: decision-record`.

### DEC-141 — Sandbox prerequisites installed by the owner
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER (record of an owner action) · **For:** DEC-138
- **Record:** For the sandbox spike, the owner installed bubblewrap 0.9.0 and socat 1.8.0.0 with `sudo apt-get`. The
  `bwrap` smoke test printed OK. This is an owner install; it goes into the tool registry when W1-06 creates it.
- The orchestrator does not start the spike.

### DEC-142 — W1-03 KD-5: a snapshot of a call that is known to be over no longer blocks restoration
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-03 KPI dispute KD-5 (fix it; proportion rule, DEC-135) · **Refines:** DEC-124, DEC-130
- **Decision:** A snapshot of another actor's call that never ended (for example, a declined prompt) no longer blocks
  restoration once that call is known to be over: its session has issued a later tool call, or the hook timeout has
  passed. Restoration still requires certain attribution; otherwise flag.

### DEC-143 — W1-03 KD-6: an acceptance test changed in a call that also moves `HEAD` is restored from the pre-call `HEAD`
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-03 KPI dispute KD-6 (fix it; proportion rule, DEC-135) · **Refines:** DEC-129
- **Decision:** When a non-designer changes an acceptance test in the same call as a non-forward `HEAD` move, the test
  is restored from the pre-call `HEAD` recorded in the snapshot, when attribution is certain. The `HEAD` move itself
  is still flagged and never reverted.

| Version | Date | Change |
|---|---|---|
| 0.23 | 2026-10-01 | Owner answers at the W1-04 diff check: DEC-139 (an install is denied to every role while frozen), DEC-140 (residual commits use `Task: decision-record`), DEC-141 (owner install of bubblewrap 0.9.0 and socat 1.8.0.0 for the sandbox spike), DEC-142 (W1-03 KD-5: a snapshot of a call known to be over no longer blocks restoration), DEC-143 (W1-03 KD-6: restore from the pre-call `HEAD` after a non-forward move). |

## 24. Wave 1 build decisions, round 10 (register v0.24, appended by W1-BUILD on branch `w1/integrate`)

The owner's answers given with `DIFF OK` for `5e14561..fd9972d` and with the test designer's acceptance tests for the
W1-03 repair (commit `95df6c5`): the answer to W1-BUILD decision package DP-6, one more KPI dispute on W1-03
(`DAEO-8qvp`, KD-7), a reading of DEC-142, and two working rules. No KPI text changes.

### DEC-144 — When another actor's unfinished call is known to be over
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-BUILD DP-6 option (a) · **Refines:** DEC-142
- **Decision:** In DEC-142, "call known to be over" means either the same actor's session has issued a later tool
  call, or ten minutes have passed.
- **Accepted residual:** background commands keep running after their call returns, so their later writes may be
  attributed to whichever call is active then. Recorded in `governance/project/bootstrap.md`.

### DEC-145 — W1-03 KD-7: the ten minutes is a named, overridable constant
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-03 KPI dispute KD-7 · **Refines:** DEC-144
- **Decision:** The ten minutes is a named constant, `PENDING_SNAPSHOT_TIMEOUT_S = 600`, in the containment module,
  overridable by the environment variable `GOV_PENDING_SNAPSHOT_TIMEOUT_S`.

### DEC-146 — "Its session" in DEC-142 means the same actor
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the test designer's reading in `tests/acceptance/W1-03/README.md` · **Refines:** DEC-142
- **Decision:** "Its session" means the same actor (session and agent id). Another actor's later call doesn't clear a
  snapshot.

### DEC-147 — The install rule's two misses and two false asks stay residuals; the sandbox spike tests installs
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on the residuals reported at the W1-04 repair diff check · **Under:** DEC-135 · **Extends:** DEC-138
- **Decision:** The two install misses (`python3 -u -m pip …`, `uv --directory … pip …`) and the two harmless false
  asks stay as residuals. The sandbox spike (DEC-138) must test whether the sandbox blocks installs, meaning writes
  outside the repository, whatever the command form.

### DEC-148 — How a ticket is reopened for a repair
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER · **Refines:** DEC-133
- **Decision:** Repairs follow W1-03's pattern: reopening sets the status to `in_progress` and claims the ticket, and
  closing sets it back to `closed`. W1-04's repair kept its status unchanged in history; no fix is needed, and the
  pattern holds from here on.

| Version | Date | Change |
|---|---|---|
| 0.24 | 2026-10-01 | W1-BUILD DP-6: DEC-144 (a call is known to be over after the same actor's later tool call or ten minutes; background commands are an accepted residual). DEC-145 (W1-03 KD-7: `PENDING_SNAPSHOT_TIMEOUT_S = 600`, overridable by `GOV_PENDING_SNAPSHOT_TIMEOUT_S`). DEC-146 ("its session" is the same actor). DEC-147 (install-rule residuals stay; the sandbox spike tests installs). DEC-148 (a repair reopens to `in_progress` and closes to `closed`). |

## 25. Wave 1 build decisions, round 11 (register v0.25, appended by W1-BUILD on branch `w1/integrate`)

The owner's answer to the Independent Test Designer's KPI dispute KD-1 on W1-05 (`DAEO-m7u4`), given with the revised
acceptance tests of W1-05 (commit `2b2944a`, recorded in `tests/acceptance/W1-05/README.md`). No KPI text changes.

### DEC-149 — W1-05 KD-1: what the 100 ms hook budget covers
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-05 KPI dispute KD-1 · **Refines:** DEC-134 (the snapshot's cost)
- **Decision:** The 100 ms p95 hook budget covers the guard's decision, for every tool. For Bash, the total wait
  including W1-03's before-snapshot (observed 115–119 ms p95) is measured and reported in W1-05's record, and isn't a
  failure.

| Version | Date | Change |
|---|---|---|
| 0.25 | 2026-10-01 | W1-05 KD-1: DEC-149 (the 100 ms p95 budget is the guard's decision for every tool; the Bash wait with the before-snapshot is measured and reported, not a failure). |

## 26. S2 specification-change decisions (register v0.26, appended by S2 on branch `s2/spec`)

Owner decisions given in the S2 brief (DEC-150…DEC-155), and the owner's answers of 2026-10-03 to the S2 decision
packages P-1…P-5, to DP-7 and to the open point on the oracle (DEC-156…DEC-162). The impact is listed in `docs/changes/S2-CIT-P.md` and the execution
in `docs/changes/S2-CIT-E.md`.

### DEC-150 — DP-7: the orchestrator's standing rights, option (b) extended
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief, on DP-7 option (b) extended · **Amended by:** DEC-156
- **Decision as given in the brief:** whatever its active ticket, the orchestrator role may write `.tickets/**`,
  `docs/DECISION_REGISTER.md`, `governance/project/bootstrap.md` and `.gov-runtime/scratch/**`. A commit made by the
  orchestrator is judged against these standing paths plus the active ticket's `allowed_paths`. DEC-156 replaces both
  of these rules.
- **Still in force:**
  - The orchestrator's checkpoint moves to `.gov-runtime/scratch/orchestrator/` until W1-25's `gov checkpoint`
    replaces it.
  - `tests/acceptance/**` is never covered, unless the committing actor is the Independent Test Designer.
  - This is a guard change and needs a new ticket (W1-45).
  - Bootstrap of that ticket: S2 creates it and sets it `in_progress`. Under the live guard, the test designer writes
    its tests with the ticket in its `GOV_TICKET`; an `engineer` subagent implements it and commits its own work; the
    owner, through the operator console outside the guard, closes it.

### DEC-151 — Two confirmations from W1-05
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief · **Confirms:** DEC-120
- **Decision:** Moving the install settings rules from `deny` to `ask` at the switch-over is correct; it keeps the
  second line of DEC-120. W1-01's interim acceptance tests skipping after the switch-over is by design.

### DEC-152 — EXP-001 is accepted as ADOPT-PARTIAL
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief, on `spike-sandbox/EVIDENCE.md` · **Outcome of:** DEC-138, DEC-147 · **Scoped by:** DEC-161
- **Decision:**
  - The OS sandbox is the outer wall for everything a Bash command does: writes outside the repository, installs,
    network, and reads of hidden paths. Its configuration comes from the launcher through `--settings`, never from the
    repository: enabled, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, and network `strictAllowlist`.
  - The guard stays the wall for the file tools: Read, Edit and Write run outside the sandbox. `Edit(...)` and
    `Read(...)` deny rules bind both layers.
  - The qualification oracle is hidden from Bash by the sandbox, and from the file tools by a `Read` deny rule. Hiding
    is silent: the directory looks empty.
  - Residuals closed for Bash: outside-repository writes through opaque forms (DEC-123), and the install misses
    (DEC-147).
  - Residuals restated: file-tool reads and writes (guard only); anything a hook or MCP server does; the shared
    `$TMPDIR` (see DEC-159).
- DEC-161 limits which sessions are sandboxed; the closures hold for those sessions.

### DEC-153 — New Wave 1 tickets from EXP-001
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief, on EVIDENCE §5.5 · **Under:** DEC-152
- **Decision:** Wave 1 gains three tickets:
  1. **The launcher** (`gov launch`, or equivalent). It builds per-role `--settings` (sandbox block plus role `Edit`
     deny rules), sets `GOV_ROLE` and `GOV_TICKET`, and refuses to start unless the sandbox is on, strict and
     fail-closed.
  2. **Guard hardening.** Deny any Bash call carrying `dangerouslyDisableSandbox: true`; register the containment
     check on `PostToolUseFailure` as well, because a failed command may still have written files before failing.
  3. **Claude Code version.** Pin it at 2.1.285 or later, and align the CLI used for headless runs with the VS Code
     extension's bundled version. The spike saw 2.1.284 on the CLI; the test designer saw 2.1.286.

### DEC-154 — The W1-05 provider change
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief · **Implements:** DEC-119
- **Decision:** W1-05 delivered minimal role subagent definitions in `.claude/agents/`; W1-33 replaces them. The
  providers in Contract v4 are updated to match.

### DEC-155 — The plan validator after S1
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief
- **Decision:** `docs/plan/tools/validate_s1.py` scopes its "writes only under docs/ and .tickets/" check to the S1
  branch, or retires it, and is extended to check everything the S2 change adds. It stays runnable from the
  repository root.

### DEC-156 — DP-7 corrected: the orchestrator may write anywhere except `tests/acceptance/**`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, answer to S2 · **Amends:** DEC-150 (replaces its standing paths and commit rule)
- **Decision:** The orchestrator role may write anywhere in the repository except `tests/acceptance/**` (MR-3). The
  guard enforces only that exclusion for the orchestrator. Containment still records its changes. Its checkpoint goes
  to `.gov-runtime/scratch/orchestrator/` until W1-25. The orchestrator's interactive session (VS Code or terminal)
  is not sandboxed.

### DEC-157 — P-1: installs stay as DEC-083 decided
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2 package P-1, option (d), the owner's own · **Confirms:** DEC-083
- **Decision:** The orchestrator installs tools under DEC-083 as decided: the guard asks, and the owner approves in
  chat. Worker roles never install system-wide.

### DEC-158 — P-2: network profiles per role
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2 package P-2 (the owner's own answer)
- **Decision:**
  - The orchestrator is unrestricted, being unsandboxed.
  - Research and experiment work (discovery spikes, bake-offs, and product-spec when it runs experiments) gets a
    broad allowlist of research and development domains, which the owner can extend: GitHub, PyPI, npm, Hugging Face,
    arXiv and documentation sites. Its writes and installs stay inside its own experiment folder (a venv or local
    prefix).
  - Engineer, independent test designer and independent auditor get an empty allowlist.
  - WebSearch and WebFetch run outside the sandbox (EXP-001), so web research stays available to every role.

### DEC-159 — P-3: a per-session temp directory for worker sessions
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2 package P-3 option (a), with a fallback
- **Decision:** The launcher sets a per-session temp directory for worker sessions. If the launcher's acceptance test
  shows the temp directory can't be overridden, the shared `$TMPDIR` is recorded as a residual.

### DEC-160 — P-4: the untested sandbox cases go to a Wave 2 experiment
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2 package P-4 option (a) · **Under:** DEC-102
- **Decision:** `denyWrite` on a path that doesn't exist yet, symlink and hard-link tricks, the seccomp filter and
  `bypassPermissions` mode are tested by a Wave 2 experiment. Until then they are residuals.

### DEC-161 — P-5: the sandbox applies to launched worker sessions only
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2 package P-5 (the owner's own answer) · **Scopes:** DEC-152, DEC-153
- **Decision:** The launcher applies the sandbox to worker sessions only: engineer, independent test designer,
  independent auditor, and research or experiment work, each with its network profile from DEC-158. Work that needs
  the sandbox runs as a worker session the orchestrator launches. In-session subagents remain for read-only work,
  such as review, exploration and web research. The repository's settings carry no sandbox block.
- **The launcher's acceptance tests must show:**
  - that a launched worker is sandboxed;
  - that its network profile applies, including that the domain allowlist accepts the research domains (EXP-001
    tested only an empty list);
  - that its `GOV_ROLE` and `GOV_TICKET` reach the guard.

### DEC-162 — The qualification oracle is hidden from every session started in the repository root
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, answer to the S2 open point on DEC-161 · **Refines:** DEC-152 (oracle hiding), DEC-161
- **Decision:** The qualification oracle is hidden from every session started in the repository root, the unsandboxed
  orchestrator included, by two layers:
  - a `Read` deny rule with the oracle's absolute path in the repository's committed `.claude/settings.json`;
  - the guard denying any tool call whose input names the oracle path (Read, Grep, Glob, Bash).
- Both are delivered by the guard-hardening ticket (W1-47).
- **Residual:** an opaque Bash read in the orchestrator's own session remains an accepted residual, restated in
  `governance/project/bootstrap.md`.

| Version | Date | Change |
|---|---|---|
| 0.26 | 2026-10-03 | S2 brief: DEC-150 (DP-7 orchestrator standing rights; amended by DEC-156), DEC-151 (two W1-05 confirmations), DEC-152 (EXP-001 accepted as ADOPT-PARTIAL), DEC-153 (launcher, guard hardening and Claude Code pin tickets), DEC-154 (W1-05 provider change), DEC-155 (plan validator scope). Owner answers to S2: DEC-156 (DP-7 corrected: the orchestrator writes anywhere except `tests/acceptance/**`, unsandboxed), DEC-157 (P-1: installs stay as DEC-083), DEC-158 (P-2: network profiles per role), DEC-159 (P-3: per-session temp directory for workers, residual as fallback), DEC-160 (P-4: Wave 2 experiment), DEC-161 (P-5: sandbox for launched worker sessions only), DEC-162 (the qualification oracle is hidden from every session started in the repository root by a committed `Read` deny rule and a guard rule, both from W1-47; an opaque Bash read in the orchestrator session stays a residual). |

## 27. S2 repair decisions after the S2-A round-1 audit (register v0.27, appended by S2 on branch `s2/spec`)

Owner decisions of 2026-10-03, given with the S2-A round-1 verdict (ACCEPT_WITH_FINDINGS): the answers to the audit's
decision packages DP-1 and DP-2, and three additions the owner made in the same message. The repair is recorded in
`docs/changes/S2-CIT-E.md` §6.

### DEC-163 — DP-1: a minimal research role in the Wave 1 roster
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2-A package DP-1 · **Refines:** DEC-157, DEC-158 · **Amends:** DEC-083 (for the research role only), Charter v5 §6 (roster)
- **Decision:**
  - The Wave 1 roster gains a minimal research role: a role file delivered with the launcher (W1-46).
  - It may install only inside its own experiment folder: a venv or local prefix within its ticket's `allowed_paths`.
    System-wide installs are denied to it. The sandbox's write fence enforces this.
  - Its network profile is the research allowlist of DEC-158.
  - The full research lifecycle (CAP-32) stays in Wave 3.
- **Note:** the owner's message names "DEC-159's research allowlist". The research allowlist is in DEC-158; DEC-159
  is the per-session temp directory, which a research session also gets. The decision is carried against DEC-158.

### DEC-164 — DP-2: two more sandbox residuals, and no `excludedCommands`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2-A package DP-2 · **Extends:** DEC-160 · **Under:** DEC-152, DEC-161
- **Decision:**
  - Two points are open residuals: subagents inside a sandboxed worker session, and `excludedCommands`.
  - Both are added to EXP-002, the Wave 2 sandbox experiment of DEC-160.
  - The launcher sets no `excludedCommands`.

### DEC-165 — The upstream lesson loop, in a lite form (Wave 3)
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Reverses:** DEC-053 Q7, for framework lessons only · **Amends:** DEC-156 (one path outside the repository), Charter v5 §7 (non-goal row)
- **Decision:** A lite form of CAP-41 and of the former Contract v3 Q4, built in Wave 3:
  - Every lesson record carries a scope (project, product or framework) and a severity (low, medium, high or
    critical).
  - A framework lesson becomes a lesson packet: failure pattern, evidence and suggested change. It carries no product
    code, data or secrets, and is scanned by gitleaks. The product's orchestrator writes it to the shared inbox
    `~/gov-os-lessons-inbox/`, the one path outside its repository the orchestrator may write (a guard exception).
  - A high or critical lesson is raised to the owner immediately, as a decision package.
  - The Gov OS orchestrator triages the inbox (deduplicate, rank) into change proposals under the normal cycle. Each
    release's notes list the lessons fixed, with their severity.
  - In every repository, `gov doctor` compares the installed release with the latest and reports pending updates and
    their highest severity at session start. The owner decides when to run `gov update`.
  - Product decisions, specifications and lessons never leave their repository.

### DEC-166 — `gov discover`, the entry point to discovery (Wave 2)
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Under:** DEC-102, DEC-103
- **Decision:** `gov discover <question or feature>` is the entry point to discovery. It opens a discovery ticket,
  runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose
  evidence records, with measured numbers, back the answer. Plain language works the same way.

### DEC-167 — "What's the impact of X?" triggers the impact assessment
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Under:** DEC-105
- **Decision:** "What's the impact of X?" asked in plain language triggers the impact assessment: `gov impact` from
  Wave 2; in Wave 1, an OpenSpec proposal plus `gov closure`.

| Version | Date | Change |
|---|---|---|
| 0.27 | 2026-10-03 | S2 repair after the S2-A round-1 audit: DEC-163 (DP-1: a minimal research role in the Wave 1 roster, delivered with W1-46; installs only inside its experiment folder, enforced by the sandbox's write fence; research allowlist of DEC-158), DEC-164 (DP-2: subagents inside a sandboxed worker session and `excludedCommands` are open residuals, added to EXP-002; the launcher sets no `excludedCommands`), DEC-165 (the lite upstream lesson loop, Wave 3; reverses DEC-053 Q7 for framework lessons only), DEC-166 (`gov discover`, Wave 2), DEC-167 (a plain-language impact question triggers the impact assessment). |

## 28. S2 repair decisions, second pass (register v0.28, appended by S2 on branch `s2/spec`)

Owner answers of 2026-10-03 to the points S2 raised after the first repair pass. The owner also confirmed, without a
new decision: the Charter change, limited to the lines DEC-163 and DEC-165 require; DEC-158 as the citation in
DEC-163 (the "DEC-159" in the owner's message was a numbering slip); and W1-46's growth to 220 LOC with its dependency
on W1-47.

### DEC-168 — Scope and severity are in the Wave 1 lesson schema
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, answer to S2 · **Refines:** DEC-165
- **Decision:** W1-08's lesson schema carries scope and severity now, in Wave 1, so that no migration is needed later.
  The lesson loop itself stays in Wave 3.

### DEC-169 — The plan validator: the fingerprint fallback and the S2 write-scope check
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, repair instruction on S2-A finding S2A-F-08 · **Extends:** DEC-155 · **Under:** DEC-101
- **Decision:** The S1-A fingerprint check accepts a renamed file for `PROMPT.md` only (`PROMPT.retired.md`, same
  hash, DEC-101). Every other listed file must exist under its own name. The S2 write-scope check excludes
  `docs/SOURCES.md`, as the S1 check did.

| Version | Date | Change |
|---|---|---|
| 0.28 | 2026-10-03 | S2 repair, second pass: DEC-168 (scope and severity in W1-08's lesson schema in Wave 1; the loop stays Wave 3), DEC-169 (the fingerprint rename fallback is for `PROMPT.md` only; the S2 write-scope check excludes `docs/SOURCES.md`). |

## 29. Owner confirmations after the S2 repair (register v0.29, appended by S2 on branch `s2/spec`)

Owner confirmations of 2026-10-03 on three points the S2 repair raised (`docs/changes/S2-CIT-E.md` §6.4). The owner
confirmed DEC-169 as the owner's decision; its entry is unchanged.

### DEC-170 — Sandbox instruction tokens are reported apart from the governance share
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2-A finding S2A-F-07 · **Under:** DEC-086
- **Decision:** Sandbox instruction tokens are reported as a separate line in W1-31, not inside the governance share.
  Whether they count toward the 15 % is decided at the Wave 1 exit, using measured figures.

### DEC-171 — An orchestrator change outside its ticket's paths is a record, not a containment finding
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2-A finding S2A-F-01 · **Confirms:** DEC-156
- **Decision:** A change the orchestrator makes outside its ticket's paths is a record, not a containment finding
  (DEC-156).

| Version | Date | Change |
|---|---|---|
| 0.29 | 2026-10-03 | Owner confirmations: DEC-169 confirmed as the owner's decision; DEC-170 (sandbox instruction tokens are a separate line in W1-31, outside the governance share; whether they count toward the 15 % is decided at the Wave 1 exit); DEC-171 (an orchestrator change outside its ticket's paths is a record, not a containment finding). |

## 30. Owner answers after the S2-A round-2 audit (register v0.30, appended by S2 on branch `s2/spec`)

Owner answers of 2026-10-03 to the two decision packages of the S2-A round-2 audit (ACCEPT_WITH_FINDINGS). The repair
is recorded in `docs/changes/S2-CIT-E.md` §7.

### DEC-172 — DP-3: the settings ask rules for installs and downloads are removed; the guard's install rule stands alone
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2-A package DP-3 option (b), unconditionally · **Withdraws:** the settings "second line" of DEC-120 and DEC-151 · **Under:** DEC-083, DEC-163
- **Decision:**
  - The install and download ask rules are removed from the committed `.claude/settings.json`. The guard's install
    rule is relied on alone.
  - No test run is needed first. W1-05's live attempts showed that the guard's rule suffices alone: an install that
    no settings rule matched still got the hook's `ask`.
  - In launched worker sessions, the sandbox backs the guard.
  - W1-47, which already holds `.claude/settings.json` in its `allowed_paths`, makes the settings change. W1-46's
    KPI and `governance/project/bootstrap.md` are updated to match.

### DEC-173 — DP-4: Charter §6's install sentence names the research exception
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2-A package DP-4 option (a) · **Extends:** DEC-163 · **Amends:** Charter v5 §6 (install sentence)
- **Decision:** Charter §6's install sentence gains "except the research role, inside its experiment folder
  (DEC-163)". The plan validator's Charter line count and `docs/changes/S2-CIT-E.md` §6.3 are updated to match.

| Version | Date | Change |
|---|---|---|
| 0.30 | 2026-10-03 | Owner answers after the S2-A round-2 audit: DEC-172 (DP-3: the install and download ask rules leave the committed `.claude/settings.json`, in W1-47; the guard's install rule stands alone, backed by the sandbox in launched worker sessions; withdraws the settings second line of DEC-120 and DEC-151), DEC-173 (DP-4: Charter §6's install sentence names the research exception of DEC-163). |

## 31. Owner decision at the S2-A round-3 closure check (register v0.31, appended by S2 on branch `s2/spec`)

Owner decision of 2026-10-03, given with the round-3 closure check (ACCEPT_WITH_FINDINGS, two minor findings; no
further audit round). The fixes are recorded in `docs/changes/S2-CIT-E.md` §8.

### DEC-174 — The guard's install rule recognises `uv add`, `uv sync`, `uv run --with` and `uvx` as installs
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2-A finding S2A-F-17 · **Extends:** DEC-172 · **Under:** DEC-083, DEC-163
- **Decision:**
  - W1-47 extends the guard's install rule to recognise `uv add`, `uv sync`, `uv run --with` and `uvx` as installs,
    so they keep their `ask` for the orchestrator (DEC-083).
  - The research role's exception (DEC-163) still lets them through inside its experiment folder.

| Version | Date | Change |
|---|---|---|
| 0.31 | 2026-10-03 | Round-3 closure check: DEC-174 (W1-47 extends the guard's install rule to `uv add`, `uv sync`, `uv run --with` and `uvx`; `ask` for the orchestrator under DEC-083; the research exception of DEC-163 still applies). |

## 32. Owner answers on W1-45's decision packages (register v0.32, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-03 to the four packages the W1 orchestrator raised while building W1-45 (`DAEO-6cc2`), from
its verification and from the reviewer's probe (DEC-137).

### DEC-175 — DP-1: the Independent Test Designer revises W1-04's two cases; `tests/unit/install/**` joins W1-45's paths
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-45 package DP-1 option (a) · **Under:** DEC-156, DEC-106
- **Decision:**
  - The Independent Test Designer revises the two W1-04 acceptance cases that assert the old orchestrator rule
    (`write-outside-the-ticket-paths` and `redirect-outside-the-ticket-paths` in `test_w1_04_only_escalates.py`) in
    a W1-45 test design batch. Each is recorded as a rewrite after implementation, with the reason "owner
    correction, DEC-156".
  - `tests/unit/install/**` joins W1-45's `allowed_paths`, so the engineer can update the builder test. The ticket
    change is its own commit, with the trailer `Task: DAEO-6cc2`.

### DEC-176 — DP-2: `.gov-runtime/` other than `scratch/**` stays denied to the orchestrator
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-45 package DP-2 option (a) · **Amends:** DEC-156
- **Decision:**
  - Everything under `.gov-runtime/` other than `scratch/**` stays denied to the orchestrator: the freeze flag, the
    snapshots, the findings and the records.
  - Setting or lifting a freeze is the owner's action.
  - The W1-02 freeze test stays as it is.

### DEC-177 — DP-3: the record of DEC-171 is one JSON line per call in `.gov-runtime/records.jsonl`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-45 package DP-3 option (a) · **Extends:** DEC-171 · **Under:** DEC-122
- **Decision:** An orchestrator change outside its ticket's paths writes one JSON line per call to
  `.gov-runtime/records.jsonl`, with DEC-122's fields and `action: "recorded"`. `findings.jsonl` and its action list
  are unchanged.

### DEC-178 — DP-4: the orchestrator's wide scope holds only when the session's own role is orchestrator
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-45 package DP-4 option (a) · **Extends:** DEC-156 · **Under:** DEC-117
- **Decision:** The wide scope of DEC-156 holds only when the session's own role is orchestrator. An `orchestrator`
  subagent in another role's session keeps the ticket-paths rule.

| Version | Date | Change |
|---|---|---|
| 0.32 | 2026-10-03 | Owner answers on W1-45's packages: DEC-175 (DP-1: the test designer revises two W1-04 cases; `tests/unit/install/**` joins W1-45's `allowed_paths`), DEC-176 (DP-2, amends DEC-156: `.gov-runtime/` other than `scratch/**` stays denied to the orchestrator; a freeze is the owner's action), DEC-177 (DP-3: the DEC-171 record is one JSON line per call in `.gov-runtime/records.jsonl`, `action: "recorded"`), DEC-178 (DP-4: the wide scope holds only in a session whose own role is orchestrator). |

## 33. Owner decisions at W1-45's close (register v0.33, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-03, given when the owner closed W1-45 (`DAEO-6cc2`), on the three items the final
reviewer's probe left (DEC-137) and on commit trailers.

### DEC-179 — A guard function that fails open is a defect: W1-47 makes the session-role default fail closed
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, at W1-45's close · **Under:** DEC-178, DEC-135
- **Decision:**
  - The guard function that gives the orchestrator's wide scope when its session-role argument is missing
    (`_get_allowed_paths` in `src/gov/guard/decide.py`) is a defect, not a residual.
  - W1-47's engineer makes it fail closed when the session-role argument is missing, with a builder test. W1-47
    gains a matching KPI line, in its own commit with the trailer `Task: DAEO-o4fg`.
  - In general, a finding that makes the guard fail open is a defect, not a residual.

### DEC-180 — `.gov-runtime/` is protected in worker sessions by an `Edit` deny rule the launcher sets
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, at W1-45's close · **Extends:** DEC-176 · **Under:** DEC-152, DEC-161, EXP-001
- **Decision:**
  - The settings the launcher builds for every worker role carry an `Edit` deny rule for `.gov-runtime/**` except
    `.gov-runtime/scratch/**`.
  - That closes opaque Bash writes and `ln` there at OS level: one `Edit` rule binds the file tools and Bash
    (EXP-001).
  - W1-46 gains a matching KPI line, in its own commit with the trailer `Task: DAEO-jdqr`.

### DEC-181 — In the orchestrator's own session, opaque Bash writes and `ln` into `.gov-runtime/` stay a residual
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, at W1-45's close · **Under:** DEC-156, DEC-176
- **Decision:** The orchestrator's own session is not sandboxed (DEC-156). An opaque Bash write or an `ln` into
  `.gov-runtime/` in that session is seen by neither the guard nor the containment check, and stays an accepted
  residual, recorded in `governance/project/bootstrap.md`.

### DEC-182 — Commit trailers go in the final trailer block, with `git commit --trailer`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, at W1-45's close · **Under:** DEC-097
- **Decision:**
  - From now on every commit puts `Task:`, `Implements:` and `Role:` in the final trailer block, using
    `git commit --trailer`. Git reads trailers only from the last paragraph of a commit message.
  - Checks that read trailers fall back to the message body for commits made before 2026-10-03.
  - History is not rewritten.
  - The rule is added to the rules of `docs/plan/WAVE_1_WBS.md`.

| Version | Date | Change |
|---|---|---|
| 0.33 | 2026-10-03 | Owner decisions at W1-45's close: DEC-179 (a fail-open guard default is a defect; W1-47 makes it fail closed), DEC-180 (the launcher's worker settings deny `Edit` on `.gov-runtime/**` except `scratch/**`; W1-46), DEC-181 (opaque Bash writes and `ln` into `.gov-runtime/` stay a residual in the orchestrator's own session), DEC-182 (trailers in the final block with `git commit --trailer`; checks fall back to the body for commits before 2026-10-03). |

## 34. Owner answers on W1-07's decision packages (register v0.34, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-03 to the packages raised at W1-07's test design (`DAEO-drvn`): the test designer's three
KPI disputes (KD-1…KD-3), the orchestrator's DP-5, and two items the orchestrator reported.

### DEC-183 — Worker identity and headless flags until the launcher exists
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-161, DEC-107
- **Decision:**
  - Until W1-46 closes, every headless worker session is started with
    `--settings '{"env":{"GOV_ROLE":"<role>","GOV_TICKET":"<id>"}}'`, which overrides the `env` block in
    `.claude/settings.local.json`.
  - The headless flags are approved: `--permission-mode acceptEdits`, with Bash and the file tools allowed. The
    guard decides every call.
  - Both are added to the orchestrator's checkpoint and to the rules of `docs/plan/WAVE_1_WBS.md`.

### DEC-184 — DP-5: the W1-07 drafts written under the wrong identity are discarded
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-07 package DP-5 option (b) · **Under:** MR-3
- **Decision:** The drafts in `.gov-runtime/scratch/independent-test-designer/W1-07/` are discarded and the folder
  deleted. A fresh, correctly identified test designer starts from the ticket and these decisions alone.

### DEC-185 — KD-1: every `gov` command loads the `governance/project/` files it knows; an invalid one is `CONFIG_INVALID`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-07 package KD-1 option (a), without a new `overlay.yaml`
- **Decision:**
  - Every `gov` command loads the `governance/project/` files it knows: `path-map.yaml` now, the other overlay
    files as their tickets add them. There is no new `overlay.yaml`.
  - A missing file is not an error. An invalid one gives exit 1 with `CONFIG_INVALID`, naming the file and the key.
  - A minimal path-map schema lives under `src/gov/config/` until W1-08 supplies the real one and replaces it.

### DEC-186 — KD-2: check declarations are YAML in the kernel template; `gov check --list --json` is built at W1-07
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-07 package KD-2 option (a), in the kernel template
- **Decision:**
  - Check declarations are YAML files under `template/governance/kernel/checks/*.yaml`, with `id`, `family`,
    `tier`, `severity` and `command`.
  - `gov check --list --json` is built at W1-07. Running checks stays `NOT_IMPLEMENTED` until W1-26.
  - `template/governance/kernel/checks/**` joins W1-07's `allowed_paths`, in its own commit with the trailer
    `Task: DAEO-drvn`.

### DEC-187 — KD-3: no public surface for the read/act class at W1-07
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-07 package KD-3 option (b)
- **Decision:** W1-07 gives the read/act class no public surface. It is tested by behaviour only, and revisited at
  W1-26.

### DEC-188 — The plan validator accepts the owner's close of W1-45
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-150, DEC-169
- **Decision:** `docs/plan/tools/validate_s1.py` is updated so that its W1-45 check accepts the owner's close (W1-45
  closed under DEC-150), in its own commit with the trailer `Task: decision-record`. The validator must then pass.

| Version | Date | Change |
|---|---|---|
| 0.34 | 2026-10-03 | Owner answers on W1-07's packages: DEC-183 (worker identity through `--settings` env, and the headless flags, until W1-46), DEC-184 (DP-5: the W1-07 drafts are discarded), DEC-185 (KD-1: commands load the `governance/project/` files they know; invalid gives `CONFIG_INVALID`; a minimal path-map schema until W1-08), DEC-186 (KD-2: check declarations under `template/governance/kernel/checks/`; `gov check --list --json` at W1-07), DEC-187 (KD-3: no public surface for the read/act class at W1-07), DEC-188 (the validator accepts W1-45's close). |

## 35. Owner answers during W1-07's build (register v0.35, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-03 to the test designer's package DP-1 on W1-07 (`DAEO-drvn`) and to two points the
orchestrator reported.

### DEC-189 — W1-07 DP-1: `CONFIG_INVALID` carries `file` and `key` in `error.details`; the minimal path-map shape is provisional
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-07 package DP-1 option (a), with a clarification · **Extends:** DEC-185
- **Decision:**
  - The stable contract: an invalid `governance/project/` file gives exit 1 with `CONFIG_INVALID`, and
    `error.details` carries `file` and `key`. The acceptance tests rely on that.
  - The minimal path-map shape (the top level is a map; `namespaces` is required and maps a name to a map) is
    provisional until W1-08 replaces the minimal schema.
  - If W1-08 changes the keys, the matching test revisions are expected.

### DEC-190 — Planned test revisions are counted apart from rewrites
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Extends:** DEC-106
- **Decision:**
  - When a later ticket implements a `gov` command and revises its `NOT_IMPLEMENTED` case in
    `tests/acceptance/W1-07/test_w1_07_registry.py`, the revision is recorded with the reason "planned: command
    implemented".
  - The learning metric counts planned revisions apart from rewrites that correct a test or a specification.

### DEC-191 — PyYAML goes into the tool registry when W1-06 creates it
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-083, DEC-127
- **Decision:** PyYAML 6.0.1, already on this machine and declared in `pyproject.toml`, is recorded in the tool
  registry when W1-06 creates it, like every other dependency.

| Version | Date | Change |
|---|---|---|
| 0.35 | 2026-10-03 | Owner answers during W1-07's build: DEC-189 (DP-1: `CONFIG_INVALID` with `file` and `key` in `error.details` is the stable contract; the minimal path-map shape is provisional until W1-08), DEC-190 (planned test revisions, reason "planned: command implemented", counted apart from rewrites), DEC-191 (PyYAML 6.0.1 enters the tool registry at W1-06). |

## 36. Owner answers on W1-06's packages (register v0.36, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-03 to the orchestrator's install package for W1-06 (`DAEO-ipqy`, DEC-083) and to the test
designer's four packages (DP-1…DP-4).

### DEC-192 — Install approved: ccusage 20.0.26
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1-06 install package · **Under:** DEC-083, DEC-086
- **Decision:** The orchestrator installs ccusage 20.0.26 with
  `~/.nvm/versions/node/v22.23.3/bin/npm install -g ccusage@20.0.26` (ADR-0002's Node 22). It is uninstalled with
  the same npm. This entry is the owner approval the registry cites.

### DEC-193 — Download approved: the Superpowers v6.4.2 source
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1-06 install package · **Under:** DEC-083, DEC-074 Q5
- **Decision:** The orchestrator runs `git clone --depth 1 --branch v6.4.2 https://github.com/obra/superpowers` into
  `.gov-runtime/scratch/orchestrator/vendor-src/superpowers/`. This entry is the owner approval the registry cites
  for Superpowers v6.4.2.

### DEC-194 — W1-06 DP-3: only the three skills and the licence are committed
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-06 package DP-3 option (a) · **Under:** DEC-074 Q5, DEC-076
- **Decision:**
  - Only the three skill folders (test-driven-development, systematic-debugging, verification-before-completion)
    and the upstream licence are committed, unchanged, under `template/governance/kernel/vendor/superpowers/`.
  - The plugin, its hook and every other skill never enter the repository.
  - The scratch clone is deleted afterwards.

### DEC-195 — W1-06 DP-1: the ten pins with a sha256, plus gitleaks 8.30.1
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-06 package DP-1 option (a), with an addition · **Under:** DEC-074, DEC-056
- **Decision:**
  - "Every DEC-074 pin" in W1-06 means the ten rows of ADR-0002 §2 that give a version and a sha256.
  - gitleaks 8.30.1 is added now (already installed; W1-15 uses it), with the sha256 of its binary.
  - The other stack rows without a sha256 enter the registry when the ticket that installs them runs.

### DEC-196 — W1-06 DP-2: what the registry's sha256 covers
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-06 package DP-2 option (a), with a clarification
- **Decision:**
  - `sha256` covers the one downloaded artefact (npm tarball, release tarball, distribution package), or the binary
    itself for a single-file tool.
  - `gov doctor` re-checks the hash for single-file binaries and the version for multi-file tools.

### DEC-197 — W1-06 DP-4: each install has its own register entry, which `approved_by` cites
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-06 package DP-4 option (a) · **Under:** DEC-083
- **Decision:**
  - Each install has its own register entry naming the tool and its exact version, and the registry's `approved_by`
    cites it.
  - Older pins cite the decision that names them (DEC-074, DEC-191, DEC-141).

### DEC-198 — The S0b2 tool registry is read for the full digests
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report
- **Decision:** The orchestrator reads `~/gov-os-workbench/s0b2/out/TOOL_REGISTRY.yaml` for the full digests of the
  pins. It reads workbench files by exact path, and does not list the workbench's top level.

| Version | Date | Change |
|---|---|---|
| 0.36 | 2026-10-03 | Owner answers on W1-06's packages: DEC-192 (install approved: ccusage 20.0.26 under Node v22.23.3), DEC-193 (download approved: Superpowers v6.4.2 source into the orchestrator's scratch), DEC-194 (DP-3: only the three skills and the licence are committed), DEC-195 (DP-1: the ten pins with a sha256, plus gitleaks 8.30.1), DEC-196 (DP-2: sha256 covers the downloaded artefact, or the binary of a single-file tool), DEC-197 (DP-4: each install has its own register entry, cited by `approved_by`), DEC-198 (the S0b2 registry is read for full digests; workbench files by exact path). |

## 37. Owner answers at W1-06's implementation (register v0.37, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-03 to the test designer's package DP-5 on W1-06 (`DAEO-ipqy`) and to three points the
orchestrator reported about the registry.

### DEC-199 — W1-06 DP-5: the sha256 of a vendored folder is a digest of its committed files
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-06 package DP-5 option (a) · **Extends:** DEC-196
- **Decision:**
  - The Superpowers entry's `sha256` is a digest of the committed vendor folder: the sha256 of the sorted lines
    `<sha256 of the file>  <relative path>` over every file under `template/governance/kernel/vendor/superpowers/`.
  - A test and `gov doctor` recompute it offline.
  - This widens DEC-196 to vendored folders.

### DEC-200 — DEC-196 clarified: an installed entry script's digest where ADR-0002 already pins it
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Clarifies:** DEC-196
- **Decision:** For a tool installed through a package manager, the registry may carry the digest of its installed
  entry script where ADR-0002 already pins that value (openspec, check-jsonschema, copier). `gov doctor` re-checks it
  locally.

### DEC-201 — gitleaks and PyYAML carry their date of record
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-195, DEC-191
- **Decision:** gitleaks 8.30.1 and PyYAML 6.0.1 carry 2026-10-03 as their date of record, with a note that the
  original install dates were not recorded. PyYAML's install and uninstall are `sudo apt-get` owner actions.

### DEC-202 — Node 22 installs carry the PATH prefix
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Corrects:** DEC-192 (the command's form)
- **Decision:**
  - The ccusage commands carry the prefix `PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH`, because npm's script runs
    the first `node` on `PATH`. The command approved in DEC-192 lacked it; the orchestrator's correction (the copy
    that landed under Node v18.20.8 was uninstalled, and ccusage 20.0.26 reinstalled under Node v22.23.3) is
    confirmed.
  - Every future Node 22 install uses the prefix.

| Version | Date | Change |
|---|---|---|
| 0.37 | 2026-10-03 | Owner answers at W1-06's implementation: DEC-199 (DP-5: a vendored folder's sha256 is the digest of its committed files, by a written rule; widens DEC-196), DEC-200 (DEC-196 clarified: an installed entry script's digest where ADR-0002 pins it), DEC-201 (gitleaks and PyYAML carry their date of record), DEC-202 (Node 22 installs carry the PATH prefix; the ccusage correction is confirmed). |

## 38. Owner answers on W1-48's install package, W1-06's close and the context limit (register v0.38, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-03 to the orchestrator's install package for W1-48 (`DAEO-0qs5`, DEC-083), to the points
reported at W1-06's close, and on the orchestrator's context limit.

### DEC-203 — Install approved and made by the owner: Claude Code 2.1.288
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1-48 install package option (b) · **Under:** DEC-083, DEC-153, DEC-196, DEC-197
- **Decision:**
  - The owner updated the Claude Code CLI from 2.1.284 to 2.1.288 with `claude install 2.1.288`, through the
    operator console, outside every agent session, as an owner action. No agent session installed it.
  - Facts: `claude --version` prints `2.1.288 (Claude Code)`; `~/.local/bin/claude` resolves to
    `/home/usain/.local/share/claude/versions/2.1.288`; the sha256 of that binary is
    `0298068b686e7fdbaf9402a7a587bb7f49c0b0e084de09f69145a0719207640c`.
  - The registry entry for Claude Code 2.1.288 is recorded from these facts, with the binary's sha256 (DEC-196).
    This entry is the owner approval its `approved_by` cites.
  - bubblewrap 0.9.0 and socat 1.8.0.0 enter the registry as owner installs under DEC-141.

### DEC-204 — The stale npm copy of Claude Code 2.1.59 is removed
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1-48 install package
- **Decision:** The owner removed the npm global `@anthropic-ai/claude-code` 2.1.59 under Node v18.20.8. The removal
  is noted in `governance/project/bootstrap.md`.

### DEC-205 — Headless workers start with the absolute path `~/.local/bin/claude`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1-48 install package · **Amends:** DEC-183 (the command's first word)
- **Decision:**
  - A second `claude` is on `PATH`: `/mnt/c/Users/usain/AppData/Roaming/npm/claude`, a Windows-side npm install
    reached through WSL's `PATH`, listed after `~/.local/bin/claude`.
  - Every headless worker is started with the absolute path `~/.local/bin/claude`, never a bare `claude`, so that a
    changed `PATH` can never start the Windows copy.
  - The Windows copy is recorded in `governance/project/bootstrap.md` as noted, not removed. It is outside WSL and
    the owner's choice.
  - W1-48's test designer adds a check that the pinned CLI is the one at `~/.local/bin/claude`.

### DEC-206 — The W1-06 containment finding stays as written; workers always run in the background
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report at W1-06's close · **Under:** DEC-134
- **Decision:**
  - The finding of 2026-10-03 in `.gov-runtime/findings.jsonl` (a test designer's commit attributed to the
    orchestrator's foreground call) stays as written. The findings file is append-only evidence.
  - The orchestrator's record in `governance/project/bootstrap.md` explains it, and the exit audit reads both.
  - The orchestrator's rule is confirmed: worker sessions always run in the background.

### DEC-207 — The DEC-202 PATH-prefix gap is closed in W1-48's test design batch
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-202, DEC-136
- **Decision:** W1-48's test designer adds a check that every Node 22 install command in the registry carries the
  prefix `PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH`.

### DEC-208 — The orchestrator's context limit: about 300k tokens, automatic from W1-29
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Under:** DEC-025, CAP-37
- **Decision:**
  - The orchestrator checkpoints and stops with `CONTEXT_CHECKPOINT` at about 300k tokens used, of a 1M window. Its
    prompt says so since commit `66e09aa1`.
  - From W1-29 this becomes automatic: the PreCompact hook writes the checkpoint; the SessionStart hook (on compact,
    clear and resume) re-injects the context packet and the checkpoint; the auto-compact threshold is set to about
    300k tokens if Claude Code allows it.
  - W1-29's test designer adds a test that a compaction preserves the open decisions, the active ticket and the
    loop counts.
  - If the threshold can't be configured, the `CONTEXT_CHECKPOINT` stop stays.
  - W1-29 (`DAEO-zsvl`) gets a matching KPI line, in its own commit with the trailer `Task: DAEO-zsvl`.

| Version | Date | Change |
|---|---|---|
| 0.38 | 2026-10-03 | Owner answers on W1-48's install package, W1-06's close and the context limit: DEC-203 (Claude Code 2.1.288 installed by the owner, option (b); the approval the registry cites; bubblewrap and socat as owner installs under DEC-141), DEC-204 (the stale npm copy 2.1.59 is removed), DEC-205 (headless workers start with `~/.local/bin/claude`; the Windows copy is noted, not removed), DEC-206 (the W1-06 finding stays as written; workers always run in the background), DEC-207 (the PATH-prefix check goes into W1-48's test design), DEC-208 (context limit of about 300k tokens, automatic from W1-29, with a KPI line). |

## 39. Owner answer on W1-48's KPI wording (register v0.39, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answer of 2026-10-03 to the orchestrator's report that W1-48's KPI line and Contract item CAP-25.d still said
the upgrade "is installed by the orchestrator", after DEC-203 made it an owner install.

### DEC-209 — W1-48's KPI line and CAP-25.d are reworded to match DEC-203
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-203, DEC-083 · **Amends:** the wording of DEC-153 ticket 3 and DEC-157 as carried by W1-48 and CAP-25.d
- **Decision:**
  - The Claude Code upgrade is installed by the owner, or by the orchestrator under DEC-083, and in both cases
    recorded with its owner approval.
  - W1-48's KPI line (`DAEO-0qs5`) is reworded so, in its own commit with the trailer `Task: DAEO-0qs5`.
  - Contract item CAP-25.d is reworded so, in its own commit with the trailer `Task: decision-record`.
  - The plan validator is re-run after both.

| Version | Date | Change |
|---|---|---|
| 0.39 | 2026-10-03 | Owner answer on W1-48's KPI wording: DEC-209 (W1-48's KPI line and CAP-25.d reworded to match DEC-203: the Claude Code upgrade is installed by the owner, or by the orchestrator under DEC-083, and in both cases recorded with its owner approval). |

## 40. Owner answers on W1-48's test design packages (register v0.40, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-04 to the test designer's packages DP-1 and DP-2 on W1-48 (`DAEO-0qs5`) and to the
orchestrator's report on the WBS wording.

### DEC-210 — W1-48 DP-1: the active VS Code extension, checked against the minimum; drift is reported, not failed
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-48 package DP-1 option (a) with (iii), with a change · **Under:** DEC-153, CAP-61.e
- **Decision:**
  - The extension is the one VS Code has active, read from its `extensions.json`.
  - Its bundled version is read from both `package.json` and the bundled binary's `--version`, and the binary's
    sha256 is compared with the registry.
  - The check is dynamic, not exact. It is a hard failure only if the CLI or the active extension is below the
    minimum, 2.1.285 (DEC-153).
  - If the CLI and the extension differ, or either is newer than the registry's record, that is drift that
    `gov doctor` reports, not a test failure. The owner re-records when convenient.
  - The test designer tests "at or above the minimum", not "equal to the pin".

### DEC-211 — W1-48 DP-2: registry commands carry the absolute path of the CLI
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-48 package DP-2 option (a) · **Under:** DEC-205
- **Decision:** Registry commands carry the absolute path (`$HOME/.local/bin/claude`), and a test refuses a bare
  `claude`.

### DEC-212 — Line 15 of the WBS is aligned with DEC-209
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-209
- **Decision:** The "Installs" rule of `docs/plan/WAVE_1_WBS.md` says that raising the Claude Code pin is an owner
  install, or an orchestrator install under DEC-083, recorded with its owner approval. The change is made in its
  own commit with the trailer `Task: decision-record`.

| Version | Date | Change |
|---|---|---|
| 0.40 | 2026-10-04 | Owner answers on W1-48's test design packages: DEC-210 (DP-1: the active extension from `extensions.json`, version from `package.json` and the bundled binary, sha256 compared with the registry; a hard failure only below 2.1.285; drift is reported by `gov doctor`, not failed), DEC-211 (DP-2: registry commands carry `$HOME/.local/bin/claude`; a test refuses a bare `claude`), DEC-212 (WBS line 15 aligned with DEC-209). |

## 41. Owner answers on W1-47's test design packages and W1-48's DP-3 (register v0.41, appended by the W1 orchestrator on branch `w1/integrate`)

Owner answers of 2026-10-04 to the test designer's packages DP-1…DP-6 on W1-47 (`DAEO-o4fg`) and DP-3 on W1-48
(`DAEO-0qs5`). The entries never name the held-out path; it is held in `governance/project/held-out.yaml` only.

### DEC-213 — W1-47 DP-6: the qualification oracle is outside the repository
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-47 package DP-6 (P1) option 1 · **Under:** DEC-162
- **Decision:** The qualification oracle is outside the repository, so W1-05's fixture, which copies the working
  tree, never copies it. Nothing changes.

### DEC-214 — W1-48 DP-3: the recorded version with another sha256 fails for the CLI and is drift for the extension
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-48 package DP-3 option (c) · **Refines:** DEC-210 · **Under:** DEC-196, DEC-205
- **Decision:**
  - For the CLI at `~/.local/bin/claude`, the recorded version with a different sha256 is a hard failure.
  - For the active extension's bundled binary it is drift, reported by `gov doctor`.
  - W1-48's second success line is reworded to match DEC-210 ("at or above the minimum"; a difference is drift), in
    its own commit with the trailer `Task: DAEO-0qs5`.
  - W1-27 gets a KPI line for `gov doctor`'s Claude Code drift report (DEC-210), in its own commit with the trailer
    `Task: DAEO-xw3k`.

### DEC-215 — W1-47 DP-1: what "names the held-out path" covers
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-47 package DP-1 option 3 · **Under:** DEC-162
- **Decision:**
  - The guard denies a tool call whose input contains the held-out path literally anywhere, or reaches it through a
    relative path, `..`, `~`, `$HOME` or a symbolic link.
  - Exception: edits to the two files that hold the path (`governance/project/held-out.yaml` and the committed
    `.claude/settings.json`).
  - Parent directories, globs and look-alike siblings are recorded in `governance/project/bootstrap.md` under the
    accepted residual.

### DEC-216 — W1-47 DP-3: the install rule knows `uv`'s value options
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-47 package DP-3 option 2 · **Extends:** DEC-174
- **Decision:** The install rule knows `uv`'s value options `--directory`, `--project`, `--cache-dir` and
  `--config-file`, plus `uv run -w`, and skips their value when looking for the subcommand.

### DEC-217 — W1-47 DP-4: the kernel template carries `settings.json`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-47 package DP-4 option 1
- **Decision:** The kernel template carries `template/governance/kernel/settings.json`, with PreToolUse for every
  tool and both post-command events, commands through `$CLAUDE_PROJECT_DIR`, and a behavioural test.

### DEC-218 — W1-47 DP-5: the owner wrote `held-out.yaml`; its key is `held_out_paths`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-47 package DP-5 (the owner fixed the key and wrote the file) · **Under:** DEC-162, DEC-179
- **Decision:**
  - `governance/project/held-out.yaml` was committed by the owner in
    `f66bd1b35dd4f5d0a88e63eec77485b7d7ca9685`. Its key is `held_out_paths`, a list of absolute paths. The guard and
    the launcher read that key.
  - A missing key, or a broken file, makes the guard fail closed. The owner repairs it through the operator.
  - No agent writes or retypes the path. The engineer generates the committed `Read` deny rule in
    `.claude/settings.json` with a script that reads `held-out.yaml`, so the path never appears in an agent's tool
    input.
  - The owner's commit counts as the KPI's owner confirmation of the value.

### DEC-219 — W1-47 DP-2: W1-46's test design covers the research role's exception
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-47 package DP-2 option 1 · **Under:** DEC-163, DEC-174
- **Decision:** The clause of W1-47's sixth success line on the research role's exception is tested in W1-46's test
  design, with the four `uv` forms. W1-47 closes with the clause recorded as carried.

| Version | Date | Change |
|---|---|---|
| 0.41 | 2026-10-04 | Owner answers on W1-47's packages and W1-48's DP-3: DEC-213 (DP-6: the oracle is outside the repository), DEC-214 (W1-48 DP-3: another sha256 at the recorded version fails for the CLI, is drift for the extension; W1-48's second success line reworded; a W1-27 KPI line for the drift report), DEC-215 (DP-1: literal anywhere, relative path, `..`, `~`, `$HOME`, symbolic link; exception for the two files that hold the path; parents, globs and look-alike siblings are residuals), DEC-216 (DP-3: `uv`'s four value options and `uv run -w`), DEC-217 (DP-4: `template/governance/kernel/settings.json`), DEC-218 (DP-5: the owner wrote `held-out.yaml`, key `held_out_paths`; fail closed on a missing key or a broken file; the deny rule is generated by a script), DEC-219 (DP-2: W1-46's test design covers the research exception). |

## 42. Standing rules of the orchestrator prompt v3, and owner answers on W1-47 and W1-08 (register v0.42, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04. Rules A, B and C are standing instructions carried by the orchestrator prompt v3
(`governance/project/prompts/w1-orchestrator.md`, commit `9ea35972`), sections 6 and 8. D and E answer the open
points on W1-47 (`DAEO-o4fg`) and W1-08 (`DAEO-uudf`).

### DEC-220 — Delegated decisions
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v3, section 6) · **Under:** MR-6 · **Amends:** DEC-093 (which packages reach the owner)
- **Decision:**
  - The orchestrator decides a package itself when all of these hold: it is P2 or P3; it is reversible; the
    orchestrator's recommendation and the proposer's (test designer, engineer, reviewer or product-spec worker)
    agree; confidence is medium or higher; it changes nothing in the Charter, the master rules, or the Contract's
    scope or waves; it doesn't weaken the guard or containment; it doesn't touch the held-out path, installs, merges
    or releases.
  - Each is recorded as ACCEPTED (orchestrator, delegated under DEC-220), applied, and listed in a short digest at
    the orchestrator's next stop. The owner may overturn any delegated decision.
  - Everything else goes to the owner as a decision package, at most five at a time; a P1 may bypass the cap.
  - While owner packages are open, the orchestrator continues with any other ready ticket whose work they don't
    affect, and doesn't stop just to deliver a digest.

### DEC-221 — Tests are proportional to the ticket's profile
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v3, section 8 and brief A1) · **Under:** MR-3, DEC-135
- **Decision:**
  - FULL: thorough. STANDARD: every KPI line's success and failure, plus the key edge cases. LITE: one test per KPI
    line.
  - No combinatorial expansion beyond what a KPI demands. Every covers id gets at least one test.

### DEC-222 — Archived sources may be read by a product-spec worker for a specification gap
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v3, section 6 and brief A4) · **Exception to:** Charter v5 principle 3, for specification gaps only · **Under:** DEC-058, DEC-082
- **Decision:**
  - When a KPI's source is only in the archived `docs/source/`, a product-spec worker (brief A4) may read it with
    `git show <SOURCES_COMMIT>:docs/source/<path>` (see `docs/SOURCES.md`) to draft the answer.
  - For a gap the worker writes nothing: it returns a draft answer with its sources, a recommendation and a
    confidence, as a decision package, which then follows DEC-220.

### DEC-223 — W1-47: DP-7, DP-8, a missing `held-out.yaml`, and reading the two holder files
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-47 packages DP-7 option 1 and DP-8 option 1, and on the orchestrator's report · **Under:** DEC-162, DEC-218
- **Decision:**
  - DP-7: the two static checks that compare the committed list with the implementation files and with the suite
    stay.
  - DP-8: an empty `held_out_paths` list fails closed, as built.
  - A missing `held-out.yaml` means no rule, as tested. W1-27 gets a KPI line (commit trailer `Task: DAEO-xw3k`) so
    that `gov doctor` reports a missing `held-out.yaml` in this repository.
  - Reading the two holder files (`governance/project/held-out.yaml` and `.claude/settings.json`) stays an accepted
    residual: seeing the path isn't seeing the oracle's contents. It is recorded in `governance/project/bootstrap.md`.
  - W1-47 is then closed.

### DEC-224 — W1-08 DP-1: the project floor lives in `path-map.yaml`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-08 package DP-1 option (a) · **Under:** CAP-06.e, CAP-54.b
- **Decision:**
  - The floor lives in `path-map.yaml`, under top-level keys of the path-map schema.
  - A product-spec worker (brief A4) drafts the capabilities, the policy strengths (an ordered list), the kernel
    minimum and the constitutional systems, from Contract v4.1, Charter v5 and the archived sources (DEC-222).
  - The draft follows DEC-220; it comes to the owner only if it changes scope or weakens a master rule.

### DEC-225 — W1-08 DP-2: namespace paths and memory class
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-08 package DP-2 option (a) · **Under:** CAP-06.a, CAP-03.b
- **Decision:**
  - `paths` is a list of patterns in the language of ticket `allowed_paths`.
  - Every tracked path matches exactly one namespace.
  - `memory_class` is `governance` or `product`.
  - W1-08's five held packages (DP-3 to DP-7) follow DEC-220 where they qualify.

| Version | Date | Change |
|---|---|---|
| 0.42 | 2026-10-04 | Orchestrator prompt v3 and owner answers: DEC-220 (delegated decisions), DEC-221 (proportional tests), DEC-222 (archived sources for specification gaps, brief A4), DEC-223 (W1-47: DP-7 the static checks stay; DP-8 an empty list fails closed; a missing `held-out.yaml` means no rule, with a W1-27 KPI line; reading the holder files is an accepted residual), DEC-224 (W1-08 DP-1: the floor lives in `path-map.yaml`, drafted by a product-spec worker), DEC-225 (W1-08 DP-2: `paths` patterns, exactly one namespace per tracked path, `memory_class`). |

## 43. Delegated decisions on W1-08's packages DP-5, DP-6 and DP-7 (register v0.43, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220. For each, the test designer's recommendation and the
orchestrator's agree, the confidence is medium or higher, the choice is reversible, and nothing in the Charter, the
master rules or the Contract's scope or waves changes. The owner may overturn any of them. DP-3 (identity field key
names) and DP-4 (`state_class` values) are not decided here: their sources are archived, so a product-spec worker
drafts the answers first (DEC-222).

### DEC-226 — W1-08 DP-5: a lesson's scope and severity are stored in lower case
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-5 option (a); test designer's confidence high · **Under:** DEC-168, CAP-41.c, CAP-41.f
- **Decision:** `scope` is `project`, `product` or `framework`, and `severity` is `low`, `medium`, `high` or
  `critical`, in lower case, as DEC-168 and CAP-41.f write them. The schema refuses the upper-case forms. CAP-41.c's
  upper-case spelling names the same three values; the Contract text is not changed.

### DEC-227 — W1-08 DP-6: one shared definitions file holds every id grammar
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-6 option (a); test designer's confidence medium-high
- **Decision:** One shared definitions file under `template/governance/kernel/schemas/` holds every id grammar under
  a fixed name (`ticket_id`, `wbs_id`, `decision_id`, `lesson_id`, `record_id`), and no other schema writes an id
  `pattern` of its own; the record schemas refer to it.

### DEC-228 — W1-08 DP-7: W1-27 makes `gov` validate the path map against the real schema
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-7 option (a), on W1-27; test designer's confidence medium · **Under:** DEC-185, DEC-189
- **Decision:**
  - W1-08 delivers the path-map schema and this repository's `path-map.yaml`, which must also fit the minimal shape
    the loader in `src/gov/config/` accepts. W1-08 does not change `src/gov/config/`.
  - W1-27 (`DAEO-xw3k`) replaces the minimal schema: it gets a KPI line and `src/gov/config/**` in its
    `allowed_paths`, in a commit with the trailer `Task: DAEO-xw3k`. Its test design makes the revisions of
    `tests/acceptance/W1-07/test_w1_07_config_details.py` that DEC-189 expects.

| Version | Date | Change |
|---|---|---|
| 0.43 | 2026-10-04 | Delegated under DEC-220: DEC-226 (W1-08 DP-5: lesson scope and severity in lower case), DEC-227 (W1-08 DP-6: one shared definitions file for the id grammars), DEC-228 (W1-08 DP-7: W1-27 replaces the minimal path-map schema in `src/gov/config/`). |

## 44. Delegated decisions on W1-08 from the product-spec drafts (register v0.44, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the drafts a product-spec worker returned for W1-08's
gaps (DEC-222, DEC-224; sources: the archived Framework v4.1.2 §3, §7, §20, §21 and Contract v3 W1, with DEC-012,
DEC-046, DEC-060 and API-0002). Two parts of the drafts are not decided here and go to the owner: the kernel minimum
per policy with the capability list (the worker's confidence is below medium), and the rewording of W1-08's KPI line
on the identity fields (it changes a KPI's meaning, and the worker asked for the owner).

### DEC-229 — W1-08 DP-4: `state_class` takes the six values of Framework §3
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-4 option (a) and the product-spec draft (confidence high for the values, medium for the per-type defaults) · **Under:** CAP-07.b, DEC-046
- **Decision:**
  - `state_class` is one of `AUTHORITATIVE`, `DERIVED`, `NARRATIVE`, `EVIDENCE`, `HISTORICAL`,
    `UNKNOWN_OR_CONFLICTING`, held once in the shared definitions file (DEC-227). Every record schema accepts all six.
  - The templates carry these defaults, which the schemas do not pin: decision, ticket, lesson, gate or decision
    package and path map `AUTHORITATIVE`; failure and research record `EVIDENCE`; checkpoint `NARRATIVE`.
  - Tickets carry it too: the 48 committed tickets each get `state_class: AUTHORITATIVE` in one orchestrator commit
    with the trailer `Task: DAEO-uudf`, and W1-09 adds the key when a ticket is created.

### DEC-230 — W1-08 DP-1, the parts that qualify: strengths, policy keys, systems and the shape in `path-map.yaml`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** DEC-224 and the product-spec draft option (a) (confidence high for the systems, medium for the shape) · **Under:** CAP-06.e, CAP-54.b, DEC-060
- **Decision:**
  - `path-map.yaml` gets three top-level keys beside `namespaces`: `capabilities`, `policies` and `systems`.
  - Policy strengths, weakest to strongest: `informational`, `warning`, `hard-block`.
  - `policies` has the thirteen policy keys of Framework §20, in lower case: `security`, `authority`, `test`,
    `change`, `human_gate`, `tool`, `memory`, `context`, `checkpoint`, `model_routing`, `budget`, `learning`,
    `archive`. All are required. The schema gives each key only the strengths at or above its kernel minimum, so the
    validator alone refuses a value below the floor.
  - `systems` has the twenty-two constitutional systems of Framework §7 as keys, all required:
    `constitution-and-policies`, `knowledge-fabric`, `repository-contract`, `agent-organisation`, `skills`,
    `tools-and-capabilities`, `command-surface`, `model-adapters`, `orchestration-and-handoffs`,
    `specification-and-planning`, `research-and-experiments`, `task-system`, `product-delivery`,
    `verification-and-governance-tests`, `change-impact-control`, `checkpoint-and-recovery`,
    `observability-and-cost`, `organisational-learning`, `independent-audit`, `security-and-permissions`,
    `budget-governance`, `emergency-stop-and-rollback`. Each has `status` (`implemented`, `minimal` or `absent`),
    `where` (at least one path pattern or tool name) unless absent, and `reason` when absent. That is what
    "identifies each constitutional system at least minimally" requires.
  - **Not decided here, with the owner:** the kernel minimum of each policy, and the list of capabilities.

| Version | Date | Change |
|---|---|---|
| 0.44 | 2026-10-04 | Delegated under DEC-220, from the product-spec drafts: DEC-229 (W1-08 DP-4: the six `state_class` values; tickets carry it), DEC-230 (W1-08 DP-1 in part: the three top-level keys, the strength order, the thirteen policy keys, the twenty-two systems; the kernel minimums and the capability list go to the owner). |

## 45. Delegated decisions on W1-46's test design packages (register v0.45, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the test designer's packages for W1-46 (`DAEO-jdqr`).
For each, the test designer's recommendation and the orchestrator's agree, the confidence is medium, and the choice
is reversible. The designer's "P1" on DP-1 and DP-2 marks how much they block the tests; neither is a breach or a
loss, and the orchestrator ranks them P2. DP-4 (the install exception), DP-5 (the allowlist file) and DP-7 (three
refusal cases) are not decided here: they touch installs, the network grant or the held-out file, or the designer's
confidence is low. They go to the owner.

### DEC-231 — W1-46 DP-1: the command line of `gov launch`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-1 option (a); the WBS and the orchestrator prompt already write `gov launch <role> <ticket>` · **Under:** DEC-161
- **Decision:** `gov launch <role> <ticket> [-- <arguments for the CLI>]`. The role and the ticket are positional;
  everything after `--` is passed to the CLI unchanged, which is how a headless worker gets `-p` and its prompt.

### DEC-232 — W1-46 DP-2: the "launched worker" lines are tested with two short real sessions
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-2 option (a) · **Under:** CAP-61.b, DEC-221
- **Decision:**
  - The KPI lines that say "an acceptance test shows that a launched worker …" are tested with two short real
    headless sessions per run (one engineer, one research), started through `gov launch`, marked `local_only`, on
    the cheapest model with a turn limit. The sandbox is inside the CLI, so nothing else exercises it.
  - A run in which the model does not execute the stated command fails with that reason and is repeated; it is not
    a finding against the launcher.
  - They are not put behind an opt-in variable, so that the ticket cannot close on skipped tests.

### DEC-233 — W1-46 DP-3: a sandbox block in the repository's settings makes `gov launch` refuse
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-3 option (a); it fails closed · **Under:** CAP-61.a, DEC-161
- **Decision:** `gov launch` refuses to start, with a non-zero exit and a named reason, when the repository's
  `.claude/settings.json` or `.claude/settings.local.json` carries a `sandbox` key, because the CLI may merge
  repository settings into the ones the launcher builds.

### DEC-234 — W1-46 DP-6: the per-session temp directory test keeps its assertion
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-6 option (a) · **Under:** DEC-159, CAP-61.d
- **Decision:** The live test asserts that each session's temp files land in a directory of its own. If the CLI
  cannot be made to do that, the orchestrator records the shared `$TMPDIR` as a residual in
  `governance/project/bootstrap.md`, as the KPI says, and the test designer revises the test to assert the residual
  (a planned revision).

| Version | Date | Change |
|---|---|---|
| 0.45 | 2026-10-04 | Delegated under DEC-220: DEC-231 (W1-46 DP-1: `gov launch <role> <ticket> [-- <CLI arguments>]`), DEC-232 (W1-46 DP-2: two short real sessions, `local_only`, not opt-in), DEC-233 (W1-46 DP-3: a `sandbox` key in the repository's settings makes the launcher refuse), DEC-234 (W1-46 DP-6: the temp-directory assertion stays; a residual if the CLI can't). |

## 46. Parallel tickets, ticket leads, and owner answers on W1-08 and W1-46 (register v0.46, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04. DEC-235 to DEC-237 are standing rules carried by the orchestrator prompt v4
(`governance/project/prompts/w1-orchestrator.md`, commit `e4dc57ce`), sections 3, 4, 5 and 7 and brief A5. DEC-238
to DEC-242 answer the five open packages on W1-08 (`DAEO-uudf`) and W1-46 (`DAEO-jdqr`). DEC-243 accepts the digest.

### DEC-235 — Parallel tickets in Wave 1 (a light form of CAP-23)
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 3) · **Under:** CAP-23, DEC-076 · **Amends:** the Wave 3 placing of parallel work, for this light form only; DEC-183 (a worker starts in its ticket's worktree, not the repository root)
- **Decision:**
  - Up to 6 tickets are in flight at once, each in its own short-lived worktree
    (`~/gov-os-worktrees/<W1-id>`, branch `w1/<W1-id>`, cut from `w1/integrate`). A ticket starts only when its
    dependencies are closed and its `allowed_paths` overlap no ticket in flight; overlapping tickets wait.
  - Resource gate, checked before each start: at least 4 GiB of memory available (`free -g`) and a 1-minute load
    average below the number of CPU cores. Heavy tickets (retrieval, indexing, models) count double. WSL now has
    24 GB (the owner's change to `.wslconfig`).
  - The main orchestrator merges a ticket's branch into `w1/integrate` after green, in the main tree, and re-runs
    every acceptance suite and the builder tests after each merge. Only then is the ticket closed, its worktree
    removed and its branch deleted. No worktree is left behind.
  - The full claims and concurrency capability, with the claims role and `gov claim` (CAP-23.b), stays in Wave 3.
  - The Contract gets a Wave 1 covers item under CAP-23 for this light form. The validator needs a provider ticket
    and a KPI line for every Wave 1 covers item; the orchestrator puts it on W1-42 (`DAEO-gjjf`), whose exit report
    shows it. That choice of provider is the orchestrator's, not the owner's, and the owner may move it.

### DEC-236 — Two-level orchestration: the main orchestrator and a ticket lead per ticket
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, sections 3 to 5 and brief A5) · **Under:** MR-5, DEC-096, DEC-156
- **Decision:**
  - The main orchestrator runs the wave: it chooses and claims tickets, starts a ticket lead for each, merges and
    re-verifies, makes delegated decisions (DEC-220) and brings the owner the rest. It reads only a lead's final
    summary, never its workers' output.
  - A ticket lead runs the ticket loop for one ticket in that ticket's worktree, as `GOV_ROLE=orchestrator` with
    the ticket in `GOV_TICKET`. It starts the workers, holds that ticket's loop count and never discloses it.
  - A lead never edits `.tickets/`, the decision register or `bootstrap.md`, never merges into `w1/integrate` and
    never pushes. It returns DONE, PACKAGES, ESCALATION or LEAD_CHECKPOINT.
  - Tickets, claims, the register and `bootstrap.md` are edited only by the main orchestrator, in the main tree.

### DEC-237 — Context limits for the main orchestrator and the ticket leads
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 7 and brief A5) · **Amends:** DEC-208
- **Decision:**
  - The main orchestrator stops with `CONTEXT_CHECKPOINT` at about 300k tokens, after a merge or a close. Leads
    keep running in their worktrees.
  - Each ticket lead, at about 300k tokens, writes `.gov-runtime/scratch/lead/CHECKPOINT.md` in its worktree and
    returns `LEAD_CHECKPOINT`; a fresh lead in the same worktree resumes from it.

### DEC-238 — W1-08: the kernel minimum per policy, and the capability list
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1-08 package, option (a), as the product-spec worker drafted it · **Under:** DEC-224, DEC-230, CAP-06.e, CAP-54.b
- **Decision:**
  - Kernel minimum: `hard-block` for `security`, `authority`, `test`, `change`, `human_gate` and `tool`; `warning`
    for `memory`, `context` and `checkpoint`; `informational` for `model_routing`, `budget`, `learning` and
    `archive`.
  - `capabilities` is a closed list of two: `code_intelligence` (with `languages`) and `research_corpus`.

### DEC-239 — W1-08 DP-3: the identity field keys, and the KPI line's wording
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-08 package DP-3 option (a), as drafted · **Under:** CAP-50.a
- **Decision:**
  - Shared frontmatter: `id`, `type` and `status` required; `lifecycle`, `version`, `provenance`, `supersedes`,
    `superseded_by` and `consumers` optional. The canonical path and `content_hash` are derived by `gov`, not
    stored.
  - W1-08's KPI line is reworded from "are in the shared frontmatter" to "are in the shared frontmatter or derived
    by gov", in its own commit with the trailer `Task: DAEO-uudf`.

### DEC-240 — W1-46 DP-4: when a research install is inside its experiment folder
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-4 option (a) · **Under:** DEC-163, DEC-174, CAP-25.e
- **Decision:**
  - A research install is inside its experiment folder when the session's working directory is the folder or below
    it, or the command first changes into it with `cd`.
  - `uv --directory` and `uv --project` are not followed by the rule. The reviewer probes them, as a described
    behaviour (DEC-136).

### DEC-241 — W1-46 DP-5: the research allowlist file and its starting hosts
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-5 option (a) · **Under:** DEC-158, DEC-163, CAP-61.c
- **Decision:**
  - `governance/project/research-allowlist.yaml` extends the kernel default. The owner extends the list. That path
    is added to W1-46's `allowed_paths`, in its own commit with the trailer `Task: DAEO-jdqr`.
  - Starting hosts: `github.com`, `api.github.com`, `raw.githubusercontent.com`, `objects.githubusercontent.com`,
    `codeload.github.com`, `pypi.org`, `files.pythonhosted.org`, `registry.npmjs.org`, `huggingface.co`,
    `cdn-lfs.huggingface.co`, `arxiv.org`, `export.arxiv.org`, `docs.python.org`, `docs.rs`, `crates.io`,
    `static.crates.io`, `developer.mozilla.org`, and the subdomains of `readthedocs.io`.
  - The launcher's acceptance test must show that the sandbox accepts these entries; EXP-001 tested only an empty
    list.

### DEC-242 — W1-46 DP-7: when `gov launch` refuses, and a missing `held-out.yaml`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-7 · **Under:** DEC-161, DEC-163, DEC-223
- **Decision:**
  - `gov launch` refuses to launch for an unknown ticket, a ticket that isn't `in_progress`, or a ticket of another
    role.
  - It refuses a research ticket whose `allowed_paths` isn't exactly one experiment folder.
  - It launches normally when `held-out.yaml` is missing: no held-out rule, consistent with the guard (DEC-223). A
    product repository without a qualification oracle must still be able to launch workers.

### DEC-243 — The digest of delegated decisions DEC-226 to DEC-234 is accepted
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the orchestrator's digests · **Under:** DEC-220
- **Decision:** DEC-226 to DEC-234 stand as recorded, including the orchestrator's ranking of W1-46's DP-1 and DP-2
  as P2.

| Version | Date | Change |
|---|---|---|
| 0.46 | 2026-10-04 | Orchestrator prompt v4 and owner answers: DEC-235 (parallel tickets in Wave 1, a light form of CAP-23: up to 6 in flight, one worktree each, a resource gate, merges by the main orchestrator with every suite re-run), DEC-236 (main orchestrator and ticket leads), DEC-237 (context limits, about 300k tokens for each), DEC-238 (W1-08: kernel minimums and the two capabilities), DEC-239 (W1-08 DP-3: identity keys; KPI line reworded), DEC-240 (W1-46 DP-4: inside the experiment folder), DEC-241 (W1-46 DP-5: `research-allowlist.yaml` and its starting hosts), DEC-242 (W1-46 DP-7: refusals; a missing `held-out.yaml` launches), DEC-243 (digest DEC-226…DEC-234 accepted). |

## 47. Delegated decisions on W1-37's test design packages (register v0.47, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the four packages the W1-37 (`DAEO-yvzh`) ticket lead
returned from its test designer. For each, the designer's, the lead's and the orchestrator's recommendations agree,
the confidence is medium or higher, and the choice is reversible before W1-38. One part of DP-2 is not decided here
and goes to the owner: whether a version recorded beside the vendored files satisfies CAP-24's "every skill file
carries a version in frontmatter" for vendored skills. It reads the Contract, so it is the owner's.

### DEC-244 — W1-37 DP-1: the three skills are copied from the vendor folder into the skills path
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-1 option (a); confidence medium · **Under:** DEC-074 Q5, DEC-194
- **Decision:** W1-37 copies the three skill folders (`SKILL.md` and its supporting files) from
  `template/governance/kernel/vendor/superpowers/skills/` into `template/governance/kernel/skills/superpowers/<skill>/`.
  The vendor folder stays unchanged and is the only source; the skills folder is the path W1-38 registers.

### DEC-245 — W1-37 DP-2, in part: "namespaced" means the folder
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-2 option (a); confidence medium · **Under:** DEC-074 Q5
- **Decision:**
  - The namespace is the folder `skills/superpowers/<skill>/`. The copied files stay byte-identical to the vendor
    copy, so the hash check is a plain byte comparison.
  - The source version, v6.4.2, is recorded beside the files, in the record of DEC-246.
  - **Not decided here, with the owner:** whether that record satisfies CAP-24's version in frontmatter for
    vendored skills. If the owner wants the version in each `SKILL.md`, the copies change and the hash rule with
    them, as a revision of this ticket's tests.

### DEC-246 — W1-37 DP-3: the source hash is recorded in a file beside the copied skills
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-3 option (b); confidence medium · **Under:** DEC-199
- **Decision:** A record file inside `template/governance/kernel/skills/superpowers/` carries the source version,
  the vendor folder's digest by the DEC-199 rule, and the digest of the copy by the same rule. A test recomputes
  both offline. The tool registry is not changed.

### DEC-247 — W1-37 DP-4: how the token sizes are measured against the I-09 figures
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-4 option (a); confidence high on the mapping and the formula, medium on "within" as a ceiling · **Under:** DEC-074 Q5
- **Decision:**
  - A skill's size is floor(characters ÷ 4) of its `SKILL.md` alone, measured on the copy under
    `skills/superpowers/`. Each is at or below its figure: test-driven-development 2,389, systematic-debugging
    2,360, verification-before-completion 899. No tolerance.
  - The figures 8,089 and 795 of DEC-074 belong to nothing this ticket vendors and are not asserted.
  - The measured sizes go in the record of DEC-246.

| Version | Date | Change |
|---|---|---|
| 0.47 | 2026-10-04 | Delegated under DEC-220: DEC-244 (W1-37 DP-1: copy from the vendor folder into `skills/superpowers/`), DEC-245 (W1-37 DP-2 in part: the namespace is the folder, files byte-identical; the CAP-24 version question goes to the owner), DEC-246 (W1-37 DP-3: a record file beside the copies, by the DEC-199 rule), DEC-247 (W1-37 DP-4: floor(characters ÷ 4) of `SKILL.md`, at or below the three figures). |

## 48. Owner decisions: auto-resume hooks (W1-49), the mid-wave audit, and stops (register v0.48, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04, given during the parallel run.

### DEC-248 — New ticket W1-49: light auto-resume hooks (a light form of CAP-37)
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** CAP-37, DEC-025, DEC-208, DEC-237 · **Amends:** the Wave 1 ticket set (48 → 49 tickets)
- **Decision:**
  - A new ticket, W1-49, delivers light auto-resume hooks, a light form of CAP-37 brought forward by the owner.
    W1-29 later upgrades the injection to the full context packet.
  - Role engineer, profile FULL, priority high, no dependency on an open ticket. It runs with priority, in parallel
    with the tickets in flight.
  - KPIs:
    - (a) a PreCompact hook ensures the orchestrator's checkpoint is current, and in a worktree the lead's;
    - (b) a SessionStart hook on compact, clear and resume injects, within the hook's size cap, the prompt path and
      the checkpoint's RESUME HERE section, with the instruction to read both now;
    - (c) the auto-compact threshold is set to about 300k tokens (30 % of the window) if Claude Code allows it to
      be configured. An acceptance test proves whether it can. If it can't, a residual is recorded: the
      `CONTEXT_CHECKPOINT` stop stays;
    - (d) after a forced compaction (`/compact`), the session's next action shows it knows the active tickets, the
      open owner decisions and the loop counts, without the owner restating them.
  - Allowed paths: `template/governance/kernel/hooks/precompact*`, `template/governance/kernel/hooks/sessionstart*`,
    `.claude/settings.json` (hook registration and any env key, under this decision), `tests/unit/hooks/**`.
  - The Contract gets a Wave 1 covers item under CAP-37 for the light form, in its own commit.
  - Written by the orchestrator to make the ticket valid, not by the owner, and open to the owner's change: the
    dependency on W1-05 (closed; it placed the hook wiring), the estimate of 120 LOC, and the failure KPI lines,
    which mirror the success lines.

### DEC-249 — Mid-wave audit when W1-21 is merged
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** MR-4, DEC-088, DEC-220
- **Decision:**
  - When W1-21 (`gov retrieve`) is merged, a fresh read-only independent auditor, in its own worktree and writing
    to no ticket, checks every ticket closed so far against Contract v4.1 and its covers items, and reports
    findings.
  - Findings follow the delegation rule (DEC-220); owner-level ones come to the owner.

### DEC-250 — Stops after W1-49 closes
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Amends:** DEC-237, DEC-208 (the main orchestrator's `CONTEXT_CHECKPOINT` stop)
- **Decision:**
  - Until W1-49 closes, the `CONTEXT_CHECKPOINT` stop stays.
  - After W1-49 closes, the orchestrator stops only for owner-level decision packages (P1, and everything the
    delegation rule reserves for the owner), for escalations, and for `WAVE_1_EXIT_READY`. Context is handled by
    auto-compaction with the W1-49 hooks.
  - When W1-49 closes, the orchestrator tells the owner, so that the operator can update section 7 of the
    orchestrator prompt. The orchestrator does not edit the prompt.
  - If KPI (c) of W1-49 ends in the residual (the threshold can't be configured), the orchestrator says so in the
    same message, because the `CONTEXT_CHECKPOINT` stop then stays by DEC-248.

| Version | Date | Change |
|---|---|---|
| 0.48 | 2026-10-04 | Owner decisions: DEC-248 (new ticket W1-49, light auto-resume hooks, a light form of CAP-37; engineer, FULL, priority high), DEC-249 (a mid-wave audit by a fresh read-only independent auditor when W1-21 is merged), DEC-250 (after W1-49 closes the orchestrator stops only for owner-level packages, escalations and `WAVE_1_EXIT_READY`). |

## 49. Delegated decisions on W1-08's packages DP-8 and DP-9 (register v0.49, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the two packages the W1-08 (`DAEO-uudf`) ticket lead
returned after implementation. For each, the proposer's recommendation and the orchestrator's agree, the confidence
is medium or higher, and the choice is reversible: no reader of either key exists yet.

### DEC-251 — W1-08 DP-8: the value of a `capabilities` entry
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-8 option (a), the test designer's and the lead's recommendation; confidence medium-high for the shape, medium for "both required" · **Under:** DEC-238, CAP-06.e
- **Decision:** Both keys, `code_intelligence` and `research_corpus`, are required. Each is a closed map with a
  required boolean `enabled`. `code_intelligence` also has `languages`, a non-empty list of strings when it is
  enabled. The path map already has this form; the schema is tightened to it, after a short test design round.

### DEC-252 — W1-08 DP-9: the lesson id grammar is the carried form
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-9 option (a), the lead's recommendation; confidence medium-high · **Under:** DEC-227, CAP-41.d
- **Decision:** `lesson_id` is `^L-[0-9]{4,}$`, the form of the carried lesson `L-0074`, in the shared definitions
  file and the lesson template. W1-44 carries the Phase-2 lessons without renumbering.

| Version | Date | Change |
|---|---|---|
| 0.49 | 2026-10-04 | Delegated under DEC-220: DEC-251 (W1-08 DP-8: both capabilities required, each a closed map with a boolean `enabled`; `languages` non-empty when `code_intelligence` is enabled), DEC-252 (W1-08 DP-9: `lesson_id` is `^L-[0-9]{4,}$`). |

## 50. Owner decisions: integration merges, the W1-01 history test, and containment by commit trailers (W1-50) (register v0.50, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04, on the orchestrator's P1 package (the W1-37 merge commit `00e3d539` made
`test_only_the_test_designer_commits_to_acceptance_tests` of W1-01 fail) and its package on containment findings.

### DEC-253 — The W1-01 history test accepts an integration merge of test-designer commits
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the P1 package, option (a) · **Under:** MR-3, DEC-235, DEC-106
- **Decision:**
  - A test designer revises `test_only_the_test_designer_commits_to_acceptance_tests` so that an integration merge
    commit passes when every change it brings under `tests/acceptance/` comes from commits on the merged side
    carrying `Role: independent-test-designer`.
  - Every non-merge commit is still checked exactly as now.
  - The revision is recorded as a rewrite after implementation, reason "owner decision: integration merges".

### DEC-254 — Merge findings and worker-commit misattributions are records, for now
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the containment package, option (a) · **Under:** DEC-171, DEC-235, DEC-206
- **Decision:** Until W1-50 is built, a containment finding raised by an integration merge of the main
  orchestrator, and a finding that attributes a worker's commit to the call of the lead that was waiting for it, are
  records of permitted actions. They are noted in `governance/project/bootstrap.md` and in each ticket's close row;
  they are not defects.

### DEC-255 — New ticket W1-50: containment attribution by commit trailers
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** CAP-58, DEC-076, DEC-182, DEC-235 · **Amends:** the Wave 1 ticket set (49 → 50 tickets)
- **Decision:**
  - A new ticket, W1-50: role engineer, profile FULL, priority high, depends on W1-03.
  - KPIs:
    - a forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit: each
      commit's paths against the allowed paths of its own `Role` and `Task` trailers, not against the caller;
    - a merge commit itself is not a finding when every commit it brings passes that check;
    - a worker's commit made during another actor's call is judged by its own trailers;
    - a commit with no `Role` or `Task` trailer is judged against the caller, as today.
  - Allowed paths: `src/gov/guard/containment*`, `template/governance/kernel/hooks/posttooluse*`,
    `template/governance/kernel/hooks/pretooluse*`, `tests/unit/containment/**`.
  - Its test design batch also carries the W1-01 revision of DEC-253.
  - The Contract gets a covers item under CAP-58, in its own commit.
  - Written by the orchestrator to make the ticket valid, and open to the owner's change: the estimate of 100 LOC
    and the failure KPI lines, which mirror the success lines.

### DEC-256 — Order of work around W1-50
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** DEC-235
- **Decision:**
  - W1-50 is claimed now, and only its test design batch runs, in its own worktree.
  - That batch is merged, with the revised W1-01 test included.
  - The orchestrator confirms W1-01 is green on `w1/integrate` (the W1-37 merge then passes).
  - Merges and closes resume, W1-37 included.
  - W1-50's implementation starts after W1-46 is merged, because both touch `src/gov/guard/**`.

| Version | Date | Change |
|---|---|---|
| 0.50 | 2026-10-04 | Owner decisions: DEC-253 (the W1-01 history test accepts an integration merge whose acceptance-test changes all come from test-designer commits; a rewrite after implementation, "owner decision: integration merges"), DEC-254 (merge findings and worker-commit misattributions are records for now), DEC-255 (new ticket W1-50, containment attribution by commit trailers; engineer, FULL, priority high, depends on W1-03), DEC-256 (W1-50's test batch first and merged; then merges and closes resume; its implementation after W1-46). |

## 51. Delegated decision on W1-18's package DP-3 (register v0.51, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on one of the three packages the W1-18 (`DAEO-1ve2`) ticket
lead returned. The designer's, the lead's and the orchestrator's recommendations agree, the confidence is medium, and
the choice is reversible: W1-19 and W1-21, the only callers, are not written. DP-1 (the module's public interface) and
DP-2 (whether `gov` stops the daemon) are not decided here and go to the owner: on DP-1 the confidence in the names is
low and it changes the ticket's `allowed_paths`; DP-2 sets aside a phrase of ADR-0002.

### DEC-257 — W1-18 DP-3: "the facet state recorded" is the state in the module's result
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-18 package DP-3 option (a); confidence medium · **Under:** DEC-033, DEC-034, DEC-037, DEC-074 Q4
- **Decision:**
  - When Ollama is unavailable, the lifecycle module's result names the facet `semantic`, the state
    `FACET_UNAVAILABLE` and a non-empty warning that names Ollama and says results are FTS-only. The warning is
    also written once to standard error. No file is written.
  - The module reports the state; it does not set a bundle's stopping reason. W1-21 copies the state into the
    bundle, and how an FTS-only bundle's stopping reason (CAP-55) relates to it is settled there.
  - The form in which the result is returned follows the owner's answer on DP-1.

| Version | Date | Change |
|---|---|---|
| 0.51 | 2026-10-04 | Delegated under DEC-220: DEC-257 (W1-18 DP-3: facet `semantic`, state `FACET_UNAVAILABLE` and a warning in the module's result and on standard error; no file). |

## 52. Delegated decisions on W1-49's packages DP-1 and DP-2 (register v0.52, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on two of the three packages the W1-49 (`DAEO-32n6`) ticket
lead returned from its test design. For each, the designer's, the lead's and the orchestrator's recommendations
agree, the confidence is medium or higher, and the choice is reversible: W1-29 replaces both hook files. DP-3 (the
prompt path injected for a ticket lead) is not decided here: the designer and the lead recommend differently, so it
goes to the owner. Meanwhile the suite stands as the designer wrote it (option (a): in a worktree, the lead
checkpoint's path and its RESUME HERE section only), and the owner's answer may add one assertion.

### DEC-258 — W1-49 DP-1: what "ensures the checkpoint is current" means for a PreCompact hook
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-1 option (a) with measure (i); confidence medium-high on the option, medium on the 30 minutes · **Under:** DEC-248, CAP-37.g
- **Decision:**
  - A hook can check and block; it cannot write the checkpoint's content. The checkpoint is current when its file
    is at most 30 minutes old.
  - On a manual compaction over a checkpoint that is not current, the hook blocks (exit 2) and says why.
  - On an automatic compaction it lets the compaction through and tells the user, and the SessionStart injection
    after it says `CHECKPOINT NOT CURRENT` with the path.
  - **Known gap, told to the owner:** an automatic compaction over a stale checkpoint still proceeds; the session
    is told only afterwards. With auto-compaction replacing the `CONTEXT_CHECKPOINT` stop (DEC-250) that is the
    common case, and it rests on the orchestrator and the leads rewriting their checkpoint after every merge,
    close and stop, as the prompt's section 1 already asks of the orchestrator.

### DEC-259 — W1-49 DP-2: the hooks act only for the orchestrator role
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-2 option (a); confidence high · **Under:** DEC-248, DEC-096, DEC-236
- **Decision:** The PreCompact and SessionStart hooks act only when `GOV_ROLE` is `orchestrator` (the main
  orchestrator and the ticket leads). A worker session gets no injection and is not blocked: the lead's checkpoint
  holds the loop count, which no session inside the loop may see. An unset `GOV_ROLE` is not the orchestrator.

| Version | Date | Change |
|---|---|---|
| 0.52 | 2026-10-04 | Delegated under DEC-220: DEC-258 (W1-49 DP-1: current means at most 30 minutes old; a manual compaction is blocked, an automatic one goes through with a notice and a `CHECKPOINT NOT CURRENT` line after it), DEC-259 (W1-49 DP-2: the hooks act only for `GOV_ROLE=orchestrator`). DP-3 goes to the owner. |

## 53. Owner answers on W1-18, W1-37 and W1-49 (register v0.53, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04, on the three packages the orchestrator presented (W1-18 DP-1 and DP-2, the CAP-24
version question of W1-37), on W1-49's DP-3, and on the gap the orchestrator reported in DEC-258.

### DEC-260 — W1-18 DP-1: the public interface of the Ollama lifecycle module
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-18 package DP-1 option (a), with both riders · **Under:** DEC-074 Q4, G-22
- **Decision:**
  - One function, `gov.retrieval.ollama.ensure_available(*, timeout_s, env=None)`. It returns `available`,
    `started`, `facet`, `state` and `warning`, and never raises when the daemon is unavailable.
  - The executable comes from `GOV_OLLAMA_BIN`, then `ollama` on `PATH`, then `~/.local/ollama/bin/ollama`.
  - The endpoint comes from `OLLAMA_HOST` (default `127.0.0.1:11434`); healthy means `GET /api/version` answers 200.
  - The default total deadline is 20 s.
  - `src/gov/retrieval/__init__.py` is added to W1-18's `allowed_paths`, in its own commit with the trailer
    `Task: DAEO-1ve2`.

### DEC-261 — W1-18 DP-2: `gov` starts the daemon and never stops it
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-18 package DP-2 option (a) · **Under:** DEC-074 Q4, ADR-0002 §3
- **Decision:**
  - `gov` starts `ollama serve` on demand and never stops it. Ollama's 5-minute idle unload frees the model's GPU
    memory, which was the owner's intent.
  - W1-18 delivers "started by `gov`", not "stopped by `gov`" (ADR-0002 §3). This is an accepted difference,
    recorded in `governance/project/bootstrap.md`. The ADR is not changed.

### DEC-262 — The owner's reading of CAP-24 for vendored skills
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1-37 question left open by DEC-245, option (a) · **Under:** CAP-24, DEC-245, DEC-246
- **Decision:**
  - For a vendored skill, the version recorded beside it (`vendored.yaml`) satisfies CAP-24. The copies stay
    byte-identical to upstream.
  - This is the owner's reading of CAP-24 for vendored skills; the Contract's text is not changed.
  - It is noted in W1-30's brief: `gov close` reads a vendored skill's version from the record beside it.

### DEC-263 — W1-49 DP-3: the SessionStart injection is role-specific
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-49 package DP-3 option (b), role-specific · **Under:** DEC-248, DEC-236, CAP-37.g
- **Decision:**
  - In the main tree, the injection points to the orchestrator prompt and the orchestrator's checkpoint.
  - In a worktree, it says "you are the ticket lead for <ticket>; read appendix A5 of
    governance/project/prompts/w1-orchestrator.md and your checkpoint", plus the lead checkpoint's RESUME HERE
    section.

### DEC-264 — The PreCompact hook never blocks; it appends a generated state block
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the gap reported with DEC-258 · **Amends:** DEC-258 (no compaction is blocked; "current" is no longer a 30-minute age) · **Under:** DEC-248, DEC-250, CAP-37.g
- **Decision:**
  - The PreCompact hook doesn't block a compaction. It appends a generated state block to the checkpoint: the git
    head, the tickets in progress from `tk`, the worktree list and the pending owner decisions.
  - The SessionStart injection warns when the checkpoint's written part is older than that block, and tells the
    session to re-derive state from git and the tickets before acting.
  - This is added to W1-49's KPIs, in its own commit with the trailer `Task: DAEO-32n6`.
  - The tests that assert a blocked manual compaction are revised by a test designer, as rewrites after
    implementation where the implementation exists by then, reason "owner decision, DEC-264".

| Version | Date | Change |
|---|---|---|
| 0.53 | 2026-10-04 | Owner answers: DEC-260 (W1-18 DP-1: `ensure_available`, executable and endpoint lookup, 20 s total deadline, `src/gov/retrieval/__init__.py` in the ticket's paths), DEC-261 (W1-18 DP-2: `gov` starts the daemon and never stops it; accepted difference from ADR-0002 §3), DEC-262 (CAP-24 for vendored skills: the version in `vendored.yaml` is enough), DEC-263 (W1-49 DP-3: role-specific injection), DEC-264 (the PreCompact hook never blocks and appends a generated state block; amends DEC-258). |

## 54. Delegated decision on W1-08's package DP-10 (register v0.54, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the package the W1-08 (`DAEO-uudf`) ticket lead returned
with its DONE. The designer's, the repair worker's, the lead's and the orchestrator's recommendations agree, the
confidence is medium-high, and the choice is reversible: no reader of the key exists yet.

### DEC-265 — W1-08 DP-10: `languages` is required only when `code_intelligence` is enabled
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-10 option (a); confidence medium-high · **Under:** DEC-251, CAP-06.e
- **Decision:** When `code_intelligence` has `enabled: true`, `languages` is required and is a non-empty list of
  strings. When it has `enabled: false`, `languages` may be left out or be any list of strings. The schema is
  already written this way. The one test case for the disabled form goes to the next test design batch that
  touches the path-map schema (W1-27, DEC-228), as a described behaviour.

| Version | Date | Change |
|---|---|---|
| 0.54 | 2026-10-04 | Delegated under DEC-220: DEC-265 (W1-08 DP-10: `languages` is required only when `code_intelligence` is enabled; the test case goes to W1-27's test design). |

## 55. Delegated decisions on W1-50's test design packages (register v0.55, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on five of the seven packages the W1-50 (`DAEO-xnbx`)
ticket lead returned with its test design batch. For each, the designer's, the lead's and the orchestrator's
recommendations agree, the confidence is medium or higher, the choice is reversible, and it never lets through
something today's containment check flags without the commit's own trailers allowing it. DP-4 (trailers naming a
ticket that is closed or not started) and DP-5 (a worker's call that makes a commit carrying another role's
trailers) are not decided here: they set how strong containment is, and on DP-4 the confidence is low. They go to
the owner.

### DEC-266 — W1-50 DP-1: only a merge in the orchestrator's own call is judged commit by commit
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-1 option (a); confidence high · **Under:** DEC-255, CAP-58.h
- **Decision:** A non-fast-forward merge is judged commit by commit only when it is made in an orchestrator
  session's own call (the main orchestrator's integration merge, or a lead taking `w1/integrate` into its ticket
  branch). A merge in any other caller's call stays flagged, as W1-03 tests it.

### DEC-267 — W1-50 DP-2: own-trailer judging needs both trailers in the final block
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-2 option (a); confidence medium-high · **Under:** DEC-255, DEC-182
- **Decision:** A commit is judged by its own trailers only when its final trailer block carries both `Role` and
  `Task`. A commit with one of the two, or with `Role:` and `Task:` lines only in the message body, is judged
  against the caller, as today.

### DEC-268 — W1-50 DP-3: trailers that name nothing valid allow nothing
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-3 option (a), the fail-closed reading; confidence medium · **Under:** DEC-255
- **Decision:** When a commit's trailers name an unknown role, an unknown ticket, a role that is not the ticket's,
  or several different `Role` or `Task` values, the commit has no allowed paths and every path it changes is a
  finding. A ticket is found by its `id` or its `wbs_id`, as the guard does.

### DEC-269 — W1-50 DP-6: a path the merge commit itself changes is judged by the merge commit's trailers
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-6 option (a); confidence medium-high · **Under:** DEC-255, DEC-156, DEC-253
- **Decision:** A path a merge commit changes beyond what its parents hold (a conflict resolution, a hand edit) is
  judged by the merge commit's own trailers, or against the caller when it has none. An orchestrator's conflict
  resolution under `tests/acceptance/**` is therefore a finding, and elsewhere it is not.

### DEC-270 — W1-50 DP-7: the finding record keeps the caller's role and ticket
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-7 option (a); confidence medium · **Under:** DEC-122, DEC-255
- **Decision:** In a finding for a commit judged by its trailers, `role` and `ticket` hold the caller's values, as
  today; the commit id and its trailers are named in `reason`.

| Version | Date | Change |
|---|---|---|
| 0.55 | 2026-10-04 | Delegated under DEC-220: DEC-266 (W1-50 DP-1: only the orchestrator's own merge is judged commit by commit), DEC-267 (DP-2: both trailers, in the final block), DEC-268 (DP-3: invalid trailers allow nothing), DEC-269 (DP-6: a merge commit's own changes are judged by its trailers), DEC-270 (DP-7: the finding keeps the caller's role and ticket). DP-4 and DP-5 go to the owner. |

## 56. Delegated decisions on W1-46's packages DP-8, DP-9 and DP-13 (register v0.56, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on three of the nine packages the W1-46 (`DAEO-jdqr`)
ticket lead returned after implementation and review. For each, the lead's recommendation and the orchestrator's
agree, the confidence is medium, the choice is reversible, and none loosens the guard, the sandbox or the network
grant. The other six go to the owner: DP-10, DP-11, DP-12, DP-14 and DP-16 are P1 or set how strong the sandbox and
the guard are; DP-15 changes the owner's list of research hosts.

### DEC-271 — W1-46 DP-8: which tickets each role may be launched on
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-8 option (a); confidence medium · **Under:** DEC-242, DEC-161
- **Decision:** `gov launch` starts an engineer or a research session only on a ticket of its own role. An
  independent test designer and an independent auditor are launched on any ticket that is `in_progress`: their work
  is always on another role's ticket. This is how "a ticket of another role" in DEC-242 is read.

### DEC-272 — W1-46 DP-9: the key of `research-allowlist.yaml`, and a project without the file
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-9 option (a); confidence medium · **Under:** DEC-241
- **Decision:** The list is under the key `hosts`. A project without `governance/project/research-allowlist.yaml`
  launches a research session on the kernel default alone: no file means no extension. One test covers the missing
  file.

### DEC-273 — W1-46 DP-13: an experiment folder lies under a root the project names
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-13 option (a); confidence medium · **Under:** DEC-242, DEC-163
- **Decision:** The one folder of a research ticket must lie under a root the project names, `experiments/` by
  default. `gov launch` refuses a research ticket whose folder is anywhere else, so a research ticket on `.claude/`,
  `.tickets/`, `governance/project/`, `src/` or `.git/` does not launch.

| Version | Date | Change |
|---|---|---|
| 0.56 | 2026-10-04 | Delegated under DEC-220: DEC-271 (W1-46 DP-8: engineer and research on their own role's ticket; test designer and auditor on any ticket in progress), DEC-272 (DP-9: key `hosts`; no project file means the kernel default alone), DEC-273 (DP-13: an experiment folder lies under a named root, `experiments/` by default). DP-10, DP-11, DP-12, DP-14, DP-15 and DP-16 go to the owner. |

## 57. Delegated decisions on W1-10's test design packages (register v0.57, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on five of the six packages the W1-10 (`DAEO-4yyl`) ticket
lead returned. For each, the designer's, the lead's and the orchestrator's recommendations agree, the confidence is
medium or higher, and the choice is reversible: each is a rule inside `gov.store.load` or the suite, and no later
ticket has built on it yet. The suite and the implementation on the branch already follow them. DP-3 (who writes
`.gov-runtime/store.db` in a live session) is not decided here: it touches the guard, so it goes to the owner; it
changes nothing in this ticket.

### DEC-274 — W1-10 DP-1: what a record is, and what an invalid one does to a load
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-1 option (a); confidence medium · **Under:** DEC-239, CAP-13.a
- **Decision:**
  - A record is any tracked Markdown file whose frontmatter has an `id`. It needs `id`, `type` and `status`
    (DEC-239). An unreadable or incomplete one is listed in the load's `invalid` by path, and the load continues.
  - Known consequences, recorded as residuals for later tickets: the charter, the contract and the plan have `id`
    and `status` but no `type` and are reported invalid; the seven kernel templates load as records with
    placeholder ids; decisions are headings in the register, not files, so every `DEC-…` reference is dangling
    until decisions are records; two files with one id both load.

### DEC-275 — W1-10 DP-2: the store's public interface is a Python interface
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-2 option (a); confidence high · **Under:** DEC-190
- **Decision:** W1-10 delivers `gov.store.load` and `gov.store.digest`, and `gov.records.records`, `active`,
  `edges`, `dangling` and `commits`. `gov rebuild` stays reserved; the ticket that wires it to `load` (W1-27)
  revises its registry case with the reason "planned: command implemented".

### DEC-276 — W1-10 DP-4: the digest covers the store's logical content
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-4 option (a); confidence high · **Under:** CAP-13.a
- **Decision:** "The same digest twice" is over the store's logical content (records, edges, commits, trailers, in
  a fixed order), not over the bytes of `store.db`.

### DEC-277 — W1-10 DP-5: the source of each typed edge, and trailers
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-5 option (a); confidence medium, high for DEC-012's five keys · **Under:** DEC-012, DEC-182, CAP-09.a
- **Decision:**
  - A frontmatter key gives an edge of the same name in upper case, from the carrying record to each listed id:
    `evidence_for`, `constrains`, `implements`, `tests`, `generates`, `validates`, `supersedes`, `depends_on`.
    `superseded_by` gives the same SUPERSEDES edge once.
  - Trailers are not edges. They come from `commits()`, and a trailer id that names no record is in `dangling()`.
  - Before any real record uses the four keys DEC-012 does not name (`evidence_for`, `tests`, `generates`,
    `validates`), a product-spec worker checks them against the archived Framework §11.2 (DEC-222).
  - Known consequences, recorded as residuals: a ticket's `depends_on` holds WBS ids while its `id` is the tk id,
    so those edges are dangling in this repository; trailer values such as `decision-record` name no record and
    are dangling too.

### DEC-278 — W1-10 DP-6: both dev tiers, and the load call alone is timed
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-6 option (a); confidence medium-high
- **Decision:** "Full load of a dev tier < 5 s" is tested on both `a-dev` and `b-dev`, and the limit is on the
  `load` call alone.

| Version | Date | Change |
|---|---|---|
| 0.57 | 2026-10-04 | Delegated under DEC-220: DEC-274 (W1-10 DP-1: a record is a tracked Markdown file with an `id` in its frontmatter; invalid ones are listed and the load continues), DEC-275 (DP-2: a Python interface; `gov rebuild` stays reserved for W1-27), DEC-276 (DP-4: the digest covers logical content), DEC-277 (DP-5: frontmatter key to edge of the same name; trailers are not edges), DEC-278 (DP-6: both dev tiers, the load call alone). DP-3 goes to the owner. |

## 58. Delegated decisions on W1-25's test design packages (register v0.58, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on four of the six packages the W1-25 (`DAEO-rrxp`) ticket
lead returned from its test design. For each, the designer's, the lead's and the orchestrator's recommendations
agree, the confidence is medium or higher, and the choice is reversible. The suite on the branch already follows
them. Two are not decided here and go to the owner: DP-1 (how the command is wired, where the designer and the lead
recommend differently) and DP-3 (the checkpoint directory, which needs a guard and containment exception). The
default age and commit thresholds of DP-5 are also the owner's to name.

### DEC-279 — W1-25 DP-2: the checkpoint's schema, keys and arguments
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-2 option (a); confidence medium-high on the schema, medium on the names · **Under:** CAP-37.a, CAP-13.b, DEC-229
- **Decision:**
  - A checkpoint conforms to W1-08's kernel checkpoint schema, extended by this ticket: a markdown record with the
    frontmatter keys `task`, `trigger`, `next_action`, `created`, and `inputs` as a list of `{id, version, hash}`
    with a sha256.
  - `template/governance/kernel/schemas/checkpoint.schema.json` and
    `template/governance/kernel/templates/checkpoint.md` are added to W1-25's `allowed_paths`, in a commit with the
    trailer `Task: DAEO-rrxp`.
  - The command is `gov checkpoint --ticket <id> --trigger <ticket-transition|compaction|stop> --next <text>
    [--input <path>]…`. The ticket file is always an input; the result gives `path` and `id`. A missing argument,
    an unknown ticket or an input that cannot be hashed is an error (exit 1) and nothing is written.

### DEC-280 — W1-25 DP-4: what W1-25 shows of "every ticket transition, compaction and stop"
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-4 option (a); confidence medium · **Under:** CAP-37.b
- **Decision:** The command accepts exactly the three triggers and records which. The watchdog reports
  `CHECKPOINT_MISSING` for a ticket with no checkpoint, and `CHECKPOINT_STALE` with the reason `ticket-transition`
  when the ticket's status changed after the latest one. The calls at the three moments belong to W1-29, W1-49 and
  W1-30.

### DEC-281 — W1-25 DP-5: the `--watch` policy comes from arguments, and stale is exit 3
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-5 option (a); confidence medium · **Under:** CAP-37.c, DEC-208, DEC-237
- **Decision:**
  - Thresholds are arguments with kernel defaults: `--max-age-minutes`, `--max-commits`, and `--max-context`
    (default 0.30). The caller passes `--context-utilisation`; without it, context is not judged. The watchdog
    only reads.
  - Fresh is exit 0 with `stale` false. Stale is `CHECKPOINT_STALE`, exit 3, with the reasons listed.
  - **Not decided here, with the owner:** the default age and the default commit count. The tests pass thresholds
    explicitly. A project value in `path-map.yaml` waits until W1-29 needs one.

### DEC-282 — W1-25 DP-6: the resume brief, the family check, and one real session
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-6 option (b); confidence medium-high for the check, medium for the session · **Under:** CAP-20.a, CAP-37.f, CAP-38.b, DEC-232
- **Decision:**
  - `gov checkpoint --resume --ticket <id>` prints the brief (the ticket, its inputs with their hashes, the next
    step) from the latest checkpoint alone.
  - The fresh-agent-reconstruction family check is deterministic: it passes when that brief can be built for the
    latest checkpoint of every ticket that has one, and fails on a missing next step or hash.
  - The acceptance suite adds one real short headless session per run (`local_only`, the cheapest model, two
    turns, an empty directory, only the brief), as DEC-232 did for the launcher.

| Version | Date | Change |
|---|---|---|
| 0.58 | 2026-10-04 | Delegated under DEC-220: DEC-279 (W1-25 DP-2: W1-08's checkpoint schema extended; keys and arguments; two kernel files join the ticket's paths), DEC-280 (DP-4: three triggers recorded; the watchdog detects a missing or outdated checkpoint), DEC-281 (DP-5: thresholds as arguments, stale is exit 3; the defaults go to the owner), DEC-282 (DP-6: `--resume`, a deterministic family check, one real session). DP-1 and DP-3 go to the owner. |

## 59. Delegated decisions on W1-49's packages DP-4 and DP-5 (register v0.59, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the two packages the W1-49 (`DAEO-32n6`) test designer
returned in batch 3, after DEC-263 and DEC-264. For each, the lead's recommendation and the orchestrator's agree, the
confidence is medium or higher, and the choice is reversible: W1-29 replaces both hook files. The branch is built
this way. Both read the owner's own words in DEC-264, so each is told to the owner with what it means in practice.
A reviewer finding that could lose written content is not decided here: the prompt says such a finding is fixed,
the lead recommends a residual, and that is the owner's to settle before the ticket is merged.

### DEC-283 — W1-49 DP-4: "older than the block" compares the written part's time with the block's time
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-4 option (a); confidence medium · **Under:** DEC-264
- **Decision:** The SessionStart injection warns when the checkpoint file's time, which the hook sets back to the
  written part's time after it appends, is earlier than the block's `generated:` time. In practice the warning
  shows after every compaction until the session rewrites its checkpoint, and then stops. No tolerance in minutes
  is used (that was DEC-258).

### DEC-284 — W1-49 DP-5: the hook does not invent the pending owner decisions
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-5 option (a); confidence medium-high · **Under:** DEC-264
- **Decision:** A hook is a command and has no source for the pending owner decisions. In the generated block that
  line says `not known to the hook; see the written part of this checkpoint`. The git head, the tickets in
  progress and the worktree list are generated. A file the orchestrator keeps for this, which the hook could read,
  is a matter for W1-29.

| Version | Date | Change |
|---|---|---|
| 0.59 | 2026-10-04 | Delegated under DEC-220: DEC-283 (W1-49 DP-4: the warning compares the written part's time with the block's; it shows after every compaction until the checkpoint is rewritten), DEC-284 (W1-49 DP-5: the block says the pending owner decisions are not known to the hook). |

## 60. Delegated decisions on W1-15's test design packages (register v0.60, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the six packages the W1-15 (`DAEO-7nne`) ticket lead
returned from its test design. For each, the designer's, the lead's and the orchestrator's recommendations agree,
the confidence is medium or higher, and the choice is reversible until W1-16 or W1-17 builds on it. None changes
the guard or containment. The suite on the branch already follows them.

### DEC-285 — W1-15 DP-1: the filter's interface, and how a check command is run
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-1 option (a); confidence medium-high on the function, medium on the check convention · **Under:** CAP-03.a, CAP-03.e, CAP-38.b
- **Decision:**
  - The filter is the function `gov.secrets.indexable(root, paths)`: it takes the project root and a list of
    project-relative paths and returns, in order, the sub-list an indexer may read. It drops a file that holds a
    secret, a file whose namespace is not `memory_class: governance`, and anything unreadable. If it cannot decide,
    it raises or drops the path; it never lets the path through.
  - A family check's `command` is run by `sh -c` in the project root, and exit 0 means green. W1-26 may refine this
    when it builds `gov check`.

### DEC-286 — W1-15 DP-2: the seven dev canaries, and both spellings of the token canary
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-2 option (a); confidence medium on the count · **Under:** DEC-074 Q8
- **Decision:** The seven dev canaries are the seven planted values the test designer found in the dev tiers (three
  strings with the canary word and an example cloud key pair in `a-dev`; the token canary and a key-file canary in
  `b-dev`). The token canary is detected in both spellings, with underscores as the KPI writes it and hyphenated as
  `b-dev` holds it. The owner is asked to confirm the count against the S0b1 manifest; the list is one tuple in the
  suite's support module.

### DEC-287 — W1-15 DP-3: the filter runs the gitleaks binary
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-3 option (a); confidence medium-high · **Under:** CAP-03, DEC-195
- **Decision:** The filter runs gitleaks 8.30.1 (in the tool registry) with the rules of `.gitleaks.toml`, so there
  is one source of rules. The filter and check cases therefore need the binary where they run. Putting gitleaks on
  CI is an install for the owner, raised with W1-40; until then those cases run on this machine.

### DEC-288 — W1-15 DP-4: what each gitleaks file holds
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-4 option (a); confidence medium
- **Decision:** `template/.gitleaks.toml` holds the defaults plus the token and canary rules, with no path
  allowlist. The root `.gitleaks.toml` holds the same rules plus this repository's own allowlist. A product that
  adopts the template inherits no allowlist.

### DEC-289 — W1-15 DP-5: the two W1-08 residuals stay open
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-5 option (a); confidence high
- **Decision:** W1-15 reads only a namespace's `paths` and `memory_class`. The closed lists for the free-text
  namespace fields and the meaning of `permitted_roles` move to the first ticket that reads export or embedding
  policy (W1-17 or W1-24). `bootstrap.md` is corrected at W1-15's close.

### DEC-290 — W1-15 DP-6: allowlists, and secrets inside a store
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-6, the lead's three recommendations; confidence medium · **Under:** CAP-03.a, CAP-38.b
- **Decision:**
  - The root `.gitleaks.toml` allowlists, by path, the tracked documents that only name the canary identifier (the
    ticket file, plan documents, this suite's README), after the engineer runs gitleaks over the tree and reports
    which they are. The template gets no such entry.
  - The pre-index filter ignores path allowlists: a file with a fake secret in a governance namespace, such as a
    test fixture, never reaches an index.
  - The secrets-indexing check scans the content of the stores, SQLite rows included, because `gitleaks dir` skips
    binary files. The extra lines over the 70 LOC estimate are accepted.

| Version | Date | Change |
|---|---|---|
| 0.60 | 2026-10-04 | Delegated under DEC-220: DEC-285 (W1-15 DP-1: `gov.secrets.indexable(root, paths)`; a check command runs by `sh -c`, exit 0 is green), DEC-286 (DP-2: the seven canaries as found in the tiers, both spellings; the owner confirms the count), DEC-287 (DP-3: the filter runs gitleaks), DEC-288 (DP-4: the template has no allowlist), DEC-289 (DP-5: the two W1-08 residuals move to W1-17 or W1-24), DEC-290 (DP-6: a root-only allowlist for documents naming the canary; the filter ignores allowlists; the check scans store content). |

## 61. Delegated decisions on W1-09's test design packages (register v0.61, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on seven of the nine packages the W1-09 (`DAEO-topz`)
ticket lead returned from its test design. For each, the designer's, the lead's and the orchestrator's
recommendations agree, the confidence is medium or higher, and the choice is reversible. The suite on the branch
already follows them. DP-4 (how the READY rule knows a specification is not closed) and DP-6 (what an open decision
package is before W1-34 and W1-11) are not decided here: the confidence is below medium, so they go to the owner.
Meanwhile the engineer builds to the suite as written, and the branch is not merged until both are answered.

### DEC-291 — W1-09 DP-1: claims and the READY rule have a Python interface
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-1 option (a); confidence high · **Under:** CAP-23.a, CAP-23.b, DEC-275
- **Decision:** W1-09 delivers `gov.tasks.claim`, `release`, `holder`, `ready`, `blocked` and `create`, raising
  `GovError` with the codes `CLAIM_HELD`, `CLAIM_NOT_HELD`, `TICKET_NOT_FOUND` and `TICKET_CLOSED`. No `gov`
  command is added: `gov claim` stays in Wave 3 (CAP-23.b), and the twelve-command registry is unchanged.

### DEC-292 — W1-09 DP-2: the claim convention
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-2 option (a); confidence medium-high, medium for the closed ticket and `in_progress` · **Under:** CAP-23.a, DEC-116
- **Decision:**
  - The lock is `.tickets/.claims/<ticket id>`, created with O_EXCL, a text file naming the holder. The holder is a
    string the caller gives, by convention `<role>:<session>`.
  - Only the holder releases. Nothing expires: a dead session's claim is released by whoever names its recorded
    holder, which is the main orchestrator's job.
  - A closed ticket cannot be claimed (`TICKET_CLOSED`). A lock and `status: in_progress` both count as claimed.
  - Left open and untested: whether `claim` also sets `in_progress`; a second claim by the same holder; an empty
    holder.

### DEC-293 — W1-09 DP-3: which acceptance tests folder makes a ticket READY
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-3 option (a); confidence high for the folder, medium for the classes · **Under:** DEC-069, CAP-31.c
- **Decision:** The folder is the ticket's `acceptance_tests.path`, else `tests/acceptance/<wbs_id>/`, else
  `tests/acceptance/<ticket id>/`. It must be a directory. The rule applies to tickets of every class.

### DEC-294 — W1-09 DP-5: a ticket's mandatory inputs
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-5 option (a); confidence medium · **Under:** CAP-31.d, DEC-277
- **Decision:** A ticket key `inputs` holds a list of record ids. An input is absent when no such record exists,
  and superseded when a SUPERSEDES edge points at it. A ticket with an absent or superseded input is not READY.
  Adding `inputs` to W1-08's ticket schema and template is a residual for the next ticket that touches them; the
  schema accepts unknown keys today.

### DEC-295 — W1-09 DP-7: `gov.tasks.create` adds `state_class` to a new ticket
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-7 option (a); confidence medium · **Under:** DEC-229
- **Decision:** `gov.tasks.create(root, title)` runs the kernel's `tk create` and adds `state_class: AUTHORITATIVE`
  to the new ticket, so the vendored script keeps its hash. W1-09 gets a KPI line for it, in a commit with the
  trailer `Task: DAEO-topz`. Which copy of the script `create` runs in this repository, where the kernel is under
  `template/` until it is installed here, stays open and is a residual.

### DEC-296 — W1-09 DP-8: what W1-09 shows of "verified by gov doctor"
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-8 option (a); confidence medium-high · **Under:** DEC-196
- **Decision:** W1-09's tests check the vendored file against its pinned sha256. The check by `gov doctor` goes to
  W1-27's test design as a described behaviour.

### DEC-297 — W1-09 DP-9: claims are made in the main tree; the claims folder is untracked
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-9 option (a); confidence medium · **Under:** DEC-235, DEC-236
- **Decision:** In Wave 1 claims are made only in the main tree, by the main orchestrator; a claim is not shared
  across worktrees. `.tickets/.claims/` is untracked: the orchestrator adds it to `.gitignore`. A claims folder
  that is a symbolic link is an untested residual; exclusive creation cannot overwrite a file.

| Version | Date | Change |
|---|---|---|
| 0.61 | 2026-10-04 | Delegated under DEC-220: DEC-291 (W1-09 DP-1: a `gov.tasks` Python interface, no `gov` command), DEC-292 (DP-2: the claim convention), DEC-293 (DP-3: the acceptance tests folder, for every class), DEC-294 (DP-5: `inputs` as record ids), DEC-295 (DP-7: `create` adds `state_class`; a KPI line), DEC-296 (DP-8: the doctor check goes to W1-27), DEC-297 (DP-9: claims in the main tree only; the folder is untracked). DP-4 and DP-6 go to the owner. |

## 62. Delegated decision on W1-15's reviewer finding F9 (register v0.62, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the one reviewer finding the W1-15 (`DAEO-7nne`) ticket
lead returned as needing a decision. The lead's recommendation and the orchestrator's agree, the confidence is
medium, the choice is reversible, and it makes the filter stricter.

### DEC-298 — W1-15 F9: the pre-index filter ignores every allowlist of the project's gitleaks file
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 reviewer finding F9 and the lead's recommendation; confidence medium · **Extends:** DEC-290 · **Under:** CAP-03.a
- **Decision:** DEC-290 made the filter ignore path allowlists. It also ignores the other ways a project's
  `.gitleaks.toml` can shelter a secret: allowlist `regexes` and `stopwords`, per-rule allowlists, and disabled
  rules. A file that holds a secret by the rules never reaches an index, whatever the project's file allows. The
  finding lets a secret through, so it is fixed before W1-15 closes: a test design batch first, as a described
  behaviour, then a fresh engineer.

| Version | Date | Change |
|---|---|---|
| 0.62 | 2026-10-04 | Delegated under DEC-220: DEC-298 (W1-15 F9: the filter ignores every allowlist and disabled rule of the project's gitleaks file; fixed before the ticket closes). |

## 63. Delegated decision on W1-15's package DP-7 (register v0.63, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the package the W1-15 (`DAEO-7nne`) test designer
returned in its third batch. The designer's, the lead's and the orchestrator's recommendations agree, the
confidence is medium, and the choice is reversible.

### DEC-299 — W1-15 DP-7: a project that removes or rewrites a template rule is out of DEC-298's scope
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-7 option (a); confidence medium · **Under:** DEC-287, DEC-298
- **Decision:** The project's `.gitleaks.toml` stays the one source of rules (DEC-287). DEC-298 strips its
  allowlists and disabled rules; it does not put back a rule the project deleted or rewrote. A file with no rules
  at all is refused. That a project can remove a template rule, such as the canary rule, and so let that secret
  through the filter and the check, is recorded as a residual in `governance/project/bootstrap.md`; a kernel rule
  set that always applies would be a second rule source and a later decision.

| Version | Date | Change |
|---|---|---|
| 0.63 | 2026-10-04 | Delegated under DEC-220: DEC-299 (W1-15 DP-7: the project's gitleaks file stays the one source of rules; a removed template rule is a residual). |

## 64. Delegated decisions on W1-09 after its review (register v0.64, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on what the W1-09 (`DAEO-topz`) ticket lead returned with
its DONE. Both make the READY rule stricter (they fail closed), the recommendations agree, the confidence is medium
or higher, and both are reversible. W1-09's DP-4 and DP-6 remain with the owner.

### DEC-300 — W1-09: the acceptance tests folder must lie below `tests/acceptance/`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 reviewer finding H2 and its repair; confidence high · **Narrows:** DEC-293 · **Under:** DEC-069, CAP-31.c
- **Decision:** The folder that makes a ticket READY (DEC-293) counts only if, with links resolved, it is a
  directory inside the project and strictly below `tests/acceptance/`. An absolute path, `.`, `..`, `src`, `.git`,
  `tests/acceptance/` itself or a link leading outside the project does not count. A path naming another ticket's
  folder, and an empty folder, still count; both are residuals.

### DEC-301 — W1-09 DP-10: while the claims folder cannot be inspected, every open ticket counts as claimed
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-10 option (a); confidence medium · **Under:** DEC-292, CAP-23.a
- **Decision:** When `.tickets/.claims` cannot be read, every open ticket is `CLAIMED` and the ready queue is empty
  until the folder is repaired. A claim that cannot be inspected counts as a claim.

| Version | Date | Change |
|---|---|---|
| 0.64 | 2026-10-04 | Delegated under DEC-220: DEC-300 (W1-09: the acceptance tests folder must lie strictly below `tests/acceptance/`, inside the project; narrows DEC-293), DEC-301 (W1-09 DP-10: an unreadable claims folder makes every open ticket claimed). |

## 65. Delegated decisions on W1-12's packages DP-1 to DP-4 (register v0.65, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on four of the five packages the W1-12 (`DAEO-lc4q`) ticket
lead returned. For each, the designer's, the lead's and the orchestrator's recommendations agree, the confidence is
medium or higher, and the choice is reversible before W1-13 reads the schema. DP-5 (what W1-12 shows of the CIT-E
half of its third KPI line) is not decided here: it moves part of a KPI's enforcement to another ticket, so it goes
to the owner, and W1-12 is not merged before the answer.

### DEC-302 — W1-12 DP-1: the schema carries the readiness data under the YAML's own keys
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-1 option (a); confidence medium-high · **Under:** CAP-30.a, DEC-085
- **Decision:** The forked OpenSpec schema `feature-readiness` carries the rows, the states and the capability-type
  table under the key names and entry shapes of `docs/contract/readiness-dimensions.yaml` (`dimensions`,
  `cell_states`, `capability_types`), as top-level keys of its `schema.yaml`. W1-13 reads that structure.

### DEC-303 — W1-12 DP-2: W1-12 delivers `template/openspec/config.yaml`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-2 option (a); confidence medium · **Under:** CAP-30.a
- **Decision:** `template/openspec/config.yaml`, with `schema: feature-readiness`, is added to W1-12's
  `allowed_paths`, in a commit with the trailer `Task: DAEO-lc4q`, so that a new change gets the readiness record
  without `--schema` being passed. One test covers it.

### DEC-304 — W1-12 DP-3: the kernel `templates/openspec/` folder stays unused for now
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-3 option (1), the lead's fallback; confidence medium · **Under:** DEC-198, DEC-222
- **Decision:** OpenSpec reads templates only from the schema's own `templates/` folder, so the templates the KPI
  validates live there, and `template/governance/kernel/templates/openspec/**` holds nothing. That is recorded as a
  residual. The text of G-07 and G-09 is in the S0b2 output in the workbench, not in the archived sources; whether
  it is read before W1-12 closes is asked of the owner, and an answer may put a file in that folder.

### DEC-305 — W1-12 DP-4: the readiness record is YAML
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-4 option (a); confidence medium · **Under:** CAP-30.a
- **Decision:** The readiness record is `readiness.yaml`, artifact id `readiness`: one entry per row with `n`, `key`,
  `state`, `evidence`, `reason` and `gap_ticket`. A fresh record has all 26 rows `MISSING`: empty is invalid, N/A is
  never a default, and the other states need content.

| Version | Date | Change |
|---|---|---|
| 0.65 | 2026-10-04 | Delegated under DEC-220: DEC-302 (W1-12 DP-1: the schema carries the YAML's own keys), DEC-303 (DP-2: W1-12 delivers `template/openspec/config.yaml`), DEC-304 (DP-3: the kernel `templates/openspec/` folder stays unused for now), DEC-305 (DP-4: the readiness record is YAML, fresh rows `MISSING`). DP-5 goes to the owner. |

## 66. Owner answers of 2026-10-04 on the parallel run's open packages (register v0.66, appended by the W1 orchestrator on branch `w1/integrate`)

The owner answered every package and question open at the stop of the parallel run: W1-49's lost-content finding,
W1-09 DP-4 and DP-6, W1-12 DP-5, W1-46 DP-10 to DP-12 and DP-14 to DP-16, W1-25 DP-1 and DP-3 with the watchdog
defaults, W1-50 DP-4 and DP-5, W1-10 DP-3, and four confirmations. DEC-306 to DEC-324 record them. DEC-325 is the
orchestrator's delegated decision that DEC-324 asks for. The orchestrator prompt is v4.1 (`3ccbf75c`): its section 6
now also delegates stricter-only decisions.

### DEC-306 — W1-49: the in-place-save race is a residual until W1-29 replaces the checkpoint file
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-49's second review, finding 1 · **Under:** DEC-264, DEC-250, CAP-37
- **Decision:**
  - If the session saves its checkpoint in place between the PreCompact hook's read and its write, the new text can
    be cut or overwritten. That is accepted as a residual in `bootstrap.md` until W1-29 replaces the checkpoint
    file. W1-49 is merged and closed as built.
  - When it is closed the orchestrator tells the owner, who updates section 7 of the orchestrator prompt (DEC-250).
  - The auto-compact setting takes effect in sessions started after the merge.

### DEC-307 — W1-09 DP-4: a ticket names its specification in a `specification` key
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-09 package DP-4 option (a), as built · **Under:** CAP-31, MR-2
- **Decision:** A ticket key `specification` holds a record id. The specification is closed when that record's
  status is `CLOSED`; any other status, or no such record, means not closed, and the ticket is not READY. A ticket
  without the key is not held. W1-12, W1-13 and W1-14 make a specification a record and write the key accordingly.

### DEC-308 — W1-09 DP-6: an open decision package names its waiting tickets in `constrains`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-09 package DP-6 option (a), as built · **Under:** CAP-34.e
- **Decision:** A decision package names the tickets that wait on it in `constrains`, which is already a graph
  edge, and it is open while its status is `PROPOSED`. A ticket constrained by an open package is not READY. W1-34
  keeps the key and the status; W1-11 decides what a declined or stale package does.

### DEC-309 — W1-12 DP-5: the CIT-E rule is stated in the schema, and W1-26 checks the link
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-12 package DP-5 option (a), as built · **Under:** CAP-30.e
- **Decision:** W1-12's schema carries the source and the extension rule of `readiness-dimensions.yaml`, and its
  suite goes red when the YAML changes without the schema. The check that a change to the taxonomy or to the YAML
  has a linked CIT-E record goes to W1-26, as a new KPI line in its own commit (`Task: DAEO-fygv`), with W1-26 added
  as a provider of CAP-30.e. W1-12 is merged and closed as built.

### DEC-310 — G-07 and G-09 may be read from the S0b2 output, by exact file path
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the question DEC-304 left open · **Amends:** DEC-304 · **Under:** DEC-198, DEC-222
- **Decision:** A product-spec worker may read the text of G-07 and G-09 from the S0b2 output in
  `~/gov-os-workbench/s0b2/out/`, by exact file path only, and never anything under `s0b2/probe/`. Its draft settles
  what the kernel `templates/openspec/` folder holds, under the delegation rule.

### DEC-311 — W1-46 DP-14: literal deny rules for the names that exist at launch, and `ln` judged by the guard
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-14 option (b) · **Amends:** DEC-180 · **Under:** DEC-176, CAP-58
- **Decision:**
  - The launcher's settings carry a literal `Edit` deny rule for every name that exists under `.gov-runtime/`
    outside `scratch/` at launch, plus the freeze flag.
  - The guard treats the destination of `ln` as a write target.
  - A new name created under `.gov-runtime/` at the OS level after launch is a residual in `bootstrap.md`.
  - The two live `ln` tests are revised to target existing names: rewrites after implementation, reason "owner
    decision".
  - The engineer's wider guard change is accepted: `.gov-runtime/` outside `scratch/` is denied by the guard to
    every role, not only to the orchestrator.

### DEC-312 — W1-46 DP-16: the owner committed `.claude/agents/research.md`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-16 option (a) · **Under:** DEC-163, DEC-254, CAP-22.d
- **Decision:** The owner committed `.claude/agents/research.md` in the W1-46 worktree as `b311c4c`, with the
  trailers `Task: DAEO-jdqr` and `Role: owner`, while no session ran there. If the containment check flags that
  HEAD move at the next call in that worktree, it is a record of an owner action (DEC-254), not a defect.

### DEC-313 — W1-46 DP-10: `gov launch` refuses permission bypass and added directories
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-10 option (a) · **Under:** CAP-61, DEC-161
- **Decision:** `gov launch` refuses `--dangerously-skip-permissions`, `--permission-mode bypassPermissions` and
  `--add-dir`, in any position, and the matching settings keys (`permissions.defaultMode: bypassPermissions`,
  `permissions.additionalDirectories`). `--allow-dangerously-skip-permissions`, which the package also named, is
  refused with them: that only makes the launcher stricter.

### DEC-314 — W1-46 DP-11: no launch when the project's settings don't register the guard
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-11 option (a), as built · **Under:** CAP-61, CAP-58
- **Decision:** `gov launch` refuses when the project's settings do not register the guard. The launcher does not
  register the hooks itself. As built, the refusal covers a missing or unwired `.claude/settings.json`,
  `disableAllHooks`, `--bare`, and `--setting-sources` with any value.

### DEC-315 — W1-46 DP-12: `Edit` deny rules for acceptance tests, tickets and `.claude` in worker sessions
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-12 option (a) · **Under:** MR-3, CAP-58, CAP-61
- **Decision:** The settings the launcher builds carry `Edit` deny rules for `tests/acceptance/**` (every role but
  the independent test designer), `.tickets/**` and `.claude/**`. W1-46 gets a new KPI line for them, in its own
  commit (`Task: DAEO-jdqr`).

### DEC-316 — W1-46 DP-15: `cdn-lfs.huggingface.co` leaves the research allowlist
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-15 option (a) · **Amends:** DEC-241
- **Decision:** `cdn-lfs.huggingface.co`, which does not resolve, is dropped from the starting hosts. The owner
  extends the list later if research needs it.

### DEC-317 — W1-25 DP-1: one generic change in `src/gov/cli/main.py`, made in W1-46's round
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-25 package DP-1 option (b) · **Under:** CAP-27, CAP-28
- **Decision:** In W1-46's engineer round, one generic change is made in `src/gov/cli/main.py`: each command's
  handler, arguments, act paths and exit codes come from its own module, including command-defined exit codes
  beyond 0 and 1. W1-07's suite is re-run. `src/gov/cli/**` is already in W1-46's `allowed_paths`. Later command
  tickets no longer need `main.py`. W1-25's engineer starts once this change is merged.

### DEC-318 — W1-50 DP-4: a commit that names a closed ticket, or one never started
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-50 package DP-4 · **Under:** DEC-255, CAP-58.h
- **Decision:** A commit whose trailers name a closed ticket is judged by that ticket's role and `allowed_paths`
  only if it is an ancestor of the ticket's close commit; otherwise it is a finding. A commit that names a ticket
  that was never started is a finding.

### DEC-319 — W1-50 DP-5: in a worker's call, another role's trailer is a finding
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-50 package DP-5 option (b) · **Under:** DEC-255, MR-3, CAP-58.h
- **Decision:** In a worker's call, a commit whose `Role` trailer differs from the caller's role is a finding.
  Own-trailer judging applies only in an orchestrator session's own call. W1-50's implementation follows W1-46's
  merge, as planned (DEC-256).

### DEC-320 — W1-25 DP-3: only orchestrator-role sessions run `gov checkpoint`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-25 package DP-3 · **Under:** CAP-37.a, CAP-20.a, DEC-176
- **Decision:** There is no guard or containment exception. Only orchestrator-role sessions, the main orchestrator
  and the ticket leads, run `gov checkpoint`, and they may already write `docs/checkpoints/<ticket>/`. Workers don't
  checkpoint; their state is their commits.

### DEC-321 — W1-25: the watchdog's defaults
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the defaults DEC-281 left open · **Extends:** DEC-281 · **Under:** CAP-37.c
- **Decision:** By default a checkpoint is stale after 4 hours, or after 20 commits on the branch since the
  checkpoint.

### DEC-322 — W1-10 DP-3: only orchestrator-role sessions write the live store
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-10 package DP-3 option (a) · **Under:** DEC-176, DEC-311, CAP-58
- **Decision:** Only orchestrator-role sessions write the live `.gov-runtime/store.db`. Tests and workers build
  their own stores in temporary directories. Revisit when `gov rebuild` is wired (W1-27).

### DEC-323 — Confirmed: the seven canaries, the root allowlist, the compaction warning and DEC-299
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Confirms:** DEC-286, DEC-290, DEC-283, DEC-299
- **Decision:** The owner confirms the seven dev canaries (DEC-286), the root allowlist of DEC-290, and DEC-283's
  warning after every compaction, which W1-29 may refine. That a project can remove or rewrite a template rule
  (DEC-299) stays a residual.

### DEC-324 — W1-15: the token rule's over-blocking is fixed before adoption
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1-15 residual "the rules over-block" · **Under:** CAP-03.a
- **Decision:** The token rule's over-blocking is fixed before W1-41 (adoption), by requiring a digit or mixed
  case in the token body. The orchestrator decides the form under delegation and adds the KPI line to the ticket it
  chooses.

### DEC-325 — The token rule fix: its form, and W1-16 carries it
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** DEC-324; the W1-15 reviewer's suggested repair; confidence medium · **Under:** DEC-287, DEC-298, CAP-03.a
- **Decision:**
  - The `gov-token` rule flags a prefixed string (`sk`, `pk`, `rk`, `tok`, then `_` or `-`) only when the body
    after the prefix holds at least one digit, or both an upper-case and a lower-case letter. The length floor of
    16 characters stays.
  - The requirement is part of the rule itself, in both `template/.gitleaks.toml` and the root `.gitleaks.toml`,
    and never an allowlist: the pre-index filter ignores allowlists (DEC-298). gitleaks' expression language has no
    look-ahead, so the engineer chooses how the rule expresses it.
  - The canary rule is unchanged, and the seven dev canaries are still detected.
  - W1-16 (`DAEO-lkeb`) carries the fix: it depends on W1-15, starts next, and already has a secret-exclusion KPI.
    It gets a KPI line and W1-15's rule paths, in a commit with `Task: DAEO-lkeb`. W1-15's acceptance tests that
    assert the old rule are revised by W1-16's test designer, as rewrites after implementation, reason "owner
    decision".

| Version | Date | Change |
|---|---|---|
| 0.66 | 2026-10-04 | Owner answers: DEC-306 (W1-49: the in-place-save race is a residual until W1-29), DEC-307 and DEC-308 (W1-09 DP-4 and DP-6, as built), DEC-309 (W1-12 DP-5 as built; W1-26 checks the CIT-E link), DEC-310 (G-07 and G-09 read by exact path), DEC-311 to DEC-316 (W1-46 DP-14, DP-16, DP-10, DP-11, DP-12, DP-15), DEC-317 (W1-25 DP-1: one generic change in `main.py`, in W1-46's round), DEC-318 and DEC-319 (W1-50 DP-4, DP-5), DEC-320 and DEC-321 (W1-25 DP-3 and the watchdog's defaults), DEC-322 (W1-10 DP-3), DEC-323 (confirmations), DEC-324 (the token rule is fixed before W1-41). Delegated under DEC-220: DEC-325 (the fix's form; W1-16 carries it). |

## 67. Delegated decision on the kernel `templates/openspec/` folder (register v0.67, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the draft a product-spec worker returned after reading
G-07 and G-09 by exact path (DEC-310). The worker's and the orchestrator's recommendations agree, the confidence is
high, and the choice is reversible: a later ticket can add the path and a file.

### DEC-326 — W1-12: the kernel `templates/openspec/` folder stays empty and leaves the ticket's paths
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** the product-spec worker's package, option 1; confidence high that no file is required, medium-high on removing the path · **Closes:** the question DEC-304 left open · **Under:** DEC-310, CAP-30.a
- **Decision:**
  - G-07 and G-09 are single rows of the S0b2 glue requirements. Neither names a path, a folder or the kernel. They
    require no file in `template/governance/kernel/templates/openspec/`: G-09 asks for templates that pass
    `validate --strict` on first use, and OpenSpec reads templates only from the schema's own folder.
  - The folder stays empty, and `template/governance/kernel/templates/openspec/**` leaves W1-12's `allowed_paths`,
    in a commit with the trailer `Task: DAEO-lc4q`.
  - G-08, a source of W1-13, says the checker reads `feature-readiness.md`. DEC-305 supersedes that file name: the
    record is `readiness.yaml`. W1-13's test designer is told so.

| Version | Date | Change |
|---|---|---|
| 0.67 | 2026-10-04 | Delegated under DEC-220: DEC-326 (W1-12: G-07 and G-09 require no file in the kernel `templates/openspec/` folder; the path leaves the ticket's `allowed_paths`; DEC-305 supersedes G-08's file name for W1-13). |

## 68. Delegated decision on W1-50's package DP-10 (register v0.68, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220 and the stricter-only rule of the orchestrator prompt v4.1
(section 6), on one of the three packages W1-50's second test design batch returned. The designer's, the lead's and
the orchestrator's recommendations agree, the confidence is medium, the choice is reversible, and it only makes the
containment check report more. DP-8 (how the check finds a ticket's close commit) and DP-9 (an orchestrator commit
that names a closed or never-started ticket) interpret the owner's DEC-318 and go to the owner.

### DEC-327 — W1-50 DP-10: a worker's call is judged commit by commit against the caller
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-04) · **Basis:** W1-50 package DP-10 option (a), the fail-closed reading; confidence medium · **Under:** DEC-319, DEC-255, CAP-58.h
- **Decision:** In a worker's call, a forward HEAD move is judged commit by commit against the caller, not by its
  two ends. A worker's commit outside its paths is a finding even when a later commit of the same call undoes it.

| Version | Date | Change |
|---|---|---|
| 0.68 | 2026-10-04 | Delegated under DEC-220 (stricter-only): DEC-327 (W1-50 DP-10: a worker's call is judged commit by commit against the caller). DP-8 and DP-9 go to the owner. |

## 69. Delegated decision on W1-34's package DP-1 (register v0.69, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the one package the W1-34 (`DAEO-egm9`) ticket lead
returned. The designer's, the lead's and the orchestrator's recommendations agree, the confidence is medium, and the
choice is reversible until W1-11 reads the state.

### DEC-328 — W1-34 DP-1: a gate record holds its state in `status` alone
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-34 package DP-1 option (a); confidence medium · **Under:** CAP-34.d, DEC-308
- **Decision:**
  - A decision package holds its gate state in `status` alone, with no second key: `PROPOSED` is open, `ACCEPTED` is
    answered, `DECLINED` is declined, `REVOKED` is revoked and `STALE` is stale. The template states the mapping.
  - The key that names the CIT a package belongs to is `cit`.
  - The READY rule (DEC-308) and W1-11's checker read the same value. One test pins the five values and the key.

| Version | Date | Change |
|---|---|---|
| 0.69 | 2026-10-04 | Delegated under DEC-220: DEC-328 (W1-34 DP-1: a gate record holds its state in `status` alone, `PROPOSED`, `ACCEPTED`, `DECLINED`, `REVOKED`, `STALE`; the CIT key is `cit`). |

## 70. Delegated decisions on W1-11's packages DP-1 and DP-4 (register v0.70, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on two of the four packages the W1-11 (`DAEO-be7u`) ticket
lead returned. The designer's, the lead's and the orchestrator's recommendations agree, the confidence is medium, and
both are reversible. DP-2 (the owner approval fact) and DP-3 (how a gate is cited) are with a product-spec worker,
who reads the archived sources under DEC-222; DP-2 goes to the owner afterwards.

### DEC-329 — W1-11 DP-1: the decision checker reads frontmatter and git, never prose
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-11 package DP-1 option (a); confidence medium · **Under:** CAP-51.a
- **Decision:**
  - The checker is deterministic: it reads frontmatter and git only. It does not read a decision's body for
    statements such as "superseded by DEC-003".
  - On the b-dev tier as planted it flags the overlapping ids across `docs/adr/` and `decisions/`. The other hazard
    classes (ACTIVE while superseded, a supersession cycle) are tested on a clone where the test writes the link the
    hazard describes, because HZ-B-03 states its link only in prose and the tier holds no cycle.
  - G-04 is in the S0b2 output and was not read. If it requires prose reading, this decision is revisited.

### DEC-330 — W1-11 DP-4: the checker fails a ticket that waits on a declined, revoked or stale package
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-11 package DP-4 option (a); confidence medium · **Under:** CAP-34.d, DEC-308, DEC-328
- **Decision:**
  - The checker fails every ticket that is not closed and is named in the `constrains` of a package whose `status` is
    `DECLINED`, `REVOKED` or `STALE`.
  - The READY rule in `gov.tasks` is unchanged in this ticket: it still releases a ticket once its package is no
    longer `PROPOSED`, so the queue can list such a ticket until W1-26 runs the checker. Closing that at the queue is
    a residual of W1-11, for the ticket that next changes `gov.tasks`.

| Version | Date | Change |
|---|---|---|
| 0.70 | 2026-10-04 | Delegated under DEC-220: DEC-329 (W1-11 DP-1: the checker reads frontmatter and git, never prose), DEC-330 (W1-11 DP-4: the checker fails a ticket waiting on a declined, revoked or stale package; the READY rule is unchanged). |

## 71. Delegated decision on W1-11's package DP-3 (register v0.71, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, after a product-spec worker read the archived sources under
DEC-222 (Contract v3 Gate L3 and A1, Framework §47). The originals name no key; they say only that a declined,
revoked, stale or other-CIT gate cannot authorise execution. The designer's, the lead's, the worker's and the
orchestrator's recommendations agree, the confidence is medium, and the choice only adds two optional keys and a
check that fails closed. DP-2 (the owner approval fact) goes to the owner.

### DEC-331 — W1-11 DP-3: a record cites its gate in `approval` and names its change in `cit`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-11 package DP-3 option (a); the gap worker's draft; confidence medium · **Under:** CAP-34.d, DEC-328, DEC-277
- **Decision:**
  - A ticket or change that claims a gate as its approval carries `approval`, a list of gate ids, and `cit`, a
    scalar. A gate authorises it only when the gate's `status` is `ACCEPTED` and the two `cit` values are the same
    string. A `PROPOSED` gate does not authorise.
  - The check fails closed, with the finding `GATE_NOT_AUTHORISING`: a cited id that is no record or is not a
    decision package; a citing record with `approval` and no `cit`; a gate with no `cit`.
  - A record with no `approval` is not checked. `approval` is not a graph edge (DEC-277).
  - The CIT id has no grammar yet; the ticket that builds the CIT-P and CIT-E records fixes it. The schema lines for
    `approval` and `cit` on a ticket are outside W1-11's paths and are a residual.
  - Whether setting a gate's `status` to `ACCEPTED` needs an owner approval fact is asked by no KPI; it is a residual
    of W1-11, to be raised with the owner's answer on DP-2.

| Version | Date | Change |
|---|---|---|
| 0.71 | 2026-10-04 | Delegated under DEC-220: DEC-331 (W1-11 DP-3: a record cites its gate in `approval` and names its change in `cit`; the check fails closed). DP-2 goes to the owner. |

## 72. Delegated decisions on W1-46's packages DP-17 to DP-21 (register v0.72, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the five packages the W1-46 (`DAEO-jdqr`) ticket lead
returned with its second run. Each is P2 or P3 and reversible, the lead's and the orchestrator's recommendations
agree, and the confidence is medium or higher. DEC-334 touches the guard and only makes it refuse more (stricter-only,
orchestrator prompt v4.1, section 6).

### DEC-332 — W1-46 DP-17: `gov launch` ends with the session's exit code
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-17 option (a); confidence medium · **Under:** DEC-317
- **Decision:** `gov launch` ends with the exit code of the session it started, whatever it is, and prints no
  envelope then (`CHILD_EXIT_CODE`), as built. A caller that needs to tell a launcher refusal from a session's own
  code 1 to 4 reads the output: a refusal prints the envelope.

### DEC-333 — W1-46 DP-18: the experiments root is `experiments/` in Wave 1
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-18 option (a); confidence medium · **Under:** DEC-273
- **Decision:** The experiments root is the fixed name `experiments/` in Wave 1, as built. A project key that names
  another root waits for a project that needs one.

### DEC-334 — W1-46 DP-19 and DP-20: the guard refuses a hard link to a file the role may not write, and `mv --target-directory` and `install` into protected places
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-04) · **Basis:** W1-46 packages DP-19 option (a) and DP-20 option (a); confidence medium-high and medium · **Under:** DEC-311, MR-3
- **Decision:**
  - The guard refuses `ln` without `-s` (and `link`, `cp -l`) when the source is a file the role may not write:
    otherwise a later call writes through the hard link and changes an acceptance test.
  - The guard treats the destination of `mv --target-directory=<dir>` and of `install` as a write target, as it does
    for `mv -t` and `cp -t`.
  - W1-46 carries both, in one short round (tests first), before it closes.

### DEC-335 — W1-46 DP-21: the builder test of the symbolic link under the acceptance tests makes its link by a form the guard does not read
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-21 option (a); confidence high · **Under:** DEC-311, DEC-132
- **Decision:** `tests/unit/containment/test_probe_repairs.py::TestRepair3Symlinks` still tests containment (the
  link is found and removed after the call), so it stays. Since DEC-311 the guard refuses `ln -s` into the acceptance
  tests before the call, so the test now makes the link with an interpreter one-liner, which the guard does not
  read. The orchestrator makes the change in the main tree, in its own commit with W1-46's trailer.

| Version | Date | Change |
|---|---|---|
| 0.72 | 2026-10-04 | Delegated under DEC-220: DEC-332 (W1-46 DP-17: `gov launch` ends with the session's exit code), DEC-333 (DP-18: `experiments/` fixed in Wave 1), DEC-334 (DP-19, DP-20, stricter-only: hard links to files the role may not write, `mv --target-directory` and `install` are refused), DEC-335 (DP-21: the containment builder test makes its link by an interpreter one-liner). |

## 73. Delegated decision on what W1-25 built beyond the decisions' wording (register v0.73, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the points the W1-25 (`DAEO-rrxp`) ticket lead asked to
have confirmed. Each is a detail of the built command, reversible until W1-29 and W1-30 call it; the lead's and the
orchestrator's recommendations agree; confidence high.

### DEC-336 — W1-25: the details of `gov checkpoint` as built are accepted
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** the W1-25 lead's "to confirm" list; confidence high · **Under:** DEC-279 to DEC-282, DEC-317, DEC-320, DEC-321
- **Decision:**
  - A checkpoint also stores `task_status`, the ticket's status when it was written; the watchdog compares it for
    the `ticket-transition` reason. The key is optional in the schema, and a checkpoint without it is judged stale.
  - The file is `docs/checkpoints/<ticket>/CP-<ticket>-<NNNN>.md`; the highest number is the latest.
  - An input's `version` is the short hash of the last commit that changed the file, or `untracked`.
  - The family check's command is `gov checkpoint --resume --json`, tier `G1`, severity `hard-block`.
  - `CHECKPOINT_STALE` and `CHECKPOINT_MISSING` end with exit code 3, for `--watch` and `--resume`. The other
    errors end with 1: `CHECKPOINT_ARGUMENT_MISSING`, `CHECKPOINT_TRIGGER_UNKNOWN`, `TICKET_UNKNOWN`,
    `CHECKPOINT_INPUT_UNREADABLE`, `CHECKPOINT_INVALID`, `GIT_FAILED`.
  - The lead's change to the W1-46 builder test `tests/unit/launch/test_command_modules.py` (the stand-in command
    renamed from `checkpoint` to `pause`, `9c8fec02`) is accepted; it is outside W1-25's paths and is a record.

| Version | Date | Change |
|---|---|---|
| 0.73 | 2026-10-04 | Delegated under DEC-220: DEC-336 (W1-25: `task_status`, the file name, the input version, the family check's command, the exit codes and the builder-test rename are accepted as built). |

## 74. Delegated decisions on W1-16's packages (register v0.74, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the packages the W1-16 (`DAEO-lkeb`) ticket lead
returned. Each is P2 or P3 and reversible, the lead's and the orchestrator's recommendations agree, and the
confidence is medium or higher. DP-1 (which question set decides the 60 % line) and the daemon's loopback UI go to
the owner.

### DEC-337 — W1-16 DP-2 and DP-3: the wrapper is a Python package, and "a rename" is a symbol rename
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 packages DP-2 option (A), confidence high, and DP-3 option (A), confidence medium · **Under:** CAP-12.a, CAP-12.b
- **Decision:**
  - The public interface is the package `gov.codeintel` (`index`, `home`, `projects`, `definitions`, `references`,
    `callers`, `impact`, `dead_code`), as built. It has no `gov` command; a later ticket that needs one adds a
    command module (DEC-317).
  - "Before and after a rename" is tested with a symbol rename. A file or folder move is a residual.

### DEC-338 — W1-16 DP-4: the tool's daemon files go to a short per-repository directory outside the repository
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 package DP-4 option (C); confidence medium · **Under:** CAP-12.a
- **Decision:**
  - The daemon's lock and socket files are not index files, so the failure line "an index file outside
    `.gov-runtime/`" does not cover them. They cannot live under `.gov-runtime/`: a socket path is limited to 108
    bytes.
  - The wrapper sets a short directory of its own for each repository, outside the repository, and never uses the
    tool's shared default. A test shows the shared default is not used.
  - Whether the daemon may serve its loopback UI at every call is the owner's to decide and is not settled here.

### DEC-339 — W1-16 R-1 and R-3: a token body that begins with `_` or `-` is flagged, and `gov.secrets` gets a public name check
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 packages R-1 and R-3; confidence medium · **Under:** DEC-324, DEC-325, DEC-298
- **Decision:**
  - R-1: the token rule also flags a body that begins with `_` or `-` when the rest meets DEC-325 (a digit, or
    mixed case; 16 characters). It only makes the rule flag more.
  - R-3: `gov.secrets` exposes a public function that says whether a path name holds a secret, and the wrapper
    stops importing private names. W1-17 and W1-19 use the same function. Batching the filter's gitleaks runs is a
    residual, to be measured on a large repository.
  - R-2 (a token holding the full alphabet run is never flagged when the gitleaks defaults are extended): W1-16's
    engineer traces the cause and reports it; a fix is a separate decision before W1-41.

| Version | Date | Change |
|---|---|---|
| 0.74 | 2026-10-04 | Delegated under DEC-220: DEC-337 (W1-16 DP-2, DP-3: a Python package; a rename is a symbol rename), DEC-338 (DP-4: daemon files in a short per-repository directory outside the repository), DEC-339 (R-1: a body beginning with `_` or `-` is flagged; R-3: a public name check in `gov.secrets`; R-2 is traced). DP-1 and the loopback UI go to the owner. |

## 75. Delegated decisions on W1-17's packages (register v0.75, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the six packages the W1-17 (`DAEO-rxln`) ticket lead
returned. For each the test designer's, the lead's and the orchestrator's recommendations agree on option (a), the
confidence is medium or higher, and the choice is reversible until W1-20 consumes the interface. The tests already
encode these options.

### DEC-340 — W1-17 DP-1: the public interface of the lexical index
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-1 option (a); confidence medium-high · **Under:** CAP-18.b, CAP-11.a, DEC-322
- **Decision:** `gov.retrieval.lexical` exposes `refresh(root)`, `search(root, query, refresh=True)`,
  `freshness(root)`, `digest(root)`, `chunks(root, path=None)` and `parent(root, parent_id)`, with the return shapes
  the suite's README states. `search(..., refresh=False)` never writes, so a worker session can read a live store it
  may not write (DEC-322). W1-20 and W1-27 build on these names.

### DEC-341 — W1-17 DP-3: "2.8 s scale" bounds the incremental re-index, held to 10 s
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-3 option (a); confidence medium · **Under:** CAP-17.a
- **Decision:** The test times only the `search` that follows one edited, committed file on an a-dev clone, with a
  bound of 10 seconds; the full build is not timed. G-20 is in the S0b2 output and was not read: what it measured is
  to be confirmed if the owner allows that read, and the bound is one constant.

### DEC-342 — W1-17 DP-4 and DP-5: a missing, empty or stale index makes the whole facet unavailable, and the check is not green without an index
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 packages DP-4 option (a), confidence medium-high, and DP-5 option (a), confidence medium · **Under:** CAP-17.a, CAP-38.b
- **Decision:**
  - A `search` on a missing, empty or stale index returns the facet as unavailable (`FACET_UNAVAILABLE`), with the
    reason `missing`, `empty` or `stale` and no hits; it does not return hits from the fresh files only. A default
    `search` builds a missing index and refreshes a stale one first.
  - The index-freshness check is not green when no index exists; it prints each stale path, prints no traceback and
    never writes. So the check is red in a repository whose live store has no index yet, this one included, until
    an orchestrator-role session builds it (DEC-322). W1-26 and W1-27 take that into account.

### DEC-343 — W1-17 DP-6: Python chunks get a function parent through the standard library
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-6 option (a); confidence medium · **Under:** DEC-091, CAP-18.b
- **Decision:** A chunk's parent is the function for Python (through `ast`, no install), the module (the whole
  file) for other code, and the section for Markdown. The 40 to 60 lines this adds to the estimate are accepted.

### DEC-344 — W1-17 DP-7: the corpus is the working-tree content of tracked files
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-7 option (a); confidence medium-high · **Under:** CAP-03.d, CAP-17.a, DEC-285
- **Decision:** The index reads tracked files as they stand in the working tree, the same content the secret
  filter judges, not the blobs of `HEAD`. The index and the record graph (`gov.store.load` reads `HEAD`) can
  therefore describe different states of one file; that is a residual for W1-20.

| Version | Date | Change |
|---|---|---|
| 0.75 | 2026-10-04 | Delegated under DEC-220: DEC-340 (W1-17 DP-1: the lexical interface), DEC-341 (DP-3: the incremental re-index is timed, 10 s), DEC-342 (DP-4, DP-5: an unusable index makes the facet unavailable; the check is not green without an index), DEC-343 (DP-6: function parents for Python through `ast`), DEC-344 (DP-7: working-tree content of tracked files). |

## 76. Delegated decision on W1-17's package DP-8 (register v0.76, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220. The engineer's, the lead's and the orchestrator's
recommendations agree, the confidence is medium, the choice is one condition and it is the stricter one.

### DEC-345 — W1-17 DP-8: the index-freshness check is not green on an index that holds no chunk
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-8 option (a); confidence medium · **Under:** DEC-342, CAP-38.b
- **Decision:** An index that matches the tracked blobs and holds no chunk does not pass the check, as built: a
  filter that wrongly drops every file cannot pass, and the check agrees with `search`, which reports `empty` as
  unavailable. A project with no governance-class file can therefore never be green; that is a residual.

| Version | Date | Change |
|---|---|---|
| 0.76 | 2026-10-04 | Delegated under DEC-220: DEC-345 (W1-17 DP-8: the index-freshness check is not green on an empty index). |

## 77. Delegated decisions on W1-16's second round (register v0.77, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on what the W1-16 (`DAEO-lkeb`) ticket lead returned with
its second run. Each is reversible, the recommendations agree and the confidence is medium. DEC-347 touches the
secret filter and only makes it refuse more (stricter-only).

### DEC-346 — W1-16 DP-5 and DP-6: the 16-character floor counts the rest alone, and the daemon directory is a residual with one test
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 packages DP-5 option (a) and DP-6 options (a) and (c); confidence medium · **Under:** DEC-325, DEC-338, DEC-339
- **Decision:**
  - A leading `_` or `-` of a token body (DEC-339) does not count toward the 16-character floor: the rest alone
    needs 16 characters, as built.
  - The files the tool's daemon leaves in the wrapper's per-repository directory under `/tmp` are a residual;
    the wrapper does not remove the directory, because that races a live daemon. One test shows that no planted
    secret stands in that directory after an index run.

### DEC-347 — The secret filter also scans with the project's rules alone, so gitleaks' built-in global allowlist cannot shelter a finding
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-04) · **Basis:** W1-16 package R-2, fix option 1, the engineer's and the lead's recommendation; confidence medium · **Under:** DEC-298, DEC-324, DEC-286
- **Context:** gitleaks' built-in defaults carry a global allowlist, and `[extend] useDefault = true` merges it over
  every rule, the project's included. DEC-298's stripping removes only the allowlists written in the project's
  file. So a canary or token that contains `abcdefghijklmnopqrstuvwxyz` in any case, contains `false`, begins with
  `true` or ends with `null`, or contains the default uuid stopword, passes the filter and reaches an indexer.
- **Decision:**
  - The pre-index filter and the path-name check run a second scan with the project's rules alone, without
    `extend`, and refuse a file that either scan flags. This closes the gap for the project's rules (the canary and
    token rules); the built-in rules stay sheltered by their own defaults, which is a residual.
  - W1-16 carries the change, tests first, before it closes: `src/gov/secrets/**` is in its paths. The doubled
    gitleaks runs are accepted; batching stays the residual of DEC-339.
  - A plain `gitleaks` run outside the filter (the pre-commit hook) keeps the built-in allowlist; whether the commit
    hook also needs the second scan is settled before W1-41, with the owner.

| Version | Date | Change |
|---|---|---|
| 0.77 | 2026-10-04 | Delegated under DEC-220: DEC-346 (W1-16 DP-5, DP-6: the floor counts the rest alone; the daemon directory is a residual with one test), DEC-347 (stricter-only: the secret filter also scans with the project's rules alone, so gitleaks' built-in global allowlist cannot shelter a canary or token). |

## 78. Delegated decisions on W1-13's packages (register v0.78, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on the four packages the W1-13 (`DAEO-w616`) ticket lead
returned. For each the test designer's, the lead's and the orchestrator's recommendations agree on option (a), the
confidence is medium or higher, and the choice is reversible. The tests already encode these options.

### DEC-348 — W1-13 DP-1: `gov readiness` blocks through its exit code, judged from the rows
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-1 option (a); confidence medium-high · **Under:** CAP-30.a, DEC-308
- **Decision:**
  - W1-13 delivers the verdict and its exit code, judged from the readiness rows and never from the record's
    `status`. W1-26 runs it as a check and also fails a specification that is `CLOSED` with a required row open.
    W1-35's change skill runs it before OpenSpec apply and archive.
  - Until W1-26 and W1-35 exist nothing stops a direct `openspec archive`, and the READY rule (W1-09) still trusts
    a status set by hand. Both are residuals of W1-13, for W1-26 and W1-35.

### DEC-349 — W1-13 DP-2: a specification is closed by `gov.readiness.close`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-2 option (a); confidence medium · **Under:** CAP-47.d, DEC-088, CAP-27
- **Decision:**
  - `gov readiness` stays a read command. Closing is the public function `gov.readiness.close(root, id)`: it
    refuses and writes nothing when a required row is open or the record is invalid; otherwise it creates the audit
    ticket through `gov.tasks.create` (none for a LITE feature) and then sets the status. Closing twice gives one
    ticket, and the record is not left `CLOSED` when the ticket cannot be created.
  - The audit ticket has `role: independent-auditor`, `class: audit`, `status: open`, and a title that names the
    specification. A later ticket gives closing a command or a skill step (W1-35 or W1-30).
  - "Fresh" and "authored none of the audited files" (MR-4) are not testable here and stay with the orchestrator's
    session rules.

### DEC-350 — W1-13 DP-3: the specification record is the frontmatter of the change's `proposal.md`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-3 option (a); confidence medium · **Under:** DEC-307, DEC-302, DEC-305, DEC-085
- **Decision:**
  - A specification is the record in the frontmatter of `openspec/changes/<change>/proposal.md`: `id`,
    `type: specification`, `status`, `state_class`, `profile`, `spine` and `capability_types`; `readiness.yaml`
    sits beside it. A missing profile or an unknown capability type does not pass.
  - Nothing writes that frontmatter yet. W1-14's bridge reads this form, and the proposal template of W1-12 or the
    planning skill of W1-35 writes it: a residual of W1-13.

### DEC-351 — W1-13 DP-4: arguments, report and exit codes of `gov readiness`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-4 option (a); confidence medium-high on the codes, medium on the names · **Under:** DEC-317, CAP-30.b, DEC-089
- **Decision:**
  - `--specification <record id>` or `--ticket <ticket id>` (through the ticket's `specification` key); with
    neither, every specification.
  - Passing: `ok: true`, exit 0, the report in `result`. A required row open: `ok: false`, `SPEC_NOT_CLOSED`, exit
    code 3, the report in `error.details`, and the message names the open rows. An invalid record:
    `READINESS_INVALID`, exit 1.
  - The report has `specification`, `profile`, `closed` and `open`; each open row has `n`, `key`, `state` and
    `gap_ticket` (the id or `UNLINKED`), in row order.

| Version | Date | Change |
|---|---|---|
| 0.78 | 2026-10-05 | Delegated under DEC-220: DEC-348 (W1-13 DP-1: the exit code blocks, judged from the rows; wiring is W1-26's and W1-35's), DEC-349 (DP-2: `gov.readiness.close` closes and creates the audit ticket), DEC-350 (DP-3: the specification record is the frontmatter of `proposal.md`), DEC-351 (DP-4: arguments, report, exit code 3). |

## 79. Delegated decisions on W1-33's packages P-2 to P-4 (register v0.79, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on three of the four packages the W1-33 (`DAEO-xog0`)
ticket lead returned. The test designer's, the lead's and the orchestrator's recommendations agree, the confidence
is medium or higher, and each is reversible; none grants a role anything. P-1 (placing the five definitions under
`.claude/agents/`) is an owner action.

### DEC-352 — W1-33 P-2, P-3 and P-4: what "generated" means, the permission-class families, and the two unsandboxed roles' grants
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-33 packages P-2 option (a), confidence medium-high; P-3 option (a), confidence medium; P-4 as written, confidence medium · **Under:** CAP-22.a, CAP-58.b, DEC-066, DEC-158
- **Decision:**
  - P-2: until the rulesync adapters of W1-38 exist, a definition under `.claude/agents/` that is placed by hand
    and agrees field by field with its kernel role file is a "generated definition" for W1-33. W1-38 later produces
    the same files from the same sources.
  - P-3: a role file maps the `NETWORK_*`, `DB_*`, `CLOUD_*` and `DEPLOY_*` families as CAP-58.b writes them; it
    does not list each member class of the archived Framework §32. Listing them is a residual, for the mid-wave
    audit to weigh.
  - P-4: the definitions stand as written: the orchestrator has `NETWORK_*` allowed (DEC-158: it is unsandboxed)
    and the database, cloud, CI-trigger and deploy classes denied; product-spec has all of them denied. The tests
    require only that each class has a stated disposition.

| Version | Date | Change |
|---|---|---|
| 0.79 | 2026-10-05 | Delegated under DEC-220: DEC-352 (W1-33 P-2: a hand-placed definition that agrees with its kernel role file counts as generated until W1-38; P-3: permission-class families as CAP-58.b writes them; P-4: the orchestrator's and product-spec's grants as written). P-1 is an owner action. |

## 80. Delegated decisions on what W1-13 and W1-16 built beyond the decisions' wording (register v0.80, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on the points the two ticket leads asked to have recorded.
Each is a detail of built code, reversible, and none makes a check weaker; the leads' and the orchestrator's views
agree; confidence medium-high.

### DEC-353 — W1-13: the details of `gov readiness` as built are accepted
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** the W1-13 lead's list of choices no decision fixes, and its reviewer's two fixed findings · **Under:** DEC-348 to DEC-351, DEC-085, CAP-30.e
- **Decision:**
  - The bare command's result is `{closed, specifications: [...]}`. Both selectors together is a usage error
    (exit 2). The error codes `SPECIFICATION_NOT_FOUND`, `TICKET_NOT_FOUND` and `AUDIT_TICKET_FAILED` end with 1.
  - A STANDARD specification with no capability type is invalid. A PRESENT row with no evidence is invalid, not
    open.
  - The audit ticket also carries `audits`, `assignee: independent-auditor`,
    `allowed_paths: [docs/audit/<id>/**]`, `profile` and `sources`.
  - From the review: a change folder that holds no specification record makes the bare command answer
    `READINESS_INVALID`, and a project readiness schema whose rows or capability-type table differ from the
    Contract's makes every specification in that project `READINESS_INVALID`. The rows and the table are constants
    in the checker, so a governed taxonomy change (CAP-30.e) changes the checker with the schema and the Contract.

### DEC-354 — W1-16: `stores_with_secrets` also runs the second scan
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** the W1-16 lead's third return · **Under:** DEC-347, DEC-287
- **Decision:** The secrets-indexing check's `stores_with_secrets` shares the filter's helper and therefore also
  scans with the project's rules alone, which DEC-347 did not name. It is accepted: it only makes the check find
  more. Where a project's rules have no expression of their own (they only modify a built-in rule), one scan stays;
  that is a residual.

| Version | Date | Change |
|---|---|---|
| 0.80 | 2026-10-05 | Delegated under DEC-220: DEC-353 (W1-13: result shape, codes, the audit ticket's fields and the two review fixes are accepted as built), DEC-354 (W1-16, stricter-only: `stores_with_secrets` also runs the second scan). |

## 81. Delegated decisions on W1-14's packages (register v0.81, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on the five packages the W1-14 (`DAEO-w9l3`) ticket lead
returned. For each the test designer's, the lead's and the orchestrator's recommendations agree on option (a), the
confidence is medium or higher, and the choice is reversible until W1-35 teaches the format. The lead had the
engineer build to the recommended options before they were decided; the result is accepted, and later briefs say
again that an engineer waits for the decision.

### DEC-355 — W1-14 DP-1 and DP-2: the bridge is `gov.tasks.bridge.derive`, and a task carries its fields in a YAML block
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-14 packages DP-1 option (a) and DP-2 option (a); confidence medium · **Under:** CAP-31.a, DEC-307, DEC-350
- **Decision:**
  - `gov.tasks.bridge.derive(root, change)` takes the change's folder name under `openspec/changes/` and returns
    `{"change", "specification", "tickets": [{"task", "ticket"}, ...]}`, one entry per task in file order. It
    commits nothing. A faulty `tasks.md` is refused with `TASKS_INVALID`, whose details name each faulty task.
  - A task carries `kpis`, `role`, `allowed_paths`, `profile` and `class` in a fenced `yaml` block indented under
    its checkbox line. A task that lacks one, `profile` and `class` included, refuses the whole derivation and
    nothing is written.
  - W1-12's `tasks.md` template does not show the block yet, so a change written from it is refused: a residual,
    for W1-35 or a template change.

### DEC-356 — W1-14 DP-3, DP-4 and DP-5: a hand-set `CLOSED` is not trusted, dependencies form one DAG, and a second run adds only new tasks
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-14 packages DP-3 option (a), confidence medium-high; DP-4 option (a), confidence medium; DP-5 option (a), confidence medium-high · **Under:** MR-2, DEC-348, CAP-31.a
- **Decision:**
  - The bridge derives only when the specification's status is `CLOSED` and `gov.readiness.check` passes.
  - `depends_on` holds quoted task numbers of the same file or ids of existing tickets, written to the ticket's
    `deps` as ticket ids. A name that resolves to nothing, an unquoted number, a cycle among tasks, or a dependency
    that reaches an existing cycle is `TASKS_INVALID`.
  - On a second run a task that has a ticket keeps it byte for byte, only new tasks get tickets, and a refused
    run changes nothing. A task is matched to its ticket by `specification` and the `task` key the bridge writes.
    A task edited or removed after derivation is a residual.

| Version | Date | Change |
|---|---|---|
| 0.81 | 2026-10-05 | Delegated under DEC-220: DEC-355 (W1-14 DP-1, DP-2: `gov.tasks.bridge.derive`; a task's fields in a YAML block; a faulty task refuses the whole derivation), DEC-356 (DP-3 to DP-5: `CLOSED` and a passing readiness check; one DAG; a second run adds only new tasks). |

## 82. Delegated decisions on W1-28's packages DP-4 and DP-7 (register v0.82, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on two of the eight packages the W1-28 (`DAEO-9279`)
ticket lead returned. The test designer's, the lead's and the orchestrator's recommendations agree, the confidence
is medium-high, and both are reversible. The other six (DP-1, DP-2, DP-3, DP-5, DP-6, DP-8) touch KPI lines, the
freeze flag or what a rollback does to history, and go to the owner.

### DEC-357 — W1-28 DP-4 and DP-7: `--cancel-agents` releases locks only, and "the same result on repeat" means the same state
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-28 packages DP-4 option (a) and DP-7 option (a); confidence medium-high · **Under:** CAP-05.b, CAP-05.d, DEC-292
- **Decision:**
  - `gov pause --cancel-agents` releases the claim locks under `.tickets/.claims/` and records the sessions that
    held them. It does not change a ticket's status: a ticket left `in_progress` is set back by hand, which is a
    residual. The command cannot stop a process.
  - "The same result on repeat" means the same state: a repeat succeeds and leaves the project as the first run
    did. The two `result` objects need not be equal field for field.

| Version | Date | Change |
|---|---|---|
| 0.82 | 2026-10-05 | Delegated under DEC-220: DEC-357 (W1-28 DP-4: `--cancel-agents` releases locks only; DP-7: a repeat leaves the same state). Six W1-28 packages go to the owner. |

## 83. Owner answers of 2026-10-05 on the parallel run's open packages (register v0.83, appended by the W1 orchestrator on branch `w1/integrate`)

The owner's answers of 2026-10-05, given through the operator and confirmed by the owner in the orchestrator's
session, on the packages the orchestrator's checkpoint listed as open: W1-50 DP-8 and DP-9, W1-11 DP-2, W1-16 DP-1
and its loopback UI, the slot question, six W1-28 packages, and four standing points. Ticket edits that follow from
them are separate commits with the trailer `Task: <ticket id>`.

### DEC-358 — W1-50 DP-8: a ticket's close commit is the latest commit in HEAD's history where its status becomes closed
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-50 package DP-8 option (a) · **Under:** DEC-255, DEC-318, CAP-58.h
- **Decision:** A ticket's close commit is the latest commit in HEAD's history in which the ticket's status becomes
  `closed`. When no such commit is found for a ticket whose status is `closed`, that is a finding.

### DEC-359 — W1-50 DP-9: an orchestrator commit naming a closed, never-started or unknown ticket is allowed outside the acceptance tests
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-50 package DP-9 option (a) · **Amends:** DEC-318 · **Under:** DEC-255, CAP-58.h
- **Decision:** A commit with `Role: orchestrator` whose `Task:` trailer names a closed ticket, a ticket never
  started, or a name that is no ticket (such as `Task: decision-record`) is allowed for every path outside
  `tests/acceptance/**`. Inside `tests/acceptance/**` it stays a finding (MR-3).

### DEC-360 — W1-11 DP-2: the owner's approval fact is the `Role: owner` trailer on the commit that sets ACTIVE
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-11 package DP-2 option (a) · **Under:** CAP-01.b, CAP-21.a, DEC-182
- **Decision:**
  - The owner's approval fact for a decision is the `Role: owner` trailer on the commit that sets the decision
    `ACTIVE`. A later owner commit approves nothing earlier.
  - Safeguard: W1-50 gets a KPI line, in its own commit, so that a commit carrying `Role: owner` made during any
    agent session's call is a finding.
  - A signature as the stricter form of the fact stays a residual.

### DEC-361 — W1-16 DP-1: the hit@5 question set is the S0b2 C1 set when it is in the S0b2 output, else the designer's set with harder questions
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-16 package DP-1 · **Under:** CAP-12.a, DEC-198, DEC-310
- **Decision:**
  - If the C1 question set is under `~/gov-os-workbench/s0b2/out/`, option (B): a test designer may read it there by
    exact file path, never anything under `s0b2/probe/`, and `questions.yaml` is swapped for it.
  - If it exists only under `s0b2/probe/`, option (A): the designer's set stays, with harder questions added.
  - Then W1-16 is merged and closed.

### DEC-362 — W1-16: the wrapper turns the tool's loopback UI off
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on the question W1-16 package DP-4 left open · **Under:** DEC-338, DEC-346
- **Decision:** The codebase-memory wrapper sets `--ui=false`. The change of the tool's configuration is recorded in
  the notes of its entry in `governance/project/tool-registry.yaml`.

### DEC-363 — A ticket idle on an owner answer does not count against the six
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER; orchestrator prompt v4.2, section 3 · **Amends:** DEC-235 · **Under:** DEC-236
- **Decision:** A ticket in flight that is idle waiting on an owner answer no longer counts against the six. The
  resource gate still applies to every running lead.

### DEC-364 — W1-28 DP-1: the pause-state line moves to W1-32
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-1 option (a) · **Under:** CAP-05, CAP-28
- **Decision:** The KPI line "Pause state appears in gov status" leaves W1-28. W1-32, which builds `gov status`
  and already names the pause state in its first success line, carries it; the two status cases move to W1-32's
  suite. W1-28 makes the state readable.

### DEC-365 — W1-28 DP-2 and DP-3: the orchestrator may set the freeze, only the owner lifts it, and the caller is `GOV_ROLE`
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 packages DP-2 option (b) and DP-3 · **Amends:** DEC-176 · **Under:** CAP-05.a, CAP-05.d, DEC-179
- **Decision:**
  - The orchestrator may set the freeze. Only the owner lifts it.
  - The caller is `GOV_ROLE` when it is set: `orchestrator` is allowed, and every worker role is refused. When
    `GOV_ROLE` is unset, the caller is the owner.
  - The `--role` flag is dropped for this command.
  - Lifting a freeze works only with `GOV_ROLE` unset.

### DEC-366 — W1-28 DP-5: what `--rollback` does
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-5 option (a) · **Under:** CAP-05.c, DEC-182
- **Decision:**
  - One `git revert --no-edit` per commit of the ticket, newest first.
  - Merge commits are skipped and named in the result, which says that a merge's own conflict resolutions stay.
  - Revert commits carry `Role:` and `Reverts-Task: <ticket>`, not `Task:`.
  - A conflicting revert aborts everything with an error.
  - An unknown ticket is an error; a ticket with no commit succeeds with an empty list.
  - A dirty tree is refused.
  - A repeat reverts nothing and succeeds.

### DEC-367 — W1-28 DP-6: the record of a rollback or a cancel is a commit to the ticket file
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-6 · **Under:** CAP-05.d, DEC-366
- **Decision:**
  - The record for `--rollback` and `--cancel-agents` is a commit to the ticket file, made after the reverts, with
    the trailers `Task: <ticket>` and `Reverts-Task: <ticket>`.
  - A plain pause writes no record.
  - KPI success 4 of W1-28 is reworded to match, in its own commit.

### DEC-368 — W1-28 DP-8: cancel and rollback both set the freeze flag
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-8 option (a) · **Under:** CAP-05.a, CAP-05.b, CAP-05.c
- **Decision:** `gov pause --cancel-agents` and `gov pause --rollback <ticket>` both also set the freeze flag.

### DEC-369 — The pre-commit hook runs the second gitleaks scan
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on the W1-16 residual · **Extends:** DEC-347 · **Under:** CAP-03.a, CAP-39.a
- **Decision:** The pre-commit hook also runs the second gitleaks scan, with the project's rules alone (DEC-347).
  W1-40 gets the KPI line, in its own commit.

### DEC-370 — G-20 may be read from the S0b2 output, by exact file path
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Under:** DEC-198, DEC-310, DEC-341
- **Decision:** A worker may read the text of G-20 from the S0b2 output in `~/gov-os-workbench/s0b2/out/`, by exact
  file path only, and never anything under `s0b2/probe/`.

### DEC-371 — Leads start their workers with `gov launch`
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER; orchestrator prompt v4.2, section 4 · **Supersedes:** DEC-183 for the roles the launcher starts · **Under:** DEC-231, DEC-311
- **Decision:**
  - W1-46 is closed, so from now on a ticket lead starts its workers with `gov launch <role> <ticket>`, sandboxed.
  - The W1-46 residuals stand as `governance/project/bootstrap.md` records them at its close.
  - `gov` is not on the PATH. A lead runs it from its worktree as
    `PYTHONPATH=src python3 -m gov.cli.main launch <role> <ticket> -- <CLI arguments>`.
  - The launcher starts `engineer`, `independent-test-designer`, `independent-auditor` and `research`. It has no
    `product-spec` role, so a product-spec worker still starts under DEC-183: a residual, told to the owner.

### DEC-372 — A latency case that fails under parallel load is re-run alone
- **Status:** ACCEPTED (owner, 2026-10-05; the handling is delegated to the orchestrator) · **Basis:** OWNER · **Under:** DEC-237
- **Decision:** A latency acceptance case that fails during the post-merge regression under parallel load is re-run
  alone, after the rest of the regression has ended. A pass alone counts, and each occurrence is recorded.

| Version | Date | Change |
|---|---|---|
| 0.83 | 2026-10-05 | Owner answers: DEC-358, DEC-359 (W1-50 DP-8, DP-9), DEC-360 (W1-11 DP-2: the `Role: owner` trailer; W1-50 KPI line), DEC-361, DEC-362 (W1-16 DP-1 and the UI), DEC-363 (idle tickets and the six), DEC-364 to DEC-368 (W1-28 DP-1, DP-2, DP-3, DP-5, DP-6, DP-8), DEC-369 (second scan in pre-commit; W1-40 KPI line), DEC-370 (G-20 by exact path), DEC-371 (`gov launch` from now on), DEC-372 (latency cases re-run alone). |

## 84. Delegated decisions on W1-19's and W1-28's packages (register v0.84, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on packages the W1-19 (`DAEO-t6hf`) and W1-28
(`DAEO-9279`) ticket leads returned. For each the test designer's, the lead's and the orchestrator's recommendations
agree, the confidence is medium or higher, and the choice is reversible. W1-19's DP-1, DP-2, DP-6, DP-7 and its four
install packages, and W1-28's DP-10 (the freeze flag when a rollback fails), go to the owner.

### DEC-373 — W1-19 DP-3: how warm p95 and the rerank process's peak RAM are measured
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-19 package DP-3, option (a) for both; confidence medium · **Under:** CAP-18.a, DEC-074 R1
- **Decision:**
  - Warm: one process per tier builds the index, asks three questions outside the set, then times each query of
    the dev query set once; p95 by nearest rank, against 0.5 s.
  - Peak RAM: the largest `VmHWM` of the calling process and every descendant, sampled every 50 ms, leaving out
    `ollama` and its children, against 2.5 × 10⁹ bytes. A reranker that detaches from the process tree is not seen:
    a residual.

### DEC-374 — W1-19 DP-4 and DP-5: an absent reranker keeps the fused order, and the manifest is held in the shared store
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-19 packages DP-4 option (a) and DP-5 option (a); confidence medium · **Under:** CAP-10.a, CAP-18.a, DEC-257, DEC-340
- **Decision:**
  - When the default reranker cannot be loaded, the fused search keeps the fused order, reports that nothing was
    reranked, and does not raise.
  - The index manifest is held in the shared store and read through the semantic module. It names the embedder and
    the reranker, each with its model and revision; the embedder's revision is the one observed from Ollama's model
    list, not a constant.
  - The names of the functions and keys follow the owner's answer to DP-1.

### DEC-375 — W1-28 DP-9 and DP-11: one record commit per released ticket, and no record when nothing was reverted
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-28 packages DP-9 option (a) and DP-11 option (a); confidence medium-high · **Under:** DEC-357, DEC-367, CAP-05.d
- **Decision:**
  - `gov pause --cancel-agents` writes one record commit per released ticket, each with that ticket's `Task:` and
    `Reverts-Task:` trailers. A cancel that releases nothing makes no commit.
  - A rollback that reverts nothing, on its first run as on a repeat, writes no record commit.

| Version | Date | Change |
|---|---|---|
| 0.84 | 2026-10-05 | Delegated under DEC-220: DEC-373 (W1-19 DP-3: warm p95 and peak RAM), DEC-374 (W1-19 DP-4, DP-5: absent reranker, manifest in the shared store), DEC-375 (W1-28 DP-9, DP-11: one record commit per released ticket; none when nothing was reverted). |

## 85. Owner actions and answers of 2026-10-05 after the first launched sessions (register v0.85, appended by the W1 orchestrator on branch `w1/integrate`)

The owner's actions through the operator and answers of 2026-10-05, on the held-out copy incident, W1-16 DP-1,
W1-28 DP-10, W1-19's packages and installs, and the launcher. DEC-372 stays as recorded.

### DEC-376 — The held-out copies are removed, and no worker bulk-copies the tree
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on the incident the W1-28 ticket lead reported · **Under:** DEC-213, DEC-218, MR-3
- **Decision:**
  - The owner removed `/tmp/gov-launch-independent-test-designer-5e58yicw` (3.4 GB, no process using it) through
    the operator.
  - 17 more copies of `governance/project/held-out.yaml` were found and deleted, all inside pytest's temporary test
    projects under one launched engineer session's temp folder (`/tmp/gov-launch-engineer-_foa_zpg/`). None remain.
  - 78 other `gov-launch-*` folders remain in `/tmp`. When no lead is running, the orchestrator tells the owner, so
    the operator can clear them.
  - The orchestrator's rule that a worker never bulk-copies the tree is confirmed. The incident is recorded in
    `governance/project/bootstrap.md`.

### DEC-377 — W1-16 DP-1: W1-16 closes with the designer's 26 questions, and the exit run measures the comparable hit@5
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-16 package DP-1 option (A) · **Settles:** DEC-361 · **Under:** CAP-12.a, DEC-362
- **Decision:**
  - No C1 question set exists under `~/gov-os-workbench/s0b2/out/`. S0b2's code-intelligence comparison scored
    hit@5 on the dev query set's code classes, as `~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md` reports.
  - W1-16 closes with the designer's 26 questions (option A).
  - W1-42 gets a KPI line, in its own commit: the Wave 1 exit run measures callers/impact hit@5 on the dev query
    set's code classes, the measurement comparable to S0b2's baseline. A worker may read that report by exact path.
  - The `--ui=false` wrapper change (DEC-362) and its registry note go in the same round; then W1-16 closes.

### DEC-378 — W1-28 DP-10: a rollback sets the freeze flag first, and it stays
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-10 option (a) · **Under:** DEC-365, DEC-368, CAP-05.c
- **Decision:**
  - `gov pause --rollback` sets the freeze flag first, once the caller is allowed, and the flag stays whatever the
    rollback's result (a conflict, an unknown ticket, a dirty tree). Only the owner lifts it.
  - The test designer's three pinned readings are confirmed: `Role:` on a revert commit is the caller's (`owner`
    with `GOV_ROLE` unset, `orchestrator` otherwise); the refusal code is `PAUSE_REFUSED`; a cancel that releases
    nothing makes no commit.

### DEC-379 — W1-19 DP-1: the interface of the semantic route, the fusion and the rerank, as proposed
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-19 package DP-1 option (a) · **Under:** CAP-10.a, CAP-18.a, DEC-340, DEC-260
- **Decision:**
  - `gov.retrieval.semantic.refresh(root)` returns `available`, `facet` (`"semantic"`), `state`, `reason`.
  - `gov.retrieval.semantic.search(root, query, refresh=True)` returns the same plus `hits` (W1-17's chunk records,
    nearest first); `refresh=False` never writes.
  - `gov.retrieval.semantic.manifest(root)` returns `None` without an index, else
    `{"embedder": {"model", "revision"}, "reranker": {"model", "revision"}}`.
  - `gov.retrieval.fusion.rrf(routes, k=60)` returns one list, each chunk once, with `score` (the sum of
    `1/(k+rank)`) and `routes`.
  - `gov.retrieval.fusion.search(root, query, limit, refresh=True, reranker=None)` returns `hits`, `facets` and
    `reranked`; a limit cuts after the rerank.
  - `gov.retrieval.rerank.rerank(query, candidates, reranker=None)` returns the candidates in score order with
    `rerank_score`.
  - `reranker` is a loader: a no-argument function returning `score(query, texts)`. It is called at the first rerank
    and not before, and one rerank calls `score` once with every candidate's text.
  - No function raises because Ollama, `sqlite_vec` or the reranker is absent.

### DEC-380 — W1-19 DP-2: mean hit@5 follows S0b2's own method where it is stated
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-19 package DP-2 · **Under:** CAP-18.a, DEC-074 R1, DEC-383
- **Decision:** A test designer reads `~/gov-os-workbench/s0b2/out/RESULTS.md` by exact path (and the
  code-intelligence report of DEC-377 if needed), and the scoring follows S0b2's own method where it is stated there.
  If it is not stated, option (a): a hit when one `must_cite` path is in the first five; queries without a gold path
  left out; a percentage per tier; the mean of the two tiers.

### DEC-381 — W1-19 DP-6: a namespace that is not embedded never reaches the vectors
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-19 package DP-6 option (a) · **Settles:** the DEC-289 residual on `embedding_policy` · **Under:** CAP-10.a, CAP-03
- **Decision:** A namespace whose `embedding_policy` is `not embedded` never reaches the vectors. This holds before
  any live index is built.

### DEC-382 — W1-19 DP-7: the G-17 read is accepted
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-19 package DP-7 option (a) · **Extends:** DEC-370
- **Decision:** The test designer's read of G-17's row is accepted, and DEC-370 extends to G-17.

### DEC-383 — The S0b2 files a worker may read, by exact path only
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Under:** DEC-198, DEC-310, DEC-370
- **Decision:** Workers may read these S0b2 files by exact path only:
  `~/gov-os-workbench/s0b2/out/RESULTS.md`, `~/gov-os-workbench/s0b2/out/GLUE_REQUIREMENTS.md`,
  `~/gov-os-workbench/s0b2/out/TOOL_REGISTRY.yaml` and `~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md`.
  Nobody lists folders there, and nobody touches `s0b2/probe/`.

### DEC-384 — W1-19's installs: complete packages from the S0b2 registry, verifying what is on disk
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Under:** DEC-083, DEC-195, DEC-198
- **Decision:**
  - The orchestrator fills the four install packages from `~/gov-os-workbench/s0b2/out/TOOL_REGISTRY.yaml`.
  - Verifying the artefacts already on disk (the Ollama executable, the embedding model, the reranker snapshot)
    against their recorded hashes is preferred over downloading again.
  - The package for sqlite-vec says which path is proposed in the Python that runs pytest.
  - The complete packages come to the owner. Meanwhile the model-free part of W1-19 is built.

### DEC-385 — No test fixture copies the held-out file
- **Status:** ACCEPTED (owner, 2026-10-05; stricter-only, the ticket is the orchestrator's choice) · **Basis:** OWNER · **Under:** DEC-213, DEC-376
- **Decision:**
  - Every test fixture that copies the repository leaves `governance/project/held-out.yaml` out, so it is never
    copied into a temporary project.
  - Ticket (orchestrator): W1-28 (`DAEO-9279`), whose round is about to start and whose first round met the
    incident. Its test designer revises the copying fixtures of the earlier suites; the KPI line is added in its
    own commit.

### DEC-386 — The launcher removes its temp folder and starts product-spec workers sandboxed
- **Status:** ACCEPTED (owner, 2026-10-05; stricter-only, the ticket is the orchestrator's choice) · **Basis:** OWNER · **Amends:** DEC-371 · **Under:** DEC-159, DEC-311, CAP-58
- **Decision:**
  - `gov launch` removes its per-session temp folder when the session ends.
  - The launcher gets a `product-spec` role with an empty network allowlist, so product-spec workers are sandboxed
    too. When it is merged, the DEC-183 form ends for that role.
  - Ticket (orchestrator): W1-28 (`DAEO-9279`), with `src/gov/launch/**` and `tests/unit/launch/**` added to its
    `allowed_paths` and the two KPI lines added, in its own commit. The launcher lines get a reviewer pass
    (brief A3) although the ticket's profile is STANDARD.

| Version | Date | Change |
|---|---|---|
| 0.85 | 2026-10-05 | Owner: DEC-376 (held-out copies removed; no bulk copy of the tree), DEC-377 (W1-16 closes with the designer's questions; W1-42 KPI line), DEC-378 (W1-28 DP-10 (a) and three readings), DEC-379 to DEC-382 (W1-19 DP-1, DP-2, DP-6, DP-7), DEC-383 (the four S0b2 files a worker may read), DEC-384 (W1-19 installs), DEC-385 (fixtures leave the held-out file out; W1-28), DEC-386 (the launcher removes its temp folder and gets a product-spec role; W1-28). |

## 86. Delegated decisions on W1-11's packages DP-5 and DP-7 (register v0.86, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220 and its stricter-only rule, on two of the three packages
the W1-11 (`DAEO-be7u`) ticket lead returned after three review rounds. Both options only make the checker report
more; the lead's and the orchestrator's recommendations agree, the confidence is medium or higher, and both are
reversible. DP-6 (how the approval rule reads merges) decides what counts as the owner's approval fact of DEC-360
and goes to the owner.

### DEC-387 — W1-11 DP-5 and DP-7: unreadable frontmatter is a finding, and the checker ignores replace refs
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-11 packages DP-5 option (a), confidence medium, and DP-7 option (a), confidence medium-high · **Under:** CAP-51.a, CAP-01.b, DEC-329, DEC-360
- **Decision:**
  - A Markdown file of `HEAD` whose head looks like frontmatter and cannot be read as the store reads it (a
    byte-order mark or a blank line before `---`, a first line such as `--- # c`, CR-only line ends, UTF-16) is
    reported as `FRONTMATTER_UNREADABLE`. A file with `type: decision` and no `id` is a decision that fails.
  - Ids outside the grammar with no `type`, and the extensions `.MD` and `.markdown`, are residuals.
  - The checker runs git with replace refs off. A loose object overwritten in place in the root's own `.git` is a
    residual, left to W1-50 and the worker sandbox.
  - Accepted as built, each failing closed: `FRONTMATTER_UNREADABLE` as an eighth finding code; a decision is
    followed by its `id`, and "later" is by ancestry, not by date; `check` needs no loaded store; a history it cannot
    read (a shallow or partial clone) is a `GovError`; every `GIT_*` variable is dropped when the checker runs git.

| Version | Date | Change |
|---|---|---|
| 0.86 | 2026-10-05 | Delegated under DEC-220 (stricter-only): DEC-387 (W1-11 DP-5: unreadable frontmatter is a finding; DP-7: replace refs off; the checker's interface as built). W1-11 DP-6 goes to the owner. |

## 87. Delegated decisions on W1-19's packages DP-8 and DP-9, and W1-16's UI switch as built (register v0.87, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220 and its stricter-only rule. Each is reversible, the test
designer's, the lead's and the orchestrator's recommendations agree, and the confidence is medium or higher. The
owner was told of all three on 2026-10-05 and may reverse any of them.

### DEC-388 — W1-19 DP-8 and DP-9: an unknown `embedding_policy` is not embedded; hit@5 follows S0b2's stated method
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-19 packages DP-8 option (a), confidence medium-high, and DP-9 option (a), confidence medium · **Under:** DEC-380, DEC-381, DEC-383, CAP-09
- **Decision:**
  - DP-8: the closed list of `embedding_policy` values is `embedded` and `not embedded`. Any other value is read as
    not embedded (fail closed). This repository's path map gives `template/**` the value
    `embedded, except vendored code`, so `template/**` is found by the lexical route only. Giving the vendored paths
    their own namespace, so that the rest of `template/**` can say `embedded`, is a follow-up for whoever wants it
    embedded; it is a path map edit outside W1-19's paths.
  - DP-9: `~/gov-os-workbench/s0b2/out/RESULTS.md` states S0b2's method ("each candidate's top-5 distinct paths per
    query against `must_cite` / `must_not_cite`", over "52 queries, ten classes", "Mean of ten classes | 85.0"), so
    under DEC-380 mean hit@5 is scored per class, as the mean of the ten classes, over all 52 queries. The two
    queries with no gold path (`DQ-A-21`, `DQ-A-24`) count as misses, which caps the mean at 96.3 and matches S0b2's
    figures for their two classes. DEC-380's fallback (leave them out; per tier) does not apply, because the method
    is stated.
  - Also stricter than DEC-381 states, accepted as built: a path in several namespaces is embedded only if every
    one says `embedded`; a path in no namespace is not embedded.

### DEC-389 — W1-16: the wrapper turns the UI off with `config set ui_enabled false`, not `--ui=false`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05; the purpose of DEC-362 is unchanged) · **Basis:** the W1-16 ticket lead's fourth round; observed on codebase-memory-mcp 0.11.0 · **Amends:** DEC-362 (the mechanism only) · **Under:** DEC-083, CAP-09
- **Decision:**
  - `--ui=false` does nothing on the `cli` calls the wrapper makes, and the server form serves the UI once while it
    persists the switch. The wrapper therefore runs `codebase-memory-mcp config set ui_enabled false` in the
    repository's home before every `cli` call; if that fails, the call raises and the tool is not run.
  - The acceptance tests assert the outcome (no `ui.serving` line, nothing listening on the UI port, the setting
    `false`; a caller's environment or argument cannot turn it back on), not the argument.
  - The tool persists `{"ui_enabled": false, "ui_port": 9749}` in
    `<repository>/.gov-runtime/codeintel/home/config.json`. This is recorded in the tool registry's note for
    codebase-memory-mcp. `~/.cache/codebase-memory-mcp` is not changed.

| Version | Date | Change |
|---|---|---|
| 0.87 | 2026-10-05 | Delegated under DEC-220: DEC-388 (W1-19 DP-8: an unknown `embedding_policy` is not embedded; DP-9: hit@5 per class over 52 queries, as S0b2 states), DEC-389 (W1-16: the UI is turned off with `config set ui_enabled false`; amends the mechanism of DEC-362). |

## 88. Delegated decisions on W1-50's packages DP-11 to DP-16 (register v0.88, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220 and its stricter-only rule, on the packages the W1-50
(`DAEO-xnbx`) ticket lead returned after its implementation and two reviews. Every option taken only makes the
containment check report more, each is reversible, and the lead's and the orchestrator's recommendations agree.
DP-11 and DP-12 touch owner decisions (DEC-360, DEC-366, DEC-367): they are kept as built, which is the literal and
stricter reading, and were told to the owner, who may choose otherwise.

### DEC-390 — W1-50 DP-11 to DP-16: the stricter reading in each case
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-11 (a), DP-12 (a), DP-13 (a), DP-14 (c), DP-15 (a), DP-16 (a finding); confidence medium-low to medium-high · **Under:** CAP-58, DEC-254, DEC-269, DEC-358, DEC-359, DEC-360
- **Decision:**
  - DP-15: when a merge commit has a parent that is not among the commits new in the move, every path it changes
    against its first parent is judged by the merge commit's own trailers, or against the caller without them. An
    ordinary integration merge, whose other parent is new in the move, is read as before (DEC-269).
  - DP-16: a change under `.tickets/**` in a commit that carries a worker's `Role:` trailer is a finding.
  - DP-13: a ticket file whose first version is already `closed` is not a close commit; the close commit itself is
    not "before" itself when it carries a worker's trailers; a close made by a merge commit does not count.
  - DP-14: a ticket's state and `allowed_paths` are read from `HEAD` and from the working tree, and both must allow.
  - DP-11, as built until the owner says otherwise: a commit carrying `Role: owner` that becomes new to `HEAD` in an
    agent session's call is a finding, also when it was made earlier from the owner's console and arrives by a merge
    or a fast-forward. Such a finding is a record of a permitted action (DEC-254).
  - DP-12, as built until the owner says otherwise: the revert commits and the record commit of
    `gov pause --rollback` are judged like any other commit; where they are findings, the findings are records.
  - `.git/info/grafts` is closed off for the check's git calls; this needs no decision, only tests and a fix.

| Version | Date | Change |
|---|---|---|
| 0.88 | 2026-10-05 | Delegated under DEC-220 (stricter-only): DEC-390 (W1-50 DP-11 to DP-16: a merge commit with a parent not new in the move is judged on its own change; a worker-trailer commit under `.tickets/**` is a finding; close-commit edges fail closed; ticket state from HEAD and the working tree together; DP-11 and DP-12 as built, told to the owner). |

## 89. Delegated decisions on W1-20's packages DP-1 to DP-7 (register v0.89, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on the packages the W1-20 (`DAEO-jozo`, P2, STANDARD)
ticket lead returned with its acceptance tests. Each is reversible, the test designer's, the lead's and the
orchestrator's recommendations agree, and the confidence is medium or higher. One part of DP-5 changes the fixed list
of stopping reasons of ADR-0002 §4 and goes to the owner.

### DEC-391 — W1-20 DP-1 to DP-7: the interface, the ids, the depth, the code facet and the gaps of `gov closure`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-20 packages DP-1 (a), DP-2 (a), DP-3 (a), DP-4 (a), DP-5 (gap reasons), DP-6 (a), DP-7 (b); confidence medium to high · **Under:** CAP-57.a, CAP-09, DEC-033, DEC-034, DEC-035, DEC-080, DEC-317, DEC-322, DEC-344
- **Decision:**
  - DP-1: both `gov closure (--depth N | --radius R) <id>...` and `gov.closure.closure(root, ids, depth=N)`, which
    returns the envelope's `result`. Its keys: `start`, `depth`, `stopping_reason`, `closure` (`id`, `kind`), `gaps`
    (`id`, `reason`), `facets`, `uncommitted`.
  - DP-2: the start ids are the untyped ids on the command line. A record id is a record; anything else is asked of
    the code index as a symbol name. The eight typed edges are followed both ways, and a symbol's callers and callees
    are followed. No text scan, no trailer edges, no record-to-symbol edge.
  - DP-3: `--depth N` is the plain input; `--radius R` gives R0 and R1 → 1, R2 → 3, R3 and above → 8, as constants
    (DEC-035's placeholders, read as hops).
  - DP-4: the code facet is asked only about a start id that is no record and about symbols reached from a symbol.
    A record's edge to no record is `UNRESOLVED` without asking. When the facet cannot answer, `facets.code` is
    `unavailable`, each such id is a gap with reason `FACET_UNAVAILABLE`, the stopping reason is `FACET_UNAVAILABLE`,
    and the record side is returned as usual. A closure never builds the store or the code index.
  - DP-5, the gap reasons: each gap carries `DEPTH_LIMIT_REACHED`, `UNRESOLVED` or `FACET_UNAVAILABLE`. **With the
    owner:** the stopping reason when unresolved ids are the only gaps (recommended: a sixth value `UNRESOLVED_IDS`,
    a change to ADR-0002 §4). Until the answer, the tests hold only that it is not `CLOSURE_COMPLETE`, the code keeps
    the value in one constant, and the ticket is not merged.
  - DP-6: `callees(root, name)` is added to `gov.codeintel` beside `callers`, in its own commit. The ticket's
    `allowed_paths` get `src/gov/codeintel/**` and `tests/unit/codeintel/**` for it (the DEC-260 form), and W1-16's
    suite is run again.
  - DP-7: the result names, under `uncommitted`, the sorted paths `git status --porcelain` names. A check that
    `HEAD` is among the store's commits is left to W1-27.

| Version | Date | Change |
|---|---|---|
| 0.89 | 2026-10-05 | Delegated under DEC-220: DEC-391 (W1-20 DP-1 to DP-7: command and function, untyped start ids and edges both ways, depth by radius 1/3/8, the code facet asked lazily and stated when unavailable, three gap reasons, `callees` added to `gov.codeintel`, `uncommitted` paths). The stopping reason for unresolved ids alone goes to the owner. |

## 90. Delegated decision on W1-28's package DP-13 (register v0.90, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on one of the three packages the W1-28 (`DAEO-9279`) ticket
lead returned with DONE. It is reversible, the lead's and the orchestrator's recommendations agree, and the
confidence is medium. DP-12 (the product-spec role file and agent definition) and DP-15 (the copied settings file's
held-out deny line) go to the owner.

### DEC-392 — W1-28 DP-13: the launcher's temp folder when a signal arrives or the removal fails
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-28 package DP-13 options 1a, 2a and 3a, confidence medium; the reviewer's findings F1 and F2 · **Amends:** DEC-386 · **Under:** DEC-332, DEC-159, CAP-58
- **Decision:**
  - When the removal of the temp folder fails, `gov launch` still ends with the session's exit code (DEC-332) and
    writes one line to stderr that names the folder that stayed.
  - SIGTERM and SIGHUP to the launcher are handled as an interrupt is: the session is ended and the folder removed.
  - After an interrupt the launcher's exit code is 130.
  - Ticket (orchestrator): W1-32 (`DAEO-8goq`), which already depends on W1-28, with `src/gov/launch/**` and
    `tests/unit/launch/**` added to its `allowed_paths` and one KPI line, in its own commit. W1-28 closes as built.

| Version | Date | Change |
|---|---|---|
| 0.90 | 2026-10-05 | Delegated under DEC-220: DEC-392 (W1-28 DP-13: a failed removal keeps the session's exit code and names the folder; SIGTERM and SIGHUP as an interrupt; exit code 130; carried by W1-32). W1-28 DP-12 and DP-15 go to the owner. |

## 91. Delegated decisions on W1-20's packages DP-A and DP-B (register v0.91, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on two packages the W1-20 (`DAEO-jozo`) ticket lead
returned after the implementation. Both are what is built, reversible in one line before W1-21 is written, and the
lead's and the orchestrator's recommendations agree at medium confidence or higher. DP-8 (the tests' fixed list of
stopping reasons) follows the owner's answer on DP-5 (DEC-391).

### DEC-393 — W1-20 DP-A and DP-B: the depth cut wins over unresolved ids; an unasked code facet says `not_asked`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-20 packages DP-A option (a), confidence medium, and DP-B option (a), confidence medium-high · **Amends:** DEC-391 · **Under:** CAP-57.a, DEC-034
- **Decision:**
  - The stopping reason is chosen in this order: `FACET_UNAVAILABLE` when the code facet could not answer, then
    `DEPTH_LIMIT_REACHED` when any gap lies beyond the depth, then the value for unresolved ids alone (with the
    owner, DEC-391), then `CLOSURE_COMPLETE`. The reason on each gap carries the rest.
  - `facets.code` is `not_asked` for a closure in which the code facet was never asked.
  - Accepted as built: a repository without a store answers `STORE_MISSING` with exit code 1; a depth below zero is
    refused with `CLOSURE_DEPTH_INVALID`; once the facet fails in a run it is not asked again; `start` is sorted and
    de-duplicated.

| Version | Date | Change |
|---|---|---|
| 0.91 | 2026-10-05 | Delegated under DEC-220: DEC-393 (W1-20 DP-A: the order of stopping reasons; DP-B: `facets.code` is `not_asked` when the facet was not asked; four engineer choices as built). |

## 92. Delegated decisions on W1-50's packages DP-17 and DP-18 (register v0.92, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220 and its stricter-only rule. The DP-15 rule of DEC-390 was the
orchestrator's own and was wrong in two ways, which the closing round's reviewer showed by running them: it flags an
ordinary merge-back of a ticket branch that earlier took the integration branch (a false finding, KPI failure line
1), and one extra empty commit evades it. The rule below replaces it. Against DEC-269, which it refines, it only
makes the check report more; it is reversible, and the lead's and the orchestrator's recommendations agree at
medium-high confidence. The owner was told on 2026-10-05.

### DEC-394 — W1-50 DP-18 and DP-17: a merge commit's own change by the three-way rule; a ticket-file commit in a worker's call
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-18 option (a) and DP-17 option (a), confidence medium-high; the third reviewer's findings F1 and F2 · **Amends:** DEC-390 (replaces its DP-15 rule), DEC-269 (refines "content a parent holds") · **Under:** CAP-58, DEC-254, DEC-359
- **Decision:**
  - DP-18: a path a merge commit changes against its first parent is brought by another parent only when that
    parent's content of the path differs from the merge base of the parents; with several merge bases, it must differ
    from every one. Otherwise the change is the merge commit's own, judged by the merge commit's trailers, or against
    the caller without them. Whether a parent is new in the move no longer matters.
  - Consequences accepted: a merge that drops the first parent's later changes in favour of another parent's
    unchanged content (for example `-s ours` turned round, or by hand) is now the merge commit's own change. An
    ordinary integration merge and an ordinary merge-back stay silent.
  - DP-17: in a worker's call, any commit of the move that changes a path under `.tickets/**` is a finding, with or
    without trailers.
  - The check is not made the live one (the branch is not merged) before a reviewer has run the new rule against
    ordinary merges, merge-backs, octopus merges and criss-cross histories.

| Version | Date | Change |
|---|---|---|
| 0.92 | 2026-10-05 | Delegated under DEC-220 (stricter-only): DEC-394 (W1-50 DP-18: a merge commit's own change is read by a three-way rule against the merge base, replacing DEC-390's DP-15 rule; DP-17: a `.tickets/**` commit in a worker's call is a finding). |

## 93. Owner actions and answers of 2026-10-05, evening (register v0.93, appended by the W1 orchestrator on branch `w1/integrate`)

The owner's actions through the operator and the owner's answers to the packages open on 2026-10-05, as given to the
orchestrator. Where an answer leaves the ticket to the orchestrator, the choice is named in the entry.

### DEC-395 — Temp folders cleared; temp hygiene delegated to the orchestrator
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Amends:** DEC-376 · **Under:** DEC-385, DEC-386
- **Decision:**
  - Done by the owner through the operator: `/tmp/pytest-of-usain` and all 113 `/tmp/gov-launch-*` folders are
    removed (about 31 GB). `.git/config.lock` had already gone and no lock file remains. `w1/integrate` is pushed at
    `6b20a0ad`.
  - Delegated: at each checkpoint, when no lead, worker or regression is running, the orchestrator removes
    `/tmp/pytest-of-usain` and any leftover `/tmp/gov-launch-*` folder. If the guard refuses, it tells the owner
    instead. Each cleanup is recorded in the orchestrator's checkpoint. Nothing in those folders is opened.

### DEC-396 — W1-20 DP-5: a sixth stopping reason, `UNRESOLVED_IDS`
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, W1-20 package DP-5 option (a) · **Amends:** ADR-0002 §4, DEC-034, DEC-391 · **Under:** CAP-57.a
- **Decision:** the stopping reason when unresolved ids are the only gaps is `UNRESOLVED_IDS`. The fixed list of
  ADR-0002 §4 is amended under this decision, in its own commit. A test designer adds the value to the W1-20 tests'
  list. W1-20 is then merged and closed.

### DEC-397 — W1-19 installs: approved (DEC-083)
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Amends:** DEC-384 · **Under:** DEC-083, DEC-195, DEC-074
- **Decision:**
  - Ollama 0.35.0 and `qwen3-embedding:0.6b` are approved for use as verified on disk; the embedding model gets its
    row in the tool registry.
  - sqlite-vec 0.1.9 is approved, installed by
    `/usr/bin/python3 -m pip install --user --break-system-packages sqlite-vec==0.1.9`; the sha256 of `vec0.so` is
    verified afterwards and recorded.
  - The reranker does not depend on the S0b2 virtual environment in the workbench. A fresh one is created at
    `~/.local/share/gov-os/reranker-venv` with the exact pins S0b2 recorded (Python 3.12, sentence-transformers
    6.1.0, torch 2.14.1+cu130, transformers 5.18.0), by S0b2's recorded install method; the existing Hugging Face
    snapshot is reused. It enters the registry with its pins and its uninstall command. The default reranker process
    starts from that environment.
  - The orchestrator runs the installs; the guard's ask is the owner's approval. W1-19 is then finished.

### DEC-398 — W1-11 DP-6: the approval rule reads merges by the merge base, with one helper shared with containment
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, W1-11 package DP-6 option (b) · **Amends:** DEC-394 · **Under:** DEC-360, DEC-387, CAP-51.a
- **Decision:**
  - The approval rule judges a merge against the merge base. It shares one helper with W1-50's three-way rule
    (DEC-394), so the approval check and containment read merges the same way.
  - Where several merge bases exist (a criss-cross history), it fails closed.
  - One design batch, then the engineer and a review.
  - Orchestrator's reading, told to the owner: the shared helper is the one place that reads a merge, so it fails
    closed for both callers. With several merge bases nothing counts as brought by another parent; in containment
    every path such a merge commit changes against its first parent is its own change. This is stricter than
    DEC-394's "must differ from every one" and replaces that clause. W1-50 builds the helper; W1-11 uses it after
    W1-50 is merged.

### DEC-399 — W1-28 DP-15: whole-tree fixtures strip the held-out deny line from copied settings files
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, W1-28 package DP-15 option (a) · **Amends:** DEC-385 · **Under:** CAP-58
- **Decision:** the fixtures that copy the whole tree strip the held-out deny line from the copied
  `.claude/settings.json`, as W1-46's and W1-47's fixtures do. Nobody displays that line. Ticket (orchestrator):
  W1-50 (`DAEO-xnbx`), in the second branch of DEC-402, as a test designer's revision.

### DEC-400 — W1-28 DP-12: the product-spec role file and agent definition are rewritten
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, W1-28 package DP-12 option (a) · **Under:** DEC-386, DEC-312, DEC-352
- **Decision:** the product-spec role file is rewritten to say that `gov launch` starts the role sandboxed. The
  orchestrator drafts the text of `.claude/agents/product-spec.md` in its scratch folder and tells the owner, and the
  operator places it.

### DEC-401 — W1-50 DP-11 and DP-12 kept as built; DEC-394 accepted on a condition; DEC-388 and DEC-389 stand
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Under:** DEC-254, DEC-390, DEC-394
- **Decision:**
  - W1-50 DP-11 and DP-12 stay as built; those findings are records (DEC-254).
  - DEC-394 replacing DEC-390's DP-15 rule is accepted, provided the reviewer's criss-cross and replay tests pass
    before the merge.
  - No objection to DEC-388 and DEC-389.
  - DEC-372 stands as recorded: an owner decision, its handling delegated.

### DEC-402 — The freeze flag carries a marker; an empty placeholder is no freeze (high priority)
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Amends:** DEC-176, DEC-365, DEC-378 · **Under:** CAP-58, DEC-159, DEC-180
- **Context:** launched sessions were refused with "frozen: all writes denied" although no freeze was set. Likely
  cause: the launcher denies `.gov-runtime/freeze` also when it does not exist, so the sandbox creates an empty
  placeholder at that path on the real filesystem while a worker's command runs, and the guard, outside the sandbox,
  reads it as a freeze.
- **Decision:**
  - A real freeze flag carries a marker line written by `gov pause` (for example `FROZEN`, with who and when).
  - The guard treats an empty file, or one without that marker, as no freeze, and records its presence as a
    residual observation.
  - The launcher stops denying the freeze path when it does not exist at launch.
  - The cause is verified with one live launched session before anything is built.
  - Ticket (orchestrator): W1-50 (`DAEO-xnbx`, P1, FULL, in progress), on a second branch and worktree of its own
    (`w1/W1-50-freeze`), with `src/gov/guard/decide*`, `src/gov/pause/**`, `src/gov/launch/**`,
    `tests/unit/guard/**`, `tests/unit/pause/**` and `tests/unit/launch/**` added to its `allowed_paths` and the KPI
    lines added, in its own commit. W1-32, which holds the launcher paths, is not ready (W1-31 is open) and cannot
    be run with priority. W1-50 closes when both branches are merged.

| Version | Date | Change |
|---|---|---|
| 0.93 | 2026-10-05 | Owner: DEC-395 (temp folders cleared; temp hygiene delegated), DEC-396 (W1-20 DP-5: `UNRESOLVED_IDS`; ADR-0002 §4 amended), DEC-397 (W1-19 installs approved; a fresh reranker environment), DEC-398 (W1-11 DP-6: merge-base rule, one helper shared with containment, criss-cross fails closed), DEC-399 (W1-28 DP-15), DEC-400 (W1-28 DP-12), DEC-401 (W1-50 DP-11 and DP-12 as built; DEC-394 accepted on a condition; DEC-388 and DEC-389 stand), DEC-402 (the freeze flag's marker; W1-50). |

## 94. Delegated decision on W1-50's packages DP-19 and DP-20 (register v0.94, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220 and its stricter-only rule, on the two packages the W1-50
(`DAEO-xnbx`) ticket lead returned after its fifth round. The owner's two conditions of DEC-401 passed in that round
(criss-cross histories fail closed; a replay of 174 real merges flags none by mistake). Both options only make the
check report more, are reversible before W1-11 uses the helper, and the lead's and the orchestrator's recommendations
agree at medium confidence or higher. The owner was told on 2026-10-05.

### DEC-403 — W1-50 DP-20 and DP-19: the merge helper reads every parent; an octopus with a crossing parent fails closed
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-20 option (a), confidence medium-high, and DP-19 option (a), confidence medium; the fourth reviewer's finding F1 (seven merge shapes that undo acceptance tests silently) · **Amends:** DEC-394, DEC-398 ("against its first parent") · **Under:** CAP-58, DEC-269, DEC-401
- **Decision:**
  - DP-20: the one helper that reads a merge (`gov.guard.containment_merge.read_merge`) reads every parent the way
    it reads the first. A path where the merge commit's content differs from any parent's is the merge commit's own
    change, unless another parent brought it by the three-way rule: that parent's content differs from the merge
    base and the merge commit has that parent's content. So a merge that keeps one parent's content and drops what
    another parent changed is judged. With several merge bases, or none, every path that differs from any parent is
    the merge commit's own change.
  - DP-19: an octopus merge in which one other parent has several merge bases, or none, with the first parent fails
    closed as a whole. An octopus whose other parents cross only each other is read parent by parent.
  - The helper raises a public error, and refuses a `commit` argument that is not a commit id.
  - The owner's conditions of DEC-401 are run again on this rule before the branch is merged.

| Version | Date | Change |
|---|---|---|
| 0.94 | 2026-10-05 | Delegated under DEC-220 (stricter-only): DEC-403 (W1-50 DP-20: the merge helper reads every parent, so a merge that drops a parent's change is judged; DP-19: an octopus merge with a crossing parent fails closed as a whole). |

## 95. Delegated decisions on the W1-50 freeze branch's packages DP-F1, DP-F3, DP-F4 and DP-F5 (register v0.95, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on four of the five packages the lead of W1-50's freeze
branch (`w1/W1-50-freeze`) returned after its first round. That round confirmed the cause DEC-402 names with one live
launched session: the flag's path was absent before, an empty read-only file stood there while the launched worker's
command ran, the lead's own write was refused as frozen in that window, and the file was gone when the command ended.
With the branch's launcher no file appeared over a 66-second command. All four are P3, reversible, and the lead's and
the orchestrator's recommendations agree at medium confidence or higher. The fifth package, DP-F2 (what protects the
flag's path in a session launched while no flag existed), lowers a protection and is the owner's. The owner was told
on 2026-10-05.

### DEC-404 — W1-50 freeze branch: the marker line's layout; an unmarked file at launch; `gov pause` over a linked runtime folder; one builder test
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** packages DP-F3 option (a), confidence medium-high; DP-F1 option (a), medium; DP-F4 option (a), medium; DP-F5 option (a), high · **Under:** DEC-402, DEC-311, DEC-365
- **Decision:**
  - DP-F3: the flag's first line, as `gov pause` writes it, is `FROZEN <who> <when>` with single spaces; who is
    `owner` or `orchestrator` (the caller of DEC-365), when is UTC `YYYY-MM-DDTHH:MM:SSZ`.
  - The guard's reading is wider than what `gov pause` writes, as built and reviewed: any file at the flag's path
    that carries the word freezes, in any of the spellings the review probed; an empty file, or one without the
    word, is no freeze and its presence is recorded (DEC-402). A flag the guard cannot read, or a dangling link at
    the runtime folder, freezes.
  - DP-F1: `gov launch` denies the flag's path by name whenever a file exists there at launch, marked or not, as
    for any name that exists at launch (DEC-311). A placeholder renewed this way freezes nothing.
  - DP-F4: when `.gov-runtime` is a symbolic link, `gov pause` refuses with an error that names the link and
    writes nothing. The owner repairs the folder.
  - DP-F5: `tests/unit/install/**` is added to the ticket's `allowed_paths`, in its own commit, so the engineer
    updates the one builder test that sets an empty flag.
  - `gov pause` writes the flag by a temporary file and a rename, never through a link at the flag's path, and
    reads it back with the guard's own reader; `--off` over a directory is a clear refusal (the review's findings,
    tests already written).

| Version | Date | Change |
|---|---|---|
| 0.95 | 2026-10-05 | Delegated under DEC-220: DEC-404 (W1-50 freeze branch: the marker line is `FROZEN <who> <when>`; an unmarked file at the flag's path is still denied by name at launch; `gov pause` refuses over a linked runtime folder; one builder test's path added). |

## 96. Owner actions and answers of 2026-10-05, third round (register v0.96, appended by the W1 orchestrator on branch `w1/integrate`)

Given by the owner on 2026-10-05, after the W1-19 lead's third round, the W1-50 freeze branch's first round, and
DEC-400's drafts.

### DEC-405 — The product-spec role file and agent definition are placed
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** owner action through the operator · **Under:** DEC-400, DEC-254
- **Decision:**
  - `template/governance/kernel/roles/product-spec.md` and `.claude/agents/product-spec.md` are committed together
    in the main tree as `5d1d9cffc796240a86eb021bc6a03a3da243b1df` (Task: decision-record, Role: owner), each
    byte-identical to the orchestrator's draft.
  - If containment flags that commit, the finding is a record of an owner action (DEC-254).
  - W1-33's suite was run again at that commit: 113 passed, the field-by-field check among them.

### DEC-406 — W1-19 DP-10: a worker reads S0b2's R1 prototype by exact path; tuning on the dev set is not the fix
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** W1-19 package DP-10 option (a) · **Under:** DEC-397, DEC-388
- **Decision:**
  - A worker may read `/home/usain/gov-os-workbench/s0b2/sandbox/retrieval/r1/r1_retrieval.py` by that exact path.
    Folders there are never listed, and `s0b2/probe/` is never touched.
  - The reading finds how R1 ran the lexical query (ranked full-text or exact string), the candidate counts, the
    chunking and the reranker call.
  - If the difference lies outside W1-19's paths (for example W1-17's exact-string lexical route), it comes back as
    a package with the measured effect, not as a workaround.
  - Tuning on the dev set alone (option (c), a larger top-k) is not accepted as the fix.

### DEC-407 — W1-50 DP-F2: accepted for the merge; before W1-50 closes, the flag is compared around every Bash call and owner identity follows process ancestry
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** W1-50 freeze branch package DP-F2 option (a) now, option (b) and a new rule before the close · **Amends:** DEC-365 ("unset `GOV_ROLE` is the owner") · **Under:** DEC-402, DEC-404, DEC-311
- **Decision:**
  - Now, so the freeze branch can merge: W1-46's one live assertion is revised as a rewrite after implementation,
    reason "owner decision: freeze marker".
  - Before W1-50 closes, two things are built:
    - the containment check compares the freeze flag around every Bash call; a removed or emptied flag is a
      finding and is restored with its marker line;
    - the ancestry rule (owner identity): an owner-only action, such as lifting a freeze, refuses whenever any
      parent process of the command is a Claude Code session, whatever `GOV_ROLE` says. "`GOV_ROLE` unset" alone no
      longer means the owner, which closes `env -u GOV_ROLE gov pause --off` from a worker. The same rule applies
      wherever the code treats an unset `GOV_ROLE` as the owner.
  - The KPI lines are added to W1-50 in their own commit.

### DEC-408 — DEC-403 stands; three orchestrator choices are confirmed
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** owner answer · **Under:** DEC-403, DEC-402, DEC-398, DEC-397
- **Decision:**
  - DEC-403 (the symmetric merge rule; an octopus merge with a crossing parent fails closed): no objection.
  - Confirmed: the freeze work is carried by W1-50 and not by W1-32; the fail-closed reading of criss-cross merges
    applies to containment too; the reranker environment's extra pin `huggingface-hub` 1.33.0.

| Version | Date | Change |
|---|---|---|
| 0.96 | 2026-10-05 | Owner: DEC-405 (product-spec role file and agent definition placed, `5d1d9cff`), DEC-406 (W1-19 DP-10: an exact-path read of S0b2's R1 prototype; dev-set tuning is not the fix), DEC-407 (W1-50 DP-F2: accepted for the merge; before the close, the flag is compared around every Bash call and owner-only actions refuse under a Claude Code parent process), DEC-408 (DEC-403 stands; three orchestrator choices confirmed). |

## 97. Owner decision of 2026-10-05: lifting a freeze requires the owner in person (register v0.97, appended by the W1 orchestrator on branch `w1/integrate`)

Given by the owner on 2026-10-05. It replaces the ancestry rule of DEC-407. The owner named DEC-367 and the W1-28
DP-3 answer as amended; the W1-28 DP-3 answer is DEC-365 ("lifting a freeze works only with `GOV_ROLE` unset"), which
this decision amends. DEC-367 (the record of a rollback or a cancel) says nothing about lifting and its text is not
changed here; the orchestrator told the owner so.

### DEC-409 — Lifting a freeze requires the owner in person: no Claude Code ancestor, an interactive terminal with a typed one-time code, and a guard rule on the lift form
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Amends:** DEC-365, DEC-407 (its ancestry rule is replaced), DEC-367 as the owner named it · **Under:** DEC-402, DEC-404, CAP-05.a
- **Decision:**
  1. `gov pause --off` refuses if any ancestor process is a Claude Code session, wherever that session was
     started. The operator console cannot lift either; only a plain terminal can.
  2. It requires an interactive terminal: stdin and stdout are TTYs, and it shows a one-time random code ("type
     LIFT-<4 digits> to lift the freeze") that must be typed back. A wrong code, piped input, or no TTY refuses,
     and nothing changes.
  3. The guard refuses any agent Bash command whose text contains the lift form of `gov pause` (the `--off`
     option), for every role, including a command that starts another Claude Code session with that text in its
     prompt. Obfuscated forms are a residual.
  4. The containment check, as DEC-407 decided: a removed or emptied freeze flag is a finding, and the flag is
     restored with its marker line.
  - Setting a freeze stays as decided: the owner (terminal or operator console) and the orchestrator may set it.
  - Wherever else the code treats an unset `GOV_ROLE` as the owner, rule 1 applies to owner-only actions.
  - All of this is built on the freeze branch before W1-50 closes, with acceptance tests for the refused cases (an
    agent session, the operator console, piped input, a wrong code) and one manual check by the owner from a plain
    terminal.
  - The KPI lines are added to W1-50 in their own commit.

| Version | Date | Change |
|---|---|---|
| 0.97 | 2026-10-05 | Owner: DEC-409 (lifting a freeze requires the owner in person: no Claude Code ancestor process, an interactive terminal with a typed one-time code, a guard rule on the lift form; the flag comparison of DEC-407 stays; replaces DEC-407's ancestry rule, amends DEC-365). |

## 98. Delegated decisions on W1-50's packages DP-21 to DP-28 (register v0.98, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220 and its stricter-only rule, on the eight packages the W1-50
(`DAEO-xnbx`) ticket lead returned after its sixth round. In that round the owner's two conditions of DEC-401 passed
on the symmetric rule (criss-cross histories fail closed; a replay of 176 real merges flags none by mistake; a fuzz
of 1,604 merges against an independent reading of DEC-403 gave no mismatch). Every choice below either keeps what is
built or makes the check report more; none makes it report less. The findings of this check are records (DEC-254).
The owner was told on 2026-10-05.

### DEC-410 — W1-50 DP-21 to DP-28: a merge commit's own change to a ticket file or an acceptance test is a finding whatever its trailers; a path both sides changed is the merge commit's own; 24 parents at most
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-21 (b), DP-22 (the complement), DP-23 (a), DP-24 (b), DP-25 (a), DP-26 (a), DP-27 (b), DP-28 (a); the fifth reviewer's findings F1 to F9 · **Amends:** DEC-403 (the octopus sentence; what `brought` holds) · **Under:** CAP-58, DEC-269, DEC-255, DEC-359, DEC-401
- **Decision:**
  - DP-21: a change to a file under `.tickets/**` that a merge commit itself makes (its own change, by the helper)
    is a finding whatever the merge commit's trailers, also with orchestrator trailers or none.
  - DP-27: the same for `tests/acceptance/**`: a merge commit's own change there is a finding whatever its
    trailers, test-designer trailers included.
  - DP-24: under `tests/acceptance/**`, a path that more than one parent changed against the merge base is the
    merge commit's own, whichever side's content it holds. Taking one side whole is a resolution, and a resolution
    of an acceptance test is a finding (DEC-269).
  - DP-26: git's own clean combination of two sides' edits of one acceptance test stays flagged, as built. Branches
    are brought to a state where no acceptance test is changed on both sides before they are merged.
  - DP-25: an octopus whose other parents cross only each other is read as built in round six: that pair brings
    nothing against each other. DEC-403's words "read parent by parent" are amended to this stricter reading.
  - DP-23: with several merge bases or none, every path that differs from any parent is the merge commit's own,
    also where it keeps what its first parent holds. DEC-403's words stand.
  - DP-22: `brought` is the complement of `own` over every parent: each path where the merge commit differs from
    some parent and that is not its own.
  - DP-28: the helper refuses a merge commit with more than 24 distinct parents; the move is then a finding as a
    whole.
  - The owner's conditions of DEC-401 are run again on the final head before the branch is merged.

| Version | Date | Change |
|---|---|---|
| 0.98 | 2026-10-05 | Delegated under DEC-220 (stricter-only): DEC-410 (W1-50 DP-21 to DP-28: a merge commit's own change to a ticket file or an acceptance test is a finding whatever its trailers; a test both sides changed is the merge commit's own; 24 parents at most; `brought` is the complement of `own`). |

## 99. Owner answers and decisions of 2026-10-06 (register v0.99, appended by the W1 orchestrator on branch `w1/integrate`)

Given by the owner on 2026-10-06, after the W1-50 freeze branch's second round, W1-50's sixth round and W1-19's
fourth round.

### DEC-411 — DEC-409 amends DEC-365, not DEC-367
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** owner answer · **Under:** DEC-409
- **Decision:** DEC-409 amends DEC-365 (the W1-28 DP-3 answer). DEC-367 stays unchanged.

### DEC-412 — W1-50 DP-F6: the freeze branch is rebuilt; rewriting an unpushed ticket branch is allowed
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** W1-50 freeze branch package DP-F6 option (a) · **Under:** DEC-410, DEC-235
- **Decision:**
  - The freeze branch is rebuilt: a test designer aligns `tests/acceptance/W1-07/w1_07_support.py` first, then
    `w1/integrate` is merged and the four commits are cherry-picked.
  - Rewriting an unpushed ticket branch is allowed. "Never rebase" protects shared history: `main` and
    `w1/integrate`.
  - The old branch is kept until the new one verifies, then deleted.
  - It is done once, after W1-50's main branch merges, in the round that builds DEC-409.
  - The freeze branch's choices no decision pinned are fine as built: the error codes `PAUSE_RUNTIME_LINKED`,
    `PAUSE_NOT_SET` and `PAUSE_NOT_LIFTED`, and the flag's mode 0600.

### DEC-413 — Review rounds: at most two per FULL ticket; what is fixed after that; W1-50 keeps its seventh round
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Under:** DEC-136, DEC-220
- **Decision:**
  - A FULL ticket has at most two review rounds.
  - After the second, only two kinds of finding are fixed: fail-open holes, and silent changes to tests or ticket
    files in shapes that ordinary work produces. Everything else becomes a residual.
  - A fail-open that remains after the second round comes to the owner as a decision package, not as a third
    round.
  - W1-50 keeps its seventh round, whose stop rule (the same two kinds) is confirmed. If that round still finds a
    fail-open, no eighth round starts: it comes to the owner as a decision package, with the option of accepting
    it as a residual.

### DEC-414 — W1-19 DP-12, DP-11 and DP-13: the pass line is 80 on the dev tiers; the parent-bounded chunks stay; no ranked lexical route in W1-19; the retrieval instruction stays
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** W1-19 packages DP-12 option (b), DP-11, DP-13 option (a) · **Amends:** W1-19's second KPI line · **Under:** DEC-343, DEC-406, DEC-388
- **Decision:**
  - DP-12: the parent-bounded chunks stay (DEC-343). The KPI line is restated: mean hit@5 at or above 80 on the
    dev tiers is the pass line; 85 (the S0b2 baseline) is re-measured at the Wave 1 exit run (W1-42) and at
    qualification.
  - The miss of query `DQ-B-03` and R1's whole-file chunking are recorded as residuals.
  - A test designer revises the baseline case; then W1-19 is merged and closed.
  - DP-11: not in W1-19. "A ranked lexical route for exact identifiers" is a backlog item for W1-17's area, for a
    later wave.
  - DP-13: the embedding model's retrieval instruction on the question stays.

### DEC-415 — Early test design
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Amends:** the READY rule for test design only · **Under:** DEC-235, DEC-069
- **Decision:**
  - When every dependency of a ticket is built and green on its branch (merged or not, closed or not), the
    orchestrator may claim that ticket, create its worktree and run its test design.
  - Its engineer starts only after its dependencies are merged into `w1/integrate`.
  - If a dependency changes its interface before merging, the test designer revises the tests, recorded as "owner
    decision: early test design".

### DEC-416 — Delegation widened for the rest of Wave 1
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Amends:** DEC-220 · **Under:** DEC-220
- **Decision:**
  - The orchestrator may also decide P2 packages with medium-low confidence, when they are reversible and do not
    touch the guard, containment, the launcher, scope, installs, the held-out path, merges into `main` or
    releases.
  - They are listed in the digest as before.

| Version | Date | Change |
|---|---|---|
| 0.99 | 2026-10-06 | Owner: DEC-411 (DEC-409 amends DEC-365, not DEC-367), DEC-412 (W1-50 DP-F6: the freeze branch is rebuilt; an unpushed ticket branch may be rewritten; unpinned choices fine as built), DEC-413 (at most two review rounds per FULL ticket; W1-50's round 7 stop rule), DEC-414 (W1-19: pass line 80 on the dev tiers, 85 re-measured at W1-42 and qualification; chunks stay; no ranked lexical route in W1-19; the instruction stays), DEC-415 (early test design), DEC-416 (delegation widened to P2 at medium-low confidence, with exclusions). |

## 100. Delegated decisions on W1-50's packages DP-29 and DP-30 and on W1-11's package DP-8 (register v0.100, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06 under DEC-220. W1-50's seventh round returned DONE with both of the
owner's conditions of DEC-401 passing on the final rules (criss-cross histories fail closed over 37 shapes; a replay
of 189 real merges flags two, neither by mistake: W1-20's merge-back `5922e24e` and the old freeze branch's merge
`135ed94e`, both records). The branch was merged as `6a978dbc`; the full regression there is green (W1-50 342
passed, `tests/unit` 760 passed, every other suite passed). The owner was told on 2026-10-06.

### DEC-417 — W1-50 DP-29, DP-30 and the bound on a move: as built
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-06) · **Basis:** W1-50 packages DP-29 and DP-30, the stricter option of each, as the lead built them; the sixth reviewer's finding F3 · **Under:** DEC-410, DEC-413, DEC-401
- **Decision:**
  - DP-29: under `tests/acceptance/**`, a path two parents both changed against their one merge base in the same
    way is the merge commit's own change too, although it differs from no parent.
  - DP-30: in a worker's call, the whole-move finding also names the merge commits' own ticket files and
    acceptance tests.
  - A move whose merge commits would need more than 3000 git processes to read is a finding as a whole
    (`MAX_MOVE_PROCESSES`). The commit that built it was not reviewed (DEC-413: no further round).
  - Not built, a residual with the reviewer's recommendation, brought to the owner: a ticket file both sides
    changed, where the merge takes one side whole, raises no finding in an orchestrator's own call.

### DEC-418 — W1-11 DP-8: the checker reads the merge base itself where the helper found exactly one
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-06) · **Basis:** W1-11 package DP-8 option (a), confidence medium; P2, reversible; the designer's, the lead's and the orchestrator's recommendations agree · **Under:** DEC-398, DEC-410, DEC-415
- **Decision:**
  - The checker reads merges through `gov.guard.containment_merge.read_merge`. Only for a parent pair where the
    helper listed the decision's path as brought (so exactly one merge base exists for that pair), the checker
    itself asks git for that merge base and reads the decision there by its `id`, to learn whether the other parent
    changed the decision's id, status or presence since the base.
  - Where the helper fails closed (several merge bases, none, or an error), the checker asks for no base and
    fails closed too. Crossed or unrelated histories are therefore findings for decision files unless the merge
    carries the owner's fact.
  - The checker's own ancestry rule for merges goes; no second merge reader is written, and the helper is not
    changed.

| Version | Date | Change |
|---|---|---|
| 0.100 | 2026-10-06 | Delegated under DEC-220: DEC-417 (W1-50 DP-29, DP-30 and the bound of 3000 git processes per move, as built), DEC-418 (W1-11 DP-8: the checker reads the merge base itself where the helper found exactly one; fails closed where the helper does). |

## 101. Delegated decisions on W1-21's packages DP-0, DP-1, DP-3, DP-6, DP-8 and DP-9 (register v0.101, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06 under DEC-220 and DEC-416, on six of the ten packages the W1-21
(`DAEO-5x4l`) ticket lead returned after the test design (119 cases, all red, no engineer started). Each is
reversible at low cost before W1-22 starts, and the designer's, the lead's and the orchestrator's recommendations
agree. DP-2 (what a batch, a round and a continuation are, with the numbers), DP-4 (what marks a record superseded
or must-not-cite), DP-5 (when a failure or lesson record matches a ticket's scope) and DP-7 (the retrieval-regression
check's baselines) are the owner's. The owner was told on 2026-10-06, including that the lead ranked DP-0 and DP-1 as
P1.

### DEC-419 — W1-21: the command's path, the public interface, the bundle budget, the order of stopping reasons, facets as routes, one rerank over the merged set
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220 and DEC-416, 2026-10-06) · **Basis:** W1-21 packages DP-0 option (a), confidence high; DP-1 (a), medium-high; DP-3 (a), medium; DP-6 (a), medium; DP-8 (a), medium; DP-9 (a), high on one pass · **Under:** DEC-317, DEC-080, DEC-091, DEC-374, DEC-396, CAP-16, CAP-18, CAP-55
- **Decision:**
  - DP-0: `src/gov/retrieve/**` is added to W1-21's `allowed_paths`, in its own commit. It follows DEC-317: a `gov`
    command is built by `src/gov/<name>/command.py`. The module is thin and calls `gov.retrieval.retrieve`.
  - DP-1: the public interface is the one the test design fixes:
    `gov.retrieval.retrieve.retrieve(root, query, *, ids=(), ticket=None, radius=0, batch_size=None,
    bundle_budget=None, continuation=None, reranker=None)`, read-only, returning the bundle as a plain map with
    the keys `stopping_reason`, `evidence`, `batches`, `merge`, `expansions`, `gaps`, `facets`, `budget` and
    `continuation`; and `gov retrieve` with `--json`, `--root`, `--ticket`, `--id`, `--radius`, `--batch-size`,
    `--bundle-budget`, `--continue` and the query. Exit 0 for any bundle, 1 for a bad token, 2 for a usage error.
    A bundle with a continuation token never says `CLOSURE_COMPLETE` or `SATURATED`.
  - DP-3: the bundle budget is counted in tokens of four characters and bounds parent expansion only; a child hit
    is never dropped for it. Its default is DEC-004's packet ceiling until a decision gives another number.
  - DP-6: when several stopping reasons apply the bundle carries the first of `FACET_UNAVAILABLE`,
    `BUDGET_EXHAUSTED_WITH_GAPS`, `DEPTH_LIMIT_REACHED`, `UNRESOLVED_IDS`, then `SATURATED` or `CLOSURE_COMPLETE`.
    An unavailable semantic route still returns the lexical evidence. A reranker that dies leaves `reranked:
    false` and raises nothing.
  - DP-8: "facets" in the first KPI line are the routes (lexical, semantic, closure), reported with their state.
    Content facets stay with W1-36.
  - DP-9: retrieval calls the reranker once, over all candidates gathered for the bundle, after deduplication and
    the authority filter. The latency of a set above 30 is measured and reported.

| Version | Date | Change |
|---|---|---|
| 0.101 | 2026-10-06 | Delegated under DEC-220 and DEC-416: DEC-419 (W1-21 DP-0: the command's path; DP-1: the public interface; DP-3: the bundle budget bounds expansion only; DP-6: the order of stopping reasons; DP-8: facets are the routes; DP-9: one rerank over the merged set). DP-2, DP-4, DP-5 and DP-7 go to the owner. |

## 102. Owner answers and a standing rule of 2026-10-06, second round (register v0.102, appended by the W1 orchestrator on branch `w1/integrate`)

Given by the owner on 2026-10-06. During the night every ticket lead stopped with "403 Access to this model requires
an access grant your request does not have"; the cause was an expired Claude login, not a model. The owner signed in
again; no model or settings change was made. A one-line headless probe answered before any lead was restarted.

### DEC-420 — An authentication or access error stops the launching of leads: `AUTH_REQUIRED`
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Amends:** DEC-250 (one more stop) · **Under:** DEC-235, DEC-250
- **Decision:**
  - If a session or a lead fails with an authentication or access error (401, 403, "Failed to authenticate",
    "access grant"), the orchestrator does not retry in a loop.
  - It stops launching leads, writes its checkpoint, and stops with `AUTH_REQUIRED`, so that the owner knows to
    sign in again.
  - After the owner restores access: a one-line headless probe first; if it works, one lead as a test, then the
    others, each from its branch's last commit.

### DEC-421 — W1-50: the both-sides rule is extended to ticket files
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, on the residual of W1-50's seventh round (the sixth reviewer's finding F1) · **Amends:** DEC-410 (DP-24), DEC-417 (its residual) · **Under:** DEC-413
- **Decision:**
  - Under `.tickets/**` too, a path that more than one parent changed against the merge base is the merge commit's
    own, whichever side's content it holds. Stricter-only.
  - It is built on the freeze branch's round, with its cases.

### DEC-422 — W1-21 DP-2: a round is one more batch; the round limits; the default batch size
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** W1-21 package DP-2 option (a) · **Under:** DEC-035, DEC-080, CAP-04.c, CAP-16.c
- **Decision:**
  - A round is one more batch of candidates.
  - The round limits are 1, 1, 3, 8 and 8 for radius 0 to 4.
  - Reaching the limit gives `BUDGET_EXHAUSTED_WITH_GAPS`, with the ungathered candidates as gaps and a stateless
    continuation token.
  - The default batch size is 10.

### DEC-423 — W1-21 DP-4: superseded from the store; must-not-cite is a closed status list; a file the store could not load is read by its frontmatter
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** W1-21 package DP-4 option (a) · **Under:** DEC-329, CAP-51.b
- **Decision:**
  - Superseded comes from the store: status `SUPERSEDED`, or being the target of a supersedes edge.
  - Must-not-cite is a closed status list: `DEPRECATED`, `REJECTED` and `WITHDRAWN`.
  - A cited file the store could not load is read by its frontmatter.
  - Dropped records are listed in the bundle.

### DEC-424 — W1-21 DP-5: a failure or lesson record is in scope through a typed edge within the closure
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** W1-21 package DP-5 option (a) · **Under:** CAP-14.a, CAP-41
- **Decision:** records of the types `failure` and `lesson` are in scope when a typed edge (for example
  `constrains: [<ticket id>]`) joins the record and the ticket within the closure. No schema work.

### DEC-425 — W1-21 DP-7: the retrieval-regression check's baselines and severity
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** W1-21 package DP-7 option (a) · **Under:** DEC-414, CAP-38.b
- **Decision:**
  - The check needs a mean hit@5 of at least 80 (DEC-414) and at most 2 forbidden citations.
  - The query set is found through `GOV_DEV_TIERS`.
  - Severity: hard-block where the query set is configured. Where it is not (an adopter without dev tiers), the
    check reports "unmeasured" as a warning and is never shown as green.

### DEC-426 — `S0a-G-06`: where a worker may look for its text
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Under:** DEC-383
- **Decision:** a product-spec worker may look for the text of `S0a-G-06` in the archived `docs/source/` through
  `docs/SOURCES.md` (rule C), or ask the owner for an exact workbench path. Never `qualification-oracle/` or
  `s0b2/probe/`.

| Version | Date | Change |
|---|---|---|
| 0.102 | 2026-10-06 | Owner: DEC-420 (an authentication or access error stops the launching of leads, `AUTH_REQUIRED`), DEC-421 (W1-50: the both-sides rule extended to ticket files), DEC-422 to DEC-425 (W1-21 DP-2, DP-4, DP-5, DP-7), DEC-426 (`S0a-G-06`: where its text may be looked for). |

## 103. A delegated decision on W1-24's first round and its package DP-1 (register v0.103, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06 under DEC-220, DEC-412 and DEC-416. The W1-24 (`DAEO-wk2v`) ticket lead
returned DONE after one hour. Its test designer was a launched worker (`1f6b9e30`, 34 cases). Its engineer was an
in-session subagent started with the Agent tool, not a launched worker (DEC-371); the lead then wrote the review
fixes into `src/gov/context/` itself and committed them without a role; it decided the designer's two packages
itself; and its verification stopped at the first failure. The owner was told on 2026-10-06.

### DEC-427 — W1-24: the first round is not accepted and the branch is rebuilt from the test design; the public interface
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220 and DEC-416, 2026-10-06) · **Basis:** DEC-371 (workers are started by the launcher), MR-3, DEC-412 (an unpushed ticket branch may be rewritten); W1-24 package DP-1 option (a), confidence medium-high · **Under:** DEC-317, CAP-15
- **Decision:**
  - The first round's implementation (`f03c0283`, `5375ba84`) is not accepted. `w1/W1-24` is set back to the test
    designer's commit `1f6b9e30`; the discarded commits are kept on `w1/W1-24-run1` until the ticket closes, and
    no worker is given them. A second test designer deepens the design, a launched engineer builds, every suite
    is run to its end, and a read-only reviewer follows (DEC-413).
  - DP-1: the public interface is the one the test design fixes: `gov.context.context(root, ticket, *, brief,
    budget)`, returning the packet as a plain map with the keys `authority`, `mandatory`, `supplementary`,
    `dropped`, `hash`, `tokens` and `budget`; a mandatory input has `id`, `sha256`, `authority`, `lifecycle`,
    `constraint` and `reason`.
  - DP-2 (the exit code of a `BLOCKED` state) stays open until the second designer names the source that fixes
    the envelope's exit codes.
  - Every lead brief now opens with four rules: writing workers are started by `gov launch` only; a lead writes
    no file under `src/`, `template/`, `tests/` or `docs/`; a lead decides no package; a lead never ends its
    turn while its worker or its test run is running, and never verifies with a stop at the first failure.

| Version | Date | Change |
|---|---|---|
| 0.103 | 2026-10-06 | Delegated under DEC-220, DEC-412 and DEC-416: DEC-427 (W1-24's first round is not accepted, since its engineer was not a launched worker and the lead wrote source; the branch is rebuilt from the test design; DP-1: the public interface). |

## 104. Owner answers of 2026-10-06, third round: the mid-wave audit's findings, the freeze mirror, the lead's role (register v0.104, appended by the W1 orchestrator on branch `w1/integrate`)

The owner's answers to the mid-wave audit (DEC-249; findings MWA-01, MWA-02, MWA-05), to W1-50's remaining
fail-open, to the open sources `S0a-G-06` and `S0a-G-07`, to W1-44's residuals, and to the report that W1-24's lead
wrote source (DEC-427). Ticket edits are in their own commits.

### DEC-428 — The owner's manual check of freeze, pause and lift moves to the Wave 1 exit
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Amends:** DEC-409 (the one manual check before W1-50 closes)
- **Decision:**
  - The owner's manual check moves to the Wave 1 exit run. W1-42 gets the KPI line: "The owner freezes, pauses and
    lifts from a plain terminal, on a throwaway repository and on this one, and the results are recorded."
  - W1-50 no longer waits for it: W1-50 closes when DEC-429 is built, green and reviewed.

### DEC-429 — W1-50: the freeze is also written to a mirror outside the repository (MWA-01)
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, on the last freeze review's findings F2, F3 and F8 and the mid-wave audit's MWA-01; options (a) and (b) combined · **Extends:** DEC-404, DEC-407, DEC-409 · **Under:** DEC-413, DEC-415, CAP-05
- **Decision:**
  - `gov pause` writes the freeze to `.gov-runtime/freeze` and to a mirror outside the repository, under
    `~/.local/state/gov-os/`, keyed by the repository.
  - The guard treats the project as frozen if either exists (fail closed).
  - If the flag in the repository is removed or emptied while the mirror remains, that is a finding, and the flag
    is restored with its marker line.
  - Lifting in person (DEC-409) removes both.
  - Sandboxed workers cannot reach the mirror. An opaque write by the orchestrator's own unsandboxed session stays
    a recorded residual.
  - It is built as a follow-up on W1-50, in one build round and one review; then W1-50 closes.

### DEC-430 — The owner's reading of MR-3 (MWA-02)
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, option (a) on the mid-wave audit's MWA-02 · **Under:** MR-3, DEC-069, DEC-136
- **Decision:**
  - The core tests for every KPI line are written by the independent test designer before implementation. Cases
    found in review may be added afterwards, by the test designer only, red before their fix (DEC-136).
  - This is how MR-3 is met, not an exception to it.
  - The exit auditor is told so in W1-43's brief.

### DEC-431 — CAP-08.a's `owner` and `links` filters go to the backlog (MWA-05)
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, option (a) on the mid-wave audit's MWA-05 · **Under:** CAP-08
- **Decision:** the `owner` and `links` filters of CAP-08.a are not built in Wave 1. They go to the backlog for a
  later wave, recorded as a known partial of W1-10.

### DEC-432 — `S0a-G-06` and `S0a-G-07` are residuals; two files may be read by exact path
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Extends:** DEC-426 · **Under:** DEC-383
- **Decision:**
  - `S0a-G-06` (W1-21) and `S0a-G-07` (W1-24) are residuals for now; neither ticket waits on them. The S0a output
    names gaps by bare id (`G-06`, `G-07`); the `S0a-` prefix was added in the Contract.
  - The orchestrator may read two files by exact path: `/home/usain/gov-os-workbench/s0a/out/STACK_OPTIONS.md`
    (G-06 and G-07) and `/home/usain/gov-os-workbench/s0a/out/BAKEOFF_PLAN.md` (G-06 only). Nobody lists folders
    there, and nobody touches `qualification-oracle/` or `s0b2/probe/`.
  - If they confirm the gap texts, the orchestrator passes any needed lines to a worker in its brief; if they do
    not, the residual stands.
- **Read on 2026-10-06:** both texts are in `STACK_OPTIONS.md`. G-06: "`gov retrieve`: facets, batches, follow-up
  rounds, dedup, stopping reasons, NOT_FOUND ≠ absent" (CAP-16, CAP-17, CAP-55). G-07: "`gov context`: authority
  block first, supplementary block, token ceiling, sha256, file-path delivery + ≤ 2.5k-token summary" (CAP-01,
  CAP-15). Neither contradicts a case of W1-21. `BAKEOFF_PLAN.md` adds no requirement.

### DEC-433 — W1-44: the lessons' severities and lifecycles stand; the anti-snowball lesson's link to W1-30
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Under:** DEC-168, DEC-424
- **Decision:** the lesson records' severities and lifecycles stand as written. Linking the anti-snowball lesson
  to W1-30 is delegated to the orchestrator.

### DEC-434 — Ticket leads get their own role
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, on DEC-427 · **Amends:** DEC-156 (as far as a ticket lead is concerned) · **Under:** DEC-371, MR-3
- **Decision:**
  - Leads run as `GOV_ROLE=orchestrator`, which has wide write rights (DEC-156); that is why the guard did not
    stop W1-24's lead from writing source.
  - Delegated to the orchestrator, stricter-only: ticket leads get their own role, allowed to write only their
    checkpoint, their scratch and merge-backs (judged by the three-way rule), so that a lead cannot write source
    or tests. The orchestrator chooses the ticket.

| Version | Date | Change |
|---|---|---|
| 0.104 | 2026-10-06 | Owner: DEC-428 (the manual freeze check moves to W1-42), DEC-429 (W1-50: the freeze mirror outside the repository), DEC-430 (the reading of MR-3), DEC-431 (CAP-08.a's `owner` and `links` filters to the backlog), DEC-432 (`S0a-G-06`, `S0a-G-07`: residuals, two files by exact path), DEC-433 (W1-44's lessons stand), DEC-434 (ticket leads get their own role). |

## 105. Delegated decisions under DEC-433, DEC-434 and DEC-416 (register v0.105, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06.

### DEC-435 — The lead's role is built on W1-50; L-0077 constrains W1-30; W1-22's interface packages
- **Status:** ACCEPTED (orchestrator, delegated under DEC-434, DEC-433 and DEC-416, 2026-10-06) · **Basis:** W1-50 already holds the paths (`src/gov/guard/decide*`, `src/gov/guard/containment*`, `src/gov/launch/**`) and the three-way merge reading; W1-22 packages DP-1 to DP-4, the designer's confidence high or medium-high · **Under:** DEC-429, DEC-410, DEC-317
- **Decision:**
  - The ticket lead's role (DEC-434) is built on W1-50, in the same follow-up round as the freeze mirror
    (DEC-429): one build round and one review cover both. W1-50 gets the KPI lines in its own commit. The lead
    start command in the orchestrator prompt is the owner's to change once the role is built.
  - The anti-snowball lesson `L-0077` also constrains W1-30 (`DAEO-2lwj`), the ticket that builds `gov close`.
  - W1-22 DP-1 to DP-4, as its design encodes them: `gov.retrieval.validate.validate(root, bundle)` returning
    `valid` and `errors`; `gov.retrieval.canary.run_canaries(root)` returning, per index, `passed`, `status` and
    `misses`; canary declarations as YAML under `template/governance/kernel/canaries/`, one per index; the
    validator checks a citation's `sha256` against the cited span only. Which indexes "each index" covers is open
    with the ticket's closing round.

| Version | Date | Change |
|---|---|---|
| 0.105 | 2026-10-06 | Delegated: DEC-435 (the lead's role is built on W1-50 with the freeze mirror; `L-0077` also constrains W1-30; W1-22 DP-1 to DP-4, the validator's and the canary runner's interface). |

## 106. Delegated decisions on W1-26's second round (register v0.106, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06.

### DEC-436 — W1-26: the second round's merge is not accepted and the branch is rebuilt; a declaration of an unknown family is never green
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416 and DEC-412, 2026-10-06) · **Basis:** the return of W1-26's second round and the orchestrator's check of the branch against `w1/integrate` · **Under:** DEC-413, DEC-425, DEC-427, DEC-254
- **Decision:**
  - The branch's merge of `w1/integrate` (`2cb1924e`) was made without committing in the same command, and the
    containment check restored the incoming acceptance tests before the commit: the merged tree lacks W1-21's
    tests and holds older versions of other tickets' tests. That merge is not a record under DEC-254 and is not
    merged. The branch is rebuilt from `w1/integrate` (DEC-412); the old branch is kept as `w1/W1-26-run2` until
    the ticket closes.
  - On the new base a launched test designer restores this ticket's tests and its lines in the W1-07 files in one
    commit with its role trailer, and a launched engineer restores the source in one commit with its role trailer.
    The untrailered commits `93c96e49` and `5b1109ec` do not return to the history.
  - A lead merges `w1/integrate` into its branch in one command that commits. After it, the acceptance tests of
    the branch differ from those of `w1/integrate` only in the ticket's own files; a difference in another
    ticket's tests is a defect of the merge, never a record.
  - A check declaration's family is compared with the seventeen families by a normalised name (lower case, every
    run of characters that are not letters or digits read as one hyphen), so `retrieval-regression` is the
    Contract's "retrieval regression". A declaration whose family matches none is reported by name and makes the
    result not green; it is never dropped from the result (DEC-425).
  - Both review rounds are spent (DEC-413). The third round fixes only this fail-open case, the failure line
    "the scope of a check is a hand-maintained list", and the readiness check that ignores its result; no
    reviewer runs.

| Version | Date | Change |
|---|---|---|
| 0.106 | 2026-10-06 | Delegated: DEC-436 (W1-26's second-round merge not accepted, the branch rebuilt; a lead's merge commits in one command; a check declaration of an unknown family is never green; family names compared normalised). |

## 107. Delegated decisions on the W1-50 follow-up's packages and on W1-24's packages (register v0.107, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06. The owner was told the same day that DP-M2 to DP-M4 touch the guard and may be overturned.

### DEC-437 — W1-50 follow-up DP-M1 to DP-M4, DP-L1, DP-L2; W1-24 DP-2 to DP-5
- **Status:** ACCEPTED (orchestrator, delegated under DEC-434 and DEC-416, and as the strictest reading of DEC-429, 2026-10-06) · **Basis:** the test designers' packages, each with a recommendation · **Under:** DEC-429, DEC-409, DEC-402, DEC-425
- **Decision:**
  - DP-M1: the mirror entry is named by the SHA-256, in hex, of the real path of the repository's git common
    directory. The main tree and every worktree share one entry; two clones differ; a moved repository has a new
    key, which is a residual.
  - DP-M2: an empty or unmarked file at the mirror's path means frozen (DEC-429: "frozen if either exists").
    `gov pause` writes the marker line into the mirror.
  - DP-M3: a lift that cannot remove the mirror refuses and nothing changes; the project stays frozen and the
    message names the mirror's path. The owner's answer did not cover this case.
  - DP-M4: the mirror is at `~/.local/state/gov-os/` under the home directory the process sees;
    `XDG_STATE_HOME` is not followed. A session that changes a child's home directory makes that child read
    another mirror: a residual to be named with the sessions that can do it.
  - DP-L1: the lead's role is named `ticket-lead`.
  - DP-L2: the role has no allowed paths; it writes its scratch through the existing scratch rule.
  - W1-24 DP-2: `gov context` exits 1 for BLOCKED and CONTRADICTION. DP-3: the supplementary query as built.
    DP-4: an entry dropped because an index is unavailable carries that reason. DP-5: `--dry-run` computes
    without writing the brief file.
  - W1-24's family check that ends green after measuring nothing is a fail-open under DEC-413 and DEC-425 and is
    fixed, test first, before the ticket's merge.

| Version | Date | Change |
|---|---|---|
| 0.107 | 2026-10-06 | Delegated: DEC-437 (the freeze mirror's key, content, lift failure and place; the lead's role name and paths; W1-24 DP-2 to DP-5; W1-24's check that measured nothing is not green). |

## 108. A delegated decision on W1-26's third round (register v0.108, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06.

### DEC-438 — W1-26: a family with no registered check is never green
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-06) · **Basis:** `gov check --json` run by the orchestrator on W1-26's branch at `be229cdd`: four of the seventeen families had no registered check and were reported green · **Under:** DEC-425, DEC-413, DEC-436
- **Decision:**
  - A family with no registered check has the status YELLOW, with the reason "no registered check" and a count
    of 0 in its entry. It is never green, and it is not a hard-block by itself.
  - Every family's entry carries the count of its registered checks, so the wave's exit run (W1-42) can count
    the families that have at least one executable check.
  - This is a fail-open under DEC-413 and is fixed test first in a short fourth start of the ticket; no review
    round follows.

| Version | Date | Change |
|---|---|---|
| 0.108 | 2026-10-06 | Delegated: DEC-438 (W1-26: a family with no registered check is YELLOW with its reason and a count, never green). |

## 109. A delegated decision: W1-26 is reopened for the generic validators it did not build (register v0.109, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06.

### DEC-439 — W1-26 reopened: the generic validators for skill files and audit reports
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-06) · **Basis:** W1-35's return: its check `skill-regression-a` had no validator to call and was declared with a command that always succeeds; W1-26's KPI line "provides the generic validators for skill files and audit reports" was met by no code and by no case, and the ticket was closed by the orchestrator without noticing · **Under:** DEC-413, DEC-425, DEC-438
- **Decision:**
  - W1-26 (`DAEO-fygv`) is reopened for one follow-up round in its own paths: a validator for skill files
    (frontmatter, version, description and body size, every referenced `gov` command exists) and a validator
    for audit reports (the cited commit, the rows and the evidence paths resolve), each callable as a check
    command with the files or folders to validate as arguments, test first.
  - A validator that is given nothing to validate, or that cannot read what it is given, is unmeasured and
    never green (DEC-425).
  - W1-35 and W1-36 declare their checks with these validators. A check declared with a command that always
    succeeds is not merged.
  - No new ticket is made and no KPI line changes: the line was already W1-26's.
  - The close of W1-26 on 2026-10-06 was the orchestrator's error: a KPI clause with no case. From now on the
    orchestrator reads every clause of every KPI line against the designer's case table before a close.

| Version | Date | Change |
|---|---|---|
| 0.109 | 2026-10-06 | Delegated: DEC-439 (W1-26 reopened for the generic validators for skill files and audit reports; a check declared with a command that always succeeds is not merged). |


## 110. Two delegated decisions: what rebuild and doctor must do, and the form of an audit report (register v0.110, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-06.

### DEC-440 — W1-27: rebuild recreates each derived store through its owner; a doctor measurement that fails is a failure
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-06) · **Basis:** W1-27's second return: `gov rebuild` recreated only the record graph, created empty lexical tables from a copy of W1-17's table definitions and named the semantic and the code index as skipped with constant sentences; `gov doctor` was healthy whenever no section said "fail" or "drift", and a measurement that raised an error said "unmeasured" · **Under:** DEC-413, DEC-425, DEC-438
- **Decision:**
  - `gov rebuild` recreates the lexical index by the code that owns it and holds no copy of another module's
    table definitions. It recreates the semantic index and the code index by the code that owns them when
    their tool answers, and names each as not recreated, with the measured reason, when it does not. Rebuild
    itself succeeds with nothing but git. Its result names every derived store with what was done to it.
  - In `gov doctor`, a section whose measurement raised an error, or whose input exists and cannot be read, is
    a failure. A section whose component is not installed in the project is unmeasured with its reason; it
    does not by itself make the project unhealthy, and such a project is never reported at the top adoption
    level.

### DEC-441 — The minimal form of an audit report, for the audit-reproducibility check
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-06; the owner may overturn) · **Basis:** the W1-26 follow-up's package: no source fixes the report as a file; DEC-070 fixes the six row classes, DEC-088 the triggers and the milestone, CAP-47 the pack hash and the evidence · **Under:** DEC-070, DEC-088, DEC-439
- **Decision:**
  - An audit report is a Markdown file with YAML frontmatter holding `milestone`, `commit` (the audited
    commit) and `pack_sha256` (the hash of the context pack the auditor received), and a body holding one
    table whose header is `item`, `class`, `evidence`.
  - Each row names one contract item or decision, exactly one of the six classes of DEC-070, and its evidence:
    paths relative to the repository root, separated by commas. A row of class `OK` cites at least one path;
    a row of another class may cite none, written as `-`.
  - The audit-report validator of W1-26 is green only when the commit resolves in the repository, the table
    has at least one row, every row is well-formed, and every cited path exists at the cited commit. Prose
    around the table is free.
  - The audit skill of W1-36 states this form. The form is the minimum the check needs; a later decision may
    add fields.

| Version | Date | Change |
|---|---|---|
| 0.110 | 2026-10-06 | Delegated: DEC-440 (W1-27: rebuild recreates each derived store through its owner; a failed doctor measurement is a failure), DEC-441 (minimal form of an audit report). |


## 111. Owner answers after W1-29's close, and one delegated decision (register v0.111, appended by the W1 orchestrator on branch `w1/integrate`)

Answered by the owner on 2026-10-07 in two messages; DEC-450 decided by the orchestrator.

### DEC-442 — The Stop and SubagentStop hooks are activated at the Wave 1 exit run, not mid-wave
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** W1-29's residuals: the two hooks are built and not registered; SubagentStop would refuse the returns of the leads' verification subagents, which do not carry the twelve contract fields · **Under:** DEC-137, DEC-208
- **Decision:**
  - The two hooks are not registered while Wave 1 tickets are being built.
  - Both are activated at the Wave 1 exit run (W1-42), after every brief asks for the twelve-field return.
    That step is part of W1-42.
  - The orchestrator brings the exact settings lines to the owner at that point.

### DEC-443 — The auto-compact threshold is verified from Claude Code's official documentation
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** W1-49 reported a settings key; W1-29 reports that the threshold is not set · **Under:** DEC-208
- **Decision:**
  - The orchestrator verifies from Claude Code's official documentation which setting, a settings key or an
    environment variable, controls the auto-compact threshold, and whether it is set in this repository.
  - If a documented key exists and is not set, the orchestrator brings the exact line to the operator.
  - Until then the orchestrator's CONTEXT_CHECKPOINT fallback stays.

### DEC-444 — The hooks' automatic checkpoints go to the ignored scratch folder; deliberate checkpoint records are committed
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** W1-29's residuals: the hooks wrote untracked files under `docs/checkpoints/` in every session with a ticket · **Under:** DEC-264
- **Decision:**
  - The checkpoints the hooks write by themselves go to `.gov-runtime/scratch/checkpoints/`, which is ignored.
  - Only deliberate `gov checkpoint` records go to `docs/checkpoints/` and are committed.
  - The orchestrator chooses the ticket for the change. It chose W1-29, reopened for one follow-up round in
    its own paths.

### DEC-445 — "A checkpoint when context utilisation passes the threshold" is accepted as a residual
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** W1-29's KPI line 3; no hook receives the context utilisation
- **Decision:**
  - The clause is accepted as a residual of W1-29. What exists stands in its place: a checkpoint at every
    stop and every compaction, and the watchdog marking a checkpoint stale on utilisation.

### DEC-446 — DEC-441, the minimal form of an audit report, is accepted by the owner
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** DEC-441 was delegated and open to overturn
- **Decision:**
  - The form of DEC-441 stands as decided.

### DEC-447 — The audit-reproducibility check before the first audit is a warning, and a hard block afterwards
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** a hard-block check that measured nothing is red, so a project with no audit report yet would be red at every `gov check` · **Under:** DEC-425, DEC-438, DEC-441
- **Decision:**
  - While a project has no audit report, the audit-reproducibility check reports "not applicable until the
    first audit" as a warning, not red.
  - Once an audit report exists, the check is a hard block.
  - How it is built (the orchestrator's detail under DEC-416): the audit-report validator says "not
    applicable" by name only when the folder it is given holds no report at all, and `gov check` shows that
    answer as yellow with that reason. A report that is unreadable, broken or failing is red as before. No
    other check gains this answer, and the answer is never green.

### DEC-448 — `gov doctor`: registered tool locations, historical records, one rebuild, and the Claude Code drift
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** `gov doctor` on this repository: Node 18 found against 22 pinned, `openspec` and `ccusage` not found, 180 references to moved paths, a stale index, Claude Code drift · **Under:** DEC-202, DEC-210, DEC-440
- **Decision:**
  - Each tool is checked at its registered location (the PATH prefix of DEC-202 and the registry's paths),
    not only on PATH, so Node 22, `openspec` and `ccusage` are found where they are installed. The machine's
    default Node stays 18.
  - Historical records (the register, the CIT records, `bootstrap.md`, archived sources) are excluded from the
    stale-path check. The stale paths in live documents are fixed, and any remainder becomes a small cleanup
    task.
  - `gov rebuild` is run once on this repository when W1-27's fixed rebuild is merged. This one run is the
    owner's exception to the rule that `gov rebuild` is never run against this repository.
  - The Claude Code drift (extension 2.1.289, command line 2.1.288) is harmless, both being above the
    minimum; the record is renewed at the Wave 1 exit.

### DEC-449 — Every KPI clause is read against the tests and the code before a close is accepted
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** the orchestrator's practice since DEC-439 · **Under:** DEC-439
- **Decision:**
  - The orchestrator's practice of reading every KPI clause against the tests and the code before accepting a
    close is confirmed and kept for every ticket.

### DEC-450 — `gov close` calls the checkpoint watchdog before it closes
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-06) · **Basis:** W1-29's failure line "a handoff or ticket close proceeds while the latest checkpoint is stale for its policy"; W1-29's design left the call to `gov close`, and W1-30's first design left it out · **Under:** DEC-413, DEC-425
- **Decision:**
  - `gov close` calls W1-25's watchdog before it closes and refuses on a stale or missing checkpoint with the
    watchdog's own code. The closing checkpoint is written after the checks pass. The cases are W1-30's.

### DEC-451 — The auto-compact threshold is already set by environment variable; the CONTEXT_CHECKPOINT fallback is dropped
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** the check asked for by DEC-443: the official documentation names the settings key `autoCompactWindow` and the equivalent environment variable `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, each a number of tokens from 100000 to 1000000, capped at the model's context window; the owner, through the operator, read the project's settings file · **Under:** DEC-208, DEC-443
- **Decision:**
  - The project's settings file already sets `CLAUDE_CODE_AUTO_COMPACT_WINDOW` to 300000 in its environment
    block, added by W1-49. There is no `autoCompactWindow` key and none is needed. No settings change is made.
  - The orchestrator's session started after W1-49's merge, so the setting is active in it.
  - The orchestrator drops its CONTEXT_CHECKPOINT fallback and relies on auto-compaction with the hooks of
    W1-49 and W1-29, as section 7 of its prompt says.
  - W1-29's residual line that the threshold is not set, and the key name `autocompact` its lead gave, are
    wrong and are corrected by this entry.

| Version | Date | Change |
|---|---|---|
| 0.111 | 2026-10-07 | Owner answers: DEC-442 (Stop and SubagentStop activated at the exit run), DEC-443 (auto-compact threshold verified from the official documentation), DEC-444 (automatic checkpoints to the ignored scratch folder), DEC-445 (utilisation-triggered checkpoint accepted as a residual), DEC-446 (DEC-441 accepted), DEC-447 (audit reproducibility: a warning before the first audit, a hard block after), DEC-448 (`gov doctor`: registered tool locations, historical records, one rebuild, drift), DEC-449 (KPI clauses read against tests and code before every close). DEC-451 (the auto-compact threshold is already set by environment variable; the CONTEXT_CHECKPOINT fallback is dropped). Delegated: DEC-450 (`gov close` calls the checkpoint watchdog). |

## 112. Three delegated decisions: where `gov doctor` looks for a tool, and what `gov close` must measure (register v0.112, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-452 — Doctor looks under every registered PATH prefix before PATH, and a tool it cannot verify fails
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07) · **Basis:** the orchestrator's reading of W1-27's code and of `gov doctor` run on this repository after DEC-448 was built: `openspec` and `ccusage` are found under the prefix their registry entries carry, Node is not (its entry's install command is the `nvm install` line and carries no prefix; the place is only in a free-text note), `socat` passes with no version read and no hash match, and one case asserted a key name · **Under:** DEC-202, DEC-425, DEC-440, DEC-448
- **Decision:**
  - Doctor looks for a tool first under its own registry entry's PATH prefix, then under every PATH prefix that
    any entry of the registry carries, in the registry's order, and only then on PATH. This is the reading of
    DEC-448's "the PATH prefix of DEC-202" for a tool whose own entry carries none; with it Node 22 is found
    where it is installed, and the registry is not changed.
  - A tool passes only when the version read equals the pin, or, where no version can be read, when the file's
    hash equals the pinned hash. A tool for which neither can be established fails, with the reason; so does a
    version command that errors or times out (DEC-440: an error in a measurement is a failure).
  - Both are fixed test-first (DEC-136) inside W1-27, without a further review round (DEC-413).

### DEC-453 — W1-50 is reopened for a public, read-only judgement of commits; `gov close` calls it
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07) · **Basis:** W1-30's second return: its containment check is a private rule set that exempts `tests/`, `docs/`, `governance/`, `template/` and `openspec/`, so an engineer's commit that changes an acceptance test closes clean; the lead's package says W1-50's module has no public function that judges a ticket's commits (the judgement by `Role` and `Task` trailers exists there, but only inside the post-command check) · **Under:** DEC-319, DEC-410, DEC-425, DEC-439
- **Decision:**
  - W1-50 is reopened for a follow-up: `gov.guard.containment` gets a public function that judges a list of
    commits by their trailers exactly as the post-command check judges an orchestrator's own commits, and
    returns the findings. It only reads: it restores nothing and writes no record.
  - `gov close` calls it for the ticket's commits and refuses on any finding. Its private rule set is removed.
    No second rule set is written anywhere.

### DEC-454 — What `gov close` measures where its KPI lines left the mechanism open
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; the owner may overturn any point) · **Basis:** W1-30's second return (six packages for the owner) and the orchestrator's reading of the code against each KPI clause (DEC-449): the disposition of every finding was a constant, a context that could not be built was replaced by a hash of the ticket file, "the regression tests" were two folders of unit tests, the reviewer's "wrote nothing" was the record's own word, a fourth iteration had no owner's decision to wait for, and the stale-evidence rule measured nothing · **Under:** DEC-096, DEC-136, DEC-137, DEC-413, DEC-425
- **Decision:**
  - **The regression tests** of a close are every test under the project's `tests/` outside the ticket's own
    acceptance folder. All run to their end. A failure, a collection error or a time limit reached refuses the
    close. The time limit is a setting with a default.
  - **The disposition** of a finding is given by the caller as an argument, one of the six names. Without it
    the finding is recorded as unclassed, the output says so, and the repair ticket records "unclassed":
    `gov close` never invents a class. With it, the context is built first and its hash is recorded.
  - **A context that cannot be built** refuses the close.
  - **"The reviewer wrote nothing"** is checked against the commits' `Role` trailers, and the probe record
    names the commit it probed; a ticket commit outside tests and probe records after that commit makes the
    probe stale.
  - **Iterations:** every consecutive failed close of a ticket counts. The count resets on a successful close
    or on an owner's decision, given as an argument that names a register entry which W1-11's checker confirms
    as the owner's. Without it a fourth attempt is refused before anything runs. A count file that cannot be
    read refuses.
  - **Stale evidence:** when a ticket's commits change governance files, `gov close` re-runs the checks at HEAD
    through W1-26's runner and refuses on any hard-block red. It trusts no recorded result.
  - All are built test-first in W1-30's third start, without a further review round (DEC-413).

| Version | Date | Change |
|---|---|---|
| 0.112 | 2026-10-07 | Three delegated decisions: DEC-452 (doctor looks under every registered PATH prefix before PATH; a tool it cannot verify fails), DEC-453 (W1-50 reopened for a public read-only judgement of commits, which `gov close` calls), DEC-454 (what `gov close` measures: regression tests, disposition, context, the reviewer's writes, iterations and the owner's decision, stale evidence). Next free id: DEC-455. |

## 113. One delegated decision: where the owner's choice after an escalation is recorded (register v0.113, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-455 — The owner's choice after an escalation is the register entry; `gov close` records its id, and every refusal for a finding counts
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; the owner may overturn it) · **Basis:** W1-30's test designer (round 4): DEC-096 and CAP-59.a name six options for the owner (fix differently, narrow, split, defer, delete, continue) but no field that records which was chosen; and the orchestrator's reading of `gov close` (DEC-449) after its lead's third start ended unfinished: only failing tests were counted as an iteration · **Under:** DEC-096, DEC-454, CAP-59.a
- **Decision:**
  - The owner's choice is recorded where the owner records decisions: in the register entry itself, in its text.
    `gov close` takes that entry's id as an argument, accepts it only when the ticket is escalated and W1-11's
    checker finds the entry active with the owner's approval fact, and records the id with the ticket's count.
    It does not parse the entry for one of the six words.
  - A close refused for a finding about the ticket's work (trailers, containment, the probe record, a failing or
    timed-out test run, the governance checks, the checkpoint watchdog, a context that cannot be built) is one
    iteration and opens a repair ticket. A close refused because the ticket is unknown, the arguments are
    invalid, the ticket is already closed, the escalation is in force or the count file is corrupt is not.
  - W1-30 is finished by designer and engineer turns the orchestrator starts itself; no fourth lead start.

| Version | Date | Change |
|---|---|---|
| 0.113 | 2026-10-07 | One delegated decision: DEC-455 (the owner's choice after an escalation is the register entry and `gov close` records its id; every refusal for a finding about the ticket's work counts as an iteration). |

## 114. Owner answers: stale paths, DEC-455, the exit package and a compliance report (register v0.114, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-456 — Stale paths: the move table and the old `cli/` tree are historical; the plan validator's one stale path is fixed
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the record of the one rebuild (DEC-448): `gov doctor` reported 180 stale paths on this repository, 156 in `docs/SOURCES.md`, 23 in the old `cli/` tree, one in `docs/plan/tools/validate_s1.py` · **Amends:** DEC-448 (the set of historical records) · **Under:** DEC-440
- **Decision:**
  - `docs/SOURCES.md` is a historical table of moves and must keep the old paths: it is left out of doctor's
    stale-path check.
  - The old `cli/` tree is legacy code (the live CLI is `src/gov/cli/`): it is treated as historical and left
    out of the check. W1-41's adoption review decides whether to archive it.
  - The one stale path in the plan validator script, which is live, is corrected.
  - Doctor's remaining red on this repository is then only the Claude Code drift, re-recorded at the Wave 1
    exit.
  - W1-27 is reopened for the two exclusions, test first.

### DEC-457 — DEC-455 is accepted by the owner
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER · **Confirms:** DEC-455
- **Decision:** The owner's choice after an escalation is the register entry and `gov close` records its id;
  every close refused for a finding about the ticket's work counts as an iteration.

### DEC-458 — One package for the owner's actions at the Wave 1 exit
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER · **Under:** DEC-442, DEC-444, DEC-448, DEC-070
- **Decision:** When W1-41 is merged, the orchestrator brings the owner one package listing everything the
  owner does at the exit, with exact commands and steps for each:
  - the manual freeze, pause and lift check (DEC-442);
  - the Stop and SubagentStop hook lines to register (DEC-444);
  - the Claude Code version to re-record;
  - the external audit session the owner starts alongside W1-43 (DEC-070).

### DEC-459 — A rule-by-rule compliance report for Wave 1, compiled by a read-only subagent and verified by the exit auditor
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER
- **Decision:**
  - A read-only subagent compiles a compliance report for Wave 1 so far, without stopping the running work. It
    writes nothing; it returns the report to the orchestrator, who saves it as
    `.gov-runtime/scratch/orchestrator/COMPLIANCE.md`.
  - It covers each master rule MR-1 to MR-6, quoted from Charter v5, and these process rules: tests before
    implementation (the READY rule and the MWA-02 reading); independence between test designer, engineer and
    reviewer, including that no worker saw another's output and none saw a stand-in implementation;
    `allowed_paths` scope; workers started only through `gov launch`, sandboxed; leads write no source or tests
    and decide no packages; the loop policy (hidden counts, escalation) and the two-round review cap; the
    delegation limits (what came to the owner and what the orchestrator decided); decisions recorded before the
    changes they authorise; held-out discipline; never push, merge into main or rewrite shared history; commit
    trailers; the proportion rule.
  - For each rule it gives what enforces it (the guard, containment, a test or check, or only a brief or
    prompt), the evidence (counts, commit ids, findings, decision numbers), every deviation so far (date,
    ticket, what happened, how it was caught, the fix), and the remaining risk, named honestly where the rule
    rests on instructions alone.
  - The orchestrator brings the owner a short summary: which rules are enforced by mechanism, which by
    instruction only, and the deviations in one table. The full report goes into W1-43's brief, so the exit
    auditor verifies it independently instead of taking it as given.

| Version | Date | Change |
|---|---|---|
| 0.114 | 2026-10-07 | Owner answers: DEC-456 (the move table and the old `cli/` tree are historical for doctor's stale-path check; the plan validator's stale path is fixed; W1-27 reopened), DEC-457 (DEC-455 accepted), DEC-458 (one package of the owner's exit actions when W1-41 is merged), DEC-459 (a rule-by-rule compliance report by a read-only subagent, verified by the exit auditor). |

## 115. Owner answers on the compliance report (register v0.115, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-460 — Session models: subagents on Opus 4.6 by the owner's setting; main sessions pinned to Opus 5.5 and recorded
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report (DEC-459): 91 co-author lines and about 70 worker sessions name "Claude Opus 4.6"
- **Decision:**
  - `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6` is the owner's own user setting: in-session subagents run on
    Opus 4.6 by design. It is kept. The "Claude Opus 4.6" co-author lines come from subagent sessions and are
    not a defect.
  - Main sessions run on Opus 5.5, pinned explicitly from now on: a lead is started with
    `~/.local/bin/claude -p ... --model claude-opus-5-5`, a launched worker with
    `gov launch <role> <ticket> -- --model claude-opus-5-5`.
  - Each session's model is recorded in close records.

### DEC-461 — The three closes recorded green without a saved re-run are accepted; every re-run alone is saved from now on
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report: the closes of W1-26 (`64172c93`), W1-23 (`a7964c97`) and W1-50 (`b894a7b7`) say the regression was green while its summary shows failures in the latency suites, and no output of the re-run alone was saved · **Under:** DEC-372
- **Decision:** Accepted, since later full regressions show those suites green and W1-42 re-checks everything.
  The orchestrator's new rule is confirmed: the output of every re-run alone is saved beside the regression
  summary.

### DEC-462 — A designer's brief states behaviour and sources only
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report: the orchestrator's designer briefs for W1-27 and W1-30 named private identifiers of the implementation · **Under:** MR-3, DEC-069
- **Decision:** Confirmed stopped. A brief for a test designer states behaviour and sources, never the names of
  the implementation's private parts.

### DEC-463 — Decisions recorded late are accepted; from now on the record comes first, and `gov check` flags a commit citing an unrecorded decision
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report: DEC-391, DEC-417, DEC-437, DEC-440, DEC-450, DEC-452 and DEC-455 were recorded after the work they authorise
- **Decision:**
  - Those seven are accepted as recorded late.
  - From now on a decision is recorded before the change it authorises.
  - A KPI line is added to W1-26 (or the ticket the orchestrator chooses) so that `gov check` flags a commit
    that cites a decision id missing from the register at that commit. The orchestrator chooses W1-26 and
    reopens it for this line, test first.

### DEC-464 — Delegated decisions that touched containment, the freeze or the launcher are ratified after the fact
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report · **Ratifies:** DEC-266, DEC-267, DEC-268, DEC-269, DEC-270, DEC-392, DEC-404, DEC-408, DEC-453
- **Decision:**
  - **The deviation:** these nine decisions were taken by the orchestrator under delegation (DEC-220, later
    DEC-416) although they touched containment (DEC-266 to DEC-270, DEC-453), the freeze or the launcher
    (DEC-392, DEC-404, DEC-408), before the rule that a delegated decision may only make such things
    stricter, or outside what delegation covers.
  - **The ratification:** the owner ratifies all nine now, after the fact. They stand as decided.

### DEC-465 — The pushes of `w1/integrate` were the owner's
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report's open point (who ran the 12 pushes)
- **Decision:** All 12 pushes of `w1/integrate` were owner actions, through the operator console. No agent
  session pushes.

### DEC-466 — What the report shows as instruction-only is mechanised with what Wave 1 has built
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report · **Amends:** the orchestrator's standing rule that `gov close` is never run against this repository (it holds until W1-30 is merged) · **Under:** DEC-458, DEC-459
- **Decision:**
  - Once W1-30 is merged, every ticket close goes through `gov close`.
  - Before every merge into `w1/integrate`, `gov check` is run, and red is treated as blocking.
  - After W1-30 and W1-26 are in use, the read-only subagent re-classifies the rules, and whatever is still
    instruction-only becomes a Wave 2 list for mechanising. That list is added to the exit package (DEC-458).

| Version | Date | Change |
|---|---|---|
| 0.115 | 2026-10-07 | Owner answers on the compliance report: DEC-460 (subagents on Opus 4.6 by the owner's setting; main sessions pinned to Opus 5.5 and recorded in close records), DEC-461 (three closes accepted; every re-run alone saved), DEC-462 (designer briefs state behaviour and sources only), DEC-463 (late records accepted; record first; `gov check` flags a commit citing an unrecorded decision, W1-26 reopened), DEC-464 (nine delegated decisions on containment, the freeze and the launcher ratified after the fact), DEC-465 (the pushes were the owner's), DEC-466 (closes through `gov close` after W1-30; `gov check` before every merge, red blocks; a Wave 2 list of what stays instruction-only). |

## 116. One delegated decision, for the owner to confirm or replace: what "red blocks a merge" means while this repository is not yet adopted (register v0.116, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-467 — Until this repository is adopted, `gov check` blocks a merge on any red that the recorded baseline does not hold
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; provisional: brought to the owner at once, who may replace it) · **Basis:** DEC-466 orders `gov check` before every merge into `w1/integrate`, red blocking. Run on this repository at `46ec8da3` (output kept as `.gov-runtime/scratch/orchestrator/log/check-at-46ec8da3.json`), `gov check` exits 3 with thirteen hard-block checks red, none caused by a ticket branch: `gov` is not on PATH for a check command (fresh-agent reconstruction), the tickets are not in the record store (context reproducibility), the tickets' `depends_on` name W1 ids (core-graph), records without `state_class` (core-schema), the indexes are stale after every commit since the one rebuild (index freshness, recovery/rebuild), the dev tiers are not configured (retrieval regression), the secrets check exceeds its 60 seconds on this tree, and five policy keys have no check (security, test, change, human_gate, tool). Read literally, DEC-466 would stop every merge until W1-39 and W1-41 adopt this repository · **Under:** DEC-466, DEC-425
- **Decision:**
  - The baseline is the set of red checks at `46ec8da3`, each with its reason, recorded in
    `governance/project/bootstrap.md`.
  - Before every merge into `w1/integrate` the orchestrator runs `gov check` on the branch to be merged (after
    the integration branch is merged into it) and saves the output beside the regression summary. A check that
    is red and is not in the baseline, or is in the baseline with a new finding caused by the branch, blocks
    the merge. A baseline red is named in the merge's record, never called green.
  - A baseline red that turns green leaves the baseline and may not come back.
  - The baseline is emptied by W1-39 and W1-41 (adoption of this repository) and by the exit run; what cannot
    be emptied is an owner item in the exit package.

| Version | Date | Change |
|---|---|---|
| 0.116 | 2026-10-07 | One delegated decision, provisional: DEC-467 (until this repository is adopted, `gov check` blocks a merge on any red the recorded baseline at `46ec8da3` does not hold). |

## 117. Two delegated decisions on W1-38: the OpenSpec skills are registered sources too; who refreshes the registered OpenSpec sources (register v0.117, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-468 — The six skills OpenSpec writes beside its commands are registered rulesync sources, like its commands
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** W1-38's test designer measured with rulesync 24.0.0 that `generate --delete` removes every file under `.claude/commands/` and `.claude/skills/` that is not a registered source, and that `openspec init --tools claude` (OpenSpec 1.13.2) writes six commands and six `openspec-*` skills. The ticket's failure line reads "generate --delete removes OpenSpec or vendored skills"; DEC-074 (question 7) makes rulesync the holder of what OpenSpec writes. Registering the commands alone would let `--delete` remove the six skills.
- **Decision:**
  - The registered rulesync sources hold what the registered OpenSpec version ships, unchanged: its six commands and its six skills. A text written for the ticket in their place is not a source.
  - The acceptance cases compare the generated files with what the installed, registered OpenSpec writes; an OpenSpec that is absent or of another version fails those cases with that reason.
  - Recorded before the change (DEC-463): the designer's cases for the six skills and the engineer's sources follow this entry.

### DEC-469 — The change that moves the registered OpenSpec or rulesync version refreshes the registered sources in the same change
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the cases of DEC-468 turn red when the tool registry names a new OpenSpec version and the sources still hold the old texts; no source named who refreshes them.
- **Decision:**
  - The ticket that changes the `openspec` or `rulesync` entry of the tool registry refreshes the registered sources from that version in the same change, in a temporary folder outside the repository (nobody runs a writing rulesync command in the repository), and copies the result in.
  - Where a project keeps its check declarations once adopted (`template/governance/kernel/checks/` today, `governance/kernel/` after adoption) is not decided here: W1-39 settles it.

| Version | Date | Change |
|---|---|---|
| 0.117 | 2026-10-07 | Two delegated decisions on W1-38: DEC-468 (OpenSpec's six skills are registered rulesync sources, like its six commands), DEC-469 (the change that moves the registered version refreshes the sources). Next free id: DEC-470. |

## 118. One delegated decision on W1-30: four points the test designer found open in what `gov close` measures (register v0.118, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-470 — `gov close`: no store means no close; a missing source refuses; a probe refusal is a failed verification; the model is read from the commits until launch records carry it
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** W1-30's test designer (round 5, commit `f07051bf`) returned four points no source settles. The rule of DEC-454 stands over all four: nothing is closed, and nothing is recorded, that was not measured.
- **Decision:**
  - **The record store.** When the ticket's context cannot be built because the project has no record store, `gov close` refuses with that reason. It does not build the store itself: building it is `gov rebuild`'s work.
  - **A missing source.** A ticket naming a source that does not resolve is refused, as DEC-454 and the context command state. The older case that expected a close record listing the missing source with a reason gives way and is rewritten to the refusal.
  - **The probe gate's exit code.** A refusal by the probe gate is a finding about the ticket's work like missing trailers or a containment finding: exit code 3 (verification failed). Exit code 4 stays for an escalation in force.
  - **Session models (DEC-460).** No source records a session's model today: the launcher writes no launch record with a model and commits carry no session trailer. Until that exists, the close record lists, for each of the ticket's commits, its role and the model named in its `Co-Authored-By` trailer, exactly as read; a commit without such a line is listed with "not measured". No model is guessed and no commit is left out. A launch record per session (id, role, ticket, model) and a `Session:` trailer are an item for the Wave 2 list of DEC-466.
  - Recorded before the change (DEC-463): the designer's cases and the engineer's code for these four points follow this entry.

| Version | Date | Change |
|---|---|---|
| 0.118 | 2026-10-07 | One delegated decision on W1-30: DEC-470 (no store, no close; a missing source refuses; a probe refusal exits 3; the model is read from the commits' co-author lines until launch records carry it). Next free id: DEC-471. |

## 119. One delegated decision on W1-38: a role's adapter tools equal the kernel role's; which paths under `.claude/` must have a source (register v0.119, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-471 — The adapter source of a role names exactly the kernel role's tools; the three generated folders and the settings file must have a source for everything in them
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** W1-38's test designer (round 4, commit `5ca159c0`) returned two open points. The kernel role files are the authority for a role's limits (DEC-066, W1-33); the ticket's third success line reads "generated adapters match their source". The delivered adapter source of the independent auditor names four tools where the kernel role names eight (among them `Write` and `Edit`, "for its report only").
- **Decision:**
  - **Tools.** The tools an adapter source gives a role are exactly those the kernel role's Tools field names: neither more nor fewer. The auditor's source is brought to the kernel's eight. Whether the kernel's list for a role should be narrower is a question for that role's file (W1-33), not for the adapter.
  - **Paths under `.claude/`.** For this ticket the check requires a source for everything in `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and for every key of `.claude/settings.json`; `.claude/settings.local.json` and `.claude/worktrees/` belong to other owners (DEC-063, DEC-050) and are not findings. Anything else directly under `.claude/` is not judged yet: W1-42's exit run records what a live session writes there, and the rule for those paths is decided after it (an item for the exit package).
  - Recorded before the change (DEC-463): the engineer's code and the auditor source follow this entry.

| Version | Date | Change |
|---|---|---|
| 0.119 | 2026-10-07 | One delegated decision on W1-38: DEC-471 (a role's adapter tools equal the kernel role's; the three generated folders and the settings file must have a source for everything in them). Next free id: DEC-472. |

## 120. Owner answers: the `gov check` baseline, the decision-citations check, `gov close` before adoption, index freshness, four delegated decisions accepted (register v0.120, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-472 — DEC-467 confirmed: the `gov check` baseline; it must be empty at W1-42's exit run
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** the orchestrator's provisional DEC-467.
- **Decision:**
  - A merge into `w1/integrate` is blocked by any red outside the recorded baseline, or by a new finding in a baseline check. A baseline red is named in the merge record and never called green. A baseline check that turns green may not return to the baseline.
  - Added: the baseline must be empty at W1-42's exit run, cleared by W1-39 and by W1-41's adoption. Any item still in it then comes to the owner as a decision package. This is added to W1-42's KPI lines.

### DEC-473 — The decision-citations check knows both register forms (W1-26, package P-1)
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** DEC-463; the test designer's package P-1 on W1-26's follow-up.
- **Decision:**
  - A decision is recorded either as a decision file, or as an entry of a register file that the project names in one line of configuration under `governance/project/`. With no register file named, decision files alone count. No path of this repository goes into the kernel.
  - Heading grammar of a register file: a level-3 heading `### DEC-<digits>` at the start of a line, followed by a space, a colon or a dash and the title. A heading inside a fenced code block does not count.

### DEC-474 — The decision-citations check judges the commits after a base commit recorded in the project (W1-26, package P-2)
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** DEC-463; the test designer's package P-2.
- **Decision:**
  - A base commit is recorded in the project's configuration: the commits after it are judged. With no base recorded, the whole history is judged.
  - In this repository the base is `46ec8da3`, the commit that records DEC-463.

### DEC-475 — The designer's three readings on the decision-citations check are confirmed
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** W1-26's follow-up cases (`e3d2cc1b`).
- **Decision:**
  - Severity is `warning`: history cannot be rewritten, and a hard block could never clear.
  - The family is authority/role limits.
  - A citation is a DEC id in the commit message only.
  - W1-26's follow-up is then merged and closed, with the pre-merge `gov check`.

### DEC-476 — `gov close` stays strict for every project; how every ticket closes here until W1-41 (W1-30, package P-3)
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** DEC-466; the orchestrator's package P-3 (thirteen baseline reds; commits without `Implements:`).
- **Decision:**
  - `gov close` holds no baseline: it stays strict for every project.
  - From now on every worker commit carries `Implements:`.
  - Until W1-41, the orchestrator runs `gov close` on every ticket. Where it refuses only because of baseline reds (DEC-467, DEC-472), or only because of commits made before this decision without `Implements:`, its output is saved beside the close, the ticket is closed with `tk close`, and the ticket is listed for the exit auditor.
  - Any other refusal reason means the ticket does not close.

### DEC-477 — Index freshness: `gov rebuild` is run before W1-42's exit run and whenever a measurement needs fresh indexes
- **Status:** ACCEPTED (owner, 2026-10-07) · **Supersedes:** the one-off limit of DEC-448 (its other parts stand) · **Basis:** `gov doctor` at `6db36969` reports nine stale index files after the one rebuild.
- **Decision:**
  - Stale indexes between commits are normal during development.
  - `gov rebuild` is run on this repository before W1-42's exit run, and whenever a measurement needs fresh indexes. This replaces DEC-448's limit of a single run.

### DEC-478 — DEC-468, DEC-469, DEC-470 and DEC-471 are accepted
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** the orchestrator's delegated decisions on W1-38 and W1-30.
- **Decision:**
  - DEC-468 (OpenSpec's six skills are registered sources), DEC-469 (who refreshes the registered sources), DEC-470 (`gov close`: no store, a missing source, the probe gate's exit code, the models of the commits) and DEC-471 (role tools; paths under `.claude/`) are accepted as recorded.
  - On DEC-471: the independent auditor's eight tools stay as in its kernel role; the guard holds its writes to its report folder.

| Version | Date | Change |
|---|---|---|
| 0.120 | 2026-10-07 | Owner answers: DEC-472 (DEC-467 confirmed; the baseline empty at W1-42's exit run), DEC-473 (both register forms; heading grammar), DEC-474 (base commit, here `46ec8da3`), DEC-475 (severity warning, family authority/role limits, citation in the message only), DEC-476 (`gov close` strict; closes until W1-41), DEC-477 (`gov rebuild` before the exit run and when a measurement needs it; replaces DEC-448's one-off limit), DEC-478 (DEC-468 to DEC-471 accepted). Next free id: DEC-479. |

## 121. One delegated decision on W1-26: where a project records its register file and its base commit (register v0.121, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-479 — The register file and the base commit of the decision-citations check are two optional keys of the project's path map
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** DEC-473 and DEC-474 order "one line of configuration under `governance/project/`" without naming the file. W1-26's test designer (commit `ac952490`) found no source that names it and settled on the path map: DEC-185 refuses a new overlay file and has commands load the `governance/project/` files they know, the path map first; DEC-224 and DEC-230 already put project data there under top-level keys.
- **Decision:**
  - `governance/project/path-map.yaml` holds two optional top-level keys: `decision_register` (the register file's path from the project root) and `decision_citations_base` (a commit id, full or abbreviated).
  - The configuration read is the project's present one, not each judged commit's: a base can only be recorded after it exists.
  - With a base recorded and no commit after it, the check gives the unmeasured answer, never green.
  - A named register that cannot be read at a judged commit is never green and its path is reported, also when the cited decision is recorded as a decision file.
  - In this repository the two keys are `docs/DECISION_REGISTER.md` and `46ec8da3` (DEC-474); the orchestrator adds them when the check is merged.
  - Recorded before the change (DEC-463): the engineer's code follows this entry.

| Version | Date | Change |
|---|---|---|
| 0.121 | 2026-10-07 | One delegated decision on W1-26: DEC-479 (the register file and the base commit are two optional keys of the project's path map). Next free id: DEC-480. |

## 122. One delegated decision on W1-30: `gov close` refuses on what `gov check` blocks on (register v0.122, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-480 — For a governance-changing ticket, `gov close` refuses on exactly the checks `gov check` reports red at hard-block; it holds no rule of its own about checks
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** DEC-476 (strict, no baseline inside `gov close`). W1-30's test designer (round 6, commit `fd7ad4f0`) returned three points no source settles: a warning check that cannot run, the time limit of a check, and a built-in hard-block check that the runner reports yellow where its tool is absent. As for containment (DEC-453), the close gate takes the judgement of the component that owns it: W1-26's runner is the authority on a check's status.
- **Decision:**
  - When a ticket's commits change a governance file, `gov close` runs the checks at the commit being closed through W1-26's runner and refuses when the runner reports any hard-block check red, naming each. That is the same condition on which `gov check` blocks a merge.
  - A check of severity warning refuses nothing, whether it ran and failed or could not run: the runner gives both the same status, and `gov close` does not read more into it. The designer's case that expected a refusal for a warning check whose command is absent is reversed.
  - A hard-block check that cannot run (its command absent, over its time limit) refuses when the runner reports it red, as the runner does today. The time limit of a check is the runner's own; `gov close` adds none, and its `--timeout` stays the limit of its test runs.
  - A hard-block check the runner reports yellow (not applicable, or a built-in check whose tool is absent) refuses nothing. Whether the runner should report an absent tool of a hard-block check as red is a question for W1-26, listed for the Wave 2 list of DEC-466.
  - A ticket without acceptance tests is a finding about the ticket's work: exit code 3, counted, a repair ticket (the designer's reading of DEC-455, accepted).
  - Recorded before the change (DEC-463): the designer's adjusted cases and the engineer's code follow this entry.

| Version | Date | Change |
|---|---|---|
| 0.122 | 2026-10-07 | One delegated decision on W1-30: DEC-480 (`gov close` refuses on exactly the checks the runner reports red at hard-block; warning checks refuse nothing; the time limit of a check is the runner's; a ticket without acceptance tests is a counted finding). Next free id: DEC-481. |

## 123. Owner answers: the two new baseline checks, the trailers base, `gov close` in use (register v0.123, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-481 — `adapter-portability` joins the `gov check` baseline with its 43 findings; W1-38 merges and closes
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-4. W1-38's check compares this repository's hand-kept `.claude/`, `CLAUDE.md` and `AGENTS.md` with freshly generated output; they differ until the owner applies the generated output at the exit (`log/check-at-W1-38-premerge.json`).
- **Decision:**
  - `adapter-portability` joins the baseline of DEC-467, with its 43 findings as the recorded state. A new finding in it blocks a merge, as for the other baseline checks (DEC-472).
  - It clears at the exit, when the owner applies the generated output.
  - The check running `rulesync generate` into its own empty temporary folder, writing nothing in the project, is within the owner's rule that nobody runs a writing rulesync command in this repository.
  - W1-38 is merged and closed.

### DEC-482 — `product-traceability-trailers` joins the baseline with its 735 findings; a project may record a trailers base commit
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-5 (`log/check-at-W1-30-premerge.json`): 408 commits of closed tickets without an `Implements:` trailer, made before DEC-476, and 327 `Implements:` ids that resolve to no record here before adoption.
- **Decision:**
  - `product-traceability-trailers` joins the baseline of DEC-467, with its 735 findings as the recorded state. A new finding in it blocks a merge.
  - The check gets the same base-commit setting as the citations check (DEC-474, DEC-479): a project may record a trailers base, and only commits after it are judged; with none, the whole history. Here the base is the commit that recorded DEC-476, `429815b5`. That removes the 408 commits made before the rule.
  - The unresolved ids are cleared by W1-41's adoption.
  - The base setting is built in W1-41 or in a short follow-up the orchestrator chooses.
  - W1-30 is merged and closed, through `gov close` itself under DEC-476.

### DEC-483 — The owner-decision lookup of `gov close` reading decision files only is a residual for W1-41's adoption
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** W1-30's escalation path reads the owner's decision from decision files, not from a register file such as this repository's.
- **Decision:** It is recorded as a residual of W1-30 and handed to W1-41's adoption; it does not hold W1-30's merge.

### DEC-484 — The run time of `gov close` here is accepted; it runs in the main tree while the next tickets are worked in their worktrees
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** `gov close` runs the project's tests; on this repository that is about an hour per ticket.
- **Decision:** The run time is accepted. `gov close` runs in the main tree while the next tickets' sessions work in their worktrees, within the resource gate. (This replaces the orchestrator's own precaution of running it with nothing else running.)

### DEC-485 — DEC-479 and DEC-480 are accepted; three residuals of the citations check go on the Wave 2 list
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** the two delegated decisions told to the owner; W1-26's follow-up residuals.
- **Decision:** DEC-479 and DEC-480 stand as written. On the Wave 2 list (DEC-466): moving the base takes earlier commits out of judgement unreported; any Markdown file with a decision id in its frontmatter counts as its record; a register heading alone is enough for an entry.

### DEC-486 — The orchestrator's closed count is reconciled: 41 of 50 closed
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** the orchestrator reported 45 of 50 closed while nine tickets were open. The ticket files give 41 closed, 2 in progress, 7 open; the orchestrator had counted closed follow-ups of already closed tickets.
- **Decision:** Reports state the count from the ticket files and list the open tickets by id. At this entry: in progress W1-30 (`DAEO-2lwj`), W1-38 (`DAEO-3ef2`); open W1-31 (`DAEO-6mk8`), W1-32 (`DAEO-8goq`), W1-39 (`DAEO-5ylr`), W1-40 (`DAEO-fdkq`), W1-41 (`DAEO-cdoi`), W1-42 (`DAEO-gjjf`), W1-43 (`DAEO-03pw`). Order of work: W1-31 and W1-40 after W1-30, W1-39 after W1-38, then W1-32, W1-41, the exit run and the exit audit.

| Version | Date | Change |
|---|---|---|
| 0.123 | 2026-10-07 | Owner answers: DEC-481 (`adapter-portability` in the baseline, 43 findings; W1-38 merges), DEC-482 (`product-traceability-trailers` in the baseline, 735 findings; a trailers base commit, here `429815b5`; W1-30 merges and closes through `gov close`), DEC-483 (owner-decision lookup from a register file: residual for W1-41), DEC-484 (`gov close` run time accepted; runs beside worktree work), DEC-485 (DEC-479 and DEC-480 accepted; three Wave 2 items), DEC-486 (41 of 50 closed; open tickets listed by id). Next free id: DEC-487. |

## 124. One delegated decision on W1-30: what the review of `gov close` found and how each finding is settled (register v0.124, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-487 — W1-30's review found thirteen ways `gov close` closes what it did not measure; the fail-open ones are fixed in a follow-up, cases first
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** `gov close` refused W1-30 for a missing probe record (FULL profile). The final code had the orchestrator's reading (DEC-449) and no fresh review. A read-only reviewer (brief A3, session `350cc2a3`, at `6f2130c8`) returned thirteen findings, most reproduced in throwaway projects (`log/W1-30-probe.json`). The orchestrator prompt, section 5 step 5: findings that could lose work, let an implementer change acceptance tests or fail open are fixed, a test design batch first; the rest are residuals. Recorded before the change (DEC-463).
- **Decision (what `gov close` does after the follow-up):**
  - **The tree it measures is the commit it records.** With any tracked file changed or any untracked, not ignored file present, `gov close` refuses before it measures and names the paths. It is not a finding about the ticket's work: not counted, no repair ticket.
  - **The test runs are the suite's own.** Options a caller's environment would add to the test runner are not passed on; a run of the ticket's acceptance tests in which no test passed refuses, as a run that collects none does.
  - **Every commit since the ticket's first is somebody's.** A commit after the ticket's first commit that names no task at all refuses the close (its work was measured by no ticket); a commit of the ticket without a role refuses like one without `Implements:`; a root commit and a merge commit are judged with the paths they bring.
  - **The probe record is evidence only if it could not have been written by the implementer:** it is committed, by a commit with the orchestrator's role; its judgement says the probe passed (a failing judgement refuses); the probed commit is a commit id, not a name that moves; a commit with the reviewer's role refuses wherever it lies in the ticket's range.
  - **The owner's decision lifts an escalation only if** W1-11's checker confirms it as the owner's and in force, it is committed, it was recorded after the escalation began, and it has not lifted an escalation before.
  - **The escalation state cannot be reset by its absence:** an escalation in force with its counter missing, or a counter that is not a count from zero up, blocks and says so. The counter, the ticket files and the records are written whole or not at all.
  - **A close that fails at its last step leaves no record that says the ticket closed.**
  - **A record store older than the commit being closed refuses** (the context would be built from superseded records); the answer names `gov rebuild`.
  - **The installed kernel counts as governance files:** a ticket commit under `governance/kernel/` runs the checks, as one under the template's kernel does. The suite's earlier settlement to the contrary is revised.
  - A time limit that is not a positive number is refused as an invalid argument.
- **Residuals, not fixed in Wave 1:** a second close of a reopened ticket overwrites the first close record (it survives in git); every refusal for the same cause opens a new repair ticket, and their number shows the count to the looping session (against DEC-096 in spirit: Wave 2 list); the folder of escalation files is not among the command's declared write paths; `gov close` records `Implements:` ids without resolving them (the traceability check resolves them).
- **Not decided here (package P-6, with the owner):** that `gov close` stops at its first finding, where it looks for the ticket tool, and how tickets close in this repository before adoption.

| Version | Date | Change |
|---|---|---|
| 0.124 | 2026-10-07 | One delegated decision on W1-30: DEC-487 (the review's thirteen findings; ten settled behaviours for a follow-up, cases first; four residuals). Next free id: DEC-488. |

## 125. One delegated decision on W1-39: the lock comparison, the update procedure, the adapter generation step (register v0.125, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-488 — W1-39: one comparison of a project with its lock, owned by W1-39; the update procedure is in the template's messages and the lock's header; adapter generation is a documented step after `copier copy`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-39 lead's packages P-1 (in part), P-3 and P-4 (`log/W1-39-lead-run1.json`), each with the lead's recommendation. The parts of its packages that change a ticket's allowed paths (P-1's call site in `gov doctor`, P-2, P-5) are the owner's and are not decided here.
- **Decision:**
  - **The comparison of a project with its lock is built once, by W1-39, as a public function of its own code:** given a project, it answers match or drift, the drifted files, and the reason where it could not compare. It never answers match without having hashed: an absent or empty manifest is not a match; a kernel file that the manifest does not list is drift, named; the lock's template tag and commit are compared with the answers file. `gov doctor` is to call it (where and under which ticket: with the owner).
  - **Only `__pycache__/` folders are left out of "a kernel file the manifest does not list".** Git-ignored files in general are not left out: an ignore rule is the project's to write, and a file hidden by one would escape the comparison.
  - **The update procedure is documented in two places that reach a product repository:** the template's messages after copy and after update, and a comment header of the generated lock.
  - **`copier copy` does not run the adapter generation.** Generating `.claude/`, `CLAUDE.md` and `AGENTS.md` from `.rulesync/` is a documented step after the copy, named in the procedure; an install does not fail where rulesync or Node is absent. W1-41's adoption runs or names the step.
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.125 | 2026-10-07 | One delegated decision on W1-39: DEC-488 (the lock comparison is W1-39's and never matches unhashed; only `__pycache__/` is left out; the update procedure in the template's messages and the lock's header; adapter generation a documented step). Next free id: DEC-489. |

## 126. One delegated decision on W1-40: the hook files' author, what pre-push runs, the evidence record (register v0.126, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-489 — W1-40: the engineer writes the hook and workflow files through its template files; pre-push runs the declared G3 checks; the evidence record is a git note on the head commit
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-40 lead's packages P-A, P-1, P-2, P-3, P-5, P-B and P-C (`log/W1-40-lead-run1.json`), each with its recommendation. Its P-4 (whether the CI workflow may install registered tools on the hosted runner) is an install and the owner's; it is not decided here.
- **Decision:**
  - **Who writes `lefthook.yml` and the workflow files.** A launched engineer's Write tool refuses these file names. The files stay the implementer's: the engineer writes the template file with its tools and produces the repository's own file from it with a command (a copy, or a rendering where the two differ). Only if that is refused too does the orchestrator place the engineer's content word for word, with a commit that says so.
  - **What pre-push runs.** The declared checks of tier G3; a model-dependent test belongs there when its ticket declares it as a check. Where a project declares no G3 check, the push is not refused for that alone: the evidence record states that no G3 check is declared, in those words and never as a pass, and CI reports it.
  - **A tier named to the hook's command that has no declaration is never passed over silently** when another named tier has one, except G3 as above; a mistyped tier refuses.
  - **The evidence record is a git note on the head commit, under a ref of its own,** written by the pre-push hook after G3 has run, and pushed by the hook; CI fetches that ref and reads the note of the commit it builds. It holds at least the commit id, the result and the checks that ran. A record for another commit, or none, fails CI. The choice is documented in the hook file and the workflow.
  - **A record edited by hand is not detected in Wave 1** (a deliberate bypass, like skipping the hook): residual; a hash or signature is a Wave 2 item.
  - **The template files use no Copier answers**; they render to this repository's own files, with GitHub's expressions escaped.
  - **Tier selection stays as built** (the hook command calls the check runner's internals): residual, unit tests hold the join; a public tier argument of the runner, and whether its tier-less built-in checks belong to G1 and G2, go on the Wave 2 list. CI runs the whole of the deterministic checks, so no check runs nowhere.
  - **The second gitleaks scan stays strict** (it does not carry the project's path allowlist): residual; in this repository it will refuse commits that touch the canary fixtures once the hooks are activated, which is named in the exit package.
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.126 | 2026-10-07 | One delegated decision on W1-40: DEC-489 (hook and workflow files written by the engineer through their templates; pre-push runs declared G3 checks, none declared is recorded as such; the evidence record is a git note under its own ref; three residuals). Next free id: DEC-490. |

## 127. One delegated decision on W1-30: the test designer's seven points on DEC-487 (register v0.127, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-490 — DEC-487 made exact: which task-less commits refuse, the judgement words, what a refusal's own files do to the tree rule, the exit codes
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** W1-30's test designer wrote the cases for DEC-487 (commit `ed52a286`: 43 new cases, 39 red for the reviewer's reasons) and returned seven points no source settles (`log/W1-30-r8-cases.json`). Recorded before the engineer's change (DEC-463).
- **Decision:**
  - **A commit that names no task** (DEC-487 said: refuses). Made exact: among the commits after the ticket's first, one that names no task refuses the close when it changes the ticket's acceptance tests, a path inside the ticket's allowed paths, or the ticket's own file: that is work on this ticket which no ticket measured. One that changes a governance file has the governance checks run, as a ticket commit would. After the probed commit, one that changes a path inside the ticket's allowed paths makes the probe stale. Any other task-less commit (a decision record, a checkpoint, a probe record, another folder) refuses nothing. A commit that names another ticket is that ticket's.
  - **The judgement of a probe record** is `pass` or `passed` to be accepted; `fail`, `failed` or any other value refuses.
  - **Store freshness:** the cases hold the behaviour only (refused, the rebuild named, nothing closed). The engineer uses a mark the store or the runtime already keeps of the commit it was built from; if none exists inside what `gov close` may read, that case is returned, not guessed.
  - **The tree rule and a refusal's own files.** A refused close leaves its repair ticket as an untracked ticket file. An untracked ticket file whose parent is the ticket being closed does not refuse the next close. Every other untracked, not ignored file and every change to a tracked file does, the ticket's own file included.
  - **Exit codes.** A tree that is not its commit, a record store older than the commit, and a counter that is not a count (the file named in the answer) are "could not measure": exit code 1, not counted, no repair ticket. An owner's decision that does not qualify lifts nothing: the close stays blocked, with the blocked exit code. A time limit that is not a positive number is refused like any other invalid argument, before anything runs.
  - **"Written whole or not at all"** is held by the unit tests and by reading (write beside, then rename); no acceptance case with timing.

| Version | Date | Change |
|---|---|---|
| 0.127 | 2026-10-07 | One delegated decision on W1-30: DEC-490 (which task-less commits refuse; judgement words; a refusal's own repair ticket does not dirty the tree; exit codes for "could not measure"). Next free id: DEC-491. |

## 128. One delegated decision on W1-31: session attribution, the sandbox figure, the learning metrics' sources (register v0.128, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-491 — W1-31: the caller names a ticket's sessions; the sandbox's added tokens are measured once at the exit run; rewrites are read from designer commits and disputes from a record the orchestrator writes
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-31 lead's packages P-2, P-5, P-6 and P-7 (`log/W1-31-lead-run1.json`), each with its recommendation. Its P-3 (cache creation in the denominator) and P-4 (how five of the seven governance sources are counted) define the figure the Wave 1 exit is judged by, and its P-1 (the call from `gov close`) depends on them: these are with the owner and are not decided here.
- **Decision:**
  - **Attribution.** The caller names the sessions of a ticket (as built). A launch record per session, from which attribution would be automatic, stays on the Wave 2 list (DEC-470).
  - **The sandbox's added system-prompt tokens (DEC-170)** are measured once, by a paired run in W1-42's exit run (the same prompt in a launched and in a plain session), recorded with its date and the Claude Code version; the counter reports that recorded figure per launched session as its separate line, and "not measured" until the record exists.
  - **Acceptance tests rewritten after implementation began** are read from the test designer's commits after the ticket's first engineer commit; the reason for each is a trailer `Rewrite-Reason:` on that commit, and a rewrite without one is reported as "reason not recorded", never left out. From this entry on, every designer brief for a ticket that already has an engineer commit asks for the trailer.
  - **KPI disputes** are read from a per-ticket record the orchestrator writes at the merge (one line per dispute with the decision that settled it); without the record the figure is "not measured".
  - **Smaller points.** A ticket without a profile is "not measured" for the per-profile report (the counter does not assume STANDARD). The aggregate by profile across tickets is W1-42's. A ticket whose record folders were read and hold nothing counts 0 for them; a folder that is absent is "not measured". The close record's own tokens are counted by a re-measure after the close. A session's model is reported from both places, each named: the session log's and the commits' co-author lines.
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.128 | 2026-10-07 | One delegated decision on W1-31: DEC-491 (sessions named by the caller; the sandbox figure measured once in W1-42; rewrites from designer commits with a `Rewrite-Reason:` trailer; disputes from an orchestrator record; smaller points). Next free id: DEC-492. |

## 129. Owner answers: closing before adoption, W1-39's paths, CI installs, how the governance share is measured (register v0.129, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-492 — How tickets close until W1-41: `gov close` reports every finding and finds the ticket tool on PATH; a refusal for adoption gaps alone closes with `tk close`
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-6. `gov close` refused W1-30 and W1-38 at its first finding (`log/close-W1-30.json`, `log/close-W1-38.json`), and cannot close any ticket here before adoption (it looks for the ticket tool only at the kernel path).
- **Decision:**
  - **In the W1-30 follow-up already running:** `gov close` reports every finding in one run instead of stopping at the first, and finds the ticket tool on PATH as well as at the kernel path.
  - **Until W1-41:** the orchestrator runs `gov close` once per ticket and saves its output. It closes with `tk close`, and lists the ticket for the exit auditor, only if all of these hold: every finding `gov close` reports is an adoption gap (baseline reds; commits before DEC-476 without `Implements:`; the orchestrator's merge commits before 2026-10-07 without it; the ticket tool not at the kernel path); the orchestrator has checked the rest itself (Role trailers, containment, the full regression, the pre-merge `gov check`); and a FULL ticket has its probe record of the final code.
  - **Refusals for adoption gaps alone do not count toward escalation.**
  - **Three containment findings in history are accepted as recorded history:** `148f7584` and `29af0646` on W1-30 (merge commits' own change to the shared W1-07 support file), and `a95e54a3` on W1-38 (eight kernel skill files, restored in `deead8f9`).
- **Orchestrator's reading, recorded as such:** DEC-476 keeps `gov close` without a baseline inside it, so "do not count toward escalation" is applied outside the tool: where the tool's own counter is raised by such a refusal, the orchestrator does not treat it as an iteration, and a block reached only by such refusals is brought to the owner as that, not as a looping ticket.

### DEC-493 — W1-39's allowed paths gain the doctor call site, the overlay's path map, Copier's standard answers file and an ignore file
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-7, from the W1-39 lead's packages P-1, P-2 and P-5 and two residuals of earlier tickets.
- **Decision:** W1-39's `allowed_paths` gain, each in its own commit with `Task: DAEO-5ylr`:
  - `src/gov/doctor/command.py` and `tests/unit/doctor/**`, for the lock-comparison call only;
  - `template/governance/project/**`, shipping a minimal path map that an update never overwrites;
  - Copier's standard `.copier-answers.yml` (DEC-023), in place of `template/copier-answers*`;
  - `template/.gitignore`, ignoring `.gov-runtime/` and `__pycache__/`.

### DEC-494 — The CI workflow installs gitleaks and the `gov` package only, each verified against its archive's checksum; steps that need the dev tiers report "unmeasured"
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-8 (the W1-40 lead's P-4): the hosted runner has none of the tools the job needs.
- **Decision:**
  - The CI workflow installs only gitleaks and the `gov` package now; rulesync when the adapter comparison step is added.
  - Each at its registered version, in its own step, and each download verified against the checksum of its archive: a new field of `governance/project/tool-registry.yaml`, which the orchestrator adds and fills.
  - CI steps that need the dev tiers report "unmeasured", never green.

### DEC-495 — How the governance share is measured: session logs for hook output, the SessionStart packet and `gov` output; a labelled estimate for instruction files and MCP definitions; cache creation in the denominator
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-9 (the W1-31 lead's P-1, P-3 and P-4): five of the seven governance sources leave no trace today, so the share is always "not measured".
- **Decision:**
  - **Hook output, the SessionStart packet and `gov` output** are read from the harness's session logs by the counter's code, which outputs counts only and never content. The log format is learnt from a specimen made in a throwaway project in `/tmp` (one short headless session with one hook and one `gov` command), not from a real log of this machine; no worker reads a real session log.
  - **Instruction files and governance MCP definitions** are a static estimate on its own line, labelled "estimated".
  - **Cache creation is included in the denominator and shown separately; cache reads stay out.**
  - **The share reaches the close record through a small W1-30 follow-up once W1-31 is merged;** until then the orchestrator runs `gov telemetry` beside each close.
  - W1-42 reports the share with its measured and estimated parts separate; the 15% verdict is the owner's at the exit.

### DEC-496 — DEC-487 to DEC-491 are accepted; the reviewer looks at the fixed `gov close` before W1-30 closes
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** the five delegated decisions told to the owner (the review of `gov close` and its exact form; W1-39's lock comparison; W1-40's hook files and evidence record; W1-31's attribution and metric sources).
- **Decision:** DEC-487, DEC-488, DEC-489, DEC-490 and DEC-491 stand as written. A fresh reviewer probes the fixed `gov close` before W1-30 closes; its probe record is of the final code.

| Version | Date | Change |
|---|---|---|
| 0.129 | 2026-10-07 | Owner answers: DEC-492 (`gov close` reports every finding and finds the ticket tool on PATH; closes for adoption gaps alone go through `tk close` until W1-41; three containment findings accepted as history), DEC-493 (four additions to W1-39's allowed paths), DEC-494 (CI installs gitleaks and the `gov` package, verified by archive checksum; dev-tier steps report "unmeasured"), DEC-495 (the governance share: session logs, a labelled estimate, cache creation in the denominator; the call from `gov close` after W1-31), DEC-496 (DEC-487 to DEC-491 accepted; second review of `gov close`). Next free id: DEC-497. |

## 130. One delegated decision on W1-40: what the CI job does where a tool or a G3 check is absent, and five smaller points (register v0.130, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-497 — W1-40: a step whose tool is not on the runner says "unmeasured" and fails; "no G3 check declared" is reported in words and does not fail the job; the checkout brings the parent commit; an unknown check family fails as in `gov check`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-40 lead's packages P-6 to P-11 of its second return (`log/W1-40-lead-run2.json`), each with its recommendation; its P-4 is decided by the owner in DEC-494, which this entry applies and does not widen · **Refines:** DEC-489, DEC-494
- **Decision:**
  - **Installs (DEC-494, applied).** The workflow gains two steps of their own: gitleaks, downloaded from the registry's `archive` and verified against the registry's `archive_sha256` before it is unpacked, the step failing on a mismatch; and the `gov` package, installed from the checkout. The workflow installs nothing else: not pytest, not openspec, not rulesync, not lefthook. The version, the address and the checksum are read from `governance/project/tool-registry.yaml` by the step, or a case holds that the workflow's text and the registry agree.
  - **A step whose tool is not on the runner.** It prints the word "unmeasured" with the tool's name and fails. It is never green and it is never skipped in silence. This holds for the tests step (pytest is absent) and, inside `gov ci job`, for a check of `gov check` that reports its tool absent (openspec; rulesync for the adapter check): the job names that check as unmeasured and exits non-zero. This replaces the lead's recommendation on P-9 (take `gov check`'s yellow), because DEC-494 says such a step is never green. The later steps still run after a failed one, so one run of the job reports every step. Consequence, stated here and told to the owner: this repository's CI job is red, with "unmeasured" as the reason, until the owner approves those tools for the runner.
  - **P-6, a record that says "no G3 check declared".** `gov ci record` prints those words and exits 0. The record itself stays what DEC-489 made it: never the word "passed". The weakness is recorded: removing a project's G3 declarations turns that gate into a report. A project stating in a file that it declares no G3 check on purpose, the job failing without that statement, goes on the Wave 2 list.
  - **P-7, the notes ref with more than one clone.** Left as built: the push of the ref is never forced, and a clone whose notes do not descend from the remote's is refused. Fetching and merging the notes before writing goes on the Wave 2 list.
  - **P-8, `gov ci` declaring the class "read".** Left; nothing reads the class today. Wave 2 list.
  - **P-10, the skill-version check on a depth-1 checkout.** The workflow checks out with the parent commit (`fetch-depth: 2`), a case first. That the runner reports a missing parent commit as green instead of not measured is a residual in W1-26's code, on the Wave 2 list; so is that only the last commit of a push is compared.
  - **P-11, an unknown check family.** `gov ci job` fails for it as `gov check` does, a case first.
  - **The engineer's `install -D` after the guard refused `mkdir -p .github/workflows`.** Accepted: the file written is on the ticket's allowed paths, it was produced by the Bash copy DEC-489 prescribes, and the guard itself allowed that command. That the guard refuses to create the folder of an allowed file is a residual for the guard (Wave 2 list).
  - The adapter comparison keeps its named place in the workflow: `gov ci job` already runs the adapter check of `gov check`, which is unmeasured on the runner until rulesync is installed there (DEC-494: with that step).
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.130 | 2026-10-07 | One delegated decision on W1-40: DEC-497 (a step whose tool is absent says "unmeasured" and fails; "no G3 check declared" is reported and does not fail the job; `fetch-depth: 2`; an unknown check family fails; smaller points left for Wave 2). Next free id: DEC-498. |

## 131. Owner answers: W1-30's last review and the order of the probe for FULL tickets (register v0.131, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-498 — W1-30's second review is its last; what it may still change; a FULL ticket is probed before its merge
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER · **Under:** DEC-415, DEC-137 · **Refines:** DEC-496
- **Decision:**
  - **W1-30.** The review of the fixed `gov close` (after the DEC-487 follow-up) is the ticket's second and last independent review under DEC-415. After it, only two kinds of finding are fixed: a fail-open hole, and a silent close in a shape that ordinary work produces. Every other finding becomes a residual. A fail-open that one fix does not close comes to the owner as a decision package, not as another round. Then W1-30 closes.
  - **Process, for every FULL ticket from now on.** The fresh reviewer probes the ticket's final code before the orchestrator merges it (DEC-137), not after a later tool asks for the record.
  - **Deviation.** W1-30 was merged (`2c71bc64`) before any independent probe of its final code; the probe was commissioned only after `gov close` refused for the missing record. This is recorded as a deviation in the compliance report.

| Version | Date | Change |
|---|---|---|
| 0.131 | 2026-10-07 | Owner answers: DEC-498 (W1-30's second review is its last, only fail-open holes and silent closes in ordinary shapes are fixed after it, a hole one fix does not close goes to the owner; every FULL ticket is probed before its merge; W1-30's late probe recorded as a deviation). Next free id: DEC-499. |

## 132. One delegated decision on W1-39: a missing lock in an installed project, and three smaller points (register v0.132, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-499 — W1-39: an installed project without its lock is a failure, not "unmeasured"; each Copier message states the whole procedure; a fresh project is at MINIMAL; the lock task's command is settled with W1-41
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-39 lead's packages P-A to P-D of its second return (`log/W1-39-lead-run2.json`), each with its recommendation · **Refines:** DEC-488, DEC-493
- **Decision:**
  - **P-C, a missing lock.** Where the project's Copier answers file exists and `governance/framework.lock` does not, the comparison answers that the lock is missing from an installed project, and `gov doctor` reports that part as failed and exits non-zero. Where neither file exists (a project that was never installed from the template, as this repository before adoption) the part stays "unmeasured", as W1-27's cases hold. Reason: as built, deleting the lock silences drift detection with exit code 0, and W1-41 and the exit run rely on doctor's exit code. A case first, then the fix, inside `src/gov/lock/` where possible. That a project can delete both files, or edit the lock's manifest together with a kernel file, is not closed here: the lock is not signed before Wave 3 (CAP-02.c), and both are residuals.
  - **P-A.** The message after a copy and the message after an update each state all four steps of the procedure, as built.
  - **P-B.** A fresh project is at MINIMAL with a path map of namespaces only, as built. That this map is not valid against the kernel's path-map schema (which requires 22 systems) is a residual for W1-41's adoption; nothing here changes how doctor derives the level.
  - **P-D.** The lock task stays `python3 -m gov.lock` in this ticket. A `gov lock` subcommand, needed where `gov` is installed as an isolated tool, is decided with W1-41, which fixes the real install path; residual until then.
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.132 | 2026-10-07 | One delegated decision on W1-39: DEC-499 (an installed project without its lock fails in `gov doctor`; each Copier message states the whole procedure; a fresh project is at MINIMAL; the lock task's command is settled with W1-41). Next free id: DEC-500. |

## 133. The orchestrator's judgement of W1-30's second and last review (register v0.133, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-500 — W1-30: of the last review's sixteen findings, six behaviours are fixed in one round, the rest are residuals, and one fail-open that this round cannot close goes to the owner
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the second reviewer's return on `gov close` at `b59d7244` (`log/W1-30-probe2.json`, reviewer session `35e6015b-375b-4173-87df-7d5abfc1e07b`, sixteen findings, each reproduced in projects built in its temporary folder; the collection of every finding into one refusal and the ticket-tool lookup did not fail open in anything it tried) · **Under:** DEC-498 (only fail-open holes, and silent closes in shapes that ordinary work produces, are fixed) · **Refines:** DEC-487, DEC-490
- **Decision — fixed, a case first, in one round:**
  - **Every probe record of the ticket is read (finding 3).** A record that says the probe of the final code failed refuses the close, whatever another record says; a close needs a passing record of the final code and no failing one. Ordinary shape: a ticket with two reviews has two records.
  - **A `Task:` that names no ticket of the project names no task (finding 1).** Such a commit is judged as a commit without a task is (DEC-490): where it changes the ticket's work it refuses the close, and where it changes a governance file the checks run. Ordinary shape: a mistyped id, and this project's own commits whose `Task:` names a kind of record and not a ticket.
  - **The git that `gov close` asks is not the caller's to bend (findings 6 and 8).** An untracked file that is ignored only by a rule outside the commit (the repository's private exclude file, an excludes file named by configuration or by the caller's environment) makes the tree not its commit. Replacement refs are not followed, and configuration passed in the caller's environment does not reach the git calls.
  - **The test runs take no interpreter switches from the caller's environment (finding 7):** a variable that changes how Python runs the tests (for one, the switch that removes assertions) does not reach them.
  - **Skipped tests are counted in the close record (finding 13),** for the acceptance run and the regression run, beside passed, failed and errors. They refuse nothing: a skip is ordinary, and it is no longer silent.
- **Decision — to the owner, not fixed in this round:** a file that the commit's own ignore rules ignore (a build product, a local file) is in the tree the tests run in and not in the commit, so it can decide a test's result (the ordinary form of finding 6). Closing it means running the tests in a clean checkout of the commit, which one fix does not do. Under DEC-498 it comes to the owner as a package.
- **Decision — residuals (in `bootstrap.md`, each with its finding number):** a trailer-less commit that adds a test configuration file outside the ticket's folder (2: a gap in DEC-490's own rule, deliberate shape); the range when commit dates disagree with ancestry (4); the orchestrator's role on the probe record is a self-written trailer, the guard's matter (5); any later owner decision lifts an escalation, and removing both state files resets it (9, 10); the close record lists no skills in a project with an installed kernel (11, for W1-41's adoption); an interruption while the ticket tool closes leaves the two records, and the next close refuses for them (12); template kernel folders outside the six prefixes do not run the checks (14); a ticket argument that is a path (15); a refused close's own compiled files in a project that does not ignore them (16); a record of an earlier round refuses beside a passing one, so the orchestrator keeps only the record of the final code (3, other side).
- Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.133 | 2026-10-07 | The orchestrator's judgement of W1-30's last review: DEC-500 (fixed in one round: every probe record read, a `Task:` naming no ticket, git not bent by the caller, no interpreter switches from the caller, skips counted; to the owner: files ignored by the commit's own rules; the rest residuals). Next free id: DEC-501. |

## 134. One delegated decision on W1-31: the log forms a second specimen shows, and the smaller fields (register v0.134, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-501 — W1-31: hook runs of every event and `gov` commands in every plain form are counted from a second specimen; where a form allows two readings the counter takes the larger; the estimate's formula is the owner's
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-31 lead's packages P-2 to P-7 of its second return (`log/W1-31-lead-run2.json`); a second specimen made by the orchestrator as DEC-495 prescribes (one short headless session in a throwaway project in `/tmp`, Claude Code 2.1.288, with hooks on six events, one that blocks and one that fails, four forms of a `gov` command, one sub-agent and one compaction; its reduced copy is `specimen/session-specimen-2.jsonl` with the sub-agent's log, the settings, the hook script and the prompt beside it). The lead's P-1 (what the estimated part stands on) defines a figure the exit is judged by: it is with the owner and is not decided here · **Refines:** DEC-491, DEC-495
- **Decision:**
  - **Hook runs (P-2).** As the second specimen shows them: a successful run of any event without a following added-context line added nothing and counts 0 (Stop and SubagentStop in the specimen); added context of PreToolUse counts as hook output like PostToolUse's; SessionStart's added context counts again each time it is given (after a compaction too); the text of a hook that blocks a tool call reaches the session as that call's error result and counts as hook output; the text of a hook that fails without blocking is counted as hook output too (whether it reaches the model is not shown: the larger reading is taken, and the record says so). A PreCompact hook left no line in the specimen: its output cannot be counted and the record names that as a known gap. Any hook line of a form neither specimen shows still makes hook output "not measured", by name.
  - **Sub-agents.** A sub-agent's lines are in a file of their own under the session's folder (the specimen shows where). They belong to the named session: their hook lines and `gov` results are counted with it. Whether the token cross-check with ccusage covers those files is established by the lead from the tool's own behaviour, or returned.
  - **`gov` commands (P-3).** A result marked as an error is counted like any other (every refusal of `gov` is one). A command in which `gov` runs beside other commands, through a pipe or with a redirection has its whole result counted, and the record says that such results were counted whole: it over-counts, the safe side for a ceiling. How a command "runs `gov`" is told is the test designer's to settle from how this project and an installed project call it. `gov` inside `bash -c`, `eval`, backticks or a wrapper script stays a residual.
  - **The harness's own totals (P-4).** Tokens come from the assistant lines, cross-checked with ccusage, as built. The harness's summed figures are not used for tokens: they include calls the log does not show as assistant lines, so the denominator is slightly low and the share reads slightly high. Residual; W1-42 reports the difference once.
  - **Smaller fields (P-5).** Latency is the harness's summed API duration from the session's last totals line, named as such. The agent is the harness and its version. Provider and files read stay "not measured".
  - **The sandbox measurement's record (P-6)** is placed and formed by W1-42 when it makes the measurement; "not measured" until then.
  - **The KPI disputes record (P-7)** is `docs/close/<ticket>/kpi-disputes.txt` as built: one line per dispute beginning with the decision that settled it, an empty file for none. The orchestrator writes it at the merge; for a FULL ticket before the probe.
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.134 | 2026-10-07 | One delegated decision on W1-31: DEC-501 (hook runs of every event and `gov` commands in every plain form counted from a second specimen, the larger reading where two are possible; sub-agent logs belong to the session; the smaller fields; the disputes record's place). Next free id: DEC-502. |

## 135. One delegated decision on W1-31: the forms a third specimen shows, and one correction of DEC-501 (register v0.135, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-502 — W1-31: the remaining log forms are counted from a third specimen; DEC-501's sentence on the PreCompact hook was wrong and is corrected; W1-31 merges as built and these points follow on its branch
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-31 lead's packages P-1 to P-5 of its third return (`log/W1-31-lead-run3-return.json`); a third specimen made by the orchestrator as DEC-495 prescribes (throwaway project in `/tmp`, Claude Code 2.1.288: a SessionStart hook that prints plain text and one that fails, a hook that denies a call by its answer, a call denied by a permission rule, a hook of the event after a failed tool call, a Stop and a SubagentStop hook that each block once, a `gov` called by a path, an over-long tool output, one sub-agent; reduced copies `specimen/session-specimen-3*.jsonl` with settings, hook script and prompt) · **Corrects:** DEC-501 (one sentence) · **Refines:** DEC-495, DEC-501
- **Correction.** DEC-501 says a PreCompact hook "left no line in the specimen". That was the orchestrator's misreading: after the manual compaction the second specimen holds the hook's text inside a line that records the compaction command's output, not in a hook line. The lead found it.
- **Decision:**
  - **PreCompact (the lead's P-1).** Its output stays a named gap of the record, with the reason corrected to "in no hook line". The template registers no hook for that event. An automatic compaction is shown by no specimen.
  - **`gov` by a path or by the interpreter (P-2).** A command word whose last path component is `gov`, and a Python interpreter run with the module `gov.cli.main`, run `gov` and are counted. `gov` through another runner stays "not measured" by name.
  - **A SessionStart hook that fails (P-3)** is counted as hook output by the larger reading, as DEC-501 says for a failing hook of any event.
  - **A SessionStart hook that prints plain text (P-4).** The third specimen shows its run line with the text and no added-context line. The harness gives a SessionStart hook's plain output to the session, so that text is counted as the packet, the record saying the larger reading was taken. For every other event a successful run with plain output and no added-context line counts 0, as DEC-501 says; the lead's stricter branch is replaced by these two rules.
  - **What else a session's folder holds (P-5).** A `tool-results` folder beside `subagents` is passed over by name: the third specimen shows it holds the full text of an over-long tool output, while the log's result line holds a shortened form with a preview. The result is counted as logged (what reached the session). Any other content of the folder still refuses the session.
  - **Further forms the third specimen shows.** A hook that denies a call by its answer appears as the call's error result with the hook's reason, like a hook that blocks: hook output. A call denied by a permission rule is no hook's and no `gov` output: it counts nothing. A Stop or SubagentStop hook that blocks appears as a line of feedback given to the session: hook output. Added context of the event after a failed tool call is counted like any event's.
  - **Order of work.** W1-31 is green as built, and what it does not know it reports as "not measured" by name: it merges now, so that W1-32 and the W1-30 follow-up can start. The points above are built as a follow-up on its branch (a test designer first), together with the owner's answer on the estimate when it is given; the ticket closes after that follow-up.
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.135 | 2026-10-07 | One delegated decision on W1-31: DEC-502 (forms of a third specimen counted; DEC-501's sentence on the PreCompact hook corrected; `gov` by a path or the interpreter counted; W1-31 merges as built, the points follow on its branch). Next free id: DEC-503. |

## 136. Owner answers: W1-30's leftovers and its close, the probe gate against the probe's order, W1-39's doctor message, the estimate, the held-out file in the guard, the runner's tools (register v0.136, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-503 — W1-30: files that the project's own ignore rules hide are a residual
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on package P-10 option (a) · **Refines:** DEC-500
- **Decision:** That a file ignored by the commit's own ignore rules is in the tree the tests run in, and not in the commit, is a residual. "Tests run in a clean checkout of the commit" goes on the Wave 2 list.

### DEC-504 — W1-30: the three points the last fix closed in part are residuals; W1-30 closes
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on package P-13 option (a) · **Under:** DEC-498
- **Decision:** Recorded as residuals: git calls made by other modules still inherit the caller's git variables and replacement refs; git configuration still reaches every call; `PYTHONUSERBASE` stays. Then W1-30 closes.

### DEC-505 — A probe refusal caused only by the orchestrator's merge and residual commits, or by a fix round the owner ordered, counts with the adoption gaps; the probe gate is changed in the planned W1-30 follow-up
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on package P-14 option (a) · **Refines:** DEC-492, DEC-498 · **Under:** DEC-137
- **Decision:**
  - Until the tool is changed, a `PROBE_INVALID` refusal whose only later commits are the orchestrator's merge and residual commits, or a fix round the owner ordered, counts with the DEC-492 adoption gaps: the ticket closes with `tk close` and is listed for the exit auditor.
  - W1-30's probe record names `b59d7244` as the probed commit, truthfully.
  - The probe gate is changed in the planned W1-30 follow-up (the one that adds the counter call, DEC-495), so that a merge bringing exactly the probed code no longer counts as "after" the probed commit.

### DEC-506 — W1-39: the doctor message change is accepted; W1-39 merges
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on package P-11 option (a) · **Refines:** DEC-493
- **Decision:** The change to `gov doctor`'s failure message in `src/gov/doctor/command.py` (every failed part named with its reason), which goes beyond "the lock-comparison call only", is accepted. W1-39 merges.

### DEC-507 — W1-31: what the estimated part of the governance share stands on
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on package P-12 option (a) · **Refines:** DEC-495
- **Decision:** Per session: the session role's file under `.claude/agents/`, plus `CLAUDE.md` and `AGENTS.md` where they exist. MCP counts 0, because the Governance OS defines no MCP server.

### DEC-508 — The held-out file: the brief rule is confirmed, and the guard refuses any agent tool call whose targets include it
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on the incident in W1-31's second run (a test designer's search with a glob over the folder that holds the held-out file) · **Under:** DEC-108
- **Decision:**
  - The orchestrator's brief rule is confirmed: no worker runs a glob, a search or a listing over `governance/project/`; files there are named one by one.
  - Delegated to the orchestrator, stricter-only: the guard refuses any agent tool call whose expanded file targets (globs included, DEC-108) include the project's held-out file under `governance/project/` (the owner's answer names its path). The orchestrator chooses the ticket.

### DEC-509 — DEC-499 to DEC-502 are accepted
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER · **Ratifies:** DEC-499, DEC-500, DEC-501, DEC-502
- **Decision:** DEC-499, DEC-500, DEC-501 and DEC-502 stand as written, including the orchestrator's correction to DEC-501.

### DEC-510 — Exit package: the tools the CI runner still needs, each as an install for the owner to approve
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER · **Under:** DEC-083, DEC-494
- **Decision:** The exit package lists which tools the hosted runner still needs for this repository's CI to go green (pytest, openspec, rulesync, as the W1-40 residual says), each as an install for the owner to approve, with its version and checksum.

| Version | Date | Change |
|---|---|---|
| 0.136 | 2026-10-07 | Owner answers: DEC-503 (ignored files a residual), DEC-504 (three partly closed points residuals; W1-30 closes), DEC-505 (a probe refusal from the orchestrator's merge and residual commits or an owner-ordered fix round counts with the adoption gaps; the gate changes in the W1-30 follow-up), DEC-506 (W1-39's doctor message accepted), DEC-507 (the estimate's basis), DEC-508 (the guard refuses tool calls whose targets include the held-out file), DEC-509 (DEC-499 to DEC-502 accepted), DEC-510 (the runner's tools in the exit package). Next free id: DEC-511. |

## 137. Owner answer: what else counts as an adoption gap at a close, when every such exception ends, and real checkpoints (register v0.137, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-511 — Four more adoption gaps until W1-41; every adoption-gap exception ends when W1-41 is merged; W1-42 shows one clean `gov close`; leads write real checkpoints
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-15 option (a) with three guards. `gov close DAEO-2lwj`, run once with the fixed tool, reported 55 findings in seven classes (`log/close-W1-30b.json`); four things among them are not on DEC-492's list. · **Refines:** DEC-476, DEC-492, DEC-505
- **Decision:**
  - **Until W1-41, these also count as adoption gaps:**
    - a missing checkpoint record;
    - a context that fails only because a source outside the repository (such as `S0a-G-12`) is not in the store;
    - the orchestrator's merge commits without `Implements:` made before DEC-492 was recorded (2026-10-07 19:46);
    - the two history commits `7674efde` and `478a8ed0`, as recorded history.
  - **Repair tickets** made by such refusals are not committed; their text is kept beside the close output.
  - **W1-30** closes with `tk close` and is listed for the exit auditor. Then `gov close` is run once each on W1-38, W1-39 and W1-40 under the same rule.
  - **Expiry.** Every adoption-gap exception (DEC-492, DEC-505 and this decision) ends when W1-41 is merged. From then on a ticket closes only through a clean `gov close`. W1-41's and W1-42's KPI lines say so.
  - **Proof at the exit.** W1-42's exit run includes at least one real ticket closed by a clean `gov close`, with no exception, showing the gate works end to end. W1-42 gains that KPI line.
  - **Real checkpoints, not closing ones.** From now on every lead runs `gov checkpoint` at each round boundary of its ticket, so that W1-32 and W1-41 have genuine checkpoint records when they close. No checkpoint is written at the close only to pass the gate.
  - **Sources.** W1-41 brings sources such as `S0a-G-12` into the store, or records them as external references the context accepts.

| Version | Date | Change |
|---|---|---|
| 0.137 | 2026-10-08 | Owner answer: DEC-511 (a missing checkpoint, a context failing for a source outside the repository, the orchestrator's merge commits before DEC-492 without `Implements:` and two history commits count as adoption gaps until W1-41; every such exception ends at W1-41's merge; W1-42 shows one clean `gov close`; leads run `gov checkpoint` at each round boundary; W1-41 brings outside sources into the store). Next free id: DEC-512. |

## 138. One delegated decision on W1-31: the packages of its follow-up, and a second correction of DEC-502 (register v0.138, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-512 — W1-31: the follow-up's packages A to G; DEC-502's sentence on the template's PreCompact hook is corrected; W1-31 merges and closes at `35904984`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-08; told to the owner, who may replace it) · **Basis:** the W1-31 lead's fourth return (`log/W1-31-lead-run4.json`: suite of 131 cases green at `35904984`; packages A to F from the test designer, G from the lead) · **Corrects:** DEC-502 (one sentence) · **Refines:** DEC-502, DEC-507
- **Correction.** DEC-502 says "The template registers no hook for that event" (PreCompact). That is wrong: this repository's settings register a PreCompact hook that runs the template's `precompact.py` (the lead read the registered hook events). The decision itself stands: the hook's output is in no hook line of the log and stays a named gap of the record.
- **Decision:**
  - **A. Interpreter words.** DEC-502 says "a Python interpreter": a command word whose last path component is `python`, `python3` or `python3.<n>`, run with the module `gov.cli.main`, runs `gov`. As built only `python3` is counted and the others are "not measured" by name, which is the safe side. The wider form is built with the next change of the counter (below), not now.
  - **B. A SessionStart with plain text and an added-context line at the same start** stays "not measured" until a specimen shows it.
  - **C. The larger-reading note** also counts a hook's denial by its answer and the Stop and SubagentStop feedback lines, as built.
  - **D. The plain SessionStart text** is counted from the run line's `content`, as built.
  - **E. A permission rule's denial of a tool other than Bash** stays "not measured" until a specimen shows its sentence.
  - **F. A sub-agent's own instruction files** are not in the estimate; the record names that as a known gap, as built. DEC-507 speaks of sessions; whether the estimate should grow by the agent-type file per sub-agent is for the owner if the exit run shows sub-agents matter.
  - **G. A user line whose content is a list holding anything but tool results** keeps the three log sources "not measured", as built.
  - **What follows, and when.** A, B, E and G are forms no specimen shows. Before W1-42's exit run the orchestrator makes a fourth specimen (a denied Write, a prompt logged as a list, two SessionStart hooks of different forms, an interpreter called by a path) and, only if the exit run's real sessions would otherwise be "not measured" for one of these forms, one more change of the counter is built from it, a test designer first. Until then each of these forms is "not measured" by name and never a figure.
  - **W1-31 merges at `35904984` and closes.** Its residual list is the lead's (runs 2 to 4).
  - Recorded before the merge (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.138 | 2026-10-08 | One delegated decision on W1-31: DEC-512 (the follow-up's packages A to G; DEC-502's sentence on the template's PreCompact hook corrected; a fourth specimen before the exit run; W1-31 merges and closes at `35904984`). Next free id: DEC-513. |

## 139. Owner decisions on test run time: no double runs, a measuring agent, and the bar for parallel runs (register v0.139, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-513 — No double runs: a `gov close` that directly follows its ticket's merge counts as the post-merge regression
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Refines:** the orchestrator's practice of a full regression after every merge
- **Decision:**
  - When a merge is followed directly by its ticket's `gov close` on the same merge commit, the `gov close` run counts as the post-merge regression; no separate regression is run for it.
  - A separate full regression is needed only after a merge that is not followed directly by a close.
  - Each run's output is saved, as now.

### DEC-514 — A measuring agent profiles `gov close` and trials parallel test runs (an experiment under DEC-102); pytest-xdist is installed for it
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Under:** DEC-102, DEC-083, DEC-372
- **Decision:**
  - A fresh worker session, in its own worktree cut from `w1/integrate`, writes only its report under `.gov-runtime/scratch/perf/` and never commits. The orchestrator chooses its role and ticket within the launcher's rules (attaching it to W1-30 is acceptable) and tells the owner which it chose. It runs alongside the other work, within the resource gate.
  - **(a) Profile of today's `gov close`:** run once on a closed ticket's state in that worktree; reported are the time per phase (store rebuild, each suite, `gov check`, containment, the other gates) and the 20 slowest test cases.
  - **(b) Trial of parallel runs:**
    - pytest-xdist, pinned to its current release, is installed into the user site of `/usr/bin/python3`, as was done for sqlite-vec (an install under DEC-083: the guard's ask is the owner's approval), and recorded in the tool registry with its version and checksum;
    - the unit tests and the largest suites (W1-02, W1-47, W1-50, and whichever the profile shows as slowest) are timed serially and with `pytest -n auto`;
    - the latency and live-session cases are run separately and serially in both arms, because they fail under load (DEC-372);
    - reported are the time in each arm, any case that fails only in parallel (and why: a shared path, port, file or daemon), and the machine load.

### DEC-515 — The bar for parallel runs: three times faster with no failure the tests cannot fix; then one package for a W1-30 follow-up, else serial
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Under:** DEC-514
- **Decision:**
  - If the parallel arm is at least 3 times faster, with no new failures that cannot be fixed in the tests themselves, the orchestrator brings the owner one package proposing a W1-30 follow-up:
    - `gov close`'s test runner and the regression script run suites in parallel, with the latency and live-session cases run alone afterwards;
    - any test that collides in parallel is fixed by the test designer, with its own temporary paths;
    - built the normal way: test designer, engineer, the reviewer probe before the merge;
    - the plan stays at 50 tickets.
  - If the trial does not meet that bar, the result is recorded and the runs stay serial.

| Version | Date | Change |
|---|---|---|
| 0.139 | 2026-10-08 | Owner decisions on test run time: DEC-513 (a `gov close` directly after its ticket's merge counts as the post-merge regression), DEC-514 (a measuring agent profiles `gov close` and trials parallel runs; pytest-xdist installed and registered), DEC-515 (the bar: three times faster with no failure the tests cannot fix, then a package for a W1-30 follow-up; else serial). Next free id: DEC-516. |

## 140. One reading by the orchestrator: the trailers check's count grows with each close (register v0.140, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-516 — `product-traceability-trailers`: findings that a close adds for the closed ticket's own commits, of the two kinds the baseline already holds, count with the baseline until W1-41
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-08; told to the owner, who may replace it) · **Basis:** `gov close` on W1-38, W1-39 and W1-40 at `2f31bef2` (`log/close-W1-38b.json`, `log/close-W1-39.json`, `log/close-W1-40.json`) reports the check red with 814 findings where DEC-482 records 735. The 79 new findings are all about commits of W1-30, which was closed between the two measurements: 57 `IMPLEMENTS_UNRESOLVED` (capability ids such as `CAP-38.f`, which resolve to no record until adoption) and 22 `MISSING_IMPLEMENTS_TRAILER` (commits made before DEC-476). The check judges the commits of closed tickets, so its count rises with every close. · **Refines:** DEC-482 · **Under:** DEC-492, DEC-511
- **Decision:**
  - Until W1-41 is merged, findings of this check that are about the commits of a ticket closed since the last measurement, and are of those two kinds (a capability id that resolves to no record; a commit before DEC-476 without `Implements:`), count with the baseline of DEC-482. Any other new finding of the check blocks, as before.
  - The orchestrator's comparison before a merge and at a close therefore reads the check's findings by kind and ticket, not by the count alone, and each saved output shows the count at that time.
  - This ends with the other adoption-gap exceptions when W1-41 is merged (DEC-511).

| Version | Date | Change |
|---|---|---|
| 0.140 | 2026-10-08 | One reading by the orchestrator: DEC-516 (the trailers check's findings for a newly closed ticket's own commits, of the two kinds the baseline holds, count with the baseline until W1-41; 814 at `2f31bef2` against 735). Next free id: DEC-517. |

## 141. One delegated decision on W1-41: the adoption tool's input, records and import (register v0.141, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-517 — W1-41: who supplies the path map's actions, who runs the move cases, the A8 import, moves out of a native layout, rewrites, the interface; the stricter readings stand until the owner answers the rest
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-08; told to the owner, who may replace it) · **Basis:** the W1-41 lead's first return (`log/W1-41-lead-run1.json`: 104 cases at `74500e1f`, red because the command is not built; the test designer's packages P-1 to P-9, the lead's L-1 to L-3). L-1, L-2, L-3, P-4, P-5 and P-8 are with the owner. · **Under:** DEC-006, DEC-090, DEC-449, DEC-454
- **Decision:**
  - **P-1. A3's actions, targets and batches come from a proposal file the caller supplies.** An artefact the proposal does not name is kept where it is. The tool proposes nothing itself in Wave 1: no readable source says how it would.
  - **P-2. The move cases are run by the ticket lead outside the sandbox** (a launched session cannot build the code index: its index folder is read-only there). The engineer runs every case its sandbox allows and names the rest; the lead runs the whole suite and reports both. The launcher is not changed, and code intelligence is not turned off in the fixtures.
  - **P-3. The A8 import.** `rulesync import`, run by the tool in the project being adopted, is used for what it imports correctly (measured with 24.0.0: `.cursor/rules/*.mdc`). The tool itself imports what rulesync does not or does not split: `.cursorrules`, `.windsurfrules`, `.mcp/tools.json`, and the role sections of `AGENTS.md` one by one. The cases hold what lies under `.rulesync/` afterwards. No rulesync command is run in this repository or a worktree of it: only in a case's own temporary project.
  - **P-6. A move out of a healthy native layout (CAP-44.j):** the proposal states both grounds (the target is materially better; the migration risk is justified) or the stage refuses; the A5 auditor judges them. The tool scores nothing.
  - **P-7. Rewrites of importers and references:** the tool flags, it does not rewrite, in Wave 1. A move batch changes no file content; each importer, reference and consumer is marked `rewrite` or `flag` in the plan.
  - **P-9. The interface as the cases hold it is accepted:** `gov adopt --lite --stage <A0|A1|A2|A3|A4|A5|A6|A8> [--map <file>] [--verdict <path>]`, one stage per call; each stage commits its evidence record and refuses without the previous stage's; the A5 verdict is a committed record with the hash of the A3 record and an auditor session other than the adopting one, checked again at A6; each A6 batch is one commit with its rollback ref; an unknown artefact is a tracked path no namespace of the project's path map holds; `gov adopt` without `--lite` stays reserved.
  - **Until the owner answers P-4, P-5 and P-8, the stricter reading is built, as the cases hold it:** a chat database is retired only when a committed record cites it by path and current hash (the caller extracts its knowledge); one unknown artefact blocks all of A6 and A8; nothing is moved where the project's path map turns code intelligence off (a case is added for this one). Each is a refusal that an owner answer can only loosen.
  - **L-1 (outside sources) is not built yet:** it needs paths this ticket does not have, which is the owner's to give.
  - Recorded before the engineer starts (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.141 | 2026-10-08 | One delegated decision on W1-41: DEC-517 (a caller's proposal file for A3; the lead runs the move cases outside the sandbox; the A8 import by `rulesync import` plus the tool's own; both grounds for a move out of a native layout; flag, not rewrite; the interface accepted; stricter readings until the owner answers). Next free id: DEC-518. |

## 142. Owner answers: the regression after every merge again, W1-40 and W1-31 close, W1-41's paths and follow-up, when the close exceptions end, the guard against two files (register v0.142, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-518 — DEC-513 amended: a full regression runs after every merge into `w1/integrate`
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER. DEC-513's premise was wrong: `gov close` runs only the ticket's own acceptance suite. · **Amends:** DEC-513
- **Decision:**
  - A full regression runs after every merge into `w1/integrate`, as before DEC-513. One is run now at the current head, since W1-31 was merged without one.
  - If the parallel trial passes (DEC-515), the W1-30 follow-up makes `gov close`'s regression step run every suite, in parallel; then the separate regression is dropped.

### DEC-519 — Package P-16: commit `7c6bf804` is recorded history; a register decision that is not yet a store record is an adoption gap; W1-40 and W1-31 close
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-16 option (a) (`log/close-W1-40.json`, `log/close-W1-31.json`) · **Refines:** DEC-511
- **Decision:**
  - `7c6bf804` (the orchestrator's commit "Start W1-31, W1-40 and W1-39", whose `Task:` names no ticket) counts as recorded history.
  - A decision that is in the register but not yet a store record (such as DEC-086) counts as an adoption gap, like a source outside the repository.
  - W1-40 and W1-31 close with `tk close`, after the full regression of DEC-518 is green, and both are listed for the exit auditor.

### DEC-520 — Package P-17.1: W1-41's paths gain the context code and one file of external references
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-17 point 1 option (a) · **Under:** DEC-511
- **Decision:** W1-41's `allowed_paths` gain `src/gov/context/**`, `tests/unit/context/**` and one file under `governance/project/` that lists external references. The context accepts a listed id and reports it as external, never as content.

### DEC-521 — Package P-17.2: one short follow-up after W1-41; capability records for this repository are agent work
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-17 point 2 · **Under:** DEC-482, DEC-483, DEC-473
- **Decision:**
  - One short follow-up builds: the trailers base commit (DEC-482); the owner-decision lookup from a register file (DEC-483); the close record's skills list in a project with an installed kernel; the declared check commands that name `template/` paths; and, added by the owner, that the record store loads decisions from the project's named register file (DEC-473) as decision records, one per heading.
  - Creating capability records for this repository from `contract.yaml` is agent work after W1-41 merges, not an owner step.
  - The owner's exit package holds only owner actions.

### DEC-522 — Package P-17.3: the close exceptions end when this repository's adoption is complete, not at W1-41's merge
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-17 point 3 · **Amends:** DEC-511 (its expiry)
- **Decision:**
  - The expiry of every adoption-gap exception (DEC-492, DEC-505, DEC-511, DEC-516, DEC-519) moves from "W1-41's merge" to "this repository's adoption is complete".
  - **Adoption complete** means: `gov adopt --lite` run on this repository, the `gov check` baseline empty, and capability records present. It is a defined step after W1-41's merge and before W1-42.
  - W1-41 itself closes under the exceptions.
  - From adoption on, every ticket closes only through a clean `gov close`, and W1-42 proves it on a real ticket.
  - The KPI lines of W1-41 and W1-42 are brought to this.

### DEC-523 — Package P-17.4 to P-17.6: the adoption tool's three stricter readings stand as built
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-17 points 4, 5 and 6 · **Ratifies:** the interim readings of DEC-517
- **Decision:** As built: a chat database is retired only when a committed record cites it by path and current hash (the caller extracts its knowledge); one unknown artefact blocks all of A6 and A8; nothing is moved where the project's path map turns code intelligence off.

### DEC-524 — DEC-512 and DEC-516 are accepted; the measuring agent's role and ticket are accepted
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Ratifies:** DEC-512, DEC-516
- **Decision:** DEC-512 and DEC-516 stand as written. The measuring agent of DEC-514 as an independent auditor on W1-31 is accepted.

### DEC-525 — The guard refuses any agent tool call that reads the Claude Code settings file or the held-out file, for every role
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on the incident in W1-31's fourth run (a lead loaded `.claude/settings.json` in a script to list hook events) · **Extends:** DEC-508 · **Under:** DEC-108
- **Decision:**
  - Delegated to the orchestrator, stricter-only: the guard refuses any agent tool call that reads `.claude/settings.json` or the project's held-out file under `governance/project/` (the owner's answer names its path), for every role, the orchestrator included.
  - For hook listings, a small helper prints only the hook events, with the deny lines redacted.
  - The orchestrator chooses the ticket.

| Version | Date | Change |
|---|---|---|
| 0.142 | 2026-10-08 | Owner answers: DEC-518 (a full regression after every merge again; DEC-513 amended), DEC-519 (`7c6bf804` recorded history; a register decision not yet a store record is an adoption gap; W1-40 and W1-31 close), DEC-520 (W1-41's paths gain the context code and an external-references file), DEC-521 (one follow-up after W1-41, with register decisions loaded as records; capability records are agent work), DEC-522 (the close exceptions end when this repository's adoption is complete), DEC-523 (three stricter readings of the adoption tool stand), DEC-524 (DEC-512, DEC-516 and the measuring agent's role accepted), DEC-525 (the guard refuses reads of the settings file and the held-out file for every role; a helper lists hook events). Next free id: DEC-526. |

## 143. Delegated: W1-32 merges as built while its six packages are with the owner (register v0.143, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-526 — W1-32 (`gov status`, the launcher's two residuals) merges as built; its open questions are with the owner and the ticket stays open until they are answered
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-08; interim until the owner answers package P-19) · **Basis:** the lead's return at `ff85c968` (`log/W1-32-lead-run1.json`): 81 cases green, every suite run · **Under:** DEC-392, DEC-449, DEC-491, DEC-518
- **Decision:**
  - The branch `w1/W1-32` is merged into `w1/integrate` as built, after the orchestrator's own runs and `gov check`, and a full regression follows (DEC-518). The merge loosens nothing: `gov status` only reads, and the launcher change only adds the ending of a session on SIGTERM and SIGHUP and keeps the session's exit code.
  - Until the owner answers, these readings hold, each as built:
    - the governance share in `gov status` is asked of the counter for each claimed ticket with no session named, so it reads "not measured" with the counter's reason and never a number (no record names a ticket's sessions, DEC-491);
    - an open gate is an open decision package or a specification with an open required readiness row;
    - a tickets folder or a changes folder that is absent reads as an empty list; one that exists and cannot be listed reads as not read;
    - the three commands found beyond the twelve reserved names (`ci`, `launch`, `telemetry`) are pinned by the suite as found; no command is added.
  - The ticket is **not closed** on this decision: the half of its KPI line that routes a status question asked in natural language to `gov status --json` has no file within the ticket's paths and no case, and whether that half is built by another ticket or recorded as not covered is the owner's (P-19 point 2).
  - A record file the store's load cannot take is shown by `gov status` as not read; that the READY rule still calls a ticket ready when the package constraining it failed to load lies outside this ticket and goes to the owner as a proposal for the follow-up of DEC-521 (P-19 point 5).

| Version | Date | Change |
|---|---|---|
| 0.143 | 2026-10-08 | Delegated: DEC-526 (W1-32 merges as built; four interim readings; the ticket stays open until the owner answers package P-19). Next free id: DEC-527. |

## 144. Owner answers to package P-18: suites run in parallel, built now as a W1-30 follow-up (register v0.144, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-527 — Package P-18: `gov close`'s regression step and the regression script run suites in parallel
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-18 option (a) with the W1-05 addition; the measuring agent's report (DEC-514; `log/PERF-REPORT.md` in the orchestrator's scratch: 6.0 times faster on what ran in parallel, 2.8 times with the serial cases counted on both sides; no failure from a shared path, port, file or daemon) · **Under:** DEC-515, DEC-518, DEC-372
- **Decision:**
  - `gov close`'s regression step and the regression script run suites in parallel (`pytest -n auto`).
  - Inside a full regression, W1-05's switch-over case is satisfied by the regression's own W1-02, W1-03 and W1-04 results, or runs alone last.
  - The latency, real-model and live-session cases run alone afterwards, serially (DEC-372).

### DEC-528 — The parallel run is built now, as its own W1-30 follow-up, alongside W1-41
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Under:** DEC-527, DEC-498
- **Decision:**
  - The follow-up starts now, on W1-30 (`DAEO-2lwj`, reopened for it), in parallel with W1-41. It does not touch W1-41's paths; if it touches the guard's paths, it is sequenced after the W1-02 follow-up (DEC-525).
  - It is built the normal way: test designer, engineer, the reviewer probe before the merge.
  - The plan stays at 50 tickets.

### DEC-529 — The same follow-up repairs the two test defects the trial found
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER; the report's section "Cases that fail only in parallel" · **Under:** DEC-491
- **Decision:**
  - The test designer fixes: the W1-50 test file that imports `gov` without setting its own import path (it fails when run alone serially as well), and the unit case that expects the word "pytest" in its own command line.
  - Both are recorded as rewrites after implementation, with the reason "defect found by the parallel trial".

### DEC-530 — The same follow-up gives `gov rebuild` a mode without embeddings
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER; the report (a rebuild with embeddings did not end in 44 minutes; 161 seconds with the embedding endpoint unreachable) · **Refines:** DEC-477
- **Decision:**
  - `gov rebuild` gets a mode without embeddings, for closes and checks that need only fresh lexical and graph indexes.
  - A full rebuild with embeddings runs before W1-42's retrieval measurements.

### DEC-531 — From its merge on, every regression and every close uses the parallel run
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Under:** DEC-518, DEC-527
- **Decision:**
  - Once the follow-up is merged, every later regression and close uses the parallel run, including this repository's adoption, W1-42 and W1-43.
  - The orchestrator reports the new regression time after the first run.

### DEC-532 — How the orchestrator applies DEC-527 to DEC-530: the ticket's paths and who repairs the unit case
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-08; consequences of the owner's order, nothing loosened) · **Under:** DEC-527, DEC-529, DEC-530, DEC-463
- **Decision:**
  - For this follow-up W1-30's `allowed_paths` gain `src/gov/rebuild/**`, `tests/unit/rebuild/**` and the one unit file `tests/unit/pause/test_pause.py`, beside `src/gov/close/**` and `tests/unit/close/**`. The acceptance cases, and the repair of the W1-50 file, are the test designer's under `tests/acceptance/`.
  - The guard lets a test designer write only under `tests/acceptance/**`. The unit case is therefore repaired by the engineer exactly as the test designer states it in writing, in a commit of its own that carries `Rewrite-Reason: defect found by the parallel trial`; it changes what the case expects of its own command line and nothing else.
  - "The regression script" is the orchestrator's own script in its scratch folder: no regression script is shipped today. The product's parallel run lives in `gov close`; the orchestrator's script is brought to the same form (the same parallel option, the same cases set apart) when the follow-up merges, and is dropped once `gov close`'s regression step covers every suite (DEC-518).
  - No command is added. If the mode without embeddings needs a new argument that a suite pins, the lead returns it as a package.
  - The other planned changes to `gov close` (the counter call of DEC-495, the probe gate of DEC-505, the items of DEC-521) stay with the follow-up after W1-41 and are sequenced after this one, since they share its paths.

| Version | Date | Change |
|---|---|---|
| 0.144 | 2026-10-08 | Owner answers to P-18: DEC-527 (suites in parallel in `gov close`'s regression step and the regression script; W1-05's switch-over case; serial cases alone afterwards), DEC-528 (built now as a W1-30 follow-up beside W1-41), DEC-529 (the two test defects repaired as rewrites), DEC-530 (`gov rebuild` without embeddings), DEC-531 (every later regression and close uses it). Delegated: DEC-532 (paths, the unit case, the regression script). Next free id: DEC-533. |

## 145. A correction of fact about `gov close`'s test runs, and two Wave 2 items (register v0.145, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-533 — Correction: `gov close` does run the regression tests; the orchestrator's report to the owner that it runs only the ticket's own suite was wrong
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-08; a correction of fact, no rule changed) · **Basis:** `src/gov/close/command.py` (after the ticket's acceptance run it runs everything under `tests/` except the ticket's own acceptance folder, in one serial call); the measuring agent's report (DEC-514), which reads the same; the times of the closes of 2026-10-08 (about 80 minutes each) · **Corrects:** the stated basis of DEC-518
- **Decision:**
  - The sentence in DEC-518 "DEC-513's premise was wrong: `gov close` runs only the ticket's own acceptance suite" is itself wrong, and so was the orchestrator's report that led to it. `gov close` runs the ticket's acceptance suite and then the regression (every other suite and the unit tests), serially. DEC-513's premise was right.
  - DEC-518's rule (a full regression after every merge) is the owner's and stands until the owner changes it. Whether a `gov close` on the merge commit again counts as that regression (DEC-513) is put to the owner (package P-20); until the answer, both are run.
  - What DEC-527 changes in `gov close` is therefore the form of its regression run (parallel, with the serial cases alone afterwards), not its coverage.

### DEC-534 — Two items join the Wave 2 list: declared test commands in any language, and test selection by impact
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER; the orchestrator's reading that `gov close` can run only pytest today (the command and the two paths `tests/acceptance/<ticket>/` and `tests/` are fixed in the code; a project cannot declare a test command)
- **Decision:** The Wave 2 list gains:
  - declared, language-agnostic test commands for `gov close` and the regression, each with its own parallel option (for example `cargo test` for Rust, `npm test` or `vitest` for TypeScript);
  - impact-based test selection: run only the tests a change can affect (`gov impact`), with the full suite nightly or in CI, for large repositories.

| Version | Date | Change |
|---|---|---|
| 0.145 | 2026-10-08 | DEC-533 (correction of fact: `gov close` runs the regression tests too; the basis stated in DEC-518 was wrong; its rule stands until the owner answers P-20), DEC-534 (owner: two Wave 2 items, declared test commands in any language and test selection by impact). Next free id: DEC-535. |

## 146. Delegated: two packages of W1-41's second run (register v0.146, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-535 — W1-41: the unit file of the command-module convention joins the ticket's paths; SPLIT, MERGE and EXTRACT are refused where code intelligence is off
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-08; P3, reversible, the lead's recommendation and the orchestrator's agree, nothing loosened) · **Basis:** the lead's return at `b8d97636` (`log/W1-41-lead-run2.json`: 114 cases green, every acceptance suite green, 11 unit tests red in one file outside the ticket's paths) · **Under:** DEC-517, DEC-523
- **Decision:**
  - **U-1.** `tests/unit/launch/test_command_modules.py` joins W1-41's `allowed_paths`. The file plants a stand-in `adopt` module because `adopt` was the last reserved command without one; now that the command is built, the built package is found first and 11 of its cases fail. A fresh engineer repairs the file so that its stand-in is the module the cases load, as W1-46 and W1-28 did for the same file when they built `checkpoint` and `pause`. The cases keep what they hold about the convention; nothing in `src/` is changed for it.
  - **P-10.** In a project whose path map turns code intelligence off, SPLIT, MERGE and EXTRACT are refused at A3 as MOVE and RENAME are (DEC-523: nothing is moved there). The tool does so as built; the test designer adds the rows that hold it.

| Version | Date | Change |
|---|---|---|
| 0.146 | 2026-10-08 | Delegated: DEC-535 (W1-41: one unit file joins the ticket's paths and is repaired by an engineer; SPLIT, MERGE and EXTRACT refused where code intelligence is off). Next free id: DEC-536. |

## 147. Owner answers: a close on the merge commit is the regression again; the way the wave is run goes into the kernel (register v0.147, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-536 — Package P-20: a `gov close` on the merge commit counts as the post-merge regression, from now
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-20 option (b); DEC-533 is noted: `gov close` runs the ticket's suite and then everything under `tests/`, and DEC-513's premise was right · **Amends:** DEC-518 · **Restores:** DEC-513
- **Decision:**
  - A `gov close` on the merge commit counts as the post-merge regression. DEC-518's separate full regression is dropped for merges followed directly by their close.
  - The plan validator is run separately, since it is not under `tests/`.
  - A merge not followed directly by its close still gets a full regression.
  - When the parallel run merges (DEC-527), `gov close` uses it.

### DEC-537 — Package P-21: the way the wave is run is promoted into the kernel by one follow-up on W1-35, before the exit run
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-21 option (a); the orchestrator's report C (most working rules live only in this repository's prompt, briefs and decisions) · **Under:** DEC-534
- **Decision:**
  - One STANDARD follow-up on W1-35, alongside W1-41, with W1-33's role path and the kernel templates folder added to its paths, builds:
    - an orchestration skill (about 150 to 200 lines) holding every "only in prompt or decisions" row of report C, written as text the skill states;
    - the orchestrator role file extended, with the ticket lead as a section of it, not a seventh role;
    - five brief templates (test designer, engineer, reviewer, product-spec worker, lead) under the kernel's templates, including the "behaviour and sources only" rule;
    - a skill-regression check for the new skill.
  - The wording stays language-neutral where tests are named, so that it does not assume pytest (DEC-534).
  - W1-42 runs from the kernel's orchestration skill and briefs, not from this repository's prompt; that KPI line is added to W1-42.
  - The parts that need code go on the Wave 2 list: the resource gate as a command, the launcher refusing a launch without a model, `AUTH_REQUIRED` as a mechanism, and starting leads through the launcher.
  - The generated `.claude/**` output is the owner's to apply at the exit, with the other adapters.

### DEC-538 — DEC-532, DEC-534 and DEC-535 are accepted
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Ratifies:** DEC-532, DEC-534, DEC-535
- **Decision:** DEC-532, DEC-534 and DEC-535 stand as written.

### DEC-539 — How the orchestrator applies DEC-537: the paths W1-35 gains and what the skill may hold
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-08; consequences of the owner's order, nothing loosened) · **Under:** DEC-537, DEC-463
- **Decision:**
  - For this follow-up W1-35 (`DAEO-0i6h`, reopened for it) gains in `allowed_paths`: `template/governance/kernel/skills/orchestration/**`, `template/governance/kernel/roles/orchestrator.md`, `template/governance/kernel/templates/**`, `template/governance/kernel/checks/skill-regression-orchestration*`, and the rulesync sources of the same two things in the template (`template/.rulesync/skills/orchestration/**`, `template/.rulesync/subagents/orchestrator.md`). Nothing under this repository's `.claude/**`, `.rulesync/**`, `CLAUDE.md` or `AGENTS.md` is written by the follow-up.
  - The ticket's own rule holds for the new skill: a skill is a method, grants no permission, and cites the policy or decision it follows; its size bounds are those of the ticket's first KPI line. If every row of report C does not fit within them, the rows are divided between the skill and the brief templates it names, and the lead returns how; no row is dropped.
  - The sources of the text are this repository's orchestrator prompt and its appendix of briefs, the two common lead files of the orchestrator's scratch folder (given to the lead as content), and the decisions named in report C. Rules that are particular to this repository's wave (its ticket ids, its branch names, its workbench folders, its installed versions) are stated in the kernel as a project's own values, not copied.

| Version | Date | Change |
|---|---|---|
| 0.147 | 2026-10-08 | Owner answers: DEC-536 (P-20: a `gov close` on the merge commit is the post-merge regression again; the validator runs separately), DEC-537 (P-21: an orchestration skill, the lead as a section of the orchestrator role, five brief templates and a skill-regression check, as a follow-up on W1-35; W1-42 runs from them; code parts to Wave 2), DEC-538 (DEC-532, DEC-534, DEC-535 accepted). Delegated: DEC-539 (W1-35's added paths; what the skill holds). Next free id: DEC-540. |

## 148. Owner answers to package P-19 (W1-32, `gov status`) (register v0.148, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-540 — P-19.1: `gov status` shows the governance share as "not measured", with the counter's reason
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-19 point 1 option (a) · **Under:** DEC-491
- **Decision:** `gov status` shows the governance share as "not measured", with the counter's reason. Per-session attribution stays on the Wave 2 list (the launch record).

### DEC-541 — P-19.2: the natural-language route to `gov status --json` goes into the W1-35 follow-up; W1-32 closes
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-19 point 2 option (a) · **Under:** DEC-537 · **Supersedes:** the last point of DEC-526 (the ticket stays open)
- **Decision:**
  - The natural-language route to `gov status --json`, with its test, goes into the W1-35 follow-up (the orchestration skill).
  - The provider of that half of CAP-28.a moves to that follow-up: W1-32's KPI line keeps the command-set half, and W1-35 gains a KPI line for the route.
  - W1-32 then closes under the current close rules.

### DEC-542 — P-19.3: `ci`, `launch`, `telemetry` and `lock` are recorded in the command list
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-19 point 3 option (a)
- **Decision:** `ci`, `launch`, `telemetry` and `lock` are recorded in the command list, each with one test-designer line.

### DEC-543 — P-19.4: for W1-32 an open gate is an open decision package or an open required readiness row; the source is read for more kinds
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-19 point 4 option (a)
- **Decision:**
  - For W1-32, option (a): the two kinds as built.
  - In addition the orchestrator reads S0a-G-01 by exact path in the workbench's `s0a/out/` (`STACK_OPTIONS.md` or `BAKEOFF_PLAN.md`, by the bare id G-01), never listing folders there. If the source names more kinds of gate (gate records, audit tickets, check gates), it is brought as a package for Wave 2; otherwise (a) stands.
- **What the reading gave (2026-10-08):** `STACK_OPTIONS.md` names G-01 as "`gov` CLI skeleton, API-0002 JSON envelope + exit codes 0–4; `gov status`; record templates (lesson, failure, gate, research); overlay config for model tiers", for CAP-14, CAP-28, CAP-34 (human decision gates), CAP-35 and CAP-41. It names a `gate` record as a template; it does not say what `gov status` shows, and it names neither audit tickets nor check gates. `BAKEOFF_PLAN.md` does not name G-01. The one further kind, `gate` records in status, is brought to the owner as a Wave 2 proposal (P-22).

### DEC-544 — P-19.5: the READY rule treats a constraining package the store could not load as blocking
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-19 point 5 option (a); stricter-only · **Under:** DEC-521
- **Decision:** In the follow-up after W1-41, the READY rule treats a constraining package the store could not load as blocking.

### DEC-545 — P-19.6: an absent tickets or changes folder reads as an empty list
- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-19 point 6 option (a)
- **Decision:** An absent tickets or changes folder reads as an empty list, as built.

### DEC-546 — How the orchestrator applies DEC-541 and DEC-542
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-08; consequences of the owner's answers, nothing loosened) · **Under:** DEC-541, DEC-542, DEC-463
- **Decision:**
  - W1-32's fifth success line becomes "The command set stays at the Wave 1 list (no command without a contract item) [CAP-28.a]". W1-35 gains the success line "A status question asked in natural language is answered from gov status --json: the orchestration skill states the route, and a case holds it [CAP-28.a]", on the follow-up's branch.
  - The four command-list lines of DEC-542 are written by a test designer in the follow-up after W1-41 (DEC-521), with the list itself; until then W1-32's suite pins `ci`, `launch` and `telemetry` as found.

| Version | Date | Change |
|---|---|---|
| 0.148 | 2026-10-08 | Owner answers to P-19: DEC-540 (governance share "not measured" in status), DEC-541 (the natural-language route goes into the W1-35 follow-up; W1-32 closes), DEC-542 (`ci`, `launch`, `telemetry`, `lock` in the command list), DEC-543 (two kinds of gate for W1-32; what S0a-G-01 says), DEC-544 (READY blocks on a package the store could not load), DEC-545 (an absent folder reads as empty). Delegated: DEC-546 (the two KPI lines; where the command-list lines are written). Next free id: DEC-547. |

## 149. Delegated: how the provider of half of CAP-28.a is moved (register v0.149, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-547 — W1-35 is named as a second provider of CAP-28 and of its item CAP-28.a in the Contract's capability file
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; the form of a change the owner ordered in DEC-541, nothing else in the Contract changed) · **Under:** DEC-541, DEC-546, DEC-463
- **Decision:**
  - The plan validator holds that a ticket's KPI may cite a covers item only when the Contract names that ticket as its provider, and that the provider is also a provider of the capability and has it among its sources. To move the natural-language half of CAP-28.a to the W1-35 follow-up, `docs/contract/contract.yaml` therefore gains `W1-35` in the provider list of CAP-28 and in the provider list of its item CAP-28.a (W1-32 stays, for the command-set half), and W1-35's ticket gains `CAP-28` among its sources.
  - The change is made in its own commit on the follow-up's branch, with the trailer `Task: DAEO-0i6h`, so that the Contract and the ticket's new KPI line arrive on the integration branch together. No scope, wave or wording of the Contract changes.

| Version | Date | Change |
|---|---|---|
| 0.149 | 2026-10-09 | Delegated: DEC-547 (W1-35 named as a second provider of CAP-28 and CAP-28.a, the form of the move ordered in DEC-541). Next free id: DEC-548. |

## 150. Delegated, stricter-only: four packages of the guard follow-up on W1-02 (register v0.150, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-548 — The guard's rule against reads of the settings file and the held-out file: redaction in the helper, second names, copies outside the project, and the refusals beyond the order
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; stricter-only: each point refuses more and blocks none of the owner's own actions; the lead's recommendation and the orchestrator's agree; reversible) · **Basis:** the lead's return at `c95bb271` (`log/W1-02-lead-run1.json`: 447 new cases green, every suite green) · **Under:** DEC-108, DEC-508, DEC-525
- **Decision:**
  - **DP-2.** The hook-listing helper redacts a whole deny value, as built, and also an absolute path that a deny rule carries wherever a hook command holds it bare.
  - **DP-3.** A command that gives either file a second name is refused as a read, for every role: a move or rename of the file, a hard or symbolic link to it, a linking copy, and an in-place edit that leaves a backup copy. A plain write to the file by a role that may write it today stays as it is.
  - **DP-4.** The rule covers the same two files outside the session's own project: any target whose path ends in either file's project-relative path, in another checkout or worktree or anywhere else, and the user-level settings file of the harness. If a suite reads such a copy through a tool call and goes red, the lead returns it by name; nothing is narrowed to make it pass.
  - **DP-5.** The refusals beyond the order stand as built: a shell command that only mentions the settings file's path as text; a shell word that is a folder holding either file or a folder above it inside the project, also in a command that does not read; `git -C <dir> diff --stat <file>`. `git status` and `git diff --stat` with no other option stay allowed on both files. Every session writes "the settings file" in commit messages and command text, not its path.
  - **DP-1 (a search from the project's root with nothing that keeps both files out) is with the owner (P-23).** Until the answer it stays as built: the search tool from the root is allowed, as four suites hold; a glob over everything from the root is refused.

| Version | Date | Change |
|---|---|---|
| 0.150 | 2026-10-09 | Delegated, stricter-only: DEC-548 (the guard follow-up on W1-02: helper redaction, second names refused, copies outside the project covered, the refusals beyond the order stand; the root search is with the owner). Next free id: DEC-549. |

## 151. Delegated: six packages of the parallel-run follow-up on W1-30 (register v0.151, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-549 — The parallel run in `gov close`: W1-27's command bound, the worker count as a project setting, the time limit, a list entry that names no case, and the second W1-50 repair
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, test-side or as built; no ticket closes on fewer tests) · **Basis:** the lead's return at `33a1b1c5` (`log/W1-30-lead-runF1.json`: the four pieces built; two regressions of this repository in the parallel form each red on three or four W1-27 cases whose command did not end within 30 seconds under ten workers) · **Under:** DEC-527, DEC-529, DEC-532, DEC-372
- **Decision:**
  - **P-1.** A test designer gives the `gov rebuild` and `gov doctor` commands of W1-27's cases a longer bound in W1-27's own support (a rewrite with the reason "defect found by the parallel trial": the bound is how long the case waits for the command, not a time the ticket promises). The cases stay parallel. Where a case asserts a time the ticket's KPI names, nothing is changed. If the cases still do not hold under ten workers, declaring them serial-only changes which cases count as serial-only and is the owner's.
  - **P-2.** The number of parallel workers of a `gov close` is a setting of the project, default `auto`; the temporary projects of the suites set it small, so that a close under test does not start ten workers inside a parallel run. The setting changes how many workers run, never which tests run.
  - **P-3.** No code: a close of this repository is given a time limit of 7200 seconds, as the orchestrator has passed it until now; the project's own setting is written at the merge.
  - **P-4.** A list entry that names no case: as built. The run afterwards fails and the close is refused with a finding. (The lead recommended a refusal that is not counted against the ticket; the stricter form already built is kept, and this repository's own case keeps such entries out of its list.)
  - **P-5.** The stray untracked file under the worktree's `tests/acceptance/W1-27/` (a two-line comment, no test, in no commit) is not the orchestrator's to remove (MR-3); it goes with the worktree when the worktree is removed.
  - **P-6.** The second W1-50 repair (`1e2ec82b`, the same missing import path in another file of that suite) stands, with its `Rewrite-Reason:`.

| Version | Date | Change |
|---|---|---|
| 0.151 | 2026-10-09 | Delegated: DEC-549 (the parallel-run follow-up on W1-30: a longer command bound in W1-27's support, the worker count as a project setting, the time limit, a list entry without a case stays a finding, the second W1-50 repair stands). Next free id: DEC-550. |

## 152. Delegated: four packages of the orchestration-skill follow-up on W1-35 (register v0.152, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-550 — The orchestration skill: two known findings of the adapter check until the exit, and three points of wording as built
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, the lead's recommendation and the orchestrator's agree; wording and a known check state, nothing loosened) · **Basis:** the lead's return at `e2797b3b` (`log/W1-35-lead-runF1.json`: 54 new cases, every suite green) · **Under:** DEC-537, DEC-539, DEC-481, DEC-516
- **Decision:**
  - **P-1.** The adapter-portability check at this repository's root gains two findings (a rulesync source of the new skill that this repository does not hold, and the orchestrator subagent source that now differs from the template's), beside the 43 of DEC-481. They are known and of the same cause as the 43: this repository's rulesync sources and generated output are the owner's to apply at the exit (DEC-537). Until then they count with the baseline at a close (DEC-516). They are named in the exit package.
  - **P-2.** A rule that only this repository's orchestrator prompt held is cited in the skill with DEC-537, which ordered it stated there; the skill's opening sentence says so. A decision that states those rules one by one may follow with a later register batch.
  - **P-3.** After the second review of a FULL ticket the skill names fail-open holes and losses of work, with DEC-413's own words (silent changes to tests or ticket files) beside them: both stand.
  - **P-4.** The skill states "confidence medium or higher" as the delegation rule, and the widening to medium-low for a P2 as one an owner may give, as in DEC-416: as built.

| Version | Date | Change |
|---|---|---|
| 0.152 | 2026-10-09 | Delegated: DEC-550 (the orchestration-skill follow-up on W1-35: two known adapter-check findings count with the baseline until the owner applies the output at the exit; three points of wording as built). Next free id: DEC-551. |

## 153. Delegated, stricter-only: three packages of W1-41's third run and the judgement of its probe (register v0.153, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-551 — External references in the context: a defective file blocks every ticket, a register-shaped id is refused by its form, a ticket with only external sources is refused
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, stricter-only: each is the form that refuses more, as built; the lead's recommendation and the orchestrator's agree) · **Basis:** the lead's return at `920229dc` (`log/W1-41-lead-run3.json`: 156 cases green, every acceptance suite green) · **Under:** DEC-511, DEC-520, DEC-449, DEC-454
- **Decision:**
  - **P-11.** A defective `governance/project/external-references.yaml` (unreadable, not valid, wrong shape, a duplicate id) blocks every ticket's context and names the file, not only a ticket that declares an id the store lacks: a defect is seen at once.
  - **P-12.** An entry whose id has the form of a register decision is refused by its form in every project, whether or not the project names a register: a decision is never made an outside source by a list.
  - **P-13.** A ticket whose declared ids are all external references is refused, as a ticket that declares nothing is: no close stands on a context in which nothing was read.
  - The outside sources that closed tickets cite and that are neither records nor listed (the lead's list in its return) are not listed by the orchestrator: which of them become records and which are listed belongs to this repository's adoption step (DEC-522) and is brought to the owner with it.

### DEC-552 — W1-41's reviewer probe: judged pass with one fix round of three behaviours; the rest are residuals
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, stricter-only: each fix refuses more) · **Basis:** the probe's return (`log/W1-41-probe.json`, session `2020c8c7-b490-4464-8b39-64fc3030412a`, at `920229dc`; ten findings, each reproduced; the ticket's four failure lines hold as observed) · **Under:** DEC-498, DEC-137, DEC-454, DEC-520
- **Decision:** One fix round, test designer first, then one engineer; no second probe (DEC-498).
  - **Finding 1 (fails open, ordinary work produces it).** The dependency proof sees a citation of a legacy memory store in a kept rule file when the path stands behind `./`, `/`, `../` or a folder (and an id behind a folder), as it sees the bare path and the bare id. A store so cited is not retired.
  - **Finding 6 (the stricter reading of "active record").** In the dependency proof a record holds a store back unless its status says it no longer stands (superseded, retired, rejected). A record with the status ACCEPTED, PROPOSED or DRAFT counts: the decisions of this repository's own register carry ACCEPTED.
  - **Finding 8 (the gap that P-13 above closes, one step further).** A ticket whose declared sources are all external references is refused whether or not it also names dependency tickets: a dependency that was read is not a source that was read.
  - **Residuals, named in `bootstrap.md`:** findings 2 to 5, 7, 9 and 10 (no record of the completed batches after a failed one, and rollback refs reused by the next round; an interruption inside a batch; a move target in no namespace, refused only at A8; a flat package layout moved without the two grounds; four legacy shapes that cannot be adopted and fail closed; the external list read from the working tree, and repository-held id forms other than a decision's accepted in it; retired and rejected records satisfying a mandatory source). Findings 9 and 10 go to the follow-up after W1-41 with DEC-521's items; finding 4 and the first two shapes of finding 7 are read again before this repository's own adoption.

| Version | Date | Change |
|---|---|---|
| 0.153 | 2026-10-09 | Delegated, stricter-only: DEC-551 and DEC-552 (W1-41's external references: a defective file blocks every context, a register-shaped id is refused by form, an all-external ticket is refused; the unlisted outside sources go to the adoption step; the probe judged pass with one fix round: citations behind a path prefix, records that still stand, all-external sources beside dependencies). Next free id: DEC-553. |

## 154. Delegated, stricter-only: three packages of the guard follow-up's second run on W1-02 (register v0.154, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-553 — The read rule for the two protected files: a wildcard-only glob from a copy's folder, a deny path spelled from the home folder, a move of the holding folder
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, stricter-only: each refuses or redacts more; the lead's recommendation and the orchestrator's agree) · **Basis:** the lead's return at `750d57fb` (`log/W1-02-lead-run2.json`: DEC-548's four points built, 331 new cases, every suite green; a comparison over 420,000 random calls found none that was refused before and is allowed now) · **Under:** DEC-508, DEC-525, DEC-548
- **Decision:**
  - **DP-6: (b).** A glob made of wildcards alone from the folder a copy lies under is refused as the same glob from the session's own root is: the two no longer differ. A glob or search from above that folder whose pattern names the file's own name or path is answered together with DP-1, which is with the owner (P-23); until then it is a residual.
  - **DP-7: (b).** The helper also redacts a deny path that is spelled from the home folder, as written and with the home folder in its place. A project-relative spelling is not redacted (it would blank ordinary relative paths) and stays a residual.
  - **DP-8: (b).** A move or a link of a folder that holds either file or a copy is a second name and is refused as a read, for every role. An in-place edit whose backup suffix is its own word without a dot, and a move or copy with an option the reader of operands cannot read, stay residuals.
  - The lead's reading of DEC-548's fourth point is confirmed: an existing file at the same project-relative path under another folder is treated as the file is.

| Version | Date | Change |
|---|---|---|
| 0.154 | 2026-10-09 | Delegated, stricter-only: DEC-553 (the guard follow-up on W1-02: a wildcard-only glob from a copy's folder refused, a deny path spelled from the home folder redacted, a move or link of a holding folder refused as a read). Next free id: DEC-554. |

## 155. Delegated: six points of the parallel-run follow-up's second run on W1-30 (register v0.155, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-554 — The close's time limit and worker count in the project's path map; a command wait in W1-07; four points as built
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible; no ticket closes on fewer tests; the lead's recommendation and the orchestrator's agree) · **Basis:** the lead's return at `c52de7c2` (`log/W1-30-lead-runF2.json`: two whole regressions in the close form, each green except one case that passed alone; a close of this repository takes about 16 to 20 minutes for the parallel part and 28 to 33 for the serial part) · **Under:** DEC-527, DEC-549, DEC-372
- **Decision:**
  1. **The time limit is a setting of the project, as built.** DEC-549's third point said "no code"; no project file could reach the limit, so the engineer moved its read: `close_timeout` and `close_workers` are optional top-level keys of `governance/project/path-map.yaml`, and the argument wins over the file. Kept. The orchestrator writes `close_timeout: 7200` there at the merge.
  2. **W1-07's wait for a read command** (30 seconds; `gov status --json` passed it once under ten workers): until the follow-up after W1-41, a case that fails on that wait and passes alone is re-run alone and named, as a latency case is (DEC-372). In that follow-up a test designer gives W1-07's commands a longer wait in W1-07's own support, as DEC-549 did for W1-27, with the same reason. The worker count of this repository stays `auto`.
  3. A project that gains a path map for these keys also gets what a path map brings in `gov rebuild` (the lexical index): accepted; the two rebuild-mode cases keep a project without one.
  4. The record states `auto` where the project says `auto`, not the count the runner chose: as built.
  5. The stricter readings of a worker count (a quoted number, a fraction, an empty value, another spelling of `auto` are refused): as built.
  6. The kernel's path-map schema names neither key, nor DEC-479's two: it goes to the follow-up after W1-41 with DEC-521's items, as a product-spec line.

| Version | Date | Change |
|---|---|---|
| 0.155 | 2026-10-09 | Delegated: DEC-554 (the parallel-run follow-up on W1-30: the close's time limit and worker count are settings in the path map; W1-07's command wait is re-run alone until a designer lengthens it; four points as built). Next free id: DEC-555. |

## 156. Delegated: the judgement of the probe of the parallel-run follow-up on W1-30 (register v0.156, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-555 — The parallel run in `gov close`: the probe is judged pass without a fix round; five of its findings are built in the follow-up after W1-41
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible) · **Basis:** the probe's return (`log/W1-30-probe3.json`, session `2e97ad0c-eee6-4500-baae-303e79f117f7`, at `c52de7c2`; nine findings, each reproduced or read; "no case is lost in any shape ordinary work produces") · **Under:** DEC-498, DEC-137, DEC-527, DEC-549, DEC-521
- **Decision:** The follow-up merges as probed. DEC-498 orders a fix before the merge only for a fail-open hole or a silent close in a shape ordinary work produces; the probe found none. The two shapes that close a ticket on a failing acceptance case need a deliberate or unusual input, and are named here and to the owner:
  - **Finding 1.** A run of the declared cases that ends with exit code 0 and no result (a case that ends its own process with 0) is accepted, because the parallel run's passes cover it.
  - **Finding 2.** A file in the project named like the close's own plugin replaces it (the plugin is named bare and its folder stands last on the import path), so a ticket's own commit can keep a failing case out of every run.
  - Both, with **finding 3** (parallel workers outlive a run cut at the time limit and can still write into the project), **finding 4** (a list entry that names an existing file without a case refuses nothing, against DEC-549's fourth point) and the first shape of **finding 7** (a byte in the list that is not UTF-8 ends in a traceback), are built in the follow-up after W1-41 with DEC-521's items, test designer first; that follow-up is FULL and is probed before its merge.
  - Findings 5, 6, 8 and 9 and the rest of 7 are residuals in `bootstrap.md` (counts that do not match what ran for entries outside the documented forms; `parallel` recorded for a run with no worker; no upper bound and YAML's own readings of the two settings; an unusable parallel plugin counted against the ticket; a very large time limit; a list that is a folder or begins with a byte-order mark).
  - Until that follow-up merges, the orchestrator reads the `test_runs` of every close: a run of declared cases with no passed case is not accepted as green.

| Version | Date | Change |
|---|---|---|
| 0.156 | 2026-10-09 | Delegated: DEC-555 (the probe of W1-30's parallel-run follow-up judged pass without a fix round; five findings, two of them fail-open in deliberate shapes, go to the follow-up after W1-41; until then the orchestrator reads each close's test runs). Next free id: DEC-556. |

## 157. Owner answers to P-22, P-23 and P-24, on the probe of W1-30's follow-up, on the outside sources of the adoption step, and one delegation (register v0.157, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-556 — P-22: open gate records in `gov status` go on the Wave 2 list
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-543
- **Decision:** Showing open `gate` records in `gov status` is an item of the Wave 2 list. For Wave 1, DEC-543 stands as decided.

### DEC-557 — P-23: the guard refuses a search from the project root that gives no path or glob, for every role
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-508, DEC-525, DEC-548, DEC-553
- **Decision:** A search from the project root that gives no path or glob is refused by the guard, for every role. W1-02's current probe and merge are not held for it. It is built as one short round on W1-02 after that merge: the test designer first, who also rewrites the 14 cases in W1-02, W1-05, W1-47 and W1-50 that hold such a search as allowed (recorded as rewrites, reason "owner decision P-23"), then the engineer, then that round's own reviewer probe before its merge.

### DEC-558 — P-24: three test-designer commits without `Implements:` are named exceptions; the pre-merge check is confirmed
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-476, DEC-492, DEC-516
- **Decision:** The commits `a7eb9257` (merged, W1-35's follow-up), `15a0dbc4` and `56f1476d` (branch `w1/W1-02`) carry `Task:` and `Role:` and no `Implements:`. They are named exceptions at a close, listed for the exit auditor with the earlier history commits. No branch is rewritten. W1-35 closes under the current close rules. The orchestrator's check of `Implements:` on every commit of a branch before its merge, and the trailer line in every lead brief, are confirmed.

### DEC-559 — The probe of W1-30's follow-up: DEC-555 is accepted
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-555, DEC-498
- **Decision:** Building the two findings of deliberate shape (a serial case that ends its own process with exit code 0; a project file that stands in for the close's plugin) in the follow-up after W1-41, with that follow-up's own probe, is accepted. Until it merges, the orchestrator keeps reading the test runs of each close itself.

### DEC-560 — Outside sources at this repository's adoption step: two kinds
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-511, DEC-520, DEC-522, DEC-551
- **Decision:**
  - Decisions and evidence the repository relies on (the `OWNER-…` ids; the evidence record of `EXP-001`) are imported as records, each with its origin path and its sha256 recorded.
  - Ids of the research catalogues (`S0a-G-…`, and S0b2's `G-…`) are listed as external references (DEC-520).
  - The orchestrator prepares the full list of the about 35 ids, sorted into the two kinds, and applies it in the adoption step. Only an id that fits neither kind is brought to the owner.

### DEC-561 — Delegated: the long code-index daemon cases of W1-16 and W1-20
- **Status:** ACCEPTED (owner, 2026-10-09; delegated to the orchestrator) · **Under:** DEC-527, DEC-554
- **Decision:** In the follow-up after W1-41 the orchestrator has it found why the code-index daemon cases of W1-16 and W1-20 take 17 to 19 minutes when run alone (for example a daemon started for each case where one for a session would do), and has them shortened where that can be done without weakening what they test. The new serial time is reported to the owner.

| Version | Date | Change |
|---|---|---|
| 0.157 | 2026-10-09 | Owner: DEC-556 (gate records in status on the Wave 2 list), DEC-557 (a root search without path or glob is refused for every role; a short W1-02 round after the merge), DEC-558 (three commits without Implements are named exceptions; W1-35 closes; the pre-merge check confirmed), DEC-559 (DEC-555 accepted), DEC-560 (outside sources: decisions and evidence imported as records with origin and sha256, catalogue ids listed as external), DEC-561 (delegated: the W1-16 and W1-20 daemon cases). Next free id: DEC-562. |

## 158. Delegated: the judgement of the probe of the guard follow-up on W1-02 (register v0.158, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-562 — The read rule for the two protected files: the probe is judged pass; the follow-up merges as probed and three findings join the round of DEC-557
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible; stricter-only for what is built) · **Basis:** the probe's return (`log/W1-02-probe.json`, session `cc784d3e-ecb5-4176-8726-847f86f79cf6`, at `e9e6ee25`; eleven findings; no ordinary work newly stopped in about 170 daily calls; a shell command with a tilde and a NUL byte is refused, exit code 2) · **Under:** DEC-498, DEC-137, DEC-508, DEC-525, DEC-557
- **Decision:**
  - **The follow-up merges as probed.** The integration branch holds no read rule for the two files today, so the merge refuses more in every case and loosens nothing; the owner ordered a short round on W1-02 directly after this merge, with its own probe (DEC-557). The one finding in a shape ordinary work produces is built in that round, not in a round of its own before the merge.
  - **Into the round of DEC-557, test designer first:**
    - **Finding 1 (a read gets through, ordinary work produces it).** A search in the shell from the project root, or from a copy's folder, whose name filter names either file's name or matches it (`--include`, the other search program's glob option in each spelling) is refused, as the same search through the search tool with that glob is.
    - **Finding 7 (no answer in time; whether it fails open is the harness's).** The rule answers every pattern and every command in bounded time: a pattern or a command the rule cannot answer within its bound is refused. The round establishes, without reading the settings file, what the harness does with a hook that passes its time limit, and returns it.
    - **A NUL byte in a path or a command** is refused wherever it stands (today a NUL with no tilde before it is allowed and one with a tilde is refused).
  - **Residuals, named in `bootstrap.md`** (each needs a deliberate or unusual shape): a `cd` that does not take effect (a subshell, a pipeline, a background job, a branch not taken, a folder that does not exist) is followed all the same, which lets a read through and refuses two ordinary listings; shell spellings the token expansion gives up on; a script on the command line with an operator glued to the name, and a here-string; search-tool globs with an escape, single braces or a comma; an in-place edit that prints, by a role that may write the file; the helper's unmatched rule shapes, a path held outside the deny list, the matcher and event printed as written, and the lesser spellings.

| Version | Date | Change |
|---|---|---|
| 0.158 | 2026-10-09 | Delegated: DEC-562 (the probe of the guard follow-up on W1-02 judged pass; it merges as probed; a shell search with a name filter, an answer in bounded time and a NUL byte join the round of DEC-557; the rest are residuals). Next free id: DEC-563. |

## 159. Owner answers to P-25, on EXP-001's evidence file, on the schema findings of probe records, on two findings of W1-30's close, and a Wave 2 item (register v0.159, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-563 — P-25: W1-16's case on this repository's runtime folder is re-run alone until a designer narrows it; W1-30 closes
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-372, DEC-322, DEC-527
- **Decision:** Until it is fixed, W1-16's `test_this_repository_is_not_indexed_by_the_run` is treated like a case of DEC-372: when it fails in a regression or a close it is re-run alone, and it is named for the exit auditor. W1-30 closes now. In the follow-up after W1-41 a test designer narrows the case to watch only the index stores, not the whole runtime folder.

### DEC-564 — EXP-001's evidence file: its place, and its import at the adoption step
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-152, DEC-560
- **Decision:** EXP-001's evidence file is at `/home/usain/gov-os-workbench/spike-sandbox/EVIDENCE.md`. It is read by that exact path only; the folder is never listed. It is imported as a record at the adoption step, with its origin path and its sha256 (DEC-560). The orchestrator confirmed on 2026-10-09 that the file exists (266 lines; sha256 `84ce1d1390d40a25ae1b5a8af224db871132ebcd8d5b0842b64796f1e0ad7714`); the import checks the bytes against that value.

### DEC-565 — The schema findings a probe record adds are known growth; the probe type enters the kernel's record schema in the follow-up after W1-41
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-467, DEC-481, DEC-505
- **Decision:** The four findings each probe record adds to the schema check are accepted as known growth and are recorded with each probe record. In the follow-up after W1-41 the probe type is added to the kernel's record schema, so that the schema check returns to its recorded baseline. DEC-467's rule that a new finding in a baseline check blocks a merge applies to everything else as before.

### DEC-566 — Two findings of W1-30's close: the probe gate on `ccac9506`, and the runs of a refused close
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-505, DEC-549, DEC-555
- **Decision:** The probe gate's finding on the orchestrator's commit `ccac9506` (the residual notes and the project's close time limit, made after the probed commit) is covered by DEC-505. That a refused close prints the totals of its test runs and not each run is accepted as an item of the follow-up after W1-41.

### DEC-567 — Wave 2 list: "fast feedback at scale", one item beside DEC-534's two; and its ranking
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-534, DEC-527 · **Scope:** the Wave 2 list only; nothing in Wave 1 changes
- **Decision:** The Wave 2 list gains one item, "fast feedback at scale", beside impact-based test selection and language-agnostic test commands (DEC-534). Its parts:
  - **Test result caching.** A test whose code, dependencies and data are unchanged since its last green run is not re-run; its earlier result is reused and named as reused.
  - **A merge queue.** Several finished tickets are merged as one batch, the batch's combination is tested once, and a failing batch is split automatically to find the culprit.
  - **Staged gates.** A ticket's close runs its own tests plus the tests impact selection names; the full suite runs nightly, at each wave's exit, and before any release.
  - **The full suite on CI machines** rather than this one, where the project allows it.
  - **Flaky-test quarantine.** A case that fails and then passes alone is marked flaky automatically, kept out of the gate with its record, and must be fixed or removed within a set time; the list of quarantined cases is visible in gov status.
- **Ranking for Wave 2 planning:** language-agnostic test commands are a must-have before the Gov OS is adopted in any non-Python repository (UPIM, ASMO). They, impact-based selection and result caching stand at the top of Wave 2.

| Version | Date | Change |
|---|---|---|
| 0.159 | 2026-10-09 | Owner: DEC-563 (W1-16's runtime-folder case re-run alone and named until a designer narrows it; W1-30 closes), DEC-564 (EXP-001's evidence file, its exact path and sha256, imported at adoption), DEC-565 (a probe record's four schema findings are known growth; the probe type enters the schema in the follow-up after W1-41), DEC-566 (the probe gate on ccac9506 is covered by DEC-505; per-run figures on a refused close go to the follow-up), DEC-567 (Wave 2 list: fast feedback at scale - result caching, a merge queue, staged gates, the full suite on CI machines, flaky-test quarantine; language-agnostic test commands, impact selection and result caching rank at the top). Next free id: DEC-568. |

## 160. Delegated, stricter-only: one package of W1-41's fix round (register v0.160, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-568 — All-external sources: refused whatever the ticket's dependencies name; a deprecated record holds a store back
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, stricter-only, as built; the lead's recommendation and the orchestrator's agree) · **Basis:** the lead's return at `868d72b9` (`log/W1-41-lead-run4.json`: the three behaviours of DEC-552 built, 182 cases green, every acceptance suite green) · **Under:** DEC-552, DEC-551, DEC-454
- **Decision:**
  - **P-14: (a).** A ticket is refused whenever every id under its `sources` is an external reference, whatever its `depends_on` or `deps` name (a ticket, a decision or another record). Listing a record as a dependency does not make a source read.
  - A record with the status `DEPRECATED`, with no status or with an unknown one holds a legacy store back in the dependency proof, as DEC-552's wording gives it: only `SUPERSEDED`, `RETIRED` and `REJECTED` release. A record that is superseded by an edge alone, with its status unchanged, holds the store back too.
  - No second probe (DEC-498): the fix round's diff is 17 lines added and 8 removed, each refusing more; the lead and the orchestrator read it.

| Version | Date | Change |
|---|---|---|
| 0.160 | 2026-10-09 | Delegated, stricter-only: DEC-568 (W1-41's fix round: an all-external ticket is refused whatever its dependencies name; only superseded, retired and rejected records release a legacy store). Next free id: DEC-569. |

## 161. Delegated: the follow-up after W1-41, its ticket and its paths (register v0.161, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-569 — The follow-up after W1-41 runs on W1-30's ticket, reopened; its pieces and its paths
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible; told to the owner, who may replace it) · **Basis:** DEC-521 orders one short follow-up after W1-41 and names no ticket; most of its pieces change `gov close` · **Under:** DEC-521, DEC-416, DEC-498, DEC-532
- **Decision:**
  - **Ticket.** The follow-up runs on `DAEO-2lwj` (W1-30, `gov close`), reopened for it, profile FULL, with its own reviewer probe before the merge (DEC-498, DEC-559). A test designer comes first for every piece.
  - **Pieces, each ordered by the decision named:** the trailers base commit (DEC-482); the owner-decision lookup from a register file (DEC-483); the record store loads the decisions of the project's named register file as decision records, one per heading (DEC-521, DEC-473); the close record's skills list in a project with an installed kernel, and the declared check commands that name `template/` paths (DEC-521); `gov close` calls the counter (DEC-495); the probe gate (DEC-505); the command-list lines for `ci`, `launch`, `telemetry` and `lock` (DEC-542); the READY rule on a constraining package the store could not load (DEC-544); the repair ticket of a refused close whose findings are too long for one argument; findings 9 and 10 of W1-41's probe with the two readings beside them (DEC-552); findings 1, 2, 3, 4 and the first shape of 7 of W1-30's probe (DEC-555); a refused close prints each test run (DEC-566); a longer command wait in W1-07's support and the path-map schema's keys (DEC-554); the probe type in the kernel's record schema (DEC-565); W1-16's runtime-folder case narrowed to the index stores (DEC-563); the code-index daemon cases of W1-16 and W1-20 (DEC-561).
  - **Paths.** The ticket's `allowed_paths` gain, for this follow-up: `src/gov/check/**`, `tests/unit/check/**`, `src/gov/store/**`, `tests/unit/store/**`, `src/gov/readiness/**`, `tests/unit/readiness/**`, `src/gov/context/**`, `tests/unit/context/**`, `src/gov/telemetry/**`, `tests/unit/telemetry/**`, `src/gov/codeintel/**`, `tests/unit/codeintel/**`, `template/governance/kernel/schemas/**`, `template/governance/kernel/checks/**`. Nothing under the guard's paths is in it. A piece that needs another path comes back as a package.
  - **This repository's own settings** (the trailers base `429815b5` of DEC-482, as a key of the path map) are written by the orchestrator at the merge, as `close_timeout` was (DEC-554).
  - If the lead finds the follow-up too large for one round, it returns the pieces it built with the head named and lists the rest; nothing is dropped silently.

| Version | Date | Change |
|---|---|---|
| 0.161 | 2026-10-09 | Delegated: DEC-569 (the follow-up after W1-41 runs on W1-30's ticket, reopened, FULL with its own probe; its pieces by decision; the paths it adds). Next free id: DEC-570. |

## 162. Delegated: the probe of W1-02's root-search round (register v0.162, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-570 — W1-02's round of DEC-557: the probe is judged pass with one fix round, stricter-only
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, stricter-only; told to the owner, who may replace it) · **Basis:** the probe's return (`log/W1-02-probe4.json`, session `ea1c1fed-b545-4461-b029-09dae6731851`, at `dc9fda16`, code `02d0b35b`; each finding reproduced on a stand-in project) · **Under:** DEC-498, DEC-137, DEC-557, DEC-562
- **Decision:** DEC-498 orders a fix before the merge for a hole in a shape ordinary work produces. The probe found such shapes, so one fix round is built before the merge, test designer first, each point refusing more than today:
  - **A root search with a numbered redirect** (`2>/dev/null`, `2>&1`, `1>file`) is refused like the same search without it: the number of a redirect is no path. (The probe's A1; ordinary work types it constantly.)
  - **A search after a shell keyword** (`do`, `then`, `else`, `if`, `while`, `until`, and a `!` in front) is judged as the search it is. (A2.)
  - **Daily spellings:** a comment after the search is no path; `ls` and `grep` option groups that hold a digit beside the recursive letter; `egrep` and `fgrep`; a search behind `timeout`, `command`, `env`, `nice`, `nohup` or `time`. (A3, and `time` of A4.)
  - **A brace word that expands past the bound is refused**, not judged unexpanded. (A5; a deliberate shape, but one line.)
  - **Time.** The harness lets a call through when the hook passes its time limit (DEC-110, DEC-179), so a slow decision fails open. The probe found decisions of 1 to 190 seconds for inputs under the round's bounds (long paths times many filters or expansions; many fed searches in one command). The rule's work is bounded by count times length, or the input is refused; the test designer states the bound as a time with a wide margin for a loaded machine.
  - **Residuals, not built:** `find` with a name test (it prints names; what reads them is the run-time-name residual already recorded); valued options the rule does not list; a search in a brace group, in a shell started with `-c`, behind `xargs`, or with a substitution as its path; a file-tool path that is not text; a line of a here-document's body that reads as a search is refused (the way round is the file tool); `rg --type-list`.
  - **Told to the owner, as built:** a type filter with no path (`rg -t py <word>` from the root) is refused, as DEC-557's wording "no path or glob" gives it; the refusal names the way round (`-g '*.py'`).
  - **No second probe** if the fix round's product diff only adds refusals and is small enough for the lead and the orchestrator to read line by line (DEC-552's precedent); otherwise a second probe before the merge.

| Version | Date | Change |
|---|---|---|
| 0.162 | 2026-10-09 | Delegated, stricter-only: DEC-570 (the probe of W1-02's root-search round is judged pass with one fix round: numbered redirects, searches after shell keywords, daily spellings, a brace word past the bound, bounded decision time). Next free id: DEC-571. |

## 163. Delegated: the fix round of W1-02's root-search round merges without a second probe (register v0.163, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-571 — W1-02's fix round after the probe: read line by line, stricter-only, no second probe
- **Status:** ACCEPTED (delegated to the orchestrator, 2026-10-09; P3, reversible, stricter-only; the lead's reading and the orchestrator's agree) · **Basis:** the lead's return at `02f0294d` (`log/W1-02-lead-run5.json`: code at `10e6ef39`; 2762 cases in the suite, every acceptance suite and 1804 unit tests green; over three seeds of 420,000 random calls no call that was refused is now allowed; the probe's thirteen slow inputs answer in under 0.4 s) and the orchestrator's own reading of `git diff 033bbbca 02f0294d -- src/` · **Under:** DEC-570, DEC-498, DEC-552
- **Decision:**
  - DEC-570's condition holds: the product diff is 127 lines added and 22 removed in one file, and every changed line adds refusals or does the same work with the same answer. The one line that alone would loosen (a path is no longer resolved once a call's paths hold more than 131,072 folders) sets in the same statement the mark that refuses the call. No second probe.
  - **Refused beyond what was ordered, kept as built (stricter):** a quoted word whose brace groups expand past the bound (inline JSON or a script with many brace groups: put it in a file); a digit word directly before a redirect in a search is read as the redirect's number; a call whose paths together hold more than 131,072 folders; `find` and `ls` behind a keyword or prefix.
  - The designer's point on `mkdir -p` with a brace word under the scratch folder (denied today by the write rule, not by this round) changes nothing; allowing it would loosen the write rule and is not proposed.
  - The residuals of the round (the lead's 36 to 51) go to `governance/project/bootstrap.md`.

| Version | Date | Change |
|---|---|---|
| 0.163 | 2026-10-09 | Delegated, stricter-only: DEC-571 (W1-02's fix round after the probe is read line by line and merges without a second probe; four stricter behaviours kept as built). Next free id: DEC-572. |

## 164. Owner answers to P-26, P-27 and P-28, on the type filter, on three delegated decisions, on the guard's scope for the rest of Wave 1, and a delegated experiment on a hook's time limit (register v0.164, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-572 — P-26: `803f731c` is a named exception and W1-41 closes; a merge commit's file that equals one parent's version is not its own change
- **Status:** ACCEPTED (owner, 2026-10-09) · **Basis:** OWNER, on package P-26 option (a) (`log/close-W1-41.json`) · **Under:** DEC-492, DEC-519, DEC-522, DEC-410
- **Decision:**
  - Commit `803f731c` (the orchestrator's merge of `w1/integrate` into `w1/W1-41`, which brought the ticket file's path and KPI lines as they were committed on `w1/integrate`) is a named exception, listed for the exit auditor. W1-41 closes.
  - In the running follow-up after W1-41, test designer first: a merge commit's file is not its own change when it equals one parent's version and every commit that brought that version passes the check.
  - The existing rules stay as they are: a merge commit's own change under `tests/acceptance/**` or `.tickets/**` remains a finding, and so do both sides changing the same acceptance test (DEC-410).

### DEC-573 — P-27: a root search is refused only where a protected file, or a copy of one, lies under the search start
- **Status:** ACCEPTED (owner, 2026-10-09) · **Basis:** OWNER, on package P-27 option (b), as built · **Refines:** DEC-557
- **Decision:** The guard refuses a root search only where a protected file, or a copy of one, lies under the search start. A project that holds neither refuses none.

### DEC-574 — P-28: the held-out check skips path resolution for a string longer than the system path limit
- **Status:** ACCEPTED (owner, 2026-10-09) · **Basis:** OWNER, on package P-28 option (a) (`log/W1-02-lead-run4.json`: a megabyte of path-like text in a field that is not a path takes 40 seconds and more to decide) · **Under:** DEC-570
- **Decision:** The held-out check skips path resolution for any string longer than the system path limit, and keeps the literal substring check.

### DEC-575 — A type filter with no path stays refused
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-557, DEC-570
- **Decision:** `rg -t <type>` from the root with no path stays refused, as built; the refusal names `-g` as the way round.

### DEC-576 — DEC-569, DEC-570 and DEC-571 are accepted
- **Status:** ACCEPTED (owner, 2026-10-09)
- **Decision:** The orchestrator's delegated decisions DEC-569 (the follow-up after W1-41 on W1-30's ticket), DEC-570 (the probe of W1-02's root-search round, one fix round) and DEC-571 (the fix round merges without a second probe) are accepted.

### DEC-577 — Guard scope for the rest of Wave 1
- **Status:** ACCEPTED (owner, 2026-10-09) · **Under:** DEC-498, DEC-557
- **Decision:** After the current W1-02 round merges, there are no further guard rounds in Wave 1, except for a hole that ordinary work produces. Holes that need a deliberate shape become residuals on the Wave 2 list.

### DEC-578 — Delegated experiment: what the harness does with a PreToolUse hook that passes its time limit; an explicit time limit for this repository's guard hooks
- **Status:** ACCEPTED (owner, 2026-10-09; delegated to the orchestrator) · **Under:** DEC-102, DEC-110, DEC-179, DEC-570
- **Decision:**
  - Now, in a throwaway project under `/tmp`: register a PreToolUse hook that sleeps past its time limit, and record whether Claude Code allows the call, blocks it, or errors. The result is recorded as an evidence record.
  - Then an explicit time limit is set for this repository's guard hooks in the settings, through the owner, as a line the operator applies.
  - If a timed-out hook lets the call through, the orchestrator brings the owner one package on how the guard should fail closed.

| Version | Date | Change |
|---|---|---|
| 0.164 | 2026-10-09 | Owner: DEC-572 (P-26: 803f731c a named exception, W1-41 closes; a merge commit's file equal to one parent's version is not its own change), DEC-573 (P-27: a root search is refused only where a protected file or a copy lies under its start), DEC-574 (P-28: the held-out check skips path resolution for strings longer than the system path limit), DEC-575 (a type filter with no path stays refused), DEC-576 (DEC-569 to DEC-571 accepted), DEC-577 (no further guard rounds in Wave 1 except for a hole ordinary work produces), DEC-578 (delegated experiment on a hook's time limit; an explicit time limit for the guard hooks through the owner). Next free id: DEC-579. |
