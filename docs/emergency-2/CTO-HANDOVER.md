# CTO handover (the CTO session 10cfb730, 2026-11-18, evening)

Read `docs/emergency-2/EMERGENCY-2.md` first. This page is the state at the handover and what comes next. DEC-1211,
DEC-1212 and DEC-1213 are in force.

## 1. Waits on the owner
- The decision page `docs/emergency-2/audits/DECISIONS-FOR-THE-OWNER.md`: the owner answers it himself, line by line
  (his word, 2026-11-18). Open: L3, M1, K1, K2, G1-G7, E1-E3, Q-UPD, Q-CLOSE; L1, L2, T1-T3 to confirm (built on the
  working assumptions). Q-CAP44 is answered (DEC-1213). Record each answer as it comes, one register entry per message.
- The EXAMIN CTO's input box held an unsent line of the owner's at 20:45 ("A, as you recommend; S1-S7 as recommended
  too"); the CTO did not type into that session (see 3).

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
- Nothing of the CTO's: no lead, no suite.
- **EXAMIN:** the owner asked the CTO to tell the EXAMIN CTO to run `gov update`. Its instructions are written:
  `/home/usain/gov-os-runs/W2-27/examin/.gov-runtime/scratch/govos/FROM-GOVOS-CTO-2026-11-18-update.md` (with the
  CTO's read-only `--check`: 0.1.0 → 0.1.3, no conflicts, 33 updated, 2 added, 2 removed, 1 merged). Not yet delivered:
  the session's input box held the owner's unsent line. Deliver it once that line is sent (tmux `examin-cto`:
  "Read .gov-runtime/scratch/govos/FROM-GOVOS-CTO-2026-11-18-update.md and follow it").
- The shared reranker runs from the new pin (pid 83090, started 20:32 by the first search; a search reranks 40).

## 4. Next, in order
1. The owner's decisions as they come; the EXAMIN `gov update` and its report.
2. A green night: `python3 -m gov.close.nightly w2/integrate --root .` writes `docs/close/nightly/NR-*.json` (the
   first green base since 29 October), through the slot's rule above; then map what still places nothing (hooks,
   skills) and move Gov OS's own landing onto `gov queue`.
3. The first fresh 80 for Gov OS from the reserve (JOB-20261116-17's design, `gov memaudit scan` for the hidden set).
4. Run-time tool slices 2 to 4; the proving run (Sonnet, DEC-1212); the re-baseline (G5) once the owner answers it.
5. Small, Wave 3 unless friction: five modules whose git calls inherit `GIT_*` (AR-2 rows 78, 80, 86, 87, 90); AR-2
   rows 19-21 name retired guard files; W1-07's `RECORDED_GOV_COMMANDS` lacks the commands since; load-timed cases
   (W2-45 S1, W2-13 latency, W1-07 timeouts) want event waits.
6. From the old handover, still open: W2-195's launch refusal or a gov brief flag; gov brief's retrieval time limit;
   the memory line in CLAUDE.md/AGENTS.md and the other skills (audit 2 M5, M6); gov adapters' held-out Read deny rules
   and the indep-walls hook; the W2-155 branch and the E2-finish-base worktree after bundling.

## How to run things without false reds (learned today)
- Absolute `PYTHONPATH` (tests start `gov` in subprocesses); node on PATH for openspec
  (`/home/usain/.nvm/versions/node/v22.23.3/bin`); rebuild the main tree's store at HEAD (`gov rebuild --root .`,
  about a minute, through the slot) before a full suite, or W2-54's context check is red; W1-35 and W2-185 collected in
  one run clash on `conftest`; W1-30 alone takes about 33 minutes.
