# W2-150 evidence: memory's static import closure free of the gates (DAEO-ijf5; DEC-1109 (2), DEC-1039 (2))

**What it is.** Memory's modules (every module of `gov.retrieval`, `gov.retrieve`, `gov.store` and `gov.secrets`)
reached the close, the guard and `gov.decisions.checker` through six import edges, each for a small helper. Each
helper now lives in `gov.util` or `gov.store`. The old module imports it back, so every old name stays importable and
is the same object. No import is hidden from the walk: no `importlib` or `__import__`, only plain import statements.

## The walk

A static walk over `src/gov` with `ast`. It follows every `import` and `from … import` statement, at module level and
inside functions, including relative imports. A dotted name also reaches its parent packages' `__init__`, and
`from pkg import name` reaches `pkg.name` when that is a module. The walk starts from every module of the four memory
packages.

| | modules | lines | gate modules reached |
|---|---|---|---|
| before (`82faa2c89`) | 101 | 25,596 | 27 (`gov.close` and 16 of its modules, `gov.guard` and 8 of its modules, `gov.decisions.checker`) |
| after | 53 | 11,095 | 0 |

The six edges at the base, each gone:

| edge (base line) | what memory used | now |
|---|---|---|
| `store/loader.py:546`, `:599` → `gov.close.fingerprint` → `close.select` → `guard.decide._match_pattern` | `of_commit` | `gov.store.loader.of_commit` (same file, no import) |
| `retrieve/command.py:123` → `gov.decisions.register` → `gov/decisions/__init__:3` → `checker` | `leave_out` | `gov.util.register.leave_out` |
| `retrieval/supplementary.py:56` → `gov.decisions.register` (the second route to `checker`) | `leave_out` | `gov.util.register.leave_out` |
| `secrets/__init__.py:48` → `gov.guard.runs` → `guard.decide` | `runs.root` | `gov.util.runs_root.root` |
| `retrieval/measure.py:74` → `gov.guard.reads` → `guard.decide`, `heldout`, `protected` | the evaluation-set reading | `gov.util.parts` |
| `retrieval/retrieve.py:39`, `supplementary.py:135` → `gov.guard.role_paths` → `guard.reads` (the fifth edge) | the role filter | `gov.util.role_paths` |

`grep` of the six files finds no import of `gov.close`, `gov.guard` or `gov.decisions`; only `loader.py`'s comments
name `gov.close.fingerprint` and `gov.close.repo` as where its code came from. A runtime check agrees: importing all 30
memory modules in a fresh process loads no module of `gov.close` or `gov.guard`, and not `gov.decisions.checker`.

## Each moved name and its new home

| name | old module (still importable there, the same object) | new home |
|---|---|---|
| `of_commit`, `ALWAYS_CODE`, `PATH_MAP_REL`, `PREFIX`, `SCHEMA_RELS` (`of_commit`'s path classification) | `gov.close.fingerprint` | `gov.store.loader` |
| `MAP_REL`, `SCHEMA_NAME`, `SCHEMA_DIRS` (the test map's places) | `gov.close.select` | `gov.store.loader` (`TEST_MAP_REL`, `TEST_MAP_SCHEMA`, `SCHEMA_DIRS`) |
| `_match_pattern`, `_has_glob` | `gov.guard.decide` | `gov.util.patterns` |
| `_parse_frontmatter` | `gov.guard.decide` | `gov.util.tickets` |
| `TICKETS_REL` | `gov.tasks.tickets` | `gov.util.tickets` |
| `root`, `ROOT_NAME` | `gov.guard.runs` | `gov.util.runs_root` |
| `evaluation_sets`, `set_fault`, `PolicyError`, `PATH_MAP_REL`, `SETS_KEY`, `_Part`, `_ticket`, and what they need (`_front`, `_read_text`, `_related`, `_walk`, `_walk_fault`, `_paths_ok`, `_measures_ok`, `HIDDEN_REFUSAL`, `_MOST_FILES`, `_MOST_DEPTH`, `_LONG_PART`, `_WALK_FAULT`, `_TICKET_FAULT`, `_WBS_RE`) | `gov.guard.reads` | `gov.util.parts` |
| the whole role filter (`caller`, `Filter`, `RolePathsError`, `section`, `expand`, `Judge`, …) | `gov.guard.role_paths` | `gov.util.role_paths` |
| the whole register module (`leave_out`, `read`, `in_force`, `ids`, …) | `gov.decisions.register` | `gov.util.register` |

- **Moved whole, old name aliased.** `gov.guard.role_paths` and `gov.decisions.register` are the same module objects as
  their new homes: the old file imports the new module and puts it in `sys.modules` under its own name. This is needed
  because existing unit tests patch module attributes, and the moved code must see the patch: `role_paths.WORKTREES`,
  `.changed` and `.engineer_side` (`tests/unit/guard/test_role_paths.py`), and `register._read`
  (`tests/unit/decisions/test_register_w2_55.py`). A plain re-import would leave those tests patching a copy the moved
  code never reads.
- **Copies in the first pass, one source since S6:** `_Glob`, `load_yaml_unique` and the git runner were copied,
  because their home files were outside the ticket's paths. The follow-up removed the copies (see "S6 (the follow-up)"
  below).
- **Why the fingerprint went to `gov.store`, not `gov.util`.** The fingerprint starts git. W2-05's sweep
  (`tests/acceptance/W2-05/test_w2_05_sweep.py::test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`)
  requires every `src/gov` file that starts git to be named in `docs/research/AR-2-git-sweep.md`. `loader.py` is named
  there (row 41); a new `gov/util/fingerprint.py` would not be. That case is red at the base, with 4 unnamed files. It is
  still red with 4: `src/gov/util/role_paths.py` takes the place of `src/gov/guard/role_paths.py`, which was already
  unnamed.
- **`guard/decide.py`** changes only by importing `_match_pattern`, `_has_glob` and `_parse_frontmatter` from `gov.util`.
  Importing it loads `gov`, `gov.guard`, `gov.guard.decide`, `gov.guard.runs`, `gov.util`, `gov.util.gitenv`,
  `gov.util.patterns`, `gov.util.runs_root` and `gov.util.tickets`. The three new modules use the standard library only.
- `retrieval/synthesis.py` and `gov/decisions/__init__.py` are unchanged.

## One row per KPI line

| KPI | Evidence | Outcome |
|---|---|---|
| S1 no gate in memory's static closure | the walk above: 27 gate modules → 0; `gov accept` success-1 3/3 | pass |
| S2 the edges gone | the edge table and the grep above; `gov accept` success-2 4/4 | pass |
| S3 public calls unchanged | every old name is the same object as its new home's (an import check, and `test_the_old_*` in the new unit files); the touched packages' unit suites below; `gov accept` success-3 18/18 | pass |
| S4 the guard's hot path | `decide`'s import pulls only `gov.guard` and `gov.util` modules (above); `tests/unit/guard` with the opt-in lists, below; `gov accept` success-4 1/1. The CTO's `hook_timing.py` before and after is for the CTO to run | pass (timing: CTO) |
| S5 unit cases move with the helpers | `tests/unit/util/test_w2_150_patterns_tickets_runs.py`, `test_w2_150_parts.py`, `test_w2_150_role_paths_register.py`, `test_w2_150_store_fingerprint.py`: 60 cases, all green (`tests/unit/util` in all: 73 passed); the old cases stay where they test the old names | pass |
| failure lines | `gov accept` failure-1 5/5, failure-2 15/15 | pass |

## Runs (2026-11-09, `PYTHONPATH=<worktree>/src`, scratch `HOME`, through `heavy_slot.sh`)

- `gov accept W2-150`: before, 21 passed and 5 red (the test designer's count); after, **26 passed, 0 failed**
  (success-1 3, success-2 4, success-3 18, success-4 1, failure-1 5, failure-2 15).
- Scoped unit run, default selection (`-m "not local_only" -k "not real and not green_here and not time_limit"`):
  - suites: `tests/unit/{util,store,close,guard,decisions,secrets_check,retrieve,tasks}`;
  - other files that import a moved name: `tests/unit/retrieval/test_measure.py`, `test_w2_134_reanchor.py`,
    `test_w2_13_role_filter.py`, `test_w2_135_item_cap.py`, `test_w2_61h_families.py`, `test_w2_138_store.py`;
    `tests/unit/rebuild/test_w2_122_seed.py`, `test_w2_116_integration.py`; `tests/unit/plan/test_w2_136_overlap.py`;
    `tests/unit/launch/test_runs.py`, `test_launcher.py`; `tests/unit/containment/test_review_fixes.py`;
    `tests/unit/doctor/test_doctor.py`; `tests/unit/context/test_dropped_order.py`, `test_all_external.py`,
    `test_bounded.py`;
  - result: **809 passed, 1 failed**. 1,558 were deselected, almost all by the repo's opt-in lists (DEC-1061); the
    `-k` exclusion removes 2 of them.
  - The red is `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`. It
    compares the text of `.claude/hooks/pretooluse.py` with its staged copy; neither file is touched here, so it is red
    at the base too.
- The gate suites with the opt-in lists (`--optin=lifted,breadth`):
  `tests/unit/{guard,close,decisions,store,util,tasks,secrets_check,retrieve}`: **2,046 passed, 1 failed**, 16
  deselected (the `-m`/`-k` exclusion). The one red is the same `test_w2_141_search.py` case, and it is red against the
  base's `src` too (re-run with `PYTHONPATH` at an extract of `82faa2c89`).
- Not run here: `tests/unit/hooks/test_live_hook.py` (it plants trees under `~/gov-os-worktrees`, which the sandbox
  keeps read-only); the scoped set from `select_tests.py` (the CTO runs it outside the sandbox, as DEC-1064 asks); the
  real-model and `local_only` cases; the CTO's `hook_timing.py`.

## S6 (the follow-up): one source each (the review's R1, R2)

| helper | defined once in | imported by (the old name, the same object) |
|---|---|---|
| `_Glob` | `gov.util.parts` | `gov.guard.protected` (and its alias `_glob_rx`), `gov.guard.reads` |
| `load_yaml_unique` | `gov.util.parts` | `gov.guard.heldout` |
| the git runner `git` | `gov.util.gitrun` (new) | `gov.close.repo.git`; `gov.store.loader._commit_git` |

- **The move.** The copies in `guard/protected.py`, `guard/heldout.py`, `close/repo.py` and `store/loader.py` are
  deleted. Each of those files imports the name from its home. The bodies moved without a change, so glob matching, the
  twice-written-key refusal and `git`'s call (arguments, environment, `GIT_FAILURE` errors, return value) behave
  exactly as before. `close/repo.py` no longer imports `os` or `subprocess`, and `loader.py` no longer imports `os`;
  nothing else used them.
- **Why `gov.util.gitrun` and not `gov.util.gitenv`.** `gov.guard.decide` imports `gov.util.gitenv` when it loads.
  Adding the runner there would add `gov.cli.errors` to the guard hook's imports. The new module imports only the
  standard library, `gov.cli.errors` and `gov.util.gitenv`. Neither new home imports a gate: importing `gov.util.gitrun`
  and `gov.util.parts` in a fresh process loads no module of `gov.close` or `gov.guard`.
- **The guard's hook.** `gov.guard.reads` already imported `gov.util.parts`. Where the hook imports only
  `gov.guard.heldout`, it now also loads `gov.util.parts`, which is a `gov.util` module (S4).
- **DEC-500 comparison.** `close.repo.git` and the store's `_commit_git` were the same, so there was no stricter
  side to choose. Both:
  - drop every `GIT_*` variable of the caller's environment before `git_env` runs, so the person's identity and
    `GIT_INDEX_FILE` are dropped too;
  - pin the configuration (`pinned=True`: no system or global config);
  - set `GIT_NO_LAZY_FETCH=1`;
  - pass `--no-replace-objects`;
  - set stdin to `DEVNULL`;
  - raise `GIT_FAILURE` on any exit code outside `ok`.

  The store's copy was `git` with its defaults (`ok=(0,)`, no `given`, `pinned=True`). The single source keeps all of
  it.
- **Static scan.** An `ast` scan of `src/gov` finds one `class _Glob` (`util/parts.py`), one
  `def load_yaml_unique` (`util/parts.py`), and one function that runs `git --no-replace-objects` under `git_env`
  (`util/gitrun.py:git`).
- **Unit cases.** `tests/unit/util/test_w2_150_gitrun.py` has 5 cases:
  - the close and the store share the object;
  - output, exit code and stdin;
  - `GIT_FAILURE` outside `ok`;
  - a caller's `GIT_DIR` does not reach git;
  - replacement refs are not followed.

  The old names keep their cases in `tests/unit/close` and `tests/unit/guard`.
- **Runs (2026-11-09).** `gov accept W2-150`: **32 passed, 0 failed** (success-1 3, success-2 4, success-3 18,
  success-4 1, success-6 7, failure-1 5, failure-2 15).
- **Unit suites (2026-11-09).** `tests/unit/{util,guard,close,store}` with `--optin=lifted,breadth`, `-m "not local_only"`
  and `-k "not real and not green_here and not time_limit"`: **1,906 passed, 1 failed**. Of 1,922 cases, 15 were
  deselected, all by `-k` (12 `time_limit`, 3 `real`); no case in these suites is marked `local_only`.
  - The red is the known base red: `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`.
    It compares two hook files that S6 does not touch, and it fails the same way when re-run alone.

[DEC-1109 (2), DEC-1039 (2), DEC-1040 (1), DEC-136]
