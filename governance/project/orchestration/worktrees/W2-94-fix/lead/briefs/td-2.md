# W2-94 fix flow — acceptance cases for the launch script's one-question fix flow, the independent test designer's brief (DAEO-g87r)

You are a fresh independent test designer (class C2) under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; read its "Reopened 2026-11-14" paragraph and KPI
lines S6 to S12 and F4 to F6). The owner decided **DEC-1180 (2)** (P-Q02-RUN-1 (a), "run today, as soon as it is built
and reviewed"): the walled launch script `governance/project/orchestration/tools/indep_launch.py` gains a one-question
fix flow on the writer's round 2, so the owner's approved writer variant for hidden question q02 (DEC-1178 (5)) runs
byte for byte unchanged. You write the acceptance cases **from the KPI lines and the interface below, as described
behaviour (DEC-136)**. An engineer changes the script in parallel; you do not read its branch or its work.

**Speed matters:** the owner's operator runs q02 today once this lands. Write a tight suite that checks each line once,
well; no case beyond S6 to S12 and F4 to F6.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-94-fix-tests`, branch `w2/W2-94-fix-tests` (at `340cd0efb`). Write only
  **new** files under `tests/acceptance/W2-94/`: `test_w2_94_fix_flow.py`, and a support file
  (`w2_94_fix_support.py`) if you need one, plus a byte copy of the approved variant as a fixture
  (`tests/acceptance/W2-94/fixtures/EXAMIN-writer-q02-fix.md`; copy it from
  `/home/usain/gov-os-worktrees/W2-94-fix-tests/.gov-runtime/scratch/variant/EXAMIN-writer-q02-fix.md` and have a case
  assert its sha256 is `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`). Leave every existing W2-94
  test file unchanged, except `tests/acceptance/W2-94/README.md`, where you add one map row per KPI id you cover
  (S6, S7, S8, S9, S10, S11, S12, F4, F5, F6) in the existing table's form: a row's KPI cell names only this ticket's
  line, its tests cell names `<file>::<test>` ids, and the red reason against the unchanged script.
- Read first: the script's docstring (top of `indep_launch.py`) and only as much of its code as you need to know its
  command-line interface, exit codes and file layout (`check_args`, `plan_inputs`, `build_and_run`'s order, `deliver`'s
  writer branch, `pack`, `choose_run`); then the existing **fake-session test seam**: `tests/unit/orchestration/test_w2_149_indep_launch.py`
  (`World`: a planted sets root, HOME, repository with the walls' template and an APPROVED list, and a stub `claude`
  driven by a JSON config; `w.launch(...)`, `w.args(...)`, `w.plant_set`, `nothing_built`, `writer_out`), and how
  `tests/unit/orchestration/test_w2_173_indep_launch.py` and `test_w2_178_indep_launch.py` reuse it (import from
  `test_w2_149_indep_launch`; you may import it the same way, putting `tests/unit/orchestration` on `sys.path` in your
  support file). Do not change those unit files.
- A delivered round-1 run for the sample: plant it as the interface's item 3 says (a `counts.json` under
  `<runs>/indep/writer/<rid>/` and the archive `<walls>/writer/<rid>.tar` holding `<rid>/input/selection.json`), either
  by writing those planted files directly or by running a planted round-1 writer launch through the stub; plant two
  delivered round-1 runs with different samples and one non-delivered later one, so "the latest delivered" is tested.
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

## What the cases must show (one test or a parametrized table per line; each must be red against the unchanged script)
- **S6:** each wrong form of item 1 exits 17 with nothing built (no wall, no run folder, no seed line): `--fix` alone,
  `--reason` alone, `--kind checker`/`auditor` with both flags, round 1 and no `--round`, `--counts-only` with them, bad
  ids, an unknown code, a lower-case code. One good form passes the argument stage (it may be refused later for a
  planted reason; that is fine to show it is not 17).
- **S7 / F4:** a planted set of several questions (at least 5 in `hidden/`, some in `hidden/visible/`, a
  `hidden/dropped/` file, `DRAW.txt`, an `XCHECK-r1.md`, a `visible/` folder and `.release-visible.record`), each file
  holding a unique planted content marker; a `--dry` fix run on the planted root (`--seed` allowed with `--dry`): the
  wall's file list is exactly item 3's, `input/<id>.yaml` equals the set's bytes, `verdict.txt` is `<id> <code>\n`,
  `sample.json` parses to the latest delivered round-1 run's sample in order; no other marker is anywhere in the wall.
  The staging refusals: `hidden/<id>.yaml` absent, a link, a folder; no delivered round-1 run; its archive missing;
  its member missing or malformed: each 10 with nothing built.
- **S8 / F5:** with the stub session writing into `out/`: sha256 of every planted file under `<setdir>` before and
  after; a good fix run (exit 0) changes only `hidden/<id>.yaml` (now `out/<id>.yaml`'s bytes) and the archive holds
  the old bytes at `<run>/replaced-hidden/<id>.yaml`; each delivery refusal is 20 and leaves every set file
  byte-unchanged: an extra file in `out/`, a folder in `out/`, `out/<id>.yaml` absent, a link, not YAML, not a
  mapping, its `id` another id.
- **S9:** results refused 20 (no `action`, another word, `questions` 0 or 2, `by_kind` summing to 2 or 0, `by_area`
  summing to 2 or 0); a stopped result (with `out/conflicts.md`) is 21, nothing delivered; on delivery the counts'
  `fix` is `{"id": "q0N", "code": <code>, "action": <word>}` for each of `corrected` and `replaced`; a grep of stdout,
  stderr, `counts.json` and `launch.log` for every planted content marker finds 0.
- **S10 / F6:** the end-to-end run with the variant fixture committed byte for byte into the planted repository at its
  approved path (`governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md`) and approved in the planted
  APPROVED list: `--fix q02 --reason ANSWER_NOT_IN_SPANS`, the stub delivering a good `out/q02.yaml` and result: exit 0,
  the delivered file in place, `brief_sha256` in the counts equal to the approved sha256.
- **S11:** the script's docstring holds a usage line with `--fix` and `--reason` naming only `--sets-root <root>` as a
  path; and `git diff --name-only <base>...HEAD` of the branch under test names no path under
  `governance/project/indep-walls/`, `governance/project/indep-briefs/` or `governance/project/orchestration/tools/indep-schemas/`
  (take the base as `git merge-base HEAD w2/integrate` in the repository the test runs from; skip with a clear reason
  if that ref is absent).
- **S12:** a planted writer round-2 run without `--fix` still stages `input/set/` and `input/notes.md` and replaces the
  whole hidden folder as today, and its counts have no `fix` key (the existing unit suites are the main check; the lead
  runs them).

Do not assert the counts schema (`indep-counts.schema.json`) on a fix run's counts (item 6's known gap); assert keys
and values.

## Walls (hard; a breach fails the ticket)
- **Planted fixtures only.** Never open, list, grep or print anything under `/home/usain/gov-os-eval/`,
  `/home/usain/gov-os-runs/`, any folder named `hidden` outside your `tmp_path`, any `fixtures/evaluation/examin/visible`
  or `hidden` folder of any tree, EXAMIN's real repository or the owner's copy. You need none of them. Every word you
  plant is made up and carries the planted prefix `zqxw94`, as the existing W2-94 cases do.
- No GPU, model, network or installs; no real `claude` session (the stub only). One simple command per Bash call;
  longer things in a script file under your sandbox's `$TMPDIR` (`/tmp` is read-only in the sandbox). No merge inside
  the sandbox. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in different words if
  the first does not answer.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Order of work
1. Write the cases; run them against the unchanged script; every case must be red (or, for an S12 guard case, green),
   and record which and why.
2. Commit (only your new files and the README rows), every trailer in ONE final paragraph:
   `git commit -m "W2-94 (DAEO-g87r): the fix flow's acceptance cases (S6-S12, F4-F6)" --trailer "Task: DAEO-g87r" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1180, DEC-1178, DEC-820" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-94`
3. Name, for S7, S8 and S9, one planted break of a correct fix flow that a case would catch (by reading; no script
   copy needed).

Pytest, every run (if the slot tool cannot run in your sandbox, run the same pytest without it and say so; a resource
gate's refusal is a wait, not a refusal):
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94/test_w2_94_fix_flow.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=line`
Use your sandbox's own `$TMPDIR` for every temporary file.

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (the red
run's counts and the commit hash), tests, discoveries (any point where the interface is unclear or the KPI and the
interface disagree), risks, lessons, proposed_decisions, unresolved, recommended_next_action. Never quote a planted
hidden question or answer beyond its made-up marker.

## The lead's answers to the first designer's points (a first session stopped before writing; its design is below; build on it)

- **The variant fixture.** The first session's `cp` by Bash was refused twice by the headless harness's permission
  prompt (not a guard rule). Do not use Bash to copy it. Write the file with the **Write tool** (the documented form
  for files in this repository): `/home/usain/gov-os-worktrees/W2-94-fix-tests/tests/acceptance/W2-94/fixtures/EXAMIN-writer-q02-fix.md`,
  its content exactly the text of `/home/usain/gov-os-worktrees/W2-94-fix-tests/.gov-runtime/scratch/variant/EXAMIN-writer-q02-fix.md`
  (Read it, then Write the same text; it ends with one newline). Then check it with one simple command,
  `sha256sum tests/acceptance/W2-94/fixtures/EXAMIN-writer-q02-fix.md`: it must be
  `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`. If the sha differs, do not commit the fixture:
  make S10's case read the variant from the path in env `W2_94_VARIANT` and skip with a clear reason when it is unset,
  and say so in your return. If the Write is refused, stop and say so.
- **S6's bad forms are green today** (argparse already refuses the unknown option with 17): pair each with a control as
  you proposed (the good form's `--dry` run is not 17), or assert the bad form's 17 *and* that the same run with the
  form corrected reaches past the argument stage. Every case must be red against the unchanged script.
- **`fix.action` on a delivery refusal of item 4** (an extra file in `out/`, etc.): do not assert it. Assert `action`
  `null` on item-5 result refusals and on 21, the word on delivery.
- **A dry run's counts:** assert `fix` present as `{"id": <id>, "code": <code>, "action": null}`.
- **Links:** plant them from the `GOV_INDEP_TEST_HOOK` `after_session` hook, as the W2-149 cases do; if that seam
  cannot plant one, drop that one sub-case and say so.
- **S11 and S12 together.** S12 requires `test_w2_149_indep_launch.py` to pass unchanged; its
  `test_documented_lines_name_only_the_sets_root` counts exactly 10 docstring lines that start with `python3 `, and
  `test_help_offers_exactly_the_options_and_no_path_list` pins the `--help` option set. So the engineer will (1) write
  the fix flow's usage line in the docstring so that it does **not** start with `python3 ` after stripping (for
  example a line starting `The fix flow: python3 governance/...`), with real values, no `<`, `>`, `$`, `*`, `?`, `[`,
  `{`, `|`, `;`, `&` or backquote, and (2) keep `--fix` and `--reason` out of `--help`'s option list. Your S11 case:
  the docstring has exactly one line holding both `--fix` and `--reason`; it names `--sets-root` with a value that is
  not a folder under it (no `indep-walls/` in it), holds none of those characters, and holds `--kind writer` and
  `--round 2`; do not require it to start with `python3 `, and do not require `--fix` in `--help`.

The first session's design (use it): a `FixWorld` over `World`: set `examin` with q01-q06 in `hidden/`, q07/q08 in
`hidden/visible/`, a `hidden/dropped/` file, `DRAW.txt`, `XCHECK-r1.md`, `visible/` and `.release-visible.record`,
each with its own `zqxw94-...` marker; the variant committed at its approved path with an APPROVED `brief writer` line;
planted runs: an old delivered round-1 run, the latest delivered round-1 run (three samples, unsorted), a newer
rejected round-1 run, a newer delivered round-2 run and a newer delivered round-1 run of another set; a snapshot of the
sets root, the runs dir and the trees dir to prove "nothing built". Planted breaks it named: S7 the sample taken from
the latest run of any status, round or set; S8 the whole `hidden/` replaced or a temporary file left; S9 only the type
of `questions` checked, `by_kind` with one entry accepted whatever its number, or `yaml.load` (a `!!python/object` case).
