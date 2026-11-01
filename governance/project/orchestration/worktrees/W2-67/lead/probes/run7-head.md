---
type: probe
task: DAEO-9nys
reviewer_session: 5ac658ff-a07d-4fcd-8247-c5d9710f9ba8
implementer_session: 6edef3cd-38c2-4751-88db-fceef0c5c9bf
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: @@PROBED@@
---

# Probe record: W2-67 (DAEO-9nys), run 7: the disposition case's ids (DEC-970, P-W2-67-R6-DISP (a))

- **What was probed.** Run 6's scoped run found one red this ticket caused: a clean auto-merge (`0568d91baf56`, DEC-954) had given `tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure` W2-64's fixture ids (`DEC-9003`, `DEC-9004`) while this ticket's revised assertion still looked for `DEC-cyc1` and `DEC-cyc2`. The CTO decided a second test-design batch and a short review (DEC-970, P-W2-67-R6-DISP (a)). Before run 7 the orchestrator merged `w2/integrate` (`1a8357702abd`) as `0978a976e85f`, a clean auto-merge (its tree equals git's own merge of its parents).
  - **td-11** (independent test designer, session `6edef3cd-38c2-4751-88db-fceef0c5c9bf`, sandboxed through `gov launch`, effort xhigh), in the tests worktree `W2-67-tests` (DEC-963): commit `0d2fc195f449`, the assertion's two ids made the fixture's (+1 −1), `Rewrite-Reason: DEC-954 merge of W2-64`. Case alone: 1 failed before (on that assertion only), 1 passed after; the whole file 1 failed, 15 passed before, 16 passed after.
  - The lead merged the tests branch as `f7ca56a0fbb5` (`--no-ff`, message file) and committed checkpoint CP-DAEO-9nys-0028 as `aa4a4a9ef53e`, the head probed.
  - **rev-7** (session `5ac658ff-a07d-4fcd-8247-c5d9710f9ba8`; role `independent-auditor`, `gov launch` under its OS sandbox, reading tools only, effort max), commissioned and judged by the ticket lead, reviewed `0978a976e85f..f7ca56a0fbb5` on `aa4a4a9ef53e`, plus the two W1-27 files both sides of the clean merge `0978a976e85f` changed (run 6's lesson). **Pass**: no finding that justifies a round; one observation, O1 ("Ordinary work: yes", "Consequence: other").
- **Which review this is.** The review of DEC-970's new round (DEC-916), the last of this change (DEC-413). The earlier records keep their verdicts (`PR-DAEO-9nys.md`, `PR-DAEO-9nys-run3.md`, `PR-DAEO-9nys-run6.md`).
- **The tripwire.** td-11: only the tests worktree changed (its head and `tests/acceptance/W1-30`); rev-7: nothing changed in this worktree; the main tree changed by the orchestrator's own work only.
- **The lead's verification on `aa4a4a9ef53e`** (this worktree's `src/`; `gov.__file__` = `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`):
@@VERIFY@@
- **Threat model (DEC-801, DEC-808).** Every finding is judged by ADR-0001's two questions; only "yes" with "fails open" or "loses work" fails a probe. **The lead's judgement: pass.** O1 (the ids assertion is also met by core-schema's finding on the fixture's single-value `supersedes`, since W2-64's merge, not this change) is "Ordinary work: yes", "Consequence: other" (W1-11's hazard cases pin the cycle's detection): a residual row, no round.

## rev-7's record

