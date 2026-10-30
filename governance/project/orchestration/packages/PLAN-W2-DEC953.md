# PLAN-W2-DEC953

The rest of Wave 2 and the plan for closing its tickets, under DEC-953.

From the W2 orchestrator's planning helper, 2026-10-30, for the owner to review.

**Approved by the owner with amendments (DEC-954, 2026-10-30).** The owner's text is verbatim in `.gov-runtime/scratch/orchestrator/drafts/DEC-954-owner-text.md`. The plan below is edited to the approved version; §7 gives each question with the owner's answer.

**What DEC-954 changed, in short**
- **The order (Q2, Q8, the roles spec):**
  1. ACT 1 at milestone 2: the five-rule guard switched on (the settings regeneration);
  2. then the 10 built tickets finished and closed on the 10 practices, and the streams in parallel, within the resource gate;
  3. the roles spec first, for the owner's approval: W2-60b, W2-11, W2-33 and W2-83a/b build nothing further until it is approved (W2-60a's scoped last round finishes meanwhile);
  4. memory lands, for this repository and for any adopted repository (W2-88, Q9f);
  5. the roles land, with the three layers' foundations (the CTO's and the Senior Engineers' roles, skills and briefs; a coordination ticket per stream; the CTO's watchers);
  6. ACT 2: one re-pin, so all of it takes effect together;
  7. the three layers start, in new sessions: the CTO and a Senior Engineer per stream;
  8. EXAMIN's copy only when K9's entry criteria are met.
- **EXAMIN's copy is gated by K9's criteria, not a date (Q1).** Every date here is an estimate, re-estimated weekly.
- **Names (Q13):** the master orchestrator is the **CTO**; each sub-orchestrator is a **Senior Engineer** for its stream. Agents keep their role names.
- **The guard has five rules:** DEC-953 item 2's four, plus reviewers and auditors write only their own review and audit records.
- **Tickets:** W2-78 parked (Q5); W2-85 goes ahead (Q3); W2-67's rounds right after memory's quick wins (Q11); W2-20 on DEC-950's rule (Q12); a coordination ticket per stream (Q13); the release through W2-16 (Q8c); a new memory ticket, **W2-88**, memory for any repository (Q9f).

**Legend**
- **Profile:** L = LITE, S = STANDARD, F = FULL.
- **est:** lead-hours. The default is the measured median for the profile (see §2.0); any other basis is named. An estimate is marked "est.".
- **Go:**
  - **A** = goes ahead now (DEC-953 items 2 to 5, memory's quick wins).
  - **R** = a lead running now, which continues.
  - **F** = finish built work, **after ACT 1** (DEC-954 Q2).
  - **W** = waited for the owner's approval of this plan. Approved by DEC-954: it starts in DEC-954's order, within the resource gate. **W·RS** = it also waits for the owner's approval of the roles spec.
- **Marks:**
  - ◆M = memory foundation (item 6a, item 8c).
  - ◆R = roles, skills and briefs foundation (item 6b, item 8c).
  - ★ = on the critical path to EXAMIN's copy.

---

## 1. Summary (one screen)

**What changes**
- Tickets close on the audit's 10 practices (§5 of AUDIT-GOV-FEATURES-1). There is no `gov close` gate, no ratchet commit, no quiet window and no queue gates (a) to (h).
- No re-pins for gates. There are two owner acts (DEC-954 Q8): ACT 1, the five-rule guard; ACT 2, one re-pin once memory, the roles and the three layers' foundations have landed.
- `gov close` is proved on the proving ground (W2-81) and on EXAMIN's copy (W2-27), each on W2-16's numbered, frozen release, not by re-closing this repo's tickets.
- The streams' tickets run in parallel from ACT 1. The three layers (the CTO and a Senior Engineer per stream) start after ACT 2, in new sessions.
- 19 tickets move to Wave 3, and W2-78 is parked. W2-79 and W2-80 are withdrawn. Six repair tickets are closed.

**EXAMIN's copy is gated by K9's entry criteria, not by a date (DEC-954 Q1).** The criteria are: memory proven; the roles, skills and briefs landed; the proving ground passed; the rest of the minimum closed. **Estimate only: 2026-11-12** (range 11-09 to 11-20), re-estimated weekly. The old target was 11-18 (range 11-14 to 11-25; REPLAN-W2 §3, DEC-941). Since DEC-954, the estimate has not been recomputed. DEC-954 adds the roles spec's owner turn, ACT 1 before the built tickets, ACT 2 before the three layers, and W2-88 on the memory path. The first weekly re-estimate takes them in.

The basis:
- **The critical path is memory reaching 85 %:** W2-87 → W2-55 → W2-13 → W2-15a → W2-32, about 55 lead-hours in series. Memory is judged on the combined memory spec (DEC-954 Q9c).
  - The proving ground runs alongside: W2-81 (est. 26–30 h), its run, then the fixes for what it finds.
  - **W2-88 also runs alongside** (memory for any repository, est. 20–26 h; DEC-954 Q9f). It comes after W2-52, W2-76 and W2-81's builders, and it must close before W2-27, which is its live trial.
  - **The roles stream waits for one owner turn:** the roles spec (DEC-954).
- **Lead time per ticket** is the measured median for its profile (96 lead returns, 399.4 h, $631.91, `log/W2-*-A5-*.json`). These medians include the old gate waits, so they are cautious.
- **About 16 working lead-hours a day per chain** (est.). Leads run through the day and night, except the 02:00–05:00 nightly and the morning handover.
- **Closes take 10–20 min scoped, about 70 min full** (audit §5, practice 2). The measured means were 12.0 min scoped and 72.5 min full (audit §3.2).
- **What makes it earlier than 11-18:**
  - the lifts: 42 % of lead time went on machinery, and 16.4 h of launch waits in 20 h (audit §1);
  - more leads at once: a mean of 4.52 and a peak of 7 since 10-29 (`log/lead-mem.jsonl`), against the 3 assumed in REPLAN.
- **What makes it later:**
  - memory starts at 40 % hit@5, not lens B's 65 %;
  - a second W2-32 round adds about 1 day;
  - an unknown number of proving-ground fixes.

**Counts**

| Section | Tickets |
|---|---|
| §2 Wave 2, remaining (as sent) | **51** (49 filed + W2-86, W2-87 to file) |
| — go ahead now (A) | 8 |
| — running leads (R) | 3 |
| — finish built work (F) | 10 |
| — wait for approval (W) | 30 |
| §3 Deferred to Wave 3 | **19** |
| §4 No longer needed | **2** withdrawn (W2-79, W2-80) + **6** repair tickets closed |
| §4 Machinery tickets closed as built, kept as product (also counted in §2) | 6 (W2-57, 67, 71, 76, 77, 78) |

The check as sent: 90 Wave 2 tickets (88 with `wbs_id` + W2-15a and W2-15b) − 20 closed = 70 open. 49 + 19 + 2 = 70.

**After DEC-954:**
- **Wave 2, remaining: 51.**
  - 49 filed: the 49 above, with W2-87 now filed (`DAEO-s9qc`) and W2-78 parked out of them.
  - 2 to file: W2-86 and **W2-88**.
  - Also to file: one coordination ticket per stream, at the three-layer start (Q13). Their count is set by the stream count, which waits on Q10's measurement.
- **Moved out:** 19 deferred, plus W2-78 parked (Q5): 20 to Wave 3.
- **The check:** 71 open (70 + W2-87) = 49 + 19 + 1 + 2.
- **Machinery closed as built and kept as product:** W2-57, 67, 71, 76 and 77. W2-78 is parked.

---

## 2. Wave 2 (item 10a)

### 2.0 How the estimates are made

**Measured lead-hours per ticket**, as each ticket's runs summed (`duration_ms`):

| Profile | n | Median | Middle half |
|---|---|---|---|
| L | 6 | **4.3 h** | 0.2–7.9 (range) |
| S | 11 | **9.2 h** | 4.9–18.5 |
| F | 18 | **13.6 h** | 7.4–17.4 |

**Other measured figures:**
- one lead run: median 3.52 h, 75th percentile 5.42 h, maximum 16.12 h;
- 2.7 runs per ticket on average (96 runs over 36 tickets).

**What the estimates use:**
- A resume of built work counts as **one run, 3.5 h** (median run).
- Large tickets are scaled by est. LOC from W2-66 (400 LOC, 13.1 h) and W2-67 (750 LOC, 18.8 h). That is how W2-81 (1,200 LOC) gets **est. 26–30 h**.
- Integration and audit tickets use WBS §4's rule: 1 day each (est.).

### 2.1 Order and parallel streams

**The order (DEC-954), each step after the one before:**
1. **ACT 1** at milestone 2: the five-rule guard switched on (the settings regeneration, the owner's act). Milestone 2 also needs the gates lifted, selection proven scoped and the five closes done.
2. **The 10 built tickets** (W2-67, W2-51, W2-49, W2-37, W2-16, W2-84, W2-05, W2-20, W2-52, W2-60a) are finished and closed on the 10 practices under the five-rule guard. **In parallel, the streams S1 to S4 run** within the resource gate.
   - Already going before ACT 1: W2-87, W2-86, W2-85, W2-76 (finish and close), and W2-64 (P-W2-64-1 (a)).
3. **The roles spec first**, written by the CTO for the owner's approval. W2-60b, W2-11, W2-33 and W2-83a/b build nothing further until it is approved.
4. **Memory lands,** for this repository (S1) and for any adopted repository (W2-88).
5. **The roles land** (S2). This includes the three layers' foundations: the CTO's and the Senior Engineers' roles, skills and briefs; a coordination ticket per stream; the CTO's watchers.
6. **ACT 2:** one re-pin, so memory, the roles and the foundations take effect together.
7. **The three layers start,** in new sessions: the CTO and a Senior Engineer per stream.
8. **EXAMIN's copy (W2-27),** only when K9's entry criteria are met.

S0 is the CTO's own work. S1 to S4 run side by side from step 2. Until step 7 the CTO runs them itself; after it, a Senior Engineer runs each. Inside a stream, a ticket follows its dependency.

| Stream | Holds | Runs beside | In series because |
|---|---|---|---|
| S0 CTO (the master) | closes, integration, held work, the roles spec, ACT 1 and ACT 2, exit | all | the exit chain |
| S1 Memory ★ | 17 (with W2-88) | S2, S3, S4 | retrieval paths (W2-87 → W2-55 → W2-13) |
| S2 Roles, skills, briefs | 6, plus the three layers' foundations | S1, S3, S4 | the roles spec first, then the launcher file (W2-60a → W2-60b) |
| S3 Sandbox and launch | 5 | S1, S2, S4 | the launcher file, after S2's W2-60b |
| S4 Adoption and proving ground ★ | 8 | S1, S2, S3 | K9's criteria before W2-27 |

**CTO tasks with no ticket:**
- **Done or going now:**
  - item 3: the nightly rule;
  - item 4: selection that leaves governance files out, in the close script and `scoped_plan.py`, with its proof on W2-64, W2-76 and W2-78's worktrees;
  - item 5: the closes;
  - item 7: the decisions-in-force list;
  - DEC-952, DEC-953 and DEC-954 recorded.
- **ACT 1 (DEC-954 Q8a), replacing item 2's switch-down:** the five-rule hook (committed `f7533c61`, not wired), its planted cases, the settings regeneration as the owner's act, and the live-settings tests revised by a test designer.
- **The roles spec (DEC-954), sent as soon as it is ready.** It covers:
  - (a) what exists and where;
  - (b) every role from the CTO to the auditor: duties, reads and writes, skills, model, what its brief always contains, and its handover;
  - (c) the gaps (at least the ticket lead's role file, machine-readable defaults per role, the CTO and the Senior Engineers) and the ticket that fills each.
- **Memory's measure enlarged (Q9a):** the size and time cost go to the owner (`drafts/plan-dec954/MEMORY-SPEC-MAP.md` part B). W2-61h is re-scoped to write it.
- **The memory spec mapped to the tickets (Q9d):** `drafts/plan-dec954/MEMORY-SPEC-MAP.md` part A.
- **W2-88 filed** in Wave 2's minimum (Q9f).
- **Q10, after scoped tests, W2-76 and W2-06 have finished:** the machine's use measured by kind (Claude sessions, test runs, rebuilds, gitleaks, git, the code graph, Ollama), for the owner's decision.
- **ACT 2 (Q8b):** one re-pin, once memory, the roles and the foundations have landed.

### 2.2 S0 — the CTO (the master): closes, integration, held work and the exit

| # | W2 · tk | What | Now | Deps | ∥ | P · est | Go |
|---|---|---|---|---|---|---|---|
| 1 | W2-71 · e8f0 | secrets check, W2-L423 | merged | — | all | F · close 0.2–1.2 h | A |
| 2 | W2-77 · b6hm | nightly own-clone clean-up | merged | — | all | F · close | A |
| 3 | W2-57 · cy5o | load out of the close | merged | — | all | F · close | A |
| 4 | W2-76 · tgk2 | rebuild timings, watchdog | lead running | — | all | S · 1 run left | R |
| 5 | W2-78 · v4is | governance edits stop widening closes | **parked** (P-W2-78-PARK (a), DEC-954 Q5); branch kept unmerged; its discoveries filed as rows | — | — | — | Wave 3 |
| 6 | W2-85 · gdzh | W2-54's 2 time limits to the nightly | claimed (DEC-954 Q3) | — | all | L · 4.3 h | A |
| 7 | W2-67 · 9nys | test hygiene (rest of r1) | r1 merged, rest held | — | all | F · its remaining rounds right after memory's quick wins (Q11) + review | F |
| 8 | W2-51 · egsy | plan validator | built, held | W2-01 | all | S · serial phase only | F |
| 9 | W2-49 · ha8z | Contract v4.2 lite (CIT-P) | built, held | W2-51 | all | S · owner CIT-P | F |
| 10 | W2-37 · 6n5k | `gov impact` | built, held | W2-03 | all | F · 1 run (merge-back) | F |
| 11 | W2-16 · 49o5 | hash-pinned releases; **the numbered, frozen release W2-81 and EXAMIN's copy install (Q8c)** | built, held | W2-49 | all | F · 1 run + owner tag | F |
| 12 | W2-24 · 0mab | Track A gate run | open | Wave 2 Track A (cut, §6) | — | F · 1 d (est.) | W |
| 13 | W2-25 · btt7 | Track A audit | open | W2-24 | — | F · 1 d (est.) | W |
| 14 | W2-46 · nn1s | Wave 2 exit run | open | all Wave 2 | — | F · 1 d (est.) | W |
| 15 | W2-47 · jip3 | exit audit | open | W2-46 | — | F · 1 d (est.) | W |
| 16 | W2-00 · sdxk | the CTO's coordination | open | closes last | — | L | W |
| 17 | (to file) | a coordination ticket per stream: the guard and the CTO know each Senior Engineer's identity (Q13) | to file at the three-layer start | the roles spec; built in S2 before ACT 2 | — | L each (est.) | W·RS |

### 2.3 S1 — memory ★ (item 6a)

| # | W2 · tk | What | Now | Deps | ∥ | P · est | Go |
|---|---|---|---|---|---|---|---|
| 1 | W2-61 · iw1f | 20-question measure (tool); **approved as EXP-003's measure, amended (DEC-954 Q9)** | merged (`758cd53f`); close due | — | all | S · close | A ◆M |
| 2 | W2-86 · (to file) | `template/` embedded; vendored code its own namespace | draft | — | W2-87 | path-map line by the CTO (DEC-952 1c), est. 2 h + rebuild + measure | A ◆M |
| 3 | W2-87 · s9qc | rank by authority; **the register-as-one-record fix stays inside, KPI 4 (Q4)** | filed and claimed (`df0782fa`) | — | W2-86 | S · 9.2 h | A ◆M ★ |
| 4 | W2-03 · ym8a | decisions as records | merged | — | all | S · close | A ◆M |
| 5 | W2-64 · 0uhh | record validator widening | lead running | — | all | S · 1 run left | R ◆M |
| 6 | W2-84 · m1u3 | hidden-set refusal in every tree (guard rule 2) | serial phase + review left | — | all | F · 1 run + full run + review | F |
| 7 | W2-05 · 0z8c | git environment (run 4) | W1-02 revision first | W2-01 | 1–6 | F · L 4.3 + 3.5 h | F |
| 8 | W2-55 · arrl | superseded entries out | open | W2-03, W2-87's entry map | W2-04 | S · 9.2 h | W ◆M ★ |
| 9 | W2-04 · u4oz | `gov context` bounded | open | W2-03 | W2-55 | F · 13.6 h | W ◆M |
| 10 | W2-61h · h2k3 | hidden half (auditor); **re-scoped to the enlarged set (Q9a): 28 new questions, 24 hidden and 4 visible** | open | W2-84, and the five-rule hook live (ACT 1, Q9b) before the hidden half is used | 8–9 | S · est. 12–14 h | W |
| 11 | W2-06 · kia7 | pre-commit tier, re-index | open | W2-05 | 8–10, 12 | F · 13.6 h | W |
| 12 | W2-13 · zqvn | ranked lexical (BM25) | open | W2-03; after W2-55 (same paths) | W2-06 | F · 13.6–17 h | W ★ |
| 13 | W2-08 · 7r5e | hooks back on (+ owner reinstall) | open | W2-06 | 14–15 | S · 9.2 h | W |
| 14 | W2-15a · rd0g | EXP-003 baseline; **Q-2 answered: W2-61's measure, enlarged (DEC-954 Q9)** | open | W2-04, W2-13, W2-61h | W2-08 | F · 13.6 h | W ★ |
| 15 | W2-32 · 0pyc | bounded improvements (the 85 % row); **below 85 % after two rounds: an escalation to the owner with the reasons (Q9e)** | open | W2-15a | — | S · 9.2 h a round | W ★ |
| 16 | W2-15b · swdu | EXP-003 final (99 %), **on the combined memory spec (Q9c)** | open | W2-32, W2-26, W2-88 | S4 | F · 13.6 h | W |
| 17 | **W2-88 · (to file)** | **memory for any repository (Q9f):** at adoption, assess any repository however large; plan the refactoring full indexing needs, as governed tickets for its owner's approval (never applied); build the full index and the embeddings; set up the SQLite and vector-store structure. Proven on W2-81's five, two real public GitHub repositories, and the register's test repositories. EXAMIN's copy is its live trial | draft (`drafts/tickets/W2-88.md`) | W2-52, W2-76, W2-81 (builders), W2-03 | W2-13, W2-55, W2-04; paths beside S4's W2-23 (`src/gov/adopt/`, split by file) | F · est. 20–26 h (500 LOC, scaled as §2.0; + the real runs) | W ◆M ★ |

**The memory foundation has landed when:**
- W2-86 and W2-87 are re-measured;
- W2-55 and W2-04 have closed;
- W2-61's measure has been repeated.

That is DEC-943's trigger: from then, the CTO uses `gov context` at every resume. Est. 11-02.

**Memory has landed (DEC-954 step 4) when** this repository is at 85 % on the enlarged measure (after W2-32), **and** W2-88 has closed, so memory works in an adopted repository. Memory is judged on the combined memory spec (Q9c): semantic and lexical search, full indexing, full embeddings, the knowledge and code graph, and the SQLite and vector-store structure. It is measured along the way. The spec's mapping to the tickets, and its gaps, are in `drafts/plan-dec954/MEMORY-SPEC-MAP.md`.

**At 85 %** (the K9 copy criterion, DEC-833): after W2-32. Est. 11-06, 11-07 if a second round is needed. If it is still below 85 % after two improvement rounds, it goes to the owner with the reasons. At the third the owner decides (Q9e): a discovery and research ticket benchmarking market tools in a separate worktree, accepting the level, or another course.

### 2.4 S2 — roles, skills, briefs (K3, item 6b)

**The roles spec comes first (DEC-954).** The roles are built on an approved spec, never on a sketch. Rows 2 to 6 build nothing further until the owner approves it. Row 1's scoped last round (its fail-open fix) finishes meanwhile.

| # | W2 · tk | What | Now | Deps | ∥ | P · est | Go |
|---|---|---|---|---|---|---|---|
| 0 | (the CTO's) | **the roles and briefs spec**, for the owner's approval | to write; sent as soon as ready | — | S1, S3, S4 | — | A |
| 1 | W2-60a · cv58 | role, skills, model at launch (round 3, the last) | built; round 3 due | — | 3, 4 | F · 1 run + review 3 | F ◆R |
| 2 | W2-60b · ecac | one record per session; launchable roles read from role files | open | W2-60a (launcher file); the roles spec | 3, 4 | S · 9.2 h | W·RS ◆R |
| 3 | W2-11 · k7hz | briefs and skills: twelve fields, the test-proportion rule; W2-79's KPI (brief gaps stay fixed) | open | **W2-10 dropped** (§6); the roles spec | 1, 2, 4 | S · 9.2 h + CIT-P | W·RS ◆R |
| 4 | W2-33 · lrre | **re-scoped (Q6):** the three layers' roles, well scoped: the CTO, the Senior Engineer, the ticket lead's role file, machine-readable defaults per role, the typed handoff. **Outline only: the roles spec defines it** | open | **W2-21 dropped** (§6); the roles spec | 1–3 | S · 9.2 h + CIT-P | W·RS ◆R |
| 5 | W2-83a · dy7j | the kernel's playbook form | open | W2-64; the roles spec | 6 | S · 9.2 h + CIT-P | W·RS |
| 6 | W2-83b · mc6n | **re-scoped:** one playbook per stream (the Senior Engineer's brief) | open | W2-83a; the roles spec | — | S · 9.2 h | W·RS |
| 7 | (to name in the roles spec) | **the CTO's watchers (Q13b):** each Senior Engineer's state (working, idle, waiting for a decision), so none sits idle unnoticed; the CTO acts or escalates | — | the roles spec | — | est. | W·RS ◆R |
| 8 | (to file, §2.2 row 17) | a coordination ticket per stream (Q13) | — | the roles spec | — | L each | W·RS ◆R |

**The roles foundation has landed when:**
- W2-60a, W2-60b, W2-11 and W2-33 (re-scoped) have closed;
- the three layers' foundations are built: the CTO's and the Senior Engineers' roles, skills and briefs; the coordination tickets; the CTO's watchers;
- their **one combined CIT-P** (Q7: quality first, no extra work for its own sake) is approved.

Then comes ACT 2. Est. 11-03 as sent. The roles spec's owner turn moves this later; it is re-estimated weekly.

### 2.5 S3 — sandbox and launch (K6)

| # | W2 · tk | What | Now | Deps | ∥ | P · est | Go |
|---|---|---|---|---|---|---|---|
| 1 | W2-20 · r30l | resource gate (run 3) **on the owner's measured rule for this machine, DEC-950 (Q12)**; machine-agnostic in Wave 3 (a parking row) | built, held | — | S1, S2 | S · 1 run | F |
| 2 | W2-56 · wnnz | `gov launch` for every worker | claimed, no commits | W2-50, W2-05; launcher after W2-60b | W2-20 | F · 13.6 h | W |
| 3 | W2-21 · 1ahb | `gov launch lead`, the ticket-lead role | open | W2-20, W2-56 | W2-82 | F · 13.6 h | W |
| 4 | W2-82 · 4k3l | Definition of Ready at claim and launch | open | W2-60a, W2-56 | W2-21 | S · 9.2 h | W |
| 5 | W2-40 · 6ox0 | EXP-002 sandbox cases (CAP-61.f) | open | W2-21 | S4 | F · est. 7 h (60 LOC) | W |

### 2.6 S4 — adoption and the proving ground ★

| # | W2 · tk | What | Now | Deps | ∥ | P · est | Go |
|---|---|---|---|---|---|---|---|
| 1 | W2-26 · 2ds6 | EXAMIN profile | merged | — | all | S · close | A |
| 2 | W2-52 · siiz | lite A7/A10 stage records | built, held | W2-49 | 3 | F · 1 run | F |
| 3 | W2-81 · l78m | proving ground; **+ `gov close` proof KPI on W2-16's pinned release** (§6, Q8c); its synthetic repositories are also W2-88's proof | claimed, no commits | — | S1–S3 | F · est. 26–30 h | W ★ |
| 4 | W2-23 · kmcr | adoption safety | open | **W2-16** (was W2-18, §6) | 3 | F · 13.6 h | W |
| 5 | W2-27 · h4rh | EXAMIN copy adoption: **installs W2-16's numbered, frozen release (Q8c)**; W2-88's live trial | open | **K9's entry criteria (Q1)**: memory proven (W2-32), the roles landed (W2-60a, W2-60b, W2-11, W2-33), the proving ground passed (W2-81), W2-82, W2-83a, W2-56; plus W2-26, W2-52, W2-21, W2-16, W2-88 (deps cut, §6) | — | F · est. 1–2 d | W ★ |
| 6 | W2-28 · csj8 | copy verdict | open | W2-27 | W2-15b | F · est. 3–6 h | W |
| 7 | W2-29 · b926 | EXAMIN real repository | open | W2-28, W2-25, W2-15b, W2-16, owner's go | — | F · est. 1–2 d | W |
| 8 | W2-30 · 60rw | real-repository verdict | open | W2-29 | — | F · est. 3–6 h | W |

W2-26's finding 2 is a risk for W2-81 and W2-27: `gov rebuild` reports ok on an unadopted clone with no index (`docs/research/EXP-003/examin/README.md`). **W2-88 takes it** (its KPI: a store not built is never ok).

### 2.7 The calendar (estimates only, DEC-954 Q1)

The dates are estimates, re-estimated weekly. EXAMIN's copy starts when K9's entry criteria are met, never because a date arrived. The table is the calendar as sent (10-30), with the DEC-954 steps marked. Its dates have not been recomputed.

| Date | What |
|---|---|
| 10-30 | Plan sent and approved (DEC-954). Items 3–5 start. The 5 closes. W2-86's line. W2-87's lead. W2-61 merged. W2-85 claimed |
| 10-31 | **ACT 1 at milestone 2** (the five-rule guard). Then the 10 built tickets, and the streams: W2-55, W2-04, W2-60a r3, W2-81, W2-20 r3, W2-84's resume, W2-67's rounds after the quick wins. **The roles spec to the owner.** W2-88 filed |
| 11-01 | W2-87, W2-55 and W2-60a close. W2-05 run 4 |
| 11-02 | W2-04 closes, so ◆M's foundation has landed; re-measure. After the roles spec's approval: W2-60b, W2-11, W2-33, W2-83a/b and the foundations |
| 11-03 | ◆R has landed: **milestone 3** (memory landed for this repository and any adopted one, and the roles landed) |
| 11-04 | **ACT 2**, one re-pin. Then the three layers start: the CTO and a Senior Engineer per stream, in fresh sessions |
| 11-05 | W2-15a. W2-21 and W2-82. W2-81 built; its run |
| 11-06/07 | W2-32 round 1 (and 2). Memory ≥ 85 %? Proving-ground fixes |
| 11-08/11 | Entry checks (K9, DEC-941 item 7). W2-88 closed. W2-16's release cut. W2-27 prepared |
| **11-12 (est.)** | **EXAMIN's copy starts, only if K9's entry criteria are met** |
| 11-13–11-20 | W2-27, W2-28, W2-15b, W2-24, W2-25 |
| est. 11-24 (11-20 to 12-04) | W2-29 and W2-30 (the owner's go), W2-46, W2-47 |

### 2.8 Closes of built and merged tickets under the 10 practices

The practices (audit §5):
1. tests first, by an independent designer;
2. scoped tests on the merged commit, in a clean worktree;
3. independent review for FULL;
4. the nightly;
5. the guard's rules: four, and five from ACT 1 (DEC-954: reviewers and auditors write only their own records);
6. gitleaks;
7. git discipline;
8. the disk floor;
9. a close record;
10. a quick record check.

Practices 4 to 8 and 10 hold for every ticket. The table gives what each ticket still needs.

| Ticket | Needs |
|---|---|
| W2-71 F | P2 on the merged commit (full if the tool selects core); P3: its review on record; P9. Its premise test was repaired and merged (P1-MORNING-2026-10-30) |
| W2-77 F | P2; P3 on record; P9 |
| W2-57 F | P2 (its #23 refusal was W2-71's test, since repaired); P3: re-probe run 4 on record; P9 |
| W2-03 S | P2 (all tests passed on 10-30: 16,887 and 104; re-run scoped if the head moved); P9. The containment refusal is lifted |
| W2-26 S (research) | Evidence class: `docs/research/EXP-003/examin/`; P9 |
| W2-61 S | merge; P2; P9 |
| W2-84 F | the serial phase; P2 full (guard, judge core); P3; P9 |
| W2-67 F | r1: P2, P9. The rest: one resume, P3 (rev-4 brief). Staleness is lifted. Park if it grows past one run (DEC-941 item 2) |
| W2-51 S | the serial phase only (CHECKPOINT); P2; P9 |
| W2-49 S | after W2-51; the owner's CIT-P on v4.2's text; P9 |
| W2-37 F | merge-back; P2; P3 (DEC-812's fixes are in); P9 |
| W2-16 F | merge-back; P2; P3; P9; the owner tags the release (needed for W2-29) |
| W2-20 S | run 3 (DEC-950); P2; P9 |
| W2-52 F | merge-back; P2; P3; P9 |
| W2-05 F | P1: W1-02's revision by the test designer (DEC-951 item 2); run 4; P3; P2; P9 |
| W2-60a F | round 3 (last, DEC-951 item 4); review 3; P2; P9 |
| W2-64, W2-76 S | the run in flight; P2 scoped (the item 4c proof uses these worktrees); P9. W2-64 under P-W2-64-1 (a): a fresh test designer corrects the 203 fixtures, verified by a scoped run of the corrected tests only (DEC-954) |
| W2-78 S | parked (DEC-954 Q5); no close |

The 10 built tickets (F) are finished **after ACT 1**, under the five-rule guard (DEC-954 Q2). **The test lock:** closes take it ahead of any lead's full run (DEC-954).

---

## 3. Deferred to Wave 3 (item 10b): 19 tickets (approved, DEC-954)

The 19 deferrals are approved. W2-78 is also moved out of Wave 2: it is parked, not deferred (P-W2-78-PARK (a), DEC-954 Q5). Its branch `w2/W2-78` is kept unmerged for Wave 3's hardening.

| W2 · tk | P | Why |
|---|---|---|
| W2-09 · a3m2 | F | The guard keeps only four rules (DEC-953 item 2). DEC-946 already held it |
| W2-10 · cuao | F | Deferred in REPLAN §2.2. The guard is down to four rules |
| W2-12 · j8gn | F | K5, `gov approve` (DEC-941 item 3) |
| W2-14 · 7y6v | F | REPLAN §2.2. The governance share is measured on W2-81 and EXAMIN instead (W2-60b's records) |
| W2-17 · sdhj | F | The rest of K7 (DEC-941 item 3). CAP-45.a needs a CIT-P note (§6) |
| W2-18 · 057v | S | The rest of K7 (DEC-941 item 3). The real repository uses W2-16's release |
| W2-19 · jzvg | F | EXAMIN's tests are pytest (W2-26's README, finding 1), so DEC-727's condition is not met |
| W2-22 · xm6l | S | K8 (DEC-941 item 3) |
| W2-31 · wbdh | F | CAP-04 moved to Wave 3 (DEC-841); REPLAN §2.2 |
| W2-34 · yadm | S | CAP-30.c moved to Wave 3 (DEC-841) |
| W2-35 · 2keg | S | CAP-30.g moved to Wave 3 (DEC-841) |
| W2-36 · w19l | S | CAP-32.d moved to Wave 3 (DEC-841) |
| W2-38 · g23i | F | CAP-53.b moved to Wave 3 (DEC-841); W2-66 covers selection |
| W2-39 · wudw | S | CAP-37.e moved to Wave 3 (DEC-841) |
| W2-41 · s694 | F | `gov close` is not a gate here. Its high rows go to Wave 3's hardening; W2-81's proof shows whether any of them bites |
| W2-42 · fau3 | F | The guard is down to four rules; write scope is lifted (item 2). Moved out of REPLAN block D |
| W2-43 · u5g6 | S | K8 (DEC-941). The nightly is the integration check (DEC-952 1b; DEC-953 item 3) |
| W2-44 · zndm | F | Trailers are lifted as a gate (audit §4.3) |
| W2-45 · neam | S | K8 (DEC-941). W2-26 found no trigger (indexing about 30 % of the envelope) |

W2-33's other parts (the UX role, the test-execution role) become Wave 3 rows, unless the roles spec places them.

Also to Wave 3's parking list: W2-20 made machine-agnostic (DEC-954 Q12). On any machine, the Gov OS reads its resources (CPU, memory, disk, GPU) and plans the execution to that capacity.

---

## 4. No longer needed now the gates are lifted (item 10c)

### 4.1 The 18 machinery tickets (audit §3.1)

| W2 | State | What happens to the built work | Product for W2-81 or EXAMIN? |
|---|---|---|---|
| W2-53 | closed | stays built | yes: a `gov close` gate, back when `gov close` runs there |
| W2-54 | closed | stays | yes: the context packet (W2-04 builds on it) |
| W2-57 | merged | close as built (item 5) | yes: routes slow and live tests to the nightly |
| W2-59 | closed | stays | yes: the pinned judge in releases |
| W2-63 | closed | stays | no |
| W2-66 | closed | stays | **yes: scoped selection (item 4d)** |
| W2-67 | r1 merged | close r1 as built; one resume or park the branch | yes: test hygiene |
| W2-68 | closed | stays | **yes: batched closes, measured on W2-81** |
| W2-69 | closed | stays | yes: the secrets check |
| W2-70 | closed | stays | no |
| W2-71 | merged | close as built (item 5) | yes: the secrets check |
| W2-72 | closed | stays | yes: the containment gate (lifted here) |
| W2-73, 74, 75 | closed | stay (test fixes) | no |
| W2-76 | lead running | finish; close as built (DEC-954 Q5) | yes: rebuild timings and watchdog (memory needs rebuilds) |
| W2-77 | merged | close as built (item 5) | yes: the nightly |
| W2-78 | lead returned (81 reds in earlier suites) | **parked, not merged** (P-W2-78-PARK (a), DEC-954 Q5): branch kept for Wave 3; its discoveries filed as Wave 2 list rows | later: scoped selection in adopted repositories |

W2-58 (Policy 2, the guard) is closed and stays. It is consistent with the four rules.

### 4.2 Withdrawn

| W2 · tk | Fate |
|---|---|
| W2-80 · 03dg | Withdraw (unbuilt). Queue gates (a) to (h) are lifted |
| W2-79 · av72 | Withdraw (unbuilt). The brief builder will change with W2-11 and W2-60a. Its KPI (brief gaps stay fixed) goes to W2-11 |

### 4.3 Repair tickets (not W2 ids): close each once the nightly shows the named test green

| tk | From | Fate |
|---|---|---|
| 2d6f | W2-03 containment | not needed: containment is lifted |
| sg6x | W2-71's premise test | done: repaired and merged (P1-MORNING-10-30) |
| cv6c | W2-57 on W2-71's test | duplicate of sg6x |
| pr0y | W2-58 green-here fixture | done by W2-75 |
| 2upp | W2-70, W1-01 settings | done by W2-74 |
| s1wp | W2-66 live test map | not needed: ACT-TESTMAP-1 dropped (item 4a) |

### 4.4 Other items dropped
- ACT-TESTMAP-1 (item 4a).
- ACT-W2-57-LS-2: the ratchet lists are lifted.
- ACT-REPIN-3 for closes. In its place (DEC-954 Q8):
  - a numbered, frozen release is cut through W2-16 for W2-81 and EXAMIN's copy;
  - ACT 2 is one re-pin, once memory, the roles and the three layers' foundations have landed.

---

## 5. The three-layer orchestration study (item 8)

**DEC-954 (Q13) names the layers:**
- the master is the **CTO**;
- each sub-orchestrator is a **Senior Engineer** for its stream, with the skills its stream needs;
- agents keep their role names.

Any role not yet defined is scoped and drafted in its ticket. The roles spec defines each role before it is built. This study is the sketch, and it is not built on as it stands. Below, "master" reads CTO and "sub-orchestrator" reads Senior Engineer.

### 5.1 Structure
- **The master** (today's orchestrator) keeps:
  - the WBS and the dependency graph (`.tickets` deps);
  - starting tickets by their dependencies;
  - integration and merges into `w2/integrate`;
  - closes under the 10 practices;
  - the nightly and its red investigations (item 3);
  - the register: only the master and the owner record decisions (W3-P09);
  - the owner's packages and pings (item 9).
- **Each sub-orchestrator** runs its stream's tickets:
  - claims, briefs, leads, merge-backs into its stream's branches, reviews;
  - "ready to close" sent to the master;
  - proposed decisions sent up.
- **Leads and workers** work as today.

### 5.2 Streams for the rest of Wave 2
- **Memory (S1):** §2.3. W2-13, W2-15a, W2-32 and W2-15b in series. W2-06 and W2-08 alongside.
- **Agents (S2 + S3, one sub-orchestrator):** roles and briefs (W2-83a, W2-83b), then the sandbox (W2-56 → W2-21 ∥ W2-82 → W2-40). Merged because both use `src/gov/launch/` in turn (REPLAN §2.1) and S2 thins out after its foundation.
- **Adoption (S4):** W2-52, W2-81, W2-23, then W2-27 to W2-30.
- **Master (S0):** closes, held work, W2-24, W2-25, W2-46, W2-47.

**Must wait:**
- **The three layers' start** waits for both foundations and ACT 2 (DEC-954 Q8b), in new sessions.
- **W2-27** waits for K9's criteria (Q1): memory at 85 %, the roles landed, W2-81 passed, W2-82, W2-83a and W2-56. It also waits for W2-88 and W2-16's release.
- **W2-29** waits for W2-16's release and the owner's go.
- **W2-88** sits in S1 (memory). Its proofs use S4's proving ground, and its files sit beside S4's W2-52 and W2-23 in `src/gov/adopt/`.

### 5.3 How many sub-orchestrators the machine carries
- **The machine:** nproc 20; MemTotal 24,607,384 kB (23.5 GiB).
- **The memory pool**, by DEC-947's method (`gate-config.json`):
  - 21.1 GiB (available plus what leads hold, measured 10-29 20:47);
  - − 3.0 GiB floor;
  - − 7.06 GiB, one verification run's peak;
  - **= 11.0 GiB.**
- **At 2.04 GiB per session** (`working_kb` 2,140,236), that is **5 sessions** by the rule.
- **Measured** (`lead-mem.jsonl`, 1,292 samples, 10-29 17:02 to 10-30 16:11):
  - up to **7 leads at once**, mean 4.52;
  - lowest MemAvailable 5.02 GiB (5,265,152 kB), above the 2 GiB trip-wire;
  - no out-of-memory kill (`oom-watch.txt`).
- **Per-lead samples:** p50 0.29 GiB, p75 0.66, p90 2.77, p95 3.97. The maximum, 8.87 GiB, was W2-03's full run.
- **A sub-orchestrator runs no tests.** Its size is unmeasured; est. 0.3–0.7 GiB (lead p50 to p75).
  - 3 sub-orchestrators × 0.7 GiB = 2.1 GiB. The other 8.9 GiB holds 4 leads at 2.04 GiB, so 7 sessions, the measured safe figure.
  - With 4 sub-orchestrators, 2.8 + 4 × 2.04 = 11.0 GiB. That leaves no room, and it is 8 sessions, above anything measured.
- **CPU:** the load comes from test runs (50.5 at 16:09 today with 3 leads, one testing). Full runs stay one at a time (one lock); a session's own load is light.
- **Recommendation as sent:**
  - **3 sub-orchestrators plus up to 4 leads**, the master in addition (it is already in the baseline);
  - measure the sub-orchestrators on day 1 (tag them in `lead_mem.py`);
  - split Agents into S2 and S3 only if each sub-orchestrator is under 0.7 GiB and MemAvailable stays above 5 GiB.
- **The owner's answer (DEC-954 Q10):**
  1. First the related tickets finish: scoped tests, W2-76 and W2-06.
  2. Then the machine's use is measured by kind: Claude sessions, test runs, rebuilds, gitleaks, git, the code graph and Ollama.
  3. The owner decides the number of Senior Engineers from that measurement.

### 5.4 Each role's brief and skills

| Role | Role file | Skills | Brief |
|---|---|---|---|
| Master | `roles/orchestrator.md` (62 lines), split in two by W2-33 | orchestration, planning, checkpoint, change, retrieval | `prompts/w2-orchestrator.md` (80,599 B), cut to master duties + decisions-in-force (item 7) |
| Sub-orchestrator | new (W2-33) | orchestration (stream part), checkpoint, retrieval, test-design | `briefs/SUB-common.md` (new) + stream playbook (W2-83b) + its WBS slice |
| Ticket lead | new (W2-21's ticket-lead role, via W2-33) | orchestration (lead part), checkpoint, retrieval | `briefs/LEAD-w2-common.md` (169 lines), moving into the kernel template (W2-11) |
| Test designer | `independent-test-designer.md` | test-design (proportion rule, red first, mutation: W2-11) | from W2-11's template |
| Implementer | `engineer.md` | superpowers (TDD, debugging), retrieval | lead's worker brief |
| Reviewer | `independent-auditor.md` (+ a reviewer role, W2-33) | audit | `AUDITOR-common.md`, `JUDGEMENT.md` |
| Product-spec / research | `product-spec.md`, `research.md` | planning, change / discovery | worker brief |

- Paths: `template/governance/kernel/roles/`, `.../skills/`, `governance/project/briefs/`.
- Every role loads its skills and model at launch (W2-60a), and is launchable from its file (W2-60b).
- **DEC-954:** this table is the starting point for the roles spec, which replaces it once approved. The company map's known gaps are:
  - no role file for the ticket lead;
  - no machine-readable defaults per role;
  - nothing yet for the CTO and the Senior Engineers beyond this sketch.

### 5.5 Handovers
- **Night:** the nightly runs 02:00–05:00. The master investigates any red (item 3).
- **Morning:**
  - by 07:00 each sub-orchestrator writes its stream checkpoint (checkpoint skill) and stops. The checkpoint holds the leads running, the returns pending, the next 3 tickets and its asks to the master.
  - The master sends the 07:30 package (DEC-938, DEC-949, DEC-951 B), writes its handover and stops.
  - The owner starts a fresh master. It reads the decisions-in-force list, its checkpoint and the stream checkpoints.
  - The master starts fresh sub-orchestrators, each with its stream brief and checkpoint.
- **Leads continue through the handover:** they run detached (`lead_chain2.sh`). Returns land in `log/<W2>-A5-*.json`, and each stream's watcher picks up its own.
- **Up** to the master: a typed handoff record (W2-33) at each lead return, plus "ready to close".
- **Down** to the streams: tickets released by dependency, decisions, and close results.
- **The CTO's watchers (DEC-954 Q13b):** they track every Senior Engineer's state (working, idle, waiting for a decision), so none sits idle unnoticed. The CTO acts or escalates to the owner. They are built in S2 before ACT 2.

### 5.6 Wave 3
Streams:
- (a) the EXAMIN pilot beyond the copy, and W3-P09's measured trial;
- (b) hardening: the guard and the close (W2-09, 10, 41, 42, 44), and the lifted gates turned back on once the Gov OS is whole;
- (c) release and update (W2-17, 18, 19; the container and RunPod row);
- (d) breadth (W2-12, 14, 22, 31, 34–36, 38, 39, 43, 45).

Three at once (§5.3); the fourth is queued.

---

## 6. Changed exit criteria and WBS edits (approved, DEC-954; applied to `docs/plan/WAVE_2_WBS.md` revision 4)

DEC-954 adds these, applied with the rest:
- the new row W2-88 (Q9f);
- W2-27 gains W2-16's release (Q8c) and W2-88 (its live trial);
- K9 is gated by its criteria, not a date (Q1);
- W2-61h is re-scoped to the enlarged set (Q9a);
- W2-32 gains the escalation after two rounds (Q9e);
- W2-78 is parked (Q5).

**Exit criteria (§5)**
1. **Criterion 1 becomes:** "Every Wave 2 ticket closes on the 10 practices, with its close record. A clean `gov close` is shown on the proving ground (W2-81) and on EXAMIN's copy (W2-27)."
2. **Criterion 3:** `gov check` runs on the nightly. `gov doctor` is green on EXAMIN's copy (W2-27's KPI). W2-22's rows go to Wave 3.
3. **Criterion 5:** the AR lines whose tickets moved are named as Wave 3 in W2-24's report.
4. **Criterion 6:** EXAMIN runs W2-16's release. W2-18 is deferred.
5. **Criterion 7:** CAP-45.a (W2-17) moves to Wave 3 by a CIT-P note, or is a named exception.
6. **Criterion 8:** the governance share is measured on W2-81 and EXAMIN (W2-60b). W2-14 is deferred.

**§0 rules**
- Rule 1 is replaced by criterion 1 above.
- Lifted: rule 3 (a rebuild before each close); rule 11's second bullet and rule 16 (ratchet entries as owner commits); rule 19 (closes first, quiet windows).
- Rule 9 is replaced by the gate in `gate-config.json`, then W2-20.

**§1 table and cards**
- New rows: W2-86 and W2-87.
- W2-11: drop the dependency on W2-10.
- W2-33: re-scoped to the three-layer roles and the typed handoff; drop the dependency on W2-21.
- W2-23: depends on W2-16, not W2-18.
- W2-27: dependencies are K9's copy criteria plus W2-26, W2-52, W2-56 and W2-21 (W2-08, 09, 10, 18, 19, 45 removed).
- W2-24 and W2-46: dependencies are the Wave 2 tickets only.
- W2-81: a new KPI, a ticket in each synthetic repository closes with `gov close` at exit 0 on a pinned release.
- W2-83b: re-scoped to the stream playbooks.
- W2-79 and W2-80: withdrawn.
- The 19 tickets in §3 are marked Wave 3 (DEC-953).

**§3 and §4:** the layers table becomes §2.1's streams. The estimates become §2.0 and §2.7.

**K9:** add W2-81's `gov close` proof to the copy's criteria. DEC-954 also adds:
- EXAMIN's copy starts only when K9's criteria are met, never by a date (Q1);
- W2-88 closed (memory for any repository);
- W2-16's release installed (Q8c).

---

## 7. The owner's questions, answered (DEC-954)

| # | Question | Recommendation | **The owner's answer (DEC-954)** |
|---|---|---|---|
| Q1 | Target 11-12 (range 11-09 to 11-20)? | Yes, re-estimated weekly (DEC-941) | **Answered: no date gate.** EXAMIN's copy starts only when K9's entry criteria are met (memory proven; the roles, skills and briefs landed; the proving ground passed; the rest of the minimum closed). The dates are estimates, re-estimated weekly. No adoption on a weak Gov OS because a date arrived |
| Q2 | Do resumes of built work (F, 10 tickets) go ahead before approval? | Yes: item 5 and DEC-946 item 1 | **Answered: after ACT 1, not before.** Once the five-rule guard is on, each is finished and closed on the 10 practices |
| Q3 | Does W2-85 go ahead under item 4? | Yes: it keeps scoped runs free of load reds | **Answered: yes** |
| Q4 | The register-as-one-record defect: inside W2-87 (its KPI 4) or a separate ticket? | Inside W2-87, which W2-55 reuses | **Answered: yes, inside W2-87** |
| Q5 | W2-78 and W2-76: finish and close as built? | Yes: both are product features | **Answered:** W2-76 finishes and closes. W2-78 is parked (P-W2-78-PARK (a)), with its discoveries filed as rows |
| Q6 | W2-33 re-scoped to the roles the three layers need, or a new ticket? | Re-scope W2-33 (it is CAP-22.b/c) | **Answered: re-scope W2-33, and scope it well for the three layers** (Q13 and the roles spec) |
| Q7 | One CIT-P for the four K3 tickets? | Yes: one owner turn | **Answered: yes, one combined CIT-P.** Quality first; no extra work for its own sake |
| Q8 | ACT-REPIN-3 dropped; a release via W2-16 for W2-81 and EXAMIN? | Yes | **Answered: two acts, no re-pins for gates.** (a) ACT 1 at milestone 2: the five-rule guard; then the 10 built tickets and the streams in parallel. (b) ACT 2: one re-pin once memory, the roles with their skills and briefs, and the three layers' foundations have landed; the roles are built on an approved spec, so the roles spec comes first. (c) A release through W2-16: numbered and frozen, installed by W2-81 and EXAMIN's copy |
| Q9 | Q-2, EXP-003's metric, before W2-15a | Approve W2-61's 20-question measure; package now | **Answered: approved as memory's measure, amended.** (a) The set is enlarged to about double, up to 50, with visible and hidden halves; the size and time cost are proposed in `drafts/plan-dec954/MEMORY-SPEC-MAP.md` part B. (b) The hidden half is protected from every worktree (W2-84's fix) in the new guard hook before use. (c) Memory is judged on the combined memory spec and measured along the way. (d) The spec is mapped to the tickets, in the same file, part A. (e) Below 85 % after two rounds: escalate; the owner decides at the third. (f) Memory for any repository: W2-88, in Wave 2's minimum |
| Q10 | 3 sub-orchestrators, a 4th once measured? | Yes (§5.3) | **Answered: measure first.** After scoped tests, W2-76 and W2-06 finish, the machine's use is measured by kind (Claude sessions, test runs, rebuilds, gitleaks, git, the code graph, Ollama), and the owner decides from that |
| Q11 | W2-67's rest: one resume, or park? | One scoped resume in spare capacity; park if it grows | **Answered: its remaining rounds go soon after memory's quick wins,** for speed |
| Q12 | W2-20's run 3 as DEC-950 decided, or the audit's fixed cap? | DEC-950, a product feature that the three layers' capacity needs | **Answered:** in Wave 2, on the owner's measured rule for this machine (DEC-950). In Wave 3, machine-agnostic: the Gov OS reads any machine's resources (CPU, memory, disk, GPU) and plans the execution to that capacity |
| Q13 | A coordination ticket per stream (as W2-00) for the guard's identity? | Yes, filed at the three-layer start | **Answered: yes.** (a) The master is the CTO; each sub-orchestrator is a Senior Engineer for its stream, with its stream's skills; agents keep their role names; any undefined role is scoped and drafted in its ticket. (b) The CTO's watchers track every Senior Engineer's state (working, idle, waiting for a decision); the CTO acts or escalates |

**Also decided by DEC-954:**
- **The roles spec before building.** It covers what exists, every role and its brief, and the gaps with the ticket filling each. It goes to the owner before W2-60b, W2-11, W2-33 and W2-83 build further.
- **P-W2-64-1 (a).**
- **The test lock:** closes take it ahead of any lead's full run.
- **The guard's fifth rule:** independent reviewers and auditors write only their own review and audit records. It is tested with planted cases and switched on in ACT 1.
- **§6's edits and the 19 deferrals:** approved.
- **Milestone pings:** milestones 2 and 3 are pinged; ACT 1 comes with milestone 2.

**Sources:**
- DEC-953's and DEC-954's texts; AUDIT-GOV-FEATURES-1; REPLAN-W2; DEC-841, DEC-941 to DEC-951; P-W2-78-PARK; P-W2-64-1;
- `.tickets/`; `log/W2-*-A5-*.json`; `log/lead-mem.jsonl`; `tools/gate-config.json`; `report-state.json`;
- CHECKPOINT; `after-queue-2026-10-30.md`; W2-26's README; W2-87's draft.

**Unmeasured (estimates):**
- a sub-orchestrator's memory;
- W2-81's effort;
- 16 working lead-hours a day per chain;
- W2-27 to W2-30 and the auditors' times;
- the number of proving-ground fixes;
- whether memory can reach 85 %;
- the owner's turnaround on CIT-Ps (an upper bound from commit times);
- W2-88's effort and its real runs' time on the large repositories (scaled from LOC, unmeasured);
- the roles spec's owner turn, and the time from ACT 1 to ACT 2.

END OF PLAN
