# ACT-OPERATOR-HOURS-2: the operator agent's gate G9 holds only while the night hold is on (DEC-1141 (6))

- **For:** the owner, by hand, as the message in section 0 (the operator's own install, class (O), like ACT-OPERATOR-1, -2 and
  ACT-OPERATOR-ROUNDS-1). About one minute. Nothing is committed by the script; the owner commits four repository paths.
- **By:** an ACT-preparation helper of the CTO (Sonnet, high; RUBRIC-2, class C1), 2026-11-12 from about 02:50 to 03:40 UTC.
  **Nothing live was changed or started:** no write under `~/gov-os-operator`, no crontab write, no commit, no stage, nothing in the
  main tree. Built and rehearsed in planted folders and a clone (section 6). **Reviewed READY** (`reviews/ACT-OPERATOR-HOURS-2-review.md`).
- **Under:** DEC-1141 (6) (the owner, 2026-11-12: "the operator agent sleeps only while the nightly runs (the night hold, from 03:00
  until the nightly ends)... a skip while the night hold is on, so it never applies an ACT during the nightly"); it replaces the
  fixed quiet hours of DEC-1104 (2) in the operator's G9. DEC-1138 (3) is the night hold's own rule. DEC-1104 (4): the operator's own
  install is the owner's, by hand. The manifest's `dec` names DEC-1141, DEC-1104, DEC-1138.
- **Companion:** ACT-OPERATOR-HOURS-1 (its package `drafts/operator-hours-1/ACT-OPERATOR-HOURS-1.md`):
  the crontab line, the CTO's to apply. Its section 7 is this ACT's reason (section 1 below).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/operator-hours-2/` (`build_act.py`: build, rehearse, finalize, gates; `code/`:
  the after files). The bundle: `.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-2/`.

## 0. The short version, your line, and the steps for your operator
1. **One gate changes.** G9 (the holds, in `opcommon.py`'s `holds()`) no longer holds for the fixed quiet hours 02:00 to 07:30 or for
   the nightly's fixed window 03:50 to 08:00. It holds: from **02:10 to 03:09 always** (a session started then could run into the
   night hold), and from **03:10 to 07:59 unless** the night hold's state file (`log/night-hold.state.json`) is **under 300 s old and
   `holding` is exactly `false`**; at every other hour there is no time hold and the file is not read. A missing, empty, malformed,
   stale or odd file is a hold (fail closed). This is the same rule and the same reading as ACT-OPERATOR-HOURS-1's crontab guard.
2. **Every other gate stays**, and so does every other G9 hold: the NIGHTLY-RUNNING flag (a nightly that overruns the hold still
   holds), the close queue, the CTO's `log/act-in-progress.txt`, the operator's commit freeze, an unreadable clock.
3. **Two install files change, and four repository paths** (the source the install is copied from and its tests): the install's
   `opcommon.py` and `APPROVED` (one line, `opcommon.py`'s hash); in the main tree the same `opcommon.py`, the acceptance test for G9's
   holds (one case replaced by two), its README (three lines) and one new unit test file (86 cases).
4. **Safe with or without ACT-OPERATOR-HOURS-1, in either order** (section 4).

**Your line: `yes ACT-OPERATOR-HOURS-2 d3d29237`** (the first 8 digits of the manifest's sha256 in section 8). Your operator then does,
in the main tree, not at a :x0 minute (the cron's launch) and best after 08:00 UTC, with nothing queued:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-2
bash $G/apply.sh check     # exit 0: "check: ready to apply ..." (every listed file is the before; the operator holds nothing)
bash $G/apply.sh apply     # exit 0: six lines "apply: ...", "the install's own APPROVED check: ok", "APPROVED 1e557c49...", "state applied"
bash $G/apply.sh verify    # exit 0: "verify: every listed file is the after ..."
sha256sum ~/gov-os-operator/install/APPROVED    # expect 1e557c49be5802256efa1906753964b53893a2eb507701fac02ebfe4f60914bc
git status --short         # 3 M and 1 ?? (opcommon.py, test_w2_148_gates.py, its README.md; the new test_act_operator_hours_2.py)
git add governance/project/operator/opcommon.py tests/acceptance/W2-148/test_w2_148_gates.py tests/acceptance/W2-148/README.md tests/unit/operator/test_act_operator_hours_2.py
git commit -m "ACT-OPERATOR-HOURS-2: G9 holds only while the night hold is on (DEC-1141 (6)); the fixed quiet hours and the nightly window gone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1141" --trailer "Role: owner"
```
If `check` stops (exit 3: a file moved; exit 4: a frozen copy altered; exit 6: the operator is busy), send its line to the CTO and
apply nothing: exit 6 means wait and run it again. If `apply` stops part way (a full disk, a kill), run `apply` again: it finishes
(a file already after is left; a file that is neither before nor after refuses, nothing touched). **Undo:** section 5.

## 1. Why: ACT-OPERATOR-HOURS-1's finding
DEC-1141 (6) asks the operator agent to sleep only while the night hold is on, every other hour to run as usual. ACT-OPERATOR-HOURS-1
changes the crontab line to every hour with a guard on the same state file. Its builder found (its section 7) that the launcher
the line starts is not enough: the launcher's own gate **G9 (`opcommon.holds`, hashed in the operator's `APPROVED`, so a change is
yours, class (O))** still held a queued ACT through the constants `QUIET = ((2, 0), (7, 30))` and `DEFAULT_NIGHTLY = "03:50-08:00"`.
With HOURS-1 alone the launcher is called every 10 minutes at every hour but a queued ACT is applied only from 08:00 to 01:59; from
02:00 to 07:59 G9 holds it, nightly or not, so the hours given back were 01:00 to 01:59 only. HOURS-1's table named this "option B": a
second ACT on the install, `QUIET` removed or cut to the hold's own window, `DEFAULT_NIGHTLY` dropped for the flag and the hold, `APPROVED`
re-hashed, the owner's operator applies by hand. This is that ACT, with the same boundaries as the guard so the line and the gate agree.

## 2. What changes
`opcommon.py` (708 lines to 741; sha256 first 12 `e392d8a0e177` to `123e17e55811`); the repository's copy and the install's are the same bytes
(`governance/project/operator/opcommon.py`; the install is that file, as ACT-OPERATOR-1 and -2 installed it). The whole diff:
```diff
-QUIET = ((2, 0), (7, 30))           # the quiet hours, 02:00 to 07:30 (DEC-1104 (2), G9)
-DEFAULT_NIGHTLY = "03:50-08:00"     # the nightly (04:00 to about 07:00) and its wake (03:50): ACT-NIGHTLY-0400
+# G9 holds only while the night hold is on (DEC-1141 (6), ACT-OPERATOR-HOURS-2; ...): the same rule and the same fail-closed reading as the
+# crontab's guard (ACT-OPERATOR-HOURS-1). From 02:10 to 03:09 it holds ...; from 03:10 to 07:59 it holds unless the night hold's state file
+# is under NIGHT_HOLD_MAX_AGE_S old and its "holding" is exactly false; at every other hour the file is not read and there is no time hold.
+HOLD_FROM = (2, 10)
+HOLD_READ_FROM = (3, 10)
+HOLD_END = (8, 0)
+NIGHT_HOLD_MAX_AGE_S = 300
+DEFAULT_NIGHTLY = None              # no fixed nightly window by default; the NIGHTLY-RUNNING flag and the night hold say when
 ...
-    s["nightly_window"] = conf.get("nightly_window") or DEFAULT_NIGHTLY
+    s["nightly_window"] = conf.get("nightly_window") or DEFAULT_NIGHTLY       # an explicit window still holds
+    s["night_hold_state"] = os.path.abspath(os.path.expanduser(
+        conf.get("night_hold_state") or os.path.join(s["scratch"], "log/night-hold.state.json")))
+    s["night_hold_max_age_s"] = float(conf.get("night_hold_max_age_s") or NIGHT_HOLD_MAX_AGE_S)
 ...
+def night_hold_reasons(s):
+    path = s["night_hold_state"]
+    try:
+        age = time.time() - os.stat(path).st_mtime
+        with open(path, encoding="utf-8") as f:
+            holding = json.load(f)["holding"]
+    except Exception as exc:     # fail closed: any error is a hold
+        return [f"the night hold's state cannot be read ({exc.__class__.__name__})"]
+    if not age < s["night_hold_max_age_s"]:
+        return [f"the night hold's state is stale ({int(age)} s old)"]
+    if holding is not False:
+        return ["the night hold is on"]
+    return []
 ...
 in holds():
-    (qa, qb) = QUIET
-    if in_window(d, f"{qa[0]:02d}:{qa[1]:02d}-{qb[0]:02d}:{qb[1]:02d}"):
-        out.append("the quiet hours (02:00 to 07:30)")
+    t = d.hour * 60 + d.minute
+    if HOLD_FROM[0] * 60 + HOLD_FROM[1] <= t < HOLD_READ_FROM[0] * 60 + HOLD_READ_FROM[1]:
+        out.append("before the night hold (02:10 to 03:09: no session starts that could run into it)")
+    elif HOLD_READ_FROM[0] * 60 + HOLD_READ_FROM[1] <= t < HOLD_END[0] * 60 + HOLD_END[1]:
+        out.extend(night_hold_reasons(s))
     try:
-        if in_window(d, s["nightly_window"]):
+        if s["nightly_window"] and in_window(d, s["nightly_window"]):
```
`APPROVED`: the one line `e392d8a0...  opcommon.py` becomes `123e17e5581149725c75babaa9200a09c4854254053df14105b6ce17450bbc87  opcommon.py`
(sha256sum's form, every other line as it is); `APPROVED` itself `97c9a3a5bd22` to `1e557c49be58`
(`1e557c49be5802256efa1906753964b53893a2eb507701fac02ebfe4f60914bc`). The other thirteen install files are untouched
(`operator-settings.json` too: the state file's path defaults from the `scratch` setting, `<scratch>/log/night-hold.state.json`, the very file
the crontab guard reads; the new settings `night_hold_state` and `night_hold_max_age_s` exist for tests and are left out of the live file).

### The choices (M: read here; E: my estimate)
| Choice | Reason |
|---|---|
| **Same boundaries and same fail-closed rule as the crontab guard** | DEC-1141 (6) as HOURS-1 read it: 02:10 to 03:09 never; from 03:10 to 07:59 only when the file is under 300 s old and `holding` is exactly `false`; the file is not read at other hours, so a leftover `holding: true` never stops the operator in the day. Two places (the line and the gate) that disagree by a minute would make one of them wrong; both are in the package, the rehearsal runs the same table against the gate. |
| **`holding is not False` is a hold; age by the file's mtime, as the guard** | M: `night_hold.py` rewrites the file every 60 s with `pid`, `at`, `holding`, `in_window`, `nightly`; when it is not running the file keeps its last content, so the age (300 s, four missed looks) is what shows a dead hold. The rehearsal checks 0, 1, `"false"`, null, no key, `[false]`, an empty file, a directory: all holds. Parity detail: a file whose mtime is in the future passes the age test in both (negative age), as in the guard. |
| **`DEFAULT_NIGHTLY` dropped (default none); the setting stays** | The window 03:50 to 08:00 would still hold at 05:10 after the nightly ended, which DEC-1141 (6) rules out ("until the nightly ends"). The NIGHTLY-RUNNING flag (M: written by `nightly.sh`, removed by its trap; the night hold itself reads it) holds a nightly that overruns 07:30 or 08:00. A configured `nightly_window` still holds (the tests use one). |
| **The flag and every other hold kept** | "Keep every other gate". The flag is the one signal the night hold does not carry past 07:30. |
| **`QUIET` removed, not edited** | No other code reads it (M: grep over the install, the tree and the tests). A constant named for hours that no longer hold would mislead. |
| **G9 reads the file at every poll** | `holds()` is the gate's one function, called by the launcher once and by the run's G9 loop at each poll (60 s): a hold that releases at 05:00 lets a waiting run through at its next poll. |

## 3. Class and route
- **Class (O).** M: `class-rules.yaml`'s `operator-own` row (`governance/project/operator/**` and `gov-os-operator/**`): control, the owner's;
  `act_class.classify` on this bundle (`build_act.py gates`, read only): **class O**, hits `[]`; the two `opcommon.py` rows and `APPROVED` are
  `operator-own`, the three tests are the catch-all `unknown` row (also O). The operator agent cannot apply it: rule 2d and `APPROVED` keep its own install out of its reach
  (G6 refuses an (O) class). No queue request; your yes line and your operator's by-hand steps are the route, as for ACT-OPERATOR-2 and
  ACT-OPERATOR-ROUNDS-1.
- **Why the repository files are in the bundle.** The install is a copy of `governance/project/operator/`; W2-148's tests and the
  acceptance world copy the operator from the tree. Changing the install alone would leave the tree's G9 on the old rule and its
  acceptance case S13 (`quiet-hours`, clock 02:00, cleared at 07:30) red against its own code. So the tree's `opcommon.py`, that test
  and its README line move with the install, and 86 new unit cases pin the new rule (red on the old code: 42 fail).

## 4. Order: after or with ACT-OPERATOR-HOURS-1; either alone is safe
| Applied | What the operator does | Why it is safe |
|---|---|---|
| **HOURS-1 alone** (the crontab every 10 minutes at every hour, the guard; G9 as today) | The launcher is called from 01:00; G9 holds a queued ACT from 02:00 to 07:30 and in 03:50-08:00; the request stays in `queue/` ("held"). Applying hours are as before plus 01:00 to 01:59. | M (HOURS-1 section 7): nothing new reaches the nightly: the guard skips from 02:10 and from 03:10 while the hold is on, and G9 holds on top. |
| **HOURS-2 alone** (the cron line `*/10 0,8-23`; G9 new) | The cron calls the launcher only at 00:00 to 00:50 and 08:00 to 23:50. At those times the new G9 holds nothing the old did not (no time hold at 00:00-02:09 or from 08:00; the old held nothing there either), so the operator's behaviour does not change until HOURS-1 is applied. | M: the rehearsal's table of 247 (time, state) cases, old against new: the only cases that turn are 02:00-02:09 (now free) and, with a fresh `holding: false`, 03:10 to 07:59 (now free); none turns from free to held. The cron does not fire in either. A launcher run by hand at 05:10 with the hold off would go on (intended). |
| **Both** (either order, or together) | The launcher at every hour; G9 and the guard agree: no session from 02:10 to 03:09; from 03:10 to 07:59 only with the hold off; every other hour as usual. The gate is also a second line behind the guard: if the crontab line is ever put back or changed, G9 still holds in the hold. | Recommended: HOURS-2 first or together; then HOURS-1 (the CTO applies it from 08:00). |

If one of the two is changed later (a different margin, a different file), the other must be changed with it; both name their boundaries
(`02:10`, `03:10`, `08:00`, `300`).

## 5. The check line, and the undo
After the apply (section 0): `apply.sh verify` exits 0; `sha256sum ~/gov-os-operator/install/APPROVED` prints
`1e557c49be5802256efa1906753964b53893a2eb507701fac02ebfe4f60914bc`; the next launch's line in `~/gov-os-operator/log/operator-launch.out`
carries `"approved_sha256": "1e557c49be58..."` and `"result": "idle"` (the file has no timestamps; its `ls -l` time moves). The manifest's five checks (the new
`opcommon.py` and `APPROVED` hashes, no `QUIET =` line, the new `HOLD_FROM` line once, one `opcommon.py` line in `APPROVED`) pass.
**The first night is watched:** from 02:10 to the night hold's `release` event a queued ACT stays in `queue/` with a `G9 held` line in
`operator.jsonl` ("before the night hold" or "the night hold is on"); after the release it is taken.

**Undo:** `bash $G/apply.sh undo` (the same busy and moved refusals), then `bash $G/apply.sh check` exits 0 again: every listed file is back
byte for byte from the frozen `before/` copies (the new test file removed), `APPROVED` `97c9a3a5bd22` again, the install's own check ok.
After the commit, `undo` leaves a working-tree diff: `git add` the same four paths and commit "ACT-OPERATOR-HOURS-2 undone" with the same three
trailers. **By hand** (only if `apply.sh` cannot run), the restore is `before/home/gov-os-operator/install/opcommon.py` and `.../APPROVED` copied over the
install's two files (opcommon.py first, `APPROVED` last, nothing queued and no launch running) and `before/repo/...` over the tree's three files, the new test file deleted.

## 6. The rehearsal (DEC-1057): `rehearsal.log`, 103 cases, ends `failures: 0`
`python3 -B drafts/operator-hours-2/build_act.py rehearse` (no date, pid or head in the log, so a rebuild gives the same manifest). Planted: a
planted HOME holding a copy of the live install, a planted main tree (the three before files and the new test's folder), the bundle copied in at the same relative
path, a clock file (the operator's own `clock` setting) and a state file planted at each case. The live install, crontab and main tree are
hashed before and after: unchanged (cases 101 to 103).
- **Part 1, apply.sh (cases 1 to 41):** check, verify (exit 3 before), undo when already before (untouched), an unknown step (exit 2), apply (the install's own `APPROVED` check ok), every file
  byte-equal to the frozen after, both install files 0444, no temporary file, no `__pycache__`, the thirteen other install files unchanged, `APPROVED`
  differs in the one line; verify; apply again (untouched); check (exit 3 "already applied"); undo; every file and the whole tree (hash, mode,
  listing) as at the start; **a stop part way** (the install folder not writable: exit 5, repository files written) and the finish by a second
  apply; a half-undone state finished by undo; **refusals that touch nothing:** a moved repository file, a moved install file, a stray file in
  `install/`, `opcommon.py` or `APPROVED` or the new test file edited after the apply, a tampered frozen copy (exit 4), the operator's freeze, journal, lock of a failed undo,
  a request in `queue/`, a launch holding `log/launch.lock` (exit 6).
- **Part 2, G9 over a stub clock (cases 42 to 63):** the installed `holds()` over **247 (time, state) cases** (19 times x 13 states: true, false, missing, stale,
  malformed, empty, `[false]`, no key, null, 0, `"false"`, 1, a directory) against the rule written out separately: 0 disagree. Named: **01:30** and **02:05**: no
  hold in any state; **02:30**: a hold in every state, even a fresh false; **03:30**: true holds, fresh false releases, missing, stale (400 s) and
  malformed hold (with their reasons), the odd files hold; **05:10 after the release**: free (a fresh true holds); **07:45**: false releases,
  true and stale hold; **14:00**, 08:00, 23:59, 00:00: free in every state; the edges 02:09 / 02:10 / 03:09 / 03:10 / 07:59 / 08:00. Against the OLD install
  over the same table: it holds at 02:05, 05:10 and 07:45 in every state, nothing at 01:30, 14:00, 08:00; the 33 cases that differ are 02:00-02:09
  and a fresh false from 03:10 to 07:59; none turns free to held. The planted NIGHTLY-RUNNING flag, close flag, the CTO's and the operator's
  `act-in-progress.txt` each still hold at 14:00, 05:10 and 01:30.
- **Part 3, the real writer (cases 64 to 69):** `night_hold.py`'s own `step()` at fixed times writes the file G9 reads: 02:59:30 false (G9 holds before the hold, free
  at 01:30); 03:00:20 true (G9 holds at 03:10 and 03:30); 05:00 with today's status line, released (free at 05:10); a night with no end at
  06:00 holds; 07:31 released by the 07:30 limit (free at 07:40); the writer stopped an hour ago: G9 holds at 07:40 (stale), free at 14:00.
- **Part 4, the real launcher (cases 70 to 80):** `operator_launch.py` from the applied planted install, a stub `claude`, a queued request: **01:30 no
  file, 02:05 no file: the request taken and a session started** (result `launched`); **02:30 false, 03:30 true, 03:30 no file: `held` at G9, the request stays in `queue/`**; 05:10 false, 07:45
  false, 14:00 no file: taken; the held lines' reasons read as in section 2; every result carries the new `approved_sha256`.
- **Part 5, does it bite (cases 81 to 95):** the installed `opcommon.py` mutated fourteen ways and the same table re-run (the right code: 0 disagree; each
  mutant at least 2): the old quiet hours back (30), the state never read (7 and 84), `== True` for `is not False` (21), no age test (7), an
  unreadable file as no hold (42), the pre-hold margin from 02:20 (13) or 02:00 (26), the state read from 03:00 (2), to 07:30 (36) or to 08:30 (24), the old
  window as the default (5), the age limit 3000 s (7), the NIGHTLY-RUNNING hold dropped (2). Each is caught.
- **Part 6, the operator's own tests (cases 96 to 100):** a `git clone --no-hardlinks` of the committed head (`448e9faf493d`) with the ACT's four
  repository files (hashed against the frozen after copies): **`pytest tests/unit/operator tests/acceptance/W2-148`: 507 passed** (the same suites on
  the unchanged head exited 0 before the change); the new file alone 86 passed; **the same 86 on the OLD `opcommon.py`: 42 failed, 44 passed**
  (the rest are cases the old code also meets: the free hours and the other holds).
- **Read only on the live system, not in the log:** the new `holds()` on the real clock and the real state file (03:22 UTC: `holding: true`) said
  `["the night hold is on"]`; `apply.sh check` against the live install and tree exits 0 ("ready to apply"), `verify` exits 3 ("not applied").
- Not rehearsed: a real `claude` session started by the launcher (the stub stands in; the canary and the walls are not what this changes); a real
  cron firing; the owner's by-hand typing (the lines of section 0 were run by the rehearsal's `apply.sh` calls, not by `bash -c` of the text).

## 7. What a session that began before 02:10 does (G9's own checks)
M (`operator_launch.py` and `operator_run.py` read): G9 is called **twice per request and never again**. The launcher calls `holds()` once before it
builds the wall and starts the session (`held` leaves the request in `queue/`). The run (`operator_run.py go`) loops on `holds()` at G9 **after
G1 to G8** (the dry run included), polling every `poll_s` (60 s), and goes on only when it is clear; it then recomputes, re-checks G7 if it had
waited, takes the commit freeze and applies. **G9 is not checked again before the commit or after the apply starts.**
- A launch at 02:00 (the last cron tick before the margin when HOURS-1's guard is in): G9 passes at the launcher; if the run reaches its G9 at or after
  02:10 (a slow G1 to G8), it **waits there** through 02:10 to 03:09, then through the hold, until the launcher's `session_timeout_s` (2700 s) kills the
  session group (the request is then in `done/`, nothing applied, no journal: **it must be queued again**; this is what a quiet-hours hold did to such a
  run before). If it reaches G9 before 02:10 it passes and **applies to the end** (G9 is not read again); the worst case is the launch's 300 s canary
  plus 2700 s session plus 30 s to stop the group: **a 02:00 launch ends by 02:50:30**, ten minutes before the hold's first look.
- A launch by hand at 02:09 (or the cron if HOURS-1's guard were not in) could end at 03:04:30, up to four and a half minutes into the hold, in the worst case
  (E: a typical ACT takes minutes). With HOURS-1's guard no cron launch starts after 02:00.
- A launch at 03:10 or later with the hold off is clear at the launcher, and the run's G9 reads the file again after G8: if the file has gone stale or says true
  in between (the hold died or came back on), the run waits there, as above.

## 8. Files and hashes
| File (`acts/ACT-OPERATOR-HOURS-2/`) | sha256 |
|---|---|
| `before/repo/governance/project/operator/opcommon.py` and `before/home/gov-os-operator/install/opcommon.py` (the live bytes) | `e392d8a0e177e999f5361243a053e386f5fccc0619dec7d5e8c832cd756a1024` |
| `after/repo/governance/project/operator/opcommon.py` and `after/home/gov-os-operator/install/opcommon.py` | `123e17e5581149725c75babaa9200a09c4854254053df14105b6ce17450bbc87` |
| `before/home/gov-os-operator/install/APPROVED` | `97c9a3a5bd22e0bc3546cc12c6c5d9aca8f9f39d145825b6f129b59259895820` |
| `after/home/gov-os-operator/install/APPROVED` | `1e557c49be5802256efa1906753964b53893a2eb507701fac02ebfe4f60914bc` |
| `after/repo/tests/unit/operator/test_act_operator_hours_2.py` (new, 86 cases) | `b57723caaabb96efce377e6dc3003e6af185a5c580bf36b2d909b95cb528f760` |
| `before/repo/tests/acceptance/W2-148/test_w2_148_gates.py` to `after/...` | `1c9c44c33abc` to `0f05dbcefa09` (first 12) |
| `before/repo/tests/acceptance/W2-148/README.md` to `after/...` | `a9e4dc8833e4` to `625e078ba23d` (first 12) |
| `apply.sh` | `f4eaf481a22ca106944d33a73b4afd1bc62f6ce899c54fe3f57e5c6322714988` |
| `list.txt` (root, path, before, after; the order of the apply) | `34010112c71059f6fe46459794e038d83f7c315aa8999e78766febe67884e578` |
| `keep.txt` (the thirteen install files this ACT leaves, sha256sum's form) | `851ee3394cde348686421bd4dd9c0edf1c2c71ef122905e2834eefa08189e0a1` |
| `rehearsal.log` | `a4a04d9dc85f1e914c5a127a416189eede88415ed63e927337a1ee2da8534b16` |
| **`manifest.json`** | **`d3d292378b7bda8c4339fcbcaa77025a53dd40b91aefad0eef8a686f3ad8e6f2`** |

The operator's own code on the bundle (`build_act.py gates`, read only): `validate_manifest` pass; 15 files hash as the manifest says; the path
rule passes on `apply.sh` and every check; `act_class.classify`: class O. The bundle depends on the live install and the committed files as they
are today (head `448e9faf493d`): if any of them moves before you apply, `check` says "moved: ..." and the CTO rebuilds (`build_act.py all`).

## 9. Risks, and what I did not do
1. **Not independently reviewed.** The CTO's ordinary round (an independent auditor on the bundle and this package before your yes) is not done. The rehearsal is mine, and the
   rule's wording in the tests was written from the owner's sentence by the same helper; the table in the rehearsal states the rule separately from the code, but not from another mind.
2. **A dead night hold stops the operator from 03:10 to 07:59** (fail closed): after a reboot nothing restarts `night_hold.py` by itself that I could find (M, HOURS-1 risk 2). The operator then
   sleeps those hours as before this ACT; elsewhere it runs. The hold's absence shows as a state file whose `at` stops moving.
3. **The gate reads the main tree's scratch path** (`<repo>/.gov-runtime/scratch/orchestrator/log/night-hold.state.json`, from the `repo` setting). If that folder moves, G9 fails closed from 02:10 to 07:59 and
   runs the rest; it would need the setting `night_hold_state` in `operator-settings.json` (a further install change, yours).
4. **A session that passed G9 before 02:10 applies to its end** (section 7); the worst case ends 02:50:30 for a 02:00 launch (a manual 02:09 launch: 03:04:30). The ACT is
   committed by the operator in those minutes in the main tree; the hold's wind-down starts at 03:00.
5. **After the nightly ends the operator may apply an ACT at 05:10** on a host that has just run the nightly, in the main tree. Its safeguards stay: the commit freeze, the NIGHTLY-RUNNING flag, the CTO's
   `act-in-progress.txt`, the close queue, G7's live re-check after any wait. This is DEC-1141 (6)'s intent; I name it because the old rule kept 05:10 quiet.
6. **The age is mtime-based and uses the real clock** (`time.time()`), as the crontab guard; the hold's own `at` field is not read. A future-dated file counts as fresh in both.
7. **Local time.** The gate takes the clock's own wall time (`now()`: the system's offset), the guard the machine's local time, the hold `datetime.now()`: Europe/London, equal to UTC now. They move together
   at the clocks' change; no UTC is assumed.
8. **The unit tests read the repository's `opcommon.py`**: the commit of the four paths is what keeps the tree and the install the same bytes (the check in the tree's tests that the install is the tree's is not there; `apply.sh verify` and your commit are).
9. **`apply.sh` writes the main tree's working files** (three modified, one new) on whatever branch is checked out; it needs no clean tree but you should commit the four paths and nothing else with them (ACT-OPERATOR-ROUNDS-1's note).
10. **The launcher does not wait on the lock.** A launch in the instant between the two install files and `APPROVED` refuses "APPROVED mismatch" once (the swap holds `log/launch.lock`; the launcher checks `APPROVED` before it takes the lock):
    hence "not at a :x0 minute" (ACT-OPERATOR-2 section 8 item 4).

## 10. Placeholder scan
`python3 .gov-runtime/scratch/orchestrator/tools/placeholder_scan.py drafts/operator-hours-2/ACT-OPERATOR-HOURS-2.md` is run at the end of the helper's work; its result is in the helper's report.
