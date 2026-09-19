# P2-AR-0021 evidence (repair 1, WS-9 part + WS-11)

**Regression evidence only** (Contract v3 O3). This is a builder's record. It is not acceptance evidence, and it does not grade this repair.

| Directory / file | What it holds |
|---|---|
| `before/` | Probe and regression outputs from the base commit `c6b60bc` (branch base, product code identical to `cap2-candidate-0`). The base release binary had sha256 `3271ce0e4e095561911e0d03d8641aa92fbeda39ef3c8a2ecb2a9f21cacbe81d`. |
| `after/` | The same probes run against the final work commit's release binary. That binary's sha256 is `691e1f66925d5e2712e2a296eab4c1fa83f1dae637ef9297ad778233d5ada838`, recorded before and after the run. |
| `RUN-PROBES.sh` | Re-runs every probe listed below from the worktree root: `OUT=<dir> SCR=<scratch> bash …/RUN-PROBES.sh` |
| `B-ws0911-regression-probes.py` | Builder probes S1–S8. Each is a general scenario that goes beyond what the audit-of-record probes cover. Run against the base binary, 24 of 27 lines FAIL; the 3 that pass are the controls. Against the final binary, all 27 PASS. |
| `00-build-base-release.log` | Log of the release build of the base commit. |

The audit-of-record probes were run **unedited** from `release/capability-baseline/audit-0/*/evidence/`:

- `synthesis/evidence/LEAD-X5-adoption-rerun-archives-os-adapter.py`
- `beta-r/evidence/R1-R2-legacy-and-chat-retirement.py`
- `alpha-r/evidence/S4-adopt-end-to-end.py`, run twice: with `RAW_SQL_STORE=1` and with the prepared fixture
- `alpha-r/evidence/S4-T2-B2-negative.py` (`[N5]`)
- `alpha-r/evidence/T1-roles.py` (regression only; BC-P2-34 is round 2)
- `zeta-r/evidence/W01b-migration-plan-identity.py`
- `zeta-r/evidence/W01-artefact-identity.py`
- `epsilon-r/evidence/Q-learning-upstream.sh` (`Q4.5`)

Regression suites at the final work commit: `cargo test --lib` gives 51 passed. The base gave 42; the 9 new tests are in the new migrations modules. `cargo test --test certification` gives 81 passed. The base gave 79; the 2 new tests are `migration::adoption_dependency_proof_citations_and_rerun_identity` and `upstream::export_gate_fails_closed_on_content_whatever_the_name`. See `after/REG-*.out`.
