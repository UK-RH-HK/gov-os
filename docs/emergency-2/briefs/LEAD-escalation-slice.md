# Lead brief: W2-211, decisions by page slice (a) with the escalation rubric's first slice (F-2; DEC-1236 (1), DEC-1242 T-1 and R-6, DEC-1246 (3)(b))

You are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10). Where this brief leaves a choice, make it and say what you chose in your return.

## Why
The owner approved decisions by page as one feature in two slices (DEC-1236 (1), DB-1 (a)); slice (a) carries the escalation rubric's first slice (DEC-1242 T-1 (b): the record's fields, a computed level, the refusal below the level, `gov decisions answer`; R-6 (a): the level computed from the record's stated facts). DEC-1246 (3)(b) puts it into 0.1.6, in every repository through the kit. This is item 5-4 of `docs/emergency-2/integration/INTEGRATION-PLAN.md` (read its row). Slice (b), the page renderer, is not yours.

## The ticket (new; approved feature)
Open `.tickets/W2-211` on your branch in the form other open tickets use (look at `.tickets/DAEO-rt4s.md`; create it with the repository's ticket tool if one exists, else by hand with a fresh `DAEO-xxxx` id and `wbs_id: W2-211`), `kind: feature`, `specification: docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md`, and these KPI lines, each copied word for word from the spec where the spec has it (Q-5), with its verify from the spec's "How each KPI is verified" table:
- **PG-1, PG-3, PG-4, PG-5, PG-6** (the spec's slice (a), its §"Placement and size" and §KPIs).
- **EL-1 The level computed from stated facts.** A decision record states three facts: `touches` (what it changes: a spec or KPI, a standing decision, the Contract or Charter, shared code, work across streams, kernel text, a secret or paid service, a model or effort, a release, or only its own ticket), `reversible` (yes or no) and `inside` (a worktree, the repository, or outside it). Code computes its level (P3 lead, P2 CTO, P1 owner, or emergency) from those facts by the escalation rubric (golden workflow rule 8 in `docs/emergency-2/GOLDEN-WORKFLOW.md`; `docs/emergency-2/T2-ESCALATION-RUBRIC.md`) and prints the level with the facts that set it.
- **EL-2 A decision below its level is refused.** A record whose `Decided-by` is below its computed level (a P1 record not decided by the owner; a P2 record decided by a lead) is refused with `DECISION_BELOW_LEVEL`, naming the computed level and the facts, at the check every decision-record commit runs (`gov decisions basis --range`) and by `gov decisions answer`; a P1 record without the owner's decision becomes an open package (a card), never an ACCEPTED entry.
- **EL-3 Through the kit.** The record fields, the level rule and the check reach an adopted repository by `gov update` (PG-9's road), and its own decisions are judged by the same rule.

Read the register entries DEC-1225 to DEC-1247 for the entry form PG-4 must write (the newest, DEC-1247, has the CTO's calls written inside the owner's decision: a P2 choice inside a P1 decision, which EL-2 must allow).

Code area (stream F): `src/gov/decisions/`, the decision and package templates and schemas under `template/governance/kernel/`. Stay out of `src/gov/launch/`, `src/gov/dispatch/`, `src/gov/resources/`, `src/gov/rebuild*` (other leads).

## Where
Worktree `/home/usain/gov-os-worktrees/E2-escalation-slice`, branch `e2/escalation-slice` from `w2/integrate`. Never write `docs/DECISION_REGISTER.md` on the live tree; tests use a scratch register.

## Green
LEAD-COMMON's flow: the test designer writes acceptance tests for PG-1, PG-3 to PG-6 and EL-1 to EL-3 under `tests/acceptance/W2-211/` (red on the base; give it the spec, this brief's KPI lines, the `gov decisions` command's files and one example folder); the engineer builds. PG-3 needs `node` on PATH (LEAD-COMMON's command sets it). Then the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue w2-211=e2/escalation-slice --onto w2/integrate --select`; run exactly that list (DEC-1244 X-1). Check the acceptance trailers (LEAD-COMMON).

## Return
Branch and head; each KPI line with its tests and result; the selected suites' summary lines; the level rule as built (facts in, level out, as a table); reds not yours; the C3-trial counts.
