---
id: CONTRACT-v5
status: PROPOSED
version: "5.0"
revised: 2026-11-18
depends_on: [CHARTER-v6, ADR-0001, ADR-0002]
decisions: [DEC-064, DEC-065, DEC-074, DEC-075, DEC-078, DEC-080, DEC-083, DEC-085, DEC-086, DEC-087, DEC-088, DEC-089, DEC-090, DEC-091, DEC-092, DEC-093, DEC-094, DEC-095, DEC-096, DEC-102, DEC-103, DEC-104, DEC-105, DEC-106, DEC-119, DEC-136, DEC-137, DEC-138, DEC-150, DEC-151, DEC-152, DEC-153, DEC-154, DEC-155, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162, DEC-163, DEC-164, DEC-165, DEC-166, DEC-167, DEC-168, DEC-169, DEC-170, DEC-171, DEC-172, DEC-173, DEC-174, DEC-409, DEC-722, DEC-741, DEC-836, DEC-848, DEC-906, DEC-1007, DEC-1030, DEC-1052, DEC-1065, DEC-1089, DEC-1090, DEC-1093, DEC-1116, DEC-1120, DEC-1149, DEC-1182, DEC-1200, DEC-1204, DEC-1207, DEC-1210, DEC-1211, DEC-1212, DEC-1213, DEC-1214]
type: specification
state_class: AUTHORITATIVE
---

# Governance OS — Capability Acceptance Contract v5 (version 5.0)

Contract v5 states what the Gov OS must do, as outcomes with **one observable acceptance check each**. It replaces Contract v3 as the working text (DEC-058). `contract.yaml` holds the same content in machine-readable form; `readiness-dimensions.yaml` defines the 26 readiness rows that Wave 1's OpenSpec schema implements.

**Version 5.0** (2026-11-18, status PROPOSED until the owner approves it by group, `docs/emergency-2/G5-APPROVAL.md`). The re-baseline of EMERGENCY-2 (audit 7, DEC-1214 G5): the file is `CONTRACT_v5.md`, the id `CONTRACT-v5`; the text of version 4.4 is in git history.

| Version | Date | Change |
|---|---|---|
| 4.0 | 2026-09-30 | Contract v4 as closed by S1 and audited by S1-A (DEC-083…DEC-096). |
| 4.1 | 2026-10-03 | S2 specification change (docs/changes/S2-CIT-P.md, S2-CIT-E.md). Carries DEC-102…DEC-106, DEC-136, DEC-137 and the outcome of DEC-138 (EXP-001, ADOPT-PARTIAL); applies DEC-150…DEC-162. Envelope: boundary and tool installs extended. MR-3: the orchestrator exception. CAP-58 split between the OS sandbox (a worker session's Bash) and the guard (file tools, the orchestrator session). New CAP-61 (worker session launcher and OS sandbox) and CAP-62 (sandbox escape hatch denied). New covers items in CAP-22, 25, 30, 32, 33, 38, 40, 49 and 58; wave note in CAP-37. 60 → 62 capabilities. Repair after the S2-A round-1 audit, same version: applies DEC-163…DEC-167. New covers items in CAP-22, 25, 32, 33, 41, 45 and 58; CAP-25 acceptance, CAP-41.e, CAP-61.a and CAP-61.f reworded; envelope tool installs names the research role. Second pass of the repair: CAP-41.f moved to W1 on W1-08 (DEC-168); CAP-22.d, 25.e, 49.c, 58.a, 58.b, 58.e and 61.c reworded for S2A-F-01…F-04; CAP-58.e cites DEC-171. Repair after the S2-A round-2 audit, same version: applies DEC-172 (new `CAP-25.f` on W1-47: no install or download ask rule in the committed settings); new `CAP-40.d` on W1-31 carries DEC-170 (S2A-F-15); CAP-25.e, 49.c and 61.c reworded for S2A-F-13 and F-14. DEC-173 changes the Charter only. Round-3 closure check, same version: new `CAP-25.g` on W1-47 (DEC-174: `uv add`, `uv sync`, `uv run --with` and `uvx` are installs). Owner answer during W1-48, same version: CAP-25.d reworded (DEC-209: the Claude Code upgrade is installed by the owner, or by the orchestrator under DEC-083, in both cases recorded with its owner approval). Owner decision during Wave 1, same version: new `CAP-23.c` on W1-42 (DEC-235: parallel tickets in Wave 1, a light form of the Wave 3 concurrency capability). Owner decision during Wave 1, same version: new `CAP-37.g` on the new ticket W1-49 (DEC-248: light auto-resume hooks, a light form of CAP-37). Owner decision during Wave 1, same version: new `CAP-58.h` on the new ticket W1-50 (DEC-255: containment attribution by commit trailers). |
| 4.2 | 2026-10-17 | W2-49 specification change (docs/changes/W2-49-CIT-P.md, W2-49-CIT-E.md), approved by the owner (DEC-741). Carries DEC-722: the adoption verdict (CAP-44.h) and the A7 and A10 gates of CAP-44.f come into Wave 2, lite; the release contents of CAP-43.b come into Wave 2, lite: the manifest and file hashes. What stays in Wave 3 is split into new covers items: CAP-44.k (A9, A11, and A7 and A10 beyond their lite form), CAP-44.l (the verdict with the ten ADOPTED_HEALTHY conditions) and CAP-43.d (the rest of the release contents). CAP-44.h lists the ten ADOPTED_HEALTHY conditions of Adoption Protocol v3.0 §20, each marked W2 or W3, from the named read of Adoption Protocol v3.0 §20 and Distribution Protocol v1.2 §18 the owner allowed for this change (DEC-741 C). CAP-45.a gets a Wave 2 wording: in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3). CAP-02.c (signed release tags) and CAP-43.c stay in Wave 3. Wave notes in CAP-43, CAP-44 and CAP-47. Status ACCEPTED in both files (row W2-L343; DEC-741). No capability changes wave; 62 capabilities; 211 → 214 covers items. |
| 4.3 | 2026-11-09 | W2-27 specification change (docs/changes/W2-27-CIT-P.md, W2-27-CIT-E.md), approved by the owner (DEC-1093). Carries DEC-1089 (2) and DEC-1090 (5): gov update is built in Wave 3, so CAP-45.a moves from Wave 2 to Wave 3, and CAP-45 with it, since no Wave 2 part of it remains. The Wave 2 clause of version 4.2 (in Wave 2 the authenticated source is the release's manifest and file hashes, DEC-741 D) is withdrawn; the manifest and file hashes stay part of the authenticated source, beside the signed tag (CAP-02.c). 62 capabilities (W2 7 → 6, W3 11 → 12); 214 covers items (W2 20 → 19, W3 38 → 39). |
| 4.4 | 2026-11-18 | W2-192 specification change (docs/changes/W2-192-CIT-P.md), approved by the owner (DEC-1213). Carries DEC-1200 (4): the spec audit is a standard adoption stage, AS, after A2 and before A3, lite (CAP-44.m, W2). CAP-44 stays W3. 62 capabilities; 215 covers items (W2 19 → 20). |
| 5.0 | 2026-11-18 | Re-baseline to EMERGENCY-2 (docs/emergency-2/audits/07-contract-rebaseline.md; owner decisions DEC-1214 G5, G6, L3, M1, G7), proposed by group in docs/emergency-2/G5-APPROVAL.md and awaiting the owner's approval. No guard, no sandbox, no box (CAP-58, CAP-61, CAP-62 and their clauses dropped; §2 Boundary rewritten); pause carried by the launch, the dispatcher and the landing (CAP-05); memory in the brief and a fresh 80 at 95 % end to end, `gov context` retired, hit@k a diagnostic (CAP-01, CAP-10, CAP-15, CAP-17.b, CAP-19.c, CAP-48.a, §2 Token budget); the landing and the flow, no repair ticket, two rounds (MR-1 to MR-3, CAP-23.c, CAP-31, CAP-38, CAP-39, CAP-53, CAP-59, §2 Loop budget); a fresh audit only at the release acceptance and at adoption stages A5, AS, A7 and A10 (MR-4, CAP-47.d, CAP-38.f, CAP-24.c, CAP-33.d); the lean release pinned and hash-verified, no signing, `gov update` in the release (CAP-02, CAP-43, CAP-45, CAP-44.f/.h, CAP-49); gitleaks only before a repository goes public (CAP-03, CAP-41.g); the run-time tool and the rubric (CAP-04, CAP-22.b, CAP-23.b, CAP-35, CAP-37, CAP-40); the CTO approves every install (§2 Tool installs, CAP-25); Wave 3 is friction. New CAP-63 to CAP-69 (the landing, the run-time tool, memory by construction, the hidden-set scan, backups, the basis line, transcripts kept). Status PROPOSED until the owner approves. CAP-44.m's leftovers settled: the records' version, DEC-1200 in the decisions list, the source map. 69 capabilities; 239 covers items. |

**Precedence:** Charter v6 → Contract v5 → ADRs → everything else. The ADRs supersede the originals where they conflict.

**Fields:** `outcome` (what an agent or the owner can do) · `acceptance` (one observable check) · `wave` (W1/W2/W3; the wave in which the acceptance check must pass, with earlier partial delivery in `wave_note`) · `provider` (tool or W1 ticket; W2/W3 components are named) · `sources` (Contract v3 gates, Framework sections, owner records, decisions) · `covers` (every carried sub-requirement with its source and wave; each has an id; a Wave 1 item names the ticket whose KPI delivers it, and that KPI line carries the id in brackets; wave-exit audits check each item, DEC-092) · `scenarios` (dev and qual ids from `COVERAGE_MATRIX.md`; where the matrix truncates a list, the count of unlisted ids is given) · `disposition` (KEPT, LITE with its lite form, or DROP with its decision).

## 1. Counts

| Wave | KEPT | LITE | DROP | Total |
|---|---|---|---|---|
| W1 | 37 | 4 | 0 | 41 |
| W2 | 18 | 0 | 0 | 18 |
| W3 | 7 | 0 | 0 | 7 |
| NONE | 0 | 0 | 3 | 3 |
| **All** | 62 | 4 | 3 | 69 |

DEC-080 places CAP-15, 16, 18, 55, 56 and 57 in Wave 1, with the citation validator and hierarchical synthesis. DEC-074 R1/Q3 places semantic retrieval and the reranker (CAP-10) in Wave 1. Version 4.1 added CAP-61 and CAP-62 to Wave 1 (DEC-152, DEC-153). **Version 5.0** (EMERGENCY-2, audit 7): Wave 2 is what the lean release must have and Wave 3 is friction only (EMERGENCY-2 §8.4); CAP-15, 23, 35, 39, 45 and 49 move to Wave 2; CAP-62 becomes a dropped capability like CAP-26 and CAP-60; CAP-58 and CAP-61 keep a few items and drop the rest (Wave NONE); CAP-63 to CAP-69 are new.

## 2. Envelope and boundary

- **Scale envelope** (DEC-078). Tested up to ≈ 80k nodes / 270k edges of code graph at ≈ 2.2 GB peak RSS for codebase-memory-mcp; larger graphs are measured before adoption. Memory scales with graph edges, not file count. Each project in a multi-project folder gets its own index.
- **RAM budget** (DEC-078, DEC-1065, DEC-1211). Worst case ≈ 12.5 GB of the 15.5 GiB host (IDE + local models + a full index run), leaving ≈ 2.5 GiB spare; incremental updates are far smaller. The stack runs with one on-demand daemon (Ollama, 5-min idle unload), no Docker, VRAM peak ≈ 5.2 of 16 GiB. Embedders and rerankers stay resident on the GPU and never spill to the CPU (RT-4); there is no CPU fallback (DEC-1065). Slots come from the CPU, RAM and GPU the run-time tool detects at start, with no machine-specific constant (RT-3).
- **Token budget** (DEC-004, DEC-086, DEC-1211, DEC-1214). Governance tokens ≤ 15 % of a ticket's fresh input + output tokens, reported weekly with its baseline (56 % before EMERGENCY-2) by P1's method until `gov telemetry` measures it (EMERGENCY-2 §10.2, A-7). Governance tokens = text the Gov OS injects or returns (instruction files, the brief, hook output, `gov` output, governance MCP tool definitions, checkpoint and close records), counted by `gov`; the denominator comes from ccusage. Cache reads are reported separately. AGENTS.md ≤ ~1.5k tokens. There is no context packet and no packet ceiling anywhere: `gov context` is retired (DEC-1214 M1), and the brief carries the ticket's retrieval uncut. A breach is a health finding, never a silent cost.
- **Boundary** (DEC-039, DEC-075, DEC-087, DEC-848, DEC-1211). No guard, no sandbox, no box and no permission prompts (EMERGENCY-2 §2). Agents have full permission in the repository, the worktree and the run folder they work in; sessions stay apart by where each starts, the folders it is given and its brief, and nothing enforces it. Mistakes are caught and corrected at the landing and by the transcript scan, not prevented. The hard boundary is git history; the owner's own `git push` and release from his own terminal; two settings deny lines, `git push` and `sudo`, which hold in every permission mode; and an hourly `git bundle` of each repository, kept outside the tree. The landing merges into integration and only the owner pushes. The lefthook pre-push gate G3 on the owner's machine and GitHub Actions CI G4–G5 stay as an advisory result on every push (deterministic checks only; model-dependent tests run at G3 and leave an evidence record bound to the head commit that CI checks). `main` is not protected; enabling protection later changes no other decision.
- **Loop budget** (DEC-044, DEC-096, DEC-1204, DEC-1211). Any loop that runs until convergence (review→repair, audit→repair, test→fix, verification) runs at most two rounds; if the second does not converge there is one escalation package for the owner (each round's outcome, why it is not converging, options: fix differently, narrow, split, defer, delete, continue), and the owner decides once. READY is computed by code from the reviewers' verdict blocks. The round count and budget are held by the orchestrator or gov and never disclosed to the sessions inside the loop. Retrieval stopping rules are unchanged (DEC-034, DEC-080).
- **Tool installs** (DEC-083, DEC-157, DEC-163, DEC-1214). The CTO approves and records every install in the tool registry (tool, exact version, source and checksum, need, disk and RAM, uninstall command), so that nothing out of the work's scope or beyond the machine's capacity is installed; there is no permission prompt, and `sudo` stays with the owner (DEC-1214 G7 (c)). Worker roles never install system-wide.

## 3. Master-rule clauses

The rule texts are in Charter v6 §4, from architecture v0.3 §1A; EMERGENCY-2 reworded the checks of MR-1 to MR-4. Each clause below is a contract item with one acceptance check.

| Id | Rule | Acceptance | Provider | Dev scenarios | Decisions |
|---|---|---|---|---|---|
| MR-1 | Specification comes first | A feature ticket whose specification has a required readiness cell open for its profile (FULL for a spine) cannot reach READY: `tk ready` does not list it and `gov readiness` names the open cells; an N/A without a reason is rejected. READY is computed by code from the template; a fix or a chore has no ticket. | W1-12, W1-13, W1-35, W1-42 | MR-A-02, MR-B-02 | DEC-065, DEC-085, DEC-1052, DEC-1116, DEC-1211 |
| MR-2 | Closed specifications generate the work | A closed specification produces feature tickets with class, role, depends_on, allowed_paths, KPIs and profile, and `gov check` fails a ticket missing any of them; every required open readiness cell has a linked gap ticket (discovery, data, research or test-design) and `gov check` fails an unlinked one — created by the planning skill, generated by `gov discover` (`gov readiness --generate` is folded into it, W2-36). | W1-14, W1-35, W1-13, W1-26, W2-36 (gov discover), W1-09, W1-42 | MR-A-02, MR-A-04, MR-B-02, MR-B-04 | DEC-065, DEC-089, DEC-1211 |
| MR-3 | KPIs; the builder never writes its own acceptance tests | The landing refuses a commit that changes `tests/acceptance/` without `Role: independent-test-designer` (or the owner's `Role: owner`), naming the commit, in the Gov OS repository and in an adopted repository (`gov queue`); a feature ticket is not READY until `tests/acceptance/<ticket-id>/` exists and its tests are red on the base; a breach is a forbidden outcome. | W1-09, W1-30, W1-33, W1-05, W1-26, W1-35, W1-42, W2-115b | MR-A-01, MR-B-01 | DEC-065, DEC-069, DEC-906, DEC-1211 |
| MR-4 | Audit, discovery and impact are distinct functions | The functions stay distinct: each of `gov doctor`, discovery, CIT-P, CIT-E and audit has its own command or skill and record. A fresh auditor that authored none of the audited files runs at the release acceptance and at adoption stages A5, AS, A7 and A10; otherwise a review happens only for a red test, a failed landing or merge, or a feature that does not work as intended, batched when several come together; the audit report names its milestone, and contested or owner-level findings appear in chat as decision packages. | W1-27, W1-13, W1-35, W1-36, W1-33, W1-43, W1-42 | MR-A-05, MR-A-06, MR-B-05, MR-B-06 | DEC-065, DEC-066, DEC-070, DEC-1204, DEC-1214 |
| MR-5 | The Gov OS works as a software company | Each Wave 1 role exists as a generated subagent definition with purpose, allowed-path pattern, tools, model tier, authority level and handoff format, and a ticket's role field names one of them. | W1-33, W1-38 | CHAOS-X-02 | DEC-065, DEC-066 |
| MR-6 | The human is the customer and final authority | Every owner question appears in the active chat as a package with all eight MR-6 fields (the template carries ten), ranked P1–P3 and batched at most five at a time, P1 allowed to bypass; the dependent branch waits while an independent branch proceeds; each answer is committed as a decision record. | W1-34, W1-35, W1-42 | MR-A-03, MR-B-03 | DEC-065, DEC-093 |

## 4. Capabilities

### CAP-01 — Authority precedence and hard invariants

- **Outcome:** An agent can tell which of two conflicting records governs, by a deterministic precedence (Charter → Contract → ADRs → specifications → tasks → retrieval → inference) and by supersession status.
- **Acceptance:** Given two conflicting records at different precedence levels, `gov retrieve` returns the higher one as in force and marks the lower one superseded.
- **Wave:** W1
- **Provider:** MADR + check-jsonschema 0.38.2, W1-10, W1-11, W1-24, W1-26
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A1; Framework v4.1.2 §2, §21; OWNER-CLARIFICATION-P2-0004; DEC-012; DEC-046; DEC-083; EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1
- **Covers:**
  - `CAP-01.a` [W1] Machine-readable precedence: Charter → Contract → ADRs → specifications → tasks → retrieval → inference — Contract v3 A1; Framework v4.1.2 §2, §21 · delivered by W1-24
  - `CAP-01.b` [W1] Project files cannot manufacture authority; approvals are owner git facts — OWNER-CLARIFICATION-P2-0004; DEC-046 · delivered by W1-11
  - `CAP-01.c` [W1] Authority semantics preserved across stages: research cannot silently become a decision, lessons cannot silently become policy, historical material cannot replace current input — Contract v3 W2 · delivered by W1-26
  - `CAP-01.d` [W1] Mandatory authoritative inputs outrank retrieval and are resolved deterministically — Contract v3 W10 · delivered by W1-24
- **Scenarios:** dev MR-A-06, CHAOS-A-13, AUDIT-A-01, MR-B-01, MR-B-06, CHAOS-B-13, AUDIT-B-07 · qual CHAOS-A-Q05, AUDIT-A-Q01, AUDIT-A-Q07, AUDIT-A-Q08, A-Q04, AUDIT-A-Q22, AUDIT-A-Q39, AUDIT-A-Q42, AUDIT-A-Q45

### CAP-02 — Release authenticity (lite: pinned and hash-verified)

- **Outcome:** The owner can confirm that an installed kernel matches a released version.
- **Acceptance:** `gov doctor` reports MATCH for the pinned `framework.lock` manifest against the release's own manifest and file hashes, and DRIFT naming the edited file after a one-byte edit; a release is pinned and hash-verified, and no tag signature is required.
- **Wave:** W1 (manifest check in W1; releases are pinned and hash-verified; a signed tag waits for friction (DEC-1214 L3))
- **Provider:** Copier 9.18.2, W1-39, W1-27
- **Disposition:** LITE — lite form: A file-hash manifest in `framework.lock` and the release's own manifest and file hashes, verified by `gov doctor`; releases pinned and hash-verified; no signing until friction asks for it (DEC-1214 L3); no TUF, key rotation, offline envelopes or bootstrap separation.
- **Sources:** Contract v3 Gate A2; Framework v4.1.2 §75B-75D; Distribution Protocol v1.2 §5-8; OWNER-DIRECTIVE-0004; OWNER-DECISION-0009; OWNER-DECISION-P2-0005; DEC-027; DEC-074; DEC-083; DEC-1214 L3
- **Covers:**
  - `CAP-02.a` [W1] File-hash manifest in framework.lock; gov doctor MATCH/DRIFT — Contract v3 A2 (LITE); Framework v4.1.2 §75B–75D · delivered by W1-39, W1-27
  - `CAP-02.b` [NONE] Non-goal: TUF metadata, key rotation and revocation, offline envelopes, bootstrap-mode separation, unprovisioned-machine trust anchors — DEC-027, DEC-039, OWNER-DECISION-P2-0002
  - `CAP-02.c` [W3] SSH-signed release tag, verified by `git tag -v`: built only if friction asks for it (DEC-1214 L3) — Contract v3 A2 (LITE); Framework v4.1.2 §75B–75D; DEC-027; DEC-1214 L3; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev CHAOS-X-01 · qual CHAOS-X-Q01

### CAP-03 — Security and sensitivity classification

- **Outcome:** An agent can rely on secrets never reaching an index, a brief or an export: the path map's sensitivity classes keep secret-class files out of every index, and one full gitleaks scan runs before a repository goes public or is shared.
- **Acceptance:** After `gov rebuild` on a tree with planted secret-class files (including a token-shaped canary), no planted string appears in any `.gov-runtime/` store, codebase-memory index, brief or evidence bundle; the release steps include one full gitleaks scan before any public push or sharing, and no gitleaks scan runs on a private repository.
- **Wave:** W1
- **Provider:** gitleaks 8.30.1, W1-15, W1-16, W1-01, W1-08, W1-17
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A3; Framework v4.1.2 §16, §72; Distribution Protocol v1.2 §14, §17; DEC-074; DEC-076; EMERGENCY-2 §2.11 (DEC-1211); DEC-1182
- **Covers:**
  - `CAP-03.a` [W1] Sensitivity class per path/dataset/namespace before read, index or export; secret-class paths excluded from every index by default-deny; one full gitleaks scan runs before a repository goes public or is shared — Contract v3 A3; Framework v4.1.2 §16, §72; EMERGENCY-2 §2.11 (DEC-1211); DEC-1182 · delivered by W1-15, W1-08
  - `CAP-03.b` [W1] Development/governance memory separated from customer/runtime product data — Framework v4.1.2 §16 · delivered by W1-15, W1-08
  - `CAP-03.c` [W1] Each namespace declares sensitivity class, permitted roles, retention, export policy, embedding policy, provenance and deletion/rebuild behaviour (path-map namespace fields) — Framework v4.1.2 §16 · delivered by W1-08
  - `CAP-03.d` [W1] Whole-repository corpus minus secrets — OWNER-CLARIFICATION-BR-0002 · delivered by W1-17
  - `CAP-03.e` [W1] Secret exclusion by sensitivity class holds on every retrieval route, including the code route — OWNER-DIRECTION-BR-0003; DEC-076; EMERGENCY-2 §2.11 (DEC-1211); DEC-1182 · delivered by W1-16, W1-15
- **Scenarios:** dev CHAOS-A-14, SEC-A-01, SEC-A-02, SEC-A-03, CHAOS-B-15, SEC-B-01, SEC-B-02, ISO-X-01 · qual CHAOS-A-Q09, RETR-A-Q03, SEC-A-Q01, SEC-A-Q02, SEC-A-Q03, SEC-A-Q04, AUDIT-A-Q49, SEC-A-Q05, SEC-A-Q06, MR-B-Q03, MR-B-Q06, CHAOS-B-Q08 (+9 not listed in the matrix row)

### CAP-04 — Budget and resource governance

- **Outcome:** The owner can see what a ticket costs against its projection, and a ticket that runs away is held once instead of continuing silently.
- **Acceptance:** A ticket whose measured cost passes twice its projection holds its next launch and goes to the inbox once; usage is recorded and reported weekly and never holds, refuses or stops a lead or a worker (W2-156, DEC-1149 (3)).
- **Wave:** W2 (W1 measures the governance share (W1-31); the runaway brake is W2 (W2-156); budgets per task wait for friction (EMERGENCY-2 §6.2 A-1))
- **Provider:** ccusage (pinned, DEC-086), W1-31, W2-156 (the runaway brake), W1-21
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A4; Framework v4.1.2 §73; OWNER-DIRECTION-P2-0009 §11 (10-15% overhead target); DEC-004, DEC-031; DEC-083; DEC-086; DEC-1149; EMERGENCY-2 §6.2 A-1, §10.2 (DEC-1211)
- **Covers:**
  - `CAP-04.a` [W3] Token/cost budgets per task with executable thresholds (built only if friction asks; until then the run-time tool's spend brake covers it, EMERGENCY-2 §6.2 A-1) — Contract v3 A4; Framework v4.1.2 §73; EMERGENCY-2 §6.2 A-1 (DEC-1211); EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-04.b` [W1] Governance share ≤ 15 %, reported weekly with its baseline (56 %), by P1's method until `gov telemetry` measures it (DEC-086; EMERGENCY-2 §10.2, A-7) — OWNER-DIRECTION-P2-0009 §11; DEC-004; EMERGENCY-2 §10.2 (DEC-1211) · delivered by W1-31
  - `CAP-04.c` [W1] Retrieval spend budget scaled by impact radius; hitting it is a governed event, never silent truncation; there is no packet ceiling (the final-packet budget of DEC-031 is superseded by EMERGENCY-2 §5.5) — DEC-031; EMERGENCY-2 §5.5 (DEC-1211) · delivered by W1-21
  - `CAP-04.d` [W3] Exceeding a delegated limit raises a decision package (built only if friction asks; until then the run-time tool's spend brake covers it, EMERGENCY-2 §6.2 A-1) — Contract v3 A4; EMERGENCY-2 §6.2 A-1 (DEC-1211); EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev SOAK-X-01 · qual SOAK-X-Q01

### CAP-05 — Emergency controls (pause/freeze/cancel/rollback)

- **Outcome:** The owner can stop the work with one command and resume it, and roll back by `git revert`.
- **Acceptance:** After `gov pause`, `gov launch` and the dispatcher start no session, the landing lands nothing, and every running session gets a stop message in its inbox; `gov pause --off` restores all three and `git status --porcelain` is unchanged.
- **Wave:** W1 (the freeze flag and `gov pause` are W1; its readers (launch, dispatch, landing) are a fix recorded in W1-28)
- **Provider:** W1-28, the flag's readers in `gov launch`, the dispatcher and the landing: a fix to W1-28's feature (EMERGENCY-2 §4.2; audit 7 C-1)
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A5; Framework v4.1.2 §74; DEC-025; EMERGENCY-2 §9.2 (DEC-1211); DEC-409
- **Covers:**
  - `CAP-05.a` [W1] PAUSE and FREEZE (`gov pause`): the freeze flag stops launches, dispatcher ticks and landings and sends a stop message to every running session; `--off` lifts all three, and only the owner in person lifts (DEC-409) — Contract v3 A5; Framework v4.1.2 §74; EMERGENCY-2 §9.2 (DEC-1211) · delivered by W1-28
  - `CAP-05.b` [W1] CANCEL_AGENTS: stop running subagents and release their claims — Contract v3 A5; Framework v4.1.2 §74 · delivered by W1-28
  - `CAP-05.c` [W1] ROLLBACK_TRANSACTION: git revert of the ticket's commits, recorded — Contract v3 A5; Framework v4.1.2 §74 · delivered by W1-28
  - `CAP-05.d` [W1] Emergency commands deterministic and owner-gated; recovery auditable (recorded in the ticket) — Contract v3 A5 · delivered by W1-28
- **Scenarios:** dev CHAOS-A-10, CHAOS-A-15 · qual CHAOS-X-Q04

### CAP-06 — Repository contract and path map

- **Outcome:** An agent can find where every kind of artefact lives from the committed path map, and nothing material is unclassified.
- **Acceptance:** `gov doctor` reports zero unclassified tracked paths against `governance/project/path-map.yaml`, and names each path when one is added outside the map.
- **Wave:** W1
- **Provider:** W1-08, W1-27, W1-41
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate B1, B2; Framework v4.1.2 §8, §9; Adoption Protocol v3.0 §8; OWNER-DECISION-P2-0008 §2 (project-specific floor); DEC-060; DEC-041
- **Covers:**
  - `CAP-06.a` [W1] Every material artefact classified by current path, class, authority and intended target — Contract v3 B1, B2; Framework v4.1.2 §8, §9 · delivered by W1-27, W1-08
  - `CAP-06.b` [W1] Target actions KEEP/MOVE/RENAME/SPLIT/MERGE/EXTRACT/RETIRE/DELETE_FROM_ACTIVE_TREE — Contract v3 B2 · delivered by W1-41
  - `CAP-06.c` [W1] Unknown material artefacts block destructive migration — Contract v3 B2 · delivered by W1-41
  - `CAP-06.d` [W1] Imports/references/consumers represented; path-map compliance machine-checkable — Contract v3 B2 · delivered by W1-41, W1-27
  - `CAP-06.e` [W1] Project-specific floor in the overlay — OWNER-DECISION-P2-0008 §2 · delivered by W1-08
- **Scenarios:** dev B-01, B-02, B-03, B-04, B-05, B-08, B-09, B-11, AUDIT-B-03, AUDIT-B-07, SEC-B-01, SEC-B-02 (+2 not listed in the matrix row) · qual MR-B-Q06, SEC-B-Q02, B-Q01, B-Q02, B-Q03, AUDIT-B-Q18, AUDIT-B-Q23, AUDIT-B-Q38, ISO-X-Q01, B-X-Q01

### CAP-07 — Authoritative vs derived state separation

- **Outcome:** An agent can delete all derived state without losing anything authoritative.
- **Acceptance:** Deleting `.gov-runtime/` leaves `git status --porcelain` empty, and `gov rebuild` restores every derived store.
- **Wave:** W1
- **Provider:** W1-17, W1-27, W1-08
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate B3; Framework v4.1.2 §10, §12, §19; DEC-057
- **Covers:**
  - `CAP-07.a` [W1] Authoritative state in git; derived state rebuildable and gitignored — Contract v3 B3; Framework v4.1.2 §10, §12, §81 · delivered by W1-27
  - `CAP-07.b` [W1] State classes recorded per record (state_class convention) — Framework v4.1.2 §3; DEC-046 · delivered by W1-08
- **Scenarios:** dev CHAOS-A-02, CHAOS-B-02, CHAOS-B-10, B-03, B-06, ISO-X-01, ISO-X-02 · qual CHAOS-A-Q03, CHAOS-A-Q06, CHAOS-A-Q08, RETR-A-Q04, SOAK-A-Q01, SOAK-A-Q02, SOAK-A-Q03, AUDIT-A-Q33, AUDIT-A-Q34, ISO-X-Q01, ISO-X-Q02

### CAP-08 — Deterministic structured memory (records)

- **Outcome:** An agent can ask exact structured questions over records (status, type, owner, links) and get exact answers.
- **Acceptance:** A query for ACTIVE decisions returns exactly the set whose frontmatter status is ACTIVE and that nothing supersedes.
- **Wave:** W1
- **Provider:** W1-10, W1-08
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C1; Framework v4.1.2 §11.1; DEC-012
- **Covers:**
  - `CAP-08.a` [W1] Exact structured queries over records (status, type, owner, links) — Contract v3 C1; Framework v4.1.2 §11.1 · delivered by W1-10
- **Scenarios:** dev RETR-A-02, ISO-X-01 · qual AUDIT-A-Q01, AUDIT-A-Q03, A-Q04, AUDIT-A-Q10, AUDIT-A-Q45, ISO-X-Q01

### CAP-09 — Relationship/graph memory

- **Outcome:** An agent can traverse implements, validates, supersedes and depends_on links across all record types, including broken ones.
- **Acceptance:** For a fixture record set, the graph returns every IMPLEMENTS and VALIDATES edge of a requirement and reports each dangling reference by id.
- **Wave:** W1
- **Provider:** W1-10, W1-20
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C2; Framework v4.1.2 §11.2; DEC-012; DEC-080
- **Covers:**
  - `CAP-09.a` [W1] Typed edges EVIDENCE_FOR, CONSTRAINS, IMPLEMENTS, TESTS, GENERATES, VALIDATES, SUPERSEDES, DEPENDS_ON — Contract v3 C2, W2; Framework v4.1.2 §11.2 · delivered by W1-10
  - `CAP-09.b` [W1] Dangling references reported by id — Contract v3 C2 · delivered by W1-10
- **Scenarios:** dev MR-B-05, CHAOS-B-11, CHAOS-B-12, B-09, RETR-B-04, CIT-B-01, AUDIT-B-01, AUDIT-B-02, AUDIT-B-04, A-X-01, RETR-X-05 · qual MR-A-Q06, CHAOS-A-Q11, RETR-A-Q02, AUDIT-A-Q03, AUDIT-A-Q34, RETR-B-Q01, RETR-B-Q02, RETR-B-Q03, RETR-B-Q04, AUDIT-B-Q03, B-Q04, AUDIT-B-Q13 (+9 not listed in the matrix row)

### CAP-10 — Semantic memory (vector/embedding retrieval)

- **Outcome:** An agent can find a record from a paraphrased question.
- **Acceptance:** A fresh 80 (40 visible questions, 40 hidden), written and measured at once on a pinned snapshot, is judged end to end at 95 % or more: the reader reads the whole ranked bundle and searches once more in its own words, and both the answer and its citation must be right; the hidden half's figure is the verdict. hit@k is a diagnostic only, never a target or a floor.
- **Wave:** W1 (moved from W2 by DEC-074 R1/Q3 and DEC-080)
- **Provider:** Ollama 0.35.0 + qwen3-embedding:0.6b, sqlite-vec 0.1.9, W1-19
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C3; Framework v4.1.2 §11.3, §14; OWNER-DIRECTION-BR-0006 §1, §5 (provisional BGE, replaceable); OWNER-CLARIFICATION-BR-0002 (whole-repo corpus); DEC-016; DEC-017; DEC-074; DEC-080; DEC-1210; EMERGENCY-2 §5.2, §5.3 (DEC-1211)
- **Covers:**
  - `CAP-10.a` [W1] Paraphrase retrieval with pinned embedder (Qwen3-Embedding-0.6B via Ollama) — Contract v3 C3; Framework v4.1.2 §11.3, §14; DEC-074 · delivered by W1-19
  - `CAP-10.b` [W2] Embedder replaceable (provisional choice) — OWNER-DIRECTION-BR-0006 §5
- **Scenarios:** dev RETR-A-01, RETR-A-02, CHAOS-B-11, B-11, RETR-B-01, RETR-B-02, AUDIT-B-06, ISO-X-01, RETR-X-05 · qual B-Q05, AUDIT-B-Q26, AUDIT-B-Q28, AUDIT-B-Q29, AUDIT-B-Q31, AUDIT-B-Q32, AUDIT-B-Q40, ISO-X-Q01

### CAP-11 — Lexical memory (FTS/BM25)

- **Outcome:** An agent can find exact strings, identifiers and error messages with file and line.
- **Acceptance:** An exact error-string query returns the file path and line number of every occurrence in the indexed tree.
- **Wave:** W1
- **Provider:** SQLite FTS5 (carried), W1-17
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C4; Framework v4.1.2 §11.4; DEC-016; DEC-074
- **Covers:**
  - `CAP-11.a` [W1] Exact strings, identifiers and error messages with file and line — Contract v3 C4; Framework v4.1.2 §11.4 · delivered by W1-17
- **Scenarios:** dev RETR-A-04, RETR-B-03, RETR-B-04, ISO-X-01, RETR-X-05 · qual CHAOS-A-Q04, CHAOS-A-Q12, AUDIT-A-Q05, A-Q04, AUDIT-A-Q09, AUDIT-A-Q13, AUDIT-A-Q15, RETR-B-Q01, AUDIT-B-Q20, ISO-X-Q01

### CAP-12 — Code-structural memory (AST/LSP/SCIP)

- **Outcome:** An agent can find definitions, callers and impact across languages from a code graph, without reading whole files.
- **Acceptance:** "References to function X" returns every call site across Rust, Python and TypeScript in the dev tier, before and after a rename.
- **Wave:** W1
- **Provider:** codebase-memory-mcp 0.11.0, W1-16
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C5; Framework v4.1.2 §11.5; DEC-014; DEC-074; DEC-076
- **Covers:**
  - `CAP-12.a` [W1] Definitions, references, callers, impact, dead code across languages — Contract v3 C5; Framework v4.1.2 §11.5; DEC-014 · delivered by W1-16
  - `CAP-12.b` [W1] Per-repository index home; secrets excluded from the code graph — DEC-074 Q10; DEC-076 · delivered by W1-16
- **Scenarios:** dev MR-A-06, RETR-A-03, AUDIT-A-01, MR-B-06, B-08, RETR-B-02, RETR-B-03, RETR-X-05 · qual RETR-A-Q01, AUDIT-A-Q04, AUDIT-A-Q05, AUDIT-A-Q07, AUDIT-A-Q16, MR-B-Q01, B-Q01, B-Q03, ISO-X-Q01

### CAP-13 — Temporal and episodic memory

- **Outcome:** An agent can see how a file or decision changed over time and which decision or task caused each change.
- **Acceptance:** For a changed file, the graph returns its commits with their `Implements:` and `Task:` trailers resolved to the decision and ticket records.
- **Wave:** W1
- **Provider:** git log + commit trailers, W1-10, W1-30, W1-25
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C6, C7; Framework v4.1.2 §11.6, §11.7; DEC-012
- **Covers:**
  - `CAP-13.a` [W1] Temporal memory: change history with causal decision/task links (trailers) — Contract v3 C6; Framework v4.1.2 §11.6 · delivered by W1-10, W1-30
  - `CAP-13.b` [W1] Episodic execution memory: checkpoints and close records per ticket — Contract v3 C7; Framework v4.1.2 §11.7 · delivered by W1-25
- **Scenarios:** dev CHAOS-A-03, CHAOS-B-03, B-07 · qual CHAOS-A-Q04, CHAOS-A-Q08, AUDIT-A-Q04, AUDIT-A-Q11, AUDIT-A-Q12, AUDIT-A-Q13, AUDIT-A-Q14, AUDIT-A-Q15, AUDIT-A-Q16, AUDIT-A-Q17, AUDIT-A-Q18, AUDIT-A-Q19

### CAP-14 — Failure memory

- **Outcome:** An agent can see a previously failed approach before it retries it.
- **Acceptance:** A retrieval for a task whose scope matches a committed failure record returns that record in the evidence bundle before any implementation step.
- **Wave:** W1
- **Provider:** W1-08, W1-21, W1-44
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C8; Framework v4.1.2 §11.8; OWNER-DIRECTION-BR-0006 §1 (lessons/failed approaches); DEC-080
- **Covers:**
  - `CAP-14.a` [W1] Failed approaches recorded and surfaced before a retry — Contract v3 C8; Framework v4.1.2 §11.8; OWNER-DIRECTION-BR-0006 §1 · delivered by W1-21
- **Scenarios:** dev CHAOS-B-01, CHAOS-B-04, RETR-X-04, B-X-02 · qual AUDIT-A-Q02, AUDIT-A-Q20, AUDIT-A-Q22, AUDIT-A-Q23, AUDIT-A-Q25, CHAOS-B-Q13, B-Q02, SEC-B-Q03, RETR-X-Q04

### CAP-15 — The brief carries the ticket's retrieval

- **Outcome:** An agent starts every task with a brief that carries the ticket's whole retrieval bundle, uncut, with its mandatory inputs by id and hash and the authority record first.
- **Acceptance:** `gov brief <role> <ticket>` writes a brief that holds the ticket's whole retrieval bundle, uncut, every mandatory input by id and sha256 and no unfilled placeholder (no `{QUESTION}`), refuses when a mandatory input is missing or the ticket is not READY, and the memory-use log has a line for it; `gov context` is retired and no packet ceiling exists.
- **Wave:** W2 (the Wave 1 packet (`gov context`) is retired (DEC-1214 M1); the brief carries the retrieval (W2-197, EMERGENCY-2 §5.4))
- **Provider:** W1-23, W2-197
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate C9; Framework v4.1.2 §15; Contract v3 Gate W4, W9, W10; OWNER-DIRECTION-BR-0005 (multi-batch retrieval); OWNER-DIRECTION-BR-0006 §4 (hierarchical synthesis); DEC-030, DEC-031, DEC-032; DEC-003; DEC-004; DEC-036; DEC-080; EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1
- **Covers:**
  - `CAP-15.a` [W2] Brief: mandatory inputs by id, version and sha256; the authority record first; the supplementary block separate; all carried in the brief — Contract v3 C9, W3, W4, W10; Framework v4.1.2 §15; EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1 · delivered by W2-197
  - `CAP-15.b` [W2] Required inputs: id, authority/lifecycle state, version/hash constraint, reason per dependency; carried in the brief — Contract v3 W3; EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1 · delivered by W2-197
  - `CAP-15.c` [W2] Missing mandatory input → `gov brief` refuses or reports BLOCKED; a superseded input cannot satisfy a current requirement; conflicting inputs → contradiction handling — Contract v3 W3, W4; EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1 · delivered by W2-197
  - `CAP-15.d` [NONE] Non-goal: token pressure drops supplementary context before mandatory inputs: packet mechanics, retired with `gov context` — EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1
  - `CAP-15.e` [W2] The brief's hash and provenance prove what the worker received — Contract v3 W4; EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1 · delivered by W2-197
  - `CAP-15.f` [W3] Hierarchical synthesis notes: derived, cited, hash-checked, disclose unresolved evidence, rebuildable (built only if friction asks; off with `gov context`) — DEC-080; DEC-030; DEC-036; OWNER-DIRECTION-BR-0006 §4; EMERGENCY-2 §9.2 (DEC-1211); EMERGENCY-2 §8.4 (DEC-1211) · delivered by W1-23
  - `CAP-15.g` [NONE] Non-goal: a file path plus a summary of at most ~2.5k tokens: packet mechanics, retired with `gov context` — EMERGENCY-2 §5.4, §5.5 (DEC-1211); DEC-1214 M1
- **Scenarios:** dev CHAOS-A-11, ISO-X-01, RETR-X-04 · qual ISO-X-Q01, RETR-X-Q02

### CAP-16 — Multi-batch, multi-hop, paginated retrieval

- **Outcome:** An agent can gather evidence that spans many locations and hops, in batches, until a stated stopping reason.
- **Acceptance:** On RETR-A-04 and RETR-X-02, the evidence bundle shows more than one batch, the merge, and a stopping reason from the fixed list; a batch-size limit is never reported as completeness.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-21, W1-36
- **Disposition:** KEPT
- **Sources:** OWNER-DIRECTION-BR-0005 (full); OWNER-DIRECTION-BR-0006 §2, §3; DEC-030, DEC-033, DEC-034, DEC-035; DEC-080
- **Covers:**
  - `CAP-16.a` [W1] Batches with continuation; batch size never a completeness limit — DEC-030; DEC-080; OWNER-DIRECTION-BR-0005 · delivered by W1-21
  - `CAP-16.b` [W1] Parallel facet retrieval → merge/filter → unresolved dependencies → sequential follow-up → bounded compilation — DEC-030; OWNER-DIRECTION-BR-0006 §2, §3 · delivered by W1-36, W1-21
  - `CAP-16.c` [W1] Radius-scaled rounds (placeholders tuned from telemetry) — DEC-035 · delivered by W1-21
- **Scenarios:** dev RETR-A-04, RETR-X-02 · qual RETR-A-Q01, RETR-A-Q02, RETR-A-Q03, RETR-A-Q04, RETR-X-Q02, RETR-X-Q05

### CAP-17 — Incremental indexing and freshness

- **Outcome:** An agent never receives stale evidence silently: changed files are re-indexed before the next retrieval, or the facet is reported unavailable.
- **Acceptance:** After one decision file is edited, the next `gov retrieve` returns the edited content, or reports the facet FACET_UNAVAILABLE; it never returns the old text as current.
- **Wave:** W1 (the landing refreshes the store after each land (replaces the commit-time hook G-23, W2))
- **Provider:** W1-17, W1-22, W2: the landing's store refresh (W2-115b)
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D1; Framework v4.1.2 §13; DEC-037 (zero-result canaries); DEC-080
- **Covers:**
  - `CAP-17.a` [W1] Changed content re-indexed before the next retrieval, or facet reported unavailable — Contract v3 D1; Framework v4.1.2 §13 · delivered by W1-17
  - `CAP-17.b` [W2] The landing rebuilds the store after each land, and `gov retrieve` reports a stale store — G-23; EMERGENCY-2 §4.4 (DEC-1211)
  - `CAP-17.c` [W1] Zero-result canaries after reindex — DEC-037; DEC-080 · delivered by W1-22
- **Scenarios:** dev CHAOS-A-02, CHAOS-A-03, CHAOS-A-12, CHAOS-B-02, CHAOS-B-03, CHAOS-B-09, CHAOS-B-12, B-06, B-10, RETR-X-01 · qual RETR-X-Q01

### CAP-18 — Retrieval router (multi-route fusion)

- **Outcome:** An agent can answer a complex question through several retrieval routes, fused, deduplicated and reranked once.
- **Acceptance:** A question that needs lexical, semantic and graph routes returns one fused list with duplicates removed by chunk hash and one rerank over the merged set; child hits carry parent_id and are expanded to their parent span only within the bundle budget; the bundle names the routes and the expansions.
- **Wave:** W1 (DEC-080; parent-child retrieval DEC-091)
- **Provider:** W1-17, W1-19, W1-21
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D2, D3; Framework v4.1.2 §14, §14.1; DEC-016; DEC-074; DEC-080; DEC-091
- **Covers:**
  - `CAP-18.a` [W1] Multi-route router with fusion (RRF), dedup by chunk hash, one rerank — Contract v3 D2; Framework v4.1.2 §14; DEC-080 · delivered by W1-19, W1-21
  - `CAP-18.b` [W1] Hierarchical retrieval: document→section→chunk, code file→module→function; child first; parent/neighbour expansion only as needed, named in the bundle — Contract v3 D3; Framework v4.1.2 §14.1; DEC-091 · delivered by W1-17, W1-21
- **Scenarios:** dev RETR-A-01, RETR-X-01, RETR-X-05 · qual RETR-X-Q05

### CAP-19 — Retrieval component separation and model selection

- **Outcome:** The owner can swap an embedding or reranking model through configuration, with a pinned revision and a regression check.
- **Acceptance:** Changing the embedder pin in configuration triggers a full re-embed, the dev-tier retrieval regression passes, and an unpinned or mismatched model makes retrieval fail closed with a named error.
- **Wave:** W2 (fail-closed model pin and lighter reranker spike W2; per-repository benchmark W3)
- **Provider:** W2: embedder/reranker adapters under the fail-closed pin, W3: per-repository retrieval benchmark
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D4, D5; Framework v4.1.2 §14.2, §14.3; OWNER-DIRECTION-BR-0006 §5 (provisional BGE, replaceable); DEC-017; DEC-046; DEC-074
- **Covers:**
  - `CAP-19.a` [W2] Components separable; model swap by configuration under a fail-closed pin — Contract v3 D4; Framework v4.1.2 §14.2; DEC-046 (D-0005/6)
  - `CAP-19.b` [W3] Evidence-driven model selection (bake-off, per-repository benchmark) — Contract v3 D5; Framework v4.1.2 §14.3; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-19.c` [W2] Retrieval learning loop: a miss is a memory-quality event → root cause → fix → judged by the next fresh 80 (no set is reused) — Framework v4.1.2 §18; DEC-1207 (3); DEC-1210
- **Scenarios:** dev RETR-X-01 · qual RETR-X-Q01

### CAP-20 — Rebuild guarantee (delete derived, rebuild from git)

- **Outcome:** A fresh agent on a fresh clone can rebuild all derived state from git and continue.
- **Acceptance:** `gov rebuild` twice from the same commit yields the same chunk-SHA-256 digest, and a fresh agent resumes the active ticket from the rebuilt state and the latest checkpoint.
- **Wave:** W1
- **Provider:** W1-27, W1-25
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate D6; Framework v4.1.2 §19; Distribution Protocol v1.2 §7.5; DEC-016
- **Covers:**
  - `CAP-20.a` [W1] Delete derived state, rebuild from git, identical digest; fresh agent reconstructs — Contract v3 D6; Framework v4.1.2 §19; Distribution Protocol v1.2 §7.5 · delivered by W1-27, W1-25
- **Scenarios:** dev CHAOS-A-01, CHAOS-A-02, CHAOS-A-09, CHAOS-B-01, CHAOS-B-02, CHAOS-B-09, CHAOS-B-10, B-06, ISO-X-01, ISO-X-02 · qual CHAOS-A-Q03, CHAOS-B-Q02, SOAK-B-Q01, B-Q04, AUDIT-B-Q17, AUDIT-B-Q19, AUDIT-B-Q21, AUDIT-B-Q22, AUDIT-B-Q24, AUDIT-B-Q33, SOAK-B-Q02, ISO-X-Q01 (+1 not listed in the matrix row)

### CAP-21 — Owner-only approval facts (lite of L0-L5 authority levels)

- **Outcome:** The owner can trust that no agent makes a decision ACTIVE on its own.
- **Acceptance:** `gov check` (and CI) fails a change that sets a decision ACTIVE unless the change carries an owner approval fact from git.
- **Wave:** W1
- **Provider:** W1-11
- **Disposition:** LITE — lite form: An approval is a fact only when it comes from the owner's git account (owner commit, signed tag or PR approval); no in-process L0–L5 machinery.
- **Sources:** Contract v3 Gate E1; Framework v4.1.2 §23; OWNER-DECISION-P2-0001 (role identity binding); DEC-039; DEC-046; DEC-074
- **Covers:**
  - `CAP-21.a` [W1] Approval facts only from the owner's git account; kernel and instruction text needs the CTO's approval, not the owner's (EMERGENCY-2 §3.5); decisions still need the owner's — Contract v3 E1 (LITE); Framework v4.1.2 §23 · delivered by W1-11
  - `CAP-21.b` [NONE] Non-goal: in-process L0–L5 levels, acting-role resolution, sealed human channel — DEC-039; OWNER-DECISION-P2-0001
- **Scenarios:** dev MR-A-01 · qual MR-A-Q01, CHAOS-A-Q10, AUDIT-A-Q27

### CAP-22 — Agent roles and typed A2A handoffs

- **Outcome:** An agent can hand work to a fresh agent in a typed record the receiver can act on without the sender's chat.
- **Acceptance:** A fresh agent B, given only the handoff record and the repository, states the task, inputs, open questions and next step identically to agent A's record.
- **Wave:** W2 (W1 hands off through checkpoints; typed handoff records and specialist roles, including test execution and integration (DEC-094), are W2)
- **Provider:** W1-25, W2-121c (inbox files), W1-33, W1-05, W1-46
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate E2, E3; Framework v4.1.2 §24, §25; DEC-066; DEC-094; DEC-119; DEC-154; DEC-163
- **Covers:**
  - `CAP-22.a` [W1] Representative roles as subagent definitions: minimal definitions first from W1-05 at the switch-over, replaced by W1-33's generated definitions — Contract v3 E2; Framework v4.1.2 §24; DEC-119; DEC-154 · delivered by W1-05, W1-33
  - `CAP-22.b` [W2] A handoff is the worker's return contract (CAP-37.d) plus the run-time tool's per-session inbox files with a read mark (RT-6): a finished worker's return reaches its lead's inbox file and no owner message relays it — Contract v3 E3; Framework v4.1.2 §25; EMERGENCY-2 §6.3 (DEC-1211) · delivered by W2-121c
  - `CAP-22.c` [W3] Distinct test execution and integration roles — MR-5; DEC-094; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-22.d` [W1] A minimal research role in the Wave 1 roster, as a role file delivered with the launcher: a research or experiment session runs as `GOV_ROLE=research` in its own experiment folder or worktree, its ticket's `allowed_paths` judged at the landing as a notice; no guard and no network allowlist; the full research lifecycle (CAP-32) stays W3 — DEC-163; DEC-158; EMERGENCY-2 §2.2 (DEC-1211) · delivered by W1-46
- **Scenarios:** dev CHAOS-X-02 · qual CHAOS-X-Q02

### CAP-23 — Concurrency and task claims

- **Outcome:** Two agents cannot both take the same task.
- **Acceptance:** A second agent claiming a ticket already claimed by another gets a collision error naming the holder, and the ticket is absent from its ready queue.
- **Wave:** W2 (the exclusive claim lock (G-03) is delivered in W1-09; a light form of parallel tickets runs in Wave 1 (DEC-235); the run-time tool dispatches ready tickets into slots from the machine it detects (RT-1, RT-3, W2-121c))
- **Provider:** ticket v0.3.2, W1-09, W1-42, W2-121c, W2-121d (the run-time tool)
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate E4; Framework v4.1.2 §44; DEC-066; DEC-074; DEC-076; DEC-235; EMERGENCY-2 §6.3 (DEC-1211)
- **Covers:**
  - `CAP-23.a` [W1] Exclusive claim lock with holder named — Contract v3 E4; G-03 · delivered by W1-09
  - `CAP-23.b` [W2] The run-time tool dispatches ready tickets into slots from the CPU, RAM and GPU it detects (RT-1, RT-3); the claim lock (CAP-23.a) keeps two agents off one ticket — Contract v3 E4, I4; Framework v4.1.2 §44; DEC-066; EMERGENCY-2 §6.3 (DEC-1211) · delivered by W2-121c, W2-121d
  - `CAP-23.c` [W2] Parallel tickets: each ticket in its own worktree with a ticket lead; the landing merges it into the integration branch, runs the impact-selected tests and checks paths and test authorship (NEW-1); the number in flight comes from the machine's slots, not from a constant — DEC-235; DEC-236; EMERGENCY-2 §4 (DEC-1211) · delivered by W1-42
- **Scenarios:** dev CHAOS-X-03 · qual CHAOS-X-Q03

### CAP-24 — Skill lifecycle and versioning

- **Outcome:** An agent can tell which version of each skill produced a piece of work.
- **Acceptance:** Every skill file carries a version in frontmatter, and the land record of a ticket lists the skill ids and versions used.
- **Wave:** W1
- **Provider:** W1-35, W1-36, W1-37, W1-30, W1-26
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate F1; Framework v4.1.2 §26, §27; DEC-024; DEC-074
- **Covers:**
  - `CAP-24.a` [W1] Skills versioned; versions recorded against the work — Contract v3 F1; Framework v4.1.2 §26, §27 · delivered by W1-35, W1-30
  - `CAP-24.b` [W1] A skill is a method: not a tool and not a policy (skills hold no permissions and no authority) — Framework v4.1.2 §26 · delivered by W1-35, W1-36
  - `CAP-24.c` [W1] Kernel and instruction text (role files, brief and role templates, skills, CLAUDE.md and AGENTS.md) changes only by the CTO's decision, approval and own commit; the landing checks kernel bytes against the CTO-approved list — Framework v4.1.2 §5, §27; EMERGENCY-2 §3.5 (DEC-1211) · delivered by W1-35, W1-26
- **Scenarios:** dev CHAOS-A-05 · qual CHAOS-X-Q05

### CAP-25 — Tool registry and capability memory (lite)

- **Outcome:** The owner can see every tool the Gov OS relies on, at which pinned version, and trust that the CTO approved and recorded each install.
- **Acceptance:** `gov doctor --json` lists pinned versus found versions and exits non-zero on drift; every install is recorded in the tool registry with the CTO's approval, its scope and its machine cost; `sudo` stays the owner's (the deny line refuses it in every permission mode).
- **Wave:** W1
- **Provider:** W1-04, W1-06, W1-27, W1-48, W1-46, W1-47
- **Disposition:** LITE — lite form: Tool registry with pins; the CTO approves and records every install (version, sha256, install and uninstall commands, date, approving decision, scope and machine cost), so that nothing out of the work's scope or beyond the machine's capacity is installed; `gov doctor` checks the pins; `sudo` stays the owner's. No automated install classification (DEC-083).
- **Sources:** Contract v3 Gate F2, F3; Framework v4.1.2 §28-30; OWNER-DECISION-P2-0003 (gate only elevated installs); Contract v3 Gate C10; Framework v4.1.2 §11.10; DEC-040; DEC-074; DEC-083; DEC-153; DEC-157; DEC-163; DEC-172; DEC-174; DEC-1214 G7 (c)
- **Covers:**
  - `CAP-25.a` [W1] Tool registry with pins, sha256, install/uninstall commands, date, approving decision; gov doctor checks — Contract v3 F2, C10 (LITE); Framework v4.1.2 §28–29, §11.10 · delivered by W1-04, W1-06, W1-27
  - `CAP-25.b` [W1] The CTO approves and records every install; no permission prompt; `sudo` stays with the owner — Contract v3 F3 (LITE); Framework v4.1.2 §30; DEC-083; DEC-1214 G7 (c) · delivered by W1-04
  - `CAP-25.c` [NONE] Non-goal: automated install classification, argv analysis, authority envelopes — DEC-083; OWNER-DECISION-P2-0003
  - `CAP-25.d` [W1] Claude Code is a tool registry entry pinned at 2.1.285 or later; raising the pin is an install by the owner, or by the orchestrator under DEC-083, in both cases recorded with its owner approval; worker roles never install system-wide — DEC-153; DEC-157; DEC-209 · delivered by W1-48
  - `CAP-25.e` [NONE] Non-goal: the research role's install fence (the sandbox write fence and the generated `Edit` deny rules): an install by the research role is free inside its repository, worktree or venv (CAP-25.b) — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-25.f` [NONE] Non-goal: the committed settings carry no install ask rule so that the guard's install rule decides alone: no guard, no install rule — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-25.g` [NONE] Non-goal: the guard's install rule for `uv add`, `uv sync`, `uv run --with` and `uvx`: no guard — EMERGENCY-2 §2.2 (DEC-1211)
- **Scenarios:** dev CHAOS-A-05, CHAOS-B-04, CHAOS-B-05, CHAOS-B-14, B-10, AUDIT-B-03 · qual CHAOS-X-Q05

### CAP-26 — Plugin trust boundary (hash-binding, descriptor security)

- **Outcome:** (none — non-goal)
- **Acceptance:** No kernel file implements plugin hash-binding or descriptor trust; the wave-exit audit finds none (DEC-070).
- **Wave:** NONE (dropped)
- **Provider:** none (non-goal)
- **Disposition:** DROP — Non-goal: plugin trust boundary (hash-binding, descriptor security, self-attestation prevention) defends against a same-privilege adversary (ADR-0001).
- **Sources:** Contract v3 Gate F4; OWNER-DECISION-P2-0005 (bind the bytes); OWNER-CLARIFICATION-P2-0004 (project files cannot manufacture authority); DEC-039; DEC-075
- **Covers:**
  - `CAP-26.a` [NONE] Non-goal: plugin hash-binding, descriptor security, self-attestation prevention — Contract v3 F4; OWNER-DECISION-P2-0005
- **Scenarios:** dev — · qual —

### CAP-27 — Read/act separation of commands (lite of MCP/A2A/knowledge layers)

- **Outcome:** An agent can run any read command without changing the repository.
- **Acceptance:** Every `gov` read command (status, check, readiness, doctor, context --dry-run, closure, retrieve) leaves `git status --porcelain` empty.
- **Wave:** W1
- **Provider:** W1-07, W1-32
- **Disposition:** LITE — lite form: Read commands never mutate; no separate A2A layer or three-layer knowledge fabric; the minimal per-session inbox files inside the run-time tool are in scope (RT-6) and are not an A2A layer.
- **Sources:** Contract v3 Gate F5; Framework v4.1.2 §31; DEC-074
- **Covers:**
  - `CAP-27.a` [W1] Read commands never mutate — Contract v3 F5 (LITE); Framework v4.1.2 §31 · delivered by W1-07, W1-32
  - `CAP-27.b` [NONE] Non-goal: separate A2A layer and three-layer knowledge fabric — DEC-074 Q11
- **Scenarios:** dev MR-X-01 · qual MR-X-Q01

### CAP-28 — Natural-language intent routing and small command surface

- **Outcome:** The owner can ask in natural language and get a structured governance answer; a small command set covers the rest.
- **Acceptance:** A status question in chat is answered from `gov status --json` (tickets, gates, readiness, share, pause state) rather than from free recall.
- **Wave:** W1
- **Provider:** Claude Code (harness), W1-07, W1-32, W1-35, W1-42
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate G1, G2; Framework v4.1.2 §33, §34; DEC-003
- **Covers:**
  - `CAP-28.a` [W1] Natural-language intent first; small explicit command set — Contract v3 G1, G2; Framework v4.1.2 §33, §34 · delivered by W1-32, W1-35
  - `CAP-28.b` [W1] Internal governance operations exposed as gov commands — Framework v4.1.2 §35 · delivered by W1-07, W1-42
- **Scenarios:** dev MR-X-01 · qual MR-X-Q01

### CAP-29 — Specification lineage (idea to live evidence)

- **Outcome:** An agent can follow a feature from idea through scenarios, requirements, decisions, tasks and tests to live evidence.
- **Acceptance:** For a feature, `gov closure` returns its linked mission, scenario, requirement, decision, ticket and acceptance-test ids, and reports each missing link.
- **Wave:** W3 (links from OpenSpec and frontmatter in W1; full idea→live-evidence lineage W3)
- **Provider:** OpenSpec 1.13.2, W1-08, W1-10, W3: full lineage
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate H1; Framework v4.1.2 §36; DEC-011; DEC-064
- **Covers:**
  - `CAP-29.a` [W3] Lineage idea → mission → actors → journeys → scenarios → features → data → requirements → research → decisions → algorithms → architecture → interfaces → security/performance/operations → WBS → tests → live evidence — Contract v3 H1; Framework v4.1.2 §36; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-29.b` [W3] Forward and reverse lineage; missing and stale links detected — Contract v3 W8; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev A-X-01 · qual A-X-Q01

### CAP-30 — Feature readiness contract (26-dimension checklist)

- **Outcome:** An agent can see, per feature, which of the 26 readiness rows are open for its profile, and each gap becomes work.
- **Acceptance:** A specification with a row its profile requires MISSING (for example test data at FULL) keeps its production tickets out of READY, and `gov discover` opens one linked gap ticket per required open row with its dependencies.
- **Wave:** W2 (schema, checker, the READY gate and linked gap tickets (planning skill + gov check, DEC-089) are W1; automatic generation is W2)
- **Provider:** OpenSpec custom schema, W1-12, W1-13, W2-36 (gov discover), W1-26, W1-35
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate H2, H3, H4; Framework v4.1.2 §37, §38, §39; DEC-005; DEC-064; DEC-085; DEC-089; DEC-103; DEC-104
- **Covers:**
  - `CAP-30.a` [W1] 26-row readiness checklist, five states, silent N/A invalid, no defaulted N/A — Contract v3 H2; Framework v4.1.2 §37; DEC-085 · delivered by W1-12, W1-13
  - `CAP-30.b` [W1] Readiness gaps generate linked tickets (W1 planning skill + gov check) — Contract v3 H3; Framework v4.1.2 §38; DEC-089 · delivered by W1-13, W1-26, W1-35
  - `CAP-30.c` [W2] Automatic generation of the gap tickets, inside `gov discover` (`gov readiness --generate` is folded into it, W2-36) — Contract v3 H3; DEC-089; EMERGENCY-2 §6.2 A-4 (DEC-1211) · delivered by W2-36
  - `CAP-30.d` [W3] Scenarios drive data and tests; data provenance recorded; data author independent where practical — Contract v3 H4; Framework v4.1.2 §39; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-30.e` [W1] Capability taxonomy for STANDARD rows; extended only through a governed change — Framework v4.1.2 §40 · delivered by W1-12, W1-26
  - `CAP-30.f` [W1] Order of specification work: discovery and research, scenarios, representative data, UX for a feature with a user interface, acceptance tests, implementation; the owner reviews scenarios and UX designs, not test code — DEC-103 · delivered by W1-35
  - `CAP-30.g` [W3] For a feature with a user interface, the UX row closes only on scenario-derived wireframes or mockups the owner has approved; its acceptance tests include visual checks against them (screenshot comparison, scenario walk-throughs); owned by the UX role — DEC-104; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev MR-A-02, MR-A-04, A-01 · qual MR-A-Q02, MR-A-Q04, CHAOS-A-Q07, A-Q01, A-Q02, A-Q05, AUDIT-A-Q32, AUDIT-A-Q35, AUDIT-A-Q37, AUDIT-A-Q43, AUDIT-A-Q44, AUDIT-A-Q47 (+9 not listed in the matrix row)

### CAP-31 — Unified task DAG

- **Outcome:** An agent works from one task DAG in git, and a red landing names its own cause.
- **Acceptance:** A landing that turns red names its cause in the land record; the fix lands without a new ticket and is recorded in the owning ticket, and where no test caught the bug the failing test is committed first; `tk ready` lists a ticket only after its dependencies are closed.
- **Wave:** W1
- **Provider:** ticket v0.3.2, W1-09, W1-14, W1-30, W1-08
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate I1, I2, I3, I4; Framework v4.1.2 §41-44; DEC-074; EMERGENCY-2 §4.2 (DEC-1211)
- **Covers:**
  - `CAP-31.a` [W1] One task DAG; task contract with class, role, inputs, allowed paths, KPIs, profile — Contract v3 I1, I2; Framework v4.1.2 §41, §42 · delivered by W1-08, W1-14
  - `CAP-31.b` [W1] A known bug is a fix, not a ticket: a red landing generates no repair ticket; the fix is recorded in the owning ticket, the failing test first where no test caught it — Contract v3 I3; Framework v4.1.2 §43; EMERGENCY-2 §4.2 (DEC-1211) · delivered by W1-30
  - `CAP-31.c` [W1] Parallel and serial execution by dependency — Contract v3 I4; Framework v4.1.2 §44 · delivered by W1-09
  - `CAP-31.d` [W1] A task cannot be READY if a mandatory input is absent — Contract v3 W3 · delivered by W1-09
- **Scenarios:** dev MR-A-02, MR-A-03, MR-A-04, A-03, A-04, MR-B-02, MR-B-03, MR-B-04, CHAOS-B-05, CHAOS-B-06, GATE-B-01, AUDIT-B-05 (+2 not listed in the matrix row) · qual MR-A-Q02, MR-A-Q03, MR-A-Q04, GATE-A-Q04, A-Q01, A-Q02, AUDIT-A-Q28, AUDIT-A-Q29, AUDIT-A-Q30, AUDIT-A-Q31, AUDIT-A-Q32, MR-B-Q04 (+2 not listed in the matrix row)

### CAP-32 — Research and experiment lifecycle

- **Outcome:** An agent keeps research as evidence records separate from authority, and experimental results cannot reach production unreviewed.
- **Acceptance:** A research record marked EXPERIMENTAL cited by a production change makes `gov check` fail until a decision promotes it.
- **Wave:** W3 (experiments as part of discovery, with an evidence record, are W1 (DEC-102); a minimal research role is W1 (DEC-163, CAP-22.d); `gov discover` is W2 (DEC-166); the full research lifecycle is W3)
- **Provider:** Docling (pinned), MarkItDown, W3: gov research sync + research records, W1-35, W2-36 (gov discover)
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate J1, J2; Framework v4.1.2 §45, §46; DEC-019; DEC-020; DEC-102; DEC-163; DEC-166
- **Covers:**
  - `CAP-32.a` [W3] Research becomes evidence records separate from authority — Contract v3 J1; Framework v4.1.2 §45; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-32.b` [W3] Experiment lifecycle; discovery flow — Contract v3 J2; Framework v4.1.2 §46; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-32.c` [W1] Experiments (spikes, tool compatibility and performance trials) are part of discovery and can run at any point; they run in their own experiment folder or worktree, outside production paths, and leave an evidence record (what was tested, how, results, verdict); their code is promoted only through the normal cycle; their results change a closed specification only through CIT-P — DEC-102; EMERGENCY-2 §2.2 (DEC-1211) · delivered by W1-35
  - `CAP-32.d` [W2] `gov discover <question or feature>` is the entry point to discovery: it opens a discovery ticket, runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose evidence records, with measured numbers, back the answer; the same request in plain language works the same way — DEC-166 · delivered by W2-36
- **Scenarios:** dev A-X-02 · qual AUDIT-A-Q02, AUDIT-A-Q06, AUDIT-A-Q20, AUDIT-A-Q21, AUDIT-A-Q23, AUDIT-A-Q24, AUDIT-A-Q38, AUDIT-A-Q43, CIT-B-Q01

### CAP-33 — Change-impact transactions (CIT-P simulation, CIT-E execution)

- **Outcome:** An agent can simulate a change before making it (CIT-P) and record what it changed (CIT-E).
- **Acceptance:** A decision change raises a CIT-P listing the affected specs, decisions, tickets, tests and code from both graphs, with a radius; after apply/archive the CIT-E record matches the proposal or lists the differences.
- **Wave:** W2 (OpenSpec proposal and apply/archive in W1, where a plain-language impact question runs an OpenSpec proposal plus `gov closure` (DEC-167); computed impact W2)
- **Provider:** OpenSpec 1.13.2, W1-35, W2: gov impact
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate K1, K2, K3, K4; Framework v4.1.2 §47-49; DEC-005 (proportionality profiles LITE/STANDARD/FULL); DEC-035 (radius-scaled budgets/facets); DEC-011; DEC-066; DEC-105; DEC-167
- **Covers:**
  - `CAP-33.a` [W1] CIT-P proposal and CIT-E apply/archive records — Contract v3 K1, K2; Framework v4.1.2 §47 · delivered by W1-35
  - `CAP-33.b` [W2] Automatic impact simulation over record and code graphs; impact radius → profile — Contract v3 K3, K4; Framework v4.1.2 §48, §49
  - `CAP-33.c` [W3] Upstream change propagates staleness and generates revalidation tasks — Contract v3 W6; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-33.d` [W1] Changes to the Gov OS's own Charter and Contract pass evidence → a CIT-P with three costed options (DEC-105) → the owner's approval → a versioned promotion; kernel and instruction text follows CAP-24.c — Framework v4.1.2 §5; EMERGENCY-2 §3.5 (DEC-1211) · delivered by W1-35
  - `CAP-33.e` [W1] An experiment or finding that contradicts a closed specification opens a CIT-P whose impact assessment gives three costed options (apply now, defer, re-baseline); the owner chooses; CIT-E records what was done; every version of the specification is kept — DEC-105 · delivered by W1-35
  - `CAP-33.f` [W1] The question "what is the impact of X?", asked in plain language, triggers the impact assessment; in Wave 1 that is an OpenSpec proposal plus `gov closure` — DEC-167 · delivered by W1-35
  - `CAP-33.g` [W2] From Wave 2 the same plain-language question runs `gov impact` — DEC-167
- **Scenarios:** dev MR-A-05, CIT-A-01, CIT-A-02, MR-B-05, CIT-B-01 · qual MR-A-Q05, CHAOS-A-Q01, CHAOS-A-Q02, CHAOS-A-Q05, CIT-A-Q01, CIT-A-Q02, CIT-A-Q03, A-Q03, AUDIT-A-Q26, AUDIT-A-Q27, AUDIT-A-Q39, SOAK-X-Q01

### CAP-34 — Human decision gates and contradiction resolution

- **Outcome:** The owner receives every question that matters as a ranked decision package in the active chat, and independent branches keep going.
- **Acceptance:** A high-impact contradiction produces a package in chat with all ten fields (MR-6's eight plus current state and exact permitted next actions), ranked P1–P3 and batched at most five at a time with P1 allowed to bypass; the dependent ticket is blocked; an independent ticket still reaches close; the answer lands as a register entry in git.
- **Wave:** W1
- **Provider:** W1-34, W1-35, W1-09, W1-11
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate L1, L2, L3, L4; Framework v4.1.2 §50-54; DEC-044 as amended by DEC-096 (loop policy); DEC-065; DEC-093
- **Covers:**
  - `CAP-34.a` [W1] Agent- vs human-resolvable contradictions — Contract v3 L1; Framework v4.1.2 §50 · delivered by W1-34
  - `CAP-34.b` [W1] Decision package with ten fields — Contract v3 L2; Framework v4.1.2 §52 · delivered by W1-34
  - `CAP-34.c` [W1] Presented in the active chat; ranked P1–P3; at most five at a time, P1 may bypass — Contract v3 L3; Framework v4.1.2 §52, §54; DEC-093 · delivered by W1-34, W1-35
  - `CAP-34.d` [W1] Declined, revoked, stale or other-CIT gates cannot authorise execution — Contract v3 L3 · delivered by W1-11, W1-34
  - `CAP-34.e` [W1] Non-global blocking — Contract v3 L4; Framework v4.1.2 §53 · delivered by W1-09
- **Scenarios:** dev MR-A-03, CHAOS-A-06, CHAOS-A-07, CHAOS-A-08, CHAOS-A-15, GATE-A-01, MR-B-03, CHAOS-B-06, CHAOS-B-07, CHAOS-B-08, GATE-B-01, GATE-B-02 (+2 not listed in the matrix row) · qual MR-A-Q03, CHAOS-A-Q13, GATE-A-Q01, GATE-A-Q02, GATE-A-Q03, GATE-A-Q04, A-Q01, MR-B-Q05, AUDIT-B-Q01, AUDIT-B-Q05, AUDIT-B-Q08, AUDIT-B-Q14 (+6 not listed in the matrix row)

### CAP-35 — Model routing from the owner's rubric

- **Outcome:** The owner can route each role and task class to a model and effort through his rubric, and no session chooses its own.
- **Acceptance:** Every launch takes its model and effort from the owner's rubric (DEC-1120, DEC-1212) and states them in the launch log (RT-8); a launch that names another model is refused.
- **Wave:** W2
- **Provider:** W2-121c (the launcher states the rubric's model and effort)
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate M1, M2, M3; Framework v4.1.2 §55-57; DEC-010; DEC-018; DEC-083; DEC-1120; DEC-1212; DEC-1214 K1; EMERGENCY-2 §6.3 (DEC-1211)
- **Covers:**
  - `CAP-35.a` [W2] The rubric names the model and effort for each role and work class (capability tiers T0–T3 are its coarse form) — Contract v3 M1; Framework v4.1.2 §55; DEC-1120 · delivered by W2-121c
  - `CAP-35.b` [W2] Effort is declared by the rubric and enforced by the launcher, not chosen by the session — Contract v3 M2; Framework v4.1.2 §56; DEC-1120 · delivered by W2-121c
  - `CAP-35.c` [W2] Role defaults: the rubric's model and effort per role — Contract v3 M3; Framework v4.1.2 §57; DEC-1120 · delivered by W2-121c
- **Scenarios:** dev CHAOS-A-04, ISO-X-03 · qual CHAOS-X-Q06

### CAP-36 — Empirical model routing telemetry

- **Outcome:** The owner can compare cost and pass/fail per model per task class from real runs.
- **Acceptance:** A report lists tokens, cost and pass/fail per model per task class over the recorded tickets.
- **Wave:** W3
- **Provider:** W3: OTel evidence per role and model
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate M4; Framework v4.1.2 §58; DEC-026
- **Covers:**
  - `CAP-36.a` [W3] Per run: model/provider, task class, reasoning effort, cost, latency, pass/fail, repair count, reviewer findings — Contract v3 M4; Framework v4.1.2 §58; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev SOAK-X-01 · qual SOAK-X-Q01

### CAP-37 — Structured checkpoints and mandatory triggers

- **Outcome:** An agent can resume after compaction, a crash or a model switch from a structured checkpoint in the repository.
- **Acceptance:** After every ticket transition a checkpoint file exists; after a forced compaction and after a killed session, a session resumes at the checkpoint's recorded next step without the owner restating it (RT-5).
- **Wave:** W1 (model-switch continuity waits for friction (CAP-37.e); until W1-25's `gov checkpoint`, the orchestrator's checkpoint lives in `.gov-runtime/scratch/orchestrator/` (DEC-150, DEC-156))
- **Provider:** W1-25, W1-29, W1-49
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate N1, N2, N3, N4; Framework v4.1.2 §59-61; OWNER-DIRECTION-BR-0004 (checkpoint discipline); OWNER-DIRECTION-BR-0006 §7, §8; DEC-025; DEC-150; DEC-156; DEC-248; EMERGENCY-2 §6.3 (DEC-1211)
- **Covers:**
  - `CAP-37.a` [W1] Structured checkpoint in the repository with input ids/versions/hashes — Contract v3 N1, W9; Framework v4.1.2 §59 · delivered by W1-25
  - `CAP-37.b` [W1] Mandatory triggers incl. ticket transition, compaction, stop — Contract v3 N2; Framework v4.1.2 §60 · delivered by W1-25, W1-29
  - `CAP-37.c` [W1] The run-time tool's one state file and one wake rule mark a stale session and wake it (RT-5, RT-7); nothing is blocked — Contract v3 N3; Framework v4.1.2 §60; EMERGENCY-2 §6.3 (DEC-1211) · delivered by W1-25, W1-29
  - `CAP-37.d` [W1] Worker return contract: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action — Contract v3 N4; Framework v4.1.2 §61 · delivered by W1-29
  - `CAP-37.e` [W3] Model/provider switch reconstructs the same inputs — Contract v3 W9; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-37.f` [W1] Checkpoint discipline; resume after crash — OWNER-DIRECTION-BR-0004; OWNER-DIRECTION-BR-0006 §7, §8 · delivered by W1-25
  - `CAP-37.g` [W1] Auto-resume hooks: a PreCompact hook ensures the checkpoint is current (the orchestrator's, and in a worktree the lead's); a SessionStart hook on compact, clear and resume injects the prompt path and the checkpoint's RESUME HERE section; after a forced compaction the session knows the active tickets, the open owner decisions and the round counts without the owner restating them; there is no context packet (EMERGENCY-2 §5.5) — DEC-248; DEC-208; EMERGENCY-2 §5.5, §6.1 (DEC-1211); DEC-837 · delivered by W1-49
- **Scenarios:** dev CHAOS-A-01, CHAOS-A-04, ISO-X-01, ISO-X-03, CHAOS-X-02 · qual CHAOS-A-Q01, CIT-A-Q02, CIT-A-Q04, SOAK-A-Q01, A-Q03, AUDIT-A-Q36, CHAOS-B-Q01, CHAOS-B-Q03, CHAOS-B-Q04, CHAOS-B-Q05, CHAOS-B-Q10, CHAOS-B-Q11 (+6 not listed in the matrix row)

### CAP-38 — Verification test families (product and governance)

- **Outcome:** The owner can see product and governance verification results, with builder tests counted as regression evidence only.
- **Acceptance:** `gov check` reports each governance test family RED/YELLOW/GREEN; `gov accept` runs only the independent acceptance tests and reports pass or fail per KPI line; the landing runs the impact-selected tests; builder tests count as regression evidence only.
- **Wave:** W1
- **Provider:** W1-26, W1-30, W1-37, W1-02, W1-15, W1-17, W1-21, W1-24, W1-25, W1-27, W1-35, W1-36, W1-38, W1-42
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate O1, O2, O3, O4; Framework v4.1.2 §62-64; DEC-042 (builder tests are regression evidence only); DEC-083; DEC-136; DEC-137; EMERGENCY-2 §4 (DEC-1211)
- **Covers:**
  - `CAP-38.a` [W1] Product test families — Contract v3 O1; Framework v4.1.2 §62 · delivered by W1-30
  - `CAP-38.b` [W1] Governance test families: schema/invariants, graph integrity, index freshness, retrieval regression, path-map compliance, context reproducibility, concurrency/claims, adapter/model portability, skill regression, command-contract consistency, secrets indexing, recovery/rebuild, fresh-agent reconstruction, product traceability, audit reproducibility; authority/role limits and mutation scope are landing checks (CAP-58.h, MR-3), not test families — Contract v3 O2; Framework v4.1.2 §63; EMERGENCY-2 §2.2 (DEC-1211) · delivered by W1-26, W1-15, W1-17, W1-21, W1-24, W1-25, W1-27, W1-30, W1-35, W1-36, W1-38, W1-42
  - `CAP-38.c` [W1] Independent test authorship; builder tests are regression evidence only — Contract v3 O3; DEC-042 · delivered by W1-30, W1-02
  - `CAP-38.d` [W1] Governance suite currency — Contract v3 O4; Framework v4.1.2 §64 · delivered by W1-30
  - `CAP-38.e` [W1] A case the orchestrator's review finds that the acceptance tests miss goes to the next test design batch as a described behaviour, never as code; the test designer decides from the specification whether it becomes an acceptance test and reports a specification gap — DEC-136 · delivered by W1-35
  - `CAP-38.f` [NONE] Non-goal: a fresh reviewer's adversarial probe after green for a FULL ticket, with the close needing the probe record: work that went through green gets no review — EMERGENCY-2 §3.4, §3.6 (DEC-1211); DEC-1214 G6
- **Scenarios:** dev MR-A-06, A-02, MR-B-02, MR-B-04, MR-B-06, AUDIT-B-04, AUDIT-X-01 · qual AUDIT-A-Q08, A-Q05, AUDIT-A-Q40, AUDIT-A-Q41, AUDIT-A-Q46, AUDIT-B-Q02, AUDIT-X-Q01

### CAP-39 — Governance health tiers and the landing's checks (G1-G5)

- **Outcome:** Governance checks run at the right tier automatically, and a stale required index fails the landing.
- **Acceptance:** The landing fails when a required index is stale, and records each check it ran with its tier and its RED, YELLOW or GREEN result; `gov ci` runs the CI tiers.
- **Wave:** W2 (tiers G1–G5 in W1 (W1-40); the landing's impact selection is the release (W2); a scheduler beyond it is friction)
- **Provider:** lefthook 2.1.15, GitHub Actions, W1-40, W2-115b (the landing), W1-02, W1-26
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate O5; Framework v4.1.2 §62-64; DEC-007; DEC-075; DEC-087; EMERGENCY-2 §4.3, §4.4 (DEC-1211)
- **Covers:**
  - `CAP-39.a` [W1] Tiers G1 commit, G2 landing (the task's close), G3 pre-push (checkpoint and handoff), G4 milestone and G5 full suite on CI; there is no G0, since there is no guard — Contract v3 O5; EMERGENCY-2 §2.2 (DEC-1211) · delivered by W1-40, W1-02
  - `CAP-39.b` [W2] The proving run on the synthetic repositories (G6 qualification, EMERGENCY-2 §8.2 item 2): chaos, soak and hidden tests as the Contract's checks need them — Contract v3 O5; DEC-067; EMERGENCY-2 §8.2 (DEC-1211) · delivered by W2-81
  - `CAP-39.c` [W2] Impact-selected tests at the landing: the landing runs the tests the change's impact selects (`gov impact`) — Contract v3 O5; EMERGENCY-2 §4 (DEC-1211) · delivered by W2-115b
  - `CAP-39.d` [W1] RED/YELLOW/GREEN state; explicit hard-block vs warning; health result provenance recorded — Contract v3 O5 · delivered by W1-26
  - `CAP-39.e` [W3] Scheduler beyond the landing's selection: parallel independent checks, isolated worktrees and processes, a cache keyed by content, policy and framework hashes (built only if friction asks) — Contract v3 O5; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev ISO-X-02, SOAK-X-02, MR-X-02 · qual ISO-X-Q02, SOAK-X-Q02, MR-X-Q02

### CAP-40 — Execution telemetry and organisational questions

- **Outcome:** The owner can see tokens, model, cost and outcome per ticket.
- **Acceptance:** Each closed ticket has a telemetry record with fresh input/output tokens, cache reads, model, governance tokens and pass/fail.
- **Wave:** W1 (OTel dashboards W3)
- **Provider:** ccusage (pinned), W1-31, W1-06, W1-42
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate P1, P2; Framework v4.1.2 §65, §66; DEC-026; DEC-086; DEC-106; DEC-170
- **Covers:**
  - `CAP-40.a` [W1] Per ticket: agent/session/model/provider, role/task, skill/tool versions, brief id, retrieval queries/hits, tokens in/out, latency/cost, files read/written, tests, retries/failures, handoffs, decisions, human interventions — Contract v3 P1; Framework v4.1.2 §65 · delivered by W1-31
  - `CAP-40.b` [W3] Organisational questions: rework by role, retrieval effect on tokens, model over/under-power, skill repair rate, human-gate concentration, retrieval misses, cost by task/feature, first-pass completion — Contract v3 P2; Framework v4.1.2 §66; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-40.c` [W1] The weekly measures with their baselines: product share of spend, governance share (≤ 15 %), owner messages per day, time and cost per ticket, landing time, memory use (EMERGENCY-2 §10.2) — DEC-106; DEC-086; EMERGENCY-2 §10.2 (DEC-1211) · delivered by W1-31, W1-42
  - `CAP-40.d` [NONE] Non-goal: the sandbox's instruction tokens as a separate line of the telemetry record: there is no sandbox — EMERGENCY-2 §2.2 (DEC-1211)
- **Scenarios:** dev CHAOS-A-12, ISO-X-03, SOAK-X-01 · qual GATE-B-Q01, GATE-B-Q03, GATE-B-Q04, SOAK-X-Q01

### CAP-41 — Lesson records with scope

- **Outcome:** An agent receives the lessons that apply to its task, scoped, and lessons stay in the repository.
- **Acceptance:** A committed lesson whose scope matches a ticket is returned by `gov retrieve` for that ticket and not for an out-of-scope ticket.
- **Wave:** W1 (upstream export excluded (DEC-053 Q7), except the lite lesson loop for framework lessons, which is W3 (DEC-165); scope and severity are in the W1 lesson schema (DEC-168))
- **Provider:** W1-08, W1-21, W1-44, W3: lesson packets, shared inbox and triage (lite)
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate Q1, Q2, Q3, Q4; Framework v4.1.2 §67, §68, §75E-75G; Distribution Protocol v1.2 §13-15; DEC-053; DEC-165; DEC-168
- **Covers:**
  - `CAP-41.a` [W1] Lesson lifecycle: report → candidate → corroboration → scope → rule/skill/retrieval/tool proposal → independent validation → owner approval → versioned — Contract v3 Q1; Framework v4.1.2 §67 · delivered by W1-08
  - `CAP-41.b` [W1] Decision vs lesson distinction; lessons cannot silently become policy — Contract v3 Q2, W2; Framework v4.1.2 §68 · delivered by W1-44
  - `CAP-41.c` [W1] PROJECT/PRODUCT/FRAMEWORK scope — Contract v3 Q3 · delivered by W1-08
  - `CAP-41.d` [W1] Phase-2 lessons carried (L-0074, anti-stall, no manufactured history, anti-snowball) — DEC-046; OWNER-DECISION-P2-0008 §9; OWNER-DIRECTION-BR-0004 §2D; OWNER-AMENDMENT-P2-0010 §7 · delivered by W1-44
  - `CAP-41.e` [NONE] Non-goal: the full upstream export gate and FCP loop of Contract v3 Q4; only the lite loop for framework lessons is built (CAP-41.f to CAP-41.j) — Contract v3 Q4; Framework v4.1.2 §75E–75G; DEC-053 Q7; DEC-165
  - `CAP-41.f` [W1] Every lesson record carries a scope (project, product or framework) and a severity (low, medium, high or critical); both fields are in the Wave 1 lesson schema, so the Wave 3 loop needs no migration — DEC-165; DEC-168 · delivered by W1-08
  - `CAP-41.g` [W3] A framework lesson becomes a lesson packet: failure pattern, evidence and suggested change, with no product code, data or secrets; the product's orchestrator writes it to the shared inbox `~/gov-os-lessons-inbox/`; no gitleaks scan while the inbox is private, one full scan before it is shared — DEC-165; EMERGENCY-2 §2.11 (DEC-1211); DEC-1182; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-41.h` [W3] A high or critical lesson is raised to the owner immediately, as a decision package — DEC-165; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-41.i` [W3] The Gov OS orchestrator triages the inbox (deduplicate, rank) into change proposals under the normal cycle; each release's notes list the lessons fixed, with their severity — DEC-165; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-41.j` [W3] Product decisions, specifications and lessons never leave their repository; only lesson packets reach the inbox — DEC-165; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev RETR-X-04, B-X-02 · qual GATE-B-Q01, GATE-B-Q02, AUDIT-B-Q16, AUDIT-B-Q27, RETR-X-Q04

### CAP-42 — Legacy governance retirement and archive policy

- **Outcome:** An agent can retire a repository's legacy governance (rules files, memory, indexes) into archived, inactive state.
- **Acceptance:** After adoption, the retired system contributes zero ACTIVE decisions and zero loaded instructions; its files are archived or imported into `.rulesync/`.
- **Wave:** W1
- **Provider:** rulesync 24.0.0 (import), W1-41
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate R1, R2, R3; Framework v4.1.2 §69-71; DEC-022; DEC-074
- **Covers:**
  - `CAP-42.a` [W1] Legacy governance retirement: rules imported or archived, zero active authority — Contract v3 R1; Framework v4.1.2 §69 · delivered by W1-41
  - `CAP-42.b` [W1] Chat-memory retirement: raw chat DB not active truth; unique knowledge extracted; dependency proof before retirement; CIT-E and index refresh on retirement — Contract v3 R2; Framework v4.1.2 §70 · delivered by W1-41
  - `CAP-42.c` [W1] Archive policy — Contract v3 R3; Framework v4.1.2 §71 · delivered by W1-41
- **Scenarios:** dev CHAOS-B-07, B-01, B-04, B-07, B-11, GATE-B-02 · qual B-X-Q02

### CAP-43 — Canonical OS repo separation and immutable releases

- **Outcome:** The owner can tell exactly which Gov OS version a repository runs; releases never change once tagged.
- **Acceptance:** `framework.lock` records the template tag, commit and file-hash manifest, and `gov doctor` fails when any of them disagrees with the installed kernel.
- **Wave:** W1 (the manifest and file hashes of a release are W2 (CAP-43.b, lite, DEC-722); the release is cut and re-pinned by the owner once the release acceptance passes (EMERGENCY-2 §8.3); release contents of CAP-43.d are friction)
- **Provider:** Copier 9.18.2, W1-39
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S1, S2; Framework v4.1.2 §75A-75D; Distribution Protocol v1.2 §1-8; DEC-023; DEC-027; DEC-064; DEC-722; EMERGENCY-2 §6.1, §8 (DEC-1211); DEC-1214 L3
- **Covers:**
  - `CAP-43.a` [W1] Canonical OS repository separation; developed once — Contract v3 S1; Framework v4.1.2 §75A, §75B · delivered by W1-39
  - `CAP-43.b` [W2] Release contents, lite: the release's own manifest and file hashes, built with the release (the lock on the install side is CAP-02.a, W1); a release is pinned and hash-verified, not signed — Contract v3 S2; Framework v4.1.2 §75D; DEC-722; DEC-1214 L3
  - `CAP-43.c` [W2] Release certification by the release acceptance (EMERGENCY-2 §8.2): the Contract's checks, the proving run, EXAMIN's copy adopted, one EXAMIN feature ticket through the flow — Framework v4.1.2 §75C; DEC-067; EMERGENCY-2 §8.2 (DEC-1211) · delivered by W2-81
  - `CAP-43.d` [W3] Release contents beyond the lite manifest and file hashes of CAP-43.b: semantic version, supported migrations, schema versions, CLI/runtime versions, adapter/capability versions, release notes, affected indexes, required human decisions, rollback procedure — Contract v3 S2; Framework v4.1.2 §75D; DEC-722; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev CHAOS-X-01 · qual CHAOS-X-Q01

### CAP-44 — gov init and gov adopt lifecycle

- **Outcome:** The owner can install the Gov OS into a new repository, or adopt an existing one through the staged A0–A11 transaction with one evidence record per stage, ending in a verdict.
- **Acceptance:** On b-dev, `gov adopt` produces the evidence tree with one record per stage A0–A11; no move happens before an A5 verdict; a failed batch rolls back to its recorded point; the run ends with ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY.
- **Wave:** W3 (W1 delivers gov init (copier copy) and adoption stages A0-A6 and A8 with baseline, rollback points and the A5 independent path-map review (W1-39, W1-41); the lite A7 and A10 gates and the lite verdict are W2 (CAP-44.f, CAP-44.h; DEC-722); stage AS, the lite spec audit, is W2 (CAP-44.m; DEC-1200); A9, A11, the full A7 and A10 gates and the verdict with the ten ADOPTED_HEALTHY conditions are W3 with CAP-47 (CAP-44.k, CAP-44.l; DEC-090))
- **Provider:** Copier 9.18.2, W1-39, W1-41, W2: lite A7/A10 gates + lite verdict (DEC-722), W2: stage AS, the lite spec audit (W2-192, DEC-1200), W3: A9/A11 + full A7/A10 gates + full verdict (with CAP-47)
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S3, S4; Framework v4.1.2 §77-79; Adoption Protocol v3.0 §2-16; Distribution Protocol v1.2 §9, §10; DEC-006; DEC-023; DEC-090; DEC-722; DEC-1200
- **Covers:**
  - `CAP-44.a` [W1] gov init: kernel, overlay, repository contract, initial state, health checks — Contract v3 S3; Framework v4.1.2 §77, §78; Distribution Protocol v1.2 §9 · delivered by W1-39
  - `CAP-44.b` [W1] A0 safety baseline (clean tree, backup ref); A1 cold inventory; A2 classification; A3 target path map; A4 batched plan with rollback points — Contract v3 S4; Adoption Protocol v3.0 §2, §6–§9; Distribution Protocol v1.2 §10 · delivered by W1-41
  - `CAP-44.c` [W1] A5 independent review of the path map before any move (Independent Auditor) — Contract v3 S4; Adoption Protocol v3.0 §10; DEC-090 · delivered by W1-41
  - `CAP-44.d` [W1] A6 controlled migration; failed batch rolls back; moves precede new indexing — Adoption Protocol v3.0 §11; Distribution Protocol v1.2 §10, §11 · delivered by W1-41
  - `CAP-44.e` [W1] A8 legacy memory extraction/retirement — Adoption Protocol v3.0 §13; Distribution Protocol v1.2 §10 · delivered by W1-41
  - `CAP-44.f` [W2] A7 independent migration verification and A10 independent memory verification, lite: each by a fresh Independent Auditor session and recorded as its own stage; A7 checks the A6 migration against the A3 path map and the A4 plan reviewed at A5; A10 checks the A8 legacy memory extraction and retirement, the derived state rebuilt from git and the canary of each index (CAP-55); the fresh auditor runs at A5, AS, A7 and A10 (DEC-1214 G6) — Adoption Protocol v3.0 §12, §15; Distribution Protocol v1.2 §10; DEC-722; DEC-1214 G6
  - `CAP-44.g` [W3] Remediation, finding states, human gates during adoption — Adoption Protocol v3.0 §17–§19; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-44.h` [W2] Adoption verdict, lite: ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY from a fresh Independent Auditor against the lite conditions: A0–A6 and A8 with their stage records and the A5 review, the native layout kept, the lite A7 and A10 gates passed, the pinned, hash-verified release (gov doctor MATCH), gov doctor green (exit 0), gov check with no RED family, and one ticket closed by gov close at exit 0 with the repository's own test command; of the ten ADOPTED_HEALTHY conditions of Adoption Protocol v3.0 §20, the lite conditions check those marked W2 and the lite part named for those marked W3: (1) certified kernel pinned: W3 (the certification by qualification is CAP-43.c), its lite part the pinned, hash-verified release (CAP-02.a, CAP-43.b), (2) project overlay separate: W3, no lite part, (3) path mapping, with the A5 independent review passed: W2 (the A3 path map, the A5 review and the native layout kept, CAP-44.b, CAP-44.c, CAP-44.j), (4) migration independently verified: W3 (a separate verifier role, CAP-47.a), its lite part the lite A7 gate (CAP-44.f), (5) legacy authority retired: W3 (no accidental legacy authority, CAP-48.b), its lite part A8's retirement of legacy memory (CAP-44.e), (6) memory independently verified: W3 (over the A9 knowledge fabric and by a separate role, CAP-44.k, CAP-47.a), its lite part the lite A10 gate (CAP-44.f), (7) comprehensive v4 audit completed: W3 (A11, CAP-44.k), no lite part, (8) critical/high unaccepted findings resolved: W3 (finding states and remediation, CAP-44.g, and the A11 audit), no lite part, (9) runtime rebuildable: W3 (derived memory rebuildable, CAP-48.b), its lite part the derived state rebuilt from git that the lite A10 gate checks (CAP-20), (10) clean-machine reconstruction demonstrated: W3 (CAP-48.b), no lite part; ADOPTED_HEALTHY when every lite condition is met; ADOPTED_WITH_ACCEPTED_EXCEPTIONS when each lite condition not met is accepted by name in an owner decision (Role: owner); otherwise NOT_ADOPTED_HEALTHY; only the owner accepts an exception; the auditor accepts none; the verdict record names itself lite and names the conditions it does not check; at the release, EXAMIN's copy gets its verdict with memory at 95 % or more end to end on a fresh 80 (EMERGENCY-2 §8.2 item 3) — Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722; EMERGENCY-2 §8.2 (DEC-1211)
  - `CAP-44.i` [W3] Interrupted-session recovery and freeze during adoption — Adoption Protocol v3.0 §4; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-44.j` [W1] The path map keeps a healthy native framework/package layout unless the target structure is materially better and the migration risk is justified — Framework v4.1.2 §79.3; Distribution Protocol v1.2 §10 A3 · delivered by W1-41
  - `CAP-44.k` [W3] A9 new knowledge fabric; A11 full audit; A7 and A10 beyond their lite form in CAP-44.f (separate verifier roles, A10 over the A9 knowledge fabric) — Adoption Protocol v3.0 §12, §14–§16; Distribution Protocol v1.2 §10; DEC-722; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-44.l` [W3] Final verdict ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY with the ten ADOPTED_HEALTHY conditions, after A0–A11 — Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-44.m` [W2] AS spec audit, lite: after A2 and before A3, `gov adopt --lite --stage AS` records every spec found (path, title, its stated wave or status), each built, partly built or not built with evidence (code paths, tests, commits), the tickets found done or not by wave, the specs with no code, the code with no spec (top-level code modules no spec names), and each gap as one question to the owner with a place for the answer; the lite checks (every spec and every top-level code module the inventory holds named, every gap with a question) refuse a record that fails either; A3 refuses to run before AS is recorded; built or not is judged from code paths, tests and commits, never by a model; the path map's reviewer at A5 reads the record — DEC-1200; P-ADOPT-SPEC-AUDIT-1 · delivered by W2-192
- **Scenarios:** dev B-01, B-04, B-05, B-X-01 · qual B-X-Q01

### CAP-45 — gov update lifecycle

- **Outcome:** The owner can update the Gov OS in a repository without losing his overlay or his own edits, and without re-adopting.
- **Acceptance:** `gov update --check` reports the version change and migrations; `gov update` installs the pinned, hash-verified release and applies it with a three-way merge that keeps the owner's own edits and the overlay files, and `gov doctor` is green, with no re-adopt.
- **Wave:** W2 (`gov update` is built in the release (EMERGENCY-2 §6.1, §7.6), which brings it back from Wave 3, where DEC-1089 and DEC-1090 had put it)
- **Provider:** Copier 9.18.2, W2-17, W2-18 (pinned install), W2-17: gov doctor pending-update report
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-023; DEC-165; DEC-1090; EMERGENCY-2 §6.1, §8 (DEC-1211); DEC-1214 Q-UPD; DEC-1214 L3
- **Covers:**
  - `CAP-45.a` [W2] gov update: check/impact, authenticated source (the release's manifest and file hashes, CAP-43.b; no signature, DEC-1214 L3), compatibility/migration, a three-way merge that keeps the owner's own edits and the overlay, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance — Contract v3 S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-722; DEC-1090; EMERGENCY-2 §6.1 (DEC-1211); DEC-1214 Q-UPD · delivered by W2-17, W2-18
  - `CAP-45.b` [W2] In every repository, `gov doctor` compares the installed release with the latest and reports pending updates and their highest lesson severity at session start; the owner decides when to run `gov update` — DEC-165 · delivered by W2-17
- **Scenarios:** dev CHAOS-A-10, CHAOS-X-01 · qual CHAOS-X-Q01

### CAP-46 — Cross-machine sync via git

- **Outcome:** The owner can move to another machine with git alone.
- **Acceptance:** A fresh clone followed by `gov doctor` and `gov rebuild` gives a working environment whose derived digest equals the source machine's.
- **Wave:** W1
- **Provider:** W1-27
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S6; Framework v4.1.2 §83; Distribution Protocol v1.2 §16; DEC-057
- **Covers:**
  - `CAP-46.a` [W1] Clone + doctor + rebuild reproduces the environment — Contract v3 S6; Framework v4.1.2 §83; Distribution Protocol v1.2 §16 · delivered by W1-27
- **Scenarios:** dev CHAOS-A-09, ISO-X-01, CHAOS-X-01 · qual ISO-X-Q01

### CAP-47 — Independent adoption/audit roles and fresh-session independence

- **Outcome:** The owner gets independent verification from fresh sessions that did not build what they check.
- **Acceptance:** A fresh verifier session with only the bounded context pack runs held-out tests and reports; its transcript contains no builder chat.
- **Wave:** W3 (Independent Test Designer and Independent Auditor roles in W1 (W1-33), including the A5 path-map review (DEC-090); the lite A7 and A10 gates and the AS spec audit W2 by that Independent Auditor role (CAP-44.f, DEC-722); full independent adoption/audit roles and the full A7, A10 and A11 gates W3)
- **Provider:** W1-33, W3: independent adoption/audit roles, W1-13, W1-35, W1-36, W1-43
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate T1, T2, T3; Adoption Protocol v3.0 §3; DEC-042 (builder tests are regression, not certification); DEC-066; DEC-070; DEC-088; DEC-090; DEC-1214 G6
- **Covers:**
  - `CAP-47.a` [W3] Role separation for adoption and audit — Contract v3 T1; Adoption Protocol v3.0 §3; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-47.b` [W1] Fresh-session independence with a bounded context pack — Contract v3 T2; DEC-042; OWNER-AMENDMENT-P2-0010 · delivered by W1-36
  - `CAP-47.c` [W3] Adoption evidence tree — Contract v3 T3; Adoption Protocol v3.0 §5; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-47.d` [W1] Audit triggers: the release acceptance and adoption stages A5, AS, A7 and A10; otherwise only a red test, a failed landing or merge, or a feature that does not work as intended — MR-4; DEC-1214 G6 (a); EMERGENCY-2 §3.4, §3.6 (DEC-1211) · delivered by W1-13, W1-35, W1-36
- **Scenarios:** dev AUDIT-X-01 · qual AUDIT-X-Q01

### CAP-48 — Framework health SLOs and healthy-repo definition

- **Outcome:** The owner can see the Gov OS's health against SLOs.
- **Acceptance:** `gov health` shows index freshness, test status and governance share as G/Y/R against configured SLOs.
- **Wave:** W3 (subset in `gov doctor` from W1)
- **Provider:** W1-27, W3: health SLOs
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate U; Framework v4.1.2 §75, §76; DEC-004
- **Covers:**
  - `CAP-48.a` [W3] SLOs tracked with thresholds: suite freshness, product-test health, the end-to-end judged memory figure (not Recall@K), stale-index count, orphan-graph count, unresolved contradictions, unresolved human gates, task traceability %, readiness coverage, packet size, tokens per completed task, first-pass completion, handoff failure, memory rebuild success, fresh-agent reconstruction success — Contract v3 U; Framework v4.1.2 §75; EMERGENCY-2 §5.2 (DEC-1211); EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-48.b` [W3] HEALTHY only when: authority unambiguous; no accidental legacy authority; deterministic state consistent; freshness passes; retrieval meets thresholds; sensitive material isolated; readiness explicit; task states correct; tests/traceability satisfy policy; suite current/green; no unresolved critical finding; fresh agent reconstructs within budget; derived memory rebuildable — Contract v3 U; Framework v4.1.2 §76; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev SOAK-X-02 · qual SOAK-X-Q02

### CAP-49 — Qualification oracle (synthetic repos, fault injection, hidden tests)

- **Outcome:** The owner can prove the Gov OS on synthetic repositories against a held-out oracle before the release.
- **Acceptance:** A fresh executor runs the proving run on W2-81's synthetic repositories and produces a scorecard in SCORECARD_FORMAT; any forbidden outcome fails; the hidden sets are protected by the transcript scan (CAP-66): the transcripts written between a set's writing and the end of its measure contain neither its path nor its question ids, or the measure is void.
- **Wave:** W2 (the pack exists (S0b1); it runs as the release proving run (EMERGENCY-2 §8.2 item 2))
- **Provider:** synthetic Programmes A and B, held-out oracle, qualification executor, W2-81 (the six synthetic repositories)
- **Disposition:** KEPT (DROP in S0a; KEPT as qualification by DEC-067)
- **Sources:** Contract v3 Gate V1, V2, V3, V4; DEC-067; DEC-071; EMERGENCY-2 §2.7, §8.2 (DEC-1211)
- **Covers:**
  - `CAP-49.a` [W2] Fault manifest; hidden path-map and memory oracles, protected by the transcript scan (CAP-66); quantitative scoring; forbidden outcomes fail — Contract v3 V1–V4; DEC-067; EMERGENCY-2 §2.7, §8.2 (DEC-1211) · delivered by W2-81
  - `CAP-49.b` [NONE] Non-goal: the oracle hidden from a launched worker's Bash by the sandbox and a `Read` deny rule: no sandbox; the transcript scan (CAP-66) detects a read instead — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-49.c` [NONE] Non-goal: the oracle hidden from every session by a `Read` deny rule in the committed settings and the guard refusing any call that names its path: no guard; the transcript scan (CAP-66) detects a read instead — EMERGENCY-2 §2.2 (DEC-1211)
- **Scenarios:** dev — · qual —

### CAP-50 — Artifact flow, dependency consumption and end-to-end traceability

- **Outcome:** An agent can tell which evidence becomes stale when a requirement changes.
- **Acceptance:** Changing a requirement marks every dependent test result, packet and synthesis note stale, listed by id.
- **Wave:** W3 (trailers and graph in W1; full W1–W12 in W3)
- **Provider:** W1-10, W1-30, W3: Gate W traceability, W1-08
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate W1-W12; Framework v4.1.2 §36-38; DEC-036; DEC-064
- **Covers:**
  - `CAP-50.a` [W1] Stable artefact identity: id, type, canonical path, status, lifecycle, version/hash, provenance, lineage, expected consumers — Contract v3 W1 · delivered by W1-08
  - `CAP-50.b` [W3] Typed output→input contracts with required/optional dependencies and output schemas — Contract v3 W2; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-50.c` [W1] Consumption receipt and implementation traceability — Contract v3 W5 · delivered by W1-30
  - `CAP-50.d` [W3] Upstream-change staleness propagation; COMPLETE is not permanently valid — Contract v3 W6; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-50.e` [W3] Orphan/dead-output detection with governed remediation — Contract v3 W7; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-50.f` [W3] Artifact-flow health metrics: delivery accuracy, current-version accuracy, superseded leakage, missing-input detection, staleness accuracy, requirement→code and →test coverage, orphan recall, reconstruction correctness — Contract v3 W11; EMERGENCY-2 §8.4 (DEC-1211)
  - `CAP-50.g` [W3] Health-scheduler integration — Contract v3 W12; EMERGENCY-2 §8.4 (DEC-1211)
- **Scenarios:** dev A-X-01 · qual CHAOS-X-Q02, A-X-Q01

### CAP-51 — Decisions register (structured, versioned, authoritative)

- **Outcome:** An agent can rely on one structured, versioned register of decisions with supersession.
- **Acceptance:** Superseding a decision updates both records' status and links, and the checker flags an ACTIVE record that is superseded, a duplicate id or a cycle.
- **Wave:** W1
- **Provider:** MADR + check-jsonschema 0.38.2, W1-11, W1-21
- **Disposition:** KEPT
- **Sources:** Framework v4.1.2 §2, §68; Contract v3 Gate C1 (decisions); Contract v3 Gate L1 (contradiction resolution); DEC-030 (authority/current/superseded filtering); DEC-012; DEC-074
- **Covers:**
  - `CAP-51.a` [W1] Structured, versioned decisions with supersession; contradiction resolution — Framework v4.1.2 §2, §68; Contract v3 C1, L1 · delivered by W1-11
  - `CAP-51.b` [W1] Authority/current/superseded filtering in retrieval — DEC-030 · delivered by W1-21
- **Scenarios:** dev CHAOS-B-08, B-02, RETR-B-01, AUDIT-B-01, AUDIT-B-02, AUDIT-B-05, AUDIT-B-06 · qual MR-A-Q06, AUDIT-A-Q03, AUDIT-A-Q06, AUDIT-A-Q10, AUDIT-A-Q21, AUDIT-A-Q24, MR-B-Q05, GATE-B-Q03, AUDIT-B-Q01, AUDIT-B-Q04, AUDIT-B-Q05, AUDIT-B-Q06 (+7 not listed in the matrix row)

### CAP-52 — Model-agnostic adapters (provider, IDE, CLI)

- **Outcome:** The owner can use Claude Code or an AGENTS.md-reading harness with the same rules, generated from one source.
- **Acceptance:** `rulesync generate` produces CLAUDE.md, AGENTS.md and `.claude/`; CI fails when a generated file differs from its source; the Claude Code adapter carries the checkpoint hooks and the two deny lines (`git push`, `sudo`).
- **Wave:** W1
- **Provider:** rulesync 24.0.0, W1-38
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate A1 (model-agnostic); Framework v4.1.2 §4, §22; OWNER-LAUNCHER-BR-0001 (Claude Code first, others later); DEC-022; DEC-074; EMERGENCY-2 §2.2, §2.4 (DEC-1211)
- **Covers:**
  - `CAP-52.a` [W1] Model-agnostic adapters for Claude Code and AGENTS.md from one source — Contract v3 A1; Framework v4.1.2 §4, §22; DEC-074 Q6 · delivered by W1-38
  - `CAP-52.b` [W1] Claude Code first, others later — OWNER-LAUNCHER-BR-0001 · delivered by W1-38
- **Scenarios:** dev ISO-X-03 · qual CHAOS-X-Q06

### CAP-53 — Proportionality profiles (LITE/STANDARD/FULL)

- **Outcome:** The owner gets ceremony in proportion to the work: a feature, a fix or a chore, with model, effort and checks from the owner's rubric.
- **Acceptance:** A feature ticket carries its profile (LITE, STANDARD or FULL) and the model, effort and checks follow from its class in the rubric; a fix is recorded in its owning ticket and a chore is a direct commit listed in the digest, neither with a ticket of its own; the profiles stay until the measured rubric replaces them (DEC-1208, DEC-1120).
- **Wave:** W2 (profiles declared per ticket in W1 (W1-09); the rubric replaces computing the profile from impact)
- **Provider:** W1-09, W1-08, W1-13, W1-31, W2-121c (the launcher states the rubric's model and effort)
- **Disposition:** KEPT
- **Sources:** DEC-005 (proportionality profiles); DEC-035 (radius-scaled budgets/facets); DEC-004 (governance overhead budget 10-15%); OWNER-DIRECTION-P2-0009 §11; DEC-085; DEC-1120; DEC-1208; EMERGENCY-2 §4.1, §4.5, §4.6 (DEC-1211)
- **Covers:**
  - `CAP-53.a` [W1] Work is a feature, a fix or a chore; model, effort and checks come from the measured rubric; the profiles LITE/STANDARD/FULL by radius, with readiness rows per profile, stay until the rubric replaces them — DEC-005; DEC-085; EMERGENCY-2 §4.5 (DEC-1211) · delivered by W1-13, W1-08
  - `CAP-53.b` [NONE] Non-goal: a profile computed from impact (`gov impact`): the rubric replaces it — EMERGENCY-2 §4.5 (DEC-1211)
  - `CAP-53.c` [W1] Governance budget within profile — DEC-004; OWNER-DIRECTION-P2-0009 §11 · delivered by W1-31
- **Scenarios:** dev MR-X-02 · qual MR-X-Q02

### CAP-54 — Progressive adoption (day-one to maturity)

- **Outcome:** The owner can govern a repository from day one while its full migration continues in batches.
- **Acceptance:** A repository with only the kernel installed passes `gov doctor` at the minimal level, and later adoption batches raise its level without reinstalling.
- **Wave:** W1
- **Provider:** W1-39, W1-41, W1-27, W1-08
- **Disposition:** KEPT
- **Sources:** DEC-006 (progressive adoption); OWNER-DIRECTION-P2-0009 §2 (simplification principle); Framework v4.1.2 §7 (every mature repo should identify systems, even minimally)
- **Covers:**
  - `CAP-54.a` [W1] Governable from day one; A0–A11 remains the target for ADOPTED_HEALTHY — DEC-006 · delivered by W1-27
  - `CAP-54.b` [W1] Simplification principle; minimal system identification — OWNER-DIRECTION-P2-0009 §2; Framework v4.1.2 §7 · delivered by W1-08
- **Scenarios:** dev B-X-01 · qual B-X-Q01

### CAP-55 — Retrieval stopping reasons

- **Outcome:** An agent always knows why retrieval stopped, and an empty result is never taken as absence.
- **Acceptance:** Every evidence bundle carries one stopping reason from the fixed list; a canary miss on an index yields FACET_UNAVAILABLE, and the validator rejects a bundle without a stopping reason.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-21, W1-22
- **Disposition:** KEPT
- **Sources:** DEC-034 (stopping reasons); DEC-037 (zero-result canaries); OWNER-DIRECTION-BR-0005 §5; DEC-080
- **Covers:**
  - `CAP-55.a` [W1] Fixed stopping reasons; NOT_FOUND never proof of absence; canaries per index — DEC-034; DEC-037; OWNER-DIRECTION-BR-0005 §5 · delivered by W1-21, W1-22
- **Scenarios:** dev RETR-X-02 · qual RETR-X-Q02

### CAP-56 — Retrieval in disposable subagent context

- **Outcome:** An agent keeps retrieval out of its own context: facet retrieval runs in disposable subagents and only the cited bundle returns.
- **Acceptance:** On RETR-X-02 the main session's transcript contains the bundle and none of the intermediate retrieval batches.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-36
- **Disposition:** KEPT
- **Sources:** DEC-032 (retrieval loop in disposable subagent); DEC-031 (two budgets: retrieval spend vs final packet); DEC-080
- **Covers:**
  - `CAP-56.a` [W1] Retrieval in a disposable subagent; only the cited bundle returns — DEC-032 · delivered by W1-36
- **Scenarios:** dev CHAOS-A-11, RETR-X-02 · qual CHAOS-B-Q06, CHAOS-B-Q07, CHAOS-B-Q08, CHAOS-B-Q09, RETR-X-Q02

### CAP-57 — Deterministic worklist closure for facets

- **Outcome:** An agent gets the same dependency closure for referenced ids every time, with no model involved.
- **Acceptance:** `gov closure` over the same commit and depth returns byte-identical output on repeated runs and reports DEPTH_LIMIT_REACHED with the gap list when the depth is hit.
- **Wave:** W1 (DEC-080)
- **Provider:** W1-20, W1-22
- **Disposition:** KEPT
- **Sources:** DEC-033 (deterministic worklist closure over referenced IDs); DEC-036 (synthesis notes with deterministic citation check); DEC-080
- **Covers:**
  - `CAP-57.a` [W1] Deterministic closure over referenced ids to radius-scaled depth; synthesis citation check — DEC-033; DEC-036 · delivered by W1-20, W1-22
- **Scenarios:** dev RETR-X-03 · qual RETR-X-Q03

### CAP-58 — Containment judged at the landing

- **Outcome:** An agent works inside its task's declared paths. A change outside them is a notice in the landing's record; only a change that breaks test authorship is refused (MR-3).
- **Acceptance:** At the landing, each commit's paths are judged against the allowed paths of its `Role` and `Task` trailers: a path outside them is a notice in the land record and never a refusal; a commit that changes `tests/acceptance/` without `Role: independent-test-designer` (or the owner's `Role: owner`) is refused, naming the commit. Nothing is refused at write time.
- **Wave:** W1 (the guard and its allow-lists are retired (EMERGENCY-2 §2.2); containment is a landing check (NEW-1, CAP-63))
- **Provider:** W1-50, W2-115b
- **Disposition:** KEPT
- **Sources:** DEC-041 (default-deny allow-lists, derived not enumerated); DEC-076; DEC-152; DEC-153; DEC-156; DEC-161; EXP-001 (spike-sandbox/EVIDENCE.md §5.4); DEC-165; DEC-171; DEC-255; EMERGENCY-2 §2.1, §2.2, §4.3, §4.4 (DEC-1211)
- **Covers:**
  - `CAP-58.a` [NONE] Non-goal: default-deny write allow-lists per role and ticket: the guard is retired — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-58.b` [NONE] Non-goal: permission classes enforced as role permissions by the guard: no guard, no permission editing — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-58.c` [NONE] Non-goal: a session with no or an unknown role has no write privilege: nothing refuses a write; the landing judges the commit — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-58.d` [NONE] Non-goal: the claim split by tool between the OS sandbox and the guard: neither exists — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-58.e` [NONE] Non-goal: the orchestrator's write scope under the guard: there is no guard to except it from — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-58.f` [NONE] Non-goal: the containment check on `PostToolUseFailure`: a hook-time check; the landing judges commits instead — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-58.g` [NONE] Non-goal: the lessons inbox as a guard exception: there is no guard — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-58.h` [W1] Containment judged at the landing by commit trailers: a forward HEAD move, including an integration merge, is judged commit by commit, each commit's paths against the allowed paths of its own `Role` and `Task` trailers; a path outside them is a notice, never a refusal; only a test-authorship breach (MR-3) is refused; a merge commit is not a finding when every commit it brings passes; a commit with no `Role` or `Task` trailer is judged against the caller — DEC-255; DEC-182; EMERGENCY-2 §4.3 (DEC-1211) · delivered by W1-50, W2-115b
- **Scenarios:** dev MR-A-01, CHAOS-A-13, CHAOS-A-14, MR-B-01, CHAOS-B-13, CHAOS-B-14, CHAOS-B-15, A-X-02 · qual MR-A-Q01, SEC-A-Q02, AUDIT-A-Q49, SEC-A-Q06, MR-B-Q02, SOAK-X-Q02

### CAP-59 — Review-repair loop budget

- **Outcome:** The owner never sees an endless loop: any review→repair, audit→repair, test→fix or verification loop runs at most two rounds, and then the owner decides once, from an escalation package with options.
- **Acceptance:** After two rounds on the same surface the review tool refuses a third and puts one escalation package in chat (each round's outcome, why it is not converging, options: fix differently, narrow, split, defer, delete, continue); READY is computed from the reviewers' verdict blocks; the round count never appears in the output seen by the looping session.
- **Wave:** W1
- **Provider:** W1-30, W1-43, W1-44
- **Disposition:** KEPT
- **Sources:** DEC-044 as amended by DEC-096 (loop policy); OWNER-DIRECTION-P2-0009 §2 (simplification principle); DEC-1204; EMERGENCY-2 §3.3 (DEC-1211)
- **Covers:**
  - `CAP-59.a` [W1] Loops (review→repair, audit→repair, test→fix, verification) run at most two rounds; then one escalation package with each round's outcome, the reason it is not converging and the options fix differently / narrow / split / defer / delete / continue; the owner decides once; READY is computed by code — DEC-044 as amended by DEC-096; OWNER-DIRECTIVE-0003; OWNER-AUTHORISATION-P2-0006; DEC-1204 · delivered by W1-30, W1-43
  - `CAP-59.b` [W1] Iteration count and budget held by the orchestrator or gov, never disclosed to sessions inside the loop — DEC-096 · delivered by W1-30, W1-43
  - `CAP-59.c` [W1] Anti-snowball: finding → whole-system context → one disposition before code — OWNER-AMENDMENT-P2-0010 §7 · delivered by W1-30, W1-44
- **Scenarios:** dev MR-X-03 · qual MR-X-Q03

### CAP-60 — Below-floor recovery (break-glass)

- **Outcome:** (none — non-goal)
- **Acceptance:** No kernel file implements break-glass or DEGRADED-mode recovery; the wave-exit audit finds none (DEC-070).
- **Wave:** NONE (dropped)
- **Provider:** none (non-goal)
- **Disposition:** DROP — Non-goal: below-floor recovery, break-glass and DEGRADED mode rest on the signed-release-root chain, which is not built (ADR-0001).
- **Sources:** OWNER-DECISION-0006; OWNER-DECISION-0007; DEC-039
- **Covers:**
  - `CAP-60.a` [NONE] Non-goal: below-floor recovery, break-glass, DEGRADED mode — OWNER-DECISION-0006; OWNER-DECISION-0007; DEC-039
- **Scenarios:** dev — · qual —

### CAP-61 — Worker session launcher

- **Outcome:** The orchestrator can start a worker session (engineer, independent test designer, independent auditor, research or experiment) in its own worktree with its role file and the model and effort the owner's rubric gives it, and with no permission prompt.
- **Acceptance:** `gov launch` starts a worker in its worktree with its role file, `GOV_ROLE`, `GOV_TICKET`, its own temp folder and the rubric's model and effort, with no permission prompt; it refuses a launch whose model or effort the rubric does not give for that role.
- **Wave:** W1
- **Provider:** Claude Code sandbox (bubblewrap 0.9.0, socat 1.8.0.0), W1-46, W1-48
- **Disposition:** KEPT
- **Sources:** DEC-138; DEC-141; DEC-152; DEC-153; DEC-158; DEC-159; DEC-160; DEC-161; EXP-001 (spike-sandbox/EVIDENCE.md §5.2–5.5); DEC-163; DEC-164; EMERGENCY-2 §2.2, §2.3, §6.1 (DEC-1211)
- **Covers:**
  - `CAP-61.a` [NONE] Non-goal: the launcher refuses a worker unless the OS sandbox is on, strict and fail-closed: there is no sandbox — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-61.b` [W1] `gov launch` starts a worker in its worktree with its role file, `GOV_ROLE`, `GOV_TICKET` and the rubric's model and effort; in-session subagents remain for read-only work (review, exploration, web research); no permission prompt, no per-role `--settings` sandbox block — DEC-153; DEC-161; EXP-001 §5.3; EMERGENCY-2 §2.2 (DEC-1211) · delivered by W1-46
  - `CAP-61.c` [NONE] Non-goal: the network profile per role, held by the sandbox and generated `Edit` deny rules: no sandbox, no allowlist — EMERGENCY-2 §2.2 (DEC-1211)
  - `CAP-61.d` [W1] The launcher sets a per-session temp directory for each worker session; if the acceptance test shows it cannot be overridden, the shared `$TMPDIR` is recorded as a residual — DEC-159 · delivered by W1-46
  - `CAP-61.e` [W1] Sessions run on Claude Code 2.1.285 or later, and the CLI used for headless runs is aligned with the VS Code extension's bundled version — DEC-153; EXP-001 §5.5 · delivered by W1-48
  - `CAP-61.f` [NONE] Non-goal: the untested sandbox cases of EXP-002: there is no sandbox to test — EMERGENCY-2 §2.2 (DEC-1211)
- **Scenarios:** dev — · qual —

### CAP-62 — Sandbox escape hatch denied

- **Outcome:** (none — non-goal)
- **Acceptance:** No file of the kernel implements a sandbox or the denial of its escape hatch; the release acceptance finds none (EMERGENCY-2 §2.2).
- **Wave:** NONE (dropped)
- **Provider:** none (non-goal)
- **Disposition:** DROP — Non-goal: the sandbox escape hatch is moot where there is no sandbox (EMERGENCY-2 §2.2).
- **Sources:** DEC-152; DEC-153; EXP-001 (spike-sandbox/EVIDENCE.md §5.4); EMERGENCY-2 §2.2 (DEC-1211)
- **Covers:**
  - `CAP-62.a` [NONE] Non-goal: the guard denies a Bash call carrying `dangerouslyDisableSandbox: true`: no sandbox, no guard — EMERGENCY-2 §2.2 (DEC-1211)
- **Scenarios:** dev — · qual —

### CAP-63 — The landing

- **Outcome:** A ticket lands by one deterministic action, in minutes, in Gov OS and in an adopted repository: the merge, the impact-selected tests, the path and authorship checks and the close record are one step.
- **Acceptance:** `gov queue` merges a ticket's branch into integration, runs the impact-selected tests on the merged result, checks trailers, paths, test authorship, a committed tree, store freshness and disk, writes the ticket's close record itself and closes the ticket at the land; the merge, tests and checks of one EXAMIN feature ticket finish in minutes; a red landing names its cause.
- **Wave:** W2
- **Provider:** W2-115b (gov queue), W2-193, W2-194
- **Disposition:** KEPT
- **Sources:** EMERGENCY-2 §4.3, §4.4 (DEC-1211); DEC-1214 L1, L2, Q-CLOSE; DEC-906; DEC-1052; DEC-1116
- **Covers:**
  - `CAP-63.a` [W2] The landing merges, runs the impact-selected tests on the merged result and checks trailers, containment (a notice), test authorship, a committed tree, store freshness and disk — EMERGENCY-2 §4.3, §4.4 (DEC-1211) · delivered by W2-115b
  - `CAP-63.b` [W2] The landing writes the ticket's close record and closes the ticket at the land; no separate close step carries weight of its own (DEC-1214 L2) — EMERGENCY-2 §4.3, §4.4 (DEC-1211) · delivered by W2-115b
  - `CAP-63.c` [W2] A red landing is fixed by finding and removing its cause; the fix lands without a new ticket; a red already on the base is recorded as a known base red (DEC-1214 Q-CLOSE) — EMERGENCY-2 §4.3, §4.4 (DEC-1211) · delivered by W2-193, W2-194
  - `CAP-63.d` [W2] The landing exists in an adopted repository (`gov queue`), not only among Gov OS's own tools — EMERGENCY-2 §4.3, §4.4 (DEC-1211) · delivered by W2-115b
- **Scenarios:** dev — · qual —

### CAP-64 — The run-time tool

- **Outcome:** The work keeps going without the owner as the relay: ready tickets start in the slots the machine has, a finished session is told to its lead, and a stalled session is woken.
- **Acceptance:** RT-1 to RT-8 each pass their own verify (EMERGENCY-2 §6.3): no ready ticket waits more than 10 minutes while the machine has room for it; the orchestrating session gets a message within 2 minutes of any lead, worker or job finishing; slots come from the CPU, RAM and GPU detected at start; zero GPU spill events; a session resumes after a compaction, restart or crash at its recorded next step; messages go through per-session inbox files and none passes through the owner; one watcher process; the launcher states the rubric's model and effort.
- **Wave:** W2
- **Provider:** W2-121c, W2-121d, W2-156
- **Disposition:** KEPT
- **Sources:** EMERGENCY-2 §6.3, A-5 (DEC-1211); DEC-1007; DEC-1030; DEC-1214 T1, T2, T3
- **Covers:**
  - `CAP-64.a` [W2] RT-1: no ready ticket waits more than 10 minutes while the machine has room for it (verify: a week of the tool's log) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
  - `CAP-64.b` [W2] RT-2: the orchestrating session gets a message within 2 minutes of any lead, worker or job finishing (verify: finish times against message times) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c, W2-121d
  - `CAP-64.c` [W2] RT-3: slots come from the CPU, RAM and GPU detected at start, with no machine-specific constant (verify: one configuration runs on two simulated machine profiles) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
  - `CAP-64.d` [W2] RT-4: zero GPU spill events; embedders and rerankers stay on the GPU, even if that limits parallel leads (verify: the GPU log; DEC-1214 T3) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
  - `CAP-64.e` [W2] RT-5: after a compaction, restart or crash a session resumes at the recorded next step without the owner restating it (CAP-37; verify: a forced compaction and a killed session) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
  - `CAP-64.f` [W2] RT-6: messages between CTOs, leads, workers and the operator go through per-session inbox files with a read mark; none passes through the owner (verify: a week of owner messages carries no relays) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
  - `CAP-64.g` [W2] RT-7: one state file and one wake rule replace today's watcher layers (verify: one watcher process) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c, W2-121d
  - `CAP-64.h` [W2] RT-8: the launcher picks the model and effort from the rubric and states them (verify: the launch log) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
  - `CAP-64.i` [W2] A stalled session is detected by the dispatcher's cron pass, a shell script that costs no model (DEC-1214 T1) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
  - `CAP-64.j` [W2] The owner is pushed to his phone when the CTO needs his decision (features, specs, KPIs, data and measurement, P1 decisions touching the core or the kernel) (DEC-1214 T2) — EMERGENCY-2 §6.3, A-5 (DEC-1211) · delivered by W2-121c
- **Scenarios:** dev — · qual —

### CAP-65 — Memory by construction

- **Outcome:** Every agent uses memory because its brief carries it, not because it remembers to ask.
- **Acceptance:** Every brief `gov brief` writes holds the ticket's whole retrieval bundle and no unfilled `{…}` placeholder; every role template and every skill says memory first and none forbids `gov retrieve`; the memory-use log has a line for each retrieve.
- **Wave:** W2
- **Provider:** W2-197
- **Disposition:** KEPT
- **Sources:** EMERGENCY-2 §5.4, §5.6, §5.7 (DEC-1211); DEC-836; DEC-1210
- **Covers:**
  - `CAP-65.a` [W2] Every brief carries the ticket's retrieval bundle, uncut (CAP-15) — EMERGENCY-2 §5.4, §5.6, §5.7 (DEC-1211) · delivered by W2-197
  - `CAP-65.b` [W2] Every template and every skill says memory first; the brief template no longer says "No `gov retrieve` in the sandbox" — EMERGENCY-2 §5.4, §5.6, §5.7 (DEC-1211) · delivered by W2-197
  - `CAP-65.c` [W2] A memory-use log records each retrieve: who asked, when, the question and what came back — EMERGENCY-2 §5.4, §5.6, §5.7 (DEC-1211) · delivered by W2-197
- **Scenarios:** dev — · qual —

### CAP-66 — The hidden-set scan

- **Outcome:** A hidden question set that an agent has read is detected, and its measure is void.
- **Acceptance:** The transcripts written between a set's writing and the end of its measure contain neither its path nor its question ids, or the measure is void; the memory reader runs with only the memory tool and the gold sits outside the index.
- **Wave:** W2
- **Provider:** W2: the transcript scan (A-12)
- **Disposition:** KEPT
- **Sources:** EMERGENCY-2 §2.7, A-12 (DEC-1211); DEC-1214 E3
- **Covers:**
  - `CAP-66.a` [W2] The transcript scan reads every transcript written between the set's writing and the end of its measure, looking for the set's path and its question ids; a hit voids the measure — EMERGENCY-2 §2.7, A-12 (DEC-1211)
  - `CAP-66.b` [W2] The memory reader runs with only the memory tool, and the gold sits outside the index and outside the clone — EMERGENCY-2 §2.7, A-12 (DEC-1211)
- **Scenarios:** dev — · qual —

### CAP-67 — Backups

- **Outcome:** The owner can recover any repository from a bundle less than an hour old.
- **Acceptance:** Each repository has a `git bundle` kept outside its tree that is less than an hour old.
- **Wave:** W2
- **Provider:** W2: the hourly bundle job
- **Disposition:** KEPT
- **Sources:** EMERGENCY-2 §2.8 (DEC-1211); DEC-848
- **Covers:**
  - `CAP-67.a` [W2] An hourly `git bundle` of each repository, kept outside the tree — EMERGENCY-2 §2.8 (DEC-1211)
- **Scenarios:** dev — · qual —

### CAP-68 — The basis line

- **Outcome:** No new rule arrives without the incident behind it.
- **Acceptance:** A decision record that adds a rule names its incident in a basis line, `gov check` fails a decision-record commit without one, and a weekly basis review lists the rules added since the last.
- **Wave:** W2
- **Provider:** W2: the basis-line check (A-8)
- **Disposition:** KEPT
- **Sources:** EMERGENCY-2 §10.1, A-8 (DEC-1211)
- **Covers:**
  - `CAP-68.a` [W2] A new rule's decision record names its incident, checked by code at the decision-record commit — EMERGENCY-2 §10.1, A-8 (DEC-1211)
  - `CAP-68.b` [W2] A weekly basis review lists the rules added since the last review — EMERGENCY-2 §10.1, A-8 (DEC-1211)
- **Scenarios:** dev — · qual —

### CAP-69 — Transcripts kept

- **Outcome:** The owner can see what any session did for a year.
- **Acceptance:** The harness setting `cleanupPeriodDays` is 365 in the owner's settings.
- **Wave:** W1 (built: the owner's setting)
- **Provider:** the owner's `~/.claude/settings.json`
- **Disposition:** KEPT
- **Sources:** EMERGENCY-2 §10.3 (DEC-1211)
- **Covers:**
  - `CAP-69.a` [W1] Transcripts are kept for 365 days — EMERGENCY-2 §10.3 (DEC-1211)
- **Scenarios:** dev — · qual —
