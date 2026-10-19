# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-19 ~23:00 — Wave 2 RESUMED by keystones; plan ACCEPTED with DEC-831..DEC-852 STAGED)

### Where things stand
- **Owner batch STAGED, not committed:** DEC-831..DEC-852 (register §248, v0.248, next free DEC-853; "Changed by"
  notes on DEC-062/140/460/726/737/776/786/792/828/829/830) + the plan ACCEPTED (`docs/plan/WAVE_2_REVISED_PLAN.md`)
  + prompt v3 + `LEAD-w2-common.md` + `AUDITOR-common.md` + W2-48's card (WBS) and ticket file `DAEO-xxgp`
  (DEC-843, DEC-852). The owner commits it (`Role: owner`). **A staged batch blocks `git merge`, and DEC-788 needs
  it committed before any close.**
- **NOTIFY-TEST open:** my turn ended with "QUESTION FOR THE OWNER: NOTIFY-TEST - did this reach your phone? (a) yes
  (b) no" (DEC-850's test). If (b), the owner adds a Notification hook.
- **The close lock (LEAD-w2-common, DEC-847/780):** before each close I create
  `.gov-runtime/scratch/orchestrator/CLOSE-RUNNING`; leads start no worker or suite batch while it exists; I remove
  it when the close ends.
- **The pin is proven** (session of 2026-10-19 evening): `~/.local/bin/gov` -> `~/.local/share/gov-os/pin-fecb870c/
  bin/gov`; system `python3 -c 'import gov'` -> ModuleNotFoundError; window "1m tokens (default for this model)".
  Full rebuild under the pin: exit 0, 21 min (Wave 1: 2.5-3.5 min; lexical 396 s; load ~32 from parallel gitleaks).
  `gov check` under the pin: see `log/pin-check-2026-10-19.json`.
- **Package P-W2-48 (P2, part-blocking, in the report):** W2-59 overlaps W2-05's unmerged `_run_command` env lines
  (`check/runner.py`, `retrieval/retrieve_check.py`). Rec (a): start W2-59 now on w2/integrate; W2-05's resume
  absorbs the overlap. Until answered, W2-59 waits; everything else goes on.
- **Notification test 1 (owner, 22:2x):** the AskUserQuestion box did NOT reach the owner's phone (answer "No").
  Hence DEC-850 item 1: never the box; end the turn with the QUESTION FOR THE OWNER line.
- **Next, in order:** owner commits the batch -> W2-53 close (quiet window, rebuild immediately before, once) ->
  W2-54 close. Leads now: W2-62 (resume in full, new, no overlap) and W2-50 (resume probe; frees W2-58). W2-58
  starts when W2-50 merges or stacked on it after its probe passes. Then the plan's WBS/LIST/tk edits ticket by
  ticket before each starts (DEC-825 item 7). Next free: ticket W2-63, rows W2-H063 / W2-M386 / W2-L362.
- **Usage (owner's subscription):** `claude -p "/usage"` at 22:1x: session 1 %, week 17 % (resets Oct 25 09:00).
- **Lead usage sampler running:** `tools/lead_usage.py log/lead-usage.jsonl 30`; summary with `--summary`.

### Standing owner rules of 2026-10-19 (short form; full text in the register and prompt v3, DEC-851)
- **Window (DEC-838):** every session on its model's full window (1M, Opus 5.5). Never set a compaction threshold;
  never ask a session to stop or compact early. Usage is the limit: digest reports daily/weekly use (`/usage`).
- **Checkpoint at every handover (DEC-837):** a worker's return, a merge, a package, a compaction. RESUME HERE holds
  the full session state (happening / decided / next / where); repository knowledge comes from retrieval and packets.
  DEC-792's 8,000-char limit is lifted once W2-62 lands (the hook then loads RESUME HERE in full).
- **Memory used (DEC-836):** every lead/worker brief tells its agent to use `gov retrieve`; from W2-04's merge I
  build every brief with `gov context` (until then, record each brief built without one); usage counted.
- **Parallelism (DEC-847):** no fixed cap. Start leads as eligible tickets (deps closed or DEC-786-stackable), the
  MEASURED gate (DEC-798's figures until measured: load1 < 20, MemAvailable >= 6710886 kB), the owner's usage
  limits, never during a close's quiet window, one writer per worktree, ceiling 10. Fewer until W2-48 lands. Every
  countdown: number in flight and why.
- **W2-58 first in keystone 3 (DEC-849).** Until it lands: take a read refusal, never another form, search named
  folders (never from the repo root, `governance/project/` or `.claude/`); count refusals in the digest (today: 1).
- **Questions (DEC-850):** all-blocking -> six-part package (DEC-818) as my message + saved under
  `governance/project/orchestration/packages/<id>.md`; END THE TURN with it, last lines: "QUESTION FOR THE OWNER:
  <id> - choose (a), (b), (c) or Discuss first; my recommendation is (x)" then OWNER_ACTION. NEVER the
  AskUserQuestion box (it does not notify the phone). Background work keeps going. Part-blocking -> report +
  digest, six parts, no question line. Leads/workers never ask the owner; leads return packages saying all/part.
- **W2-48 (DEC-852):** cache sees subprocess code or re-runs process-starting tests; serves leads' runs (same rules,
  `--no-cache`); from its merge, a NIGHTLY full uncached regression on w2/integrate's head in a quiet window, result
  in the next digest; a test failing there but passed via cache = P1 package. W2-24/W2-46 full runs stay.
- **Rules about rules (DEC-851):** each standing rule goes to the register, prompt v3, RESUME HERE, LEAD-w2-common,
  and JUDGEMENT/AUDITOR-common where it applies; each report names the places.
- **Backups (DEC-848):** agents never push; the owner's own backup push of w2/integrate continues, at least daily.
- **Effort per launch (DEC-839):** Opus 5.5 everywhere; `--effort high` (max: auditors, FULL probes, owner
  packages; xhigh trial: FULL test designers); subagents on the parent's model; agent teams off.
- **CAP-10 (DEC-833):** report both figures: hit@5 vs the floor 85, and complete stacked evidence vs the target 99 %.
- **Estimates (DEC-834):** recalibrate all after keystone 2 from measured ticket and close times.
- **POLICY 1 (DEC-819):** all context in git; at every checkpoint `python3 governance/project/orchestration/
  sync_context.py`, gitleaks on the staged set, commit with `Task: DAEO-sdxk`, `Role: orchestrator`, `-- <paths>`;
  a session summary under `governance/project/orchestration/sessions/` at each session end.
- **POLICY 2 (DEC-820, ADR-0001):** reads open; refused only (a) secrets, (b) held-out contents (names ok),
  (c) the counterpart's work on the same ticket, (d) the hidden half of an evaluation set. Writes: own ticket paths
  only.

### State (git is the truth; re-derive from git + `.tickets/` if this block is older)
- **Branch** `w2/integrate` at `70aea435` (owner's DEC-822 pin registry commit) + my working-memory commits of
  2026-10-19 evening. Before: `6a5d6b34` (handover), `b8571d9d` (owner batch DEC-813..830).
- **Countdown:** 1/55 closed (W2-01, by `tk close`). Merged not closed: W2-53, W2-54. Running 0. Idle 1 (W2-05).
  Held 10. Close success rate: 0 of 3 `gov close` runs clean (all W2-53). Wave 2 = 55 tickets + W2-00 (DEC-831).
- **W2-53's last re-close** (12:01, `log/close-DAEO-7rr2-3.json`) REFUSED on the W1-30 r13 case only; repair ticket
  DAEO-c6ir in `log/repair-tickets/`. Its next re-close is legitimate now (the load_sensitive change), once only.

### Held / idle tickets (heads)
- W2-02 `2a35fd7b` (resolve standalone-types to its line; fresh probe; + check-jsonschema widening). W2-03
  `9a3e3456`. W2-16 `1908149d`. W2-20 `1a54976c`. W2-26 `62c4e477`. W2-49 `19d45246`. W2-51 `c2c80e6c`
  (+ lens A F4). W2-50 `0affa162` (resume probe). W2-05 `f19f156e` (idle; F-A, P-1, W2-M281, DEC-805, lens G R7).
- W2-37 `2ff873b2` (on W2-03): resume per DEC-812 + DEC-815/816 + `codeintel/**` via `trace_path`. W2-52 `a21f06a7`
  (on W2-49): merge, DEC-814 regenerate, rebuild, all suites, probe. W2-54 `226ec458`: merged, close after W2-53.

### Open owner items
- **COMMIT:** the staged batch DEC-831..DEC-852 (above). **P2 P-W2-48** (W2-59 vs W2-05; rec (a)), saved at
  `governance/project/orchestration/packages/P-W2-48.md`. **NOTIFY-TEST** (a)/(b). DEC-822 step 2 (the hook lines)
  rides in W2-59. The path-map lines of DEC-845 (I give them when W2-58/W2-26 need them).

### Decision packages (DEC-818)
Every P1 package is self-contained: (1) context in plain words with history and links; (2) what happened, with
evidence; (3) why it matters to the Gov OS's purpose; (4) options with consequence, cost, risk and what each changes
in the Contract, specs, skills or briefs; (5) recommendation and confidence, threat-model class of any finding;
(6) what it blocks and what waiting costs. P2 items go into one daily digest.

### Judgement rules (w2 prompt §14; DEC-801..803, DEC-807..809)
- `governance/project/briefs/JUDGEMENT.md`: "Can an honest agent hit this in ordinary work?" "Does it fail open or
  lose work?" Only yes to both = a round; constructions = Wave 3 rows. Each finding: `Ordinary work: yes|no,
  because …`, `Consequence: fails open|loses work|other`. `briefs/AUDITOR-common.md` starts W2-25/28/30/47 briefs.

### Standing rules (short; the prompt and the register hold the full text)
- Every report: countdown first; phone-readable; evidence; last line exactly one
  `OWNER_ACTION: <P1|P2|COMMIT|COMMIT-NEEDED|none> <ids> - <summary>` naming every open owner item (DEC-787, DEC-788).
- Lead launch (DEC-715) as in the prompt; gate by hand in the same command: load1 < 20, MemAvailable >= 6710886 kB.
- Workers: `gov launch` sandboxed unless the suites need the code graph (old form + tripwire), DEC-799.
- Commits: `--trailer Task/Implements/Role: orchestrator/Co-Authored-By`, `-- <paths>` only; merges `--no-ff`, tree
  == `git merge-tree --write-tree HEAD^1 HEAD^2`. A staged batch blocks `git merge`.
- Closes (DEC-780): quiet window; rebuild IMMEDIATELY before (no commit between: STORE_STALE); fresh checkpoint;
  once only; a refused close's repair ticket -> `log/repair-tickets/`.
- Guard: no `$VAR` write targets; never type the settings or held-out paths; no glob/list over `governance/project/`.
- Never: push/tag/rebase/main; amend w2/integrate; `gov approve`; `rebuild --no-embeddings`; tk close a W2 ticket;
  lefthook install/uninstall; --no-verify; read ~/.claude/, workers' output, held-out/settings files; touch
  ~/gov-os-workbench or EXAMIN's real repo; edit a reviewed ticket's file on w2/integrate; grow accepted_reds/
  load_sensitive without the owner; weaken a hard-block check; let the ratchet retry; strip CLAUDE* from my close.

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
