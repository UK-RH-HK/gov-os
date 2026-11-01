---
type: probe
task: DAEO-9nys
reviewer_session: 75a5fb44-6607-4386-ab23-4b87f0fa174b
implementer_session: 8a693c0b-3078-481b-ad80-99104401fbb7
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 90d41204d412b09f348c422fce9cdce95870bd4e
---

# Probe record: W2-67 (DAEO-9nys), run 6: the merge of w2/integrate (DEC-954) and its one repair batch

- **What was probed.** Run 6 merged `w2/integrate` (`c07a1115577f`) into `w2/W2-67` (merge `0568d91baf56`, 2026-10-31). The merge had to resolve one conflict, in `tests/acceptance/W1-30/test_w1_30_close.py` (the KPI S1 case `test_task_trailer_exact_match_not_substring`: W2-64's schema-valid ids against this ticket's PF15 revision). A fresh independent test designer resolved it (td-9, session `4e4a6cce-c3a2-492e-b120-e905a6f27271`). Under DEC-953 (its lifted DEC-895: a new review only where a merge resolved conflicts in files a review judged), two reviews ran on that change only, each a fresh read-only reviewer (role `independent-auditor`, through `gov launch` under its OS sandbox, reading tools only, effort max), commissioned and judged by the ticket lead:
  - **rev-5** (session `29477cee-8ee8-442a-9ee4-e3872ad1fcad`), on head `3a2f2a1f0497` (the merge plus checkpoint CP-DAEO-9nys-0022): the resolution. **Pass**, with F1 (medium; with W2-64's ids the close's fixed-string search hides AB's commit, so the case no longer turned red under PF15, seen under the plant) and F2 (low; the README-W2-67 row stale). Both "Ordinary work: yes", "Consequence: other".
  - **The one repair batch** (DEC-136: the finding given as behaviour): a fresh independent test designer (td-10, session `8a693c0b-3078-481b-ad80-99104401fbb7`), commit `a8c0920abead` (`Rewrite-Reason: DEC-954 merge of W2-64: the merged ids hid PF15 behind the close's search, so the case no longer caught its plant`): a near-miss commit `Task: PROJ-tkaab` (A's id plus one character, naming no ticket) in the same case, and the README-W2-67 row and a run-6 section.
  - **rev-6** (session `75a5fb44-6607-4386-ab23-4b87f0fa174b`), on head `90d41204d412` (the repair plus checkpoint CP-DAEO-9nys-0025): the repair's change, `3a2f2a1f0497..a8c0920abead`. **Pass**: F1 and F2 fixed (under PF15 1 failed for PF15's own reason, marker "matched by substring: 1, of them exactly: 0"; without it 1 passed); nothing lowered; scope as stated. Two low findings on README-W2-67's wording (G1, G2), both "Ordinary work: yes", "Consequence: other".
- **Which review this is.** These are reviews of the run-6 merge resolution and its repair, not new rounds (DEC-916); rev-6 is the second and last review of this change (DEC-413). The three declared rounds keep their passed records (`PR-DAEO-9nys.md`, `PR-DAEO-9nys-run3.md`).
- **The tripwire.** Before and after each reviewer: no change in this worktree or the main tree (other worktrees moved by their own leads and the store refresh only).
- **The lead's verification on `90d41204d412`** (this worktree's `src/`; `gov.__file__` = `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`):
  - rebuild (under the rebuild lock, never `--no-embeddings`): exit 0, `store.invalid: []`;
  - the selection (`select_tests.py`): scope `scoped`, `core_changed` [], `unplaced` [], 36 targets; no "serial"-route entry reached, so no serial phase;
  - the scoped run in the close's form (`-n auto`, `-p gov_close_serial_only`, `--timeout=900 --timeout_method=signal`, `-o tmp_path_retention_policy=failed`, the selection's `--ignore`/`--deselect`): **1 failed, 4965 passed, 1 skipped in 1570.68 s**. The red: `tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure`, red alone too. Cause: the merge's clean auto-merge of that file kept W2-64's fixture ids (`DEC-9003`, `DEC-9004`) beside this ticket's revised assertion on the old ids (`DEC-cyc1`, `DEC-cyc2`); git reported no conflict there, and neither review judged that file. It is this ticket's to fix (a two-line test-design change); the one repair batch being spent, it is returned to the orchestrator as a package (P-W2-67-R6-DISP);
  - KPI 4's count: four base folders right after the run (pytest's three retained nested-session folders and the outer run's own, kept for the one red's `tmp_path`); the next pytest session pruned them to three;
  - TD1C-A's case, run by the lead outside the sandbox: 5 passed in 48.29 s; daemon folders under `/tmp/gov-cbm-<uid>` 17,691 before and after;
  - collect-only over `tests`: "17475/17477 tests collected (2 deselected)", exit 0; `gov check`: core-mutation RED for W2-76's ticket file (the same on `w2/integrate`), two YELLOW, the rest GREEN.
- **Threat model (DEC-801, DEC-808).** Every finding is judged by ADR-0001's two questions; only "yes" with "fails open" or "loses work" fails a probe. **The lead's judgement: pass.** F1 and F2 (rev-5) are fixed by the repair; G1 and G2 (rev-6) are "Ordinary work: yes", "Consequence: other": residual rows on README-W2-67's wording. The verification red is not a review finding: it is the package above.

## rev-5's record

