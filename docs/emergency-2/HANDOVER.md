# Emergency 2: handover (facts only)

Written 2026-11-16 22:09 by the Gov OS CTO session acd80751, after the switch-off job (JOB-20261116-18, 22:08). Facts and
paths only; no proposals. `w2/integrate` at bb61d3d74 (the switch-off commit), clean; tag `pre-emergency-2` at b0631a61e,
pushed by the owner with w2/integrate 45444531e..b0631a61e.

## 1. Open tickets (Gov OS, .tickets/)
| Ticket | Status | Step reached | Branch / worktree | Uncommitted |
|---|---|---|---|---|
| W2-145 DAEO-2tfd | in_progress | merged; close waits (re-pin plus a day, S7) | w2/W2-145; ~/gov-os-worktrees/W2-145 (head 1be3e47de), W2-145-tests (aadce89d6) | 0 / 0 |
| W2-155 DAEO-ar89 | in_progress | merged; closes after W2-145 | w2/W2-155; W2-155 (8da607e3d) | 0 |
| W2-81 DAEO-l78m | in_progress | reopened for the 0.1.1 re-run (DEC-1202); 5 of 6 adopters at ADOPTION STOPPED, secret-history before its test designer; JOB-13 (read step) not run | w2/W2-81; W2-81 (e64ef21ea) | 0 |
| W2-156 DAEO-ylsh | in_progress | build done (50505b081, 5e7fb0572); stopped by the emergency watch 17:48 as its auditor started | w2/W2-156; W2-156 (5e7fb0572); W2-156-tests: empty folder, not a worktree | 0 |
| W2-186 DAEO-sq3a | in_progress | build and TD batch 2 merged (c5c66e6e8); stopped 18:50 as its auditor started | w2/W2-186; W2-186 (c5c66e6e8), W2-186-tests (2056da17c) | 0 / 0 |
| W2-191 DAEO-v6pf | in_progress | round 1's fixes and two TD cases merged (a1cdb91f7); stopped 18:05 as review round 2 started | w2/W2-191; W2-191 (a1cdb91f7) | 0 |
| W2-192 DAEO-mpq2 | in_progress | build done, gov accept 30/30; returned PACKAGES 18:24 (a path case: two helpers run A3 after A2, 65 reds; the kernel CIT-P for the owner) | w2/W2-192; W2-192 (62a038daa) | 0 |
| W2-195 DAEO-d8df | in_progress | build done, 45/45 at 8ec12d149; CIT-P committed (67a36b9e4); returned PACKAGES 19:26 (lead_verify 173 reds elsewhere, one product defect outside its paths); review not started | w2/W2-195; W2-195 (67a36b9e4) | 0 |
| W2-82 DAEO-4k3l | open | not started | — | — |
| W2-193 DAEO-7jln | open | filed (DEC-1203); waits for W2-191 to land | — | — |
| W2-194 DAEO-kq8b | open | filed (DEC-1203), keeps F-031 (DEC-1206) | — | — |
| W2-46 DAEO-nn1s | open | Wave 2 exit run; points at W2-81's re-run (DEC-1202) | — | — |
| W2-47 DAEO-jip3 | open | Wave 2 exit audit | — | — |
| W2-15b DAEO-swdu | open | measure lines amended by DEC-1210 A11 | — | — |
| W2-00 DAEO-sdxk | open | the CTO's coordination record | main tree | 0 |
Counts (status_block.py, 18:35): 170 closed, 2 merged not closed, 6 in flight, 7 not started, of 185; 10 moved to Wave 3, 4 to EXAMIN's Wave 0. W2-196 (DAEO-z3ss) withdrawn and removed (DEC-1209).

**EXAMIN clone** /home/usain/gov-os-runs/W2-27/examin: branch `wave0/schema-contract-and-disclosure-fix`, head ed08f69 (Wave 0 step 2 part 2, 16:45), 0 uncommitted; open tk tickets exa-cccg, exa-g6db, exa-qu2x, exa-rlmz (in_progress); its CTO runs interactive in tmux `examin-cto` (Remote Control "EXAMIN CTO"), told of DEC-1209 (no ticket loop).

**W2-81 run repositories** /home/usain/gov-os-runs/W2-81/run-0.1.1/repos/ (all 0 uncommitted; each has 4 in_progress tickets):
legacy-docs aaf71b9, python-app c9ee3c8, python-app-clean f0d13b3, rust-workspace 66c4b01, typescript-monorepo 628051c: handoff written, "ADOPTION STOPPED"; secret-history f5c3c8e: no handoff, stopped before its closing ticket's test designer. Each has a `<name>-tests` worktree.

## 2. Leads and workers
- **Running now:** the CTO session (pid 4067946, tmux `cto`) and the sentinel (pid 623044, tmux `cto-sentinel`, haiku). The EXAMIN CTO session in tmux `examin-cto`. No lead, worker or adopter runs.
- **Stopped by the emergency watch** (log/emergency-stop.log): W2-156 lead 17:48 (auditor au-1), W2-191 lead 18:05 (au-2), W2-186 lead 18:50 (au-1-2); **ended by themselves:** W2-192 18:24, W2-195 19:26.
- **Adopter sessions** (tools/adopter.sh status): all idle: examin-cto (first registration), w281-* (6, the 0.1.0 run), w281r-* (6, the 0.1.1 re-run).

## 3. Jobs and ACTs
**Jobs** (~/gov-os-operator/queue/jobs/, interim queue since DEC-1199 (3)):
| Job | What | State |
|---|---|---|
| JOB-20261116-01 | exa-g6db acceptance_tests.path | done (b17cd5a) |
| JOB-20261116-02 | W2-15a's walled run, hidden half | done (every mode MISS) |
| JOB-20261116-03 | exa-g6db kit copy path | done |
| JOB-20261116-05 | EXAMIN APP's trial data census and copy | done (3,243 copied, 0 withheld) |
| JOB-20261116-11 | W2-81 re-run build (seed 1324021) | done |
| JOB-20261116-12 | W2-81 re-run set-up of six repositories | done |
| JOB-20261116-13 | W2-81 re-run read step | not run |
| JOB-20261116-14 | W2-15a gap diagnosis, ids and counts | done |
| JOB-20261116-15 | the first fresh 80 | ran 19:24-19:38; stopped at the visible half's preflight (PF-SPREAD: plan area 1; PF-DRAWN: q24); no figure |
| JOB-20261116-16 | cleanupPeriodDays 365 | done 19:32 |
| JOB-20261116-17 | the first fresh 80, second attempt (retry route; audits memory-audit-26111603/04) | queued, not run |
| JOB-20261116-18 | Emergency 2: the guard and the prompts switched off | done 22:08 (exit 0; commit bb61d3d74) |

**ACTs** (bundles in .gov-runtime/scratch/orchestrator/acts/; 49 bundles excluding round copies): applied this week by the operator agent: ACT-GUARD-FIX-7 (a35d0edd6, 11-16), ACT-GOLDEN-RULE-1 (8bdb3ab35), ACT-GUARD-FIX-8 (7d6c2b5a5, 19:21), and earlier ACT-GUARD-FIX-6 (fa6135903, 11-15), ACT-CLAUDE-COPIES-2,3,7-12, ACT-CLAUDE-RULES-1, ACT-DEADMAN-STANDBY-1, ACT-DEADMAN-WAKE-1, ACT-LEADS-ADD-DIR-1, ACT-NIGHTLY-RESTART-1; by the owner's hand: ACT-DEADMAN-INBOX-1, ACT-W1-01-EXEMPT-3; others recorded applied in decision commits: ACT-EXAMIN-WRITERS-INSTALL-1, ACT-P95-1, ACT-PATHMAP-NS-2, ACT-IDLE-GUARD-1. **ACT-GUARD-FIX-9** (manifest 8f9cfcf0, the owner's yes): applied at 19:31 and **undone** by the operator: all six checks passed, but two files appeared during its apply window (`docs/audit/emergency-2026-11.zip`, `docs/audit/emergency-2026-11 (2).zip`, gone since); **the operator's lock is held** since 19:31 (`~/gov-os-operator/log/operator.lock`): nothing else applies until the owner removes it. **ACT-BOX-LAUNCH-1** (d7ed6246, the owner's yes): never queued; dequeued plan stopped by Emergency 2. Not applied, never queued or superseded: 23 other bundles (e.g. ACT-GUARD-FIX-5, ACT-PERMISSIONS-3, ACT-OPERATOR-HOURS-1/2/3 drafts, ACT-WALLS-REANCHOR-1, ACT-EFFORT-HIGH-1/2, ACT-DISPATCH-1). No .req is in the queue. Operator queue: 23 done entries 11-10..11-16.

## 4. Cron entries and registered hooks (before the switch-off)
**crontab** (active lines):
- `* * * * * run_tick.sh` — one dispatcher pass a minute (starts leads from ready.txt, returns, inbox items).
- `0 4 * * * nightly_restart.sh` — the nightly suite in its wrapper (quiet, one run, a memory cap).
- `0 8 * * * nightly_check.sh` — the morning check that last night's nightly ran.
- `*/10 * * * * operator_launch.py` — the operator agent's launcher (takes queue/*.req; walled session; gates G1-G9).
- Commented out (DEC-1049/1050): the old nightly_cron.sh, the @reboot check, runs_sweep.sh.

**Hooks** (repo `.claude/settings.json`, tracked; each runs through the pinned gov's interpreter):
- PreToolUse [*] → `.claude/hooks/pretooluse.py`: the guard (refuses per its rules; fails closed on a crash).
- PostToolUse [Bash] → kernel `context_watch.py`: a once-per-window reminder near the context's end.
- PreCompact → kernel `precompact.py`: a checkpoint record and the state block before compaction.
- SessionStart [compact|clear|resume] → kernel `sessionstart.py`: the resume injection and the context packet (gov context).
- Stop → kernel `stop.py`: a checkpoint record at each stop.
- SubagentStop → kernel `subagentstop.py`: blocks a worker return missing any of the 12 fields.
(repo `.claude/settings.local.json`, untracked, main tree only):
- PermissionRequest → `permission_request.py`: the quiet-hours net (refuses prompts 02:00-07:30, DEC-991).
- Stop → `stop_waiter_check.py`: the CTO's turn does not end with its inbox waiter unarmed (DEC-1027 E).
- Stop → `stop_idle_check.py`: the CTO's turn does not end idle while a ticket is launchable (DEC-1110 (1)).
(user `~/.claude/settings.json`): no hooks; defaultMode acceptEdits; allow Bash(*), Read(*), Edit(*), Write(*), WebFetch(*), WebSearch(*); ask: owner-ping (4 forms); cleanupPeriodDays 365.
**Permission denies:** repo settings.json: `Bash(sudo:*)`, Edit of *.key, *.pem, .env*, config/secrets*, Read of the qualification-oracle folder; settings.local.json: `Bash(git push *)` and Read of three evaluation-set folders; 42 allow lines.
**After the switch-off (JOB-20261116-18, run by the owner's operator 22:08:23, exit 0; commit bb61d3d74; every before and
after in `.gov-runtime/scratch/orchestrator/drafts/emergency-2-switch-off/applied/` with MANIFEST.json; `applied/revert.sh`
restores all nine files byte for byte):**
- `~/.claude/settings.json` (c9a35282d81e -> 6250ff64bcd3): `defaultMode` bypassPermissions; `skipDangerousModePermissionPrompt`
  true; the ask list removed; deny = `Bash(git push:*)`, `Bash(git push *)`, `Bash(sudo:*)`, `Bash(sudo *)` only; no hooks;
  cleanupPeriodDays 365.
- repo `.claude/settings.json` (2a319ea4284a -> 7dc2c0521d4d): PreToolUse (the guard) removed; deny list empty. Hooks
  registered now: PostToolUse (context_watch.py), PreCompact (precompact.py), SessionStart (sessionstart.py), Stop
  (stop.py), SubagentStop (subagentstop.py). `.claude/hooks/pretooluse.py` stays on disk, unregistered (live bytes
  cf82617d57a3, ACT-GUARD-FIX-8's after).
- repo `.claude/settings.local.json` (217706284c17 -> 8feb294cf01c): no hooks (PermissionRequest and the two Stop hooks
  removed); deny list empty.
- `template/governance/kernel/hooks/sessionstart.py` (db9668f5261f -> f29c0d3e396e): no `gov context` packet; the checkpoint
  injection and `tk ready` stay.
- `template/governance/kernel/templates/role-lead.md` and `.claude/templates/role-lead.md` (c731503e7f64 -> e9fd5af397ad):
  workers' briefs by `gov brief <role> {ID}`, no `gov context`. `governance/project/facts.yaml` (a85100017a1d ->
  1ef666f503c5): `context_ceiling` off.
- `governance/project/orchestration/tools/dispatch/launch_now.sh` (54345463a67b -> ba642544b03c) and
  `.gov-runtime/scratch/orchestrator/tools/adopter.sh` (b50519992410 -> d8c46dbc2685): leads and adopters start with
  bypassPermissions.
- **Not changed (only a code change in the pin can):** the pinned `gov launch` (0.1.1) refuses a worker launch whose
  repository settings do not register the guard (`src/gov/launch/launcher.py:371-413`, also checked for a lead at :1054),
  refuses bypassPermissions for workers (:440) and always writes the sandbox block into a worker's settings (:279-284):
  after the switch-off every `gov launch` of a worker is refused.
- Unchanged and running: the four crontab lines above (dispatcher, nightly, morning check, operator launcher), land.py and
  the merge queue, heavy_slot.sh and mem_guard, the spend brake (W2-156's, on its branch, not merged), the sentinel
  (tmux `cto-sentinel`) and the dead-man. Running sessions keep their settings until their next start.
- The operator's lock (`~/gov-os-operator/log/operator.lock`, 19:31) is still held: the operator applies no ACT until the
  owner removes it; jobs run through the owner's operator chat as before.


## 5. Where the rules live (sizes)
| Place | Size |
|---|---|
| Memory index `~/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/memory/MEMORY.md` | 20,225 B, 107 lines; the folder 108 files, 170,911 B |
| `.gov-runtime/scratch/orchestrator/CHECKPOINT.md` | 339,120 B, 1,866 lines |
| `governance/project/orchestration/START-NEXT-SESSION.md` | 12,822 B, 140 lines (last changed 11-13) |
| `governance/project/orchestration/DECISIONS-IN-FORCE.md` | 91,951 B, 756 lines (last changed 11-16) |
| `docs/DECISION_REGISTER.md` | 2,152,085 B, 15,612 lines (DEC-1210 the last) |
| `governance/project/orchestration/packages/DECIDED-NOT-DONE.md` | 128,619 B, 454 lines |
| Prompts `governance/project/prompts/` (w1-orchestrator.md, w2-orchestrator.md 82,502 B / 369 lines) | 2 files, 98,512 B |
| `CLAUDE.md` / `AGENTS.md` (golden rule section since 8bdb3ab35) | 5,265 B / 5,445 B |
| `.rulesync/` (the source of CLAUDE.md, AGENTS.md, generated agents and skills) | 93 files, 635,888 B |
| Brief and role templates `.claude/templates/` (brief.md, role-cto, role-engineer, role-lead, role-product-spec, role-research, role-reviewer, role-test-designer) | 8 files, 25,438 B |
| Kernel templates `template/governance/kernel/templates/` | 22 files, 43,252 B |
| Kernel role files `template/governance/kernel/roles/` (engineer, independent-auditor, independent-test-designer, orchestrator, product-spec, qa-engineer, research, senior-engineer, ticket-lead) | 9 files, 38,277 B |
| Kernel skills `template/governance/kernel/skills/` (adopt, api, audit, backend, change, checkpoint, data, devops, discovery, frontend, orchestration, planning, qa-review, retrieval, security, spec-writing, superpowers, test-design, ui-ux) | 70 files, 387,916 B |
| Generated `.claude/skills/` / `.claude/agents/` | 75 files, 479,032 B / 9 files, 57,950 B |
| Lead briefs `.gov-runtime/scratch/orchestrator/briefs/` | 1,741 files |
| The provisional rubric `governance/project/orchestration/packages/PROVISIONAL-RUBRIC.md`; the golden rule DEC-1204 and `packages/judging-work.SKILL.md` | — |

## 6. Pin and release, and what is known to break
- **Pin:** `~/.local/bin/gov` → `~/.local/share/gov-os/pin-2becaacdc2fb/bin/gov`, `gov 0.1.1`; release tag `v0.1.1`, record commit 45444531e (11-16 12:40); ten pins installed under ~/.local/share/gov-os/ (pin-076cded14882 … pin-fecb870c).
- **Known to break in 0.1.1** (sources: drafts/w2-27-findings/PRODUCT-FINDINGS.md; the W2-81 adopters' FINDINGS.md; the emergency's reports):
  - gov close in an adopted repository: base reds counted as the change's; accepted_reds not applied under `close: scoped` (F-028, F-030, F-031; W2-193, W2-194).
  - gov adopt's stage commits carry no Role:/Task: trailers, so an adoption ticket's F1 cannot pass (W81 F-001, all six adopters).
  - A2 classifies with gov doctor's `_match_pattern`, which never matches `*` before `**` (rust-workspace F-002; src/gov/doctor/command.py:532).
  - A6 and A8 rebuild the store, undocumented (python-app-clean F-007, python-app F-013).
  - The memaudit driver stops at any preflight refusal where the design repairs (F-1, drafts/fresh-80/P-FRESH-80-1.md §6); the writer's result counts areas in a different list from the preflight (F-2).
  - `gov context` refuses 38 % of leads' calls (CONTEXT_OVER_CEILING, BLOCKED, STORE_MISSING; P5 F3); the sandboxed embedder is unreachable, so workers' searches degrade (P5 F1).
  - `gov brief` leaves Objective empty and `{...}` slots unfilled in auditor briefs (W81 F-004 and others).
  - A launched auditor's Write to its brief's scratch folder is refused (W81 F-006).
  - `gov launch` refuses a `--model` that differs from its routing instead of picking it (W81 F-014; P4).
  - W2-195's lead found one product defect outside its paths behind 173 reds (its return, log/W2-195-A5-build.json).

## 7. JOB-20261116-15 and the figure
JOB-20261116-15 ran 19:24-19:38 and stopped at the visible half's first preflight (PF-SPREAD refused: plan area 1; PF-DRAWN refused: q24); the checker, the hidden half, the judge and the diagnostics did not run: **no figure**. The visible half `memory-audit-26111601` is abandoned, never measured; `…02` never written. JOB-20261116-17 (the same measure with the product's retry route; audits `memory-audit-26111603/04`, commit c1fdb0517a93) is queued, not run (no result at writing, 22:09).

## 8. cleanupPeriodDays
`/home/usain/.claude/settings.json` holds `"cleanupPeriodDays": 365` (JOB-20261116-16, 19:32; backup `~/.claude/settings.json.bak-keep-transcripts`).

## 9. The 98.7 % behind DEC-1098
Record: `governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md` (5,961 B, committed a35c78072, 11-08). Run 2026-11-08 by the CTO session ad44f5fe. **Right end to end 78 of 79 (98.7 %), wrong claims 0 of 79**; bar at least 68 right and at most 3 wrong claims, met; the 95 % target (at least 76) reached; exact 95 % interval 93.1-100.0 %. Configuration: pin `pin-bcea09060ebc`, the pool on, the 6,000-token bundle, search again once (A2), at `c00d525f` on E0's clone, the reader `claude-opus-5-5` effort high no tools, graders Opus (counts) and Sonnet (agrees). Beside it (data): one search 72 (91.1 %); hit@5 67 (84.8 %); hit@10 70, hit@20 74. DEC-1098 (1) (11-09) accepted it as K9's memory line met and made the configuration the memory standard.

## 10. Access outside the repositories, their worktrees and run folders (this month)
| What | Where | Who | How often (evidence) |
|---|---|---|---|
| Releases and re-pins | `~/.local/share/gov-os/`, `~/.local/bin/gov`, release tags | the owner in a plain terminal | 2 releases (v0.1.0, v0.1.1); 10 pins installed; each re-pin the owner's step |
| Installs | `~/.local` (pip), EXAMIN's `.venv` (item 15) | the owner (the guard asks or refuses installs elsewhere) | EXAMIN item 15 once; the operator agent's install once (undone) |
| Control files of the repository (hooks, .claude/, settings, crontab) by ACT | the repo's `.claude/`, `~/.claude/` | the operator agent (class b) or the owner's hand | 19 operator applies since 10-16; 2 by the owner's hand; 23 operator queue entries 11-10..11-16 |
| Crontab | the user crontab | the operator agent (ACT-NIGHTLY-RESTART-1, ACT-OPERATOR-1/HOURS) or the owner | 7 commits naming crontab changes since 10-16 |
| User settings | `~/.claude/settings.json` | the operator (JOB-16) | 1 (cleanupPeriodDays) |
| The evaluation sets root (hidden halves, writers) | `~/gov-os-eval` | walled jobs and the walled writers (indep_launch.py) by the operator | jobs 02, 11, 14, 15 today; the writers' installs (ACT-EXAMIN-WRITERS-INSTALL-1) |
| The operator's own folder | `~/gov-os-operator` (queue, jobs, results, log) | the CTO writes queue/ only; the owner's operator runs jobs | 11 interim jobs today (9 results) |
| Another product's data | `/home/usain/EXAMIN APP/product/data` | the operator (JOB-05) | 1 |
| Session-box rehearsals | `/dev/shm/gov-os-*` | the box builder, reviewers | 12 folders now |
| Machine-wide state | `~/.gov-os/guard-calls`, `~/.gov-os/machine` (registry, launch lock, gate.json) | every guarded session and gov launch | 9 guard-log files; 8 registry entries |
| Local services | docker (ASMO Redis/Postgres), Ollama | read-only investigation (R2), Gov OS's embedder on 127.0.0.1:11434 | 1 investigation; Ollama on every search and rebuild |
| Owner's relays | the owner runs a job or a command by hand | the owner | 134 of 544 owner messages in the month relayed jobs or ACTs (retro P1) |
