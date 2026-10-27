# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-27 15:50 GMT — W2-74 MERGED `6ee7b4d0` (full run green); CLOSE QUEUE RUNNING (7: W2-70 first, full; then scoped); W2-69 out (stale probe) -> re-probe brief ready, launch AFTER the queue; W2-07 r2 DONE, merge after the queue; W2-57 run 2 in flight; DEC-926 delegated `429cac2e`; next free DEC-927)

### Now (2026-10-26)
- **Pin:** gov = pin-6a4696eb (DEC-922; smoke test in the archive); pin-fecb870c kept for rollback.
- **First queue run (2026-10-26):** W2-70 refused, count 1, on 8 base reds (P-REPIN-R1; details in the archive).
- **W2-07 round 2 RETURNED DONE** (head `75048114`; gate (h) per DEC-923; W2-07 69/69; unmeasured 0/0/0 for W2-58,
  W2-63, W2-07 on `a42e899b`; full run = the 8 base reds + W2-54 load timeout, passed alone). **MERGE HELD until the
  close queue ends** (its src/gov/close change is shared core: merged now it would make every queued close full;
  DEC-883 no code merges while closes run). Its branch lacks `048f5758` (the 611955fa entry) -> merge-back before its
  own close. Rides the second re-pin. Temp folder removed. Lead's stricter readings O1-O4 (README) noted.
- **W2-57 returned PACKAGES** (run 1: probe fix, doctor, serial list done; review pass; branch head `d0bfeb6afd95`).
  P-W2-57-B: B1 (widen to command.py's serial call) + B2 to the owner; B3/R1/R2/A1 delegated unless objected.
  6 load_sensitive removals ready (at its merge). Two lead commits carry `Implements: engineer` (my IMPL error in
  its brief): a row; run 2 brief IMPL=DEC-892. Temp folder removed.
- **W2-67** stays held (probe stale on W1-26/W1-27 files; r2+r3 unmerged at `d0140d4d`).
- **Prior refusals on record:** W2-58 count 1 (WORK_WITHOUT_TASK), W2-63 count 1 (RULESYNC etc.). Commit-gate refusals
  are not counted by the new judge.

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
- **Settings changes and ACTs (DEC-925, standing):** any settings change or regeneration -> a full run in the close's
  form on a clone with it applied + a sweep for dependent tests, BEFORE the owner's commit; every ACT's commands in
  `governance/project/orchestration/packages/ACT-<id>.md`, named in the ping.

### Plan in force (DEC-896..DEC-919)
- **First re-pin = ACT-REPIN-1** (`8455edd6`; DONE 2026-10-26, smoke test passed, DEC-922; history below): owner runs `pin/REPIN-COMMANDS-6a4696eb.sh` Part A (wheel of
  `6a4696eb`, sha256 `73a281ff…c6b6c9`, dry run twice alike; pin-6a4696eb; link; `pin/repin_registry.py`; Role: owner
  commit) and Part B (by hand drop the two `docs/source` deny entries in `.rulesync/permissions.jsonc`; `rulesync
  generate --targets claudecode,agentsmd --features rules,hooks,permissions,subagents,commands,skills`; pinned
  `gov.guard.heldout`; commit). Lead clean-up rule: options (a) none yet [recommended] / (b) literal per lead / (c)
  pattern. **Before Part A: no Claude session running a gov command (W2-73's lead).** After: my smoke test (pinned
  `gov check`, adapter-portability GREEN, a guard allow + refuse, skip guard + keyword warning dry runs); then delete
  the backup ref `w2/integrate-before-reset-2026-10-24` (DEC-921); then the close queue.
- **Merged, not closed (11):** W2-58, W2-63, W2-70, W2-07, W2-67 r1, W2-69, W2-66, W2-72, W2-59, W2-65, W2-73. **Held DONE:
  W2-67** at `d0140d4d`, probe STALE (W1-26/W1-27 files changed by W2-59/65): after the re-pin, merge integrate back +
  a judgement-only re-probe of those files. W2-57 first free slot after the re-pin (DEC-915). Second re-pin: W2-68 +
  W2-71.
- **W2-72's residuals to rows** (F5-F8, the UnicodeDecodeError, the tab-in-name flag, stale facets, the transient
  secrets-indexing red): not yet filed.
- **Standing (summary):** full runs pass `-o tmp_path_retention_policy=failed` under `flock /tmp/gov-os-verify.lock`
  (lock until W2-67 lands); tests/acceptance/ only by test designers (DEC-906); owner Role: owner commits = ratchet,
  accepted_history, acceptance_exemptions entries; remove each returned lead's temp folder after a holder check;
  weekly sweep (lists 3 + 5 pending: `tools/sweep.py --apply --only pytest-runs,code-graph`). Older text: archive.

### HOLD lifted (owner, 2026-10-26): ACT-REPIN-1 done; DEC-922 recorded (lead clean-up rule (a): none yet; I keep
removing returned leads' temp folders after the holder check).

### Next
1. **Queue RUNNING** (task bsbmwu264, `log/close-queue-20261027-1546/`): DAEO-uzme DAEO-c1uz DAEO-ye2a DAEO-kh9l
   DAEO-e82f DAEO-qty6 DAEO-2azm. W2-70 runs full (no base); the six after it should be SCOPED off W2-70's close
   record: report each close's evidence scope / why_full / selected to the owner. W2-70's next refusal on the same
   reds = its second -> package. NO main-tree commit while it runs. keyword_warn: interim line removed; DEC-926 leaves
   out only the refused close's 4 JUnit files (exact paths).
2. **After the queue:** (a) launch W2-69's judgement-only re-probe (`briefs/W2-69-A5-run3.md`, built; worktree
   `34e1c59f06e6`), then merge it and close W2-69; (b) merge W2-57 FIRST (DONE run 2, head `da0240e0563e`,
   review 2 pass, probe `PR-DAEO-cy5o-review-2.md`; serial 104 cases 11:48 vs 180 17:40; nightly batch 76 green),
   then commit its 30 load_sensitive removals (W1-38 x3, W1-07 [doctor], W1-30 r13, unit close follow-up, W1-46 x23,
   W1-19 warm p95; list in `log/W2-57-A5-run2.json`); (c) W2-07 r2 SECOND: lead merges integrate back + re-verifies
   (STANDARD, no probe). Temp folders of W2-57 and W2-07 removed.
3. W2-57's proposals for the digest/owner: P-1 (entry criterion on row W2-M406's fix: gov.close.nightly must run both
   routes; DEC-803, mine to record); P-2 (DEC-549 P-4 re-baseline (c): owner, DEC-105 options); P-R2-T1 (mark DEC-373
   changed by DEC-925 + W1-19 README via a ticket); rows F3/F4/O2/O3, run 1 F3/F4/O1; W1-09 condition.
3. W2-67: merge-back + judgement-only re-probe of the W1-26/W1-27 files.
4. Daily digest (decisions since the owner's push of 8ba8b231: DEC-922); the sweep in a quiet moment; trial d redo,
   then remove /tmp/gov-os-tooltrial; W2-72's residuals to rows.
5. Next free: DEC-925; ticket W2-74 (proposed); rows W2-M407, W2-L449, W2-H063.

### Never
push/tag/rebase/main; amend w2/integrate; `gov approve`; Role: owner; `rebuild --no-embeddings`; tk close a W2
ticket without the owner; hooks; --no-verify; print secrets or held-out contents, or name the qualification
oracle; ~/gov-os-workbench; grow accepted_reds/load_sensitive; weaken a hard-block check; let the ratchet retry;
`$VAR` write targets (also sed -i); heredocs/backticks in commands (DEC-409).

## Archive
The long history moved to `CHECKPOINT-ARCHIVE.md` beside this file (DEC-792, 2026-10-18).

<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-10-24T13:52:07Z f2c5712158e10c392f25707b4f4db1ce65b35fedc6383db08728d98244ac557e
git head: cbc7d08ec61f8e6bfd2ad229d449aac037eff77b
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0z8c [in_progress] - W2-05 The git environment of every check, hook and helper; the settings re-sort <- [DAEO-g0ip]
  DAEO-2ds6 [in_progress] - W2-26 EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)
  DAEO-49o5 [in_progress] - W2-16 Immutable, hash-pinned releases (CAP-43.b lite) <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-5j8b [in_progress] - W2-58 Policy 2 in the guard and the launcher: reads open, four refusals
  DAEO-6n5k [in_progress] - W2-37 gov impact <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-9nys [in_progress] - W2-67 Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions
  DAEO-c1uz [in_progress] - W2-66 Path-scoped regression at close: selection and evidence (the lite W2-38)
  DAEO-e82f [in_progress] - W2-65 The guard's hook lines refuse a call when the guard program cannot run
  DAEO-egsy [in_progress] - W2-51 The Wave 2 plan validator <- [DAEO-g0ip]
  DAEO-ha8z [in_progress] - W2-49 Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P) <- [DAEO-g0ip, DAEO-egsy]
  DAEO-kh9l [in_progress] - W2-59 The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps
  DAEO-pl6k [in_progress] - W2-63 W1-49's two window tests follow DEC-838: no compaction threshold, the model's own window
  DAEO-r30l [in_progress] - W2-20 Machine-wide resource gate <- [DAEO-g0ip]
  DAEO-r9ss [in_progress] - W2-07 gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close <- [DAEO-g0ip, DAEO-zflj, DAEO-7rr2]
  DAEO-rmbe [in_progress] - W2-69 The secrets check reads what the stores hold: no chance red from where a scan begins
  DAEO-siiz [in_progress] - W2-52 The lite A7 and A10 stage records <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-uzme [in_progress] - W2-70 Retire the two nested reruns
  DAEO-ym8a [in_progress] - W2-03 Decisions as records, each with its own hash <- [DAEO-g0ip, DAEO-zflj]
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  cbc7d08e [w2/integrate]
  /home/usain/gov-os-worktrees/W2-00-record   f6752ecf [record/w2]
  /home/usain/gov-os-worktrees/W2-03          9a3e3456 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-05          f19f156e [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-07          80ec31ab [w2/W2-07]
  /home/usain/gov-os-worktrees/W2-16          1908149d [w2/W2-16]
  /home/usain/gov-os-worktrees/W2-20          1a54976c [w2/W2-20]
  /home/usain/gov-os-worktrees/W2-26          62c4e477 [w2/W2-26]
  /home/usain/gov-os-worktrees/W2-37          2ff873b2 [w2/W2-37]
  /home/usain/gov-os-worktrees/W2-49          19d45246 [w2/W2-49]
  /home/usain/gov-os-worktrees/W2-51          c2c80e6c [w2/W2-51]
  /home/usain/gov-os-worktrees/W2-52          a21f06a7 [w2/W2-52]
  /home/usain/gov-os-worktrees/W2-58          09f5ebfa [w2/W2-58]
  /home/usain/gov-os-worktrees/W2-59          1cad6aa0 [w2/W2-59]
  /home/usain/gov-os-worktrees/W2-63          ad38ed68 [w2/W2-63]
  /home/usain/gov-os-worktrees/W2-65          4ef3293a [w2/W2-65]
  /home/usain/gov-os-worktrees/W2-66          5634d430 [w2/W2-66]
  /home/usain/gov-os-worktrees/W2-67          09c327d2 [w2/W2-67]
  /home/usain/gov-os-worktrees/W2-69          34e1c59f [w2/W2-69]
  /home/usain/gov-os-worktrees/W2-70          e052b7b5 [w2/W2-70]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
