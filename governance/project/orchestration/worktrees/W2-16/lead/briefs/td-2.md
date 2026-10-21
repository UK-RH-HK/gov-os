# Brief: independent test designer (a batch after the first review)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`. The ticket's acceptance tests exist (`tests/acceptance/W2-16/`, 75 cases) and an implementation has been committed. A review found behaviour the tests miss; you add the cases that hold it, from the KPI lines and the behaviour described below, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-49o5`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`). If anything differs, stop and say so.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A single tool call is cut off at 10 minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree (inside your own temporary repositories you may do what a case needs).
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch, copying single named files, as the suite's support module already does. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag of this repository. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Nobody tags this repository and nobody signs.** A case that needs a tag makes it in its own temporary repository, unsigned, standing for the owner. Releases are built only in temporary repositories.
- Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md` (read-only): its KPI lines and sources (CAP-43.b, CAP-43, DEC-722, CAP-02.c).
- The suite as it stands: `tests/acceptance/W2-16/README.md`, its support module and its cases. You extend it; you change no existing case's expectation (if you judge one must change, return it as a package).
- CAP-43 and its covers in `docs/contract/contract.yaml`; DEC-722, DEC-136, DEC-221, DEC-491 in `docs/DECISION_REGISTER.md`.
- Public interfaces only: `gov release <version>` and its exit code and output, the release record under `docs/releases/` of the repository the release is built in (as your README already describes it), `git` in temporary repositories. You read no private part of the implementation to learn what a case should expect.

## The behaviour to add (from the review, as described behaviour; DEC-136)

KPI line 3, "A release is immutable: building the same version from another commit ... is refused [CAP-43]", and KPI line 1, "builds a release from a clean `w2/integrate` commit":

1. **The same version is refused wherever the repository already knows it,** not only where its record is in the checked-out tree. Each of these, built in a temporary repository whose `w2/integrate` holds release V's committed record (the owner's step), must refuse `gov release V` with a non-zero exit and write nothing:
   - HEAD is an older commit that `w2/integrate` contains (for example a detached checkout of the commit before the record was committed), so the checked-out tree has no record of V;
   - the record of V was removed in a later commit on `w2/integrate`, and V is built again from a new commit;
   - a tag `vV` already exists (made by the case, standing for the owner), with no record of V in the tree.
   Seen today: the first two build a second record of V naming another commit and exit 0.
2. **A version that differs from a recorded one only by its build metadata** (`V+build.2` beside a recorded `V`; semantic versioning gives them equal precedence) is the same version and is refused. Seen today: accepted, giving two records of one version.
3. **A release is built from the commit, never from bytes the commit does not hold.** Where a tracked file of `template/` has been edited but `git status` shows the tree clean (the file marked `git update-index --assume-unchanged`, or `--skip-worktree`), `gov release` either refuses with a non-zero exit and writes nothing, or writes a manifest whose hash for that file is the sha256 of the file as committed at the release's commit (`git cat-file blob <commit>:template/<path>`). Never a manifest holding the edited bytes' hash. Seen today: exit 0, with the edited bytes' hash.

Keep each case a positive control where it helps: the same set-up without the defect still releases (the suite already has such controls; reuse them).

## What you write

- Only inside `tests/acceptance/W2-16/`: new cases (in a new file, or appended to the release file on lines of your own) and the README's mapping (each new case, its KPI line, its source "first review of W2-16, finding N", its expected red reason). No existing case's expectation changes.
- No combinatorial expansion: one case per bullet above, parameterised where natural.
- Red first: run the new cases, then the whole suite to its end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs`
  The new cases fail for the reason your README states; the 75 earlier cases still pass.
- An ambiguous point is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit: stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "W2-16 (DAEO-49o5): acceptance cases for release immutability found by the first review" --trailer "Task: DAEO-49o5" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-43.b" --trailer "Rewrite-Reason: cases added after implementation, from the first review's findings 1, 4 and 5 (DEC-136)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself: your commit's hash; the new cases with their KPI line and red reason as you saw it; the whole suite's counts; the `gov.__file__` line; any package.

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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
