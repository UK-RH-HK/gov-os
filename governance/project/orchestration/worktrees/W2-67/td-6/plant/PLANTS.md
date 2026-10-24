# W2-67 run 3, batch 6: the plants (DAEO-9nys, independent test designer, 2026-10-24)

Branch `w2/W2-67` from `6d44fc80`; code under test this worktree's `src/` (DEC-732). Commit ids here are 12 digits
(row W2-L423's rule); the JUnit XML files had their ids shortened the same way after the runs (`shorten_ids.py`).

## Carrier

- `td6_plant_plugin.py` (pytest plugin, `-p td6_plant_plugin`, this folder on `PYTHONPATH`): wraps
  `w1_30_support.sandbox_env` so each `gov` process a W1-30 case starts has `site/` first on its `PYTHONPATH`, and
  passes `GOV_TD6_PLANT` and `GOV_TD6_MARKER` on.
- `site/sitecustomize.py`: a meta-path finder applies the named fault to `gov.close.command` or `gov.close.state` as
  the module loads, and appends a line to the marker file each time the planted behaviour runs. `gov close` gives
  its nested test runs `PYTHONPATH=<project>/src` only, so the plant lives in the `gov close` process.
- `td6_guard_plant.py` (pytest plugin, `-p td6_guard_plant`): piece 3's plants (KPI 4's static guard).
  `fstring_basetemp_source.py`: the planted source it adds.
- `probe.py`: builds one case's project in a temporary folder and prints the close's answer (used to read the head).

## The faults

| Plant | The fault, in words | How |
|---|---|---|
| PF1 | `DISPOSITIONS` loses `owner` | module constant replaced; `run` wrapped to mark `--disposition owner` |
| PF2 | a refusal with a class no longer carries `details["context"]` | `_refuse` wrapped: drops the key, marks; marks too when the key is absent |
| PF2b | a refusal with a class given a fallback context hash (sha256 of the ticket file) when no context was built | `_refuse_for` wrapped |
| PF4 | containment returns before it judges | `_check_containment` replaced |
| PF5 | the acceptance run is never made and reports one pass | `_check_acceptance` replaced |
| PF9 | the packet hash a constant (64 zeros) | `_build_context` wrapped |
| PF10 | the decision checker's findings never read when an owner decision lifts an escalation | `state.lift_escalation` wrapped: `gov.decisions.check` returns `[]` within it, after asking the real checker |
| PF11 | the regression run stops at its first failure | `_one_test_run` and `_told_run` wrapped: `--maxfail=1` added to a run with `--ignore` |
| PF12 | a failing regression refuses nothing | `_check_tests` wrapped: the regression's `_Finding` dropped, its counts returned |
| PF13 | the trailer gate judges nothing | `_check_trailers` replaced |
| PF15 | a ticket's commits matched by substring of `Task:` | `repo.ticket_commits` and `command._ticket_commits` replaced |
| PF16 | the regression is never run and counts nothing | `_check_tests` wrapped: zero counts for a run with `ignore` |

## Commands

    cd <worktree>
    GOV_TD6_PLANT=<plant> GOV_TD6_MARKER=<this folder>/<before|after>-<plant>.marker \
    PYTHONPATH=<worktree>/src:<worktree>/.gov-runtime/scratch/td-6/plant \
      python3 -m pytest -p td6_plant_plugin -p no:cacheprovider -o tmp_path_retention_policy=failed -q --no-header \
      -n 3 -rA --junitxml=<this folder>/junit/<before|after>-<plant>.xml <node ids>

    GOV_TD6_GUARD_PLANT=<other|refusal-0..5> PYTHONPATH=<worktree>/src:<this folder> \
      python3 -m pytest -p td6_guard_plant -p no:cacheprovider -o tmp_path_retention_policy=failed -q -p no:xdist \
      tests/acceptance/W1-27/test_w2_67_temp_folders.py::test_no_source_of_round_1_passes_a_per_run_basetemp_or_changes_the_retention

## Results

- `before-*`: the 13 cases as they stood, each under its plant: all passed (weak). Markers: PF1 and PF10 none (no
  close was run; the checker was never asked); PF2 "the planted line is not on this path (code CHECK_FAILED)"; PF4 and
  PF5 one line each, from the green case only (the refusal cases stopped at the missing checkpoint); the others one
  line per close.
- `after-*`: the revised cases, each under its plant: every one failed (red), with a marker line from its own close;
  PF2 alone passed (its line is off the path since DEC-868 item 3), and the case is red under PF2b.
- `head-close-10.xml`, `head-other-4.xml`: the revised cases green on the head; `head-w1-30-six-files.xml`: the six
  W1-30 files changed, whole, 133 passed; `td4a-*.xml`: piece 3 (head green, `other` red; the two W1-27 files whole,
  18 passed).
- `w2-l420-checker-shallow-probe.txt`: the checker case's project on the head: W1-11's checker raises
  `DECISIONS_OBJECT_UNREADABLE`, `gov check` exits 0, `gov context` answers, the close runs both test runs and is
  refused `CONTEXT_FAILED`, count 1.
