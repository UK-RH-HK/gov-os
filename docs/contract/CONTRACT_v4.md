---
id: CONTRACT-v4
status: PROPOSED
depends_on: [CHARTER-v5, ADR-0001, ADR-0002]
decisions: [DEC-064, DEC-065, DEC-074, DEC-075, DEC-078, DEC-080, DEC-083, DEC-085, DEC-086, DEC-087]
---

# Governance OS — Capability Acceptance Contract v4

Contract v4 states what the Gov OS must do, as outcomes with **one observable acceptance check each**. It replaces Contract v3 as the working text (DEC-058). `contract.yaml` holds the same content in machine-readable form; `readiness-dimensions.yaml` defines the 26 readiness rows that Wave 1's OpenSpec schema implements.

**Precedence:** Charter v5 → Contract v4 → ADRs → everything else. The ADRs supersede the originals where they conflict.

**Fields:** `outcome` (what an agent or the owner can do) · `acceptance` (one observable check) · `wave` (W1/W2/W3; the wave in which the acceptance check must pass, with earlier partial delivery in `wave_note`) · `provider` (tool or W1 ticket; W2/W3 components are named) · `sources` (Contract v3 gates, Framework sections, owner records, decisions) · `scenarios` (dev and qual ids from `COVERAGE_MATRIX.md`; where the matrix truncates a list, the count of unlisted ids is given) · `disposition` (KEPT, LITE with its lite form, or DROP with its decision).

## 1. Counts

| Wave | KEPT | LITE | DROP | Total |
|---|---|---|---|---|
| W1 | 37 | 4 | 0 | 41 |
| W2 | 7 | 0 | 0 | 7 |
| W3 | 10 | 0 | 0 | 10 |
| NONE | 0 | 0 | 2 | 2 |
| **All** | 54 | 4 | 2 | 60 |

DEC-080 places CAP-15, 16, 18, 55, 56 and 57 in Wave 1, with the citation validator and hierarchical synthesis. DEC-074 R1/Q3 places semantic retrieval and the reranker (CAP-10) in Wave 1.

## 2. Envelope and boundary

- **Scale envelope** (DEC-078). Tested up to ≈ 80k nodes / 270k edges of code graph at ≈ 2.2 GB peak RSS for codebase-memory-mcp; larger graphs are measured before adoption. Memory scales with graph edges, not file count. Each project in a multi-project folder gets its own index.
- **RAM budget** (DEC-078). Worst case ≈ 12.5 GB of the 15.5 GiB host (IDE + local models + a full index run), leaving ≈ 2.5 GiB spare; incremental updates are far smaller. The stack runs with one on-demand daemon (Ollama, 5-min idle unload), no Docker, VRAM peak ≈ 5.2 of 16 GiB.
- **Token budget** (DEC-004, DEC-086). Governance tokens ≤ 10–15 % of a ticket's fresh input + output tokens (the Wave 1 exit bound is 15 %). Governance tokens = text the Gov OS injects or returns (instruction files, SessionStart packet, hook output, `gov` output, governance MCP tool definitions, checkpoint and close records), counted by `gov`; the denominator comes from ccusage. Cache reads are reported separately. Context packet ≤ ~6k tokens; SessionStart injection ≤ ~2.5k tokens plus a file path; AGENTS.md ≤ ~1.5k tokens. A breach is a health finding, never a silent cost.
- **Boundary** (DEC-039, DEC-075, DEC-087). Hooks are guardrails. The boundary is git history, the lefthook pre-push gate G3 on the owner's machine, GitHub Actions CI G4–G5 as an advisory result on every push (deterministic checks only; model-dependent tests run at G3 and leave an evidence record bound to the head commit that CI checks), and the rule that only the owner merges, and only on green. `main` is not protected; enabling protection later changes no other decision.
- **Loop budget** (DEC-044). At most two review→repair rounds per surface; then DELETE, NARROW or DEFER unless an owner ADR says otherwise.
- **Tool installs** (DEC-083). The orchestrator installs a tool only after the owner approves a decision package in chat (tool, exact version, source and checksum, need, disk and RAM, uninstall command), and records it in the tool registry; install commands are `ask` for the orchestrator and denied for every other role; `sudo` stays with the owner.

## 3. Master-rule clauses

The rule texts are in Charter v5 §4, verbatim from architecture v0.3 §1A. Each clause below is a contract item with one acceptance check.

| Id | Rule | Acceptance | Provider | Dev scenarios | Decisions |
|---|---|---|---|---|---|
| MR-1 | Specification comes first | A production ticket whose specification has a required readiness cell open for its profile (FULL for a spine) cannot reach READY: `tk ready` does not list it and `gov readiness` names the open cells; an N/A without a reason is rejected. | W1-12, W1-13, W1-35 | MR-A-02, MR-B-02 | DEC-065, DEC-085 |
| MR-2 | Closed specifications generate the work | A closed specification produces tickets with class, role, depends_on, allowed_paths, KPIs and profile, and `gov check` fails a ticket missing any of them; from W2 every required open cell yields a ticket. | W1-14, W1-35, W2: gov readiness --generate | MR-A-02, MR-A-04, MR-B-02, MR-B-04 | DEC-065 |
| MR-3 | KPIs; the builder never writes its own acceptance tests | An implementer write to `tests/acceptance/**` is refused by the guard and caught by the post-command containment check; an implementation ticket is not READY until `tests/acceptance/<ticket-id>/` exists; a breach is a forbidden outcome. | W1-02, W1-03, W1-09, W1-30, W1-33 | MR-A-01, MR-B-01 | DEC-065, DEC-069, DEC-076, DEC-084 |
| MR-4 | Audit, discovery and impact are distinct functions | Each of `gov doctor`, discovery, CIT-P, CIT-E and audit has its own command or skill and record; an audit report names an auditor session that authored none of the audited files. | W1-27, W1-13, W1-35, W1-36, W1-33 | MR-A-05, MR-A-06, MR-B-05, MR-B-06 | DEC-065, DEC-066, DEC-070 |
| MR-5 | The Gov OS works as a software company | Each Wave 1 role exists as a generated subagent definition with purpose, allowed-path pattern, tools, model tier, authority level and handoff format, and a ticket's role field names one of them. | W1-33, W1-38 | CHAOS-X-02 | DEC-065, DEC-066 |
| MR-6 | The human is the customer and final authority | Every owner question appears in the active chat as a package with all eight fields, ranked; the dependent branch waits while an independent branch proceeds; each answer is committed as a decision record. | W1-34, W1-35 | MR-A-03, MR-B-03 | DEC-065 |

## 4. Capabilities

### CAP-01 — Authority precedence and hard invariants

- **Outcome:** An agent can tell which of two conflicting records governs, by a deterministic precedence (Charter → Contract → ADRs → specifications → tasks → retrieval → inference) and by supersession status.
- **Acceptance:** Given two conflicting records at different precedence levels, `gov context` puts only the higher one in the authority block and marks the lower one superseded.
- **Wave:** W1
- **Provider:** MADR + check-jsonschema 0.38.2, W1-10, W1-11, W1-24
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A1; Framework v4.1.2 §2, §21; OWNER-CLARIFICATION-P2-0004; DEC-012; DEC-046; DEC-083
- **Scenarios:** dev MR-A-06, CHAOS-A-13, AUDIT-A-01, MR-B-01, MR-B-06, CHAOS-B-13, AUDIT-B-07 · qual CHAOS-A-Q05, AUDIT-A-Q01, AUDIT-A-Q07, AUDIT-A-Q08, A-Q04, AUDIT-A-Q22, AUDIT-A-Q39, AUDIT-A-Q42, AUDIT-A-Q45

### CAP-02 — Release authenticity (lite: signed git tags)

- **Outcome:** The owner can confirm that an installed kernel matches a released version.
- **Acceptance:** `gov doctor` reports MATCH when every kernel file hashes to the manifest recorded in `framework.lock`, and DRIFT naming the file after one kernel file is edited; `git tag -v` verifies the release tag.
- **Wave:** W1 (manifest check in W1; the signed v1.0.0 tag is made at Release 1)
- **Provider:** Copier 9.18.2, git SSH-signed tags, W1-39, W1-27
- **Disposition:** LITE — lite form: SSH-signed release tag plus a file-hash manifest in `framework.lock`, verified by `gov doctor`; no TUF, key rotation, offline envelopes or bootstrap separation.
- **Sources:** Contract v3 Gate A2; Framework v4.1.2 §75B-75D; Distribution Protocol v1.2 §5-8; OWNER-DIRECTIVE-0004; OWNER-DECISION-0009; OWNER-DECISION-P2-0005; DEC-027; DEC-074; DEC-083
- **Scenarios:** dev CHAOS-X-01 · qual CHAOS-X-Q01

### CAP-03 — Security and sensitivity classification

- **Outcome:** An agent can rely on secrets never reaching an index, a packet or an export: a content-based filter runs before every indexer, and harness deny rules cover secret files.
- **Acceptance:** After indexing a tree with planted secrets (including a token-shaped canary gitleaks defaults miss), no canary string appears in any `.gov-runtime/` store, codebase-memory index, context packet or evidence bundle.
- **Wave:** W1
- **Provider:** gitleaks 8.30.1, W1-15, W1-16, W1-01
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A3; Framework v4.1.2 §16, §72; Distribution Protocol v1.2 §14, §17; DEC-074; DEC-076
- **Scenarios:** dev CHAOS-A-14, SEC-A-01, SEC-A-02, SEC-A-03, CHAOS-B-15, SEC-B-01, SEC-B-02, ISO-X-01 · qual CHAOS-A-Q09, RETR-A-Q03, SEC-A-Q01, SEC-A-Q02, SEC-A-Q03, SEC-A-Q04, AUDIT-A-Q49, SEC-A-Q05, SEC-A-Q06, MR-B-Q03, MR-B-Q06, CHAOS-B-Q08 (+9 not listed in the matrix row)

### CAP-04 — Budget and resource governance

- **Outcome:** The owner can set token and cost budgets per task; crossing one raises a decision package instead of continuing silently.
- **Acceptance:** A task configured with a token budget that its run exceeds stops at the next `gov close` or hook boundary and surfaces a decision package; the breach is recorded in the ticket.
- **Wave:** W2 (W1 measures the governance share (W1-31); the halting budget gate is W2)
- **Provider:** ccusage (pinned, DEC-086), W1-31, W2: budget gate in gov close/status
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A4; Framework v4.1.2 §73; OWNER-DIRECTION-P2-0009 §11 (10-15% overhead target); DEC-004, DEC-031; DEC-083; DEC-086
- **Scenarios:** dev SOAK-X-01 · qual SOAK-X-Q01

### CAP-05 — Emergency controls (pause/freeze/cancel/rollback)

- **Outcome:** The owner can freeze all agent writes with one command and resume them, and roll back by `git revert`.
- **Acceptance:** After `gov pause`, the next Edit/Write/Bash write by any role is denied by the guard, and `git status --porcelain` is unchanged; `gov pause --off` restores writes.
- **Wave:** W1
- **Provider:** W1-28, W1-02
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A5; Framework v4.1.2 §74; DEC-025
- **Scenarios:** dev CHAOS-A-10, CHAOS-A-15 · qual CHAOS-X-Q04

### CAP-06 — Repository contract and path map

- **Outcome:** An agent can find where every kind of artefact lives from the committed path map, and nothing material is unclassified.
- **Acceptance:** `gov doctor` reports zero unclassified tracked paths against `governance/project/path-map.yaml`, and names each path when one is added outside the map.
- **Wave:** W1
- **Provider:** W1-08, W1-27, W1-41
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate B1, B2; Framework v4.1.2 §8, §9; Adoption Protocol v3.0 §8; OWNER-DECISION-P2-0008 §2 (project-specific floor); DEC-060; DEC-041
- **Scenarios:** dev B-01, B-02, B-03, B-04, B-05, B-08, B-09, B-11, AUDIT-B-03, AUDIT-B-07, SEC-B-01, SEC-B-02 (+2 not listed in the matrix row) · qual MR-B-Q06, SEC-B-Q02, B-Q01, B-Q02, B-Q03, AUDIT-B-Q18, AUDIT-B-Q23, AUDIT-B-Q38, ISO-X-Q01, B-X-Q01

### CAP-07 — Authoritative vs derived state separation

- **Outcome:** An agent can delete all derived state without losing anything authoritative.
- **Acceptance:** Deleting `.gov-runtime/` leaves `git status --porcelain` empty, and `gov rebuild` restores every derived store.
- **Wave:** W1
- **Provider:** W1-17, W1-27
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate B3; Framework v4.1.2 §10, §12, §19; DEC-057
- **Scenarios:** dev CHAOS-A-02, CHAOS-B-02, CHAOS-B-10, B-03, B-06, ISO-X-01, ISO-X-02 · qual CHAOS-A-Q03, CHAOS-A-Q06, CHAOS-A-Q08, RETR-A-Q04, SOAK-A-Q01, SOAK-A-Q02, SOAK-A-Q03, AUDIT-A-Q33, AUDIT-A-Q34, ISO-X-Q01, ISO-X-Q02

### CAP-08 — Deterministic structured memory (records)

- **Outcome:** An agent can ask exact structured questions over records (status, type, owner, links) and get exact answers.
- **Acceptance:** A query for ACTIVE decisions returns exactly the set whose frontmatter status is ACTIVE and that nothing supersedes.
- **Wave:** W1
- **Provider:** W1-10
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C1; Framework v4.1.2 §11.1; DEC-012
- **Scenarios:** dev RETR-A-02, ISO-X-01 · qual AUDIT-A-Q01, AUDIT-A-Q03, A-Q04, AUDIT-A-Q10, AUDIT-A-Q45, ISO-X-Q01

### CAP-09 — Relationship/graph memory

- **Outcome:** An agent can traverse implements, validates, supersedes and depends_on links across all record types, including broken ones.
- **Acceptance:** For a fixture record set, the graph returns every IMPLEMENTS and VALIDATES edge of a requirement and reports each dangling reference by id.
- **Wave:** W1
- **Provider:** W1-10, W1-20
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C2; Framework v4.1.2 §11.2; DEC-012; DEC-080
- **Scenarios:** dev MR-B-05, CHAOS-B-11, CHAOS-B-12, B-09, RETR-B-04, CIT-B-01, AUDIT-B-01, AUDIT-B-02, AUDIT-B-04, A-X-01, RETR-X-05 · qual MR-A-Q06, CHAOS-A-Q11, RETR-A-Q02, AUDIT-A-Q03, AUDIT-A-Q34, RETR-B-Q01, RETR-B-Q02, RETR-B-Q03, RETR-B-Q04, AUDIT-B-Q03, B-Q04, AUDIT-B-Q13 (+9 not listed in the matrix row)

### CAP-10 — Semantic memory (vector/embedding retrieval)

- **Outcome:** An agent can find a record from a paraphrased question.
- **Acceptance:** On the dev query set, paraphrased questions reach the gold record in the top 5 at least as often as the S0b2 R1 baseline (mean hit@5 85).
- **Wave:** W1 (moved from W2 by DEC-074 R1/Q3 and DEC-080)
- **Provider:** Ollama 0.35.0 + qwen3-embedding:0.6b, sqlite-vec 0.1.9, W1-19
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C3; Framework v4.1.2 §11.3, §14; OWNER-DIRECTION-BR-0006 §1, §5 (provisional BGE, replaceable); OWNER-CLARIFICATION-BR-0002 (whole-repo corpus); DEC-016; DEC-017; DEC-074; DEC-080
- **Scenarios:** dev RETR-A-01, RETR-A-02, CHAOS-B-11, B-11, RETR-B-01, RETR-B-02, AUDIT-B-06, ISO-X-01, RETR-X-05 · qual B-Q05, AUDIT-B-Q26, AUDIT-B-Q28, AUDIT-B-Q29, AUDIT-B-Q31, AUDIT-B-Q32, AUDIT-B-Q40, ISO-X-Q01

### CAP-11 — Lexical memory (FTS/BM25)

- **Outcome:** An agent can find exact strings, identifiers and error messages with file and line.
- **Acceptance:** An exact error-string query returns the file path and line number of every occurrence in the indexed tree.
- **Wave:** W1
- **Provider:** SQLite FTS5 (carried), W1-17
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C4; Framework v4.1.2 §11.4; DEC-016; DEC-074
- **Scenarios:** dev RETR-A-04, RETR-B-03, RETR-B-04, ISO-X-01, RETR-X-05 · qual CHAOS-A-Q04, CHAOS-A-Q12, AUDIT-A-Q05, A-Q04, AUDIT-A-Q09, AUDIT-A-Q13, AUDIT-A-Q15, RETR-B-Q01, AUDIT-B-Q20, ISO-X-Q01

### CAP-12 — Code-structural memory (AST/LSP/SCIP)

- **Outcome:** An agent can find definitions, callers and impact across languages from a code graph, without reading whole files.
- **Acceptance:** "References to function X" returns every call site across Rust, Python and TypeScript in the dev tier, before and after a rename.
- **Wave:** W1
- **Provider:** codebase-memory-mcp 0.11.0, W1-16
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C5; Framework v4.1.2 §11.5; DEC-014; DEC-074; DEC-076
- **Scenarios:** dev MR-A-06, RETR-A-03, AUDIT-A-01, MR-B-06, B-08, RETR-B-02, RETR-B-03, RETR-X-05 · qual RETR-A-Q01, AUDIT-A-Q04, AUDIT-A-Q05, AUDIT-A-Q07, AUDIT-A-Q16, MR-B-Q01, B-Q01, B-Q03, ISO-X-Q01

### CAP-13 — Temporal and episodic memory

- **Outcome:** An agent can see how a file or decision changed over time and which decision or task caused each change.
- **Acceptance:** For a changed file, the graph returns its commits with their `Implements:` and `Task:` trailers resolved to the decision and ticket records.
- **Wave:** W1
- **Provider:** git log + commit trailers, W1-10, W1-30, W1-25
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C6, C7; Framework v4.1.2 §11.6, §11.7; DEC-012
- **Scenarios:** dev CHAOS-A-03, CHAOS-B-03, B-07 · qual CHAOS-A-Q04, CHAOS-A-Q08, AUDIT-A-Q04, AUDIT-A-Q11, AUDIT-A-Q12, AUDIT-A-Q13, AUDIT-A-Q14, AUDIT-A-Q15, AUDIT-A-Q16, AUDIT-A-Q17, AUDIT-A-Q18, AUDIT-A-Q19

### CAP-14 — Failure memory

- **Outcome:** An agent can see a previously failed approach before it retries it.
- **Acceptance:** A retrieval for a task whose scope matches a committed failure record returns that record in the evidence bundle before any implementation step.
- **Wave:** W1
- **Provider:** W1-08, W1-21
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C8; Framework v4.1.2 §11.8; OWNER-DIRECTION-BR-0006 §1 (lessons/failed approaches); DEC-080
- **Scenarios:** dev CHAOS-B-01, CHAOS-B-04, RETR-X-04, B-X-02 · qual AUDIT-A-Q02, AUDIT-A-Q20, AUDIT-A-Q22, AUDIT-A-Q23, AUDIT-A-Q25, CHAOS-B-Q13, B-Q02, SEC-B-Q03, RETR-X-Q04

### CAP-15 — Context packet compilation

- **Outcome:** An agent starts every task with a compiled context packet: mandatory inputs by id and hash, an authority block first, under a ceiling.
- **Acceptance:** `gov context <ticket>` writes a packet that contains every mandatory input by id and sha256, stays under the configured ceiling (default ~6k tokens), carries its own hash, and is delivered as a file path plus a summary of at most ~2.5k tokens.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-24, W1-29
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C9; Framework v4.1.2 §15; Contract v3 Gate W4, W9, W10; OWNER-DIRECTION-BR-0005 (multi-batch retrieval); OWNER-DIRECTION-BR-0006 §4 (hierarchical synthesis); DEC-030, DEC-031, DEC-032; DEC-003; DEC-004; DEC-080
- **Scenarios:** dev CHAOS-A-11, ISO-X-01, RETR-X-04 · qual ISO-X-Q01, RETR-X-Q02

### CAP-16 — Multi-batch, multi-hop, paginated retrieval

- **Outcome:** An agent can gather evidence that spans many locations and hops, in batches, until a stated stopping reason.
- **Acceptance:** On RETR-A-04 and RETR-X-02, the evidence bundle shows more than one batch, the merge, and a stopping reason from the fixed list; a batch-size limit is never reported as completeness.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-21, W1-36
- **Disposition:** KEPT
- **Sources:** OWNER-DIRECTION-BR-0005 (full); OWNER-DIRECTION-BR-0006 §2, §3; DEC-030, DEC-033, DEC-034, DEC-035; DEC-080
- **Scenarios:** dev RETR-A-04, RETR-X-02 · qual RETR-A-Q01, RETR-A-Q02, RETR-A-Q03, RETR-A-Q04, RETR-X-Q02, RETR-X-Q05

### CAP-17 — Incremental indexing and freshness

- **Outcome:** An agent never receives stale evidence silently: changed files are re-indexed before the next retrieval, or the facet is reported unavailable.
- **Acceptance:** After one decision file is edited, the next `gov retrieve` returns the edited content, or reports the facet FACET_UNAVAILABLE; it never returns the old text as current.
- **Wave:** W1 (commit-time re-index hook (G-23) is W2)
- **Provider:** W1-17, W1-22, W2: G-23 re-index hook
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D1; Framework v4.1.2 §13; DEC-037 (zero-result canaries); DEC-080
- **Scenarios:** dev CHAOS-A-02, CHAOS-A-03, CHAOS-A-12, CHAOS-B-02, CHAOS-B-03, CHAOS-B-09, CHAOS-B-12, B-06, B-10, RETR-X-01 · qual RETR-X-Q01

### CAP-18 — Retrieval router (multi-route fusion)

- **Outcome:** An agent can answer a complex question through several retrieval routes, fused, deduplicated and reranked once.
- **Acceptance:** A question that needs lexical, semantic and graph routes returns one fused list with duplicates removed by chunk hash and one rerank over the merged set; the bundle names the routes used.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-19, W1-21
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D2, D3; Framework v4.1.2 §14, §14.1; DEC-016; DEC-074; DEC-080
- **Scenarios:** dev RETR-A-01, RETR-X-01, RETR-X-05 · qual RETR-X-Q05

### CAP-19 — Retrieval component separation and model selection

- **Outcome:** The owner can swap an embedding or reranking model through configuration, with a pinned revision and a regression check.
- **Acceptance:** Changing the embedder pin in configuration triggers a full re-embed, the dev-tier retrieval regression passes, and an unpinned or mismatched model makes retrieval fail closed with a named error.
- **Wave:** W2 (fail-closed model pin and lighter reranker spike W2; per-repository benchmark W3)
- **Provider:** W2: embedder/reranker adapters under the fail-closed pin, W3: per-repository retrieval benchmark
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D4, D5; Framework v4.1.2 §14.2, §14.3; OWNER-DIRECTION-BR-0006 §5 (provisional BGE, replaceable); DEC-017; DEC-046; DEC-074
- **Scenarios:** dev RETR-X-01 · qual RETR-X-Q01

### CAP-20 — Rebuild guarantee (delete derived, rebuild from git)

- **Outcome:** A fresh agent on a fresh clone can rebuild all derived state from git and continue.
- **Acceptance:** `gov rebuild` twice from the same commit yields the same chunk-SHA-256 digest, and a fresh agent resumes the active ticket from the rebuilt state and the latest checkpoint.
- **Wave:** W1
- **Provider:** W1-27
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D6; Framework v4.1.2 §19; Distribution Protocol v1.2 §7.5; DEC-016
- **Scenarios:** dev CHAOS-A-01, CHAOS-A-02, CHAOS-A-09, CHAOS-B-01, CHAOS-B-02, CHAOS-B-09, CHAOS-B-10, B-06, ISO-X-01, ISO-X-02 · qual CHAOS-A-Q03, CHAOS-B-Q02, SOAK-B-Q01, B-Q04, AUDIT-B-Q17, AUDIT-B-Q19, AUDIT-B-Q21, AUDIT-B-Q22, AUDIT-B-Q24, AUDIT-B-Q33, SOAK-B-Q02, ISO-X-Q01 (+1 not listed in the matrix row)

### CAP-21 — Owner-only approval facts (lite of L0-L5 authority levels)

- **Outcome:** The owner can trust that no agent makes a decision ACTIVE on its own.
- **Acceptance:** `gov check` (and CI) fails a change that sets a decision ACTIVE unless the change carries an owner approval fact from git.
- **Wave:** W1
- **Provider:** W1-11
- **Disposition:** LITE — lite form: An approval is a fact only when it comes from the owner's git account (owner commit, signed tag or PR approval); no in-process L0–L5 machinery.
- **Sources:** Contract v3 Gate E1; Framework v4.1.2 §23; OWNER-DECISION-P2-0001 (role identity binding); DEC-039; DEC-046; DEC-074
- **Scenarios:** dev MR-A-01 · qual MR-A-Q01, CHAOS-A-Q10, AUDIT-A-Q27

### CAP-22 — Agent roles and typed A2A handoffs

- **Outcome:** An agent can hand work to a fresh agent in a typed record the receiver can act on without the sender's chat.
- **Acceptance:** A fresh agent B, given only the handoff record and the repository, states the task, inputs, open questions and next step identically to agent A's record.
- **Wave:** W2 (W1 hands off through checkpoints; typed handoff records and specialist roles are W2)
- **Provider:** W1-25, W2: typed handoff records
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate E2, E3; Framework v4.1.2 §24, §25; DEC-066
- **Scenarios:** dev CHAOS-X-02 · qual CHAOS-X-Q02

### CAP-23 — Concurrency and task claims

- **Outcome:** Two agents cannot both take the same task.
- **Acceptance:** A second agent claiming a ticket already claimed by another gets a collision error naming the holder, and the ticket is absent from its ready queue.
- **Wave:** W3 (the exclusive claim lock (G-03) is delivered in W1-09; parallel-agent concurrency and the claims role are W3)
- **Provider:** ticket v0.3.2, W1-09, W3: gov claim + claims/concurrency role
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate E4; Framework v4.1.2 §44; DEC-066; DEC-074; DEC-076
- **Scenarios:** dev CHAOS-X-03 · qual CHAOS-X-Q03

### CAP-24 — Skill lifecycle and versioning

- **Outcome:** An agent can tell which version of each skill produced a piece of work.
- **Acceptance:** Every skill file carries a version in frontmatter, and the `gov close` record of a ticket lists the skill ids and versions used.
- **Wave:** W1
- **Provider:** W1-35, W1-36, W1-37, W1-30
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate F1; Framework v4.1.2 §26, §27; DEC-024; DEC-074
- **Scenarios:** dev CHAOS-A-05 · qual CHAOS-X-Q05

### CAP-25 — Tool registry and capability memory (lite)

- **Outcome:** The owner can see every tool the Gov OS relies on, at which pinned version, and approve every install.
- **Acceptance:** `gov doctor --json` lists pinned versus found versions and exits non-zero on drift; an install command from the orchestrator raises an approval prompt (also in Auto mode), and from any other role is denied.
- **Wave:** W1
- **Provider:** W1-04, W1-06, W1-27
- **Disposition:** LITE — lite form: Tool registry with pins; the orchestrator installs a tool only after the owner approves a decision package in chat, and records version, sha256, install and uninstall commands, date and approving decision; `gov doctor` checks the pins. No automated install classification (DEC-083).
- **Sources:** Contract v3 Gate F2, F3; Framework v4.1.2 §28-30; OWNER-DECISION-P2-0003 (gate only elevated installs); Contract v3 Gate C10; Framework v4.1.2 §11.10; DEC-040; DEC-074; DEC-083
- **Scenarios:** dev CHAOS-A-05, CHAOS-B-04, CHAOS-B-05, CHAOS-B-14, B-10, AUDIT-B-03 · qual CHAOS-X-Q05

### CAP-26 — Plugin trust boundary (hash-binding, descriptor security)

- **Outcome:** (none — non-goal)
- **Acceptance:** No kernel file implements plugin hash-binding or descriptor trust; the wave-exit audit finds none (DEC-070).
- **Wave:** NONE (dropped)
- **Provider:** none (non-goal)
- **Disposition:** DROP — Non-goal: plugin trust boundary (hash-binding, descriptor security, self-attestation prevention) defends against a same-privilege adversary (ADR-0001).
- **Sources:** Contract v3 Gate F4; OWNER-DECISION-P2-0005 (bind the bytes); OWNER-CLARIFICATION-P2-0004 (project files cannot manufacture authority); DEC-039; DEC-075
- **Scenarios:** dev — · qual —

### CAP-27 — Read/act separation of commands (lite of MCP/A2A/knowledge layers)

- **Outcome:** An agent can run any read command without changing the repository.
- **Acceptance:** Every `gov` read command (status, check, readiness, doctor, context --dry-run, closure, retrieve) leaves `git status --porcelain` empty.
- **Wave:** W1
- **Provider:** W1-07
- **Disposition:** LITE — lite form: Read commands never mutate; no separate A2A layer or three-layer knowledge fabric.
- **Sources:** Contract v3 Gate F5; Framework v4.1.2 §31; DEC-074
- **Scenarios:** dev MR-X-01 · qual MR-X-Q01

### CAP-28 — Natural-language intent routing and small command surface

- **Outcome:** The owner can ask in natural language and get a structured governance answer; a small command set covers the rest.
- **Acceptance:** A status question in chat is answered from `gov status --json` (tickets, gates, readiness, share, pause state) rather than from free recall.
- **Wave:** W1
- **Provider:** Claude Code (harness), W1-07, W1-32
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate G1, G2; Framework v4.1.2 §33, §34; DEC-003
- **Scenarios:** dev MR-X-01 · qual MR-X-Q01

### CAP-29 — Specification lineage (idea to live evidence)

- **Outcome:** An agent can follow a feature from idea through scenarios, requirements, decisions, tasks and tests to live evidence.
- **Acceptance:** For a feature, `gov closure` returns its linked mission, scenario, requirement, decision, ticket and acceptance-test ids, and reports each missing link.
- **Wave:** W3 (links from OpenSpec and frontmatter in W1; full idea→live-evidence lineage W3)
- **Provider:** OpenSpec 1.13.2, W1-08, W1-10, W3: full lineage
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate H1; Framework v4.1.2 §36; DEC-011; DEC-064
- **Scenarios:** dev A-X-01 · qual A-X-Q01

### CAP-30 — Feature readiness contract (26-dimension checklist)

- **Outcome:** An agent can see, per feature, which of the 26 readiness rows are open for its profile, and each gap becomes work.
- **Acceptance:** A specification with the test-data row MISSING keeps its production tickets out of READY, and `gov readiness --generate` creates one ticket per required open row with its dependencies.
- **Wave:** W2 (schema, checker and the READY gate are W1 (W1-12, W1-13); generating work from gaps is W2)
- **Provider:** OpenSpec custom schema, W1-12, W1-13, W2: gov readiness --generate
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate H2, H3, H4; Framework v4.1.2 §37, §38, §39; DEC-005; DEC-064; DEC-085
- **Scenarios:** dev MR-A-02, MR-A-04, A-01 · qual MR-A-Q02, MR-A-Q04, CHAOS-A-Q07, A-Q01, A-Q02, A-Q05, AUDIT-A-Q32, AUDIT-A-Q35, AUDIT-A-Q37, AUDIT-A-Q43, AUDIT-A-Q44, AUDIT-A-Q47 (+9 not listed in the matrix row)

### CAP-31 — Unified task DAG with dynamic generation

- **Outcome:** An agent works from one task DAG in git, and failures generate their own repair tasks.
- **Acceptance:** A failed `gov close` creates a repair ticket that depends on the failed one, and `tk ready` shows it only after its dependencies are closed.
- **Wave:** W1
- **Provider:** ticket v0.3.2, W1-09, W1-14, W1-30
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate I1, I2, I3, I4; Framework v4.1.2 §41-44; DEC-074
- **Scenarios:** dev MR-A-02, MR-A-03, MR-A-04, A-03, A-04, MR-B-02, MR-B-03, MR-B-04, CHAOS-B-05, CHAOS-B-06, GATE-B-01, AUDIT-B-05 (+2 not listed in the matrix row) · qual MR-A-Q02, MR-A-Q03, MR-A-Q04, GATE-A-Q04, A-Q01, A-Q02, AUDIT-A-Q28, AUDIT-A-Q29, AUDIT-A-Q30, AUDIT-A-Q31, AUDIT-A-Q32, MR-B-Q04 (+2 not listed in the matrix row)

### CAP-32 — Research and experiment lifecycle

- **Outcome:** An agent keeps research as evidence records separate from authority, and experimental results cannot reach production unreviewed.
- **Acceptance:** A research record marked EXPERIMENTAL cited by a production change makes `gov check` fail until a decision promotes it.
- **Wave:** W3
- **Provider:** Docling (pinned), MarkItDown, W3: gov research sync + research records
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate J1, J2; Framework v4.1.2 §45, §46; DEC-019; DEC-020
- **Scenarios:** dev A-X-02 · qual AUDIT-A-Q02, AUDIT-A-Q06, AUDIT-A-Q20, AUDIT-A-Q21, AUDIT-A-Q23, AUDIT-A-Q24, AUDIT-A-Q38, AUDIT-A-Q43, CIT-B-Q01

### CAP-33 — Change-impact transactions (CIT-P simulation, CIT-E execution)

- **Outcome:** An agent can simulate a change before making it (CIT-P) and record what it changed (CIT-E).
- **Acceptance:** A decision change raises a CIT-P listing the affected specs, decisions, tickets, tests and code from both graphs, with a radius; after apply/archive the CIT-E record matches the proposal or lists the differences.
- **Wave:** W2 (OpenSpec proposal and apply/archive in W1; computed impact W2)
- **Provider:** OpenSpec 1.13.2, W1-35, W2: gov impact
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate K1, K2, K3, K4; Framework v4.1.2 §47-49; DEC-005 (proportionality profiles LITE/STANDARD/FULL); DEC-035 (radius-scaled budgets/facets); DEC-011; DEC-066
- **Scenarios:** dev MR-A-05, CIT-A-01, CIT-A-02, MR-B-05, CIT-B-01 · qual MR-A-Q05, CHAOS-A-Q01, CHAOS-A-Q02, CHAOS-A-Q05, CIT-A-Q01, CIT-A-Q02, CIT-A-Q03, A-Q03, AUDIT-A-Q26, AUDIT-A-Q27, AUDIT-A-Q39, SOAK-X-Q01

### CAP-34 — Human decision gates and contradiction resolution

- **Outcome:** The owner receives every question that matters as a ranked decision package in the active chat, and independent branches keep going.
- **Acceptance:** A high-impact contradiction produces a package with all eight fields in chat; the dependent ticket is blocked; an independent ticket still reaches close; the answer lands as a register entry in git.
- **Wave:** W1
- **Provider:** W1-34, W1-35
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate L1, L2, L3, L4; Framework v4.1.2 §50-54; DEC-044 (at most two review-repair rounds then DELETE/NARROW/DEFER); DEC-065
- **Scenarios:** dev MR-A-03, CHAOS-A-06, CHAOS-A-07, CHAOS-A-08, CHAOS-A-15, GATE-A-01, MR-B-03, CHAOS-B-06, CHAOS-B-07, CHAOS-B-08, GATE-B-01, GATE-B-02 (+2 not listed in the matrix row) · qual MR-A-Q03, CHAOS-A-Q13, GATE-A-Q01, GATE-A-Q02, GATE-A-Q03, GATE-A-Q04, A-Q01, MR-B-Q05, AUDIT-B-Q01, AUDIT-B-Q05, AUDIT-B-Q08, AUDIT-B-Q14 (+6 not listed in the matrix row)

### CAP-35 — Model routing (T0-T3 tiers, reasoning levels)

- **Outcome:** The owner can route each role and task class to a model tier.
- **Acceptance:** With the routing configuration set, an orchestration task runs on the T3 tier and a documentation task on T1, as recorded in telemetry.
- **Wave:** W3
- **Provider:** W3: role model tiers + routing config
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate M1, M2, M3; Framework v4.1.2 §55-57; DEC-010; DEC-018; DEC-083
- **Scenarios:** dev CHAOS-A-04, ISO-X-03 · qual CHAOS-X-Q06

### CAP-36 — Empirical model routing telemetry

- **Outcome:** The owner can compare cost and pass/fail per model per task class from real runs.
- **Acceptance:** A report lists tokens, cost and pass/fail per model per task class over the recorded tickets.
- **Wave:** W3
- **Provider:** W3: OTel evidence per role and model
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate M4; Framework v4.1.2 §58; DEC-026
- **Scenarios:** dev SOAK-X-01 · qual SOAK-X-Q01

### CAP-37 — Structured checkpoints and mandatory triggers

- **Outcome:** An agent can resume after compaction, a crash or a model switch from a structured checkpoint in the repository.
- **Acceptance:** After every ticket transition a checkpoint file exists; a fresh session with only SessionStart output resumes the ticket at the recorded next step.
- **Wave:** W1 (model-switch continuity tested in W2)
- **Provider:** W1-25, W1-29
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate N1, N2, N3, N4; Framework v4.1.2 §59-61; OWNER-DIRECTION-BR-0004 (checkpoint discipline); OWNER-DIRECTION-BR-0006 §7, §8; DEC-025
- **Scenarios:** dev CHAOS-A-01, CHAOS-A-04, ISO-X-01, ISO-X-03, CHAOS-X-02 · qual CHAOS-A-Q01, CIT-A-Q02, CIT-A-Q04, SOAK-A-Q01, A-Q03, AUDIT-A-Q36, CHAOS-B-Q01, CHAOS-B-Q03, CHAOS-B-Q04, CHAOS-B-Q05, CHAOS-B-Q10, CHAOS-B-Q11 (+6 not listed in the matrix row)

### CAP-38 — Verification test families (product and governance)

- **Outcome:** The owner can see product and governance verification results, with builder tests counted as regression evidence only.
- **Acceptance:** `gov check` reports each governance test family RED/YELLOW/GREEN, and `gov close` runs the independent acceptance tests separately from builder tests.
- **Wave:** W1
- **Provider:** W1-26, W1-30, W1-37
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate O1, O2, O3, O4; Framework v4.1.2 §62-64; DEC-042 (builder tests are regression evidence only); DEC-083
- **Scenarios:** dev MR-A-06, A-02, MR-B-02, MR-B-04, MR-B-06, AUDIT-B-04, AUDIT-X-01 · qual AUDIT-A-Q08, A-Q05, AUDIT-A-Q40, AUDIT-A-Q41, AUDIT-A-Q46, AUDIT-B-Q02, AUDIT-X-Q01

### CAP-39 — Governance health scheduler (G0-G6 tiers)

- **Outcome:** Governance checks run at the right tier automatically, and a stale required index blocks close.
- **Acceptance:** `gov close` fails when a required index is stale; the scheduler runs the configured tiers on schedule and records results.
- **Wave:** W3 (G0–G5 tiers in W1 (W1-40); the health scheduler and G6 (in qualification) are W3)
- **Provider:** lefthook 2.1.15, GitHub Actions, W1-40, W3: health scheduler
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate O5; Framework v4.1.2 §62-64; DEC-007; DEC-075; DEC-087
- **Scenarios:** dev ISO-X-02, SOAK-X-02, MR-X-02 · qual ISO-X-Q02, SOAK-X-Q02, MR-X-Q02

### CAP-40 — Execution telemetry and organisational questions

- **Outcome:** The owner can see tokens, model, cost and outcome per ticket.
- **Acceptance:** Each closed ticket has a telemetry record with fresh input/output tokens, cache reads, model, governance tokens and pass/fail.
- **Wave:** W1 (OTel dashboards W3)
- **Provider:** ccusage (pinned), W1-31
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate P1, P2; Framework v4.1.2 §65, §66; DEC-026; DEC-086
- **Scenarios:** dev CHAOS-A-12, ISO-X-03, SOAK-X-01 · qual GATE-B-Q01, GATE-B-Q03, GATE-B-Q04, SOAK-X-Q01

### CAP-41 — Lesson records with scope

- **Outcome:** An agent receives the lessons that apply to its task, scoped, and lessons stay in the repository.
- **Acceptance:** A committed lesson whose scope matches a ticket is returned by `gov retrieve` for that ticket and not for an out-of-scope ticket.
- **Wave:** W1 (upstream export excluded (DEC-053 Q7))
- **Provider:** W1-08, W1-21
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate Q1, Q2, Q3, Q4; Framework v4.1.2 §67, §68, §75E-75G; Distribution Protocol v1.2 §13-15; DEC-053
- **Scenarios:** dev RETR-X-04, B-X-02 · qual GATE-B-Q01, GATE-B-Q02, AUDIT-B-Q16, AUDIT-B-Q27, RETR-X-Q04

### CAP-42 — Legacy governance retirement and archive policy

- **Outcome:** An agent can retire a repository's legacy governance (rules files, memory, indexes) into archived, inactive state.
- **Acceptance:** After adoption, the retired system contributes zero ACTIVE decisions and zero loaded instructions; its files are archived or imported into `.rulesync/`.
- **Wave:** W1
- **Provider:** rulesync 24.0.0 (import), W1-41
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate R1, R2, R3; Framework v4.1.2 §69-71; DEC-022; DEC-074
- **Scenarios:** dev CHAOS-B-07, B-01, B-04, B-07, B-11, GATE-B-02 · qual B-X-Q02

### CAP-43 — Canonical OS repo separation and immutable releases

- **Outcome:** The owner can tell exactly which Gov OS version a repository runs; releases never change once tagged.
- **Acceptance:** `framework.lock` records the template tag, commit and file-hash manifest, and `gov doctor` fails when any of them disagrees with the installed kernel.
- **Wave:** W1 (Release 1 tag at the end of qualification)
- **Provider:** Copier 9.18.2, W1-39
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S1, S2; Framework v4.1.2 §75A-75D; Distribution Protocol v1.2 §1-8; DEC-023; DEC-027; DEC-064
- **Scenarios:** dev CHAOS-X-01 · qual CHAOS-X-Q01

### CAP-44 — gov init and gov adopt lifecycle

- **Outcome:** The owner can install the Gov OS into a new or existing repository with one command sequence.
- **Acceptance:** `copier copy` plus the post-copy tasks create `governance/`, the overlay, `.rulesync/`, hooks and `framework.lock`, and `gov doctor` passes on the result.
- **Wave:** W1
- **Provider:** Copier 9.18.2, W1-39, W1-41
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S3, S4; Framework v4.1.2 §77-79; Adoption Protocol v3.0 §2-16; Distribution Protocol v1.2 §9, §10; DEC-006; DEC-023
- **Scenarios:** dev B-01, B-04, B-05, B-X-01 · qual B-X-Q01

### CAP-45 — gov update lifecycle

- **Outcome:** The owner can update the Gov OS in a repository without losing overlay configuration.
- **Acceptance:** `gov update --check` reports the version change and migrations; `copier update` applies them with the overlay files unchanged and `gov doctor` green.
- **Wave:** W2 (first real `copier update` in W2)
- **Provider:** Copier 9.18.2, W2: gov update --check
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-023
- **Scenarios:** dev CHAOS-A-10, CHAOS-X-01 · qual CHAOS-X-Q01

### CAP-46 — Cross-machine sync via git

- **Outcome:** The owner can move to another machine with git alone.
- **Acceptance:** A fresh clone followed by `gov doctor` and `gov rebuild` gives a working environment whose derived digest equals the source machine's.
- **Wave:** W1
- **Provider:** W1-27
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S6; Framework v4.1.2 §83; Distribution Protocol v1.2 §16; DEC-057
- **Scenarios:** dev CHAOS-A-09, ISO-X-01, CHAOS-X-01 · qual ISO-X-Q01

### CAP-47 — Independent adoption/audit roles and fresh-session independence

- **Outcome:** The owner gets independent verification from fresh sessions that did not build what they check.
- **Acceptance:** A fresh verifier session with only the bounded context pack runs held-out tests and reports; its transcript contains no builder chat.
- **Wave:** W3 (Independent Test Designer and Independent Auditor roles in W1 (W1-33); full independent adoption/audit roles W3)
- **Provider:** W1-33, W3: independent adoption/audit roles
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate T1, T2, T3; Adoption Protocol v3.0 §3; DEC-042 (builder tests are regression, not certification); DEC-066; DEC-070
- **Scenarios:** dev AUDIT-X-01 · qual AUDIT-X-Q01

### CAP-48 — Framework health SLOs and healthy-repo definition

- **Outcome:** The owner can see the Gov OS's health against SLOs.
- **Acceptance:** `gov health` shows index freshness, test status and governance share as G/Y/R against configured SLOs.
- **Wave:** W3 (subset in `gov doctor` from W1)
- **Provider:** W1-27, W3: health SLOs
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate U; Framework v4.1.2 §75, §76; DEC-004
- **Scenarios:** dev SOAK-X-02 · qual SOAK-X-Q02

### CAP-49 — Qualification oracle (synthetic repos, fault injection, hidden tests)

- **Outcome:** The owner can qualify the Gov OS on two synthetic programmes against a held-out oracle before Release 1.
- **Acceptance:** A fresh qualification executor runs both qualification tiers and produces a scorecard in SCORECARD_FORMAT; any forbidden outcome fails; the builder sessions had no read access to the oracle.
- **Wave:** W3 (the pack exists (S0b1); executed as qualification after W3 (DEC-067))
- **Provider:** synthetic Programmes A and B, held-out oracle, qualification executor
- **Disposition:** KEPT (DROP in S0a; KEPT as qualification by DEC-067)
- **Sources:** Contract v3 Gate V1, V2, V3, V4; DEC-067; DEC-071
- **Scenarios:** dev — · qual —

### CAP-50 — Artifact flow, dependency consumption and end-to-end traceability

- **Outcome:** An agent can tell which evidence becomes stale when a requirement changes.
- **Acceptance:** Changing a requirement marks every dependent test result, packet and synthesis note stale, listed by id.
- **Wave:** W3 (trailers and graph in W1; full W1–W12 in W3)
- **Provider:** W1-10, W1-30, W3: Gate W traceability
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate W1-W12; Framework v4.1.2 §36-38; DEC-036; DEC-064
- **Scenarios:** dev A-X-01 · qual CHAOS-X-Q02, A-X-Q01

### CAP-51 — Decisions register (structured, versioned, authoritative)

- **Outcome:** An agent can rely on one structured, versioned register of decisions with supersession.
- **Acceptance:** Superseding a decision updates both records' status and links, and the checker flags an ACTIVE record that is superseded, a duplicate id or a cycle.
- **Wave:** W1
- **Provider:** MADR + check-jsonschema 0.38.2, W1-11
- **Disposition:** KEPT
- **Sources:** Framework v4.1.2 §2, §68; Contract v3 Gate C1 (decisions); Contract v3 Gate L1 (contradiction resolution); DEC-030 (authority/current/superseded filtering); DEC-012; DEC-074
- **Scenarios:** dev CHAOS-B-08, B-02, RETR-B-01, AUDIT-B-01, AUDIT-B-02, AUDIT-B-05, AUDIT-B-06 · qual MR-A-Q06, AUDIT-A-Q03, AUDIT-A-Q06, AUDIT-A-Q10, AUDIT-A-Q21, AUDIT-A-Q24, MR-B-Q05, GATE-B-Q03, AUDIT-B-Q01, AUDIT-B-Q04, AUDIT-B-Q05, AUDIT-B-Q06 (+7 not listed in the matrix row)

### CAP-52 — Model-agnostic adapters (provider, IDE, CLI)

- **Outcome:** The owner can use Claude Code or an AGENTS.md-reading harness with the same rules, generated from one source.
- **Acceptance:** `rulesync generate` produces CLAUDE.md, AGENTS.md and `.claude/`; CI fails when a generated file differs from its source; the Claude Code adapter carries every hook and deny rule.
- **Wave:** W1
- **Provider:** rulesync 24.0.0, W1-38
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A1 (model-agnostic); Framework v4.1.2 §4, §22; OWNER-LAUNCHER-BR-0001 (Claude Code first, others later); DEC-022; DEC-074
- **Scenarios:** dev ISO-X-03 · qual CHAOS-X-Q06

### CAP-53 — Proportionality profiles (LITE/STANDARD/FULL)

- **Outcome:** The owner gets ceremony in proportion to impact: LITE, STANDARD or FULL.
- **Acceptance:** An R0 change runs only the LITE checks and an R3 change raises the FULL gate and readiness rows, with the profile computed by `gov impact`.
- **Wave:** W2 (declared per ticket in W1 (W1-09); computed from impact in W2)
- **Provider:** W1-09, W2: gov impact profile
- **Disposition:** KEPT
- **Sources:** DEC-005 (proportionality profiles); DEC-035 (radius-scaled budgets/facets); DEC-004 (governance overhead budget 10-15%); OWNER-DIRECTION-P2-0009 §11; DEC-085
- **Scenarios:** dev MR-X-02 · qual MR-X-Q02

### CAP-54 — Progressive adoption (day-one to maturity)

- **Outcome:** The owner can govern a repository from day one while its full migration continues in batches.
- **Acceptance:** A repository with only the kernel installed passes `gov doctor` at the minimal level, and later adoption batches raise its level without reinstalling.
- **Wave:** W1
- **Provider:** W1-39, W1-41, W1-27
- **Disposition:** KEPT
- **Sources:** DEC-006 (progressive adoption); OWNER-DIRECTION-P2-0009 §2 (simplification principle); Framework v4.1.2 §7 (every mature repo should identify systems, even minimally)
- **Scenarios:** dev B-X-01 · qual B-X-Q01

### CAP-55 — Retrieval stopping reasons

- **Outcome:** An agent always knows why retrieval stopped, and an empty result is never taken as absence.
- **Acceptance:** Every evidence bundle carries one stopping reason from the fixed list; a canary miss on an index yields FACET_UNAVAILABLE, and the validator rejects a bundle without a stopping reason.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-21, W1-22
- **Disposition:** KEPT
- **Sources:** DEC-034 (stopping reasons); DEC-037 (zero-result canaries); OWNER-DIRECTION-BR-0005 §5; DEC-080
- **Scenarios:** dev RETR-X-02 · qual RETR-X-Q02

### CAP-56 — Retrieval in disposable subagent context

- **Outcome:** An agent keeps retrieval out of its own context: facet retrieval runs in disposable subagents and only the cited bundle returns.
- **Acceptance:** On RETR-X-02 the main session's transcript contains the bundle and none of the intermediate retrieval batches.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-36
- **Disposition:** KEPT
- **Sources:** DEC-032 (retrieval loop in disposable subagent); DEC-031 (two budgets: retrieval spend vs final packet); DEC-080
- **Scenarios:** dev CHAOS-A-11, RETR-X-02 · qual CHAOS-B-Q06, CHAOS-B-Q07, CHAOS-B-Q08, CHAOS-B-Q09, RETR-X-Q02

### CAP-57 — Deterministic worklist closure for facets

- **Outcome:** An agent gets the same dependency closure for referenced ids every time, with no model involved.
- **Acceptance:** `gov closure` over the same commit and depth returns byte-identical output on repeated runs and reports DEPTH_LIMIT_REACHED with the gap list when the depth is hit.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-20
- **Disposition:** KEPT
- **Sources:** DEC-033 (deterministic worklist closure over referenced IDs); DEC-036 (synthesis notes with deterministic citation check); DEC-080
- **Scenarios:** dev RETR-X-03 · qual RETR-X-Q03

### CAP-58 — Path guards as default-deny allow-lists

- **Outcome:** An agent can write only inside its task's declared paths; everything else is denied.
- **Acceptance:** An Edit, Write or Bash write outside the ticket's `allowed_paths` is refused by the guard; a Bash form the guard cannot parse is caught by the post-command containment check.
- **Wave:** W1
- **Provider:** W1-02, W1-03
- **Disposition:** KEPT
- **Sources:** DEC-041 (default-deny allow-lists, derived not enumerated); DEC-076
- **Scenarios:** dev MR-A-01, CHAOS-A-13, CHAOS-A-14, MR-B-01, CHAOS-B-13, CHAOS-B-14, CHAOS-B-15, A-X-02 · qual MR-A-Q01, SEC-A-Q02, AUDIT-A-Q49, SEC-A-Q06, MR-B-Q02, SOAK-X-Q02

### CAP-59 — Review-repair loop budget

- **Outcome:** The owner never sees a surface loop: after two review→repair rounds the default is DELETE, NARROW or DEFER.
- **Acceptance:** A third review round on the same surface is refused by `gov close` unless an owner ADR authorises it, and the ticket shows the DELETE/NARROW/DEFER proposal.
- **Wave:** W1
- **Provider:** W1-30
- **Disposition:** KEPT
- **Sources:** DEC-044 (at most two rounds then DELETE/NARROW/DEFER); OWNER-DIRECTION-P2-0009 §2 (simplification principle)
- **Scenarios:** dev MR-X-03 · qual MR-X-Q03

### CAP-60 — Below-floor recovery (break-glass)

- **Outcome:** (none — non-goal)
- **Acceptance:** No kernel file implements break-glass or DEGRADED-mode recovery; the wave-exit audit finds none (DEC-070).
- **Wave:** NONE (dropped)
- **Provider:** none (non-goal)
- **Disposition:** DROP — Non-goal: below-floor recovery, break-glass and DEGRADED mode rest on the signed-release-root chain, which is not built (ADR-0001).
- **Sources:** OWNER-DECISION-0006; OWNER-DECISION-0007; DEC-039
- **Scenarios:** dev — · qual —
