Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-148/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-148 — the independent review (DAEO-xafn), round 1

You are a fresh, read-only independent reviewer. Review **W2-148** (`.tickets/DAEO-xafn.md`: read it in full, with its
body's "Readings settled by the CTO"): the operator agent, which applies ACTs by class from a queue in a walled
headless session, only when every gate passes (the owner's DEC-1104 (2), approving
`governance/project/orchestration/packages/OPERATOR-AGENT-1.md`; read the package's §1 to §6, the specification).
Profile FULL. This agent will apply changes to governance files and controls without the owner at the terminal: a gate
that fails open is the fault that matters most.

## What to review
- **The branch:** `w2/W2-148` in `/home/usain/gov-os-worktrees/W2-148`, head `45dd9e2dc`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-148`): `governance/project/operator/**` (`operator_run.py`, `opcommon.py`,
  `act_class.py`, `class-rules.yaml`, `operator_launch.py`, `landing_check.py`, `verdict.py`, `brief.md`,
  `reviewer-brief.md`, `wall/settings.json.tmpl`, `wall/operator_wall_hook.py`); the engineer's unit tests
  `tests/unit/operator/test_w2_148_*`; the designer's cases `tests/acceptance/W2-148/` (and their README's interface);
  `docs/changes/W2-148-evidence.md` (the trial, S23).
- **The runs:** the CTO's `gov accept W2-148` outside the sandbox, with a planted HOME: **157/157, all 38 lines pass,
  0 skipped**; the live operator folder, `~/.claude`'s settings, the crontab, the live hooks and the pin hashed before
  and after: unchanged (one owner's-operator log line written meanwhile by the owner's own session, not this run). The
  engineer's: unit `tests/unit/operator` 108 passed; the trial: 57 ACT files (6 a, 19 b, 32 O; 22 rises), 8 replays as
  expected, 7 faults refused, undone or lock held.

## Check, against each KPI line S1 to S24 and the fourteen failure lines
- **Every gate fails closed:** for G1 to G9, the recompute and the after-checks, can an exception, a missing or
  malformed input, an unreadable file or a timeout ever be read as a pass? Read each gate's code path, not only its
  test.
- **The classifier (S6, S7, S8):** each row of the package's §2 table as `class-rules.yaml` encodes it; the "only
  added / only removed" parsing (can a reordering, a duplicate, a comment, a key moved between lists, or a YAML anchor
  pass as (a)?); the script scan (can `sudo`, a push, a tag, an install, a network call or an `rm` outside the project
  slip past it, e.g. through a variable or a `$(...)`?); the class only rises.
- **The engineer's own readings, to judge each (in scope or not, and whether it fails open):**
  - **an empty touched list classifies as (a)**: can an ACT with no touched files but commands (a crontab line, an
    install, a settings write through a script) reach the apply as (a)?
  - **the default `push_cmd` is `deadman.py --channel push --test`**: does `--test` mean a live notice never reaches
    the owner (F10)?
  - **`close_flag` defaults to `<scratch>/CLOSE-RUNNING`** and the nightly window to `03:50-08:00`: does anything
    today write that flag, so G9 can hold for a close at all?
  - the launcher starts no session while G9 would hold; refusals pushed from G7 on; (b) apply notices always pushed;
    a transcript line without `origin.kind` never a yes.
- **The yes and the undo line (S10, S22):** only a human-marked user line after the review's time, with the right ACT
  and sha8; never a tool result, task notification, meta or sidechain line; read only from the transcript named in
  `log/cto-session.txt`.
- **The dry run (S12) and the after-check (S15):** the changed set compared in the clone's tree and the planted HOME
  (untracked and ignored files, git hooks included); the control-file list against the package's §3 list; the guard
  replay's old and new map; undo byte for byte.
- **The launch and the wall (S17 to S19, S24):** the session's flags and clean environment against the ticket and
  `.gov-runtime/scratch/ref/LAUNCH-SPEC.md` S10 (the engineer names `--permission-prompts none`,
  `--disable-slash-commands` and `--tools` as not exercised live); the wall hook's allowed forms: can a Bash line chain
  a second command (`;`, `&&`, `|`, `$(...)`, a newline) after an allowed form, or call `operator_run.py` with another
  step or option? Does it refuse `git push`, `git tag`, `sudo`, `tests/acceptance/**`, its own install, and
  `~/.claude` beyond the named transcript? Waits and stops by pid or pgid only.
- **Nothing live by default:** does any default path (operator root, HOME, scratch, transcripts, calls, push) make a
  test or the trial (`tests/unit/operator/test_w2_148_trial.py`) write a live place when a setting is left out? The
  CTO runs the trial outside the sandbox only after your answer.
- **The landing check (S16):** "outside a ticket" as `landing_select.sh` reads it; the named (b) and (O) rows only.
- **The trial (S23):** re-read a sample of the 57 rows against the table; are the rises right, and is any ACT lower
  than the table?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree. Run nothing that writes outside your own temporary folder. You may run the tests
  read-only (with `-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148/src`. Never run anything against the real `~/gov-os-operator/`,
  `~/.claude/`, the crontab or a real `claude` session. No GPU. Single simple Bash commands (DEC-1080). The
  hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own, different words;
  then answer from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full (the launcher keeps it in this worktree's log; the CTO
  transcribes it): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per
  line, every finding with its two lines and `scope: in|out`, and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S24"]}`.
