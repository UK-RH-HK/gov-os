---
id: ADR-0002
title: Architecture and stack of the Gov OS
type: decision
status: ACCEPTED
date: 2026-09-30
depends_on: [ADR-0001]
decisions: [DEC-064, DEC-065, DEC-066, DEC-067, DEC-073, DEC-074, DEC-075, DEC-076, DEC-078, DEC-080, DEC-083, DEC-084, DEC-085, DEC-086, DEC-087, DEC-088, DEC-089, DEC-090, DEC-091, DEC-092, DEC-093, DEC-094, DEC-095, DEC-096, DEC-138, DEC-141, DEC-150, DEC-152, DEC-153, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162, DEC-163, DEC-164, DEC-165, DEC-166, DEC-167, DEC-168, DEC-170, DEC-171, DEC-172, DEC-173, DEC-174, DEC-192, DEC-261, DEC-396, DEC-397, DEC-419, DEC-530, DEC-637, DEC-649, DEC-700, DEC-953, DEC-954, DEC-963, DEC-979, DEC-1010, DEC-1015, DEC-1029, DEC-1030, DEC-1031, DEC-1032, DEC-1033, DEC-1034, DEC-1035, DEC-1036, DEC-1037, DEC-1038, DEC-1039, DEC-1043, DEC-1045, DEC-1046, DEC-1047, DEC-1048, DEC-1049, DEC-1052, DEC-1055, DEC-1056, DEC-1057, DEC-1058, DEC-1059, DEC-1061, DEC-1064, DEC-1065, DEC-1066, DEC-1067, DEC-1068, DEC-1069, DEC-1070, DEC-1072, DEC-1073, DEC-1074, DEC-1075, DEC-1076, DEC-1077, DEC-1079, DEC-1081, DEC-1082, DEC-1084, DEC-1085, DEC-1086, DEC-1087, DEC-1088, DEC-1089, DEC-1090, DEC-1092, DEC-1093, DEC-1094, DEC-1095, DEC-1096, DEC-1097, DEC-1098, DEC-1204, DEC-1210, DEC-1211, DEC-1214, DEC-1217, DEC-1219]
supersedes: []
implements: [CHARTER-v6, CONTRACT-v5]
state_class: AUTHORITATIVE
---

# ADR-0002 — Architecture and stack

Status ACCEPTED by the owner on 2026-11-09 (DEC-1098 (5)); refreshed 2026-11-08 (DEC-1093 (3)); **revised 2026-11-19 to
Charter v6 and Contract v5** (EMERGENCY-2, DEC-1211; the owner's decisions DEC-1214 G4, G5 and G6, approved by group in
DEC-1219 (1); audit 7 C-4). Every decided change from the text of 2026-10-10 cites its decision (descriptive updates
cite their source); `CHANGES.md` beside the draft lists the refresh's changes old → new, and the list below gives this
revision's.

**What the revision of 2026-11-19 retired** (EMERGENCY-2 §2, §3, §5.5, §6.1, §7, §8; Charter v6 §2 and §7; Contract v5
§2 and CAP-58, CAP-61, CAP-62). Each place below says so again in one clause that cites its section.
- The L3 guard, the OS sandbox and everything that rested on them: the write allow-lists, post-command containment
  hooks, the escape-hatch denial, the deny rules for the qualification oracle, the install rule, the launcher's sandbox
  block and network profiles, the untested sandbox cases and the sandbox's cost lines. Agents now have full permission
  in the repository, worktree and run folder they work in; nothing is prevented, and mistakes are caught and
  corrected at the landing (EMERGENCY-2 §2.1 to §2.3).
- The ACT pipeline, the operator agent and the "Until Release 1" bootstrapping (§2.6, §2.10).
- `gov context`, its packet and every packet ceiling (§5.5; DEC-1214 M1): the brief carries the ticket's retrieval
  (§5.4).
- Three non-converging iterations of a loop: two rounds, then the owner once (DEC-1204; Contract v5 §2 Loop budget).
- SSH-signed release tags: a release is pinned and hash-verified, and a signature waits for friction (DEC-1214 L3;
  CAP-02.c).
- A fresh audit at every wave exit and spine closure: it runs only at the release acceptance and at adoption stages
  A5, AS, A7 and A10 (DEC-1214 G6; MR-4).
- The content scan on every index: gitleaks runs once, before a repository goes public or is shared with a third
  party (§2.11; DEC-1219 (1)).

## Context and Problem Statement

- Architecture v0.3 (draft, for owner lock-in) describes the layers, the spec-first cycle, the organisation, the five
  distinct functions and the waves.
- S0b2 then decided the four open bake-off choices and measured the stack (DEC-074).
- The owner moved all of retrieval completeness into Wave 1 (DEC-080) and settled the Wave 1 adjustments (DEC-076)
  and the S1 packages (DEC-083…DEC-087).
- Wave 2 then rebuilt memory's runtime: the shared GPU services and the emergency of 2026-11-02 (DEC-1031…DEC-1052),
  memory's structural work D-4b (DEC-1055…DEC-1084), re-pin window 4 and the end-to-end experiments E0 to E5
  (DEC-1087…DEC-1097). This refresh states memory's architecture and the stack as decided and live on window 4's pin,
  `pin-bcea09060ebc` (DEC-1087 (8), DEC-1097 (1)); the pin has since moved to release 0.1.3 (§2), and the figures below
  were measured on window 4's.
- EMERGENCY-2 (DEC-1211, in force from 2026-11-17) then retired the enforcement layer and changed how work is judged,
  landed and measured; the owner approved the re-baseline of the Charter and the Contract by group on 2026-11-19
  (DEC-1214 G5, DEC-1219 (1)).

This ADR locks architecture v0.3 **as amended by those decisions**. Where v0.3 and the register differ, the register
wins. Charter v6 and Contract v5 carry EMERGENCY-2's rules, and this ADR follows them (Charter v6 §8). The 15 recorded
conflicts are in `docs/spec/gov-os/READINESS.md` §3.

## Decision Drivers

- Memory and context live in the repository. Everything else is derived and rebuildable.
- The Gov OS is agnostic to project type, language and harness (DEC-060).
- Governance costs at most 10–15 % of task tokens, 15 % being the bound, reported weekly with its baseline (56 % before
  EMERGENCY-2); there is no packet ceiling (DEC-004, DEC-086; Contract v5 §2 Token budget; DEC-1214 M1).
- It fits the one workstation it runs on, with no Docker. Every limit (slots, the lead cap, the GPU budget, the CPU
  band) is derived from the machine detected at start, never hard-coded (DEC-1037 (4)); in the product the run-time tool does
  it (RT-3; EMERGENCY-2 §6.3). Memory's models stay on the
  GPU within its budget: the dedicated memory never spills and never runs into a CUDA crash, and no model falls back to
  the CPU (DEC-1031, DEC-1039 (1b), DEC-1065 (1); EMERGENCY-2 §5.8).
- Mature tools do the heavy lifting; the glue is thin (DEC-001).
- Memory is judged by what an agent answers from its bundle, end to end, not by rank alone, and its verdict comes from
  a set used once (DEC-1085, DEC-1092 (4), DEC-1097 (1)).
- The basis: a rule, check or practice earns its place only if it helps deliver tests and code that match the KPIs
  and the spec with less drift, and it enters the product only after it has proven itself in use (DEC-1052).
- Trust, then catch and correct; do not prevent (EMERGENCY-2 §2.1; DEC-1211). The Gov OS guards against honest
  mistakes and drift, not a same-privilege adversary, and judges work by the golden rule (DEC-1204; ADR-0001).

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
- **Enforcement** (architecture v0.3 §2.1 L3; DEC-152, DEC-161): a default-deny path guard; the guard with an OS
  sandbox for worker sessions (the experiment of DEC-1098 (4)); or none. The owner chose **none**: no guard, no sandbox,
  no box and no permission prompts, the landing being deterministic code that catches and corrects (EMERGENCY-2 §2.1,
  §2.2; DEC-1211). The other two are retired, and DEC-1098 (4) is superseded.

## Decision Outcome

### 1. Layers (architecture v0.3 §2.1, amended)

| # | Layer | Content | State |
|---|---|---|---|
| L0 | Harness | Claude Code (primary); AGENTS.md for other harnesses; subagents; LSP stays a harness feature | session only |
| L1 | Organisation | Role subagents generated by rulesync from kernel role files plus the project roster (DEC-066) | repo files |
| L2 | Instructions and skills | rulesync-generated CLAUDE.md, AGENTS.md, `.claude/`; three vendored Superpowers skills; Gov OS skills. The search-again practice is in the briefs and in the two kernel skills (W2-142; DEC-1094 (2)). `gov brief` puts the ticket's retrieval into every brief, and every template and skill says memory first (EMERGENCY-2 §5.4; CAP-65) | repo files |
| L3 | Catch and correct (was Enforcement) | **Retired by EMERGENCY-2 §2.2 and §6.1 (DEC-1211; Contract v5 §2 Boundary):** the PreToolUse default-deny guard with its rules and parser; post-command containment hooks, also on `PostToolUseFailure` (DEC-153); the OS sandbox for a worker's Bash (DEC-152, DEC-161); the escape-hatch denial and the oracle's `Read` deny rule (DEC-162); the install rule (DEC-083's `ask` and `deny`, DEC-172, DEC-174); the ACT pipeline (§2.10); permission prompts and editing (CAP-58's write-time rules, CAP-61.a, .c, .f, CAP-62, CAP-25.e to .g, CAP-49.b, .c). **What stands:** the checkpoint hooks (SessionStart, PreCompact, Stop; §6.1); **the landing** (`gov queue`: it merges into integration, runs the impact-selected tests on the merged result, and checks trailers, paths as a notice, test authorship, a committed tree, store freshness and disk, and writes the close record; EMERGENCY-2 §4.3, §4.4; CAP-63, CAP-58); role separation by the landing, the templates, the briefs, the skills and the path map (§1.2), the landing refusing an acceptance-test change that lacks the test designer's role (MR-3); `gov retrieve` filtering every route by the caller's `role_paths` (DEC-1065 (2)); the transcript scan for hidden sets (§2.7; CAP-66); two settings deny lines, `git push` and `sudo` (§2.4); an hourly `git bundle` of each repository, kept outside the tree (§2.8; CAP-67); lefthook G1–G3; GitHub Actions G4–G5, **advisory**, on an unprotected `main` (DEC-075, DEC-087) | repo files |
| L4 | `gov` CLI | **W1:** `status · check · readiness · doctor · rebuild · closure · retrieve · checkpoint · close · adopt --lite · pause`, plus the claim lock, and `launch`, the start command for worker sessions (DEC-153, DEC-161; not one of the twelve governance operations). `context` is retired (EMERGENCY-2 §5.5; DEC-1214 M1) and `pause` is carried by the launch, the dispatcher and the landing (CAP-05). **W2:** `impact · discover` (DEC-166; `readiness --generate` folds into `discover`, EMERGENCY-2 §6.2 A-4); `brief`, carrying the ticket's retrieval (W2-197; CAP-15); `rebuild --integration`, the double-buffered integration store, and `launch` setting `GOV_STORE` (W2-116; DEC-1087 (3)); `links` (W2-129; DEC-1074 (7), DEC-1087 (4)); `plan` (W2-136; DEC-1088); `launch` refusing a lead outside the approved batch or with unmet waits, and any session while the resource gate is shut or the machine's limits would be passed, with one recorded override (W2-136, W2-20; DEC-1088 (5)); `queue`, the landing (W2-115b; CAP-63), and `accept` (EMERGENCY-2 §4.3); `update --check` and `update` (W2-17, W2-18), built for the release (EMERGENCY-2 §6.1, §7.6; CAP-45), which brings them back from Wave 3 (DEC-1089 (2)). **W3, only from friction** (EMERGENCY-2 §8.4): `claim` (concurrency) · `route` · `health` · `research sync` | code |
| L5 | Authority (git) | OpenSpec specs, changes and the `feature-readiness` artefact; MADR decisions; **ticket** tasks in `.tickets/` with KPIs, role, allowed paths, profile; lessons, failures, research, checkpoints, gate records; overlay; `framework.lock` | **git only** |
| L6 | Derived runtime | The store: frontmatter graph with the stated links as typed edges (W2-92; DEC-1074 (5)) + FTS5 + sqlite-vec + the code graph; the codebase-memory index in a per-repository home (DEC-074 Q10). **One integration store** for every session, at `w2/integrate`'s head, outside the trees (`integration_store` in `governance/project/rebuild.yaml`): two halves behind one link, rebuilt by the `reference-transaction` hook after every update of the integration branch, seeded from the ready half and switched only on a complete build, with a daily backstop (W2-116; DEC-963, DEC-1087 (3)). A worktree has no store of its own; `gov launch` sets `GOV_STORE` (DEC-1087 (3)); the test designer retrieves only from it (DEC-963). The store is built with the pinned code that searches it. No cold rebuild: every copy is seeded from the warm integration index and embeds only what changed (W2-122; DEC-1032 (3)(iv), DEC-1033 (2)(d)), and each text is embedded once on the machine through a shared vector cache (W2-126; DEC-1032 (1), DEC-1039 (1)). A rebuild asked for its semantic store that does not recreate it fails, named (DEC-1015 (4)); `--no-embeddings` skips it (DEC-530) | gitignored; `gov rebuild` |
| L7 | Distribution | `gov-os` as a Copier template; `framework.lock` = answers ref + file-hash manifest. A release is numbered, pinned and hash-verified by its manifest and file hashes (CAP-02, CAP-43.b); no tag is signed until friction asks for it (DEC-1214 L3; CAP-02.c). The owner cuts the release and re-pins (EMERGENCY-2 §2.5, §8.3); the lean release is accepted by §8.2; `gov update` moves a repository between releases without re-adopting (§7.6; CAP-45); the pin ladder stays by hand until it ships | tags + lock |

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
| Secrets | gitleaks + Gov OS rules. The scan runs once, in full, before a repository goes public or is shared with a third party, and never while it is private; secret-class paths stay out of every index by the path map's sensitivity classes (EMERGENCY-2 §2.11; DEC-1045, DEC-1219 (1); CAP-03) | 8.30.1 (DEC-056) | `88f91962…2e5509` |
| Method skills | Superpowers: test-driven-development, systematic-debugging, verification-before-completion (copied, not the plugin) | v6.4.2 | `f2a95244…e8c0b90a` |
| Python tooling | uv | 0.12.21 | `e8a4e7b4…478eb2076` |
| Node | Node LTS (tools only; the nvm default stays v18.20.8) | v22.23.3 | `fde6a4bf…5e348f48` |
| Telemetry (W1) | ccusage | 20.0.26 (DEC-192) | `b8d59c19…5eb1f2` |
| Harness | Claude Code (CLI for headless runs aligned with the VS Code extension's bundled version) | 2.1.292 (DEC-637, DEC-649) | `a967e7b1…a4ec93b3` |
| The `gov` CLI | the wheel of release 0.1.3 in its own environment, linked from `~/.local/bin/gov` (the owner's re-pin from release 0.1.3, recorded in `governance/project/tool-registry.yaml`; DEC-1037 (1), DEC-1087 (8), DEC-1061 (8)) | `pin-1d4e6a875a5d` (gov 0.1.3, tag v0.1.3) | wheel `707ebfd6…bbca6` |

- **Rejected:** qmd 2.8.3, Backlog.md 1.53.0, adrkit 0.15.0, beads_rust, and LSP as a stack component;
  mxbai-rerank-large-v2 (76 of 138; DEC-1079); a CPU query embedder (DEC-798, superseded by DEC-1033; DEC-1065 (1));
  non-commercial rerankers (DEC-1079 (d)).
- **Retired:** the sandbox prerequisites, bubblewrap 0.9.0 and socat 1.8.0.0 (DEC-141): there is no sandbox
  (EMERGENCY-2 §2.2; CAP-61).
- **Measured, not adopted:** Qwen3-Reranker-4B in 8-bit (DEC-1077 (b)); M1 and M3 (better hit@5, no better answers
  end to end: E4; DEC-1097 (5)); measured on the fresh 80 for data only (DEC-1097 (5)).
- **Deferred:**
  - Docling and MarkItDown (Wave 3 research lifecycle);
  - RAGFlow (CONDITIONAL, DEC-020);
  - the OTel stack (Wave 3);
  - gpt-oss:20b (Wave 3 routing, DEC-083);
  - the embedder trial (Qwen3-Embedding-4B): a Wave 3 row (DEC-1097 (14)).
- **Installs:** the CTO approves and records every install, upgrade or removal in the tool registry (tool, exact
  version, source and checksum, need, disk and RAM, uninstall command), so that nothing out of the work's scope or
  beyond the machine's capacity is installed. There is no permission prompt, and `sudo` stays with the owner
  (DEC-083, DEC-1214 G7; Contract v5 §2 Tool installs). The ACT pipeline, which treated a change to the machine outside
  the repository (`~/.local/bin`, `~/.config`, `~/.ollama`, the crontab, services) as a rehearsed ACT, is retired:
  control files change by ordinary commits (EMERGENCY-2 §2.10; DEC-1038 (1), DEC-1057, DEC-1058 as they stood).
  `gov doctor` compares these pins with what it finds.
- **The `gov` CLI:**
  - It is a Python 3.12 package in the Gov OS repository (`src/gov/`). Every session runs the pinned wheel. Releases and
    re-pins are the owner's (EMERGENCY-2 §2.5, §8.3). A re-pin runs its checks before the switch, installs the new pin
    beside the old one and switches by one rename, the old pin kept for an instant rollback (DEC-1037 (1)); each
    release's wheel is built twice from a clean export and the two builds match. A release is pinned and hash-verified,
    with no signature until friction asks for it (DEC-1214 L3; CAP-02, CAP-43.b). The kernel records the `gov` version
    pin. Its pinned install (W2-18) and `gov update` (W2-17) are built for the release (EMERGENCY-2 §6.1, §6.2 A-4,
    §7.6; CAP-45), which changes DEC-1089 (2)'s placement in Wave 3.
  - Its core needs only the standard library, PyYAML and sqlite-vec.
  - **The reranker** is one shared service per user (W2-112; DEC-979 (4), DEC-1033 (2)(a)): `rerank_service.py` in the
    reranker venv, on the socket `~/.cache/gov-os/rerank.sock`, started by the first search under a lock when none
    listens and ending after an idle period (DEC-1034 (3)). It releases its GPU memory after each request (DEC-1068).
    It holds reranker GPU slot 0 and does not start below its GPU share: never the CPU (DEC-1036 (1), (2),
    DEC-1043 (2)). A search that cannot reach it keeps the fused order, named `rerank: unavailable`, and never starts a
    private reranker, on the GPU or the CPU (W2-145, closed; DEC-1046 (1), DEC-1048 (5), DEC-1097 (8)). The CTO's
    interim slot module and slot-hold watcher stay on this machine until old code fails closed by construction
    (DEC-1043 (2), DEC-1048 (1)).
  - **The embedders:** `gov` never starts an embedder for a search, a rebuild, a close, a seed or a launch.
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
- **The machine.** On this repository the CTO's tools derive every limit from the machine detected; in the product it
  is the run-time tool's work (RT-3, RT-4; EMERGENCY-2 §6.3; CAP-64; DEC-1037 (4), DEC-1097 (8)). Today it is WSL on 20
  logical CPUs with a 24 GB memory cap, and a 16 GB GPU (16,303 MiB) (recorded with DEC-1038; DEC-1076 (4)).
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
  (DEC-1030), and the servers restart by class from their committed configurations, (DEC-1057 (4)).
  In the product they are the run-time tool's (RT-3, RT-4; CAP-64; DEC-1030 (4), DEC-1031 (4)). No Docker.
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
- **the bundle:** 6,000 tokens, retrieval's own bound on parent expansion only (DEC-419 DP-3; kept against 12,000 by E5,
  DEC-1097 (1)); it is not a packet ceiling, of which Contract v5 has none (§2 Token budget; DEC-1214 M1). An item whose
  line runs over 4,000 characters is cut to 4,000, marked `cut`, its path and lines cited unchanged (W2-135;
  DEC-1086 B);
- **the brief carries the bundle:** `gov brief` puts the ticket's whole retrieval bundle, uncut, into every brief, with
  its mandatory inputs by id and sha256 and no unfilled placeholder, and a memory-use log records each retrieve
  (EMERGENCY-2 §5.4, §5.6; CAP-15, CAP-65). It replaces `gov context`, retired with its packet, packet hash and
  ceiling (§5.5; DEC-1214 M1);
- **search respects role separation:** every route's hits are filtered by the caller's `role_paths`, and what is
  withheld is counted in the bundle (W2-13 S5; DEC-1065 (2));
- a cited evidence bundle: citations by id and sha256, and one stopping reason from `CLOSURE_COMPLETE`, `SATURATED`,
  `DEPTH_LIMIT_REACHED`, `BUDGET_EXHAUSTED_WITH_GAPS`, `FACET_UNAVAILABLE`, `UNRESOLVED_IDS` (the sixth value, added
  by DEC-396: everything within depth was reached and some referenced ids name nothing);
- the citation validator;
- zero-result canaries per index;
- hierarchical synthesis notes (derived, cited, hash-checked): built only if friction asks, off with `gov context`
  (CAP-15.f; EMERGENCY-2 §8.4);
- **search again once**, the agents' standing practice: when the first bundle does not answer, or the answer may be
  incomplete, search again once in other words, then settle as not found; two searches at most (DEC-1092 (1),
  DEC-1094 (2)). Overlapping slices of one record stay as they are before the fresh 80 (DEC-1097 (7)).

Secrets are kept out of every index by the path map's sensitivity classes (DEC-074 Q8); the gitleaks content scan runs
once, in full, before a repository goes public or is shared with a third party, never while it is private
(EMERGENCY-2 §2.11; DEC-1045, DEC-1219 (1); CAP-03). Wave 1's exit runs RETR-A-04 and RETR-X-02.

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

The hidden sets of memory's measure live outside every worktree and are never indexed (DEC-1052 G-3, DEC-1055 (4),
DEC-1066 (3)). With no guard, a set is protected by the transcript scan: it reads every transcript written between the
set's writing and the end of its measure for the set's path and question ids, and a hit voids the measure; the memory
reader runs with only the memory tool, and the gold sits outside the index and the clone (EMERGENCY-2 §2.7, A-12;
CAP-66; DEC-1214 E3). The guard rule that refused the hidden sets, DEC-1082 (3), DEC-1084 (1) and ACT-GUARD-SETS-1,
is retired (DEC-1211).

### 6. Operating model

*Revised 2026-11-19: this states the operating model under EMERGENCY-2 (DEC-1211), with the memory lines of the
2026-11-08 refresh.*

- **Roles** (DEC-066, DEC-163). Wave 1 has five roles, and a sixth in a minimal form:
  - orchestrator (the CTO): runs the flow and the build list, and approves and records every tool install, so that
    nothing out of the work's scope or beyond the machine's capacity is installed. Every install is recorded in the
    tool registry (version, sha256, install and uninstall commands, date, approving decision), and `gov doctor` checks
    the pins. There is no permission prompt, and `sudo` stays with the owner (DEC-083, DEC-095; DEC-1214 G7;
    EMERGENCY-2 §2.2);
  - product/specification;
  - independent test designer: writes the acceptance tests in `tests/acceptance/**` from the KPIs, red on the base;
  - engineer: never writes `tests/acceptance/**`; builds until `gov accept` is green. The landing refuses an
    acceptance-test commit that lacks the test designer's role (MR-3; EMERGENCY-2 §4.3, §4.4; CAP-58);
  - independent auditor: read-only and fresh, called as MR-4 says (§7);
  - research, minimal (DEC-163): a role file delivered with the launcher (W1-46). It runs as a launched worker session
    in its own worktree, on its ticket, with its experiment folder as the ticket's `allowed_paths`, which the landing
    judges as a notice (CAP-58). It installs only into a venv or local prefix inside that folder, never system-wide
    (Contract v5 §2 Tool installs). Its network allowlist (DEC-158) and the write fence of generated `Edit` deny rules
    (EXP-001 §3.4) are retired with the sandbox (CAP-61.c; EMERGENCY-2 §2.2). It runs as `GOV_ROLE=research`. The full
    research lifecycle (CAP-32) stays in Wave 3.

  Wave 2 and Wave 3 roles follow Charter v6 §6, with test execution and integration as distinct Wave 2 roles
  (DEC-094). A ticket lead runs one ticket's loop, and a senior engineer one stream's tickets, under the CTO
  (EMERGENCY-2 §4.3; DEC-1087 (13)).
- **The owner** is the customer and L5. Decision packages come in chat, ranked P1–P3 and batched at most five at a
  time; a P1 package may bypass the cap (DEC-093). The template carries ten fields (Framework §52).
  Answers are recorded in git (MR-6).
- **Until the lean release** (DEC-073, DEC-084, which said "Release 1"; EMERGENCY-2 §8):
  - the owner's operator is his own interactive session, with full permission across WSL; the operator agent, its cron
    launcher and its lock are retired with the ACT pipeline (EMERGENCY-2 §2.6, §2.10; Charter v6 §6);
  - the first text bootstrapped MR-3 with settings deny rules and an operator diff check, and then ran the Gov OS
    "under its own guard": retired. The landing holds MR-3 (EMERGENCY-2 §4.3), and the lean release is accepted by
    §8.2.
- **Permission and write scope** (DEC-150, DEC-156 and W1-45's orchestrator exception, retired by EMERGENCY-2 §2.2,
  §2.3). Every agent has full permission in the repository it works in, its worktree and its run folder; the CTO has
  four more places: the evaluation sets, the machine state in `~/.gov-os`, the crontab and EXAMIN APP. Sessions stay
  apart by where each starts, the folders it is given and its brief; nothing enforces it. Paths declared on a ticket
  are checked at the landing as a notice, never at write time (CAP-58; Charter v6 §3, principle 7). The exclusion of
  `tests/acceptance/**` that the guard held for the orchestrator is now the landing's test-authorship check; the path
  map's `acceptance_exemptions` lists the commits the owner exempted (DEC-1217 (2)). Checkpoints and compaction stay:
  the SessionStart, PreCompact and Stop checkpoint hooks and `gov checkpoint` (W1-25; EMERGENCY-2 §6.1; CAP-37).
- **Worker sessions** (DEC-152, DEC-153, DEC-161; W1-46; CAP-61.b):
  - engineer, independent test designer, independent auditor, and research or experiment work run as worker sessions
    the orchestrator starts with `gov launch`, each in its own worktree; in-session subagents remain for read-only
    work (review, exploration, web research);
  - the launcher starts the worker with its role file, sets `GOV_ROLE`, `GOV_TICKET`, `GOV_STORE` (DEC-1087 (3)) and a
    per-session temp directory (DEC-159), and runs it on the model and effort the owner's rubric gives its role,
    refusing a launch the rubric does not give (DEC-1212 (2), DEC-1214 K1; CAP-61, RT-8). It also refuses a lead
    outside the approved batch, and any session while the resource gate is shut (DEC-1088 (5)). It sets no per-role
    `--settings` sandbox block, and the session meets no permission prompt. A fix under its owning ticket and a chore
    with no ticket are accepted, and a new ticket must be a feature with its spec and KPIs, flagged at the landing if
    not, never refused: decided for release 0.1.4 (DEC-1219 (5));
  - **memory in every session:** with no sandbox, every session retrieves from the one store, with the semantic route
    and the shared reranker, and the brief no longer says "No `gov retrieve` in the sandbox" (EMERGENCY-2 §5.7;
    CAP-65.b). The sandbox's refusal of the reranker's Unix socket (DEC-1034 (1)), W2-127 and W2-186 are moot
    (EMERGENCY-2 §6.1); never a private CPU embedder (DEC-1065 (1); §5.8);
  - worker roles never install system-wide (DEC-157; Contract v5 §2 Tool installs); the research role's installs inside
    its experiment folder are its one exception (DEC-163). The guard's install rule, the settings' ask rule (DEC-172),
    the `uv` extension of the rule (DEC-174) and `excludedCommands` (DEC-164) are retired with the guard and the sandbox
    (CAP-25.e to .g; EMERGENCY-2 §2.2).
- **The qualification oracle** (DEC-067, DEC-162) is held out of the tree: its path is held in
  `governance/project/held-out.yaml`, and no acceptance test names it. A sandbox, a `Read` deny rule and the guard no
  longer hide it (retired: CAP-49.b, CAP-49.c; EMERGENCY-2 §2.2). A read of it is caught by the transcript scan, which
  voids a measure whose hidden set was read (EMERGENCY-2 §2.7; CAP-66), not prevented.
- **The untested sandbox cases** (`denyWrite` on a path that doesn't exist yet, symlink and hard-link tricks, the
  seccomp filter, `bypassPermissions` mode), EXP-002 (DEC-160) and the two residuals sent to it (subagents inside a
  sandboxed worker session, and `excludedCommands`, DEC-164) are moot: there is no sandbox to test (CAP-61.f;
  EMERGENCY-2 §2.2).
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

*Revised 2026-11-19 for MR-4's audit triggers and the loop budget (DEC-1214 G6, DEC-1204; Charter v6 §4, §5).*

| Function | Question | Mechanism | Wave |
|---|---|---|---|
| `gov doctor` | Is the Gov OS installed and healthy here? | pins, hooks, path map, index freshness, canaries, framework.lock; deterministic | W1 |
| Discovery | Is this specification closed, and what must the customer answer? | discovery skill + `gov readiness`; linked gap tickets (DEC-089) | W1 (automatic generation W2) |
| Impact (CIT-P) | What will this change affect? | OpenSpec proposal; `gov impact` over both graphs | W1 proposal; W2 computed |
| Execution (CIT-E) | Was the change applied as proposed? | OpenSpec apply/archive + `gov close` trailers + checkpoint | W1 |
| Audit | Does the actual state match the specification, contract and decisions? | fresh read-only Independent Auditor + audit skill. It runs at the release acceptance and at adoption stages A5, AS, A7 and A10 (MR-4; DEC-1214 G6); otherwise a review happens only for a red test, a failed landing or merge, or a feature that does not work as intended (EMERGENCY-2 §3.4, §3.6). The audits of every spine closure and of every wave and release exit (DEC-088) are retired. Contested and owner-level findings go to the owner as decision packages; a fix is recorded in the owning ticket | W1 (full roles W3) |

The fidelity audit (S1-A, done) and the audits MR-4 now calls use the Independent Auditor role (DEC-070, DEC-082).
Every review→repair, audit→repair, test→fix or verification loop follows DEC-096 as DEC-1204 amends it (Contract v5 §2
Loop budget; CAP-59):
- it runs at most two rounds, in place of DEC-096's three consecutive non-converging iterations;
- a second round that does not converge produces one escalation package for the owner (each round's outcome, why it is
  not converging, options: fix differently, narrow, split, defer, delete, continue), and the owner decides once;
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
  - Work is caught and corrected, not prevented: a deterministic landing with no write-time refusals and no permission
    prompts, so the owner is not the relay (EMERGENCY-2 §1.4, §2). The sandbox's closing of Bash writes at the OS level
    (EXP-001) went with it.
  - Every session searches one current store, refreshed after every merge, with the models on the GPU and loaded
    once for the machine, not once per session (DEC-1031, DEC-1033, DEC-1087 (3)).
  - On the 138 tuning questions, window 4's configuration answers right end to end on 83.3 % with one search and
    92.8 % with search again once, wrong claims 2 → 3 (E2; DEC-1092 (1)); hit@5 is 76.8 % and the gold is in the
    first bundle for 89.1 % (E0); hit@k is a diagnostic only (EMERGENCY-2 §5.2).
- **Bad:**
  - Wave 1 glue grows to ≈ 5,680 LOC (the figure in `docs/plan/WAVE_1_WBS.md` §3), against architecture v0.3's ≈ 2.4k.
    This is the effect of DEC-080, DEC-074 R1, DEC-076, DEC-083, DEC-086, the S1-A repairs (DEC-089…DEC-092, and
    a ticket KPI for every Wave 1 `covers` item), and the S2 change (+370 LOC: W1-45, W1-46 and W1-47, +320; KPIs added to W1-30 and W1-31, +50). DEC-064 turns
    DEC-001's size trigger into a per-wave review. The guard, sandbox and `gov context` code in the figure is retired
    (EMERGENCY-2 §2.2, §5.5); the figure is not re-measured.
  - Nothing prevents a session from reaching beyond its folder: a shell command can reach anywhere the owner can. The
    landing and the transcript scan catch it afterwards (EMERGENCY-2 §2.3, §2.7); the boundary is git history, the two
    deny lines and the hourly `git bundle` (Contract v5 §2 Boundary). The sandbox's measured cost (EXP-001 §3.6;
    DEC-170) is gone; governance tokens are reported weekly against the 56 % of before EMERGENCY-2 (Contract v5 §2
    Token budget).
  - `ticket` is unmaintained upstream; it is vendored by hash.
  - The reranker venv is 5.6 GB. Wave 2's trial measured lighter and heavier rerankers on hit@5 and MRR (DEC-074 Q3's
    spike); only M1 and M3 were run end to end (E4), and neither made agents answer better, so the 0.6B and its venv
    stay (DEC-1097 (5)).
  - The GPU is one shared resource for every session's memory: a CUDA crash or a model loaded off the GPU degrades
    every search. On this repository the CTO's dispatcher watches it and pushes an alert at once (DEC-1029, DEC-1030);
    in the product it is the run-time tool's (CAP-64; DEC-1030 (4)).
  - The shared reranker saturates its GPU when 20 agents search at once (14.5–17.4 s
    for a burst of 20 in G1; 13.4–13.9 s in PAT-1). The lever, fewer scored pairs per search, changes ranking; it comes to the owner after the lift, with the 138 re-measured if adopted
    (DEC-1097 (10)).
  - Interims remain outside the product until retired: the machine-wide reranker slot module and the slot-hold watcher
    (DEC-1043 (2), DEC-1048 (1), (5)), which W2-145 (closed) leaves in place until old code fails closed by
    construction; the query server's start wrapper, whose removal DEC-1037 tracks by a W2-20 / W2-121 KPI line that no
    ticket carries yet.

### Confirmation

- The release acceptance of EMERGENCY-2 §8.2 and the independent audit at it against Contract v5: the Contract's checks
  pass (`docs/emergency-2/audits/07-contract-rebaseline.md`), the proving run on the synthetic repositories passes,
  EXAMIN's copy is adopted with memory at 95 % or more end to end, and one EXAMIN feature ticket goes through the flow.
  The Wave 1 exit (WAVE_1_WBS §4) stands as history.
- `gov doctor` checks every pin in §2.
- **Memory's verdict:** a fresh 80 questions (40 visible, 40 hidden), written and measured at once on a pinned
  snapshot, judged end to end at 95 % or more: the reader reads the whole ranked bundle and searches once more in its
  own words, and both the answer and its citation must be right; the hidden half's figure is the verdict, and hit@k is
  a diagnostic only, never a target (EMERGENCY-2 §5.2, §5.3; CAP-10; DEC-1210 (1)). A miss is a memory-quality event,
  judged by the next fresh 80, no set reused (CAP-19.c). K9's bar of 85 % and the 138's re-measure at the release
  commit (DEC-1097 (1), (4); DEC-1092 (4)) are replaced by this.
- Every comparison of memory reports its gains, its losses and an exact McNemar test (DEC-1079 (b) L1).

## More Information

- **Sources:** architecture v0.3; S0a `STACK_OPTIONS.md`, `CAPABILITY_CATALOGUE.md`; S0b2 `RESULTS.md`,
  `GLUE_REQUIREMENTS.md`, `TOOL_REGISTRY.yaml`, `INTEGRATION_REPORT.md`; register DEC-064…DEC-096, and
  DEC-138…DEC-174 for the launcher, the research role and the lesson loop (and, as history, the sandbox layer retired by
  EMERGENCY-2 §2.2); `spike-sandbox/EVIDENCE.md` (EXP-001, ADOPT-PARTIAL, history);
  for Wave 2's memory, DEC-1029…DEC-1097, `governance/project/tool-registry.yaml` (the `gov` entry of re-pin
  window 4), `docs/research/W2-88-memory-practice.md`, `docs/research/W2-112-shared-reranker.md`, and
  `governance/project/orchestration/packages/LIFT-1/` (E0 to E5, E0B, E2G, G1-PROFILE, PAT-1, BUNDLE-BUDGET-1,
  M3-ADOPTION-1, FRESH-80-1).
  For the revision of 2026-11-19: `docs/emergency-2/EMERGENCY-2.md` (§2 to §8), `docs/charter/CHARTER_v6.md`,
  `docs/contract/CONTRACT_v5.md` (§2 and CAP-58, CAP-61, CAP-62 to CAP-66), `docs/emergency-2/audits/07-contract-rebaseline.md`
  (Tables 1 and 2, C-4), and DEC-1204, DEC-1210, DEC-1211, DEC-1214, DEC-1217, DEC-1219.
- **Revisit triggers:**
  - a code graph above the tested envelope;
  - vectors above ~100k (move to LanceDB, DEC-016);
  - OpenSpec or codebase-memory-mcp breaking changes at a pin upgrade;
  - the per-wave glue review;
  - a reranker or embedder that makes agents answer better end to end on the 138 under a reading rule declared before
    its figures, measured on the standing model bench (DEC-1069 (13), DEC-1097 (5));
  - any change to retrieval, judged by the next fresh 80 (CAP-19.c; DEC-1097 (3), (4) as replaced by EMERGENCY-2 §5.3);
  - the glossary's fate (DEC-1096; DEC-1097 (6), open);
  - friction with an adopted repository, from which Wave 3's items are built (EMERGENCY-2 §8.4).
