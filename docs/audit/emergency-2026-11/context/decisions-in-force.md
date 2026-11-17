# Summary: the decisions in force (not the register)

A summary for a newcomer, made 2026-11-16 from `docs/DECISION_REGISTER.md`. How chosen: the decisions this
project's working practice names daily (the CTO's standing practices, the guard, the operator, the reviews, the
memory measure, today's owner decisions), each by its register title, its status and its "Changed by" marks. It
is not complete: the register holds about 1,200 entries; read an entry there before acting on it. Titles are the
register's own words, cut at 220 characters.

## The aim, the register and how decisions are made

- DEC-1047: The emergency raised one level: everything stopped but the memory infrastructure; a harsh investigation of what to lift, measured against the Gov OS's aim; DEC-1010 stays (ACCEPTED)
- DEC-861: The orchestrator commits the records of the owner's decisions; the owner's push is the acceptance (standing) (ACCEPTED)
- DEC-866: Supersession propagates (standing) (ACCEPTED)
- DEC-974: The memory-chain line back in every status block; a new ticket in the WBS is a P1; a lighter lane for the CTO's own tools, to be proposed (standing) (ACCEPTED)
- DEC-105: Evidence-triggered change (ACCEPTED)
- DEC-1158: The emergency of 2026-11-02 lifted, with its freeze; its spent items marked (standing) (ACCEPTED)
- DEC-1209: EMERGENCY: break the cycle that is stalling the work: no new tickets (W2-196 withdrawn); running work stops at its current step; no new review rounds, leads or workers; the audits and the rubric research go on; EXAMIN… (ACCEPTED)

## Roles and who talks to whom

- DEC-1199: EXAMIN's CTO leads EXAMIN's Wave 0 (the Gov OS CTO on Gov OS only); F-022 (b), go LITE, F-023 (a) with a product ticket; the freeze lifted; the operator as the owner's free second hand (FREE-HAND D1-D7) on (A-full) se… (ACCEPTED; changed by DEC-1203)
- DEC-1200: P-EXAMIN-LEAD-1 (a), (b), (c): the EXAMIN CTO's Wave 0 brief 0d96110c approved, a long-lived Remote Control session, the channel; P-ADOPT-SPEC-AUDIT-1 (a): stage AS standard, its ticket W2-192 (ACCEPTED)
- DEC-1191: P-SESSIONS-1 items 1, 2 (widened) and 4b: adopting sessions headless; one operator job runner for everything the owner approves; the sentinel's inbox rule (ACCEPTED; changed by DEC-1196)
- DEC-1193: The sets-root file: the owner writes ~/.config/gov-os/sets-root once; an operator job that reads it reports only counts and ids to the CTO (ACCEPTED)
- DEC-1104: D-4's ten cases by option C; the operator agent approved as recommended; the landing selection's environment fixed before its results are relied on; ACTs given as messages for the owner's operator (ACCEPTED)
- DEC-1173: The evening of 2026-11-13 (3): P-9 (a); CLAUDE.md and AGENTS.md (b); no plan change for EXAMIN; the handover's trial line (ACCEPTED)
- DEC-1196: The accidental runner install undone; (O) ACTs by hand until act-O is built straight after the runner's install; P-JOBS-ROUTINE-1 (a) with R3 changed; when the owner's yes is needed; no rehearsal against a live path (ACCEPTED)

## How work is judged and reviewed

- DEC-1204: How work is judged: one golden rule (merges ADR-0001 / DEC-039, DEC-801 and DEC-1010 item 1) (standing); P-GOLDEN-RULE-1 (a); the skill `judging-work` approved (0fc1c502); W2-195 filed (ACCEPTED)
- DEC-1010: Reviews converge; W2-81 lands; W2-93 proves its own exam; W2-117 before EXAMIN's copy; the dispatcher versioned; checks and the embedding server in slots, real CPU judged; a research session (standing) (ACCEPTED)
- DEC-1154: A change decided after a ticket's review gets a narrow independent check of that change, without asking the owner; the ticket lands on it (standing) (ACCEPTED)
- DEC-1156: Five lead packages decided at night (ROUTE-1 (a), P-W2-120-1 (b), W2-33 A, W2-113 PKG-1 (a) and PKG-2 (b), P-W2-98-IF-1 (a)); W2-157's and W2-159's F4 fixed now; two standing rules (the CTO fixes decided-behaviour tes… (ACCEPTED)

## Tickets, leads and the lifecycle

- DEC-1157: Every rule that holds or delays a lead removed tonight, except what protects the machine and the governance; W2-113 PKG-3 (b); W2-155 started; W2-60a built; two logs added (standing) (ACCEPTED)
- DEC-1180: The afternoon of 2026-11-14: N2 (b), changed heading-cited sections listed for the walled writer; q02's fix by a one-question fix flow, run today (W2-94 reopened); the EXAMIN CTO starts tonight after the re-pin and th… (ACCEPTED; changed by DEC-1182 (5))
- DEC-1142: The morning of 11-12: W2-176's no-cap bytes approved; P-W2-23-8 (a); W2-115 PK-1 (a)+(c); W2-148 S15 option 2; the operator hours as built; the ticket table (kept after the fact, four parked); no new ticket or split w… (ACCEPTED)
- DEC-1146: A resource gate's refusal is a wait, not a refusal under the two-refusal rule (standing) (ACCEPTED)
- DEC-1088: Dependency mapping decided: `gov plan` (W2-136), the template's `reads:`, `needs:` and `waits_on:`, enforcement at launch; closed tickets are never edited (standing) (ACCEPTED)
- DEC-1120: RUBRIC-2: the owner's rubric of model and effort by role and criticality class, replacing OWNER-DECISION-P2-0008 §11 (RUBRIC-1); changes DEC-839 (1)-(3) (ACCEPTED)
- DEC-839: Lens F's other values: model, effort and subagents per launch; agent teams off; prompt v3 (plan §11 item 5; item 3) (ACCEPTED)
- DEC-1169: W2-32 closes on its own review, S11 re-worded to the measured trade; every status block names each ticket added and the decision that approved it (ACCEPTED)
- DEC-878: Every countdown starts with one progress line: the tickets by state out of the total, and the keystones done, in progress and ahead (ACCEPTED)

## The guard and the walls

- DEC-953: The owner's decision on AUDIT-GOV-FEATURES-1: the Gov OS is built and tested first, then dog-fooded; every Gov OS feature lifted as a gate on this repository's own development; tickets close on the audit's 10 practice… (ACCEPTED)
- DEC-954: The owner's approval of PLAN-W2-DEC953, with answers and amendments: EXAMIN gated by milestones, not a date; ACT 1 the five-rule guard; the roles spec first; memory for any repository; ACT 2 one re-pin; the three laye… (ACCEPTED; changed by DEC-1201, DEC-1202)
- DEC-820: Policy 2: reads open, writes closed (standing, under ADR-0001) (ACCEPTED)
- DEC-957: The owner's decisions on ACT 1, ROLES-SPEC-1 and MEMORY-SPEC-MAP: the batch stopped, installs only through the CTO, the 235 tests revised in W2-90, the roles approved with a software company's work order and an escala… (ACCEPTED)
- DEC-1052: P1-LIFT-1 and P1-PLAN decided: the basis, the rows, the templates with READY and DONE by code, the test suite cut to about 5,000, the homes, the updated plan, tonight's restart (ACCEPTED)
- DEC-1106: W2-148: F15 fixed in one exception round to DEC-1010; the guard's call log by its own ACT; the commit freeze in the operator agent's install folder; F7 kept; then ACT-OPERATOR-1 (ACCEPTED)

## Sandbox, box and permissions

- DEC-313: W1-46 DP-10: `gov launch` refuses permission bypass and added directories (ACCEPTED)
- DEC-1128: No switched-off control returns and no new guard rule goes live without set-up A's 100 % on the path map's actions; the lift does not wait for set-up A; set-up B dropped entirely; DEC-1010's one-rule principle investi… (ACCEPTED)
- DEC-1065: No CPU fallback for embeddings; search respects role separation; the fusion as a gap if a single route beats it; the search's speed near the pin's (standing for 1 and 2) (ACCEPTED)
- DEC-1203: P-JOBS-USER-1 corrected to (B), live now as an exception until Wave 3; GF-7 alone first; W2-27's run closed with exa-g6db as a named exception and product tickets for F-028 and F-030; W2-81's re-run brief 31acaf29 app… (ACCEPTED)
- DEC-1205: P-PERMISSIONS-1 (a) with the push belt (P): full permission inside the box, the guard still deciding; the order ACT-GUARD-FIX-9, the box, the no-prompt start lines, today (ACCEPTED)
- DEC-1207: yes ACT-GOLDEN-RULE-1 f9d67d5a; P-BOX-EXCEPTION-1 yes with F2 fixed, F1 and F3 Wave 3 rows; the memory measurement rule (standing): a fresh 80 for every measure, written and measured on one frozen state; today's order (ACCEPTED)

## Memory and its measurement

- DEC-1097: The experiments decided: the fresh 80 judges window 4's configuration (search again once) against K9's end-to-end bar; ACT-GUARD-SETS-1 rebuilt and applied before it; a seven-reviewer readiness review; keep the 0.6B; … (ACCEPTED)
- DEC-1098: The fresh 80 accepted and the measured configuration made Gov OS's memory standard; P-SELECT-GRAPH closed (do not build) with three cheaper fixes to propose; W2-130's sitting accepted; a sandbox-and-guard experiment b… (ACCEPTED)
- DEC-1179: MEMORY-AUDIT-P1: each repository keeps a standing hidden set judged end to end at 95 %, counts only, with a monthly fresh set as the check against fitting; W2-187 and W2-188 filed; O3 (b), the computed cadence (ACCEPTED; changed by DEC-1186 (4), DEC-1207 (3), DEC-1210 (1), (2))
- DEC-1186: ACT-GUARD-FIX-6 approved, applied after the re-pin with the hook measured by W2-111's method (Bash over 100 ms brings P-W2-111-MARGIN (b) at once); W2-15a's close Q1 (a), Q2 (a), Q3 (a); P-WALLS-REANCHOR-1 (B) and the… (ACCEPTED; changed by DEC-1187, DEC-1210 (3))
- DEC-1206: W2-194 keeps F-031; W2-15a closed on the walled run's record under Q2 (a), its gaps to W2-15b; the gap investigated by an operator job, ids and counts only (ACCEPTED)
- DEC-1210: P-FRESH-80-1 (a) with A13 (b): every memory measure a fresh 80 measured end to end at 95 % (the hidden half's judged figure the verdict, hit@k and the stacked share diagnostics); the amendments recorded now; W2-187 an… (ACCEPTED)

## Scope, waves and releases

- DEC-1201: Wave 2 keeps only Gov OS's own work: ten deferred or parked tickets to Wave 3's list, W2-27 to W2-30 to EXAMIN's Wave 0; F-028 (a) with the base-red condition; every report ends with the status block; EXAMIN has no cu… (ACCEPTED)
- DEC-1202: Wave 2's exit proof: W2-81's full re-run on release 0.1.1 across its six repositories (S-RERUN) stands for Gov OS proven on adopted repositories; W2-46 re-pointed; W2-82's wait on W2-27 dropped; the four extra Wave 3 … (ACCEPTED)
- DEC-1198: P-RELEASE-2 (a): release 0.1.1 and gov re-pinned from it; EXAMIN (i), go 0.1.1; EXAMIN F-021 (c), item 15 (a), TD tree (a); P-JOBS-USER-1 (B) with a Wave 3 row for OS-level separation; W2-81-FIGURES (b); BATCH1-HELD (… (ACCEPTED; changed by DEC-1199)
- DEC-1197: P-W2-81-VERDICT-1 (a), (b), (c): the five stale stores rebuilt and the read step re-run; the runner's stage list fixed in W2-81; two product tickets filed; the lite verdict and findings a Wave 3 row; W2-81 re-runs in … (ACCEPTED)

## Work sizing (provisional)

- DEC-1208: A work-sizing rubric: the ticket W2-196 approved (FULL, Wave 2, in parallel with EXAMIN's Wave 0); the provisional rubric in force from today; the operator's full permission and the no-prompt switch routed by it first… (ACCEPTED; changed by DEC-1209 (1))
