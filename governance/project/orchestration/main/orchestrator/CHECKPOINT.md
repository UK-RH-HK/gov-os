# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-24 20:15 BST — W2-70 round 2 merged `3ff8ba51`; W2-66 run 3 at its full run and third review (head `6eb5a93f`); W2-65 run 1 PACKAGES -> DEC-913 (delegated, owner's acceptance asked), run 2 launched; next free DEC-914)

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
- **Merged, not closed:** W2-58, W2-63, W2-70 (`efdc4188`), W2-07 (`2a9d1a11`), W2-67 round 1 (`4da40b60`),
  **W2-69 (`2d5a829a`; DONE, third review passed; rows W2-L422..425 `cea70ea1`; R3-A a row by DEC-910 `10592b6e`
  (W2-L419 widened); byte-exact review originals kept in `/tmp/gov-os-lead-W2-69/records-original/`,
  which the sync cannot hold since they trip gitleaks)**.
- **DEC-912** (`6f6ce36d`; tickets `dc3a85f8` W2-70, `b2632d76` W2-66), on P-W2-66-M1-R2 (`de5f966c`): M1 (a) W1-01's
  merge rule passes a merge whose acceptance files equal git's own merge (merge-tree), else refused; R2 (a) owner's
  exception to DEC-413, third and last review; a further fail-open = package, no fourth round.
  - **W2-70 round 2 DONE, merged `3ff8ba51`** (tree == merge-tree, probe_impact 0; flag `flags/W2-70-R2-MERGED`
    written; temp folder removed; row W2-L426 `0c789794`, W1-01's README). Full run 15,938 passed / serial 265;
    03f470a5 and 4ef3293a pass. Reading to report to the owner: a merge-tree conflict OUTSIDE tests/acceptance/
    (03f470a5's is in command.py) does not remove the allowance; only a conflict on the file itself does.
  - **W2-66 run 3** (task b58cregy1, `log/W2-66-A5-run3.json`, from `5634d430`): merge integrate, td P1/P2, engineer,
    wait for the flag, merge integrate again, full run (W1-01 green), third FULL review. Rows R1-R4 at DONE; note
    `class_evidence` for W2-07's readers.
  - **W2-65 run 1 PACKAGES** (head `20d72c19`): P-W2-65-1 kernel template settings.json's 3 hook lines (W1-38 x6
    red), P-W2-65-2 its merge-back on W1-01 (answered by DEC-912, no exemption), P-W2-65-3 W1-27 doctor fixture
    (W2-59 x W2-67). **DEC-913** (`3e27836d`, delegated, owner's acceptance asked; ticket `fd813dfa`): (a), none,
    (a); rows W2-L427..429. **Run 2** (task bls9benwf, `log/W2-65-A5-run2.json`): merge integrate, td W1-27, engineer
    kernel lines, full run. Stray untracked `W2-65/pytest-of-usain/` (guard refuses my rm; not merged) for the
    owner or a later cleanup; `/tmp/gov-os-lead-W2-65/verify-v1` kept (JUnit evidence, holds fixture tokens).
- **In flight: W2-65 run 1** (DAEO-e82f, claimed `cbc7d08e`, stacked on
  W2-59 `1cad6aa0`, merged integrate `4ef3293a`; tests `ce70eb73` + W1-29 revision `d8f1af7d`; engineer next;
  estimate 3 to 4 h from 14:51; held unmerged, merges with W2-59 just before the re-pin; `log/W2-65-A5-run1.json`,
  task bfeof3y95; expect its 2 W1-01 reds from M1). **DEC-911** (`6a898cbf`): 12-digit hashes, no keyword of row
  W2-L423's rule under `.gov-runtime/` (in every brief), `tools/keyword_warn.py` in record_checks (prints) and
  close_queue (stops after the rebuild); W2-71 = DAEO-e8f0 (`e48a0f57`), FULL engineer, after the first re-pin,
  carried by the second with W2-68. W2-67 rounds 2 (after W2-66 merges: W1-30 13 cases + unit close nested
  runs + rows W2-L420, F4 guard) and 3 (after W2-69: W2-50 cases); its next designer removes the untracked
  `tests/acceptance/W1-27/w2_67_td4_plant.py` in its worktree.
- **At W2-66's merge:** remove `test_inputs` from the path map (DEC-903 item 4), record edit.
- **Standing (summary):** full runs pass `-o tmp_path_retention_policy=failed` under `flock /tmp/gov-os-verify.lock`
  (DEC-905; lock until W2-67 lands, DEC-906); changes under tests/acceptance/ only by test designers (DEC-906); owner
  Role: owner commits = ratchet, accepted_history, acceptance_exemptions entries, validated first with a full run;
  remove each returned lead's temp folder after a holder check (DEC-904 item 2); weekly sweep (DEC-902; lists 3 + 5
  still to run in a quiet moment: `tools/sweep.py --apply --only pytest-runs,code-graph`).

### Where things stand (10-24 08:40)
- **Owner pushed through `18ad2382`** (commit C). Since: DEC-907 `82e86d54`, DEC-908 `e4b745a6`, DEC-909 `5ee86abf`,
  the W2-70 / W2-07 / W2-67 merges, rows `7c3638c0` `a00ae32d`, tickets `a6af5bb1` `2d32b7bb` `488972e4` `9394c4fa`,
  packages P-W2-69-R2-1 `f47c3c47`, W2-69 merge `2d5a829a`, DEC-910 `10592b6e`, P-W2-L423-A `7f6e1ab5`, DEC-911
  `6a898cbf`, W2-71 `e48a0f57`, P-W2-66-M1-R2 `de5f966c`.
- **Closed:** W2-01, W2-53, W2-02, W2-54, W2-62, W2-50. Close success 5 of 18. Progress: 6 closed / 6 merged-not-
  closed / 10 built and held / 3 in flight (W2-66 run 3, W2-65, W2-67; W2-70 round 2 merged) / 36 not started (W2-71 new), of
  61; keystones 0 / 8 / 1.
- **Owner's digest items:** P-W2-67-TD1B-B (pinned version local label), P-W2-67-TD2-A (CIT-E per readiness change).
- **Disk:** check with `df -i /`; leads' temps removed on return; the sweep's lists 3 + 5 pending.
- **Credentials:** only two tracked fixtures (W2-M398). **`.git/config.lock`:** leave alone.

### Next
1. W2-66 run 3 DONE: merge, probe_impact, test_inputs removal, temp folder; then the re-pin's ladder. PACKAGES: to
   the owner (no fourth round).
2. W2-65 run 2 DONE: hold unmerged; W2-59 + W2-65 merge together just before the re-pin (after W2-66's merge).
3. Then W2-67 rounds 2 and 3; on W2-65's return W2-59 + W2-65 merge together; the re-pin ACT.
4. Daily digest; the sweep in a quiet moment; trial d redo, then remove /tmp/gov-os-tooltrial.
5. Next free: DEC-914; ticket W2-72; rows W2-M406, W2-L430, W2-H063.

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
