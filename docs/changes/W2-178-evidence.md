# W2-178 evidence: the auditor's copy of a set leaves out its dropped questions

Ticket DAEO-7oxm, class C2, profile FULL. Engineer: Sonnet 5.5. Base `03393ee51`. Sources: DEC-1101 (2), DEC-820 (b), (d),
DEC-1052, DEC-1120; W2-170's Interface (`packages/MEMORY-AUDIT-1.md`).

## The change

`governance/project/orchestration/tools/indep_launch.py`, `plan_inputs()`, inner `set_copies()` (lines 780-781): after
`plain_files(hidden)` has listed the set (a link or a non-file anywhere still raises, so refuses 10 `input`), an auditor's
list drops every relative path that starts with `dropped/`; the existing empty check follows, so a set empty after the
exclusion refuses 10 `input` as an empty set does. Module docstring: one paragraph (lines 38-40) naming the rule. Six
inserted lines in all; no other line of the script changed.

## KPI lines

| KPI line | implemented by | shown by (tests/unit/orchestration/test_w2_178_indep_launch.py) |
|---|---|---|
| S1 the auditor's copy has every file except those under `hidden/dropped/`; every other kind's copy is unchanged | `set_copies()` lines 780-781 (the filter is for `kind == "auditor"` only); the checker and the writer round 2 take the unfiltered list | `test_the_auditors_plan_leaves_out_every_file_under_hidden_dropped_at_any_depth`; `test_the_auditors_other_files_are_the_sources_as_before_and_misses_still_staged`; `test_the_auditors_wall_copy_has_no_dropped_file_and_every_other_file_byte_identical` (a dry auditor build, wall copy compared byte for byte with the planted files); `test_the_checkers_and_the_writers_round_two_wall_copies_hold_every_file_dropped_ones_too` (dry checker and writer round 2 builds: every file, dropped ones included, byte-identical); `test_the_checkers_plan_and_the_writers_round_two_plan_keep_the_dropped_files`; `test_a_set_with_no_dropped_folder_stages_exactly_as_before` |
| F1 a dropped question reaching an auditor, or any other kind's wall changing | same lines; nested `dropped/x/y/` files are covered by the prefix; the other kinds never reach the filter | the S1 tests above, with `dropped/x/q04.yaml` and `dropped/x/y/q05.yaml` planted; `test_a_dropped_folder_below_another_folder_and_a_name_that_only_starts_with_dropped_stay` (`sub/q03.yaml`, `sub/dropped/q06.yaml`, `dropped.yaml` still staged) |
| F2 no session or test opens the real sets root, a hidden half or the held-out material | no code change touches it; every test plants its sets root under `tmp_path` (W2-149's `World`), HOME and the repository likewise; the stub `claude` stands in for the session | the whole file; grep of it for the real root's path: 0 lines (the path is never written in it) |
| F3 no change outside the allowed paths | the ticket's three paths only | `git diff --name-only 03393ee51` lists `governance/project/orchestration/tools/indep_launch.py`, `tests/unit/orchestration/test_w2_178_indep_launch.py`, `docs/changes/W2-178-evidence.md` |

Refusals that keep their meaning (tests): `test_a_link_inside_the_dropped_folder_still_refuses_10_input_for_the_auditor`,
`test_a_linked_folder_inside_the_dropped_folder_still_refuses_10_input_for_the_auditor`,
`test_an_auditors_set_of_only_dropped_files_refuses_10_input_as_an_empty_set_does`,
`test_the_auditors_set_of_only_dropped_files_builds_nothing_10` (nothing built; the sets root's tree unchanged).

## The lead's readings (the brief's), as built

1. "Under the folder `dropped/`" is the first path component `dropped` with at least one component below it, at any depth
   below it. A plain FILE named `hidden/dropped` is not under the folder: it stays staged
   (`test_a_plain_file_named_dropped_is_not_the_folder_and_stays`). A file `dropped.yaml` and a folder `sub/dropped/` are not
   `hidden/dropped/` either and stay staged.
2. A set empty after the exclusion refuses 10 `input` (the counts' `reason` word for code 10 is the same for every cause).
3. The links check runs before the exclusion, over the whole `hidden/` tree, the dropped folder included.
4. The set-up A flows (the overlap auditor goes through `plan_sgx`) are not touched.

## Diff

`git diff --stat 03393ee51 -- governance/project/orchestration/tools/`

```
 governance/project/orchestration/tools/indep_launch.py | 6 ++++++
 1 file changed, 6 insertions(+)
```

## Runs (through the heavy slot, TMPDIR under the launch folder: /tmp/w2-178-eng is read-only in the sandbox)

The exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"` left out the real-model cases.
See the return's evidence line for each summary.
