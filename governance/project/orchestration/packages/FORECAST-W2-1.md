# FORECAST-W2-1: the rest of Wave 2, ticket by ticket (for the owner)

Written for the CTO by a read-only agent on 2026-11-09, at `w2/integrate` `b7b3f4b8`. Nothing was run but `gov plan`
(read-only, from the integrate code, without `--ready`). Every figure is marked: **M** means measured, with its source
named; **E** means estimated, with its basis in the footnotes. Dates are calendar days. Leads run seven days a week,
but your answers may slow at weekends.

## 1. Headline

**The lift** is set for about **11-15 (E; range 11-14 to 11-18)**. At the lift, **23 tickets close formally (M,
from the lists)**, and up to 6 more if they are merged before it. That leaves **39 Wave 2 tickets (E; up to 45)**.
EXAMIN's copy (W2-27) needs **21** of them, counting W2-27 itself. Assumed capacity under the three layers: three
leads at once (range 2 to 4) in three streams, which gives 40 to 55 lead-hours a day (E). On that basis:

- **EXAMIN's copy starts about 2026-11-21 (E; range 11-19 to 11-26).** The status block's "about 11-20" is one day
  earlier. The day comes from W2-88's larger scope under DEC-1098 (1), and from `gov plan` ordering W2-128 and W2-33
  behind the launch chain.
- **Wave 2 ends about 2026-11-28 (E; range 11-25 to 12-05).** After the copy, six milestones must run one after
  another (W2-27 → W2-28 → W2-29 → W2-30 → W2-46 → W2-47), and each waits for your verdict.

The risks that move these dates most are the sandbox experiment in front of W2-56, how many red rounds D-10 takes,
and when W2-88's six answers come back (§5).

## 2. Every ticket left after the lift (39)

The batches come from `gov plan --tickets <these 39>`, run read-only. Before the lift, `gov plan` holds 11 of these
tickets because each waits on one of the lift's formal closes (for example W2-88 on W2-129, W2-115 on W2-55, and
W2-124 on W2-122). Here those waits are taken as met, and the batches are re-levelled from `gov plan`'s own waits.
None of the 39 declares `needs:` yet (finding `NEEDS_UNDECLARED` on all 39). So the order rests on `depends_on` and
on overlapping writes only.

| id | title | state (11-09) | spent so far (M)¹ | left, lead-h (E) | basis | batch | EXAMIN needs |
|---|---|---|---|---|---|---|---|
| W2-11 | Briefs and the orchestration skill | built; lands as built | 5.5 h, 4 runs | 3.5–5.3 | a | 1 | yes |
| W2-20 | Machine-wide resource gate | rebuilt before the lift (item 8); S6, S9 live after | 6.3 h, 2 runs | 3.5–5.3 | a | 1 | yes |
| W2-23 | Adoption safety on a real repository | open | — | 10.5–13.6 | b (F) | 1 | yes |
| W2-81 | Proving ground: five synthetic repositories | in progress, partly built | 5.5 h, 5 runs | 5–8.8 | a, + one proving run | 1 | yes |
| W2-94 | EXAMIN's question set | open | — | 7–9.2 | d | 1 | yes |
| W2-105 | Template's install block removed | built | 4.5 h, 2 runs | 3.5 | a | 1 | yes |
| W2-110 | Product's CTO-only install rule | built, held | 7.5 h, 2 runs | 3.5–5.3 | a | 1 | yes |
| W2-90b | W2-90's next round of cases | in progress | 6.1 h, 1 run | 3.5–5.3 | a | 1 | yes |
| W2-115 | `gov close`, the smart close | open (takes W2-117) | — | 26–34 | d | 1 | yes |
| W2-124 | Rebuild without semantic store fails named | open | — | 7–9.2 | d | 1 | yes |
| W2-37 | `gov impact`, the query only | built, held | 3.2 h, 1 run | 3.5–5.3 | a | 1 | no |
| W2-40 | EXP-002, re-scoped to S3 | open | — | 3–4.3 | b (L) | 1 | no |
| W2-42a | Guard reads Bash writes; guard's homes | in progress; new lines unwritten | — | 10–19 | f | 1 | no |
| W2-130 | The link clean-up | in progress (a0, a1, a2, b1 done) | — | 2–4 | g | 1 | no |
| W2-52 | Lite A7 and A10 stage records | in progress | 3.7 h, 3 runs | 3.5–5.3 | a | 2 | yes |
| W2-56 | `gov launch` for every worker, sandboxed | restarted; waits on the sandbox experiment | — | 17–20 | d | 2 | yes |
| W2-93 | W2-81's held-out half | open | — | 7–9.2 | d | 2 | yes |
| W2-98 | Spec-writing skill for product-spec | open | — | 7–9.2 | d | 2 | yes |
| W2-121 | `gov dispatch` | open | — | 17–20 | d | 2 | yes |
| W2-104 | Skill evaluation harness (optional) | in progress | 9.2 h, 2 runs | 3.5–5.3 | a | 2 | no |
| W2-120 | Validator refuses brief without the fields | open | — | 3–4.3 | b (L) | 2 | no |
| W2-90c | W2-90b's cases that need W2-105 | open | — | 3–4.3 | b (L) | 2 | no |
| W2-60a | Role, skills, model loaded at launch | built, held | 18.1 h, 2 runs | 3.5–5.3 | a | 3 | yes |
| W2-88 | Memory for any repository (the standard) | open; waits on your six answers | — | 30–38 | e | 3 | yes |
| W2-45 | `gov check` runner semantics and scale | open | — | 7–9.2 | b (S) | 3 | no |
| W2-111 | Hook-latency cases time the hook | open | — | 3–4.3 | b (L) | 3 | no |
| W2-113 | Product's CTO named at adoption | open | — | 3–4.3 | b (L) | 3 | no |
| W2-60b | One record per session | open | — | 7–9.2 | d | 4 | yes |
| W2-15b | EXP-003 pass 2, the final measurement | open | — | 9–13 | d² | 4 | no |
| W2-82 | Light Definition of Ready check | open | — | 5–9.2 | b (S) | 5 | no |
| W2-128 | The templates, one per role | open; part built in D-5 before the lift | — | 9.2–18.4 | g | 6 | yes |
| W2-33 | Three layers' roles, the typed handoff | open | — | 7–9.2 | d | 7 | yes |
| W2-27 | EXAMIN adoption on a copy | open | — | 1 day (8–16) | c | 8 | **the copy** |
| W2-116 | The designers' store in the product | pass 1 merged; S2 next | — | 3.5–5.3 | a | 8 | no |
| W2-28 | Independent verdict on the copy | open | — | 1 day (4–8) | c | 9 | no (after) |
| W2-29 | EXAMIN adoption on the real repository | open | — | 1 day (8–16) | c | 10 | no (after) |
| W2-30 | Healthy-adoption verdict | open | — | 1 day (4–8) | c | 11 | no (after) |
| W2-46 | Wave 2 exit run | open | — | 1 day (8–16) | c | 12 | no (after) |
| W2-47 | Wave 2 exit audit | open | — | 1 day (4–8) | c | 13 | no (after) |

**May not be filed yet:**
- W2-132 (W2-128's code parts), split off when it is reached.
- W2-143 and W2-144 (the glossary), filed only if the retest helps.

**Footnotes:**
1. **Spent so far (M):** the sum of `duration_ms` over the lead runs in `.gov-runtime/scratch/orchestrator/log/W2-*.json`. These are the leads from before the emergency only. Agent work since 11-02 is not logged in that form, so these are lower bounds.
2. **W2-15b (E):** half of P1-PLAN §G's 17–20 for W2-15a and W2-15b together, plus GPU windows.

**Bases:**
- **a:** a resume of built work is 1 to 1.5 runs × the median run of 3.52 h (M, PLAN-W2-DEC953 §2.0). E.
- **b:** the profile medians, L 4.3, S 9.2 and F 13.6 h (M, PLAN-W2-DEC953 §2.0). The low end is cut by a quarter for the lifted gates. E.
- **c:** WBS §4's rule, one day per integration or audit ticket. E.
- **d:** P1-PLAN §G's figure for this ticket. E.
- **e:** W2-88-STANDARD-1 §4: 30–38 lead-h, plus about 2 days elapsed for one full practice run on a proof repository. E.
- **f:** scaled by est. LOC (600) from W2-66 and W2-67 (M: 400 LOC took 13.1 h, 750 LOC took 18.8 h), less what is built. E.
- **g:** the CTO's judgement from the ticket's state: W2-128 is 4–5 working days in D9-FATES §4, part of it done in D-5; W2-130 has batches a3 and b2 left after the sitting. E.

## 3. The counts

| | tickets | basis |
|---|---:|---|
| Wave 2 tickets in `.tickets` | 151 | M |
| closed now | 74 | M (status `closed`) |
| not closed | 77 | M (37 in progress, 40 open) |
| leave Wave 2 for Wave 3 (W2-17, 18, 19, 34, 35, 36, 42, 100, 101) | 9 | M (D9-FATES fates) |
| W2-00, the coordination ticket (closes with the wave) | 1 | — |
| **formal closes at the lift: certain** | **23** | M (lists) |
| formal closes at the lift: if merged before it | up to 6 | E |
| **left after the lift** | **39** (up to 45) | E |
| of which EXAMIN's copy needs (W2-27 included) | **21** (22 if W2-15a slips) | M (W2-27's `depends_on` closure) |
| of which come after the copy or are not on its path | 18 | M |

**The 23 certain closes** (`report-state.json` `merged_not_closed`; DEC-1083 (7)):
- **the 21 merged:** W2-04, 05, 13, 32, 55, 61h, 91, 92, 96, 112, 122, 123, 126, 129, 131, 133, 134, 135, 136, 137, 138;
- **at D-10's green run:** W1-01b and W2-66b.

Seven of the 23 carry a line met only in part: W2-55, 61h, 92, 96, 112, 122 and 126. Each needs its measure, a
re-word or a move before it closes (D9-FATES §4).

**The 6 that close at the lift only if merged first:**
- W2-139 and W2-140 (one batch, DEC-1098 (6));
- W2-141, W2-142 and W2-145 (item 8, before the re-pin);
- W2-15a, a formal close whose S3 is met only in part. W2-32 depends on it, so it must close with W2-32 or W2-32's close waits.

W2-20 is also rebuilt before the lift, but it closes after the lift, once S6 and S9 are measured live.

**Volume (E).** The 21 tickets EXAMIN needs come to 189–259 lead-h at the plan's medians. Less the 20–25 % the lifted
gates took out of each run (P1-PLAN §G), that is **142–207 lead-h**. The other 18 come to 65–118 lead-h. All 39 come
to **207–326 lead-h**.

## 4. The schedule under the three layers

**The capacity it assumes:**

| | figure | basis |
|---|---|---|
| layers | the CTO; 3 streams under 2 to 3 Senior Engineers; their leads; 1–2 workers per lead | DEC-1087 (13), SEVEN-ANSWERS §5 |
| leads at once | **3** (range 2 to 4) | E, from RAM below; P1-PLAN §G used 2–3 |
| sessions at once | about 10–13 (1 CTO + 2–3 Senior Engineers + 3 leads + 4–6 workers) | E. CAPACITY-1's 29-session design does not fit this machine |
| RAM per lead | p95 4.2 GB, max 6.5 GB | M, the dispatcher's peaks (status.txt, 11-09 00:23) |
| RAM free for leads | 13.1 GB available with the servers up, less the 3.0 GB floor: about 10 GB | M, dispatcher 11-09 00:33 |
| RAM for the other sessions | 0.24 GiB each, so 2–3 GB for the rest | M, CAPACITY-1 §1 |
| what fits | 2 leads at p95 (8.4 GB) always; a 3rd when the Load Balancer staggers the peaks | E |
| machine | 20 CPUs, 3 heavy slots × 6 workers, RTX 5070 Ti 16 GB (7.3 GB used), one shared reranker | M, dispatcher |
| searches at once | up to about 10 (each lead and worker searches; with search again once, two searches per question) | E |
| search time | 13.4–17.4 s per search with 20 at once (about 41 scored pairs each), so about 7 s with 10 at once and 4–5 s with 6 | M at 20 (G1-PROFILE, PAT-1); E below 20, taking time as linear in pairs |
| throughput | 40–55 lead-h a day; about 25 % less over the trial's first three days | E (P1-PLAN §G; SEVEN-ANSWERS §5). Measured 80–110 a day on 10-30 to 11-01 with about 6 leads, overloaded (M, P1-PLAN evidence 2) |

**The streams (proposed):**
- **A, launch and roles:** W2-20, 56, 60a, 60b, 11, 98, 120, 128, 33, 82, 116.
- **B, memory and adoption:** W2-81, 93, 52, 23, 88, 94, 124, 105, 110, 90b, 90c, 111, 113, 15b.
- **C, close, dispatch and the rest:** W2-115, 121, 104, 45, 37, 40, 42a, 130.

The CTO keeps the milestones (W2-27 to W2-47).

**By batch and week (E).** L is the lift, about Sunday 11-15.

| when | what |
|---|---|
| **week of 11-09** (before the lift) | Item 8 (W2-141, W2-20 rebuilt, W2-142, W2-145); Q07 and Q14; W2-139 and W2-140; W2-130's sitting; D-5 (W2-128's templates in part); D-6 part 2; the sandbox experiment, approved and run (3–4 working days, E, SANDBOX-GUARD-EXP-1 §6); your W2-88 answers; then D-10 on your word |
| **L, 11-15 to 11-16** | The re-pin (ADR-0002 re-read); 23–29 formal closes, at 10–20 min each (M, PLAN-W2-DEC953 §2), so 4–8 h plus the seven in-part measures; `gov plan --ready`; the three-layer package; the TPL-8 pilot starts on batch 1 |
| **11-16 to 11-18** | Batch 1 (14 tickets; W2-115 the largest), then batch 2 as W2-20, W2-11 and W2-81 clear: W2-52, W2-93, W2-98, W2-121, and W2-56 once the experiment's result is in. The stream trial runs on these tickets |
| **11-18 to 11-20** | Batch 3 (W2-60a, W2-88, W2-45, W2-111, W2-113); batch 4 (W2-60b, W2-15b); W2-88's practice run (about 2 days elapsed) |
| **11-19 to 11-21** | Batches 5 to 7: W2-82, W2-128, W2-33 |
| **11-21** | **EXAMIN's copy, W2-27** (batch 8), with W2-116 |
| **11-22 to 11-28** | W2-28 → W2-29 → W2-30 → W2-46 → W2-47, a day each plus your verdicts. Stream C's remainder (W2-42a, W2-45, W2-82, W2-104, W2-116) runs beside them. **Wave 2 ends about 11-28** |

**The critical path (E):** the lift → W2-20's live close → [the sandbox experiment's result] → W2-56 → W2-60a →
W2-60b → W2-82 → W2-128 → W2-33 → W2-27 → W2-28 → W2-29 → W2-30 → W2-46 → W2-47.
- **Length to W2-27:** 52–77 lead-h in series (E), plus a review and merge at each of the 7 hops: about 5 to 6 days after the lift.
- **The near-critical chain:** W2-81 → W2-88 (build plus one practice run) → W2-27, about 5 days.
- **W2-82's link is not a dependency.** W2-128 waits on W2-82 only because they write the same file (`ticket.schema.json`, a tiebreak in `gov plan`). W2-82 is not on EXAMIN's path. A `plan_override` or a decision to put W2-82 after W2-27 takes about 0.5 day off.

## 5. The risks, their effect on the dates, and the mitigations (all effects E)

| risk | effect on the dates | mitigation |
|---|---|---|
| **The lift's formal closes.** 23 to 29 closes, seven with lines met only in part (W2-55, 61h, 92, 96, 112, 122, 126); W2-55 S1's re-word is your §5 question 2 | +0.5 to 1 day on every date if the in-part measures run after the lift | Take the in-part measures and re-words before the lift, beside D-10; approve W2-55 S1 (a); close W2-15a with W2-32 |
| **D-10's reds.** The last full run had 32 reds in 8 groups (M, 11-02, before the cut); the suite is now cut to 5,628 cases, about 1.8 h a run plus re-runs (E, D4-LIST); three reds are known (`core.bare`'s half, the W1-19 `-n auto` case, W1-01b/W2-66b/W2-90c) | 2 rounds (planned): none. 3 rounds: +1 day. 4 or more: +2 to 3 days, and the lift goes to about 11-18 | Fix the three known reds before the first run; run D-10 as soon as item 8 has merged; triage the reds by group the same evening |
| **The three layers' trial.** Pilot 1 day, then a 2-day stream trial (SEVEN-ANSWERS §5); untried on this machine; RAM fits 3 leads only if their peaks are staggered | About −25 % throughput over 3 days: +0.5 to 1 day. If the trial fails (drift, compactions), fall back to two tiers at the same 40–55 lead-h a day: +0 to 0.5 day | Run the trial on batch 1's real tickets, not apart from them; measure it on R2's figures; agree the fall-back in the three-layer package |
| **The sandbox experiment and W2-56.** Design out 11-09; 3–4 working days after your approval (SANDBOX-GUARD-EXP-1 §6); both results to you before W2-56 builds anything (DEC-1098 (4)) | If the results come by L+1: none. By L+3: +1 to 2 days on EXAMIN and the end. If the guard with the sandbox misses the 100 % bar, W2-56 keeps the path-map guard alone, which is probably smaller | Approve the design on 11-10 and run it beside D-10 (CPU only); let W2-56's test designer write the tests that do not depend on the result in the meantime |
| **The item-8 tickets** (W2-141, W2-20, W2-142, W2-145; test designers started 11-09) must merge before the re-pin | Each one late holds the lift day for day | One review round each; anything not ready by D-10 goes to after the lift, with your word (except W2-20's launch line, which W2-136 needs) |
| **The glossary retest** (DEC-1097 (6) (b); on the 138; GPU; no commits on integrate during a GPU measure) | Freezes merges for its hours (+0 to 0.5 day). If it helps: W2-143 and W2-144 are filed and W2-88 gains a Wave 0 line, about +10–20 lead-h on the near-critical chain (+0.5 to 1 day) | Run it before the lift or in a night window; keep it out of W2-88's path unless it beats E2 |
| **G1's fewer scored pairs** (DEC-1097 (10), after the lift) | Any ranking change voids the fresh 80's verdict (FRESH-80-READINESS §4). Re-proving K9's memory line could add 2 to 4 days to EXAMIN | Not needed for speed: 10 at once is about 7 s (E). Defer it until after EXAMIN's copy or to Wave 3 |
| **W2-88's six answers** (W2-88-STANDARD-1, 11-09) | Each day late moves the near-critical chain a day | Answer before the lift; write the practice run's sets (an independent writer) while the code is built |

## 6. What is assumed, and what would change the forecast

**Assumed:**
- The lift is about 11-15, with D-10 green in 2 rounds.
- The 23 certain closes go through without re-opening any ticket.
- The 6 pre-lift tickets merge before the re-pin.
- Three leads run at once, around the clock (§4), at the plan's medians less 20–25 % for the lifted gates.
- Your answers take 0.5 to 1 day per package (P1-PLAN §G; 61 % of returns ended in packages).
- No new ticket enters EXAMIN's path except W2-132, which sits inside W2-128's estimate.
- K9's memory line stays met: no ranking change before the copy.
- The milestones W2-27 to W2-47 take one day each.

**What would move the dates:**
- **Earlier (−1 to 2 days):**
  - the lift on 11-14;
  - W2-82 put after W2-27;
  - the sandbox result in before the lift;
  - W2-88's answers and sets ready at the lift;
  - a 4th lead, which needs about 4 GB more free RAM.
- **Later:**
  - each extra D-10 round, +1 day;
  - the experiment's result after L+2, +1 to 2 days;
  - a failed stream trial, +0.5 day;
  - G1's fewer pairs adopted before the copy, +2 to 4 days;
  - a formal close that re-opens its ticket, +0.5 to 1 day each;
  - W2-88's practice run needing a second verdict set, +2 days;
  - your verdicts at weekends (11-21/22 and 11-28/29).
- **Re-estimate** at the lift with `gov plan --ready`, once the tickets carry `needs:`. Then weekly, old and new
  figures side by side (the register's standing rule).

**Sources:** `.tickets/*.md`; `report-state.json`; P1-PLAN §A, F and G; D9-FATES §1, §3, §4 and §5; DEPENDENCY-MAP-1; `gov plan` (`src/gov/plan/`, read-only); PLAN-W2-DEC953 §2.0; the lead logs; CAPACITY-1; SEVEN-ANSWERS §5; G1-PROFILE; W2-112's ticket; the dispatcher's `status.txt`; DECIDED-NOT-DONE §0 and §0b; DEC-1087 (13), DEC-1097 and DEC-1098; W2-88-STANDARD-1; SANDBOX-GUARD-EXP-1 §6; D4-LIST; START-NEXT-SESSION.
