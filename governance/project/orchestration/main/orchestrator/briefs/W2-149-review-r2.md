# W2-149 — the independent review (DAEO-52ku), round 2 (the last, DEC-1010)

You are a fresh, read-only independent reviewer. Review round 2 of **W2-149** (`.tickets/DAEO-52ku.md`: read it in
full): the independent sessions' launch script (DEC-1101 (2)-(3) step 2). Profile FULL.

## What happened in round 1
Round 1's review (its full text: `.gov-runtime/scratch/ref/W2-149-review-r1.md` in the worktree) passed every KPI line
but **S12**, blocked by **F1**: for a stopped session the trace check returned 0 without running (no session id when
the output does not parse). Its rows: F3, F4, F5, F6, F7, F8, F9, F10, F12 in scope; F2 and F11 out of scope.

**The CTO's fix for F1 (settled):** the script draws each session's id (`uuid4`) and passes it with `--session-id`
(Claude Code 2.1.318 offers it; S10 says the line "carries" its flags, so one more closing flag amends nothing); the
id is kept only as the trace check's key, never printed; `traces` counts entries named by the drawn id plus the
reported one. Round 2 also fixed F6 (the canary's traces counted the same way), F3 (the test hook recorded in
`WALL.json` and `launch.log`), F5 (delivery folders made only after every check) and F8 (the schemas read once, their
sha256s in `WALL.json`). F4, F7, F9, F10 and F12 stay rows; F2 (the path map's hidden globs) and F11 go to the owner.

## What to review
- **The branch:** `w2/W2-149` in `/home/usain/gov-os-worktrees/W2-149`, head `a929356ea`; round 2's change is
  `git diff 8d4569bfef3c..a929356ea` (`indep_launch.py`, the unit tests, the evidence record's "Round 2" section).
  Review that change in full, and re-judge every KPI line S1 to S21 as the branch now stands (the round-1 record has
  the reasoning for the lines round 2 did not touch: confirm they still hold).
- **The runs:** the CTO's `gov accept W2-149` outside the sandbox at `a929356ea`: **77 passed, 0 failed, 3 skipped
  (live)**; the three live cases (haiku, planted roots, real HOME for the login) at `a929356ea`: **3 passed**: the real
  `claude` accepts `--session-id` beside `--no-session-persistence`, the real canary is refused with valid settings and
  not refused with one key corrupted (16), every outside Read in the live wall refused, 0 traces. The engineer's unit
  tests: 74 passed.
- **Check especially:** can `traces` still read 0 without a check (an id not drawn, an exception between the session and
  the count, a canary failing early); does the drawn id ever reach `counts.json`, stdout, stderr or `launch.log`; do the
  F5 changes keep the delivery all or nothing and inside its destination (links on the way, a folder made then a copy
  failing); do the F8 schema reads fail closed.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree. Run nothing that writes outside your own temporary folder. You may run the tests
  read-only (with `-p no:cacheprovider --optin=lifted --optin=breadth`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149/src`. Never run anything against the real `~/gov-os-eval/`,
  `~/gov-os-runs/`, `~/gov-os-wall-trees/`, `~/.claude/` or a real `claude` session. No GPU. Single simple Bash commands
  (DEC-1080). The hidden-half rule holds. Read the template folder `governance/project/indep-walls/` with the Read
  tool only, never naming it in a Bash line.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your verdict per line, every finding with its two lines and `scope: in|out` (round 1's rows
  carried with their ids), and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S21"]}`.
