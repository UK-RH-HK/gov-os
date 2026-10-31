# Orchestration: briefs, returns and standing decisions

A reference file of the orchestration skill, one level below `SKILL.md`. It states; the guard decides, and nothing
here grants a permission (CAP-24.b). A project's own values stand as `<placeholders>` (DEC-539).

## The common brief checklist

Every brief carries these; each role's template adds its own (the roles specification approved by DEC-957).

| # | Item |
|---|---|
| C1 | Identity check first: `GOV_ROLE`, `GOV_TICKET`, tree and branch; stop if anything differs |
| C2 | The ticket: its ids, profile, allowed paths and KPI lines |
| C3 | The sources and the decisions that apply, by id |
| C4 | The guard's rules, and Policy 2 (c) where it applies |
| C5 | What it writes, and what it never writes |
| C6 | Memory: `gov retrieve` first (DEC-836); large questions in batches (DEC-860); small code-graph queries (DEC-859) |
| C7 | The code under test: the worktree's own code, set per command, where it runs tests (DEC-732) |
| C8 | The machine: its scratch budget and temp folder, the disk check before heavy runs, no tree copies (DEC-898) |
| C9 | Commits: `Task:`, `Implements:` (ids only), `Role:`, in the final block; no amend, rebase or push |
| C10 | Packages go to whoever started it, in six parts; never to the owner |
| C11 | A checkpoint at every handover (DEC-837 item 3) |
| C12 | The return: the twelve fields first; the two-refusal stop; `AUTH_REQUIRED` |

## The return (CAP-37, AR-5, AR-6, DEC-420)

Every return, of every role, is one message, its last. The twelve fields come first, each as a labelled line (the
label at the start of a line, a colon, at least one word; "none" where there is nothing); any payload (JSON lines,
a probe record's content and the like) comes after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

- **Stop after two identical refusals and return:** refused twice for the same call, the session stops and says
  so; there is no third try (AR-6).
- An authentication or access error (401, 403, "Failed to authenticate", "access grant"): nothing more starts, and
  the session returns with status `AUTH_REQUIRED` (DEC-420).
- A lead's return adds `brief_gaps:` right after the twelve fields, one line per gap
  (`<what was missing> | <where it belonged> | <minutes, measured or estimated, so marked>`), or
  `brief_gaps: none` (DEC-943 item 1).
- Until a mechanism checks returns, the lead checks each worker's and sends back one that lacks a field, naming
  it (DEC-793).

## Policy 2: reads open, four refusals (DEC-820)

Agents read freely: the whole repository, its history, other worktrees, and what their own retrieval and searches
return. Only four things are refused:

- (a) secrets and keys; a secret is never printed;
- (b) the contents of the held-out qualification material; its file names may be seen;
- (c) the counterpart's work on the same ticket: the implementer (engineer or product-spec worker) never reads the
  ticket's acceptance-test code, but may run the tests and see their names, results and failure messages; the test
  designer never reads the ticket's implementation (the files the ticket's branch changes against its base, other
  than its own tests) and drops unread any retrieval result under it;
- (d) the hidden half of any evaluation set, by whoever it measures.

Reviewers and auditors read everything, tests and code alike. Writes stay inside the ticket's paths. Where the
guard still refuses a read this policy opens, the session takes the refusal, never tries another spelling, and
counts it in its return (DEC-820 item 6). Rule (c) is kept by the briefs; the guard keeps at least these five
rules (DEC-953 item 2, DEC-954): only the independent test designer writes the acceptance tests; no reads of the
hidden half of an evaluation set or of the held-out material; no reads of secrets; no installs without the owner;
reviewers and auditors write only their own review and audit records.

## The decision-record rule (DEC-861, DEC-862)

They changed DEC-724, under which the owner committed the owner's entries with `Role: owner`.

- The orchestrator commits the records of the owner's decisions (the register, the plan, the prompt, the briefs,
  the path map) as soon as they are written, with `Role: orchestrator`, `Task: decision-record` and
  `Decided-by: owner (<channel>, <date>)`. Nothing is left staged for the owner.
- It never signs as the owner, and it never pushes: the owner's push is the owner's acceptance. Its digest lists
  every decision recorded since the owner's last push.
- Entries that the close reads only from a `Role: owner` commit (the known-red lists, escalation lifts) stay the
  owner's own commits until the project reads the push as the acceptance; `Decided-by` alone never counts, since it
  would fail open (DEC-862 (a), (c)).
- No worker and no lead puts `Role: owner` or `Decided-by:` on a commit.

## The escalation rubric (DEC-957)

- **P3, the stream's Senior Engineer decides and logs it** (the orchestrator, where there are no streams):
  reversible; inside one ticket's scope and paths; no change to the spec, the KPIs or any standing decision; no
  effect on other streams; a delay under half a day.
- **P2, the Senior Engineer decides, the orchestrator approves:** touches another stream or shared code; changes a
  ticket's scope or KPIs within the approved spec; changes the plan's order; delays a milestone by up to a day;
  revises older tests under an existing decision.
- **P1, the lead and the Senior Engineer recommend, the orchestrator amends or escalates, the owner decides:**
  changes the spec, the Contract, the Charter or a standing decision; weakens any guard rule or anything that fails
  open; irreversible or destructive; secrets or security; cost, installs or paid services; `<the project's own P1
  items>`; a milestone slipping more than a day.
- **Emergency:** a secret exposed, a risk of losing data, the disk below its floor, or the guard failing open: stop
  the affected work at once, then P1.
- Installs: only the orchestrator's own session asks the owner; every other session, leads included, raises an
  install as a P1 in its return.
- A package has six parts (DEC-818): the context; what happened, with the evidence; why it matters; the options,
  each with its consequence, cost and risk; the recommendation and confidence, with the classification of any
  findings (DEC-809); what it blocks and what waiting costs.

## The exit audit's reading of MR-3 (DEC-430)

An exit audit brief states DEC-430, the owner's reading of MR-3: the core tests for every KPI line are written by
the independent test designer, not by the implementer; cases found in review may be added afterwards, by the test
designer only, red before their fix (DEC-136). This is how MR-3 is met, not an exception to it. Under the work
order in parallel (DEC-959 item 7) the designer writes them at the same time as the implementer, from the
specification, never reading the implementation; the auditor checks that independence.

## Standing decisions in the briefs (DEC-791 (ii))

Each in the part that holds in any repository; entries scoped to one repository belong in its project prompt.

| Decision | The rule | Where it stands |
|---|---|---|
| DEC-715, DEC-731 | One stable launch command starts leads and workers and builds the whole invocation; a session starts one with the Bash tool's own background run, never a trailing `&`; a denied launch is LAUNCH_BLOCKED with the exact denial, and no other form is tried | lead brief; skill, Sessions |
| DEC-719 | A rebuild of the store is a full rebuild, never one without embeddings, and never in a tree while a worker's command runs there | lead, engineer and product-spec briefs |
| DEC-732 | In a ticket worktree every test run and verification command runs that worktree's own code, set per command, never in the session's settings; the lead's verification shows where the code was loaded from; the rule is in every brief, word for word | every brief |
| DEC-733 | A FULL ticket's lead commits the reviewer's probe record under `docs/probes/<ticket id>/`, a passing one only; it is the one documentation path a lead writes | lead and reviewer briefs |
| DEC-847 | No fixed number of tickets in flight: the eligible tickets, the measured resource gate and the owner's usage limits decide; a ticket idle on the owner does not count; every countdown says how many and why | skill, Parallel tickets |
| DEC-750, DEC-754 | Every merge carries `Task:`; never `-s ours`; never a conflict resolved by dropping the ticket's side; never removing what git's own merge of its parents keeps; a conflict that cannot keep both sides' intent is a package | lead brief; skill, Integration |
| DEC-757 item 6 | Never edit an open ticket's file on the integration branch after its review | skill, Integration |
| DEC-766 | The known-red lists only shrink; an addition comes to the owner as a package first | lead brief; skill, Decisions |
| DEC-768 item 4 | No hard-block check is weakened to let a close pass | every writing brief; skill, Integration |
| DEC-779 | A guard hole is a row, not a round, when it needs a precondition no session can create through the guard, or only unsandboxed sessions can reach it | lead and reviewer briefs; skill, The ticket loop |
| DEC-780 | A load-sensitive case is never retried to let a close through; where the project keeps a quiet window for closes, no lead starts during one | skill, Integration |
| DEC-787 | Every report of the orchestrator ends with one line `OWNER_ACTION: <P1, P2, COMMIT or none> <ids> - <one-line summary>` | skill, Stops |

## Supersession in the briefs (DEC-866)

The briefs and this skill teach the rules now in force: a checkpoint at every handover and the model's full window,
with no early stop for context (DEC-837, DEC-838); reads open under Policy 2, the held-out material's file names
readable (DEC-820); no fixed number of tickets in flight (DEC-847); the owner's decisions recorded by decision-record
commits (DEC-861); the test designer and the implementer at the same time from the spec (DEC-959 item 7).
