# ACT-OPERATOR-ROUNDS-1: a failed KPI line blocks READY; reviews counted per ACT id (DEC-1131 (3))

Read `LIFT-common.md` first (scratch only; never edit the live operator files or `~/gov-os-operator/`). Role:
ACT-preparation helper, Sonnet high, class C2 (DEC-1120). Scratch folder:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-operator-rounds/`; temporary
folder its `tmp/`; any clone there too, removed when done. Save your package early and extend it.

## The two gaps (DEC1010-REVIEW §2.4 (1), §4.2; read DEC-1131 in the register)
1. `governance/project/operator/verdict.py` lines ~11-12: a review verdict is READY when no finding blocks, even if a KPI
   line is marked `fail`. Fix: READY also needs no KPI line marked fail (the ACT reviewer brief already says so:
   `governance/project/operator/reviewer-brief.md`). Find every caller (`operator_run.py`'s G4, the CTO's copy
   `.gov-runtime/scratch/orchestrator/tools/verdict.py`, any test) and say what each now does.
2. `governance/project/operator/operator_run.py`: the two-round cap counts reviews per manifest sha, so each rebuild of an
   ACT resets it (ACT-W2-149-INSTALL-1 had five reviews on four builds). Fix: count per ACT id (the manifest's `act`
   field) across manifests, from the operator's log (`~/gov-os-operator/log/operator.jsonl` is read-only evidence; the
   code reads what it reads today) or from the review files: find where the count is made and change only that.

## The route
`class-rules.yaml`'s `operator-own` row: class (O), control: the owner's, applied by hand like ACT-OPERATOR-1. Model the
package on the last operator change (search `packages/` for ACT-OPERATOR-*). The installed copies under
`~/gov-os-operator/install/` are hashed in its APPROVED list: say what the owner's steps change there (the repository
files, the installed copies, the APPROVED hashes) and in what order, so the running operator never sees half a change.

## Build
`ACT-OPERATOR-ROUNDS-1.md`: what, why, the two diffs (exact), the class, the owner's commands, the rollback, and a
rehearsal on a copy in your folder: the operator's own unit tests (find them: `governance/project/operator/test_*.py`)
pass; new cases: a verdict with no blocking finding but one KPI `fail` is refused; a second build of the same ACT id
after two reviews is refused at G4 (or wherever the cap is) with the reason; a different ACT id is unaffected. Record
the rehearsal log ending `failures: <n>`. The CTO's copy of `verdict.py` gets the same change (list it; the CTO applies
it).

Return the twelve fields, short; the files; the rehearsal count. Estimate 1 to 1.5 h.
