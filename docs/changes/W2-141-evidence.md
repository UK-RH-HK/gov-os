# W2-141 evidence: an engineer's search into its own acceptance folder (DAEO-xwro; DEC-1093 (2), DEC-1102)

**The gap.** W2-138's engineer saw six lines of its own acceptance tests through a repository-wide Grep. Integrate's
`decide` already refused broad searches, but its refusal said only "run them with pytest". It did not accept an
exclusion, missed Glob with `**`, ag and ack, and never said how to keep the folder out. The live hook
(`.claude/hooks/role_reads.py`) let every search from a folder above through, and Glob never reached it.

## The change

- **`src/gov/guard/reads.py`** (the decide side):
  - A block between `# BEGIN W2-141 BLOCK` and `# END W2-141 BLOCK` decides which files a search takes in or keeps
    out, following each tool's own rules:
    - rg's globs and the Grep tool's: gitignore lines read from the session's folder; the last matching line wins.
    - grep -r's `--exclude-dir` (a folder's base name), `--include` and `--exclude`.
    - ag's `--ignore` and `--ignore-dir`.
    - ack's `--ignore-dir`.
    - find's `-prune` and its negated `-path` and `-name` tests, and `-maxdepth`.
    - Glob's pattern. A pattern with no folder in it matches a name at any depth, as rg's `--files` reads it.

    The block also holds the refusal, `SEARCH_REFUSAL` and `X_HOW`, which names `tests/acceptance/<T>/` and says how
    to keep it out.
  - The engineer's own part carries its WBS id. `above()` takes the block's verdict for that part only, and its
    refusal then says how. The changed routes:
    - the Grep tool;
    - Glob, now with `**` too, for the own folder only;
    - recursive grep, rg and find with a reading action;
    - ag and ack, which are new, for the own folder only;
    - a find, grep or rg listing whose names go to a reader (the run-time routes: `| xargs`, a while-read loop,
      `$(...)`).

    A find's `-path` or `-name` value is a pattern, not a read. A secret or hidden part named there still refuses.
    A direct read keeps `TESTS_REFUSAL`. Hidden parts and secrets are judged as before.
- **`docs/changes/W2-141-hook/role_reads.py`** and **`pretooluse.py`**: the hook side, as whole-file copies for the
  operator's ACT. Their diff against the live files is in that folder's `README.md`. `role_reads.py` holds the same
  block byte for byte, so it does not depend on the pinned product. `pretooluse.py` adds only `"Glob"` to G-14's tool
  list.
- **`tests/unit/hooks/test_live_hook.py`**: the one `G14_PASSED` case `grep -r foo tests/` becomes
  `grep -r --exclude-dir=W2-G14T foo tests/` (commented DEC-1093 (2)). It passes on the live hook and on the copy.
- **`tests/unit/guard/test_reads.py`**: its rows that expected the old refusal of a search into the own folder expect
  the new one (round 2: 15 rows; round 3: the four `git grep` and `git ls-files` rows, and the git "how").
- **Round 3, the independent review's findings (round 1):**
  - **F1** (`git grep` from a folder that holds the own folder). The block's `x_search` reads `git grep` and
    `git ls-files` (`_x_git`): pathspecs from the folder git runs in, their exclusions (`:!`, `:^`, `:(exclude)`)
    honoured; before `--`, a word that is not a path, a wildcard or magic is a revision. Decide: `git` judges the own
    folder through it (`_own_git`), with the git "how" (`-- . ':!tests/acceptance/<T>'`), and the other parts as
    before. Hook: `Bash.git` records the search from where `-C` leaves it.
  - **F2** (`git ls-files` piped into a reader). `git ls-files` is a listing in the block. Hook: it waits in
    `_listed` like find's. Decide: the run-time listing (`lists`) judges the own folder through it, with the git "how".
  - **F3** (a for loop over a listing's `$(...)` whose body reads). Hook: `_for_reads` makes the list's `$(...)` a
    reader's word. Decide already refused these through `runtime()`.
  - **F4** (decide: a recursive search whose start is a shell glob). `above()` reads a glob start, for the own folder,
    as a search from its literal folder of what lies at or below a path the glob matches (`x_spread`). The hook
    already expanded the glob.
  - **F5** (decide: `zgrep -r`, `grep -d recurse`). Judged for the own folder through `x_search`, which already read
    them as recursive. The hook already refused them.
  - **F6** (a brace-expanded `--exclude-dir={.git,<T>}`). The block reads an option word with braces as the options
    Bash makes of it, on both sides.
  - **F7**: a rollback step in `W2-141-hook/README.md`. **F8**: this file's regression section.
- **`tests/unit/guard/test_w2_141_search.py`**: 204 cases run the same planted calls against both sides; round 3 adds
  a case for every call F1 to F6 name (refused or allowed as stated). Each of them fails on round 2's code on the side
  the review named and passes now.

## The KPI lines

| KPI line | Evidence | Applied |
|---|---|---|
| S1: Grep or Glob that can reach `tests/acceptance/<T>/` is refused unless it keeps the folder out; the refusal names the folder and says how | `gov accept W2-141`, success-1: 49 passed. Unit: `REFUSED` Grep and Glob rows (from the root, `tests/`, `tests/acceptance/`, `**/*.py`, `*.py`, `tests/**`, a later glob taking the folder back), both sides, each reason with `tests/acceptance/W2-95/` and `!tests/acceptance/W2-95/**` or Glob's "no exclusion" | decide side: on merge; hook side: by the operator's ACT at the lift's re-pin (`role_reads.py` and `pretooluse.py` copies) |
| S2: Bash recursive searches the same (grep -r/-R, rg, ag, ack, find with a reading action or piped into a reader) | `gov accept W2-141`, success-2: 61 passed. Unit: `REFUSED` Bash rows (grep -rn/-R, grep after a cd, `--exclude-dir` given as a path, rg, ag, ack, find -exec, find piped into `xargs grep`, into a while-read loop, in a `$(...)`, `rg --files \| xargs cat`; round 3: `git grep`, `git ls-files` into a reader, a for loop over a listing that reads, glob starts, `zgrep -r`, `grep -d recurse`), each reason with its tool's exclusion | as S1 |
| S3: nothing else changes (searches that cannot reach the folder or keep it out, other tickets' tests, other roles, names-only listings, a grep for the tests' names by pattern) | `gov accept W2-141`, success-3: 81 passed. Unit: 52 `ALLOWED` rows on both sides (round 3 adds git pathspec exclusions, a brace-expanded `--exclude-dir`, glob starts that cannot reach the folder or keep it out). `test_live_hook.py`'s G-14 cases pass (the one revised case included). See "The regression run" | as S1 |
| Failure 1: an engineer's search reaching its folder allowed without an exclusion | `gov accept`, failure-1: 82 passed | as S1 |
| Failure 2: a refusal that does not say how | `gov accept`, failure-2: 71 passed | as S1 |
| Failure 3: any other role or call newly refused | `gov accept`, failure-3: 79 passed. Unit: other roles' rows; `test_a_find_test_naming_a_secret_still_refuses` | as S1 |

`gov accept W2-141`: outcome pass, 182 passed, 0 failed, 0 skipped. It ran with the real `HOME`: the runner strips
`PYTHON*` from its child, so with an empty `HOME` its pytest is not found. No case there loads a model.

## The regression run (round 3, 2026-11-09)

Folders: `tests/unit/guard`, `tests/unit/hooks`, `tests/acceptance/W2-84`. Each run went through the heavy slot with
`PYTHONPATH` set to this tree's `src`, the real `HOME` (pytest is installed in the user's site, so an empty `HOME`
cannot find it), `-m "not local_only"` and `-k "not real and not green_here and not time_limit"`.

- **The standard run:** 436 passed, 0 failed, 997 deselected. The deselected cases are the project's opt-in rows
  (DEC-1061, `tests/conftest.py`: a parametrized function keeps only its first row unless the run opts in).
- **With every opt-in row** (`GOV_TESTS_OPTIN=lifted,breadth`): 1,433 passed, 0 failed.
- **What the exclusion left out:** nothing. A collect-only run with the opposite filter (`-k "real or green_here or
  time_limit or local_only"`, and separately `-m local_only`) collects 0 of the 1,433 cases. No case in these
  folders starts a model, reranker or embedder.
- **`tests/unit/guard/test_reads.py`** has been in this ticket's paths since round 2 (DEC-1102). Its rows that
  expected the old refusal of a search into the own folder now expect the new one, and they pass: 15 rows in round 2,
  and in round 3 the four `git grep` and `git ls-files` rows (`CASES` `git grep -n z`; `RUNTIME`
  `git ls-files | xargs grep -n q`, `grep -n q $(git ls-files '*.py')`, `for f in $(git ls-files); do cat $f; done`).
- **The two reds that the empty `HOME` caused in round 1** (`test_live_hook.py::test_a_catastrophic_rm_is_refused`
  `[outside the project]` and `::test_the_reason_is_plain`) do not occur with the real `HOME`. They pass in both runs.
