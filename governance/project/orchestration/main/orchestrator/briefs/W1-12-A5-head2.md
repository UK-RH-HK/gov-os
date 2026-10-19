You are the ticket lead for ticket `DAEO-lc4q` (`W1-12`, "Readiness schema and proposal templates"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-12` on branch `w1/W1-12`. You run one short round of the ticket loop. Its implementer is a product-spec worker (brief A4, ticket mode).

**Read this first.** A headless lead's turn ends its background work. After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- An earlier lead brought the branch to head `257611cf`: 19 tests green, the forked schema `feature-readiness` with its templates, every other suite green. Its checkpoint, if any, is in `.gov-runtime/scratch/lead/`.
- Four of its five packages are decided as recommended (DEC-302 to DEC-305 on `w1/integrate`): DP-1 the schema carries the readiness YAML's own keys; DP-3 the kernel `templates/openspec/` folder stays unused for now; DP-4 the readiness record is `readiness.yaml`, fresh rows `MISSING`. **DP-2 needs work: DEC-303 says W1-12 delivers `template/openspec/config.yaml` with `schema: feature-readiness`**, and that file is now in the ticket's `allowed_paths` on `w1/integrate`. DP-5 is with the owner; change nothing for it.

## What you do, in order

1. **Take `w1/integrate` into this branch**: `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-lc4q` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES saying so. The containment flag on the merge is a record (DEC-254). Confirm `.tickets/DAEO-lc4q.md` lists `template/openspec/config.yaml`.
2. **A short test design round** (brief A1, a fresh designer, profile STANDARD) for DEC-303 only: the committed config names the schema; a change created in a temporary project from the template, without `--schema`, gets the readiness record (`local_only`, with the Node 22 PATH prefix, DEC-202). Tests added after implementation, reason "delegated decision".
3. **Check red** yourself.
4. **Product-spec worker** (brief A4, ticket mode, fresh): the one file.
5. **Verify** every suite and the validator; W1-46 and W1-50 are red on this branch from their own tickets (W1-50 by design); report them apart.
6. Return DONE with the whole ticket's summary: all commits; the earlier lead's residuals that still stand; learning metrics for the whole ticket (so far: 5 ambiguity packages; rewrites after implementation 0; 427 lines added against 110, about 110 authored; converged).

