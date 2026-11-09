**Verdict: READY. No blocking finding. S22 and F15 both pass on DEC-1107's point.** On both paths and every branch into them, if anything is left the result is `refused` with exit 1, the lock is held, and the P1 names each file left. The ACT's own files are still undone. With nothing left, behaviour is unchanged. One minor row (F28): the recovery's reason text contains the word "undone". It does not block.

**task:** W2-148 (DAEO-xafn): the narrow review of DEC-1107 (F21) on `w2/W2-148-f21`, `b134a760b..0fe71aa8b`.

**status:** DONE.

**work_completed:**
- Step 0 sandbox check passed:
  - (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-148` failed with `OSError: [Errno 30] Read-only file system`.
  - (b) `git hash-object -w --stdin` returned `1ae28402a109…` and `git update-index --refresh` exited 0.
- `ps` check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing (exit 1).
- Read DEC-1107, F21, JUDGEMENT.md, EMG-common and EMG-d4b, and the full diff.
- Read these code paths in full: `undo_step`, `recover`, `undo_live`, `foreign_differences`, `restore_live_file`, `stageable`, `is_after`/`is_before`, `UndoState.fail`, `main`, the launcher's recovery hand-off (`operator_launch.py:245-254`) and `g7`.
- Ran the tests read-only (see tests).

**files_changed:** none. The worktree has no changes of mine. `git status` lists untracked `.bashrc`, `.mcp.json`, `.idea` and similar, but these are the sandbox's empty `/dev/null` placeholders (character device 1,3, dated Nov 3), not files.

**evidence:**
- Code lines: `operator_run.py:1461-1464`, `:1494-1501`, `:1520-1544`, `:1347-1406`, `:1580-1613`, `:547-552`.
- `operator_launch.py:247-249`: the launcher passes a non-zero recovery result through as its own.
- Scratch TMPDIR: `du -sh` 8.3M, `du -s --inodes` 2096.

**tests:** all run through `heavy_slot.sh` with an empty scratch HOME, `PYTHONPATH=<tree>/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`. The filter deselected nothing.
- `test_w2_148_f21.py` plus `test_w2_148_undo_refused.py`: 12 passed.
- `tests/unit/operator` plus `test_w2_148_notices_undo.py` plus `test_w2_148_restore_freeze.py`: 205 passed.
- My first try used `--basetemp`, which the gate refused (DEC-898). I re-ran without it.

**discoveries:** answers to checks 1–5 are below.

**risks:** F28 only, which is not a blocker.

**lessons:** none.

**proposed_decisions:** none.

**unresolved:** none.

**recommended_next_action:** the CTO merges `w2/W2-148-f21` and ACT-OPERATOR-1 goes ahead. F28 becomes a Wave 3 row, or is left as is.

## Checks 1–5

**1. Never `undone` or exit 0 when anything is left.** Holds on both paths and every branch into them.
- **Owner's undo** (`:1520-1544`):
  - `not ok` gives `refused`/`failed`, exit 1.
  - `st.left` not empty gives `refused`, `undo:"done"`, `lock:true`, exit 1, `hold_lock` and a P1.
  - Only an empty `st.left` reaches `undone`/0. `st.left` is set only by `undo_live`, and on success it holds the third-bytes files plus `foreign_differences`.
- **A touched file at third bytes:** it always lands in `left` (`:1363`), so that case can never reach `undone`.
- **Recovery** (`:1595-1613`): the same three-way split. The "already at before" branch writes nothing and has no third bytes, so `undone` is correct there. The launcher exits with the recovery's code and result (`launch:248-249`), so nothing is wrapped as `recovered`.
- **"Already undone" and every other up-front refusal:** these raise `Refused`, which `main` turns into exit 1 (`:1728-1730`).
- **A second undo after the lock is cleared:** caught as "already undone" (the unit case confirms it).

**2. The owner's undo at third bytes.** The up-front check now refuses ("moved since the apply") only when no file is at third bytes (`:1496-1501`). Otherwise `undo_live` runs. It re-reads the live state itself, so a file that reaches third bytes after the up-front check still takes the safe branch.
- In the third-bytes branch, `apply_sh` is never called (`:1364-1383`). Only own files at their after-copy are written, from the frozen `before/` copy after its sha is checked. `restore_live_file` writes only `mine` paths.
- The commit stages only `mine` repo paths (`:1393-1396`). The staged list must equal the reverse touched list, or the undo fails closed. The unit case confirms the undo commit holds only `OPTIN`.
- **Can this branch write a file that is not the ACT's own?** No.
- One note, not a finding: an own file already back at its before-copy is accepted in the third-bytes case. If it is uncommitted, it goes into the undo commit at its before bytes, which is exactly what the undo commit is meant to hold.

**3. The P1 and the lock.**
- Both left-case texts start "refused:" and carry `left_text`, which names each file.
- `hold_lock` is written. The next run stops at the lock (`main:1720`) and so does the next launch (`launch:235`).
- The launcher's stdout in the left case is a single `result: "refused"`. No object at any nesting carries `result: "undone"`; the acceptance test walks every nested object to check this. The reason text does contain the word "undone": see F28.

**4. Unchanged behaviour.**
- Owner's undo with nothing left: `undone`, exit 0.
- Recovery with nothing left: `undone`, exit 0, so the launcher reports `recovered` with `recovered.result == "undone"`.
- An undo after a later ACT on the same files: still a plain "later ACT" refusal, with no lock.
- The run path's `UndoState.fail` is not in the diff. The old unit and acceptance cases (205) are green.

**5. The "already undone" change** (`:1462-1463`).
- **Can it skip a genuine first undo?** No. The new match needs a line for the same ACT and sha with `undo:"done"` after the last `applied`. The run path can only write that line after an apply, and a re-run of an applied ACT stops at G7 (`:550`: live must be at the before-copy) before the journal or the apply. A recovery line after `applied` comes only from an owner's undo that crashed mid-way, which is a real undo, so counting it is correct.
- **Can it let an undo run twice?** No. The refused-with-left line now blocks a second run after the lock is cleared. A failed undo (`undo:"failed"`) still allows a retry, as before.

## Findings

**F28 (S22), scope: in.** In the left case, the recovery's `reason` reads "refused: a session died mid-apply; the ACT's own touched files undone at the next launch…" (`operator_run.py:1604`). So the raw stdout line still contains the substring "undone", although `result` is `refused` and the exit code is 1. The owner's undo text avoids the word ("undid … only").
- Ordinary work: no, because the interface (README) names the `result` field and the exit code as what callers read. The reason itself begins "refused:", and only a raw text grep, not a JSON reader, would misread it.
- Consequence: other. The lock is held, the P1 names each file, and nothing else is applied, so nothing fails open and no work is lost. It could be changed to "put back" if the text is ever touched again.

```verdict
{"kpis": [{"kpi": "S22", "verdict": "pass", "findings": [{"id": "F28", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F15", "verdict": "pass", "findings": []}]}
```