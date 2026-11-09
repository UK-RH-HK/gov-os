Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-148-act2/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# ACT-OPERATOR-2 — the independent review of an ACT package (one round; READY by verdict.py)

You are a fresh, read-only independent reviewer. You are not the ACT's author. Review **ACT-OPERATOR-2**: the operator
agent's install re-installed to carry W2-148's replay check (merged `a170641e`, DEC-1108 (2)), and its call set named in
the install's settings. It is class (O) by its package (the operator's own install, applied by the owner's operator by
hand), so it never goes through the operator agent's queue; your verdict block is read by `verdict.py` for the CTO.

Everything you need is copied into your worktree, under `.gov-runtime/scratch/ref/ACT-OPERATOR-2/`:
- `ACT-OPERATOR-2.md` (the package: read it in full), `ACT-OPERATOR-1.md` (the install as it was applied) and
  `OPERATOR-AGENT-1.md` (the design: §2 classes, §4 gates, §5 what stays the owner's);
- `drafts/`: `apply.sh`, `code/opcommon.py`, `code/operator_run.py`, `operator-settings.before.json`,
  `operator-settings.after.json`, `APPROVED.after`, `op2_rehearsal.py`, `rehearse.sh`, `rehearsal.log`;
- `live-install/`: a read-only copy of the live `~/gov-os-operator/install/` as it is today (taken 2026-11-09 by the CTO's
  helper);
- `rehearsal-outputs/`: the rehearsal's own output files (counts and hash prefixes only);
- `build_replay_calls.py`: the CTO's builder of the call set.
The merged code is also in your worktree's tree at `governance/project/operator/` (`w2/integrate` at its head), with
W2-148's evidence `docs/changes/W2-148-evidence.md` ("Replay check") and tests (`tests/acceptance/W2-148/`,
`tests/unit/operator/`).

## Check (each a KPI line of your verdict block)
- **K1 the touched set is exact:** `apply.sh apply` changes only `install/opcommon.py`, `install/operator_run.py`,
  `install/operator-settings.json` and `install/APPROVED` (and its own `backup/`), each to the stated after-hash; every
  other install file is checked unchanged; nothing in the repository, the crontab, the guard, the path map or the git
  hook changes. Compute the hashes yourself from the copies.
- **K2 the undo is real:** `apply.sh undo` restores all four byte for byte from a checked backup and refuses otherwise;
  the rehearsal log shows it.
- **K3 the rehearsal is real:** the log is a run of this `apply.sh` and these files in a clone with a planted HOME, ends
  `failures: 0`, and its counts are what the package states; say where it differs from the live run.
- **K4 the refusals fail closed:** `check`/`apply`/`undo` refuse when the install is in any other state, while the
  operator holds a freeze, a journal or a lock, while a request waits, or while a launch holds `log/launch.lock`; a
  partial failure leaves a state the operator can see (and undo can or cannot restore: say which). Read the script.
- **K5 the class:** by OPERATOR-AGENT-1 §2 and §5, the class you find, whatever the package claims.
- **K6 the settings change is right:** `calls` names a file the CTO can write and the guard's rule 2d does not refuse
  (`write_refused`: `~/gov-os-operator` but `queue/`, and `~/.gov-os/guard-calls`); `guard_calls` stays the guard's log;
  nothing in the new settings weakens a gate. Is anything trusted from the CTO's file that should not be?
- **K7 the package's claims about the replay check are true:** (a) the check does not require the guard's log to cover
  the window's start (read `read_guard_log` and `check_against_log`); (b) the 48-hour point (the log began 2026-11-09
  18:13Z); (c) the `Monitor` call that blocks the real set until about 2026-11-11 20:06Z, and why. Say whether (a) is a
  fail-open for this ACT or a residual (the ACT only installs merged, reviewed code).
- **K8 the code installed is the merged code:** `code/*.py` byte for byte the tree's `governance/project/operator/`
  files at the head, and the after-`APPROVED` lists exactly the install's files.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT's change.

## Write and return
- **You write nothing** in any tree. You may run `apply.sh` only against a copy you make in your own temporary folder
  with a planted HOME (never the real `~/gov-os-operator`, never the main tree), and the tests read-only through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
  `PYTHONPATH=<your worktree>/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`). No real `claude`
  session, no GPU, no network. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/` or any `hidden` folder.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (task,
  status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), your answer to K1-K8, every finding with its two lines and
  scope (ids F1, F2, …), and at the end one fenced block opened with three backticks and the word `verdict`:
  `{"act": "ACT-OPERATOR-2", "class": "a|b|O", "apply_sh_sha256": "<the sha256 of drafts/apply.sh you read>", "kpis": [{"kpi": "K1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "K8"]}`.
Refused twice for the same call: stop and say so; no third try.
