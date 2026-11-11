# An adopted repository's tickets without `Verify:` lines: the ticket and its approach (DEC-1130 (2))

Read `LIFT-common.md` first (scratch only; read-only elsewhere). Role: product-spec helper, Sonnet high, class C2
(DEC-1120). Scratch folder: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/adopt-verify/`.
Read DEC-1130 in the register first, and DEC-1083, DEC-1121/1122 (template 1.0.1), DEC-1052 (readiness by code).

## The problem
`gov brief` (`src/gov/brief/build.py`, line ~160: `KPI_NO_VERIFY` for each KPI line with no `Verify:`; `kpi_rows`)
refuses a ticket whose KPI lines carry no `Verify:` clause. An adopted repository's tickets (from its own tracker, or
written before adoption) will arrive without them, so no brief could be built there. It must land before EXAMIN's
copy (W2-27, `DAEO-h4rh`).

## Work
1. Read how adoption brings tickets in (`src/gov/adopt/`, the adopt skill `template/governance/kernel/skills/adopt/`,
   W2-88 `DAEO-2bdu`, W2-113 `DAEO-g29a`, W2-23 `DAEO-kmcr`), how `gov brief` and the ready check read KPI lines (W2-128
   S10, W2-152 `DAEO-o5x1`), and the ticket template and schema (`template/governance/...` ticket template 1.0.1).
2. Options, each costed in lead-hours with what it keeps and what it risks: (c) `gov brief` (and the ready check) take a
   ticket's acceptance folder or `acceptance_tests.path` as its verification when lines lack `Verify:`, stated in the
   brief; (d) an adoption step that adds `Verify:` clauses (by whom: a product-spec session per ticket, with the owner's
   approval?) and marks them; (e) any better route the code shows, or a combination (e.g. (d) at adoption and (c) as the
   fallback with a recorded warning). Say which keeps "readiness computed by code" (DEC-1083) true for adopted tickets.
   Your recommendation with confidence.
3. Draft the ticket in 1.0.1 form (`TICKET-DRAFT.md` in your folder; next WBS id W2-174 unless taken: check
   `grep -h '^wbs_id' .tickets/*.md`): title, profile, class, `allowed_paths` (narrow), `needs`, `reads`, `waits_on`,
   `depends_on`, KPI lines each with a `Verify:` clause and decision brackets (DEC-1130 (2)), `sources` with DAEO ids
   and DEC ids only, priority so it lands before W2-27, and the note for W2-27's `depends_on`.

## Write
`APPROACH.md` (the options and the recommendation, plain language for the owner) and `TICKET-DRAFT.md`. Return the twelve
fields, short. Estimate 1 h.
