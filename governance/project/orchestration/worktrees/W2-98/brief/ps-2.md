You are a fresh product-spec worker. Ticket: DAEO-wi46 (W2-98, "The spec-writing skill for product-spec"), profile STANDARD, run 3 (build), fix batch 2. You work only in the ticket's worktree `/home/usain/gov-os-worktrees/W2-98` (branch `w2/W2-98`, head 61b4de632827); you are its one writer while you run.

Your budget: about 30 minutes. A small fix to one script and its two byte copies.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wi46','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.
Then: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec`, `DAEO-wi46`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-98`, `w2/W2-98`). If anything differs, stop and say so.

## The failing output (the lead's hand check of `template/governance/kernel/skills/spec-writing/check_spec.py`)
A planted spec, otherwise clean (it passes with K1 on one line), whose KPIs section is:
```
- K1: A member sees it when
  send_welcome runs.
  Fails if: no.
```
gave:
```
--- wrapped.md: exit 0
PASS
```
Expected: exit 1 and `REFUSED KPIs: K1 names code (snake_case identifier "send_welcome")`. A KPI's behaviour that wraps onto indented continuation lines (before its `Fails if:` line, the next KPI or the next section) is part of that KPI and must be judged for code like its first line (ticket KPI failure-1: "A KPI that names code ... passed by the skill's check").

Also, in the same change: judge the KPI's `Fails if:` text (and its continuation lines) for code too, refusing with `REFUSED KPIs: K<n> names code in its Fails if: line (<kind>)`; the failure line is part of the KPI and must also be testable without naming code (DEC-959 item 8). Keep the `REFUSED KPIs: K<n> ...` start (the part `KPIs` and the KPI id in the reason) and every other output word as it is; a clean KPI is never named. State the continuation and Fails-if rule in one line in `spec-form.md`'s "What names code" (or KPI) part.

## What you read and may not read
- The ticket file `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-wi46.md` (its `## Interface` I1-I4 binds the words and exits) and the skill folder `template/governance/kernel/skills/spec-writing/`.
- **You never read the acceptance tests** (`tests/acceptance/W2-98/`, DEC-820 (c)). You may run them and read their pass/fail output.
- Search with the Read and Grep tools only (no `gov retrieve`, no `gov context`). Never open the evaluation sets' root or any hidden or memory-verdict folder.

## Write only
`template/governance/kernel/skills/spec-writing/check_spec.py` and `spec-form.md`, then copy both with `cp` to `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/` (byte copies; never edit a copy by hand). Never write `.claude/`. Keep check_spec.py standard library only and about its present size.

## Check your work (every pytest through the heavy slot)
- Planted specs for your own checks go in `/tmp/gov-os-lead-W2-98/ps2/` (make it with `mkdir -p`; the guard refused writes to `.gov-runtime/scratch/ps/` last batch). Write a script there with the Write tool and run it: the wrapped case above refused naming K1; the same KPI on one line still refused; a clean wrapped KPI of plain prose passes; a `Fails if:` line naming `account.create` refused naming the KPI; a clean spec passes. Remove the folder before you return.
- `cd /home/usain/gov-os-worktrees/W2-98 && TMPDIR=/tmp/gov-os-lead-W2-98 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-98 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`. Never `-x`. Expected: 92 passed, 2 failed, the two failures being `test_the_claude_copy_matches_the_kernel_source` and `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill` (no `.claude/skills/spec-writing/` until the CTO's copies ACT). Remove any `pytest-of-*` folder pytest leaves in the worktree root, by its exact path.
- `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src python3 -m gov.check.skill_validator template/governance/kernel/skills/spec-writing/SKILL.md` exits 0; `diff -r` of each `.rulesync` copy against the kernel folder is empty.

## Commands the guard can read (DEC-941 item 4a)
No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; write files with the Write and Edit tools and absolute paths. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so** (DEC-1142 (9)). A resource gate's refusal is a wait (DEC-1146). On an authentication error, return `AUTH_REQUIRED`.

## Commit
- Check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one is there, stop. Never `--no-verify`. No amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-wi46" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-957, DEC-616, DEC-645, DEC-1083, DEC-1084, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- template/governance/kernel/skills/spec-writing .rulesync/skills/spec-writing template/.rulesync/skills/spec-writing`

## Never
Never write `.claude/`, `tests/`, `src/`, `docs/`, a ticket file, the register or a plan file; never run `gov close`, `gov adopt`, `gov pause`, `gov accept`; never ask or notify the owner; install nothing.

## Return
One message, your last. The twelve fields first, each a labelled line; then the payload (the change, the hand-check output, the pytest counts and red names, the validator and diff results, the sandbox check).
```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
