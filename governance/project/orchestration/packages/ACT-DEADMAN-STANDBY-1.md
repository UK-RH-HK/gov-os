# ACT-DEADMAN-STANDBY-1: a stand-by note expires after 2 hours, so a stale one can never mute the dead-man again

## 0. What the owner says
Class **(b)**: the owner's yes, then the operator agent. The line the operator agent reads, on its own line:

yes ACT-DEADMAN-STANDBY-1 824cfc16

**What the yes decides.**
- A stand-by note (`log/cto-standby.txt`) mutes the dead-man only while it is **under 2 hours old**. The default is
  7200 seconds; the flag `--standby-max-s` changes it.
- After that the normal logic applies: the stall ALERT (60 minutes by day, 2 hours from 02:00 to 07:30), the wake item,
  and the inbox-line rules for a CTO that is not in a stand-by.
- A CTO that is still waiting on the owner renews the note by writing a new time into it. A CTO that is idle, or
  handed over without removing the note, is alerted once the 2 hours are up.
- **The one number the owner may change before the yes is the 2 hours** (§7, first item).

- **For:** the owner's yes, then the operator agent (as ACT-DEADMAN-WAKE-1 ran). One file changes:
  `governance/project/orchestration/tools/deadman.py`, a control path (class-rules.yaml row `watchers`).
- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-10, on the owner's decision of the same day (chat): "A
  stand-by note expires after a set time, so a stale one can never mute the dead-man for hours again." Built and
  rehearsed in a throwaway clone. **Nothing live changes until it runs.** The live file was only read; this package and
  its bundle are not committed.
- **Under:** DEC-998 (the dead-man's switch; the stand-by note), DEC-1112 (3) (what the CTO brings the owner: a change to
  a control path is a (b) ACT), DEC-1057 (rehearsed), OPERATOR-AGENT-1 §2 and §3. The owner's decision of 2026-11-10 has
  no DEC number yet; the CTO's record names it.
- **Bundle:** built in `.gov-runtime/scratch/orchestrator/drafts/act-deadman-standby-1/acts/ACT-DEADMAN-STANDBY-1/`. The CTO
  copies that folder to `.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-STANDBY-1/` (the manifest names no place of its
  own; its hash does not change). **Manifest sha256
  `824cfc1613cf6d0f2c3f48b09407ff8931dd1896022049a9a37184dad48a7c8d`.**
- **Review:** `review.md` is **absent now**, as ACT-EFFORT-HIGH-2's was at its build. The CTO launches the review under
  the operator's fixed reviewer brief (`~/gov-os-operator/install/reviewer-brief.md`, `e86703304144…`) and drops the
  result into the bundle as `review.md`, with `reviewer_brief_sha256` set to the brief's line in `install/APPROVED`. The
  yes line stays valid if the bundle is not rebuilt; a rebuild changes the sha8 and the CTO brings a new line.

## 1. Why
On 2026-11-10 a CTO session wrote the stand-by note at 15:49:50 UTC while it waited on the owner ("2026-11-10 15:49:50
CTO 412a4e37 waits on the owner: ..."). It handed over without removing the note. The dead-man (`deadman.py`, DEC-998)
suppresses its ALERT while the note exists, so it stayed muted until 19:18: **about 3.5 hours** with a session that had
stopped, and no push. The dead-man's whole purpose is that a stopped session is noticed; one forgotten file switched it
off with nothing to end the mute.

The rule in force until now was "the note exists" (`deadman.py` line 57, the constant `STANDBY`; the verdict
`standby: ...` at line 212). This ACT replaces it with "the note exists and is young".

## 2. What it does (one file: before `5d770bfbfa52`, after `040b4d710f81`; 57 lines added, 4 changed)
- **The age.** Read from the UTC time that leads the note (`YYYY-MM-DD HH:MM:SS`, a space or `T`, an optional `Z`),
  else from the file's mtime.
  - A note whose leading time is more than 5 minutes ahead of the clock is not believed. The mtime is read instead.
    With the mtime ahead too, the note is expired. So a typo in the year can never mute for good.
  - A file that cannot be read, or has no usable time at all, is expired: the doubt goes toward the alert.
  - A time up to 5 minutes ahead of the clock (skew) still counts as fresh.
- **Fresh note (under the limit): nothing changes.** The verdict is `standby: <the note, 120 characters>` as before; no
  ALERT, no wake, and in the watch the inbox exemptions of ACT-DEADMAN-WAKE-1 apply as for a stand-by.
- **Expired note: the normal logic.**
  - The logged note gets a field `"standby": "expired (written 2026-11-10 15:49 UTC, 208 min ago)"`.
  - The verdict is the normal verdict (`alive`, `ALERT`, `stalled, alerted already`). It is not replaced by a text
    verdict, because the watch and the sentinel act on `ALERT`.
  - An ALERT line then ends with `| its stand-by note had expired (written 2026-11-10 15:49 UTC, 208 min ago)`, so the
    owner reads why the push came. A line with no note is byte for byte as before (manifest check 4).
  - The wake item (one per stall, ACT-DEADMAN-WAKE-1) is written again, because there is no stand-by any more. It wakes
    the CTO's inbox waiter, which gives a living session the moment to renew or remove its note.
  - The watch's inbox-line rules (`leave_out_inbox_line`) read the note the same way: an expired note counts as no
    stand-by.
- **The limit.** `--standby-max-s`, default 7200 (the new constant `STANDBY_MAX_S`).
- **Unchanged:** the ALERT's limits, reminders and state; the wake; `--dry`; every flag; the exit codes; the log's other
  fields; the file's imports.
- **The other readers of the file:**
  - `sentinel_check.sh` (in the scratch `tools/`, not in the repository) and the dispatcher (`tools/dispatch/*`) do not
    read `cto-standby.txt`; the sentinel only reads `deadman.log`'s age and starts `deadman.py --watch`.
  - `stop_waiter_check.py` (a Stop hook) tests `cto-standby.txt` with `.exists()`, to let a turn end with no waiter
    armed. It is **not** changed here and does not mute the dead-man (§7).

## 3. The class
**(b).**
- class-rules.yaml's `watchers` row names `governance/project/orchestration/tools/deadman.py` (b, a control path).
- The operator's own `act_class.classify` on the bundle gives (b) with no script hits (gates log below).
- The new unit cases are not in the ACT. Their path (`tests/unit/orchestration/test_cto_safety_nets.py`) falls to the
  catch-all row, (O). They are the CTO's own commit after the ACT (§6).

## 4. Rehearsal and gates (DEC-1057; 0 failures)
- **The bundle's rehearsal** (`rehearsal.log`, sha256 `8b9d7b4fa2f2…`, hashed in the manifest), produced by
  `drafts/act-deadman-standby-1/rehearse.sh`. It ran in a fresh `--no-hardlinks` clone of `w2/integrate` at
  `c9742b08910a`, with HOME planted at an empty folder and ORCH at the rehearsal's own folder (inside `drafts/`):
  1. `check` (exit 0), `verify` before the apply (3), `apply` (0), `verify` (0). The mode stays 644 and the changed set
     is exactly the touched file.
  2. The six manifest checks, each in the operator's clean environment with the planted HOME (standard library and
     coreutils only):
     - a note 70 minutes old (idle since 15:49): the verdict `standby: 2026-11-10 15:49:50 CTO ...`, count 1;
     - the same note at 19:18 (the incident): the ALERT line, byte for byte, with the expiry words, count 1;
     - a note with no time, its mtime set to 15:49:50 UTC, at 19:00: `"standby": "expired (written ... 190 min ago)"`,
       count 1;
     - no note at all: the day ALERT line byte for byte as before, count 1;
     - the sentinel's `--watch` with a note written now and a session stalled since 11-01: HEARTBEAT standby, exit 0;
     - the same with a note 3 hours old: ALERT, exit 10.
  3. **The safety nets' unit file** (`tests/unit/orchestration/test_cto_safety_nets.py`), on the applied file in the
     clone:
     - the CTO's current file (the working tree's, with its `isolated(tmp_path)` cases): **9 passed**;
     - the same file with **6 new cases**: **15 passed**.
  4. **Red first:** `undo`, then the 15-case file on the before: **5 failed, 10 passed**. The five failures are the
     expiry cases (expired note, live session with an expired note and the flag, mtime fallback, time ahead of the
     clock, the watch). The fresh-note case passes on the before as well: it pins the old behaviour.
  5. `undo`: byte for byte the before; `check` 0. Planted faults: a moved live file is refused by `check` (exit 3,
     "moved: ..."); a tampered frozen copy is refused by `apply` (exit 4), the file untouched.
  6. **Nothing live written:** the live deadman.py, sentinel-brief.md, deadman-state.json, the live log's planted-line
     count, the live inbox's wake items, the wake key and the tree's status were the same before and after. Nothing was
     written to the planted HOME.
- **The new cases** (`test_cto_safety_nets.py`, sha256 `09c11e4bc3e9…`):
  - a fresh note still mutes, at 70 minutes and at 119 minutes 10 seconds;
  - an expired note alerts, the line and the field exact, at 19:18 and just past the limit (2 h 0 min 10 s);
  - the flag sets the limit (600 s expires a 40-minute note; 3600 s keeps it);
  - a note with no time is aged by the mtime, fresh at 16:30 and expired at 19:00;
  - a time ahead of the clock never mutes for good (year 2030 with an old mtime, with a 2030 mtime too; 5 minutes of
    skew still mutes);
  - the watch alerts on an expired note, and a stale helper-watch item pushes in a live stand-by and does not after
    the expiry.
  Each case runs with the switch's files in its own folder (`isolated(tmp_path)`) and the clock set with `TZ=UTC`.
- **The operator's gates, read-only** (`build_act.py gates`):
  - `validate_manifest`: pass;
  - all 5 files hash as the manifest states;
  - the path rule over `apply.sh` and the six checks: pass;
  - `act_class.classify`: (b), no hits.
- **Not run:** the wake's own 11 tests (`drafts/deadman-wake/test_deadman_wake.py`, not yet committed) on the applied
  file, and the full suite, because a D-10 run was using the machine and the brief limited the runs to the one unit
  file. The wake and the ALERT paths are unchanged in the diff; checks 1 to 4 show the unchanged line and the fresh
  mute. The CTO can run the wake's tests against the clone before the yes.

## 5. The operator's steps (the yes line again)
yes ACT-DEADMAN-STANDBY-1 824cfc16

**The queue request** (not queued; the CTO writes it after the yes), `~/gov-os-operator/queue/ACT-DEADMAN-STANDBY-1.req`,
one line:

ACT-DEADMAN-STANDBY-1 824cfc1613cf6d0f2c3f48b09407ff8931dd1896022049a9a37184dad48a7c8d

**By the operator agent:** the agent runs the bundle through G1 to G9, applies it, runs the six checks and commits the
one file with its own trailers.

**The message for the owner's operator** (if by hand, rehearsed):
> **ACT-DEADMAN-STANDBY-1 (DEC-998, DEC-1112 (3)): a stand-by note mutes the dead-man for 2 hours at most.** Class (b),
> about a minute, in the main tree.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean   # expect: clean
> G=.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-STANDBY-1
> sha256sum $G/manifest.json      # expect 824cfc1613cf6d0f2c3f48b09407ff8931dd1896022049a9a37184dad48a7c8d
> bash $G/apply.sh check          # silent, exit 0 (a "moved: <path>" line: stop, tell the CTO)
> bash $G/apply.sh apply          # silent, exit 0
> bash $G/apply.sh verify         # silent, exit 0
> git add governance/project/orchestration/tools/deadman.py
> git diff --cached --name-only   # expect exactly: governance/project/orchestration/tools/deadman.py
> git commit -m "ACT-DEADMAN-STANDBY-1: a stand-by note older than 2 hours no longer mutes the dead-man (deadman.py 5d770bfbfa52 -> 040b4d710f81)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-998, DEC-1112" --trailer "Role: owner"
> ```
> **Undo:** `bash $G/apply.sh undo`, then `git add` the file and commit with the same trailers (rehearsed, byte for
> byte).

The `git status` line expects a clean tree for tracked files. The working tree's `tests/unit/orchestration/test_cto_safety_nets.py`
(the isolated cases, uncommitted when this was written) must be committed first, or the line stops the steps. Its 9
cases pass on the old and the new `deadman.py` alike (rehearsal, step 3), so the CTO commits that version before the
yes; the 6 new cases follow the ACT (§6).

## 6. After it (the CTO's)
- **The sentinel needs no restart.** It starts a fresh `deadman.py --watch` after every exit (an ALERT, the HEARTBEAT at
  `--max 6600`, or the 09:05 DAILY line), so the new code runs within 110 minutes. Never stop the running watch to
  hurry it.
  - Check: the first `deadman.log` line written while an expired note stands carries `"standby": "expired (...)"`.
- **The CTO's commit** (CTO-owned path, `Role: orchestrator`), from `drafts/act-deadman-standby-1/`:
  `tests/unit/orchestration/test_cto_safety_nets.py` (sha `09c11e4bc3e9`: the isolated cases plus the 6 new ones;
  `test_cto_safety_nets.patch`, sha `b089bd8233f0`, is the difference from the isolated-only file,
  `test_cto_safety_nets.py.worktree`, `fbff6ec2b06a`, the one to commit before the yes). Commit the new file **after**
  the ACT: before it, 5 of its cases fail on the old `deadman.py`.
- **The prompt line.** `governance/project/prompts/w2-orchestrator.md` and the stand-by habit: a session that stands by
  writes its UTC time first (`date -u '+%F %T'`) and rewrites it when it still waits; one that ends the stand-by removes
  the file. The tool reads the leading time and falls back to the mtime, so a note without it still expires.
- **The scratch copy:** `.gov-runtime/scratch/orchestrator/tools/deadman.py` is copied from the committed file after the
  ACT. Nothing runs it.

## 7. Residuals, and what the owner may change
- **The 2 hours (the owner's number).** Why 2 hours:
  - It equals the quiet hours' limit, so an idle CTO on a stand-by is noticed no later than a stalled one at night.
  - The incident's mute was 3.5 hours; at 2 hours the same note would have been dead at 17:49.
  - A stand-by on the owner that really lasts that long is rare, and a renewal costs one line of the CTO.
  - **The cost of a shorter limit** (1 hour or less): a CTO waiting on a long decision pushes the owner by day. **The
    cost of a longer one** (3 to 4 hours): a forgotten note mutes for that long. `--standby-max-s` is a flag, but the
    sentinel starts `deadman.py --watch` without it; **changing the default is a new ACT** (the constant
    `STANDBY_MAX_S`), as is naming the flag in the sentinel's command.
- **A long stand-by now alerts.** A CTO that waits on the owner overnight (say 9 hours) with no one to renew the note
  is pushed at the 2 hours' end, then every 2 hours (the ALERT's own reminder). That is the owner's decision
  working as written. The wake item reaches the CTO's inbox waiter at the same moment, if one is armed.
- **The time must be UTC.** A note led by a local time is aged by its offset from UTC: a local time ahead of UTC
  looks like the future and the mtime is read, a local time behind it makes the note older than it is. The 11-10 note
  was UTC.
- **`stop_waiter_check.py` is not changed.** It tests `.exists()` to let a turn end with no inbox waiter armed. A stale
  note still lets a turn end without a waiter; it does not mute the dead-man. Giving it the same expiry is a separate
  (b) ACT (its row is the same kind); the owner says whether to ask for it.
- **An expired note is not removed.** The tool reads the file and never writes `cto-standby.txt`; the CTO or the owner
  removes it.
- **A file that vanishes between the two reads** counts as expired for that one look: toward the alert.
- **F4 of ACT-DEADMAN-WAKE-1** (an inbox folder that cannot be listed drops the dispatcher's line; fix `os.scandir`) is
  still carried to a later deadman.py ACT; this one does not take it, so the scope stays one rule.

## 8. The files
Paths below are relative to `.gov-runtime/scratch/orchestrator/drafts/act-deadman-standby-1/`.

| File | sha256 (first 12) | What |
|---|---|---|
| `acts/ACT-DEADMAN-STANDBY-1/manifest.json` | `824cfc1613cf` | the manifest |
| `…/apply.sh` | `2f3f86f5551d` | check, apply, undo, verify by list.txt; relative to its cwd |
| `…/list.txt` | `03d67ce9d7f6` | the one file, before and after |
| `…/before/repo/…/deadman.py`, `…/after/repo/…/deadman.py` | `5d770bfbfa52`, `040b4d710f81` | the frozen copies |
| `…/rehearsal.log` | `8b9d7b4fa2f2` | the rehearsal, `failures: 0` |
| `deadman.patch` | `dbe89e77a45b` | the change as a unified diff (`patch -p0` on a copy of the before) |
| `build_act.py`, `rehearse.sh` | `ffe94a1d02c9`, `29d18dbcae80` | the builder and the rehearsal |
| `test_cto_safety_nets.py`, `test_cto_safety_nets.patch` | `09c11e4bc3e9`, `b089bd8233f0` | the CTO's commit after the ACT |
| `test_cto_safety_nets.py.worktree` | `fbff6ec2b06a` | the isolated-only file, as the working tree held it: the CTO's commit before the yes |

[DEC-998, DEC-1112 (3), DEC-1057, OPERATOR-AGENT-1 §2 and §3; the owner's decision of 2026-11-10 (chat); ACT-DEADMAN-WAKE-1
(the form, and the wake and inbox rules this keeps)]
