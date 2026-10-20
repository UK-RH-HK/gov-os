# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-20 20:40 BST — Wave 2 by keystones; 4 leads in flight; next free DEC-879)

### Standing owner rules (short; full text: register §248-§265, prompt v3.5; DEC-851)
- **Window (DEC-838):** full window (1M); no compaction threshold; never ask a session to stop early. Usage is the
  limit (`claude -p "/usage"` in the digest).
- **Checkpoint at every handover (DEC-837):** return, merge, package, compaction. Keep this section < 10,000 chars.
- **Memory used (DEC-836):** every brief says `gov retrieve`; from W2-04 briefs built with `gov context`; counted.
- **Large/code questions (DEC-859/860):** batches, ranked, stacked; code graph by traversal and pages.
- **Parallelism (DEC-847):** no fixed cap; measured gate (by hand: load1 < 20, MemAvailable >= 6710886 kB, in the
  launch command); owner's usage; never in a close's quiet window; ceiling 10; fewer until W2-48. Countdown says
  number in flight + why.
- **W2-58 ahead of everything (DEC-873; DEC-821's sandbox clause re-baselined; row W2-L374).** Until it lands take
  read refusals, never another form; search named folders; count them for the digest.
- **Notify (DEC-855):** six-part package in my message + `governance/project/orchestration/packages/<id>.md`; start
  all independent work; LAST ACTION `~/.local/bin/owner-ping "<P1|P2|COMMIT|ACT> <id> | gates <...> | <need>"`.
  Never AskUserQuestion; no secret/key/held-out path/file content; leads never ping. Gates nothing -> digest.
- **Current owner instruction (2026-10-20):** run the close queue behind the gate; **ping only if a close is
  refused, saying whether the cause is new or already seen.**
- **W2-48 (DEC-852, DEC-876):** subprocess code seen; fail safe; each widening proven by a test; `test_inputs`
  declared (65039414); nightly full uncached run; target >= 60-70 % reuse, close < ~15 min, else a fallback
  PACKAGE (no open round); simplify (1,680 lines vs 220).
- **Effort (DEC-839):** opus-5-5; high; max auditors/FULL probes/packages; xhigh FULL designers.
- **I commit owner decision records (DEC-861):** `Task: decision-record`, `Role: orchestrator`, `Decided-by: owner
  (chat, <date>)`; never Role: owner; never push. Ratchet entries/escalation lifts stay Role: owner commits until
  W2-12 (DEC-862): prepare + ping ACT.
- **Supersession propagates (DEC-866):** mark at once, sweep by id and value, update or keep with a reason.
- **Pre-close gate (DEC-868):** collect-only in one process; gov check after rebuild; fresh ticket checkpoint;
  clean tree; trailers; `tools/close_queue.sh <id>[:DEC-n] ...`. Record edits: `tools/record_checks.sh` first.
- **Policy 1 (DEC-819):** sync_context.py, gitleaks staged, commit `-- <paths>`, Task: DAEO-sdxk.
- **Also:** CAP-10 both figures (DEC-833); recalibrate after K2 (DEC-834); owner's daily backup push (DEC-848).

### Where things stand (20:40)
- **Owner pushed through `8dfd54e9`.** Records since: DEC-872 `4b6e5766`; DEC-873 `19357fcb`,`6e125150`; DEC-874
  `5f346750`; DEC-875 `8542a970`,`e6976ef3`; DEC-876 `65039414`; registry (testmon, coverage, DEC-843) `b0756906`;
  DEC-877 `97fc656a` (delegated); DEC-878 (the progress line, owner) below.
- **Closed by gov close:** W2-53 (15:53, outputs `a1565e56`). Close success 1 of 8 runs.
- **Merged, not closed:** W2-54, W2-62, W2-63, W2-50. core-schema RED on W2-53's close record until W2-02 merges
  (DEC-872). context-reproducibility RED only while the store lacks DEC-873 (next rebuild).
- **In flight (4):** W2-58 run 2 (DEC-873, `log/W2-58-A5-run2.json`); W2-48 run 2 (DEC-876,
  `log/W2-48-A5-run2.json`); W2-54 run 5 (DEC-874: fix the 4 cases contradicting W2-02's types;
  `log/W2-54-A5-run5.json`); W2-59 run 3 (DEC-877, 20:40, `log/W2-59-A5-run3.json`; last run: merge-back with
  trailers, CIT-P ids, verify, 2nd/last CIT-P review).
- **W2-59's branch remade by me under DEC-412 (DEC-877):** new head `d3e594bf` (same tree as old `3d6a27f8`),
  merge `e48a601d` trailered. Old kept as `w2/W2-59-old`: delete after run 3 verifies. After W2-59 merges the
  owner re-pins at the merge commit, then regenerates settings from `.rulesync/hooks.jsonc` (ping ACT then).
- **W2-02 waiting:** after W2-54 run 5 merges, W2-02 run 5 (re-merge, re-verify, probe, merge).
- **`.git/config.lock`** zero-byte read-only placeholder (16:06, likely a sandboxed worker): recheck, leave alone.

### Next
1. On each return: read the JSON `result` (`json.loads(t[t.index('{'):])['result']`); merge per prompt §3
   (`--no-ff`, Task/Role trailers, tree == merge-tree); checkpoint; sync.
2. Close queue after W2-02 merges: `bash tools/close_queue.sh DAEO-zflj DAEO-0rfi DAEO-juee DAEO-pl6k DAEO-kl5e`
   (+ W2-48 `DAEO-xxgp` after its merge). After each close: commit outputs, repair ticket -> `log/repair-tickets/`,
   sync, remove worktree + branch. Refused -> ping P1 (new or seen cause).
3. Later: W2-64 (W2-02's widening); re-measure a lead rebuild, raise parallelism; daily digest (records since last
   push, usage, refusal counts, memory-use counts).
4. Before each start: WBS/LIST/tk edits (DEC-825 item 7). Next free: ticket W2-65; rows W2-H063, W2-M395, W2-L382.
   Briefs: `tools/build_lead_brief.py <part> <out> ID= W2= PROFILE= PATHS= ROWS= SOURCES= IMPL= EST=`.

### Standing rules (short; the prompt holds the full text)
- Report: countdown first, its first line the progress line (DEC-878: tickets closed / merged-not-closed / built
  and held / in flight / not started of 57, W2-00 apart, each in its first state, in flight before merged;
  keystones done / in progress / ahead of 9), phone-readable, evidence, last line `OWNER_ACTION: <P1|P2|COMMIT|COMMIT-NEEDED|none>
  <ids> - <summary>`. Lead launch per prompt §4, gate in the same command, Bash background, timeout 7200000.
- Commits: trailers Task/Implements/Role/Co-Authored-By; `-- <paths>`; merges `--no-ff`, tree == merge-tree.
- Closes (DEC-780): quiet window; rebuild immediately before; fresh checkpoint; once only.
- Never: push/tag/rebase/main; amend w2/integrate; `gov approve`; `rebuild --no-embeddings`; tk close a W2 ticket;
  hooks; --no-verify; secrets/held-out contents; ~/gov-os-workbench; grow accepted_reds/load_sensitive; weaken a
  hard-block check; let the ratchet retry; `$VAR` write targets; heredocs/backticks in commands (DEC-409).

## Archive
The long history moved to `CHECKPOINT-ARCHIVE.md` beside this file (DEC-792, 2026-10-18).

<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-10-20T19:28:23Z 51f6c40af491bc5100727053169fe429e1d69750aa8709806ac0973d038361d0
git head: a90b27094339ed8f80facf9d94166429e2fe1fba
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0rfi [in_progress] - W2-54 The context packet's dropped list in a stable order; the context check's declared time limit; the audit-report type
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
  DAEO-xxgp [in_progress] - W2-48 Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run <- [DAEO-g0ip, DAEO-7rr2]
  DAEO-ym8a [in_progress] - W2-03 Decisions as records, each with its own hash <- [DAEO-g0ip, DAEO-zflj]
  DAEO-zflj [in_progress] - W2-02 Record types: decision entry, audit report, adoption verdict, close record; core-schema green here <- [DAEO-g0ip]
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  a90b2709 [w2/integrate]
  /home/usain/gov-os-worktrees/W2-02          4ce16df2 [w2/W2-02]
  /home/usain/gov-os-worktrees/W2-03          9a3e3456 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-05          f19f156e [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-16          1908149d [w2/W2-16]
  /home/usain/gov-os-worktrees/W2-20          1a54976c [w2/W2-20]
  /home/usain/gov-os-worktrees/W2-26          62c4e477 [w2/W2-26]
  /home/usain/gov-os-worktrees/W2-37          2ff873b2 [w2/W2-37]
  /home/usain/gov-os-worktrees/W2-48          d2035259 [w2/W2-48]
  /home/usain/gov-os-worktrees/W2-49          19d45246 [w2/W2-49]
  /home/usain/gov-os-worktrees/W2-50          b9a5e5cd [w2/W2-50]
  /home/usain/gov-os-worktrees/W2-51          c2c80e6c [w2/W2-51]
  /home/usain/gov-os-worktrees/W2-52          a21f06a7 [w2/W2-52]
  /home/usain/gov-os-worktrees/W2-54          40909d21 [w2/W2-54]
  /home/usain/gov-os-worktrees/W2-58          7bd32fd7 [w2/W2-58]
  /home/usain/gov-os-worktrees/W2-59          3d6a27f8 [w2/W2-59]
  /home/usain/gov-os-worktrees/W2-62          fbc6b706 [w2/W2-62]
  /home/usain/gov-os-worktrees/W2-63          ad38ed68 [w2/W2-63]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
