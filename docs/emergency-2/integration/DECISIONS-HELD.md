# Integration step two: every decision since DEC-1209 held by code or by text, and the three rubrics (DEC-1238 (6))

`docs/emergency-2/integration/DECISIONS-HELD.md` · research (Sonnet), read-only · 2026-11-22 · Gov OS `w2/integrate` at `1085f9b95`; EXAMIN `/home/usain/gov-os-runs/W2-27/examin` (read only, branch `wave0/schema-contract-and-disclosure-fix`)

**How it was made.** Memory first: `gov retrieve` ran once and returned a stale-path list (480 paths; the store is behind HEAD), so the bundle was not usable; the reading below is from the files named. Audit 1 (carrier by carrier) and audit 4 (§1.7 the standing rules and their class, §2 List A) are the base; I read DEC-1232 to DEC-1238 in the register (`docs/DECISION_REGISTER.md:2067-2140`), the golden workflow rules 6 to 8, `T2-ESCALATION-RUBRIC.md`, `DECISIONS-BY-PAGE-SPEC.md`, the lead briefs `LEAD-models-rubric.md` and `LEAD-fixes-015a.md`, and confirmed each code claim by reading the line named. No tests were run. No helpers were used.

**What moved since audits 1 and 4** (they read `3ab01e94b` and `266d6507c`; checked by `git merge-base` against `w2/integrate`):
- **Merged:** `e2/l2-4-queue` (the proving landing, `4f779086f` "batch: merge DAEO-j9z6", is Gov OS's first landing through `gov queue`; there is still no `governance/project/queue.yaml` here, EXAMIN has one), `e2/release-patch` (W2-209 slice a), `e2/d6-doctor-drift`, `e2/contract-015` (Contract 5.1, Charter release lines), `e2/w2-81-fixes`, `e2/fixes-015b` (F2, F4 to F9: doctor tools, one hook entry per program, W2-16's map, `QUEUE_WORKTREE_DIRTY`, no hit@5 floor: `FLOOR, TARGET = 85, 99` is gone from `retrieval/measure.py`), EMERGENCY-2 §13 (DEC-1237).
- **Not merged, in flight:** `e2/models-rubric` (9 commits ahead: R1 to R4), `e2/d1-verdict` (5), `e2/d5-memaudit-strict` (5), `e2/w2-207-runtime` (17), `e2/d7-adopt-lands` (3).
- **Brief only, no branch yet:** `LEAD-fixes-015a.md` (F1, F3, F10 to F19).
- **Still true at HEAD:** `close/state.py:17` `ESCALATION_AT = 3`; `memaudit/judge.py:31` reader and grader are Opus; the kit's role files still carry a `Launch by criticality` line naming Opus for C3 (engineer, independent-test-designer, independent-auditor, qa-engineer); `check/authority.py:44` skips `ACTIVE_UNAPPROVED`; the Charter has no determinism sentence yet (`CHARTER_v6.md:84` is still "Deterministic where it can be, judgement where it must be").

**EXAMIN's register.** It ends at **DEC-005** (69 lines, `docs/DECISION_REGISTER.md`). There is no DEC-006 or later on any branch (`git grep`, `git log --all`). The brief's "from DEC-006 on" is empty; Table 2 covers DEC-001 to DEC-005.

## Key

| Code | Class | Meaning |
|---|---|---|
| **P** | code on the path | code refuses or does it before the act, on the path today's Gov OS sessions take (path:line) |
| **P\*** | code on the path, outside the product | the same, but the code is a scratch script or the CTO's own tool (`.gov-runtime/scratch/…`, `start_lead.sh`); no adopted repository gets it |
| **O** | code off the path | built inside `gov queue`, `gov launch`, `gov brief`, `gov release --patch` and not used by Gov OS's own sessions today |
| **A** | checked after (auto) | a hook, cron line or after-step finds it by itself |
| **T** | checked after (typed) | code finds it only when someone types the command |
| **X** | text only | a sentence in a document, role file, skill, script comment or memory note; no code reads it |
| **N** | not built | decided, with no code and no complete text carrier yet |
| **H** | history | spent or superseded; nothing to hold |

Where an item has several parts, the row takes the **weakest** part and the notes name the strongest. "Fix" names the audit 4 List A id (`A-n`) or the brief line that would hold it by code. The mark "(H\*)" means history once an act happens (0.1.5's cut).

---

## Table 1: Gov OS, EMERGENCY-2 itself (DEC-1211 "v3 in force", A-1 to A-14, B-1 to B-4)

| # | Item | Requires | Class | Held by (path:line) | In flight | Fix / List A |
|---|---|---|---|---|---|---|
| E1 | Read EMERGENCY-2 first; it supersedes | reading order | X | `CLAUDE.md:5`; no hook injects it (`sessionstart.py` injects only the checkpoint). §13 (DEC-1237, `543e0559f`) closes the stale lines audit 1 listed | – | A-30 (SessionStart `startup`); A-25 lint |
| E2 | Guard, sandbox, permission prompts retired | none exist | X (state) | `src/gov/guard` holds only `__pycache__`; `launcher.py:12-16`. Nothing refuses re-adding one; role files, templates and ~18 skills still say "the guard decides" | contract-015 text only | A-25 kernel text lint; N-24 sweep |
| E3 | Two denies only: `git push`, `sudo` | no push, no sudo | P | `.claude/settings.json` deny lines; `update/core.py:22-24, 382-390` removes legacy lines | – | A-31 doctor line "deny lines present" |
| E4 | Operator retired | no operator | H | folder removed (G1 `3efb533c5`); residue is text in `adopt/SKILL.md:71` | – | A-25 |
| E5 | Hidden sets caught by the transcript scan | a voided measure | T | `memaudit/scan.py:1-13`; runs inside `gov memaudit` | – | A-29 schedules the weekly measure |
| E6 | Hourly `git bundle` backup | recover work | A | crontab `7 * * * * … gov backup`; `src/gov/backup/`. A 41-hour gap (20-22 Nov) went unnoticed | – | A-8 doctor `backup` age |
| E7 | ACT and CIT-P retired; kernel text is the CTO's call | no process for text | X | `CLAUDE.md:27`; `skills/change/SKILL.md` still describes CIT-P; no check | – | A-25 lint; CAP-24.c re-worded (merged) |
| E8 | Gitleaks only before a repository goes public or is shared | no scan cost | X | off by `secrets.yaml` `scan: off` (`secrets/__init__.py:56,99`), but the kit CI scans on push (`ci.yml.jinja:73`) | – | N-12 |
| E9 | Review only for a red test, a failed landing or a broken feature; at most two rounds | no review of green | X | `CLAUDE.md:29-35`, `judging-work`; **contradicted by** `ESCALATION_AT = 3` (`close/state.py:17`), `role-lead.md:49`, qa-engineer "checks every ticket" | – | A-18, A-25 |
| E10 | Memory first: retrieve, read the whole bundle, search again | agents use memory | X | text in role templates and 7 skills; `gov brief` carries the retrieval (`brief/memory.py`) but cuts it (`BUNDLE_BUDGET`, `retrieve.py:48`); memory-use log is typed | N-13 | A-11 (uncut bundle), A-35 |
| E11 | Memory-use log | countable use | T | `src/gov/memory_use/` | – | A-35 |
| E12 | Basis line checked at the decision-record commit; weekly review | no regrowth | T | `gov decisions basis` (`decisions/basis.py`) exits 1 on `BASIS_MISSING`; nothing runs it at a commit | – | A-28 (reference-transaction hook) |
| E13 | Old register archived read-only | no stale reading | H | `docs/archive/DECISION_REGISTER-2026-11-19.md`; path map | – | – |
| E14 | A-1: keep the nightly, brake, slots, dead-man | machine safety | X (state, **contradicted**) | crontab lines for the nightly are commented; no dead-man line; `run_tick.sh` runs each minute | w2-207 | A-29; A-38 |
| E15 | RT-1 to RT-8, the run-time tool | one tool for dispatch, load, stalls | O / N mix | slices 1 to 3 built; old watchers live; RT-3, RT-7 not built | `e2/w2-207-runtime` | A-38 |

## Table 1: DEC-1209 to DEC-1238

| # | Item | Requires | Class | Held by (path:line) | In flight | Fix / List A |
|---|---|---|---|---|---|---|
| 1209 (1)-(4), (6), (7) | emergency stop, audits, guard fixes, reports | – | H | lifted by DEC-1211 (A-10); (1) replaced by DEC-1219 (6) | – | – |
| 1209 (5) | EXAMIN works directly, no ticket loop | – | H | superseded by DEC-1224 (1) and EXAMIN DEC-005 | – | – |
| 1210 (1), (6), (7) | every measure a fresh 80 (40+40), end to end, 95 %, hidden half the verdict; hit@k only a diagnostic | a figure that means one thing | T | `memaudit/declare.py:34-36` (95 %, n=80). The hit@5 floor is gone (F9 merged; `measure.py`, `retrieve_check.py`, kit check now a warning). Open: the figure has no stamp | F15 (015a, no branch); `e2/d5` | A-9 |
| 1210 (2)-(4), (9) | DEC-1179 amendments, W2-15b, first job | – | H | – | – | – |
| 1210 (5) | EXAMIN's measure is a fresh 80 at 95 % | same | T | EXAMIN `memory-audit.yaml` (`half_size: 40`); the 95 % is a code constant, not a key | – | A-9 |
| 1210 (8) | W2-187, W2-188 reopen at the lift | – | H | changed by DEC-1233 (1) N-31: no reopen; the weekly maintenance is a chore | – | – |
| 1212 (1) | the CTO's full window, a fresh CTO each morning | CTO cost | X | `CTO-HANDOVER.md`; `start_cto.sh`; DEC-1229 confirms no cap | – | A-36 |
| 1212 (2) | models by the rubric, by code; helpers from fixed roles; the exceptions file | right model | P | `.claude/hooks/agent_model.py` (refuses non-Sonnet, fork, Fable; `model-exceptions.yaml`). **Gap:** a spawn that names no model passes on the assumption the default applies; audit 1's four `Explore` helpers ran Opus | F13 (015a, no branch) | A-22 |
| 1212 (3) | Sonnet for the operator, leads, helpers, C2 | – | H | superseded by DEC-1214 K1, DEC-1225 | – | – |
| 1212 (4) | no inbox waiter, no fork, review only red | no fork | P (fork) / X (rest) | hook refuses `fork` (`agent_model.py`); `usage_log.sh:27` | – | – |
| 1213 | stage AS before A3; CAP-44.m | adoption order | P | `adopt/stages.py:475`; Contract rows 4.4, 5.0 | – | – |
| 1214 K1 | audit 4's rubric table; landing and close are code; a quality auditor only when a landing goes red | rubric; no reviewer per ticket | X | the table: see DEC-1225; "auditor only on red" is **not carried**: qa-engineer still checks every ticket (E9) | models-rubric R1 | A-25 |
| 1214 K2 | planning first; a planned wave's list changes only with the owner | owner controls the list | O | `launcher.py:47-48, 958` (a lead only for a planned ticket whose waits are met); escalation rubric P1.2 as text (`briefs-and-returns.md:114`) | – | A-6 puts leads on `gov launch`; see §3 (escalation) |
| 1214 G4, G5 | audit 8 groups; Charter v6, Contract v5 | – | H | both ACCEPTED; Contract 5.1 for 0.1.5 merged (`e2/contract-015`) | – | – |
| 1214 G6 | fresh audits only at release acceptance and stages A5, AS, A7, A10 | no audit per ticket | X | Contract MR-4, row 5.0; `audit/SKILL.md:61-65` still says "reviews of FULL tickets"; at A5/A7/A10 a typed auditor id is checked | – | A-20 (later), A-25 |
| 1214 G7 | the CTO approves and records every install | a registry row per tool | X | `tool-registry.yaml:6-11`; REA and Node recorded by hand (`6e0ce2101`); no check that a tool in use has a row | – | no List A id: a doctor part "every tool called has a registry row" (S) |
| 1214 L2 | landing and close are one deterministic action; the landing writes the close | one landing | O | `queue/command.py` (close written at the land, `:404`); proving landing done (`4f779086f`); Gov OS lands otherwise by hand merge (`Merge e2/fixes-015b` etc.). No `queue.yaml` | – | A-1 |
| 1214 M1 | `gov context` retired | no ceiling | P | command gone from `cli/main.py`; residue `dispatch/dispatcher.py:350`, EXAMIN `facts.yaml:33-35,78-80,117-120` | – | EXAMIN one-line change |
| 1214 G1-G3 | retired code removed; `record/w2` kept; size audit after | – | H | tag `pre-emergency-2`; G3 not yet due | – | – |
| 1214 T2 | a push when the CTO needs the owner's decision | owner pushed | N | text in `briefs-and-returns.md:127`; code: only the dispatcher's stall push (`dispatcher.py:1364-1374`, scratch). No push for a decision | – | decisions by page (DEC-1236 (1)) |
| 1214 E1-E3 | EXAMIN's dispositions; no new red | – | H | EXAMIN DEC-001 | – | – |
| 1214 NIGHT (c) | nightly and morning brief off until green, then both back | regression | X (state) | green met (`NR-20261120T154700Z`, 18,245 passed); crontab lines still commented | – | A-29 |
| 1215 | temporary Fable for Opus roles | – | H | reverted 2026-11-19; residue `model-substitution.yaml` (`active: false`), `launch/role.py:281-310 substitute`, `start_cto.sh:10` still calls `substitute()` | models-rubric R3 | – |
| 1216 (1), (2) | that night's order | – | H | – | – | – |
| 1216 (3) | the status block ends every report, counted each time | honest counts | P\* | `.gov-runtime/scratch/orchestrator/tools/status_block.py`; no kit text names it; only the CTO's memory note | – | A-32 `gov status --digest` |
| 1216 (5) | CTO-stall push; plan read every 10 min above 95 % | no stall | P\* | `usage_log.sh:27`, `dispatcher.py:1364` (stall 3600 s), `cto_watch.sh` | w2-207 | A-38 |
| 1217 (1) L2-1 | `gov close` merged into `gov queue`; the strict close retires | one landing | N | `cli/main.py:102` `Command("close", …)` still live; strict close tests remain | – | A-18 (`COMMAND_RETIRED`) |
| 1217 (1) L2-2 | `accepted_reds`, `load_sensitive` retire | no waived reds | N | `path-map.yaml:483, 495`; `close/ratchet.py:23`; `close/command.py:1085` | – | A-25 + a retirement ticket |
| 1217 (1) L2-3 | a lead runs `gov accept` only before returning | cost | X | `role-lead.md:43` still says "check red"; ticket-lead.md:12 | – | A-3 |
| 1217 (1) L2-4 | Gov OS lands on `gov queue` after one green proving landing | one landing | O | proving landing done 2026-11-22 13:54 (`4f779086f`); the code is merged; own landings still by hand | – | A-1 (add `queue.yaml`, retire `land.py`, `close_queue.sh`, `hand_merge_check.sh`) |
| 1217 (1) L2-5 | keep the name `queue` | – | H | done | – | – |
| 1217 (1) L2-6 | `gov queue --direct` checks direct commits after the fact | chores checked | N | no `--direct` in `queue/command.py` | – | A-16 |
| 1217 (2), (3) | G1-X exemption; 0.1.4 cut | – | H | `path-map.yaml:443`; tag `v0.1.4` | – | – |
| 1217 (4) K1-1 | senior engineer Opus | rubric | X | `senior-engineer.md:6` | models-rubric R1 | A-22 |
| 1217 (4) G1-2 | the P-* packages and the October assessment removed before the first fresh 80 | clean memory | N | `governance/project/orchestration/packages/` still holds 87 `P-*.md`; `docs/assessment/2026-10/` | – | W-2 / a chore |
| 1217 (5) | a decision that stops work pushes the owner at any hour | owner pushed | X | `briefs-and-returns.md:127`, `T2-ESCALATION-RUBRIC.md` §3; no code | – | decisions by page; §3 below |
| 1217 (6) | `gov update` restores no removed deny line | two denies | P | `update/core.py:22-24, 382-390` | – | – |
| 1217 (7) | golden rules at the head of every adopted CLAUDE.md/AGENTS.md | rules reach adopters | X | kit head `governance.md:12-27`; adopt and update copy it, nothing checks it stays at the head; Gov OS's own files put it last (`CLAUDE.md:29`); EXAMIN's `judging-work` is 1.1.0 | – | A-26, N-26 |
| 1218 (1) | full pace; push at 95 % and 99 % | owner pushed | N | `cto_watch.sh:13-14` wakes the CTO; nothing pushes the owner | – | A-36, A-38 |
| 1218 (2)-(5) | fresh CTO; TI-8 audit; W2-42 closed | – | H | – | – | – |
| 1219 (1) | G5-1 to G5-13, CAP-63 to CAP-69 | – | H | Contract row 5.0 | – | – |
| 1219 (2) | the escalation rubric replaces DEC-957's | the right level | X | text only: `briefs-and-returns.md:104-127`, `incident-response.md:6`, role files; kit cites `docs/emergency-2/T2-ESCALATION-RUBRIC.md`, a path dead in adopted repositories | – | §3 below |
| 1219 (4) | W2-208 is not a ticket | – | H | – | – | – |
| 1219 (5) | `gov launch --fix`/`--chore`; a non-feature new ticket flagged, never refused; the `Fix:` trailer | rubric in code | O | `launch/command.py:64-65, 89-103`; `launcher.py:45-52, 1117`; `queue/checks.py:34, 124-139`; `queue/fix.py`; `queue/command.py:230, 409-416` | – | §1 below |
| 1219 (6) | a new ticket only for a new feature | no ticket sprawl | O (notice) / X | `NEW_TICKET_NOT_FEATURE` notice only; "a new KPI line on a closed feature is a new ticket": nothing refuses | – | §1 below |
| 1220 (1) | test cuts TI-1 to TI-7 | fewer tests | N | TI-2 done; TI-1 (`test_judge_commits`, `test_w2_115_strict`), TI-3 (`tests/unit/secrets_check/`) not done | – | a chore list |
| 1220 (2), (3), 1221 (2) | tmux exact names; release design; imports proposal | – | H | memory note `tmux-exact-session-target.md`; became DEC-1222, DEC-1223 | – | – |
| 1221 (1) | W2-81 judges memory end to end on Sonnet | one grading | T | `tests/acceptance/W2-81/w2_81_score.py:15-16, 31` | – | – |
| 1222 (1) | imports feature IM-0 to IM-5 | – | N | spec only (`proposals/IMPORTS-ADOPTION-SPEC.md`); after EXAMIN's fresh 80 | – | – |
| 1222 (2) | C3 trial: Opus test designers | – | H | superseded by DEC-1225 (6); `C3-TRIAL.md`, `NIGHT-COMMON.md:15-18` still old | – | A-25 |
| 1223 RB-1 | the CTO cuts patch releases by code; the authority file is the off-switch | release on behalf | O | `release/patch.py` (P1 to P5), `release/gates.py`, `gov release --patch`; `release-authority.yaml` `patch_releases: off`; **text still says "owner's"** (`CLAUDE.md:9`) | `contract-015` fixed the Contract | A-13 |
| 1223 RB-2, RB-3, RB-6 | rehearsal gate; `bake_hours: 4`; `--rollback`; doctor as a fix | safe update | O | `release/gates.py:65-94`, `release/proving.py:29`, `update/command.py:7-9` | – | – |
| 1223 RB-4, RB-5 | push only on hold or rollback; the update a step of the run-time tool | auto-update | N | slice (b) | `e2/w2-207-runtime` | A-38 |
| 1223 (8), (9) | study ceilings 2,000/5,000 chunks; order after 0.1.4 | – | N / H | (8) in the imports spec only; (9) spent | – | – |
| 1224 (1) | EXAMIN's own rules under review | – | X | EXAMIN DEC-005 | – | – |
| 1224 (2) | release acceptance item 4 moves to EXAMIN's first planned wave | accept on W2-81 and the fresh 80 | X | Contract 5.1 now says it (`e2/contract-015`); `gov release` gates do not read it | – | A-13 |
| 1224 (3) | release on behalf, slice (a) first | – | O | as RB-1 | – | – |
| 1225 (1) helpers | Opus only for the CTO and the senior engineer; helpers Sonnet, C3 included | rubric | P | `agent_model.py` (gap F13) | F13 | A-22 |
| 1225 (1) launched roles | the same for `gov launch` | rubric | O | `launch/role.py:345-380` reads the role file's `Launch by criticality`, which **still names Opus for C3 and Haiku for C0** at HEAD; `criticality.yaml:6 opus:` for promotion and probe (`launcher.py:700-725`) | `e2/models-rubric` R1, R2 (unmerged); F19 (015a, no branch) | A-22 |
| 1225 (1) leads, CTO | the same for leads and the CTO | rubric | P\* | `start_lead.sh:6` (`--model claude-sonnet-5-5`); `start_cto.sh` `--model $model --effort high` (a computed Opus, with `substitute()`) | A-6; `gov launch orchestrator` later | A-6, A-24 |
| 1225 (2) | a wide audit the owner asks for runs Opus; a reviewer after a failed landing runs Sonnet | no stray Opus | P | `model-exceptions.yaml`: one `independent-auditor` Opus entry **with no limiter**, so any auditor helper may name Opus | `models-rubric` R3 | A-22 |
| 1225 (3) | no session runs Fable | no Fable | P | the hook refuses Fable; `launcher.py:739-745`; dead Fable code remains (1215 residue) | models-rubric R3 | – |
| 1225 (4) | the memory measure's reader and grader on Sonnet; the first Sonnet fresh 80 is the baseline | one grading | N | `memaudit/judge.py:31` is Opus at HEAD | `models-rubric` R4 (983fd5af0, unmerged) | A-9 |
| 1225 (5) | the table in the role files and copies, both repositories; tell the owner when live | one table | N | HEAD role files carry the old table; EXAMIN gets the kit's by `gov update` | `models-rubric` R1, R5 | A-24, A-27 |
| 1225 (6) | every Sonnet role measured as the C3 trial does | quality watch | X | `LEAD-COMMON:50`; `C3-TRIAL.md` baseline | – | – |
| 1226 | 0.1.5 carries W2-209; the owner's last manual cut | – | H\* | merged; 0.1.5 not cut | – | – |
| 1227 D1 (→ 1231) | the lite verdict stage (CAP-44.h) | verdict stage | N | `adopt/lite_gates.py:30` `GATES = ("A7", "A10")` | `e2/d1-verdict` | A-21 |
| 1227 D2-D4, D9 | findings; A2 and A8 documents as named exceptions; the route that keeps stale and legacy out of default memory | clean memory | N | EXAMIN's group `archive` has no `lexical_policy: not indexed` | waits for D1 | – |
| 1227 D5 | the strict forbidden-citation rule, also in the product's measure | one grading | N | `memaudit/matcher.py:105-107` lenient at HEAD | `e2/d5-memaudit-strict` (5 commits) | A-9 |
| 1227 D6 | `gov doctor`: a patch-only gap reports with exit 0 | quiet drift | T | merged `9a4adb350`; doctor is typed | – | A-29 (daily doctor) |
| 1227 D7 | real adopted repositories land; no new code (DEC-1232 (4)) | adopt then land | T | acceptance tests only | `e2/d7-adopt-lands` (3 commits) | – |
| 1227 D8 | the re-run measures the release with the fixes | – | X | `CTO-HANDOVER.md` §3 | – | – |
| 1228 (1) | imports its own ticket after the fresh 80 | – | N | not due | – | – |
| 1228 (2) | MCP tools are imports: registered, pinned, approved, given only to the roles that need them | role-scoped tools | N | REA registry row (`tool-registry.yaml:253-260`); no field or code gives a tool to some roles; see DEC-1232 (6) | 015a F1 | A-4 |
| 1228 (3), (4) | REA's code is study with its origin; the Startup Launchpad study outside the products | – | X / N | (4) the study folder; (3) the origin-record rule has no carrier | – | the imports register |
| 1229 | per-session context and wake cost measured, reported daily | cost | N | `usage_log.sh:14-19` logs the plan's percentages only | – | A-36 |
| 1230 | three audits, read-only, on Opus | – | H | audits delivered | – | – |
| 1231 | D1 rides the release after 0.1.5; 0.1.5 not held | – | H\* | – | `e2/d1-verdict` | – |
| 1232 (1) | the owner's priority order | order of work | X | judgement; `CTO-HANDOVER.md` | – | – |
| 1232 (2) | D1 and W2-207 start today | – | H | branches exist | – | – |
| 1232 (3) | W2-207 agnostic of the machine, MA-1 to MA-5 | a refusal on a machine too small | N | KPI lines in the lead brief; no code on the base | `e2/w2-207-runtime` | A-38 |
| 1232 (4) | D7, no new code | – | T | see D7 | – | – |
| 1232 (5) | the embedding server back before 0.1.5 | – | H | done 13:58; boot start is (7) of DEC-1233 | – | – |
| 1232 (6) | no session loads the owner's claude.ai connectors; each gets its role's MCP tools | no connector reaches a session | N (product) / P\* (leads) | only `start_lead.sh:6` `--strict-mcp-config`; `disableClaudeAiConnectors` is **not** in Gov OS's settings (015a's brief says it is); the CTO and its helpers load the connectors | `LEAD-fixes-015a.md` F1 (no branch) | A-4 |
| 1232 (7) | Startup Launchpad licence basis | – | H | recorded in the study's `LICENCE-BASIS.md` | – | – |
| 1233 (1) | N-27, N-28, N-29, N-30, N-31, W-3 (text decisions) | – | H | N-27, N-28, N-29 done (`e2/contract-015`, `543e0559f`); N-31 no reopen; N-30 and W-3 wait for the re-baseline | – | – |
| 1233 (1) N-13 | `gov brief` carries the whole bundle's text, no ceiling | uncut bundle | N | `BUNDLE_BUDGET` (`retrieve.py:48`) | – | A-11 |
| 1233 (2) N-07 | pause stops the dispatcher and the lead starter | the owner's brake | N | `start_lead.sh`, `run_tick.sh` ignore `.gov-runtime/freeze` | 015a F10 (no branch) | A-5 |
| 1233 (2) N-14 | no hit@5 floor or hard-blocking kit check | measure end to end | H | done (F9 merged: `W2-61`, `W1-21`, `W2-59`) | – | – |
| 1233 (3) N-06, N-03, N-25 | leads from a filled brief; the acceptance folder red on the base; the skills sweep | a deterministic flow | N | `start_lead.sh` has no ready check; `queue/checks.py:171-` checks tests exist, not red on base | – | A-6, A-3, A-25 |
| 1233 (4) | W-2: wire or retire each piece of uncalled code | no dead code | N | no ticket | – | – |
| 1233 (5) | audit 4 on determinism | – | H | delivered; approved by DEC-1238 | – | – |
| 1233 (6) | the determinism rule in the Charter and every Contract item | assessed by code | N | Charter sentence not applied; no `enforcement:` field | – | A-23 |
| 1233 (7) | embedders start at boot | memory always up | A | crontab `@reboot … embedders_at_boot.sh` (scratch) | W2-207 MA-5 | A-10 |
| 1233 (8), (9) | RAM restart after 0.1.5; Launchpad steps | – | H | the owner's hand | – | – |
| 1234 | a capacity assessment when W2-207 lands | – | N | `capacity_sampler.py` (scratch) collects; the assessment waits | `e2/w2-207-runtime` | – |
| 1235 (1) | nothing ahead of 0.1.5; push the moment it is green | – | H\* | – | – | – |
| 1235 (2) | after 0.1.5 the CTO cuts every release whose content the owner approved; the release rule names the owner's approving decision | release on behalf | N | `release/patch.py` P2 and P3 refuse any feature or Contract change (patch only); the change is a fix under W2-209 after 0.1.5 | – | A-13 |
| 1235 (3) | decisions by page | the owner answers by page | N | proposal only | – | §3 below |
| 1235 (4) | the week's usage explained | – | H | `usage-breakdown-2026-11-22.md` | – | – |
| 1236 (1) | decisions by page DB-1 to DB-5 | – | N | feature in two slices, the release after 0.1.5 | – | §3 |
| 1236 (2) | leads at medium effort | rubric | P\* | `start_lead.sh:3` `EFFORT=${EFFORT:-medium}`. **In the product, `launcher.py:176-177, 766` refuses `--effort medium` where the table says high** (the floor, DEC-1120 (3)) | F14 (015a, no branch) | §2 below |
| 1236 (3) | a change to any role's model or effort comes to the owner first | no silent change | X | DEC-1236 (3); the CTO's memory. Nothing refuses a change in code, settings, scripts or briefs | – | §2 below |
| 1237 | N-28: EMERGENCY-2 §13 | – | H | `543e0559f` | – | – |
| 1238 (1a) | the Charter's determinism sentence and the Contract's seventh envelope rule | – | N | not yet applied | – | A-23 |
| 1238 (1b) | the enforcement field on every item and new rule | assessed by code | N | – | – | A-23 |
| 1238 (1c) | the rubric covers research outputs; W2-81 analysis A4 is a fix under W1-41 | no ticket | N | the fix is not made | – | – |
| 1238 (2) | the golden workflow, verified and completed | – | X | `GOLDEN-WORKFLOW.md` | steps one to two | – |
| 1238 (3) | the integration emergency from the 0.1.5 cut | nothing new but integration | X | judgement; K2's planned-wave check (`launcher.py:958`) is off the path | – | A-6 |
| 1238 (4) | EXAMIN's planning waits for integrated Gov OS | – | X | – | – | – |
| 1238 (5)-(9) | steps one to four and the lift | – | N | step one and two briefs exist; the plan, the test, the lift not yet | – | – |
| 1238 (10) | spec questions come to the owner as decision records | no guessing | X | by hand until the page exists (DEC-1235 (3)) | – | §3, §4 below |

## Table 2: EXAMIN (`docs/DECISION_REGISTER.md`, DEC-001 to DEC-005; nothing later exists)

| # | Item | Requires | Class | Held by | In flight | Fix |
|---|---|---|---|---|---|---|
| 001 (1) | move groups G1 to G5; task cards become records | – | H | commits `d00a0f5` to `7e01891` | – | – |
| 001 (2) | trial data placed | – | H | – | – | – |
| 001 (3) | CLAUDE.md and AGENTS.md on Gov OS's template, keeping the owner's rules | one source | T | generated block checked by `portability.py:415-446` (typed) | – | A-26 |
| 001 (4) | as-built specs; S5 check; SCN-0038 | – | X | specs under `openspec/specs/`; the withdrawal fix waits for the release (002 (1)) | – | – |
| 001 (5) | memory option A: records with ids; legacy archived, out of the index | clean memory | P (partial) | `path-map.yaml:232-243` `archive-legacy` not indexed; **group `archive` (:212-228) has no `lexical_policy`** | – | D3 route (1227 D3) |
| 001 (6) | the measure: independent writer, fresh 80, 95 %, sets outside the clone | one grading | T | `memory-audit.yaml`; graded on Opus with the lenient citation rule, against DEC-1225 (4) and D5 | models-rubric R4; e2/d5 | A-9 |
| 002 (1) | withdrawal erases files and redacts, at the release | – | N | deferred as decided | – | – |
| 002 (2)-(5), (7) | U1-U7 as CONSTRAINTS; research documents; F00; exa-g6db | – | H | done | – | – |
| 002 (6) | `governance-close`, `cit-controller` archived; the other skills rewritten at the release | no retired kit named | N | 9 skills still name the archived kit (`live-migration/SKILL.md:46-47`) | – | A-25 |
| 002 (8) | three deny lines removed, with the fix in `gov update` | two denies | P | `.claude/settings.json:4-9`; `update/core.py:22-24` | – | – |
| 002 (9) | the market report placeholder bug fixed at the release | – | N | deferred as decided | – | – |
| 003 | what leaves the machine is allowed while the data is mocked trial data; revisit before real data | – | X | register only; the as-built spec still says "none" | – | a stopper before real data (a P1) |
| 004 (1)-(4) | value first, threat model, golden rule at the head | rules in every session | X | `CLAUDE.md:9-21`, `AGENTS.md:9-21`; `judging-work` at 1.1.0 | – | A-26 |
| 005 (1) | EXAMIN's own rules under review | – | X | CONSTRAINTS.md:3-7; `CLAUDE.md:76-77` reads as in force | – | – |
| 005 (2) | planning starts after the measure passes, Contract first | order | X | superseded in timing by Gov OS DEC-1238 (4) (waits for integrated Gov OS) | – | – |
| 005 (3) | X12 held until the planning stage | no ticket start | X | `.tickets/exa-6lq4.md:3, 68` open with a hold note; nothing refuses a start | – | §3 (a launch for a held ticket) |
| 005 (4) | the fresh 80 goes on | – | H | – | – | – |

## Counts by class

Counted by a script over the class column of the three tables above (a split class such as "P (partial)" or "O / N mix" counts as its first class; `P\*` is its own row). One row is one decision item, so a count is of items, not of lines of code.

| Class | Gov OS, EMERGENCY-2 (15) | Gov OS, DEC-1209 to DEC-1238 | Gov OS total | EXAMIN (DEC-001 to DEC-005) |
|---|---|---|---|---|
| P code on the path | 1 | 8 | 9 | 2 |
| P\* on the path, outside the product | 0 | 4 | 4 | 0 |
| O code off the path | 1 | 9 | 10 | 0 |
| A checked after (auto) | 1 | 1 | 2 | 0 |
| T checked after (typed) | 3 | 6 | 9 | 2 |
| X text only | 7 | 21 | 28 | 6 |
| N not built | 0 | 33 | 33 | 3 |
| H history | 2 | 30 | 32 | 4 |
| **rows** | 15 | 112 | 127 | 17 |

**Reading the counts.** Of the Gov OS decisions that still ask for something (not H), the largest group is **text only** (X) and **not built** (N): most decisions are held by a sentence in a document or are not built. Code that holds a decision **on the path** is a short list: the two denies and `gov update`'s refusal to restore them, the helper-model hook (fork, Fable, other models; the exceptions file), `gov adopt`'s stage chain, and the removal of `gov context`. The next group is built and **off the path** (O): the queue and launch refusals, the patch release gates, the planned-wave check. The scratch scripts that hold a decision (P\*) are exactly the tools the tool map (step one) must absorb or retire.

---

## 1. The ticket rubric: feature, fix, chore (golden rule 6; DEC-1219 (5)-(6); EMERGENCY-2 §4)

**The rule:** a ticket is a feature (spec and KPIs); a known bug in an existing feature is a fix, recorded under its owning ticket with its failing test first; records, docs, configuration and kernel text are chores, committed directly; a quick item that outgrows its time box becomes a fix or a feature; a new KPI line on a closed feature is a new ticket.

**What is in code today** (all of it built, none of it on Gov OS's own path):

| Part | Where | What it does | On the path? |
|---|---|---|---|
| `gov launch <role> <ticket> --fix "<line>"` | `launch/command.py:64-65, 89-103`; `launcher.py:45-52, 1117` | starts a role under the owning ticket, open or closed; the plan is not asked for a fix; usage errors exit 2 (both flags; `--fix` without a ticket; `--chore` with one; neither) | No: leads start by `start_lead.sh`, which has no ticket, class, `GOV_TICKET` or claim |
| `gov launch <role> --chore "<line>"` | same | starts with no ticket file and no `GOV_TICKET` | No |
| the queue's fix landing | `queue/checks.py:142 fix_line`; `queue/command.py:230, 409-416`; `queue/fix.py` | a branch whose commit carries `Task: <closed ticket>` and a non-blank `Fix:` lands with no second close, and `fix.append` writes one `fixes` entry (`line, branch, tip, tested, landed`) and a body line into `docs/close/<ticket>/CL-<ticket>.md` | Only for a landing through `gov queue`; Gov OS has landed once that way (`4f779086f`) |
| `NEW_TICKET_NOT_FEATURE` | `queue/checks.py:34, 106-139` | a ticket file the branch adds that has no verified KPI line or no spec body is named in a notice; **never refuses** (DEC-1219 (5)) | Same |
| the patch rule P1 to P5 | `release/patch.py:1-30, 162-169` | P3 reads ticket status and the `Fix:` / `Class: Q` / `Class: C` trailers: a release with a ticket closed since the last release, or a source commit with none of them, is not a patch | Used by `gov release --patch`, off (`patch_releases: off`) |
| the kernel text | `orchestration/SKILL.md:20`; `CLAUDE.md:10` | states the rule | text |

**What still rests on text:**
- A chore's class: `Class: C` is a commit trailer read only by the patch rule; there is no `--direct` in the queue (`queue/command.py`), so a chore lands untested and unlisted. "Tests unchanged" is not checked.
- Fix's failing test first: nothing checks it. The queue records a fix; it does not read the order of commits.
- A new KPI line on a closed feature: nothing refuses it.
- `ticket.md`, `planning/SKILL.md` and the brief template never name feature, fix or chore (audit 1, DEC-1219 (6)); `nightly-sheriff.md:119-122` still says "a P1 package, a new ticket".
- The "time box": no document defines it (see spec question SQ-1).
- A ticket's `class:` front-matter key is **not** the rubric's class. It is a free kind (`implementation` 185, `audit`, `config`, `integration`, `ops`, `research`, `schema`, …) that `launch/criticality.py:8` says "is never read"; `ticket.schema.json:44` makes it an optional non-empty string. A third meaning of "class" is criticality C0 to C3; a fourth is the trailer `Class: F|Q|C`.

**What makes it enforced on the path** (the design, smallest forms; sizes after audit 4):

| # | Change | Form | Size | When |
|---|---|---|---|---|
| 1 | Gov OS lands only through `gov queue` | add `governance/project/queue.yaml`; retire `land.py`, `close_queue.sh`, `hand_merge_check.sh` (A-1) | XS + chore | 0.1.5 follow-up, the first integration item |
| 2 | Every lead started by `gov launch` | `gov launch lead --brief <file>` with `--fix` / `--chore` / the ticket; `start_lead.sh` retired (A-6, with N-06 and F19) | M | 0.1.6 (integration) |
| 3 | The queue writes the fix record in the owning ticket from the `Fix:` trailer, and gives a notice when no test-adding commit precedes the first source commit of the fix | extend `queue/fix.py` (A-15) | S | 0.1.6 |
| 4 | `gov queue --direct` for chores: impact-selected tests, no ticket; a notice when a `Class: C` commit changes `tests/**` or `src/**` beyond records | A-16 (L2-6) | M | 0.1.6 |
| 5 | A ticket file the branch adds is checked at the land: no verified KPI or spec is a **refusal** where it is today a notice; a ticket file not in the planned wave's list is a refusal (rubric P1.2) | `queue/checks.py`; DEC-1219 (5) said "never refuse", so this needs the owner's yes (SQ-2) | S | 0.1.6 |
| 6 | The ticket carries one explicit kind so the check has a field to read | `ticket.schema.json` gains a `kind` that can only be `feature` (a fix and a chore have no ticket); do **not** reuse `class` (SQ-3) | XS | 0.1.6 |
| 7 | A commit that adds a KPI line to a closed ticket's `kpis` without being a new ticket is flagged | a queue check on the closed ticket's front-matter diff | S | later |
| 8 | The ticket's KPI lines equal the spec's K-lines | `gov brief`'s ready check runs `check_spec.py` (A-23b) | S | 0.1.6 |
| 9 | Chores and fixes listed in the digest | `gov status --digest` (A-32) | S | 0.1.6 |
| 10 | Text: ticket.md, planning skill and the brief template name the three kinds; the retired phrases linted (A-25) | kernel text, the CTO's | XS | 0.1.6 |

**Held today:** the code exists for 1 (`4f779086f` proves the queue), 3 (partly: the record, not the order), and the launcher's flags; **after 0.1.5:** 1 only if the CTO adds `queue.yaml` as the first integration chore; **left:** 2 to 10, about one M + one M + five S/XS items, and the definition of the time box.

---

## 2. The model and effort rubric by criticality (golden rule 7; DEC-1225; DEC-1236 (2)-(3))

**The rule:** Opus only for each product's CTO and a senior engineer per stream; every other agent Sonnet, critical work included; a wide audit the owner asks for runs Opus; effort is set by role in the rubric; **no session chooses its own model or effort; a change comes to the owner first**; leads at medium effort (DEC-1236 (2)).

**What holds today (HEAD):**

| Part | Where | Holds | Gap |
|---|---|---|---|
| Helper hook | `.claude/hooks/agent_model.py` (218 lines); `governance/project/model-exceptions.yaml` | every Agent spawn naming a model other than Sonnet is refused (Opus by an entry only; Fable and `fork` refused) | a spawn that names **no model** passes, so built-in types such as `Explore` ran Opus (F13); the one auditor Opus entry has no limiter |
| Criticality | `governance/project/criticality.yaml` (rules C3 to C1, default C2, `opus:`); `launch/criticality.py` | computes a ticket's class from `allowed_paths` and `profile`; read by the hook (`class: C3` entries, none left) and by `gov launch` (table lookup, promotion and probe use `opus:`) | with the table gone from the role files (R1) the class no longer changes any model or effort except promotion and probe |
| Role files | `template/governance/kernel/roles/*.md` and 3 copies | each carries `Launch default: model …, effort high` (CTO and senior engineer Opus; every other role Sonnet at **high**) and, for engineer, test designer, auditor and QA, `Launch by criticality: C3 claude-opus-5-5 …; C0 claude-haiku-5-5` | the C3-Opus and C0-Haiku lines are wrong against DEC-1225; `gov launch` reads them (`role.py:345-380`), so a launched C3 worker gets Opus |
| `gov launch` | `launch/launcher.py:427-455` refuses `--model`/`--effort` the launcher sets; `:176-177, 766` effort floor `high` | a worker's model and effort come from the role file; a caller's own `--model` is refused unless an exceptions entry names it | the **floor refuses `--effort medium`** where the table says high: DEC-1236 (2) cannot be applied through `gov launch` without changing it |
| Start scripts | `start_lead.sh:3,6` (Sonnet, `EFFORT` default medium, `--strict-mcp-config`); `governance/project/orchestration/tools/start_cto.sh:10,20` (Opus via `substitute()`, `--effort high`) | leads at Sonnet medium and the CTO at Opus high, by the script | scratch / outside the product; the CTO's script still calls the Fable substitution reader |
| Memory measure | `memaudit/judge.py:31` | – | reader and grader are Opus (DEC-1225 (4)) |
| "A change to a model or effort comes to the owner first" | DEC-1236 (3) | – | text and the CTO's memory only |

**What `e2/models-rubric` adds** (9 commits, unmerged; read from the commit subjects and the brief, not run): R1 the role files carry the table (Sonnet for every role but the two Opus roles, no `Launch by criticality` line) and copies regenerated; R2 `gov launch` picks the model by role (a lead gets Sonnet; another model needs an entry; Fable refused; a promotion's or probe's launch refuses another `--model`); R3 exceptions limited by class, task and decision; R4 the measure's reader, grader and checker run Sonnet and `FIGURES.json` names the models; R5 the EXAMIN list. **`fixes-015a` (brief only, no branch):** F13 the hook writes `model: "sonnet"` into every spawn that names none; F14 ticket leads at medium in the rubric and `gov launch`; F15 the figure's stamp; F19 `_rubric` refuses or replaces any model the table does not give (the 92 unit and 272 acceptance cases that plant Opus tables move to Sonnet) and the orchestration tools that still launch Haiku.

**What is left after those:**
1. **The effort table.** Golden rule 7 says effort is set by role in the rubric, but no table exists: every role file says `high`, DEC-1236 (2) sets leads to medium in the brief, and `criticality.yaml` has nothing for effort. One table (role, model, effort) in one file (SQ-4: the owner approves the effort of each role, since DEC-1236 (3) forbids the CTO setting any).
2. **The effort floor** (`launcher.py:176-177, 766`) changed or removed, or F14 fails its own verify.
3. **The CTO's own start** through the same table: `start_cto.sh` (later `gov launch orchestrator`) reads Opus and its effort from the table, with the Fable reader gone.
4. **A change refused unless it names the owner's decision:** the table file carries `decided: DEC-n` per row; a check (a `gov doctor` part and a G1 check, S) finds a table, role-file `Launch default`, start-script `--model`/`--effort` or settings value that differs from it, and a commit that changes the table without a `Decided-by: owner` trailer is flagged by the basis check (A-28's hook).
5. **Role files and scripts read the table**, not restate it (a role file loses its `Launch default` line, or a lint compares them), so there is one place to change (A-22, A-24, A-27).
6. **The criticality's job** is stated: today it varies nothing but promotion and probe; if the owner wants effort to vary by criticality (e.g. C0 at low), that is the table's columns (SQ-5).

| When | Held |
|---|---|
| **Today** | helper model by hook (with the F13 gap); leads Sonnet medium and the CTO Opus high by scratch scripts; wrong C3-Opus table in launched workers |
| **After 0.1.5 if models-rubric and fixes-015a land** | launched roles and helpers Sonnet by code (R1, R2, F13, F19); leads at medium in `gov launch` (F14); the measure on Sonnet (R4); Fable and un-limited Opus refused |
| **Left** | the one effort table with owner's `decided:` lines; the floor; the CTO and leads started by `gov launch` from the table (A-6, 0.1.6); the refusal of an unnamed change (S); EXAMIN's role files by `gov update` |

Size left: about S (table file and its check), XS (floor), S (CTO start), with A-6 (M) already counted in §1. When: the table and the check in 0.1.6 with A-22; nothing here blocks 0.1.5.

---

## 3. The escalation rubric (golden rule 8; `T2-ESCALATION-RUBRIC.md`; DECISIONS-BY-PAGE-SPEC)

**The rule:** every decision is taken at its level: P3 (a lead: reversible, inside its ticket, changes no spec, KPI or standing decision), P2 (the CTO: shared code, kernel text, a red landing, an install in scope), P1 (the owner: features, specs, KPIs, a ticket added to or removed from a planned wave, the Contract, the Charter, standing decisions, data and measurement, anything irreversible outside a worktree, a secret or paid service, a model or effort exception, a review not converged after two rounds, a release whose content he has not approved), or an emergency. The level is set **by code from the record's fields**, code **refuses a decision taken below its level**, owner decisions go to the decisions page, and the judgement is **kept in a fixed form** (golden rule 8; golden workflow W5).

**Today:**

| Question | Answer | Evidence |
|---|---|---|
| Is the level computed from the record anywhere? | **No.** `grep` for the rubric levels and `owner_decision` finds none that computes P1/P2/P3. The only "level" code is `close/state.py:17 ESCALATION_AT = 3` (review rounds) and the dispatcher's stall push | `src/gov/decisions` has `basis`, `checker`, `register`, `in-force` only |
| Is a decision below its level refused anywhere? | **Partly, for one fact.** The decision checker reports a decision that is ACTIVE with no `Decided-by: owner` trailer (`decisions/checker.py:289-420`, `ACTIVE_UNAPPROVED`), and `gov release` refuses the authority file without that trailer (`release/gates.py:60-93`). But `check/authority.py:44` **skips** `ACTIVE_UNAPPROVED`, so the check is defeated. The queue refuses nothing for a ticket that changes a spec, and the planned-wave check (`launcher.py:47-48, 958`) is off the path | A-14 |
| Is the judgement kept in a fixed form? | **Partly.** A register entry has a fixed shape (status, `Under:`, `Changes:`, decision, basis, governing sources) and the basis check reads it for rule entries; `decision-package` has `id, type, status` only (`decision-package.schema.json`); `decision-record.md` is an ADR template with no level or rubric field. DEC-818's six parts are prose | `decisions/basis.py`; schemas |
| Does a decision for the owner reach him by code? | No: by chat and by the CTO's push tool. DEC-1217 (5) "a stopper pushes at any hour" is text (`briefs-and-returns.md:127`) | – |
| Does the owner's answer reach the register by code? | No: the CTO writes it by hand with `Decided-by: owner (chat)` (basis line and ids checked later, typed) | – |

**The design that makes it enforced on the path.**

1. **The fields that set the level** (all on the decision's package, the existing `decision-package` schema extended, as DECISIONS-BY-PAGE-SPEC already does for `question`, `found`, `options`, `recommendation`, `sources`, `blocks`):

   | Field | Values | Level it forces |
   |---|---|---|
   | `touches` | list of: `spec`, `kpi`, `contract`, `charter`, `standing-decision`, `wave-list`, `kernel-text`, `shared-code`, `install`, `data`, `measurement`, `model-or-effort`, `release`, `none` | `spec`, `kpi`, `contract`, `charter`, `standing-decision`, `wave-list`, `data`, `measurement`, `model-or-effort`, `release` → P1; `kernel-text`, `shared-code`, `install` → P2; `none` → P3 |
   | `reversible` | `yes` / `no` | `no` → P1 |
   | `inside` | `worktree` / `repository` / `machine` / `outside` | `outside` → P1 |
   | `spends` | `none` / `paid` / `secret` | `paid`, `secret` → P1 (`secret` also `file_only`) |
   | `rounds` | the review round count | ≥ 2 and not converged → P1 |
   | `emergency` | one of the four named events or `none` | set → emergency |

   The level is `max` over these; **the author states facts, code states the level.** The spec's `rubric` field (`P1.1` to `P1.10`, `P2.brought`) becomes the **computed** line, not the author's claim; the author's `rubric` is allowed only if it equals the computed one.

2. **The code that computes it** (`src/gov/decisions/level.py`, a pure function over the package's front matter, with the table above as data in `governance/project/escalation.yaml`, so the rubric is data, not prose): returns `{level, line, reasons}`. A record whose fields are missing or contradict (`reversible: yes` with `touches: [contract]` is fine, it is P1; `spends: paid` with `touches: [none]` is also P1) gets a level, never a blank; a record with a field absent is **not page-ready** and is refused by `gov decisions page`.
3. **Where the refusal sits:**
   - **At the decision-record commit:** the basis check (`gov decisions basis`, today typed, A-28 puts it in the reference-transaction hook) gains: the entry's `Decided-by` must match its level (`owner` for P1; the CTO's `Role: orchestrator` for P2; the lead for P3). A P1 entry with no `Decided-by: owner` is refused as `ACTIVE_UNAPPROVED` once `check/authority.py:44`'s skip is deleted (A-14), and each new standing rule needs `Enforced-by:` (A-23).
   - **At the queue:** a branch that changes a spec (`docs/specs/**`, a `specification` record), a ticket's `kpis` or `allowed_paths`, a path under `docs/contract`, `docs/charter` or a planned wave's list must name an ACCEPTED P1 decision in a `Decision:` trailer; otherwise `QUEUE_DECISION_BELOW_LEVEL` (refuse). This is the same place as `NEW_TICKET_NOT_FEATURE` and uses the patch rule's P2 (owner's text) as a model.
   - **At launch:** the planned-wave check (K2) stays and joins A-6 so it is on the path.
4. **How it joins the decisions page:** `gov decisions page` takes only P1 and the P2 the CTO brings (`blocks` is not `nothing`); `rubric` is the computed line; a stopper (`blocks` set) forces the immediate page and the push; `gov decisions answer <sheet>` writes each answer as a register entry with `Decided-by: owner (page <batch>)`, so the level check at the commit passes by the same rule the sheet's entry satisfies (`ACCEPTED (owner, …)`, DEC-862 (c)). `gov decisions basis --week` lists owner entries by channel (`page` or `chat`) and counts open packages not on a page, as the spec says.
5. **The fixed form of the judgement** is the package itself: `question` (300), `found` (900), `options` 2-6 with `cost` and `consequence`, `recommendation {option, reason, confidence}`, `sources` each existing. The lead's or the CTO's own P3 and P2 choices are the same record with `status: ACCEPTED` and their `Decided-by`, listed in the digest (DEC-220), so the check at the commit is one rule for all three levels.

**Size and when:**

| Piece | Size | When |
|---|---|---|
| fields, limits, page-ready check, `gov decisions answer` (PG-1, PG-3 to PG-6) | slice (a), about 600 lines of the 1,100 | the release after 0.1.5 (DEC-1236 (1)); the integration plan may pull it in because rule 8 needs it |
| the level function and `escalation.yaml` | S (about 80 lines) | with slice (a) |
| the decision-record commit's level check | S | 0.1.6 with A-28 |
| delete the skip at `check/authority.py:44` | XS | 0.1.6 (A-14) |
| the queue's `QUEUE_DECISION_BELOW_LEVEL` | S | 0.1.6 |
| the page, push text, `--week` lines (PG-2, PG-7, PG-8) | slice (b), about 500 lines | the same release |
| kernel text, T2 file updated | CTO's, small | with slice (b) |

| When | Held |
|---|---|
| **Today** | text (the rubric), one fact checked after and defeated by a skip, none computed, none refused |
| **After 0.1.5** | nothing new (decisions by page is the release after it); `Decided-by` is checked only when typed |
| **Left** | the level function, the refusals at the commit and the queue, the page; decided by DEC-1236 (1) as a feature, so no new approval is needed for slice (a) and (b), but the **level function and the queue refusal are additions to the spec** the owner must approve (SQ-6) |

---

## 4. Spec questions (DEC-1238 (10))

Each is a decision record in the fixed form; none is answered here. "Stops work" says whether anything must wait.

### SQ-1: What is "a time box", so that a quick item that outgrows it becomes a fix or a feature?
- **Found:** golden rule 6 (`GOLDEN-WORKFLOW.md:31`) says a quick item that outgrows its time box becomes a fix or a feature. No document defines a time box, a length, or who starts the clock; no code reads one. EMERGENCY-2 §4 and CLAUDE.md name only the three kinds.
- **Options:** (a) a count the code can read: a chore's commits stop at N commits or M changed lines beyond records, then the queue refuses `Class: C` (cost: a number to choose, a few false refusals); (b) drop the sentence, a chore is whatever changes no behaviour and keeps the tests unchanged and green (cost: a loose item that grows is caught only by the `tests/**` and `src/**` check of A-16); (c) a stated limit in minutes for the lead only, judged (cost: not enforceable).
- **Recommendation:** (b), enforced by A-16's notice. Confidence: medium.
- **Sources:** `GOLDEN-WORKFLOW.md:29-31`; `EMERGENCY-2.md` §4; audit 4 A-16; `src/gov/release/patch.py:237-246`.
- **Stops work:** no.

### SQ-2: May the queue refuse a ticket that is not a feature, where DEC-1219 (5) said "flagged, never refused"?
- **Found:** `NEW_TICKET_NOT_FEATURE` is a notice by decision (DEC-1219 (5)); golden rule 6 and W12/W7 say the ready check refuses an unfilled item and every plan item is checked before work starts. The two disagree for a ticket added in a branch.
- **Options:** (a) keep the notice, refuse only at planning and launch where the ready check already refuses (cost: a non-feature ticket can land, then show in the digest); (b) refuse at the landing (cost: a lead's branch with a draft ticket is sent back; DEC-1219 (5) amended); (c) refuse only a ticket not in the planned wave's list (P1.2).
- **Recommendation:** (c), and keep the notice for the rest. Confidence: medium.
- **Sources:** DEC-1219 (5); `queue/checks.py:106-139`; `launcher.py:47-48`; `GOLDEN-WORKFLOW.md` rules 6, 8.
- **Stops work:** no.

### SQ-3: Which field carries "feature", given `class` already means three other things?
- **Found:** a ticket's `class:` is a free kind (`implementation` 185 of 219 tickets) that the launcher never reads (`criticality.py:8`); the trailer `Class: F|Q|C` is read only by the patch rule; criticality C0 to C3 is a fourth. The brief's example "`ticket.schema.json` requires `class`" would overload the first.
- **Options:** (a) add `kind: feature` (the only legal value; a fix or chore has no ticket) and require it in the schema (cost: a migration of 219 tickets, a one-off script); (b) require `class` to be one of `feature|…` (cost: breaks the 185 existing values and tests that read them); (c) infer feature from "has KPIs and a spec", as the queue does now, no field (cost: a draft is indistinguishable from a mistake).
- **Recommendation:** (a), migrated by a chore. Confidence: medium.
- **Sources:** `ticket.schema.json:44`; `launch/criticality.py:8`; `release/patch.py:162`; `.tickets/*.md`.
- **Stops work:** no.

### SQ-4: What is the effort of each role (golden rule 7: "effort is set by role in the rubric")?
- **Found:** there is no effort table. Every role file says `effort high`; leads run medium by DEC-1236 (2); `launcher.py:176-177, 766` refuses a launch's own effort below `high`; DEC-1236 (3) forbids the CTO changing any role's effort before the owner's yes, so the CTO cannot write the table.
- **Options:** (a) record today's as the table: CTO and senior engineer high, ticket lead and fix/chore lead medium, every other role high, then change only by the owner (cost: none now; engineer and test designer stay at the most expensive effort, 27 % of a day's spend was output at high effort, DEC-1236 basis); (b) the owner sets each role's effort now (cost: his time; best for usage); (c) effort by criticality, C0 low (cost: an extra axis, see SQ-5).
- **Recommendation:** (a) now, with (b) as a P1 page card after the integration, since changing it needs his yes anyway. Confidence: medium.
- **Sources:** `template/governance/kernel/roles/*.md` (line `Launch default`); DEC-1236 (2), (3); `usage-breakdown-2026-11-22.md`.
- **Stops work:** F14 (leads medium in `gov launch`) needs the floor changed; it is already approved in DEC-1236 (2), so no stop.

### SQ-5: Does criticality still vary the model or effort?
- **Found:** DEC-1225 made every launched role Sonnet at every criticality; after `models-rubric` R1 no role file has a `Launch by criticality` line, so the class decides only the promotion and probe Opus (`criticality.yaml:6`, `launcher.py:700-725`) and a `class: C3` exception entry (none). The brief's own title is "by criticality".
- **Options:** (a) retire the model axis and keep criticality for review depth and the profile only (cost: a few lines, rename the rubric "by role"); (b) keep an effort-by-criticality column (cost: another table the owner approves); (c) keep promotion and probe on Opus (cost: conflicts with DEC-1225 "no Opus but two roles and the owner's audit").
- **Recommendation:** (a), and say whether promotion and probe retire with it (they do under DEC-1225 unless the owner says otherwise). Confidence: medium.
- **Sources:** `LEAD-models-rubric.md` R1; `criticality.yaml:6`; `launcher.py:700-725`; DEC-1225; golden rule 7.
- **Stops work:** no.

### SQ-6: Is the level computed from the author's stated facts, or declared by the author (and only checked)?
- **Found:** golden rule 8 and W5 say the record's fields set the level by code. DECISIONS-BY-PAGE-SPEC (approved, DEC-1236) has a `rubric` field the author names (`P1.1` to `P1.10`, `P2.brought`) and PG-1 only checks it is a rubric line; the spec has no `touches`, `reversible` or `inside` fields. Taken as approved, the page cannot refuse a P1 that an author calls P2.
- **Options:** (a) add the fields of §3 to slice (a) and compute the line (cost: about 80 lines, a spec amendment the owner approves; a lead can still misstate a fact, caught after by the digest); (b) keep the declared `rubric` and add a check that `touches` of the diff (paths changed) forces P1 (cost: it covers only decisions that change files, not those about measurement or a spend); (c) leave the judgement to the CTO (cost: golden rule 8's "code refuses below its level" stays text).
- **Recommendation:** (a). Confidence: medium.
- **Sources:** `GOLDEN-WORKFLOW.md` rule 8, W5; `DECISIONS-BY-PAGE-SPEC.md` "The record", PG-1; DEC-1236 (1); `T2-ESCALATION-RUBRIC.md` §2.
- **Stops work:** no for 0.1.5; it shapes slice (a)'s record, so it should be answered before that ticket's spec is filled.

### SQ-7: Rubric P1.10 says a release and a re-pin are the owner's own hand; DEC-1235 (2) and golden rule 8 say the CTO cuts a release whose content he approved
- **Found:** `T2-ESCALATION-RUBRIC.md` §2 item 10 ("a release, a re-pin, a push, sudo… your own hand") was approved in DEC-1219 (2); DEC-1235 (2) changed releases (EMERGENCY-2 2.5, 8.3) after it; the T2 file and `CLAUDE.md:9`, the kit head and `judging-work:23-24` still say "owner's"; golden rule 8 lists "a release whose content he has not approved" under P1.
- **Options:** (a) amend T2 §2 item 10 to the golden rule's form, and the kit text with it (cost: a kernel-text change, the CTO's, plus the owner's yes to the rewording); (b) leave T2 and read the golden rule as overriding (cost: two rubrics in force, one in the code design).
- **Recommendation:** (a), in the same kernel sweep as N-25. Confidence: high.
- **Sources:** `T2-ESCALATION-RUBRIC.md` §2; DEC-1235 (2); `GOLDEN-WORKFLOW.md` rule 8; audit 4 §1.7 "Contradictions".
- **Stops work:** no.

### SQ-8: What is `Class: Q` in the patch rule?
- **Found:** `release/patch.py:10, 169, 246` accepts `Class: Q` and `Class: C` beside a `Fix:` trailer as a non-feature, but no document defines Q (RELEASE-ON-BEHALF names `F`, `Q`, `C` in passing: "F is on 263 commits").
- **Options:** (a) define Q as "a quick fix with no owning ticket" and make it a chore (cost: none, it is already a chore under the rubric); (b) drop Q and require `Fix:` or `Class: C` (cost: a patch of old commits fails); (c) leave it undefined.
- **Recommendation:** (b) once SQ-1 settles the chore definition. Confidence: low (the definition of Q may exist in a commit message I did not read).
- **Sources:** `release/patch.py:10, 162-169, 237-246`; `RELEASE-ON-BEHALF.md:63-69`.
- **Stops work:** no.

**Stoppers: none.** Nothing found stops 0.1.5 or the step three plan; SQ-4 and SQ-6 should be answered before F14 and the decisions-by-page ticket's spec are filled.
