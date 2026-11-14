This is W2-94 (DAEO-g87r), a short run on the gold check. You returned DONE at cfbcd75ab386. The owner's operator then ran `check_gold.py` on the real delivery: 17 of 20, draw FAIL, release ok, exit 1. The owner decided W2-94 GOLD (2026-11-13; recorded as DEC-1175 with the evening's decisions):
- **(a) for q01 and q12:** the check reads the writer's own words too literally, and the set stays unchanged.
- **The draw:** every DRAW.txt line writes `SEED+k=` with the letter k, as the brief's §6 literally reads, with the values present. The check accepts that form; the set stays unchanged.
- **§6 of the brief** is corrected to `SEED+<k>=` for future sets. That edit is the owner's and is not in this run.
- **q02 (hidden)** is a real defect, handled by a separate package. It stays red in this run.

Read your lead checkpoint, then the CTO's diagnosis `.gov-runtime/scratch/orchestrator/drafts/P-W2-94-GOLD-1.md` (§2 to §4), then `fixtures/evaluation/examin/check_gold.py` (rule 2a, `_shaped`, `answer_in`, `DRAW_LINE`).

**The order:**
1. Merge `w2/integrate` into `w2/W2-94`: one command, `--no-ff`, with `Task: DAEO-g87r` and `Role: orchestrator`. **Never commit a merge with conflict markers** (DEC-1173 (1)).
2. **A fresh independent test designer** (check_gold.py is the designer's script; `Rewrite-Reason: W2-94 GOLD (owner, 2026-11-13)`), with cases first under `tests/acceptance/W2-94/` and each red before the change:
   - (i) A hyphenated word with a digit counts as an identifier token only when it is id-shaped: an upper-case letter prefix, as in `DEC-051`, `W2-94` or `CAP-10`. Lower-case words such as `level-2` or `top-3` are not tokens.
   - (ii) A path token (one with `/`) is held when its path segments occur in order in the union of the spans, the way code joins a path (`os.path.join("spec/2-PLAN", "VIEWS.md")`). The literal rule still holds first.
   - (iii) `DRAW_LINE` also accepts the literal `SEED+k=<value>` form, as the brief's §6 reads. The `k` is then taken from the line's first field, and every other rule is unchanged (seed consistency, parity, ids, the parity rule).
   - Nothing else changes, and every existing case keeps its point. Planted fixtures only: never the real set's hidden half.
3. `gov accept W2-94` and the scoped run once (DEC-968).
4. **A narrow independent check** (a fresh independent auditor, Opus, high, read-only, carrying JUDGEMENT.md word for word):
   - It checks only this change, against (i) to (iii). It confirms that the rule still catches a wrong span (an identifier-shaped token absent from the spans) and a wrong path, and that the draw rules stay strict apart from the literal `k`.
   - Commit its record under `docs/probes/DAEO-g87r/` with `implementer_session` and `probed_commit` in full. Quote any front-matter value that holds `: `.
   - Every commit's trailers go in one final paragraph.
5. Return DONE with the head. The owner's operator then re-runs `check_gold.py` on the real delivery. The expected result is 19 of 20 with draw ok, and q02 the only FAIL until its package is decided.

Never open the evaluation sets' root or any hidden folder (`/home/usain/gov-os-eval`); this run needs none of it. Workers use the sandbox's own `$TMPDIR` (`/tmp` is read-only there). Every pytest, yours and every worker's, through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits and stops by pid only (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`); never the Monitor tool, never a name match. If another ticket's case turns red on this branch, name it with file:line; the CTO fixes it under DEC-1156 (7). Known reds: `test_w2_23_space.py:94` and the three `test_cto_safety_nets.py` live-inbox cases. A resource gate's refusal is a wait (DEC-1146). No new ticket: a gap comes back as a package. A session refused twice for the same action by the guard, the sandbox or a hook stops and says so, and never works around a refusal (DEC-1142 (9)). If an API error ends a worker, relaunch it once from its checkpoint; if it ends again, return PACKAGES naming it. There is no token cap.
