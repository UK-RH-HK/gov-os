# Brief: product-spec worker (repair), W2-11 (DAEO-k7hz) round 2, STANDARD, a kernel change under the CIT-P (CAP-33)

Hand-written by the ticket lead (`gov context DAEO-k7hz --role product-spec` refused: `BLOCKED: mandatory input 'DEC-1083' not found in the store`). A fresh session after a red: you get the failing output only.

## Step 0: the sandbox check, before any work (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed: stop and return.

## Who and where
- Role `product-spec`, ticket `DAEO-k7hz`. Check `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11`, `w2/W2-11`). Different: stop and say so.
- **Policy 2 (c) (DEC-820 (c)):** never read `tests/acceptance/W2-11/`; every Grep or Glob call that could reach `tests/acceptance/W2-11/` excludes it (`!tests/acceptance/W2-11/**`), and so does every recursive Bash search (`grep -r --exclude-dir`, `rg -g '!…'`, `find … -prune`); if a search shows you a line from there anyway, stop reading it and say so in your return. You may run `gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11` and read only its pass/fail per line and counts. **(d):** never read the hidden half of any evaluation set by which you are measured.

## The red (the acceptance run's failing output, all of it you get)
The ticket's line success-16 (read it in full in `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`: "... one scenario each for day, night and a chained command [DEC-991, DEC-994 item 3]") fails two cases:
```
AssertionError: the orchestration skill has no approvals scenario for day
AssertionError: the orchestration skill has no approvals scenario for night
```
The chained-command scenario passes. The approvals section is in `template/governance/kernel/skills/orchestration/briefs-and-returns.md` ("## Approvals: the orchestrator's own allow list"), with three numbered scenarios after "One scenario each, run on a fresh session before the section is promoted:". Make the day and night scenarios read plainly as scenarios of the approvals section, as the ticket's line asks, keeping their content and decisions. Change nothing else.

## Do
- Edit that section in the kernel source and its two copies, keeping all three byte-identical: `template/governance/kernel/skills/orchestration/briefs-and-returns.md`, `.rulesync/skills/orchestration/briefs-and-returns.md`, `template/.rulesync/skills/orchestration/briefs-and-returns.md` (`cmp` them after).
- The orchestration skill's version is already raised this round (1.4.0, not yet released): leave it.
- `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py /home/usain/gov-os-worktrees/W2-11/template/governance/kernel/skills/orchestration/SKILL.md` must still say `OK` (you do not touch `SKILL.md`).
- Then run `gov accept` once (command below) and report success-16's line.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env). So: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11`.
- **Memory (DEC-836):** use `gov retrieve` first if you need to know anything beyond this brief: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.cli.main retrieve "<question>" --json`; **search again once** (DEC-1092 (1)) in your own, different words if a bundle does not answer, then answer from both or say "not found"; two searches in all; never one giant query (batches, DEC-860); small code-graph queries (DEC-859).
- **Guard read refusals (DEC-849):** take a refusal, never another spelling; count them in your return.
- Never write `.claude/**`, a `brief-*.md`, a role template, `src/`, `tests/`, `.tickets/` or the register.

## Commit
`git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Implements: CAP-33, DEC-991, DEC-994" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <the three paths>`. Check `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` first; never `--no-verify`; no amend, rebase, reset, push or merge.

## Rules
- Machine (DEC-898): your share 1 GB and 10,000 files and folders outside the tracked tree; no tree copies (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`); give `du -sh` / `du -s --inodes` of anything you made. (Inside your sandbox `/tmp/gov-os-lead-W2-11` may not be writable; then use the sandbox's own temp and say so.)
- Row W2-L423's rule (DEC-911): under `.gov-runtime/` commit hashes as 12 digits, never 40, and never the keywords of the secrets rule that takes a bare 40-hex string.
- Protected material (DEC-820): never read the held-out material's contents; never print a secret; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- Command forms: one simple command per Bash call; literal paths; no here-documents, backticks, `bash -c`, long inline `python3 -c` with braces. Never `pgrep`, `pkill`, `killall` or the Monitor tool.
- Never ask or notify the owner; install nothing; one role per ticket (DEC-995, DEC-996).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). Never work around a refusal: report it.
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"): stop, return status `AUTH_REQUIRED`.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line, any payload after them; refused twice for the same call, stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
After the twelve fields: the sandbox check's result; the `body_tokens.py` line; whether you used `gov retrieve`; `guard_refusals:` lines or `none`; `brief_gaps:` lines or `none`.
