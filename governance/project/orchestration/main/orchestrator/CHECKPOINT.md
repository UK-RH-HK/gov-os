# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-24 08:40 BST — W2-07, W2-70, W2-67 r1 merged; W2-66 run 2 and W2-69's last round queued; next free DEC-910)

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

### Plan in force (DEC-896..DEC-909)
- **First re-pin:** W2-58, W2-59, W2-65, W2-66, W2-07, W2-69 (W2-59 + W2-65 merge together just before; settings
  regeneration drops `docs/source` read-deny rules and adds a lead's own-temp allow rule). Second: W2-68. Until the
  first: no close unless gates (a)-(h) predict a pass; DEC-897 (b) one proven re-run; the interim skip guard (31).
- **Merged, not closed:** W2-58, W2-63, W2-70 (`efdc4188`), W2-07 (`2a9d1a11`), W2-67 round 1 (`4da40b60`),
  **W2-69 (`2d5a829a`; DONE, third review passed; rows W2-L422..425 `cea70ea1`; R3-A, widening W2-L419 to encoded key
  exports, for the owner's DIGEST; byte-exact review originals kept in `/tmp/gov-os-lead-W2-69/records-original/`,
  which the sync cannot hold since they trip gitleaks)**.
- **In flight:** W2-66 run 2 (merges integrate WITH W2-07, keeps both sides of `command.py`; W1-39 case; the
  retention KPI; report + fixture trial; fresh FULL probe; `log/W2-66-A5-run2.json`). W2-69 run 2, its LAST round
  (DEC-909: key blocks whole up to 24 KB; filter cases; two serial cases; a further fail-open finding = package, no
  fourth round; `log/W2-69-A5-run2.json`). W2-67 rounds 2 (after W2-66 merges: W1-30 13 cases + unit close nested
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
  packages P-W2-69-R2-1 `f47c3c47`.
- **Closed:** W2-01, W2-53, W2-02, W2-54, W2-62, W2-50. Close success 5 of 18. Progress: 6 closed / 5 merged-not-
  closed / 10 built and held / 3 in flight (W2-66, W2-69, W2-67) / 36 not started, of 60; keystones 0 / 8 / 1.
- **Owner's digest items:** P-W2-67-TD1B-B (pinned version local label), P-W2-67-TD2-A (CIT-E per readiness change).
- **Disk:** check with `df -i /`; leads' temps removed on return; the sweep's lists 3 + 5 pending.
- **Credentials:** only two tracked fixtures (W2-M398). **`.git/config.lock`:** leave alone.

### Next
1. On W2-66's return: merge (after W2-07, done), probe_impact, test_inputs removal; then the re-pin's ladder.
2. On W2-69's return: DONE -> merge; PACKAGES -> to the owner (no fourth round).
3. Then W2-67 round 2; W2-59 + W2-65 together; the re-pin ACT.
4. Daily digest; the sweep in a quiet moment; trial d redo, then remove /tmp/gov-os-tooltrial.
5. Next free: DEC-910; ticket W2-71; rows W2-M406, W2-L422, W2-H063.

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
