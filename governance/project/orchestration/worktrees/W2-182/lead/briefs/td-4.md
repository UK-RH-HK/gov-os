# Brief: independent test designer, W2-182 (DAEO-5y8d), run 2 batch 2: the folder's redirect must never drop other folders

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-5y8d (W2-182), profile LITE,
class C1. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-182-tests |
| branch | w2/W2-182-tests (head cc7867f93) |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md |
| scratch for scripts and temp folders | your sandbox's own `$TMPDIR` only |

Your allowed paths (write nothing else): `tests/acceptance/W2-182/**`.

## The behaviour to fix (the lead's finding)
Commit cc7867f93 added `tests/acceptance/W2-182/` (README map, `conftest.py`, `w2_182_support.py`,
`test_w2_182_no_lowering.py`). Its `conftest.py` `pytest_configure` replaces `config.args` with the README's 9 mapped node ids
whenever the conftest is loaded early. Measured by the lead (`--collect-only -q`):
- `pytest tests/acceptance/W1-32` → 52/81 collected (29 deselected)
- `pytest tests/acceptance/W1-32 tests/acceptance/W2-182` → 9 collected (W1-32's other cases silently dropped)
- `pytest tests/acceptance/W1-32 tests/acceptance/W2-182/test_w2_182_no_lowering.py` → 9 collected (the same)

A pytest call that names this folder (or a file in it) together with any other path must run all of those other paths' cases
as it would without this folder; only a run whose every argument is this folder (or a node inside it) may be pointed at the
mapped node ids. A whole-tree run (`pytest tests`, `pytest tests/acceptance`, `pytest tests -n auto`) must collect exactly
what it did before cc7867f93 plus this folder's own case(s), with each mapped case once. `gov accept W2-182` must still run
exactly the 9 mapped ids (read how it calls pytest in `src/gov/accept/runner.py` to know what its arguments are).

Fix it the smallest way (for example: redirect only when every entry of `config.args`, resolved, is inside this folder; else
leave `config.args` untouched). Keep the README map, the support and the no-lowering case as they are unless the fix needs
otherwise; lower nothing; add no skip, xfail, flaky or rerun mark.

## Prove it (record each command and its count line)
1. The three commands above: now 52, 52 + this folder's own case(s) (or + 9, say which and why), and the same with the file.
2. `pytest tests/acceptance/W2-182 --collect-only -q` → the 9 mapped ids.
3. `pytest tests/acceptance --collect-only -q -m "not local_only" -k "not real and not green_here and not time_limit"`: the
   count on cc7867f93's parent (23e7c4971: use `git worktree`-free means, e.g. a temporary copy of the folder removed, or
   `--ignore=tests/acceptance/W2-182`) against the count with the folder; the difference is the folder's own case(s) only.
4. `gov accept W2-182` (call `gov.cli.main.main(['accept','W2-182','--root','/home/usain/gov-os-worktrees/W2-182-tests'])`
   through the heavy slot, as batch 1 did): 8 passed, 1 failed (line E, red until the template's hooks line lands in the
   ticket's own tree; do not touch `template/`).

## How you run tests
Every pytest through the heavy slot, TMPDIR the sandbox's own `$TMPDIR` (outside the repository and outside ~/gov-os-runs):
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-182-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <args> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A resource gate's refusal is a wait: wait and retry, it is not a refusal. If another ticket's case turns red, name it with
file:line and leave it.

## Searching and forms
No `gov retrieve` and no `gov context` in the sandbox: Read and Grep. Never open the evaluation sets' root, held-out material
or any hidden or memory-verdict folder. Write and edit with the Write and Edit tools and absolute paths; scripts longer than
one line go in `$TMPDIR`. Refused twice for the same call: stop and say so; never work around a refusal. No merge, no push.

## Commit (your paths only)
```
git -C /home/usain/gov-os-worktrees/W2-182-tests commit -m "W2-182: its folder's redirect only when the run names the folder alone" --trailer "Task: DAEO-5y8d" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1163, DEC-1156" -- tests/acceptance/W2-182
```
Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty; `git diff 23e7c4971 --stat`
names only `tests/acceptance/W2-182/` paths.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (each command and its count line) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
