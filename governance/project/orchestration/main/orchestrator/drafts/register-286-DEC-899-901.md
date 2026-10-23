
## 286. The owner's answers of 2026-10-23 at the review point (register v0.286, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-899 — The review point: W2-66, W2-07, W2-68, W2-67, W2-57 and W2-70 confirmed; lens I's P-IS-1 to P-IS-7 (a); W2-07 merges before W2-66; the p95 entries removed; two re-pins; DEC-898's figures confirmed; the interim skip guard
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** DEC-880, DEC-883, DEC-884, DEC-889 items 7 and 14 to 16, DEC-890, DEC-892, DEC-895, DEC-896, DEC-897, DEC-898, DEC-813, DEC-757, DEC-762, DEC-766, DEC-866, DEC-861 · **Basis:**
  - the review bundle, filed as `governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md` (its combined file, `ALL-DRAFTS-AND-PACKAGES.md`, as the owner read it);
  - lens I's synthesis (`docs/assessment/2026-10/I-SYNTHESIS.md`) and its four area reports.
- **Decision:**
  1. **The drafts are confirmed as drafted,** with P-IS-1 to P-IS-7, each (a):
     - W2-66's ticket file and card (selection and evidence; the test map);
     - W2-07's ticket file and card;
     - W2-68's, W2-67's and W2-57's ticket files and cards;
     - the new LITE ticket W2-70, which retires W1-05's switch-over case and W1-47's builder rerun.
     P-IS-5 includes P-I1-2: the stale `docs/source` read-deny rules are dropped at the settings regeneration after the first re-pin. W2-68's and W2-67's ticket files are created when W2-66 merges; W2-57's and W2-70's now.
  2. **The order of work.** W2-66 and W2-07 both edit `src/gov/close/command.py`, which risks the W2-50/W2-58 pattern: a merge invalidating the other's review.
     - **Built in parallel,** an owner exception to the rule that no two tickets with overlapping allowed paths are in flight (the prompt §3), for these two only.
     - **W2-07 merges first.**
     - **Then W2-66** merges `w2/integrate` back, re-verifies, and gets a fresh FULL probe on the merged head before the re-pin.
     This is written into both cards and the re-pin plan.
  3. **The p95 entries are removed.** W1-02's (`test_decision_p95_is_under_100_ms`) and W1-05's (`test_a_call_waits_under_100_ms_p95_for_the_hook`) p95 `load_sensitive` entries leave the list.
     - **Why:** they already run alone, in a checked quiet window. A second try under the same conditions only risks masking an intermittent slowdown (I2 F14).
     - **W2-M332** keeps its date before W2-24.
     - **If they start refusing closes,** the orchestrator brings the owner a package.
     - **The removal** is the owner's own `Role: owner` commit, prepared by the orchestrator and validated with the pinned ratchet first (DEC-862 (a), DEC-895).
  4. **The re-pin plan:** two re-pins, as drafted, with item 2's merge order.
     - The first carries W2-58, W2-59, W2-65, W2-66, W2-07 and W2-69. W2-59 and W2-65 merge together just before it.
     - The second carries W2-68.
     - The old pin folder stays for a one-command rollback.
  5. **DEC-898's figures are confirmed:**
     - 100 GiB and 10,000,000 inodes free as the floor;
     - 30 GB and 2,000,000 files and folders per auditor, trial or research session, or nightly run;
     - 20 GB and 1,000,000 per lead with its workers.
  6. **Lens I's area 4 is not resumed.** The nightly full run supplies the missing runs. A red or flaky result in area 4's suites comes to the owner as an addendum.
  7. **The live gaps:**
     - **The interim guard is approved now:** until W2-57 lands, the close queue stops a close whose skip count is not the expected 31, so a silent rulesync skip stops the queue (P-IS-6).
     - **The silently empty context packet** rides in W2-04, as its entry criterion (P-IS-12).
     - **The path-map checks** are an entry criterion of W2-27, as lens I says (P-IS-9).
  8. **Later packages:**
     - P-IS-13 comes back when W2-32 starts; the owner leans to (a), raising the line to 85 once a measured run reaches it.
     - P-IS-9 to P-IS-12, P-IS-14 and P-IS-15 come before the ticket each gates.
     - P-IS-8 is decided in DEC-900; P-IS-16 is delegated (DEC-901).
  9. **Then:**
     - **Starts:** W2-66 and W2-07 in the first slots, W2-69 next; W2-70 is created.
     - **Lens H's three raw files** (`rest.log`, `analysis_a6.json`, `analysis_b2.json`), whose `/tmp` originals will not survive a reboot, are archived into the orchestration record on `record/w2` with their sha256. Every other file in the owner's share must have a committed or synced original, or is archived the same way.
     - **Then the share** (`.gov-runtime/scratch/owner-share/`, the folder, the zip and its `.gitignore`) is deleted.
  10. **A read-only disk inventory, then a cleanup proposal** (delete nothing yet):
      - the ten folders holding the most files and the most space, under `/tmp`, `~/gov-os-runs`, `~/gov-os-worktrees` and `~/.cache`;
      - which are leftovers and which are in use;
      - a proposal of exact literal paths for the owner's approval;
      - a standing-rule proposal: what cleans itself up after each run, and what a weekly sweep removes.
- **Changes:**
  - DEC-884 and DEC-889 item 15 (the re-pins as above, with the merge order);
  - DEC-889 item 7 and DEC-890 (W2-66, W2-67 and W2-68 as drafted);
  - DEC-892 a (worksteal's condition met through W2-70 and W2-67);
  - DEC-898 (the figures confirmed, no longer provisional);
  - DEC-813's W2-57 KPI on W1-46's live cases, replaced by DEC-889 item 5's move to the nightly;
  - the prompt §3's overlap rule, for W2-66 and W2-07 only.
- **Where it goes (DEC-851):**
  - this register, with the changed entries marked;
  - the prompt §3 (the order, the merge order, the re-pins) and §15 (the interim skip guard; DEC-898's figures confirmed), v3.19;
  - RESUME HERE;
  - the WBS cards and ticket files of W2-66, W2-07, W2-68, W2-67, W2-57 and W2-70, and P-IS-5's corrections to W2-65's and W2-69's ticket files, each ticket file in its own commit with its Task (DEC-896);
  - the orchestrator's `close_queue.sh` (the skip guard).
  It does not reach the lead or auditor briefs: no lead rule changes.
- Next free id: DEC-900.

### DEC-900 — The AR-9 ruling: RETR-X-02's accepted outcome is the stated gap; W1-42's two accepted reds retired with their entries (P-IS-8 (b))
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** DEC-718 item 11, DEC-713, DEC-714, DEC-757, DEC-762, DEC-766, DEC-862 (a), DEC-895, DEC-889 item 16 d · **Basis:** lens I's P-IS-8 (`docs/assessment/2026-10/I-SYNTHESIS.md`; I2 F1, I3 F1 and R1).
  - Both W1-42 cases read only the frozen Wave 1 exit record.
  - W2-13's and W2-14's paths cannot reach them.
  - The kept bundle fails both possible rulings.
  - W1-21 already asserts the "stated gap" outcome on the same scenario.
- **Decision:**
  1. **The AR-9 ruling (adoption-readiness item Q-1):** for the cross-section query RETR-X-02, the accepted outcome is **the stated gap**: retrieval states that no named parent expansion exists, as `tests/acceptance/W1-21/` already asserts. This closes DEC-718 item 11's first exception by the owner's ruling.
  2. **Retired, in one `Role: owner` commit:**
     - the case `tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]` (its parameter dropped; RETR-A-04 stays);
     - the function `tests/acceptance/W1-42/test_w1_42_exit_report.py::test_governance_share_is_measured_and_at_most_15_percent_on_each_programme`;
     - both `accepted_reds` entries (`fixed_by: W2-13`, `fixed_by: W2-14`).
     The orchestrator prepares the commit and validates it with the pinned ratchet first (DEC-895). **The `accepted_reds` list is then empty.**
  3. **The requirements live on:**
     - the parent expansion in W2-13's own acceptance tests;
     - the measured governance share per programme in W2-14's evidence (DEC-713).
     The Wave 1 record stays as history.
- **Changes:** DEC-757's two `accepted_reds` entries (removed); DEC-718 item 11 (the first exception closed by this ruling; the second, the share, by W2-14's evidence); W2-13's and W2-14's cards (no W1-42 case gates their closes).
- **Where it goes (DEC-851):** this register; RESUME HERE; the prepared owner commit; W2-13's and W2-14's cards' notes. No brief changes.
- Next free id: DEC-901.

### DEC-901 — DEC-281's context threshold of 0.30 kept, with a recorded reason (P-IS-16 (a); delegated)
- **Status:** ACCEPTED (delegated, orchestrator, 2026-10-23, under the owner's delegation of P-IS-16 in the chat; `Task: decision-record`, `Role: orchestrator`) · **Under:** DEC-281, DEC-838, DEC-866 · **Basis:** lens I's P-IS-16 (I3 F14, O4).
- **Decision:** `gov checkpoint --watch` keeps its default `--max-context` of 0.30.
  - **The reason, recorded:** a reminder at 30 % of the window is a handover aid, not an early stop. DEC-838 forbids a compaction threshold and any request to stop early, and the watch neither compacts nor stops; it reports.
  - DEC-281's status line is marked "Changed by DEC-901": its basis DEC-208 and DEC-237 is replaced by this reason.
  - The builder test that pins the default stays.
- **The owner may overturn it.**
- Next free id: DEC-902.

| Version | Date | Change |
|---|---|---|
| 0.286 | 2026-10-23 | Owner (recorded by the orchestrator, DEC-861): DEC-899 (the review point: the drafts of W2-66, W2-07, W2-68, W2-67, W2-57 and W2-70 confirmed with P-IS-1 to P-IS-7 (a), P-I1-2 at the settings regeneration; W2-66 and W2-07 built in parallel, W2-07 merging first, W2-66 merging back with a fresh probe; W1-02's and W1-05's p95 load_sensitive entries removed by the owner's commit; two re-pins; DEC-898's figures confirmed; area 4 not resumed; the interim skip guard; P-IS-13 and the other packages later; the share archived and deleted; a disk inventory). DEC-900 (the AR-9 ruling: RETR-X-02's accepted outcome is the stated gap; W1-42's two accepted reds retired with their entries in one owner commit; accepted_reds empty). Delegated: DEC-901 (DEC-281's 0.30 kept with a recorded reason). Next free id: DEC-902. |
