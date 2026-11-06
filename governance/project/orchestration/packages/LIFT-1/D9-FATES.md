# D9-FATES: every Wave 2 ticket's fate and K9, amended (for the owner; DEC-1039 (3b), P1-PLAN D-9)

- **For:** the owner. **By:** a read-only drafter, 2026-11-06 (restarted under DEC-1082 (1)), reviewed by the CTO
  (session `812bc5ce`).
- **Nothing is applied before you decide.** DEC-1052 already approved the W-rows (W-1 to W-10) and K-1 to K-4. Only
  the per-ticket fates and K9 are open.
- **After your answer:** an independent auditor checks the KPI lines' fates (792 lines), the edits are applied in
  batches, and a second pass follows for the link findings after W2-129 and W2-130.
- **The CTO's corrections to the draft:**
  - W2-61h S7 is built on `w2/W2-61h-s7` with its acceptance cases passing. It awaits review and merge; it is not
    "running".
  - W2-131 is in progress, with its test designer running since 11:15.
- **How changes are marked:** **Δ D-4b** means D-4b's work changed the fate P1-PLAN §C proposed. **Δ** means
  another cause changed it: D-1, D-4, or a ticket filed since §C.
- **What is counted:** 94 live Wave 2 tickets with 759 KPI lines, success and failure, from today's front matter.
  §C counted 92 tickets and 716 lines. The 43 new lines are in W2-128 (24), W2-131 (6), W2-92 (+6), W2-32 (+3),
  W2-13 (+2) and W2-61h (+2).

## 1. The fates, one row per ticket

### Keep (19 tickets, 157 lines)
| W2 | DAEO | status | fate | KPI lines and their fate | reason |
|---|---|---|---|---|---|
| W2-00 | sdxk | open | keep | 1 open | the main session's coordination ticket |
| W2-11 | k7hz | in_progress | keep, land as built | 19, met as built at its close; W2-128's lines later replace its template lines | built; DEC-1081 (2) |
| W2-23 | kmcr | open | keep | 8 open | W2-27 S3 relies on it |
| W2-28 | csj8 | open | keep | 2 open | the independent verdict on the copy |
| W2-29 | b926 | open | keep; drop the dep on W2-25 (retired) | 1 open | real adoption; gated by W2-15b, not K9 |
| W2-30 | 60rw | open | keep | 1 open | |
| W2-52 | siiz | in_progress | keep | 4 | W2-27 S2 |
| W2-60a | cv58 | in_progress | keep (S10 as is; G-12 refused) | 13 | roles at launch (K9) |
| W2-61h | h2k3 | in_progress | **keep, narrowed (Δ D-4b)** | 11: S1–S6 and F1–F3 met (`15592622`, `cd8e5420`; S5 and S6 re-worded to G-3 by D-8). S7 and F4 (source families, DEC-1079) are built on `w2/W2-61h-s7` with acceptance passing, and await review and merge | D-4b merged all but S7 |
| W2-81 | l78m | in_progress | keep | 17 | the proving ground (K9) |
| W2-90b | nqa2 | in_progress | keep | 7 | |
| W2-93 | 6y0x | open | keep | 7 | W2-81's held-out half |
| W2-94 | g87r | open | keep | 8 | EXAMIN's question set |
| W2-105 | zpdj | in_progress | keep | 8 | |
| W2-110 | 3r1j | in_progress | keep | 8 | |
| W2-116 | f58b | open | keep; takes W2-06's S1, S2, S5 and F1 (shared with W2-122) | 6, plus those moved in | not K9 |
| W2-124 | mb2t | open | keep; takes W2-88's S5 | 6 + 1 | a store not built is never reported ok |
| W2-128 | t8mp | open | **keep (Δ: filed, DEC-1081 (2))**; takes W2-11b's lines | 24 open (TPL-3 S5's scripts built 11-06), plus D-11's weekly-review line in the CTO template | the templates |
| W2-131 | r8vq | in_progress | **keep (Δ: filed 11-06, DEC-1082 (2))** | 6 open; S4 at re-pin window 4 | the DEC-999 labels, a priority fix |

### Re-scope (21 tickets, 229 lines; about 34 lines lifted inside them, est. from INVESTIGATION §5)
| W2 | DAEO | status | fate | KPI lines and their fate | reason |
|---|---|---|---|---|---|
| W2-15b | swdu | open | **re-scope (Δ D-4b)** | 10, plus W2-15a's S2, S4 and S6. This repository's verdict lines (S1–S3, S5, S7–S9) become the fresh 80 used once at the decision point. S4 (scale), S10 (GPU against CPU) and the other corpora come after the lift, with W2-88 | It no longer absorbs W2-15a whole. §C's re-point of W2-32 to it is dropped, since it made a cycle (DEC-1055 (6)). It leaves K9 and gates only W2-29 |
| W2-20 | r30l | in_progress | re-scope: rebuilt from `heavy_slot.sh` and `balancer.py`, not merged from its 10-17 branch | 24: S12 goes to W2-123 (met); S6, S9 and S11 go to W2-121 or are lifted; Q-14 | W-6 |
| W2-27 | h4rh | open | re-scope | 15: S1 and S13 use W2-16's release only; S4 becomes "`gov doctor` green"; S8 becomes "reds named in the close record" (W-4); its deps are K9 (§3) | |
| W2-32 | 0pyc | in_progress | **re-scope (Δ D-4b; §C had keep)** | 13. **Met on integrate:** S1–S5, S7, S8, S10 and F1 (`b32e8504`, `16e0287a`, `0936077c`; `W2-32-evidence.md`). **On `w2/W2-32` `1aeae788` for window 4:** S11 and F2 (READY at round 2; the wording package is due). **Not built:** S6 (G2). **Open:** S9, the 85 % question (§3), and R2-F1 (parked at `park/W2-32-R2-F1`, "deferred to D-9") | stays dependent on W2-15a (DEC-1055 (6)) |
| W2-33 | lrre | open | re-scope: keep S2, S3, S6, S7, S8, S10; S1, S4, S5 to Wave 3; S9 lifted | 11 | role files reach sessions through W2-128's TPL-4 |
| W2-37 | 6n5k | in_progress | re-scope: the query only, no CIT-P | 4 | |
| W2-40 | 6ox0 | open | re-scope to S3 | 4: S3 kept, 3 lifted | |
| W2-42a | 03ub | in_progress | re-scope (G-7), **plus (Δ) the guard's homes**: G-14's path-map roles (DEC-1052), and the hidden sets outside the repository refused to the measured roles (DEC-1082 (3); live by ACT) | 13, plus the new lines | the guard's re-scoped ticket, as DEC-1052 names it |
| W2-45 | neam | open | re-scope: T-2's home | 5 | |
| W2-46 | nn1s | open | re-scope: S5 becomes "in EXAMIN"; deps cut (W-1); takes W2-24's AR lines (W-8) | 5 + 6 | |
| W2-47 | jip3 | open | re-scope: S3 dropped; takes W2-25 | 3 + 1 | |
| W2-56 | wnnz | in_progress | re-scope: status back to open (built nothing, W-6); S1 becomes T-8's daemon folder; takes W2-127 and W2-21's S5–S8 | 10 + 10 | K9 (DEC-799) |
| W2-60b | ecac | open | re-scope | 13 | |
| W2-82 | 4k3l | open | re-scope: a light readiness check the dispatcher calls | 12 | leaves K9 |
| W2-88 | 2bdu | open | **re-scope (Δ D-4b)** | 19, plus LINK-INTEGRITY §6.1's two lines (DEC-1074 (7), not yet applied); S5 to W2-124 | gains a dep on W2-129; owns memory-building (DEC-1072 (2)); W2-15b's other corpora run on its tools |
| W2-98 | wi46 | open | re-scope; its dep on W2-104 cut | 13, plus one link line (DEC-1074 (7), not yet applied) | |
| W2-104 | drhj | in_progress | re-scope: an optional tool, not gating | 7 | |
| W2-113 | g29a | open | re-scope: S4 lifted | 7 | |
| W2-115 | emq1 | open | re-scope: takes W2-117 (`gov queue`); S4 per Q-1; Q-2 to Q-11 and T-9; S12–S15 lifted; S11 is READY's one home (W-2) | 19 + 9 | K9 (test before merge, DEC-1010 item 5) |
| W2-120 | i89t | open | re-scope to S3 | 4: S3 kept, 3 lifted | |
| W2-121 | cb2b | open | re-scope: takes W2-118's S1 and S3 and W2-21's lines; S12 to Wave 3; S17 lifted; O-12's line; the dep on W2-118 cut; **plus D-11's symptom-flag line** (DEC-1052) | 18, plus those moved in | K9 (DEC-1008) |

### Merge (7 tickets, 59 lines)
| W2 | DAEO | status | into | KPI lines | reason |
|---|---|---|---|---|---|
| W2-06 | kia7 | open | W2-116, W2-122 | 6: S1, S2, S5 and F1 moved; S3 and S4 lifted | "paperwork only" (D4B-MEMORY-STAGE §3) |
| W2-11b | 9bc0 | open | **W2-128 (Δ; §C had re-scope)** | 9: S1 to TPL-1 S3 (the verdict block); S2 to the reviewer template; F1 and F2 to TPL-1 S3 and TPL-4; S3–S7 lifted | W2-128's text says its lines replace W2-11b's |
| W2-21 | 1ahb | open | W2-121, W2-33, W2-60a, W2-56 | 9 moved | |
| W2-99 | lxzn | open | the `discovery` skill | 13 moved, **no ticket home yet** (§5) | |
| W2-117 | zkr9 | open | W2-115 | 9 moved; the `after-examin` tag resolved | |
| W2-118 | ts4y | open | W2-121 | 7: S1 and S3 to W2-121; S2 to Wave 3 (W3-P02, W-10); S5 is W2-121's S13 (one home); S4, F1 and F2 follow S1 | |
| W2-127 | 1vka | open | W2-56 | 6 moved | |

### Close formally (16 tickets, 126 lines)
| W2 | DAEO | status | KPI lines | reason |
|---|---|---|---|---|
| W2-04 | u4oz | in_progress | 8, met as built (`70965cf6`, D-1) | **Δ (§C had re-scope):** decided once (DEC-1052 M-1) |
| W2-05 | 0z8c | in_progress | 4 met (landed `b4a747f1`) | |
| W2-13 | zqvn | in_progress | 8 met: `8550788b` (S1–S4, F1, F2; FULL review READY), `9ed83413` (S5), `261d6415` (S6); `W2-13-evidence.md` | **Δ D-4b (§C had keep)** |
| W2-15a | rd0g | open | 7: S1, S3, S5 and S7 met (`ff691ec2`, `docs/research/EXP-003/w2-15a-baseline.md`; S3's lighter reranker covered by D4B-TRIAL-W4); S2, S4 and S6 moved to W2-15b | **Δ D-4b (§C had merge into W2-15b):** DEC-1055 (5)'s split |
| W2-55 | arrl | in_progress | 12: S1, S3, S6 and S8 met (landed `e0cb7d13`); S5 met as amended by LINK-INTEGRITY §6.1 (a notice; W2-129 carries its findings); S2, S4 and S7 lifted; each F line follows its S line | **Δ D-4b (§C had re-scope)** |
| W2-91 | a3u2 | in_progress | 10 met (`947da7a4`, `W2-91-evidence.md`); S1 re-worded to M-4's scope (DEC-1055 (2); D-7 `27a80411`) | **Δ D-4b (§C had keep)** |
| W2-92 | n0wb | in_progress | 15 met: S1–S5 `0d33901a`, S6 `88748f99`, S7–S10 and F5 `3679ca0b` (acceptance 116/0, READY, DEC-1071's rule); the pin carries them at window 4 | **Δ D-4b (§C had keep)** |
| W2-96 | ouet | in_progress | 10, met as built | |
| W2-111 | qvff | open | 7, met by D-4's cut (`6008a41f`; D4-LIST-A) | **Δ (§C had merge into P1-5)** |
| W2-112 | clon | in_progress | 10 met (`9a02a474`, D-1) | |
| W2-122 | blwa | in_progress | 5 met (`5543a03a`), plus W2-06's share | |
| W2-123 | qzrq | in_progress | 9 met (`f704f7d3`), plus W2-20's S12 | |
| W2-126 | jpr0 | in_progress | 10 met (`0c5d7f4c`) | |
| W1-01b | vhad | in_progress | 3, met at D-10's green run | **Δ (§C had merge into the red fixes):** a plan step is no home for a KPI line |
| W2-66b | zuiy | in_progress | 2, the same | **Δ** |
| W2-90c | fu3n | open | 6, the same (the 11 install and hook reds) | **Δ** |

### Retire (22 tickets, 131 lines), as §C (reasons from INVESTIGATION §5)
| Tickets (lines) | Reason |
|---|---|
| W2-08 (7r5e, 8) | O1 (A), no hook |
| W2-09 (a3m2, 4), W2-10 (cuao, 7) | G-4 (DEC-954 had already dropped W2-10) |
| W2-12 (j8gn, 10), W2-14 (7y6v, 6), W2-31 (wbdh, 3), W2-38 (g23i, 3), W2-39 (wudw, 1), W2-41 (s694, 8), W2-43 (u5g6, 5), W2-44 (zndm, 2) | part D's retirements |
| W2-22 (xm6l, 8) | B1-24 ("`gov doctor` green" lives in W2-27 and W2-46) |
| W2-24 (0mab, 6), W2-25 (btt7, 1) | W-8: their AR lines are shown once in W2-46 and audited in W2-47; exit criterion 5 is re-worded |
| W2-78 (v4is, 6) | T-4 was done as config; its branch is deleted with this answer (DEC-1053 (6)) |
| W2-83a (dy7j, 9; leaves K9), W2-83b (mc6n, 6) | as §C |
| W2-102 (rpfv, 10), W2-103 (hgv3, 9) | as §C |
| W2-109 (6b2q, in_progress, 9) | built nothing (W-6); K-2 is retired into P1-11's Contract re-baseline |
| W2-119 (168f, 5) | G-10: the harvest is stopped |
| W2-125 (jfm3, 5) | as §C |

### Wave 3 (9 tickets, 57 lines), as §C
- W2-17 (sdhj, 5), W2-18 (057v, 6), W2-34 (yadm, 5), W2-35 (2keg, 1).
- W2-19 (jzvg, 8): S5 and S7 lifted.
- W2-36 (w19l, 1): first in line.
- W2-42 (fau3, 8): S3, atomic saves, first.
- W2-100 (uw5h, 12), W2-101 (6icv, 11).

### Outside the Wave 2 count: six old repair tickets (no W2 id)
- **The tickets** (the old strict close filed them automatically): DAEO-2d6f (parent W2-03), DAEO-2upp (W2-70),
  DAEO-cv6c (W2-57), DAEO-pr0y (W2-58), DAEO-s1wp (W2-66) and DAEO-sg6x (W2-71).
- **Their parents:** all six are closed.
- **Proposed: retire.** D-10 catches any red they name that still stands.

## 2. New tickets
- **W2-129, `gov links`** (engineer, STANDARD, est. 400 LOC; 21 lines from
  `LINK-INTEGRITY-tickets/W2-129-gov-links.md`).
  - Approved by DEC-1074 (7). It depends on W2-92 and W2-55.
  - It runs right after window 4, about one lead-day, and enters K9 through W2-88.
- **W2-130, the link clean-up** (orchestrator, STANDARD; 12 lines).
  - Approved by DEC-1074 (7). It depends on W2-129 and W2-92.
  - It is not gating. Its per-ticket findings come back into D-9 (LINK-INTEGRITY §7).
- **The DEC-999 fix** is already W2-131.
- **Only when it is reached: W2-132**, an engineer's ticket for W2-128's code parts (TPL-3's `gov brief` and TPL-4's
  launcher flag), which W2-128's text says the CTO brings you.
- **The other loose items already have homes:**
  - DEC-1082 (3)'s guard rule goes to W2-42a.
  - D-11 goes to W2-121 and W2-128.
  - The reranker chosen at the decision point goes under W2-32's model-pin lines.
  - The P-SELECT-GRAPH trial (DEC-1062) is research inside D-9; adopted, it becomes a W2-115 line.

## 3. K9, amended (EXAMIN's copy), as W2-27's dependencies
1. **Memory proven** (W2-32, with W2-131 and re-pin window 4):
   - the bar: hit@5 at least 85 % (DEC-833's floor), with the complete-evidence share beside it;
   - the set: a fresh verdict set used once (`memory-verdict-2` at the decision point), on the pin that carries
     W2-92, W2-32's S11 and W2-131;
   - short of it: you decide under W2-32's S9.
   - This replaces "the enlarged measure at 85 %" and DEC-1055 (7)'s "85 % on the 48, 21 of 24 hidden", which
     DEC-1074 (1) made tuning sets.
2. **Roles, skills and briefs landed:** W2-11, W2-33, W2-60a, W2-60b and **W2-128** (replacing W2-11b). W2-83a's
   playbook leaves K9.
3. **The proving ground passed:** W2-81 and W2-93. DEC-953 and DEC-954's line stays: a ticket in each synthetic
   repository closes with `gov close` exit 0 on a pinned release.
4. **The dispatcher:** W2-121 (DEC-1008).
5. **Test before merge and a clean close:** W2-115, which takes W2-117; W2-27's S14 needs it.
6. **Workers launched and sandboxed:** W2-56 (DEC-799) and W2-20.
7. **Memory for any repository:** W2-88 (with W2-129), W2-124 and W2-94.
8. **The release and the adoption path:** W2-16 (closed), W2-23, W2-52, W2-105, W2-110 and W2-90b.
9. **Out of K9:**
   - W2-82 becomes a light check, and W2-83a is retired.
   - DEC-794's gate (W2-24's repeat, (a) and (d)) is re-homed: (a) to W2-56's close; (d) to W2-04's S4 (met) and
     criterion 1.

**W2-27's deps:** 46 become 44.
- **Removed (11):** W2-06, W2-21 and W2-99 (merged); W2-100 and W2-101 (Wave 3); W2-102, W2-103, W2-109 and W2-83a
  (retired); W2-104 and W2-82 (not gating).
- **Added (9):** W2-112, W2-122, W2-123 and W2-126 (formal closes); W2-115, W2-121 and W2-124; W2-128 and W2-131.
- **Kept, unlike part D:** W2-05 and W2-96. P1-13 closes them before the copy.
- **Other dependency edits:**
  - W2-121 loses W2-118, W2-98 loses W2-104, and W2-29 loses W2-25.
  - W2-88 gains W2-129.
  - W2-46 is cut per W-1.
  - W2-32 stays dependent on W2-15a.
  - W2-117's and W2-118's `after-examin` tags go with their merges.

## 4. The counts
| fate | tickets | lines | the lines' fate (est. where marked) |
|---|---:|---:|---|
| keep | 19 | 157 | about 148 open; 9 met (W2-61h) |
| re-scope | 21 | 229 | about 9 met (W2-32); about 34 lifted (est.); the rest open; 3 come in from W2-15a |
| merge | 7 | 59 | about 52 moved, about 7 lifted; W2-99's 13 have no home |
| close formally | 16 | 126 | 120 met (11 at D-10's green run); 3 moved; 3 lifted |
| retire | 22 | 131 | out of Wave 2 (W2-24's and W2-25's AR lines shown in W2-46 and W2-47) |
| Wave 3 | 9 | 57 | moved out |
| **total** | **94** | **759** | with W2-129 (21) and W2-130 (12): **96 tickets, 792 lines**; plus 3 approved lines not yet applied |

**Against §C:** keep 21 → 19; re-scope 23 → 21; merge 11 → 7; close formally 6 → 16.

**Left before EXAMIN's copy: 24 tickets of work plus 12 formal closes** (§G counted 31).
- **Formal closes:** W2-04, W2-05, W2-13, W2-15a, W2-55, W2-91, W2-92, W2-96, W2-112, W2-122, W2-123 and W2-126.
  They take about 0.5 day.
- **In flight (9):** W2-11, W2-32, W2-52, W2-60a, W2-61h, W2-81, W2-90b, W2-105, W2-110.
- **Restarted (2):** W2-20, W2-56.
- **Open, nothing built (13):** W2-23, W2-33, W2-60b, W2-88, W2-93, W2-94, W2-98, W2-115, W2-121, W2-124, W2-128,
  W2-129, W2-131. Add W2-132 when it is split off.
- **Estimate (est.):** about 160–190 lead-h after the lifts, plus W2-128's 4–5 working days (R3, parts in parallel).

## 5. For your decision
1. **The fates as listed**, in one approval. What changed:
   - W2-04, W2-13, W2-15a, W2-55, W2-91, W2-92, W2-111, W1-01b, W2-66b and W2-90c become formal closes;
   - W2-32 becomes a re-scope;
   - W2-61h narrows to S7;
   - W2-11b merges into W2-128.
2. **K9's memory criterion** (§3, item 1).
   - Today's figures: 67.8 % on the spent 60; on the tuning sets, 107 of 138 and m6's 81.2 %.
   - The questions: is 85 % on the fresh 80, used once, the bar? And what does S9 offer if it is missed?
3. **W2-32's S6 (G2) and its parked R2-F1:**
   - S6: drop it as overtaken by the levers (DEC-1070, DEC-1079), or keep it as a round;
   - R2-F1: fold it into the remaining work, or drop it.
4. **W2-15b out of K9**, so it gates W2-29 only.
5. **W2-128 in K9** (recommended), and the W2-132 split when it is reached.
6. **A home for W2-99's 13 lines:** W2-128, P1-11's K-4 CIT-P, or retire them.
7. **W1-01b, W2-66b and W2-90c closed at D-10's green run**, rather than merged into a step.
8. **Retire the six old repair tickets.**
9. **W2-42a as the home** of DEC-1082 (3)'s guard rule and of G-14's path-map lines.
10. **Exit criterion 5's re-wording (W-8)**, which is yours.

**Not settled by the draft:**
- **W2-111** rests on D4-LIST-A's one line; the auditor should check its 7 lines.
- **W2-55's S5:** D4B-MEMORY-STAGE §3 sends it to W2-37; LINK-INTEGRITY §6.1, adopted later, keeps it in W2-55 as
  a notice. The draft follows the later package.
- **W2-04's S2** is taken as met as built. M-1's "warning" variant is not pursued (DEC-1052).
- **W2-15a's** cold-rebuild peak RSS was never measured; it moves with S4.
- **W2-128's TPL-5** ("warns, never refuses") may contradict DEC-1052 ("READY and DONE computed by code … not
  warnings"). To settle before TPL-5 is built.
- **The `core.bare` tests' half** (DEC-1074 (8)) has no home: D-10's red fixes, or a line in W2-122's close.
- **Link findings** (unknown ids, `closes:`) come only after W2-129 and W2-130, so a second pass may follow.
- **Not re-read:** the per-line evidence for W2-05, W2-96, W2-112, W2-122, W2-123 and W2-126. Their fates rest on
  §C, DEC-1052 and the D-1 merges.

**Sources:**
- P1-PLAN (DEC-1052 section, status table, §A P1-8, §B.8, §C, §E, §G);
- INVESTIGATION-1-COMBINED §3.8 and §5;
- `docs/plan/WAVE_2_WBS.md` (K9, W2-27);
- `.tickets/*.md`;
- D4B-MEMORY-STAGE §3 and §10;
- START-NEXT-SESSION §3, §3b and §3c;
- LINK-INTEGRITY §6 and §7, and its tickets;
- D4-LIST-A and D0-CLEANUP-LIST;
- the W2-15a baseline and the W2-32 evidence;
- the register (DEC-1052, DEC-1055, DEC-1062, DEC-1074 to DEC-1082);
- `git log --merges w2/integrate` since 11-02, and `park/W2-32-R2-F1`.

Nothing under `~/gov-os-eval/` or `~/gov-os-runs/` was read.
