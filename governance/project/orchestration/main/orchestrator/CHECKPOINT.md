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
- **Questions (DEC-850):** all-blocking -> six-part package as my message, saved in `governance/project/
  orchestration/packages/<id>.md`, END THE TURN with "QUESTION FOR THE OWNER: <id> - choose (a), (b), (c) or
  Discuss first; my recommendation is (x)" then OWNER_ACTION. NEVER the AskUserQuestion box. Part-blocking ->
  report + digest, six parts. Leads/workers never ask the owner.
- **W2-48 (DEC-852):** subprocess code seen or such tests re-run; serves leads' runs; from its merge a NIGHTLY full
  uncached regression in a quiet window, result in the digest; fail-there-but-cached-pass = P1.
- **Effort (DEC-839):** Opus 5.5; `--effort high`; max auditors/FULL probes/owner packages; xhigh FULL test designer.
- **Also:** CAP-10 both figures (85 floor, 99 % target; DEC-833); recalibrate estimates after K2 (DEC-834);
  agents never push, the owner's daily backup push continues (DEC-848); rules about rules (DEC-851).
- **Policy 1 (DEC-819):** `python3 governance/project/orchestration/sync_context.py`, gitleaks on staged, commit
  `-- <paths>` with `Task: DAEO-sdxk`, `Role: orchestrator`; a session summary in `.../orchestration/sessions/`.
- **Policy 2 (DEC-820):** reads open except secrets, held-out contents, the counterpart's work, a hidden eval half.

### Where things stand
- **Staged batch (owner commits, `Role: owner`):** register §248 DEC-831..852 (v0.248, next DEC-853) + Changed-by
  notes; plan ACCEPTED; prompt v3; `LEAD-w2-common.md`; `AUDITOR-common.md`; W2-48 card + `.tickets/DAEO-xxgp.md`.
  A staged batch blocks `git merge`; DEC-788: committed before any close. Working memory: `a5798521`.
- **Pin proven:** gov -> `~/.local/share/gov-os/pin-fecb870c/bin/gov`; no system `gov`; window 1M. Rebuild 21 min
  (Wave 1: 2.5-3.5). `gov check` (12.6 min): 21 GREEN; YELLOW openspec-validate (not on PATH), core-decision-
  citations (warning); **RED secrets-indexing**: declared checks still run the tree's `src` (W2-59's gap), and
  gitleaks times out (60 s per file, ~24 in parallel) on `store.db` 250 MB and `code.db` 210 MB. Deterministic ->
  **every `gov close` would be refused.**
- **P1 P-W2-49 (part-blocking: all closes):** fix the scan's time limit/concurrency. W2-50's branch rewrites the same
  function. Options in the report; W2-50's resume waits for the answer. Never attempt a close known to fail.
- **P2 P-W2-48:** W2-59 overlaps W2-05's unmerged lines (`check/runner.py` `_run_command` env, `retrieve_check.py`).
  Rec (a) start now beside W2-05. W2-59 waits.
- **Notify:** test 1 (the box) did NOT reach the phone. Test 2 (end of turn, NOTIFY-TEST) open.
- **Close lock:** before a close, create `.gov-runtime/scratch/orchestrator/CLOSE-RUNNING`; leads hold; remove after.
- **Usage 22:1x:** session 1 %, week 17 % (resets Oct 25 09:00). Sampler running -> `log/lead-usage.jsonl`.

### Next
1. **W2-62 lead IN FLIGHT** since 22:29 (PID 3744202; worktree `~/gov-os-worktrees/W2-62` from `162f17ea`; brief
   `briefs/W2-62-A5-run1.md` built by `tools/build_lead_brief.py`; log `log/W2-62-A5-run1.json`). Hook-size facts
   given to it: SessionStart context arrives whole up to ~10,000 chars; at 12,000+ Claude Code saves it to a file
   and shows a preview only (measured 22:4x with random tokens). 1 lead in flight: fewer until W2-48, and the
   other candidates wait on P-W2-48 / P-W2-49 / the batch commit.
2. On the owner's commit + P-W2-49's answer: the secrets fix; then W2-53's close (rebuild immediately before, once),
   W2-54's close; W2-50's resume -> W2-58. On P-W2-48: W2-59.
3. Before each ticket starts: its WBS/LIST/tk edits (DEC-825 item 7). Next free: ticket W2-63; rows W2-H063,
   W2-M386, W2-L362; package P-W2-50.

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
