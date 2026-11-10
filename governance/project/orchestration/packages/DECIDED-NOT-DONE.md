# Decided but not done: DEC-1047 to DEC-1096 and the owner actions since (audit, 2026-11-08)

**Kept current by every CTO session:** read at session start; tick an item off (with its commit) when done; add every new decided item with its trigger at the moment it is decided. START-NEXT-SESSION §3 and RESUME HERE carry the short form.

Read-only audit (an independent general-purpose agent for the CTO, session `ad44f5fe`) of every numbered item in DEC-1047..DEC-1096 (`docs/DECISION_REGISTER.md` lines 12978-13846), the
OWNER_ACTION line in `log/report-state.json` and `log/status-latest.txt` (11-07 23:03), CHECKPOINT RESUME HERE,
START-NEXT-SESSION §6, P1-PLAN's status table, the packages (LIFT-1 included) and the tickets in `.tickets/`.
Evidence of done was taken from `git log w2/integrate`, the files and the tickets' status. The tree is at `1fcd6ad5`,
with the CTO's uncommitted edits of 11-08 (START-NEXT-SESSION, DECISIONS-IN-FORCE, P1-PLAN, W2-88 record,
FRESH-80-READINESS). Nothing under `~/gov-os-eval/` and no question file was opened.

## 0. DEC-1097's fates (2026-11-08): the tracking table (tick with the commit when done)
| # | item | fate (DEC-1097) | state |
|---|---|---|---|
| 1 | ACT-GUARD-SETS-1 | (2) rebuilt with the reader folder and W2-84's cases deleted; rehearsed; operator applies before the 80 | **DONE 11-08**: applied by the owner's operator `15952bbf`; live guard check 453 run, PASS (hook `bd545af83198`); the writer's and checker's transcripts moved into the sets root's transcripts folder; no live worktree to merge |
| 2 | W2-141 | (8) tests first, built, reviewed, before the lift's re-pin | **MERGED 11-09** (`b1e2c3b9`, review READY round 2, accept 182/182); its hook change (`docs/changes/W2-141-hook/`) goes live in the lift's re-pin ACT |
| 3 | G3 | (7) no change before the 80; a ticket after the lift if the review finds it worth it | **DONE (decided)**; readiness 4: no ticket of its own, fold into M5's retest (16 % of items overlap, ~3 % of text) |
| 4 | G1 fewer scored pairs | (10) after the lift, as an option; the 138 re-measured if adopted | WAITS: after the lift |
| 5 | W2-20's launch line | (8) rebuilt to the line and W2-136's F2, reviewed, merged before the lift | **MERGED 11-09** (`686c594f`); live at the lift's re-pin |
| 6 | W2-130 and the 110-decision list | (9) now, CPU, proposal per id for the owner's sitting | **DONE 11-09**: the clean-up (`e12f8a30`) and the sitting (`c4420040`) applied |
| 7 | P-SELECT-GRAPH | (9) now, research only, result to the owner | **DONE**: do not build accepted, DEC-1062 closed (DEC-1098 (2)) |
| 8 | W2-84's hidden-half cases | (2) deleted with ACT-GUARD-SETS-1 | **DONE 11-08** (`15952bbf`); its three support files stay, a row for W2-84's close |
| 9 | no private reranker | (8) a new ticket, tests first, built before the lift | **MERGED 11-09** W2-145 (`22b734cb`, review READY round 2, accept 79/79); the slot-hold watcher retires at the lift's re-pin |
| 10 | P-LB-PRODUCT-1 | (11) into the three-layer plan after the lift | WAITS: after the lift |
| 11 | Q07/Q14; the visible 40's gaps | (12) Q07/Q14 after the 80, before any 138 re-measure; gaps to the next label audit | Q07/Q14 **DONE 11-09** (`55d1c029`, the sets root's visible copy synced); the gaps WAIT: the next label audit |
| 12 | the status block's K9 | (15) computed from the plan's list | **DONE 11-08**: `tools/status_block.py` reads `keystone_lists` in `log/report-state.json` (K9 from D9-FATES §3, 22 tickets; K7 done by DEC-1089); K9 now "in progress". K5 and K8 have neither a list nor a tag |
| 13 | ADR-0002 | (8) refreshed, reviewed, to the owner; DEC-1098 (5) accepted | **DONE 11-09**: `docs/adr/ADR-0002-architecture-and-stack.md` ACCEPTED; WAITS: re-read at the lift's re-pin |
| 14 | the label audit | (13) at each release cut and before any new verdict set; rubric v3 after the 80 | **DONE (trigger set)**; rubric v3 **DUE NOW** (after the 80) |
| 15 | the embedder trial | (14) a Wave 3 row | **DONE (parked)**: row to add with the Wave 3 list |
| 16 | the old window scripts (F1) | (15) fixed or retired, never reused | **DONE 11-08**: `live_window.sh`, `score_once_window.sh` and `extend_window.sh` (same defect) moved to `drafts/score-once/retired/` with a README (scratch, untracked) |
| 17 | GLOSSARY-1 | (6) (b): redesign beside the agent's words, toward decisions, for asking; retest on the 138 after the 80; build only if it helps | **DECIDED 11-08**; **DUE NOW** (after the 80): the redesign and its declaration, then the retest on the 138 |
| 18 | the fresh-80 path | (1): the scripts, the checker's pass (operator), the readiness review, the pre-flight, the control, the 80 | **DONE 11-08 21:46**: K9's bar PASSES, right end to end 78/79 (98.7 %), wrong claims 0 (`FRESH-80-RESULT.md`); every data condition run, all below the judged one; spent $109.05 |
| 19 | W2-139, W2-140 | (1)(g) held until after the 80 | **DUE NOW** (the 80 ran 11-08): one batch, one green run, outside a GPU window (DEC-1093 (1)) |
| 20 | DEC-1037's query-wrapper removal line (found by ADR-0002's review, F17) | DEC-1037 says a W2-20 or W2-121 KPI line tracks it | **DONE 11-09**: W2-20's line (`19b9ce4b`), ollama.py in its paths |

## 0b. DEC-1098's items (2026-11-09)
| # | item | fate (DEC-1098) | state |
|---|---|---|---|
| 21 | W2-88's lines for the memory standard | (1) a package to the owner: the standard built at Wave 0, proven with the repository's own tuning set and a fresh verdict set, once | ANSWERED 11-09 (DEC-1099 (2)); next: the lines into W2-88 (marked), its allowed paths, the nonexistent-id ticket filed |
| 22 | P-SELECT-GRAPH's three cheaper fixes | (2)(b) proposals: test-map couplings; W2-66's record-only case always run; a scoped selection on every commit outside a ticket touching settings, the registry or the test map | DONE 11-09: answered by DEC-1100; its work tracked in rows 37-40 |
| 23 | the code route confirmed | (2)(b) its figures on the 138 and the 80 (callers questions; where it supplied the gold) | **DONE 11-09** (`P-SELECT-FIXES-1.md` §6: first gold by code for 9 of 12 callers on the 138, 3 of 8 on the 80; ~2 % of bundle items) |
| 24 | W2-130's sitting applied | (3) A-G, H1 (b) (open and in-progress tickets; KPI 4 changed), H2 | **DONE 11-09** (`c4420040`; audit READY; gov links 2204 -> 1973). Rows to D-6 part 2: the 29 test-fixture ids now flagged ENFORCES_SUPERSEDED (made-up ids; the check to skip test fixtures), the loader's 8 wrong pairs, MR-1..MR-6 regenerated from contract.yaml |
| 25 | the sandbox-and-guard experiment | (4) the design package to the owner first; then run; both results before W2-56 builds | **Design to the owner 11-09** (`SANDBOX-GUARD-EXP-1.md`); WAITS: the owner's answers (§7, ten), then a declaration, then the run |
| 26 | ADR-0002 re-read | (5) at the lift's re-pin | WAITS: the lift's re-pin |
| 49 | the lift's re-pin ACT carries | W2-136, W2-137, W2-138, W2-141 (+ its hook), W2-142 (+ the `.claude/` skill copies), W2-145 (watcher retired), W2-147, W2-20 | WAITS: W2-20, then D-10 and the owner's word |
| 27 | the work in order | (6) item 8; Q07/Q14; W2-139/W2-140; the sitting; D-5, D-6 part 2; D-10 on the owner's word; the lift | IN PROGRESS 11-09 |

## 0c. DEC-1099's items (2026-11-09)
| # | item | fate (DEC-1099) | state |
|---|---|---|---|
| 28 | the sandbox experiment's seal | (1) Q6: a path-map entry sealing the held-out halves, an ACT for the operator | DONE 11-09: applied inside ACT-INDEP-WALLS-1 (`147706ae`) |
| 29 | the sandbox experiment run | (1) beside D-10; brake at twice the projection; both results to the owner before W2-56 builds | WAITS: the seal, the labellers, D-10's window |
| 30 | W2-56 | DEC-1112 (1): builds on the path-map guard alone; DEC-1114 (1): S8's reach and S10 to Wave 3 | IN PROGRESS: READY 11-09 (`befa57695`, accept 260/0/0, review READY round 1); merged on DEC-1114 (row 79); next: R3 and R5 follow-ups, then the close at the lift |
| 31 | W2-88's lines and paths | (2) S10-S17 and three failure lines into W2-88 (marked DEC-1099), the set tools and the practice record in its allowed paths; EXAMIN's copy the first full run | **DONE 11-09** (`663fa278`, `e0811c67`; W2-88 waits on W2-145 once the W2-137 cycle was broken) |
| 32 | the nonexistent-id ticket | (2)(6) filed now, tests first | **Filed 11-09**: W2-146 `DAEO-f6x3` (`cbbe9733`); next: its test designer |
| 33 | W2-82 after W2-27 | (3) its order changed (marked DEC-1099) | **DONE 11-09** (`75b88b22`; gov plan: W2-27 batch 14, W2-82 batch 15) |
| 34 | G1's fewer scored pairs | (3) after EXAMIN's copy | WAITS: EXAMIN's copy |
| 35 | W2-15a with W2-32 | (3) closed together at the lift | Noted in P1-13 (`741faf90`); WAITS: the lift |
| 36 | W2-139 and W2-140 | (3) merged before D-10, closed at the lift | **MERGED 11-09** (see 63) |

## 0d. DEC-1100's items (2026-11-09)
| # | item | fate (DEC-1100) | state |
|---|---|---|---|
| 37 | ACT-SELECT-FIXES-1 | (1) the test-map couplings and W2-66's record-only case always run; an ACT for the operator | **APPLIED 11-09** by the operator (`8038e0ee`); WAITS: the owner on D-4's 3 capped and 7 lifted cases |
| 38 | W2-66c | (1) tests first, pins (i) and (ii) | Filed `DAEO-btcs` (`28b4b5ba`); its test designer next |
| 39 | the scoped selection's hook line | (2)-(3) trigger (a), one line in the reference-transaction hook, an ACT for the operator; in the CTO's tools first | **APPLIED 11-09** (the hook line, 12:14); first run refused by a missing folder (fixed); the re-run RED 13 of 2,841: W1-06 (known), test_fusion (W2-137's cap, now on D-10's list), 11 reranker-service cases that pass in the main tree (the selection's environment: a row to fix in `landing_select.sh`); a regression case for the folder; row to W2-116 (GIT_DIR) |
| 41 | `gov plan`'s cycle break (DEC-1102) | fixed before the lift's re-pin, tests first | **MERGED 11-09** W2-147 (`7ed72a1e`, review READY, accept 25/25); live at the lift's re-pin |
| 40 | (iii) into W2-115 | (4) once proven in use; widen the trigger if an emergency merge reds again | WAITS: proven in use |

## 0e. DEC-1101's items (2026-11-09; standing)
| # | item | fate (DEC-1101) | state |
|---|---|---|---|
| 42 | the walls ACT | (3) path map, guard and the folders' settings for the automated sessions, one ACT, rehearsed | **DONE 11-09**: applied by the operator (`147706ae`); W2-56's worktree merged; walls_check.py repo PASS (245 run, 0 failed) |
| 43 | the launch script | (3) tests first, one review | WAITS: the ACT's design |
| 44 | the fixed briefs and their package | (3) writer, checker, auditor, labeller, to the owner with set size, walls, costs, home tickets, W2-88's lines, the first audit's date | WAITS: the script |
| 45 | the periodic audit | (1) every two weeks while active, monthly once stable; the regression pool | WAITS: 42-44 |
| 46 | the weekly counts | (1) "not found" and "may be incomplete" from agents' returns, in the digest | NOT STARTED |
| 47 | unindexed-path notices | (1) resolved within a day | STANDING (from now) |
| 48 | the sandbox labellers automated | (2) DEC-1099 (1) Q5 by the automated sessions | IN PROGRESS (the experiment's prep told) |

## 0f. DEC-1103's items (2026-11-09)
| # | item | fate (DEC-1103) | state |
|---|---|---|---|
| 50 | W2-20's gate file | (1) an ACT: `gov resources --init-config` from W2-20's code, rehearsed, exact commands | **APPLIED twice 11-09**: ACT-GATE-CONFIG-1 (`d7490945`), then ACT-GATE-CONFIG-2 for W2-20's frozen format (`0fcd02b0`, 52e32fc1…); W2-20 round 3 running |
| 51 | D-4's ten cases back in the gates | (2) an ACT, rehearsed (DEC-1061 amended) | **APPLIED 11-09** form B (`a46d4517`); D-10 decides the three red by design (W1-33 auditor, W1-05 install, W1-46 research install) |
| 53 | the landing selection's environment | DEC-1104 (3): fixed before its results are relied on | **DONE 11-09**: a short temporary folder (the socket path under 107 bytes); 49/49 tests incl. the folder regression; the re-run shows only W1-06 and test_fusion (D-10's list) |
| 52 | the operator-agent package | (4) classes (a)/(b), who classifies, how a misclassification is caught | APPROVED (DEC-1104 (2)); next: build it, tests first, one review, a replay trial on past ACTs |

## 0g. DEC-1105 and DEC-1106 (2026-11-09)
| # | item | fate | state |
|---|---|---|---|
| 55 | W2-20's exception round | DEC-1105: S16 per-CPU; R2-F1 resampled; one narrow review; then merge, `--sample` a working day, `--remeasure` | **MERGED 11-09** (`686c594f`, review READY, accept 170/170, S16 passed twice per CPU). The sample day WAITS the first working day after the lift's re-pin: `--sample` records only sessions registered through W2-20's launcher (none until it is live); tool ready: `tools/resources_sample_day.sh`. Rows: R3-F1 (a runner child's exit reads as null once; fold its two-line fix into the next W2-20 touch, DEC-802), R3-F2 |
| 56 | W2-148's exception round | DEC-1106 (1): F15 (restore only its own change; else refuse, hold, P1) | **MERGED 11-09** (`511a4a17`, review READY, accept 166/166); F21 fixed and merged (DEC-1107, review READY, accept 169/169) |
| 57 | the guard's call log | DEC-1106 (2): an ACT, rehearsed (hash, role, decision; no contents) | **APPLIED 11-09** (`b7a373cf`; the hook a7981319); the first day's file validates PASS; W2-56's worktree merged |
| 59 | W2-148's replay corpus | DEC-1108 (2) | **MERGED 11-09** (see 68) |
| 60 | the live-hook suites' temporary folder | DEC-1108 (5): GOV_GUARD_CALLS_DIR set in the suites (W2-141's acceptance file by its designer) | NOT STARTED (follow-up) |
| 61 | the tuner's hidden log | DEC-1108 (4): ~/.gov-os/guard-calls in W2-56's tuner's hidden paths | WAITS: a fresh experiment window |
| 58 | ACT-OPERATOR-1 | DEC-1106 (3)-(5), DEC-1109 (1): the install, rule 2d, the freeze, F26, the cron | **APPLIED 11-09** (`2a646265`; APPROVED 157a9dc0; the crontab loaded by stdin after Debian's path cut; apply.sh fixed `babf768e`); queue empty; nothing queued until an eligible (a) ACT (not path-map until the replay builder) |

## 0h. DEC-1109's items (2026-11-09; item 3 standing)
| # | item | state |
|---|---|---|
| 62 | ACT-OPERATOR-1: the operator brief's change, hashes and APPROVED rebuilt, the affected cases re-run, a new message | **DONE 11-09** (`0240833b`, `5f7641e6`); applied `2a646265` |
| 63 | W2-139 and W2-140, one batch, before D-10 | **MERGED 11-09** (one batch; accept 160/160; review READY); close at the lift; the queue run sets GOV_TESTS_OPTIN=breadth,lifted |
| 64 | D-5 (the templates) | IN PROGRESS: W2-128 rounds 1, 2a and 2b, W2-152 (with its tests' fix) and W2-153 merged (`27ab8f88d`, 11-10; accept W2-153 51/51, W2-128 121/121, W2-56 292/0/4); ACT-CLAUDE-COPIES-1 applied (`eb48fe2fd`); TPL-6's Appendix A done; next: ACT-CLAUDE-COPIES-2 (the six agents, round 2b's two skills) built and reviewed, then the owner's yes; TEMPLATES-APPROVAL-1 refreshed for one approval; the CAP-38.b row |
| 65 | D-6 part 2 (with its rows) | **MERGED 11-09**: A-F, then F2 (`757cf3109` W2-129 S18, `336828354` W2-55 S9, merged together; accept W2-129 156/0, W2-55 55 with the 3 backfill base reds on D-10's list); D-6 part 2 complete; a Wave 3 row: gov links counts an entry marked if its status line names the changer anywhere |
| 66 | the sandbox experiment | DEC-1112 (1): set-up A fully beside D-10; set-up B a Wave 3 row | WAITS: ACT-W2-149-INSTALL-1 (row 75: the owner's yes, then the operator by hand); the wiring merged 11-10 (`7f0e71519`, row 86); the seeds' amendment A5 recorded (`4fd701aba`); next: the declaration's pin amendment A6 after the operator's commit (text drafted: `drafts/w2-149-sgx/PIN-AMENDMENT-A6.md`), then set-up A's corpus, writers, labels, tuning and held-out run beside D-10 |
| 67 | the launch script for the independent sessions, tests first | **MERGED 11-09** W2-149 (`b4de529b`, accept 77/77, review READY round 2) |
| 74 | ACT-SETS-GLOBS-1 | the hidden globs for a new set's hidden/, the checker's notes, an audit's miss classes (W2-149's F2; delegated tightening); F11 judged | **APPLIED 11-09** by the owner's operator (`9cce7430d`; hook 74f8dbea4761, map 44f99ea563cb; check 8 → 12 ms); the live check cases PASS (385 run, 0 failed; R skipped, planted only); next: the helpers merge integrate into their worktrees at a safe point |
| 75 | W2-149's install ACT | the launch script installed with its approved list (the five set-up A briefs, the operator agent's two) | WAITS: the CTO's ping for the owner's `yes ACT-W2-149-INSTALL-1 0edc1eb9`: rebuilt 11-10 on the merged wiring (`7f0e71519`; the list's two template lines `kinds.yaml`, `tree-exclude.txt` changed), rehearsed 0 failures (set-up A's five briefs pass stage 10 and build dry walls), review READY round 1 (F31-F35 carried as text); next: the CTO decides whether the wiring's F18-F23 are fixed before the yes (a rebuild) or after it, then the owner's yes, then the operator by hand (§5) |
| 77 | W2-149's F11 follow-up | the launch script passes `--setting-sources project` (defence in depth; delegated), tests first | **MERGED 11-10** (`ff1865184`; accept 78/0/3; the live S9, S11, S12 3/3; review READY, rows F16, F17); F11's stated reason to correct when next touched (F16: `--restricted` already ignores the user settings) |
| 78 | W2-141's hook rebuilt on the new hook | its staged change (docs/changes/W2-141-hook/) rebuilt on top of ACT-SETS-GLOBS-1's hook before the lift's re-pin ACT | **DONE 11-10** in `beec1f2f8`: staged `pretooluse.py` = live `74f8dbea4761` + `"Glob"` in G-14's tools (`e7e1c4ce66d6`; the first copy was made from `bd545af83198`, not `97a84e770058`, so as it stood it would have taken out ACT-INDEP-WALLS-1, -GUARD-CALLLOG-1, -OPERATOR-1 and -SETS-GLOBS-1); `role_reads.py`'s copy stands (live unchanged); unit 204/204 (no test changed), `gov accept W2-141` 184/0/0; rehearsal (`drafts/w2-141-rebase/`, planted HOME, 0 failures): sets_globs_check 573/0, walls 331/0, guard4 501/0 before and after; replay 48 h 14,569 calls: 0 changed under DAEO-sdxk, under DAEO-xwro 29 allow→deny, all W2-141's S1/S2 (engineer Grep 23, `grep -r` 6), 0 deny→allow; review READY by verdict.py (`reviews/W2-141-rebase-review.md`), F1–F4 and D1 rows in the ticket; the D-10 restage engineer's `9536ea954` (`w2/W2-141-d10`) is byte for byte the same change; next (re-pin ACT): `drafts/g14/test_g14.py`'s four engineer near-miss cases (searches from above) are W2-141's intended refusals: revise them or expect them red (F2) |
| 76 | ACT-OPERATOR-2 | the operator agent re-installed to carry the replay check (`a170641e`) | WAITS: the owner's operator by hand (class (O), no yes line; ready `d3e3017a5`, review READY, live check ready 00:52Z 11-10); `acts/replay/` made; the first path-map ACT through the agent after 2026-11-11 20:02Z (the Monitor call in the window) |
| 68 | the replay set builder (DEC-1108 (2)) | IN PROGRESS: merged 11-09 (`a170641e`); next: ACT-OPERATOR-2 re-installs the agent to carry it; WAITS: the call log's 48 h of history (about 11-11 18:16Z) before path-map ACTs go through the agent |
| 69 | D-10's red-fix list ready (W1-06, test_fusion, the three red-by-design cases; then FORECAST-W2-2 row 11's five and the CTO's additions, DEC-1109 (2), DEC-1112 (3)) | READY 11-10 (the helper's part; others' items named): MERGED, each review READY: W1-06 `dddf54782`, test_fusion `56a1a554c`, core.bare `384b2245b`, W1-19 and W2-54 shared_gpu `e43d66d07`, W2-92 `6e904ced2`, W2-55 `df7c67292`, W2-54 one-answer `54ab0528c`, W1-19 reranker `c570a4cc0`, validator `18cc289a6`/`6129d96cd`/`9f9809e09`, W1-33 launcher `cfe4ed605`, W2-96 reaping `f7e63ae4e`, launcher open gate `e74b551bc`; the three cases decided (DEC-1111); W1-28/W1-50 whole-tree `f2e05e303`; READY for D-10's word but for others' items: the CTO: W1-32's command lists (brief, links, plan), W2-66's schemas case (DEC-105, (a)), W2-134's KPI prose; W2-56's designer: W2-116 6 and W1-32 7; trace W2-58's 5 live-session cases (`LIFT-1/D10-REDS.md` §6); 11-10's seven items MERGED (W2-66 `7b14fed34`, W2-116/W1-32 `9a1b21cf1`, command lists `fb4b7a05d`/`c3bf5a547`, W2-58 `2d4cc60f2`, W2-13 `89495ad15`, W2-134 `7ffe6f89c`, maps `8b31965ed`, probes `327f63e55`/`26726eb52`); next: the CTO's choice on the serial phase's W1-16 ui_off entry (a probable D-10 blocker, D10-REDS §6.4) |

## 0i. DEC-1110's items (2026-11-09)
| # | item | state |
|---|---|---|
| 70 | the standing-rules list at the top of the prompt and in START-NEXT-SESSION §2 | **DONE 11-09** |
| 71 | the stop-hook check against idling, an ACT for the operator, rehearsed | **APPLIED 11-09** (`115be191`; review READY round 2); live at the fresh session's start |
| 72 | a fresh CTO session after the seven helpers report, before D-10, the handover to the 11-08 standard | WAITS: the seven helpers |
| 73 | after the lift, ready lists covering several of gov plan's batches | STANDING (from the lift) |

## 0j. DEC-1114's items (2026-11-09)
| # | item | state |
|---|---|---|
| 79 | W2-56 merged without S8's reach and S10 | **MERGED 11-09** in `cf23e9f8d` (that commit's subject is W2-153's review: a helper's commit took the CTO's staged merge); checked after on integrate: `gov accept W2-56` 256/0/4 (the real cases skip without the opt-in), launch units 182/182 |
| 80 | W3-P28: ranked search for sandboxed workers without opening every Unix socket | DONE (parked) 11-09: `docs/plan/WAVE_3_PARKING.md` W3-P28; a ticket in Wave 3 |
| 81 | W2-56's review rows R1-R6 | IN PROGRESS: R3 and R5 **MERGED 11-10** (`4bc040898`; review READY round 1; accept 292/4 with the real cases, the 4 the sandboxed real cases' relative PYTHONPATH and the gate; S2, S9, S13 pass alone); R6 parked as W3-P29 (DONE); next: R1 to W2-60a's rows; R2, R4 and the follow-up review's F2, F3 for W2-56's close review; S7's real case re-run alone when the gate is open; W2-05's fresh probe (probe_impact flags `src/gov/codeintel/__init__.py`, docstring only) |
| 82 | FORECAST-W2-2: the re-estimate at today's measured pace beside the lead-hour method | **DONE 11-09**: `packages/FORECAST-W2-2.md`, sent to the owner |

## 0k. DEC-1115's items (2026-11-09; item 4 standing until the lift)
| # | item | state |
|---|---|---|
| 83 | ACT-CLAUDE-COPIES-1 by the operator agent, its first live run | **APPLIED 11-10** by the operator agent (`eb48fe2fd`, 00:10Z; class (b); the owner's yes read from the CTO transcript, 00:02:59Z, logged in act-approvals.jsonl); 19 files; structural pass all 10 families ok, portability ok; next: R3 (worktrees merge integrate), W2-153's merge, ACT-CLAUDE-COPIES-2 |
| 84 | TPL-6's Appendix A cut to the pointer | **DONE 11-09** (this commit) |
| 85 | past 80 % of the week's usage before the lift, only the lift's critical path runs | STANDING until the lift (rule 6); usage 33 % at 22:41 11-09 |

## 0l. Delegated follow-ups (2026-11-10; DEC-1112 (3))
| # | item | state |
|---|---|---|
| 86 | W2-149's set-up A wiring (stage 10's front matter from the walls' template, the briefs' bytes unchanged; the labellers' rounds, the auditor's inputs and delivery, the scorer's names, the declaration's overlap rule; `indep-briefs/**` in tree-exclude.txt first), tests first; then the install ACT rebuilt and the declaration's pin amendment proposed | **MERGED 11-10** in `7f0e71519` (the seeds ruled (2), A5 `4fd701aba`; tests first, the engineer, review READY round 1; `gov accept W2-149` pass 146/0/3, live 3 passed); rows F18-F30 in W2-149's file; next: the CTO's call on F18-F23 (each changes the script; before the install ACT's yes it rebuilds the ACT), the pin amendment A6 (row 66) |
| 87 | the replay check's follow-ups (ACT-OPERATOR-2 §8): the log's cover of the window in code (F7); calls that name the sets root re-judged (F6); the builder writing a normalised call as a dropped line with the log's sha256; `--setting-sources` and `-B`/backup checks at the next re-install | NOT STARTED: rows for W2-148's code and the CTO's builder; until then the CTO queues no path-map or deny-list ACT before 2026-11-11 20:02Z and no sets_root_hidden addition to the agent |
| 88 | the lift's re-pin ACT: what it must carry from W2-141's rebuild (`beec1f2f8`) | NOT STARTED (at the lift): revise or expect red the four engineer near-miss cases in `drafts/g14/test_g14.py` (S1/S2 refuse them by design); re-run `drafts/w2-141-rebase/rehearse.sh` with the candidate pin (review F4); fold F1 and F3 into the README; `w2/W2-141-d10` not merged (its content is on integrate); D1 (a git diff of two blob refs falsely refused) a row |
| 89 | the test-design skill's five remaining CAP-38.b citations (Inputs and "Writing acceptance tests", lines 24-26, 38-39; W2-128 round 2b review F1, out of scope there) re-cited to CAP-38.c | NOT STARTED: a W2-128 round 2c (the designer's guard revision, then product-spec, one review), a 1.2.1 delta after the templates' approval; its copies with the next copies ACT |
| 90 | ACT-CLAUDE-COPIES-2: the six agents from W2-153's composed sources and round 2b's two skills | **APPLIED 11-10** by the operator agent (`2059048f2`, 11:30Z; class (b); the owner's yes 11:20:53Z); structural pass all 10 families ok, portability ok; next: the portability reds re-run (the D-10 helper) |
| 91 | W1-46's two argv-tail cases after W2-153 (the D-10 helper's find): the order is W2-153's intent (the CTO, DEC-1112 (3)), cases revised under DEC-866 | **READY to merge**: `w2/W2-153-tests` `23f63f49eccc` (W1-46 0 failed, 122 passed; all four rows pass by node id); review READY (`reviews/w2-153-w1-46.md`) |
| 92 | the folded acceptance runs (DEC-1061's one row per case) can hide reds in later rows: a ticket that changes behaviour a case's later rows exercise runs them by node id or with the opt-in before calling them green (W2-153 W1-46 review F2) | NOT STARTED: a Wave 3 or process row; the CTO's briefs to name the opt-in run for launcher, guard and template changes meanwhile |
| 93 | the six-field agents and W1-38's builder (the D-10 helper's find after ACT-2; the CTO, DEC-1112 (3)): the composed agent carries the kernel role file's body after the role template's (`portability.compose()`, shared with the ACT builder); W1-38's builder copies `templates/` | **MERGED** `13f15785f` (designer `9a6f55c5af7b`, engineer `3cf6c4951`, review READY `reviews/w2-153-s3-amended.md`); the approved templates unchanged |
| 94 | ACT-CLAUDE-COPIES-3: the six agents recomposed | **READY for the owner's yes** (manifest `7368f4f2`, 6 files, class (b), rehearsed twice with 0 failures, review READY); with it applied in a clone: W1-33 112, W1-38 42, W2-05 30, W2-57 19 passed |
| 95 | W1-46's two argument-order cases (D10-REDS §6 item 16) | **DONE** before the listing: `23f63f49eccc` merged; with the opt-ins both files pass, 49 of 49; D10-REDS item 16 stale |
| 96 | rows from the S3 and ACT-3 reviews: a missing role template is reported against the role file alone (S3 review F1); the designer's S3 case copies W1-33's `fields()` instead of importing it (F2); the copies builder's check should come from the touched list, as a `sha256sum -c` of the after hashes (ACT-3 review F1) | NOT STARTED: small; the builder's check is the CTO's tool, at the next copies ACT |

## 1. Every item not done, partly done or waiting

### 1a. Overdue: should already have happened by its own terms

| DEC-n (item) | What was decided | State | Next step | Trigger / when |
|---|---|---|---|---|
| DEC-1084 (ACT-GUARD-SETS-1 (1)-(4)); DEC-1082 (3) | Guard refuses the hidden sets to six measured roles and `transcripts/**`; apply right after window 4; live worktrees merge the same day | NOT DONE. Tools converted 11-06 (`sets_form.py`); patch stale (`apply.sh check` exit 1 on 11-08) | Engineer rebuilds the patch against today's hook and path map, adds `runs/fresh-80/`; rehearse; review; operator applies | Was due 11-07 14:22 (window 4). Must be done before the 80 |
| DEC-1093 (2) | W2-141 (`DAEO-xwro`): guard refuses an engineer's wide search into its own acceptance folder; built beside the experiments | NOT DONE. Ticket open, not started. Stopgap in place: exclusion line in EMG-common and LEAD-w2-common | Test designer, then engineer, then one review. Goes live with the guard ACT at the lift | Experiments ended 11-07 23:03. Must be ready before the lift's re-pin |
| DEC-1090 (4) | G3 (overlapping slices) decided after E0, using the 138's figures | NOT DONE. E0 finished 11-07 16:33; still undecided | Bring the owner a one-line choice. FRESH-80-READINESS §6 recommends no change before the 80, a ticket after the lift | Due since E0 |
| DEC-1094 (1) | Reranker saturated: CTO brings the "fewer scored pairs per search" option after E3-E5 | NOT DONE. G1-PROFILE names the lever; it was never put to the owner as an option | Put the option to the owner, noting that any ranking change voids the 80's verdict (READINESS §4) | Due since E3-E5 (11-07) |
| DEC-1088 (5)(b) | W2-20 gains the launch-refusal line (every session, recorded override); lands with W2-136 | PARTLY. Line added to W2-20's KPIs (`DAEO-r30l`:49). W2-20 is not rebuilt (branch from 10-17) and not merged. W2-136 merged 11-07 without it | Rebuild W2-20 to the new line plus W2-136's F2 entry criterion; review; merge | Should have landed with W2-136. Both go live at the lift |
| DEC-1074 (7), LINK-INTEGRITY §7; DEC-1073 (2), (5)(a) | W2-130 cleanup right after window 4: the marks patch (87 first), the `sources:` patch, the 110-decision reconciliation list to the owner | NOT DONE. W2-130 (`DAEO-q8cl`) open, not started | Start W2-130's marks patch and the auditor's check. Prepare a proposal per id for the 150-id sitting | Was due right after window 4 (11-07) |
| DEC-1062 | P-SELECT-GRAPH: research replays two weeks of merges in D-9; result to the owner before anything is built | NOT DONE. P1-PLAN lists D-9 as "mostly done", with this trial left | Brief a research agent (CPU only, no GPU) | D-9's own step; D-9 otherwise finished |
| DEC-1061 (4) | W2-84's hidden-half cases (opt-in) deleted with the guard's hidden-half rule at D-9 | NOT DONE. Still in `tests/optin-lifted-guard.txt`:435-437 and `tests/unit/guard/test_w2_84_trees.py` | Decide together with ACT-GUARD-SETS-1's rebuild; a test designer deletes them | D-9 |
| DEC-1048 (5) / DEC-1046 (1) | Follow-up after W2-112 lands: no private reranker beside the shared service in the product (KPI change) | NOT DONE. In no ticket. W2-112's KPI still falls back to a private reranker. Interim `rerank_service_slot_hold.py` remains | File the follow-up ticket (or a W2-112 line marked with its DEC), tests first | W2-112 landed (D-1, then window 4) |
| DEC-1048 (3) | P-LB-PRODUCT-1 (Load Balancer KPI lines in W2-121 and W2-20) decided after the investigation | NOT DONE. Never brought back. W2-121 and W2-20 carry no balancer line | Bring P-LB-PRODUCT-1 to the owner again, or fold it into the three-layer plan | Investigation finished 11-02/03 |
| DEC-1070 (13), restated DEC-1074 (8) | Q07 and Q14 re-worded to stable facts by an independent session | NOT DONE. Only marked volatile (DEC-1069, `00ef8222`). CHECKPOINT:422 says "not yet done" | Independent session re-words them; old copies go to `retired/` | "Next in line on CPU" since 11-05 |
| DEC-1074 (8) | The visible 40's category shortfalls fixed | NOT DONE | Independent writer fills the shortfall categories, or the owner drops the item | Open since 11-05 |
| DEC-1087 (6), DEC-1079 (standing block) | Status block correct (DEC-948) | PARTLY. Block in use, but it counts K9 as done from stale tags (K7-W2-REMAINDER §5) | Fix `status_block.py`'s keystone source or keep K9's state by hand | Found 11-07 15:10 |

### 1b. Waiting on a trigger

| DEC-n (item) | What was decided | State | Next step | Trigger / when |
|---|---|---|---|---|
| DEC-1092 (4), DEC-1085 (7), DEC-1083 (2) | The owner decides the fresh 80's configuration and the K9 bar before the 80 runs | Package FRESH-80-1 ready. Owner holding (11-08) | Owner reads FRESH-80-READINESS and decides §5's seven questions | Owner's word (held) |
| DEC-1087 (12), DEC-1085 (3) | M3's (two-reranker) adoption decided after all the experiments | M3-ADOPTION-1 ready; keeping the 0.6B is recommended | Owner decides §6 | Owner's word (held) |
| DEC-1096 (2), (3), (5) | Glossary built and refreshed with the store, used by every agent; package beside the test | Test done (E2G: worse, 122 against 128). GLOSSARY-1 ready, parking recommended. W2-143 and W2-144 proposed, NOT filed. W2-88's line not added | Owner decides §9. If built: file W2-143/144 and add W2-88's Wave-0 line | Owner's word (held) |
| FRESH-80-1 §2 items 14-19, §2 (checker) | Fresh-80 scripts (one-shot, resume, silent-failure, citation check); staleness pass by the owner's checker | NOT BUILT / NOT RUN. Proposals, not yet decided | Build and review once the owner decides; checker's brief in READINESS §2 | After the owner's FRESH-80 decision; before the 80 |
| READINESS §5 (proposal) | Seven-reviewer readiness review of memory before the 80 | Proposed, not decided | Owner says yes or no | Owner's word |
| DEC-1093 (1) | W2-139 + W2-140 (Contract 4.3) merge and close in one batch on one green run, outside an experiment window | Filed, not started. CTO holds them until after the 80 (owner to confirm) | Owner confirms the hold. Then test designer (W2-140), then apply (W2-139) | After the fresh 80 |
| DEC-1093 (3) | ADR-0002 refreshed by product-spec, one independent review, then the owner accepts it | NOT STARTED. ADR still PROPOSED, unchanged since 10-10 | Brief product-spec; independent review; to the owner | Due now (experiments done). Deadline: the lift's re-pin |
| DEC-1094 (2)(3) | W2-142 (`DAEO-qskx`): the two kernel skills carry search-again | Filed, not started | Tests first, build, review | Built before the lift. Live at the lift's re-pin |
| DEC-1088 (4), DEC-1090 (2)(3), DEC-1095 (1), DEC-1093 (2), DEC-1094 (3) | W2-136 (+W2-20), W2-137 (cap 64), W2-138, W2-141 (guard ACT), W2-142 live at the lift's re-pin | W2-136, W2-137 and W2-138 merged, not live. W2-20, W2-141 and W2-142 not built | The lift's re-pin ACT carries them all, plus the guard ACT for W2-141 | The lift's re-pin |
| DEC-1052 (templates, READY/DONE by code), DEC-1083 (W2-128 ready check), DEC-1088 (3), DEC-1094 (4), DEC-1073 (5)(c), DEC-1059 rows, DEC-1057 item 9, DEC-1074 (8) MR row | D-5: TPL-1..8 and W2-128 (ready check refuses missing fields, `reads:`/`needs:`/`waits_on:`, the search-again line, link lines, D5-ROWS 1-17, lead brief rebuilt, MR-1..MR-6 row) | D-5 started 11-06. W2-128 open, lines placed in the ticket, not built | Product-spec and CTO finish TPL-*. Owner approves the templates and the `.claude/` copies ACT and TPL-6's Appendix A | D-5. Before the lift |
| DEC-1083 (5) | W2-132 split from W2-128 | Not split (by design) | Split when W2-128 is reached | W2-128 starts |
| DEC-1079 (D-6), LINK-INTEGRITY §7 (D-6) | D-6 part 2: E-2's coupling edges, `retrieve.py`/`measure.py`, `gov links` code and test findings | Not started | Engineers, beside D-5 | After the experiments (now). Before D-10 |
| DEC-1049 (1), DEC-1050 (5), DEC-1052 (plan) | Full suite only on the refactored repo, on the owner's word (D-10) | Not started | Owner's word for D-10 | After D-5 and D-6 |
| DEC-1061 (2) | Opt-in suite `lifted` runs once, report-only; reds filed to the home tickets | Not run | Run in D-10's window | D-10 |
| DEC-1074 (8), DEC-1083 | `core.bare`'s tests half (a CIT-P) on D-10's red-fix list | Listed in P1-PLAN D-10 | Fix in D-10 | D-10 |
| DEC-1083 (7), DEC-1084 (3) | W1-01b closes at D-10's green run; W2-66b a D-10 red-fix item; W2-90c's run after W2-105 and W2-110 merge | Open / in progress | Do them in D-10 | D-10 green run; W2-105 + W2-110 merged |
| DEC-1084 (2), P1-13 | W2-55 closes formally (S1 re-worded: done); the 21 merged-not-closed tickets close | W2-55 `in_progress`; no `gov close` in the emergency | Formal closes | At the lift |
| DEC-1089 (2)(a), DEC-1090 (5) | First numbered, frozen, hash-checked release cut after the lift's re-pin, before W2-81's run (W2-27) | Not cut | Owner cuts it (DEC-772); CTO prepares it in W2-27 | After the lift's re-pin |
| DEC-1087 (13) | Three-layer plan (streams, capacity, RAM, how the trial is measured) to the owner as a package | Not started | CTO drafts it | Straight after the lift |
| DEC-1052 (basis standing practice) | D-11: flag symptoms from the logs; a weekly basis review with costs | Not started | Build the weekly review and the symptom flag | After the lift |
| DEC-1072 (2) | The memory-building practice (W2-88 record) becomes a kernel skill | Record kept current (11-08 edit uncommitted) | Kernel skill via W2-88 / CAP-33 | After the refactoring |
| DEC-1052 (Option A) | Product switches (G-4..G-6) as re-scoped tickets after the resume, with their own scoped tests | Not re-scoped | Re-scope in the three-layer plan | After the lift |
| DEC-1055 (5) | W2-15a/W2-15b's other corpora, the scale probe and the GPU-vs-CPU study with W2-88 | Not started (W2-15b out of K9) | Plan it with W2-88 | After the lift |
| DEC-1051 (2) | Stopped work resumes where it stopped (W2-42a's pair, the home of DEC-1082 (3) and G-14's lines per DEC-1083 (9)) | W2-42a `in_progress`, stopped | Restart under the three layers | After the lift |
| DEC-1084 (spill floor) | 2,048 MiB, re-read in a week | Set 11-06 | Re-read the dispatcher's spill readings | About 11-13 |
| DEC-1094 (2)(6) | Search-again adoption count, weekly in the digest, never a gate | Script not written (about 40 lines) | Write the read-only count in the CTO's tools | Two weeks after 11-07 (about 11-21), then weekly |
| DEC-1074 (7) O2 | The owner decides the 150 ids in one sitting, with a CTO proposal per id | No proposal yet (waits on W2-130) | W2-130's list, then the sitting | After W2-130 (overdue, above) |
| DEC-1070 (14), DEC-1076 (5), DEC-1078 (4) | Labels audited on a schedule; rubric v3 (missing-alternative R7 item, source-family rule); the tuning sets' extra-source check at the next audit | Rule recorded, no date or cadence set. RUBRIC.md still version 2. Family code done (W2-134) | Set the audit cadence. Write rubric v3 before the next audit | No trigger set: needs one |

### 1c. Superseded (no action)
- DEC-1066 (2): replaced by DEC-1067 (a). DEC-1066 (6) (measure 4): overtaken by DEC-1070, DEC-1071 and DEC-1074.
- DEC-1067 (d), (e) (the morning's reranker and embedder choice): replaced by DEC-1068 and DEC-1070.
- DEC-1069 (12) (all three candidates in turn): replaced by DEC-1070 (1), then DEC-1076 and DEC-1079 (mxbai dropped).
- DEC-1068 (b) and DEC-1069 (13)'s embedder trial: deferred by DEC-1079 (d) ("L7 later") and DEC-1085 (4) ("no 4B
  embedder for now"). No trigger is set.
- DEC-1071 (4) (all three rerankers on three sets): replaced by DEC-1076 (3)-(4) and DEC-1079 (a).

### 1d. Open, with no DEC behind it (found on the way)
- `drafts/d4b/live_window.sh` and `score_once_window.sh` still have the F1 restore defect that was fixed in
  `e4_window.sh`. Do not reuse them until they are fixed.
- E0b's 246 seed conflicts (affect the harness only) and W2-138's F1 (a store built from a dirty tree) are rows.
- FRESH-80-READINESS proposes a verdict-transfer check at the release commit (§4). Not decided.

## 2. OVERDUE (the ACT-GUARD-SETS-1 kind)
1. **ACT-GUARD-SETS-1** (DEC-1084, DEC-1082 (3)): due right after window 4 (11-07). Not applied; patch stale. Must be done before the 80.
2. **W2-141** (DEC-1093 (2)): to be built beside the experiments, which ended 11-07. Not started.
3. **G3, overlapping slices** (DEC-1090 (4)): to be decided after E0 (11-07 16:33). Still undecided.
4. **G1's "fewer scored pairs" option** (DEC-1094 (1)): to be brought after E3-E5. Never brought.
5. **W2-20's launch line** (DEC-1088 (5)(b)): to land with W2-136. W2-136 merged without it; W2-20 not rebuilt.
6. **W2-130 link cleanup + the 110-decision reconciliation list** (DEC-1074 (7), DEC-1073 (2), (5)(a); LINK-INTEGRITY §7): due right after window 4. Not started.
7. **P-SELECT-GRAPH trial** (DEC-1062): a D-9 step. Not run, though D-9 is otherwise done.
8. **W2-84's hidden-half cases deleted** (DEC-1061 (4)): due at D-9. Still present.
9. **No private reranker beside the shared service** (DEC-1048 (5) / DEC-1046 (1)): a follow-up due after W2-112 landed. Not placed in any ticket.
10. **P-LB-PRODUCT-1** (DEC-1048 (3)): to be decided after the investigation (finished 11-03). Never brought back.
11. **Q07 and Q14 re-worded to stable facts** (DEC-1070 (13), DEC-1074 (8)), and **the visible 40's category shortfalls** (DEC-1074 (8)): open since 11-05.
12. **Status block counts K9 as done** from stale tags (DEC-1087 (6) / DEC-948): found 11-07. Not fixed.

## 3. Count
Action items checked: 251. Done: 193. Not done or partly done: 15 (12 overdue entries in §2, plus ADR-0002 due now and the untriggered label-audit cadence with rubric v3). Waiting on a trigger: 36 (owner's word 6, before the lift 9, at or after the lift or D-10 15, dated 2, other 4). Superseded: 7.
