# Proposed text for the CTO to record: SANDBOX-GUARD-EXP-DECLARATION amendment A6, the pin (not recorded by the lead)

Kept current by the W2-149 lead. Last updated 2026-11-10, after W2-149's F36/F38 merge (`2f98aecbc`).

Insert under "Amendments", after A5, once the owner's operator has committed ACT-W2-149-INSTALL-1 (§5) and before
step 4 (the extractor). Fill the brackets at recording; nothing else changes.

> - **A6 ([date], the CTO, delegated under DEC-1112 (3)): the pin.**
>   - **§2's pinned commit moves** from `f000adda4` to **`[sha]`**.
>     - It is the first `w2/integrate` commit at or after both W2-149's last set-up A wiring merge (`2f98aecbc`: the
>       wiring `7f0e71519`, its review's F18-F23 fixes `90c1fea6c`, F36/F38 closed `2f98aecbc`) and the owner's operator's commit of ACT-W2-149-INSTALL-1
>       (the five briefs, `[sha]`).
>     - If W2-141's rebuilt hook (DECIDED-NOT-DONE row 78) is applied first, the pin is after it.
>   - **Why:**
>     1. The launch script reads each brief and template file at `--commit`, and builds each wall's tree from that
>        same commit. At `f000adda4` no brief exists and the template is the old one. Every launch there is refused:
>        10 today, 11 once the install ACT's list is applied (ACT-W2-149-INSTALL-1 §3, review F33).
>     2. ACT-SETS-GLOBS-1 (`9cce7430d`) changed the live hook (`97a84e770058` → `74f8dbea4761`) and the path map
>        (`40085090306e` → `44f99ea563cb`). §2 requires the live files to equal the pin's when `prepare_a.sh` copies
>        them.
>     3. The walls' template change (`kinds.yaml` `ddd84ae25910`, `tree-exclude.txt` `e8395088167e`) and the launch
>        script set-up A runs under (`90b943aef8be`) must be at the pin. Then every wall's tree leaves out
>        `governance/project/indep-briefs/**`, and set-up A's trees also leave out the guard's and the launcher's code.
>   - **The guard rules A2 needs stay live at the new pin** (the walls, rule 2c, rule 2d, the call log). Between
>     `f000adda4` and the new pin, these commits touch `.claude/`, `src/gov/guard/`, the path map or the held-out list:
>     - ACT-SETS-GLOBS-1 (`9cce7430d`): four more hidden globs, with the line rule keying them. It only tightens;
>     - ACT-CLAUDE-COPIES-1 (`eb48fe2fd`) and ACT-CLAUDE-COPIES-2 (`2059048f2`): `.claude/templates/`, `.claude/agents/`,
>       `.claude/skills/` and `.rulesync/` copies. Neither changes the hook, the map, the held-out list or
>       `.claude/settings.json`;
>     - W2-150's two refactors (`28c586930`, `ee700af36`): `src/gov/guard/` names moved into `gov.util` and `gov.store`
>       and re-imported. The judge imports `gov` from the pinned python, not from the clone, so these change none of
>       set-up A's decisions until a re-pin of gov;
>     - [W2-141's hook, if applied first].
>
>     Re-run `git log --oneline f000adda4..[pin] -- .claude/ src/gov/guard/ governance/project/path-map.yaml governance/project/held-out.yaml`
>     at recording, and list any commit beyond these.
>   - **The hashes at the new pin** (first 12 of each sha256), checked again at the run (§2):
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
>     - every set-up A launch takes the new pin as its `--commit`;
>     - `prepare_a.sh check` compares the live files with the new pin's;
>     - whether `docs/changes/W2-141-hook/` is still in the tree at the new pin is noted (ACT-W2-149-INSTALL-1 §8
>       item 5);
>     - before the overlap auditor's first real run, the CTO dry-builds its wall at the new pin and searches its tree
>       for any text that tells the dispute sides apart (ACT-W2-149-INSTALL-1 §3, F40), and records the result here.

**Today's values** (2026-11-10, `w2/integrate` at `2f98aecbc`), so the CTO can see what is expected to hold at
recording:
- the hook `74f8dbea4761`;
- `role_reads.py` `5407aade9417`;
- `bash_writes.py` `bb246a21735e`;
- the map `44f99ea563cb`;
- the held-out list `1d724dcb0a8b`;
- `.claude/settings.json` `8f1a3ef183f2`;
- the launch script `90b943aef8be`;
- `kinds.yaml` `ddd84ae25910`;
- `tree-exclude.txt` `e8395088167e`.
