# Brief: engineer (repair)

You are a fresh engineer. Ticket: `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`. The ticket is implemented, and its acceptance suite holds new cases that fail. You repair the implementation until they pass, keeping every other case green.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-49o5`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`). If anything differs, stop and say so.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A single tool call is cut off at 10 minutes: if a suite takes longer, run it file by file, one after another, never two at once.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A try-out that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. **Install nothing** (no `pip install`, no download, no network): a tool you need is returned as a package. No push, merge, rebase or tag.
- **Nobody tags and nobody signs.** You never create a git tag in this repository, and your code never creates one or signs anything. You never run `gov release` against this repository's real history, and you write nothing into this worktree's `docs/releases/` except its existing README. Try-outs build releases in temporary repositories.
- Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never touch `tests/acceptance/**` (MR-3). Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md` (read-only): its KPI lines and its `allowed_paths`.
- The acceptance suite and its README (read-only): `tests/acceptance/W2-16/`, the new cases in `test_w2_16_immutability.py` among them.
- CAP-43 and its covers in `docs/contract/contract.yaml`; DEC-722 and DEC-135 in `docs/DECISION_REGISTER.md`.
- The code the ticket touches: `src/gov/release/`, `src/gov/lock/`, `copier.yml`, and their builder tests.

## The failing output (and nothing else of the earlier rounds)

Run from this worktree, `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs` gives `10 failed, 75 passed`. The ten:

```
FAILED test_w2_16_immutability.py::test_the_same_version_from_an_older_integration_commit_is_refused[the first release's record commit]
FAILED test_w2_16_immutability.py::test_the_same_version_from_an_older_integration_commit_is_refused[the first release's own commit]
  AssertionError: `gov release 1.5.0` built a release although w2/integrate holds release 1.5.0's record; HEAD is at the first release's record commit, older
  (exit code: 0)
FAILED test_w2_16_immutability.py::test_the_same_version_after_its_record_was_removed_is_refused[first]
FAILED test_w2_16_immutability.py::test_the_same_version_after_its_record_was_removed_is_refused[second]
  AssertionError: `gov release 1.4.0` built a release although release 1.4.0's record was committed on w2/integrate and removed later
  (exit code: 0)
FAILED test_w2_16_immutability.py::test_the_same_version_as_an_existing_owner_tag_is_refused[lightweight tag]
FAILED test_w2_16_immutability.py::test_the_same_version_as_an_existing_owner_tag_is_refused[annotated tag]
  AssertionError: `gov release 1.4.0` built a release although the tag v1.4.0 already exists, on another commit
  (exit code: 0)
FAILED test_w2_16_immutability.py::test_a_version_differing_only_by_build_metadata_from_a_recorded_one_is_refused[first]
FAILED test_w2_16_immutability.py::test_a_version_differing_only_by_build_metadata_from_a_recorded_one_is_refused[second]
  AssertionError: `gov release 1.4.0+build.2` built a release although release 1.4.0 exists and 1.4.0+build.2 differs from it only by build metadata
  (exit code: 0)
FAILED test_w2_16_immutability.py::test_a_release_never_hashes_bytes_the_commit_does_not_hold[--assume-unchanged]
FAILED test_w2_16_immutability.py::test_a_release_never_hashes_bytes_the_commit_does_not_hold[--skip-worktree]
  AssertionError: the manifest of 1.4.0 gives template/governance/kernel/schemas/ticket.schema.json the hash of bytes the commit ea2bf29f... does not hold (--assume-unchanged hid the edit): listed ['22865a7f...'], committed 186c1388..., edited 22865a7f...
  (exit code: 0)
```

## What you write

- Only inside `src/gov/lock/**`, `src/gov/release/**`, `copier.yml`, `tests/unit/lock/**`, `tests/unit/release/**`, `docs/releases/README.md`. **Not** `src/gov/check/commands.py` (DEC-753: `gov release` is recorded in the command lists only in a later round), never `src/gov/close/**`, `tests/unit/close/**` or `template/governance/kernel/checks/product-traceability-trailers.yaml`, and never a file of W2-49.
- If a repair needs a change outside those paths, do not make it: return a package naming the file.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests for what you change go in `tests/unit/release/` (or `tests/unit/lock/`), as regression evidence only.
- Proportion (DEC-135): only what the failing cases need. **Never make a guard or gate decision fail open:** a check that cannot be made (git cannot be read, a tag list cannot be read) refuses the release; it never lets it through.
- **Commit your work before you run any long suite.** Then run, each to its end, never with `-x`, one after another:
  - `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs` (expect 85 passed);
  - the same for `tests/acceptance/W1-39` (one case is a known red: `test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured`; report any other) and `tests/acceptance/W1-27` (file by file if it passes 10 minutes);
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/unit/release tests/unit/lock -q -p no:cacheprovider`, then `tests/unit` whole.
  A repair after a run is a new commit.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit: stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-49o5" --trailer "Role: engineer" --trailer "Implements: DEC-722" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself: your commits' hashes; the files changed; what the release now checks before it builds; each suite you ran with its counts and each red case by name with its reason; the `gov.__file__` line; the lines added and removed (`git diff --stat 68cea1a4..HEAD`); anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
