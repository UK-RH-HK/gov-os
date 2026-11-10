Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-66c-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-66's DEC-891 record case counts code-read files as records (W2-66c, DAEO-btcs)

You are a fresh **independent test designer**, launched under W2-66c's ticket (`.tickets/DAEO-btcs.md`: W2-66's
live-map suite). The CTO decided this item as a delegated P2 (DEC-1112 (3)), option (a): you revise the case so that
files read by code are not counted as records.

## The red (at integrate, alone)
- **The case:** `tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only[governance/project/orchestration/]`.
- **The failure:** "records of governance/project/orchestration/ the record-only list leaves out:
  ['governance/project/orchestration/tools/indep-schemas/auditor-result.schema.json', … checker-result …,
  indep-counts …, labeller-result …, writer-result …]".
- **The cause:**
  - The case calls every tracked file under a DEC-891 place a record unless its suffix is a code suffix (`CODE_SUFFIXES`).
  - W2-149 (`6f811da36`) added JSON schemas under `governance/project/orchestration/tools/indep-schemas/`, which
    `governance/project/orchestration/tools/indep_launch.py` reads.
  - They are not records. Listing them record-only would let a change to them skip their tests, which fails open for
    the selection. That is why the CTO chose (a), not (c).

## The task
1. Revise the case so that a file under a DEC-891 place that code reads is not counted as a record.
   - The test map already knows, in its own terms, which files run suites: a file the test map couples to a suite
     (any section other than `record_only` places it), or one a tracked `.py` beside it in the same `tools/` folder
     reads.
   - Choose the narrowest rule that is decidable from the repository alone, and say why.
   - Do not exclude a whole folder by name if a narrower rule works.
   - Keep the case failing for a real record (a `.md`, a ticket, a probe, a close record) that the list leaves out.
2. Keep every other case of the file as strict as it is. Check
   `test_paths_dec_891_does_not_name_are_not_record_only` and the "record-only list hides code paths" case still
   hold.
3. One README line in W2-66's README, and a docstring paragraph `Rewrite-Reason: …` on the case.
4. Every commit carries `--trailer "Rewrite-Reason: DEC-891, DEC-1112 (3): a file under a DEC-891 place that code reads (W2-149's result schemas, read by indep_launch.py) is not a record; record-only would skip its tests"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-66c-d10-tests`, branch `w2/W2-66c-d10-tests`, at integrate
  `9ca161a6f` plus the CTO's ticket commit `25d72380f` (W2-66c in progress).
- Write only `tests/acceptance/W2-66/**`.
- Do not touch `governance/project/test-map.yaml` or W2-149's files.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66c-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder;
  - `python3 -m pytest tests/acceptance/W2-66 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --optin=lifted,breadth`.
  - Report the counts before and after.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-66c-d10-tests` only, with `--trailer "Task: DAEO-btcs" --trailer "Implements: DEC-1109, DEC-1112"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 25 minutes. Return the twelve fields, short:
  - the rule chosen and why;
  - the counts;
  - the head commit.
