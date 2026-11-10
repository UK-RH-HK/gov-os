# D-10 run 1's red group A (103 cases): the socket helpers refuse /tmp itself (DAEO-clon, W2-112)

You are a fresh **independent test designer**, launched under W2-112's ticket (`.tickets/DAEO-clon.md`) because its
acceptance helper causes this red. D-10 (DEC-1122 (3)) needs the fix before run 2.

## The red
At integrate's head `c9742b08910a`, 101 cases of `tests/acceptance/W2-112/` and `tests/acceptance/W2-145/` error at
setup, and 2 cases of `tests/acceptance/W2-32/test_w2_32_s4_reranker_dies.py` fail, with:
`no temporary folder (None or a parent of it, outside the repository) is both writable here and short enough for a
Unix socket's path under it (108 bytes): set TMPDIR to a writable, shorter folder`.
Cause: `short_base()` in `tests/acceptance/W2-112/w2_112_support.py` skips every candidate with fewer than three path
parts (`len(folder.parts) < 3`), so `/tmp` itself never qualifies. With `TMPDIR` unset (the nightly, cron, any plain
shell) `tempfile.gettempdir()` is `/tmp` and no folder is left. It passes only where `TMPDIR` is a subfolder, as in a
Claude session. W2-145 uses the same helper (its conftest/support); W2-32's s4 case has its own copy of the logic.

## The task
1. Make the helper (and W2-32 s4's copy) find a short folder on a machine where `TMPDIR` is unset: e.g. when no
   candidate qualifies, make a fresh private folder directly under `/tmp` (`tempfile.mkdtemp(dir="/tmp", prefix=...)`,
   mode 0700) and use it as the base. Keep the purpose of the old rule: never write loose entries into `/` or `/tmp`
   itself, never inside the repository, path short enough for the socket (108 bytes). Lower no other expectation.
2. Prove it both ways, each through the heavy slot (`EMG-common.md`), with `PYTHONPATH=<your tree>/src`:
   `env -u TMPDIR python3 -m pytest tests/acceptance/W2-112 tests/acceptance/W2-145 tests/acceptance/W2-32/test_w2_32_s4_reranker_dies.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
   and the same with `TMPDIR=/tmp/claude-test-$$` (a subfolder). Report counts before and after for both. A case red
   for another reason (a GPU, a model) is named, not fixed.
3. One line in W2-112's README (and W2-32's if you change it) for the revision.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-112-d10r2-tests`, branch `w2/W2-112-d10r2-tests` (from integrate at
  `c9742b08910a`). Write only `tests/acceptance/W2-112/**`, `tests/acceptance/W2-145/**` (only if its own copy needs
  it) and `tests/acceptance/W2-32/**`.

## Rules
- `EMG-common.md` holds. Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No installs, never the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-clon" --trailer "Implements: DEC-1122"
  --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: D-10 run 1: the socket base refused /tmp itself; red wherever TMPDIR is unset"
  --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short: the change, both runs' counts before and after, the head commit.
