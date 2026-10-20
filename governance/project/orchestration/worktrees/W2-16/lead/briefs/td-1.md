# Brief: independent test designer

You are a fresh independent test designer (MR-3). Ticket: `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-49o5`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`). If anything differs, stop and say so.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Your tests, run from this worktree with that `PYTHONPATH`, must exercise this worktree's code: every `gov` they run, and every program a Copier task runs, must resolve to `/home/usain/gov-os-worktrees/W2-16/src`. Your README says how the tests ensure it (for example by running `gov` as `sys.executable -m gov.cli.main` with the caller's `PYTHONPATH` passed on), and one case may check it.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests (if any) use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch, copying single named files (W1-39's tests do this for the template source: read `tests/acceptance/W1-39/README.md` and `w1_39_support.py` for a working pattern you may follow in your own files). No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag of this repository. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Nobody tags this repository and nobody signs.** A test that needs a release tag makes it in its own temporary repository, unsigned. Tests build releases in temporary folders and temporary repositories, never in this worktree's `docs/releases/` and never from this repository's real history.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md` (read-only): its KPI lines, its `allowed_paths` and its sources. The card in `docs/plan/WAVE_2_WBS.md` §2 (W2-16), and §0 ("Rules for every ticket").
- The sources: CAP-43 and its covers CAP-43.a to CAP-43.d, and CAP-02 with CAP-02.a and CAP-02.c, in `docs/contract/contract.yaml` (Contract v4.2, in this tree). CAP-43.b lite: the release's own manifest and file hashes, built with the release; pinned and hash-verified, not signed. The KPI also asks for version, schema versions, CLI version and release notes: CAP-43's wave note lets CAP-43.d contents built now be delivered ahead of their wave.
- The list rows the KPIs name, in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`: W2-H029, W2-L002, W2-L014, W2-L227, W2-M174, W2-M175. Their origin lines are in `governance/project/bootstrap.md` (name that file only): lines 1965 to 1980 (the comparison's gaps: silencing, what it does not look at, the lock task), 380 to 384 and 1548 to 1552 (the vendored skills' licence and version).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-722 (Contract v4.2; signed tags stay in Wave 3), DEC-023, DEC-027, DEC-488 (one comparison; never a match unhashed), DEC-493, DEC-499 (a missing lock fails; neither file = unmeasured; the lock task's command), DEC-542 (the recorded commands; `lock` is the module command), DEC-194 and DEC-244 (the vendored skills), DEC-654 (copying `template/` directly writes no lock), DEC-135 and DEC-221 (proportion), DEC-462, DEC-476, DEC-491.
- Two staged owner decisions that apply, not yet in this tree's register (apply them as written here):
  - **DEC-752:** this branch carries W2-49's held work (Contract v4.2). W2-49's files are not this ticket's.
  - **DEC-753 (delegated):** `gov release` is a new `gov` command. It is recorded in the two command lists (W1-07's tests' list and the recorded-commands list in `src/gov/check/commands.py`) only in this ticket's resume round, after W2-20 closes. Until then the W1-07 and W1-26 cases that find `release` unrecorded are named reds. You do not touch W1-07's or W1-26's files in this round.
- The public interfaces the ticket must work with: the `gov` command line (`gov --help`, `gov doctor --json` and its `framework_lock` part); the tool `copier` (`copier copy` and `copier update` with `--trust --vcs-ref <tag>`) on the template source made of `copier.yml` and `template/`; the lock file `governance/framework.lock` of a created project and its answers file `.copier-answers.yml`; the module command `python3 -m gov.lock` (the Copier task today); `git` in temporary repositories. You read no private part of an implementation to learn what a test should expect.
- The earlier acceptance suites that hold the same interfaces, which must stay green: `tests/acceptance/W1-39/` (the template and the lock), `tests/acceptance/W1-27/` (doctor, its `framework_lock` part, "unmeasured" where a project was never installed), `tests/acceptance/W1-07/` (the recorded commands: `gov lock` stays a usage error, `python3 -m gov.lock` is the module command, DEC-542), `tests/acceptance/W1-26/`, `tests/acceptance/W1-32/`. **If a KPI of this ticket cannot be met without revising one of their cases, name the case and the KPI line and return it as a package; you do not edit them in this round.**

## The behaviour to test

Success lines (each, with its failure side):

1. **`gov release <version>` builds a release from a clean `w2/integrate` commit [CAP-43.b lite].** Its manifest holds: the semantic version and the commit (full id); every shipped file with its sha256; the wheel hash, the CLI version and the schema versions; release notes; the manifest's own hash (a reader can recompute it and find it equal). The failure side: no release from a tree with uncommitted or untracked changes, from a commit that is not on `w2/integrate`, or with a version that is not a semantic version; a refused release writes nothing. The ticket's allowed paths put the release record under `docs/releases/` of the repository the release is built in; what your tests assume of the record's layout and format is written in your README, each point with its source, fixing no more than the tests need (as W1-39's README does).
2. **The owner tags the release commit; agents never tag; the tag is not signed** (CAP-02.c stays in Wave 3, DEC-722). Seen from outside: building a release creates no git tag and signs nothing; a release installed from an unsigned tag (made by the test, standing for the owner) is accepted.
3. **A release is immutable [CAP-43]:** building the same version again from another commit is refused, and the existing record is left byte for byte as it was; a file changed after the release (a shipped file whose bytes no longer match the manifest) is refused (see the failure line).
4. **`framework.lock` records the release version and the manifest hash, at copy as well as at update.** A project created by `copier copy` from a release tag, and updated by `copier update` to a later release tag, holds in its lock the version and manifest hash of the release it was installed from. And, from the rows:
   - **A missing lock fails** [W2-L227]: any install path produces `framework.lock`, or `gov doctor` names the missing step (copying `template/` directly runs no Copier task, DEC-654).
   - **A project cannot silence the lock comparison** [W2-H029, the silencing part]: today deleting both the lock and the answers file of an installed project gives "unmeasured" and exit code 0, and editing the lock's manifest together with a kernel file gives a match. Neither may give a pass any more. A project that was never installed from the template (this repository itself, and W1-27's cases) stays as W1-27 holds it, and `gov doctor` stays green on this repository (Wave 2 exit criterion 3).
   - **The comparison covers what it skipped** [W2-M174]: file modes, folders (an added empty folder) and declared non-kernel paths, and `__pycache__/` as the row states. Read the row's "closes when" and its origin line; test what it names.
   - **The lock task** [W2-M175]: the row closes when a `gov` subcommand is used by the Copier task (so the task no longer needs a `python3` on `PATH` that imports `gov`). Constraint: W1-07's case that `gov lock` is a usage error stands (DEC-542), and DEC-753 excuses only `release` as a new command. Test the behaviour the row needs within that constraint; if you judge the row cannot be met without a new top-level `gov` command other than `release`, return it as a package with your recommendation.
5. **The vendored skills carry their licence and version in the release** [W2-L002, W2-L014]: a release holds, for the vendored skills, their upstream licence and their version (today the licence is only in the vendor folder and the version only in `vendored.yaml`; the copies are committed unchanged, DEC-194, DEC-244).

Failure line:

6. **A release whose files or manifest do not match their hashes is refused by `gov install`, `gov update` and `gov doctor`.** Cases: a shipped file changed, added or removed after the release; a manifest whose own hash is wrong; a manifest whose file hash is wrong. **What this tree holds:** there is no `gov install` and no `gov update` command yet; W2-18 (pinned install) and W2-17 (`gov update`) build them after this ticket and depend on it. The install and update paths this tree has are `copier copy` and `copier update` of the template, whose task this ticket owns (`copier.yml` is in its paths), and `gov doctor`. The lead's reading: test the refusal through those paths and `gov doctor`, and state the reading in your README. If you judge that the KPI cannot be tested without the `gov install` and `gov update` commands themselves, say so as a package with your recommendation, and test the rest.

## What you write

- Only inside `tests/acceptance/W2-16/`. No throwaway implementation is left in the tree.
- FULL, thorough (DEC-221): every KPI line's success and failure, every list row the KPIs name, the edge cases above; no combinatorial expansion beyond what a KPI demands. Every covers id (CAP-43.b, CAP-43, and the rows) gets at least one test.
- Behaviour through public interfaces, never internals: the brief names no code to be written (DEC-462), and your tests import no module of `src/gov/lock/` or of the release code. Deterministic, no network. Copier is needed and never skipped where a case needs it (as W1-39 holds). Keep the whole suite's run under 20 minutes on this machine (Copier runs are slow: share a created project between cases where a case does not change it).
- A README that maps each KPI line and each row to its tests and gives the expected red reason of each, states the interface the tests assume and its source (as W1-39's README does), says how the tests run this worktree's code, and gives the run command.
- Red first: run the tests to the end, never with `-x`, with
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs`
  They fail for the reason the README states (the release command and the release record do not exist yet; the lock does not record a release; the comparison's gaps are still open). A case that passes before the implementation is either a guard that must already hold (say so in the README) or a test that tests nothing (fix it).
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit: stop and say so. Never `--no-verify`, never `core.hooksPath`.

Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-16 (DAEO-49o5): acceptance tests for hash-pinned releases" --trailer "Task: DAEO-49o5" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-43.b" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself: your commit's hash; the test count; the KPI lines, rows and covers ids with their tests; the red reason as you saw it (counts: failed, passed, errors, skipped); the `gov.__file__` line; every earlier test you would need revised, with its reason; any package.

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
