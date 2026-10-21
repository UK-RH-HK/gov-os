You are the ticket lead for ticket `DAEO-rxln` (`W1-17`, "Lexical index and shared store"), profile STANDARD, on the critical path, working only in the worktree `/home/usain/gov-os-worktrees/W1-17` on branch `w1/W1-17`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). STANDARD has no reviewer step.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `src/gov/retrieval/lexical*`, `src/gov/retrieval/chunking*`, `src/gov/retrieval/store*`, `cli/govbridge/**`, `tests/unit/retrieval/**`, `template/governance/kernel/checks/index-freshness*`.
- Its dependencies are closed: W1-10 (the shared store, `gov.store`, and the record graph) and W1-15 (the secret rules and the pre-index content filter in `src/gov/secrets/`). Read "W1-10 residuals" and "W1-15 residuals" in `governance/project/bootstrap.md`.
- "Carried FTS5 and chunking" is the code under `cli/govbridge/` (carried from the v4 line; `docs/SOURCES.md` lists it). The ticket ports it into `src/gov/retrieval/`.
- Read the Contract's CAP-18, CAP-17, CAP-11, CAP-03, CAP-07 and CAP-38 with their covers items (CAP-18.b, CAP-17.a, CAP-38.b, CAP-03.d, CAP-11.a), and in `docs/DECISION_REGISTER.md`:
  - DEC-091 (parent ids on chunk records);
  - DEC-274 to DEC-278 (the store, what a record is, the load);
  - **DEC-322**: only orchestrator-role sessions write this repository's live `.gov-runtime/store.db`. Every test builds its own store and index in a temporary repository, and the engineer never indexes this worktree into its own `.gov-runtime/`;
  - DEC-285 to DEC-290, DEC-298, DEC-299 (the secret filter: every indexer calls it before it reads a file; it ignores allowlists) and DEC-289;
  - the fresh-agent-reconstruction and secrets-indexing check declarations under `template/governance/kernel/checks/` show the form of a family check declaration.
- Dev tiers: `GOV_DEV_TIERS`, default `~/gov-os-workbench/synthetic`; tests clone a tier into a temporary directory and are marked `local_only`. Never list `~/gov-os-workbench/` itself; read nothing under `~/gov-os-workbench/w1-tests/` or `~/gov-os-workbench/s0b2/`.
- The sources G-17, G-20 and G-21 are in the S0b2 output, which you and your workers do not read. If a KPI cannot be tested without them, that is a package.
- W1-16 (the code-graph wrapper) is in flight in another worktree; its paths (`src/gov/codeintel/**`, `src/gov/secrets/**`, the gitleaks rule files) are not this ticket's. It is changing the `gov-token` secret rule (DEC-325); do not depend on that rule's current over-blocking.
- This ticket counts double for resources (indexing): run one indexing job at a time.

## What you do, in order

1. `git merge w1/integrate` if it is not already up to date.
2. **Test design** (brief A1, a fresh designer, profile STANDARD). Points it settles from the sources, or returns as packages, never as guesses:
   - the public interface (a Python interface in `gov.retrieval`, as `gov.store` and `gov.tasks` are; no KPI names a `gov` command and `src/gov/cli/**` is outside this ticket's paths; W1-20 and W1-27 build on it);
   - what "the path map excludes" means for the corpus (which key of `governance/project/path-map.yaml`), and how "no hand-kept include list" is shown;
   - how "changed blobs re-index before the next retrieval" and "2.8 s scale on a-dev" are tested without a flaky time bound (a generous bound, `local_only`);
   - what "an empty or stale index is reported, never returned as absent" returns to the caller;
   - what the index digest is and what makes two rebuilds equal;
   - what the parent id of a chunk is for a document and for code, without a code parser this ticket does not have.
3. **Check red** yourself.
4. **Engineer** (brief A2, fresh). Estimate 240 lines. Proportion rule DEC-135.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. Red by design, to report apart: W1-50 (26 failed, 17 passed). The W1-05 latency case (`test_a_call_waits_under_100_ms_p95_for_the_hook`) is sensitive to machine load, and other tickets' suites run on this machine at the same time: if it fails, re-run `tests/acceptance/W1-05/test_w1_05_live_hooks.py` alone before you treat it as red.
6. Return DONE with the summary, the residuals for `bootstrap.md` and the learning metrics.

