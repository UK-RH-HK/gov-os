task: Probe ticket DAEO-xxgp (W2-48, the test-result cache) at head `5f201781` for behaviour its acceptance tests miss, above all a reused or reported pass for a test that now fails (DEC-876 condition 1), and return the probe record's content.
status: DONE — the probe is complete and its judgement is fail. Four findings are "Ordinary work: yes" with "Consequence: fails open". The worst one: a test that the ticket's change breaks is silently dropped, and `gov close` passes.
work_completed: The Step 0 sandbox check passed. Check (a) was refused with `OSError: [Errno 30] Read-only file system`. Check (b) worked: `git hash-object -w --stdin` gave `1ae28402…` and `git update-index --refresh` exited 0. GOV_ROLE was `independent-auditor`, GOV_TICKET `DAEO-xxgp`, on `/home/usain/gov-os-worktrees/W2-48`, branch `w2/W2-48`. The probed head is `5f201781b4cc1cd834ea6d4cff0ebdda7406869b`. I read the ticket, DEC-875, DEC-876, `governance/project/orchestration/packages/P-W2-48-5.md`, the suite's README and support module, all the cache's source, the ticket's lines in `src/gov/close/command.py`, testmon 2.2.0's selection code, and the research record's sections 5 and 6. Then I ran 14 probes in temporary git projects under my session's temporary folder. Some drove `python3 -m gov.testcache run` or `nightly`, some drove the close's two-run form through the `Session` API, and some ran a real `gov close` in W2-01's governed projects through the suite's own support. Probing ran from 05:27 to about 06:00. I did not use `gov retrieve`, because the brief named every file I needed and I read them by name.
files_changed: none. Probe scripts and temporary projects lived only in my session's temporary folder. The worktree's `git status` shows only the sandbox's 12 character-device placeholders, dated 2026-10-16 (`.bashrc`, `.gitconfig`, `docs/source` and others); none came from me.
evidence: `gov.__file__` is `/home/usain/gov-os-worktrees/W2-48/src/gov/__init__.py`. F1 — a real close: close B exit 0, `ok: true`; its regression run says "passed 4, reused 4"; `test_uses_gamma` (fails under B's change) neither ran nor is listed; the nightly then exited 3 naming it (`failed`, cached `passed`). F1 — the store: after the change, a cached run of the acceptance folder alone removed `test_calc`'s record; later whole-suite runs exited 0 without it; `--no-cache` exited 3 with it `failed`. F1 — a re-close (close form through the `Session` API, two workers): close 1 pytest exit codes [0, 1] with `test_calc` failed; close 2 after an attempted fix, [0, 0] with only reused tests listed. F2 — run 3 exited 0 with `test_b_in` and `test_b_child` reused, where `--no-cache` exits 3 with both failed; a real close B exited 0 with `test_b_in` reused from close A's run `20261021T044842Z-2d5e33be`. F3 — close 1 exit 3 with `ACCEPTED_RED_PASSES` and `wrote_entries: true`; close 2 exit 0 with the entry's result `not run` and `test_listed` reused. F4 — a lead's run gave `ok: true`, exit 0, zero tests, with record `exit_code` 4, 4 and 3; the nightly gave exit 0, no faults, zero tests for a mistyped path and for a head whose conftest hook raises. Read refusals met: none. The 1-minute load stayed under 10; no CLOSE-RUNNING flag was present.
tests: No repository suite was run; the W2-48 acceptance suite was not re-run. Probe runs:
- the lead's run: P1 (serial and two workers), P3 (twice), P6, P7, P8, P11 (two forms), P12, P14;
- the nightly: P9;
- the close's form through `Session`: P10 (twice), P11 (one form), P13;
- a real `gov close` through the suite's support: P5, P1 at the close, P10 at the close with the nightly, P13 at the close (twice).
The two P13 real re-closes were refused only for my own commit sequencing (a containment finding, then `TRAILER_MISSING`). Their test part is the evidence: no test ran and no test finding was raised.
discoveries:
- F1 (critical) — a changed test that shares its file with an unchanged test, or is one case of a parametrized test, is dropped after any cached run whose paths left it out. The close's own acceptance run is such a run, and so is a lead's run of its folder. The dropped test is neither run nor listed, the run exits 0, and it stays dropped until its file changes or a `--no-cache` run. Ordinary work: yes. Consequence: fails open.
- F2 (high) — the work of a module-, session-, package- or class-scoped fixture is credited only to the first test that sets it up: in-process code, Python children, and class setups. The four views the lead fixed (a child's read, `git` on the project, an unknown program) also hold only for that first test. The other tests using the fixture are reused after a change that breaks them. Ordinary work: yes. Consequence: fails open.
- F3 (high) — a listed accepted red that passes refuses one close; afterwards it is reused, read as `not run`, and refuses no more. Ordinary work: yes. Consequence: fails open.
- F4 (medium) — the lead's run and the nightly ignore pytest's exit code, so a run that ran nothing reads as passed or as a clean night. Ordinary work: yes. Consequence: fails open.
- Rows R1 to R8 (Ordinary work: no) and other observations O1 to O3 are in the record below.
risks: Merged as it stands, F1 and F2 let closes pass with red tests, and the shared entries keep the loss for later closes. The nightly names such a test the following night, but only after the merge, and not at all on a night when pytest runs nothing (F4).
lessons: For the test designer:
- KPI 1's cases each use one whole-suite run. F1 appears only when the close's acceptance-then-regression sequence, or a lead's "my folder, then everything", meets a changed test that shares its file.
- The suite's honesty check compares the record with the tests that ran, so it cannot see a test that neither ran nor is listed. Comparing the record with the collected set would.
- Fixtures of wider scope, accepted reds under reuse, and pytest's exit code have no case yet.
proposed_decisions: Classification: F1 to F4 are yes with fails open; R1 to R8 are no (rows for the Wave 3 hardening pass); O1 to O3 are other. Recommendation: the lead's resume, or the DEC-876 condition 4 fallback package, carries F1 to F4, F1 first, as evidence that condition 1 (fail safe) is not yet met. Confidence: high.
unresolved: Not probed or not settled:
- F1 combined with the serial-only run afterwards;
- a close cut at its time limit (R7, from reading only);
- `git` asked about ignored files of the project (not isolated: the re-run I saw came from another change);
- two runs at once on one store;
- the guard's view of `python3 -m gov.testcache` under each role;
- re-measuring the time saved.
The known red P-W2-48-7 is not re-reported.
recommended_next_action: The lead commits the probe record below and routes F1 to F4 to a test designer and to its package under DEC-876 condition 4.

```
---
type: probe
task: DAEO-xxgp
reviewer_session: 12ea90cb-f36c-440c-88c4-35468e9fec28
implementer_session: <the lead fills it>
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 5f201781b4cc1cd834ea6d4cff0ebdda7406869b
---

# Probe record: W2-48 (DAEO-xxgp), the cache drops changed tests, credits a wider fixture's work to its first test, silences the accepted-reds ratchet, and reads an empty run as passed

- **What was probed.**
  - Head `5f201781`, with this worktree's `src/` on every command (DEC-732).
  - Temporary git projects built from scratch, run through `python3 -m gov.testcache run|nightly`.
  - The close's two-run form (acceptance folder, then the rest, one set of entries; with and without two workers) through the cache's session.
  - A real `gov close` in W2-01's governed projects, through the suite's own support.
  - Areas covered: fixtures of every scope and class setups; children; `git`; unknown programs; reads, listings and package data; environment variables; conftest import-time reads; parametrized cases; refused and repeated closes; accepted reds; `--no-cache`; the nightly; pytest's exit codes.
  - No repository suite was run.

- **What was found.**
  - **F1 (critical): a test the change breaks is dropped without a word, and the close passes.**
    - Done: ticket B's change made `tests/unit/test_mixed.py::test_uses_gamma` fail; that file also holds a test the change does not reach. Then `gov close PROJ-bbbb`.
    - Happened: the close passed (exit 0). Its regression run reported "passed 4, reused 4". The failing test neither ran nor appeared anywhere in the record, and the shared entries were written. The nightly named the test the next night.
    - Same outcome in the close form with or without workers; in a re-close after a refused close whose attempted fix still failed (pytest exit codes 0 and 0); for one case of a parametrized test; and in a lead's run of its acceptance folder followed by the whole suite.
    - Persistence: the test stays dropped in every later cached run, until its file changes or a `--no-cache` run.
    - Behaviour: the earlier run on the same entries left the test out of its paths, and its record was removed at that run's end. The next run judged the whole file unchanged from its other tests and did not collect it. Having no record, it was not counted as reused either.
    - Should: run it and refuse (KPI 1, KPI 5, failure KPI 1; "a test whose code changed never gets a reused result").
    - Ordinary work: yes, because every close runs the ticket's acceptance folder before the regression on the same entries, a change that reaches one test of a file and not another is the usual case, and refuse, fix, re-close is daily work.
    - Consequence: fails open.
  - **F2 (high): a wider fixture's work is credited to its first test only.**
    - Done: module-scoped fixtures that call a project function in-process, or start a Python child, each used by two tests; the code they run was then changed so the second test fails. Lead runs, serial and with two workers, and a real close.
    - Happened: the first test re-ran; the second was `reused` with exit 0, where an uncached run fails it. At the close, ticket B closed with that test reused from ticket A's close.
    - The lead's four fixed views hold for the first test only: a Python child's read of an undeclared file, `git rev-list` on the project, and `cat` taken in a module-scoped fixture each left the second test reused after the change (the uncached run: 3 failed).
    - Class setups (`setup_class`, `setUpClass`) behave the same, even for a change in the setup's own body.
    - Should: every test using the fixture's result re-runs when what the fixture ran or read changes, or always runs when that is not seen.
    - Ordinary work: yes, because this suite has 243 fixtures of module, session, class or package scope in 111 files. For example, W1-20's session fixture `graph` loads the store once through a `gov.store` child, and its tests only ask closures of it.
    - Consequence: fails open.
  - **F3 (high): the accepted-reds ratchet refuses once, then never again.**
    - Done: `accepted_reds` listed a test that passes; ticket A was closed twice with nothing changed.
    - Happened: close 1 refused with `ACCEPTED_RED_PASSES` and wrote the shared entries. Close 2 reused the test, the ratchet reported the entry `not run`, which refuses nothing, and the ticket closed.
    - The record of close 2 says `reused` and `not run` for the same test. Any later close behaves the same while the test's code is unchanged (same mechanism; not run separately).
    - Should: refuse every close until the entry is removed (DEC-757 item 2, DEC-762).
    - Ordinary work: yes, because a listed red starts passing whenever its fix lands or a flaky red passes, and the refusal falls on whichever close runs it first.
    - Consequence: fails open (the ratchet; the stale entry later accepts a real regression of that test).
  - **F4 (medium): a run in which pytest ran nothing reads as passed.**
    - Done: a lead's run given a mistyped path (alone, and beside a good path), or with a conftest hook that raises at collection; the nightly given a mistyped path, or at a head whose hook raises.
    - Happened: every answer was `ok`, exit 0, with zero tests. The lead's record buries pytest's exit code 4 or 3; the nightly's record has none and reports no cache fault.
    - Should: nothing measured is a failure. The close itself refuses such a run.
    - Ordinary work: yes, because a mistyped path or a conftest change that breaks collection is an ordinary slip, and the nightly's fresh clone lacks the tree's ignored files.
    - Consequence: fails open (a lead's verification and the nightly backstop).
  - **R1:** a module-level read in the conftest of the run's own path, which pytest loads before collection, is not attributed. That is the ticket's acceptance conftest in the close's acceptance run, not only a root conftest. Reused after its file changed.
    - Ordinary work: no, because no conftest or support module here reads a file at import time, and there is no root conftest.
    - Consequence: fails open.
  - **R2:** a read through `pkgutil.get_data` is taken for the import machinery's own read; reused after the package data changed.
    - Ordinary work: no, because neither `src/gov` nor the tests use it.
    - Consequence: fails open.
  - **R3:** listing the current folder with no argument (`os.listdir()`, `os.scandir()`) is not seen; reused after a file was added.
    - Ordinary work: no, because nothing here uses that form.
    - Consequence: fails open.
  - **R4:** environment variables other than `PYTEST_ADDOPTS` and `PYTEST_PLUGINS` are not keyed; a test depending on one was reused under another value.
    - Ordinary work: no, because closes run in one environment, and a lead's run reusing a close's pass in its own environment is not the gate; the nightly is the backstop.
    - Consequence: fails open.
  - **R5:** reads outside the project are reused unless declared. W1-16's and W1-32's dev-tier tests (`GOV_DEV_TIERS`) carry `local_only`, not `unseen_inputs("outside-read")`. Read from the code; not run.
    - Ordinary work: no, because the workbench changes only by the owner's hand, and this is the fault the nightly's own planted case catches.
    - Consequence: fails open.
  - **R6 (known):** an existence check is not seen. The suite has some.
    - Example: `test_w2_54_audit_report.py::test_no_schema_file_of_w2_02_s_other_types_comes_with_it` stats a file in `template/governance/kernel/schemas/` (declared: a new file re-runs every test) and in `governance/kernel/schemas/` (undeclared: a file added there alone is reused).
    - Ordinary work: no, because such files arrive in both folders together.
    - Consequence: fails open.
  - **R7:** a close cut at its time limit still writes its entries, keeping testmon's passes without the plugin's skipped and unseen marks. Read only, not reproduced.
    - Ordinary work: no, because it needs a timeout, a test newly unseen in that run, and a later unseen change.
    - Consequence: fails open.
  - **R8 (known):** no root `conftest.py` exists, and no SQLite or C-library read of a repository path was found.
    - Ordinary work: no.
    - Consequence: other.
  - **O1:** over-selection that fails safe. A module-level read in a conftest loaded during collection made every test of the run always run; listing a folder inside a declared glob always runs.
    - Ordinary work: yes, because the research record counts 7,076 such tests.
    - Consequence: other (cost against DEC-876's target).
  - **O2:** record honesty. F1's dropped tests appear nowhere, and F3 states two results for one test; the suite's honesty check cannot see a test that neither ran nor is listed.
    - Ordinary work: yes.
    - Consequence: other.
  - **O3:** the research record's time-saved section states what was measured and how. It used the lead's single runs standing in for the close, so it did not exercise the acceptance-then-regression sequence where F1 arises.
    - Ordinary work: yes.
    - Consequence: other.
  - **What holds:**
    - a test's own undeclared reads and listings, and a Python child started directly by a test, make it always run;
    - `git` run directly on the project is keyed by head, refs, status, diff and untracked files, so an uncommitted change in a lead's tree re-runs it;
    - unknown programs and shells started directly always run;
    - failed, errored and skipped results are not reused while the test is collected;
    - an unreadable store runs everything;
    - shared entries are written only by a close from a clean tree;
    - a lead's run writes only in its own tree;
    - nothing deletes or overwrites a user's file;
    - cache faults in the close become findings, and the close refuses pytest exit codes 3 and 4;
    - listed reused tests carry the run and commit of the close they came from;
    - `--no-cache` runs everything and restores dropped records;
    - the nightly names a failing test whose cached result was a pass.
    - No way was found for a role to write outside its scope, for an implementer to change the acceptance tests, or for work to be lost.

- **Judgement.** fail. F1, F2, F3 and F4 are each "Ordinary work: yes" with "Consequence: fails open", which fails the probe under the judgement rules (DEC-801 to DEC-809). R1 to R8 are rows for the Wave 3 hardening pass, and O1 to O3 are other.
```