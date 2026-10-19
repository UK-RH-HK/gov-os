You are the ticket lead for ticket `DAEO-t6hf` (`W1-19`, "Semantic retrieval, RRF and rerank"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-19` on branch `w1/W1-19`. Its implementer is an engineer (brief A2). STANDARD has no reviewer step. This ticket is on the critical path. **This round builds the model-free part**; the installs the model-dependent cases need are with the owner.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written your return, write nothing more, even if a notification about an earlier wait arrives.

**An engineer starts only on decided ground.** If the test designer returns a new package the model-free build depends on, you return PACKAGES and no engineer runs.

## State of this ticket

- Branch head `6bfd89fe`: 33 acceptance cases (19 errors for the missing module, 13 skipped because `sqlite_vec` does not import in `/usr/bin/python3`, 1 passed); nothing implemented. The earlier lead returned DP-1 to DP-7 and four install packages.
- **All seven packages are decided.** Read them in `docs/DECISION_REGISTER.md` after step 1:
  - **DEC-379** (owner, DP-1 option (a)): the interface as proposed, name by name.
  - **DEC-380** (owner, DP-2): a test designer reads `~/gov-os-workbench/s0b2/out/RESULTS.md` by exact path (and `~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md` if needed), and mean hit@5 follows S0b2's own method where it is stated there. If it is not stated: a hit when one `must_cite` path is in the first five; queries without a gold path left out; a percentage per tier; the mean of the two tiers. The README says which of the two it is and quotes where S0b2 states it.
  - **DEC-373** (delegated, DP-3): warm p95 and peak RAM, option (a) for both.
  - **DEC-374** (delegated, DP-4 and DP-5): an absent reranker keeps the fused order, reports that nothing was reranked and does not raise; the manifest is held in the shared store and read through the semantic module, the embedder's revision being the one observed, not a constant.
  - **DEC-381** (owner, DP-6 option (a)): a namespace whose `embedding_policy` is `not embedded` never reaches the vectors. This needs a case, and a closed reading of the field's values (what the path map's schema of W1-08 allows; anything else fails closed: not embedded).
  - **DEC-382** (owner, DP-7): the G-17 read is accepted; DEC-370 extends to G-17.
  - **DEC-383** (owner): the S0b2 files a worker may read, by exact path only: `~/gov-os-workbench/s0b2/out/RESULTS.md`, `~/gov-os-workbench/s0b2/out/GLUE_REQUIREMENTS.md`, `~/gov-os-workbench/s0b2/out/TOOL_REGISTRY.yaml` and `~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md`. Nobody lists a folder there, and nobody touches `s0b2/probe/`. Put this, word for word, in each worker's brief.
- **Installs (DEC-384): nothing is installed in this round, by anyone.** The main orchestrator has verified the artefacts on disk and brings the complete packages to the owner. Until they are approved, `sqlite_vec` does not import in `/usr/bin/python3`, the reranker's libraries do not import there, and no test or worker starts Ollama, loads a model, or uses the S0b2 virtual environment. The cases that need them skip or stay red; report them apart.
- The engineer builds for the installs as proposed to the owner, without using them: `sqlite_vec` imported from the Python that runs the code (absent today: the semantic facet is then unavailable, never an exception); Ollama found as W1-18's lifecycle module finds it (DEC-260); the default reranker run as a separate pinned process (ADR-0002 §2), which is absent today (DEC-374). How the default reranker process is started (which interpreter, which command) is not decided: the engineer keeps it behind the loader of DEC-379 and the designer returns it as a package with options if a test must fix it.
- A launched worker is sandboxed. If the sandbox stops something a worker needs for this ticket, it does not work around it; you return it.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-t6hf` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES. A containment flag on the merge is a record (DEC-254).
2. **Test design batch 2** (brief A1, one fresh designer, profile STANDARD; before implementation): checks every case against the decisions and revises what an answer makes wrong; settles the hit@5 rule from `RESULTS.md` (DEC-380); adds the DEC-381 case and the DEC-374 cases where none holds them yet. The designer leaves no throwaway implementation in this worktree and copies nothing of the tree anywhere.
3. **Check red** yourself.
4. **Engineer** (brief A2, fresh): the model-free part (RRF, the interfaces, the manifest, the unavailable-facet behaviour, the `embedding_policy` rule). Estimate 280 lines for the whole ticket. It runs its tests in the foreground and commits before it ends its turn.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator. Red by design, to report apart: W1-50, and this ticket's install-dependent cases.
6. Return, as your last message, one of: `PACKAGES` (if any is open), or `DONE` beginning with the sentence "model-free part only: the ticket is not ready to merge until the installs are decided", with the commits, each suite's result, exactly which cases wait for which install, the residuals for `bootstrap.md` and the learning metrics so far (the earlier round: 7 decision packages and 4 install packages).

