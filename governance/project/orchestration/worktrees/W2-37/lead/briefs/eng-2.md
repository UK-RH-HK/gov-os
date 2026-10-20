You are a fresh engineer. Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37` on branch `w2/W2-37`. `gov impact` is built (`src/gov/impact/`, commit `2234049f`); a test design batch (commit `ac4983f8`, `tests/acceptance/W2-37/test_w2_37_review_findings.py`, and the README's section "Second batch: the first review's findings") adds acceptance cases that are red against it. You make them pass without turning any other case red.

## Step 0, before any work: the sandbox check (DEC-789)

Report its result first in your return.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6n5k','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree (do not delete it).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-6n5k`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37` and `w2/W2-37`), and `git rev-parse HEAD` (expect `ac4983f8` as its prefix). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it); copy single named files only, never `governance/project/`. A test that needs a repository builds a temporary one. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Untracked names such as `.bashrc`, `.gitconfig`, `.mcp.json`, `docs/source` in `git status` are sandbox placeholders: never add, edit or delete them; stage your files by exact path, never `git add -A` or `git add .`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. The guard refuses tools it does not know (`Monitor` and every `mcp__` tool): do not call them.
- Never run `gov rebuild` (any form). Never run `gov close`, `gov adopt` or `gov pause`.
- The git hooks are uninstalled until W2-08: never `--no-verify`, never `core.hooksPath`.
- **Known limit (package P-W2-38):** inside the sandbox the code graph's folder `/tmp/gov-cbm-<uid>` is read-only, so the suite's `local_only` cases (they build a code index) fail at setup here with `OSError: [Errno 30] Read-only file system`. Make every change the failing cases need, run what can run, commit, and then say plainly in your return which `local_only` cases you could not run, with the exact error. The lead may then resume this same session outside the sandbox for you to run them and finish. Do not work around it.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-6n5k.md` (read-only) and the W2-37 card in `docs/plan/WAVE_2_WBS.md` section 2.
- The acceptance tests and README (read-only), `tests/acceptance/W2-37/`, the new file and the README's new section above all.
- DEC-391 in `docs/DECISION_REGISTER.md` (what `gov closure` reports as `uncommitted`, current and stale), DEC-135, DEC-732.
- The code you change, `src/gov/impact/`, and what it reads: `src/gov/closure/` (read API only: you change **no** file there), the store and records (`src/gov/store/`, `src/gov/records/`, `src/gov/decisions/`: public API only, change nothing), the code index (`src/gov/codeintel/`, read only).

## The failing output (the lead's run outside the sandbox at `ac4983f8`: 14 failed, 82 passed)

Three are expected to stay red; leave them red and report their failure lines:
- `test_w2_37_rows.py::test_the_depth_of_a_radius_comes_from_an_owner_decision_or_a_measurement` (owner decision pending, P-2: never cite a decision id that does not say so);
- `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question[template]` and `[claude-copy]` (the change skill is outside your paths, P-1).

The eleven you make pass, all in `test_w2_37_review_findings.py`:
- `test_a_record_graph_that_does_not_match_the_tree_is_never_reported_current[ticket-added-uncommitted]`, `[edge-removed-uncommitted]`, `[switched-to-older-branch]`: `AssertionError: \`graphs.record\` says 'ok' although that graph was not`
- `test_with_both_graphs_a_record_graph_that_does_not_match_the_tree_is_never_complete[ticket-added-uncommitted]`, `[switched-to-older-branch]` (`local_only`): `AssertionError: \`graphs.record\` says 'ok' although that graph was not`
- `test_an_execution_record_whose_kind_is_not_a_list_never_matches[single-item]`: `AssertionError: a CIT-E whose \`code\` is 'some_symbol', not a list, matches`; `[map]`: `AssertionError: a CIT-E whose \`decisions\` is {'DEC-099': 'done'}, not a list, matches`
- `test_a_cit_p_written_from_an_incomplete_assessment_says_so_or_is_refused`: `AssertionError: the CIT-P written from an incomplete assessment does not say \`complete: false\`: {'id': 'CITP-901', 'type': 'change-impact-proposal', 'status': 'PROPOSED', 'state_class': 'DERIVED', 'title': 'The impact of changing DEC-001', 'change': ['DEC-001'], 'radius': 'R3', 'depth': 8, 'affected': {...}}`
- `test_a_name_two_definitions_share_is_not_deletable_when_one_is_called` (`local_only`): `AssertionError: w37_shared is reported deletable although w37_caller calls one of its definitions: [{'id': 'w37_shared', 'graph': 'code', 'path': 'app/alpha.py', 'deletable': True, 'governance': True}]`
- `test_a_code_file_older_than_the_index_but_not_in_it_is_never_missed[untracked]` and `[committed]` (`local_only`): `AssertionError: the report reads as complete although the code graph was not` / `AssertionError: \`graphs.code\` says 'ok' although that graph was not`

## What you write

- **Only inside the ticket's `allowed_paths`, as the card narrows them:** `src/gov/impact/**` and `tests/unit/impact/**`. `src/gov/closure/**` is read API only: you change no file there; if its API lacks what a case needs, stop that part and return a package naming the function. No other file anywhere.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/impact/`, as regression evidence only.
- Proportion (DEC-135): only what the failing cases need. Never make a guard or gate decision fail open: an impact report never reads as complete when a graph was missing, stale or unreadable; a refusal stays a refusal. `gov impact` stays a read command: it writes nothing outside its declared output (`--out`'s one file), and it never builds or rebuilds the store or the code index.
- Run the ticket's acceptance tests in the foreground to their end, never with `-x`: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -rs`, then the builder tests `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/unit/impact -q -p no:cacheprovider`.

## Commit

Commit only your paths, staged by exact path, with the trailers in the final block (DEC-182):

    git commit -m "W2-37: gov impact, the first review's findings" --trailer "Task: DAEO-6n5k" --trailer "Role: engineer" --trailer "Implements: CAP-33.b" --trailer "Implements: DEC-167" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

A later fix is a new commit with the same trailers. Show `git log --format='%h %s' -3`, `git show --stat --format='%(trailers)' HEAD` and `git status --short` in your return.

## Return

Your commit hashes; the files changed; the lines added and removed (`git diff --stat ac4983f8..HEAD -- src tests/unit`, and `git diff --stat 4d79565e..HEAD -- src tests/unit`); the tests you ran with their counts, each still red with its failure line and why, and each `local_only` case you could not run with its error; any change to the interface (output keys, exit codes, error codes); the `gov.__file__` line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
