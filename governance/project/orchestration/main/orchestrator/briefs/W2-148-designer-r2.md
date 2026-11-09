# W2-148 — the independent test designer's brief, round 2: F15's rule and the freeze's place (DAEO-xafn)

You are the independent test designer for **W2-148** (`.tickets/DAEO-xafn.md`): the operator agent (the owner's
DEC-1104 (2), `governance/project/orchestration/packages/OPERATOR-AGENT-1.md`). Round 1 of your work wrote
`tests/acceptance/W2-148/` (157 cases, commit `49eb5d66d` on `w2/W2-148-tests`); read your own README and support
module first. The engineer has since built to it; an independent review then found one defect that blocks, and the
owner decided it: **DEC-1106** (recorded on `w2/integrate` after your branch was made; its text is in your worktree at `.gov-runtime/scratch/ref/DEC-1106.md`: read it in full). Your job is to add the
cases for its items (1) and (3), **before** the engineer's exception round.

## What the owner decided (DEC-1106), as you test it
- **(1) F15, the restore rule.** After the G8 dry run the agent re-hashes the live touched files and the §3 control
  files. Until now the design restored *every* live difference to its pre-dry-run bytes, which cannot tell the dry
  run's change from someone else's (a CTO commit or merge landing in the live tree during the dry run would be
  reverted, and files it created deleted; a guard tightening merged in that window would silently stop applying). The
  rule now: **the agent restores only its own dry-run change: a touched file whose live bytes equal the frozen
  `after/` copy. For anything else it writes nothing, refuses, holds the lock and sends the owner a P1 naming each
  file.** **The same rule in the (a) after-check's undo** (S15): after an (a) apply, a live difference that is not the
  ACT's own (a control file the ACT does not list, or a touched file whose bytes are neither the ACT's after-copy nor
  its before-copy) is left exactly as it is: refused, lock held, a P1 naming each such file; the ACT's own touched
  files are undone as before.
- **(3) The commit freeze is a file in the operator agent's install folder** (`<operator root>/install/`, the default
  of the freeze setting), no longer in the operator root's or the scratch's `log/`. It must exist during the apply and
  be gone after; `install/APPROVED`'s check must not count it (a freeze present during a run never makes the APPROVED
  check fail, and a stale one never makes a later run refuse on APPROVED; it holds G9 instead). G9 still also holds on
  the CTO's `<scratch>/log/act-in-progress.txt`.
- **(4) F7 kept:** the session's allowed forms stay as they are (your S19 cases unchanged).

## What the cases must show
- **The dry run, F15:** a planted ACT whose dry run is clean, with a **planted concurrent commit in the live repository
  during G8** (after the dry run's apply in the clone, before the live re-hash): one case where it changes a control
  file (the path map: a new hidden glob), one where it creates a new file under `.claude/skills/`, one where it changes
  a touched file to bytes that are neither its before- nor its after-copy. Each: the concurrent change left untouched
  (bytes equal to what the commit wrote; the new file still present; `git status` of the live tree clean against its
  new HEAD), the run refused with nothing applied, the lock held (the next queued ACT not run), and a P1 notice whose
  text names each such file.
- **The dry run, the agent's own change:** a planted script that writes the live tree during the dry run despite the
  path rule (simulated the same way, the live bytes made equal to the frozen after-copy): that file restored to its
  before bytes, refused, P1 says live files changed.
- **The (a) undo, F15:** an (a) ACT applied live, with a planted concurrent change to a control file it does not list
  (during the apply's checks): the ACT's own files undone, the concurrent change left exactly as written, lock held, a
  P1 naming the file. **Revise** the round-1 S15 cases that expect an unlisted control file to be "restored byte for
  byte" (README: "the control file is restored byte for byte too") to the new rule: left as is, lock held, P1 naming
  it, the ACT's own touched files undone; those commits carry `--trailer "Rewrite-Reason: DEC-1106 (1)"`.
- **The freeze, (3):** during the apply the freeze file exists in `<operator root>/install/`, not in either `log/`;
  after the run it is gone; a stale freeze left in `install/` holds G9 and does not make the APPROVED check refuse;
  revise the cases that accept the freeze "in either log" (N-4) to the install folder (Rewrite-Reason: DEC-1106 (3)).
- **How to make "during G8" and "during the apply's checks" deterministic:** extend the test hook. State in the README
  new points of `GOV_OPERATOR_TEST_HOOK` (for example `in-G8`, run after the dry run's steps and before the live
  re-hash, and `in-apply-checks`, run after the live apply's checks and before the after-check), run as
  `<exe> <point> <frozen folder>` like the existing ones, with cwd and environment the hook needs to commit to the
  planted live repository. The engineer builds to what the README states. No timing-based race.
- Map the new cases to **S12** (the dry run), **S15** (the (a) undo) and **S14** (the freeze), and to the failure
  lines they guard (a control file changed by an (a) ACT left in place; any live change made by the operator that is
  not its own). Say for each whether it is red against the current design for the right reason; you cannot run them
  against the engineer's code (you never read it), so say what each expects.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-148-tests`, branch `w2/W2-148-tests` (your round 1 commit at its
  head). You write only `tests/acceptance/W2-148/`; update the README (the interface: the freeze's place and the
  APPROVED exception, the new hook points, the restore rule; the map; a note N-9 for DEC-1106).
- **Your record:** your whole return (the twelve fields below) is your session's **final message**, in full: the
  launcher keeps it in this worktree's `.gov-runtime/scratch/lead/log/W2-148-designer-r2.json`.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** never open the engineer's worktree (base name
  `W2-148`, under the worktrees folder) or the branch `w2/W2-148` (no `git show`, `git diff` or `git log -p` on it),
  and never read `governance/project/operator/` on any branch. You work from the ticket, the package, DEC-1106 and your
  own cases.
- **The exclusion line (DEC-1093 (2)), by base name:** keep every Grep, Glob and recursive Bash search inside your own
  worktree. If a search must start above it, it carries `--exclude-dir=W2-148` for grep, `!**/W2-148/**` for Grep and
  Glob, `-path '*/W2-148' -prune` for find. If a search shows you a line of the implementation anyway, stop reading it
  and say so in your return.
- **Search again once (DEC-1092 (1)):** two searches in all, then answer with path and lines or "not found".
- **Planted folders only;** never the real `~/gov-os-operator/`, `~/.claude/`, crontab, live hook, settings or git
  hooks; no real `claude`; no GPU, model, network or installs. **The hidden-half rule:** never open anything under
  `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-tests/src`, and run
  `python3 -m gov.cli.main accept W2-148 --root /home/usain/gov-os-worktrees/W2-148-tests` to show the runner reads
  your map (all red here: no code on this branch).
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Commit** on `w2/W2-148-tests`, only `tests/acceptance/W2-148/`, with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1106" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`;
  new cases and revisions in separate commits, the revisions with their `Rewrite-Reason`.
- Before you end, every run you started has finished; waits and stops by pid only. Keep it small: about 8 to 12 new
  cases plus the revisions.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the new and revised cases
(node id, KPI line, what each expects), the README's changed interface lines quoted in full (the CTO hands them to the
engineer), the commits, `gov accept`'s counts, `TESTS-READY` text, and anything ambiguous as `discoveries` with your
recommendation and confidence.
