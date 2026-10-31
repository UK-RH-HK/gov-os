# W1-30: W2-67's revisions of the first-round cases (DAEO-9nys, run 3, batch 6)

Independent test designer (MR-3), 2026-10-24, on `w2/W2-67` from `6d44fc80`. The ticket's fifth KPI line: "Each weak
case revised is first shown red against a planted fault, then green on the head, each with a Rewrite-Reason; …
W1-30's 13 first-round cases …" (P-IS-7 (a), lens I2 Finding 2 and §2.7). Row W2-L420 (DEC-866): one case and two
module docstrings to DEC-868 and DEC-908.

## The method

**Re-checked first (DEC-718).** On the head, each of the 13 cases was run as it stood under its planted fault (I2's
PF-n): all 13 still passed, so none was already sound. W2-07 had given `test_regression_runs_to_end_all_failures_collected`
its checkpoint, and it still passed under PF11 and PF12: its failing tests were the engineer's, outside the ticket's
paths, so containment refused and named their files whatever the regression did, and one name of two was enough.

**Planting a fault.** `src/` is never written and the tree is never copied. A pytest plugin
(`td6_plant_plugin.py`, `-p td6_plant_plugin`) wraps `w1_30_support.sandbox_env` so that every `gov` process a case
starts has the plant's `site/` folder first on its `PYTHONPATH`; its `sitecustomize.py` applies the one fault
`GOV_TD6_PLANT` names to `gov.close.command` or `gov.close.state` as the module loads, and writes a line to
`GOV_TD6_MARKER` each time the planted behaviour runs. The close gives its nested test runs a `PYTHONPATH` of the
project's `src/` only, so the plant lives in the `gov close` process, where every fault of the table lives. Each run's
marker shows that the planted behaviour ran in the case's own `gov close`. The modules, the markers and the JUnit XML
of every run are under `.gov-runtime/scratch/td-6/plant/` (`before-*` the cases as they stood, `after-*` the revised
cases). A run:

    GOV_TD6_PLANT=PF13 GOV_TD6_MARKER=<plant>/after-PF13.marker \
    PYTHONPATH=<worktree>/src:<worktree>/.gov-runtime/scratch/td-6/plant \
      python3 -m pytest -p td6_plant_plugin -p no:cacheprovider -o tmp_path_retention_policy=failed -q \
      -n 3 --junitxml=<plant>/junit/after-PF13.xml <node ids>

**What every revised case now has.** What every ticket has before its close (its checkpoint; the failing regression
tests are the owner's, committed before the ticket's work, so no containment finding names them), so that it is
refused or closed by the gate it names and not by an earlier one; and an assertion on that gate's own finding or
result (for a success case, that the run was made: a test that tells, into a folder outside the project, each time it
runs, and the run the answer states). No expectation is lowered; each name is kept.

## The 13 cases

| Case | Plant (I2 §2.7) | Before: under the plant | After: red under the plant (seen) | Head | Rewrite-Reason, commit |
|---|---|---|---|---|---|
| `test_w1_30_close.py::test_close_requires_implements_trailer` | PF13: `_check_trailers` judges nothing | passed (refused for the missing checkpoint) | `gov close was not refused`: `ok: true` | green | refused for the missing checkpoint, not for the gate it names; `f7867ea6ac38` |
| `…::test_close_requires_task_trailer` | PF13 | passed | `gov close was not refused` | green | the same; `f7867ea6ac38` |
| `…::test_close_refuses_when_acceptance_tests_fail` | PF5: `_check_acceptance` makes no run and reports one pass | passed (missing checkpoint) | `gov close was not refused` | green | refused for the missing checkpoint or for containment, not for the gate it names; the success cases asserted only ok; `37e8a18760a9` |
| `…::test_close_runs_acceptance_tests` | PF5 | passed (`ok` alone) | `the ticket's acceptance test did not run once in the close: {}` | green | the same; `37e8a18760a9` |
| `…::test_containment_blocks_close_for_out_of_scope_commit` | PF4: `_check_containment` returns before judging | passed (missing checkpoint) | `gov close closed a ticket although W1-50's judgement of its commits has findings (DEC-453)` | green | refused for the missing checkpoint, not for the gate it names; `eae5892e2a4a` |
| `…::test_task_trailer_exact_match_not_substring` | PF15: a ticket's commits matched by substring of `Task:` | passed (missing checkpoint); passed again after DEC-954's merge (marker: 0 commits found), see run 6 below | run 6, on the head's ids: `the refusal does not say that no commit carries Task: PROJ-tkaa` (refused `CONTAINMENT_FINDING`; marker: 1 commit by substring, 0 exactly) | green | the same; `PROJ-a` could have no checkpoint; A is `PROJ-tkaa`, AB `XPROJ-tkaa` (DEC-954), and a commit with `Task: PROJ-tkaab` (no ticket) is the one PF15 can see; `41d0ebde76e9`, then run 6 |
| `…::test_regression_runs_to_end_all_failures_collected` | PF11: `--maxfail=1` on the regression run; PF12: its findings dropped; PF16: no regression run | passed under PF11 and PF12 (containment named the files), PF16 not run before | PF11: `does not name the failing regression tests ['test_reg_1', 'test_reg_3', …]` (2 of 8 counted); PF12, PF16: `gov close was not refused` | green | as for the acceptance cases; `37e8a18760a9` |
| `…::test_regression_failure_blocks_close` | PF12, PF16 | passed under both (missing checkpoint; containment) | `gov close was not refused` under both | green | the same; `37e8a18760a9` |
| `…::test_close_runs_regression_tests_when_present` | PF16 | passed (`ok` alone) | `the regression test did not run once in the close: {}` | green | the same; `37e8a18760a9` |
| `test_w1_30_receipt.py::test_close_record_packet_hash_matches_context` | PF9: the packet hash a constant | passed (`gov context` unread: no store yet) | `packet_hash '000…0' must match context hash '16f092641442…'` | green | accepted any string when the context could not be read; `a460820311ee` |
| `test_w1_30_iteration.py::test_owner_decision_checker_failing_refuses` | PF10: the checker's findings never read in the lift | passed, no marker: the checker was never asked | `expected exit code 4`: lifted (marker: 1 finding not read), then refused by the pre-close gate, exit 3 | green | refused before the checker was asked; `f0c9c4d46e36` |
| `test_w1_30_disposition.py::test_all_six_dispositions_recognized` | PF1: `DISPOSITIONS` loses `owner` | passed, no marker: no `gov close` was run | `{'owner': {'exit': 1, 'code': 'INVALID_DISPOSITION', 'recorded': []}}` | green | it read the support's constant; `a4b39e7e68a4` |
| `test_w1_30_disposition.py::test_disposition_with_context_failure` | PF2b (see below): a fallback context hash given to a refusal with a class | passed under PF2 | PF2b: `the repair ticket carries a context hash although no context was built` | green | asserted only the absence of a literal the close never writes; `515ab9874cb0` |

**The disposition case and PF2.** I2's PF2 drops `details["context"]`, which the close sets only for its own context
step's finding (`CONTEXT_FAILED`). Since W2-07 (DEC-868 item 3) the pre-close `gov check` finds the case's broken
context first (`core-authority` and `core-graph` RED for the two decisions that supersede each other) and refuses at
once, so PF2's line is never reached on the head: under PF2 the revised case passes, and the marker says `_refuse
reached without details['context'] (code CHECK_FAILED)`. The revised case holds what DEC-868 leaves of its docstring:
the refusal names the two decisions, the class is recorded, and neither the answer nor the repair ticket carries a
hash. It is shown red against PF2b, a fault of that last claim.

**Not the batch's, left unchanged:** `test_w1_30_close.py::test_close_runs_containment_check`, whose retirement
(P-I2-5) is undecided. Under PF4 it still passes (`before-PF4.xml`).

## Row W2-L420 (DEC-866)

- **The two module docstrings** (`test_w1_30_governance_checks.py`, `test_w1_30_context_failures.py`) now state
  DEC-868 and DEC-908: the checks run on every close and are the pre-close gate, a red check or a broken context is
  refused at once, before any test, not counted; `Rewrite-Reason: DEC-868 item 3 and DEC-908 (DEC-455 and DEC-480
  changed)`, `a0325f527f06`. No assertion changed.
- **`test_w1_30_context_failures.py::test_a_decision_checker_that_cannot_run_refuses_the_close` is not revised**
  (package P-W2-67-TD6-1 in the designer's return). In its shallow clone W1-11's checker raises
  (`DECISIONS_OBJECT_UNREADABLE`), but `gov context` builds and `gov check` exits 0 (`core-authority` among its green
  checks), so the pre-close gate does not see it: the close runs both test runs and refuses at its own context step,
  `CONTEXT_FAILED`, counted (count 1). DEC-908 changes DEC-455's counting for "a broken context [that] turns
  context-reproducibility RED"; here that check is green. Which refusal and exit DEC-868 gives a checker that cannot
  run is the package's question; the case keeps its counted refusal until it is answered.

## Runs (this worktree's `src/`, `-o tmp_path_retention_policy=failed`)

- The batch's 15 cases as they stood, on the head: 15 passed. Under their plants: all 13 passed (`before-*.xml`).
- The revised cases on the head: 9 + 4 passed (`head-close-10.xml`, `head-other-4.xml`). Under their plants: every
  one failed as in the table (`after-*.xml`).
- The six W1-30 files changed, whole, on the head (`-n 4`): 133 passed in 161.6 s (`head-w1-30-six-files.xml`).

## Run 6: the merge of W2-64's ids (repair batch)

**What the merge lowered.** The merge of `w2/integrate` (`0568d91baf56`, DEC-954) gave
`test_task_trailer_exact_match_not_substring` W2-64's schema-valid ids: A `PROJ-tkaa`, AB `XPROJ-tkaa` (A's id with
one character in front). The close finds a ticket's commits with git's fixed-string search for `Task: <ticket>`, and
`Task: XPROJ-tkaa` does not hold the text `Task: PROJ-tkaa`, so AB's commit is never found and PF15's substring match
never sees it: on the head the case passed under PF15. Under the ticket schema no valid id is another valid id with
more characters after it, so no pair of tickets can show PF15.

**How it was found.** A reviewer ran the case under td-6's PF15 plant on the head: 1 passed, the marker saying 0
commits found. Seen again here through td-6's carrier, the marker in `.gov-runtime/scratch/td-10/`:
`commits of PROJ-tkaa matched by substring: 0, of them exactly: 0`, 1 passed.

**What changed.** The case keeps W2-64's ids, AB's commit and every assertion it had, and gets one more commit: its
`Task:` is `PROJ-tkaab`, A's id with one character after it, which names no ticket of the project (it is made with
the case's own commit helper, which checks no trailer). Git's search for `Task: PROJ-tkaa` finds it; it must not count
as A's: the close still refuses with the trailer gate (exit 3, `Task: PROJ-tkaa` named exactly) and does not name that
commit. Added to the case rather than beside it, so that the case that names the rule is the one its plant turns red.

**Red and green.** Under PF15: 1 failed, `the refusal does not say that no commit carries Task: PROJ-tkaa`; the close
counted the `PROJ-tkaab` commit as A's, passed its trailer gate and refused for containment instead
(`CONTAINMENT_FINDING`, naming `src/example/feature_after.py`); marker `commits of PROJ-tkaa matched by substring: 1,
of them exactly: 0`. On the head: 1 passed. `test_w1_30_close.py` whole on the head (`-n 4`): 33 passed before, 33
passed after.
