# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-24 23:35 BST — W2-65 DONE, held at `f6881547`; DEC-919; W2-72 (first re-pin) and W2-67 run 3 in flight; next free DEC-920)

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

### Plan in force (DEC-896..DEC-919)
- **First re-pin** carries W2-58, W2-59, W2-65, W2-66, W2-07, W2-69, **W2-72** (DEC-918). Order: W2-72 DONE -> merge;
  then W2-59 + W2-65 merge together (`w2/W2-65` holds W2-59; dry merge-tree onto integrate clean) -> probe_impact ->
  re-judge every pending ticket's merges with scratchpad `judge_tickets.py` (must be clean) -> the re-pin ACT package
  (pin commands, pytest-timeout in the pin's env, settings regeneration: drop `docs/source` read-deny, add a lead's
  own-temp allow rule; ladder evidence = W2-66's fixture trial + 32/32 planted faults; batching is W2-68's). Second
  re-pin: W2-68 + W2-71. W2-57 takes the first free slot after the first re-pin (DEC-915).
- **Merged, not closed (7):** W2-58, W2-63, W2-70 (`efdc4188`, r2 `3ff8ba51`), W2-07 (`2a9d1a11`), W2-67 r1
  (`4da40b60`), W2-69 (`2d5a829a`), W2-66 (`c60c9704`; `test_inputs` removed `8f56ada1`). The close's containment gate
  refuses W2-66 (`03f470a5`) and W2-65 (`4ef3293a`) until W2-72 is pinned.
- **Held DONE: W2-65 at `f6881547`** (run 3: W1-38 revised per DEC-917, W1-01/W1-27/W1-38/W2-65 green; reds not its
  own: W2-54 600 s timing (W2-L429), W1-19 load_sensitive, W2-66's lead-verification case (DEC-919, W2-L440);
  `gov check` RED only adapter-portability until the regeneration). Evidence `/tmp/gov-os-lead-W2-65/verify-v3`.
  `W2-65/pytest-of-usain/` stays (owner).
- **In flight:** **W2-72** (DAEO-ye2a, task bot7jgimp, `log/W2-72-A5-run1.json`, FULL ~5 h: containment = DEC-912,
  W1-50 DP-24 revisions). **W2-67 run 3** (rounds 2+3, DEC-914; task b6xu384z3; returns DONE-UNREVIEWED, then one
  review of both rounds under DEC-916, one more if it fails; it will show W2-66's lead-verification known red).
- **Decisions today:** DEC-911 (12-digit hashes, no W2-L423 keyword under `.gov-runtime/`; `tools/keyword_warn.py`;
  W2-71 = DAEO-e8f0, second re-pin), DEC-912 (W1-01 merge rule = git's own merge), DEC-913/917 (W2-65's kernel lines;
  W1-38 two forms; owner accepted both), DEC-914 (W2-67 rounds 2+3), DEC-915 (skip guard by reasons:
  `tools/skip_gate.py` + `tools/skip_known.json`, 31 entries, validated 8/8; W2-66's nightly command NOT run until
  W2-M406's fix, nightly.sh stays), DEC-916 (standing: two reviews per declared round), DEC-918 (containment = DEC-912;
  W2-72 first re-pin), DEC-919 (W2-66 lead-verification known red; lead brief note).
- **Standing (summary):** full runs pass `-o tmp_path_retention_policy=failed` under `flock /tmp/gov-os-verify.lock`
  (lock until W2-67 lands); tests/acceptance/ only by test designers (DEC-906); owner Role: owner commits = ratchet,
  accepted_history, acceptance_exemptions entries; remove each returned lead's temp folder after a holder check;
  weekly sweep (lists 3 + 5 pending: `tools/sweep.py --apply --only pytest-runs,code-graph`). Older text: archive.

### Where things stand (10-24 23:35)
- **Owner pushed through `18ad2382`.** Since: DEC-907..DEC-919, merges W2-70, W2-07, W2-67 r1, W2-69, W2-70 r2,
  W2-66; tickets W2-71 `e48a0f57`, W2-72 `8fe6d284`; packages P-W2-69-R2-1, P-W2-L423-A, P-W2-66-M1-R2, P-SKIP-GUARD-1,
  P-W2-67-R23, P-W2-L437-A/B.
- **Closed:** W2-01, W2-53, W2-02, W2-54, W2-62, W2-50. Close success 5 of 18. Progress: 6 closed / 7 merged-not-
  closed / 11 built and held (W2-65 joins) / 2 in flight (W2-72, W2-67 run 3) / 36 not started, of 62; keystones
  0 / 8 / 1.
- **Owner's digest items:** P-W2-67-TD1B-B, P-W2-67-TD2-A; DEC-919 (delegated); skip list addition (test_inputs).
- **Disk:** `df -i /`; the sweep's lists 3 + 5 pending. **Credentials:** two tracked fixtures (W2-M398).
  **`.git/config.lock`:** leave alone.

### Next
1. W2-72 DONE: merge, probe_impact, temp folder; then W2-59 + W2-65 together; re-judge; the re-pin ACT (P1 ping).
2. W2-67 run 3 DONE-UNREVIEWED: its review (DEC-916), then merge after the re-pin.
3. Daily digest; the sweep in a quiet moment; trial d redo, then remove /tmp/gov-os-tooltrial.
4. Next free: DEC-920; ticket W2-73; rows W2-M407, W2-L442, W2-H063.

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
