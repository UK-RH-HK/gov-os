## What you read

- The ticket file as it stands on `w2/integrate` (`git show w2/integrate:.tickets/DAEO-qzrq.md`; your worktree's copy
  is older): success-7 now says the query server starts "with the GPU visible (DEC-1033, replacing DEC-798)", and
  success-8 says `ensure_query_available` starts the query server without hiding the GPU (no
  `CUDA_VISIBLE_DEVICES=-1`), so a server restarted by the code comes back on the GPU, a test that enforced the
  CPU-only start being revised with `Rewrite-Reason: DEC-1033`.
- The decisions, in `docs/DECISION_REGISTER.md` on `w2/integrate` (`git show w2/integrate:docs/DECISION_REGISTER.md`):
  DEC-1033, DEC-1032, DEC-866 (supersession: a test revised for a newer decision carries `Rewrite-Reason:` and lowers
  no other expectation), DEC-491.
- Run 1's and run 2's tests and README in your worktree, `tests/acceptance/W2-123/` (your predecessors' work). The
  expectations to revise are where a test asserts the query server's (or its runner's, or a restarted query server's)
  `CUDA_VISIBLE_DEVICES` is `-1`: today `test_w2_123_start.py` (about lines 60-80, the query server's start, with
  `CUDA_VISIBLE_DEVICES=0` in the caller's environment) and `test_w2_123_restart.py` (about line 116, the restarted
  query server); find any other by `grep -n CUDA_VISIBLE tests/acceptance/W2-123/`.

## What you change

- Each such expectation becomes the new behaviour: the code adds no `CUDA_VISIBLE_DEVICES=-1`; the caller's own
  environment reaches the daemon and its runner as it is (with `CUDA_VISIBLE_DEVICES=0` in the caller's environment,
  the daemon and its runner see `0`; with none, they see none), for the query server's start by `ensure_query_available`
  and for its safe restart. Every other assertion of those tests stays as it is (the cap: CPU list, niceness,
  `OLLAMA_NUM_PARALLEL`, `OLLAMA_HOST`, the result's `settings`); rename a test whose name says the GPU is hidden.
- The README: map the revised tests to **success-8** (keep them also under success-7 where they test the cap), state
  their expected red reason on the code before the patch (the query server's start adds `CUDA_VISIBLE_DEVICES=-1`), and
  note the revision with its reason. Keep run 2's map as it is otherwise.
- Do not touch `tests/acceptance/W2-54/` or any other ticket's tests: if one still enforces the CPU-only start, name it
  in your return (DEC-866).
- Only inside `tests/acceptance/W2-123/`.

## Checks

- Red on the old behaviour: your worktree's `src/` still adds `CUDA_VISIBLE_DEVICES=-1` (it predates the patch), so run
  the revised files there and show the revised cases fail for that reason only, to the end, never with `-x`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src TMPDIR=/tmp/gov-os-lead-W2-123 python3 -m pytest tests/acceptance/W2-123/test_w2_123_start.py tests/acceptance/W2-123/test_w2_123_restart.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (two files: through `verify_lock.sh`, as the standing rules say; if `/tmp/gov-os-lead-W2-123` is read-only in your
  sandbox, use the sandbox's own `TMPDIR` and say so). Report the counts; the unrevised cases must still pass there.
- `gov accept` in your worktree to check the map (every test mapped, 0 unmapped):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src python3 -m gov.cli.main accept DAEO-qzrq --json`
  (your worktree's ticket file has no success-8 yet, so the map may name a line it lacks: say what you saw; the lead
  checks it again after the merge).
- An ambiguity or a dispute is never a guess: return it as a package.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only your test paths, in one commit, with the trailers in
the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-qzrq" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1033, DEC-1032" --trailer "Rewrite-Reason: DEC-1033" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then run `git log --oneline -2` and `git status --short` and quote them.
