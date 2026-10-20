# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-20 00:20 BST — Wave 2 running by keystones; 3 leads; DEC-859..860 STAGED)

### Standing owner rules (short; full text: register §248-§251, prompt v3.2; DEC-851)
- **Window (DEC-838):** full model window (1M); never a compaction threshold; never ask a session to stop or
  compact early. Usage is the limit: the digest gives daily/weekly allowance used (`claude -p "/usage"`).
- **Checkpoint at every handover (DEC-837):** return, merge, package, compaction. RESUME HERE = full session
  state; repo knowledge from retrieval. W2-62 merged: the hook now names this section's lines and size; DEC-792's
  8,000-char limit is lifted, but keep it tight (the hook injects it whole only up to 10,000 chars).
- **Memory used (DEC-836):** every brief says `gov retrieve`; from W2-04's merge every brief built with
  `gov context`; usage counted for the digest and K4's exit.
- **Large and code questions (DEC-859, DEC-860):** never one giant query or context: batches (`--batch-size`,
  `--continue`), ranked, stacked within budget. Code questions: the tool's `trace_path`/`search_graph`/`query_graph`,
  small; whole-graph jobs in pages, never a query over the cap; split by module on large repos.
- **Parallelism (DEC-847):** no fixed cap: eligible tickets, the MEASURED gate (`tools/lead_usage.py`; until
  measured load1 < 20, MemAvailable >= 6710886 kB), the owner's usage, never in a close's quiet window, one writer
  per worktree, ceiling 10; fewer until W2-48. Countdown: number in flight + why.
- **Read refusals until W2-58 (DEC-849, DEC-857):** take them, never another form, search named folders; count
  them (2026-10-19: 5). No config-only fix (constants `src/gov/guard/heldout.py:19-21`). W2-58 starts straight
  after W2-50 merges, ahead of all.
- **Notify (DEC-855, DEC-858):** anything needing the owner (a decision gating ANY ticket, COMMIT-NEEDED, an owner
  act, LAUNCH_BLOCKED/ESCALATION/AUTH_REQUIRED): six-part package in my message + `governance/project/orchestration/
  packages/<id>.md`; start all independent work; LAST ACTION `~/.local/bin/owner-ping "<P1|P2|COMMIT|ACT> <id> |
  gates <tickets|nothing> | <need>"`. It reaches the phone; my session can't see the request. Gates nothing ->
  digest. No secret/key/held-out path/file content in a ping. Never the AskUserQuestion box. Leads never ping.
- **W2-48 (DEC-852):** subprocess code seen; serves leads' runs; from its merge a nightly full uncached run.
- **Effort (DEC-839):** Opus 5.5; `--effort high`; max auditors/FULL probes/owner packages; xhigh FULL designers.
- **Also:** CAP-10 both figures (85 floor, 99 % target; DEC-833); recalibrate after K2 (DEC-834); the owner's daily
  backup push (DEC-848); every standing rule to register/prompt/RESUME/lead brief/cards (DEC-851).
- **I commit the owner's decision records (DEC-861):** as soon as written, with the files they govern, trailers
  `Task: decision-record`, `Role: orchestrator`, `Decided-by: owner (chat, <date>)`; never `Role: owner`; never push
  (the owner's push = acceptance); nothing left staged. Digest lists every record since the owner's last push (DEC,
  one line, sha). Exception until W2-12 (DEC-862): ratchet entries and escalation lifts stay the owner's Role: owner
  commits: prepare ready to commit + operator commands, ping ACT. Never read Decided-by alone (fails open).
- **Policy 1 (DEC-819):** `python3 governance/project/orchestration/sync_context.py`, gitleaks on staged, commit
  `-- <paths>`, `Task: DAEO-sdxk`, `Role: orchestrator`. **Policy 2 (DEC-820):** reads open but four.

### Where things stand
- **Owner pushed through `f0680605`.** I committed DEC-861 + DEC-862 (P-W2-51 (a) now, (b) in W2-12's card and
  ticket `DAEO-j8gn`, (c) never) as my first decision records (register §252, v0.252, next DEC-863). **Records
  since the owner's last push:** DEC-861, DEC-862 (shas in the digest). W2-37's ticket file: its lead at resume.
- **W2-62 returned PACKAGES (01:0x), work green, probe pass; MERGED `6e4b2750`;** DEC-863 (delegated) applied:
  skill copies regenerated + roster `prompt:` (`d4096dde`), record `d0cd2167`. Re-verify in main tree running
  (`tools/reverify_w2_62.sh` -> `log/reverify-W2-62/`). Close W2-62 later (quiet window; W1-49 reds first).
- **P1 P-W2-52 (open):** W1-49's two tests require DEC-636's 300k window, retired by DEC-838 -> every close red.
  Rec (a): new LITE ticket W2-63 (test designer revises them, Rewrite-Reason: DEC-838) before W2-53's re-close.
- **Leads:** W2-59 verifying (rebuild-2); W2-50 run 8 verifying (fix `a403309e`). Neither has `ccf28d5c`.
- **Merge `w2/integrate` into a lead's branch only at its return** (a commit under a running lead trips its stop
  rule; under a worker, containment, DEC-254). Then re-measure that lead's rebuild under the new map; then raise
  parallelism.
- **Rebuild (main tree):** before 1,258 s (lexical 396, semantic ~55, code graph ~808); after 443.7 s (119 / ~66 /
  ~258, mean load 32). Chunks 56,999 -> 35,296; code graph 86k/182,113 -> 28,923 nodes/117,939 edges (> 100k cap:
  tests); code.db 200 -> 82 MB; store.db 241 MB. A clean figure before W2-53's close.
- **secrets-indexing RED** until W2-50's fix merges (timeouts on the 241 MB store). Never attempt a close known to
  fail. Re-pin after W2-59 at a commit holding W2-50's fix (DEC-853 item 4).
- **Close lock:** create `.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` before a close; remove after.

### Next
1. On each lead's return: read the last JSON `result`; merge per the prompt; W2-62 DONE -> merge into
   `w2/integrate` (needs nothing staged: ask COMMIT first). W2-50 merges -> W2-53's close, W2-54's close, W2-58.
2. Before each start: its WBS/LIST/tk edits (DEC-825 item 7). Next free: ticket W2-63; rows W2-H063, W2-M386,
   W2-L363; package P-W2-51. Briefs: `tools/build_lead_brief.py <part> <out> ID=… W2=… …`.

### State (git is the truth)
- 1/55 closed (W2-01 by `tk close`). Merged not closed: W2-53, W2-54. In flight: W2-62, W2-59, W2-50. Idle: W2-05.
  Held: W2-02 `2a35fd7b`, W2-03 `9a3e3456`, W2-16 `1908149d`, W2-20 `1a54976c`, W2-26 `62c4e477`, W2-37 `2ff873b2`,
  W2-49 `19d45246`, W2-51 `c2c80e6c`, W2-52 `a21f06a7`. Close success 0 of 3.

### Standing rules (short; the prompt holds the full text)
- Report: countdown first, phone-readable, evidence, last line one `OWNER_ACTION: <P1|P2|COMMIT|COMMIT-NEEDED|none>
  <ids> - <summary>`. Lead launch per prompt v3 §4, gate in the same command. Workers via `gov launch` (DEC-799).
- Commits: trailers Task/Implements/Role/Co-Authored-By; `-- <paths>`; merges `--no-ff`, tree == merge-tree.
- Closes (DEC-780): quiet window; rebuild immediately before; fresh checkpoint; once only; repair -> `log/repair-tickets/`.
- Never: push/tag/rebase/main; amend; `gov approve`; `rebuild --no-embeddings`; tk close a W2 ticket; hooks;
  --no-verify; secrets/held-out contents; ~/gov-os-workbench; grow accepted_reds/load_sensitive; weaken a
  hard-block check; let the ratchet retry; `$VAR` write targets.

## Archive
The long history moved to `CHECKPOINT-ARCHIVE.md` beside this file (DEC-792, 2026-10-18).

<!-- GENERATED STATE BLOCK BEGIN -->
generated: 2026-10-19T18:14:10Z 9163145d32e1c3de978a03b7ca71d55ad22f8bf1390db198672df5a271ded6a8
git head: fecb870c9fde976fe18c993bd3ccb80426208de9
tickets in progress (`tk ls --status=in_progress`):
  DAEO-0rfi [in_progress] - W2-54 The context packet's dropped list in a stable order; the context check's declared time limit; the audit-report type
  DAEO-0z8c [in_progress] - W2-05 The git environment of every check, hook and helper; the settings re-sort <- [DAEO-g0ip]
  DAEO-2ds6 [in_progress] - W2-26 EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)
  DAEO-49o5 [in_progress] - W2-16 Immutable, hash-pinned releases (CAP-43.b lite) <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-6n5k [in_progress] - W2-37 gov impact <- [DAEO-g0ip, DAEO-ym8a]
  DAEO-7rr2 [in_progress] - W2-53 The probe gate measures every later merge against git's own merge of its parents <- [DAEO-g0ip]
  DAEO-egsy [in_progress] - W2-51 The Wave 2 plan validator <- [DAEO-g0ip]
  DAEO-ha8z [in_progress] - W2-49 Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P) <- [DAEO-g0ip, DAEO-egsy]
  DAEO-kl5e [in_progress] - W2-50 The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P) <- [DAEO-g0ip]
  DAEO-r30l [in_progress] - W2-20 Machine-wide resource gate <- [DAEO-g0ip]
  DAEO-siiz [in_progress] - W2-52 The lite A7 and A10 stage records <- [DAEO-g0ip, DAEO-ha8z]
  DAEO-ym8a [in_progress] - W2-03 Decisions as records, each with its own hash <- [DAEO-g0ip, DAEO-zflj]
  DAEO-zflj [in_progress] - W2-02 Record types: decision entry, audit report, adoption verdict, close record; core-schema green here <- [DAEO-g0ip]
worktrees (`git worktree list`):
  /home/usain/Dynamic-Agentic-Engineering-OS  fecb870c [w2/integrate]
  /home/usain/gov-os-worktrees/W2-02          2a35fd7b [w2/W2-02]
  /home/usain/gov-os-worktrees/W2-03          9a3e3456 [w2/W2-03]
  /home/usain/gov-os-worktrees/W2-05          f19f156e [w2/W2-05]
  /home/usain/gov-os-worktrees/W2-16          1908149d [w2/W2-16]
  /home/usain/gov-os-worktrees/W2-20          1a54976c [w2/W2-20]
  /home/usain/gov-os-worktrees/W2-26          62c4e477 [w2/W2-26]
  /home/usain/gov-os-worktrees/W2-37          2ff873b2 [w2/W2-37]
  /home/usain/gov-os-worktrees/W2-49          19d45246 [w2/W2-49]
  /home/usain/gov-os-worktrees/W2-50          0affa162 [w2/W2-50]
  /home/usain/gov-os-worktrees/W2-51          c2c80e6c [w2/W2-51]
  /home/usain/gov-os-worktrees/W2-52          a21f06a7 [w2/W2-52]
  /home/usain/gov-os-worktrees/W2-53          4f3d3405 [w2/W2-53]
  /home/usain/gov-os-worktrees/W2-54          226ec458 [w2/W2-54]
pending owner decisions: not known to the hook; see the written part of this checkpoint
<!-- GENERATED STATE BLOCK END -->
