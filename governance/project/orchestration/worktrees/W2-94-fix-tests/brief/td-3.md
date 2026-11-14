Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-94-fix-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-94 S13: acceptance cases for the counts schema's `fix` object, the independent test designer's brief (DAEO-g87r)

You are a fresh independent test designer (class C3) under **W2-94** (`DAEO-g87r`). The ticket is read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`. Read its last paragraph ("Kept open and reopened
2026-11-14 16:20") and the KPI line **S13**. Write the S13 cases **from the KPI line and the interface below, as
described behaviour (DEC-136)**. After you, an engineer who sees only your failing output will change the schema file.
You never edit the schema, the launch script or any file outside `tests/acceptance/W2-94/`.

## Governing decisions (quoted from the register; `gov context` was BLOCKED)
- **DEC-1180 (4)**, standing: "Do now everything that can be done now ... a defect spotted is fixed in the same flow."
  The CTO kept W2-94 open under it and added S13 for the fix-flow review's finding P4: the closed counts schema refuses
  the fix flow's `fix` key.
- **DEC-1180 (2)**: the launch script gains a one-question fix flow on the writer's round 2 (already landed, with its
  acceptance cases in `tests/acceptance/W2-94/test_w2_94_fix_flow.py`).
- **DEC-136**: tests are written from described behaviour, not from the implementation.

## The KPI line (the ticket's S13, word for word)
S13 The counts schema takes the fix flow's `fix` key (rv P4, 2026-11-14): `indep-counts.schema.json` allows an optional
`fix` object with exactly `id` (a question id), `code` (the reason code) and `action` (`corrected` or `replaced`), and
nothing else; a fix run's counts validate, so `finish()` no longer logs "counts schema failed" and `--counts-only` of a
fix run no longer refuses with 17; every other flow's counts validate as before [rv-fix P4, DEC-1180 (4)]
Verify: a fix run's counts with `fix` validate; a `fix` with an extra key or another action is refused; the W2-149 counts
cases pass unchanged.

## The interface, made exact by the lead (the engineer gets the same rule through your failing output)
File: `governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json` (the launch script reads it as
`indep_launch.COUNTS_SCHEMA` and checks with `indep_launch.schema_ok(obj, schema)`).
1. The top-level object may carry an optional key `fix`. A counts object without `fix` validates exactly as today.
2. When present, `fix` is an object with exactly the three keys `id`, `code`, `action`, all required, no other key.
3. `id`: a string fully matching `q` and two digits (`q00` to `q99`); `q2`, `Q02`, `q002`, `q0a` are refused.
4. `code`: exactly one of `SOURCE_IS_SCAFFOLD`, `SOURCE_PATH_ABSENT`, `SOURCE_NOT_TEXT`, `SPAN_OUT_OF_FILE`,
   `HEADING_NOT_FOUND`, `ANSWER_NOT_IN_SPANS`, `NONEXISTENT_NAME_FOUND`, `NONEXISTENT_NO_NAME`; any other string (also
   lower case) is refused.
5. `action`: `corrected`, `replaced`, or `null`. The landed fix flow writes `null` until the result has passed its checks
   (a dry run, a refusal at the result, a stop), and the word on delivery; so `null` must validate, or a dry or refused
   fix run would still log "counts schema failed". Any other word (`fixed`, `Corrected`, the empty string) is refused.
   (The lead's reading of S13's "`corrected` or `replaced`" together with "finish() no longer logs 'counts schema
   failed'"; the narrow review checks it.)
6. `fix` as `null`, a list or a string is refused (the launch script omits the key when there is no fix).

## What the cases must show (add them to `tests/acceptance/W2-94/`; one new file `test_w2_94_s13_counts_fix.py` is
## the suggested form; a parametrized table per item is fine)
- **Validates (S13's first Verify):** (a) the counts of a real **delivered** fix run on the planted world (the fixtures
  of `test_w2_94_fix_flow.py`: `FixWorld` in `w2_94_fix_support.py`; reuse them, do not copy them) validate with
  `indep_launch.schema_ok(counts, schema)` for each of `corrected` and `replaced`; (b) the counts of a **dry** fix run
  (`action` null) validate; (c) a fix run refused 20 at the result (`action` null) validates.
- **The visible effects:** after a delivered fix run, its `launch.log` has no `counts schema failed` line (the script
  logs the words `counts schema failed` on a failed check; read `finish()` only to learn that log line's form), and
  `--counts-only` of that run (`--sets-root <root> --kind writer --run <run id> --counts-only`) exits 0 and prints the
  counts object with its `fix` key.
- **Refused (S13's second Verify):** starting from a valid fix run's counts object, each of these makes
  `schema_ok` false: an extra key in `fix`; each of the three keys missing; `action` another word, `Corrected`, `""`;
  `id` `q2`, `Q02`, `q002`, `q0a`; `code` unknown or lower case; `fix` `null`, `[]`, `"q02"`.
- **As before (S13's third):** a counts object without `fix` (a planted round-2 writer run without `--fix`, and a
  checker or auditor dry run of the W2-149 world) still validates. This is a guard, green today and after.
- **The S11/F6 diff case must be revised (decided behaviour, the CTO's S13):** `test_w2_94_fix_flow.py::test_s11_f6_the_branch_changes_no_wall_brief_or_schema_file`
  today requires no change under `indep-schemas/`; S13 now changes `indep-counts.schema.json` by this ticket. Revise it so
  `indep-walls/` and `indep-briefs/` stay unchanged as before, and under `indep-schemas/` only `indep-counts.schema.json`
  may change (any other file there, changed or untracked, still fails). Rename the test only if its name would lie.
  Also drop or reword the "a fix run's counts do not validate / do not assert the schema" notes in that file's
  docstrings or comments and in the README, now that S13 makes them validate.
- Every new case (except the as-before guard) must be **red against the unchanged schema on the merged base** for the
  reason "the schema refuses the `fix` key" (or, for the refusal cases, list them as green-today where the closed
  schema already refuses: say which in the README row; at least the "valid" cases and the `--counts-only` case are red).

README: in `tests/acceptance/W2-94/README.md`, in the same commit, add one map row for **S13** in the fix-flow table's
form (KPI cell names only S13; tests cell names `<file>::<test>` ids; the red reason against the unchanged schema), and
update the S11/F6 rows and the "Counts schema" sentence for the revision above.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-94-fix-tests`, branch `w2/W2-94-fix-tests` (at `5285ef173`, the merged
  base). Write only under `tests/acceptance/W2-94/`. Leave every other W2-94 test file unchanged except the S11/F6
  revision above and the README.
- Read first: `tests/acceptance/W2-94/README.md` (the fix-flow section), `test_w2_94_fix_flow.py`, `w2_94_fix_support.py`,
  the schema file (read it; do not change it), and `finish()` and `counts_only()` in
  `governance/project/orchestration/tools/indep_launch.py` only for their log line and exit codes.
- If you need a byte-exact fixture, write it with the Write tool, never Bash `cp`.

## Walls (hard; a breach fails the ticket)
- **Planted fixtures only.** Never open, list, grep or print anything under `/home/usain/gov-os-eval/`,
  `/home/usain/gov-os-runs/`, any folder named `hidden` outside your `tmp_path`, any `fixtures/evaluation/examin/visible`
  or `hidden` folder of any tree, EXAMIN's real repository or the owner's copy. Every planted word carries the prefix
  `zqxw94`, as the existing W2-94 cases do.
- No model, network or installs; no real `claude` session (the stub only). One simple command per Bash call; longer
  things in a script file under your sandbox's own `$TMPDIR` (never a new folder under `.gov-runtime/scratch/`; `/tmp`
  is read-only in the sandbox). No merge inside the sandbox. No `gov retrieve` or `gov context`: search with Read and
  Grep, and search again once in different words if the first does not answer.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Pytest, every run (a resource gate's refusal is a wait, not a refusal)
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94/ -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=line`
If the slot tool cannot run in your sandbox, run the same pytest without it and say so.

## Order of work
1. Write the cases; run the W2-94 folder against the unchanged schema; record which new cases are red and why, and
   that every pre-existing case is still green (the S11/F6 revision included).
2. Commit (only `tests/acceptance/W2-94/`), every trailer in ONE final paragraph (no blank line between them):
   `git commit -m "W2-94 (DAEO-g87r): S13's cases, the counts schema's optional fix object; the S11/F6 diff case allows indep-counts.schema.json" --trailer "Task: DAEO-g87r" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1180" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-94`
3. Name one planted break of a correct schema change that a case would catch (by reading; e.g. `action` left a free
   string, or `fix` left open to extra keys).

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (the red
run's counts, the failing test ids with their one-line reason, and the commit hash), tests, discoveries (any point where
the interface and the KPI disagree), risks, lessons, proposed_decisions, unresolved, recommended_next_action.
