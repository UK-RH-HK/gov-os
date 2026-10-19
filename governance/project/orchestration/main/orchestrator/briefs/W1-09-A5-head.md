You are the ticket lead for ticket `DAEO-topz` (`W1-09`, "Ticket vendoring, claims and READY rule"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-09` on branch `w1/W1-09`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). FULL: after green, a reviewer (brief A3).

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `template/governance/kernel/bin/tk`, `src/gov/tasks/**`, `tests/unit/tasks/**`.
- Its dependencies are closed: W1-07 (the `gov` CLI skeleton), W1-08 (the ticket schema and template; tickets carry `state_class`, DEC-229, "W1-09 adds the key when a ticket is created") and W1-10 (the store and record graph: `gov.store.load`, `gov.records.*`; DEC-274 to DEC-278; in this repository a ticket's `depends_on` holds WBS ids while its `id` is the tk id, see "W1-10 residuals" in `governance/project/bootstrap.md`).
- The ticket script is installed at `~/.local/bin/tk` (wedow/ticket v0.3.2) and recorded in `governance/project/tool-registry.yaml` with its sha256; the vendored copy goes to `template/governance/kernel/bin/tk`. The source of the copy is the installed script on this machine: nothing is downloaded and nothing is installed. "Verified by gov doctor" names a command W1-27 builds; what this ticket can show of it is a point for the test designer.
- The live tickets are in `.tickets/` in the main tree and are edited only by the main orchestrator. Every test builds its own tickets, claims and `tests/acceptance/<id>/` folders in a temporary project; no test writes this worktree's `.tickets/` or creates `.tickets/.claims/` here.
- Things the test designer must look at and not guess; each is a decision package if the sources leave it open:
  - the public interface: `src/gov/cli/**` is not in this ticket's paths, and how a command ticket wires into `src/gov/cli/main.py` is an open owner question for another ticket (W1-25 DP-1). So test through a Python interface under `gov.tasks` (as W1-10 did under DEC-275) unless the registry already dispatches; say which reserved `gov` commands, if any, this ticket would implement, and do not revise their `NOT_IMPLEMENTED` cases unless it does;
  - the claim convention: the lock file's name and content under `.tickets/.claims/` (O_EXCL), who "the holder" is (role, session, ticket lead), how a claim is released, and a stale claim left by a dead session;
  - the READY rule's three inputs: "claimed", "acceptance tests directory missing" (`tests/acceptance/<wbs id>/` or `<ticket id>/`: see how the existing suites are named), and "specification is not closed" (where a ticket's specification status is read from, given that readiness records are W1-12 and W1-13);
  - "a mandatory input absent or superseded" (CAP-31.d): which ticket field names its inputs and how superseded is known (the record graph's SUPERSEDES edges, DEC-277);
  - "waiting on an open decision package" (CAP-34.e): where an open package is recorded before W1-34 (the decision-package template) and W1-11 (the decision checker) exist.
- Described behaviours for the reviewer (DEC-136): two claims raced from two processes; a claim on a closed ticket; a claims folder that is a symbolic link; a ticket id with a path separator.

## What you do, in order

1. **Test design** (brief A1, a fresh designer, profile FULL, DEC-221; every covers id, CAP-23.a, CAP-31.c, CAP-31.d, CAP-34.e, gets at least one test).
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh). Estimate 100 LOC; proportion rule DEC-135.
4. **Verify** every suite and the validator. Suites of tickets still in flight elsewhere (W1-46, W1-49, W1-50, W1-25, W1-15) may be red or absent on this branch from their own tickets; W1-50 is red by design (26 failed, 17 passed). Confirm that and report them apart.
5. **Reviewer** (brief A3), with the described behaviours above.

