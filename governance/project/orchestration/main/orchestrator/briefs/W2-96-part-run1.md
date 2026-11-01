You are the ticket lead for ticket `DAEO-ouet` (`W2-96`, the opaque acceptance runner, `gov accept`), profile FULL, priority 0 (the owner: "a priority now", DEC-959 item 6). You work only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `ab1ea26c5585`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:** the ticket file (`.tickets/DAEO-ouet.md`), whole; DEC-959 (items 6 and 7), DEC-957 (the work order), DEC-820 (c), DEC-317 in `docs/DECISION_REGISTER.md`; `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §2.7 (why the runner exists); how a `gov` command module is laid out (`src/gov/cli/main.py` and one existing command module, e.g. `src/gov/retrieve/`); the API-0002 envelope (`gov retrieve` for "API-0002").

## Why now
The five-rule guard lets every role read the acceptance tests (only writes are refused), so the owner's rule that the engineer sees "only pass or fail" needs a tool that enforces it: engineers run the acceptance tests through `gov accept`, which reports per KPI line and leaks nothing of the tests' content.

## The decisions for this run
- **The work order in parallel (DEC-959 item 7, DEC-963, the common brief's loop):** the independent test designer in the tests worktree (`/home/usain/gov-os-worktrees/W2-96-tests`, retrieving only from the integration branch's store) and the engineer in this worktree start at the same time, both from the ticket's KPIs. The test designer writes `tests/acceptance/W2-96/` (a planted ticket with a README map, tests that pass, fail, error and are unmapped, assertions carrying a recognisable marker string, so a leak is detectable by searching the output and any files left). The engineer builds `src/gov/accept/**` and its unit tests to the KPIs, never to the tests. When TESTS-READY appears, the engineer merges the tests branch and runs the tests once (through `pytest` on that folder this once, since `gov accept` is what it is building; say so in its brief).
- **Design note first, short** (in your scratch, `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour): how the README's KPI map is read (the form the designers' READMEs use today: look at three of them), how the child pytest's results are read without its text (JUnit XML parsed for outcome per node id, then mapped to KPI lines; stdout and stderr discarded), where its temp files go and how they are removed, the exit codes, and the JSON shape. It goes into both workers' briefs as text.
- **FULL:** after green, a fresh reviewer (brief A3, `JUDGEMENT.md`, effort max) probes for any path by which test content reaches the caller (stderr of the child, a crash message, a leftover JUnit file, a file name in an error, environment variables), and for any write in the repository. The fixed hook (ACT-GUARD-FIX-1) is in this worktree, so the reviewer can run commands.
- **KPI 6 (the brief change)** is the orchestrator's at merge: name it in your return, do nothing for it.
- **Running beside you:** nothing holds `src/gov/accept/**`. Do not touch `src/gov/cli/main.py` unless the command module convention requires it; if it does, return PACKAGES (shared file).
- **Verification (DEC-959 item 1):** this ticket's acceptance suite and unit tests, plus `select_tests.py` once before returning (full only if it says core). Through `verify_lock.sh` for a full run.
- **Budget:** about 6 to 8 hours. Scratch: 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-96`.

Return DONE (commits, suites, the passing probe record, residuals) or PACKAGES.


**DEC-968 (owner, 2026-10-31), overriding anything above about a full run:** never run the full suite, whatever your change, core included: the nightly runs it once a day. Your verification is the scoped set `select_tests.py` gives (always `scoped` now; for a core change it names `core_changed` and selects every suite the change can reach), run once before you return, in the close's form. A case that fails there and that your change did not cause (it fails on `w2/integrate` too) is named in your return for the CTO to deal with at once; one your change caused is yours to fix. Exit 2 from the selection (scope `refused`): return PACKAGES with its reasons.
