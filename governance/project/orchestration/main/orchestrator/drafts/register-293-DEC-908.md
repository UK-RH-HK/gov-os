
## 293. Delegated decisions of 2026-10-23 from W2-07's run 2 (register v0.293, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-908 — W2-07's test-designer batch gains the 14 W1-30 cases its KPIs also change; DEC-455, DEC-480 and DEC-454 marked; W1-01's merge case read through DEC-906's list (delegated)
- **Status:** ACCEPTED (delegated, orchestrator, 2026-10-23, under the prompt §7: P2, reversible, the lead's recommendation and mine agree, confidence medium-high; it applies the owner's DEC-904 item 6 and DEC-906 to cases of the same kind; it changes nothing in the Charter, the master rules or the Contract's scope; `Task: decision-record`, `Role: orchestrator`). The owner may overturn it. · **Under:** DEC-904 item 6, DEC-906, DEC-868 items 1 (b) and 3, DEC-866, MR-3 · **Basis:** W2-07's run 2 return (`log/W2-07-A5-run2.json`).
  - The widened batch is done and green, and `gov check` is all green.
  - No gap in the implementation.
  - The W1-30 fixture was RED at 7 hard-block checks, not 3, and now declares the 13 that a project built from scratch can pass.
  - 14 W1-30 cases still hold rules the KPIs changed: 13 of run 1's 175, which the fixture alone did not clear, and 1 newly exposed.
- **Decision:**
  1. **P-W2-07-T2 (a): the batch is widened to the 14,** each with a `Rewrite-Reason:` naming its decision, and no other expectation lowered:
     - **8 in `test_w1_30_context_failures.py`,** to DEC-868 item 3: a broken context turns context-reproducibility RED, so the pre-close `gov check` refuses at once, naming it, uncounted.
     - **5 to DEC-868 item 1 (b) and KPI 5** (the check runs on every close, and the record states it):
       - `test_w1_30_governance_checks.py` ×2;
       - `test_w1_30_r8_commits.py` ×2;
       - `test_w1_30_r13_installed_skills.py` (refused naming core-authority).
     - **1 to KPI 10 (W2-M252):** `test_w1_30_iteration.py::test_each_refusal_opens_repair_ticket`, since an identical refusal reuses and names its ticket.
  2. **Marked under DEC-866:**
     - DEC-455's "counted iteration" for a context failure, changed by DEC-868 item 3;
     - DEC-480's "the checks only when governance files change", changed by DEC-868 item 1 (b) and W2-07's KPI 5;
     - DEC-454's "each refusal opens a repair ticket", changed by W2-07's KPI 10 (W2-M252).
  3. **P-W2-07-T3 is already decided by DEC-906.**
     - W1-01's history cases are a known red until W2-70 merges. They are reported by name, and do not stop W2-07's DONE.
     - The integration-merge case (`test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass`) reads the same exact-commit list, through `merge_offences` in `w1_01_support.py`.
     - W2-70's ticket gains that case. No `accepted_reds` entry: the owner chose the list (DEC-906).
  4. **A row, W2-L416:** in the W1-30 fixture, repeated closes pass without a fresh checkpoint after the close's own repair-ticket commit. W2-07's checkpoint gate takes it if the fix is small; otherwise it is a row for W2-24.
- **Where it goes (DEC-851):**
  - this register, with DEC-455's, DEC-480's and DEC-454's status lines marked;
  - W2-07's ticket file and W2-70's ticket file (each in its own commit);
  - the Wave 2 list (row W2-L416);
  - RESUME HERE.
- Next free id: DEC-909.

| Version | Date | Change |
|---|---|---|
| 0.293 | 2026-10-23 | Delegated (orchestrator): DEC-908 (W2-07's test-designer batch gains 14 W1-30 cases its KPIs also change; DEC-455, DEC-480 and DEC-454 marked; W1-01's merge case read through DEC-906's list in W2-70; row W2-L416). Next free id: DEC-909. |
