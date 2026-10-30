# ROLES-RESEARCH-1: a software company's roles and skills, who integrates, who pushes, and benchmarking

For the owner (DEC-957, "a research session now"). Read-only research; nothing has been filed or changed.

## Insights: the five things most worth your attention

1. **Your work order matches industry best practice, with one gap.** Tests written separately from the code, and a QA role that reads both, is what ISTQB calls "high independence" [S15]. Google also requires separate approvals from a peer, an owner and a style reviewer [S10]. The gap: ISTQB warns that independence can leave developers "losing their sense of responsibility for quality" [S15]. Your rule already covers this, because the engineer writes its own unit tests. Keep that line in every engineer skill.
2. **The "QA engineer" is two industry roles, and the repo has three files for them.** In industry, a QA engineer checks each change against its requirements, while an auditor checks a whole milestone against the standards. My recommendation:
   - make **QA engineer** the per-ticket role, and fold in the planned `independent-reviewer`, scaled to the ticket's profile;
   - keep the **independent auditor** for milestone audits (MR-4).
   This takes the per-ticket check "the tests against the KPIs against the code" off the CTO, who today does it alone and by hand.
3. **Merging is not the CTO's bottleneck; record-keeping is.** In the last 7 days:
   - 24 ticket merges went into `w2/integrate`, about 3 a day, with no commits mentioning conflicts;
   - about 200 of the 230 commits on the branch carry `Role: orchestrator`, 51 of them decision records.
   Stream branches would add a second merge layer and long-lived branches, which DORA advises against [S4], and they would not lighten the CTO's real load.
4. **Test before merging, not after.** close_build.py clones `w2/integrate` after the ticket has merged, so a red result leaves the shared head red until someone repairs it. The "not rocket science rule" behind every merge queue is: test the merged result first, then advance the branch only if it is green [S1, S2, S7]. This is a small change to an existing tool and keeps the integration branch green.
5. **Most company job titles are skills, not roles.** Frontend, backend, security, DevOps, technical writer, release engineer and build sheriff differ in method, not in rights. Only four new kinds of rights are needed: Senior Engineer, ticket lead, QA engineer, and (already there) the auditor. Everything else is a skill, written to Anthropic's skill-authoring guide [S20]:
   - a short checklist;
   - inputs and outputs;
   - escalation;
   - three test scenarios written before the skill text.

---

## 1. Context in plain words

**What exists today**
- **Six role files** in `template/governance/kernel/roles/`: `orchestrator.md`, `engineer.md`, `independent-test-designer.md`, `product-spec.md`, `research.md`, `independent-auditor.md`. The ticket lead is a section inside `orchestrator.md`. None of the six has the defaults block yet (ROLES-SPEC-1 §2.2).
- **Ten skills** in `template/governance/kernel/skills/`: orchestration, checkpoint, retrieval, test-design, audit, planning, change, discovery and adopt, plus three vendored "superpowers" skills (737 lines, loaded by the engineer).
  - Most cite a decision id on every line and read as rule lists.
  - Few have a step checklist, a "done when" test or an escalation section.
- **The approved roles spec**, `governance/project/orchestration/packages/ROLES-SPEC-1.md`, plus your answers in DEC-957:
  - CTO, Senior Engineer per stream, ticket lead, workers;
  - the planned tickets W2-33 r1/r2, W2-11 r1/r2, W2-60b, W2-83a/b, W2-89 and W2-00a/b/c.
- **Integration today** (DEC-235, DEC-236, DEC-720, DEC-848, DEC-861):
  - leads work on `w2/<W2 id>` branches in their worktrees;
  - only the CTO merges into `w2/integrate`, with `--no-ff`;
  - `.gov-runtime/scratch/orchestrator/tools/close_build.py` then clones the integration head and runs the scoped tests;
  - you push daily, and your push is the acceptance (DEC-861).
- **The hard boundary** (ADR-0001, `docs/adr/ADR-0001-threat-model.md`): git history never rewritten, the pre-push gate, CI, and "only the owner merges [to main], only on green". ADR-0001 guards against honest mistakes, not adversaries; this report is judged in that proportion.
- **The work order and escalation rubric** (DEC-957, prompt §0): product-spec, then the test designer, then the engineer, then the QA engineer; P3, P2, P1 and Emergency.

**What the Charter promised** (Charter v5 §4 MR-5, §6): a company of 22 role agents, including architecture, UX, frontend, backend, data, API, AI/ML, DevOps/SRE, security, performance, test execution, integration, change controller, memory, tooling and release. DEC-832 made four of them skill packs and deferred four. DEC-957 Q5 makes every domain specialist "an engineer plus its domain skill".

---

## 2. What I found, role by role

Each entry gives: the industry role (with sources), what it reads and writes, its skills, and how it maps to this repo.

**What every skill file should contain.** These are Anthropic's authoring rules [S20], applied to this repo:
- front matter with name, version, and a third-person description saying what it does and when to use it;
- **When / not when**;
- **Inputs:** what to read first;
- **Steps:** a checklist the agent copies and ticks;
- **Done when:** a check, then fix, then check again;
- **Output and handover:** the twelve fields and the typed handoff kind;
- **Escalation:** mapped to P3/P2/P1/Emergency, and to whom;
- **Never:** reminders only, since the guard decides;
- **Sources:** decision ids at the end, not on every line.

Keep the body under about 150 lines (Anthropic's ceiling is 500) and put details in reference files one level deep. Write three test scenarios before the text and run them on a fresh session before promotion. That is Anthropic's "evaluation-driven development", and it fits CIT-P/CIT-E.

### 2.1 CTO (master orchestrator)

- **Industry:** sets technical strategy and structure, owns delivery and operations, and is the last escalation step before the business owner. Larson's *Engineering Executive's Primer* names these as the CTO's core work. The SRE incident model adds that one person "holds the high-level state" and hands off explicitly [S14].
- **Duties here:** as in ROLES-SPEC-1 §3.1. Added by this research:
  - owns the merge queue (§4);
  - runs the nightly as the build sheriff (Chromium's sheriffs keep the tree "green and open" [S8]);
  - is incident commander for Emergencies;
  - is release manager for W2-16's frozen release. The tag stays yours.
- **Reads:** everything outside the five rules. **Writes:** the main tree's tracked files: records, merges, closes.
- **Skills:**
  - `orchestration` (CTO part; already planned to split, W2-11 r2), with three reference files:
    - `integration-queue`: enqueue, test the candidate merge, advance or eject, record;
    - `nightly-sheriff`: re-run the red alone, bisect to the change, fix small things or send a P1;
    - `incident-response`: stop, contain, P1, a live handoff, a blameless note;
  - `release` (W2-16): freeze, version, changelog, provenance note, tag request to you;
  - `planning`, `checkpoint`, `change`, `retrieval`; other roles' skills on demand (Q12).
- **Gap:** the three reference files and `release` are missing.

### 2.2 Senior Engineer (stream lead)

- **Industry:** this is the "Tech Lead" archetype: it "guides the approach and execution of a particular team", sets direction, scopes work and clears blockers [S18]. In GitLab's model it is the **maintainer**: "the DRI for ensuring MRs reasonably meet acceptance criteria", taking "responsibility alongside the author" [S12].
- **Duties here:** ROLES-SPEC-1 §3.2, plus the maintainer's gate. Before READY_TO_CLOSE it checks:
  - the QA engineer's report is clean or its findings are dispositioned;
  - the lead's return meets the 10 practices;
  - the paths do not overlap another stream's.
  It decides P3s and logs them, and proposes P2s (DEC-957 rubric).
- **Reads:** everything outside the five rules. **Writes:** its stream folder only (Q6, as approved).
- **Skills:** `stream-orchestration` (planned), with a maintainer-review checklist, a P3 decision log, a dependency and overlap check, and the morning stop; `checkpoint`; `retrieval`.
- **Gap:** role file, skill and brief (G4, G7, G8, already ticketed).

### 2.3 Ticket lead

- **Industry:** close to a feature owner or "directly responsible individual" for one change: it drives the change through review and checks, but does not own the trunk [S12].
- **Duties, reads and writes:** as ROLES-SPEC-1 §3.3.
- **Skills:** `ticket-loop` (planned), `checkpoint`, `retrieval`.
- **Change from this research:** the loop's last worker step is the QA engineer at every profile, scaled down for LITE (§2.9).

### 2.4 Product-spec (product manager plus spec writer)

- **Industry:**
  - the product manager owns the problem, goals and non-goals, and success measures;
  - Google's design docs record context, goals, **non-goals**, the alternatives considered and trade-offs, and "rarely contain code" [S30];
  - Scrum adds a shared **Definition of Done** [S36].
  You are the product owner; product-spec is the PM and spec writer.
- **Duties (DEC-957):** develops the spec with research, the Senior Engineer, the CTO and you. It writes the KPIs: the testable success and failure lines.
- **Reads:** everything. **Writes:** the ticket's paths.
- **Skills:**
  - `spec-writing` (new): problem; users and scenarios; goals and non-goals; KPIs written as observable behaviour, each with a failure line; out of scope; open questions as packages; acceptance by whom. Its "done when" check: every KPI is testable without naming code;
  - `technical-writing` (new): Diátaxis's four kinds (tutorial, how-to, reference, explanation) [S29];
  - `planning`, `change`, `retrieval`.
- **Gap:** `spec-writing` is missing. Today the discovery skill lists only the order of work.

### 2.5 Research

- **Industry:** spikes, bake-offs and technology radars. Thoughtworks' rings are Adopt, Trial, Assess and Caution, and something reaches Trial only "with production experience" [S26].
- **Reads:** everything. **Writes:** one experiment folder.
- **Skills:** `discovery` (exists), plus `benchmarking` (new; sketched in §5.3).
- **Gap:** `benchmarking`.

### 2.6 Independent test designer (SDET / test analyst)

- **Industry:** ISTQB's "testing role": test analysis, design, implementation and execution [S15]. Google calls it Software Engineer in Test. Microsoft retired its SDET title in 2014 and folded testing into engineering [S17]. Atlassian made QA a coaching role, with developers owning their tests [S16].
- **What this repo keeps:** it keeps the separation those companies dropped. That is right here, because the builders are models and the main failure is "coding to the tests" (DEC-957).
- **Reads:** the spec, the KPIs and existing code; never this ticket's code. **Writes:** `tests/acceptance/**` (rule 1).
- **Skill:** `test-design` (exists). Add:
  - ISTQB's black-box techniques: equivalence partitions, boundary values, decision tables, state transitions;
  - red-first;
  - the proportion rule;
  - a README mapping each KPI line to its tests, written so the opaque runner (§5) can report pass or fail per KPI line.
- **Gap:** red-first and the techniques (ROLES-SPEC-1 §2.3 already notes red-first).

### 2.7 Engineer, plus domain skills

- **Industry:** the IC ladder (Microsoft's ISE playbook expects engineers to own tests, reviews and documentation [S19]). Domain specialists share the same rights and differ by practice.
- **Reads:** everything except this ticket's acceptance-test code. **Writes:** the ticket's paths.
- **Skills:** the three vendored skills (TDD, debugging, verification), which are its own unit tests, plus one domain skill per ticket (DEC-957 Q5). Each domain skill should hold:
  - the area's conventions (naming, layout);
  - a pre-commit checklist;
  - the unit-test focus for the area;
  - its common mistakes;
  - "escalate when".
  The seven domains, with the main points each checklist should cover:
  - **backend:** error handling, idempotence, migrations;
  - **API:** contract-first, versioning, backward compatibility;
  - **data:** schema changes, migration and rollback, data quality;
  - **security:** OWASP-style input checks, secrets never in code, least privilege; any finding is a P1 (DEC-957); NIST SSDF's four groups as the frame: prepare, protect, produce well-secured, respond [S27];
  - **frontend:** accessibility, state, browser support;
  - **UI/UX:** user flows reviewed by you as scenarios, not code (discovery skill, DEC-103);
  - **DevOps:** hermetic builds, pinned versions, rollback (SRE release engineering principles [S13]).
- **Gaps:**
  - all seven domain skills;
  - an **opaque acceptance runner**. Your rule says "sees only pass or fail", but pytest prints test names and assertion values. A small `gov`-level runner that prints only pass or fail per KPI line would give it effect. Under ADR-0001 that is enough; no guard rule is needed.

### 2.8 Reviewer (code review)

- **Industry:** Google's standard is to approve once a change "definitely improves the overall code health" [S9]. Google requires three approvals: a peer's LGTM, an owner's, and readability [S10]. GitLab uses a reviewer, then a maintainer, and "the last required approver merges" [S12]. CODEOWNERS routes reviews by path [S11].
- **Mapping:** in this repo the peer review is the FULL probe (`independent-reviewer`, planned), and the owner approval is the Senior Engineer's maintainer gate.
- **Recommendation:** fold the probe into the QA engineer (§2.9), so there is one checking role with one guard class ("reviewer", rule 5).

### 2.9 QA engineer (new; what the industry calls QA)

- **Industry:** ISTQB says independent testers "verify, challenge, or disprove assumptions made by stakeholders", and warns about isolation and bottlenecks [S15]. Atlassian's quality engineers work on preventing defects and coaching, not only catching them at the end [S16].
- **Duties here (DEC-957):** the only role that reads the spec, the KPIs, the tests and the code. In five steps:
  1. builds a trace: each KPI line, the tests that cover it, the code behind it;
  2. checks the tests against the spec: missing failure lines, weak assertions, tests that pass for the wrong reason;
  3. checks the code against the spec: behaviour the tests miss, out-of-scope writes, fail-open guards (today's FULL probe, DEC-137, DEC-498);
  4. runs exploratory probes in proportion: LITE a short trace check, STANDARD trace plus key probes, FULL a full probe at max effort;
  5. writes findings only, each in JUDGEMENT.md's two-line form.
  An unresolved bug goes to the Senior Engineer, then the CTO, then you.
- **Writes:** its findings report only (rule 5).
- **Skill:** `qa-review` (new). Steps as above, a severity scale tied to P3/P2/P1, and "done when" every KPI line is traced or flagged.
- **Gaps:**
  - the role file: rename W2-33 r2's planned `independent-reviewer.md` to `qa-engineer.md`;
  - the skill;
  - the guard's reviewer set and `KNOWN_ROLES` gain `qa-engineer` (W2-60b).

### 2.10 Independent auditor

- **Industry:** internal audit and compliance: whole-system fidelity to standards and decisions, by someone who did not write the work. SLSA's top source level asks for two-party review of every change [S28], which is the same separation-of-duties idea.
- **Here:** unchanged (MR-4): milestone and wave-exit audits, read-only, writing its report. **Skill:** `audit` (exists). Add the judgement rules (ROLES-SPEC-1 G15).

### 2.11 Release engineer / DevOps / SRE

- **Industry:** release engineering's principles are self-service, high velocity, hermetic builds and enforced policies, with gated actions such as "creating a new release" [S13]. Incident roles are command, operations, communication and planning [S14].
- **Here:**
  - release is a CTO skill (W2-16's frozen release), with the tag yours;
  - DevOps work on tickets is an engineer plus the `devops` skill;
  - the build sheriff is the CTO's `nightly-sheriff` reference file.
- **No new role file:** none of these needs different rights.

### 2.12 Security

- **Industry:** application-security reviews of designs and risky changes, threat modelling, the NIST SSDF [S27], and supply-chain checks such as SLSA [S28] and the OpenSSF Scorecard (branch protection, code review, pinned dependencies) [S33].
- **Here:** security-flagged tickets get an engineer with the `security` skill. The QA engineer loads the same skill for its review. Secrets and security are P1 (DEC-957), and gitleaks is already a close practice. No role file.

### 2.13 Architect

- **Industry:** owns a central technical area's direction ("Architect" archetype [S18]); writes design docs [S30] and ADRs.
- **Here:** DEC-832 deferred this to Wave 3, and this repo already writes ADRs (`docs/adr/`). Keep it deferred; an `architecture-review` skill for FULL tickets can come in Wave 3.

### 2.14 Technical writer

Product-spec with the `technical-writing` skill. No role file.

### 2.15 Others a company has: mapping only

- **Engineering manager / scrum master** (flow, blockers, retros): split between the Senior Engineer (flow) and the CTO (the watchers, learning metrics, brief gaps).
- **Test execution and integration roles** (CAP-22.c): become two tools, not roles: the opaque runner and the merge queue.
- **Performance, AI/ML, data author:** Wave 3, as decided.

**What the industry adds that this repo lacks.** Every role above gives the same answer: rights by role, method by skill, one integrator per trunk, and testing before merging.

---

## 3. Why it matters for the Gov OS

The Gov OS sells governed, multi-agent delivery: accurate, bounded and traceable (ADR-0001). Three things follow.

- **Separation is the product.** Multi-agent research systems show that separate agents with clear objectives, output formats and boundaries outperform single agents, at about 15 times the tokens of a chat [S22]. Published "software company" agent systems also use roles with procedures and reviewers:
  - MetaGPT's standard procedures [S23];
  - ChatDev's chat chain [S24];
  - Agyn's manager, engineer, reviewer and researcher (72.2% on SWE-bench Verified; one team's figures, not independently replicated) [S25].
  The QA engineer and the opaque runner put your separation into the product, not just the briefs.
- **Each extra role costs context and money.** Only add a role where its rights differ. Skills load on demand, and only their descriptions are always present [S20]. Fewer role files means fewer guard classes and less drift to test.
- **An adopter will compare the Gov OS with how real companies work.** If its roles match recognised practice (ISTQB, DORA, Google and GitLab review, SRE), EXAMIN and later adopters can read it without a glossary.

---

## 4. Options for integration and push

**The facts the options are judged on:**
- about 3 ticket merges a day, no conflict commits, and 54 merge-backs of `w2/integrate` into ticket branches in 14 days;
- test runs are the scarce resource on this machine (the test lock, closes first);
- tests run after the merge today;
- DORA: three or fewer active branches, merge at least daily, no code freezes [S4];
- hosted merge queues need GitHub Enterprise Cloud for private repositories (at least when the feature came out in 2023) [S34] or GitLab Premium [S2]: a paid service, so P1.

### (a) Today: the CTO alone integrates; the owner pushes
- **Consequence:** one writer and a simple record. The CTO verifies by hand and merges before testing.
- **Cost:** nothing new.
- **Risk:** a red close leaves `w2/integrate` red until it is repaired. With three Senior Engineers sending READY_TO_CLOSE in parallel, the CTO's hand checks become the queue.
- **Changes:** none.

### (b) Stream branches: the Senior Engineer integrates its stream; the CTO integrates across; the owner pushes
- **Consequence:**
  - three more long-lived branches, five or more active in all;
  - conflicts found at the cross-stream merge, later than today;
  - two clean-clone test runs per ticket (stream, then integration) on a machine whose test lock is already the constraint.
- **Cost:** stream-branch tooling, a second close form, merge-backs at two levels; about 1.5 to 2 days of work, plus ongoing test time.
- **Risk:** against DORA's guidance [S4] and the trunk-based model [S3]. It reverses Q6 (the Senior Engineer would write tracked files); a second writer in the main tree needs guard classes and new git discipline. It is hard to undo once streams diverge.
- **Changes:** roles spec Q6, the Senior Engineer's writes and guard class, `stream-orchestration`, close_build, the brief and the WBS.

### (c) A local merge queue: Senior Engineers enqueue; the CTO's tool tests each candidate merge, then advances the branch; the CTO approves exceptions; the owner pushes
- **How:**
  - the Senior Engineer's READY_TO_CLOSE handoff is the enqueue, made after its maintainer gate;
  - the CTO's tool, in a clean clone, makes the `--no-ff` merge of the ticket onto the current head, runs the scoped tests under the lock, and on green fast-forwards `w2/integrate` to that tested merge commit (`--ff-only`). The same commit is tested and landed, so DEC-848's `--no-ff` holds;
  - on red it ejects the ticket back to its Senior Engineer with the failure output; the head never goes red;
  - the CTO approves only P2 items (cross-stream or shared code, DEC-957), and the tool merges the rest in order.
- **Consequence:** "the not rocket science rule" [S7] and what GitHub and GitLab do [S1, S2], built locally at no service cost. One writer stays; nothing is approved by hand that the rubric does not need.
- **Cost:** a change to close_build.py (test before advancing; queue file read from the stream folders; eject handoff), about 4 to 6 hours, STANDARD.
- **Risk:** low. While a merge is under test, a new head means a re-test; at about 3 merges a day this is rare. If a hosted queue is ever wanted, that is a P1 cost decision.
- **Changes:** CTO skill `integration-queue`; the Senior Engineer's READY_TO_CLOSE becomes the enqueue; the 10 practices' "tests on the merged commit" now runs *before* the branch moves; the SE brief and the common lead brief gain one line each.

### (d) Delegated merge: each Senior Engineer merges its own stream into `w2/integrate` under one lock; the CTO keeps the records
- **Consequence:** like GitLab's "last approver merges" [S12]; less CTO work per ticket.
- **Cost:** guard and brief changes; three writers on one branch.
- **Risk:** reverses Q6. Interleaved commits from three sessions in one tree break "never two writing sessions in one tree" (DEC-254) unless each merges from its own clone. The gain is small at 3 merges a day.
- **Changes:** as (b), slightly less.

### (e) Push variant, alongside any of the above: the CTO pushes `w2/integrate` after the pre-push gate; you keep `main`, tags and release
- **Consequence:** your daily push stops being a chore; the boundary stays at `main`.
- **Risk:** it changes DEC-861 ("the owner's push is the acceptance") and ADR-0001's boundary reading. Pushing is an irreversible public act on a private repository: P1 by the rubric.
- **Recommendation:** not now. Revisit in Wave 3 if your push is ever the reason work waits.

---

## 5. Recommendation

### 5.1 Integration and push

- **Option (c), the local merge queue, with the owner's push unchanged.**
  - The Senior Engineer is its stream's maintainer: it gates.
  - The CTO's tool is the only integrator: one writer, test before landing.
  - You push.
  - Confidence **medium-high**: the evidence fits it well, and it is reversible. It is a step from (a) towards industry practice, not a jump.

### 5.2 Questions for you

- **RR-Q1:** integration by option (c)? Recommended: yes (medium-high).
- **RR-Q2:** the push stays yours (option (e) not now)? Recommended: yes (high).
- **RR-Q3:** the QA engineer becomes the per-ticket checking role at every profile, taking in W2-33 r2's planned `independent-reviewer`, while the independent auditor keeps milestone audits? Recommended: yes (medium-high).
- **RR-Q4:** domain skills (seven) land in Wave 2 *after* ACT 2, so they do not hold up the three layers? Recommended: yes (medium).
- **RR-Q5:** every new or changed skill follows one template with three test scenarios written first? Recommended: yes (medium-high).
- **RR-Q6:** an opaque acceptance runner gives "only pass or fail" its effect, with no new guard rule? Recommended: yes (medium).

### 5.3 Missing roles and skills: proposed tickets (none filed)

**Folded into existing tickets** (the order is unchanged):
1. **W2-33 r2 change:** `qa-engineer.md` replaces `independent-reviewer.md`; every role file states the DEC-957 work order in one line. Small (+0.5 h).
2. **W2-60b change:** `qa-engineer` added to `KNOWN_ROLES` and the reviewer set. Small (+0.5 h).
3. **W2-11 r1 change:** the skill template (the sections listed at the start of part 2); `test-design` gains red-first, the ISTQB techniques and the KPI-mapped README. STANDARD, +2 h.
4. **W2-11 r2 change:**
   - `stream-orchestration` gains the maintainer checklist and the P3 log;
   - the CTO's `orchestration` gains the `integration-queue`, `nightly-sheriff` and `incident-response` reference files;
   - a new `qa-review` skill.
   STANDARD, +4 h.

**New tickets:**
5. **Merge queue: test the candidate merge, then advance `w2/integrate`; eject on red.** Project tool (close_build.py). STANDARD, about 4 to 6 h. Before ACT 2.
6. **Opaque acceptance runner: pass or fail per KPI line for the engineer.** Product code. STANDARD, about 4 to 6 h. Before ACT 2 if you want it in force for the three layers; otherwise just after.
7. **`spec-writing` skill for product-spec** (problem, goals and non-goals, KPIs with failure lines, open questions as packages). STANDARD, about 3 h, CIT-P with the K3 batch.
8. **`benchmarking` skill for research.** STANDARD, about 3 h (sketch below).
9. **Domain skills A: backend, API, data, security** (DEC-832's four). STANDARD, about 1.5 days, after ACT 2.
10. **Domain skills B: frontend, UI/UX, DevOps.** STANDARD, about 1 day, after ACT 2.
11. **`release` skill for the CTO** (W2-16's frozen release). LITE, about 2 h, with W2-16.
12. **`technical-writing` skill** (Diátaxis). LITE, about 2 h, Wave 2 tail.
13. **A skill evaluation harness:** run each skill's three scenarios on a fresh session, used at CIT-E. STANDARD, about 4 h. With or just after W2-11 r1.

**Deferred, unchanged:** architect (`architecture-review`), performance, AI/ML, data author, change controller, memory/knowledge, tooling: Wave 3 (DEC-832).

### 5.4 Sketch: the `benchmarking` skill (research role)

**Description:** "Compares a practice, tool or design of the Gov OS with software companies' published practice and market tools, and returns a ranked verdict with evidence. Use when a decision needs an external yardstick, a bake-off, or a 'build or adopt' answer."

**Inputs:**
- the question;
- the Gov OS feature, with its files and decisions;
- the criteria (from the spec's KPIs, or agreed with the CTO);
- the budget (time and tokens);
- the research allowlist.

**Steps (checklist):**
1. State the question and the decision it serves. Write the criteria, their weights and a pass line *before* looking at candidates.
2. Ask `gov retrieve` for earlier evidence and decisions; don't redo settled work.
3. Build a long list from standard sources:
   - practice: DORA [S4, S5], SPACE [S32], Google eng-practices and the SWE book [S9, S10], GitLab handbook [S12], SRE book [S13, S14], ISTQB [S15], NIST SSDF [S27], SLSA [S28], OpenSSF Scorecard [S33], Microsoft ISE playbook [S19];
   - tools: vendor docs, the Thoughtworks Radar [S26], CNCF landscape;
   - agent systems: Anthropic engineering posts [S20, S22], arXiv (MetaGPT, ChatDev, Agyn) [S23, S24, S25], SWE-bench.
   Paid analyst reports (Gartner, Forrester) are a P1 cost question; never buy one.
4. Narrow to a short list of 3 to 5 on the hard criteria.
5. Gather evidence per candidate, with every claim sourced. Mark each source primary, secondary or vendor, and mark claims unverified when only one secondary source has them.
6. Where it is cheap and safe, run a bake-off in the experiment folder: the same task, the same measure, installs only in the folder's venv.
7. Score against the weights. Write the "what we would lose" line for the top two.
8. Give the verdict in Radar form, Adopt / Trial / Assess / Caution [S26], plus "build", "adopt" or "keep ours", with a confidence.
9. Check citations: every claim traced to a source, and every number with its date.

**Output:** an evidence record in the folder (question, criteria, long and short lists, the scoring table, the verdict, residuals, sources with URLs and access dates), then a six-part package (DEC-818) through the CTO.

**Escalation:** a paid service, an install outside the venv, or a verdict that changes a standing decision: P1. A benchmark showing a lifted Gov OS feature is worse than a market tool: P2 to the CTO, with the CIT-P route named.

**Its three test scenarios (examples):**
- "Is our merge queue as good as GitHub's for our case?"
- "Does `gov retrieve`'s hit rate beat a plain ripgrep baseline?"
- "Do our role files cover ISTQB's test roles?"

---

## 6. What it blocks, and what waiting costs

**What waits on your answers:**
- **W2-33 r2:** RR-Q3 (QA engineer or independent reviewer);
- **W2-11 r2:** RR-Q1 and RR-Q5 (the skills list);
- **W2-83b:** the stream playbooks name the Senior Engineer's integration duties (RR-Q1);
- **the SE brief and prompt v4:** RR-Q1 and RR-Q2;
- **ticket 5 (the queue):** RR-Q1.

DEC-954 holds W2-60b, W2-11, W2-33 and W2-83 from further building until the roles land, and the three layers wait for the roles and ACT 2.

**What need not wait:** none of these depends on this research, so they can start as soon as you allow:
- **W2-33 r1:** the defaults block in the six existing files;
- **W2-11 r1:** skill versions and the lead-brief catch-up; the skill template if RR-Q5 is yes;
- **W2-60b:** reading roles from role files;
- **W2-83a:** the playbook form.

**What waiting costs:**
- **Days:** ROLES-SPEC-1 estimated the roles landing on 11-04 to 11-06.
  - The additions here that come before ACT 2 (items 1 to 5, 7, 8, and 6 if wanted) add about 1 to 1.5 days of worker time; most of it runs in parallel with work already planned.
  - The domain skills (items 9 and 10) come after ACT 2, so they add nothing before ACT 2.
  - Each day your answers wait moves ACT 2 and the three layers by about a day, because W2-33 r2 and W2-11 r2 are on the roles' critical path.
- **Risk while waiting:** the integration head can still go red after a merge (§4 (a)), and the CTO keeps doing the per-ticket QA check by hand. Both are already true today.

---

## Sources

Accessed 2026-10-30. "Search" means read through search summaries, not opened directly.

- S1 GitHub, managing a merge queue: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- S2 GitLab, merge trains: https://docs.gitlab.com/ee/ci/pipelines/merge_trains.html
- S3 Trunk-based development: https://trunkbaseddevelopment.com/
- S4 DORA, trunk-based development: https://dora.dev/capabilities/trunk-based-development/
- S5 DORA, metrics: https://dora.dev/guides/dora-metrics-four-keys/
- S6 Uber, SubmitQueue and CI at scale (search): https://www.uber.com/en-AU/blog/slashing-ci-costs-at-uber/
- S7 The "not rocket science rule" (Hoare, bors; a copy, since the original returned 404) (search): https://eluvk.github.io/readings/nrsr.html
- S8 Chromium tree sheriffs: https://www.chromium.org/developers/tree-sheriffs/
- S9 Google eng-practices, the standard of code review: https://google.github.io/eng-practices/review/reviewer/standard.html
- S10 Software Engineering at Google, ch. 9: https://abseil.io/resources/swe-book/html/ch09.html
- S11 GitHub, CODEOWNERS: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- S12 GitLab, code review guidelines: https://docs.gitlab.com/development/code_review/
- S13 SRE book, release engineering: https://sre.google/sre-book/release-engineering/
- S14 SRE book, managing incidents: https://sre.google/sre-book/managing-incidents/
- S15 ISTQB CTFL v4.0.1 §1.4.5, §1.5.3: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf (text read from the mirror https://heyallan.github.io/istqb-ctfl/foundation-level/syllabus/)
- S16 Atlassian, quality assistance (search): https://www.atlassian.com/blog/development/6-essential-skills-quality-assistance-engineer
- S17 Pragmatic Engineer, how Microsoft does QA (search): https://newsletter.pragmaticengineer.com/p/how-microsoft-does-quality-assurance
- S18 StaffEng, staff archetypes: https://staffeng.com/guides/staff-archetypes/
- S19 Microsoft ISE Engineering Fundamentals Playbook: https://microsoft.github.io/code-with-engineering-playbook/
- S20 Anthropic, skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- S21 Claude Code, subagents (frontmatter `skills`, `effort`, `model`): https://code.claude.com/docs/en/sub-agents
- S22 Anthropic, multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
- S23 MetaGPT: https://arxiv.org/abs/2308.00352
- S24 ChatDev: https://arxiv.org/abs/2307.07924
- S25 Agyn, team-based autonomous SE (search): https://arxiv.org/html/2602.01465v2
- S26 Thoughtworks Radar FAQ: https://www.thoughtworks.com/radar/faq
- S27 NIST SP 800-218 SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
- S28 SLSA verified properties (two-party review) (search): https://slsa.dev/spec/v1.2/verified-properties
- S29 Diátaxis (search): https://diataxis.fr/
- S30 Design docs at Google (search): https://www.industrialempathy.com/posts/design-docs-at-google/
- S31 Atlassian, incident severity levels (search): https://www.atlassian.com/incident-management/kpis/severity-levels
- S32 SPACE of developer productivity (search): https://queue.acm.org/detail.cfm?id=3454124
- S33 OpenSSF Scorecard (search): https://github.com/ossf/scorecard
- S34 GitHub merge queue GA, Enterprise Cloud for private repositories (search): https://github.blog/changelog/2023-07-12-pull-request-merge-queue-is-now-generally-available/
- S35 Larson on the CTO role (search): https://review.firstround.com/a-masterclass-in-engineering-leadership-from-carta-stripe-uber-and-calm-will-larson-cto-at-carta/
- S36 Scrum Guide (Definition of Done): https://scrumguides.org/scrum-guide.html

**Repository files read:**
- `docs/DECISION_REGISTER.md` (DEC-832, DEC-953 to DEC-957)
- `governance/project/orchestration/packages/ROLES-SPEC-1.md`
- `governance/project/prompts/w2-orchestrator.md` §0
- `governance/project/orchestration/DECISIONS-IN-FORCE.md`
- `docs/charter/CHARTER_v5.md` §4 to §6
- `docs/adr/ADR-0001-threat-model.md`
- `template/governance/kernel/roles/*.md` (6)
- `template/governance/kernel/skills/*/SKILL.md`
- `governance/project/roster.yaml`
- `.gov-runtime/scratch/orchestrator/tools/close_build.py`
- the git history of `w2/integrate`
