# Brief: independent test designer (run 2: a decided boundary, and two README counts)

You are a fresh independent test designer (MR-3). Ticket: DAEO-r30l (W2-20, "Machine-wide resource gate"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-20` on branch `w2/W2-20`. The ticket's acceptance tests exist under `tests/acceptance/W2-20/` and an implementer's commit exists, so DEC-491 applies to anything you rewrite. An orchestrator decision now settles a boundary those tests left open on purpose; you add the tests for it, red first.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-r30l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-20` and `w2/W2-20`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists (or with a package and no commit).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Read nothing under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. (This ticket needs no dev tier.)
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. **Never write the real `~/.gov-os/`**: every test keeps the machine-wide registry in a temporary home folder, as the existing suite does, and depends on no real memory, load or session of this machine.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. On ESCALATION_BLOCKED from any command, stop and return it.
- The git hooks are uninstalled until W2-08. Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return a package. Never `--no-verify`, never `core.hooksPath`.
- You read the tests and their README, never the implementation under `src/` (MR-3, DEC-462): the behaviour comes from the decisions below and the README's public interface.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message. Leave no temporary folder of your own behind.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-r30l.md` (read-only): its KPI lines and its closing paragraph on DEC-747.
- `tests/acceptance/W2-20/README.md` (the public interface, and its package P-1 at the end), and the suite's files `test_w2_20_gate.py`, `test_w2_20_failure.py`, `w2_20_support.py`, `conftest.py`.
- In `docs/DECISION_REGISTER.md`: DEC-742 (the gate's values), DEC-136 (described behaviour), DEC-221, DEC-462, DEC-491, DEC-729, DEC-732.
- `tests/acceptance/W1-07/README.md` (section "The four commands of DEC-542") and `tests/acceptance/W1-26/README.md` (section "The four recorded commands in the checks"), with `tests/acceptance/W1-07/w1_07_support.py` and `tests/acceptance/W1-07/test_w1_07_recorded_commands.py`, `tests/acceptance/W1-26/test_w1_26_recorded_commands.py`.

## The decision (DEC-747 item 2, delegated by the orchestrator on 2026-10-17; it is not yet in this worktree's register, so cite it as "DEC-747 (delegated, staged)")

> **P-B, a reading of DEC-742 (stricter than built).** "At most 8" holds after the start: the start check opens only when the weighted count of live sessions plus the new session's own weight (2 when heavy) is at most 8; the reading shows the gate shut when the weighted count is already 8. Not "< 8 everywhere" (a heavy start could then reach 9).

It settles the README's package P-1. DEC-742 itself stands: at least 4 GiB available, the 1-minute load below `nproc`, heavy sessions counting double, at most 8 Gov OS sessions on the machine, as configuration in one place with these as the defaults (they are no longer "proposed" or "pending").

## The behaviour to test (described behaviour, DEC-136)

1. **The start check knows the weight of the session it is asked to start.** A start of a light session adds 1, a start of a heavy one adds 2. It opens on the sessions condition only when (weighted count of live sessions) + (the new session's weight) is at most the configured maximum; otherwise it is refused, as every refused start is, with the reading and a named `sessions` reason. The means by which the start check is told the new session is heavy is part of this ticket's public interface: choose it, consistent with the interface the README already defines for entering a heavy session, and state it in the README. A start check told nothing about weight is a light start.
2. **The reading** (`gov resources` without the start check) shows the gate shut on the sessions condition when the weighted count is already at the maximum (no room for even a light session), and open on it below the maximum.
3. **The boundary, with a maximum of 8** (configured, or the default) and the other conditions holding:
   - weighted count 7, a light start: opens (7 + 1 = 8);
   - weighted count 7, a heavy start: refused with the reading and the `sessions` reason (7 + 2 = 9);
   - weighted count 8: the reading shows the gate shut on `sessions`, and a light start is refused.
   Build the counts from live child processes you start and stop yourself, light and heavy, as the suite already does. One test per bullet, or one parametrised test; STANDARD, no combinatorial expansion. State in the README what `reading` and `threshold` a refused `sessions` reason carries (for the reading and for each kind of start) and make the tests hold it.
4. **The existing tests stay as they are** unless one now contradicts the decision; if one does, revise only the lines that contradict it, with the reason in the README and in `Rewrite-Reason:`. Update the README: the gate's sessions condition, the start-check row of the interface table, the KPI mapping table (the new tests under success 2 and the failure line), the case count, the red run, and P-1 marked decided by DEC-747 (delegated, staged), with the defaults named as DEC-742's (no longer proposed or pending).

## Two README counts (if still wrong)

W2-20 recorded `resources` beside DEC-542's four (commit `173e8e97`). If `tests/acceptance/W1-07/README.md` or `tests/acceptance/W1-26/README.md` still say "four" recorded commands (section titles, the case table rows, the parametrised counts) where the suites now hold five, correct those lines to the count and names the suites hold now (one line each, naming W2-20 and DEC-542's form). Change no test file under W1-07 or W1-26 for this, and no other text.

## What you write

- Only `tests/acceptance/W2-20/**` and those lines of the two READMEs. Nothing under `src/`.
- Red first: run `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/acceptance/W2-20 -q -p no:cacheprovider -rs` to the end (never `-x`). The cases the decision makes stricter than the code as built must fail, for the reason your README states; the rest of the suite stays green. Report the counts and each red reason as you saw it.
- An ambiguity or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

One commit, only your paths, trailers in the final block (DEC-182, DEC-476, DEC-491), after checking the hooks folder as above:

    git commit -m "W2-20 (DAEO-r30l): the sessions boundary of the start check (DEC-747)" --trailer "Task: DAEO-r30l" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Implements: DEC-742" --trailer "Rewrite-Reason: <one line: DEC-747 (delegated) settles P-1, the sessions boundary; README counts follow 173e8e97>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash; the tests added and any revised, with reasons; the interface you chose for a heavy start; the suite's counts and red reasons; the README lines you corrected in W1-07 and W1-26 (or "already right"); the `gov.__file__` line; any package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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
