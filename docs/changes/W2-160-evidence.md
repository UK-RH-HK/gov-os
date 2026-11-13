# W2-160 evidence: `gov wait` and `gov session-watch helper-watch`

Ticket DAEO-fd0p (profile STANDARD, class C2). Sources: DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1119, DEC-1109.

## What was built

- `src/gov/wait/` : `command.py` (`gov wait <exit-file> [<max-s>]`, `CLASS = "read"`, `CHILD_EXIT_CODE = True`),
  `liveness.py` (the one liveness function: a signal 0 to the pid, a `/proc/<pid>/stat` state of `Z` counts as gone;
  shared with the helper watch), `__init__.py` (package docstring with the KPI map).
- `src/gov/session_watch/helper_watch.py`: the helper watch (I2 as written in the ticket).
- `src/gov/session_watch/command.py`: the `helper-watch` action beside `stop-check` (its five options, one call to
  `helper_watch.run`) and `.gov-runtime/dispatch/inbox/**` in `ACT_PATHS`; `stop-check` unchanged in behaviour.
- `src/gov/check/commands.py`: `wait` added to `RECORDED_GOV_COMMANDS` (one line).

## KPI map

| KPI | code | tests |
|---|---|---|
| S1 bounded wait, 570 cap, tail, codes | `wait/command.py` `run`, `_tail` | acceptance `test_s1_wait.py`; unit `tests/unit/wait/test_command.py` |
| S2 liveness by pid alone, 125 GONE, 2 usage | `wait/liveness.py`, `wait/command.py` | acceptance `test_s2_gone.py`; unit `test_liveness.py` (zombie, pid-file forms) |
| S3 one item per condition, once | `helper_watch.py` `_helpers`, `_workers`, `_pass`, `_item` | acceptance `test_s3_helper_watch.py`; unit `test_w2_160_helper_watch.py` (name collision `-<n>`, window and stale edges, empty exit file, second pass, configuration error) |
| S4 names only; no process-name match; writes only inbox, state, log | `helper_watch.py` `_name`, `_describe`; no temporary or lock file | acceptance `test_s4_reads_and_writes.py`; unit text-canary case |
| F1 wait never outlives its bound / waits for a gone process | sleep cut to the time left; gone pid seen at the next poll | S1 and S2 cases above |
| F2 no process matched by name, no message text copied | same as S4 | S4 |
| F3 the same condition never written twice | state file keys only grow | S3 second-pass cases |
| F4 only the ticket's paths | see `files_changed` of the return | branch diff against the base |

S2's "as `gov launch` writes it": `gov launch` in this tree writes no `<base>.pid`; the `<base>.pid`, `<base>.exit` and
`<base>.json` names are `launch_worker.sh`'s (the ticket's facts line). The tests plant the files.

## Runs (through the heavy slot, empty HOME, `-m "not local_only" -k "not real and not green_here and not time_limit"`)

- `tests/acceptance/W2-160`: `66 passed in 10.26s`
- `tests/unit/wait`: `14 passed in 0.52s`
- `tests/unit/session_watch`: `1 failed, 58 passed in 1.01s` (the one failure is
  `test_route.py::test_the_command_is_declared_by_its_module`, W2-159's test asserting `ACT_PATHS` is the single
  session-watch path; the ticket requires the inbox path added, and the file is outside this ticket's paths)
- `tests/acceptance/W2-159`: `1 failed, 93 passed in 7.19s` (the one failure is
  `test_f4_scope.py::test_f4_the_branch_changes_only_the_tickets_allowed_paths`, which checks this branch's diff against
  W2-159's own `allowed_paths`; it cannot pass on a later ticket's branch)

The exclusion left out the real-model cases (none exist in these folders).
