# Lead brief: the fixes W2-81's proving run on 0.1.4 found that need no owner decision (fixes under W2-52, W2-88 and W2-81)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `w2-81-fixes`; worktree
`/home/usain/gov-os-worktrees/E2-w2-81-fixes`, branch `e2/w2-81-fixes` from `w2/integrate`. **Do not merge.**

**Read first:** `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` (the whole plan section; the reason ids R1 to
R11 it uses), the run record on branch `e2/w2-81-proving-run` (`docs/plan/wave-2/w2-81-proving-run/`) and the run folder
`~/gov-os-runs/W2-81/run-0.1.4/`. Never open the hidden half (`~/gov-os-eval/**`) or the manifests outside the run folder.

**All of this is fixes** (no new ticket, DEC-1219 (6)): each recorded in its owning ticket's record (append a
`## Fix: ... (W2-81's proving run on 0.1.4)` section with the lines and their verify), the ticket left closed or as it is,
the failing test first by the test designer, every commit `Task: <owning ticket>` and `Fix: <one line>`, all trailers in
ONE final paragraph with no blank line inside it.

## The fixes (the analysis's ids)
1. **A2, under W2-52 (`DAEO-siiz`)**: a verdict that the A5 or A7 gate accepts, written as the adopt skill gives it, is a
   record the store reads; `gov rebuild` reports no invalid record. (Analysis "Draft KPI lines" 2.)
2. **A3, under W2-88 (`DAEO-2bdu`)**: A9's `FABRIC_INCOMPLETE` names each file in neither list (and each in two).
   (Draft KPI line 3.)
3. **W2-81's test code, under W2-81 (`DAEO-l78m`), the test designer's:** T1 the runner's `gov queue` runs with the
   operator's `HOME` (its pytest resolves); T2 stage AS in the stage list (required; MISSED and named if absent); T3 an
   owner-exceptions input to the judge's `overall` (a file of reason ids with the decision id; READY with exceptions only
   when every non-FOUND reason is named; one unnamed stays NOT_READY); T5 `CAPABILITIES` and the README's VERDICT row
   refreshed; T6 the report records, per question, the ranked bundle's `(path, start, end)` list and the forbidden
   source's rank (ids and numbers only, never text); and **T10** every session the run launches (the adopters and what
   they launch) gets `GOV_MSG_ADDRESS` set to the address of whoever started the run (the run's own end messages went
   to the live CTO's inbox: 29 of them on 2026-11-20). Draft KPI line 7, plus T10.
4. **The adopter brief for the re-run** (the analysis's C1 to C7), written into W2-81's record folder as
   `adopter-brief-rerun.md` on your branch: the order A1, the path map committed (every tracked path in exactly one
   namespace), then A2, AS, MA, A3; A3's form as the release takes it; `facts.yaml`'s `where`, `tests_tree`, `accept`;
   `ccusage`'s directory on `PATH`; `gov queue` and `gov doctor` with the operator's `HOME`. Leave C5 (the memory rule
   for stale namespaces) and anything F1 or the not-built stages touch as a marked placeholder: they wait for the owner's
   D3 and D7.

## Not yours (they wait for the owner's D1 to D9)
The verdict stage (D1), the stale-document route (D3), `gov doctor`'s drift policy (D6), F1 (D7), the exceptions list
(D9), the re-run itself (D8).

## Green and return
`gov accept W2-52`, `gov accept W2-88`, `gov accept W2-81`, `tests/unit/adopt`, `tests/unit/store`, `tests/unit/optin`;
return: branch and head; each fix with its tests and the summary lines; reds not yours.
