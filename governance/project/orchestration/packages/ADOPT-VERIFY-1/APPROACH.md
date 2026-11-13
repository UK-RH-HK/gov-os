# An adopted repository's tickets without `Verify:` lines: the approach (DEC-1130 (2))

For the owner. Written 2026-11-11 by a product-spec helper of the CTO. Estimate used: 1 h of reading and writing.

## The problem in four sentences

`gov brief` refuses any ticket whose KPI lines have no `Verify:` clause. The code is
`src/gov/brief/build.py`: `ready_check` (line 163) raises `KPI_NO_VERIFY` for each such line, and nothing else
in `src/` calls the ready check. A repository that is adopted will bring tickets from its own tracker, written
before adoption, with no such clauses, so no brief could be built there. DEC-1083 says a ticket's readiness is
computed by code, and DEC-1130 (2) asks for the fix to land before EXAMIN's copy (W2-27, `DAEO-h4rh`).

## What the code shows (facts found)

1. **`gov brief` is the only ready check.** It accepts a verify in two forms: `{line, verify}` with text, or a
   plain string with `Verify:` and text after it (`kpi_rows`, `build.py` lines 109-125). The plain-string form
   was kept on purpose, "so today's tickets need no rewrite" (W2-152's Interface).
2. **Adoption brings no tickets in today.** `src/gov/adopt/` has stages A0 to A8 and no code that reads or
   writes tickets. W2-88 (`DAEO-2bdu`) will write the refactoring plan as proposed tickets in the kernel's form,
   but its text asks for "KPIs with success and failure", not for a `Verify:` on each. If that stays so, W2-88's
   own proposed tickets would be refused by `gov brief` once the owner approves them. This is a second case of
   the same problem, and it is cheap to close now (the CTO's note 4 in the draft: one line in W2-88).
3. **The acceptance folder does not exist when the first brief is needed.** The test designer's brief is the
   first brief of a ticket, and the designer is the one who writes `tests/acceptance/<id>/`. A rule that reads
   the folder as the verification therefore has nothing to read for the first role.
4. **The ticket schema lets a line be a plain string** and does not forbid extra front-matter keys, so a marker
   needs no template change (the 1.0.1 template stays as approved at hash `bbfc068e...`).
5. **Many tickets hold YAML comments** (W2-88's front matter does). A tool that re-writes the file with a YAML
   dump would delete them. A tool must edit the text of the lines only.

## The options

Lead-hours count the CTO's or a ticket lead's time, as in the other plans. One new ticket costs about 3 lead-hours
(designer 1, engineer 1, audit 0.5, close and merge 0.5), more when it needs a test-designer round 2.

### (c) `gov brief` reads the acceptance folder when lines have no `Verify:`

`acceptance_tests.path` (for example `tests/acceptance/W2-nn/`) stands in for the missing clauses, with a
statement in the brief.

- **Cost:** about 4 lead-hours (the ticket, plus a rule for the test designer, see below). Per adopted ticket: 0.
- **Keeps:** no work on each ticket; one rule for every repository.
- **Risks:**
  - It fails for the first role. The folder is written by the test designer after its brief. Either the designer's
    brief is exempt (then the designer invents the verification, and the ticket is "ready" with no verification
    stated by anyone), or every adopted ticket deadlocks. Fact 3 above.
  - The check turns coarse. It would test that a folder exists, not that each KPI line has a check. A stale or
    empty folder passes. A line with no test behind it passes.
  - It changes `build.py`, which W2-152 (`DAEO-o5x1`, in progress) and W2-128 (`DAEO-t8mp`) still hold.
- **DEC-1083:** computed by code, yes, but the required field becomes optional for adopted tickets. The meaning
  of "ready" is weaker for them than for ours.

### (d) An adoption step that adds the `Verify:` clauses, and marks them

A `Verify:` pass over the tickets that are about to launch (not over a whole tracker at adoption), by a
product-spec session, with a small tool that checks and writes.

- **Cost:** about 3 lead-hours for the ticket (the tool and the adopt skill's step). Per adopted ticket about 0.2
  lead-hours (one product-spec session of about 10 minutes, and the CTO's read). For EXAMIN's copy, if 20 to 40
  tickets launch, that is 4 to 8 lead-hours spread over the run; the figure is a guess until W2-27 counts its
  tickets.
- **Keeps:** `gov brief` and the ready check stay as they are, strict, and the same for every ticket. Nothing
  about W2-152's accepted tests changes.
- **Who writes, who approves:** a product-spec session writes the clauses from each ticket's lines and the
  repository's `facts.yaml` commands. The owner does not approve each ticket. The owner approves the rule once
  (this ticket's text). Three things check the clauses: the tool by code (a non-empty clause on every line, no
  line changed, the file otherwise unchanged); the ticket's independent test designer, who reads each clause and
  records a disagreement as a finding; and the independent auditor's sample at the next review.
- **Marks:** the tool adds one front-matter line, `verify_pass: <date> <session>`, and each clause it adds is
  appended to the plain line as ` Verify: <clause>`, the form `gov brief` already reads. A reader can see which
  tickets went through the pass, and no schema or template changes.
- **Risks:** a clause written after the fact can be weak (a command that always passes). The mark and the
  designer's review are the answer. The pass costs time per ticket, which (c) does not.
- **DEC-1083:** fully true. The ready check is unchanged, so a ticket is READY by the same code whether it was
  written here or adopted.

### (e) The better route, and the combination

- **(e1) (d) now, (c) later as a recorded fallback.** (c)'s rule is added only if the first adoption shows the
  pass too slow. Because the designer problem stays, (c) would be limited to roles after the designer, and would
  print a warning `KPI_VERIFY_FROM_FOLDER` in the brief. Cost: (d) plus about 4 lead-hours when needed. Not built
  now.
- **(e2) Make the importers write the clauses.** A tracker importer, if one is ever built, would write
  `Verify:` itself. There is no importer, so this has nothing to attach to today; it is the reason W2-88's
  proposed tickets should carry clauses from the start (note 4 of the draft).
- **(e3) Lower the check for adopted tickets by a flag** (a `ready.adopted_since` date in facts.yaml like
  `new_since`). Cheapest in code (about 2 lead-hours) but it is DEC-1083 turned off for exactly the tickets that
  are hardest to trust. Not recommended.

## Which keeps "readiness computed by code" true

(d) does, completely. (c) and (e3) keep the words and weaken the meaning for adopted tickets.

## Recommendation

**(d), with the marker, as the ticket drafted in `TICKET-DRAFT.md` (W2-174).** The check stays strict and unchanged,
which is DEC-1083's point; the cost is a small per-ticket pass, paid only for tickets that launch. (c) is kept as
an option to revisit after EXAMIN's copy, not built now.
Confidence: 70 %. What would change it: if W2-27's tracker has far more than 100 launching tickets without clauses,
the per-ticket cost makes (e1) worth building at once; if the owner prefers one rule with no passes, (c) is
workable only with the designer's brief handled separately.

## Land-before order

The draft depends on W2-152 (`DAEO-o5x1`, for `kpi_rows`, so the tool uses the same reading as the check), W2-88
(`DAEO-2bdu`) and W2-23 (`DAEO-kmcr`), which hold the adopt command and skill. W2-27 then takes the new ticket in
its `depends_on`. The one-line change to W2-88's refactoring-plan KPI is for the CTO to make (see the draft's
note), not for this ticket.
