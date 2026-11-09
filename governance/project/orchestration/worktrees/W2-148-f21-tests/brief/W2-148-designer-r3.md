Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-148-f21-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-148 — the independent test designer's brief, round 3: F21 (DEC-1107) (DAEO-xafn)

You are the independent test designer for **W2-148** (`.tickets/DAEO-xafn.md`, with its DEC-1106 note and fifteenth
failure line): the operator agent (the owner's DEC-1104 (2), `governance/project/orchestration/packages/OPERATOR-AGENT-1.md`).
Your earlier rounds wrote `tests/acceptance/W2-148/` (166 cases, now merged into `w2/integrate` with the agent at
`511a4a17`). Read your own README (its interface and the DEC-1106 restore rule, N-9) and support module first.

## What the owner decided (DEC-1107; its text in your worktree at `.gov-runtime/scratch/ref/DEC-1107.md`)
One tiny extra round before the agent is installed: **the owner-undo path (`operator_run.py --config C undo <ACT>
<manifest sha>`, on the owner's `undo ACT-<id> <sha8>` line, S22) and the crash-recovery path (the launcher finding an
unfinished journal and undoing first, S22) must exit non-zero and say `refused` (the result line's `result`) whenever
they leave another's files untouched**, with the P1 naming each file and the lock held, as before. Today the review
found the owner's undo returns `result: "undone"` with exit 0 in that case (the recovery may already exit non-zero, but
its result word is `undone`). The ACT's own touched files are still undone where they can be shown to be its own.

## What the cases must show (add them first; the engineer then builds)
- **The owner's undo, leaving another's file:** an ACT applied live (any class); then "someone else" changes one of
  its touched files to bytes that are neither its before- nor its after-copy (a deterministic trigger: no hook point is
  needed, since the change is made before the undo is called); then a valid owner's `undo` line in the planted
  transcript and the undo step run. Expect: exit non-zero; the last stdout line's `result` is `refused`; that file left
  exactly as the other wrote it; the ACT's other own touched files undone (before bytes); a P1 whose `text` names the
  left file; the lock held (the next queued ACT not launched, S22's form).
- **The crash recovery, leaving another's file:** an unfinished journal (S22's planted form, a run stopped mid-apply),
  with one of the ACT's touched files changed by someone else to third bytes before the next launch; then the launch.
  Expect: the launcher's result non-zero and `refused` (whatever the launcher's own wrapping, the recovery's result
  word is `refused`, not `undone`); the file left as written; a P1 naming it; the lock held; no new session started.
- **Guards, unchanged behaviour:** the owner's undo and the recovery with nothing foreign still say `undone` and the
  owner's undo exits 0 (S22's existing cases cover this; add one each only if they do not).
- Map the cases to **S22** and **F15**; say for each what it expects and whether it is red today (the review saw the
  owner's undo exit 0 with `undone`). Update the README: the interface line for the undo step's and the recovery's
  result (`refused` and non-zero when anything is left), and a note N-10 for DEC-1107.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-148-f21-tests`, branch `w2/W2-148-f21-tests`, made from
  `w2/integrate` at `b134a760b`. You write only `tests/acceptance/W2-148/`.
- **Your record:** your whole return is your session's **final message**, in full: the launcher keeps it in this
  worktree's `.gov-runtime/scratch/lead/log/W2-148-designer-r3.json`.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** it is now on `w2/integrate` in
  `governance/project/operator/` and in your own worktree: **never open, grep or list that folder** (nor the engineer's
  worktree, base name `W2-148-f21`, nor `W2-148`, nor their branches), never `git show`/`git log -p`/`git diff` on it.
  Run its code only through your cases, and read only their results. You work from the ticket, the package, DEC-1106,
  DEC-1107 and your own cases.
- **The exclusion line (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=operator`, every
  Grep or Glob call that could reach it carries `!governance/project/operator/**`, find carries
  `-path '*/governance/project/operator' -prune`; keep searches inside your own worktree. If a search shows you a line
  of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1));** two searches in all.
- **Planted folders only;** never the real `~/gov-os-operator/`, `~/.claude/`, crontab, live hook, settings or git
  hooks; no real `claude`; no GPU, model, network or installs. **The hidden-half rule:** never open anything under
  `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-f21-tests/src` and a scratch HOME (link `.local/lib` to the user
  site so pytest is found), and run `python3 -m gov.cli.main accept W2-148 --root
  /home/usain/gov-os-worktrees/W2-148-f21-tests`: the code is present on this branch, so the 166 earlier cases should
  pass and your new F21 cases should be red for the right reason.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Commit** on `w2/W2-148-f21-tests`, only `tests/acceptance/W2-148/`, with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1107" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished; waits and stops by pid only. Keep it tiny: 2 to 4 cases.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), the new cases (node id, KPI line,
what each expects, red or green today and why), the README's changed interface lines quoted in full, the commit,
`gov accept`'s counts, `TESTS-READY` text, and anything ambiguous as `discoveries`.
