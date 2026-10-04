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
