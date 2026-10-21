You are the ticket lead for ticket `DAEO-w9l3` (`W1-14`, "Proposal-to-ticket bridge"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-14` on branch `w1/W1-14`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). STANDARD has no reviewer step.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `src/gov/tasks/bridge*`, `tests/unit/bridge/**`.
- Its dependencies are closed: W1-09 (the ticket wrapper `gov.tasks`: `create`, the ticket schema, the READY rule) and W1-12 (the forked OpenSpec schema `template/openspec/schemas/feature-readiness/`, whose `tasks.md` template this bridge reads). W1-13 (`gov readiness`) is merged too. Read "W1-09 residuals", "W1-12 residuals" and "W1-13 residuals" in `governance/project/bootstrap.md`.
- Read the Contract's CAP-31 with its covers item CAP-31.a, MR-2 and MR-3, and in `docs/DECISION_REGISTER.md`:
  - DEC-302 to DEC-305 (the forked schema and its artefacts);
  - DEC-307: a ticket names its specification in the key `specification`; W1-12 to W1-14 write it. **This bridge writes that key**: it is the back-reference;
  - **DEC-350**: the specification record is the frontmatter of the change's `openspec/changes/<change>/proposal.md` (`id`, `type: specification`, `status`, `profile`, `spine`, `capability_types`), with `readiness.yaml` beside it. Nothing writes that frontmatter yet, so tests write it in their fixtures;
  - DEC-348 and DEC-349 (what `gov readiness` and `gov.readiness.close` do; MR-2: tickets come after the specification is closed);
  - DEC-322: tests build their own repositories and ticket folders in temporary directories; the bridge is never run against this repository's `.tickets/`.
- The source G-05 is in the S0b2 output, which you and your workers do not read. If a KPI cannot be tested without it, that is a package.
- Things the test designer settles from the sources, or returns as packages, never as guesses:
  - the public interface (a Python function in `gov.tasks`, in a module named `bridge*`; no KPI names a `gov` command and `src/gov/cli/**` is outside this ticket's paths);
  - how a task in `tasks.md` carries its `kpis`, `role`, `allowed_paths` and `profile` (what W1-12's `tasks.md` template already gives, and what the bridge does with a task that lacks one: refuse the whole derivation, or that task);
  - whether the bridge refuses a change whose specification is not closed (MR-2), and by which check (`gov.readiness`, or the record's status);
  - how dependencies between tasks are written and how "the DAG is acyclic" is shown, cycles through already existing tickets included;
  - what a second run on the same change does (no duplicate tickets);
  - that an implementer ticket whose `allowed_paths` would cover `tests/acceptance/**` is refused, in every spelling a glob allows (`tests/**`, `**`, a parent directory).
- W1-11 (the decision checker) and W1-33 (role definitions) are idle in other worktrees; their paths are not yours.

## What you do, in order

1. `git merge w1/integrate` if it is not already up to date.
2. **Test design** (brief A1, a fresh designer, profile STANDARD). The designer leaves no throwaway implementation in this worktree: a reference it needs lives in its session scratchpad.
3. **Check red** yourself.
4. **Engineer** (brief A2, fresh). Estimate 120 lines. Proportion rule DEC-135. It runs its tests in the foreground and commits before it ends its turn.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH` (the W1-12 suite runs `openspec`). Red by design, to report apart: W1-50 (26 failed, 17 passed). The two 100 ms latency cases (`test_a_call_waits_under_100_ms_p95_for_the_hook` in W1-05 and `test_decision_p95_is_under_100_ms` in W1-02) are sensitive to machine load: if one fails, re-run its file alone before you treat it as red.
6. Return DONE, or PACKAGES, with the summary, the residuals for `bootstrap.md` and the learning metrics, as your last message.

