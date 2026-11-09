# Brief: engineer (run 2)

You are a fresh engineer. Ticket: DAEO-r30l (W2-20, "Machine-wide resource gate"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-20` on branch `w2/W2-20`. The ticket's code exists from an earlier round; two decided changes remain, and you make them until the failing acceptance cases below pass.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-r30l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-20` and `w2/W2-20`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- **Commit before you run any long suite.** The suites named below take under a minute each; run nothing broader.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Read nothing under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. (This ticket needs no dev tier.)
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never write the real `~/.gov-os/`.** Anything you run by hand that touches the registry runs with a temporary `HOME`; builder tests do the same, and never depend on this machine's real memory, load or sessions.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. On ESCALATION_BLOCKED from any command, stop and return it.
- The git hooks are uninstalled until W2-08. Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return a package. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-r30l.md` (read-only): its KPI lines, its `allowed_paths` and its closing paragraph on DEC-747.
- The acceptance tests and their README (read-only): `tests/acceptance/W2-20/` (the public interface you build, including the start check's heavy start and the sessions condition), and `tests/acceptance/W1-26/test_w1_26_recorded_commands.py`.
- In `docs/DECISION_REGISTER.md`: DEC-742 (the gate's values), DEC-135, DEC-182, DEC-476, DEC-729, DEC-732.
- The ticket's code from the earlier round: `src/gov/resources/`, `src/gov/launch/gate.py`, `tests/unit/resources/`, and `src/gov/check/commands.py`.

## The two decided changes (DEC-747, delegated by the orchestrator on 2026-10-17; staged, not yet in this worktree's register)

1. **P-A.** `src/gov/check/commands.py` is in this ticket's `allowed_paths` **for the one line that records `resources` in `RECORDED_GOV_COMMANDS`. Nothing else in that file changes.**
2. **P-B, a reading of DEC-742.** "At most 8" holds after the start: the start check opens only when the weighted count of live sessions plus the new session's own weight (2 when heavy) is at most 8; the reading shows the gate shut when the weighted count is already 8. Not "< 8 everywhere" (a heavy start could then reach 9). The maximum stays configuration in its one place with DEC-742's default; keep the comparison in one place.

DEC-742's values (at least 4 GiB available, 1-minute load below `nproc`, heavy counting double, at most 8) are decided: where the code's comments or docstrings call them proposed or pending P-W2-9, say DEC-742 instead. The load value stands (DEC-747 item 3): change nothing about it.

## The failing output (run at `70e40474`)

    tests/acceptance/W2-20: 2 failed, 23 passed
    test_DEC_747_at_most_8_holds_after_the_start[7, a heavy start is refused]
      AssertionError: the refusal is not the named error RESOURCE_GATE_SHUT: {'code': 'RESOURCE_REGISTER_INVALID', 'message': '--ticket, --session-role and --heavy go with --register', 'details': {}}
    test_DEC_747_at_most_8_holds_after_the_start[8, the reading shuts and a light start is refused]
      AssertionError: 8 of 8 leaves no room and must read shut: {... 'weighted_sessions': 8, ... 'thresholds': {..., 'max_weighted_sessions': 8}, 'gate': {'open': True, 'reasons': []}}

    tests/acceptance/W1-26/test_w1_26_recorded_commands.py: 2 failed
    test_a_recorded_command_without_its_module_is_a_finding_that_names_it[resources]   (no finding names resources)
    test_a_skill_may_name_a_recorded_gov_command[resources]
      AssertionError: a skill that names `gov resources` is flagged: [{'code': 'SKILL_UNKNOWN_COMMAND', 'message': "unknown gov command 'resources' in .../SKILL.md"}]

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/resources/**`, `src/gov/launch/gate*`, `tests/unit/resources/**`, and the one line of `src/gov/check/commands.py`. Nothing else: `src/gov/launch/launcher.py`, `src/gov/launch/command.py` and `src/gov/cli/**` belong to other tickets; never write under `src/gov/close/**`, `tests/unit/close/**` or `template/governance/kernel/checks/product-traceability-trailers.yaml` (W2-01's).
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests in `tests/unit/resources/` for the boundary, as regression evidence; update any builder test the decision makes wrong.
- Proportion (DEC-135): the change is small. Never make the gate fail open: every refusal the suite holds must still refuse.
- Commit first (below), then run, each in the foreground to its end (never `-x`):
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/acceptance/W2-20 tests/acceptance/W1-26/test_w1_26_recorded_commands.py tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-32/test_w1_32_command_set.py -q -p no:cacheprovider -rs`
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/unit/resources tests/unit/check -q -p no:cacheprovider` (if `tests/unit/check` does not exist, leave it out).
  If one fails, fix it within your paths and make one more commit, with the same trailers. Afterwards check that `~/.gov-os/` was not created or changed by your runs.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476), after checking the hooks folder as above:

    git commit -m "W2-20 (DAEO-r30l): resources recorded; the start check counts the new session (DEC-747)" --trailer "Task: DAEO-r30l" --trailer "Role: engineer" --trailer "Implements: DEC-729" --trailer "Implements: DEC-742" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your commit hashes; the files changed; the tests you ran with their counts; the lines added and removed; the interface as built (the start check's options, how the sessions comparison reads for the reading and for a light and a heavy start, the reason's reading and threshold); the `gov.__file__` line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
