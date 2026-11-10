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
