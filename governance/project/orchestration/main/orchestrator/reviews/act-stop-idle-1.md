# Review: ACT-STOP-IDLE-1 (DEC-1110 (1)), the CTO's idle check as a second Stop hook

- **Reviewer:** the one independent reviewer, 2026-11-09, read-only (this record only).
- **Reviewed:** `packages/ACT-STOP-IDLE-1.md`; `drafts/stop-idle/`: hook `482663cb476f`, tests `46d06d1513c0`,
  `settings_edit.py` `b9afa575c4ed`, `apply.sh` `1441f951309c`, `rehearse.sh` `d8d0bf9f908b`, `rehearsal.log`
  `49170181563c`, `mutation.log` `82a572c00f52` (all hash as the package's §8 pins); the live Stop hooks
  (`.claude/settings.local.json` `2b8909d236b7`: `stop_waiter_check.py`; `.claude/settings.json`: the kernel
  `stop.py`; `~/.claude/settings.json`: none); `packages/DECIDED-NOT-DONE.md` at `49885f32b`; OPERATOR-AGENT-1 §2–§3.
- **Run:** the 24 draft tests (24 passed, 1.27 s); the hook's classifier on the live DECIDED-NOT-DONE; two planted
  reproductions in my scratch (F1, F2; removed after); the CTO's live transcript, subagent meta files, task folder and
  pid files read to check the "running" sources.
- **Retrieval:** `gov retrieve` not used; every question was answered by reading the named files directly. Guard
  refusals: 0.
- **Findings' classification (DEC-809):** 3 must-fix (in scope, ordinary work, fail open); 10 rows.
- **Class vote:** **(O)**, not (b) (row R8).

## Verdict: NOT READY

## Must fix

### F1. A scheduled wakeup is not read as a new turn, so after one block or one IDLE-REASON every later wakeup turn ends unchecked
`turn_and_reason()` takes the turn's id from the last user entry that is not `isMeta`. In this Claude Code version
the scheduled wakeups (the 09:00 and 18:00 digests, every `schedule_wakeup`) are user entries with `isMeta: true`,
`wakeupSource: "schedule_wakeup"`, `turnOrigin: "scheduled"` (5 in the CTO's live transcript). The hook therefore reads
a wakeup turn as part of the turn before it:
- if the hook blocked in that earlier turn, the wakeup turn's stop matches the stored turn and is let through as
  "a second stop this turn, let through (no IDLE-REASON line stated)";
- if the earlier turn holds an `IDLE-REASON:` line, the scan collects it (it reads assistant text back to the last
  non-meta user entry) and the wakeup turn passes "on the CTO's stated reason" with the old reason.

Reproduced on a planted transcript: a block in turn 1, then a digest wakeup turn with an unblocked item: let through
as "a second stop this turn". With an IDLE-REASON in turn 1: let through on that old reason. The test "a reason line
from an earlier turn does not count" covers only a non-meta boundary. When the CTO is idle, scheduled wakeups are its
only wakeups, so this case is the target of the rule, and it continues until the next non-meta user entry.
- Ordinary work: yes, because the CTO wakes on scheduled digests twice a day and on its own wakeups, and an idle CTO
  wakes on nothing else.
- Consequence: fails open
- Fix: treat a user entry that carries `turnOrigin` (or `wakeupSource`) as a turn start, even when it is `isMeta`. In
  the live transcript the Stop hook feedback and the system reminders carry no `turnOrigin`, so the bound still holds.
  Add a test with a meta wakeup between two turns.

### F2. Closed words that carry a pending next step read as closed
`CLOSED_WORDS` includes READY, APPROVED, FILED, DECIDED and ANSWERED. In DECIDED-NOT-DONE these words usually come
before an action that is still the CTO's to do. Live rows read as **closed**:
- #21: "ANSWERED …; next: the lines into W2-88 …"
- #32: "Filed …; next: its test designer"
- #38: "Filed DAEO-btcs …; its test designer next"
- #52: "APPROVED (DEC-1104 (2)); next: build it, tests first, one review, a replay trial"
- #69: "READY 11-09: W1-06 on w2/W2-130-d10-tests (reviewed …)", which is ready to merge, a CTO action

Each of these follows the package's rule for the CTO ("begin each state with one of the words above"), yet each
hides unblocked work. Reproduced: rows "APPROVED; next: build it", "READY: to merge" and "Filed; its test designer
next", plus one owner wait. Result: let through, "every open item waits (1 on the owner, 0 on a running job, 0 on a
trigger)". The three are not named anywhere. This is the end-of-queue case: once the NOT STARTED and IN PROGRESS rows
are gone, these are what remain.
- Ordinary work: yes, because five live rows have this form today.
- Consequence: fails open
- Fix: a state with a `next` clause (`\bnext\b`) and no WAIT word is open. Read READY, APPROVED and FILED as open
  unless a WAIT word follows (or drop them from the closed list). Since a block happens at most once a turn, err toward
  open. Add tests with the live forms of #32, #52 and #69.

### F3. Background tasks and pid files have no age bound, so a loop that never ends lets every idle turn through silently
An unfinished agent counts only for 30 minutes after its last write. A background task or a pid file counts for as
long as its process lives, and a let-through on "running" sends nothing to the owner (only `log/stop-idle.log`). Live
cases, today:
- the CTO's task `bqav99dw4` is `until grep -q "== …W2-140-tests" …b83w7niwj.output && …; do sleep 10; done`, with no
  bound. If the test run it watches dies before printing, it loops forever;
- the package's own residual: a new standing watcher counts as running until it is added to `WATCHERS`, and the CTO
  has added six so far;
- a service left up beside its pid file (`gov-os-runs/D4B/score-once/svc.pid` is of this kind).

Each one masks idling for hours or days without a word to the owner. `wait_for.sh` (capped at 570 s) and
`proc.sh wait --max` are bounded, which shows that the CTO's own waits need not be unbounded.
- Ordinary work: yes, because an unbounded until-loop is running in the CTO's session now.
- Consequence: fails open
- Fix (small): when every counted item is a task or pid file older than a bound (say 2 h), let the turn through with a
  `systemMessage` that names them ("running only: … for N h; check it is work"), or stop counting them past the bound,
  as for agents. Add a test for each.

## Rows (Wave 3 or the CTO's backlog; none blocks)

- **R1. The IDLE-REASON escape, and whether the owner sees it.** It is recorded in the log and in an in-session
  `systemMessage`, and in no digest. `grep` finds no reader of `stop-idle.log`. It is checked before everything else,
  so a line written out of habit skips the reminder even when items are unblocked. The bound (one block a turn) already
  keeps the check from blocking forever, so the escape is needed only to skip the one reminder. Recommend: consult the
  reason only when the check would otherwise block, and log "reason used" or "reason not needed"; put a daily count of
  reasons used, with their text, in the digest.
  - Ordinary work: yes, because a compacted CTO can settle into a habit after a few blocks.
  - Consequence: other (each use is recorded and shown)
- **R2. An agent silent for more than 30 minutes** (a long model call, a hung tool) is not counted, which gives one
  wrong block. Its foreground commands do count, as tasks: checked live, a foreground Bash call writes
  `tasks/<id>.output`.
  - Ordinary work: yes, rarely.
  - Consequence: other (one wrong block, which passes on the next stop)
- **R3. The WSL clock and the pid globs.** A process's start is computed from `/proc/uptime`. After a host suspend the
  wall clock can move ahead of the boot clock, so a pid file that does not name a launcher (the `gov-os-runs` runs) is
  refused as a reused pid, and the block says "no launched worker". Separately, the main tree's
  `lead/log/verify/verify.pid` is not in the globs (only `lead/log/*.pid` for ROOT).
  - Ordinary work: yes, on a laptop host.
  - Consequence: other (wrong block once)
- **R4. Edges of the state parsing.**
  - `WAIT` and the open words are case-sensitive: "waits on …" and "in progress" in lower case are unclassified, or
    closed when the state begins "Done …".
  - "DONE (part 1); part 2 NOT STARTED" reads closed, because NOT STARTED counts only at the start.
  - "NOT STARTED; WAITS: X" reads open.
  - Unclassified states are named but read as not unblocked. Since a block is bounded, reading them as open would err
    toward the reminder.
  - "WAITS on a running job" is not checked against step 4's own finding that nothing runs. Live: 0 such rows. The
    count "N on a running job" shows the contradiction in the message.
  - Ordinary work: yes.
  - Consequence: fails open but named (the message counts or names the row); other otherwise
- **R5. The waiter's block marks the idle check's record.** When the inbox waiter blocks, the next stop carries
  `stop_hook_active`. The idle check then logs `through / bound: blocked once this turn` and tells the owner "a second
  stop this turn … no IDLE-REASON line stated", though it never blocked. The record then reads as if the CTO ignored a
  reminder. The waiter itself is unaffected: its command is byte-identical, its 6 tests pass, and it honours
  `stop_hook_active` as before. A waiter that ends during a continued turn still sends a task notification, which
  starts a new turn.
  - Ordinary work: yes.
  - Consequence: other
- **R6. Machine-wide jobs count as the CTO's.** The dispatcher's `jobs` include any heavy test run, the rebuilds and
  the nightly. While the nightly runs, the hook never blocks. The nightly's cron is stopped (DEC-1049), so this is
  feature-gated (DEC-803): an entry criterion for the ticket that turns the nightly back on.
  - Ordinary work: no today (feature off).
  - Consequence: fails open when on
- **R7. "Machine full" and "gate shut" let the turn through even when the unblocked items are light CTO work** (a
  package, a DECIDED-NOT-DONE update) that needs no lead slot. This follows the decision's words; the package states
  the stricter per-item check as an unbuilt option.
  - Ordinary work: yes (live now: `admit: false`, CPU-bound).
  - Consequence: other (follows DEC-1110 (1) as worded)
- **R8. The class.** OPERATOR-AGENT-1 §2 puts "tests" and "a path no rule names" in (O), and `Role: owner` records in
  (O). §3 says the highest of the three votes applies. The full ACT installs a test file, commits with `Role: owner`,
  and `act_class.py` votes (O). The class is **(O)**. The package's head line and §6 ("Class (b)") understate it.
  Nothing fails open: §6's procedure (by hand, plain terminal, `Role: owner`) is already the (O) procedure, and the
  operator agent would refuse it as (b). Fix the head line and the message; show the disagreement in the digest as §3
  requires.
  - Ordinary work: yes.
  - Consequence: other (fails closed)
- **R9. The hook is not in `class-rules.yaml`'s guard-hook row.** The package already lists this as the owner's (O)
  change. Until then, a later CTO edit of the hook, for example adding a watcher as §7 foresees, is not flagged by the
  landing check.
  - Ordinary work: yes.
  - Consequence: other
- **R10. A wording slip.** Package §4 says the clone is at `d1f50e2fa`; `rehearsal.log` says
  "clone at 6a8707001".
  - Ordinary work: yes.
  - Consequence: other

## Checked and sound
- **Never blocks forever:** `stop_hook_active` and the stored turn bound it to one block a turn. A state file that
  cannot be written raises an error, which is named rather than turned into a block. The settings guard exits 1, never
  2. The timeout is 10 s; measured runs take 26 to 63 ms.
- **Parse errors are never silent:** every `CheckError` and every other exception is named in a `systemMessage` and
  logged; the hook always exits 0. Five malformed files are tested, and an unclassified state is named.
- **Running sources:** agent meta `finished` matches the live picture (6 unfinished, all running, this review among
  them). The task folder's path, built from the transcript, matches the live layout. The `eval '…' < /dev/null`
  extraction works on the live wrapped commands, and the watchers and bare sleeps are excluded (all live ones
  matched). The pid-file start-time rule plus the always-accepted launchers handle pid wrap. A stale `status.json` is
  named and not relied on.
- **apply/undo:** pinned hashes; the live settings hash as rehearsed (`2b8909d236b7`). `verify` compares the parsed
  files with the one entry removed. Undo restores the backup only when the bytes match, and otherwise removes only the
  entry. Committed files are left for a revert. The rehearsal record shows 0 failures, the 13 live paths unchanged
  after, and the 13 mutants killed.

```verdict
{"class": "O", "kpis": [
 {"kpi": "K0 bound: once a turn, never forever, the reason line only for this turn", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "K1 running: false nothing-running and false running", "verdict": "fail", "findings": [
   {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R6", "scope": "out", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "R7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K2 state parsing and the unrecognised state", "verdict": "fail", "findings": [
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "R4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K3 the IDLE-REASON escape recorded and shown", "verdict": "pass", "findings": [
   {"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K4 the inbox waiter unaffected", "verdict": "pass", "findings": [
   {"id": "R5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K5 apply, undo and the rehearsal", "verdict": "pass", "findings": [
   {"id": "R10", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K6 the class", "verdict": "pass", "findings": [
   {"id": "R8", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R9", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}
]}
```

Evidence: my own scratch use was a planted world of a few files, removed after the run. The shared scratchpad
measured 31,496 inodes and 368 MB, which is other sessions' content.

## Round 2 (the last), 2026-11-09

- **Reviewed:** hook `d56a7aa79331`, tests `a58027c533fd`, `apply.sh` `eb1d3a086a3f` (pins these two and keeps the
  settings pins `2b8909d236b7` → `d715292711a2`; `settings_edit.py` `b9afa575c4ed` unchanged), `rehearsal.log`
  `2bfb87085175` (clone at `7a3c527c8`, 0 failures), `mutation.log` `717c86af803c` (20 of 20 killed), the rewritten
  package. All hash as stated.
- **Run:** the 31 draft tests (31 passed, 1.76 s); the classifier on the live DECIDED-NOT-DONE; planted reproductions
  of F1 and F3 in scratch (removed after).
- **Findings' classification (DEC-809):** 0 must-fix; 2 new rows.

### The three fixes, in context
- **F1, fixed.** A user entry with `turnOrigin` or `wakeupSource` now starts a turn.
  - Checked on the CTO's live transcript: 161 prompts and the 5 scheduled wakeups carry `turnOrigin`. None of the
    1,195 tool results, the 2 Stop hook feedback entries or the 4 system reminders carries it. So the bound still
    holds inside a turn, and a tool result does not restart one.
  - Replayed my round-1 case (a block and an `IDLE-REASON` in turn 1, then a digest wakeup with a tool call inside):
    the wakeup turn is checked and blocked, and its second stop is let through.
  - A continuation after Stop hook feedback is still the same turn: blocked once, then let through.
- **F2, fixed.** On the live file, #21, #32, #38, #52 and #69 now read open. Counts: 19 open, 33 closed, 20 waits
  (3 on the owner). READY, APPROVED, FILED, ANSWERED and unknown words read open. A block is bounded, so erring toward
  open is right.
- **F3, fixed.** A task or pid file older than 3 hours is not counted and is named in the block and in every
  let-through message. Replayed: with only a 4-hour until-loop alive, the turn blocks, where round 1 let it through
  silently. When something else is running, the item past the bound goes to the log only, which is fine because real
  work runs.
- **R8, done.** The class is (O) in the head line and in §6's message.

### Nothing new wrong; two rows
- **R11. A pending step written in prose still reads closed.** The step is not phrased `next` or `; then`. Live
  examples: #42 "APPLIED …; the CTO merges the live worktrees …" and #68 "MERGED …; the installed agent needs a
  re-install ACT …". No classifier reads prose completely. Recommend: add "write a pending step as `next: …`" to the
  CTO's standing-rules list, and restate #42 and #68 that way.
  - Ordinary work: yes, because two live rows have this form.
  - Consequence: fails open, but only through a writing-convention lapse that a rule can close, so a row (no third
    round, DEC-1010)
- **R12. WAIT now matches in any case.** So prose such as "W2-88 waits on W2-145" turns a DONE row (#31) into a wait,
  and would turn an unknown-word state into a wait rather than open. Harmless today: #31 is done.
  - Ordinary work: yes.
  - Consequence: other

### Verdict: READY

```verdict
{"round": 2, "class": "O", "kpis": [
 {"kpi": "K0 bound: once a turn, never forever, the reason line only for this turn", "verdict": "pass", "findings": []},
 {"kpi": "K1 running: false nothing-running and false running", "verdict": "pass", "findings": [
   {"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R6", "scope": "out", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "R7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K2 state parsing and the unrecognised state", "verdict": "pass", "findings": [
   {"id": "R4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R11", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"},
   {"id": "R12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K3 the IDLE-REASON escape recorded and shown", "verdict": "pass", "findings": [
   {"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K4 the inbox waiter unaffected", "verdict": "pass", "findings": [
   {"id": "R5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "K5 apply, undo and the rehearsal", "verdict": "pass", "findings": []},
 {"kpi": "K6 the class", "verdict": "pass", "findings": [
   {"id": "R9", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
