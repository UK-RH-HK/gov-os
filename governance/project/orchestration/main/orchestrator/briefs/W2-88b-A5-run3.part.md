This is W2-88b (DAEO-aks1), run 3: the smoke run. Your earlier run was stopped by the CTO on the owner's scope change. DEC-1176 is now recorded (e3c94cd77), and the ticket is re-scoped. Read the ticket in full: its new KPI lines S1 to S5 and F1 to F3, the Verify clauses, the lines "Removed by DEC-1176 (2)", and the non-goals. Read DEC-1176 in docs/DECISION_REGISTER.md. Your earlier scratch work stands where it fits, including the GitHub clones if they are still under `~/gov-os-runs/W2-88b/`.

**The purpose, in the owner's words:** "its only purpose is to test whether gov adopt works on repositories different from ours, small and large, and where it fails. No measuring and no validation."

**The order:**
1. **A research worker** runs `gov adopt` on copies of grafana (large) and redis (smaller) under `~/gov-os-runs/W2-88b/`.
   - It takes them through the stages MA, A0 to A6, A8 and A9, with A9 run without `--questions`.
   - The work is the assessment, the index, the embeddings and the stores.
   - Indexing and embeddings take a heavy slot; a resource gate's refusal is a wait, never a failure.
2. **A5 on each copy (DEC-1176 (3) (a)):**
   - When a copy reaches A5, launch a fresh independent auditor on it (Opus, high, read-only, a session that ran no stage).
   - It judges that copy's path map only, never memory, and commits its verdict there with `Role: independent-auditor` alone.
   - The gate needs that trailer (`src/gov/adopt/stages.py:432-461`).
3. **The record:** `experiments/W2-88/smoke-run.md`.
   - For each repository and each stage, it says whether the stage completed, or where and how it failed: the command, exit code, refusal code, error and time.
   - A failure is a finding to record and return. It never stops the other repository and is never fixed here.
   - No questions, no measure, no validation of quality.
   - `~/workspace`, the workbench and the owner's repositories are neither cloned, read nor written.
4. **A narrow independent check** that the record holds every stage's outcome for both repositories and claims no measure:
   - a fresh independent auditor, Opus, high, read-only, carrying JUDGEMENT.md word for word, ending with the verdict block;
   - its record goes under `docs/probes/DAEO-aks1/`, with `implementer_session` and `probed_commit` in full; quote any front-matter value that holds `: `.
5. Return DONE with the head and the list of failures found, or PACKAGES.

Every commit's trailers go in one final paragraph. Never commit a merge with conflict markers (DEC-1175 (4)). Workers use the sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, PYTHONUSERBASE=/home/usain/.local. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. Never open the evaluation sets' root, the workbench, EXAMIN's real repository, or any hidden or memory-verdict folder. No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
