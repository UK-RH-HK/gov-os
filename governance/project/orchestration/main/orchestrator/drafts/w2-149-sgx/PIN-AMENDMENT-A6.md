# Proposed text for the CTO to record: SANDBOX-GUARD-EXP-DECLARATION amendment A6, the pin (not recorded by the lead)

Insert under "Amendments", after A5, when the operator has committed ACT-W2-149-INSTALL-1 (§5) and before step 4 (the
extractor). Fill the brackets at recording; nothing else changes.

> - **A6 ([date], the CTO, delegated under DEC-1112 (3)): the pin.**
>   - **§2's pinned commit moves** from `f000adda4` to **`[sha]`**. That is the first `w2/integrate` commit at or after
>     both W2-149's set-up A wiring merge (`7f0e71519`) and the owner's operator's commit of ACT-W2-149-INSTALL-1 (the
>     five briefs, `[sha]`). If W2-141's rebuilt hook (DECIDED-NOT-DONE row 78) is applied first, the pin is after it.
>   - **Why:**
>     1. The launch script reads each brief and template file at `--commit`, and builds each wall's tree from that same
>        commit. At `f000adda4` no brief exists, so every launch is refused with 10 (ACT-W2-149-INSTALL-1, first
>        review F6).
>     2. ACT-SETS-GLOBS-1 (`9cce7430d`) changed the live hook (`97a84e770058` → `74f8dbea4761`) and the path map
>        (`40085090306e` → `44f99ea563cb`). §2 requires the live files to equal the pin's when `prepare_a.sh` copies
>        them.
>     3. The walls' template change (`kinds.yaml` `734b26e261fa`, `tree-exclude.txt` `e8395088167e`) must be at the
>        pin, so that every wall's tree leaves out `governance/project/indep-briefs/**`, and set-up A's trees also leave
>        out the guard's and the launcher's code.
>   - **The guard rules A2 needs stay live at the new pin:** the walls, rule 2c, rule 2d and the call log. Between
>     `f000adda4` and the new pin, the commits that touch `.claude/`, `src/gov/guard/`, the path map or the held-out
>     list are:
>     - ACT-SETS-GLOBS-1 (`9cce7430d`: four more hidden globs; the line rule keys them; it only tightens);
>     - ACT-CLAUDE-COPIES-1 (`eb48fe2fd`: `.claude/templates/`, `.rulesync/` copies; no hook, map or settings change);
>     - W2-150's two refactors (`28c586930`, `ee700af36`: `src/gov/guard/` names moved into `gov.util`/`gov.store` and
>       re-imported). The judge imports `gov` from the pinned python, not from the clone, so they do not change set-up
>       A's decisions until a re-pin of gov;
>     - [W2-141's hook, if applied first].
>
>     Re-run `git log --oneline f000adda4..[pin] -- .claude/ src/gov/guard/ governance/project/path-map.yaml governance/project/held-out.yaml`
>     at recording, and list any commit beyond these.
>   - **The hashes at the new pin**, first 12 of each sha256, checked again at the run (§2):
>     - the hook `pretooluse.py` [`74f8dbea4761` today];
>     - `role_reads.py` [`5407aade9417`];
>     - `bash_writes.py` [`bb246a21735e`];
>     - the path map [`44f99ea563cb`];
>     - the held-out list [`1d724dcb0a8b`];
>     - `.claude/settings.json` [`8f1a3ef183f2`].
>
>     The judge's python stays `pin-bcea09060ebc`, unless a re-pin of gov lands first; then A6 names the new one.
>   - **What follows from it:**
>     - every wall's tree, the briefs' `PIN` and `prepare_a.sh`'s clone are at the new pin;
>     - the launch script's `--commit` for every set-up A launch is the new pin;
>     - `prepare_a.sh check` compares the live files with the new pin's.

Today's values (2026-11-10, `w2/integrate` at `29907d750`), so the CTO can see what is expected to hold at recording:
- the hook `74f8dbea4761`;
- `role_reads.py` `5407aade9417`;
- `bash_writes.py` `bb246a21735e`;
- the map `44f99ea563cb`;
- the held-out list `1d724dcb0a8b`;
- `.claude/settings.json` `8f1a3ef183f2`.
