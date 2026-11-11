# ACT-IDLE-GUARD-1: the CTO's idle check cannot pass silently while a ticket could launch (DEC-1110 (1), DEC-1109 (3), DEC-936 item 2)

> **Review:** round 1 **READY**, class (O) (2026-11-11, `reviews/ACT-IDLE-GUARD-1-review-r1.md`; rows F1-F6: a follow-up ACT for the F1 wording, the F2 merged-ticket filter and the F3 timeout). `max_leads: 3` written to `dispatch/config.json` before the apply (F4), 18:50. Yes line: `yes ACT-IDLE-GUARD-1 a49a4228`.


- **For:** the owner's yes, then the owner's operator by hand (§5). About two minutes in the main tree.
- **By:** an ACT-preparation helper of the CTO (Sonnet, high; RUBRIC-2), 2026-11-11 ~18:00 UTC. **Nothing live was changed
  or started:** no commit, no stage, no live hook, no live dispatcher, no crontab, no `.claude/`. The main tree stayed
  clean. Built and rehearsed in clones (§6). **Not yet independently reviewed** (§7).
- **Under:** DEC-1110 (1) (the stop-hook check against idling), DEC-1109 (3), DEC-936 item 2 (the owner's standing rule
  1: never idle while unblocked work remains); all three ACCEPTED in the register. The manifest's `dec` names them.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-idle-guard/` (the bundle `acts/ACT-IDLE-GUARD-1/`, the
  companion tests `companion-tests.diff`, the tools in `tools/`).

## 0. Class: (O), by the code's vote; your yes, then your operator by hand
**The yes line: `yes ACT-IDLE-GUARD-1 a49a4228`** (the first 8 digits of the manifest's sha256 in §3).

I read `governance/project/operator/class-rules.yaml` first, and ran the operator's own `act_class.py` (read only) on the
bundle:

| File | Row | Class | Control path |
|---|---|---|---|
| `governance/project/orchestration/tools/dispatch/dispatcher.py` | `watchers` (`dispatch/**`) | **b** | yes |
| `governance/project/orchestration/tools/stop_idle_check.py` | `unknown` (the catch-all) | **O** | no |

**The ACT is (O)** (the highest file or hit applies; no script hit was raised). Two consequences:
- The operator agent never takes an (O) ACT (its gate G6 refuses it). So this is **your operator by hand**: the message in
  §5 runs `apply.sh` from the bundle and commits with `Role: owner`. The bundle is still in the operator's form
  (manifest, `apply.sh` deciding by sha256, a rehearsal log, checks run with `bash -c`), so the agent can take it, and
  `act_class.py` can vote on it, if you later move the file to class (b) (the next point).
- **A finding for you:** `stop_idle_check.py` is a Stop hook (the CTO's idle check, ACT-STOP-IDLE-1) and falls to the
  catch-all only because no row names it. Its sibling `stop_waiter_check.py` is named in row `guard-hook` (class b,
  control). Adding `governance/project/orchestration/tools/stop_idle_check.py` to that row would make it a control path by
  name. That is a change to `class-rules.yaml`, which is yours ((O), `operator-own`); I propose it, I did not write it.
  The same ACT could not carry it (it would change the rule table that classifies it).

**Alternative:** split into two bundles: the dispatcher alone as class (b) through the operator agent, the hook by hand.
Not recommended: two yes lines for one rule, and the hook's block and the dispatcher's item are meant to land together.

## 1. What changes, and why (the evidence)
The owner's standing rule 1 failed on 11-11. From the re-pin at 13:31 to 17:54 no lead ran, although the gate was open and
W2-170 and batch 1 of READY-AFTER-LIFT-1 were ready. Two safety nets let it pass:

**(a) The CTO's Stop hook** (`stop_idle_check.py`). `log/stop-idle.log` lines 17:06 to 17:49 read
`through running: 1 task ...: python3 .../helper_watch.py --every 300 --max 86400`. `helper_watch.py` is a standing watcher
but was missing from the hook's watcher list, so it counted as work for 24 h; every idle turn passed. And the hook's only
"open work" source is DECIDED-NOT-DONE; it never asked whether a ready ticket could launch.

**(b) The dispatcher** (`dispatch/dispatcher.py`, one pass a minute) ticked all afternoon. Its `ready.txt` held one line,
W2-170, which `why_not()` answered "already started for W2-170-A5-tests.json" from 15:20 (that lead returned PACKAGES)
until the CTO wrote a new line at about 17:53. It raised no inbox item when no line was startable with the gate open and
leads below the cap, so it never woke the CTO.

### What the ACT does
**The hook (`stop_idle_check.py`):**
1. **The watcher list** is now `inbox_wait.sh, inbox_wait_quiet.sh, helper_watch.py, sentinel_check.sh, bare_watch.sh,
   store_refresh_daily.sh, usage_log.sh, mem_guard.py, oom_watch.sh`: every watcher in START-NEXT-SESSION §6 (the inbox
   waiter in both forms, the helper watch, the sentinel check, the bare-repository watch, the store backstop, the usage
   log) and the two machine watchers (`mem_guard.py`, `oom_watch.sh`). A bare `sleep N` timer was already exempt.
2. **A new block, checked before the "running" let-through,** so whatever else runs (a watcher, a job, a lead, a pid
   file). It blocks the turn, naming the tickets, when the dispatcher's tick (`status.json`, at most 5 minutes old):
   - shows no legitimate wait (the gate and the disk gate open, the machine not full: the same test as before);
   - shows fewer leads running or launching than the cap in `dispatch/config.json`, key **`max_leads`** (a whole number
     of 1 or more; read each time, never a constant; **unset or unreadable: no cap is known and the forecast alone admits**,
     the post-ACT-A reading, DEC-1052 O-A1); and
   - names a launchable ticket. **Launchable** is either (i) a `ready.txt` line the dispatcher skipped only for a used or a
     returned log (the tick's `ready_waits` reason holds "already started for" or "already holds a return"), or (ii) when
     the tick counts no ready line (`ready_count` is 0): the tickets of `gov plan`'s first batch (its `--ready` form,
     run for at most 30 s; the plan exits 1 on its own findings, so only its output counts) that no lead runs, the CTO's own
     W2-00 left out. A line waiting for any other reason (no brief, claim not committed, a worktree) is the CTO's prep and
     is not named here.
3. The once-per-turn bound, the `stop_hook_active` bound and the `IDLE-REASON:` escape are kept. **An IDLE-REASON while a
   ticket is launchable still ends the turn, but is shown as such:** the log case reads `the CTO's stated reason WHILE a
   ticket was launchable`, the tickets follow the reason in the log, and the owner's `systemMessage` adds `NOTE for the
   owner: a ticket was launchable (...)`. The second stop of a blocked turn is logged and shown the same way.
4. An unusable tick or an unusable `gov plan` is named in the log and never relied on (the hook still never fails open
   silently, and still always exits 0).

**The dispatcher (`dispatcher.py`):**
1. **An inbox item `idle-headroom`** (`dispatch/inbox/<time>-idle-headroom.txt`, so the inbox waiter wakes the CTO) when, in
   one pass: nothing started, the gate and the disk gate open, the machine not full, fewer leads running or launching than
   `max_leads`, and no ready line startable (the list empty, or every line waiting). It names every line skipped for a used or
   returned log first, with the cure (write the line again with a new log name), then the other waits. Once per cause per
   hour (`dispatch/idle-headroom-reported.json`; a cause that stops holding is forgotten, so it is reported again if it
   returns). A hold the dispatcher keeps itself (the stagger after a start, a hung embedding server) is not idle. No item in a
   dry pass. The body has no line starting `W2: ` (that line would hold a W2's own start, `why_not()`'s inbox rule).
2. `status.json` gains `ready_count` (the ready list's lines) and `max_leads` (the cap read, or null). The hook reads
   `ready_count`.
3. **The item is sent only when `max_leads` is set.** Without a cap the dispatcher stays silent: two existing tests in
   `test_dispatcher.py` run a pass with nothing startable and read the inbox as theirs alone, and an unset cap would send an
   item on every quiet project state. The hook's block does not need the cap.

**What the ACT does not do:** it does not enforce the cap. Today nothing in the dispatcher stops a fourth lead; the owner's
"at most 3 until ACT A" is a rule the CTO holds. `max_leads` is only what the guard reads. Nor does it start anything.

### What the CTO does beside it (not an ACT's business: `dispatch/config.json` is the CTO's scratch, class (O) `cto-scratch`)
Write `"max_leads": 3` into `.gov-runtime/scratch/orchestrator/dispatch/config.json` (the dispatcher re-reads it each pass;
an unknown key is harmless: `c.update(explicit)`). Raise or remove it when ACT A lands. Until it is set, only the hook's
block (not the dispatcher's item) is armed, and the hook treats the cap as unset.

## 2. Plain-language summary for the owner
After this, the CTO cannot end a turn idle while a ready ticket could launch: a standing watcher no longer counts as work,
and a "ready" line whose log was already used is named and blocks the turn once. If the CTO still stops, the log and your
message say a ticket was launchable. And when nothing can start although there is room, the dispatcher puts a note in the
CTO's inbox, which wakes it, at most once an hour per cause.

## 3. The bundle (`acts/ACT-IDLE-GUARD-1/`, beside this file; the CTO copies it to `.gov-runtime/scratch/orchestrator/acts/`)
`manifest.json` sha256: **`a49a4228dc1e334749e062ecb859e633c652b022564311551b6ddd6c6203a8e5`** (sha8 `a49a4228`).

| File | sha256 (first 16) |
|---|---|
| `before/repo/.../stop_idle_check.py` | `d56a7aa7933197c3` (the live file at the build, git head `4c55f14179be`) |
| `after/repo/.../stop_idle_check.py` | `2d74d8ed5c5ea7b3` |
| `before/repo/.../dispatch/dispatcher.py` | `1e698a717bdb232a` (the live file at the build) |
| `after/repo/.../dispatch/dispatcher.py` | `bc0c74b119baa8a3` |
| `apply.sh`, `list.txt`, `rehearsal.log` | in the manifest's `files` |

`apply.sh check | apply | undo | verify`, by `list.txt` (`root|path|before|after`): each file's state is decided by its sha256
alone (before, applied, other). **Every file is read first; if one is neither the before nor the after, nothing is
written** (exit 3). Each frozen copy is hashed against `list.txt` before it is used (exit 4). Writes go to a `mktemp` file
beside the target, the mode kept, then a rename; no temp file is left. A link or a missing file is refused. `check` is exit 0
only on the before; `verify` only on the after.

**Checks** (the manifest's four, each run with `bash -c` from the repository root; none needs pytest, which the operator's
planted HOME hides): 0 both files parse (no byte-code written); 1 the hook's behaviour in a planted folder (a lead, a
watcher and a used-log line with the cap at 3: blocked and named; the watcher alone: blocked on the open DECIDED-NOT-DONE
item), count 2; 2 the dispatcher's item with a planted truth (one item naming the line; none the second time; none with no
cap; none at the cap), count 4; 3 both files are tracked. They leave only small `mktemp` folders in the temp directory.

**Undo:** `bash $A/apply.sh undo` puts both files back byte for byte (§5), then a commit with the same trailers.
**Rollback in short:** the CTO's Stop hook goes back to counting `helper_watch.py` as work and to ignoring ready lines; the
dispatcher stops writing `idle-headroom` items and the two status keys. Nothing else changed.

## 4. The companion tests (`companion-tests.diff`: a CTO commit, not part of the ACT)
The tests are class (O) paths the CTO commits (`tests/unit/orchestration/test_stop_idle_check.py` and
`test_dispatcher.py`; extended, nothing removed): 265 added lines, 16 new cases in all.
- **Hook** (12 cases): the nine watchers are not work; `helper_watch.py` beside a real job counts only the job; **a used-log
  ready line with an open gate blocks whatever runs** (a lead, a watcher, a job, a worker pid file); a returned-log line and
  every such line named; no block at the cap (running plus launching), with the gate shut or the machine full; the cap read
  from the config, unset or unreadable meaning no cap; a stale tick not relied on; an IDLE-REASON while launchable shown as
  such; the once-a-turn bound; no `ready_count` and only other waits not launchable; an empty ready list with `gov plan`
  tickets blocks naming the first batch (a stub `gov`; the CTO's W2-00 and a running lead left out; no temp file left); an
  unusable plan does not block and says so.
- **Dispatcher** (4 cases): one item an hour for a used-log line with an open gate (the body, no `W2: ` line, the status keys);
  a returned log and an empty list as separate causes; no item when a line starts, at the cap, with the gate shut, with no cap,
  or in a dry pass; a cleared cause reported again.
- **Red on the old code, green on the new** (rehearsal C1, E3): on the old code 13 of the 16 fail, including the two named
  cases (the `helper_watch.py` let-through; the used-log ready line with an open gate, for the hook and for the dispatcher);
  the other three are "does not fire" cases, which pass on the old code by nature. Every existing case of both files
  stays green on the new code (B1 and E1).
- **Order:** apply the ACT, then commit the tests (`git apply companion-tests.diff`). The ACT keeps every existing test
  green by itself (E1); committing the tests first would leave 13 red until the ACT lands.

## 5. The operator's steps: the message
> **ACT-IDLE-GUARD-1 (DEC-1110 (1), DEC-1109 (3)): the CTO's idle check cannot pass silently while a ticket could launch.**
> Class (O), by hand: your yes first: **`yes ACT-IDLE-GUARD-1 a49a4228`**. In the main tree, about two minutes:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> A=.gov-runtime/scratch/orchestrator/acts/ACT-IDLE-GUARD-1
> sha256sum $A/manifest.json     # expect a49a4228dc1e334749e062ecb859e633c652b022564311551b6ddd6c6203a8e5
> git status --porcelain         # expect empty
> bash $A/apply.sh check         # exit 0 (both files as frozen)
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly two M: stop_idle_check.py and dispatch/dispatcher.py
> git commit -m "ACT-IDLE-GUARD-1: the idle check names launchable tickets and counts helper_watch as a watcher; the dispatcher raises idle-with-headroom (DEC-1110 (1), DEC-1109 (3))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1110, DEC-1109" --trailer "Role: owner" -- governance/project/orchestration/tools/stop_idle_check.py governance/project/orchestration/tools/dispatch/dispatcher.py
> ```
> - **If `check` stops** ("moved: <path>"), send its line to the CTO and apply nothing (`apply.sh` refuses by itself and writes nothing).
> - **If `git diff --name-status` lists anything besides the two,** commit anyway: the `--` paths limit the commit.
> - **Undo:** `bash $A/apply.sh undo`, then the same `git commit` with the subject `ACT-IDLE-GUARD-1 undone`.
> - No restart is needed: each Stop hook and each dispatcher pass reads its file whole when it starts.

**Then the CTO, the same day:** write `"max_leads": 3` in `dispatch/config.json`; commit `companion-tests.diff` (scoped run:
`test_stop_idle_check.py`, and `test_dispatcher.py` through the heavy gate); watch `log/stop-idle.log` for the first
`launchable:` block and `dispatch/dispatch.log` for `idle with headroom: inbox item written`.

## 6. The rehearsal (`rehearsal.log`; 61 ok lines, `failures: 0`)
As the operator will run it (`tools/rehearse.sh`): a `--no-hardlinks` clone of `w2/integrate` (the main tree's head at the
build), a planted HOME, the clean environment of the operator's dry run (PATH, LANG, TMPDIR, HOME planted, no `GOV_*`),
each manifest check run exactly as written with `bash -c`, the plain `apply.sh apply` with no option. In order:
A the bundle is not stale (the clone's and the main tree's files are the frozen before; `check`, `verify` refused, `undo` a no-op);
B the existing tests of both files pass on the old code, and checks 1 and 2 are red on it (they tell the two apart);
C the new tests applied to the old code: red; D the plain apply: both files are the frozen after byte for byte, modes kept,
`git status` shows exactly the two files, no temp file left, `verify` 0, a second `apply` changes nothing;
E all four checks green exactly as written, the existing tests green, the existing and the new tests green;
F undo byte for byte and the clone clean; one file moved: `check`, `apply` and `undo` refuse (3) and write nothing to the other;
a half-applied state is finished by `apply` and taken back by `undo`; a tampered frozen copy: exit 4, nothing written; a missing
file and a link refused; G the live files and the main tree unchanged, the planted HOME empty.
**The log has no head, pid, date, duration or count line: rebuilt a second time it is byte for byte the same, and so is the
manifest (sha256 above).** Also by hand, outside the log: the new hook run against the real `gov plan` in a clone with a planted
orchestrator folder and an empty ready count named the 11 open tickets of the plan's first batch (W2-00 left out) and left
no temp file.

**Differences from the real run:**
- It is a clone of the head at the build (`4c55f14179be`); the files are checked by sha256, so a later head that leaves the
  two files alone changes nothing; one that edits either file makes `apply.sh check` refuse, and the bundle is rebuilt.
  ACT-LOAD-BALANCER-A touches `dispatch/launch_now.sh` only: no clash.
- No operator gates G1 to G9 ran (the agent does not take an (O) ACT; by hand there is no dry run in a clone): the owner's
  operator runs `apply.sh` directly, as in §5. The checks run in the main tree after the apply are the manifest's four if the
  operator chooses to run them (`bash -c` from the repository root).
- The real HOME is used for pytest only (the planted one hides the user-site pytest); no manifest check needs pytest.
- The planted HOME has no `gov`: the hook's `gov plan` path is covered by the stub in the tests and by the hand run above, not
  in the rehearsal log.
- No real tick, no real Stop hook and no real session ran; the dispatcher's item is exercised through `watch_headroom()` with a
  planted truth, and in the unit tests through full planted passes.

## 7. The review, residuals, risks
- **Independently reviewed: round 1 READY**, class (O) (2026-11-11, a fresh read-only independent auditor, not the author;
  `reviews/ACT-IDLE-GUARD-1-review-r1.md`, also `acts/ACT-IDLE-GUARD-1/review.md`); rows F1-F6, no blocking finding; a
  follow-up ACT for F1 (the wording), F2 (the merged-ticket filter) and F3 (the timeout). The owner's yes `a49a4228` followed;
  **APPLIED** by the owner's operator by hand, committed as `256b4e12d` (exactly the two files; check, apply, verify exit 0).
- **A false block costs one extra turn,** bounded once per turn, with the `IDLE-REASON:` escape (shown to the owner as
  stated while launchable). The likeliest false block: the plan's first batch when `ready.txt` is empty: it holds tickets
  merged and waiting for a formal close, which need the CTO's close, not a lead, and tickets with no brief or claim yet
  (the block's text says so). A ticket the owner has parked outside the plan's own waits cannot be told apart by the hook.
- **The dispatcher's item can repeat hourly** when the CTO is legitimately waiting with an empty list and a cap set. The
  cause is keyed, so a different cause is reported at once; the hourly repeat for one cause is the intended nudge.
- **`gov plan` runs inside the Stop hook** (about one second, at most 30 s) only when `ready_count` is 0 and no used-log line
  exists. A hang costs at most the timeout; an error is named and the turn ends.
- **The cap is not enforced** (§1).
- **ACT A or any edit of either file before the apply** makes `check` refuse: rebuild from the new bytes
  (`tools/make_manifest.py` and `tools/rehearse.sh`).
- **Not done, listed only:** the README of `dispatch/` does not yet describe `idle-headroom`, `ready_count` and `max_leads`
  (a later edit would itself be a (b) control-path change); the hook's docstring does.
