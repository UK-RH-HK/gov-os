Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent test designer, DAEO-emq1 (W2-115), FULL, class C3 — one named revision (build run 2, td-2)

Budget: projection 2 USD. Keep your context short: read only what this revision needs.

You are a fresh independent test designer (MR-3) for ticket DAEO-emq1 (W2-115), in
`/home/usain/gov-os-worktrees/W2-115-tests` on `w2/W2-115-tests` (DEC-963), which holds the acceptance tests
(`tests/acceptance/W2-115/`, written at 01ececd0b758). Step 0 (the sandbox check), the standing rules, the writes
(`tests/acceptance/W2-115/**` only), the never-read rule for `src/gov/close/`, the Interface and the return are those
of the previous designer's brief, copied beside this one:
`/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/brief/td-1.md` (read it whole). Do step 0 first and
report it first. **Every pytest run adds `PYTHONUSERBASE=/home/usain/.local`** to its `env` (pytest is not found under
the empty `HOME` otherwise).

## The revision (with a `Rewrite-Reason:` line in the test's docstring)

`tests/acceptance/W2-115/test_w2_115_reds.py::test_no_clone_is_built_for_the_nightly_baseline` fails on the built
code with: `a nightly-baseline clone was built: ['<tmp>/w2_115_unowned0/project/.gov-runtime/close/clone/docs/close/nightly']`.
That folder is the S10 warm clone (`.gov-runtime/close/clone/`, the Interface's place), a checkout of the head under
test, which naturally holds the project's committed `docs/close/nightly/` records. S4's line forbids a clone built
**for the nightly baseline** (a checkout of the nightly's recorded commit, or a folder made to rebuild that baseline),
not the warm clone S10 requires. Revise the check so that it fails on a checkout at the nightly record's commit, or on
any new clone or worktree other than `.gov-runtime/close/clone/` (e.g. a new `git worktree list` entry, or a folder
holding a `.git` that points at the nightly's commit), and passes with the warm clone alone. Keep it as strict as that
allows. Rewrite-Reason: S10's warm clone is the Interface's (DEC-1001 (b), DEC-1112 (3)); S4 forbids only a
nightly-baseline clone (DEC-1083).

Touch no other case. The lead's answers to two of your proposals stand as you wrote the tests: P-W2-115-TD-1 (a),
load-sensitive = a serial-only entry of kind `latency`; P-W2-115-TD-2 (a), the batch as `gov.close.batch run <ticket>...`
with unmerged `w2/<wbs>` branches.

## Check and commit

1. Run the revised case and its file on this branch (today's integrated code: the case need not pass here, say what
   it shows), then `git -C /home/usain/gov-os-worktrees/W2-115-tests log --oneline -1`.
2. Commit only `tests/acceptance/W2-115` with td-1.md's commit form, subject
   `W2-115 acceptance: S4's no-baseline-clone check spares the S10 warm clone (td-2)`; quote `git log --oneline -2`
   and `git status --short`. Return as td-1.md says.
