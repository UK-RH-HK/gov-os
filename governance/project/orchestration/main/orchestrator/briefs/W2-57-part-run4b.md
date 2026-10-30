You are the ticket lead for ticket `DAEO-cy5o` (`W2-57`, "the rulesync probe, the doctor probes, the serial pass and its route to the nightly"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`.

**This is run 4b: the resume of run 4's judgement-only re-probe (DEC-895), not a new round.** `git rev-parse --short=12 HEAD` must show `bd418982e6c0`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:** your run-4 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, in full. It names every step left and the tools you wrote for them (`tools/run4.sh`, `briefs/rev-4.md`, `tools/write_probe4.py`).

## Why you start now

- **Your P-W2-57-R4-FLAG is answered (a):** the orchestrator stopped the close queue on purpose at 14:51 on 2026-10-29, to record the owner's re-plan (DEC-941) before W2-68's close, with the load at 28. The rebuild it was running finished at 14:53. The orchestrator removed `CLOSE-RUNNING` at about 15:44. No queue runs now; the next starts after the re-plan's records and leads are settled, and you will see its flag if it does.
- **`w2/integrate` moved, but not in code:** from `848f5ab366b9` to today's head, `git diff --stat 848f5ab366b9 w2/integrate -- src tests` is empty. The commits are records (DEC-939 to DEC-941, the plan, new tickets, W2-07's and W2-63's closes). **Do not merge again:** your merged head `bd418982e6c0` still holds the code the re-probe judges. Check that diff yourself first; if it is not empty, stop and return PACKAGES naming the files.
- **The owner's re-plan** keeps W2-57's close in block A (DEC-941), after W2-68's and W2-58's.

## The decisions for this run

1. **Your checkpoint's "What a resume must do",** in its order: `bash tools/run4.sh check; parallel; serial; collect` in the background; the tripwire snapshot; fill `@@HEAD@@` (`bd418982e6c0`) and `@@VERIFY@@` in `briefs/rev-4.md`; the reviewer (gov launch, independent-auditor, `--effort max`, read tools only); the tripwire compare; the probe record only if it passes; `trailer_gate.py`.
2. **The gates in one loop** (your own lesson): every suite and the reviewer start only when `CLOSE-RUNNING` and `NIGHTLY-RUNNING` (both under `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/`) are absent and the 1-minute load is under 20, tested together. From about 01:00, start no suite that cannot finish before 02:00.
3. **Every rebuild** (none is planned) runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
4. **Known:** `test_w2_57_designer_read_p95.py` fails under load from other sessions (row W2-L450). If it is red, re-run it alone and report both.
5. **Return** DONE (the new probe passed; ready to merge, then the close queue) or PACKAGES.

**Running beside you:** up to three other leads (W2-71, W2-61, W2-03, W2-05, W2-77, W2-56 in turn). None holds your paths. Touch nothing outside your worktree.

**Estimate:** about 1 to 1.5 hours (verification about 10 minutes, the reviewer 15 to 45 minutes).

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
