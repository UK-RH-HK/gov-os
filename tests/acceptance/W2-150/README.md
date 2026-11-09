# W2-150 acceptance tests: memory's import closure free of the gates (E-2's four edges)

Ticket DAEO-ijf5 (W2-150), profile STANDARD; D-6 part 2's code item (P1-PLAN §A P1-6 item 1, §D; DEC-1039 (2),
DEC-1040 (1), DEC-1109 (2)); source INVESTIGATION-1 part E, row E-2. Written by the independent test designer (MR-3)
from the ticket's KPI lines S1 to S5 and its three failure lines, before any implementation, reading only
`w2/integrate` as merged into `w2/W2-150-tests` (`235341a0b`). Nothing of the engineer's work was read (there is none
yet).

## How they run

    PYTHONPATH=<worktree>/src PYTHONUSERBASE=$HOME/.local HOME=<empty scratch> TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-150 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

Or `python3 -m gov.cli.main accept W2-150 --root <worktree>`. The runner drops every `PYTHON*` variable, so with a
scratch HOME, link `<scratch>/.local` to the real user site so its child finds pytest.

26 cases, about 2 seconds. No GPU, model, network, install or store. Nothing under `fixtures/evaluation/**`, the
hidden half or held-out material is read: the walk parses `src/gov/**/*.py` only.

## The instrument

`w2_150_walk.py` is a **static** walk over `src/gov`: every `.py` file is parsed with `ast` and never imported.
- It follows every `import` and `from … import` statement **anywhere in a module** (module level, functions,
  methods, classes, `if`/`try` blocks: `ast.walk` over the whole tree).
- Relative imports are resolved against the importing module's package. `from gov.x import y` reaches `gov.x.y`
  as well when `y` is a submodule.
- Importing a module runs its parent packages' `__init__`, so a module reached brings its parents
  (`gov.decisions.register` brings `gov.decisions`, and with it whatever `gov/decisions/__init__.py` imports).
- Only `src/gov` modules are nodes.

**S1's start set:** every module of `gov.retrieval`, `gov.retrieve`, `gov.store` and `gov.secrets` (31 today).
**Forbidden:** every module of `gov.close` and `gov.guard`, and `gov.decisions.checker`. On a failure each forbidden
module is printed with the shortest import path that reaches it, every edge with its file and line, e.g.
`gov.close.select: gov.store.loader -> gov.close.fingerprint [src/gov/store/loader.py:546] -> gov.close.select
[src/gov/close/fingerprint.py:26]`.

`w2_150_run.py` runs `python3 -c` in a fresh subprocess with `PYTHONPATH` set to this tree's `src` (S3, S4).

## KPI lines, tests, and the outcome on `w2/integrate` (`235341a0b`)

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_150_closure.py::test_s1_memory_closure_reaches_no_gate` | red | the walk from the 31 memory modules reaches 101 modules, 27 of them gates: 17 of `gov.close` (by `store/loader.py:546`), 9 of `gov.guard` (by `retrieval/measure.py:74`, `retrieval/retrieve.py:39`, `secrets/__init__.py:48`, and `decisions/checker.py:53` for the two containment modules) and `gov.decisions.checker` (by `retrieval/supplementary.py:56 -> gov.decisions -> __init__.py:3`) |
| S1 | `test_w2_150_closure.py::test_s1_the_start_set_is_every_module_of_the_memory_packages` | green (guard) | the instrument: the start set is every `.py` of the four packages, not empty, and holds the four modules E-2 names |
| S1 | `test_w2_150_closure.py::test_s1_the_walk_follows_every_import_statement_form` | green (guard) | the instrument, on a planted tree: function-, method- and `if`-level imports, relative imports, `from pkg import submodule`, a parent package's `__init__`, the printed path form, no false edge for a non-module name |
| S2 | `test_w2_150_edges.py::test_s2_store_loader_imports_no_close_and_no_tickets` | red | `store/loader.py:546` (and `:599`) `from gov.close.fingerprint import of_commit` |
| S2 | `test_w2_150_edges.py::test_s2_retrieve_command_closure_reaches_no_decisions_checker` | red | `gov.retrieve.command -> gov.decisions [src/gov/retrieve/command.py:123] -> gov.decisions.checker [src/gov/decisions/__init__.py:3]` |
| S2 | `test_w2_150_edges.py::test_s2_secrets_closure_reaches_no_guard` | red | `gov.secrets -> gov.guard.runs [src/gov/secrets/__init__.py:48] -> gov.guard.decide [src/gov/guard/runs.py:42] -> …` (6 guard modules) |
| S2 | `test_w2_150_edges.py::test_s2_retrieval_measure_closure_reaches_no_guard` | red | `gov.retrieval.measure -> gov.guard.reads [src/gov/retrieval/measure.py:74] -> gov.guard.decide [src/gov/guard/reads.py:27] -> …` (6 guard modules) |
| S3 | `test_w2_150_old_names.py::test_s3_old_name_importable_from_its_old_module` | green (guard) | 12 items, each `from <old module> import <name>` in a fresh process: `of_commit`, `_match_pattern`, `TICKETS_REL`, `runs.root`, `leave_out`, and from `gov.guard.reads` `evaluation_sets`, `PolicyError`, `PATH_MAP_REL`, `SETS_KEY`, `set_fault`, plus `_Part` and `_ticket` (the other names `measure.py:74` imports, "the names measure.py used") |
| S3 | `test_w2_150_old_names.py::test_s3_constants_keep_their_values` | green (guard) | `.tickets`, `governance/project/path-map.yaml`, `evaluation_sets`; `PolicyError` an `Exception` |
| S3 | `test_w2_150_old_names.py::test_s3_match_pattern_behaves_as_today` | green (guard) | nine path/pattern pairs (`**`, `*`, an escaped `.`, a trailing `/**` not matching the bare folder) |
| S3 | `test_w2_150_old_names.py::test_s3_runs_root_behaves_as_today` | green (guard) | `<realpath of HOME>/gov-os-runs`; `None` for a relative HOME |
| S3 | `test_w2_150_old_names.py::test_s3_leave_out_passes_evidence_without_lines_through` | green (guard) | evidence with no `start_line` comes back unchanged with `None` |
| S3 | `test_w2_150_old_names.py::test_s3_evaluation_sets_and_set_fault_behave_as_today` | green (guard) | no path map `{}`; the block alone parsed; a list block `PolicyError`; `set_fault`'s four messages and `None` |
| S3 | `test_w2_150_old_names.py::test_s3_of_commit_classifies_paths_as_today` | green (guard) | a temporary git folder: no test map `None`; with one, the code and records fingerprints recomputed from `git ls-tree` (`record_only` matches out of code, the test map always code); an unreadable commit `None` |
| S4 | `test_w2_150_guard_imports.py::test_s4_import_of_guard_decide_loads_only_guard_util_and_stdlib` | green (guard) | `sys.modules` before and after `import gov.guard.decide` in a fresh process: only `gov`, `gov.guard.*`, `gov.util.*` and the standard library (`sys.stdlib_module_names`) |

The failure lines, by the cases that would catch each:

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| F1 | `test_w2_150_closure.py::test_s1_memory_closure_reaches_no_gate` | red | a gate still reached from memory's closure |
| F1 | `test_w2_150_edges.py::test_s2_store_loader_imports_no_close_and_no_tickets` | red | as above, edge 1 |
| F1 | `test_w2_150_edges.py::test_s2_retrieve_command_closure_reaches_no_decisions_checker` | red | as above, edge 2 |
| F1 | `test_w2_150_edges.py::test_s2_secrets_closure_reaches_no_guard` | red | as above, edge 3 |
| F1 | `test_w2_150_edges.py::test_s2_retrieval_measure_closure_reaches_no_guard` | red | as above, edge 4 |
| F2 | `test_w2_150_old_names.py::test_s3_old_name_importable_from_its_old_module` | green (guard) | a moved name no longer importable from its old module |
| F2 | `test_w2_150_old_names.py::test_s3_of_commit_classifies_paths_as_today` | green (guard) | a change in the close fingerprint's path classification |
| F2 | `test_w2_150_old_names.py::test_s3_match_pattern_behaves_as_today` | green (guard) | a change in the guard's and the close selection's pattern grammar |
| F2 | `test_w2_150_guard_imports.py::test_s4_import_of_guard_decide_loads_only_guard_util_and_stdlib` | green (guard) | the guard's hot path pulling a new module |

## Notes and limits

- **N-1. S5 and F3 are the reviewer's.** S5 (each moved helper's unit cases under `tests/unit/util/`, the old ones
  kept where they test the old name) and F3 (an acceptance test edited to fit the move) are judged by the reviewer
  on the diff. No case here. S3's "existing unit and acceptance suites pass unchanged" and S4's "the guard's
  decisions on its own unit suite" and `hook_timing.py` median of five are the CTO's scoped runs. The cases here are
  the import and behaviour guards only.
- **N-2. What counts as an import (the KPI's words, read literally).** "Every import statement (module level and
  inside functions)". So an `import`/`from` placed inside a function body still counts: a `gov.decisions/__init__`
  that only moves `from gov.decisions.checker import check` into a function (or a PEP 562 `__getattr__` holding an
  import statement) still reaches `checker` from any module that imports `gov.decisions.<anything>`. A call such as
  `importlib.import_module("gov.decisions.checker")` is not an import statement and is not followed. That is the
  form of the ticket's "`gov.decisions`' `__init__` imports its submodules lazily" that S1's walk lets through. The
  `__init__`'s existing function-level imports of `tags` (line 10) and `propagation` (line 16) count too, and
  `propagation.py:24` imports `checker`.
- **N-3. The walk's view of today: two routes E-2 did not name (P1 for the CTO, see the return).** With E-2's four
  edges cut (a simulation, not code), S1 still reaches the gates by:
  - (a) `gov.retrieval.retrieve -> gov.guard.role_paths [src/gov/retrieval/retrieve.py:39] -> gov.guard.reads
    [src/gov/guard/role_paths.py:121] -> gov.guard.decide …`. This is W2-13 S5's role filter (`5b42e9810`,
    2026-11-03, after E-2 was measured on 11-02); `retrieval/supplementary.py:135` also calls it. Neither
    `retrieval/retrieve.py`, `retrieval/supplementary.py` nor `guard/role_paths.py` is in the ticket's
    `allowed_paths`.
  - (b) `gov.retrieval.supplementary -> gov.decisions [src/gov/retrieval/supplementary.py:56] ->
    gov.decisions.propagation [src/gov/decisions/__init__.py:16] -> gov.decisions.checker
    [src/gov/decisions/propagation.py:24]`. This can be closed inside `allowed_paths` (`decisions/__init__.py`) by
    N-2's form.

  The four S2 cases each go green under the simulated cuts. S1 stays red until (a) is dealt with, which the ticket
  as filed cannot do. The test follows the KPI line (no module of `gov.guard`) and makes no exception for
  `role_paths`.
- **N-4. S2 edge 1 is the module's own statements only** (any level); edges 2 to 4 are each module's whole closure,
  as the brief states. `gov.secrets`' case starts from the package (`secrets/__init__.py`); its other modules are
  in S1.
- **N-5. S4's allowance.** `gov` (the empty top package), `gov.guard.*`, `gov.util.*`, and any module whose top-level
  name is in `sys.stdlib_module_names`. A third-party module (for example `yaml`) loaded at import time is outside.

## Files

- `w2_150_walk.py`: the static walk (S1, S2).
- `w2_150_run.py`: the fresh-subprocess runner (S3, S4).
- `test_w2_150_closure.py` (S1), `test_w2_150_edges.py` (S2), `test_w2_150_old_names.py` (S3),
  `test_w2_150_guard_imports.py` (S4).
