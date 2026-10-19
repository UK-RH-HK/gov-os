# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-19 ~22:30 BST — Wave 2 RESUMED by keystones; DEC-831..DEC-852 STAGED for the owner)

### Standing owner rules of 2026-10-19 (short; full text: register §248, prompt v3; DEC-851)
- **Window (DEC-838):** full model window (1M); never set a compaction threshold; never ask a session to stop or
  compact early. Usage is the limit: digest gives daily/weekly allowance used (`~/.local/bin/claude -p "/usage"`).
- **Checkpoint at every handover (DEC-837):** worker return, merge, package, compaction. RESUME HERE = full session
  state (happening/decided/next/where); repo knowledge from retrieval. Keep it < 8,000 chars until W2-62 lands.
- **Memory used (DEC-836):** every lead/worker brief says use `gov retrieve`; from W2-04's merge every brief is built
  with `gov context` (until then record each one built without); count usage for the digest and K4's exit.
- **Parallelism (DEC-847):** no fixed cap; eligible tickets (deps closed / DEC-786 stack), the MEASURED gate
  (`tools/lead_usage.py`; until measured load1 < 20, MemAvailable >= 6710886 kB), the owner's usage, never in a
  close's quiet window, one writer per worktree, ceiling 10; fewer until W2-48. Countdown: number in flight + why.
- **W2-58 first in K3 (DEC-849).** Until it lands: take a refusal, never another form, search named folders (not
  the repo root, `governance/project/`, `.claude/`); count refusals for the digest (today: 3, incl. 2 DEC-409).
- **Notify the owner (DEC-855, replaces DEC-850's question line):** anything needing the owner (a decision gating
  ANY ticket, COMMIT-NEEDED, an owner act, LAUNCH_BLOCKED/ESCALATION/AUTH_REQUIRED): (a) six-part package in my
  message + `governance/project/orchestration/packages/<id>.md`; (b) start everything not depending on it; (c) LAST
  ACTION: `~/.local/bin/owner-ping "<P1|P2|COMMIT|ACT> <id> | gates <tickets|nothing> | <what I need>"` (a
  permission request: the only route that reaches the phone). Gates nothing -> daily digest. No secret, key,
  held-out path or file content in a ping. Never the AskUserQuestion box. Only I ping; leads/workers never.
- **W2-48 (DEC-852):** subprocess code seen or such tests re-run; serves leads' runs; from its merge a NIGHTLY full
  uncached regression in a quiet window, result in the digest; fail-there-but-cached-pass = P1.
- **Effort (DEC-839):** Opus 5.5; `--effort high`; max auditors/FULL probes/owner packages; xhigh FULL test designer.
- **Also:** CAP-10 both figures (85 floor, 99 % target; DEC-833); recalibrate estimates after K2 (DEC-834);
  agents never push, the owner's daily backup push continues (DEC-848); rules about rules (DEC-851).
- **Policy 1 (DEC-819):** `python3 governance/project/orchestration/sync_context.py`, gitleaks on staged, commit
  `-- <paths>` with `Task: DAEO-sdxk`, `Role: orchestrator`; a session summary in `.../orchestration/sessions/`.
- **Policy 2 (DEC-820):** reads open except secrets, held-out contents, the counterpart's work, a hidden eval half.

### Where things stand (23:15 BST)
- **Owner committed DEC-853..855 (`7f95e6f5`).** Pings DO reach the phone (DEC-858); my session can't see the request.
- **STAGED for the owner:** register §250 DEC-856..858 (v0.250, next DEC-859), `path-map.yaml` (P-W2-50 (a):
  `project-overlay` split into explicit patterns + new `orchestration-record` namespace, memory_class product;
  pinned `gov.check.pathmap` exit 0), WBS (W2-58 straight after W2-50, DEC-857), LIST (row W2-L362), prompt.
  A staged batch blocks `git merge`: COMMIT before any merge.
- **Leads:** W2-62 (td-1 running); W2-59 (since 22:58; its rebuild-1 on the OLD map); W2-50 run 8 waiting/starting.
- **Rebuild before:** 1,258 s (lexical 396, semantic ~55, code graph ~808); store 7,606 files / 56,999 chunks;
  code graph ~86k nodes / 182,113 edges. **After (23:10, mean load 32 beside W2-59's rebuild):** 443.7 s (lexical
  119, semantic ~66, code graph ~258); chunks 35,296 (record 90); code graph 28,923 nodes / 117,939 edges (still
  > 100k: tests); code.db 82 MB; store.db 241 MB (vectors unchanged). Clean figure: before W2-53's close.
- Leads' worktrees keep the old map until the owner commits and they merge `w2/integrate`; re-measure a lead's
  rebuild at the next start after the commit (W2-58), then raise parallelism.
- **Read restrictions:** no config-only way (constants in `src/gov/guard/heldout.py:19-21`, rule in
  `protected.py`); W2-58 straight after W2-50 merges, ahead of all (DEC-857). Read refusals today: 5. The owner
  authorised a Read-tool read of `path-map.yaml` for this edit only (it worked).
- **After the lighter rebuild:** re-measure one lead's rebuild; raise parallelism (DEC-847).
- **Pin proven:** gov -> `~/.local/share/gov-os/pin-fecb870c/bin/gov`; no system `gov`; window 1M. Rebuild 21 min
  (Wave 1: 2.5-3.5). `gov check` (12.6 min): 21 GREEN; YELLOW openspec-validate (not on PATH), core-decision-
  citations (warning); **RED secrets-indexing**: declared checks still run the tree's `src` (W2-59's gap), and
  gitleaks times out (60 s per file, ~24 in parallel) on `store.db` 250 MB and `code.db` 210 MB. Deterministic ->
  **every `gov close` would be refused.**
- Closes wait for W2-50's merge (the secrets fix). Never attempt a close known to fail. The re-pin after W2-59 must
  be at a commit holding W2-50's fix (DEC-853 item 4).
- **Close lock:** before a close, create `.gov-runtime/scratch/orchestrator/CLOSE-RUNNING`; leads hold; remove after.
- **Usage 22:1x:** session 1 %, week 17 % (resets Oct 25 09:00). Sampler running -> `log/lead-usage.jsonl`.

### Next
1. **W2-62 lead IN FLIGHT** since 22:29 (PID 3744202; worktree `~/gov-os-worktrees/W2-62` from `162f17ea`; brief
   `briefs/W2-62-A5-run1.md` built by `tools/build_lead_brief.py`; log `log/W2-62-A5-run1.json`). Hook-size facts
   given to it: SessionStart context arrives whole up to ~10,000 chars; at 12,000+ Claude Code saves it to a file
   and shows a preview only (measured 22:4x with random tokens). 1 lead in flight: fewer until W2-48, and the
   other candidates wait on P-W2-48 / P-W2-49 / the batch commit.
2. W2-50 merges -> W2-53's close (rebuild immediately before, once) -> W2-54's close -> W2-58 starts.
3. Before each ticket starts: its WBS/LIST/tk edits (DEC-825 item 7). Next free: ticket W2-63; rows W2-H063,
   W2-M386, W2-L362 (proposed in P-W2-50); package P-W2-51.

### State (git is the truth)
- Countdown: 1/55 closed (W2-01 by `tk close`). Merged not closed: W2-53, W2-54. Idle: W2-05. Held: W2-02 `2a35fd7b`,
  W2-03 `9a3e3456`, W2-16 `1908149d`, W2-20 `1a54976c`, W2-26 `62c4e477`, W2-37 `2ff873b2` (on W2-03), W2-49
  `19d45246`, W2-50 `0affa162` (resume: merge-back, re-verify, fresh probe under DEC-779/785), W2-51 `c2c80e6c`,
  W2-52 `a21f06a7` (on W2-49). Close success rate 0 of 3 `gov close` runs (W2-53).
- W2-53's last re-close (12:01) refused on the W1-30 r13 case only (now in `load_sensitive`); next re-close once.

### Standing rules (short; the prompt holds the full text)
- Report: countdown first, phone-readable, evidence, last line one `OWNER_ACTION: <P1|P2|COMMIT|COMMIT-NEEDED|none>
  <ids> - <summary>`. Lead launch per prompt v3 §4, gate in the same command. Workers via `gov launch` (DEC-799).
- Commits: trailers Task/Implements/Role/Co-Authored-By; `-- <paths>`; merges `--no-ff`, tree == merge-tree.
- Closes (DEC-780): quiet window; rebuild immediately before; fresh checkpoint; once only; repair -> `log/repair-tickets/`.
- Never: push/tag/rebase/main; amend; `gov approve`; `rebuild --no-embeddings`; tk close a W2 ticket; hooks;
  --no-verify; secrets/held-out contents; ~/gov-os-workbench; grow accepted_reds/load_sensitive; weaken a
  hard-block check; let the ratchet retry.

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
