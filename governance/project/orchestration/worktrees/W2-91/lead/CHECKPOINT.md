# W2-91 (DAEO-a3u2) lead checkpoint — run 1, at return (2026-11-01 21:20)

## State
- Status returned: PACKAGES. The implementation, the acceptance tests and the evidence are done; my scoped verification did NOT run: the verification rebuild waited for a heavy-job slot from 19:45 to 21:15 (90 min, DEC-943), so I stopped it (only polling, never started) and returned.
- Branch `w2/W2-91` head `f652eeae3911`, clean. Commits since `f46b96537d74`:
  - `663b7915ff65` lead: merge of `w2/integrate` (`904bb3a0e7c6`) for the claim `9861958e` (Task, Implements DEC-957,DEC-954,DEC-388,DEC-694, Role: orchestrator).
  - `657a264dcd53` test designer: tests/acceptance/W2-91/ (19 tests, README, support).
  - `d094f02ce0e2` lead: merge of the tests.
  - `b652fc96d2b5` engineer: path map (root-files, project-overlay embedded; carried-code = cli/**; new carried-schemas = schemas/** embedded) + tests/unit/retrieval/test_w2_91_full_embeddings.py (6).
  - `f57fa0cdf694` test designer: README map column "Tests" (Rewrite-Reason).
  - `a53650525fd8` lead: merge of the README fix.
  - `38d347634fff` engineer: docs/changes/W2-91-evidence.md (253 lines).
  - `f652eeae3911` lead: docs/checkpoints/DAEO-a3u2/CP-DAEO-a3u2-0003.md.
- Done: red check (3 failed / 16 passed at d094f02ce0e2); my run at a53650525fd8 25 passed; gov accept (engineer) pass on 8/8 lines, 19 passed; trailer_gate 10/0/0; keyword_warn 0; collect-only 19084/19086 (2 deselected), no error; select.json (head f652eeae3911): scoped, core_changed [path-map.yaml], unplaced [].
- Measure: control 7/11/13 of 20, head 7/11/13 of 20 (pinned gov), records in /home/usain/gov-os-runs/W2-91/records.

## What a resume must do
1. Disk gate; `bash .gov-runtime/scratch/lead/rebuild.sh 4` (rebuild_slot form; detach it with `setsid -f` so the two-hour tool limit cannot cut it), wait for `log/rebuild-4.exit`.
2. `gov check --json` (this worktree's code) -> report non-green checks.
3. Re-run select_tests.py (head unchanged: `f652eeae3911`), then `python3 .gov-runtime/scratch/lead/verify.py .gov-runtime/scratch/lead/log/select.json .gov-runtime/scratch/lead/log/verify` (detached), read parallel/serial exits and JUnit.
4. Expected reds: W2-86's `test_guard_outside_template_every_verdict_as_at_the_base` (package TD-2); W1-01's known red (DEC-906) if selected; accepted_reds/load_sensitive per lists.
5. Return DONE with `f652eeae3911` (or PACKAGES if TD-2 is still open).

## Packages (returned, not decided)
- P-W2-91-TD-1: KPI 3's export half: no export path exists.
- P-W2-91-TD-2: W2-86's guard case turns red.
- P-W2-91-VERIFY-1: the verification run held 90 minutes by the heavy-job slots.

## Leftovers for the orchestrator
- `/home/usain/gov-os-runs/W2-91/base` (647M) and `/head` (666M) clones (rm needs a permission); records (24K) are cited by the evidence record.
- `/tmp/gov-os-lead-W2-91` (33M, 2,042 inodes).
- td-1 sandbox temp `/tmp/gov-launch-independent-test-designer-llshsdr8/claude-1000` (36 MB, 3,032 inodes); engineer sandbox temp `/tmp/gov-launch-engineer-5h0j_i74/claude-1000`; two scratchpad files each.

## Loop count: (held by the lead; not disclosed)
