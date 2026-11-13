# The owner's terms — a glossary (two lines each)

**The basis** (DEC-1052). One question judges everything: does it help deliver tests and code that match the KPIs and
the spec, with less drift? Five tests follow it, and anything that fails them is lifted or removed (`INTENT-DEC-1052.md`).

**The basis as a standing practice** (DEC-1052). Every rule, gate, check or KPI line, old or new, is held to the basis:
at adoption, on symptoms in the logs, and in a weekly review with measured costs; what fails goes to the owner first.

**DEC-1010, how reviews converge.** A moderator sorts each finding against the ticket's own scope; it blocks only if it
is in scope, reachable in ordinary work, and fails open or loses work. At most two review rounds, then the owner once.

**READY and DONE.** READY means the work may go ahead (a review's verdict, or a ticket's filled template); DONE means it
is finished. Both are computed by code from required fields (`verdict.py` and its kind), never declared by an agent.

**The templates** (DEC-1050, DEC-1052). One short, shared template per role, ticket and brief, filled from the ticket and
a tested facts file: the right paths, the commands as scripts, how to report; product-spec writes them, the CTO approves.

**The path-map roles** (DEC-1052 G-14). Each role may read and write only its paths in the path map: the engineer never
reads the acceptance tests, the test designer never the engineer's new code. Simple path checks, no shell guessing.

**The five guard rules.** The builder never writes acceptance tests; reviewers write only their records; no reading
secrets, the held-out material or an evaluation set's hidden half; no installs without the owner.

**Ordinary work / fails open / loses work** (ADR-0001, DEC-1010). The test for a finding: an honest agent's mistake in
normal work (not a deliberate attack), which would let something wrong through (fails open) or destroy work.

**ACT.** A file of exact commands for the owner's operator to run, for changes to the machine outside the repository
(installs, services, the crontab, the pinned `gov`); a hold stops the CTO's commits until the owner says it is done.

**P1 / P2 / P3** (DEC-957). How far a decision reaches: P3 the Senior Engineer decides (inside one ticket); P2 the CTO
approves (another stream, a ticket's scope); P1 the owner decides (the spec, a standing rule, security, cost, an ACT).

**Package.** A written decision request to the owner in six parts: context, what happened, why it matters, options with
costs, the recommendation, and what it blocks; saved in `governance/project/orchestration/packages/`.

**Delegated decision.** A P2 or P3 the CTO decides itself (reversible, within the owner's decisions), recorded in the
register for the owner to overturn at any time.

**The re-pin.** Replacing the installed `gov` (`~/.local/bin/gov`, a pinned, hash-checked build) with a newer commit, by
an ACT with its checks and a rollback; agents' hooks and searches run the pinned copy, not the working tree.

**Window 1 / window 2.** The re-pins of the emergency: window 1 (2026-11-02, `pin-a7182f6c`, the query vector from any
device); window 2 (to come) carries the memory branches and the emergency fixes once they are merged.

**The freeze** (DEC-1032). No new ticket or lead starts except the infrastructure work; it lifts only on the owner's
word, after the assessment and redesign of the ticket's path.

**The emergency** (DEC-1033, raised by DEC-1047, then DEC-1051). Everything stops except the fixes the owner names; now:
everything stopped until the refactoring and the re-pins, nothing scheduled but the dispatcher.

**The lift.** The owner's word that ends the emergency and the freeze, after the full suite is green on the refactored
repository; tickets then resume and the finished ones are closed formally.

**The refactoring** (DEC-1039, DEC-1052). The plan D-0 to D-11 in `packages/LIFT-1/P1-PLAN.md`: clean-up, the memory
merges and re-pin, the tools, the lifts, the test cut, the templates, the WBS refactor, the full suite, the lift.

**The full suite / the nightly.** Every test, run once on the refactored repository on the owner's word (D-10); the
nightly that ran it each night is stopped (DEC-1049) until the owner says otherwise.

**Scoped tests.** Only the tests a change can reach (`select_tests.py`), plus the ticket's own acceptance tests; what
every lead, landing and close runs between full suites (DEC-968).

**The merge queue / landing.** How a finished ticket reaches `w2/integrate`: its merge is tested once, then merged and
closed in one step (`land.py`); "landing" is that run.

**Attribution.** Deciding whether a failing test was caused by the change being landed: re-run once with it and once
without it (Q-1, approved), instead of the old three-and-three against a nightly clone.

**The landing check (G-1).** Before a ticket lands, every commit in its range that changes an acceptance test must
carry `Role: independent-test-designer` or `Role: owner`, or the landing refuses, naming the commits (`tools/land.py`).

**The structural pass (R1-21).** A 10-second run of the cheap record checks (schema, graph, claims, path map and the
like) after each landing and each CTO record commit; it reports a notice, never refuses (`tools/structural_pass.py`).

**The dispatcher.** The program cron runs every minute: it starts leads from the CTO's ready list, lands approved
tickets, collects returns into the inbox, and writes the machine's true status.

**The Load Balancer** (DEC-1039 (1b)). The dispatcher's admission by measured peaks on CPU, memory and the GPU, pairing
GPU-heavy with CPU-heavy work; it keeps the GPU within its budget and raises an alert before a spill or a crash.

**Heavy slots / the gate.** Three machine-wide slots for test runs (`heavy_slot.sh`), each confined to its own CPUs;
every heavy job goes through them so the machine never overloads.

**The shared reranker / the embedders.** The models memory uses: two embedding servers on the GPU (11434 shared, 11435
for questions) and one shared reranker service (W2-112) instead of one reranker per session.

**Memory / the stores / W2-61's measure.** The lexical and semantic indexes agents search with `gov retrieve`; W2-61's
measure (hit@5 against a floor of 85 %) is the standing proof that memory finds what is needed.

**The sentinel / the dead-man's switch.** A small Claude session in tmux that watches the CTO's session and pushes the
owner's phone only if the CTO has stalled; the stand-by file tells it the CTO is waiting on purpose.

**The CTO / leads / workers.** The CTO is this orchestrator session; a lead runs one ticket in its worktree; workers
(test designer, engineer, reviewer, product-spec, research) do the parts, each in its role.

**Wave 2 / EXAMIN's copy.** Wave 2 is the current build of the Gov OS; EXAMIN's copy is the first adoption on a copy of
a real product repository, which starts when its entry criteria (K9) are met, never because a date arrived.

**The register / DECISIONS-IN-FORCE.** `docs/DECISION_REGISTER.md` holds every decision with its reasons; the short
list in `governance/project/orchestration/DECISIONS-IN-FORCE.md` holds what is in force now.
