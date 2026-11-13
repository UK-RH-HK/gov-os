Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief rev-3: independent reviewer (STANDARD review) for DAEO-ozyt (W2-157), class C2: the reopened fix's diff

You are a fresh, read-only independent reviewer (independent-auditor) of ticket DAEO-ozyt (W2-157: the GPU backstop,
`gov resources --backstop <pgid>...`). The backstop passed its STANDARD review earlier today (round 2, head
365a4acda69b; the record is docs/probes/DAEO-ozyt/). The owner reopened the ticket for one fix (DEC-1144 (2), P1-B (a)):
read the ticket's last section "Reopened for one fix" first. You review that fix's diff, by running it as well as
reading it, against the ticket's KPI lines (S1-S5, F1-F4; mostly S4 and F1) and the fix as the ticket states it. You
write nothing in the repository: everything you plant goes under your session's `$TMPDIR`. Your lead writes the probe
record from your return.

## What to read
| what | path |
|---|---|
| the ticket (KPI lines with their Verify; the last section "Reopened for one fix") | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| the fix's diff: `git -C /home/usain/gov-os-worktrees/W2-157 diff 13ab2c9fe f5b148151` (13ab2c9fe is the merge of w2/integrate into the branch; the fix is the two commits after it) | src/gov/resources/backstop.py (`_state_and_group`, `_thread_runs`, `_all_ended`, `_live`, `watch(..., max_polls=)`), tests/unit/resources/test_w2_157_backstop.py, docs/changes/W2-157-evidence.md (section "Reopened fix (DEC-1144 (2))") |
| the readings L1-L9 and L5b the code was built to | docs/changes/W2-157-evidence.md |
| the earlier rounds' probe record (FR-1 to FR-13; do not re-raise the residual rows unless this fix changed them) | docs/probes/DAEO-ozyt/ |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1067, DEC-1068, DEC-1073, DEC-1144 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The fault and the fix (as the ticket states them)
`test_s3_the_limit_comes_before_the_spill_before_the_embedder_before_the_log` hung two merge-queue runs: the test
replaces the backstop's sleep and calls `watch()`; a call that does not trip polls forever, because a group of only
zombies (unreaped) or paused processes still passes `os.killpg(g, 0)`. The fix: (1) a group whose live members are all
zombies counts as ended (read `/proc/<pid>/stat`; nothing by name); (2) `watch()` takes a bound, a keyword argument
whose default keeps the command's behaviour, and every test that calls it passes one; (3) each test reaps the groups it
plants. The engineer also found the test's own non-trip (its replaced sleep overwrote the log with equal bytes, so a
call that started at offset 28 never saw a new line) and made the sleep append.

## What the lead already ran (do not re-run whole suites; DEC-959 item 1)
- The engineer: the backstop file 20 times under `timeout 120`, 20 of 20 exit 0 (132 passed each);
  tests/unit/resources 318 passed; tests/acceptance/W2-157 116 passed; tests/acceptance/W2-20 170 passed.
- The lead: the same 20-run loop under added CPU load, and the scoped verify of the head, alongside you.

## What to probe (safety first: the backstop pauses real process groups)
Run `backstop.watch` or `python3 -m gov.cli.main resources --backstop ... --root <planted project> --json` with this
tree's `src/` on `PYTHONPATH`, a planted `HOME` (its own `.gov-os/machine/gate.json`), a stand-in `nvidia-smi` first on
`PATH`, planted logs, all under `$TMPDIR`. Signal and pause only process groups you start yourself
(`setsid`/`start_new_session`); send each SIGCONT then SIGKILL when done and reap them; stop anything stuck by its pid,
never by a name. Never the real GPU, the real HOME's gate.json, the real embedding servers. Probe at least:
- the zombie rule: a group whose only member is an unreaped zombie ends the watch untripped with the `end: every
  watched group has ended` line; a zombie leader with a live child in its group stays live and is paused on a trip; a
  zombie leader whose other threads still run; a paused (SIGSTOP) group stays live; a group that turns all-zombie
  mid-watch; whether the rule can ever call a live group ended (fails open: a GPU job left running past a trip), e.g. a
  member in uninterruptible sleep (`D`), a process whose `/proc/<pid>/stat` cannot be read, a command name holding `)`
  and spaces;
- the bound: the default (no `max_polls`) behaves as before for the command (`command.py` unchanged); `max_polls=n`
  ends after exactly n polls without a trip and logs one line; a trip on the last allowed poll; invalid bounds; whether
  the bound's line or return changes the L6 log or L8 result for the command;
- the tests: every unit-test call of `watch()` passes a bound or has its own runaway guard; every process a test plants
  is reaped, also when the test fails (try a forced failure); no `time.sleep` busy-loop left; the S3 order test now
  trips deterministically whatever the earlier calls did;
- that nothing else changed: F4 (`git diff --name-only 5d915dc6c f5b148151` against the ticket's allowed_paths), no
  KPI line or acceptance test changed, and S5 (only the log and the one inbox item written) still holds with `/proc`
  read.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then:
- `What was probed:` the setup and each probe, run or read.
- `Findings:` each as `FR-<n> (<severity>): <one line>` (numbered from FR-14; earlier rounds used FR-1 to FR-13), then
  what was done, what happened, what should have happened, known or new, and whether ordinary work reaches it.
- One fenced block opened by ```verdict holding JSON, one entry per KPI line S1-S5 and F1-F4, and a top-level
  `"ready": true|false` (the fix lands as is):
  `{"ready": true, "kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "FR-14", "scope": "in|out",
  "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`. A KPI line is marked fail only
  when it does not hold; a finding goes under the line it bears on.
- `guard_refusals:` none, or each: time | form | the hook's reason | true or false-positive.
