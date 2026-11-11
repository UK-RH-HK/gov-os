# The `Verify:` pass on the tickets not yet reviewed (DEC-1130 (1))

Read `LIFT-common.md` first, **with one change: you edit `.tickets/*.md` files in the main tree**
(`/home/usain/Dynamic-Agentic-Engineering-OS`), only the KPI lines named below, only in tickets that pass step 1; you
never commit (the CTO does). Report to `.gov-runtime/scratch/orchestrator/drafts/verify-pass/REPORT.md`. Role: product-spec
helper, Sonnet high, class C1 (DEC-1120). Read DEC-1130, DEC-757 (6), DEC-1083, DEC-1121 in the register first.

## 1. Which tickets (the list is the finding; be strict)
From `gov plan --open` (the open and in-progress tickets), run `gov brief lead <ticket> --run tests` (or `--run build`
for one past tests) for each and keep those refused with `KPI_NO_VERIFY`. A ticket is **reviewed**, and so **out of
this pass** (DEC-757 (6): its file is never edited after its review; it launches on a hand-built brief), if any of these
holds: a review or probe record names it (`governance/project/orchestration/reviews/`, `.gov-runtime/scratch/orchestrator/reviews/`,
`docs/probes/<id>/`), its acceptance folder exists with a TESTS-READY commit, a commit subject names its review round,
or its status is in_progress with work merged. When unsure: out, and say why. Never touch a closed ticket.

## 2. The line form
Each KPI line without a `Verify:` clause gains one, before its decision brackets, in the form the 1.0.1 tickets use
(read two, e.g. `.tickets/DAEO-ylsh.md`, `.tickets/DAEO-61vm.md`): `Verify: <the observable check: a planted case, a
command and what it prints, a record and what it holds>`. The clause states how the line's **own words** are checked;
it never narrows, widens or re-words the line. If a line cannot be given a check without changing what it says, leave it,
and list it (the owner's call). Confirm with `gov brief` after: the ticket no longer refuses on KPI_NO_VERIFY (other
refusals, e.g. DEPENDS_NOT_CLOSED, stay and are listed).

## Checks
Each edited file's front matter parses; the structural pass (`python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS`)
ok; `git diff --stat` touches only `.tickets/`.

## Return
The twelve fields, short; the in/out table (ticket, reviewed?, why, lines given a Verify, lines left); `gov brief`
before and after per ticket. Estimate 1 to 1.5 h.
