# W2-27 part (b): the CIT-P note moving CAP-45.a to Wave 3 (DEC-1089 (2)(b), DEC-1090 (5)), product-spec, 2026-11-07

Read `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` first: its rules hold.

- **Role:** product-spec. **Worktree:** `/home/usain/gov-os-worktrees/W2-27-citp`, branch `w2/W2-27-citp`. Write only
  `docs/changes/W2-27-CIT-P.md` there. Commit it on your branch with `Task: DAEO-h4rh`, `Role: product-spec`,
  `Implements: DEC-1089, DEC-1090`. The CTO merges. **Do not edit the Contract** (`docs/contract/**`): the edit follows
  only after the owner approves this note.
- **What the owner decided:** K7 is done for Wave 2; W2-17 (`gov update`, the ticket that delivers CAP-45.a) stays in
  Wave 3; exit criterion 7 (`docs/plan/WAVE_2_WBS.md` §5 item 7) is met by a CIT-P note moving CAP-45.a to Wave 3 —
  option A of `governance/project/orchestration/packages/K7-W2-REMAINDER.md` §3.
- **The note** follows the CIT-P form used here (models: `docs/changes/W2-49-CIT-P.md`, which kept CAP-45.a in Wave 2
  with a Wave 2 clause, §7 D (ii); and `docs/changes/W2-88-CIT-P.md`, a recent single-item note). It states:
  - the change: CAP-45.a's wave from W2 to W3, and the Wave 2 clause W2-49 added (§7 D (ii)) withdrawn or moved;
  - the evidence: DEC-953 and DEC-954 (W2-17 and W2-18 to Wave 3), DEC-941 item 3, DEC-1089 (2), DEC-1090 (5); the
    current text of CAP-45.a in `contract.yaml` and `docs/contract/capabilities/CAP-45.a.md` (quote them);
  - **the impact set,** found by search and by reading: every place that names CAP-45.a or its Wave 2 status (the
    Contract files, the WBS card and exit criterion 7, W2-17's ticket `DAEO-sdhj` (open), the WBS's covers list, the
    plan validator's checks, any acceptance test that cites CAP-45.a, the traceability or covers records, the
    readiness table); for each, what changes when the note is applied and who changes it (a closed ticket is never
    edited, DEC-1088 (6));
  - the exact Contract edit to apply after approval (the lines, as a patch in the note, not applied), the change-log
    row, and the Contract version it makes;
  - DEC-105's three options with their cost (apply now, defer, re-baseline) and the recommendation (apply now, as the
    owner chose option A);
  - how the exit audit (W2-47) will check it.
- **Budget:** about 2 hours; searches by `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store` (its line
  numbers are integrate's; your worktree is at integrate's head `95eec049`). No test runs beyond the placeholder scan
  (`python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/placeholder_scan.py <file>`).
- **Return:** the twelve fields; the impact set as a table in `work_completed`.
