# ACT-DEADMAN-WAKE-1: the dead-man's switch wakes the CTO through its own inbox at 60 minutes, at any hour

## 0. What the owner says
Class **(b)**: the owner's yes, then the operator agent. The line the operator agent reads, on its own line:

yes ACT-DEADMAN-WAKE-1 25c3af62

**What the yes also decides** (both reviewers asked that it be named). It narrows the owner's rule of 2026-11-01, that
an inbox item unread 30 minutes alerts, during a stand-by too:
- outside a CTO stand-by, the CTO's own wake items (`-deadman-wake`, `-helper-watch`) reach the owner only through
  the stall ALERT, with its own limits;
- `-spend-brake` items never push (DEC-1089 (3));
- a dispatcher line about an item already read no longer pushes.

Every other unread item pushes exactly as before. In a stand-by, the wake and helper-watch items push as before.

- **For:** the owner's yes, then the operator agent (as ACT-CLAUDE-COPIES-2 ran). One file changes:
  `governance/project/orchestration/tools/deadman.py`, a control path (class-rules.yaml row `watchers`).
- **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-10, built and rehearsed by a helper agent. **Nothing live changes
  until it runs.** The first version was committed directly (`b0eb21f1a`), which was wrong for a control path; the
  landing check raised a P1, and the CTO reverted it (`09e1ff6e1`). This ACT replaces it, with the code review's fixes.
- **Under:** DEC-998 (the dead-man's switch through the Claude app; the sentinel), DEC-1112 (3) (what the CTO brings
  the owner: a change to a control path is a (b) ACT), DEC-1089 (3) (usage never an alarm to the owner), DEC-1057
  (rehearsed), OPERATOR-AGENT-1 §2 and §3.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-WAKE-1/`. **Manifest sha256
  `25c3af62cd5192798ab47b6934725ec9160c7632cdcf88a04a6e3cbff5a4c1b5`.**
- **Review:** `review.md` in the bundle, under the operator's fixed reviewer brief (`e86703304144…`), by two fresh
  read-only `claude -p` independent-auditor sessions, neither of them the author.
  - **Round 1:** NOT READY at `9749d056`. F2 blocked: in a stand-by, a stale helper-watch item failed open. F1 was a
    false push after a read; F3 a crash on a malformed key.
  - All three were fixed tests first, the bundle rebuilt and re-rehearsed.
  - **Round 2:** **READY** at `25c3af62` by the pinned `verdict.py` (the last of 2 blocks decides; `(True, [])`). One
    low finding, F4, is carried (§7).
  - Each reviewer's role cannot write, so the CTO's helper appended its returned text unchanged. Their session logs
    are in `drafts/deadman-wake/review-round{1,2}.session.json`.

## 1. Why
On 2026-11-10, at about 02:19 to 02:26 UTC, a short network fault (EAI_AGAIN) killed two of the CTO's in-session
helpers. Their failure notices did not wake the CTO session. It sat idle from 02:35 until a scheduled prompt at 09:30:
**7 hours lost**. The API was reachable again from about 02:50.

The dead-man raised ALERT at 04:35, 06:35 and 08:37 (the night limit is 2 hours), and the sentinel pushed each time.
None of the pushes reached the owner, and none of them could wake the CTO. Throughout, the CTO's inbox waiter
(`inbox_wait_quiet.sh`) was armed: any new file in `dispatch/inbox/` would have woken the CTO.

## 2. What it does (one file: before `b425895b3aba`, after `5d770bfbfa52`)
- **The wake.** Once the watched session's last `assistant` entry is 60 minutes old, **at any hour**, the switch writes
  one item, `dispatch/inbox/<stamp>-deadman-wake.txt`. The item holds the stall line and "check the helpers and resume
  them".
  - One item per stall; the key is in `log/deadman-wake-state.json`. The key is written first, atomically, so a key
    that cannot be written gives no item, never one every 2 minutes. A key that is not a JSON object is read as no key
    (ACT review F3).
  - No wake in a stand-by (`cto-standby.txt`) or with `--dry`.
  - **It writes only into the CTO's inbox.** It sends no push itself.
- **The push is unchanged.** The ALERT text, its limits (60 minutes by day, 2 hours from 02:00 to 07:30), its
  reminders and the sentinel's handling are all unchanged. This is shown by checks 2 and 4, the diff of the two
  copies, and round 1's comparison: 672 alarm scenarios, 0 mismatches.
- **The inbox-stale exception.**
  - The dispatcher turns any item unread for 30 minutes into an `inbox:` line in `inbox-stale.txt`, and the watch
    turns that line into a push at any hour.
  - So an unread wake item would bring the night push forward. An unread spend-brake item would alarm the owner,
    which DEC-1089 (3) forbids.
  - The watch now re-reads the inbox folder before it uses the dispatcher's line. The CTO's own wake items are names
    ending `-deadman-wake`, `-helper-watch` or `-spend-brake`, with an optional `-<n>`, matched on the suffix.
    - **No item unread past 30 minutes:** the line dates from before a read, so it is left out (ACT review F1). A
      missing or unreadable folder keeps the line, failing toward the push.
    - **Outside a CTO stand-by:** the line is left out only when every stale item is a wake item. The stall's own
      ALERT covers those.
    - **In a stand-by, when the ALERT is silent by design:** the line is left out only when every stale item is a
      `-spend-brake` item (DEC-1089 (3)). A stale `-helper-watch` or `-deadman-wake` item pushes as before (ACT review
      F2).
    - Any other stale item pushes exactly as before, even behind a wake item (code review finding 2).
  - **What the owner's yes also decides.** This narrows the owner's rule of 2026-11-01 (an inbox item unread 30
    minutes alerts, during a stand-by too). After the yes:
    - outside a stand-by, the CTO's own wake items no longer alert on staleness;
    - `-spend-brake` items never alert;
    - a line about an item already read no longer alerts.
- **Its files are movable, for tests.** It honours ORCH, and it gains `--log`, `--inbox` and `--stale-s` beside the
  existing `--state`, `--session-file`, `--standby` and `--inbox-stale`. A test or rehearsal never touches the live
  log, state or inbox.
  - Today two test runs of the old file (which could not be redirected) appended planted lines to the live
    `deadman.log`, and the dispatcher read them as "sentinel silent since 03:40": a false alarm.
  - The wake's tests now refuse to run against any copy without `--log`.

## 3. The class
**(b).**
- class-rules.yaml's `watchers` row names `governance/project/orchestration/tools/deadman.py` (b, a control path).
- The operator's own `act_class.classify` on the bundle gives (b) with no script hits (gates log below).
- The reviewers' class: (b), both rounds. Code, claim and review agree.
- The wake's test, the README line and the safety nets' ORCH fixture are not in the ACT. Their paths fall to the
  catch-all row, (O) in a manifest. They are the CTO's own commit after the ACT (§6).

## 4. Rehearsal and gates (DEC-1057; 0 failures)
- **The bundle's rehearsal** (`rehearsal.log`, sha256 `0d4839ba932d…`, hashed in the manifest), produced by
  `drafts/deadman-wake/rehearse.sh`. It ran in a fresh `--no-hardlinks` clone of `w2/integrate` at `13f15785f91f`,
  with HOME planted at an empty folder and ORCH at the rehearsal's own folder:
  1. `check` (exit 0), then `verify` before the apply (3), `apply` (0), `verify` (0). The mode stays 644, and the
     changed set is exactly the touched file.
  2. The six manifest checks, each in the operator's clean environment with the planted HOME. They use the standard
     library and coreutils only, because the operator's dry run plants HOME and the user site's pytest is not there:
     - the night wake: count 1, verdict alive;
     - the day ALERT line byte for byte: count 1;
     - a stale wake item alone: no push, exit 0;
     - a stale guard item behind it: the push, exit 10;
     - the line left over after a read (F1): no push, exit 0;
     - a stale helper-watch item in a stand-by (F2): the push, exit 10.
  3. The wake's tests on the applied file: 11 passed. The safety nets with the post-ACT fixture: 9 passed.
  4. `undo`: byte for byte the before, the tree clean, `check` 0.
  5. Planted faults: a moved live file is refused by `check` (exit 3, "moved: …"). A tampered frozen copy is refused
     by `apply` (exit 4), with the file untouched.
  6. **Nothing live written.** These were the same before and after the run:
     - the live deadman.py, sentinel-brief.md, deadman-state.json and cto-session.txt (hashes);
     - the live log's planted-line count;
     - the live inbox's wake items (0);
     - the live wake key (absent);
     - the live tree's status.

     Nothing was written to the planted HOME.
- **The operator's gates, read-only:**
  - `validate_manifest`: pass;
  - all 5 files hash as the manifest states;
  - the path rule over `apply.sh` and the six checks: pass;
  - `act_class.classify`: (b), no hits.
- **Red first:**
  - Every test passes on the candidate (11).
  - The module refuses to run on the live (old) copy, because it has no `--log`.
  - Two mutants restoring the code review's faults (the name-substring filter; the key written after the item) each
    fail exactly their test.
  - The three `test_r1_*` cases for round 1's F1, F2 and F3 were red on the round-1 candidate before the fix.

## 5. The operator's steps (the yes line again)
yes ACT-DEADMAN-WAKE-1 25c3af62

**By the operator agent:** after the owner's yes, the CTO writes the request line (the ACT's id and the manifest sha)
in `~/gov-os-operator/queue/`. The agent then runs the bundle through G1 to G9, applies it, runs the six checks and
commits the one file with its own trailers.

**The message for the owner's operator** (if by hand, rehearsed):
> **ACT-DEADMAN-WAKE-1 (DEC-998, DEC-1112 (3)): the dead-man's switch writes one inbox item at 60 minutes, at any hour,
> so the CTO wakes itself; the push and its limits unchanged.** Class (b), about a minute, in the main tree.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean   # expect: clean
> G=.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-WAKE-1
> sha256sum $G/manifest.json      # expect 25c3af62cd5192798ab47b6934725ec9160c7632cdcf88a04a6e3cbff5a4c1b5
> bash $G/apply.sh check          # silent, exit 0 (a "moved: <path>" line: stop, tell the CTO)
> bash $G/apply.sh apply          # silent, exit 0
> bash $G/apply.sh verify         # silent, exit 0
> git add governance/project/orchestration/tools/deadman.py
> git diff --cached --name-only   # expect exactly: governance/project/orchestration/tools/deadman.py
> git commit -m "ACT-DEADMAN-WAKE-1: the dead-man's switch wakes the CTO through its inbox at 60 minutes, at any hour; the push and its limits unchanged (deadman.py b425895b3aba -> 5d770bfbfa52)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-998, DEC-1112" --trailer "Role: owner"
> ```
> **Undo:** `bash $G/apply.sh undo`, then `git add` the file and commit with the same trailers (rehearsed, byte for
> byte).

## 6. After it (the CTO's)
- **The sentinel needs no restart.** It starts a fresh `deadman.py --watch` after every exit (an ALERT, the HEARTBEAT
  at `--max 6600`, or the 09:05 DAILY line), so the new code runs within 110 minutes.
  - Never stop the running watch to hurry it: the sentinel would push "the watch failed" to the owner.
  - Check: `log/deadman-wake-state.json` appears at the first stall past 60 minutes, and every `deadman.log` line
    carries `"wake"` once a stall passes 60 minutes.
- **The CTO's commit** (CTO-owned paths, `Role: orchestrator`), from `drafts/deadman-wake/`:
  - `test_deadman_wake.py` (sha `bb93a3d2a98e`), beside the tool;
  - the README's dead-man entry (`README.md`, `19ca1cc5bc46`);
  - `tests/unit/orchestration/test_cto_safety_nets.py` with an autouse ORCH fixture (`ae515211d08f`), so that suite
    stops appending to the live `deadman.log`, as it does on every run today.
- **The scratch copy:** `.gov-runtime/scratch/orchestrator/tools/deadman.py` equals HEAD's (the old file) now, and is
  copied from the committed file after the ACT. Nothing runs it.

## 7. Residuals
- **The wake needs an armed waiter.** It wakes the CTO only while `inbox_wait_quiet.sh` runs in the CTO session.
  - If the woken turn itself fails (the network still down), the waiter has already exited and nothing re-arms it.
    The next stall's wake then has no listener, and the push is the backstop.
  - The helper watch (`tools/helper_watch.py`, below) keeps running, but it writes items; it does not wake on its
    own.
- **One wake per stall.** A CTO that is woken but does not act produces no second wake for the same stall.
- **Until this ACT runs**, an unread helper-watch or spend-brake item still makes the dispatcher's inbox-stale line
  and a push after 30 minutes, as any inbox item does today.
- **F4 (round 2, low, carried to the next deadman.py ACT):** an inbox folder that cannot be listed (a chmod from
  outside) drops the dispatcher's line. Python 3.12's `Path.glob` returns nothing there instead of raising. The
  dispatcher lists the folder the same way and drops its own line within a minute, so at most one push is lost.
  - Fix: `os.scandir` there.
  - Also from round 2: the equality of `--stale-s` and the dispatcher's `STALE_S` (1800 s on both sides) is a
    convention that nothing tests.
- **Outside a stand-by, a CTO that is active but not reading its inbox** gets no push for a stale wake or helper item:
  the stall ALERT covers only a stalled CTO. This is the narrowing in §0.
- **The ALERT's own state file** has the same not-an-object pattern as F3 (round 1); left as it was, so the ALERT is
  unchanged.
- **Claude Code internals:** the transcript's entry types and the sentinel's loop, as checked on 2026-11-10.

## 8. The files
| File | sha256 (first 12) | What |
|---|---|---|
| `acts/ACT-DEADMAN-WAKE-1/manifest.json` | `25c3af62cd51` | the manifest |
| `…/apply.sh` | `6107995519fb` | check, apply, undo, verify by list.txt; relative to its cwd |
| `…/list.txt` | `dd2282b8a8e3` | the one file, before and after |
| `…/before/repo/…/deadman.py`, `…/after/repo/…/deadman.py` | `b425895b3aba`, `5d770bfbfa52` | the frozen copies |
| `…/rehearsal.log` | `0d4839ba932d` | the rehearsal, `failures: 0` |
| `…/review.md` | `0a5ed1a01774` | rounds 1 and 2 under the operator's fixed brief (`e86703304144…`); READY |
| `drafts/deadman-wake/build_act.py`, `rehearse.sh` | `0557364c4ad7`, `e1528a016d00` | the builder and the rehearsal |
| `drafts/deadman-wake/test_deadman_wake.py`, `README.md`, `test_cto_safety_nets.py` | `bb93a3d2a98e`, `19ca1cc5bc46`, `ae515211d08f` | the CTO's commit after the ACT |

[DEC-998, DEC-1112 (3), DEC-1089 (3), DEC-1057, OPERATOR-AGENT-1 §2 and §3; the code review of 2026-11-10 (NOT READY,
findings 2 and 4 fixed here); the ACT review, rounds 1 and 2 (READY); revert `09e1ff6e1`]
