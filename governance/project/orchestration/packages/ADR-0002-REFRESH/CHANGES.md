# ADR-0002 refresh: the changes, old → new (DEC-1093 (3), DEC-1097 (8))

- **Draft:** `ADR-0002-architecture-and-stack.md` beside this file; revised once for round 1's findings (§8b). The live ADR in `docs/adr/` is not touched.
- **Drafted:** 2026-11-08 by a product-spec agent for the CTO (session `ad44f5fe`). Status stays PROPOSED.
- **Basis:** the register up to DEC-1097 (v0.481), `governance/project/tool-registry.yaml` (the `gov` entry of re-pin
  window 4), `governance/project/retrieval.yaml` and `rebuild.yaml`, `docs/research/W2-88-memory-practice.md`,
  `packages/LIFT-1/` (E0 to E5, E0B, G1-PROFILE, PAT-1, BUNDLE-BUDGET-1, M3-ADOPTION-1 §2), and the code at
  `w2/integrate` where a decision names a ticket (the role filter and S10 checked to be inside `bcea09060ebc`).
- **"Live" means** on window 4's pin `pin-bcea09060ebc`. Items that land at the lift's re-pin are marked so in the
  draft (W2-136, W2-137, W2-138, W2-141, W2-142, W2-145 "no private reranker beside the service").
- **The next step:** one independent review, then the owner accepts or returns it (DEC-1093 (3)).

## 1. Front matter and header
| # | Where | Old | New | Decision |
|---|---|---|---|---|
| 1 | `decisions:` | 47 ids, DEC-064 … DEC-174 | 115 ids: those 47 plus every later id the text now cites (DEC-798, superseded, cited but not listed) | DEC-1093 (3) |
| 2 | Under the title | — | "Status PROPOSED; refreshed 2026-11-08 for the owner's acceptance (DEC-1093 (3))" and a pointer to this file | DEC-1093 (3) |

## 2. Context, drivers, options
| # | Where | Old | New | Decision |
|---|---|---|---|---|
| 3 | Context | three bullets (v0.3, S0b2, DEC-080/076/083-087) | a fourth: Wave 2 rebuilt memory's runtime; the ADR states window 4's pin | DEC-1087 (8), DEC-1097 (1) |
| 4 | Driver 4 | "fits a 15.5 GiB, 16 GB-VRAM workstation, with no Docker and one on-demand daemon" | no Docker; every limit derived from the machine detected; memory's models on the GPU within budget, never spilling, never on the CPU | DEC-1037 (4), DEC-1031, DEC-1039 (1b), DEC-1065 (1) |
| 5 | Drivers | — | memory judged end to end, its verdict from a set used once | DEC-1085, DEC-1092 (4), DEC-1097 (1) |
| 6 | Drivers | — | the basis: helps deliver with less drift; a practice enters the product only after proven in use | DEC-1052 |
| 7 | Options | the S0a stacks and four bake-off pairs | + Wave 2's reranker trial (4B 8-bit, mxbai, gte, zerank, cascade, M1, M3); the 0.6B kept | DEC-1068, DEC-1069, DEC-1076 (4), DEC-1077, DEC-1079, DEC-1081, DEC-1097 (5) |
| 8 | Options | — | query embedding on the CPU or the GPU: the GPU only | DEC-798 (superseded), DEC-1033, DEC-1065 (1) |
| 9 | Options | — | the bundle's shape (top 5/10/20, today's, 40 unranked, 12,000 tokens): today's 6,000 kept | DEC-1092 (2), DEC-1097 (1) |

## 3. §1 Layers
| # | Row | Old | New | Decision |
|---|---|---|---|---|
| 10 | L2 | rulesync files, three Superpowers skills, Gov OS skills | + the search-again practice: project layer now, two kernel skills by W2-142 at the lift | DEC-1094 (2) |
| 11 | L3 | guard, sandbox, install rule, lefthook, CI | + role separation by path checks from the path map, and `gov retrieve` filtered the same way | DEC-1052 G-14, DEC-1056, DEC-1059, DEC-1065 (2) |
| 12 | L4 | W2: `impact · readiness --generate · update --check · discover` | W2: `impact · readiness --generate · discover`, + `rebuild --integration`, `launch` setting `GOV_STORE`, `links`, `plan` (at the lift); `update --check` moved to W3 with W2-17 | DEC-166, DEC-1087 (3), (4), DEC-1074 (7), DEC-1088, DEC-1089 (2) |
| 13 | L6 | `.gov-runtime/store.db`: graph + FTS5 + sqlite-vec from W1 | one integration store at the integration head, outside the trees, two halves behind a link, rebuilt by the `reference-transaction` hook after every update, seeded, switched only on a complete build, daily backstop; no store per worktree; `GOV_STORE`; designers search only it; built with the pinned code | DEC-963, DEC-1087 (3) |
| 14 | L6 | frontmatter graph | the stated links as typed edges (W2-92) | DEC-1074 (5) |
| 15 | L6 | — | no cold rebuild (seeding, W2-122); each text embedded once (vector cache, W2-126) | DEC-1032 (1), (3)(iv), DEC-1033 (2)(d), DEC-1039 (1) |
| 16 | L6 | — | a rebuild that does not recreate its asked-for semantic store fails, named; `--no-embeddings` skips it | DEC-1015 (4), DEC-530 |
| 17 | L7 | Copier, signed tags, lock | + the first numbered, frozen release after the lift's re-pin; the pin ladder by hand until W3 | DEC-1090 (5), DEC-1089 (2) |

## 4. §2 Stack
| # | Row | Old | New | Decision |
|---|---|---|---|---|
| 18 | Heading | pins from `s0b2/out/TOOL_REGISTRY.yaml` | + `governance/project/tool-registry.yaml` | (descriptive; DEC-083) |
| 19 | Lexical | SQLite FTS5 | SQLite FTS5, BM25 | (descriptive, W2-88 §1; no decision) |
| 20 | Vectors | 0.1.9, sha "venv" | 0.1.9 (DEC-397), sha of `vec0.so` from the registry | DEC-397 |
| 21 | Embeddings | Ollama + qwen3-embedding:0.6b | the same pins, in two shared GPU servers (:11434 index, model kept loaded; :11435 questions), CPU-capped; a CPU vector refused; model blob sha | DEC-397, DEC-1031, DEC-1033 (2)(b), DEC-1065 (1) |
| 22 | Reranker | 0.6B in the R1 venv; sha "HF etag" | the same pins in `~/.local/share/gov-os/reranker-venv`, served by one shared service; sha of `model.safetensors` | DEC-397, DEC-1033 (2)(a), DEC-1043 (2) |
| 23 | Fusion | RRF (R1) | RRF over the routes with the authority lift, routing by question type and the pool; pin column `retrieval.yaml` | DEC-1067 (a), DEC-1075 (3) |
| 24 | Secrets | gitleaks 8.30.1 | + switched off by configuration on this repository, on elsewhere, the switch named | DEC-1045 |
| 25 | Telemetry | "pinned by the orchestrator on approval" | 20.0.26 | DEC-192 |
| 26 | Harness | ≥ 2.1.285 | 2.1.292, with its sha | DEC-637, DEC-649 |
| 27 | New row | — | the `gov` CLI: `pin-bcea09060ebc`, wheel sha `11a16d0f…d406` | DEC-1037 (1), DEC-1087 (8), DEC-1061 (8) |
| 28 | Rejected | qmd, Backlog.md, adrkit, beads_rust, LSP | + mxbai-rerank-large-v2; a CPU query embedder; non-commercial rerankers | DEC-1079, DEC-1079 (d), DEC-1033, DEC-1065 (1) |
| 29 | New list | — | "Measured, not adopted": the 4B in 8-bit; M1 and M3 (data only on the 80) | DEC-1077 (b), DEC-1097 (5) |
| 30 | Deferred | Docling/MarkItDown, RAGFlow, OTel, gpt-oss:20b | + the embedder trial (Qwen3-Embedding-4B), a Wave 3 row | DEC-1097 (14) |
| 31 | Installs | through DEC-083; `gov doctor` checks | + machine changes outside the repository by ACT, rehearsed end to end | DEC-1038 (1), DEC-1057, DEC-1058 |
| 32 | `gov` CLI | "installed as a user tool pinned to the release tag" | every session runs the pinned wheel; re-pin with checks, side-by-side install, one-rename switch, rollback; W2-17 and W2-18 in W3 | DEC-1037 (1), DEC-1089 (2) |
| 33 | `gov` CLI | "the reranker runs as a separate, pinned process in the R1 venv, loaded lazily per query" | one shared service per user on `~/.cache/gov-os/rerank.sock`, started by the first search under a lock, idle end, memory released after each request, slot 0, never the CPU; fallback to a private GPU-slot reranker or the fused order named; no private reranker beside the running service | DEC-979 (4), DEC-1033 (2), DEC-1034 (3), DEC-1035 (2), DEC-1036 (1), (2), DEC-1043 (2), DEC-1046 (1), DEC-1068 |
| 34 | `gov` CLI | — | `gov` never starts an embedder for a search, rebuild, close, seed or the sandbox; `EMBEDDER_UNAVAILABLE` and keywords; only an explicit restart starts `ollama serve`, never stopped by `gov` | DEC-261, DEC-1065 (1), DEC-1057 (4) |

## 5. §3 Scale envelope and resources
| # | Item | Old | New | Decision |
|---|---|---|---|---|
| 35 | Heading | (DEC-078, DEC-074) | + "re-read for Wave 2" | — |
| 36 | New: the store | — | 69,464 chunks, 19,113 embedded from 1,126 files; `embedding_policy` per namespace | DEC-700, DEC-1052 M-4, DEC-1055 (3) |
| 37 | New: the machine | — | limits derived from it; WSL, 20 CPUs, 24 GB cap, 16,303 MiB GPU | DEC-1037 (4), DEC-1076 (4); recorded with DEC-1038 |
| 38 | RAM | ≈ 12.5 GB of 15.5 GiB | the same, marked "not re-measured on Wave 2's runtime" | (none: open point 2) |
| 39 | VRAM | "peak ≈ 5.2 of 16 GiB, returning to baseline when idle" | budget 14,255 MiB; embedders first (≈ 5.6 GB), reranker second (≈ 4.8, up to 6.4 GB); measured 8,404 MiB (E0), ≈ 9.4 GB at 20 at once (G1); models stay loaded; spill floor 2,048 MiB; experiments' backstop 15.5 GB, one GPU job at a time | DEC-1031 (1)-(2), DEC-1032 (1), DEC-1043 (2), DEC-1076 (4), DEC-1084, DEC-1067 |
| 40 | Disk | ≈ 11.9 GB | the same, "not re-measured"; the trial downloads kept for now | DEC-1070 (1), DEC-1079 |
| 41 | Processes | "One on-demand daemon (Ollama, 5-min idle unload, started and stopped by `gov`)" | two shared embedding servers and one shared reranker service on the GPU; watched by the dispatcher; restarted by class without an ACT | DEC-1030, DEC-1057 (4) (and DEC-261: never stopped by `gov`) |
| 42 | Retrieval speed | warm p50 0.24 s / p95 0.33 s; cold index 4.5 s; incremental 2.8 s | one search 1.24 s (E0) to 1.68 s (PAT-1) median against a ~1 s target; 10 at once 6.6–6.8 s; 20 at once 13.4–13.9 s, no error; saturated at 20 (G1); the seeded store rebuild ≈ 30 s | DEC-1065 (4) (evidence E0, PAT-1, G1) |

## 6. §4 Retrieval completeness
| # | Item | Old | New | Decision |
|---|---|---|---|---|
| 43 | Heading | "Retrieval completeness in Wave 1 (DEC-080)" | + "as built through Wave 2" | — |
| 44 | `gov retrieve` | paging and continuation | + answers from the integration store; from the lift, each result carries the store's commit | DEC-1087 (3), DEC-1090 (3) |
| 45 | New: routes | — | lexical, semantic, record, closure, code, stated links; three phrasings; routing by question type | DEC-419 DP-8, DEC-1074 (5), DEC-1067 (a) |
| 46 | Filtering | dedup, authority/current/superseded | + register items carry id, status, "changed by"; PROPOSED never a rule | DEC-1073 (2) |
| 47 | New: what is embedded | — | the M-4 list; tests and close/checkpoint/probe records keyword-only; the evaluation documents indexed nowhere; chunks embedded with path and headings; models read the whole chunk | DEC-1052 M-4, DEC-1055 (3), DEC-1066 (1), (3), DEC-1067 (f), DEC-1068 (e) |
| 48 | New: the pool | — | meaning route uncut, routes 60 deep, 40 reranked, ≤ 2 chunks a file in the first 10, nested repeats dropped; on since window 4 | DEC-1074 (5), DEC-1075 (3), DEC-1089 (1) |
| 49 | One rerank | "one rerank over the merged candidate set" | by the shared service; requests ≤ 16 texts and 24,000 padded characters, 64 texts at the lift; the bundle's `rerank {by, device, reason}` | DEC-419 DP-9, DEC-1067 (f), DEC-1090 (2), DEC-1095 (1), DEC-1036 (3) |
| 50 | New: the bundle | ("within the bundle budget", no figure) | 6,000 tokens, bounding parent expansion; kept against 12,000 (E5); a line over 4,000 characters cut and marked | DEC-419 DP-3 (DEC-004), DEC-1097 (1), DEC-1086 B |
| 51 | New: role filter | — | every route filtered by the caller's `role_paths`; withheld counted | DEC-1065 (2) |
| 52 | New: search again once | — | the standing practice, two searches at most; overlapping slices unchanged before the 80 | DEC-1092 (1), DEC-1094 (2), DEC-1097 (7) |
| 53 | Secrets sentence | filtered before every indexer | + except where switched off by configuration, as here | DEC-1045 |

## 7. §5 Layouts, §6 Operating model, §7 Functions
| # | Item | Old | New | Decision |
|---|---|---|---|---|
| 54 | `governance/project/` | path-map, roster, profiles, tool-registry | + `retrieval.yaml`, `rebuild.yaml` | DEC-1075 (3), DEC-1087 (3) |
| 55 | `.tickets/` | "the Wave 1 WBS" | "the WBS" | (descriptive) |
| 56 | New line | — | `fixtures/evaluation/`, never indexed | DEC-1066 (3) |
| 57 | New paragraph | — | the hidden sets outside every worktree; decided: the guard refuses them to six measured roles and `transcripts/**`; **not yet applied** (ACT-GUARD-SETS-1 being rebuilt with the 80's reader-run folder, applied before the 80) | DEC-1052 G-3, DEC-1055 (4), DEC-1082 (3), DEC-1084, DEC-1097 (2) |
| 58 | Launcher | sets `GOV_ROLE`, `GOV_TICKET`, temp dir | + `GOV_STORE` | DEC-1087 (3) |
| 59 | New bullet | — | the shared services and the sandbox: unreachable until W2-127 (inside W2-56); fallback named; sandboxed workers run no `gov retrieve`; never a private CPU embedder | DEC-1034 (1), DEC-1035 (2), DEC-1064 (2), DEC-1065 (1) |
| 60 | New bullet | — | memory-building at every adoption's Wave 0 (W2-88's practice) | DEC-1072 (2) |
| 61 | §7 loops | DEC-096 for every loop | + reviews converge under DEC-1010 (moderator triage, at most two rounds, then the owner once, READY by code) | DEC-1010 (1), DEC-1047 (3) |

## 8. Consequences, Confirmation, More Information
| # | Item | Old | New | Decision |
|---|---|---|---|---|
| 62 | Good | — | one current store; models loaded once for the machine | DEC-1031, DEC-1033, DEC-1087 (3) |
| 63 | Good | — | E0 and E2's figures on the 138 (83.3 % → 92.8 % end to end, wrong claims 2 → 3; hit@5 76.8 %; gold in the bundle 89.1 %) | DEC-1092 (1) |
| 64 | Bad | "The reranker venv is 5.6 GB; a lighter replacement spike is Wave 2 (DEC-074 Q3)" | the spike was the trial (hit@5 and MRR); only M1 and M3 ran end to end and neither answered better; the 0.6B and its venv stay | DEC-1097 (5) |
| 65 | Bad | — | the GPU is one shared resource; watched, alert at once | DEC-1029, DEC-1030 |
| 66 | Bad | — | the reranker saturates at 20 at once; "fewer scored pairs" after the lift | DEC-1097 (10) |
| 67 | Bad | — | sandboxed workers without the semantic route and the shared reranker until W2-127 | DEC-1035 (2), DEC-1064 (2) |
| 68 | Bad | — | interims outside the product: the slot module and slot-hold watcher, the query server's wrapper; the product ticket before the lift | DEC-1043 (2), DEC-1048 (1), (5), DEC-1097 (8), DEC-1037 |
| 69 | Confirmation | Wave 1 exit; `gov doctor` | + memory's verdict on the fresh 80 against K9's end-to-end bar; the 138 re-measured at the release commit if retrieval changes | DEC-1097 (1), (4), DEC-1092 (4) |
| 70 | Confirmation | — | every memory comparison with gains, losses and exact McNemar | DEC-1079 (b) L1 |
| 71 | Sources | S0a, S0b2, DEC-064…096, DEC-138…174, EXP-001 | + DEC-1029…DEC-1097, the registry, W2-88, W2-112's research, `packages/LIFT-1/` | — |
| 72 | Revisit triggers | four | + a model better end to end under a declared rule (the model bench); any retrieval change after the verdict; W2-127; the glossary's fate | DEC-1069 (13), DEC-1097 (3)-(6), DEC-1035 (2), DEC-1096 |

## 8b. Round 1 of the independent review (`reviews/adr-0002-refresh.md`, NOT READY): the fixes
| # | Finding | Where | Change | Decision |
|---|---|---|---|---|
| 73 | F1 | §5 hidden-sets paragraph | ACT-GUARD-SETS-1 stated as decided, **not yet applied**: six measured roles and `transcripts/**`, being rebuilt with the 80's reader-run folder, applied before the 80 | DEC-1082 (3), DEC-1084 (1), DEC-1097 (2) |
| 74 | F2 | head of L3, §6, §7 | the marker "Not re-audited in the 2026-11-08 refresh", naming DEC-953 / DEC-954's lifts, the guard's five rules, the stopped nightly, six roles and the three layers; DECISIONS-IN-FORCE | DEC-953, DEC-954, DEC-1061 (3a), DEC-1049, DEC-1087 (13) |
| 75 | F3 | L3, after G-14 | a wide Grep, Glob or recursive Bash search reaching the ticket's own acceptance folder is refused only from W2-141 at the lift; until then the exclusion line in every engineer brief | DEC-1093 (2) |
| 76 | F5 | §2 reranker bullet; Bad list | "no private reranker beside the service": today only the CTO's interim slot-hold watcher; W2-112's KPI still allows one; the product change is W2-145, not yet built, before the lift | DEC-1036 (2), DEC-1043 (2), DEC-1046 (1), DEC-1048 (5), DEC-1097 (8) |
| 77 | F4 | Options; Bad list | only M1 and M3 were run end to end (E4); the others judged on hit@5 and MRR | DEC-1097 (5) |
| 78 | F7 | §2 embedders bullet | the "starts none" sentence cites W2-32 S10 / DEC-1065 (1) and says it changes DEC-261's start, DEC-261 not yet marked; "never stopped" stays DEC-261's | DEC-261, DEC-1065 (1) |
| 79 | F8 | §3 machine, processes; Bad list (GPU) | limits derived from the machine, the dispatcher's watch and the restart classes marked "on this repository, by the CTO's tools; in the product through W2-20 / W2-121, not on the pin" | DEC-1030 (4), DEC-1031 (4), DEC-1037 (4), DEC-1057 (4), DEC-1097 (8) |
| 80 | F9 | Good list | "wrong claims unchanged" → "wrong claims 2 → 3" | DEC-1092 (1) |
| 81 | F10 | §3 VRAM | the reranker's 4.8 / 6.4 GB dated 2026-11-02, before the memory release | DEC-1043 (2), DEC-1068 |
| 82 | F11 | Bad list | G1's bursts 14.5–17.4 s; PAT-1's 13.4–13.9 s | (evidence G1, PAT-1) |
| 83 | F12 | §2 | sha256 from the registry for gitleaks, ccusage, Superpowers, bubblewrap and socat, replacing the "recorded at …" placeholders | (registry) |
| 84 | F13 | L4; §6 launcher | launch enforcement at the lift: a lead outside the approved batch or with unmet waits, any session while the gate is shut or limits would be passed; one recorded override | DEC-1088 (5) |
| 85 | F14 | status line | "every change" → "every decided change; descriptive updates cite their source" | DEC-1093 (3) |
| 86 | F15 | §3 store | the counts dated: D-4b's (W2-88 §1), not window 4's store | — |
| 87 | F16 | Good list | "every session" → "every unsandboxed session" (sandboxed wait for W2-127) | DEC-1064 (2) |
| 88 | F6, F17 | §9 | point 5 dropped (DEC-966 now marked); point 6 reframed; point 12 widened; a new point on §3 (below) | — |

**88 changes in all** (72 in the first pass, 16 from round 1). Unchanged: §5's product layout, most of §6 (roles,
owner, orchestrator scope, the oracle, EXP-002, discovery, the lesson loop, readiness), §7's table, and the Wave 1
consequences. L3, §6 and §7 now carry the "not re-audited" marker.

## 9. What no source settled (for the owner)
1. **Sections outside memory and the stack were not re-audited.** The draft now marks L3, §6 and §7 "not re-audited"
   (F2). L3, §6 and §7 still describe the product's
   enforcement as of Wave 1. On this repository DEC-953 lifted every Gov OS feature as a gate (the guard down to four
   rules, then five with DEC-954; the full guard's cases opt-in, DEC-1061 (3a)), the nightly is stopped (DEC-1049,
   DEC-1050), and Wave 2 adds the three layers and the ticket lead (DEC-1087 (13)). The features stay built in the
   product, so the ADR's product text may stand. The question left: should the ADR also state this repository's lifted
   regime, or leave it to DECISIONS-IN-FORCE?
2. **RAM and disk were not re-measured** on Wave 2's runtime. The draft keeps S0b2's figures, marked. Measure them
   (EXAMIN's per-index RSS is already W2-27's, DEC-735), or accept them as stated?
3. **The machine's figures** (20 CPUs, 24 GB WSL cap) are the orchestrator's record under DEC-1038, not a decision,
   and a RAM upgrade is planned. The draft states them as "today", with limits derived (DEC-1037 (4)).
4. **The search's speed target.** DEC-1065 (4) set "near the pin's ~1 s"; window 4 measures 1.24 s (E0) to 1.68 s
   (PAT-1) median alone. The draft states both and does not judge whether the target is met.
5. **DEC-966 (3)**: done since the first draft; DEC-966 now carries "Changed by: DEC-1087 (3)" (`3552f0f59bb7`).
   Kept only as a `gov links` note: DEC-963's status still names only DEC-966. No ADR matter.
6. **Mark DEC-261 as changed by DEC-1065 (1) / W2-32 S10.** DEC-261 decided "`gov` starts `ollama serve` on demand and
   never stops it". The pin starts none for a search, a rebuild, a close, a seed or the sandbox (W2-32 S10,
   `ollama.py`); only an explicit restart does. "Never stopped" still matches DEC-261. DEC-261 carries no "Changed by"
   mark (DEC-866), so the register and the ADR disagree until the owner marks it.
7. **The glossary** (DEC-1096) is decided and DEC-1097 (6) is open. E2G found a glossary at search-again lowered
   answers (122 against 128, p 0.031). The draft names it only as a revisit trigger.
8. **The content facets** (decisions, code, tests, history, why, lessons/failures, DEC-080) are kept as written.
   DEC-419 DP-8 left content facets with W1-36; the register does not say whether they run as parallel subagents today.
9. **L4's Wave 2 commands** `impact`, `readiness --generate` and `discover` are kept in Wave 2 (DEC-166). Their fates
   after D9-FATES (DEC-1083, DEC-1084) were not traced.
10. **W2-88 §1 is stale on one line.** It says "keyword and meaning routes, 30 each" and "20 chunks reranked". Window
    4 runs routes 60 deep and 40 reranked (`retrieval.yaml`, DEC-1075 (3), DEC-1089 (1)). The draft follows the
    pool. W2-88 §8 also says "wrong claims unchanged" where E2 has 2 → 3 (F9). The record needs fixing, but not in
    the ADR.
11. **The lift will make parts of the draft stale.** W2-136, W2-137 (64 texts), W2-138, W2-141, W2-142 and W2-145
    ("no private reranker beside the service", not yet built) are marked "at the lift's re-pin". Accept now
    and re-read at the lift, or accept after the lift?
12. **The query server's start wrapper** (`~/.local/bin/ollama`, DEC-1037 "recorded with it") is an interim. DEC-1037
    says its removal "stays tracked (the W2-20 / W2-121 KPI line, then its own small ACT)", but no ticket carries that
    line (the reviewer searched `.tickets/` twice; F17). It is a decided-but-not-done item for DECIDED-NOT-DONE as well
    as an ADR point. P-LB-PRODUCT-1 (DEC-1048 (3)) is folded into the three-layer plan (DEC-1097 (11)).
13. **Front matter.** `date` stays 2026-09-30, and no field records the refresh (the schema allows one). Add
    `version` or a date when the owner accepts?
14. **§3 and the Consequences describe the CTO's tools, not the product** (F8). The machine-derived limits
    (DEC-1037 (4)), the dispatcher's GPU and crash watch (DEC-1030) and the restart classes (DEC-1057 (4)) run on this
    repository through the CTO's tools. In the product they are KPI lines of W2-20 and W2-121, and none is on the pin;
    W2-20 is to be rebuilt before the lift (DEC-1097 (8)). The draft now marks each so. Should the ADR state them at
    all before W2-20 and W2-121 land, or move them to a "this repository" note?
15. **W2-145** (the product's "no private reranker beside the service", DEC-1097 (8)) is named in the draft from the
    coordinator's message; its ticket file was not found in `.tickets/` on this branch at drafting time.
