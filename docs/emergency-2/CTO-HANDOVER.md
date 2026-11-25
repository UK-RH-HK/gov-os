# CTO handover (session ac51847d -> the fresh CTO, 2026-11-25 about 23:05)

The method is DEC-1253: read your card first (`template/governance/kernel/templates/role-cto.md`), then this file, then take over by the card's eight checks and send the owner one takeover message before any other work. The outgoing CTO stops after that message.

## 0. State
- HEAD on `w2/integrate`: the commit that records this handover (its parent is `7fc18d489`, DEC-1253).
- Live gov: **0.1.7** (`readlink -f ~/.local/bin/gov` -> `~/.local/share/gov-os/pin-3d039a8fb6d3/bin/gov`; `gov --version` -> `gov 0.1.7 (commit 3d039a8fb6d3...)`); the owner re-pinned it by hand tonight (registry entry `c1e81afd3`). 0.1.6 and 0.1.7 are in `~/.local/share/gov-os/burned` (their automatic re-pins rolled back, I-31); 0.1.7 is live all the same.
- Decisions to read by id: DEC-1244, DEC-1245, DEC-1246, DEC-1247, DEC-1248, DEC-1249, DEC-1250, DEC-1251, DEC-1252, DEC-1253.
- The integration plan's current phase: **Phase 1** (the landing; item 1-0 built tonight); the next: **Phase 2** (the launch). Read those two phases whole; Phase 0 is landed; Phase 3's W2-207 items are built and held.
- The account of 23 to 25 Nov: `docs/emergency-2/integration/ACCOUNT-2026-11-25.md`. The latest decisions page: `docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html` (answered: `ANSWERS-B-2026-11-25-cto.txt`, DEC-1251, DEC-1252).

## 1. Progress (run `python3 .gov-runtime/scratch/orchestrator/tools/progress_block.py`; this is its output at the handover)
- Keystones: K1-K8 done; K9 7/12 (W2-19 deferred, W2-27..30 moved to EXAMIN's Wave 0)
- Wave 2: 201 closed, 4 left (W2-207, W2-209, W2-210, W2-81); on branches: W2-211, W2-212
- Integration plan: P0 4/4 landed; P1 0/15 (1-0 built, to land); P2 0/14, held 2-7 2-9 2-10; P3 0/13, held 3-1 3-2 3-10 3-13; P4 0/6, held 4-2; P5 0/18, held 5-4; P6 0/6
- Releases: 0.1.5; 0.1.6 burned; 0.1.7 LIVE (owner's re-pin); next: 0.1.8, the bundle, built by the owner's hand until I-34's rule is built

## 2. Running, and how to check each
- **Leads:** none running. The last, `1-0-selection`, returned at 22:56 (`log/leads/1-0-selection.json`).
- **Watcher:** none (the outgoing CTO's ended with the 1-0 event). Start yours, tracked, no heartbeat: seed a seen file from `log/cto-ac51847d.seen`, then `HEARTBEAT_S=999999 NSAMP=10 bash .gov-runtime/scratch/orchestrator/tools/cto_watch.sh .gov-runtime/scratch/orchestrator/log/cto-<your session's first 8>.seen` as a tracked background command; restart it first thing after every event (memory: watcher-restart-every-time; two 3-hour lapses on 25 Nov).
- **Cron lines** (`crontab -l`): the old dispatcher tick (every minute; starts nothing); hourly backups (Gov OS and EXAMIN); `@reboot` embedders; `stall_check.sh` every 15 min (reads `log/cto-tmux.txt`, so write yours); the 0-1 integration-store retry every 5 min.
- **Background, detached:** `usage_log.sh` (hourly plan reading into `log/usage.txt`) and `capacity_sampler.py` (36 h from 24 Nov 17:23, `log/capacity-samples.jsonl`): check with `ps -eo pid,args | awk '/usage_log|capacity_sampler/ && !/awk/'`.
- **tmux sessions:** `cto-1124-1722` (the outgoing CTO; it stops after your takeover message), `examin-cto-1124-1725` (EXAMIN's CTO), `asmo-cto-1124-1725` (ASMO OS's CTO), and yours. Always an exact target: `tmux send-keys -t "=<name>:0.0" -l "<text>"` then `Enter`.

## 3. Held branches (land them in one batch after 1-0, the owner's order; each record under `.gov-runtime/scratch/orchestrator/log/landings/`)
- `e2/1-0-selection` (head `22101a73d`, plan item 1-0, SEL-1 to SEL-4): **land first, alone**, by the plain path; its own selection is now small. Cause it fixed: `src/gov/close/select.py:775-778` added every path since the last green record. Record: write `1-0-selection-<date>.md`.
- The 0.1.8 bundle, eight branches, one batch merge then one selected run (SEL-4: `gov queue A=b1 B=b2 ... --select` gives one list for the merged tree), acceptance conflicts by the test designer only: `e2/d1-verdict` (W2-210, `d1-verdict-20261124.md`), `e2/escalation-slice` (W2-211, place `.tickets/DAEO-esl1.md` first), `e2/d3-stale-route` (W2-212, place `.tickets/DAEO-d3sr.md` first; re-read EXAMIN's map, not `/home/usain/examin-eval`), `e2/kit-head` (after eval-roots: KH-3 vs the interim deny lines), `e2/usage-per-repo` (UR-1 to UR-7), `e2/w2-207-pre-retire` + `e2/w2-207-runtime` (then the cut-over by `docs/emergency-2/W2-207-CUTOVER-RUNBOOK.md` on the branch, then DEC-1234's capacity assessment), `e2/models-by-role`, `e2/eval-roots` (then the two root moves with each repository CTO's yes, then remove the interim deny lines `e8e277a74`). The bundle is a bigger release: the owner builds it by hand (I-34) unless I-34's rule lands first.

## 4. Waiting on the owner
- Nothing of Gov OS's. EXAMIN: 36 cards on its own page (https://claude.ai/artifact/PGxntigTiaDu4G58nmj1xz), answered with the EXAMIN CTO (DEC-1251 D-07). ASMO OS: its two questions before A6, in its CTO's chat (D-08). Startup Launchpad steps when he can (nothing waits).

## 5. NEXT ACTIONS, in order
1. Take over (the card); takeover message to the owner.
2. Land `e2/1-0-selection` by the plain path (its selection run exactly; trailers checked; landing record; `log/plan-items.json`: 1-0 landed).
3. Tell the EXAMIN and ASMO OS CTOs the handover method from tomorrow (DEC-1253): each writes its handover in its own repository at day end, records it, starts its fresh session from it, and the fresh session takes over by the same checks; send them the card's "Take over" section adapted (their own coordination ticket and paths).
4. Start, in parallel (one code area each):
   - the timing-tests lead (DEC-1251 D-03: (b) the timing cases W2-112, W2-13, W1-19 into the serial phase now, then (a) measured against the machine's reading; I-32);
   - the release-rule lead (DEC-1251 D-01's note: build DEC-1235 (2)'s rule for approved bigger releases, I-34, and settle W2-209 so a fix like RP-1 rides a patch);
   - the I-33 fix (`gov memaudit brief --kind writer` exits 4 and prints no LAUNCH line).
5. The bundle: one batch merge and one selected run, then land; then the owner builds 0.1.8 by hand (or the CTO by code once I-34's rule lands).
6. Gov OS's own fresh 80 on 0.1.7: the writer wall's template is approved (the owner added the line to `APPROVED`); confirm the launcher accepts it when the measure starts (DEC-1253).
7. The practice-first work (DEC-1252, all 31 recommendations): the tool status list for 0.1.7, the findings log form in each repository with `gov findings collect`/`sync` (an approved feature), the `release:` field, the decision rubric with `Affects:`/`Enforced-by:` and one Sonnet research pass classing the 162 older decisions, `docs/RUBRICS.md`, data in specs. Plan them into the integration plan's streams.
8. ASMO OS's usage report to the owner about 27 Nov (DEC-1245 (3)).

## 6. The other CTOs
- **EXAMIN** (`/home/usain/gov-os-runs/W2-27/examin`, tmux `examin-cto-1124-1725`): on 0.1.7 (`gov update 0.1.7` at `b51f5a0`); its fresh 80 pair 20261125 runs, writers launched from `LAUNCH.txt` (I-33); its Contract draft 1.0 (`52e96ed`); its page of 36 cards waits on the owner; it now asks for "the memory-fix plan as a decisions page" (its own work). Findings it raised: EF-4 (I-17, fixed), EF-5/6/8/9 (fixed in 0.1.7), EF-10/11 (I-26, I-27, wait for the measure), EF-12 (the gate null, fixed), EF-13 (I-33, open). It types findings into your tmux session; read its `REQUESTS.md` FINDINGS LOG if a message seems missing.
- **ASMO OS** (`/home/usain/ASMO-OS-V1`, tmux `asmo-cto-1124-1725`): adoption at A5, waiting on the owner's two answers; then A6 to A10 (memory build, auditors), its fresh 80, its Contract.

## 7. Traps of the two days (also in memory)
- The watcher only as a tracked background command, restarted first after every event; no heartbeat.
- A test of a command line does not prove a hook, a session or a re-pin: prove the real path (FM-5, I-31).
- Q-7 holds for flakes: the second failure of a case that passes alone stops re-runs; fix the cause.
- Run the release suite on an idle machine; move untracked records out of `docs/close/nightly/` before a cut (G4 refuses an untracked file); point `--suite` at the moved record.
- A blank line before `Co-Authored-By` hides `Role:` and `Fix:`; check trailers by code before every merge.
- Never resolve an acceptance conflict inside a merge commit (DEC-253): the test designer commits it first.
- A shell command naming EXAMIN's sets root is refused by the interim deny (use a file tool or a variable).
- `pkill -f` kills your own shell: kill by PID. tmux always with `=name`.
