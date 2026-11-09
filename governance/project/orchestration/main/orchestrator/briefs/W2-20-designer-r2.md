# W2-20 — the independent test designer's brief, round 2: the F2 line and the points settled (DAEO-r30l)

You are a fresh independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`). Round 1 (`61682b3e2`, 146 cases in
`tests/acceptance/W2-20/`, KPI ids S1-S20 and F1-F6 in its README) is on your branch. Since then the CTO has:
- added a KPI line for **W2-136's F2 entry criterion** (marked DEC-1088 (5)(b)), with `src/gov/launch/plan_check.py`,
  `launcher.py` and `command.py` in the paths: the plan check reads the current tickets and the approved ready list
  from the main tree (or a named path the dispatcher keeps), never a lead worktree's stale copies, and a plan override
  is written to a launch log as well as standard error;
- settled round 1's packages P-1 to P-6 (the ticket's section "The designer's points settled").

**Your job:** (1) the F2 line's cases: give it the next id (S21) in the README's map. (2) Bring round 1's cases into
line with the settled points where they are not already (P-1 (a): the launch option; P-2 (a)+(c): a full set of slots
never refuses a session, a launch refused on the slots only when their reading cannot be taken; P-3 (a): a case for
`gov resources --init-config` writing a dated, sourced template and refusing to overwrite; P-4: the measured case on
time-bound programs; P-5 (a): the rebuild peak as a third figure from slot holders of kind `rebuild`, a rebuild not
holding the verification lock; P-6 kept). Each change to a round-1 case is its own commit with
`--trailer "Rewrite-Reason: DEC-1097 (8)"`, named in your return. (3) **Port the 10-17 designer's revisions of other
tickets' cases** onto today's versions: on `w2/W2-20`, test-designer commits `173e8e97a` and `d82619c36` revised
`tests/acceptance/W1-07/README.md`, `test_w1_07_recorded_commands.py`, `w1_07_support.py`,
`tests/acceptance/W1-26/README.md` and `tests/acceptance/W1-32/test_w1_32_command_set.py` so the recorded `gov`
commands include `resources` (W2-20's command). Integrate has revised the same cases since (`accept`, DEC-970;
`release` excused until recorded, DEC-753). Read only those two commits' changes to those five files
(`git show 173e8e97a -- <file>`, `git show d82619c36 -- <file>`: they are tests, not the implementation) and make
today's versions also expect `resources` (keeping `accept` and the `release` excuse), each file's change committed with
`--trailer "Rewrite-Reason: DEC-1097 (8)"`. You may write those five files for this. (When the CTO merges integrate
into `w2/W2-20`, it keeps integrate's version of them, so your port is the one that lands.)

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests` (integrate merged in today).
- You write only `tests/acceptance/W2-20/`.
- You may read any code on `w2/integrate`: `src/gov/launch/plan_check.py` (`check_lead`, how it finds the tickets and
  the ready list today), `src/gov/launch/launcher.py`, `command.py`, and `tests/acceptance/W2-136/` for how a planted
  ready list and a lead check are driven without starting a session. For F2, plant a main tree and a lead worktree
  (a git worktree of it) whose tickets and ready list differ: the check must follow the main tree's.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** it exists on the branch `w2/W2-20` and in the
  worktree `/home/usain/gov-os-worktrees/W2-20`. Never open that worktree and never `git show`, `git diff` or
  `git log -p` anything on that branch.
- **The exclusion line (DEC-1093 (2)), for you:** keep every search inside your own worktree, never from
  `/home/usain/gov-os-worktrees/` or `/home/usain/`; if a search shows you a line of the implementation anyway, stop
  and say so.
- **Search again once (DEC-1092 (1)):** if a search (Grep and Read; no `gov retrieve` in the sandbox) does not answer,
  search once more in your own, different words; then answer from both, with path and lines, or say "not found".
- Planted machines and stores only; no GPU, no model, no network, no real servers, never the real `~/.gov-os/`.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-tests/src` (through the heavy slot where the
  sandbox allows it), and `python3 -m gov.cli.main accept W2-20 --root /home/usain/gov-os-worktrees/W2-20-tests`.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Commit** on `w2/W2-20-tests`, only `tests/acceptance/W2-20/`, with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log; it is
the record): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the new and changed cases
(node id, KPI line, red or green on integrate, why), the commits, `gov accept`'s counts, `TESTS-READY` text.
