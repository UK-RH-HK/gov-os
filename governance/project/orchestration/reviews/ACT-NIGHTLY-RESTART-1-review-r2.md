## Round 2

Reviewer: independent-auditor, claude -p session (round 2) started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Brief: `reviewer-brief.md`, sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a (checked). Manifest sha256 computed: 0e308cde3aecb0347a0aad634a8bf248a3df881cad500c23c8044611cec8ed88. All 5 files hash as the manifest says. This round judges only round 1's findings and the fix pass (DEC-1131).

**How I checked.**
- **Clone and stubs:** a clone of w2/integrate (483a5a2bee12) under my TMPDIR, with HOME planted and `crontab` stubbed by a file.
- **wrapper-r2:** it applies cleanly. The result is byte-equal to `files/nightly-r2/`, with blobs dd5129a25715b3bc00685e6104eba79f195563e2 and 3225297532f2dcdbb849c21e758cd4529b300dc2. I committed it in the clone only (affb4436236d).
- **Operator code on the bundle:** validate_manifest and the path rule pass on apply.sh and all 13 checks. act_class.classify gives class b, no hits, why crontab:crontab.

### Round 1's findings, as fixed
| Finding | Result |
|---|---|
| F1 | **Closed.** Over a crontab with a line added, apply and undo both exit 3 and the file is unchanged (`cmp`). The same holds over a missing or empty crontab. Apply over the after and undo over the before exit 0 and touch nothing. A tampered frozen copy exits 4. The full cycle restores the before byte for byte, and the clone and HOME are unchanged. |
| F2 | **Closed.** build_act.py prints the live head and the count of red checks to the console only. The hashed log holds only fixed text, manifest values and blob ids, and the test's pid, count and exit texts are gone. My 52 passing wrapper lines are byte-identical to the rehearsal's. |
| F3 | **Closed.** At the unpatched head, checks 1–11 are green and 12–13 red (fails closed). With wrapper-r2 committed in my clone, all 13 are green. On the before crontab, only the 3 crontab-line checks are red. |
| F4 | **Closed.** §0, §1.1 and §4.2 (the yes line) name both lines: the new 04:00 `nightly_restart.sh` line and the 08:00 `nightly_check.sh` line back on. |
| F5 | **Closed, partly reproduced.** `build_act.py rehearse` part 3 runs `test_nightly_restart.sh` from the clone, on the wrapper as committed there. rehearsal-wrapper.log is no longer read. I reproduced 52 of 62 cases; the other 10 need a real scope (R2-F1). |
| F8 | **Small, fails closed.** An OFF is removed only when its token is `nightly_restart pid N …` and `kill -0 N` fails. A reused or foreign pid keeps the OFF and the night is refused. The CTO's own OFF is never touched (case 40). |
| F9 | **Small, report only.** A non-zero exit with no run folder for today writes a NOT STARTED run.txt. nightly_check.sh reads it as FAILED with a P1 (first line has "nightly night:", no `verdict:` line). It is never green. A run that wrote its own run.txt is left as it is (case 59). |
| F10 | **Small, adds a refusal.** The probe must read back memory.max 67108864, or the night is refused before OFF, the marker or the run. A stand-in that drops the limits is refused (case 60). |
| F11 | **Small.** `GIT_OPTIONAL_LOCKS=0` is set in `git()`. The index is left unchanged, and the control case shows a plain `git status` would change it (cases 61–62). |
| settle (new) | **Harmless.** At most 10 × 0.5 s of reads after the run ends. The verdict still rests on exit 137, the watchdog's TRIPPED file or a Result of timeout/oom-kill, so it cannot turn a killed run green (see R2-F4). |

**Point (7):**
- **Crontab:** the after is byte-identical to round 1's.
- **apply.sh:** only adds refusals.
- **Checks:** the two new pins only tighten. `commands` stays empty.
- **Hook:** the only new hook is `NR_SYSTEMD_RUN`, which cron never sets, and F10's read-back still applies through it.
- **F8:** lets a night run that a stale OFF would have refused. That is the fix round 1 asked for, not a widening.

**Tests run:**
- **`test_nightly_restart.sh`:** run on the committed patched copy, with the run command stubbed through `NR_SYSTEMD_RUN` (the sandbox refuses the user bus). 52 of 62 pass. All F8–F11 cases (54–62) pass.
- **`test_nightly.sh`:** passes on the patched clone (N1–N19 including N19, C1–C3, K1–K17, G1–G11, E1–E2, S1–S7, R1–R3).

### Findings

**R2-F1: the real-scope cases, including F10's success path, were not reproduced by the reviewer**
- KPI: 3. Scope: in (F5 and F10's check).
- Ordinary work: yes, because every night runs the probe and the scope.
- Consequence: other (fails closed). If the probe reads anything but 67108864 here, the night is refused (FAILED, P1). A cap that is not enforced is refused, never run.
- Evidence: the sandbox's user bus is refused ("Failed to connect to bus: Operation not permitted"). With a stub run command, cases 34–36, 39, 41–44, 47 and 51 fail. Each reads the scope's cgroup files or needs a kernel kill or RuntimeMaxSec. The rehearsal shows them passing with a real `systemd-run --user --scope`, and the code confirms part 3 runs them live.
- Fix: none needed before queuing. On the first watched night (§4.4), the CTO reads `log/nightly/restart/<date>.log` for "the memory cap is not enforced". Or run part 3 once outside the sandbox.

**R2-F2: F9's NOT STARTED text also fires when nightly_cron.sh itself refuses**
- KPI: 3 (the wrapper's rehearsal). Scope: out.
- Ordinary work: no, because the wrapper checks the same "committed code" rule just before, and quiet_check needs a clean main tree for 5 minutes in a row.
- Consequence: other. The night is still FAILED with a P1, and nightly_cron.sh sends its own P1 NIGHTLY-NOT-RUN. Only the stated reason ("the scope failed after the probe") is wrong.
- Evidence: nightly_cron.sh exits 2 without making a run folder on its code-check refusal. The wrapper's new branch fires on any `rc != 0` with no run folder today.
- Fix (later, ordinary change): word it as "the run exited N and left no run folder (the scope failed, or nightly_cron.sh refused)".

**R2-F3: F8 removes a stale OFF even if the dead wrapper's scope still runs**
- KPI: 3. Scope: out.
- Ordinary work: no. It needs the wrapper SIGKILLed while the VM stays up, its scope living on, and a second start by hand the same night. Cron's next start is 24 h later, past RuntimeMaxSec (3 h).
- Consequence: other. The dispatcher (it stops only on OFF) could start leads beside a run that is still capped. The second wrapper still refuses on NIGHTLY-RUNNING.
- Evidence: the F8 block runs before any check of `gov-nightly-*.scope`. run_tick.sh reads only `dispatch/OFF`.
- Fix (later, optional): remove the OFF only when no `gov-nightly-*` scope is active (`systemctl --user list-units --state=active 'gov-nightly-*'`).

**R2-F4: the settle loop may not wait through "deactivating"**
- KPI: 3. Scope: out.
- Ordinary work: yes, because every run ends through it.
- Consequence: other. It only reads, at most 5 s. The verdict rests on exit 137, the watchdog's TRIPPED file or a Result of timeout/oom-kill, so a killed run is never reported green. At worst a failed unit is left loaded. The next run uses a new unit name.
- Evidence: plausible, not reproduced here (no bus). `systemctl is-active` exits non-zero for a unit in "deactivating", so the loop breaks at once in that state.
- Fix (later, optional): loop while `systemctl --user show -p ActiveState --value "$UNIT.scope"` is `active` or `deactivating`.

No finding blocks. None is both reachable in ordinary work and fails open or loses work. Every KPI passes.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []}, {"kpi": "2", "verdict": "pass", "findings": []}, {"kpi": "3", "verdict": "pass", "findings": [{"id": "R2-F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2-F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "R2-F3", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "R2-F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "4", "verdict": "pass", "findings": []}, {"kpi": "5", "verdict": "pass", "findings": []}, {"kpi": "6", "verdict": "pass", "findings": []}], "manifest_sha256": "0e308cde3aecb0347a0aad634a8bf248a3df881cad500c23c8044611cec8ed88", "class": "b", "reviewer": "independent-auditor, claude -p session (round 2) started by the CTO (launch_worker.sh, DAEO-r30l); not the author", "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a", "time": "2026-11-11T16:59:30+00:00", "replay_refused": []}
```
