## Round 1

Reviewer: independent-auditor, `claude -p` session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Brief sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a (checked). Manifest sha256 a49a4228dc1e334749e062ecb859e633c652b022564311551b6ddd6c6203a8e5 (computed). All seven `files` entries and all four `before/` and `after/` copies hash as listed. The live tree's two files are the frozen befores (d56a7aa7…, 1e698a71…), and so are those at w2/integrate head 35f4eb9943a5. The bundle was built at 4c55f14179be; the two files are the same bytes at both heads.

**The six checks**
1. **Touched list and path rule: pass.** `apply.sh apply` changed exactly the two listed files in the clone. Nothing changed in the planted HOME, no crontab line was touched, and no temp file was left. `apply.sh` and the manifest name no live path and no `~`/`$HOME`; the only `cd` is into the script's own folder, inside `$( )`.
2. **Undo tested: pass.** In my clone, `undo` restored both files byte for byte (shas d56a7aa7…, 1e698a71…; clean `git status`). The rehearsal log shows the same (F1 to F3, F11).
3. **Rehearsal real: pass.** The log runs this `apply.sh` in a clone and ends `failures: 0`. Every step I repeated gave the same result: A5 to A7, D1, D6 to D8, F5 to F6, and B, C and E for the tests and checks.
4. **Checks right: pass.** Run from the repository with `bash -c` in a clean environment, on the new code: exit 0; exit 0 count 2; exit 0 count 4; exit 0. Checks 1 and 2 are red on the old code.
5. **Class: pass, (O).** `act_class.py` votes O: `stop_idle_check.py` falls to the `unknown` catch-all, and `dispatch/dispatcher.py` is row `watchers` (b). On substance the hook change is a control change. It tightens (more watchers, a new block), but no rule can prove a code change only tightens, so with a named row it would be (b), like its sibling `stop_waiter_check.py`. (O) by hand is correct today (F6).
6. **Guard replay: pass, nothing to replay.** No path-map or deny-list change; `replay_refused` is empty.

**The CTO's added questions**
- **(1) Class.** (O) is right. `stop_idle_check.py` should have a named row: `guard-hook`, b, control (F6).
- **(2) No trap.** The new code runs inside `decide()`, and `main()` catches every exception, logs it, exits 0 and lets the turn end. Seven planted cases, all rc 0 with no stderr:
  - a plan-named ticket: blocked;
  - the second stop of that turn (`stop_hook_active`): let through, with the launchable note;
  - an IDLE-REASON while a ticket is launchable: let through, logged "WHILE a ticket was launchable";
  - `gov` missing: not launchable, so the old path decides;
  - a tick 600 s old: not relied on, old path;
  - a malformed `lead_count`: logged as an error, the turn ends;
  - a hanging `gov`: killed at 30 s, the old path decides (32.9 s in all; see F3).

  The once-per-turn state is written before the block returns.
- **(3) False blocks.** These come from both arms of the check, not only the plan's (F1, F2). An honest CTO hits them in ordinary work. Each costs one extra turn and a misleading note to the owner. None fails open or loses work.
- **(4) Dispatcher.** The change adds `watch_headroom()` inside its own `try`, after `start_one()`. It writes one inbox item (`log:`/`Idle:`/`status:` format, no `W2: ` line), `idle-headroom-reported.json`, a log line and two status keys (`ready_count`, `max_leads`). It never launches, stops or refuses anything, and writes nothing in a dry pass. One small point: if `start_one()` raised, `waits` is empty and the item may call the list "waiting"; the pass's failures list still shows the error.
- **(5) apply.sh.** Each file's state is decided by its sha256 alone. A first pass reads every file and refuses (exit 3) before any write unless each file is the before or the after. I reproduced this: dispatcher changed, apply refused, the hook untouched. Frozen copies are hashed before use (exit 4). Links and missing files are refused.
- **(6) Tests.** 13 of the 16 fail on the old code for the stated reasons (no block, or missing text); the other 3 are "does not fire" cases. On the new code: 226 passed, 3 skipped, 10 `local_only` deselected. Existing cases stay green.

**Findings**

**F1. A finished lead's line reads "launchable".**
- KPI: check 4, the behaviour under check. Scope: in.
- Ordinary work: yes, because `why_not()` answers "running" while the lead's process lives, then "already started for <log>" as soon as it ends, whatever it returned. The dispatcher never removes a `ready.txt` line. Today's list holds three such lines (W2-170 tests2, W2-04 r6c, W2-81 r5b), and each becomes "launchable" when its lead returns, until the CTO comments it out.
- Consequence: other. One extra turn per return (once a turn), including while the CTO verifies that same return in the background, because the block comes before the running let-through. The owner sees a false "WHILE a ticket was launchable" note. The block's text and the dispatcher's hourly item both advise "write the line again with a new log name", which points towards relaunching a finished lead. No work is lost, and nothing fails open.
- Evidence: the `after/` hook lines 350 to 351 and the `why_not()` order; the live `ready.txt`; the test `test_a_used_log_ready_line_with_an_open_gate_blocks_whatever_runs`.
- Fix (follow-up): in the block's text and the item, add "or comment the line out if its ticket needs no new run". Optionally, leave out a line whose W2 has an unread return item (the dispatcher already computes `inbox_w2s`).

**F2. The plan arm names merged and parked tickets.**
- KPI: check 4. Scope: in.
- Ordinary work: yes, but only while `ready.txt` has no line (`ready_count` 0) and leads are below the cap. Then every turn end is blocked once until batch 1 is closed.
- What it names today (`gov plan --ready`, 1.1 s): 11 tickets after dropping W2-00. W2-131 and W2-139 are merged into integrate and still `in_progress` (awaiting close). W2-11 is off the list by the CTO's 18:20 note (merge conflicts). W2-94, W2-140, W2-40 and W2-66c have no branch yet. W2-04 is merged and running: left out only while the tick lists it in `leads`, and a pending launch is not left out.
- Consequence: other. The text does say "not yet shown startable, a brief or a claim may be missing", and closing merged tickets is itself CTO work under rule 1. But "launchable" overstates it, and a ticket the owner or CTO parked outside the plan can't be told apart.
- Evidence: the plan output, `git merge-base --is-ancestor` per branch, and ticket `status:`.
- Fix (follow-up): leave out tickets whose branch is already in w2/integrate, or name them "to close"; consider a parked list the hook reads.

**F3. The plan's timeout is longer than the hook's.**
- KPI: check 4. Scope: in.
- Ordinary work: no, because `gov plan` takes about 1.1 s at load 9.6 on 20 CPUs. It would take a hung `gov`, git lock or disk.
- Consequence: fails open. `PLAN_TIMEOUT_S = 30`, but the live Stop hook entry gives the hook `timeout: 10`. Past 10 s, Claude Code kills the hook: no log line, no message from the hook, a `plan-ready-*.txt` left in `log/`, and the turn ends unchecked. That contradicts the docstring's "never fails open silently".
- Evidence: `.claude/settings.local.json` lines 93 to 94; the hanging-stub run, 32.9 s.
- Fix: `PLAN_TIMEOUT_S = 5`, or raise the settings timeout, which is its own (b) change.

**F4. No cap is known until `max_leads` is written.**
- KPI: check 4. Scope: in.
- Ordinary work: yes, in the window §5 creates by writing `max_leads` after the apply. Until then the hook reads "no cap" and blocks at any lead count the forecast admits, with "Start them now". That goes against the owner's "at most 3 until ACT A". It doesn't fire at this moment: with 3 leads the tick shows `admit: false`.
- Consequence: other. The honest answer is an IDLE-REASON; nothing starts by itself.
- Fix: write `"max_leads": 3` before `apply.sh apply`. The old code ignores the key, so this is harmless.

**F5. Check 2 writes byte-code into the repository.**
- KPI: check 4. Scope: in.
- Ordinary work: yes, because every run of check 2 does it.
- Consequence: other, harmless. It writes `tools/dispatch/__pycache__/dispatcher.cpython-312.pyc` and `balancer…pyc`. They are git-ignored and already present in the live tree. But the package says the checks leave only `mktemp` folders.
- Fix: `sys.dont_write_bytecode = True` at the top of check 2 (or `python3 -I -B`).

**F6. The hook has no named row.**
- KPI: check 5. Scope: out (a change to `class-rules.yaml`, the owner's).
- Ordinary work: no, because only the classifier's vote is affected.
- Consequence: other.
- Evidence: `act_class.py` output: row `unknown` for `stop_idle_check.py`; its sibling `stop_waiter_check.py` is in `guard-hook`.
- Fix: the owner adds `governance/project/orchestration/tools/stop_idle_check.py` to row `guard-hook` (b, control: true) in a separate change. Until then (O) by hand is right.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": []},
          {"kpi": "check 2", "verdict": "pass", "findings": []},
          {"kpi": "check 3", "verdict": "pass", "findings": []},
          {"kpi": "check 4", "verdict": "pass",
           "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
                        {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
                        {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
                        {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
                        {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "check 5", "verdict": "pass",
           "findings": [{"id": "F6", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
          {"kpi": "check 6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "a49a4228dc1e334749e062ecb859e633c652b022564311551b6ddd6c6203a8e5",
 "class": "O",
 "reviewer": "independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-11T18:34:00+00:00",
 "replay_refused": []}
```

Scratch: peak 230M and 34,967 inodes (clone, pytest temp files). After removal, `du -sh` shows 60K and `du -s --inodes` shows 11. The clone is removed.
