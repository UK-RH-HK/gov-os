# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-21 09:0x BST — W2-58 run 3 in flight, queue held for it; next free DEC-881)

### Standing owner rules (short; full text: register §248-§268, prompt v3.7; DEC-851)
- **Window (DEC-838):** full window (1M); no compaction threshold; never ask a session to stop early. Usage is the
  limit (`claude -p "/usage"` in the digest).
- **Checkpoint at every handover (DEC-837):** return, merge, package, compaction. Keep this section < 10,000 chars.
- **Memory used (DEC-836):** every brief says `gov retrieve`; from W2-04 briefs built with `gov context`; counted.
- **Large/code questions (DEC-859/860):** batches, ranked, stacked; code graph by traversal and pages.
- **Parallelism (DEC-847, DEC-880):** no fixed cap; measured gate (by hand: load1 < 20, MemAvailable >= 6710886 kB,
  in the launch command); owner's usage; never in a close's quiet window; ceiling 10; fewer until W2-66.
- **W2-58 ahead of everything (DEC-857, DEC-873, DEC-880).** Until it lands take read refusals, never another form;
  search named folders; count them for the digest.
- **Notify (DEC-855):** six-part package in my message + `governance/project/orchestration/packages/<id>.md`; start
  all independent work; LAST ACTION `~/.local/bin/owner-ping "<P1|P2|COMMIT|ACT> <id> | gates <...> | <need>"`.
  Never AskUserQuestion; no secret/key/held-out path/file content; leads never ping. Gates nothing -> digest.
  Owner (10-20): during the close queue, ping only if a close is refused, saying new or already-seen cause.
- **No test cache (DEC-880):** W2-48 withdrawn (testmon can't see `gov` subprocesses; 11.5 % reuse, 3 % saved).
  W2-66 = path-scoped regression at close: own suite + unit + suites of tickets whose allowed_paths overlap; FULL
  suite for shared core (close, guard, check, records, retrieval core, kernel hooks, path map), unplaced file or no
  map; lead's full verification unchanged; nightly full uncached run stays (a miss = P1 + map fix); W2-24/W2-46
  full. Target < ~15 min typical close, measured. W2-66 takes the next slot after W2-58's merge (DEC-869's place).
- **Progress line (DEC-878):** first line of every countdown: tickets closed / merged-not-closed / built and held /
  in flight / not started of 58 (57 - W2-48 withdrawn + W2-65 + W2-66; W2-00 apart; each in its first state, in
  flight before merged); keystones done / in progress / ahead of 9.
- **Effort (DEC-839):** opus-5-5; high; max auditors/FULL probes/packages; xhigh FULL designers.
- **I commit owner decision records (DEC-861):** `Task: decision-record`, `Role: orchestrator`, `Decided-by: owner
  (chat, <date>)`; never Role: owner; never push. Ratchet entries/escalation lifts stay Role: owner commits until
  W2-12 (DEC-862): prepare + ping ACT.
- **Supersession propagates (DEC-866):** mark at once, sweep by id and value, update or keep with a reason.
- **Pre-close gate (DEC-868):** collect-only in one process; gov check after rebuild; fresh ticket checkpoint;
  clean tree AS THE CLOSE READS IT (`tools/tree_diff.py`); trailers; `tools/close_queue.sh <id>[:DEC-n] ...` (commits
  each clean close's outputs). Record edits: `tools/record_checks.sh` first. No main-tree commits while it runs.
- **Policy 1 (DEC-819):** sync_context.py (skips self-ignoring folders), gitleaks staged, commit `-- <paths>`,
  Task: DAEO-sdxk.
- **Also:** CAP-10 both figures (DEC-833); recalibrate after K2 (DEC-834); owner's daily backup push (DEC-848).

### Where things stand (10-21 09:0x)
- **Owner pushed through `8dfd54e9`.** Records since: DEC-872 `4b6e5766`; DEC-873 `19357fcb`,`6e125150`; DEC-874
  `5f346750`; DEC-875 `8542a970`,`e6976ef3`; DEC-876 `65039414`; registry `b0756906`; DEC-877 `97fc656a`; DEC-878
  `172961fa`; DEC-879 `fcc82099`; DEC-880 `b772b2fe` (+ its follow-up commit: cards, tickets, prompt v3.7, brief).
- **Closed:** W2-01 (tk), W2-53 (gov close). Close success 1 of 9 runs (W2-02 refused 02:37, TREE_NOT_COMMITTED,
  cause mine and fixed: copied self-ignoring stores; sync + gate (d) fixed `c3b32d31`).
- **Merged, not closed:** W2-02 `94ac7951`, W2-54 `6855cdf3`, W2-62, W2-63, W2-50. core-schema GREEN on main.
- **Queue run 2 STOPPED by me at 08:2x** before any close (only its rebuild lost; checkpoint commit `bceec2e9`
  stays) to give W2-58 the machine (DEC-880 "ahead of everything"). Re-run after W2-58 merges, with W2-58 added:
  `bash tools/close_queue.sh DAEO-zflj DAEO-0rfi DAEO-juee DAEO-pl6k DAEO-kl5e DAEO-5j8b`.
- **In flight (1): W2-58 run 3** (DEC-880 item 1: `~` expansion on Read/Grep/Glob/Edit/Write/Bash + flagged pytest
  forms, full verification, 3rd review limited to the change), started 08:3x, `log/W2-58-A5-run3.json`.
- **W2-59 DONE, HELD (DEC-879):** head `1cad6aa0`, last review pass. Merge after the queue; then W2-65 (after W2-59,
  same hooks file); then ONE ACT ping: owner re-pins at W2-65's merge commit + regenerates settings.
- **W2-48 WITHDRAWN** (DEC-880): ticket closed by the owner's decision; branch `w2/W2-48` kept (`2c3c46b5`, research
  record on it); worktree to remove after a sync. 44 `/tmp/gov-testcache-*` leftovers.
- **New tickets:** W2-65 `DAEO-e82f` (LITE, hook lines exit 2 when the guard program can't run); W2-66 `DAEO-c1uz`
  (FULL, path-scoped regression). Cards in WBS §2.
- **Credentials (P-W2-58-3):** none in any tree by name; only two tracked fixtures
  (`fixtures/brownfield/project/.env`, `fixtures/brownfield/project/config/secrets.yaml`). Row W2-M398.
- **secrets-indexing false positive (row W2-M395):** raw SQLite bytes can spell a token by chance per rebuild. If a
  queue rebuild hits it, gate (b) stops the queue: bring a P1 package; never rebuild-until-green.
- **`.git/config.lock`** zero-byte read-only placeholder (recreated 20:34 10-20): leave alone; `git branch -D` worked.

### Next
1. On each return: read the JSON `result` (`json.loads(t[t.index('{'):])['result']`); merge per prompt §3
   (`--no-ff`, Task/Role trailers, tree == merge-tree); checkpoint; sync.
2. W2-58 DONE -> merge -> queue (six) -> merge W2-59 -> W2-65 -> ACT ping (re-pin + settings) -> W2-66 start.
3. Later: W2-64; held tickets' resumes by keystone; daily digest (records since push, usage, refusals, memory use).
4. Next free: ticket W2-67; rows W2-H063, W2-M399, W2-L401. Briefs: `tools/build_lead_brief.py <part> <out> ID= W2=
   PROFILE= PATHS= ROWS= SOURCES= IMPL= EST=`.

### Standing rules (short; the prompt holds the full text)
- Report: countdown first (progress line first), phone-readable, evidence, last line `OWNER_ACTION: <P1|P2|COMMIT|
  COMMIT-NEEDED|none> <ids> - <summary>`. Lead launch per prompt §4, gate in the same command, Bash background.
- Commits: trailers Task/Implements/Role/Co-Authored-By; `-- <paths>`; merges `--no-ff`, tree == merge-tree.
- Closes (DEC-780): quiet window; rebuild immediately before; fresh checkpoint; once only.
- Never: push/tag/rebase/main; amend w2/integrate; `gov approve`; `rebuild --no-embeddings`; tk close a W2 ticket
  without the owner's decision; hooks; --no-verify; secrets/held-out contents; ~/gov-os-workbench; grow
  accepted_reds/load_sensitive; weaken a hard-block check; let the ratchet retry; `$VAR` write targets (also in
  sed -i!); heredocs/backticks in commands (DEC-409).

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
