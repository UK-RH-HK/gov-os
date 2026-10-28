# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-28 14:30 GMT — RE-PIN 2 DONE: gov = pin-5c401220 (owner `bc37c419`), smoke passed, DEC-935 `eb0015a4`; the nightly route takes 15 entries out of the close (nightly only now); owner installing ACT-NIGHTLY-1; QUEUE STARTED W2-58, W2-63, W2-07, W2-57 (all full; gates e+h dry pass); NO main-tree commits while it runs; next DEC-936)

### Now
- **Pin:** gov = pin-6a4696eb (DEC-922); pin-fecb870c kept. Tools now read the pin from ~/.local/bin/gov's first line.
- **Queue 2026-10-27c done:** 7 closed (W2-66 full; six scoped off `00b371a0`). Gates ~12 min per close > the scoped
  close -> re-plan item. Closed tickets' worktrees removed except **W2-65's** (guard refused my rm of its stray
  `pytest-of-usain/`, 5.8M) -> digest. Rows moved to §4 (`4f2fc3d6`).
- **Merged today:** W2-57 `57e363c5`; W2-07 r2 `8555aafc` (run 5: full 16479 passed, serial 180; probe_impact made
  W2-57's probe stale on command.py); W2-57 re-probe `4904a60f` (PR-DAEO-cy5o-reprobe-1.md pass). Rebuilds ok. Temp
  folders of W2-07, W2-57 removed. Merged-not-closed now: W2-58, W2-63, W2-07, W2-67 (r1), W2-57.
- **ACT-W2-57-LS-1 done** (owner `6367e965`). ACT-W2-57-LS-2 (W1-46 x23, W1-19) right after re-pin 2, validated
  with the new pin (`tools/act_clone_run.sh`, reads the pin from ~/.local/bin/gov).
- **Re-pin 2 (DEC-933):** ACT-REPIN-2 sent (`packages/ACT-REPIN-2.md`; `pin/REPIN-COMMANDS-5c401220.sh`, plain
  terminal). Ladder: full run on 5c401220 16478 passed, 1 flaky (W2-54 time limit, passed alone), serial 180; wheel
  e4f35131…905d0 twice. When owner says done: smoke test, prompt pin line (DEC-895's command), ACT-W2-57-LS-2, queue
  W2-58, W2-63, W2-07, W2-57. Confirm no lead/close/nightly before the owner runs it.
- **Nightly (DEC-934):** committed `governance/project/orchestration/nightly/` (cron entry refuses changed code;
  logs + rotate; morning check -> status.txt; test_nightly.sh 20/20). ACT-NIGHTLY-1 revised: Part A crontab (3
  lines), Part B Windows wake task 01:50 + wake timers. cron measured: 4/4 hourly runs every night 10-20..10-28.
  Digest: report status.txt per night; no line = MISSED P1. Scratch copies removed.
- **Lesson today:** record checks on untracked files prove nothing about tracked ones (a999f97b's 9 paths in no
  namespace, W1-08 red, fixed 95a810a6); and never chain a commit after `;` (1916501d went in on a red check).
  W2-58's review cases fail when run from inside a Claude session (its env leaks into the guard sandbox): row.
- **Rows added:** W2-L449 (bare run loads the pin), W2-M407 (product nightly rule), W2-L450 (W2-57 designer p95
  under load, not on load_sensitive).
- **Run clones** under ~/gov-os-runs/W2-00 (2.6G+, plus 560M ACT clone) never removed -> P-TOOLS-REVIEW-1.
- **W2-67** held (probe stale: W1-26/W1-27 + w1_07_support.py; `d0140d4d`).
- **Owner's asks in the register:** DEC-929 (P-SCOPE-RECORDS-1), DEC-930 (re-plan after re-pin 2; four weekly
  numbers), DEC-931/932 (ACTs), DEC-933 (re-pin cadence; nightly rule).

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
- **Implements: ids (DEC-927, standing):** gate (e) = `tools/trailer_gate.py` also refuses an Implements item that is
  not a DEC the register holds or a CAP the store holds; leads run it on their worktree before returning
  (LEAD-w2-common); build_lead_brief.py refuses a non-id IMPL. CAP-n reading ACCEPTED by the owner (DEC-928).
- **ACT wording (DEC-928, standing):** "a plain terminal, not a Claude session" only when an ACT replaces or
  reinstalls gov (a re-pin); an owner commit of a patch is run by the owner's operator.

### Plan in force (DEC-896..DEC-919)
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

### Next
1. **Re-pin 2:** full run -> ACT-REPIN-2 -> smoke -> ACT-W2-57-LS-2 -> queue W2-58, W2-63, W2-07, W2-57.
2. Packages P-SCOPE-RECORDS-1 (DEC-929) and P-TOOLS-REVIEW-1; then the re-plan package (DEC-930). Re-pin 3 =
   W2-68 + W2-71 when they land.
3. **P-TOOLS-REVIEW-1 (independent review of my tools: lens + this week's slips, list in the
   archive; acceptance tests for build_lead_brief.py and the queue's gates). Repair tickets DAEO-2upp (W2-70) and
   DAEO-s1wp (W2-66, now closed): owner's decision.
4. W2-57's proposals for the digest/owner: P-1 (entry criterion on row W2-M406's fix: gov.close.nightly must run both
   routes; DEC-803, mine to record); P-2 (DEC-549 P-4 re-baseline (c): owner, DEC-105 options); P-R2-T1 (mark DEC-373
   changed by DEC-925 + W1-19 README via a ticket); rows F3/F4/O2/O3, run 1 F3/F4/O1; W1-09 condition.
3. W2-67: merge-back + judgement-only re-probe of the W1-26/W1-27 files.
4. Daily digest (DEC-922..); sweep; trial d redo + remove /tmp/gov-os-tooltrial; W2-72's residuals to rows.
5. Next free: DEC-932; ticket W2-75; rows W2-M407, W2-L449, W2-H063.

### Never
push/tag/rebase/main; amend w2/integrate; `gov approve`; Role: owner; `rebuild --no-embeddings`; tk close a W2
ticket without the owner; hooks; --no-verify; print secrets or held-out contents, or name the qualification
oracle; ~/gov-os-workbench; grow accepted_reds/load_sensitive; weaken a hard-block check; let the ratchet retry;
`$VAR` write targets (also sed -i); heredocs/backticks in commands (DEC-409).

## Archive
The long history moved to `CHECKPOINT-ARCHIVE.md` beside this file (DEC-792, 2026-10-18).

<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-10-27T20:51:25Z c04801fc00fd86097d5b1e79af2d4f9a63255abe226a2ee31f4aee18f669a161
git head: 00b371a09163e86f20a086c1e6664073902c4173
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0z8c [in_progress] - W2-05 The git environment of every check, hook and helper; the settings re-sort <- [DAEO-g0ip]
  DAEO-2azm [in_progress] - W2-74 The settings regeneration's test revisions: the docs/source cases retired, W1-49's sandbox gov, W2-69's case name
  DAEO-2ds6 [in_progress] - W2-26 EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)
  DAEO-49o5 [in_progress] - W2-16 Immutable, hash-pinned releases (CAP-43.b lite) <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-5j8b [in_progress] - W2-58 Policy 2 in the guard and the launcher: reads open, four refusals
  DAEO-6n5k [in_progress] - W2-37 gov impact <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-9nys [in_progress] - W2-67 Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions
  DAEO-c1uz [in_progress] - W2-66 Path-scoped regression at close: selection and evidence (the lite W2-38)
  DAEO-cy5o [in_progress] - W2-57 Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry
  DAEO-e82f [in_progress] - W2-65 The guard's hook lines refuse a call when the guard program cannot run
  DAEO-egsy [in_progress] - W2-51 The Wave 2 plan validator <- [DAEO-g0ip]
  DAEO-ha8z [in_progress] - W2-49 Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P) <- [DAEO-g0ip, DAEO-egsy]
  DAEO-kh9l [in_progress] - W2-59 The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps
  DAEO-pl6k [in_progress] - W2-63 W1-49's two window tests follow DEC-838: no compaction threshold, the model's own window
  DAEO-qty6 [in_progress] - W2-73 W1-03's head-move fixture: an amend that always moves HEAD
  DAEO-r30l [in_progress] - W2-20 Machine-wide resource gate <- [DAEO-g0ip]
  DAEO-r9ss [in_progress] - W2-07 gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close <- [DAEO-g0ip, DAEO-zflj, DAEO-7rr2]
  DAEO-rmbe [in_progress] - W2-69 The secrets check reads what the stores hold: no chance red from where a scan begins
  DAEO-siiz [in_progress] - W2-52 The lite A7 and A10 stage records <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-ye2a [in_progress] - W2-72 Containment's merge rule matches DEC-912: a merge-back file equal to git's own merge is no change
  DAEO-ym8a [in_progress] - W2-03 Decisions as records, each with its own hash <- [DAEO-g0ip, DAEO-zflj]
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  00b371a0 [w2/integrate]
  /home/usain/gov-os-worktrees/W2-00-record   a6efab00 [record/w2]
  /home/usain/gov-os-worktrees/W2-03          9a3e3456 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-05          f19f156e [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-07          75048114 [w2/W2-07]
  /home/usain/gov-os-worktrees/W2-16          1908149d [w2/W2-16]
  /home/usain/gov-os-worktrees/W2-20          1a54976c [w2/W2-20]
  /home/usain/gov-os-worktrees/W2-26          62c4e477 [w2/W2-26]
  /home/usain/gov-os-worktrees/W2-37          2ff873b2 [w2/W2-37]
  /home/usain/gov-os-worktrees/W2-49          19d45246 [w2/W2-49]
  /home/usain/gov-os-worktrees/W2-51          c2c80e6c [w2/W2-51]
  /home/usain/gov-os-worktrees/W2-52          a21f06a7 [w2/W2-52]
  /home/usain/gov-os-worktrees/W2-57          da0240e0 [w2/W2-57]
  /home/usain/gov-os-worktrees/W2-58          09f5ebfa [w2/W2-58]
  /home/usain/gov-os-worktrees/W2-59          1cad6aa0 [w2/W2-59]
  /home/usain/gov-os-worktrees/W2-63          ad38ed68 [w2/W2-63]
  /home/usain/gov-os-worktrees/W2-65          f6881547 [w2/W2-65]
  /home/usain/gov-os-worktrees/W2-66          d738898f [w2/W2-66]
  /home/usain/gov-os-worktrees/W2-67          d0140d4d [w2/W2-67]
  /home/usain/gov-os-worktrees/W2-69          ade5cbdb [w2/W2-69]
  /home/usain/gov-os-worktrees/W2-72          2bd574f3 [w2/W2-72]
  /home/usain/gov-os-worktrees/W2-73          42daa2ab [w2/W2-73]
  /home/usain/gov-os-worktrees/W2-74          260aa087 [w2/W2-74]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
