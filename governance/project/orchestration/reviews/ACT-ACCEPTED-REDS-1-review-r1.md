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
