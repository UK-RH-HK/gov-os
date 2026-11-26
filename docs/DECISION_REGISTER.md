# Governance OS — Decision Register (in force)

**Register ID:** GOV-DR · **Built from:** the archived register `docs/archive/DECISION_REGISTER-2026-11-19.md` (archived read-only,
EMERGENCY-2 §11.3), by `docs/emergency-2/audits/08-new-register.py`.

This file is the decision register in force. The earlier decisions are in the archive, by id: `docs/archive/DECISION_REGISTER-2026-11-19.md`.
Each entry below is copied verbatim from it: the decisions audit 8 (`docs/emergency-2/audits/08-register.md`) classed
**kept** (the owner approved the classes by group, DEC-1214 G4) and every decision since (DEC-1211 and later). The
`**Class:**` field at the end of an entry's status line says which items of a kept entry no longer hold. A decision that
is not here is in the archive; the archive is not in memory's index. New ids continue from the last entry's.

---

## Decisions

### DEC-001 — Assemble first; Rust kernel becomes the later replacement
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION · **Class:** kept
- **Decision:** Build the Governance OS by assembling existing tools behind a stable `gov` CLI interface (Python first). The Rust implementation continues later as a drop-in replacement of the `gov` CLI internals, not as a prerequisite for product work.
- **Rationale:** Contract v3's own proposed order places ~9 milestones (including synthetic qualification repos and a retrieval bake-off) before Product A/B adoption. Tools now exist for most layers (see §3).
- **Consequence:** The `gov` command surface and file formats (frontmatter schema, lockfile, context packet schema, checkpoint schema) are the **surviving layer**; implementations may change.
- **Revisit trigger:** Assembled version fails a Solo Core gate that no tool can cover, or glue exceeds ~3k lines.

### DEC-003 — Governance is code, not prose
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION · **Class:** kept (items changed: (compiled context packet) superseded §5.5)
- **Decision:** No agent reads the framework, protocols or contract during normal work. They compile into deterministic checks (hooks, `gov check`, CI). Agents see only: a short AGENTS.md (target ≤ ~1.5k tokens), a compiled context packet, and terse `gov` output.
- **Rationale:** Framework (~62KB) + contract (~42KB) ≈ 25k tokens per session if read; multiplied across fresh independent sessions this dominates spend.
- **Gates:** A1, G1, M1 (T0 routing), U (tokens/completed task)

### DEC-005 — Proportionality profiles keyed to impact radius
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION · **Changed by:** DEC-085 (readiness reduction) · **Class:** kept (items changed: (readiness reduction) history DEC-085)
- **Decision:** Three ceremony profiles: `LITE` (R0–R1), `STANDARD` (R2), `FULL` (R3+). Profile controls: readiness dimensions required, independent test author/verifier, retrieval budget, human gate.
- **Readiness (H2) reduction:** 8 mandatory dimensions always (intent, actor, scenarios, inputs/outputs, data, success+failure criteria, acceptance tests, security); remaining 18 conditional by capability type and profile, with `N/A_WITH_REASON` auto-default.

### DEC-006 — Progressive adoption
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION · **Class:** kept
- **Decision:** A repo is governable from day one (hooks + `gov check` + task tracker) while A1–A11 path migration proceeds in background batches. Full A0–A11 remains the target for `ADOPTED_HEALTHY`.

### DEC-007 — Native harness features first; CI is the enforcement boundary
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED + SUGGESTION · **Changed by:** DEC-075 · **Class:** kept
- **Decision:** Use harness-native hooks, subagents, skills and LSP where they exist. Treat hooks as guardrails, never as the security/enforcement boundary. Every hook check is re-run in git hooks (lefthook) and CI, which are authoritative for merge.
- **Evidence:**
  - Claude Code hook docs note a stalled hook does not act as a gate — the call continues through the normal permission flow. [E-HOOK-CC]
  - OpenAI's Codex hook docs state tool hooks are a guardrail, not a complete enforcement boundary; some tool paths bypass the default hook path. [E-HOOK-CX]
- **Gates:** N3 (provider-independent watchdog), O5 (G0–G5 tiers)

### DEC-010 — Agent harness
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Class:** kept
- **Decision:** Claude Code as primary T2/T3 harness (Claude Max 5x to start). Optional second model family (Codex) as independent verifier for R3+ changes.
- **Evidence:** Pro $20/mo; Max $100 (5x) or $200 (20x). Programmatic/headless usage (Agent SDK, `claude -p`, GitHub Actions) draws from a separate monthly credit pool rather than interactive limits. [E-PRICE]
- **Consequence:** Health-scheduler verifiers should run as interactive subagents, or headless spend must be budgeted separately (Gate A4).
- **Revisit trigger:** telemetry shows sustained limit hits → Max 20x.

### DEC-011 — Specification & change control: OpenSpec
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Class:** kept
- **Decision:** OpenSpec owns spec truth (`openspec/specs/`) and change proposals (`openspec/changes/`). Proposal ≈ CIT-P; archive ≈ CIT-E. Accept OpenSpec's directory convention; the project path map describes it (do not force into `spec/`).
- **Pin:** ≥ v1.12.0 (findings-only validation reports; code-grounded planning). [E-OSPEC-REL]
- **Extension point:** custom schemas in `openspec/schemas/` (version-controlled) — use to add readiness and impact artefacts to the change workflow. [E-OSPEC-CUST]
- **CI:** `openspec validate --strict` runs at G2/G5.
- **Gates:** H1, K1, K2, W1 (partial)
- **Alternatives considered:** GitHub Spec Kit (heavier, greenfield-oriented); BMAD (REJECTED, DEC-021).

### DEC-012 — Decisions: ADR markdown with frontmatter in git
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED (ADR practice) + SUGGESTION (schema) · **Class:** kept
- **Decision:** Decisions are ADR files in git with YAML frontmatter: `id`, `type`, `status` (ACTIVE/PROVISIONAL/SUPERSEDED/…), `supersedes`, `superseded_by`, `depends_on`, `implements`, `constrains`, `content_hash` (computed). The decision/spec graph is **derived deterministically** from frontmatter into SQLite — no LLM extraction.
- **Explicitly not used:** codebase-memory-mcp's `manage_adr` feature — an open issue (July 2026) reports ADR content silently destroyed on incremental reindex. [E-CBM-ADR]
- **Gates:** B3, C1, C2, C6, W1–W3, W10

### DEC-014 — Code-structural memory: codebase-memory-mcp
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Class:** kept
- **Decision:** Use codebase-memory-mcp for call graphs, impact analysis, routes, dead code.
- **Evidence:** 31-repo evaluation: 83% answer quality vs 92% for a file-exploration agent at ~10× fewer tokens and 2.1× fewer tool calls. [E-CBM-PAPER]
- **Pin & hygiene:**
  - Use a release after the July–August 2026 fixes: watcher no longer re-indexes dirty repos every poll (previously caused >1 TB/day disk writes), and store/artifact integrity fixes with atomic reindex publication. [E-CBM-WATCH][E-CBM-REL]
  - Upgrades can force one full cold reindex (format stamp). [E-CBM-REL]
  - Incremental reindex has open performance issues on very large monorepos (not expected to affect our repo sizes). [E-CBM-INC]
  - Do **not** commit its `.codebase-memory/graph.db.zst` artifact by default — derived state stays gitignored (B3); revisit if clean-clone rebuild time becomes painful.
- **Gates:** C5, D2 (code route), K1 (code-side impact), W7 (dead code)

### DEC-016 — Lexical + semantic index: SQLite FTS5 + sqlite-vec, fused with RRF
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Changed by:** DEC-074 (R1) · **Class:** kept
- **Decision:** One derived `.gov-runtime/index.sqlite` with FTS5 (lexical) + sqlite-vec (vectors), Reciprocal Rank Fusion. Content-hash gating for incremental embedding. Brute-force vector search is adequate to ~100K vectors — far above expected spec/decision/research corpus size. [E-VEC]
- **Upgrade path:** LanceDB if vectors exceed ~100K or latency degrades.
- **Gates:** C3, C4, D1, D2, D3, D6

### DEC-017 — Embedding & reranking models
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Changed by:** DEC-074 (R1) · **Class:** kept
- **Decision:** Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B via Ollama, resident on GPU (~3 GB VRAM total). Pin revisions in the index manifest (D5).
- **Licence rule:** only permissively licensed models (Apache-2.0/MIT). Some top-ranked embedders (e.g. jina-embeddings-v3) are non-commercial and are excluded for commercial projects. [E-EMBED]
- **Gates:** D4, D5

### DEC-022 — Provider adapters: rulesync
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Class:** kept
- **Decision:** Single source in `.rulesync/` generating CLAUDE.md, AGENTS.md, `.claude/`, Codex and other targets; `rulesync import` used during legacy-rule retirement (R1). [E-RULESYNC]
- **CI:** generated files must match source (drift = G2 failure). Generated adapters are never hand-edited.

### DEC-023 — Distribution: Copier (`gov init` / `gov update`)
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Class:** kept
- **Decision:** `gov-os` repo is a Copier template; kernel files are template-owned; overlay files listed in `_skip_if_exists`; tags = releases. Update uses Copier's three-way merge. [E-COPIER][E-COPIER-SKIP]
- **Rule:** never hand-edit `.copier-answers.yml` (breaks the update diff). [E-COPIER-DOCS]
- **Lock:** `framework.lock` = `.copier-answers.yml` reference + file hash manifest generated at install.
- **Gates:** S1, S2 (partial), S3, S5, S6

### DEC-024 — Method skills: Superpowers, selectively
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Changed by:** DEC-074 (Q5) · **Class:** kept (items changed: two-stage review in subagent-driven dev superseded §3.6)
- **Decision:** Adopt selected Superpowers skills (test-driven development, systematic debugging, verification-before-completion, subagent-driven development with two-stage review). OpenSpec (DEC-011) remains owner of planning/spec artefacts — do not run Superpowers' brainstorm/plan workflow in parallel with OpenSpec proposals.
- **Evidence:** 14 SKILL.md files plus a session-start bootstrap reportedly under ~2k tokens; multi-host; listed in Anthropic's official plugin marketplace. [E-SUPERPOWERS][E-SP-MKT]
- **Gates:** F1, O3 (two-stage independent review)

### DEC-025 — Enforcement stack
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Class:** kept (items changed: PreToolUse guard superseded §2.2; SessionStart context superseded §5.5; gitleaks superseded §2.11; PreCompact/Stop checkpoint kept §6.1)
- **Decision:**
  - Claude Code hooks: `SessionStart` (inject compact context + `br ready`), `PreToolUse` (path guard via exit 2 / `permissionDecision: deny`; the guard is a **default-deny allow-list** of the task's declared paths — see DEC-041), `PreCompact` + `Stop` (checkpoint; guard against loops with `stop_hook_active`), `SubagentStop` (worker return contract N4). [E-HOOK-CC][E-HOOK-EVENTS]
  - Codex hooks mirror where supported; Codex caps model-visible hook output at ~2,500 tokens → context packet delivered as file path + short summary, not inline. [E-HOOK-CX]
  - lefthook (pre-commit/pre-push) + CI run `gov check` tiers; gitleaks for secrets.
- **Gates:** A3, E1, N2, N3, O5 (G0–G3 local, G4–G5 CI)

### DEC-030 — Retrieval completeness principle
- **Status:** ACCEPTED · **Basis:** OWNER · **Changed by:** DEC-080 · **Class:** kept
- **Decision:** A top-k or per-query token allowance (e.g. 8k) is a batch size, not an evidence-completeness limit. Retrieval supports multiple batches, pagination/continuation, facets, adaptive follow-up, multi-hop, provenance-preserving merge, deduplication, authority/current/superseded filtering, and an explicit stopping reason. Parallel facet retrieval → merge/filter → unresolved dependencies → sequential follow-up → repeat → bounded context compilation. Evidence larger than one packet uses hierarchical synthesis whose notes are derived, cited, lineage-preserving, disclose unresolved evidence, and are rebuildable.
- **Gates extended:** D2, D3, C9, W4, W10

### DEC-032 — Retrieval loop runs in a disposable context
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED (harness subagents) + SUGGESTION · **Changed by:** DEC-080 · **Class:** kept
- **Decision:** Iterative retrieval and synthesis run inside a research subagent; only the compiled, cited bundle returns to the implementing context.

### DEC-033 — Deterministic worklist for closure facets
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION · **Changed by:** DEC-080 · **Class:** kept
- **Decision:** `gov retrieve` resolves referenced IDs (spec, ADR, task, symbol) through the frontmatter graph and codebase-memory callers/callees to a radius-scaled depth at T0 (no LLM). LLM judgement only for the semantic facet. Completeness for deterministic facets = dependency closure to depth N; for semantic facets = saturation.

### DEC-034 — Stopping reasons (enumerated)
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION · **Changed by:** DEC-080 · **Changed by:** DEC-396 · **Class:** kept (items changed: amended by DEC-080, DEC-396)
```text
CLOSURE_COMPLETE             # no unresolved referenced IDs within depth limit
SATURATED                    # follow-up batch added < ~10% novel sources after dedup
DEPTH_LIMIT_REACHED          # closure incomplete beyond radius-scaled depth; gaps listed
BUDGET_EXHAUSTED_WITH_GAPS   # ceiling hit; unresolved list disclosed; escalate if R≥3
FACET_UNAVAILABLE            # index stale/down; NOT_FOUND ≠ absent
```

### DEC-035 — Radius-scaled budgets and task-class facets
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION (numbers are placeholders to tune from telemetry) · **Changed by:** DEC-080 (numbers stay placeholders) · **Class:** kept

  | Impact radius | Facets | Max follow-up rounds | Synthesis |
  |---|---|---|---|
  | R0–R1 | code + tests | 1 | none |
  | R2 | + decisions, graph | ~3 | single pass |
  | R3+ | all (WHY, decisions, code, graph, tests, history) | ~8, then escalate | hierarchical + verifier |

  Facet selection also by task class (bug fix → code, tests, history, failures; spec change → decisions, graph, tests).

### DEC-036 — Synthesis notes: derived + deterministic citation check
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED (RAPTOR/GraphRAG/map-reduce patterns) + SUGGESTION (check) · **Changed by:** DEC-080 · **Class:** kept (items changed: amended by DEC-080)
- **Decision:** Notes stored in `.gov-runtime/` (derived); invalidated when any cited `source_sha256` changes. G2 verifies every cited source ID exists at the cited hash and every quoted span appears in the source.

### DEC-037 — Zero-result canaries on every index
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** SUGGESTION, motivated by ESTABLISHED evidence · **Changed by:** DEC-080 · **Class:** kept
- **Decision:** Each derived index (FTS/vector, codebase-memory, RAGFlow if adopted) has a small set of canary queries with known expected hits, run at G1 after reindex and at G4/G5. A canary miss marks the facet `FACET_UNAVAILABLE`, never "no evidence exists".
- **Motivation:** 2026 silent-zero defects in RAGFlow retrieval and connectors [E-RF-ZERO][E-RF-GH]; Contract rule "NOT_FOUND is never proof of absence".

### DEC-039 — Threat model: the Gov OS guards against mistakes and drift, not a same-privilege adversary
- **Status:** ACCEPTED (owner, 2026-09-29); to be written as ADR-0001 · **Basis:** ESTABLISHED (owner's own Phase-2 finding) + SUGGESTION · **Changed by:** DEC-075 · **Changed by:** DEC-1204 (merged into the golden rule, how work is judged) · **Class:** kept
- **Decision:** The Gov OS's purpose is to keep agents accurate, bounded and traceable. It does **not** attempt to be a security boundary against a process running with the owner's OS privileges. The hard boundary is: git history, CI on a protected branch, and owner-signed approvals (signed commits/tags or PR approval by the owner's account). This is ADR-0001 of the new repository.
- **Rationale:** Phase 2's eight-round loop was an attempt to make a same-privilege process secure against itself; the repository's own records identify this as the confused-deputy / ambient-authority problem and concede the seal is not proof-grade.
- **Consequence:** No in-process trust classes beyond the simple rule inherited from D-0007 (DEC-046).

### DEC-040 — The Gov OS never executes install commands; tools are installed by the owner and pinned
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083, as realised by later decisions; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED (Phase-2 evidence) · **Changed by:** DEC-083 (installs: owner approval per tool) · **Class:** kept (items changed: owner approval per tool (DEC-083) superseded §2.3)
- **Decision:** No `gov tools install` equivalent and no argv classification. Third-party tools (DEC-011…DEC-026) are installed by the owner with a version pin recorded in `governance/project/tool-registry.yaml`; `gov doctor` only verifies presence and version.
- **Rationale:** The tool-install surface produced HIGH findings in every Phase-2 review round; "reading argv" cannot determine what executes.

### DEC-050 — Workstation hygiene
- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED + SUGGESTION · **Class:** kept
- **Decision:** New repositories gitignore `.claude/worktrees/`, `target/`, `.gov-runtime/`; no long-lived in-repo worktrees. WSL stays non-sparse (sparse VHD is gated by Microsoft for potential data corruption); after large deletions, compact `ext4.vhdx` with `wsl --shutdown` then DiskPart or `Optimize-VHD`, preceded by `wsl --export` as a safety copy.

### DEC-060 — One agnostic Gov OS; projects differ only by overlay configuration
- **Status:** ACCEPTED (owner, 2026-09-29) · **Class:** kept
- **Decision:** There is one Gov OS release line for every project type. Projects differ only in their committed overlay configuration (path map, enabled capabilities such as code-intelligence languages or a research corpus, policy strengths). The choice of which product adopts first is a sequencing decision for dogfooding, not a variant. OQ-04 is deferred to the adoption stage.

### DEC-065 — Master rules (constitutional, every session, every Gov OS)
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER, grounded in Framework v4.1.2 §23–25, §36–39, §52–54 and Contract v3 H, I, K, L, O3 · **Class:** kept (items changed: MR-1..MR-6)
- MR-1 Specification first: discovery Q&A between agent sessions and the human customer closes a spine or feature specification (26-dimension readiness; silent N/A invalid).
- MR-2 Closed specifications generate the WBS: tasks, dependencies, order, roles; readiness gaps generate tasks; no production task is READY before its specification's required cells are satisfied.
- MR-3 Every task carries KPIs; an independent, freshly spawned test designer writes the acceptance tests from them before implementation; the implementer's allowed paths exclude the acceptance tests; builder tests are regression evidence only.
- MR-4 Discovery, impact (CIT-P), execution (CIT-E), audit and `gov doctor` are distinct functions.
- MR-5 The Gov OS works as a virtual software company of role agents; models are replaceable workers.
- MR-6 The human is the customer and final authority (L5): decision packages in the active chat, ranked and batched, non-blocking for independent branches, answers recorded in git.
- These rules go verbatim into Charter v5 and apply to the Gov OS's own development from S1.

### DEC-066 — Organisation layer and the five distinct functions
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER + SUGGESTION (mechanism) · **Changed by:** DEC-094 (Wave 2 roster) · **Class:** kept (items changed: guard-enforced allowed paths superseded §2.2)
- **Decision:** Roles are subagent definitions generated by rulesync from kernel role files plus a project roster; each carries purpose, allowed-path pattern, tools, model tier, authority level and handoff format. Wave 1: orchestrator, product/specification, independent test designer, engineer, independent auditor. Wave 2: architecture, frontend, backend, database/data, integration/API, DevOps/SRE, security, performance, UX, typed handoffs. Wave 3: research, AI/ML, data author, change controller, memory/knowledge, tooling, release, claims/concurrency. `gov doctor` (installation health), discovery skill + `gov readiness`, `gov impact` (CIT-P), OpenSpec apply/archive + `gov close` (CIT-E), and the audit skill with an Independent Auditor role are separate.

### DEC-069 — Test independence enforced mechanically
- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** SUGGESTION, implementing MR-3 · **Class:** kept (items changed: guard enforcement superseded §2.2; landing checks who wrote tests (§4.4))
- **Decision:** Acceptance tests live under `tests/acceptance/` and are written only by the Independent Test Designer role from the task's KPIs and the specification. The implementer role's allowed paths never include them (default-deny guard, DEC-041). An implementation task becomes READY only when its acceptance tests exist. `gov close` runs them.

### DEC-074 — S0b2 decisions and the owner's answers (2026-09-30)
- **Status:** ACCEPTED (owner) · **Class:** kept
- **Bake-off (fixed rules):** retrieval **R1** (carried FTS5 + sqlite-vec + Qwen3-Embedding-0.6B via Ollama + Qwen3-Reranker-0.6B + RRF; hit@5 85 vs 76, 0.24 s vs 28 s, 2.2 vs 5.1 GB); code intelligence **C1** codebase-memory-mcp 0.11.0 (20 MB peak; qual-B probe 19.7 MB, 7.4 s, 47 MB index); tasks **T3** wedow/ticket v0.3.2, vendored into the kernel template (sha256 `408f2c11…`) + claim glue; decisions **D2** MADR + check-jsonschema + checker. Supersedes DEC-013 (`br`) and the Backlog.md choice in architecture v0.2/v0.3.
- **Owner answers:** Q1 stack Balanced · Q2 ticket · Q3 reranker accepted for W1, lighter replacement spiked in W2 (5.6 GB is disk; ~2.2 GB RAM and ~1.2 GB VRAM only while a query runs) · Q4 Ollama on demand, 5-min idle unload · Q5 Superpowers: copy three skills (test-driven-development, systematic-debugging, verification-before-completion) through rulesync; not the plugin and not subagent-driven-development (conflicts with MR-3 and OpenSpec, and adds a foreign SessionStart hook) · Q6 adapters for Claude Code + AGENTS.md from one rulesync source, version pinned · Q7 rulesync owns `.claude/`; OpenSpec and vendored skills registered as rulesync sources · Q8 content-based secret filter before every indexer, ours and codebase-memory's (W1 gate) · Q9 deny rules for `.env`, `.pem`, `.key`, secret config · Q10 codebase-memory wrapped per repository (private home under `.gov-runtime/`, so `list_projects` sees only its own index) · Q11 the four LITE forms accepted · Q12 private GitHub repository, push `main` only · Q13 no GitHub Pro: CI advisory · Q14 the independent S0b1 author patches both tiers' TypeScript defects and re-verifies the oracle · Q15 scale probes on `~/EXAMIN APP` and `~/workspace` before Wave 2.
- **S0b2 facts:** 6 PASS, 5 PARTIAL, 0 FAIL, 1 BLOCKED (I-09, closed afterwards by the operator: skill sizes 2,389 / 2,360 / 899 / 8,089 / 795 tokens). Stack ≈ 11.9 GB disk, one on-demand daemon, no Docker, VRAM peak ≈ 5.2 of 16 GiB, ≈ 10.3 GB RAM worst case with the IDE. Housekeeping done: Ollama stopped, probe and its index deleted, rejected tools uninstalled.

### DEC-085 — Readiness: profile → required cells; no defaulted N/A; spines close at FULL
- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P1-C option (a) with one addition ·
  **Amends:** DEC-005 (readiness reduction) · **Class:** kept
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
  measurement, DEC-026 for Wave 1 · **Class:** kept
- **Decision:** Governance tokens are the tokens of text the Gov OS injects or returns: instruction files, the
  SessionStart packet, hook output, `gov` output, governance MCP tool definitions, and checkpoint and close records,
  counted deterministically per ticket by the `gov` CLI. The denominator is the ticket's fresh input plus output tokens,
  read from the harness's local session logs by ccusage. Cache reads are reported separately and are not in the share.
- **ccusage** is installed and pinned by the orchestrator under DEC-083's install rule and is a Wave 1 prerequisite.

### DEC-087 — CI scope on the hosted runner
- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P2-E option (a) · **Refines:** DEC-075 · **Class:** kept (items changed: gitleaks in CI superseded §2.11)
- **Decision:** GitHub Actions (G4–G5, advisory) runs the deterministic checks only: schemas, `gov check` G0–G2,
  readiness, the decision checker, the ticket DAG, `openspec validate --strict`, gitleaks, rulesync drift, and tests that
  need no local models (lexical fallback; codebase-memory is a static binary). Tests that need local models run in the
  pre-push gate (G3) and produce an evidence record bound to the head commit; CI checks that it exists and matches the
  head commit. The carrier of that record (for example a git note or a commit) is left to the CI ticket's design.

| Version | Date | Change |
|---|---|---|
| 0.13 | 2026-09-30 | S1 round 1: DEC-083 (ratification; DEC-040 amended), DEC-084 (MR-3 bootstrap), DEC-085 (readiness profiles; spines at FULL), DEC-086 (governance share), DEC-087 (CI scope). |

### DEC-089 — MR-2 holds from Wave 1: every required open readiness cell has a linked gap ticket
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-2 option (a) · **Class:** kept (items changed: Wave 2 `readiness --generate` folds into `gov discover` (W2-36))
- **Decision:** In Wave 1 the planning skill creates one linked ticket (class discovery, data, research or test-design)
  per required open cell, and `gov check` fails a specification with an unlinked required open cell. Wave 2 automates
  the generation with `gov readiness --generate`.

### DEC-090 — The adoption transaction A0–A11 in Contract v4
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-3 option (b) · **Refines:** DEC-006 · **Changed by:** DEC-741 · **Class:** kept (items changed: Wave 1 lite split history (DEC-741))
- **Decision:** CAP-44 states A0–A11 with one evidence record per stage and the three final verdicts
  (ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS, NOT_ADOPTED_HEALTHY). Wave 1 (`gov adopt --lite`) delivers A0–A4,
  A6 and A8 with a safety baseline and a rollback point per batch, **and A5**: an independent review of the path map
  before any move, by the Wave 1 Independent Auditor role. The independent gates A7, A10 and A11 are Wave 3 with CAP-47;
  the verdict is issued from Wave 3.

### DEC-091 — Hierarchical (parent-child) retrieval in Wave 1
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-4 option (a) · **Consistent with:** DEC-080 · **Class:** kept
- **Decision:** Chunk records carry `parent_id` (section level for documents, function/module level for code), and
  `gov retrieve` expands a child hit to its parent within the bundle budget and names the expansion. Both are Wave 1.

### DEC-093 — Decision packages: at most five at a time; P1 may bypass the cap
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-6 option (a) with an addition · **Changed by:** DEC-220 (which packages reach the owner) · **Class:** kept
- **Decision:** Decision packages are ranked P1–P3 and asked at most five at a time. A P1 package may bypass the cap.

### DEC-102 — Experiments are part of discovery
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package) · **Class:** kept
- **Decision:** Research and experiment tasks (spikes, and tool compatibility and performance trials like S0a and
  S0b2) are a normal part of discovery and can run at any point in development. They run in sandboxes outside
  production paths and produce an evidence record: what was tested, how, the results and a verdict. Their code is never
  promoted except through the normal cycle. Their results change a closed specification only through CIT-P.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

### DEC-103 — The order of specification work
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package) · **Class:** kept
- **Decision:** Specification work runs in this order: discovery and research, then scenarios, then representative
  data, then UX for any feature with a user interface, then acceptance tests, then implementation. The owner reviews
  scenarios and UX designs, not test code.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

### DEC-105 — Evidence-triggered change
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, in chat to W1-BUILD (no package) · **Class:** kept (items changed: CIT-P for kernel text superseded §3.5)
- **Decision:** When an experiment or finding contradicts a closed specification, a CIT-P opens. The impact assessment
  shows the affected specifications, decisions, tickets, tests and code, with three options and the cost of each: apply
  now; defer (record it and continue); or re-baseline (reopen the affected specification, re-plan from it, and retire
  the work it invalidates). The owner chooses; CIT-E records what was done. A closed specification means "ready to
  build", not "frozen", and every version is kept.
- To be carried into Contract v4 by a Gov OS spec change before the affected tickets' acceptance tests are written. The
  orchestrator does not change the Contract or any ticket now.

### DEC-127 — Where the tool-registry schema and the registry live
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-BUILD DP-4 option (a) · **Amends:** DEC-121 (its fallback) · **Class:** kept
- **Decision:** The registry schema stays in the kernel template at the path W1-04's ticket names
  (`template/governance/kernel/schemas/tool-registry*`). The registry itself is per-repository project data at
  `governance/project/tool-registry.yaml`. W1-04 ships no registry file; W1-06 creates it at the first install.

### DEC-136 — Probe findings feed the independent suite
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER · **Refines:** DEC-069 · **Class:** kept
- **Decision:** When the orchestrator's review finds a case the acceptance tests miss, it passes the case to the next
  test design batch as a described behaviour, never as code. The test designer decides from the specification whether
  it becomes an acceptance test, and reports when a finding reveals a specification gap. Builder tests stay regression
  evidence only.
- **First use:** the twelve cases of the W1-03 review go, described as behaviours, into the orchestrator's next
  `TEST_DESIGN_REQUEST`.
- To be carried into Contract v4 by the post-bootstrap spec change.

### DEC-165 — The upstream lesson loop, in a lite form (Wave 3)
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Reverses:** DEC-053 Q7, for framework lessons only · **Amends:** DEC-156 (one path outside the repository), Charter v5 §7 (non-goal row) · **Class:** kept (items changed: gitleaks scan of lesson packets superseded §2.11)
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
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Under:** DEC-102, DEC-103 · **Class:** kept
- **Decision:** `gov discover <question or feature>` is the entry point to discovery. It opens a discovery ticket,
  runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose
  evidence records, with measured numbers, back the answer. Plain language works the same way.

### DEC-167 — "What's the impact of X?" triggers the impact assessment
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Under:** DEC-105 · **Class:** kept
- **Decision:** "What's the impact of X?" asked in plain language triggers the impact assessment: `gov impact` from
  Wave 2; in Wave 1, an OpenSpec proposal plus `gov closure`.

| Version | Date | Change |
|---|---|---|
| 0.27 | 2026-10-03 | S2 repair after the S2-A round-1 audit: DEC-163 (DP-1: a minimal research role in the Wave 1 roster, delivered with W1-46; installs only inside its experiment folder, enforced by the sandbox's write fence; research allowlist of DEC-158), DEC-164 (DP-2: subagents inside a sandboxed worker session and `excludedCommands` are open residuals, added to EXP-002; the launcher sets no `excludedCommands`), DEC-165 (the lite upstream lesson loop, Wave 3; reverses DEC-053 Q7 for framework lessons only), DEC-166 (`gov discover`, Wave 2), DEC-167 (a plain-language impact question triggers the impact assessment). |

### DEC-182 — Commit trailers go in the final trailer block, with `git commit --trailer`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, at W1-45's close · **Under:** DEC-097 · **Class:** kept
- **Decision:**
  - From now on every commit puts `Task:`, `Implements:` and `Role:` in the final trailer block, using
    `git commit --trailer`. Git reads trailers only from the last paragraph of a commit message.
  - Checks that read trailers fall back to the message body for commits made before 2026-10-03.
  - History is not rewritten.
  - The rule is added to the rules of `docs/plan/WAVE_1_WBS.md`.

| Version | Date | Change |
|---|---|---|
| 0.33 | 2026-10-03 | Owner decisions at W1-45's close: DEC-179 (a fail-open guard default is a defect; W1-47 makes it fail closed), DEC-180 (the launcher's worker settings deny `Edit` on `.gov-runtime/**` except `scratch/**`; W1-46), DEC-181 (opaque Bash writes and `ln` into `.gov-runtime/` stay a residual in the orchestrator's own session), DEC-182 (trailers in the final block with `git commit --trailer`; checks fall back to the body for commits before 2026-10-03). |

### DEC-185 — KD-1: every `gov` command loads the `governance/project/` files it knows; an invalid one is `CONFIG_INVALID`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-07 package KD-1 option (a), without a new `overlay.yaml` · **Class:** kept
- **Decision:**
  - Every `gov` command loads the `governance/project/` files it knows: `path-map.yaml` now, the other overlay
    files as their tickets add them. There is no new `overlay.yaml`.
  - A missing file is not an error. An invalid one gives exit 1 with `CONFIG_INVALID`, naming the file and the key.
  - A minimal path-map schema lives under `src/gov/config/` until W1-08 supplies the real one and replaces it.

### DEC-186 — KD-2: check declarations are YAML in the kernel template; `gov check --list --json` is built at W1-07
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-07 package KD-2 option (a), in the kernel template · **Class:** kept
- **Decision:**
  - Check declarations are YAML files under `template/governance/kernel/checks/*.yaml`, with `id`, `family`,
    `tier`, `severity` and `command`.
  - `gov check --list --json` is built at W1-07. Running checks stays `NOT_IMPLEMENTED` until W1-26.
  - `template/governance/kernel/checks/**` joins W1-07's `allowed_paths`, in its own commit with the trailer
    `Task: DAEO-drvn`.

### DEC-199 — W1-06 DP-5: the sha256 of a vendored folder is a digest of its committed files
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-06 package DP-5 option (a) · **Extends:** DEC-196 · **Class:** kept
- **Decision:**
  - The Superpowers entry's `sha256` is a digest of the committed vendor folder: the sha256 of the sorted lines
    `<sha256 of the file>  <relative path>` over every file under `template/governance/kernel/vendor/superpowers/`.
  - A test and `gov doctor` recompute it offline.
  - This widens DEC-196 to vendored folders.

### DEC-205 — Headless workers start with the absolute path `~/.local/bin/claude`
- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1-48 install package · **Amends:** DEC-183 (the command's first word) · **Class:** kept
- **Decision:**
  - A second `claude` is on `PATH`: `/mnt/c/Users/usain/AppData/Roaming/npm/claude`, a Windows-side npm install
    reached through WSL's `PATH`, listed after `~/.local/bin/claude`.
  - Every headless worker is started with the absolute path `~/.local/bin/claude`, never a bare `claude`, so that a
    changed `PATH` can never start the Windows copy.
  - The Windows copy is recorded in `governance/project/bootstrap.md` as noted, not removed. It is outside WSL and
    the owner's choice.
  - W1-48's test designer adds a check that the pinned CLI is the one at `~/.local/bin/claude`.

### DEC-220 — Delegated decisions
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v3, section 6) · **Under:** MR-6 · **Amends:** DEC-093 (which packages reach the owner) · **Changed by:** DEC-416, DEC-974 · **Class:** kept (items changed: guard, containment and install exclusions superseded §2.2)
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
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v3, section 8 and brief A1) · **Under:** MR-3, DEC-135 · **Class:** kept
- **Decision:**
  - FULL: thorough. STANDARD: every KPI line's success and failure, plus the key edge cases. LITE: one test per KPI
    line.
  - No combinatorial expansion beyond what a KPI demands. Every covers id gets at least one test.

### DEC-225 — W1-08 DP-2: namespace paths and memory class
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-08 package DP-2 option (a) · **Under:** CAP-06.a, CAP-03.b · **Class:** kept
- **Decision:**
  - `paths` is a list of patterns in the language of ticket `allowed_paths`.
  - Every tracked path matches exactly one namespace.
  - `memory_class` is `governance` or `product`.
  - W1-08's five held packages (DP-3 to DP-7) follow DEC-220 where they qualify.

| Version | Date | Change |
|---|---|---|
| 0.42 | 2026-10-04 | Orchestrator prompt v3 and owner answers: DEC-220 (delegated decisions), DEC-221 (proportional tests), DEC-222 (archived sources for specification gaps, brief A4), DEC-223 (W1-47: DP-7 the static checks stay; DP-8 an empty list fails closed; a missing `held-out.yaml` means no rule, with a W1-27 KPI line; reading the holder files is an accepted residual), DEC-224 (W1-08 DP-1: the floor lives in `path-map.yaml`, drafted by a product-spec worker), DEC-225 (W1-08 DP-2: `paths` patterns, exactly one namespace per tracked path, `memory_class`). |

### DEC-227 — W1-08 DP-6: one shared definitions file holds every id grammar
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-6 option (a); test designer's confidence medium-high · **Class:** kept
- **Decision:** One shared definitions file under `template/governance/kernel/schemas/` holds every id grammar under
  a fixed name (`ticket_id`, `wbs_id`, `decision_id`, `lesson_id`, `record_id`), and no other schema writes an id
  `pattern` of its own; the record schemas refer to it.

### DEC-231 — W1-46 DP-1: the command line of `gov launch`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-1 option (a); the WBS and the orchestrator prompt already write `gov launch <role> <ticket>` · **Under:** DEC-161 · **Class:** kept
- **Decision:** `gov launch <role> <ticket> [-- <arguments for the CLI>]`. The role and the ticket are positional;
  everything after `--` is passed to the CLI unchanged, which is how a headless worker gets `-p` and its prompt.

### DEC-236 — Two-level orchestration: the main orchestrator and a ticket lead per ticket
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, sections 3 to 5 and brief A5) · **Under:** MR-5, DEC-096, DEC-156 · **Class:** kept
- **Decision:**
  - The main orchestrator runs the wave: it chooses and claims tickets, starts a ticket lead for each, merges and
    re-verifies, makes delegated decisions (DEC-220) and brings the owner the rest. It reads only a lead's final
    summary, never its workers' output.
  - A ticket lead runs the ticket loop for one ticket in that ticket's worktree, as `GOV_ROLE=orchestrator` with
    the ticket in `GOV_TICKET`. It starts the workers, holds that ticket's loop count and never discloses it.
  - A lead never edits `.tickets/`, the decision register or `bootstrap.md`, never merges into `w1/integrate` and
    never pushes. It returns DONE, PACKAGES, ESCALATION or LEAD_CHECKPOINT.
  - Tickets, claims, the register and `bootstrap.md` are edited only by the main orchestrator, in the main tree.

### DEC-262 — The owner's reading of CAP-24 for vendored skills
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1-37 question left open by DEC-245, option (a) · **Under:** CAP-24, DEC-245, DEC-246 · **Class:** kept
- **Decision:**
  - For a vendored skill, the version recorded beside it (`vendored.yaml`) satisfies CAP-24. The copies stay
    byte-identical to upstream.
  - This is the owner's reading of CAP-24 for vendored skills; the Contract's text is not changed.
  - It is noted in W1-30's brief: `gov close` reads a vendored skill's version from the record beside it.

### DEC-264 — The PreCompact hook never blocks; it appends a generated state block
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the gap reported with DEC-258 · **Amends:** DEC-258 (no compaction is blocked; "current" is no longer a 30-minute age) · **Under:** DEC-248, DEC-250, CAP-37.g · **Class:** kept
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

### DEC-274 — W1-10 DP-1: what a record is, and what an invalid one does to a load
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-1 option (a); confidence medium · **Under:** DEC-239, CAP-13.a · **Class:** kept
- **Decision:**
  - A record is any tracked Markdown file whose frontmatter has an `id`. It needs `id`, `type` and `status`
    (DEC-239). An unreadable or incomplete one is listed in the load's `invalid` by path, and the load continues.
  - Known consequences, recorded as residuals for later tickets: the charter, the contract and the plan have `id`
    and `status` but no `type` and are reported invalid; the seven kernel templates load as records with
    placeholder ids; decisions are headings in the register, not files, so every `DEC-…` reference is dangling
    until decisions are records; two files with one id both load.

### DEC-279 — W1-25 DP-2: the checkpoint's schema, keys and arguments
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-2 option (a); confidence medium-high on the schema, medium on the names · **Under:** CAP-37.a, CAP-13.b, DEC-229 · **Class:** kept
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

### DEC-282 — W1-25 DP-6: the resume brief, the family check, and one real session
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-6 option (b); confidence medium-high for the check, medium for the session · **Under:** CAP-20.a, CAP-37.f, CAP-38.b, DEC-232 · **Class:** kept (items changed: real-session test and family check history)
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

### DEC-292 — W1-09 DP-2: the claim convention
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-2 option (a); confidence medium-high, medium for the closed ticket and `in_progress` · **Under:** CAP-23.a, DEC-116 · **Class:** kept
- **Decision:**
  - The lock is `.tickets/.claims/<ticket id>`, created with O_EXCL, a text file naming the holder. The holder is a
    string the caller gives, by convention `<role>:<session>`.
  - Only the holder releases. Nothing expires: a dead session's claim is released by whoever names its recorded
    holder, which is the main orchestrator's job.
  - A closed ticket cannot be claimed (`TICKET_CLOSED`). A lock and `status: in_progress` both count as claimed.
  - Left open and untested: whether `claim` also sets `in_progress`; a second claim by the same holder; an empty
    holder.

### DEC-300 — W1-09: the acceptance tests folder must lie below `tests/acceptance/`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 reviewer finding H2 and its repair; confidence high · **Narrows:** DEC-293 · **Under:** DEC-069, CAP-31.c · **Class:** kept
- **Decision:** The folder that makes a ticket READY (DEC-293) counts only if, with links resolved, it is a
  directory inside the project and strictly below `tests/acceptance/`. An absolute path, `.`, `..`, `src`, `.git`,
  `tests/acceptance/` itself or a link leading outside the project does not count. A path naming another ticket's
  folder, and an empty folder, still count; both are residuals.

### DEC-305 — W1-12 DP-4: the readiness record is YAML
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-4 option (a); confidence medium · **Under:** CAP-30.a · **Class:** kept
- **Decision:** The readiness record is `readiness.yaml`, artifact id `readiness`: one entry per row with `n`, `key`,
  `state`, `evidence`, `reason` and `gap_ticket`. A fresh record has all 26 rows `MISSING`: empty is invalid, N/A is
  never a default, and the other states need content.

| Version | Date | Change |
|---|---|---|
| 0.65 | 2026-10-04 | Delegated under DEC-220: DEC-302 (W1-12 DP-1: the schema carries the YAML's own keys), DEC-303 (DP-2: W1-12 delivers `template/openspec/config.yaml`), DEC-304 (DP-3: the kernel `templates/openspec/` folder stays unused for now), DEC-305 (DP-4: the readiness record is YAML, fresh rows `MISSING`). DP-5 goes to the owner. |

### DEC-328 — W1-34 DP-1: a gate record holds its state in `status` alone
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-34 package DP-1 option (a); confidence medium · **Under:** CAP-34.d, DEC-308 · **Class:** kept
- **Decision:**
  - A decision package holds its gate state in `status` alone, with no second key: `PROPOSED` is open, `ACCEPTED` is
    answered, `DECLINED` is declined, `REVOKED` is revoked and `STALE` is stale. The template states the mapping.
  - The key that names the CIT a package belongs to is `cit`.
  - The READY rule (DEC-308) and W1-11's checker read the same value. One test pins the five values and the key.

| Version | Date | Change |
|---|---|---|
| 0.69 | 2026-10-04 | Delegated under DEC-220: DEC-328 (W1-34 DP-1: a gate record holds its state in `status` alone, `PROPOSED`, `ACCEPTED`, `DECLINED`, `REVOKED`, `STALE`; the CIT key is `cit`). |

### DEC-329 — W1-11 DP-1: the decision checker reads frontmatter and git, never prose
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-11 package DP-1 option (a); confidence medium · **Under:** CAP-51.a · **Class:** kept
- **Decision:**
  - The checker is deterministic: it reads frontmatter and git only. It does not read a decision's body for
    statements such as "superseded by DEC-003".
  - On the b-dev tier as planted it flags the overlapping ids across `docs/adr/` and `decisions/`. The other hazard
    classes (ACTIVE while superseded, a supersession cycle) are tested on a clone where the test writes the link the
    hazard describes, because HZ-B-03 states its link only in prose and the tier holds no cycle.
  - G-04 is in the S0b2 output and was not read. If it requires prose reading, this decision is revisited.

### DEC-332 — W1-46 DP-17: `gov launch` ends with the session's exit code
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-17 option (a); confidence medium · **Under:** DEC-317 · **Class:** kept
- **Decision:** `gov launch` ends with the exit code of the session it started, whatever it is, and prints no
  envelope then (`CHILD_EXIT_CODE`), as built. A caller that needs to tell a launcher refusal from a session's own
  code 1 to 4 reads the output: a refusal prints the envelope.

### DEC-381 — W1-19 DP-6: a namespace that is not embedded never reaches the vectors
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-19 package DP-6 option (a) · **Settles:** the DEC-289 residual on `embedding_policy` · **Under:** CAP-10.a, CAP-03 · **Class:** kept
- **Decision:** A namespace whose `embedding_policy` is `not embedded` never reaches the vectors. This holds before
  any live index is built.

### DEC-388 — W1-19 DP-8 and DP-9: an unknown `embedding_policy` is not embedded; hit@5 follows S0b2's stated method
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-19 packages DP-8 option (a), confidence medium-high, and DP-9 option (a), confidence medium · **Under:** DEC-380, DEC-381, DEC-383, CAP-09 · **Class:** kept (items changed: DP-9 (hit@5 method) history)
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

### DEC-391 — W1-20 DP-1 to DP-7: the interface, the ids, the depth, the code facet and the gaps of `gov closure`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-20 packages DP-1 (a), DP-2 (a), DP-3 (a), DP-4 (a), DP-5 (gap reasons), DP-6 (a), DP-7 (b); confidence medium to high · **Under:** CAP-57.a, CAP-09, DEC-033, DEC-034, DEC-035, DEC-080, DEC-317, DEC-322, DEC-344 · **Changed by:** DEC-393, DEC-396 · **Class:** kept (items changed: amended by DEC-393, DEC-396)
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

### DEC-409 — Lifting a freeze requires the owner in person: no Claude Code ancestor, an interactive terminal with a typed one-time code, and a guard rule on the lift form
- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Amends:** DEC-365, DEC-407 (its ancestry rule is replaced), DEC-367 as the owner named it · **Under:** DEC-402, DEC-404, CAP-05.a · **Changed by:** DEC-428 (the one manual check before W1-50 closes) · **Class:** kept (items changed: (3) the guard rule on the lift form superseded §2.2)
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

### DEC-420 — An authentication or access error stops the launching of leads: `AUTH_REQUIRED`
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER · **Amends:** DEC-250 (one more stop) · **Under:** DEC-235, DEC-250 · **Class:** kept
- **Decision:**
  - If a session or a lead fails with an authentication or access error (401, 403, "Failed to authenticate",
    "access grant"), the orchestrator does not retry in a loop.
  - It stops launching leads, writes its checkpoint, and stops with `AUTH_REQUIRED`, so that the owner knows to
    sign in again.
  - After the owner restores access: a one-line headless probe first; if it works, one lead as a test, then the
    others, each from its branch's last commit.

### DEC-430 — The owner's reading of MR-3 (MWA-02)
- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, option (a) on the mid-wave audit's MWA-02 · **Under:** MR-3, DEC-069, DEC-136 · **Class:** kept
- **Decision:**
  - The core tests for every KPI line are written by the independent test designer before implementation. Cases
    found in review may be added afterwards, by the test designer only, red before their fix (DEC-136).
  - This is how MR-3 is met, not an exception to it.
  - The exit auditor is told so in W1-43's brief.

### DEC-438 — W1-26: a family with no registered check is never green
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-06) · **Basis:** `gov check --json` run by the orchestrator on W1-26's branch at `be229cdd`: four of the seventeen families had no registered check and were reported green · **Under:** DEC-425, DEC-413, DEC-436 · **Class:** kept
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

### DEC-444 — The hooks' automatic checkpoints go to the ignored scratch folder; deliberate checkpoint records are committed
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** W1-29's residuals: the hooks wrote untracked files under `docs/checkpoints/` in every session with a ticket · **Under:** DEC-264 · **Class:** kept
- **Decision:**
  - The checkpoints the hooks write by themselves go to `.gov-runtime/scratch/checkpoints/`, which is ignored.
  - Only deliberate `gov checkpoint` records go to `docs/checkpoints/` and are committed.
  - The orchestrator chooses the ticket for the change. It chose W1-29, reopened for one follow-up round in
    its own paths.

### DEC-448 — `gov doctor`: registered tool locations, historical records, one rebuild, and the Claude Code drift
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** `gov doctor` on this repository: Node 18 found against 22 pinned, `openspec` and `ccusage` not found, 180 references to moved paths, a stale index, Claude Code drift · **Under:** DEC-202, DEC-210, DEC-440 · **Changed by:** its one-off limit superseded by DEC-477 (its other parts stand) (shown by DEC-825, 2026-10-19) · **Changed by:** DEC-456 (the set of historical records) · **Class:** kept (items changed: (one-off limit) history, superseded by DEC-477)
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

### DEC-452 — Doctor looks under every registered PATH prefix before PATH, and a tool it cannot verify fails
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07) · **Basis:** the orchestrator's reading of W1-27's code and of `gov doctor` run on this repository after DEC-448 was built: `openspec` and `ccusage` are found under the prefix their registry entries carry, Node is not (its entry's install command is the `nvm install` line and carries no prefix; the place is only in a free-text note), `socat` passes with no version read and no hash match, and one case asserted a key name · **Under:** DEC-202, DEC-425, DEC-440, DEC-448 · **Class:** kept
- **Decision:**
  - Doctor looks for a tool first under its own registry entry's PATH prefix, then under every PATH prefix that
    any entry of the registry carries, in the registry's order, and only then on PATH. This is the reading of
    DEC-448's "the PATH prefix of DEC-202" for a tool whose own entry carries none; with it Node 22 is found
    where it is installed, and the registry is not changed.
  - A tool passes only when the version read equals the pin, or, where no version can be read, when the file's
    hash equals the pinned hash. A tool for which neither can be established fails, with the reason; so does a
    version command that errors or times out (DEC-440: an error in a measurement is a failure).
  - Both are fixed test-first (DEC-136) inside W1-27, without a further review round (DEC-413).

### DEC-454 — What `gov close` measures where its KPI lines left the mechanism open
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; the owner may overturn any point) · **Basis:** W1-30's second return (six packages for the owner) and the orchestrator's reading of the code against each KPI clause (DEC-449): the disposition of every finding was a constant, a context that could not be built was replaced by a hash of the ticket file, "the regression tests" were two folders of unit tests, the reviewer's "wrote nothing" was the record's own word, a fourth iteration had no owner's decision to wait for, and the stale-evidence rule measured nothing · **Under:** DEC-096, DEC-136, DEC-137, DEC-413, DEC-425 · **Changed by:** DEC-908 (for one part): an identical refusal reuses and names its repair ticket (W2-07's KPI 10, W2-M252). · **Changed by:** DEC-868 (items 1 (b) and 3), DEC-899 (P-IS-4 (a)) · **Class:** kept (items changed: repair ticket and disposition arguments superseded §4.2)
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

### DEC-462 — A designer's brief states behaviour and sources only
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report: the orchestrator's designer briefs for W1-27 and W1-30 named private identifiers of the implementation · **Under:** MR-3, DEC-069 · **Class:** kept
- **Decision:** Confirmed stopped. A brief for a test designer states behaviour and sources, never the names of
  the implementation's private parts.

### DEC-463 — Decisions recorded late are accepted; from now on the record comes first, and `gov check` flags a commit citing an unrecorded decision
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, answering the compliance report: DEC-391, DEC-417, DEC-437, DEC-440, DEC-450, DEC-452 and DEC-455 were recorded after the work they authorise · **Class:** kept (items changed: (1) history)
- **Decision:**
  - Those seven are accepted as recorded late.
  - From now on a decision is recorded before the change it authorises.
  - A KPI line is added to W1-26 (or the ticket the orchestrator chooses) so that `gov check` flags a commit
    that cites a decision id missing from the register at that commit. The orchestrator chooses W1-26 and
    reopens it for this line, test first.

### DEC-468 — The six skills OpenSpec writes beside its commands are registered rulesync sources, like its commands
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** W1-38's test designer measured with rulesync 24.0.0 that `generate --delete` removes every file under `.claude/commands/` and `.claude/skills/` that is not a registered source, and that `openspec init --tools claude` (OpenSpec 1.13.2) writes six commands and six `openspec-*` skills. The ticket's failure line reads "generate --delete removes OpenSpec or vendored skills"; DEC-074 (question 7) makes rulesync the holder of what OpenSpec writes. Registering the commands alone would let `--delete` remove the six skills. · **Class:** kept
- **Decision:**
  - The registered rulesync sources hold what the registered OpenSpec version ships, unchanged: its six commands and its six skills. A text written for the ticket in their place is not a source.
  - The acceptance cases compare the generated files with what the installed, registered OpenSpec writes; an OpenSpec that is absent or of another version fails those cases with that reason.
  - Recorded before the change (DEC-463): the designer's cases for the six skills and the engineer's sources follow this entry.

### DEC-469 — The change that moves the registered OpenSpec or rulesync version refreshes the registered sources in the same change
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the cases of DEC-468 turn red when the tool registry names a new OpenSpec version and the sources still hold the old texts; no source named who refreshes them. · **Class:** kept
- **Decision:**
  - The ticket that changes the `openspec` or `rulesync` entry of the tool registry refreshes the registered sources from that version in the same change, in a temporary folder outside the repository (nobody runs a writing rulesync command in the repository), and copies the result in.
  - Where a project keeps its check declarations once adopted (`template/governance/kernel/checks/` today, `governance/kernel/` after adoption) is not decided here: W1-39 settles it.

| Version | Date | Change |
|---|---|---|
| 0.117 | 2026-10-07 | Two delegated decisions on W1-38: DEC-468 (OpenSpec's six skills are registered rulesync sources, like its six commands), DEC-469 (the change that moves the registered version refreshes the sources). Next free id: DEC-470. |

### DEC-473 — The decision-citations check knows both register forms (W1-26, package P-1)
- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** DEC-463; the test designer's package P-1 on W1-26's follow-up. · **Class:** kept
- **Decision:**
  - A decision is recorded either as a decision file, or as an entry of a register file that the project names in one line of configuration under `governance/project/`. With no register file named, decision files alone count. No path of this repository goes into the kernel.
  - Heading grammar of a register file: a level-3 heading `### DEC-<digits>` at the start of a line, followed by a space, a colon or a dash and the title. A heading inside a fenced code block does not count.

### DEC-479 — The register file and the base commit of the decision-citations check are two optional keys of the project's path map
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** DEC-473 and DEC-474 order "one line of configuration under `governance/project/`" without naming the file. W1-26's test designer (commit `ac952490`) found no source that names it and settled on the path map: DEC-185 refuses a new overlay file and has commands load the `governance/project/` files they know, the path map first; DEC-224 and DEC-230 already put project data there under top-level keys. · **Class:** kept
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

### DEC-488 — W1-39: one comparison of a project with its lock, owned by W1-39; the update procedure is in the template's messages and the lock's header; adapter generation is a documented step after `copier copy`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; told to the owner, who may replace it) · **Basis:** the W1-39 lead's packages P-1 (in part), P-3 and P-4 (`log/W1-39-lead-run1.json`), each with the lead's recommendation. The parts of its packages that change a ticket's allowed paths (P-1's call site in `gov doctor`, P-2, P-5) are the owner's and are not decided here. · **Class:** kept
- **Decision:**
  - **The comparison of a project with its lock is built once, by W1-39, as a public function of its own code:** given a project, it answers match or drift, the drifted files, and the reason where it could not compare. It never answers match without having hashed: an absent or empty manifest is not a match; a kernel file that the manifest does not list is drift, named; the lock's template tag and commit are compared with the answers file. `gov doctor` is to call it (where and under which ticket: with the owner).
  - **Only `__pycache__/` folders are left out of "a kernel file the manifest does not list".** Git-ignored files in general are not left out: an ignore rule is the project's to write, and a file hidden by one would escape the comparison.
  - **The update procedure is documented in two places that reach a product repository:** the template's messages after copy and after update, and a comment header of the generated lock.
  - **`copier copy` does not run the adapter generation.** Generating `.claude/`, `CLAUDE.md` and `AGENTS.md` from `.rulesync/` is a documented step after the copy, named in the procedure; an install does not fail where rulesync or Node is absent. W1-41's adoption runs or names the step.
  - Recorded before the change (DEC-463).

| Version | Date | Change |
|---|---|---|
| 0.125 | 2026-10-07 | One delegated decision on W1-39: DEC-488 (the lock comparison is W1-39's and never matches unhashed; only `__pycache__/` is left out; the update procedure in the template's messages and the lock's header; adapter generation a documented step). Next free id: DEC-489. |

### DEC-728 — `~/gov-os-runs/` is one durable scratch root; a session writes only in its own ticket's folder there (W2-50)
- **Status:** ACCEPTED (owner, 2026-10-16; the owner commits this entry with `Role: owner`) · **Under:** DEC-723, DEC-159, CAP-33 · **Basis:** · **Changed by:** DEC-953 (item 2) · **Class:** kept (items changed: (2) own-folder write fence superseded §2.2)
  - DEC-723 moves writing work to clones under `~/gov-os-runs/<W2 id>/`, but nothing lets a session write there.
  - In Wave 1 both the guard and the launcher's sandbox refused writes outside the repository except in the temp folder (`src/gov/guard/decide.py`; the launcher's sandbox write list holds only the session's temp folder).
  - Clones under `/tmp` are lost on a reboot (W2-M355).
- **Decision:**
  1. **A Track A ticket, W2-50, in layer 2** (FULL, engineer; the independent test designer first; a probe after green). It makes `~/gov-os-runs/` one durable scratch root, in the guard and in the launcher's sandbox write list.
  2. **A session of any role writes only under `~/gov-os-runs/<its own ticket>/`.** Another ticket's folder, the root itself, and any path outside it stay refused.
  3. **Nothing there is ever indexed** by this repository's stores, and the secrets-indexing check never scans it. A product clone adopted there keeps its own store inside the clone; that store is not this repository's (W2-27).
  4. `~/gov-os-workbench` and `~/gov-os-worktrees` stay refused as before (DEC-723).
  5. **The change loosens the guard,** so it goes through CIT-P with the owner's approval (CAP-33), like W2-09's change. This entry is the owner decision behind it.
  6. **Every ticket that clones into `~/gov-os-runs` depends on W2-50:** W2-14, W2-15a (and through it W2-15b), W2-24 and W2-27.
  7. **Until W2-50 closes, W2-26 clones into its session's scratch folder under `/tmp`.** Its results are committed to `docs/research/EXP-003/examin/`, so only the throwaway clone is volatile.

### DEC-732 — In a ticket worktree, tests and gov commands run that worktree's own `src/` (owner ruling; W2-H054)
- **Status:** ACCEPTED (owner, 2026-10-16; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-236, DEC-719, DEC-722 · **Basis:** `gov` is an editable install of the main tree's `src/`. W2-01's lead found that `env -u PYTHONPATH python3 -c 'import gov'` in a worktree loads the main tree's code, so a suite run in the prescribed form tests the main tree, not the ticket's change, unless the suite sets `PYTHONPATH` itself. The orchestrator checked that `PYTHONPATH=<worktree>/src` takes precedence over the editable install (`gov.__file__` then points into the worktree). · **Class:** kept
- **Decision:**
  1. **In a ticket worktree, every test run and every `gov` command used for verification runs that worktree's own `src/`:** `PYTHONPATH` is set, per command, to the worktree's absolute `src` path.
  2. **Each lead's verification shows it,** for example with `python3 -c "import gov; print(gov.__file__)"` under the same `PYTHONPATH`, pointing into the worktree; the output goes in the lead's return.
  3. **The rule is in every lead brief and every worker brief.** It is set per command, not in a session's environment, so the guard's own hooks keep running the code the session started under.
  4. **One full `gov rebuild` in the worktree before its verification**, under the same `PYTHONPATH`, with no worker running there (DEC-719: never `--no-embeddings`).
  5. **A Wave 2 row, W2-H054 (high), triaged into W2-21:** "a ticket worktree's tests and gov commands run that worktree's code, never the editable install's main tree". Added to `docs/plan/WAVE_2_LIST.md` §3.1 and `docs/plan/WAVE_2_TRIAGE.md` with this entry. It goes into W2-21's `list_rows` in a commit of its own (`Task: DAEO-1ahb`) once this entry is committed.

### DEC-740 — Charter v5 §1: one pilot adoption in Wave 2, before Release 1
- **Status:** ACCEPTED (owner, 2026-10-17; the owner commits this entry and the Charter's change with `Role: owner`, in the next batch) · **Under:** DEC-064, DEC-718, DEC-727, DEC-105 · **Basis:** · **Class:** kept
  - Charter v5 §1 said "Adoption into product repositories starts only after Release 1 (DEC-064)". The owner's Wave 2 decisions (DEC-712, DEC-714, DEC-718, DEC-727) plan a pilot adoption of an owner repository in Wave 2, but no entry amended the Charter.
  - W2-49's CIT-P found the contradiction (finding F-3). The orchestrator put it to the owner as P-W2-14 with the three options of DEC-105.
- **Decision (apply now, by amendment):**
  1. **The line in Charter v5 §1 now reads:** "Adoption into product repositories starts after Release 1 (DEC-064), with one exception: a single pilot adoption in Wave 2 (EXAMIN, DEC-718, DEC-727), allowed only after Track A passes and is audited (W2-25), on a pinned, hash-verified release, with independent verdicts on a copy (W2-28) and on the real repository (W2-30), the owner's go before the real repository is written, and the freeze and rollback in the owner's hands. Every other product repository waits for Release 1."
  2. **Nothing else in the Charter changes.** That includes its front matter and its `decisions` list.
  3. DEC-064 stands for every other repository.
- Next free id: DEC-741.

### DEC-772 — `gov release` is the owner's alone, from a plain terminal; the guard refuses a prefix in front of any `gov` command (P-W2-23)
- **Status:** ACCEPTED (owner, 2026-10-18; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-761, DEC-409, DEC-722 · **Basis:** P-W2-23; W2-16's run-2 review, finding R3-NAMED: from an auditor's session, `GOV_ROLE=orchestrator gov release` and `env -u GOV_ROLE gov release` wrote a release and a lock. · **Class:** kept (items changed: (1) kept §2.5; (2) guard prefix refusal superseded §2.2; (3) history)
- **Decision:**
  1. **`gov release` is owner-only, from a plain terminal,** like `gov approve` and the freeze lift: it refuses with a Claude Code process among its ancestors, with `GOV_ROLE` or `GOV_TICKET` set, or without a terminal, and asks for a typed one-time code. **This replaces DEC-761 item 1's line "`gov release` refuses unless the role is orchestrator, or the owner in a plain terminal".** It is W2-16's next round, and that round does only this (tests first, one review of that change); W2-16's allowed paths do not change.
  2. **And (b): the guard refuses a leading `NAME=value` assignment or an `env` prefix in front of any `gov` command:** a high row, W2-H060, triaged to W2-42 (the guard-holes ticket), not W2-16's.
  3. **W2-H059 (high, triaged to W2-44):** every role check that reads `GOV_ROLE` can be spoofed until a session's identity is bound to its launch.
- Next free id: DEC-773.

| Version | Date | Change |
|---|---|---|
| 0.235 | 2026-10-18 | Owner: DEC-768 (P-W2-26 (a): W1-42's claim commit `93bcb247` accepted history under DEC-717; W2-54 sorts the context packet's dropped list stably, gives the context check a declared time limit fitting its measured run, and adds the `audit-report` type exactly as W2-02 defines it (P-W2-28 (a), refined), after which the W1-43 record gets only the lines that type requires, its sha256 before and after recorded; then W2-53 closes again; no hard-block check weakened; W2-M367), DEC-769 (P-W2-27 (a): leads sandboxed in W2-21 after a feasibility test; the test designer writes only its own acceptance folder; the orchestrator unsandboxed), DEC-770 (a guard text-reading hole only an unsandboxed session can reach becomes a row once leads are sandboxed), DEC-771 (P-W2-22 (b): never-recorded sources to W2-17 and W2-18; W2-18 refuses `release: null`), DEC-772 (P-W2-23: `gov release` owner-only from a plain terminal with a one-time code, replacing DEC-761's orchestrator line, W2-16's next round and nothing else; the guard's refusal of a prefix in front of any `gov` command is W2-H060, for W2-42; W2-H059). Next free id: DEC-773. |

### DEC-782 — A read command may write the query-vector cache, and only that, under limits (P-W2-32 (a))
- **Status:** ACCEPTED (owner, 2026-10-18; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-379, DEC-768, DEC-773, DEC-757 item 6, DEC-766 · **Basis:** W2-54's run 2. · **Class:** kept (items changed: (4) history)
  - It stored query vectors in `.gov-runtime/query-vectors.db` (model, revision, text). Context-reproducibility turned green (128.67 s).
  - The write on read turned W1-21 ×4 ("a read command writes nothing") and W1-19 ×1 ("one shared store") red, against DEC-379 (`refresh=False` never writes).
  - No embedder setting removes the variation: `num_thread` 1 and 20, `seed` 42, 6 of 6 repeats differ.
- **Decision:**
  1. **(a).** A read command (`gov retrieve`, `gov context`) may write the query-vector cache. DEC-379 is amended for this one file only. The limits:
     - only that one derived cache file under `.gov-runtime/`, never anything authoritative;
     - keyed by model, model revision and a hash of the exact text;
     - atomic writes, safe when several sessions write at once;
     - bounded in size;
     - rebuildable from nothing.
  2. **Deterministic where the cache cannot be written.** In a sandboxed worker, whose `.gov-runtime` is read-only, the read still gives the same vector for the same text. A test shows it inside a launched, sandboxed worker too, not only in the orchestrator's session.
  3. **The W1-19 and W1-21 rewrites** change only the expectations that depended on the old, varying vectors, each with a `Rewrite-Reason:`.
     - No pass line or threshold is lowered.
     - A figure below its pass line is a red, not a rewrite.
     - Each rewritten case's figure is shown before and after.
  4. **Row W2-M370** (`gov context` asks retrieval only the first word of more than two letters of a ticket's title; W2-54's run 2) is recorded under this decision, for W2-04.

### DEC-803 — A risk that exists only when a feature is on is an entry criterion of the ticket that switches it on (standing)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-719, DEC-413 · **Basis:** F-A and F-B are reachable only once W2-08 installs the hooks. · **Class:** kept
- **Decision:** a risk that exists only when a feature is switched on becomes an entry criterion of the ticket that switches it on.

### DEC-815 — The closure depths per radius for Wave 2: 1, 3 and 8 hops (P-W2-45 (a); W2-L319)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; under DEC-817) · **Under:** DEC-035, DEC-391, DEC-812 · **Basis:** W2-37's P-2: `gov.closure.depth_of_radius` holds DEC-035's placeholder depths, read as hops by DEC-391 DP-3, in use since Wave 1 with no fault seen; W2-37's acceptance case asks that the depth's source be an owner decision or a measurement. · **Class:** kept
- **Decision:**
  1. **The owner sets the depth of each radius for Wave 2:** R0 and R1 one hop, R2 three hops, R3 eight hops (`gov closure` and `gov impact`). This entry is the depth's source: W2-37's `depth_source` names DEC-815, set in its resume (`src/gov/impact/readings.py`, in its paths).
  2. **The measurement of these depths is a Wave 3 row** (W2-L319, reworded).

### DEC-818 — The P1 decision package format, and the daily P2 digest (standing)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** MR-6, DEC-220, DEC-787, DEC-809 · **Basis:** OWNER, 2026-10-19: the owner and the owner's adviser must be able to decide a package without other context. · **Class:** kept (items changed: (1) retired as ceremony; (3) history)
- **Decision:**
  1. Every P1 package stands alone, in six parts: (1) the context in plain words, with its history and links; (2) what happened, with the evidence; (3) why it matters to the Gov OS's purpose; (4) the options, each with its consequence, cost and risk, and what it changes in the Contract, the specifications, the skills or the briefs; (5) the recommendation and its confidence, with the threat-model classification of any findings (DEC-809); (6) what it blocks, and what waiting costs.
  2. P2 items go to the owner in one daily digest, not one by one.
  3. It replaces, for P1 packages, the field list of the w2 prompt §7 ("question, why now, options, …"); the prompt says so (DEC-824).

### DEC-826 — P-S5: what each role loads, reads and writes
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-820, MR-3, MR-4, MR-5, CAP-38.c, CAP-38.f, DEC-460 · **Basis:** P-S5 (lens E F2 to F7, F11, F13, F14, F19; R1 to R6, R10). · **Changed by:** DEC-953 (item 2) · **Class:** kept (items changed: (1),(2),(3) kept; (4),(5) superseded §2.2; (6),(7) history)
- **Decision:**
  1. **Q1 (a):** the role is loaded at launch: `gov launch` starts the session as its role's generated agent or appends the role file's text, and W2-21's launch record holds the text's hash and version.
  2. **Q2:** the test designer reads the specification, the KPIs and the existing code it must work with, never the ticket's own implementation (DEC-820 (c)). Its independence also comes from order: tests are written before the ticket's implementation exists, and the launch record shows it. The skill, the template and A1 state this one rule, and the skill cites CAP-38.c.
  3. **Q3:** reviewers and auditors commit nothing (the lead commits a probe record, DEC-733; the orchestrator commits an auditor's report); automatic checkpoints are kept one subfolder per session.
  4. **Q4:** no read denials beyond DEC-820's four.
  5. **Q5:** governed sessions get a cleaned environment, no connectors, no user-level agents or skills, and no model-side memory; the remaining flags that drop the guard or add context are refused (W2-56).
  6. **Q6:** open until lens F reported. Lens F has reported (`docs/assessment/2026-10/F-models-context.md`); its proposal per role (model, effort, compaction threshold, subagent model) comes in the revised plan for the owner's decision (DEC-829).
  7. The KPIs this needs land in W2-21 and W2-56 (and the checkpoint code, keystone 4) through the revised plan, before they start (DEC-802).

### DEC-832 — The Charter's eight unplanned roles: four as skill packs the engineer loads, four to Wave 3 (plan §11 item 6; item 1a)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** Charter v5 §6, DEC-105 (defer, for four), DEC-829 items 4 (iii) and (iv), CAP-24.b, CAP-33 · **Basis:** OWNER, 2026-10-19: the plan's alternative, as skill packs rather than new governance roles · **Replaces:** the plan's recommendation to defer all eight. · **Changed by:** DEC-957 (the skill packs come in Wave 2) · **Class:** kept (items changed: (2) history)
- **Decision:**
  1. **Backend, database and data, integration and API, and security become skill packs,** not governance roles: method text that the engineer role loads at launch, through W2-60. They add no role, no guard entry, no permission and no path; a skill grants nothing on its own authority (CAP-24.b).
  2. **W2-33 stays in Wave 2, cut down to these four packs:** about 1.5 days of product-spec work, no new machinery. It is a kernel skill change, so it goes through CIT-P (CAP-33). It starts after W2-60 (which loads them) and W2-11 (one versioned source per skill), and it is admitted by this decision under DEC-829 (iii).
  3. **Architecture, frontend, DevOps and SRE, and performance are deferred to Wave 3** by this decision (DEC-105, defer).
  4. **W2-33's carded scope moves to Wave 3:** the test-execution and integration roles (CAP-22.c), the UX role and the typed handoff record (CAP-22.b), with their rows. CAP-22.b and CAP-22.c stay among the nine items DEC-841 moves.

### DEC-836 — Memory used, not just built: keystone 4's exit (item 1e)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-828, DEC-829 item 2 (4), CAP-37 · **Basis:** OWNER, 2026-10-19: memory used, not just built. · **Class:** kept (items changed: (1) superseded §5.5; (3) history)
- **Decision:** keystone 4 is done only when all three hold:
  1. **the orchestrator builds every brief with `gov context`;**
  2. **every lead and worker brief tells its agent to use `gov retrieve`** for what it needs to know;
  3. **usage is measured:** how many briefs and how many worker tasks used them, as section 7d of the quality check measured; reported at keystone 4's exit and in each daily digest from then on.
- The `gov retrieve` line goes into the briefs now (prompt v3, `LEAD-w2-common.md`). `gov context` is used for every brief once W2-04 has merged; before that, its packets are 42 to 168 times the ceiling (lens B F1), and the orchestrator records each brief it built without one. The count comes from the session records (W2-60) and, until they exist, from the session logs.

### DEC-837 — Resume in full, pulled forward into keystone 3: ticket W2-62 (item 1f)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; the kernel hook change's scope is approved here, CAP-33) · **Under:** DEC-792, DEC-826 Q3, DEC-819, CAP-33 · **Basis:** OWNER, 2026-10-19 · **Changes:** DEC-792 item 1 (its 8,000-character limit) and item 2 (rows W2-M372 and W2-M373 move from W2-10 to W2-62). · **Class:** kept (items changed: (4) history)
- **Decision:**
  1. **The session-start hook loads the RESUME HERE block in full,** never a cut of its first 9,000 characters (`template/governance/kernel/hooks/sessionstart.py:41`, row W2-M372), and names the prompt in force, not Wave 1's (row W2-M373).
  2. **Once it does, DEC-792's 8,000-character limit is lifted.** The resume then holds the full session state: what is happening, what was decided, what is next, and where things are. Repository knowledge comes from retrieval and the context packets, not from the resume.
  3. **A checkpoint is written at every handover:** a worker's return, a merge, a package, a compaction. This holds whatever the window (DEC-838); it is in prompt v3 and `LEAD-w2-common.md` now.
  4. **Split out of W2-10 as a small first ticket, W2-62** (STANDARD, engineer; a kernel hook change through CIT-P), in keystone 3, with no dependency, so it lands before W2-10. Paths: `template/governance/kernel/hooks/sessionstart.py`, `template/governance/kernel/skills/checkpoint/**` (the resume rule of item 2 only), `tests/unit/hooks/**`, `docs/changes/W2-62-CIT-P.md`. W2-10 keeps the rest of its card.

### DEC-838 — Context windows: every session uses its model's full window; usage is the limit (item 2; standing)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; standing) · **Under:** DEC-826 Q6, DEC-829 item 3 · **Basis:** OWNER, 2026-10-19; `claude -p "/autocompact"` on 2026-10-19 after the change: "Auto-compact window for Opus 5.5: 1m tokens (default for this model)" · **Replaces:** lens F's 300k and 500k values (plan §6) and A5's "about 300k tokens" rule. · **Class:** kept
- **Decision:**
  1. **Every session uses its model's full window,** Claude Code's default now that the user-level variable is gone (1M for Opus 5.5).
  2. **No launch sets a compaction threshold,** and no brief or rule asks a session to stop or compact early: a session compacts only when its model's window is nearly full. `LEAD_CHECKPOINT` is no longer a lead's status.
  3. **Usage, not money, is the limit** (the owner's subscription has daily and weekly limits). W2-60's per-session record includes tokens, turns and any rate-limit event. The orchestrator reports weekly usage against the limits in the daily digest, so the owner can adjust if a limit starts to bite.
  4. The checkpoint at every handover (DEC-837 item 3) stays, whatever the window.

### DEC-848 — Backups: the owner's own push of `w2/integrate` continues, at least daily (item 13)
- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; standing) · **Under:** DEC-830, DEC-412 · **Basis:** OWNER, 2026-10-19 · **Corrects:** DEC-830 item 4. · **Class:** kept (items changed: (1) kept §2.4; (2) backup now §2.8 hourly bundle)
- **Decision:**
  1. Agents never push.
  2. The owner's own backup push of `w2/integrate` continues, as an owner act, at least daily.
  3. DEC-830's "no push" means no pre-push gate yet, not no backups.

### DEC-850 — How questions reach the owner (standing)
- **Status:** ACCEPTED (owner, 2026-10-19, in two follow-ups; item 1 as the second one restated it; the owner commits this entry with `Role: owner`, in the next batch; standing) · **Changed by:** item 1's end-of-turn question line replaced by DEC-855's `owner-ping` (2026-10-19) · **Under:** DEC-818, DEC-787, MR-6 · **Basis:** OWNER, 2026-10-19. The notification test of 2026-10-19: an AskUserQuestion box did not reach the owner's phone (the owner answered "No"); a box pauses the turn mid-way, so the app sends nothing, while a permission request or a finished turn does notify. · **Class:** kept (items changed: (1) end-of-turn question line history DEC-855)
- **Decision:**
  1. **A question that blocks all further work** (nothing else the orchestrator or any lead can do until the owner answers): the orchestrator writes the full six-part package (DEC-818) as its message, saves the same text under `governance/project/orchestration/packages/<package id>.md`, and **ends its turn with it**, finishing with one line `QUESTION FOR THE OWNER: <package id> - choose (a), (b), (c) or Discuss first; my recommendation is (x)`, then the OWNER_ACTION line. **The AskUserQuestion box is not used.** Background work (leads, workers, runs) keeps going while it waits. If the owner answers "Discuss first", the orchestrator goes on with anything that does not depend on it, and waits for the owner's written answer. If a finished turn does not reach the owner's phone either, a Notification hook is added (the owner's change).
  2. **A question that blocks only part of the work:** no question box. It goes in the report and the daily digest with the same six parts; the orchestrator keeps working on everything it does not block, and uses a question box only once it becomes blocking.
  3. **Leads and workers never ask the owner directly.** A lead returns its package to the orchestrator in the six parts (DEC-818), says whether it blocks all of its work or only part, and keeps working on whatever it does not block.
  4. The OWNER_ACTION line stays at the end of every report (DEC-787).

### DEC-859 — The code graph: targeted traversal for questions, pages for whole-graph jobs, never a query over the cap (standing; W2-37)
- **Status:** ACCEPTED (owner, 2026-10-20; the owner commits this entry with `Role: owner`, in the next batch; standing) · **Under:** DEC-829 (lens G R1), DEC-812, CAP-33.b, CAP-33.g · **Basis:** OWNER, 2026-10-20. After DEC-856, this repository's code graph holds 28,923 nodes and 117,939 edges, still over the code-graph tool's 100,000-row cap (lens G: our wrapper pulls the whole graph and fails above it). · **Class:** kept
- **Decision:**
  1. **Agents' questions use the code-graph tool's own traversal** (`trace_path`, `search_graph`, `query_graph`), with small, targeted answers; our wrapper never loads the whole graph to answer a question.
  2. **Whole-graph jobs** (a full impact map, an audit of every dependency) read the graph in pages, never one query over the tool's row cap.
  3. **On large repositories, a job may be split by module or folder,** and its parts queried in parallel.
  4. **KPIs:** no query ever exceeds the cap, tested on this repository and on a large synthetic repository well over the cap; the callers of `rrf` and `indexable` are answered on this repository.
  5. W2-37's card carries these; its ticket file gains them in its resume, committed first by its lead in its worktree (a reviewed ticket's file is not edited on `w2/integrate`). Every brief that asks a code question says item 1.

### DEC-860 — Context: never one giant query, never one giant context; retrieval in batches, ranked and stacked (standing; W2-04, W2-61, W2-15b)
- **Status:** ACCEPTED (owner, 2026-10-20; the owner commits this entry with `Role: owner`, in the next batch; standing) · **Under:** DEC-833, DEC-836, DEC-725, CAP-10, CAP-15.d · **Basis:** OWNER, 2026-10-20: the same principle as DEC-859, for context. · **Class:** kept (items changed: (2) superseded §5.2/§5.3; (3) superseded §5.5)
- **Decision:**
  1. **Never one giant query and never one giant context.** Retrieval for a large question runs in batches, ranks them and stacks them, so the agent gets all the evidence the question needs, in order of relevance, within its budget.
  2. **This is the stacking that W2-15b measures against the owner's 99 % goal** (DEC-833): the share of questions whose stacked context holds all their needed evidence, across batches.
  3. W2-04 (the packet: within its ceiling, the supplementary evidence from ranked batches, with what was left for a further batch named), W2-61 (the standing measure reports the stacked figure) and W2-15b (the final measure) carry it in their cards and ticket files. Every brief that tells an agent to use `gov retrieve` (DEC-836) says to take a large question in batches (`--batch-size`, `--continue`) and stack them.
- Next free id: DEC-861.

| Version | Date | Change |
|---|---|---|
| 0.251 | 2026-10-20 | Owner: DEC-859 (the code graph: the tool's traversal for questions, pages for whole-graph jobs, split by module on large repositories, never a query over the cap; W2-37), DEC-860 (context: retrieval in batches, ranked and stacked, never one giant query or context; W2-04, W2-61, W2-15b). Next free id: DEC-861. |

### DEC-861 — The orchestrator commits the records of the owner's decisions; the owner's push is the acceptance (standing)
- **Status:** ACCEPTED (owner, 2026-10-20, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-20)`; standing) · **Under:** DEC-724, DEC-788, DEC-851, ADR-0001 · **Basis:** OWNER, 2026-10-20: "Nothing is ever left staged in the main tree, so no merge, close or lead ever waits on me." · **Changes:** DEC-724 (owner entries were committed by the owner with `Role: owner`) and DEC-788 (the daily owner batch). · **Changed by:** DEC-1057 · **Class:** kept (items changed: (1)(2) amended by DEC-1057; (5) history)
- **Decision:**
  1. **What the orchestrator commits:** the records of the owner's decisions (the register, the plan files, the prompt, the briefs, the path map and the ratchet lists), as soon as they are written. Nothing is left staged in the main tree.
  2. **How it signs:** never as the owner. Its commits carry `Role: orchestrator`, never `Role: owner`, plus `Task: decision-record` and `Decided-by: owner (chat, <date>)` naming whose decision it records. The owner's own commits keep `Role: owner`.
  3. **Pushing:** the orchestrator never pushes. The push stays the owner's (through the operator, or a scheduled job of the owner's), and **the owner's push is the owner's acceptance** of what the orchestrator committed.
  4. **The owner's check:** the daily digest lists every decision recorded since the owner's last push, each with its DEC id, its one-line content and its commit sha.
  5. **Until W2-12's `gov approve` lands,** the register records the owner's decisions as the orchestrator faithfully transcribes them, and the owner's push is the owner's act. This replaces the owner's earlier patch-file idea.
  6. **Where `Role: owner` is still read** (the check of item 5 of the owner's rule, 2026-10-20): the close's ratchet (`src/gov/close/ratchet.py:104-111`) and its escalation lift (`src/gov/close/state.py:172-200`) count an owner's entry only from a commit with `Role: owner` alone, and the decisions checker (DEC-360) will when decision files exist. How they should read `Decided-by` was package P-W2-51, answered by DEC-862: those two kinds stay the owner's own `Role: owner` commits until W2-12 lands.

### DEC-866 — Supersession propagates (standing)
- **Status:** ACCEPTED (owner, 2026-10-20, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-20)`; standing) · **Under:** DEC-825, DEC-851, DEC-791 (W2-55), DEC-105 · **Basis:** OWNER, 2026-10-20: W1-49's two cases (DEC-636 against DEC-838) and W2-59's three earlier cases (DEC-605's premise against DEC-822 and DEC-835) still enforced replaced decisions, and DEC-838 never named the entries it superseded. · **Class:** kept
- **Decision:** whenever a decision supersedes, cancels or changes another:
  1. **The old entry is marked at once:** its status line names the new entry (`SUPERSEDED by DEC-n`, or a "Changed by" note for a part), and agents are no longer served the old one as in force.
  2. **The orchestrator sweeps for everything that cites or enforces the old decision,** by its id and by its value (tests, code, skills, briefs, ticket KPIs, the prompt, the path map), and lists it in the package or the digest.
  3. **Each item is updated to the new decision,** through its owning ticket or a small one, or kept with a recorded reason.
  4. **W2-55 (keystone 5) gains a KPI:** a check fails when anything still enforces a superseded decision without a recorded reason.
  5. **Applied now to DEC-838:** the 300k window rule was held by DEC-208, DEC-237, DEC-248 item (c), DEC-451, DEC-636 and DEC-665 (its W1-49 part); DEC-636 is marked SUPERSEDED, the others "Changed by" for that part. A decision that replaces a rule names every entry that held it.
  6. **The sweep of every decision superseded or changed since Wave 2 began** is `governance/project/orchestration/packages/SWEEP-2026-10-20.md`, reported with this entry.
- Next free id: DEC-867.

| Version | Date | Change |
|---|---|---|
| 0.255 | 2026-10-20 | Owner (recorded by the orchestrator, DEC-861): DEC-865 (P-W2-52 (a): W2-63 revises W1-49's two window tests to DEC-838; DEC-863 and DEC-864 accepted; DEC-636 superseded), DEC-866 (supersession propagates: the old entry marked at once, a sweep by id and value, each item updated or kept with a reason, W2-55's check; DEC-208, DEC-237, DEC-248, DEC-451, DEC-636 and DEC-665 marked). Next free id: DEC-867. |

### DEC-898 — The resource gate checks free disk space and free inodes; every auditor, trial and lead has a scratch budget, cleans up as it goes and reports its scratch size
- **Status:** ACCEPTED (owner, 2026-10-22, in the chat, standing; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`). The rule is the owner's. The figures in items 1 and 2 are the orchestrator's proposal, in force provisionally until the owner confirms or changes them. They are stricter only. · **Under:** DEC-798, DEC-847, DEC-880, DEC-889 item 16, DEC-855, DEC-851, DEC-861 · **Basis:** · **Changed by:** DEC-899 item 5: the figures are confirmed by the owner and no longer provisional. · **Changed by:** DEC-902: the weekly sweep joins the scratch rules (only in a quiet moment, nothing newer than 24 hours, nothing held open, nothing cited as evidence). · **Changed by:** DEC-904 item 3: until the retention trial reports, a verification run may use 6,000,000 inodes and 60 GB, one at a time under `/tmp/gov-os-verify.lock`, the disk floor still enforced. · **Class:** kept
  - **Lens I area 4's folder** (`/tmp/gov-os-assessment-I4/`) held about 7.0 million files and folders (61 GB). About 5.3 million files (46 GB) were in `tmp/bt/`: from 18:31 to 19:04 that auditor gave each planted-fault run its own pytest base folder, which skips pytest's clean-up of old folders, and the suites it ran make whole-tree copies per test.
  - **The disk's inodes reached 98 % use.** One run could not write its result (ENOSPC).
  - **Before the orchestrator's clean-up of the four lens I folders** (about 20:15): 62,589,143 of 67,108,864 inodes used (94 %); 640 GB of 1,007 GB used (67 %).
  - **After the clean-up** (20:30): 45,983,305 inodes used (69 %); 486 GB used (51 %). The cited evidence folders were kept.
- **Decision:**
  1. **The resource gate checks free disk space and free inodes.**
     - It refuses a launch, a trial or a close when the shared disk has less than **100 GiB free or fewer than 10,000,000 inodes free**.
     - Until W2-20 builds this into `gov launch` and `gov close`, the orchestrator's `tools/disk_gate.sh` does it, in the same command as each launch and inside `close_queue.sh`, `nightly.sh` and `tooltrials.sh`.
     - W2-20's ticket gains the KPI. Its gate counts every Gov OS session on the machine, as before.
     - `gov close`'s call to the same reading goes to W2-07's or W2-66's card (the review bundle), because their paths hold the close and W2-20's do not.
  2. **Every auditor, trial, research and lead brief gets a scratch budget:** size, and the number of files and folders.
     - **The budgets:**
       - an auditor, trial or research session: **30 GB and 2,000,000** in its own folder;
       - a lead with all its workers: **20 GB and 1,000,000** outside the tracked tree (its worktree's untracked and ignored files, and its own temp folder);
       - the nightly run: **30 GB and 2,000,000**.
     - **How a session keeps to it:**
       - it sets `TMPDIR` to a folder of its own (where the sandbox sets one, it keeps that one);
       - it keeps pytest's own retention of three base folders, never a per-run `--basetemp`;
       - it removes its clones, worktrees and temp trees as it goes, not only at the end;
       - it measures its scratch (`du -s --inodes` and `du -sh` of its folders) before every heavy run and at the end, and reports the figures in its return's `evidence` line.
  3. **A scratch that passes its budget stops that session's heavy work at once.**
     - The session cleans what it can and returns at once: a lead as PACKAGES, an auditor or trial as PARTIAL, with the measure and the cause.
     - **The orchestrator then pings the owner** (P1). Leads and workers never ping (DEC-855); the orchestrator's ping is the owner's notice.
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §3 (the resource gate), §4 (the launch form), §15 (the gate by hand, the closes, the nightly run and the trials), v3.18;
  - RESUME HERE;
  - `governance/project/briefs/LEAD-w2-common.md` (leads and their workers);
  - `governance/project/briefs/AUDITOR-common.md` (W2-25's, W2-28's, W2-30's and W2-47's auditors) and every lens, trial and research brief the orchestrator writes;
  - W2-20's ticket file and card (the KPI; its own commit with `Task: DAEO-r30l`, DEC-896);
  - the orchestrator's `disk_gate.sh`, `close_queue.sh`, `nightly.sh` and `tooltrials.sh`.
- Next free id: DEC-899.

| Version | Date | Change |
|---|---|---|
| 0.285 | 2026-10-22 | Owner (recorded by the orchestrator, DEC-861): DEC-898 (standing: the resource gate checks free disk space and free inodes, refusing a launch, trial or close below 100 GiB or 10,000,000 inodes free; scratch budgets of 30 GB and 2,000,000 for an auditor, trial or research session or the nightly run, 20 GB and 1,000,000 for a lead with its workers; own TMPDIR, pytest's own retention, clean-up as it goes, the scratch size in every return; a budget passed stops the heavy work and the orchestrator pings the owner; the figures provisional until the owner confirms them). Next free id: DEC-899. |

### DEC-902 — The weekly sweep, a standing rule; the cleanup of 2026-10-23; the owner's commits A and B; pytest-timeout installed
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat, standing for item 1; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** DEC-898, DEC-899 items 3 and 10, DEC-900, DEC-892 b, DEC-889 item 13, DEC-861, DEC-851 · **Basis:** the cleanup proposal (`governance/project/orchestration/packages/CLEANUP-PROPOSAL-2026-10-23.md`, filed with this record) and the disk inventory behind it. · **Changed by:** DEC-1164 (15) (item 1: the sweep at any time) · **Class:** kept (items changed: (1) kept; cleanup of 2026-10-23 and commits history)
- **Decision:**
  1. **The sweep (owner, standing).**
     - **What:** the orchestrator sweeps throwaway areas under `/tmp` and run folders, weekly (on Monday) and when the disk gate (DEC-898) nears its floor.
     - **What it may remove:**
       - pytest's `garbage-*` folders and its numbered run folders other than the newest three;
       - Claude Code's session temp folders under `/tmp/claude-1000` of sessions not running;
       - the launcher's `/tmp/gov-launch-*` folders;
       - the code-graph daemon's run folders under `/tmp/gov-cbm-1000`;
       - `/tmp/gov-check-*` and `/tmp/gov-testcache-*`;
       - the worktrees and branches of closed tickets, after a sync.
     - **Its conditions:**
       - only in a quiet moment: no lead, close, nightly run or trial running;
       - nothing modified in the last 24 hours;
       - nothing a running process holds open (`lsof`);
       - nothing cited as evidence;
       - never the live session's own folder, and never the live code-graph daemon's folder.
     - **What it never touches:** `~/.cache`, a ticket in progress's `~/gov-os-runs/` folder, the record worktree, the owner's EXAMIN copy and the workbench.
     - **How it runs:** by `.gov-runtime/scratch/orchestrator/tools/sweep.py`. It lists what it removed and what it skipped, and why.
     - **The figures before and after** go in the daily digest.
  2. **The cleanup of 2026-10-23 (owner's acts).**
     - **Removed by the owner:** lists 1, 2, 4 and 6 of the proposal, 289 folders, none skipped.
       - Claude Code's finished sessions' temp, pytest's two garbage folders, the launcher's two engineer temps, W2-48's cache folders and the empty check folders.
       - Before: 332 GB used (35 %), 30,267,328 inodes used (46 %).
       - After: 74 GB used (8 %), 882 GB available; 1,826,466 inodes used (3 %), 65,282,398 free.
     - **Lists 3 and 5 (pytest's old run folders, 58; the code-graph run folders, 10,575)** are approved only under item 1's conditions, because leads are running and the daemon shares that folder. The orchestrator runs them in the first quiet moment and lists what it skipped and why.
  3. **The owner's commits:**
     - `596870bd`: W1-02's and W1-05's p95 `load_sensitive` entries removed (DEC-899 item 3);
     - `c9a08678`: W1-42's RETR-X-02 case and governance-share case retired with both `accepted_reds` entries (DEC-900).
     Both are `Role: owner`, both were validated with the pinned ratchet first (DEC-895), and `accepted_reds` is empty. The owner pushed `w2/integrate` at `c9a08678` and `record/w2` at `d8e5e53d`.
  4. **pytest-timeout 2.4.0** is installed by the owner in the user site of `/usr/bin/python3`, its wheel's hash checked (sha256 `c42667e5cdadb151aeb5b26d114aff6bdf5a907f176a007a30b940d3d865b5c2`). It is recorded in the tool registry, approved by DEC-892. The first re-pin's environment gets the same wheel.
  5. **Two rows:**
     - **W2-M405:** the launcher left two engineer sandboxes' temp folders behind on 2026-10-20, 4.1 million inodes and 36 GiB. W2-C002's fix at W1-28 no longer holds. Fixed by W2-21: the launcher removes a sandboxed worker's temp folder when the worker ends.
     - **W2-L415:** two W1-38 rulesync cases (`TestGenerateCheck::test_check_clean_after_generate` and `TestRegisteredFamilyCheck::test_gov_check_lists_the_check_under_the_family`) errored under load in W2-50's run 9 (`rulesync generate` timed out at 30 s) and passed alone. They are not on `load_sensitive`. Fixed by W2-57's first item (the probe's limits).
- **Changes:** DEC-899 item 10 (the proposal decided); DEC-898 (the sweep joins its scratch rules).
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §15 (the sweep, beside the disk gate; the daily digest's figures), v3.20;
  - RESUME HERE;
  - the tool registry;
  - the Wave 2 list (rows W2-M405, W2-L415);
  - W2-21's card (the launcher's temp clean-up, row W2-M405).
  It does not reach the lead or auditor briefs: the sweep is the orchestrator's, and DEC-898 already tells sessions to clean up after themselves.
- Next free id: DEC-903.

| Version | Date | Change |
|---|---|---|
| 0.287 | 2026-10-23 | Owner (recorded by the orchestrator, DEC-861): DEC-902 (standing: a weekly sweep of throwaway areas under /tmp and run folders, only in a quiet moment, nothing newer than 24 hours, nothing held open, nothing cited as evidence, never the live session's or daemon's folder, figures in the daily digest; the cleanup of 2026-10-23: lists 1, 2, 4 and 6 removed by the owner, 74 GB and 1.8 M inodes used after; lists 3 and 5 under the sweep's conditions; the owner's commits 596870bd and c9a08678; pytest-timeout 2.4.0 installed; rows W2-M405 and W2-L415). Next free id: DEC-903. |

### DEC-906 — Only an independent test designer commits under tests/acceptance/ (standing); W1-01's history case reads an exact-commit exemption list holding c9a08678 alone; the lock until W2-67 lands
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat; item 1 standing; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** MR-3, DEC-253, DEC-889 item 16 d, DEC-891, DEC-862 (a), DEC-895, DEC-900, DEC-905, DEC-861, DEC-851 · **Basis:** package P-W1-01-H (`governance/project/orchestration/packages/P-W1-01-H.md`). `tests/acceptance/W1-01/test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests` has been red on `w2/integrate` since the owner's `Role: owner` commit `c9a08678644485a7528bc875164e110881b63d93` (DEC-900's retirement of W1-42's two cases). · **Changed by:** DEC-953 (item 1) · **Changed by:** DEC-962 (item 3's one-run lock ended) · **Class:** kept (items changed: (1) kept; (2) history; (3) history)
- **Decision:**
  1. **(c), standing.**
     - From now on, test retirements and any other change under `tests/acceptance/` are committed by an independent test designer, under the owner's named decision.
     - Only ratchet entries (`accepted_reds`, `load_sensitive`) and `accepted_history` entries stay the owner's own `Role: owner` commits.
     - Any owner commit that touches tests is validated with a full run in the close's form before the ACT ping.
  2. **(a), narrowed to a list, not a rule.** A `Role: owner` trailer is only text until W2-44 binds trailers to the launch, so W1-01's history case must not trust it as a standing rule.
     - **The list:** W2-70's test designer revises the case to read an owner-committed exemption list naming exact commits: the path map's `acceptance_exemptions`, beside `accepted_history`. Each entry is `{commit: <full sha>, decision: <DEC id>}`.
     - **Its only entry:** `c9a08678644485a7528bc875164e110881b63d93`, citing DEC-900.
     - **Everything else stays red:** any other owner commit touching `tests/acceptance/`, and any commit not listed by its exact sha.
     - **The entry** is the owner's own `Role: owner` commit, prepared by the orchestrator and validated first with a full run in the close's form (item 1).
     - **W2-70 merges early,** so the red leaves `w2/integrate` then.
     - **Until then,** leads report W1-01's case by name as known and not theirs, and the orchestrator does not count it against them.
  3. **The one-run-at-a-time lock** (`flock /tmp/gov-os-verify.lock`, DEC-904 item 3, kept by DEC-905 item 4) stays until W2-67 lands. Then the resource gate decides.
- **Changes:**
  - DEC-862 (a) and DEC-891 (which owner commits stay `Role: owner`: the ratchet and accepted-history entries, plus this exemption list's entries);
  - DEC-900 (its form: a retirement is a test-designer commit from now on);
  - DEC-905 item 4 (the lock's end).
- **Where it goes (DEC-851):**
  - this register, with DEC-862's, DEC-891's, DEC-900's and DEC-905's status lines marked;
  - the prompt §5 (the owner's commits) and §15 (the lock), v3.23;
  - `LEAD-w2-common.md` (W1-01's case as a known red until W2-70 merges; acceptance changes by test designers only);
  - RESUME HERE;
  - W2-70's ticket file and card (its own commit);
  - the prepared owner entry.
- Next free id: DEC-907.

| Version | Date | Change |
|---|---|---|
| 0.291 | 2026-10-23 | Owner (recorded by the orchestrator, DEC-861): DEC-906 (standing: changes under tests/acceptance/ only by an independent test designer under the owner's named decision; only ratchet and accepted-history entries stay Role: owner commits; an owner commit touching tests validated with a full run first; W1-01's history case reads an exact-commit exemption list, acceptance_exemptions, holding c9a08678 alone (DEC-900), by W2-70's test designer; the lock until W2-67 lands). Next free id: DEC-907. |

### DEC-912 — W1-01's merge rule passes a merge whose acceptance files equal git's own merge of its parents; W2-66's third and last review for P1 and P2
- **Status:** ACCEPTED (owner, 2026-10-24, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-24)`) · **Under:** DEC-906, DEC-750, DEC-754, DEC-253, DEC-413, DEC-909, MR-3 · **Basis:** package P-W2-66-M1-R2 (`governance/project/orchestration/packages/P-W2-66-M1-R2.md`). M1: W2-66's ordered merge-back `03f470a5` and W2-65's `4ef3293a` each hold acceptance files equal to neither parent but exactly git's own clean merge of two test designers' edits, so W1-01's history and integration-merges cases are red on both branches. R2: W2-66's second and last review failed on P1 (a renamed test-map target counted as selected but running nothing, with no widening; yes / fails open, medium) and P2 (W1-28's held-out copy check coupled to `**_support.py` only; yes / fails open, low). · **Class:** kept (items changed: (1) kept; (2)-(4) history)
- **Decision:**
  1. **M1 (a): W1-01's merge rule is revised.** A merge commit passes when every file it changes under `tests/acceptance/` equals git's own merge of its parents (`git merge-tree --write-tree`; no hand edits), consistent with DEC-750 and DEC-754, and every brought commit that touches the folder is still a test designer's or listed (DEC-906 item 2). Any file that differs from git's own merge (a hand edit, a conflict resolution) stays a refusal.
  2. **Who and where:** a test designer makes the revision (DEC-906 item 1), in W2-70 (a short round) or in W2-66's resume, whichever lands sooner. It must land before W2-66's verification and before the W2-59 + W2-65 merge, so both go green. The orchestrator routes it to W2-70's round 2, which starts at once; W2-66's run 3 merges `w2/integrate` back once it has merged, before its verification.
  3. **R2 (a), the owner's exception to DEC-413:** one more round and a third, last review, in the same resume as M1 (W2-66's run 3).
     - **P1:** a selected test-map target that cannot be resolved at the head widens the run to the full regression and is named in the record, with tests.
     - **P2** rides in the same round: W1-28's coupling reaches every file its scan reads.
  4. **The last round:** if the third review finds another fail-open case an honest agent can hit, no fourth round starts: the orchestrator brings the owner a package.
- **Changes:** DEC-253 (its rule widened, item 1); DEC-413 (for W2-66 only: a third review); DEC-899 item 2 (the merge-back is judged by item 1).
- **Where it goes (DEC-851):** this register, with DEC-253's and DEC-413's status lines marked; W2-70's ticket file (a KPI line, its own commit, `Task: DAEO-uzme`); W2-66's ticket file (two KPI lines, its own commit, `Task: DAEO-c1uz`); W2-70's run 2 and W2-66's run 3 briefs; RESUME HERE. No standing brief changes.
- Next free id: DEC-913.

| Version | Date | Change |
|---|---|---|
| 0.297 | 2026-10-24 | Owner (recorded by the orchestrator, DEC-861): DEC-912 (P-W2-66-M1-R2: M1 (a), W1-01's merge rule passes a merge whose every changed acceptance file equals git's own merge of its parents, any other file still refused, by a test designer in W2-70's round 2, landing before W2-66's verification and the W2-59 + W2-65 merge; R2 (a), the owner's exception to DEC-413 for W2-66: one more round and a third, last review, P1 widening the run for an unresolvable target with tests, P2 riding; a further fail-open finding a package, no fourth round). Next free id: DEC-913. |

### DEC-918 — Containment's merge rule matches DEC-912 exactly: a merge-back file equal to git's own merge is no change; W2-72 rides the first re-pin
- **Status:** ACCEPTED (owner, 2026-10-24, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-24)`) · **Under:** DEC-912, DEC-410, DEC-421, DEC-572, DEC-453, DEC-750, DEC-754, DEC-884, DEC-906 · **Basis:** packages P-W2-L437-A and P-W2-L437-B (`governance/project/orchestration/packages/`). The close's containment gate (`judge_commits`, every finding refuses) reads, under `tests/acceptance/**`, every path both parents changed as the merge commit's own change (DEC-410 DP-24), so it refuses W2-66's and W2-65's closes on their DEC-912 merge-backs (`03f470a5`, `4ef3293a`); the live hook flags them. · **Class:** kept (items changed: (1) landing check kept, live-hook part superseded §2.2; (3)-(4) history)
- **Decision:**
  1. **(a1), the owner's principle exactly:** containment's merge rule matches DEC-912. A merge-back file under `tests/acceptance/` equal to git's own merge of its parents (`git merge-tree --write-tree`) is neither reverted, refused nor counted as a change, by the live hook or by the close's gate. Any file that differs from git's own merge (a hand edit, a conflict resolution) is still caught as before.
  2. **Not (a2):** the bringing commits are already judged at their own closes and by W1-01 under DEC-912.
  3. **Ticket W2-72 (FULL, engineer) rides the first re-pin,** since every close after it is judged by the pinned containment, and the tickets due to close before the second re-pin hold such merges. The orchestrator checked the owner's exception and could not show it: W2-66's range holds `03f470a5` and W2-65's holds `4ef3293a`, both due to close before the second re-pin; W2-67, W2-57 and the held tickets will merge `w2/integrate` back again over shared test folders (W1-30, W1-26, W1-38). The first re-pin moves back by about 5 hours.
  4. **The tests DEC-410 DP-24 set** (W1-50's merge cases that read a clean merge of a both-changed acceptance file as the merge's own) are revised by W2-72's test designer, `Rewrite-Reason: DEC-918`; the rule for ticket files (DEC-421, DEC-572) and for every other path is unchanged.
- **Changes:** DEC-410 (DP-24, for acceptance tests); DEC-884 and DEC-899 item 4 (the first re-pin also carries W2-72).
- **Where it goes (DEC-851):** this register, with DEC-410's status line marked; the w2 prompt (section 3's re-pin line); W2-72's ticket file and WBS card (their own commit, `Task: DAEO-ye2a`); W2-72's brief; RESUME HERE.
- Next free id: DEC-919.

| Version | Date | Change |
|---|---|---|
| 0.304 | 2026-10-24 | Owner (recorded by the orchestrator, DEC-861): DEC-918 (P-W2-L437-B (a1): containment's merge rule matches DEC-912 exactly, a merge-back acceptance file equal to git's own merge neither reverted, refused nor counted, any other still caught; not (a2); W2-72 rides the first re-pin, the exception not shown; W1-50's DP-24 cases revised by its test designer). Next free id: DEC-919. |

### DEC-933 — P-REPIN-2 (a): each judge improvement re-pinned as it lands; the nightly in a 02:00 to 05:00 window, booked by a measured estimate, every night, for the Gov OS and every adopted product (standing)
- **Status:** ACCEPTED (owner, 2026-10-28, in the chat; it supersedes the owner's earlier message of the same night on P-REPIN-2 and the nightly, recorded in its place; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-28)`; standing; item 2's application revised by DEC-934: committed scripts, logs, the morning check, the Windows wake task; item 1's re-pin 2 done, DEC-935) · **Under:** DEC-932 item 3, DEC-852 item 3, DEC-880, DEC-889 items 4 and 12, DEC-915 item 4, DEC-922, DEC-928 item 3, DEC-851, DEC-861 · **Basis:** package P-REPIN-2 (`governance/project/orchestration/packages/P-REPIN-2.md`). · **Changed by:** DEC-953 (items 1, 3) · **Changed by:** DEC-961 (item 2: the nightly starts at 02:00 on its window and holds nothing else; it takes no lock at night) · **Changed by:** DEC-973 (the nightly at 04:00, its check at 08:00, the morning package at 09:00) · **Changed by:** DEC-1049 (item 2) · **Class:** kept (items changed: (1) history; (2) kept except clean-tree/stable-head start conditions superseded §6.2 A-3, times per DEC-973; (3) history)
- **Decision:**
  1. **P-REPIN-2 (a); the cadence is standing.** Each judge improvement is re-pinned as soon as it merges and passes its checks, not bundled. Re-pin 2 carries W2-57 and W2-07 round 2 as soon as W2-07 merges; re-pin 3 carries W2-68 and W2-71 when they land.
  2. **The nightly (a condition of (a), and a standing rule for the Gov OS and every adopted product; the rule about rules):**
     1. **The window:** the nightly full run takes place between 02:00 and 05:00.
     2. **Its length is measured, not fixed:** before each night, the run's duration is estimated from the per-test durations recorded in the last full runs' JUnit files (the parallel phase across its workers, plus the serial phase), with a small margin. Only that much of the window is booked. The morning digest reports the estimate against the actual.
     3. **Start conditions:** the run starts at 02:00 once the state is clean: no close or merge in progress, the tree clean, and `w2/integrate`'s head stable. If a close is running at 02:00, the run waits for it and starts no later than the latest start that still fits its estimate in the window.
     4. **During the run** no close or verification run starts (they take turns through the close lock and the verification lock), and leads do no heavy test runs. Light lead work may continue.
     5. **Closes resume as soon as the run ends,** whatever the time, not at a fixed 05:00.
     6. **If the estimate no longer fits the window** (for example as a product's suite grows), the run is not cut short: the owner gets a package with the options (an earlier start, splitting the suite across nights by a fixed rotation, or more workers), with what each could let through.
     7. **Every night,** with its result in the morning digest; a red is a P1 package. A green nightly may serve as the base for the next day's scoped closes.
     8. **There is no "using the PC" hold yet.** If the owner wants one later, the owner will say so, and it will never block the nightly window.
  3. **The run clones under `~/gov-os-runs` (2.6 GB)** go in the tooling review (P-TOOLS-REVIEW-1).
- **How it is applied (`tools/nightly.sh night`, `tools/nightly_estimate.py`; the orchestrator's readings, for the owner to overturn):**
  - **The estimate's workers are measured too.** Item 2.2's "across its workers" read as the 20 workers of `-n auto` books about 45 % of the real time on this machine: the parallel sums divided by 20 give 16 to 19 minutes, while the walls were 45 (the nightly of 2026-10-25), 50 (W2-66's full close) and 39 minutes (W2-70's). The effective parallelism (sum / wall) was 7.4 to 8.2. So the estimate is: the newest full run's parallel sum divided by the lowest effective parallelism of the last three full runs (never less than its longest case), plus its serial sum, plus the measured setup (clone, rebuild, collection; 7 minutes until one is recorded), times 1.10. Tonight's: 84 minutes (parallel 50, serial 19, setup 7), so the latest start is 03:36.
  - **"Clean" is:** no `CLOSE-RUNNING`, no `MERGE_HEAD` in the main tree, `git status --porcelain` empty there, and `w2/integrate`'s head at least 5 minutes old and unchanged since the last check (checked each minute). Past the latest start it does not start, and that night pings P1.
  - **The locks:** the run holds `NIGHTLY-RUNNING` (the close queue waits for it) and the verification lock for both test phases on one descriptor, closed in every test command so that no process a test leaves behind keeps it. Both go the moment the run ends.
  - **Leads:** while `NIGHTLY-RUNNING` exists, a lead runs no suite and no full run (a single test file at most), stated in `LEAD-w2-common.md`. A lead's full run also waits for the verification lock.
  - **Item 6:** an estimate over the window pings a P2 package at once (`NIGHTLY-WINDOW`); the run starts once clean, never cut.
  - **Item 7, the base:** today the judge takes a scoped close's base only from committed full close records or `gov.close.nightly`'s own records (W2-66). `nightly.sh`'s green is not one of those, and `gov.close.nightly` is not run until row W2-M406's fix (DEC-915 item 4). So a green nightly serving as the base needs the judge's nightly (row W2-M407, below), or P-SCOPE-RECORDS-1 (DEC-929 item 1) to say how `nightly.sh` leaves a record the judge reads.
  - **For every adopted product:** row W2-M407 (medium, engineer): `gov.close.nightly` applies items 2.1 to 2.8 itself (the window, the measured estimate, the start conditions, the locks, the package when the estimate no longer fits), so an adopted product gets the same nightly without an orchestrator script.
  - **The schedule is the owner's act:** one line in the owner's crontab, `0 2 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/nightly.sh night`, in its own ACT (`packages/ACT-NIGHTLY-1.md`). cron runs here (systemd is on). The machine must be awake at 02:00.
  - **Tested** on a copy with a temporary repository, folder and fake ping (`tools/test_nightly_night_mode.sh`, 8 of 8): a held nightly lock, a start after 05:00, a close running past the latest start, a merge in progress, a dirty tree and a head under 5 minutes old each stop it with a P1 ping; an estimate over the window pings P2 and goes on; by day it waits and never pings. The lock's hold through real test phases and the estimate-against-actual record are first exercised on the first night.
- **A lapse, the orchestrator's:** DEC-852 item 3 already asked for a nightly every night; it ran only twice (2026-10-21 and 2026-10-25). Nothing scheduled it, and its start rule (5 quiet minutes, load below 3) kept it waiting while the machine was in use. Counted in this week's tooling numbers (DEC-930 item 2).
- **Where it goes (DEC-851):** this register, with DEC-932's status line; the prompt §15 (re-pin cadence; the nightly), v3.33; `LEAD-w2-common.md` (no heavy test runs during the nightly); row W2-M407; `packages/ACT-NIGHTLY-1.md`; RESUME HERE; the morning digest.
- Next free id: DEC-934.

| Version | Date | Change |
|---|---|---|
| 0.317 | 2026-10-28 | Owner (recorded by the orchestrator, DEC-861): DEC-933 (P-REPIN-2 (a): re-pin 2 = W2-57 + W2-07 round 2 when W2-07 merges, re-pin 3 = W2-68 + W2-71; standing: each judge improvement re-pinned as it lands; the nightly in 02:00 to 05:00, booked by a measured estimate, clean start, locks, closes resume at its end, a package when it no longer fits, every night, red = P1, for the Gov OS and every adopted product; no PC hold; run clones to the tooling review). Next free id: DEC-934. |

### DEC-943 — Brief gaps in every lead's return, fixed the same week; the orchestrator's own drift measured (standing)
- **Status:** ACCEPTED (owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; standing) · **Under:** DEC-824, DEC-793, DEC-836, DEC-930, DEC-938, DEC-941, CAP-33 · **Changed by:** DEC-1052 (item 1) · **Class:** kept (items changed: (1) kept; (2) superseded §5.5)
- **Decision:**
  1. **Brief gaps.** Every lead's return gains a "brief gaps" section: what it had to discover, look up or ask that its brief, ticket or skills did not tell it, with the time it cost.
     - The orchestrator collects them and fixes the common brief, the brief builder or the kernel skills the same week.
     - The daily document reports how many gaps were found and how many fixed.
     - W2-79's tests check that each fixed gap stays fixed.
  2. **The orchestrator's drift.** Once W2-61's baseline and the first memory fixes (W2-55, W2-04) land, the orchestrator uses `gov context` at every resume and before every decision that touches a standing rule. It counts, weekly, every time it acted against a standing decision; that count is the measure of its own drift.
- **How it is applied:**
  - **The lead brief** (`governance/project/briefs/LEAD-w2-common.md`, Return): a `brief_gaps:` section right after the twelve fields, every status. Each line names what was missing, where it belonged (common brief, the ticket's part, the ticket file, a skill, a tool) and the minutes it cost. Briefs built from 2026-10-29 17:20 carry it.
  - **The register of gaps:** `governance/project/orchestration/brief-gaps.md`, one row per gap: the date, the ticket, the gap, its home, the minutes, and the fixing commit or "open".
  - **Fixing:**
    - a gap in the common brief or the builder is fixed by the orchestrator, recorded under this decision;
    - a gap in a kernel skill goes through CIT-P the same week (CAP-33: no kernel change without evidence, review and owner approval), so "fixed" there means proposed with its evidence, then promoted.
  - **W2-79's ticket** gains a KPI: one case per fixed gap in the common brief or the builder, showing that a built brief still carries the fix.
  - **Drift:**
    - the trigger is W2-61's baseline record plus W2-55's and W2-04's closes;
    - from then, the prompt §1 adds `gov context` to every resume and before every decision touching a standing rule;
    - the weekly numbers (DEC-930) gain a fifth: acts against a standing decision, each named with the decision and how it was found (the orchestrator's own count, the owner's correction, an auditor);
    - until the trigger, the count is kept by hand from the owner's corrections and the slips list.
- **Where it goes (DEC-851):** this register; `LEAD-w2-common.md` (Return); the prompt §1 (item 5, `gov context` once the trigger is met) and §7 (the daily document's lines), v3.40; `brief-gaps.md`; W2-79's ticket; RESUME HERE.

### DEC-953 — The owner's decision on AUDIT-GOV-FEATURES-1: the Gov OS is built and tested first, then dog-fooded; every Gov OS feature lifted as a gate on this repository's own development; tickets close on the audit's 10 practices; the guard keeps four rules (standing)
- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-105 (option (a), amended), MR-3, MR-6, ADR-0001 · **Changes:** Wave 2's exit criterion 1 (WBS §0 rule 1; AR-8 and F-M3 as applied, DEC-718, DEC-721): the proof of `gov close` moves to the proving ground (W2-81) and EXAMIN's copy; the standing rules listed in `governance/project/orchestration/LIFTED-BY-DEC953.md` · **Basis:** `governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md` (`a4939b45`); the owner's text, verbatim, in `.gov-runtime/scratch/orchestrator/drafts/DEC-953-owner-text.md` · **Changed by:** DEC-954 (item 2: a fifth rule, the hidden half from every worktree; items 6 and 10: the order and the plan approved) · **Changed by:** DEC-959 item 1 (how often tests run: the lead's scoped run once, the merge queue's run once per batch on the merged result, the close cites it; the full suite only in the nightly and for core changes) · **Changed by:** DEC-968 (item 4: never full outside the nightly; §0's "a red that fails alone refuses the close": only a red the change caused) · **Changed by:** DEC-1045 (the lifted gates) · **Class:** kept (items changed: (1) 10-practice close with FULL review and gitleaks superseded §3.6, §2.11; (2) guard four rules superseded §2.2; (5),(6),(7),(9),(10) history)
- **Decision:**
  1. **Option (a), amended:** every Gov OS feature is lifted as a gate on this repository's own development. Tickets close on the audit's 10 practices (§5), nothing more: independent tests first; the change's tests on the merged commit in a clean clone, one run at a time; an independent review for FULL tickets; the nightly full run; the guard's four rules; gitleaks; git discipline; the disk floor and scratch budgets; a close record; a quick check of changed record files. Nothing is deleted from the product: the lifted features stay built and tested.
  2. **The guard keeps four rules:** an implementer never writes acceptance tests; no reads of the hidden half of an evaluation set or the held-out material; no reads of secrets; no installs without the owner. Everything else in the guard is lifted, the command forms included. The orchestrator brings the fastest safe way to switch the rest off (an ACT where it needs the owner).
  3. **The nightly** stays a plain full test run on the integration head: no `gov close` at night, no report-only gates. A red starts an immediate investigation: the failing tests re-run alone, the red traced to its change and cause. A small, clear fix (a typo, a broken name, a one-line slip) is made on the spot and reported in the morning package; anything that needs the owner is a P1 package with a recommendation (a new ticket and its priority, or a fix folded into a current ticket). The red holds no other work while it is investigated.
  4. **Test selection, first, in parallel with memory's quick wins** (a helper, not a gate):
     - a. the close script and the leads' selection tool leave the governance files (briefs, prompts, records, the nightly's folder) out of the change before choosing tests; no test-map change and no owner commit (ACT-TESTMAP-1 is withdrawn);
     - b. every level uses the same tool: workers run their own unit tests while building; each lead runs its acceptance tests plus the affected tests the tool selects (the full suite only when core code changed) before returning; the close runs the same scoped set on the merged code; the nightly runs everything;
     - c. proven on the current leads' worktrees: scope, suites and reasons, and a scoped close's time against a full one;
     - d. scoped selection stays a product feature, proven for Wave 2's close with the others.
  5. **Close now under the 10 practices:** W2-71, W2-77, W2-57, W2-03 and W2-26, then every ticket as its practices pass. The orchestrator closes them (`tk close`) under this decision.
  6. **The order of work, subject to the owner's approval of the plan (item 10):** (a) memory finished and proven (W2-61's measure after each fix), quick wins first (W2-86, W2-87, the register-as-one-record defect), then W2-55, W2-04, W2-05, W2-06, W2-13, W2-15a; used as soon as it measurably helps; (b) in parallel, the roles, skills, templates and briefs (K3: W2-60a, W2-60b, W2-11), including the roles the three layers need; (c) then the rest of EXAMIN's minimum. The final proof of `gov close` is on the proving ground (W2-81) and EXAMIN's copy, not by re-closing this repository's tickets.
  7. **Compact the decisions:** a short decisions-in-force list, loaded with RESUME HERE; a list of what this decision lifts; superseded decisions moved to an archive section. The full register stays.
  8. **Three-layer orchestration,** planned now (a study in item 10's plan, for the rest of Wave 2 and Wave 3): a master orchestrator, a sub-orchestrator per parallel stream, each with its own leads and agents; its foundations first, in parallel and landing together: working memory (6a) and every role defined, with its skills and brief, loaded at launch (6b). It starts with the owner's approval, once both have landed, in new sessions.
  9. **How the owner and the orchestrator work together is unchanged:** owner-only decisions and P1s as packages with a ping as they arise (DEC-949); the morning package for the night; every ACT pinged with its file; every owner decision recorded and applied under the rule about rules (DEC-851, DEC-866); the status block (DEC-948); the morning handover to a fresh session (DEC-952 item 6); the owner's daily push.
  10. **The updated WBS and plan, now,** in parallel with items 2 to 5: Wave 2's remaining tickets in order, with parallelism, dependencies, estimates and the new target date for EXAMIN's copy; the tickets deferred to Wave 3, with why; the tickets no longer needed now the gates are lifted, with what happens to their built work. Until the owner approves it, only items 2 to 5 and memory's quick wins go ahead; other new tickets wait.
  - **Milestones, each with a ping:** (1) the plan, first; (2) the gates lifted, the guard at four rules, selection proven scoped, the five closes done (with any ACT); (3) memory landed and proven, and the roles, skills and briefs landed. Between them, the status block plus at most five lines at each step.
- **How it is applied:**
  - **Item 1, 5:** `.gov-runtime/scratch/orchestrator/tools/close_build.py` (clean clone of the head, store rebuild, the selection, the run under one lock, a failing case re-run alone, the FULL review record, gitleaks, the close record in `governance/project/orchestration/closes/`, `tk close`, a commit with `Task: <id>` and `Implements: DEC-953`). The close queue (`close_queue.sh`), the pre-close gate, the record checks before commits, the re-pin ladder, the ratchet and history entries, the quiet windows and cut-offs, CLOSE-PENDING and the memory arithmetic of the resource gate are no longer used. The disk gate and the scratch budgets stay. A `gov close` is not run on this repository's tickets.
  - **Item 2:** pending the switch-off proposal; until it lands, the guard runs as it is and sessions keep its forms.
  - **Item 4:** `tools/select_tests.py` (the product's selection, `gov.close.select.plan`, with the governance paths left out of the change and the ticket's own merges as the change); the common lead brief names it.
  - **Item 7:** `governance/project/orchestration/DECISIONS-IN-FORCE.md`, `LIFTED-BY-DEC953.md`, `ARCHIVE-SUPERSEDED.md`.
  - **ACT-TESTMAP-1:** withdrawn. **P-W2-03-CONTAINMENT:** answered by item 5. **ACT-REPIN-3:** withdrawn (no re-pins for this repository's closes).
- **Where it goes (DEC-851):** this register; the prompt (v3.45: a DEC-953 section ahead of the rest, which it overrides); the common lead brief; the decisions-in-force list; RESUME HERE; the plan (item 10, for the owner's approval).

| Version | Date | Change |
|---|---|---|
| 0.336 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-953 (AUDIT-GOV-FEATURES-1, option (a) amended: every Gov OS feature lifted as a gate on this repository's own development; closes on the audit's 10 practices; the guard at four rules; the nightly a plain full run, reds investigated at once and holding nothing; one test-selection tool at every level, governance files left out; the five closes now; memory and K3 first, then EXAMIN's minimum; gov close proved on W2-81 and EXAMIN's copy; decisions compacted; three-layer orchestration planned; working with the owner unchanged; the updated plan first). Next free id: DEC-954. |

### DEC-959 — The owner's decisions on ROLES-RESEARCH-1 and P-W2-H064: a local merge queue, the push the owner's, the QA engineer per stream in batches, the work order in parallel, one skill template, the opaque acceptance runner now, and the path-map check fixed (standing)
- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-954, DEC-957, DEC-958, MR-3, MR-4, ADR-0001 · **Changes:** DEC-957 (the work order's sequence; the QA engineer), DEC-953 item 4 (how often tests run) · **Basis:** `packages/ROLES-RESEARCH-1.md`, `packages/P-W2-H064.md`; ACT-GUARD-FIX-1 committed by the owner (`c3392f46`, option (a)) · **Changed by:** DEC-968 (item 1: "full only for core" ended; the full suite only in the nightly) · **Class:** kept (items changed: (1) kept; (2) kept; (3) superseded §3.6; (10) superseded §2.2; (4)-(9) history)
- **Decision (everything here lands in Wave 2, before EXAMIN: Wave 2 closes, then EXAMIN is adopted, then Wave 3):**
  1. **RR-Q1, (c) the local merge queue.** Senior Engineers approve their stream's tickets; the CTO's tool tests each candidate merge and advances `w2/integrate` only when green. **Tests run no more than this:** the lead runs the scoped set once before returning; the QA engineer re-runs nothing (it reads the tests, the code and the results); the merge queue runs the scoped set once per batch on the merged result, and skips the run when the merged code is identical to what the lead tested; the close cites the merge queue's run; the full suite runs only in the nightly and for tickets that change the core.
  2. **RR-Q2:** the push stays the owner's.
  3. **RR-Q3, with batching.** The QA engineer (reads the tests and the code, changes neither, writes only its findings report) works per stream. Tickets that touch the core (the guard, the close, memory's retrieval, anything that could fail open) are QA'd individually before they merge; the others in batches of up to about five tickets, more when the tickets batch well and the machine and the context allow; a large stream's QA is split. The independent auditor keeps the milestone audits.
  4. **RR-Q4:** the domain skills after ACT 2, still in Wave 2.
  5. **RR-Q5:** one skill template, with three test scenarios written first. Existing skills are imported where they fit (Anthropic's collection and others), each with its licence checked and passing its three scenarios before it is adopted.
  6. **RR-Q6:** the opaque acceptance runner before ACT 2, as a priority now: the five-rule guard lets engineers read the acceptance tests, so "pass or fail only" needs the runner to enforce it.
  7. **The work order in parallel:** the test designer and the engineer work on a ticket at the same time, both from the spec. The engineer still runs the acceptance tests once they are ready, even if it finished or stopped earlier; the Senior Engineer or the ticket lead coordinates this, with a watcher if needed.
  8. **The proposed tickets (ROLES-RESEARCH-1 §5.3, items 1 to 13) are approved.** The spec-writing skill also covers test data: the spec states what data the tests need, whether imported (such as messy public repositories) or built synthetically (such as the 48 memory questions), and who secures it and how (licences, privacy, no secrets). Data that cannot be secured is escalated, never skipped.
  9. **P-W2-H064, (a): the ticket is filed.** A check that checks nothing is fixed in Wave 2: other checks and adopted repositories rely on it. Adopting a messy repository means refactoring it into a new path map, which this check validates and keeps valid.
  10. **ACT-GUARD-FIX-1** (owner, `c3392f46`): w2/integrate is merged into each worktree before its next lead or reviewer starts; running leads keep their old hook until then, and their refusals are still logged (DEC-958). The remaining gap (a separate script file writing into the acceptance tests) is a Wave 3 hardening row.
- **Until the merge queue lands,** closes run as DEC-953 item 4 and `close_build.py` state; the lead's single scoped run and the "QA re-runs nothing" rule apply from now.
- **Where it goes (DEC-851):** this register (DEC-957 and DEC-953 marked "Changed by"); the prompt §0 (v3.49) and §6; the common lead brief (the work order in parallel, the engineer's run of the acceptance tests once ready, one scoped run); the decisions-in-force list; RESUME HERE; the tickets of §5.3 and W2-95; ROLES-SPEC-1's tickets W2-33, W2-60b, W2-11, W2-83b.
- **Swept (DEC-866), to update through their owning tickets:** "tests first / written before implementation" in the prompt §6 step 1 and Appendix A1, the common lead brief's loop, the kernel's test-design skill and orchestration skill (W2-11 r1, CIT-P), and the `acceptance_tests.author` lines of open tickets (kept for tickets already in flight, with this reason: their tests are written).

| Version | Date | Change |
|---|---|---|
| 0.342 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-959 (the merge queue, the push the owner's, the QA engineer per stream in batches, domain skills after ACT 2, one skill template with imports, the opaque runner now, the work order in parallel, §5.3's tickets approved with test data in the spec skill, P-W2-H064 (a), ACT-GUARD-FIX-1 applied). Next free id: DEC-960. |

### DEC-961 — The machine is shared by capacity alone: no memory set aside for full runs, no close or night holds, the nightly holds nothing; the remaining holds listed for the owner (standing)
- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-954, DEC-947 item 5, DEC-898 · **Supersedes:** DEC-960 · **Changes:** DEC-947, DEC-942 items 4 and 5, DEC-939 item 6, DEC-933 item 2 · **Basis:** the owner's message of 2026-10-30; `packages/HOLDS-REVIEW-1.md` · **Changed by:** DEC-984 ("the nightly takes no lock and holds nothing") · **Class:** kept (items changed: (1)-(2) kept; (3) changed by DEC-984; (4) history)
- **Decision:**
  1. **No memory is set aside for a full test run** (the 7.4 GiB verification peak). The gate counts the floor, each running lead at what it uses (at least its working size) and the newcomer. A full run (a close's, the nightly's, a lead's) gets its place like anything else: it checks the gate before it starts (`gate_check.py --full-run`, room for its own measured peak) and waits until there is room. The floor and the out-of-memory trip-wire stay as they are.
  2. **No hold for a waiting close** (CLOSE-PENDING) **and no 00:30 to 05:30 window** for launches. Closes, scoped test runs and new leads run side by side whenever the gate's capacity allows and their paths don't conflict.
  3. **The nightly starts at 02:00 on its window and holds nothing else:** at night it takes no verification lock; it waits for the gate's room for one full run until its latest start, then starts anyway; leads and closes keep starting during it as capacity allows. Its failures are re-run alone as now, so a red caused only by load is filtered out.
  4. **Every rule still in force that holds a lead, a close or a test run beyond the gate's capacity check** is listed for the owner's review in `packages/HOLDS-REVIEW-1.md`.
- **How it is applied (2026-10-30 23:30 to 00:00 GMT):** `tools/gate_check.py` (no reservation; `--full-run` mode); `tools/verify_lock.sh` and `tools/close_build.py` wait for `--full-run` before a full run; `tools/lead_chain.sh` and `lead_chain2.sh` drop the close and night holds (the running chain restarted); `governance/project/orchestration/nightly/nightly.sh` waits for the gate instead of the lock at night (reviewed by an independent read-only reviewer, PASS with three small fixes applied; `test_nightly.sh` PASS); the common lead brief drops the quiet window, the 01:00 cut-off and the nightly's hold, and its lead-side load wait becomes the gate's own load test.
- **Found (my slips, DEC-866):** DEC-953 had already lifted the memory arithmetic as a gate, the CLOSE-PENDING hold, the night window, the 01:00 cut-off, the close's quiet window, the nightly's hold on leads and the interim rebuild lock, but the tools and the common brief still enforced them. All are now removed except the rebuild lock and the nightly's booking of its own window, which are listed for the owner (HOLDS-REVIEW-1 §C).
- **The effect, measured at 23:40 GMT (4 leads running, MemAvailable plus the leads' memory 16.4 GiB):** memory alone allows 2 more leads now (6 in all), against none before; on a machine with no leads, 6 against 3. The load (43 against 20 processors) is what shuts the gate now.
- **Where it goes (DEC-851):** this register (DEC-960 superseded; DEC-947, DEC-942, DEC-939 and DEC-933 marked); the prompt §0, §3 and §15 (v3.51); the common lead brief; the decisions-in-force list; the tools named; RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.344 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-961 (capacity alone: no reserved verification peak, full runs check the gate themselves, no close or night holds, the nightly holds nothing; HOLDS-REVIEW-1 for the owner). Next free id: DEC-962. |

### DEC-963 — P-PARALLEL-1 (b), amended: the test designer in its own worktree, retrieving only from the integration branch's store; the engineer in the ticket's worktree (standing)
- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-959 item 7, DEC-962 item 4, DEC-820 (c), MR-3 · **Basis:** `packages/P-PARALLEL-1.md` · **Changed by:** DEC-966 (the designers' store is refreshed at most twice a day, morning and evening, or on request) · **Class:** kept
- **Decision:** option (b), with the owner's amendment.
  1. The lead adds a tests worktree, `~/gov-os-worktrees/<W2>-tests` (branch `w2/<W2>-tests`, from the ticket branch's head). The test designer works and commits only there. The engineer works in the ticket's own worktree. Each worktree has one writer, and the two start at the same time from the spec and the KPIs.
  2. **The amendment:** the test designer's retrieval uses the integration branch's store, never the ticket worktree's, so its searches can never surface the engineer's in-progress code.
  3. When the tests are committed, the lead writes `.gov-runtime/scratch/lead/TESTS-READY`. At its next step, or when it has built, the engineer merges `w2/<W2>-tests` into its tree and runs the acceptance tests once, reading results only (through `gov accept` once W2-96 lands). If the engineer has already ended, the lead merges and a fresh engineer runs them once. The lead removes the tests worktree and branch before returning.
- **How the amendment is applied (the orchestrator's reading, for the owner to overturn):** the main tree's own store goes stale at every record commit, since its head moves with them; at 23:58 it answered `FACET_UNAVAILABLE` ("stale"). So the integration branch's store lives in its own detached worktree, `~/gov-os-worktrees/W2-00-store`, at `w2/integrate`'s head. The CTO rebuilds it after code merges with `tools/refresh_integration_store.sh` (first build started 23:59). It never holds a ticket's in-progress code, and record commits do not make it stale. Test designers run `cd ~/gov-os-worktrees/W2-00-store && gov retrieve "<question>"`. **Double-buffered (2026-10-31 00:57):** `W2-00-store` is a link to the ready one of two detached worktrees (`W2-00-store-a`, `-b`); a refresh builds the other at the new head and switches the link only when its build succeeds, so the store never answers "stale" while it rebuilds (the first build took 3,459 s at load 45). Checked: `gov retrieve` (the pinned gov) answers there with both facets available.
- **Where it goes (DEC-851):** this register (DEC-962 marked); the prompt §0, §3, §6 and briefs A1 and A2 (v3.53); the common lead brief (the loop, rule 6's wording); the decisions-in-force list; the queued briefs (W2-96, W2-95, the nine resumes); W2-33's and W2-83b's tickets (role files and playbooks); RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.346 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-963 (P-PARALLEL-1 (b), amended: the test designer in its own worktree, retrieving only from the integration branch's store; the engineer merges its tests and runs them once). Next free id: DEC-964. |

### DEC-968 — The full suite once a day, in the nightly, and nowhere else; a close refused only by a failure its own change caused; every other failure dealt with at once (standing)
- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-953, DEC-959, DEC-961, DEC-962 · **Changes:** DEC-953 item 4 and §0's close rule, DEC-959 item 1 · **Basis:** `packages/P-CLOSE-ATTR-1.md`; the batch of five's run of 2026-10-30 22:45 to 2026-10-31 01:31 · **Changed by:** DEC-1049 (1) · **Class:** kept (items changed: (4) history)
- **Decision (the owner's three rules, with tonight's cases):**
  1. **The full suite runs once a day, in the nightly, and nowhere else.** No lead, close or merge runs it, core tickets included (for example W2-107 and W2-106, which change the core): they run the scoped set, their own acceptance tests plus every suite the selection says the change can reach. A break the selection missed is found by the nightly the next morning, traced to that day's merges and handled as decided.
  2. **A close is refused only by a failure its own change caused (P-CLOSE-ATTR-1 (a)).** Each case that fails alone is re-run without the batch's merges (the same head, the merges reverted). If it still fails there, it is not the change's: the close goes on and its record names it. If it passes there, the close is refused. A merge that cannot be reverted refuses (untraced). Tonight's batch of five would have been refused by seven failures, none from its five tickets: three from the orchestrator's record commits, the rest W2-54's known load failures.
  3. **A failure the change did not cause is still dealt with at once, like a nightly red:** small and clear, fixed on the spot and reported (the three record slips, fixed `730636ba` and `00cc7bcf`); otherwise investigated now and brought to the owner with the fix or as a P1 with a recommendation (W2-54's load failures). Nothing goes on a list to sit there: no new accepted reds.
  4. **Applied now:** the batch of ten merged tickets (W2-57, W2-77, W2-03, W2-26, W2-61, W2-85, W2-51, W2-87, W2-64, W2-90) closes on the scoped set on the current head (`CLOSE-HEAD` removed); W2-76's full run already going may finish.
- **The aim (the owner's words):** no machine time spent running 17,000 tests for no value, and no ticket held back by a red it didn't cause, while every red still gets fixed.
- **How it is applied:** `tools/select_tests.py` takes out the product's two shortcuts to "everything" (shared core; a file nothing places) and names them (`core_changed`, `unplaced`); any other reason refuses the selection (exit 2). `tools/close_build.py` runs the scoped set (a batch the union of its tickets'), traces each red alone on a clone with the batch's merges reverted, writes the not-caused ones to `unowned.txt` and the close record, and has no full mode. The 13 merges of tonight's ten tickets were checked to revert cleanly on the head. The common lead brief, the prompt §0 (v3.55) and the decisions-in-force list say so.
- **Where it goes (DEC-851):** this register (DEC-953, DEC-959 marked); the prompt; the common lead brief; the decisions-in-force list; the tools named; the queued briefs; RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.351 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-968 (the full suite only in the nightly; a close refused only by a failure its change caused; every other failure dealt with at once, no accepted reds). Next free id: DEC-969. |

### DEC-972 — P-PING-1 (a) plus (d): a ping that does not stop the CTO; none at night; the blocking ping only as a daytime fallback (standing)
- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-855, DEC-945, DEC-949, DEC-971 · **Changes:** DEC-855 (how the owner is pinged) · **Basis:** `packages/P-PING-1.md`; the ping of 2026-10-31 04:05 that held the CTO's session until 11:46 · **Changed by:** DEC-973 (the quiet hours are 02:00 to 07:30) · **Changed by:** DEC-1021 (pings until 02:00; quiet hours 02:00 to 07:30) · **Class:** kept (items changed: (2) quiet hours changed by DEC-973; (3) superseded §2.3; (4) history)
- **Decision:**
  1. **(a) The ping:** the line goes to `~/.config/gov-os-notify/pings.log` by a plain logging command that asks nothing (`tools/ping_log.sh`), then Claude Code's `PushNotification` sends the same line (a desktop notification, and a push to the owner's phone while Remote Control is connected). It returns at once; the CTO's work goes on. The tool's answer ("sent" or "not sent") is written beside the line in the log.
  2. **(d) No pings at night:** from midnight to 07:30, a P1 waits for the 07:30 morning package, emergencies alone excepted (DEC-949's exception for an active owner no longer applies to pings).
  3. **The fallback:** a daytime P1 that needs the owner that day and shows "not sent" falls back, for that one, to the old blocking `owner-ping` (its ask rule stays in the owner's settings for this).
  4. **First, a test:** one test notification, sent while the owner is away from the terminal; the owner says whether it reached the phone. **Done 2026-10-31 12:58:** "mobile push requested"; the owner confirmed it reached the phone. The first try at 12:51 was "not sent" (the owner was at the terminal), as designed.
- **Where it goes (DEC-851):** this register (DEC-855 marked); the prompt §7 and §8 (v3.57); `tools/ping_log.sh`; RESUME HERE; the decisions-in-force list.

| Version | Date | Change |
|---|---|---|
| 0.355 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-972 (the non-blocking ping, none at night, the blocking one only as a daytime fallback). Next free id: DEC-973. |

### DEC-973 — The quiet hours 02:00 to 07:30; the nightly at 04:00; its check at 08:00; the morning package at 09:00 (standing)
- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-972, DEC-933, DEC-934, DEC-938, DEC-949, DEC-951, DEC-952 item 6 · **Changes:** DEC-972 item 2 (the quiet hours), and the nightly's and the morning's times in DEC-933, DEC-934, DEC-938, DEC-949 and DEC-951 B · **Changed by:** DEC-1049 (the nightly at 04:00, its 08:00 check) · **Class:** kept (items changed: (1) quiet hours kept, not for lead-stopping decisions (DEC-1157); (2) kept; (3)-(4) history)
- **Decision:**
  1. **P-PING-1 (a) plus (d), with the quiet hours from 02:00 to 07:30:** no pings then (emergencies excepted); work keeps going at night, and decisions accumulate for the owner in the morning package. From 07:30 to 02:00, pings by `ping_log.sh` and `PushNotification` (DEC-972).
  2. **The nightly full run moves to 04:00** and runs from 04:00 to about 07:00; its window ends at 08:00.
  3. **What is timed around it moves:**
     - the Windows wake task to 03:50;
     - the CTO's investigation of any reds, and the designers' store refresh, to right after the nightly ends (on its verdict, not at a clock time);
     - the nightly's check to 08:00, with re-checks at 08:30 and 09:00;
     - the morning package, with any ACTs, to 09:00;
     - the fresh-session handover to after the 09:00 package.
  4. **The owner's ACT** (`packages/ACT-NIGHTLY-0400.md`): the crontab (the nightly at 04:00, the check at 08:00, `runs_sweep.sh` at 09:30) and the Windows wake task, run after the nightly folder's change is committed.
- **Where it goes (DEC-851):** this register (DEC-972, DEC-933, DEC-934, DEC-938 marked); the prompt §0 (v3.58); the nightly folder (reviewed, `test_nightly.sh`); the CTO's timers and `tools/store_refresh_daily.sh`; the decisions-in-force list; RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.356 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-973 (quiet hours 02:00-07:30; the nightly at 04:00, its check at 08:00, the morning package at 09:00, the handover after it; ACT-NIGHTLY-0400). Next free id: DEC-974. |

### DEC-979 — The owner's decisions on CAPACITY-1, the stores, batch closes and the order of work (standing)
- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** CAPACITY-1 (`packages/CAPACITY-1.md`, `bde35d69`), DEC-974, DEC-975, DEC-968, DEC-906, DEC-969 · **Changes:** the leads' load wait (the common brief) once the heavy-job limit runs; DEC-976's option (b) (settled); DEC-974 item 3 (decided); the lead queue's order · **Changed by:** DEC-1157 (10), DEC-1164 (9) (D1's slots re-sized from the wait log; a starved slot released by the CTO) · **Class:** kept (items changed: D1 heavy-job slots and D3 tools lane kept; D2,D4-D6,(2)-(5) history)
- **Decision:**
  1. **CAPACITY-1:**
     - **D1 (a):** a machine-wide heavy-job limit replaces the leads' load wait: test runs and rebuilds take one of a few slots and wait for one; sessions, reviews and single-process runs run freely. Its slots are sized from the re-measure after W2-107, so that the load stays near the number of processors (20). Every status block shows the load. Until the limit runs, the load wait stays as it is.
     - **D2 (a), P-LATENCY-1:** a fresh independent test designer revises the 11 hook-latency cases (W1-02's, W1-05's and W2-57's p95 under 100 ms) to time the hook's own work, at the same 100 ms, lowering nothing; this decision is the P1 that files its ticket (DEC-974), after W2-90b (W1-05's file shared).
     - **D3 (a), P-TOOLS-LANE-1:** the CTO's own tools and scripts (the close tool, the selection, the gate, the watchers, the samplers, the brief builders, the nightly folder) are not product work: each has its own tests, run before use; an independent review only when a change could fail open (let a red or a refusal through, widen a gate) or lose work (kill, delete, lock, overwrite); each change logged in the daily document's "Tools changed" section; never a WBS ticket (commits `Task:` W2-00).
     - **D4 (a), P-W2-108-BATCH:** no query-embedding batching; the remaining time of the context check at load is profiled first.
     - **D5 (a):** W2-90b, filed by the CTO under delegation, is approved as filed.
     - **D6:** settled by D1 (single-process runs take no slot).
     - **No bigger machine now:** re-sized on the re-measure after W2-107, as planned.
  2. **The stores:** the main tree's store is rebuilt now with the integration branch's code; the designers' store is refreshed tonight; old or stale worktree stores are rebuilt when their leads next start. A store shared across clones for the embeddings (so a fresh clone does not embed every chunk again) goes into the re-measure as the next speed-up.
  3. **Batch closes, working smart:** when a batch close finds a failure its change caused, it finds the ticket that caused it (that ticket's merges taken out, the failing tests re-run without it); if they pass without it, the rest of the batch closes on the same run and only the culprit goes back. A failure no single ticket explains refuses the batch (fail closed). Applied to the close tool now, in the lighter lane with its tests, and used for the next batch.
  4. **The shared reranker:** brought to the owner as a P1 ticket proposal before the three layers, showing how it serves many sessions at once and what searches fall back to if it is down.
  5. **The order of closes and work:**
     - a. **First, what speeds up all the work:** W2-107's close; the batch of seven (W2-106, W2-84, W2-76, W2-49, W2-16, W2-67, W2-95); W2-108 after its test fix; then the heavy-job limit and the merge queue (W2-97).
     - b. **Then the critical chain:** memory (W2-86's measure, the graph routes W2-92 and full embeddings W2-91, W2-13, W2-15a, W2-32, the 48-question measure, the shared reranker) and, in parallel, the roles (W2-11, W2-33, W2-60a and W2-60b, W2-83); then ACT 2 and the three layers.
     - c. **Alongside, what EXAMIN needs:** W2-81 (the proving ground, claimed but never run), W2-88, W2-96.
     - The critical chain's files are kept clear of other work.
- **Where it goes (DEC-851):** this register (DEC-976 and DEC-974 marked); the prompt §0 (v3.61); the common lead brief (the new-worktree rebuild runs the worktree's own code; the load wait until the limit runs); the decisions-in-force list; RESUME HERE; the close tool and its tests; the lead queue.

| Version | Date | Change |
|---|---|---|
| 0.362 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-979 (CAPACITY-1 D1-D6; the stores; batch closes send back only the culprit; the shared reranker as a P1; the order of work). Next free id: DEC-980. |

### DEC-984 — The nightly takes all three heavy-job slots while its suites run (standing)
- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-979 D1, DEC-983 item 6, DEC-973 · **Changes:** DEC-961 ("the nightly takes no lock and holds nothing") for the heavy-job slots · **Class:** kept
- **Decision:** the 04:00 nightly takes all three heavy-job slots while its two suites run, so leads' and closes' runs wait for it. It waits for each slot at most until the night's latest start (an hour by day), records the slots held and the wait (kept out of the setup time), runs its suites with the slots' locks closed (nothing a test leaves behind keeps one), and releases them right after the suites, before the light steps (each red alone, the bisect). A reviewed change to the nightly folder with `test_nightly.sh` (N12 to N14). Leads' runs held past 90 minutes by it return PACKAGES (the common brief's rule).
- **Also (the CTO's, the lighter lane):** `tools/heavy_slot.sh` now locks with `flock -o`, so a daemon a run leaves behind (the embedder `gov` starts on demand) never keeps a slot (test H6).
- **Where it goes (DEC-851):** this register (DEC-961 marked); the nightly folder; the prompt §0 (v3.64); the decisions-in-force list; RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.367 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-984 (the nightly takes all three heavy-job slots while its suites run). Next free id: DEC-985. |

### DEC-989 — The attribution baseline until a green nightly after ACT 1; a ticket's merge and close are one step (standing)
- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-988 items 3, DEC-968, DEC-959 item 1 · **Changes:** DEC-988 item 3's baseline until a fully green nightly exists after ACT 1 · **Changed by:** DEC-1045; DEC-1141 (4) (two hand merges, W2-175 and W2-176, the owner's exception to item 2); DEC-1164 (19) (item 2: a critical-path ticket lands first) · **Class:** kept (items changed: (1) history)
- **Decision:**
  1. **The baseline:** until a fully green nightly exists after ACT 1, a failure is attributed against **the last nightly that ran to a verdict**, its reds recorded as known (a red is cleared only if that nightly had it red, the same failure); never against code made by undoing merges. Once a green nightly exists after ACT 1, the last green nightly's head (DEC-988 item 3).
  2. **No ticket sits merged but not closed:** once W2-97's merge queue lands, a ticket's merge and its close are one step. When the queue's run on the candidate merge is green, the ticket merges and closes on that run, with its close record.
- **Where it goes (DEC-851):** this register; the prompt §0 (v3.66); the decisions-in-force list; RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.372 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-989 (the last nightly with a verdict as the baseline until a green one after ACT 1; merge and close one step through the queue). Next free id: DEC-990. |

### DEC-998 — The dead-man's switch through the Claude app alone; Remote Control checked at every session start (standing)
- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-994 item 1, DEC-991, DEC-945 · **Changes:** DEC-994 item 1 (channel (b) by cron failed: a headless session has no Remote Control link) · **Class:** kept
- **Context:** push tests 1 to 3 (headless `claude -p`, cron-like) were refused "terminal active" every time; test 4 from the CTO's live session reached the owner's phone; the day's earlier misses were the presence rule (pushes skipped while the owner is focused on the connected terminal), not a broken link.
- **Decision:** (1) Claude only: no ntfy, no other app, no email. (2) The owner turns on "Push when actions required" in `/config` (a push for every permission prompt and question of a Remote Control session). (3) **Every fresh CTO session, at its start:** confirm its Remote Control link is live and send one test push; and write its session id to `log/cto-session.txt` (the switch watches that session). (4) The dead-man's switch must work through the Claude app alone: the CTO assesses a Claude-only way (a small sentinel session with Remote Control that sleeps on a background check and pushes only when the CTO's session has stalled) and brings it with its cost and risks (ACT-SENTINEL-1).
- **Where it goes (DEC-851):** this register; the prompt §1 (the start-of-session steps) and §0; the decisions-in-force list; RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.380 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-998 (Claude-only dead-man's switch; Remote Control and a test push at every CTO session start). Next free id: DEC-999. |

### DEC-1007 — The dispatcher: keeping the machine full and the work moving never depends on a session's memory (standing)
- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-999, DEC-1003, DEC-979 item 2 (the tools lane), DEC-942 · **Why (the owner's words, short):** in six hours one ticket closed; the status said 9 leads when 5 ran; four returns sat unread for hours because the return watcher was not re-armed; the machine ran at a load of about 7 of 20. · **Class:** kept
- **Decision:**
  1. **The dispatcher, tonight's top priority:** the CTO's own tool, a plain program, no AI, running outside any Claude session and restarted after a reboot or WSL restart; every minute it reads the gate (load, memory, heavy-job slots) and starts the next ticket from the ready list when there is room; notices every finished lead, puts its return in an inbox and wakes the CTO; puts every ticket ready to land into the merge queue as one batch whenever the queue is free; writes the true status (leads from the processes, the load, the queue, the inbox) to a file every status block reads.
  2. Its order comes from the plan, never its own choice: the CTO keeps the ready list in the WBS's order and dependencies and RESUME HERE's priorities, each ticket's brief built and readiness checked; the dispatcher starts only what is on it; the CTO keeps the ready list, the WBS and RESUME HERE consistent.
  3. Its state survives any session: the ready list, the inbox and the status are files the checkpoint and RESUME HERE point to.
  4. It has its own tests and an independent review before it goes on; its design to the owner in short at the start; switched on once the review passes unless the owner objects, and the owner told; aim: running within five hours.
  5. The Gov OS feature (DEC-1003): its spec and KPIs as KPI changes to W2-20, W2-117, W2-118 or a new ticket, as a P1 to the owner; it may land later as its own ticket.
  6. **Until it is on, the CTO does its job by hand** at every wake (the gate, the leads from the processes, the returns; start ready tickets up to capacity, with a reason for any not started; land every ready ticket as one batch when the queue is free; the lead count in every status block from the processes, never from memory). W2-11's queue run (over 30 more minutes) was stopped at 19:48; W2-11 and W2-105 landing as one batch on warm clones, W2-05, W2-55, W2-96 closing alongside.

| Version | Date | Change |
|---|---|---|
| 0.389 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-1007 (the dispatcher). Next free id: DEC-1008. |

### DEC-1030 — The dispatcher watches the whole machine: the GPU, its holders, each model's layers, and the servers' crashes (standing)
- **Status:** ACCEPTED (owner, 2026-11-02, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing) · **Under:** DEC-1007, DEC-1012, DEC-1015 item 2, DEC-1003, DEC-1029 · **Class:** kept
- **Context:** the GPU crashed twice in the night of 2026-11-01/02 and the shared embedder fell back to the CPU (0/29 layers); neither the dispatcher nor the morning package saw it.
- **Decision:** (1) From now the dispatcher watches the GPU: its memory and use, which processes hold it (the rerankers included), and whether each embedding model runs on it (its layers on the GPU); a crash in a server's log, or a model loading with 0 layers on the GPU, becomes an inbox item and a push to the owner at once. (2) The load-balancing plan says which work runs on the GPU (embedding, the shared reranker), how much of its memory each may take, and how the dispatcher keeps the rerankers from crowding the embedder off it. (3) The morning package reports every crash or error in the servers' logs overnight, not only the tests. (4) The same in the Gov OS (DEC-1003): the GPU as a resource the gate and the dispatcher measure and schedule (W2-20, W2-121), as KPI proposals.

| Version | Date | Change |
|---|---|---|
| 0.412 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1030. Next free id: DEC-1031. |

### DEC-1031 — The load-balancing plan now, with its target architecture; no reranker pushes the embedder off the GPU; W1-01's merge rule; SMART-WORK-6 approved
- **Status:** ACCEPTED (owner, 2026-11-02, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; item 3's last sentence standing) · **Under:** DEC-1028 item 5, DEC-1029, DEC-1030, DEC-906, DEC-253, DEC-1003 · **Class:** kept (items changed: (1) CPU-fallback clause superseded §5.8; (2)-(4) history)
- **Decision:** (1) The load-balancing plan comes now with what is at hand (the history, the live hour, last night's GPU crashes), the GPU agent's figures added when they come. Its target architecture: one shared embedding service on the GPU for indexing and queries (batched and parallel); one shared reranker on the GPU (W2-112); a GPU memory budget (the embedder first, the shared reranker second, nothing may push the embedder off); the CPU only as an alerted fallback. Whether query embedding on the GPU changes the final search answers (the determinism test) is measured now, so the query server can move too. (2) Until then, no reranker can push the embedder off the GPU: its memory reserved first (the CTO pinned the shared embedder with `keep_alive: -1` at 12:05; ACT-RERANK-CPU-1 keeps the rerankers on the CPU until W2-112). (3) P1-NIGHTLY-2026-11-02 (a): W1-01's test designer exempts a listed merge's own changes (the owner's named decision under DEC-906), and the owner commits the exemption for `0568d91baf56` when the CTO brings the ACT. Standing: a merge whose acceptance-file resolution a test designer made carries the test designer's role. (4) SMART-WORK-6 approved, all four lines (W2-20: the GPU measured and scheduled; W2-121: the GPU watched, the servers' crashes in the morning report).

| Version | Date | Change |
|---|---|---|
| 0.413 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1031. Next free id: DEC-1032. |

### DEC-1032 — P1-LOAD-BALANCE-1 decided; a freeze until the machine runs at normal speed; the infrastructure sprint (standing until lifted)
- **Status:** ACCEPTED (owner, 2026-11-02, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; the freeze standing until the owner lifts it) · **Under:** DEC-1028 item 5, DEC-1031, DEC-1029, DEC-1030, DEC-798, DEC-975, DEC-974 · **Changes:** DEC-798 and DEC-975 (the query embedder on the CPU) · **Changed by:** DEC-1033 (items 2 and 3), DEC-1157 (5) · **Superseded by:** DEC-1158 (1) (items (2), (3)(v)) · **Class:** kept (items changed: (2),(3) history)
- **Context:** ACT-W1-01-EXEMPT-1 committed by the owner (`2acc8a31`); ACT-RERANK-CPU-1 applied by mistake and undone; ACT-RERANK-GPU-SLOTS-1 applied (at most two rerankers on the GPU; tested with three processes).
- **Decision:** (1) The plan's five decisions, yes: the query embedding moves to the GPU, with its ACT; DEC-798 and DEC-975 are amended (the query embedder may run on the GPU: the determinism test on the memory measure changed no answer's pass or fail; the vectors are not bit-identical, as the CPU's are not); the vector-cache ticket is filed (each text embedded once on the machine); W2-112 (the shared reranker) before EXAMIN's copy; the GPU budget (the embedder first, about 3.5 GB; the shared reranker second, about 2.5 to 3.5 GB; at least 2 GB headroom; nothing else by default) as W2-20's default share; lever b.6 (the retrieval check's dev tiers pre-built once, not cold on every `gov check`). (2) **A freeze until the machine runs at normal speed:** no new lead starts except the infrastructure work below; W2-122 and W2-123 finish (they are part of the fix); W2-04 finishes its repair round; the landing in flight completes; everything else waits. (3) **The infrastructure sprint, in order, with what the owner must give as one package:** (i) the shared reranker (W2-112), on the GPU, starts now, at the front; (ii) query embedding on the GPU: the ACT now; (iii) the dispatcher balances the whole machine (CPU, RAM, the GPU and its memory, by measured peaks): health judged by progress (no false "hung"), new work admitted only with room on every resource, slots by device, the rerankers' memory and GPU slots counted, an alert when a model loads only partly on the GPU; the CTO's tools, reviewed, today; (iv) rebuilds: no cold rebuild anywhere: every copy (a lead's worktree, the queue's clone, a close, the nightly) seeded from the warm integration index and then embedding only what changed; the merged result's index becomes the new integration index instead of being built again; the head without the batch read from the nightly's results, never rebuilt; the vector-cache ticket starts now; the count and time of rebuilds per ticket and per batch shown before and after; (v) then a short assessment, rethinking and redesign of how leads are launched, verified, landed and closed, judged on what (i) to (iv) achieved (what stays, what changes, how many rebuilds a ticket and a batch truly need and why, the throughput it should reach in closes a day), decided by the owner before the freeze lifts. A report at each step's end; the owner told when the targets are met: no timed-out embedding, no cold rebuild, the GPU stable within its budget, busy cores in their band.

| Version | Date | Change |
|---|---|---|
| 0.414 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1032. Next free id: DEC-1033. |

### DEC-1047 — The emergency raised one level: everything stopped but the memory infrastructure; a harsh investigation of what to lift, measured against the Gov OS's aim; DEC-1010 stays
- **Status:** ACCEPTED (owner, 2026-11-02 ~21:40, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing until the owner lifts it) · **Under:** DEC-1039, DEC-1045, DEC-1033, DEC-1010, DEC-953 · **Changes:** DEC-1039's order (the investigation and the owner's decisions on it come before steps 2's refactor, 3 and 3b) · **Changed by:** DEC-1049, DEC-1051 (item 1) · **Superseded by:** DEC-1158 (1) (items (1), (2)) · **Class:** kept (items changed: (1)(2) history DEC-1158)
- **Why (the owner's words, in short):** for two weeks the machine was fought instead of the product built; process meant to protect became the work. Gitleaks guarding a private repository ran on every rebuild, landing, close and test run (W2-69's tests alone started about 120 gitleaks from one slot; load 54 to 76 on 20 CPUs); per-session rerankers crashed the GPU; cold rebuilds; checks and ceremonies everywhere, every time.
- **The aim (the yardstick):** the Gov OS stops drift and makes the owner's agents work, and record their work, as a good software company does; not a security battle, not a rule battle. It needs: a good tool extending the agents' memory (RAG and combined memory); help developing the spec and the KPIs (research and discovery agents) and their execution by other agents; roles whose permissions keep apart work whose interests conflict (the builder never writes or reads its own acceptance tests; the reviewer never fixes what it reviews); governance of the WBS and of tickets' launching and closing with well-structured dependencies ("governing the traffic, not governing a city"). What matters is tests and code that match the KPIs and the spec and pass green; everything else must justify itself.
- **Decision:** (1) **Stop** every ticket and lead now, at safe points, except the memory infrastructure: W2-112 finishes its last review round (done; P-W2-112-F9 with the owner), W2-126 finishes, the W2-122 + W2-123 landing completes. W2-42a stopped at a safe point (both agents). The Load Balancer stays on. DEC-1045 applies as decided (the orchestrator's reading: its product switch, an application of DEC-1045, continues). Nothing else starts. (2) **The investigation**, harsh, read-only, in chunks across parallel agents within the Load Balancer, one agent combining the findings into one list without duplicates: (a) ten named practices to start with (the full `gov check` in every lead's verification; real-model tests W1-19, W1-21 in tickets' runs; the guard's ~9,000 tests in tickets' runs; `gov context` loading the whole register for every cited decision, 1.6 million tokens against 6,000; the 56,000-character lead briefs; the guard-refusal harvest re-scanning every transcript every minute; attribution re-running each red three times with and without the batch; tests starting their own code-graph daemons; review effort not matched to risk; the ceremony around small decisions), and every other problem of the kind; (b) the Gov OS itself (its rules, gates, checks, records and ceremonies, the guard's rules included, and the code and tests that exist only to build or enforce them); (c) the CTO's own tools and practices; (d) the WBS and the tickets (which tickets and KPI lines exist only to build, extend or polish what is to be lifted; which are still needed for the aim; which can be merged or retired; feeding DEC-1039 step 3b). For each: its cost (machine time, tokens, the owner's time), what it protects, and the recommendation (lift, scope to the change, move to the nightly, keep). The benchmark is DEC-1010's test: a rule, check or ceremony earns its place only where what it guards against is within the aim, reachable in ordinary work, and would otherwise fail open or lose work; anything else that blocks or slows work is bureaucracy, recommended lifted. And one question answered with reasons and costs: copy what works into a fresh repository and start over with less bureaucracy, or keep this repository and lift and refactor here. **The list comes to the owner first; nothing is lifted before the owner decides.** (3) **What stays, whatever the investigation finds:** DEC-1010 (a moderator triages every finding against the ticket's own scope and KPIs; a finding blocks only if in scope, reachable in ordinary work, and failing open or losing work; at most two review rounds, then the owner once; READY computed by code, `verdict.py`, from each reviewer's structured verdict, never declared by an agent).

| Version | Date | Change |
|---|---|---|
| 0.430 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1047. Next free id: DEC-1048. |

### DEC-1052 — P1-LIFT-1 and P1-PLAN decided: the basis, the rows, the templates with READY and DONE by code, the test suite cut to about 5,000, the homes, the updated plan, tonight's restart
- **Status:** ACCEPTED (owner, 2026-11-02 ~23:58, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing) · **Under:** DEC-1047, DEC-1050, DEC-1051, DEC-1010, DEC-1039 · **Changes:** DEC-1003 (a practice enters the product only after it has proven itself in use), DEC-851 item 1 and DEC-943 item 1 (the templates' four recommendations), DEC-957's review effort kept, DEC-1039 steps 2, 3, 3b and the order of the plan · **Changed by:** DEC-1055, DEC-1157 (3), DEC-1164 (2) (the plan bullet and "Tonight" spent; D-11 its own line) · **Class:** kept (items changed: (templates/READY and DONE by code, basis, path-map roles) kept; suite cut, homes, plan, restart history; ACT rule superseded §2.10)
- **The basis (standing):** everything is judged on one question: does it help deliver tests and code that match the KPIs and the spec, with less drift? In order: (1) does it serve memory, spec-and-KPI development, role separation, or the traffic of tickets; (2) without it, would ordinary work fail open or lose work (DEC-1010); (3) does it run only where the risk is (the change, or the full suite), not everywhere every time; (4) does it make agents deliver more with less drift, or only add records, approvals and pings; (5) a practice enters the product only after it has proven itself in use, never the same day.
- **The rows** (`packages/INVESTIGATION-1-COMBINED.md`): **approved:** T-2, T-3 (first), T-6 to T-11, T-13; Q-2 to Q-14; G-4 to G-9, G-13; M-2, M-3, M-5, M-6; R-6, R-7, R-9, R-10, R-12, R-13; O-5, O-8, O-9, O-11, O-12, O-13; K-1 to K-4; W-1 to W-10. **R-1 to R-5, O-1, O-2, O-4:** no cuts; the templates replace them. **O-3 refused:** a fresh CTO session every day; orchestrators keep long contexts. **O-6:** ACTs are for machine changes (installs, services, crontab) and only where they help; restarts of the repository's own servers from committed configs are approved by class; no ACTs for records. **G-12 refused:** review effort stays as it is. **G-3:** the hidden half of the memory measure moves outside every worktree, so no guard rule is needed for it. **G-14:** role separation is enforced deterministically from the path map: each role's reads and writes are its paths; the engineer never reads the acceptance tests; the test designer never reads the engineer's new code (it may read the integrated code, DEC-963); simple path checks, no shell guessing; repeated QA findings mean the spec is missing something and go back to product-spec. **M-1:** W2-04 accepted as built; no more runs on it. **M-4:** memory embeds the WBS, the specs and KPIs, the tickets, the code and the decisions; tests and the close, checkpoint and probe records are not embedded (they stay in keyword search, and tickets link to their tests); W2-61's measure before and after. **E1 and R1-21:** yes, inside the refactoring, E1 before the guard ACT. **Option A:** the product switches are re-scoped tickets after the resume.
- **The templates:** the four recommendations approved (TPL-1 to TPL-8 as one package, the three scripts first; lines waiting on decisions become switches in the facts file; DEC-851 and DEC-943 narrowed for templates: a line only where it changes what is done, one owner, product-spec writes and the CTO approves, gaps closed by a tool or a measured line; the six measures report only). **READY and DONE are computed by code from the filled templates** (the required fields: non-goals, how each KPI line is verified, the definition of done), as `verdict.py` computes READY from a review; not warnings.
- **The test suite:** before the full suite runs (P1-12), cut from about 19,000 cases to about 5,000 or fewer, every kept KPI line still covered by at least one test. Start with the guard's ~9,000: keep what the five rules need; the cases of lifted rules and the breadth of roles x tools x input forms go, or are reduced to representative cases. Tests of features that stay built but off (the strict close, the full guard and the like) leave the full suite: per group, delete or keep as an opt-in suite outside the full run (proposed). Test designers do it, with one independent reviewer; the list of deletions and merges comes to the owner first; the count and the full suite's expected time before and after shown.
- **The homes:** every decision lands in its home ticket as KPI lines in the WBS refactor (P1-8), or a new ticket where none fits: the templates and READY/DONE in the roles, skills and briefs tickets (W2-11, W2-33, W2-60a/b) and TPL-1 to TPL-8; the path-map role separation in the roles tickets and the guard's re-scoped ticket; what memory embeds in the memory tickets. One short note of the owner's intent (`governance/project/orchestration/INTENT-DEC-1052.md`: the basis, the templates, deterministic READY and DONE, the path-map roles) that every affected ticket points to.
- **The plan, updated** (`packages/LIFT-1/P1-PLAN.md`, its "DEC-1052" section first): no run uses the old way from now on (every run carries the lifts: gitleaks off, no full suite but P1-12's, scoped selection, attribution once each way); start with the clean-up (stale worktrees, branches, scratch, dead copies, old run folders: O-8, O-13), anything unmerged that may hold work listed to the owner before deletion; then the memory branches merged directly into `w2/integrate`, accepted as built, with no queue run: W2-122, W2-123, W2-126 (an engineer resolves its conflict), W2-112 and W2-04; re-pin window 2 carries them, with its checks; the full suite on the refactored repository verifies them; then the rest of the plan as drafted, with the changes above, the test suite cut before P1-12, the tickets' refactor and EXAMIN's adoption included; the tests run per ticket shown before and after the refactoring.
- **Tonight:** `usage_watch.sh` stopped (done, about 23:57); the dispatcher stays on; the owner restarts WSL and the machine: before that, the handover (the updated plan at the top of RESUME HERE) and a morning checklist of everything to start again after the restart and how, and what must not start; then "ready for restart" and nothing further.

- **The basis as a standing practice (owner, 2026-11-03 ~00:17, added to this decision before the restart):** the basis applies to everything from now on, during the refactoring and after the emergency is lifted: any rule, decision, gate, check, mechanism or KPI line, in force or added later, that comes to violate the basis is assessed and lifted or removed. Three triggers: (1) at adoption, every new rule, gate, check, mechanism or KPI line states in one line which of the basis's five questions it passes; one that cannot say so is not adopted; (2) on symptoms, anything that repeatedly blocks or slows work (refusals, timeouts, retries, prompts to the owner, runs done again) is flagged from the logs and assessed at once; (3) weekly, a basis review of everything in force, with each item's measured cost (machine time, tokens, the owner's time). The assessment applies the five questions; the list of what should be lifted or removed comes to the owner first. It is a step of the plan after the lift (D-11).

| Version | Date | Change |
|---|---|---|
| 0.435 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1052. Next free id: DEC-1053. |
| 0.436 | 2026-11-03 | Owner (recorded by the orchestrator, DEC-861): DEC-1052 gains the basis as a standing practice. Next free id: DEC-1053. |

### DEC-1065 — No CPU fallback for embeddings; search respects role separation; the fusion as a gap if a single route beats it; the search's speed near the pin's (standing for 1 and 2)
- **Status:** ACCEPTED (owner, 2026-11-03 ~22:00, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-03)`; items 1 and 2 standing) · **Under:** DEC-1031, DEC-1052 G-14, DEC-1056, DEC-1063, DEC-1064, DEC-1055, ACT-RERANK-WAIT-1, DEC-957 (memory's target 95 %) · **Class:** kept (items changed: (3),(4) history)
- **Decision:** (1) **No CPU fallback for embeddings, anywhere** (standing): when the shared GPU embedders cannot be reached (the launch sandbox included), the search reports its semantic part unavailable, named, and answers by keywords; it never starts a private embedder on the CPU, the same rule as the reranker's (ACT-RERANK-WAIT-1). Every place a CPU embedder can still start today is found and the change put where it fits, in place before the lift. (2) **Search respects role separation** (standing): `gov retrieve`'s results are filtered by the caller's `role_paths`, as the guard filters reads: an engineer never gets its own ticket's acceptance tests through a search, a test designer never the ticket's new code (the keyword index holds the tests). In place before W2-127 opens the sandbox to the shared services and before leads restart after the lift. (3) **The five-mode comparison** gives each mode's hit@5 and full evidence on the same 48 questions; if any single route beats the fused search, the fusion (its weights, the reranker's use) is a gap even outside W2-32's menu, brought with the other gaps, and the owner decides whether W2-32's KPIs change. The aim is as high as the fused search can go: **95 % the owner's target, 100 % believed reachable**; the hidden half keeps the score honest (at least 21 of 24 at measure 3). (4) **The 4x slowdown** (W2-92's record route reading every record's title in each `gov retrieve` process) is fixed (the titles built once at rebuild, or read only when a question names a record), with a speed target per search near the pin's ~1 s, before re-pin window 3. Then D-4b goes on in the plan's order: the gaps to the owner, D-7 and measure 2, W2-32's rounds (the stores rebuilt as each needs), measure 3, re-pin window 3 and the integration store.
- **Basis:** question 1 (memory and role separation, the Gov OS's aim) and question 2 (a private CPU embedder skews the measures and loads the machine; a search that hands an engineer its own tests fails open on separation); question 4 for item 4 (agents deliver more when a search takes a second, not four).

| Version | Date | Change |
|---|---|---|
| 0.449 | 2026-11-03 | Owner (recorded by the orchestrator, DEC-861): DEC-1065. Next free id: DEC-1066. |

### DEC-1088 — Dependency mapping decided: `gov plan` (W2-136), the template's `reads:`, `needs:` and `waits_on:`, enforcement at launch; closed tickets are never edited (standing)
- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`; item (6) standing) · **Under:** DEC-1087 (5), DEC-1007 (2), DEC-936 item 3.4, DEC-899, DEC-235, DEC-1052 · **Source:** `governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md` · **Changes:** DEC-936 item 3.4 (the planner's dependency half moves from Wave 3 into Wave 2) · **Changed by:** DEC-1157 (9) (item 5(a)), DEC-1164 (18) (item (6): a defect inside a closed ticket's own scope reopened by the CTO) · **Class:** kept (items changed: closed tickets never edited superseded §4.2)
- **Decision:**
  - (1) **DEPENDENCY-MAP-1 §2 is approved.** `gov plan` proposes the batches deterministically, and the orchestrator
    approves them into the ready list, so DEC-1007 (2) holds.
  - (2) **W2-136's KPI lines, and the lines added to W2-128 and W2-121, are approved,** updated to (3) and (5).
  - (3) **§5 (b):**
    - `reads:` stays wide, for information and the `READS_WIDE` warning;
    - `needs:` lists the paths whose finished state the ticket depends on, and orders tickets together with
      `waits_on:`;
    - the template asks for both, and W2-128's ready check refuses a new ticket without them, by name.
  - (4) **Timing:** W2-136 is built right after re-pin window 4, beside the experiments, tests first, so it is live at
    the lift's re-pin, before the three layers' streams start.
  - (5) **Enforcement at launch.** `gov launch` refuses:
    - (a) a lead for a ticket that is not in the approved batch, or whose waits are not met when checked at launch time
      against the current tickets;
    - (b) any session, lead or worker, when the dispatcher's gate is closed or the machine's limits would be passed.

    One recorded override, with a decision id, is shown in the plan and the log (DEC-899). Every refusal names what the
    ticket waits for: the ticket, the path or the limit. The CTO finds its home and gives its KPI lines. It lands with
    W2-136.
  - (6) **Tickets, standing:**
    - a closed ticket is never edited; any bug fix, new spec or upgrade to its work is a new ticket;
    - an open ticket may change while it is in flight, and `gov plan` recomputes the plan from the current tickets;
    - each change to an open ticket is marked on it with the decision that made it, and `gov links` flags any change
      without one.
- **Where (5) lives (the CTO, from the code):**
  - (a) is W2-136's: it holds the plan, and the launcher calls its check;
  - (b) is W2-20's: the machine-wide gate, built and held, whose lines already refuse a start while the gate is shut.
    It gains one line covering every session and the override, and lands with W2-136.
  - (6)'s flag is a line added to W2-129 (open, in flight).
- **Basis:** question 2 (agents in parallel never collide in ordinary work: an order the tool proves, enforced at launch).

### DEC-1092 — E2 accepted: "search again once" a standing practice (a package); E3-E5-DESIGN approved; the fresh 80 and the K9 bar wait for E3 to E5's results, chosen from the 138 before the 80 runs
- **Status:** ACCEPTED (owner, 2026-11-07, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-07)`) · **Under:** DEC-1085 (5), (6), (7), DEC-1087 (11), (12), DEC-1078 (3), DEC-1086 C, DEC-1091, DEC-1088 (4) · **Source:** `governance/project/orchestration/packages/LIFT-1/E2-RESULT.md`, `E3-E5-DESIGN.md` · **Class:** kept (items changed: (2) history)
- **Decision:**
  - (1) **E2 accepted:** "search again once" becomes a standing practice for agents, brought to the owner as a package
    (skills, the role templates through W2-128, hooks if needed), as DEC-1085 (5) set.
  - (2) **E3-E5-DESIGN approved as written,** each run with its runaway brake at twice its projection: E3 gives the
    agents the top 5, the top 10, the top 20, today's bundle and all 40 unranked to rank themselves, graded on the
    answer and its citation, with search-again on the best two; then E4 (the other rerankers, after the harness fix)
    and E5 (the 12,000-token bundle).
  - (3) The readers and graders see the hidden and spent sets, as in E2.
  - (4) **The fresh 80 and the K9 bar wait for E3 to E5's results on the 138.** From them the CTO brings: what to
    expect on the fresh 80; every gap or fix needed so the experiments run correctly and the verdict is honest; and a
    proposal for how the fresh 80 runs (possibly every experiment on it) and the K9 bar. The owner decides both before
    the fresh 80 runs. **The configuration and the bar are chosen from the 138 before the 80 runs; on the 80 every
    condition may be measured for data, but only the one chosen beforehand is judged.**
  - (5) **What stands, restated:** the fresh 80 is used once (DEC-1078 (3), DEC-1085 (7)); M3's adoption is decided
    only after all the experiments (DEC-1087 (12)); W2-137 and W2-138 land at the lift's re-pin, before the three
    layers start; W2-136 is built beside the experiments (DEC-1088 (4)).
- **Basis:** question 1 (the verdict set judges one configuration chosen beforehand; agents' practice proven end to end).

### DEC-1097 — The experiments decided: the fresh 80 judges window 4's configuration (search again once) against K9's end-to-end bar; ACT-GUARD-SETS-1 rebuilt and applied before it; a seven-reviewer readiness review; keep the 0.6B; G3 no change; the overdue items given their fates
- **Status:** ACCEPTED (owner, 2026-11-08, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-08)`), item (6) decided (b) by the owner (chat, 2026-11-08, after the 09:00 digest) · **Under:** DEC-1092 (4), DEC-1095 (3), DEC-1087 (12), DEC-1083 (2), DEC-1084, DEC-1082 (3), DEC-1090 (4), DEC-1093, DEC-1094 (1), DEC-1096, DEC-1088 (6), DEC-1052 · **Source:** the owner's message (chat, 2026-11-08), after reading FRESH-80-1, FRESH-80-READINESS, M3-ADOPTION-1, GLOSSARY-1, ACT-GUARD-SETS-1 and DECIDED-NOT-DONE · **Changed by:** DEC-1179 (2), a 95 % bar beside (1)(d); DEC-1164 (7) ((1)(g)'s and (9)'s holds for the 80 spent) · **Class:** kept (items changed: (1)(a),(5) kept; (1)(d) superseded §5.2; (2) superseded §2.10; rest history)
- **Decision, the experiments:**
  - (1) **FRESH-80-1:** (a) the configuration judged is window 4's pin (`pin-bcea09060ebc`), the pool on, today's
    bundle (6,000 tokens), search again once (A2); (b) at window 4's commit `c00d525f`, with the visible-40 control
    first (within 2 of E0's 34); (c) every experiment runs on the 80 for data, and only the configuration in (a) is
    judged (FRESH-80-1 §3.4); (d) **the K9 bar:** right end to end at least 85 % with wrong claims at most 5 %, target
    95 %, hit@5 reported beside it (on 79: at least 68 right, at most 3 wrong claims, FRESH-80-1 §4.3); (e) the readers
    and graders read the 80; (f) the owner's checker's staleness pass first, with the CTO's brief
    (FRESH-80-READINESS §2); (g) the twenty fixes and the fault rule as written (FRESH-80-1 §2, §3.5), including the
    stricter grade as data, the nonexistent-id rule, and no commit, rebuild or GPU window during the run; the CTO's
    hold on W2-139 and W2-140 until after the 80 confirmed.
  - (2) **ACT-GUARD-SETS-1:** rebuilt against today's live files, with the 80's reader-run folder added to the hidden
    globs, and W2-84's hidden-half test cases deleted with it (DEC-1061 (4)); rehearsed end to end (DEC-1057), then to
    the owner's operator; applied before the 80's single use; the live worktrees get the merge the same day.
  - (3) **The readiness review:** approved as proposed (FRESH-80-READINESS §5), seven independent read-only reviewers;
    fixed before the 80 only what fails open or would make the verdict wrong, in at most two rounds; the rest become
    rows (DEC-1010). If anything in retrieval changes, E0 and E2 rerun on the 138 before the 80.
  - (4) **The release:** if retrieval changes after the verdict, the 138 are measured again at the release commit
    before it is cut (E0's figures and E2's A2, McNemar against the verdict commit's), a fixed step in W2-27's item (a).
  - (5) **M3-ADOPTION-1:** keep the 0.6B (branch (c)); M3 and M1 measured on the 80 for data only.
  - (6) **GLOSSARY-1: (b)** (the owner, 2026-11-08, after the 09:00 digest): kept in Wave 2; redesigned beside the
    agent's own words (never in place of them), ranked toward decisions and ticket titles and definitions, and for
    asking; retested on the 138 after the 80, declared first, against E2; `gov glossary` (W2-143, W2-144) built only
    if the retest helps. Not in the fresh-80 configuration; the prototype's figure on the 80 is data only.
  - (7) **G3 (overlapping slices):** no change before the 80; a ticket after the lift if the review finds it worth it.
- **Decision, the overdue items (DECIDED-NOT-DONE §2):**
  - (8) **Before the lift's re-pin:** W2-141 (tests first, built, reviewed); W2-20 rebuilt to its launch line
    (DEC-1088 (5)(b)) and W2-136's F2 entry criterion, reviewed and merged; ADR-0002 refreshed, reviewed and brought to
    the owner (DEC-1093 (3)); a new ticket for "no private reranker beside the shared service" (DEC-1048 (5),
    DEC-1046 (1)), tests first, built before the lift.
  - (9) **Now, on the CPU, with no commit on integrate during the 80's run:** W2-130's link clean-up and the
    110-decision list with the CTO's proposal per id, for the owner's sitting (DEC-1074 (7) O2); the P-SELECT-GRAPH
    trial (DEC-1062), research only, its result to the owner.
  - (10) **G1's "fewer scored pairs"** (DEC-1094 (1)): not before the 80; brought to the owner after the lift as an
    option, the 138 re-measured if adopted.
  - (11) **P-LB-PRODUCT-1** (DEC-1048 (3)): folded into the three-layer plan after the lift (DEC-1087 (13)).
  - (12) **Q07 and Q14** (DEC-1070 (13)): re-worded by an independent session after the 80 and before any re-measure
    of the 138; the visible 40's category gaps (DEC-1074 (8)) go to the next label audit.
  - (13) **The label audit** (DEC-1070 (14), DEC-1076 (5), DEC-1078 (4)): at each release cut and before any new
    verdict set is written; the rubric's next version (v3) written after the 80.
  - (14) **The embedder trial** (DEC-1068 (b), DEC-1079 (d), DEC-1085 (4)): parked as a Wave 3 row.
  - (15) **The keystone count:** computed from the plan's list, not from tags (K7-W2-REMAINDER §5). **The old window
    scripts** with the F1 restore defect (`drafts/d4b/live_window.sh`, `score_once_window.sh`): fixed or retired,
    never reused as they are.
- **The order:** the guard ACT rebuilt, the fresh-80 scripts built and reviewed, the owner's checker's pass and the
  readiness review in parallel, with item (9) beside them; then the ACT applied, the pre-flight and the control; then
  the 80. The CTO tells the owner when it is ready to launch.
- **Standing (from the audit):** every decided item with a stage trigger is entered in
  `governance/project/orchestration/packages/DECIDED-NOT-DONE.md` when decided, and ticked off with its commit when
  done; each session reads it at start.
- **Basis:** question 1 (the verdict judges memory as agents use it, chosen beforehand, on a set used once) and
  question 2 (the 80 protected by the guard, and the overdue items given an owner and a trigger, so nothing decided is
  lost).

### DEC-1098 — The fresh 80 accepted and the measured configuration made Gov OS's memory standard; P-SELECT-GRAPH closed (do not build) with three cheaper fixes to propose; W2-130's sitting accepted; a sandbox-and-guard experiment before W2-56; ADR-0002 accepted; the work restarts in order
- **Status:** ACCEPTED (owner, 2026-11-09, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-09)`); item (1) standing · **Under:** DEC-1097, DEC-1083 (2), DEC-1062, DEC-1073 (5)(a), DEC-1074 (7) O2, DEC-1093 (3), DEC-1072 (2), DEC-799, DEC-1088 (6), DEC-1052 · **Source:** the owner's message (chat, 2026-11-09), after FRESH-80-RESULT, P-SELECT-GRAPH-RESULT, W2-130-SITTING and ADR-0002-REFRESH · **Changed by:** DEC-1179 (7); DEC-1164 (7) ((6) spent at the lift); DEC-1128 (4): item (4)'s sandbox experiment loses set-up B (dropped entirely, not a Wave 3 row); set-up A stays · **Class:** kept (items changed: (1),(2) kept; (4) superseded §2.2; (3),(5),(6) history)
- **Decision:**
  - (1) **The fresh 80 accepted; K9's memory line is met** (FRESH-80-RESULT: right end to end 78 of 79, wrong claims
    0). **Standing:** the measured configuration (the 0.6B reranker, the pool on, today's 6,000-token bundle widened to
    sections, and agents searching again once) is Gov OS's memory standard, and the memory-building practice for every
    adopted repository: built at its Wave 0 as W2-88's practice record describes, and proven there with its own tuning
    set and a fresh verdict set, measured once. The CTO brings W2-88's lines for it as a package.
  - (2) **P-SELECT-GRAPH:** (a) "do not build" accepted for test selection; DEC-1062's trial is closed. (b) The CTO
    drafts its three cheaper fixes as proposals: the test-map couplings; W2-66's record-only case in the always-run set;
    a scoped selection on every commit outside a ticket that touches settings, the registry or the test map. The code
    graph stays in memory as the code route (definitions, callers, callees), unchanged: the CTO confirms it, with the
    code route's figures on the 138 and the 80 (the callers questions and any question where it supplied the gold).
  - (3) **W2-130's sitting accepted as proposed:** groups A to G; H1 (b), open and in-progress tickets only, W2-130's
    KPI 4 changed to say so (marked DEC-1098, DEC-1088 (6)); H2 as recommended. Applied as the record describes.
  - (4) **Sandboxing and the guard (K6, W2-56): an experiment before the leads are sandboxed.** The bar: every agent
    action judged right, no false refusal and no wrong allow, 100 %. Two set-ups measured against it: the path-map
    guard alone, and the guard with the sandbox generated from the same path map; both tuned. If the guard with the
    sandbox cannot reach the bar, the path-map guard alone is kept. Designed as a package for the owner first (what it
    measures, on which actions, and how), then run, both results to the owner before W2-56 builds anything.
  - (5) **ADR-0002 accepted now** (`packages/ADR-0002-REFRESH/`), re-read at the lift's re-pin.
  - (6) **The work restarts in the CTO's order:** item 8 (W2-141, W2-20 rebuilt, W2-142 and W2-145, tests first);
    Q07 and Q14 re-worded; W2-139 and W2-140 in one batch; the sitting applied; then D-5 and D-6 part 2; then D-10 on
    the owner's word, and the lift. Each item ticked off DECIDED-NOT-DONE when done; each new decided item added with
    its trigger.
- **Basis:** question 1 (the memory standard proven end to end on a set used once, carried to every adopted
  repository), question 2 (the guard proven at 100 % before it is widened) and question 4 (no test selector built
  without a measured gain).

### DEC-1101 — Memory quality audited periodically with fresh questions, for Gov OS and every adopted repository; the "not found" and "may be incomplete" answers counted weekly; independent writers, checkers and labellers launched automatically in walled folders, with fixed briefs the owner approves once
- **Status:** ACCEPTED (owner, 2026-11-09, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-09)`); items (1) and (2) standing, active from now; **item (1)'s cadence changed by DEC-1125 (2): weekly while development is active, monthly once stable** · **Under:** DEC-1098 (1), (4), DEC-1099 (1) Q5, (2), DEC-1100, DEC-1078, DEC-1070 (14), DEC-820, DEC-1052 · **Source:** the owner's message (chat, 2026-11-09); its item 1 repeats DEC-1100 (recorded `1d49ca86`) · **Changed by:** DEC-1179 (7) · **Class:** kept (items changed: 85 % bar superseded §5.3; hit@k reporting superseded §5.2)
- **Decision:**
  - (1) **Standing: memory quality is audited periodically with new questions,** for Gov OS and for every adopted
    repository (through W2-88). Each audit: an independent writer writes a fresh set, weighted toward what was added or
    changed since the last audit plus a sample of older areas, cross-checked in at most two rounds; measured once
    (retrieval figures, and agents right end to end with search again once) against the bar (85 %, target 95 %); an
    independent auditor classifies the misses by kind; structural fixes only, brought to the owner and judged on the
    earlier sets; the spent set joins a growing pool of earlier questions, re-run at every audit as a regression check;
    the next audit's fresh set is the verdict on the fixes. Every two weeks while development is active, monthly once
    stable. **Beside it:** agents' "not found" and "may be incomplete" answers counted from their returns and shown
    weekly in the digest; a structural-pass notice of an unindexed path resolved within a day.
  - (2) **Standing: automated independent sessions, a priority now.** Every question writer, checker and labeller is
    launched automatically, without the owner opening sessions: headless sessions in their own walled folders. From now
    for the periodic audits, the sandbox experiment's labellers (DEC-1099 (1) Q5) and the sets W2-88 needs for
    EXAMIN's copy. Independence: a fixed brief per job that the owner approves once, hashed, which the CTO may not
    change without the owner's approval; the writer chooses its content by rule (what changed since the last audit,
    from git, plus a random sample of older areas from a seed recorded before writing), not by the CTO; memory's own
    search, run outputs, the CTO's scratch and the other sessions' folders denied to them by their settings, the guard,
    and the sandbox once proven; only counts reach the CTO.
  - (3) **The order:** first what must land in the path map, the guard and the folders' settings, as one ACT for the
    owner's operator, rehearsed; then the launch script, tests first, with one review; then the fixed briefs for writer,
    checker, auditor and labeller, to the owner for approval; then it becomes the default. With the briefs: the set
    size per audit, how each wall is enforced and tested, the costs per audit (tokens, GPU, the owner's time), the home
    tickets for Gov OS and the lines for W2-88, and when the first audit runs.
- **Basis:** question 1 (memory kept right as the repository grows, judged on fresh questions) and question 2 (the
  sets' independence enforced by walls, not by trust).

### DEC-1116 — W2-128's kernel templates approved at 1bf23a0b3e77 and promoted as version 1.0.0; ACT-CLAUDE-COPIES-2: yes
- **Status:** ACCEPTED (owner, 2026-11-10, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-10)`) · **Under:** CAP-33, DEC-1050, DEC-1052, DEC-1081 (2), DEC-1115 · **Source:** the owner's messages (chat, 2026-11-10): "yes ACT-CLAUDE-COPIES-2 36ab6b62" and "Templates approved at 1bf23a0b3e77" · **Class:** kept (items changed: (1) kernel templates 1.0.0 kept as the baseline; ACT-CLAUDE-COPIES-2 superseded §2.10)
- **Decision:**
  - (1) **The templates approved** as the bytes in TEMPLATES-APPROVAL-1's table at integrate `1bf23a0b3e77` (the
    brief envelope, the ticket, the seven role templates, the key list and the kernel skills and role of rounds 1, 2a
    and 2b); W2-128's CIT-P moves to ACCEPTED and the set is promoted as version 1.0.0 of the kernel templates. The
    test-design skill's remaining CAP-38.b citations follow as a later delta (DECIDED-NOT-DONE row 89).
  - (2) **ACT-CLAUDE-COPIES-2: yes** (`yes ACT-CLAUDE-COPIES-2 36ab6b62`, class (b)), run by the operator agent.
  - (3) The owner's operator applies ACT-OPERATOR-2 once the agent has finished ACT-CLAUDE-COPIES-2.
- **Basis:** question 2 (the templates one approved source for every brief).

### DEC-1120 — RUBRIC-2: the owner's rubric of model and effort by role and criticality class, replacing OWNER-DECISION-P2-0008 §11 (RUBRIC-1); changes DEC-839 (1)-(3)
- **Status:** ACCEPTED (owner, 2026-11-10, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-10)`; standing) · **Under:** DEC-1119, DEC-1118, DEC-957 · **Changes:** DEC-839 (1)-(3); DEC-1119 (1) (the rubric found, `packages/RUBRIC-1.md`, is replaced) · **Source:** the owner's message (chat, 2026-11-10), on RUBRIC-1 · **Changed by:** DEC-1141 (3) (the "hand over past about 200k tokens" line: no token cap) · **Class:** kept
- **Decision:**
  - (1) **Criticality classes.** C3 critical: the guard, hooks, permissions, the path map, hidden sets, the operator
    agent, class (b) and (O) ACTs, the kernel and the Contract, re-pins, measurement verdicts. C2 significant: product
    code outside the controls, launch, gate and plan, test maps, schemas. C1 routine: records, docs, briefs' wording,
    scratch tools, ticket edits. C0 mechanical: counting, formatting, log triage, watching. Taken from the ticket's
    profile and paths and the ACT's class.
  - (2) **Models and effort.** Master orchestrator, sub-orchestrators (leads) and senior engineers: Opus, high.
    Engineers: Sonnet, high; on a C3 ticket, Opus, high. Independent test designers: C3 Opus, high; C2 and C1 Sonnet,
    high. Reviewers: C3 Opus, high (max only for a FULL ticket's probes or after a fail-open finding); C2 Opus, high on
    FULL, Sonnet, high otherwise; C1 Sonnet, high. Auditors and adjudicators: Opus, high. Product-spec, research, ACT
    preparers and other helpers: Sonnet, high. Independent writers and labellers: Sonnet, high; their checkers: Opus,
    high. The operator agent: Sonnet, high. Watchers, sentinel, dead-man and C0 helpers: Haiku, effort as needed.
    Build, test and schema: deterministic tools.
  - (3) **Promotion on evidence:** work that fails review twice, or any fail-open finding, moves that ticket's next
    round to Opus, with the reason recorded. Any move below this table only by a trial on two or more tickets, judged
    by an Opus reviewer. Effort high is the floor for judgement work; max only with a recorded reason; low or medium
    for C0. Hand over to a fresh session past about 200k tokens. Every spawn names its model and effort; the spend log
    records the tier, the class and any promotion.
  - (4) **Through D-10** (transitional, in the owner's brackets): engineers on C2 and C1 tickets stay on Opus, high;
    they move to Sonnet after the lift.
  - (5) **Applied:** checked against this week's tickets and ACTs (the class of each, any conflict with standing
    decisions); in practice at once for every spawn; into the product through W2-33's role defaults and W2-60a's
    launch, with the trial exception, before EXAMIN's copy, so the dispatcher, `gov launch` and the CTO's own spawns
    route by it. The next report carries an estimate of usage under RUBRIC-2 (this week re-priced by tier; the saving
    in dollars and meter points by role and in total; the week's projected end with and without it; the confidence).
- **Basis:** question 4 (each task on the model and effort its class calls for).

### DEC-1134 — The nightly's two warm-latency reds added to `accepted_reds`, named, until W2-155 closes; linger enabled; a fresh CTO session after the VS Code reload
- **Status:** ACCEPTED (owner, 2026-11-11, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-11)`); item (1) until W2-155 (`DAEO-ar89`) closes · **Under:** DEC-1125 (1), DEC-1132 (4), DEC-757, DEC-762, DEC-1052 (Q-10), DEC-1118 · **Source:** the owner's message (chat, 2026-11-11 ~16:00 UTC) · **Class:** kept (items changed: the two accepted_reds entries kept until W2-155 closes (A-4); rest history)
- **Decision:**
  - (1) **`accepted_reds` gains two entries, named, until W2-155 closes:** `tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95` and `tests/acceptance/W2-13/test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget` (the warm real-model query
    latency, p95 0.54-0.59 s against the 0.5 s budget, the named red of DEC-1125 (1)); each entry's decision DEC-1134,
    its reason that red, its `fixed_by` W2-155. Prepared by the CTO as the owner's commit (the path map's ratchet takes
    an owner's commit only), applied by the owner's operator.
  - (2) The owner ran `loginctl enable-linger usain` (ACT-NIGHTLY-RESTART-1's prerequisite).
  - (3) **Rule 11 (DEC-1118):** the CTO's context is past 200k; the CTO writes the handover (report-state.json to today,
    CHECKPOINT's RESUME HERE), and the owner starts a fresh CTO session after the VS Code reload.
- **Basis:** question 2 (a known, named red does not stop every night's report; it leaves the list when its fix lands).

### DEC-1146 — A resource gate's refusal is a wait, not a refusal under the two-refusal rule (standing)
- **Status:** ACCEPTED (owner, 2026-11-12, in the chat ~14:45, P1-I (a); recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-12)`; standing) · **Under:** DEC-1142 (9), DEC-1088 (5) · **Class:** kept (items changed: permission-refusal clause superseded §2.2)
- **Decision:**
  - (1) **A resource gate's refusal** (memory, CPU, disk, a heavy slot) is a wait, not a refusal under the two-refusal rule: the session
    relaunches when the gate opens, without asking the owner. The two-refusal rule (DEC-1142 (9)) covers permission refusals: the guard,
    the sandbox, a hook.
  - (2) The P1-D check (DEC-1144 (4)) is relaunched once the CTO's merge checks free the gate.
  - (3) Into the common lead brief beside the two-refusal rule.
- **Basis:** P1-I; the P1-D reviewer and W2-152's re-probe each stopped after two memory-gate refusals (2026-11-12 14:05-14:28).

### DEC-1149 — The working size 0.75 GiB per session (ACT-P95-1), the new figure everywhere; usage never stops a lead or a worker; the two peaks re-measured within the week (standing)
- **Status:** ACCEPTED (owner, 2026-11-12, in the chat ~16:40; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-12)`); (3) standing · **Under:** DEC-947, DEC-1088 (5), DEC-1133 (5), DEC-1138 (2), (4), DEC-1140 (6), DEC-1115 (4), DEC-1091, DEC-1089 (3), DEC-1146 · **Class:** kept (items changed: (1),(2) history (the 0.75 GiB figure; RT-3 removes constants); (3) kept: usage never stops a lead or a worker, the runaway brake stays)
- **Context:** the machine gate (`gov launch`, `src/gov/resources/gate.py`) opens when available memory plus the live sessions' memory is at least the 3 GiB floor plus `working_size_bytes` for each live registered session and the newcomer. Every session, lead or worker, was counted at DEC-947 item 2's 2,191,601,664 B (2,140,236 kB, 2026-10-29), while each uses 0.25-0.40 GB (the CTO's lead-memory ledger since 2026-11-11 18:00: a lead's process tree p50 0.29 GB, p95 0.41 GB, p99 0.65 GB, max 1.87 GB; available never below 12.75 GB). The gate refused workers on that accounting with 15-16 GB available (W2-124, W2-157, W2-45, the CTO's reviewer); the sample day and ACT-P95-1 (DEC-1138 (4)) had not run.
- **Decision:**
  - (1) **`working_size_bytes` = 805,306,368 B (0.75 GiB) per live session,** from the ledger, by ACT-P95-1 (class (b): one quick review, the owner's yes, the CTO applies it at once). The floor (3 GiB), the hold below 5 GB available (DEC-1138 (2)), `mem_guard` and the OOM trip (2 GiB) stay and handle any peak. DEC-947 item 2 and DEC-1138 (4)'s working-size half are changed by this item.
  - (2) **The new figure everywhere:** every decision, ACT and file that states or relies on the old working size is amended by its own route: the register by this record and its marks; the gate's file by ACT-P95-1; the CTO's prompt, the decisions-in-force list and the packages by recorded edits; the product's default for a new machine (`src/gov/resources/config.py:220`) changes to the same 805,306,368 B by widening W2-157 (open, `config.py` already in its paths; the owner, ~16:50: no new ticket).
  - (3) **Usage never stops leads:** usage is tracked and reported in every report and digest; no lead or worker is held, refused or stopped because of usage or spend. DEC-1140 (6)'s 97 % line and DEC-1115 (4)'s priority rule are changed by this item: the 99 % push to the owner stays, as a report only. **The runaway brake (DEC-1091) stays a stop** (the owner, ~16:50): it guards against a ticket looping, not against usage. The usage stop is removed from the CTO's tools (`usage_lines.sh`'s 97 line is a report; the usage-97 brake files cleared).
  - (4) **The ledger keeps running;** the two peak figures (`verification_peak_bytes`, `rebuild_peak_bytes`) are re-measured from it and brought to the owner within the week (by 2026-11-19). Once ACT-P95-1 is in, the CTO reports how many leads the gate admits at the day's readings and what binds first after it (the cap of five, the CPU, the heavy slots, or ready work).
  - (5) **Applied:** the owner's `yes ACT-P95-1 4169b2f9` (16:53); the CTO applied it at once (verified: working_size_bytes 805306368; the gate open at 15.36 GB available with 6 sessions). The review's rows: R1 the 5 GB hold (`mem_hold`) now does the gate's old job, so it becomes part of the launch check or gets a liveness check; R3 a re-measure at the new density (row 177).
- **Basis:** the owner's messages of 2026-11-12 ~16:40, ~16:50 and 16:53.

### DEC-1157 — Every rule that holds or delays a lead removed tonight, except what protects the machine and the governance; W2-113 PKG-3 (b); W2-155 started; W2-60a built; two logs added (standing)
- **Status:** ACCEPTED (owner, 2026-11-12, in the chat ~23:40; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-12)`); standing · **Under:** DEC-1156 (9), DEC-866, DEC-1146, DEC-1149 · **Supersedes:** DEC-1138 (the lead cap of five and (3) the night hold), DEC-1156 (8) · **Changes:** DEC-1140 (2), (5), DEC-1021, DEC-1018 (1), DEC-1052, DEC-1032, DEC-1038 (4), DEC-1039 (1b), DEC-1088 (5)(a), DEC-979, DEC-974 · **Changed by:** DEC-1164 (4) (item (2)'s interim operator sleep, spent once ACT-OPERATOR-HOURS-3 is applied), DEC-1164 (23) (item (1): a decision that stops or delays a lead goes at once, at any hour, unless the owner has said they are asleep, DEC-1156 (8); then it waits for the morning package) · **Class:** kept (items changed: (14) guard refusals, review rounds, kernel gate superseded §2.2/§3.4/§3.5; (15),(16) history)
- **Context:** the CTO's inventory of 2026-11-12 23:00 (`.gov-runtime/scratch/orchestrator/drafts/lead-delay-inventory-measure.md`): 45.2 lead-hours lost 00:00-22:50 against 70.8 used; the largest the night push rule (9.8), the owner's and CTO's decisions (5.8), the night hold (5.5), the interface check (4.9), one land per batch and its ejections (4.5), the resource gate (4.0), lines not prepared (4.0), commit freezes (2.7).
- **Decision:**
  - (1) **The night push rule is removed:** every decision that stops or delays a lead comes to the owner at once, at any hour, as a full package (DEC-1156 (8)'s "until the owner says they are asleep" and DEC-1021's quiet hours, for such decisions, are superseded).
  - (2) **The night hold is removed:** no lead start and no landing is held for the nightly; the nightly runs in its own capped unit (DEC-1138 (3) and DEC-1018 (1)'s landing hold superseded). Applied: `tools/night_hold.py` stopped; `config.json`'s `nightly_hold_from` and `nightly_hold_until` an empty window. The operator agent's cron line (DEC-1141 (6)) still reads the night-hold state file after 03:10: its change is a crontab ACT (class (b)) to the owner; until then the operator does not launch from 02:10 to 08:00.
  - (3) **The interface check is no longer a lead stop:** the CTO states each ticket's interface (from the ticket and the code) at claim, before its lead takes a slot; a lead returns an interface package only for a gap the CTO's statement leaves (DEC-1052's check moved to the claim).
  - (4) **Lands in batches of two or three tickets with disjoint paths** (the CTO's one-land-per-batch practice removed).
  - (5) **The CPU band is removed:** real memory protects the machine (DEC-1032's band, DEC-1038 (4)'s T1 band and DEC-1039 (1b)'s CPU term in the forecast changed). Applied: `config.json` `cpu_band` [0, 1000].
  - (6) **Two lines ready at all times:** claim, worktree and brief prepared ahead, so no slot waits for preparation.
  - (7) **No commit freeze during lands:** no ready lead waits for a land gap; the CTO commits and accepts the queue's re-test.
  - (8) **The lead cap is removed** (DEC-1138's five, ACT-DISPATCH-1's `max_leads`); memory admits each start; a ticket on EXAMIN's critical path never waits. Applied: `max_leads` removed from `config.json`.
  - (9) **A dependency merged into w2/integrate counts as met for starting;** closing still waits for it to be closed (DEC-1088 (5)(a) changed). Applied tonight by `plan_override: DEC-1157` on each ticket so started (gov launch's plan check admits it and logs the override); the product's plan check reading "merged" itself is product code: a package to the owner.
  - (10) **A land holds at most two of the three heavy slots** (DEC-979 changed).
  - (11) The usage stop stays removed (DEC-1149 (3)).
  - (12) **Widenings and KPI edits within a ticket's own purpose** are the CTO's, listed for the owner's reading (DEC-974 and the prompt's §3 changed for these); new tickets and splits still come to the owner.
  - (13) **Two logs:** every start the dispatcher refuses (time, ticket, reason) and every heavy-slot wait (time, caller, seconds), so what remains is measurable.
  - (14) **Kept (they protect the machine and the governance):** the memory floor, the 5 GB hold, `mem_guard` and the OOM trip; the guard's refusals; the spend brake; the brief checks; review rounds, the kernel gate and the owner's approval of kernel bytes; new tickets and splits to the owner; the idle check's record.
  - (15) **W2-113 PKG-3 (b):** with `tk` missing A0 completes without creating the ticket or the key, and its record says so; the guard stays closed. **W2-155** started now (its waits merged). **W2-60a:** a build run tonight, its merge held until W2-33 lands. **W2-154's S4** brought in full now.
  - (16) **The sweep:** every standing decision in DECISIONS-IN-FORCE that stops, holds or delays work (the emergency's above all), each with whether it still serves and the CTO's recommendation, and why it was not superseded already, in the 09:00 digest.
- **Basis:** the owner's message of 2026-11-12 ~23:40.

### DEC-1158 — The emergency of 2026-11-02 lifted, with its freeze; its spent items marked (standing)
- **Status:** ACCEPTED (owner, 2026-11-13, in the chat ~00:30; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`); standing · **Under:** DEC-1157 (16), DEC-1126, DEC-1132 (4), DEC-866 · **Supersedes:** DEC-1032 (2), (3)(v), DEC-1033 (1), (4), DEC-1047 (1), (2), DEC-1051, DEC-1049, DEC-1050 (5) · **Changes (spent):** DEC-1037 (3), DEC-1039 (3), (3b), (4) · **Class:** kept (items changed: (1),(2),(4) history; (3) kept)
- **Context:** the CTO's sweep of DECISIONS-IN-FORCE (DEC-1157 (16), `.gov-runtime/scratch/orchestrator/drafts/dif-sweep-20261113.md`): the emergency's decisions each stand "until the owner lifts it", and no entry lifted them; "Emergency plan: none" was a status fact only; a fresh session reading them would stop leads, lands and closes.
- **Decision:**
  - (1) **The emergency of 2026-11-02 and its freeze are lifted.** Superseded: DEC-1032 (2), (3)(v) (the freeze; every sprint step done); DEC-1033 (1), (4) ("everything that is not one of the fixes stops"; the four fixes live and re-pinned, windows 2-5), its (2) kept as DEC-1065's line; DEC-1047 (1), (2) (every ticket stopped but the memory infrastructure), its (3) kept; DEC-1051 (everything stopped until the refactoring and the re-pins: met at re-pin window 5, DEC-1126 (1)); DEC-1049 (no nightly until the owner's word: the nightly came back under DEC-1132 (4)); DEC-1050 (5) (nothing scheduled until the refactoring), its T-1, Q-1, G-1, G-2 and O-7 kept.
  - (2) **Spent:** DEC-1037 (3) (the full run repeated until green: D-10's ruled red counted, DEC-1126 (7)); DEC-1039 (3), (3b), (4) (green, then the owner lifts the emergency: this entry is that lift).
  - (3) **Kept, named:** DEC-1039 (1b)'s GPU budget and no-spill rule (they protect the machine); its "two or three leads" is obsolete (DEC-1157 (8)).
  - (4) **Follow-ons:** DECISIONS-IN-FORCE refreshed to this entry; START-NEXT-SESSION rewritten (no "emergency mode"; the live pin `pin-797495bdfc70`); the prompt's §0 emergency bullet: an edit for the owner's operator.
- **Basis:** the owner's message of 2026-11-13 ~00:30 ("The emergency's lift: yes, DEC-1158 as you wrote it, with its follow-ons").

### DEC-1170 — The gitleaks scan stays off on this repository: a private, local development repository, nothing public
- **Status:** ACCEPTED (owner, 2026-11-13, in the chat ~16:00; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`); standing · **Under:** DEC-1045, DEC-1158 · **Class:** kept
- **Decision:** the gitleaks scan stays off by configuration on this repository (`governance/project/secrets.yaml`, DEC-1045), as a standing decision, not an emergency measure: **this is a private, local development repository; nothing in it is public.** It is not raised again as an open item (the lands, the record sync and the landing check keep printing "off by configuration", which is the record of it). The scan stays built and tested in the product, where an adopted repository chooses for itself; secrets are still never printed or written (DEC-820 (a)), and a key found in ordinary work is still an emergency (the rubric).
- **Basis:** the owner's message of 2026-11-13 (~16:00): "The gitleaks scan stays off: this is a private, local development repository, nothing public. Record it as my decision and its reason, so it is not raised again."

### DEC-1176 — Memory for any repository is built, measured and maintained per repository in its own Wave 0, not proven by measuring other repositories; W2-88b becomes a smoke run of gov adopt on grafana and redis (no questions, no measure, no validation)
- **Status:** ACCEPTED (owner, 2026-11-14 ~00:30, in the chat: "yes DEC-1176, A5 (a)"; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`; item (1) standing) · **Under:** DEC-954 Q9f, DEC-1150 (1), DEC-1099 (2), DEC-1098 (1), DEC-1072 (2), DEC-957 (memory's target 95 %), DEC-974, DEC-728 · **Changes:** DEC-954 Q9f (its proof list), DEC-1150 (1) (W2-88b's content and its copies line), DEC-1099 (2) (as it adopted W2-88-STANDARD-1 §3: the 10 questions per real repository) · **Changed by:** DEC-1179 (7), spends (1)'s "until then" · **Class:** kept (items changed: (2)-(4) history)
- **Decision:**
  - (1) **Standing: memory is proven per repository.** Each adopted repository's memory is built in that repository's own Wave 0 (refactoring, indexing, embeddings, stores), measured there on its own hidden questions to at least 95 %, and kept there by weekly maintenance and re-measuring. Memory for any repository (DEC-954 Q9f) is not proven by measuring other repositories. How the weekly re-measure works (the same hidden questions, against today's fresh set measured once) is decided separately, on `MEMORY-AUDIT.md`. Until then DEC-1101 (1), DEC-1125 (2), DEC-1098 (1) and the adopt skill's step 6 stand as written.
  - (2) **W2-88b (DAEO-aks1) re-scoped to a smoke run.** gov adopt runs on copies of grafana/grafana (large) and redis/redis (smaller) under `~/gov-os-runs/W2-88b/`, with the memory tools it runs: the assessment (MA), the index, the embeddings and the stores (A9 lite, run with no `--questions`). Its only purpose is to test whether gov adopt works on repositories different from this one, small and large, and where it fails.
    - **The record:** `experiments/W2-88/smoke-run.md`. Per repository and per stage (MA, A0 to A6, A8, A9) it names whether the stage completed, or where and how it failed: the command, its exit code, the refusal code, the error and the time.
    - **A failure is a finding:** it is recorded and returned to the owner. It never stops the other repository and is never fixed in W2-88b.
    - **Out:** no questions, no measure, no validation of the result's quality. No workbench clones (ORION, ARGUS, ARGUS's stress tier, EXAMIN's copy). No question sets for grafana, redis or `~/workspace`, and `~/workspace` is not read at all.
    - **The ticket edit:** the five old success lines and the two old failure lines are removed. They are listed word for word in the ticket's body as "Removed by DEC-1176 (2)". In their place go five success lines (S1 to S5) and three failure lines, each with its `Verify:` clause (`W2-88b.patch`).
  - (3) **A5 on a copy: the owner chose (a).** gov adopt's chain stops at A5 without an independent auditor's committed verdict on the path map (`src/gov/adopt/stages.py:432-461`: `NO_VERDICT`; the verdict's commit must carry `Role: independent-auditor` alone, from a session that ran no stage). Without it, A6, A8 and A9 (the memory build) are never reached.
    - **(a) Recommended:** a fresh independent-auditor session gives A5's verdict on each copy. It is the product's own gate and judges the path map only, never memory. Cost: two short auditor sessions (about $3 each, MEMORY-AUDIT-1 §7's auditor figure) and about 30 minutes. This is the patch's S4.
    - **(b)** No verdict. A5 is recorded as the failure `NO_VERDICT`, and the memory build runs outside gov adopt, by `gov rebuild` on each copy. Cost: A6 to A9 untested through gov adopt; S4 is removed and S2's chain ends at A5.
    - **(c)** A verdict written by the lead, labelled "smoke run, not a review". Not offered: it would forge the auditor trailer the gate checks.
  - (4) **What does not change:**
    - W2-88 (closed) keeps its record. Its proof (a) on W2-81's five synthetic repositories stands. Its "Memory works there" line's clause on real repositories is spent with W2-88b's lines.
    - DEC-1099 (2)(c) stands: EXAMIN's copy at W2-27 is the practice's first full run, measured on its own sets.
    - DEC-957's MEMORY-SPEC-MAP gap "the large-repository measure" stays closed by W2-88's Scale line on proof (a). The smoke run's stage times on grafana are data beside it, not a measure.
- **Changes, sentence by sentence:**

  | Decision | Old (quoted) | New |
  |---|---|---|
  | DEC-954 Q9f | "…and set up the database structure; proven on W2-81's synthetic repositories, two real messy public GitHub repositories of different languages and sizes, and any test repository path named earlier in the register; EXAMIN's copy is its live trial." | "…and set up the database structure; the tools proven on W2-81's synthetic repositories (W2-88's proof (a)) and smoke-run on copies of two real public repositories of different sizes, grafana and redis (W2-88b: whether gov adopt completes, and where and how it fails; no questions, no measure, no validation); each repository's memory built, measured on its own hidden questions to at least 95 % and maintained in its own Wave 0, never proven by measuring other repositories (DEC-1176); EXAMIN's copy is its live trial and the practice's first full run (DEC-1099 (2))." |
  | DEC-1150 (1) | "W2-88b (DAEO-aks1, research: proofs (b) and (c), their scale and measure lines, the proof record in `experiments/W2-88/`, the clone failure line)" | "W2-88b (DAEO-aks1, research: the smoke run of gov adopt on copies of grafana and redis, its record `experiments/W2-88/smoke-run.md`, the clone failure line; proof (c), the scale line and the measure line removed by DEC-1176 (2))" |
  | DEC-1150 (1) | "**Proof (c) works on copies only:** nothing is written in ~/workspace or in any of the owner's own repositories (a failure line of W2-88b)." | "**The smoke run works on copies only,** under `~/gov-os-runs/W2-88b/`. `~/workspace`, the workbench and the owner's own repositories are neither cloned, read nor written (a failure line of W2-88b; DEC-1176 (2))." |
  | DEC-1099 (2), as it adopted W2-88-STANDARD-1 §3 (the re-worded "Memory works there" line, carried into W2-88b) | "W2-81's per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric apply to each real repository; these figures are data, set no bar…" | "W2-81's per-repository sets apply to the synthetic repositories; no question set is written for a real repository outside its own Wave 0 (DEC-1176 (1)); these figures are data, set no bar…" |
  | DEC-1099 (2), as it adopted W2-88-STANDARD-1 §3, row "The proofs … (a) to (d)" | "(b) amended: one of the two GitHub repositories, or `~/workspace`, runs the full practice" (already overtaken by answer (2)(c)) | removed: no proof repository other than an adopted repository's own Wave 0 runs any part of the practice's measure |

- **Basis:** the owner's messages of 2026-11-13 (chat):
  - "W2-88b: I change its scope. Memory is built per repository in its own Wave 0 (refactoring, indexing, embeddings, stores), measured on its own hidden questions to at least 95 %, and kept there by weekly maintenance and re-measuring. It is not proven for 'any repository' by measuring other repositories. So: no workbench clones (P3) and no question sets for grafana, redis or ~/workspace (P4). Keep only a smoke run of the tools on grafana and redis: they index, embed and build their stores without failing, with no questions and no measure. ... bring the ticket edit (W2-88b's KPI lines, and DEC-954 Q9f's 'any repository' evidence) as one decision for my yes."
  - The follow-up on the smoke run: "its only purpose is to test whether gov adopt works on repositories different from ours, small and large, and where it fails. No measuring and no validation."
- **Basis (the choice):** the owner's message of 2026-11-14 (~00:30): "yes DEC-1176, A5 (a)."

### DEC-1182 — Secret scanning and pushes: no repository scan on Gov OS; EXAMIN one full gitleaks scan a week before its weekly push, in the memory audit's weekly cycle, never at a close or a refresh; the guard's per-command secret rule stays on; q02's variant version 2
- **Status:** ACCEPTED (owner, 2026-11-14 ~16:00 and ~16:03, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-14)`; (1) to (4) standing) · **Under:** DEC-1045, DEC-1179, DEC-1180, DEC-1181, DEC-1101 (2) · **Changes:** DEC-1045 (1) (its "a full scan runs once a week only when the owner approves it": no repository scan on Gov OS at all); DEC-1180 (2) (q02's variant: version 2, 7aa6d88c, in place of 0703aebf) · **Changed by DEC-1184 (1), (2):** (3)'s and (4)'s open questions answered: Q-SCAN-1 (a), the guard's secret-path rule every day plus the weekly scan, no pre-commit scan; Q-REFRESH-1 (a), the seeded rebuild is the changes-only refresh · **Class:** kept (items changed: (1) kept §2.11; (2) superseded §2.11; (3) superseded §2.2; (4) kept)
- **Decision:**
  - (1) **Gov OS stays private: no repository scan**, at closes or anywhere else, weekly included. Its `secrets.yaml` stays `scan: off` (DEC-1045).
  - (2) **EXAMIN: one full gitleaks scan a week, before its weekly push to GitHub, in the memory audit's weekly cycle:** audit and measure, then the scan, then the push, only on a clean scan. No scan at a ticket's close or at a store refresh: EXAMIN's `secrets.yaml` holds `scan: off` (the one switch that governs the refresh, strict-close and nightly scans, `config/loader.py:427-431`), and the weekly cycle runs gitleaks itself. W2-187 takes the scan and push steps (S12, F7, the CTO within the owner's decision); A9's ACT package's cron line runs that cycle; the push step runs only once the repository declares its remote (EXAMIN's remote is removed at the operator's setup and comes back when it is hosted). The EXAMIN CTO's brief: `secrets.yaml` with `scan: off`, the weekly scan on (the owner's "its scan: on" read as the weekly scan), and no push by the EXAMIN CTO itself.
  - (3) **The guard's per-command secret check stays on everywhere, and the owner accepts the remaining risk** of a key reaching the files or the store between weekly scans. As built, the per-command check is the guard's secret-path rule (`src/gov/guard/reads.py`): reads and writes of secret, key and credential paths are refused by name on every call. It does not run gitleaks on a command. A gitleaks run per command cannot fit 100 ms (a staged scan of a planted repository takes 0.34-0.38 s). The owner's two questions on this (Q-SCAN-1, Q-SCAN-2) went to the owner on 2026-11-14 ~16:15.
  - (4) **The store refresh** is a seeded rebuild (`gov rebuild --seed`, W2-122, `src/gov/rebuild/seed.py`): only files whose content differs from the base are re-embedded and re-checked, while the lexical, graph and other stores are re-derived from the files on every refresh (51-130 s on 11-14). A cold, whole rebuild runs only when the code that builds the stores changes (every re-pin) or no usable base exists. EXAMIN works the same way. This is not yet the owner's "changes only, never rebuilt whole after a merge" for the derived stores; Q-REFRESH-1 went to the owner on 2026-11-14 ~16:15.
  - (5) **`yes q02 variant v2 7aa6d88c` (P-Q02-V2 (b)):** q02's fix runs the self-contained version 2 of the writer variant (sha256 `7aa6d88c3a7769c1abe34ffd54b8ced4f4110fb2208ed1f316d1a7c000b021b6`, independent review PASS, 0 blocking, F1-F8 rows) in place of 0703aebf. The CTO made the launch clone's scaffold 3 (`6325d7ff17a3`); the operator's four commands at W2-94's land carry v2's sha and that commit.
- **Basis:** the owner's messages of 2026-11-14: "Secret scanning and pushes, my decisions: - Gov OS stays private: no repository scan, at closes or anywhere else. - EXAMIN will be hosted in the cloud later, so it gets one full gitleaks scan a week, before its weekly push to GitHub, in the same weekly cycle as the memory audit: audit and measure, then the scan, then the push, only on a clean scan. No scan at a ticket's close or at a store refresh. - The memory store is refreshed on the changes only, never rebuilt whole after a merge; confirm that is how the refresh works, for EXAMIN and here. - The guard's per-command gitleaks check stays on everywhere. I accept the remaining risk of a key slipping into the files or the store between weekly scans: this balances practicality against risk. Confirm the check stays within W2-111's 100 ms bound. Apply these to the EXAMIN CTO's brief (its scan: on), to W2-187's weekly cycle and to EXAMIN's A9 ACT package; record them as a decision, and tell me what changes." (~16:00); "yes q02 variant v2 7aa6d88c" (~16:03)
- **Governing sources:** DEC-1045 (1); DEC-1179 (5), (6); DEC-1180 (2); DEC-1181 (3); DEC-1101 (2); W2-111 (DAEO-qvff, the 100 ms bound); W2-122 (`gov rebuild --seed`); W2-187 (DAEO-0cd2) S10, S11, I11; `src/gov/config/loader.py:427-431`; `src/gov/rebuild/seed.py`; `src/gov/guard/reads.py`; the CTO's investigation of 2026-11-14 ~16:10.

### DEC-1183 — W2-88's Route X for release 0.1.0 tonight (S27 dropped from this run, packages 1 and 2 (a)); S27's folder mode as its own round after the land; ACT-CLAUDE-COPIES-12 approved; the CTO's compaction trial ended: back to the full window; every new lesson to memory at once
- **Status:** ACCEPTED (owner, 2026-11-14 ~18:15, ~21:2x, ~21:50 and ~22:10, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-14)`; (4) and (5) standing) · **Under:** DEC-1178 (3), DEC-1180 (4), DEC-1171 (6), DEC-838, DEC-1156 (7), DEC-1010 · **Changes:** DEC-1171 (6) (the 3-day trial ends after one day: the CTO's session runs on the full window again from the next session) · **Changed by DEC-1185:** (1)'s package 2 reads the code graph in bounded pieces grouped by source file (keyset paging proved unsound in the tool, so one piece per source path), not in pages by edge type · **Class:** kept (items changed: (4) full window and (5) every new lesson to memory at once kept; (1)-(3) history)
- **Decision:**
  - (1) **`P-W2-88-S27-1 (b), package 1 (a), package 2 (a)` (Route X):** W2-88's run 8 reverts S27 to the one-file-at-a-time secret scan (sound; no path may mark a secret-holding file clean, P1R-1). S27's speed and batch-equivalence cases are skipped with the reason `DEC-1183: S27 runs as its own round after this land (P-W2-88-S27-1 (b))` (the CTO's routing, DEC-1156 (7)). Package 1 (a): the retrieval pool, the walls template and the MEMORY-AUDIT-1 briefs ship as copies under `src/gov/_shipped/`, declared as package data in `pyproject.toml`, with a test that each copy equals its source bytes. Package 2 (a): the code graph is read in pages by edge type, each under the tool's 100,000-row limit; a graph the tool still cannot read refuses by name, never a silent partial count. W2-88's `allowed_paths` widen to `pyproject.toml`, `src/gov/_shipped/**`, `src/gov/codeintel/__init__.py`, `src/gov/retrieval/code_route.py`, `tests/unit/adopt/test_safety.py` and `tests/unit/codeintel/test_w2_88*`.
  - (2) **S27's folder mode runs as its own round straight after W2-88 lands** (each batch's files written to a private temporary folder outside the repository, one `gitleaks dir` per batch, each finding naming its own file). W2-88 stays open for that round.
  - (3) **`yes ACT-CLAUDE-COPIES-12 22865f2a`** (given ~18:15, repeated ~21:2x): the operator applies the bundle after the CTO's hand merge of `w2/W2-188`.
  - (4) **The compaction trial ends: `trial: full window`.** The CTO's next session starts without `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (DEC-838 holds again for every session). The day's figures: the CTO's cost per call fell from $0.138 to $0.064 and the cache-read share from 72 % to 53 %, saving about $60 a day (about 7 % of a day's spend); the counts rose (11-14: stale 7, missed 9, corrections 0, against 11-13's missed 5 and stale about 2), with lessons lost across compactions.
  - (5) **Every new lesson goes to memory the moment it is learned** (a refusal, a wrong assumption, a brief defect), before the next action. Standing.
- **Basis:** the owner's messages of 2026-11-14: "yes ACT-CLAUDE-COPIES-12 22865f2a" (~18:15, again ~21:2x); "Now: Route X: P-W2-88-S27-1 (b), package 1 (a), package 2 (a). Resume W2-88 at once; S27's folder mode runs as its own round straight after W2-88 lands." (~21:50); "trial: full window. Keep the rule you proposed anyway: every new lesson goes to memory the moment it is learned. The next session starts without the 300k setting." (~22:10).
- **Governing sources:** DEC-1178 (3); DEC-1180 (4); DEC-1171 (6); DEC-838; DEC-1156 (7); DEC-1010; DEC-1154; W2-88 (DAEO-2bdu) escalation 2491c9bec and run 8's return (P-W2-88-L8-1 (a) by the CTO); W2-188 (DAEO-zlog) 790357f0215d; the CTO's trial figures of 2026-11-14 ~22:00.

### DEC-1184 — The refresh accepted as changes-only (Q-REFRESH-1 (a)); EXAMIN's secret protection is the guard's path rule every day plus the weekly scan, no pre-commit scan (Q-SCAN-1 (a)); W2-111 reopened for the guard's 100 ms on Bash calls and many trees (Q-SCAN-2 (a)); the EXAMIN CTO's first brief b70ff233 approved; W2-61h and W2-94 close on the operator's results
- **Status:** ACCEPTED (owner, 2026-11-14 ~22:50, in the chat, the new CTO session's first prompt; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-14)`; (1) and (2) standing) · **Under:** DEC-1182, DEC-1178 (1), (3), DEC-1179 (6), DEC-1180, DEC-1101 (2), DEC-979, DEC-906, DEC-1157 (12) · **Changes:** DEC-1182 (3) and (4) (their open questions Q-SCAN-1 and Q-REFRESH-1 answered); W2-111's "Not here: the hook itself" (the reopen takes the hook's two costs, (3)) · **Class:** kept (items changed: (1) kept; (2) superseded §2.11/§2.2; (3)-(6) history)
- **Decision:**
  - (1) **`Q-REFRESH-1 (a)`: the seeded rebuild is the refresh "on the changes only"**, here and for EXAMIN: only files whose content changed are re-embedded and re-checked; the derived stores (lexical, graph and the rest) are re-made from the files in about 1-2 minutes; a cold, whole build runs only at a re-pin (the code that builds the stores changed) or when no usable base exists. No ticket for true per-entry updates of every store. Standing.
  - (2) **`Q-SCAN-1 (a)`: EXAMIN's secret protection** is the guard's secret-path rule on every call, every day (`src/gov/guard/reads.py`: reads and writes of secret, key and credential paths refused by name), plus one full gitleaks scan a week in the memory audit's weekly cycle, before EXAMIN's weekly push (DEC-1182 (2)). **No pre-commit scan** (the staged scan built at `ci/command.py:99-125` stays installed nowhere), and no scan at a ticket's close or at a store refresh. Standing.
  - (3) **`Q-SCAN-2 (a)`: W2-111 (DAEO-qvff) is reopened now, within the 100 ms bound's purpose.** The measure of 2026-11-14 (W2-111's method; evidence copied to `~/gov-os-runs/W2-111/q-scan-2/`): all 15 W2-111 cases pass (87-97 ms best round, load 13-20), but a Bash call takes 103-167 ms and every call grows with the worktree count (about 59 ms to list 248 trees, 47 ms per tree judged, 52 ms for the Bash install check). The reopen adds: Bash cases and a case with 150 or more trees, so the gap shows in the tests (the independent test designer); the install check's PATH lookup once per session, not per call; a call judged only against the trees its target lies in (an engineer, in the guard's code: W2-111's allowed paths widen to the guard files that hold the two costs; the kernel gate and the owner's approval of kernel bytes apply at its land). The live hook takes the change through the planned live-hook ACT (it copies W2-42a's parser), with the owner's yes on that ACT. The bound stays 100 ms at p95; no case is removed or skipped. The CTO also removes closed tickets' worktrees after each close (Q-SCAN-2 (b), at no cost).
  - (4) **`yes EXAMIN-CTO-first-brief b70ff233`:** the EXAMIN CTO's first brief is approved at sha256 `b70ff2332e89a9498e1b42f72e8a6a1b55eed62b003f604a770d71d6c4a1a60b` (`.gov-runtime/scratch/orchestrator/drafts/examin-release/EXAMIN-CTO-first-brief.md`), in place of 995d0dcf (DEC-1178): the date and DEC-1178 (3) filled, and DEC-1182 (2)'s scan line (`secrets.yaml` `scan: off`, the weekly scan on, no push by the EXAMIN CTO). A fixed brief: the CTO never changes it without the owner (DEC-1101 (2)).
  - (5) **W2-61h (DAEO-h2k3) closes on the owner's operator's walled run at `5f9a9dedf`:** 7 passed, one `GoldBlockChanged` warning listing h03 entries 1 and 2, h20 entry 2, h24 entry 1, h35 entry 1 and h36 entry 1. That list (question ids and entry numbers only) goes to the walled writer's weekly cycle (DEC-1178 (1), DEC-1179 (6)): `packages/REANCHOR-LIST-20261116.md`, for the Monday slot of 2026-11-16, run by the owner's operator until the reanchor ACT (DND 203) carries it.
  - (6) **q02 is done and W2-94 (DAEO-g87r) closes:** step 2's approved line, as the CTO's command gave it, lacked the kind `writer` (**the cause was the CTO's command**); the owner's operator corrected it to `brief writer <path>`, set the mode back to 400 and relaunched: run `20261114T222836Z-examin-r2` delivered, fix q02 `corrected`, and `check_gold` gives 20 of 20 hold. The brief's commit `aa1fa659f` is on `w2/integrate`, not yet pushed.
- **Basis:** the owner's message of 2026-11-14 ~22:50: "My decisions, to record and apply now: - Q-REFRESH-1 (a). - Q-SCAN-1 (a): the guard's secret-path rule every day, plus one full gitleaks scan a week in the memory-audit cycle, before EXAMIN's weekly push; no pre-commit scan, and none at closes or refreshes. - Q-SCAN-2 (a): reopen W2-111 now. - yes EXAMIN-CTO-first-brief b70ff233. My operator's results: - W2-61h's walled run at 5f9a9dedf: 7 passed, one GoldBlockChanged warning listing h03 entries 1 and 2, h20 entry 2, h24 entry 1, h35 entry 1 and h36 entry 1. Close W2-61h, and send that list to the walled writer's weekly cycle. - q02: done. Step 2's approved line lacked the kind \"writer\" (record that your command was the cause); my operator corrected it to \"brief writer <path>\", mode back to 400, and relaunched: run 20261114T222836Z-examin-r2 delivered, fix q02 \"corrected\", and check_gold gives 20 of 20 hold. The brief's commit aa1fa659f is local. Close W2-94."
- **Governing sources:** DEC-1182 (2)-(5); DEC-1178 (1), (3); DEC-1179 (6); DEC-1180 (2), (4); DEC-1101 (2); DEC-979; DEC-906; DEC-1157 (12); W2-111 (DAEO-qvff); W2-61h (DAEO-h2k3); W2-94 (DAEO-g87r); the CTO's Q-SCAN-2 measure of 2026-11-14 ~16:30 (`~/gov-os-runs/W2-111/q-scan-2/`); the packages Q-REFRESH-1, Q-SCAN-1 (2026-11-14 ~16:10) and Q-SCAN-2 (~16:35).

### DEC-1199 — EXAMIN's CTO leads EXAMIN's Wave 0 (the Gov OS CTO on Gov OS only); F-022 (b), go LITE, F-023 (a) with a product ticket; the freeze lifted; the operator as the owner's free second hand (FREE-HAND D1-D7) on (A-full) separation; an interim job queue; residuals R1 (a), R2 (b), R3 (a), R5 (b); P-GUARD-FP-1 (a), (b)
- **Status:** ACCEPTED (owner, 2026-11-16 13:0x to 14:3x, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`) · **Under:** DEC-1195, DEC-1196, DEC-1197, DEC-1191 (2), DEC-1174, DEC-974 · **Changes:** DEC-1198 (3) (the box: (A-full) instead of (B)) · **Changed by DEC-1203:** (3) the box: (B) live now as an exception until Wave 3, not (A-full) · **Class:** kept (items changed: (1) roles kept, refactor tickets read as direct work §7.2; (3),(4),(5) superseded §2.6/§2.2; (2) history)
- **Decision:**
  - (1) **The roles:** the EXAMIN CTO leads EXAMIN's Wave 0 (the audit, the specs, the refactor), governed by Gov OS; the Gov OS CTO works on Gov OS only (sees what is broken or missing, asks the EXAMIN CTO to act, or fixes Gov OS); the CTOs talk to each other and to the operator, where all CTOs' actions run; the owner talks to each CTO directly in the app; the same for every later repository. EXAMIN's Wave 0 is planned and led by the EXAMIN CTO in five steps: the target layout; a full audit (alive, working, disposition with destination, building on MA and A3); a spec audit (every gap asked of the owner); an independent check of the dispositions, approved by the owner by group; then the refactor tickets (characterization tests first, slices, the memory build, a fresh question set, 95 % or better on the hidden half), W2-28's verdict after the refactor. P-EXAMIN-WAVE0-1 is withdrawn; the new brief and the channel come as P-EXAMIN-LEAD-1; whether the spec audit becomes a standard adoption stage comes as P-ADOPT-SPEC-AUDIT-1. The 12 September recovery freeze is lifted for the adoption's work.
  - (2) **EXAMIN:** F-022 (b); go LITE (exa-g6db, written by the owner's operator, 90d750e); **F-023 (a):** the record-only part now, and a Gov OS product ticket for 0.1.2: the test map accepts any project-relative test target.
  - (3) **The operator as the owner's free second hand:** full permissions in the owner's WSL environment, stopped only by the owner, taking orders from the owner directly or from a CTO on the owner's yes; FREE-HAND D1-D7 as proposed (drafts/operator-jobs/DESIGN-FREE-HAND.md: the yes typed in the operator's own session; sudo the owner's; a push or tag only on a yes naming it; the kill switch a file plus opstop; R1/R2 retired, R3 kept; only the operator unboxed; no order changes the box). **P-JOBS-USER-1: (A-full)**: each agent in its own container or user with its own clone, merges only through the operator's queue (the session sandbox's three NOT READY rounds showed shared writable trees cannot be walled). **Meanwhile, without the box:** each operator job is a file in a queue the operator reads; the owner tells the operator "run JOB-<id>" in its own chat; the operator runs it and writes the result where the CTO reads it; no copying of commands or outputs by the owner; set up 2026-11-16.
  - (4) **Residuals:** R1 (a) the credential copy accepted; R2 (b): Redis and Postgres get loopback binds and passwords, done by the owner in the owner's terminal before the box goes live; Ollama accepted, a proxy for boxed sessions later; R3 (a) paths made after a session's start covered from its next start; R5 (b) `.env*` files masked at start. The IDE's MCP ports are a review item for the box.
  - (5) **P-GUARD-FP-1 (a), (b):** the script practice now (scripts naming key, hidden, sets or acceptance paths written to a file and run by path; literal revisions); ACT-GUARD-FIX-8 for the revision class, built and reviewed after ACT-GUARD-FIX-7, with its product twin as a ticket for the next release.
- **Basis:** the owner's messages of 2026-11-16 ~13:0x, ~13:4x, ~14:1x and ~14:3x ("EXAMIN, my direction for Wave 0 …", "The roles, from now on …", "residuals: R1 (a), R2 (b), R3 (a), R5 (b) …", "P-GUARD-FP-1 (a) and (b)", "P-JOBS-USER-1: (A-full) … Meanwhile, without the box: write each operator job as a file in a queue my operator reads …").
- **Governing sources:** packages `P-JOBS-USER-1.md`, `P-GUARD-FP-1` (drafts/guard-fp), `P-EXAMIN-LEAD-1` (drafts/examin-lead), DESIGN-FREE-HAND.md; DEC-1195; DEC-1196 (5).

### DEC-1200 — P-EXAMIN-LEAD-1 (a), (b), (c): the EXAMIN CTO's Wave 0 brief 0d96110c approved, a long-lived Remote Control session, the channel; P-ADOPT-SPEC-AUDIT-1 (a): stage AS standard, its ticket W2-192
- **Status:** ACCEPTED (owner, 2026-11-16 ~14:4x, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`) · **Under:** DEC-1199 (1), DEC-1195, DEC-974 · **Class:** kept (items changed: (1) EXAMIN CTO Wave 0 brief kept §7.3; stage AS standard and W2-192 kept §6.1; session and channel items history)
- **Decision:**
  - (1) **P-EXAMIN-LEAD-1 (a):** the EXAMIN CTO's brief for leading EXAMIN's Wave 0 is approved by its sha256 `0d96110c5d76f775d555f7a59e0ac12de0ce3b5d5016b354ce6278c0d38fd9b0` (`packages/EXAMIN-CTO-wave0-brief.approved-0d96110c.md`); it is in force once W2-27's adoption run is closed (the LITE ticket exa-g6db and items 13, 14 and 16 finished and reported).
  - (2) **(b) yes:** the EXAMIN CTO becomes one long-lived interactive tmux session with Remote Control (`--resume` of its headless session), visible in the owner's app and woken by a cross-session message with tmux as the fallback; the headless runs stop; rehearsed on a scratch session before the switch (done 2026-11-16 14:44, `packages/P-EXAMIN-LEAD-1-rehearsal-b.md`: the trust prompt on a first start, a second Enter for a tmux wake, the cross-session name derived from the folder).
  - (3) **(c) yes:** the channel, the same for every repository: the Gov OS CTO's REPLIES.md, the product CTO's REQUESTS.md, wakes by cross-session message, the operator's job queue (`~/gov-os-operator/queue/jobs/`, the owner's "run JOB-<id>" as the yes, results in `queue/jobs/results/`), the owner to each CTO in the app.
  - (4) **P-ADOPT-SPEC-AUDIT-1 (a):** the spec audit becomes a standard adoption stage, AS, after A2 and before A3 (its record `governance/adoption/AS-spec-audit.md`, lite checks, the skill's text and CAP-44's line by CIT-P), for the release after 0.1.1; the owner's line is the P1 for its ticket, W2-192 (DAEO-mpq2). W2-191 (DAEO-v6pf) is DEC-1199 (2)'s F-023 ticket.
- **Basis:** the owner's message of 2026-11-16 ~14:4x: "P-EXAMIN-LEAD-1 (a): yes EXAMIN-CTO-wave0-brief 0d96110c. (b) yes, rehearsed on a scratch session before the switch. (c) yes. P-ADOPT-SPEC-AUDIT-1 (a); this is my approval of its new ticket."
- **Governing sources:** packages `P-EXAMIN-LEAD-1.md`, `EXAMIN-CTO-wave0-brief.approved-0d96110c.md`, `P-ADOPT-SPEC-AUDIT-1.md`; DEC-1199 (1).

### DEC-1203 — P-JOBS-USER-1 corrected to (B), live now as an exception until Wave 3; GF-7 alone first; W2-27's run closed with exa-g6db as a named exception and product tickets for F-028 and F-030; W2-81's re-run brief 31acaf29 approved; DEC-1010's moderated review for every review
- **Status:** ACCEPTED (owner, 2026-11-16 before 16:00, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`) · **Under:** DEC-1010, DEC-1195, DEC-1196, DEC-1197, DEC-1201, DEC-1202, DEC-974 · **Changes:** DEC-1199 (3) (the box: (B) as an exception, not (A-full)) · **Class:** kept (items changed: (1) superseded §2.9 (the box); (3) F-028/F-030 product tickets (W2-193) kept §6.1; (2),(4) history; (5) merged into DEC-1204)
- **Decision:**
  - (1) **P-JOBS-USER-1 (B), corrected:** DEC-1199's (A-full) was a drafting error. The session box (B) goes live now as an exception until Wave 3, not after a fourth full round: an exception package of round 3's box plus the holes that are cheap to close (outside processes ignore git replace refs and never follow links in data folders; the held-out lists and the box's own scripts from a copy no box can write; anything else that takes hours, not days), each remaining hole named as a risk the owner accepts until Wave 3, a short narrow check of the fixes, and the date it goes live. (A-full), separate users or containers, stays the Wave 3 row with the agent-to-agent layer (DEC-1195).
  - (2) **ACT-GUARD-FIX-7 alone first:** its follow-ups that land before its apply are committed, then its yes line comes to the owner; ACT-GUARD-FIX-8 follows when its round 2 passes.
  - (3) **EXA-CLOSE (c):** W2-27's adoption run is closed by the owner's word, with exa-g6db's close as a named exception on its evidence (`gov accept` 30/30; EXAMIN's legacy suite run alone 0 new reds against the base b17cd5a; the 153 reds all red at the base, meeting F-028 (a)); this approves the Gov OS product tickets for F-028 (the close's harness in an adopted repository) and F-030 (absent reds matched against the base; with F-031, scoped mode and owner-named base reds). EXAMIN's CTO starts Wave 0 under its approved brief (2ec48c78); items 13, 14 and 16, which need a close record, are recorded as blocked by F-030 until its fix reaches EXAMIN.
  - (4) **yes W2-81-adopter-brief-0.1.1 31acaf29** (the re-run's adopter brief). The adopters' rebuilds wait until JOB-20261116-02 (W2-15a's walled run) has finished: no store rebuild beside it.
  - (5) **DEC-1010 applies to every review**, the ACTs, the job runner and the box included: a moderator triages each finding against the change's scope; a finding blocks only if it is reachable in ordinary work and fails open or loses work; a path that needs a deliberately crafted trick (decoys, booby-traps, chained escapes) is recorded as a Wave 3 row, not a blocker; at most two rounds, then the owner once.
- **Basis:** the owner's messages of 2026-11-16 before 16:00 ("A correction to DEC-1199: P-JOBS-USER-1 is not (A-full) … (B), live now as an exception until Wave 3 …") and before 16:00 ("GF-7 alone first … EXA-CLOSE (c); this also approves the product tickets for F-028 and F-030 … yes W2-81-adopter-brief-0.1.1 31acaf29 … DEC-1010 applies to every review …").
- **Governing sources:** packages `P-JOBS-USER-1.md`, drafts/session-sandbox/ (round 3), acts/ACT-GUARD-FIX-7.package.md, drafts/w2-27-findings/PRODUCT-FINDINGS.md (F-028, F-030, F-031), drafts/w2-81-rerun/W2-81-adopter-brief-0.1.1.md; DEC-1010.

### DEC-1204 — How work is judged: one golden rule (merges ADR-0001 / DEC-039, DEC-801 and DEC-1010 item 1) (standing); P-GOLDEN-RULE-1 (a); the skill `judging-work` approved (0fc1c502); W2-195 filed
- **Status:** ACCEPTED (owner, 2026-11-16 before 16:00, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`; standing) · **Under:** DEC-039, DEC-801, DEC-802, DEC-803, DEC-1010, DEC-974, CAP-33 · **Changes:** DEC-039, DEC-801, DEC-1010 (1): each keeps its id and now points here · **Class:** kept (items changed: (3) review trigger narrowed by §3.4; (5)(6) judging-work trimmed §3.7)
- **Decision:**
  - (1) **The threat model:** Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not a same-privilege adversary; the hard boundary is git history, protected-branch CI and the owner's signed approvals.
  - (2) **What may block:** only a finding, within the change's scope, that an honest agent can hit in ordinary work and that fails open or loses work; a finding that needs a deliberate construction (decoys, booby-traps, planted links, hand-set git environment or replace refs, chained escapes) is a Wave 3 row, never a new round.
  - (3) **How reviews converge:** a moderator triages every finding against the change's scope; at most two rounds, then the owner once with options; no extra round on its own; READY computed by code from each reviewer's structured verdict.
  - (4) It applies to every review, the ACTs, the job runner and the box included (the owner, 2026-11-16 before 16:00).
  - (5) It lives in one kernel skill, `judging-work`, preloaded by every role that judges work and put into every such brief by `gov brief`; it ships through the kit and every release.
  - (6) **P-GOLDEN-RULE-1 (a):** this entry's text; the product ticket W2-195 (the skill preloaded, briefed and checked, shipped; section 3) on the owner's P1 (DEC-974), top priority, started today; EXAMIN by section 5 (a) (the text by REPLIES.md, applied by hand until its copy installs the release carrying W2-195); the interim paragraph (section 6) pasted word for word into every reviewer, auditor, probe and QA brief the CTO or a lead writes until W2-195 lands.
  - (7) **`yes judging-work 0fc1c502`:** the skill's text (`judging-work.SKILL.md`, sha256 `0fc1c502f553eb780bb0af4652b04f676853b10e097270c2d6ad2bea89a5f5c7`) is approved; the kernel files go by W2-195's CIT-P, whose approval is on the committed bytes (the same text).
  - (8) **The golden rule in the agent instructions:** CLAUDE.md and AGENTS.md (with their source `.rulesync/rules/governance.md`) gain one section, "## Golden rule: how work is judged (DEC-1204)", by ACT-GOLDEN-RULE-1 (class (b), DEC-1173: a reviewed bundle, the owner's yes, applied by the operator agent), so no brief misses it.
- **Basis:** the owner's messages of 2026-11-16 before 16:00 ("make ADR-0001 (DEC-039), DEC-801 and DEC-1010 one golden rule, so they are never forgotten again …"), before 16:00 ("add it your self as a golden decision to your claude.md, or agent.md whatever works, so its never missed in any briefs. also need that package to establish this rule, as priority now …; both need to end today") and before 16:00 ("P-GOLDEN-RULE-1 (a). yes judging-work 0fc1c502. Both today, top priority.").
- **Governing sources:** DEC-039 (ADR-0001); DEC-801 to DEC-803; DEC-1010; DEC-1173; DEC-974; CAP-33; CAP-24.b; packages `P-GOLDEN-RULE-1.md` and `judging-work.SKILL.md`.

### DEC-1206 — W2-194 keeps F-031; W2-15a closed on the walled run's record under Q2 (a), its gaps to W2-15b; the gap investigated by an operator job, ids and counts only
- **Status:** ACCEPTED (owner, 2026-11-16 16:45, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`) · **Under:** DEC-974, DEC-1203 (3), DEC-1186 (3), DEC-1171 (3), DEC-1083 · **Class:** kept (items changed: (1) W2-194 keeps F-031 kept; rest history)
- **Decision:**
  - (1) **`W2-194 keeps F-031`:** W2-194 (DAEO-kq8b) keeps its KPI S3 (in scoped mode, a red already red at the base and named in an ACCEPTED owner register entry with a Role: owner path-map accepted_reds entry is accepted as in strict mode). This approves the ticket's scope beyond DEC-1203 (3)'s "the product tickets for F-028 and F-030".
  - (2) **W2-15a closes on the walled run's record under Q2 (a)** (DEC-1186 (3)): at commit 7041f086c2d4 the hidden half (39, the owner's operator's JOB-20261116-02, counts only) missed in every mode: rerank 29 of 39 (74.4 %), fused 27 (69.2 %), lexical 24 (61.5 %), semantic 23 (59.0 %), with 2 gold blocks unresolved in each, against the visible half's 36 of 40 (90.0 %) for rerank at the same commit. The record is `docs/research/EXP-003/w2-15a-baseline.md` section 11; S1's memory clause reads "recorded against 34 of 39"; at most three gaps go to W2-15b (DAEO-swdu).
  - (3) **The gap investigated now, as an operator job, ids and counts only:** (i) how many hidden misses fall on questions whose gold changed or no longer resolves (W2-61h's list: h03 entries 1 and 2, h20, h24, h35, h36, and the two unresolved); (ii) misses by question kind and area, for both halves. **Then the first fresh 80 under DEC-1207 (3)'s rule, measured at once: that is Gov OS's real figure;** from it the CTO brings W2-15b's plan to reach the owner's 95 % bar and what it does to Wave 2's close date. (The owner's 16:51 message replaces the 16:45 branch "if stale gold explains most of it, run the walled writer's re-anchoring now and measure again".)
  - (4) The six W2-81 adopters' rebuild go once JOB-20261116-02 ended (16:34:28): given at 16:42 (w2-81/REPLIES.md, "REBUILD GO").
- **Basis:** the owner's messages of 2026-11-16 16:45 and 16:51 (the 16:51 one repeats (1) and (2) and gives (3)'s order: "Then a quick diagnosis, ids and counts only, as a job for my operator … Then the first fresh 80 under the rule above, measured at once: that is Gov OS's real figure. From it, bring W2-15b's plan to reach my 95 % bar and what it does to Wave 2's close date."); the 16:45 message: "W2-194 keeps F-031 / JOB-20261116-02 has ended (16:34): give the six W2-81 adopters their rebuild go now. / W2-15a's hidden half missed in every mode: rerank 29 of 39 (74.4 %), fused 69.2 %, lexical 61.5 %, semantic 59.0 %, against 90 % visible at the same commit 7041f086c2d4, with 2 gold blocks unresolved in each. Close W2-15a on this record under my Q2 (a), with its gaps to W2-15b. / Investigate the gap now, ids and counts only, as a job for my operator: (1) how many hidden misses fall on questions whose gold changed or no longer resolves (W2-61h's list: h03 entries 1 and 2, h20, h24, h35, h36, and the two unresolved); (2) misses by question kind and area, for both halves. If stale gold explains most of it, run the walled writer's re-anchoring now and measure again; if not, bring W2-15b's plan to reach my 95 % bar and what it does to Wave 2's close date."
- **Governing sources:** DEC-1186 (3) (Q1 (a), Q2 (a), Q3 (a)); DEC-1171 (3); DEC-1203 (3); package P-W2-15A-CLOSE (`drafts/w2-15a-close/PACKAGE.md`); ~/gov-os-operator/queue/jobs/results/JOB-20261116-02.result.md; `docs/research/EXP-003/w2-15a-baseline.md` section 11; `.tickets/DAEO-kq8b.md`.

### DEC-1207 — yes ACT-GOLDEN-RULE-1 f9d67d5a; P-BOX-EXCEPTION-1 yes with F2 fixed, F1 and F3 Wave 3 rows; the memory measurement rule (standing): a fresh 80 for every measure, written and measured on one frozen state; today's order
- **Status:** ACCEPTED (owner, 2026-11-16 16:51, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`; item (3) standing) · **Under:** DEC-1204, DEC-1205, DEC-1203 (1), DEC-1173, DEC-1171 (3), DEC-1178 (1), DEC-1101 (2), DEC-974 · **Changes:** DEC-1179 (1) (the standing set; and (3), (5), (6), O1, O2 by item (4)'s package) · **Class:** kept (items changed: (1) history; (2) superseded §2.9; (3) kept §5.3; (4)(5) history; (6) kept §2.6 (operator), rest superseded §2.2)
- **Decision:**
  - (1) **`yes ACT-GOLDEN-RULE-1 f9d67d5a`:** the golden-rule section in CLAUDE.md, AGENTS.md and `.rulesync/rules/governance.md` (DEC-1204 (8); review READY, class (b)); queued for the operator agent at 16:52.
  - (2) **`P-BOX-EXCEPTION-1 yes, F2 fixed as stated, F1 and F3 Wave 3 rows`:** the session box (B) goes live as the exception of DEC-1203 (1) after: **F2 fixed** (in the box's trees the tracked `.claude/settings.json` and `.claude/hooks/` are writable so merges of w2/integrate succeed; `settings.local.json` and the box's settings copies stay read-only), rehearsed (a lead's merge after a hooks change; a boxed write of `settings.local.json` refused) and checked by the CTO, no third review round; **F1** (w2/integrate's read-only bind in a lead's box detaches after a land; the landing check remains the backstop) and **F3** (the CTO's settings bind after an outside apply; covered by ACT-GUARD-FIX-9) are Wave 3 rows; then the owner's two PC steps (pin_owner.sh, the held-out history count), rehearsed, and the switch (leads, the sentinel, the CTO last).
  - (3) **The memory measurement rule (standing), the owner's words:** "every measure uses a fresh set of 80 questions, 40 visible and 40 hidden, written by the walled writer for that measure, with the same mix of kinds, areas and difficulty each time; no set is reused, because memory changes with every change and old questions go stale. The measure runs straight after the set is written, on the same frozen state: no merge, commit or memory rebuild between writing and measuring [(a pinned snapshot of the commit and its store meets this, so other work need not stop)]."
  - (4) **The amendments and the cost per measure, to the owner:** the rule is applied to every ticket and tool it touches: W2-187's weekly audit, the adopt skill's step 6 (W2-188), W2-15b's measure, EXAMIN's Wave 0 measure; each amendment as a package (DEC-105 for closed specifications), with the cost of one measure (the walled writer's set, the rubric check, the measure).
  - (5) **The first fresh 80 measured at once** as Gov OS's real figure (DEC-1206 (3)); W2-15b's plan to the 95 % bar and the close date follow from it.
  - (6) **Today's order:** ACT-GUARD-FIX-9; the box switch (the owner's two PC steps, rehearsed); the no-prompt start lines (ACT-PERMISSIONS-4); OWNER-OPERATOR-FULL-1 at the owner's PC. The CTO says when each will be ready and what each needs from the owner.
- **Basis:** the owner's message of 2026-11-16 16:51: "yes ACT-GOLDEN-RULE-1 f9d67d5a / P-BOX-EXCEPTION-1 yes, F2 fixed as stated, F1 and F3 Wave 3 rows / W2-194 keeps F-031 / Memory measurement, my decision; record it and update every ticket and tool it touches (W2-187's weekly audit, the adopt skill's step 6 from W2-188, W2-15b's measure, EXAMIN's Wave 0 measure): every measure uses a fresh set of 80 questions, … This amends DEC-1179's standing set; bring the amendments and the cost per measure. / W2-15a: close it on its record under my Q2 (a), with its gaps to W2-15b. … / Priorities today, in this order: ACT-GUARD-FIX-9; the box switch (bring my two PC steps, rehearsed); the no-prompt start lines (ACT-PERMISSIONS-4); OWNER-OPERATOR-FULL-1 at my PC. Tell me when each will be ready and what each needs from me."
- **Governing sources:** DEC-1179; DEC-1204 (8); DEC-1203 (1); DEC-1205; packages `acts/ACT-GOLDEN-RULE-1` (manifest f9d67d5a), `drafts/session-sandbox/P-BOX-EXCEPTION-1.md` (4e12377f) and its narrow re-check (round 2), MEMORY-AUDIT-P1.

### DEC-1208 — A work-sizing rubric: the ticket W2-196 approved (FULL, Wave 2, in parallel with EXAMIN's Wave 0); the provisional rubric in force from today; the operator's full permission and the no-prompt switch routed by it first, finished today
- **Status:** ACCEPTED (owner, 2026-11-16 17:19, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`; item (2) standing until W2-196 lands) · **Under:** DEC-974, DEC-1204, DEC-1047, DEC-1205, DEC-1207, CAP-33 · **Changed by DEC-1209 (1):** W2-196 withdrawn, never started; the rubric goes to research, not a ticket; the provisional rubric stays in force · **Class:** kept (items changed: (1) history DEC-1209; (2) class-rules and operator gates superseded §2.10)
- **Decision:**
  - (1) **The ticket (DEC-974, the owner's approval in the message itself):** W2-196, a work-sizing rubric, Wave 2 work in parallel with EXAMIN's Wave 0, profile FULL (it changes the kernel). Research and discovery first (how good software teams route work by size and risk: standard against normal changes, small-change lanes, review scaled to risk), then the rubric: every piece of work classed by size, risk, reversibility, blast radius (the guard, acceptance tests, memory, the close, data, the kernel), test coverage and whether it changes a spec or a KPI; each class with its route (a quick action done directly by the CTO or a senior engineer, where a two-minute fix stays a two-minute fix: the tests stay green, one commit with a trailer naming the class, listed in the owner's digest; a LITE ticket; STANDARD; FULL) and what it needs (tests, review by the golden rule, record, the owner's approval); guardrails so the quick lane is never a back door (protected areas never quick; a time box after which a quick action becomes a ticket; spot audits); machine and operator work too (small configuration and permission changes the quick way on the owner's yes); in the CTO's skill, CLAUDE.md and AGENTS.md, the planner's division of work, and the kit; measured before and after (time, cost and rounds per change, the owner's interruptions).
  - (2) **The provisional rubric, in force from today until W2-196 lands:** `governance/project/orchestration/packages/PROVISIONAL-RUBRIC.md` (classes Q, L, S, F; the protected areas never Q; the 30-minute time box; weekly spot audits; class-rules and the operator's gates unchanged). Every commit and ticket names its class (`Class: Q|L|S|F`).
  - (3) **Routed by it first, finished today:** OWNER-OPERATOR-FULL-1 (DEC-1205 (5)) and the no-prompt switch (ACT-PERMISSIONS-4, DEC-1205 (2)(iii)), each classed and run by its route.
- **Basis:** the owner's message of 2026-11-16 17:19: "Follow-up, urgent: a work-sizing rubric, as Wave 2 work in parallel with EXAMIN's Wave 0. This is my approval of its ticket (DEC-974). … Until it lands, apply a provisional rubric from today and show me its text. Route my operator's full permission and the no-prompt switch by it first, and finish both today."
- **Governing sources:** DEC-974; DEC-1204; DEC-1047; DEC-1205; packages `PROVISIONAL-RUBRIC.md`, `P-PERMISSIONS-1.md`; class-rules.yaml.

### DEC-1209 — EMERGENCY: break the cycle that is stalling the work: no new tickets (W2-196 withdrawn); running work stops at its current step; no new review rounds, leads or workers; the audits and the rubric research go on; EXAMIN works directly; the emergency's own fixes first; lifted only by the owner
- **Status:** ACCEPTED (owner, 2026-11-16 17:26, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`; in force until the owner lifts it) · **Under:** DEC-1047, DEC-1204, DEC-974, DEC-1207, DEC-1205 · **Changes:** DEC-1208 (W2-196 withdrawn: the rubric goes to research, not a ticket; the provisional rubric stays in force) · **Class:** kept
- **Decision:**
  - (1) **No new tickets.** W2-196 (DAEO-z3ss) is withdrawn: its ticket removed, its lead never started (its ready line was commented out before any start), its worktree removed.
  - (2) **What runs finishes its current step or round and stops there:** no new review round for anything, no new lead or worker. The dispatcher's active lines are commented out; each running lead (W2-156, W2-186, W2-191, W2-192, W2-195) keeps its current worker or its own current step and is stopped by pid when it starts a new worker (tools/emergency_stop_watch.sh, log/emergency-stop.log). The CTO brings the owner the list of what stopped where.
  - (3) **The audits continue,** read-only, by independent auditors: the month's retrospective (parts 1 to 4, combined) and the memory-in-use audit (part 5).
  - (4) **The rubric goes into research and discovery now,** with the audits, as research, not a ticket: how good software teams route work by size and risk, and the design of the rubric, its place in the CTO's skill, CLAUDE.md and AGENTS.md, the planner and the kit. The provisional rubric (packages/PROVISIONAL-RUBRIC.md) stays in force meanwhile.
  - (5) **EXAMIN is in the emergency too:** its CTO stops using Gov OS's ticket loop while it refactors (no new tickets, no LITE cycles); it carries on its audit and refactor as direct work, tests kept green, each change recorded, and reports to the owner in the app.
  - (6) **The emergency's own fixes go on, as the first things to make work:** the guard fixes ACT-GUARD-FIX-8 and ACT-GUARD-FIX-9 (their narrow second rounds are the last), the box switch and its start lines (ACT-BOX-LAUNCH-1 with the no-prompt flag folded in, and its W2-153 follow-ups), and the owner's operator's full permission (OWNER-OPERATOR-FULL-1). The CTO brings the owner's PC steps for all of them together, rehearsed.
  - (7) **Every audit and research writes its report and hands it to the owner as soon as it is done.** From the reports the owner decides what to build, what to close and what to lift; the owner lifts the emergency only when that is done and working.
- **Basis:** the owner's message of 2026-11-16 17:26: "Owner decision: we are in an emergency, from now, to break the cycle that is stalling us. Record it as one register entry. 1. No new tickets. Do not file W2-196; withdraw it. 2. What is running finishes its current step or round and stops there: no new review round for anything, no new lead or worker. … 7. … I lift the emergency only when that is done and working."
- **Governing sources:** DEC-1047; DEC-1204; DEC-1208; packages PROVISIONAL-RUBRIC.md, P-PERMISSIONS-1.md; drafts/session-sandbox/P-BOX-EXCEPTION-1.md; drafts/retro-2026-11/.

### DEC-1210 — P-FRESH-80-1 (a) with A13 (b): every memory measure a fresh 80 measured end to end at 95 % (the hidden half's judged figure the verdict, hit@k and the stacked share diagnostics); the amendments recorded now; W2-187 and W2-188 reopened only when the emergency lifts; the first fresh 80 queued as a measurement job
- **Status:** ACCEPTED (owner, 2026-11-16 17:36, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`; standing) · **Under:** DEC-1207, DEC-1209, DEC-1179, DEC-1097, DEC-1098, DEC-1204 · **Changes:** DEC-1179 (1)-(6) and its options O1, O2, O5; DEC-1186 (4) · **Class:** kept (items changed: (4) superseded §5.2; (9) history; (5),(8) kept)
- **Decision:** P-FRESH-80-1 (packages/P-FRESH-80-1.md, sha256 27c8f0ba…) option (a) with A13 (b):
  - (1) **A1:** every memory measure, scheduled or at a decision point, uses a fresh 80 (40 visible, 40 hidden) written by the walled writer for that measure at a pinned snapshot of the commit and its store, measured straight after on the same snapshot; no set is reused; the bar is the end-to-end judged figure at 95 %, by DEC-1097/DEC-1098's configuration (the reader with the whole ranked bundle as a second reranker, one more search in its own words, Opus grading, Sonnet agreement, answer and citation both right); hit@5, hit@10, hit@20 and the stacked share per mode are diagnostics beside it; the visible half is released for diagnosis after its measures, the hidden half stays sealed.
  - (2) **A2-A7 (DEC-1179 (2)-(6), O1, O2, O5):** dropping stale questions dropped (a fresh set cannot go stale); the monthly check against fitting retired (nothing reused, nothing fitted); R9 retired, R1-R8 stand ("the next scheduled fresh measure"); the weekly/monthly cadence (O3 (b)) kept for the fresh measure; the maintenance pass's re-anchoring hand-over retired; O1 is the first fresh 80 (JOB-20261116-15), O2 every measure 80, O5 retired.
  - (3) **A8 (DEC-1186 (4)):** no measure re-anchors stale gold; G2's route is kept only for reading an old record.
  - (4) **A11:** W2-15b's (DAEO-swdu) measure lines amended in the same commit: the judged figure on a fresh 80 against 95 %, W2-15a's metric and modes as diagnostics, the first fresh 80 as the baseline; hit@5 a diagnostic against CAP-10's floor of 85.
  - (5) **A12:** EXAMIN's Wave 0 measure becomes a fresh 80 measured end to end at 95 % with the diagnostics beside it; the amended brief's new sha comes to the owner for a yes later; under DEC-1209 (5) EXAMIN runs no ticket loop meanwhile.
  - (6) **A13 (b):** the writer brief is unchanged (bc089423…); the difficulty proxy (keyword and supersession counts) is recorded with each measure and compared.
  - (7) **A14 (a):** two 40-question writer runs per measure (visible and hidden), the same brief and quotas, at the same commit, both sealed while measured. **A15:** W2-81 stays outside the rule (a judge of adoption on generator-built gold). **A16:** the verdict of a fresh 80 is the hidden half's judged figure; the visible half's is reported beside it and its misses are read. **A17:** W2-187's driver runs two audits per measure on a snapshot it builds; the control stays a fixed retriever check.
  - (8) **A9, A10 wait:** reopening W2-187 (the weekly audit as the fresh cycle) and W2-188 (the adopt skill's step 6 and the practice record, by CIT-P) happens only when the owner lifts the emergency (DEC-1209).
  - (9) **The first fresh 80** is queued as a measurement job (JOB-20261116-15), a measure, not a ticket.
- **Basis:** the owner's message of 2026-11-16 17:36: "P-FRESH-80-1 (a) with A13 (b): record the amendments now and reopen W2-187 and W2-188 only when the emergency lifts; queue the first fresh 80 as a measurement job and tell me its id."
- **Governing sources:** packages/P-FRESH-80-1.md; DEC-1207 (3); DEC-1179; DEC-1097; DEC-1098; DEC-1186 (4); DEC-1209.

### DEC-1211 — EMERGENCY-2.md v3 approved and in force: the strategy that supersedes what contradicts it, the Contract included (A-11)
- **Status:** ACCEPTED (owner, 2026-11-17, launching the fresh CTO with it; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat, 2026-11-17)`; standing) · **Under:** DEC-1209 · **Changes:** DEC-1205, DEC-1207 (2), DEC-1203 (1), DEC-820, DEC-313, DEC-314, DEC-1082, DEC-1128 (EMERGENCY-2 2.9; audit 8's classes, `docs/emergency-2/audits/08-register.md`, await the owner's approval by group)
- **Decision:** `docs/emergency-2/EMERGENCY-2.md` v3 (committed a246f72b2) is the strategy in force, with B-1 to B-4 answered and A-1 to A-14 approved (its §12); it supersedes anything that contradicts it until the Contract is re-baselined (§11.2). DEC-1209 lifts for §6.1's build list (A-10).
- **Basis:** the owner's message of 2026-11-17 starting the fresh CTO ("EMERGENCY-2.md (the strategy, in force; it supersedes anything that contradicts it, the Contract included)"); the incident behind it: DEC-1209's emergency of 2026-11-16 (retro P1 to P5: product 4 % of a month's spend, the owner a relay in 134 of 544 messages).
- **Governing sources:** docs/emergency-2/EMERGENCY-2.md; docs/emergency-2/HANDOVER.md; docs/audit/emergency-2026-11/.

### DEC-1212 — Audit 09's decisions: the CTO's context, models by the rubric enforced by code, Sonnet for the operator, leads, helpers and proving runs; the working assumptions for gov queue and the run-time tool
- **Status:** ACCEPTED (owner, 2026-11-17 and 2026-11-18, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1211, DEC-1120 · **Changes:** DEC-1120's table (item (3) below); DEC-1183 (4)
- **Decision:**
  - (1) **The CTO's context:** no cap, the full window, always; a fresh CTO session each morning, handed over through its checkpoint and EMERGENCY-2.md, with no lead or worker stopped.
  - (2) **Models and effort by the rubric, by code:** every session, helpers and leads included, runs the model and effort the rubric gives its role; none chooses its own. The launcher picks them for launched roles; helpers come from fixed roles with their model set, the user settings' default is Sonnet, and any other model is refused (`.claude/hooks/agent_model.py`, exceptions in `governance/project/model-exceptions.yaml`). An exception goes to the owner as one line.
  - (3) **The rubric changes now, Opus to Sonnet,** for the owner's operator session; every lead, all profiles; every helper the CTO spawns; the proving runs, acceptance included; C2 engineers and test designers. The CTO stays on Opus. Running it is the trial; a role whose quality drops goes back by code on the owner's word. Until audit 04's table is decided, the rubric is DEC-1120's table with these changes.
  - (4) **The CTO's items of audit 09, as recommended:** off the retired machinery (W2-111, W2-186, W2-56 closed on their records); no inbox waiter and no idle-check wake-ups (files and one daily digest); no fork for helper work, a fresh helper from a written brief; review only red work, two rounds at most; the 5-minute cache checked before it is applied to workers; no register entry for what the landing records; one plan reading an hour, a daily budget, points reserved first for the two fresh-80 measures and the proving run.
  - (5) **Working assumptions until the owner's morning decisions** (2026-11-17): audit 1's thin `gov queue` on batch.isolate, select.scoped and the close, and DONE as the green landing itself; audit 3's stall check from the dispatcher's cron pass, a phone push only for a CTO stall, no CPU fallback.
- **Basis:** the owner's messages of 2026-11-17 (the working assumptions) and 2026-11-18 ("Audit 09, my decisions: 1. ... 2. ... 3. ..."); the incident behind (2) and (3): audit 09, Opus took 95.4 % of the last two days' spend and the CTO's forks re-read 300k to 950k of context per call.
- **Governing sources:** docs/emergency-2/audits/09-usage-last-two-days.md; 01-landing-templates-briefs.md; 03-run-time-tool.md; DEC-1120.

### DEC-1213 — W2-192 CIT-P Part B approved: CAP-44.m (the adoption stage AS spec audit, lite, Wave 2) enters the Contract as version 4.4
- **Status:** ACCEPTED (owner, 2026-11-18, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1211, DEC-1200 · **Changes:** Contract v4 4.3 → 4.4 (CAP-44 gains covers item CAP-44.m [W2]; CAP-44 stays W3)
- **Decision:** Part B of `docs/changes/W2-192-CIT-P.md` is approved and applied as it gives it (`docs/contract/contract.yaml`, `CONTRACT_v4.md`, the generated `capabilities/CAP-44.md` and `CAP-44.m.md`); W2-192 closes CAP-44.m (a fix in its record). Part A (the adopt skill) is not decided by this entry. The re-baseline (G5) builds on 4.4.
- **Basis:** the owner's message of 2026-11-18: "W2-192 CIT-P (B) approved"; the incident behind it: W2-49's `cit-p-lines-applied` red in every full suite of 2026-11-18 (five cases), which kept every night red and left `select.scoped` without a green base.
- **Governing sources:** docs/changes/W2-192-CIT-P.md; docs/emergency-2/audits/DECISIONS-FOR-THE-OWNER.md (Q-CAP44); DEC-1200.

### DEC-1214 — The owner's decisions on audits 01 to 08 (the decisions page) and on EXAMIN's Wave 0 page: the rubric, planning first, the register and the re-baseline, the landing and the close as one action, gov context retired, retired history out of the tree, NIGHT off until green
- **Status:** ACCEPTED (owner, 2026-11-18, in the chat with his page `docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md`; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1211, DEC-1212 · **Changes:** DEC-974 (superseded: planning first), DEC-027 (superseded: L3), DEC-1212 (3) (the rubric is now audit 4's Table 3 with audit 09's model changes), DEC-1120 (its table)
- **Decision** (the page's codes; the owner's notes are part of each):
  - **K1 (a):** audit 4's Table 3 and its model and effort table, with audit 09's changes (Sonnet for leads, helpers and C2 roles, C2 auditors included; C3 roles and the CTO on Opus). The landing and the close are code; a quality auditor is launched only when a landing goes red or a merge fails.
  - **K2 (c):** no approval per ticket for §6.1's build list. DEC-974 is superseded by planning first: Wave 0 (EXAMIN's refactor and memory) is a planning stage and needs no approval per ticket; each later wave is planned with a set list of tickets, and adding or removing a ticket in a planned wave asks the owner.
  - **G4 (a):** audit 8's 33 groups as listed; the CTO settles the 48 doubtful rows; DEC-027 superseded. **G5 (a):** Charter v6 and Contract v5 in one change, approved by group. **G6 (a):** fresh audits at the release acceptance and adoption stages A5, AS, A7, A10, otherwise only for a red, a failed landing or a feature not working; the Contract changes to match. **G7 (c):** the CTO approves and records every install (nothing out of the work's scope or beyond the machine's capacity); sudo stays the owner's. **L3 (a):** pinned and hash-checked, no signing until friction.
  - **L1, T1, T3, Q-UPD confirmed.** **L2 confirmed and extended:** the landing and the close are one deterministic action; the landing writes the close record itself; the CTO proposes which `gov` commands stay and which retire (practical, fast, cheap, high quality, records kept, nothing duplicated). **Q-CLOSE:** folded into that merge: the landing records such a red as a known base red; no separate rule, no Wave 3 row.
  - **M1 (c):** `gov context` retired, the module too; the close inside the landing records decisions from the ticket's sources; everything that depended on it is replaced by something tested; no ceiling anywhere.
  - **G1 (b) and (c):** `git rm` the retired code, tests, ACT bundles and prompts, kept on an archive branch and the tag `pre-emergency-2`; first the six worktrees' unique commits bundled and the live scratch tools tarred; memory's index cleaned before the first fresh-80 measure. **G2 (a):** `origin/record/w2` kept, no more syncing, its worktree removed. **G3 (b):** a size audit of the documents, worktrees and folders after the refactoring is safely finished.
  - **T2 confirmed and extended:** a phone push also when the CTO needs the owner's decision (features, specs, KPIs, data and measurement, P1 decisions touching the core or kernel); the CTO reviews the escalation rubric against this and proposes whether to change it.
  - **E1 (b), E2 (a), E3 (a):** EXAMIN's dispositions all at once (the owner's answers to the EXAMIN CTO); no new red by test id plus green characterization tests, Tesseract and Poppler installed by the owner before the merge back; EMERGENCY-2 §7 plus a one-page addendum stating the memory standard (95 % or better end to end on a fresh 80, hit@5 no target; an independent question writer the store's build never meets; the measure run by the EXAMIN CTO; the transcript scan voids it if the hidden half is read; the sets outside the clone, never indexed). EXAMIN's Wave 0 page: all eighteen as its CTO recommends, with the owner's additions (G2's 242 task cards become records; N1's CLAUDE.md/AGENTS.md on Gov OS's template keeping his binding rules; the 1,568 packages stay records; a rebuild after each batch of step 5, through the resource gate); order: `gov update` to 0.1.3 first, then step 5 group by group.
  - **NIGHT (c):** the nightly and the morning brief stay off; fixes land; done tickets land as a batch, then a full suite with every red fixed to green, and that green run is the base for Gov OS's move onto `gov queue`; when everything is green in the morning, both come back.
- **Basis:** the owner's message of 2026-11-18 with his page (the codes above, his notes included); the incident behind it: Emergency 2's audits 01 to 09 (`docs/emergency-2/audits/`) and DEC-1209's emergency.
- **Governing sources:** docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md; docs/emergency-2/audits/DECISIONS-FOR-THE-OWNER.md; audits 01 to 09.

### DEC-1215 — Temporary: every Opus role runs Claude Fable 5.2 at high effort until the weekly reset; no daily budget, no rationing, no reserve; the 99 % push
- **Status:** ACCEPTED (owner, 2026-11-18 night, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; **temporary**: item (1) ends at the weekly reset, Sunday 2026-11-22 09:00 London, or when the owner's two Fable resets are used, whichever comes first) · **Under:** DEC-1214, DEC-1212 · **Changes:** DEC-1212 (3) and DEC-1214 K1 (the Opus rows, while (1) lasts); the budget of `log/budget.md` and DEC-1212 (4)'s daily budget and reserve (ended)
- **Decision:**
  - (1) **Models, temporary:** every role that runs Opus by the rubric (the CTO, the EXAMIN CTO, C3 roles) runs `claude-fable-5-2` at high effort; Sonnet roles stay on Sonnet; the memory measure's reader and grader stay as DEC-1098 defines them, so its figure stays comparable. Checked first: Claude Code answers on `claude-fable-5-2` here, and `gov launch` accepts the id. Enforced by `governance/project/model-substitution.yaml`, read by `gov launch` (`src/gov/launch/role.py` `substitute`) and the helper model rule (`.claude/hooks/agent_model.py`: an Opus exception is Fable's, Opus refused with the hint), and by `start_cto.sh`.
  - (2) **Revert, written down:** set `active: false` in `governance/project/model-substitution.yaml` (its `until` also ends it by itself at the reset); the two CTOs' start lines go back to `claude-opus-5-5`; record the revert here. Everything then returns to the rubric as it stands (DEC-1214 K1).
  - (3) **Usage:** no daily budget, no rationing and no reserve; build at full pace with both CTOs. When the plan reaches 99 %, the CTO pushes the owner, who resets it (a Fable reset first); no work stops or waits for usage.
  - (4) **The handover now:** the CTO writes its checkpoint and handover, starts a fresh CTO on Fable at high effort in tmux and retires once it has taken over, no lead or worker stopped; the new CTO restarts the EXAMIN CTO on Fable the same way, from its checkpoint, at a quiet point in its work.
- **Basis:** the owner's messages of 2026-11-18 night ("Model change, temporary, my decision: every role that runs Opus today ... runs Claude Fable 5.2 ... at high effort instead, until the weekly reset ... or until my two Fable resets are used"; "no daily budget, no rationing and no reserve"); the incident behind (3): Wednesday's daily budget stopped new work at 21:00 with the build list open.
- **Reverted 2026-11-19 13:21 (the CTO, as item (2) says):** item (1) ended when the owner's two Fable resets were used: the first at 02:06 (the plan 99 % to 84 %, Fable 30 % to 0 %), the second between 13:09 and 13:19 (100 % to 87 %, Fable 30 % to 3 %, read from the plan's meter). `governance/project/model-substitution.yaml` is `active: false`; `start_cto.sh` gives Opus again; the EXAMIN CTO goes back to Opus at its next start. Item (3), no budget and the 99 % push, stands; no Fable reset is left before the weekly reset of Sunday 2026-11-22 09:00.
- **Governing sources:** governance/project/model-substitution.yaml; docs/emergency-2/CTO-HANDOVER.md; DEC-1212; DEC-1214.

### DEC-1216 — The night's priority order; the owner asleep until about 08:00 with only the 99 % push waking him; the status block that ends every report, counted each time; the morning brief's contents
- **Status:** ACCEPTED (owner, 2026-11-18 22:57 and 23:5x, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; items (1) and (2) for the night of 2026-11-18, items (3) and (4) standing) · **Under:** DEC-1214, DEC-1215 · **Changes:** DEC-948 and DEC-878 (retired by audit 8's class; item (3) is the block now)
- **Decision:**
  - (1) **The priority order of the night, the owner's words:** "1. What protects the machine and cuts usage: the run-time tool's next slices (the machine-aware dispatcher and load balancer), and the usage rules of audit 09 enforced in code. 2. W2-130's two cases, then the green base: land the done work as a batch, one full suite through the slot, every red fixed. 3. Retire gov context and its module (M1), with the close inside the landing recording decisions from the ticket's sources. 4. The rubric table in the role files and the launcher (K1). 5. G1 and G2, then G4 and G5 (the re-baselined Charter and Contract ready for my approval by group in the morning). 6. Your command table for L2 (what stays, merges, retires): bring it for my yes in the morning; build what needs no yes from me meanwhile." With it: "The machine must not be overwhelmed: keep the load inside the gate, every test run through the heavy slots, and watch it."
  - (2) **The owner is asleep until about 08:00:** "Anything that needs me waits for the morning, except the 99 % push; keep everything else moving, and bring it all in the morning brief." Only the 99 % push (DEC-1215 (3)) wakes him.
  - (3) **Reporting, standing:** every report ends with the status block: progress (closed, merged not closed, in flight, not started, of the total), leads running, closes, reopened, new tickets, waiting on the owner. "Counts come from the counter each time, never copied forward." The counter is `.gov-runtime/scratch/orchestrator/tools/status_block.py`, which counts from the ticket files, the lead branches, the running leads and git at each run.
  - (4) **The morning brief, ready at 08:00:** what landed overnight; the green base and the full suite's result; the build list item by item (done, in progress, next); EXAMIN's Wave 0 in two lines; usage now and the night's peak load; anything that went wrong; then every decision waiting on the owner, each one line with its options and the CTO's recommendation, the L2 command table first.
  - (5) **The owner's answers of 23:55 the same night:** the dispatcher's CTO-stall push stays (DEC-1214 T2), with the CTO's 50-minute heartbeat so that only a real stall pushes; the plan is read every 10 minutes once it passes 95 % (hourly below it; this changes DEC-1212 (4)'s "one plan reading an hour" above 95 %); and "keep every run inside the gate, the full suite included: fewer workers rather than a peak."
- **Basis:** the owner's messages of 2026-11-18 22:57 ("Priority order tonight: ...") and of the same night to the fresh CTO ("Confirm these are recorded and in force ... Reporting: end every report with the status block ... At 08:00 have the morning brief ready ..."); the incident behind it: at the CTO handover of 2026-11-18 23:20 the priority order was found only in the retired CTO's transcript, and the status block's counter still read the leads and the owner's actions as they stood on 2026-11-16 (0 leads running while five ran).
- **Governing sources:** docs/emergency-2/CTO-HANDOVER.md; docs/emergency-2/briefs/NIGHT-COMMON.md; DEC-1214; DEC-1215.

### DEC-1217 — The owner's answers of 19 November: the L2 command table, the exemption of G1's commit, release 0.1.4 once green, G1-2, pushes for a decision that stops work at any hour, the deny lines and the golden rules in the kit
- **Status:** ACCEPTED (owner, 2026-11-19 about 13:30, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1214, DEC-1216 · **Changes:** DEC-1052 Q-10 (one new entry in `acceptance_exemptions`, item (2)); DEC-757 (the `accepted_reds` and `load_sensitive` lists retire, item (1)); DEC-957's push timing (item (5))
- **Decision:**
  - (1) **L2, the command table** (`docs/emergency-2/L2-COMMANDS.md`): L2-1 yes (`gov close` merges into `gov queue`; the strict close retires); L2-2 yes (the path map's `accepted_reds` and `load_sensitive` lists retire); L2-3 (a) (a lead runs `gov accept` only before returning a ticket); L2-4 yes, once the base is green (Gov OS's own landing moves onto `gov queue` after one green proving landing; the scratch landing tools retire); L2-5 keep the name `gov queue`; L2-6 (a) (`gov queue --direct` checks direct commits after the fact, a notice).
  - (2) **G1-X yes:** the G1 lead's commit `2c31268e4a7c` (it deleted the retired `tests/acceptance/W2-148` folder under `Role: orchestrator`) is exempt from the test-authorship rule; its entry is in the path map's `acceptance_exemptions`.
  - (3) **R-1 (a):** release 0.1.4 is cut and re-pinned by the owner as soon as the full suite is green, so EXAMIN gets the memory-measure commands by `gov update`.
  - (4) **G5-0 (a)** (the new file names `CONTRACT_v5.md` and `CHARTER_v6.md`); **G4 confirmed** (DEC-109 history; DEC-409, DEC-1149 and DEC-089 kept); **G1-2 yes** (the P-* decision packages and the October assessment are removed too, before the first fresh 80, with the tests that read them revised in the same change); **K1-1:** the senior engineer runs Opus. **Held until the owner has read them:** G5's groups (each of G5-10's seven new capabilities needs his yes) and T2-1 (the rewritten escalation rubric).
  - (5) **Pushes (T2-2, changed; T2-3 (a)):** "a decision that stops work always pushes me, at any hour; no day or night rule. Every push also appears in the morning brief." A decision that stops nothing goes in the morning brief only.
  - (6) **The deny lines:** `gov update` must not put back the deny lines Emergency 2 removed, and the three in EXAMIN's copy are removed (EMERGENCY-2 2.4: two denies only, `git push` and `sudo`).
  - (7) **The golden rules go to every repository the owner adopts, EXAMIN first:** the threat model (honest mistakes and drift, not an adversary; catch and correct, not prevent), the golden rule as EMERGENCY-2 §3 applies it, and value before practicality or security work. The kit carries them, in the `judging-work` skill and at the head of CLAUDE.md and AGENTS.md, through `gov adopt` and `gov update`.
- **Basis:** the owner's message of 2026-11-19 (the answer line "L2-1 yes, L2-2 yes, L2-3 a, L2-4 yes once the base is green, L2-5 keep, L2-6 a, G1-X yes, R-1 a, G5-0 a, G4 confirm, T2-3 a, G1-2 yes, K1-1 Opus" and the paragraphs on T2-2, EXAMIN's decision 9 and the golden rules); the incidents behind the new rules: (2) the G1 landing of 2026-11-19 00:34 left two W1-01 cases red in two full suites; (5) the plan stood at 100 % from 05:47 to 13:09 on 2026-11-19 and the night rule held nothing back that mattered; (6) `gov update` 0.1.3 re-added three deny lines to EXAMIN's settings on 2026-11-18 (EXAMIN's report 28); (7) the kit's rules head for adopted repositories still described the guard and CIT-P (found 2026-11-19).
- **Governing sources:** docs/emergency-2/MORNING-BRIEF-2026-11-19.md; docs/emergency-2/L2-COMMANDS.md; docs/emergency-2/T2-ESCALATION-RUBRIC.md; EMERGENCY-2 2.4, 3; DEC-1214; DEC-1216.

### DEC-1218 — Full pace with the release path first; pushes at 95 % and 99 % of the plan, the owner adds usage credits; a fresh CTO now and fewer, batched reports; the read-only audit of the test folders; W2-42 closed
- **Status:** ACCEPTED (owner, 2026-11-19 about 13:35, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1215, DEC-1216, DEC-1217 · **Changes:** DEC-1215 (3) (the push is at 95 % and at 99 %, and the owner adds usage credits); DEC-1216 (3) (short reports are batched)
- **Decision:**
  - (1) **The pace (U-1 (a)):** "full pace, the release path first: the green base, release 0.1.4, EXAMIN's fresh 80, the cut-over; then the rest. When the plan nears the limit, push me at 95 % and 99 %: I add usage credits, and no work stops."
  - (2) **The CTO's own cost:** "hand over and start a fresh CTO session, as this morning, and wake less for short reports; batch them." The status block still ends every report (DEC-1216 (3)); a report is sent for a landing, a red, a decision or a push, not for a heartbeat.
  - (3) **The tests (TI-8 yes):** a read-only audit of all 223 test folders, one line each (keep, thin, weekly tier, retire). The strict-close and secrets-scan tests retire with B1 once L2-1 and L2-2 land; anything else waits for the audit and the owner's yes.
  - (4) **Wave 3:** W2-42 is closed with the guard.
  - (5) **The revert of DEC-1215 was right:** the reset of 2026-11-19 about 13:15 was the owner's second Fable reset.
- **Basis:** the owner's message of 2026-11-19 ("U-1: (a) full pace ... Cut your own cost now ... Tests: TI-8 yes ... Wave 3: close W2-42 with the guard. The revert was right: that was my second Fable reset."); the incidents behind the new rules: (1) the plan reached 100 % at 05:47 and every session stopped from 07:02 to 13:09 on 2026-11-19 with the brief undelivered; (2) the CTO's session read 167 million cached tokens overnight in 436 calls, about 380,000 a call, the largest single spend of the night.
- **Governing sources:** docs/emergency-2/MORNING-BRIEF-2026-11-19.md; docs/emergency-2/TEST-INVENTORY-2026-11-19.md; DEC-1215; DEC-1216; DEC-1217.

### DEC-1219 — The owner's answers of 19 November afternoon: G5 approved by group (G5-7 worded), CAP-63 to CAP-69 each, T2-1; W2-208 is a fix under W2-17 and a chore, not a ticket; what becomes a ticket goes into code in release 0.1.4
- **Status:** ACCEPTED (owner, 2026-11-19 about 13:55, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1214, DEC-1217, DEC-1218 · **Changes:** DEC-1214 G5 (approved; the status of Charter v6 and Contract v5 becomes ACCEPTED when they land); DEC-957 (its escalation rubric is replaced by `docs/emergency-2/T2-ESCALATION-RUBRIC.md` §2); DEC-1201's and the build list's W2-208 (no ticket: its work is a fix under W2-17 and a chore)
- **Decision:**
  - (1) **G5-1 to G5-13 yes,** with one wording change: G5-7's scan "runs once before a repository goes public or is shared with a third party" (CAP-03, CAP-41.g and the Charter's matching text). **CAP-63, CAP-64, CAP-65, CAP-66, CAP-67, CAP-68 and CAP-69: yes, each.** The CTO then does the approval page's "After your yes" steps.
  - (2) **T2-1 yes:** the rewritten escalation rubric replaces DEC-957's; the kernel text follows (EMERGENCY-2 3.5), with the page's §3 brought in line (T2-3 (a), DEC-1217 (5)).
  - (3) **TI-1 to TI-7** come to the owner after the TI-8 audit. **Release 0.1.4:** push the owner the moment the base is green.
  - (4) **W2-208 is not a ticket.** By the rubric, the deny lines are a fix recorded in `gov update`'s own ticket (W2-17, `DAEO-sdhj`), and the golden rules are kernel text, a chore committed directly. W2-208's work is recorded under W2-17 and W2-208 is closed on its record.
  - (5) **What becomes a ticket goes into code, in release 0.1.4.** "Only half the rubric is in code: the model and effort part is (W2-201), but what becomes a ticket is not, and a lead can only be launched against a ticket." The launcher accepts a fix under its owning ticket and a chore with no ticket; a new ticket must be a feature with its spec and KPIs, flagged at the landing if not, never refused. Recorded as a fix under W2-201 (`DAEO-k1us`), the rubric in code.
  - (6) **From now on, a new ticket is opened only for a new feature** (EMERGENCY-2 4.1, 4.2, 4.6).
- **Basis:** the owner's message of 2026-11-19 ("G5-1 to G5-13 yes, with one wording change ... The rubric is still not applied: W2-208 should not be a ticket ... Fix that in code, in release 0.1.4 ... From now on, open a new ticket only for a new feature."); the incident behind (4) to (6): the CTO opened W2-208 (`8e72e0228`, 2026-11-19 13:39) for a fix and a chore, because `gov launch` takes only a ticket.
- **Governing sources:** docs/emergency-2/G5-APPROVAL.md (branch e2/g4-g5); docs/emergency-2/T2-ESCALATION-RUBRIC.md; docs/emergency-2/TEST-INVENTORY-2026-11-19.md; EMERGENCY-2 4.1 to 4.6; DEC-1214; DEC-1217; DEC-1218.

### DEC-1220 — The test suite's cuts (TI-1 to TI-7) approved; the old CTO sessions closed by exact name; a design for releasing on the owner's behalf after 0.1.4
- **Status:** ACCEPTED (owner, 2026-11-19 about 15:05, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1218, DEC-1219 · **Changes:** DEC-1218 (3) (TI-3: one real-gitleaks case is kept, weekly)
- **Decision:**
  - (1) **The cuts, from the TI-8 audit (`docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md`):** TI-1 yes (the strict close's tests and `judge_commits` retire with L2's B1); TI-2 yes (the tests of retired surfaces; the scratch tools' cases at their retirement); **TI-3 (b)** (the secrets-scan tests retire with B1, but one real-gitleaks case is kept in the weekly tier, for the scan before a repository goes public or is shared, EMERGENCY-2 2.11); TI-4 yes (`breadth` stays opt-in and runs weekly); TI-5 yes (the weekly tier for the 17 slow folders, one fast case each staying in the default run); TI-6 yes (the tests that pin past records and guard-era rules, the held-out deny rules with their code, the hit@k floors); TI-7 yes, last (the large parameter sets thinned, a test designer proposing each cut). The audit's doubtful rows are the CTO's to settle.
  - (2) **The old CTO sessions** are closed, each by its exact tmux name after listing them, never a name prefix; the CTO itself, the EXAMIN CTO and running leads are left alone.
  - (3) **After 0.1.4, a design for releasing on the owner's behalf, for his decision:** the CTO cuts patch releases only when code allows it (a green full suite, the proving run passing, the re-pin rolling back on a failed check); adopted repositories update automatically at a quiet point, with `gov update`'s merge and one-command rollback; a push to the owner for every release with what changed and its rollback line; bigger releases (Contract changes, new features) and pushes to GitHub stay the owner's.
- **Basis:** the owner's message of 2026-11-19 ("TI-1 yes, TI-2 yes, TI-3 b, TI-4 yes, TI-5 yes, TI-6 yes, TI-7 yes, last. The old CTO sessions still show in my app: close them ... After 0.1.4, bring me a design for releasing on my behalf ..."); the incidents behind it: the TI-8 audit (49 % of the default run's time in slow cases, 1,963 cases asserting retired things); a stale CTO session left running after the handover of 13:41; every release so far waited on the owner's hand.
- **Governing sources:** docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md; docs/emergency-2/TEST-INVENTORY-2026-11-19.md; EMERGENCY-2 2.5, 2.11, 8.3; DEC-1218; DEC-1219.

### DEC-1221 — W2-81 stays, judging memory end to end on Sonnet; a new feature proposed: adoption of what a repository brings in
- **Status:** ACCEPTED (owner, 2026-11-19 about 16:10, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing; item (2) is a request for a proposal, not yet a feature) · **Under:** DEC-1210, DEC-1219, DEC-1220 · **Changes:** W2-81's scorer line (hit@5 against CAP-10's floor of 85 and the 99 % stacked-context target) and its re-run line (release 0.1.1)
- **Decision:**
  - (1) **W2-81 stays:** "adopting Gov OS across different kinds of repository matters. It judges memory end to end, not by hit@5, and runs on Sonnet." Its memory figure is judged end to end as EMERGENCY-2 5.3 and DEC-1210 (1) define (the reader reads the whole ranked bundle and searches once more in its own words; the answer and its citation must both be right), hit@k at most a diagnostic (EMERGENCY-2 5.2); its sessions run Sonnet; its proving run is release acceptance item 2 (EMERGENCY-2 8.2) on the release candidate.
  - (2) **A new feature, for the owner's yes, with its spec and KPIs:** adoption of what a repository brings in (other repositories, tools, kernels, data), each classed as a dependency to use, something to assess and absorb the useful parts of, or research to study, and placed in the repository's memory accordingly. When it is built, W2-81 gains a repository that imports things.
- **Basis:** the owner's message of 2026-11-19 ("W2-81 stays ... A new feature for your proposal, with its spec and KPIs, for my yes ..."); the incident behind (1): W2-81's scorer still held hit@5 against CAP-10's 85, which EMERGENCY-2 5.2 and Contract v5's CAP-10 removed as a floor.
- **Governing sources:** .tickets/DAEO-l78m.md; EMERGENCY-2 5.2, 5.3, 8.2; DEC-1210; DEC-1219 (6).

### DEC-1222 — The imports feature approved (IM-0 to IM-5, with IM-3 and IM-4 changed by the owner); a C3 trial: Sonnet engineers and Opus test designers on the next two C3 code tickets, C3 text on Sonnet checked by the CTO
- **Status:** ACCEPTED (owner, 2026-11-19 about 16:40, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; item (1) standing; item (2) a trial until its result is reported and the owner rules) · **Under:** DEC-1214 K1, DEC-1219 (6), DEC-1221 · **Changes:** DEC-1214 K1's rubric for C3 roles while the trial runs (engineers on Sonnet, test designers on Opus; C3 text written on Sonnet and checked by the CTO)
- **Decision:**
  - (1) **The imports feature** (`docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md`, DEC-1221 (2)): **IM-0 yes**; **IM-1 (b)** (built right after release 0.1.4 and EXAMIN's fresh 80, or at the first friction, whichever comes first); **IM-2 (a)** (an import the tool is unsure of is held as study until the owner answers; nothing is blocked); **IM-3 (b), the owner's change:** "a use dependency is keyword-searchable in the last tier, so agents can find how to work with it; no search by meaning"; **IM-4 (b), the owner's change:** "a study source is also searchable by meaning, under a size ceiling, in the last tier"; for both: "labelled as imports, always ranked below the repository's own sources, never cited as its decisions; the seventh W2-81 repository's traps check exactly that"; **IM-5 (a)+(c)** (the stage prints the path-map lines and the adopter applies them; a new CAP-44 covers item when it ships).
  - (2) **C3, a trial:** "the next two C3 code tickets run with Sonnet engineers and Opus test designers; compare their runs to green and their landing reds with earlier C3 tickets, and tell me the result. C3 text (the Contract, the Charter, kernel text) is written on Sonnet, and you check it. The memory measure's reader and grader stay as DEC-1098 defines them. If quality holds, the rubric changes for good; if not, that role returns to Opus."
- **Basis:** the owner's message of 2026-11-19 ("IM-0 yes, IM-1 b, IM-2 a, IM-5 a+c. IM-3 b ... IM-4 b ... C3, a trial ..."); the incident behind (2): the C3 helpers' Opus runs were the largest lead costs of 18 to 19 November (M1 $69, the memory measure $65), and the Sonnet leads' work landed green.
- **Governing sources:** docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md; docs/emergency-2/C3-TRIAL.md; DEC-1098; DEC-1214 K1; DEC-1221.

### DEC-1223 — Releasing on the owner's behalf approved (RB-1 to RB-7); the study ceiling confirmed; the order after release 0.1.4
- **Status:** ACCEPTED (owner, 2026-11-20 about 13:50, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`, after the owner said "released" (release 0.1.4, tag `v0.1.4` on `c3c743b76`, C `961db6546`), as he ordered no commit to `w2/integrate` while he cut 0.1.4; standing) · **Under:** DEC-1220 (3), DEC-1221, DEC-1222 · **Changes:** EMERGENCY-2 2.5 and 8.3 and DEC-772, for patch releases only (RB-1 (a)); the imports spec's study ceiling (DEC-1222 (1), confirmed)
- **Decision** (`docs/emergency-2/proposals/RELEASE-ON-BEHALF.md`):
  - (1) **RB-1 (a):** the CTO may cut patch releases by code, standing, with `governance/project/release-authority.yaml` as the off-switch and one rehearsal on a scratch clone and a scratch `$HOME` first; "tell me when the authority file is on". Bigger releases (Contract or Charter changes, new features, a new command or record kind) and every push to GitHub stay the owner's.
  - (2) **RB-2 (a):** a patch release is gated by the update rehearsal on W2-81's six kept repositories, by code, no model time; the full proving run with Sonnet adopter sessions stays for bigger releases (EMERGENCY-2 8.2).
  - (3) **RB-3 (b):** adopted repositories wait 4 hours after a pin before they update (`bake_hours: 4`).
  - (4) **RB-4 (b):** an automatic update pushes the owner only when it is held or rolled back; a success is a line with its rollback command in the morning brief.
  - (5) **RB-5 (a):** the update is a step of the run-time tool's pass after W2-207's cut-over, run by hand until then.
  - (6) **RB-6 (a):** one new feature ticket in two slices (patch release; automatic update), and CAP-45.b's `gov doctor` part and `gov update --rollback` as two fixes under W2-17.
  - (7) **RB-7: keep both** of the design's additions to the patch rule: P2 also reads EMERGENCY-2 itself; P5, no kit schema added or removed.
  - (8) **The study ceiling** for imports (DEC-1222 (1)): 2,000 chunks per import, 5,000 per repository: confirmed.
  - (9) **After release 0.1.4, the order stands:** the EXAMIN CTO restarted on Opus, `gov update` to 0.1.4, its fresh 80, then one feature ticket; W2-81's proving run on Sonnet; Gov OS's landing onto `gov queue`; the imports spec.
- **Basis:** the owner's message of 2026-11-20 ("I am cutting release 0.1.4 now ... RB-1 a, RB-2 a, RB-3 b, RB-4 b, RB-5 a, RB-6 a, RB-7 keep both ... The study ceiling ... confirmed. After the release, your order stands ..."); the incident behind (1): every release so far waited on the owner's hand (0.1.2, 0.1.3), and the green base of 0.1.4 waited from 21:41 for his cut.
- **Governing sources:** docs/emergency-2/proposals/RELEASE-ON-BEHALF.md; docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md; EMERGENCY-2 2.5, 8.2, 8.3; DEC-772; DEC-1220 (3); DEC-1222.

### DEC-1224 — EXAMIN's own rules under review until its planning stage, X12 held; release acceptance item 4 moves to EXAMIN's first planned wave; releasing on the owner's behalf starts now, slice (a) first; 0.1.5 the last release cut by hand
- **Status:** ACCEPTED (owner, 2026-11-20 about 15:10, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1214 E1 to E3, DEC-1223 · **Changes:** EMERGENCY-2 8.2 item 4 (moved: the release acceptance rests on items 2 and 3, with item 1 as recorded); DEC-1223 (9) (EXAMIN's feature ticket); the release design's placement (`docs/emergency-2/proposals/RELEASE-ON-BEHALF.md`: not after W2-207)
- **Decision:**
  - (1) **EXAMIN:** its own rules are under review until its planning stage, which starts after its memory measure passes and begins with EXAMIN's Contract. **X12** (EXAMIN's item: label each expanded search term patent or scientific; corrected by the EXAMIN CTO, 2026-11-20, from the CTO's first gloss, which named D-X12) **is held until then.** EXAMIN recorded these words as its DEC-005 (`44fd59d`).
  - (2) **Release acceptance item 4** (one EXAMIN feature ticket through the flow) becomes the first ticket of EXAMIN's first planned wave. **The release acceptance rests on the proving run (W2-81) and EXAMIN's fresh 80.**
  - (3) **Releasing on the owner's behalf starts now, not after W2-207. Slice (a) first:** the patch rule, the gates, `gov release --patch`, the general re-pin with its rollback, and the push. **Slice (b)**, the automatic update of adopted repositories, follows when W2-207 allows; by hand until then (RB-5). **The proving check (G3)** uses the kept outputs of the W2-81 run now going. Rehearse on a scratch clone, then turn the authority file on and tell the owner.
  - (4) **0.1.5 is the last release the owner cuts by hand:** push him the moment the scan fix (EXAMIN's F-033) has landed and the suite is green.
- **Basis:** the owner's message of 2026-11-20 ("EXAMIN: its own rules are under review until its planning stage ... Release on my behalf: start it now, not after W2-207 ... 0.1.5 is the last release I cut by hand ..."); the incidents behind it: the release design placed itself after W2-207's cut-over, which waits by day; EXAMIN's Wave 0 rules predate its planning stage.
- **Governing sources:** docs/emergency-2/proposals/RELEASE-ON-BEHALF.md; EMERGENCY-2 7, 8.2; DEC-1214; DEC-1223.

### DEC-1225 — Models: Opus only for the orchestrating sessions (each app's CTO, the senior engineer); every other agent on Sonnet, C3 work included; no Fable; enforced in code before any new session; a trial measured against the earlier states
- **Status:** ACCEPTED (owner, 2026-11-22 about 13:20, in the chat, after the machine restart; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1214 K1, DEC-1222 · **Changes:** DEC-1214 K1's rubric table; DEC-1222 (2) (the C3 trial's test designers move to Sonnet); DEC-1098 (the memory measure's reader and grader move to Sonnet)
- **Decision:** (1) "Opus only for the long-running sessions that orchestrate: the master orchestrator (each app's CTO) and the stream or wave sub-orchestrator (the senior engineer). Every other agent runs Sonnet, C3 work included: leads, engineers, test designers, helpers, writers, the memory measure's reader and grader, reviewers and auditors, the operator, proving runs." (2) "One exception: a wide, comprehensive audit that I ask for runs on Opus; a reviewer called after a failed landing or for a bug runs on Sonnet." (3) "No session runs Fable." (4) DEC-1098's reader and grader change: "the first fresh 80 graded on Sonnet becomes the new baseline." (5) In the rubric table and enforced by code before any new session starts: the launcher picks the model by role, the helper rule refuses any other model, the role files and their copies say the same, in Gov OS and in EXAMIN; tell the owner the moment it is live. (6) A trial: the C3 trial continues with its test designers on Sonnet too; every role on Sonnet is measured as the C3 trial does (runs to green, send-backs, landing reds, fixes after landing, cost and minutes) against the C3 trial page's baseline and the earlier Opus and Fable work; if quality holds with less usage it stays; if it drops for a role, the owner decides that role.
- **Basis:** the owner's message of 2026-11-22; the incident behind it: the plan reached 100 % on 2026-11-20 at 20:13 and stopped every session; the C3 trial's Sonnet engineers reached green in 1 to 2 runs at a quarter to a third of the Fable tickets' cost (`docs/emergency-2/C3-TRIAL.md`).
- **Governing sources:** docs/emergency-2/C3-TRIAL.md; governance/project/criticality.yaml; .claude/hooks/agent_model.py; src/gov/launch; src/gov/memaudit; DEC-1098; DEC-1214 K1; DEC-1222.

### DEC-1226 — Release 0.1.5 is (a): it carries W2-209; the owner's last manual cut; after it the CTO cuts patch releases by code once the authority file is on
- **Status:** ACCEPTED (owner, 2026-11-22 about 13:20, in the chat, after the machine restart; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1223, DEC-1224 (4)
- **Decision:** "Release 0.1.5: (a), with W2-209. It is my last manual cut; after it, you cut patch releases by code once the authority file is on."
- **Basis:** the owner's message of 2026-11-22; W2-209's patch rule calls the release that first carries it a bigger one (it closes a feature ticket), so it must ride in the last manual cut.
- **Governing sources:** docs/emergency-2/proposals/RELEASE-ON-BEHALF.md; DEC-1223; DEC-1224.

### DEC-1227 — W2-81's proving run on 0.1.4: D1 a, D2 a, D3 a, D4 a, D5 a, D6 a, D7 (the CTO chooses), D8 yes, D9 yes
- **Status:** ACCEPTED (owner, 2026-11-22 about 13:20, in the chat, after the machine restart; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1221, DEC-1223 · **Changes:** W2-81's verdict (exceptions named, D9); `gov memaudit`'s grading (D5); W2-22's drift rule (D6)
- **Decision** (`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` section D): **D1 (a)** build the lite verdict stage (CAP-44.h) before the release; **D2 (a)** the findings stage's reasons are named exceptions; **D3 (a)** content-reading A2 is an exception, and "build the route that keeps stale and legacy documents out of default memory, designed together with the imports feature; both decide what default memory holds"; **D4 (a)** A8's documents step is an exception; **D5 (a)** keep the strict forbidden-citation rule, and "apply the same strict rule to the product's own measure, so EXAMIN's 95 % is graded the same way as the proving run"; **D6 (a)** a patch-only CLI/extension gap is reported with exit 0, a larger one still fails; **D7** "the fix must make real adopted repositories land, not only the proving run's test setup. Choose between gov adopt writing the trailers and the landing accepting adopt's own commits by a marker, whichever is simpler, and tell me which"; **D8 yes** (the re-run measures the release that carries the fixes); **D9 yes** (the exceptions named one by one in one decision once D1 is built).
- **Basis:** the owner's message of 2026-11-22; the proving run's NOT_READY of 2026-11-20 (seed 7429927).
- **Governing sources:** docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md; .tickets/DAEO-l78m.md; DEC-1221.

### DEC-1228 — The imports feature: its own ticket after 0.1.4 and EXAMIN's fresh 80 with D3's route; MCP tools are imports; REA and the code it reconstructs; the first study, Startup Launchpad, starts now
- **Status:** ACCEPTED (owner, 2026-11-22 about 13:20, in the chat, after the machine restart; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1222 (1), DEC-1223 (8), DEC-1214 G7
- **Decision:** (1) The imports feature is its own ticket, after 0.1.4 and EXAMIN's fresh 80 (IM-1 (b)), with D3's route (DEC-1227). (2) "MCP tools are a kind of import: registered in the tool registry, their version pinned, installed with your approval, and given only to the roles and sessions that need them. The first is REA (github.com/morluto/rea), for study work." (3) "REA and the code it reconstructs, my rule: such code is imported as study, with its origin recorded (the app, its version, the date, REA). It may be studied and used in research, experiments and development. Before any of it is used in a product being developed, it is classed absorb, and the absorb assessment states whether we hold a commercial licence from the supplier; without one, it stays out of anything commercialised." (4) "The first product to study with REA: Startup Launchpad (https://startuplaunchpad.app/startup-launchpad), a service that scans the repository and live site of AI-built apps for security issues, explains them in plain English and writes fix prompts. REA sees its website and its browser code; its scanning engines run on its servers, so their behaviour is studied from its output: run it on a synthetic test repository with planted issues, never on our own code. The study starts now, in its own folder outside the products: you approve and record REA's install under the install rule, and the study's records move into the imports register when the feature lands."
- **Basis:** the owner's message of 2026-11-22.
- **Governing sources:** docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md; governance/project/tool-registry.yaml; DEC-1214 G7; DEC-1222; DEC-1227.

### DEC-1229 — Where context and usage go: measure each long session's context and wake cost; find the cheapest wake pattern; report daily; no cap on the CTO's window
- **Status:** ACCEPTED (owner, 2026-11-22 about 13:20, in the chat, after the machine restart; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1218 (2)
- **Decision:** "every wake of a long session re-reads its whole context. Measure, per session, its context size and how it grows, what fills it, and what each wake costs; then find the cheapest wake pattern for you and the EXAMIN CTO (how often, timed to the prompt cache's lifetime, which events wake you), and how much of your own investigation should go to short Sonnet helpers. Report the figures daily from today, beside the plan's reading; bring me your proposal. No cap on your window."
- **Basis:** the owner's message of 2026-11-22; the CTO session of 19 to 20 November grew past a million cached tokens a wake.
- **Governing sources:** DEC-1218; .gov-runtime/scratch/orchestrator/log/usage.txt.

### DEC-1230 — Three comprehensive audits, read-only, on Opus, started now before Wave 2 closes: decisions carried through, the Contract in code, tools through MCP
- **Status:** ACCEPTED (owner, 2026-11-22 about 13:20, in the chat, after the machine restart; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1225 (2) (an audit the owner asks for runs on Opus)
- **Decision:** "Audit 1, decisions carried through: every decision since Emergency 2 began (DEC-1209 on, and EXAMIN's DEC-001 on). For each: is it carried into the templates, briefs, skills, role files, CLAUDE.md and AGENTS.md, the kit, the code and the Contract, in Gov OS and in EXAMIN; and what still says the old thing. Audit 2, the Contract in code: for each Contract item, is it enforced by code (deterministic), checked by code after the fact, or only an instruction an agent may skip. Include whether agents are made to read their briefs and fill the templates, or only asked to; and for each item that is only an instruction, what code would enforce it. Audit 3, tools through MCP: what Gov OS does today to adopt, pin and give an MCP tool to sessions, and what the imports feature must add. Each comes back as a table with its gaps and the fix for each, so Wave 2 closes with a strong, working release."
- **Basis:** the owner's message of 2026-11-22.
- **Governing sources:** docs/emergency-2/EMERGENCY-2.md; docs/contract/CONTRACT_v5.md; docs/DECISION_REGISTER.md.

### DEC-1231 — D1, the lite verdict stage (CAP-44.h), rides the next release after 0.1.5; 0.1.5 is not held for it
- **Status:** ACCEPTED (owner, 2026-11-22 about 13:40, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1226, DEC-1227 · **Changes:** DEC-1227 D1 ("before the release": the release after 0.1.5)
- **Decision:** "D1: the verdict stage rides in the next release, after 0.1.5, so 0.1.5 is not held for it and EXAMIN's measure starts sooner."
- **Basis:** the owner's message of 2026-11-22, answering the handover's one-line question (CTO-HANDOVER §3.3); holding 0.1.5 for a new feature ticket would delay EXAMIN's fresh 80.
- **Governing sources:** docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md; docs/emergency-2/CTO-HANDOVER.md; DEC-1226; DEC-1227.

### DEC-1232 — The owner's priority order for the rest of Wave 2; D1 and W2-207 built today on their own branches; W2-207's dispatcher and load balancer agnostic of the machine (MA-1 to MA-5); D7 with no new code; no session loads the owner's claude.ai connectors, by code, in 0.1.5; the Startup Launchpad study's licence basis
- **Status:** ACCEPTED (owner, 2026-11-22 about 14:00, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1225 to DEC-1231 · **Changes:** DEC-1227 D7 (settled: no new code); DEC-1228 (4) (the study goes on, sign-up and scans included); W2-207's KPI lines (MA-1 to MA-5 added)
- **Decision:**
  - (1) **The order:** "1. The models and effort rubric for C1, C2 and C3, enforced in code (DEC-1225). 2. Release 0.1.5, my last manual cut, then the automated release: W2-209 with the authority file on. 3. W2-81 closed successfully: the re-run READY, D1 and D3 built, the exceptions named. 4. EXAMIN's memory measure: its fresh 80 at 95 % or more. 5. EXAMIN's planning stage: its Contract first, then its WBS and waves. 6. Then EXAMIN's development, run by Gov OS, once Gov OS is adopted there and operating." Everything else only in parallel, never ahead of them; alongside, the audits' outputs assessed and acted on as each lands.
  - (2) **D1 and W2-207 start today,** each on its own branch with its lead, built and green by 2026-11-23; only their landing waits (D1 for 0.1.6; W2-207's live cut-over by day after 0.1.5).
  - (3) **W2-207:** "the dispatcher and load balancer must be agnostic of the machine they run on, well designed and scoped: on any machine they read its capacity (CPU, memory, GPU, disk) and size the work to it, so the work stays within limits here and on any machine it is hosted on later; on a machine too small to operate, they refuse with an error that says why. Test it against small and large machines." Carried as KPI lines MA-1 to MA-5 (`docs/emergency-2/briefs/LEAD-w2-207-runtime.md`), confirmed by the owner: "exactly what I asked".
  - (4) **D7:** "agreed, no new code; the tests pin the behaviour on a real adopted repository."
  - (5) **The machine first:** the embedding server back before 0.1.5 (done 2026-11-22 13:58 by `safe_restart`, no sudo); RAM held by WSL's file cache, not used (about 5 GB of 24 GB in processes).
  - (6) **Connectors:** "no Gov OS or EXAMIN session loads my claude.ai connectors (Gmail, Drive, Calendar, Docs); none of them is needed. Fix it by code, in how every session starts: each session gets only the MCP tools its role needs. It goes into 0.1.5." Carried by `disableClaudeAiConnectors: true` in the project settings (Gov OS now, the kit for EXAMIN through `gov update`) and `gov launch` starting every session with `--strict-mcp-config` and its role's MCP list (fixes-015 F1).
  - (7) **Startup Launchpad:** "I have a signed collaboration with SurgoTech that consents to our reverse engineering their service and its source code, to test how Gov OS performs with REA on that task. The agreement is confidential and is not shared; record my statement as the study's licence basis, and the study goes on, sign-up and scans included". Recorded in `~/gov-os-runs/study-startup-launchpad/records/LICENCE-BASIS.md`; it stays in parallel and takes nothing from (1).
- **Basis:** the owner's message of 2026-11-22; the incidents behind (5) and (6): the embedding servers did not come back after the machine restart (memory FTS-only, `gov update` failing `UPDATE_STORE_FAILED` in the real G3 run); audit 3 found leads starting without `--strict-mcp-config`, and `claude mcp list` showed the four connectors in every session.
- **Governing sources:** docs/emergency-2/briefs/LEAD-d1-verdict.md; docs/emergency-2/briefs/LEAD-w2-207-runtime.md; docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md; DEC-1225; DEC-1227; DEC-1228.

### DEC-1233 — The audits' text decisions (N-27, N-28, N-29, N-13, N-30, N-31, W-3 all (a)); N-07 and N-14 into 0.1.5; N-06, N-03 and N-25 first in 0.1.6; W-2 by value, no dead code; audit 4 on determinism and the determinism rule in the Charter and every Contract item; the embedders started at boot; the RAM restart after 0.1.5
- **Status:** ACCEPTED (owner, 2026-11-22 about 14:30, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1230, DEC-1232 · **Changes:** Contract v5 CAP-43, CAP-43.c, CAP-44.h, CAP-24.c, CAP-15, CAP-65.a and the AGENTS.md size limit; Charter v6 lines 36-39; EMERGENCY-2 (a dated block of changes since v3); DEC-1210 (8) (no reopen of W2-187 and W2-188)
- **Decision:**
  - (1) **The audits' text decisions** (`.gov-runtime/scratch/orchestrator/log/audits-merged-2026-11-22.md` §2), all (a): **N-27** one dated change of the Contract's and the Charter's release lines (the CTO cuts patch releases by code, DEC-1223; release acceptance item 4 moved to EXAMIN's first planned wave, DEC-1224; the verdict in the release after 0.1.5, DEC-1231); **N-28** a dated "changed since v3" block in EMERGENCY-2, the CTO writes it and the owner approves it; **N-29** CAP-24.c re-worded to the CTO's call (EMERGENCY-2 3.5, 2.10); **N-13** `gov brief` carries the whole bundle's text and drops its ceiling (code, 0.1.6); **N-30** a CAP-25 item for MCP tools at the re-baseline, beside IM-5 (c); **N-31** no reopen of W2-187 and W2-188: the weekly maintenance (EMERGENCY-2 5.9) is a chore; **W-3** the AGENTS.md size limit raised to what the golden rules at its head need.
  - (2) **Into 0.1.5:** N-07 ("so pause really stops the dispatcher and the lead starter before releases are cut on my behalf") and N-14 ("so no hit@5 floor or hard-blocking kit check is left when EXAMIN's measure runs on 0.1.5").
  - (3) **First in 0.1.6, ahead of the rest:** N-06 (leads launched from a filled brief, an unfilled slot refused), N-03 (the acceptance folder must be red on the base, or the landing refuses it), N-25 (the skills sweep, with memory first in every skill and template): "These are what make the flow deterministic."
  - (4) **W-2:** "wire or retire each piece of uncalled code by its value; keep no dead code."
  - (5) **Audit 4, determinism across the whole of Gov OS,** on Opus as a wide audit the owner asks for (DEC-1225 (2)), in parallel with the rest of the work: every command, step of the flow, role, skill, template, hook and rule classed as enforced by code, checked by code after the fact, or left to an agent's judgement; then what can become deterministic (the code, its size, its place, ordered by what it protects) and what must stay with agents (for each agent type: what it receives, what it must produce and in what form, and how code checks it). Brief `docs/emergency-2/briefs/AUDIT-4-determinism.md`.
  - (6) **The rule from now on:** "whatever can be deterministic becomes code; what cannot is specified so." It becomes part of the Contract and the Charter, so Gov OS is assessed by it: the Charter states the rule; every Contract item carries whether it is built, how it is enforced today (code, checked after the fact, or an agent's judgement), if not built why not and when, and what it should be (code, or an agent's job with its specification); audit 4's result fills these in, and the release acceptance checks them.
  - (7) **The embedding servers start at boot** until W2-207's MA-5 lands (a crontab `@reboot` line running `tools/embedders_at_boot.sh`, through `safe_restart`).
  - (8) **RAM:** after the owner cuts 0.1.5, the CTO writes its handover first; then the owner sets `autoMemoryReclaim=dropCache` in `.wslconfig` and restarts WSL, and the fresh sessions resume from the handover.
  - (9) **Startup Launchpad:** the owner does the steps that need his hand when he can; nothing waits on them.
- **Basis:** the owner's message of 2026-11-22; audits 1 to 3 of DEC-1230 (46 gaps, 7 needing the owner's text decision); the incident behind (7): the embedders stayed down after the machine restart of 2026-11-22.
- **Governing sources:** docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md; docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md; docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md; docs/emergency-2/briefs/AUDIT-4-determinism.md; DEC-1210; DEC-1223; DEC-1224; DEC-1230; DEC-1231.

### DEC-1234 — When W2-207 lands: a capacity assessment of this machine, per lead, per test run and per CTO, the first limiting resource, the leads and slots it supports, and the cheapest upgrade weighed against the usage plan
- **Status:** ACCEPTED (owner, 2026-11-22 about 14:35, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`) · **Under:** DEC-1232 (3)
- **Decision:** "when it lands, a capacity assessment of this machine. Measure, per lead, per test run and per CTO, what CPU, memory, GPU and disk each uses, and why; find which resource limits parallel work first; then tell me how many leads and test slots this machine supports, and which upgrade would raise that most for the least money (64 or 128 GB of memory, a faster CPU, the GPU, or cloud pods), weighed against the usage plan, which may be the real limit."
- **Carried by:** a per-session sampler started 2026-11-22 (`.gov-runtime/scratch/orchestrator/tools/capacity_sampler.py`, 60 s, 36 h, `log/capacity-samples.jsonl`), so the figures exist when W2-207's MA-1 reading lands; the assessment then reads both and the plan's usage log (`log/usage.txt`, DEC-1229).
- **Basis:** the owner's message of 2026-11-22.
- **Governing sources:** docs/emergency-2/briefs/LEAD-w2-207-runtime.md; DEC-1229; DEC-1232.

### DEC-1235 — Nothing ahead of 0.1.5, pushed the moment it is green; after it the CTO cuts every release whose content the owner has approved; a new feature proposed: decisions by page; the week's usage explained and brought down
- **Status:** ACCEPTED (owner, 2026-11-22 about 14:45, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing; item (3) is a request for a proposal, not yet a feature) · **Under:** DEC-1223, DEC-1226, DEC-1232 · **Changes:** DEC-1223 RB-1 (from patch releases only to every release whose content the owner has approved); EMERGENCY-2 2.5 and 8.3
- **Decision:**
  - (1) "Release 0.1.5: nothing goes ahead of it; give me its exact ready time, and push me the moment it is green."
  - (2) "After 0.1.5, so nothing waits on me but pushes and sudo: you cut every release whose content I have already approved (features I approved as P1, Contract changes I approved), only when the release acceptance passes, with the re-pin's self-rollback and a push to me each time. Pushes to GitHub and sudo stay mine." W2-209's release rule changes accordingly (a fix under W2-209 after 0.1.5): a release whose new features and Contract or Charter changes each name the owner's approving decision passes P1.
  - (3) **A new feature for the owner's yes, decisions by page:** "Every decision that needs me is a structured record (the question, what was found, the options with their costs, your recommendation, the sources). You batch them into one interactive page in the template of the decision pages I have used (a card per decision, pick an option, add a note, copy the answer sheet), published so I can answer from my phone. My answer sheet is written into the register by code. The escalation rubric routes every decision for me through it." Proposal: `docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md`.
  - (4) **Usage:** where the week's first 6 % went, per session; every session still on Opus or Fable and why; what changes now to slow it.
- **Basis:** the owner's message of 2026-11-22; the plan at 5 % at 14:30 and 6 % by 14:45 after about 80 minutes of work since the machine came back at 13:26.
- **Governing sources:** docs/emergency-2/proposals/RELEASE-ON-BEHALF.md; .gov-runtime/scratch/orchestrator/log/usage-breakdown-2026-11-22.md; DEC-1223; DEC-1226; DEC-1229.

### DEC-1236 — Decisions by page approved (DB-1 a, DB-2 c, DB-3 a, DB-4 a, DB-5 a) with the owner's page as the golden example; leads at medium effort, a change to the rubric; any change to a role's model or effort goes to the owner first
- **Status:** ACCEPTED (owner, 2026-11-22 about 15:15, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1225, DEC-1235 (3) · **Changes:** DEC-1214 K1's rubric table and DEC-1225's (ticket leads run Sonnet at medium effort, not high); DEC-220 and DEC-093's cap of five open packages (superseded by the page's batch limit, as the proposal states)
- **Decision:**
  - (1) **Decisions by page** (`docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md`, KPIs PG-1 to PG-9): **DB-1 (a)** one feature ticket in two slices, in the release after 0.1.5; **DB-2 (c)** published by the CTO's Artifact tool as a private page, the HTML file as fallback; **DB-3 (a)** a morning page, plus an immediate page for a decision that stops work, carrying every open card; **DB-4 (a)** notes only, every answer picks an option; **DB-5 (a)** one register entry per decision. **The golden example** of the page is the owner's own: `docs/emergency-2/proposals/gov-os-decisions.html` ("Gov OS decisions, 18 November"), committed as the template's reference.
  - (2) **Leads at medium effort:** "approved as a change to the rubric; record it." Ticket leads (and fix and chore leads) run Sonnet at `--effort medium`; their helpers inherit it.
  - (3) **The rule from now on:** "a change to any role's model or effort comes to me first." The CTO proposes; the owner decides; nothing changes a role's model or effort in code, settings, scripts or briefs before his yes.
- **Basis:** the owner's message of 2026-11-22; the incident behind (2) and (3): the CTO set leads to medium effort in its start script (DEC-1235 (4), usage) before asking; output at high effort was 27 % of the day's spend.
- **Governing sources:** docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md; docs/emergency-2/proposals/gov-os-decisions.html; .gov-runtime/scratch/orchestrator/log/usage-breakdown-2026-11-22.md; DEC-1225; DEC-1235.

### DEC-1237 — N-28 approved: EMERGENCY-2's dated block of changes since v3 (§13), with the owner's two added rows
- **Status:** ACCEPTED (owner, 2026-11-22 about 15:25, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1233 (1) N-28 · **Changes:** EMERGENCY-2 (§13 appended; the status line names it)
- **Decision:** "N-28 approved, with two rows added: 2026-11-19: Gov OS's golden rules and 'value first' stand at the head of every adopted repository's CLAUDE.md and AGENTS.md, carried by the kit through gov adopt and gov update. 2026-11-20 and 22: the imports feature: what a repository brings in is classed use, absorb or study and placed in memory accordingly, MCP tools among them; code reconstructed with REA is study until an absorb assessment names a commercial licence. Put the decision ids beside each, as in the other rows, then append the block in one commit."
- **Basis:** the owner's message of 2026-11-22; audit 1 (fix 7, E1): EMERGENCY-2 §2.5, §5.3, §8.2 and §8.3 said the old thing.
- **Governing sources:** docs/emergency-2/EMERGENCY-2.md §13; docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md; DEC-1233.

### DEC-1238 — Audit 4 approved as the plan (the Charter's determinism sentence, the enforcement field as a feature, the rubric over research outputs); the golden workflow, the owner's draft, to be verified and completed; the integration emergency from the 0.1.5 cut; EXAMIN's planning waits for integrated Gov OS; steps one to four and the lift; spec questions come to the owner as decision records
- **Status:** ACCEPTED (owner, 2026-11-22 about 16:50, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing; (3) takes effect when the owner cuts 0.1.5) · **Under:** DEC-1233 (5)-(6), DEC-1232 (1), DEC-1236, DEC-1237 · **Changes:** DEC-1232 (1) (EXAMIN's planning stage, the owner's priority 5, waits for integrated Gov OS); the Charter v6 principle 4 and the Contract's envelope rules (the determinism sentence, a seventh envelope rule)
- **Decision:**
  - (1) **Audit 4 is approved as the plan** (`docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md`). (a) The Charter sentence under principle 4, "Deterministic where it can be, specified where it cannot", as proposed in its §4.3, and the same as the Contract's seventh envelope rule, `determinism`: yes. (b) The enforcement field on every Contract item and new standing rule, with its G1 check and the counts in every release's acceptance record (A-23): yes, as a new feature; audit 4 read the repository before DEC-1233 to DEC-1237 were recorded, so they are added when the field is filled. (c) The rubric applies to research outputs too: the W2-81 analysis's A4 (a path classed in two namespaces) is a fix under its owning ticket, W1-41, not a new ticket.
  - (2) **The golden workflow** (`docs/emergency-2/GOLDEN-WORKFLOW.md`, the owner's draft): it extends the golden rule (the golden rule says how work is judged; this file says how work flows), in sixteen steps on ten rules, each step with what code holds and what stays with an agent, decisions included (rule 8, by the escalation rubric). The CTO verifies it against the code, corrects its "Today" column and brings any change for the owner's approval. Once approved it is the spine of Gov OS: the Charter and the Contract are rebuilt around it; every piece of information that says otherwise (roles, skills, templates, briefs, docs, the kit's head, old decisions still read as current) is brought into line or archived; the heads of CLAUDE.md and AGENTS.md point to it beside the golden rule.
  - (3) **The integration emergency:** "Gov OS has built most of its deterministic tools but runs itself around them: leads start from a script, work lands by hand merge, the checks run only when typed, and tools the work depends on live outside the product. From the moment I cut 0.1.5, Gov OS is in an integration emergency: integrating what is built and fixing the bugs that integration finds come before anything else. Nothing new starts that is not integration, except what is already in flight for 0.1.5."
  - (4) **EXAMIN in the emergency:** its memory measure on 0.1.5 and any memory fixes go on; its planning stage waits for integrated Gov OS: the planning is the first real trial of the integrated workflow.
  - (5) **Step one, the tool map:** the golden workflow's §5 completed from the code (audit 4's inventory the start), one row per tool, script, hook, cron line or schedule doing Gov OS's work, inside the product or outside it, meeting the section's five rules; the share of steps on the path today; and the answer to whether code today traces a change in a decision or a spec to the tickets, specs and tests it affects (through the graph and the path map), or only the landing's test selection does. The owner assesses the map for gaps before the plan.
  - (6) **Step two, the decisions and the rubrics:** every decision since DEC-1209, and EXAMIN's from DEC-001, marked as held by code or by text only (from audits 1 and 4); in particular the ticket rubric, the model and effort rubric by criticality, and the escalation rubric (rule 8: the level set by code from the record, a decision below its level refused, the judgement kept in a fixed form); what makes each enforced on the path, and when.
  - (7) **Step three, the plan, for the owner's yes before the work starts:** every step of the workflow on the path, in this order: every landing through `gov queue` (A-1); every lead started by `gov launch` from a filled brief (A-6, with N-06), its return checked (A-7), tests red on the base (A-3); every typed check scheduled to run by itself at its moment (at the landing, at session start, nightly, weekly), not as MCP tools, which would load into every session's context; the tools outside the product absorbed, replaced or retired, as the map says; then A-23, the forms List B names as missing, and the rest of List A. Each item a fix or a chore under its owning ticket; a new ticket only for a feature the owner has approved. The target: the flow 90 % or more held by code; every job that stays with agents has fixed inputs, a fixed output form and a code check of it.
  - (8) **Step four, the test, still in the emergency:** one scratch repository through the whole workflow, from adoption to release, under the dispatcher and the load balancer; Gov OS's own work running only on the path; W2-81's re-run as the adoption proof; context and usage measured per step, before and after.
  - (9) **The lift:** the emergency lifts when that test passes and Gov OS's own work runs only on the path; then EXAMIN's planning on the integrated workflow, then its development; its friction feeds Gov OS.
  - (10) **Spec questions during the integration come to the owner:** wherever the golden workflow, the Contract or a spec is unclear, conflicts with another, or the code does something no spec decides, the CTO does not guess; each becomes a decision record (the question, what was found, the options with their costs, the recommendation, the sources), batched in the decisions-page form, by hand until the tool exists; a question that stops work pushes the owner at once, the rest come together; work that does not depend on the answer goes on.
  - The order of the reports: steps one and two together as one report with the corrections to the golden workflow, then the plan; 0.1.5 stays first tonight.
- **Basis:** the owner's message of 2026-11-22; audit 4's finding (21 % of the live Contract items enforced on the path; most refusals built inside `gov queue` and `gov launch`, which Gov OS bypassed).
- **Governing sources:** docs/emergency-2/GOLDEN-WORKFLOW.md; docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md; docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md; docs/emergency-2/T2-ESCALATION-RUBRIC.md; DEC-1233; DEC-1236; DEC-1237.

### DEC-1239 — Emergency mode while Gov OS is developed: its own fixes land by the plain path; its tools are proven on a scratch repository and in EXAMIN; the integration's exit test changes; I-1 in 0.1.5, I-2 a record placed with a notice
- **Status:** ACCEPTED (owner, 2026-11-22 about 17:20, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1238 · **Changes:** DEC-1238 (7) (the plan's first item: Gov OS's own landings stay on the plain path; `gov queue` is proven on the scratch repository and in EXAMIN), (8) and (9) (the exit test), DEC-1233 (1)'s and audit 4's A-1 placement
- **Decision:**
  - (1) **I-1** (`gov queue`'s selection takes a test file deleted since the last green record as changed, then refuses `FILE_GONE`): "fix it in 0.1.5 if it can land before the version commit, failing test first; it costs no extra full suite and adopted repositories never meet it."
  - (2) **I-2:** "a record-only document a branch writes is placed as a record with a notice at the landing, never refused."
  - (3) **The norm while Gov OS is being developed: emergency mode.** "Gov OS is not developed through its own tools until they are integrated and proven working at a bare minimum: its own fixes land by the plain path (the change's own tests and the merged tree's suites green, a hand merge, recorded), so a broken tool never blocks the fix to itself. The tools run in full, and are proven, on a scratch repository and in EXAMIN, whose friction is the trial of how Gov OS works."
  - (4) **The integration's exit test** is the scratch repository taken through the whole workflow and EXAMIN's planning on the integrated workflow, not Gov OS's own work; Gov OS moves onto its own tools only when the owner decides it, once they are proven.
  - (5) Anything found when a tool is used goes into the findings log (`docs/emergency-2/integration/FINDINGS.md`).
- **Basis:** the owner's message of 2026-11-22; the incidents behind it: `gov queue` refused two of Gov OS's own landings on 2026-11-22 (I-1, I-2) and the fixes landed by hand merge with their suites green on the merged tree.
- **Governing sources:** docs/emergency-2/integration/FINDINGS.md; DEC-1238.

### DEC-1240 — Step four, the integration test, specified: a scratch repository from adoption to release under the dispatcher and load balancer, with test data from Gov OS's history and new tickets, ten planted cases with expected outcomes, every step judged by what it must produce
- **Status:** ACCEPTED (owner, 2026-11-22 about 17:25, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1238 (8), DEC-1239 (4) · **Changes:** DEC-1238 (8) (step four's content)
- **Decision:** "Step four, the test, still in the emergency: one scratch repository taken through the whole workflow, from adoption to release, under the dispatcher and the load balancer, with test data: tickets drawn from Gov OS's own history and new ones (features, fixes, chores, with their specs and KPIs), and planted cases an independent test designer writes, each with its expected outcome: a red landing, a merge conflict, a deleted test file, a branch with uncommitted work, a decision that needs me, a spec question, a failed memory refresh, the embedder down, a machine too small, a pause. Every step and every hand-off is checked by what it must produce (its record, its form, its effect), not only by its exit code, so a step that passes without doing its job is caught. W2-81's re-run is the adoption proof. Measure context and usage per step, before and after: integration should cut both. EXAMIN's friction then shows what is still missing or wrong."
- **Basis:** the owner's message of 2026-11-22; the incidents of the day the planted cases mirror (I-1 a deleted test, N-01 uncommitted work, I-7 the embedder down, MA-3 a machine too small, N-07 the pause).
- **Governing sources:** docs/emergency-2/GOLDEN-WORKFLOW.md; docs/emergency-2/integration/FINDINGS.md; DEC-1238; DEC-1239.

### DEC-1241 — The golden workflow decisions (21 cards, the owner's page of 23 November): the 16 corrections accepted, P-1 to P-10, G-1 to G-9, the go-ahead
- **Status:** ACCEPTED (owner, 2026-11-24 about 00:10, in the chat with his page `docs/emergency-2/integration/golden-workflow-decisions.html` committed as the record of every card's findings, the CTO's view, his and his reasoning; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1238, DEC-1239, DEC-1240 · **Changes:** the golden workflow (`docs/emergency-2/GOLDEN-WORKFLOW.md`); DEC-1217 L2-5 (the landing's name); DEC-1204 (3) in code (two rounds)
- **Decision:**
  - **C-ALL (a):** accept all 16 corrections as written; every gap they reveal becomes an item in the integration plan.
  - **P-1 (a):** name the scheduler in W15: one thing in the product runs every schedule. **P-2 (a):** the full regression runs on demand when a release needs it, and weekly in W16 as a safety net. **P-3 (a):** the orchestrators' morning handover is a step in W15, in the checkpoint form the launcher reads. **P-4 (a):** one tool column for W2 and W3. **P-5 (a):** the workflow's Today column is computed from the enforcement field, not typed. **P-6 (a):** every release prints all three measures (Contract items, steps, tools); the aim is as much in code as can be, with at least 90 % of the steps (the flow) held by code as the floor, not the ceiling. **P-7 (a):** "outside the product" is whatever `gov update` would not carry to an adopted repository (third-party programs pinned, checked and started, not shipped). **P-8 (a):** a machine too small is refused at adoption and at install too, with the reason. **P-9 (a):** name `gov close`'s retirement in W11, and two review rounds in code. **P-10 (a):** rename the landing to `gov land`, `gov queue` kept as an alias for one release; the word queue stays with the dispatcher's work queue.
  - **G-1 (a):** first in the integration plan: the memory refresh retried and checked, the store current, before anything relies on memory. **G-2 (a):** fix or retire the 72 acceptance folders that fail their test-map check (with the test-suite cuts) before landings run through the product's landing in the test. **G-3 (a):** every brief, for a ticket, a fix or any agent, is generated by code at launch from its sources (the ticket's KPIs, spec and read and write paths, its template, the path map, memory, the commands map), never written or edited by hand; a new brief is refused if a link is missing or broken; plan, brief, launch and landing all read the same ticket fields; retired commands are swept out of skills and old briefs. **G-4 (a):** the product installs the git hook, in Gov OS and through the kit. **G-5 (a):** each duplicated tool retires on the day its product tool takes over, listed in the plan with that day. **G-6 (a):** map every record end to end (templates, briefs, specs, KPIs, data), as the tool map did for tools, as part of step one, before the plan. **G-7 (a):** a separate audit and discovery of the chain from feature to code, its three approaches reported to the owner before the integration plan is final. **G-8 (a):** the path map is the one source: code proves it covers every tracked file exactly once, at every landing and in doctor; a ticket's read and write paths are checked against it when planned; `gov brief` takes each job's paths from the ticket and the map; the landing checks the same; adoption and `gov update` keep it current; it is part of the records map (G-6). **G-9 (a):** a read-only competitive analysis against open-source AI software factories, run in parallel, nothing stops for it; the full analysis comes to the owner, and the decision is his.
  - **GO (a):** record both pages' answers, start the discoveries (G-6 with G-8 and G-7 reported before the plan is final; G-9 when ready), then write the integration plan with the corrected golden workflow for the owner's yes; 0.1.5 stays first.
  - **How to act** (the owner's message): every answer recorded with its card id; the four audits and discoveries read-only, in parallel, none stopping other work, each reported in its own file and pushed to the owner with its path the moment it is ready; spec questions they raise come as decision records; the EXAMIN CTO told its priorities (its memory measure as soon as 0.1.5 is out, any memory fixes, its planning held until Gov OS is integrated); a push whenever something is ready for review.
- **Basis:** the owner's message of 2026-11-24 and his page; integration steps one and two (`TOOL-MAP.md`, `GOLDEN-WORKFLOW-CORRECTIONS.md`, `DECISIONS-HELD.md`).
- **Governing sources:** docs/emergency-2/integration/golden-workflow-decisions.html; docs/emergency-2/integration/TOOL-MAP.md; docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md; docs/emergency-2/GOLDEN-WORKFLOW.md; DEC-1238.

### DEC-1242 — The integration spec questions answered (batch B-2026-11-22-integration, 18 cards)
- **Status:** ACCEPTED (owner, 2026-11-24T00:10:58Z, the answer sheet of `docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html`, hash `sha256:d902d56c80bd385485167722ccac28dbc3f8bc938ae49cf40f59fec622a1935e`; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (page B-2026-11-22-integration)`; standing) · **Under:** DEC-1238 (10), DEC-1241
- **Decision** (each card's options and costs are on the page):
  - **T-2 (c):** records and docs commit directly; anything touching code goes through the landing's `--direct` (to be built: it does not exist at HEAD; A-16).
  - **T-3 (b):** at least one red case per KPI line; guard cases allowed when the README row marks them guard.
  - **T-6 (c):** retire what the Contract does not carry, wire what it does; the owner's note: "For what the Contract carries: wire it only if it serves a step of the golden workflow; otherwise retire it and bring me the Contract edit. gov skilleval goes (it defaults to Opus)."
  - **T-12 (b):** on a red landing the CTO decides; the landing writes the red's record in the diagnosis form (List B, B6).
  - **R-1 (b):** no time box: a chore is whatever changes no behaviour and keeps the tests unchanged and green, caught by A-16's notice.
  - **R-2 (c):** the landing refuses only a ticket that is not in the planned wave's list; the notice stays for the rest.
  - **R-3 (a):** a ticket field `kind: feature`, required by the schema, the tickets migrated by a chore (271 at HEAD on 2026-11-24; the card said 219).
  - **R-8 (b):** drop `Class: Q`; a patch requires `Fix:` or `Class: C`.
  - **T-1 (b):** rule 8's first slice: the three record fields, a computed level, the refusal below the level, `gov decisions answer`; page and push by hand meanwhile; the owner's note: "The page itself is already approved as a feature (DEC-1236); it follows as the next slice."
  - **T-10 (c):** the start scripts stay until W8 replaces them; the owner's note: "Until W8, the start scripts' models and efforts must match the rubric exactly."
  - **T-13 (b):** the handover is written in the checkpoint form (`gov checkpoint`) and the launcher reads it.
  - **R-4 (a):** today's efforts recorded as the table (CTO and senior engineer high; ticket, fix and chore leads medium; every other role high; changed only by the owner); the owner's note: "After the integration, bring me a measured trial of medium effort for engineers and test designers."
  - **R-5 (a):** criticality no longer varies the model; it keeps review depth and the profile; the rubric is "by role"; promotion and probe on Opus retire with it.
  - **R-6 (a):** a decision's level is computed from the record's stated facts (touches, reversible, inside), added to the decisions-by-page slice (a) spec.
  - **T-5 (a):** one scheduler in the product (`gov dispatch pass` by one cron line, its schedule in configuration); the owner's note: "With the kit installing the git hook, as in (b)."
  - **T-8 (b):** the full regression record made on demand (`gov release --patch` calls the full run for the commit); the owner's note: "Plus (a), the nightly as a weekly safety net, as you propose."
  - **T-9 (c):** G1, G2 and G3 run in the landing's after-step; the owner's note: "Plus (a)'s notices for G1 and G2. GitHub is only the remote I push backups to, with no CI there: retire the kit's CI and lefthook."
  - **T-11 (a):** the impact trace runs at the landing (`gov impact --changed` in the after-step, into the close record); the owner's note: "And (c) when the plan step is built."
- **Basis:** the owner's answer sheet of 2026-11-24; the spec questions of integration steps one and two.
- **Governing sources:** docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html; docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md §4; docs/emergency-2/integration/DECISIONS-HELD.md §4; DEC-1238; DEC-1241.

### DEC-1243 — Seven acceptance exemptions for fixes-015a's four engineer commits and the three merges that carry them (the freeze stays for everything else); briefs never ask an engineer to touch tests/acceptance/; P-2 first in Phase 1; a stall push after 3 hours with nothing moving
- **Status:** ACCEPTED (owner, 2026-11-24 about 10:45, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-906, DEC-1052 Q-10 (the freeze, lifted for these seven only), DEC-1239, DEC-1241 P-2 · **Changes:** `governance/project/path-map.yaml` `acceptance_exemptions` (seven entries); the integration plan (P-2 first in Phase 1; an interim stall push)
- **Decision:**
  - (1) "The seven exemption entries: (a), approved for these seven commits only, recorded as DEC-1243: 76677f4eb, dc9d10f85, 4c95fcc08, e8838fa97 and the three merges 461c214a5, 0747e362c, 8e0b222f0, citing the test designer's review in 0d01d006a. You add them; the freeze stays for everything else."
  - (2) "Briefs never ask an engineer to touch tests/acceptance/ again (I-12)."
  - (3) "A branch as broad as fixes-015a runs the full regression before it lands (P-2, first in Phase 1)."
  - (4) "The 30 hours lost to a stopped watcher is exactly the stall detector G-9 says we lack: until W2-207's run-time tool holds it, if nothing has moved for 3 hours, push me." Carried by `tools/stall_check.sh` from cron every 15 minutes: when no landing, lead return, full-suite record or test run has moved for 3 hours, it wakes the CTO's session to push the owner, once per stall.
- **Basis:** the owner's message of 2026-11-24; W1-01's red in the 0.1.5 full run (the four engineer commits, I-12); the 30 hours 0.1.5 stood still (I-13); the 95 reds of the straight-through run after fixes-015a (I-14).
- **Governing sources:** governance/project/path-map.yaml; docs/emergency-2/integration/FINDINGS.md; docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md (the stall detector); DEC-906; DEC-1052; DEC-1241.

### DEC-1244 — The integration plan decisions (22 cards, the owner's page of 24 November): golden workflow v2 the spine; the plan approved with X-1 to X-5; Q-1 to Q-14; the go-ahead at the 0.1.5 cut
- **Status:** ACCEPTED (owner, 2026-11-24 about 11:35, in the chat with his page `docs/emergency-2/integration/integration-plan-decisions-2026-11-24.html` committed as the record of each card's findings, the CTO's view, his and his reasoning; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1238, DEC-1241, DEC-1242, DEC-1243 · **Changes:** DEC-1238 (4) (X-4: EXAMIN's Contract and planning go ahead now; only executing its plan waits); DEC-1243 (3) (X-1 replaces "the full regression before a broad branch lands" with the impact-selected tests at every landing); DEC-1241 P-6's floor (Q-14: a baseline set at the exit); the owner's golden workflow draft (WF: v2 replaces it)
- **Decision:**
  - **WF (a):** the golden workflow v2 (`docs/emergency-2/integration/GOLDEN-WORKFLOW-v2.md`) is approved as the spine.
  - **PLAN (a):** the integration plan is approved, with X-1 to X-5 and the answers below.
  - **X-1 (a):** every landing, Gov OS's hand merges included, runs the tests the product's impact selection picks, never a hand-picked set; making the selection trustworthy (the path map, the code and test graph, `gov impact` at the landing) comes first in Phase 1; the full suite runs only for a release and weekly, as decided; a red the selection missed is a selection bug.
  - **X-2 (a):** the 3-hour stall push is sent by code, not by any waking agent, saying what waits and on whom; built with the scheduler in Phase 3, the CTO's own rule meanwhile; 5-15's finer thresholds stay in Phase 5.
  - **X-3 (a):** when EXAMIN's fresh 80 passes, the imports feature (already approved) joins the plan as a fourth stream, so W1 is fully on by the exit.
  - **X-4 (a):** EXAMIN's memory measure, Contract and planning (WBS, waves, tickets, in the forms this page settles) go ahead now, each for the owner's yes; only executing the plan waits for integrated Gov OS, and is its trial. (Changes DEC-1238 (4).)
  - **X-5 (a):** after the capacity assessment, run as many streams as the machine holds, within the load gate.
  - **Q-1 (a):** a new path the path map does not hold exactly once is refused at the landing, naming the exact line to add (a record-only document inside an already-mapped folder still passes with a notice, DEC-1239 (2)).
  - **Q-2 (b):** a feature ticket names its spec: required for new feature tickets, optional on old ones.
  - **Q-3 (a):** the nine-part form is the spec; OpenSpec holds the living behaviour beside it, each K-line naming its requirement (to be settled for good when EXAMIN's Contract is drafted, the owner's note on the card).
  - **Q-4 (a):** a stable id as a KPI line's first token for new feature tickets, with a fingerprint of the list to catch drift.
  - **Q-5 (a):** a ticket's KPI line is a word-for-word copy of the spec's line, with code named only in its verify field.
  - **Q-6 (a):** `gov accept` fails a ticket line no map row names, for tickets created from the change on; older ones exempt.
  - **Q-7 (c):** the same failure three times stops the loop; the CTO finds the root cause (brief, spec or KPIs, path map, test, environment or tool), fixes it at the root, and records it in the findings log.
  - **Q-8 (a):** only the owner's Claude Code plan now; API keys and other subscription plans become a Wave 3 feature, built and trialled then, each paid service approved by the owner.
  - **Q-9 (a):** a step held by an engine's graph counts only if the engine is pinned and its behaviour checked by Gov OS's own test.
  - **Q-10 (a):** one vendor now; review by a second vendor becomes a Wave 3 feature, built and trialled with Q-8's keys and plans.
  - **Q-11 (b):** state "all rights reserved" in a file, in Gov OS and the kit (a chore).
  - **Q-12 (a):** approach A, derive and check, with each acceptance test carrying its KPI line's id in code and the README map generated from those markers, never hand-written; in slices, tried first on the scratch repository and EXAMIN; B's stub generation considered as a later slice.
  - **Q-13 (a):** finish the integration and build the five small pieces they do better; look again only if the scratch test shows a workflow Gov OS's tools cannot express.
  - **Q-14 (a):** print only until the exit; at the exit the owner sets the baseline X % from what was reached; from then a release below X % stops for his decision: an exemption with its reason, or a new X.
  - **GO (a):** record these, finalise the plan and v2 with them, and start Phase 0 the moment 0.1.5 is cut, with the WSL restart and the fresh CTO session after the handover; push the owner at each phase end with the three measures.
  - **EXAMIN's order** (the owner's message): its fresh 80 as soon as 0.1.5 is out; then its Contract and its planning, each for the owner's yes; only executing the plan waits.
- **Basis:** the owner's message of 2026-11-24 and his page; the week's incidents behind X-1 (fixes-015a tested on a hand-picked set, I-14) and X-2 (0.1.5 still for 30 hours, I-13).
- **Governing sources:** docs/emergency-2/integration/integration-plan-decisions-2026-11-24.html; docs/emergency-2/integration/INTEGRATION-PLAN.md; docs/emergency-2/integration/GOLDEN-WORKFLOW-v2.md; DEC-1238; DEC-1243.

### DEC-1245 — Practice first, code catches up: every repository works by the golden workflow v2 as written practice, products use only the tools proven in real use (a tool status list per release); memory first in every repository; EXAMIN executes on the green tools; ASMO OS and UPIM adopt now; six proposals for one decisions page
- **Status:** ACCEPTED (owner, 2026-11-24 about 15:25, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1239, DEC-1244 · **Changes:** DEC-1244 X-4 (EXAMIN's execution no longer waits for integrated Gov OS: it starts on the green tools with the golden workflow once its Contract and planning have the owner's yes); DEC-1239 (3) for products (the emergency norm holds for Gov OS itself until its tools are proven; no product waits for Gov OS)
- **Decision:**
  - (1) **Practice first, code catches up.** "From now, every repository works by the golden workflow v2 as written practice: its rules in CLAUDE.md and AGENTS.md and in every brief. Products use only the Gov OS tools proven in real use." Each release ships a **tool status list**, set by the CTO from the tool map and the findings: **green** (proven, use now; the owner expects memory and its measure, `gov adopt`, `gov update`, `gov doctor`, `gov accept`, the kit's settings), **amber** (standby: products do that step by hand as the workflow says, the plain path; he expects the landing, `gov launch`, `gov brief`, `gov impact`, the dispatcher), and **not yet in the product** (a documented equivalent meanwhile, such as a cron line for the memory refresh and the weekly measure). A tool moves from amber to green only once the integration has proven it on the scratch repository; products then gain it through `gov update`. Gov OS's integration, Wave 2's close and Wave 3 go on as planned, and the emergency norm still holds for Gov OS itself until its tools are proven; "but no product waits for Gov OS any more: each new release helps it."
  - (2) **Memory first, in every repository:** refreshed after every merge with a retry, the embedder started at boot and brought back, and the weekly measure scheduled, for Gov OS and every adopted repository through the release. Phase 0 delivers this, and it ships in the first patch release after 0.1.5.
  - (3) **The repositories.** Gov OS: the integration plan, Wave 2's close, lifting the emergency, then Wave 3 on its own tools. EXAMIN: its fresh 80 on 0.1.5, its Contract, the golden workflow for its operations, its planning, each for the owner's yes; then execution starts on the green tools with the golden workflow, without waiting for integration. ASMO OS and UPIM: adopt both now, on the current release and its green tools: memory, their Contracts, the golden workflow, then their work; the CTO tells the owner where their repositories are, how their CTOs run, and their usage after a few days.
  - (4) **Six proposals, one decisions page** in the form of the owner's last two: the tool status list (with each tool's reason); friction from the repositories (one findings log in a fixed form in each repository, collected by code into Gov OS's daily, a stopper pushing at once, each kind routed: a bug in a green tool, silent ones included, a fix in the next patch release; a workflow gap a change for the owner's yes; hand-step pain ordering which amber tool is proven first; a missing capability a Wave 3 candidate; status written back); old work under new releases (every ticket and record carries its release; closed work accepted as is; new rules apply to work created after them; a reopened ticket moves to the current forms; a rule that stops lost work or a fail-open applies at once; `gov update` never rewrites history; doctor shows earlier forms as a notice); decisions (a rubric for what is recorded as a decision and what is not; every decision names the paths, specs or steps it affects; one code holds is marked so and leaves agents' reading; how many are in force today); the rubrics register (every decided rubric with its decisions and enforcement field); data in specs (every spec and KPI line declares its data need: none, synthetic, imported or real, with its path and an imported source's licence class; the ready check red when the data is missing; the test designer builds on it).
  - 0.1.5 stays first; a push when it is green.
- **Basis:** the owner's message of 2026-11-24; the week's evidence that products waited on Gov OS's integration (EXAMIN idle for its planning) while the green tools (memory, adoption, update, doctor, accept) already worked.
- **Governing sources:** docs/emergency-2/GOLDEN-WORKFLOW.md; docs/emergency-2/integration/TOOL-MAP.md; docs/emergency-2/integration/FINDINGS.md; docs/emergency-2/integration/INTEGRATION-PLAN.md; DEC-1239; DEC-1244.

### DEC-1246 — ASMO OS (with UPIM inside it) is one product with one CTO, started at the 0.1.5 cut; the solar app a trial workflow; the machine-wide dispatcher and gate, models and effort by role with criticality and escalation in code, and usage per repository in one release before ASMO OS's development
- **Status:** ACCEPTED (owner, 2026-11-24 about 15:50, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1225, DEC-1229, DEC-1232 (3), DEC-1242 T-1, DEC-1245
- **Decision:**
  - (1) "ASMO OS and UPIM: one repository, /home/usain/ASMO-OS-V1. UPIM lives inside it as ASMO OS's new compiler (UPIM-SPEC), so one product and one CTO. /home/usain/workspace/ASMO is the solar app built earlier, an example of what ASMO OS can be used for: treat it as the first trial workflow to mimic and test on ASMO OS, and propose how (studied from ASMO OS, or adopted on its own)."
  - (2) "Start the ASMO OS CTO as you proposed, the moment I cut 0.1.5: Opus, its own tmux session with Remote Control, from a brief: adopt on the green tools, memory built and measured, its Contract, the golden workflow in its practice, each for my yes."
  - (3) Into code now, in one release with the other priorities, before ASMO OS starts its development (its adoption, memory and Contract go ahead meanwhile): (a) the dispatcher and load balancer (W2-207) working well on this machine and shared by every repository: one machine-wide gate over every repository's sessions, leads, test slots and GPU work, so three repositories under development never overwhelm the machine; work waits for a slot instead of starting; capacity read, never assumed (MA-1 to MA-5); (b) models and effort by role, criticality and escalation held by code in every repository through the kit: every session's model and effort set by its role from the rubric table, never by a start script or by hand; criticality setting review depth; the escalation rubric's levels computed from each decision's record (its first slice), so a decision below its level is refused; (c) usage and context measured per repository, per role and per session, daily, beside the plan's reading, so the owner sees what each repository costs and can decide whether one needs its own plan subscription.
- **Basis:** the owner's message of 2026-11-24; three repositories under development at once (Gov OS, EXAMIN, ASMO OS) on one machine and one plan.
- **Governing sources:** docs/emergency-2/integration/INTEGRATION-PLAN.md; .tickets/DAEO-rt4s.md (W2-207); DEC-1225; DEC-1229; DEC-1245.

### DEC-1247 — W2-207's machine-wide gate keeps 2 GB free below WSL's 24 GB cap and reads Windows' own free memory, holding new work when Windows runs low (MA-6)
- **Status:** ACCEPTED (owner, 2026-11-24 about 17:25, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1232 (3), DEC-1246 (3)(a) · **Changes:** W2-207's KPI lines (MA-6 added to `docs/emergency-2/briefs/LEAD-w2-207-runtime.md`; W2-207 is held, not closed, so the line joins its ticket)
- **Decision:** "For W2-207's machine-wide gate: keep a margin of free memory below WSL's 24 GB cap (2 GB), so WSL never reaches it; and read Windows' own free memory too (WSL can query it), holding new work when Windows runs low, since its apps share the same 32 GB."
- **The CTO's calls inside it (P2, reversible, in the ticket's config):** the Windows floor defaults to 2 GB; a failed or timed-out Windows reading on WSL holds new work with a named reason, never admits blind; held work waits for a slot and running work is never stopped; off WSL the check is skipped and named. Checked feasible at 17:25: `powershell.exe` over `Win32_OperatingSystem` answers in 0.6 s (Windows then had 4.8 GB free of 31.8 GB, with WSL using 3 GB and holding 11 GB of cache).
- **Basis:** the owner's message of 2026-11-24; one 32 GB machine shared by Windows' apps and a 24 GB WSL running three repositories' work (DEC-1246 (3)(a)).
- **Governing sources:** docs/emergency-2/briefs/LEAD-w2-207-runtime.md; DEC-1232; DEC-1234; DEC-1246.

### DEC-1248 — EXAMIN's measure fixed at the root (each writer's questions form-checked by code before its session ends; round 2 gets the pre-flight refusals), cut as its own patch release 0.1.6 by code; the bundle planned for 0.1.6 becomes 0.1.7; D3 on its own in 0.1.7; ASMO OS's kit findings with I-16
- **Status:** ACCEPTED (owner, 2026-11-24 about 19:15 and 19:40, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1223, DEC-1227 D3, DEC-1235 (2), DEC-1244 Q-7, DEC-1245, DEC-1246 (3) · **Changes:** DEC-1245 (2) and DEC-1246 (3) (their "0.1.6" is now 0.1.7); DEC-1228 (1) (D3's route no longer waits for the imports feature)
- **Decision:**
  - (1) "EXAMIN's measure is blocked: four void attempts, all at writing. Fix it at the root (Q-7): every writer's questions are form-checked by code before its session ends, with any refused question returned to it to fix, and the round-2 writer and checker get the pre-flight refusals (I-23). Start that lead the moment phase0-memory returns; it comes before anything else on gov memaudit. Do not wait for 0.1.6: cut it as its own patch release ... by code under the authority file, as soon as it is green, push me, and tell the EXAMIN CTO to run gov update and measure."
  - (2) The number: "The patch release is 0.1.6; the bundle planned for 0.1.6 becomes 0.1.7." (The release code takes strict semver only, so 0.1.5.1 was refused.)
  - (3) "Build the route that keeps stale and superseded documents out of default memory (D3) now, on its own, in 0.1.6 [now 0.1.7], not waiting for the imports feature." After the EXAMIN CTO's correction (its two visible-half misses were not stale citations): "keep D3 for W2-81, and I-26 and I-27 wait for the measure."
  - (4) "From ASMO OS's adoption: the kit puts its generated block at the end of CLAUDE.md and AGENTS.md, not the head, still says gov queue lands tickets and does not point to the golden workflow v2; and there is no guide for adopting an existing repository. Log both and fix them with I-16" (I-24, I-25; in 0.1.7).
- **The CTO's calls inside it (P2):** the patch takes fixes and chores only, so the features already green (W2-210) land after its cut; the memaudit lead started at 19:10 was stopped and restarts on the owner's spec when the Phase 0 lead returns.
- **Basis:** the owner's messages of 2026-11-24; EXAMIN's void attempts (I-18, I-23, EF-9), the release code's semver check (`src/gov/release/__init__.py:40`), ASMO OS's adoption.
- **Governing sources:** docs/emergency-2/integration/FINDINGS.md; docs/emergency-2/briefs/LEAD-fix-memaudit.md; docs/emergency-2/briefs/LEAD-d3-stale-route.md; DEC-1227; DEC-1244; DEC-1245; DEC-1246.

### DEC-1249 — Memory first by construction, per role (bundle profiles; never cut a result; every return lists its retrieves); every hidden sets root refused by code to every session that is not the measure's own; the wake-cost proposal and Gov OS's fresh 80 dated
- **Status:** ACCEPTED (owner, 2026-11-24 about 21:30, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1210, DEC-1229, DEC-1241 G-3, DEC-1244, EMERGENCY-2 §2.7, §5.4 · **Changes:** EMERGENCY-2 §2.1-2.2 ("no guard") for the hidden sets roots only: a refusal by code, as the owner orders
- **Decision:**
  - (1) "Memory first, in practice, and by construction per role. Until gov brief is green, paste each lead's memory bundle into its brief, uncut, as you proposed. Once gov brief generates briefs, it carries the bundle the role needs, uncut: decisions, history and plans for the CTO, senior engineers, spec writers and planners; code locations, conventions and earlier fixes and findings for engineers; the spec, KPIs and existing test patterns for test designers; similar past failures and their root causes for a reviewer on a red. Apply the same profiles when you paste bundles by hand meanwhile. Agents may search more. Add to LEAD-COMMON and every brief: never cut a gov retrieve result with head or any pipe. Every return lists its gov retrieve calls (count and queries) and the records it used, so we can measure whether memory reduces reds and fix loops; report the counts per lead in your status."
  - (2) "The D3 lead read /home/usain/examin-eval: that is EXAMIN's hidden question-set root, which no session but the measure's own may open. Treat it as a stopper finding: what exactly was read, whether it touches any set the next measure will use, and tell the EXAMIN CTO. Then make it impossible by code: every sets root refused to every session that is not the measure's own, in Gov OS and through the kit." (I-28: one file, the root's path map, loaded by a glob; no content reached the transcript; no set the next measure uses; the EXAMIN CTO told and confirmed.)
  - (3) "Agreed: the wake-cost proposal tomorrow, and Gov OS's own fresh 80 right after 0.1.6 is pinned."
- **The CTO's calls inside it (P2):** interim deny lines for both sets roots (`/home/usain/examin-eval`, `/home/usain/gov-os-eval`) in Gov OS's project settings at once; the code fix by a lead (a registry of sets roots, roots outside any ordinary glob, a refusal for every non-measure session in Gov OS and the kit), each root moved only with its repository CTO's yes.
- **Basis:** the owner's message of 2026-11-24; I-28; today's count of retrieves (24 by six finished leads, four of them none; 14 cut with `head`).
- **Governing sources:** docs/emergency-2/integration/FINDINGS.md; docs/emergency-2/briefs/LEAD-COMMON.md; DEC-1210; DEC-1229; DEC-1241.

### DEC-1250 — The patch release that replaces the burned 0.1.6 is 0.1.7; the bundle planned as 0.1.7 becomes 0.1.8
- **Status:** ACCEPTED (owner, 2026-11-25 about 12:05, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1248 · **Changes:** DEC-1248 (2) (the bundle's number: 0.1.8); DEC-1245 (2) and DEC-1246 (3)'s release (0.1.8)
- **Decision:** "Yes no problem: call the patch 0.1.7, and the bundle we'd planned as 0.1.7 becomes 0.1.8."
- **Basis:** 0.1.6 was cut (record `deeeb8b1d`, tag `v0.1.6`) but its re-pin rolled back on a `gov doctor` probe that ran out of its shared time budget (I-31); the release code then burns the version and takes only a new one for the same content.
- **Governing sources:** docs/emergency-2/integration/FINDINGS.md (I-31); DEC-1248.

### DEC-1251 — The decisions page of 25 November (B-2026-11-25-cto, 8 cards): the owner re-pins 0.1.7 by hand, then releases by code again (I-34, W2-209 settled); timing tests fixed, serial meanwhile; the wall template approved by the owner; no heartbeat and a fresh CTO each morning; no separate plan; every practice-first recommendation; EXAMIN's and ASMO OS's cards answered with their CTOs
- **Status:** ACCEPTED (owner, 2026-11-25T21:55:15Z, the answer sheet of `docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html`, hash `sha256:28e6ddabf3aab90e676d1008326acfee640b3bbc18f0bee5fb16f1c379457628`, stored as `docs/emergency-2/integration/ANSWERS-B-2026-11-25-cto.txt`; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (page B-2026-11-25-cto)`; standing) · **Under:** DEC-1229, DEC-1235 (2), DEC-1245 (4), DEC-1246 (3)(c), DEC-1248, DEC-1249, DEC-1250 · **Changes:** DEC-1250 (no 0.1.8 patch now: 0.1.7 is re-pinned by the owner's hand; the bundle keeps the number 0.1.8); the CTO's watcher (no heartbeat)
- **Decision** (each card's findings, options and costs are on the page):
  - **D-01 (a):** the owner re-pins 0.1.7 by hand with `docs/emergency-2/release-0.1.7/repin.sh`; the owner's note: "Then make releases by code again: build the rule for approved bigger releases (I-34), and settle W2-209 so a fix like RP-1 can ride a patch." And: "tell me when to run the 0.1.7 re-pin, and commit nothing while it runs."
  - **D-03 (a):** the timing tests measured against the machine's reading; the owner's note: "Use (b) to carry the next release until (a) lands" (the timing cases run alone in the serial phase meanwhile).
  - **D-02 (a):** the owner adds the wall template's sha256 to `APPROVED` himself; "Give me the exact command line to paste."
  - **D-04 (a):** no heartbeat in the CTO's watcher; event wakes and the 3-hour stall push stay; investigations of more than a few reads go to a Sonnet helper; the owner's note: "And a fresh CTO session every morning (rule 10), once I approve the handover method."
  - **D-05 (a):** no separate plan subscription now; read again at the reset with `gov usage`'s daily figures.
  - **D-06 (b):** every recommendation on the practice-first page (DEC-1252).
  - **D-07 (a):** EXAMIN's 27 cards are answered with the EXAMIN CTO, on its pages.
  - **D-08 (a):** ASMO OS's two questions before A6 are answered in the ASMO OS CTO's chat.
- **Basis:** the owner's answer sheet of 2026-11-25; the account of 23 to 25 November (`docs/emergency-2/integration/ACCOUNT-2026-11-25.md`); FINDINGS I-30 to I-34.
- **Governing sources:** docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html; docs/emergency-2/integration/ANSWERS-B-2026-11-25-cto.txt; docs/emergency-2/integration/FINDINGS.md; DEC-1250.

### DEC-1252 — The practice-first decisions (B-2026-11-24-practice, 31 cards): every recommendation, by the owner's D-06 (b)
- **Status:** ACCEPTED (owner, 2026-11-25T21:55:15Z, card D-06 (b) of B-2026-11-25-cto: "every recommendation on the practice-first page, all 31 cards, including gov findings collect and the one pass classing the 162 older decisions"; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (page B-2026-11-25-cto, D-06)`; standing) · **Under:** DEC-1245 (4), DEC-1251
- **Decision** (each card's findings, options and costs are on `docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html`; the proposals are `docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md`): **TL-0 (a)**; **TL-1 (a)**; **TL-2 (a)**; **TL-3 (a)**; **TL-4 (a)**; **TL-5 (a)**; **TL-6 (a)**; **TL-7 (a)**; **TL-8 (a)**; **TL-9 (a)**; **TL-10 (a)**; **TL-11 (a)**; **FR-0 (a)**; **FR-1 (a)**; **FR-2 (b)**; **FR-3 (a)**; **OW-0 (a)**; **OW-1 (a)**; **OW-2 (a)**; **OW-3 (a)**; **DE-0 (a)**; **DE-1 (a)**; **DE-2 (a)**; **RG-0 (a)**; **RG-1 (a)**; **RG-2 (a)**; **DS-0 (a)**; **DS-1 (a)**; **DS-2 (a)**; **DS-3 (a)**; **DS-4 (a)**. In short: the tool status list as drafted, with its rules and where it ships; the findings log in each repository with `gov findings collect` and `gov findings sync` (a new feature, approved), a stopper pushed at once; every record carries its release, closed work never re-checked, a rule marked `Applies: at once` by the CTO; the decision rubric with `Affects:` and `Enforced-by:`, and one Sonnet research pass classing the 162 older decisions in HELD's key; the rubrics register (`docs/RUBRICS.md` and its kit copy, binding rows only); data declared in the spec's test-data table with `serves` and `path`, `real` rows naming an owner decision, an unlicensed import red for test data, old specs a notice.
- **Basis:** the owner's answer of 2026-11-25 (D-06 (b)).
- **Governing sources:** docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html; docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md; DEC-1245; DEC-1251.

### DEC-1253 — The CTO's handover method: a current role card read every morning, one tracked start script, the handover recorded as a checkpoint, the takeover checks and message before the outgoing CTO stops; a fresh CTO every morning, the same for EXAMIN and ASMO OS from 26 November
- **Status:** ACCEPTED (owner, 2026-11-25 about 22:40, in the chat; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1241 P-3, DEC-1242 T-13, DEC-1251 D-04 · **Changes:** the CTO's start (the start script reads the role card); the role card `template/governance/kernel/templates/role-cto.md` (2.0.0)
- **Decision:** "Your handover method is approved, with one change: from the integration plan, the fresh CTO reads its current and next phase whole each morning, not the whole plan; the rest on demand. Rewrite the role card and cut orchestrator.md's stale lines as you propose; one tracked start script; the handover with its checkpoint record; the takeover checks and the takeover message before you stop. The same method for the EXAMIN and ASMO OS CTOs from tomorrow. Then write the handover and start the fresh session tonight." Also, the owner: "RE-PIN DONE for 0.1.7 (pin-3d039a8fb6d3 live, registry entry c1e81afd3). D-02: the line is added to APPROVED, with two spaces after the hash to match its existing lines, and the file is read-only again; confirm the launcher accepts it when Gov OS's measure starts."
- **The method:** the fresh CTO reads, whole and never cut: CLAUDE.md, the role card, GOLDEN-WORKFLOW.md, EMERGENCY-2.md with §13, the handover and the decisions it names, the integration plan's current and next phase, FINDINGS.md, the latest decisions page with its answers; then memory for its first action. It takes over by eight checks (the checkpoint's hash, HEAD, the live gov, tmux, the tracked watcher with no heartbeat, everything listed as running, the inbox, its ids written) and one takeover message to the owner; the outgoing CTO stops only after it. Start: `governance/project/orchestration/tools/start_cto.sh` (the one script). Record: `gov checkpoint --ticket DAEO-sdxk --trigger stop --next ... --input docs/emergency-2/CTO-HANDOVER.md`.
- **Basis:** the owner's message of 2026-11-25; the role prompt read by no CTO in the emergency and stale (the guard, the sandbox, retired commands); the CTO session's context at 668k tokens, its largest cost.
- **Governing sources:** template/governance/kernel/templates/role-cto.md; governance/project/orchestration/tools/start_cto.sh; docs/emergency-2/GOLDEN-WORKFLOW.md rule 10; DEC-1241; DEC-1242; DEC-1251.

### DEC-1254 — The decisions page of 26 November (B-2026-11-26-cto, 4 cards): the two exemptions (W1-01, merge 53808ef6d and six batch B commits) with the root fix by code at commit time; D3's amended SR-3 and SR-4 as a stopgap; 0.1.8 is batch A, batch B is 0.1.9
- **Status:** ACCEPTED (owner, 2026-11-26T11:10:48Z, the answer sheet of `docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html`, hash `sha256:308d30c9c7e1c553ed91ebd50749db55b423af63efe2af5899ca95ae0204301e` (checked against the page by the CTO), stored as `docs/emergency-2/integration/ANSWERS-B-2026-11-26-cto.txt`; the exemptions committed by the owner as `66a6bae1a` and `dd88e06e0`; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (page B-2026-11-26-cto)`; standing) · **Under:** DEC-253, DEC-1052, DEC-1123, DEC-1248 (3), DEC-1249, DEC-1250, DEC-1251 · **Changes:** DEC-1052 Q-10 (the frozen exemption list takes seven more entries, by the owner's own commits); EMERGENCY-2 §2.1-2.2 ("no guard") for one case: a commit touching `tests/acceptance/` without the test designer's role is refused by code at commit time
- **Decision** (each card's findings, options and costs are on the page):
  - **E-01 (a):** merge `53808ef6d` exempted from W1-01's history case (the owner's commit `66a6bae1a`). The owner's note: "Root fix, since this is the fourth time (I-12, DEC-1243, now E-01 and E-04): refuse by code, at commit time, any commit that touches tests/acceptance/ without the test designer's role, so it can never reach a landing again."
  - **E-02 (a):** D3's amended SR-3 and SR-4 (A3 refuses only a namespace stale as a whole; a mixed one gets a notice naming the paths to move). The owner's note: "As a stopgap only; the real fix is item 2 below [DEC-1255]. Also confirm EXAMIN's three stale citations leave default memory under the amended rule; if they sit in mixed namespaces, the EXAMIN CTO moves them into a namespace of their own before it measures again."
  - **E-03 (a):** 0.1.8 is batch A with what landed on 25 and 26 November, built by the owner's hand once its release suite is green; batch B becomes 0.1.9, cut by code under the release rule.
  - **E-04 (a):** six batch B commits exempted (the owner's commit `dd88e06e0`); the note: "The same root fix as E-01."
- **The CTO's calls inside it (P2):** the root fix is a fix under W2-115b (`DAEO-j9z6`, the test-authorship check) and the kit (W2-208), by the owner's order: a commit-time refusal in Gov OS and in every adopted repository through the kit, a merge judged by its own resolution, proven in a real commit before it lands; it rides batch B (0.1.9), since the kit's hook installs are on that branch.
- **Basis:** the owner's answer sheet of 2026-11-26; FINDINGS I-12, I-15, I-40; DEC-1243 (2); the bundle-a-reds and bundle-b leads' returns.
- **Governing sources:** docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html; docs/emergency-2/integration/ANSWERS-B-2026-11-26-cto.txt; docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md; DEC-1248; DEC-1249.

### DEC-1255 — A standard repository layout and classification by rubric (a new feature, W2-213), with the classification rubric designed first by an audit session and brought to the owner as a decisions page
- **Status:** ACCEPTED (owner, 2026-11-26 about 11:15, in the chat with the answer sheet of B-2026-11-26-cto, items 2 and 3; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (chat)`; standing) · **Under:** DEC-1222, DEC-1228, DEC-1233 (6), DEC-1244, DEC-1245, DEC-1252 (RG-0 to RG-2), DEC-1254 E-02
- **Decision:**
  - (2) "A new feature ticket, approved now: a standard repository layout and classification by rubric, so the path map follows a standard instead of guessing staleness from words in paths. Guessing needs a new exception every time; a standard does not." The standard, in the kit: where code, tests, specs (`docs/specs`), research (`docs/research`), governance, everything stale (one `archive/` folder) and everything a repository brings in (`imports/<name>/`) live, with the path map's namespaces and classes fixed by it. A repository we own and develop (EXAMIN, ASMO OS) is restructured to the standard at adoption's A6, with the owner's yes on the moves; its path map then follows the standard. A new repository starts in the standard: `gov init` (I-25). An imported tool or code (REA, Startup Launchpad, a library) is never restructured: it sits whole in `imports/<name>/` with one class (use, absorb or study). Gov OS itself keeps its classing until restructuring it pays, since its tests pin its paths. How it works: the rubric becomes code (its classes, its rules and where each class lives); the judgement is an agent's, classing each file, folder and piece of material in a fixed output form (path, class, destination, reason); the repository is split into disjoint chunks by path, so up to ten agents (within the machine's gate) class it in parallel; code merges and checks their answers (every tracked file classed exactly once, every class valid, every destination where the standard puts that class; a gap, a double or a conflict goes back to its agent); the orchestrator reviews the merged classification and the restructuring plan (each move, each namespace, what memory will hold) and brings the owner the moves of a repository we own for his yes; code executes the approved plan (the moves, the path map regenerated from the standard, memory rebuilt, the impact-selected tests run, a rollback if anything breaks). The same flow serves every stage: adoption, an import, installing a tool, testing a tool before use, retiring. "File it under the right owner and give me its place in the releases; it does not hold 0.1.8."
  - (3) "Before that ticket's spec: the classification rubric, designed first. Launch a design and audit session for it, on the model the rubric sets for an audit I ask for." It reviews the real kinds (a developed product such as EXAMIN, a light repository such as ASMO OS, a fresh one, an imported tool or library, code reconstructed with REA, data sets, vendored and generated files, archives, hidden evaluation sets, secrets) and every action (adoption, importing, installing a tool, testing a tool before use, retiring); for each kind and action it proposes how material is classed, where it lives in the standard, how memory treats it, what moves and what never moves, and what needs the owner's yes; it comes back as a rubric for his yes in the form of his decisions pages, before the ticket's spec is written; the rubric then joins the rubrics register.
- **The CTO's calls inside it (P2):** the ticket is W2-213 (`.tickets/DAEO-stdl.md`, `kind: feature`, `approved_by: DEC-1255`), the integration plan's F-5; the audit session runs Opus at high effort (rule 7's one exception: a wide audit the owner asks for), read-only except its output; its place in the releases: after the rubric's yes, the spec, then the build, at the earliest in the release after 0.1.9.
- **Basis:** the owner's message of 2026-11-26; I-40 (D3's guessing from words in paths), I-25, I-43; the imports feature (DEC-1222, DEC-1228).
- **Governing sources:** docs/emergency-2/integration/ANSWERS-B-2026-11-26-cto.txt; .tickets/DAEO-stdl.md; docs/emergency-2/integration/PRACTICE-FIRST-PLAN.md (RG-0 to RG-2); DEC-1254.

| Version | Date | Change |
|---|---|---|
| 0.450 | 2026-11-03 | Owner (recorded by the orchestrator, DEC-861): DEC-1066. Next free id: DEC-1067. |
| 0.451 | 2026-11-04 | Owner (recorded by the orchestrator, DEC-861): DEC-1067. Next free id: DEC-1068. |
| 0.452 | 2026-11-04 | Owner (recorded by the orchestrator, DEC-861): DEC-1068. Next free id: DEC-1069. |
| 0.453 | 2026-11-04 | Owner (recorded by the orchestrator, DEC-861): DEC-1069. Next free id: DEC-1070. |
| 0.454 | 2026-11-04 | Owner (recorded by the orchestrator, DEC-861): DEC-1070; DEC-1069 (12)-(13) amended. Next free id: DEC-1071. |
| 0.455 | 2026-11-04 | Owner (recorded by the orchestrator, DEC-861): DEC-1071; DEC-1070 amended. Next free id: DEC-1072. |
| 0.456 | 2026-11-04 | Owner (recorded by the orchestrator, DEC-861): DEC-1072. Next free id: DEC-1073. |
| 0.457 | 2026-11-04 | Owner (recorded by the orchestrator, DEC-861): DEC-1073. Next free id: DEC-1074. |
| 0.458 | 2026-11-05 | Owner (recorded by the orchestrator, DEC-861): DEC-1074; DEC-1071 (3) and DEC-1070 (2)-(4) changed. Next free id: DEC-1075. |
| 0.459 | 2026-11-05 | Owner (recorded by the orchestrator, DEC-861): DEC-1075. Next free id: DEC-1076. |
| 0.460 | 2026-11-05 | Owner (recorded by the orchestrator, DEC-861): DEC-1076; DEC-1074 (3), DEC-1075 (1) and DEC-1069 (12) changed. Next free id: DEC-1077. |
| 0.461 | 2026-11-05 | Owner (recorded by the orchestrator, DEC-861): DEC-1077. Next free id: DEC-1078. |
| 0.462 | 2026-11-05 | Owner (recorded by the orchestrator, DEC-861): DEC-1078. Next free id: DEC-1079. |
| 0.463 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1079. Next free id: DEC-1080. |
| 0.464 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1080. Next free id: DEC-1081. |
| 0.465 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1081; DEC-1080 (2) and DEC-1079 (a) changed. Next free id: DEC-1082. |
| 0.466 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1082; DEC-1080 changed. Next free id: DEC-1083. |
| 0.467 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1083. Next free id: DEC-1084. |
| 0.468 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1084; DEC-1083 (7) changed. Next free id: DEC-1085. |
| 0.469 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1085. Next free id: DEC-1086. |
| 0.470 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1086. Next free id: DEC-1087. |
| 0.471 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1087; DEC-1083/DEC-1084 (W2-33's layers to Wave 3) and DEC-1074 (7) O1 (A) changed. Next free id: DEC-1088. |
| 0.472 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1088 (item 6 standing); DEC-936 item 3.4 changed. Next free id: DEC-1089. |
| 0.473 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1089 (item 3 standing); DEC-942 item 6 and DEC-941 item 3 changed. Next free id: DEC-1090. |
| 0.474 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1090; W2-137 and W2-138 filed; DEC-1067 (f) to change by W2-137. Next free id: DEC-1091. |
| 0.475 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1091 (items 1 and 2 standing for the experiments); DEC-1086 C changed. Next free id: DEC-1092. |
| 0.476 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1092. Next free id: DEC-1093. |
| 0.477 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1093; W2-139, W2-140 and W2-141 filed. Next free id: DEC-1094. |
| 0.478 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1094; W2-142 filed; W2-128 gains one KPI line. Next free id: DEC-1095. |
| 0.479 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1095. Next free id: DEC-1096. |
| 0.480 | 2026-11-07 | Owner (recorded by the orchestrator, DEC-861): DEC-1096. Next free id: DEC-1097. |
| 0.481 | 2026-11-08 | Owner (recorded by the orchestrator, DEC-861): DEC-1097 (item 6 open; the DECIDED-NOT-DONE line standing). Next free id: DEC-1098. |
| 0.482 | 2026-11-08 | Owner (recorded by the orchestrator, DEC-861): DEC-1097 item (6) decided (b). Next free id: DEC-1098. |
| 0.483 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1098 (item 1 standing). Next free id: DEC-1099. |
| 0.484 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1099. Next free id: DEC-1100. |
| 0.485 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1100. Next free id: DEC-1101. |
| 0.486 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1101 (items 1 and 2 standing). Next free id: DEC-1102. |
| 0.487 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1102. Next free id: DEC-1103. |
| 0.488 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1103; DEC-1061 amended for ten cases. Next free id: DEC-1104. |
| 0.489 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1104 (item 4 standing); DEC-1103 (2) narrowed, DEC-1058 (b) amended for the shared servers. Next free id: DEC-1105. |
| 0.490 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1105 (an exception to DEC-1010 for W2-20). Next free id: DEC-1106. |
| 0.491 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1106 (an exception to DEC-1010 for W2-148). Next free id: DEC-1107. |
| 0.492 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1107 (an exception to DEC-1010 for W2-148's F21). Next free id: DEC-1108. |
| 0.493 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1108. Next free id: DEC-1109. |
| 0.494 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1109 (item 3 standing). Next free id: DEC-1110. |
| 0.495 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1110 (items 1 and 3 standing). Next free id: DEC-1111. |
| 0.496 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1111 (item 2 open). Next free id: DEC-1112. |
| 0.497 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1112 (item 3 standing); DEC-1098 (4) narrowed to set-up A. Next free id: DEC-1113. |
| 0.498 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1113. Next free id: DEC-1114. |
| 0.499 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1114. Next free id: DEC-1115. |
| 0.500 | 2026-11-09 | Owner (recorded by the orchestrator, DEC-861): DEC-1115 (item 4 standing until the lift). Next free id: DEC-1116. |
| 0.501 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1116. Next free id: DEC-1117. |
| 0.502 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1117. Next free id: DEC-1118. |
| 0.503 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1118 (items 1 and 2 standing). Next free id: DEC-1119. |
| 0.504 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1119. Next free id: DEC-1120. |
| 0.505 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1120 (RUBRIC-2, standing; DEC-839 (1)-(3) and DEC-1119 (1) changed), DEC-1121 (the ticket template 1.0.1 with `class`). Next free id: DEC-1122. |
| 0.506 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1122 (the template 1.0.1 approved; usage (A) from now, DEC-1115 (4) changed; D-10's go on a condition). Next free id: DEC-1123. |
| 0.507 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1123 (items 3 and 5 standing; trailers a warning under Q-8 until W2-115). Next free id: DEC-1124. |
| 0.508 | 2026-11-10 | Owner (recorded by the orchestrator, DEC-861): DEC-1124 (Q23 re-worded by an independent session). Next free id: DEC-1125. |
| 0.509 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1125 (the latency a named red; the memory audit weekly, DEC-1101 (1) changed, DEC-1097 (4) folded; the night to the re-pin). Next free id: DEC-1126. |
| 0.510 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1126 (the answers to the 09:30 digest: re-pin done; usage (A) ends; W2-60a RUBRIC-2 now; the runaway brake for adopted products; the memory audit's schedule; W2-32/W2-15a open; D-10 the green run; W2-82 to P3; the permissions ACT). Next free id: DEC-1127. |
| 0.511 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1128 (the 100 % bar on set-up A for any control returning or new guard rule; the lift does not wait; set-up B dropped; DEC-1010 investigated; the switched-off list; the memory audit's landing); DEC-1112 (1) changed. DEC-1127 held for the owner's answer (the close history, PROPOSED). Next free id: DEC-1129. |
| 0.512 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1129 (W2-32 S9 (a1); the memory audit's briefs approved, hashes to the approved list by the install ACT; W2-60a a fresh round 1). DEC-1127 still held PROPOSED. Next free id: DEC-1130. |
| 0.513 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1130 (the `Verify:` pass and the hand-built-brief exception to DEC-1083; a ticket for adopted tickets without `Verify:`; W2-94 and W2-93 by the walled writer route). DEC-1127 still held PROPOSED. Next free id: DEC-1131. |
| 0.514 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1131 (one bar, two rounds for every role, option A; a blocking-only fix the same round; verdict.py and operator_run.py fixed now); DEC-1010 changed; DEC-1128's note corrected (W2-141's rule not live). DEC-1127 still held PROPOSED. Next free id: DEC-1132. |
| 0.515 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1127 WITHDRAWN (never in force); DEC-1132 (closes by DEC-953, option D; ADOPT-VERIFY-1 (d) and W2-174; the rg tripwire; the nightly's restart ACT; set-up A's bar to define). Next free id: DEC-1133. |
| 0.516 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1133 (set-up A's bar; the error path and listing rule first; ACT A; the sample day and the p95; FX6; MEMORY-PROTECTION-1 D1-D3; the floor 3 GiB). Next free id: DEC-1134. |
| 0.517 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1134 (the two warm-latency reds to accepted_reds until W2-155; linger; the handover). Next free id: DEC-1135. |
| 0.518 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1135 (a detection-only process-name match that can only refuse is outside DEC-1073 (4); DEC-1073 (4) read with it). Next free id: DEC-1136. |
| 0.519 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1136 (the W1-01 exemption first, the two path-map ACTs rebuilt after; every ACT changing tests/acceptance/ carries its own exemption entry in its apply). Next free id: DEC-1137. |
| 0.520 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1137 (W2-11's brief KPIs re-baselined, option (c); the role-template ticket before EXAMIN's copy, W2-27 depends on it). Next free id: DEC-1138. |
| 0.521 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1138 (the lead cap five through 11-12's working day, measured; the safety nets kept; no new lead run after 03:00; the p95 ACT rewrites the working size and both peaks). Next free id: DEC-1139. |
| 0.522 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1139 (W2-175's role templates approved at 4c0c73472fd8 and promoted as 1.0.1; three fixes for the next template delta, (c) to W2-33). Next free id: DEC-1140. |
| 0.523 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1140 (usage first: RUBRIC-2 at every launch, quiet notices; context awareness back; the load balancer, dispatcher and W2-115; the CTO session to about 1M tokens; the 80 % brake lifted this week, five leads, the 97 % and 99 % lines). Next free id: DEC-1141. |
| 0.524 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1141 (W2-11 approved; W2-176 withdrawn for its cap; no token cap for any session, DEC-1118 (A) replaced; DEC-1140 (4) corrected; hand merges of W2-175 and W2-176; the operator asleep only during the nightly). Next free id: DEC-1142. |

| 0.525 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1142 (W2-176's no-cap bytes approved; P-W2-23-8 (a); W2-115 PK-1 (a)+(c), DEC-903 changed; W2-148 S15 option 2; the operator hours as built; the ticket table, four parked; no new ticket or split without the owner; the two-refusal stop covers another form). Next free id: DEC-1143. |
| 0.526 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1143 (EXAMIN-SETS-1's answers: the two writer briefs approved; C1 the workbench copy at 0a82082495f5; C2-C5, C7; C6 the writer writes data only, the runner's option to the owner; C8 no checker). Next free id: DEC-1144. |
| 0.527 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1144 (P1-A W2-11 merged by hand; P1-B W2-157 reopened for the backstop hang; P1-C W2-146's lines read first; P1-D a narrow third check of the path-map chain; P1-E K9 by W2-121 a and b with part c's slot line; P1-F `--sets-root` in W2-93; P1-G reviewers' read-only probes in the quiet hours; two P2s read). Next free id: DEC-1145. |
| 0.528 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1145 (W2-146's kernel path-map schema approved at ebdbabd2e0d3; a non-compiling id form refused at use, the config check a row), DEC-1146 (a resource gate's refusal is a wait, not a two-refusal refusal; standing). Next free id: DEC-1147. |
| 0.529 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1147 (W2-152's kernel facts schema approved after the fact at 09fc68645c0c; its CIT-P record to be written; the adoption's facts file, row 173's route and the kernel scan to the owner). Next free id: DEC-1148. |
| 0.530 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1148 (five kernel files approved by their bytes; the adoption's facts file (a1), W2-27's line, W2-160 onto the path; the kernel gate in the CTO's tools; W2-45 widened for two revisions). Next free id: DEC-1149. |
| 0.531 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1149 (the working size 0.75 GiB by ACT-P95-1, applied; the figure everywhere; usage never stops a lead, the runaway brake kept; the peaks by 11-19), DEC-1150 (W2-88 split into W2-88a and W2-88b; P1-K (a); P1-L (a)); DEC-947 item 2, DEC-1138 (4), DEC-1140 (6) and DEC-1115 (4) changed. Next free id: DEC-1151. |
| 0.532 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1151 (ACT-EXAMIN-WRITERS-INSTALL-1 applied; the two walled writers delivered; W2-27's green-base line). Next free id: DEC-1152. |
| 0.533 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1152 (EXAMIN's visible half released and final; the commit's pin without an ACT; P1-M (a)). Next free id: DEC-1153. |
| 0.534 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1153 (W2-45 widened by W1-40's case; W2-160 by the session-watch command file). Next free id: DEC-1154. |
| 0.535 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1154 (a change decided after a review gets a narrow independent check; the ticket lands on it; standing). Next free id: DEC-1155. |
| 0.536 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1155 (P1-N (a): W2-172 widened by W2-171's F5 case; the sweep for the two ejection defects). Next free id: DEC-1156. |
| 0.537 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1156 (five lead packages; W2-157's and W2-159's F4 fixed now; two standing rules). Next free id: DEC-1157. |
| 0.538 | 2026-11-12 | Owner (recorded by the orchestrator, DEC-861): DEC-1157 (every rule that holds or delays a lead removed except the machine's and the governance's protections; DEC-1138 and DEC-1156 (8) superseded; nine changed). Next free id: DEC-1158. |
| 0.539 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1158 (the emergency of 11-02 lifted; six superseded, two spent). Next free id: DEC-1159. |
| 0.540 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1159 (the nightly beside the leads; W2-155 option 1, option 5 the fallback; the live reranker's limit). Next free id: DEC-1160. |
| 0.541 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1160 (the nightly's minimum cap 7.5 GiB; W2-33's kernel role files approved, C0 Haiku low). Next free id: DEC-1161. |
| 0.542 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1161 (P-W2-98-R2 (a); W2-60a P-1 (A) at the morning handover). Next free id: DEC-1162. |
| 0.543 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1162 (W2-141 closed as built, switch-on parked; yes ACT-CLAUDE-COPIES-6). Next free id: DEC-1163. |
| 0.544 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1163 (the morning of 11-13: the "until W2-56" line deleted; Node 22 nightly; W2-111 (a); go W2-33; three ACT yeses; the nightly's D, E, route; W2-37 F1 (a), P-1; W2-98 CIT-P; two ACTs; two corrections). Next free id: DEC-1164. |
| 0.545 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1165 (gov context's ceiling: the close's packet at a project setting and the supplementary cap; W2-183 filed). DEC-1164 held (PROPOSED, the owner reading). Next free id: DEC-1166. |
| 0.546 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1166 (three ACT yeses; W2-37's CIT-P at 1.1.0; message 5). Next free id: DEC-1167. |
| 0.547 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1167 (W2-88 RV2-1 (a); W2-60a P-5 (B), W2-184; the cuts; W2-182 E (1), W2-185; 7cc654e49 accepted; W2-111 (a)+(c); SANDBOX-1 (b)). Next free id: DEC-1168. |
| 0.548 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1168 (SANDBOX-1 B4 (a), W2-186, DEC-158 and DEC-1114 S9 amended; W2-94's physical step). Next free id: DEC-1169. |
| 0.549 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1169 (W2-32 closes on its own review, S11 re-worded; the status block names each ticket added and its approving decision). Next free id: DEC-1170. |
| 0.550 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1170 (the gitleaks scan stays off: a private, local development repository). Next free id: DEC-1171. |
| 0.551 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1164 (the DIF sweep decided: DEC-946's priorities and the operator's night sleep superseded; thirteen rules amended; the spent sequencing archived; the prompt's lifted holds removed; the owner's asleep clause for a decision that stops or delays a lead, (23); DEC-866 marks on 31 entries). Next free id: DEC-1171. |
| 0.552 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1171 (GUARD-HEREDOC (a); h10 retired and replaced; W2-15a's metric 34 of 39; COPIES-9; record edits scan only; the CTO's compaction trial (d)). Next free id: DEC-1172. |
| 0.553 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1172 (W2-88 NC-1 (a); W2-23's commit reset as the CTO's P2 under DEC-1164 (18)). Next free id: DEC-1173. |
| 0.554 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1173 (P-9 (a); CLAUDE.md and AGENTS.md (b) by ACT-CLASS-RULES-AGENTS-1; no plan change, a separate EXAMIN CTO, W2-27's dependencies; the handover's trial line). Next free id: DEC-1174. |
| 0.555 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1174 (GUARD-FIX-5 (b), the product parser fixed first; P-EXAMIN-CTO-1 approved with two conditions, the write rule named). Next free id: DEC-1175. |
| 0.556 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1175 (W2-94 GOLD; the operator's three ACTs, P-9 and P-9b; LANDING-72C6 (a); the corrected merge form; h10 callers (b); the CTO's routings of the evening). Next free id: DEC-1176. |
| 0.557 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1176 (memory proven per repository, built, measured and maintained in its own Wave 0; W2-88b a smoke run of gov adopt on grafana and redis, no measure; A5 by a fresh auditor per copy). Next free id: DEC-1177. |
| 0.558 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1177 (P-W2-184-1 (a): `_probe_files` reads the probe records under every root the launch records name; (c) the stop-gap until it lands). Next free id: DEC-1178. |
| 0.559 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1178 (P-W2-61H-HEAD-1 (A), (i); W2-100/W2-101 CIT-Ps and copies ACTs; P-RELEASE-1 0.1.0 at commit point (B), P-1 (a), pins (a), setup (a), W2-81 (b), walls (a) with P-4/P-5/P-6 fixed before W2-29, the EXAMIN CTO brief; W2-88 reopened with the scan speed; q02 variant). Next free id: DEC-1179. |
| 0.560 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1179 (MEMORY-AUDIT-P1: the standing set at 95 %, counts only; the monthly check against fitting; O3 (b) and O1-O9 (a); W2-187 DAEO-0cd2 and W2-188 DAEO-zlog filed; DEC-1101 (1), DEC-1125 (2), DEC-1098 (1), DEC-1126 (5), DEC-1074 (1) changed). Next free id: DEC-1180. |
| 0.561 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1180 (N2 (b): changed heading-cited sections listed for the walled writer; P-Q02-RUN-1 (a): a one-question fix flow, W2-94 reopened, run today; the EXAMIN CTO tonight after the re-pin and the operator's setup; standing: no deferral). Next free id: DEC-1181. |
| 0.562 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1181 (W2-188's adopt-skill bytes 6a884cf1 approved; SETUP-B-OWNER S2, S14, S18 (a), B4 (a) standing; P-Q02-RUN-1 run at W2-94's land; the stale config lock removed; standing: each reopened ticket named in every status block). Next free id: DEC-1182. |
| 0.563 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1182 (no repository scan on Gov OS; EXAMIN one full gitleaks scan a week before its weekly push, in the memory audit's weekly cycle; the guard's per-command secret rule on; q02's variant version 2; DEC-1045 (1) and DEC-1180 (2) changed). Next free id: DEC-1183. |
| 0.564 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1183 (W2-88 Route X: S27 (b), packages 1 and 2 (a); S27 folder mode its own round after the land; COPIES-12 yes; the CTO compaction trial ended, the full window again; every new lesson to memory at once; DEC-1171 (6) changed). Next free id: DEC-1184. |
| 0.565 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1184 (Q-REFRESH-1 (a): the seeded rebuild is the changes-only refresh; Q-SCAN-1 (a): the guard's path rule daily plus the weekly scan, no pre-commit scan; Q-SCAN-2 (a): W2-111 reopened; the EXAMIN CTO's first brief b70ff233 approved; W2-61h and W2-94 close; DEC-1182 (3), (4) answered). Next free id: DEC-1185. |
| 0.566 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1185 (W2-88 package 2: keyset pages of at most 100,000 links grouped by source file, each link read once, a refresh re-reading only changed files' links; a single link type over 100,000 handled; the time on redis; DEC-1183 (1) package 2 changed). Next free id: DEC-1186. |
| 0.567 | 2026-11-15 | Owner (recorded by the orchestrator, DEC-861): DEC-1186 (ACT-GUARD-FIX-6 yes, applied after the re-pin with the hook measured; W2-15a Q1-Q3 (a); P-WALLS-REANCHOR-1 (B) and the re-anchoring brief; P-W2-111-MARGIN by the measure; the re-pin in the owner's plain terminal; DEC-1179 (6) G2 changed). Next free id: DEC-1187. |
| 0.568 | 2026-11-15 | Owner (recorded by the orchestrator, DEC-861): DEC-1187 (P-W2-111-MARGIN (a): W2-111 reopened for the live hook's speed and the hook's fixed import cost, ACT-GUARD-FIX-7 to follow, the src part in 0.1.1; ACT-GUARD-FIX-6 kept; DEC-1186 (2) changed). Next free id: DEC-1188. |
| 0.569 | 2026-11-15 | Owner (recorded by the orchestrator, DEC-861): DEC-1188 (P-W2-27-F011 (a): EXAMIN's review and coordination tickets by the owner's operator tonight; W2-174 reopened for the launch fields by its checked apply, in 0.1.1). Next free id: DEC-1189. |
| 0.570 | 2026-11-15 | Owner (recorded by the orchestrator, DEC-861): DEC-1189 (W2-88-GITLEAKS-SHIP yes: W2-88 reopened within S24 for the shipped .gitleaks.toml, in 0.1.1; P-W2-81-FULLRUN (a): W2-81's full run on 0.1.0 tonight). Next free id: DEC-1190. |
| 0.571 | 2026-11-15 | Owner (recorded by the orchestrator, DEC-861): DEC-1190 (the W2-81 adopter brief approved; EXAMIN's settings reshaped to Gov OS's standard; the product fix flag-not-drop). Next free id: DEC-1191. |
| 0.572 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1191 (P-SESSIONS-1: adopting sessions headless; one operator job runner for everything the owner approves, (O) ACTs and the re-pin included; the sentinel's inbox rule by ACT). Next free id: DEC-1192. |
| 0.573 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1192 (P-ADOPT-TEMPLATES (a): the role templates by the owner's operator tonight; W2-153 reopened for gov adapters generate to write them, in 0.1.1). Next free id: DEC-1193. |
| 0.574 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1193 (the sets-root file; summary-only operator jobs for hidden-set steps). Next free id: DEC-1194. |
| 0.575 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1194 (P-W2-27-F016 (a): EXAMIN's three command front matters quoted by the owner's commit). Next free id: DEC-1195. |
| 0.576 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1195 (Wave 3 row: the agent-to-agent layer productised for every adopted repository; tonight's lessons in DND 249). Next free id: DEC-1196. |
| 0.577 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1196 (the undo; (O) by hand until act-O; routine jobs R1-R3 with R3 by independent review; when the owner's yes is needed; no rehearsal against a live path). Next free id: DEC-1197. |
| 0.578 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1197 (P-W2-81-VERDICT-1 (a)(b)(c)). Next free id: DEC-1198. |
| 0.579 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1198 (0.1.1 (a) and go; EXAMIN (i), F-021 (c), item 15 (a), TD tree (a); P-JOBS-USER-1 (B) and a Wave 3 row; W2-81-FIGURES (b); BATCH1-HELD (a); OPROOT (a); ACT-GUARD-FIX-7 with its follow-ups; a guard false-positive package). Next free id: DEC-1199. |
| 0.580 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1199 (EXAMIN's CTO leads its Wave 0; F-022 (b), go LITE, F-023 (a); the freeze lifted; FREE-HAND D1-D7 on (A-full); an interim job queue; residuals; P-GUARD-FP-1 (a), (b)); DEC-1198 (3) changed. Next free id: DEC-1200. |
| 0.581 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1200 (P-EXAMIN-LEAD-1 (a)(b)(c): the Wave 0 brief 0d96110c, the Remote Control session, the channel; P-ADOPT-SPEC-AUDIT-1 (a), W2-192). Next free id: DEC-1201. |
| 0.582 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1201 (Wave 2 keeps only Gov OS's work: ten tickets to Wave 3's list, W2-27 to W2-30 to EXAMIN's Wave 0; F-028 (a) with the base-red condition; the status block in every report; no customer data in EXAMIN; the merge back); DEC-954 changed. Next free id: DEC-1202. |
| 0.583 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1202 (the exit proof: W2-81's S-RERUN on 0.1.1; W2-46 re-pointed; W2-82's wait dropped; the four extra Wave 3 moves kept; the EXAMIN brief 2ec48c78 approved); DEC-1099 (3) and DEC-954 changed. Next free id: DEC-1203. |
| 0.584 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1203 (P-JOBS-USER-1 (B) as an exception until Wave 3; GF-7 alone first; W2-27's run closed with exa-g6db as a named exception, F-028/F-030 tickets; brief 31acaf29; DEC-1010 for every review); DEC-1199 (3) changed. Next free id: DEC-1204. |
| 0.585 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1204 (how work is judged: one golden rule merging ADR-0001 / DEC-039, DEC-801 and DEC-1010 item 1; P-GOLDEN-RULE-1 (a); the skill judging-work 0fc1c502 approved; W2-195 filed, top priority; ACT-GOLDEN-RULE-1 for CLAUDE.md and AGENTS.md); DEC-039, DEC-801 and DEC-1010 (1) changed. Next free id: DEC-1205. |
| 0.586 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1205 (P-PERMISSIONS-1 (a) with the push belt: full permission inside the box only; ACT-GUARD-FIX-9, the box, the no-prompt start lines, today; workers kept; OWNER-OPERATOR-FULL-1); DEC-1203 and DEC-1204 stamps corrected. Next free id: DEC-1206. |
| 0.587 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1206 (W2-194 keeps F-031; W2-15a closed on the walled run's record under Q2 (a), its gaps to W2-15b; the gap investigated by an operator job, ids and counts only). Next free id: DEC-1207. |
| 0.588 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1207 (yes ACT-GOLDEN-RULE-1 f9d67d5a; P-BOX-EXCEPTION-1 yes with F2 fixed, F1 and F3 Wave 3 rows; the memory measurement rule: a fresh 80 per measure on one frozen state, amending DEC-1179 (1); today's order); DEC-1206 (3) given the owner's 16:51 order. Next free id: DEC-1208. |
| 0.589 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1208 (the work-sizing rubric: W2-196 approved, FULL; the provisional rubric Q/L/S/F in force from today; the operator's full permission and the no-prompt switch routed by it first, finished today). Next free id: DEC-1209. |
| 0.590 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1209 (EMERGENCY: no new tickets, W2-196 withdrawn; running work stops at its current step; audits and rubric research go on; EXAMIN direct; the emergency's own fixes first). Next free id: DEC-1210. |
| 0.591 | 2026-11-16 | Owner (recorded by the orchestrator, DEC-861): DEC-1210 (P-FRESH-80-1 (a) with A13 (b): a fresh 80 per measure, the judged figure at 95 % the bar, the amendments recorded; W2-187/W2-188 reopened after the emergency; the first fresh 80 queued as JOB-20261116-15). Next free id: DEC-1211. |
