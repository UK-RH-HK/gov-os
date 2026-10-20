# Lead checkpoint — DAEO-egsy (W2-51, the Wave 2 plan validator), STANDARD

**State:** DONE, held for the close order (DEC-737). The loop ended green. Nothing is merged and nothing is closed.

- Worktree: `/home/usain/gov-os-worktrees/W2-51`, branch `w2/W2-51`, cut from `w2/integrate` at `61ca9c1a`.
- Branch head: `c2c80e6c`.
- Loop count (the lead's only, never disclosed, DEC-096): 1 implementation iteration, converged.

## Commits on the branch since the base

| Commit | Role | What | Trailers |
|---|---|---|---|
| `07376b4a` | independent-test-designer | 47 acceptance tests and README in `tests/acceptance/W2-51/` | Task: DAEO-egsy; Role: independent-test-designer; Implements: DEC-723, DEC-729; Co-Authored-By |
| `9832f926` | orchestrator | checkpoint record `docs/checkpoints/DAEO-egsy/CP-DAEO-egsy-0002.md` (after red) | Task: DAEO-egsy; Implements: DEC-723; Role: orchestrator; Co-Authored-By |
| `73d28a4a` | engineer | `docs/plan/tools/validate_w2.py` (+276), `tests/unit/plan/__init__.py`, `tests/unit/plan/test_validate_w2.py` (+46) | Task: DAEO-egsy; Role: engineer; Implements: DEC-723, DEC-729; Co-Authored-By |
| `c2c80e6c` | orchestrator | checkpoint record `CP-DAEO-egsy-0004.md` (the hold) | Task: DAEO-egsy; Implements: DEC-723; Role: orchestrator; Co-Authored-By |

## Verification at `73d28a4a` (this worktree's code, DEC-732)

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -c "import gov; print(gov.__file__)"` → `/home/usain/gov-os-worktrees/W2-51/src/gov/__init__.py`.
- Full rebuild: exit 0, lexical, semantic and codeintel recreated, digest `72c10e5c…`.
- W2-51: 47 passed. Builder tests (`tests/unit`): 2103 passed, 1 skipped.
- Every W1 suite green except:
  - W1-19: 1 latency failure in the full run (`test_a_warm_query_answers_within_half_a_second_at_p95`, warm p95 1.133 s under load); `test_w1_19_real_models.py` alone: 6 passed.
  - W1-42: the two known reds (RETR-X-02 no named parent expansion; the governance share per programme).
  - W1-46: `test_w1_46_live_sessions.py`, 23 setup errors from the research fixture (the launched haiku research session did not run probe.sh: exit 127), in the full run and alone (13 passed, 23 errors). Not caused by this ticket: the branch changes no file under `src/`.
- `validate_s1.py` not run (DEC-738, P-W2-11).
- Validator over this tree: 2 FAIL (W2-51 and W2-52 missing from WBS §1's table; 14 Wave 2 items not cited under `tests/acceptance/`), 6 PASS, 5 NOT RUN; exit 1. Plan findings, not this ticket's.

## What the resume lead must do (after W2-01 has closed cleanly)

1. Checks: `printenv GOV_ROLE GOV_TICKET`, top level and branch; the hooks folder holds no `pre-commit`.
2. Merge `w2/integrate` into `w2/W2-51` with a merge commit carrying `Task: DAEO-egsy` and `Role: orchestrator` (and `Implements: DEC-723`). Never rebase, amend or reset.
3. One full rebuild (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 -m gov.cli.main rebuild --json`, never `--no-embeddings`), in the background with an exit-code file.
4. Every suite again with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src`: `tests/acceptance/W2-51`, every `tests/acceptance/W1-*` suite, `tests/unit`. Split them over several background jobs: the whole run in one job took more than the 2-hour background limit (W1-41 alone takes about 28 min, W1-30 about 19, W1-05 about 18). Rerun latency and live-session files alone after the rest.
5. Re-run the validator over the tree and quote it.
6. A `gov checkpoint` record, commit it, return DONE for the orchestrator's merge and close.
