# Copy: the provisional work-sizing rubric (in force, DEC-1208/DEC-1209 (4))

Source: `governance/project/orchestration/packages/PROVISIONAL-RUBRIC.md` (sha256 `3d49895e7c6c585ca89e360ab503a02e0d73c16e13821478ba514ef50ede5c6e`).

# The provisional work-sizing rubric (in force from 2026-11-16 until W2-196 lands; the owner's approval of the ticket, DEC-974)

Every piece of work, code, configuration, machine or operator, is classed before it starts. The class is written in the
commit (`Class: Q|L|S|F`) or the ticket. When in doubt, the higher class.

## Protected areas (never Q)
The guard and its hooks and settings (`.claude/hooks/**`, `.claude/settings*.json`, `~/.claude/settings*.json`); the box's
walls; acceptance tests (`tests/acceptance/**`); memory (the store, retrieval, the measure, the evaluation sets);
`gov close`, `land.py` and the landing check; data migrations; the kernel (`template/governance/kernel/**`, skills, role
files, CLAUDE.md, AGENTS.md); secrets, held-out material; anything that changes a spec, a KPI or a decision.

## The classes
| Class | When (all must hold) | Route | Needs |
|---|---|---|---|
| **Q, quick** | about 30 minutes or less; one commit; revert undoes it; outside every protected area; the touched code already has tests; no spec or KPI change; or a small configuration or permission change with a written rollback | done directly by the CTO or a senior engineer | the affected tests run and stay green; one commit with `Class: Q` and the purpose in its trailers; listed in the owner's digest. Configuration and permission changes: on the owner's yes line. No package, no review, no register entry |
| **L, LITE** | one area, not protected, about half a day or less, reversible | a LITE ticket: a test designer's cases, the engineer, `gov accept`, close | review only if a change could fail open (a narrow check by the golden rule); a ticket record; the owner's approval of the ticket (DEC-974) |
| **S, STANDARD** | several files or one behaviour with KPIs, not protected | a STANDARD ticket (today's) | one independent review by the golden rule; the ticket record; the owner's approval of the ticket |
| **F, FULL** | touches a protected area, or irreversible, or a wide blast radius, or changes a spec or a KPI | a FULL ticket, an ACT for control paths, a CIT-P for the kernel (today's) | review by the golden rule, at most two rounds, then the owner once; the owner's approval of the ticket and of the bytes (ACT yes, CIT-P) |

## Guardrails (the quick lane is never a back door)
1. A protected area is never Q, whatever its size.
2. **Time box:** a Q that passes 30 minutes, needs a second commit, turns a test red or touches a protected path stops,
   is reverted if half done, and comes to the owner as a package for a LITE or larger ticket (DEC-974 still holds).
3. **Spot audits:** weekly, an independent auditor reads every Q commit of the week (or 10, whichever is fewer) against
   this rubric; a misrouted one goes into the owner's digest with its fix.
4. The class-rules (`class-rules.yaml`, class (b) control paths by ACT) and the operator's gates are unchanged: a Q on a
   class (b) path still goes by the operator, with the smallest review its G4 gate needs (one narrow reviewer pass).

## Measured
From today, per change: class, wall time, cost, review rounds and the owner's interruptions, so W2-196 compares before
and after.
