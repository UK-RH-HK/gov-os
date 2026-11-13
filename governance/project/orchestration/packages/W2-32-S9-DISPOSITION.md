# W2-32 S9: a disposition in line with DEC-1097 (for the owner; DEC-1126 (6))

By the CTO's product-spec helper, 2026-11-11. Class C1. Read-only on the register, tickets and packages; nothing
outside this folder written. No figure below comes from the hidden folders: all are the published ones.

## 0. The short answer

- **A correction first.** The "58.3 %" that LIFT-CLOSES-1 gives for W2-32 is **not** the fresh 80's figure. It is
  D-4b measure 1, the baseline on the 48 dev questions on 2026-11-03, 28 of 48, before any improvement round
  (`packages/LIFT-1/D4B-GAPS.md` line 13; `docs/changes/W2-32-evidence.md`, S9 row). The fresh 80 gave **hit@5 67 of 79
  (84.8 %)** and **right end to end 78 of 79 (98.7 %), wrong claims 0** (`packages/LIFT-1/FRESH-80-RESULT.md`).
- Under DEC-1097's bar the fresh 80 **passes, and reaches the 95 % target.** DEC-1098 (1) already says so: "K9's memory
  line is met". So S9's trigger (a miss) never fired, and the owner is not being asked to accept a low level.
- What is wrong is **the record**: S9's words, the evidence note's S9 row, three packages and the W2-32 acceptance
  rule still speak of hit@5 at 85 % and of 58.3 %.
- **Recommendation: option (a1) below** (re-word S9 to DEC-1097's end-to-end bar, met on the fresh 80's recorded
  result, with the 11-23 audit named as the check on today's pin). Confidence: **high** that S9 should now say
  end to end; **medium-high** on (a1) over (a2), because the 80 was judged at window 4's pin, not at today's.

## 1. What S9 says now, and what DEC-1097 decided

**S9 now.** The ticket (`.tickets/DAEO-0pyc.md`, W2-32) carries S9 as the success line that has no label (the
acceptance README and the evidence note name it S9):

> If memory is below 85 % after two improvement rounds, the orchestrator escalates to the owner with the reasons; at the
> third the owner decides: a discovery and research ticket benchmarking market tools in a separate worktree, accepting
> the level reached, or another course. At 85 % or above but under the owner's target of 95 %, with room for improvement
> found, memory is not closed: an escalation to the owner [DEC-954 Q9e, DEC-957]

Its source is DEC-954 Q9 (e) and DEC-957. Its test rule (`tests/acceptance/W2-32/w2_32_record.py`, `FLOOR, TARGET =
85, 95`, "CAP-10's floor; the owner's target for hit@5") is about hit@5. The ticket's title still says "the hit@5 85
row".

**DEC-1083 (2), 2026-11-06 (word for word):** "K9's memory bar: 85 % hit@5 on the fresh 80, used once, on the pin that
carries W2-92, W2-32's S11, W2-131 and the reranker chosen at the decision point. 95 % stays the target. If the bar is
missed, S9's options come to the owner." D9-FATES §3 item 1 added: "its home: a line under W2-32's S9, so the bar sits
inside W2-27's dependencies."

**DEC-1097 (1)(d), 2026-11-08 (word for word):** "**the K9 bar:** right end to end at least 85 % with wrong claims at
most 5 %, target 95 %, hit@5 reported beside it (on 79: at least 68 right, at most 3 wrong claims, FRESH-80-1 §4.3)".
(1)(a): the configuration judged is window 4's pin `pin-bcea09060ebc`, the pool on, today's 6,000-token bundle, search
again once.

**DEC-1098 (1), 2026-11-09:** "The fresh 80 accepted; K9's memory line is met (FRESH-80-RESULT: right end to end 78 of
79, wrong claims 0)." **DEC-1126 (6), 2026-11-11:** W2-32 and W2-15a stay open at the lift; S9 gets "a disposition in
line with DEC-1097, whose end-to-end bar ... replaced the hit@5 bar of DEC-1083 (2)."

Two things the records show that the ticket does not:
- **The ticket never received K9's bar as a line.** D9-FATES (§3 item 1, the W2-32 row) and DEC-1083 (2) said S9
  "gains K9's bar". The ticket's S9 is still DEC-954's old escalation rule; no "right end to end" text is in it.
- **The two improvement rounds did run** (S7, S8, S11 and the pool; S6 dropped). The evidence note's "no improvement
  round has run yet" is from 2026-11-03 and is stale.

## 2. Does the 80's recorded result meet DEC-1097's bar? Yes.

| figure | bar (DEC-1097 (1)(d), on 79) | fresh 80 | recorded in |
|---|---|---|---|
| right end to end, search again once (A2) | at least 85 % (68), target 95 % (76) | **78 of 79 (98.7 %)** | FRESH-80-RESULT.md, "The verdict"; DEC-1098 (1); DECIDED-NOT-DONE row 18 |
| wrong claims | at most 5 % (3) | **0 of 79** | same |
| stricter of the two grades | (data) | 77 right, 1 wrong claim: still passes | FRESH-80-RESULT.md |
| hit@5, reported beside | no bar | 67 of 79 (84.8 %) | FRESH-80-RESULT.md, table |
| the 138 (data, not the verdict) | | right end to end 128 (92.8 %); hit@5 106 (76.8 %) | same table |

Three cautions, so the owner sees them:
1. **The 80 was judged at window 4's pin** (`pin-bcea09060ebc`, commit `c00d525f`). Today's pin is
   `pin-797495bdfc70` (window 5). Retrieval changed since: W2-137 and W2-138 (store commit in results, line-hash
   check), W2-136 and W2-145 (reranker cap and no private reranker). DEC-1083 (2) asked for the bar on the pin that
   carries the listed items, and it was met on that pin. The first memory audit (Monday 11-23, 21:00, DEC-1125 (2),
   MEMORY-AUDIT-1 §6) is built to measure exactly this change ("the changed list starts at the fresh 80's commit").
2. **The 80 is spent** (used once, USED 19:05 on 11-08). A re-measure on it is not possible and not asked for.
3. **hit@5 at 84.8 % is 0.2 points under the old 85 % bar** on 79 (67 against 67.15). Under the old bar this is a
   near miss; under the bar the owner chose beforehand it is beside, not judged.

## 3. Options (DEC-105: apply now, defer, or re-baseline)

The ticket is open, so its KPI lines can be re-worded by the owner's decision (a closed ticket is never edited). The
marker form already used on this ticket is `[re-worded, DEC-nnnn]` (S11 carries one).

### Option (a1), apply now: S9 re-worded to DEC-1097's bar, met on the fresh 80's recorded result. RECOMMENDED
- **New S9 line:** "S9 K9's memory line (DEC-1083 (2), re-worded by DEC-1097 (1)(d)): on the verdict set, judged once on
  the declared configuration, right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5
  reported beside it. Judged on the fresh 80 at window 4's pin: 78 of 79 right (98.7 %), 0 wrong claims, hit@5 67 of
  79 (84.8 %) [FRESH-80-RESULT, DEC-1098 (1)]. A later fall below 85 % is brought to the owner by the memory audit
  (DEC-1101 (1), DEC-1125 (2)), whose first run on 11-23 measures today's pin [re-worded, DEC-1126 (6)]". The old
  escalation sentence (below 85 % after two rounds; 85 to 95 % with room) is kept as the audit's rule, not repeated.
- **Also:** the title's "the hit@5 85 row" changed to "the memory line"; the evidence note's S9 row rewritten with
  the 80's figures; `w2_32_record.py`'s `s9_state` and its cases re-pointed to the end-to-end figure by an
  independent test designer (`Rewrite-Reason: DEC-1126 (6)`), with the README's S9 row.
- **For W2-32's close:** S9 is met and no longer blocks. What still holds W2-32 open is only W2-15a (its record fixes
  and a probe; they close together) and the owner's word that it stays open at the lift (DEC-1126 (6)).
  W2-27 (EXAMIN's copy) lists W2-32 in its `deps`, so closing W2-32 is also what frees K9's memory line there.
- **Cost:** about 2 lead-hours: ticket line and title (CTO, 0.25 h); evidence row (product-spec, 0.25 h); test
  designer's revision and a scoped `gov accept W2-32` (about 4 minutes of run) (0.75 h); one independent review
  (0.5 h); sweep items in section 4, the quick ones (0.25 h).
- **Leaves open:** the current pin's end-to-end figure is not yet known; the audit on 11-23 gives it, reported, not a
  gate on this close.

### Option (a2), apply now, but measured by the weekly memory audit instead
- **New S9 line:** as (a1), but "judged on the first memory audit after the lift (Monday 11-23, 40 questions), at
  today's pin", with the 80's result named as the earlier figure.
- **For W2-32's close:** W2-32 waits until about 11-24 (the audit's digest 09:00), then closes with W2-15a.
- **Cost:** (a1)'s 2 lead-hours plus about 0.25 h to record the audit's figures, and 12 days of waiting.
- **Leaves open:** the audit's set is fresh questions weighted toward what changed, with its own bar and writer; a
  weak first audit would hold W2-32 (and W2-27's dependency on it) for a measure DEC-1101 designed as a periodic
  check, not as a gate. It also double-counts: the audit already carries the bar (DEC-1101 (1)).

### Option (b), defer or re-baseline: S9 retired as overtaken, hit@5 kept as a reported figure
- **Change:** S9 deleted, marked "dropped, DEC-1126 (6): overtaken by DEC-1097 (1)(d)"; hit@5 stays a reported figure in
  W2-61's measure (DEC-833 already requires it).
- **For W2-32's close:** the line vanishes; same remaining blockers as (a1).
- **Cost:** about 3 lead-hours: (a1)'s work plus **re-homing K9's memory line**. DEC-1083 (2) and D9-FATES §3 say its
  home is W2-32's S9, "so the bar sits inside W2-27's dependencies"; DEC-1098 (1) repeats "its home under W2-32 S9".
  Retiring S9 leaves the bar with no home, so a line must go into W2-27 (or W2-88's S14, which is the bar for
  *adopted* repositories, not Gov OS). The test designer must also drop the S9 cases.
- **Leaves open:** the rule "85 to 95 % with room is not closed; the owner is told" (DEC-954 Q9e, DEC-957) loses its
  ticket home. That rule touches memory's target, which is the owner's (P1). Not recommended.

### Option (c), defer: a note only, the line's words untouched
- **Change:** append to S9: "met under DEC-1097 (1)(d): 78 of 79, 0 wrong claims; DEC-1098 (1)" and fix the evidence
  row. No re-wording, no test change.
- **For W2-32's close:** S9 is shown met; the acceptance rule still reads hit@5.
- **Cost:** about 0.75 lead-hours.
- **Leaves open:** the live line still says 85 % hit@5 and its test still encodes it, so S9 is "met" by a line that
  is not the bar. This is the drift DEC-866 asks us not to leave. Only worth it if the owner wants W2-32 to close
  before the test designer is free.

### Recommendation
**(a1)**, confidence **high** on the direction and **medium-high** on the choice of (a1) over (a2): the owner chose
the end-to-end bar and the verdict set exactly so a result could be taken once and used; DEC-1125 (2) says the audit
replaces ad-hoc re-measures, so the next audit is reported against today's pin and not made a gate on W2-32. If the
owner wants today's pin proven before W2-27's dependency is released, choose (a2) and accept the wait.

## 4. The supersession sweep (DEC-866): a list only

DEC-866 asks first whether DEC-1083 is marked. **It is.** DEC-1083's status line already carries "Changed by: ...
DEC-1098 (1) (K9's memory line met); DEC-1097 (1)(d) (K9's bar: right end to end >= 85 % with wrong claims <= 5 %,
target 95 %, hit@5 beside it, replacing item (2)'s hit@5 bar)". No register drift there. Two small points: DEC-1097's own
status line has no "Changes: DEC-1083 (2)" field (the replacement is said only on DEC-1083's side and in DEC-1126
(6)); and DEC-1097 (1)(d) never says "replaces" in its own text. `DECISIONS-IN-FORCE.md` lines 224, 313 and 503
already carry the change.

### A. Still states K9's hit@5 85 % bar (DEC-1083 (2)) as a gate, or the 58.3 % as the 80's level (by id and value)
- `.tickets/DAEO-0pyc.md` (W2-32): S9 line (85 %, hit@5) and the title ("the hit@5 85 row"); body line 101 ("the hit@5
  85 row on the dev queryset [W2-M341]") is DEC-725 history.
- `docs/changes/W2-32-evidence.md`: S9 row ("hit@5 28 of 48 (58.3 %), below 85 %"; "no improvement round has run yet").
- `tests/acceptance/W2-32/w2_32_record.py` (`FLOOR, TARGET = 85, 95`; `s9_state`); `test_w2_32_record.py` lines 63-67
  (the six s9 cases) and 70-77 (S9's row wants a hit@5 figure); `tests/acceptance/W2-32/README.md` lines 138 and 150-158.
- `packages/LIFT-CLOSES-1.md` lines 23, 164, 176 (58.3 % "the 80"); `packages/READY-AFTER-LIFT-1.md` line 26;
  `packages/DECIDED-NOT-DONE.md` row 126 (58.3 %): **the wrong figure itself, record drift for the CTO.**
- `packages/LIFT-1/D9-FATES.md` §3 item 1 (line 180), W2-32 row (line 65), lines 274 and 330-331: history of the
  decision, marked by DEC-1083's status line; no edit needed.
- `docs/plan/WAVE_2_WBS.md` lines 833, 859, 1861 ("memory proven: the enlarged measure at 85 %"; "W2-32 (memory at
  85 %)"; "the critical path is memory reaching 85 %"): K9's entry criterion in older words; the WBS says earlier text
  stays as history where not marked changed. Line 833 is the one that reads as a live criterion.
- `.tickets/DAEO-h4rh.md` (W2-27) line 124 ("memory proven") rests on W2-32's S9 through `deps`; no 85 % hit@5 text.
- History only, no edit: `packages/LIFT-1/E3-E5-DESIGN.md` line 56 ("beside DEC-1083's hit@5 bar, not replacing it");
  `packages/LIFT-1/FRESH-80-1.md` lines 8, 233, 290-291; `packages/LIFT-1/M3-ADOPTION-1.md` line 255;
  `packages/LIFT-1/E0-RESULT.md` line 30; `packages/LIFT-1/D4B-MEMORY-STAGE.md` line 171 (the 48 at 85 %, replaced by
  DEC-1074 (1)); `packages/ACT-MSET-1.md`, `-2`, `-3`, `-4` ("target 95 % hit@5, 85 % the floor").

### B. States CAP-10's hit@5 floor of 85 % (DEC-833; Contract CAP-10) as the memory proof or as a reporting rule
DEC-1097 replaced K9's bar only; it did not change DEC-833's "both figures in every report" or CAP-10. These are listed
for the CTO to judge, not as certain supersession. The one that reads most against DEC-1098 (1) is the first.
- `governance/project/orchestration/OWNER-GLOSSARY.md` line 88: "W2-61's measure (hit@5 against a floor of 85 %) is the
  standing proof that memory finds what is needed" (the standing proof is now end to end).
- `governance/project/prompts/w2-orchestrator.md` line 335 (CAP-10, DEC-833: both figures, hit@5 floor 85).
- `.tickets/DAEO-swdu.md` (W2-15b) lines 33, 37, 44, 89, 91 (hit@5 against 95 %, 85 the floor; "not closed" at 85-95 %
  with room); W2-15b is out of K9 and keeps its own verdict lines (D9-FATES).
- `.tickets/DAEO-h4rh.md` (W2-27) line 92 (EXAMIN's set measured with "both figures, hit@5 against CAP-10's floor of 85
  and the target of 95 %"); `packages/W2-88-STANDARD-1.md` line 48 and `.tickets/DAEO-l78m.md` (W2-81) line 28 (the
  scorer reports hit@5 against 85 and full evidence against 99 %); W2-88's S14 (`.tickets/DAEO-2bdu.md`) is already
  end to end.
- Tickets that re-run W2-61's measure with "both figures": `.tickets/DAEO-n0wb.md` (W2-92), `-a3u2`, `-jsg1`, `-s9qc`,
  `-iw1f`, `-rd0g` (W2-15a), `-t6hf`, `-gjjf`.
- `src/gov/retrieval/measure.py` (`FLOOR, TARGET = 85, 99`, line 78; "floor 85" in the total line, 468);
  `src/gov/retrieval/retrieve_baseline.yaml`; `template/governance/kernel/checks/retrieval-regression.yaml` (hit@5
  baselines, hard-block): code and a kernel check, out of this helper's scope and the CTO's to judge.
- Tests that assert "floor 85": `tests/acceptance/W2-61/`, `W2-61h/test_w2_61h_families.py:424`,
  `W2-134/test_w2_134_s4_unchanged.py:32`, `W2-91/README.md:165`; older, held to history: `W1-19`, `W1-42`.
- `docs/contract/capabilities/CAP-10.md` line 16, `docs/contract/CONTRACT_v4.md` line 197, `contract.yaml` line 742
  (the Contract's CAP-10 acceptance, mean hit@5 85): the Contract; a change goes through CAP-33, never in passing.

### C. Checked and clear
- `governance/project/path-map.yaml`: no hit@5 or 85 % memory bar. `template/governance/kernel/skills/`: none.
  The orchestrator prompt has no K9 hit@5 text (line 335 is under B).
- Not read in full: the files under `docs/assessment/`, `docs/research/` raw tables and `docs/plan/` history, which
  state the bar as it stood.
