# INVESTIGATION-1, part D: the WBS and the tickets (DEC-1047 item 2 (d); feeds DEC-1039 step 3b)

Investigator D, read-only, 2026-11-02. Sources: `.tickets/*.md` (parsed with `/tmp/gov-os-inv-D/tickets.py` and `kpis.py`), `docs/plan/WAVE_2_WBS.md` (rev. 4), `PLAN-W2-DEC953.md`, `LIFTED-BY-DEC953.md`, `git` on `w2/integrate` and the ticket branches, the lead logs `log/*.json` (`/tmp/gov-os-inv-D/costs.txt`), the dispatcher's lists, the register.

**Headline**
1. Of 137 tickets tagged `wave-2` (W1-01b included), 45 are closed and 92 are live. **20 of the 92 are already Wave 3 or parked** but still count as Wave 2. That leaves 72 real ones, carrying **716 KPI lines** between them.
2. **44 % of Wave 2's measured lead spend went on tickets that build gates, checks, records, Contract paperwork or test revisions for them: $512 of $1,161 (1.40 of 3.15 billion tokens, 31 of 66 tickets with logs).** Memory got $278, roles $214, traffic $117 and skills $42. The split is my estimate (method under D-3).
3. **Proposed fate for the 92 live tickets:**
   - Keep: 22.
   - Re-scope: 21.
   - Merge into another ticket: 11.
   - Close formally, done in substance: 6 (W2-05, W2-96, W2-112, W2-122, W2-123, W2-126).
   - Retire: 19.
   - Wave 3 and out of the count: 13.

   About 146 KPI lines are lifted and about 88 move to Wave 3 (estimate). That leaves about 480 lines in Wave 2.
4. **Three gaps in the plan itself:**
   - EXAMIN's copy (W2-27) waits on 34 open tickets. They include p3 domain skills, Contract v4.3 and the pre-commit tier.
   - W2-27 does not depend on the smart close, although its own exit-criterion proof needs one.
   - W2-121, an entry criterion for the copy, sits transitively *after* the copy (W2-121 → W2-118 → W2-27).
5. **The growth comes from a mechanism, not from scope.** DEC-1003 maps every CTO practice into a product KPI the same day:
   - W2-20 grew from 4 to 24 lines, W2-11 from 6 to 19, W2-27 from 6 to 15 and W2-121 from 9 to 18.
   - 65 tickets were filed between 10-29 and 11-02, 13 of them test revisions.

   DEC-1010 alone is restated in five tickets.

## Part 1. Structural items

| id | what | where (paths, tickets, decisions) | cost (machine / tokens / owner; source) | what it protects | DEC-1010 test: in aim? ordinary work? fails open or loses work? | recommendation | what lifting takes (code, tests, tickets, config) | depends on |
|---|---|---|---|---|---|---|---|---|
| D-1 | 20 Wave-3 or parked tickets still open under the `wave-2` tag. They inflate the count of 136 (W2-09, 10, 12, 14, 17, 18, 19, 22, 31, 34–36, 38, 39, 41–45, 78) | `.tickets/*` tags `wave-3`/`parked` beside `wave-2`; WBS §1 table "Wave 3 (DEC-953, DEC-954)" | Every status count, countdown and progress line reads 92 live instead of 72. W2-46's deps list 89 tickets (owner's reading time; WBS §6 countdown rule) | Nothing | Not in the aim; a counting error | **Move out of Wave 2**: retire 10 of them, keep 10 in Wave 3 (Part 2) | Re-tag them (`wave-3` only) or close with a reason; drop them from W2-46/W2-27 deps; WBS §1 row note | — |
| D-2 | KPI-line growth by standing mapping. DEC-1003 maps every CTO practice into a product KPI the same day; DEC-982 item 2 says the smart way of working is the product's | DEC-982 item 2, DEC-1003, SMART-WORK-1..5. Growth by `git log` of the ticket file: W2-20 (`DAEO-r30l`) 4→24 in 13 commits; W2-11 6→19 in 12; W2-27 6→15 in 7; W2-121 9→18; W2-115 13→19 | Each mapping is a package, a register entry, a ticket edit and a widened review. W2-20 is mentioned in 47 register lines and W2-11 in 37 (`grep`). Filing: 54 tickets on 10-16, 65 between 10-29 and 11-02 | That the product gets what the CTO learned | In the aim only where the practice itself passes the DEC-1010 test. Otherwise it copies the CTO's ceremonies into the product | **Change DEC-1003 (owner):** a practice enters a product ticket only if it passes the DEC-1010 test, mapped once a week as one batch, not the same day | One register entry; prompt §0 and DECISIONS-IN-FORCE line (part C's tools) | Part C (which CTO practices stay) |
| D-3 | Spend on gate, check, record, Contract and test-revision tickets | 31 tickets: W2-01, 02, 05, 37, 48, 49, 51–54, 57, 59, 62–64, 67, 69–75, 77, 78, 85, 90, 90b, 95, 107, 114. 13 test-revision or test-design tickets in all (W2-63, 67, 70, 73–75, 90, 90b, 90c, 111, 114, W1-01b, 66b) | **$512 of $1,161 measured lead cost (44 %); 1.40 of 3.15 billion tokens; 77 of 170 lead runs.** Source: `log/W2-*.json` `total_cost_usd` and `usage` (15 logs unparsed, so these are lower bounds). The grouping is my estimate: each ticket put in one group by its title and KPIs | — | — (history; informs the rest) | **Use as the yardstick for the lift.** No closed ticket reopened | — | Parts B1 and B2 (whether those gates leave the defaults) |
| D-4 | KPI lines that cannot pass as written because they depend on Wave-3 or lifted features | W2-24 S2 (W2-19's TypeScript fixture, Wave 3), S3 (`gov update`, W2-17, Wave 3); W2-27 S1 (W2-18, Wave 3), S8 (W2-19's ratchet baseline; ratchet lifted, DEC-953 B); W2-46 S5 ("gov doctor green **here**", but exit criterion 3 was restated to EXAMIN only, W2-22 Wave 3); W2-47 S3 ("commits through the hook", needs W2-08) | A milestone run that would stop on its own plan; one package each to the owner (estimate: 4 packages) | Nothing | No | **Re-word or retire** (W2-24 retired; W2-27 S8 → reds named in the close record; W2-46 S5 → EXAMIN only; W2-47 S3 dropped) | Ticket-file edits (W2-00's paths) | — |
| D-5 | Dependency errors around EXAMIN's copy | W2-27 (`DAEO-h4rh`) deps = 46, of which 34 open, including W2-100 and W2-101 (p3, "after ACT 2"), W2-102, W2-103, W2-109 (Contract v4.3), W2-06 (pre-commit tier) and W2-83a. **W2-115 is not a dep although W2-27 S14 needs a clean `gov close`.** W2-121 (a K9 criterion, "before EXAMIN's copy") → W2-118 → W2-27: after the copy. W2-117 is tagged `after-examin` but the WBS says "before EXAMIN's copy (DEC-1010 item 5)". K9's criteria (`PLAN-W2-DEC953.md` l.250, 433) are in no ticket's deps | The copy's critical path waits on polish. The cycle-in-spirit would surface as a stall, then a package | Ordering | Within aim 4 (governing the traffic): yes; the errors make it fail | **Re-derive W2-27's deps:** remove 13 (W2-05 and W2-96 to formal close; W2-06, W2-21, W2-99 merged; W2-100 and W2-101 to Wave 3; W2-102, W2-103, W2-109 and W2-83a retired; W2-104 and W2-82 not gating) and add 7 (W2-115, W2-121, W2-112, W2-122, W2-123, W2-126, W2-124). Cut W2-121's dep on W2-118. Resolve W2-117's tag. Encode K9 as deps | Ticket edits, WBS §1 rows, K9 amended by the owner | Owner (K9) |
| D-6 | Duplicate KPI lines across tickets | Same rule in two or more tickets:<br>• W2-118 S5 ≡ W2-121 S13 (word for word)<br>• W2-88 S5 ≈ W2-124 S1 (a store not built is never ok)<br>• W2-20 S12 ≈ W2-123 S2/S5/S7 (embedding servers' CPU cap from the gate config)<br>• W2-21 S3 ≈ W2-60a S8 (launch record); W2-21 S2 ≈ W2-33 S2 (ticket-lead role)<br>• W2-115 S6 ≈ W2-117 S1 (culprit); S7 ≈ W2-117 S2 (close record); S10 ≈ W2-117 S6 (warm clones); S2 ≈ W2-117 S5 (record-only)<br>• W2-116 S4 ≈ W2-117 S4 ≈ W2-122 S4 (integration store as warm base)<br>• W2-15b S4 ≈ W2-88 S6/S11 (scale probe on EXAMIN and ~/workspace)<br>• W2-08 S7 ≈ W2-42a S9/S11 (false refusals)<br>• W2-55 S8 ≈ W2-11 S14 (in-force digest at start)<br>• W2-60b S9 ≈ W2-33 S6 (QA engineer role)<br>• quiet hours in three tickets: W2-11 S17, W2-33 S9, W2-113 S4<br>• brief gaps in three tickets: W2-11 S9/S13, W2-118 S2 | Each duplicate is built, tested and reviewed twice, or contradicts its twin. Estimate: 1–2 lead runs per pair | — | — | **Keep one home per rule** (Part 2 names it) | Ticket edits; DEC-1039 3b's KPI-line map | — |
| D-7 | Process boilerplate written into KPI lines | Of the 716 KPI lines in the 92 live tickets (`/tmp/gov-os-inv-D/kpis.txt`):<br>• 15 "three test scenarios … fresh session"<br>• 15 "generated copies"<br>• 19 licence lines<br>• 19 CIT-P/CIT-E<br>• 26 owner-approval or ACT lines<br>• 12 "both figures together"<br>• 9 "Rewrite-Reason / nothing lowered"<br>• 2 "scoped set green, every red named for the CTO"<br>The skill tickets W2-98–W2-103 each carry the same 4 template lines | Each line needs a test or evidence and a review finding when missed. W2-11 S10 makes three scenarios on a fresh session per skill a rule (tokens per skill: estimate 3 sessions × the skill's size) | That skills are tested and licensed, and that measures report both figures | Licence for imports: yes, cheap. Three scenarios per skill as a gate: not fail-open and not loss: no | **Lift as KPI lines:** a skill's three scenarios become optional (W2-104's tool); "both figures" stays one rule in W2-61's measure, not a KPI line per ticket; CIT-P lines only where the Contract changes | Ticket edits; W2-11's skill template text in the lift pass | Parts B2 (CIT-P rules) and A2-9 |
| D-8 | Stale in-flight branches: in progress by claim, not by work | W2-20: built and held since 10-17, **1,628 commits behind** `w2/integrate`, KPI lines since 4→24. W2-37: held since 10-19, 571 behind, 3,121 lines. W2-56: claimed 10-29, **nothing built**, 842 behind. W2-109: claimed 10-31, nothing built, 460 behind. W2-52: 462 behind. (`git rev-list --count`) | Each resume starts with a large merge and re-verification (W2-20's own checkpoint line: "acceptance conflicts: its test designer"). Estimate: 1 lead run each before any KPI work | — | — | **Status follows work:** W2-56 and W2-109 back to `open` (W2-109 retired); W2-20 rebuilt from the CTO's `heavy_slot.sh` and balancer rather than by merging its 10-17 branch | Ticket status lines; W2-20's brief | — |
| D-9 | Churn before landing | W2-05: 10 merges of `w2/integrate` into its branch before its one landing, **$61.5, the most expensive Wave 2 ticket**. W2-96: 7 sync merges + 6 tests-branch merges, $34.9. W2-04: 6 lead runs, now "r5-repair", 6 owner packages. W2-60a: three review rounds, $35.0. W2-11: 9 owner packages (`P-W2-11-*` in the register) | A long-lived branch pays a merge and re-verification per sync (`git log --merges`) | — | — | **Apply DEC-1010's two-round cap to W2-04 now** (the owner once). Land what is built; no new round for W2-05, W2-96 or W2-55 | Owner decision on W2-04 | Part A2-9 |
| D-10 | DEC-1010 (stays) restated in five product tickets | W2-11b S1 (reviewer verdict block), W2-33 S10 (QA engineer as moderator), W2-115 S11 (READY computed), W2-117 S7 and W2-121 S11 (round count). The CTO's `tools/verdict.py` and `test_verdict.py` already do it | Five tests and five reviews of one rule (estimate) | The moderated review, two rounds, READY by code | Yes: DEC-1010 stays | **One product home:** W2-115 S11 computes READY and counts rounds (W2-117 S7 and W2-121 S11 call it); W2-33 S10 the role; W2-11b S1 the template | Ticket edits | — |
| D-11 | Milestone tickets that repeat each other | W2-24 (Track A gate run) and W2-25 (Track A audit) against W2-46 (exit run), W2-47 (exit audit), W2-81 (proving ground's clean `gov close`, exit criterion 1) and W2-27/W2-28 (the copy and its verdict) | W2-24 has 23 deps and W2-46 has 89. Two gate runs and two independent audits: estimate 2 FULL milestones, about 27 lead-hours (13.6 h each, PLAN-W2-DEC953 §2.0) | Proof that AR-1..AR-10 hold | Partly: one proof is enough | **Retire W2-24 and W2-25**; the AR lines are shown once in W2-46 and audited in W2-47 | Ticket close with reason; W2-46/W2-47 KPI edits; exit criterion 5 re-worded by the owner | Owner (exit criteria) |
| D-12 | Done in substance by the emergency | W2-112 (shared reranker on the GPU; round 2 done; P-W2-112-F9); W2-122 and W2-123 (approved in the queue: `3fc44860`, `3de9bcf4`); W2-126 (finishing). W2-20 S15/S17 (CTO `heavy_slot.sh`, confined gate live 20:37:40, DEC-1043); W2-20 S18 (product: `emg/gitleaks` `6046339b`, `src/gov/secrets` pool by affinity). W2-121 and the Load Balancer (the CTO's `tools/dispatch/dispatcher.py` 3,191 lines + `balancer.py` 347, `emg/lb` `758bc89f`). W2-15b S10 (query embedder on the GPU: DEC-1033, ACT-QUERY-GPU-2, a question 0.04–0.22 s against 13.7 s). W2-05, W2-96 and W2-55 merged (`b4a747f1`, `107514f5`, `e0cb7d13`) | Only the formal close is left: one close record each (DEC-1039 (4)) | — | — | **Formal close; their KPI lines shown as met**; product ports (W2-20, W2-121) re-scoped | `gov close` or the close script; evidence paths in the close record | — |
| D-13 | Plan contradictions | W2-33 S4 builds a typed handoff for CAP-22.b (lite) while W2-109 S1 moves CAP-22.b to Wave 3. W2-11 S13 and W2-118 S2 build `brief_gaps:` in the kernel while W3-P02 parks exactly that. W2-121 S12 (orchestrator heartbeat) builds W3-P16 (parked). W2-46 S5 contradicts exit criterion 3 | Reviews will find these as findings (rounds) | — | — | **Follow the parking list:** W2-33 S4, W2-121 S12 and W2-118 S2 to Wave 3; W2-11 S13 stays only as built text | Ticket edits | — |

## Part 2. Per ticket, open or in flight (92), with its KPI lines' fate

Cost:
- **$** is the measured lead cost summed from `log/<ticket>-*.json`, a lower bound.
- **pk** is the count of owner packages `P-W2-<n>-*` in the register.
- **Est.** marks an estimate from the profile: L 4.3 h, S 9.2 h, F 13.6 h median lead-hours (PLAN-W2-DEC953 §2.0).
- **beh** is how many commits the branch is behind `w2/integrate`.

The DEC-1010 test is written as aim / ordinary / fails open or loses work.

### 2a. In flight (27)

| id | what | where | cost | what it protects | DEC-1010 test | recommendation | what lifting takes | depends on |
|---|---|---|---|---|---|---|---|---|
| D-T01 | W1-01b, W1-01's merge rule reads `acceptance_exemptions` | `DAEO-vhad`, LITE test-revision; a nightly red | Not started (0 ahead) | Rule 1: no implementer change to acceptance tests, over history | Aim 3 yes / yes / no (a red, not a hole) | **Merge into DEC-1039 step 3 (the reds)**: S1, S2 and F1 become the red's fix | Test designer's red fix; ticket closed as absorbed | B1 (if `acceptance_exemptions` is lifted with the ratchet lists, the case's source of exemptions changes) |
| D-T02 | W2-04, `gov context` bounded | `DAEO-u4oz`; 4,386 lines; 6 lead runs (r5); beh 97 | $13.3+, 6 pk | The packet ceiling. A1-4 measured 1.6 M tokens against 6 k | Aim 1 yes / yes / loses work (a context that cannot load) | **Re-scope; the owner once (DEC-1010 cap):**<br>• keep S1, S2, S3 (each decision by its own hash, not the whole register), S5<br>• S6 and S7: met as built, no new round<br>• S4 (packet hash reproducible with or without a live semantic index) to the nightly or lifted with the context-reproducibility family | Ticket edit; owner's call on round 6 | A1-4 (what the packet is used for), B1 (the family) |
| D-T03 | W2-05, the git environment of checks and hooks | `DAEO-0z8c`; landed `b4a747f1` (0 ahead) | $61.5, 2 pk | No inherited `GIT_*` reaching child git (DEC-710: corrupts a worktree) | Aim 4 / yes / loses work | **Formal close** (done in substance); S1–S3 and F1 met by the landing's evidence | One close record | — |
| D-T04 | W2-11, briefs and the orchestration skill (17 lines) | `DAEO-k7hz`; approved to land `c9f99b28b88b`; 4,046 lines | $27.1, 9 pk | Twelve-field returns; the skill template; test-design proportion | Aim 2/3 in part | **Keep: land as built; no new round.** S1–S17 met by the landing. S13 (brief gaps), S14 (anti-drift kit, five places), S15 and S17 (approvals, quiet hours): their texts are trimmed in the lift if part C lifts those practices | Landing; later text edit | C, A1-5 |
| D-T05 | W2-13, ranked lexical route (BM25) | `DAEO-zqvn`; built, waits W2-92's landing | $15.7, 2 pk | Memory quality | Aim 1 | **Keep**; all lines | — | W2-92 landing |
| D-T06 | W2-20, machine-wide resource gate (24 lines) | `DAEO-r30l`; held since 10-17; **beh 1,628** | $6.9, 2 pk; 47 register mentions | Heavy jobs in slots; thread budget; GPU budget | Aim 4 yes / yes (load 54–76, GPU crashes) / loses work | **Re-scope:**<br>• keep S1–S5, S7, S8, S10, S13, S14, S15, S17, F1–F6<br>• S18 met (`6046339b`)<br>• S12 → W2-123<br>• S6 (memory arithmetic), S9 (re-measure into the config), S11 (OOM trip-wire) → the Load Balancer's measured peaks in W2-121 or lifted (DEC-953 D)<br>• S16 → S15's evidence in CPU-seconds (DEC-1041)<br>Rebuild from `heavy_slot.sh` and `balancer.py`, not by merging the 10-17 branch | Ticket edit; new brief | Part C (the LB stays), A2 |
| D-T07 | W2-37, `gov impact` | `DAEO-6n5k`; 3,121 lines held since 10-19; beh 571 | $8.6 | A decision change's impact found (drift) | Aim 1/2: the query yes. The CIT-P automation: no | **Re-scope:**<br>• land S3 (plain-language "impact of X") and S1's listing as that query's answer, without raising a CIT-P<br>• S2 (CIT-E matches the proposal) lifted<br>• S4 if built<br>• absorbs W2-55 S5 as a query, not a failing check | Ticket edit; resume after a merge | B2 (CIT-P ceremony) |
| D-T08 | W2-42a, the product guard's Bash parser | `DAEO-03ub`; 7,891 lines; stopped at a safe point; beh 24 | No log; DEC-1040 and DEC-1043 | **72 of 78 refusals since ACT 1 were false (DEC-1040):** the guard's main cost to honest work | Aim 3 yes / yes / both (false refusals block, misses fail open) | **Keep**; S1–S11 and F1–F2; absorbs W2-08 S7 (rate under 10 %) into S9 | — (resume after the lift) | B2 (the five rules) |
| D-T09 | W2-52, the lite A7 and A10 stage records | `DAEO-siiz`; built, probe pass; beh 462 | $8.7, 1 pk | Independent migration and memory verification at adoption | Aim 1/3 | **Keep: land**; S1–S3 and F1 met | Landing after a merge | B2 (CAP-44.h's "gov check no RED family" condition) |
| D-T10 | W2-55, decisions tagged, superseded left out | `DAEO-arrl`; landed `e0cb7d13`; run 2 (append) pending | $15.2, 2 pk | Superseded decisions not served to agents (drift) | Aim 1 yes: S1, S3, S8. The rest: no | **Re-scope, then close on what landed:**<br>• S1, S3, S6, S8 met<br>• S2 ("lands in" tag, DEC-851's five places) lifted<br>• S4's owner sample review lifted (the orchestrator applies; the owner may spot-check)<br>• S5 → W2-37 (query)<br>• S7 (append mode in the decision tool) lifted | Ticket edit; run 2 cancelled | C (five places, decision tooling) |
| D-T11 | W2-56, `gov launch` for every worker | `DAEO-wnnz`; claimed 10-29, **nothing built**; beh 842 | Est. F 13.6 h | The sandbox holds a worker's scripts to its write list (the guard cannot see inside scripts, W3-P13) | Aim 3 / yes / fails open | **Keep, re-scoped:**<br>• S1 (the code graph in the session's temp folder: A2-8's daemons), S2, S4, S5, S7 (concurrent launches: loses work)<br>• S3 → one stderr line, no CIT-E<br>• S6 (refusing `--plugin-dir` and others: deliberate, ADR-0001) → Wave 3<br>• absorbs W2-21 S5, S6, S7, S8, F1 and W2-127<br>• status back to `open` | Ticket edit | A2-8 |
| D-T12 | W2-60a, the role, skills, model and effort at launch | `DAEO-cv58`; review 3 pass; 4,980 lines; beh 120 | $35.0, 1 pk | The role loaded with its permissions | Aim 3 | **Keep: land**; S1–S9 met; S10 (second review on a different model) built but switchable off | Landing; a config switch if A2-9 lifts S10 | A2-9 |
| D-T13 | W2-61h, 28 new memory questions | `DAEO-h2k3`; approved to land `ac7dfa17` | $10.9 | The measure's hidden half | Aim 1/3 | **Keep: land**; all met | Landing | — |
| D-T14 | W2-66b, W2-66's PowerShell case | `DAEO-zuiy`; 2-line test revision; not started | Est. L | — | No (a red) | **Merge into DEC-1039 step 3** (the reds); S1 and F1 → the red's fix | Red fix | — |
| D-T15 | W2-81, the adoption proving ground | `DAEO-l78m`; approved to land `e78e6af7` | $18.8, 2 pk | Adoption and memory proven on planted repositories | Aim 1/4 | **Keep: land**; S1–S10 and S12 met; S11 (a clean `gov close` per synthetic repository) waits W2-115 | Landing; dep on W2-115 | B1 (close) |
| D-T16 | W2-90b, the live-wiring tests' next round | `DAEO-nqa2`; approved `73c18fea` | $7.1, 1 pk | Tests judge the kernel's wiring | Aim 3 (rules 1 and 4 tests) | **Keep: land**; met | Landing | — |
| D-T17 | W2-91, full embeddings | `DAEO-a3u2`; approved `55b47e07` | $13.5, 1 pk | Memory coverage | Aim 1 | **Keep: land**; met | Landing | — |
| D-T18 | W2-92, graph and code routes in retrieval | `DAEO-n0wb`; approved `448a835a` | $27.2, 2 pk | Memory | Aim 1 | **Keep: land**; met | Landing | — |
| D-T19 | W2-96, `gov accept` (opaque acceptance runner) | `DAEO-ouet`; landed `107514f5` | $34.9, 4 pk | **The builder never reads its own acceptance tests** | Aim 3 core | **Formal close**; S1–S6 and F1–F4 met | Close record | — |
| D-T20 | W2-104, `gov skilleval` | `DAEO-drhj`; 2,029 lines; run 3 pending (its gitleaks reason gone by DEC-1045) | $15.0, 2 pk | Skills tested; imports licensed | Aim 2 / — / no | **Re-scope:**<br>• land as an optional tool: S1, S3, S4 met; S2 (import licence) kept<br>• lift the rule that every skill passes three scenarios before adoption (W2-11 S10; W2-98–W2-103's lines)<br>• not a dep of W2-27 | Landing; rule text in the lift | A2-9 |
| D-T21 | W2-105, the template's install block removed | `DAEO-zpdj`; approved `fa653609` | $9.1 | Rule 4 (installs) in products | Aim 3 | **Keep: land**; met | Landing | — |
| D-T22 | W2-109, Contract v4.3 | `DAEO-6b2q`; claimed 10-31, **nothing built** | Est. S 9.2 h; a CIT-P, an independent review, an owner approval, 276 records rewritten | That the plan validator's contract checks pass | No | **Retire:**<br>• S1 → one owner register line (or none: DEC-841 already decided the nine)<br>• S2–S5 and F1–F4 lifted (the forms-agree check, the authority-line rewrite) | Ticket closed with reason; W2-27/W2-46 deps cut | B1 (`validate_w2.py`'s checks), B2 (Contract) |
| D-T23 | W2-110, a product's CTO-only install rule | `DAEO-3r1j`; FULL review pass; beh 328 | $15.0, 4 pk | Rule 4 | Aim 3 | **Keep: land**; met | Landing after a merge | — |
| D-T24 | W2-112, shared reranker | `DAEO-clon`; round 2 done; P-W2-112-F9 with the owner | $20.8, 7 pk | GPU crashes from per-session rerankers | Aim 1 / yes / loses work | **Done in substance; finish and close** (DEC-1047 (1)); S6 per DEC-1046; S7 by its ACT | Close record; the stopgap's ACT | Owner (F9) |
| D-T25 | W2-122, seeded rebuilds | `DAEO-blwa`; approved in the queue | $17.4 | No cold rebuild | Aim 1 / yes / loses work (time) | **Done in substance; land and close**; S4 needs W2-116 | Landing | — |
| D-T26 | W2-123, parallel shared embedder and bounded retry | `DAEO-qzrq`; approved in the queue | $22.9, 3 pk | Timed-out embeddings | Aim 1 | **Done in substance; land and close**; absorbs W2-20 S12 (its S2, S5 and S7 already say it) | Landing | — |
| D-T27 | W2-126, the machine-wide vector cache | `DAEO-jpr0`; finishing (DEC-1047) | $5.6 | 503,000 texts embedded in 13 h | Aim 1 | **Done in substance; close**; S7 after W2-123 lands | Close record | W2-123 |

### 2b. Open, Wave 2 (45)

| id | what | where | cost | what it protects | DEC-1010 test | recommendation | what lifting takes | depends on |
|---|---|---|---|---|---|---|---|---|
| D-T28 | W2-00, coordination | `DAEO-sdxk` | LITE | The main session's identity | Aim 4 | **Keep** | — | — |
| D-T29 | W2-06, fast pre-commit tier and commit-time re-index | `DAEO-kia7` | Est. F 13.6 h | Fresh indexes after a commit; a fast pre-commit | Re-index: aim 1. Pre-commit tier: no (hooks off here). Staged secrets: lifted (DEC-1045) | **Merge:**<br>• S1, S2, S5, F1 → W2-116 (the integration store refreshed after every landing) and W2-122 (a worktree's incremental seeded rebuild)<br>• S3 and S4 lifted | Ticket closed as absorbed | B2 (hooks), A1-1 |
| D-T30 | W2-08, hooks back on | `DAEO-7r5e` | Est. S 9.2 h + an owner act; S4 asks for 17 of 17 `gov check` families | Checks on every commit | No (checks at every commit: the owner's complaint) | **Retire:**<br>• S1–S6 lifted with exit criterion 2 (owner)<br>• S7 → W2-42a S9 | Close with reason; exit criterion 2 dropped by the owner | B1, B2 (hooks) |
| D-T31 | W2-11b, seven lines W2-11 landed without | `DAEO-9bc0` | Est. S | DEC-1010's verdict in the template | S1 yes (DEC-1010). S3–S7: CTO ceremony | **Re-scope to S1 and S2.** S3 (status-block counts), S4 (mechanism per rule), S5 (checkpoint budget), S6 (corroboration rule), S7 (net-growth daily document) lifted | Ticket edit | C |
| D-T32 | W2-15a, EXP-003 baseline | `DAEO-rd0g` | Est. F | Memory measured | Aim 1 | **Merge into W2-15b** (one EXP-003 ticket, two runs, W2-32 between):<br>• S1 met (DEC-954 Q9, DEC-957)<br>• S2, S3, S5–S7 as run 1<br>• S4 → W2-88 S6 | Ticket closed as absorbed | — |
| D-T33 | W2-15b, EXP-003 final | `DAEO-swdu` | Est. F | Memory at 85/95 % | Aim 1 | **Re-scope:**<br>• absorbs W2-15a<br>• S1–S3, S5–S9 keep<br>• S4 → W2-88 (duplicate)<br>• S10 met by the emergency (query embedder on the GPU) | Ticket edit | — |
| D-T34 | W2-21, stable launch: `gov launch lead` | `DAEO-1ahb` | Est. F | Leads launched with a role | Aim 3 | **Merge:**<br>• S1 → W2-121 (the dispatcher launches through the gate)<br>• S2 → W2-33 S2<br>• S3 → W2-60a S8 (the `Session:` trailer lifted: trailers as gates, DEC-953 B)<br>• S4 met by W2-60a S3 and S4<br>• S5–S8 and F1 → W2-56 | Ticket closed as absorbed | — |
| D-T35 | W2-23, adoption safety | `DAEO-kmcr` | Est. F | The owner's files survive adoption and rollback | Aim 4 / yes / **loses work** | **Keep**, all lines (S6: EXAMIN's path has a space) | — | — |
| D-T36 | W2-24, Track A gate run | `DAEO-0mab`; 23 deps | Est. F 13.6 h | AR lines shown | Repeats W2-46; **unpassable** (S2, S3 need Wave 3) | **Retire:**<br>• S1 → W2-60a/W2-56<br>• S2 → W2-81 S11<br>• S3 → Wave 3 (W2-17)<br>• S4 → W2-46 S1<br>• S5 → W2-46 | Close with reason; exit criterion 5 re-worded | Owner |
| D-T37 | W2-25, Track A audit | `DAEO-btt7` | Est. F | — | Repeats W2-47 | **Retire** → W2-47 | Close with reason | Owner |
| D-T38 | W2-27, EXAMIN's copy | `DAEO-h4rh`; 46 deps, 34 open | Est. F, 1–2 days | The product's real goal | Aim (all four) | **Keep, re-scope:**<br>• S1 and S13: W2-16's release only<br>• S4: `gov doctor` green only (`gov check` families per B1)<br>• S8: reds named in the close record, no ratchet<br>• the rest kept<br>• deps re-derived (D-5) | Ticket edit; K9 amended | B1, owner |
| D-T39 | W2-28, independent verdict on the copy | `DAEO-csj8` | Est. F | The reviewer never fixes what it reviews | Aim 3 | **Keep** | — | — |
| D-T40 | W2-29, EXAMIN's real repository | `DAEO-b926` | Est. F | — | Aim | **Keep** (S1's "after green CI" depends on CI: Wave 3) | Wording | — |
| D-T41 | W2-30, the healthy verdict on the real repository | `DAEO-60rw` | Est. F | — | Aim 3 | **Keep** | — | — |
| D-T42 | W2-32, retrieval improvements | `DAEO-0pyc` | Est. S | Memory to 85/95 % | Aim 1 | **Keep** | — | — |
| D-T43 | W2-33, the three layers' roles | `DAEO-lrre`, p2 | Est. S, about 260 LOC | Roles kept apart | Aim 3: S2, S3, S6, S7, S8, S10 yes | **Re-scope:**<br>• keep S2 (ticket-lead role), S3 (defaults), S6 (QA engineer), **S7 (the work order: the builder never reads the acceptance tests)**, S8 (one writer per worktree: loses work), S10 (DEC-1010 moderator); absorbs W2-60b S9<br>• S1 and S5 (CTO and Senior Engineer roles) → Wave 3 with W3-P09<br>• S4 (typed handoff, CAP-22.b) → Wave 3 (contradicts W2-109)<br>• S9 (approval classes, quiet hours) lifted | Ticket edit | C |
| D-T44 | W2-40, EXP-002 sandbox research | `DAEO-6ox0`, p2 | Est. F, research | The hook's time limit against the guard's deadline | S3: aim 3 / yes (under load) / fails open. S1: deliberate | **Re-scope to S3** (one measurement); S1, S2 and S4 → Wave 3 | Ticket edit | — |
| D-T45 | W2-46, Wave 2 exit run | `DAEO-nn1s`; 89 deps | Est. F | Exit evidence | Aim | **Re-scope:**<br>• S1, S3, S4 keep<br>• S2 (the CIT-P→CIT-E propagation on a-dev) lifted with W2-37's CIT-P part<br>• S5 → "`gov doctor` green in EXAMIN"<br>• absorbs W2-24 S5<br>• deps regenerated | Ticket edit | Owner (exit criteria) |
| D-T46 | W2-47, Wave 2 exit audit | `DAEO-jip3` | Est. F | Independent audit | Aim 3 | **Keep**; S3 ("through the hook") lifted; absorbs W2-25 | Ticket edit | — |
| D-T47 | W2-60b, one record per session | `DAEO-ecac` | Est. S | Cost measured (governance share, exit criterion 8) | Aim (the owner's cost question) / — / no | **Re-scope:**<br>• keep S1–S3, S5 (the record from the harness's own JSON: the lead logs already carry `usage` and `total_cost_usd`)<br>• keep S7, S8 (roles from files) and S10 (one writer per worktree: loses work)<br>• S4 (window and compactions) and S6 (the close's join) lifted<br>• S9 → W2-33 | Ticket edit | A1 (token measures) |
| D-T48 | W2-82, a Definition of Ready | `DAEO-4k3l`; K9 criterion | Est. S, 7 lines | Tickets launched with well-formed deps (aim 4) | Aim 4 / yes / no loss, but a launch on an open dep wastes a run | **Re-scope to a lite check the dispatcher calls:**<br>• S1, S3, S4 with DEPENDENCY_OPEN, KPIS_INCOMPLETE, PATHS_INVALID, ACCEPTANCE_PATH_MISSING<br>• SOURCES_UNRESOLVED (a register lookup) and PROFILE_MISSING lifted<br>• S5's schema field, S6 (CIT-P and owner approval) and S7 (boilerplate) lifted<br>• out of K9 | Ticket edit; K9 amended | Owner (K9) |
| D-T49 | W2-83a, a playbook form, its schema and the adopt step | `DAEO-dy7j`; K9 criterion | Est. S + CIT-P + owner approval | Documentation of each stream's practices | No | **Retire**: S1–S5 and F1–F4 lifted (a new record type checked by `gov check`, an adopt step, a CIT-P) | Close with reason; K9 amended | B1, B2, owner |
| D-T50 | W2-83b, nine keystone playbooks | `DAEO-mc6n` | Est. S | The Senior Engineers' briefs | No (the three layers go to Wave 3) | **Retire**: S1–S4 lifted; S2's annex D practices → DECISIONS-IN-FORCE (part C) | Close with reason | C |
| D-T51 | W2-88, memory for any repository | `DAEO-2bdu`; 500 LOC | Est. F | Memory in an adopted repository | Aim 1 | **Keep, re-scope:**<br>• S5 → W2-124 (duplicate)<br>• absorbs W2-15a S4 and W2-15b S4 (scale)<br>• S10: one public GitHub repository, not two (estimate: saves indexing about 10^4 files)<br>• the rest kept | Ticket edit | — |
| D-T52 | W2-90c, W2-90b's cases that need W2-105 or W2-110 | `DAEO-fu3n` | Est. L | Rule 4's tests green | Aim 3 (a red) | **Merge into DEC-1039 step 3** (the reds, a test designer); S1–S4 and F1–F2 kept as that fix's acceptance | Ticket closed as absorbed | W2-105 and W2-110 landing |
| D-T53 | W2-93, W2-81's hidden half | `DAEO-6y0x` | Est. S | The measure not tuned to its test | Aim 3 | **Keep** | — | — |
| D-T54 | W2-94, EXAMIN's question set | `DAEO-g87r` | Est. S | Memory measured on EXAMIN | Aim 1/3 | **Keep** | — | — |
| D-T55 | W2-98, the spec-writing skill | `DAEO-wi46` | Est. S | **Specs and KPIs (aim 2)** | Aim 2 | **Keep, re-scope:**<br>• S1–S4 keep<br>• S5 (three scenarios before the text) optional<br>• S6 only if imported<br>• S7 kept (the adapter does it) | Ticket edit | — |
| D-T56 | W2-99, the benchmarking skill | `DAEO-lxzn`, p2 | Est. S | Research | Aim 2 | **Merge into the kernel's existing `discovery` skill** (a section: criteria first, a sourced verdict): S1 and S2 → that section; S3–S7 and F4–F7 (boilerplate) lifted | Ticket closed as absorbed; one skill edit | — |
| D-T57 | W2-100, domain skills A | `DAEO-uw5h`, p3, after ACT 2 | Est. S, 400 LOC | — | Not in the four needs | **Wave 3** | Re-tag; out of W2-27's deps | — |
| D-T58 | W2-101, domain skills B | `DAEO-6icv`, p3 | Est. S, 300 LOC | — | No | **Wave 3** | Re-tag | — |
| D-T59 | W2-102, the release skill | `DAEO-rpfv`, p2 | Est. L | — | No (W2-16 closed) | **Retire**: S1 → a checklist in W2-16's own document; F1 is already the guard's and the owner's | Close with reason | — |
| D-T60 | W2-103, the technical-writing skill | `DAEO-hgv3`, p3 | Est. L | — | No | **Retire** (or Wave 3) | Close with reason | — |
| D-T61 | W2-111, the hook-latency cases time the hook | `DAEO-qvff` | Est. L | 11 latency cases that fail by load | Not fail-open | **Merge into DEC-1039 step 2's test refactor**; S1–S4 and F1–F3 kept as its lines | Ticket closed as absorbed | A1-3 |
| D-T62 | W2-113, the adopted CTO named at adoption | `DAEO-g29a` | Est. S | Rule 4 works in an adopted product with no hand edit | Aim 3 / yes / **blocks all installs** | **Re-scope:** keep S1–S3; S4 (a quiet-hours permission hook in the kernel) lifted | Ticket edit | C (quiet hours) |
| D-T63 | W2-115, the smart close (19 lines) | `DAEO-emq1`; 400 LOC | Est. F | Scoped closes; red attribution; READY by code | Aim 4: S1–S3, S5, S7, S11 yes | **Keep, re-scope, absorb W2-117:**<br>• keep S1–S3, S5, S7, S9, S10, S11 (DEC-1010's one home)<br>• S4 simplified: a red is the change's unless the last nightly had it red the same way. No triple re-run with and without the batch (A2-7)<br>• S6: isolate culprits only when a batch is red<br>• S8: product default, off here (DEC-1045)<br>• S12 (rounds not converging), S13 (case and assertion counts), S14 (three green runs before a test may refuse), S15 (governance share per close) lifted | Ticket edit | A2-7, B1, C |
| D-T64 | W2-116, the designers' store | `DAEO-f58b` | Est. S | **The test designer never reads the engineer's worktree**; a warm base for seeding | Aim 3 and 1 | **Keep**; absorbs W2-06 S1, S2, S5, F1 | Ticket edit | — |
| D-T65 | W2-117, the merge queue in the product | `DAEO-zkr9` | Est. F | Test before merge | Aim 4 | **Merge into W2-115** (one land-and-close path):<br>• S1–S6 → W2-115 (S1 duplicates S6, S2 duplicates S7, S6 duplicates S10)<br>• S7 → W2-115 S11 | Ticket closed as absorbed | — |
| D-T66 | W2-118, `gov watch` and brief gaps | `DAEO-ts4y` | Est. S | Waking the CTO | Aim 4 in part | **Merge:**<br>• S1 and S3 → W2-121 (inbox)<br>• S5 is word for word W2-121 S13<br>• S2 (brief gaps, W3-P02 parked) and S4 (resolving every id in a return) lifted<br>• this breaks the W2-121 → W2-27 chain | Ticket closed as absorbed; W2-121's dep cut | C |
| D-T67 | W2-119, the guard's refusals counted | `DAEO-168f` | Est. F, 80 LOC | Finding false refusals | Not fail-open; product version of the refusal harvest (A2-6) | **Retire**: S1–S3 and F1–F2 lifted; W2-42a's replay measures false refusals once | Close with reason | A2-6 |
| D-T68 | W2-120, the skill validator | `DAEO-i89t`, p2 | Est. S | Skills grant no permissions (CAP-24.b) | S3: aim 3, cheap, static | **Re-scope to S3**; S1 (the twelve-field brief check) and S2 lifted | Ticket edit | — |
| D-T69 | W2-121, `gov dispatch` (18 lines) | `DAEO-cb2b`; 500 LOC | Est. F; the CTO's live version 3,538 lines | **Governing the traffic** | Aim 4 | **Keep, re-scope** (a port of the CTO's dispatcher and balancer):<br>• keep S1–S10, S13, S15, S16, plus the Load Balancer lines (DEC-1039 1b, P-LB-PRODUCT-1) and W2-20's S6, S9, S11 as measured peaks<br>• S11 → W2-115 S11<br>• S12 (heartbeat, W3-P16) → Wave 3<br>• S14 kept as a status figure, not a daily report<br>• S17 (morning report of server crashes) lifted<br>• the W2-118 dep removed | Ticket edit | C (LB and dispatcher stay) |
| D-T70 | W2-124, a rebuild without its semantic store fails | `DAEO-mb2t` | Est. S | A partial store not reported ok | Aim 1 / yes / fails open | **Keep**; absorbs W2-88 S5 | — | W2-122 |
| D-T71 | W2-125, the context gate before the close's runs | `DAEO-jfm3` | Est. S | Polish of a lifted gate (CONTEXT_FAILED, DEC-953 A) | No | **Retire**: S1–S3 and F1–F2 lifted | Close with reason | A1-4, B1 |
| D-T72 | W2-127, the reranker socket in the sandbox | `DAEO-1vka`, p0 | Est. F, 40 LOC | Sandboxed workers reranked | Aim 1/3 | **Merge into W2-56** (the same `launcher.py` sandbox write list): S1–S3 and F1–F2 → W2-56; S4 → W2-112 S4's count | Ticket closed as absorbed | W2-112 |

### 2c. Tagged Wave 3 or parked but still counted (20)

| id | what | where | cost | what it protects | DEC-1010 test | recommendation | what lifting takes | depends on |
|---|---|---|---|---|---|---|---|---|
| D-T73 | W2-09, SubagentHandback on the guard's list | `DAEO-a3m2` | Est. F | Known-tool list | Aim 3 | **Wave 3** (stays) | Re-tag | — |
| D-T74 | W2-10, guardrails explain and refuse once | `DAEO-cuao` | Est. F | Fewer repeated refusals | Aim 3 | **Wave 3** | Re-tag | B2 |
| D-T75 | W2-12, `gov approve` and owner-approval facts | `DAEO-j8gn`, 340 LOC | Est. F | Gating ratchet and escalation entries | Lifted gates (DEC-953 B) | **Retire**: S1–S7 and F1–F3 lifted; DEC-861's decision-record commits stand | Close with reason | B1, B2 |
| D-T76 | W2-14, ARGUS's full cycle | `DAEO-7y6v` | Est. F | Governance share per programme | Moved to W2-81 and EXAMIN (exit criterion 8) | **Retire** | Close with reason | — |
| D-T77 | W2-17, `gov update` | `DAEO-sdhj` | Est. F | Products updated | Aim (products) | **Wave 3** | Re-tag | — |
| D-T78 | W2-18, pinned install | `DAEO-057v` | Est. S | — | Aim | **Wave 3** | Re-tag | — |
| D-T79 | W2-19, language-agnostic test commands | `DAEO-jzvg` | Est. F | Non-Python products | Aim 4 | **Wave 3, re-scoped**: S5 and S7 (the ratchet baseline and its field rule) lifted | Ticket edit | B1 |
| D-T80 | W2-22, `gov doctor` green | `DAEO-xm6l` | Est. S | — | — | **Wave 3** | Re-tag | B1 |
| D-T81 | W2-31, budget gates | `DAEO-wbdh` | Est. F | A token budget that stops a run | A gate: not fail-open or loss | **Retire** (W2-60b's records measure cost) | Close with reason | — |
| D-T82 | W2-34, `gov readiness --generate` | `DAEO-yadm` | Est. S | — | — | **Wave 3** | Re-tag | — |
| D-T83 | W2-35, the UX readiness row | `DAEO-2keg` | Est. S | — | — | **Wave 3** | Re-tag | — |
| D-T84 | W2-36, `gov discover` | `DAEO-w19l` | Est. S | **Discovery agents (aim 2)** | Aim 2 | **Wave 3, first in line** | Re-tag | — |
| D-T85 | W2-38, profile from impact | `DAEO-g23i`; dep on withdrawn W2-48 | Est. F | Impact-selected tests | W2-66's scoped selection does it | **Retire** | Close with reason | — |
| D-T86 | W2-39, a model switch gives the same input hash | `DAEO-wudw` | Est. S | Reproducibility | No ordinary failure | **Retire** | Close with reason | — |
| D-T87 | W2-41, close and escalation integrity | `DAEO-s694` | Est. F | Escalation state, the probe gate | Lifted gates | **Retire** | Close with reason | B1 |
| D-T88 | W2-42, guard: missing role, links, atomic saves | `DAEO-fau3` | Est. F | S3 (atomic saves: loses work) | S3 yes; S6 (links) deliberate | **Wave 3**, S3 first | Re-tag | B2 |
| D-T89 | W2-43, CI integrity and the secret-rule floor | `DAEO-u5g6` | Est. S | Gitleaks on every pushed commit | Lifted here (DEC-1045) | **Retire here**; a product CI row in Wave 3 | Close with reason | — |
| D-T90 | W2-44, trailers bound to the launch identity | `DAEO-zndm` | Est. F | A forged role | Deliberate (ADR-0001); trailers as gates lifted | **Retire** | Close with reason | B2 |
| D-T91 | W2-45, `gov check` runner semantics | `DAEO-neam` | Est. S | — | — | **Wave 3, or retire per B1** | — | B1 |
| D-T92 | W2-78, the path map's lists in record files | `DAEO-v4is`, parked | $8.3 spent | Moving the ratchet lists | Lifted lists (DEC-953 B) | **Retire** | Close with reason | B1 |

## Evidence for the larger items

**Counts.**
- `python3 /tmp/gov-os-inv-D/tickets.py`: 193 tickets; 137 tagged `wave-2` (45 closed, 27 in progress, 65 open).
- 20 of the open ones are also tagged `wave-3` or `parked`.
- Class counts: 88 implementation, 13 test-revision, 9 specification.
- Filed per day: 54 on 10-16; 17, 19, 16, 5 and 8 on 10-29 to 11-02.

**KPI lines.**
- `kpis.py` → `/tmp/gov-os-inv-D/kpis.txt`: 716 lines in the 92 live tickets.
- Pattern counts are in D-7.
- Growth per ticket comes from the first version of each ticket file (`git log --diff-filter=A`) against today.

**Fate of the 716 lines (estimate):**

| Fate | Lines |
|---|---|
| Retired tickets | 112 |
| Lifted inside re-scoped tickets | about 34 |
| Moved to Wave 3 (81 already tagged, about 7 more) | about 88 |
| Met by the emergency or a landing | 48 |
| Moved by merges | 75 |
| Left in Wave 2 | about 480 |

**Spend.**
- 170 Wave 2 lead logs parsed from `log/W2-*.json`, 15 unparsed. The total is **$1,161.1**.
- Per group (my grouping, an estimate):

| Group | Tickets | Cost | Tokens |
|---|---|---|---|
| Memory | 18 | $278 | 757 M |
| Roles, guard and launch | 9 | $214 | 574 M |
| Skills | 2 | $42 | 114 M |
| Traffic | 6 | $117 | 312 M |
| Gates, checks, records, Contract and test revisions | 31 | $512 | 1,397 M |

- The most expensive tickets are W2-05 ($61.5), W2-67 ($55.1), W2-50 ($46.4), W2-60a ($35.0), W2-96 ($34.9), W2-58 ($34.7) and W2-54 ($34.3).

**Saving from Part 2 (estimate)**, at the plan's median lead-hours per profile:

| What | Tickets | Lead-hours |
|---|---|---|
| Retiring the non-Wave-3 tickets | 10: 3 FULL, 5 STANDARD, 2 LITE | about 95 |
| Merging (half of each merged ticket's profile; its separate launch, review and close saved) | 11 | about 52 |
| Moving W2-100 and W2-101 to Wave 3 | 2 | about 18 |
| **Total** | | **about 165 lead-hours** |

That is about 17.5 ticket-equivalents (10 + 11/2 + 2). At the measured mean of $17.3 per Wave 2 ticket with logs, it comes to about $300 in lead tokens, plus the owner's packages. Wave 2 tickets averaged about 1 to 9 `P-W2-<n>-*` packages each, and W2-11 had 9.

**Branch state.**
- `git rev-list --count w2/<t>..w2/integrate` and the reverse; see D-8. W2-05, W2-55 and W2-96 have landed with nothing ahead; W2-56 and W2-109 are ahead 0 too but were only claimed.
- `git log --merges --first-parent` shows one landing each for W2-05, W2-96 and W2-55. The rest are syncs: W2-05 10, W2-96 7 + 6 tests-branch merges.

**Awaiting landing.**
- `dispatch/land.pending.txt`: W2-11, W2-105, W2-90b, W2-81, W2-91, W2-92, W2-61h.
- The queue holds W2-122 and W2-123 (`EMERGENCY-PLAN-2026-11-02.md` §"What was stopped").

**Dependencies.**
- A transitive walk over `.tickets` deps: W2-121, W2-118, W2-28–W2-30, W2-46 and W2-47 sit after W2-27.
- W2-27's open deps (34) are listed in D-5.

**The CTO's versions already live.**
- `governance/project/orchestration/tools/dispatch/dispatcher.py`: 3,191 lines.
- `balancer.py`: 347 lines.
- The cron runs the dispatcher every minute.
- `tools/verdict.py` and `test_verdict.py` are in place.
- The confined `heavy_slot.sh` is live (DEC-1043).

## Notes for the combiner (outside part D)
- DEC-1003's same-day mapping is the engine of KPI growth (D-2); it belongs to part C's list of CTO practices.
- `docs/plan/tools/validate_w2.py` (W2-51) checks contract items both ways. Retiring tickets may turn it red: part B1 should say whether it stays.
- CAP-44.h's lite verdict requires "gov check with no RED family" and "gov doctor green" for EXAMIN. If B1 lifts families, the Contract line needs the owner's change (a Contract ceremony, part B2).
- The CTO's `CHECKPOINT.md` is 35,642 bytes and its RESUME HERE runs to dozens of lines of history (part C).
