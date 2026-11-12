# ACT-IDLE-GUARD-2: the idle check no longer names a finished lead's line, merged tickets or a hanging plan as launchable (DEC-1140 (2); the review's F1-F3 of ACT-IDLE-GUARD-1)

- **For:** the owner's yes, then the owner's operator **by hand** (class (O): section 0). About two minutes in the main tree.
- **By:** an ACT-preparation helper of the CTO (Sonnet, high; RUBRIC-2, class C1), 2026-11-11 about 23:00 to 24:00 UTC. **Nothing live
  was changed or started:** no commit, no stage, no live hook, no live dispatcher, no `.claude/`. Built and rehearsed in clones
  (section 6). **Not yet independently reviewed** (section 7).
- **Under:** DEC-1140 (2) (the idle guard's follow-up, F1-F3); DEC-1110 (1) (the stop-hook check against idling), DEC-1109 (3),
  DEC-936 item 2 (never idle while unblocked work remains). ACT-IDLE-GUARD-1 (applied, `256b4e12d`) and its review
  (`governance/project/orchestration/reviews/ACT-IDLE-GUARD-1-review-r1.md`, rows F1-F6) are the evidence.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/dispatch-1/` (the bundle `acts/ACT-IDLE-GUARD-2/`, its checks `tools/check_hook.py`,
  `tools/rehearse_guard2.sh`). Its sibling for the dispatcher is `ACT-DISPATCH-1.md`.

## 0. Class: (O), by the code's vote; your yes, then your operator by hand. Why it is a second ACT
**The yes line: `yes ACT-IDLE-GUARD-2 531d98c0`** (the first 8 digits of the manifest's sha256 in section 3).

F1-F3 live in `governance/project/orchestration/tools/stop_idle_check.py`, the CTO's Stop hook (and the hook's test file), **not** in
`dispatch/**`. I read `governance/project/operator/class-rules.yaml` and ran `act_class.py` (read only):

| File | Row | Class | Control path |
|---|---|---|---|
| `governance/project/orchestration/tools/stop_idle_check.py` | `unknown` (the catch-all; no row names it) | **O** | no |
| `tests/unit/orchestration/test_stop_idle_check.py` | `unknown` | **O** | no |

So it cannot ride in ACT-DISPATCH-1 as a class-(b) ACT, and it is **(O) by hand**, as ACT-IDLE-GUARD-1 was. (The review's F6 still stands, and
is yours: adding `stop_idle_check.py` to row `guard-hook` (class b, control) would make it a named control path and let the operator
agent take hook changes. A change to `class-rules.yaml` is `operator-own`; I propose it, I did not write it.)

## 1. What changes, and why (the evidence)
The idle check (ACT-IDLE-GUARD-1) blocks a CTO turn when a ticket "could launch". Its review found it names three things that are not launchable (and one
that fails open). This ACT fixes F1-F3; F4-F6 are listed at the end of this section.

**F1. A finished lead's line read "launchable".** The dispatcher never removes a `ready.txt` line, and `why_not()` answers "already started for <log>"
as soon as a lead ends, whatever it returned. So each return made its line "launchable", including while its return item waited unread for the CTO, and
the block's text advised "write the line again with a new log name", which points towards relaunching a finished lead.
- **A used-log line whose W2 has an unread return in `dispatch/inbox` (an item with a `W2: <id>` line, the form the dispatcher writes) is left out** and
  named in the log (`left out, a return waits unread in the dispatcher's inbox: <line>`). When the CTO reads the item (it leaves the inbox) the line
  is named again, the old behaviour, so a line left in `ready.txt` for a ticket that needs no new run is the CTO's to comment out.
- **The block's text** now says: "..., or comment a line out of ready.txt when its ticket needs no new run (a lead that returned packages waits for
  the owner), then end the turn". (The dispatcher's item says the same: ACT-DISPATCH-1.)

**F2. The plan arm named merged and parked tickets.** When `ready.txt` is empty (`ready_count` 0) the hook asks `gov plan --ready` and names the first
batch's tickets that no lead runs. Tickets merged into `w2/integrate` and waiting for their close (W2-131 and W2-139 on 11-11) are not launchable.
- **A plan ticket whose branch `w2/<id>` is already in `w2/integrate` is left out** (one `git for-each-ref --merged w2/integrate refs/heads/w2/`, at
  most 3 s) and **named in the log** (`merged into w2/integrate, to close (not launchable): W2-131, W2-139`), so the close work stays visible. A ticket with
  no branch yet (W2-94, W2-40) is still named: it needs a brief and a claim, which is the CTO's preparation and is said in the block. An unreadable git
  is named in the log and **nothing is left out** (the old behaviour: fail toward naming).
- Not done (a decision, not code): a ticket "parked outside the plan" by the owner or the CTO still cannot be told apart (the review's F2 asked to
  "consider a parked list the hook reads"). It is listed in section 7.

**F3. The plan's timeout was longer than the hook's.** `PLAN_TIMEOUT_S` was 30 s and the live Stop hook entry (`.claude/settings.local.json`) gives the hook
`timeout: 10`: past 10 s Claude Code kills the hook with no log line and no message, and the turn ends unchecked, against the docstring's "never fails
open silently".
- `PLAN_TIMEOUT_S = 5` and the new `MERGED_TIMEOUT_S = 3`: **8 s at the worst, inside the entry's 10**. A plan that hangs is cut at 5 s and named in the log
  (`gov plan unusable (TimeoutExpired, at most 5 s)`), and the turn ends. (Raising the settings timeout instead would be its own class-(b) change.)

**F4-F6 (not in this ACT):** F4 (write `max_leads` before the apply) was done by the CTO (`max_leads` is set, 5 now). F5 (check 2 wrote byte-code): this ACT's
checks, like ACT-DISPATCH-1's, set `sys.dont_write_bytecode` and are run with `-I -B`. F6: above.

**Also carried: ACT-IDLE-GUARD-1's companion cases.** `drafts/act-idle-guard/companion-tests.diff` was never committed. The hook's twelve cases (the
watchers, the used-log block, the cap, the stale tick, the IDLE-REASON note, the once-a-turn bound, the plan arm) are in this ACT's `test_stop_idle_check.py`
(its after copy is the committed file plus those cases plus the cases below), so the ACT is the only thing that touches the file. **Do not commit the old
companion diff** (its dispatcher hunk is superseded by ACT-DISPATCH-1's; its hook hunk is carried here).

## 2. Plain-language summary for the owner
After this, the CTO's idle check stops crying "a ticket could launch" about a lead that has just returned (its return is waiting to be read), about tickets
that are merged and only need closing, and it can no longer be killed silently by a slow `gov plan`: it gives up after 5 seconds, says so in its log, and
lets the turn end.

## 3. The bundle (`acts/ACT-IDLE-GUARD-2/`, beside this file; the CTO copies it to `.gov-runtime/scratch/orchestrator/acts/`)
`manifest.json` sha256: **`531d98c006de973fd4c17c5ca61a1b6c89f8536192036b8dd22f7625da081d0a`** (sha8 `531d98c0`).

| File | sha256 (first 16) |
|---|---|
| `before/repo/.../stop_idle_check.py` | `2d74d8ed5c5ea7b3` (the live file at the build; ACT-IDLE-GUARD-1's after) |
| `after/repo/.../stop_idle_check.py` | `05ba5a90a50d6dd2` |
| `before/repo/tests/unit/orchestration/test_stop_idle_check.py` | `a58027c533fd8176` |
| `after/repo/tests/unit/orchestration/test_stop_idle_check.py` | `4e6b665cf4d19f1b` |
| `apply.sh`, `list.txt`, `rehearsal.log` | in the manifest's `files` |

`apply.sh check | apply | undo | verify` is the same script as ACT-IDLE-GUARD-1's and ACT-DISPATCH-1's (state by sha256: before, applied, other; every
file read first, nothing written unless every file is as the step expects, exit 3; a frozen copy hashed before use, exit 4; temp file and rename, mode kept).

**Checks** (the manifest's three, each with `bash -c` from the repository root, no pytest, no byte-code): 0 both files parse; 1 the hook's behaviour in
planted folders with a stub `gov` and a planted repository, count 4: a used-log line with an unread return is left out and a second line still blocks with
the new wording; a merged plan ticket is left out and named, one with no branch is named; a plan that hangs is cut inside 9 s and named, the turn ends; the two
timeouts together are under 10 s; 2 both files are tracked. **Check 1 is red on the old hook** (rehearsal C).
**Undo:** `bash $A/apply.sh undo`, then a commit with the same trailers. **Rollback in short:** the hook names a returned lead's line and merged tickets again and its
plan may run 30 s. Nothing else changed.

## 4. The tests (carried by the ACT: `test_stop_idle_check.py`)
On the old hook 9 of the new file's cases fail (rehearsal C); the others are the cases that already hold on the old code.  10 new cases of F1-F3 on top of ACT-IDLE-GUARD-1's twelve, and `World.run` sets `GOV_STOPIDLE_REPO` to a planted repository (a path that need not
exist: an unreadable git is a case). The new cases: an unread return leaves its line out and the log names it; only that line is left out and a read return names it again;
the block's wording; an inbox item with no `W2:` line leaves nothing out; a merged plan ticket is left out and named; a branch with commits of its own is launchable;
every plan ticket merged: nothing launchable and the close work named; an unreadable repository names every ticket and says so; a plan that hangs is cut under 9 s and
named; the two timeouts together under 10 s.

## 5. The operator's steps: the message
> **ACT-IDLE-GUARD-2 (DEC-1140 (2); the review's F1-F3): the idle check leaves out a returned lead's line and merged tickets, and cannot be killed by a slow plan.**
> Class (O), by hand: your yes first: **`yes ACT-IDLE-GUARD-2 531d98c0`**. In the main tree, about two minutes:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> A=.gov-runtime/scratch/orchestrator/acts/ACT-IDLE-GUARD-2
> sha256sum $A/manifest.json     # expect 531d98c006de973fd4c17c5ca61a1b6c89f8536192036b8dd22f7625da081d0a
> git status --porcelain         # expect empty
> bash $A/apply.sh check         # exit 0 (both files as frozen)
> bash $A/apply.sh apply         # exit 0
> bash $A/apply.sh verify        # exit 0
> git diff --name-status         # expect exactly two M: stop_idle_check.py and test_stop_idle_check.py
> git commit -m "ACT-IDLE-GUARD-2: the idle check leaves out a returned lead's line and merged plan tickets, and cuts a slow plan at 5 s (DEC-1140 (2); ACT-IDLE-GUARD-1 review F1-F3)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1140, DEC-1110" --trailer "Role: owner" -- governance/project/orchestration/tools/stop_idle_check.py tests/unit/orchestration/test_stop_idle_check.py
> ```
> - **If `check` stops** ("moved: <path>"), send its line to the CTO and apply nothing.
> - **Undo:** `bash $A/apply.sh undo`, then the same `git commit` with the subject `ACT-IDLE-GUARD-2 undone`.
> - No restart is needed: each Stop hook reads its file whole when it starts.

## 6. The rehearsal (`rehearsal.log`; 58 ok lines, `failures: 0`)
As the operator will run it (`tools/rehearse_guard2.sh`): a `--no-hardlinks` clone of `w2/integrate`, a planted HOME, the clean environment of the operator's
dry run, each manifest check run as written with `bash -c`, the plain `apply.sh apply`; the tests scoped through the heavy-slot gate
(`heavy_slot.sh env TMPDIR=... PYTHONPATH=<clone>/src python3 -m pytest ...`). In order: A the bundle is not stale and the states of `apply.sh`;
B `test_stop_idle_check.py` on the old hook and old tests: **31 passed**; C the new test file on the old hook: **9 failed, 44 passed**, check 1 red; D the plain apply (two
files the frozen after, modes kept, `git status` exactly the two, no temp file, `verify` 0, a second `apply` no change); E the three checks green and the file
green: **53 passed**, the two other hook suites green; **F the new hook against the real `gov plan`** (a planted orchestrator folder and an empty ready count,
the real `gov`, the main tree's branches read only): exit 0, nothing on standard error, no plan temp file left, **no ticket merged in the main tree named
launchable**, W2-00 never; G undo byte for byte, one file moved refused, half-applied finished and taken back, a tampered frozen copy (4), a missing file and
a link refused; H the live files unchanged, the planted HOME empty. **The log has no head, pid, date or duration.**

**Differences from the real run:**
- A clone of the head at the build; a later head that leaves the two files alone changes nothing; one that edits either makes `check` refuse.
- No real Stop hook and no real session ran: the hook is run as Claude Code does (JSON on standard input) in planted folders, and once against the real
  `gov plan` in a planted orchestrator folder. The live `timeout: 10` is a settings value I read, not a thing the rehearsal enforces: the hang case
  shows the hook gives up in under 9 s by itself.
- The real `gov` ran as the user (the planted HOME has none), which is why step F passes the user's HOME.

## 7. The review, residuals, risks
- **Not independently reviewed.** The CTO starts the independent auditor (fresh read-only session).
- **A left-out line can hide a launchable one.** A used-log line is left out while its return item is unread; if the CTO leaves the item unread for hours
  the hook says nothing about that ticket (the dispatcher's own stale-inbox flag at 30 minutes covers the unread item).
- **A merged branch is not a closed ticket.** The hook names it in the log only, not to the owner; the close is the CTO's work under the same rule 1, found by
  DECIDED-NOT-DONE and the plan, not by this hook.
- **Parked tickets** (the owner's or the CTO's "off the list") still cannot be told apart from launchable ones in the plan arm; an `IDLE-REASON` line ends the turn.
- **A timeout of 5 s may be short on a loaded machine** (`gov plan` takes about 1.1 s at load 9.6 on 20 CPUs, the review's reading). A plan cut short names itself
  in the log and ends the turn unchecked for the plan arm only; the used-log arm and DECIDED-NOT-DONE are not affected.
- A false block still costs one extra turn, bounded once per turn, with the `IDLE-REASON:` escape.
