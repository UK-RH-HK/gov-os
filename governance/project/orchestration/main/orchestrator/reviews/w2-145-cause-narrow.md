---
type: probe
task: DAEO-2tfd
decisions: [DEC-1167, DEC-1088, DEC-1048, DEC-801, DEC-808, DEC-1010, DEC-953]
reviewer_session: subagent of CTO f3886235
implementer_session: CTO f3886235
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass. No finding blocks. 4 rows, all "other", none fails open or loses work. The planted-break runs (item 3) were not run because the guard refused them twice. The cases' strength is established by reading only.
probed_commit: 61aba98a5
---

# Narrow check: W2-145 (DAEO-2tfd), SANDBOX-1 B2, commit 61aba98a5

Identity: worktree `/home/usain/gov-os-worktrees/W2-145-cause` HEAD = `61aba98a5af7ee12a42b2e2155928f6012fa1faa`, parent `95a55bfca` (w2/integrate). Status was clean at the start and at the end.

Classification: 0 blocking. 4 rows (F1 to F4), each "other", none in scope with ordinary work yes and fails open or loses work.

## 1. It does what it says (sound)

- **An existing folder at 0700:** it is not made again, because the existence check is true, and its mode is not set again, because it is already 0700. So inside a sandbox that binds the existing folder read-only, the first call that can fail is the socket's creation. That call raises the sandbox's EPERM. The commit's own reranker log evidence (399 sandboxed FALLBACK lines naming the read-only folder) is the case this addresses.
- **A missing folder:** it is still made, with its parents, then narrowed to 0700 because a fresh folder takes the default mode less the umask.
- **A folder with a wider mode:** it is still narrowed to 0700.
- **The change itself:** four lines in the connection set-up, as the owner decided in DEC-1167 (7) B2. No other behaviour of the connection loop changed.

## 2. Nothing fails open, no work lost (sound)

- **A folder someone else made with a wider mode, owned by the session's user:** its mode is read, found different and narrowed, the same as before. The window between making and narrowing a fresh folder is the same as before the change.
- **The folder is a symlink to a directory:** the existence check, the mode read and the narrowing all follow the link, so the target is narrowed. The old code did the same, since an existing-directory check also follows the link.
- **The folder is a dangling symlink, or a file:** making it fails ("exists"), as before. The search still goes on unranked and named.
- **A race between the existence check and the make:** the make tolerates an existing folder. The mode is then read and narrowed if needed. No new failure.
- **A folder owned by another user, at 0700:** before the change, the narrowing raised (not the owner). Now the socket's connect is refused instead. In both cases the search stays unranked and named. Nothing is reached that was not reachable before.
- **The error a search reports:** the exception from the connection set-up is caught by the scorer's handler, which is unchanged and catches any exception. That handler writes one FALLBACK line with the error's type and text, records `last_outcome()` as by "unavailable" with that reason, and returns no scores. So the order given is kept and no private reranker is started (W2-145 S1, S2, S4). The reason now reads as a PermissionError, EPERM, not the folder's EROFS. W2-145's acceptance S1 already plants the EPERM kind and matches its reason at the search level (`tests/acceptance/W2-145/w2_145_support.py`, kind "socket-refused-eperm").

## 3. The three cases against planted breaks (NOT RUN: refused twice)

- **Baseline:** the three cases pass at 61aba98a5 in a detached throwaway worktree under `/tmp/claude-1000/nc-145/wt` (3 passed, 0.20 s, through heavy_slot.sh, TMPDIR `/tmp/claude-1000/nc-145/tmp`).
- **The refusal:** the next step changed the throwaway copy's `rerank.py` (a planted break, then a restore). The guard refused it twice with the same message, "a reviewer or auditor writes only its own review or audit record ..., its own scratch, or /tmp (DEC-953 item 2)". The first try used paths relative to the copy; the second used absolute /tmp paths. Per DEC-1137 I stopped and tried no other form. The guard refused before anything ran, so nothing in the copy was changed. The throwaway worktree was then removed (`git worktree remove`), and the worktree list no longer shows it.
- **By reading only, each case should fail on the break it guards.** The fixture makes the folder's make and mode-change raise EROFS, and an EROFS error is not a PermissionError.
  - The parent's code, or the existence check reverted: case 1 fails (EROFS raised from the make).
  - The mode check reverted (always narrow): case 1 fails (EROFS raised from the narrowing).
  - The make dropped: case 2 fails (reading a missing folder's mode raises FileNotFoundError, not PermissionError).
  - The narrowing dropped: case 3 fails (0755 stays). Case 2 also fails under the usual 022 umask.
  - The narrowing set to another mode: cases 2 and 3 fail.
- **What would confirm or reverse this:** the five planted runs above, made by a session the guard lets write a throwaway copy (the CTO or a lead).

## 4. Files and trailers (sound)

- The commit changes only `src/gov/retrieval/rerank.py` (+4 -2) and adds `tests/unit/retrieval/test_w2_145_cause_named.py` (60 lines). Both are within the ticket's `allowed_paths`.
- Trailers: `Task: DAEO-2tfd`, `Role: orchestrator`, `Implements: DEC-1167, DEC-1088`. No `Role: owner`, no `Decided-by:`.

## Findings (rows, none blocks)

**F1: special mode bits on an existing folder are no longer cleared.** The mode is compared on its permission bits only. A folder at 0700 that also carries the setgid or sticky bit is now left as it is, where the old unconditional narrowing cleared those bits. Its permission bits stay 0700, so its privacy holds.
- Ordinary work: no, because the folder is made only by this code, at 0700, and nothing in ordinary work sets special bits on it.
- Consequence: other
- Would reverse: a path in ordinary work that sets a special bit on `~/.cache/gov-os`, or a rule that the folder's whole mode must be exactly 0700.

**F2: a sandboxed search with no cache folder yet still names the folder.** On a HOME where the cache folder does not yet exist, a sandboxed search still fails at making the folder, so its reason names that failure, not the socket's EPERM. The search is still unranked and named.
- Ordinary work: yes, because a fresh HOME whose first search runs sandboxed can reach it, although on this machine the folder exists and the sandbox binds it.
- Consequence: other (no fail open: unranked and named, with a less precise reason)
- Would reverse: evidence that the sandbox profile makes or binds the folder even when it is absent, so the make is never reached in a sandbox.

**F3: the new unit case checks only the connection set-up's exception.** Case 1 does not follow the error through to the search's named outcome (the FALLBACK line and `last_outcome()`). That part of the path is unchanged and is covered by W2-145's acceptance S1 EPERM kind.
- Ordinary work: no, because this is test depth, not a behaviour an agent hits.
- Consequence: other
- Would reverse: the acceptance S1 EPERM kind not reaching the scorer's handler (for example, if it planted the refusal after the connection set-up).

**F4: an orchestrator commit on an engineer-role ticket.** The ticket's `role` is engineer, and this code commit carries `Role: orchestrator`. The owner decided the fix itself in DEC-1167 (7) B2 ("the one-line fix so the reranker's log names the true cause"). DECIDED-NOT-DONE row 186 leaves "the log fix's route" open, and this commit is that route. Both files are within the ticket's `allowed_paths`.
- Ordinary work: no, because the commit is a deliberate CTO step under a named owner decision, not drift.
- Consequence: other
- Would reverse: a reading of DEC-1167 (7), or of the route recorded in row 186, that routes the fix through W2-145's engineer rather than the CTO.

## Probed and found sound

The diff, the three cases, `_connect`'s callers (`_ask`, the scorer in `default_reranker`, `rerank`), the reason format in the FALLBACK line, the symlink, race, wider-mode, foreign-owner and missing-folder paths, the acceptance S1 EPERM kind's presence, the file list and the trailers, and DEC-1167 (7)'s text.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S4", "verdict": "pass", "findings": []}]}
```
