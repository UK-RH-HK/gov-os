This is W2-42a (DAEO-03ub), reopened by the CTO under DEC-1164 (18), FULL ticket, class C2: one defect fix with a narrow check (DEC-1154; no review round, DEC-1010). Read the ticket's last paragraph ("Reopened 2026-11-13"), then DEC-1174 (1) in docs/DECISION_REGISTER.md, then your lead checkpoint if one is left.

**The defect.** `src/gov/guard/decide.py` on w2/integrate (e437c799c) refuses a Bash call whose heredoc body, read by a shell, holds a comment with an apostrophe, with "the command cannot be read". It does so even when the call writes nothing:
- `bash -euo pipefail <<'EOF'` / `# don't overwrite` / `echo hi` / `EOF` is refused.
- `bash <<'EOF'` / `# it's fine` / `ls` / `EOF` is refused.
- The same bodies without the comment are allowed.

The CTO's probe is `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/f3886235-4854-4c91-9cf3-1a1dd009cb50/scratchpad/f1probe/product_probe.py`; it calls `decide()` as an engineer on DAEO-03ub. Read it; it is yours to reuse.

**The order:**
1. Merge `w2/integrate` into `w2/W2-42a`: one command, `--no-ff`, with `Task: DAEO-03ub` and `Role: orchestrator`. The branch is at 5d58123b1 and merged; integrate has moved. **Never commit a merge with conflict markers** (DEC-1173 (1)). If a test file conflicts, take one side exactly and let the test designer commit the rest.
2. **A fresh independent test designer** (`Rewrite-Reason: DEC-1174 (1)`) adds cases under `tests/acceptance/W2-42a/`:
   - (a) The harmless forms above are allowed: each options form of W2-42a's F1 fixture (`-euo pipefail`, `-o pipefail`, `-O extglob`, `--rcfile`, `/dev/stdin`, `cat … | bash -o pipefail`) and plain `bash <<EOF`, each with a body whose comment holds an apostrophe and writes nothing.
   - (b) Still refused: the same forms where the call then writes into `tests/acceptance/X/zz.py` after the heredoc, by `>`, by `cp` and by `python3 -c "open(…,'w')"` (ACT-GUARD-FIX-5 round 2's four reversal calls).
   - (c) Still refused: a body that itself writes there after such a comment.
   - (d) Still refused, as today: a body with a real unclosed quote outside a comment.

   Check that (a) is red for the stated reason before step 3.
3. **An engineer** fixes `src/gov/guard/bash_writes.py`: comment text in a shell body is dropped before the body is tokenised (a `#` that starts a word, outside quotes and not part of `${…}` or `$#`, to the end of its line). Nothing else changes.
4. `gov accept W2-42a` on the final head, then the scoped run once (DEC-968): `tests/unit/guard`, `tests/acceptance/W2-42a`, and the live hook's own suites (`tests/unit/hooks`).
5. **A narrow independent check:** a fresh independent auditor (Opus, high, read-only, carrying JUDGEMENT.md word for word).
   - It reviews only the change since the merge, against this brief's (a) to (d), and ends with the verdict block.
   - Commit its record as `docs/probes/DAEO-03ub/PR-DAEO-03ub-apos.md`, with `implementer_session` and `probed_commit` in full (40 hex digits).
   - Every commit's trailers go in one final paragraph.
6. Return DONE with the head to land, or PACKAGES.

Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. If another ticket's case turns red on this branch, name it with file:line; the CTO fixes it under DEC-1156 (7). Known reds: `test_w2_23_space.py:94` and the three `test_cto_safety_nets.py` live-inbox cases. A resource gate's refusal is a wait (DEC-1146). Never open the evaluation sets' root or any hidden or memory-verdict folder. No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
