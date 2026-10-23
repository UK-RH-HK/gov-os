
## 287. The owner's acts and standing rule of 2026-10-23 on the disk (register v0.287, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-902 — The weekly sweep, a standing rule; the cleanup of 2026-10-23; the owner's commits A and B; pytest-timeout installed
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat, standing for item 1; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** DEC-898, DEC-899 items 3 and 10, DEC-900, DEC-892 b, DEC-889 item 13, DEC-861, DEC-851 · **Basis:** the cleanup proposal (`governance/project/orchestration/packages/CLEANUP-PROPOSAL-2026-10-23.md`, filed with this record) and the disk inventory behind it.
- **Decision:**
  1. **The sweep (owner, standing).**
     - **What:** the orchestrator sweeps throwaway areas under `/tmp` and run folders, weekly (on Monday) and when the disk gate (DEC-898) nears its floor.
     - **What it may remove:**
       - pytest's `garbage-*` folders and its numbered run folders other than the newest three;
       - Claude Code's session temp folders under `/tmp/claude-1000` of sessions not running;
       - the launcher's `/tmp/gov-launch-*` folders;
       - the code-graph daemon's run folders under `/tmp/gov-cbm-1000`;
       - `/tmp/gov-check-*` and `/tmp/gov-testcache-*`;
       - the worktrees and branches of closed tickets, after a sync.
     - **Its conditions:**
       - only in a quiet moment: no lead, close, nightly run or trial running;
       - nothing modified in the last 24 hours;
       - nothing a running process holds open (`lsof`);
       - nothing cited as evidence;
       - never the live session's own folder, and never the live code-graph daemon's folder.
     - **What it never touches:** `~/.cache`, a ticket in progress's `~/gov-os-runs/` folder, the record worktree, the owner's EXAMIN copy and the workbench.
     - **How it runs:** by `.gov-runtime/scratch/orchestrator/tools/sweep.py`. It lists what it removed and what it skipped, and why.
     - **The figures before and after** go in the daily digest.
  2. **The cleanup of 2026-10-23 (owner's acts).**
     - **Removed by the owner:** lists 1, 2, 4 and 6 of the proposal, 289 folders, none skipped.
       - Claude Code's finished sessions' temp, pytest's two garbage folders, the launcher's two engineer temps, W2-48's cache folders and the empty check folders.
       - Before: 332 GB used (35 %), 30,267,328 inodes used (46 %).
       - After: 74 GB used (8 %), 882 GB available; 1,826,466 inodes used (3 %), 65,282,398 free.
     - **Lists 3 and 5 (pytest's old run folders, 58; the code-graph run folders, 10,575)** are approved only under item 1's conditions, because leads are running and the daemon shares that folder. The orchestrator runs them in the first quiet moment and lists what it skipped and why.
  3. **The owner's commits:**
     - `596870bd`: W1-02's and W1-05's p95 `load_sensitive` entries removed (DEC-899 item 3);
     - `c9a08678`: W1-42's RETR-X-02 case and governance-share case retired with both `accepted_reds` entries (DEC-900).
     Both are `Role: owner`, both were validated with the pinned ratchet first (DEC-895), and `accepted_reds` is empty. The owner pushed `w2/integrate` at `c9a08678` and `record/w2` at `d8e5e53d`.
  4. **pytest-timeout 2.4.0** is installed by the owner in the user site of `/usr/bin/python3`, its wheel's hash checked (sha256 `c42667e5cdadb151aeb5b26d114aff6bdf5a907f176a007a30b940d3d865b5c2`). It is recorded in the tool registry, approved by DEC-892. The first re-pin's environment gets the same wheel.
  5. **Two rows:**
     - **W2-M405:** the launcher left two engineer sandboxes' temp folders behind on 2026-10-20, 4.1 million inodes and 36 GiB. W2-C002's fix at W1-28 no longer holds. Fixed by W2-21: the launcher removes a sandboxed worker's temp folder when the worker ends.
     - **W2-L415:** two W1-38 rulesync cases (`TestGenerateCheck::test_check_clean_after_generate` and `TestRegisteredFamilyCheck::test_gov_check_lists_the_check_under_the_family`) errored under load in W2-50's run 9 (`rulesync generate` timed out at 30 s) and passed alone. They are not on `load_sensitive`. Fixed by W2-57's first item (the probe's limits).
- **Changes:** DEC-899 item 10 (the proposal decided); DEC-898 (the sweep joins its scratch rules).
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §15 (the sweep, beside the disk gate; the daily digest's figures), v3.20;
  - RESUME HERE;
  - the tool registry;
  - the Wave 2 list (rows W2-M405, W2-L415);
  - W2-21's card (the launcher's temp clean-up, row W2-M405).
  It does not reach the lead or auditor briefs: the sweep is the orchestrator's, and DEC-898 already tells sessions to clean up after themselves.
- Next free id: DEC-903.

| Version | Date | Change |
|---|---|---|
| 0.287 | 2026-10-23 | Owner (recorded by the orchestrator, DEC-861): DEC-902 (standing: a weekly sweep of throwaway areas under /tmp and run folders, only in a quiet moment, nothing newer than 24 hours, nothing held open, nothing cited as evidence, never the live session's or daemon's folder, figures in the daily digest; the cleanup of 2026-10-23: lists 1, 2, 4 and 6 removed by the owner, 74 GB and 1.8 M inodes used after; lists 3 and 5 under the sweep's conditions; the owner's commits 596870bd and c9a08678; pytest-timeout 2.4.0 installed; rows W2-M405 and W2-L415). Next free id: DEC-903. |
