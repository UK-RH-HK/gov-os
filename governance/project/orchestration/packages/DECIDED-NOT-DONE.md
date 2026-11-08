# Decided but not done: DEC-1047 to DEC-1096 and the owner actions since (audit, 2026-11-08)

**Kept current by every CTO session:** read at session start; tick an item off (with its commit) when done; add every new decided item with its trigger at the moment it is decided. START-NEXT-SESSION §3 and RESUME HERE carry the short form.

Read-only audit (an independent general-purpose agent for the CTO, session `ad44f5fe`) of every numbered item in DEC-1047..DEC-1096 (`docs/DECISION_REGISTER.md` lines 12978-13846), the
OWNER_ACTION line in `log/report-state.json` and `log/status-latest.txt` (11-07 23:03), CHECKPOINT RESUME HERE,
START-NEXT-SESSION §6, P1-PLAN's status table, the packages (LIFT-1 included) and the tickets in `.tickets/`.
Evidence of done was taken from `git log w2/integrate`, the files and the tickets' status. The tree is at `1fcd6ad5`,
with the CTO's uncommitted edits of 11-08 (START-NEXT-SESSION, DECISIONS-IN-FORCE, P1-PLAN, W2-88 record,
FRESH-80-READINESS). Nothing under `~/gov-os-eval/` and no question file was opened.

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
