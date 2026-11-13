# ACT-OPERATOR-HOURS-3: the operator agent applies ACTs at night again, now that the night hold is removed (DEC-1157 (2))

- **For:** the owner (one yes line), then **Part A** the CTO by hand (the crontab, class (b)) and **Part B** the owner's operator by hand
  (the operator's own install and four repository paths, class (O), as ACT-OPERATOR-HOURS-2 was). About five minutes in all. The final rehearsal ran without the heavy slots (section 6, parts 6 and 7).
  Nothing is committed by the script; the owner's operator makes **two commits** for Part B (the four paths, then the path map's
  exemption entry for the first, DEC-1136 (2)).
- **By:** an ACT-preparation helper of the CTO (Sonnet-class work), 2026-11-13 from about 00:15 UTC. **Nothing live was changed or
  started:** no write under `~/gov-os-operator`, no crontab write, no commit, no stage, nothing in the main tree's tracked files. Built
  and rehearsed on a stub crontab, planted folders and clones under the helper's own TMPDIR (section 6). **Not yet independently
  reviewed** (section 9, item 1).
- **Under:** **DEC-1157 (2)** (the owner, 2026-11-12 ~23:40: "The night hold is removed: no lead start and no landing is held for the
  nightly ... The operator agent's cron line (DEC-1141 (6)) still reads the night-hold state file after 03:10: its change is a crontab
  ACT (class (b)) to the owner; until then the operator does not launch from 02:10 to 08:00"); **DEC-1141 (6)** (the rule HOURS-1 and
  HOURS-2 built, which this ACT retires); **DEC-1104** ((2) the operator's hours, (4) its own install is the owner's, by hand). DEC-1136 (2):
  the exemption entry. The manifest's `dec`: "DEC-1157, DEC-1141 (6), DEC-1104".
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/operator-hours-3/` (`build_act.py`: build, rehearse, finalize, gates; `part7.py`:
  the exempt stage on a clone; `apply.sh`; `code/`: the after files and the two crontabs). **The bundle:**
  `.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-3/`.

## 0. The short version, the yes line, and the steps
1. **Part A, the crontab's line 7 (class (b), the CTO's):** the operator is launched from its queue **every 10 minutes at every hour**,
   with **no time window and no night-hold state file read**. Only the line's schedule guard goes: the launcher command and the log redirect
   are byte for byte the old ones; the trailing comment cites DEC-1157 (2) and ACT-OPERATOR-HOURS-3. The six other lines are untouched.
2. **Part B, G9 (class (O), the owner's operator's):** G9's two time holds are removed (02:10 to 03:09 always; 03:10 to 07:59 unless the
   night-hold state file is fresh and says `holding: false`). **Every other G9 hold stays exactly**: the NIGHTLY-RUNNING flag, an explicit
   `nightly_window` (none by default), the close queue, the CTO's `log/act-in-progress.txt`, the operator's commit freeze, a clock it cannot
   read. Two install files (`opcommon.py`, `APPROVED`'s one line) and four repository paths (the same `opcommon.py`; G9's acceptance test and its
   README; the unit file for G9's hours), then the path map's entry.
3. **Why both:** today the night hold's state file is no longer refreshed (`night_hold.py` stopped, DEC-1157 (2)); it says `holding: false` but
   is stale (last written 2026-11-12 23:39), so the crontab guard skips every tick from 02:10 to 07:59 and G9 would hold anyway. Part A alone:
   the launcher runs at night but G9 holds every queued ACT ("held", the request stays in `queue/`). Part B alone: G9 would let it through but cron
   never calls the launcher from 02:10 to 07:59. **Both are needed** for an ACT to be applied tonight.
4. **Order: none required; each alone is safe** (section 4). Suggested: Part B first (the owner's operator), then Part A (the CTO), or together.

**The owner's line: `yes ACT-OPERATOR-HOURS-3 716da9dc`** (the first 8 digits of the manifest's sha256, section 8). It covers both parts.

**Part A, the CTO, after the review and that yes** (any minute but a :x0 minute; nothing else needed):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-3
bash $G/apply.sh A check     # exit 0: "check A: ready to apply (the crontab is the before)"
bash $G/apply.sh A apply     # exit 0: "apply A: crontab", "state applied (A)"
bash $G/apply.sh A verify    # exit 0: "verify A: the crontab is the after"
crontab -l | sed -n 7p       # "*/10 * * * * /usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> ... 2>&1  # DEC-1157 (2), ACT-OPERATOR-HOURS-3 ..."
```

**Part B, the owner's operator, by hand,** in the main tree, not at a :x0 minute (the cron's launch), with nothing queued for the operator.
Before step 1 tell the CTO "starting HOURS-3"; the CTO writes `log/act-in-progress.txt` and makes no commit and no land on `w2/integrate` until
you send both commit ids (so nothing lands between the two commits). **Step 1, the install and the first commit:**
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-3
bash $G/apply.sh B check     # exit 0: "check B: ready to apply ..." (every listed file is the before; the operator holds nothing)
bash $G/apply.sh B apply     # exit 0: six lines "apply: ...", "the install's own APPROVED check: ok", "APPROVED ff3579ff...", "state applied (B)"
bash $G/apply.sh B verify    # exit 0: "verify B: every listed file is the after ..."
sha256sum ~/gov-os-operator/install/APPROVED    # expect ff3579ff5abd13f54c8c5b844db5baa23d97f8372dd7ea84f01b3a93c9809114
git status --short -- governance/project/operator/opcommon.py tests/acceptance/W2-148/test_w2_148_gates.py tests/acceptance/W2-148/README.md tests/unit/operator/test_act_operator_hours_2.py    # 4 lines " M"
git add governance/project/operator/opcommon.py tests/acceptance/W2-148/test_w2_148_gates.py tests/acceptance/W2-148/README.md tests/unit/operator/test_act_operator_hours_2.py
git commit -m "ACT-OPERATOR-HOURS-3: G9 has no time hold; the night hold's hours 02:10 to 07:59 gone (DEC-1157 (2))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1157" --trailer "Role: owner" -- governance/project/operator/opcommon.py tests/acceptance/W2-148/test_w2_148_gates.py tests/acceptance/W2-148/README.md tests/unit/operator/test_act_operator_hours_2.py
```
**Step 2, straight after step 1: the second commit, the path map's exemption entry for the first (DEC-1136 (2)).** Nothing else is committed between the two:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-3
bash $G/apply.sh B exempt           # exit 0: "exempt: added the entry for <12 digits>", then "exempt-verify: the map is the allowed before (sha256 805bd918d467) plus exactly the entry ..."
git diff --numstat -- governance/project/path-map.yaml   # expect: 2  0  governance/project/path-map.yaml
H=$(git rev-parse HEAD)
git add governance/project/path-map.yaml
git commit -m "ACT-OPERATOR-HOURS-3: acceptance_exemptions lists its own commit ${H:0:12} (DEC-1136 (2))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1136, DEC-1157" --trailer "Role: owner" -- governance/project/path-map.yaml
bash $G/apply.sh B exempt-verify    # exit 0: the committed map is the allowed before plus exactly the entry
```
Send the CTO both commit ids (12 digits) and the last line; the CTO then removes `log/act-in-progress.txt`. **Between the two commits W1-01 is red**
(the control in section 6, part 7): do not stop or merge in between. If `B check` stops (exit 3: a file moved; exit 4: a frozen copy altered;
exit 6: the operator is busy), send its line to the CTO and apply nothing (exit 6: wait and run it again). If `B apply` stops part way (a full disk, a
kill), run it again: it finishes. If `B exempt` refuses (exit 3) or cannot write (exit 5), nothing is touched: send its line to the CTO.
**Undo:** section 5.

## 1. Why
DEC-1157 (2) removed the night hold: the CTO stopped `tools/night_hold.py`, so `log/night-hold.state.json` keeps its last content
(`holding: false`, `at` 2026-11-12 23:39:28, M: read 00:25 UTC) and is no longer refreshed. Both places that make the operator sleep read that file
and fail closed on a stale one:
- **the crontab's line 7** (ACT-OPERATOR-HOURS-1, applied; M: `crontab -l` line 7): no launch from 02:10 to 03:09, and from 03:10 to 07:59 none unless
  the file is under 300 s old (and not over 60 s in the future) and says `holding` false;
- **G9** in `~/gov-os-operator/install/opcommon.py` `holds()` (ACT-OPERATOR-HOURS-2, applied; M: install `opcommon.py` `123e17e55811` = the tree's,
  `APPROVED` `1e557c49be58`): the same two holds.
So from 02:10 to 07:59 every night the operator applies nothing, which DEC-1157 (2) names ("until then the operator does not launch from 02:10 to
08:00") and the owner wants gone ("to land tonight if it is ready, since the night hold it waits on is gone"). The rehearsal's part 3 shows the old G9
holding at 02:30 in every state and at 05:10 with the file missing or stale.

## 2. What changes
### Part A: the crontab (line 7 only)
Before (ACT-OPERATOR-HOURS-1's line; the crontab `88cf08b165a1`):
```
*/10 * * * * h=$(date +\%H\%M 2>/dev/null); { [ "$h" -lt 0210 ] || [ "$h" -ge 0800 ] || { [ "$h" -ge 0310 ] && /usr/bin/python3 -I -c '...night-hold.state.json...'; }; } 2>/dev/null && /usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> /home/usain/gov-os-operator/log/operator-launch.out 2>&1  # DEC-1141 (6), ACT-OPERATOR-HOURS-1 (...): ...; needs ACT-OPERATOR-HOURS-2 first
```
After (the crontab `72f1106f7a0c`):
```
*/10 * * * * /usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> /home/usain/gov-os-operator/log/operator-launch.out 2>&1  # DEC-1157 (2), ACT-OPERATOR-HOURS-3 (was DEC-1141 (6), ACT-OPERATOR-HOURS-1; DEC-1104 (2) (5), ACT-OPERATOR-1): the operator agent launched from its queue every 10 minutes at every hour; no time window and no night-hold state file read (the night hold is removed); the launcher gate G9 still holds while the nightly runs (NIGHTLY-RUNNING) and for its other holds
```
The command after the schedule is the old line's text after its `&&`, byte for byte (the rehearsal checks it). No `%` (cron would cut the line), no quote.
`crontab -n` accepts it. Lines 1 to 6 and the final newline are unchanged.

### Part B: G9 (`opcommon.py`, 741 lines to 709; sha256 `123e17e55811` to `c7ec467c5691`)
The install's copy and the repository's are the same bytes before and after. The whole diff (the code part):
```diff
-# G9 holds only while the night hold is on (DEC-1141 (6), ACT-OPERATOR-HOURS-2; ...) ... (5 comment lines)
-HOLD_FROM = (2, 10)
-HOLD_READ_FROM = (3, 10)
-HOLD_END = (8, 0)
-NIGHT_HOLD_MAX_AGE_S = 300
-DEFAULT_NIGHTLY = None              # no fixed nightly window by default; the NIGHTLY-RUNNING flag and the night hold say when
+# G9 has no time hold (DEC-1157 (2), ACT-OPERATOR-HOURS-3: ...) ... (4 comment lines)
+DEFAULT_NIGHTLY = None              # no fixed nightly window by default; the NIGHTLY-RUNNING flag says when the nightly runs
 ... in load_settings:
-    # DEC-1141 (6): the night hold's state file (night_hold.py writes it every 60 s: pid, at, holding, in_window, nightly)
-    s["night_hold_state"] = os.path.abspath(os.path.expanduser(
-        conf.get("night_hold_state") or os.path.join(s["scratch"], "log/night-hold.state.json")))
-    s["night_hold_max_age_s"] = float(conf.get("night_hold_max_age_s") or NIGHT_HOLD_MAX_AGE_S)
 ...
-def night_hold_reasons(s):  ... (18 lines: the fail-closed reader of the state file)
 def holds(s):
-    """G9's holds now, as a list of reasons (empty: no hold). Fails closed: a clock it cannot read is a hold."""
+    """G9's holds now, as a list of reasons (empty: no hold). No time hold (DEC-1157 (2)). Fails closed: a clock it
+    cannot read is a hold."""
 ...
-    t = d.hour * 60 + d.minute
-    if HOLD_FROM[0] * 60 + HOLD_FROM[1] <= t < HOLD_READ_FROM[0] * 60 + HOLD_READ_FROM[1]:
-        out.append("before the night hold (02:10 to 03:09: no session starts that could run into it)")
-    elif HOLD_READ_FROM[0] * 60 + HOLD_READ_FROM[1] <= t < HOLD_END[0] * 60 + HOLD_END[1]:
-        out.extend(night_hold_reasons(s))
```
The rest of `holds()` (the nightly window, NIGHTLY-RUNNING and its 6-hour age, the close flag, the CTO's freeze, the operator's freeze) is unchanged
byte for byte. No other code reads the removed names (M: grep over `governance/project/operator/`, `tests/`; `operator_run.py` and
`operator_launch.py` call only `holds()`). The live `operator-settings.json` names neither removed setting (M: its keys are `calls`, `claude`,
`home`, `repo`); a settings file that still named them would be ignored (`load_settings` reads only the keys it knows).
`APPROVED`: the one line `123e17e5...  opcommon.py` becomes `c7ec467c569126d803046ad7ca0e883d19d69a8f03bca17ffdd615a815981f7f  opcommon.py`; `APPROVED`
itself `1e557c49be58` to `ff3579ff5abd`. The thirteen other install files are untouched (`keep.txt`).

### Part B: the tests (each a test designer's revision, written from DEC-1157 (2) and the kept holds, not from the new code)
- **`tests/unit/operator/test_act_operator_hours_2.py`** (the unit file for G9's hours; the name kept: it is the file the tree knows; 86 cases to
  232): every case that asserted a time hold is replaced. It now asserts: the constants, the reader and the two settings are gone; **no hold at any
  of 23 times from 00:00 to 23:59 (02:10, 02:30, 03:09, 03:10, 05:10, 07:59 among them) in any of 9 file states** (true, false, missing, stale
  true, stale false, malformed, empty, `"false"`, a directory); no hold with no file at all; `holds()` never opens or stats the state file (a spy);
  **the kept holds at night and by day**: a fresh NIGHTLY-RUNNING at 02:30, 05:10, 08:30, 14:00 (and a 7-hour-old one does not hold), the close
  queue, the CTO's and the operator's `act-in-progress.txt` at 01:30, 02:30, 05:10, 14:00, an explicit `nightly_window` (none by default), an
  unreadable clock; **the real launcher** takes the request at 02:30 and 05:30 with the file missing, false, true or stale, and holds at 05:30 on a fresh
  NIGHTLY-RUNNING; **the real run** applies at 02:15 and 05:30 with G9's one line `pass`, and waits at G9 while NIGHTLY-RUNNING is fresh, then applies
  once it is removed.
- **`tests/acceptance/W2-148/test_w2_148_gates.py`** (S13): the `HOLDS` cases `before-the-night-hold` and `night-hold-on` (HOURS-2's) are replaced by
  `nightly-running` (05:30, a fresh `NIGHTLY-RUNNING`, cleared by removing it: the kept hold the night now relies on); a new test
  `test_s13_g9_no_time_hold_at_night` (02:30 with no state file; 05:30 with a fresh `holding: true`): the run applies and none of its G9 lines is `held`.
  The other three `HOLDS` cases (the nightly window, the close queue, the CTO's `act-in-progress.txt`) are unchanged.
- **`tests/acceptance/W2-148/README.md`**: the settings paragraph (the night hold's hours and the two settings gone) and S13's row (now two rows).

## 3. Class and route (M: `governance/project/operator/class-rules.yaml`)
| Path | Row | Class |
|---|---|---|
| crontab `crontab` (Part A) | `crontab` (control) | **b** |
| repo `governance/project/operator/opcommon.py` | `operator-own` | O |
| home `gov-os-operator/install/opcommon.py`, `.../APPROVED` | `operator-own` | O |
| repo `tests/unit/operator/test_act_operator_hours_2.py`, `tests/acceptance/W2-148/test_w2_148_gates.py`, `.../README.md` | `unknown` (the catch-all) | O |
| repo `governance/project/path-map.yaml` (`acceptance_exemptions`, by `apply.sh B exempt`) | `path-map`, a ratchet list (`ratchet_class: O`) | O |

`act_class.classify` on the whole bundle votes **O** (Part B's rows); on Part A's rows and checks alone **b**; on Part B's alone **O** (`build_act.py gates`,
section 8). The manifest's top-level `claimed_class` is "O" (the strictest; `validate_manifest` needs one) and `parts.A.claimed_class` "b", `parts.B.claimed_class` "O".
Route: **Part A** the CTO applies by hand after one independent review and the owner's yes (as ACT-OPERATOR-HOURS-1). **Part B** the owner's operator
applies by hand (the operator agent cannot apply its own install: rule 2d, `APPROVED`, G6 refuses (O)); no queue request for either part.

## 4. Order: none required; either part alone is safe
| Applied | What the operator does at night | Why it is safe |
|---|---|---|
| **neither (today)** | cron skips 02:10 to 07:59 (stale file); G9 would hold too | as now |
| **Part A alone** | cron calls the launcher every 10 minutes all night; with a request queued, G9 (HOURS-2's) holds it: `"result": "held"`, the request stays in `queue/`, a `G9 held` line in `operator.jsonl` each tick; with none queued, `"idle"` | M (`operator_launch.py`): a G9 hold logs and returns before the wall, the canary or a session; it sends no notice. Nothing is applied that was not before. |
| **Part B alone** | cron still skips 02:10 to 07:59 (the stale file), so G9's new rule is never reached at night by cron; by day nothing changes (neither rule held by day) | M: part 3's table, old against new: the only cases that change are in 02:10 to 07:59, where cron does not call the launcher; a launch by hand at night would go on (intended). |
| **Both** | the launcher every 10 minutes at every hour; a queued ACT is applied at night unless a kept hold holds it (NIGHTLY-RUNNING above all) | DEC-1157 (2)'s intent; the risks in section 9. |

ACT-OPERATOR-HOURS-1's `apply.sh` gate (it refused unless HOURS-2 was applied) is not repeated here: the two parts are independent, and each
`check` fixes its own before (Part A the crontab `88cf08b165a1`, Part B the install's `opcommon.py` `123e17e55811` and `APPROVED` `1e557c49be58`).

## 5. The check line, and the undo
After both parts: `apply.sh A verify` and `apply.sh B verify` exit 0; `crontab -l | sed -n 7p` is the after line; `sha256sum ~/gov-os-operator/install/APPROVED`
prints `ff3579ff5abd13f54c8c5b844db5baa23d97f8372dd7ea84f01b3a93c9809114`; the next launch's line in `~/gov-os-operator/log/operator-launch.out` carries
`"approved_sha256": "ff3579ff5abd..."`. The manifest's eleven checks (six for Part A, five for Part B) pass (rehearsed on the stub crontab and the
planted install). **The first night is watched:** a request queued after 02:10 is taken at the next :x0 tick (a `launch` line in `operator.jsonl`, no
`G9 held` line) unless NIGHTLY-RUNNING is fresh (then `G9 held` "the nightly runs (NIGHTLY-RUNNING)" until the nightly ends).

**Undo Part A** (the CTO): `bash $G/apply.sh A undo` (exit 0, "state before (undone) (A)"), then `bash $G/apply.sh A check` exits 0 again: the crontab is
ACT-OPERATOR-HOURS-1's byte for byte.

**Undo Part B:**
- **Before step 1's commit:** `bash $G/apply.sh B undo`, then `bash $G/apply.sh B check` exits 0.
- **After the first commit, before the second** (`bash $G/apply.sh B exempt-undo` first if the map was changed): with `A` the first commit's full id (step 2's `H`),
  while the CTO holds: `test "$(git rev-parse HEAD)" = "$A"`, then `git reset --keep "$A~1"`, check `git rev-parse ORIG_HEAD` is `$A`, then `bash $G/apply.sh B undo`.
- **After both commits, while HEAD is still the second one** (nothing committed on top; `exempt-verify` exits 0 only then), while the CTO holds:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-3
bash $G/apply.sh B exempt-verify  # exit 0: HEAD is the exemption commit, directly on the ACT's commit (otherwise stop: below)
A=$(git rev-parse HEAD~1)         # the ACT's commit (exempt-verify has checked it: subject, Role: owner, the four paths, the after blobs)
X=$(git rev-parse HEAD)           # the exemption commit
git reset --keep "$A~1"           # both commits out of the branch, to the ACT commit's parent, by id
test "$(git rev-parse ORIG_HEAD)" = "$X" || { git reset --keep ORIG_HEAD; echo "STOP: restored; tell the CTO"; false; }
bash $G/apply.sh B undo           # the install's two files back (the repository files are already the before)
bash $G/apply.sh B check          # exit 0: ready to apply again
```
- **After other commits landed on top:** do not revert and do not `B undo` and commit: either changes `tests/acceptance/W2-148/` as an unlisted owner
  commit (W1-01 red). Tell the CTO: the undo is then an ACT of its own with its own exemption entry (DEC-1136 (2)).
**By hand** (only if `apply.sh` cannot run): `crontab .../before/crontab/crontab` for Part A; for Part B `before/home/gov-os-operator/install/opcommon.py` then
`.../APPROVED` over the install's two files (nothing queued, no launch running), `before/repo/...` over the tree's four files.

## 6. The rehearsal (DEC-1057): `rehearsal.log`, 120 cases, ends `failures: 0`
`python3 -B drafts/operator-hours-3/build_act.py rehearse` (planted folders and clones under the helper's TMPDIR, not under the repository or
`~/gov-os-runs`). The live install, crontab, four repository paths and path map are hashed before and after: unchanged (the last three cases).
- **Part 1, Part A on a stub crontab (cases 1 to 30):** a `crontab` on PATH that reads and writes a file (`-l`, and `-` by standard input, checked by the real
  `crontab -n -`), seeded with the live bytes. `A check` ready; `A verify` exit 3 before; `A undo` on the before a no-op; an unknown step or no part: exit 2;
  `A apply`: the after byte for byte; verify 0; apply again a no-op; check exit 3 "already applied"; **the manifest's six Part A checks** each with its exit and count;
  the two tables differ in line 7 only, the six other lines and the final newline equal; **the new line is `*/10 * * * * ` plus the old line's launcher command and
  log redirect byte for byte plus the DEC-1157 (2) comment**; it names no state file and no clock, no `%`, no quote; the real `crontab -n -` accepts both tables;
  **control: the real `crontab` given this bundle's long file path refuses it** ("No such file": it cuts a file name at about 100 characters, hence `crontab - <`);
  **the new line as cron runs it** (`/bin/sh -c` of its command, the operator's paths planted, a stub launcher), with no state file, a stale `false`, a fresh `true`:
  the launcher runs each time and appends its line; `A undo` the before byte for byte; check ready again; a crontab moved since the build: check, apply, undo,
  verify each exit 3, untouched; a tampered frozen copy: exit 4; Part A ignores Part B's rows (a tampered Part B copy, no install in HOME); `A apply` in a clean
  environment from an empty folder writes nothing else.
- **Part 2, Part B stage 1 on planted folders (cases 31 to 62):** check, verify, undo no-op; apply (the install's own APPROVED check ok); every file the after;
  both install files 0444; no temporary file, no `__pycache__`; the thirteen other install files unchanged; `APPROVED` differs in the one line; verify; apply again a
  no-op; check "already applied"; **the manifest's five Part B checks**; undo to the before byte for byte (hash, mode, listing); a stop part way (the install folder
  not writable: exit 5) named by check and finished by a second apply; **refusals that touch nothing:** a moved repository file, a moved install file, a stray
  install file, `APPROVED` edited after the apply (exit 3), a tampered frozen copy (exit 4), the operator's freeze, journal, a queued request, a launch holding
  `log/launch.lock` (exit 6).
- **Part 3, G9 over a clock file (cases 63 to 72):** the applied `holds()` over **160 (time, state) cases** (20 times from 00:00 to 23:59 x 8 states of the old
  state file: true, false, missing, stale, malformed, empty, `"false"`, a directory): **no hold in any**. The OLD install (HOURS-2's, live) over the same table agrees
  with its rule written out separately (0 disagree); **88 cases change, every one from held to free, all in 02:10 to 07:59**; the old one held at 02:30 in every state
  and at 05:10 with no file (tonight's state). **The kept holds:** a planted NIGHTLY-RUNNING, CLOSE-RUNNING, the CTO's and the operator's `act-in-progress.txt` each
  hold at 01:30, 02:30, 05:10, 14:00; an explicit `nightly_window` holds inside and not outside; an unreadable clock holds.
- **Part 4, the real launcher (cases 73 to 78):** `operator_launch.py` from the applied install, a stub `claude`, a queued request: **02:30 no file, 03:30 a fresh
  `holding: true`, 05:10 a stale `false`, 07:45 and 14:00: the request taken and a session started** (`launched`, the new `approved_sha256`); **05:30 with a fresh
  NIGHTLY-RUNNING: `held` at G9, the request stays in `queue/`**.
- **Part 5, does it bite (cases 79 to 84):** mutants of the installed `opcommon.py` over the same table: the old code (88 cases caught), a 02:10-03:09 hold put back
  (32), the old quiet hours (88), the old nightly window as default (48), the NIGHTLY-RUNNING hold dropped (16), the CTO's hold dropped (160). Each caught.
- **Part 6, the operator's own tests:** **not run in the final rehearsal**: every heavy slot was held by the leads; the first rehearsal waited 34 minutes in
  `heavy_slot.sh` and the CTO had it stopped by pid (a gate wait, DEC-1146). **Run earlier, through `heavy_slot.sh`** (TMPDIR outside the repository and
  `~/gov-os-runs`, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider`), on a clone of `w2/integrate` at `df8ba7007` with the four after files (byte-equal
  to the bundle's, checked by `cmp`): **`tests/unit/operator/test_act_operator_hours_2.py` plus the two S13 tests: 238 passed, 0 failed** (232 unit cases, 5
  `HOLDS` cases, 2 night cases). Not run at all: the whole of `tests/unit/operator` and `tests/acceptance/W2-148` with the after files, the revised unit file on the
  OLD code, the OLD unit file on the new code (the reviewer or the CTO runs them when a slot is free: `build_act.py rehearse` without `HOURS3_NO_SLOTS`).
- **Part 7, the second stage on a clone (cases 85 to 117):** a clone of `w2/integrate` (head `aa3bfdc19b9d`, the map `805bd918d467`), a planted HOME. **Section 0's
  two Part B blocks and section 5's undo block run as printed** (cut from this file, the repository root substituted): applied, verified, the first commit (one parent,
  the three trailers, exactly the four paths); the exempt step and the second commit (subject with the first's 12 digits, the trailers, the map only, 2 lines added,
  mode 644, the map parses: the old `acceptance_exemptions` plus the one entry, every other key equal); exempt again a no-op; exempt-verify 0; exempt-undo refused
  after the commit; the undo of both commits back to the head before the ACT, `APPROVED` the old one, check ready. Planted: exempt twice (a no-op), exempt-undo;
  **refusals that touch nothing**: another HEAD, `Role: operator`, HOURS-2's subject, a fifth path, an altered file, a changed map, a link, an unwritable folder
  (exit 5), a map moved by a committed change; the undo after the first commit alone; exempt-verify on a moved entry or a changed decision (exit 3). **W1-01 was not
  run** (the same slot wait): its green before, red between the commits (the control) and green after are what HOURS-2's part 7 showed for the same code shape, not
  shown here.

## 7. What a session already running does
Unchanged from HOURS-2's section 7 (M: `operator_launch.py`, `operator_run.py`): G9 is read by the launcher once before the wall and the session, and by
the run at its G9 step after G1 to G8, polling every `poll_s` while held; never again before the commit. With no time hold the only holds a night
session meets are the kept ones; a run that reaches G9 while NIGHTLY-RUNNING is fresh waits there until the flag goes or the launcher's
`session_timeout_s` (2700 s) ends the session (the request is then in `done/`, nothing applied: queue it again).

## 8. Files and hashes
| File (`acts/ACT-OPERATOR-HOURS-3/`) | sha256 |
|---|---|
| `before/crontab/crontab` (the live `crontab -l`, ACT-OPERATOR-HOURS-1's after) | `88cf08b165a184a23681b610ea07490c7c60559c6125fdba359db2a083d7c880` |
| `after/crontab/crontab` | `72f1106f7a0c1d3e4a5bb25f00c82d24cae7149131bcd5a3906496a463a05fdc` |
| `before/{repo/governance/project/operator,home/gov-os-operator/install}/opcommon.py` (the live bytes) | `123e17e5581149725c75babaa9200a09c4854254053df14105b6ce17450bbc87` |
| `after/.../opcommon.py` (both) | `c7ec467c569126d803046ad7ca0e883d19d69a8f03bca17ffdd615a815981f7f` |
| `before/home/gov-os-operator/install/APPROVED` | `1e557c49be5802256efa1906753964b53893a2eb507701fac02ebfe4f60914bc` |
| `after/home/gov-os-operator/install/APPROVED` | `ff3579ff5abd13f54c8c5b844db5baa23d97f8372dd7ea84f01b3a93c9809114` |
| `before/repo/tests/unit/operator/test_act_operator_hours_2.py` to `after/...` | `b57723caaabb` to `f5cab8e7dcdc` |
| `before/repo/tests/acceptance/W2-148/test_w2_148_gates.py` to `after/...` | `0f05dbcefa09` to `691f3b6b138f` |
| `before/repo/tests/acceptance/W2-148/README.md` to `after/...` | `625e078ba23d` to `e990295b9e36` |
| `apply.sh` | `e91fc7e47d5eb491208716ed77007f0540ffd099a465ba36ec10b08993676198` |
| `list.txt` (root, path, before, after; Part A's row first, then Part B's in apply order) | `e6f3250d3160d335bbda0566d410359182b249d88d84b7bf85799b86287b4a85` |
| `keep.txt` (the thirteen install files Part B leaves; byte for byte HOURS-2's) | `851ee3394cde348686421bd4dd9c0edf1c2c71ef122905e2834eefa08189e0a1` |
| `rehearsal.log` | `7cb962dc293d19785573e2f0a0a89b1e4e659bdc2ac028f02588151186a26fbb` |
| **`manifest.json`** | **`716da9dc5c4dd4c64b5d03f92a9696a35b3f119d2ff1f20e004565005b665ccc`** |

The operator's own code on the bundle (`build_act.py gates`, read only): `validate_manifest` pass; 18 files hash as the manifest says; the path rule passes on `apply.sh` and all eleven checks; `act_class.classify`: class O for the bundle (crontab b, the six other rows O), Part A alone b, Part B alone O.
The bundle depends on the live crontab, install, four repository files and path map as they are now (head `df8ba7007` at the first build, `aa3bfdc19b9d` at the final build: the commits between touch none of them): if any moves before the
apply, `check` (or `exempt`) says so and the CTO rebuilds (`build_act.py all`).

## 9. Risks, and what I did not do
1. **Not independently reviewed.** Part A needs its one review before the CTO applies it; Part B's review is the CTO's ordinary round before the owner's
   yes. The tests were revised by the same helper that wrote the code (stated as a test designer's revision: written from DEC-1157 (2) and the kept holds;
   the rehearsal's table states the rule separately, and part 6 shows the revised unit file red on the old code and the old unit file red on the new).
2. **An ACT applied while the nightly runs** is still held by **NIGHTLY-RUNNING** (G9, at the launcher and at the run's G9 step). One gap remains, small:
   `nightly.sh` writes the flag only when it reaches its run (M: line 96, after its own checks), and the wrapper `nightly_restart.sh` first waits for quiet
   (under DEC-1159 (1), recorded at 2026-11-13 after this ACT was begun, it runs beside the leads and writes no `dispatch/OFF`, but still waits for an ACT
   and the operator's freeze). A launch at the 04:00 or 04:10 tick whose session (300 s canary, then G1 to G8) reaches G9 after the wrapper's quiet check and
   before the flag exists passes and applies in the nightly's first minutes; the night hold covered that before (it held from 03:00). E: it needs a request
   queued at that tick and the two start-ups to overlap by about a minute. If the owner wants it closed, a further (O) change adds a margin (say 03:55 to
   04:15) or a nightly-start marker to G9; not in this ACT ("every other G9 hold stays exactly").
3. **The operator during leads' load.** DEC-1157 runs leads all night with no CPU band; the operator now applies ACTs then too. Its session is one Claude
   session plus the ACT's own checks (M: all 27 manifests on the machine had only short checks, HOURS-1's review); it takes no heavy slot of its own, and
   its commit freeze and G7 re-check stand. E: a small addition beside the leads; memory protection (the floor, `mem_guard`) is unchanged and is what
   protects the machine (DEC-1157 (14)).
4. **The operator commits to the main tree at night** while the CTO lands batches (DEC-1157 (4), (7): no commit freeze during lands). The operator's
   own freeze and the CTO's `log/act-in-progress.txt` (a G9 hold) are the coordination: the CTO holds the operator by writing that file during a land.
5. **Notices at night.** An applied or refused ACT may notify the owner at night (DEC-1157 (1) removed the night push rule for decisions; the operator's
   own notices were already sent at any hour by day). Not changed here.
6. **A leftover state file is now ignored everywhere.** If a future decision restores a night hold, both the line and G9 need a new ACT (the code that read
   the file is removed, not disabled).
7. **Part B writes the main tree's working files** (four modified, then the path map) on whatever branch is checked out; commit the four paths and nothing
   else with them; `exempt` needs the map unmodified at HEAD and equal to `805bd918d467` (no other path-map ACT is queued, M: every bundle under `acts/`
   and `drafts/` naming the map has a before other than the live map).
8. **The launcher does not wait on the lock**: a launch in the instant between `opcommon.py` and `APPROVED` refuses "APPROVED mismatch" once; hence "not at a
   :x0 minute" for Part B.
9. **Not rehearsed:** a real cron firing; a real `claude` session (the stub stands in); the owner's commits under the main tree's hooks (the
   `reference-transaction` freeze gate, the landing and trailer checks; the clone has git's defaults); `git reset --keep` on a branch others have fetched;
   the acceptance S13 tests on the OLD code (they would hang to their timeouts; the unit file's red run is the bite check).
10. **The gate (h) reader does not list the commit** (as for HOURS-2: DEC-1157 cannot name an id that did not exist when it was written); W1-01 reads the
    list by full id and decision shape only.
