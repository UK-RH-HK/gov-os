You are the ticket lead for ticket `DAEO-9279` (`W1-28`, "gov pause"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-28` on branch `w1/W1-28`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). STANDARD has no reviewer step.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

**An engineer starts only on decided ground.** If the test designer returns packages, you return PACKAGES and no engineer runs, even when the tests already follow the recommended options.

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `src/gov/pause/**`, `tests/unit/pause/**`.
- Its dependencies are closed: W1-02 (the guard, which already reads the freeze flag and denies writes while it is set), W1-07 (the command line) and W1-09 (the ticket wrapper `gov.tasks`, claims included). Read their residual sections in `governance/project/bootstrap.md`, and "W1-46 residuals" and "W1-25 residuals".
- Read the Contract's CAP-05 with its covers items (CAP-05.a to CAP-05.d), and in `docs/DECISION_REGISTER.md`: DEC-176 and DEC-180 (the runtime directory and who may write it), DEC-311 (the freeze flag's deny rule in launched sessions), DEC-182 (trailers), DEC-320 (a command that only orchestrator-role sessions run), DEC-322.
- **DEC-317**: `gov pause` is a reserved command, built by the file `src/gov/pause/command.py` alone. The convention a command module follows is the docstring at the top of `src/gov/cli/main.py`: read it word for word and give it to the engineer. `src/gov/cli/**` is outside this ticket's paths. `src/gov/checkpoint/command.py` and `src/gov/readiness/command.py` are working examples.
- W1-07's suite holds `gov pause` to `NOT_IMPLEMENTED` today; the test designer revises that case as a planned revision ("planned: command implemented", DEC-190).
- **A W1-46 builder test uses `pause` as its stand-in for a not-yet-built command**: `tests/unit/launch/test_command_modules.py`. Building `src/gov/pause/` will break those cases, as building `checkpoint` did. It is outside this ticket's paths: when it breaks, you (orchestrator role, not the engineer) rename the stand-in to another reserved command that is not built yet and is not `close`, with the assertions unchanged, in a commit of your own, and say so in your return.
- **The freeze flag is the guard's own state.** In this repository only the owner freezes: no test and no worker sets, clears or touches this worktree's or the main tree's real freeze flag, and nobody runs `gov pause` against this repository. Every test builds a temporary repository and pauses that. A test that leaves a temporary repository frozen cleans it up.
- Things the test designer settles from the sources, or returns as packages, never as guesses:
  - how "pause state appears in `gov status`" is delivered when `gov status` lives in `src/gov/cli/commands/status.py`, outside this ticket's paths (what `gov status` already reports about the flag; if it reports nothing, that is a package with options, not an edit);
  - what "the next write by any role is denied" needs from this ticket beyond setting the flag the guard already reads, the orchestrator and the owner included, and how `gov pause --off` can run while writes are denied;
  - what "runs only on the owner's or the orchestrator's invocation" means for a command (which role values, and what a worker's call returns);
  - what "releases every claim" changes in the tickets and what "records the cancelled sessions" writes, given that the command cannot stop a process;
  - what `--rollback <ticket>` reverts (commits found by the `Task:` trailer, merges, an already reverted commit, a ticket with no commit), that it uses `git revert` only, and what a repeat does;
  - where "a record in the ticket" is written.
- This command touches the guard's state and reverts commits: a package on what it may do is likely owner-level. Return it; do not settle it.

## What you do, in order

1. `git merge w1/integrate` if it is not already up to date.
2. **Test design** (brief A1, a fresh designer, profile STANDARD). The designer leaves no throwaway implementation in this worktree.
3. **Check red** yourself.
4. **Engineer** (brief A2, fresh), only if no package is open. Estimate 80 lines. It runs its tests in the foreground and commits before it ends its turn.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. Red by design, to report apart: W1-50 (26 failed, 17 passed). The two 100 ms latency cases (`test_a_call_waits_under_100_ms_p95_for_the_hook` in W1-05 and `test_decision_p95_is_under_100_ms` in W1-02) are sensitive to machine load: if one fails, re-run its file alone before you treat it as red.
6. Return DONE, or PACKAGES, with the summary, the residuals for `bootstrap.md` and the learning metrics, as your last message.

