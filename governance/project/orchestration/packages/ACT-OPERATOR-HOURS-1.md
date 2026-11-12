# ACT-OPERATOR-HOURS-1 (round 2): the operator agent's launcher runs at every hour and skips only while the night hold is on; it applies only after ACT-OPERATOR-HOURS-2 (DEC-1141 (6))

- **For:** the owner's ping reply naming this ACT, then **the CTO applies it** (class (b), P-ACT-SPLIT (b): a crontab change with a
  rehearsed rollback), **after ACT-OPERATOR-HOURS-2 is applied** (section 4: `apply.sh` refuses, exit 7, until it is). About one
  minute, from 08:00 UTC on (never in the quiet hours, never during the nightly).
- **By:** an ACT-preparation helper of the CTO (Sonnet, high; RUBRIC-2, class C1). Round 1: 2026-11-12 about 02:50 to 03:30 UTC.
  **Round 2** (the last review round, DEC-1010): about 03:30 to 04:00 UTC, on the independent review's round 1 (F1-F6). **Nothing live was
  changed or started:** no crontab write (only `crontab -l`, and `crontab -n`, which checks a file and bails out), no commit, no stage,
  nothing under `~/gov-os-operator`. Built and rehearsed in planted folders (section 6). **Round 2 reviewed READY** (`reviews/ACT-OPERATOR-HOURS-1-review.md`, both rounds; R2-F2 shown to the owner, section 10's `0110` variant the structural option).
- **Under:** DEC-1141 (6) (the owner, 2026-11-12: "the operator agent sleeps only while the nightly runs", the night hold, from 03:00 until
  the nightly ends; every other hour it runs); it changes DEC-1104 (5)'s operator hours, which ACT-OPERATOR-1 set. DEC-1138 (3) is the
  night hold's own rule. The manifest's `dec` names DEC-1141, DEC-1104, DEC-1138.
- **Companion:** ACT-OPERATOR-HOURS-2 (`acts/ACT-OPERATOR-HOURS-2/`, manifest sha8 `d3d29237`): the launcher's gate G9 on the same rule.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/operator-hours-1/` (`build_act.py`: build, rehearse, finalize, gates). The
  bundle: `.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-1/`. Filed here by the CTO (12119eb31, round 1's F6).

## 0. The short version, and your line
1. **One crontab line changes** (line 7, the operator's launcher). Every other line is byte for byte as it is.
2. **From `*/10 0,8-23 * * *` to `*/10 * * * *`:** every 10 minutes at every hour, with a guard in the line itself: no launch from 02:10,
   and from 03:10 a launch only when the night hold's state file is under 5 minutes old (and not dated more than 60 s ahead) and says
   `"holding": false`. A missing, empty, malformed or stale file means no launch (fail closed: no ACT is applied during the nightly).
3. **Same command, same log:** `/usr/bin/python3 -I .../operator_launch.py >> .../operator-launch.out 2>&1`, with the comment naming
   DEC-1141 (6) and ACT-OPERATOR-HOURS-1.
4. **No file in the repository changes**: the ACT is the crontab alone, class (b).
5. **Round 2: it can only apply after ACT-OPERATOR-HOURS-2.** `apply.sh check` and `apply` exit 7 ("ACT-OPERATOR-HOURS-2 is not
   applied...") unless the install's `~/gov-os-operator/install/opcommon.py` is HOURS-2's after copy (sha256 `123e17e5581149725c75babaa9200a09c4854254053df14105b6ce17450bbc87`).
   So the launcher's G9 and this line always hold on the same rule, and the 02:10 cutoff is right (section 1, F1). `undo` and `verify` never need it.

**Your line: `yes ACT-OPERATOR-HOURS-1 9cbccb82`** (the first 8 digits of the manifest's sha256 in section 8). The order, which the gate enforces:
your `yes ACT-OPERATOR-HOURS-2 d3d29237` and your operator's apply of it first; then this line is applied by the CTO.

## 1. Round 1's findings (the independent review) and what round 2 did
| Row | Finding (round 1) | Round 2 |
|---|---|---|
| **F1** (loses work) | A launch at 01:40 or 01:50 can strand in the run's own G9 wait after 02:00 (G9's quiet hours, DEC-1104 (2)) and is killed at 2700 s with its request thrown away unapplied. | **Closed by the gate, with a residual.** `apply.sh` refuses (exit 7) until HOURS-2 is live; with it G9 no longer holds at 02:00 but from 02:10 (HOURS-2's `HOLD_FROM`), the same minute as this line's cutoff, so a launch at 01:50 or 02:00 passes G9. Threshold `0210` kept, as asked. **Residual (M, read in `operator.jsonl`):** G9 comes after G1-G8 in `go()`, so a launch strands only if G1-G8 outlast 02:10. In the six applied runs I read (ACT-CLAUDE-COPIES-1, -2 and -3, ACT-DEADMAN-WAKE-1, ACT-DEADMAN-STANDBY-1, ACT-EFFORT-HIGH-2) G1 to G9 took 1-3 s. A run begun at 02:00 would need more than 10 minutes in G1-G8 to strand; at 01:50 more than 20. The "request thrown away on a timeout" is the runner's existing behaviour, not changed here: row for the CTO (an operator-install item, class (O)). |
| **F2** | The hold releases at 07:30 at the latest while a nightly may still run, so the guard launches at 07:30-07:50. | **Stands as a row, covered by G9, not by the line.** From 07:30 the line calls the launcher; the launcher's G9 still holds on the `NIGHTLY-RUNNING` flag (a flag younger than 6 hours), which HOURS-2 keeps (its package: "a nightly that overruns the hold still holds"; `holds()` in its after copy), so a queued ACT is held, not applied. The line itself does not read the flag. A one-test guard (`[ ! -e <scratch>/NIGHTLY-RUNNING ]`, about 50 characters) would close it in the line too: I did not add it, the CTO asked for F1, F3 and F4 only; say so and it is one more rehearsal case. |
| **F3** | A state file dated in the future reads as fresh (the age is negative, `age < 300` holds). | **Fixed.** The guard's test is `-60<=a<300`: more than 60 s in the future is stale (30 s of skew is allowed). Rehearsal cases 73-75: +30 s launches; +2 minutes and +1 day do not. **Note:** HOURS-2's `night_hold_reasons` reads `age < 300` (a negative age passes), so for a file dated 61 s or more ahead the line says stale and G9 says fresh. The safe direction (the line is the stricter one, and only the line starts a launch), but they differ: a mirrored fix in HOURS-2 changes its after hash and this bundle's gate with it (rebuild, section 4). Row for the CTO. |
| **F4** | When `date` fails, `[` writes "Illegal number" to standard error and cron mails it. | **Fixed.** `date`'s own stderr and the whole test group (`{ ... } 2>/dev/null`) are silenced; the launch is still refused. Cases 92-93: `date` failing with a message on stderr, and `date` printing abc, nothing, 12:30, 0a15, 2400x: no launch, nothing on either stream; the control prints 1400 and launches. |
| **F5** | Nothing restarts `night_hold.py` after a reboot. | **Stands as a row.** Fail closed on both sides: with the hold dead the file ages out in 5 minutes, so the line and (with HOURS-2) G9 do not launch from 03:10 to 07:59, as the old line did all night; the hold's other job, keeping new leads off the dispatcher, is what is lost, and that is not this ACT's. The live hold (pid 2246634) was started by hand on 11-11 at 20:08; no cron line or user unit starts it. A restart is a second small item: an `@reboot` crontab line (class (b), its own ACT) or the CTO's session-start routine. Not built here. |
| **F6** | The package still in drafts; its section 9 says "not reviewed". | **Updated.** Section 9 now states the review state: round 1 done (this table), round 2 not yet reviewed. The move to `packages/` is the CTO's (outside my two folders). |

## 2. What changes
Before (line 7 of the live table, sha256 of the whole table `c613d523f7ed`):
```
*/10 0,8-23 * * * /usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> /home/usain/gov-os-operator/log/operator-launch.out 2>&1  # DEC-1104 (2) (5), ACT-OPERATOR-1: the operator agent launched from its queue (the CTO only queues)
```
After (the whole table `88cf08b165a1`; the line is 887 characters, under cron's limit of about 1000):
```
*/10 * * * * h=$(date +\%H\%M 2>/dev/null); { [ "$h" -lt 0210 ] || [ "$h" -ge 0800 ] || { [ "$h" -ge 0310 ] && /usr/bin/python3 -I -c 'import json,os,sys,time;s=sys.argv[1];a=time.time()-os.stat(s).st_mtime;sys.exit(0 if -60<=a<300 and json.load(open(s))["holding"] is False else 1)' /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/night-hold.state.json; }; } 2>/dev/null && /usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> /home/usain/gov-os-operator/log/operator-launch.out 2>&1  # DEC-1141 (6), ACT-OPERATOR-HOURS-1 (was DEC-1104 (2) (5), ACT-OPERATOR-1): the operator agent launched from its queue every 10 minutes at every hour, except no launch from 02:10 and, from 03:10, none unless the night hold state file (under 5 minutes old) says holding false; missing or unreadable means none; needs ACT-OPERATOR-HOURS-2 first
```
Read it as: `h` is the local time as HHMM (`\%` is cron's escape for `%`). Launch when `h` is before 02:10 or from 08:00 (the state file is
not read at those hours); from 03:10 to 07:59, launch only when a small Python check exits 0 (the file exists, its age `a` is from -60 s to
300 s, it parses, and its `holding` is exactly `false`); from 02:10 to 03:09, never. Python's exit code is 1 on any exception, so every
failure (missing, empty, malformed, a directory, no `holding` key, null, 0, a string) is "no launch". The group's standard error goes to
`/dev/null`: a skip, or a `date` that fails, prints nothing, so cron has nothing to mail.

### Why these numbers
| Choice | Reason (M: read or measured here) |
|---|---|
| **The night hold's file is read only from 03:10 to 07:59** | M: `night_hold.py` writes `log/night-hold.state.json` every 60 s with `pid`, `at`, `holding`, `in_window`, `nightly` (atomic: `hold_lib.write_json_atomic`). `holding` is true from the hold's first look at or after 03:00 until the nightly has ended (a status line for today, a run folder with a verdict, or the restart log's end) or 07:30 at the latest, then false. **When the hold process is not running the file keeps its last content**; nothing marks it dead. A stale `holding: false` written at 02:59 would read as "free" at 04:00 if trusted: the age test closes that. Outside 03:10-07:59 a leftover `holding: true` must never stop the operator, so the file is not read there. |
| **Last launch before the hold: 02:00 (no launch from 02:10)** | The launcher's canary may take up to 300 s and the session up to 2700 s, plus 30 s to stop a group: 50.5 minutes in the worst case. A launch at 02:10 could end at 03:00:30, after the hold begins; 02:00 ends by 02:50:30. It is also HOURS-2's G9 boundary (`HOLD_FROM = (2, 10)`), so line and gate agree. |
| **No launch at 03:00 either (first state read at 03:10)** | The hold's loop may not yet have looked at 03:00:00; its file is then the 02:59 one (`holding: false`, fresh). Rehearsal case 96 plants exactly that. By 03:10 the hold has looked ten times. HOURS-2's `HOLD_READ_FROM = (3, 10)` is the same. |
| **The state must be from -60 s to 300 s old** | The hold looks every 60 s; 300 s allows four missed looks and still detects a dead hold within one cron tick. 60 s of future skew is allowed (a clock step); more is stale (F3). |
| **Fail closed only in the window** | Between 03:10 and 07:59 an unreadable state is "no launch". At every other hour the state is not read, so a broken hold cannot stop the operator in the day. |
| **`date` by name, `python3` by full path** | cron's PATH is `/usr/bin:/bin` and the table sets none, so `date` is `/usr/bin/date`. By name so the rehearsal runs the line byte for byte with a stub clock first in PATH. |
| **POSIX `sh`** | cron runs `/bin/sh` (dash) here (no `SHELL=` in the table). The same six cases pass under bash (case 100). |
| **No `%` but the two escaped ones** | cron turns an unescaped `%` into a newline; the rehearsal refuses any (case 107). |

## 3. Class and route
- **Class (b), a control path.** M: `governance/project/operator/class-rules.yaml`, row `crontab` (`root: crontab, path: crontab`):
  `class: b`, `control: true`. One touched file, the crontab. The operator's own `act_class.classify` (read only) on the bundle: **class b,
  hits `[]`, why `crontab:crontab`**. The path rule passes on `apply.sh` (it reads `$HOME/gov-os-operator/install/opcommon.py`, not the repository).
- **No helper script**: `governance/project/orchestration/tools/` is the catch-all row (class (O)), so a helper would raise the whole ACT to (O).
- **Route (the CTO prompt's section 7, P-ACT-SPLIT (b)): the CTO applies it by hand** on your ping reply naming the ACT, the reply recorded
  verbatim in `log/act-approvals.jsonl`. **Round 2: the operator agent cannot take it any more.** Its dry run plants a HOME without the
  install, so the gate would exit 7 there and G8 would fail; by hand, the CTO's HOME is the real one. That is intended: this ACT is meant
  for the CTO's hand, after HOURS-2.

## 4. The commands (the CTO, after your reply and after ACT-OPERATOR-HOURS-2, from 08:00 UTC, in the main tree)
```
bash .gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-1/apply.sh check     # exit 0: HOURS-2 is live, the live table is the before
bash .gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-1/apply.sh apply     # exit 0: the after installed (crontab <file>)
bash .gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-1/apply.sh verify    # exit 0: the live table is the after
```
**Exit 7** (check or apply): "ACT-OPERATOR-HOURS-2 is not applied: the install's opcommon.py is not its after copy (123e17e55811); apply it first;
check refused, nothing touched". It is also exit 7 when the file is absent, a link, a directory, or any other bytes (its before copy: the
file as it is live today; HOURS-2's after copy with one line added). The gate comes first, even over a table that is already the after.
Otherwise `apply.sh` decides by the table's sha256 alone: `apply` only over the before (or when it is already the after: nothing to do); over
any other table exit 3 and nothing touched; each frozen copy is hashed against `list.txt` first (exit 4). `crontab <file>` itself refuses a file it
cannot parse. **If HOURS-2 is rebuilt** (a new after hash for `opcommon.py`), the gate's hash is stale: rebuild this bundle
(`python3 -I drafts/operator-hours-1/build_act.py all`, read only on the live crontab, reads the hash from HOURS-2's `list.txt`) and take a new yes line.
If `check` says "moved: crontab", rebuild the same way.

## 5. The check line it must print
After the apply: `crontab -l | sed -n 7p` prints exactly the 887-character line of section 2 (it begins `*/10 * * * * h=$(date +\%H\%M 2>/dev/null);`
and ends `...needs ACT-OPERATOR-HOURS-2 first`), and `crontab -l | sha256sum` prints
`88cf08b165a184a23681b610ea07490c7c60559c6125fdba359db2a083d7c880`. The manifest's eleven checks all pass (four active lines; the new line
once; the old `*/10 0,8-23` schedule zero times; `operator_launch.py` once; the state file named once; the three other active lines and the
three stopped lines as they were). Within ten minutes `tail -2 /home/usain/gov-os-operator/log/operator-launch.out` shows a fresh
`"result": "idle"` line. **The first night is watched:** from 01:00 the file gains one line per 10 minutes; between 02:10 and the release of the
hold (`night-hold.jsonl`'s `release` event) it gains none.

## 6. Undo, and the rehearsal
```
bash .gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-1/apply.sh undo      # the before table put back, byte for byte (no gate)
bash .gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-1/apply.sh check     # exit 0 again, if HOURS-2 is still live
```
`undo` works only over the after (or when already the before); over a table that moved since it exits 3 and touches nothing.
**Rehearsal** (`rehearsal.log`, **119 cases, `failures: 0`**; no date, pid or head in it, so a rebuild gives the same manifest):
- **Parts 1 and 2, apply.sh** (HOME planted with HOURS-2's after `opcommon.py`) on a stub crontab, then in the operator's clean-environment
  form: check, verify (exit 3 before), undo when already the before, apply, byte equality, verify, apply again, the eleven manifest checks, undo
  over a moved after (exit 3), undo, check and apply over a moved table (exit 3, untouched), a tampered frozen copy (exit 4); the before and the
  after differ in the one line. **The gate (round 2), cases 27-34:** its hash is HOURS-2's after copy (its `list.txt`, both rows; its frozen
  copy hashes to it) and is in `apply.sh` in full; with the install's `opcommon.py` absent, HOURS-2's before copy (the live file today), the
  after copy with a line added, a link to the after copy, or a directory, `check` and `apply` exit 7 naming ACT-OPERATOR-HOURS-2 and the
  crontab is untouched; with it absent and the table already the after, `verify` exits 0, `apply` exits 7 and `undo` exits 0; with the after
  copy in place, check 0, apply 0, undo 0.
- **Part 3, the guard** (the line from the after table, as cron takes it, under `/bin/sh -c`; only the clock, the two path prefixes and the
  launcher are stubbed): the five cases you named: **holding true at 03:30: no launch; false: launch; file missing at 03:30: no launch; missing at
  14:00: launch; malformed JSON at 03:30 and 14:00: no launch, then launch.** And empty, `[false]`, no key, `"false"`, null, 0, `""`, a directory: no
  launch; a state 4 minutes old: launch; 6 minutes old: no launch; **F3: dated 30 s ahead: launch, 2 minutes and 1 day ahead: no launch;** a
  day-old `true` at 14:00: launch; `true` at 01:00: launch; the edges 02:00, 02:10, 03:00, 03:10, 07:30, 08:00; **F4: `date` failing with a
  message, and printing five kinds of garbage: no launch, nothing on either stream**; all 144 ticks of a day under three states against the old
  line (nothing it ran is lost; 138, 109 and 109 launch); the launcher's one call with no arguments and its log; the same six cases under bash.
- **Part 4, the real writer:** `night_hold.py`'s own `NightHold.step()` in a planted folder at fixed times (02:59:30 false, 03:00:20 true, 05:00
  released with today's status line, 06:00 true, 07:31 released by the limit, a writer stopped an hour ago): the guard follows each file.
- **Part 5:** `crontab -n` accepts the after table; a padded variant is refused; the live crontab is byte for byte as it began.
- **Does it bite?** I mutated the line and `apply.sh` and re-ran: the future test removed or widened to a day (cases 74-75 red), the group's stderr
  left open (3 red), `date`'s stderr left open (1 red), the state never read (49 red with the apply hash cases), the gate dropped from `apply` (6
  red), from `check` (5), its exit code 3 for 7 (6), the tamper test dropped (2), the link test dropped (1). Round 1's seven mutations are still caught.
- **Read only, not in the log:** at 03:32 UTC the guard on the real clock and the real hold file said "no launch" (the hold on); `apply.sh check` on
  the real HOME with a stub crontab exits **7** today, because the live `opcommon.py` is still HOURS-2's before copy.
- Not rehearsed: a real cron firing; a real launcher session; ACT-OPERATOR-HOURS-2's own apply.

## 7. What this ACT does not change; ACT-OPERATOR-HOURS-2 (was round 1's option B)
M: the launcher's gate G9 (`opcommon.holds`, hashed in the install's `APPROVED`: yours, class (O)) held a queued ACT through `QUIET` 02:00-07:30 and
`DEFAULT_NIGHTLY` 03:50-08:00, so this line alone gave back 01:00 to 01:59 only. ACT-OPERATOR-HOURS-2 (CTO's, manifest sha8 `d3d29237`) replaces them:
G9 holds from 02:10 to 03:09 always, and from 03:10 to 07:59 unless the hold's state is under 300 s old and `holding` is exactly `false`; the
`NIGHTLY-RUNNING` flag, the close queue, the CTO's freeze, the operator's own freeze and an unreadable clock still hold. With both applied the
operator agent runs every hour but the hold's, as DEC-1141 (6) says; this ACT's gate makes the two go in that order.

## 8. Files and hashes
| File (`acts/ACT-OPERATOR-HOURS-1/`) | sha256 |
|---|---|
| `before/crontab/crontab` (the live table at the build) | `c613d523f7edb4ee1214f2b5c495727c67c060db702e090cf7718c3b9db690c7` |
| `after/crontab/crontab` | `88cf08b165a184a23681b610ea07490c7c60559c6125fdba359db2a083d7c880` |
| `apply.sh` | `3ca208016bbe157a2a1b72fdd5434424262935e54ef9be6c0a8d5937744c074c` |
| `list.txt` | `46d347eda4ce5cd6e02c65a5e4ad4dd6867f88f8b1f751a2afe7ac7b54ef9d39` |
| `rehearsal.log` | `866325d9177ab46172324766e7565429ddaa9cc2e6e8e576ba3cd6015aafea13` |
| **`manifest.json`** | **`9cbccb8288a7475dff7a63241ed1eeaf78771f50cf415e90d5ed1a3b9b80485f`** |

The gate's pin: `123e17e5581149725c75babaa9200a09c4854254053df14105b6ce17450bbc87` (HOURS-2's after `opcommon.py`; its manifest
`d3d292378b7bda8c4339fcbcaa77025a53dd40b91aefad0eef8a686f3ad8e6f2`). The operator's own code on the bundle (`build_act.py gates`, read
only): `validate_manifest` pass; 5 files hash as the manifest says; the path rule passes on `apply.sh` and every check; `act_class.classify`: class b,
no script hits. Built with the repository at head `9bbef27f1d05` (not in the manifest: the bundle does not depend on the repository).

## 9. Risks, review state, what I did not do
**Review state:** round 1 (the independent auditor): not ready on F1; rows F2-F6 (section 1). **Round 2: not yet independently reviewed**, and it is
the last round (DEC-1010); the rehearsal is mine.
1. **F1's residual:** a run begun at 02:00 whose G1-G8 take more than 10 minutes strands in G9 and is killed at 2700 s with its request thrown away
   (the runner's existing behaviour). Measured 1-3 s in six runs; a manifest with slow checks is the exposure.
2. **F2:** 07:30-07:50 the line calls the launcher while a nightly may still run; G9's `NIGHTLY-RUNNING` flag holds it. The line does not read the flag.
3. **F5:** a dead night hold means no launches from 03:10 to 07:59 and no lead-start hold; nothing restarts it after a reboot.
4. **The line and HOURS-2's G9 differ on a future-dated file** (F3 note): the line is the stricter.
5. **The gate pins HOURS-2's hash:** any rebuild of HOURS-2's `opcommon.py` makes `apply.sh` refuse (exit 7) until this bundle is rebuilt; fail closed.
6. **A session begun before 02:10 may still be applying after it** (G9 is checked before the apply, not during): a launch at 02:00 can run to about 02:50.
7. **A dead hold stops the launches from 03:10 to 07:59** (as the old line did all night); the guard reads the main tree's scratch path; if the
   folder moves it fails closed in the window.
8. **The line is 887 characters.** `crontab` refuses a command past about 1000 and leaves the old table: a later edit that lengthens the comment is
   refused, not truncated (case 118).
9. **cron's `date` is found by PATH** (the table sets none today); local time everywhere (Europe/London, equal to UTC now), no UTC assumed.
10. **`crontab -n` cuts a file name at about 100 characters** (found while rehearsing): use a short relative name.
11. **The operator-launch.out grows by 42 lines a day** (144 launches against 102).

## 10. Note (not built): a stand-alone variant with the cutoff at 01:10
For the case where ACT-OPERATOR-HOURS-2 is not wanted, or not yet applied, and this crontab line should stand alone with the launcher's G9 as it is
today (quiet hours 02:00-07:30, nightly window 03:50-08:00): the same line with `0210` written `0110`, and no gate in `apply.sh`.
- **Why 01:10:** with G9 holding from 02:00, a run strands if its G9 comes after 02:00. The last launch is then 01:00, and the worst case (canary 300 s,
  session 2700 s, 30 s to stop) ends at 01:50:30, before 02:00, so no run can reach G9 inside the quiet hours, and none applies after 02:00.
  Round 1's F1 cannot happen at all, whatever the dry run's length.
- **What it gives:** the launches at 00:00-01:00 and from 08:00. Against the old line (last launch 00:50) it adds the 01:00 tick only. From 03:10 the
  state read is moot (G9 holds to 08:00 anyway) but harmless.
- **What it does not give:** the hours DEC-1141 (6) asks for between 01:10 and the nightly's end; that needs HOURS-2.
- **To build it:** `build_act.py`: the `0210` in `GUARD` to `0110`, the gate block out of `APPLY`, the rehearsal's edge cases (02:00 launch, 02:10 none) moved
  to 01:00 and 01:10, a new manifest and yes line. About 20 minutes and one more review round (E). I did not build it.

## 11. Placeholder scan
`python3 .gov-runtime/scratch/orchestrator/tools/placeholder_scan.py drafts/operator-hours-1/ACT-OPERATOR-HOURS-1.md`: 0 hits (run at the end of the helper's work).
