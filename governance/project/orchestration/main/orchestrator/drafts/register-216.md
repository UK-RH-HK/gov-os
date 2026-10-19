
## 216. Owner answers of 2026-10-15, second set: the hook's foreign commits on `w1/W1-42`, the hooks removed until W1-42 is merged, W1-42's merge with three red cases, the intended exit with named exceptions (register v0.216, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-710 — `w1/W1-42` is restored to its merge `d6d45759`, every file on disk kept
- **Status:** ACCEPTED (owner, 2026-10-15) · **Under:** DEC-706, DEC-709 · **Basis:** W1-42's final pass (lead session `3cb90cc0…`) staged its six report files, rebuilt, and committed; the pre-commit hook refused the commit (`gov ci checks G1 G2`: `CHECK_FAILED: hard-block checks failed: retrieval-regression`, 207 s; staged-secrets 0) and, while it ran, two commits "adopted" were written onto `w1/W1-42`: `4b051fde` (parent `d6d45759`, an ORION tree) and `dc6aa34c` (parent `4b051fde`, an ARGUS tree). The orchestrator verified that only `w1/W1-42`'s reflog holds them (the main tree's HEAD and `w1/integrate` hold none) and that the files on disk are exactly `d6d45759` plus the six report files.
- **Decision:** option (a). The orchestrator runs `git reset --mixed d6d45759` in the W1-42 worktree, keeping every file on disk. It is an unpushed ticket branch, so this does not rewrite shared history.

### DEC-711 — The two foreign commits stay in the local object store, named for the exit auditor
- **Status:** ACCEPTED (owner, 2026-10-15) · **Under:** DEC-604, DEC-673, DEC-710
- **Decision:** option (a). `4b051fde` and `dc6aa34c` are left in this repository's local object store, reachable through the reflog, and named for the exit auditor. They were never pushed. The planted key in `dc6aa34c`'s tree (under `tools/deploy_keys/`, named by its folder only) is a synthetic test secret; it was never on disk in a tree of this repository.

### DEC-712 — The hooks are removed until W1-42 is merged; the hook's git environment is the FIRST item of the Wave 2 list, fixed before any pilot adoption of an owner repository
- **Status:** ACCEPTED (owner, 2026-10-15) · **Under:** DEC-235, DEC-616, DEC-706, DEC-709 · **Basis:** the orchestrator's reading of the code (not run): `src/gov/retrieval/retrieve_check.py` (the G1 retrieval-regression check) clones each dev tier into a temporary folder and runs `git -C <folder> add -A` and `commit -m adopted` there without clearing the `GIT_*` variables git exports to a hook; in a linked worktree they point at the worktree's own index and branch. Three hooked commits in the main tree left its history clean.
- **Decision:** option (a).
  - **The owner's steps, through the operator:** `lefthook uninstall` exit 0; `.git/hooks` now holds only the 14 stock `*.sample` files (`pre-commit` and `pre-push` gone).
  - **Side effect:** `lefthook uninstall` rewrote `.claude/settings.json`. The operator inspected it with the deny and path lines filtered out: lefthook only sorted the hook events and each hook's fields alphabetically; no hook command changed, and the parsed JSON equals HEAD's. The operator restored the committed file with `git restore`; `git status` is clean. `lefthook install` will likely re-sort it the same way, which would turn adapter-portability red, since it compares the file exactly.
  - Every commit still runs `gov rebuild --no-embeddings` after staging (DEC-709).
  - When W1-42 is merged and its worktree removed, the orchestrator tells the owner to reinstall the hooks; the operator restores `.claude/settings.json` straight after.
  - **Classification, the owner's: more than a Wave 2 residual.** Parallel tickets in worktrees are the method (DEC-235), so in any adopted project with hooks installed every worktree commit would get foreign commits onto its branch. **The FIRST item of the Wave 2 list, to be fixed before any pilot adoption of an owner repository:**
    - checks and tests that run git clear the inherited `GIT_*` variables;
    - a sweep: every check, test helper and command that runs git in another folder, and which of them inherit the hook environment;
    - `lefthook install` and `uninstall` re-sorting `.claude/settings.json`, so that installing the hooks never leaves adapter-portability red.

### DEC-713 — W1-42 is merged with its three red cases named in the exit report
- **Status:** ACCEPTED (owner, 2026-10-15) · **Under:** DEC-687, DEC-692 · **Basis:** W1-42's suite on the final pass's files: 21 passed, 3 red. RETR-X-02 needs a named parent expansion and the kept bundle has none (the question asks about an id that exists nowhere); the governance share needs a measured share on each programme and only ORION-im02 has one (4.49 %); the worktree list can only pass after this ticket's worktree is removed, which follows the merge.
- **Decision:** option (a). `w1/W1-42` is merged into `w1/integrate` with its three red cases named in the exit report. After the worktree is removed the orchestrator records the worktree list. RETR-X-02 and the per-programme governance share stay as NOT MET evidence for the owner's exit decision.

### DEC-714 — The intended exit: Wave 1 passes with named, accepted exceptions; an adoption-readiness block opens Wave 2
- **Status:** ACCEPTED (owner, 2026-10-15) · **Under:** DEC-584, DEC-687, DEC-712, DEC-713
- **Decision:** the owner's intended exit is that Wave 1 passes with named, accepted exceptions. Each of these goes into an **adoption-readiness block** that opens Wave 2 and must pass before any pilot adoption:
  - ARGUS's incomplete cycle (b-dev adopted to A2);
  - the three reds left in the a-dev clone: context reproducibility, claims, schema;
  - RETR-X-02 (no parent expansion);
  - the missing ARGUS governance share.
- Each exception is a named line in the exit report, with what would close it. The exit decision itself stays the owner's, after the W1-43 exit audit.

| Version | Date | Change |
|---|---|---|
| 0.216 | 2026-10-15 | Owner: DEC-710 (`w1/W1-42` restored to `d6d45759`), DEC-711 (the two foreign commits left in the local object store, named), DEC-712 (hooks removed until W1-42 is merged; the hook's git environment and the settings re-sort are the FIRST Wave 2 item, before any pilot adoption), DEC-713 (W1-42 merged with three red cases named), DEC-714 (intended exit with named exceptions; the adoption-readiness block opens Wave 2). Next free id: DEC-715. |
