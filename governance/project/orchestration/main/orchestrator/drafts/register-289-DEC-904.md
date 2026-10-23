
## 289. The owner's answers of 2026-10-23 on P-W2-07-A-B (register v0.289, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-904 — A full verification run against the scratch budget: the retention trial, a lead's own clean-up rule, a bridge cap with one run at a time; W2-67 forward; W2-07's test-designer batch widened to the 196 cases
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** DEC-898, DEC-902, DEC-880 item 2 (b), DEC-889 items 6 and 7, DEC-868, DEC-896, DEC-899, DEC-903, DEC-866, MR-3 · **Basis:** package P-W2-07-A-B with its addendum (`governance/project/orchestration/packages/P-W2-07-A-B.md`). W2-07's and W2-66's leads stopped their full verification runs at DEC-898's lead budget: 1,062,156 inodes at about 13.6 % of W2-07's run; 5,306,782 inodes and 47 GB for W2-66's.
- **Decision:**
  1. **A (a), the retention trial.** pytest's `tmp_path_retention_policy=failed` is tried on one full run in the close's form, measured:
     - the peak inodes and size of the run's temp folder;
     - the wall time, against a run without it;
     - that the results are unchanged;
     - that a failing test's folder is still kept.
     If it holds, it becomes the default for the close (W2-66's close command), the nightly run and the leads' verification.
  2. **A (c), a lead's own clean-up.** An allow rule lets a lead remove only its own temp folder, by its literal path (`/tmp/gov-os-lead-<its W2 id>`). It is carried in the settings regeneration after the first re-pin. Until then, the orchestrator removes a returned lead's temp folder.
  3. **A (b), the bridge until (a)'s trial reports:**
     - 6,000,000 files and folders and 60 GB per verification run;
     - **one verification run at a time** across every session (each full run takes the lock `/tmp/gov-os-verify.lock` with `flock`, and waits while another holds it);
     - the disk floor (100 GiB and 10,000,000 inodes free) still enforced across all sessions.
     DEC-898 is marked changed accordingly.
  4. **The two stopped runs' temp folders** (`/tmp/gov-os-lead-W2-07/`, `/tmp/gov-os-lead-W2-66/`) are removed now, after a re-check just before removal that no process holds anything in them.
  5. **W2-67 (test hygiene) comes forward to the next free slot.** It removes the tree-copying tests that cause these inode explosions and much of the close time. Its acceptance revisions still close after W2-07 is pinned (DEC-896 item 3).
     - **The orchestrator's application of the overlap rule (the prompt §3):** W2-67 starts with the folders no ticket in flight holds. Its W1-30 and `tests/unit/close` work waits for W2-07's and W2-66's merges, and its W2-50 scale and hang cases wait for W2-69's.
  6. **B (a), W2-07's test-designer batch widened to the 196 cases.** Each revision carries a `Rewrite-Reason:` naming its decision, and no expectation is lowered.
     - W1-30's shared fixture (`tests/acceptance/W1-30/w1_30_support.py`, `tests/acceptance/W1-30/conftest.py`), so its fixture projects are green under the in-close `gov check` (DEC-868 item 1 (b)). This clears 175 cases.
     - The 20 gate-order cases, to DEC-868 item 3's order:
       - `test_w1_30_r9_every_finding.py` (8);
       - `test_w1_30_r13_refused_runs.py` (3);
       - `test_w1_30_check_blocks.py::test_a_refusal_where_gov_check_blocks_is_counted`;
       - `test_w1_30_governance_checks.py::test_a_refusal_for_a_red_check_is_counted`;
       - `test_w1_30_close.py::test_regression_runs_to_end_all_failures_collected`;
       - `test_w1_30_containment_places.py` (2);
       - `test_w1_30_iteration.py::test_mixed_causes_reach_escalation`;
       - `test_w1_30_repair_ticket.py` (2);
       - `tests/acceptance/W2-53/test_w2_53_load_sensitive.py::test_an_entry_the_owner_did_not_add_is_refused_naming_it_and_its_test_is_not_run_again`.
     - The repair-ticket case to KPI 8: `test_w1_30_r8_tree.py::test_a_second_close_with_the_refusals_repair_ticket_left_untracked_is_measured`.
     - **The superseded expectations, marked under DEC-866:**
       - DEC-492 (marked `17e5c3a9`);
       - DEC-490's part that an untracked repair ticket of the ticket being closed does not refuse: changed by W2-07's KPI 8, the close commits its repair ticket;
       - DEC-493's overlay holding exactly the path map: changed by DEC-896 item 2 and DEC-903.
  7. **P-W2-07-C and DEC-903:** accepted by the owner, as delegated.
  8. **The order:** resume W2-07's verification first (it merges before W2-66), then W2-66's, one verification run at a time under the bridge cap.
- **Changes:**
  - DEC-898 (the bridge cap per verification run; one at a time; the lock);
  - DEC-889 item 7 (W2-67's place);
  - DEC-490 (the untracked repair ticket);
  - DEC-493 (the overlay);
  - DEC-880 item 2 (b) (the leads' verification, now under the lock and the cap).
- **Where it goes (DEC-851):**
  - this register, with DEC-898's, DEC-889's, DEC-490's and DEC-493's status lines marked;
  - the prompt §3 (W2-67's place) and §15 (the cap, the lock, the trial), v3.21;
  - `LEAD-w2-common.md` (the cap and the lock for a verification run; the orchestrator removes a returned lead's temp folder until the allow rule);
  - RESUME HERE;
  - W2-07's ticket file (its own commit, `Task: DAEO-r9ss`);
  - W2-67's card and its ticket file (its own commit);
  - the re-pin plan's settings regeneration (the allow rule);
  - the orchestrator's `nightly.sh` and the trial (under the lock).
- Next free id: DEC-905.

| Version | Date | Change |
|---|---|---|
| 0.289 | 2026-10-23 | Owner (recorded by the orchestrator, DEC-861): DEC-904 (P-W2-07-A-B with its addendum: the retention trial, measured, then the default for the close, the nightly and the leads; a lead's own temp clean-up by literal path at the settings regeneration; the bridge cap of 6,000,000 inodes and 60 GB per verification run, one at a time under a lock, the disk floor still enforced; the two stopped runs' temp folders removed; W2-67 forward to the next free slot; W2-07's test-designer batch widened to the 196 cases; DEC-490 and DEC-493 marked; P-W2-07-C and DEC-903 accepted; W2-07's verification first, then W2-66's). Next free id: DEC-905. |
