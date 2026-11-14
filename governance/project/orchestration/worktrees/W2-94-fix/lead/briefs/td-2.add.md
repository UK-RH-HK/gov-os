
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
