---
name: orchestration
version: "1.1.0"
metadata:
  version: "1.1.0"
description: "Method for running a wave: parallel tickets under ticket leads, integration, decisions, stops, sessions, briefs, commits and status answers."
---

# Orchestration

A method for the orchestrator role and its ticket leads: the way a wave is run. The guard, the launcher and the role file decide what a session does; this skill is the method only and grants nothing (CAP-24.b). Each rule names the decision it follows; a rule that only an orchestrator's prompt held is cited with DEC-537, which ordered it stated here. A project's own values (branches, folders, thresholds, the model) stand as `<placeholders>` (DEC-539). Tests are named in the project's terms: the project's test command, the ticket's acceptance tests, the builder tests (DEC-534). Detail: [briefs-and-returns.md](briefs-and-returns.md).

## Parallel tickets

- Each independent ticket gets its own worktree and branch, cut from the integration branch `<integration branch>`; no two tickets in flight have overlapping paths, and an overlapping ticket waits (DEC-235).
- A ticket lead per ticket is started in that worktree with its identity (the orchestrator role and the ticket's id), from `brief-lead.md` (DEC-236).
- No fixed number of tickets in flight: the eligible tickets, the resource gate and the owner's usage limits decide, each time a slot could open; every countdown says how many and why (DEC-847). A ticket idle on an owner answer frees its slot (DEC-235, DEC-363).
- The resource gate is read before each start: free memory of at least `<free memory>` and a load average below the core count. Heavy tickets count double (DEC-235).
- No worktree is left behind: one whose ticket is closed is removed (DEC-235).

## Integration order

1. The lead returns DONE. The orchestrator verifies the return itself, by its own runs: it reads every KPI clause against the tests and the code, and the governance checks of `gov check` against the last known state (DEC-236, DEC-449).
2. For a FULL ticket a fresh reviewer probes the final code before the merge, and nothing is committed after the probed head (DEC-498) but its passing probe record (DEC-733).
3. Only the orchestrator merges into the integration branch, and never into the main branch (DEC-235, DEC-416).
4. Then the close: `gov close` runs the ticket's tests and the regression on the merge commit. Where the close does not follow the merge directly, a full regression runs (DEC-536): the nightly's, as a close runs the scoped set (DEC-968).
5. Residuals are recorded, and the worktree and the branch are removed (DEC-135, DEC-235).

The merge queue: [integration-queue.md](integration-queue.md). A red nightly: [nightly-sheriff.md](nightly-sheriff.md). An Emergency: [incident-response.md](incident-response.md).

## The ticket loop

The lead runs the loop from `brief-lead.md`, which states each step in full.

- The work order in parallel: a fresh test designer and a fresh implementer at the same time, from the spec, neither reading the other's work (DEC-959 item 7); the tests checked red against the ticket's base for the stated reason; then the verification, on the ticket's acceptance tests, the scoped selection and the builder tests, once (MR-3, DEC-968).
- For a FULL ticket a second review is the last. After it only fail-open holes and losses of work are fixed (DEC-413 names silent changes to tests or ticket files); the rest are residuals (DEC-413).
- The loop count is held by the lead and never disclosed; three consecutive iterations that do not converge end in an escalation (DEC-096).
- A lead returns one of these forms: DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED (DEC-236), then `brief_gaps:` (DEC-943 item 1).

## Decisions

- Delegation: the orchestrator decides a package itself when all of these hold: it is P2 or P3; it is reversible; its recommendation and the proposer's agree; confidence is medium or higher (for a P2 also medium-low, where the owner has widened it as in DEC-416); it changes nothing of the charter, the master rules or the contract's scope; it weakens neither the guard nor containment; it touches neither the held-out path, installs, merges into the main branch nor releases (MR-6, DEC-220, DEC-416).
- A stricter-only decision (the option refuses more, denies more or fails closed, and hinders no action of the owner) is delegated too, where every other condition holds (MR-6, DEC-537; so delegated in DEC-508 and DEC-525).
- A decision is recorded as accepted before the change it authorises, then applied, and a delegated one is listed in the digest of delegated decisions at the next stop; the owner overturns any (DEC-220, DEC-463).
- Everything else goes to the owner as a package from `decision-package.md`, in six parts (DEC-818): at most five packages with the owner at a time, and a P1 may bypass the cap (DEC-220).
- An owner answer is recorded in the decision register as accepted, with who and when, in a commit of its own: the orchestrator's decision-record commit, never `Role: owner` (MR-6, DEC-861, DEC-862).

## Stops

- The orchestrator stops only for owner packages (with the digest), an escalation, an authentication stop or the exit of the wave, and never only to deliver a digest (DEC-220, DEC-250, DEC-420).
- While packages are open, every ticket they do not affect keeps running (DEC-220).
- A stop is one short block, readable on a phone (DEC-537, DEC-948).
- The closed count is taken from the ticket files, and open tickets are given by id (DEC-486).

## Sessions

- A worker's identity (role and ticket) goes through the settings argument, which the launcher builds for a worker and the orchestrator passes for a lead (DEC-371).
- The model `<model>` is named on every launch (DEC-460); no launch sets a compaction threshold (DEC-838).
- Leads and workers run in the background: a lead with the absolute path of the CLI, `<absolute path of the CLI>`, a worker through the launcher; never a bare call in the foreground (DEC-371, DEC-537).- Never two writing sessions in one tree, and never a commit in a tree while a worker's command runs there: containment would attribute the change to the worker (DEC-254, DEC-537).
- On an authentication or access error there is no retry loop: nothing more is started, the checkpoint is written, and the stop is named `AUTH_REQUIRED` (DEC-420).
- The orchestrator reads only a lead's final summary, never its workers' output (DEC-236).

## Briefs

- A session is started from a filled template: `brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md` or `brief-lead.md`. Each carries the standing sentences word for word (DEC-537).
- Every return starts with the twelve fields, each a labelled line: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action (CAP-37). Any payload comes after them. Stop after two identical refusals and return (AR-6).
- Policy 2: reads are open; only secrets, the held-out material's contents (its file names are readable), the counterpart's work on the same ticket and the hidden half of an evaluation set are refused (DEC-820).
- A worker gets only its brief and the decisions that apply, never the orchestrator's notes, the loop count or another worker's output (DEC-096, DEC-537).
- A test designer's brief states behaviour and sources only, never the names of the implementation's private parts (DEC-462).
- Tests are in proportion to the profile: FULL thorough; STANDARD every KPI line's success and failure plus the key edge cases; LITE one test per KPI line; no combinatorial expansion beyond what a KPI demands (DEC-221).
- No worker bulk-copies or clones the tree or a folder of it; single named files are copied (DEC-537).

## Commits

- The trailers stand in the final trailer block, written with `git commit --trailer`: `Task:`, `Role:` and, with the capability ids, `Implements:` (DEC-182, DEC-476).
- A test designer's rewrite after implementation began carries the rewrite reason in the trailer `Rewrite-Reason:` (DEC-491).
- A commit touching a ticket's file names that ticket in `Task:` and holds nothing else (MR-6, DEC-537).
- Shared history is never rewritten, and nobody but the owner pushes (DEC-182, DEC-236).

## Checkpoints and context

- A lead writes a real checkpoint with `gov checkpoint` at each round boundary of its ticket; none is written only to pass the close (DEC-511). A checkpoint is written at every handover (DEC-837 item 3).
- The orchestrator updates its own checkpoint after every merge, close and stop (DEC-537).
- With the session-start and pre-compaction hooks in place the session compacts and continues from the injected checkpoint; it does not stop for context (DEC-250).
- When the checkpoint is older than the state, the state is re-derived from git and the tickets (DEC-537).

## Temp hygiene and protected files

- A session's temporary folder is its own and is removed with it; nothing is left in or read from another session's folders (DEC-386, DEC-537).
## Learning metrics

- The metrics are recorded at each close: KPI disputes; acceptance tests rewritten after implementation began, with reasons; lines against the estimate; wall time from claim to close; merge conflicts; false findings; governance share (DEC-106, DEC-135, DEC-491).

## Status questions

When the owner asks in plain words where things stand, the session runs `gov status --json` and answers from its parts: tickets, open decision packages and gates, readiness, governance share, pause state and health (the doctor summary). Of every part marked not read it says that the part was not read, and of a share not measured that it was not measured. A status question is never answered from recall (CAP-28, DEC-541).

## Followed by hand

These rules are followed by hand: they are not enforced by a mechanism yet (DEC-537). The resource gate is not a command; the launcher does not refuse a launch without a model; `AUTH_REQUIRED` is a stop the orchestrator names, not a mechanism; and leads are not started through the launcher, which starts workers alone.
