This is W2-116 (DAEO-f58b) pass 2b, FULL: S2, then the build. Your pass 2 returned PACKAGES (P-W2-116-S2-INTERFACE). The CTO decided all three questions under DEC-1157 (12), committed as 8801ffd17 on w2/integrate:
- **Q1 (a):** your interface, written into the ticket's notes ("S2's interface (pass 2b)").
- **Q2 (b), not (a):** the ticket is widened by `governance/project/rebuild.yaml`. Your engineer adds this repository's `integration_refresh` line with the code that reads it, so no reader meets the key before its code exists.
- **Q3 (a):** the ticket is widened by `src/gov/retrieval/retrieve.py` for R2-F3, plus `tests/unit/status/test_w2_116*` and `tests/unit/retrieval/test_w2_116*`.

Read your lead checkpoint `.gov-runtime/scratch/lead/CHECKPOINT.md` first, then the package `.gov-runtime/scratch/lead/PACKAGE-W2-116-S2-INTERFACE.md` and the ticket.

**The order:**
1. Merge `w2/integrate` into `w2/W2-116`: one command, `--no-ff`, with `Task: DAEO-f58b` and `Role: orchestrator`. Delete pass 1's leftover `w2/W2-116-tests` branch and folder only if they hold nothing unmerged (check with `git branch --no-merged`); otherwise name them in your return.
2. **An independent test designer** (a fresh tests worktree) writes S2's acceptance cases under `tests/acceptance/W2-116/` from the KPI line and the stated interface:
   - a planted config's two times are read;
   - a refresh runs after a newer verdict file, when `latest` passes without one, and at `second`; otherwise it says `not_due`;
   - `gov status`'s `integration_store` part has head, age and a named stale reason;
   - a missing or invalid time refuses `REBUILD_CONFIG_INVALID` naming the key;
   - R2-F3: a continuation token from the other half is refused.
   The clock is planted with `GOV_NOW`. Check red for the stated reasons.
3. **An engineer** builds S2 and R2-F3 inside the paths, and adds `rebuild.yaml`'s `integration_refresh` line with this repository's values, as the ticket states.
4. `gov accept W2-116` on the final head; the scoped run once (DEC-968).
5. **A narrow independent check** (a fresh independent auditor, Opus, high, read-only, carrying JUDGEMENT.md word for word): only pass 2b's change, against S2's line, the stated interface and R2-F3, ending with the verdict block. Commit its record under `docs/probes/DAEO-f58b/`, with `implementer_session`.
6. Return DONE with the head to land and the record, or PACKAGES.

Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. A path case of the form "the branch changes only the ticket's allowed_paths" judges only this ticket's branch. If another ticket's case turns red on this branch, name it with file:line; the CTO fixes it under DEC-1156 (7). The three `test_cto_safety_nets.py` live-inbox cases and `test_w2_23_space.py:94` are known reds: name them, never fix them here. A resource gate's refusal is a wait (DEC-1146). Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
