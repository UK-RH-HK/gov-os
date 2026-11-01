You are a fresh engineer (brief A2). Ticket: DAEO-k7hz (W2-11, "Briefs and the orchestration skill"), profile STANDARD, round 1 of two declared rounds (DEC-916), its resume under DEC-992 (P-W2-11-2). You work only in `/home/usain/gov-os-worktrees/W2-11` (branch `w2/W2-11`), and only on `src/gov/check/skill_validator.py`. Budget: about 45 minutes. Commit before you run any long suite.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-k7hz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11`, `w2/W2-11`); if anything differs, stop and say so.

## What you build (the spec and its KPIs; build to them, never to the tests)
The skill validator (`python3 -m gov.check.skill_validator <files-or-folders...>`, DEC-439, CAP-24.c, CAP-38.b) gains two behaviours:

1. **The ticket's failure KPI: "The skill validator refuses a brief without the twelve-field rule."** A brief template (`template/governance/kernel/templates/brief-*.md`: a file whose record front matter declares `type: brief`) is validated as a brief, not as a skill:
   - it is refused (exit 1, the `{"findings": [...]}` JSON line as today) when its return block lacks the twelve-field rule: any of the twelve labels `task`, `status`, `work_completed`, `files_changed`, `evidence`, `tests`, `discoveries`, `risks`, `lessons`, `proposed_decisions`, `unresolved`, `recommended_next_action` missing. The finding's code and message name the rule (the twelve-field return rule, CAP-37, AR-5) and the labels missing;
   - the kernel's five brief templates as they stand on this branch (`brief-engineer.md`, `brief-lead.md`, `brief-product-spec.md`, `brief-reviewer.md`, `brief-test-designer.md`) are accepted (exit 0, `{"findings": []}`). Read them to see their front matter and their return block. A brief has no skill `description` or skill body budget; do not apply the skill rules (description, body tokens) to it. Decide whether a brief's gov-command references are checked (item 2) and say what you chose.
   - A skill file (`SKILL.md`) is judged exactly as before. Nothing that refuses today is accepted after your change; an unreadable or unparseable file still refuses or reports unmeasured as today (never fail open).
2. **Row W2-L097: "The skill validator checks gov commands against the reserved list, not installed ones" (fix: "The validator checks against the installed gov").** A `gov <command>` reference in a skill's code span or code block is checked against the commands the `gov` CLI actually provides (its registered subcommands, as `gov --help` or the CLI's parser holds them), not against a hand-kept reserved list. A command the CLI does not provide is still a finding (`SKILL_UNKNOWN_COMMAND`); if the provided commands cannot be determined, the validator reports unmeasured (exit 1), never passes. Read `src/gov/check/commands.py`, `src/gov/cli/main.py` and how the CLI registers its commands. Re-check the row's state first (DEC-718): if the validator already checks the installed commands, report it with the commit that fixed it and change nothing for item 2.

Earlier acceptance tests that judge this validator (`tests/acceptance/W1-26/`, which you may read: they are not this ticket's) must stay green; run them. Run the validator on the kernel's skills as the check suite does (`python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/<each>` and on `.claude/skills/`), and report every finding; a skill that names a command the CLI does not provide is reported by name, not fixed by you (skills are not yours in this batch).

Your test-driven development uses your own unit tests (DEC-957). The ticket's paths hold no unit-test path, so keep them uncommitted in your session scratchpad (never under `tests/`), run them there, and name them in your return.

## TESTS-READY and the acceptance tests
An independent test designer is revising some acceptance tests in parallel in its own worktree; you never read them. You do not run the acceptance tests in this batch: after your return the lead merges the designer's work, and a later session runs them once through `gov accept DAEO-k7hz` (results per KPI line only). If `.gov-runtime/scratch/lead/TESTS-READY` names a newer commit than the one it names now, ignore it in this batch.

## Rules
- **Policy 2 (DEC-820):** reads are open except (a) secrets, never printed; (b) the held-out material's contents (its file names may be seen); (c) **you never read `tests/acceptance/W2-11/`** by any tool (you may run them and see their names, results and failure messages; in this batch you do not run them); (d) the hidden half of any evaluation set. Never read or name the qualification oracle; never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. **DEC-849:** until W2-58 lands, the guard may refuse some reads (searches that start at the repository root, `governance/project/` or `.claude/`): take the refusal, never another form, search named folders instead, and count the refusals in your return.
- **Memory (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.cli.main retrieve "<question>" --json` (on `STORE_MISSING`, read the named file directly and report it). Never one giant query or context: a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget (DEC-860). A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- **The code under test (DEC-732), word for word:** In this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env).
- Write only `src/gov/check/skill_validator.py` (and your scratch). Never `tests/**`, `.claude/**`, `.tickets/`, the register, plan files, `governance/project/**`, other `src/` files, or `.gov-runtime/**` outside `.gov-runtime/scratch/**`. If the change needs another file (for example `src/gov/check/commands.py`), stop and return a package naming it.
- Budget (DEC-898): your share is 2 GB and 100,000 files and folders outside the tracked tree (the lead's whole budget is 20 GB and 1,000,000); `TMPDIR=/tmp/gov-os-lead-W2-11` for every suite run unless the sandbox sets its own; pytest's own retention, never `--basetemp`; `-o tmp_path_retention_policy=failed` on suite runs; clean up every temp tree you make; no tree copies (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it); nothing copied under `.gov-runtime/` (DEC-673); measure your scratch (`du -s --inodes`, `du -sh`) and report it. **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, hashes as 12 digits, never the full 40, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Commands the guard can read (DEC-941 item 4a): no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; anything longer goes in a script file in your scratchpad, written with the Write tool. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6). On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.
- Every suite to its end, never `-x`. Never make a guard or gate decision fail open.
- Commit: check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file first (stop if one is there); never `--no-verify`, never `core.hooksPath`; no amend, rebase, reset, push. `git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Implements: DEC-992, DEC-439, CAP-37" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. `Implements:` holds only decision or Contract ids the register and store hold. Never `Role: owner` or `Decided-by:`.
- Never run `gov close`, `gov adopt`, `gov pause` or `docs/plan/tools/validate_s1.py`; never ask or notify the owner (no question box, no ping); install nothing; no sudo; never read the held-out material's contents or print a secret.

## Return
One message, your last: the twelve fields first, each as a labelled line, any payload after (the sandbox check, the diff's summary, W2-L097's state with its evidence, the validator's results on the briefs and skills, your unit tests' counts, W1-26's counts, `gov retrieve` use, guard read refusals, scratch figures).

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

The twelve fields first, any payload after. Refused twice for the same call: stop and say so.
