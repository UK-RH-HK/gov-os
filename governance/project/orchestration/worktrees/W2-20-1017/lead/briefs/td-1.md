# Brief: independent test designer

You are a fresh independent test designer (MR-3). Ticket: DAEO-r30l (W2-20, "Machine-wide resource gate"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-20` on branch `w2/W2-20`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-r30l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-20` and `w2/W2-20`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Read nothing under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. (This ticket should need no dev tier.)
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never write the real `~/.gov-os/`.** Every test that touches the machine-wide registry points the home folder at a temporary folder (a temporary `HOME` for the subprocess, or another public means); no test reads or writes the real `~/.gov-os/`, and no test depends on this machine's real memory, load or sessions.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. On ESCALATION_BLOCKED from any command, stop and return it.
- The git hooks are uninstalled until W2-08. Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return a package. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message. Leave no temporary folder of your own behind.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-r30l.md` (read-only): its KPI lines, its `allowed_paths` and its sources.
- The W2-20 card in `docs/plan/WAVE_2_WBS.md` §2, and §0 rule 9 there (the machine-wide resource gate).
- The list rows it takes in: W2-M188, W2-M244, W2-M262, in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-729 (the ticket's source), DEC-096, DEC-135, DEC-136, DEC-182, DEC-221, DEC-413, DEC-462, DEC-476, DEC-491, DEC-498, DEC-511, DEC-718, DEC-732.
- The public interfaces the ticket must work with: the `gov` command line and its command-module convention and envelope (the module docstring of `src/gov/cli/main.py`; `gov <command> --json` prints `{ok, command, result, error?, session}`), run as `python3 -m gov.cli.main ...`; the existing acceptance-suite conventions in `tests/acceptance/conftest.py` and one or two earlier suites' READMEs. You read no private part of an implementation to learn what a test should expect.

## The behaviour to test

Several repositories' Gov OS sessions share one machine. The ticket delivers a read command, `gov resources`, and the machine-wide resource gate it reports, which a session start consults.

1. **The reading.** `gov resources` reads the machine's available memory, its 1-minute load, its processor count, and every live Gov OS session on the machine from a machine-wide registry kept under `~/.gov-os/machine/` (in the home folder of whoever runs it), whichever repository started that session. It reports them (under `--json`, in the envelope's `result`).
2. **The gate opens or shuts with a named reason.** The gate is open only when all of these hold; otherwise it is shut, and each broken condition is named as a reason with its reading and its threshold:
   - at least the configured available memory (proposed default 4 GiB);
   - the 1-minute load below the configured limit (proposed default: the processor count, `nproc`);
   - the weighted count of live Gov OS sessions on the machine within the configured maximum (proposed default 8), where a heavy session counts double.
   The values are **configuration, in one place, with those proposed values as the defaults** (the owner has not yet given them: P-W2-9). Tests set their own thresholds and their own readings by a public, documented means of your choosing, and never depend on this machine's real memory, load or sessions. One test shows the defaults in force when nothing is configured. A reading that cannot be taken never opens the gate (fail closed, with a named reason).
3. **Sessions in the registry.** A session is entered in the machine-wide registry with at least its process id, its repository, its ticket and role, and whether it is heavy. The means of entering one is a public part of this ticket's interface; choose it and state it in the README (for example a `gov resources` subcommand or option, or a documented file format in the registry folder that other repositories' Gov OS also write).
4. **A stale entry is cleared** [W2-M244, W2-M188, W2-M262]: an entry whose process is no longer alive does not count against the gate and is removed from the registry when the registry is read. A live entry is kept.
5. **Failure KPI, another repository:** a session entered from another repository (a second temporary repository) counts against the gate of this one, and is shown in this one's reading.
6. **Failure KPI, a start while the gate is shut is refused with the reading:** the start check (the gate a session start consults before it starts anything) refuses when the gate is shut, with a non-zero exit (or a named error) that carries the reading and the named reasons, and lets the start go ahead when the gate is open. **Scope:** this ticket's paths are `src/gov/resources/**`, `src/gov/launch/gate*` and `tests/unit/resources/**`; the launcher itself (`src/gov/launch/launcher.py`, `src/gov/launch/command.py`) belongs to other tickets (W2-21's KPI is that the launch "passes the resource gate"). So test the refusal at the interface this ticket delivers — the start check exposed by `gov resources` and/or the gate under `src/gov/launch/gate*` — not by running `gov launch` and not by starting a real session. State in the README which interface you chose.

Edge cases worth one test each (STANDARD, no combinatorial expansion): exactly at a threshold (state which side opens); several reasons named at once when several conditions break; a heavy session counting double tipping the count over the maximum.

Process ids: use a child process you start and stop yourself for "live" and "dead"; never rely on the PIDs of real sessions on this machine.

## What you write

- Only inside `tests/acceptance/W2-20/`. No earlier ticket's test is touched unless the KPI lines name it for revision (they name none); if you think one must be, name it and return a package.
- In proportion to STANDARD (DEC-221): every KPI line's success and failure plus the key edge cases above. No combinatorial expansion. Every list row (W2-M188, W2-M244, W2-M262) gets at least one test that names it.
- Behaviour through public interfaces, never internals. Deterministic, no network. Commands run as subprocesses with a temporary `HOME` and temporary repositories built from scratch.
- A README that maps each KPI line and list row to its tests and gives the expected red reason of each, states the public interface the tests define (command, options, exit codes, the registry's location and format if public, how thresholds and readings are set), and says how the suite exercises this worktree's code (DEC-732: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src`, passed through to subprocesses).
- Red first: run the tests with `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/acceptance/W2-20 -q -p no:cacheprovider -rs` to the end (never `-x`); they fail for the reason the README states.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476), after checking the hooks folder as above:

    git commit -m "W2-20 (DAEO-r30l): acceptance tests for the machine-wide resource gate" --trailer "Task: DAEO-r30l" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash; the test count; the KPI lines and list rows with their tests; the red reason as you saw it; the `gov.__file__` line; the public interface you defined; every earlier test you rewrote, with its reason; any package.

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
