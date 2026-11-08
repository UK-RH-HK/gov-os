---
id: ADR-0002
title: Architecture and stack of the Gov OS
type: decision
status: PROPOSED
date: 2026-09-30
depends_on: [ADR-0001]
decisions: [DEC-064, DEC-065, DEC-066, DEC-067, DEC-073, DEC-074, DEC-075, DEC-076, DEC-078, DEC-080, DEC-083, DEC-084, DEC-085, DEC-086, DEC-087, DEC-088, DEC-089, DEC-090, DEC-091, DEC-092, DEC-093, DEC-094, DEC-095, DEC-096, DEC-138, DEC-141, DEC-150, DEC-152, DEC-153, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162, DEC-163, DEC-164, DEC-165, DEC-166, DEC-167, DEC-168, DEC-170, DEC-171, DEC-172, DEC-173, DEC-174, DEC-192, DEC-261, DEC-396, DEC-397, DEC-419, DEC-530, DEC-637, DEC-649, DEC-700, DEC-953, DEC-954, DEC-963, DEC-979, DEC-1010, DEC-1015, DEC-1029, DEC-1030, DEC-1031, DEC-1032, DEC-1033, DEC-1034, DEC-1035, DEC-1036, DEC-1037, DEC-1038, DEC-1039, DEC-1043, DEC-1045, DEC-1046, DEC-1047, DEC-1048, DEC-1049, DEC-1052, DEC-1055, DEC-1056, DEC-1057, DEC-1058, DEC-1059, DEC-1061, DEC-1064, DEC-1065, DEC-1066, DEC-1067, DEC-1068, DEC-1069, DEC-1070, DEC-1072, DEC-1073, DEC-1074, DEC-1075, DEC-1076, DEC-1077, DEC-1079, DEC-1081, DEC-1082, DEC-1084, DEC-1085, DEC-1086, DEC-1087, DEC-1088, DEC-1089, DEC-1090, DEC-1092, DEC-1093, DEC-1094, DEC-1095, DEC-1096, DEC-1097]
supersedes: []
implements: [CHARTER-v5, CONTRACT-v4]
state_class: AUTHORITATIVE
---

# ADR-0002 — Architecture and stack

Status PROPOSED; refreshed 2026-11-08 for the owner's acceptance (DEC-1093 (3)). Every decided change from the text
of 2026-10-10 cites its decision (descriptive updates cite their source); `CHANGES.md` beside the draft lists them old → new.

## Context and Problem Statement

- Architecture v0.3 (draft, for owner lock-in) describes the layers, the spec-first cycle, the organisation, the five
  distinct functions and the waves.
- S0b2 then decided the four open bake-off choices and measured the stack (DEC-074).
- The owner moved all of retrieval completeness into Wave 1 (DEC-080) and settled the Wave 1 adjustments (DEC-076)
  and the S1 packages (DEC-083…DEC-087).
- Wave 2 then rebuilt memory's runtime: the shared GPU services and the emergency of 2026-11-02 (DEC-1031…DEC-1052),
  memory's structural work D-4b (DEC-1055…DEC-1084), re-pin window 4 and the end-to-end experiments E0 to E5
  (DEC-1087…DEC-1097). This refresh states memory's architecture and the stack as decided and live on window 4's pin,
  `pin-bcea09060ebc` (DEC-1087 (8), DEC-1097 (1)).

This ADR locks architecture v0.3 **as amended by those decisions**. Where v0.3 and the register differ, the register
wins. The 15 recorded conflicts are in `docs/spec/gov-os/READINESS.md` §3.

## Decision Drivers

- Memory and context live in the repository. Everything else is derived and rebuildable.
- The Gov OS is agnostic to project type, language and harness (DEC-060).
- Governance costs at most 10–15 % of task tokens (DEC-004, DEC-086).
- It fits the one workstation it runs on, with no Docker. Every limit (slots, the lead cap, the GPU budget, the CPU
  band) is derived from the machine detected at start, never hard-coded (DEC-1037 (4)). Memory's models stay on the
  GPU within its budget: the dedicated memory never spills and never runs into a CUDA crash, and no model falls back to
  the CPU (DEC-1031, DEC-1039 (1b), DEC-1065 (1)).
- Mature tools do the heavy lifting; the glue is thin (DEC-001).
- Memory is judged by what an agent answers from its bundle, end to end, not by rank alone, and its verdict comes from
  a set used once (DEC-1085, DEC-1092 (4), DEC-1097 (1)).
- The basis: a rule, check or practice earns its place only if it helps deliver tests and code that match the KPIs
  and the spec with less drift, and it enters the product only after it has proven itself in use (DEC-1052).

## Considered Options

- **Stacks.** S0a's Minimal, Balanced and Maximum-local stacks. The owner chose **Balanced** (DEC-074 Q1).
- **Bake-off pairs, decided by fixed rules** (DEC-074):
  - retrieval: R1 or R2 (qmd);
  - code intelligence: C1 (codebase-memory-mcp) or C2 (LSP);
  - tasks: T1 (Backlog.md), T2 (beads_rust, excluded for its licence rider) or T3 (wedow/ticket);
  - decisions: D1 (adrkit) or D2 (MADR + check-jsonschema + checker).
- **Wave 2's reranker trial** (DEC-1068, DEC-1069, DEC-1076 (4), DEC-1077, DEC-1079, DEC-1081): Qwen3-Reranker-4B in
  8-bit (40 and 24 candidates), mxbai-rerank-large-v2, gte-reranker-modernbert-base, zerank-1-small, the cascade of the
  0.6B and the 4B, and the merged pairs M1 (the 0.6B + gte) and M3 (zerank + gte), each measured on the 138 tuning
  questions beside the 0.6B (hit@5 and MRR). Only M1 and M3 were run end to end (E4), and agents answered no better
  with them; the others were judged on hit@5 and MRR only. The 0.6B is kept (DEC-1097 (5)).
- **Query embedding on the CPU or the GPU** (DEC-798, superseded by DEC-1033; DEC-1065 (1)): the GPU only.
- **The bundle's shape** (E3, E5; DEC-1092 (2)): the top 5, 10 or 20, today's bundle, 40 unranked, and a 12,000-token
  page of 40. Today's 6,000-token bundle is kept (DEC-1097 (1)).

## Decision Outcome

### 1. Layers (architecture v0.3 §2.1, amended)

| # | Layer | Content | State |
|---|---|---|---|
| L0 | Harness | Claude Code (primary); AGENTS.md for other harnesses; subagents; LSP stays a harness feature | session only |
| L1 | Organisation | Role subagents generated by rulesync from kernel role files plus the project roster (DEC-066) | repo files |
| L2 | Instructions and skills | rulesync-generated CLAUDE.md, AGENTS.md, `.claude/`; three vendored Superpowers skills; Gov OS skills. The search-again practice is in the project layer's briefs now and reaches the two kernel skills through W2-142 at the lift's re-pin (DEC-1094 (2)) | repo files |
| L3 | Enforcement | *Not re-audited in the 2026-11-08 refresh: this states the product's enforcement as of Wave 1. On this repository DEC-953 / DEC-954 lifted it as gates (the guard's five rules; the full guard's cases opt-in, DEC-1061 (3a)); see DECISIONS-IN-FORCE.* Hooks (SessionStart, PreToolUse default-deny guard, PreCompact, Stop, SubagentStop); post-command containment (G-02, W1), also on `PostToolUseFailure`, because a failed command may have written files (DEC-153); **the OS sandbox** as the outer wall for everything a Bash command does in a worker session started by the launcher: writes outside the repository, installs, network, reads of hidden paths (DEC-152, DEC-161); the guard and the permission rules stay the wall for the file tools (Read, Edit, Write), which run outside the sandbox, and for the orchestrator's own session, which is not sandboxed (DEC-156); the guard denies any Bash call carrying `dangerouslyDisableSandbox: true` and any tool call that names the qualification oracle's path, which a committed `Read` deny rule also hides (DEC-153, DEC-162); role separation by path checks from the path map: an engineer is refused its own ticket's acceptance tests wherever they sit, a test designer the ticket's new code, new unit tests and documents (DEC-1052 G-14, DEC-1056, DEC-1059); a wide Grep, Glob or recursive Bash search that reaches the ticket's own acceptance folder is refused only from W2-141, applied with the guard's ACT at the lift's re-pin, and until then every engineer brief carries the exclusion line (DEC-1093 (2)); and `gov retrieve` filters every route the same way (DEC-1065 (2)); install rule (DEC-083: install commands `ask` for the orchestrator, also in Auto mode, `deny` for every other role, except the research role's installs inside its experiment folder, DEC-163; matching only escalates, never allows); lefthook G1–G3; GitHub Actions G4–G5, **advisory**, on an unprotected `main` (DEC-075, DEC-087) | repo files |
| L4 | `gov` CLI | **W1:** `status · check · readiness · doctor · rebuild · context · closure · retrieve · checkpoint · close · adopt --lite · pause`, plus the claim lock, and `launch`, the start command for worker sessions (DEC-153, DEC-161; not one of the twelve governance operations). **W2:** `impact · readiness --generate · discover` (DEC-166); `rebuild --integration`, the double-buffered integration store, and `launch` setting `GOV_STORE` (W2-116; DEC-1087 (3)); `links` (W2-129; DEC-1074 (7), DEC-1087 (4)); `plan` (W2-136, live at the lift's re-pin; DEC-1088); at the lift `launch` refuses a lead outside the approved batch or with unmet waits, and any session while the gate is shut or the machine's limits would be passed, with one recorded override (W2-136, W2-20; DEC-1088 (5)). **W3:** `claim` (concurrency) · `route` · `health` · `research sync` · `update --check` (W2-17, moved to Wave 3; DEC-1089 (2)) | code |
| L5 | Authority (git) | OpenSpec specs, changes and the `feature-readiness` artefact; MADR decisions; **ticket** tasks in `.tickets/` with KPIs, role, allowed paths, profile; lessons, failures, research, checkpoints, gate records; overlay; `framework.lock` | **git only** |
| L6 | Derived runtime | The store: frontmatter graph with the stated links as typed edges (W2-92; DEC-1074 (5)) + FTS5 + sqlite-vec + the code graph; packets; synthesis notes; the codebase-memory index in a per-repository home (DEC-074 Q10). **One integration store** for every session, at `w2/integrate`'s head, outside the trees (`integration_store` in `governance/project/rebuild.yaml`): two halves behind one link, rebuilt by the `reference-transaction` hook after every update of the integration branch, seeded from the ready half and switched only on a complete build, with a daily backstop (W2-116; DEC-963, DEC-1087 (3)). A worktree has no store of its own; `gov launch` sets `GOV_STORE` (DEC-1087 (3)); the test designer retrieves only from it (DEC-963). The store is built with the pinned code that searches it. No cold rebuild: every copy is seeded from the warm integration index and embeds only what changed (W2-122; DEC-1032 (3)(iv), DEC-1033 (2)(d)), and each text is embedded once on the machine through a shared vector cache (W2-126; DEC-1032 (1), DEC-1039 (1)). A rebuild asked for its semantic store that does not recreate it fails, named (DEC-1015 (4)); `--no-embeddings` skips it (DEC-530) | gitignored; `gov rebuild` |
| L7 | Distribution | `gov-os` as a Copier template; SSH-signed release tags; `framework.lock` = answers ref + file-hash manifest. The first numbered, frozen release is cut after the lift's re-pin and before the proving ground's run (DEC-1090 (5)); the pin ladder stays by hand until Wave 3 (DEC-1089 (2)) | tags + lock |

### 2. Stack (DEC-074, Balanced) — exact pins from `s0b2/out/TOOL_REGISTRY.yaml` and `governance/project/tool-registry.yaml`

| Component | Tool | Pin | sha256 (artefact) |
|---|---|---|---|
| Spec and change control | OpenSpec | 1.13.2 (Node ≥ 20.19; runs on Node v22.23.3) | `ca136f0e…32e797c6` |
| Decisions | MADR frontmatter + check-jsonschema + checker (D2) | check-jsonschema 0.38.2 | `9341d731…12aedd34` |
| Tasks | wedow/ticket (`tk`), vendored into the kernel template, plus the claim lock (T3) | v0.3.2 | `408f2c113ecc3bc071507593a78386f1b4cc743be6491c9e9f2627efd4d9902b` |
| Code intelligence | codebase-memory-mcp (C1), wrapped per repository | 0.11.0 | `a831cdca…4e3302a6` |
| Lexical retrieval | SQLite FTS5 (carried `cli/govbridge` code), BM25 | SQLite 3.45.1 | — |
| Vectors | sqlite-vec | 0.1.9 (DEC-397) | `59237308…c4498e8` |
| Embeddings | Ollama + qwen3-embedding:0.6b, in **two shared servers on the GPU**: 127.0.0.1:11434 builds the index (the model pinned loaded), 127.0.0.1:11435 embeds questions; each capped to its CPUs; a vector computed on the CPU is refused (DEC-1031, DEC-1033 (2)(b), DEC-1065 (1)) | Ollama 0.35.0 (`0b0650a9…34c4f8`); model id `ac6da0dfba84` (DEC-397) | model blob `06507c7b…49c3e439` |
| Reranker | Qwen3-Reranker-0.6B via sentence-transformers 6.1.0, torch 2.14.1+cu130, transformers 5.18.0, in `~/.local/share/gov-os/reranker-venv` (DEC-397), served by **one shared reranker service** (W2-112; DEC-1033 (2)(a), DEC-1043 (2)) | `Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473` | `model.safetensors` `27cd75a4…7c5e65b` |
| Fusion | RRF (R1) over the routes, with the authority lift, routing by question type and the candidate pool (§4; DEC-1067 (a), DEC-1075 (3)) | `governance/project/retrieval.yaml` | — |
| Adapters | rulesync | 24.0.0 | `64e8ad32…3297c71` |
| Distribution | Copier | 9.18.2 | `2343959a…16a98ac3` |
| Git hooks | lefthook | 2.1.15 | `df981b47…32e8fe3` |
| Secrets | gitleaks + Gov OS rules; switched off by configuration on this repository, on by default everywhere else, the switch named wherever it acts (DEC-1045) | 8.30.1 (DEC-056) | `88f91962…2e5509` |
| Method skills | Superpowers: test-driven-development, systematic-debugging, verification-before-completion (copied, not the plugin) | v6.4.2 | `f2a95244…e8c0b90a` |
| Python tooling | uv | 0.12.21 | `e8a4e7b4…478eb2076` |
| Node | Node LTS (tools only; the nvm default stays v18.20.8) | v22.23.3 | `fde6a4bf…5e348f48` |
| Telemetry (W1) | ccusage | 20.0.26 (DEC-192) | `b8d59c19…5eb1f2` |
| Harness | Claude Code (CLI for headless runs aligned with the VS Code extension's bundled version) | 2.1.292 (DEC-637, DEC-649) | `a967e7b1…a4ec93b3` |
| Sandbox prerequisites | bubblewrap · socat (installed by the owner, DEC-141) | 0.9.0 · 1.8.0.0 | `2461f1be…aa3094` · `46e85428…2696fe` |
| The `gov` CLI | the wheel of `bcea09060ebc` in its own environment, linked from `~/.local/bin/gov` (re-pin window 4; DEC-1037 (1), DEC-1087 (8), DEC-1061 (8)) | `pin-bcea09060ebc` (gov 0.1.0) | wheel `11a16d0f…d406` |

- **Rejected:** qmd 2.8.3, Backlog.md 1.53.0, adrkit 0.15.0, beads_rust, and LSP as a stack component;
  mxbai-rerank-large-v2 (76 of 138; DEC-1079); a CPU query embedder (DEC-798, superseded by DEC-1033; DEC-1065 (1));
  non-commercial rerankers (DEC-1079 (d)).
- **Measured, not adopted:** Qwen3-Reranker-4B in 8-bit (DEC-1077 (b)); M1 and M3 (better hit@5, no better answers
  end to end: E4; DEC-1097 (5)); measured on the fresh 80 for data only (DEC-1097 (5)).
- **Deferred:**
  - Docling and MarkItDown (Wave 3 research lifecycle);
  - RAGFlow (CONDITIONAL, DEC-020);
  - the OTel stack (Wave 3);
  - gpt-oss:20b (Wave 3 routing, DEC-083);
  - the embedder trial (Qwen3-Embedding-4B): a Wave 3 row (DEC-1097 (14)).
- **Installs:** every install, upgrade or removal goes through DEC-083. A change to the machine outside the repository
  (`~/.local/bin`, `~/.config`, `~/.ollama`, the crontab, services) is an ACT, rehearsed end to end (DEC-1038 (1),
  DEC-1057, DEC-1058). `gov doctor` compares these pins with what it finds.
- **The `gov` CLI:**
  - It is a Python 3.12 package in the Gov OS repository (`src/gov/`). Every session runs the pinned wheel. A re-pin
    runs its checks before the switch, installs the new pin beside the old one and switches by one rename, the old pin
    kept for an instant rollback (DEC-1037 (1)); window 4's wheel was built twice from a clean export and the two
    builds matched (ACT-REPIN-W4). The kernel records the `gov` version pin. Its pinned install (W2-18) and `gov update` (W2-17) stay in Wave 3 (DEC-1089 (2)).
  - Its core needs only the standard library, PyYAML and sqlite-vec.
  - **The reranker** is one shared service per user (W2-112; DEC-979 (4), DEC-1033 (2)(a)): `rerank_service.py` in the
    reranker venv, on the socket `~/.cache/gov-os/rerank.sock`, started by the first search under a lock when none
    listens and ending after an idle period (DEC-1034 (3)). It releases its GPU memory after each request (DEC-1068).
    It holds reranker GPU slot 0 and does not start below its GPU share: never the CPU (DEC-1036 (1), (2),
    DEC-1043 (2)). A search that cannot reach it falls back to a private reranker that holds a GPU slot, or keeps the
    fused order, named `rerank: unavailable` (DEC-1033 (2), DEC-1035 (2)). **No private reranker beside the running
    service** is decided (DEC-1046 (1), DEC-1048 (5)) but is not yet in the product: today only the CTO's interim
    slot-hold watcher enforces it on this machine (DEC-1043 (2)), and W2-112's own KPI still allows one private
    reranker beside the service (DEC-1036 (2)). The product change is W2-145, tests first, built before the lift
    (DEC-1097 (8)); not yet built.
  - **The embedders:** `gov` never starts an embedder for a search, a rebuild, a close, a seed or the launch sandbox.
    When the shared GPU embedders cannot be reached, the result is `EMBEDDER_UNAVAILABLE` and retrieval answers by
    keywords (W2-32 S10; DEC-1065 (1)), which changes DEC-261's "`gov` starts `ollama serve` on demand" (DEC-261 is not
    yet marked so). Only an explicit restart of the shared servers starts `ollama serve`, under their committed caps
    (DEC-1057 (4)), and `gov` never stops it (DEC-261).

### 3. Scale envelope and resources (DEC-078, DEC-074, re-read for Wave 2)

- **Code graph.** Tested up to ≈ 80k nodes / 270k edges at ≈ 2.2 GB peak RSS for codebase-memory-mcp. Memory scales
  with edges, not file count. Larger graphs are measured before adoption.
- **The store.** This repository, as counted in D-4b (W2-88 §1, 2026-11-04 to 11-06; not a count of window 4's
  store): 69,464 chunks, 19,113 of them embedded from 1,126 files; which namespaces are
  embedded is the path map's `embedding_policy` (DEC-700, DEC-1052 M-4, DEC-1055 (3)).
- **The machine.** On this repository the CTO's tools derive every limit from the machine detected; in the product
  this arrives through W2-20 and W2-121's KPI lines, not on the pin (DEC-1037 (4), DEC-1097 (8)). Today it is WSL on 20 logical CPUs
  with a 24 GB memory cap, and a 16 GB GPU (16,303 MiB) (recorded with DEC-1038; DEC-1076 (4)).
- **RAM.** S0b2's worst case was ≈ 12.5 GB of 15.5 GiB (IDE + models + a full index run); not re-measured on Wave 2's
  runtime.
- **VRAM.** The budget is 14,255 MiB: the GPU less a 2 GB headroom (DEC-1032 (1), DEC-1076 (4)). The two embedders
  come first (about 5.6 GB together), the shared reranker second (about 4.8 GB, up to 6.4 GB under load, read on 2026-11-02, before it released its memory
  after each request); nothing may
  push the embedders off the GPU (DEC-1031 (1)-(2), DEC-1043 (2)). Measured on window 4: 8,404 MiB peak through
  E0; about 9.4 GB under a burst of 20 searches at once (G1). The embedders stay loaded, so the GPU does not return to
  an empty baseline when idle. The spill floor is 2,048 MiB (DEC-1084); experiments carry a backstop at 15.5 GB and
  take the GPU one job at a time (DEC-1067).
- **Disk.** ≈ 11.9 GB at S0b2; not re-measured. The reranker trial's downloads are kept as they are for now
  (DEC-1070 (1), DEC-1079).
- **Processes.** Two shared embedding servers (Ollama) and one shared reranker service, all on the GPU. On this
  repository, by the CTO's tools: the dispatcher watches each model's layers on the GPU and the servers' crashes
  (DEC-1030), and the servers restart by class from their committed configurations, without an ACT (DEC-1057 (4)).
  In the product these are KPI lines of W2-20 and W2-121 (DEC-1030 (4), DEC-1031 (4)), not on the pin. No Docker.
- **Retrieval speed (window 4, the pool on).** One search alone: median 1.24 s (E0) to 1.68 s (PAT-1), against the
  target of about 1 s (DEC-1065 (4)). Ten searches at once: 6.6–6.8 s median; twenty: 13.4–13.9 s, with no error or
  timeout (PAT-1). Under twenty at once the shared reranker's GPU is saturated (G1). The integration store rebuilds
  from its seed in about 30 s after a commit (PAT-1).

### 4. Retrieval completeness in Wave 1 (DEC-080), as built through Wave 2

Retrieval is a **skill with deterministic helpers**, not an engine (architecture v0.3 §3). Wave 1 delivered all of
it; Wave 2 rebuilt its routes, pool and services:
- `gov retrieve` with paging and continuation (the batch size is configurable and never a completeness limit),
  answering from the integration store (DEC-1087 (3)); from the lift's re-pin every result carries the store's commit
  and folder, so a worker can tell when its tree differs (W2-138; DEC-1090 (3));
- parallel facet subagents: decisions, code, tests, history, why, lessons/failures;
- the routes (DEC-419 DP-8): lexical, semantic, the record route, the closure, the code route and the stated links
  (W2-92; DEC-1074 (5)); three phrasings of the question and routing by question type (DEC-1067 (a));
- deterministic closure with `gov closure`;
- deduplication by chunk hash, and authority/current/superseded filtering; register items carry their own id, their
  status and "changed by", so a PROPOSED record is never taken as a rule (DEC-1073 (2));
- what is embedded: the WBS, the specs and KPIs, the tickets, the code and the decisions; tests and the close,
  checkpoint and probe records stay keyword-only (DEC-1052 M-4, DEC-1055 (3)); the evaluation set's own documents
  are indexed nowhere (DEC-1066 (3), DEC-1067 (f)); each chunk is embedded with its path and headings, and the models
  read the whole chunk (DEC-1066 (1), DEC-1068 (e));
- **the candidate pool** (W2-32 S11; DEC-1074 (5), DEC-1075 (3)), switched on after re-pin window 4 (DEC-1089 (1)):
  the meaning route uncut, routes 60 deep, 40 candidates reranked, at most 2 chunks of a file in the first 10, nested
  repeats dropped;
- parent-child retrieval: chunk records carry `parent_id` (section for documents, function/module for code), and a child hit expands to its parent within the bundle budget, named in the bundle (DEC-091);
- one rerank over the merged candidate set (DEC-419 DP-9), by the shared service; each request is bounded at 16
  texts and 24,000 padded characters (DEC-1067 (f)), raised to 64 texts at the lift's re-pin (W2-137; DEC-1090 (2),
  DEC-1095 (1)); the bundle names who reranked, on which device, and why not (`rerank {by, device, reason}`;
  DEC-1036 (3));
- **the bundle:** 6,000 tokens (DEC-004's packet ceiling, DEC-419 DP-3), bounding parent expansion only; kept against
  12,000 by E5 (DEC-1097 (1)); an item whose line runs over 4,000 characters is cut to 4,000, marked `cut`, its path
  and lines cited unchanged (W2-135; DEC-1086 B);
- **search respects role separation:** every route's hits are filtered by the caller's `role_paths`, and what is
  withheld is counted in the bundle (W2-13 S5; DEC-1065 (2));
- a cited evidence bundle: citations by id and sha256, and one stopping reason from `CLOSURE_COMPLETE`, `SATURATED`,
  `DEPTH_LIMIT_REACHED`, `BUDGET_EXHAUSTED_WITH_GAPS`, `FACET_UNAVAILABLE`, `UNRESOLVED_IDS` (the sixth value, added
  by DEC-396: everything within depth was reached and some referenced ids name nothing);
- the citation validator;
- zero-result canaries per index;
- hierarchical synthesis notes (derived, cited, hash-checked) when evidence exceeds the packet budget;
- **search again once**, the agents' standing practice: when the first bundle does not answer, or the answer may be
  incomplete, search again once in other words, then settle as not found; two searches at most (DEC-1092 (1),
  DEC-1094 (2)). Overlapping slices of one record stay as they are before the fresh 80 (DEC-1097 (7)).

Secrets are filtered by content before every indexer, including codebase-memory's (DEC-074 Q8), except where the
repository switches the scan off by configuration, as this one does (DEC-1045). Wave 1's exit runs RETR-A-04 and
RETR-X-02.

### 5. Repository layouts

**Product repository after adoption** (architecture v0.3 §2.2, with `.tickets/` in place of `backlog/`):

```text
<product>/
├── AGENTS.md  CLAUDE.md  .claude/            generated by rulesync (rulesync owns .claude/, DEC-074 Q7)
├── .rulesync/                                kernel part + overlay part
├── governance/kernel/ (Copier-owned) · governance/project/ (overlay) · governance/framework.lock
├── openspec/ specs/ · changes/ · schemas/feature-readiness (26 rows, docs/contract/readiness-dimensions.yaml)
├── spec/ decisions/ · lessons/ · failures/ · research/ · gates/ · checkpoints/
├── .tickets/                                 ticket tasks (+ .tickets/.claims/)
├── tests/acceptance/<ticket-id>/             Independent Test Designer only
├── lefthook.yml  .github/workflows/gov.yml  .gitleaks.toml
└── .gov-runtime/                             gitignored, derived
```

**The Gov OS repository** (this repository; the Wave 1 tickets' `allowed_paths` use these paths):

```text
copier.yml                      template configuration (_subdirectory: template)
template/                       everything copied into a product: governance/kernel/{hooks,schemas,skills,roles,templates,bin},
                                .rulesync/, openspec/schemas/, lefthook.yml.jinja, .github/workflows/gov.yml, .gitleaks.toml
src/gov/                        the gov CLI (subpackages per command area)
tests/unit/                     builder tests (regression evidence only)
tests/acceptance/<ticket-id>/   written only by the Independent Test Designer (MR-3)
governance/project/             the Gov OS's own overlay: path-map, roster, profiles, tool-registry,
                                retrieval.yaml and rebuild.yaml (memory's query and store settings)
.tickets/                       the WBS
docs/                           charter, contract, ADRs, spec, plan, register, lessons
fixtures/evaluation/            memory's visible tuning set; never indexed (DEC-1066 (3))
cli/govbridge/                  carried code; ported into src/gov/ by the tickets that reuse it, then removed
```

The hidden sets of memory's measure live outside every worktree, so no guard rule is needed inside the trees
(DEC-1052 G-3, DEC-1055 (4)). Decided (DEC-1082 (3), DEC-1084 (1)): the guard refuses the hidden sets, wherever
they lie, to six measured roles and `transcripts/**`. **Not yet applied:** ACT-GUARD-SETS-1 is being rebuilt against
today's files with the fresh 80's reader-run folder added, and is applied before the 80's single use (DEC-1097 (2)).

### 6. Operating model

*Not re-audited in the 2026-11-08 refresh: this states the product's operating model as of Wave 1, with the memory
lines added. On this repository DEC-953 / DEC-954 lifted the Gov OS features as gates, the nightly is stopped
(DEC-1049), and Wave 2 has six roles, the ticket lead and the three layers (DEC-1087 (13)); see DECISIONS-IN-FORCE.*

- **Roles** (DEC-066, DEC-163). Wave 1 has five roles, and a sixth in a minimal form:
  - orchestrator: the only role that installs tools, except the research role inside its experiment folder
    (DEC-163), and only after the owner approves a decision package in chat that
    gives the tool, exact version, source and checksum, need, disk and RAM, and uninstall command. Every install is
    recorded in the tool registry (version, sha256, install and uninstall commands, date, approving decision), and
    `gov doctor` checks the pins (DEC-083, which amends DEC-040; DEC-095);
  - product/specification;
  - independent test designer: may write only `tests/acceptance/**`;
  - engineer: must never write `tests/acceptance/**`;
  - independent auditor: read-only;
  - research, minimal (DEC-163): a role file delivered with the launcher (W1-46). It runs as a launched worker
    session, writes only inside its ticket's `allowed_paths` (its experiment folder), and uses the research network
    allowlist of DEC-158. It may install only into a venv or local prefix inside that folder; the sandbox's write
    fence denies a system-wide install. Inside the repository the fence is a list of `Edit` deny rules the launcher
    generates at launch, because the sandbox always leaves the working directory writable (EXP-001 §3.4, §5.3). The
    list is computed at launch, from the paths that exist then. A path created later outside the experiment folder is
    not in it; that path is covered by the guard's per-ticket allow-list, which holds the role's writes to its
    ticket's `allowed_paths`, and the containment check reports a change the guard did not see. The list has two
    exceptions: `.git/`, so that the session can commit its evidence record, and an entry whose name contains `*`,
    `?` or `[`, which the sandbox skips on Linux (EXP-001 §1). Both are left to the guard and the containment check.
    A research or experiment session runs as `GOV_ROLE=research`. The full research lifecycle (CAP-32) stays in
    Wave 3.

  Wave 2 and Wave 3 roles follow Charter v5 §6, with test execution and integration as distinct Wave 2 roles
  (DEC-094).
- **The owner** is the customer and L5. Decision packages come in chat, ranked P1–P3 and batched at most five at a
  time; a P1 package may bypass the cap (DEC-093). The template carries ten fields (Framework §52).
  Answers are recorded in git (MR-6).
- **Until Release 1** (DEC-073, DEC-084):
  - an operator console session acts for the owner at the terminal;
  - the Gov OS's own Wave 1 bootstraps MR-3 with settings deny rules and an operator diff check;
  - once the guard and containment tickets pass their acceptance tests, the Gov OS runs under its own guard.
- **Orchestrator write scope** (DEC-150, DEC-156; W1-45). The orchestrator may write anywhere in the repository except
  `tests/acceptance/**`. The guard enforces only that exclusion for it, and containment still records its changes: a
  change outside its ticket's paths is a record, not a containment finding (DEC-171).
  Its interactive session (VS Code or terminal) is not sandboxed. Until W1-25's `gov checkpoint`, its checkpoint lives
  in `.gov-runtime/scratch/orchestrator/`. Every other role keeps the `allowed_paths` rule.
- **Worker sessions and the sandbox** (DEC-152, DEC-153, DEC-161; W1-46):
  - engineer, independent test designer, independent auditor, and research or experiment work run as worker sessions
    the orchestrator starts with `gov launch`. Work that needs the sandbox runs as a launched worker session;
    in-session subagents remain for read-only work (review, exploration, web research);
  - the launcher builds per-role `--settings` (the sandbox block plus the role's `Edit` deny rules), sets `GOV_ROLE`,
    `GOV_TICKET`, `GOV_STORE` (DEC-1087 (3)) and a per-session temp directory (DEC-159); from the lift it also refuses
    a lead outside the approved batch, and any session while the gate is shut (DEC-1088 (5)); it refuses to start unless
    the sandbox is enabled, strict and fail-closed (`failIfUnavailable: true`, `allowUnsandboxedCommands: false`,
    network `strictAllowlist`). The sandbox configuration never comes from the repository, whose settings carry no
    sandbox block;
  - **the shared services and the sandbox:** a sandboxed session cannot reach the shared reranker or embedders (the
    sandbox refuses the reranker's Unix socket, DEC-1034 (1)). Until W2-127 (now inside W2-56) allows the one socket path, a
    sandboxed search falls back, named, and sandboxed workers run no `gov retrieve` and no test that starts a real
    model; never a private CPU embedder (DEC-1034 (1), DEC-1035 (2), DEC-1064 (2), DEC-1065 (1));
  - network profiles (DEC-158): the orchestrator is unrestricted, being unsandboxed; research and experiment work gets
    a broad, owner-extensible allowlist (GitHub, PyPI, npm, Hugging Face, arXiv, documentation sites), with its writes
    and installs inside its own experiment folder; engineer, test designer and auditor get an empty allowlist.
    WebSearch and WebFetch run outside the sandbox;
  - worker roles never install system-wide (DEC-157). The install rule above is unchanged for the orchestrator; the
    research role's installs inside its experiment folder are its one exception (DEC-163);
  - the guard's install rule decides install commands alone. The committed `.claude/settings.json` carries no
    install or download ask rule once W1-47 has removed them; in a launched worker session the sandbox backs the
    guard (DEC-172). W1-47 also extends the rule to `uv add`, `uv sync`, `uv run --with` and `uvx` (DEC-174);
  - the launcher sets no `excludedCommands` (DEC-164).
- **The qualification oracle** is hidden from a worker's Bash by the sandbox (silently: the directory looks empty),
  and from every session started in the repository root by a `Read` deny rule in the committed `.claude/settings.json`
  and by the guard (DEC-162; W1-47). The oracle path is held in `governance/project/held-out.yaml` and in the
  committed deny rule built from it; register entry DEC-067 names the directory historically. The guard and the
  launcher take the path from `held-out.yaml`; no acceptance test names it. An opaque Bash read in the orchestrator's own session is an accepted residual.
- **Untested sandbox cases** (`denyWrite` on a path that doesn't exist yet, symlink and hard-link tricks, the seccomp
  filter, `bypassPermissions` mode) go to a Wave 2 experiment, EXP-002 (DEC-160). Two more open residuals go to the
  same experiment: subagents inside a sandboxed worker session, and `excludedCommands` (DEC-164).
- **Discovery and impact from plain language** (DEC-166, DEC-167). From Wave 2, `gov discover <question or feature>`
  is the entry point to discovery: it opens a discovery ticket, runs the discovery skill, and schedules research and
  experiment tasks whose evidence records back the answer. "What's the impact of X?" triggers the impact assessment:
  an OpenSpec proposal plus `gov closure` in Wave 1, `gov impact` from Wave 2.
- **The upstream lesson loop, lite** (DEC-165; Wave 3). Every lesson record carries a scope and a severity; both
  fields are in the Wave 1 lesson schema (DEC-168). A
  framework lesson becomes a lesson packet (failure pattern, evidence, suggested change; no product code, data or
  secrets; gitleaks-scanned), which the product's orchestrator writes to the shared inbox `~/gov-os-lessons-inbox/`,
  the one path outside its repository it may write. A high or critical lesson goes to the owner at once as a decision
  package. The Gov OS orchestrator triages the inbox into change proposals under the normal cycle, and release notes
  list the lessons fixed. `gov doctor` reports pending updates and their highest severity at session start; the owner
  decides when to run `gov update`. Product decisions, specifications and lessons never leave their repository.
- **Memory-building at adoption** (DEC-1072 (2)): every adopted repository builds and measures its memory in its
  Wave 0 by the practice recorded in `docs/research/W2-88-memory-practice.md` (W2-88), a kernel skill after the
  refactoring.
- **Readiness** (DEC-085). LITE requires the 10 mandatory rows; STANDARD adds the rows marked by capability type;
  FULL requires all 26. Spines always close at FULL. There is no defaulted N/A.

### 7. The five distinct functions (MR-4)

*Not re-audited in the 2026-11-08 refresh, except the DEC-1010 paragraph on reviews; see DECISIONS-IN-FORCE.*

| Function | Question | Mechanism | Wave |
|---|---|---|---|
| `gov doctor` | Is the Gov OS installed and healthy here? | pins, hooks, path map, index freshness, canaries, framework.lock; deterministic | W1 |
| Discovery | Is this specification closed, and what must the customer answer? | discovery skill + `gov readiness`; linked gap tickets (DEC-089) | W1 (automatic generation W2) |
| Impact (CIT-P) | What will this change affect? | OpenSpec proposal; `gov impact` over both graphs | W1 proposal; W2 computed |
| Execution (CIT-E) | Was the change applied as proposed? | OpenSpec apply/archive + `gov close` trailers + checkpoint | W1 |
| Audit | Does the actual state match the specification, contract and decisions? | fresh read-only Independent Auditor + audit skill. It runs when a spine, STANDARD or FULL feature specification closes, when an accepted CIT-E changes a closed spine, and at every wave and release exit (DEC-088). Contested and owner-level findings go to the owner as decision packages; agreed fixes become tickets | W1 (full roles W3) |

Fidelity audit (S1-A) and every wave-exit audit use the Independent Auditor role (DEC-070, DEC-082). Every review→repair,
audit→repair, test→fix or verification loop follows DEC-096:
- it runs to convergence, or to three consecutive non-converging iterations;
- the third failure goes to the owner as an escalation package;
- the orchestrator or `gov` holds the count and never discloses it to the sessions inside the loop.

Reviews converge under DEC-1010, which changes DEC-096 for reviews: a moderator triages every finding against the
ticket's own scope and KPIs; a finding blocks only if it is in scope, reachable in ordinary work, and fails open or
loses work; at most two review rounds, then the owner once with options; READY is computed by code from each
reviewer's structured verdict (DEC-1010 (1), kept by DEC-1047 (3)).

### Consequences

- **Good:**
  - The stack is measured, pinned and small.
  - All of retrieval completeness is available to Wave 1's own dogfooding.
  - The five functions stay separate.
  - In worker sessions, the opaque-write and install-miss residuals of the guard are closed for Bash at the OS level,
    without parsing the command (EXP-001).
  - Every unsandboxed session searches one current store (sandboxed workers wait for W2-127, below), refreshed after every merge, with the models on the GPU and loaded
    once for the machine, not once per session (DEC-1031, DEC-1033, DEC-1087 (3)).
  - On the 138 tuning questions, window 4's configuration answers right end to end on 83.3 % with one search and
    92.8 % with search again once, wrong claims 2 → 3 (E2; DEC-1092 (1)); hit@5 is 76.8 % and the gold is in the
    first bundle for 89.1 % (E0).
- **Bad:**
  - Wave 1 glue grows to ≈ 5,680 LOC (the figure in `docs/plan/WAVE_1_WBS.md` §3), against architecture v0.3's ≈ 2.4k.
    This is the effect of DEC-080, DEC-074 R1, DEC-076, DEC-083, DEC-086, the S1-A repairs (DEC-089…DEC-092, and
    a ticket KPI for every Wave 1 `covers` item), and the S2 change (+370 LOC: W1-45, W1-46 and W1-47, +320; KPIs added to W1-30 and W1-31, +50). DEC-064 turns
    DEC-001's size trigger into a per-wave review.
  - The sandbox has a measured cost (EXP-001 §3.6): about +65 ms per Bash command, and about +3,250 input tokens per
    session (+7 %), which are sandbox instructions in the system prompt. Every launched worker session carries them.
    W1-31 reports them as a separate line, not inside the governance share. Whether they count toward the governance
    share is decided at the Wave 1 exit, using measured figures (DEC-170).
  - Two containment layers must be kept in step: the sandbox covers a worker's Bash, the guard covers the file tools
    and the orchestrator's session. The orchestrator's own Bash stays under the guard alone.
  - `ticket` is unmaintained upstream; it is vendored by hash.
  - The reranker venv is 5.6 GB. Wave 2's trial measured lighter and heavier rerankers on hit@5 and MRR (DEC-074 Q3's
    spike); only M1 and M3 were run end to end (E4), and neither made agents answer better, so the 0.6B and its venv
    stay (DEC-1097 (5)).
  - The GPU is one shared resource for every session's memory: a CUDA crash or a model loaded off the GPU degrades
    every search. On this repository the CTO's dispatcher watches it and pushes an alert at once (DEC-1029, DEC-1030);
    in the product that is W2-20 and W2-121's (DEC-1030 (4)).
  - The shared reranker saturates its GPU when 20 agents search at once (14.5–17.4 s
    for a burst of 20 in G1; 13.4–13.9 s in PAT-1). The lever, fewer scored pairs per search, changes ranking; it comes to the owner after the lift, with the 138 re-measured if adopted
    (DEC-1097 (10)).
  - Sandboxed workers cannot use memory's semantic route or the shared reranker until W2-127 lands (DEC-1035 (2),
    DEC-1064 (2)).
  - Interims remain outside the product until their tickets land: the machine-wide reranker slot module and the
    slot-hold watcher (DEC-1043 (2), DEC-1048 (1), (5)), the only enforcement today of "no private reranker beside the
    shared service", which reaches the product with W2-145 (drafted, to be filed), not yet built, before the lift (DEC-1097 (8)); the query
    server's start wrapper, whose removal DEC-1037 tracks by a W2-20 / W2-121 KPI line that no ticket carries yet.

### Confirmation

- The Wave 1 exit (WAVE_1_WBS §4) and the independent wave-exit audit against Contract v4.
- `gov doctor` checks every pin in §2.
- **Memory's verdict:** the fresh 80 (`memory-verdict-2`), used once, judges window 4's configuration (the pin, the
  pool on, the 6,000-token bundle, search again once) against K9's bar: right end to end at least 85 % with wrong
  claims at most 5 %, target 95 %, hit@5 reported beside it; every other condition is measured on the 80 for data only
  (DEC-1097 (1), DEC-1092 (4)). If retrieval changes after the verdict, the 138 are measured again at the release
  commit before the release is cut (DEC-1097 (4)).
- Every comparison of memory reports its gains, its losses and an exact McNemar test (DEC-1079 (b) L1).

## More Information

- **Sources:** architecture v0.3; S0a `STACK_OPTIONS.md`, `CAPABILITY_CATALOGUE.md`; S0b2 `RESULTS.md`,
  `GLUE_REQUIREMENTS.md`, `TOOL_REGISTRY.yaml`, `INTEGRATION_REPORT.md`; register DEC-064…DEC-096, and
  DEC-138…DEC-174 for the sandbox layer, the launcher, the research role and the lesson loop; `spike-sandbox/EVIDENCE.md` (EXP-001, ADOPT-PARTIAL);
  for Wave 2's memory, DEC-1029…DEC-1097, `governance/project/tool-registry.yaml` (the `gov` entry of re-pin
  window 4), `docs/research/W2-88-memory-practice.md`, `docs/research/W2-112-shared-reranker.md`, and
  `governance/project/orchestration/packages/LIFT-1/` (E0 to E5, E0B, E2G, G1-PROFILE, PAT-1, BUNDLE-BUDGET-1,
  M3-ADOPTION-1, FRESH-80-1).
- **Revisit triggers:**
  - a code graph above the tested envelope;
  - vectors above ~100k (move to LanceDB, DEC-016);
  - OpenSpec or codebase-memory-mcp breaking changes at a pin upgrade;
  - the per-wave glue review;
  - a reranker or embedder that makes agents answer better end to end on the 138 under a reading rule declared before
    its figures, measured on the standing model bench (DEC-1069 (13), DEC-1097 (5));
  - any change to retrieval after the fresh 80's verdict (DEC-1097 (3), (4));
  - W2-127 opening the sandbox to the shared services (DEC-1035 (2));
  - the glossary's fate (DEC-1096; DEC-1097 (6), open).
