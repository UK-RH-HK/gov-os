# ACT-DEADMAN-WAKE-1 — independent review, round 1

Bundle: `.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-WAKE-1/` · manifest sha256 `9749d056afee5587fc7686b04c8338ba4ffb19d3d7bf15d6801c060ded9c9eca` (recomputed) · brief `governance/project/operator/reviewer-brief.md`, sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a` (as in the install's APPROVED) · reviewer: independent-auditor, a `claude -p` session started by the CTO's helper a855f83eb96bf46f7, not the author · 2026-11-10T12:17:36+00:00.

**Outcome: not READY.** The brief's six checks pass and the class is (b). F2 blocks under verdict.py's rule (in scope, ordinary work, fails open): while the CTO stands by, a stale `-helper-watch` item no longer reaches the owner, and nothing else reaches the owner in its place. F1 (a false P1 INBOX after the CTO reads a stale wake item) and F3 (a corrupt wake key stops the pass) do not block. Fix F1 and F2 (a few lines, three tests, two checks), then rebuild, rehearse and review again.

## What was checked, and how
Every run was in the reviewer's own clone of w2/integrate (`git clone --no-hardlinks`, HEAD d200322e6), under its own TMPDIR, with HOME planted. ORCH, --log, --state, --session-file, --standby and --inbox-stale all pointed under that TMPDIR. The before copy was never run, since it has no --log. Afterwards the live deadman.log still held 1083 planted-transcript lines (the count the rehearsal recorded), the live inbox held no wake item, and the live tree had not changed.

1. **Touched list and path rule: pass.**
   - One file, `governance/project/orchestration/tools/deadman.py`: before `b425895b…` (the live file and HEAD's), after `ebc94de1…`. Every bundle file hashes as the manifest says.
   - In the clone, `apply.sh apply` changed only that file. This was measured by a hash of the whole tree (ignored and untracked files, .git/hooks and .git/config included). The mode stays 644, no `.act-tmp` is left, nothing lands in the planted HOME, and no crontab is touched.
   - The operator's own `path_rule` (G1), given the live repository and the real HOME, passes `apply.sh` and all four checks. The script reaches the bundle through `BASH_SOURCE` and writes `$PWD/<path>`; the checks name the tool by a relative path.
   - No check can write the live scratch or HOME, either in the dry run or in the live run after the apply. Each check sets `ORCH="$T/o"` and every file flag under its own `mktemp -d`, so the wake's inbox is `$T/st/inbox` (beside --state, not ORCH's). The channels are `nothing` or none, so `pings.log` is never written.
2. **Undo: pass.**
   - The rehearsal log shows undo exit 0, the file byte for byte the before, and the clone's tree clean.
   - In the reviewer's clone, the whole-tree hash after undo equals the one taken before apply.
   - The operator's own dry run (point 4) also compared the undo byte for byte.
3. **Rehearsal: pass.**
   - The log is the run of this bundle. It records a "manifest sha256 before finalize" of `c1a72cd3…`. That is exactly what the final manifest hashes to once its rehearsal entry is removed (build_act.py's `write_manifest(None)`). So the rehearsal ran this apply.sh, list, before, after and these checks.
   - It ran in a clone of w2/integrate at c906619646da with HOME planted; that folder is still there, empty. The log ends `failures: 0`.
   - The rehearsal ran pytest with the real HOME. Its own live-state comparison, and today's unchanged count of 1083, show it wrote no live log line.
   - The live HEAD has since moved to d200322e6 (serial-only.txt and a review record). deadman.py is unchanged, so G7 and G8 still hold.
4. **Checks: pass.**
   - I ran the operator's own `Run._g8` on a copy of the bundle, with `s["repo"]` set to the reviewer's clone so the live repository was never cloned. The function is identical in the install and the repository; they differ only in the guard replay's call-set code and the dry run's call-log name.
   - It ran check, apply, changed set = touched, the after as stated, the four checks green by `check_ok`, undo byte for byte, and no stray change: PASS.
   - It passed in three environments:
     - cron-like: PATH=/usr/bin:/bin, no LANG, no TZ (the operator itself is started from cron);
     - TZ=Pacific/Kiritimati with LANG=C;
     - TZ=America/Los_Angeles.
   - Exit and count were as the rehearsal printed:
     - check 1: 0 / 1;
     - check 2: 0 / 1;
     - check 3: 0 ("HEARTBEAT alive age 0 min");
     - check 4: 10 ("ALERT P1 INBOX | …").
   - The wake's 7 tests pass on the applied file (`DEADMAN=<clone's file>`, run from a copy in the TMPDIR).
   - The first code review's two fixes are in the after copy: the inbox folder is read again, and the stall key is written first, atomically (a temp file then `os.replace`).
5. **Class: (b).**
   - The `watchers` row gives deadman.py class (b), a control path. `act_class.classify` on the bundle gives (b) with no script hit.
   - Code, claim and review agree.
   - In substance the ACT alters the watcher's alerting (the `inbox:` line is left out for the CTO's own wake items), which loosens a control. So the owner's yes is needed (`yes ACT-DEADMAN-WAKE-1 9749d056`).
6. **Guard replay: pass, nothing to replay.** There is no path-map or deny-list change, so `replay_refused` is empty.

The CTO's three further checks:
- **The dry run can run every check as written:** yes (point 4).
- **No check or apply step can write the live scratch:** none can (point 1).
- **The after copy's ALERT lines and limits behave as the before copy's:** yes.
  - The diff leaves `quiet()`, the limits, the three-way branch and the text of every printed line unchanged.
  - I ran the after copy 672 times, comparing against the before copy's decision lines. The runs covered day and night edges, ages from 59 to 300 minutes, idle or waiting on a tool, no earlier alert, alerted 1 h 59 or 2 h before, another stall, and with and without --dry. The verdict, the ALERT line, the age and the state written matched every time (0 mismatches).
  - The wake appeared only at 60 minutes or more, and never with --dry. A wake that cannot be written ("wake failed FileExistsError") leaves the ALERT as it was.
  - The P1 INBOX line's text is unchanged. When it fires changes by design; F1 and F2 are where it changes beyond what the ACT states.

## Findings

### F1 — after the CTO reads a stale wake item, the watch pushes a false P1 INBOX before the dispatcher's next pass
- KPI 4 · scope in · ordinary_work yes (the CTO reading a stale wake item is how every such stall normally ends) · consequence other (a false alarm, at any hour) · not blocking.
- **What happens:**
  - While every stale item is a wake item, the watch leaves the dispatcher's `inbox:` line out and deletes its seen key (`deadman-inbox-stale-seen.txt`).
  - The CTO then reads (removes) the item, but `inbox-stale.txt` keeps the line until the dispatcher's next pass.
  - `only_wake_items_stale` returns False when no item is stale (`bool(old) and …`), so the watch keeps the line. With no seen key, it pushes "ALERT P1 INBOX | the dispatcher's inbox: inbox: 1 item(s) unread; the oldest …-spend-brake.txt | read it or restart the CTO" about an item already read.
  - The before copy pushed once, when the item went stale, and not again: its seen key held the unchanged line.
- **Evidence:**
  - Reproduced with the after copy for `-deadman-wake`, `-spend-brake` and `-helper-watch`:
    - item stale 40 minutes, line present → exit 0 (HEARTBEAT);
    - item removed, line still present → exit 10 with the line above;
    - line removed → exit 0.
  - The dispatcher runs every minute from cron and the sentinel's watch looks every 120 s, so roughly one read in four of a stale wake item gives the push. This is an estimate.
  - A `-spend-brake` push is an alarm about usage, and DEC-1089 (3) allows none at all.
  - A `-deadman-wake` item read 90 to 120 minutes into a night stall brings a P1 INBOX before the 2-hour night limit. The ACT says that never happens.
- **Fix:**
  - When the inbox folder exists and can be read and no item in it is stale, the dispatcher's line comes from before a read, so leave it out (return True for an empty `old`).
  - Keep failing toward the push only for a missing or unreadable folder.
  - Add a test (item removed, line still present → exit 0) and a matching check.
  - Keep --stale-s equal to the dispatcher's STALE_S (both 1800 today) and say so in the docstring.

### F2 — in a CTO stand-by, a stale `-helper-watch` item no longer reaches the owner, and nothing else does
- KPI 4 · scope in · ordinary_work yes · consequence fails open · **blocking** under verdict.py.
- **What happens:**
  - The ACT leaves the `inbox:` line out for wake items on the ground that "the stall's own ALERT stays the backstop".
  - During a stand-by (`log/cto-standby.txt`) that ALERT is silent by design (DEC-998). The inbox alert was meant to fire then: the comment in the code, unchanged in the after copy, says "It also alerts during a CTO stand-by (intended)". The before copy's inbox handling has no stand-by test.
  - So if the CTO's inbox waiter does not wake it during a stand-by, a `-helper-watch` item can sit unread indefinitely with no push. Before the ACT it pushed once the dispatcher's 30-minute line appeared.
  - That is the failure the inbox alert exists for. DEC-1007's reason: returns sat unread for hours because the watcher was not re-armed. It is also the same kind of silence as the 7-hour idle of 2026-11-10, which the wake and the helper watch were built to answer.
- **Evidence:**
  - With the after copy, a stand-by file, the CTO silent 3 hours, and only a `-helper-watch` item stale 40 minutes: exit 0, "HEARTBEAT standby: …", no push.
  - The same with a guard item: exit 10, P1 INBOX.
  - With no stand-by: exit 10, P1 DEADMAN. The backstop holds only there.
  - Stand-bys are ordinary. On 5, 6 and 7 November, 90%, 62% and 69% of the watch's passes were in one (fewer since: 4%, 0%, 0%; live deadman.log).
  - Helper-watch items are the normal output of the helper watch, which is armed every session (DEC-1112 (3)).
- **Fix:**
  - While the stand-by file exists, leave the `inbox:` line out only when every stale item is a `-spend-brake` item. DEC-1089 (3) still applies, and no wake item is written in a stand-by.
  - Outside a stand-by, keep the current rule (with F1's fix).
  - Add "outside a stand-by" to the docstring's backstop sentence and to the INBOX_STALE comment.
  - Tests: stand-by plus a stale `-helper-watch` item → exit 10; stand-by plus a stale `-spend-brake` item → exit 0. Add a check for the first.

### F3 — a wake key holding JSON that is not an object stops the pass
- KPI 4 · scope in · ordinary_work no · consequence other · not blocking.
- **What happens:** `wake()` reads `json.loads(key).get("stall")` and catches only OSError and ValueError. A key file holding `[]` raises AttributeError, and the pass exits with a traceback before the ALERT (reproduced: exit 1).
- **Why it is minor:**
  - The tool only ever writes an object, atomically, so this needs a write from outside.
  - The sentinel then pushes "the watch failed … the dead-man's switch is down", so the failure is loud, not silent.
  - The ALERT's own state file already has the same pattern (reproduced with --dry).
- **Fix in the rebuild:** also catch AttributeError and TypeError, and treat them as no key.

## Notes (not findings)
- The installed operator (`~/gov-os-operator/install`, as APPROVED) differs from the repository copy only in the guard replay's call-set check (DEC-1108 (2)) and the dry run's call-log name. Every function this bundle goes through is identical: the path rule, check_ok, G3, G4, G6, G7, G8 and the apply.
- Each run of the checks leaves its `mktemp -d` folder (a few small files) in TMPDIR or /tmp: four in the dry run and four after the live apply.
- The committed `tests/unit/orchestration/test_cto_safety_nets.py` keeps appending to the live deadman.log whenever it runs, until the CTO's follow-up commit adds the ORCH fixture (`drafts/deadman-wake/test_cto_safety_nets.py`, which needs this ACT). Land that commit right after the ACT.
- The ACT narrows the owner's 2026-11-01 rule (an item unread 30 minutes alerts, during a stand-by too) for the CTO's own wake items. The owner's (b) yes is that decision, so the request for it should say so: with F2's fix, the narrowing applies only outside a stand-by, and always for `-spend-brake`.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": []},
          {"kpi": "4", "verdict": "pass",
           "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
                        {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
                        {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "9749d056afee5587fc7686b04c8338ba4ffb19d3d7bf15d6801c060ded9c9eca",
 "class": "b",
 "reviewer": "independent-auditor, claude -p session started by the CTO's helper a855f83eb96bf46f7; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-10T12:17:36+00:00",
 "replay_refused": []}
```

## Round 2

Bundle: `.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-WAKE-1/` · manifest sha256 `25c3af62cd5192798ab47b6934725ec9160c7632cdcf88a04a6e3cbff5a4c1b5` (recomputed) · brief sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a` (recomputed; as in the install's APPROVED) · reviewer: independent-auditor, a `claude -p` session (round 2) started by the CTO's helper a855f83eb96bf46f7; not the author and not round 1's reviewer · 2026-11-10T12:46:19+00:00.

**Outcome: READY.** The brief's six checks pass and the class is (b). Round 1's F1, F2 and F3 are fixed as proposed. Each fix has a test that fails without it, and F1 and F2 each also have a check that does. One new finding, F4, does not block: an inbox folder that cannot be listed drops the line, against the docstring. Such a folder is not ordinary work, and the dispatcher is blind to it too. Fix F4 with the next deadman.py ACT, not with a rebuild.

### What was checked, and how
Every run was in my own clone of w2/integrate (`git clone --no-hardlinks`, HEAD 9f66e4084), under my own TMPDIR, with HOME planted at an empty folder. ORCH, --log, --state, --session-file, --standby and --inbox-stale all pointed under that TMPDIR. The before copy was never run.

Afterwards, the live files were as before:
- The live deadman.log had grown only by the sentinel's own lines (the real CTO transcript, every 2 minutes). Its planted-transcript lines were still 1083.
- The live state, seen key, wake key, inbox, pings.log and tree were unchanged, apart from other sessions' commits.
- The operator's log changed only by its own 12:40 cron launch.

1. **Touched list and path rule: pass.**
   - One file is touched, `governance/project/orchestration/tools/deadman.py`: before `b425895b…` (the live file, HEAD's and the clone's), after `5d770bfb…`. Every bundle file hashes as the manifest says.
   - In the clone, `apply.sh apply` changed that file only. This was measured by the sha256 and mode of every file in the tree, `.git/hooks` and `.git/config` included. The mode stays 644, no `.act-tmp` is left, nothing lands in the planted HOME, and there is no crontab call.
   - The operator's own `validate_manifest` and `path_rule` (G1), given the live repository and the real HOME, pass `apply.sh` and all six checks.
2. **Undo: pass.**
   - After undo, the whole-tree fingerprint (hashes, modes, hooks, config) and the planted HOME equal those taken before the apply, and `apply.sh check` passes again.
   - The rehearsal log shows the same, and the operator's dry run (point 4) compared the undo byte for byte.
3. **Rehearsal: pass.**
   - The log records a "manifest sha256 before finalize" of `9ffaf2f7…`. That is exactly the final manifest's hash with its rehearsal entry removed (build_act.py's form). So the rehearsal ran this apply.sh, list, before, after and these six checks.
   - It ran in a fresh clone at 13f15785f, with HOME planted (still empty) and its own ORCH, and ran the checks under `env -i`. The log ends `failures: 0`.
   - The live HEAD has since moved to 9f66e4084 (W2-149, W2-20 and ACT-CLAUDE-COPIES-3 records; among the tools, only indep_launch.py changed). deadman.py is unchanged, so `check` still holds on the live file.
4. **Checks: pass.**
   - All six exit and count as the rehearsal printed:
     - check 1: 0 / 1;
     - check 2: 0 / 1;
     - check 3: 0, "HEARTBEAT alive age 0 min";
     - check 4: 10, P1 INBOX;
     - check 5: 0, HEARTBEAT;
     - check 6: 10, P1 INBOX.
   - They did so in four environments:
     - the operator's clean set (PATH, HOME, LANG, USER, LOGNAME, TMPDIR);
     - PATH, HOME and TMPDIR only;
     - TZ=Pacific/Kiritimati with LANG=C;
     - TZ=America/Los_Angeles.
   - I ran the installed operator's own `Run._g8` on a copy of the bundle, cloning from my clone, with its call log sent to my TMPDIR. It ran check, apply, changed set = touched, after as stated, the six checks by `check_ok`, undo byte for byte, and no stray change: PASS.
   - It passed in three clean environments: TZ=UTC; PATH only (no LANG or TZ); TZ=Pacific/Kiritimati with LANG=C. So the operator's dry run can run every check as written.
   - The installed operator still differs from the repository copy only in the guard replay's call-set code and the call log's name.
   - The new checks guard their fixes. With F1's fix undone in a copy of the after file, check 5 turns red; with F2's undone, check 6 turns red. F3 has no check; round 1 asked for none.
   - The ALERT is unchanged:
     - `check()` without the three-line wake block and the log path is textually identical to the before copy's.
     - `quiet()`, `send()`, the limits and every printed line are identical.
     - Runs at the edges agree: alive at 59 min and ALERT at 60 by day; alive at 119 (with the wake) and ALERT at 120 at night; "alerted already" at 1 h 59 and a reminder at 2 h; with --dry, no wake and no state.
5. **Class: (b).**
   - The `watchers` row gives deadman.py class (b). `act_class.classify` on the bundle gives (b) with no script hit, and the claim agrees.
   - In substance the ACT alters a watcher's alerting (see the narrowing in the notes), so the owner's yes is needed: `yes ACT-DEADMAN-WAKE-1 25c3af62`.
6. **Guard replay: pass, nothing to replay.** There is no path-map or deny-list change, so `replay_refused` is empty.

### Round 1's findings
- **F1: fixed as proposed.**
  - `leave_out_inbox_line` returns True when the folder exists and holds no stale item (`all([])`), and False when the folder is missing.
  - The docstring says --stale-s is kept equal to the dispatcher's STALE_S (1800 s).
  - test_r1_f1 covers `-deadman-wake`, `-helper-watch`, `-spend-brake` and a guard item, and check 5 covers the case.
  - Reproduced with a guard item:
    - stale, with the line → push;
    - moved to inbox/read/, line still there → exit 0, and the seen key goes;
    - line gone → exit 0.
  - One gap is left; it is F4 below.
- **F2: fixed as proposed.**
  - In a stand-by only `-spend-brake` items are exempt (`BRAKE_ITEM if standby else WAKE_ITEM`). The docstring and the INBOX_STALE comment now say "outside a stand-by".
  - test_r1_f2 and check 6 cover it.
  - Reproduced in a stand-by:
    - a stale `-deadman-wake` item → exit 10;
    - `-spend-brake-2` → exit 0;
    - no stale item, line present → exit 0;
    - `-spend-brake` plus a guard item → exit 10.
- **F3: fixed as proposed.**
  - AttributeError and TypeError are caught.
  - Key files holding `"x"`, `1`, `null`, `true`, `{"stall": null}`, `{"stall": [1, 2]}` and `[]` each give one item, then "woken already". test_r1_f3 covers `[]`.
- **Tests.** The wake's 11 tests pass on the applied file. On each copy with one fix undone, exactly that fix's round-1 test fails (1 failed, 10 passed, three times).

### The question: the `inbox:` line about any item, left out when no item is stale
This is safe for every producer and for the dispatcher's timing, with F4's exception.
- **The dispatcher's rule matches.**
  - The dispatcher writes the line exactly when `int(now - oldest mtime) >= STALE_S` over `dispatch/inbox/*.txt` (write_status, dispatcher.py lines 3012-3014 and 3076-3077).
  - The watch uses the same folder (the stale file's sibling), the same non-recursive `*.txt` glob, the same mtime and the same 1800 s.
  - Nothing sets `DISPATCH_STALE_S` (run_tick.sh unsets every `DISPATCH_` variable), and the sentinel passes no --stale-s.
  - At one instant the two agree: eight ages from 1798.6 to 2400 s, 0 mismatches.
- **Timing.**
  - The watch always reads the line after the dispatcher wrote it, and an item's age only grows while it stays in the folder.
  - So the watch finds no stale item only when every item behind the line has left the folder since. That means it was read: the CTO moves items to inbox/read/, which neither glob counts.
  - The dispatcher's next pass (cron, every minute) then removes the line too. The only window where the two differ is between a read and that pass, which is exactly F1's case.
- **Producers and readers.**
  - Every producer writes a new `<stamp>-<name>.txt` once, at the folder's top level, so its mtime is its write time. None rewrites or touches an item later.
    - With `open(…, "x")`: dispatcher.inbox_item, deadman.wake, helper_watch.py, spend.py, land.py.
    - With noclobber: landing_select.sh.
    - With `> <stamp>-<name>.txt`: gpu_backstop.sh, rerank_reset_watch.sh, bare_watch.sh, sentinel_check.sh.
  - inbox_wait.sh only lists. inbox_wait_quiet.sh files quieted server-hung items into inbox/read/, which both sides then stop counting.
  - So no producer can make an item look fresher to the watch than to the dispatcher.
- **New with F1's fix (a note, not a finding).**
  - The dispatcher keeps its inbox line as first written while any item stays stale (lines 3086-3097).
  - Suppose a look falls between a read and another item going stale. The seen key goes, and that next stale item pushes once more with the first-written text, which names the item already read.
  - Reproduced: exit 10, then 0, then 10. Before the ACT that second item never pushed.
  - So the change adds one push, about a real stale item, under a misleading name.

### Findings

#### F4 — an inbox folder that cannot be listed drops the line, though the docstring says it keeps it
- KPI 4 · scope in · ordinary_work no (the folder is the dispatcher's, mode 755; it takes a chmod from outside) · consequence fails open (bounded, see below) · not blocking.
- **What happens:**
  - The docstring and round 1's fix say a missing or unreadable folder keeps the line ("fail toward the push").
  - But `Path.glob` (Python 3.12) swallows the PermissionError from a folder it cannot list and yields nothing. So `old` is empty, `all([])` is True, and the line is left out with no push.
  - A folder that can be read but not searched (mode 600) does keep the line, because the stat raises and is caught. So does a missing folder, or a file where the folder should be.
- **Evidence (the after copy, a guard item stale 40 minutes, the line present):**
  - inbox folder mode 000 → exit 0, HEARTBEAT;
  - mode 600 → exit 10;
  - a file named `inbox` → exit 10.
- **Why it does not block:**
  - The dispatcher lists the folder the same way (`unread()`), so it reads it as empty too and removes its line on its next pass, within a minute.
  - Before the ACT, a push came only if the watch's 120 s look fell inside that minute.
  - The whole system is already blind to such a folder: the dispatcher and both inbox waiters.
- **Fix, in the next deadman.py ACT:**
  - List the folder with `os.scandir(box)`, which raises and is caught (so the line is kept), or test `os.access(box, os.R_OK | os.X_OK)` first.
  - Add a test: mode 000 folder → exit 10.
  - Or correct the docstring to "a missing folder, or items that cannot be read, keep it".

### Notes (not findings)
- **The narrowing, for the owner's yes.**
  - Outside a stand-by, a stale `-deadman-wake` or `-helper-watch` item reaches the owner only through the stall ALERT, that is, once the CTO itself has been idle 60 minutes by day or 2 hours at night.
  - While the CTO is active but not reading its inbox (a waiter not re-armed, DEC-1007's case), such an item never pushes. The docstring's "whose staleness the stall's own ALERT already covers" holds only for an idle CTO.
  - A `-spend-brake` item never pushes, stand-by or not (DEC-1089 (3)). Every other item pushes as before, during a stand-by too.
- **STALE_S equality is a convention only; nothing tests it.** If the dispatcher's default ever dropped below 1800 s, the watch would delay the push to 30 minutes (bounded). A higher default has no effect.
- **Check 6** passes `--standby` twice; argparse takes the last, the planted stand-by file. Its line also names a wake item that is not in the folder. It still guards F2 (see point 4).
- **The committed `tests/unit/orchestration/test_cto_safety_nets.py`.**
  - It still appends to the live deadman.log whenever it runs, as round 1 noted.
  - After the ACT it writes no wake item into the live inbox: its non-dry runs pass a temp --state, and its runs on the live state pass --dry.
  - Land the CTO's ORCH-fixture commit right after the ACT.
- **This reviewer's own stray write.**
  - Importing act_class from the install without `-B` wrote `~/gov-os-operator/install/__pycache__/act_class.cpython-312.pyc` (12:37:49), outside my TMPDIR.
  - The APPROVED check and the install's control hash skip `__pycache__`, and the operator's 12:40 launch reported idle.
  - The operator writes the same file on its own first import. I left it in place.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": []},
          {"kpi": "4", "verdict": "pass",
           "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "25c3af62cd5192798ab47b6934725ec9160c7632cdcf88a04a6e3cbff5a4c1b5",
 "class": "b",
 "reviewer": "independent-auditor, claude -p session (round 2) started by the CTO's helper a855f83eb96bf46f7; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-10T12:46:19+00:00",
 "replay_refused": []}
```
