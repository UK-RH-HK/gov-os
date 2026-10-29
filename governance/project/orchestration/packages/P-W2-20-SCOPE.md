# P-W2-20-SCOPE — W2-20's built gate contradicts DEC-942 and DEC-947: re-scope it, merge it as built, or park it

From: the W2 orchestrator, 2026-10-29, sent the day it arose (DEC-949). Your decision: it adds a lead run to a held ticket (DEC-817).

## 1. Context
- **The ticket:** W2-20 (`DAEO-r30l`) is the machine-wide resource gate in the product. It is one of the nine held tickets to be merged back (DEC-941 item 2), and in priority 4 (DEC-946).
- **Its branch:** head `1a54976c7a71`, worktree clean, 10 commits ahead and 789 behind. STANDARD, with no probe. It has been held since 2026-10-17 for the close order (DEC-737).
- **The rules changed since it was built:**
  - DEC-942: the load below `nproc`, no fixed number of leads;
  - DEC-947: memory reserves the floor, one verification run's peak once, and a working size per lead; the floor is 3 GiB;
  - DEC-941 item 6: the capacity minimum in W2-20's KPIs;
  - DEC-898: the disk and inode floors.

## 2. What happened
The merge-back helper read W2-20's built `src/gov/resources/gate.py` against those decisions on 2026-10-29. It has:
- a fixed 4 GiB memory floor, with no verification reserve and no working size per lead;
- the 1-minute load only (DEC-942 uses min(1-, 15-minute));
- a ceiling of 8 weighted sessions, against "no fixed number of leads";
- no disk or inode reading, although that KPI has been on the ticket since `efa2e4b0` (DEC-898);
- no machine profile and no GPU (re-plan §7.4).

A dry merge also finds one conflict, in `tests/acceptance/W1-07/README.md`, which only a test designer may resolve (MR-3).

## 3. Why it matters
- **Merged as built,** the product would ship a gate that refuses what the owner's own rules allow, and allows what they refuse (no disk floor).
- **The orchestrator meanwhile** runs DEC-942/947 by hand (`tools/gate_check.py`) until W2-20 carries it.
- **Block D (K6)** waits on W2-20: W2-21 needs it.

## 4. Options
- **(a) Re-scope as W2-20 run 3 (recommended), after its KPIs are amended.**
  - The KPI edits:
    - its "values (DEC-742)" line becomes DEC-942 item 2 and DEC-947;
    - a success KPI: "the gate opens while min(1-, 15-minute load) < nproc and MemAvailable plus the running sessions' memory ≥ floor + one verification run's peak + a working size per running session and the new one; no fixed session ceiling; all values in one configuration [DEC-942, DEC-947, DEC-941 item 6]";
    - a success KPI: "a machine profile read at start: CPUs, memory, disk, GPUs and their memory (nvidia-smi when present) [DEC-941 item 6]";
    - a failure KPI: "a fixed ceiling on leads or sessions";
    - DEC-941, DEC-942 and DEC-947 added to sources, and `est_loc` raised to about 320.
  - Cost: about 1.5 to 2 lead-days, about 200 code lines and about 20 test cases.
  - Two design points need you:
    - where the product gets each session's working size (a lead's process tree includes its workers);
    - the GPU threshold.
- **(b) Merge back as built, and move the DEC-942/947, disk and profile KPIs to a new ticket.**
  - Cost: a short merge-back now, and a new ticket of about the same size later.
  - Risk: a gate that contradicts the rules sits merged until then.
- **(c) Park W2-20 until block D starts.**
  - Cost: none now.
  - Risk: W2-21 waits, and the orchestrator's hand-run gate stays the only one.

## 5. Recommendation
(a), medium confidence. It is the smallest path to a product gate that matches the rules you set this week. Medium, because the two design points could grow it.

## 6. What it blocks, and what waiting costs
- **Blocks:** W2-21, and with it block D (K6).
- **Waiting costs:** none today; the hand-run gate covers it. W2-20 is in priority 4, behind memory.
