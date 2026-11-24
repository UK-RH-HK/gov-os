# Gov OS: the golden workflow

**Status:** the owner's draft, 22 November 2026, for the CTO to verify against the code and complete. Once the owner
approves the completed version, this file is the spine of Gov OS: the Charter and the Contract are rebuilt around its
steps, and every document, role, skill, template and Contract item that says something else is brought into line or
archived. It extends the golden rule: the golden rule says how work is judged; this file says how work flows.

**How to read it:** each step says what happens, what code holds (deterministic), what stays with an agent (a job with
fixed inputs, a fixed output form and a code check of that form), where it stands today, and where it must be. "Today"
is from Audit 4 (22 November) and is the CTO's to correct in the integration map.

---

## 0. The rules everything below rests on

1. **Value first.** The product's value is the work; governance serves it and is sized by it. Practicality and security
   work never become the core of the work.
2. **The threat model.** Gov OS guards against honest mistakes and drift in ordinary work, not an adversary. It catches
   and corrects; it does not prevent. No guard, no sandbox, no permission prompts; two denies only (git push and sudo,
   both the owner's).
3. **The golden rule.** A finding blocks only if ordinary work hits it and it fails open or loses work. A review happens
   only for a red test, a failed landing or merge, or a feature that does not work as intended; at most two rounds,
   then the owner once, with options. Green work needs no review.
4. **Deterministic where it can be, specified where it cannot.** Whatever can be decided or checked by code is decided
   or checked by code: at the launch, at the landing, or by a scheduled check, never by an agent's goodwill. Whatever
   must stay with an agent is a job with fixed inputs, a fixed output form and a code check of that form.
5. **Memory first.** Every agent asks memory before it greps or reads; the brief carries the memory bundle uncut; the
   agent searches once more in its own words.
6. **The work rubric.** A ticket is a feature: it has a spec and KPIs. A known bug in an existing feature is a fix,
   recorded under its owning ticket, its failing test written first. Records, docs, configuration and kernel text are
   chores, committed directly. A quick item that outgrows its time box becomes a fix or a feature.
7. **The model and effort rubric.** Opus only for the long-running sessions that orchestrate: each product's CTO (the
   master orchestrator) and a senior engineer per stream (the sub-orchestrator). Every other agent runs Sonnet, critical
   work included. A wide audit the owner asks for runs on Opus. Effort is set by role in the rubric. No session chooses
   its own model or effort; a change comes to the owner first.
8. **Decisions, by the escalation rubric already approved.** Every decision is taken at its level, and the levels
   combine code and judgement:
   - **The lead (P3)** decides and records what is reversible, inside its ticket, and changes no spec, KPI or standing
     decision; a fix with its failing test.
   - **The CTO (P2)** decides shared code and work across streams, the order inside a planned wave, a red landing and
     whether a review is called, kernel text, and an install inside the work's scope and the machine's capacity.
   - **The owner (P1)** decides features, specs and KPIs; a ticket added to or removed from a planned wave; the
     Contract, the Charter and standing decisions; data and measurement; anything irreversible outside a worktree; a
     secret or a paid service; a model or effort exception; a review not converged after two rounds; a release whose
     content he has not approved. Pushes to GitHub and sudo stay his. Releases whose content he has approved are cut by
     the CTO, by code.
   - **An emergency** (a secret exposed outside the machine, a risk of losing data or work, the disk below its floor,
     the machine over its gate and not recovering) stops the work, then pushes the owner.
   - **What code holds:** each decision is a structured record whose fields (what it touches, whether it is reversible,
     whether it changes a spec, a KPI, the Contract or a standing decision) set its level by code; code refuses a
     decision taken below its level, routes owner decisions to the decisions page (a stopper at once, with a push, at
     any hour; the rest in the morning brief, which also lists every push), writes the owner's answers into the
     register, and requires the basis line and the enforcement field on every new rule.
   - **What stays with an agent:** framing the question, the options, their costs and the recommendation; and the lead's
     or the CTO's own choice at P3 and P2. Each is written in the record's fixed form, so code can check it.
9. **The machine.** Work is sized to the machine it runs on; a machine too small to operate is refused with a reason.
10. **Context.** Orchestrators start fresh each morning from a handover; helpers start from a written brief, never as a
    fork; old sessions are not resumed. Every session gets only the tools its role needs.

---

## 1. The workflow, step by step

| # | Step | What happens | Held by code | Stays with an agent | Today | Must be |
|---|---|---|---|---|---|---|
| W1 | **Start or adopt a repository** | A new repository, or an existing one, goes through adoption: what it is, what it holds, what it brought in, its path map, its specs audited, its legacy retired, its memory built, its verdict | `gov adopt`'s stage chain (A0 to A10, AS, the verdict); the path map; the kit's settings (no connectors, the two denies) and the golden rules at the head of CLAUDE.md and AGENTS.md | The judged stages (A5, A7, A10, the spec audit's answers, the verdict) | Built, except the verdict stage (0.1.6) and the imports step (after EXAMIN's fresh 80); three capabilities named as exceptions | Every stage on the path; the verdict recorded; imports classed use, absorb or study |
| W2 | **Build memory** | The repository's records, code and documents are indexed: words, meaning and the record graph; stale and legacy material kept out of default memory | Store build and rebuild; the graph's links from front matter; namespaces and their index policy | None | Built; the route that keeps stale and legacy documents out comes in 0.1.6 | As today, plus the route |
| W3 | **Keep memory current** | Every commit refreshes memory; a failed refresh retries; the embedder is always up | The refresh hook after commits; the retry; the embedder started at boot and brought back if down | None | The refresh runs but did not retry when it failed; the embedder was not started at boot | Retry (0.1.5), start at boot (now), self-healing (W2-207) |
| W4 | **Measure memory** | Weekly, a fresh 80 questions (40 visible, 40 hidden) is written and judged end to end at 95 % or better; the figure is stamped with release, commit, models and rule | `gov memaudit`: declare, preflight, the hidden-set scan, the judge, the stamped figure | Writing and checking the questions; reading; grading (Sonnet), each with a fixed form | Built; typed by hand; the stamp comes in 0.1.5 | Scheduled weekly; stamped; the result in the digest |
| W5 | **Decide** | Every decision is taken at its level by the escalation rubric (rule 8): the lead, the CTO, the owner, or an emergency. Owner decisions are batched into one page; his answers are written into the register by code | The decision record's fields set its level; a decision taken below its level is refused; routing to the page and the pushes; `gov decisions answer`; the basis check; the owner-approval check; the enforcement field | Framing the question, options, costs and recommendation; the lead's and the CTO's choices at their levels, each in the record's fixed form | By message and by hand; the level is judged, not computed | Levels computed from the record (0.1.6); by page; every check on the path |
| W6 | **Trace impact** | A change to a decision, a spec or code shows which specs, tickets and tests it affects | The record graph, the path map, the code and test graph | None | The landing's test selection; the rest to be verified | One trace, used by planning and by the landing |
| W7 | **Plan** | The Contract (features, behaviour, KPIs) first; then the WBS, the waves with a set list of tickets, and each ticket filled from its template, the path map and memory | The ready check (no unfilled slot; the ticket's KPIs match its spec); the wave form; the rubric's class on every item | Writing the spec and KPIs; planning the waves (each with a fixed form) | Partly: forms exist, the checks are typed or missing | Every plan item checked by code before work starts |
| W8 | **Launch** | The dispatcher picks the next work by its dependencies; the load balancer sizes it to the machine; each session starts from a filled brief, with the memory bundle uncut, its model and effort by the rubric, only its role's tools, a claim and a launch record | `gov launch` and the run-time tool (dispatcher, load balancer, pause, spend, claim, record) | None | Off the path: leads start from a script | Every session started by `gov launch` (0.1.6); the run-time tool live (W2-207) |
| W9 | **Test first** | The independent test designer writes the acceptance tests from the KPIs only; they must be red on the base | Test authorship at the landing; red on the base | Designing the tests | Authorship checked; red on the base not checked | Both checked (0.1.6) |
| W10 | **Build** | The engineer builds until `gov accept` is green, then returns its result in the fixed form | `gov accept`; the return checked (its fields, its branch, a clean worktree) | Writing the code | `gov accept` on the path; the return partly checked | The return checked by code (0.1.6) |
| W11 | **Land** | The landing merges on a scratch copy, runs the selected tests on the merged result, checks paths and authorship, refuses a dirty worktree, records base reds and writes the close; a red calls a quality auditor (Sonnet) to diagnose and an engineer to fix | `gov queue` | Diagnosing a red (a fixed form, one cause per red) | Built, but Gov OS has landed by hand merge | Every landing through `gov queue` (started 22 November) |
| W12 | **Fix and chore** | A fix runs under its owning ticket, failing test first, and the landing writes its record; a chore is committed directly and checked after | `gov launch --fix`, `--chore`; the queue writing the fix record; `gov queue --direct` | Writing the fix | Partly built, off the path | On the path (0.1.6) |
| W13 | **Release** | The release acceptance passes (the Contract's enforcement checks, the proving run, the adopted repositories' memory measures); the CTO cuts the release, re-pins with self-rollback, and pushes the owner | The release gates, the re-pin, the authority file | None | 0.1.5 is the owner's last manual cut | Every approved release cut by code |
| W14 | **Update adopted repositories** | An adopted repository takes the new release at a quiet point, keeps its own edits, and can roll back in one command | `gov update`: the three-way merge, the check after, the rollback | None | By hand | Automatic at a quiet point (W2-207, W2-209 slice b) |
| W15 | **Run** | Under everything: the work is dispatched and sized, stalls are caught, the owner is pushed only when needed, orchestrators hand over each morning, usage and context are measured daily | The run-time tool; the daily usage and context figures | The orchestrators' coordination | Slices 1 to 3 built; old watchers still live | One run-time tool live (W2-207) |
| W16 | **Weekly hygiene** | Once a week: the memory measure, the doctor, the basis review, the clean-up; a secrets scan only before a repository goes public or is shared | The schedule | None | Unscheduled | Scheduled |

---

## 2. The jobs that stay with agents

Every job is started by `gov launch` from a filled brief, receives only what its brief names plus the memory bundle,
returns a fixed form, and is checked by code before anything relies on it. Audit 4's List B (§3) specifies each:
spec and KPIs; test design; implementation; a fix; a chore; diagnosing a red; an auditor's verdict; research; planning a
wave; the memory measure's writing, reading and grading; the ticket lead; the CTO; the senior engineer; adoption's
judged stages. A hand-off may rely only on what code has checked.

---

## 3. How Gov OS is assessed against this workflow

- Every Contract item and every standing rule carries its enforcement: built or not; held by code on the path, by code
  off the path, checked after (by itself or only when typed), or by a named agent job; why not, and when.
- Every release's acceptance prints the counts by class against the baseline of 22 November (21 % on the path, 13 % off
  the path, 31 % checked after, 19 % judgement, 16 % not built), so each release shows whether code's share grew.
- The target: the flow 90 % or more held by code; judgement only where the work is creative, and then specified.

---

## 4. What this file changes

- It is the spine of the Charter and the Contract: both are rebuilt around these sixteen steps and ten rules.
- Every piece of information that says otherwise (roles, skills, templates, briefs, docs, the kit's head, old decisions
  still read as current) is brought into line or archived; nothing old and stale is left to be read as current.
- Every tool the work depends on is part of the product, so adopted repositories get it; tools outside the product are
  absorbed, replaced by the product's own, or retired.
- The heads of CLAUDE.md and AGENTS.md point to this file beside the golden rule: whatever contradicts it is wrong.

---

## 5. The tool map (the CTO completes this section)

This file says what each step does; this section says which tool does it and how the steps join. The CTO fills one
table, from the code (Audit 4 §1.1 to §1.7 is the starting inventory), and the owner assesses it for gaps.

**One row per tool, script, hook, cron line or schedule that does Gov OS's work, inside the product or outside it:**

| Column | What it says |
|---|---|
| Step | W1 to W16, or "none" (a tool that serves no step is a candidate to retire) |
| Tool | the command, script, hook or schedule, and its path |
| Where it lives | in the product (`src/gov` or the kit, so every adopted repository gets it) or outside it (scratch, start scripts, the orchestrator's tools, cron lines) |
| Trigger | automatic by code (at the landing, at session start, on a commit, by schedule), called by an agent, or run by the owner |
| On the path | yes, or bypassed today, and by what |
| Receives / hands on | what it takes from the step before and what it gives the step after, in which form |
| How an agent knows it | for a tool an agent calls: the brief of that job names it with its exact command; for an automatic one: no agent needs to know it |
| Gap and fix | what is missing or broken, the fix, its owning ticket, its place |

**The rules the map must meet:**
1. Every step W1 to W16 has at least one tool, and every hand-off between steps names its form and the code that checks
   it.
2. Agents never need to know every tool. A tool that runs automatically is triggered by code; a tool an agent must call
   is named, with its exact command, in the brief of the job that needs it, and nowhere else is the agent expected to
   find it. Skills and role files describe the job, not the tool catalogue.
3. A tool outside the product is absorbed into it, replaced by the product's own tool, or retired; none stays outside.
4. A tool that serves no step, or duplicates another, is retired.
5. When no tool is needed (a step held entirely by an agent's job), the row says so, and names the job's form and its
   code check.
