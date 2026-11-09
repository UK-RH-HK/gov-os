**sandbox_check:** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-148` failed with `OSError: [Errno 30] Read-only file system`. (b) `git hash-object -w --stdin` worked (`1ae28402a109…`) and `git update-index --refresh` exited 0.
**ps_check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` found nothing (exit 1). No embedder, model or GPU was used.

**task:** W2-148 (DAEO-xafn): the narrow review of DEC-1106 (1) and (3), the one exception round to DEC-1010. Branch `w2/W2-148` at head `1af33c535`, diff `85a5cf655..1af33c535`.

**status:** DONE. READY by the rules: no finding is in scope, ordinary work and fails open or loses work. There are 7 findings (F21–F27). Each becomes a row or rides along with a later change. None needs a round.

**work_completed:**
- Read the ticket from the main checkout, because the worktree's copy has no DEC-1106 note. I also read DEC-1106, F15, JUDGEMENT.md, EMG-common.md, the full code diff, and the current `operator_run.py`: `g8`, `live_changed`, `apply`, `go`, `UndoState.fail`, `undo_live`, `foreign_differences`, `after_checks`, `control_snapshot`, `undo_step`, `recover`, `digest` and `main`.
- Also read `opcommon.py` (`claim_freeze`, `release_freeze`, `holds`, `approved_state`, `notify`, `notice_line`, `clean_env`), the launcher, the wall hook, `brief.md`, the README's hook section and the evidence record's Round 3.
- Ran the tests read-only (below).

**files_changed:** none.

**evidence:**
- Code references are in the check answers below.
- Scratch is the sandbox TMPDIR, not the brief's `/tmp/gov-os-emg-*`. Usage: `t/` 7.8M, 1978 inodes; `home-empty/` 4.0K, 1 inode.
- The empty HOME hides the user site-packages where pytest is installed, so every run set `PYTHONUSERBASE=/home/usain/.local`.

**tests:** all through `heavy_slot.sh`, with `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`, an empty HOME and `PYTHONPATH=<worktree>/src`.
- `test_w2_148_round3.py` with `test_w2_148_restore_freeze.py`: **31 passed**.
- `tests/unit/operator/` with `test_w2_148_apply.py`: **189 passed**.
- The exclusion deselected nothing.
- I did not re-run `gov accept` or the trial (that is the CTO's job, outside the sandbox).

**discoveries:**
- The brief's premise is half right. The journal recovery returns `result: "undone"` but **exit 1** when files are left (`operator_run.py:1592-1593`), and the launcher stops on that code (`operator_launch.py:248-249`).
- Only the owner's undo step returns exit 0 with files left (`:1528`). See F21.

**risks:**
- After my runs, `git status` shows 11 untracked dotfiles in the worktree (`.bashrc`, `.gitconfig`, `.mcp.json`, `.idea`, `.vscode`, and others). The status snapshot at the start of the session showed a clean tree. I wrote none of them myself. They look like the launch sandbox's mask mounts. The CTO should check, outside the sandbox, that they do not exist there before any `add -A`.

**lessons:**
- With an empty scratch HOME, pytest from `~/.local` needs `PYTHONUSERBASE`.

**proposed_decisions:** none. The rows are below.

**unresolved:**
- No acceptance or unit case covers the owner's undo step, or the journal recovery, meeting a foreign change (left plus lock). Only their freeze cases are tested.

**recommended_next_action:**
- Mark W2-148 READY on this narrow review.
- Carry F21 (exit 1 and a distinct result word for the owner's undo when files are left) as a ride-along.
- Make F26 an entry criterion of ACT-OPERATOR-1.
- F22, F23 and F25 become Wave 3 rows.

---

### Answers to checks 1–7

**1. No foreign write at any write-back site: holds, with one bounded gap (F23).**
- The blind restorers `restore_controls` and `restore_tree` are deleted. The only live writers left are:
  - `restore_live_file`, called only for a touched file that `is_after` returns true for (G8 at `:593-596`; the undo's third-bytes branch at `:1369-1382`);
  - the frozen `apply.sh undo`, run only when no touched file is at third bytes (`:1363-1367`);
  - `git add`/`commit`/`reset` limited to the ACT's own repo paths (`:1392-1403`).
- `foreign_differences` only names files; it never writes.
- The `unlisted` path, a red check, a failed commit and an error mid-apply all go through `St.fail` → `undo_live`. G8 does not; it uses `live_changed`.
- On the brief's question about `apply.sh undo`: G8's clone run proves it changes only listed files (`:711-717`). So when every touched file is at its before- or after-copy, it writes only the ACT's own files.
- The proof is by hash in the clone, though. An undo that writes an unlisted path to the same bytes there, such as a folder-level restore, is invisible. Live, it could overwrite a foreign change and go unnamed (F23). That needs an unusual ACT and is F7, which DEC-1106 (4) keeps.
- In the journal recovery, `foreign_differences` compares two snapshots taken at recovery time, so it sees nothing that happened before the recovery (F22). It writes nothing foreign either.

**2. Never success when a foreign change is seen.**
- The run path is correct. G8 always raises Refused. `St.fail` always returns 1, holds the lock when anything is left, and its P1 names each file.
- Journal recovery: result `"undone"`, exit 1, lock held, launcher stops. Not success.
- The owner's undo: result `"undone"`, exit 0, lock held, P1 kind `undo` with the names in its `text`, `left` and `lock: true` in the result.
- This breaks the letter of "never reports success". It does not fail open:
  - `main` (`:1700`) and the launcher (`:235`) refuse at the lock before anything else, so no next ACT runs.
  - The digest shows `"lock": true`, although its `undone` entry carries no names.
- So: in scope, other (F21).

**3. The P1 names every file.**
- The full list is in:
  - the notice's `text` (`pings_log`, and the whole JSON when `push_cmd` is set);
  - the lock file's `why`;
  - the `left` field of `operator.jsonl`.
- The old `names[:5]` truncation is gone from `live_changed`. The `unlisted` reason still cuts at `extra[:5]`, but `foreign_differences` puts every one of those names into `left` anyway.
- The pushed toast/push line is capped at 190 characters (`notice_line`, cut in the middle). The owner's undo puts no names in its short line at all (F24).
- The lock does stop both the next run and the next launch. Only `recover`, run by hand, gets past it, and it never clears the lock.

**4. A concurrent commit stays: holds.**
- The undo is a new commit with `git add -A -- <own paths>`, guarded by a check that the staged list is exactly the reversed touched list (`:1396`).
- Nothing resets HEAD, runs `checkout` or amends. The only reset is `git reset -q -- <own paths>`, which touches the index only.
- Covered by `test_a_concurrent_control_commit_during_the_checks_is_left_and_the_acts_own_file_undone` and acceptance S15.
- Side note (F27, out of scope): that reset's exit code is ignored.

**5. Hook points: as the README says.**
- `in-G8` (`:574`): after the clone is removed, before the after-snapshot. The before-hashes are already taken.
- `in-apply-checks` (`:808`): after the apply, the checks and the run's own commit, before `after_checks`, for every class.
- `Run.hook` blocks on `oc.run` (timeout 600 s), ignores the exit code, runs while no git command is in progress (so no `index.lock`), and passes `os.environ`.
- The walled session cannot reach it:
  - `clean_env` strips `GOV_*` (`opcommon.py:544`);
  - the wall hook allows only the exact 5-token `python3 <install>/operator_run.py run|undo <ACT> <sha>` (`operator_wall_hook.py:93-97`), so an env-prefixed form is refused.

**6. The freeze: correct.**
- Claimed with `O_EXCL` only after G9 passes. If it is taken in the meantime, the run loops back to G9 (`:857-869`).
- Released in `finally`, and only when the file still holds the run's token (`release_freeze`).
- Left out of `approved_state` and `control_snapshot`.
- A stale freeze holds G9, both in the run and in the launcher.
- The owner's undo claims it before writing anything and otherwise refuses with nothing written (`:1499-1502`).
- A run never applies without one.
- A crash in the few seconds between the claim and the journal write leaves a freeze no run removes. After that, nothing runs until the owner deletes it. It is named in the launcher's result and in the log's `G9 held` lines, but it is never pushed and the digest does not show it (F25). That matches the brief's "acceptable, if it is named", with that caveat.
- Recovery claims no freeze of its own. It runs under the dead run's freeze, or with none if that file was removed by hand.

**7. The wider reach: consistent with DEC-1106.**
- An unlisted live write has no after-copy, so it cannot be shown to be the ACT's own. Leaving it with a refusal, the lock and a P1 is the rule as written, and DEC-1106 overrides S15's "undoes the ACT" for such files.
- G8's clone run refuses an apply that writes an unlisted file before the live apply is ever reached.
- What remains (an unreviewed live write stays in the working tree until the owner acts, fenced by the lock) is the trade the owner chose.
- A consequence the engineer flagged: Claude Code's own writes under `.claude/**` will lock the operator (F26).

### Findings

**F21 (S22, F15), scope: in.** With files left, the owner's undo step returns `result: "undone"` and exit 0 (`operator_run.py:1528`). The journal recovery returns 1 in the same case (`:1593`). This breaks the letter of "never reports success".
- Ordinary work: yes, because the owner's undo within 7 days can meet a control file the CTO commits, or one Claude Code writes, during the undo.
- Consequence: other. The lock stops every later run and launch, the P1 names each file, and the result carries `left` and `lock: true`. Only a caller that keys on exit 0 or on the word "undone" misreads it. Ride-along: exit 1 and a distinct result word.

**F22 (S22), scope: in.** `recover` takes `st.controls` and `st.tree_before` at recovery time (`:1562-1563`), so `foreign_differences` cannot see anything that changed between the dead apply and the recovery. The `already` branch skips the check entirely. An unlisted live write by the dead apply is left unnamed, and the result is "undone" with exit 0.
- Ordinary work: no, because it needs a session to die mid-apply after the live apply wrote an unlisted file, which G8's clone run of the same `apply.sh` at the same head already refuses.
- Consequence: fails open. Row: write the undo state into the journal.

**F23 (S15, S22), scope: in.** When no touched file is at third bytes, the live `apply.sh undo` is bounded only by the clone's hash-level dry run. An undo that writes an unlisted path to the same bytes in the clone (a folder restore, `git checkout -- <dir>`, `rm -rf` of a folder) could overwrite a foreign change live. If it puts the file back to its bytes from when the apply started, the change is not named either. There is also a small gap between reading the touched files and running `apply.sh undo` (`:1358` → `:1364`).
- Ordinary work: no, because it needs a reviewed and rehearsed ACT whose undo writes beyond its touched list in a way the clone cannot show, plus a foreign change to that same path within the apply's minutes. It is also F7, kept by DEC-1106 (4).
- Consequence: loses work. Row: in live undos, restore from the frozen `before/` copies, or compare against a snapshot taken just before `apply.sh undo`.

**F24 (S12, S15), scope: in.** The pushed P1 line is capped at 190 characters, cut in the middle (`opcommon.py:381-392`), so names drop once more than one or two files are left. The owner's undo puts no names in its short line at all (`:1526-1527`).
- Ordinary work: yes, because a CTO merge touching several `.claude/**` files during G8 is common.
- Consequence: other. Every name is in the notice's `text`, the lock file and `operator.jsonl`, and the lock holds. Row.

**F25 (S13, S14), scope: in.** A crash between `claim_freeze` (`:867`) and the journal write (`:756`) leaves a freeze no run removes. Every launch then holds at G9 indefinitely. It is named in the launcher's result and the log, but not pushed, and the digest does not list holds.
- Ordinary work: no, because the window is the few seconds of the control snapshot and `git status` between the claim and the journal write.
- Consequence: other (fails closed until the owner removes the file). Row: put the freeze's existence in the digest, or push a P1 on a long hold.

**F26 (S12, S15), scope: in.** Under the rule, Claude Code's own runtime writes under `.claude/**` (`scheduled_tasks.lock`, `settings.local.json`) during G8, or between the apply's start and the after-check, refuse the run and hold the lock. While the CTO's session is active, this may lock the operator after many runs. The engineer flagged it.
- Ordinary work: yes, because those files change during normal Claude Code use in the live tree.
- Consequence: other (fails closed). Entry criterion of ACT-OPERATOR-1: decide whether runtime files leave the control list.

**F27 (S22), scope: out.** The exit code of `git reset -q -- <paths>` in `undo_live` is ignored (`:1403`; this predates round 3). If it fails, the ACT's after-bytes stay staged while the working tree is at the before-bytes, and a later plain `git commit` would commit them.
- Ordinary work: no, because it needs a concurrent git `index.lock` in a window of milliseconds.
- Consequence: fails open. Wave 3 row.

```verdict
{"kpis": [
  {"kpi": "S12", "verdict": "pass", "findings": [
    {"id": "F24", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F26", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "S13", "verdict": "pass", "findings": [
    {"id": "F25", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "S14", "verdict": "pass", "findings": [
    {"id": "F25", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "S15", "verdict": "pass", "findings": [
    {"id": "F23", "scope": "in", "ordinary_work": "no", "consequence": "loses work"},
    {"id": "F24", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F26", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "S22", "verdict": "pass", "findings": [
    {"id": "F21", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F22", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
    {"id": "F23", "scope": "in", "ordinary_work": "no", "consequence": "loses work"},
    {"id": "F27", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]},
  {"kpi": "F15", "verdict": "pass", "findings": [
    {"id": "F21", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```