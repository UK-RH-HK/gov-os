# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-22 22:21 BST — W2-50 CLOSED 01488b72; lens I in docs; review bundle ACT-pinged, WAITING; next free DEC-899)

### Standing owner rules (short; full text in the register and prompt v3.18; DEC-851)
- **Window (DEC-838):** full window, no compaction threshold. **Checkpoint at every handover (DEC-837);** keep this
  section < 10,000 chars (older text: CHECKPOINT-ARCHIVE.md). **Memory used (DEC-836):** `gov retrieve` in every brief.
- **Parallelism (DEC-847/880):** gate in the launch command (load1 < 20, MemAvailable >= 6710886 kB); never in a
  close's quiet window; ceiling 10; fewer until W2-66.
- **Disk and scratch (DEC-898, `17515bba`):** `bash tools/disk_gate.sh &&` in every launch command (>= 100 GiB and
  >= 10,000,000 inodes free; figures provisional until the owner confirms); queue/nightly/trials call it. Every
  auditor/trial/research brief: 30 GB + 2,000,000 files budget; lead + workers 20 GB + 1,000,000; own TMPDIR,
  pytest's own retention (never per-run --basetemp), clean up as they go, scratch size in the return's evidence;
  over budget -> stop heavy work, return PACKAGES/PARTIAL, I ping P1. W2-20 KPI `efa2e4b0`.
- **Notify (DEC-855):** six-part package in my message + `packages/<id>.md`; start all independent work; LAST ACTION
  `~/.local/bin/owner-ping "<P1|P2|COMMIT|ACT> <id> | gates <...> | <need>"`; never AskUserQuestion; no secret,
  key, held-out path or file content. During a queue: ping only if a close is refused (new or seen cause).
- **Reports:** countdown first, progress line first (DEC-878: closed / merged-not-closed / built-held / in flight /
  not started of 58; keystones done / in progress / ahead of 9); owner acts collected at the top in order (DEC-888);
  last line OWNER_ACTION.
- **Commits (DEC-861, DEC-896):** decision records `Task: decision-record`, `Role: orchestrator`, `Decided-by: owner
  (chat, <date>)`; a commit that changes a ticket file carries THAT ticket's Task (+ Implements); never Role:
  owner; never push. Ratchet entries and code/test/kernel accepted-history entries = the owner's Role: owner commit
  (DEC-862 (a), DEC-891), validated first with the pin's readers (`tools/validate_entry.py`, DEC-895).
- **No placeholders (DEC-893):** exact times only; `tools/placeholder_scan.py` (in record_checks.sh).
- **After every merge (DEC-895):** `tools/probe_impact.py <merge>`; a stale probe of a merged-not-closed FULL
  ticket is scheduled at once.
- **Closes:** `tools/close_queue.sh <ids>` runs gates (c) checkpoint, rebuild, (a) collection, (f) record suites,
  (g) network, (b) gov check, (e) trailers, (h) work-without-a-task (pin's code), (d) tree as the close reads it.
  **Until the first re-pin, no close unless (a)-(h) all predict a pass (DEC-896).** Record edits:
  `tools/record_checks.sh` first; no main-tree commits while a queue runs. Never rebuild-until-green.
- **Policy 1 (DEC-887):** `python3 governance/project/orchestration/sync_context.py --commit "<subject>"` (record/w2;
  safe during closes); `--main` only with a head-moving decision commit, never during a close. Owner's daily push:
  `git -C /home/usain/Dynamic-Agentic-Engineering-OS push origin w2/integrate record/w2`.
- **Supersession (DEC-866):** mark at once, sweep by id and value.

### Plan in force (DEC-884, DEC-889 items 14-15, DEC-892, DEC-896, DEC-897)
- **REVIEW POINT: NO W2-66/67/68 work until the owner confirms the bundle in writing.** Bundle:
  `drafts/review-bundle/00-INDEX.md` (+01 W2-66 ticket, 02 W2-66 card, 03 W2-68 card, 04 W2-67 card, 05 W2-57
  ticket, 06 W2-07 card, 07 re-pin plan, 08 P-IS-5 corrections; added 10-23 on the owner's ask: 03b W2-68 ticket,
  04b W2-67 ticket, 05b W2-57 card, 06b W2-07 ticket, 09 W2-70 ticket + card, 10 register draft DEC-899, and
  ALL-DRAFTS-AND-PACKAGES.md (98,649 bytes, built by scratchpad combine_bundle.py, verbatim parts)). ACT pinged 10-22 after W2-50's close. Needs:
  P-IS-1..7 (rec (a) each; the owner chooses the two p95 entries in P-IS-6), the re-pin plan, DEC-898's figures,
  area 4's resume (rec no; the nightly covers it). P-IS-3 (a) -> new small ticket W2-70 (retire W1-05's
  switch-over + W1-47's builder rerun; merges early, closes after W2-07 is pinned).
- **First re-pin:** W2-58, W2-59, W2-65, W2-66, W2-07, W2-69; second: W2-68. W2-59 + W2-65 unmerged until just
  before the first (an earlier merge needs a package). Until the first re-pin: no close unless gates (a)-(h)
  predict a pass; DEC-897 (b): one proven re-run per close on a secrets chance red.
- **W2-58, W2-63 merged-not-closed, wait for the first re-pin.**
- Free slots now: **W2-69** (FULL; brief A5 to write; W2-L373 and P-IS-5 if taken), W2-65 (stacked on w2/W2-59;
  after P-IS-5's path fix), the nightly (no worksteal; covers area 4's missing runs), held resumes by keystone.

### Where things stand (10-22 22:22)
- **Owner pushed through `49c24ac9`.** Since: DEC-893+894 `da3d77e1`; DEC-895 `365f1307`; DEC-896 `c4f2b303`;
  DEC-897 `89e760fb`; W2-62 closed `d7daf01b` + rows `466c63ae`; W2-69 `89f043e2`; DEC-898 `17515bba`; W2-20 KPI
  `efa2e4b0`; W2-50 merge `2bf30b7c`, closed `01488b72`, row `68314b8e`; lens I in docs `210721e0`.
- **Closed (gov close):** W2-01 (tk), W2-53, W2-02, W2-54, W2-62, W2-50. Close success 5 of 18. Progress: 6 closed /
  2 merged-not-closed / 10 built and held / 0 in flight / 40 not started, of 58; keystones 0 / 8 / 1.
- **Lens I:** all five reports in `docs/assessment/2026-10/` (I1..I4, I-SYNTHESIS; byte-identical). Their evidence
  folders kept under `/tmp/gov-os-assessment-I1..4` and `-H` (clones, mutation copies, temp trees removed).
- **Disk (DEC-898):** 332 GB used (35 %), 30.4M inodes (46 %), from 640 GB / 62.6M (94 %) at 20:15. Still to look
  at: `/tmp/pytest-of-usain` (61 run folders since 10-20), 44 `/tmp/gov-testcache-*`, `/tmp/gov-os-tooltrial`
  (remove after trial d). My write to `~/gov-os-runs/W2-00/...` was refused by the guard: do not retry.
- **Candidate rows (with the next record commit):** W1-38's `TestGenerateCheck::test_check_clean_after_generate`
  and `TestRegisteredFamilyCheck::test_gov_check_lists_the_check_under_the_family` red under load, not on
  load_sensitive (W2-50 run 9); the inode exhaustion of 10-22 (DEC-898).
- **Trials:** redo trial d (rerunfailures -rR, -p no:randomly; randomly with its seed) in a quiet window, then
  REMOVE /tmp/gov-os-tooltrial and show it.
- **Path map placeholder:** the W1-38 load_sensitive reason's time (real: between 00:12 and 00:16 on 10-22) goes
  into the owner's next ratchet commit or W2-57's removal.
- **Credentials:** only two tracked fixtures (`fixtures/brownfield/project/.env`, `.../config/secrets.yaml`), W2-M398.
- **`.git/config.lock`:** zero-byte read-only placeholder; leave alone. **W2-48's worktree** to remove after a sync
  (branch kept, `2c3c46b5`).

### Next
1. Owner answers the bundle -> record (DEC-899 on), commit the confirmed drafts (each ticket file with its Task),
   create W2-70 if P-IS-3 (a), start W2-66 + W2-07, then W2-69.
2. Meanwhile: W2-69's lead brief; the nightly run in a quiet window; the daily digest (records since push, usage,
   refusals, memory use); trial d redo; pytest-of-usain + testcache clean-up.
3. Next free: DEC-899; ticket W2-70; rows W2-M405, W2-L415, W2-H063. Briefs: `tools/build_lead_brief.py <part>
   <out> ID= W2= PROFILE= PATHS= ROWS= SOURCES= IMPL= EST=`.

### Never
push/tag/rebase/main; amend w2/integrate; `gov approve`; Role: owner; `rebuild --no-embeddings`; tk close a W2
ticket without the owner; hooks; --no-verify; print secrets or held-out contents, or name the qualification
oracle; ~/gov-os-workbench; grow accepted_reds/load_sensitive; weaken a hard-block check; let the ratchet retry;
`$VAR` write targets (also sed -i); heredocs/backticks in commands (DEC-409).

## Archive
The long history moved to `CHECKPOINT-ARCHIVE.md` beside this file (DEC-792, 2026-10-18).

<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-10-22T13:03:06Z 0b7f6918a796405016de40c350cc1e40dff43d0dbb0178584068c088a85f6003
git head: 2b20aa2783cd7e797b46ba5abf52903c50f40c18
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0z8c [in_progress] - W2-05 The git environment of every check, hook and helper; the settings re-sort <- [DAEO-g0ip]
  DAEO-2ds6 [in_progress] - W2-26 EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)
  DAEO-49o5 [in_progress] - W2-16 Immutable, hash-pinned releases (CAP-43.b lite) <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-5j8b [in_progress] - W2-58 Policy 2 in the guard and the launcher: reads open, four refusals
  DAEO-6n5k [in_progress] - W2-37 gov impact <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-egsy [in_progress] - W2-51 The Wave 2 plan validator <- [DAEO-g0ip]
  DAEO-ha8z [in_progress] - W2-49 Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P) <- [DAEO-g0ip, DAEO-egsy]
  DAEO-juee [in_progress] - W2-62 Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force
  DAEO-kh9l [in_progress] - W2-59 The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps
  DAEO-kl5e [in_progress] - W2-50 The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P) <- [DAEO-g0ip]
  DAEO-pl6k [in_progress] - W2-63 W1-49's two window tests follow DEC-838: no compaction threshold, the model's own window
  DAEO-r30l [in_progress] - W2-20 Machine-wide resource gate <- [DAEO-g0ip]
  DAEO-siiz [in_progress] - W2-52 The lite A7 and A10 stage records <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-ym8a [in_progress] - W2-03 Decisions as records, each with its own hash <- [DAEO-g0ip, DAEO-zflj]
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  2b20aa27 [w2/integrate]
  /home/usain/gov-os-worktrees/W2-00-record   ebfce59a [record/w2]
  /home/usain/gov-os-worktrees/W2-03          9a3e3456 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-05          f19f156e [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-16          1908149d [w2/W2-16]
  /home/usain/gov-os-worktrees/W2-20          1a54976c [w2/W2-20]
  /home/usain/gov-os-worktrees/W2-26          62c4e477 [w2/W2-26]
  /home/usain/gov-os-worktrees/W2-37          2ff873b2 [w2/W2-37]
  /home/usain/gov-os-worktrees/W2-49          19d45246 [w2/W2-49]
  /home/usain/gov-os-worktrees/W2-50          b9a5e5cd [w2/W2-50]
  /home/usain/gov-os-worktrees/W2-51          c2c80e6c [w2/W2-51]
  /home/usain/gov-os-worktrees/W2-52          a21f06a7 [w2/W2-52]
  /home/usain/gov-os-worktrees/W2-58          09f5ebfa [w2/W2-58]
  /home/usain/gov-os-worktrees/W2-59          1cad6aa0 [w2/W2-59]
  /home/usain/gov-os-worktrees/W2-62          fbc6b706 [w2/W2-62]
  /home/usain/gov-os-worktrees/W2-63          ad38ed68 [w2/W2-63]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
