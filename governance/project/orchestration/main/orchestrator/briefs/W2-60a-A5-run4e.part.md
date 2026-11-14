This is run 4e of W2-60a (DAEO-cv58), FULL, class C3: the part of your work that every answer to P-5 needs. P-5 (RUBRIC-2's unbuilt lines) is with the owner as P1-W2-60a-P5. Option (B), land the reviewed scope with the rubric in a follow-up, is the CTO's recommendation; (A) is build now with a fresh C3 review. Do not start the RUBRIC-2 build in this run. Read your lead checkpoint first.

**The work (needed under (A) and (B) alike):**
1. b12, a fresh independent test designer (C3), resolves the four acceptance files that still hold conflict markers on 5b7941b66: `tests/acceptance/W2-50/w2_50_support.py`, `W2-58/README.md`, `W2-58/test_w2_58_launched_sessions.py`, `W2-58/w2_58_support.py`. It also plants the templates and the open gate in W2-60a's fixtures.
2. The S12 test and P-3's older fixtures, as the ticket's P-2 and P-3 decided (aa25fea54). A test designer writes them in the tests worktree.
3. The engineer for S12 if it needs code.
4. `gov accept W2-60a` on its pre-RUBRIC-2 lines, and the scoped run once (DEC-968).
5. Return PACKAGES naming the head, with no conflict marker left anywhere (`git grep -n '^<<<<<<<'` empty), each RUBRIC-2 line's state, and the interface you propose for (A) unchanged from run 4d.

The CTO then resumes you on the owner's answer: under (B), a narrow check and DONE; under (A), the interface written into the ticket, b13, the engineer, and the fresh review.

Workers launched by `gov launch` write only their sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs (a launched worker: its sandbox's `$TMPDIR`), PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`). A resource gate's refusal is a wait (DEC-1146). A session refused twice for the same action stops and says so, and never works around a refusal by another tool or form (DEC-1142 (9)). Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket. There is no token cap.
