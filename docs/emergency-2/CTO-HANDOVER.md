# CTO handover (the CTO session ed90a0d3 → the fresh CTO on Opus, 2026-11-19 about 13:45)

Read `docs/emergency-2/EMERGENCY-2.md` first, then this page, then DEC-1214 to DEC-1218 in `docs/DECISION_REGISTER.md`
(the register in force holds the kept decisions and everything from DEC-1211 on; an older id is in
`docs/archive/DECISION_REGISTER-2026-11-19.md`). Then `docs/emergency-2/MORNING-BRIEF-2026-11-19.md` (the night, and the
decisions' table) and the night's notes, `.gov-runtime/scratch/orchestrator/log/night-notes-20261119.md` (every landing,
red and fix with its time; the fixes still owed). **The owner is awake and answering in the chat.**

## 0. Your standing orders (the owner; DEC-1216, DEC-1217, DEC-1218)
- **Full pace, the release path first:** the green base, release 0.1.4, EXAMIN's fresh 80, the cut-over; then the rest.
- **Usage:** push the owner (PushNotification) at 95 % and at 99 % of the plan: he adds usage credits; no work stops.
  The plan is read by `usage_log.sh` (hourly; every 10 minutes from 95 %) into
  `.gov-runtime/scratch/orchestrator/log/usage.txt`: 87 % at 13:19. Both of his Fable resets are used; DEC-1215 is
  reverted (the substitution file says `active: false`).
- **Pushes for decisions:** a decision that stops work pushes him at any hour; one that stops nothing waits for the
  morning brief. Every push also appears in the next morning brief.
- **Reports:** every report ends with the status block, counted fresh each time:
  `python3 .gov-runtime/scratch/orchestrator/tools/status_block.py` (`--mark` sets "since the last report"; keep
  `merged_not_closed` and `waiting_on_owner` true in `log/report-state.json`). **Wake less and batch:** report for a
  landing, a red, a decision or a push, not for a heartbeat. The outgoing session cost about six times a fresh one per
  call because it woke for short notes with 380,000 tokens of context.
- **Models:** the rubric. You and C3 helpers on Opus (a helper's prompt needs the line `Task: <ticket id>`); leads and
  every other helper on Sonnet. The EXAMIN CTO goes back to Opus at its next start.
- **The machine:** the load stays inside the gate (20). Test runs go through
  `.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with `-n auto` (three slots of two workers on four CPUs each,
  start under load 10: `heavy_slots.conf`), and each run removes its temp folder. Watch free inodes (the gate's floor is
  10 million; leftover `/tmp/tmp.*` and pytest `garbage-*` folders took it under twice).
- **A watch you can copy:** `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/ed90a0d3-00d1-4070-bd74-ac142103e342/scratchpad/night_watch2.sh`
  (a lead's end, a full suite's end, the plan at `USAGE_AT`, the load over `GATE` for `NSAMP` samples, low inodes, a
  heartbeat): change its `SEEN` path to your own scratchpad, copy `night_seen.txt` beside it, and make it fire at 95 and
  at 99. Keep a heartbeat under 60 minutes: the dispatcher's stall check pushes the owner after 60 minutes of CTO
  silence by day (2 hours between 02:00 and 07:30); he kept it.
- **tmux:** target a session exactly (`-t "=name"` for session commands, `-t "=name:"` for panes). A bare name matches by
  prefix; that killed the fresh EXAMIN CTO once.

## 1. Running at the handover
| What | Where it returns | Note |
|---|---|---|
| Lead `kit-e2` (W2-208): two deny lines only; the golden rules at the head of CLAUDE.md and AGENTS.md through `gov adopt` and `gov update` (DEC-1217 (6), (7)) | `log/leads/kit-e2.json`; a wake in your inbox | on the release path; brief `docs/emergency-2/briefs/LEAD-kit-e2.md` |
| The EXAMIN CTO (tmux `examin-fable-2340`, a Fable session, idle since 03:30) | its reports; `REQUESTS.md` in its clone | it waits for release 0.1.4; restart it on Opus when it has work |
| `usage_log.sh` (detached) | `log/usage.txt` | restart it if it dies: `EVERY=3600 SPEND_CHECK=0 setsid nohup bash usage_log.sh` in the tools folder |

## 2. The base
- **Integration head:** see `git log -1`. Eight tickets landed and closed overnight (W2-199 to W2-206); the register is
  archived (W2-203); `gov context` is gone (W2-200).
- **The last full suite** (05:18 to 07:01, on `712c71cba`, before W2-200 and W2-204): 18,610 passed, 9 failed, 94
  skipped. Of the nine: the two W1-01 authorship cases are green now (the owner's exemption, DEC-1217 (2)); W2-13,
  W2-86, W2-158 and W2-61's two are revised and green; the Stop hook's one-line case is fixed; **W2-76's watchdog case
  passes alone and its cause is not found.**
- **Red on the head now, known:** `tests/acceptance/W2-203/test_w2_203_close_lookup.py::test_s5_real_the_lists_count_what_the_base_counted`
  (it compares the live register's counts with the base's; the register is live from DEC-1211 on, so it needs the same
  revision the other W2-203 cases got: a test designer on Opus, `Task: DAEO-r3gx`, with a Rewrite-Reason naming the
  amendment in W2-203's record). `gov accept W2-203` is 62 of 63 until then.
- **Load-sensitive, not red in the full suite:** W2-13's warm-latency case (p95 0.53 s against 0.5 s under load).
- **Not yet in any full suite:** W2-200, W2-204 and every fix since 05:17.
- **The first full suite's record** (`docs/close/nightly/NR-*.json`, untracked) is red and is not committed. Commit only
  a green one.

## 3. Next, in order
1. **Land `kit-e2`** when it returns. Before any merge, list the commits that touch `tests/acceptance` and check each
   carries `Role: independent-test-designer` (`git log --format='%h %(trailers:key=Role,valueonly)' w2/integrate..<branch> -- tests/acceptance`).
   Then run its folders on the merged tree, `gov accept`, and close the ticket at the land with the evidence in its record.
2. **Clear the two open reds:** W2-203's count case (above) and W2-76's flaky watchdog case (an engineer finds the cause
   before any fix; it failed under the full suite confined to six CPUs, passed alone).
3. **The green base:** rebuild the main tree's store at the head, then one full suite, three workers on six CPUs outside
   the lead slots (detached; it took 103 minutes):
   `GOV_HEAVY_SLOTS=3 GOV_HEAVY_EXCLUDE_CPUS="0-1" GOV_HEAVY_WORKERS=3 bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh --held 3 python3 -m gov.close.nightly w2/integrate --root <repo> --json`
   with absolute `PYTHONPATH` and node on the PATH (the form of last night's run is in the night notes). Every red fixed;
   on green, commit the `NR-*.json` record.
4. **Release 0.1.4** is the owner's hand (R-1 (a): as soon as the suite is green): tell him the base is green and what
   the release carries (W2-204 for EXAMIN's measure, W2-208, the night's batch).
5. **EXAMIN:** restart its CTO on Opus; it runs `gov update` to 0.1.4, writes its `governance/project/memory-audit.yaml`
   (the lead's draft is `docs/changes/W2-204-evidence.md` §2) and runs its fresh 80 (the commands are §3 there); then
   one EXAMIN feature ticket through the flow (release acceptance items 3 and 4).
6. **Gov OS's own landing onto `gov queue`** (L2-4, yes once the base is green): one green proving landing through
   `kernel_gate.py` then `gov queue`, then the scratch landing tools retire (L2 page, B2).
7. **The cut-over, by day** (W2-207, `.tickets/DAEO-rt4s.md`): the cron line to the product's pass, the product slot in
   place of the scratch script, the gate file's `heavy_slots`; relaunch switched on after one day of the new pass.
8. **Then the rest**, each as a lead with the leads' common briefs (`LEAD-COMMON.md`, `NIGHT-COMMON.md`):
   - **L2's B1** (`gov close` merges into `gov queue`; the `accepted_reds` and `load_sensitive` lists retire; the
     strict-close and secrets-scan tests retire with it, the owner's word in DEC-1218 (3)), then A2 (one close record),
     A7 (`--direct`, L2-6 (a)), B3, B4; the `--full` worker cap by one slot.
   - **G1-2:** `git rm` the P-* decision packages and the October assessment, with the tests that read them revised in
     the same change, before Gov OS's first fresh 80.
   - **TI-8:** a read-only audit of all 223 test folders, one line each (keep, thin, weekly tier, retire), by an
     independent auditor on Sonnet, as a page for the owner (`docs/emergency-2/TEST-INVENTORY-2026-11-19.md` is the
     start). Nothing but the B1 retirements is cut before his yes.
   - **Gov OS's first fresh 80:** after G1-2. First settle the control (its gold is in the archived register: re-take
     the baseline, `baseline: first`, or `control: none` in `governance/project/memory-audit.yaml`) and which briefs the
     writer and checker get (the approved ones through the walls launcher, or the generated ones).
   - **W2-81, the proving run** on the synthetic repositories, on the release candidate.
   - **The fixes owed** (the night notes list them): tests that leave read-only wall trees behind; W2-60a's test that
     writes to the live CTO inbox; the conftest clash of `tests/unit/dispatch` and `tests/unit/resources`; a W2-184
     promotion's Opus; the kernel's `context` policy key and the leftover mentions of `gov context`; the 271 lines of old
     version tables in 43 kept entries; DEC-085, DEC-086 and DEC-894 (no class); the adopt skill's step 6 text
     (`docs/changes/W2-204-evidence.md` §4); EXAMIN's four smaller requests (its `REQUESTS.md`, 01:45); `gov doctor`'s
     five unhealthy checks; the lead brief's line telling engineers to read the acceptance folder.

## 4. Waiting on the owner (keep `waiting_on_owner` in `report-state.json` equal to this)
- **G5, held until he has read the groups:** Charter v6 and Contract v5 on branch `e2/g4-g5` (worktree
  `/home/usain/gov-os-worktrees/E2-g4-g5`; `docs/emergency-2/G5-APPROVAL.md` there). The outgoing CTO pasted him one
  line per group and the seven new capabilities of G5-10 (CAP-63 to CAP-69), each of which needs his own yes. G5-0 is
  answered: (a), the new file names. On his yes: the steps of the approval page's "After your yes" (a test designer
  retires or rewrites the 11 tests); its merge will conflict on `docs/emergency-2/audits/08-new-register.py` and on the
  register (keep integration's).
- **T2-1, held until he has read the short form:** the rewritten escalation rubric
  (`docs/emergency-2/T2-ESCALATION-RUBRIC.md`). T2-2 is changed by him (a decision that stops work pushes at any hour)
  and T2-3 is (a): bring the page's §3 in line when you make the kernel text change after his yes.
- **TI-1 to TI-7:** after the TI-8 audit.
- **Release 0.1.4:** his hand, when the base is green.

## 5. How to run things without false reds
The CTO's memory files `test-run-gotchas`, `tmux-exact-session-target` and `owner-report-status-block` hold them: absolute
`PYTHONPATH`; node on the PATH for openspec; the main store at the head before a full suite; `-n auto` in every slot
run; no short `timeout` around a slot run; never two folders with clashing `conftest` in one ad-hoc call; record exact
times from `git log`, not from memory.

## 6. What the outgoing session got wrong, so you do not repeat it
The brief's §6 has the night's eight. Since then: a rule of its own in a lead's brief held the live register to the
archive word for word (four W2-203 cases went red when DEC-1215's revert was recorded; amended, one case still to
revise); and it wrote times into records from memory several times and had to correct them from the commits.
