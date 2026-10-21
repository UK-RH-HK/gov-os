---
type: probe
task: DAEO-xxgp
reviewer_session: 12ea90cb-f36c-440c-88c4-35468e9fec28
implementer_session: 71bddafd-ad32-4511-bab8-f543100b177d (eng-1), unknown (eng-2, stopped), d35a9d6b-99ba-4548-b2bd-15bfd21bdb55 (eng-3), b1a81f54-d4d8-4089-be35-810378fe6f2f (eng-4)
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
