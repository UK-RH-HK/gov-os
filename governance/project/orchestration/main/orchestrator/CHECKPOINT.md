# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-24 21:25 BST — W2-65 run 2 PACKAGES -> DEC-917 (delegated, owner's acceptance asked), run 3 launched; P-W2-L437-B (3 lines, P2) with the owner; DEC-917 accepted `92ad3a84`; W2-67 run 3 in flight; next free DEC-918)

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

### Plan in force (DEC-896..DEC-912)
- **First re-pin:** W2-58, W2-59, W2-65, W2-66, W2-07, W2-69 (W2-59 + W2-65 merge together just before; settings
  regeneration drops `docs/source` read-deny rules and adds a lead's own-temp allow rule). Second: W2-68. Until the
  first: no close unless gates (a)-(h) predict a pass; DEC-897 (b) one proven re-run; the interim skip guard (31).
- **Merged, not closed:** W2-58, W2-63, W2-70 (`efdc4188`; round 2 `3ff8ba51`), W2-07 (`2a9d1a11`), W2-67 round 1
  (`4da40b60`), W2-69 (`2d5a829a`; originals kept in `/tmp/gov-os-lead-W2-69/records-original/`, which trip gitleaks),
  **W2-66 (`c60c9704`, 20:35; third and last review passed at `6eb5a93f`, probe `d738898f`; full run 16,131 / serial
  265 green; tree == merge-tree; probe_impact 0; `test_inputs` removed `8f56ada1`; rows W2-M406, W2-L430..437
  `e2c7a7e2`; temp folder removed).** Containment flags `03f470a5` (row W2-L437). W2-07's readers: record key
  `class_evidence`.
- **DEC-912** (`6f6ce36d`): W1-01's merge rule passes a merge whose acceptance files equal git's own merge (W2-70 r2;
  a conflict outside tests/acceptance/ keeps the allowance, reported to the owner). **DEC-913** (`3e27836d`, owner
  accepted `38e415e0`): W2-65's kernel template hook lines + W1-27 fixture. **DEC-911** (`6a898cbf`): 12-digit hashes,
  no keyword of row W2-L423's rule under `.gov-runtime/`; `tools/keyword_warn.py` (record_checks prints, close_queue
  stops); W2-71 = DAEO-e8f0, after the first re-pin, carried by the second with W2-68.
- **In flight: W2-65 run 3** (task by90xb0ig, `log/W2-65-A5-run3.json`, from `52a52481`): merge integrate, td W1-38
  revision (DEC-917 `07432ed0`, delegated, owner's acceptance asked; ticket `fa53ba34`: guard lines exit-mapping form,
  lifecycle lines plain), full run. Run 2 (`52a52481`): kernel template lines `2bee46b4`, W1-27 fixture `03d9aa08`;
  rows W2-L438 (lifecycle hooks fail open; exit 2 would loop), W2-L439 (lexical canary on its own declaration). On
  DONE: hold; W2-59 + W2-65 merge into integrate (merge-tree, probe_impact, temp folders), then the re-pin ACT.
  `W2-65/pytest-of-usain/` stays (owner).
- **DEC-915** (`326bd563`): skip guard by reasons (`tools/skip_gate.py`, known list `tools/skip_known.json`, 31
  entries: 30 from W2-66's/W2-65's green JUnit + the deliberate test_inputs skip; validated 8/8 on synthetic answers;
  additions named in the digest); W2-57 first free slot after the first re-pin; **W2-66's nightly command
  (`python3 -m gov.close.nightly`) NOT run until W2-M406's fix** (repo-wide `git worktree prune`); nightly.sh stays.
- **DEC-916** (standing): up to two reviews per round declared in the plan; W2-67 rounds 2+3 reviewed together.
- **P-W2-L437-A** (`d44cee76`, P1) with the owner: the close's containment gate refuses W2-66 (`03f470a5`) and W2-65
  (`4ef3293a`); all other pending tickets clean (scratchpad `judge_tickets.py`); live hook only flags. Recommended
  (a) W2-72 in the guard, second re-pin; W2-66/W2-65 close after it.
- **The re-pin ACT package** (after W2-59 + W2-65 merge): pin commands, pytest-timeout in the pin's env, settings
  regeneration (drop `docs/source` read-deny; lead's own-temp allow rule); ladder evidence = W2-66's fixture trial
  (3 closes) + 32/32 planted faults + its live-map cases (batching/reuse are W2-68's, DEC-890).
- **W2-67 run 3 = rounds 2 + 3** (DEC-914 `52065681`, delegated; task b6xu384z3, `log/W2-67-A5-run3.json`, from
  `09c327d2`): W1-30 13 cases + W2-L420, 15 unit close nested-run functions, W2-50 large-store/hang cases, ride-alongs
  (TD4-A, P1 option A, TD1C-A, F3), plant removal; returns DONE-UNREVIEWED; then its review under DEC-916 (one review of both rounds; one more if it fails).
- **Standing (summary):** full runs pass `-o tmp_path_retention_policy=failed` under `flock /tmp/gov-os-verify.lock`
  (DEC-905; lock until W2-67 lands, DEC-906); changes under tests/acceptance/ only by test designers (DEC-906); owner
  Role: owner commits = ratchet, accepted_history, acceptance_exemptions entries, validated first with a full run;
  remove each returned lead's temp folder after a holder check (DEC-904 item 2); weekly sweep (DEC-902; lists 3 + 5
  still to run in a quiet moment: `tools/sweep.py --apply --only pytest-runs,code-graph`).

### Where things stand (10-24 20:45)
- **Owner pushed through `18ad2382`** (commit C). Since: DEC-907..DEC-913, the W2-70 / W2-07 / W2-67 / W2-69 / W2-70 r2
  / W2-66 merges, rows, tickets W2-71 `e48a0f57`, packages P-W2-69-R2-1, P-W2-L423-A, P-W2-66-M1-R2, P-SKIP-GUARD-1.
- **Closed:** W2-01, W2-53, W2-02, W2-54, W2-62, W2-50. Close success 5 of 18. Progress: 6 closed / 7 merged-not-
  closed / 10 built and held / 2 in flight (W2-65 run 2, W2-67 run 3) / 36 not started, of 61; keystones 0 / 8 / 1.
- **Owner's digest items:** P-W2-67-TD1B-B (pinned version local label), P-W2-67-TD2-A (CIT-E per readiness change).
- **Disk:** check with `df -i /`; leads' temps removed on return; the sweep's lists 3 + 5 pending.
- **Credentials:** only two tracked fixtures (W2-M398). **`.git/config.lock`:** leave alone.

### Next
1. W2-65 run 3 DONE: W2-59 + W2-65 merge together (merge-tree, probe_impact, both temp folders), then the re-pin
   ACT package (see above). PACKAGES: to the owner.
2. On the owner's P-W2-L437-A answer: record DEC-918; (a) = ticket W2-72 (containment, FULL).
3. W2-67 run 3 DONE-UNREVIEWED: its review (DEC-916), then merge (after the re-pin). W2-57 first after the re-pin.
4. Daily digest; the sweep in a quiet moment; trial d redo, then remove /tmp/gov-os-tooltrial.
5. Next free: DEC-918; ticket W2-72; rows W2-M407, W2-L438, W2-H063.

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
