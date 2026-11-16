# Summary: the waves, planned against delivered (2026-11-16, at 64af03362 to 7d6c2b5a5)

A summary, not a plan. Sources: `.tickets/*.md` (wbs_id and status, counted 2026-11-16 19:2x), `docs/plan/`
(WAVE_1_WBS.md, WAVE_2_LIST.md, WAVE_2_REVISED_PLAN.md, WAVE_3_PARKING.md), the register (DEC-1201, DEC-1202,
DEC-1209), `status_block.py`, the CTO's CHECKPOINT, and the EXAMIN CTO's approved Wave 0 brief
(`governance/project/orchestration/packages/EXAMIN-CTO-wave0-brief.approved-2ec48c78.md`).

## Wave 1
- **Delivered:** 51 W1 tickets, all closed (planned in `docs/plan/WAVE_1_WBS.md`; the exit record in `docs/plan/wave-1-exit/`).

## Wave 2
- **Scope:** DEC-1201 set Wave 2 to Gov OS's own work: 182 tickets after moving 10 to Wave 3 and 4 to EXAMIN's Wave 0;
  W2-193, W2-194 (DEC-1203) and W2-195 (DEC-1204) were added since: **185**. W2-196 was filed and withdrawn the same
  afternoon (DEC-1208, DEC-1209 (1)).
- **Delivered:** 170 closed (the status block's "2 merged-not-closed" are W2-145 and W2-155, waiting on their closes).
- **In progress (8):** W2-81 (the adoption proving ground: the exit proof's full re-run on 0.1.1, DEC-1202; 5 of 6
  adopters handed off, secret-history held), W2-145 (no private reranker; merged, close pending), W2-155 (the warm
  query path; merged, close pending), W2-156 (the runaway brake; built, stopped before review), W2-186 (the reranker
  reaching sandboxed workers; built, stopped before review), W2-191 (any project-relative test target; stopped before
  review round 2), W2-192 (stage AS, the spec audit; built, accept 30/30, returned with a path case and its CIT-P),
  W2-195 (the judging-work skill; the engineer finishing).
- **Not started (7):** W2-00 (the coordination record), W2-46 (the exit run), W2-47 (the exit audit), W2-82 (a
  Definition of Ready), W2-15b (EXP-003 pass 2, now measured on a fresh 80 end to end, DEC-1210), W2-193 (gov close's
  harness in an adopted repository, F-028), W2-194 (absent reds against the base; scoped mode, F-030/F-031).
- **Expected dates (estimates made before the emergency; the emergency holds all of them):** Wave 2's close about
  2026-11-22, or about 2026-11-25 if the memory figure comes back NOT_READY. The emergency (DEC-1209, 17:26) stopped
  new leads and workers until the owner decides from these reports; no date is current.

## Wave 3 (the list)
- **Moved from Wave 2 (status deferred, 10):** W2-17 gov update; W2-18 pinned install; W2-19 language-agnostic test
  commands; W2-34 gov readiness --generate; W2-35 the UX readiness row; W2-36 gov discover; W2-42 guard: missing role,
  links, late paths, atomic saves; W2-115b gov queue (the product's merge queue); W2-121c gov dispatch part c (health);
  W2-121d gov dispatch part d (watch and launch lead).
- **The parking list (`docs/plan/WAVE_3_PARKING.md`, 45 rows):** W3-P01 to W3-P35 (ideas and hardening; W3-P28 and
  W3-P30 retired) and the rows of the tickets above. Highest on the list: W3-P09, hierarchical orchestration trialled
  on EXAMIN (the owner, 2026-10-29). Read the file for each row's source.
- **Wave 3 rows from today's reviews (not yet in the parking file):** the box's accepted holes W1-W19
  (P-BOX-EXCEPTION-1), the guard's crafted forms (GF-7, GF-8, GF-9 round findings: deletes and sudo spellings the guard
  cannot resolve, push in loops, `_patchy`'s `-L`), (A-full) the agent-to-agent layer (DEC-1195, DND 249).

## EXAMIN's Wave 0 (moved out of Wave 2: W2-27 to W2-30, DEC-1201)
- **The plan (the approved brief 2ec48c78, section 3):** 1. the target layout under Gov OS's path map; 2. the full
  audit of every file and folder (with MA's assessment and A3's proposals); 3. the spec audit (built, partly built or
  not built, gaps as questions to the owner); 4. an independent check of the dispositions by a fresh auditor; 5. the
  refactor (characterization tests first, then changes with KPI lines), then the merge back into EXAMIN APP.
- **Where it is:** steps 1 and 2 done (the layout approved by the owner in the app, path map 57429b5; the audit
  table 2b096ca, report 21; the trial data copied by JOB-20261116-05 and audited, ed08f69: 13 items placed for the
  owner's approval, the product suite 73 reds cleared and 0 new). W2-27's adoption run was closed by the owner's word
  with exa-g6db as a named exception (DEC-1203 (3)).
- **Under the emergency (DEC-1209 (5)):** no Gov OS ticket loop (no new tickets, no LITE cycles); the audit and the
  refactor go on as direct work, tests kept green, each change recorded, reporting to the owner in the app.
