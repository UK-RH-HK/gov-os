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
- **`tests/unit/guard/test_w2_141_search.py`**: 121 cases run the same planted calls against both sides.

## The KPI lines

| KPI line | Evidence | Applied |
|---|---|---|
| S1: Grep or Glob that can reach `tests/acceptance/<T>/` is refused unless it keeps the folder out; the refusal names the folder and says how | `gov accept W2-141`, success-1: 49 passed. Unit: `REFUSED` Grep and Glob rows (from the root, `tests/`, `tests/acceptance/`, `**/*.py`, `*.py`, `tests/**`, a later glob taking the folder back), both sides, each reason with `tests/acceptance/W2-95/` and `!tests/acceptance/W2-95/**` or Glob's "no exclusion" | decide side: on merge; hook side: by the operator's ACT at the lift's re-pin (`role_reads.py` and `pretooluse.py` copies) |
| S2: Bash recursive searches the same (grep -r/-R, rg, ag, ack, find with a reading action or piped into a reader) | `gov accept W2-141`, success-2: 61 passed. Unit: `REFUSED` Bash rows (grep -rn/-R, grep after a cd, `--exclude-dir` given as a path, rg, ag, ack, find -exec, find piped into `xargs grep`, into a while-read loop, in a `$(...)`, `rg --files \| xargs cat`), each reason with its tool's exclusion | as S1 |
| S3: nothing else changes (searches that cannot reach the folder or keep it out, other tickets' tests, other roles, names-only listings, a grep for the tests' names by pattern) | `gov accept W2-141`, success-3: 81 passed. Unit: 32 `ALLOWED` rows on both sides. `test_live_hook.py`'s G-14 cases pass (the one revised case included). See "The regression run" | as S1 |
| Failure 1: an engineer's search reaching its folder allowed without an exclusion | `gov accept`, failure-1: 82 passed | as S1 |
| Failure 2: a refusal that does not say how | `gov accept`, failure-2: 71 passed | as S1 |
| Failure 3: any other role or call newly refused | `gov accept`, failure-3: 79 passed. Unit: other roles' rows; `test_a_find_test_naming_a_secret_still_refuses` | as S1 |

`gov accept W2-141`: outcome pass, 182 passed, 0 failed, 0 skipped. It ran with the real `HOME`: the runner strips
`PYTHON*` from its child, so with an empty `HOME` its pytest is not found. No case there loads a model.

## The regression run

All runs used an empty `HOME` and `-m "not local_only"`. These folders hold no real-model case: no test is named for
one, and none starts a model, reranker or embedder.

- **The standard run** (`tests/unit/guard`, `tests/unit/hooks`, `tests/acceptance/W2-84`): 345 passed, 2 failed,
  997 deselected. The deselected cases are the project's opt-in rows (DEC-1061, `tests/conftest.py`: a parametrized
  function keeps only its first row unless the run opts in), with or without the brief's `-k`.
- **With every opt-in row** (`GOV_TESTS_OPTIN=lifted,breadth`; `tests/unit/guard` and `test_live_hook.py`): 1,252
  passed, 17 failed.
- **Two reds caused by the empty `HOME`, not by this change:** `test_live_hook.py::test_a_catastrophic_rm_is_refused`
  `[outside the project]` and `::test_the_reason_is_plain` (`rm -f ~/.bashrc`, where `~` is then a scratch folder
  under `/tmp`). Both pass when re-run alone with the real `HOME` (8 passed).
- **15 reds in `tests/unit/guard/test_reads.py`, all opt-in rows, all contradicting S1 or S2. The file is outside
  this ticket's paths.**
  - 14 rows expect the old fixed `TESTS_REFUSAL` for a search from above. The refusal now names the folder and says
    how to keep it out:
    - `CASES` rows 30 and 31 (Grep from `tests` and from the root);
    - row 34 (`grep -rn z tests/`);
    - row 36 (`rg z`);
    - rows 39 and 40 (find with `-exec`);
    - row 45 (`grep -rn z . 2>&1 | head`);
    - rows 48 to 50 (`ls | rg z .`, `ls | rg z &`, `ls | grep -r z`);
    - `RUNTIME` rows `find . -name '*.py' | xargs grep -n q`, ``cat `find tests -name test_feature.py` `` and
      `find . -print | while read f; ...`;
    - `TILDE`'s Grep of `~/proj`.
  - 1 row, `CASES` row 44, expects the Glob `**/*.py` from the root to be allowed. S1 refuses it.

  They need the same revision as `test_live_hook.py`'s P-2: compare those rows with the new reason (or check that it
  holds `tests/acceptance/W2-95/` and the tool's exclusion), and make row 44 a refusal.
