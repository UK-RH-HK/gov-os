# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-27 12:15 GMT — DEC-925 recorded (`ecc49cc4`): W2-74 + W2-57 run 2 + W2-07 r2 leads IN FLIGHT (3); queue waits for W2-74's merge, then W2-70 first (full: no base yet, then scoped); owner committed 611955fa entry `048f5758` and pushed; next free DEC-926)

### Now (2026-10-26)
- **Pin:** `~/.local/bin/gov` -> `pin-6a4696eb` (wheel sha256 `73a281ff…c6b6c9`); registry `82f2d453`, settings `8ba8b231`
  (both Role: owner, pushed). `pin-fecb870c` kept for rollback. Smoke test: pinned gov check exit 0 after one
  rebuild (15 GREEN, 2 known YELLOW: openspec not on PATH, citation warnings); guard allow/deny/exit-2 by the exact
  hook line; hooks and declared checks run the pin's python (-E / -P). Logs `log/repin1-smoke-*`.
- **Queue run 2026-10-26 22:02 (`log/close-queue-20261026-2157/`):** W2-70 (DAEO-uzme) close REFUSED exit 3 after 68 min
  (count 1; repair DAEO-2upp committed by the close `9fbaf969`); queue stopped; 6 others not run. 9 reds, none W2-70's:
  W1-01 docs_source x4 + W1-47 docs/source x2 (enforce the dropped deny rules: my DEC-866 sweep miss), W1-49
  precompact [not on PATH] (new lifecycle hook line exits 1 without gov), W1-06 (registry approved_by DEC-921 ->
  should be DEC-922; my repin_registry.py), W2-69 unit folder (pycache leftover: REMOVED). Package P-REPIN-R1 (P1,
  `dbfb76f0`): rec (a) LITE W2-74 test revisions + W2-69 case id rename + registry line by me; interim the warning
  leaves out .gov-runtime/close/ (the judge's JUnit holds the keyword via W2-69's case name, no hash).
- **W2-07 round 2 in flight** (A5 run 4, task bhsrfm93v, launched 11:05, `log/W2-07-A5-run4.json`), beside W2-57.
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
1. **In flight (3 leads):** W2-74 (DAEO-2azm, claimed `a42e899b`, task b3rzj4fta, `log/W2-74-A5-run1.json`);
   W2-57 run 2 (task bmlp2i9u5, `log/W2-57-A5-run2.json`; B1 route in command.py's serial call, R1, B3, R2; review 2
   = last); W2-07 r2 (task bhsrfm93v). Registry line fixed `1c3d4dff`; keyword_warn leaves out .gov-runtime/close/
   UNTIL W2-74 MERGES (then delete that line in tools/keyword_warn.py).
2. W2-74 DONE -> merge, probe_impact, remove the warning's interim line, then `tools/close_queue.sh DAEO-uzme
   DAEO-rmbe DAEO-c1uz DAEO-ye2a DAEO-kh9l DAEO-e82f DAEO-qty6` (W2-70 runs full: base unknown; the six after it
   should be SCOPED off W2-70's close record: show the owner each close's evidence scope/why_full/selected).
   W2-70's next refusal on the same reds = its second -> package. Then close W2-74 itself.
3. W2-57 / W2-07 r2 merges: second merger merges back + re-verifies + fresh probe if stale (DEC-924/925). On W2-57's
   merge, commit its load_sensitive removals (6 ready + any the route frees). W2-07 r2 rides the second re-pin.
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
