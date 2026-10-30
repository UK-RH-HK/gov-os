
### DEC-957 — The owner's decisions on ACT 1, ROLES-SPEC-1 and MEMORY-SPEC-MAP: the batch stopped, installs only through the CTO, the 235 tests revised in W2-90, the roles approved with a software company's work order and an escalation rubric, memory's target 95 % (standing)
- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-954, DEC-955, DEC-906, MR-3, MR-4, MR-6 · **Changes:** DEC-954 Q9 (memory's target and readiness); ROLES-SPEC-1's Q5, Q8, Q12; DEC-839 (effort) for the CTO and Senior Engineers; DEC-832 (the skill packs come in Wave 2) · **Basis:** `packages/ACT-1-GUARD.md`, `packages/ROLES-SPEC-1.md`, `packages/MEMORY-SPEC-MAP.md`
- **Decision:**
  - **Before ACT 1:**
    1. stop the four-ticket close batch (W2-57, W2-77, W2-03, W2-26), which tests the head with the register fault; it re-runs on the corrected head in the fresh session after ACT 1;
    2. find and fix why `gov retrieve` answers STORE_MISSING in the main tree;
    3. **the install rule:** only the CTO's own session gets an "ask me"; every other session, leads included, is refused and raises the install as an escalation;
    4. the guard check re-run;
    5. the held work committed, so the main tree is clean for the owner's operator;
    6. the handover written, with every item left for the fresh session;
    7. then ACT 1 is ready, and the orchestrator stops.
  - **ACT 1, option (a), the owner's named decision under DEC-906:** the owner commits ACT 1; then a fresh independent test designer revises the 235 live-wiring tests to judge the kernel's wiring, in a new LITE ticket W2-90, the first lead after ACT 1. Until it lands, closes test on the head from before ACT 1, and the nightly shows the 235 as known reds.
  - **ROLES-SPEC-1:**
    - Q1 to Q4, Q6, Q7, Q9, Q10 and Q11 are approved as recommended. Q6 stands until the owner decides from the research below: the CTO is the only writer of the main tree, and the push stays the owner's.
    - **Q5:** the domain skill packs come in Wave 2, as skills. Frontend, backend, UI/UX, DevOps, security, API and the like are engineers: each loads the engineer role plus its domain skill.
    - **The work order, as in a software company:**
      - **product-spec** develops the spec with research, the Senior Engineer, the CTO and the owner, with the questions and decisions that settle what goes first and what is in or out;
      - the spec's agreed KPIs drive the **independent test designer**, who builds the tests, acceptance tests included, and never reads the code;
      - the **engineer**, whatever its domain, builds the code to fulfil the spec and its KPIs, never to make the tests pass: it may run the acceptance tests and see only pass or fail, never read them. Its "test-driven development" means its own unit tests, never coding to the acceptance tests;
      - the **QA engineer** (today's independent auditor) is the only one who reads both. It changes neither, writes only its findings report in its allowed path, checks both against the spec and the KPIs, and escalates an unresolved bug to the Senior Engineer, then the CTO and the owner.
    - **A research session now:**
      - the roles and skills a software company uses, from the CTO down: which roles and skills are missing (the QA engineer among them), what each skill should contain, and best practice;
      - who integrates (whether the Senior Engineer integrates its stream's tickets and the CTO integrates across streams), and who may push;
      - benchmarking against software companies' best practice and tools on the market, as a skill of the research role.

      It reports to the owner with insights to decide from; the roles land in Wave 2.
    - **Q8:** a fresh session every morning for every orchestrator, the CTO included.
    - **Q12:** the CTO loads its own skill at launch and has every other role's skills available on demand; Senior Engineers and leads load their own part.
    - **Effort:** the CTO and the Senior Engineers at high; the highest effort only for reviewers and auditors, when needed.
    - **The escalation rubric, for the three layers** (in the roles spec, the playbooks and the briefs):
      - **P3,** the Senior Engineer decides and logs it: reversible; inside one ticket's scope and paths; no change to the spec, the KPIs or any standing decision; no effect on other streams; a delay under half a day.
      - **P2,** the Senior Engineer decides and the CTO approves: it touches another stream or shared code; changes a ticket's scope or KPIs within the approved spec; changes the plan's order; delays a milestone by up to a day; or revises older tests under an existing decision.
      - **P1,** the lead and the Senior Engineer recommend, the CTO amends or escalates, the owner decides: it changes the spec, the Contract, the Charter or a standing decision; weakens any of the five guard rules or anything that fails open; is irreversible or destructive; concerns secrets or security; involves cost, installs or paid services; touches memory's target or acceptance; EXAMIN's go; any ACT; a milestone slipping more than a day.
      - **Emergency:** a secret exposed, a risk of losing data, the disk below its floor, or the guard failing open: stop the affected work at once, then P1.
  - **MEMORY-SPEC-MAP:**
    - **The target is 95 % or more; 85 % is the floor worked with.** If 85 % is reached and room for improvement is found and possible, memory is not closed: an escalation to the owner, who decides.
    - **All seven gaps are resolved before memory is called ready:**
      - full embeddings (the root files, `governance/**` and `schemas/**`; the hidden half and generated copies stay out);
      - a ticket for the knowledge-graph and code-graph routes in ordinary questions;
      - the store layout;
      - the large-repository measure;
      - W2-81's hidden half;
      - EXAMIN's question set.

      Together with the 48-question measure, judged on the hidden half (at least 21 of 24), the combined retrieval and search, and W2-88's tools that assess, plan refactoring, build the stores, index and embed an adopted repository.
  - **Then:** after ACT 1, the handover; the fresh session starts under the five-rule guard with W2-90 first.
- **How it is applied (this session):**
  - The batch was stopped at 21:19 GMT, during its full parallel run (28 processes, by process id); its clone under `~/gov-os-runs/W2-00/close/` is left for the fresh session to remove (the guard refuses the orchestrator's writes there).
  - STORE_MISSING: the main tree's store had been built by code older than W2-03's merge (no `span` column in `records`); `gov retrieve`'s query failed and the failure reads as STORE_MISSING. The store was rebuilt with the current code. The missing store-layout version is the "store layout" gap (W2-88).
  - The hook's install rule asks only for the orchestrator role on the coordination ticket W2-00; 38 of 38 planted cases pass.
- **Where it goes (DEC-851):** this register; the prompt §0 (v3.47); the common lead brief (the rubric, the work order, installs); the roles spec (the owner's answers and the rubric); the decisions-in-force list; RESUME HERE; the memory spec map.

| Version | Date | Change |
|---|---|---|
| 0.340 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-957 (the batch stopped before ACT 1; STORE_MISSING fixed by a rebuild; installs ask only in the CTO's session; ACT 1 (a) with W2-90 for the 235 tests; ROLES-SPEC-1 approved with the domain skill packs in Wave 2, a software company's work order, a roles research session, a fresh session daily for every orchestrator, the CTO's skills on demand, effort high for the CTO and Senior Engineers, and the P3/P2/P1/emergency rubric; memory's target 95 % with 85 % the floor, and all seven gaps closed before memory is ready). Next free id: DEC-958. |
