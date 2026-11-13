# ACT-NIGHTLY-RESTART-1, review round 1 (bundle manifest 2ec8ae17c698; superseded by the rebuild, F2)

## Round 1

Reviewer: independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Brief: `reviewer-brief.md`, sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a (checked). Manifest sha256 computed: 2ec8ae17c6989dab39d4e9f7507cbc805ea4e644d1e9d061110c4275bb520ddd. All 5 files hash as the manifest says.

**How I checked.** I ran apply.sh in my own clone of w2/integrate (b9e878009c3e), with a planted HOME and a stub `crontab` that reads and writes a scratch file:
- check 0, verify 3, apply 0, after copy byte-equal, verify 0, undo 0, before copy byte-equal, check 0.
- Checks 1–8 green. At today's head checks 9/10/11 are red/green/red, as the rehearsal printed.
- The clone's tree and the planted HOME are unchanged: only the crontab changes.

I ran the package's test_nightly_restart.sh with `systemd-run` and `systemctl` stubbed (no real scope): 47 of 53 pass. The 6 fails (34–36, 39, 43, 47) need a real scope and were not reproduced. I ran the operator's act_class.classify on my copy: class b, no hits, why crontab:crontab. validate_manifest and the path rule pass on apply.sh and on all 11 checks.

### Answers to the CTO's five questions
1. **"Nothing else running."** It is not decided by pid and committed state only:
   - quiet_check.py also matches process names: the argv basenames of the job scripts, `pytest` and `gov rebuild`, and a count of processes named `rg` above 100. It also reads each pid's cwd.
   - No wait is on a named process and no stop is by name. The waits are on `$SPID` and `$WPID` by pid. The stops are `systemctl --user stop <the exact unit it created>`, falling back to `kill -TERM $SPID`.
   - A name match can only add a refusal, so it fails closed (F6).

   If something starts during the run:
   - **A lead:** dispatch/OFF stops the dispatcher's leads and landings. A lead started by hand (launch_worker.sh, launch_now.sh, `claude -p`) is not held (F7).
   - **A close:** close_queue waits on NIGHTLY-RUNNING.
   - **A heavy slot:** nightly.sh holds all three heavy slots (DEC-984), so other slot users wait.
   - **Any contention:** the cap bounds the nightly. The watchdog stops the nightly's scope if MemAvailable falls under 2 GiB, and the night is then FAILED, never green.
2. **Fail closed.**
   - A cap it cannot compute: meminfo unreadable gives "REFUSED: memory", exit 2 (reproduced).
   - No bus, systemd-run absent, or the user manager refusing the probe: "REFUSED: no systemd user scope", exit 2, NOT STARTED in run.txt (reproduced).
   - The real scope failing after the probe: systemd-run never runs the command, exit 1 (reproduced). That night reads MISSED at 08:00, with the wrong reason (F9).
   - An out-of-memory kill: exit 137 gives "KILLED by its memory cap". The wrapper removes NIGHTLY-RUNNING and appends that line to the night's run.txt. With no `verdict:` line, nightly_check.sh writes FAILED and pings P1, never `ran`. The wrapper's reporting path was reproduced with a stubbed 137.
   - Not checked at run time: that the memory controller actually enforces MemoryMax (F10).
3. **Class.** (b) is right: the crontab row of class-rules.yaml, with no script hits.
4. **apply.sh and the rebuild.**
   - `check` and `verify` decide by the crontab's sha256 alone (before, after, anything else exit 3).
   - `apply` and `undo` do not check the live crontab: they install the frozen copy over whatever is live (F1). The operator's G7, run before the apply and again after any G9 hold, covers the operator's route.
   - A rebuild with an unchanged crontab and an unchanged head gives the same manifest sha (reproduced: 2ec8ae17c698).
   - The planned rebuild comes after the wrapper's commit. That flips the rehearsal line "at the live head today: red, green, red" to green, which gives sha 7c8ff2b3ab2e (simulated), so this verdict will not pass G4/G5 (F2).
5. **Main tree and w2/integrate.** The wrapper never commits, stages or writes a tracked file. Its writes go to ignored `.gov-runtime/scratch/orchestrator/` (logs, run.txt, dispatch/OFF, inbox items). Its git calls only read (`diff --quiet`, `ls-files`, `status --porcelain`, `log`). The one exception is `git status`'s optional index refresh in the main tree's .git (F11).

### Findings

**F1: apply and undo install without checking the live crontab**
- KPI: 1. Scope: in.
- Ordinary work: no. The operator runs `apply.sh check` at G7, and again after any G9 hold, before it applies. The by-hand route in §4.2 runs `check` just before `apply`.
- Consequence: loses work. A line added to the crontab between check and apply would be overwritten.
- Evidence: in my clone, with `# moved` appended, check exits 3, but apply exits 0 and the line is gone.
- Fix: in `apply`, require the live crontab to be the before (or already the after); in `undo`, the after (or already the before); otherwise exit 3.

**F2: this sha cannot be applied, and the planned rebuild replaces it**
- KPI: 4. Scope: in.
- Ordinary work: yes, because the package (§4.4) plans the rebuild after the wrapper's commit.
- Consequence: other (fails closed; the cost is another review).
- Evidence:
  - Checks 9 and 11 are red at today's head: `nightly/nightly_restart.sh` is not committed there. The operator's G8 would refuse this bundle.
  - The rebuild flips the rehearsal's live-head line, which gives manifest sha 7c8ff2b3ab2e (simulated) instead of 2ec8ae17c698. This verdict then fails G4 ("another manifest sha") and G5.
  - build_act.py refuses to rebuild while review.md exists.
- Fix: commit the wrapper first, rebuild, then review the rebuilt bundle. Or leave the live-head line out of rehearsal.log, so the sha depends only on the crontab and the bundle.

**F3: the checks bind the crontab line to a path, not to the reviewed bytes**
- KPI: 4. Scope: in.
- Ordinary work: yes, because the move into nightly/ is still to come and a fix could land before it.
- Consequence: other. nightly/ is an ordinary-change folder by the class table (catch-all, `control: false`), like nightly.sh, and the wrapper's "committed code only" rule still holds.
- Evidence: checks 9–11 test only that the files are present, committed and parse.
- Fix: add checks that `git rev-parse HEAD:governance/project/orchestration/nightly/nightly_restart.sh` is 5e08e24764f00c2aff895057c31c8093afe1d7ea and that quiet_check.py is 1b887c11b49168bb73e2803ff9f5e52af380ad5f (the copies in b2a33d7b50e4).

**F4: two crontab lines change, not one**
- KPI: 1. Scope: in.
- Ordinary work: yes, because a summary that says "one line" is what an approver reads.
- Consequence: other.
- Evidence: the after copy also turns back on `0 8 * * * … nightly_check.sh` (its DEC-1049 stop lifted). The package's §1.1 says so; the request for this review said "one line … the old stopped lines stay commented". The @reboot check and the 09:30 sweep stay stopped (checks 5 and 6).
- Fix: the owner's yes summary names both lines.

**F5: the rehearsal is real, but part 2 is a copied log**
- KPI: 3. Scope: in.
- Ordinary work: yes. Consequence: other.
- Evidence: `build_act.py rehearse` copies part 2 from the static rehearsal-wrapper.log (15:41) instead of re-running it. The files it tested are byte-identical to the committed ones (cmp). Part 1 ran in the drafts folder, with the git checks in a fixture repository rather than a clone of the live head. My reproduction matched part 1, and part 2 as far as stubs allow.
- Fix: at the rebuild, re-run test_nightly_restart.sh on the committed copy.

**F6: quiet_check matches process names (DEC-1073 (4))**
- KPI: 3 (the wrapper's rehearsal). Scope: out (the wrapper is not a touched file; reported because the CTO asked).
- Ordinary work: yes. Consequence: other (a match can only refuse the night).
- Evidence: quiet_check.py lines 100–109 (`JOB_SCRIPTS`, pytest, `gov rebuild`), lines 200–209 (comm `rg`), and the watchdog's `ps -eo comm= | grep -cx rg`, which only writes an item.
- Fix: record in the package that a detection-only match that can only refuse is outside (4), in the spirit of DEC-1133 (5) D1 for `rg`, or have the owner confirm.

**F7: a lead started by hand during the run is not held**
- Scope: out. Ordinary work: yes (a CTO session can be active at night).
- Consequence: other. The cap, the watchdog and mem_guard bound the effect, and a stopped run is FAILED, never green.
- Evidence: only run_tick.sh reads dispatch/OFF; launch_worker.sh and launch_now.sh do not.
- Fix: make launch_worker.sh and launch_now.sh refuse while NIGHTLY-RUNNING exists, in a later ordinary change.

**F8: a stale dispatch/OFF after a hard stop**
- Scope: out. Ordinary work: yes (WSL ended at night, for example by a Windows restart).
- Consequence: other. The dispatcher stays halted until someone removes the file, and the next night is refused, then FAILED with P1. No work is lost.
- Evidence: the EXIT trap runs on SIGTERM (tested: rc 143, trap ran), but not on SIGKILL or when the VM ends.
- Fix: at start, remove an OFF whose token names a `nightly_restart pid` that is not alive (`kill -0` on that pid), and log it.

**F9: a scope that fails after the probe is reported as MISSED for the wrong reason**
- Scope: out. Ordinary work: no. Consequence: other (still a P1, never green).
- Evidence: reproduced. The wrapper logs "run ended: exit 1, unit result none" and writes no run.txt, so the 08:00 line says "cron, WSL or the PC was not up".
- Fix: when the exit is non-zero and today has no run folder, write a NOT STARTED run.txt that names the scope failure.

**F10: the probe does not check that the cap is enforced**
- Scope: out.
- Ordinary work: no. The delegation of the memory controller comes from user@.service's defaults, and linger starts the same unit. The author's real-scope run read memory.max 12 GiB, swap.max 0 and oom.group 1 on this machine.
- Consequence: fails open in principle (an uncapped run).
- Fix: in the probe, read the scope's own `memory.max` and require 67108864 (64M); refuse otherwise.

**F11: quiet_check's `git status` may take the main tree's optional index lock**
- Scope: out. Ordinary work: yes. Consequence: other.
- Evidence: quiet_check.py line 189. It runs only when the machine is otherwise quiet.
- Fix: set `GIT_OPTIONAL_LOCKS=0` in `git()`.

No finding blocks: the only one that loses work (F1) and the only one that could fail open (F10) are not reachable in ordinary work. Every KPI passes.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "2", "verdict": "pass", "findings": []}, {"kpi": "3", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F9", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F10", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F11", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "4", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "5", "verdict": "pass", "findings": []}, {"kpi": "6", "verdict": "pass", "findings": []}], "manifest_sha256": "2ec8ae17c6989dab39d4e9f7507cbc805ea4e644d1e9d061110c4275bb520ddd", "class": "b", "reviewer": "independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author", "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a", "time": "2026-11-11T16:12:00+00:00", "replay_refused": []}
```
