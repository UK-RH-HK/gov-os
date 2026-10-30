# TICKET-EDITS: the ticket-file changes that DEC-954's approval implies

From the W2 orchestrator's helper, 2026-10-30. The CTO applies them in the main tree with one commit per ticket (`Task: <tk id>`, `Implements: DEC-954`, `Role: orchestrator`). Each block gives:
- the ticket;
- the exact front-matter lines as they are (**was**) and as they become (**now**);
- the body line to add under the H1, where there is one.

The "was" lines were read from `.tickets/` at `29389754` and the commits after it up to `403d70b3`.

**Conventions used:**
- **Deferred to Wave 3:**
  - `status` stays `open`;
  - the tags gain `wave-3` and `deferred`;
  - `priority` becomes `4`, so a `tk ready` listing puts them last. No status for "deferred" exists: tk knows open, in_progress and closed;
  - the body gains one line naming DEC-953 and DEC-954 and the reason (from the plan's §3).
- **Withdrawn:** `status: closed`, the tag `withdrawn`, and a body line, as W2-48 was (DEC-880). The close is the owner's decision, not a 10-practice close.
- **Parked:** `status: open` (the claim released), the tags `parked` and `wave-3`, and a body line. The branch is kept.
- **Waits for the roles spec:** the tag `waits-roles-spec`. Remove it when the owner approves the spec.

---

## 1. The 19 tickets deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954)

The front matter for each:
- `priority:` becomes `4`;
- `tags:` gains `wave-3, deferred`.

The exact lines are in the table, then the body line (one per ticket).

| W2 · tk | was | now |
|---|---|---|
| W2-09 · DAEO-a3m2 | `priority: 1` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-10 · DAEO-cuao | `priority: 1` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-12 · DAEO-j8gn | `priority: 1` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-14 · DAEO-7y6v | `priority: 1` / `tags: [wave-2, integration, full]` | `priority: 4` / `tags: [wave-2, integration, full, wave-3, deferred]` |
| W2-17 · DAEO-sdhj | `priority: 1` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-18 · DAEO-057v | `priority: 1` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |
| W2-19 · DAEO-jzvg | `priority: 1` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-22 · DAEO-xm6l | `priority: 1` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |
| W2-31 · DAEO-wbdh | `priority: 2` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-34 · DAEO-yadm | `priority: 2` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |
| W2-35 · DAEO-2keg | `priority: 2` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |
| W2-36 · DAEO-w19l | `priority: 2` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |
| W2-38 · DAEO-g23i | `priority: 2` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-39 · DAEO-wudw | `priority: 2` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |
| W2-41 · DAEO-s694 | `priority: 2` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-42 · DAEO-fau3 | `priority: 2` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-43 · DAEO-u5g6 | `priority: 2` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |
| W2-44 · DAEO-zndm | `priority: 2` / `tags: [wave-2, implementation, full]` | `priority: 4` / `tags: [wave-2, implementation, full, wave-3, deferred]` |
| W2-45 · DAEO-neam | `priority: 2` / `tags: [wave-2, implementation, standard]` | `priority: 4` / `tags: [wave-2, implementation, standard, wave-3, deferred]` |

**The body line,** under each H1: `**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** <reason>.` The reasons, from PLAN-W2-DEC953 §3:
- **W2-09:** The guard keeps only its four, then five, rules (DEC-953 item 2); DEC-946 already held it.
- **W2-10:** Deferred in REPLAN §2.2; the guard is down to its rules; W2-11 no longer depends on it.
- **W2-12:** K5, `gov approve` (DEC-941 item 3).
- **W2-14:** REPLAN §2.2; the governance share is measured on W2-81 and EXAMIN instead (W2-60b's records).
- **W2-17:** The rest of K7 (DEC-941 item 3); CAP-45.a moves to Wave 3 by a CIT-P note or is a named exception.
- **W2-18:** The rest of K7 (DEC-941 item 3); W2-81 and EXAMIN install W2-16's release (DEC-954 Q8c).
- **W2-19:** EXAMIN's tests are pytest (W2-26's README, finding 1), so DEC-727's condition is not met.
- **W2-22:** K8 (DEC-941 item 3); `gov doctor` green on EXAMIN's copy is W2-27's KPI.
- **W2-31:** CAP-04 moved to Wave 3 (DEC-841); REPLAN §2.2.
- **W2-34:** CAP-30.c moved to Wave 3 (DEC-841).
- **W2-35:** CAP-30.g moved to Wave 3 (DEC-841).
- **W2-36:** CAP-32.d moved to Wave 3 (DEC-841).
- **W2-38:** CAP-53.b moved to Wave 3 (DEC-841); W2-66 covers selection.
- **W2-39:** CAP-37.e moved to Wave 3 (DEC-841).
- **W2-41:** `gov close` is not a gate here; its high rows go to Wave 3's hardening; W2-81's proof shows whether any bites.
- **W2-42:** The guard is down to its rules; write scope is lifted (DEC-953 item 2).
- **W2-43:** K8 (DEC-941); the nightly is the integration check (DEC-952 1b; DEC-953 item 3).
- **W2-44:** Trailers are lifted as a gate (audit §4.3).
- **W2-45:** K8 (DEC-941); W2-26 found no trigger (indexing about 30 % of the envelope).

The deferred tickets' own `deps` stay as they are: they point at each other or at Wave 2 tickets, and nothing in Wave 2 waits on them after §2's edits.

---

## 2. Parked, withdrawn

### W2-78 · DAEO-v4is: parked (DEC-954 Q5; P-W2-78-PARK (a))

**Front matter:**
- `status: in_progress` → `status: open`
- `priority: 1` → `priority: 4`
- `tags: [wave-2, close, records, standard]` → `tags: [wave-2, close, records, standard, parked, wave-3]`

**Body line under the H1:** `**Parked by the owner (DEC-954 Q5; P-W2-78-PARK (a), 2026-10-30).** The branch w2/W2-78 and its worktree's commits are kept unmerged for Wave 3's hardening or for when the lifted gates come back. Nothing on w2/integrate changes. DEC-953 item 4a gets the effect: the selection leaves governance files out. Its discoveries are filed as Wave 2 list rows (W2-H064, W2-L453, W2-L454). For whoever resumes it: (1) src/gov/close/command.py:233-234 decides from the path map's own accepted_reds and load_sensitive keys whether runs report each test's result, so a move of the lists must move that reading too; (2) W1-01's support (w1_01_support.acceptance_exemptions) reads the path map itself; (3) W2-66's live case test_the_record_only_paths_are_dec_891_s_places_and_nothing_else enforces DEC-891's place list; (4) the merge needed about half a day of test revisions in 79 earlier-suite cases, two path-map ACTs, a re-pin and the outside readers' updates (P-W2-78-PARK §2).`

### W2-79 · DAEO-av72: withdrawn (DEC-953 item 10c, DEC-954)

**Front matter:**
- `status: open` → `status: closed`
- `tags: [wave-2, tests, orchestration, tools, lite]` → `tags: [wave-2, tests, orchestration, tools, lite, withdrawn]`

**Body line:** `**WITHDRAWN by the owner (DEC-953 item 10c, approved by DEC-954, 2026-10-30), unbuilt.** The brief builder changes with W2-11 and W2-60a. This ticket's KPI that every fixed brief gap stays fixed (brief-gaps.md's "Fixed by" column) passes to W2-11 (DAEO-k7hz). It ends by that decision, not by a 10-practice close.`

### W2-80 · DAEO-03dg: withdrawn (DEC-953 item 10c, DEC-954)

**Front matter:**
- `status: open` → `status: closed`
- `tags: [wave-2, tests, orchestration, close, tools, standard]` → `tags: [wave-2, tests, orchestration, close, tools, standard, withdrawn]`

**Body line:** `**WITHDRAWN by the owner (DEC-953 item 10c, approved by DEC-954, 2026-10-30), unbuilt.** The close queue's gates (a) to (h) are lifted (LIFTED-BY-DEC953.md A: ended). It ends by that decision, not by a 10-practice close.`

---

## 3. Dependency changes

### W2-11 · DAEO-k7hz: drops W2-10; waits for the roles spec; takes W2-79's KPI

**Front matter:**
- `deps: [DAEO-g0ip, DAEO-cuao]` → `deps: [DAEO-g0ip]`
- `depends_on:` block, delete the line `- DAEO-cuao`. What is left is `- DAEO-g0ip`.
- `tags: [wave-2, skill, standard]` → `tags: [wave-2, skill, standard, waits-roles-spec]`
- `kpis.success`, append:
  `- 'Every gap the orchestrator fixed in the common brief or the brief builder (governance/project/orchestration/brief-gaps.md, its "Fixed by" column) has a case that builds a brief today and shows the fix is still in it; taken from the withdrawn W2-79 (DEC-954, PLAN-W2-DEC953 §4.2) [DEC-943 item 1]'`
- `sources:`, append `- DEC-954` and `- DEC-943`.

**Body line:** `**DEC-954 (2026-10-30):** W2-10 (Wave 3) dropped from the dependencies. The ticket builds nothing further until the owner approves the roles spec. Its CIT-P is part of the one combined K3 CIT-P (Q7). It takes W2-79's KPI.`

**Note:** the roles spec may widen or rewrite these KPIs. If so, a second edit follows its approval.

### W2-23 · DAEO-kmcr: depends on W2-16, not W2-18

**Front matter:**
- `deps: [DAEO-g0ip, DAEO-057v]` → `deps: [DAEO-g0ip, DAEO-49o5]`
- `depends_on:` block: `- DAEO-057v` → `- DAEO-49o5`
- `sources:`, append `- DEC-954`.

**Body line:** `**DEC-954:** depends on W2-16 (DAEO-49o5), not W2-18 (Wave 3). It shares src/gov/adopt/ with W2-52 and W2-88, split by file; whichever merges second merges back.`

### W2-24 · DAEO-0mab: dependencies are the Wave 2 tickets only

**Front matter:**
- `deps:` drops `DAEO-a3m2, DAEO-cuao, DAEO-j8gn, DAEO-7y6v, DAEO-sdhj, DAEO-057v, DAEO-jzvg, DAEO-xm6l` (Wave 3) and `DAEO-xxgp` (W2-48, withdrawn).
  - **now:** `deps: [DAEO-g0ip, DAEO-zflj, DAEO-ym8a, DAEO-u4oz, DAEO-0z8c, DAEO-kia7, DAEO-r9ss, DAEO-7r5e, DAEO-k7hz, DAEO-zqvn, DAEO-rd0g, DAEO-49o5, DAEO-r30l, DAEO-1ahb, DAEO-kmcr, DAEO-ha8z, DAEO-kl5e, DAEO-7rr2]`
- `depends_on:` block: the same nine lines deleted.
- **Proposed additions** (the CTO to confirm; they are not in the plan's §6):
  - `DAEO-cy5o` (W2-57): DEC-813 already says W2-24 does not start before W2-57 has closed;
  - `DAEO-siiz` (W2-52), `DAEO-wnnz` (W2-56) and `DAEO-egsy` (W2-51): later Track A tickets;
  - W2-88's id, once filed: Track A, adoption readiness.
- `sources:`, append `- DEC-954`.

**Body line:** `**DEC-954:** dependencies are the Wave 2 tickets only. The AR lines whose tickets moved to Wave 3 are named Wave 3 in this ticket's report (exit criterion 5). W2-17 is Wave 3, so the "gov update" step is a named Wave 3 line. The release is W2-16's.`

### W2-27 · DAEO-h4rh: K9's criteria, plus W2-26, W2-52, W2-56, W2-21, W2-16 and W2-88

**Front matter:**
- `deps:`
  - **drops:** `DAEO-7r5e` (W2-08), `DAEO-a3m2` (W2-09), `DAEO-cuao` (W2-10), `DAEO-057v` (W2-18), `DAEO-jzvg` (W2-19). W2-45 was not listed.
  - **adds:**
    - K9's criteria (DEC-954 Q1): `DAEO-0pyc` (W2-32, memory at 85 %), `DAEO-cv58` (W2-60a), `DAEO-ecac` (W2-60b), `DAEO-k7hz` (W2-11) and `DAEO-lrre` (W2-33) for the roles landed, `DAEO-l78m` (W2-81, passed), `DAEO-4k3l` (W2-82), `DAEO-dy7j` (W2-83a);
    - `DAEO-wnnz` (W2-56);
    - W2-88's id (its live trial).
  - W2-16 (`DAEO-49o5`), W2-21 (`DAEO-1ahb`), W2-26 (`DAEO-2ds6`) and W2-52 (`DAEO-siiz`) are already there.
  - **now:** `deps: [DAEO-g0ip, DAEO-ym8a, DAEO-u4oz, DAEO-0z8c, DAEO-kia7, DAEO-49o5, DAEO-r30l, DAEO-1ahb, DAEO-kmcr, DAEO-2ds6, DAEO-ha8z, DAEO-kl5e, DAEO-siiz, DAEO-wnnz, DAEO-0pyc, DAEO-cv58, DAEO-ecac, DAEO-k7hz, DAEO-lrre, DAEO-l78m, DAEO-4k3l, DAEO-dy7j, <W2-88 id>]`
- `depends_on:` block: the same list, one id a line.
- `kpis.success`, append:
  - `- 'W2-16''s numbered, frozen release is the one installed, never this repository''s branch [DEC-954 Q8c]'`
  - `- 'A clean gov close of the LITE ticket on the copy, at exit 0, on that release, is exit criterion 1''s proof; gov doctor green on the copy is exit criterion 3''s [DEC-953, DEC-954]'`
  - `- 'W2-88''s tools run on the copy at adoption (the assessment, the refactoring plan as proposals, the full index and embeddings), and EXAMIN''s question set is measured with both figures [DEC-954 Q9f]'`
- `sources:`, append `- DEC-953` and `- DEC-954`.

**Body line:** `**DEC-954 Q1:** this ticket starts only when K9's entry criteria are met: memory proven, the roles, skills and briefs landed, the proving ground passed, the rest of the minimum closed. Never because a date arrived.`

### W2-29 · DAEO-b926: W2-16's release

**Front matter:**
- `deps: [DAEO-g0ip, DAEO-csj8, DAEO-btt7, DAEO-swdu]` → `deps: [DAEO-g0ip, DAEO-csj8, DAEO-btt7, DAEO-swdu, DAEO-49o5]`
- `depends_on:` block, add `- DAEO-49o5`.

(PLAN-W2-DEC953 §2.6 row 7 lists W2-16 among its deps. The owner's go stays a gate that is not a ticket.)

### W2-33 · DAEO-lrre: re-scoped (DEC-954 Q6, Q13); drops W2-21; waits for the roles spec

**Front matter:**
- `deps: [DAEO-g0ip, DAEO-1ahb]` → `deps: [DAEO-g0ip]`
- `depends_on:` block, delete `- DAEO-1ahb`.
- `title: Wave 2 roles and typed handoff records` → `title: 'The three layers'' roles and the typed handoff: the CTO, the Senior Engineer, the ticket lead''s role file, machine-readable defaults per role (outline; the roles spec defines it)'`
- `tags: [wave-2, role-definition, standard]` → `tags: [wave-2, role-definition, standard, three-layers, waits-roles-spec]`
- `kpis.success`, replace the five lines with the outline. The roles spec restates it before any build:
  - `- 'Outline, to be defined by the owner-approved roles spec (DEC-954): role files for the CTO (the master orchestrator) and the Senior Engineer (a stream''s sub-orchestrator, with its stream''s skills), generated as agents, each with its reads and writes, skills, model, brief contents and handover [DEC-954 Q6, Q13]'`
  - `- 'The ticket lead''s own role file (today a section of orchestrator.md) [DEC-954, DEC-236]'`
  - `- 'Machine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a''s launcher [DEC-954, DEC-839 item 5]'`
  - `- 'A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically; the twelve-field return is one [CAP-22.b (lite), AR-6]'`
  - `- 'Any role the roles spec finds undefined is scoped and drafted here [DEC-954 Q13a]'`
- `kpis.failure: []` → `kpis.failure:`
  - `- 'A role built before the owner approves the roles spec; a role file placed by hand rather than generated; a role without its machine-readable defaults.'`
- `sources:`, append `- DEC-954`.
- `closes:` keep `CAP-22.b` and mark it lite; `CAP-22.c` (test-execution and integration roles) → move to a Wave 3 row unless the spec places it. Note: DEC-841 already moved CAP-22.b/c to Wave 3, so this ticket carries no Contract Wave 2 item.
- `est_loc: 260` stays until the spec restates it.

**Body line:** `**Re-scoped by DEC-954 (Q6, Q13).** The earlier KPIs (test-execution, integration and UX roles) become Wave 3 rows unless the roles spec places them. Nothing is built before the owner approves the spec. One combined K3 CIT-P (Q7).`

### W2-46 · DAEO-nn1s: dependencies are the Wave 2 tickets only

**Front matter:**
- `deps:`
  - **drops** the Wave 3 tickets: `DAEO-a3m2, DAEO-cuao, DAEO-j8gn, DAEO-7y6v, DAEO-sdhj, DAEO-057v, DAEO-jzvg, DAEO-xm6l, DAEO-wbdh, DAEO-yadm, DAEO-2keg, DAEO-w19l, DAEO-g23i, DAEO-wudw, DAEO-s694, DAEO-fau3, DAEO-u5g6, DAEO-zndm, DAEO-neam`.
  - **drops** the withdrawn `DAEO-xxgp` (W2-48).
  - **adds** the Wave 2 tickets not listed: `DAEO-egsy` (51), `DAEO-siiz` (52), `DAEO-0rfi` (54), `DAEO-arrl` (55), `DAEO-wnnz` (56), `DAEO-cy5o` (57), `DAEO-5j8b` (58), `DAEO-kh9l` (59), `DAEO-cv58` (60a), `DAEO-ecac` (60b), `DAEO-iw1f` (61), `DAEO-h2k3` (61h), `DAEO-juee` (62), `DAEO-pl6k` (63), `DAEO-0uhh` (64), `DAEO-e82f` (65), `DAEO-c1uz` (66), `DAEO-9nys` (67), `DAEO-2gc7` (68), `DAEO-rmbe` (69), `DAEO-uzme` (70), `DAEO-e8f0` (71), `DAEO-ye2a` (72), `DAEO-qty6` (73), `DAEO-2azm` (74), `DAEO-ebmh` (75), `DAEO-tgk2` (76), `DAEO-b6hm` (77), `DAEO-l78m` (81), `DAEO-4k3l` (82), `DAEO-dy7j` (83a), `DAEO-mc6n` (83b), `DAEO-m1u3` (84), `DAEO-gdzh` (85), `DAEO-s9qc` (87), and W2-86's and W2-88's ids once filed.
  - **not added:** the parked W2-78 (`DAEO-v4is`) and the withdrawn W2-79 and W2-80.
  - **now:** `deps: [DAEO-g0ip, DAEO-zflj, DAEO-ym8a, DAEO-u4oz, DAEO-0z8c, DAEO-kia7, DAEO-r9ss, DAEO-7r5e, DAEO-k7hz, DAEO-zqvn, DAEO-rd0g, DAEO-swdu, DAEO-49o5, DAEO-r30l, DAEO-1ahb, DAEO-kmcr, DAEO-0mab, DAEO-btt7, DAEO-2ds6, DAEO-h4rh, DAEO-csj8, DAEO-b926, DAEO-60rw, DAEO-0pyc, DAEO-lrre, DAEO-6n5k, DAEO-6ox0, DAEO-ha8z, DAEO-kl5e, DAEO-egsy, DAEO-siiz, DAEO-7rr2, DAEO-0rfi, DAEO-arrl, DAEO-wnnz, DAEO-cy5o, DAEO-5j8b, DAEO-kh9l, DAEO-cv58, DAEO-ecac, DAEO-iw1f, DAEO-h2k3, DAEO-juee, DAEO-pl6k, DAEO-0uhh, DAEO-e82f, DAEO-c1uz, DAEO-9nys, DAEO-2gc7, DAEO-rmbe, DAEO-uzme, DAEO-e8f0, DAEO-ye2a, DAEO-qty6, DAEO-2azm, DAEO-ebmh, DAEO-tgk2, DAEO-b6hm, DAEO-l78m, DAEO-4k3l, DAEO-dy7j, DAEO-mc6n, DAEO-m1u3, DAEO-gdzh, DAEO-s9qc, <W2-86 id>, <W2-88 id>]` (65 filed + 2 to file)
  - Add each stream's coordination ticket when filed.
- `depends_on:` block: the same list, one id a line.
- `sources:`, append `- DEC-953` and `- DEC-954`.

**Body line:** `**DEC-954:** dependencies are the Wave 2 tickets only (Wave 3, withdrawn and parked removed). The exit run checks §5 as revision 4 states it: 10-practice close records; a clean gov close on W2-81 and EXAMIN's copy; the governance share on W2-81 and EXAMIN; gov doctor green on EXAMIN's copy.`

### W2-15a · DAEO-rd0g: Q-2 answered; the hidden half before it runs

**Front matter:**
- `deps: [DAEO-g0ip, DAEO-ym8a, DAEO-u4oz, DAEO-r9ss, DAEO-zqvn, DAEO-kl5e]` → `deps: [DAEO-g0ip, DAEO-ym8a, DAEO-u4oz, DAEO-r9ss, DAEO-zqvn, DAEO-kl5e, DAEO-h2k3]`
- `depends_on:` block, add `- DAEO-h2k3`.
- `kpis.success`, first line ("The metric is defined and recorded before the first run …"), append:
  ` Answered by DEC-954 Q9: the metric is W2-61's measure, both figures, on the enlarged set (about 48 questions, visible and hidden halves), the hidden half used only once the five-rule hook and W2-84 refuse it from every worktree; memory judged on the combined memory spec (Q9c) [DEC-954 Q9]`
- `sources:`, append `- DEC-954`.

### W2-15b · DAEO-swdu: on the combined spec, with W2-88

**Front matter:**
- `deps: [DAEO-g0ip, DAEO-rd0g, DAEO-0pyc, DAEO-2ds6]` → `deps: [DAEO-g0ip, DAEO-rd0g, DAEO-0pyc, DAEO-2ds6, <W2-88 id>]`
- `depends_on:` block, add W2-88's id.
- `kpis.success`, append:
  `- 'Memory is judged on the combined memory spec (semantic and lexical search, full indexing, full embeddings, the knowledge and code graph, the SQLite and vector-store structure); EXAMIN''s clone and ~/workspace are indexed with W2-88''s tools [DEC-954 Q9c, Q9f]'`
- `sources:`, append `- DEC-954`.

---

## 4. Re-scopes and KPI additions

### W2-61h · DAEO-h2k3: the enlarged set (DEC-954 Q9a, Q9b)

**Front matter:**
- `deps: []` → `deps: [DAEO-m1u3]`. This matches its `depends_on: [DAEO-m1u3]`; the two fields disagree today.
- `title:` → `'W2-61''s enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session'`
- `kpis.success`, first line: "Twenty hidden questions …" → `'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml, and hidden/) [DEC-954 Q9a, DEC-828 items 3 and 4, DEC-820 (d)]'`
- `kpis.success`, third line ("The same spread as the visible half …") → `'The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1 [DEC-954 Q9a, Q9c, DEC-833, DEC-866]'`
- `kpis.success`, append:
  `- 'The hidden half is used for a measure only after ACT 1''s five-rule hook and W2-84 refuse it from every worktree and run clone [DEC-954 Q9b, DEC-950]'`
- `allowed_paths:`, add `- fixtures/evaluation/memory-retrieval/visible/q21.yaml` … `q24.yaml`. These are the 4 drawn to the visible half: new files, and lens B's q01 to q20 are untouched.
- `est_loc: 0` stays. This is question writing; est. 12–14 lead-hours (MEMORY-SPEC-MAP B.2).
- `sources:`, append `- DEC-954`.

**Body line:** `**Re-scoped by DEC-954 Q9a.** The proposed size (48 with lens B's 20) and the time cost are in drafts/plan-dec954/MEMORY-SPEC-MAP.md part B, for the owner. If the owner chooses 50, the draw is 25 and 25 and 30 are written.`

**Also, the CTO's path-map edit:** `evaluation_sets.memory-retrieval.measures` gains the measured tickets: W2-86, W2-87, W2-88, W2-13, W2-55, W2-04 and W2-32 (with the retrieval tickets W2-61h's KPI already names).

### W2-32 · DAEO-0pyc: the escalation after two rounds (Q9e)

**Front matter:**
- `kpis.success`, append:
  `- 'If memory is below 85 % after two improvement rounds, the orchestrator escalates to the owner with the reasons; at the third the owner decides: a discovery and research ticket benchmarking market tools in a separate worktree, accepting the level reached, or another course [DEC-954 Q9e]'`
- `sources:`, append `- DEC-954`.

### W2-81 · DAEO-l78m: the `gov close` proof on a pinned release

**Front matter:**
- `kpis.success`, append:
  - `- 'In each synthetic repository, a ticket closes with gov close at exit 0 on a pinned release (W2-16''s numbered, frozen release): the clean gov close of exit criterion 1; its real run is the orchestrator''s [DEC-953, DEC-954 Q8c]'`
  - `- 'The builders and the per-repository question sets serve W2-88''s proof of memory for any repository, read-only [DEC-954 Q9f]'`
- `sources:`, append `- DEC-953` and `- DEC-954`.
- `deps` unchanged. The suite is test code and needs no release; the real run waits for W2-16's release, which the orchestrator orders.

### W2-83b · DAEO-mc6n: re-scoped to one playbook per stream

**Front matter:**
- `title: 'This project''s nine keystone playbooks, placing annex D''s standing practices'` → `title: 'One playbook per stream (the Senior Engineer''s brief), placing annex D''s standing practices'`
- `priority: 2` → `priority: 1`
- `tags: [wave-2, documentation, playbooks, standard, spare-capacity]` → `tags: [wave-2, documentation, playbooks, standard, three-layers, waits-roles-spec]`
- `kpis.success`, first line → `'One playbook per stream (S1 memory; S2 roles, skills and briefs; S3 sandbox and launch; S4 adoption and the proving ground), under docs/playbooks/, in W2-83a''s form: the stream''s purpose, its standing practices each citing its decision, its usual ticket classes, its roles with their skills, and its handovers to the CTO; each is the stream''s Senior Engineer''s brief; gov check is green on them [DEC-954 Q13, DEC-953 item 8, DEC-944 item 3]'`
- `kpis.success`, second line: "in at least one playbook" stays, reading the stream playbooks.
- `est_loc: 500` → `est_loc: 250` (est.: four playbooks, not nine).
- `sources:`, append `- DEC-953` and `- DEC-954`.

**Body line:** `**Re-scoped by DEC-953 and DEC-954 (PLAN-W2-DEC953 §6):** the stream playbooks, a three-layer foundation built in S2 before ACT 2; no longer spare capacity. It waits for the owner's approval of the roles spec.`

### W2-83a · DAEO-dy7j and W2-60b · DAEO-ecac: wait for the roles spec

- **W2-83a:** `tags: [wave-2, template, playbooks, kernel-template, standard, keystone-9]` → `tags: [wave-2, template, playbooks, kernel-template, standard, keystone-9, waits-roles-spec]`; `sources:` + `- DEC-954`.
- **W2-60b:** `tags: [wave-2, implementation, standard, launch, telemetry, keystone-3]` → `tags: [wave-2, implementation, standard, launch, telemetry, keystone-3, waits-roles-spec]`; `sources:` + `- DEC-954`.
- **Body line for each:** `**DEC-954:** builds nothing further until the owner approves the roles spec; its CIT-P is part of the one combined K3 CIT-P (Q7).` (W2-83a has a CIT-P too; the "four K3 tickets" are W2-60a, W2-60b, W2-11 and W2-33.)

### W2-20 · DAEO-r30l: DEC-950's rule (Q12)

- `sources:`, append `- DEC-954`.
- **Body line:** `**DEC-954 Q12:** in Wave 2, built on the owner's measured rule for this machine (DEC-950). Machine-agnostic in Wave 3: a parking-list row.`
- Also add **W3-P12** to `docs/plan/WAVE_3_PARKING.md`: "W2-20 machine-agnostic: on any machine the Gov OS reads its resources (CPU, memory, disk, GPU) and plans the execution to that capacity | the owner (DEC-954 Q12) | 2026-10-30".

### W2-16 · DAEO-49o5: the numbered, frozen release (Q8c)

- `sources:`, append `- DEC-954`.
- **Body line:** `**DEC-954 Q8c:** cuts a numbered, frozen release that W2-81 and EXAMIN's copy install; the owner tags it. Finished after ACT 1.`

### W2-61 · DAEO-iw1f: its EXAMIN-set KPI has no ticket (a CTO decision)

- KPI 6 reads: "The same split for EXAMIN's set, written by a session independent of the adopting team before W2-27". It is not met: `fixtures/evaluation/` holds `memory-retrieval` only.
- **Proposed:** file a small independent-auditor ticket for EXAMIN's set (MEMORY-SPEC-MAP gap 7), and record in W2-61's close record that KPI 6 moved to it, with DEC-954 as the reason. Otherwise W2-61 cannot close on its own KPIs.
- No front-matter change until the CTO decides.

---

## 5. New tickets to file

| W2 | Draft | Notes |
|---|---|---|
| W2-86 | `drafts/tickets/W2-86.md` | already drafted; S1 quick win |
| **W2-88** | `drafts/tickets/W2-88.md` | new (DEC-954 Q9f). Before filing, replace `depends_on` with the tk ids. It is drafted with `DAEO-ym8a, DAEO-siiz, DAEO-tgk2, DAEO-l78m`, so set `deps:` to the same list. Its CIT-P note (A9 lite into Wave 2) is a package before the engineer starts |
| a coordination ticket per stream (Q13) | not drafted | filed at the three-layer start, after the roles spec. The count is set by the number of Senior Engineers, which waits on Q10's measurement. Form: as W2-00, LITE, `role: orchestrator`, `class: coordination`, one per stream |
| W2-81's hidden half (companion) | the WBS card exists | not filed (MEMORY-SPEC-MAP gap 6) |
| EXAMIN's question set | none | not filed (gap 7) |
| the graph and code-graph routes in plain-question retrieval | none | proposed (gaps 2 and 3), for the owner |

---

## 6. W2-78's discoveries: Wave 2 list rows to file (P-W2-78-PARK §5; DEC-954 Q5)

Text only, in `docs/plan/WAVE_2_LIST.md`'s form (`| ID | Item | Owner | Closes when | Sources |`). The next free ids are W2-H064, W2-L453 and W2-L454: the last are H063, M408 and L452.

**§3.1 high:**

| ID | Item | Owner | Closes when | Sources |
|---|---|---|---|---|
| W2-H064 | `gov.check.pathmap` (core-pathmap) reports green without checking anything when the path map's `namespaces` is a mapping, which this repository's is: `src/gov/check/pathmap.py:47-49` returns no finding unless `namespaces` is a list. It also returns none when the path map cannot be parsed (`:40-45`). So "every tracked path matches exactly one namespace" is not checked here or in an adopted repository (found by W2-78's lead, 2026-10-30) | engineer | core-pathmap reads the mapping form the path map's schema states. It judges each tracked path against exactly one namespace, naming each path in none or in two. A path map that cannot be read or parsed is a finding, never green. Planted cases for both forms | W2-78's lead (DAEO-v4is, run 1, discovery 3); P-W2-78-PARK §5; DEC-954 Q5. Ordinary work: yes, because every `gov check` here runs it. Consequence: fails open |

Under the WBS's finish line (§6), a fail-open in ordinary work comes to the owner as a package before any round. **Recommendation:** fold it into W2-88. W2-88 writes path maps for adopted repositories and needs "no path in none or two namespaces" to hold. Its paths would gain `src/gov/check/pathmap.py` and `tests/unit/check/test_w2_88*`. The alternative is a LITE ticket of its own.

**§3.3 low:**

| ID | Item | Owner | Closes when | Sources |
|---|---|---|---|---|
| W2-L453 | `gates.RECORD_PREFIXES` (`src/gov/close/gates.py`) does not name `governance/project/records/`, so a `Task: decision-record` commit that edits a record file there is not measured as a record commit. It matters only once W2-78's record files exist: the folder is not on `w2/integrate` | engineer | `RECORD_PREFIXES` names the folder, in the same change that creates it (W2-78's resume) | W2-78's lead (discovery 6); P-W2-78-PARK §5. Ordinary work: no, not before W2-78 merges. Consequence: other. **Triage: Wave 3, with the parked W2-78** |
| W2-L454 | W2-62's prompt-in-force acceptance case runs on stand-in prompts, not the live ones, so a change to the live prompt's form is not caught. The case is in the test map's `record_reading` set because W2-78's KPI named it | independent-test-designer | the case reads the live prompt of the wave in progress (or the stand-ins are generated from it), with `Rewrite-Reason:` naming this row; no expectation lowered | W2-78's test designer (discovery 8); P-W2-78-PARK §5. Ordinary work: yes. Consequence: other, a weak test, not a fail-open of the product. **Triage: Wave 3** (no exit criterion broken), or W2-67's next round if its brief has room |

Not rows: W2-78's discoveries 1, 2, 4, 5 and 7. They hold only if W2-78 merges, and they are noted in W2-78's own body line above.
