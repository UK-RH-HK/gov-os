Owner, 2026-10-30 (chat), verbatim: my decision on AUDIT-GOV-FEATURES-1. Record it as one decision, apply it now, and put it in your prompt, the lead brief and the rules-in-force digest.

1. Option (a), amended: lift every Gov OS feature as a gate on this repository's own development. Tickets close on the audit's 10 practices (§5), nothing more. Nothing is deleted from the product: the lifted features stay built and tested.

2. The guard keeps only four rules: an implementer never writes acceptance tests; no reads of the hidden half of an evaluation set or the held-out material; no reads of secrets; no installs without me. Everything else in the guard is lifted, including the command forms. Bring me the fastest safe way to switch the rest off (an ACT if it needs me).

3. The nightly stays a plain full test run on the integration head; no gov close at night, no report-only gates. A red starts an immediate investigation of why: re-run the failing tests alone, and trace the red to the change and the cause. Then, depending on what you find: a small, clear fix (a typo, a broken name, a one-line slip) is fixed on the spot and reported in the morning package; anything that needs my decision comes to me as a P1 package with your recommendation, and we decide there whether it becomes a new ticket and at what priority, or a fix folded into a current ticket. The red holds no other work while it's being investigated.

4. First, in parallel with memory's quick wins: make test selection work as intended. Scoped selection is a helper, not a gate:
   a. The close script and the leads' selection tool leave your governance files (briefs, prompts, records, the nightly's folder) out of the changed files before choosing tests, so they never widen a run to the full suite. No test-map change and no owner commit: ACT-TESTMAP-1 is no longer needed.
   b. Testing at every level uses the same tool, never an agent's own choice of tests: workers run their own unit tests while building; each lead runs its ticket's acceptance tests plus the affected tests the tool selects (the full suite only when core code changed) before returning; the close runs the same scoped set on the merged code; the nightly runs everything.
   c. Prove it works: run the tool on the current leads' worktrees and show that each comes out scoped, with the suites it chose and why, and the time a scoped close takes against a full one.
   d. Scoped selection stays a product feature, proven for Wave 2's close with the others.

5. Close now, under the 10 practices: W2-71, W2-77, W2-57, W2-03 and W2-26, then every ticket as its practices pass.

6. The order of work, subject to my approval of the plan in item 10:
   a. Memory: finish it and prove it (W2-61's measure after each fix), starting with the quick wins (W2-86, W2-87 and the register-as-one-record defect), then W2-55, W2-04, W2-05, W2-06, W2-13 and W2-15a. As soon as it measurably helps, use it: you at every resume and before decisions, and the leads through their briefs.
   b. In parallel with memory: the roles, skills, templates and briefs (K3: W2-60a, W2-60b, W2-11), so briefs are complete and leads don't miss things. These include the roles the three layers need (item 8).
   c. Then the rest of EXAMIN's minimum.
   The final proof of gov close is on the proving ground (W2-81) and EXAMIN's copy, where it has to work, not by re-closing this repository's tickets.

7. Compact the decisions: produce a short "decisions in force" list (the standing decisions that still apply, each one line), a list of those this decision lifts, and move the superseded ones to an archive section. Don't rewrite history: the full register stays. Sessions load the short list with RESUME HERE.

8. Three-layer orchestration, planned now and started once its foundations have landed. The updated plan in item 10 includes a study of it, covering the rest of Wave 2 and Wave 3:
   a. The structure: you become the master orchestrator, and a sub-orchestrator runs each stream of work that can proceed in parallel (for example memory; roles, templates and briefs; the sandbox; adoption and the proving ground), each with its own leads and agents.
   b. The master keeps the WBS and the coordination between streams: it triggers tickets by their dependencies, runs work in parallel and in series to the most the machine can hold without my reminding it, owns integration and closes, and records decisions (with mine). Each sub-orchestrator runs its stream's tickets, briefs, merge-backs and reviews, and reports to the master.
   c. Its foundations come first, in parallel with each other: working memory (item 6a), and every role defined, with its skills and brief, and loaded at launch (item 6b): the master orchestrator, the sub-orchestrator, and each agent role (lead, test designer, implementer, reviewer and the others). The plan schedules these so they land together; the three layers start only when both have landed.
   d. The study names the streams, which tickets each holds, what can run in parallel and what must wait, how many sub-orchestrators the machine can carry, what each role's brief and skills contain, and how the handovers work, including a fresh session each morning for every orchestrator.
   e. It starts with my approval of the plan, once its foundations have landed, in new sessions. The aim is more work in parallel, and less for each orchestrator to carry through a compaction.

9. How we work together stays as it is; none of it is lifted: decisions that only I can take, and P1s, reach me as packages with a ping as they arise (DEC-949); the morning package carries what happened overnight; every ACT is pinged with its file; every decision I make is recorded in the register and applied under the rule about rules; the status block ends every report; the morning handover to a fresh session stays; my daily push stays.

10. The updated WBS and plan, now, in parallel with items 2 to 5: don't wait for the gates to be lifted or for memory. Send me, as soon as you can, the WBS and the plan for closing the tickets, updated for this decision:
   a. Wave 2: every remaining ticket, in order, which can run in parallel, what each depends on, its estimate, and the new target date for EXAMIN's copy;
   b. deferred to Wave 3: every ticket moved there, with why;
   c. no longer needed now the gates are lifted: tickets that existed only to fix the machinery, with what happens to their built work.
   We'll review it together and I'll approve it. Until I approve it, only items 2 to 5 and memory's quick wins (W2-86, W2-87 and the register-as-one-record defect) go ahead; other new tickets wait.

Report back to me at three separate milestones, each with a ping:
1. The updated WBS and plan (item 10), ready for my review. I expect this one first.
2. The gates lifted and the guard down to its four rules, with test selection proven scoped (item 4c) and the five closes done. If lifting needs a re-pin or anything else from me, send the ACT with this ping.
3. Memory landed and proven, and the roles, skills and briefs landed (items 6a and 6b), so the three layers are ready to start once I approve.
Between milestones, the status block plus at most five lines at each step.
