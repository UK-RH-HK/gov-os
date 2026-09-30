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
