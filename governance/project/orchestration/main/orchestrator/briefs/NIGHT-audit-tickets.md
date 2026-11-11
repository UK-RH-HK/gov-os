# Anti-drift audit (c): every open and in-progress ticket against this week's decisions (DEC-1125 (3) (iii) c)

Read `NIGHT-common.md` first. Role: product-spec helper, Sonnet high, class C1.

## Why
After the lift, `gov plan` builds the ready lists in batches from the tickets' fields. Wrong `reads`, `needs`,
`waits_on`, `deps`/`depends_on`, status or role give wrong batches. This week's decisions also changed what a ticket
must carry.

## The task
1. Read the rules: the ticket schema and template 1.0.1 (`template/governance/kernel/` ticket template and
   `schemas/ticket.schema.json` or where they live; DEC-1121, DEC-1122: the `class` field), RUBRIC-2 (DEC-1120: model
   and effort by class), the guard's new rules this week (DEC-1119 and the W2-141 rebuild; read the register), the rule
   that **closed tickets are never edited**, and how `gov plan` reads `reads`, `needs`, `waits_on`, `deps` (find it
   under `src/gov/plan*` or by `gov plan --help`; read, do not change).
2. **Deterministic first:** a script in `/tmp/gov-os-emg-audittk/` over `.tickets/*.md` with status open or
   in_progress: schema-valid (the repository's own validator if one exists: `gov check` family or a schema check);
   `class` present and one of the allowed values; `role` matches the assignee and the class; every `deps` /
   `depends_on` / `needs` / `waits_on` id exists, and none points at a closed ticket as a wait; no cycle
   (`tk dep cycle`); `wbs_id` unique; `sources` ids resolvable (the context check: `python3 -m gov.context.context_check`
   with `PYTHONPATH=<main>/src` reads `0 error(s)`). Then `gov plan` (read-only form, e.g. `--ready` or `--dry-run`)
   to see the batches; note anything odd.
3. **Then read** each ticket the script flags, and every ticket touched by this week's decisions (DEC-1112 to
   DEC-1125: RUBRIC-2 through W2-33 and W2-60a, the template, set-up A, W2-115's trailer switch, W2-88's audit lines,
   W2-155).
4. **Fix small record drift now** in open and in-progress tickets only: a missing `class`, a dangling or missing wait,
   a wrong role, a missing source that the KPI brackets cite. Touch only the offending lines (many tickets are in
   progress in other worktrees). **Never** change KPIs, acceptance criteria, scope, allowed paths or status, and never
   edit a closed ticket. Skip `DAEO-ar89` (filed tonight) unless it is wrong.

## Paths you may write
`.tickets/*.md` (open and in-progress only, offending lines only), `/tmp/gov-os-emg-audittk/**`, and
`governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md` (your report). Another helper may create new
tickets (W2-156 and up) tonight: leave those alone.

## Return
The twelve fields, short: counts (open, in progress, flagged, fixed), each fix (ticket, field, old → new, source),
what needs the CTO or an engineer, and the `gov plan` batches as they read after your fixes (ids per batch). Estimate
1.5 h.
