You are a fresh Engineer. Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2, run 7, fix iteration 2. You are given the failing output only. You work only in the ticket's worktree `/home/usain/gov-os-worktrees/W2-88` (branch `w2/W2-88`, head 2da02b28e at your start). You never read the acceptance tests (DEC-820). Budget: about 30 minutes, one commit.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-2bdu`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-88`, `w2/W2-88`). If anything differs, stop and say so.

## Allowed paths
`src/gov/adopt/fabric.py`, `tests/unit/adopt/test_w2_88*`, `docs/changes/W2-88-evidence.md`. Anything else: name it in your return, do not change it.

## The failing output (the acceptance run at 2da02b28e, from an installed wheel with no Gov OS source tree)
```
test_s24_a_shipped_file_found_nowhere_is_refused_by_name_with_the_places_looked[not-under-template]
E   AssertionError: details.looked names no place: {'file': 'governance/project/not-shipped-anywhere.yaml', 'looked': []}
test_s24_a9_from_an_installed_release_with_a_shipped_folder_missing_is_refused_by_name_and_copies_nothing
E   AssertionError: details.looked: {'file': 'governance/project/retrieval.yaml', 'looked': []}
```
The interface (binding, the lead's, DEC-1052): `fabric.shipped(rel, root)` refuses `SHIPPED_FILE_MISSING` with "the message naming `rel` and each place looked; `details` hold `file` (= `rel`) and `looked` (the places)". **The lead's decision for this fix:** the search for the Gov OS source tree is a place looked. So `details.looked` is never empty: it always names, first, where the source tree was sought (the running `gov` package's folder, with the words that no folder at or above it holds `copier.yml`, `template/` and `src/gov/`, when none does; or the source tree's `<tree>/<rel>` when one was found), then, for a `rel` under `template/`, `<root>/X`. A place that was not looked at is never listed (never `<root>/<rel>` for a `rel` outside `template/`: that is the project's own overlay, not Gov OS's file). The message says the same places. Nothing else changes.

## The work
Unit test first (red, then green) in `tests/unit/adopt/test_w2_88_p1.py`: from no source tree (a stand-in for `_source_tree` returning None, or the wheel case you already have), a `rel` outside `template/` and one under it with the project's copy missing each give `looked` non-empty, naming the gov package's folder and the source tree's absence (and `<root>/X` for the second), and never `<root>/<rel>` for the first. Then the fix in `fabric.py`. Run `tests/unit/adopt` through the heavy slot. Commit.

## How to run
`env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=<a subfolder of the sandbox's own $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/adopt -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`. A resource gate's refusal is a wait. Never `-x`. (`tests/unit/adopt/test_safety.py::test_s1_a_stage_writes_nothing_over_an_untracked_file` is a known red from S26, outside your paths: leave it.)

## Rules
- Write files with the Write and Edit tools and absolute paths. Scripts only under a subfolder of the sandbox's own `$TMPDIR` (never `.gov-runtime/scratch/eng/`). No here-document, no backticks, no `bash -c '…'`. **Refused twice for the same call: stop and say so** (DEC-1142 (9)).
- Before the commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file. Never `--no-verify`, amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-2bdu" --trailer "Role: engineer" --trailer "Implements: DEC-954, CAP-44.f, CAP-20" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`.
- Never run `gov adopt`, `gov rebuild`, `gov close` against a real repository; install nothing on the machine; never ask the owner.

## Return
One message, your last. The twelve fields first, each a labelled line; then where the fix is (path:line), the unit counts, the sandbox check, your commit (12-digit hash and subject).
```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
Refused twice for the same call: stop and say so.
