You are the ticket lead for ticket `DAEO-lc4q` (`W1-12`, "Readiness schema and proposal templates"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-12` on branch `w1/W1-12`. You run the ticket loop for this one ticket. Its implementer is a product-spec worker (brief A4, ticket mode), not an engineer. STANDARD has no reviewer step.

**Read this first.** A headless lead's turn ends its background work. After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `template/openspec/schemas/**` and `template/governance/kernel/templates/openspec/**`. Neither folder exists yet.
- Its dependency is closed: W1-08 (record schemas and templates under `template/governance/kernel/`; the shared definitions file holds every id grammar, DEC-227; see "W1-08 residuals" in `governance/project/bootstrap.md`).
- The source of truth for the rows and states is `docs/contract/readiness-dimensions.yaml` (26 rows, 5 states). Read the Contract's CAP-30 with its covers items CAP-30.a and CAP-30.e, MR-1, and DEC-085, DEC-088, DEC-089 and DEC-105 (CIT-P, CIT-E).
- OpenSpec is a Node 22 tool recorded in `governance/project/tool-registry.yaml`. It is not on the default PATH: every run uses the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH` (DEC-202). Nothing is installed by you or a worker. A test that runs the `openspec` binary is marked `local_only`.
- Things the test designer must look at and not guess; each is a decision package if the sources leave it open:
  - what "the forked OpenSpec schema" is as a file: the format and location OpenSpec expects for a custom schema, as documented for the pinned version, and how a project under `template/` makes OpenSpec use it;
  - "exactly as readiness-dimensions.yaml": the comparison is by row id, row name and state names, taken from the YAML at test time, never from a copy in the test;
  - "proposal templates pass `openspec validate --strict` on first use": which templates (proposal, design, tasks, the readiness record), and what "first use" means (a fresh change created from the template in a temporary project);
  - "the capability-type table for STANDARD rows": where the table is defined (the readiness YAML, the Contract or an archived source; for an archived source return a package, do not read `docs/source/`);
  - "a change to the taxonomy or to readiness-dimensions.yaml is accepted only with a linked CIT-E record": what in this ticket can enforce or show that (a field in the schema, a check declaration), given that `gov readiness` is W1-13 and `gov check` is W1-26.

## What you do, in order

1. **Test design** (brief A1, a fresh designer, profile STANDARD, DEC-221: every KPI line's success and failure plus the key edge cases; every covers id, CAP-30.a and CAP-30.e, gets at least one test).
2. **Check red** yourself.
3. **Product-spec worker** (brief A4, ticket mode, fresh, role `product-spec`). Estimate 110 lines.
4. **Verify** every suite and the validator. Suites of tickets still in flight elsewhere (W1-46, W1-49, W1-50, W1-25, W1-09) may be red or absent on this branch from their own tickets; W1-50 is red by design (26 failed, 17 passed). Confirm that and report them apart. Note that W1-08's suite checks that every tracked path sits in exactly one namespace of `governance/project/path-map.yaml`: a new top-level folder under `template/` is covered by the template namespace, but confirm that suite stays green, and return a package if it does not (the path map is outside this ticket's paths).

