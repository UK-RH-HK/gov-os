
## 292. Delegated decisions of 2026-10-23 from W2-67's round 1 (register v0.292, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-907 — W2-67's ticket role is engineer, its acceptance files named for its test designers; four of its leads' readings accepted (delegated)
- **Status:** ACCEPTED (delegated, orchestrator, 2026-10-23, under the prompt §7: P2, reversible, the lead's recommendation and mine agree, confidence medium or higher; it changes nothing in the Charter, the master rules or the Contract's scope, and does not weaken the guard; item 2 is stricter only; `Task: decision-record`, `Role: orchestrator`). The owner may overturn any part. · **Under:** DEC-899, DEC-904 item 5, DEC-906, MR-3, DEC-069, DEC-315, DEC-898, DEC-440, DEC-338 · **Basis:** W2-67's round 1 return (`log/W2-67-A5-run1.json`; its packages in the worktree's `.gov-runtime/scratch/lead/packages/`).
  - The round's test design is done and red as its README states.
  - The implementation could not start: `gov launch: LAUNCH_REFUSED: ticket 'DAEO-9nys' is a ticket of another role ('independent-test-designer'), not of 'engineer'`. The guard also gives no engineer `tests/acceptance/**`.
  - The ticket file I wrote set the role to test designer, while its card puts the builder tests on an engineer: my slip, a contradiction between the card and the guard (DEC-105).
- **Decision:**
  1. **P-W2-67-1 (a).**
     - **The ticket's role is `engineer`.** Its `allowed_paths` hold only builder files: `tests/unit/guard/**`, `tests/conftest.py`, and `tests/unit/close/**` (round 2).
     - **Its acceptance files are named in the body for its test designers** (MR-3, as for W2-66, W2-07, W2-57, W2-65 and W2-69): the copying fixtures (`tests/acceptance/W1-07/w1_07_support.py`, W1-25's, W1-27's) and the revised suites.
     - **The copying fixtures are changed by a second, fresh test designer,** with `Rewrite-Reason: the copy races git's background gc (I3 F9, I4 F5)`. It runs batch 1's `test_w2_67_*` files, `w2_67_tmp_probe.py` and `README-W2-67.md`, but never reads them.
     - Test designers still launch on an engineer's ticket.
  2. **P-W2-67-TD1-A (stricter only):** the root `tests/conftest.py` refuses, at the start, a run given a per-run `--basetemp`, naming DEC-898. One opt-out stays, an explicit environment flag (`GOV_ALLOW_BASETEMP=1`), for a measured trial.
  3. **P-W2-67-TD1B-A:** "a rebuild needs only git" admits gitleaks for the secrets filter (DEC-440), as committed.
  4. **P-W2-67-TD1C-A:** the code-graph daemon's per-run folders.
     - The fixtures' clean-up goes to W2-67's round 2.
     - The module's side is a row for W1-16's code-graph owner.
     - `/tmp/gov-cbm-<uid>` is counted in DEC-898's temp-folder measure and swept under DEC-902.
  5. **To the owner's daily digest (low confidence, not delegated):**
     - P-W2-67-TD1B-B: may a pinned version's local label (`+cu130`) differ from the version read? The lead recommends strict equality unless the label is recorded on purpose.
     - P-W2-67-TD2-A: should every change to `readiness-dimensions.yaml` need its own CIT-E record?
- **Where it goes (DEC-851):** this register; W2-67's ticket file and card (its own commit, `Task: DAEO-9nys`); RESUME HERE; the next daily digest (item 5). No brief changes.
- Next free id: DEC-908.

| Version | Date | Change |
|---|---|---|
| 0.292 | 2026-10-23 | Delegated (orchestrator): DEC-907 (W2-67's role engineer, its acceptance files named for its test designers, the copying fixtures by a second fresh designer; the conftest refuses a per-run --basetemp with one opt-out; rebuild admits gitleaks; the code-graph folders' clean-up split; two low-confidence readings to the owner's digest). Next free id: DEC-908. |
