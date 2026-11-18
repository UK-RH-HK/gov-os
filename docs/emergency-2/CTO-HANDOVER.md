# CTO handover (the CTO session 10cfb730, 2026-11-18, evening)

Read `docs/emergency-2/EMERGENCY-2.md` first. This page is the state at the handover and what comes next. DEC-1211,
DEC-1212 and DEC-1213 are in force.

## 1. Waits on the owner
- Nothing on the decisions page: the owner decided all of it on 2026-11-18 evening, DEC-1214 (his page:
  `docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md`; DEC-974 and DEC-027 superseded). Proposals he asked for are
  in 4 (L2's command list, T2's escalation rubric).
- The owner sent the EXAMIN CTO his answers himself, with `gov update` from the CTO's note; the CTO's E3 addendum is
  beside it: `/home/usain/gov-os-runs/W2-27/examin/.gov-runtime/scratch/govos/ADDENDUM-WAVE0-2026-11-18.md`.

## 2. Done on 2026-11-18
- **Release 0.1.3** (the owner): tag v0.1.3 on 116aa23cd, C = 1d4e6a875a5d, re-pinned (pin-1d4e6a875a5d live,
  pin-9ef5cba29c94 kept), registry 6712cc9d8, pushed by the owner. Steps: `docs/emergency-2/release-0.1.3/`.
- **The morning's reds** (full suite 08:03: 89 failed, 26 errors): four Sonnet leads (`reds-records`, `reds-launch`,
  `reds-memory`, `reds-followup`, $10.66 together) and two test designers fixed all but W2-49's; landed (8bf76809a,
  3118cc4fa, 24564e6d7, d1fb2c8b6, 94a9e1c86). The CTO: the role files' launch line (76073838d), the release folders in
  the path map (4c7bdc77d). Briefs: `docs/emergency-2/briefs/REDS-COMMON.md`, `LEAD-reds-*.md`.
- **DEC-1213 / Contract 4.4:** CAP-44.m applied from W2-192 CIT-P Part B (1a7fa2bf0); W2-192 closes it; W2-49's CIT-E
  case checks v4.2's own change. W2-49, W1-48, W2-51, W2-130, W2-198, W1-08, W2-91, W1-01 on the merged tree: 427 passed.
  The validator's two CIT-P checks PASS; its three other FAILs (wave2-tickets, CAP-22.c delivered, cited-by-tests) were
  red before. Left for G5: the other 275 capability records still say 4.3; DEC-1200 is not in CONTRACT_v4.md's
  `decisions:`; no SOURCE_MAP row for CAP-44.m.
- **The full suite on C** (15:30): 6 failed, 20,490 passed: W2-49's five (now fixed by 4.4) and W2-45 S1's `gov check`
  over its 60 s under `-n 8` (passes alone in 15 s). No full suite has run since Contract 4.4 landed.
- **The load rule (the owner: keep the load inside the gate of 20).** Cause of the 104.6 the EXAMIN CTO saw at 01:40:
  the night's leads ran pytest outside the heavy slot (`-n 6` each, unconfined) on top of the slot runs (51 to 194 in
  eight minutes). The CTO's own unconfined `-n 8` full suites reached 54 today. Now: `heavy_slot.sh` admits an outer run
  only under a 1-minute load of 12 (`START_BELOW`, nested runs exempt), each slot 4 workers (`heavy_slots.conf`:
  SLOTS=2, WORKERS=4); LEAD-COMMON says so. The CTO's full suite goes through the slot too:
  `heavy_slot.sh --held 1,2 python3 -m pytest tests -n 4 ...` (no lock taken, so the cases that call the slot
  themselves cannot deadlock), only while no lead runs; check `lead-mem.jsonl` afterwards for samples over 20.

## 3. Running at the handover
- Nothing of the CTO's. Wednesday's building points were spent at 21:00 (78 %); Thursday has 4 (budget `log/budget.md`).
- EXAMIN: the EXAMIN CTO runs `gov update` to 0.1.3, then step 5 (the owner's order).
- The shared reranker runs from the new pin (started by the first search).
- **Known red on w2/integrate:** W2-130's two pinned-pairs cases (DEC-1214's `Changes:` marks), first item below.

## 4. Next, in order (DEC-1214 applied; no approval per ticket for this list, K2 (c))
1. **W2-130 for good (T):** the two cases accept any drift pair whose later decision is recorded as the owner's
   (`Decided-by: owner`), instead of a pinned set; one test designer.
2. **Green base, NIGHT (c):** land the done work as a batch, run the full suite through the slot rule (2 above), fix
   every red to green. Make that run with `python3 -m gov.close.nightly w2/integrate --root .` by hand (not scheduled)
   so its green writes `docs/close/nightly/NR-*.json`, the base `select.scoped` reads. Then map what places nothing and
   move Gov OS's landing onto `gov queue`. The scheduled nightly and the morning brief come back when a morning is green.
3. **M1 (c), a feature:** retire `gov context`, the module too; the close inside the landing records the decisions from
   the ticket's sources; every caller replaced by something tested (audit 2 lists them); no ceiling. Test designer
   first, then engineer.
4. **L2, a proposal to the owner first:** the landing and the close as one deterministic action (the landing writes the
   close record); a table of every `gov` command: stays, merges, retires, on practical, fast, cheap, quality, records
   kept, nothing duplicated (audit 1 and `gov --help`). Then build it.
5. **K1 in code:** audit 4's Table 3 with audit 09's models (Sonnet for leads, helpers, C2 including auditors; C3 and the
   CTO on Opus) in the role files' `Launch by criticality` lines and the launcher; W2-33/W2-184 follow (T).
6. **G1 and G2:** bundle the six worktrees' unique commits and tar the live scratch tools (outside the tree); an archive
   branch and the tag `pre-emergency-2` (the tag push is the owner's); then `git rm` the retired code, tests, ACT
   bundles and prompts (audit 5's list), with the suites green after; `origin/record/w2` no more syncing, its worktree
   removed. Memory's index cleaned of them before the fresh 80.
7. **G4 then G5 (product-spec):** apply audit 8's 33 groups (the CTO settles the 48 doubtful rows), archive the old
   register read-only out of the index; then Charter v6 and Contract v5 in one change from audit 7's tables, with G6,
   L3, M1, CAP-31's no-repair-ticket, CAP-44.m's leftovers (the 275 records at 4.3, DEC-1200 in `decisions:`, the source
   map); to the owner by group.
8. **T2:** a push for a CTO stall and for every owner decision the CTO needs (features, specs, KPIs, data and
   measurement, P1 touching the core or kernel); review the escalation rubric against it and propose a change.
9. **G7:** the CTO approves and records every install (the tool registry), sudo the owner's: one line in the kernel
   text (CLAUDE.md/AGENTS.md, the CTO's call, §3.5) and the registry's form.
10. **The first fresh 80 for Gov OS** after 6's index clean (reserve points); then run-time tool slices 2 to 4, the
    proving run (Sonnet), the release acceptance. **G3** (the size audit) after the refactoring.
11. Small, Wave 3 unless friction: five modules whose git calls inherit `GIT_*` (AR-2 rows 78, 80, 86, 87, 90); AR-2
    rows 19-21 name retired guard files; W1-07's `RECORDED_GOV_COMMANDS`; load-timed cases (W2-45 S1, W2-13 latency,
    W1-07 timeouts); from the old handover: W2-195's launch refusal or a brief flag, gov brief's retrieval time limit,
    the memory line in CLAUDE.md/AGENTS.md and the skills (audit 2 M5, M6), gov adapters' held-out Read deny rules and
    the indep-walls hook, the W2-155 branch and E2-finish-base worktree after bundling.

## How to run things without false reds (learned today)
- Absolute `PYTHONPATH` (tests start `gov` in subprocesses); node on PATH for openspec
  (`/home/usain/.nvm/versions/node/v22.23.3/bin`); rebuild the main tree's store at HEAD (`gov rebuild --root .`,
  about a minute, through the slot) before a full suite, or W2-54's context check is red; W1-35 and W2-185 collected in
  one run clash on `conftest`; W1-30 alone takes about 33 minutes.
