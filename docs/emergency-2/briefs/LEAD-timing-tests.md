# Lead brief: timing-tests, the timing cases that fail under the release suite's own load (I-32; DEC-1251 D-03: (b) now, then (a)); fixes under W2-112 (DAEO-clon), W2-13 (DAEO-zqvn), W1-19 (DAEO-t6hf)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`.

## Why
It took six full release suites to get two green ones for 0.1.6 and 0.1.7; each red run but one failed on a timing case that
passes alone (I-32, I-30): `tests/acceptance/W2-112/test_w2_112_slots.py::test_with_both_slots_held_before_any_service_the_search_goes_on_unranked_with_no_model_loaded`
(7.6 s against 4 s + 3 s), and W2-13's and W1-19's warm-latency cases, red in every busy run. G2 accepts only a green record of the
exact commit. The owner (D-03 (a), his note): "Use (b) to carry the next release until (a) lands." Read FINDINGS I-30 and I-32
(`docs/emergency-2/integration/FINDINGS.md`) and the evidence `docs/close/nightly/NR-20261125T171029Z-3d039a8fb6d3.json` if present
(else the release log under `docs/emergency-2/release-0.1.7/`).

## What (K-lines as `## Fix:` sections in the three tickets; the CTO approves them by this brief)
- **TT-1 (b), first and alone:** every case that asserts a time bound and is not yet listed runs alone in the serial phase:
  `tests/acceptance/serial-only.txt` gains an entry `<node id>  # serial: latency: <reason in words>` for the W2-112 case above and
  for each W2-13 and W1-19 case that asserts a time bound (find them by reading those folders; W2-13's ranked lexical case is listed
  already). First find and name (file:line) the code that reads `serial-only.txt` in **the release suite's** full run (the full
  regression record `gov release --patch` needs, P-2/T-8; the nightly's runner and `gov close`'s plugin both read it, per the file's
  head; confirm which runs the release suite). Verify: the release runner's collection on a planted list leaves the entry out of its
  parallel phase and runs it once in the serial phase. **Commit TT-1 by itself first** so the CTO can land it ahead of the rest.
- **TT-2 (a):** each of those cases measures against the machine's reading instead of a fixed wall-clock bound: either the reading
  is planted (the case injects the load or the clock it judges by) or its bound scales with the load the case observes (state the
  formula and its floor; a real slow-down of 2x on an idle machine must still fail). Then the entries of TT-1 for these cases may
  stay (serial costs minutes) or go: decide, and say why.
- Failure lines: a planted 2x slow-down on an idle reading still fails each case; a planted busy reading (load over the gate) no
  longer fails a case whose own work took its idle time.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-timing-tests`, branch `e2/timing-tests` from `w2/integrate`. Code area:
`tests/acceptance/serial-only.txt`, `tests/acceptance/W2-112/`, `tests/acceptance/W2-13/`, `tests/acceptance/W1-19/` (all the
independent test designer's: only it edits them, DEC-1243 (2)), their three ticket files, and a test-support helper if TT-2 needs one.
`src/` only if TT-2 cannot be done in the tests, and then only a small injectable reading; name the file first in your return.
Others work meanwhile in `src/gov/release/`, `src/gov/memaudit/`, and the bundle-b merges (W2-207, W2-204, W2-208 folders): do not edit those.

## Green
TT-1 and TT-2 red on the base where they can be (a guard where a case must stay green, marked so); the three folders green alone
through the heavy slot; then exactly the impact-selected suites for your branch (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main
queue DAEO-clon=e2/timing-tests --onto w2/integrate --select`), run through the heavy slot. Check the trailers (LEAD-COMMON): every
commit touching `tests/acceptance/` is the test designer's.

## Return
Branch and head; TT-1's commit (its own hash) and the release runner's reader (file:line); each case changed and how (planted or
scaled, the formula); the selected run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: the spec, KPIs and existing test patterns, for the test designer you start; uncut)
store: c1e81afd3e75 (/home/usain/Dynamic-Agentic-Engineering-OS), store behind HEAD, head 763d18528026, 32 stale path(s)
{
  "store": {
    "commit": "c1e81afd3e7560e7a8f769bb51de083b07d72158",
    "head": "763d18528026573bae99bb7ac906d8377532ff62",
    "stale": [
      ".claude/agents/orchestrator.md",
      ".claude/templates/role-cto.md",
      ".rulesync/subagents/orchestrator.md",
      ".tickets/DAEO-d3sr.md",
      ".tickets/DAEO-esl1.md",
      ".tickets/DAEO-j9z6.md",
      ".tickets/DAEO-l2b2.md",
      "docs/DECISION_REGISTER.md",
      "docs/checkpoints/DAEO-sdxk/CP-DAEO-sdxk-3337.md",
      "docs/emergency-2/CTO-HANDOVER.md",
      "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "docs/emergency-2/briefs/LEAD-bundle-b.md",
      "docs/emergency-2/briefs/PRODUCT-CTO-HANDOVER-METHOD.md",
      "docs/emergency-2/integration/FINDINGS.md",
      "governance/project/orchestration/tools/start_cto.sh",
      "governance/project/test-map.yaml",
      "src/gov/_shipped/template/governance/kernel/templates/role-cto.md",
      "src/gov/close/select.py",
      "src/gov/queue/command.py",
      "src/gov/queue/dry.py",
      "template/.rulesync/subagents/orchestrator.md",
      "template/governance/kernel/roles/orchestrator.md",
      "template/governance/kernel/templates/role-cto.md",
      "tests/acceptance/W2-115b/README.md",
      "tests/acceptance/W2-115b/test_w2_115b_sel.py",
      "tests/acceptance/W2-115b/test_w2_115b_unwritten_paths.py",
      "tests/acceptance/W2-115b/w2_115b_sel_support.py",
      "tests/acceptance/W2-206/README.md",
      "tests/acceptance/W2-206/test_w2_206_sel4.py",
      "tests/unit/queue/test_queue_select_sel.py",
      "tests/unit/queue/test_queue_select_unwritten.py",
      "tests/unit/queue/test_queue_w2_206_flags.py"
    ],
    "root": "/home/usain/Dynamic-Agentic-Engineering-OS"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-zqvn",
      "sha256": "7772341d478f1badf525136c02e2ebc869eb0a813cc7fc2b2428e6a86c33db72",
      "path": ".tickets/DAEO-zqvn.md",
      "start_line": 110,
      "end_line": 116,
      "text": "**DEC-1066 (3) placed here (CTO, 2026-11-03):** S6 added (W2-13 owns the keyword index): `lexical.py` takes every tracked file today (no exclusion list); the path map gains `lexical_policy`.\n\n**S6 (CTO, 2026-11-03, P2):** `src/gov/rebuild/command.py` added: the rebuild's report names the files the keyword index kept out (one line, as S5's command.py). S6's two repository cases turn green with D-7's path-map marking (the CTO's), right after W2-13 merges.\n\n**D9-FATES (DEC-1083):** Close formally at the lift (DEC-1083), lines met: all 8: `8550788b` (S1 to S4, F1, F2; FULL review READY), `9ed83413` (S5), `261d6415` and `27a80411` (S6); `W2-13-evidence.md`. The CTO closes it at the lift (P1-13).\n\n- **Open (D-10's red-fix list, 2026-11-10):** `test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget` is red alone with the real models: warm p95 0.543 s starting at load 2, 0.560 and 0.578 s at load 12 (budget 0.5 s, W1-19's, unchanged). Routed to the nightly by `tests/acceptance/serial-only.txt` (`89495ad15`, DEC-889 item 5); the latency itself is this ticket's to find and fix.\n",
      "chunk_id": "eaf48b7585143f7748068347",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-clon",
      "sha256": "780fa23ceeff24bc1457761dea7b355efd5c98998de17143bc92742467b29e5e",
      "path": ".tickets/DAEO-clon.md",
      "start_line": 46,
      "end_line": 61,
      "text": "- DEC-374\n- DEC-397\n- DEC-1032\n- DEC-1033\n- DEC-1036\n- DEC-1048\n- DEC-1068\n- ADR-0002\n- DEC-1034\nest_loc: 200\nacceptance_tests:\n  path: tests/acceptance/W2-112/\n  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); concurrency, the killed service, and the matching answers on planted texts\ntrack: B\nlist_rows: []\n---\n",
      "chunk_id": "fe5430468e7ed1f5f3877c75",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "2a5ef9c7184bab3399a64bc5",
      "sha256": "6f1622690d8a914309fb4b41058070d3d838eb290e1795e2cbdc457becd4b4c0",
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "start_line": 158,
      "end_line": 182,
      "text": "    \"title\": \"Timing tests that fail under the release suite's own load: how should the release gate treat them?\",\n    \"found\": [\n     \"It took six full release suites to get two green ones; each red run but one failed on a case that passes alone.\",\n     \"I-30 (the gate's null CPU reading) is fixed. I-32: W2-112's slot case took 7.6 s against 7 s; W2-13 and W1-19's warm-latency cases are red in every busy run.\",\n     \"G2 accepts only a green record of the exact commit.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Fix the timing cases: measure against the machine's reading (planted, or a bound scaled by observed load), in 0.1.9\",\n      \"A fix lead (size S to M); the release suite stays strict.\",\n      1\n     ],\n     [\n      \"b\",\n      \"Run the timing cases alone in the suite's serial phase\",\n      \"The suite runs a few minutes longer; no code change to the cases.\"\n     ],\n     [\n      \"c\",\n      \"Let the gate accept a case that fails once and passes on an immediate re-run, recorded as flaky\",\n      \"Fastest; a real slow-down could pass once as a flake.\"\n     ]\n    ],\n    \"reason\": \"It removes the cause; (b) can carry the next release until (a) lands.\",\n",
      "chunk_id": "2a5ef9c7184bab3399a64bc5",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e8af619d745672fbe61d57b1",
      "sha256": "7bf0a25914a17293e7212c071c9754910f3dfcadd2c40acca42ea1e582ade403",
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "start_line": 1086,
      "end_line": 1129,
      "text": "#### W2-57 Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry (FULL, independent-test-designer then engineer; DEC-813, DEC-823, DEC-883 item 5, DEC-889 item 5, DEC-892 item 2; lens I's P-IS-6)\n- **Why:**\n  - The serial phase takes about 31 minutes of every close, and most refused closes since 2026-10-20 came from listed cases or load-caused reds.\n  - The rulesync probe's 10-second limit turns load into reds, greens and a silent skip of up to 181 W1-38 cases. That is a live fail-open (I4 F2).\n  - **This card replaces DEC-813's KPI.** That KPI had W1-46's live cases pass under the close's parallel load; DEC-889 item 5 moves live and real-model tests to the nightly instead (I2 F14).\n- **Starts** in a free slot after the review point, the probe first (DEC-892 item 2). It **closes** before W2-24 starts (DEC-813).\n- **Allowed paths (widened, I2 F12):**\n  - `src/gov/adapters/portability.py` and `src/gov/doctor/command.py` (the probes only);\n  - `src/gov/close/serial.py` (new: the serial phase and its reasons);\n  - `tests/acceptance/serial-only.txt`;\n  - W1-30's r11 and r13 files;\n  - `tests/acceptance/W1-38/**`, `W1-07/**`, `W1-46/**`, `W1-50/**`, `W1-02/**`;\n  - W1-33's `w1_33_support.py`;\n  - `tests/acceptance/W2-57/**`;\n  - `tests/unit/close/test_serial*`, `tests/unit/adapters/test_portability*`;\n  - `docs/changes/W2-57-CIT-E.md`.\n- **KPIs, success:**\n  - **The probe's four effects (P-I4-5 (a)):**\n    - a limit a loaded machine meets;\n    - W1-38's fixture fails, never skips, on a timeout;\n    - the 9 cases a timeout satisfies assert the reason;\n    - W1-33's research case fails the same way;\n    - 0 rulesync skips or timeouts in three closes' worth of parallel runs.\n  - **The doctor probes:** limits a loaded machine meets, with failure text kept (W1-07 `[doctor]`).\n  - **The serial-only list reworked as P-IS-6's table:**\n    - every kept entry names its reason;\n    - W1-16's 94 non-daemon cases, W1-09's two races and W1-50's read-merge case run in parallel;\n    - the live and real-model files move to the nightly;\n    - latency cases stay alone.\n  - **Revisions:** W1-30's r11 test reads the reworked list. Also W1-30's r13 limit, W1-50's `CLAUDE*` removal (DEC-784), a p95 case for a designer's read, and W2-M332's timing without the memory sampler.\n  - **The close's resource gate** covers W1-02's 5-second bound and the guard's 20-second deadline. The network check probes through the session's route.\n  - **Then the orchestrator commits the removal** of every entry this ticket makes unnecessary (DEC-861).\n- **KPIs, failure:**\n  - a timeout that skips or passes a case;\n  - a serial entry without a reason;\n  - a live file left in the close;\n  - a case weakened, skipped or serialised by marker alone;\n  - a list entry added.\n- **Until it lands:** the close queue checks that each close's skip count equals the expected 31 (the orchestrator's interim guard).\n\n\n\n---\n\n",
      "chunk_id": "e8af619d745672fbe61d57b1",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-qvff",
      "sha256": "747316d54f26894958e5c6dc0fe12d605170f46f47531d230b43476e08656238",
      "path": ".tickets/DAEO-qvff.md",
      "start_line": 95,
      "end_line": 98,
      "text": "**Widened 2026-11-15 by the CTO (DEC-1156 (7), P-W2-111-R5-ROWS (a)):** `tests/acceptance/serial-only.txt`, so a test designer lists W2-111's five timing files as `serial: latency` (rv-3's F2: they red only inside lead_verify's parallel phase at load 10-20; alone and quiet 25/25 pass). rv-3's F1 (libyaml accepts tab and `? ` texts the pure SafeLoader refuses, so a malformed held-out.yaml no longer stops every call: fails open) is fixed in the same round by DEC-802 (engineer, product and live-hook diff, with a test-design batch giving it as a described behaviour), and F3's README line with it; then a narrow independent re-check at the new head (DEC-1154).\n\n**Widened 2026-11-15 by the owner (P-W2-111-YAML-REST (a)):** `src/gov/util/role_paths.py`. The fast YAML loader's fail-open class (rv-3's F1) also sits in the guard's other reads: `role_paths.py:85`, `:165`, `parts.py:234` and the live hook's `role_reads.py:111`, `:171` (in the diff). All are routed through the checked loader, with a planted-tab case each, before the narrow re-check; ACT-GUARD-FIX-7 and release 0.1.1 carry it.\n\n",
      "chunk_id": "6b84666a047f354ef502b3b2",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "WAVE-2-WBS",
      "sha256": "b1c8de3996f437a2ceec813f0f309938874f658782a7dfbfdf672ee86c33d081",
      "path": "docs/plan/WAVE_2_WBS.md",
      "start_line": 1097,
      "end_line": 1114,
      "text": "  - `src/gov/adapters/portability.py` and `src/gov/doctor/command.py` (the probes only);\n  - `src/gov/close/serial.py` (new: the serial phase and its reasons);\n  - `src/gov/close/command.py`, the serial phase's call to `serial.py` only (run 2, owner, DEC-925 item 3; gate (h)'s line is W2-07's round 2);\n  - run 2's test designer also: W1-19's `test_w1_19_real_models.py` (W2-M332) and W1-30's `test_w1_30_r15_policy_pairs.py` (a masked timeout) (DEC-925 item 3, delegated);\n  - KPI 6's guard deadline is left to the resource gate and the quiet window (owner, DEC-925 item 3, B2 (b));\n  - `tests/acceptance/serial-only.txt`;\n  - W1-30's r11 and r13 files;\n  - `tests/acceptance/W1-38/**`, `W1-07/**`, `W1-46/**`, `W1-50/**`, `W1-02/**`;\n  - W1-33's `w1_33_support.py`;\n  - `tests/acceptance/W2-57/**`;\n  - `tests/unit/close/test_serial*`, `tests/unit/adapters/test_portability*`;\n  - `docs/changes/W2-57-CIT-E.md`.\n- **KPIs, success:**\n  - **The probe's four effects (P-I4-5 (a)):**\n    - a limit a loaded machine meets;\n    - W1-38's fixture fails, never skips, on a timeout;\n    - the 9 cases a timeout satisfies assert the reason;\n    - W1-33's research case fails the same way;\n",
      "chunk_id": "af2537ed6a8662b928401485",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "WAVE-2-WBS",
      "sha256": "4e8a804bea2c6d334e406beddbdafb188785c8553eca3f08199444662b0e0208",
      "path": "docs/plan/WAVE_2_WBS.md",
      "start_line": 1112,
      "end_line": 1124,
      "text": "    - W1-38's fixture fails, never skips, on a timeout;\n    - the 9 cases a timeout satisfies assert the reason;\n    - W1-33's research case fails the same way;\n    - 0 rulesync skips or timeouts in three closes' worth of parallel runs.\n  - **The doctor probes:** limits a loaded machine meets, with failure text kept (W1-07 `[doctor]`).\n  - **The serial-only list reworked as P-IS-6's table:**\n    - every kept entry names its reason;\n    - W1-16's 94 non-daemon cases, W1-09's two races and W1-50's read-merge case run in parallel;\n    - the live and real-model files move to the nightly;\n    - latency cases stay alone.\n  - **Revisions:** W1-30's r11 test reads the reworked list. Also W1-30's r13 limit, W1-50's `CLAUDE*` removal (DEC-784), a p95 case for a designer's read, and W2-M332's timing without the memory sampler.\n  - **The close's resource gate** covers W1-02's 5-second bound and the guard's 20-second deadline. The network check probes through the session's route.\n  - **Then the orchestrator commits the removal** of every entry this ticket makes unnecessary (DEC-861).\n",
      "chunk_id": "1825478c313e9f852266b18a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e39bc700a8b4913e08bf64f8",
      "sha256": "5e0d172797afc31de9f31507da28a2b35d517227038c82cfe98f14264b2e9f89",
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "start_line": 210,
      "end_line": 212,
      "text": "| 5 | W2-13's real-model warm p95 (0.543-0.578 s alone, against 0.5 s) | **The existing mechanism:** `tests/acceptance/serial-only.txt` (DEC-889 item 5), whose `real-model` kind takes the `nightly` route, as W1-19's real-model file does. It is an ordinary test file, a designer's, so no ACT. The no-model latency case took the `serial` route. The 0.5 s budget is unchanged, and the latency is an open item in W2-13's file. (The path map's `load_sensitive` is a control path, and it reruns a case alone, where this one is red too.) | `89495ad15` |\n| 6 | W2-134's KPI prose \"CAP-1 never matches CAP-10\" | Reworded with its meaning kept (\"an id never matches a longer id it begins, as item 1 never matches item 10\"), marked `[changed, DEC-1112 (3)]`. The validator's `ticket-contract-ids-exist` passes; 2 FAIL left (P1-11, W2-37). | `7ffe6f89c` |\n| 7 | The stale probes of W2-05 and W2-96 | Fresh FULL probes, both pass, recorded at `docs/probes/DAEO-0z8c/PR-DAEO-0z8c-d10.md` (`327f63e55`) and `docs/probes/DAEO-ouet/PR-DAEO-ouet-d10.md` (`26726eb52`). W2-96's went stale again with item 3's merge; its second fresh probe is below. | see below |\n",
      "chunk_id": "e39bc700a8b4913e08bf64f8",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-mb2t",
      "sha256": "c193adcf8ada3e705734d2f8239c3781d26d0c00a52f840df382c3b698820cf3",
      "path": ".tickets/DAEO-mb2t.md",
      "start_line": 28,
      "end_line": 37,
      "text": "- tests/acceptance/W2-13/test_w2_13_unavailable.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-13/test_w2_13_latency.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-76/test_w2_76_timings.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-76/test_w2_76_unchanged.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-116/test_w2_116_reindex.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W1-41/test_w1_41_embedding_policy.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/rebuild/test_w2_116_integration.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/rebuild/test_no_embeddings.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/rebuild/test_w2_122_seed.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/retrieval/test_w2_32_rebuild_cut.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n",
      "chunk_id": "8039f9bea585903ffa061424",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "8f22085ddc936454a3b27444",
      "sha256": "5e4049e7b61517d5e83db80068260e677437bd33372cb55344e0116274ed4400",
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "start_line": 65,
      "end_line": 65,
      "text": "| T-6 | Real-model tests W1-19 and W1-21 in tickets' runs (27 tickets' paths hold `src/gov/retrieval/**`; also pulled in by the path-map and gitleaks-config couplings). Warm-p95 timing. The hook-latency cases (W2-111) | **Keep hit@5 and the fused/reranked route, scoped** to model-path changes, run once by the lead against the shared service. **Warm p95 to the nightly** (or a quiet measured run). Drop the path-map and gitleaks-config couplings. No private reranker in the fixture (DEC-1046). W2-111's load-failing latency cases merged into step 2's test refactor | M: W1-19 131 to 852 s and W1-21 84 to 1,061 s per run (serial). Warm p95 failed 5 of 9 runs (0.59 to 9.1 s against 0.5 s). Each run starts its own reranker. O: P-W2-112-F9-class rounds | Memory quality (hit@5 \u2265 0.80) | hit@5: yes / yes / loses work (silent recall loss). p95: not decidable under shared load | Config: test-map couplings; T-5's fix; W2-112's scope for the fixture | A1-4, D-T61 |\n",
      "chunk_id": "8f22085ddc936454a3b27444",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e24a5df87dbff42e416e34f2",
      "sha256": "01b9081ac2f0b086382ed8c8193218b0a969fce0032959f5a5a0b7c2fb2a9e65",
      "path": "docs/changes/W2-13-evidence.md",
      "start_line": 191,
      "end_line": 203,
      "text": "  behaviour, and the test designer re-pins them next (MR-3):\n  - W2-92 `test_w2_92_unchanged.py`: `test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle` `[plain]`,\n    `[batched]`, `[unknown id]`, `[ticket]`; `test_u2_todays_bundle_is_the_plain_fused_order_of_todays_routes`.\n  - W2-92 `test_w2_92_fail_closed.py`: `test_f4_a_question_naming_no_symbol_does_not_report_the_code_route_ok_or_fail`.\n  - W2-87 `test_w2_87_authority.py`: `test_2b_a_lower_chunk_better_by_more_than_the_lift_keeps_its_place`,\n    `test_3b_without_the_block_the_order_is_the_plain_fused_one`.\n  - W1-21 `test_w1_21_family_check.py`: `test_the_check_is_red_when_the_dev_tiers_fail_the_baselines` (its\n    premise, dev tiers below the 80 baseline, no longer holds: the ranked route lifts them over it).\n  - W1-19 `test_w1_19_unavailable.py`: `test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so`,\n    `test_with_the_environment_and_no_snapshot_nothing_is_reranked_nothing_is_fetched_and_nothing_raises` (their\n    reference order is built from `hits`, not `ranked`).\n\n  The other 2 are the budget gap (review R3): W2-92\n",
      "chunk_id": "e24a5df87dbff42e416e34f2",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-cy5o",
      "sha256": "0e5742f46fbca38b04248fd752bc78a7cc77e0e348f19513fc4acca4a23c3a38",
      "path": ".tickets/DAEO-cy5o.md",
      "start_line": 31,
      "end_line": 34,
      "text": "  - 'W1-30''s r11 test, which holds today''s serial entries one by one, is revised to read the reworked list and its reasons (Rewrite-Reason: DEC-889 item 5) [I2 F9]'\n  - 'W1-30''s r13 case gets a limit a loaded start meets (Rewrite-Reason: W2-M384) [I2 \u00a72.2]; W1-50''s two live freeze cases remove every CLAUDE* variable, as DEC-784 requires [I1 F-7]; one p95 case covers a test designer''s read [I1 F-10]; W2-M332 times W1-19''s queries without its memory sampler in the same process [I3 O3 (b)]'\n  - 'The close''s resource gate covers the wall-clock limits that went red under load: W1-02''s 5-second bound (168 cases), by a limit a loaded machine meets or by running them alone; the guard''s 20-second deadline is left to the resource gate (W2-20) and the quiet window, with no new serial entries (owner, DEC-925 item 3, P-W2-57-B B2 (b)) [I1 F-14]'\n  - 'Run 2 (owner, DEC-925 item 3, P-W2-57-B B1 (a)): the close''s serial phase in src/gov/close/command.py (its call to serial.py only; gate (h)''s line is W2-07''s round 2) takes only the entries not routed to the nightly, so a nightly: entry is collected and left out of both phases [DEC-889 item 5, DEC-925]'\n",
      "chunk_id": "83a7dd63dda89884f774053e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-ar89",
      "sha256": "2114c1a52017d4decef4d517bee1fdeb4ffc1917844b2da1c49cb8274cc0dbde",
      "path": ".tickets/DAEO-ar89.md",
      "start_line": 26,
      "end_line": 29,
      "text": "  - 'S2 If a simple cause is found within the time box: it is fixed, and W1-19''s and W2-13''s warm real-model cases pass at 0.5 s p95 on an idle machine, with no other case made red. Verify: where a fix is made, the run of W1-19''s and W2-13''s warm real-model cases on an idle machine prints a p95 at or under 0.5 s for each, and the scoped test run of the changed paths has no new red; where none is made, the note says no simple cause was found [DEC-1125 (1), W1-19]'\n  - 'S3 If no simple cause is found within the time box (2 lead-hours): work stops and the evidence and options go to the owner; the budget is not changed by this ticket. Verify: the lead''s checkpoint records show at most 2 lead-hours before a stop; the evidence note lists the options for the owner; the diff holds no change to the 0.5 s figure in W1-19''s or W2-13''s case [DEC-1125 (1), DEC-105]'\n  failure:\n  - 'More than the time box spent without stopping and reporting. Verify: the lead''s checkpoint records sum to at most 2 lead-hours, or a stop-and-report record exists at or before the 2 hours; work recorded past 2 hours with no report is this failure'\n",
      "chunk_id": "155da8a48bcaefb4ebfdde2a",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-ar89",
      "sha256": "40fbe41288502390d2484aec7e64aac70da840fcde3c05680a3b5f1bad55d1e6",
      "path": ".tickets/DAEO-ar89.md",
      "start_line": 25,
      "end_line": 26,
      "text": "  - 'S1 A profile of the warm real-model query path (the case of W1-19 and W2-13 that measures warm p95 with the real models) names where the time goes, stage by stage, and which retrieval changes since the budget last held added to it; the profile is kept as an evidence note in the ticket''s folder. Verify: the evidence note exists in the ticket''s folder and holds a table of the warm query''s stages with a time for each, a total, and a list of the retrieval changes since the budget last held with the time each adds [DEC-1125 (1)]'\n  - 'S2 If a simple cause is found within the time box: it is fixed, and W1-19''s and W2-13''s warm real-model cases pass at 0.5 s p95 on an idle machine, with no other case made red. Verify: where a fix is made, the run of W1-19''s and W2-13''s warm real-model cases on an idle machine prints a p95 at or under 0.5 s for each, and the scoped test run of the changed paths has no new red; where none is made, the note says no simple cause was found [DEC-1125 (1), W1-19]'\n",
      "chunk_id": "078777f7b1a60df0a3d08a14",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "W2-11-CIT-P",
      "sha256": "4d60bac0007baaf8e0f0eada29b1d692ee9ce9fbb7122b8096976083c5386a43",
      "path": "docs/changes/W2-11-CIT-P.md",
      "start_line": 219,
      "end_line": 222,
      "text": "| S15 | `skills/test-design/SKILL.md` (\"Kinds and cost\") and `test-kinds.md` (the load-sensitive row, made consistent) | A timing test measures the work under test (its process's CPU time, or its time against a quiet reference run beside it), never the wall time of a loaded machine, at the same bound | DEC-979 item 1 D2, DEC-983 |\n| W2-128's cases (P-W2-11-R6-2 (c)) | `skills/orchestration/SKILL.md` (\"Reads are open\", \"Followed by hand (Wave 2)\"); `skills/test-design/SKILL.md` (front matter, \"The work order in parallel\", \"Red against the ticket's base\") | Orchestration: the four read refusals follow \"except\", not \"apart from\"; the heading \"Followed by hand\" is the integration branch's \"Followed by hand (Wave 2)\" again (the restore had shortened it). Test-design: the read rule cites CAP-38.c; the description is the integration branch's again, word for word; the base run's worktree holds none of this ticket's implementation, not no implementation at all | DEC-820, DEC-525, DEC-963, DEC-1052, CAP-38.c |\n\nBeyond its version, `skills/orchestration/SKILL.md` changes only the reads line's \"apart from\" to \"except\" and its\n",
      "chunk_id": "9aa1d72414ec88eb307112c9",
      "routes": [
        "semantic"
      ],
      "batch": 2,
      "status": "PROPOSED",
      "in_force": false,
      "not_in_force": "PROPOSED"
    },
    {
      "id": "33ab3ad0fde50be950f43880",
      "sha256": "e58b3df07b890cefbd72c5a2f59958b30af310d448ef85202023c7af2519f68b",
      "path": "docs/changes/W2-13-evidence.md",
      "start_line": 178,
      "end_line": 192,
      "text": "  their own tree's `src` (DEC-732), so all three runs ran the head's code there. The S2 hit@5 base figure above is\n  not affected: `lexical_hit5.py` imports `gov` in its own process, with no child.\n- **The control, redone against a real checkout:** the five suites (`tests/acceptance/W2-92`, `W2-87`, `W1-21`,\n  `W1-19`, `W1-28`, `-n auto`, through `heavy_slot.sh`), run one after the other, in the worktree with its own\n  `src`, and in a `git clone` of `w2/integrate` at `7524fa04` (its `src/` and these suites the same as at\n  `5522a603dead`) with that clone's `src`:\n\n  | tree | result | reds |\n  |---|---|---|\n  | `w2/integrate` `7524fa04` | 4 failed, 369 passed | integrate's own: W1-19 `embedding_policy`, `semantic_index`, the reranker-process case; W1-28's whole-tree copy case |\n  | W2-13 head `80cdd7ff` | 17 failed, 356 passed | the same 4, plus the 13 below |\n\n- **The 13 are W2-13's, by design:** S2 changes the lexical list the fusion takes. 11 pin the old lexical\n  behaviour, and the test designer re-pins them next (MR-3):\n  - W2-92 `test_w2_92_unchanged.py`: `test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle` `[plain]`,\n",
      "chunk_id": "33ab3ad0fde50be950f43880",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-zqvn",
      "sha256": "df03ae4099109485e3ba04738918723893b0a33b052925190af521ebbed1eea7",
      "path": ".tickets/DAEO-zqvn.md",
      "start_line": 48,
      "end_line": 82,
      "text": "  - RETR-A-04's bundle is unchanged (citations, three parent expansions, stopping reason).\n  - 'The secrets filter applies to the FTS5 table as to the old index: a planted canary is never indexed.'\nprofile: FULL\nsources:\n- DEC-1109\n- DEC-889\n- DEC-725\n- DEC-900\n- DEC-1052\n- DEC-1055\n- DEC-1056\n- DEC-1063\n- DEC-1065\n- DEC-1066\n- DEC-419\n- DEC-802\n- DEC-860\nest_loc: 300\nacceptance_tests:\n  path: tests/acceptance/W2-13/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\ncloses:\n- AR-9 (RETR-X-02)\n- DEC-725\nlist_rows:\n- W2-L233\n- W2-M071\n- W2-M072\n- W2-M098\n- W2-M100\n- W2-M102\n- W2-M292\n- W2-M296\n---\n",
      "chunk_id": "89adc996618006f0244db610",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-clon",
      "sha256": "9c8f125b45764691347b687a6a4dbb6fa71f931fcc243f4bc5b4655f4dd0f741",
      "path": ".tickets/DAEO-clon.md",
      "start_line": 26,
      "end_line": 33,
      "text": "- tests/unit/status/test_status.py\n- tests/unit/retrieval/test_w2_112*\n- docs/research/W2-112-shared-reranker.md\nkpis:\n  success:\n  - 'One reranker process serves every session on the machine: the same pinned model, revision and environment as today (ADR-0002 \u00a72, DEC-397), listening on a local socket in the user''s own folder (mode 0600, no network port), started on demand by the first search that needs it under a lock (two searches starting together start one service), ending itself after a set idle time [DEC-979 item 4, P-RERANKER-1]'\n  - 'Many sessions at once: 20 concurrent searches are answered by that one process, each with its own scores for its own texts, in arrival order, with a cap on a request''s texts and a time limit per request [DEC-979 item 4]'\n  - 'The same answers: for the same inputs on the same device, the order and the scores match a private reranker''s (within float rounding; ties keep the given order), measured on the 20 visible memory questions and, after W2-61h, the 48 [DEC-979 item 4, DEC-374]'\n",
      "chunk_id": "30b6da923b1e5218df25162b",
      "routes": [
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "e1a13de52b6b34f90b57adb6",
      "sha256": "3e104207b5efc558dac15c182848f6eb2f78675829578eca581503bd1129c45e",
      "path": "docs/changes/W2-13-evidence.md",
      "start_line": 166,
      "end_line": 179,
      "text": "## The scoped run\n\n`PYTHONPATH=<tree>/src python3 .gov-runtime/scratch/orchestrator/tools/select_tests.py <tree> W2-13 DAEO-zqvn`\n(scope `scoped`, base `5522a603dead`, 90 targets), then `pytest tests <its pytest_options> -n auto -o\ntmp_path_retention_policy=failed -p no:cacheprovider` through `heavy_slot.sh`, at `3c0320080829`: 5085 passed,\n32 failed, 8 skipped, 20 errors in 1087 s, under load (`gov accept` beside it; load near 20).\n\n- **Three reds were the merge's,** in two builder tests: fixed at `06e5ae70a4a7` (above); both files then pass,\n  51 of 51.\n- **The other 29 failed and 20 errors: 13 are W2-13's (corrected after the review, R2).** A first control re-ran\n  their 18 files with `PYTHONPATH` swapped to `git archive` copies of the base's code and found the same 46. That\n  control was invalid for W2-92, W2-87, W1-21, W1-19 and W1-28: their support modules start their children with\n  their own tree's `src` (DEC-732), so all three runs ran the head's code there. The S2 hit@5 base figure above is\n  not affected: `lexical_hit5.py` imports `gov` in its own process, with no child.\n",
      "chunk_id": "e1a13de52b6b34f90b57adb6",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-zqvn",
      "sha256": "7a7148c26f719e38e6189ee50ceee1728667bc3f695cf35a5a58697c024f343d",
      "path": ".tickets/DAEO-zqvn.md",
      "start_line": 98,
      "end_line": 103,
      "text": "**Delegated (CTO, 2026-11-03, P2 under DEC-957; DEC-1057 R-8: a line here, not a register entry):** `src/gov/retrieval/retrieve.py` added to the allowed paths, so that S2's fusion takes the ranked lexical list W2-92's merged `retrieve()` now carries (one line, `answer.get(\"ranked\", answer[\"hits\"])`); D-4b (DEC-1055) finishes W2-13 on top of W2-92.\n\n**Delegated (CTO, 2026-11-03, P2; DEC-1057 R-8):** P-W2-13-R3 (a): the bundle budget bounds parent expansion only, as W1-21's approved spec DEC-419 DP-3 says (a cut of the gathered children was tried and reverted, `ea486253`/`80cdd7ff`); whether the budget should bound the whole bundle (DEC-860) is W2-32's S5, with its own tests. The 13 cases of W2-92, W2-87, W1-21 and W1-19 that W2-13's S2 and DP-3 changed were re-pinned by a test designer (`d71df8f8`). Merged as built in D-4b (`8550788b`).\n\n**DEC-1065 (2) placed here (CTO, 2026-11-03):** S5 added (W2-13 owns `gov retrieve`); the filter at `retrieve.py`'s chunk list, the matcher in a product module the hook can later reuse.\n\n",
      "chunk_id": "52b74e14def4bc261f20b05f",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 50,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "e8af619d745672fbe61d57b1",
      "parent_id": "79f9632e21a4017ae35d7919",
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "start_line": 1086,
      "end_line": 1129
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "DAEO-03ub",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-057v",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0mtg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0pyc",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0rfi",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0uhh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0z8c",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-1ahb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2azm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2bdu",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2d6f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2ds6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2gc7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2keg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2tfd",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-3r1j",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-49o5",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-4k3l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-57hm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-5j8b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-60rw",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6n5k",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6ox0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6y0x",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7r5e",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7rr2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-8lmb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-8s85",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-9nys",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-a3m2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-a3u2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-arrl",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-b6hm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-b926",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-blwa",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-btt7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-c1uz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cb2b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-csj8",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cuao",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cv58",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cy5o",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-drhj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-e82f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-e8f0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ebmh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ecac",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-egsy",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-emq1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-f58b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-fau3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-g23i",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-g87r",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-gdzh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-h2k3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ha8z",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-iw1f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-j8gn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jip3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jpr0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jsg1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-juee",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jzvg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-k4wm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-k7hz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kh9l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kia7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kiar",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kl5e",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kmcr",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-l78m",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-lrre",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-m1u3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-mb2t",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-n0wb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-neam",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-nqa2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ouet",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ozyt",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-pg6i",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-pl6k",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-qty6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-qzrq",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r30l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r8vq",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r9ss",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-rmbe",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-s694",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-s9qc",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-sdhj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-siiz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-swdu",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-t8mp",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-tgk2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ts4y",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u4oz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u5g6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-uzme",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-w19l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wahn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wbdh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wi46",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wnnz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wq2b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wudw",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-xm6l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-xxgp",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-yadm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ye2a",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zflj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zndm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zoex",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zpdj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "56d89d2c3b7d285e6a5ea471",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1vka.md",
      "chunk_id": "9f055e648b60c377fe6d09ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "f626cb5f1cd5f8dd954b06fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "571f05e2f31ce955ffe92473",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "664d72fc0dfec71366780597",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "1733c1cecd322ae0cfb840d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "b7b3f69446b5d66f3a22fce5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1vka.md",
      "chunk_id": "dd2deb62ba079b6d0650263c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1vka.md",
      "chunk_id": "8445b75518907469ed1e3c3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "45cfbf03da533c5381e9e66c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "2e6611a6919f9e95477a085a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "006ad2ddc384fdf16c4bb12b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "bc400971b8c65c2204bc91ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7y6v.md",
      "chunk_id": "b7df662427e89aebfdb64cd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "ffec9f1bb8344a1bd3f323ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7y6v.md",
      "chunk_id": "ad49962ac0cc1f745f08d571",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7y6v.md",
      "chunk_id": "6b7be7b65cd1726f301d4dbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "122f93dcf757d14a572bee93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1vka.md",
      "chunk_id": "cd5b0f43efef883e3f16971c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7y6v.md",
      "chunk_id": "bcc02c520037f9f8aef2aa94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "0fce2b011141e9bbb4af9c32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "cf235f1bce47acef83608f79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "72460c44299bb95aa9bdf656",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ar89.md",
      "chunk_id": "ff8b515f2b8d560c950f074b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "a66711c6776e34a6d20b8c5c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "e6cc350bd5020c12c0033dc1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "e867d2808a069de201f31d9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qvff.md",
      "chunk_id": "8a21c4e577547a49e2092d5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cy5o.md",
      "chunk_id": "8acd003398633f12dc4330f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "4b7b3e9d17c5058e89031dfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "a9c665e3f67dc1cb767e1c62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261116.md",
      "chunk_id": "aa38d3485795fb3cc26f7036",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "f3c510e6491ea01c771002e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "5e8e06212362d7fd54026df4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-clon.md",
      "chunk_id": "756a1e6f41b1a47ae7d21a05",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "6fa0f742788fd12d0d8e1ed8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "f6d635b3e2b3d8bc00d5f8c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "1af5e60b805ba04890d5ecc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "4f1f018c6002953eb0834b57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "968f97f5934de02194dc567c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_support.py",
      "chunk_id": "21e7a45406b0488df8d216be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "e78af241091a8ed20c1a05ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2e69abb8f8e8a3b0dbde00b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "6d43f3a0f2fd18550facebd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2ad53b6c537a997032cdee50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "f5cc48e3174ddb11b844368f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "bf04b26084bf741320459912",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qvff.md",
      "chunk_id": "5ffbef7548fa43aa5a25de8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qvff.md",
      "chunk_id": "6a3a2e0db527700e871670e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "161e6457f1af8dcea089911b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "f007adf098c7c8714ad6d6b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/README.md",
      "chunk_id": "5e7d20f4991ee71f14822803",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "223643b3916a8d9a356ece17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "a62953bc903517b189944ac8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "debe892a1ff63028d794fc07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "f97fac99f8ba254580360285",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "676a6f04c3c882eefafb6cb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "a4845c6084824dc80feca943",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "75eb4ae98b1248d3fff566d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "36eb55155ea3cd0646d10226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "db6b94a4f6a0c6a0b079234d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "52596f32d8c4af948561d4af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "52e6bece0a3935872e5e266f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "93401f4f8887c28fa5afc233",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "a9a3cdd6423d625d2a03ad2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "d268662bf817bf97ecf34402",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "759fa6c9e856384f64852c34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "a40cc78bd1eb2343e519ea3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "95640c009ccc0d1b60402a8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "37b0b788b7071778264b2d4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.b.md",
      "chunk_id": "50f65616da68125631acb1ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "2211d5b5504dc7c3b8463888",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.b.md",
      "chunk_id": "762df4427e42067ab45664c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "a159dd106c24c18ae41c4872",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "f59cf177e3f27866b03038fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-45.a.md",
      "chunk_id": "1cf25a77bd66c47342756a15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-45.a.md",
      "chunk_id": "2b1267c4180a6728ac7c6543",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "540bcc8fffba1bbfb94f0790",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ar89.md",
      "chunk_id": "29e46c52a096609885365681",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "6a0db77ff478efaf83c5f1e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/test_w1_19_real_models.py",
      "chunk_id": "9729241b2caa1d0ab35dbf82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "3bcad0f6ac59fe4fce04d639",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "a0bf78ad7d85ee4184503b87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "377a3ef7b6af11579f319d19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "f35b6ff165979596dcecdc7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "f133a7d6205f04a9c5cbe9ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "f665210f3990c211c7d96721",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "f2ff83b9c1de2b1952e36003",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "e1d1f828be4ec3a7f49b33ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "ac1061c1d3fb854294d23a4e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "4d3f30eb4feaa8ac2b1b16e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/README.md",
      "chunk_id": "de04eacbb8b59d8cb9a6109b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "e0a1a03ed4820bf89a1cf4d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "5cfd7767fab43eed267996cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "148ed5d13f7e5929447b2773",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "891861be0810d88f3c9d2927",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "a7786cfd2570f2545901340d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cy5o.md",
      "chunk_id": "e8b1d9e53506e775a7660530",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ar89.md",
      "chunk_id": "f95950327467f995c9f5bd37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "ee2efb3e8fab831035253eda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "c2b2e2596314cde6c1816441",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "b2a6a389a7c9e4ce80b633b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "5d8e6b700d825ec0a44625c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "c11feda957501de1f672da40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "77941caefa232a4420e86361",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "359e095bf5ec883a4d7beb61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "950e28ace73ee92c1bb182c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "db1c1aacb9ae5fc9f8ddf50e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "7a7db801570b4e1a1563c739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_support.py",
      "chunk_id": "6bd9590886fae390ae3a15d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ar89.md",
      "chunk_id": "56aab0eca79c2a09b1e330fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "eb15072ac692f119b49a0adf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "eb88d84ad3e86acb0052f491",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "3edc2cd3b464a8a18c489b2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "ed9a22ecab26ac4f70f75b0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "914182188f3cdc66859e4e5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2tfd.md",
      "chunk_id": "6adbb01a284979e64d277265",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "cc2c3b433b257cdf642c9141",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "210e19ccc51088f537e55254",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "9496ca58565b55cb3ecd40c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "21614d5f8f492cc1bf20a15d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-112-evidence.md",
      "chunk_id": "dd3d1f2724429ccacb6c09b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "f561dad9222054f51cbaa770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ar89.md",
      "chunk_id": "9af88b796c2f0aca917c3c4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "64736d65f8a266cda5466db1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-112-F9.md",
      "chunk_id": "83b72c0bd39bd59345a5c47f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "eeb667c5b61b8ccc685a694a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-112-shared-reranker.md",
      "chunk_id": "059ad8112d70fc5e582efb69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "3a38041f429aff9b858da3fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-145-evidence.md",
      "chunk_id": "fc08ba475b1497b109feef03",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "dc70d069f76f85a133aae886",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "228fef247583a516d63c64d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "c71d3924ee53db703859ba9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "5d9b5428298b04cb341f07e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t6hf.md",
      "chunk_id": "427d94c4609d96569cbf7bf9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "3c03f1fc4d583675d3a4eab2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "8d4ab1bbfa48dae051264f5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/test_w2_112_service.py",
      "chunk_id": "574c7fb0e18af3f97aac0ef3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "82855b0e56ad6ec31fe7afa9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "53847dc1dfa657dd6ad95c40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-112-F9.md",
      "chunk_id": "53d98c2aa2c781a9d5b696ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "83f9199df7b4c04e105c9f40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "a31f03a2f3e3f6a178d21e0b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-112-F9.md",
      "chunk_id": "07f94c5b02b0bcf505b6645f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "d0df832b198e529e3981b781",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "67f81d070bd5f5fdccbfd783",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t6hf.md",
      "chunk_id": "deb9441ebd905aee92416a05",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "0ed8402b1884f9c7c146593e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "671b83fd9115c38a03408619",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-112-F9.md",
      "chunk_id": "f13b70b82e2aa431ca3d481e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sg6x.md",
      "chunk_id": "ba65011d0b3f1ca11342ab38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "db357fc50ac5f5b61db0e026",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "f4ad52dece5ecaca1e6c8872",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "a6723c3cdf2d7a00afe557e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "ec741209bf171645eed19752",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "cf6994eb7dcab21dc8d56723",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "f3601be2a9ee92d2fbac560a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "ff8a58be95efe55177f9e840",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-112-F9.md",
      "chunk_id": "c01e1b83be3356b3b16993a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "48ca053bb7794ab0838a14ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "8957cc4c0efa0f285e598a16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qvff.md",
      "chunk_id": "8739ab9103707e3bd71faf92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "1f24e5fd8eb97e1683d75121",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "d0e96443ddcdf67df8bb7f5c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "f81fa3aae4d9cb5e343ae20c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "24f7850c5c4c74ef6d9f8db2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-112-DAEO-clon.md",
      "chunk_id": "d624d70a0e9f6060d45cf527",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2ac8a795639a9b42becebd7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "5a55561ef9ade75019f51afe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "8d21bb9638c8da643bead4c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-177-evidence.md",
      "chunk_id": "c01a2ad44033fcb11d0af3f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "46a00affb7562a1e2f59ff50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/test_w1_19_real_models.py",
      "chunk_id": "1acd8ed37a477b98144faa93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "d6f078cf6a43e5d507f9c774",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "a7f78f1e75e8a1244ff09cf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-111-MEASURE-1-R2.md",
      "chunk_id": "9ef4b055857003ddbff2a24d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "99ebea01c7a7a7f75a58e853",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "12a650f81e031e4712da67aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "36ebaa4ff84945453a078e26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "0de09af609d4567ed69086ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "5ff96c84ce208743a864e487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "52ea54d5194749c43f43dd8c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "c1331e2a8e787be381ce1039",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "10c9c40e2bd2770d69fa86be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-13-DAEO-zqvn.md",
      "chunk_id": "81209d030d3b4ff14516ab44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "f1fb482db39888819fbae542",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zqvn.md",
      "chunk_id": "a1ca4ad2eab45e0409e0087f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "4a08fb08ded622b9120eaea1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-112-shared-reranker.md",
      "chunk_id": "0f261f24af7834e01bf83358",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-112-shared-reranker.md",
      "chunk_id": "459aa3b5b7930c57ce33aedd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "906c515aa5530bd15f53e40b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "bfa67024189e9dfe87a0d68e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "d80c75c63eb2a86609f268ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "71849c394d9df4254c59e591",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "1c764288b3bd91b2f5198161",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "30e96cbfdbc99ca12dbf68c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "e60d8fb0a7ae12f36c25c922",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/README.md",
      "chunk_id": "bcf750e1759f51a6a74a2132",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "4e173d718b05c9c382a2662d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "14278ad05aaafda586d36929",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_support.py",
      "chunk_id": "c7374b32ff9b240cbf67d4d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/serial-only.txt",
      "chunk_id": "f54f711cc6c5b2f8927b211e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "80761598d539024732222620",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "4cc0f10571c4c3a675c3c00b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "a6b0d29f07cea606462d18f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "d6601761838a4782909d7abd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "fe22966cf6b7e6579271caa5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-137-evidence.md",
      "chunk_id": "5eff7ac3924c2835886d7749",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/test_w1_19_unavailable.py",
      "chunk_id": "63f6239cdcf482d7b7dda850",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "89164f3e9e83a227dc05d647",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "38947694e687ce4112e14411",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t6hf.md",
      "chunk_id": "f0d9f614c86b4c0cb0030a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/test_w1_19_unavailable.py",
      "chunk_id": "096c19493b36bbd7e5118be8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "1b9accc353857813fc0834d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "bbfbdc8ab5f70b1e17d6a2c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "63b2634029fcd77a7d49099e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "206a58a48e00e10fe4133133",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "f84f92140202ba99744a9dd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "9ce15a45c5729f8bdd860efd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "53c5e2699a0384ee9161a2dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aeb8b1da6b882f8650ed8631",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "15dbcea35085fa2a78362d6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/test_w1_19_real_models.py",
      "chunk_id": "af78dbd1a73e625ee9ae331a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "b28cca61f5576a910536c9a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "3610fd8b4bb1512b6a1c4730",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "d0a330cf72ecbf5df9f0b855",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/test_w2_13_latency.py",
      "chunk_id": "5b9d5995290971b8e5ec8113",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "3a7ab415a316af95e19d6521",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "754ed5dde478ebbd8e1c69b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "23e48ce3bba86e4645e84a6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/test_w2_13_fusion.py",
      "chunk_id": "c577302fe9f4c48954737226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A1-inventory.md",
      "chunk_id": "a3361fc93d3b3a9692392a3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-reranker-review.md",
      "chunk_id": "f2d12e2d1e9b19453f997d40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "c26450059ec20a0ff13be432",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "5b99e2728f2478bd682c0136",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "94385e1e6aeb5453ff3e8ee0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "2f2030ed85262998daba1583",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "949c58e3c94e105998b1e686",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/retrieval-w1-19-method.txt",
      "chunk_id": "64912c0974f8f4d0171de5a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "a84ae58141bd00c72dc1eee7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "76be978b0310acbf22c92649",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "14858080a533f9d2f1223c46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "b548ca547edf3aee6121b655",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "850175907058bf30de15fc19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "56f2733f9b5132424b400a62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-serial-only-1a-review.md",
      "chunk_id": "d4b6d61ae64c0d2194501040",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "7f077a6e13266f6e2b931e0b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "edf4ddde66cd993cd8461674",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "8c59d7c4840c721a08204016",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "be82ef25833c979841de3038",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "21470c857f2c87d8fb3e927a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWITCHED-OFF-1.md",
      "chunk_id": "72f6685662d76a3f3bb849d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/test-design/test-kinds.md",
      "chunk_id": "b7ef96b801c0528e94a8f308",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5emz.md",
      "chunk_id": "f310d571e8ba71e5fa66602c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "e9855ac0c4064b9d07c958d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "4aa80c65ac6a8df327140ec1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-145-evidence.md",
      "chunk_id": "68a53d1ddf20ba7583b47bd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "cb3d0c1e282fce0741e892c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "d523e27df37bfe8a186c5cfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "1b17a88ce8c993fc59443353",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-serial-only-1a-review.md",
      "chunk_id": "bdc5f172941fbf33f3650adf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "26db1781579d64437c894fd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_unchanged.py",
      "chunk_id": "e2240b3cce7ac188c6eed83f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-137-evidence.md",
      "chunk_id": "504bd51b6c77fb05f5d27293",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "6685bb6b68fd4ac575b04c5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "a6fe67e298e947aaf9076122",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A3-target-path-map.md",
      "chunk_id": "7e3d431ac1d39ca7730d1231",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-19-W2-54-review.md",
      "chunk_id": "5e4132df92bf3ebe31bb1dc8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md",
      "chunk_id": "7065545ee405cb4a5bd79005",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "fd6387249e0e1a468b26bb78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "dd12bd2d8c27ee2f4f89318b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "e3079cb0b6c6664824992bc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "0b3c6aa211f319f23cc02b11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md",
      "chunk_id": "e3b337fb8ac64501b1b4de8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "504c78bddc1f1aa2172b6be9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "2bba6eebc18a93212e6a6686",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "0da92ddb1bd476b23f84fcde",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-137.md",
      "chunk_id": "74207c08ec2c8d004b4f61cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "f8053c18142f674bc3eb708a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/RESTART-CLASSES.md",
      "chunk_id": "c8afd66ffa2cfb4b6f50bc3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9b9c1f0711d858131041f317",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1k7y.md",
      "chunk_id": "49de9f58df9ded886d301d94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/test_w1_19_real_models.py",
      "chunk_id": "b239caa7cdc8a10517e61dae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "fed8baee3d91f9620bd5ad11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "5aa53b320ec0fe4192392ee2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "0c01ec3b26e416a570221944",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "015d0b713127cbe3556710fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "eb3d78c575c1b822371a4dcb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "b8c4cc7c75613e9498f54d2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/sessions/2026-11-03-orchestrator-DAEO-sdxk.md",
      "chunk_id": "001ac1b357c57b9b922c8578",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/f-checks.md",
      "chunk_id": "13b4e5832004f3a562ab8882",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "12ff92d4cae138266f6f041f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "230e2e624aebc869d14c01b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-RERANKER-1.md",
      "chunk_id": "d124b4ddecbcf93dd719ad3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/README.md",
      "chunk_id": "6e905ccc1860b01d60d017d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "1e8f8afebd5116018e1afec7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "72a68eb311ed5a30470ef147",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "3e5104c21fdf3f3ca26a9208",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-RERANKER-1.md",
      "chunk_id": "46f719f75019a6ab6e0a792f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/README.md",
      "chunk_id": "2be669a3329d0b31faf59170",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "5035ffde31898b76d7736daf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "07188f7f011f46043ad101e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "9a32f4f1b3b497bb9df14f16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "258bf9648b548160d7192956",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/conftest.py",
      "chunk_id": "c3deabf18009de52700ce66b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "16992fd74fed3ea6bc26d2c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "66f81e8fad1a80d217eb3657",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "de0c7ade3860b287d14ad076",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A3-target-path-map.md",
      "chunk_id": "566fec3a66cc307ce18a1374",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "ddbf6d97c0c10fec1f225fb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md",
      "chunk_id": "54a8cee57c8c5b910dec597e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-clon/PR-DAEO-clon.md",
      "chunk_id": "c5c343708d800366c94cf690",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "13794b80701110145fafa3b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W1-01b-DAEO-vhad.md",
      "chunk_id": "965120b68edbd3c5bf3ef6d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "604ca38a2f91f69b634343de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "4784da605749592dcd087ff3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "331b72a11642e3a5c5f04374",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "028b658523624199bdab1954",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "5b4bb7aa6b522187a3b4bc0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "5224407897caf49d37009973",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "a83ba2a273c99cf42df94b85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "daf03bc4fb405f31634b55d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "abfa0942e30af5a13bd61100",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "4de51e372b88e350dcd27550",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "fa117f08c00e8defc5a846a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/README.md",
      "chunk_id": "8737fb714e8138c0a255d93b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "ca67f0a76724b83924f7a6f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "e6315b6bf8a4c1dfed8368d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "ccd194a17a873627b1fe7c94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "aa0e76c29142007df0982722",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "b63ed848a277184cb756b9ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "cf5e132c6d5730e1181025dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "ffe92c6a2d9bf557ecb61a38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/rerank_worker.py",
      "chunk_id": "76256f08bdffcaf35c1191a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ef079998c2224d411ba4a157",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "b8da21a5c73fb2faca07aed5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "6bce5f506aa78024573651c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c43b15573a234a0cb0a02d4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-90c-DAEO-fu3n.md",
      "chunk_id": "b3320b127e0a6101b389a2e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/fusion.py",
      "chunk_id": "822508b6032b18356b48d2c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "87451faa62b5836f7cec6dd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4dd9958136eb5f673b3c0c39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "c8a64c9bc98cb0ba044fc4d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/rerank.py",
      "chunk_id": "685668563c527aae31d5a2fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "baff8a9069051bbafd1cb739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "fb37dcf8b38f230c531470ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "eb8ebd3d5a8723dbc6787734",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/status/command.py",
      "chunk_id": "519ff20bd78441f7637f423c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "50a52dec3c812a6ac184d9ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "d73b465d60f0fd10fafde722",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-66b-DAEO-zuiy.md",
      "chunk_id": "d351a870de030e26e901bc1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-137-evidence.md",
      "chunk_id": "da5973e46dc242988a3185b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "25d48660955eb5ccb84aaab0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md",
      "chunk_id": "95cf81eeec34e0b336d5b9ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "01e1ee7b921c795bbebc2e00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "56d713949a703ede53110981",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "527c33894257b90348dabe04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "d27111e89aa646b688d6c18c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/f-checks.md",
      "chunk_id": "fd12334b2ad3103682246459",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "d083395e1e8581443419d045",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "54a98e7d8c146734f9c0d83a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "5a1b1dac6019a601f7729477",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261115.md",
      "chunk_id": "76ccca023ce0c29519d4dbae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "c2ea4cdc7146893e5edcf380",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "f38e034a8624e499035bea11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "3a7eb249f448df4ea9de557a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-015a-fallout.md",
      "chunk_id": "3e99e9879f7f97aa1943d2b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "36f6af5d9daec8c42cdfe4e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "8ebf0331baf007849942f0db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-n0wb/CP-DAEO-n0wb-0014.md",
      "chunk_id": "b1c1573a750afba0d57c4c28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "39b846453fbae5d6b0c1a17c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "ac3f53b4ef64bcc446bca062",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "04cbdfa832d8aed4770c5426",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-3.md",
      "chunk_id": "6df30fc5432c36f4120cea9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "a41f1d95afa4f7ced510c28d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1b3e225e98fe2033a2cbc1ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "0fa603862a9728cb0ae813c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "98ea85a151026da98e21ae71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "886a6ab9e44ebad42e977a02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "cd90aec2be5ccc22d0feea4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261114.md",
      "chunk_id": "aa855a5cf8563da3e4cd382d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5emz.md",
      "chunk_id": "be5faae6247dbd91c5194eb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "c2f8b740bf39a8aa4879dd19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "5256c36bef017071905e0502",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c61c2c1853c9f1ea423cce6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "3d8043e893c009af52c6c8d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "9baae4fec2c2891e5919e08b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/retrieval-hit5.json",
      "chunk_id": "025c98dabafb01b2096f1df4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/f-checks.md",
      "chunk_id": "b4cc3350f6ac13892f1af59a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/f-checks.md",
      "chunk_id": "ec276ea1ec585a120abebd18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "f14f1bde602ec9f82e9bb1b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "a6911edb4d62c9d75932fd4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "0b72107650a1b89e629c6e7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "26c7b6db38355d6ac0d1cd56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-137-evidence.md",
      "chunk_id": "272fb30cf9134b370f368420",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "3933f3bff0a21db34c5ca9ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "eafea6614d27d5b25f7f2968",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "90139d0d4a7781ca246db25e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "c602d82bbfb43ca186c76b2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/README.md",
      "chunk_id": "ea3cdd54bb30599378b4254f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5emz.md",
      "chunk_id": "601deb92c4d03c487e58b898",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES-AUDIT.md",
      "chunk_id": "7decb6d47bf6f74efc6a4fc6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-0rfi/CP-DAEO-0rfi-0009.md",
      "chunk_id": "25d9ff3da20b645536f6111f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWITCHED-OFF-1.md",
      "chunk_id": "a9783f355efa810b16f14d9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/MORNING-RESTART-2026-11-03.md",
      "chunk_id": "3cc48d3861639da63f0ba6fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-145-evidence.md",
      "chunk_id": "65ce428c15974f34fa831bc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "836cd36f536ed00ab97490e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LIFT-1.md",
      "chunk_id": "3bda410433f99ab45822c789",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "dbf804202c0a6fea21050448",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0015.md",
      "chunk_id": "ffd651033d8a4838a67e33f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "50bea134fbc410382e5d86d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "3a8d18cacfc1eb9db0df3de5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "496cc7b3813e571c3d30d509",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-137-evidence.md",
      "chunk_id": "c9da882f09a073b98009c187",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "b9a6cb7d051de98711ddb968",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-137-evidence.md",
      "chunk_id": "b7a952dbd0a11b1e0f924257",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "e8f976c7a391af559ae43987",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "0c1456875c79f1a1a7583aac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "4133b2b78efc35d93f72e440",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5emz.md",
      "chunk_id": "bc31c6613dfac6fb0bff014a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/M3-ADOPTION-1.md",
      "chunk_id": "ff5f49331a7bf03e42d90980",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "3fbcca08deb715580818d932",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "9f06d4f04a4dace86f51f68a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-145-evidence.md",
      "chunk_id": "345c9beac202ca2898c65cb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieve/command.py",
      "chunk_id": "9bcb8cdf0e6239bcb130ab45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "04b7878ca6457bf0c13c21d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "5804c98307a2930145d405da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "c5ed6355da527d619c92358c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "6b7c6cfd60cedc6c3d4e6186",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "b8ca6e7b213b85c069cacb7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "68653b12a98a1aedfd8402e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md",
      "chunk_id": "60412a5913c14c5b9a655e90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "977adaff6d046bc82ed088a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-REPIN-R1.md",
      "chunk_id": "98bfe89a543f8234a14bbdb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-zqvn/CP-DAEO-zqvn-0008.md",
      "chunk_id": "cf24cc60a780b32efac08a12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "cc012ddf342c1708856dba42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-mb2t.md",
      "chunk_id": "c5e7a97ad791ac7402f11a40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "499ee1727d9351eca22cbd0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "372f9343cbf4a4fe8995d452",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "0d51748136bf364ff3c32dbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "0322da12a651d2127d02186e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "0166784127dd3b99a7b260ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-n0wb/CP-DAEO-n0wb-0014.md",
      "chunk_id": "a4a1f4d87ae7585c4a2f5277",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6b44793c358cc08851fb0b3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6e369a38129038f963f2eaa5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "e8a7de1e1d133633e4933a18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "9d9ab2d90a0e69d01c74995f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/retrieve.py",
      "chunk_id": "9bb34b93247110da72563119",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "20f131a0a5f94481b6ff7c7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-32-evidence.md",
      "chunk_id": "8a0d5b489b0cda8716b0e9be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "1c87d3aebda9019d3446194a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "0dfb957aad0524bf4c5acaab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "d6014e6fffb7279ada5c78b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "3bb31ded4d98384d7f0e5aa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "39f69582a22f189013e50d01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/conftest.py",
      "chunk_id": "553d9099c627eb05001ddb29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "b43ddbc16aed2c8c751ecc06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "ac536ec07adc18599430116b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "4fc028c581a73c1a6c66e0b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "c015f3617d8a0b113a0aa16e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "6b46a11b0653b099e1abd2e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "972a204f7f974bd158bd2563",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "0779fbcf2ec6312ad4b85f6d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r4xc.md",
      "chunk_id": "225f06b163e1d8f0cb9bb3fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "f9ce31b8b582a86af2980dc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "606db56b61df716967b9c586",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ba14cf63b076c692a46f5037",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "7086bde8f77ca45250e85383",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "33f520622e600c2810fca1ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "c6d92968ffbeb83f469215c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "da76a4d281d032d6b84af699",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ff3b8832500ed8bd90900ece",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "2def4a99941dd99e3da2aab6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "b9bb18895bf31df7691b9688",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "1794906084208af381d2f594",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "e3fe864682e4704f8aba31e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "da157206dc930b95d7e43784",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "e81f4bf48177948e3e4f8601",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "adda9035095d1db6a0403394",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "4b1ba0411f49aefe5c7bb345",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1744e42e481620071cf4c6fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "d69fb7af320e97ee4e237ccf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "3fc120b9626519cf6d803856",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/test_w2_112_bundle.py",
      "chunk_id": "ac51e66188e401489c973030",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "7d041412a466c474880e3182",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "a2d4cc8bd27e5a94ed9f9c37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "8b7a22ba2ae0e781c15bf905",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "199c9bdd22af2bee57e70d71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "77e333cd6a7c97c6e85661e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "9e6fe605d0e023dee017e7e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "7f427fbce8af9a5586ef8315",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "4de27c012ab3d702920f2c0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "8cbb253f3219b874d6af8614",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "66a9b495b9b5917a5ffa4734",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "d72aafd8c9815932a4197293",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "22186f20b7ca208dd9b855d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "4e704d8f5728fedccaa62a9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c9ce1282aa3a37611dfff94f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "614c1a1fc8044a97644e5864",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "cfbe1fc3896489eb358c80c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "52f5b52cf72c2ee596e4cd74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "64e05021517b9913a1d4694f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "de88cc6c6a624db7a7f69eea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "9d3de38bd51bf0ff055632ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-53/w2_53_support.py",
      "chunk_id": "4cf0d8b408559113bd607cc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "a6a0f98643c3d57fb28abb28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "c0b2c8700dbae6d498c19b3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/REDS-0.1.5-f511bb6c0.txt",
      "chunk_id": "ac9ac31acb808c117ef5414d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "c8c89ca71edd9aae89a2b380",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "b291217cb923d5a12ee4b6a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "242091a5e00a6102b9925f38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "9e2ae65f27683f6a6f8f5350",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5emz.md",
      "chunk_id": "5675a76ee2c5d8e5f2e9bc7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "3c07aea225429fa11cfabc8c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "99c7c5383c732ea0967a49e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "12d1a45ba0a25fd771500b22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-RERANKER-1.md",
      "chunk_id": "f70336677fc2981405588f27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "1a7dc3068993886b3aaf9533",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "409ed93b328294aded45a625",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.1/manifest.json",
      "chunk_id": "e97024353241cff06daff594",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "c054d08a202b549b982b9a84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/README.md",
      "chunk_id": "ba2b1b7e43a601e949cbf1d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "1159a05e717eab85df77127e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "4b3ae1cf12d3cab0eb67f565",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "759b793255eaf71a37049441",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "7938e80e90076bd60e5d5761",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "5240939a13fe35022d54c7c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "b5d5e472c0380d88f87c9bc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "a7a3ea2f8b53c80ff0288d13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "13a5d06cb69fb55b2771d715",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "d6f4ee58076323cdebfe331c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "e81699036a98acccff48825e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "1f5643dfbc4c458677480092",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_support.py",
      "chunk_id": "5b7552e9d58e54b17da0fb53",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "5b8cd26b4f623e2a45c38890",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "7172b17eca386676b26ac2c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "186d42d5e99cc158cfdcef38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "612a2b40cf703dbc252f8114",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "856e4b600f6936aada50a27e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "8f19204a868429436450bc45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "ecf0a527e4bc72d755741fd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "0aa177d44671245e0d1b0156",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-juee/CL-DAEO-juee.md",
      "chunk_id": "b2fd92487d17df313d45f5ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "7a3043fd68c0190a6c48e960",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "0b0292264f9097cf756681b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/conftest.py",
      "chunk_id": "50b383a2056845dd7f7d50f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "35cc4a583af654d1d7e931ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "050c16e8025f17a24d45fb5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "9cd7f3fefb77a424d7633fcf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "605ba2b302cd7891b635033c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "1baefa7e509ee9a273cba068",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "e7e47535b6e4ab40c9119c73",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "ac0408c2b549ddb41b30b0bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "678d7cd9dba852728a0fb289",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "8a1abf3eacf90a3c05ca076f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "5fdc3f54e871b194f2eb0f33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5emz.md",
      "chunk_id": "984a4d9f193d8a384603f414",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/w2_145_support.py",
      "chunk_id": "155b1cef3aedbd8a12524741",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "337d59737b8c6b10036589b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "12aa7810cd3f96552a4f30da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-c1uz.md",
      "chunk_id": "1c8b777181589194f994f103",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bfbd32b935d44a71e15bb9af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "6c78e707b26a761ebd282227",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "140c3ffc476c569c7dd78575",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "703855d4b8e5813eaa8edfc1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "41ca8d9975cc79a2784d3262",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "217d03a1ba5780949e3f7669",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "d09b04ed3b083a9a86c8e8af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "73123a6b74ea184f3f4daa28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "366cf8ca5eb0bf69f24aabf7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "d0bd0ea3350dd47c6f1631f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "6a7b3dadf5dd2ed8f74fcbd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "68fb3be004b304196669d0c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "cec47c03bab9afc0368d7a4e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "122d44bf1c42a7e70ebb88d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "1a19313555039b408f20476a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-juee/CL-DAEO-juee.md",
      "chunk_id": "7479fa2d33a569d8f4185c0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "2ccdf7516cd77ea8c6ce5b3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.1/manifest.json",
      "chunk_id": "51f4eedfbfb07a94f58b187a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "13c07a7e7739c72a369825a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-GROWTH-1.md",
      "chunk_id": "fd5ade7e5573e038af53ae27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-21/README.md",
      "chunk_id": "3576bab6c29c22b36f63cd06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/pat/B-findings.md",
      "chunk_id": "b1f19bc42c900cc510095aee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-0rfi/CP-DAEO-0rfi-0009.md",
      "chunk_id": "d0566a258adcf08765136922",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-SCORE-ONCE.md",
      "chunk_id": "18326c314f06425b396364dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "chunk_id": "9af108faff5946d2242d91b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md",
      "chunk_id": "bed893eaff97a3a9e31a6672",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "d51809c168dad7832b8030d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "80f155083d7b091ba01dea8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md",
      "chunk_id": "5b8c9051666f20fc7e2f05a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "b41cbd3eb1f1697f4dc51020",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "8a2fade8e667817f8cbc3c21",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "1dd9c3b41c49acd781a29a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "9fd8633b996a5a4ffde795ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "9523e1aa019d3eb9dba74d8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "2eff47964acf6b74675c99ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-7rr2/CL-DAEO-7rr2.md",
      "chunk_id": "655cb6e7045fe3b53caf4ec3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "e8d81cf3c6ca18238e97acb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/conftest.py",
      "chunk_id": "521a44d90d9692bdf1c98d5c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0015.md",
      "chunk_id": "82bea5a5aa459e851a8f87ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zoex.md",
      "chunk_id": "e4d00ffd6a7ea7dd18a894b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "0995c48e1977f878f35d4e44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-c1uz/CL-DAEO-c1uz.md",
      "chunk_id": "84bc32b72d82801b6fa08930",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/REDS-0.1.5-f511bb6c0.txt",
      "chunk_id": "d14145856ea6c9a499b0f94e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "68d503359ee6efa333a85e45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "e49111cafe5a90f7f821b509",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "ccb814d4002a30cef546c484",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "b52f5dbc98746ace47c6f543",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "deb74e416729db0a87b5136e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "59a417dfc327c663130be0d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "021e73ac037bd924531b50d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "chunk_id": "1fac5d509bc22795b3578954",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "74c6cec02170610c49c45c26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "09b9fa6fd20738d59488d9bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-juee/CL-DAEO-juee.md",
      "chunk_id": "62f9ba79e90a307d18d7e22e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "8ebe3c6d57925c68ef7f7bbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "db11d54548f73fe6bb4c856e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "3c5097c1545081df1c7a466d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "3106223d627bb79dc05e68d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "dc9deb1ba72ae893e6024e30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "8d2a664b5829d6af09607dc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/w1_19_support.py",
      "chunk_id": "db19da983918fb186c5ee69b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-juee/CL-DAEO-juee.md",
      "chunk_id": "51b52f14d2cd99108b47552a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "0adb1678285e28bf0b6d3c93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-uzme/CL-DAEO-uzme.md",
      "chunk_id": "089043fdd4c0da1c056f0e1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md",
      "chunk_id": "ae340beed7ab0025b56349f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-c1uz/CL-DAEO-c1uz.md",
      "chunk_id": "192d859e553e195dab8f15da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "e2d4bf5639f283b04bdf5eff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-GROWTH-1.md",
      "chunk_id": "0d0876228eb1bf60dd8703a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "6c48588bee5997fab27e2c0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-7rr2/CL-DAEO-7rr2.md",
      "chunk_id": "87dd229e875aefdd494dc39b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-RERANKER-1.md",
      "chunk_id": "6508c08b49d7566482d92708",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-weekly.txt",
      "chunk_id": "b268ec0dbfce402194d843ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-zqvn/CP-DAEO-zqvn-0008.md",
      "chunk_id": "09294a868923ab6c2a0dd87b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-145-evidence.md",
      "chunk_id": "716d976b68032a9b3ba103ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kfn1.md",
      "chunk_id": "1b101caa2215c469d57f18d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md",
      "chunk_id": "3d46aa7db1ad3163b59bb68a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "442699b917d824e28b53e5a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-f6x3.md",
      "chunk_id": "d84bccc4b4f3e396c4b49c90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "8f990b3b2dca041340588aa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RUNTIME.md",
      "chunk_id": "89ea4a7406e2c5eee96680da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "63cc83ad84abd58d25e3b8cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "3ac221955ba08121c032e65a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "5011a78c1d00d23df99c5c21",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/E.md",
      "chunk_id": "0dd982b3cb1a4589145ac7e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "64a4fcacf5bd7337a95d5b8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "62ba2271841b66d91a584770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/retrieve.py",
      "chunk_id": "c8947f9cbfd21359edea80f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "bf9134a0e87c0e2f40f3eb8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "3c458874bf83a6ec214fb249",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "chunk_id": "a8c9b84516827613a14f41af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/pathmap.py",
      "chunk_id": "b71d27efe2dce3d62a1c32b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/rebuild/command.py",
      "chunk_id": "74227ddbe7400a687c7d90b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "3d6b7d8dd6e1945830a16239",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md",
      "chunk_id": "aec2e869dec8028c0147b72a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "968ee897a6c540ef96d2bc1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "46b9cca803a8c216cec209f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "d77fe8c325989b33ab46a05a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "d949bd65cad271c6bd7ad925",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-whole-tree-review.md",
      "chunk_id": "42ca1287e56964a73135713c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-2azm/CL-DAEO-2azm.md",
      "chunk_id": "1da139283e66505c9ca00e6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "c7ab2984d4a6174bb8774dbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-qty6/CL-DAEO-qty6.md",
      "chunk_id": "a11466561909e4dad23bf71a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5y8d.md",
      "chunk_id": "c9e6b97462745f36dbd07b04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h2k3.md",
      "chunk_id": "7045df0168503011b276c9db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-whole-tree-review.md",
      "chunk_id": "c146b9bb3a2e7a765d2e5436",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/retrieve.py",
      "chunk_id": "118312c71f7a1afecaa02671",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RECORD-REDS.md",
      "chunk_id": "4aad1b134ce30d016cfb3e29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-REPIN-2.md",
      "chunk_id": "8663eabc115435dfb966695f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "88058dce49cd76b5d1d1278a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_support.py",
      "chunk_id": "2a11abdcae5d130a876732d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "cfe35c43888b0e65c80b08f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/supplementary.py",
      "chunk_id": "2b41c7dca58b89cbdd18cb16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/sessions/2026-11-03-orchestrator-DAEO-sdxk.md",
      "chunk_id": "80065077c849f0b19457a940",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-feon.md",
      "chunk_id": "7b2b900540e40fa27944b97e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "7901ca051e51a0800135ddb3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "c0c6c3847ad193de9a4d22f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "1537da106d218a8534cdbb57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "4c9ddef32c8a3657a1824c0b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "3889cbae3831ccb7cde6b0e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "78852465fb0c9b493363297e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-91-evidence.md",
      "chunk_id": "aef3fb4e865c35a5d1b9e92d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-r9ss/CL-DAEO-r9ss.md",
      "chunk_id": "facad8ae8923f7ed86449fc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "2797d8b26f36a04c1d1ce5f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/M3-ADOPTION-1.md",
      "chunk_id": "84f77c7a56523cd92a893f6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-iw1f.md",
      "chunk_id": "eda32ca65a6079443f15f57d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-c1uz/CL-DAEO-c1uz.md",
      "chunk_id": "31b7fbb135480743d1a72922",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-91-evidence.md",
      "chunk_id": "76ddbb6e83ccf87c909b7549",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/retrieve.py",
      "chunk_id": "a3147e4204b52a426cfeddea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/G1-PROFILE.md",
      "chunk_id": "6d050ceb4854baa817b1a1a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-feon.md",
      "chunk_id": "9b7cf9eb8dbf2863e3e6a434",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T051835Z-712c71cba87b.json",
      "chunk_id": "46a07fddbcdbb28f062da042",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/w2_112_support.py",
      "chunk_id": "4555875339ccd834ce77012b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "122bacb89e4f0c25e2ce06df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R1-GOVCHECK.md",
      "chunk_id": "2e3ab995512e1beee6820a8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-r9ss/CL-DAEO-r9ss.md",
      "chunk_id": "136b178e72e55a174038aefb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "2471ca49f506254a2bf9228a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "fe49e47be8618ca5323d1074",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "f0445fa2d5971d2f3aba63e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "f3bf74e9cc43881ab1af6895",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "9ed83205ce5275ecadfbbd17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "f2b1ea9ee7a78e3e5cb43399",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/supplementary.py",
      "chunk_id": "0913f0356b490aa12a36953e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "90a11e800612aa53358159d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieve/command.py",
      "chunk_id": "13423e53073c791da0047f52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "22d47adae607372ee3a03f68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "2b55a115eadf4db9aaf00bc8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-pl6k/CL-DAEO-pl6k.md",
      "chunk_id": "4a701fe8865aab9927bcecd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-r9ss/CL-DAEO-r9ss.md",
      "chunk_id": "789dad0c42701db6a84c7bf4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-rmbe/CL-DAEO-rmbe.md",
      "chunk_id": "25033ec5920ce92ed099f65a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-ye2a/CL-DAEO-ye2a.md",
      "chunk_id": "83aa0e24bdf2859e909a1bdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-ebmh/CL-DAEO-ebmh.md",
      "chunk_id": "91c668a347a488a98bcce4ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "88440c773bb12a0d98341506",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "fbaa5eef77551df77e5551ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "86e3c5e717be13754cc6f2fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "933c416af3e0f531b6008dce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "7890a572905b083052b32279",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/role_paths.py",
      "chunk_id": "e03b9e008ec7781de94a0ead",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "762f5401fdb883152e26dd2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "fd1d0cdd2f8df20dedef8597",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8b3b2cb98b771b71cb142165",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWITCHED-OFF-1.md",
      "chunk_id": "c718a478637081ea0d67c797",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_support.py",
      "chunk_id": "34dcdc8cb7d4842a91e9f815",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9753d7577621864cc5ce31eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "3ea41decca39792ecfd565df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "ca950436f5bf80ec8b119b51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "86c75181c5a74ec643f6159a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "561e96bbe9ac8b7d27c905ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "5bb6ee768d41b1bd0b6c9115",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "a4f6f62cbbc5335428adebb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9152cf678ed4930792795869",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "f61791ca270a549a97fb9ed4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "8b5830efa5d6fad481c49aa2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "0ef5c357fb3f367221a5866c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "81ab88a7be840579a2a9d8b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-r9ss/CL-DAEO-r9ss.md",
      "chunk_id": "39022f55916257fd43eba31f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/status/command.py",
      "chunk_id": "6276173f701719ba5917bad4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ce3cb92a4664f14851e71622",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "ee5dc8792d2b6fcc5eb402ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "a122249c7f0384a8f5059322",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md",
      "chunk_id": "bb5b296ee11320938ea8e1e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "94b5c44e2715ccf60e80b3a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "7bfd7ab9d92aeb9855a1e249",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-NIGHT.md",
      "chunk_id": "5657c9c9c99f8eaafba3b766",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-TRIAL-W4.md",
      "chunk_id": "9d24000c08f1bf171fb84f1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "077aa3bec596d316bf4c6c43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/retrieve.py",
      "chunk_id": "ccafdc1511fc759c9436f282",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/test_guard_fix_3.py",
      "chunk_id": "509eec0115850404f0e36ef1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ijf5.md",
      "chunk_id": "da077060a06ce6ba8eccd94b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r3gx.md",
      "chunk_id": "6337adc2bb6c884116c8cbd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "804ec42aa3db2e1539b25816",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "e3bdfcf88d054269550f0cd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "bc1e6d19cf15fbccec9efd8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "7bca1c763ac2bc7fd833e12c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-s9qc.md",
      "chunk_id": "03161e3a47708181bbd03c70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "42482774616a2ff578d236e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-145-evidence.md",
      "chunk_id": "22568cfd9987e9fd26a05299",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "c594710d4bfd3118bd80f595",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7ed5c5c2ddd8d1ed5a4f38e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "b7410084b2cc575a0df46cb9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/dispatch/dispatcher.py",
      "chunk_id": "8ec91c5283ce8180764861d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "a963be80ddcfa6e095684631",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SIZING-1.md",
      "chunk_id": "03c3441020f0af21fe531226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/rerank.py",
      "chunk_id": "c5ff92cca871f5cd12caff64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "52c872810f54aeba725c1bc6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "ec460fdddbeabc87aa125673",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "0e08d53d9a5ebc9f9b7924ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-ebmh/CL-DAEO-ebmh.md",
      "chunk_id": "790f0bfba81cf41c19a37d54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "7ba89be48122c39a9116f6eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "3bb784a952399b8f28223b13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "a64469c954e77e2287a2dee7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/semantic.py",
      "chunk_id": "a68a0bd85573a7128439d0a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8044fe25a5ac493947b60aa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/retrieve.py",
      "chunk_id": "522df52572f888f9ad86fa5c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieve/command.py",
      "chunk_id": "0dca8039637a28b15c558bd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/rerank_service.py",
      "chunk_id": "8ea9a2015ca4e3cee23c5946",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "5bd5ad4b3e922faaebd17a9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e79670964eaac3e196ec73dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "c38925a2a721aba7f91bc62b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "1d5f0bb1b937cc512dcfdf94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "90f1a774e4b21560048b9474",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/conftest.py",
      "chunk_id": "8df14e4a75e90dfb6d29a2b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "43bca8fe963a0d611d8cafe5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "cd0ad595822c227238dd7e09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "1a1d90203dc3e863d3f14e54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r4xc.md",
      "chunk_id": "eac58dbfc8bc46673253c657",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "ca446b94f2b9dbdbfbcc1314",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "9e3256a6e0cdd8728f25474d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "09b188ffd56e25e678841653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "ce637fce491b6f0d0f93edda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f9edef98e93f4676c47e7475",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "acf4aa94ecb4b98e2b63077e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "33f46005e48003a9e24faedc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-s9qc.md",
      "chunk_id": "e417a06a7fbf6c8840bccb77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-lifted-breadth.txt",
      "chunk_id": "53bac5f145c35e338fd32a73",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4f41e57bd747c42278bf1ede",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-61-baseline.md",
      "chunk_id": "097843a68d482964acd5343f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "3b3d86c7d579c2d45062d02d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "63a51e9f7ae879d8602d707f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "794ed95f9018cd9b6ae89959",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "404344270639dbc87a5d13a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-137-DAEO-5emz.md",
      "chunk_id": "071ea8723327d7dce3c0e158",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "0568427aaeea4597b17baed5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "e28a1c95ab7074cebe0f23dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "5526f7f17145cb66a0ebc3ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "82649d0687821dd061150796",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "8f955edffdf0e25bb80b2049",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "6c9112729b891cd175219bd6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "516942c311c9eb80e3adc679",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "28dce953d94010fcf9d8dc60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kfn1.md",
      "chunk_id": "2ecd222dc526c1878dc6c20a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "595d32d4de372e57f8466daa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "f3ca9186218c00f1a9f1a1fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "e8c0275669fe26bd025aa448",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-91-evidence.md",
      "chunk_id": "a2a88720408c024c659a003f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "6e79dc2746ef620dfb6a146d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWEEP-2026-10-20.md",
      "chunk_id": "2d60a0ef9c13d589b5a8435b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "539e489b3f70fcaaf8268465",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CAPACITY-1.md",
      "chunk_id": "b5ca09eb4c28afcf2c056b8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "7b427e74d3c96c53f26614f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "161a08bae2d5b2172cab3463",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "a29542e6e1d7227362954f50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/gov_reranker_gpu_slot.py",
      "chunk_id": "f20a89d01126412a0bdfe940",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "fd5612c600c18a984c44444a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "cdfb6b51ced2766bbe9c5971",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "2001ee600603aab63bf32c5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "7fbb018a0cbddd0bfaf02e3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "631b5a097957dfb682e0c1f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "14f13752a38bbf810691e8c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "c78b167fdf93031f2135b8fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "d71ebcba53e764b43a15f2f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "ce2250e434bdcb9b7f0879f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "b4040d3488756b3123a99c19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "52e33117b1393ce24e104f8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "92d5ac155773f0de558439ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "ec677e2f1519f90fd7138cbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-f6x3.md",
      "chunk_id": "2f41f3fb83894ae5bbfc3198",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "00903f23832b5b2d9c6be4d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "6eb15eb3f69de5734ef0bd1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-03-DAEO-ym8a.md",
      "chunk_id": "fb997486caa64ea4e0f420d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-26-DAEO-2ds6.md",
      "chunk_id": "88cfb9b161b75115f2c635db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-51-DAEO-egsy.md",
      "chunk_id": "a0296250898177e620e14a8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-57-DAEO-cy5o.md",
      "chunk_id": "b8f2a4aaa83ba5cf53ee0fd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-61-DAEO-iw1f.md",
      "chunk_id": "2632862b781f34c8955dcc1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-64-DAEO-0uhh.md",
      "chunk_id": "ca3dfaa867867a0c57f8c453",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-77-DAEO-b6hm.md",
      "chunk_id": "6b14a88c0d031e25e1efc232",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-85-DAEO-gdzh.md",
      "chunk_id": "53b1a0758b058f9095983ad4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-87-DAEO-s9qc.md",
      "chunk_id": "d567bfbf2742cf39bdc953d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-90-DAEO-8lmb.md",
      "chunk_id": "ecb05fddabfbff941b40eca3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "bd79e0502c9553d76e5aa81e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "59ba48098e01d9e4a2d3002c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "52077abc0488abd26f660997",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "12bf788878267293aebc0941",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "615a648a0261ee62b505366a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "9ef02e4a2b54bad1b31f2ce9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "9c00fc1b3b07de6bf58d61a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md",
      "chunk_id": "1aea20f2a14e739f518b23f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sq3a.md",
      "chunk_id": "1075bb9f860c7a59e2a0af02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/nightly/nightly.sh",
      "chunk_id": "ca538d513c5cace9487ff26d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/supplementary.py",
      "chunk_id": "9be087dad49e031dcf77fbb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sq3a.md",
      "chunk_id": "10186899261fd43854cdd4e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "b3a3ae89afd8ef02efc35be3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "5ca14a4481c2b2c727d3f520",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e11dc1aea84c7137a6c9078d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "f1d7530a08c619163961d051",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "chunk_id": "7f4f2abaf223cc285c9d0c2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/MEMORY-INVENTION-DISCLOSURE.md",
      "chunk_id": "bc72ecc6bc772d1a1c4b6ce1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/dispatch/README.md",
      "chunk_id": "810fdd017aa184bac54e1c54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-arrl.md",
      "chunk_id": "341b993b197074e31faf4d0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "d0d976ea2852b1f0cfc51833",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "775674fe5476b0fcb62c9972",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-137-evidence.md",
      "chunk_id": "0c07d4d3b5622ecbf2759a9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R2-BRIEFS.md",
      "chunk_id": "1bcffa5468cba47bbcc2707e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "ea01571733267fc3bc4d94ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "c9f505cf4da34c150dbc2852",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "37263c94904f597080c6d41f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4781c4b0f7d3fc67d35122fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ijf5.md",
      "chunk_id": "7a97b79ffbca9db0f78591ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "d4ae36504e32d75f8c43815f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "61bd062d0e1988389467492b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D3-WORKLIST.md",
      "chunk_id": "98f32196d550b483cf258008",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2tfd.md",
      "chunk_id": "a673544eeca9e4d15eb16730",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f2dd406417ee6d07d543f78e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-54-CIT-E.md",
      "chunk_id": "dbc856176f2e58eef655bc17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "fc8601e2a91f1f3b6df8edce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "507f736c16f584abd41c09de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "d030e76735bdb4fd9bcc0bf2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "5faf5a4697031e138674ec61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1178525e276313ad9706c608",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-juee/CL-DAEO-juee.md",
      "chunk_id": "d8bc17e9ed469dd2133fbf02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "c8a61dd699db8f9b28eed521",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "601f6b4390524e0ec5dea2d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md",
      "chunk_id": "431e2265047d18c046edf1ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "2c539c33265b8d7f2796ee6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "7a8d7fc6c9c544ddcd7f5cf7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "b6442c9bd081e76678aa6e63",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "7b9a934f8cf38912f955687a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "1990af697c1147526155bc0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/fusion.py",
      "chunk_id": "4064ebd75966ed375b450c9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "fc37a00d867cba0303cdd190",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "a692efb1960889e98281b9b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "700021e0e57e611110557ce5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "c597802b771fb0aedee5516f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_roles_support.py",
      "chunk_id": "f1ff70a7e36075447f279f77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-REPIN-R1.md",
      "chunk_id": "637ad0879d085fc0c423f39e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "075428dd6233ebc3638af7f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "44f4cac203b61432189124cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "d94dd360e8fb33577ee0ecea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/E0-RESULT.md",
      "chunk_id": "8bcc02ad72a77c1d83fecdbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ijf5.md",
      "chunk_id": "10af8219122bea6f5265edca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "36e63b43d4145d92ecad53f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "da1e960ea50aac8685abf8b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R1-GOVCHECK.md",
      "chunk_id": "43ac192c9e9ff9c34e65eb2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "badacfe311150ad237927fde",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-126-evidence.md",
      "chunk_id": "8df0ced32325476c6c56084f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-54-CIT-E.md",
      "chunk_id": "4ca2498248f4bcc52dc5f9f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "bc2cb4c97bd540e2d187b817",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "bcd72865f77f459c5164b539",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "9285a926cee64ea1ef95a9c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2tfd.md",
      "chunk_id": "892fc79f9734192236fb486d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5emz.md",
      "chunk_id": "825bf4ec67fa4361435777b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "e73d5397997feed8123789a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "be196dcb939fa5d7758d60d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "3a429e23eb0501bbda2c4b13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "bc6a34b0ff8869f12c45e5b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_roles_support.py",
      "chunk_id": "8e52755eeb32272688a9dd60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "d053d80a716ce85352bd5694",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "8042a44917868ca189b70c4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "15da94b9def25705c95545bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "4b7facd6d6c0639d2ce34229",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "68b181321bd0bbc5cf7bcc74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-LEVERS.md",
      "chunk_id": "632a593722a4d689c250e565",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "22b34cc8bffb7720f1d8032e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-INVENTORY-1.md",
      "chunk_id": "e06c40ec312d4d0e3b4317e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "715d5e82294b6e500c8018df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "f9dcdb8caa442bd0b631ef12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "c7d97fe40a468ea4194e7d58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "c445cfc4bdeba8206ac7df2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/E.md",
      "chunk_id": "f61e42aceb7fbec265745e18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/OWNER-GLOSSARY.md",
      "chunk_id": "4ad9f15c05d7cd96ac982621",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "7676127b86afe1f1f950795a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "671abada066d98fe2323be71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/supplementary.py",
      "chunk_id": "de552f77da2037f0c996f884",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "f2db9ef266d023c4cbe1c6d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r4xc.md",
      "chunk_id": "cca3f5b556cfd6b06f0865d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "fa8be9eac479a3177086ceac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/USAGE-RUBRIC-2.md",
      "chunk_id": "4d60aa4f137d12ddeb4121f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2tfd.md",
      "chunk_id": "0161604e5aedbe56aa9c6fc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "88c90996599b18dab17a3b6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "7852a5a51fd0c021acaa2379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "c2ff1b232df1acca56c815ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-INVENTORY-1.md",
      "chunk_id": "55ee86294e9c260d7739c78f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-tickets-and-rubric.md",
      "chunk_id": "3431d04f1c3a3396b3cd5266",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REPLAN-W2.md",
      "chunk_id": "f23c7fd7ec237ab7b88a8f0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r3gx.md",
      "chunk_id": "cdc7e9a02b30a79c48d996f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-111-live-hook/README.md",
      "chunk_id": "9af060139cb7b56acc9ccea2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r8vq.md",
      "chunk_id": "e93f5e3b5c5e5071983a7895",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "16fdd77b998514384034c143",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "20d83527e47c5047f48545df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-jsg1.md",
      "chunk_id": "ddee01195ee989c7f5d1a13f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "943a53c7d65627d8219a2aa2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "c0127b1b8cd7453ce6950be4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RECORD-REDS.md",
      "chunk_id": "50777d347a18225097015d2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-arrl.md",
      "chunk_id": "e5363ae041377efd3fa66299",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "ff36c9d05b56089e29dfb325",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "5b87d69e03ac2c6f721de7aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-11-02.md",
      "chunk_id": "4c71deb7cae8fe3772f8065b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "26b96e43ac66a7ae931a2d51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/pat/B-findings.md",
      "chunk_id": "0b9ef9c1903615eab52f08eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "b3d991f634e72e1b4ca64754",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "2a2d1e339e371793ef6f6f09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "4d0eae4ec2e42ff509d1d009",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SIZING-1.md",
      "chunk_id": "8ea1cb596ed7b6429dc560cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-REPIN-2.md",
      "chunk_id": "be14cb1c9792bcb51d8e7f14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rmhj.md",
      "chunk_id": "8bc69f05d6e22cca07641192",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "905f887c5a237587cc5b3b4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "86de4bbd6e3c910ffe88ec28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "b2199935daddb29a7a51cfae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "1e43d2e7b111854c387e6a05",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "e4997d2367d766cf3bf8f439",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "d3c8bfedaa57b28696a7ee52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cy5o.md",
      "chunk_id": "a9976548860422d03692a42e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "a59ba0cfa8af862a1ce5f971",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "c1cb91c0b68523dd1d6180a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-NIGHT.md",
      "chunk_id": "e2c496925236f928867ec3ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-54-LOAD-1.md",
      "chunk_id": "cd8973214a72ca6926598d61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "e075695e1f44c2bfc7e79019",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "9d65996901d951fb06812a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-n0wb.md",
      "chunk_id": "bc42b68478a79d0e707c1143",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-146-evidence.md",
      "chunk_id": "cc5f8a15e2bb2346ec52405e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "313b9724c4e482431e1b7be6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REPLAN-W2.md",
      "chunk_id": "6e20afc5d4ebc5bcca36e434",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "2f6798ed0d7d9158dd1fd39e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "3dfad75b7f3d0ec44f3c098e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REPLAN-W2.md",
      "chunk_id": "486780712b9a28f9e18ecdc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-whole-tree-review.md",
      "chunk_id": "ceb675eab4d6bdeb9f18e597",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "4ab7355f4dfb79b51a9513cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/REVIEW.md",
      "chunk_id": "744388e7568546c15a51f03a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "8e9afc02ba9ae8ee3d6c1ca8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "4408f7cf842beee369865b34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "879710dd561ac9e9de7c360e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-NIGHT.md",
      "chunk_id": "b1ccd18d9127deaab5da4b49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/C.md",
      "chunk_id": "3f6069ad555322dfa6702607",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "ac42e647bfb914b31ef3d9c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md",
      "chunk_id": "7fd6b67953035111470c1766",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-whole-tree-review.md",
      "chunk_id": "901aa9e877364d9e0e492c94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/USAGE-RUBRIC-2.md",
      "chunk_id": "c1f2b7dc2a49361a87c62e65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-s9qc.md",
      "chunk_id": "524534781d6bc5e1e24d345a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "b7bbbdece2f4ae2849df86cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "57dcec48e611c2a531cd066f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "1f08e026b29cd33c0a80ef76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "07a76e3564f932c0c2676fc6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "0c4fb4a638e45990b8ce33df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST.md",
      "chunk_id": "6f1450d16491bf6c767f1cff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "5d7d684de82ad11981f3bd04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/E.md",
      "chunk_id": "9e692d614dcbc6c6b622fe92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/M3-ADOPTION-1.md",
      "chunk_id": "1375c3a3daf8302ef82f1779",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-n0wb.md",
      "chunk_id": "046843e03b3efc21076cd41d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-whole-tree-review.md",
      "chunk_id": "e0f2fd0055350f6134707beb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "b8107c02329a05dd23cd4e86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "499dc1fccce49644d39f194a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "86de6e0841fa29d3bfa0871d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "6cef6ef30b16704e37a9d518",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "cce53cbb06d74f71034a6e9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-iw1f.md",
      "chunk_id": "6ae9e952bf0d4319b64b8956",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-whole-tree-review.md",
      "chunk_id": "580913d8ac71079ff774ed66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-154-s4-check.md",
      "chunk_id": "9073f632bf8c005d2b48bd2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cy5o.md",
      "chunk_id": "e3a865d16b1d174e75b91caa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "652e01a5b67c1b052b2d546b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "2ad36ecddbb392d5b5e7cf92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-SCORE-ONCE.md",
      "chunk_id": "fe7aae4998cf35847790c14b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/M3-ADOPTION-1.md",
      "chunk_id": "e25fe2e46794d55a3ca488f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "bf63dbd3749eeb47ed074f8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "675e4ddcbdbfa5b9ec4386cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "5837ab84e49fb04bec813013",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "73a95f1dce08ef7fb1a1d67b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "f7725f907af1791b7b763e5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "352c7593849ed00c0c211f40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "af718116b13b091b265e61b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CAPACITY-1.md",
      "chunk_id": "07869758e56a96951328cb42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "3baccd65bb7a90f55a684d69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "2e3fcb948f0bc95797d8de7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "88191840e5d6af6fbc17f89b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "4895735cd7c55380639475e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "3d528b63e13e0dc1a764ccf2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "9b1dfcfa26081cacab1e98bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md",
      "chunk_id": "669c5b6ab008f3dea49a57ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "eb98891635a9e97a683f7846",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "78e6ba00d0a35f3c912734ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "c4f0676146b105e008342455",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES-AUDIT.md",
      "chunk_id": "8764b47b10fa1b5710470735",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "fe73d80f60055bdc6c4eff88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "de28f0cc65d0298af4680f46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/REVIEW.md",
      "chunk_id": "9a3eb90e23ab623165ed98c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "8dbe22edc929f2b6a02a924f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/B2.md",
      "chunk_id": "f979b1af371e301c48c7653e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "24d40c55c7f7fabdeb7f5b5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "0c14054ea0f5db3a9b740ff8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "cc5760505c13211d28713365",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "83dbb8329a6cc49d9e9bbac5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "5982a1582d89fb702ec91d69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md",
      "chunk_id": "09a47c5c9538744d8347e1ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md",
      "chunk_id": "da0a0ccc64ce34b2710b9d83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "435b9a6eeff3b789766c4763",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "effaf320678ce6cae956adeb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-LEVERS.md",
      "chunk_id": "2ead6c74ae6e30ce69d327a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "05250300b76c1932288cc656",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-ti-cuts.md",
      "chunk_id": "d91b2052af1e0d3524b95a27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "c6c109ebba77682b2f948f8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D6-PART2.md",
      "chunk_id": "5b245b600784fd40032fe966",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "7121e7b6e1790fc87ec80bc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "2076a09c07a5472c0d698707",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-154-s4-check.md",
      "chunk_id": "9c94e11f4fe3d09470d30a78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "256b366073e6800076c82dea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWITCHED-OFF-1.md",
      "chunk_id": "1897e1b5a854e74da2caadbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-SCORE-ONCE.md",
      "chunk_id": "a121f3b32daa7d59c2bd79cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SANDBOX-1-B4.md",
      "chunk_id": "8fbdb66ef4e26adacab2af85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "4d7e493bafa231666189d15d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "4713eeb051cc2375a9062d31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md",
      "chunk_id": "9b3e48958f4df088cd29c83b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md",
      "chunk_id": "54e5362a47ca2e70c16a80b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "ebd4623412c45e137cf81b29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "5dc126a6243f6affe9023774",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "aa664d48f3ba7163fd257b58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "42423889f10ab6685ed29ccf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "9b1a14e1b0636eaa5de00725",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "0657d75a9fd2997c2af7875f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/test_w2_13_unavailable.py",
      "chunk_id": "08cd87c27af1991e53c60d0b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "4a1327a26487f5db1df58d77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "9fa5bf0bc7e0ad7e1e1f38fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/B2.md",
      "chunk_id": "fa2df237c5c35bc4a4a3de11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "1a24156b200eacd20d9f2a8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-114-DAEO-4eux.md",
      "chunk_id": "4390b4ae01f40ff7bc2d4cf5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-86-DAEO-jsg1.md",
      "chunk_id": "38bdf8542699e729f42a4228",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "41bed53bab3191d97a62d043",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "6174cea0b97f4bbb6eaa9f6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/M3-ADOPTION-1.md",
      "chunk_id": "ef25e805e36817f8dd9fe4d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "a840b32cda3bd7811d65a1a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "e3041d9aa07ce40f496415cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "ce17848837cbd5c9492012e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/D4B-memory-survey-package-draft.md",
      "chunk_id": "b9d57bf87a54d17cd3f02020",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "0c199adb36fd474051f02151",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/D4B-memory-survey-package-draft.md",
      "chunk_id": "c572450c50f61406f5ff5e41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "35a8d786fda84211eb460f81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "4e378ced7f8a9eccffe92273",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "ee26b1a27057cd19a91b424f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "4d5251e62a87bfbbbbf6fc88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "73a5381ef5b5791018a12a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "ff4992e60f517495e42e7db0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "3fd898c2b5808e0c89370ebb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "2f6c88e5f2dcbea9b7f6e041",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "chunk_id": "6cd7401e825c53feef9a4d94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "9807e34458dd6adad6a7970c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "98be6d0458403939c208f19b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "57b1f8f7d3dde64b5effcdf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "3b46d807bb5abd54ff6fb49a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "3a36a4654f2748bb9f5a21bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "1c1d3d9c1c68a33f9a9869eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/w1_19_support.py",
      "chunk_id": "e427b5737b1a4a6e01d60459",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "5ce68b1bb6c0aed589951653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/M3-ADOPTION-1.md",
      "chunk_id": "469b8618adbb6d14f7576493",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md",
      "chunk_id": "89a25f746ba68396ffacbf66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "21c970c51d469c3ff07b661a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-10-31.md",
      "chunk_id": "4e7f48bc5a03ab8f6fd8b1ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-32-evidence.md",
      "chunk_id": "a432ad95d5c94b54c2736254",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "8a92761b231d23771a1bf11a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "c003cf76e1178e2d54021beb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "a085c742bd371e498790d424",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "79fcea01f024316a38d199cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "c01ff90283703918140f0393",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "1b4ccc161225f7ebf71f66f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kfn1.md",
      "chunk_id": "9ab56905e2cd6fd2ee51af67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "400761adea76e1e17ace9c10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "a2d47e19aa4a9056e738b1d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-10-31.md",
      "chunk_id": "71ab02757e0682cea32cfffb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "0f1d0e8926c782e50103676b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "7813b3c3604bcaa8d67a26e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "c66bdca232f6ae378fbd8e43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/C.md",
      "chunk_id": "1a3b948cfa4a5b7725721bf2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "d1e9d720dd6275845c6ae50a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2d6f.md",
      "chunk_id": "8285d794cadd7aa7bc130d2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2d6f.md",
      "chunk_id": "1d09fa99e0aec08125cc1e35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-32-evidence.md",
      "chunk_id": "7549ac4e87f771d27c393d8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "d0b05f25252deea7d6bb2060",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "3082ddfeedadfa026639a739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "2c19f5687259d3be8ec82e57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "8706fa0e7decb83193a06c02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-13-review.md",
      "chunk_id": "cd395a2437555aa2af91f116",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-serial-only-1a-review.md",
      "chunk_id": "89aef17ff10828b0989bd2e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_unchanged.py",
      "chunk_id": "190685ae4aac2989216c195b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-serial-only-1a-review.md",
      "chunk_id": "0b22a24b0a73c3e8abb12ceb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "695776198a0a05dfd9c31ea4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RUNTIME.md",
      "chunk_id": "ca8ab85a755de4fabb4ffa72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-serial-only-1a-review.md",
      "chunk_id": "46046b94af5bdd5165502d75",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/attribution.py",
      "chunk_id": "ca439f4a2ccae4e19dca186d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qvff.md",
      "chunk_id": "9b315e2d52f620967a06d6c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/skills/test-design/test-kinds.md",
      "chunk_id": "2ff77da1b78ed8dc51ef077b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".rulesync/skills/test-design/test-kinds.md",
      "chunk_id": "d59ede97a6289fc528571a91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/.rulesync/skills/test-design/test-kinds.md",
      "chunk_id": "788e1625cbaf25eec51263d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RUNTIME.md",
      "chunk_id": "7d2dfaa9d81bd749ed4651f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-phase0-reds.md",
      "chunk_id": "a14457d0075c1460f7f7202e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST.md",
      "chunk_id": "3fa992e5b341c16b67b9233e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-115-smart-close.md",
      "chunk_id": "451008122d99d1611844bf0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "13129b7efb7b1fbc9e9439d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qvff.md",
      "chunk_id": "c7d7c385458b3a5d9a03180d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-serial-only-1a-review.md",
      "chunk_id": "a2a30948c66d6c75cfc586c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/test_w2_112_retirement_act.py",
      "chunk_id": "2f5945a6cacbe42f5647df6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_support.py",
      "chunk_id": "58f0a28b9e76e9f0e85625c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-lifted-breadth.txt",
      "chunk_id": "9adf60753a4826c0773f015b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/test_w2_112_bundle.py",
      "chunk_id": "bece48189751e42403c1dca0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/w1_19_support.py",
      "chunk_id": "6c3b78282d9924a8db3ae126",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_unchanged.py",
      "chunk_id": "ef8d91a7a0cbd2a77adec7e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-lifted-breadth.txt",
      "chunk_id": "9cf83eb695cdb6278762c453",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "bc3803867580b96536d615d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/w1_19_support.py",
      "chunk_id": "1b956ff99d8ec0330301d0b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/serial-only.txt",
      "chunk_id": "134bb92d32305d44c427a8ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-21/README.md",
      "chunk_id": "4829d34a041fe2200a7f71bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "c70eb65cd60e31806269b79b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/w2_112_support.py",
      "chunk_id": "38984ede5c34b82a87e9b9bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/test_w2_112_fallback.py",
      "chunk_id": "25b1d3a9e2e1e29fd6a24e73",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "1077fbbfea57b64d98a10d62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "c39f37324c8791cd8989a6fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/test_w2_112_bundle.py",
      "chunk_id": "2f77a57f6b28a703ea4b0c87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/w2_112_support.py",
      "chunk_id": "feccf8c668abd50487a5b34c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/w1_19_support.py",
      "chunk_id": "e0966cff656cd6f7e3e3f073",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/test_w2_112_bundle.py",
      "chunk_id": "c362863e7d3dc612003c18bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-21/README.md",
      "chunk_id": "4692fe37f71e1611635e2280",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "fd345cdfeb45695b631ae5f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/w1_19_support.py",
      "chunk_id": "9f04bca39c262983fcefd20b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/standin/w2112_unix_over_tcp.py",
      "chunk_id": "be52976705ecd75d89bc2867",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_roles_support.py",
      "chunk_id": "4df5065cf9213fca3a6ec56e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_roles_support.py",
      "chunk_id": "34b26e14075f672fd744ce2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_roles_support.py",
      "chunk_id": "32cbbd31f82d4f613eaf91ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/test_w2_13_role_separation.py",
      "chunk_id": "1f67d0020b688d0cd3e28c31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "b5a9300a9f2d058f38d86761",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "99fec3ba1778f1337896387d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/w2_112_session.py",
      "chunk_id": "28b48fee4a1dd5b712a48a1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/w2_13_lexical_policy_support.py",
      "chunk_id": "d5c84cfd3dab39be0cf699cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/w2_112_support.py",
      "chunk_id": "1870468fdf9fa74367629faa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-112/standin/w2112_standin.py",
      "chunk_id": "31e69ce9c887195c3928aae8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "fa2158eef024c42307946673",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "c57c6e6aca921ea82022ca5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/README.md",
      "chunk_id": "76e008d0e66dfaadb2c9ef0b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/w1_19_support.py",
      "chunk_id": "072ac6befd418bb19b8a03d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "0023ab5ed0da52eaddbcc287",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "23ac1fb63ac9c15380e6840e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "a4280745141ab103cd9051f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "6f042005cd5865fb7cec87bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-clon/PR-DAEO-clon.md",
      "chunk_id": "12cf3bfdf71d7b60979d95fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-clon/PR-DAEO-clon.md",
      "chunk_id": "3352f9df65a404520fed534b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "49b5fabbf5250e6e3f778dbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-137/test_w2_137_s4_memory.py",
      "chunk_id": "f799448ce45b051d490b357b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "52388927d8a5e29443323b04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "1ae2bad72b2eecd57e2e86fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-56/w2_56_sandbox_support.py",
      "chunk_id": "9a64ecab853ac6d42fef2b47",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "b516ad111db90d07085f1106",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-53/test_w2_53_accepted_reds.py",
      "chunk_id": "1bfb8cf986a8f87ef6338229",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/close/test_ratchet.py",
      "chunk_id": "8912822891ba14e571840320",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/w2_145_support.py",
      "chunk_id": "632cb8b777d2e9293ad44917",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-137/w2_137_support.py",
      "chunk_id": "8cf91d3758b31704e1ce7744",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/test_w2_145_s6_revisions.py",
      "chunk_id": "ea02dce544d026c16b0a41a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "05b71f5ca3ac2b3f41a9773f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "11c7d07628fc7cfe06da74c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "ce6ade098c444a0a344f73a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-weekly.txt",
      "chunk_id": "3e12da4b4ef94464e9732be3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-53/test_w2_53_ratchet_core.py",
      "chunk_id": "ed0aa9f397b5968bf7acba77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "7bb7208395f44ee7d71426d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/w2_145_support.py",
      "chunk_id": "d7aec848d448e40ddde0d67e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-53/test_w2_53_accepted_reds.py",
      "chunk_id": "47698e5a51eca872983e5bc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "f0a1e3a60a4ed8d175863450",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-146/test_w2_146_reader.py",
      "chunk_id": "be192225307cba415e3f84e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/semantic/test_rerank_process.py",
      "chunk_id": "9a9b9e1b9d19ccc355a5d421",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-53/test_w2_53_ratchet_core.py",
      "chunk_id": "f1fbb29f6625538988473075",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "a6b983ac110ba79d3fda5cbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "a01c559d05ce2fe0e8e25dc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "9599d4bb62b388800e351539",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-146/test_w2_146_reader.py",
      "chunk_id": "f4b41bebc97dfd92153af578",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "6808bb603eeccefda036164a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "bb6b04c3621b4b4244b614c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "2e8c76863d6346600818914d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "56a6e66f1c8d0b70e81b3d32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-30/test_w1_30_r11_declared_here.py",
      "chunk_id": "de25bc7d7e0e8f3bf3d65b35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "9941318ea72a3231ed080afe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "42e51d373f1ae536b5dde8a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "62e8ae328672bea744ad6731",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-137/README.md",
      "chunk_id": "382ef16107b09c7350bde453",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "7267abf577fc9e5ad96f01de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "c6e72b523c77aa52ef8067b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/README.md",
      "chunk_id": "fb58d9064c047e7c0a75ea18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-kfn1/PR-DAEO-kfn1-review-1.md",
      "chunk_id": "0681930975201cf31735f972",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "96d1aaed9f3275d96c01391e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "0379eac5a622a6b65159ca2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "927b38745f219786b5edf668",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_13_rerank_work.py",
      "chunk_id": "ce67958097f45fef4202a166",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "fb8d58e48eda67710dc29dfa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "f63eb7f8fd1d925b1316c46d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_13_ranked.py",
      "chunk_id": "22059dde1ff9ba4dd418c041",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-66/test_w2_66_live_test_map.py",
      "chunk_id": "8ed210b72e9498b5578ca300",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-137/README.md",
      "chunk_id": "770af957966539584fa1216b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "f6939f951a96e5896b48a0c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "39d2dfe12cdfd0c70db7c83e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "35f4cace8ebaeb85306a9e34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "12c6fcd9263255975ae9cffe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/README.md",
      "chunk_id": "e48dbbdc3ff95aafd6824d60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "c8ccf952469cd171e30d897b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "6450329fd9ea0a06a24ce510",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "c85d5ef3eb48e7b64fab8cd1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "05f6c49b48df9f671f4d5f36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "5baefce3fec1c75dbd7bfb6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "c46753d0d3d221ce1d30aced",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/README.md",
      "chunk_id": "9a77a55c9fd7b09f55751313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-zmo4/PR-DAEO-zmo4.md",
      "chunk_id": "eb8ea86900207f44cef40717",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "deed411e55684f35c942709a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/orchestration/test_dispatcher.py",
      "chunk_id": "c9335966058cc049464b1c01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/README.md",
      "chunk_id": "2bfa07e2a6fc52dcc3f8e8e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "a3d029673e999a012a95c034",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-91/w2_91_support.py",
      "chunk_id": "83120c9fe72b72e62bcc0a25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_unchanged.py",
      "chunk_id": "c4a44cb89b4171a6e9490b4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "c6ed8f5d6d0f5a9cee467959",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_unchanged.py",
      "chunk_id": "b29c67734b9d7a91441da6e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "e84b63d5d3ab56c3d957f470",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-66/test_w2_66_live_test_map.py",
      "chunk_id": "8be6b989e83827bd27f052c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/C-decisions-to-spec.md",
      "chunk_id": "5621c2c9d5e077bbb3971352",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-0rfi/PR-DAEO-0rfi.md",
      "chunk_id": "4190302d0209f5f48560ee1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-61/README.md",
      "chunk_id": "f38b181157ac62700253724a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md",
      "chunk_id": "fb174bea86441778c5ad82ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/contract-current.md",
      "chunk_id": "477e320052996b4744dd37b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "19c6595a9abef66a4ed8ef1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-108/w2_108_support.py",
      "chunk_id": "a7ab3b39ce32f1a4549e8589",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/README.md",
      "chunk_id": "31162e8fe1f5b26d8038cd3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "e35be61954fa4c5e0b908535",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "c4247754882235cc970af73e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/w2_145_support.py",
      "chunk_id": "76581f1f039afba8d973c980",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "8217b1bf838bc6901039a0a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/conftest.py",
      "chunk_id": "ab642d0072c496e0db6a3980",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "9fb6dfde5ebe25e0a1f29f38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/test_w2_145_s2_no_private.py",
      "chunk_id": "6df0fc9419bc20b3a03a392f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "cab53ea97e16c9212c5a964e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/w2_87_support.py",
      "chunk_id": "e97a54e95e8246a75307331f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-61/README.md",
      "chunk_id": "ac7e126a1706d7f8655b095e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/dec-1047-aim.md",
      "chunk_id": "6c060e7980c77e32f8c1543f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "34ee60402defd2fb1a55005b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "b457f546cf96a61849d2707d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/README.md",
      "chunk_id": "7e88e05a660939f1df48b8a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/test_w2_145_s3_slots.py",
      "chunk_id": "74fdecc0bbd81fb186c1fa39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "87586d92e943a59e88432367",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "ddf7fd490e018b02a60145cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "abe84ea9c19a05fb2d4b9f19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "4f4193b1bcfa7fd50989ca62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "99f0c7809d747191fca3d628",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/contract-current.md",
      "chunk_id": "81161b889a83d2b5bed89ddd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "3f8c3617522c71cb9c773011",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-21/test_w1_21_merge.py",
      "chunk_id": "6338ace15c527f1088c71b88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "555f816c7da28f1076cbc959",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "cbaab058bc7948c272ba7bf1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "a05103f3e6b16e07742a7516",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-weekly.txt",
      "chunk_id": "fa84783fda9e987fc604c227",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "8c0ebf093587b5c7507f34ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "d21d86bcca467c8dc0039b89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/semantic/test_fusion.py",
      "chunk_id": "2b131e75fef36685090c0218",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "7ccaf6912a3b602d2c532b82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-15/test_w1_15_filter.py",
      "chunk_id": "01d2419e4b05807ec9215d6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-32/README.md",
      "chunk_id": "d6e74cfb1dead48ec701dfbe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "89eeadead98b2a6b059fe46e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "921468ce0a8b8336b56b54ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "51c22cc341df57820a285431",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md",
      "chunk_id": "afbcea0bf9843b362d6d57db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "b527a49aa286071737c4e715",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-203/README.md",
      "chunk_id": "72d09a8f49d3f2b57283764d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "0d72d7f54f19ce8895c8e980",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "d010403db40ee7b6cbd77ad4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/w2_87_support.py",
      "chunk_id": "fbc39739e22ecb3f5182f810",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "3dc579b2eac3ce0fb7906a96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-200/README.md",
      "chunk_id": "a751228fe14ef262672f2485",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-lifted-breadth.txt",
      "chunk_id": "a662d0b0a43afee10dfb4199",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-200/README.md",
      "chunk_id": "d860745237d63439547bf497",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_unchanged.py",
      "chunk_id": "6da53c537a844d03da3f6f29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-32/README.md",
      "chunk_id": "11794995fd47fbd09ac1cd6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/w2_92_support.py",
      "chunk_id": "16a1f9b81d077b2d13f8b32d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-p8tv/PR-DAEO-p8tv-round-1.md",
      "chunk_id": "9dbeb866ae95308c1f39f0ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/w2_145_support.py",
      "chunk_id": "8f3814fa4802fb396ba03cf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-30/test_w1_30_r11_declared_here.py",
      "chunk_id": "24e6f2c24a4163c2c74a7c7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_unchanged.py",
      "chunk_id": "bc872134edc3ec14937c37e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/README.md",
      "chunk_id": "9bfff17f616e46e182f37695",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/standin/w145_slot_rule_worker.py",
      "chunk_id": "81169f5ecc9201286c32cbe9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-22/README.md",
      "chunk_id": "f95befec96ab12bd964ddbe9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-16/README.md",
      "chunk_id": "644faaa964c85d5c13deb412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-66/test_w2_66_live_test_map.py",
      "chunk_id": "0840cd5d239b98e232a428a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-21/test_w1_21_merge.py",
      "chunk_id": "304927453fb4ed50d6cef1ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "6db26606115f268946fe7aa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_13_lexical_policy.py",
      "chunk_id": "ae57c6cbf59f442948e2aeab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "40b64d3ac081f4ba0b4dc5a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_92_routes.py",
      "chunk_id": "f46d7791a54d17d91bcf8fe4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "7c98bb33cdecbe19a5e97788",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "1cd0113771eb1b592e50b1d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-122/README.md",
      "chunk_id": "91b428dfce9ff9d758269ea5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-66/test_w2_66_live_test_map.py",
      "chunk_id": "130c53970e1a455e2741db6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "76fbd64a3f9c3e6ea9bda6b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "d3a3fec997ae7b838dd45a89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/serial-only.txt",
      "chunk_id": "9c9d3af8f68349ad10d02a55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "78e20c4c6f100e6a98b5975c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "aacfa334bc47a45e8dd6b312",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md",
      "chunk_id": "93cb75498e736e4ddf0c7d66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "0fb9652c527ca4b9480cdca3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/w2_145_support.py",
      "chunk_id": "233d9b0978fd6bb59b4b3969",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "5b66e106d5ea3beed09ce376",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "7805f3bfd3497c7ba2f6fefc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/test_w2_92_fail_closed.py",
      "chunk_id": "ebd8b0a196bd481094852557",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "484bdeb5768e808cff7b19ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieve/test_w2_13_stated_gap.py",
      "chunk_id": "60e5331d9f07a727829e5cc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/w2_54_support.py",
      "chunk_id": "d03c6ef5d2b1dd5d1f5755fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "bc6ffcf6247065eca5eb5957",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/semantic/test_semantic.py",
      "chunk_id": "9787de66916fd9342b3d2409",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/w2_87_support.py",
      "chunk_id": "c4bf86d19f5443d1b25bab88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/w2_92_support.py",
      "chunk_id": "1d9fb15bbeb64ea3fe6fc1c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-137/w2_137_support.py",
      "chunk_id": "ce806e84986bc8eb1e038734",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "06b12f11a5975ea031a8f99c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/orchestration/test_gov_reranker_gpu_slot.py",
      "chunk_id": "dc04f276edd7a536f4507207",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/test_w1_41_embedding_policy.py",
      "chunk_id": "c1fb239bc836a53584ef8527",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "e95e906a1016fcc9ce8bcb48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/status/test_status.py",
      "chunk_id": "ff762b72acb6a96772eb8035",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "03dd9c33c9ae1048e69d0488",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-56/w2_56_sandbox_support.py",
      "chunk_id": "70d2c827ad225e29b3e2df4e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-21/test_w1_21_family_check.py",
      "chunk_id": "7f6fc90db96ac784e8350920",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/orchestration/test_dispatcher.py",
      "chunk_id": "91a74a2ad03ace2f21c5c6e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "95140aeac218ca9ff33daf6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "a28d7085339cec168a47c6c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_13_id_boost.py",
      "chunk_id": "cb8a405f9d76a8d850309423",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_13_role_filter.py",
      "chunk_id": "e905dd579354098e7cffa397",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "2a9b76cf5ab474e93e16f5e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-32/README.md",
      "chunk_id": "6220732b0e68da1a12c14aa8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "5e27a2f95b649624d59c5873",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "690d3abcbcaeb1b061a2fca4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_rebuild_r2.py",
      "chunk_id": "15666266334fd5ac8998ead6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-108/README.md",
      "chunk_id": "920c597b223421da7b6dc134",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-200/README.md",
      "chunk_id": "839a934890fbabdcc4dc74de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/test_w2_87_authority.py",
      "chunk_id": "19bf44465ee1cb8f41b427c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-137/README.md",
      "chunk_id": "f25fbf2a252a38a8b574ad8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/w2_92_support.py",
      "chunk_id": "68500d9f6a3fb28232c592ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-137/README.md",
      "chunk_id": "09efc9cdd70a0c2f09c95eaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "453a2683225cb18d5f445f56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "99111fe4fbe69f711275a526",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "e33370a3bc1587770777edbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "a15c4014cc86915309397d3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "94cfe92b400bd65a67983c41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "495b97f72a2ed961a3690ece",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/semantic/test_rerank_process.py",
      "chunk_id": "5a173dfcd6f06e47d75017f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "de5a260428dd3d3dd297634b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/w2_87_support.py",
      "chunk_id": "c69b66488fd55ca6e8876607",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "1461df32aab261702c1149e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-108/w2_108_support.py",
      "chunk_id": "19228e4d34dcf551f5a33842",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "9dd202293e8235a584e1352f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-22/README.md",
      "chunk_id": "3474edf60768979914a03bc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "328553f6b66fd1fa21bb28b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "74a6eff9d57999952ac494e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "faebe3a7c419636fb2402f5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_112_shared_reranker.py",
      "chunk_id": "79f11cde5717e638ac01edfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-15/README.md",
      "chunk_id": "2e732741d37e14a83c638ac3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "5fa773655f2a14f1ec071aff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "6615b2d880b78bb659329e74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-10/README.md",
      "chunk_id": "63bb2a53eb42905b74b61c32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-30/README.md",
      "chunk_id": "4386f207af0a6ae490bb1d51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-50/README.md",
      "chunk_id": "d7ce591d027c7bc66b97f9a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-150/README.md",
      "chunk_id": "202e9f85d31f9791aaf749a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "bd2da4777914ff739964e2e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/test_w1_41_embedding_policy.py",
      "chunk_id": "8a4449a87f5d18cc6520ff96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-0rfi/PR-DAEO-0rfi.md",
      "chunk_id": "ad21a6a2f9546f74a9faa79e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-87/README.md",
      "chunk_id": "fa1ba72aefce89c693302159",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md",
      "chunk_id": "cc6458cec9b00873273f7d8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "f48c0810839b64edd845940e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md",
      "chunk_id": "90118d12760163a0597f9df6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "f541b93beae68236b0dca396",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-145/test_w2_145_s3_slots.py",
      "chunk_id": "723fa34e5a7b7369c700ef57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-2bdu/PR-DAEO-2bdu-p1-check1.md",
      "chunk_id": "71f6e9342d81f87925ef614e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "6520331201109d6f3cad20ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-kfn1/PR-DAEO-kfn1-review-1.md",
      "chunk_id": "7f2791395cfc50c7aef6ce19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "4cf5011409a322fa21d1738a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "fe4b0851848813d520eef063",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md",
      "chunk_id": "21481742627ba630e9b30059",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-30/README.md",
      "chunk_id": "c2cfc05ae2f0280401737e01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "9074dbcc033d9af3772ce225",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "64ebb18c2b5021476f8c25ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "0d5e29f1e3fa35d4b4a25fc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "ebd38a8700dcc8a2f22e9837",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-kfn1/PR-DAEO-kfn1-review-1.md",
      "chunk_id": "43a4ef04dc8852f372b1969d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md",
      "chunk_id": "59180e5d55800e41c477bf62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-b6hm/PR-DAEO-b6hm.md",
      "chunk_id": "42e66d2db97fc70e60f2574d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-0z8c/PR-DAEO-0z8c-d10.md",
      "chunk_id": "f9e34f0dcea90a9433456897",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "dc6780d5089548bff4ad4f4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "0faf23ca0699fd182586d6b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "b049ec4b817346e419b42aad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-kfn1/PR-DAEO-kfn1-review-1.md",
      "chunk_id": "87b43162a5c9db97d0d0770d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-kfn1/PR-DAEO-kfn1-review-2.md",
      "chunk_id": "01fd323bb94dec5b94481deb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-15/README.md",
      "chunk_id": "3649e0e65af00f4f714bfe00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-0z8c/PR-DAEO-0z8c-d10.md",
      "chunk_id": "c66e149fc73117500aafa748",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "42c4b98994ea128ec8209ccb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "e85d9e983400b045caee0ef3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "30241f074148a762df543857",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "bcaf4dcab229f54f9c06c557",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md",
      "chunk_id": "b414179756318e5a98929147",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "3c6ba15cf80c5af7de5f0e57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "e24b13343b46fec9b457218d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "b234bde27eadeec190c9a56d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "59ef4fda4b9f242fff86b189",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md",
      "chunk_id": "3298169c737423c0e1305a9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md",
      "chunk_id": "692b0746e82659cf8131040e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "e0dd78c8a9bd5ac9a6f415de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "28d7cd068182b2a05c871ef3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "dc75a6f92424cd135154ae26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "7b627ece5a054b4993c07820",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "f4f32755b89f79b8d8c20643",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md",
      "chunk_id": "e59d44e5f2a27f2a00ef0a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "1aed8650b2e74b1406b674a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-kfn1/PR-DAEO-kfn1-review-1.md",
      "chunk_id": "a1b8e2738782d159972ce2c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "12264868883ce72ffed51f4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "5fb3692dfb44492c75e8a63f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "a5a4b6f4c042270d20f76557",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "3b725e6e496b8215b606a134",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "5d64f818937be855cdb78f59",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "0b56203b7ce819cbb1780823",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "c274d7925efaabca1678099e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "8901ba9cb70b6dcc3a0af9fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "8aaeba3606ea1d9b0c66ca96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "4068f89c7773620466782966",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "71626ad4939413ff1806e8ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "aa69643c8ad35a7729dcc442",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "5722f853c7ff4160205888f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "a927d6cf482e0fe5bfdf891f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "924620bc9323cd1c01c36f5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "60da65d185f2c87ce82323e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "53a744f91d6361d825dfb443",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-92/README.md",
      "chunk_id": "51f07179f91aa2a8b5499a13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "de40ea76c305879a4c5e44ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-30/README.md",
      "chunk_id": "eeec12e383a499ea25fd599d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "fa6a276b424debab3a00d2aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "8e81da778d809b141cb2e336",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "12602a0a6d9e94b915da0206",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "2e691db2ab2a4b66689b55dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "ba6ee6bb2839820c1d6a05bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "604952f416009c863fd3806f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "7728f942fce43d664aa97071",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "2c94350600af7efcd5df208d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-kfn1/PR-DAEO-kfn1-review-1.md",
      "chunk_id": "30e71346227ee2cc8838df39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "3b2d20234c2c68639639a8a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "34f95bb976ddce6a5c0f1520",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/serial-only.txt",
      "chunk_id": "f10d20497dcdd5dea98fd53d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/serial-only.txt",
      "chunk_id": "6913a48384dcbdb755be9d11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "5f9a59cd1ec558dff04a5089",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "7ea2691ffdb8ba0c80222070",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "a749c51923a13748275aa5b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/close/test_w2_115_close.py",
      "chunk_id": "4ded5566790c49d73376648a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/close/test_w2_115_attribution.py",
      "chunk_id": "5ee04fe69d28782cd3ffa95f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "5ba819abaac9ffe9f75e4829",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/README.md",
      "chunk_id": "ba8f951ea2cdaf4ca00a904d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "77e6899ae785d39004acdf87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/conftest.py",
      "chunk_id": "2e8f150c040c4171e356db98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-11/test_w2_11_round2.py",
      "chunk_id": "de1d568a3dc14be14bd30e37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/close/test_w2_115_attribution.py",
      "chunk_id": "cfd4793eeffafbf07e7a0ea2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "5e2c57bc130964840e2ee311",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/close/test_serial.py",
      "chunk_id": "b0a223be9e4586594dfdaa35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-13/test_w2_13_latency.py",
      "chunk_id": "5c8de8e5534eafb2fca9533b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "a69986d4155c0389d495b8e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "b2b1da9b1fbbae9335fea9d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-57/README.md",
      "chunk_id": "25b7703dd36779e27081b5a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "5da45d74060fe6444e0b5a7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-19/test_w1_19_real_models.py",
      "chunk_id": "126f989bb798a328c80e3ff0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "bae0598450cf5d5cc1fafe1d",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    },
    "closure": {
      "available": true,
      "reason": null,
      "followed": {
        "records": [
          "ADR-0002",
          "DEC-979",
          "DEC-1032",
          "DEC-860",
          "DEC-1052",
          "DEC-1065",
          "DEC-1157",
          "DEC-1158",
          "DEC-1217",
          "CAP-43.b",
          "CAP-45.a",
          "DEC-728"
        ],
        "left": 5
      },
      "changed_by": {
        "DEC-728": [
          "DEC-953"
        ],
        "DEC-979": [
          "DEC-1157"
        ],
        "DEC-1032": [
          "DEC-1158",
          "DEC-1157"
        ],
        "DEC-1052": [
          "DEC-1217",
          "DEC-1157"
        ],
        "DEC-1217": [
          "DEC-1241"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5711
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLWFyODkubWQiLDI1LDI2LCIwNzg3NzdmN2IxYTYwZGYwYTNkMDhhMTQiXSxbIi50aWNrZXRzL0RBRU8tYXI4OS5tZCIsMjYsMjksIjE1NWRhOGE0OGJjYWVmYjRlYmZkZGUyYSJdLFsiLnRpY2tldHMvREFFTy1jbG9uLm1kIiwyNiwzMywiMzBiNmRhOTIzYjFlNTIxOGRmMjUxNjJiIl0sWyIudGlja2V0cy9EQUVPLWNsb24ubWQiLDQ2LDYxLCJmZTU0MzA0NjhlN2VkMWY1ZjM4NzdjNzUiXSxbIi50aWNrZXRzL0RBRU8tY3k1by5tZCIsMzEsMzQsIjgzYTdkZDYzZGRhODk4ODRmNzc0MDUzZSJdLFsiLnRpY2tldHMvREFFTy1tYjJ0Lm1kIiwyOCwzNywiODAzOWY5YmVhNTg1OTAzZmZhMDYxNDI0Il0sWyIudGlja2V0cy9EQUVPLXF2ZmYubWQiLDk1LDk4LCI2Yjg0NjY2YTA0N2YzNTRlZjUwMmIzYjIiXSxbIi50aWNrZXRzL0RBRU8tenF2bi5tZCIsNDgsODIsIjg5YWRjOTk2NjE4MDA2ZjAyNDRkYjYxMCJdLFsiLnRpY2tldHMvREFFTy16cXZuLm1kIiw5OCwxMDMsIjUyYjc0ZTE0ZGVmNGJjMjYxZjIwYjA1ZiJdLFsiLnRpY2tldHMvREFFTy16cXZuLm1kIiwxMTAsMTE2LCJlYWY0OGI3NTg1MTQzZjc3NDgwNjgzNDciXSxbImRvY3MvY2hhbmdlcy9XMi0xMS1DSVQtUC5tZCIsMjE5LDIyMiwiOWFhMWQ3MjQxNGVjODhlYjMwNzExMmM5Il0sWyJkb2NzL2NoYW5nZXMvVzItMTMtZXZpZGVuY2UubWQiLDE2NiwxNzksImUxYTEzZGU1MmI2YjM0ZjkwYjU3YWRiNiJdLFsiZG9jcy9jaGFuZ2VzL1cyLTEzLWV2aWRlbmNlLm1kIiwxNzgsMTkyLCIzM2FiM2FkMGZkZTUwYmU5NTBmNDM4ODAiXSxbImRvY3MvY2hhbmdlcy9XMi0xMy1ldmlkZW5jZS5tZCIsMTkxLDIwMywiZTI0YTVkZjg3ZGJmZjQyZTQxNmUzNGYyIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0dPVi1PUy1ERUNJU0lPTlMtMjAyNi0xMS0yNS5odG1sIiwxNTgsMTgyLCIyYTVlZjljNzE4NGJhYjMzOTlhNjRiYzUiXSxbImRvY3MvcGxhbi9XQVZFXzJfV0JTLm1kIiwxMDk3LDExMTQsImFmMjUzN2VkNmE4NjYyYjkyODQwMTQ4NSJdLFsiZG9jcy9wbGFuL1dBVkVfMl9XQlMubWQiLDExMTIsMTEyNCwiMTgyNTQ3OGMzMTNlOWY4NTIyNjZiMThhIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9JTlZFU1RJR0FUSU9OLTEtQ09NQklORUQubWQiLDY1LDY1LCI4ZjIyMDg1ZGRjOTM2NDU0YTNiMjc0NDQiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL0xJRlQtMS9EMTAtUkVEUy5tZCIsMjEwLDIxMiwiZTM5YmM3MDBhOGI0OTEzZTA4YmY2NGY4Il1dLCJmIjoiL2hvbWUvdXNhaW4vRHluYW1pYy1BZ2VudGljLUVuZ2luZWVyaW5nLU9TIiwiaSI6W10sIm8iOjIwLCJwIjp7ImIiOiJzZXJ2aWNlIiwiZCI6ImN1ZGE6MCIsImgiOiIzZDc5NjI2MGU2NzkzNWY0IiwibyI6WzIsMjEsMjQsMTYsMzcsNywyMCwxMCw1LDE3LDE5LDMxLDI2LDAsMzksMTUsMjMsMzMsMzgsNCwzMCwxOCwxMiwxLDEzLDE0LDM1LDYsOSwzMiwzNCwyOCwzLDI1LDM2LDI3LDIyLDExLDgsMjldfSwicSI6InRpbWluZyBhc3NlcnRpb25zIGluIGFjY2VwdGFuY2UgdGVzdHMgVzItMTEyIFcyLTEzIFcxLTE5IHdhcm0gbGF0ZW5jeSBib3VuZHMsIHRoZSBzZXJpYWwtb25seSBsaXN0IGFuZCB0aGUgc2VyaWFsIHBoYXNlIG9mIHRoZSByZWxlYXNlIHN1aXRlLCB0ZXN0IHBhdHRlcm5zIHRoYXQgcGxhbnQgdGhlIG1hY2hpbmUgcmVhZGluZyIsInIiOjAsInMiOiJjMWU4MWFmZDNlNzU2MGU3YThmNzY5YmI1MWRlMDgzYjA3ZDcyMTU4IiwidCI6bnVsbCwieCI6WyI3OWY5NjMyZTIxYTQwMTdhZTM1ZDc5MTkiXX0=",
  "routing": {
    "code": [],
    "named": [
      "eaf48b7585143f7748068347",
      "fe5430468e7ed1f5f3877c75"
    ],
    "phrasings": [
      "timing assertions in acceptance tests W2-112 W2-13 W1-19 warm latency bounds, the serial-only list and the serial phase of the release suite, test patterns that plant the machine reading",
      "timing assertions acceptance tests W2-112 W2-13 W1-19 warm latency bounds serial-only list serial phase release suite test patterns plant machine reading",
      "timing assertions in acceptance tests W2-112 W2-13 W1-19 warm latency bounds, the serial-only list and the serial phase of the release suite, test patterns that plant the machine reading DAEO-clon DAEO-zqvn"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": []
  }
}
