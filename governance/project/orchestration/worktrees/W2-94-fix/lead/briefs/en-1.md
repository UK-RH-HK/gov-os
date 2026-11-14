# W2-94 fix flow — the launch script's one-question fix flow, the engineer's brief (DAEO-g87r)

You are a fresh engineer (class C2) under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; read its "Reopened 2026-11-14" paragraph and KPI
lines S6 to S12 and F4 to F6). The owner decided **DEC-1180 (2)** (P-Q02-RUN-1 (a), "run today, as soon as it is built
and reviewed"): the walled launch script gains a one-question fix flow on the writer's round 2, so that the owner's
approved writer variant for hidden question q02 (DEC-1178 (5)) runs byte for byte unchanged. Its text is at
`/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/variant/EXAMIN-writer-q02-fix.md` (sha256
`0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`; read its front matter and sections 2, 3 and 5: they
name the inputs and the output the flow gives it). Never change it.

**Speed matters; keep the change small:** one flag pair on the existing writer round 2, read and checked before
anything is written, its own staging and delivery branch; no refactor, no change to any other flow.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-94-fix`, branch `w2/W2-94-fix`. Write only
  `governance/project/orchestration/tools/indep_launch.py` and a new `tests/unit/orchestration/test_w2_94_fix_flow_unit.py`.
  Never change `governance/project/indep-walls/**`, `governance/project/indep-briefs/**` (the owner's class O),
  `governance/project/orchestration/tools/indep-schemas/**`, or any other test file. Do not edit `tests/acceptance/W2-94/**`
  (the independent test designer's; its suite is written in parallel and the lead merges it into your branch when
  ready; then you make it pass).
- Read: the script's docstring and `check_args`, `resolve_brief`, `plan_inputs`, `build_and_run`, `check_result`,
  `copy_numbers`, `deliver` (the writer branch), `pack`, `choose_run`, `finish`. The fake-session test seam for your
  unit tests: `tests/unit/orchestration/test_w2_149_indep_launch.py` (`World`, `w.launch`, `w.args`, `w.plant_set`,
  `nothing_built`, `writer_out`), reused by `test_w2_173_indep_launch.py` and `test_w2_178_indep_launch.py` (import from
  `test_w2_149_indep_launch`).
## The fix flow's interface (the ticket's S6-S12, made exact by the lead; the test designer and the engineer work from this same text)

Script: `governance/project/orchestration/tools/indep_launch.py`. Names below: `<root>` the sets root, `<set>` the
`--set` name, `<runs>` the runs dir (`GOV_INDEP_RUNS_DIR`, default `~/gov-os-runs`), `<walls>` = `<root>/indep-walls`,
`<setdir>` = `<root>/fixtures/evaluation/<set>`.

1. **Flags (S6).** `--fix <id> --reason <code>`. Valid only together, only with `--kind writer --round 2`, never with
   `--counts-only`. `<id>` fully matches `q[0-9]{2}`. `<code>` is exactly one of `SOURCE_IS_SCAFFOLD`,
   `SOURCE_PATH_ABSENT`, `SOURCE_NOT_TEXT`, `SPAN_OUT_OF_FILE`, `HEADING_NOT_FOUND`, `ANSWER_NOT_IN_SPANS`,
   `NONEXISTENT_NAME_FOUND`, `NONEXISTENT_NO_NAME`. Any other form (either flag alone, another kind, round 1 or no
   `--round`, a bad id such as `q2`, `Q02`, `q002`, `q0a`, an unknown or lower-case code) exits **17** with nothing built:
   no wall, no tree, no run folder under `<runs>/indep/`, no SEEDS.log line (the existing `nothing_built` state).
2. **The brief's front matter (S10).** A fix run accepts the approved variant's front matter as written: it names
   `kind: writer`, `version`, `variant_of`, `rounds: 1`, `tools`, `model`, `effort`, `result_schema`, `budget_usd`,
   `timeout_s`, and **no `sample:`**. In a fix run a front matter without `sample:` is accepted (the wall's own
   `input/selection.json`, a fixed file, then has an empty `sample`); `rounds` and `variant_of` are not judged. The
   brief is still checked as today: its bytes at `--commit` equal `--brief-sha256`, and the sets root's
   `indep-walls/APPROVED` has its `brief` line for kind writer (else 10). Without `--fix` nothing about front matter
   changes.
3. **Staging (S7, F4).** Read and checked before anything is written (a refusal here is **10** with nothing built):
   - `input/<id>.yaml`: a byte copy of `<setdir>/hidden/<id>.yaml`; absent, a folder, or a link (the file or any folder
     on its way) refuses 10.
   - `input/verdict.txt`: exactly the bytes `<id> <code>\n` (one line, one trailing newline).
   - `input/sample.json`: a JSON object `{"sample": [...]}` whose list is, in order, the `sample` list of
     `input/selection.json` as staged in the **latest delivered round-1 writer run of the same set**. Found thus: every
     `<runs>/indep/writer/<rid>/counts.json` whose object has `"status": "delivered"`, `"round": 1`, `"set": <set>`
     (and `<rid>` matching the script's run-id form for that set and round 1); the latest is the greatest `<rid>` (the
     run id starts with its UTC time). That run's own record is its archive `<walls>/writer/<rid>.tar`; the list is read
     from its member `<rid>/input/selection.json` (a regular member, size-capped, parsed strictly; its `sample` a list
     of strings). No such run, no archive, no member, or a member that does not parse to that form refuses 10. Tests
     compare the parsed object, not the bytes.
   - Nothing else of the set or the sets root is staged: no `input/set/`, no `input/notes.md`, no other question, no
     `DRAW.txt`, no `XCHECK-r*.md`. The wall after staging holds exactly the 7 fixed files (`seed.txt`, `brief.md`,
     `CLAUDE.md`, `WALL.json`, `input/selection.json`, `.claude/settings.json`, `.claude/wall_hook.py`), these three,
     and an empty `out/`.
4. **Delivery (S8, F5).** After the session, `out/` may hold only `out/<id>.yaml`, `out/result.json` and (only on a
   stop) `out/conflicts.md`; any other entry (another file, a folder, a link) refuses **20**. `out/<id>.yaml` must be a
   regular file (not a link) whose YAML parses (safe load) to a mapping with `id` equal to `<id>`, else 20. On delivery
   only `<setdir>/hidden/<id>.yaml` is replaced by `out/<id>.yaml`'s bytes; every other entry under `<setdir>` (both
   halves, `hidden/visible/`, `visible/`, `DRAW.txt`, `hidden/dropped/`, any `XCHECK-r*.md`, `.release-visible.record`)
   is byte-unchanged and no entry is added (no temporary name left). The replaced file is packed into the run's
   archive `<walls>/writer/<run>.tar` as the member `<run>/replaced-hidden/<id>.yaml` (the existing `replaced-hidden`
   folder of `pack()`), and is not left anywhere under `<setdir>`. Every refusal (20, 21, or any other code) leaves
   every file under `<setdir>` byte-unchanged, `hidden/<id>.yaml` included.
5. **The result (S9).** `out/result.json` is the writer schema's (`questions`, `by_kind`, `by_area`, optional
   `stopped`) plus `action`, one of `corrected` or `replaced`. A result whose `stopped` is present and not `none`
   delivers nothing: **21** (as today). Otherwise each of these refuses **20**, nothing delivered: `action` absent or
   another word; `questions` not exactly the integer 1; the numbers of `by_kind`, or of `by_area`, not summing to 1;
   the schema failing.
6. **The counts (S9, F4).** A fix run's counts object (stdout's last line and `counts.json`) carries
   `"fix": {"id": <id>, "code": <code>, "action": <action>}`, where `action` is the result's word once the result has
   passed its checks and `null` otherwise; nothing of the question's content (no question, answer, path, span or
   heading text) appears anywhere in the counts, the launch log or stdout/stderr. A run without `--fix` has no `fix`
   key (S12). Known gap, carried by the lead as a package: `indep-schemas/indep-counts.schema.json` is closed
   (`additionalProperties: false`) and outside the ticket's paths, so a fix run's counts do not validate against it;
   do not assert that schema on a fix run's counts (assert the keys and values instead), and do not edit the schema.
7. **The usage line (S11).** The script's docstring gains one usage line for the fix flow, naming only `--sets-root
   <root>` as a path, in the form of the existing lines, e.g. `python3 governance/project/orchestration/tools/indep_launch.py
   --sets-root ~/gov-os-eval --kind writer --brief <path> --brief-sha256 <sha> --commit <commit> --set examin --round 2
   --fix q02 --reason ANSWER_NOT_IN_SPANS`.
8. **Unchanged (S12, F6).** Without `--fix`, every existing flow behaves exactly as before; `governance/project/indep-walls/**`,
   `governance/project/indep-briefs/**` and `indep-schemas/**` are not changed. The variant runs at sha256
   `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`, byte for byte.

## Your unit tests
`tests/unit/orchestration/test_w2_94_fix_flow_unit.py`: the argument refusals (17, nothing built); the three staged
inputs and the wall's file list on a `--dry` run; the sample read from the latest delivered round-1 run's archive; a
good delivery replacing only `hidden/<id>.yaml` (sha256 of every other planted set file unchanged; the archive's
`<run>/replaced-hidden/<id>.yaml`); one refusal each at delivery (20) and the stop (21) leaving the set unchanged; the
counts' `fix` key; the variant's front matter (no `sample:`) accepted. Keep it compact.

## Order of work
1. Implement; add the unit tests; run them, and run the three existing launcher suites unchanged (S12):
   `tests/unit/orchestration/test_w2_149_indep_launch.py`, `test_w2_173_indep_launch.py`, `test_w2_178_indep_launch.py`.
2. Commit (your two paths only).
3. Write `/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/en-1.between` with one line `between` when
   you are between batches (after the commit), and check every few minutes for the file
   `/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/TESTS-READY`. Do not wait more than 25 minutes
   for it: if it has not appeared, return with what you have. When it appears (it names the merge commit; it is in your
   branch then; never run git merge yourself), run `tests/acceptance/W2-94/test_w2_94_fix_flow.py` and make it pass by
   changing the script only. If a case cannot pass without going beyond the interface above, or the case and the
   interface disagree, stop and name the case; do not widen the change and do not edit the case.
4. Commit again if you changed anything.

Pytest, every run (if the slot tool cannot run in your sandbox, run the same pytest without it and say so; a resource
gate's refusal is a wait, not a refusal):
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
Use your sandbox's own `$TMPDIR` for every temporary file.

## Walls (hard)
- Planted fixtures only. Never open, list, grep or print anything under `/home/usain/gov-os-eval/`,
  `/home/usain/gov-os-runs/`, any folder named `hidden` outside a test's `tmp_path`, or any
  `fixtures/evaluation/examin/visible` or `hidden` folder. You need none of them. No real `claude` session.
- No GPU, model, network or installs. One simple command per Bash call; longer things in a script file under your
  sandbox's `$TMPDIR` (`/tmp` is read-only in the sandbox). No merge. No `gov retrieve` or `gov context`: search with
  Read and Grep, and search again once in different words if the first does not answer.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Commit
Your paths only, every trailer in ONE final paragraph (the `--trailer` flags do that):
`git commit -m "W2-94 (DAEO-g87r): <subject>" --trailer "Task: DAEO-g87r" --trailer "Role: engineer" --trailer "Implements: DEC-1180, DEC-1178, DEC-820" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- governance/project/orchestration/tools/indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py`

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (each
suite's pass/fail counts and the commit hashes), tests, discoveries (any point where the interface and the code or the
variant disagree), risks, lessons, proposed_decisions, unresolved, recommended_next_action.
