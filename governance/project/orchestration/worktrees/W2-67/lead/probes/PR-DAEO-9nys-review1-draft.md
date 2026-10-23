# Draft probe record (failing; not committed, DEC-733): W2-67 round 1, review 1

Reviewer session cda3c0fa-e8a9-48ad-8b00-69f73e6c1a77, head f1c743b3ee92b95b31a5c29cde2e756c9ace969b.

**Verdict: fail**

**Head probed:** `f1c743b3ee92b95b31a5c29cde2e756c9ace969b` (w2/W2-67), round 1's change against `w2/integrate`.

**Step 0:** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys` failed with EROFS. (b) `git hash-object -w --stdin` and `git update-index --refresh` both worked.

**gov.__file__:** `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`

**gov retrieve:** used once (DEC-836) for DEC-898 and DEC-907. It returned `FACET_UNAVAILABLE` (lexical and semantic facets stale), so I read those register entries by id. No code-graph tool was available or used.

**Refusals:** no read refusals (DEC-849). Three Bash commands were refused by the guard's hook, and none was retried in the same form:
- a heredoc it could not read (DEC-409); I wrote the probe files into my scratchpad with the Write tool instead;
- a write path it could not resolve; that probe (refusal from a subfolder cwd) was dropped;
- quoted text it could not check; the clean-up was split into plain commands, and its `rm` then needed a permission that was not granted.

### Probed and found sound
- **The refusal.** All 13 KPI 6 cases pass. The refusal judges the parsed option, so the `=` form, the separate form, `PYTEST_ADDOPTS` and `-n 2` are all refused at the controller, and xdist workers are not refused. Only `GOV_ALLOW_BASETEMP=1` opens it.
- **Nothing ordinary passes `--basetemp`.** No test outside KPI 6's own passes it, and nothing uses pytester or sets an ini addopts. `gov close` passes none and strips `PYTEST_ADDOPTS`; `nightly.sh`, `close_queue.sh` and `retention_trial.sh` pass none either. The root conftest is loaded at the start for runs under `tests/` and for runs from the repository root (read).
- **What the clean-up may touch.** It acts only on `pytest-<digits>` directories that are not symlinks, inside a `pytest-of-<user>` root owned by the user that is not a symlink. It skips the run's own folder and anything within the retention of three. It keeps a folder whose lock cannot be read, whose `.lock` is held, or whose pid is alive in the same namespace (control runs green).
- **Runs that are protected.** A run with the conftest loaded and past its first setup holds its flock and is kept across namespaces (control green). An xdist run's controller holds the flock from the start of the run loop, before any worker setup, and is kept (P7 green).
- **The copies.** `copy_working_tree` sets `gc.auto=0` in the copy's own config after `git init` and before its first commit. W1-25, W1-26 and W1-27 all copy through it. Its git runs with the copy as HOME and `GIT_CONFIG_NOSYSTEM=1`. In git 2.43, auto-maintenance runs only the gc task by default, which honours `gc.auto=0` (read).
- **The guard unit test.** Patching `tempfile.tempdir` keeps `_is_in_scratch`'s meaning (it reads `tempfile.gettempdir()`), the patch is undone at teardown, and the case passes.
- **KPI 5.** No case or parametrization was removed and no skip or xfail was added; 107 assert lines were removed and 315 added. Spot checks were all equal or stricter:
  - W1-26's green base and its checks by their own entry name the planted id;
  - W2-02's type match;
  - the doctor section reader;
  - the rebuild helper still asserts ok;
  - rebuild_r8 now also snapshots HOME;
  - "rebuild needs only git" now runs with git and gitleaks on PATH (DEC-907 item 3).
- **Roles.** The engineer's commit `75a64b28` touches only `tests/conftest.py` and `tests/unit/guard/test_decide.py`. Every commit that touches acceptance files is `Role: independent-test-designer`, with a `Rewrite-Reason` wherever a case was revised.

### Findings

**F1 (high): the end-of-run clean-up removes the base folder of a run still going in another Bash command.**
- *What was done.* One shared TMPDIR, as a session's Bash commands share it. Each command ran in a PID namespace of its own, laid out as the sandbox does it: pid 1 an init, pid 2 a bash, then the command's processes. A live run A was started in one namespace. Then three failing runs (each leaves its folder) and one passing run of the repository's own probe case (`w2_67_tmp_probe.py`, which loads `tests/conftest.py`) were run, each in a namespace of its own. A took three forms:
  - (a) `gov close`'s own test runner, with one worker, on a small project, the way the unit close tests call it;
  - (b) a run of a project of its own under `flock`, standing for a run of another checkout or clone;
  - (c) a run with the conftest loaded, still in its first test's setup (a session fixture that has made its base folder).
- *What happened.* At the passing run's end, its clean-up removed A's base folder while A was running:
  - (a) the close reported `FAILED tests/test_close_case.py::test_close_case - AssertionError: LOST…`, with counts of 0 passed and 1 failed;
  - (b) A failed with "the live run's temp folder was removed under it";
  - (c) A errored in its fixture.
  
  Each time, A's `.lock` named A's own pid (5, 5 and 4 in their namespaces) and nobody held a flock on it. pytest's own clean-up in the three failing runs had kept the folder, since its lock was younger than three days. With everything in one namespace, the same sequence kept the folder and A passed.
- *What should have happened.* A base folder whose run is still going is kept, whatever Bash command or PID namespace it runs in and whether or not it loads this conftest. Past pytest's retention, a folder is removed only when its run is known to be over.
- *Why it happens.* The pid is looked up in the sweeping command's own namespace, where a process in another command cannot be seen; the conftest's own docstring says as much. Only runs that load this conftest and have finished their first setup hold the flock.
  - Every full run contains nested `gov close` runs that hold no flock: the 15 unit close functions that start a nested pytest, and W1-30's cases. They use the session's TMPDIR and pytest's default retention, so they also leave behind the three newer folders that put a live folder past retention.
  - Their pids are large, so they are never visible from a short foreground command.
  - Serial runs (`gov close`'s serial-afterwards run, the nightly's serial run) are unheld during their first setup. On a real suite file I saw the `.lock` unheld right after its base folder was made, but that setup finished within about 1 s.
  - By reading only: a sweeping run with `tmp_path_retention_policy=none` takes every other folder as a candidate, so no three newer folders are needed.
- *The tests miss it.* The KPI 4 "run still going" case plants a pid that is alive in the same namespace.
- Ordinary work: yes, because the lead brief starts every long run (verification, acceptance batches) in the background, so one session's pytest runs share a TMPDIR across separate PID namespaces. Any run of this repository that ends in another command meanwhile sweeps that TMPDIR; nested close runs are in every full run; and DEC-906 item 3 ends the one-run-at-a-time lock when W2-67 lands.
- Consequence: loses work

**F2 (medium): whether a killed run's folder is removed depends on pid coincidence.**
- *What was done.* A run was killed with SIGKILL mid-test; its pytest was the first command of its call, so pid 3, which is what the sandbox gives a first command (confirmed: first command pid 3, second pid 4). Three failing runs followed. Then a passing probe run was made as the first command of its own call (pid 3), and another as a second command (pid 4).
- *What happened.* The first sweep kept the killed run's folder: its `.lock` names pid 3, which in the sweeper's namespace is the sweeper itself. The second sweep removed it.
- *What should have happened.* A killed run's folder past retention is removed whatever pid the sweeper has (KPI 4: a full run leaves at most three base folders behind). The KPI 4 case plants a pid above pid_max, so it never meets this.
- Ordinary work: yes, because killed runs (timeouts, stopped sessions) and pytest as a command's first process are both ordinary in sandboxed sessions.
- Consequence: other (the folders stay for pytest's three days or until the session's temp folder goes; nothing is lost)

**F3 (low, already known): the KPI 4 static guard does not see an f-string `--basetemp=` in an argument list.** Batch 4's designer recorded and returned this in `README-W2-67.md`. The runtime refusal still stops any run that loads the root conftest.
- Ordinary work: yes, because the f-string is the natural way to write it.
- Consequence: other (only a nested run of a project outside `tests/` would get a per-run base folder, and it would sit inside the outer run's own base folder)

**F4 (low): the root `tests/conftest.py`, loaded by every acceptance run, sits outside the guard's acceptance protection, which covers `tests/acceptance/**` only.** An engineer ticket that names the file, as this one does under DEC-907, can change how every acceptance case is collected or run. This round's hooks pass every outcome through unchanged (read). This existed before the change.
- Ordinary work: no, because it needs a builder change that alters acceptance outcomes, which no ordinary change of this file makes.
- Consequence: fails open

**F5 (low): the KPI 4 exemption's "the folder is the case's own" rests on a parameter's name.** The refusal file's helper takes a parameter named `tmp_path`, and a new case could hand it any folder. Under `GOV_ALLOW_BASETEMP=1`, pytest first removes a given `--basetemp` folder that already exists. In the file's current text the exemption is no wider than the refusal's own cases.
- Ordinary work: no, because it needs a test designer to hand the refusal's own helper a folder outside the case.
- Consequence: loses work