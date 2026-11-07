# E1, the search-again pilot: declared before its run, with one amendment to D4B-SEARCH-AGAIN (DEC-1087 (11))

The CTO, 2026-11-07, session `ad44f5fe`. This record is committed before the pilot runs. Everything in `D4B-SEARCH-AGAIN.md` holds except the one amendment below.

## The amendment: the product's bundles, not B0's
- **What D4B-SEARCH-AGAIN §2 said (written before re-pin window 4):** the retrieval was B0, through the score-once harness. The first bundle came from g-B0's kept outputs, and later searches ran live through the harness copy.
- **Now:**
  - the first bundle is the first call's bundle from **E0's kept outputs** (`~/gov-os-eval/runs/w4-e0/`: pin `pin-bcea09060ebc`, the pool on, clone `c00d525f`);
  - every later search is run live with the **pinned gov** on E0's measure clone (`~/gov-os-runs/D4B/w4-e0/repo`).
- **Why:**
  - SEVEN-ANSWERS §7, which the owner approved: "the bundles E2 to E5 give readers must be the product's";
  - E0 now gives the product's baseline (106/138);
  - the harness cannot run on window 4's code until it is fixed (E0-DECLARATION, E0b).

  B0 (with L3's lift) is not what ships. E2 to E5 follow the same rule, except E4's M3 condition, which needs E0b.

## The pilot (D4B-SEARCH-AGAIN §7)
- **Five visible questions:** the three whose first bundle lacks the gold in E0 (Q14, q23, q31), plus Q01 (gold at rank 1) and Q03 (gold at rank 6). Misses are chosen on purpose, so that searching again is exercised.
- **The reader, the grader and the agreement check** are as §3 and §4, with each call's cap at $1.50 (reader) and $0.50 (graders) (`--max-budget-usd`).
  - Every call runs as `claude -p --safe-mode --tools "" --no-session-persistence --output-format json --json-schema`, from the run folder `~/gov-os-runs/D4B/search-again/pilot/`.
- **The citation check, for the pilot only:** the gold sources' lines, re-anchored by their heading in the clone, overlapping a citation's lines. The full run uses the measure's own matching (with source families).
- **Script:** `.gov-runtime/scratch/orchestrator/drafts/d4b/e1_pilot.py`.
- **What it reports:**
  - per question: the verdict at each attempt, whether the gold is in each attempt's bundle, whether the citation is right, both grades, the tokens and cost of each call, and the wall time of each call;
  - in all: the cost per question, the cost projected to the 138, and the median reader call.
- **What it decides:** nothing about the practice. It checks the schema and measures the cost, for **the owner's cap before E2** (DEC-1086 C).

**Basis:** question 1 (the experiments measure the product as it ships).
