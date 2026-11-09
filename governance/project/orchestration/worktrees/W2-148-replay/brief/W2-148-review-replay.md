Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-148-replay/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-148 — the narrow review of DEC-1108 (2): the replay checks the call set against the guard's log (DAEO-xafn)

You are a fresh, read-only independent reviewer. **Narrow scope: one point.** The owner's DEC-1108 (2) (in
`docs/DECISION_REGISTER.md`; the reasoning in `governance/project/orchestration/packages/ACT-GUARD-CALLLOG-1.md` §2,
§3 (a), §7 item 2; the ticket's new DEC-1108 (2) note and S15's line in `.tickets/DAEO-xafn.md`): **the operator
agent's S15 replay re-judges the CTO's 48-hour call set only after checking it against the guard's call log by sha256
both ways, names the mismatches, and refuses (so the ACT is undone, P1) on any mismatch.** The rest of W2-148 was
reviewed READY and merged; it is not re-opened here. READY is computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-148-replay` in `/home/usain/gov-os-worktrees/W2-148-replay`, head `24abf75a1`, from
  `w2/integrate` at `75a29ff64`: `git diff 75a29ff64..24abf75a1`. The CTO's ticket note (`7438f7e91`); the designer's
  cases and README interface (`tests/acceptance/W2-148/`, `841c64944`, merged at `235d5d45d`); the engineer's change
  (`governance/project/operator/operator_run.py`, `opcommon.py`), its unit cases and the evidence record's section.
- **The CTO's builder** (context, not under review): `.gov-runtime/scratch/orchestrator/tools/build_replay_calls.py`
  in the main tree writes the set; its real run on 2026-11-09 matched the live log both ways.
- **The runs:** the CTO's outside the sandbox at `24abf75a1` with a planted HOME: `gov accept W2-148` **pass, all 39 lines, 0 failed, 0 skipped (183 cases)**; the trial: 60 ACT files (6 a, 22 b, 32 O; none lower than the table), the 9 replays and 7 faults as before, `live_unchanged: true`; the CTO's own live hashes unchanged. The engineer's unit tests: 202/202 (18 new in `tests/unit/operator/test_w2_148_replay.py`). One change outside the stated point, by the engineer: the dry run's own command record moved from `log/calls.jsonl` to `log/operator-calls.jsonl` (so the agent never appends to the set's default path); judge it too.

## Check
1. **Set to log:** can any call be re-judged whose recomputed hash has no log line of the **same session** in the
   window? Is the hash exactly the guard's (`action_bytes` in `.claude/hooks/pretooluse.py`): key order, separators,
   `ensure_ascii=False`, UTF-8? Is the set line's own `sha256` field ever trusted for a call?
2. **Log to set:** can a logged live call (UUID session, `main`/`worktree` tree, inside the window less the 2-minute
   edges) be missing from the set without a refusal? A null hash? A dropped line that is not itself logged?
3. **The window and the log's wholeness:** short or stale windows, a missing header, a capped day, a malformed log
   line, a missing folder: each refused? Can the CTO shrink the window (an early `until`, a late `since`) past the
   stated limits? Day files crossing UTC midnight?
4. **Then the re-judging:** only after all checks; the log's role and ticket used; dropped lines never re-judged; the
   hook's runs with `GOV_GUARD_CALLS_DIR` inside the replay's temporary folder, never the live log.
5. **The refusal's text** names the mismatches by id or session/hash prefix and time, never an input's text; and
   leads to the after-check's undo and P1 as other replay refusals do.
6. **Unchanged behaviour** outside the point: the rest of S15 and the other gates; the trial's outcomes.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns DEC-1108 (2)'s point above.

## Write and return
- **You write nothing** in any tree. You may run the tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-replay/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`
  so pytest is found). Never run anything against the real `~/.gov-os/`, `~/gov-os-operator/`, `~/.claude/`, the
  crontab or a real `claude` session. No GPU. Single simple Bash commands (DEC-1080). The hidden-half rule holds:
  never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your answer to checks 1-6, every finding with its two lines and scope, and at the end the fenced
  `verdict` block over the line DEC-1108 (2) touches:
  `{"kpis": [{"kpi": "S15", "verdict": "pass|fail", "findings": [...]}]}`
  with each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F30).
