Owner, 2026-10-30 (chat), verbatim: my approval of PLAN-W2-DEC953, with these answers and amendments. Record it as one decision, update the WBS and the plan, and apply it now.

Q1. EXAMIN's copy is gated by milestones and core tickets closed, not by a date: it starts only when K9's entry criteria are met (memory proven, the roles, skills and briefs landed, the proving ground passed, and the rest of the minimum closed). The dates in the plan are estimates only, re-estimated weekly. No adoption on a weak Gov OS because a date arrived.
Q2. The 10 built tickets are finished after ACT 1 (Q8 a), not before: once the new guard with its five rules is switched on. From then on, each is finished and closed on the 10 practices, under the five-rule guard.
Q3. Yes: W2-85 goes ahead.
Q4. Yes: the register-as-one-record fix stays inside W2-87.
Q5. W2-76: finish and close. W2-78: parked, as P-W2-78-PARK (a) recommends; file its discoveries as rows.
Q6. Yes: re-scope W2-33, and re-scope it well for the three layers (see Q13 and the roles spec below).
Q7. Yes: one combined CIT-P for the four K3 tickets. Quality first; no extra work for its own sake.
Q8. Two acts from me, no re-pins for gates:
   a. ACT 1, at milestone 2: switching on the new five-rule guard (the settings regeneration). After it, the 10 built tickets are finished and closed, and the plan's streams run in parallel (memory, roles with skills and briefs, the sandbox, adoption and the proving ground).
   b. ACT 2, once memory, the roles with their skills and briefs, and the three layers' foundations have landed: one re-pin, so all of them take effect together. The roles are built on an approved spec, never on a sketch. Your own company map shows the gaps: no role file for the ticket lead, no machine-readable defaults per role, and nothing yet for the CTO and the Senior Engineers beyond the sketch in the plan's three-layer study. So you write the roles spec first (below), I approve it, and only then do the tickets build it. W2-60a's last round is already scoped (its fail-open fix) and finishes meanwhile. The foundations are then built before ACT 2, in the roles stream (S2): the CTO's and the Senior Engineers' roles, skills and briefs, the coordination tickets per stream, and the CTO's watchers. After ACT 2, the three layers start working, in new sessions: the CTO and a Senior Engineer per stream.
   c. A release through W2-16: a numbered, frozen version of the Gov OS that the proving ground (W2-81) and EXAMIN's copy install, so they are governed by a fixed, tested version, never by this repository's moving branch.
Q9. The 20-question measure is approved as memory's measure (EXP-003), with these amendments:
   a. Enlarge the question set, to about double or up to 50 questions, for better coverage; propose the size with its time cost, and keep a visible and a hidden half.
   b. The hidden half is protected from every worktree (W2-84's fix) in the new guard hook before it is used.
   c. The measure that counts is the one taken on the combined memory spec: semantic and lexical search, full indexing, full embeddings, the knowledge and code graph, and the right structure in SQLite and the vector store. Measure along the way to guide the work, but judge memory on the combined whole.
   d. Map the memory spec to the tickets: does the plan cover full indexing and embedding of this repository, the knowledge and code graph, the database structure, and the tools that build the indexes and embeddings in an adopted repository? List any part with no ticket, and why it's missing. It's the core of the memory spec.
   e. If memory is below 85% after two improvement rounds, escalate to me with the reasons. At the third, I decide: a discovery and research ticket, benchmarking against tools on the market, in a separate worktree; accepting the level reached; or another course.
   f. Memory for any repository, not only this one: if we build memory that only this repository can use, we have built nothing. If Wave 2 has no ticket for it, file one in Wave 2's minimum: the tools that, at adoption, assess any repository (however large), plan any refactoring it needs so that the whole repository can be indexed, build the full index and the embeddings, and set up the database structure (SQLite and the vector store), so memory works there. Refactoring is planned and proposed as governed tickets for the repository's owner to approve, never applied on its own. Prove it on: the proving ground's synthetic repositories (W2-81); two real, messy public repositories from GitHub, of different languages and sizes; and any test repository path named earlier in the register. EXAMIN's copy is its live trial.
Q10. Let the related tickets finish (scoped tests, W2-76, W2-06), then measure what uses the machine, broken down by kind (Claude sessions, test runs, rebuilds, gitleaks, git, the code graph, Ollama), and we decide from that.
Q11. W2-67: its remaining rounds go soon after memory's quick wins, for speed.
Q12. W2-20: in Wave 2, built on my measured rule (DEC-950) for this machine, to speed up Wave 2. In Wave 3, scoped to be machine-agnostic: on any machine, the Gov OS reads its resources (CPU, memory, disk, GPU) and plans the execution to that capacity.
Q13. Yes: a coordination ticket per stream, so both the guard and the master know each sub-orchestrator's identity. Also:
   a. The names: the master orchestrator is the CTO; each sub-orchestrator is a Senior Engineer for its stream, with the skills its stream needs; the agents keep their role names, and any role not yet defined is scoped and drafted in its ticket.
   b. The CTO's watchers track every Senior Engineer's state (working, idle, waiting for a decision), so none sits idle waiting unnoticed: the CTO acts or escalates to me.

The roles spec, before building: nothing is built on a weak spec. Before W2-60b, W2-11, W2-33 and W2-83 build further, write a roles and briefs spec for my review and approval:
   a. what already exists and where (the Contract's capabilities, the kernel's role files, skills and brief templates, the tickets' KPIs);
   b. every role, from the CTO and the Senior Engineers to the ticket lead, test designer, implementer, reviewer, auditor and the others: what it does, what it may read and write, its skills, its model, what its brief must always contain, and how it hands over to the next;
   c. the gaps: anything missing or only sketched (at least the ticket lead's role file, machine-readable defaults per role, the CTO and the Senior Engineers), and which ticket fills each.

P-W2-64-1: (a). A fresh independent test designer corrects the 203 earlier fixtures that the real schemas refuse, lowering no expectation, with Rewrite-Reason: DEC-872 item 2; this is my named decision under DEC-906. Verify the correction with a scoped run of the corrected tests only: if they turn green, that is enough. No full run; the nightly covers the rest.

The test lock: closes take it ahead of any lead's full run.

The guard: a fifth rule, added to DEC-953 item 2's four. Independent reviewers and auditors write only their own outcomes (their review and audit records), in the review and audit paths allowed to them. They never change code, tests, tickets, records, handovers or anything else. Put it in the new guard hook with the other four, test it with planted cases (a reviewer or auditor writing its own record passes; writing anywhere else is refused), and switch it on with the other four in ACT 1.

Also approved: section 6's exit-criteria and WBS edits, and the 19 deferrals to Wave 3. Start the streams as the plan sets out, within the resource gate.

So it isn't lost: write this plan ahead into RESUME HERE and the checkpoint now, in this order: ACT 1 (the five-rule guard), then the 10 built tickets and the streams in parallel; the roles spec first, for my approval, before the roles tickets build further; memory landing, both for this repository and for any adopted repository (Q9 f); the roles landing; ACT 2 (the re-pin); then the three layers in new sessions; and EXAMIN only when K9's criteria are met. Every new or compacted session reads it there. Confirm in your next reply that it's written, with the commit.

Milestones 2 and 3 are reported with a ping, as before; ACT 1 comes with milestone 2, and the roles spec comes to me as soon as it's ready.
