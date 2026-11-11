# Anti-drift audit (a): decisions since the emergency began, none decided and lost (DEC-1125 (3) (iii) a)

Read `NIGHT-common.md` first. Role: orchestrator helper, Sonnet high, class C1.

## The task
1. Find where the emergency began (START-NEXT-SESSION §2, DECISIONS-IN-FORCE, the register around DEC-1033/1037).
2. **Deterministic first:** write a small script (in `/tmp/gov-os-emg-auditdec/`) that lists every `### DEC-<n>` in
   `docs/DECISION_REGISTER.md` from the emergency's first decision to DEC-1125 with its status line, and checks for
   each: (i) a line in `governance/project/orchestration/DECISIONS-IN-FORCE.md` (or a stated reason it has none:
   superseded, folded, a one-off done); (ii) superseded or changed decisions marked as such in both places (e.g.
   DEC-1101 (1) changed by DEC-1125 (2)); (iii) every decision item with a trigger or a pending action ("after the
   lift", "at the re-pin", "when", "next", an ACT, a ticket to file) has a row in
   `governance/project/orchestration/packages/DECIDED-NOT-DONE.md` with its home ticket (DAEO id or W2 id) or a
   DONE mark with evidence (commit); (iv) the register's version table and "Next free id" agree (DEC-1126).
3. **Then read** the gaps the script finds, and the last 5 days' decisions in full (DEC-1100 onward).
4. **Fix small record drift now** in `DECISIONS-IN-FORCE.md` and `DECIDED-NOT-DONE.md` only: a missing line, a status
   now known (DONE with its commit), a missing home ticket that exists. Each fix cites its source. Never change what a
   decision says; never add a decision. A row whose home ticket does not exist: list it (the ticket audit files
   tickets).

## Paths you may write
`governance/project/orchestration/DECISIONS-IN-FORCE.md`, `governance/project/orchestration/packages/DECIDED-NOT-DONE.md`
(the CTO will not touch them until you return), `/tmp/gov-os-emg-auditdec/**`, and
`governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md` (your report).

## Return
The twelve fields, short: the range checked, counts (decisions, in force, rows), each fix made (file:line, old → new,
source), each gap left with your recommendation (who: CTO, engineer, ACT, owner). Estimate 1-1.5 h.
