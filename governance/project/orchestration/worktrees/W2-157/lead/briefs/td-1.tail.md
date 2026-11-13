

## Rules
- One test (or more) per KPI line S1-S5 and F1-F4, each doing what its Verify says, read with the Interface items it
  names. Name each after its id (`test_s1_...`, `test_f3_...`).
- Reach the code as its callers do: `python3 -m gov.cli.main resources --backstop <pgid> ... --root <project> --json`
  in a child process (this tree's `src/` first on `PYTHONPATH`; fail the run if `gov` would import from elsewhere),
  judged by exit code, the envelope's `result` (L8), the log (L6) and the inbox item (L7). Never import
  `gov.resources.backstop` at collection, so the suite runs red by failing, not by erroring at import. Set
  `gpu_backstop_every_s` small (e.g. 0.1) in the planted file so each case takes seconds; bound every wait (a timeout on
  the child, polls with a deadline), never a bare sleep.
- S1: readings 15,800 then 15,900 MiB (a total that is no spill, e.g. 24,576), the limit 15,872 in the planted file,
  a stand-in job in its own group: after the first reading the job is running (state from `/proc/<pid>/stat`, not `T`),
  after the second it is stopped (`T`), the TRIP log line holds 15900; a planted file with the limit missing, and one
  with it malformed (e.g. a string, 0, no date), each refuses (exit 1, `RESOURCE_CONFIG_INVALID`, the key named),
  the job untouched. Also the period and the embedders keys missing each refuse, named (L2).
- S2: total minus 63 trips (spill named), total minus 65 does not, each with used under the limit.
- S3: a stand-in server answering `/api/ps` with a model `size_vram` < `size` trips once (the port named); a planted log
  with a line `offloaded 30/33 layers to GPU` appended after the watch starts trips once (the log named); a line
  `offloaded 33/33 layers to GPU` does not; a partial-offload line already in the log before the start does not.
- S4/F1: an unrelated process of the same executable name, in its own group not named, still running after a trip and
  having received no signal (it installs handlers for the catchable signals and records any it gets in a file; its
  state is not `T`); `--backstop abc` (and `1`, `-5`) exit 2, nothing signalled; a named group already ended at start
  is skipped and named while a live one is still watched; a job that ends on its own first ends the watch (exit 0,
  `tripped: false`, the `end:` line); a trip writes exactly one inbox item with the reason, the paused groups, the
  `resume: kill -CONT -- -<g>` and `stop:` lines (L7), and the watch has ended.
- S5: a filesystem spy over a run with no trip (the job ends first): snapshot every file (path, size, mtime_ns) under
  the planted HOME and the planted project before and after; only `$HOME/.gov-os/machine/gpu-backstop.log` is new or
  changed; `gate.json` byte-identical; the stand-in servers got only `GET /api/ps`.
- F2: each reading of S1, S2 and S3 gives its stated outcome (parametrise).
- F3: the planted file's limit (e.g. 12,000, not the built-in 15,872) with `LIMIT`, `GPU_BACKSTOP_LIMIT_MIB` and
  `GOV_GPU_BACKSTOP_LIMIT_MIB` set to a third value (e.g. 20,000): readings 11,990 then 12,010 trip at the second;
  `--gpu-backstop-limit-mib 20000` given is refused (exit 2) and nothing signalled; the missing and malformed refusals.
- F4: `git diff --name-only <merge-base with w2/integrate>...HEAD` lists only the ticket's allowed_paths plus
  `tests/acceptance/W2-157/`. It is green only when the branch is clean; say so in its docstring.
- Tests are red now (no `--backstop` yet). Run them and say which are red and why; anything green now is a fault in
  the test unless it guards "nothing else happens" or a refusal argparse already gives.
- No test named with `real`, `green_here` or `time_limit` unless it must be skipped by that filter. The whole folder in
  well under two minutes.
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-157-tests/.gov-runtime/scratch/empty-home
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-157-tests/src python3 -m pytest
  tests/acceptance/W2-157 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"
  -k "not real and not green_here and not time_limit"`.
- Add `tests/acceptance/W2-157/README.md`: how the tests reach the code, what is planted, each KPI's cases.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-157-tests/.gov-runtime/scratch/.
  Literal paths only as write targets. No merge, no push, no edit outside your paths.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1030, DEC-1073" -- tests/acceptance/W2-157`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
