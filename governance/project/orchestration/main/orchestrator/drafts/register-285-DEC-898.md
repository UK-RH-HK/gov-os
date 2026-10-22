
## 285. The owner's standing rule of 2026-10-22 on disk space, inodes and scratch budgets (register v0.285, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-898 — The resource gate checks free disk space and free inodes; every auditor, trial and lead has a scratch budget, cleans up as it goes and reports its scratch size
- **Status:** ACCEPTED (owner, 2026-10-22, in the chat, standing; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`). The rule is the owner's. The figures in items 1 and 2 are the orchestrator's proposal, in force provisionally until the owner confirms or changes them. They are stricter only. · **Under:** DEC-798, DEC-847, DEC-880, DEC-889 item 16, DEC-855, DEC-851, DEC-861 · **Basis:**
  - **Lens I area 4's folder** (`/tmp/gov-os-assessment-I4/`) held about 7.0 million files and folders (61 GB). About 5.3 million files (46 GB) were in `tmp/bt/`: from 18:31 to 19:04 that auditor gave each planted-fault run its own pytest base folder, which skips pytest's clean-up of old folders, and the suites it ran make whole-tree copies per test.
  - **The disk's inodes reached 98 % use.** One run could not write its result (ENOSPC).
  - **Before the orchestrator's clean-up of the four lens I folders** (about 20:15): 62,589,143 of 67,108,864 inodes used (94 %); 640 GB of 1,007 GB used (67 %).
  - **After the clean-up** (20:30): 45,983,305 inodes used (69 %); 486 GB used (51 %). The cited evidence folders were kept.
- **Decision:**
  1. **The resource gate checks free disk space and free inodes.**
     - It refuses a launch, a trial or a close when the shared disk has less than **100 GiB free or fewer than 10,000,000 inodes free**.
     - Until W2-20 builds this into `gov launch` and `gov close`, the orchestrator's `tools/disk_gate.sh` does it, in the same command as each launch and inside `close_queue.sh`, `nightly.sh` and `tooltrials.sh`.
     - W2-20's ticket gains the KPI. Its gate counts every Gov OS session on the machine, as before.
     - `gov close`'s call to the same reading goes to W2-07's or W2-66's card (the review bundle), because their paths hold the close and W2-20's do not.
  2. **Every auditor, trial, research and lead brief gets a scratch budget:** size, and the number of files and folders.
     - **The budgets:**
       - an auditor, trial or research session: **30 GB and 2,000,000** in its own folder;
       - a lead with all its workers: **20 GB and 1,000,000** outside the tracked tree (its worktree's untracked and ignored files, and its own temp folder);
       - the nightly run: **30 GB and 2,000,000**.
     - **How a session keeps to it:**
       - it sets `TMPDIR` to a folder of its own (where the sandbox sets one, it keeps that one);
       - it keeps pytest's own retention of three base folders, never a per-run `--basetemp`;
       - it removes its clones, worktrees and temp trees as it goes, not only at the end;
       - it measures its scratch (`du -s --inodes` and `du -sh` of its folders) before every heavy run and at the end, and reports the figures in its return's `evidence` line.
  3. **A scratch that passes its budget stops that session's heavy work at once.**
     - The session cleans what it can and returns at once: a lead as PACKAGES, an auditor or trial as PARTIAL, with the measure and the cause.
     - **The orchestrator then pings the owner** (P1). Leads and workers never ping (DEC-855); the orchestrator's ping is the owner's notice.
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §3 (the resource gate), §4 (the launch form), §15 (the gate by hand, the closes, the nightly run and the trials), v3.18;
  - RESUME HERE;
  - `governance/project/briefs/LEAD-w2-common.md` (leads and their workers);
  - `governance/project/briefs/AUDITOR-common.md` (W2-25's, W2-28's, W2-30's and W2-47's auditors) and every lens, trial and research brief the orchestrator writes;
  - W2-20's ticket file and card (the KPI; its own commit with `Task: DAEO-r30l`, DEC-896);
  - the orchestrator's `disk_gate.sh`, `close_queue.sh`, `nightly.sh` and `tooltrials.sh`.
- Next free id: DEC-899.

| Version | Date | Change |
|---|---|---|
| 0.285 | 2026-10-22 | Owner (recorded by the orchestrator, DEC-861): DEC-898 (standing: the resource gate checks free disk space and free inodes, refusing a launch, trial or close below 100 GiB or 10,000,000 inodes free; scratch budgets of 30 GB and 2,000,000 for an auditor, trial or research session or the nightly run, 20 GB and 1,000,000 for a lead with its workers; own TMPDIR, pytest's own retention, clean-up as it goes, the scratch size in every return; a budget passed stops the heavy work and the orchestrator pings the owner; the figures provisional until the owner confirms them). Next free id: DEC-899. |
