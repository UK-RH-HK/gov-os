---
name: orchestration
version: "1.1.0"
description: "Method for running a wave: parallel tickets under ticket leads, integration, decisions, stops, sessions, briefs, commits and status answers."
---

# Orchestration

A method for the orchestrator role and its ticket leads. The guard, the launcher and the role file decide what a session does; this skill grants nothing (CAP-24.b). A project's own values stand as `<placeholders>` (DEC-539); tests are named in the project's terms (DEC-534). A rule only an orchestrator's prompt held cites DEC-537. The briefs, returns and standing decisions in full: [briefs-and-returns.md](briefs-and-returns.md).

## Parallel tickets

- Each ticket gets its own worktree and branch, cut from `<integration branch>`; no two tickets in flight have overlapping paths (DEC-235). A lead per ticket starts from `brief-lead.md` (DEC-236).
- No fixed number of tickets in flight: as many leads as the eligible tickets, the measured resource gate and the owner's usage limits allow, decided each time a slot could open. A ticket idle on an owner answer does not count; every countdown says how many are in flight and why (DEC-847).
- No worktree is left behind (DEC-235).

## The work order (DEC-957, DEC-959)

- The spec's KPIs drive two sessions at the same time: the independent test designer, in a tests worktree of its own, and the engineer (or product-spec worker), in the ticket's worktree; one writer per worktree, neither reads the other's work (DEC-959 item 7, DEC-963). The test designer retrieves from the integration branch's store only.
- The engineer builds to the spec, never to the tests; once the lead has merged the tests it runs them once, reading results only. The QA engineer reads tests and code, changes neither, writes only its findings report (DEC-957).
- **Tests run no more than this** (DEC-959 item 1, DEC-968): the lead runs the scoped set once before returning; the QA engineer and the reviewer re-run nothing; the merge queue or the close runs the scoped set once on the merged result; the full suite runs only in the nightly.

## Integration

1. The orchestrator verifies a DONE return itself: every KPI clause against the tests and the code (DEC-449), and `gov check` (DEC-236).
2. For a FULL ticket a fresh reviewer probes the final head before the merge; nothing is committed after it but its probe record (DEC-498, DEC-733).
3. Only the orchestrator merges into the integration branch (DEC-236); merges into the main branch are the owner's (DEC-416). Every merge carries `Task:`, never uses `-s ours`, never drops the ticket's side of a conflict and never removes what git's own merge keeps (DEC-750, DEC-754).
4. The close: `gov close` on the merge commit (DEC-536). A close is refused only by a failure its change caused (DEC-968 item 2); no load-sensitive case is retried to let it through (DEC-780); no check is weakened (DEC-768 item 4).
5. Residuals are recorded; the worktree and branch are removed (DEC-135, DEC-235). An open ticket's file is never edited on the integration branch after its review (DEC-757 item 6).

The merge queue: [integration-queue.md](integration-queue.md). A red nightly: [nightly-sheriff.md](nightly-sheriff.md).

## The ticket loop

The lead runs it from `brief-lead.md`: tests and implementation in parallel; red against the ticket's base; one verification; for FULL a review, at most two per declared round (DEC-413, DEC-916); a guard hole only unsandboxed sessions can reach is a row (DEC-779). The lead holds the loop count; three non-converging iterations end in ESCALATION (DEC-096). It returns DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, then `brief_gaps:` (DEC-943 item 1).

## Decisions

- Delegation: the orchestrator decides a package itself when it is P2 or P3, reversible, its recommendation and the proposer's agree, confidence is medium or higher, and it touches neither the charter, the master rules, the contract's scope, the guard, containment, the held-out material, installs, merges into the main branch nor releases (MR-6, DEC-220, DEC-416). A stricter-only option is delegated too (DEC-537).
- **The escalation rubric** (DEC-957): P3 the stream's Senior Engineer decides and logs; P2 the Senior Engineer decides, the orchestrator approves; P1 the owner decides; Emergency stops the work at once, then P1. Each level's test: [briefs-and-returns.md](briefs-and-returns.md). An Emergency: [incident-response.md](incident-response.md).
- Packages go to the owner in six parts (DEC-818); only the orchestrator contacts the owner (DEC-850, DEC-855). At most five open with the owner; a P1 may bypass the cap (DEC-220).
- **Decision records** (DEC-861, DEC-862): the orchestrator commits the records of the owner's decisions itself, as soon as they are written, with `Role: orchestrator`, `Task: decision-record` and `Decided-by: owner (<channel>, <date>)`; never `Role: owner`. The owner's push is the acceptance. Entries the close reads only from the owner's own commit (known-red lists, escalation lifts) stay the owner's commits until the project reads the push as the acceptance; `Decided-by` alone never counts. No worker or lead puts `Role: owner` or `Decided-by:` on a commit.
- **Supersession** (DEC-866): the old entry is marked at once; everything that cites or enforces it is swept by id and by value and updated, or kept with a recorded reason.
- The known-red lists only shrink; an addition comes to the owner as a package first (DEC-766).

## Stops

- The orchestrator stops only for owner packages, an escalation, an authentication stop or the end of the wave (DEC-220, DEC-250, DEC-420); every ticket a package does not affect keeps running.
- A stop is short and readable on a phone (DEC-537); the closed count comes from the ticket files, open tickets by id (DEC-486). Every report ends with one `OWNER_ACTION:` line (DEC-787).

## Sessions

- Workers start through the launcher, which sets their identity (DEC-371); one stable launch command for leads as well as workers (DEC-715), run by the Bash tool's own background run, never a trailing `&` (DEC-731). A denied launch is LAUNCH_BLOCKED, with no other form tried.
- The model is named on every launch (DEC-460), with the effort for the role (DEC-839). Every session uses its model's full window; no launch sets a compaction threshold (DEC-838).
- Never two writing sessions in one tree; never a commit there while a worker runs (DEC-537, DEC-254).
- An authentication or access error: nothing more starts, the checkpoint is written, the stop is `AUTH_REQUIRED` (DEC-420).
- Only the orchestrator's own session asks the owner for an install; others raise it as a P1 (DEC-957).
- The orchestrator reads only a lead's final return (DEC-236).

## Briefs and returns

- Every session starts from a filled template (`brief-test-designer.md`, `brief-engineer.md`, `brief-product-spec.md`, `brief-reviewer.md`, `brief-lead.md`) carrying the standing sentences word for word (DEC-537) and the common checklist.
- **Every return starts with the twelve fields**, each a labelled line: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action (CAP-37). **Any payload comes after them.** **Refused twice for the same call: stop and return** (AR-6). A lead checks each worker's return and sends back one that lacks a field (DEC-793).
- **Policy 2** (DEC-820): reads are open; only secrets, the held-out material's contents (its file names are readable), the counterpart's work on the same ticket and the hidden half of an evaluation set are refused. The counterpart rule is in each writing worker's brief. A read the guard still refuses is taken, never respelled.
- A worker gets only its brief and the decisions that apply (DEC-096). A test designer's brief states behaviour only (DEC-462). Tests in proportion to the profile (DEC-221).
- The code under test is the worktree's own, set per command, word for word in every brief (DEC-732). A rebuild is a full one (DEC-719).
- Reviewer briefs carry the judgement rules (DEC-801, DEC-808). An exit audit brief states DEC-430: the core tests for every KPI line are the independent test designer's; review cases are added later by it alone.
- No session copies the tree or a folder of it.

## Commits

- `Task:`, `Role:` and `Implements:` (decision or Contract ids only) in the final trailer block (DEC-182, DEC-476). A rewrite after implementation began carries `Rewrite-Reason:` (DEC-491).
- Shared history is never rewritten; only the owner pushes (DEC-182, DEC-236).

## Checkpoints

- A lead runs `gov checkpoint` at each round boundary (DEC-511). A checkpoint is written at every handover: a worker's return, a merge, a package, a compaction (DEC-837 item 3). The session continues from the injected checkpoint after compaction (DEC-250); a checkpoint older than the state is re-derived from git and the tickets (DEC-537).

## Learning metrics

Recorded at each close: KPI disputes; acceptance tests rewritten after implementation began, with reasons; lines against the estimate; wall time; merge conflicts; false findings; governance share (DEC-106, DEC-135, DEC-491).

## Status questions

When the owner asks where things stand, run `gov status --json` and answer from its parts; say which parts were not read and which shares were not measured; never answer from recall (CAP-28, DEC-541).

## Followed by hand

Not enforced by a mechanism yet (DEC-537): the resource gate; a launch without a model; `AUTH_REQUIRED`; the twelve-field check; leads started by hand where the launcher has no lead role.
