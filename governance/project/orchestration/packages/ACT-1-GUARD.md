# ACT-1-GUARD: switch on the five-rule guard (DEC-953 item 2, DEC-954 Q8 a)

For the owner's operator, in the main tree. It needs no re-pin and no plain terminal: the owner's operator runs it, at a moment when no one is committing in the main tree (the orchestrator holds its own commits until you say it is done).

## What it does
- **The pre-tool hook** stops running the kernel's full guard (`template/governance/kernel/hooks/pretooluse.py`) and runs this repository's five-rule hook (`.claude/hooks/pretooluse.py`, committed `f7533c61` and `a4e52779`). The five rules:
  1. the implementer never writes acceptance tests;
  2. no reads of the hidden half of an evaluation set (from any worktree, run clone or origin) or of the held-out material;
  3. no reads of secrets;
  4. no installs without the owner;
  5. independent reviewers and auditors write only their own review and audit records.
- **The containment hooks** after each command (`PostToolUse`, `PostToolUseFailure`) are removed.
- **Unchanged:** every permission and deny rule (6 in force, 6 generated, none lost or added), and the PreCompact, SessionStart, Stop and SubagentStop hooks.
- **Nothing is deleted from the product:** the kernel's guard stays built and tested in `template/` and `src/gov/guard/`.

## Checked on a trial clone (`/tmp/gov-os-act1/repo`, the integration head plus this change)
- The regeneration reported deny rules in force 6, generated 6, lost 0, added 0; one generated file changed.
- `settings.json` by structure: `$schema` the same; `permissions` the same; PreToolUse changed (it runs `.claude/hooks/pretooluse.py`, and no longer names the kernel guard); PostToolUse and PostToolUseFailure removed; the rest the same.
- The registered hook line itself, run as Claude Code runs it: **35 of 35 planted cases pass**.
  - Each rule refuses: an engineer's Write and redirect into `tests/acceptance/`; the measured role reading the hidden half here, in another worktree, in a run clone and in the main tree; held-out; `.env`; an SSH key; an engineer's install; sudo; an auditor editing code, a test, a ticket, the register or a lead's handover, or running an unreadable command.
  - Each allowed form passes: the test designer writing tests; an auditor writing its probe or audit record or `/tmp`; heredocs; `$VAR` targets; backticks; inline Python with braces; `rm`; an engineer reading acceptance tests; CronCreate; a general-purpose helper writing.
- The hook takes about 0.2 s a call (one call of 3.9 s at load 34).
- **Tests that read the live hook wiring:** see "Tests" below.

## The commands (the operator, in the main tree)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short
git apply governance/project/orchestration/packages/ACT-1-GUARD.hooks.patch
python3 docs/plan/wave-1-exit/apply_adapter_output.py --dry-run
python3 docs/plan/wave-1-exit/apply_adapter_output.py
python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS
git add .rulesync/hooks.jsonc .claude/settings.json
git commit -m "ACT-1-GUARD: the five-rule guard switched on (DEC-953 item 2, DEC-954)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-953, DEC-954" --trailer "Role: owner"
```
- Before `git apply`, `git status --short` must show no change to `.rulesync/` or `.claude/`.
- The dry run must say `deny rules: in force 6, generated 6, lost 0, added 0` and `changed 1`.
- `guard4_check.py` must end with `PASS`.
- Stop at the first line that differs, and tell the orchestrator.

## Who it reaches, and when
- **New sessions in the main tree:** at once, after the commit.
- **Worktrees:** each takes it when its branch merges `w2/integrate` (new worktrees cut from it have it). The orchestrator merges `w2/integrate` into each kept worktree before its next lead.
- **Running sessions** (the orchestrator's own, and leads W2-76, W2-87, W2-85) keep the old guard until they end: Claude Code reads the hooks at a session's start.

## Undo
`git revert <the ACT's commit>`, run by the operator. It restores the full guard for new sessions.

## Tests: 235 cases go red, all of them tests of this repository's live guard wiring
- **How it was measured:**
  - every test folder that reads the hook wiring (30 folders) was run on the trial clone with ACT 1 applied;
  - each red was then re-run one at a time, both with ACT 1 and on the base;
  - only the reds that fail with ACT 1 and pass on the base are counted;
  - two collection errors in W1-35 came from load: W1-35 passes on both sides.
- **The 235, in 19 files of eight suites:**
  - W1-46: 142, the live guard's refusals (installs, links, `cp` and `mv` targets, role settings, the research role, scratch);
  - W1-05: 77, live hooks and role subagents;
  - W2-59: 5 and W2-65: 1, the hook lines;
  - W1-47: 4 and W1-49: 2, the containment hooks registered;
  - W1-28: 2 and W1-50: 2, the launcher and freeze through the live settings.

  They assert that this repository runs the kernel's full guard and its containment hooks: exactly what DEC-953 item 2 lifts. The product's own guard tests (on the template and `src/gov/guard/`) stay green. Full list: `/tmp/gov-os-act1/confirmed.json`; the script is `tools/act1_confirm.py`.
- **Your named decision asked for (DEC-906): (a) recommended.** A fresh independent test designer revises the 235 cases so they judge the kernel's wiring (the template and a generated fixture repository), not this repository's live settings, lowering no expectation on the product, with `Rewrite-Reason: DEC-953 item 2`. It is a new LITE ticket, W2-90, the first lead after ACT 1. Until it lands:
  - the nightly shows these 235 as known reds, named in the morning package;
  - closes test on the head pinned before ACT 1 (`.gov-runtime/scratch/orchestrator/CLOSE-HEAD`), which already holds every merge they close.
  - (b) would instead revise the tests first and switch afterwards, holding ACT 1 back by one test-designer run, about 2–3 hours.
- **What else ran:** the hook's 35 planted cases through the registered line (PASS). No permission rule changes, so no other test reads a difference.

## After the commit (DEC-955)
The orchestrator writes the handover (the checkpoint and RESUME HERE), tells you it is ready, and stops. The fresh session starts under the five-rule guard; it files W2-90 first, then runs the ten built tickets and the streams. The four-ticket close batch (W2-57, W2-77, W2-03, W2-26) is running on a clone of the head before ACT 1 and is not affected.
