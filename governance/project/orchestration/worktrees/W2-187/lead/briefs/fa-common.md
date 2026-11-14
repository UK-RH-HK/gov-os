## The decided fix (the CTO, 2026-11-14, after review round 1 passed; DEC-1157 (12), DEC-1180 (4), DEC-1156 (7))
Review round 1 (`docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md`, read its findings F-A, F-B and row R1) passed. The CTO decided
to fix F-A in this ticket, with F-B and R1 riding along. These three, as described behaviour (DEC-136):

1. **F-A, the searched store is the declared store (S3, S6/I6, S7).**
   - Now: the `standing run` driver hands its `preflight`, `measure` and `judge` children the repository as their root
     (`src/gov/memaudit/driver.py:177,184,186`; the fresh `run` does the same). `gov retrieve` therefore answers from the
     repository's own `.gov-runtime/store.db` while the declaration names and checks the store link's store.
   - Then: when the repository's own store sits at another commit than the link's, every attempt faults on the
     store-commit check and the week ends `STOPPED fault`.
   - Wanted: on both the standing and the fresh path, the `preflight`, `measure` and `judge` children work in the store
     link's work tree at the audit commit (I6 already says the pre-flight's root is the link's work tree). So the commit
     of the store every search reaches equals the link's, and S7 compares the same store.
   - The acceptance cases' planted `gov` (`tests/acceptance/W2-187/fake_gov_x.py:102-103`) answers the plan's store
     commit whatever folder it runs in, so it cannot show which store a search reached. The new case needs a planted
     `gov` that answers the commit of the store in the folder it is run from (its cwd, or its `--root`).
2. **F-B, push only the scanned commit (S12, F7).**
   - Now: `push.py` scans the repository, then pushes the branch name, which git reads again after the scan. A commit
     landing on the branch during the scan is pushed unscanned.
   - Wanted: the commit the branch names when the scan starts is recorded. `git push <remote>
     <that sha>:refs/heads/<branch>` pushes it, so the remote's branch is the scanned commit. The line stays
     `PUSH pushed <remote> <branch> <12 hex of the scanned commit>`.
3. **R1, gitleaks on step 6's cron line (S11, S12).**
   - Now: cron's `PATH` does not hold `~/.local/bin`, so a declared push is blocked every week as
     `scan failed missing`.
   - Wanted: A9's ACT.md step 6 line (`memory_sets.walls_act`) carries
     `GOV_MEMAUDIT_GITLEAKS=<gitleaks>` before the wrapper. `<gitleaks>` is the absolute path `shutil.which("gitleaks")`
     gives when A9 runs, else the literal `<path to gitleaks>`. The rest of the line and I13's step-6 sentence stay.

**Path cases:** if any of this needs a file outside your allowed paths (for instance a W2-172 *test* file that pins the
repository as the children's root, as opposed to `w2_172_world.py`, `w2_172_git.py` or `test_w2_172_s7_digest.py`),
stop and return PACKAGES naming the path and the line. Never widen the paths yourself.
