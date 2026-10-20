# Brief: reviewer (FULL tickets, read-only)

You are a fresh reviewer. Ticket `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`, at the head `38c8f1bbcdcd805c37b3eaccf8567f2b1b9ed481`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-49o5`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`), and `git rev-parse HEAD` (expect `38c8f1bbcdcd805c37b3eaccf8567f2b1b9ed481`). If anything differs, stop and say so.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A single tool call is cut off at 10 minutes.
- You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier probes use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A probe that needs a repository builds a temporary one in a temporary folder (under `/tmp`, from `mktemp -d`), copying single named files only, never `governance/project/`. The acceptance tests' support module (`tests/acceptance/W2-16/w2_16_support.py`, and W1-39's `w1_39_support.py`) shows how to assemble a template source from `copier.yml` and the files of `template/` one by one; you may import those helpers from a probe script kept in your temporary folder. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write no file of the repository and make no commit. No subagents. Install nothing, no network. No push, merge, rebase or tag of this repository (tags only inside your own temporary repositories, unsigned).
- Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`. Never run `gov release` in this worktree.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md`: its KPI lines and its `allowed_paths` (`src/gov/lock/**`, `src/gov/release/**`, `copier.yml`, `template/framework.lock*`, `tests/unit/lock/**`, `tests/unit/release/**`, `docs/releases/**`, `src/gov/check/commands.py`).
- The sources: CAP-43 and its covers and CAP-02 (CAP-02.a, CAP-02.c) in `docs/contract/contract.yaml` (Contract v4.2); the list rows W2-H029, W2-L002, W2-L014, W2-L227, W2-M174, W2-M175 in `docs/plan/WAVE_2_LIST.md`; their origin in `governance/project/bootstrap.md` lines 1965 to 1980 (name that file only).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-722, DEC-023, DEC-488, DEC-493, DEC-499, DEC-542, DEC-194, DEC-244, DEC-654, DEC-136, DEC-137, DEC-413. Staged, not yet in this register: DEC-752 (this branch carries W2-49's held work), DEC-753 (`gov release` is recorded in the command lists only in a later round; the W1-07, W1-26 and W1-32 cases that find it unrecorded are known).
- The ticket's acceptance tests and README (`tests/acceptance/W2-16/`) and the code at the head to probe: `git diff 846d75e1..38c8f1bbcdcd805c37b3eaccf8567f2b1b9ed481 -- src copier.yml docs/releases tests/unit`.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard or a gate fail open. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. In particular:

- a release built from a dirty tree, or from a commit that is not on `w2/integrate`;
- the same version rebuilt from another commit (including after its record was removed or changed in a later commit, or with the record left uncommitted);
- a file changed, added or removed after the release still accepted, by `copier copy`, by `copier update` or by `gov doctor`;
- a manifest whose own hash, or a file hash in it, is wrong still installed, updated or passed by doctor;
- a project silencing the lock comparison (deleting or editing parts of the lock, the answers file, or the recorded release, alone or together with kernel files), and which of these the unsigned lite design can and cannot catch (CAP-02.c stays in Wave 3);
- a missing lock passing, on any install path (Copier copy or update, a direct copy of `template/`);
- a release installed from a source that holds no release record, or from a ref that is not a release tag, and whether that is a fail-open hole for a product repository;
- a tag or a signature made by the code; any write by `gov release` outside `docs/releases/<version>/`, or a partial record left behind by a refused build;
- `gov doctor` on this repository itself (it must not turn its `framework_lock` part red), and on a project installed before this change.

For each case you check, say what you did and what happened.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity (BLOCKER, HIGH, MEDIUM, LOW), and whether it loses work, lets a role write outside its scope, lets an implementer change acceptance tests, or makes the guard or a gate fail open. Say also what you probed and found sound. Then your judgement: `pass` (no finding that loses work, writes outside scope, changes acceptance tests or fails open in ordinary work) or `fail`. You repair nothing (MR-4). The lead writes the probe record from your return.

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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them: there, the probe record's content, as a YAML block with `probed_commit` (full id), `judgement` (`pass` or `fail`) and `findings` (each with `severity`, `behaviour`, `fail_open` true/false), then the narrative. Refused twice for the same call: stop and say so.
