I recommend one more round, for one fix. The close check in S2 can let a landing go while a close of the same ticket is running, in the way closes are normally run. S1, S3 and S4 pass, with five findings to note but no block. I wrote nothing in the worktree, and the head is the same as at the start.

task: DAEO-ifgf (W2-121b), independent review, round 1 of at most 2, head 951dbcfa5cc7 on w2/W2-121b
status: done. S1 pass, S2 fail, S3 pass, S4 pass. One finding blocks (RV1).
work_completed: Read the ticket (S1–S4, non-goals, "K9 decided", Interface items 1–4 and the exit codes) and part a's Interface. Read the engineer's code (3476e8628..ab5799760, all of `landing.py` and `heavy.py`, and the changes to `config.py`, `procs.py`, `run.py`, `state.py`, `status.py` and `slots.py`). Read all of `tests/acceptance/W2-121b/`, the fix commit ed8aa4904, and the unit test list. Compared the meaning with the reference dispatcher's landing, close and nightly code. Reproduced RV1 in memory against this worktree's `src/`, plus one read-only check of this session's own process tree.
files_changed: none
evidence:
- Step 0: (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf` failed with `OSError: [Errno 30] Read-only file system`, so the sandbox holds; (b) `git update-index --refresh` worked, no output.
- Identity: `independent-auditor`, `DAEO-ifgf`; worktree `/home/usain/gov-os-worktrees/W2-121b`, branch `w2/W2-121b`.
- Head at my start: 951dbcfa5cc7. Head at my end: 951dbcfa5cc7.
- `git status --porcelain` at the end: empty.
- `gov.__file__` = `/home/usain/gov-os-worktrees/W2-121b/src/gov/__init__.py`
- `git diff --name-only w2/integrate...HEAD` lists only the ticket's `allowed_paths` (`src/gov/dispatch/*`, `src/gov/resources/slots.py`, `tests/unit/dispatch/test_w2_121b_landing.py`) plus `tests/acceptance/W2-121b/*`.
- Read refusals: none. One write refusal: the Write tool asked for permission to create a probe script at `$TMPDIR/ancestry.py`, and it was not granted. I did not retry it or write the file another way; I ran the probe inline with `python3 -c`, which writes nothing.
- RV1 probe 1, this session's process tree: a command run from the agent's Bash tool is a child of `/bin/bash -c "…; eval '<command>' < /dev/null && pwd -P …"`. The whole command text sits inside one argument of that shell.
- RV1 probe 2, in memory: a table with that shell (pid 100) and its child `python3 …/gov close W2-7` (pid 101), with marker `gov close`. `procs.find` returned `jobs [{'kind': 'close', 'pid': 100}]`, and the tickets shared with the landing `{W2-7}` were `[]`.
tests: I re-ran no suite. The lead's results stand: `gov accept` 48 passed; lead_verify 2 reds outside this ticket's paths. I ran no pytest.
discoveries:
- The reference dispatcher found closes by checking every process that runs the close script. This code checks only the topmost process matching the marker (part a's `procs.find` drops its children), which causes RV1.
- The reference finalised a landing when its process was gone. This code finalises only when an exit file exists, as the Interface says, which causes RV3.
- This project's `heavy_slot.sh` takes its own flock slots, not `gov resources` slots. Under it, every heavy step would show as outside a slot. That is a project-setup matter, not code in this ticket.
- What I checked and found sound:
  - S1:
    - The claim needs all four conditions.
    - The claim is an atomic `os.rename` made before the spawn.
    - Lines already in `land-done.txt` are dropped.
    - A second pass while a batch runs claims nothing and says why.
    - Unapproved and malformed lines are never sent, and malformed ones are named.
    - Finalisation happens in a safe order (done lines, then the inbox item, then removing the claimed file), so a pass that dies halfway is finished by the next. Exit 0 gives `landed`, others give `failed (exit N)`.
    - A launch that fails writes exit 127 and is finalised as failed.
    - A `land.txt` rewritten during a landing waits for it to finish.
  - S2:
    - Matching by W2 id and by ticket id (through `.tickets/` `external-ref`/`wbs_id`) works.
    - `index.lock` is found in the right git folder, `close_record_paths` blocks when all changes are under it, and a close with no shared ticket does not block.
    - `commit_records` retries only on an `index.lock` message, commits only the given paths, raises `CommitFailed` at the end, and two at once both land.
  - S3:
    - The window maths is right, including a window crossing midnight.
    - The marker is read relative to the root or as an absolute path, and its absence means the hold lasts until `until`.
    - A claimed landing is still finalised during the hold and never stopped; starts and the inbox are not held.
    - The `land_hold` key, the status line text and exit 0 all match the Interface.
  - S4:
    - Only the four kinds count.
    - The ancestor walk ends at init and at a loop.
    - Slot runners come from the holders read by `gate.read` (flock-held only).
    - The finding text is exact and the exit code does not change.
    - `slots.py` gains only a read helper, and `command.py` is untouched.
  - Every held landing gives exit 0 with a `land:` reason.
  - Part a's Interface is changed only by additions.
  - No new key lives outside `dispatch:`, and nothing in `src/` names this repository or the reference tool.
  - Both fixed cases in ed8aa4904 are right against the ticket:
    - The stub counts all of its arguments, so 4.
    - `(60, 30)` put "now" inside a window crossing midnight; `(60, -30)` is truly outside it.
risks: none beyond the findings below.
lessons: Acceptance tests that plant a process as one flat command line miss how commands really appear when run from a shell. A planted close (or heavy step) needs at least one case under a `bash -c` wrapper whose child matches the same marker.
proposed_decisions: none
unresolved: none
recommended_next_action: Classification: 1 finding in scope, ordinary work, fails open (RV1); 5 rows (RV2–RV6: other, or not reachable in ordinary work). Recommendation: round 2 for RV1 only.
- The fix: work out a close's tickets from every process in its tree that matches the marker (or every process matching it), not only the topmost one.
- The designer adds an S2 case: a close running under a `bash -c` wrapper with a matching child.
- RV2, RV3 and RV4 can ride along as small fixes if the lead agrees; RV5 and RV6 are rows.

RV1: src/gov/dispatch/landing.py:216 (with src/gov/dispatch/procs.py:71) When `gov close <ticket>` is run through a shell, a landing of that same ticket goes ahead while the close runs. This happens from an agent's Bash tool (`bash -c "… eval 'gov close W2-7' …"`) or from cron (`sh -c`). Both the shell and its `gov close` child match the close marker. Only the shell is kept as the close (its matching child is dropped), and the shell's arguments hold the whole command as one string. So no argument equals `W2-7`, the close shares no ticket with the landing, and the landing is claimed and sent. It should have been held, as with the test's flat planted close. Unless the close's record commit holds `index.lock` or leaves the tree unclean at that moment, nothing else stops it.
Ordinary work: yes, because closes are run by the orchestrator from a Claude Code session, whose Bash tool always wraps the command in `bash -c` (seen in this session's own process tree).
Consequence: fails open
Scope: in (S2: "a running close with a ticket in the landing's set blocks the landing")
Would reverse it: a pass, with a real close started from an agent's Bash tool for a ticket in `land.txt`, that holds the landing; or evidence that closes never run under a shell wrapper whose child matches the marker.

RV2: src/gov/dispatch/landing.py:102,113 A malformed approval sent together with good ones disappears after one status. For example `W2-8=abc1234`, a short hash. It is named as not sent in the status of the claiming pass, then goes into the claimed file with the batch. Finalisation works out the bad lines but reports them nowhere, puts them in neither the inbox item nor `land-done`, and deletes the claimed file. From the next pass on, no file and no status mentions the line. It should stay visible until someone acts, for example named in the `.land.txt` item.
Ordinary work: yes, because short or mistyped hashes are common (row W2-L423's 12-digit rule exists for that reason).
Consequence: other (the Interface asks only that it is "named in the status", and it is, but for a single pass)
Scope: in (S1)
Would reverse it: a reading of the Interface under which a mention in one pass's status is the intended, lasting record.

RV3: src/gov/dispatch/landing.py:91,283 A batch whose wrapper shell is killed blocks all landings for good, with a false "still running". This happens on a reboot, `wsl --shutdown`, or a kill of the whole process group during a long landing. No exit file is written, so the claimed file is never finalised: each later pass says `land-… is still running (one landing at a time)`, claims nothing, and writes no inbox item for that outcome. The approvals stay on disk; nothing is sent wrongly. The reference checked whether the landing process was still alive.
Ordinary work: yes, because a machine restart during a landing of many minutes is plausible.
Consequence: other (landing stops and stays stopped; nothing is sent or lost)
Scope: in (S1, "each outcome becomes an inbox item"); the Interface itself defines finalisation by the exit file.
Would reverse it: an owner reading that a landing with no exit file is meant to wait for a person indefinitely.

RV4: src/gov/dispatch/landing.py:281 Re-approving a failed landing at the same head is ignored without a word. The failed approval's line goes into `land-done.txt` with its non-zero exit code. When the orchestrator writes `W2-7=<same head>` again to retry, it is dropped from every batch: the status says `nothing to land`, `queue` hides it too, and `land.txt` keeps the line forever. This follows the Interface's "never twice", but the drop should at least be named.
Ordinary work: yes, because retrying after a flaky landing failure is ordinary.
Consequence: other (the failure was reported by its own inbox item; the retry is held, not sent twice)
Scope: in (S1)
Would reverse it: an owner ruling that a failed head must never be retried and that a silent drop is acceptable.

RV5: src/gov/dispatch/heavy.py:33 (with procs.py:71) A heavy step that does hold a slot is reported as outside one when started through a shell. Take `bash -c "… gov resources --slot test -- pytest …"`: the shell matches the test marker and is kept as the step, and the walk goes up from the shell, never down to the slot runner. So it gets `slot: null` and the finding `heavy step outside a slot: test pid <shell>`. A step really outside a slot is never hidden.
Ordinary work: yes (same wrapper as RV1)
Consequence: other (a false finding, never a missed one)
Scope: in (S4)
Would reverse it: evidence that heavy steps are never started under a wrapper whose own command line holds the marker.

RV6: src/gov/dispatch/landing.py:110 (with run.py:88, readiness.py:133) A landing's inbox item blocks a new start of its W2 only when the landing had one ticket. Part a's start check compares the W2 being started with each unread item's `W2:` field as a whole string. A landing of one ticket (`W2: W2-7`) therefore holds a start of W2-7 ("unread return") until the item is read. A landing of several (`W2: W2-7 W2-8`) holds none.
Ordinary work: yes
Consequence: other
Scope: out (part a's start check meets part b's space-separated field)
Would reverse it: an owner reading that land items are meant to hold starts, or never to.

Not a finding, a narrow row: finalisation records as landed every good line in the claimed file at finalisation time, not the batch actually sent (`landing.py:103`). A write that had opened `land.txt` before the rename and lands in the inode after the batch was read would be recorded as landed without being sent. Ordinary work: no, because it needs a write to land in the microseconds between the rename and the read. Consequence: loses work. Scope: in (S1). A Wave 3 row.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "RV2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "RV6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "fail", "findings": [{"id": "RV1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "RV5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```