# Integration step: the 162 older decisions in force, classed in HELD's key (DEC-1252 DE-2 (a), plan item 5-21)

`docs/emergency-2/integration/DECISIONS-HELD-2.md` · research (Sonnet, high), read-only · 2026-11-26 · code read at `w2/integrate` `9ad3efdf3` · **a proposal for the CTO's one commit on the register**; the register is not edited here.

**Count: 162 rows, 162 distinct ids** (153 up to DEC-1208 and the 9 of DEC-1239 to DEC-1247, equal to `gov decisions in-force` at this commit; DEC-1209 to DEC-1238 are HELD's, DEC-1248 to DEC-1253 are the CTO's by hand, C10). Checked by script, with every cited `path:line` resolving to a non-blank line.

## How the rows were made

- **Memory first:** two `gov retrieve` calls on the integration store, each read whole; then the 162 register entries read whole by id, DEC-1248 to DEC-1253, EMERGENCY-2 with §13, audit 4 §1.7, HELD's key and rows. Code was then read line by line or by targeted search. No test was run; no helper was used; no hidden question-set root was opened.
- **Class:** HELD's key (P, P\*, O, A, T, X, N, H); a decision takes the class of its **weakest live item**, and the strongest holder is named as "strongest". Items the register's `Class:` note or a later decision supersedes are not live. **P** here means the whole live decision is done or refused by code on a path today's sessions or adopted repositories take (`gov retrieve`, `gov rebuild`, `gov checkpoint`, `gov pause`, `gov release`, `gov adopt`, the installed hooks, the settings denies). Code only in `gov launch`, `gov queue`, `gov brief`, `gov close` or the unscheduled nightly is **O**.
- **Enforced-by** (proposed): P → `code` (with the cited `path:line` or check id); A, T → `checked-after`; O, X, N → `judgement` (an O row's code is not on the path, so it must stay in agents' reading; re-class it when the path takes it); H → none, mark it DONE instead.
- **Spent** is `yes` only where every live item is superseded or done and a line shows it. Where a decision looks largely overtaken but an item still asks, it stays `no` and is listed as a candidate.
- **Leaves the digest:** H, or P with a resolving `path:line`.
- **Limits:** X and N say that code does **not** hold something; that rests on the register entry, the carrier line cited and targeted searches, not on reading all of `src/`. Rows where a claim has no line read are marked **not verified**. A path under `main-tree:` is an ignored scratch file read in the main tree, not at the commit; the crontab was read on 2026-11-26.

## The 162 rows

| Decision | Class | Held by; notes | Enforced-by | Affects | Spent | Leaves digest |
|---|---|---|---|---|---|---|
| DEC-001 | X | register only; strongest P `src/gov/cli/main.py:93` (the stable `gov` command table). **not verified:** no code search for the 'assemble first, Rust later' principle. | `judgement` | `src/gov/cli/**` | no | no |
| DEC-003 | X | `template/governance/kernel/checks/core-schema.yaml:1` is the compiled form; no check holds 'agents read no framework' or the AGENTS.md size. Item 'compiled context packet' superseded (EMERGENCY-2 §5.5). Audit 4 §1.7: AGENTS.md size unchecked. | `judgement` | W11, W16; `template/governance/kernel/checks/**` | no | no |
| DEC-005 | X | strongest T `src/gov/readiness/checker.py:139` (profile decides required rows). Human gate per profile is text. Readiness reduction is DEC-085's. | `judgement` | W7; `src/gov/readiness/**` | no | no |
| DEC-006 | N | `src/gov/doctor/command.py:781` labels ADOPTED_HEALTHY from path-map systems, not from A11; strongest P `src/gov/adopt/stages.py:570`. The A0-A11 verdict stage is not built (`src/gov/adopt/lite_gates.py:30` ends at A10). | `judgement` | W1; `src/gov/adopt/**` | no | no |
| DEC-007 | X | register; `.github/workflows/ci.yml` is manual. CI/lefthook half retired by DEC-1242 T-9 (not yet applied); 'native features first' stays practice. | `judgement` | W11; `.github/**`, `template/.github/**` | no | no |
| DEC-010 | X | register only. **not verified:** harness choice; second vendor deferred by DEC-1244 Q-8, Q-10. | `judgement` | none | no | no |
| DEC-011 | T | `src/gov/check/runner.py:272` (`openspec-validate`). The G5 CI run is retired by DEC-1242 T-9. | `checked-after` | W7, W16; `openspec/**` | no | no |
| DEC-012 | P | `src/gov/store/loader.py:1` and `:13` (graph from git, no model). Register headings are the second record form (DEC-473). | `code` | W2, W6; `src/gov/store/**`, `docs/DECISION_REGISTER.md` | no | yes |
| DEC-014 | P | `src/gov/codeintel/__init__.py:38` | `code` | W2, W6; `src/gov/codeintel/**` | no | yes |
| DEC-016 | P | `src/gov/retrieval/fusion.py:31`; `src/gov/retrieval/semantic.py:494`. The store file is `.gov-runtime/store.db` (`src/gov/store/layout.py:21`). | `code` | W2; `src/gov/retrieval/**` | no | yes |
| DEC-017 | X | licence rule is text (no licence check found in `src/gov/config/models.py`); strongest P `src/gov/config/models.py:30`, `src/gov/retrieval/rerank.py:29` | `judgement` | W2; `src/gov/config/models.py`, `src/gov/retrieval/**` | no | no |
| DEC-022 | T | `src/gov/adapters/portability.py:1` (`adapter-portability`) | `checked-after` | W1, W14; `.rulesync/**`, `template/.rulesync/**` | no | no |
| DEC-023 | T | `src/gov/lock/__init__.py:149` (compare, run by `gov doctor`); strongest P `src/gov/update/core.py:324` (`copier copy`). Update plans from two Copier renders (`src/gov/update/core.py:10`). | `checked-after` | W1, W14; `copier.yml`, `src/gov/update/**`, `src/gov/lock/**` | no | no |
| DEC-024 | T | `src/gov/doctor/command.py:372` (vendored folder digest). Two-stage review item superseded (EMERGENCY-2 §3.6). | `checked-after` | W10; `template/governance/kernel/vendor/**` | no | no |
| DEC-025 | P | `.claude/settings.json:16`, `:39` (PreCompact, Stop); `template/governance/kernel/hooks/stop.py:73`. Live item is the checkpoint hooks. lefthook and kit CI: retired by DEC-1242 T-9, files still present. | `code` | W15; `.claude/settings.json`, `template/governance/kernel/hooks/**` | no | yes |
| DEC-030 | O | `src/gov/retrieval/synthesis.py:21` (synthesis notes: no caller in `src/` or the kernel); strongest P `src/gov/retrieval/retrieve.py:594`. Audit 4 'enforced for producers': true for batches and stopping reason, not for synthesis. | `judgement` | W2; `src/gov/retrieval/**` | no | no |
| DEC-032 | X | `template/governance/kernel/skills/retrieval/SKILL.md:17`. Audit 4 'enforced' not confirmed: no code runs retrieval in a subagent. | `judgement` | W2, W10; `template/governance/kernel/skills/retrieval/**` | no | no |
| DEC-033 | P | `src/gov/closure/__init__.py:27`; `src/gov/retrieval/retrieve.py:472` | `code` | W2, W6; `src/gov/closure/**` | no | yes |
| DEC-034 | P | `src/gov/retrieval/retrieve.py:796`. `UNRESOLVED_IDS` added (`src/gov/closure/__init__.py:20`). | `code` | W2; `src/gov/retrieval/**` | no | yes |
| DEC-035 | N | no facet choice by radius or task class found (grep of `routing.py`, `retrieve.py`); strongest P `src/gov/retrieval/retrieve.py:57` (rounds by radius). Synthesis column unwired (see DEC-030). | `judgement` | W2; `src/gov/retrieval/**` | no | no |
| DEC-036 | O | `src/gov/retrieval/synthesis.py:67` (`validate_notes`, no caller). Audit 4 'enforced' not confirmed: not wired to a check. | `judgement` | W2; `src/gov/retrieval/synthesis.py` | no | no |
| DEC-037 | T | `src/gov/retrieval/canary.py:18`, run by `src/gov/doctor/command.py:702` and `src/gov/adopt/lite_gates.py:231`. Not run after a reindex, and a miss does not mark a facet inside `gov retrieve`. | `checked-after` | W3, W16; `template/governance/kernel/canaries/**` | no | no |
| DEC-039 | H | `docs/DECISION_REGISTER.md:161` (changed by DEC-1204: merged into the golden rule). DEC-1204 (1) restates the threat model. | none (spent) | none | yes: DEC-1204 | yes |
| DEC-040 | X | held by absence only; `gov install` installs a pinned Gov OS release, not third-party tools (`src/gov/install/pin.py`). Owner approval per tool superseded (EMERGENCY-2 §2.3). | `judgement` | W1, W14; `governance/project/tool-registry.yaml` | no | no |
| DEC-050 | N | kit `template/.gitignore:1` ignores `.gov-runtime/` and `__pycache__/` only. Gov OS's own `.gitignore` holds all three. WSL rule is text. | `judgement` | W1; `template/.gitignore` | no | no |
| DEC-060 | X | register; `docs/charter/CHARTER_v6.md:29`. **not verified:** principle; no code search. | `judgement` | none | no | no |
| DEC-065 | X | register. **not verified:** six master rules, partly held elsewhere (DEC-069, DEC-089); this row classes the set. | `judgement` | specs; W7, W9 | no | no |
| DEC-066 | N | Wave 3 roles absent: `template/governance/kernel/roles/` holds nine roles. Guard-enforced paths superseded (EMERGENCY-2 §2.2). | `judgement` | W8; `template/governance/kernel/roles/**` | no | no |
| DEC-069 | O | `src/gov/queue/checks.py:54` (landing checks who wrote tests); `src/gov/tasks/queue.py:38`. Gov OS's own landings are plain-path (DEC-1239). | `judgement` | W9, W11; `tests/acceptance/**`, `src/gov/queue/**` | no | no |
| DEC-074 | T | `src/gov/adapters/portability.py:1` (Q5-Q7); strongest P `src/gov/codeintel/__init__.py:38` (Q10). Q9 extra denies superseded (EMERGENCY-2 §2.4; `template/governance/kernel/settings.json` has two); Q13 CI by DEC-1242 T-9; Q4 on-demand Ollama overtaken (boot start). | `checked-after` | W1, W2; `.rulesync/**`, `src/gov/retrieval/**` | no | no |
| DEC-085 | T | `src/gov/readiness/checker.py:139`, `:113` | `checked-after` | W7; `src/gov/readiness/**` | no | no |
| DEC-086 | T | `src/gov/telemetry/command.py:13` (`gov telemetry`). EMERGENCY-2 §10 A-7 measures the share by P1's method meanwhile. | `checked-after` | W15; `src/gov/telemetry/**` | no | no |
| DEC-087 | H | `docs/DECISION_REGISTER.md:2191` (DEC-1242 T-9: retire the kit's CI and lefthook). Removal is plan item 3-5; the CI files are still present. | none (spent) | `.github/**`, `template/.github/**` | yes: DEC-1242 | yes |
| DEC-089 | T | `src/gov/check/claims.py:98` (`core-claims`) | `checked-after` | W7; `src/gov/check/claims.py` | no | no |
| DEC-090 | N | `src/gov/adopt/lite_gates.py:30` (A7, A10 only; no A11 or final verdict stage); strongest P `src/gov/adopt/stages.py:570`. DEC-1227 D1 / DEC-1231 plan the lite verdict. | `judgement` | W1; `src/gov/adopt/**` | no | no |
| DEC-091 | P | `src/gov/retrieval/retrieve.py:763` | `code` | W2; `src/gov/retrieval/**` | no | yes |
| DEC-093 | X | `template/governance/kernel/templates/decision-package.md:22`. Changed by DEC-220, DEC-1236. | `judgement` | W5; `template/governance/kernel/templates/decision-package.md` | no | no |
| DEC-102 | X | `template/governance/kernel/skills/discovery/SKILL.md:28` | `judgement` | W7; `template/governance/kernel/skills/discovery/**` | no | no |
| DEC-103 | X | `template/governance/kernel/skills/planning/SKILL.md:15` | `judgement` | W7; specs | no | no |
| DEC-105 | X | `template/governance/kernel/skills/change/SKILL.md:38`. CIT-P for kernel text superseded (EMERGENCY-2 §3.5). | `judgement` | W6, W7; specs | no | no |
| DEC-127 | T | `src/gov/doctor/command.py:505` (reads `governance/project/tool-registry.yaml`) | `checked-after` | W1; `governance/project/tool-registry.yaml`, `template/governance/kernel/schemas/tool-registry.schema.json` | no | no |
| DEC-136 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md:140` | `judgement` | W9; `tests/acceptance/**` | no | no |
| DEC-165 | N | only the Contract names it (`docs/contract/capabilities/CAP-41.g.md:6`); no lesson-packet code in `src/`. Wave 3. | `judgement` | W16; specs | no | no |
| DEC-166 | X | `gov discover` exists (`gov --help`); no kit text found for the plain-language trigger beyond the discovery skill's description (`template/governance/kernel/skills/discovery/SKILL.md:6`) | `judgement` | W7; `src/gov/discover/**` | no | no |
| DEC-167 | X | `template/governance/kernel/skills/change/SKILL.md:48` | `judgement` | W6; `src/gov/impact/**` | no | no |
| DEC-182 | T | `src/gov/close/traceability.py:30` (`product-traceability-trailers`). `--trailer` use: `template/governance/kernel/roles/engineer.md:26`. | `checked-after` | W11; commit trailers | no | no |
| DEC-185 | P | `src/gov/config/loader.py:3`, `:100` | `code` | `governance/project/**`, `src/gov/config/**` | no | yes |
| DEC-186 | P | `src/gov/check/command.py:55`; check id `core-schema` (`template/governance/kernel/checks/core-schema.yaml:1`) | `code` | W11, W16; `template/governance/kernel/checks/**` | no | yes |
| DEC-199 | T | `src/gov/doctor/command.py:235` | `checked-after` | `template/governance/kernel/vendor/**` | no | no |
| DEC-205 | O | `src/gov/launch/launcher.py:126`. The CTO's start script uses the same path. | `judgement` | W8; `src/gov/launch/**` | no | no |
| DEC-220 | X | `template/governance/kernel/skills/orchestration/SKILL.md:42`. Changed by DEC-416, DEC-974, DEC-1236; the computed level (DEC-1242 T-1) is unbuilt. | `judgement` | W5; `template/governance/kernel/skills/orchestration/**` | no | no |
| DEC-221 | X | `template/governance/kernel/templates/role-test-designer.md:14` | `judgement` | W9; `tests/**` | no | no |
| DEC-225 | T | `src/gov/check/pathmap.py:75` (`core-pathmap`); strongest P `src/gov/config/loader.py:129` | `checked-after` | W11; `governance/project/path-map.yaml` | no | no |
| DEC-227 | T | `tests/acceptance/W1-08/test_w1_08_id_grammar.py:57`, `:90`. Held by an acceptance test only. | `checked-after` | `template/governance/kernel/schemas/**` | no | no |
| DEC-231 | O | `src/gov/launch/command.py:58` | `judgement` | W8; `src/gov/launch/command.py` | no | no |
| DEC-236 | X | `template/governance/kernel/roles/ticket-lead.md:13`. Nothing refuses a lead's merge. | `judgement` | W8, W11; `template/governance/kernel/roles/**` | no | no |
| DEC-262 | T | `src/gov/doctor/command.py:372`; strongest O `src/gov/launch/role.py:31` (reads `vendored.yaml`) | `checked-after` | `template/governance/kernel/skills/superpowers/**` | no | no |
| DEC-264 | P | `template/governance/kernel/hooks/precompact.py:5`, `:213`; `.claude/settings.json:16` | `code` | W15; `template/governance/kernel/hooks/**` | no | yes |
| DEC-274 | P | `src/gov/store/loader.py:7` | `code` | W2; `src/gov/store/**` | no | yes |
| DEC-279 | P | `src/gov/checkpoint/record.py:93` | `code` | W15; `src/gov/checkpoint/**` | no | yes |
| DEC-282 | P | `src/gov/checkpoint/command.py:48`. Real-session test and family check are history. | `code` | W15; `src/gov/checkpoint/**` | no | yes |
| DEC-292 | O | `src/gov/tasks/claims.py:52` (no `src/` command found that calls `claim`) | `judgement` | W8; `.tickets/**` | no | no |
| DEC-300 | T | `src/gov/tasks/queue.py:38` (read by `gov status`) | `checked-after` | W7, W9; `src/gov/tasks/**` | no | no |
| DEC-305 | T | `src/gov/readiness/checker.py:144` | `checked-after` | W7; `openspec/**` | no | no |
| DEC-328 | T | `src/gov/decisions/checker.py:61`; `template/governance/kernel/templates/decision-package.md:26` | `checked-after` | W5; `src/gov/decisions/**` | no | no |
| DEC-329 | T | `src/gov/decisions/checker.py:3`, run by `src/gov/check/authority.py:40` (`core-authority`) | `checked-after` | W5; `src/gov/decisions/**` | no | no |
| DEC-332 | O | `src/gov/launch/command.py:34` | `judgement` | W8; `src/gov/launch/command.py` | no | no |
| DEC-381 | P | `src/gov/retrieval/semantic.py:504` | `code` | W2; `governance/project/path-map.yaml` | no | yes |
| DEC-388 | P | `src/gov/retrieval/semantic.py:504`; `src/gov/adopt/stages.py:441`. hit@5 half is history. | `code` | W2; `governance/project/path-map.yaml` | no | yes |
| DEC-391 | P | `src/gov/closure/__init__.py:17`; `src/gov/closure/command.py:23`. Amended by DEC-393, DEC-396. | `code` | W6; `src/gov/closure/**` | no | yes |
| DEC-409 | P | `src/gov/pause/command.py:285` (terminal and typed code; ancestry `:245`). Items (3)-(4) went with the guard's hooks (`src/gov/containment/commits.py:6`). | `code` | W15; `src/gov/pause/**` | no | yes |
| DEC-420 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md:48` | `judgement` | W8; `template/governance/kernel/roles/**` | no | no |
| DEC-430 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md:136` | `judgement` | W9 | no | no |
| DEC-438 | T | `src/gov/check/runner.py:526` | `checked-after` | W16; `src/gov/check/**` | no | no |
| DEC-444 | P | `src/gov/checkpoint/record.py:23`; `template/governance/kernel/hooks/precompact.py:43` | `code` | W15; `src/gov/checkpoint/**` | no | yes |
| DEC-448 | T | `src/gov/doctor/command.py:66` (historical records), `:499` (tools). One-off rebuild and drift items are history. | `checked-after` | W14, W16; `src/gov/doctor/**` | no | no |
| DEC-452 | T | `src/gov/doctor/command.py:499` | `checked-after` | W14, W16; `src/gov/doctor/**` | no | no |
| DEC-454 | O | `src/gov/close/command.py:178`. `gov close` is to retire (DEC-1217 L2-1); not run on Gov OS (DEC-953). | `judgement` | W11; `src/gov/close/**` | no | no |
| DEC-462 | X | `template/governance/kernel/templates/role-test-designer.md:16` | `judgement` | W8, W9 | no | no |
| DEC-463 | T | `src/gov/check/citations.py:145` (`core-decision-citations`, warning) | `checked-after` | W5; `docs/DECISION_REGISTER.md` | no | no |
| DEC-468 | T | `tests/acceptance/W1-38/test_w1_38_rulesync.py:215`, `:258` | `checked-after` | `.rulesync/**` | no | no |
| DEC-469 | T | `tests/acceptance/W1-38/test_w1_38_rulesync.py:258` (turns red on a version move) | `checked-after` | `governance/project/tool-registry.yaml`, `.rulesync/**` | no | no |
| DEC-473 | T | `src/gov/check/citations.py:25`; strongest P `src/gov/store/loader.py:13` | `checked-after` | W5; `docs/DECISION_REGISTER.md` | no | no |
| DEC-479 | T | `src/gov/check/citations.py:21`; `governance/project/path-map.yaml:422` | `checked-after` | W5; `governance/project/path-map.yaml` | no | no |
| DEC-488 | T | `src/gov/lock/__init__.py:149`; `src/gov/doctor/command.py:719` | `checked-after` | W14; `copier.yml`, `src/gov/lock/**` | no | no |
| DEC-728 | X | register; `docs/emergency-2/EMERGENCY-2.md:60` (run folders). **not verified:** the root convention has no code line; write fence superseded (EMERGENCY-2 §2.2). | `judgement` | W15 | no | no |
| DEC-732 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md:18`; strongest P `src/gov/accept/runner.py:548` | `judgement` | W10; `src/gov/accept/**` | no | no |
| DEC-740 | H | `docs/charter/CHARTER_v6.md:32` (DEC-064 now superseded by EMERGENCY-2 §8.1); pilot run closed (DEC-1203) | none (spent) | none | yes: DEC-1211 (EMERGENCY-2 §8.1); done, DEC-1203 (3) | yes |
| DEC-772 | P | `src/gov/release/command.py:85`. Patch and approved releases by code are DEC-1223's; guard prefix item superseded. | `code` | W13; `src/gov/release/**` | no | yes |
| DEC-782 | P | `src/gov/retrieval/vector_cache.py:29` (bound) | `code` | W2; `src/gov/retrieval/vector_cache.py` | no | yes |
| DEC-803 | X | `template/governance/kernel/skills/audit/SKILL.md:26` | `judgement` | W7 | no | no |
| DEC-815 | P | `src/gov/closure/__init__.py:22` | `code` | W6; `src/gov/closure/**` | no | yes |
| DEC-818 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md:132`. P1 six parts retired as ceremony; the daily P2 digest is live. Decisions page: DEC-1236. | `judgement` | W5 | no | no |
| DEC-826 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md` (reviewers commit nothing: no line read for it); strongest O `src/gov/launch/launcher.py:160`. **not verified:** item (3)'s text carrier. | `judgement` | W8; `src/gov/launch/**` | no | no |
| DEC-832 | N | `template/.rulesync/skills/` holds the four packs, frontend and devops; no performance pack or test-execution role. Frontend and DevOps deferral overtaken; CTO may re-word. | `judgement` | W8; `template/governance/kernel/skills/**` | no | no |
| DEC-836 | X | `template/governance/kernel/templates/brief.md:34` (memory first). `gov context` item superseded (EMERGENCY-2 §5.5). | `judgement` | W2, W8 | no | no |
| DEC-837 | X | register (checkpoint at every handover); strongest P `template/governance/kernel/hooks/sessionstart.py:19`. RESUME HERE is being replaced by the checkpoint form (DEC-1242 T-13, DEC-1253). | `judgement` | W15; `template/governance/kernel/hooks/sessionstart.py` | no | no |
| DEC-838 | X | register; strongest O `src/gov/launch/launcher.py:377` (no compaction threshold) | `judgement` | W8, W15; `src/gov/launch/**` | no | no |
| DEC-848 | P | `.claude/settings.json:76` (push denied). Owner's daily backup push superseded by the hourly bundle (EMERGENCY-2 §2.8). | `code` | W13; `.claude/settings.json` | no | yes |
| DEC-850 | X | `template/governance/kernel/skills/orchestration/incident-response.md:28`. Changed by DEC-855, DEC-972; decisions page DEC-1236. | `judgement` | W5, W15 | no | no |
| DEC-859 | N | item (5) 'every code brief says so': no kit text found (grep for the tool's traversal names); strongest P `src/gov/codeintel/__init__.py:64`. Items (1)-(2) are held by code. | `judgement` | W6; `src/gov/codeintel/**` | no | no |
| DEC-860 | P | `src/gov/retrieve/command.py:56`; `src/gov/retrieval/retrieve.py:808`. Items (2)-(3) superseded. | `code` | W2; `src/gov/retrieval/**` | no | yes |
| DEC-861 | X | `template/governance/kernel/templates/role-test-designer.md:29`. Amended by DEC-1057. | `judgement` | W5 | no | no |
| DEC-866 | X | orchestrator's sweep is text; strongest T `src/gov/links/check.py:920` (`ENFORCES_SUPERSEDED`) | `judgement` | W5, W6; `docs/DECISION_REGISTER.md` | no | no |
| DEC-898 | X | scratch budgets are text; strongest O `src/gov/resources/gate.py:109` (disk, inodes) | `judgement` | W8, W15; `src/gov/resources/**` | no | no |
| DEC-902 | X | weekly trigger is text; strongest T main-tree:`.gov-runtime/scratch/orchestrator/tools/sweep.py:1`. No sweep line in the crontab. | `judgement` | W15, W16 | no | no |
| DEC-906 | T | `tests/acceptance/W1-01/test_w1_01_history.py:18`; strongest O `src/gov/queue/checks.py:54` | `checked-after` | W9, W11; `tests/acceptance/**` | no | no |
| DEC-912 | T | `tests/acceptance/W1-01/test_w1_01_integration_merges.py:112`. Third-review items are history. | `checked-after` | W11; `tests/acceptance/W1-01/**` | no | no |
| DEC-918 | O | `src/gov/containment/commits.py:308` (called by `gov close`). Live-hook half superseded. | `judgement` | W11; `src/gov/containment/**` | no | no |
| DEC-933 | X | nightly 'every night' not scheduled (crontab lines commented). **Spent candidate:** DEC-1244 X-1 / DEC-1242 T-8 make the full run on-demand and weekly; CTO to decide. | `judgement` | W16; `governance/project/orchestration/nightly/**` | no | no |
| DEC-943 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md:50` | `judgement` | W8, W10 | no | no |
| DEC-953 | X | register. **not verified:** items not checked one by one. **Spent candidate:** DEC-1239, DEC-1244 X-1, EMERGENCY-2 §4.3. | `judgement` | W9-W11 | no | no |
| DEC-959 | O | `src/gov/queue/command.py:43` (merge queue); push P `.claude/settings.json:76`. Run-frequency lines changed by DEC-968, DEC-1244 X-1. | `judgement` | W11; `src/gov/queue/**` | no | no |
| DEC-961 | O | `src/gov/resources/gate.py:7`. Item (3) changed by DEC-984. | `judgement` | W8, W15; `src/gov/resources/**` | no | no |
| DEC-963 | X | engineer's merge of the tests is practice; strongest O `src/gov/launch/launcher.py:1143`, `src/gov/launch/store.py:1` | `judgement` | W8, W9; `src/gov/launch/**` | no | no |
| DEC-968 | X | register; nightly not scheduled (crontab). **Spent candidate** for items (1)-(2): DEC-1244 X-1; (3) 'every red dealt with at once' still asks. | `judgement` | W11, W16 | no | no |
| DEC-972 | X | register. **not verified:** ping script not read; quiet hours changed by DEC-973. | `judgement` | W5, W15 | no | no |
| DEC-973 | X | `template/governance/kernel/skills/orchestration/briefs-and-returns.md:182` (quiet hours, a placeholder). Stopping decisions go at any hour (DEC-1157, DEC-1217). | `judgement` | W5, W15 | no | no |
| DEC-979 | X | tools lane is text; strongest P* main-tree:`.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh:2` (crontab uses it) | `judgement` | W15; `src/gov/resources/**` | no | no |
| DEC-984 | O | `governance/project/orchestration/nightly/nightly.sh:168` (the nightly is not scheduled) | `judgement` | W16; `governance/project/orchestration/nightly/**` | no | no |
| DEC-989 | O | `src/gov/queue/command.py:43` (close written at the land). Baseline item is history. | `judgement` | W11; `src/gov/queue/**` | no | no |
| DEC-998 | X | register; `governance/project/orchestration/tools/start_cto.sh` starts with Remote Control. **not verified:** the test push and session-id check at start have no line read. | `judgement` | W15 | no | no |
| DEC-1007 | X | CTO keeps the ready list (text); strongest P* `governance/project/orchestration/tools/dispatch/dispatcher.py:15`, `:45` (cron each minute). Product form is `gov dispatch` (W2-207 open). | `judgement` | W8, W15; `src/gov/dispatch/**` | no | no |
| DEC-1030 | X | morning-package crash report is text; strongest A `governance/project/orchestration/tools/dispatch/dispatcher.py:33` | `judgement` | W15; `src/gov/dispatch/**` | no | no |
| DEC-1031 | O | GPU budget in the gate `src/gov/resources/config.py:233`; strongest P `src/gov/retrieval/rerank_service.py:123`. CPU-fallback clause superseded (EMERGENCY-2 §5.8). | `judgement` | W2, W15; `src/gov/resources/**`, `src/gov/retrieval/**` | no | no |
| DEC-1032 | O | `src/gov/resources/config.py:233` (budget, read by the gate); strongest P `src/gov/retrieval/rerank_service.py:56`, `:123`, `src/gov/retrieval/vector_cache.py:2`. Items (2), (3) history. | `judgement` | W2, W15; `src/gov/resources/**` | no | no |
| DEC-1047 | X | `docs/emergency-2/EMERGENCY-2.md:39` (the aim, standing). Item (3) is carried by DEC-1204; the aim stays. | `judgement` | none | no | no |
| DEC-1052 | X | basis review and symptom flagging are practice; strongest O `src/gov/brief/build.py:157` (READY by code). Test-suite cut, homes and restart are history. | `judgement` | W7, W8, W16; `src/gov/brief/**` | no | no |
| DEC-1065 | P | `src/gov/retrieval/semantic.py:482`; `src/gov/retrieval/retrieve.py:397`. Items (3)-(4) history. | `code` | W2; `src/gov/retrieval/**` | no | yes |
| DEC-1088 | T | `src/gov/links/check.py:22`; strongest O `src/gov/launch/plan_check.py:1`. 'Closed tickets never edited' superseded (EMERGENCY-2 §4.2). | `checked-after` | W7, W8; `src/gov/plan/**`, `.tickets/**` | no | no |
| DEC-1092 | X | `template/governance/kernel/skills/retrieval/SKILL.md:28` | `judgement` | W2 | no | no |
| DEC-1097 | X | 'search again once' is text; strongest P `src/gov/adopt/fabric.py:115` (0.6B, 6000 tokens). The 80's run items are history. | `judgement` | W2, W4; `src/gov/retrieval/**` | no | no |
| DEC-1098 | X | `template/governance/kernel/skills/retrieval/SKILL.md:28`; strongest P `src/gov/adopt/fabric.py:115` | `judgement` | W1, W2; `src/gov/adopt/**` | no | no |
| DEC-1101 | X | weekly 'not found' count is text; strongest T `src/gov/memaudit/schedule.py:28`. No memaudit line in the crontab. | `judgement` | W4, W16; `src/gov/memaudit/**` | no | no |
| DEC-1116 | H | `docs/DECISION_REGISTER.md:1599` (approval and promotion done). The 1.0.0 'baseline' has been moved on by later versions. | none (spent) | none | yes: done; kernel text since DEC-1211 (EMERGENCY-2 §3.5) | yes |
| DEC-1120 | X | register; strongest O `src/gov/launch/launcher.py:183`. Model table and promotion superseded by DEC-1225, DEC-1242 R-4, R-5. | `judgement` | W8; `governance/project/criticality.yaml` | no | no |
| DEC-1134 | H | `.tickets/DAEO-ar89.md:3` (W2-155 closed). The two `accepted_reds` entries are still at `governance/project/path-map.yaml:500`: remove them. | none (spent) | `governance/project/path-map.yaml` | yes: done (W2-155 closed) | yes |
| DEC-1146 | X | `governance/project/briefs/LEAD-w2-common.md:129`; strongest O `src/gov/dispatch/admission.py:252` | `judgement` | W8, W15 | no | no |
| DEC-1149 | X | 'usage never stops' is text; strongest O `src/gov/launch/launcher.py:1294` (runaway brake). Figure items history. | `judgement` | W8, W15; `src/gov/spend/**` | no | no |
| DEC-1157 | X | register. **not verified:** items (9) and (13) not checked in code (either could be N). | `judgement` | W8, W11, W15 | no | no |
| DEC-1158 | A | no-spill watched by `governance/project/orchestration/tools/dispatch/dispatcher.py:33`; strongest P `src/gov/retrieval/rerank_service.py:123`. Live item (3) only. | `checked-after` | W15; `src/gov/resources/**` | no | no |
| DEC-1170 | P | `governance/project/secrets.yaml:7`; `src/gov/secrets/__init__.py:99` | `code` | W2; `governance/project/secrets.yaml` | no | yes |
| DEC-1176 | X | weekly maintenance is practice (no cron line); strongest T `src/gov/memaudit/declare.py:33` | `judgement` | W1, W4; `src/gov/memaudit/**` | no | no |
| DEC-1182 | P | `governance/project/secrets.yaml:7`; `src/gov/rebuild/integration.py:16`. Items (2)-(3) superseded. | `code` | W2, W3; `src/gov/rebuild/**` | no | yes |
| DEC-1183 | X | register. **not verified:** the full-window setting was not read; 'lesson to memory at once' is practice. | `judgement` | W15 | no | no |
| DEC-1184 | P | `src/gov/rebuild/integration.py:16` (seeded), `:164` | `code` | W3; `src/gov/rebuild/**` | no | yes |
| DEC-1199 | X | register. **not verified:** EXAMIN's side not read. | `judgement` | none | no | no |
| DEC-1200 | X | EXAMIN brief is text; strongest P `src/gov/adopt/stages.py:475` (AS before A3). **not verified:** whether EXAMIN's Wave 0 has ended. | `judgement` | W1; `src/gov/adopt/**` | no | no |
| DEC-1203 | H | `.tickets/DAEO-7jln.md:5`, `.tickets/DAEO-kq8b.md:5` (W2-193, W2-194 closed) | none (spent) | none | yes: DEC-1204 (item 5); rest done | yes |
| DEC-1204 | X | moderator triage is text; strongest O `src/gov/brief/judging.py:1`, `src/gov/launch/launcher.py:868`. Two rounds in code is DEC-1241 P-9. | `judgement` | W11; `template/governance/kernel/skills/judging-work/**` | no | no |
| DEC-1206 | H | `.tickets/DAEO-kq8b.md:5` (W2-194 closed) | none (spent) | none | yes: done; the fresh-80 order by DEC-1207 (3) | yes |
| DEC-1207 | X | operator item is text; strongest T `src/gov/memaudit/fresh.py:122` | `judgement` | W4; `src/gov/memaudit/**` | no | no |
| DEC-1208 | X | register. **not verified:** carrier not read. `Class: Q` dropped by DEC-1242 R-8, time box by R-1. | `judgement` | W12 | no | no |
| DEC-1239 | X | `template/governance/kernel/templates/role-cto.md:79`. Changed by DEC-1245 for products. | `judgement` | W11, W13; `docs/emergency-2/integration/FINDINGS.md` | no | no |
| DEC-1240 | N | planned only: `docs/emergency-2/integration/INTEGRATION-PLAN.md:192` (Phase 6) | `judgement` | W1-W16 | no | no |
| DEC-1241 | N | `gov --help` lists `queue`, no `land` (P-10). One unbuilt item read; the weakest decides. | `judgement` | W1-W16; `docs/emergency-2/GOLDEN-WORKFLOW.md` | no | no |
| DEC-1242 | N | no `--direct` in `src/gov/queue/command.py` (T-2). One unbuilt item read. | `judgement` | W5, W8, W11, W16 | no | no |
| DEC-1243 | X | briefs rule is text; strongest P* main-tree:`.gov-runtime/scratch/orchestrator/tools/stall_check.sh:2`. Seven exemptions done (`governance/project/path-map.yaml:479`); (3) replaced by DEC-1244 X-1. | `judgement` | W11, W15; `governance/project/path-map.yaml` | no | no |
| DEC-1244 | N | X-2's stall push by code is still the scratch script (crontab). One unbuilt item read. | `judgement` | W1-W16 | no | no |
| DEC-1245 | N | no `docs/releases/0.1.7/TOOL-STATUS.md` (folder listed). Items refined by DEC-1252. | `judgement` | W1, W3, W14; `docs/releases/**` | no | no |
| DEC-1246 | N | `.tickets/DAEO-rt4s.md:3` (W2-207 open). Release number changed by DEC-1248, DEC-1250. | `judgement` | W8, W15; `src/gov/resources/**`, `src/gov/dispatch/**` | no | no |
| DEC-1247 | N | no Windows-memory reading found in `src/gov`; `.tickets/DAEO-rt4s.md:3` open | `judgement` | W15; `src/gov/resources/**` | no | no |

## Counts

| Class | P | P\* | O | A | T | X | N | H | all |
|---|---|---|---|---|---|---|---|---|---|
| rows | 27 | 0 | 15 | 1 | 31 | 66 | 15 | 7 | 162 |

| Proposed `Enforced-by:` | `code` | `checked-after` | `judgement` | none (spent) | all |
|---|---|---|---|---|---|
| rows | 27 | 32 | 96 | 7 | 162 |

- **Spent: 7** (DEC-039, DEC-087, DEC-740, DEC-1116, DEC-1134, DEC-1203, DEC-1206).
- **May leave the digest: 34** (27 P and 7 H).
- **Not verified: 14** (DEC-001, DEC-010, DEC-060, DEC-065, DEC-728, DEC-826, DEC-953, DEC-972, DEC-998, DEC-1157, DEC-1183, DEC-1199, DEC-1200, DEC-1208). Each keeps `judgement` or its stated class and stays in the digest.
- **Spent candidates for the CTO (counted as not spent): 3** (DEC-933, DEC-953, DEC-968).

## What the CTO should know before applying it

1. **Audit 4's 11 "enforced for their producers", read again:** 6 are P (DEC-033, 034, 091, 409, 772, 815); DEC-037 is T (canaries run only in `gov doctor` and adoption's gate); DEC-030 and DEC-036 are O (synthesis notes have no caller); DEC-035 is N (no facet choice by radius or task class); DEC-032 is X (a skill sentence).
2. **A P row that leaves the digest still has history in its text.** The marker is the line cited; DE-1's check must resolve it, and a moved line would bring the entry back. A check id is sturdier where one exists (I cite one only for DEC-186).
3. **Entries overtaken in part or whole with no mark for it** (DEC-866 (1)): DEC-007, DEC-025 and DEC-074 (the kit's CI and lefthook, DEC-1242 T-9); DEC-087 (wholly, T-9); DEC-409 (3)-(4) (the guard's hooks); DEC-933, 953, 968 (the nightly and the selection, DEC-1244 X-1); DEC-1120 (DEC-1225, DEC-1242 R-4, R-5); DEC-1208 (DEC-1242 R-1, R-8).
4. **Stale state found while reading** (records only, nothing changed): `governance/project/path-map.yaml:500` still lists DEC-1134's two accepted reds although W2-155 is closed; the kit's `template/.gitignore` lacks DEC-050's `.claude/worktrees/` and `target/`.
