You are the ticket lead for ticket `DAEO-ha8z` (`W2-49`, "Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-49` on branch `w2/W2-49`.

**This is a resume, under DEC-953, DEC-954 and DEC-957: read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, first.** `git rev-parse --short=12 HEAD` must show `b667fdc03ece` (the orchestrator merged `w2/integrate` in: ACT 1's five-rule guard, DEC-953 to DEC-957, W2-90 filed), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Your decided scope is in your older part,** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/W2-49-part-mergeback.md`: read it whole for its texts (behaviours, checks, who runs beside you). This part holds wherever the two differ.

## What is left

- **Start check:** `git merge-base --is-ancestor w2/W2-51 HEAD` must succeed: W2-51's validator (`docs/plan/tools/validate_w2.py`) must be in your tree. W2-51 merged is enough; its close is not needed (DEC-953). If it fails, stop and return PACKAGES.
- **What is left, from the older part (its steps 2, 3, 5, 7 and 8; its step 1's merge is done, but run its two checks):**
  1. tests first by a fresh independent test designer (`--effort high`): KPI line 3 and the failure line against W2-51's validator, DEC-745 item 2's eight source-map rows, DEC-750 item 5's `CAP-45.a.md` and status lines; nothing that fixes DEC-841's nine items either way;
  2. a fresh product-spec worker: the eight `SOURCE_MAP.csv` rows, `CAP-45.a.md` regenerated and every capability record's `status:` ACCEPTED, one CIT-E line each; no Contract text changes;
  3. the verification below, plus W2-51's validator over the merged tree once, quoted;
  4. return PACKAGES with P-A (DEC-841: the CIT-P addendum the owner approves before the nine items move) and P-B (DEC-825 item 3), as the older part's step 8 gives them, and the branch state as DONE would give it.
- **Merge order (the orchestrator's):** W2-51, then W2-49, then W2-52, then W2-16 (stacked on you, DEC-752, DEC-786).

**What no longer applies (DEC-953; `governance/project/orchestration/LIFTED-BY-DEC953.md`), wherever the older part or your checkpoint says otherwise:** the merge step where the orchestrator has done it; the pre-close gate and `gov close` with its probe gate; fresh probes because a merge made a review stale (there is no staleness rule; a review is needed only where none has passed, or for new work); the trailer gate as a refusal (trailers are still written); the ratchet lists; the night window, the 01:00 cut-off, the `NIGHTLY-RUNNING` and `CLOSE-PENDING` holds and the 90-minute rule; the wait-based park. Test designers and engineers run at `--effort high`; only reviewers at `--effort max` (DEC-957). The guard is five rules now (ACT 1): command forms are no longer refused.

**Verify (DEC-953 item 4, the common brief's step):** your own acceptance suite and unit tests, then the selection, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/W2-49 W2-49 DAEO-ha8z`; the full suite only when its scope is `full`, and then once, under `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <command>` (closes take the lock first). Rebuild once first, under `flock /tmp/gov-os-rebuild.lock`, never `--no-embeddings`. A red in your files that fails alone is yours; one that passes alone is a flaky candidate, named. **Known reds you do not own** (named, left): the 235 live-wiring cases ACT 1 turned red, until W2-90 lands (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/W2-90-cases.txt`); W1-42's accepted reds; latency cases under load (W1-02, W1-05), re-run alone; DEC-919's W2-66 case naming a new conftest.

**Installs:** the guard refuses them for you and your workers; raise any as a P1 in your return. **Scratch:** 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-49`; clean as you go, report `du -sh` and `du -s --inodes` in `evidence`, and name anything left for the orchestrator. **Repair:** at most one batch; a second, a fix outside your paths, or a red in another ticket's code: PACKAGES with its cost in lines and hours. **Finish what is listed and nothing new** (DEC-946 item 6).

**Estimate:** about 4 to 5 hours.

**Return:** the twelve fields first, as labelled lines; status DONE (each step's counts, the selection's scope and reasons, the probe record where one is due; ready to merge) or PACKAGES (each in six parts, with your recommendation and confidence, saying what it blocks).


**DEC-968 (owner, 2026-10-31), overriding anything above about a full run:** never run the full suite, whatever your change, core included: the nightly runs it once a day. Your verification is the scoped set `select_tests.py` gives (always `scoped` now; for a core change it names `core_changed` and selects every suite the change can reach), run once before you return, in the close's form. A case that fails there and that your change did not cause (it fails on `w2/integrate` too) is named in your return for the CTO to deal with at once; one your change caused is yours to fix. Exit 2 from the selection (scope `refused`): return PACKAGES with its reasons.
