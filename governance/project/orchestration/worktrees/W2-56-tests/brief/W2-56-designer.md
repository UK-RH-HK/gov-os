# W2-56 — the independent test designer's brief (DAEO-wnnz), the first half

You are the independent test designer for **W2-56** (`.tickets/DAEO-wnnz.md`): `gov launch` usable for every worker
(the code graph in the session's temp folder, the write list, no placeholders, a cleaned environment, the refused
arguments, the start lock, the reranker socket, signals and temp folders). Read the ticket in full first, including its
notes. Profile FULL: thorough, every success and failure line with its edge cases.

**The split (the owner's DEC-1099 (1)):** the sandbox-and-guard experiment
(`governance/project/orchestration/packages/SANDBOX-GUARD-EXP-1.md`; read §0, §3 and §5) decides whether launched
workers get a sandbox generated from the path map (set-up B) or the path-map guard alone (set-up A). **Write only the
acceptance tests whose expected outcome is the same under either result.** Any KPI line (or part of a line) whose test
would differ by that result is left out and listed in your record as "after the experiment", each with one line on why
it depends on the result.

The CTO's first reading, for you to confirm or correct line by line from the ticket and the package (you judge; say
where you differ and why):
- **Likely independent:** KPI 1's suite half (one daemon folder per test session, cleaned at its end; the real daemon
  only where named, the tool off PATH elsewhere), KPI 4 (no placeholder name reaches a commit by an ordinary
  `git add`/`git commit`), KPI 5 (the cleaned process environment), KPI 6 (the refused arguments, spaced and `=` forms),
  KPI 7 (three launches at once in worktrees sharing one `.git` do not fail on a lock), KPI 12 (signals reach the
  process group; temp folders removed on every ending), KPI 14 (the template's one allow rule `Bash(gov launch:*)`),
  KPI 15's "none left under /tmp after a worker's run, whatever its exit", and the failure lines "a launch whose
  sandbox cannot be built starts" only insofar as today's refusals must keep refusing ("a refusal the launcher makes
  today no longer refuses"), "a parent's CLAUDE*, GOV* or PYTHONPATH value in a launched session", "a placeholder file
  in a commit", "a raw claude launch stays unallowed in the template".
- **Likely after the experiment:** KPI 1's "inside a launched, sandboxed worker" half, KPI 2 (the sandbox's write list
  refused by the operating system), KPI 3 (a pattern the operating system cannot hold), KPI 8 and KPI 9 (the sandbox's
  one socket and nothing else widened), KPI 10 (measured, sandboxed), KPI 11 (a sandboxed session's fallback logged;
  note also W2-145, `DAEO-2tfd`, which removes the private fallback: name the clash in your record), KPI 13 (suites
  inside the sandbox), and the failure lines about writes outside the list, `/tmp/gov-cbm-<uid>` on the write list, an
  allowed path widened, and the sandbox's sockets.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-56-tests`, branch `w2/W2-56-tests`, made from `w2/integrate` today.
- You write only `tests/acceptance/W2-56/`: the cases, a `conftest.py` and support module if needed, and a `README.md`
  whose map the runner reads (header `| KPI line | Test (node id) | On integrate | Why |`, one id such as `S1` in each
  KPI cell, the ticket's lines numbered S1 … in order, the test in backticks with its full node id, as
  `tests/acceptance/W2-133/README.md`). Every KPI line appears in the map: a line left for after the experiment is
  marked so in the "Why" column with no test. State there the interface the tests assume (the launcher's refusal
  wording, the environment it passes, the start lock), so the engineer builds to it.
- **Your record:** your whole return (the twelve fields below, with the "after the experiment" list) is your session's
  **final message**, in full: the launcher keeps that message in this worktree's
  `.gov-runtime/scratch/lead/log/W2-56-designer.json`, which is the record (your session cannot write that folder
  itself, and its own scratchpad is deleted when it ends). Put the "after the experiment" list in the README too.
- You may read any code on `w2/integrate` (there is no implementation of this ticket yet): `src/gov/launch/launcher.py`
  (`build_settings`, `sandbox_faults`, `_check_cli_args`, DEC-313's refused arguments, how a session is started),
  `src/gov/codeintel/__init__.py` (`DAEMON_BASE`), the kernel template's settings, and the existing tests under
  `tests/unit/launch/` and `tests/acceptance/W2-58/` (if present) for how the launcher is driven with a stub CLI so no
  real session starts.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** there is none yet; never open
  `/home/usain/gov-os-worktrees/W2-56` or the branch `w2/W2-56` if either appears, and never read the engineer's files
  on this ticket. You work from the ticket's KPI lines, the package and today's integrate code only.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree, never from `/home/usain/gov-os-worktrees/` or `/home/usain/`, so no search can reach this ticket's engineer
  worktree; if a search shows you a line of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- No GPU, no model, no network, no real `claude` session (a stub CLI that records its arguments and environment), no
  real code-graph daemon (a stand-in).
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names (where the sandbox allows it), with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56-tests/src`, and run
  `python3 -m gov.cli.main accept W2-56 --root /home/usain/gov-os-worktrees/W2-56-tests` to show the runner reads your
  map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-56-tests`, only `tests/acceptance/W2-56/`, with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-799, DEC-1099" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished: do not end with a background
  run still going.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), the "after the experiment" list (line, why), the commit, `gov accept`'s
counts, `TESTS-READY` text (for the first half), and anything untestable or ambiguous as `discoveries` or a decision
package with your recommendation and confidence.
