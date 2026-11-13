# D9-FATES: every Wave 2 ticket's fate and K9, amended (for the owner; DEC-1039 (3b), P1-PLAN D-9) — version 2

- **For:** the owner. **By:** a read-only drafter, 2026-11-06 (restarted under DEC-1082 (1)), reviewed by the CTO
  (session `812bc5ce`). **Version 2**, 2026-11-06: the 40 corrections of `D9-FATES-AUDIT.md` applied. **Version
  2.1**, 2026-11-06: the auditor's re-check found all 40 applied and 9 corrections more, applied here.
- **Where it stands:** DEC-1083 approved the fates in one approval, with an independent auditor checking all 792 KPI
  lines before any edit. The audit confirmed every count and asked for 40 corrections, 7 of them high. This version
  applies them. Three items the audit sends to you are in §5. The edits go into the tickets in batches after the
  CTO's review, and a second pass follows for the link findings after W2-129 and W2-130.
- **The CTO's corrections to the draft:**
  - W2-61h S7 is built on `w2/W2-61h-s7` (`9e85fb97`, not on integrate) with its acceptance cases passing. It awaits
    review and merge; it is not "running".
  - **(audit 40)** W2-131 merged at 11:40 (`03336f19`, review READY, `gov accept` 29/29).
- **How changes are marked:** **Δ D-4b** means D-4b's work changed the fate P1-PLAN §C proposed. **Δ** means
  another cause changed it: D-1, D-4, or a ticket filed since §C. **(audit n)** marks a row version 2 changed for the
  audit's finding n; **(re-check n)** marks one version 2.1 changed for the re-check's correction n.
- **One rule for folds (re-check 8):** a line folded into an existing line of the same intent is "folded, no new
  line". It counts as moved to a named live ticket, and adds nothing to the receiving ticket's "plus n".
- **What is counted:** 94 live Wave 2 tickets with 759 KPI lines, success and failure, from today's front matter,
  plus W2-129 (21) and W2-130 (12): 792 lines. §C counted 92 tickets and 716 lines. The 43 new lines are in W2-128
  (24), W2-131 (6), W2-92 (+6), W2-32 (+3), W2-13 (+2) and W2-61h (+2). W2-133 (6 lines, filed after the audit) and
  the six old repair tickets (23 lines) are outside the 792.

## 1. The fates, one row per ticket

### Keep (19 tickets, 157 lines)
| W2 | DAEO | status | fate | KPI lines and their fate | reason |
|---|---|---|---|---|---|
| W2-00 | sdxk | open | keep | 1 open | the main session's coordination ticket |
| W2-11 | k7hz | in_progress | keep, land as built | **(audit 36)** 19: 18 shown met at its close (counted open until then); S13 (the lead brief's `brief_gaps:` section) is parked in Wave 3 (W3-P02) under W-10. **(re-check 4)** W2-99's S3 and F4 fold into its S10 and F1 (folded, no new line). W2-128's lines later replace its template lines | built; DEC-1081 (2) |
| W2-23 | kmcr | open | keep | 8 open | W2-27 S3 relies on it |
| W2-28 | csj8 | open | keep | 2 open | the independent verdict on the copy |
| W2-29 | b926 | open | keep; drop the dep on W2-25 (retired) | 1 open | real adoption; gated by W2-15b, not K9 (DEC-1083 (4)) |
| W2-30 | 60rw | open | keep | 1 open | |
| W2-52 | siiz | in_progress | keep | 4 | W2-27 S2 |
| W2-60a | cv58 | in_progress | keep (S10 as is; G-12 refused); **(audit 23, re-check 8)** W2-21's S3 and S4 fold in, no new line: S3's launch record into its S8, and S4's refusals into its S3, S4 and S6. S3's other half, the `Session:` trailer, is lifted: no commit on integrate carries one, and the launch record, keyed by the session id, already ties a session to its work | 13 | roles at launch (K9) |
| W2-61h | h2k3 | in_progress | **keep, narrowed (Δ D-4b)** | **(audit 16)** 11. Met: S1–S3, S5, S6, F1 and F2 (`15592622`, `cd8e5420`; S5 and S6 re-worded to G-3 by D-8). Evidence missing: S4 and F3, red at `cd8e5420` until the re-pin, with no green commit cited. S1 and S3 still say 24 hidden; DEC-1069 made it 40, a re-wording not yet applied. S7 and F4 (source families, DEC-1079) are built on `w2/W2-61h-s7` with acceptance passing, and await review and merge | D-4b merged all but S7 |
| W2-81 | l78m | in_progress | keep | 17 | the proving ground (K9) |
| W2-90b | nqa2 | in_progress | keep | 7 | |
| W2-93 | 6y0x | open | keep | 7 | W2-81's held-out half |
| W2-94 | g87r | open | keep | 8 | EXAMIN's question set |
| W2-105 | zpdj | in_progress | keep | 8 | |
| W2-110 | 3r1j | in_progress | keep | 8 | |
| W2-116 | f58b | open | keep; **(audit 26, re-check 5)** takes W2-06's four moved lines, none going to W2-122: S1 and S2 (the re-index after a commit and a merge) fold into its S4 ("refreshed after every landing"), with no hook (O1), and no new line; S5 (never an empty index) and F1 (a failed re-index keeps the old one) come in as lines | 6 + 2 | not K9 |
| W2-124 | mb2t | open | keep; takes W2-88's S5 | 6 + 1 | a store not built is never reported ok |
| W2-128 | t8mp | open | **keep (Δ: filed, DEC-1081 (2))**; in K9 (DEC-1083 (5)); takes W2-11b's lines: **(re-check 8)** S1, F1 and F2 fold into TPL-1 S3 and TPL-4 (no new line), and S2 comes in as the reviewer template's line. **(re-check 4)** W2-99's S6 and F7 fold into its S9 (TPL-4, the generated copies), no new line | 24 open (TPL-3 S5's scripts built 11-06), plus 1. **(audit 35)** Not yet written: D-11's weekly-review line in the CTO template, and W2-11b's S2. **(re-check 9)** S12 (TPL-7): its brief-gaps part (`brief-gaps.md` lists every `brief_gaps` line) goes with W2-11 S13 to Wave 3 (W3-P02); the rest of S12 stays (a re-word) | the templates. **(audit 39)** Its S10 (TPL-5) ready check follows DEC-1052 as DEC-1083 rules (already in the ticket) and is the one home of a ticket's readiness (W-2) |
| W2-131 | r8vq | in_progress | **keep (Δ: filed 11-06, DEC-1082 (2))**; merged 11:40 (`03336f19`) | **(audit 9)** 6: S1–S3, F1 and F2 met at `03336f19` (`gov accept` 29/29); S4 open, at re-pin window 4, with W2-133 | the DEC-999 labels, a priority fix |

### Re-scope (21 tickets, 229 lines)
**(audit 37, re-check 3)** The draft's "about 34 lines lifted (est.)" named only 14, and the estimate is withdrawn.
The lifts inside the re-scopes, line by line:
- named in their rows: W2-33 S9; W2-40 S1, S2 and S4; W2-47 S3 (dropped); W2-113 S4; W2-115 S12–S15; W2-120's three
  lines other than S3; W2-121 S17;
- under W-3: W2-15b S7 ("both figures", one rule in W2-61's measure); W2-98 S5 and F4 (the three scenarios, now
  optional); W2-37 S1 and S2 (its fate is "the query only, no CIT-P", INVESTIGATION §5);
- re-worded under W-3, not lifted: W2-98 S6 keeps the licence and drops "and its three scenarios passing"; W2-88 F6
  drops "a figure of the measure reported without the other";
- kept: W2-91 F4 and W2-92 F4 stay met.

| W2 | DAEO | status | fate | KPI lines and their fate | reason |
|---|---|---|---|---|---|
| W2-15b | swdu | open | **re-scope (Δ D-4b)**; out of K9 (DEC-1083 (4)) | **(audits 30, 37)** 10, plus W2-15a's S2, S4 and S6 (S4 brings the cold-rebuild peak RSS, never measured). S1–S3, S5, S8 and S9 stay its own verdict lines, measured after the lift; they do not carry K9's bar, which is a line under W2-32 S9 (§3). S7 ("both figures in every report") is lifted under W-3: one rule in W2-61's measure. S4 (scale), S10 (GPU against CPU) and the other corpora come after the lift, with W2-88 | It no longer absorbs W2-15a whole. §C's re-point of W2-32 to it is dropped, since it made a cycle (DEC-1055 (6)). It gates only W2-29 |
| W2-20 | r30l | in_progress | re-scope: rebuilt from `heavy_slot.sh` and `balancer.py`, not merged from its 10-17 branch | **(audits 21, 22; re-check 1)** 24. S12 splits: its start half (both servers started under their cap) is W2-123's S7, met; its admission half (the gate counts both servers' CPU p95) stays here, open. S6 (memory admission) and S9 (the re-measure) stay here, open: S6 is the gate's own memory check for every `gov launch`, so moving it would drop the check for sessions launched outside the dispatcher (DEC-961, DEC-947). F6 stays with S6, and S8 is unchanged. W2-121's S3 reads the gate's figures (a re-word). S11 (the out-of-memory trip-wire) stays here, open: W2-121's S10 never stops a job, so it cannot hold it. Q-14 | W-6 |
| W2-27 | h4rh | open | re-scope | 15: S1 and S13 use W2-16's release only; S4 becomes "`gov doctor` green"; S8 becomes "reds named in the close record" (W-4); **(audit 31)** its deps are K9 (§3), 45 with W2-133 | |
| W2-32 | 0pyc | in_progress | **re-scope (Δ D-4b; §C had keep)** | **(audits 29, 30)** 13. **Met on integrate:** S1–S5, S7, S8, S10 and F1 (`b32e8504`, `16e0287a`, `0936077c`; `W2-32-evidence.md`). **On `w2/W2-32` `1aeae788` for window 4:** S11 and F2 (READY at round 2; the wording package is due). **Dropped:** S6 (G2), overtaken by the levers (DEC-1083 (3)). **Open:** S9, which gains K9's bar as a line (DEC-1083 (2); §3 item 1). **R2-F1** (parked at `park/W2-32-R2-F1`) goes to the Wave 3 parking list (DEC-1083 (3)). Its strict-xfail case (`test_w2_32_s7_dec1067.py::test_nested_parents_send_no_line_twice_and_name_every_span_left_out`) stays strict, so it turns red when R2-F1 is fixed; a test designer re-points its reason from "deferred to D-9" to the parking row, with `Rewrite-Reason: DEC-1083 (3)` (the CTO's call) | stays dependent on W2-15a (DEC-1055 (6)) |
| W2-33 | lrre | open | re-scope: keep S2, S3, S6, S7, S8, S10; S1, S4, S5 to Wave 3; S9 lifted; **(audit 23, re-check 8)** W2-21's S2 (the ticket-lead role) folds into its S2 (folded, no new line) | 11 | role files reach sessions through W2-128's TPL-4 |
| W2-37 | 6n5k | in_progress | re-scope: the query only, no CIT-P | **(re-check 3)** 4: S1 (a decision change raises a CIT-P) and S2 (the CIT-E record) lifted; S3 (the impact query in plain language) and S4 kept | |
| W2-40 | 6ox0 | open | re-scope to S3; **(audit 38)** its dep on W2-21 (merged) cut | 4: S3 kept; S1, S2 and S4 lifted | |
| W2-42a | 03ub | in_progress | re-scope (G-7), **plus (Δ) the guard's homes** (DEC-1083 (9)): G-14's path-map roles (DEC-1052), and DEC-1082 (3)'s hidden sets outside the repository refused to the measured roles (live by ACT) | **(audit 34)** 13, plus the new lines, still to be written | the guard's re-scoped ticket, as DEC-1052 names it |
| W2-45 | neam | open | re-scope: T-2's home; **(audit 38)** its dep on W2-08 (retired) cut | 5 | |
| W2-46 | nn1s | open | re-scope: S5 becomes "in EXAMIN"; **(audit 38)** deps cut (W-1; the new list in §3); **(audit 27)** takes W2-24's S5 and F1, the AR lines (W-8) | 5 + 2 | |
| W2-47 | jip3 | open | re-scope: S3 dropped; **(audit 27)** takes W2-25's S1 (the audit of AR-1 to AR-10) | 3 + 1 | |
| W2-56 | wnnz | in_progress | re-scope: status back to open (built nothing, W-6); S1 becomes T-8's daemon folder; takes W2-127, W2-21's S5–S8 and **(audit 23)** W2-21's F1 (a raw `claude` launch stays unallowed in the template, beside S7's allow rule) | 10 + 11 | K9 (DEC-799) |
| W2-60b | ecac | open | re-scope; **(audit 38)** its `deps` set to its `depends_on` (W2-60a, W2-07) | 13 | |
| W2-82 | 4k3l | open | re-scope: a light readiness check the dispatcher calls; **(audit 39)** it calls W2-128 S10's check, the one home of a ticket's readiness (W-2) | 12 | leaves K9 |
| W2-88 | 2bdu | open | **re-scope (Δ D-4b)** | 19, plus LINK-INTEGRITY §6.1's two lines (DEC-1074 (7), not yet written); S5 to W2-124; **(re-check 3)** F6 drops the clause "a figure of the measure reported without the other" (W-3, a re-word) | gains a dep on W2-129; owns memory-building (DEC-1072 (2)); W2-15b's other corpora run on its tools |
| W2-98 | wi46 | open | re-scope; its dep on W2-104 cut | 13, plus one link line (DEC-1074 (7), not yet written). **(re-check 3)** S5 and F4 (the three scenarios) lifted, now optional (W-3); S6 keeps the licence and drops "and its three scenarios passing" (a re-word) | |
| W2-104 | drhj | in_progress | re-scope: an optional tool, not gating | 7 | |
| W2-113 | g29a | open | re-scope: S4 lifted | 7 | |
| W2-115 | emq1 | open | re-scope: takes W2-117 (`gov queue`), **(audit 24, re-check 8)** whose S7 (review rounds counted) folds into its S11 (folded, no new line); S4 per Q-1; Q-2 to Q-11 and T-9 (not yet written); S12–S15 lifted; **(audit 39)** S11 is the one home of a review's READY (W-2; W2-121's S11 calls it) | 19 + 8 | K9 (test before merge, DEC-1010 item 5) |
| W2-120 | i89t | open | re-scope to S3 | 4: S3 kept, 3 lifted | |
| W2-121 | cb2b | open | re-scope: **(audits 23, 25; re-checks 1, 8)** takes W2-118's S1, S3, S4 and F1 as lines, while W2-118's S5 folds into its S13 (no new line); takes W2-21's S1 (the lead's launch); its S3 reads the gate's figures from W2-20 (a re-word), and W2-20's S6 and S9 stay there; S12 to Wave 3; S17 lifted; the dep on W2-118 cut; **(audit 35)** O-12's line and D-11's symptom-flag line (DEC-1052), both not yet written | 18 + 5 | K9 (DEC-1008) |

### Merge (7 tickets, 59 lines)
| W2 | DAEO | status | into | KPI lines | reason |
|---|---|---|---|---|---|
| W2-06 | kia7 | open | **(audit 26)** W2-116 | 6: S1 and S2 fold into W2-116's S4 (no new line, no hook: O1) **(re-check 5)**; S5 and F1 to W2-116 as lines; S3 and S4 lifted. None goes to W2-122, a formal close that `5543a03a` does not meet | "paperwork only" (D4B-MEMORY-STAGE §3) |
| W2-11b | 9bc0 | open | **W2-128 (Δ; §C had re-scope)** | 9: S1 to TPL-1 S3 (the verdict block); S2 to the reviewer template (**(audit 35)** not yet written in W2-128); F1 and F2 to TPL-1 S3 and TPL-4; S3–S7 lifted | W2-128's text says its lines replace W2-11b's |
| W2-21 | 1ahb | open | W2-121, W2-33, W2-60a, W2-56 | **(audit 23, re-check 8)** 9: S1 to W2-121; S2 folds into W2-33's S2 (no new line); S3 and S4 fold into W2-60a (no new line: S3's launch record into its S8, S4 into its S3, S4 and S6), and S3's `Session:` trailer half is lifted; S5–S8 and F1 to W2-56. The receiving rows show them | |
| W2-99 | lxzn | open | **(audit 28, re-check 4)** W2-11 and W2-128, by folds only (DEC-1083 (6)) | 13; none adds a line. S3 and F4 duplicate W2-11's S10 and F1 and fold into them; S6 and F7 duplicate W2-128's S9 and fold into it. Retired: S1, F1 and F2 (the discovery skill's own steps), and S2, F3, S4, F5, S5 and F6 | DEC-1083 (6) moves only lines that concern templates or briefs; the CTO's split, corrected by the CTO |
| W2-117 | zkr9 | open | W2-115 | **(audit 24, re-check 8)** 9: 8 moved as lines; S7 (review rounds counted) folds into W2-115's S11 (W-2; no new line); the `after-examin` tag resolved | |
| W2-118 | ts4y | open | W2-121 | **(audit 25)** 7: S1 and S3 to W2-121, with S4 and F1 following S1; S5 is W2-121's S13 (one home); S2 and F2 (the `brief_gaps:` check and its failure line) to Wave 3 (W3-P02, W-10) | |
| W2-127 | 1vka | open | W2-56 | 6 moved | |

### Close formally (15 tickets, 119 lines)
A formal close shows each line met. A line met in part (13 in all, §4; **re-check 6**) needs its measure, a re-word or a move before
its ticket closes.

| W2 | DAEO | status | KPI lines | reason |
|---|---|---|---|---|
| W2-04 | u4oz | in_progress | **(audit 20)** 8, met as built (`70965cf6`, D-1). The basis is DEC-1052 M-1 only, so `gov accept` runs once for the close | **Δ (§C had re-scope):** decided once (DEC-1052 M-1); M-1's "warning" variant is not pursued |
| W2-05 | 0z8c | in_progress | 4 met (landed `b4a747f1`) | |
| W2-13 | zqvn | in_progress | 8 met: `8550788b` (S1–S4, F1, F2; FULL review READY), `9ed83413` (S5), **(audit 15)** `261d6415` and `27a80411` (S6); `W2-13-evidence.md` | **Δ D-4b (§C had keep)** |
| W2-15a | rd0g | open | **(audit 7)** 7: S1, S5 and S7 met (`ff691ec2`, `docs/research/EXP-003/w2-15a-baseline.md`). S3 met in part: its lighter reranker was "not run (not installed)", and D4B-TRIAL-W4 trialled only larger ones. S2, S4 and S6 moved to W2-15b (the cold-rebuild peak RSS, never measured, moves with S4) | **Δ D-4b (§C had merge into W2-15b):** DEC-1055 (5)'s split |
| W2-55 | arrl | in_progress | **(audits 2–6, 38; re-check 6)** 12. **Met** (landed `e0cb7d13`): S3 and F2; S4, built as `docs/research/W2-55-backfill.md`, not lifted (counted met in §4), and F4 with it; F1, the validator's refusal. **In part:** S1, only its validator half (`TAG_MISSING` gives 1,069 lines until the backfill is accepted, LINK-INTEGRITY.md:314; the re-word is §5's question 2); S5, whose amendment in LINK-INTEGRITY §6.1 (line 421) is not yet applied, and whose second half is W2-130's clean-up; F3, until LINK-INTEGRITY §6.1's line 422 is applied; S6, no measure recorded after the merge (README:45); S8, only `--in-force` built, the hook half the owner's CIT-P. **Lifted:** S2 and S7. Its `deps` set to its `depends_on` (W2-03, closed) | **Δ D-4b (§C had re-scope).** D4B-MEMORY-STAGE §3 sent S5 to W2-37; LINK-INTEGRITY §6.1, adopted later, keeps it here as a notice, and this follows the later package |
| W2-91 | a3u2 | in_progress | **(audit 14)** 10 met (`947da7a4`, `W2-91-evidence.md`). S6 and F4 say "not run here" (evidence 342, 346): **(re-check 7)** their evidence is `docs/changes/W2-91-evidence.md` §3–§5 (control `f46b9653` against head `b652fc96`, 2026-11-01, both figures, per question), now cited. S1's re-word to M-4's scope (DEC-1055 (2); D-7 `27a80411`) is not yet applied | **Δ D-4b (§C had keep)** |
| W2-92 | n0wb | in_progress | **(audit 13)** 15: 14 met (S1–S5 `0d33901a`; S7–S10 and F5 `3679ca0b`, acceptance 116/0, READY, DEC-1071's rule). S6 met in part: 14/15 at `88748f99`, green only at `3679ca0b`, and its 1.2 s median is recorded nowhere (evidence:120). The pin carries them at window 4 | **Δ D-4b (§C had keep)** |
| W2-96 | ouet | in_progress | **(audit 8)** 10, landed at `107514f5`: 9 met; S6 met in half, since `brief-engineer.md` does not name `gov accept` | |
| W2-112 | clon | in_progress | **(audit 17)** 10: 9 met (`9a02a474`, D-1); S3's 48-question half is "not yet measured" (research:173) | |
| W2-122 | blwa | in_progress | **(audits 18, 26)** 5: 4 met (`5543a03a`); S3's "alone" measure was not taken (evidence:60). W2-06's lines do not come here | |
| W2-123 | qzrq | in_progress | **(audit 21)** 9 met (`f704f7d3`). Its S7 already holds the start half of W2-20's S12; the admission half stays with W2-20, so nothing moves in | |
| W2-126 | jpr0 | in_progress | **(audit 19)** 10: 9 met (`0c5d7f4c`); S6's per-day "after" figure was not measured (evidence:81–82) | |
| W1-01b | vhad | in_progress | **(audit 10)** 3, met by `10025b21` (W1-01 README:155): it closes now, not at D-10 | **Δ (§C had merge into the red fixes):** a plan step is no home for a KPI line |
| W2-66b | zuiy | in_progress | **(audit 11)** 2, not built: `CODE_SUFFIXES` at `test_w2_66_live_test_map.py:34` has no `.ps1`. Its case is the last of seven under `rep:` (`optin-lifted-breadth.txt:1133`; `conftest.py:46-48`), so D-10's full run cannot show it | **Δ.** DEC-1083 (7) closes it at D-10's green run; §5's question 3 |
| W2-90c | fu3n | open | **(audit 12)** 6 (the 11 install and hook reds). W1-05's orchestrator-asks case and four W2-59 `[stop[0]]` rows sit in `optin-lifted-guard.txt` (lines 276 and 427–430), which run report-only in D-10 | **Δ.** As W2-66b; §5's question 3 |

### For your decision (1 ticket, 7 lines)
| W2 | DAEO | status | KPI lines | reason |
|---|---|---|---|---|
| W2-111 | qvff | open | **(audit 1)** 7, not met. `6008a41f` touches only the READMEs of W1-02, W1-05 and W2-57 (D-4 kept 1 of the 5 decisions of W1-02's latency case in the full run, D4-LIST-A). There is no `tests/acceptance/W2-111/`, no `Rewrite-Reason: DEC-979`, and no CPU-time or load code | **Δ (§C had merge into P1-5).** Not a formal close: §5's question 1 |

### Retire (22 tickets, 131 lines), as §C (reasons from INVESTIGATION §5)
| Tickets (lines) | Reason |
|---|---|
| W2-08 (7r5e, 8) | O1 (A), no hook |
| W2-09 (a3m2, 4), W2-10 (cuao, 7) | G-4 (DEC-954 had already dropped W2-10) |
| W2-12 (j8gn, 10), W2-14 (7y6v, 6), W2-31 (wbdh, 3), W2-38 (g23i, 3), W2-39 (wudw, 1), W2-41 (s694, 8), W2-43 (u5g6, 5), W2-44 (zndm, 2) | part D's retirements |
| W2-22 (xm6l, 8) | B1-24 ("`gov doctor` green" lives in W2-27 and W2-46) |
| **(audit 27)** W2-24 (0mab, 6: S1–S4 retired; S5 and F1 to W2-46), W2-25 (btt7, 1: S1 to W2-47) | W-8: their AR lines are shown once in W2-46 and audited in W2-47; exit criterion 5 is re-worded (the CTO brings the wording, DEC-1083 (10)) |
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
- **(audits 25, 29, 36) Lines of live tickets that go to Wave 3:** W2-11 S13 and W2-118 S2 and F2 (W3-P02, W-10);
  W2-33 S1, S4 and S5; W2-121 S12 (W3-P16). **(re-check 9)** The brief-gaps part of W2-128's S12 goes with W2-11 S13
  (W3-P02); the rest of S12 stays, so the line is re-worded, not moved. W2-32's R2-F1, a review finding rather than a KPI line, goes to the
  parking list (DEC-1083 (3)).

### Outside the Wave 2 count: six old repair tickets (no W2 id), retired
- **The tickets** (the old strict close filed them automatically): DAEO-2d6f (parent W2-03), DAEO-2upp (W2-70),
  DAEO-cv6c (W2-57), DAEO-pr0y (W2-58), DAEO-s1wp (W2-66) and DAEO-sg6x (W2-71).
- **Their parents:** all six are closed.
- **(audit 32) Retired** (DEC-1083 (8)); their 23 lines go with them. D-10 catches any red they name that still
  stands.

## 2. New tickets
- **W2-129, `gov links`** (engineer, STANDARD, est. 400 LOC; 21 lines from
  `LINK-INTEGRITY-tickets/W2-129-gov-links.md`).
  - Approved by DEC-1074 (7). It depends on W2-92 and W2-55.
  - It runs right after window 4, about one lead-day, and enters K9 through W2-88.
- **W2-130, the link clean-up** (orchestrator, STANDARD; 12 lines).
  - Approved by DEC-1074 (7). It depends on W2-129 and W2-92.
  - It is not gating. Its per-ticket findings come back into D-9 (LINK-INTEGRITY §7).
- **The DEC-999 fix** is W2-131, merged at 11:40 (`03336f19`); its S4 rides re-pin window 4.
- **(audit 31) W2-133 (DAEO-k4wm), a narrowed or gap-starting register item carries its own entry's id** (engineer,
  STANDARD, est. 25 LOC; 6 lines, S1–S4 and two failure lines; filed 11-06, in progress).
  - W2-131's follow-up, named by its review: a small ticket of its own, tests first, in re-pin window 4 (DEC-1083).
  - It depends on W2-131. Its S4: it lands on `w2/integrate` before window 4 is built, and the window carries it with
    W2-131. It enters K9 with the pin (§3 item 1).
- **Only when it is reached: W2-132**, an engineer's ticket for W2-128's code parts (TPL-3's `gov brief` and TPL-4's
  launcher flag), which W2-128's text says the CTO brings you (DEC-1083 (5)).
- **The other loose items already have homes:**
  - DEC-1082 (3)'s guard rule and G-14's path-map lines go to W2-42a (DEC-1083 (9)).
  - D-11 goes to W2-121 and W2-128.
  - The reranker chosen at the decision point goes under W2-32's model-pin lines, and K9's bar names it (§3).
  - The P-SELECT-GRAPH trial (DEC-1062) is research inside D-9; adopted, it becomes a W2-115 line.
  - R2-F1 goes to the Wave 3 parking list (DEC-1083 (3)).

## 3. K9, amended (EXAMIN's copy), as W2-27's dependencies
1. **(audit 30) Memory proven** (DEC-1083 (2)):
   - the bar: hit@5 at least 85 % (DEC-833's floor) on the fresh 80 (`memory-verdict-2`), used once, with the
     complete-evidence share beside it; 95 % stays the target;
   - the pin: the one that carries W2-92, W2-32's S11, W2-131 (with W2-133 in the same re-pin window 4) and the
     reranker chosen at the decision point;
   - short of the bar: S9's options come to you;
   - its home: a line under W2-32's S9, so the bar sits inside W2-27's dependencies. W2-15b, out of K9, does not
     carry it.
   - This replaces "the enlarged measure at 85 %" and DEC-1055 (7)'s "85 % on the 48, 21 of 24 hidden", which
     DEC-1074 (1) made tuning sets.
2. **Roles, skills and briefs landed:** W2-11, W2-33, W2-60a, W2-60b and **W2-128** (in K9, DEC-1083 (5); replacing
   W2-11b). **(re-check 4)** W2-99's template lines fold into W2-11 and W2-128 with no new line. W2-83a's playbook leaves K9.
3. **The proving ground passed:** W2-81 and W2-93. DEC-953 and DEC-954's line stays: a ticket in each synthetic
   repository closes with `gov close` exit 0 on a pinned release.
4. **The dispatcher:** W2-121 (DEC-1008).
5. **Test before merge and a clean close:** W2-115, which takes W2-117; W2-27's S14 needs it.
6. **Workers launched and sandboxed:** W2-56 (DEC-799) and W2-20.
7. **Memory for any repository:** W2-88 (with W2-129), W2-124 and W2-94.
8. **The release and the adoption path:** W2-16 (closed), W2-23, W2-52, W2-105, W2-110 and W2-90b.
9. **Out of K9:**
   - W2-15b (DEC-1083 (4)); it gates W2-29 only.
   - W2-82 becomes a light check, and W2-83a is retired.
   - DEC-794's gate (W2-24's repeat, (a) and (d)) is re-homed: (a) to W2-56's close; (d) to W2-04's S4 (met) and
     criterion 1.

**W2-27's deps:** 46 become 45 (the audit confirmed 44 before W2-133 was filed).
- **Removed (11):** W2-06, W2-21 and W2-99 (merged); W2-100 and W2-101 (Wave 3); W2-102, W2-103, W2-109 and W2-83a
  (retired); W2-104 and W2-82 (not gating).
- **Added (10):** W2-112, W2-122, W2-123 and W2-126 (formal closes); W2-115, W2-121 and W2-124; W2-128, W2-131 and
  **(audit 31)** W2-133.
- **Kept, unlike part D:** W2-05 and W2-96. P1-13 closes them before the copy.
- **Other dependency edits:**
  - W2-121 loses W2-118, W2-98 loses W2-104, and W2-29 loses W2-25.
  - **(audit 38)** W2-40 loses W2-21 (merged), and W2-45 loses W2-08 (retired).
  - **(audit 38)** W2-55's and W2-60b's `deps` are set to their `depends_on`: W2-55 on W2-03 (closed); W2-60b on
    W2-60a and W2-07 (closed).
  - W2-88 gains W2-129.
  - **(audit 38) W2-46, cut per W-1:** its 89 deps become 76, in `deps` and `depends_on` alike. Removed (13):
    W2-06, W2-21 and W2-99 (merged); W2-08, W2-24, W2-25, W2-83a, W2-83b, W2-102, W2-103 and W2-109 (retired);
    W2-100 and W2-101 (Wave 3). K9's additions reach it through W2-27.
  - W2-32 stays dependent on W2-15a.
  - W2-133 depends on W2-131, as filed.
  - W2-117's and W2-118's `after-examin` tags go with their merges.

## 4. The counts

**By ticket fate:**
| fate | tickets | lines |
|---|---:|---:|
| keep | 19 | 157 |
| re-scope | 21 | 229 |
| merge | 7 | 59 |
| close formally | 15 | 119 |
| for your decision (W2-111, §5) | 1 | 7 |
| retire | 22 | 131 |
| Wave 3 | 9 | 57 |
| **total** | **94** | **759**; with W2-129 (21) and W2-130 (12): **96 tickets, 792 lines** |

**Against §C:** keep 21 → 19; re-scope 23 → 21; merge 11 → 7; close formally 6 → 15, with W2-111 for your decision.

**(re-check 2) By line fate (the audit's count, then this version's changes):**
| the line's fate | the audit's count | changed here | version 2.1 |
|---|---:|---|---:|
| met with evidence | 116 | +1 W2-55 S4 (from lifted); −1 W2-55 F3 (to in part, re-check 6) | 116 |
| met in part, or evidence missing | 12 | +1 W2-55 F3 | 13 |
| built on a branch, not merged | 4 | — | 4 |
| open | 383 | −1 W2-11 S13 (to Wave 3); −1 W2-15b S7 (lifted); +3 W2-20 S6, S9 and S11 and +1 W2-20 S12's admission half (stay in W2-20); −4 W2-98 S5 and F4, W2-37 S1 and S2 (lifted, re-check 3) | 381 |
| moved or folded into a named live ticket | 45 | −1 W2-20 S12; +4 W2-99 S3, F4, S6 and F7 (folded) | 48 |
| moved, home not settled | 16 | −13 W2-99; −3 W2-20 S6, S9 and S11 | 0 |
| lifted or dropped | 27 (W2-32 S6 among them) | −1 W2-55 S4; +1 W2-15b S7; +4 W2-98 S5 and F4, W2-37 S1 and S2 | 31 |
| Wave 3 | 61 | +1 W2-11 S13 | 62 |
| retired | 128 | +9 W2-99 (S1, F1, F2, S2, F3, S4, F5, S5 and F6) | 137 |
| **total** | **792** | | **792** |

- The audit counted the draft's lines with its own corrections to what is met. The changes above are only those
  this version makes. The re-check confirmed the base: W2-32 S6 was already under lifted, and W2-55 S4 under lifted
  until this version. The base's 16 "home not settled" are W2-99's 13 with W2-20's S6, S9 and S11.
- The re-check gave met as 117 (W2-55 S4 moved to met). This version also moves W2-55's F3 from met to in part (its
  correction 6), so met is 116 and in part 13. If the audit's base already counted F3 in part, met is 117 and in
  part 12.
- Partial lines change no count: the `Session:` trailer half of W2-21 S3 is lifted inside a folded line; the
  brief-gaps part of W2-128 S12 goes to Wave 3 inside a re-worded line.
- The 13 met in part: W2-55 S1, S5, F3, S6 and S8; W2-15a S3; W2-61h S4 and F3; W2-92 S6; W2-96 S6; W2-112 S3;
  W2-122 S3; W2-126 S6.
- Within the open lines: W2-111's 7, W2-66b's 2 and W2-90c's 6, which the draft counted met (§5).
- W1-01b's 3 are met now.

**(audit 35) Approved lines not yet applied** (the draft said 3):
- **New lines, outside the 792, to be written** (at least 20; W2-42a's count is set when they are written):
  - W2-88: LINK-INTEGRITY §6.1's two lines (DEC-1074 (7));
  - W2-98: one link line (DEC-1074 (7));
  - D-11's two lines: W2-121's symptom-flag line and W2-128's weekly-review line in the CTO template (DEC-1052);
  - W2-42a: DEC-1082 (3)'s guard rule and G-14's path-map lines (DEC-1083 (9));
  - W2-115: Q-2 to Q-11 and T-9;
  - W2-121: O-12's line;
  - W2-32 S9: K9's bar (DEC-1083 (2); audit 30).
- **A moved line not yet written in its new home:** W2-11b S2, into W2-128 (the reviewer template).
- **Re-wordings of lines inside the 792:**
  - W2-55 S5 and F3, as LINK-INTEGRITY §6.1 (lines 421–422) amends them (audit 5);
  - W2-91 S1, to M-4's scope (DEC-1055 (2); D-7 `27a80411`) (audit 14);
  - W2-61h S1 and S3, from 24 hidden to 40 (DEC-1069) (audit 16);
  - **(re-check 3)** W2-98 S6, without "and its three scenarios passing"; W2-88 F6, without "a figure of the measure
    reported without the other";
  - **(re-check 1)** W2-121 S3, reading the gate's figures from W2-20;
  - **(re-check 9)** W2-128 S12, its brief-gaps part out (parked with W2-11 S13 in W3-P02);
  - W2-55 S1, if you approve §5's question 2.
- **Folds to note in the receiving lines (re-check 8, no new line):** W2-21 S2 in W2-33 S2; W2-21 S3 (its launch
  record) and S4 in W2-60a S8 and S3, S4, S6; W2-117 S7 in W2-115 S11; W2-118 S5 in W2-121 S13; W2-06 S1 and S2 in
  W2-116 S4; W2-11b S1, F1 and F2 in W2-128's TPL-1 S3 and TPL-4; W2-99 S3 and F4 in W2-11 S10 and F1; W2-99 S6 and
  F7 in W2-128 S9.

**Left before EXAMIN's copy: 25 tickets of work plus 12 formal closes** (the draft said 24 and 12; §G counted 31).
- **Formal closes (12):** W2-04, W2-05, W2-13, W2-15a, W2-55, W2-91, W2-92, W2-96, W2-112, W2-122, W2-123 and W2-126.
  - W2-04 needs one `gov accept` run.
  - W2-15a, W2-55, W2-92, W2-96, W2-112, W2-122 and W2-126 carry lines met in part, each needing its measure, a
    re-word or a move first.
  - About 0.5 day for the records (the draft's est.), plus those measures (not estimated).
  - Outside K9, W1-01b closes now.
- **(audits 9, 31) In flight (11):** W2-11, W2-32, W2-52, W2-60a, W2-61h, W2-81, W2-90b, W2-105, W2-110, W2-131
  (S4 at window 4) and W2-133.
- **Restarted (2):** W2-20, W2-56.
- **Open, nothing built (12):** W2-23, W2-33, W2-60b, W2-88, W2-93, W2-94, W2-98, W2-115, W2-121, W2-124, W2-128
  and W2-129. Add W2-132 when it is split off.
- **Estimate (est.):** about 160–190 lead-h after the lifts, plus W2-128's 4–5 working days (R3, parts in parallel),
  plus W2-133, a small STANDARD ticket (est. 25 LOC).

## 5. For your decision (after the audit)
1. **(audit 1) W2-111**, whose 7 lines are not met: keep it open, or retire it with a reason.
   - **Recommended: keep it open**, as a LITE test revision outside K9 (confidence medium).
   - Why: its 11 cases still time the machine, not the hook (P-LATENCY-1), so a loaded run can turn them red, and
     the fix is a test designer's revision with no product code.
2. **(audit 2) W2-55 S1's re-word.** Only the validator half is met. Every entry gets its tags only through the
   backfill you accept (S4).
   - (a) Re-word S1 to "the decisions validator checks domain, status and scope, and names each entry without them
     (`TAG_MISSING`)". S1 is then met, and W2-55 closes formally.
   - (b) Keep S1 as written: W2-55 stays open until the backfill is accepted and applied.
   - **Recommended: (a)** (confidence high). Why: S4 bars the ticket from writing a tag before you accept the
     backfill, so S1 as written cannot be met by the ticket's own work.
3. **(audits 11, 12) W2-66b and W2-90c.** DEC-1083 (7) closes them at D-10's green run, but D-10 cannot show their
   cases: D-4 moved them to report-only opt-in lists, and W2-66b is not built.
   - (a) A red-fix item each in D-10: a test designer builds W2-66b's `.ps1` suffix (`Rewrite-Reason: DEC-1027 B`),
     and D-10 runs each ticket's cases by name and records them as the close evidence.
   - (b) Keep both open as tickets of their own, each closed by its own run of its cases.
   - (c) Retire both with a reason: their cases no longer block anything since D-4.
   - **Recommended: (a) for W2-66b; (b) for W2-90c** (confidence medium).
     - W2-66b is a one-suffix test edit that fits D-10's list.
     - W2-90c's cases pass only with W2-105 and W2-110 merged (its S1 and S2), and both are still in flight, so
       D-10 may come first. Its named run follows their merge.

### Decided by DEC-1083 (the draft's §5) — **(audit 34)**
1. The fates, in one approval, with this audit before any edit: **decided** (DEC-1083 (1)).
2. K9's memory bar: **decided**: 85 % hit@5 on the fresh 80, used once, on the pin with W2-92, W2-32's S11, W2-131
   and the chosen reranker; 95 % stays the target; if missed, S9's options come to you (DEC-1083 (2); §3 item 1).
3. W2-32's S6 dropped; R2-F1 to the Wave 3 parking list: **decided** (DEC-1083 (3)).
4. W2-15b out of K9: **decided** (DEC-1083 (4)).
5. W2-128 in K9, with the W2-132 split when it is reached: **decided** (DEC-1083 (5)).
6. W2-99's 13 lines: the template and brief lines into W2-128, the others retired: **decided** (DEC-1083 (6)).
   **(re-check 4)** As the CTO corrected its split, none adds a line: four fold into W2-11 and W2-128, and nine are
   retired (§1).
7. W1-01b, W2-66b and W2-90c closed at D-10's green run: **decided** (DEC-1083 (7)). The audit found W1-01b already
   met, so it closes now, and it sends W2-66b and W2-90c back to you (question 3).
8. The six old repair tickets retired: **decided** (DEC-1083 (8)).
9. W2-42a as the home of DEC-1082 (3)'s guard rule and of G-14's path-map lines: **decided** (DEC-1083 (9)); its new
   lines are still to be written.
10. Exit criterion 5: the CTO brings the proposed wording (DEC-1083 (10)).
- Also decided by DEC-1083: W2-128's ready check follows DEC-1052 (missing required fields make a ticket not READY,
  computed by code; only advisory items warn). The `core.bare` tests' half goes on D-10's red-fix list (P1-PLAN
  D-10, item 1). W2-133 is filed as W2-131's follow-up.

**(audit 33) Not settled:**
- **Exit criterion 5's wording (W-8):** the CTO brings it (DEC-1083 (10)).
- **W2-61h S4 and F3:** whether they turned green after the re-pin (the audit left it open).
- **W2-90c's S1:** which four W2-59 cases W2-90 named (the audit left it open).
- **The lines not yet written** (§4) are outside the 792 and need the second pass, with the link findings (unknown
  ids, `closes:`) that come only after W2-129 and W2-130.
- **W2-46's new list** names no live ticket outside K9 that it lacks today (W2-42a, W2-45, W2-113, W2-116, W2-120,
  W2-130). Whether the exit run waits on them is open.

**Sources:**
- `D9-FATES-AUDIT.md` (the 40 corrections, the counts) and DEC-1083;
- P1-PLAN (DEC-1052 section, status table, §A P1-8, §B.8, §C, §E, §G, D-10's red-fix list);
- INVESTIGATION-1-COMBINED §3.8 (W-1 to W-10) and §5;
- `docs/plan/WAVE_2_WBS.md` (K9, W2-27);
- `.tickets/*.md`, W2-133's (DAEO-k4wm) included;
- D4B-MEMORY-STAGE §3 and §10;
- START-NEXT-SESSION §3, §3b and §3c;
- LINK-INTEGRITY §6 and §7, and its tickets;
- D4-LIST-A and D0-CLEANUP-LIST;
- the W2-15a baseline, the W2-32 evidence, and `tests/acceptance/W2-32/README.md` (R2-F1's strict-xfail case);
- the register (DEC-1052, DEC-1055, DEC-1062, DEC-1069, DEC-1074 to DEC-1083);
- `git log --merges w2/integrate` since 11-02, `git show --stat 6008a41f`, and `park/W2-32-R2-F1`.

Nothing under `~/gov-os-eval/` or `~/gov-os-runs/` was read.
