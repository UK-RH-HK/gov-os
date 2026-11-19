# What every ticket lead's brief shares (Emergency 2; revised by the CTO 2026-11-18)

Written by the CTO for the ticket leads of the build list (EMERGENCY-2 §6.1, §6.2). Your own brief names your feature.

## Where you work
- Your own worktree and branch: `git -C /home/usain/Dynamic-Agentic-Engineering-OS worktree add -b e2/<name> /home/usain/gov-os-worktrees/E2-<name> w2/integrate` (or the existing ticket worktree your brief names: bring it up to date with `git merge w2/integrate` first). Work and commit only there.
- **Never commit to `w2/integrate`** and never touch the main tree `/home/usain/Dynamic-Agentic-Engineering-OS`: the CTO works there and lands your branch.
- Never `git push`, never `sudo`. Full permission otherwise in your worktree, its `-tests` worktree and `~/gov-os-runs/`.
- **The machine rule.** Every test run goes through the machine-wide heavy slot (two slots today), one run at a time:
  `TMPDIR=$(mktemp -d) PYTHONPATH=<worktree>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -n auto`
  - Add `-n auto` to a pytest run of more than one file (the CTO, 2026-11-19: without it the run is one process; the slot caps `-n auto` at its workers, three today). Never `-n` with a number. `PYTHONPATH` absolute (tests start `gov` in subprocesses). The slot waits while taken; never bypass it.
  - The slot also waits until the machine's 1-minute load is under 12, so the load stays inside the resource gate of 20 (the owner, 2026-11-18). A wait is the rule working: let it wait. Never run pytest outside the slot, and never with a number after `-n`.
  - The smallest set that proves your change; no full suites (the CTO runs those); no rebuild and no memory measure without asking the CTO.
  - Before starting a worker: `uptime` and `free -g`; over load 30 or under 3 GB available, wait.

## Read first
`docs/emergency-2/EMERGENCY-2.md` §3, §4, §5 and the rows of §6 your brief names; your ticket file(s) in `.tickets/`; the audit tables your brief names under `docs/emergency-2/audits/`.

## Memory first (§5.4)
Before grepping for a concept: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"`; read the whole bundle, search once more in your own words. Tell your workers the same in their briefs.

## The flow (§4.3); no review (§3.6)
1. **Spec and KPIs.** From the ticket. Where EMERGENCY-2 changes what the ticket must do, rewrite its KPI lines in your branch's ticket file (each line observable, each with its verify); the CTO approves them by this brief. A ticket that is deferred becomes `in_progress` in your branch.
2. **Independent test designer.** Launch one subagent (Agent tool, `subagent_type: independent-test-designer`, no `model`: helpers run Sonnet, the owner's rule of 2026-11-18, enforced by a hook) with the ticket, its KPI lines, the interface (where it lives, command names, error names, signatures) and this brief's rules. It writes the acceptance tests under `tests/acceptance/<W2>/`, red on the base, maps each KPI line to its tests (the README form other ticket folders use, so `gov accept` reads it), sets the ticket's `acceptance_tests.path`, and commits with `Role: independent-test-designer`. It does not read implementation written after the base.
3. **Engineer.** Then one subagent (`subagent_type: engineer`, no `model`: Sonnet) builds until `gov accept <W2> --root <your worktree>` is green (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main accept ...` runs your branch's code). It never edits `tests/acceptance/`; it adds unit tests where useful; commits with `Role: engineer`. If a test is wrong, the engineer says so and you send it back to the test designer, never edit it yourself.
4. **Green.** You run `gov accept`, the unit and acceptance tests of every package your change touches, and `tests/unit/optin`. A red that is the change's: back to the engineer. A red that is not (it is red on `w2/integrate` too): note it, don't fix it.
5. **Return** to the CTO (your final message): branch and head; what is built against each KPI line; the green evidence (summary lines); reds not yours; anything that needs the owner, as one line with options. Short.

## Rules that stay
- Kernel and instruction text (templates, skills, role files) changes when your brief says so: the CTO approved it by naming it (§3.5).
- A known bug you meet in a feature outside your brief: note it in your return; don't fix it.
- **Installs (the owner, DEC-1214 G7):** you install nothing outside your worktree's own venv or folders. A tool the work needs: name it in your return or message the CTO (the tool, the version, why, its size); the CTO approves and records it in `governance/project/tool-registry.yaml`, or refuses. `sudo` is the owner's.
- Commit trailers, one final paragraph:
```
Class: F
Task: <ticket id, e.g. DAEO-7jln>
Role: <orchestrator | independent-test-designer | engineer>
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## Models (the owner, 2026-11-18, audit 09 decisions 2 and 3)
Every session runs the model and effort the rubric gives its role; none chooses its own. Leads and every helper run
Sonnet; a spawn naming another model is refused by `.claude/hooks/agent_model.py`. An exception goes to the owner as one
line through the CTO. Watch the quality: if Sonnet's work drops for a role, say so in your return.
