You are a fresh engineer. Ticket: DAEO-siiz (W2-52, "The lite A7 and A10 stage records"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-52` on branch `w2/W2-52`. You implement the ticket inside its allowed paths until its acceptance tests pass, with the one exception named under "The entry point" below.

**The state of the branch.** An earlier engineer session committed an implementation at `bd9fdfec` ("the lite A7 and A10 gates and their stage records": `src/gov/adopt/lite_gates.py`, the A7 and A10 entries in `stages.py`, the skill's A7 and A10 steps, `tests/unit/adopt/test_lite_gates.py`). That session ran in a sandbox where the acceptance suites could not run (the code graph's daemon folder `/tmp/gov-cbm-1000` was read-only, so every fixture stopped at A3). Your job: read the ticket, the tests and that code, run the acceptance suites as below, and change the code inside the allowed paths until they pass. Judge that code against the tests and the sources yourself; keep it where it is right.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-siiz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-52` and `w2/W2-52`). If anything differs, stop and say so.
- **The code under test (owner's DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. Tests that need a repository build a temporary one from scratch. No clone, copy or file of a programme is put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause` against this worktree (the cases run `gov adopt` in their own temporary projects; that is fine). On ESCALATION_BLOCKED from any command, stop and return it.
- **The git hooks are uninstalled until W2-08.** Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-siiz.md` (read-only): its KPI lines and its `allowed_paths`. The card in `docs/plan/WAVE_2_WBS.md` §2 (W2-52) narrows them: `stages.py` the A7 and A10 entries only; the adopt skill the A7 and A10 steps only.
- The acceptance tests and their README (read-only): `tests/acceptance/W2-52/`. The README's section "The interface the cases hold" is the interface you build to.
- The sources: Contract v4.2's CAP-44.f, CAP-44.h and CAP-44.k in `docs/contract/capabilities/` (read-only; W2-49's files — `docs/contract/**`, `docs/changes/W2-49-*` — are never edited).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-741 (Contract v4.2: the lite A7 and A10 gates), DEC-722, DEC-738 item 1 (the engineer writes the skill's steps), DEC-090, DEC-135 (proportion), DEC-182 and DEC-476 (trailers), DEC-454 and DEC-490 (the A5 auditor's record, the precedent).
- The code it touches: `src/gov/adopt/` (`stages.py`, `project.py`, `command.py` — the last two read-only), and W1-41's acceptance support for how the stages are driven.

## What you write

- Only inside the ticket's allowed paths:
  - `src/gov/adopt/lite_gates.py` (new): the two gates.
  - `src/gov/adopt/stages.py`: **the A7 and A10 entries only** — their entries in the stage table and, if the gates need it, one routing of A7 and A10 in `run()` ahead of the chain read, changing nothing for A0 to A6 and A8. Nothing else in that file.
  - `template/governance/kernel/skills/adopt/SKILL.md` (and nothing else under the adopt skill): **the A7 and A10 steps only** — the steps that say who runs each gate (a fresh Independent Auditor session), what each checks (Contract v4.2's CAP-44.f), that each is recorded as its own stage, what stays for Wave 3 (CAP-44.k), and that a missing A7 or A10 record is a condition `not met` for the verdict. Change the sentences of the "Independent gates (Wave 3)" section only as far as A7 and A10 require; A11 and the full verdict stay Wave 3. Keep W1-36's skill form (at most 2,500 tokens of body).
  - Builder tests in `tests/unit/adopt/test_lite_gates*.py`, as regression evidence only (MR-3).
- **Never** `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the README's interface. **Never make a gate fail open:** a gate never passes when what CAP-44.f says it checks is absent or failing, when the auditor's record is missing, uncommitted, unreadable, partial, for another stage, not the auditor's, or from a session that ran the stages; a missing, unreadable or partial stage record is never read as healthy; a gate's record is written only in the adoption run's own folder, at a path no other stage's record has, and never over another record. A gate never gives a condition `accepted`.

## The entry point (outside your paths: do not touch it)

`gov adopt --lite --stage` takes its choices from `STAGES` in `src/gov/adopt/command.py`, which is **outside** the ticket's allowed paths. The lead returns that to the owner as a package (widen the paths by that one tuple). **You do not edit `src/gov/adopt/command.py` or `src/gov/adopt/project.py`**, and you do not make A7 or A10 depend on any change to `project.py` (A8 must still run after A6 with no A7 record, so A7 and A10 do not join `project.STAGES`' chain). Build the gates so that the **only** further change needed is adding `"A7"` and `"A10"` to `command.py`'s `STAGES` tuple.

To show that, run the acceptance suite against a throwaway stand-in that changes nothing but that tuple at import time — for example a `sitecustomize.py` in a temporary folder of yours (never in this tree, never under `.gov-runtime/`), placed on `PYTHONPATH` ahead of `/home/usain/gov-os-worktrees/W2-52/src` for the suite and for the `gov` children the cases start. Report exactly how you did it and that the stand-in changed only the tuple. Then also run the suite plainly (no stand-in) and report its counts: the A7 and A10 cases still stop at "invalid choice" there, and the skill cases must pass.

## Commit, then run the suites

Commit any change first (before any long suite), with only your paths staged and the trailers in the final block:

    git commit -m "W2-52 (DAEO-siiz): <what the change does>" --trailer "Task: DAEO-siiz" --trailer "Role: engineer" --trailer "Implements: DEC-741" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit, check `git log --oneline -2` and `git status --short`. A fix after a suite is a new commit with the same trailers (never amend).

Run, in the foreground, each suite to its end, never with `-x`, each in its own pytest process:

- with the stand-in: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=<your stand-in folder>:/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/acceptance/W2-52 -q -p no:cacheprovider -rs` (until it passes; the cases rebuild and take 2 to 7 minutes);
- plainly: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/acceptance/W2-52 -q -p no:cacheprovider -rs`;
- W1-36's suite (the skill form): `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/acceptance/W1-36 -q -p no:cacheprovider -rs` (the lead runs W1-41 and the other suites in its verification);
- the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/unit/adopt -q -p no:cacheprovider`.

A foreground command is killed after 10 minutes: give each suite run the Bash tool's longest timeout, and if a run would pass that, split it by test file and say so. Nothing in the background.

## Return

Your final message gives, in the fields below: your commit hashes (or "no change needed") with their trailers; the files changed; each suite you ran with its counts; the lines added and removed; the stand-in and how it was placed; the A7 and A10 records' form, with the path a gate writes; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

Return one message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
