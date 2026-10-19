# CHECKPOINT — W2 orchestrator (`orchestrator DAEO-sdxk`)

## RESUME HERE (2026-10-19 ~19:30 — Wave 2 PAUSED; handover to a fresh session; DEC-792 layout)

### WAVE 2 IS PAUSED until the owner approves the revised plan (DEC-829 item 6)
- Start no ticket, lead, worker; run no close; merge nothing. **Run no `gov` command until the owner says the
  handover is complete** (owner, 19:20: they are installing the pin and changing user-level settings).
- **Handover sequence (owner, 2026-10-19 ~19:20):**
  1. Commit the batch: **DONE** `b8571d9d` (DEC-813..DEC-830, `Role: owner`; register v0.247; next free DEC-831).
  2. Install the bootstrap pin (DEC-822 step 1): `.gov-runtime/scratch/orchestrator/pin/PIN-COMMANDS.sh` (wheel of
     `fecb870c`, sha256 `385fd5f0…f7bd`, venv `~/.local/share/gov-os/pin-fecb870c`, then `pin_registry.py`, then the
     owner commits `governance/project/tool-registry.yaml` with `Implements: DEC-822`). At 19:30 NOT yet done
     (`~/.local/bin/gov` was still the editable install's script).
  3. The owner changes user-level settings (lens F: compaction window, subagent model, agent teams). Never read
     `~/.claude/`; ask the owner what changed if it matters.
  4. This session closes; a fresh one starts here.
- **First thing in the fresh session (read-only, no `gov`):** `git log --oneline -5` (expect `b8571d9d`, my
  working-memory commit, and the owner's DEC-822 registry commit); `readlink -f ~/.local/bin/gov` (expect
  `…/pin-fecb870c/bin/gov`); `python3 -c 'import gov'` (expect ModuleNotFoundError); `git status --short`. Report
  what holds. If the pin is absent, say so: installing it is the owner's act, never mine. The pin does NOT yet cover
  the declared checks or the hook lines (they import the tree's `src`): that is W2-59, keystone 1.
- **The revised plan awaits the owner:** `docs/plan/WAVE_2_REVISED_PLAN.md` (PROPOSED; committed with my working
  memory; reported 19:15). 12 decisions in its §11: (1) approve the plan; (2) Contract re-baseline, 9 items to Wave 3,
  via W2-49 (rec (a) now); (3) CAP-10 keep 85; (4) withdraw DEC-062 and DEC-140; (5) lens F Table 3 + prompt v3,
  subagents on the parent's model, agent teams off, DEC-460's cause corrected; (6) defer the 8 Charter roles;
  (7) W2-59 scope; (8) W2-48's behaviour KPI + testmon/coverage package; (9) `docs/imported/` out of the schema
  check; (10) path map `experiments/**` + `evaluation_sets`; (11) owner acts (pin, held-out index check, lefthook
  measure, S0b2 leftovers); (12) cap 3 -> 4 after keystone 2.
- **After the owner's answers (in order):**
  1. The owner records them (DEC-831 onward, owner commit). I draft the entries only if asked.
  2. The plan's changes land before any ticket starts (DEC-825 item 7): WBS + LIST (moves to Wave 3 with reasons,
     the new cards W2-59/60/61, the widenings, row W2-M385 = doctor canary path / `gov --version` / gov-by-wheel),
     `tk` files for W2-55..W2-61, W2-27's ticket file, W2-19 cut; prompt v3 (owner edit: `--effort`, compaction
     via `--settings` env, A5 checkpoints at milestones, resume only via `gov launch --resume`); path-map edits
     (owner). Next free: ticket W2-62, rows W2-H063 / W2-M386 / W2-L362 (W2-M385 proposed in the plan).
  3. On the owner's word, resume by keystones (plan §3, §4): K1 W2-59 (lead) then the owner re-pins at its merge;
     K2 the close queue in DEC-806 order, each once, quiet window, rebuild immediately before: **W2-53 first**
     (P-W2-47 is settled by DEC-823 (a): the W1-30 r13 case is in `load_sensitive`, `b8571d9d`), W2-54, W2-02
     (resume), W2-03, W2-20, W2-51 (resume), W2-49, W2-16, W2-50 (resume), W2-05 (resume), W2-52 (resume), W2-37
     (resume), W2-26 (re-scope to `experiments/EXP-003/**`, after W2-07); with W2-57, W2-48, W2-07. Cap 3 (DEC-776)
     unless the owner raises it.
- **ASSESSMENT, done:** `docs/assessment/2026-10/` A-G + SYNTHESIS, committed `b8571d9d`; total $193.03 (F $12.15,
  G $26.82). Stats: `assessment_stats.py`.
- **POLICY 1 (DEC-819):** all context in git; at every checkpoint `python3 governance/project/orchestration/
  sync_context.py`, gitleaks on the staged set, commit with `Task: DAEO-sdxk`, `Role: orchestrator`; a session
  summary under `governance/project/orchestration/sessions/` at each session end. Never secrets, held-out material,
  stores, models, binaries.
- **POLICY 2 (DEC-820, ADR-0001):** reads open; refused only (a) secrets, (b) held-out contents (names ok),
  (c) the counterpart's work on the same ticket, (d) the hidden half of an evaluation set. Writes: own ticket paths
  only. The guard still enforces DEC-508/525/557 until W2-58: never route round it.

### State (git is the truth; re-derive from git + `.tickets/` if this block is older)
- **Branch** `w2/integrate` at `b8571d9d` (owner batch DEC-813..830) + my working-memory commit. Before: `fecb870c`
  versioned brief text; W2-54 merged `6f7d4f9e`; W2-53 merged `c9537e39`.
- **Countdown:** 1/55 closed (W2-01). Merged not closed: W2-53, W2-54. Running 0. Idle 1 (W2-05). Held 10. Not
  started 41. (With the plan approved: 53 W2 tickets + W2-00.)
- **W2-53's last re-close** (12:01, `log/close-DAEO-7rr2-3.json`) REFUSED on the W1-30 r13 case only; repair ticket
  DAEO-c6ir in `log/repair-tickets/`. Its next re-close is legitimate now (the load_sensitive change), once only.

### Held / idle tickets (heads)
- W2-02 `2a35fd7b` (resolve standalone-types to its line; fresh probe; + check-jsonschema widening). W2-03
  `9a3e3456`. W2-16 `1908149d`. W2-20 `1a54976c`. W2-26 `62c4e477`. W2-49 `19d45246`. W2-51 `c2c80e6c`
  (+ lens A F4). W2-50 `0affa162` (resume probe). W2-05 `f19f156e` (idle; F-A, P-1, W2-M281, DEC-805, lens G R7).
- W2-37 `2ff873b2` (on W2-03): resume per DEC-812 + DEC-815/816 + `codeintel/**` via `trace_path`. W2-52 `a21f06a7`
  (on W2-49): merge, DEC-814 regenerate, rebuild, all suites, probe. W2-54 `226ec458`: merged, close after W2-53.

### Open owner items
- **The revised plan's 12 decisions** (above). **The bootstrap pin** (step 2, the owner's act).

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
