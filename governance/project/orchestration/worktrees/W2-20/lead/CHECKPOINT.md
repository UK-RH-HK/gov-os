# Lead checkpoint — DAEO-r30l (W2-20, machine-wide resource gate), 2026-10-17, run 2

## State

DONE, held for the close order (DEC-737). The loop has ended green: tests first, red checked, implemented, verified. Nothing is merged and nothing is closed. Run 1's packages are decided (DEC-742, owner; DEC-747, delegated and staged).

Branch `w2/W2-20`, cut from `w2/integrate` at `689bd17e`; `w2/integrate` merged in at `2ceae1e9` (by the orchestrator). Commits of this ticket:

- `726d8b26` independent-test-designer: acceptance tests `tests/acceptance/W2-20/` (22 cases).
- `c62ea489` orchestrator: checkpoint record (tests red, engineer next).
- `786ffa04` engineer: `src/gov/resources/{__init__,gate,command}.py`, `src/gov/launch/gate.py`, `tests/unit/resources/`.
- `173e8e97` independent-test-designer: `resources` recorded in W1-07's command list; W1-07 and W1-32 pins (Rewrite-Reason).
- `637497dc` orchestrator: run 1's lead checkpoint (PACKAGES).
- `d82619c3` independent-test-designer (run 2): DEC-747's sessions boundary, 3 cases (25 in all); W1-07 and W1-26 README counts (Rewrite-Reason).
- `70e40474` orchestrator: CP-DAEO-r30l-0008 (boundary tests red, engineer next).
- `19010dca` engineer (run 2): `resources` in `RECORDED_GOV_COMMANDS` (the one line, DEC-747 item 1); the start check takes `--heavy` and counts the new session's weight; the reading shuts at the maximum (DEC-747 item 2).
- (this checkpoint's commit) orchestrator: the hold record.

## Verification at `19010dca` (this worktree's src: `/home/usain/gov-os-worktrees/W2-20/src/gov/__init__.py`)

- Full rebuild: exit 0; lexical, semantic, codeintel recreated.
- W2-20: 25 passed. Unit: 2123 passed, 1 skipped. W1-26: 414 passed, 1 skipped (its `resources` cases green now).
- Every other W1 suite green, except: W1-42, 2 failed (RETR-X-02 and the governance share: the known reds of DEC-713/714); W1-05, 1 failed (`test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer]`, DEC-372) and W1-19, 1 failed (`test_a_warm_query_answers_within_half_a_second_at_p95`, 0.515 s against 0.5 s) under load: W1-19's file alone 6 passed; W1-05's file alone red twice at load 17 to 32 (other worktrees), then 86 passed at load 5.5.
- Validator `docs/plan/tools/validate_s1.py`: not run (DEC-738).
- Logs: `.gov-runtime/scratch/lead/log/verify2/`.

## What the resume lead does (after W2-01 has closed)

1. Merge `w2/integrate` into `w2/W2-20` with a merge commit carrying `Task: DAEO-r30l` and `Role: orchestrator` (trailers in the final block).
2. One full rebuild: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m gov.cli.main rebuild --json` (never `--no-embeddings`), in the background with an exit-code file.
3. Every suite again with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src`, in batches well under two hours (W1-41 alone, about 30 to 40 min; W1-30 about 27 min; the rest grouped), each with an exit-code file; then the latency files alone at low load.
4. Return to the orchestrator, who merges and closes.

Loop: converged.
