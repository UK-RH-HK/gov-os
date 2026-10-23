# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-23 10:37 BST — review point passed (DEC-899..901); W2-66, W2-07, W2-69 IN FLIGHT; ACT pending: owner commits A and B, install, cleanup; next free DEC-902)

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

### Plan in force (DEC-896, DEC-897, DEC-899, DEC-900)
- **Review point PASSED (DEC-899, `2f048613`).** Confirmed and committed, each ticket file with its Task:
  - W2-66 `DAEO-c1uz` `eaabff01`; W2-07 `DAEO-r9ss` `6ec371c4`; W2-57 `DAEO-cy5o` (new) `e51689e5`;
  - W2-70 `DAEO-uzme` (new, LITE) `a9aa5d55`; W2-68 + W2-67 cards `f4064457` (their ticket files when W2-66 merges);
  - W2-13 `d48bdd92` + `120f6c72` (AR-9 ruled; quote fix); W2-14 `8c828e85`; W2-65 `d562ad04`; W2-69 `306d11c2`;
  - MR-3 fixes `6a7995a5 b7bf96c8 230dc88a 2359abf0 b930ed41` (no tests/acceptance in an engineer's allowed_paths:
    the test designer's files named in the body).
- **IN FLIGHT (3 leads, started about 10:37 on `c2d539c6`):** W2-66 (`log/W2-66-A5-run1.json`), W2-07
  (`log/W2-07-A5-run1.json`), W2-69 (`log/W2-69-A5-run1.json`). **W2-07 MERGES FIRST; then W2-66 merges integrate
  back, re-verifies, fresh FULL probe** (owner exception to the overlap rule, DEC-899 item 2). W2-66 needs
  pytest-timeout (owner install package, in the ACT ping). On each return: merge per §3, probe_impact, sync.
- **First re-pin:** W2-58, W2-59, W2-65, W2-66, W2-07, W2-69 (W2-59 + W2-65 merge together just before it); the
  settings regeneration drops `docs/source` read-deny rules (P-I1-2). Second: W2-68. Until then: no close unless
  gates (a)-(h) predict a pass; DEC-897 (b); **the interim skip guard (DEC-899 item 7): close_queue.sh stops after a
  close whose regression skip count is not 31, outputs uncommitted (`tools/skip_gate.py`)**.
- **W2-58, W2-63 merged-not-closed, wait for the first re-pin.** W2-70 to start (LITE, test designer) in a slot.
- **Owner acts DONE (10-23):** commits A `596870bd` + B `c9a08678` (Role: owner; accepted_reds EMPTY,
  load_sensitive 30); pytest-timeout 2.4.0 installed (user site); pushed w2/integrate `c9a08678`, record/w2
  `d8e5e53d`; cleanup lists 1, 2, 4, 6 deleted by the owner (74 G used, 1.83 M inodes). **DEC-902 `f78f9799`**
  (standing sweep; prompt v3.20; registry; rows W2-M405 -> W2-21 `9662354e`, W2-L415 -> W2-57 `a05b5f66`).
- **W2-67 round 1 returned PACKAGES (test design done, head `60f71c42`):** the launcher refused an engineer on a
  test-designer ticket (my ticket-file slip). **DEC-907 (delegated) `82e86d54`** + ticket `a6af5bb1`: role engineer,
  acceptance files in the body; the fixtures by a second fresh designer; conftest refuses per-run --basetemp (opt-out
  GOV_ALLOW_BASETEMP=1); TD1B-B and TD2-A to the owner's DIGEST. Its temp removed (2.34M inodes). **Run 2 QUEUED**
  (`log/W2-67-A5-run2.json`).
- **DEC-906 (owner) `4bffc276`** on P-W1-01-H: STANDING: changes under tests/acceptance/ only by a test designer
  (retirements too); only ratchet, accepted-history and acceptance_exemptions entries stay Role: owner commits; an
  owner commit touching tests gets a full run first. W1-01's case reads `acceptance_exemptions` (exact shas), only
  entry c9a08678 / DEC-900, via W2-70 (`83a3867e`; claimed `23518192`; lead QUEUED, `log/W2-70-A5-run1.json`).
  **The entry's patch + validation RUNNING** (`tools/validate_exemption.sh`: pin readers + full run under the lock;
  results `/tmp/gov-os-exempt/out/run.txt`, patch `drafts/OWNER-C-acceptance-exemption.patch`) -> then ACT ping.
  Lock kept until W2-67 lands.
- **DEC-905 `ac119c37`: the retention trial HELD** (peak 165,707 inodes / 0.91 GB vs 5.3M / 47 GB; failing test's
  folder kept; 30 skips = rehearsal's). The option is the default (LEAD-common, nightly.sh, W2-66 KPI `bfddcb07`);
  bridge cap ENDED; lock KEPT (delegated); TMPDIR kept short (a long one breaks W2-58's sandbox sockets).
  **P1 `packages/P-W1-01-H.md` PINGED:** W1-01's MR-3 history case red on integrate since the owner's `c9a08678`
  (my slip: B validated without the full regression). Rec (a): W2-70 widened to revise it (narrow owner-commit
  exemption) + (c) future retirements as designer commits. Leads report it as known, not theirs.
- **DEC-904 (owner) `6b496169`** on P-W2-07-A-B: retention trial (`tools/retention_trial.sh`, RUNNING, results in
  `/tmp/gov-os-trial-retention/out/run.txt`; if it holds -> the option becomes the default for close, nightly, leads);
  allow rule for a lead's own temp at the settings regeneration; bridge cap 6,000,000 / 60 GB per verification run,
  ONE AT A TIME under `flock /tmp/gov-os-verify.lock` (nightly.sh + LEAD-common + trial use it); W2-67 forward
  (`DAEO-9nys` `de2b5bf1`, claimed `f9cf898e`, round 1 lead QUEUED behind the gate, `log/W2-67-A5-run1.json`);
  W2-07's batch widened (`3b5b04b5`); W2-07 run 2 QUEUED behind the gate (`log/W2-07-A5-run2.json`), then W2-66's
  run 2 (verification after W2-07's). Both stopped runs' temps REMOVED after the holder re-check (disk 130 -> 75 GiB, inodes 8,057,115 -> 1,927,340).
- **W2-07 run 1 returned PACKAGES (head `44062fec`, implementation complete, 40/40 own):** P1 `packages/P-W2-07-A-B.md`
  (`17e5c3a9`), PINGED: A = the lead budget vs a full run (1,062,156 inodes at 13.6 %; rec (a) pytest
  `-o tmp_path_retention_policy=failed` after a measured trial + (b) a 5,000,000 / 50 GB verification cap meanwhile
  + (c) an allow rule for a lead to rm its own temp at the settings regeneration; I remove `/tmp/gov-os-lead-W2-07/`
  on approval); B = widen W2-07's designer batch (W1-30 fixture green at gov check: 175; 20 gate-order cases; 1
  repair-ticket case). C delegated (six readings, DEC-903).
- **W2-66 run 1 returned PACKAGES (head `ba38ab8d`; tests 134, impl built):** its full run left 5,306,782 inodes /
  47 GB in `/tmp/gov-os-lead-W2-66/` (addendum to P-W2-07-A-B `7df69957`: bridge cap 6,000,000 / 60 GB, one run at a
  time; approve removing both leads' temps). P-W2-66-T1 decided as delegated **DEC-903** (`f4165cee`, ticket
  `a0197576`: W1-39 overlay case for its designer; `src/gov/cli/errors.py`). Its next round: serial run, the report +
  fixture trial (`briefs/eng-2.md` in its worktree), the review. At W2-66's merge: remove `test_inputs` from the path map.
  W2-69 is still running and will meet A at its full verification.
- **SWEEP lists 3 + 5 PENDING a quiet moment** (no `claude -p`, close, nightly or trial):
  `python3 tools/sweep.py --apply --only pytest-runs,code-graph` (dry run: 49 + 10,118 would go; skips: <24 h,
  held open, the 14 live roots' code-graph folders). Report what it skipped and why. Weekly sweep: Mondays.
- **Later packages:** P-IS-13 when W2-32 starts (owner leans (a)); P-IS-9..12, 14, 15 before their tickets.

### Where things stand (10-23 10:37)
- **Owner pushed through `49c24ac9`.** Since then all of DEC-893..DEC-901 and the commits above (unpushed).
- **Closed (gov close):** W2-01 (tk), W2-53, W2-02, W2-54, W2-62, W2-50. Close success 5 of 18. Progress: 6 closed /
  2 merged-not-closed / 10 built and held / 3 in flight / 39 not started, of 60 (58 + W2-69, added 10-22 and
  missed in two reports' totals, + W2-70; W2-57, W2-67, W2-68 were cards already counted); keystones 0 / 8 / 1.
- **Lens H's raw files archived** `record/w2` `f8525d6a` (main/evidence/lens-H, sha256 in its README); the share's
  README + SHA256SUMS `9e9c5768`; every share file has a committed original; **the share DELETED**.
- **My slips today, fixed:** W2-13's KPI unquoted colon (ticket schema red) and five MR-3 paths (core-mutation red),
  both from committing with core-schema only; record_checks.sh now runs W1-08's ticket test. Run the FULL
  record_checks.sh before every ticket commit.
- **Disk:** 332 GB used, 30.4M inodes. Inventory: `scratchpad/disk-inventory.tsv` (+ disk_inventory2.py output).
- **Candidate rows:** W1-38's two rulesync cases red under load (W2-50 run 9); the inode exhaustion of 10-22.
- **Trials:** redo trial d in a quiet window, then REMOVE /tmp/gov-os-tooltrial and show it.
- **Path map placeholder:** the W1-38 load_sensitive reason's time (real: between 00:12 and 00:16 on 10-22).
- **`.git/config.lock`:** leave alone. **W2-48's worktree** to remove after a sync (branch kept, `2c3c46b5`).

### Next
1. Owner's ACT: the two commits (A then B), the install, the cleanup approval. After A and B: record checks.
2. Lead returns: W2-07 first -> merge; W2-66 -> merge back + fresh probe; W2-69 -> merge. probe_impact each.
3. W2-70's lead in a free slot; the nightly in a quiet window; the daily digest.
4. Next free: DEC-903; ticket W2-71; rows W2-M406, W2-L416, W2-H063.

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
