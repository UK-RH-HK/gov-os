---
type: probe
task: DAEO-9nys
reviewer_session: 4b163b40-cc4b-4376-881a-d90a18bb7c86
implementer_session: b8477fde-3c58-456c-94d8-b508fdd782cc
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 915a764dd660d1ff2d08944042dd05c6fc02a6a4
---

# Probe record: W2-67 (DAEO-9nys), round 1, the second and last review (DEC-413)

- **What was probed.** Head `915a764dd660d1ff2d08944042dd05c6fc02a6a4` of `w2/W2-67` (CP-DAEO-9nys-0012): round 1's whole change against `w2/integrate` (merged in at `acb45c3c`, DEC-907). Above all: the root `tests/conftest.py` (the engineer's `75a64b28`, session `ed43112b-1a55-4e7d-9ddf-89554dccd159`, then `c8674271`, session `b8477fde-3c58-456c-94d8-b508fdd782cc`), which refuses a per-run `--basetemp` (DEC-907 item 2) and removes older base folders whose run is shown to be over (KPI 4); the copying fixture's `gc.auto=0` (`b20a481f`, the second test designer, DEC-907 item 1); the guard unit test's `tmp_path` (`75a64b28`); the KPI tests of batches 1, 3, 4 and 5 and the KPI 5 revisions of batches 1, 1b, 1c and 2.
- **The first review.** Session `cda3c0fa-e8a9-48ad-8b00-69f73e6c1a77`, head `f1c743b3`: fail on F1 (the clean-up removed a live run's base folder in another PID namespace; ordinary work: yes; loses work). Its record stays a draft. F1 and F2 were given as described behaviour to test-design batch 5 (`165ff06d`, session `8a305291-2872-40e4-b412-e6781de34863`), then to a fresh engineer (`c8674271`). This review finds them answered.
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session `4b163b40-cc4b-4376-881a-d90a18bb7c86`, 2026-10-24), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max; commissioned and judged by the ticket lead (an orchestrator-role session, DEC-137). It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in any tree.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`; only "yes" with "fails open" or "loses work" fails the probe. The lead's judgement: no finding is both; R1 is a row for the Wave 3 hardening pass, and F3, F4 and F5 stay rows.

## Rows carried from the first review (its words, unchanged at this head)

- **F2 (medium), answered at this head:** whether a killed run's folder was removed depended on pid coincidence.
  - Ordinary work: yes, because killed runs (timeouts, stopped sessions) and pytest as a command's first process are both ordinary in sandboxed sessions.
  - Consequence: other (the folders stay for pytest's three days or until the session's temp folder goes; nothing is lost)
- **F3 (low):** the KPI 4 static guard does not see an f-string `--basetemp=` in an argument list; the runtime refusal still stops any run that loads the root conftest.
  - Ordinary work: yes, because the f-string is the natural way to write it.
  - Consequence: other (only a nested run of a project outside `tests/` would get a per-run base folder, and it would sit inside the outer run's own base folder)
- **F4 (low):** the root `tests/conftest.py`, loaded by every acceptance run, sits outside the guard's acceptance protection, which covers `tests/acceptance/**` only.
  - Ordinary work: no, because it needs a builder change that alters acceptance outcomes, which no ordinary change of this file makes.
  - Consequence: fails open
- **F5 (low):** the KPI 4 exemption's "the folder is the case's own" rests on a parameter's name.
  - Ordinary work: no, because it needs a test designer to hand the refusal's own helper a folder outside the case.
  - Consequence: loses work

## The reviewer's record

Verdict: pass. One new row (Ordinary work: no), no finding that justifies a round.
work_completed: Step 0 and the standing checks. Read the ticket, the conftest, its diffs, batch 5, and DEC-898/905/906/907. Ran batch 5 and the other three W2-67 KPI files. Ran 9 probes of my own in separate PID namespaces sharing one TMPDIR, plus a probe of a large killed run's folder and a clean-up killed partway. Checked commit roles against paths, the per-test copiers (KPI 1), the guard test's revision and one KPI 5 revision.
files_changed: none
evidence: Step 0 (a) refused with `OSError: [Errno 30] Read-only file system`; (b) `git hash-object -w` gave 1ae28402…, and both it and `git update-index --refresh` exited 0. GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-9nys, toplevel /home/usain/gov-os-worktrees/W2-67, branch w2/W2-67, HEAD 915a764dd660d1ff2d08944042dd05c6fc02a6a4. `gov.__file__` = /home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py. Scratch: 8 inodes and 24K at start, 13 inodes and 52K at end (after the copies run: 11 and 44K). The copies run (about 50,000 files per case, two at once) and the big-folder probe (about 50,000 files per layout, built and removed in turn) peaked well under my 300,000 share; I did not sample the peak. pytest 9.0.3, xdist 3.8.0, git 2.43.0, pid_max 4194304.
tests: test_w2_67_sweep_namespaces.py 19 passed (4.03 s, -n 4); test_w2_67_temp_folders.py with test_w2_67_basetemp_refusal.py 18 passed (1.75 s, -n 4); test_w2_67_copies.py 6 passed (22.12 s, -n 2). All with `-o tmp_path_retention_policy=failed`, no `--basetemp`, no `-x`. Own probes: nsprobe.py (9 probes) and bigkilled.py, results below.
discoveries: pytest 9 makes no `.lock` at all when it keeps no folders (`tmp_path_retention_policy=none` or `tmp_path_retention_count=0`; pathlib.py lines 389–392). Such a live run's base folder counts as over, and a sweep removes it while the run is still going. pytest's own end-of-run clean-up does the same without this conftest (row R1). W1-05's support has a second `copy_working_tree` without `gc.auto=0`; it is not the race in I3 F9 / I4 F5, and W1-05 is not a named folder.
risks: Live runs given keep 0 have no protection, from the conftest or from pytest. That is outside DEC-898 item 2 and DEC-905, so it is a row. The engineer's known round 2 residual still holds: a killed run that never loaded the conftest is kept until pytest's three-day rule.
lessons: Every sandboxed Bash command is a PID namespace of its own (`/proc/loadavg` shows its last pid as 3–6). `unshare --user --map-current-user --pid --fork --mount-proc --kill-child` with the repo's `w2_67_ns_launch.py` reproduces that layout in one foreground command. A command holding `rm -rf "$TMPDIR/…"` is refused by the hook ("Quoted text in this command can't be checked before it runs"); let the probe script clean up after itself.
proposed_decisions: none
unresolved: none for round 1. Rows F3, F4 and F5 from the first review are unchanged: `test_w2_67_temp_folders.py` has not changed since f1c743b3. The engineer's residual (killed foreign nested runs kept until pytest's three-day rule) goes to round 2.
recommended_next_action: Commit this probe record, and treat round 1's review as passed; R1 is a row for the Wave 3 hardening pass, not a round.

---

Verdict: pass

**Head probed:** 915a764dd660d1ff2d08944042dd05c6fc02a6a4 (w2/W2-67)

**Step 0:** (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys` failed (`Errno 30, Read-only file system`); (b) `git hash-object -w --stdin` and `git update-index --refresh` both worked (exit 0).

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"` → `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`

**Classification of findings (DEC-809):** 0 findings with "yes" to both questions; 1 new row (R1: Ordinary work no, loses work). Rows F3, F4 and F5 are carried over unchanged.

**Probed and found sound**

- **F1 is answered in every form the first review showed.** batch 5 passes 19 of 19 at the head. On its own it covers `gov close`'s nested runner, a run of a project of its own, and suite runs in setup, mid-test and teardown, each under sweeper policies all, failed and none. My own runs, each live run as pid 3 in its own namespace sharing one TMPDIR:
  - **xdist live run (`-n 2`), sweeper with policy none:** the controller holds a shared flock on `.lock` and has written `.lock-held`. The folder was kept and the live run passed.
  - **Live run under policy `failed` (DEC-905's default):** three newer finished folders, sweeper on the default policy. Kept; it passed.
  - **Sweeper with the same pid (3) as the live run, policy none:** kept.
  - **A live run of a project of its own, sweeper making no base folder, policy none:** its `.lock` is unmarked and unheld. Kept by the pid rule.
- **F2 is answered.** A suite run killed with its whole namespace (as a timed-out sandboxed command is), xdist controller and workers together, with three newer folders: its folder was removed by the next sweep, and three folders were left. batch 5's same-pid and next-pid cases also pass.
- **batch 5 can fail for the fault.** Under the old pid rule its live cases (sweeper on the next pid) and its killed same-pid cases would go red.
- **Nothing outside pytest's numbered folders is removed.** The sweep checks the owner of `pytest-of-<user>`, takes only `pytest-<n>` folders that are real directories, and opens `.lock` with O_NOFOLLOW.
- **Two processes using one base folder share one lock correctly.** The lock is a flock, held per open file description. A sweep in the same process as a live run (or an in-process nested session) is refused LOCK_EX and keeps the folder.
- **Nothing in the code under test can make the conftest drop its lock.** No code in `tests/` or `src/` uses `closerange`, `os.fork` (apart from the launcher), multiprocessing, in-process `pytest.main` or pytester.
- **A large killed run's folder costs little to remove.** A 50,000-file killed suite run's folder was removed at the end of a one-test run in 0.48 s in total.
- **A clean-up killed partway leaves nothing kept.** It left a `garbage-*` folder of 2,962 files with no `.lock`, and pytest's own clean-up removed it at the next run's end.
- **`gov close` is unaffected.** It writes its results file with `mkstemp` in TMPDIR, outside `pytest-of-<user>`. It kills a timed-out run's whole process group. It passes no `--basetemp`; `src/` has no `basetemp` or retention option at all.
- **The `--basetemp` refusal holds for every ordinary form, and does not refuse ordinary runs.** 18 of 18 cases of temp_folders and basetemp_refusal pass: refused as `--basetemp=X`, as `--basetemp X`, through `PYTEST_ADDOPTS` and with `-n 2`; opened only by `GOV_ALLOW_BASETEMP=1`; runs without `--basetemp` pass, serial and parallel. xdist workers are exempt by `workerinput` only.
- **The refusal also covers runs started from the repo root or a subfolder.** In pytest 9 `pyproject.toml` makes the repo root the rootdir and confcutdir, so the root conftest is loaded for any argument under `tests/`, and for a run with no arguments from the root.
- **KPI 1 (copies):** `copy_working_tree` sets `gc.auto 0` before its first commit, and git 2.43's automatic maintenance respects it. W1-25 copies through the same function. test_w2_67_copies passes 6 of 6. W1-05 has a second `copy_working_tree` without `gc.auto=0`, but its per-test copies are fresh copies whose `.git` is never copied again, so the documented race cannot happen there; W1-05 is not one of this ticket's folders either.
- **Scope:** every engineer commit touched only `tests/conftest.py` and `tests/unit/guard/test_decide.py`. Every test-designer commit touched only the named acceptance files. The orchestrator touched only checkpoint records. Nothing else has changed since f1c743b3 except batch 5 and the conftest.
- **The guard unit test is not weakened.** `_is_in_scratch` reads `tempfile.gettempdir()` when called. With `tempfile.tempdir` pointed at `tmp_path`, both branches are still exercised.
- **W2-02's unmeasured case is stricter, not lowered.** The type must now be named outside the record's own path.
- **The untracked `w2_67_td4_plant.py`** holds only a docstring and is imported by nothing.

**Findings**

R1 — A live run given `tmp_path_retention_policy=none` or `tmp_path_retention_count=0` loses its base folder to a concurrent sweep (severity: low; row).
- **What was done:** a live run was started as pid 3 in its own namespace with one of those options. A passing run then ended in another namespace on the same TMPDIR, with three newer finished folders present.
- **What happened:** with keep 0, pytest makes no `.lock`, so the live run's folder had neither `.lock` nor `.lock-held`. The sweep counted the run as over and removed its folder, and the live run then failed ("vanished"). Sweepers tried:
  - a suite run on policy failed (p4);
  - a suite run that made no base folder of its own, so the conftest's sweep alone did it (p6, and p7 with a foreign live run on count 0);
  - a run of a project of its own without this conftest (p5). pytest's own end-of-run clean-up removed the folder just the same.
  - Under a sweeper on policy none, no newer folders are needed.
- **What should have happened:** a folder whose run is still going is kept. The conftest's own docstring promises that "a folder whose run cannot be shown to be over is kept", but a missing `.lock` is taken as proof. The conftest adds removal only where the sweeping run made no base folder (for example a collect-only run); otherwise pytest already does the same.
- Ordinary work: no, because DEC-898 item 2 and DEC-905 have every run keep pytest's retention of three under `-o tmp_path_retention_policy=failed`. A live run given policy none or count 0 is outside them, and pytest's own clean-up removes the same folder without this conftest.
- Consequence: loses work

**Carried rows (unchanged since the first review):** F3 (the KPI 4 static guard does not see an f-string `--basetemp=`), F4 (the root conftest sits outside the guard's acceptance protection), F5 (the KPI 4 exemption rests on a parameter's name). The engineer's round 2 residual is confirmed by reading and by p8's unmarked foreign `.lock`: a killed run that never loaded this conftest is kept until pytest's three-day rule.

**Scratch figures:** 8 inodes and 24K at start; 11 and 44K before and after the KPI runs; 13 and 52K at end. The heavy runs peaked within my 6 GB and 300,000 share; their files are removed by the cases and probes themselves. The nested runs inside my probes deliberately used the policy under test (default, none, count 0 or failed) in the probe's own TMPDIR. Every pytest run I started directly carried `-o tmp_path_retention_policy=failed`, and I never passed `--basetemp`.

**Read refusals met:** 0. One Bash command was refused once by the hook ("Quoted text in this command can't be checked before it runs"; it held `rm -rf "$TMPDIR/…"`). The probe was rerun without the `rm`, since the script removes its own folders; no second try of that form.

**gov retrieve:** used once, for DEC-905 and DEC-898 (retention and base folders). It answered `FACET_UNAVAILABLE` (lexical and semantic facets stale), so I read those decisions in `docs/DECISION_REGISTER.md` by their ids. No code-graph tool was available; code was read by grep in named folders.