---
name: orchestration
version: "1.0.0"
description: "Method for running a wave: parallel tickets under ticket leads, integration, decisions, stops, sessions, briefs, commits and status answers."
---

# Orchestration

A method for the orchestrator role and its ticket leads: the way a wave is run. The guard, the launcher and the role file decide what a session does; this skill is the method only and grants nothing (CAP-24.b). Each rule names the decision it follows; a rule that only an orchestrator's prompt held is cited with DEC-537, which ordered it stated here. A project's own values (branches, folders, the ceiling, thresholds, the model) stand as `<placeholders>` (DEC-539). Tests are named in the project's terms: the project's test command, the ticket's acceptance tests, the builder tests (DEC-534).

## Parallel tickets

- Each independent ticket gets its own worktree and branch, cut from the integration branch `<integration branch>`; no two tickets in flight have overlapping paths, and an overlapping ticket waits (DEC-235).
- A ticket lead per ticket is started in that worktree with its identity (the orchestrator role and the ticket's id), from `brief-lead.md` (DEC-236).
- A stated ceiling holds: at most `<ceiling>` tickets in flight. A ticket idle on an owner answer frees its slot (DEC-235, DEC-363).
- The resource gate is read before each start: free memory of at least `<free memory>` and a load average below the core count. Heavy tickets count double (DEC-235).
- No worktree is left behind: one whose ticket is closed is removed (DEC-235).

## Integration order

1. The lead returns DONE. The orchestrator verifies the return itself, by its own runs: it reads every KPI clause against the tests and the code, and the governance checks of `gov check` against the last known state (DEC-236, DEC-449).
2. For a FULL ticket a fresh reviewer probes the final code before the merge, and nothing is committed after the probed head (DEC-498).
3. Only the orchestrator merges into the integration branch, and never into the main branch (DEC-235, DEC-416).
4. Then the close: `gov close` runs the ticket's tests and the regression on the merge commit. Where the close does not follow the merge directly, a full regression runs (DEC-536).
5. Residuals are recorded, and the worktree and the branch are removed (DEC-135, DEC-235).

## The ticket loop

The lead runs the loop from `brief-lead.md`, which states each step in full.

- Tests first, by a fresh test designer, checked red for the stated reason; then a fresh implementer; then the verification, on the ticket's acceptance tests, every earlier suite and the builder tests (MR-3).
- For a FULL ticket a second review is the last. After it only fail-open holes and losses of work are fixed (DEC-413 names silent changes to tests or ticket files); the rest are residuals (DEC-413).
- The loop count is held by the lead and never disclosed; three consecutive iterations that do not converge end in an escalation (DEC-096).
- A lead returns one of four forms: DONE, PACKAGES, ESCALATION or LEAD_CHECKPOINT (DEC-236).

## Decisions

- Delegation: the orchestrator decides a package itself when all of these hold: it is P2 or P3; it is reversible; its recommendation and the proposer's agree; confidence is medium or higher (for a P2 also medium-low, where the owner has widened it as in DEC-416); it changes nothing of the charter, the master rules or the contract's scope; it weakens neither the guard nor containment; it touches neither the held-out path, installs, merges into the main branch nor releases (MR-6, DEC-220, DEC-416).
- A stricter-only decision (the option refuses more, denies more or fails closed, and hinders no action of the owner) is delegated too, where every other condition holds (MR-6, DEC-537; so delegated in DEC-508 and DEC-525).
- A decision is recorded as accepted before the change it authorises, then applied, and a delegated one is listed in the digest of delegated decisions at the next stop; the owner overturns any (DEC-220, DEC-463).
- Everything else goes to the owner as a package from `decision-package.md` (question, why now, options, impact, reversibility, cost, recommendation, confidence): at most five packages with the owner at a time, and a P1 may bypass the cap (DEC-220).
- An owner answer is recorded in the decision register as accepted, with who and when, in a commit of its own with its own decision trailer `<decision trailer>` (MR-6, DEC-537).

## Stops

- The orchestrator stops only for owner packages (with the digest), an escalation, an authentication stop or the exit of the wave, and never only to deliver a digest (DEC-220, DEC-250, DEC-420).
- While packages are open, every ticket they do not affect keeps running (DEC-220).
- A stop is one short block, readable on a phone. The closed count is taken from the ticket files, and open tickets are given by id (DEC-486).

## Sessions

- A worker's identity (role and ticket) goes through the settings argument, which the launcher builds for a worker and the orchestrator passes for a lead (DEC-183, DEC-371).
- The model `<model>` is named on every launch (DEC-460).
- Leads and workers run in the background: a lead with the absolute path of the CLI, `<absolute path of the CLI>`, a worker through the launcher; never a bare call in the foreground (DEC-371, DEC-537).
- Never two writing sessions in one tree, and never a commit in a tree while a worker's command runs there: containment would attribute the change to the worker (DEC-254, DEC-537).
- On an authentication or access error there is no retry loop: nothing more is started, the checkpoint is written, and the stop is named `AUTH_REQUIRED` (DEC-420).
- The orchestrator reads only a lead's final summary, never its workers' output (DEC-236).

## Briefs

- A session is started from a filled template: `brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md` or `brief-lead.md`. Each carries the standing sentences word for word (DEC-537).
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

- A lead writes a real checkpoint with `gov checkpoint` at each round boundary of its ticket; none is written only to pass the close (DEC-511).
- The orchestrator updates its own checkpoint after every merge, close and stop (DEC-537).
- With the session-start and pre-compaction hooks in place the session compacts and continues from the injected checkpoint; it does not stop for context (DEC-250).
- When the checkpoint is older than the state, the state is re-derived from git and the tickets (DEC-537).

## Temp hygiene and protected files

- A session's temporary folder is its own and is removed with it; nothing is left in or read from another session's folders (DEC-386, DEC-537).
- No glob, search or listing runs over the project's governance folder: files there are named one by one (DEC-508).
- The settings file and the held-out file are never read, by any role (DEC-525).

## Learning metrics

- The metrics are recorded at each close: KPI disputes; acceptance tests rewritten after implementation began, with reasons; lines against the estimate; wall time from claim to close; merge conflicts; false findings; governance share (DEC-106, DEC-135, DEC-491).

## Status questions

When the owner asks in plain words where things stand, the session runs `gov status --json` and answers from its parts: tickets, open decision packages and gates, readiness, governance share, pause state and health (the doctor summary). Of every part marked not read it says that the part was not read, and of a share not measured that it was not measured. A status question is never answered from recall (CAP-28, DEC-541).

## Followed by hand (Wave 2)

These rules are followed by hand: they are not enforced by a mechanism yet (DEC-537). The resource gate is not a command; the launcher does not refuse a launch without a model; `AUTH_REQUIRED` is a stop the orchestrator names, not a mechanism; and leads are not started through the launcher, which starts workers alone.
