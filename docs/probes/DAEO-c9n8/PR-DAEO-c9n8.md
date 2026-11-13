---
type: probe
task: DAEO-c9n8
reviewer_session: 79f85759-ea74-4c94-a5ee-5103960ddc1b
implementer_session: 6117e372-d954-4339-a8ed-97ff4fc383cf
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 4a9d5d0748343351b60d6de38cdb6e5ddd07dbd4
decisions_applied: [DEC-820, DEC-866, DEC-966, DEC-1101]
---

# Probe record: W2-179 (DAEO-c9n8), the LITE review of W2-170's F3 file-access case revision

- **What was probed.** Head `4a9d5d074834` of `w2/W2-179`: the independent test designer's one commit `3c1981b03b90` (session `6117e372-d954-4339-a8ed-97ff4fc383cf`, Sonnet at effort high, class C1), merged by the ticket lead. It changes `tests/acceptance/W2-170/test_w2_170_s4_map.py` (the helper `_true_root_opens`, which leaves out the repository's own root taken from `W.HERE`, compared in realpath form, plus a guard that the root is narrower than every true root) and `tests/acceptance/W2-170/README.md`. Base `3eeb5cb2e98e`.
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session `79f85759-ea74-4c94-a5ee-5103960ddc1b`, Opus at effort high, class C1, 2026-11-12), started through `gov launch` under its OS sandbox with the reading tools alone. Commissioned and judged by the ticket lead (an orchestrator-role session). It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree, and `git status --porcelain` stayed empty.
- **Step 0.** The write outside the worktree was refused (read-only file system). `git hash-object -w` and `git update-index --refresh` worked. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-179/src/gov/__init__.py`. Read refusals: 0. One Write refusal: the probe script under TMPDIR, refused for quiet hours (DEC-991). It was not retried, and the verdict does not rest on it.
- **The lead's runs beside it.** These were all on `4a9d5d074834`, in fresh `--no-hardlinks` clones under `~/gov-os-runs/W2-179/clone` and `/tmp/w2-179-else/clone`, both since removed:
  - The case as merged passed in both clones.
  - A synthetic log entry at `~/gov-os-runs/W2-179/planted-outside/x.txt` failed the case in both, with only that path in `reached`.
  - A synthetic entry naming the clone's own `src/gov/memaudit/__init__.py` passed in both.
  - The pre-revision case failed in the runs-folder clone with the repository's own files, which reproduces the nightly's red.
  - `gov accept W2-179` passed: 179 passed, 0 failed.
  - `lead_verify`: 3,935 tests, 6 failed. All six are W2-96's shared base reds:
    - four fail on `w2/integrate`'s head `f3d612de7147`;
    - the other two pass when run alone on this head (load-sensitive);
    - all six are red in the nightly of 11-12 on `9bbef27f1d05`.
- **Threat model (DEC-801, DEC-808).** The review judges against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries.
- **Verdict: pass.** Classification (DEC-809): yes and fails open or loses work 0; yes and other 0; rows 2 (RV1, RV2). The lead's judgement agrees:
  - RV1 (the helper's docstring overstates its symlink handling; selection by spelling is unchanged from the base) is a row.
  - RV2 (a false red if the nightly ever keeps its interpreter or temp folder under `~/gov-os-runs` outside the clone; it fails closed) is a row.
  - Both are returned to the orchestrator as residuals.

## The reviewer's record (verbatim)

**task: DAEO-c9n8**
**decisions:** DEC-820, DEC-866, DEC-801, DEC-808, DEC-1010
**probed_commit:** 4a9d5d074834 (the full id is in the front matter; the lead shortened it here under row W2-L423's rule)

### Scope
- The revised case `test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders`, its helper `_true_root_opens`, the two changed README passages, and the commit's trailers. These were judged against S1, F1 and F2.
- **Out of scope:** `src/gov/memaudit/**` and the other W2-170 cases.

### Method
- I read the diff, the case, the helper, `w2_170_world.py` (`HERE` resolved; `TRUE_*` from the password database; `at_or_under` = normpath plus a separator-bounded prefix) and `w2_170_open_log.py`. The log runner makes open and `os.*` paths absolute against the working folder at the time of the event. It logs Popen argv and cwd as they are.
- I traced 15 synthetic spellings through the helper's logic and 6 repository-root choices through the guard, once each, by reading the code.
- The script that would have run the same cases against the real helper, with substituted roots under TMPDIR, was refused (quiet hours) and was not run.
- I did not touch the real `~/gov-os-eval` or `~/gov-os-runs`.

### Probed and found sound

**Only the repository's own files are let through, wherever the repository lives.**
- `repo_root = W.HERE.parents[2]`, and `HERE` is `Path(__file__).resolve().parent`. So the root comes from the test file's own resolved place, not from the working folder (the planted repository) and not from an environment variable.
- A clone under `~/gov-os-runs/W2-00/nightly/<run>/` excludes exactly that clone.
- A clone elsewhere excludes nothing under the true roots, because its files are never picked in the first place.
- The lead's six recorded runs agree with this.

**Spelling (F1).**
- *Sibling folder with the same prefix:* `.../R-other/x` is not under `.../R`, because the match needs a separator after the root. It stays reached.
- *`..`:* both `R/../R2/x` and `R/missing/../../R-other/x` are picked by the lexical normpath. The realpath on the repository side collapses them outside R, so they stay reached. `R/../../nightly/R/src/...` resolves into R and is excluded, which is correct because it is a repository file.
- *Symlink inside the repository pointing out into the runs folder:* the realpath leaves the repository, so the path stays reached. This fails closed.
- *Missing paths* (stores not yet created) are normalised by their spelling and stay excluded when they are under the root.
- *Ancestors of the clone* (`.../nightly`, `~/gov-os-runs` itself) are not excluded and still fail the case.

**Normal form on each side.**
- The repository root is in realpath form, and `HERE` is already resolved.
- Each candidate is in realpath form on the exclusion side and in normpath form on the selection side. This is the same selection the base had.
- Realpath is computed only for candidates that already passed the true-root test (the `and` short-circuits). Relative Popen argv entries therefore never reach it.

**The guard.**
- It asserts that none of TRUE_HOME, TRUE_RUNS or TRUE_SETS, raw or resolved, is at or under the repository root, raw or resolved. That covers a root equal to a true root, a root that is an ancestor of one, and an alias of one.
- A root of "/" is not caught (discovery 2), but the exclusion then excludes nothing, so it fails closed.

**Nothing else loosened (F2).**
- The only lines changed in the case are the `reached` line, the guard added before the run, and `import os`.
- The two later assertions (the planted questions were opened; `~` was the planted home) are unchanged.
- No skip or xfail was added, and no case was removed. The diff touches only the two allowed paths.

**DEC-820 (b), (d).**
- The case still plants its own sets root and runs folder.
- The guard and the helper call `realpath`, which reads link metadata only, never file contents or listings. The helper does this only for paths the run itself already touched under a true root, and the guard only on the three roots.
- Nothing under the true roots is opened or listed.

**DEC-866.** The Rewrite-Reason trailer is present and names DEC-866 and the cause.

### Findings

**RV1: the docstring overstates the symlink handling**
- *Behaviour:* the helper's docstring says a symlinked spelling cannot carry a true-root path past the filter. In fact, an open spelled through an alias outside the true roots that resolves into one is never picked, because selection is by spelling. It should either say that selection is by spelling (as in the base) or resolve the selection side too.
- *Introduced?* No. This revision did not create the gap: the base case selected the same way.
- scope: out
- Ordinary work: no, because the code under test runs with the planted HOME and would have to spell a true root through an alias path that some other process created.
- Consequence: other (wording; the selection gap is unchanged from the base)
- *Would reverse it:* a run of the code under test, in ordinary use, whose log shows a true-root file reached through such an alias.

**RV2: false red if the nightly's environment lives in the runs folder**
- *Behaviour:* if the nightly ever keeps its interpreter, venv or pytest temp folder under `~/gov-os-runs` outside the clone, the logged import or temp-folder opens there would count as runs-folder opens, and the case would go red falsely.
- *Should have:* nothing to change now. This fails closed.
- scope: out
- Ordinary work: no, because the nightly's 104 red entries of 11-12 were all of the repository, with no interpreter or temp paths, so today's layout does not hit it.
- Consequence: other (a false red that fails closed)
- *Would reverse it:* a nightly log whose `reached` list holds interpreter or temp-folder paths outside the clone.

**Classification:** yes and fails open or loses work: 0; yes and other: 0; rows: 2 (RV1, RV2).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "RV2", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "RV1", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}]}
```