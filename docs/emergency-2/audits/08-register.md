# Audit 8: the decision register (EMERGENCY-2 §9 row 8)

Date: 2026-11-17 · Commit: `a246f72b2` (branch `w2/integrate`) · Read-only; the register was not edited.
Sources read: `docs/emergency-2/EMERGENCY-2.md` (v3), `docs/emergency-2/audits/BRIEF-COMMON.md`, `docs/DECISION_REGISTER.md` (1,206 entries, DEC-001 to DEC-1210, 15,612 lines, 2,152,085 bytes), `governance/project/path-map.yaml`, `governance/project/retrieval.yaml`, `governance/project/rebuild.yaml`, `src/gov/retrieval/{lexical,semantic,authority,chunking}.py`, `src/gov/store/loader.py`, `src/gov/check/{citations,pathmap}.py`, `src/gov/close/{command,history}.py`, `src/gov/config/loader.py`, `src/gov/plan/derive.py`, `src/gov/memaudit/tables.py`, `src/gov/doctor/command.py`, `docs/emergency-2/HANDOVER.md`.

Memory use: 2 `gov retrieve` calls. Both helped in part. The first surfaced the store's per-entry `status`/`changed_by`/`in_force` parse and INVESTIGATION-1 A2-7 on archiving the register. The second confirmed the `lexical_policy: not indexed` mechanism. Neither named the include rules directly; grep found those.

**Files:**
- `docs/emergency-2/audits/08-register.csv`: the full table, one row per decision. Columns: id, date, title, theme, class, by, items, reason, source (register line), step (`marks` = settled by code, `theme` = the theme pass, `theme+CTO-check` = corrected in my check of the kept list).
- `docs/emergency-2/audits/08-parse.py`: the parser (step 1). Run it as `python3 docs/emergency-2/audits/08-parse.py --out <file>`.

## Method

1. **Code first, on the change marks (`08-parse.py`).** The parser reads each `### DEC-n — title` entry: its Status line, the date, the entry's own `Changed by:` / `Superseded by:` / `Lifted by:` marks, and the marks other entries put on it (`Supersedes:`, `Replaces:`, `Changes:` ...).
   - It settles a decision as **history** only on a mark that is unambiguous:
     - S1: status SUPERSEDED, WITHDRAWN or REJECTED (16);
     - S2: status DONE, a one-off carried out (108);
     - S4: another entry's bare `Supersedes:` / `Replaces:` naming it with no item qualifier (4).
   - Any mark that names items, parts, a clause or a scope is treated as partial and settles nothing.
   - Result: **128 of 1,206 settled by code** (10.6 %). A further 337 carry partial marks. The marks are free text ("Changed by: DEC-1164 (12) (item (6): ...)"), so code alone could not settle more without guessing.
2. **By theme, in parallel.** The remaining 1,078 rows were given a keyword theme by code, then split into six groups. Six Sonnet subagents classed them, each given the common brief, the golden rule, EMERGENCY-2 and its rows. They re-themed rows where the keyword guess was wrong.
3. **My check of the kept list and the §2.9 names.** All seven decisions §2.9 names come out superseded by §2.9, or kept with that item superseded:
   - DEC-1205, DEC-820, DEC-313, DEC-1082 and DEC-1128: superseded;
   - DEC-1207 (2) and DEC-1203 (1): superseded items, the rest of each decision kept.

   I corrected six rows that EMERGENCY-2 itself cites as live but the theme pass had classed history:
   - DEC-1116: §4.4;
   - DEC-1183 (4), (5): §6.1;
   - DEC-1200: §6.1, §7.3;
   - DEC-1203 (3): W2-193, §6.1;
   - DEC-1206 (1): W2-194, §6.1;
   - DEC-1134: still read by `gov close`, through `accepted_reds` at `path-map.yaml:429-437`.

**Accuracy (estimate).** The theme pass judged most rows from a 700-character excerpt, and opened the full entry only where the class was unclear. In a random sample of 14 theme-pass rows, 13 were clearly right and 1 was arguable: DEC-1072 (2), whose standing item is carried by kept DEC-1176. Six corrections were needed in the kept check. My estimate is that 3 to 5 % of rows would change class on a full read, mostly between history and kept. The doubtful rows are listed under "The CTO decides".

## Counts per theme and class

| Theme | kept | superseded | retired | history | total |
|---|---|---|---|---|---|
| guard | 9 | 140 | 20 | 84 | 253 |
| memory | 26 | 6 | 2 | 83 | 117 |
| landing | 8 | 2 | 2 | 135 | 147 |
| tickets | 26 | 17 | 2 | 268 | 313 |
| runtime | 25 | 6 | 0 | 65 | 96 |
| releases | 5 | 1 | 0 | 21 | 27 |
| examin | 2 | 3 | 0 | 4 | 9 |
| records | 34 | 7 | 4 | 99 | 144 |
| other | 18 | 3 | 4 | 75 | 100 |
| **total** | **153** | **185** | **34** | **834** | **1206** |

## Groups for the owner's approval (F-9)

One row per theme × class. Approving a group approves every row the CSV gives it.

| # | Group (theme × class) | Count | What it holds | Approve |
|---|---|---|---|---|
| G01 | guard × kept | 9 | What survives the guard era: threat model (DEC-039), CI and the landing as the boundary (DEC-007), the owner's push and release (DEC-848, DEC-772), no scan on private Gov OS (DEC-1182 (1)), the owner's operator (DEC-1207 (6)), the role loading (DEC-826 (1)-(3)). | [ ] |
| G02 | guard × superseded | 140 | Guard rules and parser, sandbox, box, permission prompts and editing, held-out and install refusals (§2.2, §2.3); gitleaks scans (§2.11); the §2.9 list; ACTs and operator agent (§2.10, §2.6). | [ ] |
| G03 | guard × retired | 20 | Accepted residuals and hardening plans of the guard and sandbox, the operator agent's fix rounds and briefs, W2-42 and W2-186 work: their subject is gone. | [ ] |
| G04 | guard × history | 84 | ACTs applied, guard fixes shipped, one-off install and permission answers, DONE records, early decisions settled by DEC-058/064/842. | [ ] |
| G05 | memory × kept | 26 | Memory's standard (DEC-1097, DEC-1098), index design (DEC-016, DEC-017, DEC-091), retrieval method (DEC-030 to DEC-037, DEC-859, DEC-860), fresh 80 at 95 % (DEC-1210), no CPU fallback (DEC-1065), per-repository memory (DEC-1176). | [ ] |
| G06 | memory × superseded | 6 | `gov context` budgets and ceilings (§5.5); hit@5 pass lines, floors and targets (§5.2). | [ ] |
| G07 | memory × retired | 2 | Docling corpus ingestion and RAGFlow: never built, never needed. | [ ] |
| G08 | memory × history | 83 | Past measures, lens question rewrites, prototype rounds, W1-17 to W1-21 and W2-15a/W2-61 ticket choices, the standing-set regime replaced by DEC-1210. | [ ] |
| G09 | landing × kept | 8 | Only the test designer commits acceptance tests (DEC-906, G-1), the merge rules (DEC-912, DEC-918), final-block trailers (DEC-182), full suite only in the nightly (DEC-968), merge and close one step (DEC-989), the local merge queue (DEC-959). | [ ] |
| G10 | landing × superseded | 2 | A refused close as a repair ticket and a counted iteration (DEC-455, DEC-457: §4.2, §3.3). | [ ] |
| G11 | landing × retired | 2 | The pre-close gate and the record-widening rule, both lifted since DEC-953. | [ ] |
| G12 | landing × history | 135 | Past closes, merges, re-pin windows, close design points of W1-30 and W2-01/W2-53, the close pipeline DEC-953 lifted. | [ ] |
| G13 | tickets × kept | 26 | The golden rule (DEC-1204), DEC-1209, the rubric (DEC-1208, DEC-1120), profiles and readiness (DEC-005, DEC-085), test independence (DEC-069, DEC-430), orchestrator and lead layering (DEC-236), claims, `gov plan` (DEC-1088 less its closed-ticket rule). | [ ] |
| G14 | tickets × superseded | 17 | Per-ticket reviews, FULL probes after green, review-round counts (§3.6, §3.3); repair reopen (§4.2); ticket-type and readiness gap-ticket rules (§4.1, §4.6); ticket dispositions (§6.2). | [ ] |
| G15 | tickets × retired | 2 | The countdown progress line and the same-day mapping of CTO practices into tickets: ceremony with no subject left. | [ ] |
| G16 | tickets × history | 268 | Wave 1 and Wave 2 ticket packages, test-design DPs, KPI readings, rounds, scopes and closes; review rules merged into DEC-1204. | [ ] |
| G17 | runtime × kept | 25 | Checkpoints and hooks (DEC-264, DEC-279, DEC-444), full window (DEC-838), dispatcher (DEC-1007, DEC-1030), heavy slots and the nightly (DEC-979, DEC-984), dead-man (DEC-998), resource gate (DEC-898, DEC-1146), capacity rules (DEC-1157), `gov launch` interface (DEC-231, DEC-332). | [ ] |
| G18 | runtime × superseded | 6 | The morning package and pings (§6.2 A-2), the clean tree for the nightly (A-3), the launch allow rule (§2.3), the operator job runner as the agent-to-agent layer (§6.3). | [ ] |
| G19 | runtime × history | 65 | Past capacity plans, gate figures, trials and freezes, the emergency of 2 November, rules replaced by DEC-838, DEC-1157, DEC-1120. | [ ] |
| G20 | releases × kept | 5 | Copier distribution (DEC-023), signed tags and manifest as the root of trust (DEC-027), one agnostic Gov OS (DEC-060), the lock comparison (DEC-488). | [ ] |
| G21 | releases × superseded | 1 | "Full scope, built in waves, released once" (DEC-064): the lean release of §8.1. | [ ] |
| G22 | releases × history | 21 | Specific releases and re-pins (0.1.0, 0.1.1), the Rust archive decisions. | [ ] |
| G23 | examin × kept | 2 | One pilot adoption before Release 1 (DEC-740); EXAMIN's CTO leads Wave 0 (DEC-1199 (1)). | [ ] |
| G24 | examin × superseded | 3 | EXAMIN's adoption by tickets W2-27/28/29 and W2-19 (§7.2); W2-81's exit proof (§6.2 A-4). | [ ] |
| G25 | examin × history | 4 | The W2-81 adopter brief, Wave 2's ticket parking, the EXAMIN profile copy. | [ ] |
| G26 | records × kept | 34 | Record formats and schemas (DEC-012, DEC-227, DEC-274, DEC-305), rulesync and OpenSpec (DEC-011, DEC-022), doctor and the tool registry, the citations check (DEC-463, DEC-473, DEC-479), owner decisions recorded by the CTO (DEC-861), supersession propagates (DEC-866), templates with READY and DONE by code (DEC-1052, DEC-1116). | [ ] |
| G27 | records × superseded | 7 | Copy every rule to five places (DEC-851), the commit-all-context policy, the prompt's standing rules, the one-list DECISIONS-IN-FORCE (§11.1, §2.10); tagging the old register (§11.3); a rule broken twice becomes a mechanism (DEC-1012: §10.1). | [ ] |
| G28 | records × retired | 4 | The S1/S2 plan validator scoping, the placeholder scan, the five-line owner report block. | [ ] |
| G29 | records × history | 99 | Version-row and bootstrap decisions, delegated record choices, one-off record fixes, early provenance decisions settled by DEC-058. | [ ] |
| G30 | other × kept | 18 | Assemble first (DEC-001), governance is code (DEC-003), Claude Code as the harness (DEC-010), progressive adoption and A0-A11 (DEC-006, DEC-090), `gov discover` (DEC-166), impact and closure depths (DEC-167, DEC-815), the governance-share definition (DEC-086). | [ ] |
| G31 | other × superseded | 3 | Gitleaks configuration and caching rules (§2.11). | [ ] |
| G32 | other × retired | 4 | Serena, the local T1 model, the OTEL telemetry stack, separate test-execution and integration roles: never built. | [ ] |
| G33 | other × history | 75 | Early tool choices settled by DEC-074, Wave 1 self-adoption steps, the gitleaks lift settled by DEC-1182. | [ ] |

## The kept decisions: the new in-force list, by theme

"Items changed" names the items that do not survive, and why. The rest of each decision is in force. The source is the register line.

### guard (9)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-007 | Native harness features first; CI is the enforcement boundary | Hooks are guardrails and CI/landing is the enforcement boundary; consistent with §1.2, §3.1 |  | 75 |
| DEC-025 | Enforcement stack | Checkpoint hooks survive (§6.1); the guard, context and gitleaks lines are gone | PreToolUse guard superseded §2.2; SessionStart context superseded §5.5; gitleaks superseded §2.11; PreCompact/Stop checkpoint kept §6.1 | 213 |
| DEC-039 | Threat model: the Gov OS guards against mistakes and drift, not a same | Threat model restated by §3.1 (DEC-1204 (1)); the standing golden rule |  | 301 |
| DEC-087 | CI scope on the hosted runner | Hosted CI runs deterministic checks only; the gitleaks step contradicts §2.11 | gitleaks in CI superseded §2.11 | 797 |
| DEC-826 | P-S5: what each role loads, reads and writes | Role loaded at launch, test designer reads spec not implementation, reviewers commit nothing; read-denial and guard flag items go | (1),(2),(3) kept; (4),(5) superseded §2.2; (6),(7) history | 9031 |
| DEC-848 | Backups: the owner's own push of `w2/integrate` continues, at least da | Agents never push: the owner keeps git push (§2.4); backups moved to §2.8 | (1) kept §2.4; (2) backup now §2.8 hourly bundle | 9222 |
| DEC-1182 | Secret scanning and pushes: no repository scan on Gov OS; EXAMIN one f | No scan of private Gov OS stays (§2.11); EXAMIN weekly scan and the guard secret check go | (1) kept §2.11; (2) superseded §2.11; (3) superseded §2.2; (4) kept | 15161 |
| DEC-1203 | P-JOBS-USER-1 corrected to (B), live now as an exception until Wave 3; | §6.1 builds W2-193 on DEC-1203; only its box item (1) is named in §2.9 | (1) superseded §2.9 (the box); (3) F-028/F-030 product tickets (W2-193) kept §6.1; (2),(4) history; (5) merged into DEC-1204 | 15371 |
| DEC-1207 | yes ACT-GOLDEN-RULE-1 f9d67d5a; P-BOX-EXCEPTION-1 yes with F2 fixed, F | Fresh-80 measure rule (§5.3) and OWNER-OPERATOR-FULL-1 (§2.6) stay; the box and no-prompt order go | (1) history; (2) superseded §2.9; (3) kept §5.3; (4)(5) history; (6) kept §2.6 (operator), rest superseded §2.2 | 15419 |

### memory (26)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-014 | Code-structural memory: codebase-memory-mcp | Code graph tool is still memory's code route (DEC-1098 (2), DEC-859). |  | 118 |
| DEC-016 | Lexical + semantic index: SQLite FTS5 + sqlite-vec, fused with RRF | Index design (FTS5+sqlite-vec+RRF) still the memory index base of DEC-1097/1098 |  | 134 |
| DEC-017 | Embedding & reranking models | 0.6B embedder and reranker resident on the GPU are the standard of DEC-1098 (1); GPU never spills. |  | 140 |
| DEC-030 | Retrieval completeness principle | Batch size is not a completeness limit; paging and continuation still how gov retrieve works (DEC-860). |  | 235 |
| DEC-032 | Retrieval loop runs in a disposable context | Retrieval loop in a disposable subagent is still the retrieval skill's method. |  | 244 |
| DEC-033 | Deterministic worklist for closure facets | Deterministic id-closure worklist still in gov retrieve and the closure module. |  | 248 |
| DEC-034 | Stopping reasons (enumerated) | enumerated stopping reasons still used by closure and retrieval (src/gov/closure) | amended by DEC-080, DEC-396 | 252 |
| DEC-035 | Radius-scaled budgets and task-class facets | Radius-scaled rounds still in gov retrieve (ROUNDS_BY_RADIUS); numbers stay placeholders. |  | 262 |
| DEC-036 | Synthesis notes: derived + deterministic citation check | derived synthesis notes and deterministic citation check; src/gov/retrieval/synthesis.py exists | amended by DEC-080 | 273 |
| DEC-037 | Zero-result canaries on every index | Zero-result canaries still built (retrieval/canary.py); a miss marks the facet unavailable, never "no evidence". |  | 277 |
| DEC-091 | Hierarchical (parent-child) retrieval in Wave 1 | Parent-child chunks and parent expansion still in the index and bundle (DEC-1098 bundle widened to sections). |  | 835 |
| DEC-381 | W1-19 DP-6: a namespace that is not embedded never reaches the vectors | A namespace not embedded never reaches the vectors; fail-closed embedding rule still true. |  | 3872 |
| DEC-388 | W1-19 DP-8 and DP-9: an unknown `embedding_policy` is not embedded; hi | Unknown embedding_policy is read as not embedded (fail closed) still holds. | DP-9 (hit@5 method) history | 3951 |
| DEC-391 | W1-20 DP-1 to DP-7: the interface, the ids, the depth, the code facet  | gov closure interface and gaps still how closure retrieval is built (src/gov/closure) | amended by DEC-393, DEC-396 | 4020 |
| DEC-782 | A read command may write the query-vector cache, and only that, under  | A read command may write only the bounded query-vector cache; still in semantic.py. | (4) history | 8574 |
| DEC-836 | Memory used, not just built: keystone 4's exit (item 1e) | Briefs tell agents to use gov retrieve (section 5.4) stays. | (1) superseded §5.5; (3) history | 9121 |
| DEC-859 | The code graph: targeted traversal for questions, pages for whole-grap | Targeted traversal and paged whole-graph reads for the code graph are still design rules. |  | 9345 |
| DEC-860 | Context: never one giant query, never one giant context; retrieval in  | Batched, ranked, stacked retrieval and never one giant context still the principle. | (2) superseded §5.2/§5.3; (3) superseded §5.5 | 9354 |
| DEC-1065 | No CPU fallback for embeddings; search respects role separation; the f | No CPU fallback for embeddings (section 5.8); role_paths filter of search stays. | (3),(4) history | 13149 |
| DEC-1092 | E2 accepted: "search again once" a standing practice (a package); E3-E | Search again once as standing agent practice is part of the standard (DEC-1097). | (2) history | 13761 |
| DEC-1097 | The experiments decided: the fresh 80 judges window 4's configuration  | Its configuration (window 4 pin, pool, 6,000-token bundle, search again once) is the standard of §5.1. | (1)(a),(5) kept; (1)(d) superseded §5.2; (2) superseded §2.10; rest history | 13850 |
| DEC-1098 | The fresh 80 accepted and the measured configuration made Gov OS's mem | Standing item (1): the measured configuration is memory's standard (§5.1); (2) code graph stays. | (1),(2) kept; (4) superseded §2.2; (3),(5),(6) history | 13905 |
| DEC-1101 | Memory quality audited periodically with fresh questions, for Gov OS a | Periodic fresh-question memory audit survives as the weekly maintenance (§5.9) | 85 % bar superseded §5.3; hit@k reporting superseded §5.2 | 13970 |
| DEC-1176 | Memory for any repository is built, measured and maintained per reposi | Standing item (1): memory is built and proven per repository in its own Wave 0 at 95 percent. | (2)-(4) history | 15068 |
| DEC-1184 | The refresh accepted as changes-only (Q-REFRESH-1 (a)); EXAMIN's secre | Changes-only store refresh stays standing; EXAMIN scan line replaced by §2.11 | (1) kept; (2) superseded §2.11/§2.2; (3)-(6) history | 15183 |
| DEC-1210 | P-FRESH-80-1 (a) with A13 (b): every memory measure a fresh 80 measure | Standing fresh 80 end to end at 95 percent (section 5.3); hit@k only a diagnostic. | (4) superseded §5.2; (9) history; (5),(8) kept | 15453 |

### landing (8)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-182 | Commit trailers go in the final trailer block, with `git commit --trai | Final-block trailers via git commit --trailer; the landing still checks trailers |  | 1691 |
| DEC-906 | Only an independent test designer commits under tests/acceptance/ (sta | Only an independent test designer commits under tests/acceptance/ is the G-1 landing check; ratchet owner commits a judgement call | (1) kept; (2) history; (3) history | 10585 |
| DEC-912 | W1-01's merge rule passes a merge whose acceptance files equal git's o | Merge equal to git merge of parents passes the test-designer-only check; matches the landing check of who wrote tests | (1) kept; (2)-(4) history | 10744 |
| DEC-918 | Containment's merge rule matches DEC-912 exactly: a merge-back file eq | Merge-back file equal to git own merge is no change in the close gate; hook half retired | (1) landing check kept, live-hook part superseded §2.2; (3)-(4) history | 10846 |
| DEC-959 | The owner's decisions on ROLES-RESEARCH-1 and P-W2-H064: a local merge | Local merge queue run by the CTO tool and push stays owner own; QA per-ticket for core superseded | (1) kept; (2) kept; (3) superseded §3.6; (10) superseded §2.2; (4)-(9) history | 12007 |
| DEC-968 | The full suite once a day, in the nightly, and nowhere else; a close r | Full suite only in the nightly; close refused only by failure its change caused; matches §4.3 and A-1 | (4) history | 12129 |
| DEC-989 | The attribution baseline until a green nightly after ACT 1; a ticket's | A ticket merge and close are one step through the queue; matches closing at the land (§4.3 step 5) | (1) history | 12408 |
| DEC-1134 | The nightly's two warm-latency reds added to `accepted_reds`, named, u | gov close resolves accepted_reds decision ids in the register (path-map.yaml:429-437) | the two accepted_reds entries kept until W2-155 closes (A-4); rest history | 14529 |

### tickets (26)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-005 | Proportionality profiles keyed to impact radius | LITE/STANDARD/FULL profiles still the unit of ceremony and cost baselines (§10.2, §4.5) | (readiness reduction) history DEC-085 | 66 |
| DEC-069 | Test independence enforced mechanically | Only the independent test designer writes acceptance tests (§4.3, §6.1) | guard enforcement superseded §2.2; landing checks who wrote tests (§4.4) | 464 |
| DEC-085 | Readiness: profile → required cells; no defaulted N/A; spines close at | Readiness mandatory rows per profile still the readiness rule (W2-34 folds into W2-36) |  | 776 |
| DEC-103 | The order of specification work | Order of spec work (scenarios, data, tests, build) matches the spec-and-KPI pillar |  | 936 |
| DEC-105 | Evidence-triggered change | Three costed options on a contradiction with a closed spec still stand | CIT-P for kernel text superseded §3.5 | 953 |
| DEC-136 | Probe findings feed the independent suite | Review cases pass to the test designer as behaviours, never code; matches §4.2 test first |  | 1238 |
| DEC-220 | Delegated decisions | Delegated decisions for the orchestrator remain how packages are settled without the owner | guard, containment and install exclusions superseded §2.2 | 2058 |
| DEC-221 | Tests are proportional to the ticket's profile | Tests proportional to profile; not contradicted by §4.3 |  | 2072 |
| DEC-236 | Two-level orchestration: the main orchestrator and a ticket lead per t | Orchestrator plus ticket lead per ticket still the layering (§4.3 senior engineer, leads) |  | 2258 |
| DEC-292 | W1-09 DP-2: the claim convention | Claim lock convention .tickets/.claims remains the claim mechanism |  | 2903 |
| DEC-300 | W1-09: the acceptance tests folder must lie below `tests/acceptance/` | READY needs a real folder strictly under tests/acceptance; READY by code (§4.4) |  | 2990 |
| DEC-430 | The owner's reading of MR-3 (MWA-02) | Core tests by test designer first, later cases red first by designer only (§4.2, §4.3) |  | 4646 |
| DEC-454 | What `gov close` measures where its KPI lines left the mechanism open | gov close still measures regression tests on the tree; repair tickets go | repair ticket and disposition arguments superseded §4.2 | 4964 |
| DEC-732 | In a ticket worktree, tests and gov commands run that worktree's own ` | Tests and gov commands in a worktree run that worktree's own src; worktrees remain |  | 7804 |
| DEC-803 | A risk that exists only when a feature is on is an entry criterion of  | Risk present only when a feature is on is an entry criterion of the ticket enabling it |  | 8781 |
| DEC-953 | The owner's decision on AUDIT-GOV-FEATURES-1: the Gov OS is built and  | Nightly plain run (3), scoped test selection (4) and three-layer orchestration (8) still stand | (1) 10-practice close with FULL review and gitleaks superseded §3.6, §2.11; (2) guard four rules superseded §2.2; (5),(6),(7),(9),(10) history | 11861 |
| DEC-963 | P-PARALLEL-1 (b), amended: the test designer in its own worktree, retr | Test designer in its own worktree retrieving from integration store; separation by construction (§1.2) |  | 12071 |
| DEC-1047 | The emergency raised one level: everything stopped but the memory infr | The aim (stops drift, tests and code matching KPIs green) is §1.1, kept by DEC-1158 | (1)(2) history DEC-1158 | 12981 |
| DEC-1088 | Dependency mapping decided: `gov plan` (W2-136), the template's `reads | gov plan and reads/needs/waits_on dependency mapping built; the closed-ticket rule no longer holds for fixes | closed tickets never edited superseded §4.2 | 13673 |
| DEC-1120 | RUBRIC-2: the owner's rubric of model and effort by role and criticali | Rubric of model and effort by role and class; RT-8 and §6.3 cite it |  | 14268 |
| DEC-1183 | W2-88's Route X for release 0.1.0 tonight (S27 dropped from this run,  | §6.1 keeps checkpoints and the full window on DEC-1183 | (4) full window and (5) every new lesson to memory at once kept; (1)-(3) history | 15172 |
| DEC-1200 | P-EXAMIN-LEAD-1 (a), (b), (c): the EXAMIN CTO's Wave 0 brief 0d96110c  | §6.1 finishes W2-192 on DEC-1200; the Wave 0 brief governs §7.3 | (1) EXAMIN CTO Wave 0 brief kept §7.3; stage AS standard and W2-192 kept §6.1; session and channel items history | 15338 |
| DEC-1204 | How work is judged: one golden rule (merges ADR-0001 / DEC-039, DEC-80 | Golden rule: threat model, what may block, two rounds, READY by code (§3.1-3.3) | (3) review trigger narrowed by §3.4; (5)(6) judging-work trimmed §3.7 | 15382 |
| DEC-1206 | W2-194 keeps F-031; W2-15a closed on the walled run's record under Q2  | §6.1 builds W2-194 on DEC-1206 | (1) W2-194 keeps F-031 kept; rest history | 15409 |
| DEC-1208 | A work-sizing rubric: the ticket W2-196 approved (FULL, Wave 2, in par | Provisional rubric Q/L/S/F kept for features where §4.1/§4.2 do not differ (§4.5) | (1) history DEC-1209; (2) class-rules and operator gates superseded §2.10 | 15431 |
| DEC-1209 | EMERGENCY: break the cycle that is stalling the work: no new tickets ( | EMERGENCY declaration stays in force until the owner lifts it (§11.4) |  | 15440 |

### runtime (25)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-231 | W1-46 DP-1: the command line of `gov launch` | gov launch <role> <ticket> -- args is the launcher interface and stays when rebuilt without guard |  | 2203 |
| DEC-264 | The PreCompact hook never blocks; it appends a generated state block | PreCompact never blocks, appends a generated state block; checkpoint hooks kept (§6.1, DEC-1183) |  | 2593 |
| DEC-279 | W1-25 DP-2: the checkpoint's schema, keys and arguments | Checkpoint record schema and keys; checkpoints and RT-5 resume rely on it |  | 2759 |
| DEC-282 | W1-25 DP-6: the resume brief, the family check, and one real session | gov checkpoint --resume brief from the latest checkpoint exists; checkpoints kept in §6.1, RT-5 | real-session test and family check history | 2789 |
| DEC-332 | W1-46 DP-17: `gov launch` ends with the session's exit code | gov launch ends with the child exit code; launcher interface stays when rebuilt |  | 3312 |
| DEC-420 | An authentication or access error stops the launching of leads: `AUTH_ | AUTH_REQUIRED: stop launching leads on 401/403 and tell the owner; an ordinary-failure rule the run-time tool needs |  | 4534 |
| DEC-444 | The hooks' automatic checkpoints go to the ignored scratch folder; del | Automatic hook checkpoints go to ignored scratch, deliberate gov checkpoint records to docs/checkpoints; checkpoints kept |  | 4870 |
| DEC-728 | `~/gov-os-runs/` is one durable scratch root; a session writes only in | The ~/gov-os-runs scratch root is a run folder (§2.3); the fence is not enforced | (2) own-folder write fence superseded §2.2 | 7741 |
| DEC-837 | Resume in full, pulled forward into keystone 3: ticket W2-62 (item 1f) | session-start hook loads RESUME HERE in full and a checkpoint at every handover; §6.1 keeps the checkpoint hooks, RT-5 | (4) history | 9129 |
| DEC-838 | Context windows: every session uses its model's full window; usage is  | Every session uses the full window, no compaction threshold; matches §6.1 (full window, checkpoint and handover) |  | 9137 |
| DEC-898 | The resource gate checks free disk space and free inodes; every audito | Resource gate checks free disk and inodes; the landing and machine protection need it (§4.4) |  | 10277 |
| DEC-902 | The weekly sweep, a standing rule; the cleanup of 2026-10-23; the owne | Weekly sweep of /tmp and run folders is standing hygiene that protects the disk | (1) kept; cleanup of 2026-10-23 and commits history | 10417 |
| DEC-933 | P-REPIN-2 (a): each judge improvement re-pinned as it lands; the night | Nightly full run every night for Gov OS and products is kept by A-1 | (1) history; (2) kept except clean-tree/stable-head start conditions superseded §6.2 A-3, times per DEC-973; (3) history | 11257 |
| DEC-961 | The machine is shared by capacity alone: no memory set aside for full  | Machine shared by capacity alone with no extra holds; consistent with A-1 slots and mem_guard | (1)-(2) kept; (3) changed by DEC-984; (4) history | 12039 |
| DEC-972 | P-PING-1 (a) plus (d): a ping that does not stop the CTO; none at nigh | Non-blocking owner ping via ping_log and PushNotification keeps work going; consistent with §2.1 | (2) quiet hours changed by DEC-973; (3) superseded §2.3; (4) history | 12189 |
| DEC-973 | The quiet hours 02:00 to 07:30; the nightly at 04:00; its check at 08: | Nightly at 04:00 and 08:00 check still in the crontab; 09:00 package folds into daily digest | (1) quiet hours kept, not for lead-stopping decisions (DEC-1157); (2) kept; (3)-(4) history | 12202 |
| DEC-979 | The owner's decisions on CAPACITY-1, the stores, batch closes and the  | Machine-wide heavy slots kept until the run-time tool replaces them (A-1) | D1 heavy-job slots and D3 tools lane kept; D2,D4-D6,(2)-(5) history | 12282 |
| DEC-984 | The nightly takes all three heavy-job slots while its suites run (stan | Nightly takes all three heavy slots while its suites run; nightly and heavy slots kept (A-1) |  | 12355 |
| DEC-998 | The dead-man's switch through the Claude app alone; Remote Control che | Dead-man push through the Claude app only; dead-man kept until run-time tool replaces it (A-1) |  | 12517 |
| DEC-1007 | The dispatcher: keeping the machine full and the work moving never dep | Dispatcher as plain program with no AI outside sessions; dispatcher kept then rebuilt as run-time tool (§6.1) |  | 12608 |
| DEC-1030 | The dispatcher watches the whole machine: the GPU, its holders, each m | Dispatcher watches GPU, holders and model layers; supports RT-4 zero GPU spill |  | 12816 |
| DEC-1031 | The load-balancing plan now, with its target architecture; no reranker | GPU budget (embedder first, nothing pushes it off) still holds; shared GPU services. | (1) CPU-fallback clause superseded §5.8; (2)-(4) history | 12825 |
| DEC-1032 | P1-LOAD-BALANCE-1 decided; a freeze until the machine runs at normal s | Query embedder may run on the GPU and the GPU budget stay; freeze and sprint were temporary. | (2),(3) history | 12833 |
| DEC-1146 | A resource gate's refusal is a wait, not a refusal under the two-refus | A resource gate refusal is a wait; slots and gates stay (§6.2 A-1, RT-1) | permission-refusal clause superseded §2.2 | 14744 |
| DEC-1157 | Every rule that holds or delays a lead removed tonight, except what pr | Removes lead-delaying rules, keeps memory floor, mem_guard and spend brake; fits RT-1 and A-1 | (14) guard refusals, review rounds, kernel gate superseded §2.2/§3.4/§3.5; (15),(16) history | 14863 |

### releases (5)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-023 | Distribution: Copier (`gov init` / `gov update`) | Copier template distribution with tags as releases; copier.yml still in the repo, gov update builds on it |  | 200 |
| DEC-027 | Root of trust (solo scope) | Signed tags plus hash manifest as root of trust; releases stay the owner own (§2.5) |  | 227 |
| DEC-060 | One agnostic Gov OS; projects differ only by overlay configuration | One agnostic Gov OS release line; projects differ only by overlay configuration |  | 421 |
| DEC-488 | W1-39: one comparison of a project with its lock, owned by W1-39; the  | one project-versus-lock comparison (src/gov/lock) used by doctor and gov update; still true |  | 5334 |
| DEC-772 | `gov release` is the owner's alone, from a plain terminal; the guard r | gov release stays owner-only from a plain terminal (§2.5); the guard row is gone | (1) kept §2.5; (2) guard prefix refusal superseded §2.2; (3) history | 8445 |

### examin (2)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-740 | Charter v5 §1: one pilot adoption in Wave 2, before Release 1 | Charter v5 amended: one pilot adoption before Release 1; consistent with EXAMIN Wave 0 (§7.1) |  | 7980 |
| DEC-1199 | EXAMIN's CTO leads EXAMIN's Wave 0 (the Gov OS CTO on Gov OS only); F- | EXAMIN CTO leads Wave 0 and Gov OS CTO Gov OS only match §7.2/§7.3; operator, box and guard items go | (1) roles kept, refactor tickets read as direct work §7.2; (3),(4),(5) superseded §2.6/§2.2; (2) history | 15327 |

### records (34)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-003 | Governance is code, not prose | Governance as deterministic code and short agent text still matches §2.1 and §1.2 | (compiled context packet) superseded §5.5 | 55 |
| DEC-011 | Specification & change control: OpenSpec | OpenSpec still owns spec truth; openspec skills in use |  | 94 |
| DEC-012 | Decisions: ADR markdown with frontmatter in git | ADR files with frontmatter remain the decision record format |  | 103 |
| DEC-022 | Provider adapters: rulesync | rulesync single source with generated adapters still in the tree (.rulesync/, template/.rulesync/) |  | 195 |
| DEC-024 | Method skills: Superpowers, selectively | Selected Superpowers skills still shipped; per-ticket review part contradicts no-reviewer rule | two-stage review in subagent-driven dev superseded §3.6 | 207 |
| DEC-065 | Master rules (constitutional, every session, every Gov OS) | Constitutional master rules match the aim (§1.1), roles apart through landing and templates (§1.2) and flow §4.3 | MR-1..MR-6 | 442 |
| DEC-066 | Organisation layer and the five distinct functions | Roles as rulesync-generated subagent definitions remain how roles are defined | guard-enforced allowed paths superseded §2.2 | 452 |
| DEC-093 | Decision packages: at most five at a time; P1 may bypass the cap | Decision packages ranked and capped per message; not contradicted, §9.1 A-9 batches to the owner |  | 846 |
| DEC-102 | Experiments are part of discovery | Experiments as discovery with an evidence record still the research role's method |  | 927 |
| DEC-127 | Where the tool-registry schema and the registry live | tool-registry schema in kernel, registry at governance/project/tool-registry.yaml: still true of the tree |  | 1158 |
| DEC-185 | KD-1: every `gov` command loads the `governance/project/` files it kno | Every gov command loads governance/project files, invalid file gives CONFIG_INVALID; path map still how roles stay apart |  | 1724 |
| DEC-199 | W1-06 DP-5: the sha256 of a vendored folder is a digest of its committ | vendored folder digest rule; vendored.yaml and gov doctor still use it |  | 1846 |
| DEC-227 | W1-08 DP-6: one shared definitions file holds every id grammar | one shared id-grammar definitions file (common.schema.json) still the schema design |  | 2133 |
| DEC-262 | The owner's reading of CAP-24 for vendored skills | owner reading of CAP-24 for vendored skills still applies (vendored.yaml version) |  | 2577 |
| DEC-274 | W1-10 DP-1: what a record is, and what an invalid one does to a load | definition of a record (frontmatter id, type, status) is how the record store loads; still true |  | 2707 |
| DEC-305 | W1-12 DP-4: the readiness record is YAML | readiness.yaml record shape with 26 rows; readiness is the spec-and-KPI pillar (W2-36 fold) |  | 3033 |
| DEC-328 | W1-34 DP-1: a gate record holds its state in `status` alone | decision package holds its state in status alone; schema mapping still in the template |  | 3237 |
| DEC-329 | W1-11 DP-1: the decision checker reads frontmatter and git, never pros | Decision checker reads frontmatter and git, never prose: a deterministic-code design choice still true |  | 3256 |
| DEC-448 | `gov doctor`: registered tool locations, historical records, one rebui | gov doctor checks tools at registered locations; the rule stands, only its limit was replaced | (one-off limit) history, superseded by DEC-477 | 4900 |
| DEC-452 | Doctor looks under every registered PATH prefix before PATH, and a too | doctor looks under registry PATH prefixes first, unverifiable tool fails; still true of doctor |  | 4943 |
| DEC-462 | A designer's brief states behaviour and sources only | designer brief states behaviour and sources only; keeps roles apart by brief (§1.2) |  | 5081 |
| DEC-463 | Decisions recorded late are accepted; from now on the record comes fir | record decision before change and gov check flags unrecorded citations; allied to §10.1 basis line; doubtful with the register archive | (1) history | 5086 |
| DEC-468 | The six skills OpenSpec writes beside its commands are registered rule | OpenSpec skills and commands are registered rulesync sources unchanged; still how adapters are built |  | 5142 |
| DEC-469 | The change that moves the registered OpenSpec or rulesync version refr | change that moves openspec/rulesync version refreshes sources in a temp folder; still a sound maintenance rule |  | 5149 |
| DEC-473 | The decision-citations check knows both register forms (W1-26, package | citations check reads a register file named in configuration with ### DEC-<digits> grammar; check still wired |  | 5195 |
| DEC-479 | The register file and the base commit of the decision-citations check  | path-map keys decision_register and decision_citations_base exist in the path map; will need repoint at archive |  | 5241 |
| DEC-818 | The P1 decision package format, and the daily P2 digest (standing) | P2 items go in one daily digest, consistent with §4.6 digest and A-9; six-part package format dropped | (1) retired as ceremony; (3) history | 8938 |
| DEC-832 | The Charter's eight unplanned roles: four as skill packs the engineer  | backend, data, integration/API and security as skill packs, not roles; skills exist in template kernel (DEC-957) | (2) history | 9091 |
| DEC-850 | How questions reach the owner (standing) | Six-part package format and leads never asking the owner directly still stand | (1) end-of-turn question line history DEC-855 | 9236 |
| DEC-861 | The orchestrator commits the records of the owner's decisions; the own | orchestrator records owner decisions, push stays the owner's (§2.4); kept for the A-11 approval record (§11.5) | (1)(2) amended by DEC-1057; (5) history | 9372 |
| DEC-866 | Supersession propagates (standing) | Supersession propagates: mark the old entry, sweep, update; the audit-8 archive follows it |  | 9439 |
| DEC-943 | Brief gaps in every lead's return, fixed the same week; the orchestrat | brief gaps section in every lead return fixes briefs and templates (§1.2); orchestrator gov context use is off | (1) kept; (2) superseded §5.5 | 11610 |
| DEC-1052 | P1-LIFT-1 and P1-PLAN decided: the basis, the rows, the templates with | basis line and READY/DONE computed by code from templates (DEC-1052; DEC-1116) still in §4.4 and A-4 | (templates/READY and DONE by code, basis, path-map roles) kept; suite cut, homes, plan, restart history; ACT rule superseded §2.10 | 13024 |
| DEC-1116 | W2-128's kernel templates approved at 1bf23a0b3e77 and promoted as ver | §4.4 cites DEC-1116 for the templates with READY and DONE by code | (1) kernel templates 1.0.0 kept as the baseline; ACT-CLAUDE-COPIES-2 superseded §2.10 | 14197 |

### other (18)

| Id | Title | In force, in one line | Items changed | Source |
|---|---|---|---|---|
| DEC-001 | Assemble first; Rust kernel becomes the later replacement | assemble tools behind a stable gov CLI in Python first; still true of the tree |  | 43 |
| DEC-006 | Progressive adoption | Progressive adoption (governable day one, A1-A11 in background) is still the gov adopt design (§7.2) |  | 71 |
| DEC-010 | Agent harness | Claude Code as the primary harness is still the product fact; no change in EMERGENCY-2 |  | 87 |
| DEC-040 | The Gov OS never executes install commands; tools are installed by the | Gov OS runs no install command of its own and tools stay pinned in the registry; not contradicted | owner approval per tool (DEC-083) superseded §2.3 | 307 |
| DEC-050 | Workstation hygiene | Standing workstation hygiene (gitignore worktrees, VHD compaction) still true and harmless |  | 356 |
| DEC-074 | S0b2 decisions and the owner's answers (2026-09-30) | chosen stack R1, C1, T3 (FTS5, sqlite-vec, Qwen3, codebase-memory-mcp, ticket) in the registry; hit@5 figures not targets |  | 488 |
| DEC-086 | Governance share: definition and Wave 1 measurement | Governance-token definition is the Contract CAP-04.b counter that A-7 keeps until the counter exists. |  | 788 |
| DEC-090 | The adoption transaction A0–A11 in Contract v4 | Adoption transaction A0-A11 with evidence per stage is the gov adopt design that EXAMIN uses (§7.2) | Wave 1 lite split history (DEC-741) | 827 |
| DEC-165 | The upstream lesson loop, in a lite form (Wave 3) | Wave 3 lite upstream lesson loop design still open | gitleaks scan of lesson packets superseded §2.11 | 1512 |
| DEC-166 | `gov discover`, the entry point to discovery (Wave 2) | gov discover is the discovery entry point; W2-36 build item in §6.1 |  | 1527 |
| DEC-167 | "What's the impact of X?" triggers the impact assessment | Impact assessment by gov impact is a product feature still built and used by test selection |  | 1533 |
| DEC-186 | KD-2: check declarations are YAML in the kernel template; `gov check - | check declarations as kernel YAML files, still how checks are declared (template/governance/kernel/checks/) |  | 1732 |
| DEC-205 | Headless workers start with the absolute path `~/.local/bin/claude` | Headless workers start with the absolute claude path; a launcher fact still true |  | 1900 |
| DEC-225 | W1-08 DP-2: namespace paths and memory class | Namespace paths and memory_class (governance/product) are the path map schema, still true. |  | 2107 |
| DEC-438 | W1-26: a family with no registered check is never green | family with no registered check is YELLOW, never green; fail-open guard present in src/gov/check |  | 4776 |
| DEC-815 | The closure depths per radius for Wave 2: 1, 3 and 8 hops (P-W2-45 (a) | Closure depths per radius (1, 3, 8 hops) are the product setting behind gov closure and gov impact |  | 8913 |
| DEC-1158 | The emergency of 2026-11-02 lifted, with its freeze; its spent items m | Lifts the 2 November emergency; (3) keeps the GPU budget and no-spill rule cited in §6.3 | (1),(2),(4) history; (3) kept | 14885 |
| DEC-1170 | The gitleaks scan stays off on this repository: a private, local devel | Gitleaks stays off on this private local repository; consistent with §2.11 |  | 15017 |


## Archiving the old register read-only and keeping it out of memory's index (§11.3)

**Where the include rules are.** They are not in `governance/project/retrieval.yaml`, which holds only query-time settings (`routing`, `pool`). They are in the path map and the index code:
- **Keyword index.** It takes every tracked file through `gov.secrets.indexable`. There is no include list (`src/gov/retrieval/lexical.py:6-8`). A file is kept out when its namespace says `lexical_policy: not indexed` (`lexical.py:154` `kept_out`; validated at `src/gov/config/loader.py:51, :140-149`).
- **Vectors.** They are built only from files whose namespace says `embedding_policy: embedded` (`src/gov/retrieval/semantic.py:4-5, :77`).
- **The register's current place.** `docs/DECISION_REGISTER.md` falls under the namespace `docs`, by the pattern `"docs/*"` at `path-map.yaml:51`, which is `embedded` and indexed.
- **A model to copy.** The existing namespace `evaluation-sources` (`path-map.yaml:107-120`) is kept out of both indexes this way.
- **One namespace per path.** Every tracked path must sit in exactly one namespace (`src/gov/check/pathmap.py:1`). `docs/*` does not reach subfolders, so `docs/archive/**` needs its own namespace.
- **Register entries become store records.** This happens only for the file the path map names under `decision_register` (`path-map.yaml:390`; `src/gov/store/loader.py:13, :54`).

**What else reads the register path.**
- Through the `decision_register` key:
  - `src/gov/check/citations.py:21` (with `decision_citations_base`, `path-map.yaml:391`);
  - `src/gov/util/register.py`;
  - `src/gov/retrieval/authority.py:32`;
  - `src/gov/retrieval/chunking.py:244`;
  - `src/gov/retrieval/lexical.py:331`;
  - `src/gov/close/history.py:20`;
  - `src/gov/close/command.py:52`, which resolves `accepted_reds` decision ids. Today that is DEC-1134.
- Hard-coded:
  - `src/gov/plan/derive.py:38`;
  - `src/gov/memaudit/tables.py:13`, the fresh-80 writers' "decisions" domain;
  - `src/gov/doctor/command.py:50` (`HISTORICAL_PATHS`).

**The change (proposed; one commit by the CTO after the owner approves the groups):**
1. `git mv docs/DECISION_REGISTER.md docs/archive/DECISION_REGISTER-2026-11-17.md`, and add a first line saying the file is archived and read-only, and naming this audit and the commit.
2. Start a new `docs/DECISION_REGISTER.md`:
   - the 153 kept entries copied verbatim, with their ids and headings, so the store, `gov close`, the citations check and memory read them unchanged;
   - each with one added line naming the items this audit marks changed (the CSV's `items`);
   - one new entry recording the owner's approval of EMERGENCY-2 (A-11) and of these groups.

   New ids continue from DEC-1211.
3. `path-map.yaml`: add a namespace `archive` with `paths: ["docs/archive/**"]`, `embedding_policy: not embedded` and `lexical_policy: not indexed`; its other fields as `evaluation-sources` has them. `decision_register` stays `docs/DECISION_REGISTER.md`, now the new file.
4. Add `docs/archive/DECISION_REGISTER-2026-11-17.md` to `doctor`'s `HISTORICAL_PATHS`. `derive.py` and `memaudit/tables.py` keep the live path, which is right.
5. **Read-only.** Git cannot make a tracked file read-only (it records only the executable bit), so the carrier must be code. Two choices:
   - (a) the deterministic landing refuses any commit that changes `docs/archive/**` (one path rule);
   - (b) the header line only.
6. **Citations check.** Commits after the base are judged against their own tree's register. Once the register is archived, a new commit that cites an archived id is a finding. Either move `decision_citations_base` to the archive commit and accept that nudge (cite the archive by path), or teach the check to read the archive too (a small code change).
7. `gov rebuild`. The path map is one of the keyword filter's judges (`lexical.py:70`), so the archived file loses its chunks and vectors in the next rebuild. Then confirm with `gov retrieve` that an id found only in the archive returns no `docs/archive/` chunk, and that a kept id still resolves.

## Findings the table cannot say

- **The marks settle little.** Only 128 decisions (10.6 %) are settled by unambiguous marks. 834 end as history overall, mostly ticket-level one-offs (W1/W2 packages, rounds, closes), which no mark records as spent. A register that records only owner decisions and standing rules (INVESTIGATION-1 A2-7, R-8) would have kept these out.
- **Kept decisions are often partial.** 74 of the 153 kept rows carry changed items. The new register should carry the items note on each, or an agent will read a superseded item as live. That is DEC-1072's drift concern.
- **A dependency on guard code.** In passing, the group-C subagent reports that `gov close` calls `gov.guard.containment.judge_commits`, and that `src/gov/decisions/checker.py` imports `gov.guard.containment_merge`. Retiring the guard's code (§6.1) must keep those modules or move them. I did not verify this myself.
- **Order with the fresh 80.** JOB-20261116-17, the first fresh 80, is queued and not run (`HANDOVER.md:51`). Its writers draw a "decisions" domain from the register (`memaudit/tables.py:13`). If the archive lands first, the questions are written on the new register.

## Decisions for the owner

1. **Approve the register's classes by group (F-9)?** The 33 groups G01-G33 are above; every row is in `08-register.csv`.
   - (a) Approve all 33 groups as listed. Cost: a few minutes. The CTO settles the doubtful rows below inside the groups.
   - (b) Approve the superseded, retired and history groups, and read the 9 kept groups (153 rows) before approving. Cost: about 30 to 45 minutes (estimate).
   - (c) Approve group by group with changes. Cost: an hour or more, and a second pass by the CTO.

   **Recommendation: (a).** The kept list is the new in-force list and stays open to change by ordinary decisions. Errors are estimated at 3 to 5 %, and caught by friction.

## The CTO decides

- **New register form:** 153 kept entries verbatim, with an items note, plus the approval entry (step 2). Recommended over a one-line digest, which would need code changes in the store, `gov close` and the citations check.
- **The `archive` namespace in the path map** (step 3), and the `HISTORICAL_PATHS` line (step 4). Recommended as written.
- **The read-only carrier:** recommend (a), the landing's path rule on `docs/archive/**`. It fits "the landing as deterministic code" (§2.1).
- **The citations check:** recommend moving `decision_citations_base` to the archive commit. An archived id cited in a new commit is then a finding that points to the archive. No code change is needed.
- **Order:** recommend archive and rebuild before JOB-20261116-17 writes its questions, so the fresh 80 measures the memory that will ship.
- **DEC-1134:** carry it in the new register until W2-155 closes (A-4), because `gov close` resolves it from `accepted_reds`. Then drop it.
- **Doubtful rows to settle inside the groups.** The subagents and I flagged these, one of each pair being arguable:
  - freeze rows: DEC-109, 409 and 429 (superseded) against DEC-365, 378 and 404 (history);
  - DEC-075, 494, 999, 1135;
  - memory: DEC-947, 086, 225, 1096, 1179, 497;
  - landing and runtime: DEC-906 (its ratchet item), 938, 948, 972, 973, 372, 527, 760, 905, 1117, 1149;
  - tickets: DEC-089, 093, 104, 236, 454, 878, 944, 949, 963, 995, 1003;
  - DEC-031, 826, 1199;
  - records: DEC-328, 463, 473, 479, 818, 837, 861.

  DEC-837 should probably move to superseded by §11.1, since RESUME HERE is archived. Recommendation: the CTO reads these 48 entries in full (about an hour, estimate) before writing the new register.
