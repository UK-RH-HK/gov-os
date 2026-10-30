You are the ticket lead for ticket `DAEO-0z8c` (`W2-05`, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`.

**This is run 4: the resume after the park (DEC-951 (P-B1-1), DEC-941 item 2).** `git rev-parse --short=12 HEAD` must show `d8cb39f4933e`, and `git status --short` must show one line only, `?? tests/acceptance/W2-05/test_zz_scratch_b1.py`. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-3 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` ("What a resume must do", the brief gaps);
- the batch-2 draft, `.gov-runtime/scratch/lead/briefs/eng5-work-DRAFT.md`, and the standing rules of `eng4.md` beside it;
- your run-3 return, the last JSON object's `result` in `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/W2-05-A5-run3r.json` (P-B1-1, P-B1-2);
- item 2 of the owner's package `governance/project/orchestration/packages/P1-MORNING-2026-10-30.md` (main tree);
- DEC-951, DEC-580, DEC-777, DEC-783 (item 2), DEC-804, DEC-805, DEC-807, DEC-808 (item 4), DEC-895 and DEC-906.

## Why you start now

- **Run 3 parked at 00:20 on P-B1-1.** Batch 1 (`8b8a3baa347a`) turned 14 W1-02 cases red:
  - `test_w1_02_deadline.py` 11, `test_w1_02_deadline_in_time.py` 2, `test_w1_02_unknown_tools_failure.py` 1;
  - their support slows the hook only through a `git` placed first on `PATH`, which the guard's freeze look-up no longer runs (W2-L160);
  - and the look-up's own 15 s limit (DEC-783 item 2) refuses before their lower bound of 19 s.
- **The owner's answer (DEC-951, 2026-10-30): (a).** A short test-designer revision of W1-02's deadline support, each change with a `Rewrite-Reason:`, then W2-05 resumes: batch 2, full verification, the FULL probe. The ticket's paths hold `tests/acceptance/W1-02/**` for that batch.
- **Where the branch stands:** 15 commits ahead of `w2/integrate` and 82 behind; merge base `a1629f1860ca`. A dry merge (`git merge-tree --write-tree`) on `816f764f36b8` reports **no conflict**. What came in, merged but **not closed**:
  - W2-71 (`cd256641`, `e9c40bb2`): `src/gov/secrets/__init__.py`;
  - W2-77 (`490fd575`): `src/gov/close/nightly.py`;
  - W2-57 (`6f7ace35`);
  - W2-03 (`a8eaf26e`): `src/gov/store/loader.py`, `src/gov/decisions/checker.py`, `src/gov/records/queries.py`, `src/gov/check/citations.py`;
  - W2-26 (`816f764f`).

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-05`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-0z8c`, `Implements: DEC-951, DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side (DEC-750 item 3).
   - A conflict a mechanical fix resolves (both sides kept as written, neither side's behaviour changed): resolve it and say how in the return. Any other: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge, `grep -c '^### DEC-951' docs/DECISION_REGISTER.md` must show 1. If not, stop and return PACKAGES.
2. **Rebuild** under the machine's rebuild lock, from this worktree's code (check `gov.__file__` first).
3. **The W1-02 revision: a fresh independent test designer** (`gov launch`, sandboxed, `--effort xhigh`; its brief must not set `TMPDIR`), in `tests/acceptance/W1-02/` only (the deadline support, the three files above and the README). Give it these behaviours as text. It never reads the files this branch changed (`src/gov/guard/decide.py` among them, DEC-820 (c)):
   - **The guard as it now runs:** its freeze look-up starts git by absolute path from the system folders (`/usr/bin`, `/bin`, `/usr/local/bin`, `/opt/homebrew/bin`), never by name from `PATH`, with a pinned environment and a time limit of its own of 15 s. It refuses the call when no git is found or the look-up times out; it never allows. The hook's own deadline stays 20 s (DEC-580).
   - **Slow the hook by a route the guard still takes:** the support's named pipe in the bookkeeping folder, its late input, or a repository setting that makes the real git hang. Never a `git` first on `PATH`, a slow machine, a weaker rule or a switch of the product (the support's own rule).
   - **Take in the 15 s:** a case whose slow step is the look-up gets the look-up's refusal at about 15 s, in the refusal's form. Each case that shows DEC-580's 20 s deadline keeps showing it, by a slow step the 15 s does not cover. Its lower bound stays.
   - **No other expectation lowered,** no case removed. The failure message for an allowed call ("the guard keeps no deadline of its own") stays reachable. The README says, for each revised case, what makes it red.
   - **Each changed case and the commit** carry `Rewrite-Reason: DEC-951 (P-B1-1); DEC-783 item 2; W2-L160`.
   - **Then check it yourself:** W1-02 whole, alone, on this branch: the 14 cases green, and no other case changed state. Then `tests/acceptance/W2-05/` as batch 1 left it: 46 passed, and 2 failed, both batch 2's.
4. **Engineer batch 2** (fresh, `gov launch`, sandboxed, `--effort high`): the draft `eng5-work-DRAFT.md`, spliced into a copy of `eng4.md`'s standing rules, with `retrieve_safe.py`, and these corrections:
   - `@@B1@@` is `8b8a3baa347a`.
   - **`src/gov/guard/reads.py` is W2-84's** (`DAEO-m1u3`, unmerged): never change it. Drop the draft's item 2 bullet for it. List its `_git` in the sweep, marked "after W2-84 merges" (DEC-777 item 1).
   - **W2-03 and W2-77 have merged.** In the run-3 reading, a merged ticket's marked rows become this batch's:
     - rows 39 to 41 (`decisions/checker.py`, `store/loader.py`) are routed now;
     - so are `close/nightly.py`'s git calls (bisect, `worktree remove`, `worktree prune`);
     - change only each call's environment; arguments, paths and order stay as those tickets left them.
   - **Containment's `git`** by the same absolute path as the guard's look-up (P-B1-2, a row riding along, DEC-802).
   - `src/gov/secrets/__init__.py` starts no git: list it as before.
   - If the batch does not fit one 90-minute session, a second engineer session continues the same batch. That is not a repair.
5. **Verification: in full,** in the close's form (LEAD-w2-common), plus collect-only (DEC-868), `gov check` (adapter-portability must be green) and `keyword_warn.py`.
   - **Known:** W1-42's accepted reds; the load-sensitive cases, re-run alone; W2-54's two time-limit cases if they time out under load (W2-85 is routing them to the nightly): re-run alone. Any other red is named with its cause.
   - **Repair: at most one batch,** a fresh engineer for this ticket's code, or a fresh test designer for `tests/acceptance/**` (DEC-906).
6. **`gov checkpoint`** (DEC-511), committed **before** the probe, so the head the probe judges is the last commit but its record.
7. **The FULL probe:** a fresh reviewer (brief A3 with `governance/project/briefs/JUDGEMENT.md` word for word, `--effort max`, read-only, launched sandboxed) on that head. It is the review of F-A's fix that DEC-804 item 1 named, and of batches 1 and 2 and the W1-02 revision. Above all:
   - **F-A and P-1:** no `GIT_*` variable of a hook reaches a child git call outside the project root;
   - **the freeze look-up:** git by absolute path, the pinned environment, 15 s, refusal on no git or time-out, never an allow;
   - **the close's calls:** no caller's `GIT_*`, index or trace variable reaches a test run, and who authors the close's commits is unchanged;
   - **the W1-02 revision:** it lowers no expectation beyond the 15 s;
   - **the sweep record:** every row true.
   
   F-B and D-1 are not findings (DEC-807). Every finding carries the two lines (DEC-808 item 4). Commit the probe record under `docs/probes/DAEO-0z8c/` only if it passes.
8. **Return** DONE (the probe passed; ready to merge), or PACKAGES. Run `trailer_gate.py` first. List every file you changed under:
   - `src/gov/close/**`, `src/gov/guard/**`, `src/gov/store/**` and `src/gov/decisions/**`;
   - why: merged-not-closed tickets' probes judged them (W2-03, W2-57, W2-77), and the orchestrator orders your merge after their closes (DEC-895).

**The park rule (DEC-941 item 2):** stop and return PACKAGES naming the cost (size in lines and hours, and what waits on it: W2-08's hooks) if any of these happens:
- the W1-02 revision does not converge in its one batch;
- a second repair batch is needed;
- a change is needed outside the ticket's paths or in another lead's paths;
- the probe fails on a finding an honest agent can hit in ordinary work that fails open or loses work. No new round.

**The untracked scratch file:** `tests/acceptance/W2-05/test_zz_scratch_b1.py` (a docstring, no test).
- Its removal was refused to you (the guard) and to the test designer (the permission prompt) in run 3. Do not try again, in any form.
- Commit by named paths only, so no commit takes it.
- Name it, with its path, in your return; the orchestrator removes it before the close.

**Running beside you:**
- W2-84 holds `src/gov/guard/reads.py`.
- W2-60a (round 3) holds `src/gov/launch/launcher.py`, `role.py`, `record.py`, `tests/unit/launch/test_runs.py`, `test_w1_28.py` and `test_w1_32.py`.
- W2-56 holds the rest of `src/gov/launch/**` and `src/gov/codeintel/**`; W2-20 holds `src/gov/launch/gate*`.
- W2-85 holds `tests/acceptance/W2-54/**`. W2-85 and W2-60a both hold `tests/acceptance/serial-only.txt`.
- W2-61 holds `src/gov/retrieval/measure.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 7 to 8 hours and 130 to 180 lines in all:
- the merge and the rebuild, about 45 minutes;
- the W1-02 revision and your check, about 2 hours (60 to 100 test lines);
- batch 2, about 1.5 to 3 hours (60 to 80 lines);
- one full run, about 95 minutes;
- the FULL probe, about 2 hours.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
