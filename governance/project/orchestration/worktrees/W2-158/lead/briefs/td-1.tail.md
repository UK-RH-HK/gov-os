
## Rules
- One test (or more) per KPI line S1-S5 and F1-F4, each doing what its Verify says, read with the Interface items it
  names. Name each after its id (`test_s1_...`, `test_f3_...`).
- Plant everything under pytest's `tmp_path`: a git tree (`git init`, a commit; GIT_CONFIG_GLOBAL=/dev/null,
  GIT_CONFIG_NOSYSTEM=1, a planted HOME) holding `template/governance/kernel/checks/<id>.yaml` declarations (the five
  fields id, family, tier, severity, command) whose commands are small stand-in scripts in the planted tree (e.g.
  `python3 checks/marker.py schema ok`), each recording that it ran (its pid, start and end times) in a file of its
  own and then passing, finding a problem (non-zero exit and a JSON findings list or a first line), answering not
  applicable (exit 2 and `{"not_applicable": true, "reason": "..."}`) or sleeping past the bound. Never this
  repository's tickets, checks or declarations as the subject (the ticket's acceptance_tests line); S5's timing case
  alone runs on this tree (below).
- Reach the code as its callers do: `python3 -m gov.cli.main check --structural [<base>] [--timeout <s>] --root
  <planted tree>` in a child process, with THIS tree's `src/` first on `PYTHONPATH` (fail the run if `gov` would import
  from elsewhere), judged by exit code and stdout lines (standard error for the could-not-run reason). Never import
  `gov.check.structural` at collection, so the suite runs red by failing, not by erroring at import. Use a small
  `--timeout` (1-3 s) in planted cases so each takes seconds; bound every wait (a timeout on the child), never a bare
  sleep. Allow for a loaded machine: assert "within bound + a few seconds", never tight timings.
- S1: eight families each declared with a marker: eight marker records, one line per family, in L2's order; the
  markers overlap in time (each sleeps e.g. 1 s; the whole run well under eight times that), each its own pid; a
  stand-in that sleeps far past the bound (and one that starts a grandchild that sleeps) is killed at the bound: the
  run ends within bound + slack and the (grand)child pid is gone afterwards; `--timeout` changes the bound.
- S2: passing, finding, not-applicable and timing-out planted checks, each family's line as L2/L5 states; the timed-out
  family's line starts `<family>: NOTICE` and contains `not measured`; a family with no declaration reads
  `skipped (no declaration)`; the last line starts `structural pass at <head12>` (the planted HEAD's first 12).
- S3/F1: a failing planted check gives exit 0 and a NOTICE line; `--root` a folder that is no git work tree, and a
  path that does not exist, each give exit 2 (reason on stderr); `--timeout 0` and `--timeout abc` exit 2; a static
  search of `src/gov/close`, `src/gov/launch` and `src/gov/queue` (each where it exists) finds no import or call of
  `structural` / `gov.check.structural` / `--structural`.
- S4: planted history: a `<base>` commit, then a commit touching `template/governance/kernel/skills/x/SKILL.md` (the
  portability marker runs), and one touching only another path (`portability: skipped (no such change)`); a `<base>`
  that does not resolve (the marker runs); no `<base>`: `portability: skipped (no base given)` and
  `links: skipped (no base given)`. Links: a planted tree with a stand-in `src/gov/__init__.py`,
  `src/gov/cli/__init__.py`, `src/gov/cli/main.py` and `src/gov/links/__init__.py` (the tree's own `gov links`,
  answering `gov links: 0 new since <base>, 4 standing` exit 0, or `gov links: 2 new since <base>, 4 standing` plus two
  finding lines exit 1, and writing `.gov-runtime/links/mark`): `links: ok (0 new since <base>, 4 standing)` and a line
  starting `links: NOTICE 2 new` holding the first finding line; it ran after the eight families had ended (its start
  after their markers' ends); without `src/gov/links/`: `links: skipped (no gov links in this tree)`.
- S5: a filesystem spy over a planted tree: snapshot every file (path, size, mtime_ns) under the planted tree's work
  files (you may leave `.git/` out) and the planted HOME before and after a run with a base and links; only the
  markers' own records and `.gov-runtime/links/mark` are new or changed. The timing case on this tree: `gov check
  --structural HEAD~1` with `--root` this repository's tree (ROOT, the tree the suite sits in), default bound, ends
  within 60 s and exits 0; name this test with `real` (e.g. `test_s5_real_pass_on_this_tree_is_bounded`) so the
  whole-folder filter leaves it out and `gov accept` runs it.
- F2: S1's sleeper and S2's timed-out check: the line is a NOTICE holding "not measured", never ok; exit 0.
- F3: a planted tree whose `core-schema` declaration holds a marker command: the marker runs, and no command of a
  built-in list does (plant `src/gov/__init__.py`, `src/gov/check/__init__.py` and `src/gov/check/schema.py`, graph.py
  and so on in the planted tree, each recording if run, i.e. what the reference tool's built-in
  `python3 -m gov.check.<module>` would start, and assert none ran); a planted tree with no declaration for a family reads it as
  `skipped (no declaration)`; a declaration in `governance/kernel/checks/` alone is used when the template layout has
  none, and the template layout's wins when both hold one.
- F4: `git diff --name-only <merge-base with w2/integrate>...HEAD` lists only paths matched by the ticket's
  `allowed_paths`, `tests/acceptance/W2-158/` or `docs/probes/DAEO-8a3f/`. It judges only this ticket's own branch:
  when the current branch (`git rev-parse --abbrev-ref HEAD`) is neither `w2/W2-158` nor `w2/W2-158-tests`, it skips,
  naming why (DECIDED-NOT-DONE row 171: otherwise the next ticket in the area and the merge queue's batches go red on
  it). Say so in its docstring.
- Tests are red now (no `--structural` yet). Run them and say which are red and why; anything green now is a fault in
  the test unless it guards "nothing else happens", the static search, or a refusal argparse already gives.
- No test named with `real`, `green_here` or `time_limit` unless it must be skipped by that filter. The whole folder in
  well under two minutes.
- Every pytest run goes through the heavy-job slot, with TMPDIR outside the repository and outside ~/gov-os-runs:
  `env HOME=/home/usain/gov-os-worktrees/W2-158-tests/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-158-td
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-158-tests/src
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest
  tests/acceptance/W2-158 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"
  -k "not real and not green_here and not time_limit"` (make /tmp/w2-158-td and the empty home first; put the line in a
  script file under your scratch and run it with `bash <file>`).
- Add `tests/acceptance/W2-158/README.md`: how the tests reach the code, what is planted, each KPI's cases.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-158-tests/.gov-runtime/scratch/.
  Literal paths only as write targets. No merge, no push, no edit outside your paths.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-8a3f" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1052, DEC-1073, DEC-1119, DEC-1109, DAEO-q7lk, DAEO-neam" -- tests/acceptance/W2-158`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The ticket's context packet (`gov context DAEO-8a3f --role independent-test-designer --budget 12000`)
