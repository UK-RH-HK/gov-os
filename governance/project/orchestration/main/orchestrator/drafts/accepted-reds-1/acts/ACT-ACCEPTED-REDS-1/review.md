# ACT-ACCEPTED-REDS-1, review round 1 (manifest 49e1117248e1)

## Round 1

Reviewer: independent-auditor, claude -p session (round 1), started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Brief sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, checked. Manifest sha256 computed: `49e1117248e1cccfd134151a34a18af870b49ea57cb1870863776aed006a4778`.

Reproduced in my own `--no-hardlinks` clone of w2/integrate at 09e856c70992, HOME planted. Live map `fb52ab2dc756`, read only.

- **Reversed order, this ACT first:** check, apply, undo and verify all exit 3. The map is byte for byte unchanged, `git status` is empty and no temp file is left.
- **ACT-EXAMIN-SETS-1 applied first** (its own apply.sh, committed as a stand-in): map `b1ffdb0b7b3e`.
- **This ACT, before the apply:** check prints `state before`; verify exits 3.
- **Apply:** gives the frozen after byte for byte (`72916f1da4ae`), mode 644 kept, only the map changed. A second apply changes nothing. Numstat `9 1`.
- **Manifest checks:** both run as written with `bash -c` and exit 0 with no count, as the manifest says. Check 2 exits 1 on the before map.
- **Pinned reader before the owner's commit:** `0 2`, each refused as "no commit of the history of HEAD adds it".
- **validate_entry** (pin `python -E`, on the clone's diff): PASS for both entries ("pending the owner's commit"). Placeholder scan 0 hits; exit 0.
- **§5 run as written** (only the `cd` pointed at the clone): commit 8d8d00b61328 carries `Task: DAEO-sdxk`, `Implements: DEC-1134, DEC-1125` and `Role: owner`. These are the trailers of the earlier ACT owner commits (58211909f744, 9cce7430d8f6). Its reader line printed `2 0`.
- **The same commit as `Role: operator` with `Act:`:** `0 2`, "added it without Role: owner".
- **Undo from the committed state:** restores the frozen before byte for byte; a second undo says nothing to undo.

Class (O):
- class-rules.yaml row `path-map`, `ratchet: [… accepted_reds …]`, `ratchet_class: O`. The tree copy and the installed copy are identical.
- `act_class.classify` on the bundle gives `O` ("a change to accepted_reds, read only from the owner's commits"), `hits: []`.
- The operator agent cannot apply it. G6 raises `Refused("G6", "class (O) …")` before any apply, and `git_commit` writes only `Role: operator`. Even such a commit is refused by the ratchet, as shown above.

The entries are exactly DEC-1134 (1)'s:
- Both test ids exist as written, unparametrized: W1-19 line 268, W2-13 line 67.
- Decision DEC-1134 is ACCEPTED (owner) and its text names both ids.
- The reason is the DEC-1125 (1) red; fixed_by is W2-155.
- The parsed before and after maps have the same keys, and no key other than `accepted_reds` differs.

apply.sh decides by sha256 alone: before, applied, or other (refused, touching nothing). Links, a tampered frozen copy and a read-only folder all refuse (rehearsal J; I repeated the reversed and changed-map cases). It touches nothing in HOME (only my planted `.gitconfig` is there) and does not call crontab. The operator's `live_path_refs` on apply.sh and both checks returns None.

### F1: a literal live repository path in apply.sh's header comment
- **KPI:** check 1. **Scope:** in.
- **Ordinary work:** yes, because builders copy the rebuild hint from bundle to bundle.
- **Consequence:** other. It is a comment only, and the operator's `live_path_refs` drops `#` lines, so G1 passes and no dry run touches the live tree.
- **Evidence:** apply.sh's header names `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/tools/insert_reds.py`. The brief's check 1 says no absolute live path.
- **Fix:** in the next bundle, name the tool by a relative path (`drafts/accepted-reds-1/tools/insert_reds.py`). This bundle is not edited.

### F2: the §5 commit is not covered for the main tree's freeze gate
- **KPI:** check 3 (the rehearsal's coverage). **Scope:** in.
- **Ordinary work:** yes, because the operator agent's cron can be applying another ACT, with `~/gov-os-operator/install/act-in-progress.txt` present, when the owner's operator runs §5.
- **Consequence:** other (fails closed). In the prepared state, the `reference-transaction` hook runs `freeze_gate.py`. It refuses an update touching the operator's control paths without the operator's `Act:`/`Act-sha:` trailers. The commit is refused and the map stays applied but uncommitted; nothing is counted and nothing is lost.
- **Evidence:** `.git/hooks/reference-transaction` lines 8-11. §6 (1) of the package says the main tree's hooks are not rehearsed.
- **Fix:** add one line to §5: "if `git commit` is refused by the freeze, wait for the operator's run to end and run the commit line again (or `apply.sh undo`)".

### F3: §5's last line hard-codes the pin path
- **KPI:** check 4. **Scope:** in.
- **Ordinary work:** yes, because re-pins happen (DEC-1126).
- **Consequence:** other (fails closed). After a re-pin, `pin-797495bdfc70/bin/python` may be gone. The reader line then fails after the commit is already made, so the expected `2 0` cannot be confirmed.
- **Evidence:** today the first line of `~/.local/bin/gov` is `#!/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python`, so the line is right now.
- **Fix:** use `"$(head -1 ~/.local/bin/gov | cut -c3-)" -I -c '…'`, or tell the owner to check the first line before running it.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "4", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "49e1117248e1cccfd134151a34a18af870b49ea57cb1870863776aed006a4778",
 "class": "O",
 "reviewer": "independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-11T16:29:13+00:00",
 "replay_refused": []}
```

## Round 2

Reviewer: independent-auditor, claude -p session (round 2), started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Brief sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, checked. Manifest sha256 computed: `b8df21d891600ff4701ff264ff94f32257c4c9150ae4eb4a3254af2662248ea7`. Every `files` hash in the manifest matches the bundle.

I reproduced the review in my own `--no-hardlinks` clone of w2/integrate at `08f51ea8c` with HOME planted. The live map `f4029cfb4942` was only read, and it is unchanged at the end.

**(i) The entries are byte-identical to round 1's.**
- The changed lines of `diff before after` in round 2 equal those of `ACT-ACCEPTED-REDS-1.r1/`.
- The added lines equal `tools/entries.yaml`.
- Only the line number moved: 416 in round 1, 418 now; the unified hunk is `@@ -415,7 +415,15 @@`.
- Parsed before and after maps have the same keys, and only `accepted_reds` differs: `[]` becomes 2 entries. `examin` is in `evaluation_sets`.

**(ii) The hash chain is new.**
- The live map and w2/integrate are `f4029cfb4942`. The last commit to the map is `7b5c3cb94fd9`, the owner's ACT-W1-01-EXEMPT-3.
- ACT-EXAMIN-SETS-1 round 2 (manifest `e80202922e72`) goes from `f4029cfb4942` to `0ec1d20da86a`.
- This bundle goes from `0ec1d20da86a` to `5654eca4c139`.
- `list.txt`, the manifest's `touched`, and the hashes of `before/` and `after/` all agree.

**(iii) Round 1's findings are fixed as the package says.**
- Round 1 F1 (a literal live path in apply.sh's comment): apply.sh now names no `/home`, `~` or `$HOME` path; the rebuild hint is repository-relative. The operator's `live_path_refs` returns None for apply.sh and for both checks.
- Round 1 F2 (the freeze gate): §5 now says what to do if the freeze refuses the commit: wait and run the commit line again, or `apply.sh undo`.
- Round 1 F3 (the pin path): §5's reader line now reads the pin from `head -1 ~/.local/bin/gov`.

**(iv) apply.sh decides by sha256 alone and refuses on the old map.**
- The state is before, applied or other, decided only by the file's sha256. A link is refused.
- On the live map `f4029cfb` (this ACT first): check, apply, undo and verify each exit 3. The map is unchanged, `git status` is empty and no `act-tmp` file is left.
- The round 1 bundle refuses on both `f4029cfb` and `0ec1d20d`, with exit 3.

**Rehearsal steps in my clone, in order:**
1. EXAMIN round 2 applied by its own apply.sh, then committed as a stand-in.
2. This ACT's check said `state before (sha256 0ec1d20da86a)`. Verify exited 3. Undo said "nothing to undo".
3. Apply produced the frozen after copy byte for byte. Mode 644 was kept, only the map changed, and no stray file was left.
4. A second apply changed nothing. Verify exited 0. Numstat was `9 1`.
5. Both manifest checks, run as written with `bash -c`, exited 0 with no count. Check 2 exits 1 on the before map.
6. EXAMIN's undo with this ACT on top refused (exit 3).
7. This ACT's undo restored the frozen before byte for byte, and `git status` was empty.
8. Nothing changed in HOME, and crontab is not called. The rehearsal log is this chain's run (124 checks) and ends `failures: 0`.

**Asked checks (1) to (5):**
1. **The class is (O).**
   - In class-rules.yaml, row `path-map` has `ratchet: [acceptance_exemptions, accepted_reds, load_sensitive, accepted_history]` and `ratchet_class: O`. The tree copy is identical to `~/gov-os-operator/install/class-rules.yaml`.
   - `act_class.py` on the bundle gives `{"class": "O", "row": "path-map", "why": "a change to accepted_reds, read only from the owner's commits"}` with `hits: []`.
   - The operator agent cannot apply it. G6 raises `Refused("G6", "class (O) …")` before any apply, and `git_commit` writes only `Role: operator`, `Act:`, `Act-sha:`, `Class:` and `Review:`.
   - Even such a commit counts for nothing. My `Role: operator` control commit gave `0 2`: "commit … added it without Role: owner in its final trailer block".
2. **The entries are exactly DEC-1134 (1)'s.**
   - Both test ids exist as written: `test_w1_19_real_models.py:268` and `test_w2_13_latency.py:67`.
   - DEC-1134 is ACCEPTED (owner) and names both ids. The decision is DEC-1134, the reason is DEC-1125 (1)'s red, and `fixed_by` is W2-155.
   - Nothing else in the map changes.
3. **apply.sh is sha256-only, and the reversed order touches nothing.** See (iv) above.
4. **§5 run as written** (only the `cd` line pointed at the clone; HOME planted, with links to the real `~/.local/bin` and `~/.local/share`):
   - It exited 0. The steps printed: the manifest sha `b8df21d8…`; check `state before (sha256 0ec1d20da86a)`; apply `state applied (sha256 5654eca4c139)`; verify silent; pathmap `0`; numstat `9 1`.
   - It made commit `156ccc0a` (clone only) with `Task: DAEO-sdxk`, `Implements: DEC-1134, DEC-1125` and `Role: owner`. These are the trailers of the owner's earlier ACT commits (`7b5c3cb94fd9`, `58211909f744`).
   - The reader line ran the pin's interpreter (`pin-797495bdfc70/bin/python`, the first line of `~/.local/bin/gov`) and printed `2 0`. The pin's `ratchet.py` is byte-identical to `src/gov/close/ratchet.py`.
   - `apply_accepted_reds` with both tests red: ok, each reported `failed`. With one passing: finding `ACCEPTED_RED_PASSES`.
5. **validate_entry: PASS.** I ran the pin's python with `-E` on `.gov-runtime/scratch/orchestrator/tools/validate_entry.py`, on the clone's diff and on `accepted-reds.r2.diff`; the two diffs have identical changed lines. Both entries gave PASS ("pending the owner's commit"), the placeholder scan had 0 hits, and it exited 0.

Not rehearsed, as §6 of the package says: the main tree's hooks on the by-hand commit. If the freeze refuses the commit, it fails closed, and §5 covers that case.

### F1: the package's §2 item 4 cites rehearsal step H7 for the `Role: operator` refusal; the log has it at H8
- **KPI:** check 3 (the package's pointer into the rehearsal). **Scope:** out (package prose, not the bundle).
- **Ordinary work:** yes, because a reader following the pointer opens H7 ("another red is still refused") and has to look for the step.
- **Consequence:** other. It is a citation only. The refusal is in the log at H8, and I reproduced it.
- **Evidence:** in `rehearsal.log` (69e57ee8b53e), H7 is "another red is still refused" and H8 is "both refused: added without Role: owner". §6's table correctly puts it under H.
- **Fix:** in the next package, cite H8. This bundle is not edited.

### F2: the main tree's hooks are not rehearsed on the by-hand commit (carried from round 1 F2, now covered in §5)
- **KPI:** check 3 (coverage). **Scope:** in.
- **Ordinary work:** yes, because the operator agent may be applying another ACT, with the freeze in place, when the owner's operator runs §5.
- **Consequence:** other (fails closed). The commit is refused, and the map stays applied but uncommitted. The ratchet counts nothing until a `Role: owner` commit exists, so nothing fails open and no work is lost.
- **Evidence:** §6 (1) of the package. §5's freeze line: "If `git commit` is refused by the freeze …, wait for its run to end and run the commit line again (or `bash $G/apply.sh undo`)". The same form of commit passed at `7b5c3cb94fd9`.
- **Fix:** none needed for this bundle. Recorded as a row.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "4", "verdict": "pass", "findings": []},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "b8df21d891600ff4701ff264ff94f32257c4c9150ae4eb4a3254af2662248ea7",
 "class": "O",
 "reviewer": "independent-auditor, claude -p session (round 2) started by the CTO (launch_worker.sh, DAEO-r30l); not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-11T19:40:26+00:00",
 "replay_refused": []}
```
