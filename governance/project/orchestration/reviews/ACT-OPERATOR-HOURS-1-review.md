# Review: ACT-OPERATOR-HOURS-1 (manifest `d993275aâ¦3aee`)

task: ACT-OPERATOR-HOURS-1
decisions: DEC-1141, DEC-1104, DEC-1138, DEC-1058, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1073
reviewer: independent auditor, fresh, read-only. HEAD at the end was `9bbef27f1d05`; the bundle does not depend on HEAD.

## Checks
1. **Hashes: match.** All six files match the package, `list.txt` and the manifest. The live `crontab -l` is `c613d523â¦`, the same as `before/`, and was unchanged at the end. `before/` and `after/` differ in line 7 only.
2. **Guard: fails closed for the nightly.** 86 cases under `/bin/sh` (dash) and the same under bash, with a stub `date` and a planted state file in a temp folder. Clock edges at 02:00, 02:09, 02:10, 03:00, 03:09, 03:10, 07:30, 07:59 and 08:00; missing, empty, malformed, wrong-type, directory and symlink states; stale (301 s and a day old) and fresh (299 s). Every decision was right. `crontab -n` (Debian dry run) accepts the after table.
3. **G9.** The quiet hours are 02:00 to 07:30 and the default nightly window is 03:50 to 08:00, so queued ACTs are applied only from 08:00 to 01:59, as the package says. But a launch at 01:10 to 01:50 can strand in the run's own G9 wait (F1). The ACT is safe for the nightly on its own; the only clean gain is the 01:00 tick.
4. **Class (b): right.** `class-rules.yaml`'s `crontab` row gives b and control. P-ACT-SPLIT (b): the CTO applies it on the owner's reply, from 08:00.

Classification: 1 blocking (F1: in scope, ordinary work yes, loses work); 5 rows (F2 to F6: other).

## Findings
- **F1** (scope in). A launch at 01:40 or 01:50 takes a queued ACT, passes the launcher's G9, and moves the request to `taken`. The session reaches its own G9 after 02:00 (the quiet hours, DEC-1104 (2)) and waits with no limit (`hold_max_s` 0) until the launcher kills it at 2700 s. The request is moved to `done` unapplied; no journal, no notice, no digest entry. It should not launch when its worst-case run crosses G9's earliest hold. The old last launch at 00:50 existed for this.
  Ordinary work: yes, because DEC-1141 (6) is for the operator to work at night, and an ACT waiting for the 01:40 or 01:50 tick is ordinary.
  Consequence: loses work.
  Reversed by: the live `hold_max_s` above 0; or a returned request or a notice for a killed session; or a rule keeping queued ACTs out of 01:00 to 02:00.
- **F2** (scope in). The hold releases at 07:30 even when the nightly still runs, so the launcher is called at 07:30 to 07:50. G9 holds queued ACTs, but journal recovery runs before G9.
  Ordinary work: no, because harm needs a session killed mid-apply in the night and a nightly running past 07:30.
  Consequence: other.
  Reversed by: evidence that recovery cannot run with NIGHTLY-RUNNING present.
- **F3** (scope in). A state file whose time is in the future (the clock stepped back after the hold died having written false) reads as fresh, and the guard launches.
  Ordinary work: no, because it needs a dead hold plus a backward clock step.
  Consequence: other (G9 still holds).
  Reversed by: an ordinary backward clock step on this host combined with a G9 gap.
- **F4** (scope in). When `date` fails, the shell writes "Illegal number" to stderr and no launch happens at any hour.
  Ordinary work: no, because `date` failing means a broken system.
  Consequence: other.
- **F5** (scope in). Nothing restarts the night hold after a reboot, so no launch from 03:10 to 07:59. It fails closed and is the package's risk 2.
  Ordinary work: yes, because reboots happen.
  Consequence: other.
- **F6** (scope in). The package is still in `drafts/`, not `packages/` (P-ACT-SPLIT step 1), and section 9 says it has not been reviewed.
  Ordinary work: yes, because it is the ordinary filing step.
  Consequence: other.

## Recommendation
Rebuild with the first threshold at `0110` while G9's quiet hours start at 02:00, or decide option B with this ACT and keep `0210`. Then re-run the rehearsal, recompute the hashes, file the package under `packages/`, and send it for a second review round.

## Unverified
The live `~/gov-os-operator/install` hashes and config (`hold_max_s`, `nightly_window`). The read was refused under the quiet-hours rule and not retried; the repository `opcommon.py` matches the package's `e392d8a0e177`.

## Round 1: the reviewer's verdict block (as returned)

```verdict
{"kpis": [{"kpi": "act-operator-hours-1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```


# ACT-OPERATOR-HOURS-1: independent review, round 2 (the last round)

- **task:** ACT-OPERATOR-HOURS-1. Manifest `9cbccb8288a7475dff7a63241ed1eeaf78771f50cf415e90d5ed1a3b9b80485f`. Class claimed b, class found **b**.
- **Reviewer:** a fresh independent-auditor session, read only, author of none of the bundle. 2026-11-12, about 03:40 to 04:00 UTC. Head `9bbef27f1d05`; tree clean at the end.
- **decisions:** DEC-1141 (6), DEC-1104 (2) (5), DEC-1138 (3), DEC-1010, DEC-801, DEC-808, DEC-1014, DEC-1073, DEC-136.
- **Verdict:** **pass**.

## What I probed and found sound
- **Hashes:** all six files and the manifest match the package and `list.txt`. `before/` equals today's `crontab -l` (`c613d523f7ed`). `after/` differs only at line 7, which is 887 characters. The gate's pin equals HOURS-2's after copy of `opcommon.py`; the live file is still HOURS-2's before copy (`e392d8a0e177`), so the gate refuses today.
- **Gate, on a scratch copy with a stub crontab and a planted HOME:** `check` and `apply` exit 7 with the table untouched when the file is absent, the before copy, tampered, a link to the after copy, a directory, empty or unreadable. With the after copy, `check`, `apply`, `verify`, `apply` again and `undo` behave as stated, and the tables match byte for byte. `verify` and `undo` work with the gate's file absent. A moved table gives exit 3.
- **Guard, the line as cron takes it, on a stub clock and planted state:**
  - The five round-1 cases pass.
  - Every odd body holds: empty, `"false"`, null, 0, `[false]`, no key, NaN, a BOM, a directory.
  - Ages: 299 s and 4 minutes launch; 301 s and 6 minutes do not.
  - F3: +30 s and +59 s launch; +61 s, +2 minutes and +1 day do not.
  - The edges 02:00, 02:09, 02:10, 03:00, 03:09, 03:10, 07:30, 07:59 and 08:00 behave as stated.
  - F4: a failing `date` or garbage output gives no launch and both streams stay empty.
  - The same results under bash.
  - All 144 ticks give 138, 109 and 109 launches with nothing lost against the old schedule.
- **`crontab -n`** accepts both tables. No unescaped `%`.
- **Clocks:** the line and G9 both use local time (Europe/London).
- **Timings (`operator.jsonl`):** cron tick to G9 was 10 to 26 s in all seven real runs. All 27 manifests on the machine have only short checks.
- **Launcher:** G9's holds are checked before the canary and before any session.
- **Class and route:** class b (`class-rules.yaml`, row `crontab`). The CTO applies it by hand after HOURS-2.

## Findings
| id | finding (behaviour) | scope | ordinary work | consequence | reversed by |
|---|---|---|---|---|---|
| R2-F1 | A run launched at 02:00 that spends more than about 9.5 min before G9 waits in the 02:10-03:09 hold until the 2700 s timeout; its request is thrown away unapplied | in | no: measured 10 to 26 s in seven runs; no slow checks | loses work | a real run with tick-to-G9 over about 5 min, or slow checks sent to the operator |
| R2-F2 | The package says the gate closes F1; the margin is the same 10 min as in round 1 (01:50 against 02:00, because the 02:00 tick is held at the launcher's own check). The closure is a judgement on measured timings; only the 0110 variant closes it structurally | in | yes: every reader relies on it | other | the old launcher starting a session at the 02:00 tick |
| F2 | From 07:30 the line calls the launcher while a nightly may still run; the launcher holds on `NIGHTLY-RUNNING` | in | no: the nightly starts well before 07:30 and the flag covers it | fails open | a nightly after 07:30 without the flag |
| F3-note | For a file dated more than 60 s ahead the line says stale and G9 says fresh; the line is the stricter | in | no: needs the clock to step back while the writer is down | other | another path that starts a session from 03:10 to 07:59 |
| F5 | Nothing restarts the night hold after a reboot; the line fails closed from 03:10 to 07:59 | out | yes | other | the line launching while the hold is dead |
| R2-F3 | If HOURS-2 is undone after this ACT, the line stays; the launcher's check holds the 02:00 and 03:10-07:59 ticks; exposure back to round 1's size | in | no: a deliberate owner undo | other | a session started under the old G9 at 02:00 or from 03:10 to 07:59 |
| R2-F4 | Round 1's full record is not filed, only a 397-byte summary | in | yes | other | the record filed elsewhere |

Classification: 7 findings, 0 blocking. R2-F1, F2, the F3 note and R2-F3 are in scope but not ordinary work. R2-F2 and R2-F4 are ordinary work with consequence other. F5 is out of scope.

## Recommendation
Take it to the owner with ACT-OPERATOR-HOURS-2 as it stands, and show R2-F2. If the owner holds round 1's reading of the 10-minute margin, section 10's `0110` variant is the structural option, at the cost of the hours between 01:10 and the nightly's end. No new round (DEC-1010, DEC-802).

## Limits
- My Read of the operator's `install/brief.md` was refused by the quiet-hours rule. I did not retry it.
- Not probed: a real cron firing, a real launcher session, HOURS-2's own apply.

## Round 2: the reviewer's verdict block (as returned)

```verdict
{"kpis": [{"kpi": "act-operator-hours-1", "verdict": "pass", "findings": [{"id": "R2-F1", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}, {"id": "R2-F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3-note", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2-F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R2-F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
