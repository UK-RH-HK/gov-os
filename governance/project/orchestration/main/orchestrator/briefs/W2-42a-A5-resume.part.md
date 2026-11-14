This is a resume of W2-42a (DAEO-03ub), FULL, class C3: the product's guard reads what a Bash command writes (ACT-GUARD-FIX-3's eight parser lines in `src/gov/guard`). It is on EXAMIN's critical path: W2-27 depends on it, and DEC-1028 puts it before EXAMIN's copy. The owner's emergency stopped it on 2026-11-02, and the lift (DEC-1158) restarts it. There is no lead checkpoint: the state is in the branch and the ticket.

**Where you stand (check each before acting):**
- `w2/W2-42a` at 4caf8475f. The CTO merged `w2/integrate` into it cleanly (2,506 commits; `decide.py` and `reads.py` auto-merged).
- Its last work commit is ce03bb8b3, "evidence round 2 (acceptance 452 passed, rows 80-84, scoped set reds); stopped by the owner's order".
- The acceptance tests (452 cases) are merged from `w2/W2-42a-tests` (6f4a6f3c9, 5cca6398e). The tests worktree `~/gov-os-worktrees/W2-42a-tests` is stale: remove it with `git worktree remove` once you are sure nothing in it is unmerged.
- The ticket gained its probe folder (de09ee318): merge `w2/integrate` once more, first (one command, `--no-ff`, `Task: DAEO-03ub`, `Role: orchestrator`).

**The order:**
1. Re-run the acceptance suite on the merged head. Then run the scoped set and name each red: this ticket's, another ticket's (with file:line, for the CTO under DEC-1156 (7)), or the environment's.
2. A fresh engineer fixes what is this ticket's (C3: Opus, high), with the failing output and nothing else. At most one fix round before the review.
3. The scoped run once (DEC-968).
4. The FULL review: a fresh independent auditor, Opus, high, read-only, carrying JUDGEMENT.md word for word, with the verdict block per KPI line.
5. The probe record under `docs/probes/DAEO-03ub/`, with the schema's `implementer_session` field, validated against probe.schema.json before you commit it.
6. Return DONE with the head to land, or PACKAGES.

The guard's own refusals stay as they are while you work: a session refused twice for the same action stops and says so. It never works around a refusal, not by another tool or form (DEC-1142 (9)). A finding that would make the guard fail open is a blocker, and goes to the CTO at once.

Workers launched by `gov launch` write only their sandbox's own `$TMPDIR`. Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs (a launched worker: its sandbox's `$TMPDIR`), PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. A path case of the form "the branch changes only the ticket's allowed_paths" judges only this ticket's branch. A hygiene check compares paths with Path.is_relative_to (DEC-1155). The base-red rule holds. A resource gate's refusal is a wait (DEC-1146). Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket: a gap comes back as a package. If an API error ends a worker, relaunch it once; if it ends again, return PACKAGES naming it. Use `gov retrieve` for what you need to know; code questions use the code graph's own traversal with small answers. There is no token cap.
