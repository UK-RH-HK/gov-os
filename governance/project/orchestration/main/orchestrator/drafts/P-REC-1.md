# P-REC-1 — Keep Policy 1, take the raw orchestration record out of the checked-out tree (P2; the owner's item 10 of 2026-10-21; gates nothing)

**From:** the W2 orchestrator, 2026-10-21 16:4x BST, on lens H's finding 2 and P-H-5.

## 1. Context
- Policy 1 (DEC-819) commits the orchestrator's and the leads' working memory: `sync_context.py` copies the git-ignored scratch folders into `governance/project/orchestration/`, and the owner's push keeps it.
- DEC-856 already keeps the raw part out of the index: retrieval does not serve it.
- Nothing in `src/gov/` and no test reads the record by path (checked today).

## 2. What happened (measured today, at `w2/integrate`)
- **The tree:** 10,286 tracked files, 67.4 MB.
- **The record:** 8,248 files (80 %), 49.3 MB (73 %):
  - the leads' copies `worktrees/`: 6,002 files, 25.6 MB;
  - `main/orchestrator/log/`: 1,145 files, 15.0 MB;
  - `main/orchestrator/briefs/`: 486 files, 6.0 MB;
  - checkpoints, specimens and drafts: the rest.
  - What agents search is small: `packages/` (15 files), `sessions/`, the README and the `CHECKPOINT.md` copy, about 0.6 MB.
- **What it costs** (lens H):
  - 13 acceptance suites copy the whole working tree, and take 48 % of all test time;
  - today three reds came from the record's contents or paths (W1-27's copied log, W1-08's unplaced files, W1-06 through the registry);
  - two of those refused or nearly refused closes.

## 3. Why it matters
The regression's cost and stability now grow with the orchestrator's working memory, not with the code under test. Under DEC-883's same-code reuse, every record commit is also a reuse hazard (P-H-9).

## 4. Options
- **(a) The raw record on its own branch, with a small searchable part kept in the tree** (recommended).
  - **The branch:** an orphan branch `record/w2`, checked out once as a worktree at `~/gov-os-worktrees/W2-00-record/`. `sync_context.py` writes into it and commits there (`Task: DAEO-sdxk`, `Role: orchestrator`, gitleaks first, as today). The owner's daily backup push (DEC-848) pushes both branches. The branch never merges into `w2/integrate` or `main`.
  - **Kept in the tree, for agents to search:** `governance/project/orchestration/README.md` (it names the branch and how to read it: `git show record/w2:<path>`), `packages/**`, `sessions/**`, the `CHECKPOINT.md` copy and the `PR-*.md` notes, as the governance-memory namespace already lists them, and `sync_context.py`.
  - **Moved out:** `worktrees/**`, `main/orchestrator/{log,briefs,drafts,specimen,pin,tools}/**`, `main/checkpoints/**` and the archive files.
  - **History is not rewritten:** the record's past stays in `w2/integrate`'s history; one commit removes the raw part from the tree after the branch holds it, byte for byte.
  - **Effect:** the tree goes from about 10,300 files and 67 MB to about 2,050 files and 18 MB; the copying suites copy a fifth of today's files.
  - **Changes:** DEC-819's "where" (the record's place), the path map's `orchestration-record` namespace (narrowed to what stays; an owner decision, DEC-861), the sync script, the README, the prompt §15.
  - **Cost:** about 1 to 2 hours of orchestrator work, after the queue, between closes.
  - **Risk:** low. The record branch is outside every gate, as the raw record already is outside the index. A reader who wants a lead's log uses `git show record/w2:…` or the record worktree.
- **(b) Keep the record in the tree; the copying suites leave it out** (part of P-H-5, W2-67).
  - Cost: inside W2-67.
  - The tree stays at 67 MB, and the copy cost falls only in the suites W2-67 touches.
  - Record-made reds through other tests (W1-08's namespaces, any test that walks the tree) stay possible.
- **(c) Sparse checkout of the record:** refused by the close itself. `gov close` counts skip-worktree files as "hidden from git's comparison" (`src/gov/close/repo.py`, `tree_differences`), so every close would refuse.
- **(d) A git submodule:** gitlinks, a second clone in every copy and in CI, more moving parts than (a) for the same result.
- **(e) Stop committing the raw record:** against Policy 1 (the context committed and pushed).

## 5. Recommendation
**(a), with P-H-5 (W2-67) still done for the copies' races and per-test copies.** Confidence: medium-high.
- (a) removes the cause of today's record-made reds from the tree. It keeps Policy 1 whole: the record is committed and pushed, on its own branch.
- Timing: after this queue, before W2-66's test designer starts, so that W2-66's and lens H's resumed trials measure the slim tree.
- Classification: lens H's finding 2 and P-H-5, "Ordinary work: yes; Consequence: other (fails closed; cost)"; no ticket round, an orchestrator change under the owner's decision.

## 6. What it blocks, and what waiting costs
It blocks nothing. Waiting keeps the copy tax on every run (48 % of test time in the copying suites) and the risk of another record-made red refusing a close.
