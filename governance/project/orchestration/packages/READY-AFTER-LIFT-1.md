# READY-AFTER-LIFT-1: the first ready lists after the lift, for the owner's review (DEC-1125 (3) (iv), DEC-1110 (3))

Written 2026-11-11 ~03:00 UTC by the CTO (session 8ddb8b14) from `gov plan --open` at `56b4858cc7fb` (integrate, after the
night's ticket audit). **Nothing is launched from it until the owner has reviewed it.** The dispatcher's form is
beside this file (`READY-AFTER-LIFT-1/ready-batches.txt`, from `gov plan --ready`); it goes to
`dispatch/ready*.txt` only after the review.

## How to read it
- 98 open and in-progress tickets, **21 batches**, 528 waits. A batch's tickets run in parallel; each batch waits for
  the ones before it (shared writes, read-after-write, stated dependencies).
- **"in progress"** mostly means merged and waiting for its formal close (LIFT-CLOSES-1): W2-96, W2-122, W2-123 and
  W2-126 close first after the re-pin; then batch 1's remaining tickets are what is truly ready.
- **P4/after-the-lift** tickets sit late by design (W2-155 waits for W2-138 and W2-145, intended).

## Three things in it the CTO flags
1. **W2-156 (the brake) lands too late:** W2-27 (EXAMIN's copy) now depends on it (audit d, before EXAMIN), but it
   shares `src/gov/launch/launcher.py` with W2-82, which comes after W2-27; the plan breaks the cycle at W2-156 and
   puts it in batch 18, after W2-27 (batch 16). Options for the morning: (a) the owner's `plan_override` on W2-156
   (DEC-899's exception); (b) W2-82 lowered to P3 so the shared write orders W2-156 first (W2-82 waits for W2-27
   anyway; its owner-set place, DEC-946 priority 5, unchanged); (c) W2-156's launcher call moved to its own module.
   **Recommendation: (b)**, no code or exception, confidence medium.
2. **`NEEDS_UNDECLARED` on 73 tickets** (no `needs:` declared): planned on their own writes alone; the plan exits 1
   on it. Accepted for tickets already in progress (the CTO, DEC-1112 (3)); new tickets carry `needs`, `reads`,
   `waits_on` (DEC-1088 (3)).
3. W2-32 and W2-15a are in the plan as open work: LIFT-CLOSES-1 recommends they do not close at the lift (W2-32 S9
   at hit@5 58.3 % against 85 %, the owner's disposition).

## The batches (ticket, id, priority, role, state)
**Batch 1**
- W2-96 (`DAEO-ouet`, P0, engineer, in progress): The opaque acceptance runner: gov accept runs a ticket's acceptance tests and reports only pass or fail per KP
- W2-105 (`DAEO-zpdj`, P0, product-spec, in progress): The template's install block removed: an adopted product's CTO session reaches the guard's install rule and is
- W2-122 (`DAEO-blwa`, P0, engineer, in progress): Seeded rebuilds: a new worktree's or a close copy's store is seeded from a warm base (the integration store), 
- W2-123 (`DAEO-qzrq`, P0, engineer, in progress): The shared embedding server serves several requests at once within its CPU cap, with the vectors unchanged, an
- W2-131 (`DAEO-r8vq`, P0, engineer, in progress): A register chunk in a bundle carries its own entry's id, not DEC-999 (DEC-1082 (2), a priority fix in re-pin w
- W1-01b (`DAEO-vhad`, P1, independent-test-designer, in progress): W1-01's merge rule: a merge listed in acceptance_exemptions is exempt for its own changes too (DEC-1031 item 3
- W2-00 (`DAEO-sdxk`, P1, orchestrator, open): Wave 2 coordination: the main session's records
- W2-04 (`DAEO-u4oz`, P1, engineer, in progress): gov context bounded and reproducible
- W2-11 (`DAEO-k7hz`, P1, product-spec, in progress): Briefs and the orchestration skill: twelve fields, payload after, two-refusal stop, DEC-430
- W2-66b (`DAEO-zuiy`, P1, independent-test-designer, in progress): W2-66's record-only case reads a PowerShell script under the orchestration folder as code, not as a record (DE
- W2-81 (`DAEO-l78m`, P1, independent-test-designer, in progress): The adoption proving ground: five synthetic repositories with planted problems, a judge, and question sets per
- W2-90b (`DAEO-nqa2`, P1, independent-test-designer, in progress): W2-90's next round: the cases still tied to this repository's live wiring move to the kernel's wiring now that
- W2-94 (`DAEO-g87r`, P1, independent-auditor, open): EXAMIN's question set: memory questions with gold sources about the owner's copy, a visible and a hidden half,
- W2-139 (`DAEO-ongl`, P1, product-spec, in progress): CAP-45.a to Wave 3: the approved CIT-P note applied to the Contract as version 4.3, with its CIT-E, merged in 
- W2-140 (`DAEO-5ce2`, P1, independent-test-designer, in progress): W2-49's acceptance suite revised for Contract 4.3 (CAP-45 and CAP-45.a to Wave 3), written against the approve
- W2-151 (`DAEO-qzca`, P1, product-spec, in progress): MR-1 to MR-6 regenerated from contract.yaml: the master-rule records say what the Contract says (D-6 part 2; D
- W2-40 (`DAEO-6ox0`, P2, research, open): EXP-002: the untested sandbox cases and the harness's hook limits
- W2-66c (`DAEO-btcs`, P2, independent-test-designer, open): W2-66's live-map suite pins ACT-SELECT-FIXES-1's lines: the couplings for the settings, the declared checks, t
**Batch 2**
- W2-126 (`DAEO-jpr0`, P0, engineer, in progress): A machine-wide vector cache keyed by the text: each text is embedded once on the machine, whatever tree, clone
- W2-133 (`DAEO-k4wm`, P0, engineer, in progress): A narrowed or gap-starting register item carries its own entry's id (W2-131's follow-up, DEC-1083, re-pin wind
- W2-93 (`DAEO-6y0x`, P1, independent-test-designer, open): W2-81's held-out half: hidden questions and planted-problem variants per synthetic repository, by an independe
- W2-98 (`DAEO-wi46`, P1, product-spec, open): The spec-writing skill for product-spec: problem, goals and non-goals, KPIs as observable behaviour each with 
- W2-149 (`DAEO-52ku`, P1, engineer, in progress): The independent sessions' launch script: a walled headless session per job from an approved brief (DEC-1101 (2
**Batch 3**
- W2-135 (`DAEO-c4pb`, P0, engineer, in progress): A line over 4,000 characters in a bundle item is sent as its first 4,000, the item marked cut, its lines cited
- W2-148 (`DAEO-xafn`, P1, engineer, in progress): The operator agent: ACTs applied by class from a queue, in a walled session (DEC-1104 (2))
- W2-173 (`DAEO-qz4p`, P2, engineer, open · after the lift): The launch script's follow-ups for the audit: the brief's effort passed to the session, a stop word for writer
**Batch 4**
- W2-05 (`DAEO-0z8c`, P1, engineer, in progress): The git environment of every check, hook and helper; the settings re-sort
**Batch 5**
- W2-13 (`DAEO-zqvn`, P1, engineer, in progress): RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)
- W2-20 (`DAEO-r30l`, P1, engineer, in progress): Machine-wide resource gate
- W2-23 (`DAEO-kmcr`, P1, engineer, open): Adoption safety on a real repository
- W2-42a (`DAEO-03ub`, P1, engineer, in progress): The product's guard reads what a Bash command writes: ACT-GUARD-FIX-3's eight parser lines in src/gov/guard, b
- W2-110 (`DAEO-3r1j`, P1, engineer, in progress): A product's CTO-only install rule: in a generated project the kernel's guard asks the owner only in the CTO's 
- W2-152 (`DAEO-o5x1`, P1, engineer, in progress): gov brief: a filled brief from the ticket and the facts file, refused when the ticket is not READY by code (W2
- W2-37 (`DAEO-6n5k`, P2, engineer, in progress): gov impact
- W2-120 (`DAEO-i89t`, P2, engineer, open): The skill validator refuses a brief without the twelve-field rule and a skill whose front matter carries a per
- W2-170 (`DAEO-61vm`, P2, engineer, open · after the lift): The memory audit's set record: the checks before any search, the drop and void rule, the declaration and the u
**Batch 6**
- W2-52 (`DAEO-siiz`, P1, engineer, in progress): The lite A7 and A10 stage records
- W2-55 (`DAEO-arrl`, P1, engineer, in progress): Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see
- W2-56 (`DAEO-wnnz`, P1, engineer, in progress): gov launch usable for every worker: the code graph in the session's temp folder, the write list, no placeholde
- W2-61h (`DAEO-h2k3`, P1, independent-test-designer, in progress): W2-61's enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independ
- W2-90c (`DAEO-fu3n`, P1, independent-test-designer, open): The cases of W2-90b that need W2-105 (the template's install block removed) or W2-110 (a product's CTO-only in
- W2-104 (`DAEO-drhj`, P1, engineer, in progress): The skill evaluation harness: each skill's three scenarios run on a fresh session and recorded, and every impo
- W2-121 (`DAEO-cb2b`, P1, engineer, open): gov dispatch: one pass a minute keeps the machine full and the work moving without depending on any agent sess
- W2-157 (`DAEO-ozyt`, P2, engineer, open · after the lift): The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills in
- W2-171 (`DAEO-k1e2`, P2, engineer, open · after the lift): The memory audit's measure: the control, the retrieval figures, the judged reader run, the fault rule, the mis
**Batch 7**
- W2-15a (`DAEO-rd0g`, P1, research, open): EXP-003, pass 1: the baseline
- W2-60a (`DAEO-cv58`, P1, engineer, in progress): The role, its skills and its model and effort loaded at launch; the launch record
- W2-111 (`DAEO-qvff`, P1, independent-test-designer, open): The hook-latency cases time the hook's own work: W1-02's, W1-05's and W2-57's p95-under-100-ms cases judge the
- W2-113 (`DAEO-g29a`, P1, engineer, open): An adopted product's CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestr
- W2-115 (`DAEO-emq1`, P1, engineer, open): gov close, the smart close: scoped runs only, a close refused only by a red its own change caused, the culprit
- W2-172 (`DAEO-p8tv`, P2, engineer, open · after the lift): The memory audit's driver and schedule: the cycle through the launch script, the active and stable rule, the d
**Batch 8**
- W2-32 (`DAEO-0pyc`, P1, engineer, in progress): Retrieval components and bounded improvements: model pin, swap by configuration, learning loop; ranked-lexical
- W2-60b (`DAEO-ecac`, P1, engineer, open): One record per session: model, effort, window, tokens, cost, minutes, turns, subagents
- W2-154 (`DAEO-l4gf`, P2, engineer, open · after the lift): The close's serial plugin treats an entry its opt-in lists leave out as not in the run; nightly.sh reports the
- W2-18 (`DAEO-057v`, P4, engineer, open): Pinned install: a product repository runs a fixed release, never the development copy
**Batch 9**
- W2-91 (`DAEO-a3u2`, P1, engineer, in progress): Full embeddings: the root files, the governance overlay and schemas/ embedded; the hidden half, the generated 
- W2-92 (`DAEO-n0wb`, P1, engineer, in progress): The knowledge graph and the code graph as routes of plain-question retrieval: ids, record titles and symbol na
- W2-124 (`DAEO-mb2t`, P1, engineer, open): A rebuild without its semantic store fails named, and adoption finishes and records it: KPI 5 split from W2-12
- W2-134 (`DAEO-m4rq`, P1, engineer, in progress): The memory measure re-anchors line-cited gold in memory for the commit it measures, and never writes the sets 
- W2-146 (`DAEO-f6x3`, P1, engineer, open): The id reader reads every id form a repository declares: a question that names a nonexistent id in any declare
- W2-153 (`DAEO-8s85`, P1, engineer, in progress): The role template delivered at launch: gov launch and the dispatcher pass it as the appended system prompt, re
**Batch 10**
- W2-112 (`DAEO-clon`, P1, engineer, in progress): One reranker serves every session: a shared, on-demand reranker service, with each search falling back to a pr
- W2-128 (`DAEO-t8mp`, P1, product-spec, in progress): The templates: one per role, the ticket and the brief envelope, filled from the ticket and one facts file, del
- W2-129 (`DAEO-q7lk`, P1, engineer, in progress): gov links: one cheap, incremental link-integrity check that finds every unlinked or contradicted record across
- W2-17 (`DAEO-sdhj`, P4, engineer, open): gov update
**Batch 11**
- W2-130 (`DAEO-q8cl`, P1, orchestrator, open): The link clean-up: every drifting decision marked in its own entry (the 87 with no hint first), tickets linked
- W2-136 (`DAEO-p3ln`, P1, engineer, in progress): gov plan: the dependency map from each ticket's writes, needs and waits, the launch batches it proposes, and g
- W2-137 (`DAEO-5emz`, P1, engineer, in progress): The shared reranker's request cap raised, now that memory is released after each request: fewer requests a sea
- W2-150 (`DAEO-ijf5`, P1, engineer, in progress): Memory's import closure free of the gates: E-2's four coupling edges untangled (P1-6 item 1, D-6 part 2; DEC-1
- W2-33 (`DAEO-lrre`, P2, product-spec, open): The three layers' roles and the typed handoff: the CTO, the Senior Engineer, the ticket lead's role file, mach
- W2-100 (`DAEO-uw5h`, P3, product-spec, open): Domain skills A: backend, API, data and security, each the engineer's skill for its area (conventions, a pre-c
- W2-101 (`DAEO-6icv`, P3, product-spec, open): Domain skills B: frontend, UI/UX and DevOps, each the engineer's skill for its area
- W2-158 (`DAEO-8a3f`, P3, engineer, open · after the lift): gov check --structural: one cheap, bounded pass over the declared check families and the new links on a head, 
**Batch 12**
- W2-116 (`DAEO-f58b`, P1, engineer, in progress): The designers' store in the product: a double-buffered store of the integration branch, refreshed after the ni
- W2-145 (`DAEO-2tfd`, P1, engineer, in progress): No private reranker beside the shared service: a search the shared reranker cannot answer stays unranked and n
- W2-147 (`DAEO-zi7s`, P1, engineer, in progress): gov plan breaks a cycle only at a ticket inside it: a ticket outside every cycle keeps all its waits (DEC-1102
- W2-19 (`DAEO-jzvg`, P4, engineer, open): Language-agnostic test commands
- W2-34 (`DAEO-yadm`, P4, engineer, open): gov readiness --generate
- W2-42 (`DAEO-fau3`, P4, engineer, open): Guard: missing role, links, late paths, atomic saves
- W2-45 (`DAEO-neam`, P4, engineer, open): gov check runner semantics and scale
**Batch 13**
- W2-138 (`DAEO-rmhj`, P1, engineer, in progress): The store's commit in every search result, and the worker's check of each item's line hash against its own fil
- W2-141 (`DAEO-xwro`, P1, engineer, in progress): The guard refuses an engineer's search that can reach its own ticket's acceptance folder (Grep, Glob, and Bash
- W2-35 (`DAEO-2keg`, P4, engineer, open): The UX readiness row: approved wireframes, visual checks
- W2-36 (`DAEO-w19l`, P4, engineer, open): gov discover
**Batch 14**
- W2-142 (`DAEO-qskx`, P2, product-spec, in progress): Search again once in the kernel skills: the retrieval skill's step 7 and the discovery skill's line, after the
- W2-155 (`DAEO-ar89`, P4, engineer, open · after the lift): The warm query path profiled against W1-19's 0.5 s budget; a simple cause fixed, or the evidence and options t
**Batch 15**
- W2-88 (`DAEO-2bdu`, P1, engineer, open): Memory for any repository: at adoption, assess any repository however large, plan the refactoring it needs for
**Batch 16**
- W2-15b (`DAEO-swdu`, P1, research, open): EXP-003, pass 2: the final measurement against 99 %
- W2-27 (`DAEO-h4rh`, P1, orchestrator, open): EXAMIN adoption on a copy
**Batch 17**
- W2-28 (`DAEO-csj8`, P1, independent-auditor, open): Independent verdict on the copy
- W2-82 (`DAEO-4k3l`, P1, engineer, open): A Definition of Ready: gov claim checks it, and gov launch refuses a lead on a ticket that is not ready
**Batch 18**
- W2-29 (`DAEO-b926`, P1, orchestrator, open): EXAMIN adoption on the real repository
- W2-156 (`DAEO-ylsh`, P2, engineer, open · after the lift): The runaway brake in the product: a ticket whose measured cost passes twice its projection holds its next laun
**Batch 19**
- W2-30 (`DAEO-60rw`, P1, independent-auditor, open): Healthy-adoption verdict on the real repository
- W2-159 (`DAEO-6lid`, P3, engineer, open · after the lift): The orchestrator's two Stop checks in the product: a turn does not end with the inbox waiter unarmed, nor idle
**Batch 20**
- W2-46 (`DAEO-nn1s`, P1, orchestrator, open): Wave 2 exit run
- W2-160 (`DAEO-fd0p`, P3, engineer, open · after the lift): gov wait and the helper watch in the product: a bounded wait on a job's exit file by pid, and an inbox item wh
**Batch 21**
- W2-47 (`DAEO-jip3`, P1, independent-auditor, open): Wave 2 exit audit, with the audit→repair loop's tests
