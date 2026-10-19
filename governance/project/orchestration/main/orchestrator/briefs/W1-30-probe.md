You are a fresh reviewer (brief A3) for ticket `DAEO-2lwj` (`W1-30`, `gov close`, profile FULL), in the worktree `/home/usain/gov-os-worktrees/W1-30` on branch `w1/W1-30`, at commit `6f2130c8`. The ticket is implemented and its acceptance tests pass (204 cases). **You write nothing: no file, no commit, nothing in this tree or anywhere else except your own session's temporary folder.** Check `printenv GOV_ROLE GOV_TICKET` first.

Read the ticket `.tickets/DAEO-2lwj.md` (its KPI lines), `tests/acceptance/W1-30/README.md`, the code under `src/gov/close/`, and in `docs/DECISION_REGISTER.md` the entries DEC-453, DEC-454, DEC-455, DEC-470, DEC-476 and DEC-480.

Probe for behaviour the tests miss, by reading and by trying the command in temporary projects that you build from scratch in your session's temporary folder (never by copying or cloning this tree or a folder of it; never against this worktree or the repository at `/home/usain/Dynamic-Agentic-Engineering-OS`): cases in which `gov close`
- closes a ticket whose work it did not measure, or reports as measured something it did not run (a test run, a check, containment, the context, the probe record, the owner's decision);
- could lose work, or leaves a ticket, a counter or a record half written when it is interrupted or a tool fails;
- lets a role write outside its scope, or lets an implementer's change to acceptance tests or ticket files pass;
- can be made to close by its caller's own input (an argument, an environment variable, a file the caller may write: the counter, the probe record, a decision file);
- treats an error as a pass (fails open).

Never read, print, search or copy the project's held-out file under `governance/project/`, never read or display `.claude/settings.json`, read nothing under `~/gov-os-workbench/` or `qualification-oracle/`, install nothing, no network, no `git checkout`, `git reset` or `git clean`, no `gov rebuild`, no `gov pause`. Run everything in the foreground, one command after another: your session ends with your last message.

Return, as your last message: each finding as a described behaviour (what was done, what happened, what should have happened), with its severity (could lose work / scope / acceptance tests / fails open / lesser) and how you observed it (read in the code at file and line, or reproduced: the commands); then one line saying that you wrote nothing in the repository, and `git status --short` of this worktree as you leave it.
