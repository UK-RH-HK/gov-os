---
record: research
task: rubric-research (DEC-1209 (4); research, not a ticket)
written: 2026-11-16 17:36 GMT (from date)
author: research subagent of the Gov OS CTO (read-only on every repository; this file is its only write)
decisions: [DEC-1208, DEC-1209]
sources: [DEC-1208, DEC-1209, DEC-1204, DEC-1047, DEC-974, DEC-221, DEC-1052, DEC-1157, DEC-1173, DEC-1010, DEC-861, CAP-33]
---

# The work-sizing rubric: how good teams route work by size and risk, and the design of ours

**Identity note (said first, as the research brief asks).** The research template asks for an identity check expecting
`research`. This session runs as a subagent inside the CTO's session, so it inherits `GOV_ROLE=orchestrator`,
`GOV_TICKET=DAEO-sdxk`. The template's `{CMD:identity}` slot was never filled, so it could not be run. I went on
because the CTO's task states the session's terms itself: read-only, one write to this path, no commit. I kept to
those terms. I made no commit and no other write. Scratch scripts are in my session scratchpad, outside the repository.
The CTO should decide whether this counts as a stop.

## 1. Question
How do good software teams route work by size and risk? What should Gov OS's rubric be, given that? That covers its
dimensions, a decision table an agent can apply in under a minute, the classes and what each needs, the protected
areas, the guardrails, machine and operator work, where the text lives, how it compares with the provisional rubric,
and the before and after measures with their baseline.

**Stop rule:** evidence-bounded. I stop when each research topic has at least one primary or first-hand source, the
baseline is drawn from P1 and P2, and the provisional rubric has been checked against both. I set a time box of about
one hour of session time and kept to it.

## 2. Decision it feeds
DEC-1209 (4): the rubric goes into research and discovery now, as research and not a ticket, and the provisional
rubric stays in force meanwhile. The owner then decides what to build. This record feeds that decision and DEC-1208's
specification of the rubric, items 1 to 5 in the owner's words.

## 3. Method
1. **The repository first.** I read the provisional rubric and DEC-974, DEC-1047, DEC-1204, DEC-1208, DEC-1209 and
   DEC-221. I read retrospective parts P1 to P4 (P5 skimmed) and the withdrawn W2-196 ticket's KPIs, from its filing
   commit a2a07592e. I read the planning and orchestration skills, `.claude/templates/role-lead.md`, the ticket
   template and schema, `class-rules.yaml`, `governance/project/criticality.yaml` with `src/gov/launch/criticality.py`,
   `src/gov/plan/`, `src/gov/impact` and `src/gov/closure` (radius), the shipped lists in `src/gov/adopt/fabric.py`,
   and CLAUDE.md, AGENTS.md and `.rulesync/rules/governance.md` with the template's copy.
2. **Measurements from records that exist.** These come from git history and the retrospective's `perticket.csv`. I
   ran no suite.
3. **External sources.** WebSearch and WebFetch, each cited by URL in §6. Where a figure appears only in secondary
   coverage, it is marked as such.

## 4. Commands run (read-only)
- `env | grep ^GOV_` (secrets filtered out); `git log`/`git show` on w2/integrate; `sed`/`grep` reads of the register and skills.
- `git log w2/integrate --since='2026-11-16 17:19' --format='%h %ad Class=[%(trailers:key=Class,valueonly)]'`
- `git log w2/integrate --no-merges --since=2026-11-09 --format='%(trailers:key=Task,valueonly)' | sort | uniq -c`
- `git log … --grep='^Task: DAEO-sdxk' --name-only | awk …` (the protected share and file counts of the CTO's commits)
- `python3 -I <scratchpad>/rubric/classify.py`. It joins `perticket.csv` with each closed ticket's `allowed_paths` and
  `est_loc`, then applies the protected globs.
- One guard refusal, not retried: `git show a2a07592e:$f`, a revision given through a variable. I then read the file
  under its literal path.

## 5. Measurements (est. = estimate, with how it was made)

**M1. The baseline per profile (P2, 141 worked tickets, 2026-10-16 to 11-16).**

| | LITE (19) | STANDARD (72) | FULL (50) |
|---|---|---|---|
| claim to merge, median days | 0.25 | 0.58 | 0.87 |
| claim to close, median days | 1.51 | 3.85 | 3.21 |
| lead + workers, median $ | 6.71 | 18.88 | 51.19 |
| review rounds, median [p75]; tickets with >2 | 0 [0]; 0 | 1 [2]; 11 | 2 [4]; 22 |
| lead runs ending PACKAGES | 35 % | 44 % | 46 % |
| reviewer-labelled blocking catches | 0 of 4 runs | 16 of 75 runs | 39 of 123 runs |

- **A small change through the full loop:** exa-g6db was a 7-line fix. It took 2 h 30 min and about $22, and it still
  had no close (P2 §4).
- **Owner interruptions (P1):** 544 owner messages in 31 days, about 17.5 a day and 30 a day in W5. Of these, 134 were
  relays of jobs, ACTs or commits; 140 answered packages; 33 were ACT yes lines. 206 pushes went to the owner's phone.
- **Spend:** coordination and ceremony together took 56 % of spend; builders took 8 % (P2) to 7 % (P1).
- **Probes (P4):** 25 of 502 findings were in the blocking class (5 %). 12 of 61 ACT bundles were regenerated
  `.claude/` copies.

**M2. A protected area makes most Gov OS tickets FULL under the provisional rule (est.).**
I applied the provisional protected list to each closed ticket's `allowed_paths`, as globs:

| class by the provisional rule | n | of which profile then was FULL / STANDARD / LITE |
|---|---|---|
| F (touches a protected path) | 90 (64 %) | 34 / 53 / 3 |
| not protected, ≤ 60 est. lines, ≤ 2 non-test paths | 23 | 4 / 6 / 13 |
| the rest | 28 | 12 / 13 / 3 |

- **Effect:** about 53 STANDARD tickets would become FULL. At the P2 medians ($18.88 to $51.19) that is about $1.7k
  more a month, and one more review round each, for no catch the data shows. P2 §3 finds no lost work among the
  STANDARD tickets off the guarded surfaces.
- **How estimated:** allowed paths are wider than the files a change actually touches, so this overstates. A diff-based
  recount is proposed in §9.

**M3. The pool for the quick lane (git, 2026-11-09 to 16).**
- The CTO made 335 non-merge commits under `Task: DAEO-sdxk`, about 48 a day. Of those, 290 (87 %) touch 3 files or
  fewer, and 23 (7 %) touch a protected path.
- 388 of their file touches are under `governance/project/orchestration/`, mostly records.
- **Reading:** most of the CTO's direct work is already a quick-lane shape. The rubric's main gain is not a new lane but
  fewer tickets, packages and yes lines for work of that shape.

**M4. The provisional rubric is not yet followed.**
- 0 of the 8 commits on w2/integrate between 17:19 (DEC-1208) and 17:31 carry `Class:`. They are W2-153's reopen,
  test, path case, merge and re-close, and two decision records.
- **Reading:** a trailer that every commit must carry by hand is the trailer-slip pattern again (P3 F6: P1 noise from
  trailer slips). The class should be computed where it can be.

**M5. What already exists in the code that a rubric can reuse.**
- `criticality.yaml` with `criticality.py`: path globs to C0..C3, highest match wins, read at launch, fail closed. Its
  C3 list is nearly the protected list.
- `class-rules.yaml`: the control paths that go by ACT.
- `landing_check.py`: it already re-judges first-parent history against those control paths.
- `gov impact` / `gov closure`: a radius and depth for a change.
- `gov plan` (`src/gov/plan/derive.py`): it orders by `depends_on`, `waits_on`, `needs` and write overlap. **It never
  reads profile or size.**
- The ticket template's profile comment already reads: "FULL only for memory, the five guard rules, launch/close, the
  queue, data loss". That narrower rule contradicts the provisional rubric's "FULL for any protected area, the kernel,
  a spec or a KPI".

## 6. Sources (external, each with what the rubric takes from it)

| topic | source | finding | what Gov OS takes |
|---|---|---|---|
| Standard, normal and emergency changes | [itsm.tools: Change Enablement in ITIL 4](https://itsm.tools/change-enablement/); [Faddom: ITIL change types](https://faddom.com/itil-change-management-types-standard-vs-normal-vs-emergency/); [Virima: ITIL change types](https://virima.com/blog/understanding-itil-types-of-changes-a-comprehensive-guide) (secondary, vendor summaries) | "Standard changes are pre-approved, low-risk, and repeatable changes", typically run from runbooks. Normal changes need risk assessment and approval, with workflows scaled by risk. Emergency changes are expedited and "typically need a post-implementation review". ITIL 4's change authority "decentralizes decision-making" and may be a peer review or an automated rule. | (1) **The owner pre-authorises a change model once**, not each instance. (2) **An emergency lane** with review after the fact. (3) The change authority can be a rule the code applies. |
| Heavyweight approval | [DORA: Streamlining change approval](https://dora.dev/capabilities/streamlining-change-approval/); [DORA State of DevOps 2019](https://dora.dev/publications/pdf/state-of-devops-2019.pdf); [InfoQ on the 2019 report](https://www.infoq.com/articles/2019-devops-report/); the "2.6 times more likely to be low performers" figure only in secondary coverage ([Diginomica](https://diginomica.com/devops-accelerating-do-it-right)) | "no evidence was found to support the hypothesis that a more formal, external review process" lowers change failure. "heavyweight approaches tend to slow down the delivery process". "change approvals are best implemented through peer review during the development process", with segregation of duties met by peer review and automated checks. A clearly understood change process improves performance. | Approval sits with the reviewer nearest the change, not the owner, except for real control changes. **A process an agent can read in a minute is itself a performance factor.** Automated checks are the first gate. |
| Small changes | [Google eng-practices: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html); [Software Engineering at Google, ch. 9](https://abseil.io/resources/swe-book/html/ch09.html) | "100 lines is usually a reasonable size for a CL, and 1000 lines is usually too large". A 200-line change across 50 files is too large. Small changes are "simpler to roll back". At Google "essentially every change is reviewed". Three approvals (LGTM, OWNERS, readability) are "most" often given by one person. "Small" means "about 200 lines". About 35 % of changes touch one file. | Size thresholds in lines **and** files. **A protected directory gets an owner's approval, not a heavier process.** One reviewer can carry every approval. |
| Risk-scaled review | [martinfowler.com: Ship / Show / Ask](https://martinfowler.com/articles/ship-show-ask.html) | Ship goes straight to mainline for "an unremarkable bug" or "an established pattern". Show merges at once and is reviewed after. Ask waits for review. Merging without review depends on CI keeping mainline releasable. | Q is "Ship" with tests green. A sample audit gives the "Show" after the fact. L, S and F are degrees of "Ask". |
| Trunk-based development, small batches | [DORA: Trunk-based development](https://dora.dev/capabilities/trunk-based-development/) | Branches "typically last no more than a few hours". "Merge branches to trunk at least once a day". "Perform synchronous code review". | The quick lane is the trunk-based norm, not an exception. Keep Q at one commit and under 30 minutes. |
| Code owners, protected paths | [GitHub: About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners); [GitLab: Code Owners](https://docs.gitlab.com/user/project/codeowners/) | Owners are requested automatically for the paths they own. Branch protection can "Require review from Code Owners". "the last matching pattern takes the most precedence". GitLab adds required, multiple and optional owner approvals. | **Protected paths come from one machine-readable glob file, matched by code.** A protected path adds a required reviewer; it does not force the heaviest route. |
| Reversibility | [martinfowler.com: Feature Toggles](https://martinfowler.com/articles/feature-toggles.html) | Release toggles "should generally not stick around much longer than a week or two". Toggles are "inventory which comes with a carrying cost". | Reversibility is judged by "does a revert or a written, rehearsed rollback restore the prior state". A flag or switch added to make something reversible is itself a change with a removal date. |
| Blast radius, deploy gates | [Google SRE book, Introduction](https://sre.google/sre-book/introduction/); [AWS Builders' Library: Automating safe, hands-off deployments](https://builder.aws.com/content/3ErTKQOTKc5NIw031UePBPxTQ6I/automating-safe-hands-off-deployments) | "roughly 70% of outages are due to changes in a live system". The remedies are progressive rollouts, fast detection and safe rollback. "Limiting the scope of each individual deployment limits the potential impact". The pipeline "prevents automatic deployments to production when there is a higher risk". | Blast radius is a gate condition, not a size. A config or machine change is a live change: a written, rehearsed rollback, and the owner's yes, unless it is a catalogued model. |
| Time boxes | [Shape Up, ch. 3 (appetite)](https://basecamp.com/shapeup/1.2-chapter-03); [Shape Up glossary: circuit breaker](https://basecamp.com/shapeup/4.5-appendix-06) | "Appetites start with a number and end with a design". The circuit breaker: "Cancel projects that don't ship in one cycle by default instead of extending them by default". | **The time box stops by default.** The quick action is reverted or escalated, never quietly extended. |
| Fast-lane policy | [Kanban University glossary](https://kanban.university/glossary/); [Scrum.org: classes of service](https://www.scrum.org/resources/blog/classes-service-kanban-what-are-they) | Classes of service (expedite, fixed date, standard, intangible) are explicit policies. Expedite limits are set explicitly, often a WIP of 1. | One emergency at a time, explicitly declared. |
| Auditing a fast lane | [Strike Graph: SOC 2 population and sampling](https://help.strikegraph.com/articles/4056301-soc-2-type-2-population-and-sampling-guide); [soc2auditors.org: change management controls](https://soc2auditors.org/insights/soc-2-change-management-controls/) (practitioner sources) | Auditors take the whole population of changes, sample from it (often 25 to 40), and trace each change from request to deploy. A deviation pulls a larger sample. Unreviewed changes must still be in the population. | Machine-check 100 % of the cheap properties: trailer, paths, size, tests run. Sample the judgement properties. **A miss widens the sample and suspends that change model.** |

## 7. Verdict

### 7.1 What the provisional rubric gets right (it agrees with the research)
- **Protected areas are never Q.** This matches CODEOWNERS and Google OWNERS.
- **Q is done directly, with the tests green, in one commit with a class trailer, listed in the digest.** This is
  Ship/Show and trunk-based development.
- **The 30-minute time box stops, reverts and escalates.** This is the circuit breaker. DEC-974 still holds for any new
  ticket.
- **Weekly spot audits.** This is SOC 2 sampling.
- **Config and permission changes need a written rollback.** This matches the AWS and SRE rollback guidance.
- **Class-rules and the operator's gates are unchanged, and the rubric is measured from day one.**

### 7.2 Where it is wrong or short (ranked by effect)
1. **"Touches a protected area means F" over-routes.**
   - About 64 % of last month's tickets touch a protected glob (M2, est.), so about 53 STANDARD tickets would become
     FULL.
   - Research: a protected path adds a required owner-reviewer (GitHub/GitLab Code Owners, Google OWNERS), and
     heavier approval does not improve stability (DORA).
   - P2 §3 found review earns its place on guard, gate and launch surfaces, not on every protected file.
   - **Fix:** protected means never Q or L, plus one mandatory review by the golden rule (class S). F is kept for
     changes that alter what a wall allows or refuses, kernel and instruction text (CAP-33), spec, KPI or decision
     text, or irreversible effects. The ticket template's own comment is already close to this.
2. **There is no pre-authorised standard change.**
   - The provisional rubric asks for the owner's yes on each config or permission change.
   - ITIL 4's standard change is authorised once, as a model, and then run from a runbook.
   - Evidence: 33 yes lines, 134 owner relays and 12 copy ACTs (P1, P4 Q8).
   - **Fix:** a catalogue of change models the owner approves once each, which then go Q with no yes per instance.
     Each instance still has its rollback written and rehearsed. A model leaves the catalogue after one misroute.
     **Needs the owner's word.**
3. **There is no emergency lane.**
   - ITIL's emergency change, and Kanban's expedite class, is expedited and reviewed after.
   - Gov OS had real emergencies: DEC-1047, DEC-1209, a guard refusing honest work, WSL down. The provisional rubric
     would push an urgent guard fix through FULL.
   - **Fix:** class E. It runs on the owner's word or a declared incident, one at a time. Tests prove the failing case.
     A review by the golden rule follows within 24 h, with an F-grade record after the fact.
4. **The class is judged by hand, and "when in doubt, the higher class" pushes classes up.**
   - DORA: a clearly understood process is itself a performance factor.
   - P3 F11: anti-creep mechanisms eroded, and ceremony accretes.
   - M4: the hand-written trailer is already missing on 8 of 8 commits.
   - **Fix:** an ordered first-match decision table (§7.3). Protected globs in one file, read by the planner, the
     landing check and the auditor. The class is computed by code wherever the path list decides it. Doubt raises only
     the dimension in doubt, not the whole class. A records-only commit is Q by computation and needs no trailer.
5. **Review is not scaled inside STANDARD, and the audit is a fixed "10 a week".**
   - P2: no labelled catch in 4 LITE review runs, and no spot-checked lost work for STANDARD off the guarded surfaces.
     SOC 2 practice widens the sample on a miss.
   - **Fix:** L gets no review unless it is on a fail-open surface. S gets one review only when protected or on a
     fail-open surface, otherwise the QA trace. The audit samples 10 Q commits or 20 %, whichever is larger; a miss
     doubles the next week's sample and suspends that change model.
   - Smaller points:
     - The provisional time box omits who starts the clock. The start is the first edit, written as one line in the
       standby or digest log.
     - "Second commit" is too strict when a test and a fix go together; they must be one commit.
     - L still costs an owner approval per ticket (DEC-974). Batching L approvals into one owner line per batch is an
       option for the owner.

### 7.3 The design: the decision table (first matching row wins; an agent needs only the path list, the estimate and four yes/no answers)

| # | Question | Yes: class |
|---|---|---|
| 1 | Has the owner declared an emergency, or is there a live incident (work stopped, machine down, a fail-open live)? | **E** |
| 2 | Does it change what a wall allows or refuses, or kernel or agent-instruction text, or spec, KPI or decision text, or is it irreversible (data migration, history, deletion, release or push)? | **F** |
| 3 | Does any touched path match a protected glob (the guard, acceptance tests, memory, the close and landing, data, the kernel)? | **S, review mandatory** (never Q or L) |
| 4 | More than one behaviour, more than about 150 changed lines, more than one area, or a new CLI or public interface? | **S** |
| 5 | No test runs the touched code and one cannot be added in the same commit, or more than 30 min, or more than one commit, or a revert does not fully restore? | **L** |
| 6 | A machine or operator config or permission change? Catalogued model: **Q**. Not catalogued, narrowing or reversible with a rehearsed rollback: **Q on the owner's yes**. Widens a protected area: row 2 | **Q / F** |
| 7 | Otherwise (about 50 lines or fewer, 3 files or fewer, one area, tests exist, 30 min or less, one commit, a revert restores) | **Q** |

**Routes and needs**

| class | route | tests | review (golden rule) | record | owner |
|---|---|---|---|---|---|
| Q | the CTO or a senior engineer commits directly | the affected tests green before the commit; landing select and nightly after | none before; sampled after ("Show") | one commit, `Class: Q` plus purpose (computed for records-only commits); a digest line | none; the yes only for a non-catalogued config or permission change |
| L | LITE ticket: test designer, engineer, `gov accept`, land | one per KPI line (DEC-221) | none, except a narrow check on a fail-open surface | ticket and close | ticket approval (DEC-974); batching is an option |
| S | STANDARD ticket | each KPI line's success and failure plus key edges | one round when protected or on a fail-open surface; otherwise the QA trace | ticket, close, probe record if reviewed | ticket approval |
| F | FULL ticket; ACT for control paths; CIT-P for the kernel | thorough | at most two rounds, then the owner once (DEC-1204 (3)) | probe record, ACT or CIT-P record | the ticket, plus the bytes (ACT yes / CIT-P) |
| E | done now by the CTO on the owner's word | the failing case plus the affected tests | within 24 h after | register line plus digest; F-grade record after | the word before, the review result after |

**Protected globs** (one file, a superset of `criticality.yaml`'s C3):
- **The guard:** `.claude/hooks/**`, `.claude/settings*.json`, home settings, `src/gov/guard/**`, the path map, the
  box's mounts.
- **Launch walls:** `src/gov/launch/**`.
- **Acceptance tests:** `tests/acceptance/**`, outside the ticket's own test designer.
- **Memory:** the store, retrieve and retrieval, memaudit, rebuild, the evaluation sets.
- **The close:** `src/gov/close/**`, `land.py`, the landing check and select, the merge queue.
- **Data:** migrations, history rewrites.
- **The kernel:** `template/governance/kernel/**`, CLAUDE.md, AGENTS.md, `.rulesync/**`, `docs/contract/**`.
- **Tests that could be silenced:** removals from `test-map.yaml` and the opt-in lists (class-rules already marks these
  as (b)).
- **Secrets and held-out material, and the operator's own install (O).**

**Guardrails**
1. **Protected is never Q or L.** A Q whose diff touches a protected glob is flagged by the landing check, which reuses
   `landing_check.py`'s control-path pass.
2. **Time box:** 30 minutes from the first edit, one commit, the tests green.
   - Past it, stop by default (circuit breaker): revert what is half done.
   - Under DEC-974, and under DEC-1209 while it stands, the work goes to the owner as one line in the next package
     batch, not an interrupt, unless it blocks.
3. **The audit:** weekly, by an independent auditor under the golden rule.
   - The population is every Q and E commit. Code checks 100 % of the cheap properties: protected paths, size, one
     commit, tests run, trailer.
   - The auditor samples the judgement properties: at least 10, or 20 %.
   - A misroute widens the next sample twofold, suspends that change model, and goes into the digest with its fix.
4. **Escalation path:** a lead never files a ticket and names the need in its return. The CTO packages it. The owner
   decides (DEC-974).
5. **The rubric's own basis line** (DEC-1052 trigger 1): it guards against ceremony out of proportion to risk (the aim,
   DEC-1047) and against a fast lane that fails open (the golden rule). A rule added to it states which of the two it
   serves.

**Machine and operator work**
- Rows 2, 3 and 6 apply to config, permission, cron, server and pin changes by their paths, using `class-rules.yaml`'s
  roots: repo, home, crontab.
- A class (b) path still goes by the operator's ACT and gates. Q there means the smallest review G4 accepts (one narrow
  pass), as the provisional rubric says.
- First catalogue candidates for the owner:
  - regenerated `.claude/` copies equal to the generator's output at an owner-approved kernel commit (P4 Q8);
  - deny-only additions to settings or the path map (already (a) in class-rules);
  - server restarts and committed server configs (class (a));
  - re-pins after a release the owner typed;
  - crontab time shifts that keep the same command.

### 7.4 Where the text lives
1. **The kernel skill (CAP-33, by CIT-P).**
   - A new section, "## Sizing work: the rubric", in `template/governance/kernel/skills/orchestration/SKILL.md`: the
     table, the routes, the guardrails, the audit.
   - A section, "## Dividing work by class", in `planning/SKILL.md`, with three rules:
     - split until each ticket is one class;
     - cut a protected part out into its own small S or F, so the rest stays L or Q (Google: small, self-contained
       changes);
     - Q work is never ticketed.
   - The `.rulesync` mirrors and the generated `.claude/skills` copies follow.
   - **Option:** its own skill, `sizing-work`, preloaded like `judging-work` (DEC-1204 (5)). It is cleaner, but it is
     a new shipped file and waits for W2-195's `fabric.py` and shipped-list changes.
2. **CLAUDE.md and AGENTS.md.**
   - One section, "## Sizing work (DEC-n)", of about five lines: the classes, "protected is never quick", the time box,
     where the table is.
   - Written in `.rulesync/rules/governance.md` and in `template/.rulesync/rules/governance.md` for the kit.
   - Class (b) by the agent-instructions row: an ACT, as ACT-GOLDEN-RULE-1 was (DEC-1173).
3. **The planner.** `gov plan` computes each ticket's floor class from `allowed_paths` against the protected glob file.
   It follows the pattern of `criticality.py`: highest match wins, fail closed on a bad file. A profile below the floor
   becomes a finding, `RUBRIC_FLOOR`, and the output names the class. `derive.py` today reads neither profile nor size
   (M5).
4. **The kit.**
   - The skill sections ship with `copier copy` of `template/`, which needs no `PACKAGED` change.
   - A glob file goes as `template/governance/project/rubric.yaml`, beside `close.yaml`, `path-map.yaml` and
     `test-map.yaml`. It is only added to `fabric.PACKAGED`, the shipped-list test and W2-88's items if A9 must find it
     without a kit.
   - The ticket template's profile comment is aligned to the table.

### 7.5 Measured before and after (per change and per class)

| measure | source | baseline |
|---|---|---|
| wall time, claim (or first edit) to land | ticket status history; commit times | median 0.25 / 0.58 / 0.87 days (L/S/F); Q: none (exa-g6db's 2 h 30 for 7 lines as the example) |
| cost | lead and worker `total_cost_usd`; CTO estimate per class tag | $6.71 / $18.88 / $51.19 median; CTO 46 % of spend unattributed |
| review rounds | `docs/probes/`, round ledger | median 0 / 1 / 2; >2 rounds on 0 / 11 / 22 tickets |
| owner interruptions | P1's `owner.py` rerun | 17.5 a day (W5: 30); 134 relays, 140 package answers, 33 yes lines; 206 pushes |
| relays from leads | lead returns | PACKAGES end 45 % of lead runs |
| **change failure per class** (DORA's counter-measure, new) | reverts or fix commits within 7 days naming the change; reopens; landing ejections | reopens 0 / 6 / 10 tickets; 12 of 90 lands ejected |
| misroutes and time-box overruns | weekly audit record | none yet |

## 8. Draft KPI lines (each with its verify)
- **K1. Every change has its class, mostly computed.**
  Verify: from the start date, `git log w2/integrate --no-merges --format='%h %(trailers:key=Class,valueonly)'`
  shows a class on every non-records commit. A records-only commit is classed by the check, with no trailer.
- **K2. No Q commit touches a protected glob.**
  Verify: the landing check's report over the week names 0 `Class: Q` commits whose diff matches `rubric.yaml`.
  Planted case: a one-line Q edit of `.claude/hooks/x` is flagged with its path.
- **K3. The planner names a floor class per ticket and flags a profile below it.**
  Verify: `gov plan` on a planted ticket whose `allowed_paths` hold `src/gov/close/**` at LITE prints `RUBRIC_FLOOR`
  and S.
- **K4. The quick lane is fast and safe.**
  Verify: over two weeks, the median Q wall time is 30 min or less, and the Q change-failure rate (a revert or fix
  within 7 days) is no higher than L's. Both come from git and the audit record.
- **K5. The owner's interruptions fall.**
  Verify: P1's `owner.py`, rerun on the two weeks after landing, gives relays plus yes lines plus package answers per
  day below the 11-day W4/W5 average.
- **K6. The audit runs and acts.**
  Verify: one audit record per week. Its sample is at least 10 or 20 % of the Q and E population, and it lists each
  misroute with its fix and any suspended change model.

## 9. Residuals
- **Identity.** The template's identity check could not be run as written. I proceeded on the CTO's explicit terms
  (§0). The CTO should confirm that this counts.
- **M2 overstates.** It uses allowed paths, not diffs. A diff-based recount, for the CTO or the lead to run, is a
  read-only script. Command, proposed: for each merged ticket, `git diff --name-only <merge>^1 <merge>` against the
  protected globs, then the same table as M2.
- **The DORA 2.6 figure** was found only in secondary coverage. The verdict does not rest on it. The primary page's
  "no evidence" and "slows delivery" lines carry it.
- **Owner decisions this design needs** (none taken here):
  - the class E lane;
  - the change-model catalogue (a standing yes per model, replacing a yes per instance);
  - "protected means S with mandatory review" in place of "protected means F";
  - batching L ticket approvals (DEC-974).
- **While DEC-1209 stands:** no L, S or F ticket can be filed. Only Q, E and direct work run, and a Q past its time box
  can only revert and package.
- **The new skill and the glob file wait on W2-195's shipped-list changes** if A9 must carry them. The skill sections
  alone do not.
- **P3 F11:** the rubric adds rules. Its basis line and the weekly audit are what keep it from accreting. Without the
  audit's record, the anti-creep pattern of P3 repeats.
