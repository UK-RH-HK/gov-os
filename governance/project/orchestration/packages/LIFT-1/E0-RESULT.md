# E0's result: the 138 through the live product on window 4's pin (declared in E0-DECLARATION.md, `dc5f0de0`)

Run on 2026-11-07, 15:58 to 16:33, by the CTO (session `ad44f5fe`). Counts only.

- **What ran:** pin `pin-bcea09060ebc` with the pool on, a measure clone at `c00d525fd420` (its store built by the pinned gov in 40 s, seeded from the integration store), and the live shared servers.
- **Kept:** the log is at `~/gov-os-runs/D4B/w4-e0/e0.log`. The outputs are in `~/gov-os-runs/D4B/w4-e0/out/{r80,r60}/`, and every search's ranked output is in `~/gov-os-eval/runs/w4-e0/`.

## The figures (`drafts/d4b/e0_figures.py`)
| set | hit@5 | hit@10 | hit@20 | MRR | in the bundle | full evidence |
|---|---|---|---|---|---|---|
| visible 40 | 34 (85.0 %) | 37 | 37 | 0.6779 | 37 | 35 |
| hidden 39 (counts only) | 32 (82.1 %) | 35 | 37 | 0.5619 | 36 | 33 |
| spent 59 | 40 (67.8 %) | 46 | 50 | 0.4941 | 50 | 48 |
| **the 138** | **106 (76.8 %)** | **118 (85.5 %)** | **124 (89.9 %)** | **0.5665** | **123 (89.1 %)** | 116 |

- **Spread** of hit@5 between the sets: 17.2 points (85.0 against 67.8).
- **Unresolved anchors:** 0 and 0.
- **Median call time:** 1,237 ms on the 80 and 1,256 ms on the 60.
- **Wall time:** 19 min for the 80 and 15 min for the 60.
- **The GPU backstop never tripped.** The sampled peak was 8,404 MiB.

## Against S11's check of 11-06 (the clone's code at S11's merge, pool on; `~/gov-os-runs/D4B/w4-32-product`)
- **The overall figures:** 138 hit@5 106 against 108; MRR 0.5665 against 0.5669; hit@10 118 against 119; in the bundle 123 against 123.
- **Gains 0, losses 2,** both spent-set questions: m20 (first gold rank 5 to 6) and m36 (4 to 11). Exact McNemar p = 0.50.
- **14 questions moved rank;** 12 of those kept their hit@5 result.
- **Reading:** the pin answers as the code it was built from, within 2. The two losses fit two days of new records competing in the store (11-06 to 11-07: DEC-1085 to DEC-1088, the packages and the tickets). They are not a code change: the window-4 builds after S11 (W2-135's cut, W2-116, W2-129, W2-112's release, W2-134) do not change ranking.
- **The visible and hidden halves are unchanged** in hit@5.

## What it means
- **On CAP-10's floor of 85 %:** the 138's hit@5 is 76.8 %. The verdict set (the spent 59) is at 67.8 %, the honest figure DEC-1074 recorded, and it still holds. K9's bar is 85 % on the fresh 80 (DEC-1083), and it is not met by today's configuration.
- **In the bundle, 89.1 %** of the 138 have gold in the first call's bundle, and hit@20 is 89.9 %. The gap between the top 5 and what the bundle holds is what E3's end-to-end conditions measure (top 5, 10, 20, today's bundle, 40 unranked).
- **This is the baseline** for E1 to E5 and for G3's decision (DEC-1090 (4)). It chooses nothing, and the hidden half chooses nothing (DEC-1067).

**E0b:** deferred, as declared. The harness must be fixed first; it is needed only for E4.

**Spend (DEC-1089 (3)):** no model tokens. Searches ran on the local GPU servers only, 35 minutes of wall time.
