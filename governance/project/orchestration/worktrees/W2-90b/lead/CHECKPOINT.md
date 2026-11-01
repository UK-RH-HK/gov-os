# Lead checkpoint — DAEO-nqa2 (W2-90b), run 1 — FINAL

Updated: 2026-11-01 22:00. Status returned: PACKAGES (work done and verified; P-W2-90b-1 blocks only KPI S4's two live-session harnesses).

## Branch
- w2/W2-90b head 73c18fea1e1f (records-only checkpoint commit) on verified head d2408361d185.
- Commits: 50934f4a2855 merge of w2/integrate (lead; the CTO's claim a94b3504 so gov launch saw in_progress); 591199ea16a0, 10adc4c1e5aa, 7ce46d8b39b5, d2408361d185 (independent-test-designer, all trailers incl. Rewrite-Reason: DEC-953 item 2); 73c18fea1e1f (lead, CP-DAEO-nqa2-0004).
- Diff vs 50934f4a2855: 11 files under tests/acceptance, +526 -41 (estimate ~300).

## Results
- Baseline (ticket files, parallel close form): 1185 passed, 9 failed, 2 errors, 1 skipped.
- After, scoped parallel (select_tests: scoped, core_changed [], unplaced []): 7016 passed, 8 failed, 1 skipped (2946 s).
  - 4 W2-90c (need W2-105): W1-05 orchestrator-asks [pip], [npm]; W1-46 research [npm-install]; W1-33 install [orchestrator].
  - 4 tests/unit/launch/test_runs.py: fail only when TMPDIR path contains "W2-90"; 6/6 pass with TMPDIR=/tmp. Residual.
  - skip: tests/unit/retrieval/test_lexical.py (govbridge missing; pre-existing).
- Serial phase: killed at the 2 h Bash limit (80 min slot wait). 182 collected; 179 passed up to #181; #165 W1-19 warm p95 F (load_sensitive; alone: F 4.166 s); #181 W2-54 time_limit F; #182 W2-54 green_here unfinished (both judge this repo's context check, red alone for DAEO-i89t AR-5). Nightly-routed live cases ran in it and passed (W1-46 live sessions, W1-50 launcher, W2-54 sandboxed).
- W2-54 sandboxed live case alone: 1 passed.
- collect-only: "19072/19074 tests collected (2 deselected) in 14.86s".
- gov check exit 3: RED context reproducibility (DAEO-i89t AR-5), retrieval regression (hit@5 0.0 alone), secrets indexing (green alone); YELLOW authority/role limits, product traceability.
- trailer_gate: "DAEO-nqa2: 8 commits, 8 judged, 0 lacking, 0 Implements item(s) not a decision or Contract id that resolves".
- keyword_warn: 0 files. Rebuild: exit 0, 3769 s.
- Scratch end: /tmp/gov-os-lead-W2-90b 447M / 52,087; .gov-runtime 485M / 3,315.

## What a resume must do
Nothing more in this ticket unless the CTO decides P-W2-90b-1 option (a) (then: a launcher/credential change in another ticket and a test round here). Land d2408361d185 (+ records 73c18fea1e1f) through the merge queue.

## Brief gaps
- Ticket claim on w2/integrate after the branch cut; gov launch refused until merge | this ticket's part | ~10 min
- Rebuild lock queue ~40 min; then rebuild_slot.sh (DEC-1001) landed on w2/integrate after the brief | common brief | ~15 min
- Live-session cases nightly-routed; brief's close form never runs them | this ticket's part | ~10 min (est.)
- Serial form "entries as arguments" runs all 182 list entries incl. nightly-routed and outside selection; passed the 2 h limit | common brief | ~2 h wall (slot wait + run)
- gov check --json carries no per-check detail; had to run each check module alone | tool | ~15 min
- W2-00-store retrieve hangs in the sandbox (ollama.com refused) | common brief / tool | ~2 min (worker)
- TMPDIR named after the ticket breaks 4 unit cases | common brief | ~10 min
