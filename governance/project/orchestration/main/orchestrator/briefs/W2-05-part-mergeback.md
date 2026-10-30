You are the ticket lead for ticket `DAEO-0z8c` (`W2-05`, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`.

**This is run 3: the merge-back and the resume (DEC-941 item 2, DEC-804 item 1).** `git rev-parse --short=12 HEAD` must show `f19f156ed606`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-2 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`;
- the round-2 draft probe record, `.gov-runtime/scratch/lead/probes/PR-DAEO-0z8c-round-2.md` (F-A);
- the sweep record, `docs/research/AR-2-git-sweep.md` (the rows marked "after <W2 id> merges");
- DEC-777, DEC-783 (item 2), DEC-801, DEC-804, DEC-805, DEC-807, DEC-808 (item 4), DEC-822 (item 3) and DEC-854.

## Why you start now

- **W2-05 is built and twice-reviewed work,** held since 2026-10-19. Its second and last review (DEC-413), at `f19f156e`, failed on F-A (a declared check running git in its own temporary repository acts on the project's index on a hooked commit: lost work) and F-B.
  - **The owner's answer:** no third round. F-A rides along in this resume, with P-1, and **this resume's fresh probe is the review of those fixes** (DEC-804 items 1 and 3, DEC-802).
  - F-B and D-1 are Wave 3 rows, W2-M375 and W2-M376 (DEC-807). They are not this run's work.
  - The resume waited for W2-50 and W2-53. **Both are closed.**
- **The owner's re-plan (DEC-941, 2026-10-29):** the nine held tickets are merged back, re-verified and closed, those in EXAMIN's minimum first, and W2-03 and W2-05 now (item 1.3). F-A is also an entry criterion of W2-08, which brings the hooks back (DEC-804 item 2, DEC-807 item 2).
- **Where the branch stands:** 11 commits ahead of `w2/integrate` and 712 behind; merge base `c94e1507c523`. A dry merge (`git merge-tree --write-tree`) reports **two conflicts**, both with W2-59's change, as DEC-854 foresaw:
  - `src/gov/check/runner.py` (`_run_command`'s environment);
  - `src/gov/retrieval/retrieve_check.py` (the imports).
  
  `src/gov/doctor/command.py`, `src/gov/guard/containment.py` and `src/gov/telemetry/counter.py` merge without a conflict.
- **The sweep is stale:** on the merged tree, 27 files of `src/gov` start git, and 3 are not in the record: `src/gov/cli/main.py`, `src/gov/close/nightly.py` and `src/gov/guard/reads.py`.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-05`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-0z8c`, `Implements: DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side (DEC-750 item 3). Resolve the two conflicts keeping both sides (DEC-854):
   - **`runner.py`, `_run_command`:** integrate's `command = _judged(command)` first, then your `env = git_env(root)`. The three `PYTHONPATH` lines stay out: W2-59 removed them so that a declared check runs on the judge's own package, not the project's (DEC-822 item 3, `771e9a0c`). Putting them back reopens that.
   - **`retrieve_check.py`:** your `from gov.util.gitenv import git_env` and integrate's `GITLEAKS_CONFIGS`. `REPO_ROOT` stays out: integrate reads the project from `Path.cwd()` (DEC-835), and nothing else uses it.
   - **Any other conflict,** or a resolution that changes either side's behaviour: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge, `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` must show 1. If not, stop and return PACKAGES.
2. **Red or green at the merged head.**
   - Rebuild under the machine's rebuild lock, from this worktree's code (check `gov.__file__` first). Then run `tests/acceptance/W2-05/` alone.
   - The 5 cases that waited on W2-50 (4) and W2-53 (1) should now pass. Name each one that does not, with its cause.
3. **Tests first, by a fresh independent test designer** (`gov launch`, sandboxed, `--effort xhigh`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-05/`, as described behaviours, each change to an existing case with a `Rewrite-Reason:`:
   - **F-A with P-1** (DEC-804 items 1 and 3, DEC-807 item 2): a check the project declares, run on a hooked commit (main tree plain and `-a`, linked worktree), gets no inherited `GIT_INDEX_FILE`. The commit lands with exactly what was staged, and the project's index names no missing object. An inherited `GIT_INDEX_FILE` is honoured only for git calls in the project root.
   - **DEC-805:** adapter-portability compares the template's hooks source with the repository's by hook events and matchers, paths normalised. It is green on this repository once the template carries `sessionStart`'s matcher.
   - **DEC-783 item 2:** the guard's freeze look-up (`src/gov/guard/decide.py`, sweep row 42, W2-L160) has a time limit of its own, 15 seconds.
   
   Then **check red yourself.**
4. **The engineer** (fresh, `gov launch`, sandboxed, `--effort high`) works only in the ticket's allowed paths, limited to calls that start git, plus DEC-805's two files:
   - **F-A and P-1:** `src/gov/util/gitenv.py` and `runner.py`.
   - **The marked rows whose tickets are now closed:** 32 to 36 and 38 (W2-53's `src/gov/close/**`), and 42 (W2-50's `decide.py`, with DEC-783's 15 seconds).
   - **The sweep, re-run on the merged tree:**
     - rows for `cli/main.py` and `guard/reads.py`, changed;
     - every new call in a file already listed;
     - `close/nightly.py` listed and marked "after W2-77 merges", left unchanged (DEC-777 item 2).
   - **Rows 39 to 41** (W2-03's `store/loader.py` and `decisions/checker.py`): W2-03's lead runs beside you, so leave them marked.
     - Change them only if W2-03 has merged into `w2/integrate` by the time the engineer starts (`git merge-base --is-ancestor w2/W2-03 w2/integrate`).
     - Then merge `w2/integrate` again first, in step 1's form.
   - **DEC-805:** `src/gov/adapters/portability.py`, and the one `matcher` line in `template/.rulesync/hooks.jsonc` (DEC-805 item 2 widens the ticket by that line). If the guard refuses it, return PACKAGES.
   
   Split the work into batches of about 90 minutes.
5. **Verification: in full,** in the close's form (LEAD-w2-common), plus `pytest --collect-only -q` over `tests` (DEC-868). The code changes, and the merged code was never verified as one.
   - `gov check`'s adapter-portability must be green.
   - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. From about 01:00, start no full verification run that cannot finish before 02:00. A close queue may be running in the main tree: run your suites only when the 1-minute load is under 20.
   - **Known:** W1-42's accepted reds; the load-sensitive cases, re-run alone. Any other red is named with its cause.
6. **A fresh FULL reviewer** (brief A3 with `governance/project/briefs/JUDGEMENT.md` word for word, `--effort max`, read-only, launched sandboxed) on the final head.
   - **Why:** it is the review of F-A's fix (DEC-804 item 1), and the earlier probes are stale: 712 commits came in after `f19f156e` (DEC-895).
   - **Its scope:** the whole ticket at that head, above all:
     - F-A and P-1;
     - the two conflict resolutions (the judge's own package; no `GIT_*` variable of a hook reaching a child git call);
     - every call routed in this run.
   - F-B and D-1 are not findings of this probe (DEC-807). Every finding carries the two lines (DEC-808 item 4).
   - **Commit a probe record** under `docs/probes/DAEO-0z8c/` only if it passes. Its `probed_commit` is the final head.
7. **Checkpoint and trailers:** `gov checkpoint` at the end (DEC-511). Run `trailer_gate.py` on your worktree before you return (LEAD-w2-common, DEC-927 item 2).
8. **Return** DONE (the probe passed; ready to merge), or PACKAGES. In either, list every file you changed under `src/gov/close/**` and `src/gov/guard/**`. Merged-not-closed tickets' probes judged those files (W2-58, W2-68, W2-57, W2-07), so the orchestrator orders your merge after their closes (DEC-895).

**The park rule (DEC-941 item 2):** if the repair grows beyond this one run, stop and return PACKAGES naming the cost. That means any of:
- a second test-design or engineer batch for the same finding;
- a probe that fails on a finding an honest agent can hit in ordinary work that fails open or loses work (DEC-413's two reviews are spent: no new round in this run);
- a change needed in a path another lead holds or outside the ticket's paths.

Name what is left, its size in lines and hours, and what waits on it (W2-08's hooks).

**Running beside you:**
- W2-03's lead (today) holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py` until it merges.
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- W2-61 holds `src/gov/retrieval/measure.py`.
- W2-60a and W2-56 hold `src/gov/launch/**`.
- W2-77 holds `src/gov/close/nightly.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 1 to 1.5 days, about 140 lines (the card's figure):
- the merge, about 1 hour;
- the test design and the red check, about 2 hours;
- the engineer, about 3 hours in two batches;
- one or two full runs, about 95 minutes each;
- the FULL probe, about 2 hours.

---
