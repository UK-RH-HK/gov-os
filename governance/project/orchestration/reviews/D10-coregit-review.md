# D-10's red-fix list, item (1): the review of the core.bare fix's tests' half (W2-05, DAEO-0z8c)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-coregit-review.md`; branch `w2/W2-05-d10-tests` at `5e9cdcc8d6ba`; reviewer session log `/home/usain/gov-os-worktrees/W2-05-d10-tests/.gov-runtime/scratch/lead/log/D10-coregit-review-2.json`.
- verdict.py: READY (no blocking finding).

# Review record: D-10 red-fix item (1), the tests' half of the `core.bare` fix (W2-05, DAEO-0z8c), `adec4718a..5e9cdcc8d`

**Verdict: pass.** The change does what it claims. The case goes red on the old conftest for the stated reason and green on the new one. There are two findings, both about what an ordinary run actually covers. Neither fails open, so neither blocks.

**sandbox_check:** pass.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c` failed with `OSError: [Errno 30] Read-only file system`, and no file exists.
- (b) `git hash-object -w --stdin` returned `1ae28402a109` and `git update-index --refresh` exited 0.

**ps_check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing (grep exit 1).

**task:** DAEO-0z8c (W2-05), D-10 red-fix item (1). Independent read-only review of `adec4718a..5e9cdcc8d`, KPI `core-bare-tests-half`.

**status:** DONE. Verdict pass.

**work_completed:**
- Read the diff, the whole `tests/conftest.py`, `src/gov/util/gitenv.py` and the code that starts test runs (close, nightly, check runner).
- Compared the conftest's fixed list with git's own list of repository-local variables.
- Checked the order in which plugins and conftests load, and when xdist starts its workers.
- Reproduced the red and the green runs.
- Ran a scratch probe of the path the real suites use (the conftest found by folder), with a control on the old conftest.
- Ran the neighbouring unit tests, and checked trailers and paths.
- The Write tool asked for a permission grant to put a probe script in my sandbox TMPDIR. That can't be granted in a non-interactive session, so I wrote no script and ran the probe as single Bash commands inside TMPDIR.

**files_changed:** none in any tree (`git status` is clean). The only scratch was under the sandbox TMPDIR, now removed. The one leftover is the unreferenced blob `1ae28402a109` that step 0 wrote.

**evidence:**
- git 2.43.0's `git rev-parse --local-env-vars` prints the same 15 names, in the same order, as the conftest's fixed list `_GIT_LOCAL_FALLBACK`.
- Pre-change conftest: blob `7e6692554`, which matches the diff's index line.
- Scratch used: 1.5M and 354 inodes, plus 16K and 4 inodes. Both folders removed.

**tests** (all through `heavy_slot.sh`, `PYTHONPATH=<wt>/src`, empty HOME, `-p no:cacheprovider -o tmp_path_retention_policy=failed`):
- **New case, default run:** 3 passed, 2 deselected.
- **New case, `--optin=breadth`:** 5 passed.
- **New case on the pre-change conftest (red):** 4 failed, 1 passed.
  - `[alone]` and `[xdist]`: "the sacrificial repository's core.bare is now true".
  - Both rows of test 2: 19 extra variables seen.
- **Probe:** the conftest found by folder (not `-p conftest`), with `GIT_DIR` set to a sacrificial linked worktree's git folder.

  | Conftest | Mode | Result | Sacrificial `core.bare` after |
  |---|---|---|---|
  | reviewed | alone | 1 passed | `false` |
  | reviewed | `-n 2` | 1 passed | `false` |
  | pre-change (control) | alone | 1 passed | `true` |

- **`tests/unit/gitenv` + `tests/unit/close/test_repo.py`:** 53 passed, 42 deselected.
- **`test_repo.py` with `--optin=lifted,breadth`:** 34 passed.
- **What the exclusion left out:** `-m "not local_only" -k "not real and not green_here and not time_limit"` drops exactly one case, `test_bisect_step.py::test_a_real_bisect_s_tests_get_only_the_run_s_environment`. It is a real `git bisect`, not a model. Run by node id: 1 passed.

**discoveries:**
- **The sandbox sets git variables that the conftest now drops.** The launcher exports `GIT_CONFIG_COUNT=4` (four `safe.directory` entries) and `GIT_CONFIG_PARAMETERS` (proxy settings). This is harmless today:
  - git works on the worktree without them (`env -u GIT_CONFIG_COUNT -u GIT_CONFIG_PARAMETERS git -C <wt> rev-parse HEAD` succeeds, and uid 1000 owns both the repository and the process);
  - the suites use no network.
- **The close, the nightly and `gov ci checks` already start tests with no `GIT_*` variables** (`close/command.py:998`, `nightly.py:118`, `check/runner.py:96`). There the conftest changes nothing; it only matters for a pytest started by hand or by `git bisect run`.
- **Comment wording, `tests/conftest.py:135`:** it says "before any hook". Strictly, plugins loaded earlier run their hooks first, but none of them runs git.

**risks:** The removal only acts in processes that import `tests/conftest.py`. A case that deliberately rebuilds an environment containing `GIT_DIR` is outside this, which is by design.

**lessons:** A test count for a folder that has `rep:` or lifted entries depends on the opt-in used. State the opt-in next to every count.

**proposed_decisions:** none.

**unresolved:** I did not re-run `tests/acceptance/W2-05`. The designer reports the same 9 reds with and without the change.

**recommended_next_action:** CTO merges `5e9cdcc8d`. F1 and F2 can ride along in W2-05's resume (DEC-802).

## Answers to the checks

1. **Complete: yes.**
   - **Variables.** The removal covers every name in the brief: `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_CONFIG`, `GIT_CONFIG_PARAMETERS` and `GIT_CONFIG_COUNT`.
     - It also removes every `GIT_CONFIG_KEY_n`/`VALUE_n` by pattern, and adds any name a newer git reports.
     - Of the variables it keeps (ceiling, namespace, exec path, trace, global/system config, template, identity), none points git at another repository.
   - **Timing.** `tests/conftest.py` is imported before `pytest_configure` (rootdir and confcutdir are the repository root). xdist starts its workers later, in `DSession.pytest_sessionstart` (`dsession.py:83-90`).
     - Workers are child processes that inherit the cleaned environment. xdist adds only `PYTHONPATH` and `PYTEST_XDIST_*`, and each worker imports the conftest again.
     - The probe confirms this under `-n 2`.
   - **Anything earlier?** No root conftest, no pytest settings or addopts in `pyproject.toml`, and no `PYTEST_ADDOPTS` or `PYTEST_PLUGINS`. Of the installed plugins, only testmon runs git: `git ls-files`, read-only, and only with `--testmon`, after configure.
2. **Nothing wanted is lost: yes.**
   - The close and the bisect pass no repository-local variables, and their `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` are kept (test 2 asserts this).
   - A gov command started inside a git hook by a case gets its variables from git after the import, so it is unaffected.
   - Nothing is restored, which is correct. No process other than a pytest run imports the conftest (nothing in `src/` or the orchestrator tools).
3. **The case proves it: yes.**
   - It is red on the old conftest for the stated reason.
   - It cannot pass if the conftest isn't loaded: rows 1–4 would go red.
   - Its one gap is that it loads the conftest with `-p conftest`, while the real suites find it by folder. My probe closes that gap.
   - The fifth function (monkeypatch) passes either way. It documents that nothing re-removes the variables per test, but it does not detect the hazard.
4. **Trailers and paths: correct.**
   - `5e9cdcc8d` carries Task DAEO-0z8c, Implements DEC-1109 and DEC-1074, Role independent-test-designer, Rewrite-Reason and Co-Authored-By.
   - It changes only `tests/conftest.py` and `tests/unit/gitenv/test_w2_05_suite_git_env.py`, both in the ticket's `allowed_paths`.
   - `b83e73b99` changes only the one ticket line.

## Findings

**F1: two of the new case's five rows run only with `--optin=breadth`.** scope: in
- `tests/optin-lifted-breadth.txt:1221` (`rep: tests/unit/gitenv/`) keeps only the first row of each parametrised function.
- So a default run deselects `[xdist]` and `[no-git-on-path]`. The designer's "4 failed, 1 passed" and "5 passed" are opt-in counts.
- Fix if wanted: give each mode its own unparametrised test function, or state that these rows are breadth by design.

Ordinary work: yes, because every run without the opt-in, which is the default, leaves them out.
Consequence: other. The protection holds on both paths (I verified it); only a later regression confined to those two paths would go unseen by a default run.

**F2: the evidence line "tests/unit/gitenv + tests/unit/close/test_repo.py 53 passed" contains no `test_repo.py` case.** scope: in
- `tests/optin-lifted.txt:175` lists that file, so a default run leaves it out entirely.
- I ran it with `--optin=lifted,breadth` on the branch: 34 passed.

Ordinary work: yes, because a default run deselects the file without saying so.
Consequence: other. The evidence overstates what ran; the cases themselves pass.

```verdict
{"kpis": [{"kpi": "core-bare-tests-half", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
