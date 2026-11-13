The review is done; my record follows.

```
task: Review 1 of W2-179 (DAEO-c9n8): a fresh, read-only LITE review of the test revision to W2-170's F3 file-access case at head 4a9d5d074834, against S1, F1 and F2
status: DONE; one round, no blocking finding, two rows. One call (my probe script's Write) was refused for quiet hours and queued for the 09:00 morning package; I did not retry it, and the judgement rests on reading the code plus the lead's recorded runs
work_completed: ran the sandbox check; read the diff (3eeb5cb2e98e..4a9d5d074834), the commit message, the ticket, DEC-820 and DEC-866 by id, the revised case and its helper, the README rows, and the context files w2_170_world.py (HERE, TRUE_*, at_or_under) and w2_170_open_log.py; traced each of the briefed spellings (sibling prefix, `..`, symlinks both ways, missing paths, ancestors, the guard's edge cases) through the helper and the guard; read the lead's clone-check record
files_changed: none
evidence: Step 0: (a) refused, "OSError: [Errno 30] Read-only file system" (good); (b) `echo sandbox-trial | git hash-object -w --stdin` printed 1ae28402a109 and `git update-index --refresh` succeeded (good); GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-c9n8. Head at start and at end: 4a9d5d074834 (both match). gov.__file__ = /home/usain/gov-os-worktrees/W2-179/src/gov/__init__.py. Session id: not known. TMPDIR /tmp/gov-launch-402bo5or/claude-1000 at the end: 20K, 8 inodes (my scratch folders removed). Read refusals: 0. Other refusals: 1, a Write of the probe script under TMPDIR ("Quiet hours (02:00 to 07:30) … queued for the 09:00 morning package (DEC-991)"), not retried and not done another way. Commit 3c1981b03b90 carries "Task: DAEO-c9n8", "Role: independent-test-designer", "Implements: DEC-820, DEC-866, DEC-966, DEC-1101" and "Rewrite-Reason: DEC-866, W2-179 (DAEO-c9n8): W2-170's F3 case counted the repository's own files as runs-folder opens in the nightly's clone under ~/gov-os-runs". `git diff --stat` base..head: only tests/acceptance/W2-170/README.md (+7/-2) and tests/acceptance/W2-170/test_w2_170_s4_map.py (+23/-1). Status --porcelain at the end: empty. The lead's record clone-check.txt: in both clone places, merged = pass, planted-outside = fail with only that path in `reached`, planted-own = pass; the pre-revision case in the ~/gov-os-runs clone = fail (the nightly's red reproduced)
tests: none run (the lead's runs not repeated; my synthetic call of the helper was not run because its script file was refused)
discoveries: (1) The helper picks paths "at or under a true root" by their spelling only (normpath) and resolves symlinks only on the repository side. Its docstring says a symlinked spelling "can neither carry a true-root path past the filter", which overstates this: a symlinked spelling outside the true roots is never picked at all. That behaviour is unchanged from the base. (2) The guard ignores a repository root of "/" (at_or_under never matches under "/"), but the exclusion then excludes nothing, so it fails closed
risks: the probe stands on reading the code plus the lead's six recorded runs, with no synthetic run of my own (refused). If the nightly ever puts its interpreter, venv or pytest temp folder under ~/gov-os-runs but outside the clone, the case goes red falsely. That is fail-closed, and the nightly's 104 entries show it does not happen today
lessons: a Write under TMPDIR is refused in quiet hours (DEC-991), so in a quiet-hours review, schedule any probe that needs a script file outside quiet hours or brief it as inline-only
proposed_decisions: none
unresolved: the refused probe Write is queued for the 09:00 morning package (DEC-991). Nothing in the verdict depends on it
recommended_next_action: the lead records RV1 and RV2 as Wave 3 rows and takes W2-179 to its close; READY computes from the verdict block below (no blocking finding)
```

---

**task: DAEO-c9n8**
**decisions:** DEC-820, DEC-866, DEC-801, DEC-808, DEC-1010
**probed_commit:** 4a9d5d0748343351b60d6de38cdb6e5ddd07dbd4

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